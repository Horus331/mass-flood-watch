"""Week plan, day 2-3: statewide rain-flood run on the GPU, from the 10 m foundation data on Hugging Face.

    RUN=dec2023 RES=30 python w4_flood_gpu.py          (env: RUN, RES metres, BOX 'x0,y0,x1,y1' in EPSG:26986, DEVICE cpu|gpu)

Inputs (all public):  10 m 3DEP elevation tiles (HF data/dem10), MRMS hourly radar rain, NLCD 2021 impervious surface.
Model:  2-D local-inertial shallow water (sim/solver.py) on an EPSG:26986 grid, Horton infiltration scaled by paved
        fraction, storm-drain sink on paved cells, sea cells as a sink.  Same physics as the site's scenes, one connected
        domain, so rivers collect water across the whole area.
Outputs on Hugging Face under runs/<RUN>_<RES>m/:  meta.json, frames f000.png.. (uint8 depth class, full grid),
        hmax.npy (float16 peak depth), roads.json (first/last/peak for District 3 segments when within the box).
"""
import os, io, json, time, math, gzip, sys, urllib.request, subprocess
for mod, pkg in (('pygrib', 'pygrib'), ('pyproj', 'pyproj'), ('huggingface_hub', 'huggingface_hub'), ('PIL', 'pillow'), ('scipy', 'scipy'), ('pandas', 'pandas')):
    try: __import__(mod)
    except ImportError: subprocess.run([sys.executable, '-m', 'pip', 'install', '-q', pkg], check=False)
import numpy as np, requests
RUN = os.environ.get('RUN', 'dec2023'); RES = float(os.environ.get('RES', '30')); DEV = os.environ.get('DEVICE', 'gpu')
BOX = tuple(float(v) for v in os.environ.get('BOX', '120000,780000,340000,960000').split(','))      # Districts 3-6 (EPSG:26986)
STORMS = {'dec2023': dict(t0='2023-12-17T22:00Z', hours=48, frame_min=30, wet_start_mm=120.0, title='Dec 18, 2023 statewide rain'),
          'sep2023': dict(t0='2023-09-11T16:00Z', hours=36, frame_min=30, wet_start_mm=0.0, title='Sept 11, 2023 flash floods'),
          'jul2023': dict(t0='2023-07-09T12:00Z', hours=48, frame_min=30, wet_start_mm=60.0, title='July 9-11, 2023 western Mass. rain (105 USGS surveyed marks)', box=(30000, 850000, 170000, 960000)),
          'jan2018': dict(t0='2018-01-04T00:00Z', hours=36, frame_min=30, wet_start_mm=0.0, title='Jan 4, 2018 nor\'easter rain (coast handled separately)'),
          'test_leominster': dict(t0='2023-09-11T17:00Z', hours=12, frame_min=30, wet_start_mm=0.0, title='Leominster test')}
S = STORMS[RUN]
# experiment knobs (validation-driven calibration): WET_START mm overrides the storm's antecedent wetness, FC_SCALE multiplies the
# soil infiltration rates (0.5 = soils drink half as fast), TAG names the variant (runs/<RUN><TAG>_<RES>m)
if os.environ.get('WET_START'): S = dict(S, wet_start_mm=float(os.environ['WET_START']))
FC_SCALE = float(os.environ.get('FC_SCALE', '1')); TAG = os.environ.get('TAG', '')
if 'box' in S and 'BOX' not in os.environ: BOX = tuple(float(v) for v in S['box'])     # storms outside Districts 3-6 carry their own box
OUT = f'/content/run_{RUN}{TAG}_{RES:.0f}m'; os.makedirs(OUT, exist_ok=True)
LOGP = '/content/log_flood.txt'
def log(*a):
    s = time.strftime('%H:%M:%S ') + ' '.join(str(x) for x in a); print(s, flush=True); open(LOGP, 'a').write(s + '\n')
# ---- array library ----
if DEV == 'gpu':
    import cupy as xp
    log('GPU:', xp.cuda.runtime.getDeviceProperties(0)['name'].decode(), f"{xp.cuda.Device().mem_info[1] / 2**30:.0f} GB")
else:
    xp = np
urllib.request.urlretrieve('https://raw.githubusercontent.com/Horus331/mass-flood-watch/' + os.environ.get('GIT_SHA', 'main') + '/sim/solver.py', '/content/solver.py'); sys.path.insert(0, '/content'); import solver
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
from scipy import ndimage
nod = np.isnan(Z); low = nod | (Z <= 0.3)
lab, _ = ndimage.label(low); edge = np.unique(np.r_[lab[0], lab[-1], lab[:, 0], lab[:, -1]]); edge = edge[edge > 0]
sea = np.isin(lab, edge); del lab                                   # only low ground connected to the box edge is sea
inland_void = nod & ~sea
if inland_void.any():                                               # lidar voids over inland water: fill with the surrounding minimum so streams are not swallowed
    fill = ndimage.grey_erosion(np.where(nod, 1e4, Z), size=7); Z = np.where(inland_void, fill, Z)
