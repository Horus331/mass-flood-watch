"""Water movement simulation for the map's "Water" tab.

Two scenarios, both on a Web-Mercator grid (so the frames drop straight onto the map) with true-metre cell sizes:
  flash   - Sept 11, 2023 Leominster / Fitchburg storm. USGS 3DEP bare-earth DEM, NOAA MRMS 1-km hourly radar+gauge rain
            (MultiSensor QPE Pass 2), SCS curve-number losses, 2-D local-inertial shallow-water routing (Bates et al. 2010,
            de Almeida & Bates 2013 form, the scheme inside LISFLOOD-FP).
  coastal - Jan 4, 2018 nor'easter. Same DEM and solver; the sea is a boundary that follows the observed Boston tide gauge
            (NOAA 8443970, 6-minute water level, NAVD88), so the water has to flow in over the land and back out with the tide.

Writes docs/sim/<scenario>/fNNN.png (depth, transparent where dry) and docs/sim/<scenario>/meta.json, and updates docs/sim/index.json.
Usage: python sim/water_sim.py flash|coastal
"""
import gzip, io, json, math, os, sys, time
import numpy as np, requests
from PIL import Image

R_EARTH = 6378137.0
G = 9.81
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
OUTROOT = os.path.join(ROOT, 'docs', 'sim')
UA = {'User-Agent': 'mass-flood-watch research map (github.com/Horus331/mass-flood-watch)'}

SCEN = {
    'flash': dict(title='Flash flood · Sept 11, 2023 (Leominster, Fitchburg)', kind='flash',
                  bbox=(-72.02, 42.40, -71.52, 42.66), res=40.0,
                  t0='2023-09-11T17:00Z', hours=40, frame_min=20, manning=0.06, show_m=0.10,
                  f0=30.0, fc=3.0, Fk=40.0, drain=2.0),          # Horton infiltration (mm/h, mm) on ponded water all the time + a light storm-drain sink
    'attleboro': dict(title='Flash flood · Sept 11, 2023 (North Attleborough, Attleboro, Plainville)', kind='flash',
                      bbox=(-71.45, 41.88, -71.20, 42.06), res=30.0,
                      t0='2023-09-11T16:00Z', hours=40, frame_min=20, manning=0.06, show_m=0.10,
                      f0=30.0, fc=3.0, Fk=40.0, drain=2.0),
    'flash_fcst': dict(title='Forecast test · Sept 11, 2023 storm from the NOAA HRRR forecast issued that morning (8 am ET)', kind='flash', source='hrrr', issue='2023-09-11T12:00Z',
                       bbox=(-72.02, 42.40, -71.52, 42.66), res=40.0, hours=30, frame_min=20, manning=0.06, show_m=0.10,
                       f0=30.0, fc=3.0, Fk=40.0, drain=2.0, min_rain_mm=0.0, compare='flash'),
    'forecast': dict(title='Forecast · next 30 hours of NOAA HRRR rain over District 3', kind='flash', source='hrrr',
                     bbox=(-72.35, 41.98, -71.35, 42.74), res=80.0, hours=30, frame_min=30, manning=0.06, show_m=0.10,
                     f0=30.0, fc=3.0, Fk=40.0, drain=2.0, min_rain_mm=20.0),
    'boston': dict(title="Coastal flood · Jan 4, 2018 nor'easter · Boston Harbor (Revere to Quincy)", kind='coastal',
                   bbox=(-71.10, 42.29, -70.95, 42.43), res=15.0,
                   t0='2018-01-04T02:00Z', hours=30, frame_min=15, manning=0.035, show_m=0.05, station='8443970'),
    'southshore': dict(title="Coastal flood · Jan 4, 2018 nor'easter · South Shore (Hull to Marshfield)", kind='coastal',
                       bbox=(-70.94, 42.06, -70.62, 42.31), res=20.0,
                       t0='2018-01-04T02:00Z', hours=30, frame_min=15, manning=0.035, show_m=0.05, station='8443970'),
    'coastal': dict(title="Coastal flood · Jan 4, 2018 nor'easter (Cape Ann to Duxbury, overview)", kind='coastal',
                    bbox=(-71.20, 41.98, -70.56, 42.72), res=60.0,
                    t0='2018-01-04T02:00Z', hours=30, frame_min=15, manning=0.045, show_m=0.05, station='8443970'),
}


