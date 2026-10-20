"""Every road-stream crossing in Massachusetts, with what culvert hydraulics needs, merged from four public ArcGIS services.

    python sim/infra/crossings_all.py                 # GitHub Actions / Colab (internet); writes docs/network/crossings_all.json
    python sim/infra/crossings_all.py --selftest      # offline: the merge on synthetic service pages

Sources (all public, no key; confirmed 19 Oct 2026 via their REST pages, field lists in docs/research/infra.md):
  U  USGS Database of Stream Crossings in the United States (Wieferich 2022, doi:10.5066/P9YX6KTB): TIGER 2020 roads x NHDPlus HR
     flowlines, 6.6 M modelled crossings nationwide (layer 0) + 2019 NBI observations linked to them (layer 1).  The statewide universe:
     every modelled road-stream crossing, with road/stream names, TIGER road class (MTFCC) and bridge/culvert type where NBI knows it.
  N  NAACC field assessments ('NAACC Culvert Assessment', 14 NE/Mid-Atlantic states): surveyed crossings with structure shape, material,
     inlet type (projecting / headwall / wingwalls / mitered), inlet width and height (ft), number of culverts, road-fill height (ft).
     About 22 % of MA culverts are surveyed (MassDEP).  The layer's field names are truncated shapefile names; the shape / material /
     inlet columns are found by their values at run time (see pick_fields) and the choice is printed and stored in the output.
  P  MA Stream Crossings Project (USGS / UMass / MassDEP, doi:10.5066/P9BL9CW4, layer 0): StreamStats drainage area and 10-500-yr peaks,
     bankfull width/depth, lidar road-deck elevation and channel inverts (ft NAVD88) - only the crossings modelled so far (365 in Oct 2026).
  B  MassDOT bridges & culverts (Bridge Inspection Management System; NBI bridges, short spans 10-20 ft and culverts 4-10 ft, culvert
     inventory incomplete): structure category, material, culvert condition.  Optional (staging host); skipped if unreachable.
Merge: U is the backbone; N, P and B attach to the nearest U crossing within 50 m (P first by NAACC code through N); unmatched N and P
records are added as their own rows.  Points outside Massachusetts (TIGERweb county polygons, STATE = 25) are dropped; each row
carries its county and d3 = 1 inside the District 3 box (EPSG:26986 128000, 856000, 206000, 946000).
Output docs/network/crossings_all.json: {columns, rows, sources, field_map, counts}; SI units (m, km2, m3/s); None = unknown.
"""
import os, sys, json, time, math
import numpy as np

H = {'User-Agent': 'mass-flood-watch research (github.com/Horus331/mass-flood-watch)'}
MA_BBOX = (-73.51, 41.23, -69.92, 42.89)
D3_BOX = (128000, 856000, 206000, 946000)
SRC_U = 'https://services.arcgis.com/v01gqwM5QqNysAAi/ArcGIS/rest/services/stream_crossings/FeatureServer'
SRC_N = 'https://services.arcgis.com/cJ9YHowT8TU7DUyn/ArcGIS/rest/services/NAACC_Culvert_Assessment_2/FeatureServer/0'
SRC_P = 'https://services.arcgis.com/v01gqwM5QqNysAAi/ArcGIS/rest/services/Massachusetts_Stream_Crossings_Project_Web_Map_Service/FeatureServer/0'
SRC_B = ['https://gis.massdot.state.ma.us/arcgis/rest/services/Roads/Bridges/MapServer/0', 'https://gisstg.massdot.state.ma.us/arcgis/rest/services/Roads/Bridges/MapServer/0']
TIGERWEB = 'https://tigerweb.geo.census.gov/arcgis/rest/services/TIGERweb/State_County/MapServer'
FT, SQMI, CFS = 0.3048, 2.58999, 0.0283168
COLUMNS = ['lon', 'lat', 'id', 'src', 'road', 'stream', 'county', 'mtfcc', 'xtype', 'naacc', 'n_barrels', 'shape', 'material', 'inlet',
           'span_m', 'rise_m', 'fill_m', 'drn_km2', 'pk10', 'pk25', 'pk50', 'pk100', 'pk500', 'bf_w', 'bf_d', 'deck_m', 'usie_m', 'dsie_m',
           'nbi_id', 'mdot_cat', 'mdot_mat', 'mdot_cond', 'naacc_eval', 'd3']

