"""MassDOT District 3 data-request importer: Waze alerts, closure / incident logs, Repeating Flood Areas, drainage structures -> model inputs,
label rows and a before/after score, in one command each (how-to: docs/proto/massdot/IMPORT.md).

    python proto/massdot_import.py ingest <path|dir|url> [more ...] --kind waze|closures|rfa|drains [--map time=Event Start,lon=X] [--min-alerts 5]
    python proto/massdot_import.py score [--sources waze,closures,rfa] [--pool]     # held-out re-score with the new sources (before / after)
    python proto/massdot_import.py inspect <path|url>                               # columns, auto-detected mapping, CRS, row count; writes nothing
    python proto/massdot_import.py selftest

READERS  shapefile (.shp or a .zip holding one), file geodatabase (.gdb folder or .gdb.zip; --layer, else every layer), GeoJSON / JSON
  (a FeatureCollection, a Waze for Cities feed snapshot {"alerts": [...]} or a list of them / JSON lines), CSV / TXT, XLSX / XLS (every sheet),
  an ArcGIS REST FeatureServer / MapServer layer URL (…/FeatureServer/0; a service root reads every layer): paged JSON queries
  (resultOffset / resultRecordCount = the layer's maxRecordCount, objectId chunks when the server cannot page), f=geojson with outSR=4326,
  falling back to f=json (Esri geometry).  A directory reads every supported file in it (several Waze snapshots -> last-seen times).
  Geometry: the layer's own (reprojected to EPSG:4326 and 26986), else lon/lat columns, else x/y columns with the CRS guessed from the value
  range (WGS84, MA State Plane m 26986, MA State Plane ftUS 2249, Web Mercator 3857), else a 'location' column ({"x":..,"y":..} or WKT).
  Lines / polygons keep their geometry for the RFA distance; label rows use a point on the geometry.
COLUMN MAPPING  every canonical field has a list of accepted column names (MAPPING below: the Waze for Cities alert schema - uuid, type,
  subtype, pubMillis, street, city, location.x / .y, reliability, confidence, nThumbsUp, reportRating ... - and generic date / time / lat / lon /
  road / town / description / cause names); names are compared lower-case without punctuation, and 10-character shapefile truncations match.
  --map field=Column overrides (repeatable or comma-separated).  'inspect' prints what was detected.
TIMES  epoch ms / s numbers are UTC; text columns whose name says utc / gmt / zulu are UTC; everything else is US/Eastern local (--tz overrides).
  Separate date and time columns are joined.  time_local in the label rows is Eastern local, as in every other label file.

LABEL SOURCES (separate files, same schema as proto/data/labels_<storm>_*.csv plus provenance columns; never mixed into the closure labels)
  proto/data/waze_<storm>.csv              Waze flood alerts (subtype HAZARD_WEATHER_FLOOD / any FLOOD subtype, flood words in the description)
                                           and ROAD_CLOSED_HAZARD closures (construction / event closures dropped)
  proto/data/massdot_closure_<storm>.csv   closure / incident-log rows with a flood cause (flood, water, washout, ponding, inundat ...),
  proto/data/massdot_rfa_<storm>.csv       dated incidents of the Repeating Flood Areas layer (source MassDOT_RFA; date-only -> local noon)
  proto/data/massdot/waze_negcand_<storm>.csv   'not there' (thumbs-down / not-there count above thumbs-up) and removed-early alerts
                                           (seen < REMOVED_EARLY_MIN minutes, no thumbs-up, reliability < high): CANDIDATE negatives, never
                                           scored, never turned into a negative label (label_tiers.py: unreported roads stay unknown)
  Evidence tiers (fixed here 28 Oct 2026, before any MassDOT row exists; label_tiers.py names and weights):
    Waze       'corroborated' (1.0) when nThumbsUp >= 2, or reliability >= 8 (Waze 0-10 scale, 'high'), or >= 2 distinct alert uuids
               merged by the dedupe (independent reporters); else 'reported' (0.6).  Cross-family corroboration within 150 m (label_tiers
               rule) still upgrades a reported Waze row.
    closures   'confirmed_closure' (1.0): a closure (closure / closed / lanes blocked / detour words or a closure flag) with a flood cause;
               'confirmed_inundation' (1.0): flood cause + an observation on the road (label_tiers.WATER_OBS: impassable, stuck, depth,
               washout, submerged ...); 'reported' (0.6): any other flood-cause incident.  Rows without a flood cause are dropped (counted).
  Dedupe: the same uuid / incident id is one alert (first publish time, max thumbs / reliability, last-seen time); then alerts within
    DEDUPE_M (150 m) and DEDUPE_H (2 h) of an earlier kept alert are merged into it (n_reports, uuids kept).
  Storm assignment: a row belongs to every catalogue storm (docs/proto/obs/catalog.json and catalog_d456.json) whose window
    [t0 - 6 h, t0 + hours + 12 h] holds its time and whose 20 km box (padded 2 km) holds its point.  Rows of LOCKED storms
    (PROTOCOL.md §2: aug2015 aug2018 aug2020 jul2018 oct2016) are counted and dropped: nothing is written for them, not even a count by place.
    Unassigned rows go to proto/data/massdot/unmatched_<kind>.csv; local days with >= --min-alerts of them are listed as candidate new
    storms (docs/proto/massdot/candidate_storms_<kind>.json, with a suggested 20 km box), to be added through proto/obs_catalog.py.
  Rows without coordinates are kept with empty lon/lat (coord_quality 'none', never matched) and a proto/label_geocode.py query file is written.

SEGMENT TABLES (docs/graph_segments.json segment ids; District 3 network)
  rfa    proto/data/massdot/rfa_points.csv (normalised layer) and rfa_segments.csv: per segment within RFA_TABLE_M of any RFA feature -
         dist_rfa_m (road points to the nearest RFA geometry), n_rfa_250m, n_rfa_1km, rfa_closure (any RFA within 250 m flagged closure),
         rfa_dated_incidents (sum of dated incidents of RFA within 250 m).  Segments not listed: dist_rfa_m = RFA_TABLE_M (cap), counts 0.
         A learned-model feature / prior; it is time-agnostic (RFA sites were found from past floods), so use it inside LOSO only and
         read the overlap counts in the report.  Validation check (report): for every published primary run, the share of RFA-matched
         segments (30 m) in the model's top 3 % and the lift over 3 %; and new vs already-known sites against massdot_repeat_flood_d3.csv.
  drains proto/data/massdot/inlets_segments.csv: per segment with any structure within INLET_M (25 m) of its road - n_inlets (catch basin,
         inlet, grate, curb / drop inlet), n_culverts, n_manholes, n_outfalls, n_other, seg_len_m, inlets_per_100m, q_inlet_m3s =
         n_inlets x HEC-22 sag grate at 0.10 m ponding (0.0945 m3/s, proto/pluvial_v2.Q_SAG), n_in_pluvial = max(1, n_inlets) (the observed
         count that replaces pluvial_v2's road-length / 100 m proxy), and n_flood_known (structures flagged as a known flooding location).
         A table only: lf_drains.py / pluvial_v2.py are not changed.  Structure points are not written anywhere (aggregates only).

SCORE  'score' re-scores the published primary runs (docs/proto/parity/catalog, else turing, else transfer) of every storm that has a new
  label file, with proto/score_v2.py, twice: as committed, and with the new sources added (SCORE_WAZE=1 -> waze_<storm>.csv, SCORE_MASSDOT=1
  -> massdot_closure_<storm>.csv and massdot_rfa_<storm>.csv; both are set for the 'after' pass, the 'before' pass is the committed label set).  With SCORE_TIERS=1 the
  new families get the tiers above through a runtime hook on proto/label_tiers.py (that file is not edited).  Prints sites / hits / recall at
  3 % before and after per storm; --pool also scores every other held-out-23 storm once and prints the pooled before / after.  This is a
  secondary analysis (new label sources), not a model --compare: PROTOCOL.md §1 says a label change re-scores baseline and candidate together.
"""
import argparse
import csv
import datetime as dt
import glob
import io
import json
import math
import os
import re
import sys
import tempfile
import zipfile

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
DATA = os.path.join(HERE, 'data'); SIDE = os.path.join(DATA, 'massdot'); DOCS = os.path.join(ROOT, 'docs', 'proto', 'massdot')
CATALOGS = (os.path.join(ROOT, 'docs', 'proto', 'obs', 'catalog.json'), os.path.join(ROOT, 'docs', 'proto', 'obs', 'catalog_d456.json'))
LOCKED = ('aug2015', 'aug2018', 'aug2020', 'jul2018', 'oct2016')            # PROTOCOL.md §2 (same tuple as score_v2 / label_tiers)
TZ = 'America/New_York'
DEDUPE_M, DEDUPE_H = 150.0, 2.0
WIN_BEFORE_H, WIN_AFTER_H, BOX_PAD_M = 6.0, 12.0, 2000.0
RELIABLE = 8                     # Waze reliability 0-10: 'high'
REMOVED_EARLY_MIN = 20.0
MIN_ALERTS = 5
RFA_TABLE_M = 5000.0
INLET_M = 25.0
Q_SAG = 0.0945                   # m3/s, HEC-22 sag grate at 0.10 m (proto/pluvial_v2.py)
LABEL_COLS = ['id', 'name', 'road', 'town', 'type', 'time_local', 'time_quality', 'lon', 'lat', 'coord_quality', 'source_url', 'quote', 'source',
              'tier', 'tier_reason', 'n_reports', 'uuids', 'thumbs_up', 'reliability', 'confidence', 'end_local', 'orig_type']
KINDS = ('waze', 'closures', 'rfa', 'drains')

# ------------------------------------------------------------------------------------------------ column mapping table
# canonical field -> accepted column names (compared lower-case, punctuation stripped; 10-char shapefile truncations also match)
MAPPING = {
    'uuid':        ['uuid', 'rfa_id', 'rfaid', 'site_id', 'siteid', 'alert_uuid', 'alertid', 'alert_id', 'id_alert', 'incident_id', 'incidentid', 'event_id', 'eventid', 'hoc_id',
                    'record_id', 'case_number', 'ticket', 'objectid_1'],
    'type':        ['type', 'alert_type', 'alerttype', 'event_type', 'eventtype', 'incident_type', 'incidenttype', 'category', 'class'],
    'subtype':     ['subtype', 'sub_type', 'alert_subtype', 'event_subtype', 'subcategory'],
    'time':        ['pubMillis', 'pub_millis', 'pub_utc_date', 'pubutcdate', 'startTime', 'start_time', 'starttime', 'start_date', 'startdate',
                    'begin_time', 'event_start', 'reported', 'reported_time', 'report_time', 'reported_at', 'created', 'created_at',
                    'created_date', 'open_time', 'opened', 'datetime', 'date_time', 'timestamp', 'time_local', 'event_date', 'incident_date',
                    'flood_date', 'date'],
    'time_only':   ['time', 'start_clock', 'hour', 'incident_time', 'event_time'],
    'end_time':    ['endTime', 'end_time', 'endtime', 'end_date', 'enddate', 'cleared', 'cleared_time', 'clear_time', 'closed_time',
                    'reopened', 'reopen_time', 'last_seen', 'lastseen', 'retrieval_date', 'removed', 'resolved', 'end'],
    'lon':         ['lon', 'long', 'longitude', 'lng', 'location_x', 'locationx', 'location.x', 'x_coord', 'xcoord', 'point_x', 'gps_long', 'lon_dd'],
    'lat':         ['lat', 'latitude', 'location_y', 'locationy', 'location.y', 'y_coord', 'ycoord', 'point_y', 'gps_lat', 'lat_dd'],
    'x':           ['x', 'easting', 'east', 'xm', 'x_sp', 'mass_x'],
    'y':           ['y', 'northing', 'north', 'ym', 'y_sp', 'mass_y'],
    'location':    ['location', 'geo', 'geom', 'wkt', 'shape', 'the_geom', 'point'],
    'road':        ['street', 'road', 'roadway', 'route', 'rte', 'route_name', 'routename', 'road_name', 'roadname', 'street_name', 'rdwy',
                    'highway', 'location_desc', 'facility'],
    'cross':       ['cross_street', 'crossstreet', 'at_street', 'intersection', 'near', 'from_street', 'exit', 'interchange', 'location_detail'],
    'town':        ['city', 'town', 'municipality', 'muni', 'community', 'city_town', 'town_name', 'townname', 'place'],
    'reliability': ['reliability'],
    'confidence':  ['confidence'],
    'thumbs':      ['nThumbsUp', 'n_thumbs_up', 'thumbs_up', 'thumbsup', 'thumbs', 'upvotes'],
    'not_there':   ['nNotThere', 'n_not_there', 'not_there', 'notthere', 'nThumbsDown', 'thumbs_down', 'thumbsdown', 'downvotes'],
    'rating':      ['reportRating', 'report_rating'],
    'desc':        ['reportDescription', 'report_description', 'description', 'descr', 'desc', 'comments', 'comment', 'remarks', 'notes',
                    'narrative', 'details', 'impact', 'event_description', 'summary', 'location'],
    'cause':       ['cause', 'reason', 'closure_reason', 'closurereason', 'incident_cause', 'event_cause', 'cause_desc'],
    'closure':     ['closure', 'closed', 'road_closed', 'roadclosed', 'is_closed', 'lanes_closed', 'lanesclosed', 'closure_type', 'closuretype',
                    'full_closure'],
    'struct':      ['structure', 'structure_type', 'structuretype', 'struct_type', 'asset_type', 'assettype', 'feature_type', 'featuretype',
                    'feat_type', 'type', 'ftype', 'subtype', 'layer', 'class', 'category', 'description'],
    'flood_flag':  ['flooding', 'known_flooding', 'flood_flag', 'floods', 'flood_prone', 'floodprone', 'flood_loc', 'problem', 'issue'],
    'n_incidents': ['n_incidents', 'incidents', 'incident_count', 'num_events', 'count', 'frequency', 'events', 'occurrences'],
    'dates':       ['dates', 'incident_dates', 'flood_dates', 'event_dates', 'history', 'incident_history', 'last_flood', 'last_event'],
}
WAZE_FLOOD = re.compile(r'FLOOD', re.I)
WAZE_CLOSE = re.compile(r'ROAD_CLOSED', re.I)
NOT_FLOOD_CLOSE = re.compile(r'CONSTRUCTION|EVENT$|_EVENT|PARADE|SPECIAL', re.I)
FLOOD_TXT = re.compile(r'flood|high water|standing water|water (on|over|across)|ponding|inundat|submerg|wash ?out|under ?water|'
                       r'drain(age)? (backup|failure|issue)|culvert|sinkhole|water in (the )?road|water main', re.I)
