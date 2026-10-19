"""Hydraulic exceedance at road-stream crossings: a run's modelled channel flow and water surface vs the crossing's capacity record.

    python sim/crossings_capacity.py <run_dir> --out docs/sim/<run>_crossings.json [--channels channels30.npz --channels-meta channels30_meta.json]
    python sim/crossings_capacity.py --selftest
    from crossings_capacity import assess; out = assess(run_dir, crossings, nbi, channels=None)

run_dir holds the engine's outputs (sim/colab/w4_flood_gpu.py): z.npy (ground with channels burnt to the bankfull bed, m NAVD88),
hmax.npy (peak depth m), vmax.npy (peak speed m/s), meta.json (box, res_m, crs EPSG:26986, shape).  Water surface = z + hmax.

Per crossing (docs/network/crossings_ma.json, MA Stream Crossings Project: StreamStats peak flows pk10..pk500 m3/s, bankfull bf_w/bf_d m,
deck_m = road deck elevation m NAVD88):
  1. channel cell: within 60 m of the point, the channels30 cell with the largest drainage area - the nearest among the cells within
     20 % of that maximum, so the main stem wins over a tributary but not the window's downstream edge; without the channel grid,
     the deepest cell (the protocol's HWM rule; the burnt channel is normally the deepest).
  2. unit discharge q = hmax * vmax (m2/s) at that cell and channel flow Q = q * W, W = channels30 bankfull width, else bf_w.  Peak depth
     and peak speed are not simultaneous and the cell speed stands for the channel section, so Q is an approximate peak flow.
  3. return period: log-log interpolation of Q against the StreamStats peaks (T = 10, 25, 50, 100, 500 yr), extrapolated and clipped
     to 1..1000 yr; below pk10 the label is '<10'.
  4. freeboard = deck_m - (z + hmax) at the channel cell; overtop = freeboard < 0; stage_ratio = hmax / bf_d (> 1: above bankfull).
  5. deck_minus_dem = deck_m - z at the point's own (unburnt) cell: a datum/unit check on deck_m, which should be within a few metres
     of the DEM.  A median far from 0 (or a factor of 3.28) means deck_m is not metres NAVD88 and every freeboard is wrong.
Per NBI structure (docs/network/nbi_ma.json, FHWA NBI 2024): for culverts, which carry no peak flows, the modelled peak depth at the
structure's cell and the deepest cell within 30 m, with FHWA item 71 waterway adequacy (0-9; <= 4 = frequent overtopping) and
item 113 scour.  For every NBI structure in the box, a cross-tab of waterway code vs modelled depth >= 10 cm within 30 m.

Claims (docs/validation/protocol.md, L2 "hydraulic exceedance"): these are computed quantities from physics + inventory - how
far the modelled water surface sits below or above the deck, and what StreamStats return period the modelled flow corresponds to.
They are not failure predictions (L3 would need fragility, is labelled 'assumed'), and this module carries no uncertainty: spread
comes from running it across the physics / rain ensemble members.  Indirect validation only: repeating flood points and the NBI
waterway adequacy code (frequent-overtopping structures should sit in the low-freeboard tail).
"""
import os, sys, json, math, time
import numpy as np

T_YR = np.array([10., 25., 50., 100., 500.]); PK = ['pk10', 'pk25', 'pk50', 'pk100', 'pk500']
COLS = ['naacc', 'road', 'stream', 'town', 'lon', 'lat', 'drn_km2', 'area_cell_km2', 'row', 'col', 'dist_m', 'h_m', 'v_ms', 'q_m2s', 'W_m', 'Q_m3s',
        'T_yr', 'T_label', 'pk100', 'wse_m', 'deck_m', 'freeboard_m', 'overtop', 'stage_ratio', 'deck_minus_dem_m', 'design_flood']
NBI_COLS = ['id', 'lon', 'lat', 'year', 'culvert', 'waterway_71', 'scour_113', 'culvert_62', 'adt', 'h_cell_m', 'h_max30_m', 'wet', 'frequent_overtop_code']

