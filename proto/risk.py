"""Risk matrix: likelihood (p_close / P(overtopping)) x consequence (repair + user delay + critical access) for flagged segments and crossings.

    python proto/risk.py --out docs/proto/leominster_sep2023 [--run-dir <LISFLOOD-FP run dir, for crossing status>]
    python proto/risk.py --selftest

Post-step after proto/prototype.py and proto/resilience.py (reads segments.geojson and resilience_segments.csv from --out).  Writes
risk_matrix.csv (top 50, class Low / Medium / High / Extreme), risk.json (all counts, totals, unit costs, sources) and risk_matrix.png.
ALL COSTS ARE ORDER-OF-MAGNITUDE PLANNING NUMBERS (2023 US$, low-high ranges, the midpoint is the geometric mean), not engineer's estimates.

Items
  segments   p_close >= 0.1 (prototype, unchanged).
  crossings  road-stream crossings in the box that the impacts layer (sim/infra/impacts.py, FHWA HDS-5) finds overtopped or surcharged, or
             surveyed culverts with P(overtop) >= 0.1 under the prototype's culvert rule.  P(overtop) = the prototype's culvert rule where the NAACC barrel and the modelled flow are known
             (Phi(ln(Q / Q_crest) / 0.30)), else Phi((HW - crest) / 0.10) from the modelled headwater, else Phi((road depth - 0.15) / 0.10)
             from the water on the road within 30 m (impacts.py 'overtopped from the road').  Needs the run dir; without it no crossings.

Consequence ($) per segment = pavement repair + user delay
  pavement repair, per lane-km, 2 lanes (the graph has no lane count; divided roads are one segment per direction):
     inundated < 24 h over 30 cm     $3k - $15k     clean-up, debris, shoulder / ditch repair, inspection (assumption)
     inundated >= 24 h               $60k - $150k   mill + 50 mm HMA overlay: submerged asphalt roads lost strength ~ 2 in of new AC and were costed at $250k / mile
                                                    for a 4 in mill + overlay (Gaspard et al. 2007, New Orleans after Katrina; no significant duration effect there,
                                                    so the 24 h split is our assumption); HMA $110-160 / t in place
                                                    (MassDOT 2023 liquid-asphalt price index $625-665 / t, ~5.5 % binder), milling $3-6 / m2
     washout (within 30 m of an overtopped crossing with p_close >= 0.5, or p_washout >= 0.5)
                                     $0.5M - $1.4M over min(length, 50 m): embankment, base and pavement rebuilt; upper end = VTrans 2014
                                                    post-Irene roadway / bank armoring $1.7M per mile in 2023 $
  user delay: vehicle-hours of delay the closure causes (proto/resilience.py: detours of closed stretches + slow wet driving) x 1.67 persons per
     vehicle (2017 NHTS all-trip mean occupancy, as used in USDOT BCA guidance) x $18.13 per person-hour (USDOT 2016 Revised Departmental
     Guidance on Valuation of Travel Time, local travel, all purposes, $14.10 in 2015 $ x CPI-U 2023 / 2015 = 304.702 / 237.017).
Consequence ($) per crossing = replacement at the size the Massachusetts River and Stream Crossing Standards (2011) require for a new crossing
  (span >= 1.2 x bankfull width; existing span if larger), VTrans 2014 Tropical Storm Irene unmet-needs cost table (Table 1-3) x CPI-U 2023 / 2014
  (304.702 / 236.736 = 1.287):
     span < 1.2 m (pipe <= 4 ft)            $19k - $109k     (town culverts 3-4 ft, $15k-$85k in 2014)
     1.2 - 1.8 m (4x3 - 6x5 ft box)         $264k - $360k    ($205k-$280k)
     1.8 - 3.7 m (to 10x5 ft box)           $360k - $521k    ($280k-$405k)
     3.7 - 7 m (14x7 - 22x8 ft bridge)      $553k - $1.29M   ($430k-$1.0M)
     > 7 m (bridge)                         $1.29M - $2.6M   (upper = 2 x; assumption; replacement is an upper bound for a bridge)
     size unknown                           $19k - $521k
  The crossing's own repair is not added to the segment's (no double count); delay sits on the segment.
Critical access (not in $): road-km in the box that lose access within the response-time standard (hospital 30 min, fire 8 min, police 10 min,
  as proto/resilience.py) when this segment alone is closed on the dry network: link importance in the sense of Jenelius, Petersen & Mattsson 2006.
  A crossing takes the value of the segment it carries.
Classes (5 x 5 matrix, AS/NZS ISO 31000-style qualitative bands)
  likelihood L1 p < 0.1, L2 0.1-0.3, L3 0.3-0.5, L4 0.5-0.9, L5 >= 0.9
  consequence = max of the $ class (C1 < $50k, C2 < $250k, C3 < $1M, C4 < $5M, C5 >= $5M) and the access class
                (C1 0 km, C2 <= 2 km, C3 <= 10 km, C4 <= 40 km, C5 > 40 km of the box's road-km)
  risk = L x C: Low 1-4, Medium 5-9, High 10-16, Extreme 20-25.   expected cost = likelihood x consequence $ (mid).
"""
import os, sys, json, csv, math, argparse, time
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.normpath(os.path.join(HERE, '..'))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(ROOT, 'sim', 'infra'))
import impacts as IM
import resilience as RS

