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


def pick_town_layer(T):
    P = [v for v in T.values() if v['rows'] and v['rows'][0][2] in (5, 15, 25) and any(f in v['fields'] for f in ('TOWN', 'TOWN_NAME', 'NAME'))]
    return max(P or list(T.values()), key=lambda v: len(v['rows']))


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
            nk = next((f for f in ('TOWN', 'TOWN_NAME', 'NAME', 'COMMUNITY') if f in lay['fields']), None)
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
                if xl in LR2.STOP or xl in LR2.SUF or xl in CONNECT - DIRS or not re.match(r"[A-Z0-9]", x) or x.endswith('.') and j != k - 1: break
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
    if BASEMENT_RE.search(text) and not re.search(r'road|street|\bst\b|\brd\b|route|\bave|impassable|closed', text, re.I): return [], 'basement / main'
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
    c = re.sub(r'^\d+\s+[NSEW]{1,3}\s+', '', r['city'] or '').title()
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
            nk = next((f for f in ('TOWN', 'TOWN_NAME', 'NAME', 'COMMUNITY') if f in lay['fields']), None)
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
    H = sum(b['site_hits'] for b in items); C = sum(sum(b['_chance']) for b in items); N = sum(len(b['_hits']) for b in items)
    return dict(sites=N, hits=H, recall=H / N if N else None, chance=C / N if N else None, lift=H / C if C else None,
                mean_share=float(np.mean([b['share'] for b in items])) if items else None)


def score(run):
    import glob
    sys.path.insert(0, HERE); import score_v2 as SV
    RD = os.path.join(TD, run); out = {}
    res = SV.d456(RD, os.path.join(RD, 'score_d456.json'), os.path.join(RD, 'score_d456_table.md'))
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


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('cmd', choices=['discover', 'queries', 'build', 'roads', 'extract', 'score'])
    ap.add_argument('--box'); ap.add_argument('--out'); ap.add_argument('--run-dir'); ap.add_argument('--storm'); ap.add_argument('--segments')
    ap.add_argument('--dest'); ap.add_argument('--run', default='r1'); ap.add_argument('--parts', default='districts,boston311,seeclickfix')
    a = ap.parse_args()
    if a.cmd == 'discover': discover(tuple(a.parts.split(',')))
    elif a.cmd == 'queries': queries()
    elif a.cmd == 'roads': roads(tuple(float(v) for v in a.box.split(',')), a.out)
    elif a.cmd == 'extract': extract(a.run_dir, a.storm, a.segments, a.dest)
    elif a.cmd == 'score': score(a.run)
