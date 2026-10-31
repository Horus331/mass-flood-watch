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
import os, sys, io, json, time, argparse, datetime as dt, re
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


def read_soilsat(content, bxy, var='SOILSAT_TOP'):
    """netCDF bytes -> (cell values inside the box, variable list)."""
    import netCDF4
    ds = netCDF4.Dataset('mem.nc', memory=content)
    try:
        names = list(ds.variables)
        if var not in ds.variables: return None, names
        x = ds['x'][:].astype(np.float64); y = ds['y'][:].astype(np.float64)
        sy, sx, inside = cell_mask(x, y, bxy)
        V = ds[var]; sl = tuple(sy if d == 'y' else sx if d == 'x' else 0 for d in V.dimensions)
        a = np.ma.filled(V[sl].astype(np.float64), np.nan)
        if 'south_north' in V.dimensions: raise RuntimeError('unexpected dims ' + str(V.dimensions))
        if y[1] < y[0]: pass   # slices were taken on y as stored; inside mask built on the same order
        a = np.where(inside, a, np.nan); a[(a < 0) | (a > 1.5)] = np.nan
        return a[np.isfinite(a)], names
    finally: ds.close()


def read_ldasout(content, bxy, var='SOILSAT_TOP'):
    """Retrospective LDASOUT (WRF-Hydro, dims time, y, x or time, south_north, west_east; may lack coordinate variables)."""
    import netCDF4
    ds = netCDF4.Dataset('mem.nc', memory=content)
    try:
        names = list(ds.variables)
        if var not in ds.variables: return None, names
        V = ds[var]; dims = V.dimensions
        if 'x' in ds.variables and 'y' in ds.variables:
            x = ds['x'][:].astype(np.float64); y = ds['y'][:].astype(np.float64)
        else:   # the NWM 1 km CONUS land grid: 4608 x 3840, 1000 m, lower-left cell centre (-2303499.25, -1919499.375)
            nx_ = V.shape[dims.index('west_east' if 'west_east' in dims else 'x')]; ny_ = V.shape[dims.index('south_north' if 'south_north' in dims else 'y')]
            x = -2303499.25 + 1000.0 * np.arange(nx_); y = -1919499.375 + 1000.0 * np.arange(ny_)
        sy, sx, inside = cell_mask(x, y, bxy)
        sl = tuple(sy if d in ('y', 'south_north') else sx if d in ('x', 'west_east') else 0 for d in dims)
        a = np.ma.filled(V[sl].astype(np.float64), np.nan)
        a = np.where(inside, a, np.nan); a[(a < 0) | (a > 1.5)] = np.nan
        return a[np.isfinite(a)], names
    finally: ds.close()


def operational(t, bxy, urls=OPER):
    ymd, hh = t.strftime('%Y%m%d'), t.strftime('%H')
    for u in urls:
        url = u.format(ymd=ymd, hh=hh); r = get(url)
        if r is None: log('  oper missing', url); continue
        a, names = read_soilsat(r.content, bxy)
        if a is None: log('  oper: no SOILSAT_TOP in', url, names[:12]); continue
        return dict(source=url, valid=t.strftime('%Y-%m-%dT%H:%MZ'), mb=round(len(r.content) / 1e6, 1), **(stats(a) or {}))
    return None


def retro_time(t):
    """Last 3-hourly retrospective step at or before t."""
    return t.replace(hour=(t.hour // 3) * 3, minute=0, second=0, microsecond=0)


def retrospective(t, bxy):
    tr = retro_time(t); url = RETRO_NC.format(y=tr.year, ymdh=tr.strftime('%Y%m%d%H'))
    r = get(url, timeout=900)
    if r is None: return None
    a, names = read_ldasout(r.content, bxy)
    if a is None: return dict(source=url, error='no SOILSAT_TOP', variables=names[:40])
    return dict(source=url, valid=tr.strftime('%Y-%m-%dT%H:%MZ'), mb=round(len(r.content) / 1e6, 1), **(stats(a) or {}))


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
            try: r['retrospective'] = retrospective(t, bxy)
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


def cmd_clim(a):
    """Climatology of the District 3 mean from the retrospective netCDF (one file per day at 12Z: ~ 365 x years downloads; parallel)."""
    from concurrent.futures import ThreadPoolExecutor
    bxy = box_xy_lonlat(D3_LAT, D3_LON)
    y0, y1 = a.years.split('-'); days = []
    d = dt.date(int(y0), 1, 1)
    while d <= dt.date(int(y1), 12, 31):
        if (d.timetuple().tm_yday - 1) % a.every == 0: days.append(d)
        d += dt.timedelta(days=1)
    def one(day):
        url = RETRO_NC.format(y=day.year, ymdh=day.strftime('%Y%m%d') + '12'); r = get(url, timeout=900)
        if r is None: return day, None
        try:
            v, _ = read_ldasout(r.content, bxy); return day, (float(np.mean(v)) if v is not None and len(v) else None)
        except Exception as e: log('  ', day, repr(e)[:120]); return day, None
    vals = {}
    t_ = time.time()
    with ThreadPoolExecutor(a.workers) as ex:
        for i, (day, v) in enumerate(ex.map(one, days)):
            if v is not None: vals[day.isoformat()] = round(v, 4)
            if i % 100 == 0: log(f'  {i}/{len(days)} {day} {v} ({time.time() - t_:.0f} s)')
    res = dict(made=dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%dT%H:%MZ'), made_by='proto/runoff/nwm_soilsat.py clim',
               source='NWM v3.0 retrospective (AWS noaa-nwm-retrospective-3-0-pds, CONUS/netcdf/LDASOUT), SOILSAT_TOP at 12Z, District 3 box mean '
                      f'(lat {D3_LAT}, lon {D3_LON})', years=a.years, every_days=a.every, n=len(vals), daily=vals)
    json.dump(res, open(a.out, 'w'), indent=0); log('wrote', a.out, len(vals), 'days')


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
    p = sp.add_parser('clim'); p.add_argument('--out', default=os.path.join(OUT, 'nwm_soilsat_clim.json')); p.add_argument('--years', default='1993-2022')
    p.add_argument('--every', type=int, default=1); p.add_argument('--workers', type=int, default=16)
    a = ap.parse_args()
    if a.cmd == 'probe': cmd_probe(a)
    elif a.cmd == 'storms': cmd_storms(a)
    elif a.cmd == 'clim': cmd_clim(a)
    elif a.cmd == 'live': print(json.dumps(live(), indent=1))
    else: selftest()
