"""Infrastructure impact layer for a flood run: what happened on every road segment and at every stream crossing.

    python sim/infra/impacts.py --run runs/sep2023_d3_20m                              # rain-on-grid engine run on HF
    python sim/infra/impacts.py --run runs/fim_sep2023                                 # NOAA HAND-FIM river map
    python sim/infra/impacts.py --run runs/sep2023_d3_20m --run runs/fim_sep2023 --combine   # max of both (on the first run's grid)
    python sim/infra/impacts.py --selftest                                             # offline, synthetic grid / roads / crossings
    options: --local DIR (read runs from DIR/<run> instead of HF), --out DIR, --no-upload, --channels channels30.npz --channels-meta ...

Input run dir (HF dataset mohabeldokla/mass-flood-watch-tiles): meta.json {box, res_m, shape, crs EPSG:26986, t0, frame_min, frames},
hmax.npy (peak depth m); optional z.npy (ground, channels burnt to the bankfull bed) and vmax.npy (peak speed m/s).
Roads: docs/graph_segments.json (the site's 52,698 segments; geo decoded as in sim/colab/w4_flood_gpu.py: per part a flat list of
lon/lat x 1e5 with the first pair absolute and the rest deltas).  Each part is densified to points every res/2 m (w4 samples vertices
only, which skips cells on long straight edges), and every point samples the peak-depth cell:
    max_cm, mean_cm per segment; class  0 passable (< 15 cm)  1 impassable for cars (15-30 cm)  2 dangerous (>= 30 cm, or h*v >= 0.3 m2/s)
    thresholds: NWS 'Turn Around Don't Drown' (6 in / 15 cm reaches the floor of most cars, loss of control and stalling; 1 ft floats
    many vehicles); Pregnolato et al. 2017 depth-disruption curve (speed 0 at 300 mm); Shand et al. 2011 (ARR Project 10) stability
    limits for small passenger cars: 0.3 m still water, DV 0.3 m2/s.
Network knock-on (the site's own logic in docs/v2/index.html, ported): segments of class >= 1 removed (also reported at >= 30 cm, the
site's cut), partly wet segments slowed by the Pregnolato curve; minutes to the nearest hospital (facilities.json snapped to segment
midpoints within 3 km) by multi-source Dijkstra now vs dry: 'cut off' = reachable dry, unreachable now; 'isolated' = 30+ min longer.
Also connected components: dry segments no longer connected to any open major road (cls >= 1) = 'cut from the major network'.
Crossings (docs/network/crossings_all.json, else crossings_ma.json): headwater HW above the inlet invert = peak depth at the channel cell
(largest channels30 drainage area within 60 m, else the deepest cell) - for HAND-FIM maps plus the bankfull depth (their DEM surface is the
lidar water surface, the channel below it is not in the depth); with z.npy and a surveyed invert, HW = z + h - invert.  Crest above the
invert = deck - invert, else rise + road fill, else rise + 0.6 m (assumed cover).  culvert.assess_crossing -> overtopped / surcharged /
ok; without geometry and crest, 'overtopped' when the road within 30 m carries >= 15 cm, else unknown.
Reports: docs/prone/flood_reports.json on the storm days (as sim/validate.py): point hit rate (>= 10 cm within 100 m), segment hit rate
(nearest segment within 100 m impassable), and how many flagged segments have a report within 200 m vs all segments in the box.
Writes impacts.json (+ impacts_seg.bin: uint8 pairs [code, max_cm<=254] per segment, code 0 dry / 1 wet < 15 cm / 2 impassable /
3 dangerous / 4 dry but cut off / 5 isolated (+30 min) / 255 outside the run) and uploads both to runs/<run>/ in ONE commit
(impacts_combined.* with --combine).
"""
import os, sys, json, math, time, argparse, datetime as dt
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.normpath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, HERE)
from culvert import assess_crossing

REPO = 'mohabeldokla/mass-flood-watch-tiles'
T_IMPASSABLE, T_DANGER, DV_DANGER, T_WET = 0.15, 0.30, 0.3, 0.05
D3 = (128000, 856000, 206000, 946000)                    # MassDOT District 3 study box, EPSG:26986
CLASS_KMH = [45, 65, 95]
SEG_COLS = ['seg', 'max_cm', 'mean_cm', 'cls', 'code', 'dv_m2s', 'cut_hosp', 'iso_min', 'cut_major']
X_COLS = ['id', 'lon', 'lat', 'road', 'stream', 'src', 'shape', 'material', 'inlet', 'n_barrels', 'span_m', 'rise_m', 'h_chan_m', 'hw_m', 'hw_from',
          'crest_m', 'crest_assumed', 'freeboard_m', 'road_depth_m', 'hw_rise', 'status', 'basis', 'q_pass_m3s', 'q_cap_crest_m3s', 'q_model_m3s', 'q_ratio', 'coef', 'coef_exact', 'd3']
CITATIONS = dict(
    nws='NOAA National Weather Service, Turn Around Don\'t Drown: "Six inches of water will reach the bottom of most passenger cars causing loss of control and possible stalling. A foot of water will float many vehicles." https://weather.gov/tsa/hydro_tadd',
    pregnolato='Pregnolato M., Ford A., Wilkinson S., Dawson R. (2017) The impact of flooding on road transport: a depth-disruption function. Transportation Research Part D 55, 67-81 (speed 0 at 300 mm)',
    shand='Shand T.D., Cox R.J., Blacka M.J., Smith G.P. (2011) Australian Rainfall and Runoff Project 10: Appropriate safety criteria for vehicles, Stage 2 report P10/S2/020 (small passenger car: 0.3 m still water, DV 0.3 m2/s)',
    hds5='Schall J.D. et al. (2012) Hydraulic Design of Highway Culverts, 3rd ed., FHWA-HIF-12-026 (HDS-5), Appendix A inlet-control equations and constants')

# ---------------- runs ----------------
def load_run(run, local=None):
    """dict(name, meta, H, Z, V, kind) for runs/<name>; local: a directory holding <run> (or the run dir itself)."""
    name = run.rstrip('/').split('/')[-1]; files = {}
    if local:
        d = local if os.path.exists(os.path.join(local, 'meta.json')) else os.path.join(local, run) if os.path.isdir(os.path.join(local, run)) else os.path.join(local, name)
        for f in ('meta.json', 'hmax.npy', 'z.npy', 'vmax.npy'):
            if os.path.exists(os.path.join(d, f)): files[f] = os.path.join(d, f)
    else:
        from huggingface_hub import hf_hub_download
        for f in ('meta.json', 'hmax.npy', 'z.npy', 'vmax.npy'):
            try: files[f] = hf_hub_download(REPO, f'runs/{name}/{f}', repo_type='dataset')
            except Exception as e:
                if f in ('meta.json', 'hmax.npy'): raise RuntimeError(f'runs/{name}/{f}: {e!r}'[:300])
    meta = json.load(open(files['meta.json']))
    ld = lambda f: np.nan_to_num(np.load(files[f]).astype(np.float32), nan=0.0, posinf=0.0, neginf=0.0) if f in files else None
    H = np.maximum(ld('hmax.npy'), 0); kind = 'fim' if name.startswith('fim_') or 'HAND' in str(meta.get('model', '')) else 'rog'
    return dict(name=name, meta=meta, H=H, Z=ld('z.npy'), V=ld('vmax.npy'), kind=kind)