Z = np.where(np.isnan(Z), -2.0, Z).astype(np.float32)
log(f'sea {sea.mean() * 100:.1f}% of cells (edge-connected), inland voids filled {int(inland_void.sum()):,}')
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
def get(url, tries=4):
    for k in range(tries):
        try:
            r = requests.get(url, timeout=120)
            if r.status_code == 200: return r
        except Exception: pass
        time.sleep(3 * (k + 1))
    raise RuntimeError(f'download failed: {url[-60:]}')
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
if tot.max() <= 0: raise SystemExit('no rain data at all; refusing to run a dry storm')
# rain pictures for the map: one small RGBA image per hour (every 10th cell), corners in lon/lat for a MapLibre image source
from PIL import Image as _Im
RSTOPS = [(1, (170, 220, 255, 90)), (3, (90, 170, 255, 130)), (6, (30, 110, 230, 160)), (12, (255, 200, 60, 190)), (25, (255, 110, 30, 215)), (50, (200, 20, 20, 235))]
rain_hours = []
for ts in hours:
    r_ = RAIN[ts][::10, ::10]; img = np.zeros(r_.shape + (4,), np.uint8)
    for th, col in RSTOPS: img[r_ >= th] = col
    _Im.fromarray(img).save(f'{OUT}/r{ts:%d%H}.png', optimize=True); rain_hours.append([ts.strftime('%Y-%m-%dT%H:%MZ'), f'r{ts:%d%H}.png'])
corn = [tr.transform(x_, y_) for x_, y_ in ((x0, y1), (x1, y1), (x1, y0), (x0, y0))]      # top-left, top-right, bottom-right, bottom-left
RAIN_META = dict(hours=rain_hours, corners=[[round(a, 5), round(b, 5)] for a, b in corn], stops=RSTOPS, unit='mm in the hour ending at the time')

# ---- 3b. rivers entering the box: USGS gauge discharge (plus the tributaries that join above the state line) injected along the channel ----
INFLOW = []                       # (rows, cols, name, times_utc[], m3/s[]) ; cells are refined onto channel cells once the channel grid is loaded (3d)
INFLOW_PT = []                    # (row, col) entry points, kept for the refinement
if os.environ.get('INFLOW', '1') == '1':
    try:
        G = json.load(open(hf_hub_download(REPO, f'data/gauges/gauges_{RUN}.json', repo_type='dataset', token=TOK)))
        ENTRY = {'01154500': (-72.478, 42.727, 'Connecticut River at the NH line (+ West River, Ashuelot)', ['01156000', '01161000']),
                 '01092000': (-71.422, 42.700, 'Merrimack River at the NH line (+ Souhegan)', ['01094000']),
                 '01168500': (None, None, 'Deerfield River at Charlemont (basin mostly in Vermont)', [])}
        inv = Transformer.from_crs(4326, 26986, always_xy=True)
        def series(sid):
            g = G['flow'].get(sid)
            if not g: return None
            ts = [pd.Timestamp(t_).tz_localize('America/New_York', ambiguous='NaT', nonexistent='shift_forward').tz_convert('UTC').tz_localize(None) for t_, _ in g['values']]
            keep = [i_ for i_, t_ in enumerate(ts) if not pd.isna(t_)]
            return np.array([ts[i_].value / 1e9 for i_ in keep]), np.array([float(g['values'][i_][1]) * 0.0283168 for i_ in keep], np.float32), g
        for sid, (lon, lat, name, plus) in ENTRY.items():
            sr = series(sid)
            if sr is None: continue
            tq, qq, g = sr
            for sid2 in plus:
                s2 = series(sid2)
                if s2 is not None: qq = qq + np.interp(tq, s2[0], s2[1]).astype(np.float32)
            if lon is None: lon, lat = float(g['lon']), float(g['lat'])
            xg, yg = inv.transform(lon, lat); c = int((xg - x0) / RES); r = int((y1 - yg) / RES)
            if not (0 <= r < ny and 0 <= c < nx): continue
            w = int(600 / RES); r0_, r1_, c0_, c1_ = max(2, r - w), min(ny - 2, r + w + 1), max(2, c - w), min(nx - 2, c + w + 1)
            win = np.where(sea[r0_:r1_, c0_:c1_], np.inf, Z[r0_:r1_, c0_:c1_])
            flat = np.argsort(win, axis=None)[:12]; kk = np.unravel_index(flat, win.shape)
            rr, cc = (r0_ + kk[0]).astype(np.int64), (c0_ + kk[1]).astype(np.int64)
            q_base = float(np.interp(pd.Timestamp(S['t0']).value / 1e9, tq, qq))
            INFLOW.append([rr, cc, name, tq, qq, q_base]); INFLOW_PT.append((r, c))
            log(f'inflow: {name}: peak {qq.max():.0f} m3/s, {q_base:.0f} m3/s at the start, entry cell ({r},{c})')
    except Exception as e:
        log('no gauge inflows:', repr(e)[:120])
