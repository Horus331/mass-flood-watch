"""LF_DAMS=1: dams, mill ponds and lake outlets for w9_lisflood.py, so impoundments store water instead of being breached away.

Why: the model DEM is lidar bare earth, in which every lake and pond >= 2 acres is hydro-flattened to one water-surface elevation (USGS Lidar Base
Specification, Heidemann 2018, TM 11-B4) and has no bathymetry.  The channel burn cuts a trench along the NHD artificial path through the lake,
crossing notches cut the road fills that most Massachusetts mill-pond dams carry, and depression breaching (Barnes et al. 2014) carves the rest,
so a lake is an open channel with a few cm of storage: Lake Quinsigamond in the Worcester box rises ~0.10 m and passes its inflow straight to
North Grafton (docs/proto/exp/mb_d4), and the Leominster hydrograph recedes far too fast (proto/README.md).

What (per NID dam in the box, docs/network/dams_ma.json from the USACE National Inventory of Dams):
  1. pool level P: the highest hydro-flattened water surface next to the dam (connected cells whose four face neighbours are all within 3 cm,
     touching an NHD flowline / open-water cell, within LF_DAMS_ADJ_M (120 m) of the NID point, below the dam crest).  P stands in for the
     spillway crest (normal pool of an uncontrolled spillway, the level the lidar saw).
  2. lake footprint: the cells D4-connected to that surface with lidar height in [P - 0.3, P + 0.1] m.  The footprint gets a flat bed at P - D,
     D = NID normal storage / surface area (mean depth) clipped to LF_DAMS_DEPTH (1..3 m; 1.5 m when NID has neither), and starts full
     (startfile depth D, water surface at P): lakes at normal pool, storage only above the crest, as at the start of a summer storm.  A real
     depth also lets the level rise evenly (wave speed sqrt(g D)) instead of rain crawling across a zero-depth sheet.
  3. the rim: every cell face-adjacent to the footprint.  Rim cells whose lidar height is >= P are kept at >= P (burn / notches stay, so
     inflowing streams and road notches still feed the lake, but nothing drains it below its pool); rim cells lower than P are where water would leave the lake, i.e. the dam line, and are raised to the dam crest (highest 10 m
     lidar cell around them, at least P + 0.5 m) -- except one outlet cell, the lowest rim cell near the NID point.  Footprint and rim are
     protected from depression breaching (breach_depressions(protect=...)), so no carved path ever cuts through the dam.
  4. the outlet: LISFLOOD-FP's native weir (weirfile; input.cpp LoadWeir, weir_flow.cpp CalcWeirQx/Qy, called by FloodplainQ in fp_flow.cpp
     before the acceleration flux, so it works with the CPU acceleration solver on the 2D grid) on the face between the lake and the outlet cell:
     crest P, width = NID spillway width (else the NHDPlus/Bieger et al. 2015 bankfull width at the outlet, >= 3 m), Cd = 1.7 (SI broad-crested
     weir, Q = 1.705 b H^1.5, Chow 1959 sec. 14-6; Bos 1989), modular limit 0.67 (Bos 1989).  The outlet cell is cut to <= P - 0.2 m so the
     weir discharges freely and the breach carves its path on downstream as for any other cell.
     LF_DAMS_WEIR=0: no weir file; the outlet cell is set to the crest P instead (a DEM weir one cell wide: Manning flow over a 20 m sill).
  5. solver damping in LF_DAMS runs: theta 0.7, cfl 0.5 in the .par (LF_DAMS_THETA / LF_DAMS_CFL; '' leaves the LISFLOOD-FP default).
Not modelled: gate operations, drawn-down water-supply reservoirs (they start full here), lake bathymetry, dam failure.
"""
import os, json, math
import numpy as np

N4 = ((-1, 0), (1, 0), (0, -1), (0, 1))


def load_dams(path=None):
    path = path or os.environ.get('LF_DAMS_FILE') or os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'docs', 'network', 'dams_ma.json')
    J = json.load(open(path)); C = J['columns']
    return [dict(zip(C, r)) for r in J['rows']], J.get('source', path)


