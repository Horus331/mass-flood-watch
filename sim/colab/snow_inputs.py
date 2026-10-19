"""Inputs for the snow module (sim/snow.py), fetched over plain HTTPS on Colab/Kaggle.  See docs/research/snow.md.

  hrrr_t2m(ts, lat, lon)       HRRR analysis 2 m air temperature (degC), 3 km, AWS noaa-hrrr-bdp-pds (from 2014-07-30); one byte-range
                               request per hour using the .idx inventory.
  precip_flag_snow(ts, lat, lon)  MRMS PrecipFlag (2-min product, AWS from Oct 2020; Iowa State mtarchive before): 1 where the flag is
                               snow (code 3), 0 for rain types, NaN where there is no precipitation / no coverage (the caller then
                               falls back to temperature).  The file nearest the hour is used (the S3 day listing is read once per day).
  snodas_swe(day, lat, lon)    NOHRSC SNODAS snow water equivalent (mm) at 06 UTC of `day`, 1 km, NSIDC G02158 masked daily tar.
lat and lon are 1-D vectors of the (coarse) grid rows and columns; every function returns an array (len(lat), len(lon)).
"""
import io, gzip, tarfile, re, time, tempfile, os
import numpy as np, requests

UA = {'User-Agent': 'mass-flood-watch research (github.com/Horus331/mass-flood-watch)'}

def _get(url, headers=None, tries=4, timeout=180):
    for k in range(tries):
        try:
            r = requests.get(url, headers=dict(UA, **(headers or {})), timeout=timeout)
            if r.status_code in (200, 206): return r
            if r.status_code == 404: raise FileNotFoundError(url)
        except FileNotFoundError: raise
        except Exception: pass
        time.sleep(3 * (k + 1))
    raise RuntimeError(f'download failed: {url[-80:]}')

def _grib_values(raw):
    import pygrib
    with tempfile.NamedTemporaryFile(suffix='.grib2', delete=False) as f: f.write(raw); p = f.name
    try:
        g = pygrib.open(p); m = g[1]; v = np.ma.filled(m.values, np.nan).astype(np.float32); la, lo = m.latlons(); g.close()
    finally: os.unlink(p)
    lo = np.where(lo > 180, lo - 360, lo); return v, la, lo

# ---------- HRRR 2 m temperature ----------
_HRRR_IDX = {}
def hrrr_t2m(ts, lat, lon):
    url = f'https://noaa-hrrr-bdp-pds.s3.amazonaws.com/hrrr.{ts:%Y%m%d}/conus/hrrr.t{ts:%H}z.wrfsfcf00.grib2'
    lines = _get(url + '.idx').text.strip().split('\n')
    k = next(i for i, l in enumerate(lines) if ':TMP:2 m above ground:' in l)
    b0 = int(lines[k].split(':')[1]); b1 = int(lines[k + 1].split(':')[1]) - 1 if k + 1 < len(lines) else ''
    v, la, lo = _grib_values(_get(url, headers={'Range': f'bytes={b0}-{b1}'}).content)
    key = (len(lat), len(lon), float(lat[0]), float(lon[0]))
    if key not in _HRRR_IDX:      # nearest HRRR cell for every grid cell, computed once (Lambert grid, so a KD-tree on lat/lon)
        from scipy.spatial import cKDTree
        sel = (la > lat.min() - 0.3) & (la < lat.max() + 0.3) & (lo > lon.min() - 0.3) & (lo < lon.max() + 0.3)
        ii = np.flatnonzero(sel.ravel()); tree = cKDTree(np.c_[la.ravel()[ii], lo.ravel()[ii] * np.cos(np.radians(lat.mean()))])
        LA, LO = np.meshgrid(lat, lon, indexing='ij')
        _, j = tree.query(np.c_[LA.ravel(), LO.ravel() * np.cos(np.radians(lat.mean()))]); _HRRR_IDX[key] = ii[j]
    return (v.ravel()[_HRRR_IDX[key]].reshape(len(lat), len(lon)) - 273.15).astype(np.float32)

# ---------- MRMS precipitation phase ----------
_FLAG_LIST = {}
def _flag_keys(day):
    if day in _FLAG_LIST: return _FLAG_LIST[day]
    keys, tok = [], None
    while True:
        u = f'https://noaa-mrms-pds.s3.amazonaws.com/?list-type=2&prefix=CONUS/PrecipFlag_00.00/{day}/' + (f'&continuation-token={requests.utils.quote(tok)}' if tok else '')
        t = _get(u).text; keys += re.findall(r'<Key>([^<]+)</Key>', t)
        m = re.search(r'<NextContinuationToken>([^<]+)</NextContinuationToken>', t)
        if not m: break
        tok = m.group(1)
    _FLAG_LIST[day] = keys; return keys

def precip_flag_snow(ts, lat, lon):
    day = f'{ts:%Y%m%d}'; target = ts.strftime('%Y%m%d-%H%M%S')
    try:
        keys = _flag_keys(day)
        if not keys: raise FileNotFoundError('no AWS listing')
        key = min(keys, key=lambda k: abs(int(k[-22:-16]) - int(target[-6:])) if k[-31:-23] == day else 10 ** 9)
        raw = gzip.decompress(_get('https://noaa-mrms-pds.s3.amazonaws.com/' + key).content)
    except Exception:          # before Oct 2020: Iowa State archive, file at the top of the hour
        raw = gzip.decompress(_get(f'https://mtarchive.geol.iastate.edu/{ts:%Y/%m/%d}/mrms/ncep/PrecipFlag/PrecipFlag_00.00_{target}.grib2.gz').content)
    v, la, lo = _grib_values(raw)
    lat1d, lon1d = la[:, 0], lo[0, :]
    i = np.clip(np.round((lat1d[0] - lat) / (lat1d[0] - lat1d[1])).astype(int), 0, len(lat1d) - 1)
    j = np.clip(np.round((lon - lon1d[0]) / (lon1d[1] - lon1d[0])).astype(int), 0, len(lon1d) - 1)
    f = v[np.ix_(i, j)]
    out = np.full(f.shape, np.nan, np.float32); out[f == 3] = 1.0
    out[np.isin(f, (1, 6, 7, 10, 91, 96))] = 0.0
    return out

# ---------- SNODAS snow water equivalent ----------
SNODAS = dict(ncols=6935, nrows=3351, ulx=-124.72916666666667, uly=52.87083333333333, cell=0.008333333333333333)
def snodas_swe(day, lat, lon):
    mon = day.strftime('%m_%b')
    url = f'https://noaadata.apps.nsidc.org/NOAA/G02158/masked/{day:%Y}/{mon}/SNODAS_{day:%Y%m%d}.tar'
    tf = tarfile.open(fileobj=io.BytesIO(_get(url, timeout=600).content))
    mem = next(m for m in tf.getmembers() if '1034' in m.name and m.name.endswith('.dat.gz'))     # 1034 = snow water equivalent
    a = np.frombuffer(gzip.decompress(tf.extractfile(mem).read()), dtype='>i2').reshape(SNODAS['nrows'], SNODAS['ncols'])
    i = np.clip(np.floor((SNODAS['uly'] + SNODAS['cell'] / 2 - lat) / SNODAS['cell']).astype(int), 0, SNODAS['nrows'] - 1)
    j = np.clip(np.floor((lon - SNODAS['ulx'] + SNODAS['cell'] / 2) / SNODAS['cell']).astype(int), 0, SNODAS['ncols'] - 1)
    s = a[np.ix_(i, j)].astype(np.float32); s[s < 0] = 0          # -9999 = no data; values are mm of water (scale 1)
    return s
