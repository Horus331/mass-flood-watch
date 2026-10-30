"""7-day storm OUTLOOK for MassDOT District 3 (Live tab): daily rain, WPC Excessive Rainfall Outlook, NWS alerts, storm verdicts, health.

    python proto/outlook.py fetch --out raw.json                      # the network part (NBM or GFS rain, WPC ERO days 1-5, NWS alerts)
    python proto/outlook.py build --raw raw.json --status docs/site/data/forecast_status.json --out docs/site/data/outlook.json
                                  [--prev docs/site/data/outlook.json] [--workflow .github/workflows/forecast.yml]
    python proto/outlook.py run   --out outlook.json [--status ...]   # fetch + build in one go (manual test workflow)
    python proto/outlook.py selftest

The flood model (proto/forecast.py, forecast.yml) only looks 48 h ahead on the HRRR.  This outlook looks 7 local days ahead, rain only:
  rain   NOAA NBM (National Blend of Models, 2.5 km, AWS noaa-nbm-grib2-pds) deterministic QPF in 6 h buckets; fallback GFS 0.25 deg APCP
         (AWS noaa-gfs-bdp-pds).  Per District 3 town the maximum over the grid points inside it (nearest point for small towns), as the gate.
  ERO    NWS WPC Excessive Rainfall Outlook days 1-5 (GeoJSON; fallback the NOAA mapservices wpc_precip_hazards MapServer), highest category
         touching a District 3 town.
  alerts api.weather.gov active alerts for MA touching a District 3 town (any event; flood-related ones flagged).
Schema, verdict rules and caveats: docs/proto/forecast/OUTLOOK.md.  Written by forecast.yml in the same commit as forecast_status.json.
"""
import os, sys, re, json, time, argparse, datetime as dt
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.normpath(os.path.join(HERE, '..'))
sys.path.insert(0, HERE)

SCHEMA = 'outlook/1'
TZ = 'America/New_York'
NDAYS = 7
GATE_6H_MM = float(os.environ.get('GATE_6H_MM', '25'))       # the flood-model gate (proto/forecast.py, GATE.md)
GATE_24H_MM = float(os.environ.get('GATE_24H_MM', '40'))
RAIN_MM = 10.0        # town-max daily total from which a day counts as a rain day (storm day)
LIGHT_MM = 2.0        # below: quiet
STALE_H = 7.0         # the viewer calls the outlook stale when it is older than this (6 h cycle + Actions delay)
UA = {'User-Agent': 'mass-flood-watch research (github.com/Horus331/mass-flood-watch)', 'Accept': 'application/geo+json, application/json, */*'}
NBM = 'https://noaa-nbm-grib2-pds.s3.amazonaws.com'
GFS = 'https://noaa-gfs-bdp-pds.s3.amazonaws.com'
ERO_GEOJSON = 'https://www.wpc.ncep.noaa.gov/exper/eromap/geojson/Day{n}_Latest.geojson'
ERO_MAPSERVER = 'https://mapservices.weather.noaa.gov/vector/rest/services/hazards/wpc_precip_hazards/MapServer'
ERO_LEVELS = ['none', 'marginal', 'slight', 'moderate', 'high']
FLOOD_WORDS = ('flood', 'hurricane', 'tropical storm', 'excessive rain')


def log(*a): print(*a, flush=True, file=sys.stderr)


def utcnow(): return dt.datetime.now(dt.timezone.utc).replace(microsecond=0, tzinfo=None)


def iso(d): return None if d is None else d.strftime('%Y-%m-%dT%H:%MZ')


def parse_utc(s):
    if not s: return None
    try:
        d = dt.datetime.fromisoformat(str(s).replace('Z', '+00:00'))
    except ValueError:
        return None
    return d.astimezone(dt.timezone.utc).replace(tzinfo=None) if d.tzinfo else d


def tz():
    from zoneinfo import ZoneInfo
    return ZoneInfo(TZ)


def to_local(d): return d.replace(tzinfo=dt.timezone.utc).astimezone(tz())


def local_midnight_utc(date):
    """UTC (naive) of local midnight starting `date`."""
    return dt.datetime(date.year, date.month, date.day, tzinfo=tz()).astimezone(dt.timezone.utc).replace(tzinfo=None)


def http(url, params=None, headers=None, timeout=60, tries=3, method='GET'):
    import requests
    for k in range(tries):
        try:
            r = requests.request(method, url, params=params, headers={**UA, **(headers or {})}, timeout=timeout)
            if r.status_code in (200, 206): return r
            if r.status_code in (400, 403, 404): return None
            log('  HTTP', r.status_code, url[:140])
        except Exception as e:
            log('  error', url[:140], repr(e)[:160])
        time.sleep(2 + 3 * k)
    return None


