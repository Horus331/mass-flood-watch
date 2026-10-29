"""Static flood-hazard maps vs the event model (pre-registration and results: docs/proto/static/STATIC.md).

Question: does a static flood map (FEMA 100-yr zones, a consultant's 100-yr model) already tell you which roads close?

    python proto/static_maps.py fetch --out flags.json          # GitHub Actions only (static_maps.yml): FEMA NFHL + BSC/MRPC Leominster
                                                                 #   polygons -> per-segment share of length inside each zone
    python proto/static_maps.py emit flags.json --part 0         # print the gzip+base64 payload as ::notice annotations (10 per part)
    python proto/static_maps.py checkruns flags.json             # same payload as neutral check runs (fallback channel; needs GITHUB_TOKEN)
    python proto/static_maps.py decode --run RUN_ID --out docs/proto/static/static_flags.json   # rebuild flags from a run's annotations
    python proto/static_maps.py score --flags docs/proto/static/static_flags.json --out docs/proto/static/results.json --md docs/proto/static/results.md
    python proto/static_maps.py selftest

Segment flags (fixed in STATIC.md before any result): a segment of docs/graph_segments.json is 'flagged' by a map when any length of it lies
inside the map's zone ('any'), or, stricter, when >= 30 % of its length does ('30').  Lengths are exact line / polygon intersections in
EPSG:26986 on the whole segment (all parts, not clipped to a run box).  Scoring reuses proto/score_v2.py on the clean CPU parity runs
(docs/proto/parity/catalog/<storm>_<area>_20m): same universe, matches, sites, chance and bootstrap; nothing in the run folders changes.
"""
import argparse
import base64
import copy
import gzip
import hashlib
import json
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(ROOT, 'sim', 'infra'))

FEMA_SERVERS = ('https://hazards.fema.gov/arcgis/rest/services/public/NFHL/MapServer',
                'https://hazards.fema.gov/gis/nfhl/rest/services/public/NFHL/MapServer')
FEMA_LAYER_NAME = 'flood hazard zones'; FEMA_LAYER_DEFAULT = 28
LEO_ORG = 'https://services7.arcgis.com/vZE8iWev3YlXRRXa/arcgis/rest/services'
LEO_DEFAULT = LEO_ORG + '/LeominsterFlooding_CurrentTimeHorizon/FeatureServer'
TILE_M = 8000.0; MIN_TILE_M = 250.0; MARGIN_M = 500.0
STRICT = 30.0                                        # stricter flag: >= 30 % of the segment's length inside the zone
CHUNK = 4000                                         # characters per annotation
BOOT = 2000


# ------------------------------------------------------------------------------------------------ road segments (EPSG:26986 lines)
def segment_lines():
    """-> list of shapely (Multi)LineStrings, one per graph segment, in EPSG:26986, and the town list."""
    import shapely
    from pyproj import Transformer
    from impacts import decode_segments
    S = json.load(open(os.path.join(ROOT, 'docs', 'graph_segments.json'))); tr = Transformer.from_crs(4326, 26986, always_xy=True)
    parts = {}
    for s, lon, lat in decode_segments(S):
        x, y = tr.transform(lon, lat)
        if len(x) >= 2: parts.setdefault(s, []).append(np.column_stack([x, y]))
    lines = []
    for s in range(S['n']):
        P = parts.get(s, [])
        lines.append(shapely.MultiLineString([shapely.LineString(p) for p in P]) if len(P) > 1 else shapely.LineString(P[0]) if P else None)
    return lines, S['props']['town']


# ------------------------------------------------------------------------------------------------ ArcGIS REST fetch (Actions only)
def _get(url, params=None, tries=6, timeout=180):
    import requests
    last = None
    for i in range(tries):
        try:
            r = requests.get(url, params=params, timeout=timeout, headers={'User-Agent': 'mass-flood-watch research (static_maps.py)'})
            if r.status_code == 200:
                j = r.json()
                if isinstance(j, dict) and 'error' in j and j['error'].get('code') in (500, 503, 504, 429): last = j['error']; raise RuntimeError(j['error'])
                return j
            last = f'HTTP {r.status_code}'
        except Exception as e:
            last = e
        time.sleep(min(60, 3 * 2 ** i))
    raise RuntimeError(f'{url}: {last}')


def esri_polygon(rings):
    """Esri JSON rings -> valid shapely geometry.  Exterior rings are clockwise, holes counter-clockwise; each hole goes to the exterior that
    contains it."""
    import shapely
    from shapely.geometry import LinearRing, Polygon
    ext, holes = [], []
    for r in rings or []:
        if len(r) < 4: continue
        lr = LinearRing([(p[0], p[1]) for p in r])
        (holes if lr.is_ccw else ext).append(lr)
    if not ext and holes: ext, holes = holes, []            # all rings one orientation: treat as exteriors
    polys = [[e, []] for e in ext]
    for h in holes:
        pt = shapely.Point(h.coords[0]); host = [p for p in polys if Polygon(p[0]).contains(pt)]
        (min(host, key=lambda p: Polygon(p[0]).area)[1] if host else polys[0][1] if polys else []).append(h)
    geoms = [shapely.make_valid(Polygon(e, hs)) for e, hs in polys]
    geoms = [g for g in geoms if not g.is_empty]
    return shapely.union_all(geoms) if geoms else None


