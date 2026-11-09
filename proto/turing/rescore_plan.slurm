#!/bin/bash
#SBATCH -J mfw_rescore
#SBATCH -p short
#SBATCH -c 4
#SBATCH --mem=48G
#SBATCH -t 04:00:00
#SBATCH -o rescore_%j.out
# Re-run ONLY the score_v2 step of plan tasks whose run finished but whose scoring failed (FAILED = "score_v2"): CPU, no solver, no GPU.
# The run_plan_gpu tasks of the NWM soil-wetness test (amcnwm_v1, 31 Oct) all solved and wrote their score_v2-ready folder (<task>/full)
# but score_v2 stopped (scikit-learn is not in the Turing environment; score_v2.py has had a numpy fallback since 8 Nov).
#   queue: {"id": "amcnwm_rescore", "kind": "rescore_plan", "env": {"PLAN": "proto/turing/plans/amcnwm_v1.json"}, "sbatch": {"partition": "short", "time": "04:00:00"}}
# Then collect_scores (WAIT_H=0) brings the files to main.
set -eo pipefail
source proto/turing/env.sh >/dev/null 2>&1 || true
[[ "${PLAN:-}" =~ ^proto/turing/plans/[A-Za-z0-9_]+\.json$ ]] || { echo "PLAN must be proto/turing/plans/<name>.json"; exit 2; }
python - $PLAN <<'PY'
import json, os, subprocess, sys
P = json.load(open(sys.argv[1])); root = os.path.join(os.environ['LF_WORK'], P['results_root']); n = ok = 0
for t in P['tasks']:
    R = os.path.join(root, t['name']); F = os.path.join(R, 'full'); fl = os.path.join(R, 'FAILED')
    if not (os.path.exists(fl) and open(fl).read().strip() == 'score_v2' and os.path.exists(os.path.join(F, 'segments.geojson'))): continue
    n += 1
    p = subprocess.run([sys.executable, 'proto/score_v2.py', '--run', F, '--storm', t['storm'], '--out', os.path.join(R, 'score_v2.json')], capture_output=True, text=True)
    if p.returncode == 0 and os.path.exists(os.path.join(R, 'score_v2.json')):
        os.remove(fl); open(os.path.join(R, 'DONE'), 'w').write('ok (re-scored)\n'); ok += 1
    else: print('still failing', t['name'], (p.stderr or p.stdout)[-400:])
print(f're-scored {ok} of {n} tasks')
PY
