"""Road-closure prototype: rain -> flood depth -> which road segments close, why, and what it costs the network.

    python proto/prototype.py --run-dir <LISFLOOD-FP output dir> --out <dir>      # after sim/colab/w9_lisflood.py
    python proto/prototype.py --selftest                                          # offline, synthetic storm

Inputs (all produced or kept in this repo):
  run dir      hmax.npy (peak depth, m), z.npy, meta.json (box, res_m, t0), timing.npz (hours >= 15 / 30 cm, first arrival of 30 cm),
               rainstats.npz (storm total, peak 1 h and 3 h rain per cell, MRMS)      <- sim/colab/w9_lisflood.py (LISFLOOD-FP 8.2)
  roads        docs/graph_segments.json (road segments with class, town, AADT, links)
  crossings    docs/network/crossings_all.json (road-stream crossings; FHWA HDS-5 capacity in sim/infra/culvert.py)
  hospitals    docs/network/facilities.json
  checks       docs/prone/flood_reports.json (NWS / Storm Events / crash-report flood points with dates),
               proto/data/massdot_repeat_flood_d3.csv (MassDOT District 3 repeating flood areas, no dates)

Steps:
  1. hazard per segment: peak depth along the segment, hours with >= 30 cm, when 30 cm first arrives
  2. flashness per segment: storm total, peak 1-hour and 3-hour rain, share of the storm in its worst hour
  3. closure probability v0: P = Phi((peak depth - 0.30 m) / sigma), sigma = 0.10 m depth uncertainty (to be calibrated against
     USGS high-water marks); 0.30 m = depth at which an ordinary car stops (Pregnolato et al. 2017; Shand et al. 2011).
     This is the physics prior; the learned H-V-C (labels from storms) replaces it in the dissertation.
  4. network consequence (sim/infra/impacts.py): segments >= 15 cm removed; minutes added to the nearest hospital, areas cut off;
     culverts overtopped (HDS-5 headwater vs crest)
  5. outputs: segments.geojson, watchlist.csv (top segments with a plain-language reason), map.html (layers by road class),
     figure.png, summary.json, REPORT.md
"""
import os, sys, json, math, csv, argparse, time
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.normpath(os.path.join(HERE, '..'))
sys.path.insert(0, os.path.join(ROOT, 'sim', 'infra'))
import impacts as IM
import culvert as CV

FAIL_M = 0.30          # closure depth (ordinary car stops)
SIGMA_M = 0.10         # depth uncertainty for the v0 probability
CLASS_NAME = {0: 'local / collector', 1: 'arterial', 2: 'highway'}
CULVERT_SHAPES = ('circular', 'elliptical', 'pipe_arch', 'box', 'arch_open', 'arch_closed')
# NAACC culvert-condition inlet blockage -> share of the barrel area lost to debris / sediment.  Design blockage factors of this size are what
# Australian Rainfall and Runoff 2019 (Book 6 ch. 6, Weeks et al. 2013 / Ball et al. 2019) prescribes for small culverts with debris
# supply (25-50 %, up to 100 % for openings < 1.5 m); here 'Poor' = partial (25 %), 'Critical' = severe (50 %).  Applied as an equal loss of
# capacity: HW_blocked(Q) = HW_clear(Q / (1 - B)).  Structural condition (NAACC 'Poor') is not used: no published fragility links it to
# overtopping in a single storm.
BLOCKAGE = {'Poor': 0.25, 'Critical': 0.50}
XING_SEG_M = 30.0      # a crossing closes the road segments with a road point within this distance
Q_SIGMA_LN = 0.30      # sd of ln(peak flow) at a crossing (~ +-35 %): the culvert probability is P(Q' > Q_crest), Q' lognormal about the modelled Q
LABEL_GROUPS = {'all': None, 'flood_closure': ('flooded', 'closed', 'impassable'),
                'culvert_washout': ('culvert_failure', 'washout', 'sinkhole', 'bridge_damage'), 'other_damage': ('other_damage',)}


def phi(x):
    return 0.5 * (1.0 + np.vectorize(math.erf)(x / math.sqrt(2.0)))


def load_npz(path):
    if not os.path.exists(path): return None
    with np.load(path) as d: return {k: d[k] for k in d.files}


def seg_reduce(n, seg, vals, how):
    out = np.full(n, np.nan if how == 'min' else 0.0, np.float32)
    if how == 'max': np.maximum.at(out, seg, vals)
    elif how == 'min':
        v = np.where(np.isnan(vals), np.inf, vals); o = np.full(n, np.inf, np.float32); np.minimum.at(o, seg, v); out = np.where(np.isinf(o), np.nan, o)
    return out


def seg_top2(n, seg, vals):
    """Second-highest value per segment (the highest when a segment has one point): one wet pixel cannot close a road."""
    o = np.lexsort((-vals, seg)); sg = seg[o]; v = vals[o]
    first = np.r_[True, sg[1:] != sg[:-1]]; idx = np.nonzero(first)[0]
    out = np.zeros(n, np.float32); top1 = v[idx]; has2 = np.r_[idx[1:], len(sg)] - idx >= 2
    sec = np.where(has2, v[np.minimum(idx + 1, len(v) - 1)], top1); out[sg[idx]] = sec; return out


