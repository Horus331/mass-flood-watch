"""Vermont, July 10-11 2023 flood: every input w9_lisflood.py and proto/prototype.py need, fetched from public services (GitHub Actions).

    python sim/colab/vt_inputs.py --box 107000,1096000,127000,1116000 --data $RUNNER_TEMP/vtdata --out docs/proto/vermont_jul2023/inputs
    python sim/colab/vt_inputs.py --selftest          (offline: OSM -> road segments, segment encoding, closure-line matching)

Grid frame: EPSG:26986 (Massachusetts State Plane, Lambert conformal conic), the frame every script in this repo assumes.  It is a
conformal projection valid outside Massachusetts; at Montpelier/Barre the scale factor is 1.0006 and grid north is rotated 0.73 deg from
true north (pyproj get_factors), i.e. a 20 m cell is 20.012 m on the ground.  That is far below the DEM's error, so the Vermont box keeps
the repo's frame and none of the CRS code in w9 / impacts / prototype changes.  (EPSG:32145 Vermont State Plane would give ~1e-4.)

--data gets a local mirror of the Hugging Face 'data/' layout that w9 reads (w9 env LF_DATA_DIR=<data>):
  data/dem10/index.json, data/dem10/<x>_<y>.npy  USGS 3DEP 1/3 arc-second+ (best available, 1 m lidar in Vermont) from the 3DEP
                                                ImageServer exportImage, bilinear to 10 m in EPSG:26986, 20 km tiles (same request as w1_data.py)
  data/nlcd10/<x>_<y>.png                      NLCD 2021 impervious %, MRLC WCS 1.0.0 in EPSG:26986 at 10 m (same request as nlcd.yml)
  data/soils30/soils30.npz + meta              SSURGO hydrologic group etc. via Soil Data Access: sim/soils_sda.py unchanged, run with BOX and
                                                without HF_TOKEN (never uploads)
  data/channels30/channels30.npz + meta        NHDPlus HR network flowlines (hydro.nationalmap.gov) rasterised exactly as sim/channels_grid.py
                                                (Bieger et al. 2015 bankfull width / depth from TotDASqKm, the full upstream area)
--out (small, committed): segments_vt.json  OpenStreetMap roads (Overpass; motorway .. residential + links) in the docs/graph_segments.json
                                            layout: split at junctions and every ~1 km, cls 2 motorway/trunk, 1 primary/secondary, 0 the rest;
                                            AADT is not in OSM: class defaults 20000 / 5000 / 500 (documented, used only for vehicle-hours)
                          crossings_vt.json USGS national road-stream crossings (Wieferich 2022) + NAACC culvert surveys in the box, in the
                                            docs/network/crossings_all.json layout (w9 LF_CROSSINGS notches; prototype culvert rule)
                          bridges_vt.json   bridges for the prototype's bridge-deck filter (PROTO_NBI): OSM bridge=* road ways sampled every
                                            20 m + USGS crossings typed bridge (NBI); same {columns: lon, lat, culvert} layout as nbi_ma.json
                          facilities_vt.json hospitals (OSM) in the docs/network/facilities.json layout
                          manifest.json     counts, sources, defaults
docs/proto/obs/gauges_<storm>.json: USGS gauges in the box (Water Data OGC API 'continuous', legacy WaterServices as fallback), the
                                    obs_fetch.py layout (UTC times), read by w9 (flows at gauges) and proto/score.py (rise, timing).
"""
import os, sys, io, json, math, time, argparse, subprocess, shutil
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.normpath(os.path.join(HERE, '..', '..'))
UA = {'User-Agent': 'mass-flood-watch research (github.com/Horus331/mass-flood-watch)'}
T = 20000                     # DEM / NLCD tile size (m), as data/dem10 on Hugging Face
OSM_CLASSES = {'motorway': 2, 'trunk': 2, 'motorway_link': 2, 'trunk_link': 2, 'primary': 1, 'secondary': 1, 'primary_link': 1, 'secondary_link': 1,
               'tertiary': 0, 'tertiary_link': 0, 'unclassified': 0, 'residential': 0}
AADT_DEFAULT = {2: 20000, 1: 5000, 0: 500}
SEG_MAX_M = 1000.0            # MA graph segments are split at junctions and at ~1 km (median highway segment 999 m)
OVERPASS = ('https://overpass-api.de/api/interpreter', 'https://lz4.overpass-api.de/api/interpreter', 'https://overpass.kumi.systems/api/interpreter',
            'https://overpass.private.coffee/api/interpreter')
log = lambda *a: print(time.strftime('%H:%M:%S'), *a, flush=True)


def get(url, params=None, tries=5, timeout=300, post=None):
    import requests
    for k in range(tries):
        try:
            r = requests.post(url, data=post, headers=UA, timeout=timeout) if post is not None else requests.get(url, params=params, headers=UA, timeout=timeout)
            if r.status_code == 200: return r
            log('  http', r.status_code, url[:90], r.text[:120])
        except Exception as e: log('  err', url[:90], repr(e)[:120])
        time.sleep(5 + 10 * k)
    return None


def lonlat_bbox(box, pad=0.0):
    from pyproj import Transformer
    inv = Transformer.from_crs(26986, 4326, always_xy=True); x0, y0, x1, y1 = box
    xs = [x0 - pad, x1 + pad, x0 - pad, x1 + pad, (x0 + x1) / 2, (x0 + x1) / 2]; ys = [y0 - pad, y0 - pad, y1 + pad, y1 + pad, y0 - pad, y1 + pad]
    lo, la = inv.transform(xs, ys); return min(lo), min(la), max(lo), max(la)


# ---------------------------------------------------------------- DEM + NLCD tiles (HF data/dem10, data/nlcd10 layout) ----------------
def tiles_for(box):
    x0, y0, x1, y1 = box
    return [(int(x), int(y)) for x in np.arange(x0, x1, T) for y in np.arange(y0, y1, T)]