def merc(lon, lat):
    return R_EARTH * np.radians(lon), R_EARTH * np.log(np.tan(np.pi / 4 + np.radians(lat) / 2))


def inv_merc_y(y):
    return np.degrees(2 * np.arctan(np.exp(y / R_EARTH)) - np.pi / 2)


def get(url, **kw):
    for k in range(4):
        try:
            r = requests.get(url, headers=UA, timeout=120, **kw)
            if r.status_code == 200:
                return r
            print('  http', r.status_code, url[:120])
        except Exception as e:
            print('  retry', k, e)
        time.sleep(3 + 5 * k)
    raise RuntimeError('download failed: ' + url)


def dem_3dep(bbox, res):
    """3DEP bare earth, resampled by the server onto a Web-Mercator grid whose cells are `res` true metres at mid-latitude."""
    lon0, lat0, lon1, lat1 = bbox
    x0, y0 = merc(lon0, lat0); x1, y1 = merc(lon1, lat1)
    k = 1 / math.cos(math.radians((lat0 + lat1) / 2))          # mercator stretch
    nx = int(round((x1 - x0) / (res * k))); ny = int(round((y1 - y0) / (res * k)))
    import tifffile
    tiles = []
    step = 2000
    Z = np.full((ny, nx), np.nan, np.float32)
    for r0 in range(0, ny, step):
        for c0 in range(0, nx, step):
            r1, c1 = min(ny, r0 + step), min(nx, c0 + step)
            bx0 = x0 + (x1 - x0) * c0 / nx; bx1 = x0 + (x1 - x0) * c1 / nx
            by1 = y1 - (y1 - y0) * r0 / ny; by0 = y1 - (y1 - y0) * r1 / ny
            url = ('https://elevation.nationalmap.gov/arcgis/rest/services/3DEPElevation/ImageServer/exportImage'
                   f'?bbox={bx0},{by0},{bx1},{by1}&bboxSR=3857&imageSR=3857&size={c1 - c0},{r1 - r0}'
                   '&format=tiff&pixelType=F32&noDataInterpretation=esriNoDataMatchAny&interpolation=RSP_BilinearInterpolation&f=image')
            t = tifffile.imread(io.BytesIO(get(url).content)).astype(np.float32)
            if t.ndim == 3:
                t = t[..., 0]
            Z[r0:r1, c0:c1] = t[: r1 - r0, : c1 - c0]
    Z[(Z < -500) | (Z > 3000)] = np.nan
    dx = (x1 - x0) / nx / k
    print(f'DEM {ny}x{nx}, true cell {dx:.1f} m, elev {np.nanmin(Z):.1f}..{np.nanmax(Z):.1f} m, nodata {np.isnan(Z).mean() * 100:.1f}%')
    yc = y1 - (np.arange(ny) + 0.5) * (y1 - y0) / ny; xc = x0 + (np.arange(nx) + 0.5) * (x1 - x0) / nx
    return Z, dx, inv_merc_y(yc), np.degrees(xc / R_EARTH)


def mrms_hour(ts, lats, lons):
    """MRMS MultiSensor QPE 1-h Pass 2 (mm) ending at ts, bilinear onto the grid's lat/lon axes."""
    import pygrib
    from scipy.interpolate import RegularGridInterpolator
    d = ts.strftime('%Y%m%d'); f = ts.strftime('%Y%m%d-%H%M%S')
    url = f'https://noaa-mrms-pds.s3.amazonaws.com/CONUS/MultiSensor_QPE_01H_Pass2_00.00/{d}/MRMS_MultiSensor_QPE_01H_Pass2_00.00_{f}.grib2.gz'
    raw = gzip.decompress(get(url).content)
    open('/tmp/q.grib2', 'wb').write(raw)
    g = pygrib.open('/tmp/q.grib2'); m = g[1]
    la, lo = m.latlons(); v = m.values; g.close()
    v = np.ma.filled(v, 0).astype(np.float32); v[v < 0] = 0
    lat1d = la[:, 0]; lon1d = lo[0, :]; lon1d = np.where(lon1d > 180, lon1d - 360, lon1d)
    i0 = np.searchsorted(-lat1d, -lats.max() - 0.05); i1 = np.searchsorted(-lat1d, -lats.min() + 0.05) + 1
    j0 = np.searchsorted(lon1d, lons.min() - 0.05); j1 = np.searchsorted(lon1d, lons.max() + 0.05) + 1
    sub = v[i0:i1, j0:j1]; sla = lat1d[i0:i1]; slo = lon1d[j0:j1]
    f = RegularGridInterpolator((sla[::-1], slo), sub[::-1], bounds_error=False, fill_value=0)
    LA, LO = np.meshgrid(lats, lons, indexing='ij')
    return f((LA, LO)).astype(np.float32)


