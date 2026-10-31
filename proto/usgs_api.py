"""One shared USGS gauge reader: instantaneous (15-min) discharge 00060 / gage height 00065 (or any IV parameter) for a site list,
a lon/lat box or a state, over a time window.  docs/proto/usgs/MIGRATION.md.

Why: USGS is switching off NWIS WaterServices (waterservices.usgs.gov): degraded from Nov 2026, outages Jan 2027, shut down
22 Feb 2027 (https://content.govdelivery.com/accounts/USDOIGS/bulletins/42b03d7).  The replacement is the Water Data OGC API
(https://api.waterdata.usgs.gov/ogcapi/v1, collections 'continuous', 'time-series-metadata', 'monitoring-locations',
'latest-continuous'; v0 is served until June 2027).  No key is needed; a free personal key in env API_USGS_PAT (header X-Api-Key)
only raises the rate limit.  This module never asks for, stores or prints a key.

Source switch (env USGS_SOURCE, or the source= argument):
    auto   (default) OGC API; if it returns nothing or fails, legacy WaterServices (only until 2027-02-22, then OGC only)
    ogc    OGC API only
    legacy WaterServices only (the pre-migration path; kept for the equivalence test and as an escape hatch until 22 Feb 2027)
Other env: USGS_OGC_VERSION (default 'v1,v0' = try v1, then v0 per collection), USGS_OGC_ROOT (default https://api.waterdata.usgs.gov/ogcapi).

    import usgs_api as U
    G, used = U.iv(sites=['01094400'], start='2023-09-11T04:00:00Z', end='2023-09-14T03:59:59Z')
    G['01094400']['series']['00060']  -> [('2023-09-11T04:00:00+00:00', 112.0), ...]   (UTC, sorted, the primary/fullest series)
    U.to_pandas(G, '01094400', '00060') -> pandas Series with a UTC DatetimeIndex
    U.now()                            -> the live District 3 summary (schema in MIGRATION.md; for docs/site/data/live/gauges.json)

CLI:
    python proto/usgs_api.py compare --sites 01094400,01094500,01109730 --start 2023-09-11 --end 2023-09-13 --out docs/proto/usgs/_logs
    python proto/usgs_api.py now --out /tmp/gauges.json
"""
import os, sys, json, time, glob, datetime as dt
import requests

OGC_ROOT = os.environ.get('USGS_OGC_ROOT', 'https://api.waterdata.usgs.gov/ogcapi').rstrip('/')
OGC_VERSIONS = [v.strip() for v in os.environ.get('USGS_OGC_VERSION', 'v1,v0').split(',') if v.strip()]
LEGACY_IV = 'https://waterservices.usgs.gov/nwis/iv/'
LEGACY_SITE = 'https://waterservices.usgs.gov/nwis/site/'
LEGACY_OFF = dt.date(2027, 2, 22)                       # USGS shut-down date of WaterServices; the fallback is skipped from then on
NWPS = 'https://api.water.noaa.gov/nwps/v1'
D3_BBOX = (-72.3796, 41.9511, -71.4267, 42.7646)         # MassDOT District 3 box (EPSG:26986 128000,856000,206000,946000) in lon/lat
HDR = {'User-Agent': 'mass-flood-watch research (github.com/Horus331/mass-flood-watch)'}
if os.environ.get('API_USGS_PAT'): HDR['X-Api-Key'] = os.environ['API_USGS_PAT']     # optional; only sent to api.waterdata.usgs.gov
_CACHE = {}                                                                           # site / series metadata per box or state, per process
STATE_POSTAL = {'25': 'ma', '33': 'nh', '50': 'vt', '09': 'ct', '44': 'ri', '36': 'ny', '23': 'me'}  # legacy stateCd wants the postal code
STATS = dict(requests=0, retries=0, ratelimit_remaining=None, version={})             # filled as we go; reported by the test
_log = lambda *a: print(time.strftime('%H:%M:%S'), *a, file=sys.stderr, flush=True)


