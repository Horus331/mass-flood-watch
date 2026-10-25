"""Cascade-aware features for the learned closure model: does knowing how flooding spreads on the network improve held-out prediction?

    python proto/cascade_ml.py run [--boot 2000]    # nested LOSO over the 25 non-locked parity storms -> docs/proto/cascade/ (CASCADE_ML.json, score_*.json)
    python proto/cascade_ml.py selftest

Write-up: docs/proto/cascade/CASCADE.md §4.  Protocol: docs/proto/PROTOCOL.md v2 (held-out 23).  Machinery (storm loading, nested fold,
equal-share tier, score_v2 encoding) is reused from proto/closure_v2.py and proto/closure_expanded.py unchanged.

Everything between the PRE-REGISTERED lines was committed before any held-out-23 number of these candidates was computed.
"""
import argparse
import json
import os
import sys
import tempfile

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import closure_ml as CM  # noqa: E402
import closure_v2 as V2  # noqa: E402
import closure_expanded as EX  # noqa: E402
import score_v2 as SV  # noqa: E402

OUTD = os.path.join(ROOT, 'docs', 'proto', 'cascade')
STORMS = EX.STORMS; DECISION = EX.DECISION
BASE_FILE = os.path.join(ROOT, 'docs', 'proto', 'obs', 'round2', 'score_round2.json')

# ================================================================================================ PRE-REGISTERED (25 Oct 2026)
# Cascade features (no labels used; computed per storm on the in-box segments from features_<storm>.csv and docs/graph_segments.json links).
# The parity catalogue holds per-segment peaks and durations, not frame series, so "lags" are graph hops and closure durations:
#   cl_logkm      flooding-cluster membership: ln(1 + km of road in the connected wet cluster (peak depth >= 0.15 m) that contains the segment,
#                 or, for a dry segment, the largest wet cluster it touches); 0 if none
#   nb2_h30       ln(1 + max hours over 30 cm among neighbours within 2 hops (not the segment itself))
#   nb2_closed    ln(1 + number of neighbours within 2 hops that close (hours over 30 cm > 0))
#   up_wet_km     drainage-connected inflow along the road network: ln(1 + km of road within 1 km network distance that lies upslope
#                 (HAND above the segment's) and is wet (peak depth >= 0.05 m))
# All four enter with sign + (monotone; a fitted coefficient of the wrong sign drops the feature, as closure_ml.LR does).
CAS = ['cl_logkm', 'nb2_h30', 'nb2_closed', 'up_wet_km']
CAS_SIGN = dict(CM.SIGN, **{c: 1 for c in CAS})
WET_M, UPWET_M, UP_RADIUS_M = 0.15, 0.05, 1000.0
# Candidates (PROTOCOL v2 §5a ranking route; k = 3 tests -> alpha = 0.05 / 3):
#   T1 cas_v1       learned v1 logistic (closure_ml.LR recipe: C = 0.5, standardised, sign-constrained drop, storm-balanced, reporting domains)
#                   on MAIN + CAS, refitted on the 24 training storms of each fold; tier = in-fold equal-share threshold (closure_v2.nested_fold)
#                   -> compared with the deployed depth rule (baseline).
#   T2 cas_twotier  tier 1 = depth rule (own order), the rest of the budget in cas_v1 order (as closure_expanded d_twotier) -> vs the depth rule.
#   T3 cas_v1 vs a_v1: the same conditions with the in-run refit of learned v1 on MAIN only (identical recipe and folds) as the base:
#                   the direct test of whether the cascade features add held-out skill.
# Step (b) (graph-regularised / label-propagation model) is run ONLY if T3 meets conditions 1 and 2 (gain >= +0.04, lower bound > 0 at
# alpha / k).  Otherwise it is not run and the write-up says so.
# Baseline: the parity runs as published (p_close, then depth), scored in the same run by the same code on the current labels; it must equal
# docs/proto/obs/round2/score_round2.json (parity group) site for site, and the --compare against that file is reported too.
TESTS = ('T1_cas_v1', 'T2_cas_twotier', 'T3_cas_vs_v1')
K_TESTS = len(TESTS)
ALPHA = 0.05 / K_TESTS
# ================================================================================================


