#!/bin/bash
# Score the finished run_storm results of one group (results/<GROUP>_<arm>_<storm>/) and push SMALL json summaries to main (DEST).
#   queue: {"id": "amcnwm_collect_1", "kind": "collect_group", "env": {"GROUP": "amcnwm", "DEST": "docs/proto/runoff/nwm_amc/runs"}, "after": [...]}
#   by hand: GROUP=amcnwm DEST=docs/proto/runoff/nwm_amc/runs sbatch --export=ALL proto/turing/collect_group.slurm
# proto/turing/collect_group.py does the work (score_v2 + gauges + meta json, < 1 MB each; already collected names are skipped unless
# FORCE=1); only DEST is committed, one commit, pushed through the deploy key (as publish.sh).  Re-queue with a new id to pick up stragglers.
#SBATCH -J collect_group
#SBATCH -p short
#SBATCH -c 4
#SBATCH --mem=32G
#SBATCH -t 02:00:00
#SBATCH -o collect_group_%j.out
set -eo pipefail
source proto/turing/env.sh
[[ "${GROUP:-}" =~ ^[a-z0-9]{3,20}$ ]] || { echo "bad GROUP"; exit 2; }
[[ "${DEST:-}" =~ ^docs/proto/[a-z0-9_]+(/[a-z0-9_]+){0,4}$ ]] || { echo "bad DEST"; exit 2; }
R=$(git remote get-url --push origin)     # deploy-key ssh URL (compute nodes cannot fetch over https)
git pull -q --rebase --autostash "$R" main || true
python proto/turing/collect_group.py --group "$GROUP" --dest "$DEST" $([ "${FORCE:-0}" = 1 ] && echo --force)
git add -A "$DEST"
git -c user.name="Mohab Eldokla" -c user.email="Horus331@users.noreply.github.com" commit -qm "Turing scores: $GROUP -> $DEST" || { echo "nothing to commit"; exit 0; }
for i in 1 2 3 4 5 6 7 8; do git pull -q --rebase --autostash "$R" main && git push -q "$R" HEAD:main && echo "pushed $DEST" && exit 0; sleep $((10 + RANDOM % 20)); done
echo "push failed"; exit 1
