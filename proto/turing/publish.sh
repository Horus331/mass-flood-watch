#!/bin/bash
# Push a Turing run's results to GitHub (docs/proto/turing/<NAME>/) through the repo deploy key (ssh host alias github-mfw).
#   cd ~/mass-flood-watch && bash proto/turing/publish.sh <NAME> [<NAME> ...]
# Copies results/<NAME>/ without files over 40 MB (GitHub limit 100 MB; keeps the repo small), commits only that folder, rebases, pushes.
set -eo pipefail
cd "$(dirname "$0")/../.."
for NAME in "$@"; do
  SRC=results/$NAME; DST=docs/proto/turing/$NAME
  [ -d "$SRC" ] || { echo "no $SRC"; continue; }
  mkdir -p "$DST"; rsync -a --delete --max-size=40m "$SRC"/ "$DST"/
  git add -A "$DST"
done
git -c user.name="Mohab Eldokla" -c user.email="Horus331@users.noreply.github.com" commit -qm "Turing results: $*" || { echo "nothing to commit"; exit 0; }
for i in 1 2 3 4 5; do git pull -q --rebase --autostash origin main && git push -q origin HEAD:main && echo "published: $*" && exit 0; sleep 10; done
echo "push failed"; exit 1
