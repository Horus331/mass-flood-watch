"""District 3 road-segment flood vulnerability layer for ArcGIS (MassDOT GIS hand-off). Reads committed outputs only; writes docs/proto/arcgis/.

    python proto/arcgis_export.py            # ~2 min (the cascade engine is re-run in memory on the d3_sep2023 pack; nothing else is recomputed)

Inputs (all committed; nothing here changes a model, a threshold or a published output):
  docs/graph_segments.json                                   road graph (MassDOT road inventory, District 3): geometry, road, town, class, length, AADT
  docs/proto/parity/catalog/<storm>_<area>_20m/features_*.csv  clean parity baseline (parity/BASELINE.md): every in-box segment, 25 non-locked storms
  docs/proto/turing/d3_sep2023_p/features_sep2023.csv        District 3 Sept 2023 run (GPU, parity settings), 45,099 segments
  docs/site/data/d3_sep2023/roads.json (+ proto/cascade.py)  cascade engine, closure-by-closure delay (same engine and inputs as cascade.json)
  docs/proto/damage/runs/*/crossings_*.csv + damage_model.json crossing damage layer (experimental, proto/damage.py)
  proto/data/labels_tiered_<storm>.csv                       documented flood reports (NWS, news, WX1BOX, DPW, MA state, MassDOT crash, SeeClickFix)
  proto/data/massdot_repeat_flood_d3.csv                     MassDOT District 3 repeating flood sites
"""
import os, sys, json, csv, glob, math, zipfile, collections
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.normpath(os.path.join(HERE, '..')); sys.path.insert(0, HERE)
OUT = os.path.join(ROOT, 'docs', 'proto', 'arcgis')
CAT = os.path.join(ROOT, 'docs', 'proto', 'parity', 'catalog')
D3 = os.path.join(ROOT, 'docs', 'proto', 'turing', 'd3_sep2023_p', 'features_sep2023.csv')
DMG_RUNS = os.path.join(ROOT, 'docs', 'proto', 'damage', 'runs'); DMG_MODEL = os.path.join(ROOT, 'docs', 'proto', 'damage', 'damage_model.json')
CLASS_NAME = {0: 'local / collector', 1: 'arterial', 2: 'highway'}
RPT_M = 30.0        # a report is assigned to its nearest segment within 30 m (the strict label radius, PROTOCOL.md)
MDOT_M = 100.0      # a MassDOT repeating flood site is assigned to its nearest segment within 100 m
XING_M = 30.0       # a crossing belongs to the segment within 30 m (cascade.py XING_SNAP_M)
AADT_DEFAULT = 1000  # graph_segments.json default AADT for local roads without a count
NAME = 'd3_road_flood_vulnerability'

