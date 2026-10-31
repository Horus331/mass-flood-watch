"""Transfer test of the frozen District 3 model on MassDOT Districts 4-6 (pre-registration: docs/proto/PROTOCOL.md "Transfer test").

Network steps run on GitHub Actions (.github/workflows/transfer_d456.yml; the sandbox reaches only GitHub).  Offline steps run anywhere.

    python proto/transfer_d456.py discover    # Actions: district polygons, candidate storm days (LSR + Storm Events), Boston 311 + SeeClickFix
                                              #          flood requests in those windows -> docs/proto/transfer/raw/
    python proto/transfer_d456.py queries     # offline: label rows (proto/transfer_d456_labels.py) -> raw/geocode_queries.json
    python proto/transfer_d456.py build       # offline: geocoded rows -> proto/data/labels_<id>_<area>.csv, docs/proto/obs/catalog_d456.json
    python proto/transfer_d456.py roads --box x0,y0,x1,y1 --out DIR      # Actions: OSM road segments in the docs/graph_segments.json layout
    python proto/transfer_d456.py extract --run-dir D --storm S --segments F --dest DIR   # features_/matches_ like closure_ml.extract
    python proto/transfer_d456.py score       # offline: score_v2 on every docs/proto/transfer/runs/<run>/ -> TRANSFER json + tables

Nothing here changes the model: w9_lisflood.py, prototype.py and closure_ml.py are imported or called unchanged.
"""
import os, sys, re, csv, io, json, math, time, zipfile, argparse, datetime as dt
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
TD = os.path.join(ROOT, 'docs', 'proto', 'transfer'); RAW = os.path.join(TD, 'raw')
UA = {'User-Agent': 'mass-flood-watch research (github.com/Horus331/mass-flood-watch)', 'Accept': 'application/json'}
LSR_ALL = os.path.join(ROOT, 'docs', 'proto', 'obs', 'catalog', 'lsr_ma_flood_2014_2026.csv')
SE_ALL = os.path.join(ROOT, 'docs', 'proto', 'obs', 'catalog', 'stormevents_ma_flood_2014_2026.csv')
DIST_ZIP = 'https://s3.us-east-1.amazonaws.com/download.massgis.digital.mass.gov/shapefiles/state/MassDOT_Highway_Districts.zip'
TOWN_ZIPS = ['https://s3.us-east-1.amazonaws.com/download.massgis.digital.mass.gov/shapefiles/census2020/CENSUS2020TOWNS_SHP.zip',
             'https://s3.us-east-1.amazonaws.com/download.massgis.digital.mass.gov/shapefiles/state/townssurvey_shp.zip',
             'https://s3.us-east-1.amazonaws.com/download.massgis.digital.mass.gov/shapefiles/state/TOWNSSURVEY_SHP.zip',
             'https://s3.us-east-1.amazonaws.com/download.massgis.digital.mass.gov/shapefiles/state/townssurvey_shp.zip?x=1']
COASTAL_RE = re.compile(r'\btides?\b|tidal|surge|coastal|ocean|seawall|sea wall|\bwaves?\b|splash|high tide|astronomical|nor.?easter', re.I)
SNOW_RE = re.compile(r'snow ?melt|snowmelt|ice jam|melting snow|\bthaw', re.I)
LOG = []


def log(*a):
    s = ' '.join(str(x) for x in a); print(time.strftime('%H:%M:%S'), s, flush=True); LOG.append(s[:500])


def get(url, params=None, tries=5, timeout=120, stream=False):
    import requests
    for k in range(tries):
        try:
            r = requests.get(url, params=params, headers=UA, timeout=timeout)
            if r.status_code == 200: return r
            log('  http', r.status_code, url[:120], str(params)[:200], r.text[:200])
            if r.status_code in (400, 403, 404): return None
        except Exception as e: log('  err', url[:120], repr(e)[:160])
        time.sleep(4 + 6 * k)
    return None


# ------------------------------------------------------------------------------------------------------------------ districts
def read_shp_zip(content):
    """-> list of (record dict, list of rings [(x, y), ...]) from a zipped shapefile (pyshp)."""
    import shapefile
    z = zipfile.ZipFile(io.BytesIO(content)); names = z.namelist()
    shp = [n for n in names if n.lower().endswith('.shp')]
    out = {}
    for s in shp:
        base = s[:-4]; fx = lambda ext: next((n for n in names if n.lower() == (base + ext).lower()), None)
        R = shapefile.Reader(shp=io.BytesIO(z.read(s)), shx=io.BytesIO(z.read(fx('.shx'))), dbf=io.BytesIO(z.read(fx('.dbf'))))
        fields = [f[0] for f in R.fields[1:]]; L = []
        for sr in R.iterShapeRecords():
            g = sr.shape; parts = list(g.parts) + [len(g.points)]
            rings = [g.points[parts[i]:parts[i + 1]] for i in range(len(parts) - 1)]
            L.append((dict(zip(fields, sr.record)), rings, g.shapeType))
        out[os.path.basename(s)] = dict(fields=fields, rows=L, prj=(z.read(fx('.prj')).decode('latin-1') if fx('.prj') else None))
    return out


def town_key(fields):
    for f in ('TOWN', 'TOWN_NAME', 'TOWN20', 'NAME', 'NAME20', 'COMMUNITY'):
        if f in fields: return f
    return next((f for f in fields if 'TOWN' in f.upper() and not f.upper().endswith('ID')), None)


def pick_town_layer(T):
    log('town zip layers', {k: (v['fields'], len(v['rows']), v['rows'][0][2] if v['rows'] else None) for k, v in T.items()})
    P = [v for v in T.values() if v['rows'] and v['rows'][0][2] in (5, 15, 25) and town_key(v['fields'])]
    P = sorted(P, key=lambda v: ('GENCOAST' in str(v.get('name', '')), -len(v['rows'])))
    return P[0] if P else max(T.values(), key=lambda v: len(v['rows']))


def districts():
    """MassGIS MassDOT_Highway_Districts polygons (EPSG:26986) -> raw/districts.json (simplified rings per district, lon/lat + 26986)."""
    from shapely.geometry import Polygon, MultiPolygon, mapping
    from shapely.ops import unary_union
    from pyproj import Transformer
    r = get(DIST_ZIP, timeout=300)
    if r is None: raise SystemExit('district polygons unavailable')
    S = read_shp_zip(r.content); log('district zip layers', {k: (v['fields'], len(v['rows'])) for k, v in S.items()})
    lay = next(v for k, v in S.items() if 'POLY' in k.upper() or v['rows'] and v['rows'][0][2] in (5, 15, 25))
    by = {}
    for rec, rings, st in lay['rows']:
        d = int(rec.get('DISTRICT') or 0)
        polys = []
        for ring in rings:
            if len(ring) >= 4: polys.append(Polygon(ring))
        if not polys: continue
        # rings: outer and holes mixed; build by containment (shapefile convention: outer clockwise)
        g = unary_union([p.buffer(0) for p in polys])
        by.setdefault(d, []).append(g)
    TI = Transformer.from_crs(26986, 4326, always_xy=True); out = {}
    for d, G in sorted(by.items()):
        g = unary_union(G).buffer(0); gs = g.simplify(50)
        geoms = list(gs.geoms) if isinstance(gs, MultiPolygon) else [gs]
        rings = [[[round(x, 1), round(y, 1)] for x, y in p.exterior.coords] for p in geoms if p.area > 1e5]
        out[str(d)] = dict(area_km2=round(g.area / 1e6, 1), bounds_26986=[round(v) for v in g.bounds], rings_26986=rings)
        log('district', d, out[str(d)]['area_km2'], 'km2', len(rings), 'rings')
    towns = {}
    for u in TOWN_ZIPS:
        rt = get(u, timeout=300, tries=2)
        if rt is None: continue
        try:
            T = read_shp_zip(rt.content); lay = pick_town_layer(T); log('towns layer', lay['fields'], len(lay['rows']))
            nk = town_key(lay['fields'])
            DG = {d: unary_union(G).buffer(0) for d, G in by.items()}
            for rec, rings, st in lay['rows']:
                polys = [Polygon(r_) for r_ in rings if len(r_) >= 4]
                if not polys or not nk: continue
                g = unary_union([p.buffer(0) for p in polys]); c = g.representative_point()
                d = next((k for k, v in DG.items() if v.contains(c)), None)
                towns[str(rec[nk]).title()] = d
            break
        except Exception as e: log('towns failed', u, repr(e)[:200])
    json.dump(dict(source=DIST_ZIP, crs='EPSG:26986', simplify_m=50, districts=out, towns=towns, made=time.strftime('%Y-%m-%d')),
              open(os.path.join(RAW, 'districts.json'), 'w'), separators=(',', ':'))
    return out, towns


def district_of_fn():
    from shapely.geometry import Polygon, Point
    from shapely.prepared import prep
    D = json.load(open(os.path.join(RAW, 'districts.json')))['districts']
    P = {int(d): [prep(Polygon(r)) for r in v['rings_26986']] for d, v in D.items()}

    def f(x, y):
        p = Point(x, y)
        for d, L in P.items():
            if any(q.contains(p) for q in L): return d
        return None
    return f


# ------------------------------------------------------------------------------------------------------------------ candidates
def lsr_rows():
    from pyproj import Transformer
    T = Transformer.from_crs(4326, 26986, always_xy=True); out = []
    for r in csv.DictReader(open(LSR_ALL)):
        if r['TYPETEXT'].upper() not in ('FLOOD', 'FLASH FLOOD', 'HEAVY RAIN'): continue
        t = dt.datetime.strptime(r['VALID'], '%Y%m%d%H%M')
        if t < dt.datetime(2018, 1, 1): continue
        x, y = T.transform(float(r['LON']), float(r['LAT']))
        out.append(dict(src='LSR', t=t, x=x, y=y, lon=float(r['LON']), lat=float(r['LAT']), city=r['CITY'].title(), typ=r['TYPETEXT'].upper(),
                        text=r['REMARK'], mag=r['MAG'], source=r['SOURCE'], raw=r))
    return out


def se_rows():
    from pyproj import Transformer
    T = Transformer.from_crs(4326, 26986, always_xy=True); out = []
    for r in csv.DictReader(open(SE_ALL)):
        if r['EVENT_TYPE'] not in ('Flood', 'Flash Flood') or not r['BEGIN_LAT']: continue
        t = dt.datetime.strptime(r['BEGIN_DATE_TIME'], '%d-%b-%y %H:%M:%S') + dt.timedelta(hours=int(r['CZ_TIMEZONE'][-1]))
        if t < dt.datetime(2018, 1, 1): continue
        x, y = T.transform(float(r['BEGIN_LON']), float(r['BEGIN_LAT']))
        out.append(dict(src='StormEvents', t=t, x=x, y=y, lon=float(r['BEGIN_LON']), lat=float(r['BEGIN_LAT']), city=(r['BEGIN_LOCATION'] or '').title(),
                        typ=r['EVENT_TYPE'], text=r['EVENT_NARRATIVE'], episode=r['EPISODE_NARRATIVE'], cause=r['FLOOD_CAUSE'], event_id=r['EVENT_ID'], raw=r))
    return out