def return_period(Q, pk):
    """Return period (yr) of flow Q by log-log interpolation against the StreamStats peaks; None if Q <= 0 or peaks missing."""
    p = np.array([np.nan if v is None else float(v) for v in pk]); ok = np.isfinite(p) & (p > 0)
    if Q <= 0 or ok.sum() < 2: return None
    lq, lt = np.log(p[ok]), np.log(T_YR[ok]); x = math.log(Q)
    if x <= lq[0]: slope = (lt[1] - lt[0]) / (lq[1] - lq[0]); y = lt[0] + slope * (x - lq[0])
    elif x >= lq[-1]: slope = (lt[-1] - lt[-2]) / (lq[-1] - lq[-2]); y = lt[-1] + slope * (x - lq[-1])
    else: y = float(np.interp(x, lq, lt))
    return float(min(1000.0, max(1.0, math.exp(y))))

def t_label(T, Q, pk10):
    if T is None: return None
    if pk10 is not None and Q < pk10: return '<10'
    return '>500' if T >= 1000 else f'{T:.0f}'

def load_channels(path, meta_path, run_meta):
    """Cut the whole-state channels30 grid (area km2, width m) to the run's box and cell size (nearest), as in w4_flood_gpu.hf_grid."""
    D = np.load(path); M = json.load(open(meta_path)); sx0, sy0, sx1, sy1 = M['box']; sres = M['res_m']
    x0, y0, x1, y1 = run_meta['box']; res = run_meta['res_m']; ny, nx = run_meta['shape']
    rr = np.clip(((sy1 - (y1 - (np.arange(ny) + 0.5) * res)) / sres).astype(int), 0, M['shape'][0] - 1)
    cc = np.clip(((x0 + (np.arange(nx) + 0.5) * res - sx0) / sres).astype(int), 0, M['shape'][1] - 1)
    return dict(area=D['area'][np.ix_(rr, cc)].astype(np.float32), width=D['width'][np.ix_(rr, cc)].astype(np.float32))