# ---- 3c. road segments (the site's 52,698 segments) sampled every frame -> roads_cm.npy (uint8 depth in cm per segment per frame) ----
ROAD = None
try:
    SEGJ = json.loads(get('https://raw.githubusercontent.com/Horus331/mass-flood-watch/main/docs/graph_segments.json').content)
    inv2 = Transformer.from_crs(4326, 26986, always_xy=True); px, py, pid = [], [], []
    for i_, parts in enumerate(SEGJ['geo']):
        for d_ in parts:
            x_ = np.cumsum(d_[0::2]) / 1e5; y_ = np.cumsum(d_[1::2]) / 1e5
            px.append(x_); py.append(y_); pid.append(np.full(len(x_), i_, np.int32))
    px, py, pid = np.concatenate(px), np.concatenate(py), np.concatenate(pid)
    X_, Y_ = inv2.transform(px, py); cc_ = ((X_ - x0) / RES).astype(np.int64); rr_ = ((y1 - Y_) / RES).astype(np.int64)
    ok_ = (rr_ >= 0) & (rr_ < ny) & (cc_ >= 0) & (cc_ < nx)
    ROAD = dict(n=SEGJ['n'], r=xp.asarray(rr_[ok_]), c=xp.asarray(cc_[ok_]), seg=xp.asarray(pid[ok_]), inbox=np.unique(pid[ok_]))
    nfr_ = int((S['hours'] * 60 / S['frame_min']) + 1); ROAD['cm'] = np.zeros((nfr_, SEGJ['n']), np.uint8); ROAD['mean_cm'] = np.zeros((nfr_, SEGJ['n']), np.uint8); ROAD['v'] = np.zeros((nfr_, SEGJ['n']), np.uint8)
    ROAD['cnt'] = np.bincount(pid[ok_], minlength=SEGJ['n']).astype(np.float32)
    log(f'roads: {len(ROAD["inbox"])} of {SEGJ["n"]} segments inside the box ({int(ok_.sum())} vertices)'); del SEGJ, px, py, pid, X_, Y_
except Exception as e:
    log('no road sampling:', repr(e)[:120])
def road_sample_v(kf, vel, h):
    if ROAD is None: return
    d_ = h[ROAD['r'], ROAD['c']]; v_ = vel[ROAD['r'], ROAD['c']]
    sm = xp.zeros(ROAD['n'], xp.float32); mv = xp.zeros(ROAD['n'], xp.float32)
    if xp is np: np.add.at(sm, ROAD['seg'], d_); np.maximum.at(mv, ROAD['seg'], v_)
    else:
        import cupyx; cupyx.scatter_add(sm, ROAD['seg'], d_); cupyx.scatter_max(mv, ROAD['seg'], v_)
    sm = (xp.asnumpy(sm) if hasattr(xp, 'asnumpy') else sm) / np.maximum(ROAD['cnt'], 1); mv = xp.asnumpy(mv) if hasattr(xp, 'asnumpy') else mv
    ROAD['mean_cm'][kf] = np.clip(np.round(sm * 100), 0, 255).astype(np.uint8); ROAD['v'][kf] = np.clip(np.round(mv / 0.05), 0, 255).astype(np.uint8)
def road_sample(kf, h):
    if ROAD is None: return
    d_ = h[ROAD['r'], ROAD['c']]; m_ = xp.zeros(ROAD['n'], xp.float32)
    if xp is np: np.maximum.at(m_, ROAD['seg'], d_)
    else:
        import cupyx; cupyx.scatter_max(m_, ROAD['seg'], d_)
    m_ = xp.asnumpy(m_) if hasattr(xp, 'asnumpy') else m_
    ROAD['cm'][kf] = np.clip(np.round(m_ * 100), 0, 255).astype(np.uint8)