def candidates(dof):
    """Local days (ET) with >= 2 flood LSR / Storm Events reports inside Districts 4-6 -> list of dicts (day, n, bbox of reports)."""
    R = [r for r in lsr_rows() if r['typ'] != 'HEAVY RAIN'] + se_rows(); by = {}
    for r in R:
        d = dof(r['x'], r['y'])
        if d not in (4, 5, 6): continue
        r['district'] = d; day = (r['t'] - dt.timedelta(hours=4)).date().isoformat(); by.setdefault(day, []).append(r)
    C = []
    for day, L in sorted(by.items()):
        if len(L) < 2: continue
        xs = [r['x'] for r in L]; ys = [r['y'] for r in L]
        C.append(dict(day=day, n=len(L), n_lsr=sum(r['src'] == 'LSR' for r in L), districts=sorted({r['district'] for r in L}),
                      box_26986=[min(xs) - 15000, min(ys) - 15000, max(xs) + 15000, max(ys) + 15000],
                      coastal=sum(bool(COASTAL_RE.search((r['text'] or '') + ' ' + (r.get('episode') or ''))) for r in L),
                      cities=sorted({r['city'] for r in L})[:20]))
    return C


# ------------------------------------------------------------------------------------------------------------------ Boston 311
BOS = 'https://data.boston.gov/api/3/action/'
BOS_FLOOD = "(lower(coalesce(\"{t}\",'')) like '%flood%' or lower(coalesce(\"{c}\",'')) like '%flood%')"


def boston_resources():
    out = []
    for q in ('311-service-requests', '311-service-requests-new-system'):
        r = get(BOS + 'package_show', dict(id=q))
        if r is None: continue
        for res in r.json()['result']['resources']:
            if res.get('datastore_active'): out.append(dict(pkg=q, id=res['id'], name=res.get('name'), url=res.get('url')))
    r = get(BOS + 'package_search', dict(q='311', rows=50))
    if r is not None:
        for p in r.json()['result']['results']:
            for res in p.get('resources', []):
                if res.get('datastore_active') and res['id'] not in {o['id'] for o in out} and '311' in (p.get('name') or ''):
                    out.append(dict(pkg=p['name'], id=res['id'], name=res.get('name'), url=res.get('url')))
    log('Boston 311 datastore resources', [(o['pkg'], o['name']) for o in out])
    return out


def boston_fields(rid):
    r = get(BOS + 'datastore_search', dict(resource_id=rid, limit=1))
    if r is None: return None
    return [f['id'] for f in r.json()['result']['fields']]


def boston_sql(sql):
    r = get(BOS + 'datastore_search_sql', dict(sql=sql), timeout=300)
    if r is None: return None
    return r.json()['result']['records']


def boston(windows):
    """Boston 311 requests matching full-text 'flood' / 'flooding' (CKAN datastore_search q; SQL is not open) in every 311 resource; daily
    counts over all years -> raw/boston311_days.json; every such request inside each candidate window -> raw/boston311_<day>.json."""
    RES = boston_resources(); rows = []
    for res in RES:
        seen = set()
        for q in ('flood', 'flooding', 'flooded'):
            off = 0
            while True:
                r = get(BOS + 'datastore_search', dict(resource_id=res['id'], q=q, limit=5000, offset=off), timeout=300)
                if r is None: break
                R = r.json()['result']; recs = R.get('records') or []
                for x in recs:
                    k = x.get('_id')
                    if k in seen: continue
                    seen.add(k); x['_resource'] = res['name']; rows.append(x)
                off += len(recs)
                if not recs or off >= (R.get('total') or 0): break
        log('  311', res['pkg'], res['name'], 'rows matching flood', len(seen))
    def opened(x):
        for k in ('open_dt', 'open_date', 'requested_datetime', 'created_at', 'opened'):
            if x.get(k): return str(x[k]).replace('T', ' ')[:19]
        return ''
    days = {}
    for x in rows:
        d = opened(x)[:10]; t = str(x.get('type') or x.get('service_name') or x.get('case_title') or '')
        days.setdefault(d, {}); days[d][t] = days[d].get(t, 0) + 1
    json.dump(dict(resources=RES, n=len(rows), days=days), open(os.path.join(RAW, 'boston311_days.json'), 'w'), indent=0)
    for W in windows:
        a, b = W['a'].replace('T', ' '), W['b'].replace('T', ' ')
        got = [x for x in rows if a <= opened(x) < b]
        json.dump(dict(window_local=[a, b], n=len(got), rows=got), open(os.path.join(RAW, f'boston311_{W["day"]}.json'), 'w'), indent=0, default=str)
        if got: log('  311 window', W['day'], len(got))
    return days


# ------------------------------------------------------------------------------------------------------------------ SeeClickFix
SCF = 'https://seeclickfix.com/api/v2'
SCF_FLOOD = re.compile(r'flood|standing water|ponding|water (on|in|across|over) (the )?(road|street)|road (is )?under water|washout|washed out|'
                       r'catch ?basin|storm ?drain|clogged drain|drain', re.I)


def scf_issues(params, max_pages=25):
    out = []; p = dict(params, per_page=100, status='open,acknowledged,closed,archived')
    for page in range(1, max_pages + 1):
        p['page'] = page; r = get(f'{SCF}/issues', p, tries=4, timeout=90)
        if r is None: break
        J = r.json(); I = J.get('issues') or []
        for i in I:
            rt = i.get('request_type') or {}
            out.append(dict(id=i.get('id'), created_at=i.get('created_at'), closed_at=i.get('closed_at'), status=i.get('status'), lat=i.get('lat'),
                            lng=i.get('lng'), address=i.get('address'), summary=i.get('summary'), description=(i.get('description') or '')[:800],
                            request_type=rt.get('title'), organization=rt.get('organization'), html_url=i.get('html_url')))
        pg = (J.get('metadata') or {}).get('pagination') or {}
        if not pg.get('next_page') or not I: break
        time.sleep(0.7)
    return out


def seeclickfix(windows):
    from pyproj import Transformer
    TI = Transformer.from_crs(26986, 4326, always_xy=True)
    for W in windows:
        x0, y0, x1, y1 = W['box_26986']; lo0, la0 = TI.transform(x0, y0); lo1, la1 = TI.transform(x1, y1)
        a = (dt.datetime.fromisoformat(W['a']) + dt.timedelta(hours=4)).strftime('%Y-%m-%dT%H:%M:%SZ')
        b = (dt.datetime.fromisoformat(W['b']) + dt.timedelta(hours=4)).strftime('%Y-%m-%dT%H:%M:%SZ')
        I = scf_issues(dict(min_lat=la0, min_lng=lo0, max_lat=la1, max_lng=lo1, after=a, before=b))
        F = [i for i in I if SCF_FLOOD.search(f"{i['request_type']} {i['summary']} {i['description']}")]
        json.dump(dict(window_utc=[a, b], bbox_lonlat=[lo0, la0, lo1, la1], n_all=len(I), n_flood=len(F), issues=F),
                  open(os.path.join(RAW, f'scf_{W["day"]}.json'), 'w'), indent=0)
        log('  scf', W['day'], 'all', len(I), 'flood-like', len(F))


def discover(parts=('districts', 'boston311', 'seeclickfix')):
    os.makedirs(RAW, exist_ok=True)
    if 'districts' in parts:
        try: districts()
        except BaseException as e: log('districts FAILED', repr(e)[:300]); raise
    dof = district_of_fn(); C = candidates(dof)
    json.dump(C, open(os.path.join(RAW, 'candidates.json'), 'w'), indent=0)
    log('candidate days', len(C))
    W = []
    for c in C:
        d = dt.date.fromisoformat(c['day'])
        W.append(dict(day=c['day'], a=f'{d - dt.timedelta(days=1)}T18:00:00', b=f'{d + dt.timedelta(days=1)}T12:00:00', box_26986=c['box_26986']))
    for name, fn, ww in (('boston311', boston, W), ('seeclickfix', seeclickfix, [w for w, c in zip(W, C) if c['n'] >= 3])):
        if name not in parts: continue
        try: fn(ww)
        except BaseException as e: log(name, 'FAILED', repr(e)[:300])
    json.dump(dict(parts=list(parts), log=[l for l in LOG if 'http 403' not in l][-800:], made=time.strftime('%Y-%m-%d %H:%M')), open(os.path.join(RAW, f'discover_log_{"_".join(parts)}.json'), 'w'), indent=0)


# ------------------------------------------------------------------------------------------------------------------ labels
BASEMENT_RE = re.compile(r'basement|cellar|water main|main break|hydrant|sump|in (the|a) house|home(s)? flooded|parking lot only', re.I)
ROADWORD_RE = re.compile(r'flood|water|stall|disabled|impassable|closed|closure|stuck|stranded|trapped|submerged|rescue|under water|covered|washed|washout|ponding|inches|feet|foot', re.I)
PAIR_RE = r'{a}\W+(?:at|and|&|near|by|@|/|between|corner of|off)\W+(?:the\s+)?(?:intersection\s+(?:of|with)\s+)?{b}'


def rtype(text):
    t = text.lower()
    if re.search(r'\bclos(ed|ure|ing)\b|shut down|barricad|blocked off', t): return 'closed'
    if re.search(r'impassable|stuck|stranded|trapped|stall|submerged|rescu|floating|disabled|towed|swamped|engulfed', t): return 'impassable'
    return 'flooded'


def lsr_url(t):
    a = t - dt.timedelta(hours=1); b = t + dt.timedelta(hours=1)
    return f'https://mesonet.agron.iastate.edu/lsr/#BOX/{a:%Y%m%d%H%M}/{b:%Y%m%d%H%M}'


def se_url(i): return f'https://www.ncdc.noaa.gov/stormevents/eventdetails.jsp?id={i}'


JUNK = {'under', 'underneath', 'tracks', 'track', 'train', 'lane', 'lanes', 'right', 'left', 'bridge', 'rotary', 'exit', 'ramp', 'entrance', 'from', 'area',
        'building', 'house', 'home', 'sections', 'section', 'large', 'multiple', 'alley', 'portion', 'part', 'end', 'side', 'off-ramp', 'on-ramp', 'tunnel',
        'underpass', 'overpass', 'lot', 'travel', 'breakdown', 'shoulder', 'both', 'all', 'some', 'many', 'two', 'three', 'one', 'cars', 'car', 'route'}
CONNECT = {'at', 'and', 'near', 'by', 'off', 'corner', 'of', 'intersection', 'between', 'the', '&', '@', '/', ',', 'with', 'north', 'south', 'east', 'west',
           'northbound', 'southbound', 'eastbound', 'westbound', 'nb', 'sb', 'eb', 'wb', 'n', 's', 'e', 'w', 'ramp', 'on'}
PAIRWORD = {'at', 'and', 'near', 'by', 'off', 'corner', 'intersection', 'between', '&', '@', '/'}
DIRS = {'north', 'south', 'east', 'west', 'northbound', 'southbound', 'eastbound', 'westbound', 'nb', 'sb', 'eb', 'wb', 'n', 's', 'e', 'w', 'old', 'new'}


