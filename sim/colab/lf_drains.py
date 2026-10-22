"""Urban storm-drain capacity as a per-cell sink for LISFLOOD-FP 8.2 (opt-in, used by w9_lisflood.py).

Why: short urban downpours (25-65 mm radar totals: Worcester Jul 2023, Millbury Aug 2023, Webster Sep 2022, MetroWest Aug 2023) flood
streets because the inlets and pipes are overwhelmed, and on big storms a model without pipes keeps city streets ponded too long.
LISFLOOD-FP has no pipe network, so the drains are represented by the simplest physically bounded term: a maximum sink rate on the
cells the pipes run under, equal to what the pipes can carry flowing full.  Water is removed only where it ponds (h > DepthThresh)
and never below zero, so a drained cell keeps flooding once runoff reaching it exceeds the pipe capacity (inlet/pipe limited).

Capacity of one pipe (full-flow Manning, FHWA HEC-22 urban drainage design manual: Brown et al. 2013, 3rd ed., FHWA-NHI-10-009;
Kilgore, Atayee & Herrmann 2024, 4th ed., FHWA HIF-24-006; ASCE/WEF 1992 Manual of Practice 77, Design and Construction of Urban
Stormwater Management Systems):
        Q_full = (1/n) A R^(2/3) S^(1/2)        A, R of the full section; S = invert slope
  n by material (HEC-22 / MOP 77 storm-drain values): concrete 0.013, vitrified clay 0.014, PVC 0.011, smooth-interior HDPE / PP 0.012,
  corrugated metal 0.024, ductile / cast iron 0.013, brick / stone 0.016, unknown 0.013.
  S from the upstream and downstream inverts and the pipe length when both inverts exist (floored at LF_DRAIN_SMIN_INV, 0.0005); else
  the ground slope between the pipe ends from the model DEM, floored at LF_DRAIN_SMIN (0.005: drains follow the street grade, and a
  flat street still gets a minimum design slope); every slope is capped at 0.15.
Conduits of LF_DRAIN_MAX_IN (48 in equivalent diameter) and larger are left out: they carry streams, which the surface model already
  routes through the road crossings (crossing notches in w9).
Spatial assignment: each pipe's capacity is spread along its route, per length, over the cells it runs under (a main collects its
  inlets along the street it follows).  Two caps keep the total physical:
  - network: pipes are joined into networks by shared end points (1 m snap); a network cannot drain more than its largest pipe
    carries (the trunk at the outfall of a dendritic system, HEC-22 sizes pipes to grow downstream), so every pipe of an
    over-subscribed network is scaled by Q_max / sum(Q_pipes) (conservative for networks with several outfalls);
  - inlet: one cell cannot take more than LF_DRAIN_INLET_M3S (default 0.1 m3/s, about one sag grate inlet at 10-15 cm ponding with
    50 % clogging, HEC-22 weir equation Q = Cw P d^1.5).
  The drained water leaves the model (it is not re-injected at the outfalls: the receiving streams miss that inflow; see caveats).

Generic fallback for towns without pipe data (LF_DRAIN_DESIGN=1, off by default): a sink of eff x i_design x impervious fraction on
  developed cells (impervious >= LF_DRAIN_IMP_MIN), i_design = LF_DRAIN_DESIGN_MMH (43 mm/h, about the 10-yr 60-min intensity in
  central Massachusetts, NOAA Atlas 14 Vol. 10, Perica et al. 2015; an upper bound on what a rational-method system sized for that
  storm carries), eff = LF_DRAIN_EFF (0.5, inlet efficiency/clogging).  With LF_DRAINS too, the fallback is used only on cells more
  than LF_DRAIN_COVER_M (300 m) from any mapped pipe (other towns in the box).

Privacy: pipe data shared for research only.  The file is read from the path in LF_DRAINS (a .zip with one .shp, or a .shp); nothing
derived from the pipe geometry is written anywhere except the sink raster in the run directory, which w9 deletes after the run;
reports carry only aggregate numbers.

Dependencies: numpy, scipy, pyproj (no GDAL: a minimal shapefile/dbf reader below).
"""
import io, math, os, re, struct, zipfile
import numpy as np