def grid_index(src_meta, dst_meta):
    """Nearest-cell row/col index arrays of src for the dst grid's cell centres, and the inside mask (same CRS, axis aligned)."""
    sx0, sy0, sx1, sy1 = src_meta['box']; sr = src_meta['res_m']; sny, snx = src_meta['shape']
    x0, y0, x1, y1 = dst_meta['box']; r = dst_meta['res_m']; ny, nx = dst_meta['shape']
    rr = np.floor((sy1 - (y1 - (np.arange(ny) + 0.5) * r)) / sr).astype(int); cc = np.floor((x0 + (np.arange(nx) + 0.5) * r - sx0) / sr).astype(int)
    return rr, cc, ((rr >= 0) & (rr < sny))[:, None] & ((cc >= 0) & (cc < snx))[None, :]

def resample(A, src_meta, dst_meta):
    rr, cc, ok = grid_index(src_meta, dst_meta)
    out = A[np.clip(rr, 0, A.shape[0] - 1)][:, np.clip(cc, 0, A.shape[1] - 1)]; return np.where(ok, out, 0).astype(np.float32)

def storm_days(meta):
    if not meta.get('t0'): return set()
    d0 = dt.date.fromisoformat(meta['t0'][:10]); nfr = len(meta.get('frames') or [0]); fm = meta.get('frame_min', 60)
    return {(d0 + dt.timedelta(days=k)).isoformat() for k in range(int(fm * max(nfr - 1, 0) / 1440) + 2)}

# ---------------- roads ----------------
def decode_segments(S):
    """[(seg, lon array, lat array)] for every part, exactly as w4_flood_gpu.py / the site decode 'geo'."""
    out = []
    for i, parts in enumerate(S['geo']):
        for d in parts:
            out.append((i, np.cumsum(d[0::2]) / 1e5, np.cumsum(d[1::2]) / 1e5))
    return out

def densify(parts_xy, step, return_part=False):
    """parts_xy: [(seg, x, y)] projected; points every <= step m along each part (vertices kept). Returns x, y, seg arrays (+ part index)."""
    X, Y, SG, PT = [], [], [], []
    for j, (seg, x, y) in enumerate(parts_xy):
        if len(x) == 1: X.append(x); Y.append(y); SG.append(np.full(1, seg, np.int32)); PT.append(np.full(1, j, np.int32)); continue
        dx, dy = np.diff(x), np.diff(y); k = np.maximum(1, np.ceil(np.hypot(dx, dy) / step).astype(int))
        e = np.repeat(np.arange(len(dx)), k); t = (np.arange(k.sum()) - np.repeat(np.cumsum(k) - k, k)) / np.repeat(k, k)
        X.append(np.r_[x[e] + t * dx[e], x[-1]]); Y.append(np.r_[y[e] + t * dy[e], y[-1]]); SG.append(np.full(len(e) + 1, seg, np.int32)); PT.append(np.full(len(e) + 1, j, np.int32))
    if return_part: return np.concatenate(X), np.concatenate(Y), np.concatenate(SG), np.concatenate(PT)
    return np.concatenate(X), np.concatenate(Y), np.concatenate(SG)

def road_points(S, meta, step=None):
    """Densified road points inside the run box: x, y (EPSG:26986), seg, row, col."""
    from pyproj import Transformer
    x0, y0, x1, y1 = meta['box']; res = meta['res_m']; step = step or res / 2
    inv = Transformer.from_crs(26986, 4326, always_xy=True); tr = Transformer.from_crs(4326, 26986, always_xy=True)
    lo, la = inv.transform([x0, x1, x0, x1], [y0, y0, y1, y1]); m = 0.01
    bb = (min(lo) - m, min(la) - m, max(lo) + m, max(la) + m)
    parts = [(s, lon, lat) for s, lon, lat in decode_segments(S) if lon.max() >= bb[0] and lon.min() <= bb[2] and lat.max() >= bb[1] and lat.min() <= bb[3]]
    if not parts: return dict(x=np.zeros(0), y=np.zeros(0), seg=np.zeros(0, np.int32), r=np.zeros(0, int), c=np.zeros(0, int), end=np.zeros(0, bool), part=np.zeros(0, np.int32))
    lon = np.concatenate([p[1] for p in parts]); lat = np.concatenate([p[2] for p in parts]); X, Y = tr.transform(lon, lat); k = 0; pxy = []
    for s, a, _ in parts: pxy.append((s, X[k:k + len(a)], Y[k:k + len(a)])); k += len(a)
    x, y, sg, pt = densify(pxy, step, return_part=True); c = np.floor((x - x0) / res).astype(int); r = np.floor((y1 - y) / res).astype(int)
    # segment ends: points within one cell of a segment's first / last vertex sit on the junction shared with its neighbours; a flooded
    # junction would otherwise flag every segment meeting there.  sample_segments uses interior points when a segment has any.
    ends = {}
    for s, xs, ys in pxy:
        if s not in ends: ends[s] = [xs[0], ys[0], xs[-1], ys[-1]]
        else: ends[s][2:] = [xs[-1], ys[-1]]
    E = np.array([ends[s] for s in sg]); trim = max(res, 10.0)
    end = (np.hypot(x - E[:, 0], y - E[:, 1]) < trim) | (np.hypot(x - E[:, 2], y - E[:, 3]) < trim)
    ok = (r >= 0) & (r < meta['shape'][0]) & (c >= 0) & (c < meta['shape'][1])
    return dict(x=x[ok], y=y[ok], seg=sg[ok], r=r[ok], c=c[ok], end=end[ok], part=pt[ok])

def road_graph(P, link_tol=2.0):
    """Adjacency of the densified road points as a road network: consecutive points of one part are joined, and points within link_tol m
    of a part's first / last point are joined to it (segments meet at shared vertices; grade-separated crossings share none, so a road
    on a bridge is never joined to the road under it).  Returns (indptr, nbr, dist) CSR arrays."""
    from scipy.sparse import coo_matrix
    from scipy.spatial import cKDTree
    n = len(P['x']); x, y, pt = P['x'], P['y'], P['part']
    if n == 0: return np.zeros(1, np.int64), np.zeros(0, np.int64), np.zeros(0)
    i = np.nonzero(pt[1:] == pt[:-1])[0]; a, b = [i], [i + 1]
    ends = np.nonzero(np.r_[True, pt[1:] != pt[:-1]] | np.r_[pt[1:] != pt[:-1], True])[0]
    pr = cKDTree(np.column_stack([x, y])).query_ball_point(np.column_stack([x[ends], y[ends]]), link_tol)
    ea = np.repeat(ends, [len(v) for v in pr]); eb = np.concatenate([np.asarray(v, np.int64) for v in pr]) if len(pr) else np.zeros(0, np.int64)
    k = ea != eb; a.append(ea[k]); b.append(eb[k]); a = np.concatenate(a); b = np.concatenate(b)
    d = np.maximum(np.hypot(x[a] - x[b], y[a] - y[b]), 0.01)
    M = coo_matrix((np.r_[d, d], (np.r_[a, b], np.r_[b, a])), shape=(n, n)).tocsr(); M.sum_duplicates()
    return M.indptr, M.indices, M.data

