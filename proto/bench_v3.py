"""Benchmark v3: the model against named baselines, by the rules of docs/proto/PROTOCOL_v3.md (committed before any of this was scored).

    python proto/bench_v3.py run --out docs/proto/scoring/benchmark_v3.json --md docs/proto/scoring/BENCHMARK_v3_tables.md
    python proto/bench_v3.py selftest

District 3 (Test 1) with the methods whose inputs exist now: M (model, clean CPU parity runs, docs/proto/parity/catalog), B1 (NWS FF.W
polygons, docs/proto/baselines/nws_ffw.json), B2 (FEMA SFHA share, docs/proto/static/static_flags.json), B3 (MassDOT repeating flood points,
proto/data/massdot_repeat_flood_d3.csv; undated, so all points for every storm).  B4/B5/B6 and Test 2 (Districts 4-6) are added as their
inputs arrive; the rules below do not change.

Per (segment, storm):
  midpoint   the segment's road point nearest the mean of its road points (score_v2 road points, EPSG:26986)
  positive   matched by a report within 30 m (score_v2 matches)
  domains    complete: Leominster in sep2023 (all other Leominster segments negative; tuning storm)
             reported: positives + segments >= 500 m from every located report and in a town with a report; the rest excluded
  flags      M p_close >= 0.5 | B1 midpoint inside any FF.W polygon valid in the storm window | B2 >= 30 % of length in the SFHA |
             B3 midpoint within 30 m of a MassDOT point
  scores     M p_close | B1 hours inside a warning (union of valid intervals) | B2 % of length in SFHA | B3 1 / max(distance, 1 m)
Probabilities: isotonic regression score -> positive, fitted on the complete domain (Leominster sep2023) only, frozen.
Site recall (box universe, sites = reports linked within 150 m): flag the top k by score, k = the model rule's count in that storm, and k = 3 %;
ties broken at random, mean over 5 seeds; chance = expected hits of k random segments.
95 % CIs: 2000 bootstrap resamples of storms, paired between methods.
"""
import argparse, datetime as dt, json, os, sys, time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
METHODS = ('M', 'B1', 'B2', 'B3')
NAMES = dict(M='Model (p_close)', B1='NWS flash-flood warning', B2='FEMA 100-yr zone (SFHA)', B3='MassDOT repeat flood points',
             B4='Radar rain threshold (I60 / storm total)', B5='Terrain only (HAND)', B6='Static HxVxC',
             H='Model + traffic (PREREG_HYBRID)')
NEG_M = 500.0; MATCH_M = 30.0; SITE_LINK_M = 150.0; SHARE3 = 0.03; SEEDS = 5; NBOOT = 2000
TUNE = 'sep2023'; DEV = ('aug2021',)
D456_ROOT = os.environ.get('D456_ROOT')    # staged copy of the transfer-d456 branch (r1 runs, roads_osm) + hybrid_d456_sfha.json


# ------------------------------------------------------------------------------------------------ per-storm arrays
def midpoints(R):
    n = len(R['seg']); pid = R['pidx']; xs = np.bincount(pid, R['px'], n); ys = np.bincount(pid, R['py'], n); c = np.maximum(np.bincount(pid, minlength=n), 1)
    mx, my = xs / c, ys / c; d = (R['px'] - mx[pid]) ** 2 + (R['py'] - my[pid]) ** 2
    o = np.lexsort((d, pid)); first = o[np.r_[0, np.nonzero(np.diff(pid[o]))[0] + 1]]
    X = mx.copy(); Y = my.copy(); X[pid[first]] = R['px'][first]; Y[pid[first]] = R['py'][first]
    return X, Y


