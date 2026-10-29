#!/bin/bash
# Dataset -> model A (train split, val-picked step) -> model B (every generated scene, same steps) -> the pre-registered evaluation
# (docs/proto/surrogate/SURROGATE.md) -> docs/proto/surrogate/RESULTS.md + results.json and docs/proto/turing/surrogate_eval/ (one push;
# with K=2: RESULTS_k2.md, results_k2.json, surrogate_eval_k2/, and separate dataset / model / eval folders, so nothing of the first is lost).
# Needs: surrogate_gen.slurm outputs ($SURR_ROOT/run_*/out), surrogate_inputs.slurm outputs ($SURR_ROOT/inputs/*), PyTorch with CUDA in the env:
#   conda activate ~/envs/roadflood && pip install torch --index-url https://download.pytorch.org/whl/cu126      # once, login node
#   cd ~/mass-flood-watch && git pull
#   sbatch --export=ALL,PLANS=$HOME/scratch/surrogate/plan_b1.json proto/turing/surrogate_train.slurm     # ~4-6 h, ~3 GPU-h used
# After batch 2 (SURROGATE.md section 6): PLANS=plan_b1.json,plan_b2.json and K=2 (the second and last evaluation; alpha / 2).
# PUBLISH=0 keeps everything on Turing.  Heavy outputs stay in $SURR_ROOT/{dataset,models,eval}; only small files go to GitHub.
#SBATCH -J surr_train
#SBATCH -p long
#SBATCH -N 1
#SBATCH -n 8
#SBATCH --mem=128G
#SBATCH --gres=gpu:1
#SBATCH -t 16:00:00
#SBATCH -o surr_train_%j.out
set -eo pipefail
source proto/turing/env.sh
: "${PLANS:?set PLANS=<plan json>[,<plan json>]}"
K=${K:-1}; SFX=$( [ "$K" = 1 ] && echo "" || echo "_k$K" ); NAME=surrogate_eval$SFX
SURR_ROOT=${SURR_ROOT:-$HOME/scratch/surrogate}; DATA=$SURR_ROOT/dataset$SFX; M=$SURR_ROOT/models$SFX; EV=$SURR_ROOT/eval$SFX; RES=results/$NAME
export GIT_SHA=$(git rev-parse --short HEAD 2>/dev/null || true) OMP_NUM_THREADS=${SLURM_NTASKS:-8}
python -c "import torch; print('torch', torch.__version__, 'cuda', torch.cuda.is_available())" || { echo "PyTorch missing: see the header of this script"; exit 2; }
nvidia-smi -L || true
[ -s "$SURR_ROOT/inputs_plan.json" ] || python proto/surrogate/scenarios.py inputs --out "$SURR_ROOT/inputs_plan.json"
time python proto/surrogate/dataset.py build --root "$SURR_ROOT" --plans "$PLANS" --inputs-plan "$SURR_ROOT/inputs_plan.json" --out "$DATA"
mkdir -p "$M"
time python proto/surrogate/train.py --data "$DATA" --model A --out "$M/A.pt"
time python proto/surrogate/train.py --data "$DATA" --model B --iters-from "$M/A.pt" --out "$M/B.pt"
time python proto/surrogate/evaluate.py eval --data "$DATA" --model-a "$M/A.pt" --model-b "$M/B.pt" --out "$EV" --doc docs/proto/surrogate --threads 4 --k $K
# small files for GitHub (publish.sh copies results/<name>/ to docs/proto/turing/<name>/)
rm -rf "$RES"; mkdir -p "$RES"
cp "$EV/results.json" "$EV/RESULTS.md" "$RES/"; cp "$EV"/score_*.json "$RES/" 2>/dev/null || true
cp "$DATA/index.json" "$RES/dataset_index.json"; cp "$DATA/norm.json" "$RES/"; for p in ${PLANS//,/ }; do cp "$p" "$RES/"; done
cp "$M/B.pt" "$RES/model_B.pt"; cp "$M/A.pt" "$RES/model_A.pt"
echo "results in $RES and docs/proto/surrogate/RESULTS$SFX.md"
[ "${PUBLISH:-1}" = "1" ] && PUBLISH_EXTRA="docs/proto/surrogate/RESULTS$SFX.md docs/proto/surrogate/results$SFX.json" bash proto/turing/publish.sh $NAME || true