NOT_FLOOD_TXT = re.compile(r'water main', re.I)      # a water-main break is not a storm flood (kept out unless storm words also appear)
CLOSE_TXT = re.compile(r'\bclosed\b|closure|\bclose\b|shut ?down|lanes? blocked|all lanes|detour|road closed|ramp closed', re.I)
STRUCT_CLASSES = [('culvert', re.compile(r'culv|pipe ?arch|box ?cul|\bcmp\b|\brcp\b|headwall|endwall', re.I)),
                  ('outfall', re.compile(r'outfall|outlet|\bof\b|discharge|flared', re.I)),
                  ('manhole', re.compile(r'manhole|\bmh\b|\bdmh\b|\bsmh\b|junction|structure box', re.I)),
                  ('inlet', re.compile(r'catch ?basin|\bcb\b|\bcbs\b|inlet|grate|curb|drop|leach|gutter|\bdi\b|\bci\b|trench ?drain|scupper', re.I))]


def norm(s):
    return re.sub(r'[^a-z0-9]', '', str(s).lower())


def detect_columns(cols, overrides=None, kind=None):
    """{canonical field: column} for a list of columns.  First listed name wins; each column used once (except 'location' / 'desc')."""
    by = {norm(c): c for c in cols if not str(c).startswith('_')}; out = {}; used = set()
    for f, names in MAPPING.items():
        if kind == 'drains' and f == 'type': continue
        for n in names:
            k = norm(n); c = by.get(k)
            if c is None:
                c = next((c0 for c0 in cols if len(str(c0)) == 10 and len(n) > 10 and n.lower().startswith(str(c0).lower())), None)   # shapefile 10-char cut
            if c is not None and (c not in used or f in ('desc', 'struct', 'location')):
                out[f] = c; used.add(c); break
    for k, v in (overrides or {}).items():
        if v in cols or v == '': out[k] = v
        else: raise SystemExit(f'--map {k}={v}: no column {v!r}; columns are {list(cols)}')
    return {k: v for k, v in out.items() if v}


def parse_map(items):
    out = {}
    for it in items or []:
        for part in it.split(','):
            if '=' in part:
                k, v = part.split('=', 1); k = k.strip()
                if k not in MAPPING: raise SystemExit(f'--map: unknown field {k!r}; fields are {sorted(MAPPING)}')
                out[k] = v.strip()
    return out


# ------------------------------------------------------------------------------------------------ readers
def _gpd():
    import geopandas as gpd
    return gpd


def _opener(url):
    import urllib.request
    from urllib.parse import urlparse
    h = urlparse(url).hostname or ''
    if h in ('localhost', '127.0.0.1', '::1'): return urllib.request.build_opener(urllib.request.ProxyHandler({}))
    return urllib.request.build_opener()


def _get_json(url, params):
    from urllib.parse import urlencode
    u = url + ('&' if '?' in url else '?') + urlencode(params)
    with _opener(u).open(u, timeout=120) as r: J = json.loads(r.read().decode('utf-8'))
    if isinstance(J, dict) and 'error' in J: raise RuntimeError(f"ArcGIS error {J['error']}")
    return J


def esri_to_geojson(g):
    if not g: return None
    if 'x' in g: return dict(type='Point', coordinates=[g['x'], g['y']])
    if 'points' in g: return dict(type='MultiPoint', coordinates=g['points'])
    if 'paths' in g: return dict(type='MultiLineString', coordinates=g['paths'])
    if 'rings' in g: return dict(type='Polygon', coordinates=g['rings'])          # outer + holes as written; good enough for a distance
    return None


def read_rest(url, layer=None, where='1=1'):
    """ArcGIS REST layer (…/FeatureServer/<n> or MapServer/<n>) -> GeoDataFrame in EPSG:4326; a service root reads every layer."""
    gpd = _gpd(); url = url.split('?')[0].rstrip('/')
    if re.search(r'/(Feature|Map)Server$', url):
        info = _get_json(url, dict(f='json')); ids = [l['id'] for l in info.get('layers', [])]
        if layer is not None: ids = [int(layer)]
        frames = [read_rest(f'{url}/{i}', where=where).assign(_layer=str(i)) for i in ids]
        return gpd.GeoDataFrame(__import__('pandas').concat(frames, ignore_index=True), crs=4326) if frames else gpd.GeoDataFrame()
    info = _get_json(url, dict(f='json')); page = int(info.get('maxRecordCount') or 1000)
    adv = info.get('advancedQueryCapabilities', {}); can_page = adv.get('supportsPagination', True)
    feats = []

    def fetch(params):
        base = dict(where=where, outFields='*', outSR=4326, returnGeometry='true')
        base.update(params)
        try:
            J = _get_json(url + '/query', dict(base, f='geojson'))
            if 'features' in J and (not J['features'] or 'properties' in J['features'][0]): return J['features'], J.get('exceededTransferLimit', J.get('properties', {}).get('exceededTransferLimit', False))
        except Exception:
            pass
        J = _get_json(url + '/query', dict(base, f='json'))
        return ([dict(type='Feature', properties=f.get('attributes', {}), geometry=esri_to_geojson(f.get('geometry'))) for f in J.get('features', [])],
                J.get('exceededTransferLimit', False))

    if can_page:
        off = 0
        while True:
            F, more = fetch(dict(resultOffset=off, resultRecordCount=page)); feats += F; off += len(F)
            if not F or (not more and len(F) < page): break
    else:
        oids = sorted(_get_json(url + '/query', dict(where=where, returnIdsOnly='true', f='json')).get('objectIds') or [])
        for i in range(0, len(oids), page):
            F, _ = fetch(dict(objectIds=','.join(map(str, oids[i:i + page])), where='')); feats += F
    if not feats: return gpd.GeoDataFrame(geometry=[], crs=4326)
    return gpd.GeoDataFrame.from_features(dict(type='FeatureCollection', features=feats), crs=4326)


def _waze_json(J, src):
    """Waze for Cities feed snapshot(s) -> rows (flattened location, snapshot time as last_seen)."""
    snaps = J if isinstance(J, list) else [J]; rows = []
    for S in snaps:
        if not isinstance(S, dict) or 'alerts' not in S: continue
        seen = S.get('endTimeMillis') or S.get('startTimeMillis') or S.get('endTime') or S.get('startTime')
        for a in S['alerts']:
            r = {k: v for k, v in a.items() if k != 'location'}
            loc = a.get('location') or {}
            r['location_x'] = loc.get('x'); r['location_y'] = loc.get('y'); r['_last_seen'] = seen; r['_src'] = src; rows.append(r)
    return rows


def read_any(path, layer=None):
    """-> (GeoDataFrame or DataFrame, note).  Geometry, when present, is EPSG:4326 after this call (or CRS unknown -> guessed later)."""
    import pandas as pd
    gpd = _gpd()
    if re.match(r'https?://', path): return read_rest(path, layer), f'ArcGIS REST {path}'
    if os.path.isdir(path) and not path.lower().rstrip('/').endswith('.gdb'):
        fr = []
        for f in sorted(glob.glob(os.path.join(path, '*'))):
            if re.search(r'\.(shp|geojson|json|jsonl|csv|txt|xlsx|xls|zip)$', f, re.I) or f.lower().endswith('.gdb'):
                d, _ = read_any(f, layer); d['_src'] = d.get('_src', os.path.basename(f)); fr.append(d)
        if not fr: raise SystemExit(f'{path}: no readable files')
        geo = [d for d in fr if isinstance(d, gpd.GeoDataFrame) and 'geometry' in d and d.geometry.notna().any()]
        df = pd.concat([pd.DataFrame(d) for d in fr], ignore_index=True)
        if geo: df = gpd.GeoDataFrame(df, geometry='geometry', crs=geo[0].crs)
        return df, f'directory of {len(fr)} files'
    low = path.lower()
    if low.endswith(('.csv', '.txt')):
        return pd.read_csv(path, dtype=str, keep_default_na=False, encoding_errors='replace'), 'csv'
    if low.endswith(('.xlsx', '.xls', '.xlsm')):
        sh = pd.read_excel(path, sheet_name=None, dtype=object)
        fr = [d.assign(_sheet=k) for k, d in sh.items() if len(d)]
        return pd.concat(fr, ignore_index=True), f'excel ({len(fr)} sheets)'
    if low.endswith(('.json', '.jsonl')):
        txt = open(path, encoding='utf-8', errors='replace').read().strip()
        try: J = json.loads(txt)
        except json.JSONDecodeError: J = [json.loads(l) for l in txt.splitlines() if l.strip()]
        if isinstance(J, dict) and J.get('type') == 'FeatureCollection': return gpd.read_file(path), 'geojson'
        W = _waze_json(J, os.path.basename(path))
        if W: return pd.DataFrame(W), 'waze feed json'
        if isinstance(J, list): return pd.DataFrame(J), 'json records'
        if isinstance(J, dict) and 'features' in J:      # Esri JSON
            return gpd.GeoDataFrame.from_features([dict(type='Feature', properties=f.get('attributes', {}), geometry=esri_to_geojson(f.get('geometry')))
                                                   for f in J['features']]), 'esri json'
        raise SystemExit(f'{path}: unrecognised JSON')
    if low.endswith('.geojson'): return gpd.read_file(path), 'geojson'
    if low.endswith('.zip'):
        z = zipfile.ZipFile(path); names = z.namelist()
        if any('.gdb/' in n.lower() for n in names):
            return _read_gdb('zip://' + path if not any(n.lower().endswith('.gdb/') for n in names) else path, layer)
        shp = [n for n in names if n.lower().endswith('.shp')]
        if shp:
            fr = [gpd.read_file(f'zip://{path}!{n}').assign(_layer=os.path.basename(n)[:-4]) for n in shp]
            return gpd.GeoDataFrame(pd.concat(fr, ignore_index=True), crs=fr[0].crs), f'zipped shapefile ({len(fr)})'
        tab = [n for n in names if re.search(r'\.(csv|xlsx|xls|geojson|json)$', n, re.I)]
        if tab:
            d = tempfile.mkdtemp(); z.extractall(d); return read_any(d, layer)
        raise SystemExit(f'{path}: zip without shapefile / gdb / table')
    if low.rstrip('/').endswith('.gdb'): return _read_gdb(path, layer)
    return gpd.read_file(path), os.path.splitext(low)[1].lstrip('.') or 'vector'


