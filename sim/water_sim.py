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
                  t0='2023-09-11T14:00Z', hours=17, frame_min=15, manning=0.06, cn=80, show_m=0.15),
    'coastal': dict(title="Coastal flood · Jan 4, 2018 nor'easter (Boston Harbor to the South Shore)", kind='coastal',
                    bbox=(-71.20, 41.98, -70.56, 42.72), res=60.0,
                    t0='2018-01-04T08:00Z', hours=18, frame_min=15, manning=0.045, show_m=0.05, station='8443970'),
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
STOPS = [(0.0, (154, 216, 240, 120)), (0.3, (86, 170, 224, 175)), (1.0, (31, 111, 181, 215)), (2.5, (14, 56, 128, 235)), (5.0, (8, 30, 80, 245))]


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
    for f in os.listdir(out):
        if f.endswith('.png'):
            os.remove(os.path.join(out, f))
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
        for ts in hours:
            try:
                RAIN[ts] = mrms_hour(ts, lats, lons)
            except Exception as e:
                print('  no MRMS for', ts, e); RAIN[ts] = np.zeros((ny, nx), np.float32)
            print(f'  MRMS {ts:%m-%d %H}Z: max {RAIN[ts].max():.0f} mm/h, mean {RAIN[ts].mean():.1f}')
        tot = sum(RAIN.values()); print(f'storm total max {tot.max():.0f} mm, mean {tot.mean():.0f} mm')
        Smax = 25400.0 / S['cn'] - 254.0; Ia = 0.2 * Smax
        Q = lambda P: np.where(P > Ia, (P - Ia) ** 2 / (P + 0.8 * Smax), 0.0)
        P = np.zeros((ny, nx), np.float32)
        extra = dict(rain_total_max_mm=round(float(tot.max())), rain_total_mean_mm=round(float(tot.mean())), curve_number=S['cn'])
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
        dt = min(sim.stable_dt(), (frame_t[k] - t).total_seconds())
        if S['kind'] == 'flash':
            hr = (t + pd.Timedelta(seconds=1)).ceil('h')
            if hr in RAIN:
                dP = RAIN[hr] * (dt / 3600.0)
                src = (Q(P + dP) - Q(P)) / 1000.0 / dt
                P += dP
                sim.step(dt, source=src.astype(np.float32))
            else:
                sim.step(dt)
        else:
            sim.step(dt, level=lvl_t(t))
        t = t + pd.Timedelta(seconds=dt); steps += 1
    # max-extent image
    hm = sim.hmax.copy()
    if S['kind'] == 'coastal':
        hm[~land] = 0
    save_png(to_rgba(hm, S['show_m']), os.path.join(out, 'max.png'))
    lon0, lat0, lon1, lat1 = S['bbox']
    meta = dict(id=name, title=S['title'], kind=S['kind'], bounds=[lon0, lat0, lon1, lat1], shape=[ny, nx], cell_m=round(dx, 1),
                frame_min=S['frame_min'], show_m=S['show_m'], frames=meta_frames, n=len(meta_frames), steps=steps,
                runtime_s=round(time.time() - t_start), colors=STOPS, **extra)
    if RS:
        meta['roads'] = dict(kind=rk, first={str(i): v for i, v in road_first.items()}, last={str(i): v for i, v in road_last.items()},
                             peak={str(i): v for i, v in road_peak.items()})
        if rk == 'coastal':
            D = json.load(open(os.path.join(ROOT, 'docs', 'data.json')))['coastal_roads']
            meta['roads']['names'] = {str(i): [D['street'][i] or '', D['town'][i] or ''] for i in road_first}
    json.dump(meta, open(os.path.join(out, 'meta.json'), 'w'), separators=(',', ':'))
    print(f'done {name}: {len(meta_frames)} frames, {steps} solver steps, {time.time() - t_start:.0f}s')


if __name__ == '__main__':
    run(sys.argv[1] if len(sys.argv) > 1 else 'flash')
