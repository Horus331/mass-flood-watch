#!/bin/bash
# P1 rise-rule test (docs/proto/prospective/CHANGE_PROPOSAL_2026-11-07.md) on the terrain-fix (T2) runs kept on Turing: every results/<PREFIX>*<SUFFIX>
# folder with segments.geojson; writes docs/proto/prospective/<OUT>.json and pushes it to main.  Reads model output only; changes no model setting.
#   queue: {"id": "p1test_t2", "kind": "p1test", "env": {"PREFIX": "site_", "SUFFIX": "_t2", "OUT": "p1_rise_test_t2"}   (the queue allows no * in values), "sbatch": {"partition": "short", "time": "02:00:00"}}
#SBATCH -J p1test
#SBATCH -p short
#SBATCH -c 2
#SBATCH --mem=16G
#SBATCH -t 02:00:00
#SBATCH -o p1test_%j.out
set -o pipefail
source proto/turing/env.sh >/dev/null 2>&1 || true
PREFIX=${PREFIX:-site_}; SUFFIX=${SUFFIX:-_t2}; OUT=${OUT:-p1_rise_test_t2}; RUNS="${PREFIX}*${SUFFIX}"
[[ "$PREFIX$SUFFIX" =~ ^[A-Za-z0-9_.-]{1,80}$ ]] && [[ "$OUT" =~ ^[A-Za-z0-9_.-]{1,60}$ ]] || { echo "bad PREFIX / SUFFIX / OUT"; exit 1; }
DIRS=$(ls -d results/${PREFIX}*${SUFFIX} 2>/dev/null); [ -n "$DIRS" ] || { echo "no results/$RUNS"; exit 1; }
echo "runs:"; echo "$DIRS"
python proto/p1_rise_test.py --group t2 --out /tmp/$OUT.$$.json --runs $DIRS || exit 1
exec 8>"$HOME/.mfw_repo_git.lock"; flock -w 1800 8 || echo "git lock wait timed out"
R=$(git remote get-url --push origin)
git pull -q --rebase --autostash "$R" main || true
cp /tmp/$OUT.$$.json docs/proto/prospective/$OUT.json
git add docs/proto/prospective/$OUT.json
git -c user.name="Mohab Eldokla" -c user.email="Horus331@users.noreply.github.com" commit -qm "P1 rise-rule test on Turing T2 runs ($RUNS)" || exit 0
for i in 1 2 3 4 5; do git push -q "$R" HEAD:main && exit 0; git pull -q --rebase "$R" main || git rebase --abort; sleep 20; done
exit 1