# ------------------------------------------------------------------ District 3 points on a model grid
class Points:
    """Grid points around District 3 and the town each belongs to (as proto/forecast.Gate: points inside a town polygon, else the nearest)."""
    def __init__(self, lat, lon, towns=None):
        from matplotlib.path import Path
        import forecast as FC
        lon = np.where(lon > 180, lon - 360, lon)
        towns = towns or FC.d3_towns(); self.names = [n.title() for n, _, _ in towns]
        allx = np.concatenate([r[:, 0] for _, _, rr in towns for r in rr]); ally = np.concatenate([r[:, 1] for _, _, rr in towns for r in rr])
        pad = 0.3
        m = (lat > ally.min() - pad) & (lat < ally.max() + pad) & (lon > allx.min() - pad) & (lon < allx.max() + pad)
        self.mask = m; P = np.c_[lon[m], lat[m]]; self.lon, self.lat = P[:, 0], P[:, 1]
        self.town_pts = []; inside = np.zeros(len(P), bool); owner = np.full(len(P), -1)
        for i, (n, lab, rings) in enumerate(towns):
            k = np.zeros(len(P), bool)
            for r in rings: k |= Path(r).contains_points(P)
            idx = np.nonzero(k)[0]
            if not len(idx): idx = np.array([int(np.argmin((P[:, 0] - lab[0]) ** 2 + (P[:, 1] - lab[1]) ** 2))])
            self.town_pts.append(idx); inside[idx] = True; owner[idx] = np.where(owner[idx] < 0, i, owner[idx])
        self.inside = inside; self.owner = owner

    def cut(self, v): return np.asarray(v)[self.mask].astype(np.float32)

    def town_max(self, v):
        """v (n points) -> per-town maxima (n towns)."""
        return np.array([float(v[idx].max()) for idx in self.town_pts])


# ------------------------------------------------------------------ GRIB QPF (NBM / GFS) by byte ranges
ACC = re.compile(r'^(\d+)-(\d+) (hour|day) acc')


class Grib:
    """One model cycle on AWS: .idx inventories and byte-range reads of the deterministic APCP buckets."""
    def __init__(self, name, init):
        self.name, self.init = name, init; self._idx = {}; self._fields = {}; self.points = None; self.files = set()

    def url(self, fh):
        t = self.init
        if self.name == 'NBM': return f'{NBM}/blend.{t:%Y%m%d}/{t:%H}/core/blend.t{t:%H}z.core.f{fh:03d}.co.grib2'
        return f'{GFS}/gfs.{t:%Y%m%d}/{t:%H}/atmos/gfs.t{t:%H}z.pgrb2.0p25.f{fh:03d}'

    def idx(self, fh):
        """{(a, b) hours: (start byte, end byte or '')} of the deterministic APCP buckets in file fh."""
        if fh in self._idx: return self._idx[fh]
        r = http(self.url(fh) + '.idx', timeout=60); out = {}
        if r is not None:
            L = [ln.split(':') for ln in r.text.strip().split('\n') if ln.count(':') >= 5]
            for i, p in enumerate(L):
                if p[3] != 'APCP' or p[4] != 'surface': continue
                m = ACC.match(p[5])
                if not m: continue
                extra = ':'.join(p[6:]).strip(': ').lower()
                if extra and any(w in extra for w in ('prob', 'std', '%', 'perc', 'ens')): continue
                f = 24 if m.group(3) == 'day' else 1; a, b = int(m.group(1)) * f, int(m.group(2)) * f
                st = int(p[1]); en = next((int(q[1]) - 1 for q in L[i + 1:] if int(q[1]) > st), '')
                if (a, b) not in out or not extra: out[(a, b)] = (st, en)
        self._idx[fh] = out
        return out

    def field(self, a, b):
        """Rain (mm) from init + a to init + b h on the District 3 points, from the files' buckets (recursively split), or None."""
        if (a, b) in self._fields: return self._fields[(a, b)]
        inv = self.idx(b); v = None
        cs = sorted(c for (c, e) in inv if e == b and c >= a)          # the longest bucket ending at b that starts at or after a
        if cs:
            c = cs[0]; st, en = inv[(c, b)]
            r = http(self.url(b), headers={'Range': f'bytes={st}-{en}'}, timeout=180)
            if r is not None:
                import pygrib
                msg = pygrib.fromstring(r.content)
                if self.points is None:
                    la, lo = msg.latlons(); self.points = Points(la, lo)
                x = np.ma.filled(msg.values, 0).astype(np.float32); x[~np.isfinite(x)] = 0; x[x < 0] = 0
                v = self.points.cut(x); self.files.add(b)
                if c > a:
                    w = self.field(a, c); v = None if w is None else v + w
        self._fields[(a, b)] = v
        return v


def find_cycle(name, now, need_fh=168, back_h=30):
    """Newest cycle of the model whose f<need_fh> is posted (NBM: any hour; GFS: 00/06/12/18z)."""
    for h in range(0, back_h + 1):
        t = (now - dt.timedelta(hours=h)).replace(minute=0, second=0)
        if name == 'GFS' and t.hour % 6: continue
        g = Grib(name, t)
        r = http(g.url(need_fh) + '.idx', timeout=30, tries=2, method='HEAD')
        if r is not None: return g
    return None


