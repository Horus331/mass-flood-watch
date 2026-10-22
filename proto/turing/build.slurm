#!/bin/bash
# Build LISFLOOD-FP 8.2 (CUDA, then CPU fallback) on a GPU node; full compiler log in build_<jobid>.log, errors summarised at the end.
#   cd ~/mass-flood-watch && sbatch proto/turing/build.slurm
#SBATCH -J lf_build
#SBATCH -p quick
#SBATCH --gres=gpu:1
#SBATCH -c 8
#SBATCH --mem=32G
#SBATCH -t 01:00:00
#SBATCH -o build_%j.log
set -o pipefail
source proto/turing/env.sh
export LF_CUDA_ARCH=${LF_CUDA_ARCH:-80;89;90;120}   # A100, L40S, H100/H200, RTX Pro 6000 (Blackwell needs CUDA >= 12.8)
echo "== tools"; which nvcc gcc g++ cmake; nvcc --version | tail -2; gcc --version | head -1; nvidia-smi --query-gpu=name,compute_cap --format=csv
rm -rf $LF_WORK/build_cuda $LF_WORK/build_cpu   # fresh configure (arch / CUDA version may have changed)
python - <<'PY'
import sys, os; sys.path.insert(0, 'sim/colab'); import w9_lisflood as W
src = f'{W.WORK}/src'
if not os.path.isdir(src): z, ver, url = W.get_lisflood(); W.extract_all(z, src)
try:
    exe, cuda = W.build_lisflood(W.find_source(src), want_cuda=True); print('BUILT', exe, 'CUDA', cuda)
except Exception as e: print('BUILD FAILED', e)
PY
for b in build_cuda; do
  echo "== errors in $b"; cmake --build $LF_WORK/$b -j 1 2>&1 | grep -E -B2 -A3 "error[: ]" | grep -v -i warning | head -60
done
