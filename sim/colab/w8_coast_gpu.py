"""Coastal flood run on the GPU at 10 m: the sea, held at the observed tide-gauge water level, flows over the land.

    TILE=boston STORM=jan2018 RES=10 python w8_coast_gpu.py        (env: TILE, STORM, RES, SEA_RISE metres, DEVICE)
    TILE=all ...                                                     runs every tile in turn

Sea cells (open water connected to the edge of the box, from the hydro-flattened 3DEP elevation) are held at the NOAA CO-OPS
water level (NAVD88) of the tile's gauge, every 6 minutes; the land is dry at the start except where the starting tide reaches.
Frames are the same uint8 depth-class images the rain runs write (sea cells 0), so w5_tiles.py turns them into map tiles.
Outputs on Hugging Face under runs/coast_<TILE>_<STORM>[_slr<cm>]_<RES>m/.
"""
import os, io, json, time, math, sys, urllib.request, subprocess
for mod, pkg in (('pyproj', 'pyproj'), ('huggingface_hub', 'huggingface_hub'), ('PIL', 'pillow'), ('scipy', 'scipy'), ('pandas', 'pandas')):
    try: __import__(mod)
    except ImportError: subprocess.run([sys.executable, '-m', 'pip', 'install', '-q', pkg], check=False)
import numpy as np, requests, pandas as pd
from scipy import ndimage
from pyproj import Transformer
TILE = os.environ.get('TILE', 'boston'); STORM = os.environ.get('STORM', 'jan2018'); RES = float(os.environ.get('RES', '10'))
SEA_RISE = float(os.environ.get('SEA_RISE', '0')); DEV = os.environ.get('DEVICE', 'gpu')
# tiles (lon/lat boxes) and the gauge that drives each one
TILES = {'northshore': ((-71.05, 42.40, -70.60, 42.90), '8443970'), 'boston': ((-71.12, 42.25, -70.85, 42.45), '8443970'),
         'southshore': ((-70.95, 42.02, -70.60, 42.30), '8443970'), 'plymouth': ((-70.75, 41.73, -70.45, 42.07), '8443970'),
         'ccbay': ((-70.45, 41.66, -70.08, 41.86), '8443970'), 'outer': ((-70.12, 41.62, -69.92, 42.08), '8447435'),
         'southcape': ((-70.65, 41.52, -70.00, 41.70), '8447930'), 'buzzards': ((-71.00, 41.50, -70.60, 41.80), '8447930'),
         'fallriver': ((-71.25, 41.62, -71.00, 41.80), '8447386'), 'vineyard': ((-70.85, 41.30, -70.43, 41.50), '8447930'),
         'nantucket': ((-70.25, 41.23, -69.95, 41.40), '8447930')}
STORMS = {'jan2018': dict(t0='2018-01-04T02:00Z', hours=30, frame_min=15, title="Jan 4, 2018 nor'easter"),
          'mar2018': dict(t0='2018-03-02T06:00Z', hours=36, frame_min=15, title="Mar 2-3, 2018 nor'easter"),
          'dec2022': dict(t0='2022-12-23T00:00Z', hours=30, frame_min=15, title='Dec 23, 2022 storm tide')}
S = STORMS[STORM]
LOGP = '/content/log_coast.txt'
def log(*a):
    s = time.strftime('%H:%M:%S ') + ' '.join(str(x) for x in a); print(s, flush=True); open(LOGP, 'a').write(s + '\n')
if DEV == 'gpu':
    import cupy as xp; log('GPU:', xp.cuda.runtime.getDeviceProperties(0)['name'].decode())
else: xp = np
urllib.request.urlretrieve('https://raw.githubusercontent.com/Horus331/mass-flood-watch/main/sim/solver.py?x=' + str(int(time.time())), '/content/solver.py'); sys.path.insert(0, '/content'); import solver
from huggingface_hub import HfApi, hf_hub_download, CommitOperationAdd
try:
    from google.colab import userdata; TOK = userdata.get('HF_TOKEN')
except Exception: TOK = os.environ.get('HF_TOKEN')
REPO = 'mohabeldokla/mass-flood-watch-tiles'; api = HfApi(token=TOK)
idx = json.load(open(hf_hub_download(REPO, 'data/dem10/index.json', repo_type='dataset', token=TOK)))
inv = Transformer.from_crs(4326, 26986, always_xy=True)
def get(url, tries=4):
    for k in range(tries):
        try:
            r = requests.get(url, timeout=120)
            if r.status_code == 200: return r
        except Exception: pass
        time.sleep(3 * (k + 1))
    raise RuntimeError('download failed ' + url[:80])