def fetch_rain(now, model=None):
    """6 h buckets of rain on the District 3 points from the newest NBM cycle (fallback GFS) out to the end of local day 7."""
    from concurrent.futures import ThreadPoolExecutor
    end = local_midnight_utc(to_local(now).date() + dt.timedelta(days=NDAYS))
    errs = []
    for name in ([model] if model else ['NBM', 'GFS']):
        try:
            g = find_cycle(name, now)
            if g is None: errs.append(f'{name}: no cycle with f168 in the last 30 h'); continue
            log(f'{name} cycle {g.init:%Y-%m-%d %H}z')
            # bucket ends: 6-hourly at 00/06/12/18z valid time (a whole number of 6 h after the first synoptic hour after init)
            first = 6 - (g.init.hour % 6) if g.init.hour % 6 else 6
            ends = [fh for fh in range(first, 265, 6) if g.init + dt.timedelta(hours=fh - 6) < end]
            with ThreadPoolExecutor(8) as ex: list(ex.map(g.idx, ends))
            starts = [max(0, e - 6) for e in ends]
            g.field(starts[0], ends[0])                                   # sets up the points serially once
            with ThreadPoolExecutor(6) as ex: F = list(ex.map(lambda ab: g.field(*ab), zip(starts, ends)))
            ok = [(a, b, v) for a, b, v in zip(starts, ends, F) if v is not None]
            if len(ok) < 8: errs.append(f'{name} {g.init:%Y-%m-%dT%H}Z: only {len(ok)} of {len(ends)} 6 h buckets'); continue
            # stop at the first gap (a later bucket after a missing one would be mis-assigned)
            keep = []
            for a, b, v in ok:
                if keep and a != keep[-1][1]: break
                keep.append((a, b, v))
            P = g.points
            return dict(ok=True, model=name, run=g.init.strftime('%Y-%m-%dT%HZ'), source=('NOAA NBM v4 deterministic QPF (2.5 km), AWS noaa-nbm-grib2-pds'
                        if name == 'NBM' else 'NOAA GFS 0.25 deg APCP, AWS noaa-gfs-bdp-pds'), resolution_km=2.5 if name == 'NBM' else 25,
                        horizon_h=keep[-1][1], files=len(g.files), missing_buckets=len(ends) - len(keep), n_points=int(P.inside.sum()),
                        buckets=[[iso(g.init + dt.timedelta(hours=a)), iso(g.init + dt.timedelta(hours=b))] for a, b, _ in keep],
                        _R=np.stack([v for _, _, v in keep]), _P=P, notes=errs)
        except Exception as e:
            log(name, 'failed', repr(e)[:300]); errs.append(f'{name}: {repr(e)[:200]}')
    return dict(ok=False, error='; '.join(errs) or 'no rain source')


# ------------------------------------------------------------------ WPC Excessive Rainfall Outlook
def ero_category(props):
    """Highest ERO level named in a feature's properties (dn 1-4 or text Marginal/Slight/Moderate/High, MRGL/SLGT/MDT/HIGH)."""
    best = 0
    for k, v in props.items():
        if k.lower() in ('dn', 'category_num') and isinstance(v, (int, float)) and 0 < v <= 4: best = max(best, int(v)); continue
        if not isinstance(v, str): continue
        s = v.upper()
        for lev, words in ((4, ('HIGH',)), (3, ('MODERATE', 'MDT')), (2, ('SLIGHT', 'SLGT')), (1, ('MARGINAL', 'MRGL'))):
            if k.lower() in ('outlook', 'category', 'cat', 'label', 'name', 'risk', 'snippet') and any(w in s for w in words):
                best = max(best, lev); break
    return best


def ero_times(props):
    """(issued, start, end) UTC from feature properties when present (keys vary between the GeoJSON and the MapServer)."""
    P = {k.lower(): v for k, v in props.items()}
    out = []
    for keys in (('issue_time', 'issued', 'issue'), ('start_time', 'valid_start', 'start'), ('end_time', 'valid_end', 'end', 'expire_time')):
        v = next((P[k] for k in keys if P.get(k)), None); d = None
        if isinstance(v, (int, float)): d = dt.datetime.utcfromtimestamp(v / 1000 if v > 1e11 else v)
        elif isinstance(v, str):
            s = v.strip(); d = parse_utc(s)
            for fmt in ('%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M', '%Y%m%d%H%M', '%m/%d/%Y %H:%M', '%Y%m%d %H%M'):
                if d: break
                try: d = dt.datetime.strptime(s, fmt)
                except ValueError: pass
        out.append(d)
    return tuple(out)


def ero_period(n, now):
    """Default valid period of ERO day n: the 12z-12z period containing now is day 1."""
    t = now.replace(hour=12, minute=0, second=0)
    if now < t: t -= dt.timedelta(days=1)
    return t + dt.timedelta(days=n - 1), t + dt.timedelta(days=n)


