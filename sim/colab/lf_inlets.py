"""Catch basins / storm-drain inlets as a capped, clogging-aware per-cell sink for LISFLOOD-FP 8.2 (opt-in LF_INLETS=1, used by w9_lisflood.py).

Why this and not LF_DRAINS: the earlier pipe sink (lf_drains.py, docs/proto/drains/DRAINS.md) put the full-flow capacity of every Leominster pipe
on every cell the pipe runs under, with 100 % efficient inlets.  It cut city flags by a third and removed documented sites in proportion.
Water does not enter a pipe along its length; it enters at the inlets, and an inlet takes at most what its grate passes at the ponding depth,
less what leaves and debris block.  This sink puts water removal only where inlets are, at the HEC-22 interception capacity, clogged, and
limited by the pipe network that carries it away.  Pre-registration: docs/proto/drains/INLETS_PREREG.md.

Capacity of one inlet (FHWA HEC-22, Urban Drainage Design Manual, 3rd ed., Brown, Schall, Morris, Doherty, Stein & Warner 2009 (rev. 2013),
FHWA-NHI-10-009, section 4.4.6 "Inlets in sag locations"; SI coefficients):
  grate in sag      weir     Q_w = C_w P d^1.5            C_w = 1.66, P = perimeter without the side against the curb (2 W + L)
                    orifice  Q_o = C_o A_g (2 g d)^0.5     C_o = 0.67, A_g = clear opening area
                    the smaller of the two (weir at shallow depth, orifice when the grate is submerged; HEC-22 takes the transition between)
  curb opening      weir     Q_w = C_w L d^1.5             C_w = 1.60 (no local depression), L = opening length
                    orifice  Q_o = C_o h L (2 g d_o)^0.5   C_o = 0.67, h = opening height, d_o = d - h / 2
  Inventory sizes are not recorded (MassDOT Inlet layer has no grate size field), so every grate is the standard 0.6 m x 0.6 m (2 ft x 2 ft
  square frame and grate of MassDOT Standard Drawing E 201.x; HEC-22 example grates are 0.6 m wide) with 50 % clear opening, and every curb
  opening is 1.5 m long and 0.15 m high.  "Double" inlets count as two.
  The sink is a fixed rate per cell (the patched infilfile: removed only where the cell is wet, never below zero), so the capacity is taken at
  one design ponding depth d = LF_INLETS_D (0.15 m: the 6 in curb reveal; above it water spills out of the gutter, and HEC-22 sag design
  limits ponding to about the curb height).  At 0.15 m the weir governs: Q_grate = 1.66 x 1.8 x 0.15^1.5 = 0.174 m3/s.
Clogging (fixed in advance, not fitted): Q_cap = Q x (1 - clog).
  clog = 0.50 (HEC-22 4.4.6: "a 50 percent clogging factor" for grates in sags, the usual design assumption);
  leaf-fall season (storm start between 15 Oct and 30 Nov): clog = 0.65.  Poirier, Rahman & van Duin (2025, ASCE EWRI World Environmental and
  Water Resources Congress, pp. 1190-1200: full-scale NRC Canada tests of a catch basin inlet in sag with leaf litter) measured 35 % of the
  unobstructed conveyance with heavy leaf cover; the one-year field inspection in Barcelona (Gomez et al., cited by Hao, Mu & Shi 2021,
  Water 13(6) 826) found 26.5-67.4 % capacity loss.  0.65 is the leaf-litter value; it applies to no storm of the catalogue (May-Sep).
  LF_INLETS_CLOG overrides both (sensitivity only).
Network limit: inlets drain into pipes.  Where pipe sizes are known (City of Leominster DPW Drain_Pipe, proto/data/drains/; MassDOT
  Conveyance with PIPESIZE, proto/data/inlets/), pipes are joined into networks (shared end points, lf_drains.networks), and the summed inlet
  capacity of a network is scaled down to the full-flow Manning capacity of its largest known pipe (lf_drains.full_flow_q; the trunk).
  An inlet belongs to the network of the nearest pipe within LF_INLETS_NET_M (15 m).  Elsewhere the per-inlet cap is the only cap.
Inlets used:
  MassDOT Inlet layer (state highways only: proto/data/inlets/massdot_inlets.csv.gz, snapshot 2026-10-29), in service;
  Leominster municipal inlets: the DPW layer has pipes, not structures, so each distinct pipe end node (1 m snap) is a structure, counted as
  F_INLET = 0.587 inlets (the MassDOT District 3 share of inlets among inlets + manholes: 28,936 / (28,936 + 20,331), SNAPSHOT.md); nodes
  within 10 m of a MassDOT inlet are dropped (the state's own structure).
Water removed leaves the model (not re-injected at outfalls), as in LF_DRAINS.

env: LF_INLETS=1, LF_INLETS_MASSDOT (csv.gz path, default proto/data/inlets/massdot_inlets.csv.gz), LF_INLETS_CONVEY (default
     proto/data/inlets/massdot_conveyance.csv.gz, '0' = none), LF_INLETS_DPW (default proto/data/drains/leominster_drain_pipe.zip, '0' = none),
     LF_INLETS_D (0.15), LF_INLETS_CLOG (unset = 0.50 / 0.65 leaf season), LF_INLETS_LEAF (1), LF_INLETS_NETCAP (1), LF_INLETS_NET_M (15).
"""
import csv, gzip, io, math, os, re
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.normpath(os.path.join(HERE, '..', '..'))
G = 9.81
CW_GRATE, CO, CW_CURB = 1.66, 0.67, 1.60
GRATE_L, GRATE_W, GRATE_OPEN = 0.6, 0.6, 0.5
CURB_L, CURB_H = 1.5, 0.15
D_DESIGN = 0.15
CLOG, CLOG_LEAF = 0.50, 0.65
LEAF_START, LEAF_END = (10, 15), (11, 30)          # (month, day), inclusive
F_INLET = 28936.0 / (28936.0 + 20331.0)            # MassDOT District 3 inlets / (inlets + manholes), docs/proto/stormwater/SNAPSHOT.md
NODE_DEDUP_M = 10.0
DROP_STATUS = re.compile(r'abandon|remov|^retired$|proposed install|destroy|not in service|out of service|inactive|filled', re.I)   # inventory values: docs/proto/drains/INLETS_PREREG.md


