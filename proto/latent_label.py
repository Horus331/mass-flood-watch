"""Hidden-state ('latent true flooding') label model for road segments (docs/proto/latent/LATENT.md; pre-registration PREREG.md).

    python proto/latent_label.py selftest            # synthetic data: recovers detection / false-report rates and the prevalence model
    python proto/latent_label.py cache               # load the 25 non-locked parity storms once -> scratch cache (LATENT_CACHE)
    python proto/latent_label.py fit                 # all-storm fit + storm bootstrap CIs -> docs/proto/latent/fit_all.json, posterior/, bias map
    python proto/latent_label.py loso                # leave-one-storm-out pi(x) for every storm, latent (L1) and naive control (N0)
    python proto/latent_label.py write-runs          # scratch candidate run folders (p_close replaced by the rank of pi), for score_v2
    python proto/latent_label.py score               # score baseline / L1 / N0 with proto/score_v2.py, --compare v2 (k=2), calibration
    python proto/latent_label.py d456                # secondary: frozen all-storm pi on the District 4-6 transfer runs (never fitted on)

Model (fixed in PREREG.md before any held-out score).  For segment i in storm t (unit = segment-storm):
    Z_it ~ Bernoulli(pi_it),  logit pi_it = b_o * o_it + b_0 + b . h_it        o = 1.7 * clip((peak depth - 0.30) / 0.10, -6, 6): the deployed
                                                                               physics rule's probit, on the logit scale (the offset)
    Y_its | Z ~ Bernoulli(Z * d_its + (1 - Z) * f_s)   for every source s that OPERATES at (i, t); otherwise Y_its is missing, not 0
    logit d_its = a_s + g . r_it   (DPW: a_s only)                             r = reporting-propensity covariates, h = hazard covariates
Fit: MAP-EM (E-step: q_it = P(Z = 1 | Y, x); M-step: soft-label logistic for pi, q-weighted logistic for d, closed-form Beta MAP for f).
No report = unknown: an unreported segment only lowers q through (1 - d), and only where a source operates.
"""
import csv
import glob
import json
import os
import pickle
import sys

import numpy as np
from scipy.optimize import minimize
from scipy.special import expit, log_expit

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
DATA = os.path.join(HERE, 'data')
OUT = os.path.join(ROOT, 'docs', 'proto', 'latent')
CAT = os.path.join(ROOT, 'docs', 'proto', 'parity', 'catalog')
SCR = os.environ.get('LATENT_SCRATCH') or os.path.join(os.environ.get('TMPDIR', '/tmp'), 'latent_scratch')
LOCKED = ('aug2015', 'aug2018', 'aug2020', 'jul2018', 'oct2016')

# ---------------------------------------------------------------- pre-registered settings (PREREG.md, 28 Oct 2026)
HAZ = ['log_h15', 'log_area', 'log_hand', 'log_slope', 'p_culvert', 'p_overtop', 'p_sag', 'p_edge', 'log_p1h', 'log_sdist', 'log_len']
REP = ['major_road', 'log_aadt', 'town_activity']
FAMILIES = ['NWS', 'news', 'WX1BOX', 'MassDOT_crash', 'SeeClickFix', 'DPW', 'MA_state', 'Waze', 'MassDOT_closure']
ALWAYS_ON = ('NWS', 'news', 'WX1BOX', 'MassDOT_crash')       # operate on every segment of every storm (crash data fetched for all 25 storms)
COMPLETE = dict(sep2023=('Leominster',))                       # DPW complete-detection domain (score_v2.COMPLETE)
PRIOR = dict(b_o=(1.0, 0.3), b_0=(0.0, 3.0), b=(0.0, 1.0),     # Gaussian (mean, sd) on the standardized scale
             a=(-1.5, 1.5), a_dpw=(2.2, 0.5), g=(0.0, 1.0),     # logit d: generic source ~0.18 at mean r; DPW ~0.90 (complete inventory)
             f=(1.0, 2000.0))                                  # Beta(1, 2000) on the per-segment false-report rate: MAP 0 + data, mean 5e-4
EM_TOL, EM_MAXIT = 1e-5, 300
NBOOT_FIT = 100                                                # storm-cluster bootstrap of the all-storm fit (CIs of d_s, f_s, coefficients)


def F(x, d=0.0):
    try: v = float(x); return v if np.isfinite(v) else d
    except (TypeError, ValueError): return d


# ---------------------------------------------------------------- sources
def source_files(storm):
    if storm in LOCKED: return []
    out = sorted(glob.glob(os.path.join(DATA, f'labels_{storm}_*.csv')))
    for pat in (f'crashwater_{storm}.csv', f'scf_{storm}.csv', f'waze_{storm}*.csv', f'massdot_closure_{storm}*.csv'):
        out += sorted(glob.glob(os.path.join(DATA, pat)))
    return out


