"""Live feeds for MassDOT District 3 -> small JSON summaries in docs/site/data/live/ (docs/proto/live/LIVE_FEEDS.md).

    python proto/live_feeds.py rain        # MRMS observed rain now: RadarOnly QPE 1 h / 3 h (2-min), MultiSensor QPE Pass1 1 h / 3 h, PrecipRate
    python proto/live_feeds.py nowcast     # EXPERIMENTAL 0-2 h nowcast: last PrecipRate frames advected (pysteps Lucas-Kanade, else phase correlation)
    python proto/live_feeds.py flash       # MRMS FLASH: CREST max unit streamflow, QPE/FFG ratio 1/3/6 h; per-town flags
    python proto/live_feeds.py nwm         # NWM short-range (18 h) streamflow at mapped culverts vs their HDS-5 capacity at the road crest
    python proto/live_feeds.py snow        # NOHRSC SNODAS daily snow depth / SWE (NSIDC G02158)
    python proto/live_feeds.py validation  # MassDOT roadway events + SeeClickFix flood-type issues -> docs/proto/live/archive/YYYY-MM.jsonl
    python proto/live_feeds.py run [--feeds rain,nowcast,...] [--force] [--github-output $GITHUB_OUTPUT]   # all feeds + commit decision
    python proto/live_feeds.py map-comids  # one-off: culverts -> NHDPlus v2 COMID (= NWM feature_id) via USGS NLDI -> docs/proto/live/crossing_comids.json
    python proto/live_feeds.py selftest    # offline checks (synthetic grids)

Every feed is independent: an exception in one is recorded in docs/site/data/live/status.json (state 'failed', the error, the last success)
and its previous output file is left untouched.  `run` decides whether the outputs are worth a commit (see decide()): at most one commit per
run, immediately when an alert level changes, otherwise only when something material changed and the last commit is >= 3 h old, plus a
24 h heartbeat.  Nothing here feeds the flood model; these are context layers and (validation) future scoring material.
"""
import os, sys, re, io, json, gzip, math, time, tarfile, hashlib, argparse, traceback, datetime as dt
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, 'docs', 'site', 'data', 'live')
ARCH = os.path.join(ROOT, 'docs', 'proto', 'live', 'archive')
COMID_MAP = os.path.join(ROOT, 'docs', 'proto', 'live', 'crossing_comids.json')
LAT, LON = (41.98, 42.75), (-72.25, -71.25)          # District 3 box (as proto/ground_state.py)
UA = {'User-Agent': 'mass-flood-watch research (github.com/Horus331/mass-flood-watch)'}
MRMS = 'https://noaa-mrms-pds.s3.amazonaws.com'
NWM_S3 = 'https://noaa-nwm-pds.s3.amazonaws.com'
NWPS = 'https://api.water.noaa.gov/nwps/v1/reaches/{rid}/streamflow?series=short_range'
NLDI = ['https://api.water.usgs.gov/nldi/linked-data', 'https://labs.waterdata.usgs.gov/api/nldi/linked-data']
SNODAS = 'https://noaadata.apps.nsidc.org/NOAA/G02158/masked/{d:%Y}/{d:%m_%b}/SNODAS_{d:%Y%m%d}.tar'
EVENTS = 'http://events.massdot.evbg.net/'
SCF = 'https://seeclickfix.com/api/v2/issues'
FEEDS = ('rain', 'nowcast', 'flash', 'nwm', 'snow', 'validation')
# Alert levels (fixed in advance, not tuned): 1 h rain max >= 10 / 25 / 50 mm (NWS heavy-rain rates ~ 0.4 / 1 / 2 in/h)
RAIN_LEVELS = (10.0, 25.0, 50.0)
FLASH_UNITQ = 2.0      # m3 s-1 km-2 (CREST max unit streamflow; flash-flood guidance in the FLASH literature: > 2 likely, > 5 significant)
FLASH_RATIO = 1.0      # QPE / FFG
CADENCE_H, HEARTBEAT_H = 3.0, 24.0


def log(*a): print(*a, flush=True)


def utcnow(): return dt.datetime.now(dt.timezone.utc).replace(tzinfo=None)


def iso(t): return t.strftime('%Y-%m-%dT%H:%MZ') if t else None


class HTTPErr(RuntimeError): pass


def http_get(url, params=None, timeout=90, tries=3, headers=None, ok404=False):
    import requests
    last = None
    for k in range(tries):
        try:
            r = requests.get(url, params=params, timeout=timeout, headers=dict(UA, **(headers or {})))
            if r.status_code == 200: return r
            if r.status_code == 404 and ok404: return None
            last = HTTPErr(f'HTTP {r.status_code} {r.reason} for {r.url[:200]}: {r.text[:160]!r}')
            if r.status_code < 500 and r.status_code != 429: break
        except Exception as e: last = e
        time.sleep(3 * (k + 1))
    raise last


# ------------------------------------------------------------------------------------------------ towns on a grid
_TOWNS = None


def towns():
    global _TOWNS
    if _TOWNS is None:
        sys.path.insert(0, HERE); import forecast
        _TOWNS = forecast.d3_towns()
    return _TOWNS


_TIDX = {}


def town_index(lat1d, lon1d):
    """[(name, flat indices)] of the grid points (lat1d x lon1d, row-major) inside each District 3 town; the nearest point for towns smaller
    than a cell; plus the union mask (the district)."""
    key = (lat1d.size, lon1d.size, round(float(lat1d[0]), 5), round(float(lon1d[0]), 5))
    if key in _TIDX: return _TIDX[key]
    from matplotlib.path import Path
    LO, LA = np.meshgrid(lon1d, lat1d); P = np.c_[LO.ravel(), LA.ravel()]; out = []; union = np.zeros(len(P), bool)
    for n, lab, rings in towns():
        k = np.zeros(len(P), bool)
        for r in rings:
            bb = (P[:, 0] >= r[:, 0].min()) & (P[:, 0] <= r[:, 0].max()) & (P[:, 1] >= r[:, 1].min()) & (P[:, 1] <= r[:, 1].max())
            if bb.any(): k[bb] ^= Path(r).contains_points(P[bb])       # xor: holes
        idx = np.nonzero(k)[0]
        if not len(idx): idx = np.array([int(np.argmin((P[:, 0] - lab[0]) ** 2 + (P[:, 1] - lab[1]) ** 2))])
        out.append((n, idx)); union[idx] = True
    _TIDX[key] = (out, union)
    return _TIDX[key]


def town_of_points(lon, lat):
    """Town name (or None) for each lon/lat point."""
    from matplotlib.path import Path
    P = np.c_[np.asarray(lon, float), np.asarray(lat, float)]; res = [None] * len(P)
    for n, lab, rings in towns():
        k = np.zeros(len(P), bool)
        for r in rings: k ^= Path(r).contains_points(P)
        for i in np.nonzero(k)[0]: res[i] = res[i] or n
    return res


def r1(v, d=1):
    return None if v is None or not np.isfinite(v) else round(float(v), d)