# ---- 3d. grids from Hugging Face resampled to this box: soils (SSURGO) and channels (NHDPlus HR) ----
def hf_grid(name, meta_name, fields):
    """Load a whole-state 30 m grid (npz) and cut/resample it (nearest) to this run's box; raises if the box is not covered."""
    D = np.load(hf_hub_download(REPO, f'data/{name}', repo_type='dataset', token=TOK)); M = json.load(open(hf_hub_download(REPO, f'data/{meta_name}', repo_type='dataset', token=TOK)))
    sx0, sy0, sx1, sy1 = M['box']; sres = M['res_m']
    if not (x0 >= sx0 - 1 and y0 >= sy0 - 1 and x1 <= sx1 + 1 and y1 <= sy1 + 1): raise RuntimeError(f'{name}: run box outside the grid; rerun its GitHub job for this area')
    rr_ = np.clip(((sy1 - (y1 - (np.arange(ny) + 0.5) * RES)) / sres).astype(int), 0, M['shape'][0] - 1)
    cc_ = np.clip(((x0 + (np.arange(nx) + 0.5) * RES - sx0) / sres).astype(int), 0, M['shape'][1] - 1)
    return {f: D[f][rr_][:, cc_] for f in fields}
PHYS = int(os.environ.get('PHYS', '2'))          # 2 = water balance fixed (Oct 18 review): no losses on water, storage-limited infiltration, channels, tide; 1 = the Oct 17 physics
f0, fc, Fk = 30.0, 3.0, 40.0
SOIL_META = 'none (uniform f0 30, fc 3 mm/h)'; CH = None; water = sea.copy(); grp = np.zeros((ny, nx), np.int64); Scap = np.full((ny, nx), 120.0, np.float32)
if os.environ.get('SOILS', '1') == '1':
    try:
        SO = hf_grid('soils30/soils30.npz', 'soils30/soils30_meta.json', ['hydgrp', 'wtd', 'aws', 'brock'] )
        hg, wt = SO['hydgrp'], SO['wtd']
        grp = np.where(hg >= 5, 4, hg).astype(np.int64); grp[(wt < 25) & (grp > 0)] = 4          # dual groups and shallow water table -> D
        # soil water storage before saturation-excess runoff starts (mm): available water in the top metre, cut by a shallow water table or bedrock
        aws = SO['aws'].astype(np.float32) * 10.0; aws = np.where(aws > 0, aws, 120.0)          # SSURGO aws0100wta is in cm -> mm
        dlim = np.minimum(np.where(wt < 255, wt * 2.0, 200.0), np.where(SO['brock'] < 255, SO['brock'] * 2.0, 200.0))     # cm
        Scap = np.maximum(aws * np.clip(dlim / 100.0, 0.1, 1.0), 20.0).astype(np.float32)
        SOIL_META = f'SSURGO hydrologic group on {float((grp > 0).mean()) * 100:.0f}% of cells (A {float((grp == 1).mean()) * 100:.0f}%, B {float((grp == 2).mean()) * 100:.0f}%, C {float((grp == 3).mean()) * 100:.0f}%, D {float((grp == 4).mean()) * 100:.0f}%); storage cap mean {float(Scap[grp > 0].mean()):.0f} mm'
        log('soils:', SOIL_META); del hg, wt, SO, aws, dlim
    except Exception as e:
        if PHYS >= 2: raise SystemExit(f'soils grid missing for this box: {e!r}')
        log('no soils data, uniform infiltration:', repr(e)[:120])
