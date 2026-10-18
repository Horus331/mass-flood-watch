"""Week plan, day 2-3: statewide rain-flood run on the GPU, from the 10 m foundation data on Hugging Face.

    RUN=dec2023 RES=30 python w4_flood_gpu.py          (env: RUN, RES metres, BOX 'x0,y0,x1,y1' in EPSG:26986, DEVICE cpu|gpu)

Inputs (all public):  10 m 3DEP elevation tiles (HF data/dem10), MRMS hourly radar rain, NLCD 2021 impervious surface.
Model:  2-D local-inertial shallow water (sim/solver.py) on an EPSG:26986 grid, Horton infiltration scaled by paved
        fraction, storm-drain sink on paved cells, sea cells as a sink.  Same physics as the site's scenes, one connected
        domain, so rivers collect water across the whole area.
Outputs on Hugging Face under runs/<RUN>_<RES>m/:  meta.json, frames f000.png.. (uint8 depth class, full grid),
        hmax.npy (float16 peak depth), roads.json (first/last/peak for District 3 segments when within the box).
"""
import os, io, json, time, math, gzip, sys, urllib.request
import numpy as np, requests
RUN = os.environ.get('RUN', 'dec2023'); RES = float(os.environ.get('RES', '30')); DEV = os.environ.get('DEVICE', 'gpu')
BOX = tuple(float(v) for v in os.environ.get('BOX', '120000,780000,340000,960000').split(','))      # Districts 3-6 (EPSG:26986)
STORMS = {'dec2023': dict(t0='2023-12-17T22:00Z', hours=48, frame_min=30, wet_start_mm=120.0, title='Dec 18, 2023 statewide rain'),
          'sep2023': dict(t0='2023-09-11T16:00Z', hours=36, frame_min=30, wet_start_mm=0.0, title='Sept 11, 2023 flash floods'),
          'jul2023': dict(t0='2023-07-09T12:00Z', hours=48, frame_min=30, wet_start_mm=60.0, title='July 9-11, 2023 western Mass. rain (105 USGS surveyed marks)'),
          'jan2018': dict(t0='2018-01-04T00:00Z', hours=36, frame_min=30, wet_start_mm=0.0, title='Jan 4, 2018 nor\'easter rain (coast handled separately)'),
          'test_leominster': dict(t0='2023-09-11T17:00Z', hours=12, frame_min=30, wet_start_mm=0.0, title='Leominster test')}
S = STORMS[RUN]
OUT = f'/content/run_{RUN}_{RES:.0f}m'; os.makedirs(OUT, exist_ok=True)
LOGP = '/content/log_flood.txt'
def log(*a):
    s = time.strftime('%H:%M:%S ') + ' '.join(str(x) for x in a); print(s, flush=True); open(LOGP, 'a').write(s + '\n')
# ---- array library ----
if DEV == 'gpu':
    import cupy as xp
    log('GPU:', xp.cuda.runtime.getDeviceProperties(0)['name'].decode(), f"{xp.cuda.Device().mem_info[1] / 2**30:.0f} GB")
else:
    xp = np
urllib.request.urlretrieve('https://raw.githubusercontent.com/Horus331/mass-flood-watch/main/sim/solver.py', '/content/solver.py'); sys.path.insert(0, '/content'); import solver
from huggingface_hub import HfApi, hf_hub_download
try:
    from google.colab import userdata; TOK = userdata.get('HF_TOKEN')
except Exception: TOK = os.environ.get('HF_TOKEN')
REPO = 'mohabeldokla/mass-flood-watch-tiles'; api = HfApi(token=TOK)
# ---- 1. elevation: assemble the box from 10 m tiles, then average to RES ----
idx = json.load(open(hf_hub_download(REPO, 'data/dem10/index.json', repo_type='dataset', token=TOK)))
T = 20000; x0, y0, x1, y1 = BOX; k = int(round(RES / 10)); assert abs(k * 10 - RES) < 1e-6, 'RES must be a multiple of 10 m'
nx10, ny10 = int((x1 - x0) / 10), int((y1 - y0) / 10)
Z10 = np.full((ny10, nx10), np.nan, np.float32)
need = [(key, v) for key, v in idx.items() if v['valid'] > 0 and v['x'] < x1 and v['x'] + T > x0 and v['y'] < y1 and v['y'] + T > y0]
log(f'elevation: {len(need)} tiles of 10 m for a {(x1 - x0) / 1e3:.0f} x {(y1 - y0) / 1e3:.0f} km box')
for key, v in need:
    a = np.load(hf_hub_download(REPO, f'data/dem10/{key}.npy', repo_type='dataset', token=TOK))
    c0 = int((v['x'] - x0) / 10); r0 = int((y1 - (v['y'] + T)) / 10)           # tile rows run north -> south
    rs, cs = max(r0, 0), max(c0, 0); re_, ce = min(r0 + a.shape[0], ny10), min(c0 + a.shape[1], nx10)
    Z10[rs:re_, cs:ce] = a[rs - r0:re_ - r0, cs - c0:ce - c0]
