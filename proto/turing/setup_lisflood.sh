#!/bin/bash
# One-time setup on Turing: conda env + LISFLOOD-FP 8.2 build (CUDA when a GPU node is used).
# Run inside an interactive GPU session so nvcc and the GPU architecture are visible, e.g.
#   srun -p short --gres=gpu:1 -t 01:00:00 --pty bash      (partition names: ask ARC)
#   bash proto/turing/setup_lisflood.sh
set -euo pipefail
module load cuda 2>/dev/null || module load cuda/12 2>/dev/null || echo "no cuda module found: ask ARC for the module name"
module load miniconda3 2>/dev/null || module load anaconda 2>/dev/null || true
conda env create -f proto/turing/environment.yml -n roadflood 2>/dev/null || conda env update -f proto/turing/environment.yml -n roadflood
source activate roadflood || conda activate roadflood
export LF_WORK=${LF_WORK:-$HOME/lisflood}
# w9 downloads LISFLOOD-FP 8.2 from Zenodo (DOI 10.5281/zenodo.13121102), reads its CMake switches and builds with CUDA if nvcc + GPU exist.
# libnuma headers are needed by its CMake; on a cluster they come from the system or `conda install -c conda-forge numactl`.
python - <<'PY'
import sys, os; sys.path.insert(0, 'sim/colab'); import w9_lisflood as W
z, ver, url = W.get_lisflood(); src = f'{W.WORK}/src'
if not os.path.isdir(src): W.extract_all(z, src)
exe, cuda = W.build_lisflood(W.find_source(src), want_cuda=True); print('built', exe, 'CUDA', cuda)
PY
