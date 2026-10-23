"""Sub-hourly rain forcing for w9_lisflood.py (opt-in, LF_RAIN_DT=<minutes>; docs/proto/rain/RAIN.md).

The model is driven by hourly MRMS MultiSensor QPE Pass2 (gauge-corrected). A 10-30 min convective burst is then spread evenly over
its hour. Here each hour's rain EXCESS (after the hourly CN loss and LF_INFIL_MODE=rain, exactly as the hourly run) is split into
LF_RAIN_DT-minute records in proportion to the radar's own timing inside that hour:

    record_k(cell) = excess_hour(cell) * A_k(cell) / sum_k A_k(cell)

A_k = radar accumulation in sub-interval k, from MRMS PrecipRate (2-min instantaneous rate, LF_RAIN_SUB=preciprate, the default) or
RadarOnly_QPE_15M (15-min accumulations, LF_RAIN_SUB=qpe15m). So every hour keeps the Pass2 total (and the hourly run's excess) in
every cell; only the timing inside the hour changes. Where the radar has (almost) no rain in an hour but Pass2 has, or the radar
files for the hour are mostly missing, the hour stays uniform (the hourly run's behaviour).

The weights are computed on the native 0.01 deg MRMS grid and interpolated bilinearly to the model grid (the same interpolation as
the hourly Pass2 grids in w9 mrms_hour); bilinear weights of nodes that each sum to 1 also sum to 1.

LISFLOOD-FP's DynamicRain is checked with an extra probe run (probe_subhourly): it tells whether a record's value is read as a rate
(mm/h) or as a depth per record interval, and that the sub-hourly time stamps are honoured. The file is then written in the unit the
solver reads, records stamped at the interval start (the 'forward' convention of rain_records) plus a closing zero record.
"""
import os, gzip, time, json
import numpy as np

S3 = 'https://noaa-mrms-pds.s3.amazonaws.com'
PRODUCTS = {   # key: (AWS product, interval of one file in minutes, kind)
    'preciprate': ('PrecipRate_00.00', 2, 'rate'),          # mm/h, instantaneous, every 2 min
    'qpe15m': ('RadarOnly_QPE_15M_00.00', 15, 'acc'),       # mm in the 15 min ending at the stamp
    'radar1h': ('RadarOnly_QPE_01H_00.00', 60, 'acc'),
    'pass2': ('MultiSensor_QPE_01H_Pass2_00.00', 60, 'acc'),
}


def _log(*a): print('[subhourly]', *a, flush=True)


def _get(url, tries=4, timeout=120):
    import requests
    for k in range(tries):
        try:
            r = requests.get(url, timeout=timeout)
            if r.status_code == 200: return r
            if r.status_code == 404: return None
        except Exception: pass
        time.sleep(2 * (k + 1))
    return None


def list_keys(prod, day):
    """All object keys of one MRMS product on one UTC day (S3 ListObjectsV2, paginated) -> {timestamp: key}."""
    import pandas as pd, re
    out, token = {}, None
    while True:
        u = f'{S3}/?list-type=2&prefix=CONUS/{prod}/{day:%Y%m%d}/' + (f'&continuation-token={_q(token)}' if token else '')
        r = _get(u)
        if r is None: break
        t = r.text
        for k in re.findall(r'<Key>([^<]+)</Key>', t):
            m = re.search(r'_(\d{8}-\d{6})\.grib2', k)
            if m: out[pd.Timestamp(m.group(1)[:8] + 'T' + m.group(1)[9:], tz='UTC').tz_localize(None)] = k
        m = re.search(r'<NextContinuationToken>([^<]+)</NextContinuationToken>', t)
        if not m: break
        token = m.group(1)
    return out


def _q(s):
    from urllib.parse import quote
    return quote(s, safe='')