# ---------------- canonical vocabularies (NAACC / MA protocol words -> culvert.py words) ----------------
def norm_shape(v):
    s = (v or '').lower()
    if not s: return None
    if 'ford' in s: return 'ford'
    if 'open bottom' in s or 'open-bottom' in s or 'bottomless' in s: return 'arch_open'
    if 'bridge' in s: return 'bridge'
    if 'pipe arch' in s or 'pipe-arch' in s: return 'pipe_arch'
    if 'ellip' in s: return 'elliptical'
    if 'box' in s: return 'box'
    if 'arch' in s: return 'arch_closed'
    if 'round' in s or 'circ' in s or 'pipe' in s: return 'circular'
    return 'other'

def norm_material(v):
    s = (v or '').lower()
    if not s: return None
    if 'concrete' in s or 'cement' in s: return 'concrete'
    if 'metal' in s or 'steel' in s or 'iron' in s or 'alum' in s or 'cmp' in s or 'corrugated' in s: return 'metal'
    if 'plastic' in s or 'hdpe' in s or 'pvc' in s or 'poly' in s or 'fiberglass' in s: return 'plastic'
    if 'stone' in s or 'rock' in s or 'masonry' in s or 'granite' in s: return 'stone'
    if 'wood' in s or 'timber' in s: return 'wood'
    return 'other'

def norm_inlet(v):
    s = (v or '').lower()
    if not s: return None
    if 'miter' in s: return 'mitered'
    if 'headwall' in s and 'wing' in s: return 'headwall_wingwall'
    if 'wing' in s: return 'wingwall'
    if 'headwall' in s: return 'headwall'
    if 'project' in s: return 'projecting'
    if s.strip() in ('none', 'no'): return 'none'
    return 'other'

def num(v, k=1.0):
    try:
        x = float(str(v).replace('EST.', '').replace('est', '').strip())
        return None if x <= -999 or not math.isfinite(x) else round(x * k, 3)
    except Exception: return None

def pick_fields(fields, sample):
    """Find NAACC columns by name and, for the truncated/ambiguous ones, by their values in a sample of records.
    fields: [{name, type}], sample: [attributes dict].  Returns {role: field name or None}."""
    names = [f['name'] for f in fields]; strf = [f['name'] for f in fields if f.get('type') == 'esriFieldTypeString']
    def score(fn, words):
        vals = [str(a.get(fn) or '').lower() for a in sample]; return sum(any(w in v for w in words) for v in vals)
    def best(words, among=strf, exclude=()):
        sc = [(score(f, words), f) for f in among if f not in exclude]; sc = [x for x in sc if x[0] > 0]
        return max(sc)[1] if sc else None
    m = {}
    m['shape'] = best(['round culvert', 'box culvert', 'elliptical', 'open bottom arch', 'pipe arch', 'bridge with'])
    m['inlet'] = best(['projecting', 'headwall', 'wingwall', 'mitered'], exclude=(m['shape'],))
    m['material'] = best(['concrete', 'metal', 'plastic', 'stone', 'wood'], exclude=(m['shape'], m['inlet']))
    m['xtype'] = best(['culvert', 'bridge', 'ford', 'multiple', 'single'], exclude=(m['shape'], m['inlet'], m['material'])) if 'Crossing_T' not in names else 'Crossing_T'
    look = lambda *c: next((n for n in c if n in names), None)
    m.update(code=look('Crossing_C', 'Crossing_Code', 'CrossingCode'), width=look('Inlet_Widt', 'Inlet_Width'), height=look('Inlet_Heig', 'Inlet_Height'),
             n_barrels=look('Number_Of_', 'Number_Of_Culverts'), fill=look('Road_Fill_', 'Road_Fill_Height'), road=look('Road'), stream=look('Stream_Nam', 'Stream_Name'),
             town=look('Town'), state=look('State'), lat=look('GIS_Latitu', 'GIS_Latitude', 'Latitude'), lon=look('GIS_Longit', 'GIS_Longitude', 'Longitude'),
             evaluation=look('Evaluation'), date=look('Date_Obser', 'Date_Observed'))
    return m

# ---------------- ArcGIS REST paging ----------------
def _get(url, params, tries=4):
    import requests
    for k in range(tries):
        try:
            r = requests.get(url, params=params, headers=H, timeout=180); r.raise_for_status(); j = r.json()
            if 'error' in j: raise RuntimeError(str(j['error'])[:300])
            return j
        except Exception as e:
            if k == tries - 1: raise
            time.sleep(3 * (k + 1))

