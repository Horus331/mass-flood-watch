"""Learned closure layer v2 (ROADMAP_research.md T5): rule-offset ranking, road-graph neighbour features, SAR-PU propensity weights.

    python proto/closure_v2.py selftest                 # offline, synthetic
    python proto/closure_v2.py loso [--boot 2000]       # nested LOSO on the parity catalogue -> docs/proto/ml/v2/ (score_*.json, loso.json)
    python proto/closure_v2.py fit                      # final all-storm fit -> docs/proto/ml/closure_v2.json (+ closure_v2_lgbm.txt)

Everything below the line "PRE-REGISTERED" was fixed and committed before any held-out (OOS-7) number of a v2 variant was computed
(docs/proto/PROTOCOL.md §5 "Process"; docs/proto/ml/LEARNED_v2.md §1).

Data: docs/proto/parity/catalog/<storm>_<area>_20m/features_<storm>.csv + matches_<storm>.json (closure_ml.extract output; strict 30 m match).

Model idea.  The rule's score o(x) = logit(Phi((peak depth - 0.30) / 0.10)), clipped to [-6, 6], is an offset (LightGBM init_score / a fixed
coefficient of 1 in the linear model): the learned part only adds corrections f(x), score = o(x) + f(x).  The clip makes all dry roads tie at
-6 and all roads deeper than ~0.65 m tie at +6, so the corrections mostly reorder those two ties and the 0.1-0.6 m band, and the top of the
rule's list stays where the rule put it unless the data say otherwise (v1 lost exactly there: docs/proto/parity/catalog/ml/LOSO.md).

Training (unchanged from v1): each storm contributes its reporting domain only (towns with a matched label; sep2023: Leominster city, DPW
inventory), so the reporting footprint is not learned.  Ranking objectives use query = storm (pairs only within a storm).

Neighbour features (no labels): segments within NB_M = 300 m along docs/graph_segments.json links (edge length = mean of the two segments'
lengths, capped at 300 m so a direct neighbour always counts):
  nb_logdepth_max   max log-depth of the neighbours                                     +
  nb_logdepth_mean  length-weighted mean log-depth of the neighbours                    +
  nb_pmay_max       max may-close probability (depth OR overtopping) of the neighbours   +
  nb_up_overtop     max overtopping (water beside the road minus crest, m) among *upslope* neighbours (HAND above this segment's)   +
  nb_up_road        ln(1 + upslope neighbour road length / 100 m): road runoff that drains towards this segment   +

SAR-PU weights (Bekker & Davis 2020).  Reports are not missing at random: some towns report everything, some nothing, local streets less than
arterials.  Propensity e(x) = P(reported | flooded, x) is approximated by a logistic model of 'labelled' among the rule-flagged segments
(p_close >= 0.5, the closest thing to 'flooded' we have) of the training storms, whole boxes, storm-balanced, on
  town_rate  share of training storms with the town in the box (>= 50 segments) in which the town reported anything (Jeffreys-smoothed)
  local_road, ln(1 + AADT / 1000).
Labelled positives get weight 1 / e(x), normalised to mean 1 within each storm and clipped to [0.25, 4]; unlabelled rows weight 1.  Caveats in
LEARNED_v2.md: rule-flagged != flooded (the rule's precision is a few %), so only the relative propensity is used, never its level.
"""
import argparse
import csv
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import closure_ml as CM  # noqa: E402

PAR = os.path.join(ROOT, 'docs', 'proto', 'parity', 'catalog')
OUTD = os.path.join(ROOT, 'docs', 'proto', 'ml', 'v2')
MODEL_V2 = os.path.join(ROOT, 'docs', 'proto', 'ml', 'closure_v2.json')
STORMS = ['aug2021', 'aug2023', 'aug2023b', 'aug2026', 'jul2021', 'jul2023', 'sep2021', 'sep2022', 'sep2023']
AREA = dict(aug2021='worcester', aug2023='metrowest', aug2023b='millbury', aug2026='leominster', jul2021='worcester', jul2023='worcester',
            sep2021='worcester', sep2022='webster', sep2023='leominster')
AREA_GROUP = dict(aug2021='Worcester', aug2023b='Worcester', jul2021='Worcester', jul2023='Worcester', sep2021='Worcester',
                  aug2026='Leominster', sep2023='Leominster', aug2023='MetroWest', sep2022='Webster')
DOMAIN_OVERRIDE = dict(sep2023=('Leominster',))

# ================================================================================================ PRE-REGISTERED (23 Oct 2026)
NB_M = 300.0
GRAPH = ['nb_logdepth_max', 'nb_logdepth_mean', 'nb_pmay_max', 'nb_up_overtop', 'nb_up_road']
FEATS = CM.MAIN + GRAPH                                       # 10 v1 hazard / terrain features + 5 neighbour features
SIGN = dict(CM.SIGN, **{g: 1 for g in GRAPH})
OFFSET_CLIP = 6.0
TOWN_MIN_SEGS = 50
W_CLIP = (0.25, 4.0)
LGB_P = dict(objective='lambdarank', n_estimators=200, learning_rate=0.03, num_leaves=7, min_child_samples=50, subsample=0.8, subsample_freq=1,
             colsample_bytree=0.8, reg_lambda=5.0, lambdarank_truncation_level=300, verbose=-1, random_state=0, n_jobs=2)
