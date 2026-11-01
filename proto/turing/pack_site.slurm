#!/bin/bash
# Re-score a 5-minute Turing run and pack it for the public replay (docs/site/data/<SITE>/), then push.
#   NAME=leominster_sep2023_5min STORM=sep2023 SITE=leominster_5min sbatch --export=ALL proto/turing/pack_site.slurm
#SBATCH -J pack_site
#SBATCH -p long
#SBATCH -c 8
#SBATCH --mem=64G
#SBATCH -t 03:00:00
#SBATCH -o pack_site_%j.out
set -eo pipefail
source proto/turing/env.sh
python -c "import shapely" 2>/dev/null || pip install -q shapely
OUT=$(ls -d $LF_WORK/run_${STORM}_proto_${NAME}/out)
R=results/$NAME; mkdir -p $R
python proto/score.py --run-dir $OUT --storm $STORM --out $R/score.json | tail -3 || true
python proto/validate_points.py --run-dir $OUT --storm $STORM --out $R/points.json | tail -3 || true
python proto/prototype.py --run-dir $OUT --storm $STORM --out $R | tail -3
python docs/site/build_data.py --run $SITE --src $R --run-dir $OUT $([ "${FLOW:-1}" = 1 ] && echo --flow) ${POOL:+--pool $POOL}
du -sh docs/site/data/$SITE
# whole-district packs (tiled, docs/site/build_data.py build_tiled) are too big for the main site (Pages ~1 GB): they go to the branch
# district-data of this repository (never deployed; the Turing deploy key only reaches this repository), one commit per storm folder.
# From there they are copied to the data site (Horus331/mfw-data-d3, GitHub Pages) and the main site gets a small stub with meta.data_base.
if python -c "import json,sys; sys.exit(0 if (json.load(open('docs/site/data/$SITE/meta.json')).get('depthc') or {}).get('tiles') else 1)"; then
  RM=$(git remote get-url --push origin); W=$LF_WORK/district_data_wt_$SITE; rm -rf $W; git worktree prune
  if git fetch -q "$RM" district-data 2>/dev/null; then git worktree add -q --detach $W FETCH_HEAD
  else git worktree add -q --detach $W HEAD; (cd $W && git checkout -q --orphan district-data-new && git rm -rqf . && echo "Whole-district replay packs (docs/site/build_data.py build_tiled); copied to the data site, not deployed from here." > README.md && git add README.md); fi
  rm -rf $W/$SITE; mv docs/site/data/$SITE $W/$SITE
  (cd $W && git add -A $SITE && git -c user.name="Mohab Eldokla" -c user.email="Horus331@users.noreply.github.com" commit -qm "District data: $SITE from Turing run $NAME" && \
    for i in 1 2 3; do git push -q "$RM" HEAD:refs/heads/district-data && echo "pushed $SITE to district-data" && break; sleep 15; done)
  git worktree remove --force $W || true
  exit 0
fi
if [ -n "${LIVE:-}" ] && [ -d docs/site/data/$LIVE ]; then   # replace a live replay, keeping its radar-rain loop
  cp docs/site/data/$LIVE/rain.* docs/site/data/$SITE/ 2>/dev/null || true
  git rm -rq docs/site/data/$LIVE; rm -rf docs/site/data/$LIVE; mv docs/site/data/$SITE docs/site/data/$LIVE; SITE=$LIVE
fi
git add -A docs/site/data/$SITE
git -c user.name="Mohab Eldokla" -c user.email="Horus331@users.noreply.github.com" commit -qm "Site replay: $SITE from Turing run $NAME (5-min frames, flow)"
for i in 1 2 3 4 5; do git pull -q --rebase --autostash origin main && git push -q origin HEAD:main && echo "pushed $SITE" && exit 0; sleep 15; done
exit 1