def fetch_ero(now):
    from shapely.geometry import shape
    import storm_archive as SA
    D = SA.d3(); U = D['union']; bx = U.bounds
    days, errs, src = [], [], None
    layers = None
    for n in range(1, 6):
        feats, used = None, None
        r = http(ERO_GEOJSON.format(n=n), timeout=60)
        if r is not None:
            try: feats = r.json().get('features') or []; used = 'geojson'
            except Exception as e: errs.append(f'day {n} geojson unreadable: {repr(e)[:80]}')
        if feats is None:                       # fallback: the NOAA mapservices layer for this day
            try:
                if layers is None:
                    j = http(ERO_MAPSERVER, params={'f': 'json'}, timeout=60); layers = (j.json().get('layers') if j is not None else None) or []
                lid = next((l['id'] for l in layers if re.search(rf'excessive.*day\s*_?{n}\b', l.get('name', ''), re.I)), None)
                if lid is not None:
                    q = http(f'{ERO_MAPSERVER}/{lid}/query', params=dict(where='1=1', geometry=f'{bx[0]},{bx[1]},{bx[2]},{bx[3]}', geometryType='esriGeometryEnvelope',
                                                                       inSR=4326, outSR=4326, spatialRel='esriSpatialRelIntersects', outFields='*', f='geojson'), timeout=60)
                    if q is not None: feats = q.json().get('features') or []; used = 'mapserver'
            except Exception as e: errs.append(f'day {n} mapserver: {repr(e)[:80]}')
        if feats is None: errs.append(f'day {n}: no ERO from WPC or mapservices'); days.append(dict(day=n, ok=False)); continue
        src = src or used
        lev, towns, iss, t0, t1 = 0, set(), None, None, None
        for f in feats:
            p = f.get('properties') or {}
            a, b, c = ero_times(p); iss = iss or a; t0 = t0 or b; t1 = t1 or c
            if not f.get('geometry'): continue
            try: g = shape(f['geometry']).buffer(0)
            except Exception: continue
            if not g.intersects(U): continue
            L = ero_category(p)
            if L > lev: lev = L; towns = {nm for nm, t in D['towns'] if t.intersects(g)}
            elif L == lev and L: towns |= {nm for nm, t in D['towns'] if t.intersects(g)}
        d0, d1 = ero_period(n, now)
        if not (t0 and t1 and dt.timedelta(hours=12) <= t1 - t0 <= dt.timedelta(hours=36)): t0, t1 = d0, d1
        days.append(dict(day=n, ok=True, category=ERO_LEVELS[lev], level=lev, valid=[iso(t0), iso(t1)], issued=iso(iss), towns=sorted(towns),
                         n_features=len(feats), via=used))
    good = [d for d in days if d['ok']]
    return dict(ok=len(good) == 5, partial=0 < len(good) < 5, source='NWS WPC Excessive Rainfall Outlook, days 1-5 (' +
                ('www.wpc.ncep.noaa.gov/exper/eromap/geojson' if src == 'geojson' else 'mapservices.weather.noaa.gov wpc_precip_hazards' if src else 'unavailable') + ')',
                days=days, errors=errs)


# ------------------------------------------------------------------ NWS alerts
def fetch_alerts(now):
    from shapely.geometry import shape
    from shapely.ops import unary_union
    import storm_archive as SA
    r = http('https://api.weather.gov/alerts/active', params={'area': 'MA'}, timeout=60, tries=4)
    if r is None: return dict(ok=False, error='api.weather.gov/alerts/active unavailable')
    feats = r.json().get('features') or []; rows, zc = [], {}
    for f in feats:
        p = f.get('properties') or {}
        g = f.get('geometry')
        try:
            if g: geom = shape(g)
            else:
                parts = []
                for z in p.get('affectedZones') or []:
                    if z not in zc:
                        zr = http(z, timeout=40, tries=2); zc[z] = shape(zr.json()['geometry']) if zr is not None and zr.json().get('geometry') else None
                    if zc[z] is not None: parts.append(zc[z])
                if not parts: continue
                geom = unary_union(parts)
            hit, towns, _ = SA._d3_hit(geom)
        except Exception as e:
            log('alert geometry', repr(e)[:120]); continue
        if not hit: continue
        ev = p.get('event') or ''
        rows.append(dict(event=ev, flood=any(w in ev.lower() for w in FLOOD_WORDS), severity=p.get('severity'), urgency=p.get('urgency'),
                         headline=(p.get('headline') or '')[:240], onset=iso(parse_utc(p.get('onset') or p.get('effective'))),
                         ends=iso(parse_utc(p.get('ends') or p.get('expires'))), sent=iso(parse_utc(p.get('sent'))), towns_n=len(towns), towns=towns[:15],
                         id=p.get('id') or f.get('id')))
    rows.sort(key=lambda a: (not a['flood'], a['onset'] or ''))
    return dict(ok=True, source='api.weather.gov/alerts/active?area=MA (touching a District 3 town)', fetched=iso(now), n_ma=len(feats), alerts=rows)


