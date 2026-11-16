"""Items 2-4 of docs/proto/phase1/PARAMETRIC_T2_PREREG.md (item 1 is `PM_SET=t2 python proto/parametric_eval.py`).

    PM_SET=t2 python proto/parametric_eval.py && python proto/parametric_t2_eval.py

Reads docs/proto/phase1/parametric_t2/<id>/ (segments.geojson, hmax_cm.npz, zz_cm.npz, flood_meta.json) and adds to parametric_t2.json:
notch_check (segments closed in the base but not at 100 % blockage, near a crossing or not), crest (the whatif_v3 readout per blocked run),
priority_overlap (T2 top 10 vs the pre-T2 top 10) and the reading rules' verdicts.
"""
import json, os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); sys.path.insert(0, HERE)
import whatif_v3 as W
import parametric_eval as PE

PH = f'{ROOT}/docs/proto/phase1'; RUNS = f'{PH}/parametric_t2'; OUT = f'{PH}/parametric_t2.json'
BLOCKED = ['t2_c20', 't2_c50', 't2_c100', 't2_ct']


def grids(i):
    d = f'{RUNS}/{i}'; R = PE.load_run(d)
    h = np.load(f'{d}/hmax_cm.npz')['hmax_cm'].astype(np.float32) / 100; zz = np.load(f'{d}/zz_cm.npz')
    meta = json.load(open(f'{d}/flood_meta.json'))
    return dict(H=h, Z=zz['z_cm'].astype(np.float32) / 100, ZC=zz['zc_cm'].astype(np.float32) / 100, meta=meta, seg=R['seg'])


def crossings(tr, box, which):
    src = open(f'{ROOT}/sim/colab/w9_lisflood.py').read(); ns = {'np': np}
    exec(src[src.index('def is_bridge'):src.index('def block_crossings')], ns); exec(src[src.index('def small_third'):src.index('def partial_block')], ns)
    X = json.load(open(f'{ROOT}/docs/network/crossings_all.json')); C = X['columns']
    rows = [dict(zip(C, r)) for r in X['rows'] if r[C.index('lon')] is not None]
    xs, ys = tr.transform([r['lon'] for r in rows], [r['lat'] for r in rows]); x0, y0, x1, y1 = box
    keep = ns['small_third'](rows, xs, ys, box) if which == 'small' else None
    return np.array([(x, y) for r, x, y in zip(rows, xs, ys) if x0 <= x < x1 and y0 <= y < y1 and not ns['is_bridge'](r)
                     and (keep is None or r['id'] in keep)])


