"""MassGIS 2023 orthophoto (web tiles, zoom 15) resampled to 5 m over the Leominster catalogue box (EPSG:26986 162000,908000,182000,928000):
basemap for the parametric clean-rerun culvert map. Run on GitHub (gw_scout.yml, script=param_aerial.py).
    -> docs/proto/phase1/fig/aerial_leominster_box_5m.jpg (4000 x 4000 px, upper-left = (162000, 928000))"""
import io, math, os, time, numpy as np, requests
from concurrent.futures import ThreadPoolExecutor
from PIL import Image
from pyproj import Transformer
URL = 'https://tiles.arcgis.com/tiles/hGdibHYSPO59RG1h/arcgis/rest/services/orthos2023/MapServer/tile/{z}/{y}/{x}'
BOX = (162000, 908000, 182000, 928000); PX = 5.0; Z = 15
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'docs/proto/phase1/fig/aerial_leominster_box_5m.jpg')
x0, y0, x1, y1 = BOX; W, H = int((x1 - x0) / PX), int((y1 - y0) / PX)
xs = x0 + (np.arange(W) + 0.5) * PX; ys = y1 - (np.arange(H) + 0.5) * PX; X, Y = np.meshgrid(xs, ys)
lon, lat = Transformer.from_crs(26986, 4326, always_xy=True).transform(X, Y)
n = 2 ** Z; gx = (lon + 180) / 360 * n * 256; gy = (1 - np.log(np.tan(np.radians(lat)) + 1 / np.cos(np.radians(lat))) / math.pi) / 2 * n * 256
tx0, tx1, ty0, ty1 = int(gx.min() // 256), int(gx.max() // 256), int(gy.min() // 256), int(gy.max() // 256)
print('tiles', (tx1 - tx0 + 1) * (ty1 - ty0 + 1))
mos = np.zeros(((ty1 - ty0 + 1) * 256, (tx1 - tx0 + 1) * 256, 3), np.uint8)
def get(t):
    tx, ty = t
    for k in range(5):
        try:
            r = requests.get(URL.format(z=Z, x=tx, y=ty), timeout=60, headers={'User-Agent': 'mass-flood-watch research (WPI)'})
            if r.status_code == 200:
                return t, np.asarray(Image.open(io.BytesIO(r.content)).convert('RGB'))
        except Exception as e: print('retry', t, repr(e)[:80])
        time.sleep(2 * (k + 1))
    return t, None
with ThreadPoolExecutor(12) as ex:
    for (tx, ty), a in ex.map(get, [(tx, ty) for ty in range(ty0, ty1 + 1) for tx in range(tx0, tx1 + 1)]):
        if a is not None: mos[(ty - ty0) * 256:(ty - ty0 + 1) * 256, (tx - tx0) * 256:(tx - tx0 + 1) * 256] = a[:256, :256]
c = np.clip((gx - tx0 * 256).astype(int), 0, mos.shape[1] - 1); r = np.clip((gy - ty0 * 256).astype(int), 0, mos.shape[0] - 1)
os.makedirs(os.path.dirname(OUT), exist_ok=True); Image.fromarray(mos[r, c]).save(OUT, quality=88, optimize=True)
print('aerial', W, H, OUT)
