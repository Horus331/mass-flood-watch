"""Why is the modelled river flow at a gauge too low?  Two checks on a w9 run directory (z.npy, hmax.npy, meta.json):

  1. contributing area inside the box: D8 accumulation over the run's DEM (priority-flood routing, Barnes et al. 2014) at the gauge,
     against the USGS drainage area -> the share of the watershed the box can see (FREE edges, no inflow unless LF_INFLOW).
  2. closed pits as LISFLOOD-FP sees them: water moves across cell FACES only (Bates et al. 2010 x / y fluxes), so a depression whose only
     outlet is a corner step is closed.  Priority-flood fill with 4 neighbours (the solver) vs 8 neighbours (what breach_depressions
     carves by default): pit depth at each gauge and the box's dead-storage volume under each connectivity.

    python proto/diag_basin.py --run-dir <dir with z.npy> --storm aug2021 [--out basin_diag.json]
"""
import os, json, math, heapq, argparse
import numpy as np

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
N4 = ((-1, 0), (0, -1), (0, 1), (1, 0))
N8 = ((-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1))


def fill(Z, nb):
    """Priority-flood from the grid edge: filled level F, parent (downstream) of every cell, and the pop order (a topological order)."""
    ny, nx = Z.shape; F = Z.astype(np.float64).ravel().copy(); seen = np.zeros(Z.size, bool); par = np.full(Z.size, -1, np.int64); order = []
    e = np.zeros(Z.shape, bool); e[[0, -1], :] = True; e[:, [0, -1]] = True
    hq = [(F[k], int(k)) for k in np.flatnonzero(e)]; heapq.heapify(hq); seen[np.flatnonzero(e)] = True
    while hq:
        f, k = heapq.heappop(hq); order.append(k); r, c = divmod(k, nx)
        for dr, dc in nb:
            rr, cc = r + dr, c + dc
            if 0 <= rr < ny and 0 <= cc < nx:
                kk = rr * nx + cc
                if not seen[kk]: seen[kk] = True; par[kk] = k; F[kk] = max(F[kk], f); heapq.heappush(hq, (F[kk], kk))
    return F.reshape(Z.shape), par, np.array(order)


def accumulation(par, order, shape, res):
    acc = np.ones(par.size)
    for k in order[::-1]:
        p = par[k]
        if p >= 0: acc[p] += acc[k]
    return (acc * res * res / 1e6).reshape(shape)


def diagnose(run_dir, obs_path):
    from pyproj import Transformer
    meta = json.load(open(os.path.join(run_dir, 'meta.json'))); x0, y0, x1, y1 = meta['box']; res = meta['res_m']
    Z = np.load(os.path.join(run_dir, 'z.npy')).astype(np.float64); H = np.load(os.path.join(run_dir, 'hmax.npy'))
    F8, par, order = fill(Z, N8); A = accumulation(par, order, Z.shape, res); F4, _, _ = fill(Z, N4)
    D4, D8 = F4 - Z, F8 - Z; cell = res * res
    out = dict(run=meta.get('run'), box=meta['box'], res_m=res,
               dead_storage_Mm3=dict(faces_4=round(float(D4.sum() * cell / 1e6), 2), corners_8=round(float(D8.sum() * cell / 1e6), 2)),
               pit_cells_over_0_3m=dict(faces_4=int((D4 > 0.3).sum()), corners_8=int((D8 > 0.3).sum())), gauges=[])
    tg = Transformer.from_crs(4326, 26986, always_xy=True)
    for g in json.load(open(obs_path))['gauges']:
        gx, gy = tg.transform(g['lon'], g['lat'])
        if not (x0 <= gx < x1 and y0 <= gy < y1): continue
        r, c = int((y1 - gy) // res), int((gx - x0) // res); k = max(1, int(math.ceil(120 / res)))
        w = A[max(0, r - k):r + k + 1, max(0, c - k):c + k + 1]; i = np.unravel_index(int(np.argmax(w)), w.shape); rr, cc = max(0, r - k) + i[0], max(0, c - k) + i[1]
        da = (g.get('drain_mi2') or 0) * 2.58999
        out['gauges'].append(dict(site=g['site'], name=g['name'], river_cell=[int(rr), int(cc)], drain_km2_usgs=round(da, 1), in_box_km2=round(float(A[rr, cc]), 1),
                                  share_in_box=round(float(A[rr, cc]) / da, 3) if da else None, z=round(float(Z[rr, cc]), 2),
                                  pit_depth_faces_4_m=round(float(D4[rr, cc]), 2), pit_depth_corners_8_m=round(float(D8[rr, cc]), 2),
                                  spill_level_faces_4=round(float(F4[rr, cc]), 2), peak_depth_m=round(float(H[rr, cc]), 2)))
    return out


if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('--run-dir', required=True); ap.add_argument('--storm', default='sep2023'); ap.add_argument('--obs'); ap.add_argument('--out')
    a = ap.parse_args(); R = diagnose(a.run_dir, a.obs or os.path.join(ROOT, 'docs', 'proto', 'obs', f'gauges_{a.storm}.json'))
    if a.out: json.dump(R, open(a.out, 'w'), indent=1)
    print(json.dumps({k: v for k, v in R.items() if k != 'gauges'}))
    for g in R['gauges']: print(json.dumps(g))