def _read_gdb(path, layer=None):
    import pandas as pd
    import pyogrio
    gpd = _gpd()
    layers = [l[0] for l in pyogrio.list_layers(path)] if layer is None else [layer]
    fr = []
    for l in layers:
        d = gpd.read_file(path, layer=l)
        if len(d): fr.append(d.assign(_layer=l))
    if not fr: raise SystemExit(f'{path}: empty geodatabase')
    crs = next((d.crs for d in fr if getattr(d, 'crs', None)), None)
    fr = [d.to_crs(crs) if getattr(d, 'crs', None) and crs and d.crs != crs else d for d in fr]
    return gpd.GeoDataFrame(pd.concat(fr, ignore_index=True), geometry='geometry', crs=crs), f'file geodatabase ({len(fr)} layers)'


def guess_crs(x, y):
    x = np.asarray(x, float); y = np.asarray(y, float); ok = np.isfinite(x) & np.isfinite(y) & (x != 0)
    if not ok.any(): return None
    mx, my = np.nanmedian(x[ok]), np.nanmedian(y[ok])
    if -74 < mx < -69 and 41 < my < 43.5: return 4326
    if -74 < my < -69 and 41 < mx < 43.5: return 'swap'
    if 30000 < mx < 340000 and 770000 < my < 970000: return 26986
    if 100000 < mx < 1120000 and 2520000 < my < 3190000: return 2249
    if -8300000 < mx < -7700000 and 5000000 < my < 5400000: return 3857
    return None


def to_points(df, cols):
    """-> (lon, lat, geometry4326 or None, crs note) arrays for every row."""
    gpd = _gpd(); n = len(df); lon = np.full(n, np.nan); lat = np.full(n, np.nan); geom = None; note = 'none'
    from pyproj import Transformer
    if isinstance(df, gpd.GeoDataFrame) and 'geometry' in df and df.geometry.notna().any():
        g = df.geometry
        if g.crs is None:
            rp = g.representative_point(); c = guess_crs(rp.x, rp.y)
            if c in (None, 'swap'): raise SystemExit('geometry has no CRS and the coordinates do not look like MA (WGS84 / 26986 / 2249 / 3857)')
            g = g.set_crs(c); note = f'geometry, CRS guessed EPSG:{c}'
        else: note = f'geometry, EPSG:{g.crs.to_epsg()}'
        g = g.to_crs(4326); geom = g; ok = g.notna() & ~g.is_empty
        rp = g[ok].representative_point(); lon[ok.values] = rp.x.values; lat[ok.values] = rp.y.values
        if ok.all(): return lon, lat, geom, note
    if 'lon' in cols and 'lat' in cols:
        a = num(df[cols['lon']]); b = num(df[cols['lat']]); c = guess_crs(a, b)
        if c == 'swap': a, b = b, a; c = 4326
        if c is None: c = 4326
        if c != 4326: a, b = Transformer.from_crs(c, 4326, always_xy=True).transform(a, b)
        m = np.isnan(lon); lon[m] = np.asarray(a)[m]; lat[m] = np.asarray(b)[m]; note = f'columns {cols["lon"]}/{cols["lat"]} (EPSG:{c})'
    elif 'x' in cols and 'y' in cols:
        a = num(df[cols['x']]); b = num(df[cols['y']]); c = guess_crs(a, b)
        if c == 'swap': a, b = b, a; c = 4326
        if c is None: raise SystemExit(f'x/y columns {cols["x"]}/{cols["y"]}: CRS not recognised; reproject or pass --map lon=,lat=')
        if c != 4326: a, b = Transformer.from_crs(c, 4326, always_xy=True).transform(a, b)
        m = np.isnan(lon); lon[m] = np.asarray(a)[m]; lat[m] = np.asarray(b)[m]; note = f'columns {cols["x"]}/{cols["y"]} (EPSG:{c})'
    elif 'location' in cols:
        for i, v in enumerate(df[cols['location']].tolist()):
            p = parse_loc(v)
            if p and np.isnan(lon[i]): lon[i], lat[i] = p
        note = f'column {cols["location"]} (dict / WKT)'
    bad = ~(np.isfinite(lon) & np.isfinite(lat) & (lon > -74) & (lon < -69) & (lat > 41) & (lat < 43.5))
    lon[bad] = np.nan; lat[bad] = np.nan
    return lon, lat, geom, note


def parse_loc(v):
    if isinstance(v, dict) and 'x' in v: return float(v['x']), float(v['y'])
    s = str(v or '')
    m = re.search(r"['\"]?x['\"]?\s*[:=]\s*(-?\d+\.?\d*).*?['\"]?y['\"]?\s*[:=]\s*(-?\d+\.?\d*)", s)
    if m: return float(m.group(1)), float(m.group(2))
    m = re.search(r'POINT\s*\(\s*(-?\d+\.?\d*)\s+(-?\d+\.?\d*)', s, re.I)
    if m: return float(m.group(1)), float(m.group(2))
    return None


def num(s):
    import pandas as pd
    return pd.to_numeric(pd.Series(list(s)).astype(str).str.replace(',', '').str.strip().replace({'': None, 'None': None, 'nan': None}),
                         errors='coerce').to_numpy(float)


def parse_times(df, cols, field='time', tz=None):
    """-> numpy datetime64[s] UTC per row (NaT when missing)."""
    import pandas as pd
    if field not in cols: return np.full(len(df), np.datetime64('NaT'), 'datetime64[s]')
    name = cols[field]; v = pd.Series(list(df[name]))
    if field == 'time' and 'time_only' in cols and 'time_only' != field:
        v = v.astype(str).str.slice(0, 10) + ' ' + pd.Series(list(df[cols['time_only']])).astype(str)
    out = pd.Series(pd.NaT, index=v.index, dtype='datetime64[ns, UTC]')
    nv = pd.to_numeric(v, errors='coerce')
    ms = nv > 1e11; s_ = (nv > 1e9) & ~ms
    out[ms] = pd.to_datetime(nv[ms], unit='ms', utc=True); out[s_] = pd.to_datetime(nv[s_], unit='s', utc=True)
    rest = out.isna() & v.notna() & (v.astype(str).str.strip() != '') & ~(ms | s_)
    if rest.any():
        utc = bool(re.search(r'utc|gmt|zulu|millis', name, re.I)) or tz == 'UTC'
        try: p = pd.to_datetime(v[rest].astype(str), errors='coerce', format='mixed')
        except (ValueError, TypeError): p = pd.Series({i: pd.to_datetime(str(x), errors='coerce') for i, x in v[rest].items()})
        for i, t in p.items():
            if pd.isna(t): continue
            t = pd.Timestamp(t)
            if t.tzinfo is None: t = t.tz_localize('UTC' if utc else (tz or TZ), ambiguous='NaT', nonexistent='shift_forward')
            out[i] = t.tz_convert('UTC') if not pd.isna(t) else pd.NaT
    return out.dt.tz_localize(None).to_numpy('datetime64[s]')


def local_str(t):
    import pandas as pd
    if np.isnat(t): return ''
    return pd.Timestamp(t).tz_localize('UTC').tz_convert(TZ).strftime('%Y-%m-%dT%H:%M')


def clean_town(v):
    return re.sub(r',?\s*(MA|Mass\.?|Massachusetts)\s*$', '', str(v or '').strip(), flags=re.I).strip().title()


def col(df, cols, f, i, d=''):
    c = cols.get(f)
    if not c: return d
    v = df[c].iloc[i]
    return d if v is None or (isinstance(v, float) and math.isnan(v)) else v


def fnum(x, d=0.0):
    try:
        v = float(x); return d if math.isnan(v) else v
    except (TypeError, ValueError): return d


# ------------------------------------------------------------------------------------------------ normalise per kind
def xy26986(lon, lat):
    from pyproj import Transformer
    return Transformer.from_crs(4326, 26986, always_xy=True).transform(np.asarray(lon, float), np.asarray(lat, float))


def normalise(df, cols, kind, tz=None):
    """-> list of event dicts (waze / closures) with t (UTC datetime64), lon, lat, text fields; plus counts of dropped rows."""
    lon, lat, _, crs_note = to_points(df, cols); T = parse_times(df, cols, 'time', tz); TE = parse_times(df, cols, 'end_time', tz)
    if '_last_seen' in df:
        LS = parse_times(df.rename(columns={'_last_seen': '__ls'}), {'time': '__ls'}, 'time', tz)
        TE = np.where(np.isnat(TE), LS, TE)
    ev = []; drop = dict(no_flood=0, construction_or_event=0, no_time=0, no_coords=0)
    for i in range(len(df)):
        typ = str(col(df, cols, 'type', i)); sub = str(col(df, cols, 'subtype', i)); desc = str(col(df, cols, 'desc', i))
        cause = str(col(df, cols, 'cause', i)); clo = str(col(df, cols, 'closure', i)); txt = ' '.join([typ, sub, desc, cause])
        if kind == 'waze':
            is_flood = bool(WAZE_FLOOD.search(sub) or WAZE_FLOOD.search(typ) or FLOOD_TXT.search(desc))
            is_close = bool(WAZE_CLOSE.search(typ) or WAZE_CLOSE.search(sub))
            if is_close and not is_flood and NOT_FLOOD_CLOSE.search(sub): drop['construction_or_event'] += 1; continue
            if not is_flood and not (is_close and (sub.upper() == 'ROAD_CLOSED_HAZARD' or FLOOD_TXT.search(desc))): drop['no_flood'] += 1; continue
            otype = 'closed' if is_close else 'flooded'
        else:
            flood = bool(FLOOD_TXT.search(txt)) and not (NOT_FLOOD_TXT.search(txt) and not re.search(r'flood|storm|rain', txt, re.I))
            if not flood: drop['no_flood'] += 1; continue
            is_close = bool(CLOSE_TXT.search(txt)) or str(clo).strip().lower() in ('1', 'y', 'yes', 'true', 't', 'full', 'closed', 'partial')
            otype = 'closed' if is_close else 'flooded'
        if np.isnat(T[i]): drop['no_time'] += 1; continue
        if np.isnan(lon[i]): drop['no_coords'] += 1
        uid = str(col(df, cols, 'uuid', i) or f'row{i}')
        ev.append(dict(t=T[i], te=TE[i], lon=lon[i], lat=lat[i], uuid=uid, type=otype, orig_type='/'.join(x for x in (typ, sub) if x),
                       road=str(col(df, cols, 'road', i)).strip(), cross=str(col(df, cols, 'cross', i)).strip(), town=clean_town(col(df, cols, 'town', i)),
                       desc=desc.strip(), cause=cause.strip(), thumbs=fnum(col(df, cols, 'thumbs', i)), not_there=fnum(col(df, cols, 'not_there', i)),
                       rel=fnum(col(df, cols, 'reliability', i), np.nan), conf=fnum(col(df, cols, 'confidence', i), np.nan), src=str(df['_src'].iloc[i]) if '_src' in df else ''))
    return ev, drop, crs_note