def town_stats(V, lat1d, lon1d, fn=('max',), d=1):
    """{town: [stat...]} and district (max, mean) of grid V (lat1d x lon1d)."""
    T, U = town_index(lat1d, lon1d); f = V.ravel(); res = []
    for n, idx in T:
        x = f[idx]; x = x[np.isfinite(x)]
        res.append([n] + [r1(x.max() if s == 'max' else x.mean(), d) if len(x) else None for s in fn])
    u = f[U]; u = u[np.isfinite(u)]
    return res, (r1(u.max(), d) if len(u) else None, r1(u.mean(), 2) if len(u) else None)


# ------------------------------------------------------------------------------------------------ MRMS on AWS
def s3_list(base, prefix, start_after=None):
    import xml.etree.ElementTree as ET
    out, tok = [], None
    while True:
        p = {'list-type': '2', 'prefix': prefix}
        if tok: p['continuation-token'] = tok
        elif start_after: p['start-after'] = start_after
        X = ET.fromstring(http_get(base + '/', params=p, timeout=60).content); ns = {'s': X.tag.split('}')[0].strip('{')}
        out += [c.find('s:Key', ns).text for c in X.findall('s:Contents', ns)]
        t = X.find('s:NextContinuationToken', ns)
        if t is None: return out
        tok = t.text


def mrms_recent(product, since, now=None):
    """[(valid time, url)] of `product` files valid after `since` (naive UTC), oldest first."""
    now = now or utcnow(); out = []; d = since.date()
    while d <= now.date():
        pre = f'CONUS/{product}/{d:%Y%m%d}/'
        sa = f'{pre}MRMS_{product}_{since:%Y%m%d-%H%M%S}' if d == since.date() else None
        for k in s3_list(MRMS, pre, sa):
            m = re.search(r'_(\d{8}-\d{6})\.grib2\.gz$', k)
            if m:
                t = dt.datetime.strptime(m.group(1), '%Y%m%d-%H%M%S')
                if t > since: out.append((t, f'{MRMS}/{k}'))
        d += dt.timedelta(days=1)
    return sorted(out)


def mrms_latest(product, max_age_min, now=None):
    now = now or utcnow(); L = mrms_recent(product, now - dt.timedelta(minutes=max_age_min), now)
    if not L: raise RuntimeError(f'no {product} file on AWS in the last {max_age_min} min (s3://noaa-mrms-pds/CONUS/{product}/)')
    return L[-1]


def grib_box(raw, lat_rng, lon_rng, gz=True):
    """MRMS grib2(.gz) bytes -> (values north->south, lat1d descending, lon1d ascending) inside the box; negative (no coverage / missing) -> NaN."""
    import pygrib, tempfile
    with tempfile.NamedTemporaryFile(suffix='.grib2', delete=False) as f: f.write(gzip.decompress(raw) if gz else raw); p = f.name
    try:
        g = pygrib.open(p); m = g[1]
        Ni, Nj = int(m['Ni']), int(m['Nj']); la0, lo0 = float(m['latitudeOfFirstGridPointInDegrees']), float(m['longitudeOfFirstGridPointInDegrees'])
        di, dj = float(m['iDirectionIncrementInDegrees']), float(m['jDirectionIncrementInDegrees'])
        lat = la0 + (dj if int(m['jScansPositively']) else -dj) * np.arange(Nj); lon = lo0 + di * np.arange(Ni); lon = np.where(lon > 180, lon - 360, lon)
        v = np.ma.filled(m.values, np.nan).astype(np.float32); g.close()
    finally: os.remove(p)
    if lat[0] < lat[-1]: lat = lat[::-1]; v = v[::-1]
    i = (lat >= lat_rng[0]) & (lat <= lat_rng[1]); j = (lon >= lon_rng[0]) & (lon <= lon_rng[1])
    s = v[np.ix_(i, j)].copy(); s[s < 0] = np.nan
    return s, lat[i], lon[j]


def mrms_box(url, lat_rng=LAT, lon_rng=LON):
    return grib_box(http_get(url, timeout=120).content, lat_rng, lon_rng)


# ------------------------------------------------------------------------------------------------ 1. observed rain
RAMP = [(0.25, (160, 210, 255)), (1, (90, 160, 245)), (2.5, (40, 110, 230)), (5, (40, 180, 90)), (10, (250, 220, 40)), (15, (250, 150, 30)),
        (25, (235, 60, 40)), (35, (190, 20, 60)), (50, (170, 40, 180)), (75, (240, 170, 250))]


def rain_png(V, path):
    from PIL import Image
    a = np.zeros(V.shape + (4,), np.uint8); x = np.nan_to_num(V, nan=0.0)
    for th, c in RAMP:
        k = x >= th; a[k, :3] = c; a[k, 3] = 200
    Image.fromarray(a, 'RGBA').save(path, optimize=True)


def feed_rain(now=None):
    now = now or utcnow(); P = {}; err = {}
    prods = dict(radar_1h=('RadarOnly_QPE_01H_00.00', 30), radar_3h=('RadarOnly_QPE_03H_00.00', 30), ms_1h=('MultiSensor_QPE_01H_Pass1_00.00', 180),
                 ms_3h=('MultiSensor_QPE_03H_Pass1_00.00', 180), rate=('PrecipRate_00.00', 20))
    for k, (prod, age) in prods.items():
        try:
            t, u = mrms_latest(prod, age, now); V, la, lo = mrms_box(u); P[k] = dict(t=t, url=u, V=V, lat=la, lon=lo)
        except Exception as e: err[k] = repr(e)[:240]; log('  rain', k, err[k])
    if 'radar_1h' not in P and 'ms_1h' not in P: raise RuntimeError('no 1 h QPE: ' + json.dumps(err)[:400])
    out = dict(made=iso(now), made_by='proto/live_feeds.py rain', units='mm (rate: mm/h)', products={}, errors=err,
               source='NOAA MRMS on AWS (s3://noaa-mrms-pds/CONUS/), 0.01 deg; radar_* = RadarOnly QPE (2-min updates, no gauge correction), '
                      'ms_* = MultiSensor QPE Pass1 (gauge-corrected, hourly, ~1 h latency)')
    per = {}
    for k, p in P.items():
        T, (mx, mn) = town_stats(p['V'], p['lat'], p['lon'], ('max', 'mean'))
        out['products'][k] = dict(product=prods[k][0], valid=iso(p['t']), district_max=mx, district_mean=mn, url=p['url'])
        per[k] = {t[0]: t[1:] for t in T}
    cols = [('radar_1h', 0), ('radar_1h', 1), ('radar_3h', 0), ('ms_1h', 0), ('ms_3h', 0), ('rate', 0)]
    out['town_fields'] = ['town', 'radar_1h_max', 'radar_1h_mean', 'radar_3h_max', 'ms_1h_max', 'ms_3h_max', 'rate_max']
    out['towns'] = [[n] + [per.get(k, {}).get(n, [None, None])[j] for k, j in cols] for n, _, _ in towns()]
    g = P.get('radar_1h') or P.get('ms_1h'); gk = 'radar_1h' if 'radar_1h' in P else 'ms_1h'
    V = g['V']; dlat = abs(float(g['lat'][1] - g['lat'][0])); dlon = abs(float(g['lon'][1] - g['lon'][0]))
    bounds = [[r1(g['lat'].min() - dlat / 2, 4), r1(g['lon'].min() - dlon / 2, 4)], [r1(g['lat'].max() + dlat / 2, 4), r1(g['lon'].max() + dlon / 2, 4)]]
    rain_png(V, os.path.join(OUT, 'rain_1h.png'))
    q = np.where(np.isfinite(V), np.rint(np.clip(V, 0, 6000) * 10), -1).astype(int)
    json.dump(dict(made=iso(now), product=out['products'][gk]['product'], valid=out['products'][gk]['valid'], bounds_latlon=bounds, rows='north to south',
                   shape=list(V.shape), scale=0.1, missing=-1, units='mm', data=q.tolist()), open(os.path.join(OUT, 'rain_grid.json'), 'w'), separators=(',', ':'))
    out['grid'] = dict(png='rain_1h.png', json='rain_grid.json', product=out['products'][gk]['product'], bounds_latlon=bounds,
                       ramp_mm=[[th, '#%02x%02x%02x' % c] for th, c in RAMP])
    m1 = max([v for v in (out['products'].get('radar_1h', {}).get('district_max'), out['products'].get('ms_1h', {}).get('district_max')) if v is not None] or [0])
    m3 = max([v for v in (out['products'].get('radar_3h', {}).get('district_max'), out['products'].get('ms_3h', {}).get('district_max')) if v is not None] or [0])
    lvl = sum(m1 >= t for t in RAIN_LEVELS); out['level'] = lvl; out['max_1h'] = m1; out['max_3h'] = m3
    material = dict(m1=round(m1), m3=round(m3), wet=sorted(t[0] for t in out['towns'] if (t[1] or 0) >= 2.5 or (t[4] or 0) >= 2.5))
    return out, material, dict(rain_level=lvl)


