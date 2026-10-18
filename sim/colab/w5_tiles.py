"""Turn a GPU run's depth frames (EPSG:26986 class images) into web-map tiles, one PMTiles archive per frame.

    RUN_DIR=runs/dec2023_30m python w5_tiles.py        (env: RUN_DIR on Hugging Face, ZMAX max zoom (default from cell size))

Each frame is warped to Web Mercator (EPSG:3857) with nearest-neighbour resampling, coloured with the site's depth ramp,
cut into 256 px PNG tiles for zooms 7..ZMAX and packed into <frame>.pmtiles (a single file the browser reads with HTTP
range requests, so a 30-frame storm is 30 files, not 200,000).  Uploads to HF under <RUN_DIR>/tiles/.
"""
import os, io, json, math, time, sys, subprocess
subprocess.run([sys.executable, '-m', 'pip', 'install', '-q', 'rasterio', 'pmtiles', 'mercantile'], check=False)
import numpy as np, rasterio
from rasterio.transform import from_origin
from rasterio.warp import reproject, Resampling, transform_bounds
from PIL import Image
import mercantile
from pmtiles.writer import Writer
from pmtiles.tile import zxy_to_tileid, TileType, Compression
from huggingface_hub import HfApi, hf_hub_download, CommitOperationAdd
RUN_DIR = os.environ.get('RUN_DIR', 'runs/dec2023_30m'); REPO = 'mohabeldokla/mass-flood-watch-tiles'; TOK = os.environ.get('HF_TOKEN')
api = HfApi(token=TOK)
LOGP = '/content/log_tiles.txt'
def log(*a):
    s = time.strftime('%H:%M:%S ') + ' '.join(str(x) for x in a); print(s, flush=True); open(LOGP, 'a').write(s + '\n')
meta = json.load(open(hf_hub_download(REPO, f'{RUN_DIR}/meta.json', repo_type='dataset', token=TOK)))
x0, y0, x1, y1 = meta['box']; res = meta['res_m']; ny, nx = meta['shape']
ZMAX = int(os.environ.get('ZMAX', 0)) or (14 if res <= 12 else 13 if res <= 25 else 12)
ZMIN = 7
# colours for the 5 depth classes (same ramp as the site), class 0 transparent
RAMP = np.array([[0, 0, 0, 0], [110, 196, 250, 150], [56, 146, 232, 195], [24, 98, 200, 222], [12, 54, 140, 238], [8, 30, 90, 248]], np.uint8)
src_tr = from_origin(x0, y1, res, res)
W, S, E, N = transform_bounds('EPSG:26986', 'EPSG:4326', x0, y0, x1, y1)
log(f'{RUN_DIR}: {len(meta["frames"])} frames, zoom {ZMIN}-{ZMAX}, lon {W:.3f}..{E:.3f} lat {S:.3f}..{N:.3f}')
OUT = '/content/tiles'; os.makedirs(OUT, exist_ok=True)
have = set(api.list_repo_files(REPO, repo_type='dataset'))
def warp_top(cls):
    """Nearest-neighbour warp of the class image onto the mercator tile grid at ZMAX, with the tile origin aligned so that
    every lower zoom is an exact 2x2 pooling of the level above (deepest class wins, like the site's overview frames)."""
    z = ZMAX; A = 1 << (ZMAX - ZMIN)
    tl = mercantile.tile(W, N, z); br = mercantile.tile(E, S, z)
    tx0, ty0 = tl.x - tl.x % A, tl.y - tl.y % A; tx1, ty1 = br.x + (A - 1 - br.x % A), br.y + (A - 1 - br.y % A)
    wpx, hpx = (tx1 - tx0 + 1) * 256, (ty1 - ty0 + 1) * 256
    b0 = mercantile.xy_bounds(tx0, ty0, z); b1 = mercantile.xy_bounds(tx1, ty1, z)
    dst_tr = from_origin(b0.left, b0.top, (b1.right - b0.left) / wpx, (b0.top - b1.bottom) / hpx)
    dst = np.zeros((hpx, wpx), np.uint8)
    reproject(cls, dst, src_transform=src_tr, src_crs='EPSG:26986', dst_transform=dst_tr, dst_crs='EPSG:3857', resampling=Resampling.nearest, src_nodata=0, dst_nodata=0, num_threads=4)
    return dst, tx0, ty0
