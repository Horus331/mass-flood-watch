"""Channel and open-water grids for the flood engine, from NHDPlus HR flowlines (free, already on Hugging Face).

Outputs on the whole-state 30 m grid (EPSG:26986, x 30000..340000, y 780000..960000 -> 6000 x 10333), channels30.npz:
    chan    bool     cell lies on a flowline (rivers and streams)
    water   bool     open water: flowline cells buffered to bankfull width, plus artificial paths through lakes/ponds (ftype 558)
                     -> no infiltration and no storm drains are taken from these cells
    area    float32  upstream drainage area at the flowline cell (km2, largest where lines meet), 0 elsewhere
    width   float16  bankfull width W = 2.70 * A^0.352 (m)  (Bieger et al. 2015, US regressions)
    depth   float16  bankfull depth  D = 0.30 * A^0.213 (m)
Used by w4_flood_gpu.py for (a) the water mask (no losses on water), (b) sub-grid channel burn D*W/dx on channel cells, (c) channel Manning n.
Run on GitHub Actions (channels.yml) and uploaded to HF data/channels30/.
"""
import os, json, time, math
import numpy as np, requests
from shapely.geometry import shape
from shapely.ops import transform as shp_transform
from rasterio import features
from rasterio.transform import from_origin
from pyproj import Transformer
from huggingface_hub import hf_hub_download

REPO = 'mohabeldokla/mass-flood-watch-tiles'
BOX = tuple(int(v) for v in os.environ.get('BOX', '30000,780000,340000,960000').split(',')); RES = 30
x0, y0, x1, y1 = BOX; nx, ny = (x1 - x0) // RES, (y1 - y0) // RES; tr = from_origin(x0, y1, RES, RES)
log = lambda *a: print(time.strftime('%H:%M:%S'), *a, flush=True)
p = hf_hub_download(REPO, 'data/nhdplushr_flowlines.geojson', repo_type='dataset'); log('flowlines file', os.path.getsize(p) // 2**20, 'MB')
G = json.load(open(p)); feats = G['features']; log('features', len(feats))
keys = {k.lower(): k for k in feats[0]['properties']}; log('fields:', sorted(keys)[:40])
ka = keys.get('totdasqkm'); kf = keys.get('ftype'); log('area field', ka, 'ftype field', kf)
to_m = Transformer.from_crs(4326, 26986, always_xy=True).transform
def bankfull_w(A):
    """Bieger et al. 2015 width, widened for large rivers (the national regression under-predicts the Connecticut/Merrimack main stems by ~2x)."""
    if A <= 0: return 1.0
    return 2.70 * A ** 0.352 * ((A / 500.0) ** 0.15 if A > 500 else 1.0)
chan_shapes, water_shapes, area_shapes = [], [], []
nlake = 0
for f in feats:
    try: g = shp_transform(to_m, shape(f['geometry']))
    except Exception: continue
    pr = f['properties']; A = float(pr.get(ka) or 0) if ka else 0.0; ft = int(pr.get(kf) or 0) if kf else 0
    chan_shapes.append((g, 1)); area_shapes.append((g, A))
    W = bankfull_w(A)
    if ft == 558: nlake += 1
    if W > RES or ft == 558:                          # rivers wider than a cell, and paths through lakes: buffer to width
        water_shapes.append((g.buffer(max(W, RES) / 2 if ft != 558 else 60.0), 1))
log('rasterising', len(chan_shapes), 'lines;', nlake, 'lake paths')
chan = features.rasterize(chan_shapes, out_shape=(ny, nx), transform=tr, default_value=1, all_touched=True, dtype='uint8').astype(bool)
area = features.rasterize(sorted([t for t in area_shapes if t[1] > 0], key=lambda t: t[1]), out_shape=(ny, nx), transform=tr, all_touched=True, dtype='float32')   # later (larger) shapes overwrite
water = features.rasterize(water_shapes, out_shape=(ny, nx), transform=tr, default_value=1, all_touched=True, dtype='uint8').astype(bool) | chan & (area > 50)
A_ = np.maximum(area, 0.01); width = np.where(chan, 2.70 * A_ ** 0.352 * np.where(A_ > 500, (A_ / 500.0) ** 0.15, 1.0), 0).astype(np.float16)
depth = np.where(chan, 0.30 * np.maximum(area, 0.01) ** 0.213, 0).astype(np.float16)
log(f'channel cells {chan.sum():,} ({chan.mean() * 100:.2f}%), water cells {water.sum():,} ({water.mean() * 100:.2f}%), max area {area.max():.0f} km2')
os.makedirs('out', exist_ok=True)
np.savez_compressed('out/channels30.npz', chan=chan, water=water, area=area, width=width, depth=depth)
json.dump(dict(box=BOX, res_m=RES, crs='EPSG:26986', shape=[ny, nx], flowlines=len(feats), lake_paths=nlake, chan_cells=int(chan.sum()), water_cells=int(water.sum()),
               source='NHDPlus HR flowlines via USGS hydro service; bankfull geometry Bieger et al. 2015', made=time.strftime('%Y-%m-%d')), open('out/channels30_meta.json', 'w'), indent=1)
if os.environ.get('HF_TOKEN'):
    from huggingface_hub import HfApi
    api = HfApi(token=os.environ['HF_TOKEN'])
    for f in ('channels30.npz', 'channels30_meta.json'):
        api.upload_file(path_or_fileobj=f'out/{f}', path_in_repo=f'data/channels30/{f}', repo_id=REPO, repo_type='dataset')
    log('uploaded data/channels30/')
