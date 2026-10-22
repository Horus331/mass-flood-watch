#!/bin/bash
# One-time Turing setup, run on the LOGIN node from the repo root:  bash proto/turing/bootstrap.sh
# 1) conda env in ~/envs/roadflood (login node has internet)  2) LISFLOOD-FP 8.2 GPU build on a quick-partition GPU node.
set -eo pipefail
source proto/turing/env.sh
if [ ! -d "$ROADFLOOD_ENV" ]; then conda env create -p "$ROADFLOOD_ENV" -f proto/turing/environment.yml; fi
source proto/turing/env.sh
python -c "import numpy, pyproj, netCDF4; print('env ok', numpy.__version__)"
mkdir -p "$LF_WORK"
# fetch the LISFLOOD-FP source here (login node) so the GPU node needs no internet for the build
python - <<'PY'
import sys, os; sys.path.insert(0, 'sim/colab'); import w9_lisflood as W
z, ver, url = W.get_lisflood(); src = f'{W.WORK}/src'
if not os.path.isdir(src): W.extract_all(z, src)
print('source ready', ver, src)
PY
echo "building on a GPU node (quick partition, up to 1 h)..."
srun -p quick --gres=gpu:1 -c 8 --mem=32G -t 01:00:00 bash proto/turing/setup_lisflood.sh 2>&1 | tail -40