def assess(run_dir, crossings, nbi=None, channels=None, radius_m=60):
    """crossings / nbi: loaded JSON dicts (columns + rows) or paths; channels: dict(area, width) on the run grid, or None.
    Returns the docs-ready dict (columns, rows, nbi_columns, nbi_rows, summary)."""
    from pyproj import Transformer
    if isinstance(crossings, str): crossings = json.load(open(crossings))
    if isinstance(nbi, str): nbi = json.load(open(nbi))
    meta = json.load(open(os.path.join(run_dir, 'meta.json'))); x0, y0, x1, y1 = meta['box']; res = meta['res_m']
    Z = np.load(os.path.join(run_dir, 'z.npy')).astype(np.float32); H = np.load(os.path.join(run_dir, 'hmax.npy')).astype(np.float32)
    vp = os.path.join(run_dir, 'vmax.npy'); V = np.load(vp).astype(np.float32) if os.path.exists(vp) else None
    ny, nx = H.shape; k = int(math.ceil(radius_m / res)); tr = Transformer.from_crs(4326, 26986, always_xy=True)
    A = channels['area'] if channels else None; CW = channels['width'] if channels else None
    def cell(lon, lat):
        x, y = tr.transform(lon, lat); r, c = int(math.floor((y1 - y) / res)), int(math.floor((x - x0) / res))
        return (r, c, x, y) if 0 <= r < ny and 0 <= c < nx else None
    def channel_cell(r, c, x, y):
        """(row, col, distance m) of the channel cell for the crossing: largest drainage area within radius (nearest among cells within 20 % of it); else deepest."""
        r0, r1, c0, c1 = max(0, r - k), min(ny, r + k + 1), max(0, c - k), min(nx, c + k + 1)
        rr, cc = np.mgrid[r0:r1, c0:c1]; cx, cy = x0 + (cc + 0.5) * res, y1 - (rr + 0.5) * res; d = np.hypot(cx - x, cy - y)
        win = d <= radius_m
        if A is not None and (A[r0:r1, c0:c1][win] > 0).any():
            sc = np.where(win, A[r0:r1, c0:c1], -1.0); best = sc >= 0.8 * sc.max()                    # the main stem (area within 20 % of the max), then nearest: area grows downstream, so a strict max would always pick the window's downstream edge
        else:
            sc = np.where(win, H[r0:r1, c0:c1], -1.0); best = sc >= sc.max() - 1e-3
        i = int(np.argmin(np.where(best, d, np.inf))); return int(rr.ravel()[i]), int(cc.ravel()[i]), float(d.ravel()[i])
    C = {n: i for i, n in enumerate(crossings['columns'])}; rows = []; n_out = 0
    for s in crossings['rows']:
        p = cell(s[C['lon']], s[C['lat']])
        if p is None: n_out += 1; continue
        r, c, x, y = p; cr, cc_, dist = channel_cell(r, c, x, y)
        h = float(H[cr, cc_]); v = float(V[cr, cc_]) if V is not None else None; q = None if v is None else h * v
        W = float(CW[cr, cc_]) if (CW is not None and CW[cr, cc_] > 0) else s[C['bf_w']]
        Q = None if (q is None or not W) else q * float(W); pk = [s[C[n]] for n in PK]
        T = None if Q is None else return_period(Q, pk); deck = s[C['deck_m']]; wse = float(Z[cr, cc_]) + h
        fb = None if deck is None else float(deck) - wse; bfd = s[C['bf_d']]
        rows.append([s[C['naacc']], s[C['road']], s[C['stream']], s[C['town']], s[C['lon']], s[C['lat']], s[C['drn_km2']],
                     None if A is None else round(float(A[cr, cc_]), 3), cr, cc_, round(dist, 1), round(h, 3), None if v is None else round(v, 3),
                     None if q is None else round(q, 3), None if W is None else round(float(W), 2), None if Q is None else round(Q, 3),
                     None if T is None else round(T, 1), t_label(T, Q, s[C['pk10']]) if T is not None else None, s[C['pk100']], round(wse, 2), deck,
                     None if fb is None else round(fb, 2), None if fb is None else int(fb < 0), None if not bfd else round(h / float(bfd), 2),
                     None if deck is None else round(float(deck) - float(Z[r, c]), 2), s[C['design_flood']]])
    R = {n: i for i, n in enumerate(COLS)}; col = lambda n: np.array([x[R[n]] for x in rows if x[R[n]] is not None], float)
    fb = col('freeboard_m'); T = col('T_yr'); dd = col('deck_minus_dem_m'); ac = col('area_cell_km2'); da = np.array([x[R['drn_km2']] for x in rows if x[R['area_cell_km2']] is not None], float)
    summary = dict(crossings_in_box=len(rows), crossings_outside_box=n_out, overtopped=int((fb < 0).sum()), freeboard_lt_1m=int((fb < 1).sum()),
                   above_bankfull=int(sum(1 for x in rows if x[R['stage_ratio']] is not None and x[R['stage_ratio']] > 1)),
                   T_ge_10yr=int((T >= 10).sum()), T_ge_100yr=int((T >= 100).sum()), T_median_yr=round(float(np.median(T)), 1) if len(T) else None,
                   freeboard_median_m=round(float(np.median(fb)), 2) if len(fb) else None,
                   deck_minus_dem_median_m=round(float(np.median(dd)), 2) if len(dd) else None, deck_minus_dem_p90_abs_m=round(float(np.percentile(np.abs(dd), 90)), 2) if len(dd) else None,
                   area_cell_vs_streamstats_median_ratio=round(float(np.median(ac[da > 0] / da[da > 0])), 2) if len(ac) and (da > 0).any() else None,
                   channel_grid=bool(channels), speed_available=V is not None)
    out = dict(run=meta.get('run'), res_m=res, made=time.strftime('%Y-%m-%d'), claim_level='L2 hydraulic exceedance: computed from physics + inventory, not a failure prediction; uncertainty from the ensemble (protocol.md)',
               method=dict(channel_cell='largest channels30 drainage area within 60 m (nearest cell within 20 % of it)' if channels else 'deepest cell within 60 m (no channel grid)',
                           flow='Q = hmax * vmax * W; W = channels30 bankfull width else bf_w; peak depth and speed are not simultaneous', return_period='log-log interpolation of Q against StreamStats pk10..pk500, clipped 1..1000 yr',
                           freeboard='deck_m - (z + hmax) at the channel cell; overtop = freeboard < 0', deck_check='deck_minus_dem_m = deck_m - z at the point cell; median should be near 0 if deck_m is m NAVD88'),
               columns=COLS, rows=rows, summary=summary)
    if nbi:
        N = {n: i for i, n in enumerate(nbi['columns'])}; nrows = []; k30 = int(math.ceil(30 / res)); tab = {}
        for s in nbi['rows']:
            p = cell(s[N['lon']], s[N['lat']])
            if p is None: continue
            r, c = p[:2]; h0 = float(H[r, c]); h30 = float(H[max(0, r - k30):r + k30 + 1, max(0, c - k30):c + k30 + 1].max()); wet = int(h30 >= 0.1)
            w = s[N['waterway_71']]; key = w if w in '0123456789' and len(w) == 1 else 'N'
            t = tab.setdefault(key, [0, 0]); t[0] += 1; t[1] += wet
            if s[N['culvert']]:
                nrows.append([s[N['id']], s[N['lon']], s[N['lat']], s[N['year']], 1, w, s[N['scour_113']], s[N['culvert_62']], s[N['adt']], round(h0, 3), round(h30, 3), wet, int(key != 'N' and int(key) <= 4)])
        out.update(nbi_columns=NBI_COLS, nbi_rows=nrows)
        summary.update(nbi_in_box=int(sum(t[0] for t in tab.values())), nbi_culverts_in_box=len(nrows), nbi_culverts_wet=int(sum(x[NBI_COLS.index('wet')] for x in nrows)),
                       nbi_culverts_frequent_overtop_code=int(sum(x[-1] for x in nrows)),
                       nbi_wet_share_by_waterway_code={k_: dict(n=t[0], wet=t[1], share=round(t[1] / t[0], 2)) for k_, t in sorted(tab.items())},
                       nbi_note='waterway_71: FHWA item 71 waterway adequacy, 0-9, <= 4 = frequent overtopping, N = not over water; wet = modelled peak depth >= 10 cm within 30 m')
    return out