# ------------------------------------------------------------------------------------------------------------------ HTTP
def _get(url, params=None, tries=6, headers=None, timeout=300):
    """GET with back-off: 429 honours Retry-After, 5xx / network errors retry.  Returns the Response for 200 and for 400/404
    (the caller decides; used for the v1 -> v0 switch), None if it never succeeded."""
    for k in range(tries):
        try:
            STATS['requests'] += 1
            r = requests.get(url, params=params, headers=headers if headers is not None else HDR, timeout=timeout)
            rem = r.headers.get('x-ratelimit-remaining')
            if rem is not None: STATS['ratelimit_remaining'] = rem
            if r.status_code in (200, 400, 404): return r
            wait = 15 * (k + 1)
            if r.status_code == 429:
                try: wait = max(wait, min(600, int(float(r.headers.get('Retry-After', '0')))))
                except ValueError: pass
            if r.status_code in (401, 403) and 'X-Api-Key' in (headers or HDR): _log('  key refused?', r.status_code, url[:90])
            _log('  http', r.status_code, url[:100], 'retry in', wait, 's')
        except Exception as e:
            wait = 15 * (k + 1); _log('  err', repr(e)[:120], url[:80])
        STATS['retries'] += 1; time.sleep(wait)
    return None


def items(coll, params=None, item=None):
    """All features of an OGC API items query (follows rel=next).  Tries the versions in USGS_OGC_VERSION in order and remembers
    the one that answered for this collection.  item='USGS-01094400' reads a single feature.  None if every version failed."""
    vers = [STATS['version'][coll]] if coll in STATS['version'] else OGC_VERSIONS
    for v in vers:
        url = f'{OGC_ROOT}/{v}/collections/{coll}/items' + (f'/{item}' if item else '')
        p = dict(params or {}, f='json')
        if not item: p.setdefault('limit', 10000)
        feats, nxt, ok = [], url, True
        while nxt:
            r = _get(nxt, p)
            if r is None or r.status_code != 200:
                if r is not None: _log(f'  {v} {coll}: HTTP {r.status_code} {r.text[:160]!r}')
                ok = False; break
            j = r.json()
            if item: return [j]
            feats += j.get('features', []); p = None
            nxt = next((l['href'] for l in j.get('links', []) if l.get('rel') == 'next'), None)
        if ok: STATS['version'][coll] = v; return feats
    return None


# ------------------------------------------------------------------------------------------------------------------ time
def utc(t):
    """Any ISO time (Z, offset, or naive = UTC) or datetime -> '2023-09-12T04:30:00+00:00'."""
    if isinstance(t, str): t = dt.datetime.fromisoformat(t.replace('Z', '+00:00'))
    if t.tzinfo is None: t = t.replace(tzinfo=dt.timezone.utc)
    return t.astimezone(dt.timezone.utc).strftime('%Y-%m-%dT%H:%M:%S+00:00')

def _z(t): return utc(t)[:19] + 'Z'


# ------------------------------------------------------------------------------------------------------------------ OGC path
def _meta_from_feature(f):
    q = f.get('properties') or {}; c = ((f.get('geometry') or {}).get('coordinates') or [None, None])
    num = lambda v: float(v) if v not in (None, '') else None
    return dict(name=q.get('monitoring_location_name'), lon=num(c[0]), lat=num(c[1]), datum_ft=num(q.get('altitude')),
                vdatum=q.get('vertical_datum'), drain_mi2=num(q.get('drainage_area')), state_code=q.get('state_code'),
                site_type=q.get('site_type_code') or q.get('site_type'))

def _sid(x): return str(x).split('-', 1)[-1]

def ogc_sites_meta(sites=None, bbox=None, state=None):
    """{site: meta} from 'monitoring-locations' (one bbox / state query, or one request per listed site)."""
    out = {}
    if sites:
        for s in sites:
            F = items('monitoring-locations', item=f'USGS-{s}')
            if F: out[s] = _meta_from_feature(F[0])
        return out
    key = ('ml', tuple(bbox) if bbox else state)
    if key in _CACHE: return _CACHE[key]
    p = dict(bbox=','.join(f'{v:.5f}' for v in bbox)) if bbox else dict(state_code=state)
    F = items('monitoring-locations', p)
    for f in F or []:
        if str(f.get('id', '')).startswith('USGS-'): out[_sid(f['id'])] = _meta_from_feature(f)
    if F is not None: _CACHE[key] = out
    return out