# ------------------------------------------------------------------------------------------------ 2. nowcast (experimental)
NC_LAT, NC_LON = (LAT[0] - 1.5, LAT[1] + 1.5), (LON[0] - 2.2, LON[1] + 1.2)    # upstream margin: 2 h at ~80 km/h from the W / SW
STEP_MIN, NSTEP = 10, 12


def phase_shift(a, b):
    """(dy, dx, peak): b ~ a shifted by (+dy, +dx) pixels (phase correlation, Hann window, parabolic sub-pixel)."""
    w = np.outer(np.hanning(a.shape[0]), np.hanning(a.shape[1]))
    A = np.fft.fft2(a * w); B = np.fft.fft2(b * w); R = B * np.conj(A); R /= np.abs(R) + 1e-9
    r = np.fft.ifft2(R).real; i, j = np.unravel_index(int(np.argmax(r)), r.shape); ny, nx = r.shape

    def sub(c, m, p):
        d = m - 2 * c + p
        return 0.0 if abs(d) < 1e-12 else 0.5 * (m - p) / d
    dy = i + sub(r[i, j], r[(i - 1) % ny, j], r[(i + 1) % ny, j]); dx = j + sub(r[i, j], r[i, (j - 1) % nx], r[i, (j + 1) % nx])
    if dy > ny / 2: dy -= ny
    if dx > nx / 2: dx -= nx
    return float(dy), float(dx), float(r[i, j])


def advect_phase(frames):
    from scipy import ndimage
    a, b = np.log1p(frames[-2]), np.log1p(frames[-1]); dy, dx, pk = phase_shift(a, b)
    if len(frames) >= 3:
        dy0, dx0, pk0 = phase_shift(np.log1p(frames[-3]), a); dy, dx = (dy + dy0) / 2, (dx + dx0) / 2
    if math.hypot(dy, dx) > 30: dy = dx = 0.0          # > 180 km/h: not a motion, fall back to persistence
    F = np.stack([ndimage.shift(frames[-1], (dy * k, dx * k), order=1, mode='constant', cval=0.0) for k in range(1, NSTEP + 1)])
    return F, (dy, dx), 'phase correlation (one uniform motion vector), linear advection, no growth/decay'


def advect_pysteps(frames):
    from pysteps import motion
    from pysteps.extrapolation import semilagrangian
    from pysteps.utils import transformation
    R = np.stack(frames); Rdb, _ = transformation.dB_transform(R.copy(), threshold=0.1, zerovalue=-15.0)
    V = motion.get_method('LK')(Rdb)
    F = semilagrangian.extrapolate(frames[-1], V, NSTEP); F = np.nan_to_num(np.asarray(F), nan=0.0)
    wet = frames[-1] > 0.5
    v = (float(np.mean(V[1][wet])) if wet.any() else float(np.mean(V[1])), float(np.mean(V[0][wet])) if wet.any() else float(np.mean(V[0])))
    return F, v, 'pysteps Lucas-Kanade motion field + semi-Lagrangian extrapolation (no growth/decay)'