def q_grate(d, L=GRATE_L, W=GRATE_W, open_ratio=GRATE_OPEN):
    """HEC-22 grate inlet in sag (m3/s): min(weir C_w P d^1.5, orifice C_o A_g sqrt(2 g d)); P = 2 W + L (curb side excluded)."""
    if d <= 0: return 0.0
    return min(CW_GRATE * (2 * W + L) * d ** 1.5, CO * open_ratio * L * W * math.sqrt(2 * G * d))


def q_curb(d, L=CURB_L, h=CURB_H):
    """HEC-22 curb-opening inlet in sag, no depression (m3/s): weir C_w L d^1.5 up to d = h, orifice C_o h L sqrt(2 g (d - h/2)) above."""
    if d <= 0: return 0.0
    w = CW_CURB * L * d ** 1.5
    return w if d <= h else min(w, CO * h * L * math.sqrt(2 * G * (d - h / 2)))


def inlet_kind(t):
    """Published InletType text -> (kind, count).  kind 'grate' | 'curb' | None (not a surface inlet)."""
    s = (t or '').strip().lower()
    n = 2 if re.search(r'double|twin|dual|\b2\b', s) else 1
    if re.search(r'manhole|outlet|outfall|headwall|flared|junction|control structure|water quality|oil|separator|pipe end|scupper', s): return None, 0   # scuppers: bridge-deck drains
    if re.search(r'curb', s) and not re.search(r'grate|comb', s): return 'curb', n
    return 'grate', n


def clog_for(t0, leaf=True):
    """Clogging factor for a storm starting at t0 (ISO string or None): 0.65 in the leaf-fall season 15 Oct - 30 Nov, else 0.50."""
    v = os.environ.get('LF_INLETS_CLOG')
    if v not in (None, ''): return float(v), 'LF_INLETS_CLOG override'
    if leaf and t0:
        m = re.match(r'(\d{4})-(\d{2})-(\d{2})', str(t0))
        if m and LEAF_START <= (int(m.group(2)), int(m.group(3))) <= LEAF_END: return CLOG_LEAF, 'leaf-fall season (15 Oct - 30 Nov)'
    return CLOG, 'HEC-22 sag grate design clogging'


def read_massdot(path):
    """-> list of (lon, lat, type, status)."""
    out = []
    with gzip.open(path, 'rt', encoding='utf-8') as f:
        for r in csv.DictReader(f): out.append((float(r['lon']), float(r['lat']), r.get('type', ''), r.get('status', '')))
    return out