def ffw_hours(storm, X, Y, FFW):
    from shapely.geometry import shape, Point
    from shapely.ops import transform
    from pyproj import Transformer
    S = FFW['storms'].get(storm)
    if S is None or 'error' in S: raise RuntimeError(f'no NWS polygons for {storm}')
    w0, w1 = (dt.datetime.strptime(t, '%Y-%m-%dT%H:%MZ') for t in S['window']); tr = Transformer.from_crs(4326, 26986, always_xy=True).transform
    from shapely import prepared
    ivals = [[] for _ in range(len(X))]
    for p in S['polygons']:
        g = transform(tr, shape(p['geometry']))
        if g.is_empty: continue
        b = max(dt.datetime.strptime(p['begin'], '%Y-%m-%dT%H:%MZ'), w0) if p['begin'] else w0
        e = min(dt.datetime.strptime(p['end'], '%Y-%m-%dT%H:%MZ'), w1) if p['end'] else w1
        if e <= b: continue
        x0, y0, x1, y1 = g.bounds; cand = np.nonzero((X >= x0) & (X <= x1) & (Y >= y0) & (Y <= y1))[0]
        if not len(cand): continue
        P = prepared.prep(g)
        for i in cand:
            if P.contains(Point(X[i], Y[i])): ivals[i].append((b, e))
    h = np.zeros(len(X))
    for i, L in enumerate(ivals):
        if not L: continue
        L.sort(); tot = 0.0; cb, ce = L[0]
        for b, e in L[1:]:
            if b > ce: tot += (ce - cb).total_seconds(); cb, ce = b, e
            else: ce = max(ce, e)
        h[i] = (tot + (ce - cb).total_seconds()) / 3600.0
    return h


def massdot_xy():
    import csv
    from pyproj import Transformer
    tr = Transformer.from_crs(4326, 26986, always_xy=True); P = []
    for r in csv.DictReader(open(os.path.join(HERE, 'data', 'massdot_repeat_flood_d3.csv'))):
        try: P.append(tr.transform(float(r['lon']), float(r['lat'])))
        except (TypeError, ValueError): pass
    return np.array(P)


def storm_arrays(storm, run, FFW, SF, MDP, sf_key='fema_sfha'):
    import score_v2 as S
    from scipy.spatial import cKDTree
    R = S.load_run(run, storm); n = len(R['seg']); X, Y = midpoints(R)
    y = np.zeros(n, bool)
    for v in R['matches'].values(): y[v] = True
    labs = {l['key']: l for l in R['labels']}
    loc = np.array([[l['x'], l['y']] for l in R['labels'] if l['coord'] != 'town']).reshape(-1, 2)
    if len(loc):
        dpt, _ = cKDTree(loc).query(np.column_stack([R['px'], R['py']])); dmin = np.full(n, np.inf); np.minimum.at(dmin, R['pidx'], dpt)
    else: dmin = np.full(n, np.inf)
    rtowns = {R['town'][i] for i in np.nonzero(y)[0]} | {l.get('town', '') for l in R['labels'] if l.get('town')}
    in_town = np.isin(R['town'], [t for t in rtowns if t])
    rep = y | ((dmin >= NEG_M) & in_town)
    comp = (R['town'] == 'Leominster') if storm == TUNE else np.zeros(n, bool)
    mk = [k for k, v in R['matches'].items() if k in labs]
    cl = S.link_clusters(np.array([[labs[k]['x'], labs[k]['y']] for k in mk]).reshape(-1, 2), SITE_LINK_M)
    sites = [sorted({s for i in np.nonzero(cl == c)[0] for s in R['matches'][mk[i]]}) for c in (np.unique(cl) if len(cl) else [])]
    sf = SF['categories'].get(sf_key, {}); b2 = np.array([float(sf.get(str(int(s)), 0.0)) for s in R['seg']])
    dmd = cKDTree(MDP).query(np.column_stack([X, Y]))[0] if MDP is not None and len(MDP) else np.full(n, np.inf)
    b1 = ffw_hours(storm, X, Y, FFW)
    fx = features(run, storm, R['seg'])
    score = dict(M=R['p'].astype(float), B1=b1, B2=b2); flag = dict(M=R['p'] >= 0.5, B1=b1 > 0, B2=b2 >= 30.0)
    if MDP is not None: score['B3'] = 1.0 / np.maximum(dmd, 1.0); flag['B3'] = dmd <= MATCH_M
    return dict(storm=storm, n=n, y=y, rep=rep, comp=comp, sites=sites, score=score, flag=flag, run=R['run'], fx=fx, sfha=b2)