def culvert_probability(Xrows, xq, imp_x, meta, blockage=True):
    """Probability that the road over each surveyed culvert is overtopped, P_c = P(HW > crest).
    HW: FHWA HDS-5 headwater (sim/infra/culvert.py, max of inlet and outlet control) for the peak flow Q the flood model passed through the
    crossing's notch (xings.json, LF_QOUT=1), with the NAACC barrel (shape, span, rise, material, inlet, barrels, slope, length) and the
    NAACC inlet blockage (BLOCKAGE).  crest: road crest above the invert = rise + NAACC fill (0.6 m when fill is missing, as impacts.py).
    HW rises monotonically with Q, so HW > crest exactly when Q > Q_crest (the flow the barrel passes at HW = crest, HDS-5 inverted), and
    with the flow uncertain by a lognormal factor (sd Q_SIGMA_LN): P_c = Phi(ln(Q / Q_crest) / Q_SIGMA_LN).  (Phi((HW - crest)/sigma_HW)
    with a fixed sigma_HW saturates badly: HDS-5 headwater grows ~Q^2 once the inlet is submerged.)  Without a modelled flow the modelled
    depth at the crossing's channel cell (impacts.py hw_m) stands in for HW: P_c = Phi((HW - crest) / 0.10).  Returns a list of dicts."""
    from pyproj import Transformer
    tr = Transformer.from_crs(4326, 26986, always_xy=True); x0, y0, x1, y1 = meta['box']; out = []
    for row in Xrows:
        shape, rise, span = row.get('shape'), row.get('rise_m'), row.get('span_m')
        if row.get('lon') is None or shape not in CULVERT_SHAPES or not rise or rise <= 0 or (shape != 'circular' and not span): continue
        x, y = tr.transform(row['lon'], row['lat'])
        if not (x0 <= x < x1 and y0 <= y < y1): continue
        fill = row.get('fill_m'); crest = float(rise) + (float(fill) if fill is not None else 0.6)
        B = BLOCKAGE.get(row.get('inlet_blockage'), 0.0) if blockage else 0.0
        q = (xq.get(row.get('id')) or {}).get('q_peak_m3s'); rec = dict(id=row.get('id'), road=row.get('road'), stream=row.get('stream'), x=x, y=y, crest_m=round(crest, 2),
                                                                         blockage=B, q_m3s=q)
        if q is not None:
            mat, inl, nb = row.get('material') or 'concrete', row.get('inlet') or 'headwall', int(row.get('n_barrels') or 1)
            S = (row.get('slope_pct') or 1.0) / 100.0; L = row.get('length_m') or max(10.0, 2 * crest + 8.0)
            HW = CV.headwater(q / (1.0 - B), shape, span or rise, rise, mat, inl, S, L, 0.0, nb)['hw'] if q > 0 else 0.0
            qc = CV.q_at_headwater(crest, shape, span or rise, rise, mat, inl, S, L, 0.0, nb) * (1.0 - B)
            z = math.log(max(q, 1e-6) / max(qc, 1e-6)) / Q_SIGMA_LN
            rec.update(hw_m=round(HW, 2), q_crest_m3s=round(qc, 3), basis='HDS-5 headwater at the modelled peak flow')
        else:
            a = imp_x.get(row.get('id'))
            if not a or a.get('hw_m') is None: continue
            HW = float(a['hw_m']); z = (HW - crest) / SIGMA_M; rec.update(hw_m=round(HW, 2), basis='modelled depth at the crossing')
        rec['p'] = float(phi(np.array([z]))[0]); out.append(rec)
    return out


def load_labels(path):
    if not path or not os.path.exists(path): return []
    L = []
    for r in csv.DictReader(open(path)):
        try: L.append(dict(r, lon=float(r['lon']), lat=float(r['lat'])))
        except Exception: continue
    return L


def norm_road(s):
    s = (s or '').lower().replace('.', '').strip()
    for a, b in ((' street', ' st'), (' avenue', ' ave'), (' road', ' rd'), (' drive', ' dr'), (' boulevard', ' blvd'), ('route ', 'rt '), ('state rte ', 'rt '), ('rte ', 'rt ')):
        s = s.replace(a, b)
    return s


def label_segments(labels, Q, props, meta, strict=True):
    """Road segments each documented site refers to (town-level coordinates skipped).  strict: segments with a road point within 30 m of the
    site (in effect the segment it sits on).  loose: exact coordinates within 100 m; approx within 300 m plus, when the road is named,
    segments of that name within 1.5 km (the labels README warns road-centroid points can be 0.5-1.5 km off)."""
    from scipy.spatial import cKDTree
    from pyproj import Transformer
    if not labels or not len(Q['x']): return []
    tr = Transformer.from_crs(4326, 26986, always_xy=True); x0, y0, x1, y1 = meta['box']; t = cKDTree(np.column_stack([Q['x'], Q['y']])); out = []
    nm = np.array([norm_road(v) for v in props['road']], dtype=object)
    for L in labels:
        q = L.get('coord_quality', 'approx')
        if q == 'town': continue
        x, y = tr.transform(L['lon'], L['lat'])
        if not (x0 <= x < x1 and y0 <= y < y1): continue
        segs = set(np.unique(Q['seg'][t.query_ball_point([x, y], 30.0 if strict else 100.0 if q == 'exact' else 300.0)]).tolist())
        if not strict and q != 'exact' and L.get('road'):
            names = {norm_road(v) for v in L['road'].replace(')', '(').split('(') if v.strip()}
            cand = np.unique(Q['seg'][t.query_ball_point([x, y], 1500.0)])
            segs |= {int(sg) for sg in cand if nm[sg] in names}
        if segs: out.append((L, np.array(sorted(segs), int)))
    return out


def label_recall(matches, P, inbox, thr=0.5):
    """Segment-level recall of documented sites at P >= thr, the share of all in-box segments flagged, and two lifts: recall / flagged share
    (naive) and recall / the recall random flagging of the same share would get given how many segments each site matches (chance-corrected)."""
    fl = (P >= thr) & inbox; f = float(fl[inbox].mean()) if inbox.any() else 0.0; res = dict(flagged_share=round(f, 4), n_flagged=int(fl.sum()))
    for g, types in LABEL_GROUPS.items():
        M = [m for m in matches if types is None or m[0].get('type') in types]
        if not M: continue
        hit = np.array([fl[s].any() for _, s in M]); exp_ = np.array([1 - (1 - f) ** len(s) for _, s in M])
        res[g] = dict(n=len(M), recall=round(float(hit.mean()), 3), random_recall=round(float(exp_.mean()), 3),
                      lift_naive=round(float(hit.mean() / f), 2) if f > 0 else None, lift=round(float(hit.mean() / exp_.mean()), 2) if exp_.mean() > 0 else None)
    return res


def reason(r):
    bits = [f"{r['peak_depth_m']:.2f} m of water at peak"]
    if r['hours_over_30cm'] > 0: bits.append(f"over 30 cm for {r['hours_over_30cm']:.1f} h")
    if r['arrival_h'] is not None: bits.append(f"30 cm reached {r['arrival_h']:.1f} h into the storm")
    bits.append(f"worst hour {r['peak1h_mm']:.0f} mm ({r['flashness_pct']:.0f}% of the storm)")
    if r.get('p_culvert', 0) >= 0.1 and r.get('culvert_why'): bits.append(r['culvert_why'])
    elif r['culvert_overtopped_nearby']: bits.append('a culvert within 100 m is overtopped')
    if r['adds_hospital_min'] and r['adds_hospital_min'] >= 5: bits.append(f"+{r['adds_hospital_min']:.0f} min to the nearest hospital")
    if r['cut_off_hospital']: bits.append('cut off from hospitals')
    return '; '.join(bits)