def ogc_candidates(bbox, params, t0, t1):
    """Sites in the box with an instantaneous series of any of params overlapping [t0, t1] ('time-series-metadata').  None = failed."""
    key = ('tsm', tuple(bbox), params)
    F = _CACHE.get(key) or items('time-series-metadata', dict(bbox=','.join(f'{v:.5f}' for v in bbox), parameter_code=','.join(params)))
    if F is None: return None
    _CACHE[key] = F
    a, b = t0[:10], t1[:10]; out = set()
    for f in F:
        q = f.get('properties') or {}
        if q.get('parameter_code') not in params: continue
        ci, cp = (q.get('computation_identifier') or '').lower(), (q.get('computation_period_identifier') or '').lower()
        if (ci or cp) and ci != 'instantaneous' and cp != 'points': continue                 # daily / annual statistics series
        if q.get('end') and str(q['end'])[:10] < a: continue                                  # ended before the window
        if q.get('begin') and str(q['begin'])[:10] > b: continue
        out.add(_sid(q.get('monitoring_location_id') or f.get('id')))
    return out

def ogc_series(sites, params, t0, t1, chunk=10):
    """{(site, pcode): [(t_utc, v)]} from 'continuous', keeping per site/parameter the fullest time series (the primary one).
    Several sites per request (comma list); a chunk that answers empty is retried one site at a time.  None if the API failed."""
    raw, failed = {}, False
    tw = f'{_z(t0)}/{_z(t1)}'
    def pull(ids, pc):
        F = items('continuous', dict(monitoring_location_id=','.join('USGS-' + s for s in ids), parameter_code=pc, time=tw))
        if F is None: return None
        for f in F:
            q = f['properties']
            try: v = float(q['value'])
            except (TypeError, ValueError): continue
            if v <= -999: continue
            raw.setdefault((_sid(q['monitoring_location_id']), pc), {}).setdefault(q.get('time_series_id') or '', []).append((utc(q['time']), v))
        return len(F)
    sites = list(sites); single = False
    for pc in params:
        for i in range(0, len(sites), 1 if single else chunk):
            ids = sites[i:i + (1 if single else chunk)]; n = pull(ids, pc)
            if n is None: failed = True; continue
            if n == 0 and len(ids) > 1:                                                      # comma list not honoured? one by one
                got = [pull([s], pc) for s in ids]
                if any(got): single = True; _log('  continuous: comma lists of ids gave nothing; querying one site at a time')
    if failed and not raw: return None
    return {k: sorted(set(max(by.values(), key=len))) for k, by in raw.items()}


def _iv_ogc(sites, bbox, state, params, t0, t1, meta):
    if sites: cand = list(sites)
    else:
        M = ogc_sites_meta(bbox=bbox) if bbox else ogc_sites_meta(state=state)
        if not M: return None
        box = bbox or (min(m['lon'] for m in M.values() if m['lon'] is not None), min(m['lat'] for m in M.values() if m['lat'] is not None),
                       max(m['lon'] for m in M.values() if m['lon'] is not None), max(m['lat'] for m in M.values() if m['lat'] is not None))
        c = ogc_candidates(box, params, t0, t1)
        cand = sorted((c if c is not None else set(M)) & set(M))
    S = ogc_series(cand, params, t0, t1)
    if S is None: return None
    have = sorted({s for s, _ in S})
    if sites: M = ogc_sites_meta(sites=have)                                    # name / location are always needed
    G = {}
    for s in have:
        m = M.get(s) or {}
        if bbox and not sites:
            if m.get('lon') is None or not (bbox[0] <= m['lon'] <= bbox[2] and bbox[1] <= m['lat'] <= bbox[3]): continue
        g = G.setdefault(s, dict(site=s, name=m.get('name'), lon=m.get('lon'), lat=m.get('lat'), datum_ft=m.get('datum_ft'), vdatum=m.get('vdatum'),
                                 drain_mi2=m.get('drain_mi2'), series={}))
        for pc in params:
            if S.get((s, pc)): g['series'][pc] = S[(s, pc)]
    return G