def coops(station, t0, t1):
    url = ('https://api.tidesandcurrents.noaa.gov/api/prod/datagetter' f'?product=water_level&station={station}&begin_date={t0:%Y%m%d %H:%M}&end_date={t1:%Y%m%d %H:%M}'
           '&datum=NAVD&units=metric&time_zone=gmt&format=json&application=mass-flood-watch')
    js = get(url).json()
    if 'data' not in js: raise RuntimeError(str(js)[:200])
    s = pd.Series([float(x['v']) if x['v'] not in ('', None) else np.nan for x in js['data']], index=pd.to_datetime([x['t'] for x in js['data']], utc=True))
    return s.interpolate(limit=10).bfill().ffill()
def mhhw(station):
    js = get(f'https://api.tidesandcurrents.noaa.gov/mdapi/prod/webapi/stations/{station}/datums.json?units=metric').json()
    d = {x['name']: float(x['value']) for x in js['datums'] if x.get('value') not in (None, '')}
    return d['MHHW'] - d['NAVD88'] if 'MHHW' in d and 'NAVD88' in d else 1.4
def load_dem(box, res):
    T = 20000; x0, y0, x1, y1 = box; k = int(round(res / 10))
    nx10, ny10 = int((x1 - x0) / 10), int((y1 - y0) / 10); Z10 = np.full((ny10, nx10), np.nan, np.float32)
    need = [(key, v) for key, v in idx.items() if v['valid'] > 0 and v['x'] < x1 and v['x'] + T > x0 and v['y'] < y1 and v['y'] + T > y0]
    for key, v in need:
        a = np.load(hf_hub_download(REPO, f'data/dem10/{key}.npy', repo_type='dataset', token=TOK))
        c0 = int((v['x'] - x0) / 10); r0 = int((y1 - (v['y'] + T)) / 10)
        rs, cs = max(r0, 0), max(c0, 0); re_, ce = min(r0 + a.shape[0], ny10), min(c0 + a.shape[1], nx10)
        Z10[rs:re_, cs:ce] = a[rs - r0:re_ - r0, cs - c0:ce - c0]
    if k == 1: return Z10
    ny, nx = ny10 // k, nx10 // k
    return np.nanmean(Z10[:ny * k, :nx * k].reshape(ny, k, nx, k), axis=(1, 3)).astype(np.float32)
