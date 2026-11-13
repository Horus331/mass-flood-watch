"""Blocked culverts, version 3 (docs/proto/whatif/PREREG_BLOCKED_V3.md): the same crest-relative readout for open and blocked runs.

    python proto/whatif_v3.py --pairs r100_normal,r075_wet --out docs/proto/whatif/blocked_v3.json

CPU only; reads the kept what-if runs ($LF_WORK/run_*_proto_whatif_<pair>_{open,blocked}/out) and results/<name>/segments.geojson.
"""
import argparse, glob, json, os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(ROOT, 'sim', 'infra'))
NEAR_M, POOL_M, CREST_M, CLOSE_M, WET_M = 60.0, 40.0, 20.0, 0.30, 0.05


def load(name):
    import impacts as IM
    od = glob.glob(os.path.join(os.environ.get('LF_WORK', os.path.expanduser('~/scratch/lf')), f'run_*_proto_{name}', 'out'))
    if not od: raise FileNotFoundError(f'no run dir for {name}')
    R = IM.load_run(os.path.basename(od[0].rstrip('/')), local=od[0])
    zf = np.load(os.path.join(od[0], 'z_raw.npz'))
    ZC = (zf['z_raw_max10'] if 'z_raw_max10' in zf else zf['z_raw']).astype(np.float32)
    G = json.load(open(os.path.join(ROOT, 'results', name, 'segments.geojson')))
    return dict(H=np.nan_to_num(R['H']).astype(np.float32), Z=R['Z'].astype(np.float32), ZC=ZC, meta=R['meta'],
                seg={int(f['properties']['segment']): f for f in G['features']})


def seg_cells(f, meta, tr):
    x0, y0, x1, y1 = meta['box']; res = meta['res_m']; out = set()
    g = f['geometry']; parts = g['coordinates'] if g['type'] == 'MultiLineString' else [g['coordinates']]
    for line in parts:
        for (a, b), (c, d) in zip(line[:-1], line[1:]):
            (xa, ya), (xb, yb) = tr.transform(a, b), tr.transform(c, d); n = max(2, int(np.hypot(xb - xa, yb - ya) // (res / 2)) + 1)
            for t in np.linspace(0, 1, n):
                x, y = xa + t * (xb - xa), ya + t * (yb - ya)
                if x0 <= x < x1 and y0 <= y < y1: out.add((int((y1 - y) // res), int((x - x0) // res)))
    return np.array(sorted(out)).reshape(-1, 2)


def top2(v):
    v = np.sort(v)[::-1]; return float(v[1] if len(v) > 1 else v[0])


def one_pair(p, XY, tr):
    from scipy.spatial import cKDTree
    O, B = load(f'whatif_{p}_open'), load(f'whatif_{p}_blocked'); meta = O['meta']; res = meta['res_m']; x0, y0, x1, y1 = meta['box']
    T = cKDTree(XY); ny, nx = O['Z'].shape
    near = {}
    for sid in sorted(set(O['seg']) | set(B['seg'])):
        f = O['seg'].get(sid) or B['seg'][sid]; cl = seg_cells(f, meta, tr)
        if not len(cl): continue
        xm = x0 + (cl[:, 1].mean() + 0.5) * res; ym = y1 - (cl[:, 0].mean() + 0.5) * res
        if T.query([xm, ym])[0] <= NEAR_M: near[sid] = cl
    def depth(D, cl):
        r, c = cl.T; return top2(np.maximum(D['Z'][r, c] + D['H'][r, c] - D['ZC'][r, c], 0.0))
    closed = {t: sorted(s for s, cl in near.items() if depth(D, cl) >= CLOSE_M) for t, D in (('open', O), ('blocked', B))}
    # pool and crest at each blocked crossing inside the box (crest from the open run's lidar: the lidar is the same in both)
    yy, xx = np.mgrid[0:ny, 0:nx]; kp, kc = int(POOL_M // res), max(1, int(CREST_M // res)); pools = []
    for x, y in XY:
        if not (x0 <= x < x1 and y0 <= y < y1): continue
        r0, c0 = int((y1 - y) // res), int((x - x0) // res)
        crest = float(O['ZC'][max(0, r0 - kc):r0 + kc + 1, max(0, c0 - kc):c0 + kc + 1].max())
        sl = (slice(max(0, r0 - kp), r0 + kp + 1), slice(max(0, c0 - kp), c0 + kp + 1))
        disk = (yy[sl] - r0) ** 2 + (xx[sl] - c0) ** 2 <= kp * kp
        row = dict(x=round(float(x)), y=round(float(y)), crest_m=round(crest, 2))
        for t, D in (('open', O), ('blocked', B)):
            m = disk & (D['H'][sl] >= WET_M) & (D['Z'][sl] < crest)
            row[t] = round(float((D['Z'][sl] + D['H'][sl])[m].max()), 2) if m.any() else None
        pools.append(row)
    dif = [r['blocked'] - r['open'] for r in pools if r['open'] is not None and r['blocked'] is not None]
    wet_one = [r for r in pools if (r['open'] is None) != (r['blocked'] is None)]
    # a crossing wet in only one run counts as a rise (blocked only, +1 m) or a fall (open only, -1 m); only the median's sign is used
    dif += [1.0 if r['open'] is None else -1.0 for r in wet_one]
    ov = {t: sum(1 for r in pools if r[t] is not None and r[t] > r['crest_m']) for t in ('open', 'blocked')}
    return dict(scenario=p, segments_near=len(near), closed_open=len(closed['open']), closed_blocked=len(closed['blocked']),
                closed_both=len(set(closed['open']) & set(closed['blocked'])), crossings=len(pools), crossings_wet=len(dif),
                pool_median_blocked_minus_open_m=round(float(np.median(dif)), 3) if dif else None,
                overtopped_open=ov['open'], overtopped_blocked=ov['blocked'], closed=closed, pools=pools)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--pairs', required=True); ap.add_argument('--out', required=True); a = ap.parse_args()
    from pyproj import Transformer
    tr = Transformer.from_crs(4326, 26986, always_xy=True)
    C = json.load(open(os.path.join(ROOT, 'docs', 'site', 'data', 'whatif', 'culverts.json')))['rows']
    XY = np.array([tr.transform(r[0], r[1]) for r in C if r[4] == 0])
    rows, errs = [], {}
    for p in a.pairs.split(','):
        try: rows.append(one_pair(p, XY, tr)); r = rows[-1]; print(p, {k: r[k] for k in r if k not in ('closed', 'pools')}, flush=True)
        except Exception as e: errs[p] = repr(e)[:300]; print(p, 'failed', errs[p], flush=True)
    c1 = sum(r['closed_blocked'] >= r['closed_open'] for r in rows)
    c2 = sum((r['pool_median_blocked_minus_open_m'] or -1) >= 0 for r in rows)
    S = dict(pairs=len(rows), check1_direction=f'{c1} of {len(rows)} (need >= 9 of 12)', check2_pool=f'{c2} of {len(rows)} (need >= 9 of 12)',
             passed=bool(len(rows) == 12 and c1 >= 9 and c2 >= 9), errors=errs)
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    json.dump(dict(made_by='proto/whatif_v3.py', prereg='docs/proto/whatif/PREREG_BLOCKED_V3.md', summary=S, pairs=rows), open(a.out, 'w'), indent=1)
    print(json.dumps(S, indent=1))


if __name__ == '__main__':
    main()