# ------------------------------------------------------------------------------------------------------------------ legacy path
def _iv_legacy(sites, bbox, state, params, t0, t1, meta):
    p = dict(format='json', startDT=_z(t0), endDT=_z(t1), parameterCd=','.join(params), siteStatus='all')
    if sites: p['sites'] = ','.join(sites)
    elif bbox: p['bBox'] = f'{bbox[0]:.4f},{bbox[1]:.4f},{bbox[2]:.4f},{bbox[3]:.4f}'
    else: p['stateCd'] = STATE_POSTAL.get(str(state), str(state)).lower()
    r = _get(LEGACY_IV, p, tries=4)
    if r is None or r.status_code != 200: return None
    G = {}
    for ts in r.json()['value']['timeSeries']:
        si = ts['sourceInfo']; s = si['siteCode'][0]['value']; pc = ts['variable']['variableCode'][0]['value']; gl = si['geoLocation']['geogLocation']
        vals = []
        for v in ts['values'][0]['value']:                                        # as the pre-migration readers
            try: x = float(v['value'])
            except (TypeError, ValueError): continue
            if x > -999: vals.append((utc(v['dateTime']), x))
        g = G.setdefault(s, dict(site=s, name=si['siteName'], lon=gl['longitude'], lat=gl['latitude'], datum_ft=None, vdatum=None, drain_mi2=None, series={}))
        if vals and len(vals) > len(g['series'].get(pc, [])): g['series'][pc] = sorted(set(vals))   # several methods: keep the fullest
    if meta:
        for s, g in G.items():
            m = _get(LEGACY_SITE, dict(format='rdb', sites=s, siteOutput='expanded'), tries=3)
            if m is None or m.status_code != 200: continue
            L = [l for l in m.text.splitlines() if l and not l.startswith('#')]
            if len(L) >= 3:
                d = dict(zip(L[0].split('\t'), L[2].split('\t')))
                g.update(datum_ft=float(d['alt_va']) if d.get('alt_va') else None, vdatum=d.get('alt_datum_cd'),
                         drain_mi2=float(d['drain_area_va']) if d.get('drain_area_va') else None)
    return G


# ------------------------------------------------------------------------------------------------------------------ public
def iv(sites=None, bbox=None, state=None, start=None, end=None, params=('00060', '00065'), source=None, meta=True):
    """Instantaneous values.  Give exactly one of sites (list of 8-15 digit USGS ids), bbox (w, s, e, n lon/lat) or state ('25').
    start / end: ISO times (Z / offset; naive = UTC) or datetimes, inclusive.  Returns (G, used):
      G = {site: dict(site, name, lon, lat, datum_ft, vdatum, drain_mi2, series={pcode: [(t_utc_iso, value), ...]})}
      used = 'ogc-v1' | 'ogc-v0' | 'legacy' | 'none'.
    Only sites with at least one value are returned; with bbox only sites whose location is inside the box."""
    assert sum(x is not None for x in (sites, bbox, state)) == 1, 'give one of sites, bbox, state'
    sites = [str(s) for s in sites] if sites is not None else None
    t0, t1 = utc(start), utc(end); params = tuple(params)
    source = (source or os.environ.get('USGS_SOURCE') or 'auto').lower()
    legacy_ok = dt.datetime.now(dt.timezone.utc).date() < LEGACY_OFF or os.environ.get('USGS_FORCE_LEGACY') == '1'
    if source in ('ogc', 'auto'):
        G = _iv_ogc(sites, bbox, state, params, t0, t1, meta)
        if G or source == 'ogc' or not legacy_ok: return G or {}, 'ogc-' + STATS['version'].get('continuous', '?') if G is not None else 'none'
        _log('  OGC API gave nothing; falling back to legacy WaterServices')
    G = _iv_legacy(sites, bbox, state, params, t0, t1, meta)
    return (G or {}), ('legacy' if G is not None else 'none')


def to_pandas(G, site, pcode):
    """One series of iv()'s result as a pandas Series (float, UTC DatetimeIndex); None if absent."""
    import pandas as pd
    rows = ((G.get(site) or {}).get('series') or {}).get(pcode)
    if not rows: return None
    t, v = zip(*rows)
    return pd.Series(list(v), index=pd.to_datetime(list(t), utc=True), dtype=float).sort_index()