def run_tile(tile):
    (W, Sb, E, N), st = TILES[tile]
    xs, ys = inv.transform([W, E, W, E], [Sb, Sb, N, N]); x0, x1 = math.floor(min(xs) / 100) * 100, math.ceil(max(xs) / 100) * 100; y0, y1 = math.floor(min(ys) / 100) * 100, math.ceil(max(ys) / 100) * 100
    BOX = (x0, y0, x1, y1); name = f'coast_{tile}_{STORM}' + (f'_slr{int(SEA_RISE * 100)}' if SEA_RISE else '') + f'_{RES:.0f}m'
    OUT = f'/content/run_{name}'; os.makedirs(OUT, exist_ok=True)
    Z = load_dem(BOX, RES); ny, nx = Z.shape
    log(f'{name}: {ny} x {nx} = {ny * nx / 1e6:.1f} M cells at {RES:.0f} m')
    nod = np.isnan(Z); lowsea = nod | (Z < -1.0) | (np.abs(Z) < 0.005)
    lab, nl = ndimage.label(lowsea); edge = np.unique(np.r_[lab[0], lab[-1], lab[:, 0], lab[:, -1]]); edge = edge[edge > 0]; sea = np.isin(lab, edge); del lab
    Z = np.where(nod, -5.0, Z).astype(np.float32); Z = np.where(~sea & (Z < -1.0), -1.0, Z).astype(np.float32)
    t0 = pd.Timestamp(S['t0']); lvl = coops(st, t0 - pd.Timedelta(hours=1), t0 + pd.Timedelta(hours=S['hours'] + 1)) + SEA_RISE
    MH = mhhw(st); land = (~sea) & (Z > MH)
    log(f'  sea {sea.mean() * 100:.1f}% of cells; gauge {st} peak {lvl.max():.2f} m NAVD88 at {lvl.idxmax():%m-%d %H:%M}Z; MHHW {MH:.2f} m' + (f'; sea raised {SEA_RISE} m' if SEA_RISE else ''))
    lt = (lvl.index - lvl.index[0]).total_seconds().values; lv = lvl.values.astype(np.float64)
    lvl_t = lambda ts: float(np.interp((ts - lvl.index[0]).total_seconds(), lt, lv))
    sim = solver.LocalInertial(Z, RES, 0.035, fixed=sea, xp=xp); landg = xp.asarray(land)
    nfr = int(S['hours'] * 60 / S['frame_min']) + 1; frame_t = [t0 + pd.Timedelta(minutes=S['frame_min'] * i) for i in range(nfr)]
    from PIL import Image
    meta = dict(run=name, title=f"{S['title']} · {tile}", kind='coastal', res_m=RES, box=BOX, crs='EPSG:26986', shape=[ny, nx], t0=S['t0'], frame_min=S['frame_min'], frames=[],
                station=st, sea_rise_m=SEA_RISE, mhhw_navd_m=round(MH, 2), peak_navd_m=round(float(lvl.max()), 2), peak_utc=str(lvl.idxmax()))
    t = t0; kf = 0; steps = 0; tstart = time.time()
    while kf < nfr:
        if t >= frame_t[kf]:
            hc = xp.where(landg, sim.h, 0); hc = xp.asnumpy(hc) if hasattr(xp, 'asnumpy') else hc
            cls = np.zeros(hc.shape, np.uint8)
            for i, th in enumerate((0.05, 0.10, 0.30, 1.0, 2.5)): cls[hc >= th] = i + 1
            Image.fromarray(cls, 'L').save(f'{OUT}/f{kf:03d}.png', optimize=True)
            wet = float((hc >= 0.1).sum() * RES * RES / 1e6); deep = float((hc >= 0.5).sum() * RES * RES / 1e6)
            meta['frames'].append(dict(t=frame_t[kf].strftime('%Y-%m-%dT%H:%MZ'), wet_km2=round(wet, 2), deep_km2=round(deep, 2), level_m=round(lvl_t(frame_t[kf]), 2)))
            log(f'  frame {kf}/{nfr - 1} {frame_t[kf]:%m-%d %H:%M}Z level {lvl_t(frame_t[kf]):.2f} m wet {wet:.1f} km2 | {steps} steps | {time.time() - tstart:.0f}s'); kf += 1
            if kf >= nfr: break
        rem = (frame_t[kf] - t).total_seconds()
        if rem < 0.5: t = frame_t[kf]; continue
        dt = round(min(sim.stable_dt(cap=5.0), rem), 3)
        sim.step(dt, level=lvl_t(t)); t = t + pd.Timedelta(seconds=dt); steps += 1
    hm = xp.where(landg, sim.hmax, 0); hm = xp.asnumpy(hm) if hasattr(xp, 'asnumpy') else hm
    np.save(f'{OUT}/hmax.npy', hm.astype(np.float16))
    meta.update(steps=steps, runtime_s=round(time.time() - tstart), peak_wet_km2=round(float((hm >= 0.1).sum() * RES * RES / 1e6), 2))
    json.dump(meta, open(f'{OUT}/meta.json', 'w'))
    files = sorted(os.listdir(OUT)); rem_dir = f'runs/{name}'
    for i in range(0, len(files), 25):
        ops = [CommitOperationAdd(path_in_repo=f'{rem_dir}/{f}', path_or_fileobj=f'{OUT}/{f}') for f in files[i:i + 25]]
        for k_ in range(5):
            try: api.create_commit(REPO, repo_type='dataset', operations=ops, commit_message=f'{rem_dir} {i + 1}-{i + len(ops)}'); break
            except Exception as e: log('  retry', k_, repr(e)[:120]); time.sleep(10 + 20 * k_)
    log(f'  uploaded {rem_dir}: peak wet {meta["peak_wet_km2"]} km2, {steps} steps, {meta["runtime_s"]} s')
    del sim, landg
    if hasattr(xp, 'get_default_memory_pool'): xp.get_default_memory_pool().free_all_blocks()
for tile in (list(TILES) if TILE == 'all' else TILE.split(',')):
    try: run_tile(tile)
    except Exception as e: log('TILE FAILED', tile, repr(e)[:200])
log('ALL DONE')
