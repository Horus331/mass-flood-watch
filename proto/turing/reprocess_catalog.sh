#!/bin/bash
# Re-score every catalogue storm run that still has flood outputs in $LF_WORK, extract learned-model features, publish.
#   cd ~/mass-flood-watch && bash proto/turing/reprocess_catalog.sh [RES]
# Jobs run on the CPU 'long' partition in parallel; publish.sh pulls/rebases, so concurrent pushes are safe to retry.
RES=${1:-20}
python3 - "$RES" <<'PY' | while read -r ID NAME; do
import json, sys
res = sys.argv[1]
for e in json.load(open('docs/proto/obs/catalog.json'))['events']:
    if e.get('era') == 'aws': print(e['id'], f"{e['id']}_{e['area']}_{res}m")
PY
  ls -d $HOME/scratch/lisflood/run_${ID}_proto_${NAME}/out >/dev/null 2>&1 || { echo "skip $NAME (no flood output)"; continue; }
  NAME=$NAME STORM=$ID PUBLISH=1 sbatch --export=ALL proto/turing/reprocess.slurm
done