CPI = {2014: 236.736, 2015: 237.017, 2023: 304.702}                       # BLS CPI-U, US city average, annual
VOT_2015 = 14.10                                                          # USDOT 2016 VOT guidance, local travel, all purposes, 2015 $ / person-h
VOT = round(VOT_2015 * CPI[2023] / CPI[2015], 2)                          # 18.13
OCC = 1.67
LANES = 2
WASHOUT_LEN_M = 50.0
PAVE = {'inundated_short': (3e3, 15e3), 'inundated_long': (60e3, 150e3), 'washout': (0.5e6, 1.4e6)}   # 2023 $ per lane-km
_k = CPI[2023] / CPI[2014]
CULVERT = [(1.2, 'pipe < 1.2 m', (15e3 * _k, 85e3 * _k)), (1.8, 'box 1.2-1.8 m', (205e3 * _k, 280e3 * _k)), (3.7, 'box 1.8-3.7 m', (280e3 * _k, 405e3 * _k)),
           (7.0, 'short bridge 3.7-7 m', (430e3 * _k, 1.0e6 * _k)), (1e9, 'bridge > 7 m', (1.0e6 * _k, 2.0e6 * _k))]
CULVERT_UNKNOWN = ('size unknown', (15e3 * _k, 405e3 * _k))
L_BANDS = [0.1, 0.3, 0.5, 0.9]
C_USD = [50e3, 250e3, 1e6, 5e6]
C_KM = [0.0, 2.0, 10.0, 40.0]
SIGMA_M = 0.10
SOURCES = dict(
    vot='USDOT (2016) Revised Departmental Guidance on Valuation of Travel Time in Economic Analysis, Table 4: local travel, all purposes $14.10 / person-hour (2015 $)',
    cpi='US Bureau of Labor Statistics CPI-U, US city average, annual average: 2014 236.736, 2015 237.017, 2023 304.702',
    occupancy='FHWA (2018) Summary of Travel Trends: 2017 National Household Travel Survey, vehicle occupancy 1.67 persons per vehicle (all trips); as used in USDOT Benefit-Cost Analysis Guidance',
    vtrans='Vermont Agency of Transportation (2014) State and Local Highway Unmet Needs (Tropical Storm Irene, NDRC application), Tables 1-3: box culverts 4x3-6x5 ft $205k-$280k, '
           '10x5 ft $405k, short bridges 14x7-22x8 ft $430k-$1.0M, town culverts 3-4 ft $15k-$85k; roadway slope / bank armoring ~$1.7M per mile',
    ma_standards='Massachusetts River and Stream Crossing Standards (2011, MassDEP / UMass / TNC): new and replacement crossings span >= 1.2 x bankfull width',
    neefc='New England Environmental Finance Center (2010) Culvert Material Cost Comparison, Univ. of Southern Maine (pipe material is a small part of a replacement; not applied)',
    massdot='MassDOT (2023) Price adjustment period prices: liquid asphalt $625-$665 per ton (Jan-Dec 2023)',
    gaspard='Gaspard K., Martinez M., Zhang Z., Wu Z. (2007) Impact of Hurricane Katrina on roadways in the New Orleans area. Louisiana Transportation Research Center, Technical Assistance Report 07-2TA',
    jenelius='Jenelius E., Petersen T., Mattsson L.-G. (2006) Importance and exposure in road network vulnerability analysis. Transportation Research Part A 40(7), 537-560',
    iso31000='AS/NZS ISO 31000:2009 Risk management (5 x 5 likelihood-consequence matrix as commonly applied; bands Low / Medium / High / Extreme)')