PAIR_LAMBDA = 0.01
# variants scored on OOS-7: k = 4 for the Bonferroni alpha (PROTOCOL.md §5).  Only A and B are eligible for adoption; the two ablations are
# diagnostics (they still count in k).
VARIANTS = {
    'v2_lambdamart': dict(model='lgb', feats=FEATS, pu=True, desc='A: LightGBM lambdarank (query = storm), init score = rule logit, monotone, + graph, SAR-PU'),
    'v2_pairlr': dict(model='pair', feats=FEATS, pu=True, desc='B: linear pairwise logistic (RankNet-linear), offset = rule logit, sign-bounded, + graph, SAR-PU'),
    'v2_pairlr_nograph': dict(model='pair', feats=CM.MAIN, pu=True, desc='ablation of B: no neighbour features'),
    'v2_pairlr_nopu': dict(model='pair', feats=FEATS, pu=False, desc='ablation of B: no SAR-PU weights'),
}
ELIGIBLE = ('v2_lambdamart', 'v2_pairlr')
K_VARIANTS = len(VARIANTS)
CALIB = 'platt'               # final probabilities: Platt on inner-LOSO out-of-fold scores, training reporting domains, unweighted
WATCH_P_V1 = 0.02             # today's watch tier (prototype.TIER_WATCH_P) on the v1 logistic
# ================================================================================================


def F(x, d=np.nan):
    try: return float(x)
    except (TypeError, ValueError): return d


def offset_of(depth):
    from scipy.stats import norm
    p = norm.cdf((np.asarray(depth, float) - 0.30) / 0.10)
    return np.clip(CM._logit(p), -OFFSET_CLIP, OFFSET_CLIP)


# ------------------------------------------------------------------------------------------------ graph features
_G = {}


def graph():
    if not _G: _G['S'] = json.load(open(os.path.join(ROOT, 'docs', 'graph_segments.json')))
    return _G['S']


def neighbour_lists(seg, S=None):
    """For in-box segment ids `seg`: list of (neighbour row indices, distances) within NB_M along graph links."""
    from scipy.sparse import coo_matrix
    from scipy.sparse.csgraph import dijkstra
    S = S or graph(); pos = {int(s): i for i, s in enumerate(seg)}; L = np.asarray(S['props']['len'], float)
    a, b = [], []
    for u, v in S['links']:
        if u in pos and v in pos and u != v: a.append(pos[u]); b.append(pos[v])
    a = np.array(a, int); b = np.array(b, int); n = len(seg); sl = L[np.asarray(seg, int)]
    w = np.maximum(np.minimum((sl[a] + sl[b]) / 2, NB_M), 1.0)
    A = coo_matrix((np.r_[w, w], (np.r_[a, b], np.r_[b, a])), shape=(n, n)).tocsr()
    out = []
    for c0 in range(0, n, 400):
        idx = np.arange(c0, min(n, c0 + 400)); D = dijkstra(A, directed=False, indices=idx, limit=NB_M + 1e-6)
        for k, i in enumerate(idx):
            j = np.nonzero(np.isfinite(D[k]) & (np.arange(n) != i))[0]; out.append((j, D[k][j]))
    return out


def graph_features(X, seglen, pmay, nbl):
    """X = closure_ml.design columns; -> (n, 5) GRAPH features."""
    ld = X[:, CM.FEATURES.index('log_depth')]; ov = X[:, CM.FEATURES.index('overtop_m')]; hand = X[:, CM.FEATURES.index('hand_m')]
    n = len(ld); G = np.zeros((n, len(GRAPH))); dry = np.log(0.02)
    for i, (j, _) in enumerate(nbl):
        if not len(j): G[i] = (dry, dry, 0.0, -2.0, 0.0); continue
        up = j[hand[j] > hand[i]]
        G[i] = (ld[j].max(), np.average(ld[j], weights=np.maximum(seglen[j], 1.0)), pmay[j].max(),
                ov[up].max() if len(up) else -2.0, np.log1p(seglen[up].sum() / 100.0))
    return G


# ------------------------------------------------------------------------------------------------ data
def load_storm(storm, base=PAR, S=None):
    run = os.path.join(base, f'{storm}_{AREA[storm]}_20m'); rows = list(csv.DictReader(open(os.path.join(run, f'features_{storm}.csv'))))
    X0 = CM.design(rows); seg = np.array([int(r['segment']) for r in rows]); y = np.array([int(r['y']) for r in rows])
    town = np.array([r['town'] for r in rows], dtype=object); depth = np.nan_to_num(np.array([F(r['peak_depth_m'], 0) for r in rows]))
    pmay = np.nan_to_num(np.array([F(r['p_may_close'], 0) for r in rows])); seglen = np.array([F(r['length_m'], 100) for r in rows])
    rep = tuple(sorted({t for t, yy in zip(town, y) if yy}))
    dom_towns = DOMAIN_OVERRIDE.get(storm) or rep
    G = graph_features(X0, seglen, pmay, neighbour_lists(seg, S))
    X = np.column_stack([X0[:, [CM.FEATURES.index(f) for f in CM.MAIN]], G])
    return dict(storm=storm, run=run, rows=rows, seg=seg, y=y, town=town, depth=depth, pmay=pmay, X=X, X0=X0, off=offset_of(depth),
                p_rule=np.nan_to_num(np.array([F(r['p_close'], 0) for r in rows])), rep_towns=rep, dom=np.isin(town, list(dom_towns)),
                local=X0[:, CM.FEATURES.index('local_road')], aadt=np.array([F(r['aadt'], 0) for r in rows]),
                **({'flash': __import__('mrms_flash').load(storm, seg)} if os.environ.get('PROTO_FLASH') == '1' else {}))   # opt-in MRMS FLASH (proto/mrms_flash.py)