def dedupe(ev):
    """Same uuid -> one alert; then single-pass merge of alerts within DEDUPE_M and DEDUPE_H of an earlier kept alert."""
    by = {}
    for e in sorted(ev, key=lambda e: e['t']):
        k = e['uuid']
        if k.startswith('row') or k not in by: by[k if not k.startswith('row') else f'{k}:{len(by)}'] = dict(e, uuids={e['uuid']}, n_reports=1); continue
        a = by[k]; a['thumbs'] = max(a['thumbs'], e['thumbs']); a['not_there'] = max(a['not_there'], e['not_there'])
        a['rel'] = np.nanmax([a['rel'], e['rel']]); a['conf'] = np.nanmax([a['conf'], e['conf']])
        a['te'] = max([x for x in (a['te'], e['te'], e['t']) if not np.isnat(x)], default=a['te'])
        if np.isnan(a['lon']) and not np.isnan(e['lon']): a['lon'], a['lat'] = e['lon'], e['lat']
    A = sorted(by.values(), key=lambda e: e['t']); n_uuid = len(A)
    x, y = xy26986([e['lon'] for e in A], [e['lat'] for e in A]); kept = []
    for i, e in enumerate(A):
        e['_x'], e['_y'] = x[i], y[i]; tgt = None
        if np.isfinite(x[i]):
            for k in reversed(kept):
                dh = (e['t'] - k['_tlast']) / np.timedelta64(1, 'h')
                if dh > DEDUPE_H: continue
                if math.hypot(k['_x'] - x[i], k['_y'] - y[i]) <= DEDUPE_M: tgt = k; break
        if tgt is None: e['_tlast'] = e['t']; kept.append(e); continue
        tgt['_tlast'] = e['t']; tgt['n_reports'] += e['n_reports']; tgt['uuids'] |= e['uuids']; tgt['thumbs'] = max(tgt['thumbs'], e['thumbs'])
        tgt['not_there'] = max(tgt['not_there'], e['not_there']); tgt['rel'] = np.nanmax([tgt['rel'], e['rel']])
        if e['type'] == 'closed': tgt['type'] = 'closed'
        tes = [z for z in (tgt['te'], e['te']) if not np.isnat(z)]; tgt['te'] = max(tes) if tes else tgt['te']
        if not tgt['desc'] and e['desc']: tgt['desc'] = e['desc']
    return kept, n_uuid


def tier_of(e, kind):
    sys.path.insert(0, HERE); import label_tiers as LT
    if kind == 'waze':
        r = []
        if e['thumbs'] >= 2: r.append('thumbs>=2')
        if np.isfinite(e['rel']) and e['rel'] >= RELIABLE: r.append(f'reliability>={RELIABLE}')
        if len(e['uuids']) >= 2: r.append('>=2 uuids')
        return ('corroborated', ';'.join(r)) if r else ('reported', 'single alert')
    txt = ' '.join([e['desc'], e['cause'], e['orig_type']])
    if e['type'] == 'closed': return 'confirmed_closure', 'closure with flood cause'
    if LT.WATER_OBS.search(txt) or re.search(r'wash ?out|sinkhole', txt, re.I): return 'confirmed_inundation', 'flood cause + observation on road'
    return 'reported', 'flood-cause incident'


def negative_candidate(e):
    if e['not_there'] > e['thumbs'] and e['not_there'] >= 1: return 'not_there'
    if not np.isnat(e['te']):
        mins = (e['te'] - e['t']) / np.timedelta64(1, 'm')
        if mins < REMOVED_EARLY_MIN and e['thumbs'] == 0 and not (np.isfinite(e['rel']) and e['rel'] >= RELIABLE) and len(e['uuids']) == 1:
            return f'removed_early ({mins:.0f} min)'
    return None


# ------------------------------------------------------------------------------------------------ storm catalogue
def catalogue():
    import pandas as pd
    out = []
    for f in CATALOGS:
        if not os.path.exists(f): continue
        for e in json.load(open(f))['events']:
            if not e.get('t0') or not e.get('box_26986'): continue
            t0 = pd.Timestamp(e['t0'].replace('Z', '')).to_datetime64().astype('datetime64[s]')
            a = t0 - np.timedelta64(int(WIN_BEFORE_H * 3600), 's'); b = t0 + np.timedelta64(int((float(e.get('hours', 24)) + WIN_AFTER_H) * 3600), 's')
            out.append(dict(id=e['id'], a=a, b=b, box=[float(v) for v in e['box_26986']], cat=os.path.basename(f), locked=e['id'] in LOCKED))
    return out


def assign(e, C):
    if not np.isfinite(e.get('_x', np.nan)):
        return [s for s in C if s['a'] <= e['t'] <= s['b']], True        # no coordinates: time only (never matched by the scorer)
    p = BOX_PAD_M
    return [s for s in C if s['a'] <= e['t'] <= s['b'] and s['box'][0] - p <= e['_x'] <= s['box'][2] + p and s['box'][1] - p <= e['_y'] <= s['box'][3] + p], False


# ------------------------------------------------------------------------------------------------ ingest: waze / closures
def label_row(e, kind, storm, k):
    tier, why = tier_of(e, kind)
    pre = 'WZ' if kind == 'waze' else ('RFA' if e.get('src_kind') == 'rfa' else 'MD')
    road = e['road'] or (e['desc'][:40] if kind != 'waze' else '')
    name = f"{road or 'unnamed road'}{(' at ' + e['cross']) if e['cross'] else ''}: {e['type']}"
    has = np.isfinite(e['lon'])
    src = 'Waze' if kind == 'waze' else ('MassDOT_RFA' if e.get('src_kind') == 'rfa' else 'MassDOT_closure')
    quote = '; '.join(x for x in (e['orig_type'], e['desc'], e['cause'] and f"cause={e['cause']}",
                                  kind == 'waze' and f"thumbs={int(e['thumbs'])} reliability={'' if not np.isfinite(e['rel']) else int(e['rel'])}") if x)
    return dict(id=f'{pre}-{storm}-{k:03d}', name=name, road=road, town=e['town'], type=e['type'], time_local=local_str(e['t']), time_quality='exact',
                lon=f"{e['lon']:.6f}" if has else '', lat=f"{e['lat']:.6f}" if has else '', coord_quality='exact' if has else 'none',
                source_url=f"MassDOT District 3 data request (D. Henriques, GIS), file {e['src'] or '?'}", quote=quote[:300], source=src,
                tier=tier, tier_reason=why, n_reports=e['n_reports'], uuids=';'.join(sorted(e['uuids']))[:400], thumbs_up=int(e['thumbs']),
                reliability='' if not np.isfinite(e['rel']) else int(e['rel']), confidence='' if not np.isfinite(e['conf']) else int(e['conf']),
                end_local=local_str(e['te']), orig_type=e['orig_type'])


def write_csv(path, rows, cols):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', newline='') as fh:
        w = csv.DictWriter(fh, cols, extrasaction='ignore'); w.writeheader(); w.writerows(rows)


def ingest_events(ev, kind, data, side, docs, min_alerts, prefix=None, catalog=None):
    """Dedupe, tier, assign to storms, write label / negative-candidate / unmatched files.  -> report dict."""
    C = catalog if catalog is not None else catalogue(); prefix = prefix or ('waze' if kind == 'waze' else 'massdot_closure')
    kept, n_uuid = dedupe(ev)
    per = {}; neg = {}; unmatched = []; locked_n = 0; nocoord = []; tiers = {}
    for e in kept:
        S, timeonly = assign(e, C)
        if any(s['locked'] for s in S): locked_n += 1; continue          # write nothing for locked storms (PROTOCOL.md §2)
        if not S: unmatched.append(e); continue
        nc = negative_candidate(e) if kind == 'waze' else None
        for s in S:
            if nc: neg.setdefault(s['id'], []).append((e, nc)); continue
            per.setdefault(s['id'], []).append(e)
        if not np.isfinite(e['lon']): nocoord.append(e)
    written = {}
    for sid, L in sorted(per.items()):
        rows = [label_row(e, kind, sid, k + 1) for k, e in enumerate(L)]
        f = os.path.join(data, f'{prefix}_{sid}.csv'); write_csv(f, rows, LABEL_COLS); written[sid] = len(rows)
        for r in rows: tiers[r['tier']] = tiers.get(r['tier'], 0) + 1
    for sid, L in sorted(neg.items()):
        rows = [dict(label_row(e, kind, sid, k + 1), tier='negative_candidate', tier_reason=why) for k, (e, why) in enumerate(L)]
        write_csv(os.path.join(side, f'{prefix.split("_")[0]}_negcand_{sid}.csv'), rows, LABEL_COLS)
    # unmatched -> candidate new storms by local day
    import pandas as pd
    urows = [label_row(e, kind, 'unmatched', k + 1) for k, e in enumerate(unmatched)]
    write_csv(os.path.join(side, f'unmatched_{kind}.csv'), urows, LABEL_COLS)
    days = {}
    for e, r in zip(unmatched, urows):
        days.setdefault(r['time_local'][:10], []).append(e)
    cand = []
    for d, L in sorted(days.items()):
        if len(L) < min_alerts: continue
        xs = np.array([e['_x'] for e in L if np.isfinite(e['_x'])]); ys = np.array([e['_y'] for e in L if np.isfinite(e['_y'])])
        box = None
        if len(xs):
            cx, cy = np.median(xs), np.median(ys); x0 = math.floor(cx / 1000) * 1000 - 10000; y0 = math.floor(cy / 1000) * 1000 - 10000
            box = [x0, y0, x0 + 20000, y0 + 20000]
        towns = sorted({e['town'] for e in L if e['town']})
        cand.append(dict(date_local=d, n=len(L), n_in_box=int(sum(1 for x, y in zip(xs, ys) if box and box[0] <= x < box[2] and box[1] <= y < box[3])),
                         towns=towns[:12], suggested_box_26986=box, first_local=min(local_str(e['t']) for e in L), last_local=max(local_str(e['t']) for e in L)))
    os.makedirs(docs, exist_ok=True)
    json.dump(dict(made_by='proto/massdot_import.py ingest', kind=kind, min_alerts=min_alerts, candidates=cand), open(os.path.join(docs, f'candidate_storms_{kind}.json'), 'w'), indent=1)
    if nocoord:
        Q = [dict(key=f'{prefix}:{e["uuid"]}', town=e['town'], a=e['road'] or None, b=e['cross'] or None, near=None, addr=None) for e in nocoord if e['road'] and e['town']]
        json.dump(Q, open(os.path.join(side, f'geocode_queries_{kind}.json'), 'w'), indent=1)
    return dict(rows_flood=len(ev), unique_ids=n_uuid, after_dedupe=len(kept), written_per_storm=written, tiers=tiers,
                negative_candidates={k: len(v) for k, v in neg.items()}, locked_dropped=locked_n, unmatched=len(unmatched),
                candidate_storm_days=[(c['date_local'], c['n']) for c in cand], no_coords=len(nocoord))


# ------------------------------------------------------------------------------------------------ segments (District 3 graph)
_SEG = {}


def road_points(bbox=None, step=10.0):
    """Densified road points of docs/graph_segments.json (EPSG:26986): x, y, seg; restricted to bbox (x0, y0, x1, y1) when given."""
    key = (tuple(np.round(bbox, -2)) if bbox is not None else None, step)
    if key in _SEG: return _SEG[key]
    sys.path.insert(0, os.path.join(ROOT, 'sim', 'infra')); import impacts as IM
    S = json.load(open(os.path.join(ROOT, 'docs', 'graph_segments.json'))); parts = IM.decode_segments(S)
    if bbox is not None:
        from pyproj import Transformer
        inv = Transformer.from_crs(26986, 4326, always_xy=True); lo, la = inv.transform([bbox[0], bbox[2]], [bbox[1], bbox[3]]); m = 0.01
        parts = [p for p in parts if p[1].max() >= lo[0] - m and p[1].min() <= lo[1] + m and p[2].max() >= la[0] - m and p[2].min() <= la[1] + m]
    if not parts: _SEG[key] = (np.zeros(0), np.zeros(0), np.zeros(0, int), S); return _SEG[key]
    lon = np.concatenate([p[1] for p in parts]); lat = np.concatenate([p[2] for p in parts]); X, Y = xy26986(lon, lat); k = 0; pxy = []
    for s, a, _ in parts: pxy.append((s, X[k:k + len(a)], Y[k:k + len(a)])); k += len(a)
    x, y, sg = IM.densify(pxy, step); _SEG[key] = (x, y, sg.astype(int), S); return _SEG[key]


def struct_class(s):
    for name, rx in STRUCT_CLASSES:
        if rx.search(s or ''): return name
    return 'other'


