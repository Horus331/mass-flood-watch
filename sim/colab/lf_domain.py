"""Watershed-shaped model domains for w9_lisflood.py (LF_DOMAIN=basin).

A square box cuts river basins: half of the Leominster and Fitchburg gauges' watersheds lay outside the 20 km box, so their rivers got
no upstream water.  A basin domain is a bounding box plus a mask: every cell that drains (on the model's own DEM) to a chosen outlet, plus a
short downstream river corridor to the box edge.  Cells outside the mask are written as NODATA in dem.asc.

How LISFLOOD-FP 8.2 treats NODATA cells (tools/lisflood_src):
  * input.cpp LoadDEMData: a DEM value equal to the file's NODATA_value becomes Pars.nodata_elevation (default DEM_NO_DATA = 1e7 m), a wall.
  * rain/rain.tpp: no rain is added where DEM == nodata_elevation; infevap.cpp skips them for infiltration; the GPU ACC solver
    (cuda/acc/cuda_acc_solver.cu) and cuda_rain.cu skip them explicitly.
  * fp_acc.cpp: hflow = max(z0 + h0, z1 + h1) - max(z0, z1) = 0 on any face next to a 1e7 m cell, so no water crosses it; fp_flow.cpp only
    computes a face flux when one side is wet (h > DepthThresh), so dry wall cells cost only the full-grid passes (UpdateQs, CalcMaxH,
    DryCheck, boundaries).  drain_nodata (off by default) is not needed: water never reaches a wall cell.
  * Point FREE boundaries (bci 'P x y FREE') exist only for the sub-grid channel model, so an outlet must sit on a box edge: the corridor
    carries the river from the outlet to the edge, and only those edge cells get FREE.  Every other edge cell is closed (LISFLOOD-FP default).
    Basin divides have no inflow, so closed is the right condition there.

Domain file (JSON, EPSG:26986): box, polygons (rings), outlets (gauge points), auto_outlets, pad_m.  The mask itself is made at run time on
the run grid (any RES), from the polygons and the run's DEM:
  1. rasterise the polygons (NLDI gauge basins, WBD HU8/HU10/HU12 units) -> M0;
  2. priority-flood routing on the DEM after channel burn and crossing notches, before depression breaching (Barnes et al. 2014),
     4-connected when LF_BREACH_D4=1 (the solver's face fluxes) else 8-connected;
  3. each outlet snaps to the largest-accumulation cell within LF_DOMAIN_SNAP_M (150 m); with auto_outlets, every place where M0's flow
     leaves M0 and that drains >= LF_DOMAIN_MIN_KM2 of M0 is an outlet too (HU12 sets, storm areas);
  4. mask = cells draining to an outlet on the DEM (so every masked-in cell has a surface path out) + the corridor: the flow path from each
     outlet to the box edge, widened by LF_DOMAIN_CORRIDOR_M on each side; FREE on the corridor's edge cells;
  5. w9 sets masked-out cells to WALL before breaching (carved outlets then lead to the basin outlet, never across a divide) and to NODATA
     in dem.asc; hmax / frames are zero there; z.npy keeps the lidar DEM there; out/domain_mask.npy + meta.json['domain'] record it.

    python sim/colab/lf_domain.py fetch --sites 01094500,01094400 --wbd-box 88000,816000,246000,986000 --levels 8,10,12   (Actions: basins.yml)
    python sim/colab/lf_domain.py build --name leominster_nn --sites 01094500 [--extra-outlets 01094400] [--pad 2000]
    python sim/colab/lf_domain.py build --name d3_hu8 --hu 8 --region 128000,856000,206000,946000
    python sim/colab/lf_domain.py build --name d3_storm --hu 12 --region 128000,856000,206000,946000 --rain-npz <run>/rainstats.npz --rain-min 75
    python sim/colab/lf_domain.py check --domain docs/network/basins/domain_leominster_nn.json --z <run>/z.npy --box-of <run>/meta.json
    python sim/colab/lf_domain.py --selftest
"""
import os, sys, json, math, time, heapq, argparse
import numpy as np

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
BASINS = os.path.join(ROOT, 'docs', 'network', 'basins')
WALL = 1.0e4                         # m, masked-out cells during breaching (above any ground in New England); NODATA in dem.asc
N4 = ((-1, 0), (0, -1), (0, 1), (1, 0))
N8 = ((-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1))
NLDI = ['https://api.water.usgs.gov/nldi/linked-data', 'https://labs.waterdata.usgs.gov/api/nldi/linked-data']
WBD = 'https://hydro.nationalmap.gov/arcgis/rest/services/wbd/MapServer/{layer}/query'
WBD_LAYER = {2: 1, 4: 2, 6: 3, 8: 4, 10: 5, 12: 6}
UA = {'User-Agent': 'mass-flood-watch research (github.com/Horus331/mass-flood-watch)'}
D3_BOX = (128000.0, 856000.0, 206000.0, 946000.0)     # MassDOT District 3 extent used in proto/turing/run_storm.slurm