def grid_axes(m):
    """1-D latitude (as stored, row 0 first) and longitude (-180..180) of a regular lat-lon GRIB message, from the grid keys."""
    Ni, Nj = int(m['Ni']), int(m['Nj'])
    la1, lo1 = float(m['latitudeOfFirstGridPointInDegrees']), float(m['longitudeOfFirstGridPointInDegrees'])
    di, dj = float(m['iDirectionIncrementInDegrees']), float(m['jDirectionIncrementInDegrees'])
    sgn = 1.0 if int(m['jScansPositively']) else -1.0
    lat = la1 + sgn * dj * np.arange(Nj); lon = lo1 + di * np.arange(Ni); lon = np.where(lon > 180, lon - 360, lon)
    return lat, lon


def read_crop(raw_gz, bounds, cache=None):
    """Decode one gzipped MRMS GRIB2 and cut the window bounds = (lat_min, lat_max, lon_min, lon_max).
    -> lat (descending), lon (ascending), values float32 (negative = no radar coverage -> NaN)."""
    import pygrib, tempfile
    fd, p = tempfile.mkstemp(suffix='.grib2'); os.close(fd)
    try:
        open(p, 'wb').write(gzip.decompress(raw_gz))
        g = pygrib.open(p); m = g[1]; lat, lon = grid_axes(m); v = np.ma.filled(m.values, -999).astype(np.float32); g.close()
    finally:
        os.remove(p)
    if lat[0] < lat[-1]: lat = lat[::-1]; v = v[::-1]
    i0 = np.searchsorted(-lat, -bounds[1]); i1 = np.searchsorted(-lat, -bounds[0]) + 1
    j0 = np.searchsorted(lon, bounds[2]); j1 = np.searchsorted(lon, bounds[3]) + 1
    c = v[i0:i1, j0:j1].copy(); c[c < 0] = np.nan
    return lat[i0:i1].copy(), lon[j0:j1].copy(), c


def fetch_crop(args):
    """(product key, timestamp, s3 key or None, bounds, cache dir) -> (timestamp, lat, lon, crop) or (timestamp, None, None, None)."""
    pk, ts, key, bounds, cache = args
    prod = PRODUCTS[pk][0]
    if key is None: key = f'CONUS/{prod}/{ts:%Y%m%d}/MRMS_{prod}_{ts:%Y%m%d-%H%M%S}.grib2.gz'
    cp = os.path.join(cache, os.path.basename(key)) if cache else None
    raw = None
    if cp and os.path.exists(cp): raw = open(cp, 'rb').read()
    else:
        r = _get(f'{S3}/{key}')
        if r is not None:
            raw = r.content
            if cp: os.makedirs(cache, exist_ok=True); open(cp, 'wb').write(raw)
    if raw is None: return ts, None, None, None
    try: la, lo, c = read_crop(raw, bounds)
    except Exception as e: _log('decode failed', key, repr(e)[:80]); return ts, None, None, None
    return ts, la, lo, c


def fetch_series(pk, t_start, t_end, bounds, cache=None, workers=4, log=_log):
    """Every file of product pk with stamp in [t_start, t_end] (from the S3 listing), cropped -> (lat, lon, {timestamp: crop})."""
    import pandas as pd
    from multiprocessing import Pool
    prod = PRODUCTS[pk][0]; keys = {}
    for day in pd.date_range(t_start.normalize(), t_end.normalize(), freq='D'): keys.update(list_keys(prod, day))
    sel = sorted((t, k) for t, k in keys.items() if t_start <= t <= t_end)
    if not sel: log(f'{prod}: no files on AWS for {t_start} - {t_end}'); return None, None, {}
    jobs = [(pk, t, k, bounds, cache) for t, k in sel]
    with Pool(workers) as pool: res = pool.map(fetch_crop, jobs, chunksize=4)
    out, lat, lon = {}, None, None
    for t, la, lo, c in res:
        if c is None: continue
        if lat is None: lat, lon = la, lo
        if c.shape != (len(lat), len(lon)): continue
        out[t] = c
    log(f'{prod}: {len(out)} of {len(sel)} listed files read for {t_start} - {t_end}')
    return lat, lon, out