def cascade_features(D, S=None):
    """-> (n, 4) CAS features for one storm dict from closure_v2.load_storm."""
    from scipy.sparse import coo_matrix, csr_matrix
    from scipy.sparse.csgraph import connected_components, dijkstra
    S = S or V2.graph(); seg = D['seg']; n = len(seg); pos = {int(s): i for i, s in enumerate(seg)}
    L = np.asarray(S['props']['len'], float); sl = np.maximum(L[np.asarray(seg, int)], 1.0)
    a, b = [], []
    for u, v in S['links']:
        if u in pos and v in pos and u != v: a.append(pos[u]); b.append(pos[v])
    a = np.array(a, int); b = np.array(b, int)
    A = csr_matrix((np.ones(2 * len(a)), (np.r_[a, b], np.r_[b, a])), shape=(n, n)); A.data[:] = 1
    rows = D['rows']; F = V2.F
    h30 = np.nan_to_num(np.array([F(r.get('hours_over_30cm'), 0) for r in rows])); hand = np.nan_to_num(np.array([F(r.get('hand_m'), 20) for r in rows]), nan=20.0)
    depth = D['depth']; wet = depth >= WET_M
    # cluster membership
    k = wet[a] & wet[b]
    _, lab = connected_components(csr_matrix((np.ones(2 * k.sum()), (np.r_[a[k], b[k]], np.r_[b[k], a[k]])), shape=(n, n)), directed=False)
    ckm = np.bincount(lab, weights=np.where(wet, sl / 1000.0, 0.0)); cl = np.where(wet, ckm[lab], 0.0)
    for i in np.nonzero(~wet)[0]:
        j = A.indices[A.indptr[i]:A.indptr[i + 1]]; j = j[wet[j]]
        if len(j): cl[i] = ckm[lab[j]].max()
    # 2-hop neighbourhood
    A2 = (A + A @ A).tocsr(); A2.setdiag(0); A2.eliminate_zeros()
    lh = np.log1p(h30); nbh = np.zeros(n); nbc = np.zeros(n)
    for i in range(n):
        j = A2.indices[A2.indptr[i]:A2.indptr[i + 1]]
        if len(j): nbh[i] = lh[j].max(); nbc[i] = (h30[j] > 0).sum()
    # upslope wet road within 1 km along the network
    w = np.maximum(np.minimum((sl[a] + sl[b]) / 2, UP_RADIUS_M), 1.0)
    W = coo_matrix((np.r_[w, w], (np.r_[a, b], np.r_[b, a])), shape=(n, n)).tocsr(); up = np.zeros(n); uw = depth >= UPWET_M
    for c0 in range(0, n, 500):
        idx = np.arange(c0, min(n, c0 + 500)); Dm = dijkstra(W, directed=False, indices=idx, limit=UP_RADIUS_M)
        for kk, i in enumerate(idx):
            j = np.nonzero(np.isfinite(Dm[kk]))[0]; j = j[(j != i) & uw[j] & (hand[j] > hand[i])]
            up[i] = sl[j].sum() / 1000.0
    return np.column_stack([np.log1p(cl), nbh, np.log1p(nbc), np.log1p(up)])


class CasLR:
    """closure_ml.LR on named columns of D['XC'] (MAIN + CAS) with CAS_SIGN; storm-balanced weights as closure_v2.V1."""
    NAMES = CM.MAIN + CAS

    def __init__(self, feats, C=0.5): self.feats = list(feats); self.C = C

    def fit(self, parts):
        from sklearn.linear_model import LogisticRegression
        X = np.vstack([p['XC'] for p in parts]); y = np.concatenate([p['y'] for p in parts])
        sw = np.concatenate([np.full(len(p['y']), 1.0 / len(p['y'])) for p in parts]); sw = sw / sw.mean()
        keep = [self.NAMES.index(f) for f in self.feats]; self.dropped = []
        while True:
            mu = X[:, keep].mean(0); sd = X[:, keep].std(0) + 1e-9
            m = LogisticRegression(C=self.C, max_iter=2000).fit((X[:, keep] - mu) / sd, y, sample_weight=sw)
            bad = [(abs(b), j) for j, b in zip(keep, m.coef_[0]) if CAS_SIGN[self.NAMES[j]] * b < 0]
            if not bad: break
            j = max(bad)[1]; keep.remove(j); self.dropped.append(self.NAMES[j])
        self.keep, self.mu, self.sd, self.coef, self.b0 = keep, mu, sd, m.coef_[0], float(m.intercept_[0]); return self

    def score(self, XC, off=None): return ((XC[:, self.keep] - self.mu) / self.sd) @ self.coef + self.b0

    def to_json(self): return dict(features=[self.NAMES[j] for j in self.keep], coef_std=self.coef.round(3).tolist(), dropped=self.dropped)


