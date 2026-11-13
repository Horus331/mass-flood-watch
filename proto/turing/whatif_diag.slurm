#!/bin/bash
#SBATCH -J mfw_wdiag
#SBATCH -p short
#SBATCH -c 2
#SBATCH --mem=24G
#SBATCH -t 00:45:00
#SBATCH -o whatif_diag_%j.out
# Blocked-culvert diagnostic (docs/proto/whatif/BLOCKED_V2.md): proto/whatif_diag.py on PAIRS (comma separated, e.g. "r100_normal,r075_wet"),
# CPU only, reads the kept what-if runs; pushes docs/proto/whatif/diag_<pair>.json to main.
set -o pipefail
cd ~/mass-flood-watch; source proto/turing/env.sh >/dev/null 2>&1 || true
PAIRS=${PAIRS:-r100_normal}; PAIRS=${PAIRS//,/ }   # the queue allows no spaces in env values: comma separated
for p in $PAIRS; do [[ "$p" =~ ^r[0-9]{3}_(dry|normal|wet|frozen)$ ]] || { echo "bad pair $p"; exit 1; }; done
mkdir -p /tmp/wdiag.$$
for p in $PAIRS; do python proto/whatif_diag.py --pair $p --out /tmp/wdiag.$$/diag_$p.json || echo "diag failed: $p"; done
exec 8>"$HOME/.mfw_repo_git.lock"; flock -w 1800 8 || true
R=$(git remote get-url --push origin)
git pull -q --rebase --autostash "$R" main || true
cp /tmp/wdiag.$$/diag_*.json docs/proto/whatif/ 2>/dev/null || exit 1
git add docs/proto/whatif/diag_*.json
git -c user.name="Mohab Eldokla" -c user.email="Horus331@users.noreply.github.com" commit -qm "What-if blocked-culvert diagnostic: $PAIRS" || exit 0
for i in 1 2 3 4 5; do git push -q "$R" HEAD:main && exit 0; git pull -q --rebase "$R" main || git rebase --abort; sleep 20; done
exit 1