def query_all(layer_url, where='1=1', fields='*', bbox=None, page=2000, fetch=None, geometry=False, max_rows=None):
    """All features of a layer (attributes [+ geometry]), paging with resultOffset; bbox (lon/lat) as an envelope filter."""
    fetch = fetch or _get; p = dict(where=where, outFields=fields, returnGeometry='true' if geometry else 'false', outSR=4326, f='json', orderByFields='OBJECTID')
    if bbox: p.update(geometry=','.join(map(str, bbox)), geometryType='esriGeometryEnvelope', inSR=4326, spatialRel='esriSpatialRelIntersects')
    out, off = [], 0
    while True:
        j = fetch(layer_url + '/query', dict(p, resultOffset=off, resultRecordCount=page))
        fs = j.get('features', []); out += fs; off += len(fs)
        if off and off % 20000 < page: print(f'  {layer_url.split("/services/")[-1][:60]}: {off}', flush=True)
        if not fs or not j.get('exceededTransferLimit', len(fs) >= page) or (max_rows and off >= max_rows): break
        time.sleep(0.3)
    return out

def layer_info(layer_url, fetch=None):
    return (fetch or _get)(layer_url, dict(f='json'))

def xy(feat, a, latk=None, lonk=None):
    g = feat.get('geometry') or {}
    if 'x' in g and 'y' in g and g['x'] is not None: return float(g['x']), float(g['y'])
    if latk and lonk and a.get(latk) is not None and a.get(lonk) is not None: return float(a[lonk]), float(a[latk])
    return None

# ---------------- Massachusetts polygon test ----------------
def ma_counties(fetch=None):
    """[(name, [ring arrays lon/lat])] for MA counties from TIGERweb; None if unreachable."""
    fetch = fetch or _get
    try:
        info = fetch(TIGERWEB, dict(f='json')); lid = next(l['id'] for l in info['layers'] if l['name'].lower().strip() == 'counties')
        j = fetch(f'{TIGERWEB}/{lid}/query', dict(where="STATE='25'", outFields='NAME', returnGeometry='true', outSR=4326, maxAllowableOffset=0.0005, f='json'))
        return [(f['attributes']['NAME'], [np.asarray(r, float) for r in f['geometry']['rings']]) for f in j['features']]
    except Exception as e:
        print('TIGERweb counties unavailable (rows keep the bbox filter, county None):', repr(e)[:160]); return None

def county_of(lon, lat, counties):
    """County name per point (even-odd over each county's rings), None outside MA."""
    from matplotlib.path import Path
    out = np.full(len(lon), None, object); P = np.column_stack([lon, lat])
    for name, rings in counties:
        allr = np.vstack(rings); bb = (allr[:, 0].min(), allr[:, 1].min(), allr[:, 0].max(), allr[:, 1].max())
        cand = np.nonzero((lon >= bb[0]) & (lon <= bb[2]) & (lat >= bb[1]) & (lat <= bb[3]) & (out == None))[0]   # noqa: E711
        if not len(cand): continue
        inside = np.zeros(len(cand), bool)
        for r in rings: inside ^= Path(r).contains_points(P[cand])
        out[cand[inside]] = name
    return out