# --- Manning n by material (HEC-22 4th ed. ch. 6 storm-drain roughness; ASCE MOP 77) -------------------------------------------
N_DEFAULT = 0.013
MATERIAL_N = [  # (regex on the upper-cased material code, n), first match wins
    (r'CORHDPE|CORR.*(HDPE|PE|PLAST)', 0.012),        # dual-wall corrugated HDPE, smooth interior
    (r'^CM|CMP|CORR|CSP|STEEL CORR', 0.024),          # corrugated metal
    (r'PVC|SDR|ABS', 0.011),
    (r'HDPE|^PE$|^PP$|POLY', 0.012),
    (r'^VC|CLAY|VCP|TILE', 0.014),
    (r'BRICK|STONE|MASON|^ST$', 0.016),
    (r'^RC|RCP|CONC|^CON|^CC$|^PC$|CEMENT', 0.013),   # reinforced / plain / precast concrete
    (r'^AC$|ASBESTOS', 0.012),
    (r'^DI|^CI|IRON', 0.013),
    (r'STEEL|^ST', 0.012),
]


def manning_n(material):
    m = (material or '').strip().upper()
    if not m: return N_DEFAULT
    for pat, n in MATERIAL_N:
        if re.search(pat, m): return n
    return N_DEFAULT


def parse_size(s, default_in=12.0):
    """Pipe size field -> ('circ', D m) or ('box', W m, H m).  Plain numbers are diameters in inches; 'AxB' is a box (feet when both
    numbers are <= 12, as in '3x5', else inches).  Missing / 'OTH' / unparseable -> default_in diameter (returned flag False)."""
    t = str(s if s is not None else '').strip().lower().replace('"', '').replace('in', '')
    m = re.match(r'^\s*(\d+(?:\.\d+)?)\s*[x\*]\s*(\d+(?:\.\d+)?)\s*$', t)
    if m:
        a, b = float(m.group(1)), float(m.group(2))
        k = 0.3048 if max(a, b) <= 12 else 0.0254
        if a > 0 and b > 0: return ('box', a * k, b * k), True
    m = re.match(r'^\s*(\d+(?:\.\d+)?)\s*$', t)
    if m and float(m.group(1)) > 0: return ('circ', float(m.group(1)) * 0.0254), True
    return ('circ', default_in * 0.0254), False


def full_flow_q(size, n, S):
    """Full-flow Manning capacity (m3/s, SI: Q = (1/n) A R^(2/3) S^(1/2))."""
    if size[0] == 'circ':
        D = size[1]; A = math.pi * D * D / 4.0; R = D / 4.0
    else:
        W, H = size[1], size[2]; A = W * H; R = A / (2.0 * (W + H))
    return (1.0 / n) * A * R ** (2.0 / 3.0) * math.sqrt(max(S, 0.0))


# --- minimal shapefile (PolyLine) + dBASE reader --------------------------------------------------------------------------------
def _read_dbf(b):
    nrec, hlen, rlen = struct.unpack('<IHH', b[4:12]); fields = []; p = 32
    while b[p] != 0x0D:
        name = b[p:p + 11].split(b'\0')[0].decode('latin-1'); ftype = chr(b[p + 11]); flen = b[p + 16]; fields.append((name, ftype, flen)); p += 32
    rows = []
    for r in range(nrec):
        o = hlen + r * rlen
        if b[o:o + 1] == b'*': rows.append(None); continue     # deleted record
        o += 1; row = {}
        for name, ftype, flen in fields:
            v = b[o:o + flen].decode('latin-1', 'replace').strip(); o += flen
            row[name] = v if v else None
        rows.append(row)
    return rows


def _read_shp_lines(b):
    """PolyLine / PolyLineZ / PolyLineM records -> list of parts (list of (N,2) arrays) per record (None for null shapes)."""
    out = []; p = 100; L = len(b)
    while p + 8 <= L:
        _, clen = struct.unpack('>ii', b[p:p + 8]); p += 8; rec = b[p:p + 2 * clen]; p += 2 * clen
        st = struct.unpack('<i', rec[:4])[0]
        if st == 0: out.append(None); continue
        if st not in (3, 13, 23): raise ValueError(f'shape type {st} is not a polyline')
        nparts, npts = struct.unpack('<ii', rec[36:44]); parts = list(struct.unpack(f'<{nparts}i', rec[44:44 + 4 * nparts])) + [npts]
        xy = np.frombuffer(rec[44 + 4 * nparts:44 + 4 * nparts + 16 * npts], '<f8').reshape(npts, 2)
        out.append([xy[parts[k]:parts[k + 1]] for k in range(nparts)])
    return out