def file_interval(pk, t, hour_start):
    """Minutes (start, end) after hour_start that one file covers, and the factor turning its value into mm over that interval."""
    _, L, kind = PRODUCTS[pk]
    u = (t - hour_start).total_seconds() / 60.0
    if kind == 'rate': return u - L / 2.0, u + L / 2.0, L / 60.0      # instantaneous rate, centred on its stamp (2 min: +-1 min)
    return u - L, u, 1.0                                             # accumulation over the L minutes ending at the stamp


def hour_bins(pk, files, hour_start, dt_min, min_cover=0.5):
    """Radar accumulation (mm) per dt_min sub-interval of the hour starting at hour_start, from {timestamp: crop}.
    Each file's water is spread evenly over the interval it covers and binned by overlap. A sub-interval whose covered share is
    below min_cover gets the hour's mean covered rate. -> (A (nsub, ni, nj), covered share of the hour) or (None, cover)."""
    nsub = 60 // dt_min; acc = None; cov = np.zeros(nsub)
    for t, c in files.items():
        a, b, f = file_interval(pk, t, hour_start)
        if b <= 0 or a >= 60: continue
        a_, b_ = max(a, 0.0), min(b, 60.0); L = b - a
        cc = np.nan_to_num(c, nan=0.0) * f / L        # mm per minute over [a, b]
        if acc is None: acc = np.zeros((nsub,) + c.shape, np.float64)
        for k in range(nsub):
            o = min(b_, (k + 1) * dt_min) - max(a_, k * dt_min)
            if o > 0: acc[k] += cc * o; cov[k] += o
    cover = float(cov.sum() / 60.0)
    if acc is None or cover < min_cover: return None, cover
    share = cov / dt_min
    good = share >= min_cover
    if not good.all():
        mean_rate = sum(acc[k] / max(cov[k], 1e-9) for k in range(nsub) if good[k]) / max(int(good.sum()), 1)   # mm/min
        for k in range(nsub):
            if not good[k]: acc[k] = mean_rate * dt_min
    for k in range(nsub):
        if good[k] and share[k] < 0.999: acc[k] *= 1.0 / share[k]      # scale a partly covered sub-interval to its full length
    return acc.astype(np.float32), cover


def weights_from_bins(A, eps=0.1):
    """Sub-interval weights summing to 1 per pixel; uniform where the radar hour total is below eps mm."""
    S = A.sum(0); n = A.shape[0]
    W = np.where(S[None] > eps, A / np.maximum(S[None], 1e-12), 1.0 / n).astype(np.float32)
    return W


class SubHourly:
    """Native-grid weights per model hour; .model_weights(h) interpolates them to the model grid."""

    def __init__(self, dt_min, src, lat, lon, W, lat_c, lon_c, report):
        self.dt, self.src, self.lat, self.lon, self.W, self.report = dt_min, src, lat, lon, W, report
        self.lat_c, self.lon_c = np.asarray(lat_c), np.asarray(lon_c); self.nsub = 60 // dt_min

    def model_weights(self, h):
        ny, nx = len(self.lat_c), len(self.lon_c)
        if self.W[h] is None: return np.full((self.nsub, ny, nx), 1.0 / self.nsub, np.float32)
        from scipy.interpolate import RegularGridInterpolator
        LA, LO = np.meshgrid(self.lat_c, self.lon_c, indexing='ij'); out = np.empty((self.nsub, ny, nx), np.float32)
        for k in range(self.nsub):
            fi = RegularGridInterpolator((self.lat[::-1], self.lon), self.W[h][k][::-1], bounds_error=False, fill_value=1.0 / self.nsub)
            out[k] = fi((LA, LO))
        s = out.sum(0); out /= np.where(s > 0, s, 1.0)[None]          # exact 1 (round-off)
        return out


