#!/bin/bash
# Inputs (no flood model) for the surrogate's evaluation (docs/proto/surrogate/SURROGATE.md): w9_lisflood.py with LF_INPUTS_ONLY=1 LF_SURR_SAVE=1
# for the 23 held-out + 2 dev catalogue storms on their catalogue boxes and windows, District 3 Sept 2023 (radar, as d3_sep2023_p) and the
# District 3 HRRR 18z hindcast (as hindcast_d3_sep2023_18z).  The flood depths they are compared with are the published LISFLOOD-FP runs in the
# repo; nothing is re-run.  Locked storms are never touched (scenarios.py inputs refuses them).  CPU only.
#   cd ~/mass-flood-watch && git pull && sbatch proto/turing/surrogate_inputs.slurm        # ~2-3 h; -> ~/scratch/surrogate/inputs/<name>/surr_inputs.npz
#SBATCH -J surr_inputs
#SBATCH -p long
#SBATCH -N 1
#SBATCH -c 8
#SBATCH --mem=128G
#SBATCH -t 10:00:00
#SBATCH -o surr_inputs_%j.out
set -eo pipefail
source proto/turing/env.sh
SURR_ROOT=${SURR_ROOT:-$HOME/scratch/surrogate}; mkdir -p "$SURR_ROOT"
export OMP_NUM_THREADS=${SLURM_CPUS_PER_TASK:-8} LF_MRMS_DIR=${LF_MRMS_DIR:-$SURR_ROOT/mrms_cache} GIT_SHA=$(git rev-parse --short HEAD 2>/dev/null || true)
IP=$SURR_ROOT/inputs_plan.json
python proto/surrogate/scenarios.py inputs --out "$IP"
N=$(python -c "import json; print(len(json.load(open('$IP'))['items']))")
for ((i = 0; i < N; i++)); do
  (
    eval "$(python proto/surrogate/scenarios.py inputs --out "$IP" --index $i)"
    DEST=$SURR_ROOT/inputs/$SURR_NAME
    if [ -s "$DEST/surr_inputs.npz" ]; then echo "$SURR_NAME: done already"; exit 0; fi
    mkdir -p "$DEST"; export LF_WORK=$SURR_ROOT/work/inputs_$SURR_NAME LF_SURR_OUT=$DEST/surr_inputs.npz; rm -rf "$LF_WORK"; mkdir -p "$LF_WORK"
    t0=$(date +%s)
    if python sim/colab/w9_lisflood.py > "$DEST/w9_inputs.log" 2>&1 && [ -s "$DEST/surr_inputs.npz" ]; then echo "$SURR_NAME ok in $(( $(date +%s) - t0 )) s"
    else echo "FAILED $SURR_NAME"; tail -20 "$DEST/w9_inputs.log"; rm -f "$DEST/surr_inputs.npz"; fi
    rm -rf "$LF_WORK"
  ) || echo "item $i: error"
done
ls -la "$SURR_ROOT"/inputs/*/surr_inputs.npz | wc -l | xargs echo "inputs ready:"
