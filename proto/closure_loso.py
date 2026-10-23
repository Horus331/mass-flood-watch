"""Leave-one-storm-out (LOSO) evaluation of the learned road-closure model (proto/closure_ml.py) across all storms with published features,
and the final all-storm fit.

    python proto/closure_loso.py            # -> docs/proto/ml/LOSO.md, loso_results.json, loso_reliability.png, loso_importance.png,
                                            #    docs/proto/ml/closure_lr_all.json (final model used by `closure_ml.py map`)
    python proto/closure_loso.py --reps 200 # fewer bootstrap replicates (quick)
    python proto/closure_loso.py --runs docs/proto/parity/catalog   # other run set (env PROTO_RUNS); output then defaults to <runs>/ml
                                            #    (env PROTO_ML_OUT / --out), so docs/proto/ml and the production model are not overwritten

Data: docs/proto/turing/<storm>_<area>_20m/features_<storm>.csv + matches_<storm>.json (closure_ml.extract output; strict 30 m label match).

Reporting-footprint treatment (training only).  Labels exist only where someone reported, so a whole-box fit learns where reports come from.
Each training storm contributes only its *reporting domain*: the towns with at least one matched label in that storm; for sep2023 Leominster city
only (the DPW inventory, as in closure_ml.TRAIN_TOWNS).  Each storm gets equal total weight (weights 1 / n_domain rows per storm, rescaled to mean 1)
so Leominster's 89 DPW positives do not swamp the eight news/NWS-reported storms.  Held-out storms are scored on the whole box (as the old blind
test) and, as a stricter check, on their own reporting towns (domain picked from the held-out labels, identical for every model: evaluation only).

Fixed before any LOSO number was seen: features = closure_ml.MAIN, logistic C = 0.5 with sign-constrained dropping, HGB settings below.
"""
import argparse
import glob
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import closure_ml as CM  # noqa: E402

ROOT = CM.ROOT
TUR_DEFAULT = os.path.join(ROOT, 'docs', 'proto', 'turing')
TUR = os.path.abspath(os.path.join(ROOT, os.environ['PROTO_RUNS'])) if os.environ.get('PROTO_RUNS') else TUR_DEFAULT   # folder of <storm>_<area>_20m runs
OUT = os.path.abspath(os.path.join(ROOT, os.environ['PROTO_ML_OUT'])) if os.environ.get('PROTO_ML_OUT') else (
    os.path.join(TUR, 'ml') if TUR != TUR_DEFAULT else os.path.join(ROOT, 'docs', 'proto', 'ml'))
STORMS = ['aug2021', 'aug2023', 'aug2023b', 'aug2026', 'jul2021', 'jul2023', 'sep2021', 'sep2022', 'sep2023']
AREA = dict(aug2021='worcester', aug2023='metrowest', aug2023b='millbury', aug2026='leominster', jul2021='worcester', jul2023='worcester',
            sep2021='worcester', sep2022='webster', sep2023='leominster')
# overlapping model boxes (shared segments): leave-one-area-out sensitivity
AREA_GROUP = dict(aug2021='Worcester', aug2023b='Worcester', jul2021='Worcester', jul2023='Worcester', sep2021='Worcester',
                  aug2026='Leominster', sep2023='Leominster', aug2023='MetroWest', sep2022='Webster')
DOMAIN_OVERRIDE = dict(sep2023=('Leominster',))
HGB_P = dict(learning_rate=0.05, max_iter=150, max_depth=3, max_leaf_nodes=8, min_samples_leaf=50, l2_regularization=1.0, random_state=0)


def load(storm):
    d = os.path.join(TUR, f'{storm}_{AREA[storm]}_20m')
    import csv
    rows = list(csv.DictReader(open(os.path.join(d, f'features_{storm}.csv'))))
    M = json.load(open(os.path.join(d, f'matches_{storm}.json')))
    X, y, seg, g = CM.arrays(rows)
    towns = DOMAIN_OVERRIDE.get(storm) or tuple(sorted({r['town'] for r in rows if r['y'] == '1'}))
    return dict(storm=storm, rows=rows, X=X, y=y, seg=seg, block=g, towns=towns, dom=CM.domain(rows, towns), p=CM.prior(rows),
                pm=np.array([float(r['p_may_close'] or 0) for r in rows]), matches=M['matches'], run_dir=M.get('run_dir'),
                town=np.array([r['town'] for r in rows]))


def training_set(S, storms, balanced=True, whole_box=False, with_p=False):
    X, y, w, gs, p = [], [], [], [], []
    for s in storms:
        m = np.ones(len(S[s]['y']), bool) if whole_box else S[s]['dom']
        X.append(S[s]['X'][m]); y.append(S[s]['y'][m]); w.append(np.full(m.sum(), 1.0 / m.sum() if balanced else 1.0)); gs += [s] * int(m.sum()); p.append(S[s]['p'][m])
    w = np.concatenate(w); out = (np.vstack(X), np.concatenate(y), w / w.mean(), np.array(gs))
    return out + (np.concatenate(p),) if with_p else out


class HGB:
    """sklearn HistGradientBoosting with monotone constraints = closure_ml.SIGN; Platt-calibrated on inner leave-one-storm-out predictions."""
    def __init__(self, feats=CM.MAIN): self.feats = list(feats); self.idx = [CM.FEATURES.index(f) for f in feats]
    def _fit(self, X, y, w):
        from sklearn.ensemble import HistGradientBoostingClassifier
        return HistGradientBoostingClassifier(monotonic_cst=[CM.SIGN[f] for f in self.feats], **HGB_P).fit(X[:, self.idx], y, sample_weight=w)
    def fit(self, X, y, w, groups):
        oof = np.zeros(len(y))
        for s in np.unique(groups):
            te = groups == s; oof[te] = self._fit(X[~te], y[~te], w[~te]).predict_proba(X[te][:, self.idx])[:, 1]
        from sklearn.linear_model import LogisticRegression
        m = LogisticRegression(C=1e4, max_iter=1000).fit(CM._logit(oof)[:, None], y, sample_weight=w)
        self.platt = [float(m.coef_[0][0]), float(m.intercept_[0])]; self.m = self._fit(X, y, w); return self
    def predict(self, X): return CM.platt_apply(self.platt, self.m.predict_proba(X[:, self.idx])[:, 1])


