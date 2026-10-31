"""NOAA National Water Model soil saturation (SOILSAT_TOP) as the antecedent-wetness input (docs/proto/runoff/NWM_AMC.md).

    python proto/runoff/nwm_soilsat.py probe                       # what the archives hold (Actions: network)
    python proto/runoff/nwm_soilsat.py storms [--out docs/proto/runoff/nwm_soilsat.json]
        -> box-mean SOILSAT_TOP at t0 for every District 3 catalogue storm (docs/proto/parity/catalog/*/config.json), from
           (a) the NWM operational analysis (analysis_assim land tm00; Google Cloud national-water-model, then AWS noaa-nwm-pds) and
           (b) the NWM v3.0 retrospective (AWS noaa-nwm-retrospective-3-0-pds, 3-hourly LDASOUT, last step <= t0) where it covers t0.
           The value used by LF_CN_AMC=nwm is `soilsat_top` = (a), else (b) (flagged), else missing.
    python proto/runoff/nwm_soilsat.py clim [--out docs/proto/runoff/nwm_soilsat_clim.json]
        -> District 3 mean SOILSAT_TOP climatology from the retrospective (one 12Z value per day, every year it covers), per day of year,
           +-15-day window: percentiles 5..95 and the sorted sample, so a live value can be given a percentile cheaply.
    python proto/runoff/nwm_soilsat.py live                         # District 3 stats of the latest operational analysis (ground_state 'soil')
    python proto/runoff/nwm_soilsat.py selftest

SOILSAT_TOP: NWM v2.1+/v3 land output, fraction of saturation of the top soil (the upper two Noah-MP layers, 0-40 cm), 1 km, hourly in
the operational analysis.  Box means are over the 1 km cells whose centre falls inside the box (the cell grid is the NWM Lambert grid).
"""
import os, sys, json, time, argparse, datetime as dt
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.normpath(os.path.join(HERE, '..', '..'))
OUT = os.path.join(ROOT, 'docs', 'proto', 'runoff')
OPER = ['https://storage.googleapis.com/national-water-model/nwm.{ymd}/analysis_assim/nwm.t{hh}z.analysis_assim.land.tm00.conus.nc',
        'https://noaa-nwm-pds.s3.amazonaws.com/nwm.{ymd}/analysis_assim/nwm.t{hh}z.analysis_assim.land.tm00.conus.nc']
NOMADS = 'https://nomads.ncep.noaa.gov/pub/data/nccf/com/nwm/prod/nwm.{ymd}/analysis_assim/nwm.t{hh}z.analysis_assim.land.tm00.conus.nc'
RETRO = 'https://noaa-nwm-retrospective-3-0-pds.s3.amazonaws.com'
RETRO_NC = RETRO + '/CONUS/netcdf/LDASOUT/{y}/{ymdh}00.LDASOUT_DOMAIN1'
NWM_LCC = '+proj=lcc +lat_1=30 +lat_2=60 +lat_0=40 +lon_0=-97 +x_0=0 +y_0=0 +a=6370000 +b=6370000 +units=m +no_defs'
D3_LAT, D3_LON = (41.98, 42.75), (-72.25, -71.25)          # the District 3 box of proto/ground_state.py
PCTS = (5, 10, 25, 50, 75, 90, 95)


def log(*a): print(*a, flush=True)


def get(url, timeout=600, tries=3, head=False):
    import requests
    for k in range(tries):
        try:
            r = (requests.head if head else requests.get)(url, timeout=timeout)
            if r.status_code == 200: return r
            if r.status_code in (403, 404): return None
        except Exception as e:
            log('  get', url[-90:], repr(e)[:100])
        time.sleep(5 * (k + 1))
    return None


def s3_list(bucket_url, prefix, delimiter='/', maxkeys=1000):
    """Anonymous S3 ListObjectsV2 -> (prefixes, [(key, size)])."""
    import requests, xml.etree.ElementTree as ET
    r = requests.get(bucket_url, params={'list-type': '2', 'prefix': prefix, 'delimiter': delimiter, 'max-keys': str(maxkeys)}, timeout=120)
    r.raise_for_status(); t = ET.fromstring(r.content); ns = {'s': t.tag.split('}')[0].strip('{')}
    P = [e.text for e in t.findall('s:CommonPrefixes/s:Prefix', ns)]
    K = [(c.find('s:Key', ns).text, int(c.find('s:Size', ns).text)) for c in t.findall('s:Contents', ns)]
    return P, K


