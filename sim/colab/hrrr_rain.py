"""NOAA HRRR forecast rain (hourly APCP buckets) for the flood model and the forecast gate.

The 3 km HRRR (AWS open data, noaa-hrrr-bdp-pds) runs every hour; the 00/06/12/18z cycles go out 48 h (HRRRv4, since 2 Dec 2020;
36 h from Jul 2018, 18 h before), the others 18 h.  Each forecast file wrfsfcfFF.grib2 holds the 1-hour bucket 'APCP:surface:FF-1-FF hour acc',
which is fetched alone by an HTTP byte range read from the file's .idx (~1 MB a field), the same way sim/water_sim.py hrrr_apcp does.

    latest_cycle()                       newest cycle whose last forecast hour is on AWS, preferring the 48 h synoptic cycles
    apcp(init, fh) -> pygrib message     1-hour rain ending at init + fh hours (mm)
    LccGrid(msg)                         HRRR Lambert-conformal geometry; .bilinear(x26986, y26986) -> sampler for the model grid
    hourly(init, hours, sampler)         stack of hourly fields (mm) for forecast hours 1..hours, fetched in parallel; missing hours = None

Hour convention: forecast hour fh covers [init + fh - 1, init + fh), so with T0 = init the model's hour h (sim time [h, h+1)) is fh = h + 1,
exactly like MRMS hour h is the file stamped T0 + h + 1 in w9_lisflood.py.
LF_HRRR_DIR caches the byte-range GRIB messages (stage on a login node, run offline).
"""
import os, time
import numpy as np

HB = 'https://noaa-hrrr-bdp-pds.s3.amazonaws.com'
UA = {'User-Agent': 'mass-flood-watch (WPI student research)'}


def horizon(init):
    """Longest forecast hour of a cycle (HRRRv4 rules; older versions only matter for hindcasts before Dec 2020)."""
    import pandas as pd
    t = pd.Timestamp(init)
    if t.hour % 6 == 0:
        if t >= pd.Timestamp('2020-12-02T12:00'): return 48
        if t >= pd.Timestamp('2018-07-12T12:00'): return 36
    return 18


def _get(url, headers=None, timeout=60, tries=4):
    import requests
    for k in range(tries):
        try:
            r = requests.get(url, headers={**UA, **(headers or {})}, timeout=timeout)
            if r.status_code in (200, 206): return r
            if r.status_code in (403, 404): return None
        except Exception:
            pass
        time.sleep(2 + 3 * k)
    return None


def _head_ok(url):
    import requests
    for k in range(3):
        try: return requests.head(url, headers=UA, timeout=30).status_code == 200
        except Exception: time.sleep(2)
    return False


def url(init, fh):
    import pandas as pd
    t = pd.Timestamp(init)
    return f'{HB}/hrrr.{t:%Y%m%d}/conus/hrrr.t{t:%H}z.wrfsfcf{fh:02d}.grib2'


def latest_cycle(now=None, prefer_long=True, max_back=14):
    """(init, horizon) of the newest cycle complete on AWS.  With prefer_long, the newest 00/06/12/18z cycle with f48 posted wins
    (at most ~8 h old); otherwise / failing that the newest hourly cycle with its f18."""
    import pandas as pd
    now = (pd.Timestamp(now) if now is not None else pd.Timestamp.now(tz='UTC').tz_localize(None)).floor('h')
    if prefer_long:
        for h in range(0, max_back):
            t = now - pd.Timedelta(hours=h)
            if t.hour % 6: continue
            H = horizon(t)
            if _head_ok(url(t, H) + '.idx'): return t, H
    for h in range(0, max_back):
        t = now - pd.Timedelta(hours=h)
        if _head_ok(url(t, 18) + '.idx'): return t, 18
    return None, 0


def apcp(init, fh, cache=None):
    """pygrib message of the 1-hour APCP bucket ending at forecast hour fh, or None if not posted."""
    import pygrib
    cache = cache if cache is not None else os.environ.get('LF_HRRR_DIR')
    u = url(init, fh); cp = os.path.join(cache, f'{os.path.basename(os.path.dirname(os.path.dirname(u)))}_{os.path.basename(u)}.apcp') if cache else None
    if cp and os.path.exists(cp) and os.path.getsize(cp) > 1000:
        return pygrib.fromstring(open(cp, 'rb').read())
    idx = _get(u + '.idx')
    if idx is None: return None
    lines = idx.text.strip().split('\n'); tag = f':APCP:surface:{fh - 1}-{fh} hour acc'
    for i, ln in enumerate(lines):
        if tag in ln:
            st = int(ln.split(':')[1]); en = int(lines[i + 1].split(':')[1]) - 1 if i + 1 < len(lines) else ''
            r = _get(u, headers={'Range': f'bytes={st}-{en}'}, timeout=120)
            if r is None: return None
            if cp: os.makedirs(cache, exist_ok=True); open(cp, 'wb').write(r.content)
            return pygrib.fromstring(r.content)
    return None


def values(msg):
    v = np.ma.filled(msg.values, 0).astype(np.float32); v[~np.isfinite(v)] = 0; v[v < 0] = 0
    return v