def phi(x):
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def gmean(lo, hi):
    return math.sqrt(lo * hi)


def band(v, edges):
    for k, e in enumerate(edges):
        if v < e or (edges is C_KM and v <= e): return k + 1
    return len(edges) + 1


def risk_class(score):
    return 'Low' if score <= 4 else 'Medium' if score <= 9 else 'High' if score <= 16 else 'Extreme'


def culvert_cost(span_m, bf_w):
    need = max([v for v in (span_m, 1.2 * bf_w if bf_w else None) if v] or [0])
    if not need: return CULVERT_UNKNOWN[0], CULVERT_UNKNOWN[1], None
    for top, lab, rng in CULVERT:
        if need < top: return lab, rng, round(need, 2)


def pavement_cost(p, washout):
    L = (p.get('length_m') or 0) / 1000.0; hrs = float(p.get('hours_over_30cm') or 0)
    key = 'inundated_long' if hrs >= 24 else 'inundated_short'
    lo, hi = PAVE[key]; lo, hi = lo * LANES * L, hi * LANES * L
    if washout:
        lw = min(L, WASHOUT_LEN_M / 1000.0); wl, wh = PAVE['washout']; lo += wl * LANES * lw; hi += wh * LANES * lw; key = 'washout + ' + key
    return key, lo, hi


def access_importance(S, inbox, segs, facilities):
    """Road-km in the box losing access within the standard (any of hospital / fire / police) when segment i alone is closed (dry network)."""
    net = RS.Net(S); geom = RS.seg_geometry(S); fac = json.load(open(facilities))['facilities'] if facilities and os.path.exists(facilities) else {}
    FS = RS.snap_facilities(fac, geom); lw = net.len_m / 1000.0; one = np.ones(net.n); G0 = net.graph(one)
    ok0 = {s: RS.access_minutes(net, G0, FS[s]) <= RS.ACCESS_MIN[s] for s in RS.ACCESS_MIN}
    out = {}
    for i in segs:
        m = one.copy(); m[i] = np.inf; G = net.graph(m); lost = np.zeros(net.n, bool); per = {}
        for s in RS.ACCESS_MIN:
            src = [j for j in FS[s] if j != i]; ok = RS.access_minutes(net, G, src) <= RS.ACCESS_MIN[s]
            l = inbox & ok0[s] & ~ok; l[i] = False; per[s] = round(float(lw[l].sum()), 2); lost |= l
        out[int(i)] = (round(float(lw[lost].sum()), 2), per)
    return out