# ------------------------------------------------------------------------------------------------ box selection on the NWM grid
def box_xy_26986(box):
    """EPSG:26986 box -> densified boundary points (x, y) in the NWM Lambert grid."""
    from pyproj import Transformer
    tr = Transformer.from_crs('EPSG:26986', NWM_LCC, always_xy=True)
    x0, y0, x1, y1 = box; s = np.linspace(0, 1, 41)
    X = np.r_[x0 + (x1 - x0) * s, np.full(41, x1), x1 - (x1 - x0) * s, np.full(41, x0)]     # counter-clockwise ring
    Y = np.r_[np.full(41, y0), y0 + (y1 - y0) * s, np.full(41, y1), y1 - (y1 - y0) * s]
    return tr.transform(X, Y)


def box_xy_lonlat(lat, lon):
    from pyproj import Transformer
    tr = Transformer.from_crs('EPSG:4326', NWM_LCC, always_xy=True); s = np.linspace(0, 1, 41)
    LO = np.r_[lon[0] + (lon[1] - lon[0]) * s, np.full(41, lon[1]), lon[1] - (lon[1] - lon[0]) * s, np.full(41, lon[0])]
    LA = np.r_[np.full(41, lat[0]), lat[0] + (lat[1] - lat[0]) * s, np.full(41, lat[1]), lat[1] - (lat[1] - lat[0]) * s]
    return tr.transform(LO, LA)


def cell_mask(x, y, bxy):
    """Index slices (iy, ix) of the NWM cells inside the bounding rectangle of the transformed box, plus an inside-polygon mask."""
    from matplotlib.path import Path
    bx, by = np.asarray(bxy[0]), np.asarray(bxy[1])
    ix = np.where((x >= bx.min()) & (x <= bx.max()))[0]; iy = np.where((y >= by.min()) & (y <= by.max()))[0]
    XX, YY = np.meshgrid(x[ix], y[iy]); inside = Path(np.column_stack([bx, by])).contains_points(np.column_stack([XX.ravel(), YY.ravel()])).reshape(XX.shape)
    return slice(iy[0], iy[-1] + 1), slice(ix[0], ix[-1] + 1), inside


def stats(a):
    a = np.asarray(a, np.float64); a = a[np.isfinite(a)]
    if not a.size: return None
    return dict(mean=round(float(a.mean()), 4), n_cells=int(a.size), **{f'p{p}': round(float(np.percentile(a, p)), 4) for p in PCTS})


LAYER_M = (0.1, 0.3)       # Noah-MP layer thicknesses of the top 40 cm (SOILSAT_TOP's depth)


def read_box(content, bxy, var, layer=None):
    """netCDF bytes -> 2-D array of `var` (layer `layer` if it has a soil-layer dimension) on the NWM cells of the box, NaN outside the box
    polygon / missing; plus the window's (x, y) coordinates.  None if the file lacks `var`.  Works for the operational land files and the
    retrospective LDASOUT files (both carry x, y)."""
    import netCDF4
    ds = netCDF4.Dataset('mem.nc', memory=content)
    try:
        if var not in ds.variables: return None, list(ds.variables)
        x = ds['x'][:].astype(np.float64); y = ds['y'][:].astype(np.float64)
        sy, sx, inside = cell_mask(x, y, bxy)
        V = ds[var]; sl = []
        for d in V.dimensions:
            if d == 'y': sl.append(sy)
            elif d == 'x': sl.append(sx)
            elif 'soil' in d: sl.append(layer if layer is not None else 0)
            else: sl.append(0)
        a = np.ma.filled(V[tuple(sl)].astype(np.float64), np.nan)
        a = np.where(inside, a, np.nan); a[(a < 0) | (a > 1.5)] = np.nan
        return (a, x[sx], y[sy]), list(ds.variables)
    finally: ds.close()


