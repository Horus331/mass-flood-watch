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
git add docs/site/data/$SITE
git -c user.name="Mohab Eldokla" -c user.email="Horus331@users.noreply.github.com" commit -qm "Site replay: $SITE from Turing run $NAME (5-min frames, flow)"
for i in 1 2 3 4 5; do git pull -q --rebase --autostash origin main && git push -q origin HEAD:main && echo "pushed $SITE" && exit 0; sleep 15; done
exit 1
