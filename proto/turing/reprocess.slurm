#!/bin/bash
# Re-run the closure / scoring steps (no flood model) on an existing run's outputs, e.g. after a prototype.py change.
#   NAME=leominster_sep2023_10m STORM=sep2023 sbatch --export=ALL proto/turing/reprocess.slurm
#   bash proto/turing/reprocess_catalog.sh        # every catalogue run in results/, with ML features, then publish
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
python proto/validate_points.py --run-dir "$OUT" --storm $STORM --out results/$NAME/points.json | tail -3 || true
python proto/prototype.py --run-dir "$OUT" --storm $STORM --out "results/$NAME" | tail -3
cp $OUT/meta.json results/$NAME/flood_meta.json 2>/dev/null || true
LBL=$( (ls proto/data/labels_${STORM}_*.csv proto/data/labels_${STORM}_*.geojson 2>/dev/null || true) | paste -sd, -)
if [ -n "$LBL" ]; then python proto/closure_ml.py extract --run-dir "$OUT" --storm $STORM --labels "$LBL" | tail -2 && cp docs/proto/ml/features_${STORM}.csv docs/proto/ml/matches_${STORM}.json results/$NAME/ 2>/dev/null; git checkout -q -- docs/proto/ml 2>/dev/null || true; fi
echo "reprocessed results/$NAME"
[ "${PUBLISH:-0}" = "1" ] && bash proto/turing/publish.sh "$NAME" || true