def fetch_dem(box, data):
    import tifffile
    os.makedirs(f'{data}/dem10', exist_ok=True); index = {}
    for x, y in tiles_for(box):
        key = f'{x}_{y}'
        u = ('https://elevation.nationalmap.gov/arcgis/rest/services/3DEPElevation/ImageServer/exportImage'
             f'?bbox={x},{y},{x + T},{y + T}&bboxSR=26986&imageSR=26986&size=2000,2000&format=tiff&pixelType=F32'
             '&noDataInterpretation=esriNoDataMatchAny&interpolation=RSP_BilinearInterpolation&f=image')
        a = None
        for k in range(5):
            r = get(u, tries=2)
            if r is not None and r.content[:2] in (b'II', b'MM'):
                a = tifffile.imread(io.BytesIO(r.content)).astype(np.float32); a = a[..., 0] if a.ndim == 3 else a; break
            log('  DEM retry', k, None if r is None else r.content[:100]); time.sleep(20)
        if a is None: raise SystemExit(f'3DEP DEM failed for tile {key}')
        a[(a < -100) | (a > 2000)] = np.nan; valid = float(np.isfinite(a).mean())
        np.save(f'{data}/dem10/{key}.npy', a)
        index[key] = dict(x=x, y=y, valid=round(valid, 3), zmin=float(np.nanmin(a)) if valid else None, zmax=float(np.nanmax(a)) if valid else None)
        log(f'DEM tile {key}: {a.shape}, valid {valid:.3f}, z {index[key]["zmin"]}..{index[key]["zmax"]}')
    json.dump(index, open(f'{data}/dem10/index.json', 'w')); return index


def fetch_nlcd(box, data):
    import tifffile
    from PIL import Image
    os.makedirs(f'{data}/nlcd10', exist_ok=True); got = 0
    for x, y in tiles_for(box):
        u = ('https://www.mrlc.gov/geoserver/mrlc_download/wcs?service=WCS&version=1.0.0&request=GetCoverage&coverage=mrlc_download:NLCD_2021_Impervious_L48'
             f'&CRS=EPSG:26986&BBOX={x},{y},{x + T},{y + T}&WIDTH=2000&HEIGHT=2000&FORMAT=GeoTIFF')
        r = get(u, timeout=240)
        if r is None or r.content[:2] not in (b'II', b'MM'): log('NLCD tile failed', x, y, None if r is None else r.content[:100]); continue
        a = tifffile.imread(io.BytesIO(r.content)); a = (a[..., 0] if a.ndim == 3 else a).astype(np.float32); a[a > 100] = 0
        Image.fromarray(a.astype(np.uint8), 'L').save(f'{data}/nlcd10/{x}_{y}.png'); got += 1
        log(f'NLCD tile {x}_{y}: mean {a.mean():.1f}% paved')
    return got


# ---------------------------------------------------------------- soils (sim/soils_sda.py, unchanged) ---------------------------------
def pad_box(box, res, pad):
    x0, y0, x1, y1 = box; return (int(x0 - pad), int(y0 - pad), int(x0 - pad + math.ceil((x1 - x0 + 2 * pad) / res) * res), int(y0 - pad + math.ceil((y1 - y0 + 2 * pad) / res) * res))


def fetch_soils(box, data):
    wb = pad_box(box, 30, 990); wd = f'{data}/_soils_work'; os.makedirs(wd, exist_ok=True)
    env = {k: v for k, v in os.environ.items() if k not in ('HF_TOKEN', 'HUGGING_FACE_HUB_TOKEN')}; env['BOX'] = ','.join(map(str, wb))
    p = subprocess.run([sys.executable, os.path.join(ROOT, 'sim', 'soils_sda.py')], cwd=wd, env=env, capture_output=True, text=True, timeout=5400)
    log('soils_sda.py:', (p.stdout or '')[-1500:], (p.stderr or '')[-800:])
    if p.returncode != 0 or not os.path.exists(f'{wd}/out/soils30.npz'): raise SystemExit('SSURGO soils failed')
    os.makedirs(f'{data}/soils30', exist_ok=True)
    for f in ('soils30.npz', 'soils30_meta.json'): shutil.copy(f'{wd}/out/{f}', f'{data}/soils30/{f}')
    m = json.load(open(f'{data}/soils30/soils30_meta.json')); return dict(box=wb, coverage=m.get('coverage'), polygons=m.get('polygons'))


# ---------------------------------------------------------------- channels (sim/channels_grid.py rules) -------------------------------
def bankfull_w(A):
    if A <= 0: return 1.0
    return 2.70 * A ** 0.352 * ((A / 500.0) ** 0.15 if A > 500 else 1.0)


