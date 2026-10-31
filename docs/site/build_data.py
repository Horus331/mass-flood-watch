"""Build the web-friendly replay data for the public site (docs/site/data/<run>/).

Writes, per run:
  meta.json     corners, clock, timeline series, headline numbers (copied, not recomputed)
  depth_NN.png  flood-depth classes for 9 frames per image, packed base 5 into RGB
  roads.json    flagged road segments (simplified) with closure intervals, depth on the road per frame (cm) and popup facts
  refs.json     reference layers in the run's box: USGS gauges (observed vs modelled), stream crossings and culverts,
                bridges, dams, hospitals / fire / police, and the storm reports the run is validated against
  flow.png + flow.json   (with --flow and --run-dir) low-res water velocity per frame for the flow animation

Published runs (from the committed outputs under docs/proto/), run from the repo root:
    python3 docs/site/build_data.py
A new model run straight from its LISFLOOD-FP output folder (e.g. 5-min snapshots on the Turing cluster):
    python proto/prototype.py --run-dir $OUT --storm sep2023 --out results/leominster_5min
    python3 docs/site/build_data.py --run leominster_sep2023 --src results/leominster_5min --run-dir $OUT --flow
  --src      the prototype.py output folder (segments.geojson, summary.json, map.html; risk files are optional)
  --run-dir  the flood model's out/ folder (frames_cm.npz, z.npy, watermask.npy, xings.json): depth frames are read at
             full precision from frames_cm.npz instead of the PNG frames, the flow field comes from the water surface,
             and modelled gauge flow from xings.json
  --frame-min  keep one frame every N minutes (default: every snapshot)
"""
import argparse
import datetime as dt
import json
import math
import os
import re

import numpy as np
from PIL import Image
from shapely.geometry import shape, mapping
from shapely.ops import linemerge

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
P = os.path.join(ROOT, 'docs', 'proto')
NET = os.path.join(ROOT, 'docs', 'network')
OUT = os.path.join(ROOT, 'docs', 'site', 'data')
RUNS = {  # site key: (source folder under docs/proto, spatial max-pool factor)
    'leominster_sep2023': ('leominster_sep2023', 1),
    'worcester_aug2021': ('worcester_aug2021', 1),
    'd3_sep2023': ('turing/d3_sep2023_20m', 4),
}
# frame colours written by proto/prototype.py (cols at 5 / 15 / 30 / 100 cm)
CLASS_RGB = {(198, 219, 239): 1, (107, 174, 214): 2, (33, 113, 181): 3, (8, 48, 107): 4}
CLS = {'local / collector': 0, 'arterial': 1, 'highway': 2}
CFS = 0.0283168


def corners(src):
    html = open(os.path.join(src, 'map.html')).read()
    return json.loads(re.search(r'C=(\[\[.*?\]\])', html).group(1))


