"""Paper 2: empirical fragility curve, probability of Sept 2023 DPW damage vs road-edge stream-power index (v1 spi_max), Leominster.
In-sample and descriptive (Sept 2023 is the calibration storm); v1 only (v2 is kept unseen against damage for its out-of-sample test).
Style after Anderson et al. (2017): binned empirical rates with Wilson 95 % intervals and a fitted curve (logistic in log SPI, which is the
lognormal-type CDF shape used there).
    python proto/paper2_fragility.py  ->  docs/proto/paper2/fig/fragility_spi.png, fragility_spi.json"""
import json, os, sys
import numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); sys.path.insert(0, HERE)
import rq1_eval as R
P = f'{ROOT}/docs/proto/paper2'


def wilson(k, n, z=1.96):
    if n == 0: return (np.nan, np.nan)
    p = k / n; d = 1 + z * z / n; c = (p + z * z / (2 * n)) / d; h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (c - h, c + h)


def main():
    import csv
    import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
    from sklearn.linear_model import LogisticRegression
    from pyproj import Transformer
    from shapely.geometry import shape, Point
    from shapely.ops import transform as stx
    from shapely.strtree import STRtree
    T = Transformer.from_crs(4326, 26986, always_xy=True).transform
    E = json.load(open(f'{P}/edge_spi_leominster.json'))['segments']
    F = pd.read_csv(f'{R.RUN}/features_sep2023.csv', low_memory=False); F = F[F.segment.astype(str).isin(E)].copy()
    F['spi'] = [E[str(s)]['spi_max'] for s in F.segment]
    G = {f['properties']['segment']: stx(T, shape(f['geometry'])) for f in json.load(open(f'{R.RUN}/segments.geojson'))['features'] if str(f['properties']['segment']) in E}
    ids = list(G); tree = STRtree([G[i] for i in ids]); dmg = set()
    for p in csv.DictReader(open(f'{ROOT}/proto/data/labels_sep2023_leominster_dpw.csv')):
        q = Point(T(float(p['lon']), float(p['lat']))); near = [ids[i] for i in tree.query(q.buffer(30)) if G[ids[i]].distance(q) <= 30]
        if near: dmg.add(min(near, key=lambda i: G[i].distance(q)))
    y = F.segment.isin(dmg).astype(int).values; x = np.log10(F.spi.clip(lower=1).values)
    edges = np.quantile(x, [0, .5, .75, .9, .95, 1.0]); rows = []
    for a, b in zip(edges[:-1], edges[1:]):
        m = (x >= a) & (x <= b if b == edges[-1] else x < b); k, n = int(y[m].sum()), int(m.sum()); lo, hi = wilson(k, n)
        rows.append(dict(spi_from=round(10 ** a), spi_to=round(10 ** b), segments=n, damaged=k, rate=round(k / n, 4) if n else None, ci95=[round(lo, 4), round(hi, 4)]))
    lr = LogisticRegression(C=1e6, max_iter=5000).fit(x[:, None], y); xs = np.linspace(x.min(), x.max(), 200); ps = lr.predict_proba(xs[:, None])[:, 1]
    fig, ax = plt.subplots(figsize=(6.5, 4.2))
    for r in rows:
        mid = np.log10(np.sqrt(max(r['spi_from'], 1) * r['spi_to']))
        ax.errorbar(10 ** mid, r['rate'], yerr=[[r['rate'] - r['ci95'][0]], [r['ci95'][1] - r['rate']]], fmt='o', color='#1f4e79', capsize=3)
        ax.text(10 ** mid, r['ci95'][1] + 0.01, f"{r['damaged']}/{r['segments']}", ha='center', fontsize=7, color='#444')
    ax.plot(10 ** xs, ps, color='#c0392b', lw=1.6, label='logistic fit in log SPI')
    ax.set_xscale('log'); ax.set_xlabel('Road-edge stream-power index, segment maximum (m²)'); ax.set_ylabel('Share of segments with recorded damage')
    ax.set_title('Leominster, Sept 2023 (calibration storm; in-sample, descriptive)', fontsize=9); ax.legend(fontsize=8, frameon=False)
    ax.set_ylim(0, None); fig.tight_layout(); fig.savefig(f'{P}/fig/fragility_spi.png', dpi=300)
    out = dict(made_by='proto/paper2_fragility.py', note='in-sample, calibration storm; v1 index only', segments=int(len(y)), damaged=int(y.sum()),
               bins=rows, logistic=dict(intercept=round(float(lr.intercept_[0]), 3), slope_per_log10=round(float(lr.coef_[0][0]), 3)))
    json.dump(out, open(f'{P}/fragility_spi.json', 'w'), indent=1); print(json.dumps(out, indent=1))


if __name__ == '__main__':
    main()