def coops(station, t0, t1, product='water_level', datum='NAVD'):
    url = ('https://api.tidesandcurrents.noaa.gov/api/prod/datagetter'
           f'?product={product}&station={station}&begin_date={t0:%Y%m%d %H:%M}&end_date={t1:%Y%m%d %H:%M}'
           f'&datum={datum}&units=metric&time_zone=gmt&format=json&application=mass-flood-watch')
    js = get(url).json()
    if 'data' not in js:
        raise RuntimeError(str(js)[:300])
    import pandas as pd
    s = pd.Series([float(x['v']) if x['v'] not in ('', None) else np.nan for x in js['data']],
                  index=pd.to_datetime([x['t'] for x in js['data']], utc=True))
    return s.interpolate(limit=5)


def datums(station):
    js = get(f'https://api.tidesandcurrents.noaa.gov/mdapi/prod/webapi/stations/{station}/datums.json?units=metric').json()
    d = {x['name']: float(x['value']) for x in js['datums'] if x.get('value') not in (None, '')}
    return {k: d[k] - d['NAVD88'] for k in d if 'NAVD88' in d}      # each datum in NAVD88 metres


HB = 'https://noaa-hrrr-bdp-pds.s3.amazonaws.com'


def hrrr_latest():
    import pandas as pd
    now = pd.Timestamp.now(tz='UTC').tz_localize(None).floor('h')
    for h in range(0, 30):
        t = now - pd.Timedelta(hours=h)
        if t.hour % 6 == 0:
            try:
                if requests.head(f'{HB}/hrrr.{t:%Y%m%d}/conus/hrrr.t{t:%H}z.wrfsfcf36.grib2.idx', timeout=30).status_code == 200:
                    return t
            except Exception:
                pass
    return None


def hrrr_apcp(init, fh):
    import pygrib
    u = f'{HB}/hrrr.{init:%Y%m%d}/conus/hrrr.t{init:%H}z.wrfsfcf{fh:02d}.grib2'
    lines = get(u + '.idx').text.strip().split('\n'); tag = f':APCP:surface:{fh - 1}-{fh} hour acc'
    for i, ln in enumerate(lines):
        if tag in ln:
            st = int(ln.split(':')[1]); en = int(lines[i + 1].split(':')[1]) - 1 if i + 1 < len(lines) else ''
            r = requests.get(u, headers={**UA, 'Range': f'bytes={st}-{en}'}, timeout=120)
            return pygrib.fromstring(r.content)
    return None


class HrrrRegrid:
    """3 km HRRR -> simulation grid, inverse-distance from the 4 nearest HRRR points."""
    def __init__(self, g, lats, lons):
        from scipy.spatial import cKDTree
        HL, HO = g.latlons(); m = (HL > lats.min() - 0.2) & (HL < lats.max() + 0.2) & (HO > lons.min() - 0.2) & (HO < lons.max() + 0.2)
        self.wh = np.where(m.ravel())[0]
        LA, LO = np.meshgrid(lats, lons, indexing='ij'); k = np.cos(np.radians(lats.mean()))
        d, self.i = cKDTree(np.c_[HL.ravel()[self.wh], HO.ravel()[self.wh] * k]).query(np.c_[LA.ravel(), LO.ravel() * k], k=4)
        w = 1 / np.maximum(d, 1e-6) ** 2; self.w = (w / w.sum(1, keepdims=True)).astype(np.float32); self.shape = LA.shape

    def __call__(self, g):
        v = np.ma.filled(g.values, 0).ravel()[self.wh].astype(np.float32)
        return np.maximum((v[self.i] * self.w).sum(1), 0).reshape(self.shape)