def crossings_from_run(run_dir, S, Xrows, meta):
    """Crossing status (impacts.py) and P(overtop) for crossings in the run box; the prototype's culvert rule where it applies."""
    R = IM.load_run(os.path.basename(run_dir.rstrip('/')), local=run_dir)
    # as proto/prototype.py: road points over water cells or within 30 m of an NBI bridge read the river, not the deck -> dropped
    wmp = os.path.join(run_dir, 'watermask.npy'); WM = np.load(wmp).astype(bool) if os.path.exists(wmp) else None
    bx = by = []; nbi = os.environ.get('PROTO_NBI') or os.path.join(ROOT, 'docs', 'network', 'nbi_ma.json')
    if os.path.exists(nbi):
        from pyproj import Transformer
        NB = json.load(open(nbi)); c = NB['columns']; il, ia, ic = c.index('lon'), c.index('lat'), c.index('culvert'); rb = [r for r in NB['rows'] if not r[ic]]
        bx, by = Transformer.from_crs(4326, 26986, always_xy=True).transform([r[il] for r in rb], [r[ia] for r in rb])
    orig = IM.road_points
    def no_bridges(S_, meta_, step=None):
        P_ = orig(S_, meta_, step)
        if not len(P_['x']): return P_
        keep = np.ones(len(P_['x']), bool)
        if WM is not None and WM.shape == tuple(meta_['shape']): keep &= ~WM[P_['r'], P_['c']]
        if len(bx):
            from scipy.spatial import cKDTree
            d_, _ = cKDTree(np.column_stack([bx, by])).query(np.column_stack([P_['x'], P_['y']])); keep &= d_ > 30
        return {k: v[keep] for k, v in P_.items()}
    IM.road_points = no_bridges
    try: imp, _ = IM.analyse([R], S, Xrows, None, None)
    finally: IM.road_points = orig
    XC = imp['crossing_columns']; xs = [dict(zip(XC, r)) for r in imp['crossings']]
    cp = {}
    try:                                   # prototype's culvert rule (NAACC barrel + modelled flow, xings.json from LF_QOUT=1)
        import prototype as PT
        xj = json.load(open(os.path.join(run_dir, 'xings.json'))) if os.path.exists(os.path.join(run_dir, 'xings.json')) else {}
        xq = {c['id']: c for c in xj.get('crossings', []) if c.get('q_peak_m3s') is not None}
        cp = {c['id']: c for c in PT.culvert_probability(Xrows, xq, {x['id']: x for x in xs}, R['meta'], True)}
    except Exception as e:
        print('  culvert rule unavailable:', repr(e)[:120])
    byid = {r['id']: r for r in Xrows}
    out = []
    for x in xs:
        row = byid.get(x['id'], {})
        if x['id'] in cp: p = cp[x['id']]['p']; how = 'culvert rule: ' + cp[x['id']].get('basis', '')
        elif x.get('hw_m') is not None and x.get('crest_m') is not None: p = phi((x['hw_m'] - x['crest_m']) / SIGMA_M); how = 'modelled headwater vs crest'
        elif x.get('road_depth_m') is not None: p = phi((x['road_depth_m'] - 0.15) / SIGMA_M); how = 'water on the road within 30 m'
        else: p = 0.0; how = 'no data'
        out.append(dict(x, p_overtop=round(p, 3), p_basis=how, bf_w=row.get('bf_w'), naacc=row.get('naacc'), condition=row.get('condition'), span_req=None))
    return out