def cols(feats):
    names = CM.MAIN + GRAPH; return [names.index(f) for f in feats]


# ------------------------------------------------------------------------------------------------ SAR-PU propensity
def town_rates(S, train):
    pres, rep = {}, {}
    for s in train:
        t, c = np.unique(S[s]['town'], return_counts=True)
        for tt, cc in zip(t, c):
            if cc >= TOWN_MIN_SEGS: pres[tt] = pres.get(tt, 0) + 1; rep[tt] = rep.get(tt, 0) + (tt in S[s]['rep_towns'])
    glob = (sum(rep.values()) + 0.5) / (sum(pres.values()) + 1)
    return lambda towns: np.array([(rep[t] + 0.5) / (pres[t] + 1) if t in pres else glob for t in towns])


def propensity(S, train):
    """-> function storm -> e(x) per row (fitted on the training storms only)."""
    from sklearn.linear_model import LogisticRegression
    rate = town_rates(S, train)
    Z = lambda D: np.column_stack([rate(D['town']), D['local'], np.log1p(D['aadt'] / 1000.0)])
    Xs, ys, ws = [], [], []
    for s in train:
        D = S[s]; m = D['p_rule'] >= 0.5
        if m.sum() == 0: continue
        Xs.append(Z(D)[m]); ys.append(D['y'][m]); ws.append(np.full(m.sum(), 1.0 / m.sum()))
    X, y, w = np.vstack(Xs), np.concatenate(ys), np.concatenate(ws)
    if y.sum() == 0 or y.sum() == len(y): return (lambda D: np.full(len(D['y']), 0.5)), None
    mu, sd = X.mean(0), X.std(0) + 1e-9
    m = LogisticRegression(C=1.0, max_iter=1000).fit((X - mu) / sd, y, sample_weight=w / w.mean())
    return (lambda D: m.predict_proba((Z(D) - mu) / sd)[:, 1]), dict(coef_std=dict(zip(['town_rate', 'local_road', 'log_aadt'], m.coef_[0].round(3).tolist())),
                                                                    intercept=round(float(m.intercept_[0]), 3))


def pu_weights(D, e):
    w = np.ones(len(D['y'])); p = D['y'] == 1
    if p.sum():
        v = 1.0 / np.clip(e[p], 1e-3, 1); v = v / v.mean(); v = np.clip(v, *W_CLIP); w[p] = v / v.mean()
    return w


# ------------------------------------------------------------------------------------------------ models
class Ranker:
    """LightGBM lambdarank, query = storm (reporting domain), init score = rule offset, monotone constraints; score = offset + f(x)."""
    def __init__(self, feats): self.feats = list(feats); self.ix = cols(feats)

    def fit(self, parts):
        import lightgbm as lgb
        X = np.vstack([p['X'][:, self.ix] for p in parts]); y = np.concatenate([p['y'] for p in parts]); o = np.concatenate([p['off'] for p in parts])
        w = np.concatenate([p['w'] for p in parts]); grp = [len(p['y']) for p in parts]
        self.m = lgb.LGBMRanker(monotone_constraints=[SIGN[f] for f in self.feats], **LGB_P).fit(X, y, group=grp, init_score=o, sample_weight=w)
        return self

    def score(self, X, off): return off + self.m.booster_.predict(X[:, self.ix], raw_score=True)


class PairLR:
    """Linear pairwise logistic (RankNet with a linear scorer): score = offset + z(x) . beta, z standardised; loss = mean over storms of the
    PU-weighted mean pair loss softplus(-(s_pos - s_neg)) + PAIR_LAMBDA / 2 |beta|^2; beta sign-bounded by SIGN (L-BFGS-B)."""
    def __init__(self, feats, lam=PAIR_LAMBDA): self.feats = list(feats); self.ix = cols(feats); self.lam = lam

    def fit(self, parts):
        from scipy.optimize import minimize
        Xa = np.vstack([p['X'][:, self.ix] for p in parts]); self.mu = Xa.mean(0); self.sd = Xa.std(0) + 1e-9
        Q = []
        for p in parts:
            pos = p['y'] == 1
            if pos.sum() == 0 or (~pos).sum() == 0: continue
            Z = (p['X'][:, self.ix] - self.mu) / self.sd
            Q.append((Z[pos], Z[~pos], p['off'][pos][:, None] - p['off'][~pos][None, :], p['w'][pos]))
        nq = len(Q)

        def fg(b):
            f = 0.5 * self.lam * b @ b; g = self.lam * b.copy()
            for ZP, ZN, OD, wp in Q:
                d = OD + (ZP @ b)[:, None] - (ZN @ b)[None, :]; W = wp[:, None] / (wp.sum() * ZN.shape[0])
                f += np.sum(W * np.logaddexp(0, -d)) / nq; s = -W / (1 + np.exp(np.clip(d, -50, 50))) / nq
                g += ZP.T @ s.sum(1) - ZN.T @ s.sum(0)
            return f, g
        bounds = [((0, None) if SIGN[f] > 0 else (None, 0) if SIGN[f] < 0 else (None, None)) for f in self.feats]
        r = minimize(fg, np.zeros(len(self.ix)), jac=True, method='L-BFGS-B', bounds=bounds, options=dict(maxiter=500))
        self.beta = r.x; self.ok = bool(r.success); return self

    def score(self, X, off): return off + ((X[:, self.ix] - self.mu) / self.sd) @ self.beta

    def to_json(self): return dict(model='pairwise_linear', features=self.feats, mean=self.mu.tolist(), scale=self.sd.tolist(), beta_std=self.beta.tolist(), lam=self.lam)