# ======================================================================================================================
# fetch (GitHub Actions: the sandbox cannot reach USGS)
# ======================================================================================================================
def _get(url, params=None, tries=5, timeout=180):
    import requests
    for k in range(tries):
        try:
            r = requests.get(url, params=params, headers=UA, timeout=timeout)
            if r.status_code == 200: return r.json()
            print('  HTTP', r.status_code, url[-90:], r.text[:150], flush=True)
            if r.status_code in (400, 404): return None
        except Exception as e:
            print('  retry', k, repr(e)[:120], flush=True)
        time.sleep(5 + 10 * k)
    return None


def fetch_site(site, out):
    """NLDI split-catchment basin upstream of the gauge + the gauge point -> <out>/USGS-<site>.geojson (EPSG:4326)."""
    B, P, used = None, None, None
    for base in NLDI:
        P = P or _get(f'{base}/nwissite/USGS-{site}')
        for split in ('true', 'false'):
            B = _get(f'{base}/nwissite/USGS-{site}/basin', dict(splitCatchment=split, simplified='false'))
            if B and B.get('features'): used = (base, split); break
        if used: break
    if not used: print(f'{site}: no NLDI basin'); return None
    feats = []
    for f in B['features']:
        f.setdefault('properties', {}); f['properties'].update(kind='nldi_basin', site=site, split_catchment=used[1] == 'true'); feats.append(f)
    for f in (P or {}).get('features', []):
        f.setdefault('properties', {}); f['properties']['kind'] = 'nwissite'; f['properties']['site'] = site; feats.append(f)
    G = dict(type='FeatureCollection', features=feats, source=f'{used[0]}/nwissite/USGS-{site}/basin?splitCatchment={used[1]}', fetched=time.strftime('%Y-%m-%d'))
    p = os.path.join(out, f'USGS-{site}.geojson'); json.dump(G, open(p, 'w'), separators=(',', ':'))
    a = sum(polygon_area_km2(project_rings(g)) for g in geometries(G, 'nldi_basin'))
    print(f'{site}: basin {a:.1f} km2 ({used[1]} split) -> {p}', flush=True)
    return a


def fetch_wbd(level, box, out, tag):
    """WBD hydrologic units of one level intersecting box (EPSG:26986) -> <out>/wbd_hu<level>_<tag>.geojson (EPSG:4326, ~20 m generalised)."""
    x0, y0, x1, y1 = box; url = WBD.format(layer=WBD_LAYER[level]); feats, off = [], 0
    geom = json.dumps(dict(xmin=x0, ymin=y0, xmax=x1, ymax=y1, spatialReference=dict(wkid=26986)))
    fields = f'huc{level},name,areasqkm' + (',tohuc' if level == 12 else '')
    while True:
        G = None
        for flds in (fields, '*'):
            G = _get(url, dict(where='1=1', geometry=geom, geometryType='esriGeometryEnvelope', inSR=26986, spatialRel='esriSpatialRelIntersects',
                               outFields=flds, returnGeometry='true', outSR=4326, f='geojson', resultOffset=off, resultRecordCount=200,
                               orderByFields=f'huc{level}', maxAllowableOffset=0.0002, geometryPrecision=5), timeout=300)
            if G and 'features' in G: break
        if not G: raise SystemExit(f'WBD HU{level} unreachable')
        fs = G.get('features', []); feats += fs; off += len(fs)
        if len(fs) < 200: break
    for f in feats:
        pr = {k.lower(): v for k, v in (f.get('properties') or {}).items()}
        f['properties'] = dict(kind=f'hu{level}', huc=str(pr.get(f'huc{level}')), name=pr.get('name'), areasqkm=pr.get('areasqkm'), tohuc=pr.get('tohuc'))
    p = os.path.join(out, f'wbd_hu{level}_{tag}.geojson')
    json.dump(dict(type='FeatureCollection', features=feats, source=url, box_epsg26986=list(box), fetched=time.strftime('%Y-%m-%d')), open(p, 'w'), separators=(',', ':'))
    print(f'HU{level}: {len(feats)} units -> {p}', flush=True)


# ======================================================================================================================
# geometry helpers (no shapely: numpy + pyproj + PIL, all in the w9 / Turing environments)
# ======================================================================================================================
def geometries(G, kind=None):
    """Polygon geometries (list of polygons, each a list of rings [(lon, lat), ...]) of a FeatureCollection, optionally by properties.kind."""
    out = []
    for f in G.get('features', []):
        if kind and (f.get('properties') or {}).get('kind') != kind: continue
        g = f.get('geometry') or {}
        if g.get('type') == 'Polygon': out.append(g['coordinates'])
        elif g.get('type') == 'MultiPolygon': out += g['coordinates']
    return out


