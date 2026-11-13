#!/bin/bash
#SBATCH -J mfw_wv3
#SBATCH -p short
#SBATCH -c 2
#SBATCH --mem=32G
#SBATCH -t 01:30:00
#SBATCH -o whatif_v3_%j.out
# Blocked culverts version 3 (docs/proto/whatif/PREREG_BLOCKED_V3.md): proto/whatif_v3.py on the existing open / blocked solves, CPU only;
# pushes docs/proto/whatif/blocked_v3.json to main.  PAIRS comma separated (the queue allows no spaces).
set -o pipefail
cd ~/mass-flood-watch; source proto/turing/env.sh >/dev/null 2>&1 || true
PAIRS=${PAIRS:-r050_dry,r050_wet,r075_dry,r075_frozen,r075_normal,r075_wet,r100_frozen,r100_normal,r100_wet,r125_dry,r125_normal,r125_wet}
[[ "$PAIRS" =~ ^(r[0-9]{3}_(dry|normal|wet|frozen),?)+$ ]] || { echo "bad PAIRS $PAIRS"; exit 1; }
mkdir -p /tmp/wv3.$$
python proto/whatif_v3.py --pairs "$PAIRS" --out /tmp/wv3.$$/blocked_v3.json || exit 1
exec 8>"$HOME/.mfw_repo_git.lock"; flock -w 1800 8 || true
R=$(git remote get-url --push origin)
git pull -q --rebase --autostash "$R" main || true
cp /tmp/wv3.$$/blocked_v3.json docs/proto/whatif/ || exit 1
git add docs/proto/whatif/blocked_v3.json
git -c user.name="Mohab Eldokla" -c user.email="Horus331@users.noreply.github.com" commit -qm "What-if blocked culverts v3 result" || exit 0
for i in 1 2 3 4 5; do git push -q "$R" HEAD:main && exit 0; git pull -q --rebase "$R" main || git rebase --abort; sleep 20; done
exit 1
