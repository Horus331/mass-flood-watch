#!/bin/bash
# Re-run the closure / scoring steps (no flood model) on an existing run's outputs, e.g. after a prototype.py change.
#   NAME=leominster_sep2023_10m STORM=sep2023 sbatch --export=ALL proto/turing/reprocess.slurm
#SBATCH -J reprocess
#SBATCH -p long
#SBATCH -c 4
#SBATCH --mem=32G
#SBATCH -t 02:00:00
#SBATCH -o reprocess_%j.out
set -eo pipefail
source proto/turing/env.sh
OUT=$(ls -d $LF_WORK/run_${STORM}_proto_${NAME}/out)
mkdir -p results/$NAME
python proto/score.py --run-dir "$OUT" --storm $STORM --out results/$NAME/score.json | tail -5 || true
python proto/prototype.py --run-dir "$OUT" --storm $STORM --out "results/$NAME" | tail -3
echo "reprocessed results/$NAME"