def build(hour_ends, dt_min, lat_c, lon_c, src=None, cache=None, workers=None, log=_log, pass2=None):
    """hour_ends: list of pd.Timestamp (naive UTC), hour h of the run = (hour_ends[h] - 1 h, hour_ends[h]].
    pass2: optional (H, ny, nx) hourly Pass2 on the model grid, only for the report (radar/Pass2 ratio)."""
    import pandas as pd
    if 60 % dt_min: raise SystemExit(f'LF_RAIN_DT={dt_min}: must divide 60 (2, 3, 4, 5, 6, 10, 12, 15, 20, 30)')
    src = src or ('qpe15m' if dt_min >= 15 and dt_min % 15 == 0 and os.environ.get('LF_RAIN_SUB') == 'qpe15m' else os.environ.get('LF_RAIN_SUB', 'preciprate'))
    if src not in ('preciprate', 'qpe15m'): raise SystemExit(f'LF_RAIN_SUB must be preciprate or qpe15m, not {src!r}')
    workers = workers or int(os.environ.get('LF_RAIN_SUB_WORKERS', '4'))
    bounds = (float(np.min(lat_c)) - 0.06, float(np.max(lat_c)) + 0.06, float(np.min(lon_c)) - 0.06, float(np.max(lon_c)) + 0.06)
    L = PRODUCTS[src][1]
    t_start = hour_ends[0] - pd.Timedelta(minutes=60 + L); t_end = hour_ends[-1] + pd.Timedelta(minutes=L)
    lat, lon, files = fetch_series(src, t_start, t_end, bounds, cache=cache, workers=workers, log=log)
    W, covers, uni_px, peak_sub, peak_hr = [], [], [], [], []
    for h, te in enumerate(hour_ends):
        hs = te - pd.Timedelta(hours=1)
        fh = {t: c for t, c in files.items() if hs - pd.Timedelta(minutes=L) <= t <= te + pd.Timedelta(minutes=L)}
        A, cover = hour_bins(src, fh, hs, dt_min) if fh else (None, 0.0)
        covers.append(round(cover, 2))
        if A is None: W.append(None); uni_px.append(1.0); continue
        Wh = weights_from_bins(A); W.append(Wh)
        S = A.sum(0); uni_px.append(round(float((S <= 0.1).mean()), 3))
        peak_sub.append(float(Wh.max(0).mean())); peak_hr.append(1.0 / Wh.shape[0])
    rep = dict(dt_min=dt_min, source=f'MRMS {PRODUCTS[src][0]} (AWS noaa-mrms-pds), radar timing inside each hour; hourly totals = MRMS MultiSensor QPE 01H Pass2',
               files=len(files), hours=len(hour_ends), hours_uniform=int(sum(w is None for w in W)), hour_cover=covers,
               uniform_pixel_share_per_hour=uni_px,
               mean_max_weight=round(float(np.mean(peak_sub)), 3) if peak_sub else None,
               note='weights = radar sub-interval accumulation / radar hour accumulation per 0.01 deg pixel (uniform where the radar hour < 0.1 mm '
                    'or less than half the hour is covered by files), bilinear to the model grid, applied to the hourly rain excess')
    if pass2 is not None and lat is not None:
        rep['radar_vs_pass2'] = radar_ratio(src, files, hour_ends, lat, lon, lat_c, lon_c, pass2)
    log(f"LF_RAIN_DT={dt_min} ({src}): {rep['files']} radar files, {rep['hours_uniform']} of {rep['hours']} hours uniform (no radar), "
        f"mean of the largest sub-interval weight {rep['mean_max_weight']} (uniform = {1 / (60 // dt_min):.3f})")
    return SubHourly(dt_min, src, lat if lat is not None else np.array([0.0, 1.0]), lon if lon is not None else np.array([0.0, 1.0]), W, lat_c, lon_c, rep)