def project_rings(poly, tf=None):
    """[(lon, lat) rings] -> [np.array (n, 2) EPSG:26986 rings]."""
    if tf is None:
        from pyproj import Transformer
        tf = Transformer.from_crs(4326, 26986, always_xy=True)
    out = []
    for ring in poly:
        a = np.asarray(ring, float)[:, :2]; x, y = tf.transform(a[:, 0], a[:, 1]); out.append(np.c_[x, y])
    return out


def polygon_area_km2(rings):
    """Shoelace area of a polygon (first ring exterior, the rest holes), km2."""
    def sh(r): r = np.asarray(r, float); return 0.5 * abs(np.dot(r[:-1, 0], r[1:, 1]) - np.dot(r[1:, 0], r[:-1, 1]))
    return (sh(rings[0]) - sum(sh(r) for r in rings[1:])) / 1e6 if len(rings) else 0.0


def rasterize(polys, box, res, shape=None):
    """Cells whose centre lies inside any polygon (EPSG:26986 rings, first exterior, rest holes) on the grid of box/res (rows north -> south)."""
    from PIL import Image, ImageDraw
    x0, y0, x1, y1 = box
    ny, nx = shape if shape else (int(round((y1 - y0) / res)), int(round((x1 - x0) / res)))
    M = np.zeros((ny, nx), bool); base = Image.new('1', (nx, ny), 0); dr = ImageDraw.Draw(base)
    def pix(r): r = np.asarray(r, float); return [((x - x0) / res - 0.5, (y1 - y) / res - 0.5) for x, y in r]
    for rings in polys:
        if len(rings) == 1:
            if len(rings[0]) >= 3: dr.polygon(pix(rings[0]), fill=1, outline=1)
            continue
        im = Image.new('1', (nx, ny), 0); d = ImageDraw.Draw(im); d.polygon(pix(rings[0]), fill=1, outline=1)
        for h in rings[1:]:
            if len(h) >= 3: d.polygon(pix(h), fill=0, outline=0)
        M |= np.asarray(im, bool)
    return M | np.asarray(base, bool)


# ======================================================================================================================
# routing on the run DEM
# ======================================================================================================================
def priority_flood(Z, nb=N8):
    """Priority-flood from the grid edge (Barnes et al. 2014): parent (downstream cell, -1 on the edge) of every cell and the pop order
    (parents before children: a topological order)."""
    ny, nx = Z.shape; F = np.asarray(Z, np.float64).ravel(); seen = np.zeros(Z.size, bool); par = np.full(Z.size, -1, np.int64)
    order = np.empty(Z.size, np.int64); n = 0
    e = np.zeros(Z.shape, bool); e[[0, -1], :] = True; e[:, [0, -1]] = True; ek = np.flatnonzero(e)
    hq = [(float(F[k]), int(k)) for k in ek]; heapq.heapify(hq); seen[ek] = True
    lvl = F.copy(); push, pop = heapq.heappush, heapq.heappop
    while hq:
        f, k = pop(hq); order[n] = k; n += 1; r, c = divmod(k, nx)
        for dr, dc in nb:
            rr, cc = r + dr, c + dc
            if 0 <= rr < ny and 0 <= cc < nx:
                kk = rr * nx + cc
                if not seen[kk]:
                    seen[kk] = True; par[kk] = k; v = lvl[kk]
                    if v < f: v = f; lvl[kk] = f
                    push(hq, (v, kk))
    return par, order[:n]


def accumulate(par, order, w=None):
    """Upstream sum of w (default 1 per cell) at every cell."""
    acc = np.ones(par.size) if w is None else np.asarray(w, np.float64).ravel().copy()
    for k in order[::-1]:
        p = par[k]
        if p >= 0: acc[p] += acc[k]
    return acc


def label_down(par, order, seeds):
    """lab[k] = id of the first seed met going downstream from k (0 if none).  seeds: {cell index: id}."""
    lab = np.zeros(par.size, np.int32)
    for k, i in seeds.items(): lab[k] = i
    for k in order:                       # parents come first, so lab[par[k]] is final when k is visited
        if lab[k] == 0:
            p = par[k]
            if p >= 0: lab[k] = lab[p]
    return lab