# ------------------------------------------------------------------ fetch everything
def cmd_fetch(a, now=None):
    now = now or (parse_utc(a.now) if getattr(a, 'now', None) else utcnow())
    t_ = time.time(); rain = fetch_rain(now, getattr(a, 'model', None)); log('rain', rain.get('model'), rain.get('run'), rain.get('error', ''), f'{time.time() - t_:.0f} s')
    try: ero = fetch_ero(now)
    except Exception as e: ero = dict(ok=False, error=repr(e)[:200])
    log('ero', [(d['day'], d.get('category')) for d in ero.get('days', [])], ero.get('errors') or ero.get('error') or '')
    try: al = fetch_alerts(now)
    except Exception as e: al = dict(ok=False, error=repr(e)[:200])
    log('alerts', len(al.get('alerts', [])), al.get('error', ''))
    raw = dict(fetched=iso(now), fetch_s=round(time.time() - t_), ero=ero, alerts=al)
    if rain.get('ok'):
        R, P = rain.pop('_R'), rain.pop('_P')
        raw['grid'] = dict(towns=P.names, town_pts=[[int(np.searchsorted(np.nonzero(P.inside)[0], i)) for i in idx] for idx in P.town_pts])
        raw['rain_mm'] = np.round(R[:, P.inside], 1).tolist()            # (buckets, points inside District 3)
    raw['rain'] = rain
    if a.out:
        os.makedirs(os.path.dirname(os.path.abspath(a.out)) or '.', exist_ok=True); json.dump(raw, open(a.out, 'w'), separators=(',', ':'))
    return raw


# ------------------------------------------------------------------ build outlook.json
def cron_times(workflow):
    """(cron string, [(hour, minute) UTC]) of forecast.yml's schedule."""
    cr = '40 2,8,14,20 * * *'
    try:
        m = re.search(r"cron:\s*['\"]([^'\"]+)['\"]", open(workflow).read())
        if m: cr = m.group(1)
    except Exception: pass
    mi, hr = cr.split()[:2]
    hs = list(range(24)) if hr == '*' else [int(h) for h in hr.split(',')] if '/' not in hr else list(range(0, 24, int(hr.split('/')[1])))
    ms = [int(x) for x in mi.split(',')] if mi != '*' else [0]
    return cr, sorted((h, m_) for h in hs for m_ in ms)


def next_run(now, times):
    for k in range(0, 2):
        d = (now + dt.timedelta(days=k)).date()
        for h, m in times:
            t = dt.datetime(d.year, d.month, d.day, h, m)
            if t > now: return t
    return None