def pool(c, f):
    if f > 1:  # keep the deepest class of each block so thin streams stay visible
        h, w = (c.shape[0] // f) * f, (c.shape[1] // f) * f
        c = c[:h, :w].reshape(h // f, f, w // f, f).max(axis=(1, 3))
    return c


def despeckle(c):
    """drop isolated shallow cells: a 5-15 cm cell (class 1) with fewer than 3 wet cells in its 3 x 3 neighbourhood (itself included) is
    dried for display. Deeper water and every connected patch stay; the viewer's road pieces read the same cleaned surface."""
    w = (c >= 1).astype(np.uint8); n = w.copy()
    n[1:] += w[:-1]; n[:-1] += w[1:]
    m = n.copy(); m[:, 1:] += n[:, :-1]; m[:, :-1] += n[:, 1:]
    c = c.copy(); c[(c == 1) & (m < 3)] = 0
    return c


# surface water left on the land, box mean in mm per frame, from the published depth classes (class mid-depths 0, 10, 22, 65, 130 cm). The
# viewer's 'soaked in or drained' readout is the rain fallen so far (rain_hourly_mean_mm) minus this; both are box means, so it is an
# estimate of where the rain went, not a water balance.
CLASS_MID_MM = np.array([0, 100, 220, 650, 1300], dtype=np.float64)


def surface_mm(od, meta):
    return [round(float(CLASS_MID_MM[f].mean()), 2) for f in sheet_frames(od, meta)]


def despeckle_pack(od, meta):
    """rewrite a published pack's depth sheets with despeckle() (same packing: 9 frames per image, base 5)"""
    for i, s in enumerate(meta['sheets']):
        a = np.asarray(Image.open(os.path.join(od, s))).astype(np.int32); out = np.zeros(a.shape, np.uint8)
        for j in range(9):
            if i * 9 + j >= meta['nf']: break
            k = (1, 5, 25)[j % 3]; c = ((a[..., j // 3] // k) % 5).astype(np.uint8)
            out[..., j // 3] += despeckle(c) * k
        Image.fromarray(out, 'RGB').save(os.path.join(od, s), optimize=True)


def classes_png(png, f):
    a = np.asarray(Image.open(png).convert('RGBA'))
    c = np.zeros(a.shape[:2], np.uint8)
    for rgb, k in CLASS_RGB.items():
        c[(a[..., 0] == rgb[0]) & (a[..., 1] == rgb[1]) & (a[..., 2] == rgb[2]) & (a[..., 3] > 0)] = k
    return pool(c, f)


def classes_cm(cm, f):
    c = np.zeros(cm.shape, np.uint8)
    for k, th in enumerate((5, 15, 30, 100)):
        c[cm >= th] = k + 1
    return pool(c, f)


def intervals(d):
    """closed stretches (depth >= 30 cm) in fractional frame units"""
    out, start = [], None
    for i, v in enumerate(d):
        if v >= 30 and start is None:
            start = i if i == 0 else i - 1 + (30 - d[i - 1]) / max(v - d[i - 1], 1e-6)
        if v < 30 and start is not None:
            out.append([round(start, 2), round(i - 1 + (d[i - 1] - 30) / max(d[i - 1] - v, 1e-6), 2)])
            start = None
    if start is not None:
        out.append([round(start, 2), len(d) - 1 + 0.5])
    return out


def utc(s):
    """ISO time with any offset -> naive UTC datetime"""
    s = s.replace('Z', '+00:00')
    if re.match(r'.*T\d\d:\d\d$', s):
        s += '+00:00'
    t = dt.datetime.fromisoformat(s)
    return t.astimezone(dt.timezone.utc).replace(tzinfo=None) if t.tzinfo else t


def lonlat_box(cn, m=0.0):
    lo = [c[0] for c in cn]; la = [c[1] for c in cn]
    return min(lo) - m, min(la) - m, max(lo) + m, max(la) + m


def inside(b, lon, lat):
    return lon is not None and lat is not None and b[0] <= lon <= b[2] and b[1] <= lat <= b[3]


def clean(x):
    """NaN / 'nan' -> None, recursively, so the JSON stays valid for browsers"""
    if isinstance(x, float) and (math.isnan(x) or math.isinf(x)):
        return None
    if isinstance(x, str) and x.lower() == 'nan':
        return None
    if isinstance(x, dict):
        return {k: clean(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [clean(v) for v in x]
    return x


def jload(p):
    return json.load(open(p)) if os.path.exists(p) else None


# ---------------------------------------------------------------- water at the road edge
# The road state (d) is the modelled water ON the road (second-highest road point, minus the road crown above the 20 m cell mean), so a road
# on an embankment through a flooded 20 m cell can stay open while the map draws water across it. The viewer then shows such a road as
# 'water at the road edge' instead of nothing: e = frame intervals when >= EDGE_SHARE of the road line lies under drawn water (>= 5 cm,
# land cells; channels and ponds are not drawn).
EDGE_SHARE = 0.25


def road_cells(geom, box, res, shape):
    from pyproj import Transformer
    tf = road_cells.tf = getattr(road_cells, 'tf', None) or Transformer.from_crs(4326, 26986, always_xy=True)
    lines = [geom['coordinates']] if geom['type'] == 'LineString' else geom['coordinates']
    pts = []
    for l in lines:
        x, y = tf.transform([c[0] for c in l], [c[1] for c in l])
        for a in range(len(x) - 1):
            n = max(1, int(math.hypot(x[a + 1] - x[a], y[a + 1] - y[a]) / (res / 2)))
            for t in np.linspace(0, 1, n, endpoint=False):
                pts.append((x[a] + t * (x[a + 1] - x[a]), y[a] + t * (y[a + 1] - y[a])))
    if not pts:
        return None
    P_ = np.array(pts); c = ((P_[:, 0] - box[0]) // res).astype(int); r = ((box[3] - P_[:, 1]) // res).astype(int)
    ok = (c >= 0) & (c < shape[1]) & (r >= 0) & (r < shape[0])
    return (r[ok], c[ok]) if ok.any() else None


def edge_intervals(frame_iter, cells, land=None):
    """frame_iter yields class grids (0 dry .. 4); cells {sid: (r, c)} -> {sid: [[a, b], ...]} in frame units"""
    W = {k: [] for k in cells}
    for f in frame_iter:
        for k, (r, c) in cells.items():
            v = f[r, c] >= 1
            if land is not None: v = v & land[r, c]
            W[k].append(bool(v.mean() >= EDGE_SHARE))
    out = {}
    for k, w in W.items():
        iv, st = [], None
        for i, on in enumerate(w + [False]):
            if on and st is None: st = i
            if not on and st is not None: iv.append([st, i - 1]); st = None
        if iv: out[k] = iv
    return out


# ---------------------------------------------------------------- road pieces
# A road segment runs from junction to junction (often 300 m to 1 km); its state (water on road / at risk / closed) comes from its two
# wettest road points. Drawing that state along the whole segment paints dry road. pieces.json splits every segment into ~PIECE_M pieces
# and records, per piece, the frames when the map draws water on the piece itself (>= 5 cm, the depth layer's floor, in the cells under at
# least half of its samples; water in the next cell over does not count). The viewer colours a piece with its segment's state only while
# the piece itself is wet.
PIECE_M = 40.0


def split_pieces(geom, piece_m=PIECE_M):
    from pyproj import Transformer
    tf = getattr(split_pieces, 'tf', None) or Transformer.from_crs(4326, 26986, always_xy=True); split_pieces.tf = tf
    inv = getattr(split_pieces, 'inv', None) or Transformer.from_crs(26986, 4326, always_xy=True); split_pieces.inv = inv
    lines = [geom['coordinates']] if geom['type'] == 'LineString' else geom['coordinates']
    out = []
    for l in lines:
        if len(l) < 2: continue
        x, y = tf.transform([c[0] for c in l], [c[1] for c in l]); x = np.array(x); y = np.array(y)
        d = np.r_[0, np.cumsum(np.hypot(np.diff(x), np.diff(y)))]; L = d[-1]
        if L <= 0: continue
        n = max(1, int(round(L / piece_m))); cuts = np.linspace(0, L, n + 1)
        for a, b in zip(cuts[:-1], cuts[1:]):
            inner = [i for i in range(len(d)) if a < d[i] < b]
            ds = [a] + [d[i] for i in inner] + [b]
            px = np.interp(ds, d, x); py = np.interp(ds, d, y)
            out.append((px, py))
    return out


def pieces_build(features, box, res, shape, frame_iter, land=None):
    """features: [(sid, geometry)] -> (pieces json: seg ids, lon/lat lines, per-piece wet frame intervals)"""
    segs, lines, samp = [], [], []
    inv = None
    for sid, geom in features:
        for px, py in split_pieces(geom):
            if inv is None: inv = split_pieces.inv
            lo, la = inv.transform(px, py)
            L = np.hypot(np.diff(px), np.diff(py)).sum(); n = max(2, int(L / (res / 2)))
            t = np.linspace(0, 1, n); dd = np.r_[0, np.cumsum(np.hypot(np.diff(px), np.diff(py)))]
            sx = np.interp(t * dd[-1], dd, px); sy = np.interp(t * dd[-1], dd, py)
            c = np.clip(((sx - box[0]) // res).astype(int), 0, shape[1] - 1); r = np.clip(((box[3] - sy) // res).astype(int), 0, shape[0] - 1)
            segs.append(int(sid)); lines.append([[round(a, 5), round(b, 5)] for a, b in zip(lo, la)]); samp.append((r, c))
    W = [[] for _ in segs]; N = [[] for _ in segs]; W30 = [[] for _ in segs]
    for f in frame_iter:
        m = f >= 1; m3 = f >= 3
        if land is not None: m &= land; m3 &= land
        g = m.copy(); g[1:] |= m[:-1]; g[:-1] |= m[1:]; g2 = g.copy(); g2[:, 1:] |= g[:, :-1]; g2[:, :-1] |= g[:, 1:]
        for i, (r, c) in enumerate(samp):
            W[i].append(bool(m[r, c].mean() >= 0.5)); N[i].append(bool(g2[r, c].mean() >= 0.5)); W30[i].append(bool(m3[r, c].mean() >= 0.5))

    def ivs(w):
        iv, st = [], None
        for i, on in enumerate(w + [False]):
            if on and st is None: st = i
            if not on and st is not None: iv.append([st, i - 1]); st = None
        return iv
    wet = [ivs(w) for w in W]
    # n: water drawn on the piece or in the cell beside it (3 x 3), only where it adds to w. The viewer uses it for one case: a closed
    # segment with no drawn water on any of its own pieces (the water sits in the ditch or on the embankment cell beside the road).
    near = [ivs([b and not a for a, b in zip(w, nn)]) for w, nn in zip(W, N)]
    return dict(about='road segments split into ~%d m pieces; w = frame intervals when the map draws water (>= 5 cm) on the piece '
                      '(docs/site/build_data.py pieces_build); w30 = frame intervals with 30 cm or more on the piece (impassable)' % PIECE_M,
                seg=segs, lines=lines, w=wet, n=near, w30=[ivs(w) for w in W30])


def sheet_frames(od, meta):
    for i, s in enumerate(meta['sheets']):
        a = np.asarray(Image.open(os.path.join(od, s)))
        for j in range(9):
            if i * 9 + j < meta['nf']: yield ((a[..., j // 3] // (1, 5, 25)[j % 3]) % 5).astype(np.uint8)


# ---------------------------------------------------------------- reference layers
def refs(src, cn, storm, t0, frame_min, nf, run_dir=None):
    B = lonlat_box(cn)
    out = {}
    # gauges: location and observed flow from docs/proto/obs, modelled rise / peak from the run's score.json
    G = jload(os.path.join(P, 'obs', 'gauges_%s.json' % storm)) or {'gauges': []}
    sc = {g['site']: g for g in (jload(os.path.join(src, 'score.json')) or {}).get('gauges', [])}
    mq = {}
    if run_dir:
        for g in (jload(os.path.join(run_dir, 'xings.json')) or {}).get('gauges', []):
            if g.get('q_series'):
                mq[g['site']] = g['q_series']
    times = [t0 + dt.timedelta(minutes=frame_min * i) for i in range(nf)]
    gs = []
    for g in G['gauges']:
        lon, lat = float(g['lon']), float(g['lat'])
        if not inside(B, lon, lat):
            continue
        e = {'site': g['site'], 'name': g['name'].title().replace(' Ma', ', MA').replace(' At ', ' at ').replace(' Near ', ' near '),
             'lon': round(lon, 5), 'lat': round(lat, 5)}
        if g.get('drain_mi2'):
            e['km2'] = round(float(g['drain_mi2']) * 2.58999, 1)
        q = g.get('q_cfs') or []
        if q:
            ts = np.array([(utc(a) - t0).total_seconds() / 60 for a, _ in q])
            vs = np.array([float(v) * CFS for _, v in q])
            fm = np.array([frame_min * i for i in range(nf)])
            ok = (fm >= ts.min()) & (fm <= ts.max())
            series = np.where(ok, np.interp(fm, ts, vs), np.nan)
            e['obs_q'] = [None if np.isnan(v) else round(float(v), 2) for v in series]
        s = sc.get(g['site'])
        if s:
            for k in ('obs_rise_m', 'model_rise_m', 'obs_peak_utc', 'model_peak_utc', 'timing_error_h', 'obs_peak_q_m3s'):
                if s.get(k) is not None:
                    e[k] = s[k]
        if g['site'] in mq:
            e['model_q'] = [round(float(v), 2) for v in mq[g['site']][:nf]]
        gs.append(e)
    out['gauges'] = gs
    # crossings: every assessed stream crossing in the box; risk class and overtopping chance where the run rated it
    rk = {}
    rm = os.path.join(src, 'risk_matrix.csv')
    if os.path.exists(rm):
        import csv
        for r in csv.DictReader(open(rm)):
            if r['type'] == 'crossing':
                rk[r['id']] = (r['risk'], float(r['likelihood'] or 0), r['detail'])
    X = json.load(open(os.path.join(NET, 'crossings_all.json')))
    col = {c: i for i, c in enumerate(X['columns'])}
    xs = []
    big = (B[2] - B[0]) * (B[3] - B[1]) > 0.2          # District 3: only surveyed or rated crossings, not every road-stream crossing
    for r in X['rows']:
        lon, lat = r[col['lon']], r[col['lat']]
        if not inside(B, lon, lat):
            continue
        cid = r[col['id']]
        surveyed = bool(r[col['naacc_code']]) or bool(r[col['span_m']])
        if big and not (cid in rk or surveyed):
            continue
        xt = (r[col['xtype']] or '').lower()
        kind = 'culvert' if (r[col['shape']] or 'culvert' in xt) else 'bridge' if xt and 'tiger' not in xt else 'crossing'
        cond = r[col['condition']] or ''
        e = [round(lon, 5), round(lat, 5), r[col['road']] or '', '' if (r[col['stream']] or '') == 'Unknown' else (r[col['stream']] or ''), kind,
             (r[col['shape']] or '').replace('_', ' '), r[col['span_m']], '' if cond in ('No data', 'nan') else cond]
        if cid in rk:
            e += [rk[cid][0], round(rk[cid][1], 2)]
        xs.append(e)
    out['crossings'] = {'columns': ['lon', 'lat', 'road', 'stream', 'kind', 'shape', 'span_m', 'condition', 'risk', 'p_overtop'], 'rows': xs}
    # bridges (NBI), dams (NID), facilities (OSM)
    N = json.load(open(os.path.join(NET, 'nbi_ma.json'))); c = {k: i for i, k in enumerate(N['columns'])}
    out['bridges'] = [[round(r[c['lon']], 5), round(r[c['lat']], 5), r[c['id']], int(r[c['year']] or 0), int(r[c['culvert']] or 0),
                       r[c['scour_113']], r[c['adt']]] for r in N['rows'] if inside(B, r[c['lon']], r[c['lat']])]
    D = json.load(open(os.path.join(NET, 'dams_ma.json'))); c = {k: i for i, k in enumerate(D['columns'])}
    out['dams'] = [[round(r[c['lon']], 5), round(r[c['lat']], 5), r[c['name']], r[c['river']] or '', r[c['hazard']] or '',
                    r[c['dam_height_ft']], r[c['condition']] or ''] for r in D['rows'] if inside(B, r[c['lon']], r[c['lat']])]
    F = json.load(open(os.path.join(NET, 'facilities.json')))['facilities']
    out['facilities'] = {k: [[round(a, 5), round(b, 5), n or ''] for a, b, n in F.get(k, []) if inside(B, a, b)]
                         for k in ('hospital', 'fire_station', 'police')}
    # storm reports and documented closure / damage sites the run is scored against
    pts = (jload(os.path.join(src, 'points.json')) or {}).get('points', [])
    out['reports'] = [[round(p['lon'], 5), round(p['lat'], 5), p['src'].replace('labels:', ''), (p.get('text') or '')[:140], p.get('t'),
                       round(p['max_m'], 2) if p.get('max_m') is not None else None, bool(p.get('hit_30'))]
                      for p in pts if inside(B, p['lon'], p['lat'])]
    return out


# ---------------------------------------------------------------- flow field
def flow_solver(run_dir, keep, f_out, od, cn, step_min, per_sheet=49):
    """Water velocity straight from the flood solver (out/vel_frames.npz, LF_VFRAMES=1: LISFLOOD-FP .Vx/.Vy snapshots), on blocks of f_out
    cells, one frame per kept snapshot. Block velocity = depth-weighted mean of the wet cells (h >= 5 cm), i.e. block discharge per unit width
    over block depth, so a fast thin sheet does not outweigh the channel that carries the water. Packed like flow(): R, G = east / north
    speed (128 = 0, +-VMAX, square-root scaled so slow street flow keeps resolution), B = wet share; several atlas sheets of per_sheet frames."""
    V = np.load(os.path.join(run_dir, 'vel_frames.npz')); D = np.load(os.path.join(run_dir, 'frames_cm.npz'))
    meta = jload(os.path.join(run_dir, 'meta.json')) or {}
    res = float(meta.get('res_m') or 20.0); VMAX = 4.0
    vh = np.asarray(V['hours'], float); dh = np.asarray(D['hours'], float)
    ny, nx = V['u_ms'].shape[1:]; h2, w2 = ny // f_out, nx // f_out
    frames = []; vpk = 0.0
    for k in keep:
        j = int(np.argmin(np.abs(vh - dh[k])))
        if abs(vh[j] - dh[k]) > 0.05: frames.append(None); continue       # no velocity snapshot at this depth frame
        h = D['depth_cm'][k].astype(np.float32)[:h2 * f_out, :w2 * f_out] / 100.0
        u = V['u_ms'][j].astype(np.float32)[:h2 * f_out, :w2 * f_out]; v = V['v_ms'][j].astype(np.float32)[:h2 * f_out, :w2 * f_out]
        w = np.where(h >= 0.05, h, 0.0)
        r = lambda a: a.reshape(h2, f_out, w2, f_out).sum(axis=(1, 3))
        hs = r(w) + 1e-6; U = r(u * w) / hs; Vn = r(v * w) / hs; wet = r((h >= 0.05).astype(np.float32)) / (f_out * f_out)
        vpk = max(vpk, float(np.hypot(U, Vn)[wet > 0].max()) if (wet > 0).any() else 0.0)
        sp = np.hypot(U, Vn); g = np.sqrt(np.minimum(sp, VMAX) / VMAX) / np.maximum(sp, 1e-6)   # unit vector x sqrt(speed / VMAX)
        frames.append(np.stack([np.clip(np.round(128 + U * g * 127), 1, 255), np.clip(np.round(128 + Vn * g * 127), 1, 255),
                                np.round(np.clip(wet, 0, 1) * 255)], -1).astype(np.uint8))
    blank = np.zeros((h2, w2, 3), np.uint8); blank[..., :2] = 128
    frames = [a if a is not None else blank for a in frames]
    n = len(frames); sheets = []
    cols = max(1, int(math.ceil(math.sqrt(min(n, per_sheet) * h2 / w2)))); rows = (min(n, per_sheet) + cols - 1) // cols
    for s0 in range(0, n, per_sheet):
        atlas = np.zeros((rows * h2, cols * w2, 3), np.uint8); atlas[..., :2] = 128
        for i, a in enumerate(frames[s0:s0 + per_sheet]):
            cy, cx = divmod(i, cols); atlas[cy * h2:(cy + 1) * h2, cx * w2:(cx + 1) * w2] = a
        nm = 'flow_%02d.png' % len(sheets); Image.fromarray(atlas, 'RGB').save(os.path.join(od, nm), optimize=True); sheets.append(nm)
    json.dump({'n': n, 'frame_min': step_min, 'w': w2, 'h': h2, 'cols': cols, 'rows': rows, 'per_sheet': per_sheet, 'sheets': sheets,
               'vmax_ms': VMAX, 'enc': 'sqrt', 'peak_ms': round(vpk, 2), 'cell_m': res * f_out, 'corners': cn,
               'method': 'LISFLOOD-FP solver velocity (.Vx/.Vy snapshots), depth-weighted over %d m blocks' % int(res * f_out)},
              open(os.path.join(od, 'flow.json'), 'w'), separators=(',', ':'))
    print('  flow (solver)', n, 'frames', '%dx%d' % (w2, h2), len(sheets), 'sheets, peak block speed %.2f m/s' % vpk)


def flow(run_dir, keep, f_out, od, cn, step_min):
    """Water velocity from the modelled water surface (diffusive-wave estimate, Manning n 0.05) on blocks of f_out cells,
    one frame per kept snapshot, packed 1 frame per atlas cell: R, G = east / north speed (128 = 0, +-VMAX), B = wet share."""
    D = np.load(os.path.join(run_dir, 'frames_cm.npz'))
    Z = np.load(os.path.join(run_dir, 'z.npy')).astype(np.float32)
    meta = jload(os.path.join(run_dir, 'meta.json')) or {}
    res = float(meta.get('res_m') or 20.0)
    VMAX, N_MAN = 3.0, 0.05
    ny, nx = Z.shape
    h2, w2 = ny // f_out, nx // f_out
    frames = []
    for k in keep:
        h = D['depth_cm'][k].astype(np.float32) / 100.0
        wse = Z + h
        sy, sx = np.gradient(wse, res)                # rows run north -> south, so -sy is the northward slope
        s = np.hypot(sx, sy) + 1e-6
        v = np.where(h >= 0.05, np.minimum(h ** (2 / 3) * np.sqrt(s) / N_MAN, VMAX), 0.0)
        ue, vn = -sx / s * v, sy / s * v
        hb = h[:h2 * f_out, :w2 * f_out].reshape(h2, f_out, w2, f_out)
        wet = (hb >= 0.05).mean(axis=(1, 3))
        hs = hb.sum(axis=(1, 3)) + 1e-6
        U = (ue[:h2 * f_out, :w2 * f_out].reshape(h2, f_out, w2, f_out) * hb).sum(axis=(1, 3)) / hs
        V = (vn[:h2 * f_out, :w2 * f_out].reshape(h2, f_out, w2, f_out) * hb).sum(axis=(1, 3)) / hs
        frames.append(np.stack([np.clip(np.round(128 + U / VMAX * 127), 1, 255), np.clip(np.round(128 + V / VMAX * 127), 1, 255),
                                np.round(np.clip(wet, 0, 1) * 255)], -1).astype(np.uint8))
    n = len(frames)
    cols = max(1, int(math.ceil(math.sqrt(n * h2 / w2))))
    rows = (n + cols - 1) // cols
    atlas = np.zeros((rows * h2, cols * w2, 3), np.uint8); atlas[..., :2] = 128
    for i, a in enumerate(frames):
        cy, cx = divmod(i, cols)
        atlas[cy * h2:(cy + 1) * h2, cx * w2:(cx + 1) * w2] = a
    Image.fromarray(atlas, 'RGB').save(os.path.join(od, 'flow.png'), optimize=True)
    json.dump({'n': n, 'frame_min': step_min, 'w': w2, 'h': h2, 'cols': cols, 'rows': rows, 'vmax_ms': VMAX, 'cell_m': res * f_out, 'corners': cn,
               'method': 'water-surface slope with Manning n %.2f on %d m blocks, depth-weighted' % (N_MAN, int(res * f_out)), 'sheet': 'flow.png'},
              open(os.path.join(od, 'flow.json'), 'w'), separators=(',', ':'))
    print('  flow', n, 'frames', '%dx%d' % (w2, h2), 'atlas %dx%d' % (cols * w2, rows * h2))


# ---------------------------------------------------------------- build one run
def edge_for(g, S, frames, wm, f):
    box = S.get('box_epsg26986'); res = S['resolution_m'] * f
    if not box or not frames:
        return {}
    shape = frames[0].shape; cells = {}
    for ft in g['features']:
        rc = road_cells(ft['geometry'], box, res, shape)
        if rc is not None: cells[int(ft['properties']['segment'])] = rc
    land = None if wm is None else ~pool(wm.astype(np.uint8), f).astype(bool)
    return edge_intervals(iter(frames), cells, land)


def build(key, src, f, run_dir=None, frame_min=None, do_flow=False, risk_src=None):
    od = os.path.join(OUT, key)
    os.makedirs(od, exist_ok=True)
    S = json.load(open(os.path.join(src, 'summary.json')))
    fh = S['frame_hours']
    snap_min = int(round((fh[1] - fh[0]) * 60)) if len(fh) > 1 else 30
    step = max(1, int(round((frame_min or snap_min) / snap_min)))
    keep = list(range(0, len(fh), step))
    nf, fmin = len(keep), snap_min * step
    wm = None
    if run_dir:
        D = np.load(os.path.join(run_dir, 'frames_cm.npz'))
        wm = np.load(os.path.join(run_dir, 'watermask.npy')).astype(bool) if os.path.exists(os.path.join(run_dir, 'watermask.npy')) else None
        frames = [despeckle(classes_cm(np.where(wm, 0, D['depth_cm'][k]) if wm is not None else D['depth_cm'][k], f)) for k in keep]
    else:
        frames = [despeckle(classes_png(os.path.join(src, 'frames', 'f%03d.png' % k), f)) for k in keep]
    for old in os.listdir(od):
        if re.match(r'depth_\d+\.png$', old):
            os.remove(os.path.join(od, old))
    h, w = frames[0].shape
    sheets = []
    for s in range(0, nf, 9):
        rgb = np.zeros((h, w, 3), np.uint8)
        for j in range(9):
            if s + j < nf:
                rgb[..., j // 3] += frames[s + j] * (1, 5, 25)[j % 3]
        name = 'depth_%02d.png' % (s // 9)
        Image.fromarray(rgb, 'RGB').save(os.path.join(od, name), optimize=True)
        sheets.append(name)
    # continuous depth (with --run-dir): 3 frames per RGB image, v = round(255 * sqrt(h / 3 m)), from 1 cm (v ~ 15), permanent water 0.
    # Lets the map show water gathering from the first centimetre and the true rate of rise or fall, not 4 classes.
    depthc = None
    if run_dir:
        for old in os.listdir(od):
            if re.match(r'depthc_\d+\.png$', old):
                os.remove(os.path.join(od, old))
        dsheets = []
        for s0 in range(0, nf, 3):
            rgb = np.zeros((h, w, 3), np.uint8)
            for j in range(3):
                if s0 + j >= nf:
                    continue
                hm = D['depth_cm'][keep[s0 + j]].astype(np.float32) / 100.0
                if wm is not None:
                    hm = np.where(wm, 0, hm)
                if f > 1:
                    hh, ww = (hm.shape[0] // f) * f, (hm.shape[1] // f) * f
                    hm = hm[:hh, :ww].reshape(hh // f, f, ww // f, f).max(axis=(1, 3))
                v = np.where(hm >= 0.01, np.round(255 * np.sqrt(np.minimum(hm, 3.0) / 3.0)), 0).astype(np.uint8)
                rgb[:v.shape[0], :v.shape[1], j] = v
            name = 'depthc_%03d.png' % (s0 // 3)
            Image.fromarray(rgb, 'RGB').save(os.path.join(od, name), optimize=True)
            dsheets.append(name)
        depthc = {'sheets': dsheets, 'per': 3, 'enc': 'v = 255 * sqrt(depth_m / 3), 1 cm floor, permanent water 0'}

    risk = {}
    for rsrc in (src, risk_src):
        rp = os.path.join(rsrc, 'risk_segments.json') if rsrc else None
        if rp and os.path.exists(rp):
            risk = json.load(open(rp))['segments']; break
    g = json.load(open(os.path.join(src, 'segments.geojson')))
    edge = edge_for(g, S, frames, wm if run_dir else None, f)
    edge_cells = edge
    feats = []
    closed = np.zeros(nf, int)
    for ft in g['features']:
        q = ft['properties']
        d = q.get('d') or []
        d = [d[k] for k in keep if k < len(d)]
        iv = intervals(d)
        sid = str(q['segment'])
        e = risk.get(sid, {})
        may = (q.get('p_may_close') or 0) >= 0.5 and q['p_close'] < 0.5
        if not (q['p_close'] >= 0.5 or may or iv or 'r' in e or (d and max(d) >= 3) or int(q['segment']) in edge_cells):
            continue
        geom = shape(ft['geometry'])
        if geom.geom_type == 'MultiLineString':
            geom = linemerge(geom)
        geom = geom.simplify(0.00003, preserve_topology=False)
        gm = mapping(geom)

        def rnd(x):
            return [round(x[0], 5), round(x[1], 5)]
        if gm['type'] == 'LineString':
            gm = {'type': 'LineString', 'coordinates': [rnd(c) for c in gm['coordinates']]}
        elif gm['type'] == 'MultiLineString':
            gm = {'type': 'MultiLineString', 'coordinates': [[rnd(c) for c in l] for l in gm['coordinates']]}
        else:
            continue
        pr = {'n': q.get('road') or '', 't': q.get('town') or '', 'c': CLS.get(q.get('road_class'), 0),
              'p': round(q['p_close'], 2), 'm': 1 if may else 0, 'w': q.get('why') or ''}
        if iv:
            pr['iv'] = iv
            for a, b in iv:
                closed[int(math.ceil(a)):int(min(nf, math.ceil(b)))] += 1
        if int(q['segment']) in edge:
            pr['e'] = edge[int(q['segment'])]
        if d and max(d) >= 3:
            # depth on the road (cm, capped at 255) every frame; trailing zeros dropped
            dd = [int(min(255, v)) for v in d]
            while dd and dd[-1] == 0:
                dd.pop()
            pr['d'] = dd
        a = e.get('a')
        if a and (a.get('h') or a.get('f') or a.get('p')):
            pr['a'] = [a.get('h', 0), a.get('f', 0), a.get('p', 0), a.get('iso', 0)]
        r = e.get('r')
        if r:
            pr['rk'] = r['risk']
            pr['rc'] = [r['repair'][0], r['repair'][1], r.get('delay', 0)]
        feats.append({'type': 'Feature', 'id': int(q['segment']), 'properties': pr, 'geometry': gm})
    json.dump({'type': 'FeatureCollection', 'features': feats}, open(os.path.join(od, 'roads.json'), 'w'),
              separators=(',', ':'))
    if S.get('box_epsg26986'):
        PC = pieces_build([(ft['id'], ft['geometry']) for ft in feats], S['box_epsg26986'], S['resolution_m'] * f, frames[0].shape, iter(frames),
                          None if wm is None else ~pool(wm.astype(np.uint8), f).astype(bool))
        json.dump(PC, open(os.path.join(od, 'pieces.json'), 'w'), separators=(',', ':'))

    cn = corners(src)
    keep_k = ['segments_in_box', 'segments_p_ge_50', 'km_p_ge_50', 'segments_may_close', 'km_may_close',
              'culverts_overtopped', 'crossings_assessed', 'flood_model_runtime_s', 'resolution_m',
              'rain_max_total_mm', 'rain_peak1h_max_mm', 'solver', 'storm_start']
    meta = {k: S[k] for k in keep_k if k in S}
    cpf = S.get('closed_per_frame', [])
    cpf = [cpf[k] for k in keep] if len(cpf) == len(fh) else closed.tolist()
    meta.update({'key': key, 'source': os.path.relpath(src, ROOT), 'corners': cn, 'frame_min': fmin, 'nf': nf,
                 'w': w, 'h': h, 'pixel_m': S['resolution_m'] * f, 'sheets': sheets,
                 'rain_hourly_mean_mm': S.get('rain_hourly_mean_mm', []),
                 'closed_per_frame': cpf})
    if depthc:
        meta['depthc'] = depthc
    storm = S['run'].split('_')[0]
    t0 = utc(S['storm_start'])
    R = refs(src, cn, storm, t0, fmin, nf, run_dir)
    json.dump(clean(R), open(os.path.join(od, 'refs.json'), 'w'), separators=(',', ':'), allow_nan=False)
    if do_flow and run_dir:
        if os.path.exists(os.path.join(run_dir, 'vel_frames.npz')):   # the solver's own velocity, 60 m blocks, every 10 min
            fk = max(1, int(round(10 / fmin)))
            flow_solver(run_dir, keep[::fk], max(1, int(round(60 / S['resolution_m']))), od, cn, fmin * fk)
        else:
            fk = max(1, int(round(15 / fmin)))           # the flow field changes slowly: one field every 15 min keeps flow.png small
            flow(run_dir, keep[::fk], max(2, int(round(100 / S['resolution_m']))), od, cn, fmin * fk)
        meta['flow'] = 'flow.json'
    json.dump(meta, open(os.path.join(od, 'meta.json'), 'w'), separators=(',', ':'))
    size = sum(os.path.getsize(os.path.join(od, x)) for x in os.listdir(od)) / 1e6
    print(key, 'frames', nf, 'every %d min' % fmin, '%dx%d' % (w, h), 'roads', len(feats), 'gauges', len(R['gauges']),
          'crossings', len(R['crossings']['rows']), 'reports', len(R['reports']), '%.1f MB' % size)


def roads_only(key, src):
    """rebuild roads.json of a published pack from its prototype folder (segments.geojson, summary.json) and its own depth sheets"""
    od = os.path.join(OUT, key); meta = json.load(open(os.path.join(od, 'meta.json')))
    S = json.load(open(os.path.join(src, 'summary.json'))); fh = S['frame_hours']
    snap = int(round((fh[1] - fh[0]) * 60)) if len(fh) > 1 else 30; step = max(1, int(round(meta['frame_min'] / snap)))
    keep = list(range(0, len(fh), step))[:meta['nf']]; f = int(round(meta['pixel_m'] / S['resolution_m']))
    g = json.load(open(os.path.join(src, 'segments.geojson')))
    box = S['box_epsg26986']; cells = {}
    for ft in g['features']:
        rc = road_cells(ft['geometry'], box, S['resolution_m'] * f, (meta['h'], meta['w']))
        if rc is not None: cells[int(ft['properties']['segment'])] = rc
    edge = edge_intervals(sheet_frames(od, meta), cells)
    old = {ft['id']: ft for ft in json.load(open(os.path.join(od, 'roads.json')))['features']}
    feats = []
    for ft in g['features']:
        q = ft['properties']; sid = int(q['segment']); d = q.get('d') or []
        if isinstance(d, str): d = json.loads(d)
        d = [d[k] for k in keep if k < len(d)]
        if sid in old:
            o = old[sid]
            if sid in edge: o['properties']['e'] = edge[sid]
            else: o['properties'].pop('e', None)
            feats.append(o); continue
        if not ((d and max(d) >= 3) or sid in edge): continue
        geom = shape(ft['geometry'])
        if geom.geom_type == 'MultiLineString': geom = linemerge(geom)
        gm = mapping(geom.simplify(0.00003, preserve_topology=False))
        r5 = lambda c: [round(c[0], 5), round(c[1], 5)]
        if gm['type'] == 'LineString': gm = {'type': 'LineString', 'coordinates': [r5(c) for c in gm['coordinates']]}
        elif gm['type'] == 'MultiLineString': gm = {'type': 'MultiLineString', 'coordinates': [[r5(c) for c in l] for l in gm['coordinates']]}
        else: continue
        pr = {'n': q.get('road') or '', 't': q.get('town') or '', 'c': CLS.get(q.get('road_class'), 0), 'p': round(float(q['p_close']), 2), 'm': 0, 'w': q.get('why') or ''}
        if d and max(d) >= 3:
            dd = [int(min(255, v)) for v in d]
            while dd and dd[-1] == 0: dd.pop()
            pr['d'] = dd
        if sid in edge: pr['e'] = edge[sid]
        feats.append({'type': 'Feature', 'id': sid, 'properties': pr, 'geometry': gm})
    json.dump({'type': 'FeatureCollection', 'features': feats}, open(os.path.join(od, 'roads.json'), 'w'), separators=(',', ':'))
    PC = pieces_build([(ft['id'], ft['geometry']) for ft in feats], box, S['resolution_m'] * f, (meta['h'], meta['w']), sheet_frames(od, meta))
    json.dump(PC, open(os.path.join(od, 'pieces.json'), 'w'), separators=(',', ':'))
    print(key, 'pieces', len(PC['seg']), round(os.path.getsize(os.path.join(od, 'pieces.json')) / 1e6, 2), 'MB')
    print(key, 'roads', len(old), '->', len(feats), 'segments,', len(edge), 'with water at the road edge,', round(os.path.getsize(os.path.join(od, 'roads.json')) / 1e6, 2), 'MB')


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--run', help='site key, e.g. leominster_sep2023 (default: all published runs)')
    ap.add_argument('--src', help='prototype.py output folder (default: the published one under docs/proto)')
    ap.add_argument('--run-dir', help="flood model out/ folder (frames_cm.npz, z.npy, ...)")
    ap.add_argument('--frame-min', type=int, help='minutes between frames (default: every snapshot)')
    ap.add_argument('--flow', action='store_true', help='also write the flow field (needs --run-dir)')
    ap.add_argument('--pool', type=int, help='spatial max-pool factor for the depth sheets (default per run: 1, District 3: 4)')
    ap.add_argument('--roads-only', action='store_true', help='rewrite roads.json only (depth sheets read back from the published pack)')
    ap.add_argument('--surface', action='store_true', help='with --run: add surface_mm (box-mean water left on the land per frame) to meta.json')
    ap.add_argument('--despeckle', action='store_true', help='with --roads-only: first clean the published depth sheets (despeckle)')
    a = ap.parse_args()
    if a.surface:
        mp = os.path.join(OUT, a.run, 'meta.json'); m = json.load(open(mp))
        m['surface_mm'] = surface_mm(os.path.join(OUT, a.run), m)
        json.dump(m, open(mp, 'w'), separators=(',', ':')); print(a.run, 'surface_mm max', max(m['surface_mm'])); raise SystemExit
    if a.roads_only and a.despeckle:
        despeckle_pack(os.path.join(OUT, a.run), json.load(open(os.path.join(OUT, a.run, 'meta.json'))))
    if a.roads_only:
        roads_only(a.run, a.src or os.path.join(P, RUNS[a.run][0]))
    elif a.run:
        dsrc, df = RUNS.get(a.run, (None, 1))
        build(a.run, a.src or os.path.join(P, dsrc), a.pool or df, a.run_dir, a.frame_min, a.flow,
              risk_src=os.path.join(P, dsrc) if dsrc else None)
    else:
        for k, (src, f) in RUNS.items():
            build(k, os.path.join(P, src), f)