class V1:
    """The v1 logistic (closure_ml.LR on MAIN, storm-balanced, reporting domains), refitted inside the same folds as the baseline."""
    def fit(self, parts):
        X = np.vstack([p['X0'] for p in parts]); y = np.concatenate([p['y'] for p in parts])
        w = np.concatenate([np.full(len(p['y']), 1.0 / len(p['y'])) for p in parts]); self.m = CM.LR().fit(X, y, sample_weight=w / w.mean()); return self

    def score(self, X0, off=None): return self.m.decision(X0)


def parts_for(S, train, pu, e_fn=None):
    out = []
    for s in train:
        D = S[s]; m = D['dom']; w = pu_weights(D, e_fn(D)) if (pu and e_fn) else np.ones(len(D['y']))
        out.append(dict(X=D['X'][m], X0=D['X0'][m], y=D['y'][m], off=D['off'][m], w=w[m]))
    return out


def fit_variant(name, S, train):
    if name == 'v1':
        return V1().fit(parts_for(S, train, False)), None
    v = VARIANTS[name]; e_fn, einfo = propensity(S, train) if v['pu'] else (None, None)
    P = parts_for(S, train, v['pu'], e_fn)
    m = Ranker(v['feats']) if v['model'] == 'lgb' else PairLR(v['feats'])
    return m.fit(P), einfo


def score_of(m, D): return m.score(D['X0'], D['off']) if isinstance(m, V1) else m.score(D['X'], D['off'])


# ------------------------------------------------------------------------------------------------ calibration and tier threshold
def platt(s, y):
    from sklearn.linear_model import LogisticRegression
    m = LogisticRegression(C=1e4, max_iter=2000).fit(s[:, None], y); return [float(m.coef_[0][0]), float(m.intercept_[0])]


def platt_apply(ab, s): return 1.0 / (1.0 + np.exp(-(ab[0] * np.asarray(s) + ab[1])))


def isotonic(s, y):
    from sklearn.isotonic import IsotonicRegression
    return IsotonicRegression(out_of_bounds='clip', y_min=0, y_max=1).fit(s, y)


def equal_share_threshold(scores, target):
    """t with mean over storms of share(score >= t) ~= target (bisection on the pooled score range)."""
    allv = np.concatenate(scores); lo, hi = allv.min() - 1, allv.max() + 1
    for _ in range(80):
        t = (lo + hi) / 2; sh = np.mean([(s >= t).mean() for s in scores])
        if sh > target: lo = t
        else: hi = t
    return hi


def nested_fold(name, S, train, held):
    """Outer model on `train`; inner LOSO over `train` for out-of-fold scores -> Platt + equal-share tier threshold."""
    m, einfo = fit_variant(name, S, train)
    oof = {}
    for u in train:
        mi, _ = fit_variant(name, S, [t for t in train if t != u]); oof[u] = score_of(mi, S[u])
    sd = np.concatenate([oof[u][S[u]['dom']] for u in train]); yd = np.concatenate([S[u]['y'][S[u]['dom']] for u in train])
    ab = platt(sd, yd); iso = isotonic(sd, yd)
    target = np.mean([(S[u]['p_rule'] >= 0.5).mean() for u in train])
    t_score = equal_share_threshold([oof[u] for u in train], target)
    out = {}
    for h in held:
        s = score_of(m, S[h])
        out[h] = dict(score=s, p=platt_apply(ab, s), p_iso=iso.predict(s), tier=s >= t_score)
    return out, dict(platt=ab, t_score=float(t_score), t_p=float(platt_apply(ab, t_score)), target_share=float(target), propensity=einfo,
                     model=(m.to_json() if isinstance(m, PairLR) else None))


def run_loso(names, S, groups=None):
    """-> {name: {storm: pred}}, {name: {storm: fold info}}; groups = leave-one-area-out (all storms of the held-out area excluded)."""
    P, I = {}, {}
    for name in names:
        P[name], I[name] = {}, {}
        for h in STORMS:
            if h in P[name]: continue
            held = [s for s in STORMS if groups and groups[s] == groups[h]] if groups else [h]
            train = [s for s in STORMS if s not in held]
            o, info = nested_fold(name, S, train, held)
            for k, v in o.items(): P[name][k] = v; I[name][k] = info
            print(f'  {name}: fold {"+".join(held)} done', flush=True)
    return P, I