def features(run, storm, seg):
    """Per-segment fields of the run's features csv (plain or .gz), aligned to seg: i60, total, hand, vuln, aadt (amendment 1)."""
    import csv, gzip
    p = os.path.join(run, f'features_{storm}.csv'); fh = open(p) if os.path.exists(p) else gzip.open(p + '.gz', 'rt')
    V = dict(arterial=0.7, highway=0.4); D = {}
    for r in csv.DictReader(fh):
        g = lambda k, d=0.0: float(r[k]) if r.get(k) not in (None, '') else d
        D[int(r['segment'])] = (g('peak1h_mm'), g('storm_total_mm'), g('hand_m', 20.0), V.get(r.get('road_class', ''), 1.0), g('aadt'))
    M = np.array([D.get(int(s), (0.0, 0.0, 20.0, 1.0, 0.0)) for s in seg], float)
    return dict(i60=M[:, 0], total=M[:, 1], hand=M[:, 2], vuln=M[:, 3], aadt=M[:, 4])


def csi(f, y):
    tp = (f & y).sum(); return tp / max(1, tp + (f & ~y).sum() + (~f & y).sum())


def tune_b4_b5(T):
    """Grid search on the complete domain (amendment 1); ties -> the larger threshold."""
    c = T['comp']; y = T['y'][c]; F = {k: v[c] for k, v in T['fx'].items()}; best = (-1, None, None)
    for t60 in [None] + list(range(5, 101, 5)):
        for tt in [None] + list(range(20, 301, 10)):
            if t60 is None and tt is None: continue
            f = np.zeros(len(y), bool)
            if t60: f |= F['i60'] >= t60
            if tt: f |= F['total'] >= tt
            v = csi(f, y)
            if v > best[0] + 1e-12 or (abs(v - best[0]) <= 1e-12 and ((t60 or 1e9) + (tt or 1e9)) > ((best[1] or 1e9) + (best[2] or 1e9))): best = (v, t60, tt)
    hb = (-1, None)
    for h in np.arange(0, 5.0001, 0.25):
        v = csi(F['hand'] <= h, y)
        if v > hb[0] + 1e-12: hb = (v, float(h))
    return dict(T60=best[1], Ttot=best[2], csi_b4=float(best[0]), Hstar=hb[1], csi_b5=float(hb[0]))


def add_b456(A, TU):
    fx = A['fx']; T60, Tt, H = TU['T60'], TU['Ttot'], TU['Hstar']; r = []
    f4 = np.zeros(A['n'], bool)
    if T60: f4 |= fx['i60'] >= T60; r.append(fx['i60'] / T60)
    if Tt: f4 |= fx['total'] >= Tt; r.append(fx['total'] / Tt)
    A['score']['B4'] = np.max(r, axis=0); A['flag']['B4'] = f4
    A['score']['B5'] = -fx['hand']; A['flag']['B5'] = fx['hand'] <= H
    s6 = (A['sfha'] / 100.0 + (fx['hand'] <= H)) * fx['vuln'] * np.log10(1 + fx['aadt']); A['score']['B6'] = s6
    k = max(1, int(round(SHARE3 * A['n']))); o = np.lexsort((np.random.default_rng(0).random(A['n']), -s6)); f6 = np.zeros(A['n'], bool); f6[o[:k]] = True
    A['flag']['B6'] = f6


# ------------------------------------------------------------------------------------------------ metrics
def iso_fit(s, y):
    from sklearn.isotonic import IsotonicRegression
    m = IsotonicRegression(out_of_bounds='clip', y_min=0.0, y_max=1.0).fit(s, y.astype(float)); return m