def radar_ratio(src, files, hour_ends, lat, lon, lat_c, lon_c, pass2):
    """Box-mean radar hour accumulation / box-mean Pass2 hour (where Pass2 box mean >= 1 mm), as a report."""
    import pandas as pd
    out = []
    i0, i1 = np.searchsorted(-lat, -np.max(lat_c)), np.searchsorted(-lat, -np.min(lat_c)) + 1
    j0, j1 = np.searchsorted(lon, np.min(lon_c)), np.searchsorted(lon, np.max(lon_c)) + 1
    for h, te in enumerate(hour_ends):
        p = float(pass2[h].mean())
        if p < 1.0: continue
        hs = te - pd.Timedelta(hours=1); L = PRODUCTS[src][1]
        fh = {t: c for t, c in files.items() if hs - pd.Timedelta(minutes=L) <= t <= te + pd.Timedelta(minutes=L)}
        A, _ = hour_bins(src, fh, hs, 60) if fh else (None, 0)
        if A is None: continue
        out.append(dict(hour_end=f'{te:%Y-%m-%dT%H:%MZ}', pass2_box_mm=round(p, 1), radar_box_mm=round(float(A.sum(0)[i0:i1, j0:j1].mean()), 1)))
    return out


# ---------------------------------------------------------------------------------------------------------------------------
# LISFLOOD-FP: probe how DynamicRain reads sub-hourly records, and the streaming writer
# ---------------------------------------------------------------------------------------------------------------------------
def analyse_probe_sub(depth_m, dt_min, value=360.0):
    """Mean depth after a record of `value` held for one dt_min interval (probe_subhourly) -> 'rate' (value read as mm/h),
    'depth' (mm per record interval) or None (neither: the solver does not honour sub-hourly stamps)."""
    rate_m = value * dt_min / 60.0 / 1000.0; depth_m_exp = value / 1000.0
    r1, r2 = depth_m / rate_m, depth_m / depth_m_exp
    units = 'rate' if 0.8 <= r1 <= 1.25 else ('depth' if 0.8 <= r2 <= 1.25 else None)
    return dict(dt_min=dt_min, value=value, depth_m=round(float(depth_m), 5), ratio_to_rate=round(float(r1), 3), ratio_to_depth=round(float(r2), 3), units=units)


def probe_subhourly(W9, exe, cuda, dt_min):
    """8x8 flat closed box: records at 0, dt, 2 dt (minutes) with value 360 in the SECOND record only, run for 3 dt. Under the
    forward convention the box gets 360 mm/h x dt/60 h if the value is a rate, 360 mm if it is a depth per record, 0 if the
    sub-hourly stamps are ignored (e.g. a record looked up by whole hour). W9 = the w9_lisflood module."""
    import shutil
    wd = f'{W9.WORK}/probe_sub'; shutil.rmtree(wd, ignore_errors=True); os.makedirs(f'{wd}/results')
    n = 8; W9.write_asc(f'{wd}/dem.asc', np.full((n, n), 10.0), 0.0, 0.0, 100.0)
    r = np.zeros((3, n, n), np.float32); r[1] = 360.0; th = np.array([0.0, dt_min / 60.0, 2 * dt_min / 60.0])
    W9.write_rain_nc(f'{wd}/rain.nc', r, 0.0, 0.0, 100.0, th)
    sim = int(round(3 * dt_min * 60))
    W9.write_par(f'{wd}/p.par', 'p', sim, saveint=sim, massint=60, cuda=cuda, rain='rain.nc', initial_tstep=1)
    W9.run_lisflood(exe, wd, 'p.par', timeout=600)
    h = W9.max_depth(wd, 'p')[0]
    # the last snapshot is the end state: the box is closed, so the mean of the end depth is the volume; the max file also works on a flat box
    snaps = sorted(__import__('glob').glob(f'{wd}/results/p-*.wd'))
    if snaps: h = W9.read_asc(snaps[-1])[0]
    out = analyse_probe_sub(float(np.nanmean(h)), dt_min); W9.log('sub-hourly rain probe:', out); return out