# field dictionary: (shapefile name <= 10 chars, type, unit, description)
FIELDS = [
    ('seg_id', 'int', '', 'Segment id = index in docs/graph_segments.json (the Mass Flood Watch District 3 road graph). Not a MassDOT RoadInventory ID.'),
    ('road', 'str', '', 'Street / route name from the road inventory (blank = unnamed)'),
    ('town', 'str', '', 'Town'),
    ('rd_class', 'str', '', 'Road class: highway (Interstate), arterial (other numbered US / MA route), local / collector (the rest)'),
    ('len_m', 'int', 'm', 'Segment length'),
    ('aadt', 'int', 'veh/day', 'AADT carried by the road graph'),
    ('aadt_dflt', 'int', '0/1', '1 = AADT is the 1,000 veh/day default (no count on the segment)'),
    ('n_cov', 'int', 'storms', 'Number of the 25 catalogue storms whose model box contains the segment (0 = never modelled in the catalogue)'),
    ('n_flag', 'int', 'storms', 'Number of the 25 catalogue storms with p_close >= 0.5 on the segment'),
    ('flag_rate', 'float', '0-1', 'n_flag / n_cov: share of the storms that modelled the segment in which it was flagged'),
    ('max_pclose', 'float', '0-1', 'Highest p_close over the 25 catalogue storms (physics prior: Phi((peak depth - 0.30 m) / 0.10 m), combined with freeboard / culvert / fast-water terms)'),
    ('flag_strm', 'str', '', 'Storms (catalogue keys) with p_close >= 0.5'),
    ('n_may', 'int', 'storms', "Catalogue storms where the segment is in the 'may close' layer (p_may_close >= 0.5: stream reaches the road crest) but p_close < 0.5"),
    ('cat_dep_m', 'float', 'm', 'Highest modelled peak water depth on the segment over the 25 catalogue storms'),
    ('d3_dep_m', 'float', 'm', 'Peak modelled water depth on the segment, District 3 Sept 11-13 2023 run (blank = outside the run box)'),
    ('d3_pclose', 'float', '0-1', 'p_close in the District 3 Sept 2023 run'),
    ('d3_h30', 'float', 'h', 'Hours with more than 30 cm on the segment, District 3 Sept 2023 run'),
    ('n_rpt', 'int', 'reports', 'Documented flood reports (25 catalogue storms) assigned to this segment: nearest segment within 30 m, street-level coordinates only'),
    ('rpt_src', 'str', '', 'Source families of those reports with counts (NWS, news, WX1BOX, DPW, MA_state, MassDOT_crash, SeeClickFix)'),
    ('rpt_ids', 'str', '', 'Report keys (label file:id), truncated to 254 characters'),
    ('n_mdot', 'int', 'sites', 'MassDOT District 3 repeating flood sites assigned to this segment (nearest segment within 100 m)'),
    ('mdot_ids', 'str', '', 'MassDOT repeating flood site ids'),
    ('vh_delay', 'float', 'veh-h', 'Cascade, Sept 2023 District 3 run: vehicle-hours of delay caused by this segment closing (detour) or being slowed (5-30 cm), 48 h window'),
    ('vh_detour', 'float', 'veh-h', 'Detour part of vh_delay'),
    ('h_closed', 'float', 'h', 'Cascade: hours the segment is closed (>= 30 cm) in the Sept 2023 run'),
    ('det_min', 'float', 'min', 'Cascade: largest added trip time of the detour around this closure (capped at 30 min)'),
    ('peak_vc', 'float', 'ratio', 'Cascade: peak volume / capacity when the segment carries detour traffic from other closures'),
    ('h_ovcap', 'float', 'h', 'Cascade: hours over capacity as a detour corridor'),
    ('dmg_xid', 'str', '', 'Road-stream crossing on this segment with the highest damage score (crossing id of docs/network/crossings_all.json)'),
    ('dmg_p', 'float', '0-1', 'Crossing damage score (stream-power fragility, damage_model.json), maximum over the 10 damage-layer runs. A ranking, not a calibrated probability'),
    ('dmg_rank', 'int', 'rank', 'Rank of that crossing among all modelled crossings (1 = highest damage score)'),
    ('dmg_pct', 'float', '%', 'Damage rank as a percentile of modelled crossings (0 = top)'),
    ('vuln', 'str', '', 'Vulnerability class: High / Medium / Low (rule in README.md)'),
    ('vuln_why', 'str', '', 'Which part of the rule set the class'),
]


def seg_lines(S, i):
    return [list(zip(np.cumsum(d[0::2]) / 1e5, np.cumsum(d[1::2]) / 1e5)) for d in S['geo'][i]]


def storms():
    R = []
    for d in sorted(glob.glob(os.path.join(CAT, '*_20m'))):
        f = glob.glob(os.path.join(d, 'features_*.csv'))
        if f: R.append((os.path.basename(d).split('_')[0], f[0]))
    return R


def fnum(v):
    try:
        x = float(v); return x if math.isfinite(x) else None
    except (TypeError, ValueError): return None