class LRP(CM.LR):
    """POST HOC (added after the first LOSO run showed the learned model losing at the top of the ranking): the main logistic plus the rule's own
    score as one more monotone (+) feature, prior_logit = logit(p_close) clipped to [-6, 6] (a sharp 30 cm threshold that log_depth cannot form)."""
    FE = CM.FEATURES + ['prior_logit']
    def _x(self, X, p): return np.column_stack([X, np.clip(CM._logit(p), -6, 6)])
    def fit(self, X, y, sample_weight=None, p=None):
        from sklearn.linear_model import LogisticRegression
        X = self._x(X, p); sign = dict(CM.SIGN, prior_logit=1); keep = [self.FE.index(f) for f in CM.MAIN + ['prior_logit']]; self.dropped = []
        while True:
            mu = X[:, keep].mean(0); sd = X[:, keep].std(0) + 1e-9
            m = LogisticRegression(C=self.C, max_iter=2000).fit((X[:, keep] - mu) / sd, y, sample_weight=sample_weight)
            bad = [(abs(b), j) for j, b in zip(keep, m.coef_[0]) if sign[self.FE[j]] * b < 0]
            if not bad: break
            j = max(bad)[1]; keep.remove(j); self.dropped.append(self.FE[j])
        self.keep, self.mu, self.sd, self.coef, self.b0, self.names = keep, mu, sd, m.coef_[0], float(m.intercept_[0]), [self.FE[j] for j in keep]
        return self
    def predict(self, X, p=None): return 1.0 / (1.0 + np.exp(-(((self._x(X, p)[:, self.keep] - self.mu) / self.sd) @ self.coef + self.b0)))


MODELS = {
    'lr': 'logistic, storm-balanced, reporting domains (main)',
    'lr_unw': 'logistic, unweighted, reporting domains',
    'lr_box': 'logistic, storm-balanced, whole boxes (confound check)',
    'hgb': 'HistGB monotone + Platt, storm-balanced, reporting domains',
}


def fit_model(kind, S, storms):
    if kind == 'lr_prior':
        X, y, w, _, p = training_set(S, storms, with_p=True); return LRP().fit(X, y, sample_weight=w, p=p)
    if kind == 'hgb':
        X, y, w, g = training_set(S, storms); return HGB().fit(X, y, w, g)
    X, y, w, _ = training_set(S, storms, balanced=kind != 'lr_unw', whole_box=kind == 'lr_box')
    return CM.LR().fit(X, y, sample_weight=w)


# ---------------------------------------------------------------- metrics
def rank_order(score, seed=0):
    n = len(score); return np.lexsort((np.random.default_rng(seed).random(n), -score))


def topk_recall(score, y, k, seeds=5):
    if k <= 0: return 0.0
    return float(np.mean([y[rank_order(score, s)[:k]].sum() / y.sum() for s in range(seeds)]))


def share_at_recall(score, y, rec, seeds=5):
    """Smallest flagged share (top-k by score) whose recall reaches `rec` (ties random, averaged)."""
    need = int(np.ceil(rec * y.sum() - 1e-9))
    if need <= 0: return 0.0
    out = []
    for s in range(seeds):
        cs = np.cumsum(y[rank_order(score, s)]); out.append((np.searchsorted(cs, need) + 1) / len(y))
    return float(np.mean(out))


def site_recall(flag, matches, segidx):
    sites = [[segidx[g] for g in m['segs'] if g in segidx] for m in matches.values()]; sites = [s for s in sites if s]
    return float(np.mean([flag[s].any() for s in sites])) if sites else np.nan


def storm_metrics(q, y, p, pm, matches=None, segidx=None):
    """q = learned P; p = rule p_close; pm = may-close overtop layer. Rule flag = P >= 0.5."""
    from sklearn.metrics import average_precision_score, roc_auc_score
    n, P = len(y), int(y.sum()); out = dict(n=n, pos=P, base=float(y.mean()))
    if P == 0: return out
    for nm, sc in (('ml', q), ('rule', p), ('mayclose', pm)):
        out[f'roc_{nm}'] = float(roc_auc_score(y, sc)); out[f'pr_{nm}'] = float(average_precision_score(y, sc))
    for ref, sc in (('rule', p), ('mayclose', pm)):
        fl = sc >= 0.5; sh = float(fl.mean()); rr = float(y[fl].sum() / P); k = int(fl.sum())
        rm = topk_recall(q, y, k); sm = share_at_recall(q, y, rr)
        out.update({f'{ref}_share': sh, f'{ref}_recall': rr, f'ml_recall_at_{ref}_share': rm, f'ml_share_at_{ref}_recall': sm,
                    f'{ref}_lift': rr / sh if sh else np.nan, f'ml_lift_at_{ref}_share': rm / sh if sh else np.nan})
        if matches is not None:
            fm = np.zeros(n, bool); fm[rank_order(q)[:k]] = True
            out[f'{ref}_site_recall'] = site_recall(fl, matches, segidx); out[f'ml_site_recall_at_{ref}_share'] = site_recall(fm, matches, segidx)
    out.update(brier_ml=float(np.mean((q - y) ** 2)), brier_rule=float(np.mean((p - y) ** 2)), brier_base=float(y.mean() * (1 - y.mean())),
               exp_ml=float(q.sum()), exp_rule=float(p.sum()))
    out['bss_ml'] = 1 - out['brier_ml'] / out['brier_base']; out['bss_rule'] = 1 - out['brier_rule'] / out['brier_base']
    return out


BOOT_KEYS = ['roc_ml', 'roc_rule', 'pr_ml', 'pr_rule', 'ml_recall_at_rule_share', 'rule_recall', 'ml_share_at_rule_recall', 'rule_share',
             'roc_mayclose', 'pr_mayclose', 'ml_recall_at_mayclose_share', 'mayclose_recall']


