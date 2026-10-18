"""Statewide 30 m soil grids for the flood engine, from USDA SSURGO through Soil Data Access (free, no key).

Outputs (EPSG:26986, whole state: x 30000..340000, y 780000..960000, 30 m -> 6000 x 10333):
    soils30.npz   hydgrp  uint8  hydrologic soil group: 1 A, 2 B, 3 C, 4 D, 5 A/D, 6 B/D, 7 C/D, 0 unknown/water/urban
                  ksat    uint8  saturated conductivity of the surface layer, mm/h (capped at 250)
                  wtd     uint8  shallowest annual water table, cm / 2 (0 = none reported within 2 m -> 255)
                  drcl    uint8  drainage class 1 excessively .. 7 very poorly drained, 0 unknown
    soils30_meta.json
Run on GitHub Actions (soils.yml) and uploaded to Hugging Face data/soils30/.
"""
import os, io, json, time, math, sys
import numpy as np, requests
from shapely import wkt
from shapely.geometry import box
from rasterio import features
from rasterio.transform import from_origin
from pyproj import Transformer

SDA = 'https://sdmdataaccess.sc.egov.usda.gov/tabular/post.rest'
BOX = tuple(int(v) for v in os.environ.get('BOX', '30000,780000,340000,960000').split(',')); RES = 30   # whole state
nx, ny = int((BOX[2] - BOX[0]) / RES), int((BOX[3] - BOX[1]) / RES)
tr = from_origin(BOX[0], BOX[3], RES, RES)
log = lambda *a: print(time.strftime('%H:%M:%S'), *a, flush=True)

def q(sql, tries=5):
    for k in range(tries):
        try:
            r = requests.post(SDA, json=dict(format='JSON', query=sql), timeout=600)
            if r.status_code == 200: return r.json().get('Table', [])
            log('  SDA', r.status_code, r.text[:160])
        except Exception as e: log('  SDA error', repr(e)[:120])
        time.sleep(15 * (k + 1))
    return []

# 1. attributes per map unit for all Massachusetts (and neighbouring) survey areas inside the box
rows = q("""SELECT m.mukey, a.hydgrpdcd, a.drclassdcd, a.wtdepannmin, a.aws0100wta, a.brockdepmin FROM legend l JOIN mapunit m ON m.lkey = l.lkey
            LEFT JOIN muaggatt a ON a.mukey = m.mukey WHERE l.areasymbol LIKE 'MA%' OR l.areasymbol LIKE 'RI%' OR l.areasymbol LIKE 'NH%' OR l.areasymbol LIKE 'CT%' OR l.areasymbol LIKE 'NY%' OR l.areasymbol LIKE 'VT%'""")
log('map units with attributes:', len(rows))
HG = {'A': 1, 'B': 2, 'C': 3, 'D': 4, 'A/D': 5, 'B/D': 6, 'C/D': 7}
DR = {'Excessively drained': 1, 'Somewhat excessively drained': 2, 'Well drained': 3, 'Moderately well drained': 4, 'Somewhat poorly drained': 5, 'Poorly drained': 6, 'Very poorly drained': 7}
ATTR = {}
for mukey, hg, dr, wt, aws, br in rows:
    ATTR[str(mukey)] = [HG.get(hg or '', 0), DR.get(dr or '', 0), 255 if wt in (None, '') else min(254, int(float(wt) / 2)),
                        0 if aws in (None, '') else min(250, int(round(float(aws)))), 255 if br in (None, '') else min(254, int(float(br) / 2))]   # aws: mm in top 100 cm; brock: cm/2
# surface-layer ksat of the dominant component (µm/s -> mm/h: x3.6)
ks = q("""SELECT c.mukey, c.comppct_r, h.ksat_r FROM component c JOIN chorizon h ON h.cokey = c.cokey JOIN mapunit m ON m.mukey = c.mukey JOIN legend l ON l.lkey = m.lkey
          WHERE h.hzdept_r = 0 AND c.majcompflag = 'Yes' AND h.ksat_r IS NOT NULL AND (l.areasymbol LIKE 'MA%' OR l.areasymbol LIKE 'RI%' OR l.areasymbol LIKE 'NH%' OR l.areasymbol LIKE 'CT%' OR l.areasymbol LIKE 'NY%' OR l.areasymbol LIKE 'VT%')""")
