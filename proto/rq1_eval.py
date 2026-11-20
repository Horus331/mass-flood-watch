"""Paper 2 RQ1 evaluation, exactly as frozen in docs/proto/paper2/PREREG_RQ1.md.

    python proto/rq1_eval.py  ->  docs/proto/paper2/rq1_eval.json
"""
import csv, json, math, os
import numpy as np, pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); P = f'{ROOT}/docs/proto'
RUN = f'{P}/phase1/parametric_t2/t2_base'; NB = 2000


def auc(y, s):
    y = np.asarray(y); s = np.asarray(s, float); pos, neg = s[y == 1], s[y == 0]
    if not len(pos) or not len(neg): return None
    r = pd.Series(np.concatenate([pos, neg])).rank().values[:len(pos)]
    return float((r.sum() - len(pos) * (len(pos) + 1) / 2) / (len(pos) * len(neg)))


def auc_ci(y, s, seed=0):
    rng = np.random.default_rng(seed); y = np.asarray(y); s = np.asarray(s, float); B = []
    for _ in range(NB):
        k = rng.integers(0, len(y), len(y)); a = auc(y[k], s[k])
        if a is not None: B.append(a)
    return [round(float(np.percentile(B, 2.5)), 3), round(float(np.percentile(B, 97.5)), 3)]


def lr_test(y, X0, X1):
    from sklearn.linear_model import LogisticRegression
    from scipy.stats import chi2
    def fit(X):
        m = LogisticRegression(C=1e6, max_iter=5000).fit(X, y); p = np.clip(m.predict_proba(X)[:, 1], 1e-12, 1 - 1e-12)
        return float(np.sum(y * np.log(p) + (1 - y) * np.log(1 - p))), p
    l0, p0 = fit(X0); l1, p1 = fit(X1); stat = 2 * (l1 - l0)
    return dict(lr_stat=round(stat, 3), p=round(float(chi2.sf(max(stat, 0), X1.shape[1] - X0.shape[1])), 4),
                auc_base=round(auc(y, p0), 3), auc_with_spi=round(auc(y, p1), 3))


def block(F, ycol, scol='spi_max'):
    y = F[ycol].values.astype(int); s = F[scol].values
    a = auc(y, s)
    out = dict(n=int(len(F)), positives=int(y.sum()), auc=round(a, 3) if a is not None else None, auc_ci95=auc_ci(y, s) if a is not None else None)
    X0 = np.column_stack([np.log(F.peak_depth_m.fillna(0).clip(0, 3) + 0.02), np.log1p(F.aadt.fillna(0))])
    X1 = np.column_stack([X0, np.log1p(F[scol].clip(lower=0))])
    if y.sum() >= 2: out['incremental'] = lr_test(y, X0, X1)
    return out


def main():
    from pyproj import Transformer
    from shapely.geometry import shape, Point
    from shapely.ops import transform as stx
    from shapely.strtree import STRtree
    tr = Transformer.from_crs(4326, 26986, always_xy=True).transform
    E = json.load(open(f'{P}/paper2/edge_spi_leominster.json'))['segments']
    F = pd.read_csv(f'{RUN}/features_sep2023.csv', low_memory=False)
    F = F[F.segment.astype(str).isin(E.keys())].copy()
    for k in ('spi_max', 'spi_p90', 'edge_len_over_p95_m'): F[k] = [E[str(s)][k] for s in F.segment]
    G = {f['properties']['segment']: stx(tr, shape(f['geometry'])) for f in json.load(open(f'{RUN}/segments.geojson'))['features']
         if str(f['properties']['segment']) in E}
    ids = list(G); tree = STRtree([G[i] for i in ids]); dmg, wash = set(), set()
    for p in csv.DictReader(open(f'{ROOT}/proto/data/labels_sep2023_leominster_dpw.csv')):
        q = Point(tr(float(p['lon']), float(p['lat']))); near = [ids[i] for i in tree.query(q.buffer(30)) if G[ids[i]].distance(q) <= 30]
        if not near: continue
        b = min(near, key=lambda i: G[i].distance(q)); dmg.add(b)
        if p['type'] == 'washout': wash.add(b)
    F['damaged'] = F.segment.isin(dmg).astype(int); F['washout'] = F.segment.isin(wash).astype(int)
    wach = F.road.astype(str).str.upper().str.contains('WACHUSETT')
    out = dict(spec='docs/proto/paper2/PREREG_RQ1.md', segments=len(F), damaged=int(F.damaged.sum()), washout=int(F.washout.sum()),
               main=block(F, 'damaged'), washout_only=block(F, 'washout'),
               sens_no_wachusett=block(F[~wach], 'damaged'), sens_spi_p90=block(F, 'damaged', 'spi_p90'),
               sens_edge_len=block(F, 'damaged', 'edge_len_over_p95_m'))
    # misses: segments matched to DPW points the deployed rule did not flag, damage type washout (LEOMINSTER_MISSES.md definition)
    miss = F[(F.washout == 1) & (F.p_close < 0.5)]
    thr = F.spi_max.quantile(0.90)
    out['washout_misses'] = dict(segments=int(len(miss)), in_top10pct=int((miss.spi_max >= thr).sum()),
                                 share=round(float((miss.spi_max >= thr).mean()), 3) if len(miss) else None, chance=0.10)
    m = out['main']; inc = m.get('incremental', {}); wm = out['washout_misses']
    sig = m['auc_ci95'] and m['auc_ci95'][0] > 0.5
    if not sig: verdict = 'no signal'
    elif m['auc'] >= 0.70 and inc.get('p', 1) < 0.05 and (wm['share'] or 0) >= 0.20: verdict = 'promising'
    else: verdict = 'weak'
    out['verdict'] = verdict
    json.dump(out, open(f'{P}/paper2/rq1_eval.json', 'w'), indent=1); print(json.dumps(out, indent=1))


if __name__ == '__main__':
    main()