# ---------------- merge ----------------
def build(fetch=None, counties='auto', max_rows=None):
    from pyproj import Transformer
    from scipy.spatial import cKDTree
    tr = Transformer.from_crs(4326, 26986, always_xy=True); fetch = fetch or _get
    sources, field_map, counts = {}, {}, {}
    # U: modelled crossings + NBI observations
    U = query_all(SRC_U + '/0', fields='stream_crossing_id,nhdhr_gnis_stream_name,tiger2020_feature_names,tiger2020_mtfcc_feature_class,crossing_type', bbox=MA_BBOX, fetch=fetch, geometry=True, max_rows=max_rows)
    sources['U'] = dict(url=SRC_U, n=len(U)); print('U modelled crossings in MA bbox:', len(U))
    try:
        O = query_all(SRC_U + '/1', fields='stream_crossing_id,structure_id,crossing_type,crossing_subtype', bbox=MA_BBOX, fetch=fetch, max_rows=max_rows)
    except Exception as e:                                                # observations may be a table without geometry: ask by crossing id
        print('U observations by bbox failed, by id:', repr(e)[:120]); O = []
        ids = [f['attributes']['stream_crossing_id'] for f in U if f['attributes'].get('stream_crossing_id') is not None]
        try:
            for k in range(0, len(ids), 400):
                O += query_all(SRC_U + '/1', where='stream_crossing_id IN (%s)' % ','.join(map(str, ids[k:k + 400])), fields='stream_crossing_id,structure_id,crossing_type,crossing_subtype', fetch=fetch)
        except Exception as e2: print('U observations unavailable:', repr(e2)[:120])
    obs = {}
    for f in O:
        a = f['attributes']; obs.setdefault(a.get('stream_crossing_id'), a)
    rows = []
    for f in U:
        a = f['attributes']; p = xy(f, a)
        if p is None: continue
        o = obs.get(a.get('stream_crossing_id'), {}); xt = (o.get('crossing_subtype') or o.get('crossing_type') or a.get('crossing_type') or '').lower() or None
        r = dict.fromkeys(COLUMNS); r.update(lon=round(p[0], 6), lat=round(p[1], 6), id=f"u{a.get('stream_crossing_id')}", src='U', road=a.get('tiger2020_feature_names'),
                                           stream=a.get('nhdhr_gnis_stream_name'), mtfcc=a.get('tiger2020_mtfcc_feature_class'), xtype=xt, nbi_id=o.get('structure_id'))
        if xt and 'bridge' in xt: r['shape'] = 'bridge'
        rows.append(r)
    counts['U_rows'] = len(rows)
    def index():
        if not rows: return None, None
        X, Y = tr.transform(np.array([r['lon'] for r in rows]), np.array([r['lat'] for r in rows])); return cKDTree(np.column_stack([X, Y])), len(rows)
    def attach(recs, apply, label, radius=50.0, by_code=None):
        """recs: [(lon, lat, attrs)]; apply(row, attrs) fills the row; unmatched records become new rows (src label)."""
        tree, n0 = index(); hit = new = 0; used = set()
        for lon, lat, a in recs:
            r = by_code(a) if by_code else None
            if r is None and tree is not None:
                x, y = tr.transform(lon, lat); d, i = tree.query([x, y])
                if d <= radius and i < n0 and i not in used: r = rows[i]; used.add(i)
            if r is None:
                r = dict.fromkeys(COLUMNS); r.update(lon=round(lon, 6), lat=round(lat, 6), id=f'{label.lower()}{len(rows)}', src=label); rows.append(r); new += 1
            else:
                hit += 1; r['src'] = r['src'] + label if label not in r['src'] else r['src']
            apply(r, a)
        counts[f'{label}_matched'] = hit; counts[f'{label}_added'] = new
    # N: NAACC surveys
    try:
        info = layer_info(SRC_N, fetch); flds = info.get('fields', [])
        N = []
        for wh in ("State='MA'", "State='Massachusetts'", "UPPER(State) LIKE '%MASS%'"):
            try: N = query_all(SRC_N, where=wh, fetch=fetch, geometry=True, max_rows=max_rows)
            except Exception as e: print('NAACC where', wh, 'failed:', repr(e)[:100]); N = []
            if N: break
        if not N: N = query_all(SRC_N, bbox=MA_BBOX, fetch=fetch, geometry=True, max_rows=max_rows)
        fm = pick_fields(flds, [f['attributes'] for f in N[:3000]]); field_map['N'] = fm; print('NAACC field map:', fm)
        recs = []
        for f in N:
            a = f['attributes']; p = xy(f, a, fm['lat'], fm['lon'])
            if p is None: continue
            if fm['state'] and a.get(fm['state']) and str(a[fm['state']]).upper() not in ('MA', 'MASSACHUSETTS'): continue
            recs.append((p[0], p[1], a))
        def applyN(r, a):
            g = lambda k: a.get(fm[k]) if fm.get(k) else None
            shp = norm_shape(g('shape')); r['naacc'] = g('code') or r['naacc']; r['shape'] = shp or r['shape']; r['material'] = norm_material(g('material'))
            r['inlet'] = norm_inlet(g('inlet')); r['n_barrels'] = int(num(g('n_barrels')) or 1) if g('n_barrels') not in (None, '') else r['n_barrels']
            w, h = num(g('width'), FT), num(g('height'), FT)
            if shp == 'circular' and (w or h): r['span_m'] = r['rise_m'] = max(w or 0, h or 0)                     # round: one diameter
            else: r['span_m'], r['rise_m'] = w, h
            r['fill_m'] = num(g('fill'), FT); r['naacc_eval'] = g('evaluation'); r['road'] = r['road'] or g('road'); r['stream'] = r['stream'] or g('stream')
            xt = (g('xtype') or '').lower()
            if xt: r['xtype'] = xt
        attach(recs, applyN, 'N'); sources['N'] = dict(url=SRC_N, n=len(recs))
    except Exception as e: print('NAACC unavailable:', repr(e)[:200]); sources['N'] = dict(url=SRC_N, n=0, error=repr(e)[:200])
    # P: MA Stream Crossings Project (match by NAACC code first)
    try:
        designs = ['1HYR', '50YR', '25YR', '10YR', 'SCS']
        fl = ['CrosCode', 'ROAD', 'STREAM', 'LAT', 'LON', 'DRNAREA', 'PK10AEP', 'PK4AEP', 'PK2AEP', 'PK1AEP', 'PK02AEP', 'BFWDTH', 'BFDPTH'] + \
             [f'{t}{k}{d}' for d in designs for t in ('BC', 'AC', 'PC') for k in ('ORDE', 'USIE', 'DSIE')]
        Pf = query_all(SRC_P, fields=','.join(fl), fetch=fetch, max_rows=max_rows)
        bycode = {r['naacc']: r for r in rows if r.get('naacc')}
        recs = [(float(f['attributes']['LON']), float(f['attributes']['LAT']), f['attributes']) for f in Pf if f['attributes'].get('LAT') is not None]
        def firstv(a, k):
            for d in designs:
                for t in ('BC', 'AC', 'PC'):
                    v = num(a.get(f'{t}{k}{d}'), FT)
                    if v is not None: return v
            return None
        def applyP(r, a):
            r['naacc'] = r['naacc'] or a.get('CrosCode'); r['road'] = r['road'] or a.get('ROAD'); r['stream'] = r['stream'] or a.get('STREAM')
            r['drn_km2'] = num(a.get('DRNAREA'), SQMI)
            for c, k in zip(('pk10', 'pk25', 'pk50', 'pk100', 'pk500'), ('PK10AEP', 'PK4AEP', 'PK2AEP', 'PK1AEP', 'PK02AEP')): r[c] = num(a.get(k), CFS)
            r['bf_w'], r['bf_d'] = num(a.get('BFWDTH'), FT), num(a.get('BFDPTH'), FT)
            r['deck_m'], r['usie_m'], r['dsie_m'] = firstv(a, 'ORDE'), firstv(a, 'USIE'), firstv(a, 'DSIE')
        attach(recs, applyP, 'P', by_code=lambda a: bycode.get(a.get('CrosCode'))); sources['P'] = dict(url=SRC_P, n=len(recs))
    except Exception as e: print('Stream Crossings Project unavailable:', repr(e)[:200]); sources['P'] = dict(url=SRC_P, n=0, error=repr(e)[:200])
    # B: MassDOT structures (optional, attach only - never adds rows, the inventory includes bridges over roads/rail)
    for url in SRC_B:
        try:
            Bf = query_all(url, fields='bridgeDepartmentNumber,structureCategory,structureMaterial,culvertCondition,latitude,longitude', fetch=fetch, page=1000, max_rows=max_rows)
            tree, n0 = index(); hit = 0
            for f in Bf:
                a = f['attributes']
                if a.get('latitude') is None: continue
                x, y = tr.transform(float(a['longitude']), float(a['latitude'])); d, i = tree.query([x, y])
                if d <= 30:
                    r = rows[i]; r.update(mdot_cat=a.get('structureCategory'), mdot_mat=a.get('structureMaterial'), mdot_cond=a.get('culvertCondition')); hit += 1
                    if not r['material']: r['material'] = norm_material(a.get('structureMaterial'))
            counts['B_matched'] = hit; sources['B'] = dict(url=url, n=len(Bf)); break
        except Exception as e: print('MassDOT structures unavailable at', url, repr(e)[:120]); sources['B'] = dict(url=url, n=0, error=repr(e)[:120])
    # Massachusetts filter + county + District 3 flag
    lon = np.array([r['lon'] for r in rows]); lat = np.array([r['lat'] for r in rows])
    C = ma_counties(fetch) if counties == 'auto' else counties
    keep = np.ones(len(rows), bool)
    if C:
        cn = county_of(lon, lat, C); keep = cn != None   # noqa: E711
        for r, c in zip(rows, cn): r['county'] = c
    X, Y = tr.transform(lon, lat); d3 = (X >= D3_BOX[0]) & (X < D3_BOX[2]) & (Y >= D3_BOX[1]) & (Y < D3_BOX[3])
    for r, f in zip(rows, d3): r['d3'] = int(f)
    rows = [r for r, k in zip(rows, keep) if k]
    counts.update(rows=len(rows), outside_ma_dropped=int((~keep).sum()), d3=int(sum(r['d3'] for r in rows)),
                  with_geometry=int(sum(1 for r in rows if r['rise_m'])), with_shape=int(sum(1 for r in rows if r['shape'])),
                  with_deck=int(sum(1 for r in rows if r['deck_m'] is not None)), bridges=int(sum(1 for r in rows if r['shape'] == 'bridge')))
    return dict(columns=COLUMNS, rows=[[r[c] for c in COLUMNS] for r in rows], sources=sources, field_map=field_map, counts=counts,
                made=time.strftime('%Y-%m-%d'), units='lon/lat WGS84; span/rise/fill/bf/deck/inverts m (deck & inverts NAVD88); drn_km2 km2; pk* m3/s; None = unknown',
                d3_box_epsg26986=list(D3_BOX),
                note='U = USGS national stream crossings (backbone), N = NAACC field survey, P = MA Stream Crossings Project, B = MassDOT structures; src lists every source that contributed')

