"""Storm-drain capacity test (sim/colab/lf_drains.py): per-run City of Leominster evaluation + base / drains / design comparison
(.github/workflows/drains_test.yml, docs/proto/drains/DRAINS.md).

    python proto/drains_eval.py city <w9 out dir> <dest dir>     # in the Actions job, after prototype / score / validate_points
    python proto/drains_eval.py compare                          # docs/proto/drains/<storm>_<case>/ -> docs/proto/drains/drains.json

city: everything inside the City of Leominster (road segments whose MassDOT town is Leominster, the area the DPW pipe network covers;
outside it the 'drains' sink is zero), from this run's outputs:
  - flagged share = city segments at p_close >= 0.5 / city segments in the box (prototype segments.geojson; rows not kept have P < 0.1)
  - labels caught (strict, 30 m, depth rule = p_close) for labels whose town is Leominster, chance recall at the same flagged share, lift
  - DPW damage points (labels_sep2023_leominster_dpw.csv) the same way, from summary_dpw.json (sep2023 only)
  - wet road share: city road points (10 m spacing, segment ends and water cells left out) with hmax >= 0.10 / 0.30 m: the false-alarm side
  - observed points (points.json, LSR / Storm Events / labels) whose nearest road point is a city road (<= 300 m): hit_10 / hit_30
drain totals (whole box; from the .mass file and the rain-excess file):
  - net source = last 'Rain-(Inf+Evap)' of lisflood.mass (cumulative m3: rain excess in, scalar infiltration + drain sink out)
  - rain excess = total_rainfall_depth of rain.nc (the CN rain excess the solver received), m3
compare: volume removed by the sink = net source(base) - net source(case), i.e. drain removal net of the change in the 2 mm/h scalar
  infiltration (drained cells dry out sooner and infiltrate less, so this is a lower bound on what the pipes took).
"""
import csv, glob, json, os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, 'sim', 'infra'))
CITY = 'Leominster'
DEST = os.path.join(ROOT, 'docs', 'proto', 'drains')


def labels_town(path):
    return {r['id']: (r.get('town') or '').strip() for r in csv.DictReader(open(path))} if path and os.path.exists(path) else {}


def site_stats(summary_path, labels_path, share):
    if not os.path.exists(summary_path): return None
    L = json.load(open(summary_path))['checks'].get('labels_segments') or {}
    town = labels_town(labels_path)
    S = [s for s in L.get('sites', []) if town.get(s['id']) == CITY]
    if not S: return dict(n=0)
    hit = [('depth' in s.get('hit', [])) for s in S]
    rnd = float(np.mean([1 - (1 - share) ** max(1, s.get('n_segments', 1)) for s in S]))
    rec = float(np.mean(hit))
    out = dict(n=len(S), caught=int(sum(hit)), recall=round(rec, 3), random_recall=round(rnd, 3), lift=round(rec / rnd, 2) if rnd > 0 else None)
    by = {}
    for s, h in zip(S, hit): by.setdefault(s['type'], []).append(h)
    out['by_type'] = {k: f'{sum(v)}/{len(v)}' for k, v in sorted(by.items())}
    return out


