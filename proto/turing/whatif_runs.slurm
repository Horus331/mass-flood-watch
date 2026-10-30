#!/bin/bash
# What-if storm explorer (docs/proto/whatif/WHATIF.md): one GPU array task per scenario of proto/whatif.py (Leominster box, Sept 11 2023),
# LISFLOOD-FP with the baseline settings plus that scenario's inputs, then prototype.py + cascade.py on it. No push: whatif_pack.slurm
# packs every finished scenario for the site and publishes once.
#   sbatch --array=0-31%8 proto/turing/whatif_runs.slurm          (RERUN=1 reruns scenarios that already have results)
#SBATCH -J whatif_run
#SBATCH -p short
#SBATCH -N 1
#SBATCH -n 8
#SBATCH --mem=64G
#SBATCH --gres=gpu:1
#SBATCH -t 01:30:00
#SBATCH -o whatif_run_%A_%a.out
set -eo pipefail
cd ~/mass-flood-watch
source proto/turing/env.sh
eval "$(python proto/whatif.py env ${SLURM_ARRAY_TASK_ID:-0})"      # exports NAME, BOX, STORM, HOURS, RES and the LF_* of this scenario
export OMP_NUM_THREADS=${SLURM_NTASKS:-8} GIT_SHA=$(git rev-parse --short HEAD 2>/dev/null || true)
export RUN_DIR=runs/${STORM}_proto_${NAME}
R=results/$NAME
if [ -s $R/summary.json ] && [ "${RERUN:-0}" != 1 ]; then echo "$WHATIF_ID already done ($R)"; exit 0; fi
echo "== $WHATIF_ID: $(env | grep -E '^LF_(RAIN_SCALE|CN_AMC|CN_FROZEN|INFIL_MMH|XINGS_BLOCKED|CN_SCALE|PARITY|SAVEINT)=' | sort | tr '\n' ' ')"
nvidia-smi -L || true
time python sim/colab/w9_lisflood.py
OUT=$(ls -d $LF_WORK/run_${STORM}_proto_${NAME}/out)
mkdir -p $R
python proto/score.py --run-dir "$OUT" --storm $STORM --out $R/score.json | tail -4 || true
python proto/prototype.py --run-dir "$OUT" --storm $STORM --out $R | tail -3
python proto/cascade.py outdir $R | tail -1 || true
cp $OUT/meta.json $R/flood_meta.json 2>/dev/null || true
echo "done $WHATIF_ID -> $R"