# ------------------------------------------------------------------------------------------------------------------ live 'now'
def _nwps_gauges(bbox):
    """NWS NWPS gauges in the box: {usgs_site: dict(lid, name, flood categories ft, observed category, forecast peak)}."""
    H = {'User-Agent': HDR['User-Agent']}
    r = _get(f'{NWPS}/gauges', {'bbox.xmin': bbox[0], 'bbox.ymin': bbox[1], 'bbox.xmax': bbox[2], 'bbox.ymax': bbox[3], 'srid': 'EPSG_4326'}, tries=3, headers=H, timeout=60)
    if r is None or r.status_code != 200: return {}, 'nwps list failed'
    out = {}
    for g in r.json().get('gauges', []):
        lid = g.get('lid')
        if not lid: continue
        d = _get(f'{NWPS}/gauges/{lid}', None, tries=2, headers=H, timeout=60)
        if d is None or d.status_code != 200: continue
        d = d.json(); usgs = (d.get('usgsId') or g.get('usgsId') or '').strip()
        if not usgs: continue
        cat = ((d.get('flood') or {}).get('categories') or {}); stg = lambda k: (cat.get(k) or {}).get('stage')
        num = lambda v: float(v) if isinstance(v, (int, float)) and v > -999 else None
        obs = ((d.get('status') or {}).get('observed') or {}); fc = ((d.get('status') or {}).get('forecast') or {})
        rec = dict(lid=lid, name=d.get('name'), stage_units=(d.get('flood') or {}).get('stageUnits'), action_ft=num(stg('action')), minor_ft=num(stg('minor')),
                   moderate_ft=num(stg('moderate')), major_ft=num(stg('major')), observed_category=obs.get('floodCategory'),
                   observed_stage=num(obs.get('primary')), observed_t=obs.get('validTime'), forecast_category=fc.get('floodCategory') or None,
                   forecast_peak_ft=None, forecast_peak_t=None)
        if rec['minor_ft'] is not None or fc:
            sf = _get(f'{NWPS}/gauges/{lid}/stageflow', None, tries=2, headers=H, timeout=60)
            if sf is not None and sf.status_code == 200:
                pts = [(p.get('validTime'), num(p.get('primary'))) for p in ((sf.json().get('forecast') or {}).get('data') or [])]
                pts = [p for p in pts if p[1] is not None]
                if pts: rec['forecast_peak_t'], rec['forecast_peak_ft'] = max(pts, key=lambda p: p[1])
        out[usgs] = rec
    return out, 'ok'


def ref_peaks(pattern=None):
    """Largest committed storm peak per site from docs/proto/obs/gauges_<storm>.json: {site: dict(q_cfs, q_storm, stage_ft, stage_storm)}."""
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    R = {}
    for p in sorted(glob.glob(pattern or os.path.join(root, 'docs', 'proto', 'obs', 'gauges_*.json'))):
        storm = os.path.basename(p)[7:-5]
        try: J = json.load(open(p))
        except Exception: continue
        for g in J.get('gauges', []):
            r = R.setdefault(g['site'], dict(q_cfs=None, q_storm=None, stage_ft=None, stage_storm=None))
            for k, kk in (('peak_q_cfs', 'q'), ('peak_stage_ft', 'stage')):
                v = (g.get(k) or [None, None])[1]
                key = 'q_cfs' if kk == 'q' else 'stage_ft'
                if v is not None and (r[key] is None or v > r[key]): r[key] = v; r[kk + '_storm'] = storm
    return R