def fetch_channels(box, data):
    from shapely.geometry import shape
    from shapely.ops import transform as shp_transform
    from rasterio import features
    from rasterio.transform import from_origin
    from pyproj import Transformer
    RES = 30; wb = pad_box(box, RES, 990); x0, y0, x1, y1 = wb; nx, ny = (x1 - x0) // RES, (y1 - y0) // RES; tr = from_origin(x0, y1, RES, RES)
    svc = 'https://hydro.nationalmap.gov/arcgis/rest/services/NHDPlus_HR/MapServer'
    L = get(svc, dict(f='json')).json()['layers']
    net = [l for l in L if 'flowline' in l['name'].lower() and 'network' in l['name'].lower()]
    lid = (net or [l for l in L if 'flowline' in l['name'].lower()])[0]['id']; log('NHDPlus HR flowline layer', lid)
    w, s, e, n = lonlat_bbox(wb); feats = []; off = 0
    while True:
        r = get(f'{svc}/{lid}/query', dict(geometry=f'{w},{s},{e},{n}', geometryType='esriGeometryEnvelope', inSR=4326, spatialRel='esriSpatialRelIntersects',
                                           outFields='*', returnGeometry='true', outSR=4326, f='geojson', resultOffset=off, resultRecordCount=2000))
        if r is None: raise SystemExit('NHDPlus HR query failed')
        q = r.json(); fs = q.get('features', []); feats += fs; off += len(fs)
        if len(fs) < 2000 and not q.get('properties', {}).get('exceededTransferLimit'): break
    if not feats: raise SystemExit('no NHDPlus HR flowlines in the box')
    keys = {k.lower(): k for k in feats[0]['properties']}; ka = keys.get('totdasqkm'); kf = keys.get('ftype'); log('flowlines', len(feats), 'area field', ka, 'ftype', kf)
    to_m = Transformer.from_crs(4326, 26986, always_xy=True).transform
    chan_s, water_s, area_s = [], [], []; nlake = 0; LX = []
    for f in feats:
        try: g = shp_transform(to_m, shape(f['geometry']))
        except Exception: continue
        pr = f['properties']; A = float(pr.get(ka) or 0) if ka else 0.0; ft = int(pr.get(kf) or 0) if kf else 0
        for part in (getattr(g, 'geoms', None) or [g]): LX.append(dict(a=round(A, 2), n=pr.get('GNIS_Name') or pr.get('gnis_name') or '', xy=[[round(x, 1), round(y, 1)] for x, y in part.coords]))
        chan_s.append((g, 1)); area_s.append((g, A)); W = bankfull_w(A); nlake += ft == 558
        if W > RES or ft == 558: water_s.append((g.buffer(max(W, RES) / 2 if ft != 558 else 60.0), 1))
    chan = features.rasterize(chan_s, out_shape=(ny, nx), transform=tr, default_value=1, all_touched=True, dtype='uint8').astype(bool)
    area = features.rasterize(sorted([t for t in area_s if t[1] > 0], key=lambda t: t[1]), out_shape=(ny, nx), transform=tr, all_touched=True, dtype='float32')
    water = (features.rasterize(water_s, out_shape=(ny, nx), transform=tr, default_value=1, all_touched=True, dtype='uint8').astype(bool) if water_s
             else np.zeros((ny, nx), bool)) | chan & (area > 50)
    A_ = np.maximum(area, 0.01); width = np.where(chan, 2.70 * A_ ** 0.352 * np.where(A_ > 500, (A_ / 500.0) ** 0.15, 1.0), 0).astype(np.float16)
    depth = np.where(chan, 0.30 * A_ ** 0.213, 0).astype(np.float16)
    os.makedirs(f'{data}/channels30', exist_ok=True); json.dump(LX, open(f'{data}/_flowlines_xy.json', 'w'))
    np.savez_compressed(f'{data}/channels30/channels30.npz', chan=chan, water=water, area=area, width=width, depth=depth)
    json.dump(dict(box=list(wb), res_m=RES, crs='EPSG:26986', shape=[int(ny), int(nx)], flowlines=len(feats), lake_paths=int(nlake), chan_cells=int(chan.sum()),
                   water_cells=int(water.sum()), source='NHDPlus HR flowlines via hydro.nationalmap.gov; bankfull geometry Bieger et al. 2015', made=time.strftime('%Y-%m-%d')),
              open(f'{data}/channels30/channels30_meta.json', 'w'))
    log(f'channels: {chan.sum():,} cells, water {water.sum():,}, max area {area.max():.0f} km2')
    return dict(flowlines=len(feats), chan_cells=int(chan.sum()), max_area_km2=round(float(area.max()), 1))


# ---------------------------------------------------------------- one-way nesting: river inflow at the box edge -------------------------
# A 20 km box cuts the big rivers (Winooski at Montpelier drains 1028 km2, Dog River at Northfield Falls 197 km2, mostly outside the box), so
# with rain on the box only they carry a fraction of their flow.  The flow entering the box comes from a coarse run of the SAME model and
# settings over a 60 x 60 km box holding those basins (rain on grid, MRMS + CN), read at every place a mapped stream enters the fine box.
# No gauge observation enters the fine run, so the gauges stay an independent check.
def entry_points(box, data, path, min_km2=2.0, dedupe_m=150.0):
    """Where NHDPlus HR flowlines (digitised downstream) cross the box edge from outside to inside, with upstream area >= min_km2.
    Writes [{site 'INnn', name, x, y, lon, lat, edge, area_km2}] (obs-gauge layout, so w9's gauge flux machinery samples them)."""
    from pyproj import Transformer
    inv = Transformer.from_crs(26986, 4326, always_xy=True); x0, y0, x1, y1 = box
    LX = json.load(open(f'{data}/_flowlines_xy.json')); E = []
    ins = lambda p: x0 < p[0] < x1 and y0 < p[1] < y1
    for L in LX:
        if L['a'] < min_km2: continue
        P = L['xy']
        for a, b in zip(P[:-1], P[1:]):
            if ins(a) or not ins(b): continue                     # outside -> inside only (downstream digitising)
            best = None
            for edge, v, ax in (('W', x0, 0), ('E', x1, 0), ('S', y0, 1), ('N', y1, 1)):
                if (a[ax] - v) * (b[ax] - v) > 0 or a[ax] == b[ax]: continue
                t = (v - a[ax]) / (b[ax] - a[ax]); q = (a[0] + t * (b[0] - a[0]), a[1] + t * (b[1] - a[1]))
                if x0 - 1 <= q[0] <= x1 + 1 and y0 - 1 <= q[1] <= y1 + 1 and (best is None or t > best[0]): best = (t, q, edge)
            if best: E.append(dict(x=best[1][0], y=best[1][1], edge=best[2], area_km2=L['a'], name=L['n']))
    E.sort(key=lambda e: -e['area_km2']); keep = []
    for e in E:
        if all(math.hypot(e['x'] - k['x'], e['y'] - k['y']) > dedupe_m for k in keep): keep.append(e)
    for i, e in enumerate(keep):
        e['site'] = f'IN{i + 1:02d}'; lo, la = inv.transform(e['x'], e['y']); e.update(lon=round(lo, 6), lat=round(la, 6), x=round(e['x'], 1), y=round(e['y'], 1))
        e['name'] = f"inflow {e['site']}: {e['name'] or 'stream'} ({e['area_km2']:.0f} km2, {e['edge']} edge)"
    json.dump(keep, open(path, 'w'), indent=0); log(f'{len(keep)} stream entries >= {min_km2} km2:', [(e['site'], e['name']) for e in keep[:12]])
    return dict(entries=len(keep), area_km2=[e['area_km2'] for e in keep[:10]])


