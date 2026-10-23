"""Expanded-set evaluation of the closure ranking / alert candidates under PROTOCOL.md v2 (held-out 23 storms, 90 sites).

    python proto/closure_expanded.py run [--boot 2000]     # nested LOSO over the 25 non-locked parity storms -> docs/proto/ml/expanded/,
                                                           #   docs/proto/ml/EXPANDED.json
    python proto/closure_expanded.py selftest

Write-up: docs/proto/ml/EXPANDED.md.  Everything between the PRE-REGISTERED lines was committed before any held-out-23 number of these
candidates was computed (PROTOCOL.md v2 "Process").

Data: the parity catalogue docs/proto/parity/catalog/<storm>_<area>_20m (features_<storm>.csv, matches_<storm>.json), the clean parity
baseline scored in docs/proto/scoring/BASELINE_v2_expanded.md.  Locked storms (score_v2.LOCKED) are never loaded.
Machinery (features, models, nested fold, Platt, equal-share tier, encoding for score_v2) is reused from proto/closure_v2.py unchanged.
"""
import argparse
import json
import os
import re
import sys
import tempfile

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import closure_v2 as V2  # noqa: E402
import score_v2 as SV  # noqa: E402

PAR = V2.PAR
OUTD = os.path.join(ROOT, 'docs', 'proto', 'ml', 'expanded')
OUTJ = os.path.join(ROOT, 'docs', 'proto', 'ml', 'EXPANDED.json')
STORMS = list(SV.LOSO9) + list(SV.NEW16)                       # 25 non-locked storms (2 dev + 23 held-out)
DECISION = list(SV.HELDOUT) + list(SV.NEW16)                   # held-out 23

# ================================================================================================ PRE-REGISTERED (23 Oct 2026)
# Candidates (PROTOCOL.md v2 §5a ranking route for all four; §5b alert-tier route for (c) only).  k = 5 tests -> alpha = 0.05 / 5 = 0.01.
#  a_v1        learned v1 (closure_ml.LR on MAIN, storm-balanced, reporting domains) refitted on the 24 training storms of each fold; ranking =
#              v1 score; alert tier = v1 score >= the in-fold equal-share threshold (closure_v2.nested_fold: storm-mean training share = the
#              depth rule's storm-mean training share; chosen by inner LOSO over the 24).
#  b_v2nopu    learned v2 variant B without propensity weights (closure_v2 'v2_pairlr_nopu': rule-logit offset + sign-bounded pairwise linear
#              correction, MAIN + 5 graph features), same fold recipe and tier as a_v1.
#  c_stormrel  storm-relative depth rule: rank by modelled peak road depth (ties: p_close); alert tier = top q of the storm's in-box segments.
#              q is chosen inside each fold from Q_GRID on the 24 training storms (box-wide sites): the LARGEST q whose pooled training site lift
#              (hits / exact chance hits) is >= 0.8 x the depth rule's pooled training lift on the same storms; if none qualifies, the
#              smallest q.  Q_GRID tops out at the §5b budget cap (1.5 % < 1.65 %).
#  d_twotier   two-tier at a fixed budget: tier 1 = the depth rule (p_close >= 0.5, the alert tier, unchanged, in its own order); the rest of the budget is filled
#              in the order of the in-fold v1 score (a_v1's fold models).  Scored at every share, i.e. the budget B = 1 / 3 / 5 %; the decision
#              is at B = 3 % (§5a).  Its alert tier is the rule, so condition 5 holds by construction.
# Baseline: the parity runs as published (p_close, then depth), scored by the same score_v2 code in the same run.
VARIANTS = ('a_v1', 'b_v2nopu', 'c_stormrel', 'd_twotier')
TIER_ROUTE = ('c_stormrel',)
K_TESTS = len(VARIANTS) + len(TIER_ROUTE)
ALPHA = 0.05 / K_TESTS
Q_GRID = (0.0025, 0.005, 0.0075, 0.01, 0.0125, 0.015)
Q_LIFT_FRAC = 0.8
# ================================================================================================