def run(run_dir, out, segments, crossings, reports, facilities, repeat_csv, top=30, culvert_rule=False, labels_csv=None, blockage=True):
    t_start = time.time(); os.makedirs(out, exist_ok=True)
    R = IM.load_run(os.path.basename(run_dir.rstrip('/')), local=run_dir); meta = R['meta']; H = R['H']; res = meta['res_m']
    R['name'] = meta.get('run') or R['name']
    T = load_npz(os.path.join(run_dir, 'timing.npz')); RS = load_npz(os.path.join(run_dir, 'rainstats.npz'))
    S = json.load(open(segments)); n = S['n']; props = S['props']
    Xrows, xsrc = IM.load_crossings(crossings)
    rep = json.load(open(reports)) if reports and os.path.exists(reports) else None
    fac = json.load(open(facilities))['facilities']['hospital'] if facilities and os.path.exists(facilities) else None

    # roads over rivers: lidar bare earth removes bridge decks, so a road point over a channel/water cell or within 30 m of an NBI bridge
    # reads the river depth, not the road.  Drop those points (the roadway there is the deck).
    WM = np.load(os.path.join(run_dir, 'watermask.npy')).astype(bool) if os.path.exists(os.path.join(run_dir, 'watermask.npy')) else None
    bx, by = [], []
    nbi_p = os.path.join(ROOT, 'docs', 'network', 'nbi_ma.json')
    if os.path.exists(nbi_p):
        from pyproj import Transformer as _T
        NB = json.load(open(nbi_p)); c = NB['columns']; il, ia, ic = c.index('lon'), c.index('lat'), c.index('culvert')
        rows_b = [r_ for r_ in NB['rows'] if not r_[ic]]
        bx, by = _T.from_crs(4326, 26986, always_xy=True).transform([r_[il] for r_ in rows_b], [r_[ia] for r_ in rows_b])
    _orig_rp = IM.road_points
    def road_points_no_bridges(S_, meta_, step=None):
        P_ = _orig_rp(S_, meta_, step)
        if not len(P_['x']): return P_
        keep_ = np.ones(len(P_['x']), bool)
        if WM is not None and WM.shape == tuple(meta_['shape']): keep_ &= ~WM[P_['r'], P_['c']]
        if len(bx):
            from scipy.spatial import cKDTree as _K
            d_, _ = _K(np.column_stack([bx, by])).query(np.column_stack([P_['x'], P_['y']])); keep_ &= d_ > 30
        return {k: v[keep_] for k, v in P_.items()}
    IM.road_points = road_points_no_bridges

    # 4 first: the existing impacts layer (depth classes, network, crossings, report scores)
    imp, _ = IM.analyse([R], S, Xrows, rep, fac)
    seg_cols = imp['seg_columns']; net = {row[0]: dict(zip(seg_cols, row)) for row in imp['seg_rows']}

    # 1-2 hazard and flashness along every segment (same densified points as impacts)
    P = IM.road_points(S, meta); mx, mean, dv, inbox = IM.sample_segments(n, P, H, R['V'])
    use0 = ~P['end'] | (np.bincount(P['seg'][~P['end']], minlength=n)[P['seg']] == 0)
    mx = np.where(inbox, seg_top2(n, P['seg'][use0], H[P['r'][use0], P['c'][use0]]), 0).astype(np.float32)
    use = ~P['end'] | (np.bincount(P['seg'][~P['end']], minlength=n)[P['seg']] == 0); Q = {k: v[use] for k, v in P.items()}
    hrs30 = seg_reduce(n, Q['seg'], T['tover30'][Q['r'], Q['c']], 'max') if T else np.zeros(n, np.float32)
    hrs15 = seg_reduce(n, Q['seg'], T['tover15'][Q['r'], Q['c']], 'max') if T else np.zeros(n, np.float32)
    arr30 = seg_reduce(n, Q['seg'], T['tarr30'][Q['r'], Q['c']], 'min') if T else np.full(n, np.nan, np.float32)
    if RS:
        tot = seg_reduce(n, Q['seg'], RS['total'][Q['r'], Q['c']], 'max'); p1 = seg_reduce(n, Q['seg'], RS['peak1h'][Q['r'], Q['c']], 'max')
        p3 = seg_reduce(n, Q['seg'], RS['peak3h'][Q['r'], Q['c']], 'max')
    else:
        tot = p1 = p3 = np.zeros(n, np.float32)
    flash = np.where(tot > 0, 100.0 * p1 / np.maximum(tot, 1e-6), 0.0)

    # time series: depth on every segment at every 30-min snapshot (for the animated map)
    FRM = load_npz(os.path.join(run_dir, 'frames_cm.npz')); seg_t = None; frame_hours = []
    if FRM is not None and len(Q['x']):
        DC = FRM['depth_cm']; frame_hours = [round(float(h), 2) for h in FRM['hours']]
        seg_t = np.zeros((len(DC), n), np.uint16)
        for k in range(len(DC)): seg_t[k] = np.round(seg_top2(n, Q['seg'], DC[k][Q['r'], Q['c']].astype(np.float32))).astype(np.uint16)
        os.makedirs(os.path.join(out, 'frames'), exist_ok=True)
        for k in range(len(DC)): depth_png(os.path.join(out, 'frames', f'f{k:03d}.png'), np.where(WM, 0, DC[k]).astype(np.float32) / 100.0 if WM is not None else DC[k].astype(np.float32) / 100.0)

    # 3 closure probability (v0 physics prior)
    pclose = np.where(inbox, phi((mx - FAIL_M) / SIGMA_M), 0.0)

    # culverts overtopped near a segment
    from scipy.spatial import cKDTree
    from pyproj import Transformer
    tr = Transformer.from_crs(4326, 26986, always_xy=True)
    XC = imp['crossing_columns']; xs = [dict(zip(XC, r)) for r in imp['crossings']]

    # culvert-driven closures (optional rule): P = 1 - (1 - P_depth)(1 - P_culvert), P_culvert = max over surveyed culverts within XING_SEG_M
    xj = json.load(open(os.path.join(run_dir, 'xings.json'))) if os.path.exists(os.path.join(run_dir, 'xings.json')) else {}
    xq = {c['id']: c for c in xj.get('crossings', []) if c.get('q_peak_m3s') is not None}
    CP = culvert_probability(Xrows, xq, {x['id']: x for x in xs}, meta, blockage)
    pcul = np.zeros(n, np.float32); cwhy = {}
    if CP and len(Q['x']):
        tq = cKDTree(np.column_stack([Q['x'], Q['y']]))
        for c in CP:
            for sg in np.unique(Q['seg'][tq.query_ball_point([c['x'], c['y']], XING_SEG_M)]):
                if c['p'] > pcul[sg]:
                    pcul[sg] = c['p']; cwhy[int(sg)] = (f"culvert ({c['stream'] or 'stream'}): headwater {c['hw_m']:.2f} m vs road crest {c['crest_m']:.2f} m"
                                                        + (f", {int(c['blockage'] * 100)}% blocked" if c['blockage'] else '') + (f", {c['q_m3s']:.1f} m3/s" if c['q_m3s'] is not None else ''))
    pcul = np.where(inbox, pcul, 0.0)
    p_depth = pclose.copy(); p_comb = 1.0 - (1.0 - p_depth) * (1.0 - pcul)
    if culvert_rule: pclose = p_comb
    over = [x for x in xs if x['status'] in ('overtopped', 'surcharged')]
    near_culv = np.zeros(n, bool)
    if over and len(Q['x']):
        ox, oy = tr.transform([x['lon'] for x in over], [x['lat'] for x in over]); t = cKDTree(np.column_stack([ox, oy]))
        d, _ = t.query(np.column_stack([Q['x'], Q['y']])); near_culv[np.unique(Q['seg'][d <= 100])] = True

    # rows
    ids = np.nonzero(inbox)[0]; rows = []
    for i in ids:
        nt = net.get(int(i), {})
        r = dict(segment=int(i), road=props['road'][i] or '', town=props['town'][i] or '', road_class=CLASS_NAME.get(int(props['cls'][i]), str(props['cls'][i])),
                 length_m=int(props['len'][i] or 0), aadt=int(props['aadt'][i] or 0), p_close=round(float(pclose[i]), 3), peak_depth_m=round(float(mx[i]), 3),
                 hours_over_30cm=round(float(hrs30[i]), 1), hours_over_15cm=round(float(hrs15[i]), 1),
                 arrival_h=None if np.isnan(arr30[i]) else round(float(arr30[i]), 1), storm_total_mm=round(float(tot[i])), peak1h_mm=round(float(p1[i]), 1),
                 peak3h_mm=round(float(p3[i]), 1), flashness_pct=round(float(flash[i]), 1), culvert_overtopped_nearby=bool(near_culv[i]),
                 p_depth=round(float(p_depth[i]), 3), p_culvert=round(float(pcul[i]), 3), culvert_why=cwhy.get(int(i)),
                 adds_hospital_min=float(nt.get('iso_min') or 0.0), cut_off_hospital=bool(nt.get('cut_hosp')), cut_from_major_roads=bool(nt.get('cut_major')))
        if seg_t is not None: r['d'] = [int(min(v, 255)) for v in seg_t[:, i]]
        r['vehicle_hours_at_risk'] = round(r['p_close'] * r['aadt'] / 24.0 * max(r['hours_over_30cm'], 0.0) * (1 + r['adds_hospital_min'] / 30.0), 1)
        rows.append(r)
    rows.sort(key=lambda r: (-r['p_close'], -r['vehicle_hours_at_risk'], -r['peak_depth_m']))
    for r in rows: r['why'] = reason(r)

    # checks: storm-day reports and MassDOT repeat sites
    checks = dict(reports=imp['summary'].get('reports'))
    if repeat_csv and os.path.exists(repeat_csv):
        site = list(csv.DictReader(open(repeat_csv))); x0, y0, x1, y1 = meta['box']
        sx, sy = tr.transform([float(s['lon']) for s in site], [float(s['lat']) for s in site])
        inb = [(i, a, b) for i, (a, b) in enumerate(zip(sx, sy)) if x0 <= a < x1 and y0 <= b < y1]
        if inb and len(Q['x']):
            t = cKDTree(np.column_stack([Q['x'], Q['y']])); hits = []
            for i, a, b in inb:
                segs = np.unique(Q['seg'][t.query_ball_point([a, b], 150.0)])
                hits.append(dict(site=site[i]['town'] + ', ' + (site[i]['route'] or site[i]['location']), max_p_close=round(float(pclose[segs].max()) if len(segs) else 0.0, 3),
                                 max_depth_m=round(float(mx[segs].max()) if len(segs) else 0.0, 2)))
            base = float((pclose[inbox] >= 0.5).mean())
            checks['massdot_repeat_sites'] = dict(in_box=len(hits), flagged_p05=sum(h['max_p_close'] >= 0.5 for h in hits), share_of_all_segments_flagged=round(base, 3), sites=hits)
            for (i, a, b), h in zip(inb, hits):
                segs = np.unique(Q['seg'][t.query_ball_point([a, b], 150.0)]); h['max_p_with_culverts'] = round(float(p_comb[segs].max()) if len(segs) else 0.0, 3)
            checks['massdot_repeat_sites']['flagged_p05_with_culverts'] = sum(h['max_p_with_culverts'] >= 0.5 for h in hits)
    # documented road flood / closure / damage sites (proto/data/labels_*): segment-level recall vs flagged share, depth rule and with culverts
    LB = load_labels(labels_csv); LM = label_segments(LB, Q, props, meta, strict=True); LL = label_segments(LB, Q, props, meta, strict=False)
    if LM or LL:
        checks['labels_segments'] = dict(note='recall = share of documented sites with a matched segment at P >= 0.5; random_recall = the same for random flagging of the '
                                              'same share of segments; lift = recall / random_recall; lift_naive = recall / flagged share. strict: segments within 30 m '
                                              'of the site; loose: 100 m (exact) / 300 m + same-name segments within 1.5 km (approx)', sites_matched=len(LM),
                                         depth_rule=label_recall(LM, p_depth, inbox), with_culverts=label_recall(LM, p_comb, inbox),
                                         loose=dict(sites_matched=len(LL), depth_rule=label_recall(LL, p_depth, inbox), with_culverts=label_recall(LL, p_comb, inbox)))
    checks['culverts'] = dict(surveyed_in_box=len(CP), with_model_flow=sum(1 for c in CP if c['q_m3s'] is not None), p_ge_50=sum(1 for c in CP if c['p'] >= 0.5),
                              segments_raised_to_p_ge_50=int(((p_comb >= 0.5) & (p_depth < 0.5) & inbox).sum()), rule_applied_to_p_close=bool(culvert_rule),
                              blockage_factors=BLOCKAGE if blockage else {}, probability='Phi(ln(Q / Q_crest) / 0.30) = P(HDS-5 headwater > road crest)')

    # outputs
    keep = [r for r in rows if r['peak_depth_m'] >= 0.05 or r['cut_off_hospital'] or r['adds_hospital_min'] >= 5]
    write_geojson(os.path.join(out, 'segments.geojson'), S, keep)
    for r in rows: r.pop('d', None)
    with open(os.path.join(out, 'watchlist.csv'), 'w', newline='') as f:
        cols = ['rank', 'p_close', 'p_depth', 'p_culvert', 'road', 'town', 'road_class', 'peak_depth_m', 'hours_over_30cm', 'arrival_h', 'peak1h_mm', 'flashness_pct',
                'culvert_overtopped_nearby', 'adds_hospital_min', 'aadt', 'segment', 'why']
        w = csv.writer(f); w.writerow(cols)
        for k, r in enumerate(rows[:top]): w.writerow([k + 1] + [r[c] for c in cols[1:]])
    summ = dict(run=R['name'], model=meta.get('model'), storm_start=meta.get('t0'), box_epsg26986=meta['box'], resolution_m=res,
                segments_in_box=int(inbox.sum()), closures_expected=round(float(pclose[inbox].sum()), 1),
                segments_p_ge_50=int((pclose[inbox] >= 0.5).sum()), segments_p_ge_90=int((pclose[inbox] >= 0.9).sum()),
                segments_p_ge_50_depth_rule=int((p_depth[inbox] >= 0.5).sum()), segments_p_ge_50_with_culverts=int((p_comb[inbox] >= 0.5).sum()),
                km_p_ge_50=round(float(np.asarray(props['len'], float)[inbox & (pclose >= 0.5)].sum() / 1000), 1),
                culverts_overtopped=sum(1 for x in xs if x['status'] == 'overtopped'), culverts_surcharged=sum(1 for x in xs if x['status'] == 'surcharged'),
                crossings_assessed=len(xs), cut_off_from_hospitals=imp['summary']['cut_off_from_hospitals'], worst_added_minutes=imp['summary']['worst_delay_min'],
                rain_max_total_mm=meta.get('rain_total_max_mm'), rain_peak1h_max_mm=round(float(RS['peak1h'].max()), 1) if RS else None,
                flood_model_runtime_s=meta.get('runtime_s'), solver=meta.get('solver'), checks=checks,
                method=dict(closure_depth_m=FAIL_M, sigma_m=SIGMA_M, probability='Phi((peak depth - 0.30) / 0.10), physics prior v0'
                            + (' combined with culvert overtopping: 1 - (1 - P_depth)(1 - P_culvert), P_culvert = P(HDS-5 headwater > road crest) = Phi(ln(Q / Q_crest) / 0.30)' if culvert_rule else ''),
                            network='segments >= 15 cm removed; Dijkstra to nearest hospital (sim/infra/impacts.py)', culverts='FHWA HDS-5 (sim/infra/culvert.py)'),
                frame_hours=frame_hours, closed_per_frame=[int(((seg_t[k] >= 30) & inbox).sum()) for k in range(len(frame_hours))] if seg_t is not None else [],
                rain_hourly_mean_mm=[round(float(v), 1) for v in RS['hourly_mean']] if RS is not None and 'hourly_mean' in RS else [],
                made=time.strftime('%Y-%m-%d %H:%M'), prototype_runtime_s=round(time.time() - t_start, 1))
    json.dump(summ, open(os.path.join(out, 'summary.json'), 'w'), indent=1)
    write_map(os.path.join(out, 'map.html'), out, meta, np.where(WM, 0, H) if WM is not None else H, summ)
    write_figure(os.path.join(out, 'figure.png'), meta, H, S, keep)
    write_report(os.path.join(out, 'REPORT.md'), summ, rows[:15])
    print(json.dumps({k: v for k, v in summ.items() if k != 'checks'}, indent=1)); print('wrote', out)
    return summ