def write_dry(out, name, S, issue, mx):
    import pandas as pd
    for f in os.listdir(out):
        p_ = os.path.join(out, f)
        if f.endswith('.png'): os.remove(p_)
    import shutil; shutil.rmtree(os.path.join(out, 'rain'), ignore_errors=True)
    json.dump(dict(id=name, title=S['title'], kind=S['kind'], status='dry', issued=f'{issue:%Y-%m-%d %H}Z' if issue is not None else None,
                   max_rain_mm=round(float(mx), 1), threshold_mm=S['min_rain_mm'], n=0, frames=[],
                   built=pd.Timestamp.now(tz='UTC').strftime('%Y-%m-%d %H:%M UTC')), open(os.path.join(out, 'meta.json'), 'w'))
    print(f'forecast: dry (max {mx:.1f} mm in the next {S["hours"]} h) - no simulation needed')


class LocalInertial:
    """2-D local-inertial shallow water on a regular grid (h at cells, unit-width discharge q on faces)."""

    def __init__(self, z, dx, n, fixed=None):
        self.z = z.astype(np.float32); self.dx = float(dx); self.n2 = float(n) ** 2
        ny, nx = z.shape
        self.h = np.zeros_like(self.z); self.qx = np.zeros((ny, nx - 1), np.float32); self.qy = np.zeros((ny - 1, nx), np.float32)
        self.fixed = fixed                                            # boolean mask of cells held at a given water level (sea)
        self.hmax = np.zeros_like(self.z)
        if fixed is not None:                                         # faces with sea on both sides carry no flux (the sea is a boundary)
            self.ffx = fixed[:, :-1] & fixed[:, 1:]; self.ffy = fixed[:-1, :] & fixed[1:, :]

    def _face(self, q, eta_a, eta_b, z_a, z_b, dt):
        hf = np.maximum(eta_a, eta_b) - np.maximum(z_a, z_b)
        wet = hf > 1e-3
        hf = np.where(wet, hf, 1.0).astype(np.float32)
        s = (eta_b - eta_a) / self.dx
        qn = (q - G * hf * dt * s) / (1 + G * dt * self.n2 * np.abs(q) / hf ** (7.0 / 3.0))
        lim = hf * np.sqrt(G * hf)                                   # cap at Froude 1 for stability on steep ground
        qn = np.clip(qn, -lim, lim)
        return np.where(wet, qn, 0).astype(np.float32)

    def step(self, dt, source=None, level=None):
        z, h = self.z, self.h
        if self.fixed is not None and level is not None:
            h[self.fixed] = np.maximum(level - z[self.fixed], 0)
        eta = z + h
        self.qx = self._face(self.qx, eta[:, :-1], eta[:, 1:], z[:, :-1], z[:, 1:], dt)
        self.qy = self._face(self.qy, eta[:-1, :], eta[1:, :], z[:-1, :], z[1:, :], dt)
        if self.fixed is not None:
            self.qx[self.ffx] = 0; self.qy[self.ffy] = 0
        # keep cells from going negative: scale each cell's outflow to the water it holds
        out = (np.pad(np.maximum(self.qx, 0), ((0, 0), (0, 1))) + np.pad(np.maximum(-self.qx, 0), ((0, 0), (1, 0)))
               + np.pad(np.maximum(self.qy, 0), ((0, 1), (0, 0))) + np.pad(np.maximum(-self.qy, 0), ((1, 0), (0, 0)))) * dt / self.dx
        f = np.where(out > h, h / np.maximum(out, 1e-9), 1.0).astype(np.float32)
        self.qx = np.where(self.qx > 0, self.qx * f[:, :-1], self.qx * f[:, 1:])
        self.qy = np.where(self.qy > 0, self.qy * f[:-1, :], self.qy * f[1:, :])
        div = np.zeros_like(h)
        div[:, :-1] -= self.qx; div[:, 1:] += self.qx; div[:-1, :] -= self.qy; div[1:, :] += self.qy
        h += div * (dt / self.dx)
        if source is not None:
            h += source * dt
        np.maximum(h, 0, out=h)
        if self.fixed is None:                                         # open edges: water leaves the domain
            h[0, :] = h[-1, :] = 0; h[:, 0] = h[:, -1] = 0
        np.maximum(self.hmax, h, out=self.hmax)

    def stable_dt(self, cfl=0.7, cap=20.0):
        hm = float(self.h.max() if self.fixed is None else np.max(np.where(self.fixed, 0, self.h)))
        if self.fixed is not None:                                    # sea cells next to land set the depth over the shore faces
            hm = max(hm, float(np.max(np.where(self.fixed, np.minimum(self.h, 6.0), 0))))
        return min(cap, cfl * self.dx / math.sqrt(G * max(hm, 0.05)))