def add_points(gauges_path, points_path):
    """Append the entry points to an obs gauges file (as gauges without observations) so the coarse w9 run reports flow through them."""
    G = json.load(open(gauges_path)) if os.path.exists(gauges_path) else dict(gauges=[])
    P = json.load(open(points_path)); G['gauges'] = [g for g in G['gauges'] if not str(g['site']).startswith('IN')] + [dict(site=p['site'], name=p['name'], lon=p['lon'], lat=p['lat']) for p in P]
    json.dump(G, open(gauges_path, 'w'), separators=(',', ':')); return len(P)


def make_inflows(xings_path, meta_path, points_path, out_path):
    """Coarse-run flow out of the 5 x 5-cell block at each entry (w9 LF_QOUT, every saveint) -> {points: [{name, x, y, edge, t_s, q_m3s}]}."""
    X = json.load(open(xings_path)); M = json.load(open(meta_path)); P = {p['site']: p for p in json.load(open(points_path))}
    si = float(((M.get('inputs') or {}).get('env') or {}).get('LF_SAVEINT', 1800)); out = []
    for g in X.get('gauges', []):
        p = P.get(g['site'])
        if p is None or not g.get('q_series'): continue
        q = [max(0.0, float(v)) for v in g['q_series']]
        out.append(dict(name=p['site'], x=p['x'], y=p['y'], edge=p['edge'], area_km2=p['area_km2'], peak_m3s=round(max(q), 2), t_s=[k * si for k in range(len(q))], q_m3s=q))
    json.dump(dict(points=out, source=f'coarse run {M.get("run")} box {M.get("box")} res {M.get("res_m")} m (same settings as the fine run)'), open(out_path, 'w'))
    log('inflows:', [(o['name'], o['area_km2'], o['peak_m3s']) for o in out]); return len(out)