def query_tiles(layer_url, bbox, where='1=1', out_fields='*', log=print, workers=6):
    """All features of an ArcGIS layer intersecting bbox (EPSG:26986), by envelope tiles split in four while the server truncates
    (exceededTransferLimit), then paged at the smallest tile.  Deduplicated by object id.  -> (features, stats)."""
    from concurrent.futures import ThreadPoolExecutor
    x0, y0, x1, y1 = bbox; tiles = []
    for x in np.arange(x0, x1, TILE_M):
        for y in np.arange(y0, y1, TILE_M): tiles.append((x, y, min(x + TILE_M, x1), min(y + TILE_M, y1)))
    feats = {}; stats = dict(requests=0, splits=0, paged=0, tiles=len(tiles)); oid_name = [None]

    def q(t, offset=None):
        p = dict(where=where, geometry=','.join(f'{v:.1f}' for v in t), geometryType='esriGeometryEnvelope', inSR=26986,
                 spatialRel='esriSpatialRelIntersects', outFields=out_fields, returnGeometry='true', outSR=26986, f='json',
                 maxAllowableOffset=1, geometryPrecision=1)
        if offset is not None: p.update(resultOffset=offset, resultRecordCount=1000)
        stats['requests'] += 1; return _get(layer_url + '/query', p)

    def run(t):
        out = []; stack = [t]
        while stack:
            t = stack.pop()
            try: j = q(t)
            except RuntimeError:
                if t[2] - t[0] > MIN_TILE_M: j = dict(exceededTransferLimit=True, features=[])     # server choked on a big tile: split
                else: raise
            if 'error' in j: raise RuntimeError(f"{layer_url}: {j['error']}")
            if j.get('exceededTransferLimit'):
                if t[2] - t[0] > MIN_TILE_M:
                    stats['splits'] += 1; xm, ym = (t[0] + t[2]) / 2, (t[1] + t[3]) / 2
                    stack += [(t[0], t[1], xm, ym), (xm, t[1], t[2], ym), (t[0], ym, xm, t[3]), (xm, ym, t[2], t[3])]; continue
                off = 0; fs = []
                while True:
                    jj = q(t, off); fs += jj.get('features', []); stats['paged'] += 1
                    if not jj.get('exceededTransferLimit') or not jj.get('features'): break
                    off += len(jj['features'])
                j = dict(j, features=fs)
            oid_name[0] = oid_name[0] or j.get('objectIdFieldName'); out += j.get('features', [])
        return out

    done = 0
    with ThreadPoolExecutor(workers) as ex:
        for fs in ex.map(run, tiles):
            done += 1
            for f in fs:
                a = f.get('attributes', {}); k = a.get(oid_name[0]) if oid_name[0] else None
                if k is None: k = a.get('OBJECTID', a.get('objectid', a.get('FID')))
                if k is None: k = hashlib.md5(json.dumps(f, sort_keys=True).encode()).hexdigest()
                feats[k] = f
            if done % 25 == 0: log(f'  {done}/{len(tiles)} tiles, {len(feats)} features, {stats["requests"]} requests')
    stats['features'] = len(feats); return list(feats.values()), stats


def attr(a, name):
    for k, v in a.items():
        if k.lower() == name.lower(): return v
    return None


def fema_class(a):
    """'sfha' (1 % annual chance: SFHA_TF = T, zones A*, V*), 'x02' (0.2 % / shaded X incl. levee-reduced-risk areas), else None."""
    z = str(attr(a, 'FLD_ZONE') or '').strip().upper(); sub = str(attr(a, 'ZONE_SUBTY') or '').strip().upper(); sf = str(attr(a, 'SFHA_TF') or '').strip().upper()
    if sf == 'T' or (z[:1] in ('A', 'V') and z not in ('AREA NOT INCLUDED',)): return 'sfha'
    if z == 'X' and ('0.2' in sub or 'LEVEE' in sub): return 'x02'
    return None


def overlap_pct(lines, geom_by_cat, log=print):
    """{cat: {seg: % of segment length inside}} (only > 0), exact intersections."""
    import shapely
    L = np.array([g if g is not None else shapely.LineString() for g in lines], dtype=object); tot = shapely.length(L); out = {}
    for cat, geoms in geom_by_cat.items():
        t = time.time(); parts = []
        for g in geoms:
            parts += list(shapely.get_parts(g)) if g is not None else []
        U = shapely.union_all(parts) if parts else None
        P = np.array(list(shapely.get_parts(U)) if U is not None and not U.is_empty else [], dtype=object)
        if not len(P): out[cat] = {}; continue
        tree = shapely.STRtree(P); li, pi = tree.query(L, predicate='intersects')
        inside = np.zeros(len(L))
        np.add.at(inside, li, shapely.length(shapely.intersection(L[li], P[pi])))
        pct = np.where(tot > 0, 100 * inside / np.maximum(tot, 1e-9), 0)
        out[cat] = {int(s): int(max(1, np.floor(min(100.0, pct[s])))) for s in np.nonzero(inside > 0)[0]}   # % floored, >= 1 when any overlap
        log(f'  {cat}: {len(P)} polygon parts, {len(out[cat])} segments touched, {sum(v >= STRICT for v in out[cat].values())} >= {STRICT:g} % ({time.time() - t:.0f} s)')
    return out


