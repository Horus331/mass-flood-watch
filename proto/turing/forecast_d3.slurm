#!/bin/bash
# Live forecast, PRIMARY path (docs/proto/forecast/GATE.md "Turing first"): all of MassDOT District 3 at 20 m on the GPU for one HRRR cycle whose
# gate fired, one ARRAY task per time-lagged ensemble member (a pending array is one submitted job under Turing's per-user submit cap).
# Queued by .github/workflows/forecast.yml (gate job) at the FRONT of jobs.json on the turing-queue branch:
#   {"id": "fcd3_2026110112", "kind": "forecast_d3", "env": {"CYCLE": "2026-11-01T12Z", "MEMBERS": "2026-11-01T12Z,2026-11-01T06Z,...",
#    "HOURS": "48", "PFX": "forecast_d3", "REQ_AT": "2026-11-01T13:50:12Z"}, "sbatch": {"array": "0-7", "partition": "quick", "time": "06:00:00"}}
# Each task: the same flood-model set-up as the GitHub box jobs (HRRR rain of its member, 20 km / 90th percentile neighbourhood, CN x 0.88 AMC II,
# LF_PARITY=1, 2 mm/h, LF_QOUT=1), only the box is the whole district (17.6 M cells). Task 0 (the issue cycle) also keeps depth frames and
# solver velocity for the replay. Then proto/prototype.py -> $LF_WORK/fcd3_<cycle>/m<j>/.
# Publishing (under a lock, from the task that completes it): when task 0 is done, and again when the last member is done (k-of-n complete):
# tiled replay pack docs/site/data/<PFX>/ (docs/site/build_data.py build_tiled), k-of-n (proto/forecast_kofn.py), network.json,
# docs/site/data/<PFX>_status.json, and for the live prefix forecast_status.json too when this cycle is the newest one published (a Turing
# result never replaces a newer cycle's boxes). One commit per publish, pushed through the deploy key.
#   FORCE=1: run even if the gate is quiet for CYCLE (tests on past storms).  PFX other than forecast_d3: a test, live status untouched.
#SBATCH -J fcd3
#SBATCH -p quick
#SBATCH -N 1
#SBATCH -n 8
#SBATCH --mem=96G
#SBATCH --gres=gpu:1
#SBATCH -t 06:00:00
#SBATCH -o fcd3_%A_%a.out
set -eo pipefail
source proto/turing/env.sh
[[ "${CYCLE:-}" =~ ^20[0-9]{2}-[01][0-9]-[0-3][0-9]T[0-2][0-9]Z$ ]] || { echo "CYCLE must look like 2026-11-01T12Z"; exit 2; }
[[ "${MEMBERS:-}" =~ ^(20[0-9]{2}-[01][0-9]-[0-3][0-9]T[0-2][0-9]Z,?){1,12}$ ]] || { echo "MEMBERS: comma-separated cycles"; exit 2; }
[[ "${HOURS:-48}" =~ ^[0-9]{1,2}$ ]] || exit 2
PFX=${PFX:-forecast_d3}; [[ "$PFX" =~ ^[a-z0-9_]{3,40}$ ]] || exit 2
REPO=$PWD
IFS=, read -ra M <<< "$MEMBERS"; N=${#M[@]}; J=${SLURM_ARRAY_TASK_ID:-0}
[ $J -lt $N ] || { echo "task $J: no member"; exit 0; }
MEM=${M[$J]}; TAG=$(echo $CYCLE | tr -dc 0-9); FC=$LF_WORK/fcd3_${PFX}_$TAG; R=$FC/m$J; mkdir -p $FC; rm -rf $R; mkdir -p $R
now() { date -u +%Y-%m-%dT%H:%M:%SZ; }
echo "start=$(now)" > $R/times; echo "member=$MEM" >> $R/times
nvidia-smi || true
NAME=fcd3_${PFX}_${TAG}_m$J
export LF_NO_UPLOAD=1 OMP_NUM_THREADS=${SLURM_NTASKS:-8} GIT_SHA=$(git rev-parse --short HEAD)
export BOX=128000,856000,206000,946000 RES=20 STORM=forecast LF_RAIN=hrrr LF_HRRR_INIT=$MEM LF_HRRR_HOURS=$HOURS LF_ALLOW_DRY=1 LF_HRRR_NBHD=20,90
export LF_LOSS=cn LF_CN_AMC=II LF_CN_SCALE=0.88 LF_PARITY=1 LF_INFIL_MMH=2 LF_QOUT=1          # = forecast.yml flood job (no setting changes)
if [ $J = 0 ]; then export LF_SAVEINT=1800 LF_VOUT=1 LF_VFRAMES=1; fi                         # replay frames (30 min) + solver velocity: output only
export RUN_DIR=runs/forecast_$NAME
OUT=$LF_WORK/run_forecast_$NAME/out
if python sim/colab/w9_lisflood.py > $R/w9.txt 2>&1 && [ -f $OUT/meta.json ] && python proto/prototype.py --run-dir $OUT --out $R/proto --storm forecast > $R/proto.txt 2>&1; then
  cp $OUT/meta.json $R/proto/flood_meta.json; echo "$OUT" > $R/OUTDIR; rm -rf $LF_WORK/run_forecast_$NAME/results; echo "finish=$(now)" >> $R/times; touch $R/DONE
else
  tail -30 $R/w9.txt || true; tail -10 $R/proto.txt 2>/dev/null || true; echo "finish=$(now)" >> $R/times; touch $R/FAILED
fi
# ---- publish (one task at a time): after the issue member, and when the last member finishes
exec 9>$FC/pack.lock; flock 9
NDONE=$(ls -d $FC/m*/DONE $FC/m*/FAILED 2>/dev/null | wc -l)
if [ $J != 0 ] && [ $NDONE -lt $N ]; then echo "member $J done; $NDONE of $N finished, publishing later"; exit 0; fi
if [ $J != 0 ] && [ ! -f $FC/m0/DONE ] && [ ! -f $FC/m0/FAILED ]; then echo "last member but the issue member is still running: it publishes"; exit 0; fi
P=$FC/pack; mkdir -p $P
python proto/forecast.py gate --init $CYCLE $( [ "${FORCE:-0}" = 1 ] && echo --force ) --out $P/gate.json --github-output $P/gate.env > $P/gate.txt 2>&1 || { tail $P/gate.txt; exit 1; }
python - $P/gate.json "$MEMBERS" <<'PY'
import json, sys
G = json.load(open(sys.argv[1])); G['boxes_issue'] = G.get('boxes', [])
G['boxes'] = [dict(id='b1', box=[128000.0, 856000.0, 206000.0, 946000.0], member=sys.argv[2].split(',')[0], about='all of MassDOT District 3')]
G['ensemble'] = dict(members=sys.argv[2].split(','), rule='likely closed: >= 2 of the members; possible: 1', basis='docs/proto/forecast/ENSEMBLE.md')
json.dump(G, open(sys.argv[1], 'w'), indent=1)
PY
MA=""; for j in $(seq 0 $((N - 1))); do MA="$MA --member ${M[$j]}:b1=$FC/m$j/proto"; done
python proto/forecast_kofn.py ensemble --gate $P/gate.json $MA --out $P/kofn.json --viewers $P/viewers.txt --prefix $PFX
read KEY DIR BID MM < $P/viewers.txt || { echo "no member finished"; exit 1; }
JD=$(basename $(dirname $DIR)); RD=$(cat $FC/$JD/OUTDIR)
cd $REPO
git pull -q --rebase --autostash "$(git remote get-url --push origin)" main || true
python docs/site/build_data.py --run $PFX --src $DIR --run-dir $RD --flow --frame-min 30 --budget-mb 40
python proto/forecast_kofn.py pack --kofn $P/kofn.json --key $PFX --box b1
python proto/build_network.py $PFX || true
python - $FC $P "$N" "${REQ_AT:-}" "$PFX" "$MM" <<'PY'
import json, os, sys, glob
fc, p, n, req, pfx, mm = sys.argv[1:]; T = {}
for d in sorted(glob.glob(os.path.join(fc, 'm*'))):
    if not os.path.isdir(d) or not os.path.exists(os.path.join(d, 'times')): continue
    T[os.path.basename(d)] = dict(l.strip().split('=', 1) for l in open(os.path.join(d, 'times')) if '=' in l)
    T[os.path.basename(d)]['ok'] = os.path.exists(os.path.join(d, 'DONE'))
import datetime as dt
K = json.load(open(os.path.join(p, 'kofn.json'))); fin = len(K['finished'].get('b1', []))
x = dict(display='turing', dir='data/%s/' % pfx, coverage='Whole District 3, 20 m (Turing GPU)',
         kind='One GPU flood-model run per forecast member on WPI’s Turing cluster (%d of %s members finished; the map shows the %s run).' % (fin, n, mm),
         turing=dict(requested=req or None, members=T, published=dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'), finished_members=fin, n_members=int(n)))
json.dump(x, open(os.path.join(p, 'extra.json'), 'w'))
PY
python proto/forecast.py status --gate $P/gate.json --run "$PFX=$DIR" --kofn $P/kofn.json --extra $P/extra.json --out docs/site/data/${PFX}_status.json
ADD="docs/site/data/$PFX docs/site/data/${PFX}_status.json"
if [ "$PFX" = forecast_d3 ]; then   # live: replace the public status only when this cycle is the newest published (never over a newer cycle's boxes)
  if python - docs/site/data/forecast_status.json docs/site/data/forecast_d3_status.json <<'PY'
import json, sys
try: cur = json.load(open(sys.argv[1]))
except Exception: cur = {}
new = json.load(open(sys.argv[2]))
sys.exit(0 if (cur.get('issued') or '') <= new['issued'] else 1)
PY
  then cp docs/site/data/forecast_d3_status.json docs/site/data/forecast_status.json; ADD="$ADD docs/site/data/forecast_status.json"; fi
fi
for X in $ADD; do git add -A $X; done
git -c user.name="Mohab Eldokla" -c user.email="Horus331@users.noreply.github.com" commit -qm "Forecast $PFX $CYCLE: whole District 3 at 20 m on Turing ($(python -c "import json;s=json.load(open('docs/site/data/${PFX}_status.json'));print(s.get('likely_closed'), 'likely,', s.get('possible'), 'possible')"))" || { echo "nothing to commit"; exit 0; }
RM=$(git remote get-url --push origin)
for i in 1 2 3 4 5; do git pull -q --rebase --autostash "$RM" main && git push -q "$RM" HEAD:main && echo "published $PFX $CYCLE" && exit 0; sleep 15; done
echo "push failed"; exit 1
