# Source from the repo root on Turing: modules + conda env for the road-closure model (checked on login-02, 22 Oct 2026).
# Turing modules are Spack builds with hashed names (e.g. cuda/12.6.3/5fe76nu); pick by version prefix.
_mod() { module -t avail 2>&1 | grep -m1 "^$1" ; }
module load "$(_mod miniconda3/25.1)" "$(_mod cuda/12.6)" 2>/dev/null || module load "$(_mod miniconda3/)" "$(_mod cuda/12)" 2>/dev/null || true
source "$(conda info --base)/etc/profile.d/conda.sh"
export ROADFLOOD_ENV=${ROADFLOOD_ENV:-$HOME/envs/roadflood}
[ -d "$ROADFLOOD_ENV" ] && conda activate "$ROADFLOOD_ENV"
export CMAKE_PREFIX_PATH=${CONDA_PREFIX:-}${CMAKE_PREFIX_PATH:+:$CMAKE_PREFIX_PATH}
export LF_WORK=${LF_WORK:-$HOME/scratch/lisflood}