def ingest_drains(df, cols, side, docs):
    from scipy.spatial import cKDTree
    lon, lat, _, crs_note = to_points(df, cols); ok = np.isfinite(lon)
    x, y = xy26986(lon[ok], lat[ok]); idx = np.nonzero(ok)[0]
    cls = np.array([struct_class(' '.join(str(col(df, cols, f, i)) for f in ('struct', 'subtype') if f in cols) + ' ' + str(df['_layer'].iloc[i] if '_layer' in df else ''))
                    for i in idx], dtype=object)
    ff = cols.get('flood_flag'); flood = np.array([bool(ff) and str(df[ff].iloc[i]).strip().lower() not in ('', '0', 'n', 'no', 'false', 'none', 'nan') for i in idx])
    rep = dict(rows=len(df), with_coords=int(ok.sum()), crs=crs_note, classes={c: int((cls == c).sum()) for c in ('inlet', 'culvert', 'manhole', 'outfall', 'other')},
               flagged_flooding=int(flood.sum()))
    if not len(x): rep['segments'] = 0; return rep
    PX, PY, PS, S = road_points([x.min() - 200, y.min() - 200, x.max() + 200, y.max() + 200])
    d, j = cKDTree(np.column_stack([PX, PY])).query(np.column_stack([x, y]), distance_upper_bound=INLET_M)
    hit = np.isfinite(d); seg = np.where(hit, PS[np.minimum(j, len(PS) - 1)], -1)
    T = {}
    for s, c, fl in zip(seg, cls, flood):
        if s < 0: continue
        r = T.setdefault(int(s), dict(n_inlets=0, n_culverts=0, n_manholes=0, n_outfalls=0, n_other=0, n_flood_known=0))
        r[{'inlet': 'n_inlets', 'culvert': 'n_culverts', 'manhole': 'n_manholes', 'outfall': 'n_outfalls'}.get(c, 'n_other')] += 1
        r['n_flood_known'] += int(fl)
    rows = []
    for s, r in sorted(T.items()):
        L = float(S['props']['len'][s]) if S['props'].get('len') else float('nan')
        rows.append(dict(segment=s, road=S['props']['road'][s], town=S['props']['town'][s], seg_len_m=round(L, 1), **r,
                         inlets_per_100m=round(100 * r['n_inlets'] / L, 3) if L and L > 0 else '', q_inlet_m3s=round(r['n_inlets'] * Q_SAG, 4),
                         n_in_pluvial=max(1, r['n_inlets'])))
    cols_out = ['segment', 'road', 'town', 'seg_len_m', 'n_inlets', 'n_culverts', 'n_manholes', 'n_outfalls', 'n_other', 'n_flood_known',
                'inlets_per_100m', 'q_inlet_m3s', 'n_in_pluvial']
    write_csv(os.path.join(side, 'inlets_segments.csv'), rows, cols_out)
    rep.update(segments=len(rows), structures_on_roads=int(hit.sum()), structures_off_roads=int((~hit).sum()),
               towns=sorted({r['town'] for r in rows})[:30])
    return rep


def ingest_rfa(df, cols, side, docs, data, min_alerts, catalog=None):
    from scipy.spatial import cKDTree
    import pandas as pd
    lon, lat, geom, crs_note = to_points(df, cols); ok = np.isfinite(lon); n = len(df)
    clo = cols.get('closure'); dcol = cols.get('dates') or cols.get('time'); ncol = cols.get('n_incidents')
    pts = []
    for i in range(n):
        txt = ' '.join(str(col(df, cols, f, i)) for f in ('desc', 'cause', 'type'))
        closure = (str(col(df, cols, 'closure', i)).strip().lower() in ('1', 'y', 'yes', 'true', 't', 'closed', 'full')) if clo else bool(CLOSE_TXT.search(txt))
        dv = df[dcol].iloc[i] if dcol else ''
        dates = sorted({str(pd.Timestamp(t).date()) for t in re.findall(r'\d{1,4}[/-]\d{1,2}[/-]\d{1,4}', str(dv)) if not pd.isna(pd.to_datetime(t, errors='coerce'))})
        pts.append(dict(rfa_id=str(col(df, cols, 'uuid', i) or i + 1), town=clean_town(col(df, cols, 'town', i)), road=str(col(df, cols, 'road', i)),
                        desc=str(col(df, cols, 'desc', i))[:200], closure=int(closure), lon=lon[i], lat=lat[i],
                        n_incidents=int(fnum(col(df, cols, 'n_incidents', i), 0)) if ncol else len(dates), dates=';'.join(dates)))
    write_csv(os.path.join(side, 'rfa_points.csv'), [dict(p, lon=f"{p['lon']:.6f}" if np.isfinite(p['lon']) else '', lat=f"{p['lat']:.6f}" if np.isfinite(p['lat']) else '') for p in pts],
              ['rfa_id', 'town', 'road', 'desc', 'closure', 'n_incidents', 'dates', 'lon', 'lat'])
    rep = dict(rows=n, with_coords=int(ok.sum()), crs=crs_note, closure_flagged=sum(p['closure'] for p in pts), with_dates=sum(1 for p in pts if p['dates']))
    # sample every RFA geometry (lines / polygons: points every 10 m along the boundary / line) for the distance field
    SX, SY, SI = [], [], []
    for i in np.nonzero(ok)[0]:
        g = geom.iloc[i] if geom is not None and geom.iloc[i] is not None and not geom.iloc[i].is_empty else None
        if g is not None and g.geom_type != 'Point':
            from shapely.ops import transform as stf
            from pyproj import Transformer
            tr = Transformer.from_crs(4326, 26986, always_xy=True); gp = stf(tr.transform, g)
            line = gp.boundary if gp.geom_type in ('Polygon', 'MultiPolygon') else gp
            L = max(line.length, 1.0); k = max(2, int(L / 10))
            for t in np.linspace(0, L, k): p = line.interpolate(t); SX.append(p.x); SY.append(p.y); SI.append(i)
            if gp.geom_type in ('Polygon', 'MultiPolygon'): c = gp.representative_point(); SX.append(c.x); SY.append(c.y); SI.append(i)
        else:
            x, y = xy26986([lon[i]], [lat[i]]); SX.append(x[0]); SY.append(y[0]); SI.append(i)
    if not SX: rep['segments'] = 0; return rep
    SX, SY, SI = np.array(SX), np.array(SY), np.array(SI)
    # one representative point per feature for counts
    FX = {}; [FX.setdefault(int(i), (x, y)) for x, y, i in zip(SX, SY, SI)]
    fi = np.array(sorted(FX)); fx = np.array([FX[i][0] for i in fi]); fy = np.array([FX[i][1] for i in fi])
    PX, PY, PS, S = road_points([SX.min() - RFA_TABLE_M, SY.min() - RFA_TABLE_M, SX.max() + RFA_TABLE_M, SY.max() + RFA_TABLE_M])
    d, _ = cKDTree(np.column_stack([SX, SY])).query(np.column_stack([PX, PY]), distance_upper_bound=RFA_TABLE_M)
    dseg = pd.Series(d).groupby(PS).min()
    near = dseg[dseg < RFA_TABLE_M]
    tf = cKDTree(np.column_stack([fx, fy])); tp = cKDTree(np.column_stack([PX, PY]))
    rows = []
    segpts = pd.Series(np.arange(len(PS))).groupby(PS).apply(list).to_dict()
    for s, dm in near.items():
        ii = segpts[s]; xy = np.column_stack([PX[ii], PY[ii]])
        f250 = sorted({int(fi[k]) for L in tf.query_ball_point(xy, 250.0) for k in L}); f1k = sorted({int(fi[k]) for L in tf.query_ball_point(xy, 1000.0) for k in L})
        rows.append(dict(segment=int(s), road=S['props']['road'][s], town=S['props']['town'][s], dist_rfa_m=round(float(dm), 1), n_rfa_250m=len(f250),
                         n_rfa_1km=len(f1k), rfa_closure=int(any(pts[k]['closure'] for k in f250)), rfa_dated_incidents=sum(pts[k]['n_incidents'] for k in f250)))
    write_csv(os.path.join(side, 'rfa_segments.csv'), rows, ['segment', 'road', 'town', 'dist_rfa_m', 'n_rfa_250m', 'n_rfa_1km', 'rfa_closure', 'rfa_dated_incidents'])
    # matched segments (30 m) for the validation check
    mseg = sorted({int(PS[j]) for L in tp.query_ball_point(np.column_stack([fx, fy]), 30.0) for j in L})
    rep.update(segments=len(rows), segments_within_30m=len(mseg), validation=rfa_validation(mseg, fx, fy))
    # known sites (massdot_repeat_flood_d3.csv) vs this layer
    kf = os.path.join(DATA, 'massdot_repeat_flood_d3.csv')
    if os.path.exists(kf):
        K = list(csv.DictReader(open(kf))); kx, ky = xy26986([float(r['lon']) for r in K], [float(r['lat']) for r in K])
        dk, _ = cKDTree(np.column_stack([kx, ky])).query(np.column_stack([fx, fy]))
        dn, _ = tf.query(np.column_stack([kx, ky]))
        rep['vs_known_d3_list'] = dict(known=len(K), layer_features=len(fi), layer_within_150m_of_known=int((dk <= 150).sum()),
                                       known_within_150m_of_layer=int((dn <= 150).sum()), new_in_layer=int((dk > 150).sum()))
    # dated incidents -> label rows (source MassDOT_RFA) through the closure pipeline
    ev = []
    for i, p in enumerate(pts):
        for ds in [x for x in p['dates'].split(';') if x]:
            t = pd.to_datetime(ds, errors='coerce')
            if pd.isna(t): continue
            t = (t + pd.Timedelta(hours=12)).tz_localize(TZ).tz_convert('UTC').tz_localize(None).to_datetime64().astype('datetime64[s]')
            ev.append(dict(t=t, te=np.datetime64('NaT'), lon=p['lon'], lat=p['lat'], uuid=f"RFA{p['rfa_id']}:{ds}", type='closed' if p['closure'] else 'flooded',
                           orig_type='Repeating Flood Area incident', road=p['road'], cross='', town=p['town'], desc=p['desc'], cause='flood (RFA layer)',
                           thumbs=0.0, not_there=0.0, rel=np.nan, conf=np.nan, src='RFA layer', src_kind='rfa'))
    if ev:
        rep['dated_incidents'] = ingest_events(ev, 'closures', data, side, docs, min_alerts, prefix='massdot_rfa', catalog=catalog)
        rep['dated_incidents']['note'] = 'date-only incidents are placed at local noon; the storm window decides the match'
    return rep


def rfa_validation(mseg, fx, fy):
    """Share of RFA-matched segments in each published primary run's top 3 % (p_close, then depth), and lift over 3 %."""
    sys.path.insert(0, HERE); import score_v2 as SV
    out = {}; ms = set(mseg)
    for p, s, grp, prim in SV.find_runs():
        if not prim or grp != 'parity': continue
        fe = os.path.join(p, f'features_{s}.csv')
        if not os.path.exists(fe): continue
        R = list(csv.DictReader(open(fe))); seg = np.array([int(r['segment']) for r in R])
        inr = np.isin(seg, list(ms))
        if not inr.any(): continue
        key = SV.rank_key([SV.F(r['p_close']) for r in R], [SV.F(r.get('peak_depth_m')) for r in R]); k = int(round(0.03 * len(R)))
        top = np.zeros(len(R), bool); top[np.argsort(-key, kind='stable')[:k]] = True
        sh = float((top & inr).sum() / inr.sum()); out[os.path.basename(p)] = dict(storm=s, rfa_segments=int(inr.sum()), in_top3=int((top & inr).sum()), share=round(sh, 3), lift=round(sh / 0.03, 2))
    if out:
        a = sum(v['in_top3'] for v in out.values()); b = sum(v['rfa_segments'] for v in out.values())
        out['_pooled'] = dict(rfa_segments=b, in_top3=a, share=round(a / b, 3), lift=round(a / b / 0.03, 2),
                              note='RFA segments are flood-prone in general, not storm-specific: a lift > 1 says the model ranks known problem spots high')
    return out


# ------------------------------------------------------------------------------------------------ commands
def load(paths, layer=None):
    import pandas as pd
    gpd = _gpd(); fr = []; notes = []
    for p in paths:
        d, note = read_any(p, layer)
        if '_src' not in d: d['_src'] = os.path.basename(p.rstrip('/')) if not p.startswith('http') else p
        fr.append(d); notes.append(f'{p}: {note}, {len(d)} rows')
    if len(fr) == 1: return fr[0], notes
    geo = [d for d in fr if isinstance(d, gpd.GeoDataFrame) and 'geometry' in d]
    if geo: fr = [d.to_crs(4326) if isinstance(d, gpd.GeoDataFrame) and d.crs is not None else d for d in fr]
    df = pd.concat([pd.DataFrame(d) for d in fr], ignore_index=True)
    return (gpd.GeoDataFrame(df, geometry='geometry', crs=4326) if geo else df), notes