def family(row, fname):
    if fname.startswith('waze_') or (row.get('source') or '') == 'Waze': return 'Waze'
    if fname.startswith('massdot_closure_') or (row.get('source') or '') == 'MassDOT_closure': return 'MassDOT_closure'
    import label_tiers as LT
    return LT.family(row, fname)


def scf_towns(storm, seg_xy, seg_town):
    """Towns where SeeClickFix operated during the storm: any issue of any type in the storm window (round3/scf_window_<storm>.json)."""
    p = os.path.join(ROOT, 'docs', 'proto', 'obs', 'round3', f'scf_window_{storm}.json')
    if not os.path.exists(p): return set()
    I = json.load(open(p)).get('issues') or []
    if not I: return set()
    from pyproj import Transformer
    from scipy.spatial import cKDTree
    tr = Transformer.from_crs(4326, 26986, always_xy=True); x, y = tr.transform([F(i['lng']) for i in I], [F(i['lat']) for i in I])
    d, j = cKDTree(seg_xy).query(np.column_stack([x, y]))
    return {seg_town[k] for k, dd in zip(j, d) if dd < 1000}


# ---------------------------------------------------------------- data
def run_dirs():
    out = {}
    for d in sorted(glob.glob(os.path.join(CAT, '*_20m'))):
        import score_v2 as SV
        s = SV.storm_of(os.path.basename(d))
        if s and s not in LOCKED and os.path.exists(os.path.join(d, f'features_{s}.csv')): out[s] = d
    return out


def hazard(rows):
    g = lambda k: np.array([F(r.get(k)) for r in rows])
    dep = g('peak_depth_m')
    o = 1.7 * np.clip((dep - 0.30) / 0.10, -6, 6)
    H = np.column_stack([np.log1p(g('hours_over_15cm')), np.log1p(g('area_km2')), np.log1p(np.clip(g('hand_m'), 0, None)),
                         np.log1p(np.clip(g('slope_pct'), 0, None)), g('p_culvert'), g('p_overtop'), g('p_sag'), g('p_edge'),
                         np.log1p(g('peak1h_mm')), np.log1p(g('stream_dist_m')), np.log1p(g('length_m'))])
    return o, H


def load_storm(storm, run_dir, features_csv=None):
    """One storm: features (same universe and order as score_v2), source observations Y (n x S, nan = source not operating)."""
    import score_v2 as SV
    SV.label_files = source_files                    # score_v2's matching (published matches + strict 30 m) on ALL sources
    R = SV.load_run(run_dir, storm)
    rows = list(csv.DictReader(open(features_csv or os.path.join(run_dir, f'features_{storm}.csv'))))
    assert [int(r['segment']) for r in rows] == list(R['seg'])
    fam = {}
    for f in source_files(storm):
        for r in csv.DictReader(open(f)): fam[f'{os.path.basename(f)}:{r["id"]}'] = family(r, os.path.basename(f))
    n = len(rows); town = np.array([r['town'] for r in rows], dtype=object)
    Y = np.full((n, len(FAMILIES)), np.nan); has = {fam[k] for k in fam}
    xy = np.column_stack([[F(r['cx']) for r in rows], [F(r['cy']) for r in rows]])
    for j, s in enumerate(FAMILIES):
        if s in ALWAYS_ON: Y[:, j] = 0
        elif s == 'DPW' and storm in COMPLETE and s in has: Y[np.isin(town, COMPLETE[storm]), j] = 0
        elif s == 'SeeClickFix': Y[np.isin(town, list(scf_towns(storm, xy, town))), j] = 0
        elif s in ('MA_state', 'Waze', 'MassDOT_closure') and s in has: Y[:, j] = 0
    nrep = {}
    for k, segs in R['matches'].items():
        j = FAMILIES.index(fam.get(k, 'news'))
        for i in segs:
            if np.isnan(Y[i, j]): Y[i, j] = 0          # a report from outside the assumed operating domain: the source did operate there
            Y[i, j] = 1
        t = {town[i] for i in segs}
        for tt in t: nrep[tt] = nrep.get(tt, 0) + 1
    o, H = hazard(rows)
    rc = np.array([r['road_class'] for r in rows])
    Rr = np.column_stack([(rc != 'local / collector').astype(float), np.log1p(np.array([F(r['aadt']) for r in rows]))])
    return dict(storm=storm, run_dir=run_dir, seg=R['seg'], town=town, o=o, H=H, R2=Rr, Y=Y, nrep_town=nrep, xy=xy,
                p_close=np.array([F(r['p_close']) for r in rows]), depth=np.array([F(r['peak_depth_m']) for r in rows]),
                y_dec=np.array([int(r['y']) for r in rows]), n_rule=int((np.array([F(r['p_close']) for r in rows]) >= 0.5).sum()))


def cache_path(): return os.path.join(SCR, 'cache.pkl')


def get_cache():
    return pickle.load(open(cache_path(), 'rb'))