def edge_bci(free, box, res, kind='FREE'):
    """bci lines (FREE) for the True cells of the four edges of `free` (ny, nx), contiguous runs merged.  Coordinates are cell centres
    chosen so LISFLOOD-FP's LoadBCs (input.cpp) maps each run to exactly its cells: N col c -> index c, E row r -> X + r,
    S col c -> 2X + Y - 1 - c, W row r -> 2X + 2Y - 1 - r (boundary.cpp), with BCi2 = floor(finish index) - 1."""
    x0, y0, x1, y1 = box; ny, nx = free.shape; L = []
    def runs(v):
        idx = np.flatnonzero(v); out = []
        if idx.size == 0: return out
        s = p = int(idx[0])
        for i in idx[1:]:
            i = int(i)
            if i != p + 1: out.append((s, p)); s = i
            p = i
        return out + [(s, p)]
    xc = lambda c: x0 + (c + 0.5) * res; yc = lambda r: y1 - (r + 0.5) * res
    for a, b in runs(free[0]): L.append(f'N {xc(a):.1f} {xc(b + 1):.1f} {kind}')
    for a, b in runs(free[:, -1]): L.append(f'E {yc(a):.1f} {yc(b + 1):.1f} {kind}')
    for a, b in runs(free[-1]): L.append(f'S {xc(a - 1):.1f} {xc(b):.1f} {kind}')
    for a, b in runs(free[:, 0]): L.append(f'W {yc(a - 1):.1f} {yc(b):.1f} {kind}')
    return L


def lisflood_bci_cells(lines, box, res, ny, nx):
    """Emulation of LISFLOOD-FP LoadBCs + boundary.cpp edge numbering: which edge cells (r, c) each bci line covers (selftest)."""
    x0, y0, x1, y1 = box; X, Y = nx, ny; blx, tly = x0, y0 + ny * res; cells = set()
    for ln in lines:
        s, a, b = ln.split()[0], float(ln.split()[1]), float(ln.split()[2])
        if s in 'NS': a, b = [min(max(v, blx), blx + X * res) for v in (a, b)]
        else: a, b = [min(max(v, y0), tly) for v in (a, b)]
        f = {'N': lambda v: (v - blx) / res, 'E': lambda v: X + (tly - v) / res, 'S': lambda v: 2 * X + Y - (v - blx) / res,
             'W': lambda v: 2 * X + 2 * Y - (tly - v) / res}[s]
        i1, i2 = int(math.floor(f(a) + 1e-9)), int(math.floor(f(b) + 1e-9))
        i1, i2 = min(i1, i2), max(i1, i2) - 1
        for i in range(i1, i2 + 1):
            if i <= X - 1: cells.add((0, i))
            elif i <= X + Y - 1: cells.add((i - X, X - 1))
            elif i <= 2 * X + Y - 1: cells.add((Y - 1, 2 * X + Y - 1 - i))
            else: cells.add((2 * X + 2 * Y - 1 - i, 0))
    return cells


# ======================================================================================================================
# run time (called from w9 build_inputs when LF_DOMAIN=basin)
# ======================================================================================================================
def load(path):
    D = json.load(open(path)); D['_path'] = path; return D