def print_table(out, n=15):
    R = {k: i for i, k in enumerate(out['columns'])}; rows = sorted(out['rows'], key=lambda x: (x[R['freeboard_m']] is None, x[R['freeboard_m']] if x[R['freeboard_m']] is not None else 0))
    print(f"{out['run']}: {out['summary']['crossings_in_box']} crossings in box, {out['summary']['overtopped']} overtopped (freeboard < 0), {out['summary']['freeboard_lt_1m']} with freeboard < 1 m; "
          f"deck - DEM median {out['summary']['deck_minus_dem_median_m']} m; channel grid {out['summary']['channel_grid']}")
    print(f"{'road':<26}{'town':<14}{'A km2':>7}{'h m':>6}{'v m/s':>7}{'Q m3/s':>8}{'pk100':>7}{'T yr':>6}{'freeb m':>9}{'over':>5}")
    for x in rows[:n]:
        f = lambda v, w: f'{v:>{w}}' if v is None else (f'{v:>{w}.2f}' if isinstance(v, float) else f'{v:>{w}}')
        print(f"{str(x[R['road']])[:25]:<26}{str(x[R['town']])[:13]:<14}{f(x[R['drn_km2']], 7)}{f(x[R['h_m']], 6)}{f(x[R['v_ms']], 7)}{f(x[R['Q_m3s']], 8)}{f(x[R['pk100']], 7)}{str(x[R['T_label']]):>6}{f(x[R['freeboard_m']], 9)}{f(x[R['overtop']], 5)}")
    if 'nbi_rows' in out: print(f"NBI: {out['summary']['nbi_culverts_in_box']} culverts in box, {out['summary']['nbi_culverts_wet']} wet; wet share by waterway code:",
                                 {k: v['share'] for k, v in out['summary']['nbi_wet_share_by_waterway_code'].items()})

