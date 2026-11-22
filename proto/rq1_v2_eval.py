"""Paper 2 RQ1 v2: out-of-sample test of the road-edge washout index, exactly as frozen in papers/paper2/PREREG_RQ1_V2.md
(commit 3d380b598). Written before any second damage inventory exists; nothing in the reading rule may be changed after a list is opened.

    python proto/rq1_v2_eval.py --labels new_list.csv --type_map type_map.json --depth peak_depth.csv \
        --spi papers/paper2/edge_spi_fitchburg_graph.json [...more towns] --out papers/paper2/rq1_v2_eval.json

Inputs
  --labels    CSV with columns lon, lat, type (one row per damage point; WGS84).
  --type_map  JSON {label type: "edge" | "crossing" | "other"}. Must be written and committed BEFORE matching (PREREG: "the type
              mapping of the new list is written down before matching"); its SHA-256 is recorded in the output.
  --depth     CSV with columns segment, peak_depth_m: the model run of that storm at the deployed settings. Without it the
              likelihood-ratio test cannot run and no verdict is given.
  --spi       one or more edge_spi.py outputs made with --segments graph (field spi_window_share_fixed, threshold 11,000 m2).
  --selftest  pipeline check on random points placed on segments (no real labels; nothing is read from any inventory).

Rules (frozen): unit = graph segment; outcome = >= 1 edge-type point within 30 m (nearest segment); points within 30 m of a mapped
road-stream crossing excluded (RQ3); AUC of spi_window_share_fixed with 2,000-draw bootstrap 95 % interval; LR test of its added value
over log peak depth + log AADT + log length; >= 8 damaged segments needed. Verdict: AUC >= 0.70, interval above 0.5 and LR p < 0.05
-> "confirmed out of sample"; interval above 0.5 otherwise -> "weak"; interval includes 0.5 -> "not confirmed".
"""
import argparse, csv, hashlib, json, os, sys
import numpy as np, pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, f'{ROOT}/proto'); sys.path.insert(0, f'{ROOT}/sim/infra')
from rq1_eval import auc, auc_ci, lr_test   # same statistics as the frozen v1 test

MATCH_M, CROSS_M, MIN_POS, MAIN = 30.0, 30.0, 8, 'spi_window_share_fixed'


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()[:16]


def load_segments(ids):
    import impacts as IM
    from pyproj import Transformer
    from shapely.geometry import LineString, MultiLineString
    tr = Transformer.from_crs(4326, 26986, always_xy=True).transform
    S = json.load(open(f'{ROOT}/docs/graph_segments.json')); P = S['props']; parts = {}
    for i, lo, la in IM.decode_segments(S):
        if str(i) in ids and len(lo) > 1:
            x, y = tr(np.asarray(lo), np.asarray(la)); parts.setdefault(str(i), []).append(list(zip(x, y)))
    geom = {k: (LineString(v[0]) if len(v) == 1 else MultiLineString(v)) for k, v in parts.items()}
    props = {str(i): dict(aadt=P['aadt'][i], len_m=P['len'][i], road=P['road'][i], town=P['town'][i]) for i in range(len(P['town'])) if str(i) in ids}
    return geom, props, tr