MASSGIS_ZIP = 'https://s3.us-east-1.amazonaws.com/download.massgis.digital.mass.gov/shapefiles/state/nfhl.zip'
MASSGIS_PAGE = 'https://www.mass.gov/info-details/massgis-data-fema-national-flood-hazard-layer'


def fetch_massgis(d3, log=print):
    """MassGIS statewide copy of the FEMA NFHL (FEMA_NFHL_POLY, same FLD_ZONE / ZONE_SUBTY / SFHA_TF fields) -> ({class: [geoms]}, meta)."""
    import tempfile
    import geopandas as gpd
    import requests
    import shapely
    tmp = os.path.join(tempfile.gettempdir(), 'massgis_nfhl.zip'); hdr = {}
    for i in range(4):
        try:
            with requests.get(MASSGIS_ZIP, stream=True, timeout=600) as r:
                r.raise_for_status(); hdr = {k: r.headers.get(k) for k in ('Last-Modified', 'Content-Length', 'ETag')}
                with open(tmp, 'wb') as f:
                    for b in r.iter_content(1 << 20): f.write(b)
            break
        except Exception as e:
            log(f'MassGIS download try {i}: {e}'); time.sleep(20)
    else:
        raise RuntimeError('MassGIS NFHL download failed')
    import zipfile
    names = [n for n in zipfile.ZipFile(tmp).namelist() if n.lower().endswith('.shp')]
    shp = [n for n in names if 'poly' in n.lower()] or names; log(f'MassGIS zip {hdr}; shapefiles {names}; using {shp[0]}')
    mask = gpd.GeoSeries([shapely.box(*d3)], crs=26986)
    G = gpd.read_file(f'zip://{tmp}!{shp[0]}', mask=mask).to_crs(26986)
    log(f'MassGIS NFHL: {len(G)} polygons in the District 3 bbox; columns {list(G.columns)[:25]}')
    geoms = {}; cnt = {}; zones = {}
    for a, g in zip(G.drop(columns='geometry').to_dict('records'), G.geometry):
        key = f"{attr(a, 'FLD_ZONE')}|{attr(a, 'ZONE_SUBTY')}"; zones[key] = zones.get(key, 0) + 1; c = fema_class(a)
        if c is None or g is None or g.is_empty: continue
        geoms.setdefault(f'fema_{c}', []).append(shapely.make_valid(g)); cnt[c] = cnt.get(c, 0) + 1
    dfirm = sorted({str(attr(a, 'DFIRM_ID')) for a in G.drop(columns='geometry').to_dict('records')})
    return geoms, dict(source='MassGIS statewide NFHL (FEMA_NFHL_POLY)', url=MASSGIS_ZIP, page=MASSGIS_PAGE, http=hdr, shapefile=shp[0],
                       polygons_in_bbox=len(G), polygons_by_class=cnt, zone_subtypes=zones, dfirm_ids=dfirm[:200],
                       note='MassGIS page (Jul 2025): FEMA data published as of 18 Jul 2025; latest study effective 8 Jul 2025, latest LOMR 9 Jul 2025')