ny, nx = ny10 // k, nx10 // k
Z = np.nanmean(Z10[:ny * k, :nx * k].reshape(ny, k, nx, k), axis=(1, 3)).astype(np.float32); del Z10
sea = np.isnan(Z) | (Z <= 0.3)
Z = np.where(np.isnan(Z), -2.0, Z).astype(np.float32)
log(f'grid {ny} x {nx} = {ny * nx / 1e6:.1f} M cells at {RES:.0f} m; sea/sink {sea.mean() * 100:.1f}%')
# cell centres in lon/lat (for rain and land cover)
from pyproj import Transformer
tr = Transformer.from_crs(26986, 4326, always_xy=True)
xc = x0 + (np.arange(nx) + 0.5) * RES; yc = y1 - (np.arange(ny) + 0.5) * RES
lon_c, _ = tr.transform(xc, np.full(nx, (y0 + y1) / 2)); _, lat_c = tr.transform(np.full(ny, (x0 + x1) / 2), yc)
# ---- 2. NLCD impervious from the 10 m tiles on Hugging Face (data/nlcd10, 0..100 % paved), averaged to RES ----
IMP = np.zeros((ny, nx), np.float32)
try:
    from PIL import Image as _I
    I10 = np.zeros((ny10, nx10), np.float32); got = 0
    for key, v in need:
        try: a = np.asarray(_I.open(hf_hub_download(REPO, f'data/nlcd10/{key}.png', repo_type='dataset', token=TOK))).astype(np.float32)
        except Exception: continue
        c0 = int((v['x'] - x0) / 10); r0 = int((y1 - (v['y'] + T)) / 10)
        rs, cs = max(r0, 0), max(c0, 0); re_, ce = min(r0 + a.shape[0], ny10), min(c0 + a.shape[1], nx10)
        I10[rs:re_, cs:ce] = a[rs - r0:re_ - r0, cs - c0:ce - c0]; got += 1
    IMP = I10[:ny * k, :nx * k].reshape(ny, k, nx, k).mean(axis=(1, 3)).astype(np.float32) / 100; del I10
    log(f'NLCD impervious: {got}/{len(need)} tiles, mean {IMP.mean() * 100:.1f}% paved')
except Exception as e:
    log('NLCD unavailable, no paved-surface data:', repr(e)[:120])
# ---- 3. rain: MRMS hourly, interpolated onto the grid ----
import pandas as pd, pygrib
from scipy.interpolate import RegularGridInterpolator
def mrms_hour(ts):
    d = ts.strftime('%Y%m%d'); f = ts.strftime('%Y%m%d-%H%M%S')
    url = f'https://noaa-mrms-pds.s3.amazonaws.com/CONUS/MultiSensor_QPE_01H_Pass2_00.00/{d}/MRMS_MultiSensor_QPE_01H_Pass2_00.00_{f}.grib2.gz'
    open('/tmp/q.grib2', 'wb').write(gzip.decompress(get(url).content))
    g = pygrib.open('/tmp/q.grib2'); m = g[1]; la, lo = m.latlons(); v = np.ma.filled(m.values, 0).astype(np.float32); g.close(); v[v < 0] = 0
    lat1d = la[:, 0]; lon1d = lo[0, :]; lon1d = np.where(lon1d > 180, lon1d - 360, lon1d)
    i0 = np.searchsorted(-lat1d, -lat_c.max() - 0.05); i1 = np.searchsorted(-lat1d, -lat_c.min() + 0.05) + 1
    j0 = np.searchsorted(lon1d, lon_c.min() - 0.05); j1 = np.searchsorted(lon1d, lon_c.max() + 0.05) + 1
    fi = RegularGridInterpolator((lat1d[i0:i1][::-1], lon1d[j0:j1]), v[i0:i1, j0:j1][::-1], bounds_error=False, fill_value=0)
    LA, LO = np.meshgrid(lat_c, lon_c, indexing='ij'); return fi((LA, LO)).astype(np.float32)
t0 = pd.Timestamp(S['t0']); hours = [t0 + pd.Timedelta(hours=h + 1) for h in range(S['hours'])]
RAIN = {}
for ts in hours:
    try: RAIN[ts] = mrms_hour(ts)
    except Exception as e: log('  no MRMS', ts, repr(e)[:80]); RAIN[ts] = np.zeros((ny, nx), np.float32)
