"""Ground heights for the How it works sketch: USGS 3DEP bare earth resampled to 20 m (the model's grid size) over the sketch box.
    python proto/howit_dem.py   (GitHub workflow gw_scout.yml with script=howit_dem.py; the USGS service is not reachable from the shell)
    -> docs/how-it-works/sketch/dem20.npz  (z, metres; x0, y1 upper-left corner in EPSG:26986; 20 m cells)"""
import io, os, numpy as np, requests, tifffile
BOX = (174400, 915000, 182400, 922600)          # x0, y0, x1, y1 (EPSG:26986, m); a little wider than the drawn area
SVC = 'https://elevation.nationalmap.gov/arcgis/rest/services/3DEPElevation/ImageServer/exportImage'
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'docs/how-it-works/sketch/dem20.npz')
x0, y0, x1, y1 = BOX; w, h = (x1 - x0) // 20, (y1 - y0) // 20
q = dict(bbox=f'{x0},{y0},{x1},{y1}', bboxSR=26986, imageSR=26986, size=f'{w},{h}', format='tiff', pixelType='F32',
         interpolation='RSP_BilinearInterpolation', noData=-9999, f='image')
for k in range(5):
    r = requests.get(SVC, params=q, timeout=300)
    if r.status_code == 200 and r.content[:2] in (b'II', b'MM'): break
    print('retry', r.status_code, r.content[:100])
z = tifffile.imread(io.BytesIO(r.content)).astype(np.float32); z[z < -1000] = np.nan
os.makedirs(os.path.dirname(OUT), exist_ok=True); np.savez_compressed(OUT, z=z, x0=x0, y1=y1, cell=20)
print('dem', z.shape, np.nanmin(z), np.nanmax(z))
