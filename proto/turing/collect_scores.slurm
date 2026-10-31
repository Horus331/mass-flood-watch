#!/bin/bash
# Bring the small score files of a planned batch back to main (one commit), e.g. the LF_INLETS test (docs/proto/drains/INLETS_PREREG.md).
#   queue: {"id": "inl1_collect", "kind": "collect_scores", "env": {"PLAN": "proto/turing/plans/inlets_v1.json", "WAIT_H": "40"},
#           "sbatch": {"partition": "long", "time": "2-00:00:00"}}
# Reads the plan (proto/turing/plans/<plan>.json: results_root, dest, tasks[].name), waits up to WAIT_H hours (polling every 10 min) until every
# task folder $LF_WORK/<results_root>/<name>/ has DONE or FAILED, then copies ONLY whitelisted small files (score_v2.json, score.json,
# points.json, flood_meta.json, w9_tail.txt, FAILED; each <= 400 kB) into <dest>/<name>/ on main, writes <dest>/manifest.json and pushes
# once through the deploy key (as publish.sh).  WAIT_H=0 publishes whatever is there now (re-queue with a new id to pick up stragglers).
#SBATCH -J collect_scores
#SBATCH -p long
#SBATCH -c 1
#SBATCH --mem=2G
#SBATCH -t 2-00:00:00
#SBATCH -o collect_scores_%j.out
set -eo pipefail
source proto/turing/env.sh
[[ "${PLAN:-}" =~ ^proto/turing/plans/[A-Za-z0-9_]+\.json$ ]] || { echo "PLAN must be proto/turing/plans/<name>.json"; exit 2; }
[[ "${WAIT_H:-0}" =~ ^[0-9]{1,3}$ ]] || exit 2
REPO=$PWD; T_END=$(( $(date +%s) + ${WAIT_H:-0} * 3600 ))
while :; do
  git -C $REPO pull -q --rebase --autostash "$(git -C $REPO remote get-url --push origin)" main || true
  LEFT=$(python - $PLAN <<'PY'
import json, os, sys
sys.path.insert(0, 'proto/turing'); import inlets_plan as IP
P = json.load(open(sys.argv[1])); IP.check(P); root = os.path.join(os.environ['LF_WORK'], P['results_root'])
print(sum(1 for t in P['tasks'] if not any(os.path.exists(os.path.join(root, t['name'], f)) for f in ('DONE', 'FAILED'))))
PY
)
  echo "$(date -u +%FT%TZ) tasks not finished: $LEFT"
  [ "$LEFT" = 0 ] && break
  [ $(date +%s) -ge $T_END ] && break
  sleep 600
done
python - $PLAN <<'PY'
import json, os, sys, shutil, re, datetime as dt
sys.path.insert(0, 'proto/turing'); import inlets_plan as IP
P = json.load(open(sys.argv[1])); IP.check(P); root = os.path.join(os.environ['LF_WORK'], P['results_root']); dest = P['dest']
KEEP = ('score_v2.json', 'score.json', 'points.json', 'flood_meta.json', 'w9_tail.txt', 'FAILED'); MAXB = 400_000
man = dict(plan=sys.argv[1], dest=dest, collected_utc=dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%dT%H:%MZ'), tasks={})
for t in P['tasks']:
    src = os.path.join(root, t['name']); d = os.path.join(dest, t['name']); st = 'missing'
    if os.path.exists(os.path.join(src, 'DONE')): st = 'done'
    elif os.path.exists(os.path.join(src, 'FAILED')): st = 'failed: ' + open(os.path.join(src, 'FAILED')).read().strip()[:80]
    files = []
    for f in KEEP:
        p = os.path.join(src, f)
        if os.path.isfile(p) and os.path.getsize(p) <= MAXB:
            if f.endswith('.json'): json.load(open(p))          # valid json only
            os.makedirs(d, exist_ok=True); shutil.copy(p, os.path.join(d, f)); files.append(f)
    man['tasks'][t['name']] = dict(storm=t['storm'], arm=t['arm'], status=st, files=files)
os.makedirs(dest, exist_ok=True); json.dump(man, open(os.path.join(dest, 'manifest.json'), 'w'), indent=1)
print({k: sum(1 for v in man['tasks'].values() if v['status'].startswith(k)) for k in ('done', 'failed', 'missing')})
PY
DEST=$(python -c "import json; print(json.load(open('$PLAN'))['dest'])")
[[ "$DEST" =~ ^docs/proto/[a-z0-9_]+/[A-Za-z0-9_]+$ ]] || exit 2
git add -A "$DEST"
git -c user.name="Mohab Eldokla" -c user.email="Horus331@users.noreply.github.com" commit -qm "Turing scores: $DEST ($(basename $PLAN))" || { echo "nothing to commit"; exit 0; }
R=$(git remote get-url --push origin)
for i in 1 2 3 4 5 6 7 8; do git pull -q --rebase --autostash "$R" main && git push -q "$R" HEAD:main && echo "pushed $DEST" && exit 0; sleep $((RANDOM % 30 + 10)); done
echo "push failed"; exit 1