def profile_rims(G, z, cand, radius=150.0):
    """Road-profile depressions.  For each candidate point p and each road direction leaving it (graph neighbour q, walking away from p
    along the road up to `radius` m), the highest z met in that direction (the rim).  Returns per candidate: rim = min over directions of
    the rim (the lowest side: a closed depression of the road profile holds water up to it) and ndir = number of directions (>= 2 for a
    closed depression; points stacked at a junction count as separate directions)."""
    indptr, nbr, dist = G; rim = np.full(len(cand), -np.inf); nd = np.zeros(len(cand), np.int32)
    for j, p in enumerate(cand):
        rims = []
        for e in range(indptr[p], indptr[p + 1]):
            q = nbr[e]; best = {q: dist[e]}; stack = [q]; zmax = z[q]
            while stack:
                u = stack.pop(); du = best[u]
                for f in range(indptr[u], indptr[u + 1]):
                    v = nbr[f]; dv = du + dist[f]
                    if v == p or dv > radius or dv >= best.get(v, np.inf): continue
                    best[v] = dv; stack.append(v); zmax = max(zmax, z[v])
            rims.append(zmax)
        if rims: rim[j] = min(rims); nd[j] = len(rims)
    return rim, nd

def route_number(name):
    """Route number in a road name ('I-290' -> 290, 'Route 122' -> 122, 'Main Street (US 2)' -> 2), None for named streets."""
    import re
    m = re.search(r'(?:\bI-|\bRoute |\bRte |\bUS |\bSR )\s*(\d+)', name or ''); return int(m.group(1)) if m else None