def assemble(D, storms, stats=None):
    """Stack storms; town_activity = log1p(mean reports per storm in the town over the OTHER storms of `storms`); standardize on `storms`."""
    o = np.concatenate([D[s]['o'] for s in storms]); H = np.vstack([D[s]['H'] for s in storms])
    Y = np.vstack([D[s]['Y'] for s in storms]); R2 = np.vstack([D[s]['R2'] for s in storms])
    ta = []
    for s in storms:
        others = [u for u in storms if u != s]
        ta.append(np.array([np.log1p(sum(D[u]['nrep_town'].get(t, 0) for u in others) / max(1, len(others))) for t in D[s]['town']]))
    Rr = np.column_stack([R2, np.concatenate(ta)])
    if stats is None: stats = dict(hm=H.mean(0), hs=H.std(0) + 1e-9, rm=Rr.mean(0), rs=Rr.std(0) + 1e-9)
    idx = np.concatenate([np.full(len(D[s]['o']), k) for k, s in enumerate(storms)])
    return dict(o=o, H=(H - stats['hm']) / stats['hs'], R=(Rr - stats['rm']) / stats['rs'], Y=Y, storm_idx=idx, storms=list(storms), stats=stats)


def design_new(Dt, stats, ref_storms, D):
    """Hazard / reporting design for a storm NOT in the fit, standardized with the fit's statistics (town activity from the fit storms)."""
    H = (Dt['H'] - stats['hm']) / stats['hs']
    ta = np.array([np.log1p(sum(D[u]['nrep_town'].get(t, 0) for u in ref_storms) / max(1, len(ref_storms))) for t in Dt['town']]) if D else np.zeros(len(Dt['o']))
    Rr = (np.column_stack([Dt['R2'], ta]) - stats['rm']) / stats['rs']
    return Dt['o'], H, Rr


# ---------------------------------------------------------------- model
def _pi_logit(th, o, H): return th[0] * o + th[1] + H @ th[2:]


def _pi_prior(th):
    m = np.r_[PRIOR['b_o'][0], PRIOR['b_0'][0], np.full(len(th) - 2, PRIOR['b'][0])]
    s = np.r_[PRIOR['b_o'][1], PRIOR['b_0'][1], np.full(len(th) - 2, PRIOR['b'][1])]
    return m, s


def fit_pi(o, H, q, th0):
    """MAP soft-label logistic: maximize sum q log pi + (1-q) log(1-pi) + Gaussian prior."""
    m, s = _pi_prior(th0); X = np.column_stack([o, np.ones(len(o)), H])

    def fun(th):
        z = X @ th; ll = (q * log_expit(z) + (1 - q) * log_expit(-z)).sum(); g = X.T @ (q - expit(z))
        return -(ll - 0.5 * (((th - m) / s) ** 2).sum()), -(g - (th - m) / s ** 2)
    return minimize(fun, th0, jac=True, method='L-BFGS-B').x


def _d_logit(ph, R, j):
    S = len(FAMILIES); a = ph[:S]; g = ph[S:]
    z = a[j] + (R @ g if FAMILIES[j] != 'DPW' else 0.0)
    return z


def fit_d(R, Y, q, ph0):
    """q-weighted logistic for detection: rows (i, s) with s operating at i; source intercepts + shared reporting slopes (DPW: intercept only)."""
    S = len(FAMILIES); obs = ~np.isnan(Y)
    pm = np.r_[[PRIOR['a_dpw'][0] if f == 'DPW' else PRIOR['a'][0] for f in FAMILIES], np.full(R.shape[1], PRIOR['g'][0])]
    ps = np.r_[[PRIOR['a_dpw'][1] if f == 'DPW' else PRIOR['a'][1] for f in FAMILIES], np.full(R.shape[1], PRIOR['g'][1])]
    blocks = [(j, np.where(obs[:, j])[0]) for j in range(S)]

    def fun(ph):
        ll = 0.0; gr = np.zeros_like(ph)
        for j, ii in blocks:
            if not len(ii): continue
            z = _d_logit(ph, R[ii], j); y = Y[ii, j]; w = q[ii]
            ll += (w * (y * log_expit(z) + (1 - y) * log_expit(-z))).sum(); r = w * (y - expit(z))
            gr[j] += r.sum()
            if FAMILIES[j] != 'DPW': gr[S:] += R[ii].T @ r
        return -(ll - 0.5 * (((ph - pm) / ps) ** 2).sum()), -(gr - (ph - pm) / ps ** 2)
    return minimize(fun, ph0, jac=True, method='L-BFGS-B').x


def fit_f(Y, q):
    a, b = PRIOR['f']; obs = ~np.isnan(Y); out = np.zeros(Y.shape[1])
    for j in range(Y.shape[1]):
        ii = obs[:, j]; w = 1 - q[ii]; y = Y[ii, j]
        out[j] = (np.sum(w * y) + a - 1) / (np.sum(w) + a + b - 2) if ii.any() else a / (a + b)
    return np.clip(out, 1e-7, 0.5)