def build():
    import geopandas as gpd
    from shapely.geometry import MultiLineString, Point
    from shapely.strtree import STRtree
    S = json.load(open(os.path.join(ROOT, 'docs', 'graph_segments.json'))); n = S['n']; P = S['props']
    geom = [MultiLineString(seg_lines(S, i)) for i in range(n)]
    G = gpd.GeoSeries(geom, crs=4326); G26 = G.to_crs(26986); tree = STRtree(list(G26.values))

    # --- 25 catalogue storms
    ST = storms(); assert len(ST) == 25, len(ST)
    n_cov = np.zeros(n, int); n_flag = np.zeros(n, int); n_may = np.zeros(n, int); maxp = np.full(n, np.nan); dep = np.full(n, np.nan)
    flag_st = [[] for _ in range(n)]
    for key, f in ST:
        for r in csv.DictReader(open(f)):
            i = int(r['segment']); pc = float(r['p_close']); pm = fnum(r['p_may_close']) or 0.0; d = fnum(r['peak_depth_m']) or 0.0
            n_cov[i] += 1; maxp[i] = np.fmax(maxp[i], pc); dep[i] = np.fmax(dep[i], d)
            if pc >= 0.5: n_flag[i] += 1; flag_st[i].append(key)
            elif pm >= 0.5: n_may[i] += 1
    # --- District 3 Sept 2023 run
    d3 = {}
    for r in csv.DictReader(open(D3)):
        d3[int(r['segment'])] = (fnum(r['peak_depth_m']), fnum(r['p_close']), fnum(r['hours_over_30cm']))
    # --- cascade (full closure list; same engine and inputs as docs/site/data/d3_sep2023/cascade.json)
    import cascade as CS
    CS.TOP = 10 ** 7
    fr, h, D, box, meta = CS.load_pack('d3_sep2023', n); res = CS.cascade(D, h, fr, box, S, label='d3_sep2023', verbose=False)
    ref = json.load(open(os.path.join(ROOT, 'docs', 'site', 'data', 'd3_sep2023', 'cascade.json')))['totals']['vehicle_hours']
    assert res['totals']['vehicle_hours'] == ref, (res['totals']['vehicle_hours'], ref)
    clo = {c['seg']: c for c in res['closures']}; cor = {c['seg']: c for c in res['corridors']}
    # --- documented reports (labels_tiered: the 25 non-locked District 3 storms, all source families)
    rpt = [[] for _ in range(n)]; n_rows = collections.Counter(); unplaced = collections.Counter()
    for f in sorted(glob.glob(os.path.join(ROOT, 'proto', 'data', 'labels_tiered_*.csv'))):
        for r in csv.DictReader(open(f)):
            n_rows['all'] += 1
            if r['coord_quality'] == 'town': unplaced['town-level location'] += 1; continue
            p = gpd.GeoSeries([Point(float(r['lon']), float(r['lat']))], crs=4326).to_crs(26986).iloc[0]
            j = tree.query_nearest(p, max_distance=RPT_M)
            if not len(j): unplaced['no segment within 30 m'] += 1; continue
            rpt[int(j[0])].append((r['key'], r['source_family'])); n_rows['placed'] += 1
    mdot = [[] for _ in range(n)]; md_n = collections.Counter()
    for r in csv.DictReader(open(os.path.join(ROOT, 'proto', 'data', 'massdot_repeat_flood_d3.csv'))):
        md_n['all'] += 1
        p = gpd.GeoSeries([Point(float(r['lon']), float(r['lat']))], crs=4326).to_crs(26986).iloc[0]
        j = tree.query_nearest(p, max_distance=MDOT_M)
        if len(j): mdot[int(j[0])].append(r['id']); md_n['placed'] += 1
    # --- crossing damage layer
    sys.path.insert(0, HERE); import damage as DG
    model = json.load(open(DMG_MODEL))['model']; best = {}
    for d in sorted(glob.glob(os.path.join(DMG_RUNS, '*'))):
        cf = glob.glob(os.path.join(d, 'crossings_*.csv'))
        if not cf: continue
        rows = list(csv.DictReader(open(cf[0])))
        for r, p in zip(rows, DG.fragility(rows, model)):
            if r['id'] not in best or p > best[r['id']][0]: best[r['id']] = (float(p), float(r['x']), float(r['y']))
    ids = sorted(best, key=lambda k: -best[k][0]); rank = {k: i + 1 for i, k in enumerate(ids)}; nx_ = len(ids)
    dmg = {}
    for k in ids:
        p, x, y = best[k]; j = tree.query_nearest(Point(x, y), max_distance=XING_M)
        if not len(j): continue
        s = int(j[0])
        if s not in dmg or p > dmg[s][1]: dmg[s] = (k, p, rank[k])

    # --- table
    recs = []
    for i in range(n):
        dd = d3.get(i, (None, None, None)); c = clo.get(i, {}); o = cor.get(i, {}); dm = dmg.get(i)
        src = collections.Counter(s for _, s in rpt[i])
        r = dict(seg_id=i, road=P['road'][i] or '', town=P['town'][i] or '', rd_class=CLASS_NAME[int(P['cls'][i])], len_m=int(P['len'][i]),
                 aadt=int(P['aadt'][i]), aadt_dflt=int(int(P['aadt'][i]) == AADT_DEFAULT), n_cov=int(n_cov[i]), n_flag=int(n_flag[i]),
                 flag_rate=round(n_flag[i] / n_cov[i], 3) if n_cov[i] else None,
                 max_pclose=None if np.isnan(maxp[i]) else round(float(maxp[i]), 3), flag_strm=';'.join(flag_st[i]), n_may=int(n_may[i]),
                 cat_dep_m=None if np.isnan(dep[i]) else round(float(dep[i]), 2),
                 d3_dep_m=None if dd[0] is None else round(dd[0], 2), d3_pclose=None if dd[1] is None else round(dd[1], 3), d3_h30=dd[2],
                 n_rpt=len(rpt[i]), rpt_src=';'.join(f'{k} {v}' for k, v in sorted(src.items())), rpt_ids=';'.join(k for k, _ in rpt[i])[:254],
                 n_mdot=len(mdot[i]), mdot_ids=';'.join(mdot[i]),
                 vh_delay=round(c['vehh_detour'] + c['vehh_slow'], 1) if c else None, vh_detour=c.get('vehh_detour'), h_closed=c.get('hours_closed'),
                 det_min=c.get('max_detour_min'), peak_vc=o.get('peak_vc'), h_ovcap=o.get('hours_over_capacity'),
                 dmg_xid=dm[0] if dm else '', dmg_p=round(dm[1], 4) if dm else None, dmg_rank=dm[2] if dm else None,
                 dmg_pct=round(100.0 * (dm[2] - 1) / nx_, 1) if dm else None)
        r['vuln'], r['vuln_why'] = vclass(r); recs.append(r)
    # export set: every segment the catalogue or the District 3 run modelled, or with a report / MassDOT site
    keep = [i for i, r in enumerate(recs) if r['n_cov'] > 0 or r['d3_dep_m'] is not None or r['n_rpt'] or r['n_mdot']]
    stats = dict(segments_graph=n, segments_exported=len(keep), storms=[k for k, _ in ST], reports=dict(n_rows) | dict(unplaced=dict(unplaced)),
                 massdot_repeat=dict(md_n), crossings_scored=nx_, crossings_on_segments=len(dmg), cascade_segments=len(clo), corridor_segments=len(cor),
                 cascade_totals=res['totals'])
    return recs, keep, geom, stats