def areas():
    A = {}
    for d in os.listdir(PAR):
        m = re.fullmatch(r'((?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)20\d\d[a-z]?)_([a-z]+)_20m', d)
        if m: A[m.group(1)] = m.group(2)
    assert not set(A) & set(SV.LOCKED), 'locked storm in the parity catalogue'
    missing = set(STORMS) - set(A); assert not missing, missing
    return {s: A[s] for s in STORMS}


def lift_at(D, sites, flag):
    n = len(flag); k = int(flag.sum()); msz = np.array([len(s) for s in sites], int)
    return float(V2.hits(flag, sites).sum()), float(SV.chance_hit(n, k, msz).sum()) if len(sites) else 0.0


def topq(D, q):
    return V2.topk(D['depth'], D['p_rule'], int(round(q * len(D['depth']))))


def choose_q(S, sites, train):
    H = C = 0.0
    for u in train:
        h, c = lift_at(S[u], sites[u], S[u]['p_rule'] >= 0.5); H += h; C += c
    rule_lift = H / C if C else 0.0; tab = {}
    for q in Q_GRID:
        H = C = 0.0
        for u in train:
            h, c = lift_at(S[u], sites[u], topq(S[u], q)); H += h; C += c
        tab[q] = H / C if C else 0.0
    ok = [q for q in Q_GRID if tab[q] >= Q_LIFT_FRAC * rule_lift]
    return (max(ok) if ok else min(Q_GRID)), dict(rule_lift=rule_lift, lift={f'{q:g}': v for q, v in tab.items()})


def pool_summary(scored, storms, boot):
    R = {r['storm']: r for r in scored['runs']}; pl = SV.pooled([R[s] for s in storms if s in R], 'box', boot=boot); P, C = pl['point'], pl['ci90']
    out = dict(storms=len(pl['storms']), sites=pl['n_sites'])
    for b in ('rule', 'share_0.01', 'share_0.03', 'share_0.05'):
        out[b] = dict(recall=P[b]['site_recall'], ci90=C[b]['site_recall'], chance=P[b]['chance'], lift=P[b]['lift'], fss300=P[b]['fss300'],
                      fss300_ci90=C[b]['fss300'], hits=round(P[b]['site_recall'] * pl['n_sites'], 2))
    out['tier_share_mean'] = float(np.mean([R[s]['domains']['box']['rule']['share'] for s in storms if s in R]))
    return out