def block_boot(q, y, p, pm, block, reps, seed=0):
    """Paired 2 km block bootstrap within one storm (labels cluster at sites; resampling segments would understate the spread)."""
    rng = np.random.default_rng(seed); ub, inv = np.unique(block, return_inverse=True); members = [np.nonzero(inv == b)[0] for b in range(len(ub))]
    R = {k: [] for k in BOOT_KEYS + ['d_roc', 'd_pr', 'd_rec']}
    for _ in range(reps):
        i = np.concatenate([members[b] for b in rng.integers(0, len(ub), len(ub))])
        if y[i].sum() == 0 or y[i].sum() == len(i): continue
        m = storm_metrics(q[i], y[i], p[i], pm[i])
        for k in BOOT_KEYS: R[k].append(m[k])
        R['d_roc'].append(m['roc_ml'] - m['roc_rule']); R['d_pr'].append(m['pr_ml'] - m['pr_rule']); R['d_rec'].append(m['ml_recall_at_rule_share'] - m['rule_recall'])
    return {k: [float(np.percentile(v, 5)), float(np.percentile(v, 95)), float(np.mean(np.array(v) > 0))] for k, v in R.items() if v}


def pooled(parts):
    """parts: list of (q, y, p, pm) per storm. Pooled = concatenated AUCs; recall pooled over positives with each storm flagged at its own rule share."""
    from sklearn.metrics import average_precision_score, roc_auc_score
    q, y, p, pm = (np.concatenate([a[j] for a in parts]) for j in range(4)); out = {}
    for nm, j in (('ml', 0), ('rule', 2), ('mayclose', 3)):          # stratified ROC-AUC: only (positive, negative) pairs from the same storm
        num = den = 0.0
        for a in parts:
            P_, N_ = int(a[1].sum()), int(len(a[1]) - a[1].sum())
            if P_ and N_: num += roc_auc_score(a[1], a[j]) * P_ * N_; den += P_ * N_
        out[f'sroc_{nm}'] = num / den if den else np.nan
    for nm, sc in (('ml', q), ('rule', p), ('mayclose', pm)):
        out[f'roc_{nm}'] = float(roc_auc_score(y, sc)); out[f'pr_{nm}'] = float(average_precision_score(y, sc))
    for ref, j in (('rule', 2), ('mayclose', 3)):
        tp_r = tp_m = fl_n = 0; shares = []
        for a in parts:
            fl = a[j] >= 0.5; k = int(fl.sum()); tp_r += a[1][fl].sum(); tp_m += topk_recall(a[0], a[1], k) * a[1].sum(); fl_n += k
            shares.append(share_at_recall(a[0], a[1], a[1][fl].sum() / a[1].sum()) * len(a[1]))
        out[f'{ref}_share'] = fl_n / len(y); out[f'{ref}_recall'] = float(tp_r / y.sum()); out[f'ml_recall_at_{ref}_share'] = float(tp_m / y.sum())
        out[f'ml_share_at_{ref}_recall'] = float(np.sum(shares) / len(y))
        out[f'{ref}_lift'] = out[f'{ref}_recall'] / out[f'{ref}_share']; out[f'ml_lift_at_{ref}_share'] = out[f'ml_recall_at_{ref}_share'] / out[f'{ref}_share']
    out.update(brier_ml=float(np.mean((q - y) ** 2)), brier_rule=float(np.mean((p - y) ** 2)), brier_base=float(y.mean() * (1 - y.mean())), n=len(y), pos=int(y.sum()),
               exp_ml=float(q.sum()), exp_rule=float(p.sum()))
    out['bss_ml'] = 1 - out['brier_ml'] / out['brier_base']; out['bss_rule'] = 1 - out['brier_rule'] / out['brier_base']
    return out


def pooled_boot(parts, blocks, reps, seed=1):
    """Two-stage cluster bootstrap: storms resampled with replacement, then 2 km blocks within each drawn storm."""
    rng = np.random.default_rng(seed); K = ['sroc_ml', 'sroc_rule', 'roc_ml', 'roc_rule', 'pr_ml', 'pr_rule', 'ml_recall_at_rule_share', 'rule_recall', 'ml_share_at_rule_recall', 'rule_share']
    R = {k: [] for k in K + ['d_roc', 'd_sroc', 'd_pr', 'd_rec', 'macro_d_roc']}
    pre = []
    for a, b in zip(parts, blocks):
        ub, inv = np.unique(b, return_inverse=True); pre.append([np.nonzero(inv == j)[0] for j in range(len(ub))])
    for _ in range(reps):
        sub, dr = [], []
        for s in rng.integers(0, len(parts), len(parts)):
            mem = pre[s]; i = np.concatenate([mem[j] for j in rng.integers(0, len(mem), len(mem))]); a = parts[s]
            if a[1][i].sum() == 0: continue
            sub.append(tuple(x[i] for x in a))
            if 0 < a[1][i].sum() < len(i):
                from sklearn.metrics import roc_auc_score
                dr.append(roc_auc_score(a[1][i], a[0][i]) - roc_auc_score(a[1][i], a[2][i]))
        if len(sub) < 2: continue
        m = pooled(sub)
        for k in K: R[k].append(m[k])
        R['d_sroc'].append(m['sroc_ml'] - m['sroc_rule']); R['d_roc'].append(m['roc_ml'] - m['roc_rule']); R['d_pr'].append(m['pr_ml'] - m['pr_rule'])
        R['d_rec'].append(m['ml_recall_at_rule_share'] - m['rule_recall']); R['macro_d_roc'].append(np.mean(dr))
    return {k: [float(np.percentile(v, 5)), float(np.percentile(v, 95)), float(np.mean(np.array(v) > 0))] for k, v in R.items() if v}


# ---------------------------------------------------------------- run
def loso(S, kind, groups=None):
    """Out-of-storm predictions on every held-out box. groups: storm -> group id (leave-one-group-out instead)."""
    preds = {}
    for s in STORMS:
        g = groups[s] if groups else s
        tr = [t for t in STORMS if (groups[t] if groups else t) != g]
        m = fit_model(kind, S, tr); preds[s] = m.predict(S[s]['X'], p=S[s]['p']) if kind == 'lr_prior' else m.predict(S[s]['X'])
    return preds