def fetch(out, log=print, fema_source='massgis', rest_check=True):
    import shapely
    lines, towns = segment_lines(); B = shapely.bounds(np.array([g for g in lines if g is not None], dtype=object))
    d3 = (B[:, 0].min() - MARGIN_M, B[:, 1].min() - MARGIN_M, B[:, 2].max() + MARGIN_M, B[:, 3].max() + MARGIN_M)
    meta = dict(made=time.strftime('%Y-%m-%dT%H:%MZ', time.gmtime()), d3_bbox_26986=[round(v) for v in d3], strict_pct=STRICT, sources={})
    geoms = {}
    # FEMA NFHL: MassGIS statewide copy first (one download, stated currency); FEMA's REST service if that fails or as a cross-check
    if fema_source == 'massgis':
        try:
            g, m = fetch_massgis(d3, log); geoms.update(g); meta['sources']['fema'] = m
        except Exception as e:
            log(f'MassGIS NFHL failed ({e}); falling back to the FEMA REST service'); meta['sources']['massgis_error'] = str(e)
    rest_geoms = {}
    layer = None
    if 'fema' in meta['sources'] and not rest_check: FEMA_SERVERS_ = ()
    else: FEMA_SERVERS_ = FEMA_SERVERS
    for srv in FEMA_SERVERS_:
        try:
            j = _get(srv, dict(f='json'), tries=3)
            ids = [l['id'] for l in j.get('layers', []) if l.get('name', '').strip().lower() == FEMA_LAYER_NAME]
            layer = f'{srv}/{ids[0] if ids else FEMA_LAYER_DEFAULT}'; break
        except Exception as e:
            log(f'FEMA server {srv}: {e}')
    key_rest = 'fema_rest' if 'fema' in meta['sources'] else 'fema'
    if layer:
        try:
            lj = _get(layer, dict(f='json'), tries=3); log(f"FEMA layer {layer}: {lj.get('name')} (maxRecordCount {lj.get('maxRecordCount')})")
            where = "FLD_ZONE <> 'X' OR ZONE_SUBTY <> 'AREA OF MINIMAL FLOOD HAZARD'"
            try: F, st = query_tiles(layer, d3, where=where, out_fields='*', log=log)
            except RuntimeError as e:
                log(f'where clause failed ({e}); fetching every feature'); where = '1=1'; F, st = query_tiles(layer, d3, where=where, out_fields='*', log=log)
            cnt = {}; zones = {}
            for f in F:
                a = f.get('attributes', {}); c = fema_class(a); key = f"{attr(a, 'FLD_ZONE')}|{attr(a, 'ZONE_SUBTY')}"; zones[key] = zones.get(key, 0) + 1
                if c is None: continue
                g = esri_polygon((f.get('geometry') or {}).get('rings'))
                if g is not None: rest_geoms.setdefault(f'fema_{c}', []).append(g); cnt[c] = cnt.get(c, 0) + 1
            dates = sorted({str(attr(f.get('attributes', {}), 'DFIRM_ID')) for f in F})
            meta['sources'][key_rest] = dict(source='FEMA NFHL REST', layer=layer, layer_name=lj.get('name'), where=where, fetch=st, polygons_by_class=cnt,
                                             zone_subtypes=zones, dfirm_ids=dates[:200])
        except Exception as e:
            log(f'FEMA REST failed: {e}'); meta['sources'][key_rest] = dict(error=str(e)); rest_geoms = {}
    elif FEMA_SERVERS_:
        meta['sources'][key_rest] = dict(error='NFHL REST service not reachable')
    if key_rest == 'fema': geoms.update(rest_geoms); rest_geoms = {}
    # BSC Group / MRPC Leominster (every LeominsterFlooding_* feature service of the org; groups by TimeHorizon x ReturnPeriod)
    leo = [i for i, t in enumerate(towns) if t == 'Leominster']
    LB = shapely.bounds(np.array([lines[i] for i in leo if lines[i] is not None], dtype=object))
    lbox = (LB[:, 0].min() - 3000, LB[:, 1].min() - 3000, LB[:, 2].max() + 3000, LB[:, 3].max() + 3000)
    svcs = [LEO_DEFAULT]
    try:
        j = _get(LEO_ORG, dict(f='json'), tries=3)
        svcs = sorted({f"{LEO_ORG}/{s['name']}/{s['type']}" for s in j.get('services', []) if s.get('name', '').lower().startswith('leominsterflooding')
                       and s.get('type') == 'FeatureServer'} | {LEO_DEFAULT})
    except Exception as e:
        log(f'Leominster service list: {e}')
    meta['sources']['leominster'] = dict(services=svcs, bbox_26986=[round(v) for v in lbox], layers=[])
    for sv in svcs:
        try:
            sj = _get(sv, dict(f='json'), tries=3); lids = [l['id'] for l in sj.get('layers', [])] or [0]
        except Exception as e:
            log(f'{sv}: {e}'); meta['sources']['leominster']['layers'].append(dict(service=sv, error=str(e))); continue
        for lid in lids:
            url = f'{sv}/{lid}'
            try:
                F, st = query_tiles(url, lbox, log=log); n_all = _get(url + '/query', dict(where='1=1', returnCountOnly='true', f='json')).get('count')
            except Exception as e:
                log(f'{url}: {e}'); meta['sources']['leominster']['layers'].append(dict(url=url, error=str(e))); continue
            groups = {}
            for f in F:
                a = f.get('attributes', {}); th = attr(a, 'TimeHorizon'); rp = attr(a, 'ReturnPeriod')
                th = str(th).strip() if th not in (None, '') else sv.split('/')[-2].replace('LeominsterFlooding_', ''); rp = str(rp).strip() if rp not in (None, '') else 'NA'
                g = esri_polygon((f.get('geometry') or {}).get('rings'))
                if g is not None:
                    k = f'leo|{th}|{rp}'; geoms.setdefault(k, []).append(g); groups[k] = groups.get(k, 0) + 1
            meta['sources']['leominster']['layers'].append(dict(url=url, fetch=st, count_service=n_all, groups=groups))
    log('overlaps:')
    cats = overlap_pct(lines, geoms, log)
    if 'fema_sfha' in cats and 'fema_x02' in cats:       # the 0.2 % floodplain extent (500-yr) = SFHA + shaded X; overlaps of the union
        cats.update(overlap_pct(lines, {'fema_500': geoms.get('fema_sfha', []) + geoms.get('fema_x02', [])}, log))
    if rest_geoms.get('fema_sfha') and 'fema_sfha' in cats:   # cross-check: the FEMA REST service vs the MassGIS copy (SFHA, intersects / >= 30 %)
        rc = overlap_pct(lines, {'sfha': rest_geoms['fema_sfha']}, log)['sfha']; mc = cats['fema_sfha']
        agree = {}
        for nm, f in (('any', lambda d: {s for s, v in d.items() if v > 0}), ('30', lambda d: {s for s, v in d.items() if v >= STRICT})):
            a, b = f(mc), f(rc); agree[nm] = dict(massgis=len(a), rest=len(b), both=len(a & b), jaccard=len(a & b) / max(1, len(a | b)))
        meta['sources']['fema_rest']['agreement_sfha_segments'] = agree; log(f'REST vs MassGIS SFHA segments: {agree}')
    meta['n_segments'] = len(lines)
    meta['touched'] = {c: len(v) for c, v in cats.items()}; meta['strict'] = {c: sum(x >= STRICT for x in v.values()) for c, v in cats.items()}
    meta['fema_sfha_any_by_town'] = {}
    for s in cats.get('fema_sfha', {}): t = towns[s]; meta['fema_sfha_any_by_town'][t] = meta['fema_sfha_any_by_town'].get(t, 0) + 1
    meta['towns_without_sfha_segments'] = sorted(set(towns) - set(meta['fema_sfha_any_by_town']))
    res = dict(meta=meta, categories=cats)
    json.dump(res, open(out, 'w'), separators=(',', ':')); log(json.dumps({k: meta[k] for k in ('touched', 'strict', 'towns_without_sfha_segments')}))
    return res