def _flat(zr, tol=0.03):
    """Cells whose 4 face neighbours (inside the window) are all within tol: hydro-flattened water."""
    f = np.ones(zr.shape, bool)
    for dr, dc in N4:
        sh = np.full(zr.shape, np.nan); a = slice(max(dr, 0), zr.shape[0] + min(dr, 0)); b = slice(max(-dr, 0), zr.shape[0] + min(-dr, 0))
        a2 = slice(max(dc, 0), zr.shape[1] + min(dc, 0)); b2 = slice(max(-dc, 0), zr.shape[1] + min(-dc, 0))
        sh[b, b2] = zr[a, a2]
        f &= ~(np.abs(sh - zr) > tol)          # nan (outside the window) counts as flat
    return f


def find_pool(Z_RAW, ZMAX10, wet, r, c, res, adj_m=120.0, win_m=400.0, min_cells=4):
    """-> (P, seed cells (rows, cols) in grid coords, dam crest estimate) or (None, reason)."""
    from scipy import ndimage
    ny, nx = Z_RAW.shape; k = int(math.ceil(win_m / res)); r0, r1, c0, c1 = max(0, r - k), min(ny, r + k + 1), max(0, c - k), min(nx, c + k + 1)
    zr = Z_RAW[r0:r1, c0:c1].astype(np.float64); fl = _flat(zr)
    lab, n = ndimage.label(fl)
    if n == 0: return None, 'no flat water surface near the dam'
    rr, cc = np.mgrid[r0:r1, c0:c1]; dist = np.hypot(rr - r, cc - c) * res
    ka = int(math.ceil(60.0 / res)); crest = float(np.nanmax(ZMAX10[max(0, r - ka):r + ka + 1, max(0, c - ka):c + ka + 1]))
    comps = []
    for i in range(1, n + 1):
        m = lab == i
        if m.sum() < min_cells or dist[m].min() > adj_m: continue
        P = float(np.median(zr[m]))
        if P > crest - 0.3: continue
        comps.append((P, m, bool(wet[r0:r1, c0:c1][m].any())))
    # an NHD water / flowline cell on the surface, or (no flowline mapped through it) a flat surface of >= 25 cells (1 ha at 20 m)
    ok = [t for t in comps if t[2] or t[1].sum() >= 25]
    if not ok: return None, 'no hydro-flattened pool (>= %d flat cells on an NHD water cell, or >= 25 flat cells, within %.0f m, below the crest)' % (min_cells, adj_m)
    P = max(t[0] for t in ok); m = np.zeros(zr.shape, bool)
    for t in ok:
        if abs(t[0] - P) <= 0.05: m |= t[1]                 # every piece of the same water surface seeds the footprint
    sr, sc = np.nonzero(m)
    return (P, (sr + r0, sc + c0), crest), None


def footprint(Z_RAW, P, seed, lo=0.3, hi=0.1, max_cells=None):
    """D4 flood from the seed over cells with lidar height in [P - lo, P + hi]."""
    from scipy import ndimage
    band = (Z_RAW >= P - lo) & (Z_RAW <= P + hi)
    lab, _ = ndimage.label(band, structure=[[0, 1, 0], [1, 1, 1], [0, 1, 0]])
    ids = np.unique(lab[seed]); ids = ids[ids > 0]
    m = np.isin(lab, ids)
    return m


def ring_of(m):
    from scipy import ndimage
    return ndimage.binary_dilation(m, structure=[[0, 1, 0], [1, 1, 1], [0, 1, 0]]) & ~m