def perm_importance(S, preds_models, reps=5):
    """Mean drop of held-out ROC-AUC (whole box, macro over storms) when one feature is permuted within the held-out storm (LOSO main logistic)."""
    from sklearn.metrics import roc_auc_score
    imp = {}
    for f in CM.MAIN:
        j = CM.FEATURES.index(f); d = []
        for s in STORMS:
            m = preds_models[s]; X = S[s]['X']; y = S[s]['y']; base = roc_auc_score(y, m.predict(X))
            for r in range(reps):
                X2 = X.copy(); X2[:, j] = np.random.default_rng(r).permutation(X2[:, j]); d.append((s, base - roc_auc_score(y, m.predict(X2))))
        per = {s: float(np.mean([v for t, v in d if t == s])) for s in STORMS}
        imp[f] = dict(macro=float(np.mean(list(per.values()))), per_storm=per)
    return imp


def coef_boot(S, reps, seed=2):
    """Final all-storm logistic: coefficients per SD with a two-stage cluster bootstrap (storms, then 2 km blocks); a feature dropped for sign counts as 0."""
    rng = np.random.default_rng(seed); out = {f: [] for f in CM.MAIN}
    for _ in range(reps):
        X, y, w = [], [], []
        for s in rng.choice(STORMS, len(STORMS)):
            d = S[s]['dom']; b = S[s]['block'][d]; ub, inv = np.unique(b, return_inverse=True)
            i = np.concatenate([np.nonzero(inv == j)[0] for j in rng.integers(0, len(ub), len(ub))])
            X.append(S[s]['X'][d][i]); y.append(S[s]['y'][d][i]); w.append(np.full(len(i), 1.0 / len(i)))
        X, y, w = np.vstack(X), np.concatenate(y), np.concatenate(w)
        if y.sum() < 5: continue
        m = CM.LR().fit(X, y, sample_weight=w / w.mean()); c = dict(zip(m.names, m.coef))
        for f in CM.MAIN: out[f].append(c.get(f, 0.0))
    return {f: [float(np.percentile(v, 5)), float(np.percentile(v, 95)), float(np.mean(np.array(v) != 0))] for f, v in out.items()}