# ------------------------------------------------------------------------------------------------ scoring through score_v2
def encode(score, depth, flagged):
    """score_v2 ranks by round(p_close, 3) then depth: map the candidate's order to distinct 3-dp values, flagged tier >= 0.5 (<= 500 distinct
    values inside the tier, 499 below it, then 0; remaining ties fall back to depth, as for the rule)."""
    n = len(score); o = np.lexsort((-depth, -score)); v = np.zeros(n)
    fl = o[flagged[o]]; nf = o[~flagged[o]]
    v[fl] = np.maximum(1.0 - 0.001 * np.arange(len(fl)), 0.5)
    v[nf] = np.maximum(0.499 - 0.001 * np.arange(len(nf)), 0.0)
    return np.round(v, 3)


def write_candidate(D, p, dest):
    import shutil
    os.makedirs(dest, exist_ok=True); s = D['storm']
    for f in ('flood_meta.json', f'matches_{s}.json'): shutil.copy(os.path.join(D['run'], f), dest)
    with open(os.path.join(dest, f'features_{s}.csv'), 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(D['rows'][0].keys())); w.writeheader()
        for r, v in zip(D['rows'], p): w.writerow(dict(r, p_close=f'{float(v):.3f}'))
    return dest


def score_set(S, enc, tag, tmp):
    import score_v2 as SV
    runs = []
    for s in STORMS:
        d = write_candidate(S[s], enc[s], os.path.join(tmp, tag, s)); r = SV.score_run(SV.load_run(d, s)); r.update(primary=True, group=tag); runs.append(r)
    return dict(runs=runs)


def sites_of(D):
    import score_v2 as SV
    R = SV.load_run(D['run'], D['storm']); assert np.array_equal(R['seg'], D['seg'])
    labs = {l['key']: l for l in R['labels']}; mk = [k for k, v in R['matches'].items() if k in labs and v]
    cl = SV.link_clusters(np.array([[labs[k]['x'], labs[k]['y']] for k in mk]).reshape(-1, 2), SV.SITE_LINK_M)
    return [sorted({s for i in np.nonzero(cl == c)[0] for s in R['matches'][mk[i]]}) for c in (np.unique(cl) if len(cl) else [])]


def hits(flag, sites): return np.array([bool(flag[s].any()) for s in sites], float)


def topk(score, depth, k):
    o = np.lexsort((-depth, -score)); f = np.zeros(len(score), bool); f[o[:k]] = True; return f


def paired_boot(ha, hb, storms, boot=2000, seed=0):
    """ha, hb: {storm: per-site hit vector}; two-stage (storms, sites) paired bootstrap of the pooled recall difference a - b."""
    st = [s for s in storms if len(ha[s])]; rng = np.random.default_rng(seed)
    N = sum(len(ha[s]) for s in st); d0 = (sum(ha[s].sum() for s in st) - sum(hb[s].sum() for s in st)) / N; dd = []
    for _ in range(boot):
        a = b = n = 0.0
        for i in rng.integers(0, len(st), len(st)):
            s = st[i]; j = rng.integers(0, len(ha[s]), len(ha[s])); a += ha[s][j].sum(); b += hb[s][j].sum(); n += len(j)
        dd.append((a - b) / n)
    return dict(delta=float(d0), ci90=[float(np.percentile(dd, 5)), float(np.percentile(dd, 95))], p_gt0=float(np.mean(np.array(dd) > 0)),
                hits_a=float(sum(ha[s].sum() for s in st)), hits_b=float(sum(hb[s].sum() for s in st)), sites=int(N))


# ------------------------------------------------------------------------------------------------ reliability
BINS = np.array([0, 0.002, 0.005, 0.01, 0.02, 0.05, 0.1, 0.2, 0.4, 1.0001])


def reliability(p, y):
    i = np.digitize(p, BINS) - 1; out = []
    for b in range(len(BINS) - 1):
        m = i == b
        if m.sum(): out.append(dict(p_mean=round(float(p[m].mean()), 4), obs=round(float(y[m].mean()), 4), n=int(m.sum()), pos=int(y[m].sum())))
    return out


def calib_block(p, y):
    b = float(y.mean()); br = float(np.mean((p - y) ** 2))
    return dict(n=int(len(y)), pos=int(y.sum()), expected=round(float(p.sum()), 1), brier=round(br, 5), bss=round(1 - br / (b * (1 - b)), 3),
                bins=reliability(p, y))


