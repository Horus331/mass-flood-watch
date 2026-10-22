#!/bin/bash
# Vermont July 10-11 2023 flood over the whole Winooski basin above the Montpelier gauge (USGS 04286000) with the Dog River (04287000)
# as a second outlet, 20 m, LISFLOOD-FP 8.2 on one GPU.  The 20 x 20 km Montpelier box got 96 of 654 m3/s at 04286000 because almost all
# of the basin was outside it; here every upstream cell is in the model and nothing enters through an edge (no nesting, no inflows).
# Steps (login node first, it has internet; compute nodes may not):
#   1. bash proto/turing/setup_lisflood.sh                                         # once; note the exe path it prints -> LF_EXE
#   2. DOMAIN=docs/network/basins/domain_winooski_montpelier.json STORM=jul2023vt VT=1 LF_EXE=<exe> bash proto/turing/stage_inputs.sh
#      (3DEP / NLCD / SSURGO / NHDPlus HR / OSM / USGS inputs for the domain box -> $HOME/stage/winooski_montpelier_jul2023vt, MRMS cached)
#   3. sbatch --export=ALL,LF_EXE=<exe>,LF_EXE_CUDA=1 proto/turing/run_vt_basin.slurm
#SBATCH -J vt_basin
#SBATCH -p long
#SBATCH -N 1
#SBATCH -n 8
#SBATCH --mem=96G
#SBATCH --gres=gpu:1
#SBATCH -t 24:00:00
#SBATCH -o vt_basin_%j.out
set -eo pipefail
source proto/turing/env.sh
: "${LF_EXE:?set LF_EXE (setup_lisflood.sh)}"
export DOMAIN=${DOMAIN:-docs/network/basins/domain_winooski_montpelier.json} STORM=jul2023vt
export STAGE=${STAGE:-$HOME/stage/$(basename $DOMAIN .json | sed 's/^domain_//')_${STORM}}
export LF_DOMAIN=basin LF_DOMAIN_FILE=$DOMAIN LF_DATA_DIR=$STAGE/data LF_MRMS_DIR=$STAGE/mrms LF_CROSSINGS=$STAGE/inputs/crossings_vt.json LF_GAUGES=$STAGE/gauges_${STORM}.json
export LF_WORK=${LF_WORK:-$STAGE/lf} LF_NO_UPLOAD=1 OMP_NUM_THREADS=$SLURM_NTASKS HF_HUB_OFFLINE=1
export RES=${RES:-20} HOURS=${HOURS:-60}
export LF_LOSS=${LF_LOSS:-cn} LF_CN_AMC=${LF_CN_AMC:-II} LF_CN_SCALE=${LF_CN_SCALE:-0.91} LF_INFIL_MMH=${LF_INFIL_MMH:-2} LF_QOUT=${LF_QOUT:-1}
export NAME=${NAME:-winooski_jul2023vt_${RES}m} RUN_DIR=runs/${STORM}_proto_${NAME}
[ -d "$LF_DATA_DIR/dem10" ] || { echo "no staged inputs in $STAGE: run proto/turing/stage_inputs.sh on a login node first"; exit 1; }
nvidia-smi || true
time python sim/colab/w9_lisflood.py
OUT=$(ls -d $LF_WORK/run_${STORM}_proto_${NAME}/out)
PROTO_NBI=$STAGE/inputs/bridges_vt.json python proto/prototype.py --run-dir "$OUT" --out "results/$NAME" --segments $STAGE/inputs/segments_vt.json --crossings $STAGE/inputs/crossings_vt.json \
  --facilities $STAGE/inputs/facilities_vt.json --reports none --repeat none --labels proto/data/vt_roadclosures_jul2023.geojson
python proto/score.py --run-dir "$OUT" --obs "$LF_GAUGES" --out "results/$NAME/score.json" || true
echo "results in results/$NAME; mask in $OUT/domain_mask.npy; gauge flows in $OUT/xings.json"
