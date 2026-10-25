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
TOWN_ZIPS = ['https://s3.us-east-1.amazonaws.com/download.massgis.digital.mass.gov/shapefiles/state/townssurvey_shp.zip',
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
            T = read_shp_zip(rt.content); lay = max(T.values(), key=lambda v: len(v['rows'])); log('towns layer', lay['fields'], len(lay['rows']))
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
    """Boston 311 requests whose type / title mentions flooding: (1) daily counts per resource (all years), (2) every such request inside
    each candidate window.  -> raw/boston311_days.json, raw/boston311_<day>.json"""
    RES = boston_resources(); days = {}; meta = {}
    for res in RES:
        F = boston_fields(res['id'])
        if not F: continue
        fl = {f.lower(): f for f in F}
        t_ = fl.get('type') or fl.get('case_type') or fl.get('service_name') or fl.get('request_type')
        c_ = fl.get('case_title') or fl.get('title') or fl.get('description') or fl.get('subject')
        o_ = fl.get('open_dt') or fl.get('open_date') or fl.get('opened') or fl.get('requested_datetime') or fl.get('created_at')
        meta[res['id']] = dict(res, fields=F, type=t_, title=c_, open=o_)
        if not (t_ and o_): log('  311 resource lacks type/open fields', res['name'], F[:30]); continue
        w = BOS_FLOOD.format(t=t_, c=c_ or t_)
        rec = boston_sql(f'select substring("{o_}"::text from 1 for 10) as d, "{t_}" as t, count(*) as n from "{res["id"]}" where {w} group by 1, 2')
        if rec is None: continue
        for x in rec:
            days.setdefault(x['d'], {}); days[x['d']][x['t']] = days[x['d']].get(x['t'], 0) + int(x['n'])
        log('  311', res['name'], 'flood rows', sum(int(x['n']) for x in rec))
    json.dump(dict(resources=list(meta.values()), days=days), open(os.path.join(RAW, 'boston311_days.json'), 'w'), indent=0)
    for W in windows:
        a, b = W['a'], W['b']; got = []
        for rid, m in meta.items():
            if not (m['type'] and m['open']): continue
            w = BOS_FLOOD.format(t=m['type'], c=m['title'] or m['type'])
            rec = boston_sql(f'select * from "{rid}" where {w} and "{m["open"]}"::text >= \'{a}\' and "{m["open"]}"::text < \'{b}\' limit 5000')
            for x in rec or []: x['_resource'] = m['name']; got.append(x)
        json.dump(dict(window_local=[a, b], n=len(got), rows=got), open(os.path.join(RAW, f'boston311_{W["day"]}.json'), 'w'), indent=0, default=str)
        log('  311 window', W['day'], len(got))
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


def discover():
    os.makedirs(RAW, exist_ok=True)
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
        try: fn(ww)
        except BaseException as e: log(name, 'FAILED', repr(e)[:300])
    json.dump(dict(log=LOG[-600:], made=time.strftime('%Y-%m-%d %H:%M')), open(os.path.join(RAW, 'discover_log.json'), 'w'), indent=0)


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('cmd', choices=['discover', 'queries', 'build', 'roads', 'extract', 'score'])
    a, rest = ap.parse_known_args()
    if a.cmd == 'discover': discover()