def read_conveyance(path):
    """-> (records, parts) in EPSG:26986 for lf_drains.pipe_table; culverts dropped (streams: the surface model routes them)."""
    recs, parts, culv = [], [], 0
    with gzip.open(path, 'rt', encoding='utf-8') as f:
        for r in csv.DictReader(f):
            if str(r.get('culvert', '')).strip().lower() in ('yes', 'y', 'true', '1'): culv += 1; continue
            if DROP_STATUS.search(r.get('status') or ''): continue
            xy = np.array([[float(v) for v in p.split()] for p in r['xy'].split(';') if p.strip()])
            if len(xy) < 2: continue
            recs.append(dict(PipeSize=r.get('size'), Material=r.get('material'))); parts.append([xy])
    return recs, parts, culv


def _pipes(recs, parts, epsg, BOX, RES, Z):
    """lf_drains.pipe_table split by known / defaulted size -> list of pipe dicts with 'known' flag."""
    import lf_drains as LD
    kn = [LD.parse_size(LD._field(r, ['PipeSize', 'Diameter', 'DIAM', 'Size']))[1] if r else False for r in recs]
    P = []
    for flag in (True, False):
        sel = [i for i in range(len(recs)) if recs[i] is not None and kn[i] == flag]
        Pk, _ = LD.pipe_table([recs[i] for i in sel], [parts[i] for i in sel], epsg, BOX, RES, Z)
        for p in Pk: p['known'] = flag
        P += Pk
    return P