def run(out, run_dir=None, segments=None, crossings=None, facilities=None, top=50, png=True):
    t_start = time.time()
    segments = segments or os.path.join(ROOT, 'docs', 'graph_segments.json'); facilities = facilities or os.path.join(ROOT, 'docs', 'network', 'facilities.json')
    summ = json.load(open(os.path.join(out, 'summary.json'))); GJ = json.load(open(os.path.join(out, 'segments.geojson')))
    S = json.load(open(segments)); box = summ['box_epsg26986']; res = summ['resolution_m']
    meta = dict(box=box, res_m=res, shape=[int(round((box[3] - box[1]) / res)), int(round((box[2] - box[0]) / res))])
    P = IM.road_points(S, meta); inbox = np.bincount(P['seg'], minlength=S['n']) > 0
    feats = {int(f['properties']['segment']): f['properties'] for f in GJ['features']}
    vhd = {}
    rp = os.path.join(out, 'resilience_segments.csv')
    if os.path.exists(rp):
        for r in csv.DictReader(open(rp)): vhd[int(r['segment'])] = float(r['vehicle_hours_detour']) + float(r['vehicle_hours_slow'])
    else: print('  no resilience_segments.csv: run proto/resilience.py first for the delay cost')
    segs = [i for i, p in feats.items() if float(p.get('p_close') or 0) >= 0.1]
    # crossings
    X = []
    if run_dir and os.path.exists(os.path.join(run_dir, 'hmax.npy')):
        Xrows, _ = IM.load_crossings(crossings); X = [x for x in crossings_from_run(run_dir, S, Xrows, meta) if x['status'] in ('overtopped', 'surcharged') or (x['p_basis'].startswith('culvert rule') and x['p_overtop'] >= 0.1)]
    # segment carried by each crossing (nearest road point within 30 m) and washout flags
    from scipy.spatial import cKDTree
    from pyproj import Transformer
    tr = Transformer.from_crs(4326, 26986, always_xy=True); carry = {}; washout = set()
    if X and len(P['x']):
        t = cKDTree(np.column_stack([P['x'], P['y']])); xx, yy = tr.transform([x['lon'] for x in X], [x['lat'] for x in X])
        for x, a, b in zip(X, xx, yy):
            d, k = t.query([a, b]); carry[x['id']] = int(P['seg'][k]) if d <= 30 else None
            if x['status'] == 'overtopped' or x['p_overtop'] >= 0.5:
                for s in np.unique(P['seg'][t.query_ball_point([a, b], 30.0)]): washout.add(int(s))
    imp_segs = sorted(set(segs) | {s for s in carry.values() if s is not None})
    acc = access_importance(S, inbox, imp_segs, facilities)
    items = []
    for i in segs:
        p = feats[i]; pc = float(p['p_close']); wo = (i in washout and pc >= 0.5) or float(p.get('p_washout') or 0) >= 0.5
        kind, lo, hi = pavement_cost(p, wo); vh = vhd.get(i, 0.0); dc = vh * OCC * VOT
        km, per = acc.get(i, (0.0, {}))
        items.append(dict(type='segment', id=str(i), road=p.get('road') or '', town=p.get('town') or '', detail=f"{p.get('road_class')}, AADT {p.get('aadt')}, {p.get('length_m')} m, {kind}",
                          likelihood=pc, repair_low=lo, repair_high=hi, delay_vehicle_hours=vh, delay_usd=dc, access_km_lost=km, access_detail=per))
    for x in X:
        lab, (lo, hi), need = culvert_cost(x.get('span_m'), x.get('bf_w'))
        s = carry.get(x['id']); km, per = acc.get(s, (0.0, {})) if s is not None else (0.0, {})
        size = f"span {x['span_m']} m" if x.get('span_m') else 'span unknown'
        items.append(dict(type='crossing', id=str(x['id']), road=x.get('road') or '', town='', detail=f"{x['status']} ({x.get('basis') or x['p_basis']}), {size}, bankfull {x.get('bf_w')} m, "
                          f"replace as {lab}" + (f" (required span {need} m)" if need else '') + (f", NAACC condition {x['condition']}" if x.get('condition') else ''),
                          likelihood=float(x['p_overtop']), repair_low=lo, repair_high=hi, delay_vehicle_hours=0.0, delay_usd=0.0, access_km_lost=km, access_detail=per,
                          carried_segment=s, stream=x.get('stream')))
    for it in items:
        it['consequence_low'] = it['repair_low'] + it['delay_usd']; it['consequence_high'] = it['repair_high'] + it['delay_usd']
        it['consequence_mid'] = gmean(it['repair_low'], it['repair_high']) + it['delay_usd'] if it['repair_low'] > 0 else it['delay_usd']
        it['L'] = band(it['likelihood'], L_BANDS); cu = band(it['consequence_mid'], C_USD); ca = band(it['access_km_lost'], C_KM)
        it['C'] = max(cu, ca); it['C_driver'] = 'cost' if cu >= ca else 'critical access'
        it['score'] = it['L'] * it['C']; it['risk'] = risk_class(it['score']); it['expected_cost'] = it['likelihood'] * it['consequence_mid']
    items.sort(key=lambda r: (-r['score'], -r['expected_cost']))
    cols = ['rank', 'risk', 'score', 'L', 'C', 'C_driver', 'type', 'id', 'road', 'town', 'likelihood', 'expected_cost_usd', 'consequence_mid_usd', 'consequence_low_usd',
            'consequence_high_usd', 'repair_low_usd', 'repair_high_usd', 'delay_vehicle_hours', 'delay_usd', 'access_km_lost', 'detail']
    with open(os.path.join(out, 'risk_matrix.csv'), 'w', newline='') as fh:
        w = csv.writer(fh); w.writerow(cols)
        for k, it in enumerate(items[:top]):
            w.writerow([k + 1, it['risk'], it['score'], it['L'], it['C'], it['C_driver'], it['type'], it['id'], it['road'], it['town'], round(it['likelihood'], 3),
                        round(it['expected_cost'], -2), round(it['consequence_mid'], -2), round(it['consequence_low'], -2), round(it['consequence_high'], -2),
                        round(it['repair_low'], -2), round(it['repair_high'], -2), round(it['delay_vehicle_hours'], 1), round(it['delay_usd'], -2), it['access_km_lost'], it['detail']])
    grid = [[0] * 5 for _ in range(5)]; gridx = [[0] * 5 for _ in range(5)]
    for it in items: (grid if it['type'] == 'segment' else gridx)[it['L'] - 1][it['C'] - 1] += 1
    cnt = {c: dict(segments=sum(1 for it in items if it['risk'] == c and it['type'] == 'segment'), crossings=sum(1 for it in items if it['risk'] == c and it['type'] == 'crossing'))
           for c in ('Extreme', 'High', 'Medium', 'Low')}
    tot = lambda key, typ=None: round(sum(it[key] * (1 if key != 'exp' else 1) for it in items if typ is None or it['type'] == typ), -3)
    res = dict(run=summ.get('run'), made=time.strftime('%Y-%m-%d %H:%M'), items=len(items), segments=len(segs), crossings=len(X), classes=cnt,
               grid_segments_L_by_C=grid, grid_crossings_L_by_C=gridx,
               totals_usd=dict(expected=round(sum(it['expected_cost'] for it in items), -3),
                               repair_low=round(sum(it['repair_low'] for it in items), -3), repair_high=round(sum(it['repair_high'] for it in items), -3),
                               repair_low_segments=round(sum(it['repair_low'] for it in items if it['type'] == 'segment'), -3),
                               repair_high_segments=round(sum(it['repair_high'] for it in items if it['type'] == 'segment'), -3),
                               repair_low_crossings=round(sum(it['repair_low'] for it in items if it['type'] == 'crossing'), -3),
                               repair_high_crossings=round(sum(it['repair_high'] for it in items if it['type'] == 'crossing'), -3),
                               delay=round(sum(it['delay_usd'] for it in items), -3), delay_vehicle_hours=round(sum(it['delay_vehicle_hours'] for it in items))),
               top10=[{k: (round(v, 3) if isinstance(v, float) else v) for k, v in it.items() if k not in ('access_detail',)} for it in items[:10]],
               unit_costs=dict(dollar_year=2023, vot_usd_per_person_h=VOT, occupancy=OCC, lanes=LANES, washout_length_m=WASHOUT_LEN_M,
                               pavement_usd_per_lane_km=PAVE, culvert_usd={lab: [round(a, -3), round(b, -3)] for _, lab, (a, b) in CULVERT} | {CULVERT_UNKNOWN[0]: [round(CULVERT_UNKNOWN[1][0], -3), round(CULVERT_UNKNOWN[1][1], -3)]}),
               classes_def=dict(likelihood=L_BANDS, consequence_usd=C_USD, consequence_access_km=C_KM, risk='L x C: Low 1-4, Medium 5-9, High 10-16, Extreme 20-25'),
               caveats=['Order-of-magnitude costs from public unit-cost tables (2014 Vermont, CPI-adjusted); not engineer\'s estimates.',
                        'Crossing replacement is the consequence if the crossing fails; overtopping does not mean failure.',
                        'Delay uses AADT/24 with no traffic assignment; 75 % of local AADT are 1,000 vpd defaults.',
                        'Likelihood is the physics prior p_close (and P(overtop)), not a calibrated failure probability.'],
               sources=SOURCES, runtime_s=round(time.time() - t_start, 1))
    json.dump(res, open(os.path.join(out, 'risk.json'), 'w'), indent=1)
    if png: plot(os.path.join(out, 'risk_matrix.png'), items, grid, gridx)
    print(json.dumps({k: res[k] for k in ('items', 'segments', 'crossings', 'classes', 'totals_usd')}, indent=1))
    return res