def selftest():
    """Synthetic 30 m valley with a channel; crossing A deep (overtopped), crossing B dry (clear freeboard); an NBI culvert on A."""
    import tempfile; from pyproj import Transformer
    d = tempfile.mkdtemp(); res = 30; ny, nx = 120, 160; x0, y0 = 100000.0, 900000.0; x1, y1 = x0 + nx * res, y0 + ny * res
    rr, cc = np.mgrid[0:ny, 0:nx]; z = 200 + 0.02 * res * cc + 0.05 * res * np.abs(rr - 60)             # valley floor along row 60, falling west -> east
    z[60] -= 0.8                                                                                         # burnt channel (bankfull bed)
    h = np.zeros((ny, nx), np.float32); v = np.zeros((ny, nx), np.float32); area = np.zeros((ny, nx), np.float32); width = np.zeros((ny, nx), np.float32)
    area[60] = 0.5 + 0.1 * cc[60]; width[60] = 2.70 * area[60] ** 0.352
    h[59:62, :] = 0.2; h[60, :] = 1.0; v[60, :] = 0.8                                                    # baseflow-ish everywhere
    h[60, 95:105] = 3.5; v[60, 95:105] = 2.0; h[58:63, 95:105] = np.maximum(h[58:63, 95:105], 1.2)       # a ponded reach at crossing A
    np.save(f'{d}/z.npy', z.astype(np.float32)); np.save(f'{d}/hmax.npy', h.astype(np.float16)); np.save(f'{d}/vmax.npy', v.astype(np.float16))
    json.dump(dict(run='selftest', res_m=res, box=[x0, y0, x1, y1], crs='EPSG:26986', shape=[ny, nx]), open(f'{d}/meta.json', 'w'))
    inv = Transformer.from_crs(26986, 4326, always_xy=True); pt = lambda r, c: inv.transform(x0 + (c + 0.5) * res, y1 - (r + 0.5) * res)
    def xrow(r, c, name, deck_above_ground):
        lon, lat = pt(r, c); A = float(area[60, c]); pk = [A * k for k in (2.0, 2.9, 3.6, 4.5, 6.8)]
        return [round(lon, 5), round(lat, 5), 'xy' + name, name, 'Brook', 'Testville', round(A, 3), *[round(p, 3) for p in pk], round(float(width[60, c]), 3), 0.25, round(float(z[r, c]) + deck_above_ground, 3), 0, '10-yr']
    X = dict(columns=['lon', 'lat', 'naacc', 'road', 'stream', 'town', 'drn_km2', 'pk10', 'pk25', 'pk50', 'pk100', 'pk500', 'bf_w', 'bf_d', 'deck_m', 'hwy_class', 'design_flood'],
             rows=[xrow(59, 100, 'A', 0.2), xrow(61, 40, 'B', 0.2), xrow(10, 10, 'C', 0.2)])          # points on the bank (1.5 m above the 0.8 m burnt bed) with the deck 0.2 m above ground = bed + 2.5: A has 3.5 m of water -> overtopped; B 1 m -> freeboard 1.5; C off-channel, dry
    lonA, latA = pt(60, 100); lonN, latN = pt(20, 20)
    NB = dict(columns=['lon', 'lat', 'id', 'year', 'type', 'culvert', 'waterway_71', 'scour_113', 'deck_58', 'super_59', 'sub_60', 'culvert_62', 'channel_61', 'adt', 'route'],
              rows=[[lonA, latA, 'CULV-A', '1960', '19', 1, '4', '5', 'N', 'N', 'N', '6', '6', '500', '0'], [lonN, latN, 'BR-N', '1990', '1', 0, '8', '8', '7', '7', '7', 'N', '7', '900', '0'],
                    [-70.0, 41.0, 'OUT', '1990', '1', 0, '8', '8', '7', '7', '7', 'N', '7', '900', '0']])
    out = assess(d, X, NB, channels=dict(area=area, width=width)); R = {k: i for i, k in enumerate(out['columns'])}; byn = {x[R['road']]: x for x in out['rows']}
    a, b = byn['A'], byn['B']
    assert (a[R['row']], a[R['col']]) == (60, 100) and a[R['dist_m']] <= 31, a[:12]                     # snapped from row 59 to the channel row by drainage area
    assert a[R['overtop']] == 1 and abs(a[R['freeboard_m']] - (2.5 - 3.5)) < 0.02, a
    assert b[R['overtop']] == 0 and abs(b[R['freeboard_m']] - 1.5) < 0.02, b
    QA = 3.5 * 2.0 * float(width[60, 100]); assert abs(a[R['Q_m3s']] - QA) < 0.05 * QA and 50 < a[R['T_yr']] < 100, (a[R['Q_m3s']], QA, a[R['T_yr']])   # Q between pk50 and pk100 of this synthetic record
    assert b[R['T_label']] == '<10' and 1 <= b[R['T_yr']] < 10, b[R['T_yr']]
    assert abs(a[R['stage_ratio']] - 14.0) < 0.1 and abs(byn['C'][R['freeboard_m']] - 0.2) < 0.02 and byn['C'][R['overtop']] == 0, (a[R['stage_ratio']], byn['C'])  # C: no channel within 60 m -> deepest cell (itself, dry)
    assert abs(a[R['deck_minus_dem_m']] - 0.2) < 0.02, a[R['deck_minus_dem_m']]                          # deck vs the point's own (bank) cell
    S = out['summary']; assert S['crossings_in_box'] == 3 and S['overtopped'] == 1 and S['nbi_culverts_in_box'] == 1 and S['nbi_in_box'] == 2, S
    nb = out['nbi_rows'][0]; assert nb[0] == 'CULV-A' and nb[-1] == 1 and nb[-2] == 1 and abs(nb[-4] - 3.5) < 0.01, nb
    assert S['nbi_wet_share_by_waterway_code']['8']['wet'] == 0, S['nbi_wet_share_by_waterway_code']
    # no channel grid -> deepest cell rule: A still lands on the channel row
    out2 = assess(d, X, None); a2 = {x[R['road']]: x for x in out2['rows']}['A']; assert (a2[R['row']], a2[R['col']]) == (60, 100) and a2[R['overtop']] == 1, a2
    assert abs(a2[R['Q_m3s']] - 3.5 * 2.0 * X['rows'][0][12]) < 1e-3, a2[R['Q_m3s']]                      # W falls back to bf_w
    assert return_period(0.0, [1, 2, 3, 4, 5]) is None and return_period(5.0, [None, None, 3, None, None]) is None
    assert abs(return_period(4.0, [1, 2, 3, 4, 5]) - 100) < 1e-6 and return_period(100.0, [1, 2, 3, 4, 5]) == 1000 and return_period(0.01, [1, 2, 3, 4, 5]) == 1   # exact node, clipped extrapolation both ways
    # load_channels: a 'whole-state' grid 60 m larger on every side, 30 m cells -> cut back to the run box reproduces the arrays
    np.savez(f'{d}/ch.npz', area=np.pad(area, 2), width=np.pad(width, 2)); json.dump(dict(box=[x0 - 60, y0 - 60, x1 + 60, y1 + 60], res_m=30, shape=[ny + 4, nx + 4]), open(f'{d}/ch_meta.json', 'w'))
    ch = load_channels(f'{d}/ch.npz', f'{d}/ch_meta.json', json.load(open(f'{d}/meta.json'))); assert np.array_equal(ch['area'], area) and np.array_equal(ch['width'], width)
    print_table(out); print('selftest OK:', d)