def vclass(r):
    rep = r['n_rpt'] + r['n_mdot']; d3f = (r['d3_pclose'] or 0) >= 0.5
    if r['n_flag'] >= 2: return 'High', 'flagged in >= 2 catalogue storms'
    if (r['n_flag'] >= 1 or d3f) and rep >= 1: return 'High', 'flagged by the model and a documented report / MassDOT site'
    if r['n_flag'] == 1: return 'Medium', 'flagged in 1 catalogue storm'
    if d3f: return 'Medium', 'flagged in the District 3 Sept 2023 run'
    if rep >= 1: return 'Medium', 'documented report / MassDOT site, not flagged by the model'
    if r['n_may'] >= 1: return 'Medium', "in the 'may close' layer in >= 1 catalogue storm"
    if r['n_cov'] == 0 and r['d3_dep_m'] is None: return 'Low', 'not modelled (outside every model box)'
    return 'Low', 'modelled, never flagged, no report'


def write(recs, keep, geom, stats):
    import geopandas as gpd, pandas as pd
    os.makedirs(OUT, exist_ok=True)
    cols = [f[0] for f in FIELDS]
    df = pd.DataFrame([recs[i] for i in keep], columns=cols)
    for name, typ, _, _ in FIELDS:
        if typ == 'str': df[name] = df[name].fillna('').astype(str)
    gdf = gpd.GeoDataFrame(df, geometry=[geom[i] for i in keep], crs=4326)
    gj = os.path.join(OUT, NAME + '.geojson')
    if os.path.exists(gj): os.remove(gj)
    gdf[wet_mask(df)].to_file(gj, driver='GeoJSON', engine='pyogrio', layer_options={'COORDINATE_PRECISION': 5, 'RFC7946': 'YES'})
    df.to_csv(os.path.join(OUT, NAME + '.csv'), index=False)
    sd = os.path.join(OUT, '_shp'); os.makedirs(sd, exist_ok=True)
    shp = gdf.to_crs(26986)
    shp.to_file(os.path.join(sd, NAME + '.shp'), driver='ESRI Shapefile', engine='pyogrio', encoding='UTF-8')
    zp = os.path.join(OUT, NAME + '_shp.zip')
    with zipfile.ZipFile(zp, 'w', zipfile.ZIP_DEFLATED) as z:
        for f in sorted(os.listdir(sd)): z.write(os.path.join(sd, f), f)
        z.writestr('FIELDS.csv', fields_csv())
    for f in os.listdir(sd): os.remove(os.path.join(sd, f))
    os.rmdir(sd)
    open(os.path.join(OUT, 'FIELDS.csv'), 'w').write(fields_csv())
    cnt = collections.Counter(df['vuln']); why = collections.Counter(zip(df['vuln'], df['vuln_why']))
    stats.update(vuln=dict(cnt), vuln_why={f'{a}: {b}': v for (a, b), v in sorted(why.items())},
                 km=dict(df.groupby('vuln')['len_m'].sum().div(1000).round(1)),
                 sizes_mb={f: round(os.path.getsize(os.path.join(OUT, f)) / 1e6, 2) for f in sorted(os.listdir(OUT)) if f.startswith(NAME)})
    json.dump(stats, open(os.path.join(OUT, 'build_stats.json'), 'w'), indent=1, default=float)
    return gdf, stats


