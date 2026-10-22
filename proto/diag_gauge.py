"""Why does the river at a gauge pond?  Spill-path diagnosis of a LISFLOOD-FP run's DEM around every USGS gauge in the box.

    python proto/diag_gauge.py --run-dir <w9 out dir> --out gauge_diag.json [--obs docs/proto/obs/gauges_sep2023.json]

For each gauge: priority-flood fill of the run's DEM (z.npy, after burning and breaching) from the box edges gives the level water must
reach before it can leave the box (spill level) and, by the parent pointers, the route it takes.  If the spill level at the gauge's river
cell is well above the river bed, the river is a closed pit: the highest cell on the route (the barrier) is reported with its position,
what is mapped near it (stream crossings / NBI bridges within 150 m, road names within 60 m) and the modelled depth series at the gauge
(a pit shows as a water level that never falls after the storm).  Also writes <out>_win.npz: a 4 x 4 km window of z, peak depth, last
depth, watermask and the fill level around each gauge.
"""
import os, sys, json, math, heapq, argparse
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.normpath(os.path.join(HERE, '..'))


def fill_with_parents(Z):
    """Priority-flood (Barnes et al. 2014) from the grid edge: filled level F and the parent of every cell on its spill route."""
    ny, nx = Z.shape; F = Z.astype(np.float64).ravel().copy(); seen = np.zeros(Z.size, bool); par = np.full(Z.size, -1, np.int64)
    edge = np.zeros(Z.shape, bool); edge[[0, -1], :] = True; edge[:, [0, -1]] = True
    hq = [(float(F[k]), int(k)) for k in np.flatnonzero(edge)]; heapq.heapify(hq); seen[np.flatnonzero(edge)] = True
    nb8 = ((-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1))
    while hq:
        f, k = heapq.heappop(hq); r, c = divmod(k, nx)
        for dr, dc in nb8:
            rr, cc = r + dr, c + dc
            if rr < 0 or cc < 0 or rr >= ny or cc >= nx: continue
            kk = rr * nx + cc
            if seen[kk]: continue
            seen[kk] = True; par[kk] = k; F[kk] = max(F[kk], f); heapq.heappush(hq, (F[kk], kk))
    return F.reshape(Z.shape), par