def prepare(D, Z, box, res, d4=False, log=print, env=os.environ):
    """-> dict(mask (ny, nx) bool, bci (list of FREE lines), report).  Z: the run DEM after channel burn and crossing notches, before breaching."""
    t = time.time(); ny, nx = Z.shape; x0, y0, x1, y1 = box; cell_km2 = res * res / 1e6
    snap = float(env.get('LF_DOMAIN_SNAP_M', '150')); cw = int(math.ceil(float(env.get('LF_DOMAIN_CORRIDOR_M', '200')) / res))
    min_km2 = float(env.get('LF_DOMAIN_MIN_KM2', str(D.get('min_outlet_km2', 1.0))))
    polys = [[np.asarray(r, float) for r in p['rings']] for p in D['polygons']]
    M0 = rasterize(polys, box, res, (ny, nx)) if polys else np.zeros((ny, nx), bool)
    par, order = priority_flood(Z, N4 if d4 else N8); acc = accumulate(par, order)
    log(f'domain: routing {"4" if d4 else "8"}-connected on {ny * nx / 1e6:.2f} M cells, {time.time() - t:.0f}s; polygons {M0.sum() * cell_km2:.1f} km2')
    seeds, outs = {}, []
    k_ = int(math.ceil(snap / res))
    for o in D.get('outlets', []):
        if not (x0 <= o['x'] < x1 and y0 <= o['y'] < y1): log('domain: outlet outside the box', o); continue
        r, c = int((y1 - o['y']) // res), int((o['x'] - x0) // res)
        w = acc.reshape(ny, nx)[max(0, r - k_):r + k_ + 1, max(0, c - k_):c + k_ + 1]; i = np.unravel_index(int(np.argmax(w)), w.shape)
        kk = (max(0, r - k_) + i[0]) * nx + max(0, c - k_) + i[1]
        if kk in seeds: continue
        seeds[kk] = len(seeds) + 1; outs.append(dict(o, cell=[int(kk // nx), int(kk % nx)], kind=o.get('kind', 'gauge')))
    lab = label_down(par, order, seeds)
    if D.get('auto_outlets') and M0.any():
        rest = M0.ravel() & (lab == 0); accM = accumulate(par, order, rest)
        pr = par.copy(); ex = np.flatnonzero(rest & ((pr < 0) | ~M0.ravel()[np.maximum(pr, 0)]))
        ex = ex[np.argsort(-accM[ex])]
        for kk in ex:
            a = accM[kk] * cell_km2
            if a < min_km2: break
            if lab[kk]: continue
            seeds[int(kk)] = len(seeds) + 1; outs.append(dict(id=f'auto{len(seeds)}', x=x0 + (kk % nx + 0.5) * res, y=y1 - (kk // nx + 0.5) * res,
                                                             cell=[int(kk // nx), int(kk % nx)], kind='auto', polygon_km2_drained=round(a, 1)))
            lab = label_down(par, order, {k: i for k, i in seeds.items()})
    C = (lab > 0).reshape(ny, nx)
    # corridors: outlet -> box edge along the routing, stopping where the path re-enters the domain (nested outlets)
    path = np.zeros((ny, nx), bool); Cf = C.ravel()
    for o, kk in zip(outs, seeds):
        p = int(par[kk]); n = 0; end = 'edge' if p < 0 else None
        while p >= 0 and not Cf[p]:
            path.flat[p] = True; n += 1
            if par[p] < 0: end = 'edge'; break
            p = int(par[p])
        else:
            end = end or 'domain'
        if p < 0: path.flat[kk] = True                   # the outlet itself is an edge cell
        o.update(area_km2=round(float((lab == seeds[kk]).sum() * cell_km2), 1), corridor_cells=n, corridor_km=round(n * res / 1000, 1), corridor_end=end)
    if path.any():
        from scipy import ndimage
        yy, xx = np.mgrid[-cw:cw + 1, -cw:cw + 1]; corridor = ndimage.binary_dilation(path, structure=(yy * yy + xx * xx) <= cw * cw) & ~C
    else:
        corridor = np.zeros_like(C)
    mask = C | corridor
    edge = np.zeros((ny, nx), bool); edge[[0, -1], :] = True; edge[:, [0, -1]] = True
    free = corridor & edge
    for kk in seeds: free.flat[kk] |= bool(edge.flat[kk])          # an outlet that is itself an edge cell
    bci = edge_bci(free, box, res)
    inter = float((M0 & C).sum()); uni = float((M0 | C).sum())
    rep = dict(file=os.path.relpath(D.get('_path', ''), ROOT) if D.get('_path') else None, name=D.get('name'), box=list(box), res_m=res,
               connectivity=4 if d4 else 8, cells_box=int(ny * nx), cells_active=int(mask.sum()), active_share=round(float(mask.mean()), 3),
               area_km2=dict(mask=round(float(mask.sum() * cell_km2), 1), catchments=round(float(C.sum() * cell_km2), 1),
                             corridor=round(float(corridor.sum() * cell_km2), 2), polygons=round(float(M0.sum() * cell_km2), 1)),
               polygon_dem_iou=round(inter / uni, 3) if uni else None, polygon_share_in_catchments=round(inter / max(float(M0.sum()), 1), 3),
               catchment_cells_on_closed_edge=int((C & edge).sum()), free_edge_cells=int(free.sum()), bci=bci, outlets=outs,
               corridor_half_width_m=cw * res, snap_m=snap, seconds=round(time.time() - t))
    log(f"domain {D.get('name')}: {rep['cells_active']:,} of {ny * nx:,} cells active ({rep['active_share'] * 100:.0f}%), catchments {rep['area_km2']['catchments']} km2 "
        f"(polygons {rep['area_km2']['polygons']}, IoU {rep['polygon_dem_iou']}), {len(outs)} outlets "
        + ', '.join(f"{o.get('site') or o['id']} {o['area_km2']} km2 corridor {o['corridor_km']} km to {o['corridor_end']}" for o in outs)
        + f"; FREE on {rep['free_edge_cells']} edge cells: {bci}; {rep['seconds']}s")
    return dict(mask=mask, bci=bci, report=rep)


# ======================================================================================================================
# build a domain file from fetched basins / hydrologic units
# ======================================================================================================================
def _read(p): return json.load(open(p))


def _units(level, basedir):
    fs = []
    for p in sorted(os.listdir(basedir)):
        if p.startswith(f'wbd_hu{level}_') and p.endswith('.geojson'): fs += _read(os.path.join(basedir, p))['features']
    U = {}
    for f in fs:
        h = f['properties']['huc']
        if h not in U: U[h] = f
    return U


def build(name, sites=(), extra_outlets=(), hu=None, region=None, rain_npz=None, rain_min=None, huc_ids=(), pad=2000.0, snap_box=1000.0,
          basedir=BASINS, upstream=True):
    from pyproj import Transformer
    tf = Transformer.from_crs(4326, 26986, always_xy=True)
    polys, outlets, src = [], [], []
    for s in sites:
        G = _read(os.path.join(basedir, f'USGS-{s}.geojson')); src.append(f'USGS-{s}.geojson')
        for g in geometries(G, 'nldi_basin'):
            R = project_rings(g, tf); polys.append(dict(id=f'USGS-{s}', kind='nldi', area_km2=round(polygon_area_km2(R), 1), rings=[r.round(1).tolist() for r in R]))
    for s in list(sites) + list(extra_outlets):
        G = _read(os.path.join(basedir, f'USGS-{s}.geojson'))
        pt = [f for f in G['features'] if f['properties'].get('kind') == 'nwissite' and (f.get('geometry') or {}).get('type') == 'Point']
        if not pt: raise SystemExit(f'{s}: no gauge point in USGS-{s}.geojson')
        lon, lat = pt[0]['geometry']['coordinates'][:2]; x, y = tf.transform(lon, lat)
        outlets.append(dict(id=f'USGS-{s}', site=s, name=pt[0]['properties'].get('name'), x=round(x, 1), y=round(y, 1), kind='gauge'))
    sel = []
    if hu:
        U = _units(hu, basedir); src.append(f'wbd_hu{hu}_*.geojson')
        if huc_ids: sel = [h for h in huc_ids if h in U]
        else:
            # units intersecting region (and the storm area: cells with total rain >= rain_min), tested on a 250 m grid
            rb = tuple(region) if region else D3_BOX; g = 250.0
            A = np.ones((int((rb[3] - rb[1]) / g), int((rb[2] - rb[0]) / g)), bool)
            if rain_npz:
                R = np.load(rain_npz); meta = json.load(open(os.path.join(os.path.dirname(rain_npz), 'meta.json'))); bx = meta['box']; rs = meta['res_m']
                T = R['total']; yy = rb[3] - (np.arange(A.shape[0]) + 0.5) * g; xx = rb[0] + (np.arange(A.shape[1]) + 0.5) * g
                ri = ((bx[3] - yy) // rs).astype(int); ci = ((xx - bx[0]) // rs).astype(int)
                ok = (ri[:, None] >= 0) & (ri[:, None] < T.shape[0]) & (ci[None] >= 0) & (ci[None] < T.shape[1])
                A &= ok & (T[np.clip(ri, 0, T.shape[0] - 1)][:, np.clip(ci, 0, T.shape[1] - 1)] >= float(rain_min))
                src.append(f'storm area: total rain >= {rain_min} mm in {os.path.relpath(rain_npz, ROOT)}')
            for h, f in U.items():
                for gm in geometries(dict(features=[f])):
                    if (rasterize([project_rings(gm, tf)], rb, g, A.shape) & A).any(): sel.append(h); break
        if upstream and hu == 12:          # close the set upstream with the WBD tohuc links: a domain must hold everything that drains into it
            up = {}
            for h, f in U.items(): up.setdefault(str(f['properties'].get('tohuc')), []).append(h)
            todo = list(sel); seen = set(sel)
            while todo:
                for h in up.get(todo.pop(), []):
                    if h not in seen: seen.add(h); todo.append(h); sel.append(h)
        for h in sel:
            for gm in geometries(dict(features=[U[h]])):
                R = project_rings(gm, tf); polys.append(dict(id=f'HU{hu}-{h}', kind=f'hu{hu}', name=U[h]['properties'].get('name'), area_km2=round(polygon_area_km2(R), 1),
                                                         rings=[r.round(1).tolist() for r in R]))
    if not polys: raise SystemExit('nothing selected')
    xs = np.concatenate([np.asarray(p['rings'][0])[:, 0] for p in polys]); ys = np.concatenate([np.asarray(p['rings'][0])[:, 1] for p in polys])
    box = [math.floor((xs.min() - pad) / snap_box) * snap_box, math.floor((ys.min() - pad) / snap_box) * snap_box,
           math.ceil((xs.max() + pad) / snap_box) * snap_box, math.ceil((ys.max() + pad) / snap_box) * snap_box]
    for o in outlets:
        if not (box[0] <= o['x'] < box[2] and box[1] <= o['y'] < box[3]): raise SystemExit(f'outlet {o["id"]} outside {box}')
    # union area on a 50 m grid (polygons overlap: nested gauges, HU levels)
    U50 = rasterize([[np.asarray(r) for r in p['rings']] for p in polys], box, 50.0)
    D = dict(name=name, crs='EPSG:26986', box=box, pad_m=pad, polygons=polys, outlets=outlets, auto_outlets=bool(hu), min_outlet_km2=1.0,
             union_km2=round(float(U50.sum() * 0.0025), 1), box_km2=round((box[2] - box[0]) * (box[3] - box[1]) / 1e6, 1),
             hucs=sel, sources=src, made=time.strftime('%Y-%m-%d'),
             note='EPSG:26986 rings (first exterior, rest holes). The model mask is made at run time on the run grid by sim/colab/lf_domain.py prepare: '
                  'cells draining on the run DEM to the outlets (gauges; auto = where the polygon union drains out) + a river corridor to the box edge.')
    return D


def cells_table(D, res_list=(20, 10)):
    rows = []
    for r in res_list:
        rows.append(dict(res_m=r, box_cells_M=round(D['box_km2'] * 1e6 / r / r / 1e6, 2), active_cells_M=round(D['union_km2'] * 1e6 / r / r / 1e6, 2)))
    return rows


# ======================================================================================================================
def selftest():
    import tempfile
    ok = []
    # 1. rasterise: a square with a hole, cell centres
    sq = [np.array([[0, 0], [100, 0], [100, 100], [0, 100], [0, 0]], float), np.array([[40, 40], [60, 40], [60, 60], [40, 60], [40, 40]], float)]
    M = rasterize([sq], (0, 0, 200, 200), 10)
    assert M.shape == (20, 20) and M[19, 0] and M[10, 9] and not M[9, 10] and not M[5, 15] and abs(M.sum() - 96) <= 12, M.sum()
    assert abs(polygon_area_km2(sq) - 0.0096) < 1e-9; ok.append('rasterise polygon with hole (cell centres) + shoelace area')
    # 2. routing: two valleys draining south, divide at column 10; outlet on valley A only
    ny, nx = 30, 21; yy, xx = np.mgrid[0:ny, 0:nx].astype(float)
    Z = 100 - 2.0 * yy + 0.8 * np.abs(xx - 5) * (xx <= 10) + 0.8 * np.abs(xx - 15) * (xx > 10) + 6 * (xx == 10) + 50 * ((xx == 0) | (xx == nx - 1) | (yy == 0))
    Z[1:, 5] -= 2.0; Z[1:, 15] -= 2.0                                         # burnt channels
    Z[29, :] += 50; Z[29, 5] = Z[28, 5] - 0.5; Z[29, 15] = Z[28, 15] - 0.5; Z = Z.astype(np.float32)
    Z[12, 7] -= 3.0                                                           # a pit inside valley A
    res = 20.0; box = (0.0, 0.0, nx * res, ny * res)
    for d4 in (False, True):
        par, order = priority_flood(Z, N4 if d4 else N8)
        assert len(order) == ny * nx and (par[order[0]] == -1)
        acc = accumulate(par, order); assert acc.max() <= ny * nx
        o = dict(id='A', x=(5 + 0.5) * res, y=box[3] - (27 + 0.5) * res)
        D = dict(name='t', box=list(box), polygons=[dict(rings=[[[0, 0], [10 * res, 0], [10 * res, ny * res], [0, ny * res], [0, 0]]])], outlets=[o])
        P = prepare(D, Z, box, res, d4=d4, log=lambda *a: None, env=dict(LF_DOMAIN_CORRIDOR_M='20', LF_DOMAIN_SNAP_M='40'))
        m = P['mask']
        assert m[12, 7] and m[5, 3] and not m[5, 15] and not m[5, 12], ('valley A in, valley B out', d4, m.astype(int))
        assert P['report']['outlets'][0]['corridor_end'] == 'edge' and m[29, 5] and P['report']['free_edge_cells'] >= 1
        cells = lisflood_bci_cells(P['bci'], box, res, ny, nx)
        fe = {(int(r), int(c)) for r, c in zip(*np.nonzero(P['mask'] & np.pad(np.zeros((ny - 2, nx - 2), bool), 1, constant_values=True)))}
        assert cells == fe, (cells, fe)
    ok.append('priority-flood routing, outlet snap, catchment mask (other valley excluded), corridor to the edge (4- and 8-connected)')
    # 3. bci emulation on every edge, runs at corners and in the middle
    F = np.zeros((7, 9), bool); F[0, 0:3] = True; F[0, 6] = True; F[2:5, -1] = True; F[-1, 3:9] = True; F[0:2, 0] = True; F[5:7, 0] = True
    L = edge_bci(F, (1000.0, 2000.0, 1000 + 9 * 30.0, 2000 + 7 * 30.0), 30.0)
    got = lisflood_bci_cells(L, (1000.0, 2000.0, 1000 + 9 * 30.0, 2000 + 7 * 30.0), 30.0, 7, 9)
    want = {(int(r), int(c)) for r, c in zip(*np.nonzero(F))}
    assert got == want, (sorted(got ^ want), L); ok.append('FREE edge segments map to exactly the corridor edge cells under LoadBCs indexing (N/E/S/W)')
    # 4. auto outlets: polygon over both valleys, no gauge -> two outlets, both corridors
    D = dict(name='t2', box=list(box), polygons=[dict(rings=[[[0, 0], [nx * res, 0], [nx * res, ny * res], [0, ny * res], [0, 0]]])], outlets=[], auto_outlets=True)
    P = prepare(D, Z, box, res, log=lambda *a: None, env=dict(LF_DOMAIN_MIN_KM2='0.02'))
    assert len(P['report']['outlets']) >= 2 and P['mask'][5, 3] and P['mask'][5, 15]; ok.append('automatic outlets where a polygon set drains out')
    # 5. label_down with nested seeds
    par = np.array([-1, 0, 1, 2, 3]); order = np.arange(5); lab = label_down(par, order, {1: 1, 3: 2})
    assert list(lab) == [0, 1, 1, 2, 2]; ok.append('nested outlets label to the nearest downstream seed')
    # 6. build from fake fetched files
    d = tempfile.mkdtemp(prefix='lfd_')
    ring = [[-71.80, 42.50], [-71.70, 42.50], [-71.70, 42.58], [-71.80, 42.58], [-71.80, 42.50]]
    json.dump(dict(type='FeatureCollection', features=[dict(type='Feature', properties=dict(kind='nldi_basin', site='0'), geometry=dict(type='Polygon', coordinates=[ring])),
                                                       dict(type='Feature', properties=dict(kind='nwissite', site='0', name='g'), geometry=dict(type='Point', coordinates=[-71.70, 42.50]))]),
              open(f'{d}/USGS-0.geojson', 'w'))
    D = build('x', sites=['0'], basedir=d)
    assert D['box'][0] % 1000 == 0 and 70 < D['union_km2'] < 80 and D['outlets'][0]['site'] == '0' and D['box_km2'] > D['union_km2']
    ok.append('build: NLDI basin -> EPSG:26986 polygon, gauge outlet, padded box snapped to 1 km')
    for o in ok: print('ok  ', o)
    print(f'LF_DOMAIN SELFTEST PASSED ({len(ok)} checks)')


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    sub = ap.add_subparsers(dest='cmd')
    f = sub.add_parser('fetch'); f.add_argument('--sites', default=''); f.add_argument('--wbd-box'); f.add_argument('--levels', default='8,10,12')
    f.add_argument('--tag', default='d3'); f.add_argument('--out', default=BASINS)
    b = sub.add_parser('build'); b.add_argument('--name', required=True); b.add_argument('--sites', default=''); b.add_argument('--extra-outlets', default='')
    b.add_argument('--hu', type=int); b.add_argument('--hucs', default=''); b.add_argument('--region'); b.add_argument('--rain-npz'); b.add_argument('--rain-min', type=float)
    b.add_argument('--pad', type=float, default=2000.0); b.add_argument('--no-upstream', action='store_true'); b.add_argument('--out')
    c = sub.add_parser('check'); c.add_argument('--domain', required=True); c.add_argument('--z', required=True); c.add_argument('--box-of', required=True); c.add_argument('--d4', action='store_true')
    ap.add_argument('--selftest', action='store_true')
    a = ap.parse_args()
    if a.selftest: return selftest()
    if a.cmd == 'fetch':
        os.makedirs(a.out, exist_ok=True)
        for s in [s for s in a.sites.split(',') if s]: fetch_site(s, a.out)
        if a.wbd_box:
            box = tuple(float(v) for v in a.wbd_box.split(','))
            for lv in [int(v) for v in a.levels.split(',') if v]: fetch_wbd(lv, box, a.out, a.tag)
    elif a.cmd == 'build':
        sp = lambda s: [v for v in s.split(',') if v]
        D = build(a.name, sp(a.sites), sp(a.extra_outlets), a.hu, tuple(float(v) for v in a.region.split(',')) if a.region else None, a.rain_npz, a.rain_min,
                  sp(a.hucs), a.pad, upstream=not a.no_upstream)
        out = a.out or os.path.join(BASINS, f'domain_{a.name}.json'); json.dump(D, open(out, 'w'), separators=(',', ':'))
        print(json.dumps({k: v for k, v in D.items() if k not in ('polygons',)}, indent=0)[:3000]); print('cells:', cells_table(D)); print('->', out)
    elif a.cmd == 'check':
        meta = json.load(open(a.box_of)); Z = np.load(a.z).astype(np.float32); D = load(a.domain)
        # a run DEM of another box: cut / pad it onto the domain box (NaN outside -> WALL so routing stays inside)
        bx, rs = meta['box'], meta['res_m']; db = D['box']; ny, nx = int(round((db[3] - db[1]) / rs)), int(round((db[2] - db[0]) / rs))
        Zd = np.full((ny, nx), WALL, np.float32); r0 = int(round((bx[3] - db[3]) / rs)); c0 = int(round((db[0] - bx[0]) / rs))
        rr = np.arange(ny) + r0; cc = np.arange(nx) + c0; okr = (rr >= 0) & (rr < Z.shape[0]); okc = (cc >= 0) & (cc < Z.shape[1])
        Zd[np.ix_(okr, okc)] = Z[np.ix_(rr[okr], cc[okc])]
        P = prepare(D, Zd, tuple(db), rs, d4=a.d4)
        print(json.dumps({k: v for k, v in P['report'].items()}, indent=1, default=str))
    else:
        ap.print_help()


if __name__ == '__main__':
    main()