def cmd_run(a):
    V2.AREA.update(areas()); V2.STORMS = STORMS
    os.makedirs(OUTD, exist_ok=True)
    S = {}
    for s in STORMS:
        S[s] = V2.load_storm(s); print(f"{s}: {len(S[s]['y'])} segs, {S[s]['y'].sum()} labelled, domain {S[s]['dom'].sum()}", flush=True)
    sites = {s: V2.sites_of(S[s]) for s in STORMS}
    P, I = V2.run_loso(['v1', 'v2_pairlr_nopu'], S)
    qsel = {}
    for h in STORMS:
        qsel[h] = choose_q(S, sites, [t for t in STORMS if t != h]); print(f'  c: fold {h} q = {qsel[h][0]:g}', flush=True)
    enc = {}
    for name, src in (('a_v1', 'v1'), ('b_v2nopu', 'v2_pairlr_nopu')):
        enc[name] = {s: V2.encode(P[src][s]['score'], S[s]['depth'], P[src][s]['tier']) for s in STORMS}
    enc['c_stormrel'] = {s: V2.encode(S[s]['depth'], S[s]['p_rule'], topq(S[s], qsel[s][0])) for s in STORMS}
    enc['d_twotier'] = {}
    for s in STORMS:
        rf = S[s]['p_rule'] >= 0.5; v = P['v1'][s]['score']; kr = SV.rank_key(S[s]['p_rule'], S[s]['depth'])
        sc = np.where(rf, 2.0 + kr / (kr.max() + 1e-12), (v - v.min()) / (np.ptp(v) + 1e-12))     # rule first (in the rule's own order), then v1
        enc['d_twotier'][s] = V2.encode(sc, S[s]['depth'], rf)
    tmp = tempfile.mkdtemp(prefix='exp_'); scored = {}
    scored['base'] = dict(runs=[dict(SV.score_run(SV.load_run(S[s]['run'], s)), primary=True, group='base') for s in STORMS]); print('scored base', flush=True)
    for name in VARIANTS:
        scored[name] = V2.score_set(S, enc[name], name, tmp); print('scored', name, flush=True)
    rule_a = dict(SV.ADOPT_V2, alpha=ALPHA); cmp = {}
    for name in VARIANTS:
        cmp[f'{name}:share'] = SV.compare(scored['base'], scored[name], boot=a.boot, rule=rule_a)
    for name in TIER_ROUTE:
        cmp[f'{name}:tier'] = SV.compare(scored['base'], scored[name], boot=a.boot, rule=dict(rule_a, level='rule'))
    # context only (not tests): tier route of the other variants, and the PROTOCOL v1 OOS-7 verdicts
    ctx = {f'{n}:tier': SV.compare(scored['base'], scored[n], boot=a.boot, rule=dict(rule_a, level='rule')) for n in VARIANTS if n not in TIER_ROUTE}
    ctx.update({f'{n}:v1_oos7': SV.compare(scored['base'], scored[n], boot=a.boot, rule=dict(SV.ADOPT, alpha=ALPHA)) for n in VARIANTS})
    pools = {n: {pn: pool_summary(sc, st, a.boot) for pn, st in (('heldout23', DECISION), ('oos7', SV.HELDOUT), ('new16', SV.NEW16), ('dev2', SV.DEV))}
             for n, sc in scored.items()}
    per = {n: {r['storm']: dict(sites=r['domains']['box']['n_sites'], tier_share=r['domains']['box']['rule']['share'], tier_hits=r['domains']['box']['rule']['site_hits'],
                                **{f'hits{int(float(sh) * 100)}': r['domains']['box']['shares'][sh]['site_hits'] for sh in ('0.01', '0.03', '0.05')})
               for r in sc['runs']} for n, sc in scored.items()}
    from sklearn.metrics import roc_auc_score
    roc = {}
    for n, f in (('rule', lambda s: S[s]['off'] + 1e-3 * S[s]['depth']), ('depth', lambda s: S[s]['depth'] + 1e-6 * S[s]['p_rule']),
                 ('a_v1', lambda s: P['v1'][s]['score']), ('b_v2nopu', lambda s: P['v2_pairlr_nopu'][s]['score'])):
        roc[n] = {s: float(roc_auc_score(S[s]['y'], f(s))) for s in STORMS}
    folds = dict(q=qsel, **{n: {s: {k: v for k, v in I[n][s].items() if k not in ('model', 'propensity')} for s in STORMS} for n in I})
    res = dict(made_by='proto/closure_expanded.py run', protocol='PROTOCOL.md v2', baseline='docs/proto/parity/catalog (BASELINE_v2_expanded)',
               variants=list(VARIANTS), tier_route=list(TIER_ROUTE), k_tests=K_TESTS, alpha=ALPHA, q_grid=Q_GRID, compare=cmp, context=ctx,
               pools=pools, per_storm=per, roc_auc=roc, folds=folds)
    json.dump(res, open(OUTJ, 'w'), indent=1, default=float)
    for n, sc in scored.items():
        json.dump(dict(made_by='proto/closure_expanded.py run', variant=n, runs=sc['runs']), open(os.path.join(OUTD, f'score_{n}.json'), 'w'))
    for k, v in cmp.items():
        print(k, 'ADOPT' if v['adopt'] else 'reject', round(v['delta_recall'], 3), round(v['delta_recall_lower'], 3), round(v['delta_fss'], 4),
              v['worst_storm_change'], v['lift_rule'], v['checks'], flush=True)


def selftest():
    ok = True
    A = areas(); ok &= len(A) == 25 and not set(A) & set(SV.LOCKED); print('areas', 'PASS' if ok else 'FAIL')
    ok &= K_TESTS == 5 and abs(ALPHA - 0.01) < 1e-12 and max(Q_GRID) < 0.0165; print('settings', 'PASS' if ok else 'FAIL')
    return ok


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0]); ap.add_argument('cmd', choices=['run', 'selftest'])
    ap.add_argument('--boot', type=int, default=2000)
    a = ap.parse_args()
    if a.cmd == 'selftest': sys.exit(0 if selftest() else 1)
    cmd_run(a)