def posterior(th, ph, f, o, H, R, Y):
    lp = _pi_logit(th, o, H); A = log_expit(lp); B = log_expit(-lp); obs = ~np.isnan(Y)
    for j in range(Y.shape[1]):
        ii = np.where(obs[:, j])[0]
        if not len(ii): continue
        z = _d_logit(ph, R[ii], j); y = Y[ii, j]
        A[ii] += y * log_expit(z) + (1 - y) * log_expit(-z); B[ii] += y * np.log(f[j]) + (1 - y) * np.log1p(-f[j])
    return expit(A - B), expit(lp)


def p_detect(ph, R, Y):
    """P(at least one operating source reports | Z = 1) per row: the reporting-bias surface."""
    obs = ~np.isnan(Y); miss = np.ones(len(R))
    for j in range(Y.shape[1]):
        ii = obs[:, j]
        if ii.any(): miss[ii] *= 1 - expit(_d_logit(ph, R[ii], j))
    return 1 - miss


def em(A, init=None, verbose=False):
    o, H, R, Y = A['o'], A['H'], A['R'], A['Y']
    yany = np.nan_to_num(Y, nan=0).max(1)
    th = init['th'] if init else np.r_[1.0, -2.0, np.zeros(H.shape[1])]
    ph = init['ph'] if init else np.r_[[PRIOR['a_dpw'][0] if s == 'DPW' else PRIOR['a'][0] for s in FAMILIES], np.zeros(R.shape[1])]
    f = init['f'] if init else np.full(Y.shape[1], 1e-4)
    q = posterior(th, ph, f, o, H, R, Y)[0] if init else np.clip(yany, 0.01, 0.99)
    for it in range(EM_MAXIT):
        th = fit_pi(o, H, q, th); ph = fit_d(R, Y, q, ph); f = fit_f(Y, q)
        q2, pi = posterior(th, ph, f, o, H, R, Y); dq = np.abs(q2 - q).max(); q = q2
        if verbose and it % 10 == 0: print(f'  EM {it:3d} max|dq| {dq:.2e} sum q {q.sum():.1f} sum pi {pi.sum():.1f}', flush=True)
        if dq < EM_TOL: break
    return dict(th=th, ph=ph, f=f, q=q, pi=pi, iters=it + 1, dq=float(dq))


def naive(A):
    """Control N0: the same pi design fitted by ordinary MAP logistic on y = any matched report (unreported = dry)."""
    y = np.nan_to_num(A['Y'], nan=0).max(1)
    return fit_pi(A['o'], A['H'], y, np.r_[1.0, -2.0, np.zeros(A['H'].shape[1])])


def summarize(fit, A):
    S = len(FAMILIES); obs = ~np.isnan(A['Y'])
    out = dict(iters=fit['iters'], sources={})
    for j, s in enumerate(FAMILIES):
        n_op = int(obs[:, j].sum()); n_y = int(np.nansum(A['Y'][:, j]))
        if not n_op: continue
        ii = obs[:, j]; w = fit['q'][ii]
        dbar = float((w * expit(_d_logit(fit['ph'], A['R'][ii], j))).sum() / max(w.sum(), 1e-9))
        out['sources'][s] = dict(n_operating=n_op, n_reports=n_y, d_at_mean_r=float(expit(fit['ph'][j])), d_mean_flooded=dbar,
                                 f=float(fit['f'][j]), expected_false=float(((1 - fit['q'][ii]) * A['Y'][ii, j]).sum()))
    out['g'] = dict(zip(REP, map(float, fit['ph'][S:]))); out['b_o'] = float(fit['th'][0]); out['b_0'] = float(fit['th'][1])
    out['b'] = dict(zip(HAZ, map(float, fit['th'][2:])))
    out['sum_q'] = float(fit['q'].sum()); out['sum_pi'] = float(fit['pi'].sum()); out['n_rows'] = int(len(fit['q']))
    out['n_any_report'] = int(np.nan_to_num(A['Y'], nan=0).max(1).sum())
    return out


# ---------------------------------------------------------------- selftest
def selftest():
    rng = np.random.default_rng(0); n = 60000
    o = rng.normal(-4, 2, n); H = rng.normal(size=(n, len(HAZ))); R = rng.normal(size=(n, len(REP)))
    th = np.r_[1.0, 0.5, 0.8, -0.5, np.zeros(len(HAZ) - 2)]; Z = rng.random(n) < expit(_pi_logit(th, o, H))
    d_true = dict(NWS=0.15, news=0.1, WX1BOX=0.08, MassDOT_crash=0.05, SeeClickFix=0.3, DPW=0.92)
    f_true = 2e-4; g = np.array([0.6, 0.4, 0.8])
    Y = np.full((n, len(FAMILIES)), np.nan)
    for j, s in enumerate(FAMILIES):
        if s not in d_true: continue
        op = np.ones(n, bool) if s in ALWAYS_ON else (rng.random(n) < (0.1 if s == 'DPW' else 0.3))
        dz = expit(np.log(d_true[s] / (1 - d_true[s])) + (0 if s == 'DPW' else R @ g))
        p = np.where(Z, dz, f_true); Y[op, j] = (rng.random(op.sum()) < p[op]).astype(float)
    A = dict(o=o, H=H, R=R, Y=Y); fit = em(A)
    ok = True
    for j, s in enumerate(FAMILIES):
        if s in d_true:
            e = float(expit(fit['ph'][j])); print(f'  {s:14s} d true {d_true[s]:.2f} est {e:.2f}  f est {fit["f"][j]:.1e}'); ok &= abs(np.log(e / d_true[s])) < 0.45
    print('  g true', g, 'est', np.round(fit['ph'][len(FAMILIES):], 2)); print('  b true', th[:4], 'est', np.round(fit['th'][:4], 2))
    print('  sum Z', int(Z.sum()), 'sum q', round(fit['q'].sum(), 1), 'sum pi', round(fit['pi'].sum(), 1))
    ok &= abs(fit['q'].sum() / Z.sum() - 1) < 0.2
    print('selftest', 'OK' if ok else 'FAILED'); return ok