def main(reps):
    S = {s: load(s) for s in STORMS}
    for s in STORMS: S[s]['idx'] = {g: i for i, g in enumerate(S[s]['seg'])}
    P = {k: loso(S, k) for k in MODELS}
    P['lr_lao'] = loso(S, 'lr', AREA_GROUP)
    P['lr_prior'] = loso(S, 'lr_prior')
    res_prior_dropped = fit_model('lr_prior', S, STORMS).dropped
    # POST HOC (after the first LOSO run): rule-first ranking, the rule's flagged set first, everything ordered by the learned P inside and after it
    P['hybrid'] = {s: (S[s]['p'] >= 0.5).astype(float) + 0.999 * P['lr'][s] for s in STORMS}
    MODELS_ALL = dict(MODELS, lr_lao='logistic main, leave-one-AREA-out (overlapping boxes held out together)',
                      lr_prior='POST HOC: logistic main + logit(p_close) feature', hybrid='POST HOC: rule-first hybrid (p_close >= 0.5 first, then learned order)')
    loso_lr = {s: fit_model('lr', S, [t for t in STORMS if t != s]) for s in STORMS}
    res = dict(per_storm={}, pooled={}, pooled_domain={}, macro={}, boot={}, boot_pooled={}, wins={})
    for k in MODELS_ALL:
        per, perd, parts, partsd, blocks, blocksd = {}, {}, [], [], [], []
        for s in STORMS:
            D = S[s]; q = P[k][s]
            per[s] = storm_metrics(q, D['y'], D['p'], D['pm'], D['matches'], D['idx'])
            dm = np.isin(D['town'], [t for t in D['towns']]) if s != 'sep2023' else D['dom']
            ids = {g: i for i, g in enumerate(np.array(D['seg'])[dm])}
            perd[s] = storm_metrics(q[dm], D['y'][dm], D['p'][dm], D['pm'][dm], D['matches'], ids)
            parts.append((q, D['y'], D['p'], D['pm'])); blocks.append(D['block'])
            partsd.append((q[dm], D['y'][dm], D['p'][dm], D['pm'][dm])); blocksd.append(D['block'][dm])
        res['per_storm'][k] = per; res['per_storm'][k + '@domain'] = perd
        res['pooled'][k] = pooled(parts); res['pooled_domain'][k] = pooled(partsd)
        res['macro'][k] = {m: float(np.mean([per[s][m] for s in STORMS])) for m in ('roc_ml', 'roc_rule', 'roc_mayclose', 'pr_ml', 'pr_rule', 'pr_mayclose',
                                                                                   'ml_recall_at_rule_share', 'rule_recall', 'ml_share_at_rule_recall', 'rule_share')}
        res['wins'][k] = dict(roc=int(sum(per[s]['roc_ml'] > per[s]['roc_rule'] for s in STORMS)), pr=int(sum(per[s]['pr_ml'] > per[s]['pr_rule'] for s in STORMS)),
                              rec=int(sum(per[s]['ml_recall_at_rule_share'] > per[s]['rule_recall'] + 1e-9 for s in STORMS)),
                              rec_tie=int(sum(abs(per[s]['ml_recall_at_rule_share'] - per[s]['rule_recall']) <= 1e-9 for s in STORMS)),
                              roc_domain=int(sum(perd[s]['roc_ml'] > perd[s]['roc_rule'] for s in STORMS if 'roc_ml' in perd[s])))
        if k in ('lr', 'hgb', 'hybrid'):
            res['boot'][k] = {s: block_boot(P[k][s], S[s]['y'], S[s]['p'], S[s]['pm'], S[s]['block'], reps, seed=i) for i, s in enumerate(STORMS)}
            res['boot_pooled'][k] = pooled_boot(parts, blocks, reps); res['boot_pooled'][k + '@domain'] = pooled_boot(partsd, blocksd, reps)
    # sign test over storms (ROC-AUC, main)
    from scipy.stats import binomtest
    res['sign_test_roc_lr'] = float(binomtest(res['wins']['lr']['roc'], len(STORMS), 0.5, alternative='greater').pvalue)
    # calibration (main, LOSO probabilities)
    qa = np.concatenate([P['lr'][s] for s in STORMS]); ya = np.concatenate([S[s]['y'] for s in STORMS]); pa = np.concatenate([S[s]['p'] for s in STORMS])
    dmask = np.concatenate([S[s]['dom'] for s in STORMS])
    res['reliability'] = dict(ml_box=CM.reliability(qa, ya), rule_box=CM.reliability(pa, ya), ml_domain=CM.reliability(qa[dmask], ya[dmask]),
                              rule_domain=CM.reliability(pa[dmask], ya[dmask]))
    res['brier_domain'] = dict(ml=float(np.mean((qa[dmask] - ya[dmask]) ** 2)), rule=float(np.mean((pa[dmask] - ya[dmask]) ** 2)),
                               base=float(ya[dmask].mean() * (1 - ya[dmask].mean())), exp_ml=float(qa[dmask].sum()), exp_rule=float(pa[dmask].sum()), pos=int(ya[dmask].sum()))
    # PU constant from LOSO predictions inside the reporting domains
    res['pu_c_e1'] = float(qa[dmask & (ya == 1)].mean())
    res['perm'] = perm_importance(S, loso_lr)
    res['coef_ci'] = coef_boot(S, max(100, reps // 2))
    final = fit_model('lr', S, STORMS)
    res['final'] = dict(names=final.names, coef=dict(zip(final.names, final.coef.tolist())), intercept=final.b0, dropped=final.dropped)
    X, y, w, g = training_set(S, STORMS)
    final.save(os.path.join(OUT, 'closure_lr_all.json'), dict(
        trained_on=STORMS, domain_towns={s: list(S[s]['towns']) for s in STORMS}, n=int(len(y)), positives=int(y.sum()), weights='storm-balanced (1/n_domain per storm, mean 1)',
        pu_c_e1=res['pu_c_e1'], runs={s: S[s]['run_dir'] for s in STORMS},
        note='P(documented closure/damage | x) at the average reporting completeness of the training storms\' reporting towns; ranking is the '
             'tested quantity, probabilities run high outside reporting towns. Leave-one-storm-out scores: docs/proto/ml/LOSO.md'))
    res['data'] = {s: dict(n=len(S[s]['y']), pos=int(S[s]['y'].sum()), sites=len(S[s]['matches']), domain_towns=list(S[s]['towns']), domain_n=int(S[s]['dom'].sum()),
                           domain_pos=int(S[s]['y'][S[s]['dom']].sum()), run_dir=S[s]['run_dir'], rule_share=float((S[s]['p'] >= 0.5).mean())) for s in STORMS}
    res['models'] = MODELS_ALL; res['hgb_params'] = HGB_P; res['lr_prior_dropped'] = res_prior_dropped
    json.dump(res, open(os.path.join(OUT, 'loso_results.json'), 'w'), indent=1, default=float)
    figures(res); write_md(res)
    return res


def figures(res):
    import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
    fig, axs = plt.subplots(1, 2, figsize=(10, 4.4))
    for ax, (tag, title) in zip(axs, (('box', 'held-out storms, whole box'), ('domain', 'held-out storms, reporting towns'))):
        ax.plot([1e-4, 1], [1e-4, 1], color='#9a9a9a', lw=1, ls='--', label='perfect calibration')
        for k, col, mk, lab in (('rule', '#1baf7a', 's', 'rule p_close (30 cm)'), ('ml', '#2a78d6', 'o', 'logistic, LOSO')):
            pts = [p_ for p_ in res['reliability'][f'{k}_{tag}'] if p_[0] > 0]
            ax.plot([p_[0] for p_ in pts], [max(p_[1], 2e-4) for p_ in pts], color=col, marker=mk, lw=2, ms=7, mec='white', label=lab)
        ax.set_xscale('log'); ax.set_yscale('log'); ax.set_xlim(1e-3, 1.2); ax.set_ylim(1.5e-4, 1.2); ax.grid(alpha=.25, lw=.6)
        ax.set_xlabel('predicted probability (bin mean)'); ax.set_ylabel('observed share labeled (0 drawn at 2e-4)'); ax.set_title(title, fontsize=10)
        ax.spines[['top', 'right']].set_visible(False)
    axs[0].legend(fontsize=8, frameon=False); fig.tight_layout(); fig.savefig(os.path.join(OUT, 'loso_reliability.png'), dpi=130); plt.close(fig)
    fig, axs = plt.subplots(1, 2, figsize=(10.5, 4.2))
    C, CI = res['final']['coef'], res['coef_ci']; nm = sorted(CM.MAIN, key=lambda f: abs(C.get(f, 0)))
    v = [C.get(f, 0) for f in nm]; lo = [v[i] - CI[f][0] for i, f in enumerate(nm)]; hi = [CI[f][1] - v[i] for i, f in enumerate(nm)]
    axs[0].barh(nm, v, xerr=[np.maximum(lo, 0), np.maximum(hi, 0)], color=['#2a78d6' if x >= 0 else '#eb6834' for x in v], height=.6, ecolor='#555555', capsize=2)
    axs[0].axvline(0, color='#666666', lw=.8); axs[0].set_title('all-storm logistic: coef / SD, 90 % cluster bootstrap', fontsize=10)
    I = {f: res['perm'][f]['macro'] for f in CM.MAIN}; k2 = sorted(I, key=I.get)
    axs[1].barh(k2, [I[f] for f in k2], color='#2a78d6', height=.6); axs[1].axvline(0, color='#666666', lw=.8)
    axs[1].set_title('LOSO permutation importance: ROC-AUC drop (macro)', fontsize=10)
    for a in axs: a.spines[['top', 'right']].set_visible(False); a.grid(axis='x', alpha=.25, lw=.6)
    fig.tight_layout(); fig.savefig(os.path.join(OUT, 'loso_importance.png'), dpi=130); plt.close(fig)


def write_md(res):
    f = lambda v, d=3: '-' if v is None or (isinstance(v, float) and np.isnan(v)) else f'{v:.{d}f}'
    ci = lambda c, d=2: f' [{c[0]:.{d}f}, {c[1]:.{d}f}]' if c else ''
    pc = lambda v: f'{100 * v:.1f} %'
    B = res['boot']['lr']; PB = res['boot_pooled']['lr']; PL = res['pooled']['lr']; W = res['wins']['lr']
    L = ['# Learned road-closure model: leave-one-storm-out (LOSO)', '',
         'Made by `python proto/closure_loso.py` (reuses `proto/closure_ml.py`: same 10 hazard/terrain features `MAIN`, same sign-constrained L2 logistic with C = 0.5, '
         'same strict 30 m label matching from `extract`). Data: `' + os.path.relpath(TUR, ROOT) + '/<storm>_<area>_20m/features_<storm>.csv`, 9 storms. For each held-out storm the '
         'model is fitted on the other 8 and scored on the held-out box against the rule-based closure probability `p_close` = Phi((peak depth - 0.30) / 0.10) and the '
         'may-close overtop layer `p_may_close`, both read off the same flood run. Nothing was tuned on LOSO: features, C, HGB settings and the main variant were fixed '
         'before the first LOSO run.', '',
         '## Data', '', '| storm | segments | labeled segs | sites | training domain (reporting towns) | domain segs / labeled | rule flags (p >= 0.5) |', '|---|---|---|---|---|---|---|']
    for s, d in res['data'].items():
        L.append(f"| {s} | {d['n']} | {d['pos']} | {d['sites']} | {', '.join(d['domain_towns'])} | {d['domain_n']} / {d['domain_pos']} | {pc(d['rule_share'])} |")
    tot = sum(d['pos'] for d in res['data'].values())
    L += ['', f"{tot} labeled segments in all; {res['data']['sep2023']['pos']} of them are Sept 2023 (89 from the Leominster DPW inventory). The other eight storms have 5-13 "
          'each, from news / NWS / agency reports. Several boxes overlap (five Worcester-area storms, two Leominster storms), and a handful of labeled segments repeat '
          'between storms, so a leave-one-AREA-out run is reported as a check on location leakage.', '',
          '## Reporting-footprint confound: treatment', '',
          '- **Training** uses each storm\'s reporting domain only: the towns with at least one matched report in that storm; Sept 2023 keeps the old rule, Leominster city '
          'only, where the DPW inventory makes "unlabeled" close to "undamaged". Outside the reporting towns "unlabeled" mostly means "nobody reported", and a whole-box '
          'fit would learn the footprint (in Sept 2023 rain alone had AUC 0.87 for that reason, see RESULTS.md).',
          '- **Storm-balanced weights** (each storm\'s domain sums to the same weight). Unweighted, Leominster\'s 89 DPW positives would make this a one-city model again.',
          '- **Evaluation** on the whole held-out box (as the old blind test) and, stricter, inside the held-out storm\'s reporting towns, where "which town reported" '
          'cannot help any model. The held-out domain is defined from held-out labels, but identically for the rule and the model: it is only a stratum for scoring.',
          '- The confound check row (`lr_box`, trained on whole boxes) shows what happens without the domain restriction.', '',
          '## Headline (main model: logistic, storm-balanced, reporting domains)', '',
          f"Pooled over the 9 held-out storms ({PL['n']} segments, {PL['pos']} labeled). [a, b] = 5-95 % two-stage cluster bootstrap (storms, then 2 km blocks); "
          '"P(>0)" = share of bootstrap replicates where learned minus rule is positive.', '',
          '| metric | learned (LOSO) | rule p_close | may-close layer | learned - rule, 90 % CI | P(>0) |', '|---|---|---|---|---|---|',
          f"| ROC-AUC, stratified (pairs within the same storm) | {f(PL['sroc_ml'])}{ci(PB['sroc_ml'])} | {f(PL['sroc_rule'])}{ci(PB['sroc_rule'])} | {f(PL['sroc_mayclose'])} | {PL['sroc_ml'] - PL['sroc_rule']:+.3f}{ci(PB['d_sroc'], 3)} | {PB['d_sroc'][2]:.2f} |",
          f"| ROC-AUC (all storms concatenated; see note) | {f(PL['roc_ml'])}{ci(PB['roc_ml'])} | {f(PL['roc_rule'])}{ci(PB['roc_rule'])} | {f(PL['roc_mayclose'])} | {PL['roc_ml'] - PL['roc_rule']:+.3f}{ci(PB['d_roc'], 3)} | {PB['d_roc'][2]:.2f} |",
          f"| ROC-AUC (mean of per-storm differences) | {f(res['macro']['lr']['roc_ml'])} | {f(res['macro']['lr']['roc_rule'])} | {f(res['macro']['lr']['roc_mayclose'])} | {res['macro']['lr']['roc_ml'] - res['macro']['lr']['roc_rule']:+.3f}{ci(PB['macro_d_roc'], 3)} | {PB['macro_d_roc'][2]:.2f} |",
          f"| PR-AUC (pooled) | {f(PL['pr_ml'])}{ci(PB['pr_ml'])} | {f(PL['pr_rule'])}{ci(PB['pr_rule'])} | {f(PL['pr_mayclose'])} | {PL['pr_ml'] - PL['pr_rule']:+.3f}{ci(PB['d_pr'], 3)} | {PB['d_pr'][2]:.2f} |",
          f"| recall at the rule's flagged share ({pc(PL['rule_share'])} of segments) | {f(PL['ml_recall_at_rule_share'], 2)}{ci(PB['ml_recall_at_rule_share'])} | {f(PL['rule_recall'], 2)}{ci(PB['rule_recall'])} | - | {PL['ml_recall_at_rule_share'] - PL['rule_recall']:+.2f}{ci(PB['d_rec'])} | {PB['d_rec'][2]:.2f} |",
          f"| flagged share needed for the rule's recall | {pc(PL['ml_share_at_rule_recall'])} | {pc(PL['rule_share'])} | - | - | - |",
          f"| lift at the rule's flagged share (recall / share) | {f(PL['ml_lift_at_rule_share'], 1)} | {f(PL['rule_lift'], 1)} | - | - | - |",
          f"| recall at the may-close layer's share ({pc(PL['mayclose_share'])}) | {f(PL['ml_recall_at_mayclose_share'], 2)} | - | {f(PL['mayclose_recall'], 2)} | - | - |",
          f"| flagged share for the may-close layer's recall | {pc(PL['ml_share_at_mayclose_recall'])} | - | {pc(PL['mayclose_share'])} | - | - |",
          f"| Brier (BSS vs base rate) | {f(PL['brier_ml'], 4)} ({PL['bss_ml']:+.2f}) | {f(PL['brier_rule'], 4)} ({PL['bss_rule']:+.2f}) | - | - | - |",
          f"| expected / labeled | {PL['exp_ml']:.0f} / {PL['pos']} | {PL['exp_rule']:.0f} / {PL['pos']} | - | - | - |", '',
          f"Storm-by-storm the learned model has the higher ROC-AUC on **{W['roc']} of 9** storms (one-sided sign test p = {res['sign_test_roc_lr']:.2f}), higher PR-AUC on "
          f"{W['pr']} of 9, and higher recall at the rule's flagged share on {W['rec']} of 9 (tied on {W['rec_tie']}). Inside the held-out reporting towns it wins ROC-AUC on {W['roc_domain']} of 9.", '']
    PD = res['pooled_domain']['lr']; PBD = res['boot_pooled']['lr@domain']
    L += ['Same, scored only inside each held-out storm\'s reporting towns:', '',
          f"| metric | learned | rule | learned - rule, 90 % CI |", '|---|---|---|---|',
          f"| ROC-AUC stratified | {f(PD['sroc_ml'])} | {f(PD['sroc_rule'])} | {PD['sroc_ml'] - PD['sroc_rule']:+.3f}{ci(PBD['d_sroc'], 3)} |",
          f"| ROC-AUC concatenated | {f(PD['roc_ml'])} | {f(PD['roc_rule'])} | {PD['roc_ml'] - PD['roc_rule']:+.3f}{ci(PBD['d_roc'], 3)} |",
          f"| PR-AUC pooled | {f(PD['pr_ml'])} | {f(PD['pr_rule'])} | {PD['pr_ml'] - PD['pr_rule']:+.3f}{ci(PBD['d_pr'], 3)} |",
          f"| recall at rule's share ({pc(PD['rule_share'])}) | {f(PD['ml_recall_at_rule_share'], 2)} | {f(PD['rule_recall'], 2)} | {PD['ml_recall_at_rule_share'] - PD['rule_recall']:+.2f}{ci(PBD['d_rec'])} |",
          f"| share for rule's recall | {pc(PD['ml_share_at_rule_recall'])} | {pc(PD['rule_share'])} | - |", '']
    # model variants
    L += ['## Model variants (pooled over held-out storms, whole box)', '', '| model | stratified ROC-AUC | mean per-storm ROC-AUC | PR-AUC (concat.) | recall at rule share | share for rule recall | recall at may-close share | wins ROC / PR (of 9) | stratified ROC-AUC in reporting towns |', '|---|---|---|---|---|---|---|---|---|']
    for k, nm in res['models'].items():
        p_, m_, w_, d_ = res['pooled'][k], res['macro'][k], res['wins'][k], res['pooled_domain'][k]
        L.append(f"| {nm} | {f(p_['sroc_ml'])} | {f(m_['roc_ml'])} | {f(p_['pr_ml'])} | {f(p_['ml_recall_at_rule_share'], 2)} | {pc(p_['ml_share_at_rule_recall'])} | {f(p_['ml_recall_at_mayclose_share'], 2)} | {w_['roc']} / {w_['pr']} | {f(d_['sroc_ml'])} |")
    L.append(f"| *rule p_close (reference)* | {f(PL['sroc_rule'])} | {f(res['macro']['lr']['roc_rule'])} | {f(PL['pr_rule'])} | {f(PL['rule_recall'], 2)} | {pc(PL['rule_share'])} | - | - | {f(PD['sroc_rule'])} |")
    L.append(f"| *may-close layer (reference)* | {f(PL['sroc_mayclose'])} | {f(res['macro']['lr']['roc_mayclose'])} | {f(PL['pr_mayclose'])} | - | - | {f(PL['mayclose_recall'], 2)} | - | {f(PD['sroc_mayclose'])} |")
    L += ['', f"`lr_prior`: the rule's logit got a negative weight next to log_depth and the sign check dropped it ({', '.join(res['lr_prior_dropped']) or 'nothing dropped'}), "
          'so this variant reduces to the main model. The hybrid has no probabilities of its own (Brier not defined); bootstrap for it:']
    HB = res['boot_pooled']['hybrid']; HP = res['pooled']['hybrid']
    L += [f"stratified ROC-AUC {f(HP['sroc_ml'])}{ci(HB['sroc_ml'])} vs rule {f(HP['sroc_rule'])} (diff {HP['sroc_ml'] - HP['sroc_rule']:+.3f}{ci(HB['d_sroc'], 3)}, P(>0) {HB['d_sroc'][2]:.2f}); "
          f"PR-AUC {f(HP['pr_ml'])} vs {f(HP['pr_rule'])} (diff{ci(HB['d_pr'], 3)}, P(>0) {HB['d_pr'][2]:.2f}).", '']
    # per-storm
    L += ['', '## Per storm (main model, whole held-out box)', '',
          'rec@rule = recall when the learned model flags as many segments as the rule does (p_close >= 0.5); share@rule-rec = flagged share the learned model needs to '
          'match the rule\'s recall; site = share of documented sites with a flagged segment. Intervals: 5-95 % paired 2 km block bootstrap within the storm.', '',
          '| held-out | labeled | ROC-AUC learned | ROC-AUC rule | ROC may-close | PR-AUC learned | PR-AUC rule | rule share | rule recall | learned rec@rule | site: rule / learned | share@rule-rec | lift rule / learned | dROC 90 % CI |',
          '|---|---|---|---|---|---|---|---|---|---|---|---|---|---|']
    for s in STORMS:
        m = res['per_storm']['lr'][s]; b = B[s]
        L.append(f"| {s} | {m['pos']} | {f(m['roc_ml'])} | {f(m['roc_rule'])} | {f(m['roc_mayclose'])} | {f(m['pr_ml'])}{ci(b['pr_ml'])} | {f(m['pr_rule'])}{ci(b['pr_rule'])} | "
                 f"{pc(m['rule_share'])} | {f(m['rule_recall'], 2)} | {f(m['ml_recall_at_rule_share'], 2)} | {f(m['rule_site_recall'], 2)} / {f(m['ml_site_recall_at_rule_share'], 2)} | "
                 f"{pc(m['ml_share_at_rule_recall'])} | {f(m['rule_lift'], 1)} / {f(m['ml_lift_at_rule_share'], 1)} | {ci(b['d_roc'], 3).strip()} |")
    L += ['', 'HistGB (monotone) per storm, ROC-AUC / PR-AUC: ' + '; '.join(f"{s} {f(res['per_storm']['hgb'][s]['roc_ml'])} / {f(res['per_storm']['hgb'][s]['pr_ml'])}" for s in STORMS) + '.',
          'Leave-one-area-out logistic, ROC-AUC: ' + '; '.join(f"{s} {f(res['per_storm']['lr_lao'][s]['roc_ml'])}" for s in STORMS) + '.', '',
          'Per storm inside reporting towns (main), ROC-AUC learned / rule: ' + '; '.join(
              f"{s} {f(res['per_storm']['lr@domain'][s].get('roc_ml'))} / {f(res['per_storm']['lr@domain'][s].get('roc_rule'))}" for s in STORMS) + '.', '']
    # calibration
    BD = res['brier_domain']
    L += ['## Calibration', '', '![reliability](loso_reliability.png)', '',
          f"LOSO probabilities of the main model. Whole boxes: Brier {f(PL['brier_ml'], 4)} (BSS {PL['bss_ml']:+.2f}) vs rule {f(PL['brier_rule'], 4)} (BSS {PL['bss_rule']:+.2f}); "
          f"expected {PL['exp_ml']:.0f} vs {PL['pos']} labeled (rule: {PL['exp_rule']:.0f}). Inside the reporting domains: Brier {f(BD['ml'], 4)} (BSS {1 - BD['ml'] / BD['base']:+.2f}) vs rule "
          f"{f(BD['rule'], 4)} (BSS {1 - BD['rule'] / BD['base']:+.2f}); expected {BD['exp_ml']:.0f} vs {BD['pos']} labeled (rule {BD['exp_rule']:.0f}).", '',
          'Per bin (mean P -> observed share labeled (segments, labeled)):', '']
    for k, pts in res['reliability'].items(): L.append(f"- {k}: " + '; '.join(f'{a:.3f} -> {b:.3f} ({n_}, {p_})' for a, b, n_, p_ in pts))
    L += ['', 'Per storm expected / labeled (learned, rule): ' + '; '.join(
        f"{s} {res['per_storm']['lr'][s]['exp_ml']:.0f} / {res['per_storm']['lr'][s]['exp_rule']:.0f} vs {res['per_storm']['lr'][s]['pos']}" for s in STORMS) + '.', '',
          f"PU constant (Elkan-Noto e1) from LOSO predictions on labeled segments inside reporting domains: c = **{res['pu_c_e1']:.3f}** (stored in the model file).", '']
    # drivers
    C, CI, I = res['final']['coef'], res['coef_ci'], res['perm']
    L += ['## Drivers', '', '![importance](loso_importance.png)', '',
          f"Final all-storm logistic (intercept {res['final']['intercept']:+.2f}; log-odds per SD). CI = 5-95 % two-stage cluster bootstrap (storms, 2 km blocks), "
          '"kept" = share of replicates where the sign check kept the feature. Permutation = mean drop in held-out ROC-AUC (LOSO models, macro over storms, 5 shuffles).', '',
          '| feature | expected sign | coef / SD | 90 % CI | kept | permutation dROC-AUC | storms where permutation hurts |', '|---|---|---|---|---|---|---|']
    for ft in sorted(CM.MAIN, key=lambda x: -abs(C.get(x, 0))):
        sg = '+' if CM.SIGN[ft] > 0 else '-' if CM.SIGN[ft] < 0 else 'free'
        hurt = sum(v > 0.002 for v in I[ft]['per_storm'].values())
        L.append(f"| {ft} | {sg} | {('%+.3f' % C[ft]) if ft in C else 'dropped (sign)'} | [{CI[ft][0]:+.2f}, {CI[ft][1]:+.2f}] | {CI[ft][2]:.2f} | {I[ft]['macro']:+.4f} | {hurt} / 9 |")
    L += ['', f"Dropped from the final fit for contradicting the expected sign: {', '.join(res['final']['dropped']) or 'none'}.", '']
    if TUR == TUR_DEFAULT:            # the hand-written notes discuss the published (docs/proto/turing) run set only
        L += open(os.path.join(HERE, 'ml', 'LOSO_notes.md')).read().splitlines() if os.path.exists(os.path.join(HERE, 'ml', 'LOSO_notes.md')) else []
    os.makedirs(OUT, exist_ok=True)
    open(os.path.join(OUT, 'LOSO.md'), 'w').write('\n'.join(L) + '\n')


if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('--reps', type=int, default=1000)
    ap.add_argument('--runs', help='folder of <storm>_<area>_20m runs (default docs/proto/turing; env PROTO_RUNS)')
    ap.add_argument('--out', help='output folder (default docs/proto/ml, or <runs>/ml with --runs; env PROTO_ML_OUT)'); a = ap.parse_args()
    if a.runs: TUR = os.path.abspath(a.runs); OUT = os.path.join(TUR, 'ml') if TUR != TUR_DEFAULT and not os.environ.get('PROTO_ML_OUT') else OUT
    if a.out: OUT = os.path.abspath(a.out)
    os.makedirs(OUT, exist_ok=True)
    r = main(a.reps); p = r['pooled']['lr']
    print(json.dumps({k: round(v, 4) if isinstance(v, float) else v for k, v in p.items()}, indent=0)); print('wins', r['wins'])