def city(o, d):
    from scipy.spatial import cKDTree
    import impacts as IM
    meta = json.load(open(f'{o}/meta.json')); storm = os.environ.get('STORM', 'sep2023')
    S = json.load(open(os.path.join(ROOT, 'docs', 'graph_segments.json'))); town = np.array(S['props']['town'])
    Q = IM.road_points(S, meta, 10.0); inc = town[Q['seg']] == CITY
    segs = np.unique(Q['seg'][inc]); n_seg = len(segs)
    P = {}
    if os.path.exists(f'{d}/segments.geojson'):
        for f in json.load(open(f'{d}/segments.geojson'))['features']:
            p = f['properties']; P[int(p['segment'])] = p
    pc = np.array([P.get(int(s), {}).get('p_close', 0.0) or 0.0 for s in segs]); pm = np.array([P.get(int(s), {}).get('p_may_close', 0.0) or 0.0 for s in segs])
    share = float((pc >= 0.5).mean()) if n_seg else 0.0
    R = dict(city=CITY, storm=storm, segments=int(n_seg), flagged=int((pc >= 0.5).sum()), flagged_share=round(share, 4),
             may_close=int((pm >= 0.5).sum()), may_close_share=round(float((pm >= 0.5).mean()) if n_seg else 0.0, 4))
    lab = (sorted(glob.glob(os.path.join(HERE, 'data', f'labels_{storm}_*.csv'))) or [None])[0]
    R['labels_strict'] = site_stats(f'{d}/summary.json', lab, share)
    R['labels_file'] = os.path.basename(lab) if lab else None
    dpw = os.path.join(HERE, 'data', 'labels_sep2023_leominster_dpw.csv')
    if storm == 'sep2023': R['dpw_strict'] = site_stats(f'{d}/summary_dpw.json', dpw, share)
    # wet road share in the city (false-alarm side)
    h = np.nan_to_num(np.load(f'{o}/hmax.npy').astype(np.float32))
    wm = np.load(f'{o}/watermask.npy').astype(bool) if os.path.exists(f'{o}/watermask.npy') else np.zeros(h.shape, bool)
    k = inc & ~Q['end'] & ~wm[Q['r'], Q['c']]; hv = h[Q['r'][k], Q['c'][k]]
    R['road_points'] = int(k.sum()); R['wet_road_share_10cm'] = round(float((hv >= 0.1).mean()), 4) if k.any() else None
    R['wet_road_share_30cm'] = round(float((hv >= 0.3).mean()), 4) if k.any() else None
    # observed points near city roads
    from pyproj import Transformer
    tr = Transformer.from_crs(4326, 26986, always_xy=True); t = cKDTree(np.column_stack([Q['x'], Q['y']]))
    for name, f in (('points', 'points.json'), ('dpw_points', 'points_dpw.json')):
        if not os.path.exists(f'{d}/{f}'): continue
        rows = json.load(open(f'{d}/{f}'))['points']
        if not rows: continue
        x, y = tr.transform([r['lon'] for r in rows], [r['lat'] for r in rows]); dist, i = t.query(np.column_stack([x, y]))
        sel = [r for r, di, ii in zip(rows, dist, i) if di <= 300 and town[Q['seg'][ii]] == CITY]
        R[name] = dict(n=len(sel), hit_10=round(float(np.mean([r['hit_10'] for r in sel])), 3) if sel else None,
                       hit_30=round(float(np.mean([r['hit_30'] for r in sel])), 3) if sel else None)
    # drain totals (box)
    V = {}
    if os.path.exists(f'{o}/lisflood.mass'):
        last = [l.split() for l in open(f'{o}/lisflood.mass') if l.strip() and not l.startswith('Time')][-1]
        V['net_source_m3'] = round(float(last[11])); V['volume_m3'] = round(float(last[5]))
    rn = os.path.join(os.path.dirname(o), 'rain.nc')
    if os.path.exists(rn):
        try:
            from scipy.io import netcdf_file
            f = netcdf_file(rn, 'r', mmap=False); tot = np.array(f.variables['total_rainfall_depth'][:], np.float64); f.close()
        except Exception:
            import netCDF4; f = netCDF4.Dataset(rn); tot = np.array(f.variables['total_rainfall_depth'][:], np.float64); f.close()
        tot = np.where(tot < 0, 0, tot); V['rain_excess_m3'] = round(float(tot.sum()) / 1000 * meta['res_m'] ** 2); V['rain_excess_mean_mm'] = round(float(tot.mean()), 1)
    dr = meta.get('inputs', {}).get('drains')
    if isinstance(dr, dict): V['sink_capacity_m3s'] = dr.get('total_q_m3s'); V['sink_cells'] = dr.get('cells')
    R['volumes'] = V
    json.dump(R, open(f'{d}/city.json', 'w'), indent=1); print(json.dumps(R, indent=1))


def g(d, *ks):
    for k in ks:
        if not isinstance(d, dict): return None
        d = d.get(k)
    return d


def equal_budget(storm, cases):
    """Ranking test at equal flag budgets inside the city: rank city segments by peak depth on the road (segments.geojson; rows not kept
    = 0) and flag the top k, for k = each case's own p_close >= 0.5 count.  If drains only acted like a higher threshold, base at the
    drains budget would catch as many documented sites as the drains run; if they reorder the city (pipes drain the streets that do not
    flood), the drains run catches more at the same k."""
    import gzip
    import impacts as IM
    import prototype as PR
    d0 = os.path.join(DEST, f'{storm}_{cases[0]}'); meta = json.load(open(f'{d0}/flood_meta.json'))
    S = json.load(open(os.path.join(ROOT, 'docs', 'graph_segments.json'))); town = np.array(S['props']['town'])
    Q = IM.road_points(S, meta, 10.0); segs = np.unique(Q['seg'][town[Q['seg']] == CITY]); pos = {int(s): i for i, s in enumerate(segs)}
    files = [f for f in sorted(glob.glob(os.path.join(HERE, 'data', f'labels_{storm}_*.csv')))]
    sites = {}
    for f in files:
        tw = labels_town(f)
        sites[os.path.basename(f)] = [[pos[int(x)] for x in sg if int(x) in pos] for lab, sg in PR.label_segments(PR.load_labels(f), Q, S['props'], meta, strict=True) if tw.get(lab['id']) == CITY]
        sites[os.path.basename(f)] = [v for v in sites[os.path.basename(f)] if v]
    depth, k = {}, {}
    for c in cases:
        d = os.path.join(DEST, f'{storm}_{c}'); fn = f'{d}/segments.geojson.gz'
        if not os.path.exists(fn): continue
        a = np.zeros(len(segs)); pc = np.zeros(len(segs))
        for ft in json.load(gzip.open(fn))['features']:
            p = ft['properties']; i = pos.get(int(p['segment']))
            if i is not None: a[i] = p.get('peak_depth_m') or 0.0; pc[i] = p.get('p_close') or 0.0
        depth[c] = a + 1e-3 * pc; k[c] = int((pc >= 0.5).sum())
    R = dict(note=equal_budget.__doc__.split('.')[0], k=k, caught={})
    for kc, kv in k.items():
        for c, a in depth.items():
            fl = np.zeros(len(segs), bool); fl[np.argsort(-a, kind='stable')[:kv]] = True
            R['caught'].setdefault(f'top{kv}_({kc} budget)', {})[c] = {f: f'{sum(bool(fl[v].any()) for v in V)}/{len(V)}' for f, V in sites.items()}
    return R