class LccGrid:
    """HRRR grid geometry from one message: projected x/y of row 0 / column 0 and the steps, from the message's own lat/lons."""
    def __init__(self, msg):
        from pyproj import Proj
        self.proj = Proj(msg.projparams)
        la, lo = msg.latlons(); self.shape = la.shape
        X, Y = self.proj(lo[[0, 0, 1], [0, 1, 0]], la[[0, 0, 1], [0, 1, 0]])
        self.x0, self.y0 = float(X[0]), float(Y[0]); self.dj = float(X[1] - X[0]); self.di = float(Y[2] - Y[0])
        self.lat, self.lon = la, np.where(lo > 180, lo - 360, lo)

    def frac_index(self, lon, lat):
        x, y = self.proj(lon, lat)
        return (np.asarray(y) - self.y0) / self.di, (np.asarray(x) - self.x0) / self.dj

    def bilinear(self, X26986, Y26986, chunk=2_000_000):
        """Sampler for model cell centres given in EPSG:26986 (2-D arrays): bilinear in the HRRR's own projected plane
        (the regular-grid equivalent of the RegularGridInterpolator w9 uses for the lat/lon MRMS grid)."""
        from pyproj import Transformer
        tr = Transformer.from_crs(26986, 4326, always_xy=True)
        shp = X26986.shape; xf, yf = X26986.ravel(), Y26986.ravel()
        FI = np.empty(xf.size, np.float32); FJ = np.empty(xf.size, np.float32)
        for s in range(0, xf.size, chunk):
            lo, la = tr.transform(xf[s:s + chunk], yf[s:s + chunk]); fi, fj = self.frac_index(lo, la)
            FI[s:s + chunk] = fi; FJ[s:s + chunk] = fj
        ny, nx = self.shape
        i0 = np.clip(np.floor(FI).astype(np.int64), 0, ny - 2); j0 = np.clip(np.floor(FJ).astype(np.int64), 0, nx - 2)
        wi = np.clip(FI - i0, 0, 1).astype(np.float32); wj = np.clip(FJ - j0, 0, 1).astype(np.float32)
        r0, r1, c0, c1 = int(i0.min()), int(i0.max()) + 2, int(j0.min()), int(j0.max()) + 2
        li, lj = (i0 - r0), (j0 - c0); W = (r1 - r0, c1 - c0)
        nb = neighbourhood()

        def sample(msg):
            v = values(msg)
            if nb: v = nb(v, r0, r1, c0, c1)
            else: v = v[r0:r1, c0:c1]
            out = (v[li, lj] * (1 - wi) * (1 - wj) + v[li + 1, lj] * wi * (1 - wj) + v[li, lj + 1] * (1 - wi) * wj + v[li + 1, lj + 1] * wi * wj)
            return np.maximum(out, 0).reshape(shp).astype(np.float32)
        sample.window = dict(rows=[r0, r1], cols=[c0, c1], shape=W, neighbourhood=os.environ.get('LF_HRRR_NBHD') or None)
        return sample


def neighbourhood(spec=None, dx_km=3.0):
    """LF_HRRR_NBHD='R,P': replace each HRRR value by the P-th percentile of the values within R km, every hour, before interpolation
    (the neighbourhood treatment of convection-allowing forecasts, Schwartz & Sobash 2017; refresh/hrrr_replay.py uses 20 km / 90th).
    It spreads a well-forecast but displaced rain core over the area it could plausibly hit.  None when unset."""
    spec = spec if spec is not None else os.environ.get('LF_HRRR_NBHD')
    if not spec: return None
    from scipy import ndimage
    R, P = (float(v) for v in spec.split(',')); k = int(round(R / dx_km)); yy, xx = np.mgrid[-k:k + 1, -k:k + 1]; fp = (yy ** 2 + xx ** 2) <= k * k
    def f(v, r0, r1, c0, c1):
        a0, a1, b0, b1 = max(r0 - k, 0), min(r1 + k, v.shape[0]), max(c0 - k, 0), min(c1 + k, v.shape[1])
        w = ndimage.percentile_filter(v[a0:a1, b0:b1], P, footprint=fp, mode='nearest')
        return w[r0 - a0:r0 - a0 + (r1 - r0), c0 - b0:c0 - b0 + (c1 - c0)]
    return f


def hourly(init, hours, sample=None, workers=12, log=print):
    """Forecast hours 1..hours: list of sampled fields (or raw messages' values when sample is None), missing hours None."""
    from concurrent.futures import ThreadPoolExecutor
    if sample is not None and (os.environ.get('LF_HRRR_LAG') or os.environ.get('LF_HRRR_QMAP')):     # experiments only (hrrr_ens.py, ENSEMBLE.md)
        import hrrr_ens; return hrrr_ens.model_hourly(init, hours, sample, workers=workers, log=log)
    def one(fh):
        for k in range(3):
            try:
                m = apcp(init, fh)
                if m is None: return fh, None
                return fh, (sample(m) if sample else values(m))
            except Exception as e:
                if k == 2: log(f'  HRRR f{fh:02d} failed: {e!r}'[:160])
                time.sleep(3 + 5 * k)
        return fh, None
    out = [None] * hours
    with ThreadPoolExecutor(workers) as ex:
        for fh, v in ex.map(one, range(1, hours + 1)): out[fh - 1] = v
    return out


def parse_init(s):
    """'2023-09-11T12Z', '2023-09-11T12:00Z', '2023091112' -> pandas Timestamp (UTC, naive)."""
    import pandas as pd
    s = s.strip().upper().replace('Z', '')
    if len(s) == 10 and s.isdigit(): s = f'{s[:4]}-{s[4:6]}-{s[6:8]}T{s[8:10]}'
    if len(s) == 13: s += ':00'
    return pd.Timestamp(s).tz_localize(None) if pd.Timestamp(s).tzinfo is None else pd.Timestamp(s).tz_convert('UTC').tz_localize(None)