def site_recall(A, m, k, seeds=SEEDS):
    if not A['sites']: return 0.0, 0.0, 0
    sc = A['score'][m]; n = A['n']; hits = 0.0
    for s in range(seeds):
        o = np.lexsort((np.random.default_rng(s).random(n), -sc)); fl = np.zeros(n, bool); fl[o[:k]] = True
        hits += sum(bool(fl[g].any()) for g in A['sites'])
    import score_v2 as S
    ch = float(S.chance_hit(n, k, [len(g) for g in A['sites']]).sum())
    return hits / seeds, ch, len(A['sites'])


def per_storm_stats(A, P, ms=METHODS):
    """Counts and sums per method for one storm (all additive, so the storm bootstrap resamples them)."""
    out = {}; d = A['rep']; y = A['y'][d]; kr = int(A['flag']['M'].sum()); k3 = max(1, int(round(SHARE3 * A['n'])))
    for m in ms:
        f = A['flag'][m][d]; p = P[m][d]
        h_r, c_r, ns = site_recall(A, m, kr) if kr else (0.0, 0.0, len(A['sites'])); h_3, c_3, _ = site_recall(A, m, k3)
        out[m] = dict(tp=int((f & y).sum()), fp=int((f & ~y).sum()), fn=int((~f & y).sum()), nflag_box=int(A['flag'][m].sum()),
                      brier=float(((p - y) ** 2).sum()), sites=ns, hit_rule_share=h_r, chance_rule_share=c_r, hit_3=h_3, chance_3=c_3)
    out['_'] = dict(n_box=A['n'], n_rep=int(d.sum()), pos=int(y.sum()), k_rule=kr, k3=k3)
    return out


def pooled(ST, storms, P_all, A_all, clim, ms=METHODS):
    T = {m: {k: sum(ST[s][m][k] for s in storms) for k in ST[storms[0]][m]} for m in ms}
    nb = sum(ST[s]['_']['n_box'] for s in storms); nr = sum(ST[s]['_']['n_rep'] for s in storms); pos = sum(ST[s]['_']['pos'] for s in storms)
    yy = np.concatenate([A_all[s]['y'][A_all[s]['rep']] for s in storms]); bclim = float(((clim - yy) ** 2).sum())
    out = dict(storms=len(storms), segments_box=nb, segments_reported_domain=nr, positives=pos, climatology_p=clim, methods={})
    from sklearn.metrics import average_precision_score, roc_auc_score
    for m in ms:
        t = T[m]; tp, fp, fn = t['tp'], t['fp'], t['fn']
        pp = np.concatenate([P_all[s][m][A_all[s]['rep']] for s in storms]); ss = np.concatenate([A_all[s]['score'][m][A_all[s]['rep']] for s in storms])
        out['methods'][m] = dict(name=NAMES[m], POD=tp / max(1, tp + fn), FAR=fp / max(1, tp + fp) if tp + fp else None, CSI=tp / max(1, tp + fp + fn),
                                 tp=tp, fp=fp, fn=fn, flagged_share_box=t['nflag_box'] / nb, Brier=t['brier'] / max(1, nr),
                                 BSS_vs_climatology=1 - t['brier'] / bclim if bclim else None,
                                 PR_AUC=float(average_precision_score(yy, ss)) if yy.any() else None,
                                 ROC_AUC=float(roc_auc_score(yy, ss)) if yy.any() and (~yy).any() else None,
                                 site_recall_rule_share=t['hit_rule_share'] / max(1, t['sites']), chance_rule_share=t['chance_rule_share'] / max(1, t['sites']),
                                 site_recall_3pct=t['hit_3'] / max(1, t['sites']), chance_3pct=t['chance_3'] / max(1, t['sites']), sites=t['sites'],
                                 reliability=reliability(pp, yy))
    for m in ms[1:]:
        out['methods']['M'].setdefault('BSS_vs', {})[m] = 1 - T['M']['brier'] / T[m]['brier'] if T[m]['brier'] else None
    return out