def compare():
    out = {}
    for s in ('sep2023', 'aug2026'):
        for c in ('base', 'drains', 'design'):
            d = os.path.join(DEST, f'{s}_{c}')
            if not os.path.exists(f'{d}/city.json'): continue
            C = json.load(open(f'{d}/city.json')); Su = json.load(open(f'{d}/summary.json')) if os.path.exists(f'{d}/summary.json') else {}
            Sc = json.load(open(f'{d}/score.json')) if os.path.exists(f'{d}/score.json') else {}
            Pt = json.load(open(f'{d}/points.json'))['summary'] if os.path.exists(f'{d}/points.json') else {}
            Pd = json.load(open(f'{d}/points_dpw.json'))['summary'] if os.path.exists(f'{d}/points_dpw.json') else {}
            Sd = json.load(open(f'{d}/summary_dpw.json')) if os.path.exists(f'{d}/summary_dpw.json') else {}
            M = json.load(open(f'{d}/flood_meta.json')) if os.path.exists(f'{d}/flood_meta.json') else {}
            dr = g(M, 'inputs', 'drains')
            L = g(Su, 'checks', 'labels_segments', 'depth_rule'); LD = g(Sd, 'checks', 'labels_segments', 'depth_rule')
            box = dict(flagged_share=g(L, 'flagged_share'), n_flagged=g(L, 'n_flagged'),
                       labels=dict(n=g(L, 'all', 'n'), recall=g(L, 'all', 'recall'), lift=g(L, 'all', 'lift')),
                       dpw=dict(n=g(LD, 'all', 'n'), recall=g(LD, 'all', 'recall'), lift=g(LD, 'all', 'lift')) if LD else None,
                       points_all=Pt.get('all'), random_road_points=Pt.get('random_road_points'), dpw_points=Pd.get('all') if Pd else None,
                       peak_wet_km2=M.get('peak_wet_km2'), gauge_mean_rise_bias_m=Sc.get('mean_rise_bias_m'), gauge_mean_abs_rise_error_m=Sc.get('mean_abs_rise_error_m'),
                       gauges=[dict(site=x['site'], rise_error_m=x.get('rise_error_m')) for x in Sc.get('gauges', [])], runtime_s=M.get('runtime_s'),
                       sink=dict(total_q_m3s=dr.get('total_q_m3s'), cells=dr.get('cells'), pipes=g(dr, 'pipes'), design=g(dr, 'design'), probe=dr.get('probe')) if isinstance(dr, dict) else None)
            out.setdefault(s, {})[c] = dict(box=box, city=C)
        b = g(out, s, 'base', 'city', 'volumes', 'net_source_m3')
        for c, v in out.get(s, {}).items():
            V = v['city']['volumes']; ns = V.get('net_source_m3'); rx = V.get('rain_excess_m3')
            if b is not None and ns is not None:
                rem = b - ns; V['removed_vs_base_m3'] = round(rem)
                if rx: V['removed_share_of_rain_excess'] = round(rem / rx, 4)
                V['removed_mm_over_city_77km2'] = round(rem / 76.6e6 * 1000, 1)
        if s in out: out[s]['equal_budget_city'] = equal_budget(s, [c for c in ('base', 'drains', 'design') if c in out[s]])
    json.dump(out, open(os.path.join(DEST, 'drains.json'), 'w'), indent=1)
    for s, D in out.items():
        print(f'== {s}')
        print('case    | box: flag% labels rec lift | city: segs flag% labels caught/n lift | dpw caught/n | wet road 10/30cm | pts hit30 | gauge bias | removed m3 (share)')
        for c, v in D.items():
            if c == 'equal_budget_city': print('equal budget (city, top-k by road depth):', json.dumps(v['caught'])); continue
            B, C = v['box'], v['city']; l = C.get('labels_strict') or {}; dp = C.get('dpw_strict') or {}; V = C['volumes']
            print(f"{c:7s} | {B['flagged_share']} {B['labels']['recall']} {B['labels']['lift']} | {C['segments']} {C['flagged_share']} {l.get('caught')}/{l.get('n')} {l.get('lift')} | "
                  f"{dp.get('caught')}/{dp.get('n')} | {C.get('wet_road_share_10cm')}/{C.get('wet_road_share_30cm')} | {g(C, 'points', 'hit_30')} | {B['gauge_mean_rise_bias_m']} | "
                  f"{V.get('removed_vs_base_m3')} ({V.get('removed_share_of_rain_excess')})")


if __name__ == '__main__':
    if sys.argv[1] == 'city': city(sys.argv[2], sys.argv[3])
    else: compare()