def seg_lines(S, i):
    return [[[round(float(a), 5), round(float(b), 5)] for a, b in zip(np.cumsum(d[0::2]) / 1e5, np.cumsum(d[1::2]) / 1e5)] for d in S['geo'][i]]


def write_geojson(path, S, rows):
    feats = [dict(type='Feature', geometry=dict(type='MultiLineString', coordinates=seg_lines(S, r['segment'])), properties={k: v for k, v in r.items()}) for r in rows]
    json.dump(dict(type='FeatureCollection', features=feats), open(path, 'w'), separators=(',', ':'))


def depth_png(path, H):
    from PIL import Image
    cols = [(0.05, (198, 219, 239, 150)), (0.15, (107, 174, 214, 190)), (0.30, (33, 113, 181, 215)), (1.0, (8, 48, 107, 235))]
    A = np.zeros(H.shape + (4,), np.uint8)
    for th, c in cols: A[H >= th] = c
    Image.fromarray(A, 'RGBA').save(path, optimize=True)


def write_map(path, out, meta, H, summ):
    from pyproj import Transformer
    depth_png(os.path.join(out, 'depth.png'), H)
    tr = Transformer.from_crs(26986, 4326, always_xy=True); x0, y0, x1, y1 = meta['box']
    corners = [list(tr.transform(x, y)) for x, y in ((x0, y1), (x1, y1), (x1, y0), (x0, y0))]
    cx, cy = tr.transform((x0 + x1) / 2, (y0 + y1) / 2)
    html = MAP_HTML.replace('__CORNERS__', json.dumps(corners)).replace('__CENTER__', json.dumps([cx, cy])).replace('__SUMMARY__', json.dumps(summ))
    open(path, 'w').write(html)


