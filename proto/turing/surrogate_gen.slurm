#!/bin/bash
# Training runs for the LISFLOOD-FP surrogate (docs/proto/surrogate/SURROGATE.md): each array task runs PER_TASK scenarios of a plan with
# sim/colab/w9_lisflood.py at the frozen baseline (LF_PARITY=1, CN x 0.88, 2 mm/h, 20 m; set by the plan) plus LF_SURR_SAVE=1, and keeps
#   $SURR_ROOT/run_<id>/out/  hmax.npy hsnap.npy meta.json surr_inputs.npz timing.npz vel_max.npz lisflood.mass w9_log.txt
# (raw LISFLOOD-FP files are deleted).  A scenario whose hmax.npy and surr_inputs.npz exist is skipped, so a task can simply be resubmitted.
# Nothing is published from here (no git push); back up with  bash proto/turing/backup_hf.sh --runs-root ~/scratch/surrogate --prefix runs/surrogate
#   cd ~/mass-flood-watch && git pull
#   python proto/surrogate/scenarios.py scan --out ~/scratch/surrogate/scan.json                      # login node (internet), ~1 h
#   python proto/surrogate/scenarios.py plan --scan ~/scratch/surrogate/scan.json --batch 1 --out ~/scratch/surrogate/plan_b1.json   # prints the line below
#   sbatch --array=0-23%4 --export=ALL,PLAN=$HOME/scratch/surrogate/plan_b1.json,PER_TASK=8 proto/turing/surrogate_gen.slurm
# One task = 8 box scenarios ~ 40 min on one GPU node (inputs 2-3 min, solver 1-2 min, post 1 min each); district scenarios ~ 55 min each.
# If the long partition gives no GPU, use  sbatch -p quick --array=0-23%1 ...  (one quick GPU per user: about 16 h for batch 1).
#SBATCH -J surr_gen
#SBATCH -p long
#SBATCH -N 1
#SBATCH -n 8
#SBATCH --mem=96G
#SBATCH --gres=gpu:1
#SBATCH -t 06:00:00
#SBATCH -o surr_gen_%A_%a.out
set -eo pipefail
source proto/turing/env.sh
: "${PLAN:?set PLAN=<plan json from proto/surrogate/scenarios.py plan>}"
PER_TASK=${PER_TASK:-8}; SURR_ROOT=${SURR_ROOT:-$HOME/scratch/surrogate}; TASK=${SLURM_ARRAY_TASK_ID:-0}
export OMP_NUM_THREADS=${SLURM_NTASKS:-8} LF_MRMS_DIR=${LF_MRMS_DIR:-$SURR_ROOT/mrms_cache} GIT_SHA=$(git rev-parse --short HEAD 2>/dev/null || true)
N=$(python -c "import json; print(len(json.load(open('$PLAN'))['scenarios']))")
WORK=$SURR_ROOT/work/task_${SLURM_ARRAY_JOB_ID:-0}_${TASK}
nvidia-smi -L || true
echo "== net check"; for u in https://huggingface.co https://noaa-mrms-pds.s3.amazonaws.com https://noaa-hrrr-bdp-pds.s3.amazonaws.com; do printf "%s " $u; curl -s -o /dev/null -m 10 -w "%{http_code}\n" $u; done
for ((i = TASK * PER_TASK; i < (TASK + 1) * PER_TASK && i < N; i++)); do
  (
    eval "$(python proto/surrogate/scenarios.py env --plan "$PLAN" --index $i)"
    DEST=$SURR_ROOT/run_${SURR_ID}/out
    if [ -s "$DEST/hmax.npy" ] && [ -s "$DEST/surr_inputs.npz" ]; then echo "$SURR_ID: done already"; exit 0; fi
    export LF_WORK=$WORK; rm -rf "$LF_WORK"; mkdir -p "$LF_WORK"
    echo "== [$i] $SURR_ID box $BOX t0 $T0 ${HOURS} h rain ${LF_RAIN:-mrms} ${LF_HRRR_INIT:-} nbhd ${LF_HRRR_NBHD:-none} scale ${LF_RAIN_SCALE:-1} shift ${LF_RAIN_SHIFT_M:-0}"
    t0=$(date +%s)
    if python sim/colab/w9_lisflood.py > "$LF_WORK/w9.out" 2>&1; then
      O=$LF_WORK/run_${SURR_ID}_lf/out; mkdir -p "$DEST"
      for f in hmax.npy hsnap.npy meta.json surr_inputs.npz timing.npz vel_max.npz lisflood.mass w9_log.txt xings.json rainstats.npz; do if [ -e "$O/$f" ]; then mv "$O/$f" "$DEST/"; fi; done
      echo "$SURR_ID ok in $(( $(date +%s) - t0 )) s: $(grep -o 'LISFLOOD-FP run [0-9]*s' "$LF_WORK/w9.out" | tail -1)"
    else
      echo "FAILED $SURR_ID"; tail -25 "$LF_WORK/w9.out"; mkdir -p "$SURR_ROOT/failed"; cp "$LF_WORK/w9.out" "$SURR_ROOT/failed/$SURR_ID.out"
    fi
    rm -rf "$LF_WORK"
  ) || echo "scenario $i: error (see above)"
done
echo "task $TASK done: $(ls -d $SURR_ROOT/run_*/out 2>/dev/null | wc -l) scenario outputs in $SURR_ROOT"