def _epsg_from_prj(prj):
    t = (prj or '').upper()
    if 'MASSACHUSETTS' in t and 'MAINLAND' in t: return 2249 if ('FOOT' in t or 'FEET' in t or 'FT' in t) else 26986
    return None


def read_pipes(path):
    """Read a polyline shapefile (path to .shp, or a .zip holding exactly one .shp).  Returns (records, parts, epsg)."""
    def pick(names, ext):
        c = [n for n in names if n.lower().endswith(ext)]; return c[0] if c else None
    if path.lower().endswith('.zip'):
        with zipfile.ZipFile(path) as z:
            names = z.namelist(); shp = pick(names, '.shp')
            if not shp: raise ValueError('no .shp in the zip')
            base = shp[:-4]; get = lambda e: z.read(base + e) if base + e in names else None
            bshp, bdbf, bprj = get('.shp'), get('.dbf'), get('.prj')
    else:
        base = path[:-4]; rd = lambda e: open(base + e, 'rb').read() if os.path.exists(base + e) else None
        bshp, bdbf, bprj = rd('.shp'), rd('.dbf'), rd('.prj')
    if bshp is None or bdbf is None: raise ValueError('shapefile needs .shp and .dbf')
    parts = _read_shp_lines(bshp); recs = _read_dbf(bdbf)
    if len(parts) != len(recs): raise ValueError(f'{len(parts)} shapes vs {len(recs)} dbf records')
    return recs, parts, _epsg_from_prj(bprj.decode('latin-1') if bprj else '')


def _field(rec, names):
    low = {k.lower(): v for k, v in rec.items()}
    for n in names:
        if n.lower() in low and low[n.lower()] not in (None, ''): return low[n.lower()]
    return None


def _num(v):
    try: x = float(v); return x if math.isfinite(x) else None
    except (TypeError, ValueError): return None


# --- pipes -> cells -------------------------------------------------------------------------------------------------------------
def line_cells(xy, BOX, RES, step=None):
    """Length (m) of a polyline inside each grid cell, by sampling at <= RES/4.  Rows north -> south.  {(r, c): length}."""
    x0, y0, x1, y1 = BOX; ny = int(round((y1 - y0) / RES)); nx = int(round((x1 - x0) / RES)); step = step or RES / 4.0; out = {}
    for k in range(len(xy) - 1):
        (ax, ay), (bx, by) = xy[k], xy[k + 1]; seg = math.hypot(bx - ax, by - ay)
        if seg <= 0: continue
        m = max(1, int(math.ceil(seg / step))); t = (np.arange(m) + 0.5) / m
        px = ax + (bx - ax) * t; py = ay + (by - ay) * t
        r = np.floor((y1 - py) / RES).astype(int); c = np.floor((px - x0) / RES).astype(int)
        ok = (r >= 0) & (r < ny) & (c >= 0) & (c < nx)
        for rr, cc in zip(r[ok], c[ok]): out[(rr, cc)] = out.get((rr, cc), 0.0) + seg / m
    return out