def build(raw, status=None, workflow=None, prev=None, now=None):
    now = now or utcnow()
    wf = workflow or os.path.join(ROOT, '.github', 'workflows', 'forecast.yml'); cr, times = cron_times(wf)
    today = to_local(now).date(); dates = [today + dt.timedelta(days=k) for k in range(NDAYS)]
    S = status or {}
    v0, v1 = (parse_utc(x) for x in (S.get('valid') or [None, None]))
    gate = S.get('gate') or {}
    rain = (raw or {}).get('rain') or dict(ok=False, error='no fetch result (the outlook fetch job failed or did not run)')
    ero = (raw or {}).get('ero') or dict(ok=False, error='no fetch result'); al = (raw or {}).get('alerts') or dict(ok=False, error='no fetch result')
    problems = []
    if not rain.get('ok'): problems.append('rain: ' + str(rain.get('error', 'missing'))[:200])
    if not ero.get('ok'): problems.append('ERO: ' + '; '.join(ero.get('errors') or [str(ero.get('error', 'missing'))])[:200])
    if not al.get('ok'): problems.append('alerts: ' + str(al.get('error', 'missing'))[:200])
    # ---- rain per local day
    days = []
    R = np.asarray(raw.get('rain_mm'), np.float32) if rain.get('ok') else None
    if R is not None:
        G = raw['grid']; TP = [np.asarray(ix, int) for ix in G['town_pts']]; names = G['towns']
        B = [(parse_utc(a), parse_utc(b)) for a, b in rain['buckets']]
        mid_date = [to_local(a + (b - a) / 2).date() for a, b in B]
        R24 = np.stack([R[max(0, i - 3):i + 1].sum(0) for i in range(len(B))])     # running 24 h (4 buckets) ending with bucket i
        def tmax(v): return np.array([float(v[ix].max()) for ix in TP])
        T6 = np.stack([tmax(R[i]) for i in range(len(B))]); T24 = np.stack([tmax(R24[i]) for i in range(len(B))])
    for k, d in enumerate(dates):
        s, e = local_midnight_utc(d), local_midnight_utc(d + dt.timedelta(days=1))
        day = dict(day=k + 1, date=d.isoformat(), label=d.strftime('%a %-d %b'), start=iso(s), end=iso(e))
        if R is not None:
            ib = [i for i, md in enumerate(mid_date) if md == d]
            day['hours'] = 6 * len(ib); day['partial'] = len(ib) < 4
            if ib:
                tot = R[ib].sum(0); tt = tmax(tot); j = int(np.argmax(tt))
                o6 = sorted({names[t] for i in ib for t in np.nonzero(T6[i] >= GATE_6H_MM)[0]})
                o24 = sorted({names[t] for i in ib if i >= 3 for t in np.nonzero(T24[i] >= GATE_24H_MM)[0]})
                day['rain'] = dict(d3_mean_mm=round(float(tot.mean()), 1), town_max_mm=round(float(tt[j]), 1), town_max=names[j],
                                   max6h_mm=round(float(T6[ib].max()), 1), max24h_mm=round(float(max(T24[i].max() for i in ib)), 1),
                                   six_hourly_mean_mm=[round(float(R[i].mean()), 1) for i in ib], six_hourly_max_mm=[round(float(T6[i].max()), 1) for i in ib],
                                   six_hourly_start=[rain['buckets'][i][0] for i in ib])
                day['towns_over'] = sorted(set(o6) | set(o24)); day['towns_over_6h'] = o6; day['towns_over_24h'] = o24
            else: day['rain'] = None; day['towns_over'] = []
        else: day['rain'] = None; day['towns_over'] = []; day['hours'] = 0; day['partial'] = True
        # ERO: the period whose mid-point (00z) falls in this local day
        er = None
        for x in ero.get('days') or []:
            if not x.get('ok'): continue
            a_, b_ = parse_utc(x['valid'][0]), parse_utc(x['valid'][1])
            if to_local(a_ + (b_ - a_) / 2).date() == d: er = dict(day=x['day'], category=x['category'], level=x['level'], valid=x['valid'], towns=x.get('towns', [])[:20])
        day['ero'] = er
        # alerts in force during the day
        acts = [x for x in al.get('alerts') or [] if (parse_utc(x.get('onset')) or now) < e and (parse_utc(x.get('ends')) or e) > s]
        day['alerts'] = sorted({x['event'] for x in acts})
        floodal = [x for x in acts if x['flood']]
        # HRRR flood-model window
        inwin = bool(v0 and v1 and s < v1 and e > v0)
        day['flood_model'] = dict(in_window=inwin, state=S.get('state') if inwin else None, trigger=bool(gate.get('trigger')) if inwin else None)
        r_ = day.get('rain') or {}; tmx = r_.get('town_max_mm') or 0; el = (er or {}).get('level', 0)
        heavy = bool(day['towns_over']) or el >= 2 or any(('watch' in x['event'].lower() or 'warning' in x['event'].lower()) for x in floodal)
        if inwin and S.get('state') == 'run':
            lev, verdict, det = 4, 'Flood model running', S.get('headline') or ''
        elif inwin and S.get('state') == 'error':
            lev, verdict, det = 4, 'Flood model run failed', S.get('headline') or ''
        elif heavy:
            why = ([f"{len(day['towns_over'])} town{'s' if len(day['towns_over']) != 1 else ''} over the flood-model threshold"] if day['towns_over'] else []) + \
                  ([f"WPC {er['category']} risk of excessive rain"] if el >= 2 else []) + [x['event'] for x in floodal if 'watch' in x['event'].lower() or 'warning' in x['event'].lower()][:2]
            if inwin: lev, verdict, det = 3, 'Heavy rain possible, below the flood-model threshold in the 48 h forecast', '; '.join(why) + '. The 48 h HRRR forecast stays under the gate.'
            else: lev, verdict, det = 3, 'Heavy rain possible: flood model runs when within 48 h', '; '.join(why) + '.'
        elif tmx >= RAIN_MM or el == 1:
            lev, verdict, det = 2, 'Rain, below flood threshold', f"up to {tmx:.0f} mm in a town" + (', WPC marginal risk of excessive rain' if el == 1 else '')
        elif tmx >= LIGHT_MM:
            lev, verdict, det = 1, 'Light rain', f"up to {tmx:.0f} mm in a town"
        elif R is None and not er:
            lev, verdict, det = None, 'No data', 'rain forecast unavailable'
        else:
            lev, verdict, det = 0, 'Quiet', 'little or no rain'
        day.update(level=lev, verdict=verdict, detail=det)
        days.append(day)
    # ---- storms: runs of consecutive days at level >= 2
    storms, cur = [], []
    for day in days + [None]:
        if day is not None and (day['level'] or 0) >= 2: cur.append(day); continue
        if cur:
            pk = max(cur, key=lambda x: ((x['level'] or 0), (x.get('rain') or {}).get('town_max_mm') or 0))
            st = dict(id=f's{len(storms) + 1}', start_date=cur[0]['date'], end_date=cur[-1]['date'], days=[x['day'] for x in cur], peak_day=pk['day'], peak_date=pk['date'],
                      level=max(x['level'] for x in cur), verdict=pk['verdict'], ero_max=ERO_LEVELS[max(((x['ero'] or {}).get('level', 0) for x in cur))],
                      alerts=sorted({e for x in cur for e in x['alerts']}), towns_over=sorted({t for x in cur for t in x['towns_over']}))
            if R is not None:
                ib = [i for i, md in enumerate(mid_date) if cur[0]['date'] <= md.isoformat() <= cur[-1]['date']]
                if ib:
                    tot = R[ib].sum(0); tt = tmax(tot); j = int(np.argmax(tt)); wet = [i for i in ib if T6[i].max() >= 1.0] or ib
                    st.update(start=rain['buckets'][wet[0]][0], end=rain['buckets'][wet[-1]][1], d3_mean_mm=round(float(tot.mean()), 1), town_max_mm=round(float(tt[j]), 1),
                              town_max=names[j], max6h_mm=round(float(T6[ib].max()), 1), max24h_mm=round(float(T24[ib].max()), 1))
            else: st.update(start=cur[0]['start'], end=cur[-1]['end'])
            storms.append(st); cur = []
    # ---- headline
    def span(s): return days[s['days'][0] - 1]['label'].split()[0] + ('' if len(s['days']) == 1 else '–' + days[s['days'][-1] - 1]['label'].split()[0])
    if R is None and not any(d['ero'] for d in days): headline = 'Week outlook unavailable (rain forecast missing)'
    elif not storms: headline = f'No storm in District 3 in the next {NDAYS} days'
    else:
        s0 = max(storms, key=lambda s: (s['level'], s.get('town_max_mm') or 0)); amt = f", up to {s0['town_max_mm']:.0f} mm in a town" if s0.get('town_max_mm') is not None else ''
        headline = {4: f"Flood model running for the storm {span(s0)}", 3: f"Heavy rain possible {span(s0)}{amt}"}.get(s0['level'], f"Rain {span(s0)}{amt}, below the flood threshold")
        if len(storms) > 1: headline += f" ({len(storms)} rain spells this week)"
    # ---- health
    status_ = 'failed' if not rain.get('ok') else 'ok' if not problems else 'partial'
    nx = next_run(now, times)
    run_url = (f"{os.environ['GITHUB_SERVER_URL']}/{os.environ['GITHUB_REPOSITORY']}/actions/runs/{os.environ['GITHUB_RUN_ID']}"
               if os.environ.get('GITHUB_RUN_ID') and os.environ.get('GITHUB_REPOSITORY') else None)
    out = dict(schema=SCHEMA, issued=iso(now), tz=TZ, headline=headline,
               thresholds=dict(max6h_mm=GATE_6H_MM, max24h_mm=GATE_24H_MM, rain_day_mm=RAIN_MM, light_mm=LIGHT_MM, basis='docs/proto/forecast/GATE.md'),
               days=days, storms=storms, alerts=(al.get('alerts') or [])[:20],
               sources=dict(rain={k: v for k, v in rain.items() if not k.startswith('_') and k != 'buckets'},
                            ero={k: v for k, v in ero.items() if k != 'days'} | dict(days=[{k: v for k, v in x.items() if k != 'towns'} for x in ero.get('days') or []]),
                            alerts={k: v for k, v in al.items() if k != 'alerts'}),
               health=dict(status=status_, problems=problems, issued=iso(now), fetched=(raw or {}).get('fetched'), rain_run=rain.get('run'),
                           next_update=iso(nx), schedule_cron=cr, schedule_utc=[f'{h:02d}:{m:02d}' for h, m in times], typical_delay_min=[10, 60],
                           stale_after_h=STALE_H, workflow='.github/workflows/forecast.yml', run_url=run_url,
                           forecast_cycle=dict(issued=S.get('issued'), built=S.get('built'), state=S.get('state'), headline=S.get('headline'), valid=S.get('valid')) if S else None),
               method=('Daily rain: NOAA NBM deterministic QPF (fallback GFS) in 6 h buckets, each bucket counted in the local day holding its mid-point '
                       '(so a day runs about 02:00-02:00 EDT / 01:00-01:00 EST); per town the maximum over the grid points inside it. Over-threshold towns '
                       'use the flood-model gate (6 h >= 25 mm, 24 h >= 40 mm) on these 6 h buckets. ERO: WPC days 1-5, the period whose 00z mid-point falls in '
                       'the local day. Week-ahead rain is uncertain and smoothed; the flood model itself runs only on the 48 h HRRR (docs/proto/forecast/OUTLOOK.md).'))
    if status_ == 'failed' and prev and prev.get('days'):          # keep the last good days, flagged, so the strip is not empty
        out['days_from_previous'] = prev.get('issued'); out['previous'] = dict(issued=prev.get('issued'), headline=prev.get('headline'), days=prev.get('days'), storms=prev.get('storms'))
    return out