def point_sources(J, Z, chan, box, res, inset=3, search=4):
    """LISFLOOD-FP point sources for w9 (LF_INFLOW=file): each entry goes `inset` cells inside its edge, on the lowest cell (channel first)
    within `search` cells along the edge.  Point-source QVAR values are flow per unit width (UpdateH adds value * dx * dt / dA), so the
    .bdy holds Q / res.  Returns (bci lines, bdy text, [(name, row, col)])."""
    x0, y0, x1, y1 = box; ny, nx = Z.shape; bl, cells = [], []; T = ['# w9 LF_INFLOW=file: river inflows from a coarse run (m2/s = Q / RES)']
    for p in J['points']:
        r = int((y1 - p['y']) // res); c = int((p['x'] - x0) // res); e = p['edge']
        if e == 'W': c = inset
        elif e == 'E': c = nx - 1 - inset
        elif e == 'N': r = inset
        else: r = ny - 1 - inset
        r = min(max(r, 1), ny - 2); c = min(max(c, 1), nx - 2)
        if e in 'WE': ra, rb, ca, cb = max(1, r - search), min(ny - 1, r + search + 1), c, c + 1
        else: ra, rb, ca, cb = r, r + 1, max(1, c - search), min(nx - 1, c + search + 1)
        w = Z[ra:rb, ca:cb].astype(float) - 100.0 * (chan[ra:rb, ca:cb] if chan is not None else 0); i = np.unravel_index(int(np.argmin(w)), w.shape)
        rr, cc = ra + i[0], ca + i[1]; cells.append((p['name'], int(rr), int(cc)))
        bl.append(f"P {x0 + (cc + 0.5) * res:.1f} {y1 - (rr + 0.5) * res:.1f} QVAR {p['name']}")
        T += [p['name'], f"{len(p['t_s'])} seconds"] + [f'{q / res:.5f} {t:.0f}' for q, t in zip(p['q_m3s'], p['t_s'])]
    return bl, '\n'.join(T) + '\n', cells


# ---------------------------------------------------------------- road-stream crossings (USGS + NAACC, crossings_all.py helpers) -------
def fetch_crossings(box, out):
    sys.path.insert(0, os.path.join(ROOT, 'sim', 'infra')); import crossings_all as CA
    bb = lonlat_bbox(box, 500); counts = {}
    U = CA.query_all(CA.SRC_U + '/0', fields='stream_crossing_id,nhdhr_gnis_stream_name,tiger2020_feature_names,tiger2020_mtfcc_feature_class,crossing_type', bbox=bb, geometry=True)
    try: O = CA.query_all(CA.SRC_U + '/1', fields='stream_crossing_id,structure_id,crossing_type,crossing_subtype', bbox=bb)
    except Exception as e: log('USGS crossing observations unavailable:', repr(e)[:120]); O = []
    obs = {}
    for f in O: obs.setdefault(f['attributes'].get('stream_crossing_id'), f['attributes'])
    rows = []
    for f in U:
        a = f['attributes']; p = CA.xy(f, a)
        if p is None: continue
        o = obs.get(a.get('stream_crossing_id'), {}); xt = (o.get('crossing_subtype') or o.get('crossing_type') or a.get('crossing_type') or '').lower() or None
        r = dict.fromkeys(CA.COLUMNS); r.update(lon=round(p[0], 6), lat=round(p[1], 6), id=f"u{a.get('stream_crossing_id')}", src='U', road=a.get('tiger2020_feature_names'),
                                              stream=a.get('nhdhr_gnis_stream_name'), mtfcc=a.get('tiger2020_mtfcc_feature_class'), xtype=xt, nbi_id=o.get('structure_id'), d3=0)
        if xt and 'bridge' in xt: r['shape'] = 'bridge'
        rows.append(r)
    counts['U'] = len(rows)
    try:
        from pyproj import Transformer
        from scipy.spatial import cKDTree
        tr = Transformer.from_crs(4326, 26986, always_xy=True)
        info = CA.layer_info(CA.SRC_N); N = CA.query_layer(CA.SRC_N, info, bbox=bb, geometry=True)
        fm = CA.pick_fields(info.get('fields', []), [f['attributes'] for f in N[:3000]]); log('NAACC records', len(N), 'field map', fm)
        X, Y = tr.transform([r['lon'] for r in rows], [r['lat'] for r in rows]) if rows else ([], [])
        tree = cKDTree(np.column_stack([X, Y])) if rows else None; used = set(); hit = new = 0
        for f in N:
            a = f['attributes']; p = CA.xy(f, a, fm['lat'], fm['lon'])
            if p is None: continue
            g = lambda k: a.get(fm[k]) if fm.get(k) else None
            r = None
            if tree is not None:
                d, i = tree.query(tr.transform(*p))
                if d <= 50 and i not in used: r = rows[i]; used.add(i); hit += 1; r['src'] = 'UN'
            if r is None:
                r = dict.fromkeys(CA.COLUMNS); r.update(lon=round(p[0], 6), lat=round(p[1], 6), id=f'n{len(rows)}', src='N', d3=0); rows.append(r); new += 1
            shp = CA.norm_shape(g('shape')); r['naacc'] = g('code') or r['naacc']; r['shape'] = shp or r['shape']; r['material'] = CA.norm_material(g('material'))
            r['inlet'] = CA.norm_inlet(g('inlet')); r['n_barrels'] = int(CA.num(g('n_barrels')) or 1) if g('n_barrels') not in (None, '') else r['n_barrels']
            wv, hv = CA.num(g('width'), CA.FT), CA.num(g('height'), CA.FT)
            if shp == 'circular' and (wv or hv): r['span_m'] = r['rise_m'] = max(wv or 0, hv or 0)
            else: r['span_m'], r['rise_m'] = wv, hv
            r['fill_m'] = CA.num(g('fill'), CA.FT); r['naacc_eval'] = g('evaluation'); r['road'] = r['road'] or g('road'); r['stream'] = r['stream'] or g('stream')
        counts.update(naacc=len(N), naacc_matched=hit, naacc_added=new)
    except Exception as e: log('NAACC unavailable:', repr(e)[:200]); counts['naacc_error'] = repr(e)[:200]
    try: counts.update(attach_vtrans(rows, bb, CA))
    except Exception as e: log('VTrans small culverts unavailable:', repr(e)[:200]); counts['vtrans_error'] = repr(e)[:200]
    counts['with_culvert_size'] = sum(1 for r in rows if r['rise_m']); counts['bridges'] = sum(1 for r in rows if r['shape'] == 'bridge')
    cols = CA.COLUMNS + ['length_m']
    J = dict(columns=cols, rows=[[r.get(c) for c in cols] for r in rows], counts=counts, made=time.strftime('%Y-%m-%d'),
             sources=dict(U=CA.SRC_U, N=CA.SRC_N, V=VTRANS_SCI), note='Vermont test box: USGS national stream crossings + NAACC surveys + VTrans Small Culvert '
                                                                     'Inventory sizes attached to them within 50 m (src UV); no MA-only sources')
    json.dump(J, open(f'{out}/crossings_vt.json', 'w'), separators=(',', ':')); log('crossings', counts); return counts, rows


VTRANS_SCI = 'https://maps.vtrans.vermont.gov/arcgis/rest/services/HWY/AMP_SmallCulvertInventory/FeatureServer/0'


def attach_vtrans(rows, bb, CA, radius=50.0):
    """VTrans Small Culvert Inventory (state highways; polylines inlet -> outlet): barrel size, shape, material, inlet treatment, fill and length
    attached to the nearest USGS road-stream crossing within `radius` of the culvert's midpoint, like NAACC surveys in MA.  Unmatched culverts
    (ditch relief / cross drains off the mapped streams) are not added, so the w9 notches stay the USGS stream crossings.
    Units: SIZE / HEIGHT / WIDTH in inches and FILL_DEPTH in feet unless the medians say otherwise (logged); the value lists are logged too."""
    from pyproj import Transformer
    from scipy.spatial import cKDTree
    F = CA.query_all(VTRANS_SCI, fields='*', bbox=bb, geometry=True, page=1000)
    A = [f['attributes'] for f in F]; log('VTrans small culverts in bbox:', len(F))
    if not F: return dict(vtrans=0)
    from collections import Counter
    for k in ('STRUC_TYPE', 'MATERIAL', 'IN_TREATMENT', 'DRAIN_TYPE', 'SYS_TYPE'):
        log(f'  {k}:', Counter(str(a.get(k)) for a in A).most_common(15))
    med = lambda k: float(np.nanmedian([float(a[k]) for a in A if a.get(k) not in (None, 0)] or [np.nan]))
    m_size, m_fill = med('SIZE'), med('FILL_DEPTH'); log(f'  median SIZE {m_size}, HEIGHT {med("HEIGHT")}, WIDTH {med("WIDTH")}, FILL_DEPTH {m_fill}, LENGTH_FT {med("LENGTH_FT")}')
    k_size = 0.0254 if not (m_size < 10) else CA.FT; k_fill = CA.FT if not (m_fill > 15) else 0.0254
    def shape_of(s, a):
        s = (s or '').upper()
        if 'RND' in s or 'ROUND' in s or 'CIR' in s or s in ('', 'NONE'): return 'circular' if a.get('SIZE') else None
        if 'BOX' in s: return 'box'
        if 'ELL' in s or 'ELIP' in s or 'OVAL' in s: return 'elliptical'
        if 'ARCH' in s or s.startswith('PA'): return 'pipe_arch'
        return CA.norm_shape(s) if CA.norm_shape(s) not in (None, 'other') else ('box' if a.get('WIDTH') and a.get('HEIGHT') else 'circular')
    def mat_of(s):
        s = (s or '').upper()
        if s.startswith(('CONC', 'RCP', 'RC')): return 'concrete'
        if s.startswith(('CMP', 'STEEL', 'ALUM', 'CI', 'DI', 'MET', 'GAL', 'CS')): return 'metal'
        if s.startswith(('PLAS', 'HDPE', 'PVC', 'PE', 'POLY', 'SDR')): return 'plastic'
        if s.startswith(('STONE', 'ROCK', 'MAS', 'GRAN')): return 'stone'
        return CA.norm_material(s)
    def inlet_of(s):
        s = (s or '').upper()
        if not s or s in ('NONE', 'NO', 'PROJ'): return 'projecting'
        if 'MIT' in s or 'FES' in s or 'FLAR' in s or 'END' in s: return 'mitered'
        if 'WING' in s: return 'headwall_wingwall' if 'HEAD' in s or 'HW' in s else 'wingwall'
        if 'HEAD' in s or 'HW' in s or 'HDW' in s: return 'headwall'
        return CA.norm_inlet(s)
    tr = Transformer.from_crs(4326, 26986, always_xy=True)
    cand = [i for i, r in enumerate(rows) if r['src'] == 'U' and r['shape'] != 'bridge']
    if not cand: return dict(vtrans=len(F), vtrans_matched=0)
    X, Y = tr.transform([rows[i]['lon'] for i in cand], [rows[i]['lat'] for i in cand]); tree = cKDTree(np.column_stack([X, Y])); best = {}
    for f, a in zip(F, A):
        if a.get('RETIRE_DATE') or str(a.get('DELETE_RECORD') or '').upper() in ('Y', 'YES', 'TRUE'): continue
        P = [p for path in (f.get('geometry') or {}).get('paths', []) for p in path]
        if not P: continue
        mx, my = tr.transform(*np.mean(np.asarray(P, float)[:, :2], axis=0)); d, j = tree.query([mx, my])
        if d <= radius and (cand[j] not in best or d < best[cand[j]][0]): best[cand[j]] = (d, a)
    for i, (d, a) in best.items():
        r = rows[i]; shp = shape_of(a.get('STRUC_TYPE'), a); sz = a.get('SIZE'); w_, h_ = a.get('WIDTH'), a.get('HEIGHT')
        if shp == 'circular' and sz: r['span_m'] = r['rise_m'] = round(float(sz) * k_size, 3)
        elif w_ and h_: r['span_m'], r['rise_m'] = round(float(w_) * k_size, 3), round(float(h_) * k_size, 3)
        elif sz: r['span_m'] = r['rise_m'] = round(float(sz) * k_size, 3)
        else: continue
        r['shape'] = shp or 'circular'; r['material'] = mat_of(a.get('MATERIAL')); r['inlet'] = inlet_of(a.get('IN_TREATMENT')); r['n_barrels'] = 1
        r['fill_m'] = round(float(a['FILL_DEPTH']) * k_fill, 2) if a.get('FILL_DEPTH') not in (None,) else None
        if a.get('LENGTH_FT'): r['length_m'] = round(float(a['LENGTH_FT']) * CA.FT, 1)
        r['src'] = 'UV'; r['naacc_eval'] = a.get('FUNCTIONAL_RATING'); r['road'] = r['road'] or a.get('ROUTE')
    return dict(vtrans=len(F), vtrans_matched=len(best), vtrans_units=dict(size_m_per_unit=k_size, fill_m_per_unit=k_fill, median_size=m_size, median_fill=m_fill))


# ---------------------------------------------------------------- OpenStreetMap roads -> graph_segments layout -------------------------
def overpass(q):
    for attempt in range(3):
        for url in OVERPASS:
            r = get(url, post={'data': q}, tries=1, timeout=400)
            if r is not None:
                try: return r.json()['elements']
                except Exception as e: log('overpass bad json', url, repr(e)[:80])
        time.sleep(60)
    raise SystemExit('all Overpass mirrors refused')


def encode(lon, lat):
    """[lon0*1e5, lat0*1e5, dlon, dlat, ...] integers (the docs/graph_segments.json 'geo' part encoding: cumsum / 1e5 decodes)."""
    a = np.round(np.asarray(lon) * 1e5).astype(np.int64); b = np.round(np.asarray(lat) * 1e5).astype(np.int64)
    da = np.r_[a[0], np.diff(a)]; db = np.r_[b[0], np.diff(b)]; out = np.empty(2 * len(a), np.int64); out[0::2] = da; out[1::2] = db
    return [int(v) for v in out]


def build_segments(els, places=()):
    """OSM elements (ways with tags + nodes) -> (graph_segments dict, bridge points [(lon, lat)]).  Ways are cut at every node shared by two
    or more road ways (junctions) and wherever a piece passes SEG_MAX_M; segments sharing an end node are linked."""
    from pyproj import Transformer
    tr = Transformer.from_crs(4326, 26986, always_xy=True)
    nodes = {e['id']: (e['lon'], e['lat']) for e in els if e['type'] == 'node'}
    ways = [e for e in els if e['type'] == 'way' and (e.get('tags') or {}).get('highway') in OSM_CLASSES and all(n in nodes for n in e['nodes'])]
    use = {}
    for w in ways:
        for k, nid in enumerate(w['nodes']): use[nid] = use.get(nid, 0) + (2 if k in (0, len(w['nodes']) - 1) else 1)
    PX = [(nm, tr.transform(lo, la)) for nm, lo, la in places]
    geo, props, ends, bridges = [], dict(road=[], town=[], cls=[], low=[], len=[], aadt=[]), [], []
    def town(x, y):
        if not PX: return ''
        return min(PX, key=lambda p: (p[1][0] - x) ** 2 + (p[1][1] - y) ** 2)[0]
    for w in ways:
        t = w['tags']; cls = OSM_CLASSES[t['highway']]; ref = (t.get('ref') or '').replace(';', ' / '); nm = t.get('name') or ''
        road = nm + (f' ({ref})' if ref and nm else ref)
        ll = np.array([nodes[n] for n in w['nodes']]); X, Y = tr.transform(ll[:, 0], ll[:, 1]); step = np.r_[0, np.hypot(np.diff(X), np.diff(Y))]
        if t.get('bridge') not in (None, 'no'):
            for k in range(1, len(ll)):
                m = max(1, int(math.ceil(step[k] / 20.0)))
                for j in range(m + 1): bridges.append((ll[k - 1, 0] + (ll[k, 0] - ll[k - 1, 0]) * j / m, ll[k - 1, 1] + (ll[k, 1] - ll[k - 1, 1]) * j / m))
        s = 0; acc = 0.0
        for k in range(1, len(ll)):
            acc += step[k]
            if k == len(ll) - 1 or use.get(w['nodes'][k], 0) >= 2 or acc >= SEG_MAX_M - 0.5:
                geo.append([encode(ll[s:k + 1, 0], ll[s:k + 1, 1])]); ends.append((w['nodes'][s], w['nodes'][k]))
                j = (s + k) // 2
                props['road'].append(road); props['town'].append(town(X[j], Y[j])); props['cls'].append(cls); props['low'].append(0)
                props['len'].append(int(round(acc))); props['aadt'].append(AADT_DEFAULT[cls]); s = k; acc = 0.0
    by_node = {}
    for i, (a, b) in enumerate(ends):
        by_node.setdefault(a, set()).add(i); by_node.setdefault(b, set()).add(i)
    links = sorted({(min(i, j), max(i, j)) for S_ in by_node.values() for i in S_ for j in S_ if i != j})
    return dict(n=len(geo), geo=geo, props=props, links=[list(l) for l in links],
                source='OpenStreetMap via Overpass (ODbL); split at junctions and ~1 km; aadt = class default (not in OSM)'), bridges


def fetch_roads(box, out):
    w, s, e, n = lonlat_bbox(box, 1500)
    hw = '|'.join(OSM_CLASSES)
    els = overpass(f'[out:json][timeout:300];(way["highway"~"^({hw})$"]({s},{w},{n},{e}););(._;>;);out body;')
    pls = overpass(f'[out:json][timeout:120];(node["place"~"^(city|town|village|hamlet|suburb)$"]({s - 0.05},{w - 0.05},{n + 0.05},{e + 0.05}););out body;')
    places = [((p.get('tags') or {}).get('name', ''), p['lon'], p['lat']) for p in pls if (p.get('tags') or {}).get('name')]
    S, bridges = build_segments(els, places)
    json.dump(S, open(f'{out}/segments_vt.json', 'w'), separators=(',', ':'))
    hosp = overpass(f'[out:json][timeout:120];(nwr["amenity"="hospital"]({s - 0.3},{w - 0.3},{n + 0.3},{e + 0.3}););out center tags;')
    H_ = []
    for h in hosp:
        t = h.get('tags', {})
        if t.get('emergency') == 'no': continue
        lon = h.get('lon') or h.get('center', {}).get('lon'); lat = h.get('lat') or h.get('center', {}).get('lat')
        if lon is not None: H_.append([round(lon, 5), round(lat, 5), (t.get('name') or '')[:60]])
    json.dump(dict(source='OpenStreetMap via Overpass, ' + time.strftime('%Y-%m-%d'), counts=dict(hospital=len(H_)), facilities=dict(hospital=H_, fire_station=[], police=[], ambulance_station=[])),
              open(f'{out}/facilities_vt.json', 'w'), separators=(',', ':'))
    cls = np.asarray(S['props']['cls'])
    log(f'roads: {S["n"]} segments (highway {int((cls == 2).sum())}, arterial {int((cls == 1).sum())}, local {int((cls == 0).sum())}), {len(S["links"])} links, '
        f'{len(bridges)} bridge points, {len(H_)} hospitals, {len(places)} places')
    return S, bridges, dict(segments=S['n'], by_class={k: int((cls == k).sum()) for k in (0, 1, 2)}, links=len(S['links']), bridge_points=len(bridges), hospitals=len(H_))


# ---------------------------------------------------------------- USGS gauges ----------------------------------------------------------
def fetch_gauges(box, start, end, path, state='50'):
    """Gauges inside the box with 15-min discharge (00060) / gage height (00065), obs_fetch.py layout with UTC ISO times."""
    # Through proto/usgs_api.py (OGC API bbox query; legacy WaterServices bBox as the fallback until 22 Feb 2027, env USGS_SOURCE).
    # `state` is no longer needed (the box selects the gauges) and is kept for the call signature.
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'proto')); import usgs_api as U
    w, s, e, n = lonlat_bbox(box)
    G, used = U.iv(bbox=(w, s, e, n), start=f'{start}T00:00:00Z', end=f'{end}T23:59:59Z')
    src = 'legacy waterservices.usgs.gov' if used == 'legacy' else 'api.waterdata.usgs.gov OGC continuous'
    out = {}
    for sid, g in sorted(G.items()):
        for pc, k in (('00060', 'q_cfs'), ('00065', 'stage_ft')):
            vals = g['series'].get(pc) or []
            if not vals: continue
            r = out.setdefault(sid, dict(site=sid, name=g['name'], lon=g['lon'], lat=g['lat']))
            r[k] = vals; r['peak_' + k] = max(vals, key=lambda x: x[1])
            r.update(datum_ft=g['datum_ft'], vdatum=g['vdatum'], drain_mi2=g['drain_mi2'])
    os.makedirs(os.path.dirname(path), exist_ok=True)
    json.dump(dict(bbox=[w, s, e, n], start=start, end=end, source=src, times='UTC', gauges=list(out.values())), open(path, 'w'), separators=(',', ':'))
    log('gauges in box:', [(g['site'], g['name'], g.get('peak_q_cfs')) for g in out.values()])
    return [dict(site=g['site'], name=g['name'], peak_q_cfs=g.get('peak_q_cfs'), peak_stage_ft=g.get('peak_stage_ft')) for g in out.values()]