def wet_mask(df):
    """GeoJSON subset (size): every High / Medium segment, plus every Low segment with >= 5 cm modelled water in any run, a cascade value or a
    scored crossing.  The Low segments left out are dry (< 5 cm) in all 26 runs; they are in the shapefile and the CSV."""
    return ((df['vuln'] != 'Low') | (df['cat_dep_m'].fillna(0) >= 0.05) | (df['d3_dep_m'].fillna(0) >= 0.05) | df['vh_delay'].notna()
            | df['peak_vc'].notna() | df['dmg_p'].notna()).values


def fields_csv():
    import io
    b = io.StringIO(); w = csv.writer(b); w.writerow(['field', 'type', 'unit', 'description'])
    for f in FIELDS: w.writerow(f)
    return b.getvalue()


def verify(stats):
    import geopandas as gpd, pandas as pd
    a = gpd.read_file(os.path.join(OUT, NAME + '.geojson')); b = gpd.read_file('zip://' + os.path.join(OUT, NAME + '_shp.zip') + '!' + NAME + '.shp')
    c = pd.read_csv(os.path.join(OUT, NAME + '.csv'))
    assert len(b) == len(c) == stats['segments_exported'] and len(a) == int(wet_mask(c).sum())
    assert set(b.loc[b['vuln'] != 'Low', 'seg_id']) <= set(a['seg_id'])
    assert a.crs.to_epsg() == 4326 and b.crs.to_epsg() == 26986
    bb = b.set_index('seg_id').loc[a['seg_id']]
    assert (a['vuln'].values == bb['vuln'].values).all() and (c['seg_id'].values == b['seg_id'].values).all()
    assert all(len(col) <= 10 for col in b.columns)
    la, lb = a.to_crs(26986).length.values, bb.length.values
    assert np.nanmax(np.abs(la - lb) / np.maximum(lb, 1.0)) < 0.01, np.nanmax(np.abs(la - lb))
    stats['geojson_features'] = len(a)
    print('verify ok: geojson', len(a), 'shp/csv', len(b), 'features;', a.crs, b.crs, '; shapefile columns', list(b.columns)[:6], '...')


if __name__ == '__main__':
    recs, keep, geom, stats = build(); gdf, stats = write(recs, keep, geom, stats); verify(stats)
    json.dump(stats, open(os.path.join(OUT, 'build_stats.json'), 'w'), indent=1, default=float)
    print(json.dumps({k: v for k, v in stats.items() if k != 'cascade_totals'}, indent=1, default=float))
