#!/bin/bash
# Login-node staging for a basin run, so the GPU job itself needs no internet (whether Turing compute nodes reach the internet is not known yet).
# Fetches everything the run reads from outside services, into $STAGE:
#   * MA domains: Hugging Face data/ tiles (DEM, NLCD, soils, channels) land in the HF cache ($HF_HOME); the job then runs with HF_HUB_OFFLINE=1
#   * Vermont / out-of-state domains (VT=1): sim/colab/vt_inputs.py builds the same data/ layout from public 3DEP / NLCD / SSURGO / NHDPlus HR /
#     OSM / USGS services into $STAGE/data (w9 LF_DATA_DIR), plus segments, crossings, bridges, hospitals and gauges for the domain box
#   * MRMS hourly radar rain for the storm -> $STAGE/mrms (w9 LF_MRMS_DIR cache)
# by running w9 once with LF_INPUTS_ONLY=1, which also builds the basin mask (log line "domain ...") as a check.  Needs LISFLOOD-FP built first
# (bash proto/turing/setup_lisflood.sh) and its path in LF_EXE.
#   DOMAIN=docs/network/basins/domain_leominster_nn.json STORM=sep2023 bash proto/turing/stage_inputs.sh
#   DOMAIN=docs/network/basins/domain_winooski_montpelier.json STORM=jul2023vt VT=1 bash proto/turing/stage_inputs.sh
set -euo pipefail
source activate roadflood 2>/dev/null || conda activate roadflood
: "${DOMAIN:?set DOMAIN=<domain json>}"; : "${STORM:?set STORM}"; : "${LF_EXE:?set LF_EXE to the lisflood built by setup_lisflood.sh}"
NAME=$(basename "$DOMAIN" .json | sed 's/^domain_//')
export STAGE=${STAGE:-$HOME/stage/${NAME}_${STORM}}; mkdir -p "$STAGE"
BOX=$(python -c "import json; print(','.join(str(int(v)) for v in json.load(open('$DOMAIN'))['box']))")
echo "domain $NAME box $BOX -> $STAGE"
if [ "${VT:-0}" = "1" ]; then
  python sim/colab/vt_inputs.py --box "$BOX" --data "$STAGE/data" --out "$STAGE/inputs" --gauges "$STAGE/gauges_${STORM}.json" \
    ${VT_START:+--start $VT_START} ${VT_END:+--end $VT_END} 2>&1 | tee "$STAGE/vt_inputs.log"
  export LF_DATA_DIR=$STAGE/data LF_CROSSINGS=$STAGE/inputs/crossings_vt.json LF_GAUGES=$STAGE/gauges_${STORM}.json
fi
export LF_WORK=$STAGE/lf LF_NO_UPLOAD=1 LF_INPUTS_ONLY=1 LF_MRMS_DIR=$STAGE/mrms LF_DOMAIN=basin LF_DOMAIN_FILE=$DOMAIN STORM RES=${RES:-20}
export LF_LOSS=${LF_LOSS:-cn} LF_CN_AMC=${LF_CN_AMC:-II} LF_CN_SCALE=${LF_CN_SCALE:-0.91} LF_INFIL_MMH=${LF_INFIL_MMH:-2} LF_QOUT=${LF_QOUT:-1}
python sim/colab/w9_lisflood.py 2>&1 | tee "$STAGE/w9_inputs.log" | grep -E "domain|elevation|grid|rain:|LF_INPUTS_ONLY" || true
ls "$STAGE/mrms" | wc -l | xargs echo "MRMS hours cached:"
du -sh "$STAGE"