def write_rain_nc_sub(path, excess_hourly, sub, x0, y0, res, unit='rate', divide=1.0, flip_y=False, flip_x=False, source=''):
    """Stream the sub-hourly records to the TUFLOW NetCDF dynamicrainfile, in the layout of w9 write_rain_nc (variables time, y, x
    first and in that order; y descending; x ascending; 'rainfall_depth' (time, y, x)). excess_hourly (H, ny, nx) mm per hour.
    unit 'rate': records in mm/h (mm per record x 60/dt); 'depth': mm per record. Forward stamps k*dt/60 h plus a closing zero
    record at H h. Returns stats."""
    import netCDF4
    H, ny, nx = excess_hourly.shape; n = sub.nsub; dt = sub.dt; fac = (60.0 / dt if unit == 'rate' else 1.0) / divide
    f = netCDF4.Dataset(path, 'w', format='NETCDF3_64BIT_OFFSET')
    f.title = 'Gridded Rainfall'; f.source = 'mass-flood-watch w9_lisflood.py ' + (source or f'(MRMS QPE 01H Pass2, {dt}-min radar timing)')
    f.comment = f'Contains time-varying gridded rainfall ({"mm/h" if unit == "rate" else "mm per interval"}, {dt}-min records) for LISFLOOD-FP dynamicrainfile'
    f.createDimension('time', H * n + 1); f.createDimension('y', ny); f.createDimension('x', nx)
    t = f.createVariable('time', 'f8', ('time',)); t.standard_name = 'time'; t.long_name = 'time'; t.units = 'hours'; t.axis = 'T'
    y = f.createVariable('y', 'f8', ('y',)); y.standard_name = 'projection_y_coordinate'; y.long_name = 'y-coordinate in cartesian system'; y.units = 'm'; y.axis = 'Y'
    x = f.createVariable('x', 'f8', ('x',)); x.standard_name = 'projection_x_coordinate'; x.long_name = 'x-coordinate in cartesian system'; x.units = 'm'; x.axis = 'X'
    v = f.createVariable('rainfall_depth', 'f4', ('time', 'y', 'x'), fill_value=np.float32(-999.0)); v.units = 'mm/h' if unit == 'rate' else 'mm'
    tot = f.createVariable('total_rainfall_depth', 'f4', ('y', 'x'), fill_value=np.float32(-999.0))
    y[:] = y0 + (ny - np.arange(ny) - 0.5) * res; x[:] = x0 + (np.arange(nx) + 0.5) * res
    t[:] = np.arange(H * n + 1, dtype=np.float64) * dt / 60.0
    total = np.zeros((ny, nx), np.float64); peak_rate = np.zeros((ny, nx), np.float32); peak_hourly = excess_hourly.max(0)
    for h in range(H):
        w = sub.model_weights(h); e = np.asarray(excess_hourly[h], np.float32)
        for k in range(n):
            rec = e * w[k]; total += rec; peak_rate = np.maximum(peak_rate, rec * (60.0 / dt))
            out = rec * fac
            if flip_y: out = out[::-1, :]
            if flip_x: out = out[:, ::-1]
            v[h * n + k] = out.astype(np.float32)
    v[H * n] = np.zeros((ny, nx), np.float32)
    tt = (total / divide).astype(np.float32)          # total depth in mm whatever the record unit
    if flip_y: tt = tt[::-1, :]
    if flip_x: tt = tt[:, ::-1]
    tot[:] = tt
    f.close()
    wet = peak_hourly > 1.0
    return dict(records=H * n + 1, unit=unit, total_excess_mean_mm=round(float(total.mean()), 3), hourly_excess_mean_mm=round(float(excess_hourly.sum(0).mean()), 3),
                peak_excess_rate_box_max_mmh=round(float(peak_rate.max()), 1), peak_excess_hourly_box_max_mmh=round(float(peak_hourly.max()), 1),
                peak_rate_over_hourly_mean_where_wet=round(float((peak_rate[wet] / peak_hourly[wet]).mean()), 2) if wet.any() else None)