def ingest(paths, kind, mapping=None, layer=None, tz=None, min_alerts=MIN_ALERTS, data=DATA, side=SIDE, docs=DOCS, catalog=None, quiet=False):
    df, notes = load(paths, layer); cols = detect_columns([c for c in df.columns if c != 'geometry'], mapping, kind)
    os.makedirs(side, exist_ok=True); os.makedirs(docs, exist_ok=True)
    rep = dict(kind=kind, inputs=notes, columns=cols, made=dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%dT%H:%MZ'))
    if kind in ('waze', 'closures'):
        ev, drop, crs = normalise(df, cols, kind, tz); rep.update(crs=crs, dropped=drop)
        rep.update(ingest_events(ev, kind, data, side, docs, min_alerts, catalog=catalog))
    elif kind == 'rfa': rep.update(ingest_rfa(df, cols, side, docs, data, min_alerts, catalog=catalog))
    elif kind == 'drains': rep.update(ingest_drains(df, cols, side, docs))
    stamp = rep['made'][:10]
    json.dump(rep, open(os.path.join(docs, f'ingest_{kind}.json'), 'w'), indent=1, default=str)
    md = [f'# MassDOT import: {kind} ({stamp})', '', 'Made by `python proto/massdot_import.py ingest ... --kind ' + kind + '`. Aggregates only.', '',
          '| item | value |', '|---|---|'] + [f'| {k} | {json.dumps(v, default=str)[:400]} |' for k, v in rep.items() if k not in ('made',)]
    open(os.path.join(docs, f'ingest_{kind}.md'), 'w').write('\n'.join(md) + '\n')
    if not quiet: print(json.dumps(rep, indent=1, default=str))
    return rep


def inspect(paths, mapping=None, layer=None, kind=None):
    df, notes = load(paths, layer); cols = detect_columns([c for c in df.columns if c != 'geometry'], mapping, kind)
    lon, lat, _, crs = to_points(df, cols)
    print('\n'.join(notes)); print('columns:', [c for c in df.columns]); print('detected:', json.dumps(cols, indent=1)); print('coordinates:', crs, f'{np.isfinite(lon).sum()}/{len(df)} rows in MA')
    if 'time' in cols:
        T = parse_times(df, cols); ok = ~np.isnat(T)
        if ok.any(): print('time range (local):', local_str(T[ok].min()), '->', local_str(T[ok].max()), f'({ok.sum()} rows)')
    print(df.drop(columns=[c for c in ('geometry',) if c in df]).head(3).to_string()[:2000])


# ---- score
def new_label_files(storm, sources, data=DATA):
    F = []
    if 'waze' in sources: F += sorted(glob.glob(os.path.join(data, f'waze_{storm}.csv')))
    if 'closures' in sources: F += sorted(glob.glob(os.path.join(data, f'massdot_closure_{storm}.csv')))
    if 'rfa' in sources: F += sorted(glob.glob(os.path.join(data, f'massdot_rfa_{storm}.csv')))
    return F


def install_hooks(sources=('waze', 'closures', 'rfa'), data=DATA, state=None):
    """Runtime hooks (no file edits): score_v2.label_files adds the new sources when state['on'] (or the env SCORE_WAZE / SCORE_MASSDOT
    are 1); label_tiers reads them as families 'Waze' / 'MassDOT_closure' / 'MassDOT_RFA' with the tier written in their 'tier' column."""
    sys.path.insert(0, HERE); import score_v2 as SV, label_tiers as LT
    st = state if state is not None else {'on': None}
    if getattr(SV.label_files, '_massdot', False): SV.label_files._state.update(st); return SV.label_files._state

    def on(src):
        if st['on'] is not None: return st['on']
        return os.environ.get('SCORE_WAZE' if src == 'waze' else 'SCORE_MASSDOT') == '1'

    def srcs(): return [s for s in sources if on(s)]
    o_lf, o_sf, o_fam, o_bt = SV.label_files, LT.source_files, LT.family, LT.base_tier

    def lf(storm): return o_lf(storm) + ([] if storm in LOCKED else new_label_files(storm, srcs(), data))
    def sf(storm): return o_sf(storm) + ([] if storm in LOCKED else new_label_files(storm, srcs(), data))

    def fam(r, fname):
        s = (r.get('source') or '')
        if fname.startswith('waze_') or s == 'Waze': return 'Waze'
        if fname.startswith('massdot_rfa_') or s == 'MassDOT_RFA': return 'MassDOT_RFA'
        if fname.startswith('massdot_closure_') or s == 'MassDOT_closure': return 'MassDOT_closure'
        return o_fam(r, fname)

    def bt(r, f):
        if f in ('Waze', 'MassDOT_closure', 'MassDOT_RFA') and r.get('tier') in LT.TIERS: return r['tier']
        return o_bt(r, f)
    lf._massdot = True; lf._state = st
    SV.label_files = lf; LT.source_files = sf; LT.family = fam; LT.base_tier = bt
    return st


def primary_runs():
    sys.path.insert(0, HERE); import score_v2 as SV
    best = {}
    for p, s, grp, prim in SV.find_runs():
        if prim and (s not in best or (grp == 'parity' and best[s][1] != 'parity')): best[s] = (p, grp)
    tdir = os.path.join(ROOT, 'docs', 'proto', 'transfer')
    for p in sorted(glob.glob(os.path.join(tdir, '*_*_20m'))):
        s = SV.storm_of(os.path.basename(p))
        if s and s not in best and os.path.exists(os.path.join(p, 'flood_meta.json')): best[s] = (p, 'transfer')
    return best


def score(sources=('waze', 'closures', 'rfa'), pool=False, out=None):
    sys.path.insert(0, HERE); import score_v2 as SV
    st = install_hooks(sources, state={'on': False})
    storms = sorted({re.match(r'(?:waze|massdot_closure|massdot_rfa)_(.+)\.csv$', os.path.basename(f)).group(1)
                     for p in ('waze_*.csv', 'massdot_closure_*.csv', 'massdot_rfa_*.csv') for f in glob.glob(os.path.join(DATA, p))} - set(LOCKED))
    storms = [s for s in storms if new_label_files(s, sources)]
    runs = primary_runs(); todo = [s for s in storms if s in runs]
    missing = [s for s in storms if s not in runs]
    if missing: print('no published run (label files kept, not scored):', ' '.join(missing))
    if pool: todo_pool = [s for s in SV.HELDOUT + SV.NEW16 if s in runs]
    else: todo_pool = []
    res = {}

    def blk(r):
        b = r['domains']['box']; t = b['shares']['0.03']
        return dict(sites=b['n_sites'], hits3=round(t['site_hits'], 2), rec3=t['site_recall'], rule_hits=round(b['rule']['site_hits'], 2),
                    labels_in_box=r['labels_in_box'], **({'wrec3': t.get('wsite_recall')} if SV.TIERED else {}))
    for s in sorted(set(todo) | set(todo_pool)):
        p, grp = runs[s]
        st['on'] = False; b = blk(SV.score_run(SV.load_run(p, s)))
        a = b
        if s in todo: st['on'] = True; a = blk(SV.score_run(SV.load_run(p, s))); st['on'] = False
        res[s] = dict(run=os.path.relpath(p, ROOT), group=grp, role='heldout' if s in SV.HELDOUT else 'new16' if s in SV.NEW16 else 'dev' if s in SV.DEV else 'd456' if s in SV.D456 else 'other',
                      new=s in todo, before=b, after=a)
        f = lambda v: '-' if v is None else f'{v:.2f}'
        print(f"{s:10s} {res[s]['role']:7s} sites {b['sites']:3d} -> {a['sites']:3d}  hits@3% {b['hits3']:5.1f} -> {a['hits3']:5.1f}  "
              f"recall@3% {f(b['rec3'])} -> {f(a['rec3'])}  rule hits {b['rule_hits']:.0f} -> {a['rule_hits']:.0f}"
              + (f"  weighted recall@3% {f(b.get('wrec3'))} -> {f(a.get('wrec3'))}" if SV.TIERED else ''), flush=True)
    pooled = {}
    for name, sel in ((('heldout23', SV.HELDOUT + SV.NEW16),) if pool else ()) + (('new_storms', tuple(todo)),):
        R = [res[s] for s in sel if s in res]
        if not R: continue
        hb = sum(r['before']['hits3'] for r in R); nb = sum(r['before']['sites'] for r in R); ha = sum(r['after']['hits3'] for r in R); na = sum(r['after']['sites'] for r in R)
        pooled[name] = dict(storms=len(R), before=[round(hb, 2), nb, round(hb / nb, 3) if nb else None], after=[round(ha, 2), na, round(ha / na, 3) if na else None])
        print(f"POOLED {name}: recall@3% {pooled[name]['before'][2]} ({hb:.1f}/{nb}) -> {pooled[name]['after'][2]} ({ha:.1f}/{na})  [{len(R)} storms]")
    rep = dict(made_by='proto/massdot_import.py score', sources=list(sources), tiered=SV.TIERED, storms=res, pooled=pooled,
               note='secondary analysis: new label sources added to the committed labels; the model is unchanged (PROTOCOL.md §1)')
    out = out or os.path.join(DOCS, 'score_massdot.json'); os.makedirs(os.path.dirname(out), exist_ok=True); json.dump(rep, open(out, 'w'), indent=1)
    print('wrote', os.path.relpath(out, ROOT)); return rep


# ------------------------------------------------------------------------------------------------ selftest (synthetic fixtures)
def _fixtures(d):
    """Realistic synthetic exports for every kind and format.  Points sit on real District 3 road segments inside catalogue storms."""
    import pandas as pd
    gpd = _gpd()
    from shapely.geometry import Point, LineString, Polygon
    C = {e['id']: e for e in json.load(open(CATALOGS[0]))['events']}
    PX, PY, PS, S = road_points(C['jul2023']['box_26986'])
    rng = np.random.default_rng(7); pick = rng.choice(len(PX), 12, replace=False)
    lo, la = __import__('pyproj').Transformer.from_crs(26986, 4326, always_xy=True).transform(PX[pick], PY[pick])
    t0 = pd.Timestamp(C['jul2023']['first_report_utc'].replace('Z', ''), tz='UTC'); ms = lambda t: int(t.value // 10 ** 6)
    W = []
    def alert(i, k, sub, typ, dtm, thumbs=0, rel=5, dx=0.0, uuid=None, street='Main St'):
        return dict(country='US', city='Worcester, MA', reportRating=2, reportByMunicipalityUser='false', confidence=min(10, thumbs), reliability=rel,
                    type=typ, uuid=uuid or f'a{i}-{k}', roadType=2, magvar=90, subtype=sub, street=street,
                    location={'x': float(lo[i]) + dx, 'y': float(la[i])}, pubMillis=ms(t0 + pd.Timedelta(minutes=dtm)), nThumbsUp=thumbs)
    W.append(alert(0, 0, 'HAZARD_WEATHER_FLOOD', 'WEATHERHAZARD', 0, thumbs=3))                    # corroborated by thumbs
    W.append(alert(0, 1, 'HAZARD_WEATHER_FLOOD', 'WEATHERHAZARD', 40, dx=0.0005))                   # 41 m away, 40 min later: merged
    W.append(alert(1, 0, 'HAZARD_WEATHER_FLOOD', 'WEATHERHAZARD', 10, rel=9))                       # corroborated by reliability
    W.append(alert(2, 0, 'HAZARD_WEATHER_FLOOD', 'WEATHERHAZARD', 20))                              # reported
    W.append(alert(3, 0, 'ROAD_CLOSED_HAZARD', 'ROAD_CLOSED', 30))                                  # closure (hazard)
    W.append(alert(4, 0, 'ROAD_CLOSED_CONSTRUCTION', 'ROAD_CLOSED', 30))                            # dropped (construction)
    W.append(alert(5, 0, 'HAZARD_ON_ROAD_POT_HOLE', 'WEATHERHAZARD', 30))                           # dropped (not flood)
    W.append(alert(6, 0, 'HAZARD_WEATHER_FLOOD', 'WEATHERHAZARD', 50, uuid='early'))                # removed early (two snapshots 5 min apart)
    # unmatched storm day: 6 flood alerts on a day with no catalogue storm (2024-06-15, Worcester)
    t1 = pd.Timestamp('2024-06-15T20:00', tz='UTC')
    for k in range(6):
        a = alert(7 + (k % 5), 0, 'HAZARD_WEATHER_FLOOD', 'WEATHERHAZARD', 0, uuid=f'u{k}', dx=0.01 * k); a['pubMillis'] = ms(t1 + pd.Timedelta(minutes=k)); W.append(a)
    # locked storm (aug2018, Worcester box): one alert that must not be written
    L = C['aug2018']; tl = pd.Timestamp(L['first_report_utc'].replace('Z', ''), tz='UTC'); bx = L['box_26986']
    llo, lla = __import__('pyproj').Transformer.from_crs(26986, 4326, always_xy=True).transform((bx[0] + bx[2]) / 2, (bx[1] + bx[3]) / 2)
    W.append(dict(alert(0, 9, 'HAZARD_WEATHER_FLOOD', 'WEATHERHAZARD', 0, uuid='locked1'), location={'x': llo, 'y': lla}, pubMillis=ms(tl)))
    snap1 = dict(startTimeMillis=ms(t0), endTimeMillis=ms(t0 + pd.Timedelta(minutes=55)), alerts=W)
    snap2 = dict(startTimeMillis=ms(t0 + pd.Timedelta(minutes=55)), endTimeMillis=ms(t0 + pd.Timedelta(minutes=95)),
                 alerts=[a for a in W if a['uuid'] not in ('early',)])
    snap1b = dict(snap1, endTimeMillis=ms(t0 + pd.Timedelta(minutes=50)), alerts=[a for a in W if a['uuid'] in ('early', 'a1-0')])   # a1-0 seen in both snapshots
    os.makedirs(os.path.join(d, 'waze_feed'), exist_ok=True)
    json.dump(snap1b, open(os.path.join(d, 'waze_feed', 'feed_0.json'), 'w')); json.dump(snap2, open(os.path.join(d, 'waze_feed', 'feed_1.json'), 'w'))
    flat = [dict({k: v for k, v in a.items() if k != 'location'}, location=json.dumps(a['location'])) for a in W]
    wdf = pd.DataFrame(flat)
    wg = gpd.GeoDataFrame(wdf.drop(columns=['location']), geometry=[Point(a['location']['x'], a['location']['y']) for a in W], crs=4326)
    # closures (HOC log style): local times, MA State Plane feet coordinates in a GDB / shapefile, lat/lon in CSV
    from pyproj import Transformer
    tf = Transformer.from_crs(4326, 2249, always_xy=True)
    tl0 = t0.tz_convert(TZ).tz_localize(None)
    CL = [dict(INCIDENT_ID='HOC-1', EVENT_TYPE='Road Closure', CAUSE='Flooding', ROUTE='Main St', TOWN='WORCESTER', START_TIME=str(tl0), END_TIME=str(tl0 + pd.Timedelta(hours=3)),
               DESCRIPTION='All lanes closed due to flooding', lon=float(lo[8]), lat=float(la[8])),
          dict(INCIDENT_ID='HOC-2', EVENT_TYPE='Incident', CAUSE='Weather', ROUTE='I-290 EB', TOWN='WORCESTER', START_TIME=str(tl0 + pd.Timedelta(minutes=30)), END_TIME='',
               DESCRIPTION='Vehicle stuck in standing water, travel lane impassable', lon=float(lo[9]), lat=float(la[9])),
          dict(INCIDENT_ID='HOC-3', EVENT_TYPE='Incident', CAUSE='Weather', ROUTE='Rte 146', TOWN='MILLBURY', START_TIME=str(tl0 + pd.Timedelta(minutes=40)), END_TIME='',
               DESCRIPTION='Ponding in right lane', lon=float(lo[10]), lat=float(la[10])),
          dict(INCIDENT_ID='HOC-4', EVENT_TYPE='Crash', CAUSE='Collision', ROUTE='Rte 9', TOWN='WORCESTER', START_TIME=str(tl0), END_TIME='',
               DESCRIPTION='Two-car crash', lon=float(lo[11]), lat=float(la[11])),
          dict(INCIDENT_ID='HOC-5', EVENT_TYPE='Road Closure', CAUSE='Flooding', ROUTE='Grove St', TOWN='WORCESTER', START_TIME=str(tl0 + pd.Timedelta(minutes=60)), END_TIME='',
               DESCRIPTION='Road closed, flooding', lon=None, lat=None)]
    cdf = pd.DataFrame(CL)
    ok = cdf['lon'].notna(); xs, ys = tf.transform(cdf.loc[ok, 'lon'].astype(float).values, cdf.loc[ok, 'lat'].astype(float).values)
    cg = gpd.GeoDataFrame(cdf.drop(columns=['lon', 'lat']), geometry=[Point(x, y) for x, y in zip(xs, ys)] + [None] * int((~ok).sum()), crs=2249)
    # RFA: points + a line + a polygon in 26986, with incident dates; the first site sits in jul2023's window
    rx, ry = PX[pick[:3]], PY[pick[:3]]
    rg = gpd.GeoDataFrame(dict(RFA_ID=['R1', 'R2', 'R3'], TOWN=['Worcester'] * 3, ROUTE=['Main St', 'Rte 12', 'Rte 9'],
                               LOCATION=['by the plaza', 'under the rail bridge', 'low point'], CLOSURE=[1, 0, 0],
                               INCIDENT_DATES=[C['jul2023']['date_local'] + '; 2019-07-01', '', '2022-01-02']),
                          geometry=[Point(rx[0], ry[0]), LineString([(rx[1] - 30, ry[1]), (rx[1] + 30, ry[1])]),
                                    Polygon([(rx[2] - 20, ry[2] - 20), (rx[2] + 20, ry[2] - 20), (rx[2] + 20, ry[2] + 20), (rx[2] - 20, ry[2] + 20)])], crs=26986)
    # drains: catch basins / culvert / manhole near road points, one 200 m off the road
    dx_, dy_ = PX[pick[3:8]] + 3, PY[pick[3:8]] - 3
    dg = gpd.GeoDataFrame(dict(STRUCT_TYPE=['Catch Basin', 'CB', 'Drop Inlet', 'Culvert', 'Drain Manhole'], FLOODING=['Y', '', '', '', ''], OWNER=['MassDOT'] * 5),
                          geometry=[Point(x, y) for x, y in zip(dx_, dy_)], crs=26986)
    from scipy.spatial import cKDTree
    gx, gy = np.meshgrid(np.arange(C['jul2023']['box_26986'][0], C['jul2023']['box_26986'][2], 50.0), np.arange(C['jul2023']['box_26986'][1], C['jul2023']['box_26986'][3], 50.0))
    gd, _ = cKDTree(np.column_stack([PX, PY])).query(np.column_stack([gx.ravel(), gy.ravel()])); far = int(np.argmax(gd))   # farthest from any road
    dg = pd.concat([dg, gpd.GeoDataFrame(dict(STRUCT_TYPE=['Catch Basin'], FLOODING=[''], OWNER=['town']), geometry=[Point(gx.ravel()[far], gy.ravel()[far])], crs=26986)], ignore_index=True)
    F = {}
    for kind, g in (('waze', wg), ('closures', cg), ('rfa', rg), ('drains', dg)):
        base = os.path.join(d, kind); os.makedirs(base, exist_ok=True)
        gg = g.copy()
        if kind == 'rfa': gg = gg.set_geometry(gg.geometry.representative_point())     # shapefile / GDB layers hold one geometry type
        # shapefile (field names truncated to 10 chars by the driver), GDB, GeoJSON, CSV with lon/lat or x/y, XLSX
        F[(kind, 'shp')] = os.path.join(base, f'{kind}.shp'); gg.to_file(F[(kind, 'shp')])
        F[(kind, 'gdb')] = os.path.join(base, f'{kind}.gdb'); gg.to_file(F[(kind, 'gdb')], driver='OpenFileGDB', layer=f'{kind}_layer')
        F[(kind, 'geojson')] = os.path.join(base, f'{kind}.geojson'); g.to_crs(4326).to_file(F[(kind, 'geojson')], driver='GeoJSON')   # mixed types
        tab = pd.DataFrame(gg.drop(columns='geometry'))
        rp = gg.to_crs(4326).geometry.representative_point() if gg.geometry.notna().all() else None
        if kind == 'waze': tab = wdf.copy()                                              # official Waze field names, location as {"x","y"}
        elif rp is not None: tab['LONGITUDE'] = rp.x.values; tab['LATITUDE'] = rp.y.values
        else:
            xx = [p.x if p is not None else None for p in gg.geometry]; yy = [p.y if p is not None else None for p in gg.geometry]
            tab['X_COORD'] = xx; tab['Y_COORD'] = yy                                     # state plane feet, CRS guessed
        F[(kind, 'csv')] = os.path.join(base, f'{kind}.csv'); tab.to_csv(F[(kind, 'csv')], index=False)
        F[(kind, 'xlsx')] = os.path.join(base, f'{kind}.xlsx'); tab.to_excel(F[(kind, 'xlsx')], index=False)
        F[(kind, 'rest')] = gg.to_crs(4326)
    F[('waze', 'feed')] = os.path.join(d, 'waze_feed')
    return F


class _RestServer:
    """Minimal ArcGIS REST FeatureServer layer on localhost: ?f=json info, /query with resultOffset paging, f=geojson and f=json."""
    def __init__(self, layers, page=3, geojson=True):
        import http.server, threading
        from urllib.parse import urlparse, parse_qs
        L = layers; srv = self

        class H(http.server.BaseHTTPRequestHandler):
            def log_message(self, *a): pass

            def do_GET(self):
                u = urlparse(self.path); q = {k: v[0] for k, v in parse_qs(u.query).items()}; parts = u.path.strip('/').split('/')
                if parts[-1] == 'FeatureServer': J = dict(layers=[dict(id=i, name=k) for i, k in enumerate(L)])
                else:
                    li = int(parts[-1] if parts[-1] != 'query' else parts[-2]); g = list(L.values())[li]
                    if parts[-1] != 'query': J = dict(maxRecordCount=page, advancedQueryCapabilities=dict(supportsPagination=True))
                    else:
                        o = int(q.get('resultOffset', 0)); n = int(q.get('resultRecordCount', page)); sub = g.iloc[o:o + n]
                        fc = json.loads(sub.to_json(na='null'))
                        if q.get('f') == 'geojson' and srv.geojson: J = dict(fc, exceededTransferLimit=o + n < len(g))
                        elif q.get('f') == 'geojson': J = dict(error=dict(code=400, message='geojson not supported'))
                        else:
                            def eg(G):
                                if G is None: return None
                                if G['type'] == 'Point': return dict(x=G['coordinates'][0], y=G['coordinates'][1])
                                if G['type'] == 'LineString': return dict(paths=[G['coordinates']])
                                if G['type'] == 'Polygon': return dict(rings=G['coordinates'])
                            J = dict(features=[dict(attributes=f['properties'], geometry=eg(f['geometry'])) for f in fc['features']], exceededTransferLimit=o + n < len(g))
                b = json.dumps(J).encode(); self.send_response(200); self.send_header('Content-Type', 'application/json'); self.end_headers(); self.wfile.write(b)
        self.geojson = geojson
        self.httpd = http.server.ThreadingHTTPServer(('127.0.0.1', 0), H); self.port = self.httpd.server_address[1]
        threading.Thread(target=self.httpd.serve_forever, daemon=True).start()

    def url(self, i=None): return f'http://127.0.0.1:{self.port}/arcgis/rest/services/D3/FeatureServer' + ('' if i is None else f'/{i}')

    def close(self): self.httpd.shutdown()


def selftest(full=False):
    import pandas as pd
    import warnings
    warnings.filterwarnings('ignore')
    ok = True

    def chk(name, c, info=''):
        nonlocal ok; ok &= bool(c); print(('PASS ' if c else 'FAIL ') + name + (f'  [{info}]' if info and not c else ''), flush=True)
    d = tempfile.mkdtemp(prefix='massdot_selftest_'); F = _fixtures(d)
    # 1. mapping table
    m = detect_columns(['country', 'city', 'reliabilit', 'type', 'uuid', 'subtype', 'street', 'pubMillis', 'nThumbsUp', 'confidence'])
    chk('mapping: waze schema + shapefile truncation', m.get('time') == 'pubMillis' and m.get('reliability') == 'reliabilit' and m.get('thumbs') == 'nThumbsUp' and m.get('town') == 'city', m)
    chk('mapping: --map override', detect_columns(['Event Start', 'X'], parse_map(['time=Event Start']))['time'] == 'Event Start')
    chk('crs guess', guess_crs([-71.8], [42.2]) == 4326 and guess_crs([150000], [890000]) == 26986 and guess_crs([500000], [2900000]) == 2249 and guess_crs([-7990000], [5190000]) == 3857)
    # 2. every reader x every kind: rows and coordinates survive
    srv = _RestServer({k: F[(k, 'rest')] for k in KINDS}); srv2 = _RestServer({k: F[(k, 'rest')] for k in KINDS}, geojson=False)
    for kind in KINDS:
        n0 = len(F[(kind, 'rest')])
        for fmt in ('shp', 'gdb', 'geojson', 'csv', 'xlsx', 'rest', 'rest-esrijson'):
            p = F[(kind, fmt)] if fmt not in ('rest', 'rest-esrijson') else (srv if fmt == 'rest' else srv2).url(KINDS.index(kind))
            df, _ = load([p]); cols = detect_columns([c for c in df.columns if c != 'geometry'], None, kind); lon, lat, _, note = to_points(df, cols)
            nn = int(np.isfinite(lon).sum()); exp = n0 - (1 if kind == 'closures' else 0)
            chk(f'read {kind:8s} {fmt:13s} rows {len(df)}/{n0} coords {nn}/{exp}', len(df) == n0 and nn == exp, note)
    df, _ = load([srv.url()]); chk('read REST service root (all layers)', len(df) == sum(len(F[(k, 'rest')]) for k in KINDS))
    srv.close(); srv2.close()
    # 3. Waze pipeline (official feed snapshots: last-seen times) into a temp tree
    out = os.path.join(d, 'out'); data, side, docs = os.path.join(out, 'data'), os.path.join(out, 'side'), os.path.join(out, 'docs')
    R = ingest([F[('waze', 'feed')]], 'waze', data=data, side=side, docs=docs, quiet=True)
    W = list(csv.DictReader(open(os.path.join(data, 'waze_jul2023.csv')))) if os.path.exists(os.path.join(data, 'waze_jul2023.csv')) else []
    chk('waze: construction / pothole dropped', R['dropped']['construction_or_event'] == 1 and R['dropped']['no_flood'] == 1, R['dropped'])
    chk('waze: dedupe uuid + 150 m / 2 h', R['unique_ids'] == R['rows_flood'] - 1 and R['after_dedupe'] == R['unique_ids'] - 1, (R['unique_ids'], R['after_dedupe']))
    chk('waze: jul2023 rows', len(W) == 4, len(W))
    tiers = {r['uuids']: r['tier'] for r in W}
    chk('waze: tiers (thumbs / reliability / 2 uuids -> corroborated; single -> reported)',
        tiers.get('a0-0;a0-1') == 'corroborated' and tiers.get('a1-0') == 'corroborated' and tiers.get('a2-0') == 'reported', tiers)
    chk('waze: closure type', any(r['type'] == 'closed' and r['uuids'] == 'a3-0' for r in W))
    neg = os.path.join(side, 'waze_negcand_jul2023.csv')
    chk('waze: removed-early alert -> candidate negative, not a label', os.path.exists(neg) and 'early' in open(neg).read() and not any(r['uuids'] == 'early' for r in W))
    chk('waze: locked storm written nowhere', R['locked_dropped'] == 1 and not glob.glob(os.path.join(data, '*aug2018.csv')) and 'locked1' not in ''.join(open(f).read() for f in glob.glob(os.path.join(out, '*', '*.csv'))))
    cs = json.load(open(os.path.join(docs, 'candidate_storms_waze.json')))['candidates']
    chk('waze: unmatched storm day listed', [c['date_local'] for c in cs] == ['2024-06-15'] and cs[0]['n'] == 6 and cs[0]['suggested_box_26986'], cs)
    chk('waze: label schema', list(W[0].keys())[:13] == ['id', 'name', 'road', 'town', 'type', 'time_local', 'time_quality', 'lon', 'lat', 'coord_quality', 'source_url', 'quote', 'source'])
    # same through the flat CSV (official field names; no snapshots -> no removed-early) and the shapefile
    for fmt in ('csv', 'shp', 'xlsx'):
        R2 = ingest([F[('waze', fmt)]], 'waze', data=os.path.join(out, fmt), side=os.path.join(out, fmt + 's'), docs=os.path.join(out, fmt + 'd'), quiet=True)
        chk(f'waze via {fmt}: jul2023 rows', R2['written_per_storm'].get('jul2023') == 5, R2['written_per_storm'])
    # 4. closures (GDB in MA State Plane feet; one row without coordinates; one crash dropped)
    R = ingest([F[('closures', 'gdb')]], 'closures', data=data, side=side, docs=docs, quiet=True)
    Cl = list(csv.DictReader(open(os.path.join(data, 'massdot_closure_jul2023.csv'))))
    t = {r['uuids']: r['tier'] for r in Cl}
    chk('closures: tiers', t.get('HOC-1') == 'confirmed_closure' and t.get('HOC-2') == 'confirmed_inundation' and t.get('HOC-3') == 'reported' and 'HOC-4' not in t, t)
    chk('closures: no-coordinate row kept, geocode query written', t.get('HOC-5') == 'confirmed_closure' and os.path.exists(os.path.join(side, 'geocode_queries_closures.json')))
    exp_t = pd.Timestamp(json.load(open(CATALOGS[0]))['events'][4]['first_report_utc'].replace('Z', ''), tz='UTC').tz_convert(TZ).strftime('%Y-%m-%dT%H:%M')
    chk('closures: local text times stay local', Cl[0]['time_local'] == exp_t, (Cl[0]['time_local'], exp_t))
    chk('waze: epoch ms -> local', W[0]['time_local'] == exp_t, (W[0]['time_local'], exp_t))
    R = ingest([F[('closures', 'csv')]], 'closures', data=os.path.join(out, 'cc'), side=os.path.join(out, 'ccs'), docs=os.path.join(out, 'ccd'), quiet=True)
    chk('closures via csv', R['written_per_storm'].get('jul2023') == 4, R['written_per_storm'])
    # 5. RFA (points + line + polygon, 26986) -> segment table, dated incident -> label, validation check
    R = ingest([F[('rfa', 'geojson')]], 'rfa', data=data, side=side, docs=docs, quiet=True)
    T = list(csv.DictReader(open(os.path.join(side, 'rfa_segments.csv'))))
    chk('rfa: segment table', R['segments'] > 50 and min(float(r['dist_rfa_m']) for r in T) < 5 and R['segments_within_30m'] >= 3, (R['segments'], R.get('segments_within_30m')))
    chk('rfa: dated incident in jul2023 -> massdot_rfa row (MassDOT_RFA)', any(r['source'] == 'MassDOT_RFA' for r in csv.DictReader(open(os.path.join(data, 'massdot_rfa_jul2023.csv')))))
    chk('rfa: closure file not overwritten', len(list(csv.DictReader(open(os.path.join(data, 'massdot_closure_jul2023.csv'))))) == 4)
    R2 = ingest([F[('rfa', 'shp')]], 'rfa', data=os.path.join(out, 'rs'), side=os.path.join(out, 'rss'), docs=os.path.join(out, 'rsd'), quiet=True)
    chk('rfa via shapefile (truncated field names): dated incident', os.path.exists(os.path.join(out, 'rs', 'massdot_rfa_jul2023.csv')) and R2['with_dates'] == 2, R2.get('with_dates'))
    chk('rfa: validation check ran', isinstance(R.get('validation'), dict) and 'vs_known_d3_list' in R, list(R.keys()))
    # 6. drains -> per-segment inlet table
    R = ingest([F[('drains', 'gdb')]], 'drains', data=data, side=side, docs=docs, quiet=True)
    D = list(csv.DictReader(open(os.path.join(side, 'inlets_segments.csv'))))
    chk('drains: classes', R['classes'] == dict(inlet=4, culvert=1, manhole=1, outfall=0, other=0), R['classes'])
    chk('drains: on-road vs off-road', R['structures_on_roads'] == 5 and R['structures_off_roads'] == 1, (R.get('structures_on_roads'), R.get('structures_off_roads')))
    chk('drains: inlet capacity column', sum(int(r['n_inlets']) for r in D) == 3 and abs(sum(float(r['q_inlet_m3s']) for r in D) - 3 * Q_SAG) < 1e-3 and sum(int(r['n_flood_known']) for r in D) == 1, D)
    # 7. score hooks: label_files / label_tiers see the new sources only when switched on; locked storms never
    sys.path.insert(0, HERE); import score_v2 as SV, label_tiers as LT
    st = install_hooks(data=data, state={'on': False})
    b = SV.label_files('jul2023'); st['on'] = True; a = SV.label_files('jul2023')
    chk('score hook: off = committed labels, on = + waze + closures', [os.path.basename(f) for f in a if f not in b] == ['waze_jul2023.csv', 'massdot_closure_jul2023.csv', 'massdot_rfa_jul2023.csv'], a)
    chk('score hook: locked storm untouched', SV.label_files('aug2018') == [] or all(os.path.basename(f).startswith('labels_') for f in SV.label_files('aug2018')))
    TR = [r for r in LT.tier_rows('jul2023') if r['source_family'] in ('Waze', 'MassDOT_closure', 'MassDOT_RFA')]
    chk('score hook: label_tiers families and tiers', {r['source_family'] for r in TR} == {'Waze', 'MassDOT_closure', 'MassDOT_RFA'} and
        any(r['tier'] == 'confirmed_closure' for r in TR) and any(r['tier'] == 'corroborated' for r in TR), sorted({(r['source_family'], r['tier']) for r in TR}))
    if full:
        p, _ = primary_runs()['jul2023']; st['on'] = False; rb = SV.score_run(SV.load_run(p, 'jul2023')); st['on'] = True; ra = SV.score_run(SV.load_run(p, 'jul2023'))
        chk('score: real run, more labels in box after', ra['labels_in_box'] > rb['labels_in_box'], (rb['labels_in_box'], ra['labels_in_box']))
    st['on'] = False
    import shutil; shutil.rmtree(d, ignore_errors=True)
    return ok


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    sp = ap.add_subparsers(dest='cmd', required=True)
    a = sp.add_parser('ingest'); a.add_argument('paths', nargs='+'); a.add_argument('--kind', required=True, choices=KINDS)
    a.add_argument('--map', action='append', help='field=Column override, e.g. --map time="Event Start",lon=X'); a.add_argument('--layer')
    a.add_argument('--tz', help='timezone of naive text times (default America/New_York; UTC for *utc* columns)')
    a.add_argument('--min-alerts', type=int, default=MIN_ALERTS, help='unmatched local day with >= N rows -> candidate new storm')
    i = sp.add_parser('inspect'); i.add_argument('paths', nargs='+'); i.add_argument('--map', action='append'); i.add_argument('--layer'); i.add_argument('--kind', choices=KINDS)
    s = sp.add_parser('score'); s.add_argument('--sources', default='waze,closures,rfa'); s.add_argument('--pool', action='store_true'); s.add_argument('--out')
    t = sp.add_parser('selftest'); t.add_argument('--full', action='store_true', help='also score one real published run (~25 s)')
    A = ap.parse_args()
    if A.cmd == 'ingest': ingest(A.paths, A.kind, parse_map(A.map), A.layer, A.tz, A.min_alerts)
    elif A.cmd == 'inspect': inspect(A.paths, parse_map(A.map), A.layer, A.kind)
    elif A.cmd == 'score': score(tuple(x.strip() for x in A.sources.split(',')), A.pool, A.out)
    else: sys.exit(0 if selftest(A.full) else 1)


if __name__ == '__main__':
    main()