# ---------------------------------------------------------------- pipeline
def cmd_cache():
    os.makedirs(SCR, exist_ok=True); D = {}
    for s, d in run_dirs().items():
        D[s] = load_storm(s, d); Y = D[s]['Y']
        print(s, len(D[s]['seg']), 'reports by source', {f: int(np.nansum(Y[:, j])) for j, f in enumerate(FAMILIES) if np.nansum(Y[:, j])}, flush=True)
    pickle.dump(D, open(cache_path(), 'wb'))


def cmd_fit(boot=NBOOT_FIT):
    D = get_cache(); storms = sorted(D); A = assemble(D, storms); fit = em(A, verbose=True); S0 = summarize(fit, A)
    reps = []
    rng = np.random.default_rng(0)
    for b in range(boot):
        sel = [storms[k] for k in rng.integers(0, len(storms), len(storms))]
        Db = {f'{s}#{k}': D[s] for k, s in enumerate(sel)}; Ab = assemble(Db, list(Db)); fb = em(Ab, init=fit); reps.append(summarize(fb, Ab))
        if b % 10 == 0: print('boot', b, flush=True)
    ci = lambda xs: [float(np.percentile(xs, 5)), float(np.percentile(xs, 95))] if xs else None
    for s, v in S0['sources'].items():
        for k in ('d_at_mean_r', 'd_mean_flooded', 'f'): v[k + '_ci90'] = ci([r['sources'][s][k] for r in reps if s in r['sources']])
    S0['g_ci90'] = {k: ci([r['g'][k] for r in reps]) for k in REP}; S0['b_ci90'] = {k: ci([r['b'][k] for r in reps]) for k in HAZ}
    S0['b_o_ci90'] = ci([r['b_o'] for r in reps]); S0['sum_q_ci90'] = ci([r['sum_q'] for r in reps]); S0['boot'] = boot
    S0['storms'] = storms; S0['prior'] = PRIOR; S0['stats'] = {k: v.tolist() for k, v in A['stats'].items()}
    S0['theta'] = fit['th'].tolist(); S0['phi'] = fit['ph'].tolist(); S0['f_all'] = fit['f'].tolist()
    os.makedirs(os.path.join(OUT, 'posterior'), exist_ok=True)
    pd_ = p_detect(fit['ph'], A['R'], A['Y']); per = {}
    for k, s in enumerate(storms):
        ii = A['storm_idx'] == k; Ds = D[s]; yany = np.nan_to_num(Ds['Y'], nan=0)
        per[s] = dict(n=int(ii.sum()), reports=int(yany.max(1).sum()), sum_q=float(fit['q'][ii].sum()), sum_pi=float(fit['pi'][ii].sum()),
                      mean_p_detect=float(pd_[ii].mean()))
        with open(os.path.join(OUT, 'posterior', f'{s}.csv'), 'w') as fh:
            w = csv.writer(fh); w.writerow(['segment', 'town', 'pi', 'q_post', 'p_detect', 'sources_reporting'])
            for i, gi in zip(np.where(ii)[0], range(ii.sum())):
                rep = ';'.join(FAMILIES[j] for j in range(len(FAMILIES)) if yany[gi, j] == 1)
                if fit['q'][i] >= 0.05 or rep:
                    w.writerow([int(Ds['seg'][gi]), Ds['town'][gi], f"{fit['pi'][i]:.4f}", f"{fit['q'][i]:.4f}", f'{pd_[i]:.3f}', rep])
    S0['per_storm'] = per
    json.dump(S0, open(os.path.join(OUT, 'fit_all.json'), 'w'), indent=1)
    pickle.dump(dict(fit=fit, A=A, pd=pd_), open(os.path.join(SCR, 'fit_all.pkl'), 'wb'))
    bias_map(D, storms, A, pd_)
    print(json.dumps({s: {k: round(v[k], 4) for k in ('d_at_mean_r', 'f')} for s, v in S0['sources'].items()}, indent=0))


