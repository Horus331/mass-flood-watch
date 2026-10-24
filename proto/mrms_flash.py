"""MRMS FLASH flash-flood products as per-segment storm-max features (opt-in input for the learned closure model; DATA_IDEAS.md item 9 / 27).

    python proto/mrms_flash.py extract --storm jul2023c      # (Actions: .github/workflows/mrms_flash.yml) -> docs/proto/ml/flash/flash_<storm>.csv
    python proto/mrms_flash.py coverage                      # which catalogue storms have a flash_<storm>.csv, and their value ranges

Products (NOAA MRMS, AWS s3://noaa-mrms-pds/CONUS/<product>/<YYYYMMDD>/, 0.01 deg; archive check in docs/proto/obs/round2/mrms_flash_check.json):
  flash_qmax_unit    FLASH_CREST_MAXUNITSTREAMFLOW_00.00   CREST max unit streamflow, m3 s-1 km-2 (10-min issues)
  qpe_ffg_ratio_max  FLASH_QPE_FFGMAX_00.00                max QPE / flash-flood-guidance ratio over 1/3/6 h (2-min issues)
  qpe_ari_max_yr     FLASH_QPE_ARIMAX_00.00                max QPE average recurrence interval over 30 min-24 h, years (2-min issues)
Each feature = max over the storm window (catalogue t0 .. t0 + hours, files sampled every 30 min) of the 3 x 3-cell (~1 km) neighbourhood
max at the segment's road vertices (docs/graph_segments.json).  Missing / negative = 0.  The ~1 km neighbourhood stands in for "the upstream
crossing" (the CREST grid is already basin-routed).  Pre-14-Oct-2020 storms are not on AWS (the IEM mtarchive has a FLASH folder from
2019, not read here).

Opt-in: closure_v2.load_storm attaches `flash` (dict of arrays aligned to the storm's segments) only when PROTO_FLASH=1.  No model uses it
by default; adding it to a candidate is a pre-registered change (PROTOCOL.md v2).
"""
import os, sys, re, csv, json, gzip, argparse, tempfile, datetime as dt
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, 'docs', 'proto', 'ml', 'flash')
PRODUCTS = {'flash_qmax_unit': 'FLASH_CREST_MAXUNITSTREAMFLOW_00.00', 'qpe_ffg_ratio_max': 'FLASH_QPE_FFGMAX_00.00', 'qpe_ari_max_yr': 'FLASH_QPE_ARIMAX_00.00'}
FLASH_FEATS = list(PRODUCTS)
SIGN = dict(flash_qmax_unit=1, qpe_ffg_ratio_max=1, qpe_ari_max_yr=1)
LOCKED = ('aug2015', 'aug2018', 'aug2020', 'jul2018', 'oct2016')
S3 = 'https://noaa-mrms-pds.s3.amazonaws.com'


def seg_vertices(box):
    """(segment id per vertex, lon, lat) for graph segments with a vertex inside box (EPSG:26986)."""
    from pyproj import Transformer
    sys.path.insert(0, HERE); import labels_expand as LE
    G = json.load(open(os.path.join(ROOT, 'docs', 'graph_segments.json'))); T = Transformer.from_crs(4326, 26986, always_xy=True)
    S, LO, LA = [], [], []
    for i, g in enumerate(G['geo']):
        P = [p for part in LE._decode(g) for p in part]
        if not P: continue
        lo = np.array([p[0] for p in P]); la = np.array([p[1] for p in P]); x, y = T.transform(lo, la)
        k = (x >= box[0]) & (x < box[2]) & (y >= box[1]) & (y < box[3])
        if k.any(): S += [i] * int(k.sum()); LO += lo[k].tolist(); LA += la[k].tolist()
    return np.array(S), np.array(LO), np.array(LA)


def listing(prefix):
    import requests, xml.etree.ElementTree as ET
    out, tok = [], None
    while True:
        p = {'list-type': '2', 'prefix': prefix}
        if tok: p['continuation-token'] = tok
        r = requests.get(S3 + '/', params=p, timeout=120); r.raise_for_status(); X = ET.fromstring(r.content); ns = {'s': X.tag.split('}')[0].strip('{')}
        out += [c.find('s:Key', ns).text for c in X.findall('s:Contents', ns)]
        t = X.find('s:NextContinuationToken', ns)
        if t is None: return out
        tok = t.text


def files_for(prod, t0, t1, step_min=30):
    """AWS keys of `prod` nearest each step in [t0, t1] (one per step, within 6 min)."""
    keys = {}
    d = t0.date()
    while d <= t1.date():
        for k in listing(f'CONUS/{prod}/{d:%Y%m%d}/'):
            m = re.search(r'_(\d{8}-\d{6})\.grib2', k)
            if m: keys[dt.datetime.strptime(m.group(1), '%Y%m%d-%H%M%S')] = f'{S3}/{k}'
        d += dt.timedelta(days=1)
    if not keys: return []
    T = np.array(sorted(keys)); out = []; t = t0
    while t <= t1:
        j = int(np.argmin([abs((x - t).total_seconds()) for x in T]))
        if abs((T[j] - t).total_seconds()) <= 360 and keys[T[j]] not in out: out.append(keys[T[j]])
        t += dt.timedelta(minutes=step_min)
    return out