_fit0, _score0 = V2.fit_variant, V2.score_of


def fit_variant(name, S, train):
    if name != 'cas_v1': return _fit0(name, S, train)
    parts = [dict(XC=S[s]['XC'][S[s]['dom']], y=S[s]['y'][S[s]['dom']]) for s in train]
    return CasLR(CasLR.NAMES).fit(parts), None


def score_of(m, D): return m.score(D['XC']) if isinstance(m, CasLR) else _score0(m, D)


def cmd_run(a):
    V2.AREA.update(EX.areas()); V2.STORMS = STORMS; V2.fit_variant = fit_variant; V2.score_of = score_of
    os.makedirs(OUTD, exist_ok=True); S = {}
    for s in STORMS:
        D = V2.load_storm(s); D['CAS'] = cascade_features(D); D['XC'] = np.column_stack([D['X0'][:, [CM.FEATURES.index(f) for f in CM.MAIN]], D['CAS']]); S[s] = D
        print(f"{s}: {len(D['y'])} segs, {D['y'].sum()} labelled; CAS means {np.round(D['CAS'].mean(0), 3).tolist()}", flush=True)
    P, I = V2.run_loso(['v1', 'cas_v1'], S)
    enc = {n: {s: V2.encode(P[src][s]['score'], S[s]['depth'], P[src][s]['tier']) for s in STORMS} for n, src in (('a_v1', 'v1'), ('cas_v1', 'cas_v1'))}
    enc['cas_twotier'] = {}
    for s in STORMS:
        rf = S[s]['p_rule'] >= 0.5; v = P['cas_v1'][s]['score']; kr = SV.rank_key(S[s]['p_rule'], S[s]['depth'])
        enc['cas_twotier'][s] = V2.encode(np.where(rf, 2.0 + kr / (kr.max() + 1e-12), (v - v.min()) / (np.ptp(v) + 1e-12)), S[s]['depth'], rf)
    tmp = tempfile.mkdtemp(prefix='cas_'); scored = {'base': dict(runs=[dict(SV.score_run(SV.load_run(S[s]['run'], s)), primary=True, group='base') for s in STORMS])}
    for n in enc: scored[n] = V2.score_set(S, enc[n], n, tmp); print('scored', n, flush=True)
    rule = dict(SV.ADOPT_V2, alpha=ALPHA)
    cmp = {'T1_cas_v1': SV.compare(scored['base'], scored['cas_v1'], boot=a.boot, rule=rule),
           'T2_cas_twotier': SV.compare(scored['base'], scored['cas_twotier'], boot=a.boot, rule=rule),
           'T3_cas_vs_v1': SV.compare(scored['a_v1'], scored['cas_v1'], boot=a.boot, rule=rule)}
    ctx = {'a_v1_vs_base': SV.compare(scored['base'], scored['a_v1'], boot=a.boot, rule=rule)}
    try:
        R2 = json.load(open(BASE_FILE)); R2 = dict(runs=[r for r in R2['runs'] if r.get('group') == 'parity' and r.get('primary')])
        ctx['round2_file_base'] = {n: SV.compare(R2, scored[n], boot=a.boot, rule=rule) for n in ('cas_v1', 'cas_twotier')}
        same = {r['storm']: [x['id'] for x in r['domains']['box']['sites']] for r in R2['runs']}
        ctx['base_equals_round2_sites'] = all(same.get(r['storm']) == [x['id'] for x in r['domains']['box']['sites']] for r in scored['base']['runs'] if r['storm'] in DECISION)
    except SystemExit as e: ctx['round2_file_base'] = f'refused: {e}'
    pools = {n: {pn: EX.pool_summary(sc, st, a.boot) for pn, st in (('heldout23', DECISION), ('oos7', SV.HELDOUT), ('new16', SV.NEW16), ('dev2', SV.DEV))} for n, sc in scored.items()}
    from sklearn.metrics import roc_auc_score
    roc = {n: {s: float(roc_auc_score(S[s]['y'], f(s))) for s in STORMS if 0 < S[s]['y'].sum() < len(S[s]['y'])}
           for n, f in (('rule', lambda s: S[s]['off'] + 1e-3 * S[s]['depth']), ('a_v1', lambda s: P['v1'][s]['score']), ('cas_v1', lambda s: P['cas_v1'][s]['score']))}
    coef = {s: I['cas_v1'][s]['model'] for s in STORMS} if I['cas_v1'][STORMS[0]].get('model') else None
    # final-fold-free description of the fitted cascade model: fit on all 25 storms (reporting only)
    full = fit_variant('cas_v1', S, STORMS)[0].to_json()
    # univariate: does each CAS feature separate labelled from unlabelled segments within storm (mean per-storm AUC, held-out 23)?
    uni = {c: float(np.mean([roc_auc_score(S[s]['y'], S[s]['CAS'][:, j] + 1e-9 * S[s]['depth']) for s in DECISION if 0 < S[s]['y'].sum()])) for j, c in enumerate(CAS)}
    step_b = cmp['T3_cas_vs_v1']['checks']['gain'] and cmp['T3_cas_vs_v1']['checks']['ci_lower_gt_0']
    res = dict(made_by='proto/cascade_ml.py run', protocol='PROTOCOL.md v2 §5a', k_tests=K_TESTS, alpha=ALPHA, features=CAS, compare=cmp, context=ctx, pools=pools,
               roc_auc=roc, roc_mean_heldout23={n: float(np.mean([v[s] for s in DECISION if s in v])) for n, v in roc.items()}, univariate_auc_heldout23=uni,
               cas_v1_full_fit=full, fold_models=coef, step_b_run=bool(step_b),
               step_b_note='T3 conditions 1-2 met: run the graph model' if step_b else 'T3 conditions 1-2 not met: step (b) not run (pre-registered)')
    json.dump(res, open(os.path.join(OUTD, 'CASCADE_ML.json'), 'w'), indent=1, default=float)
    for n, sc in scored.items(): json.dump(dict(made_by='proto/cascade_ml.py run', variant=n, runs=sc['runs']), open(os.path.join(OUTD, f'score_{n}.json'), 'w'))
    for k, v in list(cmp.items()) + list(ctx.items())[:1]:
        print(k, 'ADOPT' if v['adopt'] else 'reject', round(v['delta_recall'], 3), round(v['delta_recall_lower'], 3), round(v['delta_fss'], 4), v['worst_storm_change'], v['checks'])
    print(json.dumps(dict(roc=res['roc_mean_heldout23'], uni=uni, full=full, step_b=res['step_b_note'])))


def selftest():
    ok = K_TESTS == 3 and abs(ALPHA - 0.05 / 3) < 1e-12 and set(CAS) <= set(CAS_SIGN)
    V2.AREA.update(EX.areas()); D = V2.load_storm('aug2019'); C = cascade_features(D)
    ok &= C.shape == (len(D['y']), 4) and np.all(np.isfinite(C)) and np.all(C >= 0)
    ok &= np.all(C[D['depth'] >= WET_M, 0] > 0)
    print('selftest', 'PASS' if ok else 'FAIL', np.round(C.mean(0), 3).tolist()); return ok


if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('cmd', choices=['run', 'selftest']); ap.add_argument('--boot', type=int, default=2000); a = ap.parse_args()
    if a.cmd == 'run': cmd_run(a)
    else: sys.exit(0 if selftest() else 1)