def deck_points(P, zc, shape, res, roads, nbi_x, nbi_y, nbi_route, gap=2.0, radius=150.0, nbi_m=100.0, G=None):
    """Road points on a bridge deck that the bare-earth lidar removed.  3DEP bare-earth DEMs drop bridge decks (USGS Lidar Base
    Specification: bridges are removed from the bare-earth surface), so along a road carried on a structure the lidar crest falls to the
    ground or water beneath it.  A point is on such a deck when (1) its lidar crest is >= `gap` m below the road's own crest in BOTH
    directions within `radius` m along the road (a gap in the road profile: profile_rims on road_graph) and (2) an NBI bridge that carries
    this road's route number lies within `nbi_m` m (NBI item 5D, route number on the structure).  (2) keeps underpasses and stream valleys
    out: the road under a bridge has its own route number (or none) and a real sag is not a deck.  G: road_graph(P) if already built.
    Returns a bool mask over P."""
    from scipy.ndimage import maximum_filter
    from scipy.spatial import cKDTree
    n = len(P['x']); out = np.zeros(n, bool)
    rn = np.array([route_number(roads[s]) or 0 for s in range(len(roads))])[P['seg']] if n else np.zeros(0, int)
    if n == 0 or not (rn > 0).any() or len(nbi_x) == 0: return out
    RG = np.full(shape, -np.inf); np.maximum.at(RG, (P['r'], P['c']), zc)
    k = int(radius // res); MF = maximum_filter(RG, size=2 * k + 1, mode='constant', cval=-np.inf)
    nr = np.asarray(nbi_route); T = cKDTree(np.column_stack([nbi_x, nbi_y]))
    cand = np.nonzero((rn > 0) & (zc <= MF[P['r'], P['c']] - gap))[0]
    if len(cand):
        near = T.query_ball_point(np.column_stack([P['x'][cand], P['y'][cand]]), nbi_m)
        cand = cand[np.array([bool(len(nb)) and bool((nr[nb] == rn[i]).any()) for i, nb in zip(cand, near)], bool)]
    if len(cand):
        rim, nd = profile_rims(G or road_graph(P), zc.astype(np.float64), cand, radius)
        out[cand[(nd >= 2) & (rim - zc[cand] >= gap)]] = True
    return out

def closed_depressions(Z, res):
    """Closed depressions of a DEM: (filled surface, depression label per cell, D8 catchment area m2 draining into each label).  Filled =
    pit filling by morphological reconstruction (Soille 2004; the priority-flood result of Barnes et al. 2014); a depression is a connected
    set of cells with filled - Z > 1 mm; a cell's water goes to its steepest-descent (D8) neighbour, and the catchment of a depression is
    every cell whose descent path ends in it (water from upstream pits is not routed on: a lower bound)."""
    from skimage.morphology import reconstruction
    from scipy import ndimage
    Z = Z.astype(np.float64); seed = Z.copy(); seed[1:-1, 1:-1] = Z.max(); F = reconstruction(seed, Z, method='erosion')
    lab, nl = ndimage.label((F - Z) > 1e-3, structure=np.ones((3, 3)))
    ny, nx = Z.shape; idx = np.arange(ny * nx).reshape(ny, nx); Pd = np.pad(Z, 1, constant_values=np.inf); best = np.zeros_like(Z); rec = idx.copy()
    for dr in (-1, 0, 1):
        for dc in (-1, 0, 1):
            if dr or dc:
                s = (Z - Pd[1 + dr:1 + dr + ny, 1 + dc:1 + dc + nx]) / (res * (math.sqrt(2.0) if dr and dc else 1.0)); m = s > best; best[m] = s[m]; rec[m] = (idx + dr * nx + dc)[m]
    rec = rec.ravel()
    for _ in range(64):                                      # pointer jumping to each cell's terminal cell
        r2 = rec[rec]
        if np.array_equal(r2, rec): break
        rec = r2
    area = np.bincount(lab.ravel()[rec], minlength=nl + 1).astype(np.float64) * res * res; area[0] = 0.0
    return F.astype(np.float32), lab, area

def point_depth(P, H):
    """Water depth on the road at each point: the cell depth, less P['dz'] where the road crest stands above the cell's ground (dz = lidar
    crest - model ground, set by proto/prototype.py for Interstates: depth = max(0, water surface - crest))."""
    d = H[P['r'], P['c']]
    return np.maximum(d - P['dz'], 0.0).astype(d.dtype) if 'dz' in P else d

def sample_segments(n, P, H, V=None):
    """Per segment: max depth, mean depth over its sampled points (interior points when it has any), max h*v, in-box flag."""
    cnt_all = np.bincount(P['seg'], minlength=n); ci = np.bincount(P['seg'][~P['end']], minlength=n)
    use = ~P['end'] | (ci[P['seg']] == 0); P = {k: v[use] for k, v in P.items()}
    d = point_depth(P, H); cnt = np.bincount(P['seg'], minlength=n).astype(np.float64)
    mx = np.zeros(n, np.float32); np.maximum.at(mx, P['seg'], d)
    mean = np.bincount(P['seg'], weights=d, minlength=n) / np.maximum(cnt, 1)
    dv = np.zeros(n, np.float32)
    if V is not None: np.maximum.at(dv, P['seg'], d * V[P['r'], P['c']])
    return mx, mean.astype(np.float32), dv, cnt_all > 0

def classify(mx, dv):
    cls = np.zeros(len(mx), np.uint8); cls[mx >= T_IMPASSABLE] = 1; cls[(mx >= T_DANGER) | (dv >= DV_DANGER)] = 2; return cls

# ---------------- network ----------------
def speed_factor(m):
    """Pregnolato et al. 2017 speed ratio by depth (m), as the site's speedFactor (1 below 5 cm, 0 from 30 cm)."""
    d = m * 1000.0; f = np.maximum(0.05, (0.0009 * d * d - 0.5529 * d + 86.94) / 86.94)
    return np.where(m < 0.05, 1.0, np.where(m >= T_DANGER, 0.0, f))

def network(S, mx, blocked, facilities=None):
    """Hospital access (site logic) and major-network connectivity with 'blocked' segments removed."""
    from scipy.sparse import csr_matrix
    from scipy.sparse.csgraph import dijkstra, connected_components
    n = S['n']; L = np.asarray(S['links'], np.int64).reshape(-1, 2) if len(S['links']) else np.zeros((0, 2), np.int64)
    a = np.r_[L[:, 0], L[:, 1]]; b = np.r_[L[:, 1], L[:, 0]]
    cls = np.asarray(S['props']['cls']); ln = np.asarray([v or 30 for v in S['props']['len']], float)
    t0 = ln / 1000.0 / np.array(CLASS_KMH)[np.minimum(cls, 2)] * 60.0
    out = dict(cut_hosp=np.zeros(n, bool), iso_min=np.zeros(n, np.float32), cut_major=np.zeros(n, bool), hospitals=0)
    # major-network connectivity (the site's reach(): BFS from every open major segment)
    def reach(blk):
        k = ~blk[a] & ~blk[b]; G = csr_matrix((np.ones(k.sum()), (a[k], b[k])), shape=(n, n)); _, lab = connected_components(G, directed=False)
        good = np.unique(lab[(cls >= 1) & ~blk]); return np.isin(lab, good) & ~blk
    base = reach(np.zeros(n, bool)); now = reach(blocked); out['cut_major'] = base & ~now & ~blocked
    # hospital access
    if facilities:
        from scipy.spatial import cKDTree
        from pyproj import Transformer
        tr = Transformer.from_crs(4326, 26986, always_xy=True)
        mids = []
        for parts in S['geo']:
            d = parts[0]; lon = np.cumsum(d[0::2]) / 1e5; lat = np.cumsum(d[1::2]) / 1e5; j = len(lon) // 2; mids.append((lon[j], lat[j]))
        mx_, my_ = tr.transform(*np.array(mids).T); tree = cKDTree(np.column_stack([mx_, my_]))
        hx, hy = tr.transform(*np.array([(h[0], h[1]) for h in facilities]).T); dd, ii = tree.query(np.column_stack([hx, hy]))
        src = np.unique(ii[dd < 3000]); out['hospitals'] = int(len(src))
        if len(src):
            def dist(mult):
                w = t0[b] * mult[b]; k = np.isfinite(w); G = csr_matrix((w[k], (a[k], b[k])), shape=(n, n))
                return dijkstra(G, directed=True, indices=src, min_only=True)
            mult0 = np.ones(n); f = speed_factor(mx); mult = np.where(blocked | (f <= 0), np.inf, 1.0 / np.maximum(f, 1e-6))
            d0 = dist(mult0); d1 = dist(mult)
            out['cut_hosp'] = np.isfinite(d0) & ~np.isfinite(d1) & ~blocked
            with np.errstate(invalid='ignore'): out['iso_min'] = np.where(np.isfinite(d0) & np.isfinite(d1) & ~blocked, d1 - d0, 0).astype(np.float32)
    return out

# ---------------- crossings ----------------
def load_crossings(path=None):
    for p in ([path] if path else []) + [os.path.join(ROOT, 'docs', 'network', 'crossings_all.json'), os.path.join(ROOT, 'docs', 'network', 'crossings_ma.json')]:
        if p and os.path.exists(p):
            X = json.load(open(p)); C = X['columns']; return [dict(zip(C, r)) for r in X['rows']], os.path.basename(p)
    return [], None

def channel_cell(H, r, c, x, y, meta, A=None, radius=60.0):
    """(row, col) of the crossing's channel cell: largest drainage area within radius (nearest among cells within 20 % of it), else deepest."""
    x0, y0, x1, y1 = meta['box']; res = meta['res_m']; ny, nx = H.shape; k = int(math.ceil(radius / res))
    r0, r1, c0, c1 = max(0, r - k), min(ny, r + k + 1), max(0, c - k), min(nx, c + k + 1)
    rr, cc = np.mgrid[r0:r1, c0:c1]; d = np.hypot(x0 + (cc + 0.5) * res - x, y1 - (rr + 0.5) * res - y); win = d <= radius
    if A is not None and (A[r0:r1, c0:c1][win] > 0).any():
        sc = np.where(win, A[r0:r1, c0:c1], -1.0); best = sc >= 0.8 * sc.max()
    else:
        sc = np.where(win, H[r0:r1, c0:c1], -1.0); best = sc >= sc.max() - 1e-3
    i = int(np.argmin(np.where(best, d, np.inf))); return int(rr.ravel()[i]), int(cc.ravel()[i])

def crossing_headwater(x, y, row, run, ch=None):
    """(HW m above the invert, h at the channel cell, how) for one run; None outside the run."""
    meta = run['meta']; x0, y0, x1, y1 = meta['box']; res = meta['res_m']; H = run['H']
    r, c = int(math.floor((y1 - y) / res)), int(math.floor((x - x0) / res))
    if not (0 <= r < H.shape[0] and 0 <= c < H.shape[1]): return None
    cr, cc = channel_cell(H, r, c, x, y, meta, None if ch is None else ch['area'])
    h = float(H[cr, cc]); inv = row.get('usie_m')
    if run['Z'] is not None and inv is not None and run['kind'] == 'rog':
        return max(0.0, float(run['Z'][cr, cc]) + h - float(inv)), h, 'wse-invert', (cr, cc), float(run['Z'][cr, cc]) + h
    if run['kind'] == 'fim':
        bfd = row.get('bf_d')
        if not bfd and ch is not None and ch.get('depth') is not None: bfd = float(ch['depth'][cr, cc]) or None
        if not bfd:
            A = row.get('drn_km2') or (float(ch['area'][cr, cc]) if ch is not None else None)
            bfd = 0.30 * A ** 0.213 if A else 0.0                                   # Bieger et al. 2015 bankfull depth, as channels_grid.py
        return (h + float(bfd)) if h > 0 else 0.0, h, 'depth+bankfull', (cr, cc), None
    return h, h, 'depth', (cr, cc), (float(run['Z'][cr, cc]) + h) if run['Z'] is not None else None

def assess_crossings(Xrows, runs, P, seg_depth_pts, ch_by_run=None):
    from pyproj import Transformer
    from scipy.spatial import cKDTree
    tr = Transformer.from_crs(4326, 26986, always_xy=True); out = []
    meta = runs[0]['meta']; x0, y0, x1, y1 = meta['box']
    tree = cKDTree(np.column_stack([P['x'], P['y']])) if len(P['x']) else None
    for row in Xrows:
        if row.get('lon') is None: continue
        x, y = tr.transform(row['lon'], row['lat'])
        if not (x0 <= x < x1 and y0 <= y < y1): continue
        best = None; q_model = None; wse = None
        for k, run in enumerate(runs):
            ch = (ch_by_run or {}).get(run['name'])
            hw = crossing_headwater(x, y, row, run, ch)
            if hw is None: continue
            if best is None or hw[0] > best[0]: best = hw + (run,)
            if hw[4] is not None: wse = hw[4] if wse is None else max(wse, hw[4])
            if run['V'] is not None and hw[1] > 0:
                W = row.get('bf_w') or (float(ch['width'][hw[3]]) if ch is not None else None)
                if W: q_model = max(q_model or 0.0, hw[1] * float(run['V'][hw[3]]) * float(W))
        if best is None: continue
        hwm, h, how = best[0], best[1], best[2]
        rd = None
        if tree is not None:
            ii = tree.query_ball_point([x, y], 30.0)
            if ii: rd = float(seg_depth_pts[ii].max())
        shape, rise, span, fill = row.get('shape'), row.get('rise_m'), row.get('span_m'), row.get('fill_m')
        deck, inv = row.get('deck_m'), row.get('usie_m'); crest, assumed = None, 0
        if deck is not None and inv is not None and deck > inv: crest = float(deck) - float(inv)
        elif rise and shape != 'bridge': crest = float(rise) + (float(fill) if fill is not None else 0.6); assumed = int(fill is None)
        geom_shape = shape if shape in ('circular', 'elliptical', 'pipe_arch', 'box', 'arch_open', 'arch_closed') else None
        a = assess_crossing(hwm, geom_shape, span, rise if geom_shape else None, row.get('material'), row.get('inlet'), row.get('n_barrels') or 1, crest, q_model=q_model)
        fb = None if (deck is None or wse is None) else round(float(deck) - wse, 2)          # deck freeboard from the modelled water surface (needs z.npy)
        if a['status'] in ('unknown', 'ok') and fb is not None and fb < 0: a.update(status='overtopped', basis='deck')
        elif a['status'] == 'unknown' and fb is not None: a.update(status='ok', basis='deck')     # below the deck; surcharge unknown without geometry
        if a['status'] == 'unknown' and rd is not None and rd >= T_IMPASSABLE: a.update(status='overtopped', basis='road')
        d3 = int(D3[0] <= x < D3[2] and D3[1] <= y < D3[3])
        out.append([row.get('id') or row.get('naacc'), row['lon'], row['lat'], row.get('road'), row.get('stream'), row.get('src'), shape, row.get('material'), row.get('inlet'),
                    row.get('n_barrels'), span, rise, round(h, 3), round(hwm, 3), how, None if crest is None else round(crest, 2), assumed, fb, None if rd is None else round(rd, 3),
                    a['hw_rise'], a['status'], a['basis'], a['q_pass_m3s'], a['q_cap_crest_m3s'], None if q_model is None else round(q_model, 3), a.get('q_ratio'), a['coef'], a['coef_exact'], d3])
    return out

# ---------------- reports ----------------
def score_reports(reports, days, H, meta, P, cls, inbox, mx=None):
    from pyproj import Transformer
    from scipy.spatial import cKDTree
    tr = Transformer.from_crs(4326, 26986, always_xy=True); x0, y0, x1, y1 = meta['box']; res = meta['res_m']; ny, nx = H.shape
    R = reports['rows']; lon = np.array([r[0] for r in R]); lat = np.array([r[1] for r in R]); X, Y = tr.transform(lon, lat)
    inb = (X >= x0) & (X < x1) & (Y >= y0) & (Y < y1); storm = np.array([r[2] in days for r in R]) & inb
    k = int(math.ceil(100 / res))
    def near(x, y):
        c, r = int((x - x0) // res), int((y1 - y) // res); return float(H[max(0, r - k):r + k + 1, max(0, c - k):c + k + 1].max())
    pt = [near(X[i], Y[i]) >= 0.1 for i in np.nonzero(storm)[0]]
    rng = np.random.default_rng(0); idx = np.nonzero(inb)[0]; idx = rng.choice(idx, min(3000, len(idx)), replace=False) if len(idx) else idx
    rnd = [near(X[i], Y[i]) >= 0.1 for i in idx]
    out = dict(storm_days=sorted(days), n_storm_day=int(storm.sum()), point_hit_rate=round(float(np.mean(pt)), 3) if pt else None,
               point_any_day_rate=round(float(np.mean(rnd)), 3) if rnd else None)
    if len(P['x']):
        tree = cKDTree(np.column_stack([P['x'], P['y']])); d, i = tree.query(np.column_stack([X[storm], Y[storm]]))
        m = d <= 100; seg = P['seg'][i[m]]
        out.update(n_storm_day_near_road=int(m.sum()), segment_hit_rate=round(float((cls[seg] >= 1).mean()), 3) if m.any() else None,
                   segment_wet10_rate=round(float((mx[seg] >= 0.10).mean()), 3) if (m.any() and mx is not None) else None)
        # flagged segments with a storm-day report within 200 m vs all in-box segments (lift > 1: flags concentrate where people reported flooding)
        if storm.any():
            rt = cKDTree(np.column_stack([X[storm], Y[storm]])); dd, _ = rt.query(np.column_stack([P['x'], P['y']]))
            near_seg = np.zeros(len(cls), bool); near_seg[np.unique(P['seg'][dd <= 200])] = True
            fl = inbox & (cls >= 1); base = near_seg[inbox].mean() if inbox.any() else 0
            out.update(flagged_segments=int(fl.sum()), flagged_with_report_200m=round(float(near_seg[fl].mean()), 3) if fl.any() else None,
                       all_segments_with_report_200m=round(float(base), 3), lift=round(float(near_seg[fl].mean() / base), 2) if fl.any() and base > 0 else None)
    return out

# ---------------- main ----------------
def analyse(runs, S, Xrows, reports=None, facilities=None, ch_by_run=None, combine=False):
    base = runs[0]; meta = base['meta']; H = base['H'].copy(); V = base['V']; src_name = [base['name']]
    if combine:
        for r in runs[1:]:
            H = np.maximum(H, resample(r['H'], r['meta'], meta)); src_name.append(r['name'])
    n = S['n']; P = road_points(S, meta); mx, mean, dv, inbox = sample_segments(n, P, H, V)
    cls = classify(mx, dv); cls[~inbox] = 0
    blocked = inbox & (cls >= 1); net = network(S, np.where(inbox, mx, 0), blocked, facilities)
    blocked30 = inbox & (mx >= T_DANGER); net30 = network(S, np.where(inbox, mx, 0), blocked30, None)
    code = np.full(n, 255, np.uint8); code[inbox] = 0; code[inbox & (mx >= T_WET)] = 1; code[inbox & (cls == 1)] = 2; code[inbox & (cls == 2)] = 3
    code[(net['iso_min'] >= 30) & (code <= 1)] = 5; code[(net['cut_hosp'] | net['cut_major']) & ((code <= 1) | (code == 255))] = 4
    cmv = np.clip(np.round(mx * 100), 0, 254).astype(np.uint8); cmv[code == 255] = 255
    seg_bin = np.column_stack([code, cmv]).astype(np.uint8).ravel()
    keep = np.nonzero(inbox & ((mx >= T_WET) | net['cut_hosp'] | net['cut_major'] | (net['iso_min'] >= 30)) | net['cut_hosp'] | net['cut_major'])[0]
    seg_rows = [[int(i), int(round(float(mx[i]) * 100)), int(round(float(mean[i]) * 100)), int(cls[i]), int(code[i]), round(float(dv[i]), 3),
                 int(net['cut_hosp'][i]), round(float(net['iso_min'][i]), 1), int(net['cut_major'][i])] for i in keep]
    rd_pts = point_depth(P, H) if len(P['x']) else np.zeros(0)
    X = assess_crossings(Xrows, runs if combine else [base], P, rd_pts, ch_by_run)
    ln = np.asarray([v or 0 for v in S['props']['len']], float) / 1000
    st = {s: sum(1 for x in X if x[X_COLS.index('status')] == s) for s in ('overtopped', 'surcharged', 'ok', 'unknown')}
    summary = dict(segments_in_run=int(inbox.sum()), passable=int((inbox & (cls == 0)).sum()), impassable_cars=int((cls == 1).sum()), dangerous=int((cls == 2).sum()),
                   km_impassable_or_worse=round(float(ln[cls >= 1].sum()), 1), wet_ge_10cm=int((inbox & (mx >= 0.10)).sum()),
                   cut_off_from_hospitals=int(net['cut_hosp'].sum()), isolated_30min=int((net['iso_min'] >= 30).sum()), worst_delay_min=round(float(net['iso_min'].max()), 1),
                   cut_from_major_network=int(net['cut_major'].sum()), cut_from_major_network_at_30cm=int(net30['cut_major'].sum()), hospitals_snapped=net['hospitals'],
                   crossings_in_run=len(X), crossings=st, crossings_with_geometry=int(sum(1 for x in X if x[X_COLS.index('hw_rise')] is not None)),
                   crossings_d3=int(sum(1 for x in X if x[X_COLS.index('d3')])))
    days = set()
    for r in (runs if combine else [base]): days |= storm_days(r['meta'])
    if reports and days: summary['reports'] = score_reports(reports, days, H, meta, P, cls, inbox, mx)
    return dict(run=base['name'], sources=src_name, combined=bool(combine), kinds=[r['kind'] for r in (runs if combine else [base])], res_m=meta['res_m'], box=meta['box'],
                made=time.strftime('%Y-%m-%d'), claim_level='L2 hydraulic/traffic state from the modelled peak depth; not a structural failure prediction',
                thresholds=dict(impassable_m=T_IMPASSABLE, dangerous_m=T_DANGER, dangerous_dv_m2s=DV_DANGER, wet_m=T_WET, cut_rule='segments with class >= 1 removed; cut_from_major_network_at_30cm repeats it at the site\'s 30 cm'),
                citations=CITATIONS, summary=summary, seg_columns=SEG_COLS, seg_rows=seg_rows,
                seg_array=dict(file='impacts_combined_seg.bin' if combine else 'impacts_seg.bin', dtype='uint8', layout='n x [code, max_cm]', n=n,
                               codes={'0': 'dry', '1': 'wet < 15 cm, passable', '2': 'impassable for cars 15-30 cm', '3': 'dangerous >= 30 cm or h*v >= 0.3', '4': 'dry but cut off (hospitals or major network)', '5': 'nearest hospital 30+ min further', '255': 'outside the run'},
                               max_cm='peak depth cm, 254 = 2.54 m or more, 255 = outside'),
                crossing_columns=X_COLS, crossings=X), seg_bin

def upload(out_dir, run, files):
    from huggingface_hub import HfApi, CommitOperationAdd
    ops = [CommitOperationAdd(path_in_repo=f'runs/{run}/{f}', path_or_fileobj=os.path.join(out_dir, f)) for f in files]
    HfApi().create_commit(REPO, repo_type='dataset', operations=ops, commit_message=f'runs/{run}: infrastructure impacts ({", ".join(files)})')   # one commit (HF: 128 commits/hour)
    print('uploaded', files, 'to', f'runs/{run}/')

def main(a):
    S = json.load(open(a.segments)); Xrows, xsrc = load_crossings(a.crossings)
    reports = json.load(open(a.reports)) if os.path.exists(a.reports) else None
    fac = json.load(open(a.facilities))['facilities']['hospital'] if os.path.exists(a.facilities) else None
    runs = [load_run(r, a.local) for r in a.run]
    groups = [runs] if a.combine else [[r] for r in runs]
    for g in groups:
        ch_by_run = {}
        for r in g:
            try:
                sys.path.insert(0, os.path.join(HERE, '..'))
                from crossings_capacity import load_channels
                if a.channels: cp, cm = a.channels, a.channels_meta
                elif not a.local:
                    from huggingface_hub import hf_hub_download
                    cp = hf_hub_download(REPO, 'data/channels30/channels30.npz', repo_type='dataset'); cm = hf_hub_download(REPO, 'data/channels30/channels30_meta.json', repo_type='dataset')
                else: cp = None
                if cp:
                    ch = load_channels(cp, cm, r['meta'])
                    try:
                        D = np.load(cp); M = json.load(open(cm)); ch['depth'] = resample(D['depth'].astype(np.float32), M, r['meta']) if 'depth' in D else None
                    except Exception: ch['depth'] = None
                    ch_by_run[r['name']] = ch
            except Exception as e: print('no channel grid for', r['name'], repr(e)[:120])
        out, seg_bin = analyse(g, S, Xrows, reports, fac, ch_by_run, combine=a.combine)
        out['crossings_source'] = xsrc
        od = a.out or os.path.join('/tmp', 'impacts', g[0]['name']); os.makedirs(od, exist_ok=True)
        jn = 'impacts_combined.json' if a.combine else 'impacts.json'; bn = out['seg_array']['file']
        json.dump(out, open(os.path.join(od, jn), 'w'), separators=(',', ':'), allow_nan=False); seg_bin.tofile(os.path.join(od, bn))
        print(json.dumps(out['summary'], indent=1)); print('wrote', os.path.join(od, jn), os.path.join(od, bn))
        if not a.no_upload: upload(od, g[0]['name'], [jn, bn])

# ---------------- selftest ----------------
def selftest():
    import tempfile
    from pyproj import Transformer
    inv = Transformer.from_crs(26986, 4326, always_xy=True)
    root = tempfile.mkdtemp(); res = 20; ny = nx = 200; x0, y0 = 150000.0, 900000.0; x1, y1 = x0 + nx * res, y0 + ny * res
    meta = dict(run='st_rog', box=[x0, y0, x1, y1], res_m=res, shape=[ny, nx], crs='EPSG:26986', t0='2023-09-11T00:00', frame_min=60, frames=list(range(25)))
    H = np.zeros((ny, nx), np.float32); row = 100; yr = y1 - (row + 0.5) * res                      # road A along grid row 100
    col = lambda x: int((x - x0) // res)
    H[row - 1:row + 2, col(x0 + 1400):col(x0 + 2000)] = 0.5                                           # seg2 dangerous
    H[row - 1:row + 2, col(x0 + 2600):col(x0 + 3200)] = 0.2                                           # seg4 impassable
    H[row - 1:row + 2, col(x0 + 800):col(x0 + 1400)] = 0.08                                            # seg1 wet, passable (slowed)
    H[row + 1, col(x0 + 1710)] = 2.0                                                                    # C1 channel cell under seg2
    yC2 = y0 + 1000; H[int((y1 - yC2) // res), col(x0 + 3000)] = 1.2                                   # C2 channel, away from roads
    yC3 = y0 + 600; H[int((y1 - yC3) // res), col(x0 + 1000)] = 0.5                                    # C3 channel
    d = os.path.join(root, 'st_rog'); os.makedirs(d); np.save(f'{d}/hmax.npy', H.astype(np.float16)); json.dump(meta, open(f'{d}/meta.json', 'w'))
    np.save(f'{d}/z.npy', np.full((ny, nx), 100.0, np.float32))                                        # flat ground at 100 m for the deck check
    # a HAND-FIM map on a 30 m grid: 0.3 m at C3's channel, 0.4 m on seg5
    fm = dict(run='fim_st', box=[x0 - 300, y0 - 300, x1 + 300, y1 + 300], res_m=30, shape=[int((ny * res + 600) / 30), int((nx * res + 600) / 30)], crs='EPSG:26986', t0='2023-09-11T00:00', frame_min=60, frames=[0],
              model='NOAA NWM -> OWP HAND-FIM')
    HF_ = np.zeros(fm['shape'], np.float32); fr = lambda y: int((fm['box'][3] - y) // 30); fc = lambda x: int((x - fm['box'][0]) // 30)
    HF_[fr(yC3), fc(x0 + 1000)] = 0.3; HF_[fr(yr) - 1:fr(yr) + 2, fc(x0 + 3300):fc(x0 + 3700)] = 0.4
    d = os.path.join(root, 'fim_st'); os.makedirs(d); np.save(f'{d}/hmax.npy', HF_); json.dump(fm, open(f'{d}/meta.json', 'w'))
    # roads: seg0..seg5 a chain along row 100 (600 m each, seg0 major + hospital), seg6 unlinked, seg7 far away (outside the run)
    def enc(pts):
        ll = [inv.transform(x, y) for x, y in pts]; q = [(round(lo * 1e5), round(la * 1e5)) for lo, la in ll]; flat = [q[0][0], q[0][1]]
        for (a1, b1), (a2, b2) in zip(q, q[1:]): flat += [a2 - a1, b2 - b1]
        return [flat]
    geo = [enc([(x0 + 200 + 600 * k, yr), (x0 + 500 + 600 * k, yr), (x0 + 800 + 600 * k, yr)]) for k in range(6)]
    geo.append(enc([(x0 + 1000, y0 + 3600), (x0 + 1500, y0 + 3600)])); geo.append(enc([(x0 + 50000, y0), (x0 + 50500, y0)]))
    S = dict(n=8, geo=geo, links=[[0, 1], [1, 2], [2, 3], [3, 4], [4, 5]], props=dict(road=['A'] * 8, town=['T'] * 8, cls=[1, 0, 0, 0, 0, 0, 0, 0], low=[0] * 8, len=[600] * 8, aadt=[1000] * 8))
    hosp = [list(inv.transform(x0 + 450, yr + 50)) + ['Test Hospital']]
    # crossings
    def X(id_, x, y, **kw):
        lon, lat = inv.transform(x, y); r = dict(id=id_, lon=lon, lat=lat, src='T', d3=1); r.update(kw); return r
    Xrows = [X('C1', x0 + 1710, yr, shape='circular', material='concrete', inlet='headwall', rise_m=1.0, span_m=1.0, fill_m=0.5),
             X('C2', x0 + 3000, yC2, shape='circular', material='metal', inlet='projecting', rise_m=1.0, span_m=1.0, fill_m=1.0),
             X('C3', x0 + 1000, yC3, shape='box', material='concrete', inlet='wingwall', rise_m=1.5, span_m=2.0, fill_m=1.0, bf_d=1.5),
             X('C4', x0 + 2900, yr), X('C5', x0 + 90000, y0), X('C6', x0 + 3000, yC2 + 20, deck_m=100.5), X('C7', x0 + 1000, yC3 + 20, deck_m=101.0)]
    reports = dict(cols=['lon', 'lat', 'date', 'source'], rows=[list(inv.transform(x0 + 1700, yr + 10)) + ['2023-09-11', 't'], list(inv.transform(x0 + 3500, yr)) + ['2023-09-12', 't'],
                                                               list(inv.transform(x0 + 1700, yr)) + ['2020-01-01', 't']])
    ok = True
    def check(name, cond, detail=''):
        nonlocal ok; ok &= bool(cond); print(('PASS ' if cond else 'FAIL ') + name, detail)
    # geometry decode = w4 decode
    lon, lat = decode_segments(S)[0][1:]; check('geo decode (first vertex)', abs(lon[0] - inv.transform(x0 + 200, yr)[0]) < 2e-5 and len(lon) == 3)
    xs, ys, sg = densify([(0, np.array([0.0, 100.0]), np.array([0.0, 0.0]))], 10.0); check('densify every res/2', len(xs) == 11 and abs(xs[-1] - 100) < 1e-9)
    runs = [load_run('st_rog', root)]
    out, sb = analyse(runs, S, Xrows, reports, hosp)
    sr = {r[0]: dict(zip(SEG_COLS, r)) for r in out['seg_rows']}; code = sb.reshape(-1, 2)[:, 0]; cm = sb.reshape(-1, 2)[:, 1]
    check('seg2 dangerous (50 cm)', sr[2]['cls'] == 2 and sr[2]['max_cm'] == 50 and code[2] == 3, sr.get(2))
    check('seg4 impassable (20 cm)', sr[4]['cls'] == 1 and code[4] == 2, sr.get(4))
    check('seg1 wet but passable (8 cm), mean < max', sr[1]['cls'] == 0 and code[1] == 1 and sr[1]['mean_cm'] <= sr[1]['max_cm'], sr.get(1))
    check('seg3 and seg5 dry but cut off from the hospital and the major network', sr[3]['cut_hosp'] == 1 and sr[5]['cut_hosp'] == 1 and sr[3]['cut_major'] == 1 and code[3] == 4 and code[5] == 4, (sr.get(3), sr.get(5)))
    check('seg0 open, seg6 never connected (not cut), seg7 outside', code[0] == 0 and code[6] == 0 and code[7] == 255 and cm[7] == 255, code)
    S_ = out['summary']; check('summary counts', S_['dangerous'] == 1 and S_['impassable_cars'] == 1 and S_['cut_off_from_hospitals'] == 2 and S_['segments_in_run'] == 7, S_)
    check('at the site\'s 30 cm only seg2 blocks: seg3-5 cut from the major network', S_['cut_from_major_network_at_30cm'] == 3, S_['cut_from_major_network_at_30cm'])
    xr = {x[0]: dict(zip(X_COLS, x)) for x in out['crossings']}
    check('C1 overtopped (HW 2.0 > crest 1.5)', xr['C1']['status'] == 'overtopped' and xr['C1']['hw_m'] == 2.0 and xr['C1']['crest_m'] == 1.5, xr['C1'])
    check('C2 surcharged (HW/D 1.2)', xr['C2']['status'] == 'surcharged' and xr['C2']['hw_rise'] == 1.2, xr['C2'])
    check('C3 ok (HW/D 0.33)', xr['C3']['status'] == 'ok' and abs(xr['C3']['hw_rise'] - 0.333) < 0.01, xr['C3'])
    check('C4 no geometry -> overtopped from the road depth', xr['C4']['status'] == 'overtopped' and xr['C4']['basis'] == 'road', xr['C4'])
    check('C5 outside the run dropped', 'C5' not in xr and S_['crossings_in_run'] == 6)
    check('C6 deck only: WSE 101.2 > deck 100.5 -> overtopped (deck)', xr['C6']['status'] == 'overtopped' and xr['C6']['basis'] == 'deck' and xr['C6']['freeboard_m'] == -0.7, xr['C6'])
    check('C7 deck only: WSE 100.5 < deck 101 -> ok (deck)', xr['C7']['status'] == 'ok' and xr['C7']['basis'] == 'deck' and xr['C7']['freeboard_m'] == 0.5, xr['C7'])
    rp = S_['reports']; check('reports: storm days and segment hit rate 1/2', rp['n_storm_day'] == 2 and rp['segment_hit_rate'] == 0.5 and rp['point_hit_rate'] == 0.5 and '2023-09-12' in rp['storm_days'], rp)
    # combined with the HAND-FIM map
    runs2 = [load_run('st_rog', root), load_run('fim_st', root)]; check('fim run detected', runs2[1]['kind'] == 'fim')
    out2, sb2 = analyse(runs2, S, Xrows, reports, hosp, combine=True)
    sr2 = {r[0]: dict(zip(SEG_COLS, r)) for r in out2['seg_rows']}; xr2 = {x[0]: dict(zip(X_COLS, x)) for x in out2['crossings']}
    check('combine: seg5 dangerous from the river map (40 cm)', sr2[5]['cls'] == 2 and sb2.reshape(-1, 2)[5, 0] == 3, sr2.get(5))
    check('combine: C3 HW = 0.3 m FIM depth + 1.5 m bankfull -> surcharged', xr2['C3']['status'] == 'surcharged' and abs(xr2['C3']['hw_m'] - 1.8) < 1e-6 and xr2['C3']['hw_from'] == 'depth+bankfull', xr2['C3'])
    check('combine: seg-array file name', out2['seg_array']['file'] == 'impacts_combined_seg.bin' and len(sb2) == 16)
    json.dumps(out, allow_nan=False); json.dumps(out2, allow_nan=False); check('JSON has no NaN', True)
    # CLI end to end, local, no upload
    class A: pass
    a = A(); a.segments = os.path.join(root, 'S.json'); json.dump(S, open(a.segments, 'w')); a.crossings = os.path.join(root, 'X.json')
    json.dump(dict(columns=list(Xrows[0].keys()) + ['material', 'inlet', 'rise_m', 'span_m', 'fill_m', 'shape', 'bf_d'], rows=[]), open(a.crossings, 'w'))
    a.reports = os.path.join(root, 'none.json'); a.facilities = os.path.join(root, 'none.json'); a.local = root; a.run = ['runs/st_rog']; a.combine = False
    a.channels = None; a.channels_meta = None; a.out = os.path.join(root, 'out'); a.no_upload = True
    main(a); check('CLI wrote impacts.json + impacts_seg.bin', os.path.exists(os.path.join(a.out, 'impacts.json')) and os.path.getsize(os.path.join(a.out, 'impacts_seg.bin')) == 16)
    # road profile: two parts meeting at a shared vertex form one road; a 60 m gap 5 m deep (deck removed) on 'I-9'
    xs1, ys1, sg1, pt1 = densify([(0, np.array([0.0, 200.0]), np.array([0.0, 0.0])), (1, np.array([200.0, 400.0]), np.array([0.0, 0.0]))], 10.0, return_part=True)
    Pp = dict(x=xs1, y=ys1, seg=sg1, part=pt1, r=np.zeros(len(xs1), int), c=np.minimum((xs1 // 20).astype(int), 19), end=np.zeros(len(xs1), bool))
    G = road_graph(Pp); check('road graph joins parts at the shared vertex', np.diff(G[0]).min() >= 1 and (np.diff(G[0]) >= 2).sum() >= len(xs1) - 2)
    zp = np.full(len(xs1), 100.0); gap = (xs1 > 170) & (xs1 < 230); zp[gap] = 95.0
    rim, nd = profile_rims(G, zp, np.nonzero(gap)[0], 150.0); check('profile rims: gap 5 m below both sides', np.allclose(rim - zp[gap], 5.0) and (nd >= 2).all(), (rim, nd))
    rim, nd = profile_rims(G, zp, np.array([0]), 150.0); check('profile rims: road end has one direction', nd[0] == 1)
    dk = deck_points(Pp, zp, (1, 20), 20.0, ['I-9', 'I-9'], np.array([200.0]), np.array([5.0]), [9])
    check('deck: gap under an NBI bridge of the same route', dk[gap].all() and not dk[~gap].any(), dk.sum())
    check('deck: NBI bridge of another route -> not a deck', not deck_points(Pp, zp, (1, 20), 20.0, ['I-9', 'I-9'], np.array([200.0]), np.array([5.0]), [7]).any())
    check('deck: named street (no route number) -> never', not deck_points(Pp, zp, (1, 20), 20.0, ['Main Street', 'Main Street'], np.array([200.0]), np.array([5.0]), [0]).any())
    zs = zp.copy(); zs[gap] = 99.5; check('deck: 0.5 m sag is not a deck', not deck_points(Pp, zs, (1, 20), 20.0, ['I-9', 'I-9'], np.array([200.0]), np.array([5.0]), [9]).any())
    check('route numbers', route_number('I-290') == 290 and route_number('Route 12 (Main Street)') == 12 and route_number('Main Street (US 2)') == 2 and route_number('Elm Street') is None)
    Zb = np.full((9, 9), 10.0); Zb[3:6, 3:6] = 9.0; Zb[4, 4] = 8.5; Zb[:, 8] = 5.0           # a bowl; the east column is lower (drains off)
    Fb, lb, ab = closed_depressions(Zb, 20.0)
    check('closed depression: bowl filled to its rim, catchment drains into it', abs(Fb[4, 4] - 10.0) < 1e-5 and lb[4, 4] > 0 and lb[0, 0] == 0 and ab[lb[4, 4]] >= 9 * 400, (Fb[4, 4], ab))
    Pd = dict(r=np.array([0, 0]), c=np.array([0, 1]), dz=np.array([0.0, 0.5])); Hd = np.array([[0.6, 0.6]])
    check('point depth: crest offset', np.allclose(point_depth(Pd, Hd), [0.6, 0.1]))
    print('impacts selftest', 'OK' if ok else 'FAILED', root); return ok

if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--run', action='append', default=[]); ap.add_argument('--combine', action='store_true'); ap.add_argument('--local'); ap.add_argument('--out')
    ap.add_argument('--no-upload', action='store_true'); ap.add_argument('--selftest', action='store_true')
    ap.add_argument('--segments', default=os.path.join(ROOT, 'docs', 'graph_segments.json')); ap.add_argument('--crossings')
    ap.add_argument('--reports', default=os.path.join(ROOT, 'docs', 'prone', 'flood_reports.json')); ap.add_argument('--facilities', default=os.path.join(ROOT, 'docs', 'network', 'facilities.json'))
    ap.add_argument('--channels'); ap.add_argument('--channels-meta')
    a = ap.parse_args()
    if a.selftest: sys.exit(0 if selftest() else 1)
    if not a.run: ap.error('--run required (or --selftest)')
    main(a)