def bias_map(D, storms, A, pd_):
    """Town-level reporting-bias map: mean P(any source reports | flooded) over the segment-storms of each town."""
    import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
    xy = np.vstack([D[s]['xy'] for s in storms]); town = np.concatenate([D[s]['town'] for s in storms])
    fig, ax = plt.subplots(1, 2, figsize=(12, 5.5))
    sc = ax[0].scatter(xy[:, 0] / 1e3, xy[:, 1] / 1e3, c=pd_, s=1, cmap='viridis', vmin=0, vmax=np.percentile(pd_, 99))
    plt.colorbar(sc, ax=ax[0], label='P(report | flooded)'); ax[0].set_title('Detection probability per segment-storm (25 storms overlaid)')
    ax[0].set_xlabel('x km (EPSG:26986)'); ax[0].set_ylabel('y km'); ax[0].set_aspect('equal')
    T = sorted(set(town), key=lambda t: -pd_[town == t].mean()); T = [t for t in T if (town == t).sum() >= 200][:25]
    ax[1].barh(range(len(T)), [pd_[town == t].mean() for t in T]); ax[1].set_yticks(range(len(T))); ax[1].set_yticklabels(T, fontsize=7)
    ax[1].invert_yaxis(); ax[1].set_xlabel('mean P(report | flooded)'); ax[1].set_title('Towns (>= 200 segment-storms), top 25')
    fig.tight_layout(); fig.savefig(os.path.join(OUT, 'reporting_bias.png'), dpi=110); plt.close(fig)
    rows = sorted(({'town': t, 'segment_storms': int((town == t).sum()), 'mean_p_detect': round(float(pd_[town == t].mean()), 4)} for t in set(town)),
                  key=lambda r: -r['mean_p_detect'])
    json.dump(rows, open(os.path.join(OUT, 'reporting_bias_towns.json'), 'w'), indent=0)


def cmd_loso():
    D = get_cache(); storms = sorted(D); res = {}
    for t in storms:
        tr = [s for s in storms if s != t]; A = assemble(D, tr); fit = em(A); th_n = naive(A)
        o, H, R = design_new(D[t], A['stats'], tr, D)
        res[t] = dict(L1=expit(_pi_logit(fit['th'], o, H)), N0=expit(_pi_logit(th_n, o, H)), th=fit['th'], th_n=th_n, ph=fit['ph'], f=fit['f'],
                      p_detect=p_detect(fit['ph'], R, D[t]['Y']))
        print(t, 'iters', fit['iters'], 'sum pi_t', round(res[t]['L1'].sum(), 1), 'naive', round(res[t]['N0'].sum(), 1), flush=True)
    pickle.dump(res, open(os.path.join(SCR, 'loso.pkl'), 'wb'))


def rank_to_p(score, n_rule):
    """Candidate p_close: the top n_rule by score get 0.999, 0.998, ... (>= 0.5; the candidate's alert tier has the deployed rule's size),
    the rest 0.499, 0.498, ... (score_v2 ranks by p_close rounded to 3 decimals, then depth)."""
    o = np.argsort(-score, kind='stable'); p = np.zeros(len(score)); j = np.arange(len(score))
    top = j < n_rule; p[o[top]] = np.maximum(0.999 - 0.001 * j[top], 0.5); p[o[~top]] = np.maximum(0.499 - 0.001 * (j[~top] - n_rule), 0.0)
    return p


def write_run(src_dir, dst_dir, storm, p, features_csv=None):
    os.makedirs(dst_dir, exist_ok=True)
    for f in os.listdir(src_dir):
        if f.startswith('features_') or f == 'segments.geojson': continue
        if not os.path.exists(os.path.join(dst_dir, f)): os.symlink(os.path.abspath(os.path.join(src_dir, f)), os.path.join(dst_dir, f))
    rows = list(csv.DictReader(open(features_csv or os.path.join(src_dir, f'features_{storm}.csv'))))
    keep = ['segment', 'road', 'town', 'road_class', 'length_m', 'aadt', 'p_close', 'p_may_close', 'peak_depth_m', 'cx', 'cy', 'y', 'label_ids']
    with open(os.path.join(dst_dir, f'features_{storm}.csv'), 'w') as fh:
        w = csv.DictWriter(fh, keep, extrasaction='ignore'); w.writeheader()
        for r, v in zip(rows, p): r = dict(r); r['p_close'] = f'{v:.3f}'; r['p_may_close'] = f'{v:.3f}'; w.writerow(r)
    # segments.geojson is only read when features are absent; flood_meta / matches are symlinked unchanged
    open(os.path.join(dst_dir, 'segments.geojson'), 'w').write('{"type":"FeatureCollection","features":[]}')


def cmd_write_runs():
    D = get_cache(); L = pickle.load(open(os.path.join(SCR, 'loso.pkl'), 'rb'))
    for t in sorted(D):
        for c in ('L1', 'N0'):
            write_run(D[t]['run_dir'], os.path.join(SCR, 'runs', c, os.path.basename(D[t]['run_dir'])), t, rank_to_p(L[t][c], D[t]['n_rule']))
    print('written', len(D))