_GRID = {}


def sample_max(url, lon, lat, gp):
    import requests, pygrib
    from scipy.ndimage import maximum_filter
    raw = requests.get(url, timeout=180).content; open(gp, 'wb').write(gzip.decompress(raw))
    g = pygrib.open(gp); m = g[1]; v = np.ma.filled(m.values, 0).astype(np.float32)
    if v.shape not in _GRID: la, lo = m.latlons(); _GRID[v.shape] = (la[:, 0].copy(), np.where(lo[0, :] > 180, lo[0, :] - 360, lo[0, :]))
    g.close(); v[v < 0] = 0; lat1, lon1 = _GRID[v.shape]
    if lat1[0] < lat1[-1]: lat1 = lat1[::-1]; v = v[::-1]
    i0 = max(np.searchsorted(-lat1, -lat.max() - 0.05), 0); i1 = np.searchsorted(-lat1, -lat.min() + 0.05) + 1
    j0 = max(np.searchsorted(lon1, lon.min() - 0.05), 0); j1 = np.searchsorted(lon1, lon.max() + 0.05) + 1
    sub = maximum_filter(v[i0:i1, j0:j1], size=3, mode='nearest')
    ii = np.clip(np.rint((lat1[i0] - lat) / abs(lat1[1] - lat1[0])).astype(int), 0, sub.shape[0] - 1)
    jj = np.clip(np.rint((lon - lon1[j0]) / abs(lon1[1] - lon1[0])).astype(int), 0, sub.shape[1] - 1)
    return sub[ii, jj]


def extract(storm):
    assert storm not in LOCKED, 'locked storm (PROTOCOL.md §2)'
    e = next(x for x in json.load(open(os.path.join(ROOT, 'docs', 'proto', 'obs', 'catalog.json')))['events'] if x['id'] == storm)
    t0 = dt.datetime.strptime(e['t0'], '%Y-%m-%dT%H:00Z'); t1 = t0 + dt.timedelta(hours=int(e['hours']))
    seg, lon, lat = seg_vertices(e['box_26986']); useg, inv = np.unique(seg, return_inverse=True)
    gp = os.path.join(tempfile.mkdtemp(), 'f.grib2'); feats = {}; cov = dict(storm=storm, t0=e['t0'], hours=e['hours'], segments=int(len(useg)), products={})
    for name, prod in PRODUCTS.items():
        F = files_for(prod, t0, t1); acc = np.zeros(len(lon), np.float32); n = 0
        for u in F:
            try: acc = np.maximum(acc, sample_max(u, lon, lat, gp)); n += 1
            except Exception as ex: print('  skip', u, repr(ex)[:120])
        per = np.zeros(len(useg), np.float32); np.maximum.at(per, inv, acc)
        feats[name] = per; cov['products'][name] = dict(product=prod, files=n, expected=int(int(e['hours']) * 2 + 1), max=float(per.max()) if n else None,
                                                        p95=float(np.percentile(per, 95)) if n else None)
        print(storm, name, n, 'files', cov['products'][name])
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, f'flash_{storm}.csv'), 'w', newline='') as f:
        w = csv.writer(f); w.writerow(['segment'] + FLASH_FEATS)
        for k, s in enumerate(useg): w.writerow([int(s)] + [f'{feats[n][k]:.3f}' if cov['products'][n]['files'] else '' for n in FLASH_FEATS])
    json.dump(cov, open(os.path.join(OUT, f'flash_{storm}.json'), 'w'), indent=1)


def load(storm, seg):
    """dict feature -> array aligned to `seg` (NaN where the segment or the product is missing); None when no file."""
    p = os.path.join(OUT, f'flash_{storm}.csv')
    if not os.path.exists(p): return None
    R = {int(r['segment']): r for r in csv.DictReader(open(p))}
    return {n: np.array([float(R[s][n]) if s in R and R[s][n] != '' else np.nan for s in seg]) for n in FLASH_FEATS}


def coverage():
    C = [x for x in json.load(open(os.path.join(ROOT, 'docs', 'proto', 'obs', 'catalog.json')))['events'] if x['id'] not in LOCKED]
    for e in C:
        p = os.path.join(OUT, f"flash_{e['id']}.json")
        if os.path.exists(p):
            J = json.load(open(p)); print(e['id'], e['era'], {n: (v['files'], v['expected'], v['max']) for n, v in J['products'].items()})
        else: print(e['id'], e['era'], 'none')


if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('cmd', choices=['extract', 'coverage']); ap.add_argument('--storm'); a = ap.parse_args()
    extract(a.storm) if a.cmd == 'extract' else coverage()