def crossings(tr):
    X = json.load(open(f'{ROOT}/docs/network/crossings_all.json')); c = X['columns']; lo, la = c.index('lon'), c.index('lat')
    xy = np.array([tr(r[lo], r[la]) for r in X['rows']])
    from scipy.spatial import cKDTree
    return cKDTree(xy)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--labels'); ap.add_argument('--type_map'); ap.add_argument('--depth'); ap.add_argument('--spi', nargs='+', required=True)
    ap.add_argument('--out', required=True); ap.add_argument('--selftest', action='store_true'); ap.add_argument('--seed', type=int, default=0)
    a = ap.parse_args()
    from shapely.geometry import Point
    from shapely.strtree import STRtree

    spi, thr = {}, set()
    for f in a.spi:
        d = json.load(open(f)); thr.add(d.get('v2_fixed_thr_m2'))
        for k, v in d['segments'].items():
            if MAIN in v: spi[str(k)] = v
    assert thr == {11000.0}, f'index files must use the frozen 11,000 m2 threshold, got {thr}'
    geom, props, tr = load_segments(set(spi))
    ids = [k for k in spi if k in geom]; tree = STRtree([geom[k] for k in ids]); xt = crossings(tr)

    if a.selftest:   # random points on random segments; type 'edge'. Checks the plumbing only.
        rng = np.random.default_rng(a.seed); pick = rng.choice(ids, 40, replace=False); rows = []
        for k in pick:
            p = geom[k].interpolate(rng.uniform(0, geom[k].length)); rows.append(dict(x=p.x, y=p.y, type='edge'))
        tmap = {'edge': 'edge'}; meta = dict(labels='SELFTEST (random points, not an inventory)', type_map=None)
    else:
        assert a.labels and a.type_map, '--labels and --type_map are required (or --selftest)'
        tmap = json.load(open(a.type_map)); rows = []
        for r in csv.DictReader(open(a.labels)):
            x, y = tr(float(r['lon']), float(r['lat'])); rows.append(dict(x=x, y=y, type=r.get('type', '')))
        unmapped = sorted({r['type'] for r in rows} - set(tmap))
        assert not unmapped, f'types missing from the frozen type map: {unmapped}'
        meta = dict(labels=a.labels, labels_sha256=sha(a.labels), type_map=a.type_map, type_map_sha256=sha(a.type_map))

    cnt = dict(points=len(rows), edge=0, at_crossing=0, not_edge=0, unmatched=0, matched=0); dmg = set()
    for r in rows:
        if tmap.get(r['type']) != 'edge': cnt['not_edge'] += 1; continue
        cnt['edge'] += 1
        if xt.query([r['x'], r['y']], distance_upper_bound=CROSS_M)[0] <= CROSS_M: cnt['at_crossing'] += 1; continue
        q = Point(r['x'], r['y']); near = [ids[i] for i in tree.query(q.buffer(MATCH_M)) if geom[ids[i]].distance(q) <= MATCH_M]
        if not near: cnt['unmatched'] += 1; continue
        cnt['matched'] += 1; dmg.add(min(near, key=lambda k: geom[k].distance(q)))

    F = pd.DataFrame(dict(segment=ids, spi=[spi[k][MAIN] for k in ids], aadt=[props[k]['aadt'] or 0 for k in ids],
                          len_m=[props[k]['len_m'] or spi[k].get('length_m') or 1 for k in ids]))
    F['damaged'] = F.segment.isin(dmg).astype(int)
    out = dict(spec='papers/paper2/PREREG_RQ1_V2.md (frozen 3d380b598)', made_by='proto/rq1_v2_eval.py', **meta,
               index_files=a.spi, segments=int(len(F)), counts=cnt, damaged_segments=int(F.damaged.sum()))
    y = F.damaged.values; s = F.spi.values
    if y.sum() < MIN_POS:
        out.update(verdict=f'descriptive only (fewer than {MIN_POS} damaged segments)')
    else:
        A = auc(y, s); ci = auc_ci(y, s); out.update(auc=round(A, 3), auc_ci95=ci)
        if a.depth:
            D = pd.read_csv(a.depth); D['segment'] = D.segment.astype(str); F = F.merge(D[['segment', 'peak_depth_m']], on='segment', how='left')
            X0 = np.column_stack([np.log(F.peak_depth_m.fillna(0).clip(0, 3) + 0.02), np.log1p(F.aadt), np.log(F.len_m.clip(lower=1))])
            X1 = np.column_stack([X0, F.spi.values]); inc = lr_test(y, X0, X1); out['incremental'] = inc
            out['depth_file'] = a.depth; out['depth_missing'] = int(F.peak_depth_m.isna().sum())
            if ci[0] <= 0.5: v = 'not confirmed'
            elif A >= 0.70 and inc['p'] < 0.05: v = 'confirmed out of sample'
            else: v = 'weak'
            out['verdict'] = v
        else:
            out['verdict'] = 'no verdict: --depth (model run of the storm) missing, LR test not run'
    if a.selftest: out['verdict'] = 'SELFTEST: ' + out['verdict']
    json.dump(out, open(a.out, 'w'), indent=1); print(json.dumps(out, indent=1))


if __name__ == '__main__':
    main()
