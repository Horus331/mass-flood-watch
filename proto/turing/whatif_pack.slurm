#!/bin/bash
# Pack every finished what-if scenario (proto/whatif.py pack) into docs/site/data/whatif/ and publish ONCE (one push to main, one site
# redeploy). Run after whatif_runs.slurm (whatif_pipeline.slurm submits it with afterany, so a failed scenario does not block the rest).
#SBATCH -J whatif_pack
#SBATCH -p short
#SBATCH -N 1
#SBATCH -c 8
#SBATCH --mem=48G
#SBATCH -t 04:00:00
#SBATCH -o whatif_pack_%j.out
set -eo pipefail
cd ~/mass-flood-watch
source proto/turing/env.sh
python -c "import shapely" 2>/dev/null || pip install -q shapely
R=$(git remote get-url --push origin)
git pull -q --rebase --autostash "$R" main || true
python proto/whatif.py pack --results results ${ONLY:+--only $ONLY}
du -sh docs/site/data/whatif
# provenance next to the other Turing results: the scenario index and each scenario's small result files
mkdir -p results/whatif_site && cp docs/site/data/whatif/index.json results/whatif_site/
for d in results/whatif_r*; do [ -d "$d" ] || continue; k=$(basename $d); mkdir -p results/whatif_site/$k
  cp $d/summary.json $d/score.json $d/flood_meta.json results/whatif_site/$k/ 2>/dev/null || true; done
python - <<'PY'
import json; s = json.load(open('results/whatif_site/index.json'))
rows = ['| scenario | status | rain (box mean, mm) | segments closed | peak closed at once | people cut off (peak) | culverts overtopped | MB |', '|' + ' --- |' * 8]
for k, v in s['scenarios'].items():
    rows.append(f"| {k} | {v.get('status')} | {v.get('rain_total_mm', '')} | {v.get('segments_closed', '')} | {v.get('peak_closed', '')} | {v.get('people_cut_off', '')} | {v.get('culverts_overtopped', '')} | {v.get('size_mb', '')} |")
open('results/whatif_site/RESULTS.md', 'w').write(f"# What-if scenarios, packed {s['made']}\n\n{s['n_ok']} of {s['n']} scenarios. Settings: docs/proto/whatif/WHATIF.md.\n\n" + '\n'.join(rows) + '\n')
PY
PUBLISH_EXTRA=docs/site/data/whatif bash proto/turing/publish.sh whatif_site