def write_figure(path, meta, H, S, rows):
    import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
    from pyproj import Transformer
    tr = Transformer.from_crs(4326, 26986, always_xy=True); x0, y0, x1, y1 = meta['box']
    fig, ax = plt.subplots(figsize=(8, 8), dpi=130)
    ax.imshow(np.ma.masked_less(H, 0.05), extent=(x0, x1, y0, y1), cmap='Blues', vmin=0, vmax=1.0, interpolation='nearest')
    for r in rows:
        col = '#b2182b' if r['p_close'] >= 0.5 else '#f4a582' if r['p_close'] >= 0.1 else '#999999'; lw = 2.2 if r['p_close'] >= 0.5 else 0.8
        for line in seg_lines(S, r['segment']):
            a = np.array(line); X, Y = tr.transform(a[:, 0], a[:, 1]); ax.plot(X, Y, color=col, lw=lw)
    ax.set_xlim(x0, x1); ax.set_ylim(y0, y1); ax.set_xticks([]); ax.set_yticks([])
    ax.set_title(f"{meta.get('run')}: peak flood depth (blue) and segments likely to close (red, P >= 0.5)", fontsize=9)
    fig.tight_layout(); fig.savefig(path); plt.close(fig)


def write_report(path, s, top):
    L = [f"# Road-closure prototype: {s['run']}", '', f"Flood model: {s['model']} ({s['solver']}), {s['resolution_m']:.0f} m grid, storm from {s['storm_start']}.", '',
         '| Result | Value |', '| --- | --- |',
         f"| Road segments in the area | {s['segments_in_box']:,} |", f"| Expected closures (sum of probabilities) | {s['closures_expected']} |",
         f"| Segments with closure probability >= 50% | {s['segments_p_ge_50']} ({s['km_p_ge_50']} km) |",
         f"| Culverts overtopped / surcharged | {s['culverts_overtopped']} / {s['culverts_surcharged']} of {s['crossings_assessed']} |",
         f"| Road segments cut off from hospitals | {s['cut_off_from_hospitals']} |", f"| Worst added trip time to a hospital | {s['worst_added_minutes']} min |",
         f"| Heaviest hour of rain | {s['rain_peak1h_max_mm']} mm |", f"| Flood model run time | {s['flood_model_runtime_s']} s |", '']
    rp = (s['checks'] or {}).get('reports')
    if rp:
        L += ['## Checks against what happened', '',
              f"- Storm-day flood reports in the area: {rp.get('n_storm_day')}; water >= 10 cm within 100 m of {100 * (rp.get('point_hit_rate') or 0):.0f}% of them, "
              f"vs {100 * (rp.get('point_any_day_rate') or 0):.0f}% of random points (any day)."]
        if rp.get('lift') is not None: L.append(f"- Segments flagged impassable are {rp['lift']}x as likely as an average segment to have a report within 200 m.")
    ms = (s['checks'] or {}).get('massdot_repeat_sites')
    if ms: L.append(f"- MassDOT repeating flood sites in the area: {ms['in_box']}; {ms['flagged_p05']} have a segment within 150 m at P >= 0.5 "
                    f"(share of all segments at P >= 0.5: {100 * ms['share_of_all_segments_flagged']:.1f}%).")
    L += ['', '## Top segments', '', '| # | P(close) | Road | Town | Why |', '| --- | --- | --- | --- | --- |']
    for k, r in enumerate(top): L.append(f"| {k + 1} | {r['p_close']:.2f} | {r['road'] or '(unnamed)'} | {r['town']} | {r['why']} |")
    L += ['', 'Closure probability v0 = Phi((peak depth - 0.30 m) / 0.10 m): a physics prior, not yet calibrated on observed closures.']
    open(path, 'w').write('\n'.join(L) + '\n')