def top_water(content, bxy):
    """Thickness-weighted volumetric water of the top 40 cm (m3/m3) from SOIL_M layers 1-2, or None."""
    A, _ = read_box(content, bxy, 'SOIL_M', 0)
    if A is None: return None
    B, _ = read_box(content, bxy, 'SOIL_M', 1)
    return ((LAYER_M[0] * A[0] + LAYER_M[1] * B[0]) / sum(LAYER_M), A[1], A[2])


_CACHE = {}


def operational(t, bxy, urls=OPER, keep=False):
    ymd, hh = t.strftime('%Y%m%d'), t.strftime('%H')
    for u in urls:
        url = u.format(ymd=ymd, hh=hh)
        r = _CACHE.get(url) or get(url)
        if keep and r is not None: _CACHE[url] = r       # the porosity files are reused for every storm box
        if r is None: log('  oper missing', url); continue
        A, names = read_box(r.content, bxy, 'SOILSAT_TOP')
        if A is None: log('  oper: no SOILSAT_TOP in', url, names[:12]); continue
        out = dict(source=url, valid=t.strftime('%Y-%m-%dT%H:%MZ'), mb=round(len(r.content) / 1e6, 1), **(stats(A[0]) or {}))
        if keep: out['_grid'] = A; out['_top_water'] = top_water(r.content, bxy)
        return out
    return None


def porosity(bxy, dates=('2023-09-11T16:00', '2021-07-09T08:00')):
    """Effective porosity of the top 40 cm per NWM cell, from operational files carrying both SOILSAT_TOP and SOIL_M:
    smcmax = top_water / SOILSAT_TOP (SOILSAT_TOP = top-40-cm water / porosity).  Two dates; their agreement is reported (a static soil
    property must come out the same)."""
    P = []
    for d in dates:
        o = operational(dt.datetime.fromisoformat(d), bxy, keep=True)
        if not o or o.get('_top_water') is None: continue
        sat, x, y = o['_grid']; tw = o['_top_water'][0]
        with np.errstate(invalid='ignore', divide='ignore'): P.append((np.where(sat > 0.05, tw / sat, np.nan), x, y))
    if not P: return None, dict(error='no operational file with SOIL_M and SOILSAT_TOP')
    por = np.nanmean([p[0] for p in P], axis=0)
    info = dict(dates=list(dates[:len(P)]), mean=round(float(np.nanmean(por)), 4))
    if len(P) > 1:
        info['max_abs_diff_between_dates'] = round(float(np.nanmax(np.abs(P[0][0] - P[1][0]))), 5)
        info['median_abs_diff_between_dates'] = round(float(np.nanmedian(np.abs(P[0][0] - P[1][0]))), 5)
    return (por, P[0][1], P[0][2]), info