def score_set(dirs, out, n_jobs=2):
    """score_v2.score_run for each (dir, storm); runs in a process pool; -> catalogue-format JSON with pools."""
    from concurrent.futures import ProcessPoolExecutor
    with ProcessPoolExecutor(n_jobs) as ex: runs = list(ex.map(_score_one, dirs))
    import score_v2 as SV
    P = {r['storm']: r for r in runs}; pools = {}
    for name, st in (('heldout23', SV.HELDOUT + SV.NEW16), ('heldout7', SV.HELDOUT), ('new16', SV.NEW16), ('dev2', SV.DEV), ('d456', SV.D456)):
        sel = [P[s] for s in st if s in P and P[s]['domains']['box']['n_sites'] > 0]
        if sel: pools[name] = {dom: SV.pooled(sel, dom) for dom in ('box', 'towns')}
    res = dict(made_by='proto/latent_label.py score (score_v2.score_run, default label setting)', runs=runs, pools=pools)
    json.dump(res, open(out, 'w')); return res


def _score_one(ds):
    import score_v2 as SV
    d, s = ds; r = SV.score_run(SV.load_run(d, s)); r.update(group='latent', primary=True); return r


def headline(res, pool='heldout23'):
    P = res['pools'][pool]['box']; pt, ci = P['point'], P['ci90']
    return dict(n_sites=P['n_sites'], recall3=pt['share_0.03']['site_recall'], recall3_ci=ci['share_0.03']['site_recall'], lift3=pt['share_0.03']['lift'],
                fss300_3=pt['share_0.03']['fss300'], pr_auc_seg=pt['pr_auc_seg'], pr_auc_site=pt['pr_auc_site'],
                rule_recall=pt['rule']['site_recall'], rule_lift=pt['rule']['lift'])


def cmd_score():
    import subprocess
    D = get_cache(); out = os.path.join(SCR, 'scores'); os.makedirs(out, exist_ok=True); H = {}
    sets = dict(BASE=[(D[t]['run_dir'], t) for t in sorted(D)])
    for c in ('L1', 'N0'): sets[c] = [(os.path.join(SCR, 'runs', c, os.path.basename(D[t]['run_dir'])), t) for t in sorted(D)]
    for name, dirs in sets.items():
        f = os.path.join(out, f'{name}.json')
        if not os.path.exists(f): score_set(dirs, f)
        r = json.load(open(f)); H[name] = {p: headline(r, p) for p in ('heldout23', 'heldout7', 'new16', 'dev2')}
        H[name]['per_storm'] = {x['storm']: dict(sites=x['domains']['box']['n_sites'], hits3=float(sum(x['domains']['box']['shares']['0.03']['_hits'])))
                                for x in r['runs']}
    os.makedirs(OUT, exist_ok=True); cmp = {}
    for c in ('L1', 'N0'):
        o = os.path.join(OUT, f'compare_{c}_vs_base.json')
        subprocess.run([sys.executable, os.path.join(HERE, 'score_v2.py'), '--compare', os.path.join(out, 'BASE.json'), os.path.join(out, f'{c}.json'),
                        '--protocol', 'v2', '--k', '2', '--out', o], check=True, stdout=subprocess.DEVNULL)
        v = json.load(open(o)); cmp[c] = {k: v[k] for k in ('delta_recall', 'delta_recall_lower', 'delta_fss', 'worst_storm_change', 'lift_rule', 'checks', 'adopt')}
    H['compare'] = cmp; H['calibration'] = calibration(D)
    json.dump(H, open(os.path.join(OUT, 'results.json'), 'w'), indent=1); print(json.dumps({k: H[k] for k in ('compare', 'calibration')}, indent=1))


def calibration(D, storm='sep2023'):
    """(b) Leominster city, sep2023 (DPW complete domain): LOSO pi (fit without sep2023, so without the DPW anchor) vs observed flooded
    (any source report; DPW ~ complete).  Also the in-sample all-storm fit."""
    L = pickle.load(open(os.path.join(SCR, 'loso.pkl'), 'rb')); Ds = D[storm]; dom = np.isin(Ds['town'], COMPLETE[storm])
    y = np.nan_to_num(Ds['Y'], nan=0).max(1)[dom]; out = dict(n_segments=int(dom.sum()), observed=int(y.sum()))
    FA = pickle.load(open(os.path.join(SCR, 'fit_all.pkl'), 'rb')); k = FA['A']['storms'].index(storm); ii = FA['A']['storm_idx'] == k
    preds = dict(L1_loso=L[storm]['L1'][dom], N0_loso=L[storm]['N0'][dom], L1_insample=FA['fit']['pi'][ii][dom],
                 physics=Ds['p_close'][dom])
    for name, p in preds.items():
        e = np.argsort(-p); bins = np.array_split(e, 5)
        out[name] = dict(expected=float(p.sum()), ratio_obs_exp=float(y.sum() / max(p.sum(), 1e-9)), brier=float(((p - y) ** 2).mean()),
                         brier_skill_vs_const=float(1 - ((p - y) ** 2).mean() / (((y.mean() - y) ** 2).mean())),
                         quintiles=[dict(mean_pred=float(p[b].mean()), obs_rate=float(y[b].mean()), n=int(len(b))) for b in bins])
    return out


