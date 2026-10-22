#!/bin/bash
# One-time setup on Turing: conda env + LISFLOOD-FP 8.2 build (CUDA when a GPU node is used).
# Run inside an interactive GPU session so nvcc and the GPU architecture are visible, e.g.
#   srun -p short --gres=gpu:1 -t 01:00:00 --pty bash      (partition names: ask ARC)
#   bash proto/turing/setup_lisflood.sh
set -eo pipefail
source proto/turing/env.sh
# w9 downloads LISFLOOD-FP 8.2 from Zenodo (DOI 10.5281/zenodo.13121102), reads its CMake switches and builds with CUDA if nvcc + GPU exist.
# libnuma headers are needed by its CMake; on a cluster they come from the system or `conda install -c conda-forge numactl`.
python - <<'PY'
import sys, os; sys.path.insert(0, 'sim/colab'); import w9_lisflood as W
src = f'{W.WORK}/src'
if not os.path.isdir(src): z, ver, url = W.get_lisflood(); W.extract_all(z, src)   # bootstrap.sh fetches it on the login node
exe, cuda = W.build_lisflood(W.find_source(src), want_cuda=True); print('built', exe, 'CUDA', cuda)
PY