def reliability(p, y, bins=10):
    e = np.linspace(0, 1, bins + 1); b = np.clip(np.digitize(p, e[1:-1]), 0, bins - 1); R = []
    for i in range(bins):
        k = b == i
        if k.any(): R.append(dict(bin=[float(e[i]), float(e[i + 1])], n=int(k.sum()), mean_p=float(p[k].mean()), obs=float(y[k].mean())))
    return R


def boot(ST, storms, A_all, P_all, nboot=NBOOT, seed=0, ms=METHODS):
    """Paired storm bootstrap of model minus baseline: CSI, Brier (lower is better: baseline - model), PR-AUC, site recall at the rule share and 3 %."""
    from sklearn.metrics import average_precision_score
    rng = np.random.default_rng(seed); S = list(storms); D = {m: {k: [] for k in ('CSI', 'Brier', 'PR_AUC', 'recall_rule_share', 'recall_3pct')} for m in ms[1:]}
    Y = {s: A_all[s]['y'][A_all[s]['rep']] for s in S}; SC = {s: {m: A_all[s]['score'][m][A_all[s]['rep']] for m in ms} for s in S}

    def stat(sel, m):
        t = {k: sum(ST[s][m][k] for s in sel) for k in ('tp', 'fp', 'fn', 'brier', 'hit_rule_share', 'hit_3', 'sites')}
        nr = sum(ST[s]['_']['n_rep'] for s in sel)
        return dict(CSI=t['tp'] / max(1, t['tp'] + t['fp'] + t['fn']), Brier=t['brier'] / max(1, nr),
                    rr=t['hit_rule_share'] / max(1, t['sites']), r3=t['hit_3'] / max(1, t['sites']))
    for _ in range(nboot):
        sel = [S[i] for i in rng.integers(0, len(S), len(S))]; yy = np.concatenate([Y[s] for s in sel])
        sm = stat(sel, 'M'); apm = average_precision_score(yy, np.concatenate([SC[s]['M'] for s in sel])) if yy.any() else np.nan
        for m in ms[1:]:
            sb = stat(sel, m); apb = average_precision_score(yy, np.concatenate([SC[s][m] for s in sel])) if yy.any() else np.nan
            D[m]['CSI'].append(sm['CSI'] - sb['CSI']); D[m]['Brier'].append(sb['Brier'] - sm['Brier']); D[m]['PR_AUC'].append(apm - apb)
            D[m]['recall_rule_share'].append(sm['rr'] - sb['rr']); D[m]['recall_3pct'].append(sm['r3'] - sb['r3'])
    out = {}
    for m, K in D.items():
        out[m] = {}
        for k, v in K.items():
            v = np.array(v, float); v = v[np.isfinite(v)]; lo, hi = np.percentile(v, [2.5, 97.5])
            out[m][k] = dict(ci95=[float(lo), float(hi)], significant=bool(lo > 0 or hi < 0), model_better=bool(lo > 0))
    return out