def cmd_build(a, raw=None):
    raw = raw if raw is not None else (json.load(open(a.raw)) if a.raw and os.path.exists(a.raw) else None)
    S = json.load(open(a.status)) if a.status and os.path.exists(a.status) else None
    prev = None
    if a.prev and os.path.exists(a.prev):
        try: prev = json.load(open(a.prev))
        except Exception: prev = None
    O = build(raw, S, a.workflow, prev, parse_utc(a.now) if getattr(a, 'now', None) else None)
    os.makedirs(os.path.dirname(os.path.abspath(a.out)) or '.', exist_ok=True); json.dump(O, open(a.out, 'w'), separators=(',', ':'))
    log(f"outlook {O['health']['status']}: {O['headline']}")
    for d in O['days']:
        r = d.get('rain') or {}
        log(f"  {d['label']:<11} {str(r.get('d3_mean_mm', '-')):>5} / {str(r.get('town_max_mm', '-')):>5} mm  6h {str(r.get('max6h_mm', '-')):>5}  ERO {(d['ero'] or {}).get('category', '-'):<9} "
            f"{','.join(d['alerts'])[:30]:<30} L{d['level']} {d['verdict']}")
    for p in O['health']['problems']: log('  problem:', p)
    return O


def cmd_run(a):
    raw = cmd_fetch(argparse.Namespace(out=a.raw, now=a.now, model=a.model))
    return cmd_build(argparse.Namespace(raw=None, status=a.status, prev=a.prev, workflow=a.workflow, out=a.out, now=a.now), raw=raw)