def crest_pair(O, B, XY, tr):
    """proto/whatif_v3.one_pair on in-memory grids (same constants: 60 m near, 0.30 m over the crest, 40 m pool, 20 m crest)."""
    from scipy.spatial import cKDTree
    meta = O['meta']; res = meta['res_m']; x0, y0, x1, y1 = meta['box']; T = cKDTree(XY); ny, nx = O['Z'].shape; near = {}
    for sid in sorted(set(O['seg']) | set(B['seg'])):
        f = O['seg'].get(sid) or B['seg'][sid]; cl = W.seg_cells(f, meta, tr)
        if not len(cl): continue
        xm = x0 + (cl[:, 1].mean() + 0.5) * res; ym = y1 - (cl[:, 0].mean() + 0.5) * res
        if T.query([xm, ym])[0] <= W.NEAR_M: near[sid] = cl
    def depth(D, cl):
        r, c = cl.T; return W.top2(np.maximum(D['Z'][r, c] + D['H'][r, c] - D['ZC'][r, c], 0.0))
    closed = {t: sorted(s for s, cl in near.items() if depth(D, cl) >= W.CLOSE_M) for t, D in (('open', O), ('blocked', B))}
    yy, xx = np.mgrid[0:ny, 0:nx]; kp, kc = int(W.POOL_M // res), max(1, int(W.CREST_M // res)); pools = []
    for x, y in XY:
        r0, c0 = int((y1 - y) // res), int((x - x0) // res)
        crest = float(O['ZC'][max(0, r0 - kc):r0 + kc + 1, max(0, c0 - kc):c0 + kc + 1].max())
        sl = (slice(max(0, r0 - kp), r0 + kp + 1), slice(max(0, c0 - kp), c0 + kp + 1))
        disk = (yy[sl] - r0) ** 2 + (xx[sl] - c0) ** 2 <= kp * kp; row = dict(crest_m=crest)
        for t, D in (('open', O), ('blocked', B)):
            m = disk & (D['H'][sl] >= W.WET_M) & (D['Z'][sl] < crest)
            row[t] = float((D['Z'][sl] + D['H'][sl])[m].max()) if m.any() else None
        pools.append(row)
    both = [r['blocked'] - r['open'] for r in pools if r['open'] is not None and r['blocked'] is not None]
    ov = {t: sum(1 for r in pools if r[t] is not None and r[t] > r['crest_m']) for t in ('open', 'blocked')}
    return dict(crossings=len(pools), segments_near=len(near), closed_near_open=len(closed['open']), closed_near_blocked=len(closed['blocked']),
                overtopped_open=ov['open'], overtopped_blocked=ov['blocked'], crossings_wet_both=len(both),
                pool_rise_median_m=round(float(np.median(both)), 2) if both else None,
                pool_rise_share_up=round(float(np.mean(np.array(both) > 0)), 3) if both else None)


def main():
    from pyproj import Transformer
    tr = Transformer.from_crs(4326, 26986, always_xy=True)
    out = json.load(open(OUT)); G = {i: grids(i) for i in ['t2_base'] + BLOCKED if os.path.exists(f'{RUNS}/{i}/zz_cm.npz')}
    O = G['t2_base']; box = tuple(O['meta']['box'])
    FB = PE.flagged(dict(seg=O['seg'])); allX = crossings(tr, box, 'all')
    # item 2: notch-artifact check at 100 % blockage
    if 't2_c100' in G:
        F = PE.flagged(dict(seg=G['t2_c100']['seg'])); gone = sorted(FB - F)
        near = [s for s in gone if np.min(np.hypot(*(PE.seg_xy(O['seg'][s], tr)[:, None, :] - allX[None, :, :]).transpose(2, 0, 1))) <= 60]
        pd = lambda R, ss: round(float(np.median([R['seg'][s]['properties'].get('peak_depth_m') or 0 for s in ss])), 2) if ss else None
        out['notch_check'] = dict(base_closed=len(FB), c100_closed=len(F), no_longer_closed=len(gone), within_60m_of_crossing=len(near),
                                  median_peak_depth_base_m=pd(O, near), median_peak_depth_c100_m=pd(G['t2_c100'], near), pre_t2=dict(no_longer_closed=42, within_60m=39))
        out['readable_from_closures'] = bool(len(F) >= len(FB) and len(near) < len(gone) / 2) if gone else bool(len(F) >= len(FB))
    # item 3: crest readout, open vs each blocked run
    out['crest'] = {i: crest_pair(O, G[i], crossings(tr, box, 'small' if i == 't2_ct' else 'all'), tr) for i in BLOCKED if i in G}
    out['crest_readout_works'] = all(c['closed_near_blocked'] >= c['closed_near_open'] and (c['pool_rise_median_m'] or 0) >= 0 for c in out['crest'].values()) \
        if len(out['crest']) == 4 else None
    # item 4: overlap of the priority lists (crossing ids), pre-T2 vs T2
    pre = json.load(open(f'{PH}/parametric.json'))['culvert_priority']
    for a, b in (('pm_c100', 't2_c100'), ('pm_ct', 't2_ct')):
        if a in pre and b in out.get('culvert_priority', {}):
            A = [d['id'] for d in pre[a]['top']]; B = [d['id'] for d in out['culvert_priority'][b]['top']]
            out.setdefault('priority_overlap', {})[b] = dict(in_both=sorted(set(A) & set(B)), n=len(set(A) & set(B)))
    json.dump(out, open(OUT, 'w'), indent=1)
    print(json.dumps({k: out.get(k) for k in ('notch_check', 'readable_from_closures', 'crest_readout_works', 'priority_overlap')}, indent=1))
    for i, c in out['crest'].items(): print(i, c)


if __name__ == '__main__':
    main()