def build(Z, block, BOX, RES, t0=None, log=print, massdot=None, convey=None, dpw=None):
    """Per-cell sink (mm/h, float32, rows north -> south) and an aggregate report."""
    import lf_drains as LD
    from scipy.spatial import cKDTree
    from pyproj import Transformer
    x0, y0, x1, y1 = BOX; ny = int(round((y1 - y0) / RES)); nx = int(round((x1 - x0) / RES))
    env = lambda k, d: os.environ.get(k, d)
    massdot = massdot or env('LF_INLETS_MASSDOT', os.path.join(ROOT, 'proto', 'data', 'inlets', 'massdot_inlets.csv.gz'))
    convey = convey or env('LF_INLETS_CONVEY', os.path.join(ROOT, 'proto', 'data', 'inlets', 'massdot_conveyance.csv.gz'))
    dpw = dpw or env('LF_INLETS_DPW', os.path.join(ROOT, 'proto', 'data', 'drains', 'leominster_drain_pipe.zip'))
    d = float(env('LF_INLETS_D', str(D_DESIGN))); clog, clog_why = clog_for(t0, env('LF_INLETS_LEAF', '1') == '1')
    qg, qc = q_grate(d), q_curb(d); rep = dict(design_depth_m=d, clog=clog, clog_reason=clog_why, q_grate_m3s=round(qg, 4), q_curb_m3s=round(qc, 4),
                                                grate=dict(L=GRATE_L, W=GRATE_W, open_ratio=GRATE_OPEN), curb=dict(L=CURB_L, h=CURB_H), f_inlet_dpw_node=round(F_INLET, 3))
    # 1. inlets: (x, y, Q_uncapped m3/s, source)
    X, Y, Q, SRC = [], [], [], []
    if massdot and massdot != '0' and os.path.exists(massdot):
        tr = Transformer.from_crs(4326, 26986, always_xy=True); M = read_massdot(massdot); st = dict(read=len(M), status_dropped=0, not_inlet=0, kinds={})
        lon = np.array([m[0] for m in M]); lat = np.array([m[1] for m in M]); mx, my = tr.transform(lon, lat)
        for (lo, la, t, s), x, y in zip(M, mx, my):
            if not (x0 <= x < x1 and y0 <= y < y1): continue
            if DROP_STATUS.search(s or ''): st['status_dropped'] += 1; continue
            k, n = inlet_kind(t)
            if k is None: st['not_inlet'] += 1; continue
            st['kinds'][f'{k}x{n}'] = st['kinds'].get(f'{k}x{n}', 0) + 1
            X.append(x); Y.append(y); Q.append(n * (qg if k == 'grate' else qc)); SRC.append(0)
        st['in_box'] = len(X); rep['massdot'] = st
    elif massdot and massdot != '0': rep['massdot'] = f'missing file {os.path.relpath(massdot, ROOT)}'; log('LF_INLETS: WARNING no MassDOT inlet table at', massdot)
    nm = len(X)
    # 2. pipes (network limit) and DPW nodes
    P = []
    if dpw and dpw != '0' and os.path.exists(dpw):
        recs, parts, epsg = LD.read_pipes(dpw); Pd = _pipes(recs, parts, epsg or 2249, BOX, RES, Z)
        ends = np.array([p['xy'][0] for p in Pd] + [p['xy'][-1] for p in Pd]).reshape(-1, 2)
        nodes = np.zeros((0, 2))
        if len(ends):
            t = cKDTree(ends); grp = -np.ones(len(ends), int); g = 0
            for i in range(len(ends)):
                if grp[i] >= 0: continue
                for j in t.query_ball_point(ends[i], 1.0):
                    if grp[j] < 0: grp[j] = g
                g += 1
            nodes = np.array([ends[grp == k].mean(0) for k in range(g)])
        inb = (nodes[:, 0] >= x0) & (nodes[:, 0] < x1) & (nodes[:, 1] >= y0) & (nodes[:, 1] < y1) if len(nodes) else np.zeros(0, bool)
        nodes = nodes[inb]; dup = 0
        if nm and len(nodes):
            dd, _ = cKDTree(np.column_stack([X[:nm], Y[:nm]])).query(nodes); dup = int((dd <= NODE_DEDUP_M).sum()); nodes = nodes[dd > NODE_DEDUP_M]
        for x, y in nodes: X.append(x); Y.append(y); Q.append(F_INLET * qg); SRC.append(1)
        rep['dpw'] = dict(pipes_in_box=len(Pd), size_known=int(sum(p['known'] for p in Pd)), nodes_in_box=int(inb.sum()), nodes_dropped_near_massdot=dup,
                          node_inlets=len(nodes), inlet_equivalents=round(F_INLET * len(nodes), 1))
        P += Pd
    if convey and convey != '0' and os.path.exists(convey):
        recs, parts, culv = read_conveyance(convey); Pc = _pipes(recs, parts, 26986, BOX, RES, Z)
        rep['massdot_conveyance'] = dict(pipes_in_box=len(Pc), size_known=int(sum(p['known'] for p in Pc)), culverts_dropped=culv); P += Pc
    X, Y, Q, SRC = np.array(X, float), np.array(Y, float), np.array(Q, float) * (1.0 - clog), np.array(SRC, int)
    q_inlets = float(Q.sum()); scale = np.ones(len(Q)); ncap = dict(networks=0, networks_capped=0, inlets_on_network=0)
    # 3. network limit: summed inlet capacity of a pipe network <= full-flow capacity of its largest known-size pipe
    if P and len(Q) and env('LF_INLETS_NETCAP', '1') == '1':
        net = LD.networks(P); pts, pid = [], []
        for i, p in enumerate(P):
            xy = p['xy']
            for k in range(len(xy) - 1):
                m = max(1, int(math.ceil(math.hypot(*(xy[k + 1] - xy[k])) / 5.0))); tt = (np.arange(m + 1) / m)[:, None]
                pts.append(xy[k] + (xy[k + 1] - xy[k]) * tt); pid += [i] * (m + 1)
        pts = np.concatenate(pts); pid = np.array(pid); dist, j = cKDTree(pts).query(np.column_stack([X, Y]))
        on = dist <= float(env('LF_INLETS_NET_M', '15')); inet = np.where(on, net[pid[j]], -1)
        cap = {}
        for i, p in enumerate(P):
            if p['known']: cap[net[i]] = max(cap.get(net[i], 0.0), p['Q'])
        for k in np.unique(inet[inet >= 0]):
            sel = inet == k; tot = Q[sel].sum(); ncap['networks'] += 1
            if k in cap and tot > cap[k] > 0: scale[sel] = cap[k] / tot; ncap['networks_capped'] += 1
        ncap['inlets_on_network'] = int(on.sum()); ncap['networks_without_known_size'] = int(sum(1 for k in np.unique(inet[inet >= 0]) if k not in cap))
    Q = Q * scale
    # 4. cells
    r = np.floor((y1 - Y) / RES).astype(int); c = np.floor((X - x0) / RES).astype(int); ok = (r >= 0) & (r < ny) & (c >= 0) & (c < nx)
    q = np.zeros((ny, nx)); np.add.at(q, (r[ok], c[ok]), Q[ok])
    blocked = 0.0
    if block is not None: blocked = float(q[block].sum()); q[block] = 0.0
    mmh = (q / (RES * RES) * 3.6e6).astype(np.float32); on = mmh > 0
    rep.update(inlets=int(len(Q)), inlets_massdot=int((SRC == 0).sum()), inlets_dpw_nodes=int((SRC == 1).sum()), pipes_for_network_limit=len(P),
               network_limit=ncap, q_inlets_clogged_m3s=round(q_inlets, 2), q_after_network_limit_m3s=round(float(Q.sum()), 2),
               q_on_water_cells_dropped_m3s=round(blocked, 2), total_q_m3s=round(float(q.sum()), 2), cells=int(on.sum()),
               cell_rate_mmh_p50=round(float(np.median(mmh[on])), 1) if on.any() else 0.0, cell_rate_mmh_max=round(float(mmh.max()), 1) if mmh.size else 0.0)
    log(f"LF_INLETS: {rep['inlets']:,} inlets ({rep['inlets_massdot']:,} MassDOT, {rep['inlets_dpw_nodes']:,} DPW nodes x {F_INLET:.3f}); d {d} m, clog {clog} ({clog_why}); "
        f"grate {qg:.3f} m3/s, curb {qc:.3f} m3/s unclogged; {q_inlets:.1f} m3/s clogged -> {rep['q_after_network_limit_m3s']} after the network limit "
        f"({ncap.get('networks_capped', 0)} of {ncap.get('networks', 0)} networks capped) -> {rep['total_q_m3s']} m3/s on {rep['cells']:,} cells")
    return mmh, rep