# ------------------------------------------------------------------------------------------------ final fit + map hook
def fit_final(name='v2_pairlr', out=MODEL_V2):
    """All-9-storm fit of the chosen variant, Platt + tier threshold from its LOSO out-of-fold scores (same recipe as one outer fold)."""
    S = {s: load_storm(s) for s in STORMS}; m, einfo = fit_variant(name, S, STORMS); oof = {}
    for u in STORMS:
        mi, _ = fit_variant(name, S, [t for t in STORMS if t != u]); oof[u] = score_of(mi, S[u])
    sd = np.concatenate([oof[u][S[u]['dom']] for u in STORMS]); yd = np.concatenate([S[u]['y'][S[u]['dom']] for u in STORMS])
    ab = platt(sd, yd); t = equal_share_threshold([oof[u] for u in STORMS], np.mean([(S[u]['p_rule'] >= 0.5).mean() for u in STORMS]))
    doc = dict(variant=name, desc=VARIANTS[name]['desc'], trained_on=STORMS, offset=dict(kind='logit(Phi((depth-0.30)/0.10))', clip=OFFSET_CLIP), nb_m=NB_M,
               graph_features=GRAPH, sign=SIGN, platt=ab, tier_score=float(t), tier_p=float(platt_apply(ab, t)), propensity=einfo,
               note='P(documented closure / damage in a reporting town | x), Platt on LOSO out-of-fold scores. See docs/proto/ml/LEARNED_v2.md')
    if isinstance(m, PairLR): doc.update(m.to_json())
    else:
        lg = out.replace('.json', '_lgbm.txt'); m.m.booster_.save_model(lg); doc.update(model='lgb_lambdarank', features=m.feats, booster=os.path.relpath(lg, ROOT))
    json.dump(doc, open(out, 'w'), indent=1); print('wrote', out); return doc


def on_rows_v2(rows, model=MODEL_V2):
    """Adds p_close_v2 (calibrated) and tier_v2 (bool) to prototype segment rows that already carry closure_ml geo columns (call from on_rows)."""
    M = json.load(open(model)); seg = np.array([int(r['segment']) for r in rows])
    X0 = CM.design(rows); pmay = np.array([F(r.get('p_may_close'), 0) for r in rows]); L = np.array([F(r.get('length_m'), 100) for r in rows])
    G = graph_features(X0, L, np.nan_to_num(pmay), neighbour_lists(seg))
    X = np.column_stack([X0[:, [CM.FEATURES.index(f) for f in CM.MAIN]], G]); off = offset_of(np.nan_to_num(np.array([F(r.get('peak_depth_m'), 0) for r in rows])))
    if M['model'] == 'pairwise_linear':
        ix = cols(M['features']); s = off + ((X[:, ix] - np.array(M['mean'])) / np.array(M['scale'])) @ np.array(M['beta_std'])
    else:
        import lightgbm as lgb
        b = lgb.Booster(model_file=os.path.join(ROOT, M['booster'])); s = off + b.predict(X[:, cols(M['features'])], raw_score=True)
    p = platt_apply(M['platt'], s)
    for r, v, sc in zip(rows, p, s): r['p_close_v2'] = round(float(v), 4); r['tier_v2'] = bool(sc >= M['tier_score'])
    return rows


# ------------------------------------------------------------------------------------------------ selftest
def selftest():
    rng = np.random.default_rng(0); ok = True

    def check(name, c):
        nonlocal ok; ok &= bool(c); print(('PASS ' if c else 'FAIL ') + name)
    # neighbour lists on a 3-segment chain 0-1-2 of 200 m each: 0~1 at 200 m, 0~2 at 400 m (> 300: excluded)
    S = dict(props=dict(len=[200, 200, 200, 1000]), links=[[0, 1], [1, 2], [2, 3]])
    nb = neighbour_lists(np.array([0, 1, 2, 3]), S)
    check('chain: 0 sees 1 only', sorted(nb[0][0].tolist()) == [1])
    check('chain: 1 sees 0 and 2', sorted(nb[1][0].tolist()) == [0, 2])
    check('long direct neighbour still counts (capped edge)', 3 in nb[2][0].tolist())
    check('offset clip', abs(offset_of([5.0])[0] - OFFSET_CLIP) < 1e-9 and abs(offset_of([0.0])[0] + OFFSET_CLIP) < 1e-9)
    # pairwise model recovers a correction the offset lacks; sign bounds hold
    parts = []
    for q in range(4):
        n = 3000; X = rng.normal(size=(n, len(CM.MAIN) + len(GRAPH))); off = rng.normal(size=n)
        true = off + 1.5 * X[:, cols(['nb_logdepth_max'])[0]] - 6
        y = (rng.random(n) < 1 / (1 + np.exp(-true))).astype(int); parts.append(dict(X=X, X0=X[:, :11], y=y, off=off, w=np.ones(n)))
    m = PairLR(FEATS).fit(parts); b = dict(zip(m.feats, m.beta))
    check(f"pairwise: nb_logdepth_max beta {b['nb_logdepth_max']:.2f} > 1 and largest", b['nb_logdepth_max'] > 1 and b['nb_logdepth_max'] == max(abs(v) for v in b.values()))
    check('pairwise: sign bounds respected', all(SIGN[f] * v >= -1e-9 for f, v in b.items()))
    r = Ranker(FEATS).fit(parts); s = r.score(parts[0]['X'], parts[0]['off'])
    from sklearn.metrics import roc_auc_score
    check(f"lambdarank beats offset alone ({roc_auc_score(parts[0]['y'], s):.3f} > {roc_auc_score(parts[0]['y'], parts[0]['off']):.3f})",
          roc_auc_score(parts[0]['y'], s) > roc_auc_score(parts[0]['y'], parts[0]['off']))
    # encode keeps the order and the tier
    sc = rng.random(2000); fl = sc > 0.98; e = encode(sc, np.zeros(2000), fl)
    check('encode: tier >= 0.5 exactly', np.array_equal(e >= 0.5, fl))
    o = np.argsort(-sc)[:400]; check('encode: top 400 strictly decreasing', np.all(np.diff(e[o]) < 0))
    t = equal_share_threshold([rng.random(1000), rng.random(500)], 0.03); check(f'equal-share threshold {t:.3f} ~ 0.97', abs(t - 0.97) < 0.01)
    print('selftest', 'OK' if ok else 'FAILED'); return ok