def apply(Z, Z_RAW, ZMAX10, water, chan, CW, BOX, RES, log=print, dams=None):
    """Edit the model DEM (after channel burn and crossing notches, before depression breaching).
    Returns (Z, water, D) with D = dict(protect, start (lake depth, m), weirs [weirfile lines], lakes [report], dams_in_box, skipped)."""
    from pyproj import Transformer
    x0, y0, x1, y1 = BOX; ny, nx = Z.shape; Z = Z.astype(np.float32).copy()
    if dams is None: dams, src = load_dams()
    else: src = 'given'
    tf = Transformer.from_crs(4326, 26986, always_xy=True)
    wet = water | chan
    cd = float(os.environ.get('LF_DAMS_CD', '1.7')); mlim = float(os.environ.get('LF_DAMS_M', '0.67'))
    dmin, dmax = (float(v) for v in os.environ.get('LF_DAMS_DEPTH', '1,3').split(','))
    use_weir = os.environ.get('LF_DAMS_WEIR', '1') == '1'
    adj_m = float(os.environ.get('LF_DAMS_ADJ_M', '120')); max_km2 = float(os.environ.get('LF_DAMS_MAX_KM2', '40'))
    owner = np.zeros((ny, nx), np.int32)       # lake id + 1 per footprint cell
    lakes, skipped, inbox = [], [], 0
    cand = []
    for d in dams:
        if d.get('lon') is None or d.get('lat') is None: continue
        xq, yq = tf.transform(d['lon'], d['lat'])
        if not (x0 + 2 * RES <= xq < x1 - 2 * RES and y0 + 2 * RES <= yq < y1 - 2 * RES): continue
        inbox += 1; r, c = int((y1 - yq) // RES), int((xq - x0) // RES)
        got, why = find_pool(Z_RAW, ZMAX10, wet, r, c, RES, adj_m)
        if got is None: skipped.append(dict(nid=d.get('nid'), name=d.get('name'), why=why)); continue
        cand.append((got[0], d, r, c, got))
    cand.sort(key=lambda t: -t[0])               # highest pool first: a footprint belongs to the first lake that claims it
    protect = np.zeros((ny, nx), bool); start = np.zeros((ny, nx), np.float32); weirs = []
    for P, d, r, c, (P_, seed, crest) in cand:
        if owner[seed].any():                    # same lake as a dam already done (main dam + dikes): widen that lake's spillway if NID gives more
            j = int(owner[seed][owner[seed] > 0][0]) - 1; L = lakes[j]; L['dams'].append(d.get('nid'))
            w_ = (d.get('spillway_width_ft') or 0) * 0.3048
            if w_ > L['weir_w_m'] and L.get('weir_line'):
                L['weir_w_m'] = round(min(w_, 150.0), 1)
            continue
        m = footprint(Z_RAW, P, seed) & (owner == 0)
        if m[0].any() or m[-1].any() or m[:, 0].any() or m[:, -1].any():
            skipped.append(dict(nid=d.get('nid'), name=d.get('name'), why='lake touches the box edge')); continue
        if m.sum() * RES * RES / 1e6 > max_km2:
            skipped.append(dict(nid=d.get('nid'), name=d.get('name'), why='footprint > LF_DAMS_MAX_KM2')); continue
        ns, sa = d.get('normal_storage_acft'), d.get('surface_area_acres')
        D = (ns / sa) * 0.3048 if ns and sa and sa > 0 else 1.5
        D = float(np.clip(D, dmin, dmax))
        rg = ring_of(m)
        # outlet: lowest-lidar rim cell within adj_m of the NID point (else the lowest rim cell of the whole lake)
        rr, cc = np.nonzero(rg); dd = np.hypot(rr - r, cc - c) * RES; near = dd <= max(adj_m, 2 * RES)
        pick = np.flatnonzero(near) if near.any() else np.arange(len(rr))
        io = pick[np.argmin(Z_RAW[rr[pick], cc[pick]])]; ro, co = int(rr[io]), int(cc[io])
        # rim: lidar >= P -> at least P (burn / notch / breach may stay down to the pool level, so inflowing streams and road notches still
        # pass water into the lake); lidar < P (water would leave) -> raised to the dam crest
        zr_rim = Z_RAW[rg]; low = zr_rim < P
        hi10 = np.maximum(ZMAX10, Z_RAW)
        from scipy import ndimage
        crest_loc = ndimage.maximum_filter(np.where(np.isfinite(hi10), hi10, -1e9), size=5)
        crest_rim = np.maximum(crest_loc[rg], P + 0.5)
        newz = np.where(low, crest_rim, np.maximum(Z[rg], P))
        Z[rg] = newz.astype(np.float32)
        nraised = int(low.sum()) - (1 if Z_RAW[ro, co] < P else 0)
        # lake bed and start depth
        Z[m] = np.float32(P - D); start[m] = np.float32(D); owner[m] = len(lakes) + 1
        protect |= m | rg
        # face neighbour of the outlet inside the lake
        nb = [(ro + dr, co + dc) for dr, dc in N4 if 0 <= ro + dr < ny and 0 <= co + dc < nx and m[ro + dr, co + dc]]
        rl, cl = nb[0]
        k3 = 3; cwo = float(np.max(CW[max(0, ro - k3):ro + k3 + 1, max(0, co - k3):co + k3 + 1])) if CW is not None else 0.0
        wn = (d.get('spillway_width_ft') or 0) * 0.3048
        w = wn if wn > 0 else max(cwo, 3.0); w = float(min(w, 150.0)); wsrc = 'NID spillway width' if wn > 0 else 'bankfull width at the outlet (channels30, Bieger 2015), >= 3 m'
        line = None
        if use_weir:
            Z[ro, co] = np.float32(min(float(Z[ro, co]), float(Z_RAW[ro, co]), P - 0.2))
            xc, yc = x0 + (cl + 0.5) * RES, y1 - (rl + 0.5) * RES
            tag = 'W' if co == cl + 1 else 'E' if co == cl - 1 else 'N' if ro == rl + 1 else 'S'   # input.cpp: W -> east face, E -> west, N -> south, S -> north
            line = f'{xc:.2f} {yc:.2f} {tag} {cd:.3f} {P:.3f} {mlim:.3f} {w:.2f}'; weirs.append(line)
        else:
            Z[ro, co] = np.float32(P)
        L = dict(nid=d.get('nid'), name=d.get('name'), dams=[d.get('nid')], pool_m=round(P, 2), bed_depth_m=round(D, 2),
                 depth_src='NID normal storage / surface area' if ns and sa else 'default 1.5 m', cells=int(m.sum()), area_km2=round(float(m.sum()) * RES * RES / 1e6, 3),
                 nid_area_km2=round(sa * 0.0040469, 3) if sa else None, crest_m=round(float(crest), 2), rim_raised_cells=nraised,
                 outlet=[ro, co], lake_cell=[rl, cl], weir_w_m=round(w, 1), weir_w_src=wsrc, weir_line=line,
                 nid_height_ft=d.get('nid_height_ft') or d.get('dam_height_ft'), spillway_type=d.get('spillway_type'), purposes=d.get('purposes'))
        lakes.append(L)
    if use_weir:   # widths may have been widened by a second dam on the same lake
        weirs = []
        for L in lakes:
            if L['weir_line']:
                p_ = L['weir_line'].split(); p_[-1] = f"{L['weir_w_m']:.2f}"; L['weir_line'] = ' '.join(p_); weirs.append(L['weir_line'])
    water = water | (owner > 0)
    log(f'LF_DAMS: {inbox} NID dams in the box -> {len(lakes)} lakes held at their pool level ({sum(L["area_km2"] for L in lakes):.2f} km2, '
        f'{sum(L["area_km2"] * L["bed_depth_m"] for L in lakes):.2f} Mm3 start volume), {len(skipped)} skipped; '
        + ('native weirs' if use_weir else 'DEM sill outlets (LF_DAMS_WEIR=0)'))
    for L in sorted(lakes, key=lambda L: -L['area_km2'])[:12]:
        log(f"  {L['name']} ({L['nid']}): pool {L['pool_m']} m, {L['area_km2']} km2 (NID {L['nid_area_km2']}), depth {L['bed_depth_m']} m, weir {L['weir_w_m']} m, "
            f"rim raised {L['rim_raised_cells']} cells")
    # solver damping: with theta = 1 and cfl 0.7 the local-inertial scheme grows a checkerboard oscillation in deep, flat, low-friction water
    # (Bates et al. 2010; de Almeida et al. 2012, WRR 48 W05528, who add theta < 1 for exactly this); found on a synthetic full lake with the
    # LISFLOOD-FP 8.2 CPU build (mass error, stage spread of metres) and in the Leominster run.  theta 0.7 + cfl 0.5 removed it in every test.
    par = [f'{k} {v}' for k, v in (('theta', os.environ.get('LF_DAMS_THETA', '0.7')), ('cfl', os.environ.get('LF_DAMS_CFL', '0.5'))) if v]
    return Z, water, dict(protect=protect, start=start, weirs=weirs, lakes=lakes, skipped=skipped, dams_in_box=inbox, source=src, owner=owner,
                          weir=use_weir, cd=cd, m=mlim, par=par)


def weirfile(D):
    return f"{len(D['weirs'])}\n" + ''.join(l + '\n' for l in D['weirs'])


def report(D, Zm, FR, FT):
    """Lake stage over the run from the depth snapshots (FR: uint16 cm, FT hours): peak rise above the pool, its time, the weir outflow at that
    rise (free weir: Q = Cd w H^1.5) and the rise / outflow 12 h later."""
    out = []
    for i, L in enumerate(D['lakes']):
        m = D['owner'] == i + 1
        if not FR or not m.any(): out.append(L); continue
        st = np.array([float(np.mean(Zm[m] + f[m] / 100.0)) for f in FR]); rise = st - L['pool_m']; j = int(np.argmax(rise))
        q = lambda h: round(D['cd'] * L['weir_w_m'] * max(h, 0.0) ** 1.5, 2)
        j12 = int(np.argmin(np.abs(np.asarray(FT) - (FT[j] + 12.0))))
        out.append(dict(L, peak_rise_m=round(float(rise[j]), 3), peak_h=round(float(FT[j]), 2), weir_q_peak_m3s=q(rise[j]),
                        rise_12h_after_m=round(float(rise[j12]), 3) if FT[j12] > FT[j] else None, weir_q_12h_after_m3s=q(rise[j12]) if FT[j12] > FT[j] else None,
                        rise_series_m=[round(float(v), 3) for v in rise[::2]]))
    return dict(source=D['source'], dams_in_box=D['dams_in_box'], weir=D['weir'], par=D.get('par'), cd=D['cd'], modular_limit=D['m'], lakes=out, skipped=D['skipped'])


def selftest():
    """A valley with a hydro-flattened pond behind an embankment, a burnt channel through both and a road notch on the dam."""
    res = 20.0; ny, nx = 30, 20; BOX = (0.0, 0.0, nx * res, ny * res)
    yy = np.arange(ny)[:, None] * np.ones((1, nx)); xx = np.ones((ny, 1)) * np.arange(nx)[None, :]
    ZR = (120.0 - 1.0 * yy + 0.8 * np.abs(xx - 10)).astype(np.float32)       # valley falling south (rows increase southwards)
    pond = (yy >= 5) & (yy <= 14) & (np.abs(xx - 10) <= 4); ZR[pond] = 110.0   # hydro-flattened pool at 110
    ZR[15:17, :] = np.maximum(ZR[15:17, :], 112.5)                             # dam rows 15-16, crest 112.5
    ZR[15:17, 10] = 109.6                                                       # the outlet notch in the lidar (spillway / culvert)
    Zm = ZR.copy(); chan = np.zeros((ny, nx), bool); chan[:, 10] = True; Zm[chan] -= 1.5   # channel burn through pond and dam
    water = chan.copy(); CW = np.where(chan, 6.0, 0.0).astype(np.float32)
    from pyproj import Transformer
    lon, lat = Transformer.from_crs(26986, 4326, always_xy=True).transform(10.5 * res, (ny - 15.5) * res)
    dams = [dict(nid='T1', name='test pond dam', lon=lon, lat=lat, normal_storage_acft=200.0, surface_area_acres=50.0, spillway_width_ft=30.0)]
    os.environ.setdefault('LF_DAMS_WEIR', '1')
    Z2, w2, D = apply(Zm, ZR, ZR, water, chan, CW, BOX, res, log=lambda *a: None, dams=dams)
    L = D['lakes'][0]
    assert abs(L['pool_m'] - 110.0) < 1e-3 and L['cells'] >= int(pond.sum()), L
    assert abs(L['bed_depth_m'] - 1.22) < 0.01 and np.allclose(Z2[pond], 110.0 - L['bed_depth_m'], atol=0.01) and np.allclose(D['start'][pond], L['bed_depth_m'], atol=0.01)
    ro, co = L['outlet']; assert (ro, co) == (15, 10) and Z2[ro, co] <= 109.8, (ro, co, Z2[ro, co])
    lk = D['owner'] == 1; rg = ring_of(lk); rg[ro, co] = False
    assert (Z2[rg] >= 110.0).all(), 'rim leaks'                                    # no face of the lake lower than the pool except the weir
    assert D['protect'][pond].all() and D['protect'][15, 10] and w2[pond].all()
    p_ = D['weirs'][0].split(); assert p_[2] == 'N' and abs(float(p_[4]) - 110.0) < 1e-3 and abs(float(p_[6]) - 9.14) < 0.05     # outlet south of the lake cell
    # lake cell (14,10), outlet south of it: input.cpp tag 'N' -> Identy[xi + (yi+1)(xsz+1)], the face to p1 = row yi + 1
    return D


if __name__ == '__main__':
    selftest(); print('lf_dams selftest passed')