if __name__ == '__main__':
    import argparse
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0]); ap.add_argument('run_dir', nargs='?'); ap.add_argument('--out'); ap.add_argument('--selftest', action='store_true')
    ap.add_argument('--crossings', default=os.path.join(os.path.dirname(__file__), '..', 'docs', 'network', 'crossings_ma.json')); ap.add_argument('--nbi', default=os.path.join(os.path.dirname(__file__), '..', 'docs', 'network', 'nbi_ma.json'))
    ap.add_argument('--channels', help='channels30.npz (whole-state grid, from HF data/channels30/)'); ap.add_argument('--channels-meta', help='channels30_meta.json'); ap.add_argument('--top', type=int, default=15)
    a = ap.parse_args()
    if a.selftest: selftest(); sys.exit(0)
    if not a.run_dir: ap.error('run_dir required (or --selftest)')
    ch = load_channels(a.channels, a.channels_meta, json.load(open(os.path.join(a.run_dir, 'meta.json')))) if a.channels else None
    out = assess(a.run_dir, a.crossings, a.nbi if os.path.exists(a.nbi) else None, channels=ch); print_table(out, a.top)
    p = a.out or os.path.join(a.run_dir, 'crossings.json'); os.makedirs(os.path.dirname(p) or '.', exist_ok=True)
    json.dump(out, open(p, 'w'), separators=(',', ':')); print('wrote', p, f"({len(out['rows'])} crossings, {len(out.get('nbi_rows', []))} NBI culverts)")
