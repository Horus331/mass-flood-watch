"""Who owns each road, its route number, speed limit and mile points, from the MassDOT Road Inventory (ArcGIS REST), joined to the
model's District 3 road segments (docs/graph_segments.json) -> docs/site/data/road_attrs.json.

The model's segments came from the same inventory but kept only name, town, class, length and AADT.  This adds what a MassDOT or town
engineer filters by: jurisdiction (MassDOT, city/town, DCR, ...), route number, posted speed, functional class and the route mile points.
Join: each segment's midpoint to the nearest inventory line within 25 m, preferring the same street name.  Runs on GitHub Actions
(.github/workflows/road_attrs.yml): the MassDOT server is not reachable from every machine.

Output (compact, one row per segment id): fields own, rt, spd, fc, mi0, mi1; dictionaries for the codes.
"""
import json, math, os, re, sys, time, urllib.parse, urllib.request
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'sim', 'infra'))
OUT = os.path.join(ROOT, 'docs', 'site', 'data', 'road_attrs.json')
BBOX = (-72.45, 41.93, -71.38, 42.80)
CANDIDATES = [   # MassDOT and MassGIS hosts of the Road Inventory; the first that answers with a jurisdiction field is used
    'https://gis.massdot.state.ma.us/arcgis/rest/services/Roads/RoadInventory/MapServer',
    'https://gis.massdot.state.ma.us/arcgis/rest/services/Roads/RoadInventory2023/MapServer',
    'https://gis.massdot.state.ma.us/arcgis/rest/services/Roads',
    'https://gisstg.massdot.state.ma.us/arcgis/rest/services/Roads',
    'https://arcgisserver.digital.mass.gov/arcgisserver/rest/services/AGOL/MassDOT_Roads/MapServer',
]
JUR = {'1': 'MassDOT', '2': 'City or town', '3': 'DCR', '4': 'State institution', '5': 'State park or forest', '6': 'US government',
       '7': 'College or university', '8': 'Private', '9': 'MassPort', '0': 'Unaccepted by city or town', 'B': 'Mass Turnpike Authority',
       'H': 'MassDOT (Turnpike)', 'I': 'Department of Conservation', 'D': 'Private, open to public', 'M': 'MassDOT (former MDC)'}


def get(url, params=None, tries=4):
    if params: url += ('&' if '?' in url else '?') + urllib.parse.urlencode(params)
    for k in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': 'mass-flood-watch research (road attributes)'}), timeout=90) as r:
                return json.load(r)
        except Exception as e:
            if k == tries - 1: raise
            time.sleep(4 + 6 * k)


def find_layer():
    """(layer url, field map) of the first Road Inventory layer that has a jurisdiction field."""
    for base in CANDIDATES:
        try: J = get(base, {'f': 'json'})
        except Exception as e: print('  no', base, repr(e)[:100]); continue
        urls = []
        if 'layers' in J: urls = [f"{base}/{L['id']}" for L in J['layers']]
        for s in J.get('services') or []:
            if 'inventory' in s['name'].lower() or 'road' in s['name'].lower():
                root = base.split('/rest/services')[0] + '/rest/services/' + s['name'] + '/' + s['type']
                try: urls += [f"{root}/{L['id']}" for L in get(root, {'f': 'json'}).get('layers', [])]
                except Exception: pass
        for u in urls:
            try: L = get(u, {'f': 'json'})
            except Exception: continue
            names = {f['name'].lower(): f['name'] for f in L.get('fields') or []}
            jf = next((names[k] for k in names if k.startswith('jurisd')), None)
            if not jf or L.get('geometryType') != 'esriGeometryPolyline': continue
            pick = lambda *ks: next((names[k] for k in ks if k in names), None)
            F = dict(jur=jf, rt=pick('rt_number', 'route_number', 'route_numb', 'rtnumber'), spd=pick('speed_lim', 'speed_limit', 'speedlim'),
                     fc=pick('f_class', 'f_f_class', 'functional_class', 'func_class'), name=pick('st_name', 'street_name', 'streetname', 'full_name'),
                     mi0=pick('from_measure', 'frommeasure', 'from_meas'), mi1=pick('to_measure', 'tomeasure', 'to_meas'), rid=pick('route_id', 'routeid'))
            print('layer', u, L.get('name'), F, flush=True)
            return u, F, L.get('maxRecordCount') or 1000
    raise SystemExit('no Road Inventory layer with a jurisdiction field found in ' + ', '.join(CANDIDATES))


