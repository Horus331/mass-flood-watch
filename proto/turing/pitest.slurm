#!/bin/bash
#SBATCH -J mfw_pitest
#SBATCH -p short
#SBATCH -c 4
#SBATCH --mem=48G
#SBATCH -t 03:00:00
#SBATCH -o pitest_%j.out
# Live calibrated probability (docs/proto/latent/PREREG_LIVE_PI.md checks 1-3): proto/latent_live.py check on the runs kept on Turing,
# results/<PREFIX>*<SUFFIX> (features_<storm>.csv + segments.geojson). CPU only. Writes docs/proto/latent/<OUT>.json and pushes it to main.
#   CMD=heldout: leave-one-storm-out refit (PREREG_PI_HELDOUT.md) instead of the frozen-fit checks.
#   queue: {"id": "pitest_t2", "kind": "pitest", "env": {"PREFIX": "site_", "SUFFIX": "_t2", "OUT": "live_pi_check_t2"}, "sbatch": {"partition": "short", "time": "03:00:00"}}
set -o pipefail
source proto/turing/env.sh >/dev/null 2>&1 || true
PREFIX=${PREFIX:-site_}; SUFFIX=${SUFFIX:-_t2}; OUT=${OUT:-live_pi_check_t2}; CMD=${CMD:-check}
[[ "$CMD" =~ ^(check|heldout)$ ]] || { echo "bad CMD"; exit 1; }
[[ "$PREFIX$SUFFIX" =~ ^[A-Za-z0-9_.-]{1,80}$ ]] && [[ "$OUT" =~ ^[A-Za-z0-9_.-]{1,60}$ ]] || { echo "bad PREFIX / SUFFIX / OUT"; exit 1; }
DIRS=$(ls -d results/${PREFIX}*${SUFFIX} 2>/dev/null); [ -n "$DIRS" ] || { echo "no results/${PREFIX}*${SUFFIX}"; exit 1; }
echo "runs:"; echo "$DIRS"; for d in $DIRS; do ls $d/features_*.csv >/dev/null 2>&1 || echo "  no features csv: $d"; done
export LATENT_SCRATCH=${LF_WORK:-$HOME}/latent_scratch
python proto/latent_live.py ${CMD:-check} --runs $DIRS --out /tmp/$OUT.$$.json || exit 1
exec 8>"$HOME/.mfw_repo_git.lock"; flock -w 1800 8 || echo "git lock wait timed out"
R=$(git remote get-url --push origin)
git pull -q --rebase --autostash "$R" main || true
cp /tmp/$OUT.$$.json docs/proto/latent/$OUT.json
git add docs/proto/latent/$OUT.json
git -c user.name="Mohab Eldokla" -c user.email="Horus331@users.noreply.github.com" commit -qm "Calibrated probability ${CMD:-check} on Turing runs ${PREFIX}*${SUFFIX}" || exit 0
for i in 1 2 3 4 5; do git push -q "$R" HEAD:main && exit 0; git pull -q --rebase "$R" main || git rebase --abort; sleep 20; done
exit 1