# ------------------------------------------------------------------------------------------------ run
def run(out, md):
    import score_v2 as S
    FFW = json.load(open(os.path.join(ROOT, 'docs', 'proto', 'baselines', 'nws_ffw.json')))
    SF = json.load(open(os.path.join(ROOT, 'docs', 'proto', 'static', 'static_flags.json'))); MDP = massdot_xy()
    runs = {s: p for p, s, grp, prim in S.find_runs() if grp == 'parity' and prim}
    test1 = [s for s in S.HELDOUT + S.NEW16 if s in runs and s not in S.LOCKED]
    assert len(test1) == 23 and TUNE in runs, (len(test1), sorted(runs))
    A_all = {}

    def show(s):
        A = A_all[s]; print(f"{s:9s} seg {A['n']:6d} rep {A['rep'].sum():6d} pos {A['y'].sum():4d} sites {len(A['sites']):3d} "
                            + ' '.join(f"{m}:{A['flag'][m].sum()}" for m in A['flag']) + f" ({time.time() - t:.0f} s)", flush=True)
    for s in [TUNE] + list(DEV) + test1:
        t = time.time(); A_all[s] = storm_arrays(s, runs[s], FFW, SF, MDP); show(s)
    # Test 2: Districts 4-6, frozen r1 transfer runs (work branch transfer-d456, staged under D456_ROOT), SFHA from hybrid_d456_sfha.json.
    # MassDOT's repeat-flood list covers District 3 only, so B3 is not available there.
    test2 = []
    if D456_ROOT:
        import hybrid_d456 as HD
        HD.read_gz_features(S); SF2 = json.load(open(os.path.join(D456_ROOT, 'hybrid_d456_sfha.json')))
        for e in HD.events():
            if e['id'] in S.LOCKED: continue
            rd = os.path.join(D456_ROOT, 'docs', 'proto', 'transfer', 'r1', e['name'])
            if not os.path.isdir(rd): print('missing run', e['name']); continue
            t = time.time(); A_all[e['id']] = storm_arrays(e['id'], rd, FFW, SF2, None, sf_key=f"sfha|{e['id']}"); test2.append(e['id']); show(e['id'])
        assert len(test2) == 81, len(test2)
    # tuning: B4/B5 thresholds, then isotonic maps, on the complete domain (Leominster sep2023), frozen
    TU = tune_b4_b5(A_all[TUNE]); print('tuned on', TUNE, TU, flush=True)
    for A in A_all.values(): add_b456(A, TU)
    # hybrid H (PREREG_HYBRID.md): logistic on the complete domain, inputs p_close and log10(1 + AADT), frozen; flag = top 3 % per storm
    from sklearn.linear_model import LogisticRegression
    hx = lambda A: np.column_stack([A['score']['M'], np.log10(1 + A['fx']['aadt'])])
    T = A_all[TUNE]; c = T['comp']; HY = LogisticRegression(C=1e6, max_iter=2000).fit(hx(T)[c], T['y'][c])
    print('hybrid coef', HY.coef_.tolist(), HY.intercept_.tolist(), flush=True)
    for A in A_all.values():
        h = HY.predict_proba(hx(A))[:, 1]; A['score']['H'] = h; k = max(1, int(round(SHARE3 * A['n'])))
        o = np.lexsort((np.random.default_rng(0).random(A['n']), -h)); f = np.zeros(A['n'], bool); f[o[:k]] = True; A['flag']['H'] = f
    TU['hybrid'] = dict(coef=HY.coef_.tolist(), intercept=HY.intercept_.tolist(), inputs=['p_close', 'log10(1+AADT)'])
    ISO = {m: iso_fit(T['score'][m][c], T['y'][c]) for m in T['score']}; clim = float(T['y'][c].mean())
    P_all = {s: {m: ISO[m].predict(A['score'][m]) for m in A['score']} for s, A in A_all.items()}
    ST = {s: per_storm_stats(A, P_all[s], tuple(A['score'])) for s, A in A_all.items()}
    res = dict(made_by='proto/bench_v3.py', protocol='docs/proto/PROTOCOL_v3.md', made=dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%dT%H:%MZ'),
               methods=NAMES, not_available=dict(B3_test2='MassDOT repeat-flood list covers District 3 only'),
               tuning=dict(storm=TUNE, domain='complete (Leominster DPW)', climatology_p=clim,
                           thresholds=TU, complete_domain={m: complete_metrics(T, P_all[TUNE], m) for m in T['score']}),
               sets={}, per_storm={s: ST[s] for s in ST})
    ALL = METHODS + ('B4', 'B5', 'B6', 'H')
    sets = [('test1_d3_heldout23', test1, ALL), ('dev_aug2021', list(DEV), ALL), ('tuning_sep2023_reported_domain', [TUNE], ALL)]
    if test2: sets.insert(1, ('test2_d456_81', test2, ('M', 'B1', 'B2', 'B4', 'B5', 'B6', 'H')))
    for name, storms, ms in sets:
        res['sets'][name] = pooled(ST, storms, P_all, A_all, clim, ms)
        if name.startswith('test'): res['sets'][name]['model_minus_baseline'] = boot(ST, storms, A_all, P_all, ms=ms)
    json.dump(res, open(out, 'w'), indent=1); open(md, 'w').write(tables(res)); print(tables(res))