# ------------------------------------------------------------------------------------------------ transport (annotations / check runs)
def compact(d):
    """categories {cat: {seg: pct}} -> {cat: [segment id deltas, pcts]} (smaller gzip); expand() inverts."""
    d = dict(d); C = {}
    for c, v in d['categories'].items():
        k = sorted(int(x) for x in v); C[c] = [np.diff([0] + k).tolist(), [v[str(x)] if str(x) in v else v[x] for x in k]]
    d['categories'] = C; return d


def expand(d):
    d['categories'] = {c: {str(s): p for s, p in zip(np.cumsum(dl).tolist(), pc)} for c, (dl, pc) in d['categories'].items()}; return d


def payload(path):
    raw = gzip.compress(json.dumps(compact(json.load(open(path))), separators=(',', ':')).encode(), 9); b = base64.b64encode(raw).decode(); sha = hashlib.sha256(b.encode()).hexdigest()[:12]
    return [b[i:i + CHUNK] for i in range(0, len(b), CHUNK)], sha


def emit(path, part, per=10):
    ch, sha = payload(path); n = len(ch)
    if part == 0:
        m = json.load(open(path))['meta']
        print(f"::warning title=static_maps summary::chunks {n} sha {sha} touched {json.dumps(m.get('touched'))} strict {json.dumps(m.get('strict'))}")
    for i in range(part * per, min(n, (part + 1) * per)):
        print(f'::notice title=sf {i}/{n} {sha}::{ch[i]}')


def checkruns(path, size=60000):
    import requests
    b = ''.join(payload(path)[0]); sha = hashlib.sha256(b.encode()).hexdigest()[:12]; parts = [b[i:i + size] for i in range(0, len(b), size)]
    repo = os.environ['GITHUB_REPOSITORY']; head = os.environ['GITHUB_SHA']; H = {'Authorization': f"Bearer {os.environ['GITHUB_TOKEN']}", 'Accept': 'application/vnd.github+json'}
    for i, p in enumerate(parts):
        r = requests.post(f'https://api.github.com/repos/{repo}/check-runs', headers=H, json=dict(
            name=f'static-maps data {i}/{len(parts)} {sha} run {os.environ.get("GITHUB_RUN_ID")}', head_sha=head, status='completed', conclusion='neutral',
            output=dict(title=f'static_maps payload {i}/{len(parts)}', summary=f'gzip+base64 chunk {i} of {len(parts)}, sha {sha}', text=p)))
        print(f'check run {i}/{len(parts)}: HTTP {r.status_code} {r.json().get("id") if r.ok else r.text[:200]}')


def decode(run_id, out, repo='Horus331/mass-flood-watch'):
    """Rebuild the flags JSON from the annotations of a static_maps.yml run (or its check runs)."""
    import subprocess
    gh = lambda p: json.loads(subprocess.run(['gh', 'api', '--paginate', p], capture_output=True, text=True, check=True).stdout.replace('][', ','))
    jobs = gh(f'repos/{repo}/actions/runs/{run_id}/jobs?per_page=100')
    jobs = jobs['jobs'] if isinstance(jobs, dict) else [x for j in jobs for x in j['jobs']]
    got = {}; n = sha = None
    for jb in jobs:
        for a in gh(f"repos/{repo}/check-runs/{jb['id']}/annotations?per_page=100"):
            t = a.get('title') or ''
            if t.startswith('sf '):
                i, rest = t[3:].split('/', 1); n_, s_ = rest.split(); n, sha = int(n_), s_; got[int(i)] = a['message']
    if n and len(got) == n and hashlib.sha256(''.join(got[i] for i in range(n)).encode()).hexdigest()[:12] == sha:
        b = ''.join(got[i] for i in range(n)); src = 'annotations'
    else:
        print(f'annotations incomplete ({len(got)}/{n}); trying check runs')
        head = subprocess.run(['gh', 'api', f'repos/{repo}/actions/runs/{run_id}', '--jq', '.head_sha'], capture_output=True, text=True, check=True).stdout.strip()
        cr = gh(f'repos/{repo}/commits/{head}/check-runs?per_page=100')
        cr = cr['check_runs'] if isinstance(cr, dict) else [x for c in cr for x in c['check_runs']]
        cr = [c for c in cr if c['name'].startswith('static-maps data') and c['name'].endswith(f'run {run_id}')]
        cr.sort(key=lambda c: int(c['name'].split()[2].split('/')[0])); sha = cr[0]['name'].split()[3]
        b = ''.join(subprocess.run(['gh', 'api', f"repos/{repo}/check-runs/{c['id']}", '--jq', '.output.text'], capture_output=True, text=True, check=True).stdout.strip() for c in cr)
        if hashlib.sha256(b.encode()).hexdigest()[:12] != sha: raise SystemExit('payload checksum mismatch')
        src = 'check runs'
    d = expand(json.loads(gzip.decompress(base64.b64decode(b)))); d['meta']['transport'] = dict(run_id=int(run_id), via=src, sha=sha)
    json.dump(d, open(out, 'w'), separators=(',', ':')); print(f'{out}: {len(d["categories"])} categories via {src}'); return d