def plot(path, items, grid, gridx):
    import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
    col = {'Low': '#d9ead3', 'Medium': '#fff2cc', 'High': '#f9cb9c', 'Extreme': '#e06666'}
    fig, ax = plt.subplots(figsize=(7.2, 5.6), dpi=130)
    for L in range(1, 6):
        for C in range(1, 6):
            ax.add_patch(plt.Rectangle((C - 0.5, L - 0.5), 1, 1, color=col[risk_class(L * C)], ec='white', lw=2))
            s, x = grid[L - 1][C - 1], gridx[L - 1][C - 1]
            if s or x: ax.text(C, L, (f'{s} seg' if s else '') + ('\n' if s and x else '') + (f'{x} xing' if x else ''), ha='center', va='center', fontsize=9)
    ax.set_xlim(0.5, 5.5); ax.set_ylim(0.5, 5.5); ax.set_xticks(range(1, 6)); ax.set_yticks(range(1, 6))
    ax.set_xticklabels(['C1\n<\\$50k', 'C2\n<\\$250k', 'C3\n<\\$1M', 'C4\n<\\$5M', 'C5\n≥\\$5M'], fontsize=8)
    ax.set_yticklabels(['L1 p<0.1', 'L2 0.1-0.3', 'L3 0.3-0.5', 'L4 0.5-0.9', 'L5 ≥0.9'], fontsize=8)
    ax.set_xlabel('consequence: repair + user delay (2023 \\$), or critical access lost (km)', fontsize=9); ax.set_ylabel('likelihood: p_close / P(overtop)', fontsize=9)
    top = [it for it in items if it['risk'] == 'Extreme'][:5] or items[:5]
    txt = '\n'.join(f"{k + 1}. {it['road'] or it['type']} {('(' + it['town'] + ')') if it['town'] else ''}: \\${it['consequence_mid'] / 1e6:.1f}M, p {it['likelihood']:.2f}" for k, it in enumerate(top))
    ax.set_title('Risk matrix, flagged road segments and stream crossings (order of magnitude)', fontsize=10)
    fig.text(0.01, 0.005, 'Top: ' + txt.replace('\n', '; '), fontsize=6.5, wrap=True)
    fig.tight_layout(rect=(0, 0.06, 1, 1)); fig.savefig(path); plt.close(fig)


