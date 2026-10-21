#!/bin/bash
# One storm over one area: rain (MRMS) -> LISFLOOD-FP 8.2 flood depth on GPU -> road-closure probability, network cost, watchlist, map.
#   sbatch proto/turing/run_storm.slurm                                   # Leominster 20 x 20 km, 20 m (the GitHub-tested case)
#   sbatch --export=ALL,BOX=128000,856000,206000,946000,RES=10,NAME=d3_sep2023_10m proto/turing/run_storm.slurm   # all of MassDOT District 3
#SBATCH -J roadflood
#SBATCH -N 1
#SBATCH -n 8
#SBATCH --mem=64G
#SBATCH --gres=gpu:1
#SBATCH -t 08:00:00
#SBATCH -o roadflood_%j.out
set -euo pipefail
module load cuda 2>/dev/null || module load cuda/12 2>/dev/null || true
source activate roadflood 2>/dev/null || conda activate roadflood
export LF_WORK=${LF_WORK:-$HOME/lisflood} LF_NO_UPLOAD=1 OMP_NUM_THREADS=$SLURM_NTASKS
export BOX=${BOX:-168000,908000,188000,928000} RES=${RES:-20} STORM=${STORM:-sep2023} HOURS=${HOURS:-36} LF_LOSS=${LF_LOSS:-fc}
export NAME=${NAME:-leominster_sep2023_gpu} RUN_DIR=runs/${STORM}_proto_${NAME}
nvidia-smi || true
/usr/bin/time -v python sim/colab/w9_lisflood.py
OUT=$(ls -d $LF_WORK/run_${STORM}_proto_${NAME}/out)
python proto/prototype.py --run-dir "$OUT" --out "results/$NAME"
echo "results in results/$NAME (map.html, watchlist.csv, REPORT.md, summary.json)"