tot = sum(RAIN.values()); log(f'rain: max {tot.max():.0f} mm, mean {tot.mean():.0f} mm over {len(hours)} h')
# ---- 4. the run ----
sim = solver.LocalInertial(Z, RES, 0.06, xp=xp); sim.sink = xp.asarray(sea)
f0, fc, Fk, drain = 30.0, 3.0, 40.0, 2.0
IMPg = xp.asarray(IMP); f_scale = 1.0 - 0.9 * IMPg; drain_mmph = drain + 5.0 * IMPg
Finf = xp.full((ny, nx), S['wet_start_mm'], xp.float32)
nfr = int(S['hours'] * 60 / S['frame_min']) + 1; frame_t = [t0 + pd.Timedelta(minutes=S['frame_min'] * i) for i in range(nfr)]
STOPS = [(0.0, (110, 196, 250, 160)), (0.3, (56, 146, 232, 195)), (1.0, (24, 98, 200, 222)), (2.5, (12, 54, 140, 238)), (5.0, (8, 30, 90, 248))]
from PIL import Image
def save_frame(kf, h):
    hc = xp.asnumpy(h) if hasattr(xp, 'asnumpy') else h
    cls = np.zeros(hc.shape, np.uint8)                       # 0 dry, 1: 5-10 cm, 2: 10-30, 3: 30-100, 4: 1-2.5 m, 5: >2.5 m
    for i, th in enumerate((0.05, 0.10, 0.30, 1.0, 2.5)): cls[hc >= th] = i + 1
    Image.fromarray(cls, 'L').save(f'{OUT}/f{kf:03d}.png', optimize=True)
    return float((hc >= 0.1).sum() * RES * RES / 1e6), float((hc >= 0.5).sum() * RES * RES / 1e6)
meta = dict(run=RUN, title=S['title'], res_m=RES, box=BOX, crs='EPSG:26986', shape=[ny, nx], t0=S['t0'], frame_min=S['frame_min'], frames=[],
            rain_total_max_mm=round(float(tot.max())), rain_total_mean_mm=round(float(tot.mean())), infiltration=dict(f0=f0, fc=fc, Fk=Fk, drain=drain, landcover='NLCD 2021 impervious', wet_start_mm=S['wet_start_mm']))
t = t0; kf = 0; steps = 0; tstart = time.time(); Pcum = xp.zeros((ny, nx), xp.float32)
while kf < nfr:
    if t >= frame_t[kf]:
        wet, deep = save_frame(kf, sim.h)
        meta['frames'].append(dict(t=frame_t[kf].strftime('%Y-%m-%dT%H:%MZ'), wet_km2=round(wet, 1), deep_km2=round(deep, 1), soaked_mm=round(float(Finf.mean() - S['wet_start_mm']), 1)))
        log(f'frame {kf}/{nfr - 1} {frame_t[kf]:%m-%d %H:%M}Z wet {wet:.0f} km2 deep {deep:.0f} km2 | {steps} steps | {time.time() - tstart:.0f}s'); kf += 1
        if kf >= nfr: break
    rem = (frame_t[kf] - t).total_seconds()
    if rem < 0.5: t = frame_t[kf]; continue
    dt = round(min(sim.stable_dt(cap=10.0), rem), 3)
    hr = (t + pd.Timedelta(seconds=1)).ceil('h')
    if hr in RAIN:
        src = xp.asarray(RAIN[hr]) / 3.6e6; sim.step(dt, source=src)
    else:
        sim.step(dt)
    fcap = ((fc + (f0 - fc) * xp.exp(-Finf / Fk)) * f_scale + drain_mmph) / 3.6e6 * dt
    loss = xp.minimum(sim.h, fcap); sim.h -= loss; Finf += loss * 1000.0
    t = t + pd.Timedelta(seconds=dt); steps += 1
    if steps % 2000 == 0: log(f'   step {steps} t {t:%H:%M} dt {dt:.2f}s hmax {float(sim.h.max()):.2f} m | {time.time() - tstart:.0f}s')
hm = xp.asnumpy(sim.hmax) if hasattr(xp, 'asnumpy') else sim.hmax
np.save(f'{OUT}/hmax.npy', hm.astype(np.float16))
meta.update(steps=steps, runtime_s=round(time.time() - tstart), peak_wet_km2=round(float((hm >= 0.1).sum() * RES * RES / 1e6), 1))
json.dump(meta, open(f'{OUT}/meta.json', 'w'))
log('run done:', meta['peak_wet_km2'], 'km2 peak wet,', steps, 'steps,', meta['runtime_s'], 's')
# ---- 5. upload ----
from huggingface_hub import CommitOperationAdd
files = sorted(os.listdir(OUT)); rem_dir = f'runs/{RUN}_{RES:.0f}m'
for i in range(0, len(files), 25):
    ops = [CommitOperationAdd(path_in_repo=f'{rem_dir}/{f}', path_or_fileobj=f'{OUT}/{f}') for f in files[i:i + 25]]
    for k_ in range(5):
        try: api.create_commit(REPO, repo_type='dataset', operations=ops, commit_message=f'{rem_dir} {i + 1}-{i + len(ops)}'); break
        except Exception as e: log('  retry', k_, repr(e)[:120]); time.sleep(10 + 20 * k_)
log('uploaded to', rem_dir, '| ALL DONE')