# ---------------------------------------------------------------- main -----------------------------------------------------------------
def main(a):
    box = tuple(float(v) for v in a.box.split(',')); os.makedirs(a.out, exist_ok=True); data = os.path.join(a.data, 'data'); os.makedirs(data, exist_ok=True)
    man = dict(box_epsg26986=list(box), bbox_lonlat=[round(v, 5) for v in lonlat_bbox(box)], made=time.strftime('%Y-%m-%d %H:%M'),
               crs_note='EPSG:26986 (MA State Plane LCC) kept for Vermont: scale factor 1.0006, convergence 0.73 deg at Montpelier', steps={})
    def step(name, fn, *args, required=True):
        t0 = time.time()
        try: r = fn(*args); man['steps'][name] = dict(ok=True, s=round(time.time() - t0), result=r if isinstance(r, (dict, list, int, float, str)) else None)
        except BaseException as e:
            man['steps'][name] = dict(ok=False, s=round(time.time() - t0), error=repr(e)[:300]); log(name, 'FAILED', repr(e)[:300])
            json.dump(man, open(f'{a.out}/manifest.json', 'w'), indent=1)
            if required: raise
        json.dump(man, open(f'{a.out}/manifest.json', 'w'), indent=1)
    step('dem_3dep', fetch_dem, box, data)
    step('nlcd_impervious', fetch_nlcd, box, data, required=False)
    step('channels_nhdplushr', fetch_channels, box, data, required=False)
    step('soils_ssurgo', fetch_soils, box, data, required=False)
    if a.entry_points: step('entry_points', entry_points, box, data, a.entry_points, required=False)
    def roads():
        if a.skip_roads: man['_bridges'] = []; return 'skipped'
        S, bridges, info = fetch_roads(box, a.out); man['bridges_osm'] = len(bridges); man['_bridges'] = bridges; return info
    step('roads_osm', roads)
    bridges = man.pop('_bridges', [])
    def xings():
        c, rows = fetch_crossings(box, a.out)
        bridges.extend((r['lon'], r['lat']) for r in rows if r['shape'] == 'bridge'); return c
    step('crossings_usgs_naacc', xings, required=False)
    json.dump(dict(columns=['lon', 'lat', 'culvert'], rows=[[round(x, 6), round(y, 6), 0] for x, y in bridges], source='OSM bridge=* road ways every 20 m + USGS crossings typed bridge'),
              open(f'{a.out}/bridges_vt.json', 'w'), separators=(',', ':'))
    step('gauges_usgs', fetch_gauges, box, a.start, a.end, a.gauges, required=False)
    if a.add_points: step('add_entry_points', add_points, a.gauges, a.add_points, required=False)
    man['defaults'] = dict(aadt_by_class=AADT_DEFAULT, nlcd='if a tile fails, impervious = 0 (w9 default: no NLCD)', soils='if SDA fails, w9 LF_LOSS=cn has no soils30 and stops',
                           channels='if NHDPlus HR fails, rivers are not burnt (LF_CHAN runs without a grid)')
    json.dump(man, open(f'{a.out}/manifest.json', 'w'), indent=1); log('inputs done:', {k: v['ok'] for k, v in man['steps'].items()})