KS = {}
for mukey, pct, k in ks:
    mukey = str(mukey); pct = float(pct or 0)
    if mukey not in KS or pct > KS[mukey][0]: KS[mukey] = (pct, min(250, int(float(k) * 3.6)))
log('ksat for', len(KS), 'map units')

# 2. polygons by lon/lat chunk, rasterised straight into the state grid
to_m = Transformer.from_crs(4326, 26986, always_xy=True); to_ll = Transformer.from_crs(26986, 4326, always_xy=True)
W, S = to_ll.transform(BOX[0], BOX[1]); E, N = to_ll.transform(BOX[2], BOX[3])
hyd = np.zeros((ny, nx), np.uint8); ksat = np.zeros((ny, nx), np.uint8); wtd = np.full((ny, nx), 255, np.uint8); drcl = np.zeros((ny, nx), np.uint8); aws = np.zeros((ny, nx), np.uint8); brock = np.full((ny, nx), 255, np.uint8)
from shapely.ops import transform as shp_transform
step = 0.25; npoly = 0; t0 = time.time()
lons = np.arange(math.floor(W * 4) / 4, E, step); lats = np.arange(math.floor(S * 4) / 4, N, step)
for i, la in enumerate(lats):
    for lo in lons:
        poly = f'POLYGON(({lo} {la},{lo + step} {la},{lo + step} {la + step},{lo} {la + step},{lo} {la}))'
        rs = q(f"SELECT mukey, mupolygongeo.STAsText() AS g FROM mupolygon WHERE mupolygongeo.STIntersects(geometry::STGeomFromText('{poly}', 4326)) = 1")
        if not rs: continue
        shapes_h, shapes_k, shapes_w, shapes_d, shapes_a, shapes_b = [], [], [], [], [], []
        for mukey, g in rs:
            try: geom = shp_transform(to_m.transform, wkt.loads(g))
            except Exception: continue
            a = ATTR.get(str(mukey)); k = KS.get(str(mukey))
            if a:
                if a[0]: shapes_h.append((geom, a[0]))
                if a[1]: shapes_d.append((geom, a[1]))
                if a[2] != 255: shapes_w.append((geom, a[2]))
                if a[3]: shapes_a.append((geom, a[3]))
                if a[4] != 255: shapes_b.append((geom, a[4]))
            if k: shapes_k.append((geom, k[1]))
        for shp, arr in ((shapes_h, hyd), (shapes_k, ksat), (shapes_w, wtd), (shapes_d, drcl), (shapes_a, aws), (shapes_b, brock)):
            if shp: features.rasterize(shp, out=arr, transform=tr, default_value=0, all_touched=False)
        npoly += len(rs)
    log(f'row {i + 1}/{len(lats)} lat {la:.2f}: {npoly} polygons so far, {time.time() - t0:.0f}s')
cov = (hyd > 0).mean()
log(f'done: {npoly} polygons, hydrologic group known on {cov * 100:.1f}% of cells, ksat on {(ksat > 0).mean() * 100:.1f}%')
os.makedirs('out', exist_ok=True)
np.savez_compressed('out/soils30.npz', hydgrp=hyd, ksat=ksat, wtd=wtd, drcl=drcl, aws=aws, brock=brock)
json.dump(dict(box=BOX, res_m=RES, crs='EPSG:26986', shape=[ny, nx], polygons=npoly, coverage=round(float(cov), 3), source='USDA SSURGO via Soil Data Access, fetched ' + time.strftime('%Y-%m-%d'),
               legend=dict(hydgrp=HG, drcl=DR, ksat='mm/h surface layer, dominant component', wtd='cm/2, 255 = none within 2 m', aws='available water storage 0-100 cm, mm', brock='depth to bedrock cm/2, 255 = none/unknown')), open('out/soils30_meta.json', 'w'), indent=1)
if os.environ.get('HF_TOKEN'):
    from huggingface_hub import HfApi
    api = HfApi(token=os.environ['HF_TOKEN'])
    for f in ('soils30.npz', 'soils30_meta.json'):
        api.upload_file(path_or_fileobj=f'out/{f}', path_in_repo=f'data/soils30/{f}', repo_id='mohabeldokla/mass-flood-watch-tiles', repo_type='dataset')
    log('uploaded to Hugging Face data/soils30/')