def feed_nowcast(now=None, method=None):
    now = now or utcnow(); L = mrms_recent('PrecipRate_00.00', now - dt.timedelta(minutes=40), now)
    if not L: raise RuntimeError('no PrecipRate files in the last 40 min')
    t0, u0 = L[-1]; want = [t0 - dt.timedelta(minutes=STEP_MIN * k) for k in (2, 1)]; pick = []
    for w in want:
        c = min(L, key=lambda x: abs((x[0] - w).total_seconds()))
        if abs((c[0] - w).total_seconds()) <= 120: pick.append(c)
    pick.append((t0, u0))
    if len(pick) < 2: raise RuntimeError('fewer than 2 PrecipRate frames 10 min apart')
    frames, lat, lon = [], None, None
    for t, u in pick:
        V, lat, lon = mrms_box(u, NC_LAT, NC_LON); frames.append(np.nan_to_num(V, nan=0.0))
    dlat = abs(lat[1] - lat[0]); dlon = abs(lon[1] - lon[0])
    out = dict(made=iso(now), made_by='proto/live_feeds.py nowcast', experimental=True, issued=iso(t0), frames=[iso(t) for t, _ in pick],
               skill='UNVERIFIED: no verification against observed rain yet (archived for later scoring). Advection only: storms that form, '
                     'grow or decay in the next 2 h are missed. Treat as a guide to where existing rain is heading, not a forecast.',
               source='NOAA MRMS PrecipRate (2-min, AWS s3://noaa-mrms-pds/CONUS/PrecipRate_00.00/), District 3 + upstream margin')
    if max(f.max() for f in frames) < 0.1:
        F = np.zeros((NSTEP,) + frames[-1].shape, np.float32); vec = (0.0, 0.0); how = 'no rain in the domain'
    else:
        how = None
        if method in (None, 'pysteps'):
            try: F, vec, how = advect_pysteps(frames)
            except Exception as e: out['pysteps_error'] = repr(e)[:200]; log('  nowcast pysteps unavailable:', out['pysteps_error'])
        if how is None: F, vec, how = advect_phase(frames)
    out['method'] = how
    km_y, km_x = dlat * 111.2, dlon * 111.2 * math.cos(math.radians(42.35))
    vx, vy = vec[1] * km_x * 60 / STEP_MIN, -vec[0] * km_y * 60 / STEP_MIN            # km/h, east / north
    out['motion'] = dict(speed_kmh=r1(math.hypot(vx, vy)), toward_deg=r1((math.degrees(math.atan2(vx, vy)) + 360) % 360, 0), east_kmh=r1(vx), north_kmh=r1(vy))
    a1 = F[:NSTEP // 2].sum(0) * STEP_MIN / 60.0; a2 = F.sum(0) * STEP_MIN / 60.0
    i = (lat >= LAT[0]) & (lat <= LAT[1]); j = (lon >= LON[0]) & (lon <= LON[1]); la, lo = lat[i], lon[j]
    T1, (m1, mean1) = town_stats(a1[np.ix_(i, j)], la, lo, ('max', 'mean')); T2, (m2, mean2) = town_stats(a2[np.ix_(i, j)], la, lo, ('max', 'mean'))
    out['valid_to'] = [iso(t0 + dt.timedelta(hours=1)), iso(t0 + dt.timedelta(hours=2))]
    out['district'] = dict(max_0_1h=m1, mean_0_1h=mean1, max_0_2h=m2, mean_0_2h=mean2)
    out['town_fields'] = ['town', 'max_0_1h_mm', 'mean_0_1h_mm', 'max_0_2h_mm', 'mean_0_2h_mm']
    out['towns'] = [[a[0], a[1], a[2], b[1], b[2]] for a, b in zip(T1, T2)]
    lvl = sum((m1 or 0) >= t for t in RAIN_LEVELS); out['level'] = lvl
    if (m2 or 0) >= 1.0: append_archive([dict(id=f'nowcast:{iso(t0)}', src='nowcast', t=iso(t0), method=how, motion=out['motion'], district=out['district'],
                                              towns=[t for t in out['towns'] if (t[3] or 0) >= 1.0])], 'nowcast')
    material = dict(m1=round(m1 or 0), m2=round(m2 or 0), wet=sorted(t[0] for t in out['towns'] if (t[3] or 0) >= 5))
    return out, material, dict(nowcast_level=lvl)


# ------------------------------------------------------------------------------------------------ 3. MRMS FLASH
FLASH = dict(unitq='FLASH_CREST_MAXUNITSTREAMFLOW_00.00', ffg01h='FLASH_QPE_FFG01H_00.00', ffg03h='FLASH_QPE_FFG03H_00.00', ffg06h='FLASH_QPE_FFG06H_00.00')


def feed_flash(now=None):
    now = now or utcnow(); G = {}; err = {}
    for k, prod in FLASH.items():
        try:
            t, u = mrms_latest(prod, 40, now); V, la, lo = mrms_box(u); G[k] = (t, V, la, lo, u)
        except Exception as e: err[k] = repr(e)[:240]; log('  flash', k, err[k])
    if not G: raise RuntimeError('no FLASH product: ' + json.dumps(err)[:400])
    out = dict(made=iso(now), made_by='proto/live_feeds.py flash', errors=err, products={}, thresholds=dict(unitq_m3s_km2=FLASH_UNITQ, qpe_ffg_ratio=FLASH_RATIO),
               source='NOAA MRMS FLASH (CREST hydrologic model; QPE-to-flash-flood-guidance ratios), AWS s3://noaa-mrms-pds/CONUS/FLASH_*')
    per = {}
    for k, (t, V, la, lo, u) in G.items():
        V = np.nan_to_num(V, nan=0.0); T, (mx, mn) = town_stats(V, la, lo, ('max',), d=2)
        out['products'][k] = dict(product=FLASH[k], valid=iso(t), district_max=mx, url=u); per[k] = {x[0]: x[1] for x in T}
    out['town_fields'] = ['town', 'unitq_max', 'ffg01h_ratio_max', 'ffg03h_ratio_max', 'ffg06h_ratio_max']
    out['towns'] = [[n] + [per.get(k, {}).get(n) for k in FLASH] for n, _, _ in towns()]
    out['flagged'] = []
    for t in out['towns']:
        why = []
        if (t[1] or 0) > FLASH_UNITQ: why.append(f'unit streamflow {t[1]} m3/s/km2')
        for k, v in zip(('1h', '3h', '6h'), t[2:]):
            if (v or 0) > FLASH_RATIO: why.append(f'QPE/FFG {k} {v}')
        if why: out['flagged'].append(dict(town=t[0], why=why))
    flagged = sorted(f['town'] for f in out['flagged'])
    material = dict(flagged=flagged, q=round(out['products'].get('unitq', {}).get('district_max') or 0, 1),
                    r=round(max([out['products'].get(k, {}).get('district_max') or 0 for k in ('ffg01h', 'ffg03h', 'ffg06h')]), 1))
    return out, material, dict(flash_towns=flagged)


# ------------------------------------------------------------------------------------------------ 4. NWM short range at culverts
CULVERT_SHAPES = ('circular', 'elliptical', 'pipe_arch', 'box', 'arch_open', 'arch_closed')     # as proto/prototype.py
BLOCKAGE = {'Poor': 0.25, 'Critical': 0.50}                                                      # as proto/prototype.py
Q_SIGMA_LN = 0.30                                                                                # as proto/prototype.py
SNAP_MAX_M = 100.0


def d3_culverts():
    """District 3 crossings with an HDS-5-computable barrel or StreamStats peaks (docs/network/crossings_all.json)."""
    J = json.load(open(os.path.join(ROOT, 'docs', 'network', 'crossings_all.json'))); C = J['columns']; out = []
    for r in J['rows']:
        r = dict(zip(C, r))
        if r.get('d3') != 1: continue
        cap = r.get('shape') in CULVERT_SHAPES and (r.get('rise_m') or 0) > 0 and (r.get('shape') == 'circular' or r.get('span_m'))
        if cap or r.get('pk10'): out.append(r)
    return out


def q_crest(r):
    """Flow (m3/s) the barrel passes when the headwater reaches the road crest (rise + fill; 0.6 m fill when unknown), FHWA HDS-5 via
    sim/infra/culvert.py, NAACC inlet blockage applied -- the same Q_crest as prototype.culvert_probability."""
    sys.path.insert(0, os.path.join(ROOT, 'sim', 'infra')); import culvert as CV
    shape, rise, span = r.get('shape'), r.get('rise_m'), r.get('span_m')
    if shape not in CULVERT_SHAPES or not rise or rise <= 0 or (shape != 'circular' and not span): return None
    fill = r.get('fill_m'); crest = float(rise) + (float(fill) if fill is not None else 0.6); B = BLOCKAGE.get(r.get('inlet_blockage'), 0.0)
    mat, inl, nb = r.get('material') or 'concrete', r.get('inlet') or 'headwall', int(r.get('n_barrels') or 1)
    S = (r.get('slope_pct') or 1.0) / 100.0; L = r.get('length_m') or max(10.0, 2 * crest + 8.0)
    return CV.q_at_headwater(crest, shape, span or rise, rise, mat, inl, S, L, 0.0, nb) * (1.0 - B)


def hav_m(lon1, lat1, lon2, lat2):
    p1, p2 = math.radians(lat1), math.radians(lat2); dl = math.radians(lon2 - lon1)
    a = math.sin((p2 - p1) / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * 6371000 * math.asin(math.sqrt(min(1.0, a)))


def nldi_hydrolocation(lon, lat):
    """(comid, snap distance m, how) of the NHDPlus v2 flowline nearest the point (USGS NLDI hydrolocation; fallback: catchment containing it)."""
    last = None
    for base in NLDI:
        try:
            J = http_get(f'{base}/hydrolocation', params={'coords': f'POINT({lon} {lat})'}, timeout=60, tries=2).json()
            for f in J.get('features', []):
                p = f.get('properties') or {}
                if p.get('comid') and (p.get('source') in (None, 'indexed')):
                    x, y = f['geometry']['coordinates'][:2]
                    return int(p['comid']), round(hav_m(lon, lat, x, y), 1), 'nldi hydrolocation'
        except Exception as e: last = e
        try:
            J = http_get(f'{base}/comid/position', params={'coords': f'POINT({lon} {lat})'}, timeout=60, tries=2).json()
            c = J['features'][0]['properties'].get('comid') or J['features'][0]['properties'].get('identifier')
            if c: return int(c), None, 'nldi comid/position (catchment)'
        except Exception as e: last = e
    raise RuntimeError(repr(last)[:200])


def cmd_map_comids(a=None):
    from concurrent.futures import ThreadPoolExecutor
    X = d3_culverts(); old = json.load(open(COMID_MAP)) if os.path.exists(COMID_MAP) else {'map': {}}
    todo = [r for r in X if r['id'] not in old['map']]; log('culverts', len(X), 'to map', len(todo))
    M = dict(old['map']); errs = 0

    def one(r):
        try: return r['id'], nldi_hydrolocation(r['lon'], r['lat'])
        except Exception as e: return r['id'], e
    with ThreadPoolExecutor(6) as ex:
        for k, (i, res) in enumerate(ex.map(one, todo)):
            if isinstance(res, Exception): errs += 1; log('  fail', i, repr(res)[:160]) if errs < 20 else None; continue
            M[i] = dict(comid=res[0], snap_m=res[1], how=res[2])
            if k % 100 == 0: log('  ', k, i, M[i])
    os.makedirs(os.path.dirname(COMID_MAP), exist_ok=True)
    json.dump(dict(made=iso(utcnow()), made_by='proto/live_feeds.py map-comids', n=len(M), failed=errs,
                   note='crossing id (docs/network/crossings_all.json) -> NHDPlus v2 COMID (= NWM feature_id); snap_m = distance to the indexed '
                        f'flowline point; only snap_m <= {SNAP_MAX_M:.0f} m is used. NHDPlus v2 is 1:100k: small culvert streams are often absent and '
                        'snap to a bigger stream, hence the cut-off.', map=M), open(COMID_MAP, 'w'), indent=0)
    log('mapped', len(M), 'failed', errs)


def nwm_cycle(now):
    """Latest short_range cycle whose 18 channel_rt files are all on AWS: (cycle time, [urls f001..f018])."""
    for h in range(1, 8):
        c = (now - dt.timedelta(hours=h)).replace(minute=0, second=0, microsecond=0)
        pre = f'nwm.{c:%Y%m%d}/short_range/nwm.t{c:%H}z.short_range.channel_rt.f'
        K = sorted(k for k in s3_list(NWM_S3, pre) if k.endswith('.conus.nc'))
        if len(K) >= 18: return c, [f'{NWM_S3}/{k}' for k in K[:18]]
        log('  nwm cycle', iso(c), 'has', len(K), 'channel_rt files')
    raise RuntimeError('no complete NWM short_range cycle in the last 7 h on s3://noaa-nwm-pds')


def nwm_read(url, comids):
    import netCDF4
    raw = http_get(url, timeout=180).content
    with netCDF4.Dataset('mem.nc', memory=raw) as ds:
        fid = np.asarray(ds.variables['feature_id'][:]).astype(np.int64); q = np.ma.filled(ds.variables['streamflow'][:], np.nan).astype(np.float64)
        t = ds.variables['time']; tv = netCDF4.num2date(t[:], t.units)[0]
    o = np.argsort(fid); pos = np.searchsorted(fid[o], comids); pos = np.clip(pos, 0, len(fid) - 1); hit = fid[o][pos] == comids
    v = np.where(hit, q[o][pos], np.nan)
    return dt.datetime(tv.year, tv.month, tv.day, tv.hour, tv.minute), v, len(raw)


def nwps_series(comid):
    """NWPS short_range series for a reach -> (reference time, [(valid time, m3/s)])."""
    J = http_get(NWPS.format(rid=comid), timeout=60, tries=2).json()
    sr = J.get('shortRange') or J.get('short_range') or {}
    s = sr.get('series') if isinstance(sr, dict) else None; s = s or sr
    units = str(s.get('units', '')); f = 0.0283168466 if 'ft' in units.lower() or 'cfs' in units.lower() else 1.0
    pts = [(p.get('validTime'), (p.get('flow') if p.get('flow') is not None else p.get('value')) * f) for p in s.get('data', []) if (p.get('flow') if p.get('flow') is not None else p.get('value')) is not None]
    return s.get('referenceTime'), pts, units, sorted(J)[:8]


def feed_nwm(now=None):
    from concurrent.futures import ThreadPoolExecutor
    now = now or utcnow()
    if not os.path.exists(COMID_MAP): raise RuntimeError('no culvert -> COMID map yet: run `python proto/live_feeds.py map-comids` (workflow input map_comids)')
    M = json.load(open(COMID_MAP))['map']; X = []
    for r in d3_culverts():
        m = M.get(r['id'])
        if not m or (m.get('snap_m') is not None and m['snap_m'] > SNAP_MAX_M) or m.get('snap_m') is None: continue
        r = dict(r, comid=m['comid'], snap_m=m['snap_m'], q_crest=q_crest(r)); X.append(r)
    if not X: raise RuntimeError('no culvert mapped within %.0f m of an NHDPlus flowline' % SNAP_MAX_M)
    comids = np.array(sorted({r['comid'] for r in X}), np.int64); cyc, urls = nwm_cycle(now)
    with ThreadPoolExecutor(6) as ex: R = list(ex.map(lambda u: nwm_read(u, comids), urls))
    T = [t for t, _, _ in R]; Q = np.stack([v for _, v, _ in R])                  # (18, n comids)
    ci = {int(c): k for k, c in enumerate(comids)}; rows = []
    for r in X:
        s = Q[:, ci[r['comid']]]
        if not np.isfinite(s).any(): continue
        k = int(np.nanargmax(s)); qp = float(s[k]); qc = r['q_crest']
        rec = dict(id=r['id'], road=r.get('road'), stream=r.get('stream'), lon=r['lon'], lat=r['lat'], comid=r['comid'], snap_m=r['snap_m'],
                   q_peak=r1(qp, 2), t_peak=iso(T[k]), q_crest=r1(qc, 2) if qc else None)
        if qc:
            rec['ratio'] = r1(qp / max(qc, 1e-6), 2); rec['p_overtop'] = r1(0.5 * (1 + math.erf(math.log(max(qp, 1e-6) / max(qc, 1e-6)) / Q_SIGMA_LN / math.sqrt(2))), 3)
        if r.get('pk10'): rec['pk10'] = r['pk10']; rec['over_pk10'] = qp > r['pk10']
        rows.append(rec)
    cap = [x for x in rows if x.get('q_crest')]; exc = sorted([x for x in cap if x['ratio'] > 1.0], key=lambda x: -x['ratio'])
    out = dict(made=iso(now), made_by='proto/live_feeds.py nwm', cycle=iso(cyc), valid=[iso(T[0]), iso(T[-1])], n_culverts=len(rows), n_with_capacity=len(cap),
               n_reaches=int(len(comids)), mb_downloaded=round(sum(b for _, _, b in R) / 1e6, 1), exceed=exc, top=sorted(cap, key=lambda x: -x['ratio'])[:15],
               over_pk10=[x for x in rows if x.get('over_pk10')],
               method=('NWM v3 short_range channel_rt (18 hourly steps) at the NHDPlus v2 reach nearest each culvert (NLDI, <= %.0f m); peak flow vs '
                       'the HDS-5 flow at which headwater reaches the road crest (sim/infra/culvert.py, NAACC barrel + blockage). The NWM flow is '
                       'the reach-outlet flow (whole reach drainage), usually larger than at the culvert: an upper bound, not a prediction of '
                       'overtopping.' % SNAP_MAX_M),
               source='NOAA National Water Model on AWS (s3://noaa-nwm-pds/nwm.YYYYMMDD/short_range/)')
    chk = (exc or out['top'])[:2]; out['nwps_check'] = []
    for x in chk:
        try:
            ref, pts, units, keys = nwps_series(x['comid']); pk = max((p[1] for p in pts), default=None)
            out['nwps_check'].append(dict(comid=x['comid'], reference=ref, n=len(pts), peak_m3s=r1(pk, 2), s3_peak_m3s=x['q_peak'], units=units))
        except Exception as e: out['nwps_check'].append(dict(comid=x['comid'], error=repr(e)[:200]))
    material = dict(exceed=sorted(x['id'] for x in exc), top=round(out['top'][0]['ratio'], 1) if out['top'] else None)
    return out, material, dict(nwm_exceed=sorted(x['id'] for x in exc))


# ------------------------------------------------------------------------------------------------ 5. SNODAS
def snodas_hdr(txt):
    H = {}
    for line in txt.splitlines():
        if ':' in line: k, v = line.split(':', 1); H[k.strip().lower()] = v.strip()
    return H


def snodas_grid(dat, hdr):
    H = snodas_hdr(hdr)
    nc, nr = int(H.get('number of columns', 6935)), int(H.get('number of rows', 3351))
    x0 = float(H.get('minimum x-axis coordinate', H.get('benchmark x-axis coordinate', -124.733749999998366)))
    y1 = float(H.get('maximum y-axis coordinate', 52.874583333332339)); dx = float(H.get('x-axis resolution', 0.00833333333333333))
    dy = float(H.get('y-axis resolution', dx)); nod = float(H.get('no data value', -9999))
    div = 1.0
    m = re.search(r'/\s*([\d.]+)', H.get('data units', ''))
    if m: div = float(m.group(1))                                   # 'Meters / 1000.000000' -> mm
    sc = float(H.get('scale factor', 1) or 1)
    V = np.frombuffer(dat, '>i2').reshape(nr, nc).astype(np.float32); V[V == nod] = np.nan
    V = V / sc * (1000.0 / div)                                     # -> mm
    lat = y1 - dy * (np.arange(nr) + 0.5); lon = x0 + dx * (np.arange(nc) + 0.5)
    i = (lat >= LAT[0]) & (lat <= LAT[1]); j = (lon >= LON[0]) & (lon <= LON[1])
    return V[np.ix_(i, j)], lat[i], lon[j], H.get('data units', '')


def feed_snow(now=None):
    now = now or utcnow(); last = None
    for back in range(0, 5):
        d = (now - dt.timedelta(days=back)).date(); url = SNODAS.format(d=d)
        try: r = http_get(url, timeout=180, tries=2, ok404=True)
        except Exception as e: last = e; continue
        if r is None: last = HTTPErr(f'HTTP 404 for {url}'); continue
        tf = tarfile.open(fileobj=io.BytesIO(r.content)); N = {m.name: m for m in tf.getmembers()}
        res = {}
        for code, k in (('1036', 'depth'), ('1034', 'swe')):
            dn = next((n for n in N if f'ssmv1{code}' in n and n.endswith('.dat.gz')), None)
            hn = next((n for n in N if f'ssmv1{code}' in n and (n.endswith('.txt.gz') or n.endswith('.hdr.gz'))), None)
            if not dn: continue
            dat = gzip.decompress(tf.extractfile(N[dn]).read()); hdr = gzip.decompress(tf.extractfile(N[hn]).read()).decode('latin-1') if hn else ''
            res[k] = snodas_grid(dat, hdr)
        if 'depth' not in res: last = RuntimeError(f'{url}: no snow-depth (1036) grid in tar ({list(N)[:6]})'); continue
        out = dict(made=iso(now), made_by='proto/live_feeds.py snow', date=d.isoformat(), url=url, units='depth cm, SWE mm',
                   source='NOHRSC SNODAS daily (06 UTC), masked CONUS 30 arc-s, via NSIDC G02158 (https://nsidc.org/data/g02158)')
        V, la, lo, units = res['depth']; T, (mx, mn) = town_stats(V / 10.0, la, lo, ('max', 'mean'))
        out['depth_cm'] = dict(district_max=mx, district_mean=mn, units_raw=units)
        if 'swe' in res:
            S, sla, slo, su = res['swe']; TS, (smx, smn) = town_stats(S, sla, slo, ('max', 'mean')); out['swe_mm'] = dict(district_max=smx, district_mean=smn, units_raw=su)
            sw = {t[0]: t[1:] for t in TS}
        else: sw = {}
        out['town_fields'] = ['town', 'depth_cm_max', 'depth_cm_mean', 'swe_mm_mean']
        out['towns'] = [[t[0], t[1], t[2], (sw.get(t[0]) or [None, None])[1]] for t in T]
        material = dict(date=out['date'], d=round(mn or 0), s=round((out.get('swe_mm') or {}).get('district_mean') or 0))
        return out, material, dict(snow=(mn or 0) >= 1.0)
    raise RuntimeError(f'SNODAS: nothing in the last 5 days: {last!r}'[:300])


# ------------------------------------------------------------------------------------------------ 6. validation feeds (archived, not truth)
FLOOD_RE = re.compile(r'flood|high water|standing water|water on|water over|ponding|washout|washed out|wash out|sinkhole|culvert|drain|catch ?basin|'
                      r'storm ?water|stormwater|puddl|manhole|sewer back', re.I)
CLOSE_RE = re.compile(r'all lanes|road (is )?closed|closed in both|both directions closed|full closure|ramp closed|detour|closed\b.*\bclosed|'
                      r'\d+ of \d+ lane\(s\) affected.*all', re.I)


def archive_ids():
    ids = set(); now = utcnow()
    for m in {now.strftime('%Y-%m'), (now.replace(day=1) - dt.timedelta(days=1)).strftime('%Y-%m')}:
        p = os.path.join(ARCH, f'{m}.jsonl')
        if os.path.exists(p):
            for line in open(p):
                try: ids.add(json.loads(line)['id'])
                except Exception: pass
    return ids


def append_archive(recs, label=''):
    if not recs: return 0
    os.makedirs(ARCH, exist_ok=True); seen = archive_ids(); now = utcnow(); n = 0
    with open(os.path.join(ARCH, f'{now:%Y-%m}.jsonl'), 'a') as f:
        for r in recs:
            if r['id'] in seen: continue
            seen.add(r['id']); f.write(json.dumps(dict(r, archived=iso(now)), separators=(',', ':')) + '\n'); n += 1
    log('  archive', label, 'new', n, 'of', len(recs))
    return n


def massdot_events():
    import xml.etree.ElementTree as ET
    r = http_get(EVENTS, timeout=60)
    root = ET.fromstring(r.content); items = []
    for e in root:
        if not len(list(e)): continue
        d = {}
        for c in e.iter():
            if c is not e and c.text and c.text.strip() and not len(list(c)): d[c.tag.split('}')[-1]] = c.text.strip()
        items.append(d)
    rec = []
    pts = [(i, float(d['PrimaryLongitude']), float(d['PrimaryLatitude'])) for i, d in enumerate(items) if d.get('PrimaryLatitude') and d.get('PrimaryLongitude')]
    T = town_of_points([p[1] for p in pts], [p[2] for p in pts]) if pts else []
    for (i, lo, la), town in zip(pts, T):
        d = items[i]; txt = ' '.join(str(d.get(k, '')) for k in ('EventType', 'EventSubType', 'LocationDescription', 'LaneBlockageDescription'))
        kind = 'flood' if FLOOD_RE.search(txt) else ('closure' if CLOSE_RE.search(txt) else None)
        if not town or not kind: continue
        rec.append(dict(id=f"massdot:{d.get('EventId')}", src='massdot', kind=kind, town=town, lat=round(la, 5), lon=round(lo, 5), t=d.get('EventCreatedDate'),
                        updated=d.get('LastUpdate'), status=d.get('EventStatus'), type=d.get('EventType'), subtype=d.get('EventSubType'),
                        road=d.get('RoadwayName'), summary=(f"{d.get('LocationDescription', '')} | {d.get('LaneBlockageDescription', '')}")[:200]))
    return rec, len(items)


def scf_issues(hours=24):
    now = utcnow(); out = []; p = dict(min_lat=LAT[0], min_lng=LON[0], max_lat=LAT[1], max_lng=LON[1], per_page=100, status='open,acknowledged,closed,archived',
                                       after=(now - dt.timedelta(hours=hours)).strftime('%Y-%m-%dT%H:%M:%SZ'))
    total = 0
    for page in range(1, 11):
        J = http_get(SCF, params=dict(p, page=page), timeout=90, headers={'Accept': 'application/json'}).json(); I = J.get('issues') or []; total += len(I)
        for i in I:
            rt = (i.get('request_type') or {}).get('title') or ''
            if FLOOD_RE.search(f"{rt} {i.get('summary') or ''} {i.get('description') or ''}"): out.append(i)
        if not ((J.get('metadata') or {}).get('pagination') or {}).get('next_page') or not I: break
        time.sleep(0.6)
    T = town_of_points([float(i['lng']) for i in out], [float(i['lat']) for i in out]) if out else []
    rec = [dict(id=f"scf:{i['id']}", src='seeclickfix', kind='flood', town=t, lat=round(float(i['lat']), 5), lon=round(float(i['lng']), 5),
                t=i.get('created_at'), status=i.get('status'), category=(i.get('request_type') or {}).get('title'), summary=(i.get('summary') or '')[:120])
           for i, t in zip(out, T) if t]
    return rec, total


def feed_validation(now=None):
    now = now or utcnow(); out = dict(made=iso(now), made_by='proto/live_feeds.py validation', sources={},
                                      note='Reports archived for later hit / false-alarm scoring of the forecast; not ground truth and not verified.',
                                      attribution={'seeclickfix': 'Issue data (c) SeeClickFix, CC BY-NC-SA 4.0 (https://seeclickfix.com); id, time, location, '
                                                                  'category and a short summary only', 'massdot': 'MassDOT Highway Division roadway events feed '
                                                                  '(https://www.mass.gov/info-details/highway-data-for-developers)'})
    recs, ok = [], 0
    for name, fn in (('massdot', massdot_events), ('seeclickfix', scf_issues)):
        try:
            R, n = fn(); recs += R; ok += 1; out['sources'][name] = dict(state='ok', fetched=n, kept=len(R))
        except Exception as e: out['sources'][name] = dict(state='failed', error=repr(e)[:240]); log('  validation', name, repr(e)[:200])
    if not ok: raise RuntimeError('both validation sources failed: ' + json.dumps(out['sources'])[:400])
    out['new_archived'] = append_archive(recs, 'validation'); cut = now - dt.timedelta(hours=48); recent = []
    p = os.path.join(ARCH, f'{now:%Y-%m}.jsonl')
    if os.path.exists(p):
        for line in open(p):
            x = json.loads(line)
            if x.get('src') in ('massdot', 'seeclickfix') and (x.get('archived') or '') >= iso(cut): recent.append(x)
    out['recent_48h'] = recent[-60:]; out['archive'] = 'docs/proto/live/archive/YYYY-MM.jsonl'
    material = dict(ids=sorted(x['id'] for x in recent))
    return out, material, {}


# ------------------------------------------------------------------------------------------------ run + commit decision
FN = dict(rain=feed_rain, nowcast=feed_nowcast, flash=feed_flash, nwm=feed_nwm, snow=feed_snow, validation=feed_validation)


def digest(x): return hashlib.sha1(json.dumps(x, sort_keys=True, default=str).encode()).hexdigest()[:12]


def decide(prev, cur, now, force=False):
    """(commit?, reason).  Alert signature change -> now; material change -> once the last commit is >= CADENCE_H old; else a heartbeat."""
    if force: return True, 'forced'
    if not prev or not prev.get('committed'): return True, 'first run'
    last = dt.datetime.strptime(prev['committed']['utc'], '%Y-%m-%dT%H:%MZ'); age = (now - last).total_seconds() / 3600
    if digest(prev.get('alerts')) != digest(cur['alerts']): return True, 'alert change'
    if age >= CADENCE_H and digest(prev.get('material')) != digest(cur['material']): return True, f'material change, last commit {age:.1f} h ago'
    if age >= HEARTBEAT_H: return True, f'heartbeat ({age:.0f} h)'
    return False, f'nothing material (last commit {age:.1f} h ago)'


def run(feeds, force=False, gh_out=None):
    os.makedirs(OUT, exist_ok=True); sp = os.path.join(OUT, 'status.json')
    prev = json.load(open(sp)) if os.path.exists(sp) else {}
    now = utcnow(); st = dict(made=iso(now), made_by='proto/live_feeds.py run', doc='docs/proto/live/LIVE_FEEDS.md', feeds={}, alerts={}, material={})
    for name in FEEDS:
        P = (prev.get('feeds') or {}).get(name, {})
        if name not in feeds:
            st['feeds'][name] = P; st['material'][name] = (prev.get('material') or {}).get(name); st['alerts'].update({k: v for k, v in (prev.get('alerts') or {}).items() if k.startswith(name)})
            continue
        t0 = time.time(); log(f'== {name}')
        try:
            out, mat, al = FN[name](now)
            json.dump(out, open(os.path.join(OUT, f'{name}.json'), 'w'), indent=None, separators=(',', ':'))
            st['feeds'][name] = dict(state='ok', last_success=iso(now), last_attempt=iso(now), seconds=round(time.time() - t0, 1), error=None, file=f'{name}.json')
            st['material'][name] = mat; st['alerts'].update(al); log(f'   ok {time.time() - t0:.0f}s', json.dumps(mat)[:300], al)
        except Exception as e:
            traceback.print_exc()
            st['feeds'][name] = dict(state='failed', last_success=P.get('last_success'), last_attempt=iso(now), seconds=round(time.time() - t0, 1),
                                     error=f'{type(e).__name__}: {e}'[:400], file=f'{name}.json' if P.get('last_success') else None)
            st['material'][name] = 'failed'
    st['material']['_states'] = {k: v.get('state') for k, v in st['feeds'].items()}
    c, why = decide(prev, st, now, force)
    st['committed'] = dict(utc=iso(now), reason=why) if c else prev.get('committed')
    json.dump(st, open(sp, 'w'), indent=1)
    log('commit:', c, '-', why)
    if gh_out:
        with open(gh_out, 'a') as f: f.write(f'commit={"true" if c else "false"}\nreason={why}\n')
    return st


# ------------------------------------------------------------------------------------------------ selftest (offline)
def selftest():
    import tempfile
    rng = np.random.default_rng(1); a = np.zeros((120, 160)); a[40:70, 30:60] = 5 + rng.random((30, 30)); a[80:95, 100:130] = 12
    from scipy import ndimage
    b = ndimage.shift(a, (3.0, 7.0), order=1); dy, dx, _ = phase_shift(np.log1p(a), np.log1p(b)); assert abs(dy - 3) < 0.6 and abs(dx - 7) < 0.6, (dy, dx)
    F, v, how = advect_phase([a, b]); assert F.shape[0] == NSTEP and abs(v[1] - 7) < 0.6
    k = int(np.argmax(F[0].sum(0))); assert k > int(np.argmax(b.sum(0))), 'advection moves rain east'
    print('ok   phase correlation recovers a (3, 7) px shift:', round(dy, 2), round(dx, 2))
    # SNODAS reader on a synthetic grid (header in the NSIDC .txt style)
    nr, nc = 200, 300; V = np.full((nr, nc), -9999, '>i2'); V[80:90, 100:120] = 250
    hdr = ('Number of columns: %d\nNumber of rows: %d\nMinimum x-axis coordinate: -73.0\nMaximum y-axis coordinate: 43.5\n'
           'X-axis resolution: 0.01\nY-axis resolution: 0.01\nNo data value: -9999\nData units: Meters / 1000.000000\n') % (nc, nr)
    S, la, lo, u = snodas_grid(V.tobytes(), hdr); assert np.nanmax(S) == 250 and la.max() <= LAT[1] and lo.min() >= LON[0], (np.nanmax(S), la.max(), lo.min())
    print('ok   SNODAS reader: big-endian int16, header geometry, mm units')
    # town index + stats on a 0.01 deg grid over the box
    la = np.round(np.arange(LAT[1], LAT[0], -0.01), 3); lo = np.round(np.arange(LON[0], LON[1], 0.01), 3); G = np.zeros((la.size, lo.size), np.float32)
    T, U = town_index(la, lo); assert len(T) == 73 and U.sum() > 3000, (len(T), U.sum())
    n0, idx = T[0]; G.ravel()[idx] = 30.0; R, (mx, mn) = town_stats(G, la, lo, ('max', 'mean')); assert R[0][1] == 30.0 and mx == 30.0
    print('ok   73 District 3 towns indexed on the 0.01 deg grid;', n0, len(idx), 'cells')
    # q_crest: a 0.9 m circular culvert with 1 m fill passes a few m3/s at the crest
    q = q_crest(dict(shape='circular', rise_m=0.9, span_m=0.9, fill_m=1.0, material='concrete', inlet='headwall'))
    assert 0.5 < q < 6, q; print('ok   HDS-5 Q_crest, 0.9 m concrete pipe, 1 m fill:', round(q, 2), 'm3/s')
    # commit decision
    t = dt.datetime(2026, 10, 31, 12, 0); prev = dict(committed=dict(utc='2026-10-31T11:00Z'), alerts=dict(rain_level=0), material=dict(rain=dict(m1=0)))
    assert decide(prev, dict(alerts=dict(rain_level=0), material=dict(rain=dict(m1=3))), t)[0] is False
    assert decide(prev, dict(alerts=dict(rain_level=1), material=dict(rain=dict(m1=12))), t)[0] is True
    assert decide(prev, dict(alerts=dict(rain_level=0), material=dict(rain=dict(m1=3))), t + dt.timedelta(hours=2))[0] is True
    assert decide(prev, dict(alerts=dict(rain_level=0), material=dict(rain=dict(m1=0))), t + dt.timedelta(hours=2))[0] is False
    assert decide(prev, dict(alerts=dict(rain_level=0), material=dict(rain=dict(m1=0))), t + dt.timedelta(hours=24))[0] is True
    print('ok   commit decision: alert change now, material change after 3 h, 24 h heartbeat')
    assert FLOOD_RE.search('Catch Basin / Storm Drain Issue') and FLOOD_RE.search('Flooding') and not FLOOD_RE.search('Pothole')
    assert CLOSE_RE.search('Road closed') and not CLOSE_RE.search('Right 2 lanes closed')
    print('ok   validation keyword filters')
    tmp = tempfile.mkdtemp(); rain_png(G, os.path.join(tmp, 'x.png')); print('ok   rain PNG', os.path.getsize(os.path.join(tmp, 'x.png')), 'bytes')


if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('cmd', choices=list(FEEDS) + ['run', 'map-comids', 'selftest'])
    ap.add_argument('--feeds', default=','.join(FEEDS)); ap.add_argument('--force', action='store_true'); ap.add_argument('--github-output')
    ap.add_argument('--method', choices=['pysteps', 'phase'], help='nowcast motion method (default: pysteps if importable)')
    a = ap.parse_args()
    if a.cmd == 'selftest': selftest()
    elif a.cmd == 'map-comids': cmd_map_comids(a)
    elif a.cmd == 'run': run([f.strip() for f in a.feeds.split(',') if f.strip()], a.force, a.github_output)
    else:
        os.makedirs(OUT, exist_ok=True)
        res = feed_nowcast(method=a.method) if a.cmd == 'nowcast' else FN[a.cmd]()
        json.dump(res[0], open(os.path.join(OUT, f'{a.cmd}.json'), 'w'), separators=(',', ':')); print(json.dumps(res[1])[:500], res[2])