# ---------------------------------------------------------------- selftest -------------------------------------------------------------
def selftest():
    from pyproj import Transformer
    inv = Transformer.from_crs(26986, 4326, always_xy=True)
    # a plus-shaped junction: way 1 west-east 2.4 km (nodes every 400 m), way 2 north-south crossing it at the middle node, plus a bridge way
    pts = {}
    for k in range(7): pts[100 + k] = inv.transform(110000 + 400 * k, 1100000)
    for k in range(3): pts[200 + k] = inv.transform(111200, 1099600 + 400 * k)
    pts[300], pts[301] = inv.transform(112400, 1100000), inv.transform(112500, 1100000)
    els = [dict(type='node', id=i, lon=lo, lat=la) for i, (lo, la) in pts.items()]
    els += [dict(type='way', id=1, nodes=list(range(100, 107)), tags=dict(highway='primary', ref='US 2', name='Main Street')),
            dict(type='way', id=2, nodes=[200, 103, 202], tags=dict(highway='residential', name='Cross St')),
            dict(type='way', id=3, nodes=[106, 301], tags=dict(highway='primary', ref='US 2', bridge='yes')),
            dict(type='way', id=4, nodes=[200, 201], tags=dict(highway='footway'))]
    els.append(dict(type='node', id=201, lon=pts[201][0], lat=pts[201][1]))
    S, br = build_segments(els, [('Barre', *inv.transform(111000, 1100000))])
    assert S['n'] == 5, S['n']                                  # way 1: split at the junction (node 103) -> 2 pieces; way 2 -> 2; bridge -> 1
    assert S['props']['cls'][:2] == [1, 1] and S['props']['road'][0] == 'Main Street (US 2)' and S['props']['town'][0] == 'Barre'
    assert abs(S['props']['len'][0] - 1200) <= 2 and S['props']['aadt'][2] == 500, S['props']
    sys.path.insert(0, os.path.join(ROOT, 'sim', 'infra')); import impacts as IM
    dec = IM.decode_segments(S); lo, la = dec[0][1], dec[0][2]
    assert abs(lo[0] - pts[100][0]) < 1e-5 and abs(la[-1] - pts[103][1]) < 1e-5 and len(lo) == 4
    L = {tuple(l) for l in S['links']}; assert (0, 1) in L and (0, 2) in L and (1, 4) in L and (2, 3) in L, L
    assert len(br) >= 6 and all(abs(b[1] - pts[300][1]) < 1e-4 for b in br)
    # a long road gets cut every ~1 km
    els2 = [dict(type='node', id=i, lon=inv.transform(110000 + 100 * i, 1100000)[0], lat=inv.transform(110000 + 100 * i, 1100000)[1]) for i in range(26)]
    els2.append(dict(type='way', id=9, nodes=list(range(26)), tags=dict(highway='motorway', ref='I 89')))
    S2, _ = build_segments(els2); assert S2['n'] == 3 and S2['props']['len'] == [1000, 1000, 500] and S2['props']['cls'] == [2, 2, 2], S2['props']
    print('vt_inputs selftest ok')


if __name__ == '__main__':
    if '--selftest' in sys.argv: selftest(); sys.exit()
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--box', default='107000,1096000,127000,1116000'); ap.add_argument('--data'); ap.add_argument('--out', default='docs/proto/vermont_jul2023/inputs')
    ap.add_argument('--start', default='2023-07-09'); ap.add_argument('--end', default='2023-07-13'); ap.add_argument('--gauges', default='docs/proto/obs/gauges_jul2023vt.json')
    ap.add_argument('--entry-points', help='write the stream entries of this box here (nesting)'); ap.add_argument('--skip-roads', action='store_true')
    ap.add_argument('--add-points', help='entry points to append to --gauges (coarse run)')
    ap.add_argument('--make-inflows', nargs=4, metavar=('XINGS', 'META', 'POINTS', 'OUT'), help='coarse run xings.json + meta.json + entry points -> inflows json')
    a = ap.parse_args()
    if a.make_inflows: make_inflows(*a.make_inflows); sys.exit()
    main(a)