def fetch(u, F, page):
    flds = ','.join(v for v in F.values() if v)
    # tile the box so each query stays under the server's record cap
    rows, nx, ny = [], 12, 10
    for i in range(nx):
        for j in range(ny):
            x0 = BBOX[0] + (BBOX[2] - BBOX[0]) * i / nx; x1 = BBOX[0] + (BBOX[2] - BBOX[0]) * (i + 1) / nx
            y0 = BBOX[1] + (BBOX[3] - BBOX[1]) * j / ny; y1 = BBOX[1] + (BBOX[3] - BBOX[1]) * (j + 1) / ny
            off = 0
            while True:
                q = dict(f='json', where='1=1', outFields=flds, returnGeometry='true', outSR='4326', geometry=f'{x0},{y0},{x1},{y1}',
                         geometryType='esriGeometryEnvelope', inSR='4326', spatialRel='esriSpatialRelIntersects', resultOffset=off,
                         resultRecordCount=page, geometryPrecision=6)
                J = get(u + '/query', q)
                if 'error' in J: raise SystemExit(f"query error: {J['error']}")
                fs = J.get('features') or []
                for f in fs:
                    pa = (f.get('geometry') or {}).get('paths') or []
                    if pa: rows.append((f['attributes'], pa))
                if not J.get('exceededTransferLimit') and len(fs) < page: break
                off += len(fs)
            print(f'  tile {i},{j}: {len(rows)} lines so far', flush=True) if j == ny - 1 else None
    return rows


def main():
    import impacts as IM
    from shapely.geometry import LineString, Point
    from shapely.strtree import STRtree
    from pyproj import Transformer
    S = json.load(open(os.path.join(ROOT, 'docs', 'graph_segments.json'))); P = S['props']; n = S['n']
    u, F, page = find_layer(); page = min(page, 2000)
    R = fetch(u, F, page); print(len(R), 'inventory lines', flush=True)
    tr = Transformer.from_crs(4326, 26986, always_xy=True)
    lines, attrs = [], []
    for a, pa in R:
        for path in pa:
            if len(path) < 2: continue
            x, y = tr.transform([p[0] for p in path], [p[1] for p in path]); lines.append(LineString(list(zip(x, y)))); attrs.append(a)
    tree = STRtree(lines)
    norm = lambda s: re.sub(r'[^a-z0-9]', '', re.sub(r'\b(street|st|road|rd|avenue|ave|drive|dr|route|rte|rt|highway|hwy)\b', '', str(s or '').lower()))
    own = [''] * n; rt = [''] * n; spd = [0] * n; fc = [0] * n; mi0 = [None] * n; mi1 = [None] * n; hit = 0
    mids = {}
    for seg, lo, la in IM.decode_segments(S):
        if seg in mids or len(lo) < 1: continue
        k = len(lo) // 2; mids[seg] = tr.transform(float(lo[k]), float(la[k]))
    for seg, (x, y) in mids.items():
        pt = Point(x, y); idx = tree.query(pt.buffer(25))
        if not len(idx): continue
        nm = norm(P['road'][seg]); best = None
        for k in idx:
            d = lines[k].distance(pt)
            if d > 25: continue
            sc = d - (15 if nm and F['name'] and norm(attrs[k].get(F['name'])) == nm else 0)
            if best is None or sc < best[0]: best = (sc, k)
        if best is None: continue
        a = attrs[best[1]]; hit += 1
        own[seg] = str(a.get(F['jur']) if a.get(F['jur']) is not None else '').strip()
        if F['rt']: rt[seg] = str(a.get(F['rt']) or '').strip()
        if F['spd']:
            try: spd[seg] = int(float(a.get(F['spd']) or 0))
            except (TypeError, ValueError): spd[seg] = 0
        if F['fc']:
            try: fc[seg] = int(float(a.get(F['fc']) or 0))
            except (TypeError, ValueError): fc[seg] = 0
        if F['mi0'] and a.get(F['mi0']) is not None: mi0[seg] = round(float(a[F['mi0']]), 2)
        if F['mi1'] and a.get(F['mi1']) is not None: mi1[seg] = round(float(a[F['mi1']]), 2)
    codes = sorted({c for c in own if c}); ci = {c: i + 1 for i, c in enumerate(codes)}
    out = dict(made_by='tools/road_attrs.py', made=time.strftime('%Y-%m-%dT%H:%MZ', time.gmtime()), source=u, fields_used=F,
               note='MassDOT Road Inventory attributes joined to docs/graph_segments.json by segment midpoint (25 m, same street name preferred)',
               n=n, matched=hit, own_codes=[''] + codes, own_names=[''] + [JUR.get(c, c) for c in codes],
               own=[ci.get(c, 0) for c in own], rt=rt, spd=spd, fc=fc, mi0=mi0, mi1=mi1)
    json.dump(out, open(OUT, 'w'), separators=(',', ':'))
    from collections import Counter
    print('matched', hit, 'of', n, 'segments;', Counter(JUR.get(c, c) for c in own if c).most_common(8), os.path.getsize(OUT) // 1024, 'KB')


if __name__ == '__main__':
    main()