def now(bbox=D3_BBOX, hours=24, nwps=True, source=None, refs=None):
    """Live summary of every USGS discharge / stage gauge in the box over the last `hours` (default the District 3 box, 24 h).
    Returns the dict written to docs/site/data/live/gauges.json (schema: docs/proto/usgs/MIGRATION.md)."""
    t1 = dt.datetime.now(dt.timezone.utc).replace(microsecond=0); t0 = t1 - dt.timedelta(hours=hours)
    G, used = iv(bbox=bbox, start=t0, end=t1, source=source)
    R = ref_peaks() if refs is None else refs
    N, nwps_status = (_nwps_gauges(bbox) if nwps else ({}, 'off'))
    r2 = lambda v, n=2: None if v is None else round(float(v), n)
    out = []
    for s, g in sorted(G.items()):
        rec = dict(site=s, name=g['name'], lon=r2(g['lon'], 5), lat=r2(g['lat'], 5), drain_mi2=g['drain_mi2'],
                   url=f'https://waterdata.usgs.gov/monitoring-location/USGS-{s}/')
        for pc, key in (('00060', 'q_cfs'), ('00065', 'stage_ft')):
            v = g['series'].get(pc) or []
            if not v: rec[key] = None; continue
            mx = max(v, key=lambda x: x[1]); mn = min(v, key=lambda x: x[1])
            back = [x for x in v if x[0] <= utc(dt.datetime.fromisoformat(v[-1][0]) - dt.timedelta(hours=3))]
            hourly = {}
            for t, x in v: hourly[t[:13]] = max(x, hourly.get(t[:13], -1e18))
            rec[key] = dict(latest=v[-1][1], latest_t=v[-1][0], max=mx[1], max_t=mx[0], min=mn[1], n=len(v),
                            change_3h=r2(v[-1][1] - back[-1][1], 3) if back else None,
                            hourly_max=[[h + ':00Z', x] for h, x in sorted(hourly.items())])
        ref = R.get(s) or {}
        q, st = rec.get('q_cfs') or {}, rec.get('stage_ft') or {}
        rec['ref'] = dict(peak_q_cfs=ref.get('q_cfs'), q_storm=ref.get('q_storm'), peak_stage_ft=ref.get('stage_ft'), stage_storm=ref.get('stage_storm'))
        rec['pct_ref_peak_q'] = r2(100 * q['latest'] / ref['q_cfs'], 1) if q and ref.get('q_cfs') else None
        rec['pct_ref_peak_stage'] = r2(100 * st['latest'] / ref['stage_ft'], 1) if st and ref.get('stage_ft') else None
        n = N.get(s)
        if n:
            n = dict(n); n['pct_flood_stage'] = r2(100 * st['latest'] / n['minor_ft'], 1) if st and n.get('minor_ft') else None
            n['ft_below_flood_stage'] = r2(n['minor_ft'] - st['latest'], 2) if st and n.get('minor_ft') else None
        rec['nwps'] = n
        out.append(rec)
    return dict(generated=_z(t1), window_utc=[_z(t0), _z(t1)], hours=hours, bbox=list(bbox), source=used, nwps=nwps_status,
                ref_note='ref = largest peak of this gauge among the committed storm files docs/proto/obs/gauges_<storm>.json',
                links=dict(usgs='https://api.waterdata.usgs.gov/ogcapi/v1', nwps=NWPS), n=len(out), gauges=out)


# ------------------------------------------------------------------------------------------------------------------ equivalence test
def compare(sites=None, start=None, end=None, params=('00060', '00065'), bbox=None, state=None):
    """Same request through the OGC API and the legacy service; per site/parameter counts and max |difference| on common times."""
    kw = dict(sites=sites, bbox=bbox, state=state)
    A, ua = iv(start=start, end=end, params=params, source='ogc', **kw)
    B, ub = iv(start=start, end=end, params=params, source='legacy', **kw)
    rep = dict(query={k: v for k, v in kw.items() if v is not None}, start=utc(start), end=utc(end), ogc=ua, legacy=ub, stats=dict(STATS),
               sites_only_ogc=sorted(set(A) - set(B)), sites_only_legacy=sorted(set(B) - set(A)), sites=[])
    for s in sorted(set(A) | set(B)):
        for pc in params:
            a = dict((A.get(s) or {}).get('series', {}).get(pc) or []); b = dict((B.get(s) or {}).get('series', {}).get(pc) or [])
            com = sorted(set(a) & set(b)); d = [abs(a[t] - b[t]) for t in com]
            pa = max(a.items(), key=lambda x: x[1]) if a else None; pb = max(b.items(), key=lambda x: x[1]) if b else None
            rep['sites'].append(dict(site=s, pcode=pc, n_ogc=len(a), n_legacy=len(b), n_common=len(com), only_ogc=sorted(set(a) - set(b))[:10],
                                     only_legacy=sorted(set(b) - set(a))[:10], max_abs_diff=max(d) if d else None, n_diff=sum(x > 1e-9 for x in d),
                                     peak_ogc=pa, peak_legacy=pb,
                                     meta_ogc={k: (A.get(s) or {}).get(k) for k in ('name', 'lon', 'lat', 'datum_ft', 'vdatum', 'drain_mi2')},
                                     meta_legacy={k: (B.get(s) or {}).get(k) for k in ('name', 'lon', 'lat', 'datum_ft', 'vdatum', 'drain_mi2')}))
    ok = [r for r in rep['sites'] if r['n_ogc'] or r['n_legacy']]
    rep['pass'] = bool(ok) and not rep['sites_only_ogc'] and not rep['sites_only_legacy'] and all(r['n_ogc'] == r['n_legacy'] == r['n_common'] and (r['max_abs_diff'] or 0) <= 1e-6 for r in ok)
    rep['max_abs_diff'] = max([r['max_abs_diff'] or 0 for r in ok], default=None)
    return rep


