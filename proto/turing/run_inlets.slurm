#!/bin/bash
# LF_INLETS test (docs/proto/drains/INLETS_PREREG.md): one task of a plan (proto/turing/plans/<plan>.json, proto/turing/inlets_plan.py) =
# one storm x one arm, LISFLOOD-FP 8.2 on the CPU (the infilfile sink is run-tested on the CPU solver only, so both arms run on the CPU),
# at a pinned commit, then the scorers -> small json in $LF_WORK/<results_root>/<NAME>/ (collect_scores.slurm pushes them to main).
#   queue: {"id": "inl1_runs", "kind": "run_inlets", "env": {"PLAN": "proto/turing/plans/inlets_v1.json", "PIN": "<sha on main>"},
#           "sbatch": {"array": "0-49%10", "partition": "long", "time": "08:00:00"}}
#   by hand: PLAN=proto/turing/plans/inlets_v1.json PIN=<sha> sbatch --array=0-49%10 --export=ALL proto/turing/run_inlets.slurm
# PIN: every task runs the code of that commit, checked out once into $LF_WORK/code_<PIN> (git worktree, shared by all tasks), so the arms
# of a pair run identical code even if main moves while the batch runs.  Each task has its own LF_WORK (no shared probe / download dirs).
#SBATCH -J inlets
#SBATCH -p long
#SBATCH -N 1
#SBATCH -n 16
#SBATCH --mem=64G
#SBATCH -t 08:00:00
#SBATCH -o inlets_%A_%a.out
set -eo pipefail
source proto/turing/env.sh
[[ "${PIN:-}" =~ ^[0-9a-f]{7,40}$ ]] || { echo "PIN must be a commit sha"; exit 2; }
[[ "${PLAN:-}" =~ ^proto/turing/plans/[A-Za-z0-9_]+\.json$ ]] || { echo "PLAN must be proto/turing/plans/<name>.json"; exit 2; }
IDX=${SLURM_ARRAY_TASK_ID:-${IDX:-0}}; [[ "$IDX" =~ ^[0-9]+$ ]] || exit 2
BASEWORK=$LF_WORK; REPO=$PWD; CODE=$BASEWORK/code_$PIN
mkdir -p $BASEWORK
( flock 9
  if [ ! -e $CODE/.git ]; then git -C $REPO worktree add --detach -f $CODE $PIN || git -C $REPO worktree add --detach -f $CODE $(git -C $REPO rev-parse $PIN); fi
) 9>$BASEWORK/code_$PIN.lock
cd $CODE; echo "code $(git rev-parse HEAD) in $CODE"
unset LF_INLETS LF_INLETS_CLOG LF_INLETS_D LF_INLETS_LEAF LF_INLETS_NETCAP LF_DRAINS LF_DRAIN_DESIGN LF_EXE LF_EXE_CUDA
source <(python proto/turing/inlets_plan.py env $PLAN $IDX)
[[ "${NAME:-}" =~ ^[a-z0-9_]{3,80}$ && "${RESULTS_ROOT:-}" =~ ^[A-Za-z0-9_]+$ && -n "${STORM:-}" ]] || { echo "plan task $IDX not readable"; exit 2; }
R=$BASEWORK/$RESULTS_ROOT/$NAME; rm -rf $R; mkdir -p $R
echo "== task $IDX: $NAME ($TASK_STORM, $TASK_ARM) box $BOX hours $HOURS"; env | grep -E '^(LF_|BOX|HOURS|STORM|RES|NAME)' | sort | grep -v LF_WORK || true
# CPU build of LISFLOOD-FP 8.2 with the mfw-drains infilfile patch, shared by all tasks (built once, under a lock)
( flock 9
  python - <<'PY'
import os, sys, shutil; sys.path.insert(0, 'sim/colab'); import w9_lisflood as W
src = f'{W.WORK}/src'
if not os.path.isdir(src):
    try: z, ver, url = W.get_lisflood(); W.extract_all(z, src)
    except Exception as e: print('Zenodo download failed, using tools/lisflood_src (8.2 text copy):', repr(e)[:200]); shutil.copytree('tools/lisflood_src', src)
s = W.find_source(src); st = W.patch_drain_sink(s); exe = f'{W.WORK}/build_cpu/lisflood'
if not (st['cpu'] and os.path.exists(exe) and os.path.getmtime(exe) > os.path.getmtime(f'{s}/infevap.cpp')):
    exe, cuda = W.build_lisflood(s, want_cuda=False)
print('CPU build', exe); print(W.probe_sink(exe, False))
PY
) 9>$BASEWORK/build_cpu.lock
export LF_EXE=$BASEWORK/build_cpu/lisflood LF_EXE_CUDA=0 LF_NO_UPLOAD=1 OMP_NUM_THREADS=${SLURM_NTASKS:-16} GIT_SHA=$(git rev-parse --short HEAD)
export LF_WORK=$BASEWORK/$RESULTS_ROOT/work_$NAME RUN_DIR=runs/${STORM}_proto_${NAME}; rm -rf $LF_WORK
fail() { echo "$1" > $R/FAILED; echo "FAILED: $1"; exit 1; }
time python sim/colab/w9_lisflood.py > $R/w9_stdout.txt 2>&1 || { tail -40 $R/w9_stdout.txt; fail w9; }
tail -c 20000 $R/w9_stdout.txt > $R/w9_tail.txt; rm $R/w9_stdout.txt
OUT=$LF_WORK/run_${STORM}_proto_${NAME}/out; [ -f $OUT/meta.json ] || fail no_meta
F=$R/full; mkdir -p $F      # score_v2-ready run folder (not published: segments.geojson / features are MBs)
python proto/prototype.py --run-dir "$OUT" --storm $STORM --out $F | tail -3 || fail prototype
cp $OUT/meta.json $F/flood_meta.json
SCORE_WINDOWS=$R/gauge_windows.npz python proto/score.py --run-dir "$OUT" --storm $STORM --out $R/score.json | tail -8 || true
python proto/validate_points.py --run-dir "$OUT" --storm $STORM --out $R/points.json | tail -4 || true
LBL=$( (ls proto/data/labels_${STORM}_*.csv proto/data/labels_${STORM}_*.geojson 2>/dev/null || true) | paste -sd, -)
[ -n "$LBL" ] && python -c "import sys; sys.path.insert(0, 'proto'); import closure_ml as C; C.extract('$OUT', '$STORM', '$LBL'.split(','), out_dir='$F')" | tail -2 || fail closure_ml
python proto/score_v2.py --run $F --storm $STORM --out $R/score_v2.json | tail -30 || fail score_v2
python - $OUT $R <<'PY'
import json, sys, os
out, r = sys.argv[1:]; m = json.load(open(f'{out}/meta.json')); m.pop('frames', None)
json.dump(m, open(f'{r}/flood_meta.json', 'w'), indent=0)
PY
du -sh $OUT; rm -rf $LF_WORK/run_*/results     # keep out/ (hmax etc.) on scratch for re-scoring; drop the solver's raw snapshots
echo ok > $R/DONE; ls -la $R