def complete_metrics(A, P, m):
    c = A['comp']; y = A['y'][c]; f = A['flag'][m][c]; tp, fp, fn = int((f & y).sum()), int((f & ~y).sum()), int((~f & y).sum())
    return dict(POD=tp / max(1, tp + fn), FAR=fp / max(1, tp + fp) if tp + fp else None, CSI=tp / max(1, tp + fp + fn), tp=tp, fp=fp, fn=fn,
                Brier=float(((P[m][c] - y) ** 2).mean()))


def f(x, nd=3): return '–' if x is None else f'{x:.{nd}f}'


def tables(res):
    L = ['# Benchmark v3 tables (generated by proto/bench_v3.py; rules: docs/proto/PROTOCOL_v3.md)', '']
    for name, Sx in res['sets'].items():
        L += [f"## {name}: {Sx['storms']} storms, {Sx['segments_reported_domain']} segments in the reported domain ({Sx['positives']} reported), "
              f"{Sx['segments_box']} in the boxes", '',
              '| method | POD | FAR | CSI | flagged share | Brier | BSS vs climatology | PR-AUC | ROC-AUC | site recall at model share (chance) | site recall at 3 % (chance) |',
              '|---|---|---|---|---|---|---|---|---|---|---|']
        for m, r in Sx['methods'].items():
            L.append(f"| {m} {r['name']} | {f(r['POD'])} | {f(r['FAR'])} | {f(r['CSI'])} | {f(r['flagged_share_box'] * 100, 1)} % | {f(r['Brier'], 4)} | "
                     f"{f(r['BSS_vs_climatology'])} | {f(r['PR_AUC'])} | {f(r['ROC_AUC'])} | {f(r['site_recall_rule_share'])} ({f(r['chance_rule_share'])}) | "
                     f"{f(r['site_recall_3pct'])} ({f(r['chance_3pct'])}) |")
        if 'model_minus_baseline' in Sx:
            L += ['', 'Model minus baseline, 95 % CI over storms (Brier: baseline minus model, so > 0 = model better):', '',
                  '| vs | CSI | Brier | PR-AUC | site recall at model share | site recall at 3 % |', '|---|---|---|---|---|---|']
            for m, K in Sx['model_minus_baseline'].items():
                c = lambda k: f"[{K[k]['ci95'][0]:+.3f}, {K[k]['ci95'][1]:+.3f}]" + (' *' if K[k]['significant'] else '')
                L.append(f"| {m} | {c('CSI')} | {c('Brier')} | {c('PR_AUC')} | {c('recall_rule_share')} | {c('recall_3pct')} |")
            L += ['', '\\* = the 95 % interval excludes 0.']
        L.append('')
    return '\n'.join(L)


def selftest():
    y = np.array([1, 0, 0, 1, 0], bool); m = iso_fit(np.array([0.9, 0.1, 0.2, 0.8, 0.3]), y); assert m.predict([0.95])[0] == 1.0
    rl = reliability(np.array([0.05, 0.95]), np.array([0, 1])); assert rl[0]['obs'] == 0 and rl[-1]['obs'] == 1
    A = dict(n=10, sites=[[0], [5]], score=dict(M=np.r_[1.0, np.zeros(9)])); h, c, n = site_recall(A, 'M', 1); assert h == 1 and n == 2
    print('bench_v3 selftest ok')


if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('cmd'); ap.add_argument('--out', default='docs/proto/scoring/benchmark_v3.json')
    ap.add_argument('--md', default='docs/proto/scoring/BENCHMARK_v3_tables.md'); a = ap.parse_args()
    selftest() if a.cmd == 'selftest' else run(a.out, a.md)
