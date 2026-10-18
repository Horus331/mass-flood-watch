"""Week plan, day 1b: 10 m drainage for all of Massachusetts from USGS NHDPlus HR rasters.

NHDPlus HR ships, per 4-digit watershed (HU4), a 10 m flow-direction grid (fdr: D8, ESRI codes 1,2,4,...,128) and flow
accumulation (fac), built from 3DEP elevation with the mapped streams burned in, so channels follow the real rivers.
We use those directly (no re-gridding of directions, which would break them), clip to the state, and cut the grid into
2048 x 2048 tiles of one byte per cell:  byte = direction 1..8 (N NE E SE S SW W NW) + 9 * upstream-area class 0..27,
0 = no flow (sea / outside).  Tiles stay in the native EPSG:5070 (Albers) grid; the browser converts positions to lon/lat.

Outputs on local disk /content/drain10/ (tiles + index.json), copied to Drive W/drain10/.
"""
import os, re, io, json, time, math, subprocess, shutil, requests, numpy as np
W = '/content/drive/MyDrive/flood_atlas_state'; L = '/content/nhd'; OUT = '/content/drain10'
os.makedirs(L, exist_ok=True); os.makedirs(OUT, exist_ok=True); os.makedirs(f'{W}/drain10', exist_ok=True)
LOG = open(f'{W}/log_drain10.txt', 'a')
def log(*a):
    s = time.strftime('%H:%M:%S ') + ' '.join(str(x) for x in a); print(s, flush=True); LOG.write(s + '\n'); LOG.flush()