def retro_time(t):
    """Last 3-hourly retrospective step at or before t."""
    return t.replace(hour=(t.hour // 3) * 3, minute=0, second=0, microsecond=0)


def retrospective(t, bxy, por):
    """NWM v3.0 retrospective has no SOILSAT_TOP: rebuild it as top-40-cm SOIL_M water / the operational porosity of the same cells."""
    tr = retro_time(t); url = RETRO_NC.format(y=tr.year, ymdh=tr.strftime('%Y%m%d%H'))
    r = get(url, timeout=900)
    if r is None: return None
    tw = top_water(r.content, bxy)
    if tw is None: return dict(source=url, error='no SOIL_M')
    if por is None: return dict(source=url, error='no porosity')
    if not (np.array_equal(tw[1], por[1]) and np.array_equal(tw[2], por[2])): return dict(source=url, error='grid differs from the operational grid')
    with np.errstate(invalid='ignore', divide='ignore'): sat = np.clip(tw[0] / por[0], 0, 1.2)
    return dict(source=url, valid=tr.strftime('%Y-%m-%dT%H:%MZ'), mb=round(len(r.content) / 1e6, 1),
                method='SOIL_M layers 1-2 (0.1 / 0.3 m weights) / operational porosity of the same cell', **(stats(sat) or {}))


# ------------------------------------------------------------------------------------------------ commands
def catalogue():
    """[(storm, box, hours, t0)] for the District 3 parity catalogue (primary <storm>_<area>_20m runs)."""
    import glob
    cat = {e['id']: e for e in json.load(open(os.path.join(ROOT, 'docs', 'proto', 'obs', 'catalog.json')))['events']}
    sys.path.insert(0, os.path.join(ROOT, 'sim', 'colab'))
    out = []
    for f in sorted(glob.glob(os.path.join(ROOT, 'docs', 'proto', 'parity', 'catalog', '*_20m', 'config.json'))):
        c = json.load(open(f)); s = c['storm']
        t0 = cat[s]['t0'] if s in cat else None
        if t0 is None:
            import w9_lisflood as W; t0 = W.STORMS[s]['t0']
        out.append(dict(storm=s, name=c['name'], box=[int(v) for v in c['box'].split(',')], hours=int(c['hours']), t0=t0))
    return out


def cmd_probe(a):
    import requests
    for pre in ('', 'CONUS/', 'CONUS/netcdf/', 'CONUS/netcdf/LDASOUT/', 'CONUS/netcdf/LDASOUT/2023/', 'CONUS/zarr/'):
        try:
            P, K = s3_list(RETRO, pre); log('== retro', pre or '/', 'prefixes', P[:30], 'keys', K[:8], f'({len(P)} / {len(K)})')
        except Exception as e: log('== retro', pre, 'list failed', repr(e)[:200])
    try:
        P, K = s3_list(RETRO, 'CONUS/netcdf/LDASOUT/2023/', delimiter=''); log('  2023 LDASOUT last keys', K[-5:], len(K))
    except Exception as e: log('  2023 list failed', e)
    r = get(f'{RETRO}/CONUS/zarr/ldasout.zarr/.zmetadata', timeout=120)
    if r is not None:
        M = r.json()['metadata']; arrs = sorted({k.split('/')[0] for k in M if k.endswith('.zarray')}); log('== zarr ldasout arrays', arrs)
        for v in ('SOIL_M', 'SOILSAT_TOP', 'SOILSAT', 'time', 'x', 'y'):
            if f'{v}/.zarray' in M: log('== zarr', v, json.dumps(M[f'{v}/.zarray']), json.dumps(M.get(f'{v}/.zattrs'))[:600])
        r2 = get(f'{RETRO}/CONUS/zarr/ldasout.zarr/time/0', timeout=120); log('== zarr time chunk 0 bytes', None if r2 is None else len(r2.content))
    P, K = s3_list(RETRO, 'CONUS/zarr/ldasout.zarr/SOIL_M/', delimiter='', maxkeys=20); log('== zarr SOIL_M first keys', K[:20])
    # operational land file variables (current, and one from 2019 / 2023)
    for t in (dt.datetime.now(dt.timezone.utc) - dt.timedelta(hours=3), dt.datetime(2023, 9, 11, 16)):
        url = OPER[0].format(ymd=t.strftime('%Y%m%d'), hh=t.strftime('%H')); rr = get(url)
        if rr is None: log('== oper vars missing', url); continue
        import netCDF4
        ds = netCDF4.Dataset('mem.nc', memory=rr.content); log('== oper vars', url, {v: (ds[v].dimensions, getattr(ds[v], 'long_name', ''), getattr(ds[v], 'units', '')) for v in ds.variables}); ds.close()
    # one retrospective netCDF: size and variables
    r = get(RETRO_NC.format(y=2021, ymdh='2021090118'), timeout=900)
    if r is not None:
        import netCDF4
        ds = netCDF4.Dataset('mem.nc', memory=r.content); log('== LDASOUT 2021090118 MB', len(r.content) / 1e6, {v: ds[v].dimensions for v in ds.variables}); ds.close()
    else: log('== LDASOUT 2021090118 missing')
    now = dt.datetime.now(dt.timezone.utc).replace(minute=0, second=0, microsecond=0)
    for h in range(1, 4):
        t = now - dt.timedelta(hours=h); ymd, hh = t.strftime('%Y%m%d'), t.strftime('%H')
        for u in OPER + [NOMADS]:
            url = u.format(ymd=ymd, hh=hh)
            try: rr = requests.head(url, timeout=60); log('== oper', url, rr.status_code, rr.headers.get('content-length'))
            except Exception as e: log('== oper', url, repr(e)[:100])


def cmd_storms(a):
    import pandas as pd
    rows = []; retro_end = a.retro_end
    for c in catalogue():
        t = pd.Timestamp(c['t0']).tz_localize(None).to_pydatetime(); bxy = box_xy_26986(c['box'])
        log(c['storm'], c['t0'], c['box'])
        r = dict(c)
        try: r['operational'] = operational(t, bxy)
        except Exception as e: r['operational'] = dict(error=repr(e)[:200])
        if t <= dt.datetime.fromisoformat(retro_end):
            try:
                por, pinfo = porosity(bxy); r['porosity'] = pinfo; r['retrospective'] = retrospective(t, bxy, por)
            except Exception as e: r['retrospective'] = dict(error=repr(e)[:200])
        else: r['retrospective'] = None
        op, rt = r.get('operational') or {}, r.get('retrospective') or {}
        if op.get('mean') is not None: r.update(soilsat_top=op['mean'], soilsat_source='operational')
        elif rt.get('mean') is not None: r.update(soilsat_top=rt['mean'], soilsat_source='retrospective')
        else: r.update(soilsat_top=None, soilsat_source='missing')
        log('  ->', r['soilsat_top'], r['soilsat_source'], 'oper', op.get('mean'), 'retro', rt.get('mean')); rows.append(r)
    res = dict(made=dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%dT%H:%MZ'), made_by='proto/runoff/nwm_soilsat.py storms',
               variable='SOILSAT_TOP (NWM land output: fraction of saturation, top 0-40 cm), box mean of 1 km cells with centre in the catalogue box',
               rule='soilsat_top = operational analysis_assim land tm00 at t0 (GCS national-water-model, then AWS noaa-nwm-pds); '
                    'else NWM v3.0 retrospective LDASOUT (last 3-hourly step <= t0); else missing',
               retrospective_end=retro_end, storms={r['storm']: r for r in rows})
    json.dump(res, open(a.out, 'w'), indent=1); log('wrote', a.out)
    for r in rows: log(f"{r['storm']:9s} {r['t0']}  used {r['soilsat_top']} ({r['soilsat_source']})  oper {(r.get('operational') or {}).get('mean')}  retro {(r.get('retrospective') or {}).get('mean')}")


ZARR = RETRO + '/CONUS/zarr/ldasout.zarr'


def zarr_chunk(var, key, shape, dtype, attrs=None):
    """One raw zarr v2 chunk (zstd) -> numpy array (scaled; fill -> NaN); all-fill if the chunk object is absent."""
    import zstandard
    r = get(f'{ZARR}/{var}/{key}', timeout=300)
    if r is None: return np.full(shape, np.nan)
    a = np.frombuffer(zstandard.ZstdDecompressor().decompress(r.content, max_output_size=int(np.prod(shape)) * np.dtype(dtype).itemsize), dtype)
    a = a.reshape(shape)
    if attrs is None: return a
    out = a.astype(np.float32); out[a == attrs['fill']] = np.nan
    return out * attrs['scale'] + attrs['offset']


def cmd_clim(a):
    """Daily District 3 mean top-40-cm saturation 1979-2023 from the NWM v3.0 retrospective zarr (SOIL_M layers 1-2, 3-hourly), divided by
    the operational porosity of each cell (porosity()), so it is on the SOILSAT_TOP scale.  ~2300 chunks of < 1 MB."""
    from concurrent.futures import ThreadPoolExecutor
    import pandas as pd
    M = get(f'{ZARR}/.zmetadata', timeout=120).json()['metadata']
    za = M["SOIL_M/.zarray"]; zt = M["SOIL_M/.zattrs"]; ta = M["time/.zattrs"]
    attrs = dict(scale=float(zt.get('scale_factor', 1.0)), offset=float(zt.get('add_offset', 0.0)), fill=int(za['fill_value']))
    nt, ny, nl, nx = za['shape']; ct, cy, cl, cx = za['chunks']
    x = zarr_chunk('x', '0', (nx,), '<f8'); y = zarr_chunk('y', '0', (ny,), '<f8')
    bxy = box_xy_lonlat(D3_LAT, D3_LON); sy, sx, inside = cell_mask(x, y, bxy)
    por, pinfo = porosity(bxy)
    if por is None or not (np.array_equal(por[1], x[sx]) and np.array_equal(por[2], y[sy])): raise SystemExit(f'porosity grid mismatch {pinfo}')
    P = np.where(inside, por[0], np.nan)
    ycs = range(sy.start // cy, (sy.stop - 1) // cy + 1); xcs = range(sx.start // cx, (sx.stop - 1) // cx + 1)
    log('zarr', za['shape'], za['chunks'], 'attrs', attrs, 'y chunks', list(ycs), 'x chunks', list(xcs), 'porosity', pinfo, 'time units', ta.get('units'))
    t_units = ta['units']; t_origin = pd.Timestamp(t_units.split('since')[1].strip())
    nchunks = (nt + ct - 1) // ct
    if a.max_chunks: nchunks = min(nchunks, a.max_chunks)

    def one(k):
        n = min(ct, nt - k * ct)
        try:
            T = zarr_chunk('time', str(k), (n,), '<i8')
            L = []
            for l in (0, 1):      # only the District 3 window is kept (a few MB); each chunk is decoded, cut and dropped
                win = np.full((n, sy.stop - sy.start, sx.stop - sx.start), np.nan, np.float32)
                for yc in ycs:
                    for xc in xcs:
                        c = zarr_chunk('SOIL_M', f'{k}.{yc}.{l}.{xc}', (ct, cy, 1, cx), za['dtype'], attrs)
                        ya, yb = max(sy.start, yc * cy), min(sy.stop, (yc + 1) * cy); xa, xb = max(sx.start, xc * cx), min(sx.stop, (xc + 1) * cx)
                        win[:, ya - sy.start:yb - sy.start, xa - sx.start:xb - sx.start] = c[:n, ya - yc * cy:yb - yc * cy, 0, xa - xc * cx:xb - xc * cx]
                        del c
                L.append(win)
            tw = (LAYER_M[0] * L[0] + LAYER_M[1] * L[1]) / sum(LAYER_M)
            with np.errstate(invalid='ignore', divide='ignore'): sat = np.clip(tw / P[None], 0, 1.2)
            m = np.nanmean(np.where(inside[None], sat, np.nan).reshape(n, -1), axis=1)
            return k, [(t_origin + pd.Timedelta(hours=int(h)), float(v)) for h, v in zip(T, m) if np.isfinite(v)]
        except Exception as e:
            log('  chunk', k, repr(e)[:160]); return k, []
    rows = []; t_ = time.time()
    with ThreadPoolExecutor(a.workers) as ex:
        for i, (k, r) in enumerate(ex.map(one, range(nchunks))):
            rows += r
            if i % 25 == 0: log(f'  chunk {k}/{nchunks} {r[0] if r else None} ({time.time() - t_:.0f} s)')
    S = pd.Series([v for _, v in rows], index=pd.DatetimeIndex([t for t, _ in rows])).sort_index()
    D = S.groupby(S.index.date).mean()
    res = dict(made=dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%dT%H:%MZ'), made_by='proto/runoff/nwm_soilsat.py clim',
               source='NWM v3.0 retrospective (AWS noaa-nwm-retrospective-3-0-pds, CONUS/zarr/ldasout.zarr), SOIL_M layers 1-2 (0.1 / 0.3 m) '
                      '/ operational porosity per cell (= SOILSAT_TOP scale), daily mean of the 3-hourly District 3 box mean '
                      f'(lat {D3_LAT}, lon {D3_LON})', porosity=pinfo, years=f'{D.index[0]}..{D.index[-1]}', n=int(len(D)),
               daily={str(k): round(float(v), 4) for k, v in D.items()})
    json.dump(res, open(a.out, 'w'), indent=0); log('wrote', a.out, len(D), 'days', res['years'])


def clim_percentile(value, when, clim, half_window=15):
    """Percentile (0-100) of `value` among climatology days within +-half_window days of `when`'s day of year (all years)."""
    doy = when.timetuple().tm_yday; xs = []
    for k, v in clim['daily'].items():
        d = dt.date.fromisoformat(k).timetuple().tm_yday; dd = min(abs(d - doy), 365 - abs(d - doy))
        if dd <= half_window: xs.append(v)
    if len(xs) < 20: return None, len(xs), None
    xs = np.sort(xs)
    pct = 100.0 * (np.searchsorted(xs, value, 'left') + np.searchsorted(xs, value, 'right')) / 2 / len(xs)
    return round(float(pct), 1), int(len(xs)), {f'p{p}': round(float(np.percentile(xs, p)), 4) for p in PCTS}


def live(now=None, clim_path=None, log=log):
    """District 3 SOILSAT_TOP from the latest operational analysis (tries the last 6 hours, AWS first: it is the live bucket)."""
    now = now or dt.datetime.now(dt.timezone.utc).replace(tzinfo=None)
    bxy = box_xy_lonlat(D3_LAT, D3_LON); urls = [OPER[1], NOMADS, OPER[0]]
    for h in range(1, 7):
        t = (now - dt.timedelta(hours=h)).replace(minute=0, second=0, microsecond=0)
        r = operational(t, bxy, urls)
        if r is None: continue
        out = dict(state=None, soilsat_top=r['mean'], stats=r, valid_utc=r['valid'], source='NOAA National Water Model v3 operational analysis '
                   '(analysis_assim, land, tm00): SOILSAT_TOP, fraction of saturation of the top 40 cm of soil, 1 km, District 3 mean')
        cp = clim_path or os.path.join(OUT, 'nwm_soilsat_clim.json')
        if os.path.exists(cp):
            C = json.load(open(cp)); pct, n, ref = clim_percentile(r['mean'], t.date(), C)
            out.update(percentile=pct, clim_n=n, clim_pcts=ref, clim_source=C['source'] + f", {C['years']}, +-15 days of the date",
                       clim_note='Percentile of the operational value among retrospective days; the two runs differ in forcing, so read it as approximate.')
            if pct is not None: out['state'] = 'dry' if pct < 25 else ('wet' if pct > 75 else 'normal')
        return out
    raise RuntimeError('no operational NWM land analysis in the last 6 hours')


def selftest():
    a = np.array([0.2, 0.4, np.nan, 0.6]); s = stats(a); assert s['n_cells'] == 3 and abs(s['mean'] - 0.4) < 1e-9 and s['p50'] == 0.4
    C = dict(daily={(dt.date(2000, 1, 1) + dt.timedelta(days=i)).isoformat(): 0.5 + 0.1 * np.sin(i / 58.0) for i in range(3650)})
    pct, n, ref = clim_percentile(10.0, dt.date(2026, 7, 1), C); assert pct == 100.0 and n > 200, (pct, n)
    pct, n, ref = clim_percentile(-1.0, dt.date(2026, 7, 1), C); assert pct == 0.0
    assert retro_time(dt.datetime(2021, 9, 1, 17)) == dt.datetime(2021, 9, 1, 15)
    try:
        bxy = box_xy_26986([160000, 882000, 180000, 902000]); x = np.arange(1900000, 2050000, 1000.0) + 500; y = np.arange(500000, 650000, 1000.0) + 500
        sy, sx, ins = cell_mask(x, y, bxy); assert 300 < ins.sum() < 500, ins.sum()       # 20 x 20 km -> ~400 1 km cells
    except ImportError: pass
    print('nwm_soilsat selftest ok')


if __name__ == '__main__':
    ap = argparse.ArgumentParser(); sp = ap.add_subparsers(dest='cmd', required=True)
    sp.add_parser('probe'); sp.add_parser('selftest'); sp.add_parser('live')
    p = sp.add_parser('storms'); p.add_argument('--out', default=os.path.join(OUT, 'nwm_soilsat.json')); p.add_argument('--retro-end', default='2023-02-01T00:00')
    p = sp.add_parser('clim'); p.add_argument('--out', default=os.path.join(OUT, 'nwm_soilsat_clim.json'))
    p.add_argument('--max-chunks', type=int, default=0, help='test: only the first N time chunks'); p.add_argument('--workers', type=int, default=6)
    a = ap.parse_args()
    if a.cmd == 'probe': cmd_probe(a)
    elif a.cmd == 'storms': cmd_storms(a)
    elif a.cmd == 'clim': cmd_clim(a)
    elif a.cmd == 'live': print(json.dumps(live(), indent=1))
    else: selftest()