# ------------------------------------------------------------------------------------------------ scoring
HELD = None


def variants(flags):
    """name -> (category, threshold %, description).  'any' = > 0 % of the length inside, '30' = >= 30 %."""
    C = flags['categories']; V = {}
    for cat, lab in (('fema_sfha', 'FEMA SFHA (1 %)'), ('fema_500', 'FEMA SFHA + 0.2 % (500-yr extent)'), ('fema_x02', 'FEMA 0.2 % / shaded X only')):
        if cat in C:
            V[f'{cat}_any'] = (cat, 0.0, f'{lab}, intersects'); V[f'{cat}_30'] = (cat, STRICT, f'{lab}, >= 30 % of length')
    for cat in sorted(c for c in C if c.startswith('leo|')):
        _, th, rp = cat.split('|'); nm = f"leo_{th}_{rp}".replace(' ', '').replace('%', 'pct').lower()
        V[f'{nm}_any'] = (cat, 0.0, f'BSC/MRPC Leominster {th} {rp}, intersects'); V[f'{nm}_30'] = (cat, STRICT, f'BSC/MRPC Leominster {th} {rp}, >= 30 % of length')
    return V


def seg_flags(flags, cat, thr, segs):
    d = flags['categories'].get(cat, {}); g = lambda s: d.get(str(int(s)), d.get(int(s), 0.0)) if isinstance(d, dict) else 0.0
    v = np.array([g(s) for s in segs], float)
    return v > 0 if thr <= 0 else v >= thr


def _binary(R, flag):
    Q = dict(R); Q['p'] = flag.astype(float); Q['pm'] = Q['p'].copy(); Q['depth'] = np.zeros(len(flag)); return Q


def score_storm(R, flags, V, domains):
    """-> {domain: {'n','sites','model_rule', 'static': {v: {...}}, 'hybrid': {...}}} with per-site hit vectors for the paired bootstrap."""
    import warnings
    import score_v2 as S
    warnings.filterwarnings('ignore', category=RuntimeWarning)
    S.RADII = (300,); S.FSS_DRAWS = 0          # only FSS at 300 m is reported here; chance FSS is not used (speed)
    out = {}
    for dom, dm, towns in domains:
        n = int(dm.sum())
        if n == 0: continue
        fl = {v: seg_flags(flags, c, t, R['seg']) for v, (c, t, _) in V.items() if dom == 'leominster' or not v.startswith('leo_')}   # BSC map: Leominster only
        ks = {v: int((f & dm).sum()) for v, f in fl.items()}
        S.SHARES = tuple(sorted({k / n for k in ks.values()}))
        M = S.score_domain(R, dm, towns)
        S.SHARES = ()
        if M['n_sites'] == 0 and dom != 'box': continue
        blk = lambda B: dict(k=B['k'], share=B['share'], hits=B['_hits'], chance=B['_chance'], fss300=[B['fss'].get('300', {}).get('num'), B['fss'].get('300', {}).get('den')])
        D = dict(n=n, sites=[s['id'] for s in M['sites']], n_sites=M['n_sites'], model_rule=blk(M['rule']), static={}, model_k={}, hybrid={})
        rule = R['p'] >= 0.5
        for v, f in fl.items():
            D['static'][v] = blk(S.score_domain(_binary(R, f), dm, towns)['rule'])
            D['model_k'][v] = blk(M['shares'][f'{ks[v] / n:g}'])
            if v in ('fema_sfha_any', 'fema_sfha_30') or (v.startswith('leo_') and 'current' in v and '100' in v):
                D['hybrid'][f'model_or_{v}'] = blk(S.score_domain(_binary(R, rule | f), dm, towns)['rule'])
                D['hybrid'][f'model_outside_{v}'] = blk(S.score_domain(_binary(R, rule & ~f), dm, towns)['rule'])
        out[dom] = D
    return out


def runs_to_score():
    import score_v2 as S
    R = {}
    for p, s, grp, prim in S.find_runs():
        if grp == 'parity' and prim and (s in S.HELDOUT + S.NEW16 or s == 'sep2023'): R[s] = p
    return R


def boot_pair(H1, H0, boot=BOOT, seed=0):
    """Paired two-stage bootstrap (storms, then sites within storm) of pooled recall(H1) - recall(H0).  H*: list of per-storm hit arrays."""
    rng = np.random.default_rng(seed); N = sum(len(h) for h in H1)
    if N == 0: return dict(delta=None)
    d0 = (sum(h.sum() for h in H1) - sum(h.sum() for h in H0)) / N; dd = []
    for _ in range(boot):
        sel = rng.integers(0, len(H1), len(H1)); a = b = n = 0.0
        for i in sel:
            if not len(H1[i]): continue
            j = rng.integers(0, len(H1[i]), len(H1[i])); a += H1[i][j].sum(); b += H0[i][j].sum(); n += len(j)
        dd.append((a - b) / n if n else 0.0)
    dd = np.array(dd); lo, hi = np.percentile(dd, [5, 95])
    return dict(delta=float(d0), ci90=[float(lo), float(hi)], p_le0=float((dd <= 0).mean()), p_ge0=float((dd >= 0).mean()),
                p_two=float(min(1.0, 2 * min((dd <= 0).mean(), (dd >= 0).mean()))))