F0 = np.array([f0, 250, 200, 125, 75], np.float32)[grp]; FC = np.array([fc, 25.4, 12.7, 6.4, 2.5], np.float32)[grp]
KDEEP = np.array([1.0, 5.0, 2.5, 1.0, 0.5], np.float32)[grp]            # mm/h once the soil store is full (deep drainage through dense till / bedrock)
if PHYS >= 2:
    try:
        CH = hf_grid('channels30/channels30.npz', 'channels30/channels30_meta.json', ['chan', 'water', 'area', 'width', 'depth'])
        water |= CH['water'].astype(bool)
        chan = CH['chan'].astype(bool) & ~sea
        SUBGRID = os.environ.get('SUBGRID', '1') == '1'
        CW = np.where(chan, CH['width'].astype(np.float32), 0).astype(np.float32); CD = np.where(chan, CH['depth'].astype(np.float32), 0).astype(np.float32)
        if SUBGRID:
            burn = CD                                                                                              # full bankfull depth; the solver keeps the channel's own width below bank
            wide = CH['water'].astype(bool) & ~chan & ~sea                                                         # rivers wider than a cell: the buffered body is cut to the channel depth too
            if wide.any():
                CDd = ndimage.grey_dilation(CD, size=(7, 7)); burn = np.where(wide, CDd, burn).astype(np.float32)
                CW = np.where(wide, RES, CW).astype(np.float32); CD = np.where(wide, CDd, CD).astype(np.float32); chan = chan | wide
                log(f'   wide rivers: {int(wide.sum()):,} extra body cells cut to channel depth')
        else: burn = (CD * np.minimum(CW / RES, 1.0))                                                              # volume-equivalent channel depth below the cell mean
        Z = np.where(chan, Z - burn, Z).astype(np.float32)
        log(f'channels: {int(chan.sum()):,} channel cells burnt (mean {float(burn[chan].mean()):.2f} m, {"sub-grid widths" if SUBGRID else "volume-equivalent"}), open water {float(water.mean()) * 100:.1f}% of cells')
        for k_, (r, c) in enumerate(INFLOW_PT):                      # spread each inflow along the main channel near its entry point
            w = int(3000 / RES); r0_, r1_, c0_, c1_ = max(2, r - w), min(ny - 2, r + w + 1), max(2, c - w), min(nx - 2, c + w + 1)
            sub = np.where(chan[r0_:r1_, c0_:c1_] & ~sea[r0_:r1_, c0_:c1_], CH['area'][r0_:r1_, c0_:c1_], 0)
            if (sub > 0).sum() >= 10:
                flat = np.argsort(sub, axis=None)[::-1][:80]; flat = flat[sub.ravel()[flat] >= 0.5 * sub.max()]; kk = np.unravel_index(flat, sub.shape)
                INFLOW[k_][0] = (r0_ + kk[0]).astype(np.int64); INFLOW[k_][1] = (c0_ + kk[1]).astype(np.int64)
                log(f'   {INFLOW[k_][2]}: injected over {len(flat)} channel cells (drainage area {sub.max():.0f} km2)')
    except Exception as e:
        log('no channel grid, rivers unburnt:', repr(e)[:120]); chan = np.zeros((ny, nx), bool); burn = np.zeros((ny, nx), np.float32); SUBGRID = False
else:
    chan = np.zeros((ny, nx), bool); burn = np.zeros((ny, nx), np.float32); SUBGRID = False
# Manning n: channels and open water 0.035, dense urban 0.10, everything else 0.08 (forest/field/suburban mix) until NLCD classes are wired in
IMPg_np = IMP
N_MAP = np.where(water | chan, 0.035, np.where(IMPg_np > 0.3, 0.10, 0.08)).astype(np.float32) if PHYS >= 2 else np.full((ny, nx), 0.06, np.float32)
# ---- 3e. tide: sea cells held at the observed water level (compound rain + tide flooding) instead of a sink ----
TIDE = None
if PHYS >= 2 and os.environ.get('TIDE', '1') == '1' and sea.any():
    try:
        st_ = os.environ.get('TIDE_STATION', '8443970')
        url = ('https://api.tidesandcurrents.noaa.gov/api/prod/datagetter' f'?product=water_level&station={st_}&begin_date={(pd.Timestamp(S["t0"]) - pd.Timedelta(hours=2)):%Y%m%d %H:%M}&end_date={(pd.Timestamp(S["t0"]) + pd.Timedelta(hours=S["hours"] + 2)):%Y%m%d %H:%M}'
               '&datum=NAVD&units=metric&time_zone=gmt&format=json&application=mass-flood-watch')
        js = get(url).json(); ser = pd.Series([float(x['v']) if x['v'] not in ('', None) else np.nan for x in js['data']], index=pd.to_datetime([x['t'] for x in js['data']], utc=True)).interpolate(limit=10).bfill().ffill()
        TIDE = (ser.index.view('int64') / 1e9, ser.values.astype(np.float64)); log(f'tide: gauge {st_} {ser.min():.2f}..{ser.max():.2f} m NAVD88 over the run')
    except Exception as e:
        log('no tide series, sea stays a sink:', repr(e)[:120])
# ---- 4. the run ----
if TIDE is not None:
    sim = solver.LocalInertial(Z, RES, N_MAP, fixed=sea, xp=xp, theta=0.7 if PHYS >= 2 else 1.0, fr_max=2.0 if PHYS >= 2 else 1.0)
    border = np.zeros((ny, nx), bool); border[[0, -1], :] = True; border[:, [0, -1]] = True; sim.sink = xp.asarray(border & ~sea)   # open land edges still drain out