def _ground(Z, BOX, RES, x, y):
    x0, y0, x1, y1 = BOX; r = int((y1 - y) // RES); c = int((x - x0) // RES)
    if 0 <= r < Z.shape[0] and 0 <= c < Z.shape[1] and np.isfinite(Z[r, c]): return float(Z[r, c])
    return None


def pipe_table(recs, parts, epsg, BOX, RES, Z, smin=0.005, smin_inv=0.0005, smax=0.15, default_in=12.0, inv_ft=True, margin=200.0, max_in=48.0):
    """Pipes overlapping BOX (+margin) -> list of dicts (model CRS EPSG:26986 coordinates, capacity) and aggregate counts."""
    from pyproj import Transformer
    tr = None if epsg in (None, 26986) else Transformer.from_crs(epsg, 26986, always_xy=True)
    x0, y0, x1, y1 = BOX; kinv = 0.3048006 if inv_ft else 1.0; P = []
    st = dict(read=len(recs), in_box=0, size_default=0, excluded_large=0, slope_invert=0, slope_ground=0, slope_floor=0)
    for rec, pp in zip(recs, parts):
        if rec is None or not pp: continue
        xy = np.concatenate(pp)
        if tr is not None: X, Y = tr.transform(xy[:, 0], xy[:, 1]); xy = np.column_stack([X, Y])
        if xy[:, 0].max() < x0 - margin or xy[:, 0].min() > x1 + margin or xy[:, 1].max() < y0 - margin or xy[:, 1].min() > y1 + margin: continue
        L = float(np.hypot(*np.diff(xy, axis=0).T).sum())
        if L <= 0.1: continue
        st['in_box'] += 1
        size, known = parse_size(_field(rec, ['PipeSize', 'Diameter', 'DIAM', 'Size']), default_in); st['size_default'] += (not known)
        deq = size[1] if size[0] == 'circ' else 2.0 * math.sqrt(size[1] * size[2] / math.pi)
        if max_in and deq >= max_in * 0.0254: st['excluded_large'] += 1; continue      # stream culverts: the surface model routes streams (crossing notches)
        n = manning_n(_field(rec, ['Material', 'MATL', 'PipeMat']))
        iu = _num(_field(rec, ['UpstreamIn', 'US_INV', 'UpInvert', 'InvertUp'])); idn = _num(_field(rec, ['Downstream', 'DS_INV', 'DnInvert', 'InvertDn']))
        zu, zd = _ground(Z, BOX, RES, *xy[0]), _ground(Z, BOX, RES, *xy[-1])
        if iu is not None and idn is not None and iu > 0 and idn > 0 and abs(iu - idn) * kinv / L < 0.5:
            S = max(abs(iu - idn) * kinv / L, smin_inv); src = 'invert'; up_first = iu >= idn
        elif zu is not None and zd is not None:
            S = abs(zu - zd) / L; src = 'ground'; up_first = zu >= zd
            if S < smin: S = smin; src = 'floor'
        else:
            S = smin; src = 'floor'; up_first = True
        S = min(S, smax); st['slope_' + src] += 1
        P.append(dict(xy=xy, L=L, Q=full_flow_q(size, n, S), up=tuple(xy[0] if up_first else xy[-1]), dn=tuple(xy[-1] if up_first else xy[0])))
    return P, st


def networks(P, snap=1.0):
    """Union pipes sharing an end point (within `snap` m) into networks (undirected: the drawn direction and the invert data are too
    patchy to find outfalls reliably).  Returns the network id per pipe."""
    from scipy.spatial import cKDTree
    m = len(P)
    if m == 0: return np.zeros(0, int)
    E = np.array([p['xy'][0] for p in P] + [p['xy'][-1] for p in P]); parent = np.arange(2 * m)
    def find(a):
        while parent[a] != a: parent[a] = parent[parent[a]]; a = parent[a]
        return a
    for i in range(m): parent[find(i)] = find(i + m)                 # the two ends of a pipe
    for a, b in cKDTree(E).query_pairs(snap): parent[find(a)] = find(b)
    return np.array([find(i) for i in range(m)])


def build_sink(P, BOX, RES, block=None, inlet_m3s=0.1, eff=1.0, network_cap=True):
    """Per-cell sink rate (mm/h) from the pipe table; `block` = cells where no sink applies (rivers, lakes).  Returns (mm/h, report)."""
    x0, y0, x1, y1 = BOX; ny = int(round((y1 - y0) / RES)); nx = int(round((x1 - x0) / RES)); q = np.zeros((ny, nx))
    rep = dict(pipes=len(P))
    if not P: return q.astype(np.float32), rep
    net = networks(P); Q = np.array([p['Q'] for p in P]); scale = np.ones(len(P))
    if network_cap:                                     # a network drains at most what its largest pipe (the trunk) carries
        for k in np.unique(net):
            sel = net == k; cap = Q[sel].max(); tot = Q[sel].sum()
            if tot > cap > 0: scale[sel] = cap / tot
    for i, p in enumerate(P):
        for (r, c), l in line_cells(p['xy'], BOX, RES).items(): q[r, c] += eff * scale[i] * Q[i] * l / p['L']
    q_raw_total = float(q.sum())
    q = np.minimum(q, inlet_m3s)
    if block is not None: q[block] = 0.0
    mmh = q / (RES * RES) * 3.6e6
    on = mmh > 0
    rep.update(networks=int(len(np.unique(net))), q_full_sum_m3s=round(float(Q.sum()), 1),
               q_network_capped_m3s=round(float((Q * scale).sum()), 1), q_in_box_m3s=round(q_raw_total, 1), q_after_inlet_cap_m3s=round(float(q.sum()), 1),
               cells=int(on.sum()), cell_rate_mmh_p50=round(float(np.median(mmh[on])), 1) if on.any() else 0.0,
               cell_rate_mmh_max=round(float(mmh.max()), 1), inlet_cap_m3s=inlet_m3s, eff=eff,
               pipe_q_m3s_p10_p50_p90=[round(float(v), 3) for v in np.percentile(Q, [10, 50, 90])])
    return mmh.astype(np.float32), rep


def design_sink(IMP, block=None, mmh=43.0, eff=0.5, imp_min=0.2):
    """Generic fallback: eff x design intensity x impervious fraction on developed cells (mm/h)."""
    s = np.where(IMP >= imp_min, eff * mmh * IMP, 0.0)
    if block is not None: s = np.where(block, 0.0, s)
    return s.astype(np.float32)


def from_env(Z, IMP, block, BOX, RES, log=print):
    """w9 hook: sink raster (mm/h) and an aggregate report from LF_DRAINS / LF_DRAIN_DESIGN; (None, None) when both are off."""
    path = os.environ.get('LF_DRAINS'); design = os.environ.get('LF_DRAIN_DESIGN', '0') == '1'
    if not path and not design: return None, None
    g = lambda k, d: float(os.environ.get(k, d)); rep = {}; sink = np.zeros(Z.shape, np.float32)
    if path:
        path = os.path.expanduser(path)
        recs, parts, epsg = read_pipes(path)
        epsg = int(os.environ['LF_DRAINS_EPSG']) if os.environ.get('LF_DRAINS_EPSG') else (epsg or 2249)
        P, st = pipe_table(recs, parts, epsg, BOX, RES, Z, smin=g('LF_DRAIN_SMIN', '0.005'), smin_inv=g('LF_DRAIN_SMIN_INV', '0.0005'),
                           default_in=g('LF_DRAIN_DEFAULT_IN', '12'), max_in=g('LF_DRAIN_MAX_IN', '48'), inv_ft=os.environ.get('LF_DRAINS_INV_FT', '1') == '1')
        sink, r2 = build_sink(P, BOX, RES, block, inlet_m3s=g('LF_DRAIN_INLET_M3S', '0.1'), eff=g('LF_DRAIN_PIPE_EFF', '1.0'),
                              network_cap=os.environ.get('LF_DRAIN_NETCAP', '1') == '1')
        rep['pipes'] = dict(st, **r2, epsg=epsg)
        log(f"LF_DRAINS: {st['in_box']:,} pipes in the box of {st['read']:,} (sizes defaulted {st['size_default']:,}; slope from inverts {st['slope_invert']:,}, "
            f"ground {st['slope_ground']:,}, floor {st['slope_floor']:,}); {st['excluded_large']:,} stream-size conduits left to the surface model; {r2.get('networks', 0):,} networks; "
            f"capacity sum {r2.get('q_full_sum_m3s')} m3/s, network-capped {r2.get('q_network_capped_m3s')}, in box after inlet cap {r2.get('q_after_inlet_cap_m3s')} m3/s "
            f"on {r2.get('cells', 0):,} cells (median {r2.get('cell_rate_mmh_p50')} mm/h)")
    if design:
        ds = design_sink(IMP, block, g('LF_DRAIN_DESIGN_MMH', '43'), g('LF_DRAIN_EFF', '0.5'), g('LF_DRAIN_IMP_MIN', '0.2'))
        if path and (sink > 0).any():
            from scipy.ndimage import distance_transform_edt
            far = distance_transform_edt(sink <= 0) * RES > g('LF_DRAIN_COVER_M', '300'); ds = np.where(far, ds, 0.0)
        sink = np.maximum(sink, ds).astype(np.float32)
        rep['design'] = dict(mmh=g('LF_DRAIN_DESIGN_MMH', '43'), eff=g('LF_DRAIN_EFF', '0.5'), imp_min=g('LF_DRAIN_IMP_MIN', '0.2'),
                             cells=int((ds > 0).sum()), q_m3s=round(float(ds.sum()) * RES * RES / 3.6e6, 1))
        log(f"LF_DRAIN_DESIGN: {rep['design']['cells']:,} developed cells, total {rep['design']['q_m3s']} m3/s")
    rep['total_q_m3s'] = round(float(sink.sum()) * RES * RES / 3.6e6, 1); rep['cells'] = int((sink > 0).sum())
    return sink, rep


def selftest():
    """Synthetic pipes only."""
    ok = []
    # capacity: 12 in (0.3048 m) concrete at S = 0.01 -> (1/0.013) 0.07297 0.0762^(2/3) 0.1 = 0.1012 m3/s
    q = full_flow_q(('circ', 0.3048), 0.013, 0.01); assert abs(q - 0.1012) < 0.001, q
    qb = full_flow_q(('box', 0.9144, 0.9144), 0.013, 0.01); assert qb > 10 * q
    assert parse_size('12')[0] == ('circ', 12 * 0.0254) and parse_size('3x5')[0][0] == 'box' and abs(parse_size('3x5')[0][2] - 1.524) < 1e-9
    assert parse_size('OTH') == (('circ', 12 * 0.0254), False) and parse_size(None, 15)[0][1] == 15 * 0.0254
    assert manning_n('RC') == 0.013 and manning_n('CM') == 0.024 and manning_n('PVC') == 0.011 and manning_n('HDPE') == 0.012
    assert manning_n('CORHDPE') == 0.012 and manning_n('VC') == 0.014 and manning_n('') == 0.013 and manning_n('weird') == 0.013
    ok.append('full-flow Manning capacity, size parsing, n by material')
    # cells: a 100 m straight pipe on a 20 m grid -> 5 cells of 20 m each
    BOX = (0.0, 0.0, 200.0, 200.0); lc = line_cells(np.array([[0.0, 110.0], [100.0, 110.0]]), BOX, 20.0)
    assert len(lc) == 5 and all(abs(v - 20) < 1e-6 for v in lc.values()) and set(r for r, c in lc) == {4}
    ok.append('pipe route -> cell lengths')
    # network cap: two laterals (12 in) feeding a 12 in outfall pipe -> total limited to the outfall's capacity
    Z = np.full((10, 10), 100.0) - np.arange(10)[None, :] * 0.5        # ground falls to the east, 2.5 % slope
    mk = lambda xy, iu, idn: (dict(PipeSize='12', Material='RC', UpstreamIn=iu, Downstream=idn), [np.array(xy, float)])
    rs = [mk([[10, 150], [90, 150]], None, None), mk([[90, 30], [90, 150]], None, None), mk([[90, 150], [190, 150]], '330', '325')]
    recs, parts = [r for r, _ in rs], [p for _, p in rs]
    P, st = pipe_table(recs, parts, 26986, BOX, 20.0, Z)
    assert st['in_box'] == 3 and st['slope_invert'] == 1 and st['slope_ground'] + st['slope_floor'] == 2
    net = networks(P); assert len(set(net.tolist())) == 1
    assert len(set(networks(P + [dict(P[0], xy=P[0]['xy'] + 500.0)]).tolist())) == 2       # a far-away pipe is its own network
    qmax = max(p['Q'] for p in P); s_cap, rep = build_sink(P, BOX, 20.0); s_nc, rep2 = build_sink(P, BOX, 20.0, network_cap=False)
    assert rep2['q_network_capped_m3s'] > rep['q_network_capped_m3s'] and abs(s_nc.sum() * 400 / 3.6e6 - sum(p['Q'] for p in P)) < 1e-3
    assert abs(s_cap.sum() * 400 / 3.6e6 - qmax) < 0.01 * qmax, (s_cap.sum() * 400 / 3.6e6, qmax)
    big = [mk([[10, 50], [190, 50]], None, None)]; big[0][0]['PipeSize'] = '60'
    Pb, stb = pipe_table([big[0][0]], [big[0][1]], 26986, BOX, 20.0, Z); assert not Pb and stb['excluded_large'] == 1
    blk = np.zeros((10, 10), bool); blk[2, :] = True; sb, _ = build_sink(P, BOX, 20.0, blk); assert sb[2].sum() == 0
    ok.append('network cap (sum <= largest pipe), stream-size conduits excluded, river/lake cells blocked, slope from inverts else ground')
    imp = np.zeros((4, 4)); imp[0] = 1.0; imp[1] = 0.1; d = design_sink(imp)
    assert abs(d[0, 0] - 21.5) < 1e-5 and d[1].sum() == 0; ok.append('design-storm fallback (0.5 x 43 mm/h x impervious on developed cells)')
    # shapefile reader round trip on a synthetic file written here
    import tempfile
    dd = tempfile.mkdtemp(prefix='lfdr_'); write_test_shapefile(f'{dd}/t', [np.array([[0.0, 0.0], [3.0, 4.0]]), np.array([[1.0, 1.0], [1.0, 2.0], [2.0, 2.0]])],
                                                                    [dict(PipeSize='12', Material='PVC'), dict(PipeSize='3x3', Material='RC')])
    with zipfile.ZipFile(f'{dd}/t.zip', 'w') as z:
        for e in ('.shp', '.shx', '.dbf'): z.write(f'{dd}/t{e}', f't{e}')
    for pth in (f'{dd}/t.shp', f'{dd}/t.zip'):
        recs, parts, epsg = read_pipes(pth); assert len(recs) == 2 and recs[1]['PipeSize'] == '3x3' and parts[0][0].shape == (2, 2) and abs(parts[1][0][2, 0] - 2) < 1e-12
    import shutil; shutil.rmtree(dd); ok.append('minimal shapefile/dbf reader (.shp and .zip)')
    for o in ok: print('ok  ', o)
    print(f'lf_drains SELFTEST PASSED ({len(ok)} checks)')
    return ok


def write_test_shapefile(base, lines, attrs):
    """Tiny PolyLine shapefile writer, for the synthetic selftest only."""
    recs = []
    for i, xy in enumerate(lines):
        xy = np.asarray(xy, '<f8'); bb = struct.pack('<4d', xy[:, 0].min(), xy[:, 1].min(), xy[:, 0].max(), xy[:, 1].max())
        body = struct.pack('<i', 3) + bb + struct.pack('<ii', 1, len(xy)) + struct.pack('<i', 0) + xy.tobytes()
        recs.append(struct.pack('>ii', i + 1, len(body) // 2) + body)
    allxy = np.concatenate(lines); bb = struct.pack('<4d', allxy[:, 0].min(), allxy[:, 1].min(), allxy[:, 0].max(), allxy[:, 1].max()) + b'\0' * 32
    shp = b''.join(recs); hdr = lambda L: struct.pack('>i', 9994) + b'\0' * 20 + struct.pack('>i', L // 2) + struct.pack('<ii', 1000, 3) + bb
    open(base + '.shp', 'wb').write(hdr(100 + len(shp)) + shp)
    shx = b''; off = 100
    for r in recs: shx += struct.pack('>ii', off // 2, (len(r) - 8) // 2); off += len(r)
    open(base + '.shx', 'wb').write(hdr(100 + len(shx)) + shx)
    names = list(attrs[0]); flen = 20; hlen = 32 + 32 * len(names) + 1; rlen = 1 + flen * len(names)
    d = struct.pack('<BBBBIHH', 3, 126, 1, 1, len(attrs), hlen, rlen) + b'\0' * 20
    for nm in names: d += nm.encode()[:10].ljust(11, b'\0') + b'C' + b'\0' * 4 + bytes([flen, 0]) + b'\0' * 14
    d += b'\x0d'
    for a in attrs: d += b' ' + b''.join(str(a[nm]).encode().ljust(flen) for nm in names)
    open(base + '.dbf', 'wb').write(d + b'\x1a')


if __name__ == '__main__':
    selftest()