MAP_HTML = r"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Road closure replay</title>
<link href="https://unpkg.com/maplibre-gl@4.7.1/dist/maplibre-gl.css" rel="stylesheet">
<script src="https://unpkg.com/maplibre-gl@4.7.1/dist/maplibre-gl.js"></script>
<style>html,body,#m{margin:0;height:100%;font:13px system-ui,sans-serif}
#p{position:absolute;top:10px;left:10px;background:#fff;padding:10px 12px;border-radius:8px;box-shadow:0 1px 4px #0003;max-width:290px}
#p h3{margin:0 0 6px;font-size:14px}#p label{display:block;margin:2px 0}.k{display:inline-block;width:18px;height:4px;margin-right:6px;vertical-align:middle}
#t{position:absolute;left:10px;right:10px;bottom:22px;background:#fff;padding:8px 12px;border-radius:8px;box-shadow:0 1px 4px #0003;display:flex;gap:10px;align-items:center}
#t input{flex:1}#t button{font-size:16px;width:40px;height:32px;border-radius:6px;border:1px solid #ccc;background:#f6f6f6}#clock{min-width:150px;font-weight:600}
#cnt{min-width:120px}#rain{height:28px;width:120px}@media(max-width:600px){#p{max-width:200px;font-size:12px}#clock{min-width:100px}#rain{display:none}}</style>
</head><body><div id="m"></div>
<div id="p"><h3>Which roads close</h3><div id="s"></div>
<b>Layers</b><label><input type="checkbox" data-l="depth" checked> Flood depth</label>
<label><input type="checkbox" data-c="2" checked> Highways</label><label><input type="checkbox" data-c="1" checked> Arterials</label>
<label><input type="checkbox" data-c="0" checked> Local / collector</label>
<div style="margin-top:6px"><span class="k" style="background:#b2182b"></span>closed now (&ge; 30 cm)<br><span class="k" style="background:#f4a582"></span>15&ndash;30 cm<br>
<span class="k" style="background:#9ecae1"></span>wet<br><span class="k" style="background:#555;height:2px"></span>closes at peak (peak view)</div></div>
<div id="t"><button id="play">&#9654;</button><input id="sl" type="range" min="0" value="0"><span id="clock"></span><span id="cnt"></span><svg id="rain"></svg></div>
<script>
const S=__SUMMARY__, C=__CORNERS__, FH=S.frame_hours||[], NF=FH.length, T0=new Date(S.storm_start.replace('Z',':00Z'));
const CLS={0:'local / collector',1:'arterial',2:'highway'};
document.getElementById('s').innerHTML=`At peak: ${S.segments_p_ge_50} segments likely closed (${S.km_p_ge_50} km), ${S.culverts_overtopped} culverts overtopped.<br><br>`;
const m=new maplibregl.Map({container:'m',center:__CENTER__,zoom:12,style:{version:8,sources:{t:{type:'raster',tileSize:256,attribution:'Esri, USGS',
tiles:['https://server.arcgisonline.com/ArcGIS/rest/services/World_Topo_Map/MapServer/tile/{z}/{y}/{x}']}},layers:[{id:'t',type:'raster',source:'t'}]}});
const sl=document.getElementById('sl'); sl.max=Math.max(NF-1,0); let k=NF?NF-1:0, timer=null;
const pad=n=>String(n).padStart(3,'0');
function frameUrl(i){return NF?`frames/f${pad(i)}.png`:'depth.png'}
FH.forEach((h,i)=>{if(i%6==0){const im=new Image();im.src=frameUrl(i)}});
function show(i){k=i;sl.value=i;if(!m.getSource('d'))return;m.getSource('d').updateImage({url:frameUrl(i),coordinates:C});
 const d=NF?['at',i,['get','d']]:['*',100,['get','peak_depth_m']];
 if(m.getLayer('seg'))m.setPaintProperty('seg','line-color',['case',['>=',d,30],'#b2182b',['>=',d,15],'#f4a582',['>=',d,5],'#9ecae1','rgba(0,0,0,0)']),
 m.setPaintProperty('seg','line-width',['case',['>=',d,30],4,['>=',d,15],3,2]);
 const t=new Date(T0.getTime()+(FH[i]||0)*3600e3);document.getElementById('clock').textContent=t.toLocaleString('en-US',{month:'short',day:'numeric',hour:'numeric',minute:'2-digit',timeZone:'America/New_York'});
 document.getElementById('cnt').textContent=`${(S.closed_per_frame||[])[i]??''} segments closed`;
 const r=S.rain_hourly_mean_mm||[],svg=document.getElementById('rain');if(r.length){const mx=Math.max(...r,1),w=120/r.length;
 svg.innerHTML=r.map((v,j)=>`<rect x="${j*w}" y="${28-26*v/mx}" width="${Math.max(w-0.5,0.5)}" height="${26*v/mx}" fill="${j<=FH[i]?'#2171b5':'#c6dbef'}"/>`).join('')}}