else:
    sim = solver.LocalInertial(Z, RES, N_MAP, xp=xp, theta=0.7 if PHYS >= 2 else 1.0, fr_max=2.0 if PHYS >= 2 else 1.0); sim.sink = xp.asarray(sea)
if PHYS >= 2 and chan.any():
    if SUBGRID: sim.set_channels(CW, CD)                                 # sub-grid channel storage and conveyance (Neal et al. 2012, simplified)
    sim.h += xp.asarray(np.where(chan, 0.3 * burn, 0).astype(np.float32))   # baseflow: channels start a third full
INFLOW = [(xp.asarray(rr_), xp.asarray(cc_), n_, tq_, qq_, qb_) for rr_, cc_, n_, tq_, qq_, qb_ in INFLOW]
f0g, fcg, Kdg, Scapg = xp.asarray(F0), xp.asarray(FC), xp.asarray(KDEEP), xp.asarray(Scap); del F0, FC, KDEEP
IMPg = xp.asarray(IMP); f_scale = (1.0 - 0.9 * IMPg) * FC_SCALE
drain_mmph = xp.where(IMPg > 0.05, 7.0 * IMPg, 0.0) if PHYS >= 2 else 2.0 + 5.0 * IMPg      # storm drains exist only where there is pavement
WATERg = xp.asarray(water | sea)                                                              # no infiltration or drains from rivers, lakes and the sea
# antecedent soil water: 14-day MRMS rain before the storm minus 3 mm/day evapotranspiration (replaces the hand-set wet_start)
Finf0 = None
if PHYS >= 2 and not os.environ.get('WET_START'):
    try:
        api_mm = np.zeros((ny, nx), np.float32); got_d = 0
        for dd in range(1, 15):
            ts_ = (pd.Timestamp(S['t0']).floor('D') - pd.Timedelta(days=dd - 1))
            u = f'https://noaa-mrms-pds.s3.amazonaws.com/CONUS/MultiSensor_QPE_24H_Pass2_00.00/{ts_:%Y%m%d}/MRMS_MultiSensor_QPE_24H_Pass2_00.00_{ts_:%Y%m%d}-000000.grib2.gz'
            try:
                open('/tmp/q.grib2', 'wb').write(gzip.decompress(get(u, tries=2).content)); g = pygrib.open('/tmp/q.grib2'); m = g[1]; v = np.ma.filled(m.values, 0).astype(np.float32); g.close(); v[v < 0] = 0
                la, lo = m.latlons(); lat1d = la[:, 0]; lon1d = np.where(lo[0, :] > 180, lo[0, :] - 360, lo[0, :])
                i0 = np.searchsorted(-lat1d, -lat_c.max() - 0.05); i1 = np.searchsorted(-lat1d, -lat_c.min() + 0.05) + 1; j0 = np.searchsorted(lon1d, lon_c.min() - 0.05); j1 = np.searchsorted(lon1d, lon_c.max() + 0.05) + 1
                fi = RegularGridInterpolator((lat1d[i0:i1][::-1], lon1d[j0:j1]), v[i0:i1, j0:j1][::-1], bounds_error=False, fill_value=0)
                LA, LO = np.meshgrid(lat_c, lon_c, indexing='ij'); api_mm += fi((LA, LO)).astype(np.float32); got_d += 1
            except Exception: pass
        api_mm = np.maximum(api_mm - 3.0 * 14, 0)
        Finf0 = np.clip(0.6 * api_mm, 0, 0.9 * Scap).astype(np.float32)
        log(f'antecedent: {got_d}/14 days of MRMS, 14-day rain mean {float((api_mm + 42).mean()):.0f} mm -> soil store starts {float(Finf0.mean()):.0f} mm full of {float(Scap.mean()):.0f}')
    except Exception as e:
        log('antecedent rain unavailable, using the storm default:', repr(e)[:120])