def selftest():
    """Synthetic pages for all four services + TIGERweb; checks paging, NAACC field detection, joins, unit conversion, MA and D3 flags."""
    from pyproj import Transformer
    inv = Transformer.from_crs(26986, 4326, always_xy=True)
    p_in = inv.transform(150000, 900000); p_in2 = inv.transform(150020, 900010); p_out = inv.transform(300000, 900000); p_n = inv.transform(160000, 880000)
    U0 = [dict(attributes=dict(OBJECTID=i, stream_crossing_id=i, nhdhr_gnis_stream_name='Brook', tiger2020_feature_names='Main St', tiger2020_mtfcc_feature_class='S1400', crossing_type=None),
               geometry=dict(x=x, y=y)) for i, (x, y) in enumerate([p_in, p_out] + [inv.transform(170000 + 20 * k, 920000) for k in range(2500)])]
    U1 = [dict(attributes=dict(stream_crossing_id=2, structure_id='NBI123', crossing_type='bridge', crossing_subtype=None))]
    NF = [dict(name=n, type='esriFieldTypeString') for n in ('Crossing_C', 'Inlet_Type', 'Inlet_Ty_1', 'Material', 'Structure_', 'Inlet_Widt', 'Inlet_Heig', 'Number_Of_', 'Road_Fill_', 'State', 'Crossing_T')]
    NA = [dict(attributes=dict(Crossing_C='xy42', Inlet_Type='Headwall and Wingwalls', Inlet_Ty_1='Round Culvert', Material='Metal', Structure_='Severe', Inlet_Widt='3', Inlet_Heig='3',
                               Number_Of_=2, Road_Fill_='4', State='MA', Crossing_T='Multiple Culverts'), geometry=dict(x=p_in2[0], y=p_in2[1])),
          dict(attributes=dict(Crossing_C='xy99', Inlet_Type='Projecting', Inlet_Ty_1='Box Culvert', Material='Concrete', Structure_='None', Inlet_Widt='6', Inlet_Heig='4',
                               Number_Of_=1, Road_Fill_='2', State='MA', Crossing_T='Single Culvert'), geometry=dict(x=p_n[0], y=p_n[1]))]
    PA = [dict(attributes=dict(CrosCode='xy42', ROAD='Main St', STREAM='Brook', LAT=p_in[1], LON=p_in[0], DRNAREA=1.0, PK10AEP=100.0, PK4AEP=150.0, PK2AEP=200.0, PK1AEP=250.0, PK02AEP=400.0,
                               BFWDTH=10.0, BFDPTH=1.0, BCORDE1HYR=500.0, BCUSIE1HYR=490.0, BCDSIE1HYR=489.0))]
    BA = [dict(attributes=dict(bridgeDepartmentNumber='W01', structureCategory='Culvert', structureMaterial='Concrete', culvertCondition='5', latitude=p_n[1], longitude=p_n[0]))]
    calls = []
    def fetch(url, params):
        calls.append(url); off = params.get('resultOffset', 0); n = params.get('resultRecordCount', 2000)
        def page(fs): return dict(features=fs[off:off + n], exceededTransferLimit=off + n < len(fs))
        if url.startswith(TIGERWEB):
            if url == TIGERWEB: return dict(layers=[dict(id=82, name='Counties'), dict(id=83, name='Counties Labels')])
            ring = [list(inv.transform(*c)) for c in ((100000, 850000), (250000, 850000), (250000, 950000), (100000, 950000), (100000, 850000))]
            return dict(features=[dict(attributes=dict(NAME='Worcester County'), geometry=dict(rings=[ring]))])
        if url == SRC_U + '/0/query': return page(U0)
        if url == SRC_U + '/1/query': return page(U1)
        if url == SRC_N: return dict(fields=NF)
        if url == SRC_N + '/query': return page(NA)
        if url == SRC_P + '/query': return page(PA)
        if url == SRC_B[0] + '/query': raise RuntimeError('unreachable')
        if url == SRC_B[1] + '/query': return page(BA)
        raise RuntimeError('unexpected ' + url)
    out = build(fetch); C = {c: i for i, c in enumerate(out['columns'])}; rows = {r[C['id']]: r for r in out['rows']}
    ok = True
    def check(name, cond, detail=''):
        nonlocal ok; ok &= bool(cond); print(('PASS ' if cond else 'FAIL ') + name, detail)
    check('paging: all 2,502 modelled crossings read', out['sources']['U']['n'] == 2502, out['sources']['U'])
    check('outside-MA point dropped', 'u1' not in rows and out['counts']['outside_ma_dropped'] == 1, out['counts'])
    fm = out['field_map']['N']; check('NAACC fields found by value', fm['shape'] == 'Inlet_Ty_1' and fm['inlet'] == 'Inlet_Type' and fm['material'] == 'Material', fm)
    a = rows['u0']; g = lambda k: a[C[k]]
    check('NAACC joined to modelled crossing (22 m away)', 'N' in g('src') and g('naacc') == 'xy42' and g('shape') == 'circular' and g('material') == 'metal' and g('inlet') == 'headwall_wingwall', a)
    check('ft -> m and barrels', abs(g('rise_m') - 0.914) < 1e-3 and g('span_m') == g('rise_m') and abs(g('fill_m') - 1.219) < 1e-3 and g('n_barrels') == 2)
    check('Project joined by NAACC code, SI units', 'P' in g('src') and abs(g('pk100') - 250 * CFS) < 1e-3 and abs(g('drn_km2') - 2.59) < 0.01 and abs(g('deck_m') - 152.4) < 0.01 and abs(g('usie_m') - 149.352) < 0.01, a)
    check('D3 flag + county', g('d3') == 1 and g('county') == 'Worcester County')
    nn = [r for r in out['rows'] if r[C['naacc']] == 'xy99']
    check('unmatched NAACC survey added as its own row, MassDOT attached (fallback host)', len(nn) == 1 and nn[0][C['src']] == 'N' and nn[0][C['shape']] == 'box' and nn[0][C['mdot_cat']] == 'Culvert'
          and abs(nn[0][C['span_m']] - 1.829) < 1e-3, nn)
    b = [r for r in out['rows'] if r[C['nbi_id']] == 'NBI123']
    check('NBI observation marks a bridge', len(b) == 1 and b[0][C['shape']] == 'bridge')
    check('vocabularies', norm_shape('Pipe Arch/Elliptical Culvert') == 'pipe_arch' and norm_shape('Open Bottom Arch Bridge/Culvert') == 'arch_open' and norm_inlet('Mitered to Slope') == 'mitered'
          and norm_material('Rock/Stone') == 'stone' and norm_material('Plastic') == 'plastic' and norm_shape('Bridge with Abutments') == 'bridge')
    print('crossings_all selftest', 'OK' if ok else 'FAILED'); return ok

if __name__ == '__main__':
    if '--selftest' in sys.argv: sys.exit(0 if selftest() else 1)
    out = build()
    p = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'docs', 'network', 'crossings_all.json')
    json.dump(out, open(p, 'w'), separators=(',', ':')); print('wrote', os.path.normpath(p), json.dumps(out['counts']))