def pool(per, dom, key, v=None):
    """Pooled recall / chance / lift / share / FSS300 of one row over storms."""
    H = C = N = K = Nn = num = den = 0.0
    for s, D in per.items():
        if dom not in D: continue
        B = D[dom][key] if v is None else D[dom][key][v]
        H += sum(B['hits']); C += sum(B['chance']); N += len(B['hits']); K += B['k']; Nn += D[dom]['n']
        if B['fss300'][1]: num += B['fss300'][0]; den += B['fss300'][1]
    return dict(sites=int(N), hits=H, recall=H / N if N else None, chance=C / N if N else None, lift=H / C if C else None,
                share=K / Nn if Nn else None, mean_share=float(np.mean([(D[dom][key] if v is None else D[dom][key][v])['share'] for D in per.values() if dom in D])) if per else None,
                fss300=1 - num / den if den else None)


def hits_list(per, dom, key, v=None):
    return [np.asarray((D[dom][key] if v is None else D[dom][key][v])['hits'], float) for s, D in per.items() if dom in D]


def score(flags_path, out, md=None, boot=BOOT):
    import score_v2 as S
    flags = json.load(open(flags_path)); V = variants(flags); runs = runs_to_score()
    held = [s for s in S.HELDOUT + S.NEW16 if s in runs]; res = dict(flags=os.path.relpath(flags_path, ROOT), variants={k: v[2] for k, v in V.items()}, per_storm={}, pools={})
    sets = [('heldout23', held, '0'), ('sep2023', ['sep2023'], '0'), ('sep2023_crowd', ['sep2023'], '1')]
    for name, storms, crowd in sets:
        os.environ['SCORE_CROWD'] = crowd; per = {}
        for s in storms:
            t = time.time(); R = S.load_run(runs[s], s)
            towns = S.DOMAIN_OVERRIDE.get(s) or tuple(sorted({R['town'][x] for v in R['matches'].values() for x in v}))
            doms = [('box', np.ones(len(R['seg']), bool), None)]
            if towns: doms.append(('towns', np.isin(R['town'], list(towns)), towns))
            if (R['town'] == 'Leominster').any(): doms.append(('leominster', R['town'] == 'Leominster', ('Leominster',)))
            per[s] = score_storm(R, flags, V, doms)
            b = per[s]['box']; print(f"{name:14s} {s:9s} sites {b['n_sites']:3d} model rule {sum(b['model_rule']['hits']):.0f} "
                                      f"sfha_any {sum(b['static'].get('fema_sfha_any', {}).get('hits', [])):.0f} ({time.time() - t:.0f} s)", flush=True)
        os.environ.pop('SCORE_CROWD', None)
        res['per_storm'][name] = {s: {dom: {k: v for k, v in D.items()} for dom, D in X.items()} for s, X in per.items()}
        P = {}
        for dom in ('box', 'towns', 'leominster'):
            if not any(dom in D for D in per.values()): continue
            rows = {}; mr = pool(per, dom, 'model_rule'); rows['model_rule'] = mr
            for v in V:
                if not all(v in D[dom]['static'] for D in per.values() if dom in D): continue      # BSC map rows: Leominster domain only
                st = pool(per, dom, 'static', v); mk = pool(per, dom, 'model_k', v)
                rows[v] = dict(static=st, model_same_share=mk,
                               static_minus_model_same_share=boot_pair(hits_list(per, dom, 'static', v), hits_list(per, dom, 'model_k', v), boot),
                               static_minus_model_rule=boot_pair(hits_list(per, dom, 'static', v), hits_list(per, dom, 'model_rule'), boot))
            for h in sorted({h for D in per.values() if dom in D for h in D[dom]['hybrid']}):
                rows[h] = dict(hybrid=pool(per, dom, 'hybrid', h), minus_model_rule=boot_pair(hits_list(per, dom, 'hybrid', h), hits_list(per, dom, 'model_rule'), boot))
            P[dom] = rows
        res['pools'][name] = dict(storms=list(per), domains=P)
    json.dump(res, open(out, 'w'), indent=0)
    if md: open(md, 'w').write(table(res))
    return res


def f3(x, nd=3):
    return '–' if x is None else f'{x:.{nd}f}'


