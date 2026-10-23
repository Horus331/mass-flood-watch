#!/bin/bash
# Road-closure FORECAST for all of MassDOT District 3 on one GPU: NOAA HRRR rain (latest 48 h cycle, or INIT) -> gate -> LISFLOOD-FP 8.2 at 20 m
# (17.6 M cells, ~17 min for a 48 h storm on one GPU) -> proto/prototype.py -> viewer pack docs/site/data/forecast_d3/ + forecast_d3_status.json.
# Run it by hand when the GitHub gate (.github/workflows/forecast.yml, docs/site/data/forecast_status.json) says heavy rain is coming; no cron here.
#   sbatch proto/turing/run_forecast.slurm                          # latest cycle; exits early (nothing published) when the gate is quiet
#   FORCE=1 INIT=2023-09-11T12Z sbatch --export=ALL proto/turing/run_forecast.slurm   # a given cycle, model run even if the gate is quiet
#   PUBLISH=0 ...                                                   # keep the results on Turing only
# Publishes (proto/turing/publish.sh): docs/proto/turing/forecast_d3_20m/ (small files only: summary, report, watchlist, flood meta, gate),
# docs/site/data/forecast_d3/ (overwritten) and docs/site/data/forecast_d3_status.json.  Full outputs stay in $LF_WORK/run_forecast_*/out.
#SBATCH -J roadfcst
#SBATCH -p quick
#SBATCH -N 1
#SBATCH -n 8
#SBATCH --mem=96G
#SBATCH --gres=gpu:1
#SBATCH -t 04:00:00
#SBATCH -o roadfcst_%j.out
set -eo pipefail
source proto/turing/env.sh
export LF_NO_UPLOAD=1 OMP_NUM_THREADS=${SLURM_NTASKS:-8}
export BOX=${BOX:-128000,856000,206000,946000} RES=${RES:-20} STORM=forecast LF_RAIN=hrrr LF_ALLOW_DRY=1
export LF_LOSS=${LF_LOSS:-cn} LF_CN_AMC=${LF_CN_AMC:-II} LF_CN_SCALE=${LF_CN_SCALE:-0.91} LF_INFIL_MMH=${LF_INFIL_MMH:-2} LF_QOUT=${LF_QOUT:-1}
NAME=${NAME:-forecast_d3_20m}; KEY=${KEY:-forecast_d3}
export RUN_DIR=runs/forecast_${NAME}
SCR=$LF_WORK/fc_$NAME; rm -rf "$SCR"; mkdir -p "$SCR"
nvidia-smi || true
echo "== net check"; for u in https://huggingface.co https://noaa-hrrr-bdp-pds.s3.amazonaws.com; do printf "%s " $u; curl -s -o /dev/null -m 10 -w "%{http_code}\n" $u; done
# 1. gate (fixes the cycle, so the model and the status use the same one)
python proto/forecast.py gate ${INIT:+--init $INIT} $( [ "${FORCE:-0}" = "1" ] && echo --force ) --out "$SCR/gate.json" --github-output "$SCR/gate.env"
cat "$SCR/gate.env"
TRIG=$(grep '^trigger=' "$SCR/gate.env" | cut -d= -f2); CYC=$(grep '^init=' "$SCR/gate.env" | cut -d= -f2)
if [ "$TRIG" != "true" ]; then echo "gate quiet for $CYC: no flood run (FORCE=1 to run anyway)"; exit 0; fi
export LF_HRRR_INIT=$CYC
# 2. flood depth, all of District 3
time python sim/colab/w9_lisflood.py
OUT=$(ls -d $LF_WORK/run_forecast_${NAME}/out)
# 3. closures (full outputs in scratch), viewer pack, status
python proto/prototype.py --run-dir "$OUT" --out "$SCR/proto" --storm forecast | tail -5
cp $OUT/meta.json "$SCR/proto/flood_meta.json"
python docs/site/build_data.py --run $KEY --src "$SCR/proto" --pool 4
python proto/forecast.py status --gate "$SCR/gate.json" --run "$KEY=$SCR/proto" --out docs/site/data/${KEY}_status.json
mkdir -p results/$NAME
cp "$SCR/proto/summary.json" "$SCR/proto/REPORT.md" "$SCR/proto/watchlist.csv" "$SCR/gate.json" results/$NAME/
python -c "import json; m=json.load(open('$SCR/proto/flood_meta.json')); m.pop('frames', None); m['inputs']['env'].pop('LF_EXE', None); json.dump(m, open('results/$NAME/flood_meta.json', 'w'), indent=1)"
echo "results: results/$NAME, docs/site/data/$KEY/, docs/site/data/${KEY}_status.json; full run in $OUT"
[ "${PUBLISH:-1}" = "1" ] && PUBLISH_EXTRA="docs/site/data/$KEY docs/site/data/${KEY}_status.json" bash proto/turing/publish.sh "$NAME" || true