def pack(name, cls):
    fn = f'{OUT}/{name}.pmtiles'; dst, tx0, ty0 = warp_top(cls)
    with open(fn, 'wb') as f:
        w = Writer(f); n = 0; tiles = {}
        for z in range(ZMAX, ZMIN - 1, -1):
            nty, ntx = dst.shape[0] // 256, dst.shape[1] // 256
            for ty in range(nty):
                for tx in range(ntx):
                    t = dst[ty * 256:(ty + 1) * 256, tx * 256:(tx + 1) * 256]
                    if not t.any(): continue
                    buf = io.BytesIO(); Image.fromarray(RAMP[t], 'RGBA').save(buf, 'PNG', optimize=True)
                    tiles[(z, tx0 + tx, ty0 + ty)] = buf.getvalue(); n += 1
            if z > ZMIN:
                h2, w2 = dst.shape[0] // 2, dst.shape[1] // 2
                dst = dst[:h2 * 2, :w2 * 2].reshape(h2, 2, w2, 2).max(axis=(1, 3)); tx0 //= 2; ty0 //= 2
        for (z, tx, ty) in sorted(tiles, key=lambda k: zxy_to_tileid(*k)):     # PMTiles wants tiles in id order
            w.write_tile(zxy_to_tileid(z, tx, ty), tiles[(z, tx, ty)])
        w.finalize({'tile_type': TileType.PNG, 'tile_compression': Compression.NONE, 'min_zoom': ZMIN, 'max_zoom': ZMAX,
                    'min_lon_e7': int(W * 1e7), 'min_lat_e7': int(S * 1e7), 'max_lon_e7': int(E * 1e7), 'max_lat_e7': int(N * 1e7), 'center_zoom': 9, 'center_lon_e7': int((W + E) / 2 * 1e7), 'center_lat_e7': int((S + N) / 2 * 1e7)}, {'name': name})
    return fn, n
t0 = time.time(); ops = []
frames = [f'f{k:03d}' for k in range(len(meta['frames']))]
for i, name in enumerate(frames):
    if f'{RUN_DIR}/tiles/{name}.pmtiles' in have: continue
    cls = np.asarray(Image.open(hf_hub_download(REPO, f'{RUN_DIR}/{name}.png', repo_type='dataset', token=TOK)))
    fn, n = pack(name, cls); ops.append(CommitOperationAdd(path_in_repo=f'{RUN_DIR}/tiles/{name}.pmtiles', path_or_fileobj=fn))
    log(f'{name}: {n} tiles, {os.path.getsize(fn) // 1024} KB | {time.time() - t0:.0f}s')
    if len(ops) >= 10 or i == len(frames) - 1:
        for k in range(5):
            try: api.create_commit(REPO, repo_type='dataset', operations=ops, commit_message=f'{RUN_DIR} tiles up to {name}'); break
            except Exception as e: log('  retry', k, repr(e)[:120]); time.sleep(10 + 20 * k)
        for o in ops: os.remove(o.path_or_fileobj)
        ops = []
if ops:
    api.create_commit(REPO, repo_type='dataset', operations=ops, commit_message=f'{RUN_DIR} tiles (last)')
meta['tiles'] = dict(zmin=ZMIN, zmax=ZMAX, bounds=[W, S, E, N], format='pmtiles per frame')
json.dump(meta, open('/content/meta_tiles.json', 'w'))
api.upload_file(path_or_fileobj='/content/meta_tiles.json', path_in_repo=f'{RUN_DIR}/meta.json', repo_id=REPO, repo_type='dataset')
log('ALL DONE')