def selftest():
    """Synthetic raw input: day assignment, gate exceedances, verdicts, storms, health; no network."""
    now = dt.datetime(2026, 10, 29, 3, 0)
    names = ['Worcester', 'Leominster', 'Tiny']; TP = [[0, 1], [2, 3], [4]]
    t0 = dt.datetime(2026, 10, 29, 0, 0); nb = 4 * 8
    B = [[iso(t0 + dt.timedelta(hours=6 * i)), iso(t0 + dt.timedelta(hours=6 * i + 6))] for i in range(nb)]
    R = np.zeros((nb, 5), np.float32)
    R[9, 0] = 30.0                      # 2026-10-31T06-12Z: Worcester 30 mm / 6 h -> local day Oct 31 (mid-point 09Z = 05 EDT)
    R[10, 0] = 8.0; R[8, 2] = 12.0      # Oct 31: Leominster 12 mm (00-06Z mid 03Z = 23 EDT Oct 30!)
    R[18, 1] = 4.0                        # Nov 2 light
    raw = dict(fetched=iso(now), rain=dict(ok=True, model='NBM', run='2026-10-29T00Z', buckets=B), grid=dict(towns=names, town_pts=TP), rain_mm=R.tolist(),
               ero=dict(ok=True, days=[dict(day=n, ok=True, category=ERO_LEVELS[2 if n == 3 else 0], level=2 if n == 3 else 0,
                                            valid=[iso(dt.datetime(2026, 10, 28, 12) + dt.timedelta(days=n - 1)), iso(dt.datetime(2026, 10, 29, 12) + dt.timedelta(days=n - 1))]) for n in range(1, 6)]),
               alerts=dict(ok=True, alerts=[dict(event='Flood Watch', flood=True, onset='2026-10-31T00:00Z', ends='2026-11-01T00:00Z')]))
    S = dict(state='quiet', issued='2026-10-29T00:00Z', built='2026-10-29T02:50Z', valid=['2026-10-29T00:00Z', '2026-10-31T00:00Z'], gate=dict(trigger=False), headline='No road closures')
    O = build(raw, S, now=now)
    D = {d['date']: d for d in O['days']}
    # 03Z on 29 Oct is 23:00 EDT on 28 Oct: day 1 is 28 Oct
    assert O['days'][0]['date'] == '2026-10-28', O['days'][0]['date']
    o31 = D['2026-10-31']; o30 = D['2026-10-30']
    assert o31['rain']['town_max_mm'] == 38.0 and o31['rain']['town_max'] == 'Worcester', o31['rain']
    assert o31['towns_over_6h'] == ['Worcester'] and o31['level'] == 3, o31
    assert o30['rain']['town_max_mm'] == 12.0 and o30['level'] >= 2, o30          # ERO day 3 (30-31 Oct 12z) -> local 30 Oct slight
    assert o30['ero']['category'] == 'slight', o30['ero']
    assert o30['flood_model']['in_window'] and o30['verdict'].startswith('Heavy rain possible, below'), o30['verdict']
    assert D['2026-11-02']['level'] == 1 and D['2026-11-03']['level'] == 0
    assert len(O['storms']) == 1 and O['storms'][0]['days'] == [3, 4] and O['storms'][0]['peak_date'] == '2026-10-31', O['storms']
    assert O['health']['status'] == 'ok' and O['health']['next_update'] == '2026-10-29T08:40Z', O['health']
    S2 = dict(S, state='run', gate=dict(trigger=True), headline='3 road segments likely closed')
    assert build(raw, S2, now=now)['days'][1]['verdict'] == 'Flood model running'
    F = build(dict(fetched=iso(now), rain=dict(ok=False, error='x'), ero=raw['ero'], alerts=raw['alerts']), S, prev=O, now=now)
    assert F['health']['status'] == 'failed' and F['previous']['days'], F['health']
    P = build(dict(raw, alerts=dict(ok=False, error='down')), S, now=now); assert P['health']['status'] == 'partial'
    assert ero_category({'dn': 2}) == 2 and ero_category({'OUTLOOK': 'Marginal (At Least 5%)'}) == 1 and ero_category({'outlook': 'MDT'}) == 3
    print('outlook selftest ok:', O['headline'])


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0]); sp = ap.add_subparsers(dest='cmd')
    p = sp.add_parser('fetch'); p.add_argument('--out', required=True); p.add_argument('--now'); p.add_argument('--model', choices=['NBM', 'GFS'])
    for nm in ('build', 'run'):
        p = sp.add_parser(nm); p.add_argument('--out', required=True); p.add_argument('--status'); p.add_argument('--prev'); p.add_argument('--now')
        p.add_argument('--workflow', default=os.path.join(ROOT, '.github', 'workflows', 'forecast.yml'))
        if nm == 'build': p.add_argument('--raw')
        else: p.add_argument('--raw'); p.add_argument('--model', choices=['NBM', 'GFS'])
    sp.add_parser('selftest')
    a = ap.parse_args()
    {'fetch': cmd_fetch, 'build': cmd_build, 'run': cmd_run, 'selftest': lambda a: selftest()}.get(a.cmd, lambda a: ap.print_help())(a)