def selftest():
    import sys, tempfile
    sys.path.insert(0, HERE)
    ok = []
    # HEC-22 numbers: 0.6 x 0.6 grate at 0.15 m: weir 1.66 x 1.8 x 0.0581 = 0.1736; orifice 0.67 x 0.18 x sqrt(2 g 0.15) = 0.2069 -> weir governs
    assert abs(q_grate(0.15) - 1.66 * 1.8 * 0.15 ** 1.5) < 1e-9 and abs(q_grate(0.15) - 0.1736) < 5e-4
    assert abs(q_grate(1.0) - 0.67 * 0.18 * math.sqrt(2 * G)) < 1e-9          # deep: orifice governs
    assert abs(q_curb(0.15) - 1.60 * 1.5 * 0.15 ** 1.5) < 1e-9 and q_curb(0.3) <= 1.60 * 1.5 * 0.3 ** 1.5 and q_grate(0) == 0
    ok.append('HEC-22 sag grate (weir / orifice) and curb opening capacities')
    assert inlet_kind('Catch Basin') == ('grate', 1) and inlet_kind('Double Catch Basin') == ('grate', 2) and inlet_kind('Curb Inlet') == ('curb', 1)
    assert inlet_kind('Manhole')[0] is None and inlet_kind('Scupper (Discharge)')[0] is None and inlet_kind('Outlet Control Structure')[0] is None and inlet_kind('CBCI') == ('grate', 1) and inlet_kind('') == ('grate', 1) and inlet_kind('Combination Inlet') == ('grate', 1)
    ok.append('inlet type mapping')
    os.environ.pop('LF_INLETS_CLOG', None)
    assert clog_for('2023-09-11T16:00Z')[0] == 0.5 and clog_for('2026-10-15T00:00Z')[0] == 0.65 and clog_for('2026-11-30T23:00Z')[0] == 0.65
    assert clog_for('2026-12-01T00:00Z')[0] == 0.5 and clog_for('2026-10-14T23:00Z')[0] == 0.5 and clog_for('2026-10-20', leaf=False)[0] == 0.5
    os.environ['LF_INLETS_CLOG'] = '0'; assert clog_for('2023-09-11')[0] == 0.0; os.environ.pop('LF_INLETS_CLOG')
    ok.append('clogging: 0.50, leaf season 15 Oct - 30 Nov 0.65, override')
    # synthetic: 3 MassDOT grates in a 200 m box, one DPW-like pipe network (12 in) under two of them, a far inlet off-network
    import lf_drains as LD
    dd = tempfile.mkdtemp(prefix='lfin_'); from pyproj import Transformer
    tr = Transformer.from_crs(26986, 4326, always_xy=True); BOX = (100000.0, 900000.0, 100200.0, 900200.0)
    pts = [(100030.0, 900110.0), (100090.0, 900110.0), (100150.0, 900010.0)]
    with gzip.open(f'{dd}/m.csv.gz', 'wt') as f:
        w = csv.writer(f); w.writerow(['lon', 'lat', 'type', 'cover', 'status', 'district'])
        for x, y in pts: lo, la = tr.transform(x, y); w.writerow([f'{lo:.7f}', f'{la:.7f}', 'Catch Basin', '', 'In Service', '3'])
        lo, la = tr.transform(100150.0, 900150.0); w.writerow([f'{lo:.7f}', f'{la:.7f}', 'Catch Basin', '', 'Abandoned', '3'])
    with gzip.open(f'{dd}/c.csv.gz', 'wt') as f:
        w = csv.writer(f); w.writerow(['size', 'material', 'culvert', 'linetype', 'status', 'xy'])
        w.writerow(['6', 'PVC', 'No', '', '', '100010.0 900112.0;100190.0 900112.0'])          # small pipe: Q < 2 inlets -> capped
        w.writerow(['36', 'RC', 'Yes', '', '', '100010.0 900050.0;100190.0 900050.0'])         # culvert: dropped
    Z = np.full((10, 10), 100.0) - np.arange(10)[None, :] * 0.2
    s, rep = build(Z, None, BOX, 20.0, t0='2023-09-11T16:00Z', log=lambda *a: None, massdot=f'{dd}/m.csv.gz', convey=f'{dd}/c.csv.gz', dpw='0')
    assert rep['inlets_massdot'] == 3 and rep['massdot']['status_dropped'] == 1 and rep['massdot_conveyance']['culverts_dropped'] == 1, rep
    q6 = LD.full_flow_q(('circ', 6 * 0.0254), 0.011, max(0.2 / 20, 0.005))
    assert rep['network_limit']['networks_capped'] == 1 and rep['network_limit']['inlets_on_network'] == 2, rep
    expect = q6 + 0.5 * q_grate(0.15)
    assert abs(rep['total_q_m3s'] - round(expect, 2)) < 0.011 and abs(s.sum() * 400 / 3.6e6 - expect) < 1e-4, (rep['total_q_m3s'], expect)
    assert (s > 0).sum() == 3 and s[4, 1] > 0 and s[9, 7] > 0
    blk = np.zeros((10, 10), bool); blk[9, 7] = True; s2, rep2 = build(Z, blk, BOX, 20.0, log=lambda *a: None, massdot=f'{dd}/m.csv.gz', convey='0', dpw='0')
    assert s2[9, 7] == 0 and rep2['q_on_water_cells_dropped_m3s'] > 0 and rep2['network_limit']['networks'] == 0
    s3, rep3 = build(Z, None, BOX, 20.0, t0='2026-10-20T00:00Z', log=lambda *a: None, massdot=f'{dd}/m.csv.gz', convey='0', dpw='0')
    assert abs(rep3['total_q_m3s'] - round(3 * 0.35 * q_grate(0.15), 2)) < 0.011
    ok.append('sink raster: per-inlet cap x (1 - clog), network limit to the largest known pipe, culverts / abandoned dropped, water cells blocked, leaf season')
    # DPW-style shapefile: nodes become inlets x F_INLET, deduplicated against MassDOT inlets within 10 m
    LD.write_test_shapefile(f'{dd}/p', [np.array([[100030.0, 900170.0], [100110.0, 900170.0]]), np.array([[100110.0, 900170.0], [100190.0, 900170.0]])],
                            [dict(PipeSize='24', Material='RC'), dict(PipeSize='24', Material='RC')])
    open(f'{dd}/p.prj', 'w').write('PROJCS["NAD83 / Massachusetts Mainland",UNIT["metre",1]]')
    s4, rep4 = build(Z, None, BOX, 20.0, log=lambda *a: None, massdot=f'{dd}/m.csv.gz', convey='0', dpw=f'{dd}/p.shp')
    assert rep4['dpw']['nodes_in_box'] == 3 and rep4['inlets_dpw_nodes'] == 3 and rep4['network_limit']['networks_capped'] == 0, rep4
    assert abs(rep4['q_inlets_clogged_m3s'] - round(0.5 * q_grate(0.15) * (3 + 3 * F_INLET), 2)) < 0.011
    import shutil; shutil.rmtree(dd); ok.append('DPW pipe nodes -> municipal inlets (x F_INLET), node dedup, 24 in network not capped')
    for o in ok: print('ok  ', o)
    print(f'lf_inlets SELFTEST PASSED ({len(ok)} checks)')
    return ok


if __name__ == '__main__':
    selftest()