# ------------------------------------------------------------------------------------------------ LOSO driver
def cmd_loso(a):
    import tempfile
    import score_v2 as SV
    os.makedirs(OUTD, exist_ok=True)
    S = {}
    for s in STORMS:
        S[s] = load_storm(s); print(f"{s}: {len(S[s]['y'])} segs, {S[s]['y'].sum()} labelled, domain {S[s]['dom'].sum()}", flush=True)
    names = ['v1'] + list(VARIANTS)
    P, I = run_loso(names, S)
    PL, IL = run_loso(list(ELIGIBLE), S, AREA_GROUP)                  # leakage check (not part of the decision)
    tmp = tempfile.mkdtemp(prefix='v2_'); scored = {}
    base = dict(runs=[dict(SV.score_run(SV.load_run(S[s]['run'], s)), primary=True, group='base') for s in STORMS]); scored['base'] = base
    print('scored base', flush=True)
    enc = {}
    for name in names:
        enc[name] = {s: encode(P[name][s]['score'], S[s]['depth'], P[name][s]['tier']) for s in STORMS}
        scored[name] = score_set(S, enc[name], name, tmp); print('scored', name, flush=True)
        # lowered / raised depth rule with the candidate's tier size in every storm (the 'just flag as many' null)
        eqn = f'eq_{name}'; key = SV.rank_key(S[STORMS[0]]['p_rule'], S[STORMS[0]]['depth'])
        enc[eqn] = {}
        for s in STORMS:
            key = SV.rank_key(S[s]['p_rule'], S[s]['depth']); enc[eqn][s] = encode(key, S[s]['depth'], topk(key, S[s]['depth'], int(P[name][s]['tier'].sum())))
        scored[eqn] = score_set(S, enc[eqn], eqn, tmp); print('scored', eqn, flush=True)
    alpha = SV.ADOPT['alpha'] / K_VARIANTS; rule = dict(SV.ADOPT, alpha=alpha)
    cmp = {}
    for c in VARIANTS:
        for b in ('base', 'v1', f'eq_{c}'):
            cmp[f'{c}_vs_{b}'] = SV.compare(scored[b], scored[c], boot=a.boot, rule=rule)
    cmp['v1_vs_base'] = SV.compare(scored['base'], scored['v1'], boot=a.boot, rule=rule)
    pools = {}
    for name, sc in scored.items():
        R = {r['storm']: r for r in sc['runs']}; pools[name] = {}
        for pn, st in (('heldout7', SV.HELDOUT), ('dev2', SV.DEV), ('all9', tuple(STORMS))):
            for dom in ('box', 'towns'):
                pl = SV.pooled([R[s] for s in st], dom, boot=a.boot)
                pools[name][f'{pn}:{dom}'] = dict(n_sites=pl['n_sites'], point={k: v for k, v in pl['point'].items() if k in ('rule', 'share_0.01', 'share_0.02', 'share_0.03', 'share_0.05', 'share_0.1', 'pr_auc_seg', 'pr_auc_site')},
                                                  ci90={k: v for k, v in pl['ci90'].items() if k in ('rule', 'share_0.03', 'share_0.05')})
    per = {name: {r['storm']: dict(sites=r['domains']['box']['n_sites'], **{f'hits{int(float(sh) * 100)}': r['domains']['box']['shares'][sh]['site_hits'] for sh in ('0.01', '0.02', '0.03', '0.05', '0.1')},
                                   tier_share=r['domains']['box']['rule']['share'], tier_hits=r['domains']['box']['rule']['site_hits'], tier_lift=r['domains']['box']['rule']['lift'],
                                   fss300_3=r['domains']['box']['shares']['0.03']['fss']['300']['fss'], fss300_3_chance=r['domains']['box']['shares']['0.03']['fss']['300']['chance'],
                                   pr_auc_seg=r['domains']['box']['pr_auc']['seg'])
                  for r in sc['runs']} for name, sc in scored.items()}
    # full-resolution within-storm ranking metrics (no 3-dp encoding)
    from sklearn.metrics import average_precision_score, roc_auc_score
    rank = {}
    for name in ['rule'] + names:
        rank[name] = {}
        for s in STORMS:
            sc = S[s]['off'] + S[s]['depth'] * 1e-3 if name == 'rule' else P[name][s]['score']
            rank[name][s] = dict(roc=float(roc_auc_score(S[s]['y'], sc)), pr=float(average_precision_score(S[s]['y'], sc)))
    # watch tier: today's (rule OR v1 >= 0.02) vs the same number of segments by v2 (rule first, then v2 order) vs the depth rule
    sites = {s: sites_of(S[s]) for s in STORMS}; watch = {}
    H = {k: {} for k in ['today', 'eq_depth'] + [f'{v}_rulefirst' for v in ELIGIBLE] + list(ELIGIBLE)}; share = {}
    for s in STORMS:
        D = S[s]; rf = D['p_rule'] >= 0.5; p1 = 1 / (1 + np.exp(-P['v1'][s]['score'])); fl = rf | (p1 >= WATCH_P_V1); k = int(fl.sum()); share[s] = k / len(fl)
        H['today'][s] = hits(fl, sites[s]); key = SV.rank_key(D['p_rule'], D['depth']); H['eq_depth'][s] = hits(topk(key, D['depth'], k), sites[s])
        for v in ELIGIBLE:
            sc = P[v][s]['score']; H[v][s] = hits(topk(sc, D['depth'], k), sites[s]); H[f'{v}_rulefirst'][s] = hits(topk(sc + 1e3 * rf, D['depth'], k), sites[s])
    for pn, st in (('heldout7', SV.HELDOUT), ('all9', tuple(STORMS)), ('dev2', SV.DEV)):
        watch[pn] = dict(share_mean=float(np.mean([share[s] for s in st])),
                         hits={k: float(sum(H[k][s].sum() for s in st)) for k in H}, sites=int(sum(len(sites[s]) for s in st)),
                         **{f'{k}_vs_today': paired_boot(H[k], H['today'], st, a.boot) for k in H if k != 'today'},
                         **{f'{k}_vs_eq_depth': paired_boot(H[k], H['eq_depth'], st, a.boot) for k in H if k not in ('today', 'eq_depth')},
                         today_vs_eq_depth=paired_boot(H['today'], H['eq_depth'], st, a.boot))
    watch['per_storm_share'] = share; watch['per_storm_hits'] = {k: {s: float(v[s].sum()) for s in STORMS} for k, v in H.items()}
    # leave-one-area-out (leakage check): hits at 3 % on OOS-7
    lao = {}
    for v in ELIGIBLE:
        h3 = {}; hb = {}
        for s in STORMS:
            n = len(S[s]['y']); k = int(round(0.03 * n)); h3[s] = hits(topk(PL[v][s]['score'], S[s]['depth'], k), sites[s])
            key = SV.rank_key(S[s]['p_rule'], S[s]['depth']); hb[s] = hits(topk(key, S[s]['depth'], k), sites[s])
        lao[v] = dict(oos7_vs_rule=paired_boot(h3, hb, SV.HELDOUT, a.boot), per_storm={s: float(h3[s].sum()) for s in STORMS})
    # calibration: held-out Platt probabilities (and isotonic as a check)
    cal = {}
    for name in names:
        if name == 'v1':
            pp = {s: 1 / (1 + np.exp(-P['v1'][s]['score'])) for s in STORMS}; pi = None
        else:
            pp = {s: P[name][s]['p'] for s in STORMS}; pi = {s: P[name][s]['p_iso'] for s in STORMS}
        cal[name] = {}
        for dom in ('box', 'towns'):
            msk = {s: (np.ones(len(S[s]['y']), bool) if dom == 'box' else S[s]['dom']) for s in STORMS}
            p_ = np.concatenate([pp[s][msk[s]] for s in STORMS]); y_ = np.concatenate([S[s]['y'][msk[s]] for s in STORMS])
            cal[name][dom] = dict(platt=calib_block(p_, y_))
            if pi: cal[name][dom]['isotonic'] = calib_block(np.concatenate([pi[s][msk[s]] for s in STORMS]), y_)
            cal[name][dom]['per_storm'] = {s: dict(expected=round(float(pp[s][msk[s]].sum()), 1), labelled=int(S[s]['y'][msk[s]].sum())) for s in STORMS}
    folds = {name: {s: {k: v for k, v in I[name][s].items() if k != 'model'} for s in STORMS} for name in names}
    coefs = {name: {s: dict(zip(I[name][s]['model']['features'], np.round(I[name][s]['model']['beta_std'], 3).tolist())) for s in STORMS}
             for name in names if I[name][STORMS[0]].get('model')}
    res = dict(made_by='proto/closure_v2.py loso', baseline_dir=os.path.relpath(PAR, ROOT), k_variants=K_VARIANTS, alpha=alpha, variants={k: v['desc'] for k, v in VARIANTS.items()},
               eligible=list(ELIGIBLE), compare=cmp, pools=pools, per_storm=per, ranking_full_res=rank, watch=watch, leave_one_area_out=lao, calibration=cal,
               folds=folds, pair_coefs=coefs)
    json.dump(res, open(os.path.join(OUTD, 'loso.json'), 'w'), indent=1, default=float)
    for name, sc in scored.items():
        json.dump(dict(made_by='proto/closure_v2.py loso', variant=name, runs=sc['runs']), open(os.path.join(OUTD, f'score_{name}.json'), 'w'))
    for k, v in cmp.items():
        print(k, 'ADOPT' if v['adopt'] else 'reject', round(v['delta_recall'], 3), round(v['delta_recall_lower'], 3), round(v['delta_fss'], 4), v['worst_storm_change'], v['lift_rule'], v['checks'], flush=True)


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0]); ap.add_argument('cmd', choices=['selftest', 'loso', 'fit'])
    ap.add_argument('--boot', type=int, default=2000); ap.add_argument('--variant', default='v2_pairlr')
    a = ap.parse_args()
    if a.cmd == 'selftest': sys.exit(0 if selftest() else 1)
    elif a.cmd == 'loso': cmd_loso(a)
    else: fit_final(a.variant)