if Finf0 is None: Finf0 = np.full((ny, nx), S['wet_start_mm'], np.float32)
if FC_SCALE != 1 or os.environ.get('WET_START'): log(f'experiment: FC_SCALE {FC_SCALE}, wet_start {S["wet_start_mm"]} mm, tag {TAG!r}')
Finf = xp.asarray(Finf0); WET0 = float(Finf0.mean()); del Finf0
# per-cell outputs for the surrogate and the road layers: arrival frame, hours wet, peak speed, peak h*v
T_FIRST = xp.full((ny, nx), 255, xp.uint8); DUR = xp.zeros((ny, nx), xp.uint8); VMAX = xp.zeros((ny, nx), xp.float32); HVMAX = xp.zeros((ny, nx), xp.float32)
nfr = int(S['hours'] * 60 / S['frame_min']) + 1; frame_t = [t0 + pd.Timedelta(minutes=S['frame_min'] * i) for i in range(nfr)]
STOPS = [(0.0, (110, 196, 250, 160)), (0.3, (56, 146, 232, 195)), (1.0, (24, 98, 200, 222)), (2.5, (12, 54, 140, 238)), (5.0, (8, 30, 90, 248))]
from PIL import Image
def save_frame(kf, h):
    if TIDE is not None: h = xp.where(sim.fixed, 0, h)
    hc = xp.asnumpy(h) if hasattr(xp, 'asnumpy') else h
    cls = np.zeros(hc.shape, np.uint8)                       # 0 dry, 1: 5-10 cm, 2: 10-30, 3: 30-100, 4: 1-2.5 m, 5: >2.5 m
    for i, th in enumerate((0.05, 0.10, 0.30, 1.0, 2.5)): cls[hc >= th] = i + 1
    Image.fromarray(cls, 'L').save(f'{OUT}/f{kf:03d}.png', optimize=True)
    return float(((hc >= 0.1) & ~chan).sum() * RES * RES / 1e6), float(((hc >= 0.5) & ~chan).sum() * RES * RES / 1e6)     # land only: river channels are wet by definition
meta = dict(run=RUN + TAG, title=S['title'] + (f' · variant {TAG}' if TAG else ''), experiment=dict(fc_scale=FC_SCALE, wet_start_mm=S['wet_start_mm']), res_m=RES, box=BOX, crs='EPSG:26986', shape=[ny, nx], t0=S['t0'], frame_min=S['frame_min'], frames=[],
            rain_total_max_mm=round(float(tot.max())), rain_total_mean_mm=round(float(tot.mean())), rain=RAIN_META, infiltration=dict(soils=SOIL_META, Fk=Fk, drain='7 mm/h x paved fraction on paved cells' if PHYS >= 2 else '2 + 5 x paved mm/h everywhere', landcover='NLCD 2021 impervious', wet_start_mm=S['wet_start_mm']))
t = t0; kf = 0; steps = 0; tstart = time.time(); src_hr = None; src = None
while kf < nfr:
    if t >= frame_t[kf]:
        wet, deep = save_frame(kf, sim.h); road_sample(kf, sim.h)
        if TIDE is not None: hl = xp.where(sim.fixed, 0, sim.h)
        else: hl = sim.h
        wetm = hl >= 0.1; T_FIRST = xp.where(wetm & (T_FIRST == 255), kf, T_FIRST).astype(xp.uint8); DUR += wetm.astype(xp.uint8)
        vel = sim.velocity(); VMAX = xp.maximum(VMAX, vel); HVMAX = xp.maximum(HVMAX, vel * hl); road_sample_v(kf, vel, hl)
        meta['frames'].append(dict(t=frame_t[kf].strftime('%Y-%m-%dT%H:%MZ'), wet_km2=round(wet, 1), deep_km2=round(deep, 1), soaked_mm=round(float(Finf.mean()) - WET0, 1)))
        log(f'frame {kf}/{nfr - 1} {frame_t[kf]:%m-%d %H:%M}Z wet {wet:.0f} km2 deep {deep:.0f} km2 | {steps} steps | {time.time() - tstart:.0f}s'); kf += 1
        if kf >= nfr: break
    rem = (frame_t[kf] - t).total_seconds()
    if rem < 0.5: t = frame_t[kf]; continue
    dt = round(min(sim.stable_dt(cap=10.0), rem), 3)
    hr = (t + pd.Timedelta(seconds=1)).ceil('h')
    if hr != src_hr:                                   # move this hour's rain to the GPU once, not every step
        src_hr = hr; src = xp.asarray(RAIN[hr]) / 3.6e6 if hr in RAIN else None
    sim.step(dt, source=src, level=float(np.interp(t.value / 1e9, TIDE[0], TIDE[1])) if TIDE is not None else None)
    if INFLOW:
        tsec = t.value / 1e9
        for rr, cc, _, tq, qq, qb in INFLOW:
            qin = float(np.interp(tsec, tq, qq)); qin = max(qin - qb, 0.0) if PHYS >= 2 else qin      # v2: the channel carries the starting flow already; inject the rise
            if qin > 0:
                if getattr(sim, 'channels', False): sim.h[rr, cc] += qin * dt / (RES * RES * len(rr)) / xp.where(sim.h[rr, cc] < sim.dch[rr, cc], sim.phi[rr, cc], 1.0)
                else: sim.h[rr, cc] += qin * dt / (RES * RES * len(rr))
    if PHYS >= 2:
        frate = xp.where(Finf < Scapg, fcg + (f0g - fcg) * xp.exp(-Finf / Fk), Kdg)          # Horton until the soil store is full, then slow deep drainage
        fcap = xp.where(WATERg, 0.0, frate * f_scale + drain_mmph) / 3.6e6 * dt
    else:
        fcap = ((fcg + (f0g - fcg) * xp.exp(-Finf / Fk)) * f_scale + drain_mmph) / 3.6e6 * dt
    loss = xp.minimum(sim.h, fcap); sim.h -= loss; Finf += loss * 1000.0
    t = t + pd.Timedelta(seconds=dt); steps += 1
    if steps % 2000 == 0: log(f'   step {steps} t {t:%H:%M} dt {dt:.2f}s hmax {float(sim.h.max()):.2f} m | {time.time() - tstart:.0f}s')