# --------------------------------------------------------------------- frames
STOPS = [(0.0, (110, 196, 250, 160)), (0.3, (56, 146, 232, 195)), (1.0, (24, 98, 200, 222)), (2.5, (12, 54, 140, 238)), (5.0, (8, 30, 90, 248))]
RAIN_STOPS = [(1.0, (120, 220, 120, 70)), (5.0, (60, 190, 70, 110)), (15.0, (245, 225, 60, 140)), (30.0, (250, 150, 40, 160)), (50.0, (230, 50, 40, 175)), (80.0, (200, 40, 200, 185))]


def to_rgba(depth, show):
    d = np.where(np.isfinite(depth), depth, 0)
    xs = np.array([s[0] for s in STOPS]); cs = np.array([s[1] for s in STOPS], float)
    out = np.zeros(d.shape + (4,), np.uint8)
    m = d >= show
    for c in range(4):
        out[..., c][m] = np.interp(d[m], xs, cs[:, c]).astype(np.uint8)
    return out


def save_png(rgba, path):
    Image.fromarray(rgba, 'RGBA').save(path, optimize=True)


def decode_parts(parts):
    out = []
    for p in parts:
        a = np.cumsum(np.asarray(p, np.int64).reshape(-1, 2), axis=0) / 1e5
        out.append(a)
    return out


def road_samples(kind, bbox):
    """Road points to check for water: District 3 graph segments (flash) or the coastal road points (coastal)."""
    lon0, lat0, lon1, lat1 = bbox
    if kind == 'flash':
        p = os.path.join(ROOT, 'docs', 'graph_segments.json')
        if not os.path.exists(p):
            return None
        G_ = json.load(open(p))
        ids, lo, la = [], [], []
        for i, parts in enumerate(G_['geo']):
            for a in decode_parts(parts):
                sel = (a[:, 0] > lon0) & (a[:, 0] < lon1) & (a[:, 1] > lat0) & (a[:, 1] < lat1)
                if sel.any():
                    ids += [i] * int(sel.sum()); lo += a[sel, 0].tolist(); la += a[sel, 1].tolist()
        return 'graph', np.array(ids), np.array(lo), np.array(la)
    D = json.load(open(os.path.join(ROOT, 'docs', 'data.json')))['coastal_roads']
    la = np.array(D['lat'], float); lo = np.array(D['lon'], float)
    sel = (lo > lon0) & (lo < lon1) & (la > lat0) & (la < lat1)
    return 'coastal', np.where(sel)[0], lo[sel], la[sel]


