"""Week plan, day 1: statewide data foundation on Drive (runs in the background, log in W/log_data.txt).
1. USGS 3DEP elevation at 10 m for all of Massachusetts (EPSG:26986, 20 km tiles, float32 .npy)
2. NHDPlus HR flowlines (USGS hydro service) clipped to the state box
3. USGS STN surveyed high-water marks for Massachusetts events (Sept 2023, Jan/Mar 2018, others)
4. Probe of USDA soil services (SDA) for the soil step
"""
import os, io, json, time, math, requests, numpy as np
W = '/content/drive/MyDrive/flood_atlas_state'; os.makedirs(f'{W}/dem10', exist_ok=True)
LOG = open(f'{W}/log_data.txt', 'a')
def log(*a):
    s = time.strftime('%H:%M:%S ') + ' '.join(str(x) for x in a); print(s, flush=True); LOG.write(s + '\n'); LOG.flush()
def get(url, tries=6, **kw):
    for k in range(tries):
        try:
            r = requests.get(url, timeout=240, **kw)
            if r.status_code == 200: return r
            log('  http', r.status_code, url[:120])
        except Exception as e: log('  retry', k, repr(e)[:100])
        time.sleep(4 + 6 * k)
    raise RuntimeError(url[:200])
from pyproj import Transformer
tr = Transformer.from_crs(4326, 26986, always_xy=True)
# whole state with a margin (EPSG:26986 metres)
xs, ys = tr.transform([-73.55, -69.88, -73.55, -69.88], [41.22, 41.22, 42.90, 42.90])
X0, X1 = math.floor(min(xs) / 20000) * 20000, math.ceil(max(xs) / 20000) * 20000
Y0, Y1 = math.floor(min(ys) / 20000) * 20000, math.ceil(max(ys) / 20000) * 20000
T = 20000; R = 10.0; NPX = int(T / R)
tiles = [(x, y) for x in range(X0, X1, T) for y in range(Y0, Y1, T)]
log(f'DEM 10 m: box {X0}-{X1} x {Y0}-{Y1}, {len(tiles)} tiles of {NPX}px')
import tifffile
index = {}
ip = f'{W}/dem10/index.json'
if os.path.exists(ip): index = json.load(open(ip))
t0 = time.time()
for n, (x, y) in enumerate(tiles):
    key = f'{x}_{y}'
    if key in index: continue
    u = ('https://elevation.nationalmap.gov/arcgis/rest/services/3DEPElevation/ImageServer/exportImage'
         f'?bbox={x},{y},{x + T},{y + T}&bboxSR=26986&imageSR=26986&size={NPX},{NPX}&format=tiff&pixelType=F32'
         '&noDataInterpretation=esriNoDataMatchAny&interpolation=RSP_BilinearInterpolation&f=image')
    a = tifffile.imread(io.BytesIO(get(u).content)).astype(np.float32)
    a = a[..., 0] if a.ndim == 3 else a
    a[(a < -100) | (a > 2000)] = np.nan
    valid = float(np.isfinite(a).mean())
    if valid > 0: np.save(f'{W}/dem10/{key}.npy', a)
    index[key] = dict(x=x, y=y, valid=round(valid, 3), zmin=float(np.nanmin(a)) if valid else None, zmax=float(np.nanmax(a)) if valid else None)
    json.dump(index, open(ip, 'w'))
    if n % 10 == 0: log(f'  tile {n + 1}/{len(tiles)} {key} valid {valid:.2f} | {time.time() - t0:.0f}s')
log('DEM done', sum(1 for v in index.values() if v['valid'] > 0), 'tiles with land/water data')
# ---- NHDPlus HR flowlines ----
try:
    svc = 'https://hydro.nationalmap.gov/arcgis/rest/services/NHDPlus_HR/MapServer'
    L = get(svc + '?f=json').json()['layers']; log('NHDPlus HR layers:', [(l['id'], l['name']) for l in L][:30])
    lid = next(l['id'] for l in L if 'flowline' in l['name'].lower() and 'network' in l['name'].lower()) if any('network' in l['name'].lower() for l in L) else next(l['id'] for l in L if 'flowline' in l['name'].lower())
    feats = []; off = 0
    while True:
        q = get(f'{svc}/{lid}/query', params=dict(geometry='-73.55,41.22,-69.88,42.90', geometryType='esriGeometryEnvelope', inSR=4326, spatialRel='esriSpatialRelIntersects',
                                                    outFields='*', returnGeometry='true', outSR=4326, f='geojson', resultOffset=off, resultRecordCount=2000)).json()
        fs = q.get('features', []); feats += fs; off += len(fs)
        if off % 20000 < 2000: log(f'  flowlines {off:,}')
        if len(fs) < 2000 and not q.get('properties', {}).get('exceededTransferLimit'): break
    json.dump(dict(type='FeatureCollection', features=feats), open(f'{W}/nhdplushr_flowlines.geojson', 'w'))
    log('NHDPlus HR flowlines saved', len(feats))
except Exception as e: log('NHDPlus HR failed', repr(e)[:300])
# ---- USGS STN high-water marks ----
try:
    ev = get('https://stn.wim.usgs.gov/STNServices/Events.json').json()
    cand = [e for e in ev if any(k in (e.get('event_name') or '').lower() for k in ('2018', '2023', 'nor', 'massachusetts', 'new england', 'ma '))]
    log('STN events (candidates):', [(e['event_id'], e['event_name'], (e.get('event_start_date') or '')[:10]) for e in cand][:60])
    out = {}
    for e in cand:
        try:
            h = get(f"https://stn.wim.usgs.gov/STNServices/HWMs/FilteredHWMs.json?Event={e['event_id']}&States=MA", tries=2).json()
            if h: out[e['event_id']] = dict(name=e['event_name'], start=e.get('event_start_date'), hwms=h); log('  HWMs', e['event_name'], len(h))
        except Exception as ex: pass
    json.dump(out, open(f'{W}/stn_hwms_ma.json', 'w')); log('STN saved events with MA marks:', len(out))
except Exception as e: log('STN failed', repr(e)[:300])
# ---- soils probe ----
try:
    r = requests.post('https://sdmdataaccess.sc.egov.usda.gov/tabular/post.rest', json=dict(format='JSON', query=
        "SELECT TOP 5 l.areasymbol, m.mukey, a.hydgrpdcd FROM legend l JOIN mapunit m ON m.lkey = l.lkey JOIN muaggatt a ON a.mukey = m.mukey WHERE l.areasymbol LIKE 'MA%'"), timeout=120)
    log('SDA tabular:', r.status_code, r.text[:300])
except Exception as e: log('SDA failed', repr(e)[:200])
log('ALL DONE')