subprocess.run('apt-get -qq install -y p7zip-full > /dev/null 2>&1; pip -q install rasterio', shell=True)
import rasterio
from rasterio.windows import from_bounds
from pyproj import Transformer
HU4 = ['0107', '0108', '0109', '0110', '0202']
BASE = 'https://prd-tnm.s3.amazonaws.com'
# state box in EPSG:5070
tr = Transformer.from_crs(4326, 5070, always_xy=True)
xs, ys = tr.transform([-73.55, -69.88, -73.55, -69.88, -71.7, -71.7], [41.22, 41.22, 42.90, 42.90, 41.22, 42.90])
BX0, BX1 = math.floor(min(xs) / 10) * 10, math.ceil(max(xs) / 10) * 10; BY0, BY1 = math.floor(min(ys) / 10) * 10, math.ceil(max(ys) / 10) * 10
NX, NY = int((BX1 - BX0) / 10), int((BY1 - BY0) / 10)
log(f'state grid (EPSG:5070, 10 m): {NX} x {NY} = {NX * NY / 1e6:.0f} M cells')
FDR = np.zeros((NY, NX), np.uint8); LV = np.zeros((NY, NX), np.uint8)
ESRI = {64: 1, 128: 2, 1: 3, 2: 4, 4: 5, 8: 6, 16: 7, 32: 8}                 # ESRI D8 code -> our N NE E SE S SW W NW
lut = np.zeros(256, np.uint8)
for k, v in ESRI.items(): lut[k] = v
for hu in HU4:
    try:
        lst = requests.get(f'{BASE}/?prefix=StagedProducts/Hydrography/NHDPlusHR/Beta/GDB/NHDPLUS_H_{hu}', timeout=120).text
        keys = re.findall(r'<Key>([^<]+RASTER[^<]*)</Key>', lst); log(hu, 'raster packages:', keys)
        if not keys: continue
        key = keys[0]; z = f'{L}/{os.path.basename(key)}'
        if not os.path.exists(z):
            with requests.get(f'{BASE}/{key}', stream=True, timeout=600) as r:
                with open(z, 'wb') as f: shutil.copyfileobj(r.raw, f, 1 << 24)
        log(hu, 'downloaded', os.path.getsize(z) // 2**20, 'MB')
        d = f'{L}/{hu}'; os.makedirs(d, exist_ok=True)
        subprocess.run(f'7z x -y -o{d} {z} -ir!fdr.tif -ir!fac.tif > /dev/null', shell=True)
        log(hu, 'extracted:', [os.path.join(a, f) for a, _, fs in os.walk(d) for f in fs][:6])
        tifs = [os.path.join(a, f) for a, _, fs in os.walk(d) for f in fs if f.lower().endswith(('.tif', '.adf')) or f.lower() in ('hdr.adf',)]
        fdr_p = next((os.path.join(a, f) for a, ds, fs in os.walk(d) for f in fs if f.lower() == 'fdr.tif'), None)
        fac_p = next((os.path.join(a, f) for a, ds, fs in os.walk(d) for f in fs if f.lower() == 'fac.tif'), None)
        log(hu, 'fdr', fdr_p, 'fac', fac_p)
        with rasterio.open(fdr_p) as A, rasterio.open(fac_p) as B:
            log(hu, 'crs', A.crs, 'res', A.res, 'shape', A.shape)
            assert 'Albers' in A.crs.to_wkt() or str(A.crs).endswith('5070'), A.crs
            x0, y0, x1, y1 = max(BX0, A.bounds.left), max(BY0, A.bounds.bottom), min(BX1, A.bounds.right), min(BY1, A.bounds.top)
            if x1 <= x0 or y1 <= y0: continue
            win = from_bounds(x0, y0, x1, y1, A.transform).round_offsets().round_lengths()
            c0 = int(round((A.transform.c + win.col_off * 10 - BX0) / 10)); r0 = int(round((BY1 - (A.transform.f - win.row_off * 10)) / 10))
            H, Wd = int(win.height), int(win.width); H = min(H, NY - r0); Wd = min(Wd, NX - c0)
            BAND = 1024                                                   # read in bands: this machine has 12 GB
            from rasterio.windows import Window
            for rb in range(0, H, BAND):
                hb = min(BAND, H - rb)
                wb = Window(win.col_off, win.row_off + rb, Wd, hb)
                a = A.read(1, window=wb); b = B.read(1, window=wb)
                code = lut[np.clip(a, 0, 255).astype(np.uint8)]; code[(a <= 0) | (a > 128)] = 0
                lv = np.clip(np.floor(np.log2(np.maximum(b.astype(np.float32), 1))), 0, 27).astype(np.uint8)
                sel = code > 0
                FDR[r0 + rb:r0 + rb + hb, c0:c0 + Wd][sel] = code[sel]; LV[r0 + rb:r0 + rb + hb, c0:c0 + Wd][sel] = lv[sel]
                del a, b, code, lv, sel
            log(hu, f'placed at row {r0} col {c0} ({H} x {Wd})')
        shutil.rmtree(d, ignore_errors=True)
    except Exception as e:
        log(hu, 'FAILED', repr(e)[:300])
log(f'flow cells: {(FDR > 0).mean() * 100:.1f}% of the state box')
# tiles
from PIL import Image
T = 2048; idx = dict(crs='EPSG:5070', res=10, x0=BX0, y1=BY1, nx=NX, ny=NY, tile=T, tiles=[])
for r in range(0, NY, T):
    for c in range(0, NX, T):
        f = FDR[r:r + T, c:c + T]; v = LV[r:r + T, c:c + T]
        if not (f > 0).any(): continue
        byte = np.where(f > 0, f + 9 * v, 0).astype(np.uint8)
        name = f'd_{r // T}_{c // T}.png'; Image.fromarray(byte, 'L').save(f'{OUT}/{name}', optimize=True)
        idx['tiles'].append([r // T, c // T, name, os.path.getsize(f'{OUT}/{name}') // 1024])
json.dump(idx, open(f'{OUT}/index.json', 'w'))
subprocess.run(f'cp -r {OUT}/. {W}/drain10/', shell=True)
log('tiles', len(idx['tiles']), 'total MB', sum(t[3] for t in idx['tiles']) // 1024, '| ALL DONE')
