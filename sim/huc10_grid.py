"""HUC10 watershed ids on the whole-state 30 m grid, for the pre-registered spatial-block cross-validation (docs/validation/protocol.md).

Source: USGS Watershed Boundary Dataset, HU10 layer of the National Map hydro service (free).  Output data/huc10_30/huc10_30.npz
(field `huc10` int64, 0 = outside any HU10) + huc10_30_meta.json, same box/res as channels30 (EPSG:26986, 30 m).  Run by huc10.yml.
"""
import os, json, time
import numpy as np, requests
from shapely.geometry import shape
from rasterio import features
from rasterio.transform import from_origin

BOX = tuple(int(v) for v in os.environ.get('BOX', '30000,780000,340000,960000').split(',')); RES = 30
x0, y0, x1, y1 = BOX; nx, ny = (x1 - x0) // RES, (y1 - y0) // RES; tr = from_origin(x0, y1, RES, RES)
log = lambda *a: print(time.strftime('%H:%M:%S'), *a, flush=True)
URL = 'https://hydro.nationalmap.gov/arcgis/rest/services/wbd/MapServer/5/query'       # layer 5 = 10-digit HU
H = {'User-Agent': 'mass-flood-watch research (github.com/Horus331/mass-flood-watch)'}
geom = json.dumps(dict(xmin=x0, ymin=y0, xmax=x1, ymax=y1, spatialReference=dict(wkid=26986)))
feats, off = [], 0
while True:
    for k in range(5):
        try:
            r = requests.get(URL, params=dict(where='1=1', geometry=geom, geometryType='esriGeometryEnvelope', inSR=26986, spatialRel='esriSpatialRelIntersects',
                                              outFields='huc10,name', returnGeometry='true', outSR=26986, f='geojson', resultOffset=off, resultRecordCount=200,
                                              orderByFields='huc10'), headers=H, timeout=300)
            r.raise_for_status(); G = r.json(); break
        except Exception as e: log('retry', k, repr(e)[:100]); time.sleep(10 + 20 * k)
    else: raise SystemExit('WBD service unreachable')
    fs = G.get('features', []); feats += fs; off += len(fs); log('got', off)
    if len(fs) < 200: break
log(len(feats), 'HU10 polygons')
shapes = [(shape(f['geometry']), int(f['properties']['huc10'])) for f in feats if f.get('geometry')]
huc = features.rasterize(shapes, out_shape=(ny, nx), transform=tr, fill=0, dtype='int64')
os.makedirs('out', exist_ok=True); np.savez_compressed('out/huc10_30.npz', huc10=huc)
json.dump(dict(box=BOX, res_m=RES, crs='EPSG:26986', shape=[ny, nx], n_huc10=len(set(s[1] for s in shapes)), covered_share=round(float((huc > 0).mean()), 3),
               names={str(f['properties']['huc10']): f['properties'].get('name') for f in feats}, source='USGS WBD HU10 via hydro.nationalmap.gov', made=time.strftime('%Y-%m-%d')),
          open('out/huc10_30_meta.json', 'w'), indent=0)
log(f'{len(set(s[1] for s in shapes))} HU10 ids, {float((huc > 0).mean()) * 100:.1f}% of the grid covered')
if os.environ.get('HF_TOKEN'):
    from huggingface_hub import HfApi
    api = HfApi(token=os.environ['HF_TOKEN'])
    for f in ('huc10_30.npz', 'huc10_30_meta.json'):
        api.upload_file(path_or_fileobj=f'out/{f}', path_in_repo=f'data/huc10_30/{f}', repo_id='mohabeldokla/mass-flood-watch-tiles', repo_type='dataset')
    log('uploaded data/huc10_30/')