function play(){if(timer){clearInterval(timer);timer=null;document.getElementById('play').innerHTML='&#9654;';return}
 if(k>=NF-1)k=0;document.getElementById('play').innerHTML='&#10074;&#10074;';timer=setInterval(()=>{if(k>=NF-1){play();return}show(k+1)},350)}
document.getElementById('play').onclick=play;sl.oninput=e=>{if(timer)play();show(+e.target.value)};
m.on('load',()=>{m.addSource('d',{type:'image',url:frameUrl(k),coordinates:C});m.addLayer({id:'depth',type:'raster',source:'d',paint:{'raster-opacity':0.8,'raster-resampling':'nearest','raster-fade-duration':0}});
fetch('segments.geojson').then(r=>r.json()).then(g=>{m.addSource('s',{type:'geojson',data:g});
m.addLayer({id:'peak',type:'line',source:'s',filter:['>=',['get','p_close'],0.5],paint:{'line-color':'#555','line-width':1,'line-dasharray':[2,2]}});
m.addLayer({id:'seg',type:'line',source:'s',paint:{'line-width':3,'line-color':'#b2182b'}});
m.on('click','seg',e=>{const p=e.features[0].properties;new maplibregl.Popup().setLngLat(e.lngLat).setHTML(`<b>${p.road||'(unnamed)'}, ${p.town}</b><br>${p.road_class}<br>Chance of closing at peak: ${(+p.p_close*100).toFixed(0)}%<br>${p.why}`).addTo(m)});
m.on('mouseenter','seg',()=>m.getCanvas().style.cursor='pointer');m.on('mouseleave','seg',()=>m.getCanvas().style.cursor='');filt();show(0);});});
function filt(){const on=[...document.querySelectorAll('[data-c]')].filter(b=>b.checked).map(b=>CLS[b.dataset.c]);['seg','peak'].forEach(l=>{if(m.getLayer(l))m.setFilter(l,l=='peak'?['all',['>=',['get','p_close'],0.5],['in',['get','road_class'],['literal',on]]]:['in',['get','road_class'],['literal',on]])})}
document.querySelectorAll('[data-c]').forEach(b=>b.onchange=filt);
document.querySelector('[data-l=depth]').onchange=e=>m.setLayoutProperty('depth','visibility',e.target.checked?'visible':'none');
</script></body></html>"""


def selftest():
    """Synthetic storm on a fake grid and three fake segments: checks probabilities, timing, flashness, outputs."""
    import tempfile
    d = tempfile.mkdtemp(); rd = os.path.join(d, 'sep2023_test'); os.makedirs(rd); out = os.path.join(d, 'out')
    box = [150000, 905000, 152000, 907000]; res = 20; ny = nx = 100
    H = np.zeros((ny, nx), np.float32); H[40:60, :] = 0.6; H[70:75, :] = 0.2
    np.save(f'{rd}/hmax.npy', H); np.save(f'{rd}/z.npy', np.zeros_like(H))
    json.dump(dict(run='sep2023_test', box=box, res_m=res, shape=[ny, nx], t0='2023-09-11T16:00Z', frame_min=30, frames=[{}] * 3, model='synthetic', solver='none'), open(f'{rd}/meta.json', 'w'))
    tover30 = np.where(H >= 0.3, 3.0, 0).astype(np.float32); tarr = np.where(H >= 0.3, 5.0, np.nan).astype(np.float32)
    np.savez(f'{rd}/timing.npz', tover15=np.where(H >= 0.15, 4.0, 0).astype(np.float32), tover30=tover30, tarr30=tarr)
    np.savez(f'{rd}/frames_cm.npz', depth_cm=np.stack([np.zeros_like(H), H * 50, H * 100]).astype(np.uint16), hours=np.array([0, 0.5, 1.0], np.float32))
    np.savez(f'{rd}/rainstats.npz', total=np.full((ny, nx), 200, np.float32), peak1h=np.full((ny, nx), 60, np.float32), peak3h=np.full((ny, nx), 150, np.float32))
    from pyproj import Transformer
    tr = Transformer.from_crs(26986, 4326, always_xy=True)
    def seg(y):
        lo, la = tr.transform([box[0] + 100, box[2] - 100], [box[3] - y * res, box[3] - y * res])
        a = [int(round(v * 1e5)) for v in (lo[0], la[0])]; b = [int(round(v * 1e5)) for v in (lo[1], la[1])]; return [[a[0], a[1], b[0] - a[0], b[1] - a[1]]]
    S = dict(n=3, geo=[seg(50), seg(72), seg(10)], props=dict(road=['A St', 'B St', 'C St'], town=['T'] * 3, cls=[2, 1, 0], low=[0] * 3, len=[1800] * 3, aadt=[20000, 5000, 500]),
             links=[[0, 1], [1, 2]])
    sp = os.path.join(d, 'segs.json'); json.dump(S, open(sp, 'w'))
    s = run(rd, out, sp, os.path.join(d, 'none.json'), None, None, None)
    rows = list(csv.DictReader(open(os.path.join(out, 'watchlist.csv'))))
    assert rows[0]['road'] == 'A St' and float(rows[0]['p_close']) > 0.99, rows[0]
    assert float(rows[1]['p_close']) < 0.2 and rows[1]['road'] == 'B St', rows[1]
    assert abs(float(rows[0]['hours_over_30cm']) - 3.0) < 1e-6 and abs(float(rows[0]['flashness_pct']) - 30.0) < 0.1
    for f in ('segments.geojson', 'map.html', 'figure.png', 'summary.json', 'REPORT.md', 'depth.png'): assert os.path.exists(os.path.join(out, f)), f
    assert s['segments_p_ge_50'] == 1 and s['closed_per_frame'] == [0, 1, 1], s['closed_per_frame']
    g = json.load(open(os.path.join(out, 'segments.geojson'))); assert g['features'][0]['properties']['d'] == [0, 30, 60]
    assert os.path.exists(os.path.join(out, 'frames', 'f002.png'))
    # culvert rule: a 0.6 m pipe under dry C St (row 10) passing 3 m3/s overtops (HDS-5 HW >> crest 0.6 + 1.0 m); a 3 m box at 3 m3/s does not
    lo, la = tr.transform([box[0] + 1000, box[0] + 400], [box[3] - 10 * res, box[3] - 10 * res])
    cols = ['lon', 'lat', 'id', 'road', 'stream', 'shape', 'span_m', 'rise_m', 'fill_m', 'material', 'inlet', 'n_barrels', 'inlet_blockage']
    xp = os.path.join(d, 'xings_all.json')
    json.dump(dict(columns=cols, rows=[[lo[0], la[0], 'c1', 'C St', 'Brook', 'circular', 0.6, 0.6, 1.0, 'concrete', 'headwall', 1, 'Poor'],
                                       [lo[1], la[1], 'c2', 'C St', 'River', 'box', 3.0, 3.0, 1.0, 'concrete', 'wingwall', 1, None]]), open(xp, 'w'))
    json.dump(dict(crossings=[dict(id='c1', q_peak_m3s=3.0), dict(id='c2', q_peak_m3s=3.0)]), open(f'{rd}/xings.json', 'w'))
    lp = os.path.join(d, 'labels.csv')
    with open(lp, 'w', newline='') as f:
        w = csv.writer(f); w.writerow(['id', 'name', 'road', 'town', 'type', 'lon', 'lat', 'coord_quality'])
        w.writerow(['L1', 'C St culvert', 'C St', 'T', 'culvert_failure', lo[0], la[0], 'exact']); w.writerow(['L2', 'A St flood', 'A St', 'T', 'flooded', lo[1], tr.transform(box[0] + 400, box[3] - 50 * res)[1], 'exact'])
    out2 = os.path.join(d, 'out2'); s2 = run(rd, out2, sp, xp, None, None, None, culvert_rule=True, labels_csv=lp)
    rows2 = {r['road']: r for r in csv.DictReader(open(os.path.join(out2, 'watchlist.csv')))}
    assert float(rows2['C St']['p_culvert']) > 0.99 and float(rows2['C St']['p_close']) > 0.99 and float(rows2['C St']['p_depth']) < 0.01, rows2['C St']
    assert 'headwater' in rows2['C St']['why'] and '25% blocked' in rows2['C St']['why'], rows2['C St']['why']
    cu = s2['checks']['culverts']; assert cu['surveyed_in_box'] == 2 and cu['p_ge_50'] == 1 and cu['segments_raised_to_p_ge_50'] == 1, cu
    ls = s2['checks']['labels_segments']; assert ls['depth_rule']['all']['recall'] == 0.5 and ls['with_culverts']['all']['recall'] == 1.0, ls
    assert ls['with_culverts']['culvert_washout']['recall'] == 1.0 and s2['segments_p_ge_50'] == 2 and s2['segments_p_ge_50_depth_rule'] == 1
    s3 = run(rd, os.path.join(d, 'out3'), sp, xp, None, None, None, culvert_rule=False, labels_csv=lp)
    assert s3['segments_p_ge_50'] == 1 and s3['segments_p_ge_50_with_culverts'] == 2       # rule off: reported, not applied
    print('selftest ok:', out)


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--run-dir'); ap.add_argument('--out', default='proto_out'); ap.add_argument('--top', type=int, default=30)
    ap.add_argument('--segments', default=os.path.join(ROOT, 'docs', 'graph_segments.json'))
    ap.add_argument('--crossings', default=os.path.join(ROOT, 'docs', 'network', 'crossings_all.json'))
    ap.add_argument('--reports', default=os.path.join(ROOT, 'docs', 'prone', 'flood_reports.json'))
    ap.add_argument('--facilities', default=os.path.join(ROOT, 'docs', 'network', 'facilities.json'))
    ap.add_argument('--repeat', default=os.path.join(HERE, 'data', 'massdot_repeat_flood_d3.csv'))
    ap.add_argument('--labels', default=os.path.join(HERE, 'data', 'labels_sep2023_leominster.csv'))
    ap.add_argument('--culvert-rule', action='store_true', default=os.environ.get('PROTO_CULVERT_RULE', '0') == '1',
                    help='P(close) = 1 - (1 - P_depth)(1 - P_culvert) (HDS-5 overtopping of surveyed culverts); both versions are scored either way')
    ap.add_argument('--no-blockage', action='store_true', help='ignore NAACC inlet blockage in the culvert rule')
    ap.add_argument('--selftest', action='store_true')
    a = ap.parse_args()
    if a.selftest: selftest()
    else: run(a.run_dir, a.out, a.segments, a.crossings, a.reports, a.facilities, a.repeat, a.top, a.culvert_rule, a.labels, not a.no_blockage)
