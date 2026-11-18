"""Storm-level bootstrap (2000 draws) for the forecast ensemble check: 2-of-8 vs the newest single cycle, out-of-sample storms.
Reported after the pre-registered check (docs/proto/forecast/ENSEMBLE_PARITY.md §4); it does not change the verdict or the live rule.
    python proto/ensemble_ci.py"""
import os
P = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'docs/proto/forecast')
import json, numpy as np
d = json.load(open(f'{P}/ensemble_parity.json')); E = d['ensembles']; rng = np.random.default_rng(0)
out = {}
for lead in ('oos_long', 'oos_short'):
    ids = d['pooled'][lead]['ensembles']
    S = {r: np.array([[len(E[i]['rules'][r]['hits']), E[i]['rules'][r]['strict']['n']] for i in ids], float) for r in ('single', 'two_of_8')}
    rec = {r: S[r][:, 0].sum() / S[r][:, 1].sum() for r in S}
    B = []; Bs = {r: [] for r in S}
    for _ in range(2000):
        k = rng.integers(0, len(ids), len(ids))
        v = {r: S[r][k, 0].sum() / max(S[r][k, 1].sum(), 1) for r in S}
        for r in S: Bs[r].append(v[r])
        B.append(v['two_of_8'] - v['single'])
    q = lambda a: [round(float(x), 3) for x in np.percentile(a, [2.5, 97.5])]
    out[lead] = dict(storms=len(ids), sites=int(S['single'][:, 1].sum()), recall={r: round(rec[r], 3) for r in rec},
                     ci95={r: q(Bs[r]) for r in S}, diff=round(rec['two_of_8'] - rec['single'], 3), diff_ci95=q(B),
                     share_diff_gt0=round(float(np.mean(np.array(B) > 0)), 3),
                     per_storm=[(i, int(S['single'][j,0]), int(S['two_of_8'][j,0]), int(S['single'][j,1])) for j, i in enumerate(ids)])
json.dump(out, open(f'{P}/ensemble_ci.json', 'w'), indent=1); print(json.dumps(out, indent=1))