if __name__ == '__main__':
    import argparse
    ap = argparse.ArgumentParser(); ap.add_argument('mode', choices=['compare', 'now', 'fetch'])
    ap.add_argument('--sites'); ap.add_argument('--bbox'); ap.add_argument('--state'); ap.add_argument('--params', default='00060,00065')
    ap.add_argument('--start', help='local (America/New_York) date or ISO time'); ap.add_argument('--end'); ap.add_argument('--hours', type=int, default=24)
    ap.add_argument('--source'); ap.add_argument('--no-nwps', action='store_true'); ap.add_argument('--out', default='-')
    a = ap.parse_args(); P = tuple(a.params.split(','))
    def win(x, last):
        if x and len(x) == 10:                                              # a local calendar day -> UTC bounds (as proto/obs_fetch.py)
            from zoneinfo import ZoneInfo
            d = dt.datetime.fromisoformat(x).replace(tzinfo=ZoneInfo('America/New_York'))
            return d + dt.timedelta(days=1, seconds=-1) if last else d
        return x
    def dump(obj, name):
        if a.out == '-': print(json.dumps(obj, indent=1)); return
        p = a.out if a.out.endswith('.json') else os.path.join(a.out, name)
        os.makedirs(os.path.dirname(p) or '.', exist_ok=True); json.dump(obj, open(p, 'w'), indent=1); _log('wrote', p)
    if a.mode == 'compare':
        kw = dict(sites=a.sites.split(',')) if a.sites else dict(bbox=tuple(float(v) for v in a.bbox.split(','))) if a.bbox else dict(state=a.state)
        R = compare(start=win(a.start, False), end=win(a.end, True), params=P, **kw)
        dump(R, f'compare_{a.start}_{a.end}.json')
        for r in R['sites']: print(r['site'], r['pcode'], 'n', r['n_ogc'], r['n_legacy'], r['n_common'], 'maxdiff', r['max_abs_diff'], 'peak', r['peak_ogc'], r['peak_legacy'])
        print('PASS' if R['pass'] else 'FAIL', 'max_abs_diff', R['max_abs_diff'], R['ogc'], R['legacy'], R['stats'])
    elif a.mode == 'now':
        bb = tuple(float(v) for v in a.bbox.split(',')) if a.bbox else D3_BBOX
        J = now(bb, a.hours, nwps=not a.no_nwps, source=a.source); dump(J, 'gauges.json')
        print('gauges', J['n'], 'via', J['source'], 'nwps', J['nwps'], sum(1 for g in J['gauges'] if g['nwps']), 'with NWPS flood stage')
    else:
        kw = dict(sites=a.sites.split(',')) if a.sites else dict(bbox=tuple(float(v) for v in a.bbox.split(','))) if a.bbox else dict(state=a.state)
        G, used = iv(start=win(a.start, False), end=win(a.end, True), params=P, source=a.source, **kw)
        dump(dict(used=used, stats=STATS, gauges=G), 'fetch.json'); print(len(G), 'sites via', used)