hmx = xp.where(sim.fixed, 0, sim.hmax) if TIDE is not None else sim.hmax
hm = xp.asnumpy(hmx) if hasattr(xp, 'asnumpy') else hmx
np.save(f'{OUT}/hmax.npy', hm.astype(np.float16))
tonp = (lambda a: xp.asnumpy(a)) if hasattr(xp, 'asnumpy') else (lambda a: a)
np.save(f'{OUT}/z.npy', Z.astype(np.float32)); np.save(f'{OUT}/t_first.npy', tonp(T_FIRST)); np.save(f'{OUT}/dur.npy', tonp(DUR)); np.save(f'{OUT}/vmax.npy', tonp(VMAX).astype(np.float16)); np.save(f'{OUT}/hvmax.npy', tonp(HVMAX).astype(np.float16))
meta['cell_outputs'] = dict(hmax='peak depth m (float16)', t_first='frame index when depth first >= 10 cm (255 = never)', dur='number of frames >= 10 cm', vmax='peak speed m/s (float16)', hvmax='peak depth*speed m2/s (float16)')
meta['physics'] = dict(version=PHYS, water_mask=bool(PHYS >= 2), storage_limited_infiltration=bool(PHYS >= 2), channels_burnt=int(chan.sum()), subgrid_channels=bool(SUBGRID), manning='0.035 water/channel, 0.10 dense urban, 0.08 other' if PHYS >= 2 else '0.06 uniform',
                       tide=('gauge ' + os.environ.get('TIDE_STATION', '8443970')) if TIDE is not None else 'sea as sink', scheme='q-centred theta 0.7, Fr<=2' if PHYS >= 2 else 'Bates 2010, Fr<=1', antecedent_mm=round(WET0, 1))
if ROAD is not None:
    np.save(f'{OUT}/roads_cm.npy', ROAD['cm']); np.save(f'{OUT}/roads_mean_cm.npy', ROAD['mean_cm']); np.save(f'{OUT}/roads_v.npy', ROAD['v']); meta['roads'] = dict(segments=int(ROAD['n']), in_box=int(len(ROAD['inbox'])), flooded_10cm=int(((ROAD['cm'] >= 10).any(axis=0)).sum()), files='roads_cm.npy (max depth cm), roads_mean_cm.npy (mean depth cm along the segment), roads_v.npy (peak speed, 0.05 m/s units); frames x segments')
meta.update(inflows=[dict(name=n_, cells=int(len(r_)), peak_m3s=round(float(q_.max()), 1), start_m3s=round(float(qb_), 1)) for r_, c_, n_, _, q_, qb_ in INFLOW], steps=steps, runtime_s=round(time.time() - tstart), peak_wet_km2=round(float(((hm >= 0.1) & ~chan).sum() * RES * RES / 1e6), 1))
json.dump(meta, open(f'{OUT}/meta.json', 'w'))
log('run done:', meta['peak_wet_km2'], 'km2 peak wet,', steps, 'steps,', meta['runtime_s'], 's')
# ---- 5. upload ----
from huggingface_hub import CommitOperationAdd
files = sorted(os.listdir(OUT)); rem_dir = f'runs/{RUN}{TAG}_{RES:.0f}m'
for i in range(0, len(files), 25):
    ops = [CommitOperationAdd(path_in_repo=f'{rem_dir}/{f}', path_or_fileobj=f'{OUT}/{f}') for f in files[i:i + 25]]
    for k_ in range(5):
        try: api.create_commit(REPO, repo_type='dataset', operations=ops, commit_message=f'{rem_dir} {i + 1}-{i + len(ops)}'); break
        except Exception as e: log('  retry', k_, repr(e)[:120]); time.sleep(10 + 20 * k_)
log('uploaded to', rem_dir, '| ALL DONE')