def selftest():
    ok = True
    def check(name, cond, det=''):
        nonlocal ok; ok &= bool(cond); print(('ok   ' if cond else 'FAIL ') + name, '' if cond else det)
    check('VOT 2015 -> 2023', abs(VOT - 18.13) < 0.01, VOT)
    lab, rng, need = culvert_cost(0.9, 2.0); check('MA standard upsizes to 1.2 x bankfull (2.4 m box)', lab == 'box 1.8-3.7 m' and need == 2.4, (lab, need))
    lab, rng, need = culvert_cost(None, None); check('unknown size range', lab == 'size unknown')
    k, lo, hi = pavement_cost(dict(length_m=1000, hours_over_30cm=30), False); check('long inundation 1 km x 2 lanes', k == 'inundated_long' and lo == 120e3 and hi == 300e3, (k, lo, hi))
    k, lo, hi = pavement_cost(dict(length_m=200, hours_over_30cm=2), True); check('washout over 50 m', k.startswith('washout') and abs(lo - (3e3 * 2 * 0.2 + 0.5e6 * 2 * 0.05)) < 1, (k, lo))
    check('bands', band(0.95, L_BANDS) == 5 and band(0.05, L_BANDS) == 1 and band(0.0, C_KM) == 1 and band(1.5, C_KM) == 2 and band(6e6, C_USD) == 5)
    check('classes', risk_class(25) == 'Extreme' and risk_class(16) == 'High' and risk_class(9) == 'Medium' and risk_class(4) == 'Low')
    print('risk selftest', 'OK' if ok else 'FAILED'); return ok


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--out'); ap.add_argument('--run-dir', help='LISFLOOD-FP run dir (hmax.npy, z.npy, meta.json, xings.json) for crossing status')
    ap.add_argument('--segments', default=os.path.join(ROOT, 'docs', 'graph_segments.json'))
    ap.add_argument('--crossings', default=os.path.join(ROOT, 'docs', 'network', 'crossings_all.json'))
    ap.add_argument('--facilities', default=os.path.join(ROOT, 'docs', 'network', 'facilities.json'))
    ap.add_argument('--top', type=int, default=50); ap.add_argument('--selftest', action='store_true')
    a = ap.parse_args()
    if a.selftest: sys.exit(0 if selftest() else 1)
    run(a.out, a.run_dir, a.segments, a.crossings, a.facilities, a.top)
