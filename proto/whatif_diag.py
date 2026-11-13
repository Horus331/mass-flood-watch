"""Why blocked culverts close fewer roads near crossings than open ones (docs/proto/whatif/BLOCKED_V2.md): diagnostic on Turing (CPU).

    python proto/whatif_diag.py --pair r100_normal --out docs/proto/whatif/diag_r100_normal.json

For one open / blocked pair: the road segments within 60 m of a blocked crossing that close (p_close >= 0.5) in one run and not the other.
For each, along its own road cells (segments.geojson geometry, 20 m cells): peak depth in each run, whether the deepest road cell is an
edited cell (model DEM below the raw lidar by > 5 cm: notch, channel burn, breach) in each run, the edit depth, and the peak water surface
within 40 m off the road.  Tests hypothesis H1: open-run closures at crossings are water standing in the notch cut through the road (a
waterway counted as road), which the blocked run does not have.
"""
import argparse, glob, json, os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(ROOT, 'sim', 'infra'))
EDIT_TOL = 0.05


def load(name):
    import impacts as IM
    od = glob.glob(os.path.join(os.environ.get('LF_WORK', os.path.expanduser('~/scratch/lf')), f'run_*_proto_{name}', 'out'))
    if not od: raise SystemExit(f'no run dir for {name}')
    R = IM.load_run(os.path.basename(od[0].rstrip('/')), local=od[0])
    zr = np.load(os.path.join(od[0], 'z_raw.npz'))['z_raw'] if os.path.exists(os.path.join(od[0], 'z_raw.npz')) else None
    G = json.load(open(os.path.join(ROOT, 'results', name, 'segments.geojson')))
    P = {int(f['properties']['segment']): f for f in G['features']}
    return R, zr, P


def cells(f, meta):
    x0, y0, x1, y1 = meta['box']; res = meta['res_m']; out = set()
    g = f['geometry']; parts = g['coordinates'] if g['type'] == 'MultiLineString' else [g['coordinates']]
    from pyproj import Transformer
    tr = Transformer.from_crs(4326, 26986, always_xy=True)
    for line in parts:
        for (a, b), (c, d) in zip(line[:-1], line[1:]):
            (xa, ya), (xb, yb) = tr.transform(a, b), tr.transform(c, d); n = max(2, int(np.hypot(xb - xa, yb - ya) // (res / 2)) + 1)
            for t in np.linspace(0, 1, n):
                x, y = xa + t * (xb - xa), ya + t * (yb - ya)
                if x0 <= x < x1 and y0 <= y < y1: out.add((int((y1 - y) // res), int((x - x0) // res)))
    return sorted(out)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--pair', required=True); ap.add_argument('--out', required=True); a = ap.parse_args()
    from scipy.spatial import cKDTree
    from scipy.ndimage import maximum_filter
    from pyproj import Transformer
    o, b = load(f'whatif_{a.pair}_open'), load(f'whatif_{a.pair}_blocked')
    meta = o[0]['meta']; tr = Transformer.from_crs(4326, 26986, always_xy=True)
    C = json.load(open(os.path.join(ROOT, 'docs', 'site', 'data', 'whatif', 'culverts.json')))['rows']
    T = cKDTree(np.array([tr.transform(r[0], r[1]) for r in C if r[4] == 0]))
    res = meta['res_m']; k = int(40 // res)
    WS = {}
    for tag, (R, zr, P) in (('open', o), ('blocked', b)):
        H = np.nan_to_num(R['H']); Z = R['Z']; WS[tag] = maximum_filter(np.where(H >= 0.05, Z + H, -np.inf), size=2 * k + 1, mode='constant', cval=-np.inf)
    rows = []
    for sid in sorted(set(o[2]) | set(b[2])):
        fo, fb = o[2].get(sid), b[2].get(sid)
        po = (fo or {}).get('properties', {}).get('p_close', 0) or 0; pb = (fb or {}).get('properties', {}).get('p_close', 0) or 0
        if (po >= 0.5) == (pb >= 0.5): continue
        f = fo or fb; cl = cells(f, meta)
        if not cl: continue
        rr, cc = np.array(cl).T; xm = meta['box'][0] + (cc.mean() + 0.5) * res; ym = meta['box'][3] - (rr.mean() + 0.5) * res
        if T.query([xm, ym])[0] > 60: continue
        rec = dict(segment=sid, road=f['properties'].get('road'), closed_in='open' if po >= 0.5 else 'blocked', p_open=round(po, 3), p_blocked=round(pb, 3))
        for tag, (R, zr, P) in (('open', o), ('blocked', b)):
            H = np.nan_to_num(R['H'])[rr, cc]; Z = R['Z'][rr, cc]; ed = (zr[rr, cc] - Z) if zr is not None else np.zeros(len(rr))
            i = int(np.argmax(H))
            rec[tag] = dict(peak_depth_m=round(float(H[i]), 2), deepest_cell_edited=bool(ed[i] > EDIT_TOL), edit_depth_m=round(float(ed[i]), 2),
                            edited_cells=int((ed > EDIT_TOL).sum()), cells=int(len(rr)), road_z_m=round(float(Z[i]), 2),
                            wse_within_40m_m=round(float(WS[tag][rr, cc].max()), 2) if np.isfinite(WS[tag][rr, cc].max()) else None)
        rows.append(rec)
    oc = [r for r in rows if r['closed_in'] == 'open']
    S = dict(pair=a.pair, segments_changed_near_crossings=len(rows), closed_only_open=len(oc), closed_only_blocked=len(rows) - len(oc),
             open_only_deepest_cell_edited=sum(r['open']['deepest_cell_edited'] for r in oc),
             open_only_median_edit_depth_m=float(np.median([r['open']['edit_depth_m'] for r in oc])) if oc else None,
             open_only_median_depth_open_vs_blocked=[float(np.median([r['open']['peak_depth_m'] for r in oc])) if oc else None,
                                                     float(np.median([r['blocked']['peak_depth_m'] for r in oc])) if oc else None])
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    json.dump(dict(made_by='proto/whatif_diag.py', summary=S, segments=rows), open(a.out, 'w'), indent=1); print(json.dumps(S, indent=1))


if __name__ == '__main__':
    main()