def mentions(text):
    """Road names in report text, in order: [(tok0, tok1, name, paired_with_previous_gap_ok)].  'Elm St between Oak St' -> Elm Street, Oak
    Street; 'RT 1 SOUTH AT RT 129' -> Route 1, Route 129 (pair)."""
    sys.path.insert(0, HERE); import labels_round2 as LR2
    t = re.sub(r'_', ',', text or ''); t = t.title() if t.isupper() else t
    T = [m.group(0) for m in re.finditer(r"[A-Za-z0-9'\.\-]+|[,;:&@/()]", t)]
    low = [x.lower().strip('.') for x in T]; M = []
    k = 0
    while k < len(T):
        w = low[k]
        m = re.fullmatch(r'(route|rte|rt|interstate|i|us|u\.s|state route|hwy)-?(\d{1,3}[a-z]?)?', w)
        if m and (m.group(2) or (k + 1 < len(T) and re.fullmatch(r'\d{1,3}[a-z]?', low[k + 1]))):
            n = (m.group(2) or low[k + 1]).upper(); j = k + (1 if m.group(2) else 2)
            if w.startswith('i') and not w.startswith('in'): M.append([k, j, f'I-{n}'])
            elif w != 'i': M.append([k, j, f'Route {n}'])
            k = j; continue
        if w in LR2.SUF and k > 0:
            j = k - 1; words = []
            while j >= 0 and len(words) < 3:
                x = T[j]; xl = low[j]
                if xl in LR2.STOP or xl in LR2.SUF or xl in JUNK or xl in CONNECT - DIRS or not re.match(r"[A-Z0-9]", x) or x.endswith('.') and j != k - 1: break
                if re.fullmatch(r'\d+', xl): break
                words.insert(0, x.strip('.')); j -= 1
            if words and not all(x.lower() in DIRS for x in words):
                nm = ' '.join(x.capitalize() if x.islower() else x for x in words) + ' ' + LR2.SUF[w]
                M.append([j + 1, k + 1, nm])
        k += 1
    out = []
    for i, (a, b, nm) in enumerate(M):
        ok = False
        if out:
            gap = low[out[-1][1]:a]
            ok = len(gap) <= 6 and all(g in CONNECT or re.fullmatch(r'\d+', g) for g in gap) and any(g in PAIRWORD for g in gap)
        out.append((a, b, nm, ok))
    return out


def nws_sites(r):
    """One NWS report -> list of label drafts (one per road named; 'A at B' is one pair site)."""
    sys.path.insert(0, HERE); import labels_round2 as LR2
    text = (r['text'] or '').strip()
    if not text or COASTAL_RE.search(text) or SNOW_RE.search(text): return [], 'coastal/snow'
    if BASEMENT_RE.search(text) and not re.search(r'street flooding|flooded street|impassable|closed|stuck|trapped|stranded|stall|water on (the )?(road|street)|roadway', text, re.I):
        return [], 'basement / building / main'
    if not ROADWORD_RE.search(text): return [], 'no flood words'
    ments = mentions(text)
    if not ments: return [], 'no road named'
    out = []; used = set(); i = 0
    while i < len(ments):
        a, gap_ok = ments[i][2], i + 1 < len(ments) and ments[i + 1][3]
        b = ments[i + 1][2] if gap_ok else None
        if a not in used and a != b: out.append(dict(road=a, cross=b)); used.add(a)
        if b: used.add(b); i += 2
        else: i += 1
    return out, None


def osm_spec(road):
    m = re.match(r'(I-|Route )(\d+[A-Z]?)$', road)
    if m:
        n = m.group(2); return f'ref:I {n}' if m.group(1) == 'I-' else f'ref:MA {n}|ref:US {n}|Route {n}'
    return road


LABEL_COLS = ['id', 'name', 'road', 'town', 'type', 'time_local', 'time_quality', 'lon', 'lat', 'coord_quality', 'source_url', 'quote', 'source']
Q_PATH = os.path.join(RAW, 'geocode_queries.json'); OSM_PATH = os.path.join(RAW, 'geocode_osm.json')
DROP = {}        # manual review: report key -> reason (filled after reading every draft row; see CATALOG_D456.md)
EXTRA = []       # manual review: road-level rows the parser missed: dict(key, road, cross)


def nws_reports(dof):
    """Every LSR (FLOOD / FLASH FLOOD) and Storm Events (Flood / Flash Flood) report in Districts 4-6 since 2018, with a stable key."""
    out = []
    for r in lsr_rows():
        if r['typ'] == 'HEAVY RAIN': continue
        d = dof(r['x'], r['y'])
        if d in (4, 5, 6): r.update(district=d, key=f"LSR:{r['raw']['VALID']}:{r['lon']:.2f}:{r['lat']:.2f}", url=lsr_url(r['t'])); out.append(r)
    for r in se_rows():
        d = dof(r['x'], r['y'])
        if d in (4, 5, 6): r.update(district=d, key=f"SE:{r['event_id']}", url=se_url(r['event_id'])); out.append(r)
    return out


def town_of_report(r):
    c = re.sub(r'^\d+\s+[NSEW]{1,3}\s+', '', r['city'] or '', flags=re.I).title()
    return c


def queries():
    """Label drafts for every District 4-6 NWS report on a candidate day -> geocode queries (proto/label_geocode.py) + drafts."""
    dof = district_of_fn(); days = {c['day'] for c in json.load(open(os.path.join(RAW, 'candidates.json')))}
    Q, drafts, skipped = [], [], []
    for r in nws_reports(dof):
        day = (r['t'] - dt.timedelta(hours=4)).date().isoformat()
        if day not in days: continue
        if r['key'] in DROP: skipped.append((r['key'], DROP[r['key']])); continue
        S, why = nws_sites(r)
        S += [dict(road=e['road'], cross=e.get('cross')) for e in EXTRA if e['key'] == r['key']]
        if not S: skipped.append((r['key'], why, (r['text'] or '')[:160])); continue
        town = town_of_report(r)
        for k, s_ in enumerate(S):
            key = f"{r['key']}#{k}"
            q = dict(key=key, town=town, a=osm_spec(s_['road']), b=osm_spec(s_['cross']) if s_['cross'] else None, near=[round(r['lon'], 5), round(r['lat'], 5)])
            Q.append(q); drafts.append(dict(key=key, report=r['key'], day=day, src=r['src'], t_utc=r['t'].strftime('%Y-%m-%dT%H:%MZ'), town=town, district=r['district'],
                                             road=s_['road'], cross=s_['cross'], type=rtype(r['text']), quote=(r['text'] or '').strip()[:400], url=r['url'],
                                             nws_lon=r['lon'], nws_lat=r['lat'], precise=(r['src'] == 'StormEvents')))
    json.dump(Q, open(Q_PATH, 'w'), indent=0); json.dump(drafts, open(os.path.join(RAW, 'nws_drafts.json'), 'w'), indent=0)
    json.dump(skipped, open(os.path.join(RAW, 'nws_skipped.json'), 'w'), indent=0)
    print(len(Q), 'queries;', len(skipped), 'reports without a road-level site')


def place(d, G):
    """Geocode result -> (lon, lat, coord_quality, how) following labels_expand: pair gap <= 80 m -> exact; nearest vertex of the road to the
    NWS point (< 1500 m) -> approx; road centroid vertex for a road < 3 km -> approx; else None (town)."""
    from pyproj import Transformer
    r = G.get(d['key']) or {}
    if d.get('cross') and (r.get('pair') or {}).get('candidates'):
        C = r['pair']['candidates']; c = min(C, key=lambda c: c.get('to_near_m', 0) + 2 * c['gap_m'])
        if c['gap_m'] <= 80 and c.get('to_near_m', 0) <= 4000: return c['lonlat'][0], c['lonlat'][1], 'exact', f"OSM intersection {d['road']} / {d['cross']} (gap {c['gap_m']} m)"
    sg = r.get('single')
    if sg:
        if sg.get('nearest_vertex') and sg.get('nearest_m', 1e9) < 1500: v = sg['nearest_vertex']; return v[0], v[1], 'approx', f"OSM {d['road']} vertex nearest the NWS point ({sg['nearest_m']} m)"
        if sg.get('length_m', 1e9) < 3000: v = sg['centroid_vertex']; return v[0], v[1], 'approx', f"OSM {d['road']} centroid vertex (road {sg['length_m']} m)"
    return None


SCF_ROAD_RE = re.compile(r'(street|road|roadway|intersection|lane|avenue|ave|st|rd) (is |was |were |are |completely |totally )*(flood|under water|impassable)|'
                         r'flooded (street|road|roadway|intersection)|(street|road|roadway) flooding|'
                         r'(water|flooding|flood water|floodwater|ponding|puddle)s? (is |was )?(on|in|across|over|covering|throughout) (the |our |this )?(entire )?'
                         r'(street|road|roadway|intersection|travel lane|crosswalk)|impassable|cars? (stuck|stalled)|washed out|washout', re.I)
NOT_ROAD_RE = re.compile(r'basement|cellar|my (house|home|yard|property)|back ?yard|front yard|garage|sump|leak|water main|hydrant|sewer back ?up|toilet|'
                         r'odor|smell|mosquito|pothole only|dumping|trash|flood ?lights?|install .{0,20}floods|food establishment|sprinkler|parking lot|'
                         r'\bpark\b|playground|field|sidewalk only|sewer back|bathroom', re.I)
BOS_DEFAULT = (42.3594, -71.0587)


def bos_rows(day):
    """Boston 311 requests of a candidate window that report flooding on a street (not basements / private property / mains)."""
    p = os.path.join(RAW, f'boston311_{day}.json')
    if not os.path.exists(p): return []
    out = []
    for x in json.load(open(p))['rows']:
        lat = x.get('latitude') or x.get('lat'); lon = x.get('longitude') or x.get('long') or x.get('lon')
        try: lat, lon = float(lat), float(lon)
        except (TypeError, ValueError): continue
        if abs(lat - BOS_DEFAULT[0]) < 1e-3 and abs(lon - BOS_DEFAULT[1]) < 1e-3: continue
        title = ' '.join(str(x.get(k) or '') for k in ('case_title', 'type', 'service_name', 'description', 'subject'))
        if not (re.search(r'roadway flooding|street flooding', title, re.I) or SCF_ROAD_RE.search(title)) or NOT_ROAD_RE.search(title): continue
        t = str(x.get('open_dt') or x.get('open_date') or x.get('requested_datetime') or '').replace('T', ' ')[:16]
        try: tl = dt.datetime.strptime(t, '%Y-%m-%d %H:%M')
        except ValueError: continue
        cid = x.get('case_enquiry_id') or x.get('case_id') or x.get('service_request_id') or x.get('_id')
        import html as _h
        loc = re.sub(r'\s+', ' ', _h.unescape(str(x.get('location') or x.get('address') or '')))
        street = re.sub(r'^(INTERSECTION of |[\d\-]+[A-Z]?\s+)', '', loc, flags=re.I).split('&')[0].split(',')[0]
        street = re.sub(r'\s+(Boston|Brighton|Roxbury|Dorchester|Mattapan|Jamaica Plain|West Roxbury|Roslindale|Hyde Park|Charlestown|East Boston|South Boston|'
                        r'Allston|Back Bay|South End)\b.*$', '', street).strip()
        out.append(dict(src='Boston311', key=f'B311:{cid}', t=tl + dt.timedelta(hours=4), lon=lon, lat=lat, town=str(x.get('neighborhood') or 'Boston').title() or 'Boston',
                        road=street.title().strip(), type='flooded', coord='exact', quote=f"{x.get('case_title') or x.get('type')}: {loc}"[:300],
                        url=f'https://311.boston.gov/tickets/{cid}', time_quality='report'))
    return out