def run(name):
    import pandas as pd
    S = SCEN[name]; t_start = time.time()
    out = os.path.join(OUTROOT, name); os.makedirs(out, exist_ok=True)
    import shutil
    for f in os.listdir(out):
        if f.endswith('.png'):
            os.remove(os.path.join(out, f))
    shutil.rmtree(os.path.join(out, 'rain'), ignore_errors=True)
    if S.get('source') == 'hrrr':                                      # live forecast: check the rain first, simulate only when heavy rain is coming
        issue = pd.Timestamp(S['issue']).tz_localize(None) if S.get('issue') else hrrr_latest()
        if issue is None:
            write_dry(out, name, S, None, 0.0); return
        lon0_, lat0_, lon1_, lat1_ = S['bbox']; la_ = np.linspace(lat1_, lat0_, 60); lo_ = np.linspace(lon0_, lon1_, 80)
        G1 = {}; tot = 0
        for fh in range(1, S['hours'] + 1):
            g = hrrr_apcp(issue, fh)
            if g is None: break
            G1[fh] = g
        RG0 = HrrrRegrid(next(iter(G1.values())), la_, lo_); tot = sum(RG0(g) for g in G1.values())
        if tot.max() < float(os.environ.get('FORECAST_MIN_MM', S['min_rain_mm'])):
            write_dry(out, name, S, issue, tot.max()); return
        S = dict(S, t0=f'{issue:%Y-%m-%dT%H:%MZ}', title=S['title'] if S.get('issue') else f'Forecast · NOAA HRRR issued {issue:%b %d %H}Z · next {S["hours"]} h over District 3')
    Z, dx, lats, lons = dem_3dep(S['bbox'], S['res'])
    ny, nx = Z.shape
    t0 = pd.Timestamp(S['t0']); nfr = int(S['hours'] * 60 / S['frame_min']) + 1
    frame_t = [t0 + pd.Timedelta(minutes=S['frame_min'] * k) for k in range(nfr)]
    meta_frames = []
    extra = {}
    if S['kind'] == 'flash':
        Z = np.where(np.isnan(Z), np.nanmax(Z), Z)
        sim = LocalInertial(Z, dx, S['manning'])
        hours = [t0 + pd.Timedelta(hours=k + 1) for k in range(S['hours'])]
        RAIN = {}
        if S.get('source') == 'hrrr':
            RG = HrrrRegrid(next(iter(G1.values())), lats, lons)
            for fh, g in G1.items(): RAIN[t0 + pd.Timedelta(hours=fh)] = RG(g)
            hours = []
        for ts in hours:
            try:
                RAIN[ts] = mrms_hour(ts, lats, lons)
            except Exception as e:
                print('  no MRMS for', ts, e); RAIN[ts] = np.zeros((ny, nx), np.float32)
            print(f'  MRMS {ts:%m-%d %H}Z: max {RAIN[ts].max():.0f} mm/h, mean {RAIN[ts].mean():.1f}')
        for ts in [k_ for k_ in RAIN if S.get('source') == 'hrrr']: print(f'  HRRR {ts:%m-%d %H}Z: max {RAIN[ts].max():.0f} mm/h')
        os.makedirs(os.path.join(out, 'rain'), exist_ok=True); rain_frames = []
        xs_ = np.array([q[0] for q in RAIN_STOPS]); cs_ = np.array([q[1] for q in RAIN_STOPS], float)
        for ts, rr_ in RAIN.items():                                     # radar picture of each hour (1 km data, drawn at a third of the grid)
            r3 = rr_[::3, ::3]; img = np.zeros(r3.shape + (4,), np.uint8); mm = r3 >= 1.0
            for c in range(4): img[..., c][mm] = np.interp(r3[mm], xs_, cs_[:, c]).astype(np.uint8)
            fn = f'rain/h{ts:%m%d%H}.png'; save_png(img, os.path.join(out, fn)); rain_frames.append([ts.strftime('%Y-%m-%dT%H:%MZ'), fn])
        tot = sum(RAIN.values()); print(f'storm total max {tot.max():.0f} mm, mean {tot.mean():.0f} mm')
        Finf = np.zeros((ny, nx), np.float32)                          # water soaked in so far (mm), drives the Horton decay
        lost_mm = 0.0
        P = np.zeros((ny, nx), np.float32)
        extra = dict(rain_frames=rain_frames, rain_colors=RAIN_STOPS, rain_total_max_mm=round(float(tot.max())), rain_total_mean_mm=round(float(tot.mean())), infiltration=dict(f0=S['f0'], fc=S['fc'], Fk=S['Fk'], drain=S['drain']))
    else:
        st = S['station']; DT = datums(st)
        lvl = coops(st, t0 - pd.Timedelta(hours=1), t0 + pd.Timedelta(hours=S['hours'] + 1))
        mhhw = DT.get('MHHW', 1.4); print('datums NAVD88 m:', {k: round(v, 2) for k, v in DT.items() if k in ('MHHW', 'MHW', 'MSL', 'MLLW')}, '| peak', lvl.max(), lvl.idxmax())
        nod = np.isnan(Z)
        print('elevation percentiles (valid):', np.nanpercentile(Z, [1, 5, 10, 25, 50]).round(2).tolist())
        from scipy import ndimage
        # sea: no-data, flattened water or below -1 m, connected to the domain edge (keeps inland ponds and low marsh behind dunes out)
        lowsea = nod | (Z < -1.0) | (np.abs(Z) < 0.005)                     # 3DEP open water is hydro-flattened to 0 m (or about -1.6 m)
        lab, nl = ndimage.label(lowsea)
        edge = np.unique(np.r_[lab[0], lab[-1], lab[:, 0], lab[:, -1]]); edge = edge[edge > 0]
        sea = np.isin(lab, edge)
        print(f'sea cells {sea.mean() * 100:.1f}%')
        Z = np.where(nod, -5.0, Z).astype(np.float32)
        Z = np.where(~sea & (Z < -1.0), -1.0, Z).astype(np.float32)          # deep holes not open to the sea (quarries, dredged basins): cap their depth
        print(f'non-sea cells below 0 m: {((~sea) & (Z < 0)).mean() * 100:.1f}%')
        sim = LocalInertial(Z, dx, S['manning'], fixed=sea)
        lvl_t = lambda ts: float(np.interp((ts - lvl.index[0]).total_seconds(), (lvl.index - lvl.index[0]).total_seconds(), lvl.values))
        land = (~sea) & (Z > mhhw)
        # start from the sea at the starting tide: fill low connected ground below that level
        L0 = lvl_t(t0)
        sim.h[sea] = np.maximum(L0 - Z[sea], 0)
        extra = dict(station=st, mhhw_navd_m=round(mhhw, 2), peak_navd_m=round(float(lvl.max()), 2), peak_utc=str(lvl.idxmax()))
    RS = road_samples(S['kind'], S['bbox'])
    if RS:
        rk, rid, rlo, rla = RS
        x_, y_ = merc(rlo, rla); X0, Y0 = merc(S['bbox'][0], S['bbox'][1]); X1, Y1 = merc(S['bbox'][2], S['bbox'][3])
        rc = np.clip(((x_ - X0) / (X1 - X0) * nx).astype(int), 0, nx - 1); rr = np.clip(((Y1 - y_) / (Y1 - Y0) * ny).astype(int), 0, ny - 1)
        road_first = {}; road_peak = {}; road_last = {}
    t = t0; k = 0; steps = 0
    while k < nfr:
        # save frame k when the clock reaches it
        if t >= frame_t[k]:
            d = sim.h.copy()
            if S['kind'] == 'coastal':
                d[~land] = 0
            save_png(to_rgba(d, S['show_m']), os.path.join(out, f'f{k:03d}.png'))
            vis = d >= S['show_m']
            fm = dict(t=frame_t[k].strftime('%Y-%m-%dT%H:%MZ'), wet_km2=round(float(vis.sum()) * dx * dx / 1e6, 2),
                      max_depth_m=round(float(d.max()), 2), deep_km2=round(float((d >= 0.5).sum()) * dx * dx / 1e6, 2))
            if S['kind'] == 'flash':
                hr = frame_t[k].ceil('h') if frame_t[k].ceil('h') in RAIN else None
                fm['rain_mmph'] = round(float(RAIN[hr].mean()), 2) if hr is not None else 0.0
                fm['soaked_mm'] = round(float(Finf.mean()), 1); fm['volume_m3'] = round(float(sim.h.sum()) * dx * dx)
                fm['rain_max_mmph'] = round(float(RAIN[hr].max()), 1) if hr is not None else 0.0
            else:
                fm['level_navd_m'] = round(lvl_t(frame_t[k]), 2)
            if RS:
                dep = d[rr, rc]; on = dep >= 0.3
                ids_on = np.unique(rid[on])
                for i in ids_on.tolist():
                    road_first.setdefault(i, k); road_last[i] = k
                for i, v in zip(rid[on].tolist(), dep[on].tolist()):
                    if v > road_peak.get(i, (0, 0))[0]:
                        road_peak[i] = (round(v, 2), k)
                fm['roads_wet'] = int(len(ids_on))
            meta_frames.append(fm)
            print(f'frame {k:3d} {fm["t"]} wet {fm["wet_km2"]:7.2f} km2  max {fm["max_depth_m"]:5.2f} m  roads {fm.get("roads_wet", "-")}  steps {steps}  ({time.time() - t_start:.0f}s)', flush=True)
            k += 1
            continue
        rem = (frame_t[k] - t).total_seconds()
        if rem < 0.5:                                                   # clock rounding: snap to the frame time
            t = frame_t[k]; continue
        dt = round(min(sim.stable_dt(), rem), 3)
        if S['kind'] == 'flash':
            hr = (t + pd.Timedelta(seconds=1)).ceil('h')
            if hr in RAIN:
                P += RAIN[hr] * (dt / 3600.0)
                sim.step(dt, source=(RAIN[hr] / 3.6e6).astype(np.float32))   # all rain lands; the ground takes its share below
            else:
                sim.step(dt)
            fcap = (S['fc'] + (S['f0'] - S['fc']) * np.exp(-Finf / S['Fk']) + S['drain']) / 3.6e6 * dt   # m this step
            loss = np.minimum(sim.h, fcap); sim.h -= loss; Finf += loss * 1000.0
        else:
            sim.step(dt, level=lvl_t(t))
        t = t + pd.Timedelta(seconds=dt); steps += 1
        if steps % 3000 == 0:
            hh = np.where(sim.fixed, 0, sim.h) if sim.fixed is not None else sim.h; j = int(np.argmax(hh))
            print(f'   step {steps} t {t:%H:%M:%S} dt {dt:.2f}s hmax {hh.flat[j]:.2f} m at row {j // nx} col {j % nx} (z {Z.flat[j]:.2f})', flush=True)
    # max-extent image
    hm = sim.hmax.copy()
    if S['kind'] == 'coastal':
        hm[~land] = 0
    save_png(to_rgba(hm, S['show_m']), os.path.join(out, 'max.png'))
    lon0, lat0, lon1, lat1 = S['bbox']
    meta = dict(id=name, title=S['title'], kind=S['kind'], status='ok', issued=S.get('t0') if S.get('source') == 'hrrr' else None, source=S.get('source', 'mrms'), bounds=[lon0, lat0, lon1, lat1], shape=[ny, nx], cell_m=round(dx, 1),
                frame_min=S['frame_min'], show_m=S['show_m'], frames=meta_frames, n=len(meta_frames), steps=steps,
                runtime_s=round(time.time() - t_start), colors=STOPS, **extra)
    if RS:
        meta['roads'] = dict(kind=rk, first={str(i): v for i, v in road_first.items()}, last={str(i): v for i, v in road_last.items()},
                             peak={str(i): v for i, v in road_peak.items()})
        if rk == 'coastal':
            D = json.load(open(os.path.join(ROOT, 'docs', 'data.json')))['coastal_roads']
            meta['roads']['names'] = {str(i): [D['street'][i] or '', D['town'][i] or ''] for i in road_first}
    if S.get('compare') and RS:                                       # forecast vs the radar-rain run of the same storm: which flooded roads did the forecast catch?
        cp = os.path.join(OUTROOT, S['compare'], 'meta.json')
        if os.path.exists(cp):
            ref = json.load(open(cp)); a_ = set(ref.get('roads', {}).get('first', {})); b_ = set(meta['roads']['first'])
            meta['compare'] = dict(ref=S['compare'], ref_roads=len(a_), fcst_roads=len(b_), both=len(a_ & b_),
                                   caught_share=round(len(a_ & b_) / max(len(a_), 1), 3), false_share=round(len(b_ - a_) / max(len(b_), 1), 3),
                                   ref_peak_km2=max(f['wet_km2'] for f in ref['frames']), fcst_peak_km2=max(f['wet_km2'] for f in meta_frames))
            print('compare:', meta['compare'])
    json.dump(meta, open(os.path.join(out, 'meta.json'), 'w'), separators=(',', ':'))
    print(f'done {name}: {len(meta_frames)} frames, {steps} solver steps, {time.time() - t_start:.0f}s')


if __name__ == '__main__':
    run(sys.argv[1] if len(sys.argv) > 1 else 'flash')