def diagnose(run_dir, obs_path, crossings_path=None, nbi_path=None, segments_path=None):
    from pyproj import Transformer
    meta = json.load(open(os.path.join(run_dir, 'meta.json'))); x0, y0, x1, y1 = meta['box']; res = meta['res_m']
    Z = np.load(os.path.join(run_dir, 'z.npy')).astype(np.float32); H = np.load(os.path.join(run_dir, 'hmax.npy')).astype(np.float32)
    WM = np.load(os.path.join(run_dir, 'watermask.npy')).astype(bool) if os.path.exists(os.path.join(run_dir, 'watermask.npy')) else np.zeros(Z.shape, bool)
    FR = np.load(os.path.join(run_dir, 'frames_cm.npz')); D = FR['depth_cm']; hrs = FR['hours']
    XQ = json.load(open(os.path.join(run_dir, 'xings.json'))) if os.path.exists(os.path.join(run_dir, 'xings.json')) else {}
    F, par = fill_with_parents(Z); ny, nx = Z.shape
    tr = Transformer.from_crs(4326, 26986, always_xy=True); inv = Transformer.from_crs(26986, 4326, always_xy=True)
    feats = []                                                 # (x, y, label) of mapped structures for naming the barrier
    if crossings_path and os.path.exists(crossings_path):
        X = json.load(open(crossings_path)); C = X['columns']; il, ia = C.index('lon'), C.index('lat')
        rows = [dict(zip(C, r)) for r in X['rows'] if r[il] is not None]
        xs, ys = tr.transform([r['lon'] for r in rows], [r['lat'] for r in rows])
        feats += [(a, b, f"crossing {r.get('id')} {r.get('road') or ''} / {r.get('stream') or ''} ({r.get('shape') or 'no size'})") for r, a, b in zip(rows, xs, ys)]
    if nbi_path and os.path.exists(nbi_path):
        NB = json.load(open(nbi_path)); c = NB['columns']; rows = [dict(zip(c, r)) for r in NB['rows']]
        xs, ys = tr.transform([r['lon'] for r in rows], [r['lat'] for r in rows])
        feats += [(a, b, 'NBI ' + ('culvert ' if r.get('culvert') else 'bridge ') + str(r.get('id')) + ' route ' + str(r.get('route'))) for r, a, b in zip(rows, xs, ys)]
    SP = None
    if segments_path and os.path.exists(segments_path):
        sys.path.insert(0, os.path.join(ROOT, 'sim', 'infra')); import impacts as IM
        S = json.load(open(segments_path)); SP = (IM.road_points(S, meta), S['props']['road'])
    out = []
    for g in json.load(open(obs_path))['gauges']:
        gx, gy = tr.transform(g['lon'], g['lat'])
        if not (x0 <= gx < x1 and y0 <= gy < y1): continue
        r, c = int((y1 - gy) // res), int((gx - x0) // res); k = max(1, int(math.ceil(60 / res)))
        sub = WM[max(0, r - k):r + k + 1, max(0, c - k):c + k + 1]
        if sub.any():
            rr_, cc_ = np.nonzero(sub); j = int(np.argmin((rr_ - (r - max(0, r - k))) ** 2 + (cc_ - (c - max(0, c - k))) ** 2))
            r, c = int(rr_[j] + max(0, r - k)), int(cc_[j] + max(0, c - k))
        path = []; p = r * nx + c
        while p >= 0 and len(path) < ny * nx: path.append(p); p = int(par[p])
        pr, pc = np.divmod(np.array(path), nx); zp = Z[pr, pc]; seg_len = np.r_[0, np.hypot(np.diff(pr), np.diff(pc))] * res
        dist = np.cumsum(seg_len); ib = int(np.argmax(zp)); bx, by = x0 + (pc[ib] + 0.5) * res, y1 - (pr[ib] + 0.5) * res
        blon, blat = inv.transform(bx, by)
        near = sorted([(math.hypot(a - bx, b - by), lab) for a, b, lab in feats if abs(a - bx) < 150 and abs(b - by) < 150])
        roads = []
        if SP is not None and len(SP[0]['x']):
            P_ = SP[0]; dd = np.hypot(P_['x'] - bx, P_['y'] - by); roads = sorted({SP[1][s] or '(unnamed)' for s in P_['seg'][dd <= 60]})
        dser = D[:, r, c].astype(float) / 100.0
        gq = [q for q in XQ.get('gauges', []) if q.get('site') == g['site']]
        prof = [dict(dist_m=round(float(dist[i])), z=round(float(zp[i]), 2), wm=bool(WM[pr[i], pc[i]]), h_last=round(float(D[-1, pr[i], pc[i]]) / 100, 2))
                for i in range(0, min(len(path), ib + 40), 3)]
        out.append(dict(site=g['site'], name=g['name'], cell=[r, c], z_bed=round(float(Z[r, c]), 2), spill_level=round(float(F[r, c]), 2),
                        pit_depth_m=round(float(F[r, c] - Z[r, c]), 2), peak_depth_m=round(float(H[r, c]), 2), last_depth_m=round(float(dser[-1]), 2),
                        peak_wse=round(float(Z[r, c] + H[r, c]), 2), last_wse=round(float(Z[r, c] + dser[-1]), 2),
                        obs_datum_m=round(g['datum_ft'] * 0.3048, 2) if g.get('datum_ft') is not None else None,
                        barrier=dict(z=round(float(zp[ib]), 2), dist_along_route_m=round(float(dist[ib])), lon=round(blon, 5), lat=round(blat, 5), cell=[int(pr[ib]), int(pc[ib])],
                                     in_watermask=bool(WM[pr[ib], pc[ib]]), near=[f'{d_:.0f} m {lab}' for d_, lab in near[:8]], roads_within_60m=roads[:8]),
                        route_len_m=round(float(dist[-1])), depth_series_m=[round(float(v), 2) for v in dser[::2]], series_hours=[float(h) for h in hrs[::2]],
                        flow=gq[0] if gq else None, route_profile=prof))
        w = int(2000 / res); sl = (slice(max(0, r - w), r + w + 1), slice(max(0, c - w), c + w + 1))
        out[-1]['_win'] = dict(z=Z[sl], hmax=H[sl], hlast=D[-1][sl].astype(np.float32) / 100, wm=WM[sl], fill=F[sl].astype(np.float32), r0=sl[0].start, c0=sl[1].start)
    return dict(run=meta.get('run'), gauges=out)


if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('--run-dir', required=True); ap.add_argument('--out', required=True)
    ap.add_argument('--obs', help='default docs/proto/obs/gauges_<storm>.json'); ap.add_argument('--storm', default=os.environ.get('STORM') or 'sep2023')
    a = ap.parse_args(); a.obs = a.obs or os.path.join(ROOT, 'docs', 'proto', 'obs', f'gauges_{a.storm}.json')
    R = diagnose(a.run_dir, a.obs, os.path.join(ROOT, 'docs', 'network', 'crossings_all.json'), os.path.join(ROOT, 'docs', 'network', 'nbi_ma.json'),
                 os.path.join(ROOT, 'docs', 'graph_segments.json'))
    W = {}
    for g in R['gauges']:
        for k, v in g.pop('_win').items(): W[f"{g['site']}_{k}"] = v
    if W: np.savez_compressed(a.out.replace('.json', '') + '_win.npz', **W)
    json.dump(R, open(a.out, 'w'), indent=1)
    for g in R['gauges']: print(json.dumps({k: v for k, v in g.items() if k not in ('route_profile', 'depth_series_m', 'series_hours')}))