def scf_rows(day):
    p = os.path.join(RAW, f'scf_{day}.json')
    if not os.path.exists(p): return []
    out = []
    for i in json.load(open(p))['issues']:
        txt = f"{i.get('summary') or ''}. {i.get('description') or ''}"
        if not (SCF_ROAD_RE.search(txt) or re.search(r'street flooding|roadway flooding|road flooding', str(i.get('request_type')), re.I)) or NOT_ROAD_RE.search(txt) \
                or i.get('lat') is None: continue
        t = dt.datetime.strptime(i['created_at'][:19], '%Y-%m-%dT%H:%M:%S'); off = i['created_at'][19:]
        if off and off[0] in '+-': t = t - dt.timedelta(hours=int(off[1:3]) * (1 if off[0] == '+' else -1))
        addr = i.get('address') or ''; parts = [x.strip() for x in addr.split(',')]
        town = re.sub(r'^(city|town) of\s+|,?\s*(ma|massachusetts)$|\s*(town hall|dpw)$', '', str(i.get('organization') or ''), flags=re.I).strip()
        road = re.sub(r'^\d+[A-Za-z]?\s+', '', parts[0]) if parts else ''
        if town and road.lower().endswith(' ' + town.lower()): road = road[:-len(town) - 1]
        road = re.sub(r'\s+(Heights|Highlands|Center|Centre)$', '', road)
        out.append(dict(src='SeeClickFix', key=f"SCF:{i['id']}", t=t, lon=float(i['lng']), lat=float(i['lat']), town=town, road=road, type=rtype(txt),
                        coord='exact', quote=f"{i.get('request_type')}: {txt}"[:300], url=i.get('html_url') or f"https://seeclickfix.com/issues/{i['id']}",
                        time_quality='report'))
    return out