def cmd_d456():
    """(c) Districts 4-6: frozen all-storm L1 / N0 pi applied to the transfer runs (features from LATENT_D456_SRC); never fitted on."""
    import gzip, shutil
    import score_v2 as SV
    src = os.environ.get('LATENT_D456_SRC') or os.path.join(ROOT, 'docs', 'proto', 'transfer', 'r1')
    FA = pickle.load(open(os.path.join(SCR, 'fit_all.pkl'), 'rb')); A = FA['A']; th = FA['fit']['th']; th_n = naive(A)
    base = os.path.join(SCR, 'd456'); dirs = dict(BASE=[], L1=[], N0=[])
    for c in dirs:
        os.makedirs(os.path.join(base, c, 'r1'), exist_ok=True)
        lk = os.path.join(base, c, 'roads_osm')
        if not os.path.exists(lk): os.symlink(os.path.join(os.path.dirname(src), 'roads_osm'), lk)
    for d in sorted(glob.glob(os.path.join(src, '*_20m'))):
        s = SV.storm_of(os.path.basename(d)); gz = glob.glob(os.path.join(d, f'features_{s}.csv.gz'))
        if s not in SV.D456 or not gz: continue
        fcsv = os.path.join(SCR, 'd456_feat', f'features_{s}.csv'); os.makedirs(os.path.dirname(fcsv), exist_ok=True)
        if not os.path.exists(fcsv): shutil.copyfileobj(gzip.open(gz[0], 'rt'), open(fcsv, 'w'))
        rows = list(csv.DictReader(open(fcsv))); o, Hh = hazard(rows); Hs = (Hh - A['stats']['hm']) / A['stats']['hs']
        pc = np.array([F(r['p_close']) for r in rows]); nr = int((pc >= 0.5).sum())
        for c, p in (('BASE', pc), ('L1', rank_to_p(expit(_pi_logit(th, o, Hs)), nr)), ('N0', rank_to_p(expit(_pi_logit(th_n, o, Hs)), nr))):
            dd = os.path.join(base, c, 'r1', os.path.basename(d))
            write_run(d, dd, s, p, features_csv=fcsv) if c != 'BASE' else write_run(d, dd, s, np.round(pc, 3), features_csv=fcsv)
            dirs[c].append((dd, s))
    H = {}
    for c, ds in dirs.items():
        f = os.path.join(SCR, 'scores', f'd456_{c}.json')
        if not os.path.exists(f): score_set(ds, f)
        H[c] = json.load(open(f))
    out = {c: headline(H[c], 'd456') for c in H}
    out['paired'] = {c: paired(H['BASE'], H[c]) for c in ('L1', 'N0')}
    R = json.load(open(os.path.join(OUT, 'results.json'))); R['d456'] = out; json.dump(R, open(os.path.join(OUT, 'results.json'), 'w'), indent=1)
    print(json.dumps(out, indent=1))


def paired(B, C, boot=2000, seed=0):
    """Paired two-stage bootstrap of the pooled 3 % site-recall difference (score_v2.compare's resampling; no adoption rule: D4-6 is test-only)."""
    Bm = {r['storm']: r for r in B['runs']}; Cm = {r['storm']: r for r in C['runs']}
    st = [s for s in Bm if s in Cm and Bm[s]['domains']['box']['n_sites'] > 0]
    hb = [np.asarray(Bm[s]['domains']['box']['shares']['0.03']['_hits']) for s in st]; hc = [np.asarray(Cm[s]['domains']['box']['shares']['0.03']['_hits']) for s in st]
    N = sum(len(h) for h in hb); d0 = (sum(h.sum() for h in hc) - sum(h.sum() for h in hb)) / N; rng = np.random.default_rng(seed); dd = []
    for _ in range(boot):
        sel = rng.integers(0, len(st), len(st)); a = b = n = 0.0
        for i in sel: j = rng.integers(0, len(hb[i]), len(hb[i])); a += hc[i][j].sum(); b += hb[i][j].sum(); n += len(j)
        dd.append((a - b) / n)
    return dict(storms=len(st), sites=int(N), delta_recall3=float(d0), ci90=[float(np.percentile(dd, 5)), float(np.percentile(dd, 95))])


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'selftest'
    dict(selftest=lambda: sys.exit(0 if selftest() else 1), cache=cmd_cache, fit=cmd_fit, loso=cmd_loso, score=cmd_score,
         d456=cmd_d456, **{'write-runs': cmd_write_runs})[cmd]()
