#!/bin/bash
# Several tasks of a run plan (proto/turing/plans/<plan>.json, format and checks: proto/turing/inlets_plan.py), one after the other in ONE
# GPU job (so a 50-run test needs a handful of Slurm jobs, not 50: Turing caps submitted jobs per user, QOSMaxSubmitJobPerUserLimit).
# Each task = one storm x one arm: LISFLOOD-FP 8.2 on the GPU (prebuilt $LF_WORK/build_cuda, proto/turing/env.sh), at a pinned commit,
# then the scorers -> small files in $LF_WORK/<results_root>/<NAME>/ (DONE or FAILED); proto/turing/collect_scores.slurm pushes them to main.
#   queue: {"id": "amcnwm_b1", "kind": "run_plan_gpu", "env": {"PLAN": "proto/turing/plans/amcnwm_v1.json", "PIN": "<sha on main>", "IDXS": "0-9"},
#           "sbatch": {"partition": "quick", "time": "08:00:00"}}
# First used by docs/proto/runoff/NWM_AMC_PREREG.md.  Modelled on run_inlets.slurm (CPU), with the GPU build and a task loop.
#SBATCH -J planGPU
#SBATCH -p quick
#SBATCH -N 1
#SBATCH -n 8
#SBATCH --mem=96G
#SBATCH --gres=gpu:1
#SBATCH -t 08:00:00
#SBATCH -o plan_gpu_%j.out
set -eo pipefail
source proto/turing/env.sh
[[ "${PIN:-}" =~ ^[0-9a-f]{7,40}$ ]] || { echo "PIN must be a commit sha"; exit 2; }
[[ "${PLAN:-}" =~ ^proto/turing/plans/[A-Za-z0-9_]+\.json$ ]] || { echo "PLAN must be proto/turing/plans/<name>.json"; exit 2; }
[[ "${IDXS:-}" =~ ^[0-9]{1,3}(-[0-9]{1,3})?(,[0-9]{1,3}(-[0-9]{1,3})?)*$ ]] || { echo "IDXS must look like 0-9 or 0,3,5-7"; exit 2; }
[ -x "${LF_EXE:-}" ] || { echo "no prebuilt GPU LISFLOOD-FP (proto/turing/build.slurm)"; exit 2; }
nvidia-smi || true
BASEWORK=$LF_WORK; REPO=$PWD; CODE=$BASEWORK/code_$PIN; GPU_EXE=$LF_EXE
( flock 9
  if [ ! -e $CODE/.git ]; then git -C $REPO worktree add --detach -f $CODE $PIN || git -C $REPO worktree add --detach -f $CODE $(git -C $REPO rev-parse $PIN); fi
) 9>$BASEWORK/code_$PIN.lock
cd $CODE; echo "code $(git rev-parse HEAD) in $CODE"
LIST=$(python -c "
import sys
out = []
for part in sys.argv[1].split(','):
    a, _, b = part.partition('-'); out += range(int(a), int(b or a) + 1)
print(' '.join(map(str, out)))" "$IDXS")
run_task() {   # one task in a subshell: its env cannot leak into the next one
  IDX=$1
  unset $(env | grep -oE '^LF_[A-Z0-9_]+' | grep -vE '^LF_WORK$') 2>/dev/null || true
  source <(python proto/turing/inlets_plan.py env $PLAN $IDX)
  [[ "${NAME:-}" =~ ^[a-z0-9_]{3,80}$ && "${RESULTS_ROOT:-}" =~ ^[A-Za-z0-9_]+$ && -n "${STORM:-}" ]] || { echo "plan task $IDX not readable"; return 2; }
  R=$BASEWORK/$RESULTS_ROOT/$NAME; rm -rf $R; mkdir -p $R
  fail() { echo "$1" > $R/FAILED; echo "FAILED $NAME: $1"; exit 1; }
  echo "== task $IDX: $NAME ($TASK_STORM, $TASK_ARM) box $BOX hours $HOURS  $(date -u +%FT%TZ)"; env | grep -E '^(LF_|BOX|HOURS|STORM|RES|NAME)' | sort | grep -v LF_WORK || true
  export LF_EXE=$GPU_EXE LF_EXE_CUDA=1 LF_NO_UPLOAD=1 OMP_NUM_THREADS=${SLURM_NTASKS:-8} GIT_SHA=$(git rev-parse --short HEAD)
  export LF_WORK=$BASEWORK/$RESULTS_ROOT/work_$NAME RUN_DIR=runs/${STORM}_proto_${NAME}; rm -rf $LF_WORK
  python sim/colab/w9_lisflood.py > $R/w9_stdout.txt 2>&1 || { tail -40 $R/w9_stdout.txt; fail w9; }
  tail -c 20000 $R/w9_stdout.txt > $R/w9_tail.txt; rm $R/w9_stdout.txt
  OUT=$LF_WORK/run_${STORM}_proto_${NAME}/out; [ -f $OUT/meta.json ] || fail no_meta
  F=$R/full; mkdir -p $F      # score_v2-ready run folder (not published)
  python proto/prototype.py --run-dir "$OUT" --storm $STORM --out $F | tail -3 || fail prototype
  cp $OUT/meta.json $F/flood_meta.json
  SCORE_WINDOWS=$R/gauge_windows.npz python proto/score.py --run-dir "$OUT" --storm $STORM --out $R/score.json | tail -8 || true
  python proto/validate_points.py --run-dir "$OUT" --storm $STORM --out $R/points.json | tail -4 || true
  LBL=$( (ls proto/data/labels_${STORM}_*.csv proto/data/labels_${STORM}_*.geojson 2>/dev/null || true) | paste -sd, -)
  [ -n "$LBL" ] && python -c "import sys; sys.path.insert(0, 'proto'); import closure_ml as C; C.extract('$OUT', '$STORM', '$LBL'.split(','), out_dir='$F')" | tail -2 || fail closure_ml
  python proto/score_v2.py --run $F --storm $STORM --out $R/score_v2.json | tail -30 || fail score_v2
  python - $OUT $R <<'PY'
import json, sys
out, r = sys.argv[1:]; m = json.load(open(f'{out}/meta.json')); m.pop('frames', None)
json.dump(m, open(f'{r}/flood_meta.json', 'w'), indent=0)
PY
  rm -rf $LF_WORK/run_*/results     # keep out/ (hmax etc.) on scratch for re-scoring; drop the solver's raw snapshots
  echo ok > $R/DONE; echo "done $NAME $(date -u +%FT%TZ)"
}
NFAIL=0
for IDX in $LIST; do ( run_task $IDX ) || NFAIL=$((NFAIL + 1)); done
echo "tasks: $(echo $LIST | wc -w), failed: $NFAIL"