def build():
    """Geocoded drafts + Boston 311 + SeeClickFix -> storms (PROTOCOL.md Transfer test T-2) -> label CSVs + docs/proto/obs/catalog_d456.json."""
    from pyproj import Transformer
    from scipy.spatial import cKDTree
    sys.path.insert(0, HERE); import score_v2 as SV
    T = Transformer.from_crs(4326, 26986, always_xy=True); TI = Transformer.from_crs(26986, 4326, always_xy=True)
    dof = district_of_fn(); G = json.load(open(OSM_PATH)) if os.path.exists(OSM_PATH) else {}
    drafts = json.load(open(os.path.join(RAW, 'nws_drafts.json'))); cands = json.load(open(os.path.join(RAW, 'candidates.json')))
    D3 = json.load(open(os.path.join(ROOT, 'docs', 'proto', 'obs', 'catalog.json')))['events']; used_ids = {e['id'] for e in D3}
    reports = {r['key']: r for r in nws_reports(dof)}
    audit = []; storms = []
    by_day = {}
    for d in drafts:
        if d['report'] in DROP: continue
        pl = place(d, G); t = dt.datetime.strptime(d['t_utc'], '%Y-%m-%dT%H:%MZ')
        row = dict(src='LSR' if d['src'] == 'LSR' else 'StormEvents', key=d['key'], report=d['report'], t=t, town=d['town'], road=d['road'], cross=d['cross'],
                   type=d['type'], quote=d['quote'], url=d['url'], time_quality='report')
        if pl: row.update(lon=pl[0], lat=pl[1], coord=pl[2], how=pl[3])
        else: row.update(lon=d['nws_lon'], lat=d['nws_lat'], coord='town', how='not placed (OSM found no unique location): NWS point')
        by_day.setdefault(d['day'], []).append(row)
    for c in cands:
        by_day.setdefault(c['day'], [])
        by_day[c['day']] += bos_rows(c['day']) + scf_rows(c['day'])
    for day in sorted(by_day):
        R = by_day[day]
        for r in R:
            r['x'], r['y'] = T.transform(r['lon'], r['lat']); r['district'] = dof(r['x'], r['y'])
        pool = [r for r in R if r['coord'] != 'town' and r['district'] in (4, 5, 6)]
        taken = []
        for attempt in range(3):
            P = [r for r in pool if r['key'] not in {k for b in taken for k in b['keys']}]
            if not any(r['src'] in ('LSR', 'StormEvents') for r in P): break
            xy = np.array([[r['x'], r['y']] for r in P]); nws = np.array([r['src'] in ('LSR', 'StormEvents') for r in P])
            cl = SV.link_clusters(xy, SV.SITE_LINK_M)
            best = None
            # candidate origins: every 1 km offset that keeps at least one NWS site inside (vectorised over a coarse 1 km lattice)
            gx = np.arange(int(xy[:, 0].min() // 1000) - 19, int(xy[:, 0].max() // 1000) + 1) * 1000.0
            gy = np.arange(int(xy[:, 1].min() // 1000) - 19, int(xy[:, 1].max() // 1000) + 1) * 1000.0
            for x0 in gx:
                inx = (xy[:, 0] >= x0) & (xy[:, 0] < x0 + 20000)
                if not (inx & nws).any(): continue
                for y0 in gy:
                    m = inx & (xy[:, 1] >= y0) & (xy[:, 1] < y0 + 20000)
                    if not (m & nws).any(): continue
                    if dof(x0 + 10000, y0 + 10000) not in (4, 5, 6): continue
                    if any(e.get('t0') and abs((dt.date.fromisoformat(e['t0'][:10]) - dt.date.fromisoformat(day)).days) <= 1 and
                           x0 < e['box_26986'][2] and x0 + 20000 > e['box_26986'][0] and y0 < e['box_26986'][3] and y0 + 20000 > e['box_26986'][1] for e in D3): continue
                    if any(x0 < b['box'][2] and x0 + 20000 > b['box'][0] and y0 < b['box'][3] and y0 + 20000 > b['box'][1] for b in taken): continue
                    n = len(np.unique(cl[m])); cen = abs(xy[m, 0].mean() - x0 - 10000) + abs(xy[m, 1].mean() - y0 - 10000)
                    sc = (n, -cen)
                    if best is None or sc > best[0]: best = (sc, [x0, y0, x0 + 20000, y0 + 20000])
            if best is None: break
            box = best[1]; inb = lambda r: box[0] <= r['x'] < box[2] and box[1] <= r['y'] < box[3]
            nw = [r for r in R if inb(r) and r['src'] in ('LSR', 'StormEvents') and r['district'] in (4, 5, 6)]
            tt = sorted(r['t'] for r in nw)
            t0 = (tt[0] - dt.timedelta(hours=7)).replace(minute=0); hours = max(18, int(math.ceil((tt[-1] - t0).total_seconds() / 3600 + 5)))
            w0, w1 = t0, t0 + dt.timedelta(hours=hours)
            keep = [r for r in R if inb(r) and r['district'] in (4, 5, 6) and
                    ((r['src'] in ('LSR', 'StormEvents')) or (w0 - dt.timedelta(hours=2) <= r['t'] <= w1 + dt.timedelta(hours=12)))]
            # all NWS reports in box + window (also those without a road) for the scope checks
            allrep = [q for q in reports.values() if box[0] <= q['x'] < box[2] and box[1] <= q['y'] < box[3] and w0 <= q['t'] <= w1]
            coastal = sum(bool(COASTAL_RE.search((q['text'] or '') + ' ' + (q.get('episode') or ''))) for q in allrep)
            snow = sum(bool(SNOW_RE.search((q['text'] or '') + ' ' + (q.get('episode') or ''))) for q in allrep)
            # dedupe: same road (or same pair) within 1 km -> one row (best coordinate, earliest report)
            rank = dict(exact=0, approx=1, town=2); keep.sort(key=lambda r: (rank[r['coord']], r['t']))
            ded = []
            for r in keep:
                nm = re.sub(r'[^a-z0-9]', '', (r['road'] or '').lower())
                if r['src'] in ('LSR', 'StormEvents') and nm and any(re.sub(r'[^a-z0-9]', '', (q['road'] or '').lower()) == nm and
                                                                   q['src'] in ('LSR', 'StormEvents') and math.hypot(q['x'] - r['x'], q['y'] - r['y']) < 1000 for q in ded): continue
                ded.append(r)
            road = [r for r in ded if r['coord'] != 'town']
            ncl = len(np.unique(SV.link_clusters(np.array([[r['x'], r['y']] for r in road]).reshape(-1, 2), SV.SITE_LINK_M))) if road else 0
            info = dict(day=day, box=box, t0=t0, hours=hours, rows=ded, n_sites=ncl, n_nws_reports=len(allrep), coastal=coastal, snow=snow,
                        keys=[r['key'] for r in keep])
            taken.append(info)
        storms += taken
    # one event that crosses local midnight gives two candidate days: a box overlapping an earlier box whose window it continues (starts before
    # that window's end + 12 h) is merged into it (rows inside the earlier box kept, window extended)
    merged = []
    for b in sorted(storms, key=lambda b: b['t0']):
        a = next((a for a in merged if b['box'][0] < a['box'][2] and b['box'][2] > a['box'][0] and b['box'][1] < a['box'][3] and b['box'][3] > a['box'][1]
                  and b['t0'] <= a['t0'] + dt.timedelta(hours=a['hours'] + 12)), None)
        if a is None: merged.append(b); continue
        inb = lambda r: a['box'][0] <= r['x'] < a['box'][2] and a['box'][1] <= r['y'] < a['box'][3]
        have = {r['key'] for r in a['rows']}
        for r in b['rows']:
            nm = re.sub(r'[^a-z0-9]', '', (r['road'] or '').lower())
            if r['key'] in have or not inb(r): continue
            if r['src'] in ('LSR', 'StormEvents') and nm and any(re.sub(r'[^a-z0-9]', '', (q['road'] or '').lower()) == nm and q['src'] in ('LSR', 'StormEvents')
                                                               and math.hypot(q['x'] - r['x'], q['y'] - r['y']) < 1000 for q in a['rows']): continue
            a['rows'].append(r)
        a['hours'] = max(a['hours'], int(math.ceil((b['t0'] + dt.timedelta(hours=b['hours']) - a['t0']).total_seconds() / 3600)))
        a['n_nws_reports'] += b['n_nws_reports']; a['coastal'] += b['coastal']; a['snow'] += b['snow']; a['keys'] += b['keys']
        a.setdefault('merged_days', []).append(b['day'])
        road = [r for r in a['rows'] if r['coord'] != 'town']
        a['n_sites'] = len(np.unique(SV.link_clusters(np.array([[r['x'], r['y']] for r in road]).reshape(-1, 2), SV.SITE_LINK_M))) if road else 0
    storms = merged
    for b in storms:
        ok = b['n_sites'] >= 3 and b['coastal'] <= 0.5 * max(1, b['n_nws_reports']) and b['snow'] == 0
        b['selected'] = ok
        b['why'] = 'selected' if ok else ('< 3 road-level sites' if b['n_sites'] < 3 else 'coastal' if b['coastal'] > 0.5 * max(1, b['n_nws_reports']) else 'snowmelt / ice')
    sel = [b for b in storms if b['selected']]
    letters = 'efghknpqrstuvxyz'; events = []
    for b in sorted(sel, key=lambda b: (b['t0'], b['box'][0])):
        mon = b['t0'] - dt.timedelta(hours=4); base = mon.strftime('%b').lower() + mon.strftime('%Y')
        sid = next(base + L for L in letters if base + L not in used_ids); used_ids.add(sid)
        road = [r for r in b['rows'] if r['coord'] != 'town']
        tc = {}; tn = {}
        for r in road:
            if r['town']: tc[r['town']] = tc.get(r['town'], 0) + 1
            if r['src'] in ('LSR', 'StormEvents') and r['town']: tn[r['town']] = tn.get(r['town'], 0) + 1
        area = re.sub(r'[^a-z]', '', max(tn or tc or {'east': 1}, key=(tn or tc or {'east': 1}).get).lower()) or 'east'
        rows = []
        for k, r in enumerate(sorted(b['rows'], key=lambda r: r['t'])):
            tl = r['t'] - dt.timedelta(hours=4)
            rows.append(dict(id=f'{sid.upper()}-{k + 1:02d}', name=f"{r['road']}{' at ' + r['cross'] if r.get('cross') else ''}: {r['type']}", road=r['road'],
                             town=r['town'], type=r['type'], time_local=tl.strftime('%Y-%m-%dT%H:%M'), time_quality=r['time_quality'],
                             lon=f"{r['lon']:.5f}", lat=f"{r['lat']:.5f}", coord_quality=r['coord'], source_url=r['url'], quote=r['quote'], source=r['src']))
            audit.append(dict(storm=sid, id=rows[-1]['id'], key=r['key'], how=r.get('how', 'source coordinates'), coord_quality=r['coord']))
        path = os.path.join(HERE, 'data', f'labels_{sid}_{area}.csv')
        with open(path, 'w', newline='') as f:
            w = csv.DictWriter(f, fieldnames=LABEL_COLS, lineterminator='\r\n'); w.writeheader(); w.writerows(rows)
        lo0, la0 = TI.transform(b['box'][0], b['box'][1]); lo1, la1 = TI.transform(b['box'][2], b['box'][3])
        tt = sorted(r['t'] for r in b['rows'] if r['src'] in ('LSR', 'StormEvents'))
        era = 'aws' if b['t0'] >= dt.datetime(2020, 10, 14) else 'iem'
        q = {}; so = {}
        for r in b['rows']: q[r['coord']] = q.get(r['coord'], 0) + 1; so[r['src']] = so.get(r['src'], 0) + 1
        events.append(dict(id=sid, area=area, district=dof(b['box'][0] + 10000, b['box'][1] + 10000), date_local=b['day'], t0=b['t0'].strftime('%Y-%m-%dT%H:00Z'),
                           hours=b['hours'], first_report_utc=tt[0].strftime('%Y-%m-%dT%H:%MZ'), last_report_utc=tt[-1].strftime('%Y-%m-%dT%H:%MZ'),
                           box_26986=[int(v) for v in b['box']], bbox_lonlat=[round(lo0, 3), round(la0, 3), round(lo1, 3), round(la1, 3)],
                           start=(b['t0'] - dt.timedelta(days=1)).strftime('%Y-%m-%d'), end=(b['t0'] + dt.timedelta(hours=b['hours']) + dt.timedelta(days=1)).strftime('%Y-%m-%d'),
                           towns=sorted(tc), counts=dict(label_rows=len(rows), road_level_rows=len(road), sites_150m=b['n_sites'], nws_reports_in_box=b['n_nws_reports'],
                                                         coastal_reports=b['coastal']),
                           label_coord_quality=q, sources=so, era=era,
                           mrms='AWS noaa-mrms-pds MultiSensor_QPE_01H_Pass2' if era == 'aws' else 'IEM mtarchive GaugeCorr_QPE_01H (w9 fallback, as the District 3 2018-2020 storms)',
                           labels=os.path.relpath(path, ROOT), role='d456 transfer test (never tuned on)'))
    json.dump(dict(about='District 4-6 transfer-test storms (docs/proto/PROTOCOL.md "Transfer test", T-2); built by proto/transfer_d456.py build',
                   made=time.strftime('%Y-%m-%d'), events=events), open(os.path.join(ROOT, 'docs', 'proto', 'obs', 'catalog_d456.json'), 'w'), indent=1)
    json.dump(dict(audit=audit, considered=[dict(day=b['day'], box=b['box'], t0=b['t0'].strftime('%Y-%m-%dT%H:00Z'), hours=b['hours'], sites=b['n_sites'],
                                                 nws_reports=b['n_nws_reports'], coastal=b['coastal'], snow=b['snow'], selected=b['selected'], why=b['why'],
                                                 merged_days=b.get('merged_days'))
                                            for b in storms]), open(os.path.join(RAW, 'build_audit.json'), 'w'), indent=0, default=str)
    print(len(events), 'storms;', sum(e['counts']['sites_150m'] for e in events), 'sites')
    for e in events: print(e['id'], e['area'], e['district'], e['t0'], e['hours'], e['box_26986'], e['counts'], e['sources'])


def report():
    """docs/proto/obs/CATALOG_D456.md from catalog_d456.json + build_audit.json."""
    C = json.load(open(os.path.join(ROOT, 'docs', 'proto', 'obs', 'catalog_d456.json')))['events']; A = json.load(open(os.path.join(RAW, 'build_audit.json')))
    from collections import Counter
    L = ['# District 4-6 transfer-test storm catalogue (`catalog_d456.json`)', '',
         'Built by `proto/transfer_d456.py` (`discover` on Actions, `queries`, label geocode on Actions, `build`) under the pre-registered rules of',
         '`docs/proto/PROTOCOL.md` "Transfer test (Districts 4-6)" (T-2). These storms are **test-only**: the frozen District 3 model is run on them',
         'once and nothing is tuned on them. Label files: `proto/data/labels_<id>_<area>.csv` (same columns as District 3).', '']
    tot = Counter(); src = Counter(); q = Counter()
    for e in C:
        tot['storms'] += 1; tot['rows'] += e['counts']['label_rows']; tot['road'] += e['counts']['road_level_rows']; tot['sites'] += e['counts']['sites_150m']
        src.update(e['sources']); q.update(e['label_coord_quality'])
    L += [f"**{tot['storms']} storms, {tot['sites']} road-level sites** (150 m clusters of non-`town` rows), {tot['road']} road-level rows, {tot['rows']} label rows in all.",
          f"Rows by source: {', '.join(f'{k} {v}' for k, v in src.most_common())}. Coordinates: {', '.join(f'{k} {v}' for k, v in q.most_common())}.", '',
          '| id | district | date (local) | era / rain | box EPSG:26986 | t0 UTC / h | sites | rows (road-level) | sources | towns |', '|' + '---|' * 10]
    for e in C:
        L.append(f"| {e['id']} | {e['district']} | {e['date_local']} | {e['era']} | {','.join(map(str, e['box_26986']))} | {e['t0']} / {e['hours']} | "
                 f"{e['counts']['sites_150m']} | {e['counts']['label_rows']} ({e['counts']['road_level_rows']}) | {', '.join(f'{k} {v}' for k, v in e['sources'].items())} | "
                 f"{', '.join(e['towns'][:6])}{' …' if len(e['towns']) > 6 else ''} |")
    rej = [c for c in A['considered'] if not c['selected']]
    L += ['', f"**Considered and not selected: {len(rej)} boxes** (reason: {', '.join(f'{k} {v}' for k, v in Counter(c['why'] for c in rej).most_common())}).",
          'Every candidate day (>= 2 District 4-6 flood reports in LSR + Storm Events since 2018) was searched for up to three non-overlapping 20 x 20 km',
          'boxes; the full list with counts is `docs/proto/transfer/raw/build_audit.json`.', '',
          '## How the labels were made', '',
          '- **NWS reports** (IEM LSR archive, NCEI Storm Events; `docs/proto/obs/catalog/*_ma_flood_2014_2026.csv`): every FLOOD / FLASH FLOOD report whose',
          '  point lies in District 4, 5 or 6 (MassGIS `MassDOT_Highway_Districts` polygons) was split into the roads it names (one row per road; "A at B"',
          '  is one intersection row) by `transfer_d456.mentions`. Dropped: tide / surge / coastal / wave and snowmelt / ice-jam texts, basement / building /',
          '  water-main reports without a road impact, texts without a flood word. Draft rows: `raw/nws_drafts.json`; reports without a road: `raw/nws_skipped.json`.',
          '- **Placement** (OSM via `proto/label_geocode.py`, `raw/geocode_osm.json`): intersection within 80 m -> `exact`; the road vertex nearest the NWS',
          '  point (< 1.5 km) or the centroid vertex of a road shorter than 3 km -> `approx`; otherwise the row stays `town` at the NWS point and is not matched.',
          '  Same road named twice in one storm within 1 km (an LSR and its Storm Events copy) -> one row (the better coordinate).',
          '- **Boston 311** (data.boston.gov CKAN, full-text "flood"): requests whose type/title says flooding, at the city-geocoded address (`exact`), opened',
          '  between t0 - 2 h and t0 + hours + 12 h. Basement, property, flood-light and food-establishment requests are excluded.',
          '- **SeeClickFix** (api/v2 issues in the window and box): issues whose text says the street / road flooded or had standing water (not chronic',
          '  drain complaints without a flood word, not private property), at the reporter\'s pin (`exact`), same time window as 311.',
          '- News was not searched systematically for these districts (time); no news rows.', '',
          '## Storm windows and boxes', '',
          '- Box: the 1 km-aligned 20 x 20 km square with the most road-level sites that holds >= 1 NWS road report, centre in Districts 4-6, not overlapping a',
          '  District 3 catalogue box of the same date (+-1 day). t0 = first NWS report in the box - 7 h; hours = max(18, last NWS report - t0 + 5 h).',
          '- Selected when >= 3 road-level sites (150 m clusters), coastal texts <= half of the NWS reports in the box and window, and no snowmelt / ice text.',
          '- Rain: MRMS hourly QPE from AWS Pass2 (from 14 Oct 2020) or the IEM GaugeCorr archive before, exactly as the District 3 2018-2020 storms.', '']
    open(os.path.join(ROOT, 'docs', 'proto', 'obs', 'CATALOG_D456.md'), 'w').write('\n'.join(L) + '\n'); print('\n'.join(L[:12]))


# ------------------------------------------------------------------------------------------------------------------ roads (OSM)
OSM_CLASSES = ('motorway', 'trunk', 'primary', 'secondary', 'tertiary', 'unclassified', 'residential',
               'motorway_link', 'trunk_link', 'primary_link', 'secondary_link', 'tertiary_link')     # as sim/colab/vt_inputs.py
AADT_DEFAULT = {2: 20000, 1: 5000, 0: 1000}
SEG_MAX_M = 1000.0
I_RE = re.compile(r'^\s*I\s*-?\s*(\d{1,3})\s*$', re.I)
RT_RE = re.compile(r'^\s*(?:US|MA|SR|Route|RT)\s*-?\s*(\d{1,3}[A-Z]?)\s*$', re.I)


def d3_class(tags):
    """District 3 graph convention (docs/graph_segments.json): cls 2 = Interstate mainline (road 'I-nn'), 1 = other numbered US / MA route
    mainline ('Route nn'), 0 = everything else (local streets, ramps)."""
    hw = tags.get('highway', ''); refs = [r.strip() for r in (tags.get('ref') or '').split(';') if r.strip()]; nm = tags.get('name') or ''
    if hw.endswith('_link'): return 0, (nm or ('Ramp-' + '/'.join(refs) if refs else 'Ramp'))
    for r in refs:
        m = I_RE.match(r)
        if m and hw in ('motorway', 'trunk'): return 2, f'I-{m.group(1)}'
    for r in refs:
        m = RT_RE.match(r)
        if m: return 1, f'Route {m.group(1).upper()}'
    return 0, nm


def town_polys():
    """MassGIS survey-level town polygons (EPSG:26986) -> (names, prepared shapes); None if unavailable."""
    from shapely.geometry import Polygon
    from shapely.ops import unary_union
    from shapely.prepared import prep
    for u in TOWN_ZIPS:
        r = get(u, timeout=300, tries=2)
        if r is None: continue
        try:
            T = read_shp_zip(r.content); lay = pick_town_layer(T)
            nk = town_key(lay['fields'])
            out = []
            for rec, rings, st in lay['rows']:
                polys = [Polygon(r_).buffer(0) for r_ in rings if len(r_) >= 4]
                if polys and nk: g = unary_union(polys); out.append((str(rec[nk]).title(), g, prep(g)))
            log('town polygons', len(out), 'from', u); return out
        except Exception as e: log('town polygons failed', u, repr(e)[:200])
    return None


def overpass(q):
    for attempt in range(4):
        for url in ('https://overpass-api.de/api/interpreter', 'https://lz4.overpass-api.de/api/interpreter', 'https://overpass.kumi.systems/api/interpreter',
                    'https://overpass.private.coffee/api/interpreter'):
            try:
                import requests
                r = requests.post(url, data={'data': q}, headers=UA, timeout=400)
                if r.status_code == 200: return r.json()['elements']
                log('  overpass', url, r.status_code, r.text[:120])
            except Exception as e: log('  overpass', url, repr(e)[:120])
        time.sleep(45)
    raise SystemExit('all Overpass mirrors refused')


def encode(lon, lat):
    a = np.round(np.asarray(lon) * 1e5).astype(np.int64); b = np.round(np.asarray(lat) * 1e5).astype(np.int64)
    da = np.r_[a[0], np.diff(a)]; db = np.r_[b[0], np.diff(b)]; out = np.empty(2 * len(a), np.int64); out[0::2] = da; out[1::2] = db
    return [int(v) for v in out]


def build_segments(els, towns=None):
    """OSM ways -> docs/graph_segments.json layout (as sim/colab/vt_inputs.build_segments, District 3 class convention).  Ways are cut at
    every node shared by two road ways and wherever a piece passes SEG_MAX_M; segments sharing an end node are linked."""
    from pyproj import Transformer
    from shapely.geometry import Point
    tr = Transformer.from_crs(4326, 26986, always_xy=True)
    nodes = {e['id']: (e['lon'], e['lat']) for e in els if e['type'] == 'node'}
    ways = [e for e in els if e['type'] == 'way' and (e.get('tags') or {}).get('highway') in OSM_CLASSES and all(n in nodes for n in e['nodes'])]
    use = {}
    for w in ways:
        for k, nid in enumerate(w['nodes']): use[nid] = use.get(nid, 0) + (2 if k in (0, len(w['nodes']) - 1) else 1)
    geo, props, ends = [], dict(road=[], town=[], cls=[], low=[], len=[], aadt=[]), []
    cache = {}

    def town(x, y):
        if not towns: return ''
        k = (int(x // 500), int(y // 500))
        if k in cache and cache[k] is not None and cache[k][2].contains(Point(x, y)): return cache[k][0]
        p = Point(x, y)
        for t in towns:
            if t[2].contains(p): cache[k] = t; return t[0]
        return ''
    for w in ways:
        cls, road = d3_class(w['tags'])
        ll = np.array([nodes[n] for n in w['nodes']]); X, Y = tr.transform(ll[:, 0], ll[:, 1]); step = np.r_[0, np.hypot(np.diff(X), np.diff(Y))]
        s = 0; acc = 0.0
        for k in range(1, len(ll)):
            acc += step[k]
            if k == len(ll) - 1 or use.get(w['nodes'][k], 0) >= 2 or acc >= SEG_MAX_M - 0.5:
                geo.append([encode(ll[s:k + 1, 0], ll[s:k + 1, 1])]); ends.append((w['nodes'][s], w['nodes'][k])); j = (s + k) // 2
                props['road'].append(road); props['town'].append(town(X[j], Y[j])); props['cls'].append(cls); props['low'].append(0)
                props['len'].append(int(round(acc))); props['aadt'].append(AADT_DEFAULT[cls]); s = k; acc = 0.0
    by_node = {}
    for i, (a, b) in enumerate(ends):
        by_node.setdefault(a, set()).add(i); by_node.setdefault(b, set()).add(i)
    links = sorted({(min(i, j), max(i, j)) for S_ in by_node.values() for i in S_ for j in S_ if i != j})
    return dict(n=len(geo), geo=geo, props=props, links=[list(l) for l in links],
                source='OpenStreetMap via Overpass (ODbL), ' + time.strftime('%Y-%m-%d') + '; split at junctions and ~1 km; District 3 class convention '
                       '(2 Interstate I-nn, 1 numbered route, 0 other); aadt = class default; town = MassGIS survey town polygon')


def roads(box, out):
    from pyproj import Transformer
    TI = Transformer.from_crs(26986, 4326, always_xy=True); x0, y0, x1, y1 = box
    lo0, la0 = TI.transform(x0 - 1500, y0 - 1500); lo1, la1 = TI.transform(x1 + 1500, y1 + 1500)
    hw = '|'.join(OSM_CLASSES)
    els = overpass(f'[out:json][timeout:300];(way["highway"~"^({hw})$"]({la0},{lo0},{la1},{lo1}););(._;>;);out body;')
    S = build_segments(els, town_polys()); os.makedirs(out, exist_ok=True)
    import gzip
    with gzip.open(os.path.join(out, 'roads_graph.json.gz'), 'wt') as f: json.dump(S, f, separators=(',', ':'))
    cls = np.asarray(S['props']['cls'])
    info = dict(segments=S['n'], by_class={k: int((cls == k).sum()) for k in (0, 1, 2)}, links=len(S['links']), box=list(box),
                towns=sorted({t for t in S['props']['town'] if t}))
    json.dump(info, open(os.path.join(out, 'roads_info.json'), 'w'), indent=0); log('roads', info)
    return os.path.join(out, 'roads_graph.json.gz')


# ---- OSM from the Geofabrik Massachusetts extract (Overpass was too slow for ~1,100 label queries and ~50 boxes) ----
GEOFABRIK = 'https://download.geofabrik.de/north-america/us/massachusetts-latest.osm.pbf'
GEO_HW = set(OSM_CLASSES) | {'living_street', 'service', 'road', 'busway'}       # for placing labels only (the model network is OSM_CLASSES)


def osm_ways(pbf, bbox=(-71.95, 41.2, -69.85, 42.9)):
    """Every highway way in bbox from a .osm.pbf: list of dict(id, tags, nodes, lon, lat) (pyosmium, node locations)."""
    import osmium
    out = []

    class H(osmium.SimpleHandler):
        def way(self, w):
            hw = w.tags.get('highway')
            if hw not in GEO_HW: return
            try: ll = [(n.lon, n.lat) for n in w.nodes]; ids = [n.ref for n in w.nodes]
            except osmium.InvalidLocationError: return
            if len(ll) < 2: return
            a = np.array(ll)
            if a[:, 0].max() < bbox[0] or a[:, 0].min() > bbox[2] or a[:, 1].max() < bbox[1] or a[:, 1].min() > bbox[3]: return
            out.append(dict(id=w.id, tags={k: w.tags.get(k) for k in ('highway', 'name', 'ref', 'bridge') if w.tags.get(k)}, nodes=ids, ll=a))
    H().apply_file(pbf, locations=True)
    log('osm ways', len(out)); return out


def osm_geocode(pbf):
    """proto/label_geocode.py semantics (pair / single, ways within 4 km of the NWS point) on the local extract -> raw/geocode_osm.json."""
    sys.path.insert(0, HERE); import label_geocode as LG
    from pyproj import Transformer
    T = Transformer.from_crs(4326, 26986, always_xy=True)
    W = osm_ways(pbf); byname = {}; byref = {}
    for i, w in enumerate(W):
        if w['tags'].get('name'): byname.setdefault(w['tags']['name'].lower(), []).append(i)
        for r in (w['tags'].get('ref') or '').split(';'):
            if r.strip(): byref.setdefault(re.sub(r'\s+', ' ', r.strip().upper()), []).append(i)
        x, y = T.transform(w['ll'][:, 0], w['ll'][:, 1]); w['xy'] = np.column_stack([x, y])

    def match(spec, near):
        ids = set()
        for sp in spec.split('|'):
            sp = sp.strip()
            if sp.startswith('ref:'): ids |= set(byref.get(re.sub(r'\s+', ' ', sp[4:].strip().upper()), []))
            else: ids |= set(byname.get(sp.lower(), []))
        nx, ny = T.transform(*near)
        els = []
        for i in ids:
            w = W[i]
            if np.hypot(w['xy'][:, 0] - nx, w['xy'][:, 1] - ny).min() <= 4000:
                els.append(dict(id=w['id'], tags=w['tags'], nodes=w['nodes'], geometry=[dict(lon=float(a), lat=float(b)) for a, b in w['ll']]))
        return els
    Q = json.load(open(Q_PATH)); R = json.load(open(OSM_PATH)) if os.path.exists(OSM_PATH) else {}; n = 0
    for q in Q:
        k = q['key']
        if k in R and (R[k].get('pair') or R[k].get('single')): continue
        r = dict(q=q, src='Geofabrik massachusetts-latest.osm.pbf (local match, label_geocode.pair/single)')
        try:
            A = LG.lines(match(q['a'], q['near'])); r['a_ways'] = len(A)
            if q.get('b'):
                B = LG.lines(match(q['b'], q['near'])); r['b_ways'] = len(B)
                if A and B: r['pair'] = LG.pair(A, B, q['near'])
            if A: r['single'] = LG.single(A, q['near'])
        except Exception as e: r['error'] = repr(e)[:300]
        R[k] = r; n += 1
    json.dump(R, open(OSM_PATH, 'w'), indent=0); log('geocoded', n, 'new;', sum(1 for v in R.values() if v.get('pair') or v.get('single')), 'placed of', len(R))


def osm_roads(pbf, cases, out_dir):
    """Road graphs (docs/graph_segments.json layout) for every run box from one extract -> <out_dir>/<name>.json.gz + roads_info.json."""
    import gzip
    W = [w for w in osm_ways(pbf) if w['tags'].get('highway') in OSM_CLASSES]; towns = town_polys(); os.makedirs(out_dir, exist_ok=True); info = {}
    from pyproj import Transformer
    TI = Transformer.from_crs(26986, 4326, always_xy=True)
    for c in cases:
        x0, y0, x1, y1 = [float(v) for v in c['box'].split(',')]
        lo0, la0 = TI.transform(x0 - 1500, y0 - 1500); lo1, la1 = TI.transform(x1 + 1500, y1 + 1500)
        els = []; seen = set()
        for w in W:
            a = w['ll']
            if a[:, 0].max() < lo0 or a[:, 0].min() > lo1 or a[:, 1].max() < la0 or a[:, 1].min() > la1: continue
            els.append(dict(type='way', id=w['id'], nodes=w['nodes'], tags=w['tags']))
            for nid, (lo, la) in zip(w['nodes'], a):
                if nid not in seen: seen.add(nid); els.append(dict(type='node', id=nid, lon=float(lo), lat=float(la)))
        S = build_segments(els, towns); S['source'] = S['source'].replace('via Overpass', 'Geofabrik massachusetts-latest.osm.pbf ' + time.strftime('%Y-%m-%d'))
        with io.TextIOWrapper(gzip.GzipFile(os.path.join(out_dir, f"{c['name']}.json.gz"), 'wb', mtime=0)) as f: json.dump(S, f, separators=(',', ':'))
        cls = np.asarray(S['props']['cls'])
        info[c['name']] = dict(segments=S['n'], by_class={k: int((cls == k).sum()) for k in (0, 1, 2)}, links=len(S['links']), box=c['box'],
                               towns=sorted({t for t in S['props']['town'] if t}))
        log('roads', c['name'], info[c['name']]['segments'], info[c['name']]['by_class'])
    json.dump(info, open(os.path.join(out_dir, 'roads_info.json'), 'w'), indent=0)


def gauges_fast(out_dir):
    """USGS gauges in each catalogue box -> <out_dir>/gauges_<id>.json in the obs_fetch.py layout (local times).  Through
    proto/usgs_api.py: OGC API bbox query (time-series-metadata discovery, no whole-state pull), legacy WaterServices bBox as the
    fallback until it is switched off 22 Feb 2027 (env USGS_SOURCE=legacy forces the old path)."""
    sys.path.insert(0, HERE); import obs_fetch as OF
    os.makedirs(out_dir, exist_ok=True)
    for e in json.load(open(os.path.join(ROOT, 'docs', 'proto', 'obs', 'catalog_d456.json')))['events']:
        p = os.path.join(out_dir, f"gauges_{e['id']}.json")
        if os.path.exists(p): continue
        try:
            G, used = OF.gauges(e['bbox_lonlat'], e['start'], e['end'])
            src = 'legacy waterservices.usgs.gov IV (bBox)' if used == 'legacy' else 'api.waterdata.usgs.gov OGC continuous (bbox)'
            json.dump(dict(bbox=e['bbox_lonlat'], start=e['start'], end=e['end'], source=src, gauges=list(G.values())), open(p, 'w'))
            log('gauges', e['id'], len(G), [(g['site'], g.get('peak_stage_ft')) for g in G.values()])
        except Exception as ex: log('gauges failed', e['id'], repr(ex)[:200])


def cases_all():
    C = json.load(open(os.path.join(ROOT, 'docs', 'proto', 'obs', 'catalog_d456.json')))['events']
    D3 = {e['id']: e for e in json.load(open(os.path.join(ROOT, 'docs', 'proto', 'obs', 'catalog.json')))['events']}
    out = [dict(id=e['id'], name=f"{e['id']}_{e['area']}_20m", box=','.join(str(int(v)) for v in e['box_26986'])) for e in C]
    for sid in ('sep2021', 'aug2023'):
        e = D3[sid]; out.append(dict(id=sid, name=f"{sid}_{e['area']}_20m", box=','.join(str(int(v)) for v in e['box_26986'])))
    return out


def load_graph(path):
    import gzip
    return json.load(gzip.open(path, 'rt') if path.endswith('.gz') else open(path))


# ------------------------------------------------------------------------------------------------------------------ extract
def extract(run_dir, storm, segments, dest, labels=None):
    """closure_ml.extract with a given road network: features_<storm>.csv + matches_<storm>.json (strict 30 m) in dest, plus the watch tier
    (PROTO_TIERS=1: p_close_ml from docs/proto/ml/closure_lr_all.json; p_close unchanged) as extra columns."""
    import glob, tempfile
    sys.path.insert(0, HERE); import closure_ml as CM
    sys.modules.setdefault('closure_ml', CM); import prototype as PT
    labels = labels if labels is not None else sorted(glob.glob(os.path.join(HERE, 'data', f'labels_{storm}_*.csv')))
    seg_json = segments
    if segments.endswith('.gz'):
        seg_json = os.path.join(tempfile.mkdtemp(prefix='seg_'), 'segments.json'); json.dump(load_graph(segments), open(seg_json, 'w'))
    CM.CAPTURE = {}; os.environ['PROTO_ML'] = '1'; os.environ['PROTO_TIERS'] = '1'
    try:
        PT.run(run_dir, tempfile.mkdtemp(prefix='mlx_'), seg_json, os.path.join(ROOT, 'docs', 'network', 'crossings_all.json'), None, None, None, 30, False,
               labels[0] if labels else None)
    finally:
        os.environ.pop('PROTO_ML', None); os.environ.pop('PROTO_TIERS', None)
    C = CM.CAPTURE; CM.CAPTURE = None; rows = C['rows']
    y = {r['segment']: 0 for r in rows}; src = {r['segment']: '' for r in rows}; matches = {}
    for path in labels:
        L = PT.load_labels(path)
        for lab, segs in PT.label_segments(L, C.get('Qm', C['Q']), C['props'], C['meta'], strict=True):
            segs = [int(s) for s in segs if int(s) in y]
            if not segs: continue
            matches[f"{os.path.basename(path)}:{lab.get('id')}"] = dict(type=lab.get('type'), segs=segs)
            for s in segs: y[s] = 1; src[s] = (src[s] + ' ' + str(lab.get('id'))).strip()
    os.makedirs(dest, exist_ok=True); cols = CM.ROW_KEYS + ['area_km2', 'hand_m', 'stream_dist_m', 'slope_pct', 'cx', 'cy', 'y', 'label_ids', 'p_close_ml', 'tier']
    fn = os.path.join(dest, f'features_{storm}.csv')
    with open(fn, 'w', newline='') as f:
        w = csv.writer(f); w.writerow(cols)
        for r in rows:
            g = r['_geo']
            w.writerow([r.get(k) for k in CM.ROW_KEYS] + [g[k] for k in ('area_km2', 'hand_m', 'stream_dist_m', 'slope_pct', 'cx', 'cy')] +
                       [y[r['segment']], src[r['segment']], r.get('p_close_ml'), r.get('tier', '')])
    json.dump(dict(storm=storm, run_dir=os.path.basename(os.path.normpath(run_dir)), segments_file=os.path.basename(segments),
                   labels=[os.path.relpath(os.path.abspath(p), ROOT) for p in labels], segments=len(rows), positives=int(sum(y.values())),
                   sites_matched=len(matches), matches=matches), open(os.path.join(dest, f'matches_{storm}.json'), 'w'), indent=0)
    print(f'{fn}: {len(rows)} segments, {sum(y.values())} positive, {len(matches)} labels matched, watch tier {sum(1 for r in rows if r.get("tier") == "watch")}')
    return fn


# ------------------------------------------------------------------------------------------------------------------ score
HELD23_ROUND2 = os.path.join(ROOT, 'docs', 'proto', 'obs', 'round2', 'score_round2.json')
PARITY_CAT = os.path.join(ROOT, 'docs', 'proto', 'parity', 'catalog')


def watch_mask(features_csv, seg):
    """Rule + watch tier of the deployed design (prototype.TIER_WATCH_P on closure_lr_all.json), recomputed from a features table the same
    way for District 3 and District 4-6 runs -> bool array over the score_v2 universe seg."""
    sys.path.insert(0, HERE); import closure_ml as CM, prototype as PT
    import gzip
    f = gzip.open(features_csv, 'rt') if features_csv.endswith('.gz') else open(features_csv)
    rows = list(csv.DictReader(f)); pml = CM.LR.load(CM.MODEL_ALL).predict(CM.design(rows))
    pos = {int(s): i for i, s in enumerate(seg)}; m = np.zeros(len(seg), bool)
    for r, q in zip(rows, pml):
        i = pos.get(int(r['segment']))
        if i is not None and (float(r['p_close'] or 0) >= 0.5 or q >= PT.TIER_WATCH_P): m[i] = True
    return m


def score_tier(R, mask):
    """score_v2 metrics with the flagged set = mask (the 'rule' block of the result)."""
    import score_v2 as SV
    R2 = dict(R); R2['p'] = mask.astype(float); R2['pm'] = np.zeros(len(mask)); return SV.score_domain(R2, np.ones(len(mask), bool), None)['rule']


def gauge_stats(score_json):
    try: S = json.load(open(score_json))
    except Exception: return None
    G = [g for g in S.get('gauges', []) if g.get('obs_rise_m') is not None and g.get('model_rise_m') is not None]
    if not G: return None
    e = [g['rise_error_m'] for g in G]; tm = [abs(g['peak_timing_error_interval_h']) for g in G if g.get('peak_timing_error_interval_h') is not None]
    return dict(n=len(G), mean_abs_rise_error_m=float(np.mean(np.abs(e))), bias_m=float(np.mean(e)), zero_model_rise=sum(1 for g in G if g['model_rise_m'] <= 0.0),
                mean_abs_peak_timing_h=float(np.mean(tm)) if tm else None, gauges=[(g['site'], g['obs_rise_m'], g['model_rise_m']) for g in G])


def tier_pool(items):
    """Pooled site recall / chance / lift / share over (rule-block dicts)."""
    H = sum(b.get('site_hits', b.get('hits')) for b in items); C = sum(sum(b['_chance']) for b in items); N = sum(len(b['_hits']) for b in items)
    return dict(sites=N, hits=H, recall=H / N if N else None, chance=C / N if N else None, lift=H / C if C else None,
                mean_share=float(np.mean([b['share'] for b in items])) if items else None)


def score(run):
    import glob
    sys.path.insert(0, HERE); import score_v2 as SV
    RD = os.path.join(TD, run); out = {}
    sp = os.path.join(RD, 'score_d456.json')
    res = json.load(open(sp)) if os.environ.get('TRANSFER_REUSE') == '1' and os.path.exists(sp) else SV.d456(RD, sp, os.path.join(RD, 'score_d456_table.md'))
    per = {}
    for r in res['runs']:
        d = os.path.join(ROOT, r['run']); b = r['domains']['box']
        feat = (glob.glob(os.path.join(d, 'features_*.csv')) + glob.glob(os.path.join(d, 'features_*.csv.gz')))[:1]
        tier = None
        if feat:
            R = SV.load_run(d, r['storm']); tier = score_tier(R, watch_mask(feat[0], R['seg']))
        per[r['storm']] = dict(run=r['run'], sites=b['n_sites'], labels_in_box=r['labels_in_box'], n_segments=b['n_segments'],
                               rule=dict(share=b['rule']['share'], hits=b['rule']['site_hits'], recall=b['rule']['site_recall'], lift=b['rule']['lift'],
                                         fss300=b['rule']['fss'].get('300', {}).get('fss'), fss300_chance=b['rule']['fss'].get('300', {}).get('chance')),
                               share3=dict(hits=b['shares']['0.03']['site_hits'], recall=b['shares']['0.03']['site_recall'], chance=b['shares']['0.03']['chance_recall'],
                                           lift=b['shares']['0.03']['lift'], fss300=b['shares']['0.03']['fss'].get('300', {}).get('fss')),
                               share10=dict(recall=b['shares']['0.1']['site_recall']), fss_useful=b['fss_useful'],
                               tier=None if tier is None else dict(share=tier['share'], hits=tier['site_hits'], recall=tier['site_recall'], lift=tier['lift'],
                                                                   _hits=tier['_hits'], _chance=tier['_chance']),
                               gauges=gauge_stats(os.path.join(d, 'score.json')))
    out['d456'] = dict(per_storm=per, pool=res['pools'].get('transfer:d456'),
                       tier_pool=tier_pool([v['tier'] for v in per.values() if v['tier'] and v['sites']]))
    # District 3 reference: held-out 23 after label round 2 (same parity physics), watch tier and gauges recomputed the same way
    R2 = json.load(open(HELD23_ROUND2)); ref = R2['pools']['parity:heldout23']
    held = set(SV.HELDOUT) | set(SV.NEW16); ti = []; gs = []
    for r in R2['runs']:
        if r.get('group') != 'parity' or not r.get('primary') or r['storm'] not in held: continue
        d = os.path.join(ROOT, r['run']); feat = glob.glob(os.path.join(d, 'features_*.csv'))
        if feat and r['domains']['box']['n_sites']:
            R = SV.load_run(d, r['storm']); ti.append(score_tier(R, watch_mask(feat[0], R['seg'])))
        g = gauge_stats(os.path.join(d, 'score.json'))
        if g: gs.append(g)
    out['d3_heldout23'] = dict(pool=dict(box=ref['box']), tier_pool=tier_pool(ti),
                               gauges=dict(storms=len(gs), gauges=sum(g['n'] for g in gs), mean_per_storm_abs_rise_error_m=float(np.mean([g['mean_abs_rise_error_m'] for g in gs])),
                                           bias_m=float(np.mean([g['bias_m'] for g in gs])), zero_model_rise=sum(g['zero_model_rise'] for g in gs),
                                           mean_per_storm_abs_peak_timing_h=float(np.mean([g['mean_abs_peak_timing_h'] for g in gs if g['mean_abs_peak_timing_h'] is not None]))))
    gd = [v['gauges'] for v in per.values() if v['gauges']]
    if gd:
        out['d456']['gauges'] = dict(storms=len(gd), gauges=sum(g['n'] for g in gd), mean_per_storm_abs_rise_error_m=float(np.mean([g['mean_abs_rise_error_m'] for g in gd])),
                                     bias_m=float(np.mean([g['bias_m'] for g in gd])), zero_model_rise=sum(g['zero_model_rise'] for g in gd),
                                     mean_per_storm_abs_peak_timing_h=float(np.mean([g['mean_abs_peak_timing_h'] for g in gd if g['mean_abs_peak_timing_h'] is not None] or [np.nan])))
    # road-source control: same physics, District 3 graph vs OSM roads
    ctl = {}
    for d in sorted(glob.glob(os.path.join(RD, '*_d3graph'))):
        o = d[:-len('_d3graph')]; s = SV.storm_of(os.path.basename(o)); row = {}
        for tag, p in (('osm', o), ('d3graph', d)):
            try:
                rr = SV.score_run(SV.load_run(p, s)); b = rr['domains']['box']
                row[tag] = dict(n_segments=b['n_segments'], sites=b['n_sites'], rule_share=b['rule']['share'], rule_hits=b['rule']['site_hits'],
                                share3_hits=b['shares']['0.03']['site_hits'], share3_recall=b['shares']['0.03']['site_recall'], lift3=b['shares']['0.03']['lift'],
                                fss300_rule=b['rule']['fss'].get('300', {}).get('fss'))
            except Exception as e: row[tag] = dict(error=repr(e)[:300])
        pr = next((x for x in R2['runs'] if x.get('group') == 'parity' and x.get('primary') and x['storm'] == s), None)
        if pr:
            b = pr['domains']['box']; row['published_parity'] = dict(n_segments=b['n_segments'], sites=b['n_sites'], rule_share=b['rule']['share'],
                                                                    rule_hits=b['rule']['site_hits'], share3_hits=b['shares']['0.03']['site_hits'])
        try:
            hs_new = json.load(open(os.path.join(o, 'hmax_stats.json'))); hs_old = json.load(open(os.path.join(ROOT, pr['run'], 'hmax_stats.json'))) if pr else None
            row['hmax_stats'] = dict(rerun=hs_new, published=hs_old)
        except Exception: pass
        ctl[s] = row
    out['control'] = ctl
    json.dump(out, open(os.path.join(RD, 'transfer_summary.json'), 'w'), indent=1, default=float)
    P = out['d456']['pool']
    if P:
        b = P['box']; print('d456 pooled: sites', b['n_sites'], 'storms', len(b['storms']), 'rule', b['point']['rule'], '3%', b['point']['share_0.03'], b['ci90']['share_0.03'])
    print('tier', out['d456']['tier_pool'], 'd3 tier', out['d3_heldout23']['tier_pool']); print('control', json.dumps(ctl)[:1500])
    return out


def breakdown(run):
    """Descriptive splits of the pooled District 4-6 result (not part of the verdict): by district, by label source (sites whose labels are all
    NWS vs those with a 311 / SeeClickFix label), by era (AWS Pass2 vs IEM GaugeCorr) -> dict of {name: {block: pooled hits/chance/recall/lift}}."""
    R = json.load(open(os.path.join(TD, run, 'score_d456.json'))); C = {e['id']: e for e in json.load(open(os.path.join(ROOT, 'docs', 'proto', 'obs', 'catalog_d456.json')))['events']}
    src = {}
    for e in C.values():
        for r in csv.DictReader(open(os.path.join(ROOT, e['labels']))): src[r['id']] = r['source']
    groups = {}
    for r in R['runs']:
        if not r.get('primary'): continue
        b = r['domains']['box']; e = C[r['storm']]
        for blk, B in (('rule', b['rule']), ('share3', b['shares']['0.03']), ('share10', b['shares']['0.1'])):
            for i, site in enumerate(b['sites']):
                ids = site['id'].split('+'); nws = all(src.get(x) in ('LSR', 'StormEvents') for x in ids)
                for g in (f"district {e['district']}", 'NWS-only sites' if nws else 'sites with a 311 / SeeClickFix label', f"era {e['era']}", 'all'):
                    d = groups.setdefault(g, {}).setdefault(blk, dict(hits=0.0, chance=0.0, sites=0)); d['hits'] += B['_hits'][i]; d['chance'] += B['_chance'][i]; d['sites'] += 1
    for g in groups.values():
        for d in g.values(): d['recall'] = d['hits'] / d['sites'] if d['sites'] else None; d['lift'] = d['hits'] / d['chance'] if d['chance'] else None
    return groups


def tables(run):
    """Markdown tables for TRANSFER.md from docs/proto/transfer/<run>/transfer_summary.json (the prose is written by hand)."""
    S = json.load(open(os.path.join(TD, run, 'transfer_summary.json'))); C = {e['id']: e for e in json.load(open(os.path.join(ROOT, 'docs', 'proto', 'obs', 'catalog_d456.json')))['events']}
    f = lambda v, n=2: '–' if v is None else f'{v:.{n}f}'
    L = ['| storm | district | sites | rule: share / hits / lift | 3 %: hits / recall (chance) / lift | FSS300 rule (chance) | rule + watch: share / hits | gauges: n / mean abs rise err (m) / bias / timing (h) |',
         '|' + '---|' * 8]
    for sid, v in S['d456']['per_storm'].items():
        g = v['gauges'] or {}; t = v['tier'] or {}
        L.append(f"| {sid} | {C.get(sid, {}).get('district', '')} | {v['sites']} | {f(v['rule']['share'] * 100, 2)} % / {f(v['rule']['hits'], 0)} / {f(v['rule']['lift'], 1)} | "
                 f"{f(v['share3']['hits'], 1)} / {f(v['share3']['recall'])} ({f(v['share3']['chance'])}) / {f(v['share3']['lift'], 1)} | {f(v['rule']['fss300'], 3)} ({f(v['rule']['fss300_chance'], 3)}) | "
                 f"{f((t.get('share') or 0) * 100, 1)} % / {f(t.get('hits'), 0)} | {g.get('n', 0)} / {f(g.get('mean_abs_rise_error_m'))} / {f(g.get('bias_m'))} / {f(g.get('mean_abs_peak_timing_h'), 1)} |")
    return '\n'.join(L)


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('cmd', choices=['discover', 'queries', 'build', 'roads', 'extract', 'score', 'osm-geocode', 'osm-roads', 'gauges-fast'])
    ap.add_argument('--pbf')
    ap.add_argument('--box'); ap.add_argument('--out'); ap.add_argument('--run-dir'); ap.add_argument('--storm'); ap.add_argument('--segments')
    ap.add_argument('--dest'); ap.add_argument('--run', default='r1'); ap.add_argument('--parts', default='districts,boston311,seeclickfix')
    a = ap.parse_args()
    if a.cmd == 'discover': discover(tuple(a.parts.split(',')))
    elif a.cmd == 'queries': queries()
    elif a.cmd == 'build': build(); report()
    elif a.cmd == 'roads': roads(tuple(float(v) for v in a.box.split(',')), a.out)
    elif a.cmd == 'osm-geocode': osm_geocode(a.pbf)
    elif a.cmd == 'osm-roads': osm_roads(a.pbf, cases_all(), a.out or os.path.join(TD, 'roads_osm'))
    elif a.cmd == 'gauges-fast': gauges_fast(a.out or os.path.join(TD, 'gauges'))
    elif a.cmd == 'extract': extract(a.run_dir, a.storm, a.segments, a.dest)
    elif a.cmd == 'score': score(a.run); print(tables(a.run)); print(json.dumps(breakdown(a.run), indent=0))