def selftest(W9=None):
    """Offline: binning, weights, interpolation sum, the streaming writer against w9 write_rain_nc, the probe analysis."""
    import tempfile, pandas as pd
    ok = []
    hs = pd.Timestamp('2023-07-14T15:00')
    # PrecipRate: 60 mm/h in the 10 min 15:20-15:30 (files 15:22..15:28 plus half of 15:20 and 15:30), else 0 -> 10 mm all in bin 4 of 6 (dt 10)
    files = {hs + pd.Timedelta(minutes=m): np.full((2, 3), 60.0 if 20 <= m <= 30 else 0.0, np.float32) for m in range(0, 62, 2)}
    files[hs + pd.Timedelta(minutes=20)][:] = 60.0; files[hs + pd.Timedelta(minutes=30)][:] = 60.0
    A, cover = hour_bins('preciprate', files, hs, 10)
    # files 15:20..15:30 cover 15:19-15:31 at 1 mm/min: bin 1 [10, 20) 1 mm, bin 2 [20, 30) 10 mm, bin 3 [30, 40) 1 mm
    assert cover > 0.99 and A.shape == (6, 2, 3) and abs(A.sum(0)[0, 0] - 12.0) < 1e-4
    assert np.allclose(A[:, 0, 0], [0, 1, 10, 1, 0, 0], atol=1e-4)
    A5, _ = hour_bins('preciprate', files, hs, 5)
    assert A5.shape == (12, 2, 3) and abs(A5.sum(0)[0, 0] - 12.0) < 1e-4 and np.allclose(A5[:, 0, 0], [0, 0, 0, 1, 5, 5, 1, 0, 0, 0, 0, 0], atol=1e-4)
    ok.append('PrecipRate binning: rate x 2 min spread over +-1 min, overlap-binned, totals conserved for dt 5 and 10')
    # missing files: drop 15:40-15:48 -> bins covered < 50 % filled with the hour's mean rate; hour still accepted
    f2 = {t: c for t, c in files.items() if not (40 <= (t - hs).total_seconds() / 60 <= 48)}
    A2, c2 = hour_bins('preciprate', f2, hs, 10); assert A2 is not None and 0.8 < c2 < 0.9 and A2[4].min() >= 0
    A3, c3 = hour_bins('preciprate', {t: c for t, c in files.items() if (t - hs).total_seconds() < 20 * 60}, hs, 10); assert A3 is None and c3 < 0.5
    ok.append('missing radar files: partly covered bins scaled, mostly missing hour -> uniform')
    # 15-min accumulations: 4 files ending 15:15..16:00
    q = {hs + pd.Timedelta(minutes=m): np.full((2, 3), float(m), np.float32) for m in (15, 30, 45, 60)}
    Aq, _ = hour_bins('qpe15m', q, hs, 15); assert np.allclose(Aq[:, 0, 0], [15, 30, 45, 60])
    Aq5, _ = hour_bins('qpe15m', q, hs, 5); assert np.allclose(Aq5[:, 0, 0], np.repeat([5, 10, 15, 20], 3))
    ok.append('RadarOnly_QPE_15M binning (15 and 5 min)')
    W = weights_from_bins(np.stack([np.zeros((2, 2)), np.array([[3.0, 0.05], [0.0, 1.0]]), np.array([[1.0, 0.0], [0.0, 1.0]])]))
    assert np.allclose(W.sum(0), 1) and abs(W[1, 0, 0] - 0.75) < 1e-6 and np.allclose(W[:, 0, 1], 1 / 3) and np.allclose(W[:, 1, 0], 1 / 3)
    ok.append('weights sum to 1, uniform where the radar hour < 0.1 mm')
    lat = np.array([42.30, 42.29, 42.28, 42.27]); lon = np.array([-71.90, -71.89, -71.88])
    Wn = np.random.default_rng(0).random((4, 4, 3)).astype(np.float32); Wn /= Wn.sum(0)[None]
    sub = SubHourly(15, 'preciprate', lat, lon, [Wn, None], np.linspace(42.29, 42.275, 5), np.linspace(-71.895, -71.885, 6), {})
    mw = sub.model_weights(0); assert mw.shape == (4, 5, 6) and np.allclose(mw.sum(0), 1, atol=1e-5) and np.allclose(sub.model_weights(1), 0.25)
    ok.append('bilinear weights on the model grid sum to 1; a hour without radar is uniform')
    if W9 is not None:
        d = tempfile.mkdtemp(prefix='subst_'); from scipy.io import netcdf_file
        x0, y0, res = 150000.0, 905000.0, 20.0; ny, nx = 5, 6
        ex = np.zeros((2, ny, nx), np.float32); ex[0, 0, :] = 8.0; ex[1, 1, 2] = 4.0
        uni = SubHourly(15, 'preciprate', lat, lon, [None, None], np.linspace(42.29, 42.275, ny), np.linspace(-71.895, -71.885, nx), {})
        st = write_rain_nc_sub(f'{d}/s.nc', ex, uni, x0, y0, res, unit='depth')
        rec, th = W9.rain_records(np.repeat(ex / 4, 4, axis=0), 'forward'); W9.write_rain_nc(f'{d}/h.nc', rec, x0, y0, res, th / 4)
        a, b = netcdf_file(f'{d}/s.nc', 'r', mmap=False), netcdf_file(f'{d}/h.nc', 'r', mmap=False)
        assert list(a.variables)[:3] == ['time', 'y', 'x'] == list(b.variables)[:3]
        for k in ('time', 'y', 'x', 'rainfall_depth', 'total_rainfall_depth'): assert np.allclose(a.variables[k][:], b.variables[k][:]), k
        assert np.all(np.diff(a.variables['y'][:]) < 0) and abs(st['total_excess_mean_mm'] - st['hourly_excess_mean_mm']) < 1e-4
        a.close(); b.close()
        st = write_rain_nc_sub(f'{d}/r.nc', ex, uni, x0, y0, res, unit='rate')
        a = netcdf_file(f'{d}/r.nc', 'r', mmap=False); v = a.variables['rainfall_depth'][:]
        assert v.shape == (9, ny, nx) and np.allclose(v[0, 0, :], 8.0) and np.allclose(v[4:8, 1, 2], 4.0) and v[8].sum() == 0
        assert np.allclose(a.variables['time'][:], np.arange(9) * 0.25) and np.allclose(a.variables['total_rainfall_depth'][:][0], 8.0)
        a.close(); ok.append('streaming writer = w9 write_rain_nc layout (time, y, x first; y descending; forward stamps; closing zero); rate unit = mm/h')
        st = write_rain_nc_sub(f'{d}/f.nc', ex, uni, x0, y0, res, unit='depth', flip_y=True)
        a = netcdf_file(f'{d}/f.nc', 'r', mmap=False); assert np.allclose(a.variables['rainfall_depth'][:][0, -1, :], 2.0); a.close()
        ok.append('flip_y honoured')
        import shutil; shutil.rmtree(d)
    p = analyse_probe_sub(0.030, 5); assert p['units'] == 'rate'
    p = analyse_probe_sub(0.360, 5); assert p['units'] == 'depth'
    p = analyse_probe_sub(0.0, 5); assert p['units'] is None
    p = analyse_probe_sub(0.06, 5); assert p['units'] is None
    ok.append('sub-hourly probe analysis (rate / depth per record / stamps ignored)')
    for o in ok: print('ok  ', o)
    return ok
