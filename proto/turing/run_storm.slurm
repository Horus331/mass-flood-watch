#!/bin/bash
# One storm over one area: rain (MRMS) -> LISFLOOD-FP 8.2 flood depth on GPU -> road-closure probability, network cost, watchlist, map.
#   sbatch proto/turing/run_storm.slurm                                   # Leominster 20 x 20 km, 20 m (the GitHub-tested case)
#   BOX=128000,856000,206000,946000 RES=20 NAME=d3_sep2023_20m sbatch --export=ALL proto/turing/run_storm.slurm   # all of District 3 (set BOX in the shell: --export splits on commas)
#SBATCH -J roadflood
#SBATCH -p quick
#SBATCH -N 1
#SBATCH -n 8
#SBATCH --mem=64G
#SBATCH --gres=gpu:1
#SBATCH -t 08:00:00
#SBATCH -o roadflood_%j.out
set -eo pipefail
source proto/turing/env.sh
export LF_NO_UPLOAD=1 OMP_NUM_THREADS=$SLURM_NTASKS
export BOX=${BOX:-168000,908000,188000,928000} RES=${RES:-20} STORM=${STORM:-sep2023} HOURS=${HOURS:-48} LF_LOSS=${LF_LOSS:-cn} LF_CN_SCALE=${LF_CN_SCALE:-0.91} LF_INFIL_MMH=${LF_INFIL_MMH:-2} LF_QOUT=${LF_QOUT:-1} LF_VOUT=${LF_VOUT:-1}
# CPU/GPU parity (docs/proto/parity/PARITY.md): the CUDA solver ignores the infiltration keyword and caps every step at initial_tstep;
# LF_PARITY=1 (= LF_INFIL_MODE=rain LF_INIT_TSTEP=1) gives the CPU and GPU builds the same physics and time step
export GIT_SHA=${GIT_SHA:-$(git rev-parse --short HEAD 2>/dev/null || true)}
export NAME=${NAME:-leominster_sep2023_gpu}
export RUN_DIR=runs/${STORM}_proto_${NAME}
nvidia-smi || true
echo "== net check"; for u in https://huggingface.co https://noaa-mrms-pds.s3.amazonaws.com; do printf "%s " $u; curl -s -o /dev/null -m 10 -w "%{http_code}\n" $u; done
time python sim/colab/w9_lisflood.py
OUT=$(ls -d $LF_WORK/run_${STORM}_proto_${NAME}/out)
mkdir -p results/$NAME
SCORE_WINDOWS=results/$NAME/gauge_windows.npz python proto/score.py --run-dir "$OUT" --storm $STORM --out results/$NAME/score.json | tail -30 || true
python proto/parity_pack.py "$OUT" results/$NAME || true     # hmax + snapshot peak (cm), .mass: CPU/GPU parity (docs/proto/parity/PARITY.md)
python proto/validate_points.py --run-dir "$OUT" --storm $STORM --out results/$NAME/points.json | tail -12 || true
python proto/prototype.py --run-dir "$OUT" --storm $STORM --out "results/$NAME" | tail -5
cp $OUT/meta.json results/$NAME/flood_meta.json 2>/dev/null || true
LBL=$( (ls proto/data/labels_${STORM}_*.csv proto/data/labels_${STORM}_*.geojson 2>/dev/null || true) | paste -sd, -)   # ls exits 2 when one glob is empty: keep pipefail from killing the job
if [ -n "$LBL" ]; then python proto/closure_ml.py extract --run-dir "$OUT" --storm $STORM --labels "$LBL" | tail -2 && cp docs/proto/ml/features_${STORM}.csv docs/proto/ml/matches_${STORM}.json results/$NAME/ 2>/dev/null; git checkout -q -- docs/proto/ml 2>/dev/null || true; fi   # per-segment ML features for the learned closure model
echo "results in results/$NAME (map.html, watchlist.csv, REPORT.md, summary.json, score.json)"
[ "${PUBLISH:-1}" = "1" ] && bash proto/turing/publish.sh "$NAME" || true
