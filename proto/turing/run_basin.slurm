#!/bin/bash
# One storm over one watershed-shaped domain (LF_DOMAIN=basin, sim/colab/lf_domain.py): only cells that drain to the chosen outlets run;
# the rest of the bounding box is NODATA (LISFLOOD-FP walls), FREE outflow only where the outlet river corridor meets the box edge.
#   sbatch proto/turing/run_basin.slurm                                                              # North Nashua to the Leominster gauge, 20 m
#   sbatch --export=ALL,RES=10,NAME=nn_leominster_10m proto/turing/run_basin.slurm                   # same basin at 10 m
#   sbatch --export=ALL,DOMAIN=docs/network/basins/domain_worcester_bq.json,STORM=aug2021,NAME=worcester_aug2021 proto/turing/run_basin.slurm
#   District 3 by HUC8 basins (independent catchments, one job each):
#   for d in docs/network/basins/domain_d3_hu8_*.json; do sbatch --export=ALL,DOMAIN=$d,NAME=$(basename $d .json)_sep2023 proto/turing/run_basin.slurm; done
# Make a domain first (any machine with internet; basins come from basins.yml):
#   python sim/colab/lf_domain.py build --name <name> --sites <USGS sites> | --hu 8|12 --region x0,y0,x1,y1 [--rain-npz <run>/rainstats.npz --rain-min 75]
#SBATCH -J roadflood_basin
#SBATCH -p quick
#SBATCH -N 1
#SBATCH -n 8
#SBATCH --mem=64G
#SBATCH --gres=gpu:1
#SBATCH -t 12:00:00
#SBATCH -o roadflood_basin_%j.out
set -eo pipefail
source proto/turing/env.sh
export LF_NO_UPLOAD=1 OMP_NUM_THREADS=$SLURM_NTASKS
export LF_DOMAIN=basin LF_DOMAIN_FILE=${DOMAIN:-docs/network/basins/domain_leominster_nn.json}
export RES=${RES:-20} STORM=${STORM:-sep2023} HOURS=${HOURS:-48}
export LF_LOSS=${LF_LOSS:-cn} LF_CN_AMC=${LF_CN_AMC:-II} LF_CN_SCALE=${LF_CN_SCALE:-0.91} LF_INFIL_MMH=${LF_INFIL_MMH:-2} LF_QOUT=${LF_QOUT:-1}
export NAME=${NAME:-nn_leominster_sep2023_${RES}m} RUN_DIR=runs/${STORM}_proto_${NAME}
python -c "import json,sys; d=json.load(open('$LF_DOMAIN_FILE')); print('domain', d['name'], 'box', d['box'], 'basins', d['union_km2'], 'km2 of', d['box_km2'], 'km2 box')"
nvidia-smi || true
time python sim/colab/w9_lisflood.py
OUT=$(ls -d $LF_WORK/run_${STORM}_proto_${NAME}/out)
python proto/prototype.py --run-dir "$OUT" --out "results/$NAME"
python proto/score.py --run-dir "$OUT" --out "results/$NAME/score.json" || true
echo "results in results/$NAME (map.html, watchlist.csv, REPORT.md, summary.json, score.json); mask in $OUT/domain_mask.npy"
