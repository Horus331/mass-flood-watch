#!/bin/bash
# Submit one GPU job per catalogue storm (docs/proto/obs/catalog.json, events with era 'aws' = MRMS Pass2 on AWS) at RES (default 20).
#   cd ~/mass-flood-watch && bash proto/turing/submit_catalog.sh [RES] [ids...]
# Jobs run one after another (Turing allows one quick-partition GPU per user); results land in results/<id>_<area>_<RES>m/.
RES=${1:-20}; shift || true
python3 - "$RES" "$@" <<'PY' | while read -r ID BOX T0 HOURS NAME; do
import json, sys
res = sys.argv[1]; want = set(sys.argv[2:])
for e in json.load(open('docs/proto/obs/catalog.json'))['events']:
    if e.get('era') != 'aws' or (want and e['id'] not in want): continue
    print(e['id'], ','.join(str(v) for v in e['box_26986']), e['t0'], e['hours'], f"{e['id']}_{e['area']}_{res}m")
PY
  BOX=$BOX STORM=$ID T0=$T0 HOURS=$HOURS RES=$RES NAME=$NAME sbatch --export=ALL proto/turing/run_storm.slurm
done