def table(res):
    L = []
    for name, P in res['pools'].items():
        for dom, rows in P['domains'].items():
            L += [f'\n### {name} · {dom} ({len(P["storms"])} storm(s), {rows["model_rule"]["sites"]} sites)\n',
                  '| row | flagged share (pooled / mean) | site recall (hits) | chance | lift | FSS300 | model at the same share: recall (hits), FSS300 | '
                  'Δ recall static − model, same share [90 % CI], p (two-sided) | Δ static − model rule [90 % CI] |', '|' + '---|' * 9]
            m = rows['model_rule']
            L.append(f"| model, deployed rule (p_close ≥ 0.5) | {f3(m['share'] * 100, 2)} % / {f3(m['mean_share'] * 100, 2)} % | {f3(m['recall'])} ({m['hits']:.0f}) | "
                     f"{f3(m['chance'])} | {f3(m['lift'], 1)} | {f3(m['fss300'])} | | | |")
            for v, r in rows.items():
                if v == 'model_rule' or 'static' not in r: continue
                s, k, d, d2 = r['static'], r['model_same_share'], r['static_minus_model_same_share'], r['static_minus_model_rule']
                L.append(f"| {res['variants'][v]} | {f3(s['share'] * 100, 2)} % / {f3(s['mean_share'] * 100, 2)} % | {f3(s['recall'])} ({s['hits']:.0f}) | {f3(s['chance'])} | "
                         f"{f3(s['lift'], 1)} | {f3(s['fss300'])} | {f3(k['recall'])} ({k['hits']:.1f}), {f3(k['fss300'])} | "
                         f"{f3(d.get('delta'))} [{f3((d.get('ci90') or [None])[0])}, {f3((d.get('ci90') or [None, None])[1])}], p {f3(d.get('p_two'), 3)} | "
                         f"{f3(d2.get('delta'))} [{f3((d2.get('ci90') or [None])[0])}, {f3((d2.get('ci90') or [None, None])[1])}] |")
            for v, r in rows.items():
                if 'hybrid' not in r: continue
                h, d = r['hybrid'], r['minus_model_rule']
                L.append(f"| *exploratory* {v} | {f3(h['share'] * 100, 2)} % / {f3(h['mean_share'] * 100, 2)} % | {f3(h['recall'])} ({h['hits']:.0f}) | {f3(h['chance'])} | "
                         f"{f3(h['lift'], 1)} | {f3(h['fss300'])} | | | {f3(d.get('delta'))} [{f3((d.get('ci90') or [None])[0])}, {f3((d.get('ci90') or [None, None])[1])}] |")
    return '\n'.join(L) + '\n'


# ------------------------------------------------------------------------------------------------ selftest
def selftest():
    import shapely
    ok = True

    def check(n, c):
        nonlocal ok; ok &= bool(c); print(('PASS ' if c else 'FAIL ') + n)
    # esri rings: clockwise exterior 0..10 square with a ccw hole 4..6
    ext = [[0, 0], [0, 10], [10, 10], [10, 0], [0, 0]]; hole = [[4, 4], [6, 4], [6, 6], [4, 6], [4, 4]]
    g = esri_polygon([ext, hole]); check('esri polygon with hole: area 96', abs(g.area - 96) < 1e-9)
    g2 = esri_polygon([ext, [[20, 0], [20, 10], [30, 10], [30, 0], [20, 0]]]); check('two exteriors: area 200', abs(g2.area - 200) < 1e-9)
    lines = [shapely.LineString([(-10, 5), (20, 5)]), shapely.LineString([(4.5, 5), (5.5, 5)]), shapely.LineString([(50, 50), (60, 50)]), None]
    o = overlap_pct(lines, dict(z=[g, g]), log=lambda *a: None)['z']        # duplicate polygon must not double-count
    check(f'overlap pct {o}', o[0] == int(100 * 8 / 30) and 1 not in o and 2 not in o)
    check('fema classes', fema_class(dict(FLD_ZONE='AE', SFHA_TF='T')) == 'sfha' and fema_class(dict(FLD_ZONE='X', ZONE_SUBTY='0.2 PCT ANNUAL CHANCE FLOOD HAZARD')) == 'x02'
          and fema_class(dict(FLD_ZONE='X', ZONE_SUBTY='AREA OF MINIMAL FLOOD HAZARD')) is None and fema_class(dict(FLD_ZONE='AREA NOT INCLUDED')) is None)
    # bootstrap: identical -> delta 0; all better -> CI > 0
    a = [np.array([1., 0, 1]), np.array([0., 1])]; b = [np.array([0., 0, 0]), np.array([0., 0])]
    check('boot identical', boot_pair(a, a, 200)['delta'] == 0); r = boot_pair(a, b, 200); check(f'boot better {r}', r['ci90'][0] >= 0 and r['delta'] > 0)
    print('selftest', 'OK' if ok else 'FAILED'); return ok


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0]); sp = ap.add_subparsers(dest='cmd', required=True)
    p = sp.add_parser('fetch'); p.add_argument('--out', required=True); p.add_argument('--fema-source', choices=['massgis', 'rest'], default='massgis')
    p.add_argument('--no-rest-check', action='store_true', help='skip the FEMA REST cross-check when the MassGIS copy worked')
    p = sp.add_parser('emit'); p.add_argument('path'); p.add_argument('--part', type=int, default=0)
    p = sp.add_parser('checkruns'); p.add_argument('path')
    p = sp.add_parser('decode'); p.add_argument('--run', required=True); p.add_argument('--out', required=True)
    p = sp.add_parser('score'); p.add_argument('--flags', required=True); p.add_argument('--out', required=True); p.add_argument('--md'); p.add_argument('--boot', type=int, default=BOOT)
    sp.add_parser('selftest')
    a = ap.parse_args()
    if a.cmd == 'fetch': fetch(a.out, fema_source=a.fema_source, rest_check=not a.no_rest_check)
    elif a.cmd == 'emit': emit(a.path, a.part)
    elif a.cmd == 'checkruns': checkruns(a.path)
    elif a.cmd == 'decode': decode(a.run, a.out)
    elif a.cmd == 'score': score(a.flags, a.out, a.md, a.boot)
    else: sys.exit(0 if selftest() else 1)


if __name__ == '__main__':
    main()
