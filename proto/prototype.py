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
# ---- FREEBOARD rule (--freeboard): a road whose crest stands less than the design freeboard above the water beside it is at risk ----
# Margin: highway drainage design keeps the design water surface at least 1 ft (0.30 m) below the road edge, e.g. Oklahoma DOT Roadway
# Drainage Manual ch. 9 sec. 9.3.3.3 (allowable headwater "one foot lower than the upstream shoulder edge elevation at the lowest point of
# the roadway"); the 1 ft freeboard of many state DOT culvert / roadside-ditch criteria applied under FHWA HDS-5 (Schall et al. 2012).  Less than
# that margin = water at the road edge, saturating the embankment and overtopping with any wave or error in the flow.
# Sigma: the two independent height errors, combined: road crest from 3DEP QL2 lidar, RMSEz <= 0.10 m (USGS Lidar Base Specification,
# quality level 2) and modelled water surface, 0.10 m (the depth sigma above); sqrt(0.10^2 + 0.10^2) = 0.14 -> 0.15 m.  Neither number is tuned on labels.
FB_MARGIN_M = 0.30
FB_SIGMA_M = 0.15
FB_RADIUS_M = 30.0     # water "beside" the road: wet cells within 30 m of the road point (3 x 3 cells at 20 m), the road's own unedited cells excluded
# ---- OVERTOPPING layer ("may close", shown beside the main closure layer, never added to p_close) ----
# Same freeboard geometry with margin 0: the water beside the road reaches the road crest (embankment overtopping).  The margin was chosen after
# looking at the Sept 2023 Leominster labels (recall 0.74 at 9.8 % flagged vs 0.39 at 4.7 % for the depth rule), so it is a CANDIDATE to be
# confirmed on an independent storm (Vermont July 2023) before it can enter p_close.
OT_MARGIN_M = 0.0
FB_WET_M = 0.10        # a cell counts as water when its peak depth >= 10 cm (the wet threshold of w9 / validate_points)
EDIT_TOL_M = 0.05      # a cell lowered by more than this (channel burn, crossing notch, depression breach) is a waterway cell, not road surface
# ---- FAST-WATER rule (--fastwater) ----
# Vehicle stability: depth x velocity limit for a small passenger car 0.3 m2/s (Shand et al. 2011, ARR Project 10 Stage 2 report, Table 3:
# 0.1 m at 3 m/s; the H1/H2 hazard-class limit of Australian Rainfall and Runoff 2019 Book 6 ch. 7, Safety Design Criteria); large cars 0.45 and
# 4WDs 0.6 m2/s.  P_dv = Phi(ln(DV / 0.3) / 0.35): sigma_ln = half the log-range of the vehicle classes, ln(0.6 / 0.3) / 2 = 0.35.
DV0_M2S = 0.30
DV_SIGMA_LN = 0.35
# Washout: overtopping flow on a road embankment at a stream crossing erodes the fill once the velocity passes the permissible velocity of
# grass cover on easily eroded soil, 1.5 m/s (5 ft/s; SCS 1954 TP-61 / Chow 1959 Open-Channel Hydraulics Table 7-6: Kentucky bluegrass,
# easily eroded soil 1.5 m/s, erosion resistant 2.1 m/s; grass mixtures 1.2 / 1.5 m/s).  sigma_ln 0.30 spans that 1.2-2.1 m/s range
# (ln(2.1 / 1.2) / 2 = 0.28).  Applied only on unedited road cells within XING_SEG_M of a mapped crossing with >= 10 cm of water over them.
V_ERODE_MS = 1.5
V_SIGMA_LN = 0.30
ERODE_MIN_H_M = 0.10
# ---- ELEVATED ROADS (default; PROTO_BRIDGES=0 turns it off): bridge decks the bare-earth lidar removed (sim/infra/impacts.deck_points) ----
DECK_GAP_M = 2.0       # the road's own lidar crest drops >= 2 m below the road on both sides: the ground under a removed deck, not the road
DECK_RADIUS_M = 150.0  # ... within 150 m along the road each way (a deck or viaduct span seen from its approaches)
DECK_NBI_M = 100.0     # ... and an NBI bridge carrying the same route number (item 5D) within 100 m
# ---- SAG / UNDERPASS layer (candidate, never in p_close; shown as an optional map layer) ----
# A sag of the road profile (a low point >= 0.30 m below the road on both sides within 150 m along it) that is also a closed depression of the
# bare-earth lidar (>= 0.30 m deep before spilling) holds water that only storm drains remove.  Not counted at road-stream crossings (a
# mapped crossing within 50 m: the culvert rule's case) or on open water / channel cells.  Drain capacity: FHWA HEC-22 (Brown et al. 2009,
# Urban Drainage Design Manual, 3rd ed., FHWA-NHI-10-009) Table 3-1 minimum design frequencies: 10-year for sags on local / collector roads,
# 50-year for sag points on high-volume roads and for depressed sections / underpasses where ponded water can only leave through the drains.
# Design intensities from NOAA Atlas 14 vol. 10 (Perica et al. 2015) for central Massachusetts, 60 min: 10-year ~1.7 in (43 mm), 50-year
# ~2.3 in (58 mm) (approximate regional values, not read per site).  Underpass = an NBI bridge or a removed deck within 60 m, or an Interstate.
# P_rain = Phi(ln(V_excess / V_need) / 0.5): V_excess = C (i_peak1h - i_design) x 1 h x catchment (rational method, C = 0.6 for mixed urban
# land, HEC-22 Table 3-1 ranges), catchment = cells whose D8 descent ends in the depression (impacts.closed_depressions); V_need = the lidar
# volume below the sag low point + 0.30 m.  sigma_ln 0.5: design intensity, C and drain condition are each uncertain by tens of percent.
# P_pond = Phi((modelled peak water surface within 30 m - sag low point - 0.30) / 0.10): the flood model's own ponding there.
# P_sag = 1 - (1 - P_rain)(1 - P_pond); a segment takes the largest P_sag of sags within 30 m.
SAG_MIN_M = 0.30
SAG_RADIUS_M = 150.0
SAG_XING_M = 50.0
SAG_UNDER_M = 60.0
I10_MM = 43.0
I50_MM = 58.0
SAG_C = 0.6
SAG_SIGMA_LN = 0.5
SAG_SEG_M = 30.0
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


def adjacent_wse(H, Z, ZR, road_cells, res, radius=FB_RADIUS_M, wet=FB_WET_M):
    """Highest peak water surface (m) beside each cell: max of (model DEM + peak depth) over wet cells within `radius`, excluding the road's own
    unedited cells (their water is the depth rule's; counting it here would count it twice).  Edited cells (notch, burn, breach: z_raw - z >
    EDIT_TOL_M) are waterways and stay in, so the pool behind a culvert notch counts against the road over it.  The time maximum of z + h in
    one cell is z + hmax.  -inf where no wet cell is near.  Returns (wse_adj grid, edited mask)."""
    from scipy.ndimage import maximum_filter
    edited = (ZR - Z) > EDIT_TOL_M
    W = np.where((H >= wet) & ~(road_cells & ~edited), Z + H, -np.inf).astype(np.float64)
    k = max(1, int(radius // res))
    return maximum_filter(W, size=2 * k + 1, mode='constant', cval=-np.inf), edited


def sag_probability(PA, G, ZR, Z, H, peak1h, res, cls, bad, nbi_xy, xing_xy, deck_x, deck_y):
    """Road sags and P(the drains are overwhelmed and >= 0.30 m stands in the sag), see the SAG constants.  PA: all road points (unfiltered,
    so the profile runs through bridges and water), G = impacts.road_graph(PA), ZR: lidar before hydraulic edits, Z + H: modelled water
    surface, peak1h: peak 1-hour rain grid (mm) or None, bad: points never taken as a sag low point (decks, water).  Returns a list of dicts."""
    from scipy.spatial import cKDTree
    from scipy import ndimage
    from scipy.ndimage import maximum_filter
    indptr, nbr, dist = G; deg = np.diff(indptr); z = ZR[PA['r'], PA['c']].astype(np.float64)
    if len(z) == 0: return []
    nmin = np.full(len(z), np.inf); np.minimum.at(nmin, np.repeat(np.arange(len(z)), deg), z[nbr])
    cand = np.nonzero((z <= nmin + 1e-6) & (deg >= 2) & ~np.asarray(bad, bool))[0]
    rim, nd = IM.profile_rims(G, z, cand, SAG_RADIUS_M); k = (nd >= 2) & (rim - z[cand] >= SAG_MIN_M); cand, sd = cand[k], (rim - z[cand])[k]
    F, lab, area = IM.closed_depressions(ZR, res); r, c = PA['r'][cand], PA['c'][cand]; L = lab[r, c]
    k = (L > 0) & ((F - ZR)[r, c] >= SAG_MIN_M)
    if len(xing_xy): k &= cKDTree(xing_xy).query(np.column_stack([PA['x'][cand], PA['y'][cand]]))[0] > SAG_XING_M
    cand, sd, r, c, L = cand[k], sd[k], r[k], c[k], L[k]
    if not len(cand): return []
    o = np.lexsort((z[cand], PA['seg'][cand], L)); key = L[o].astype(np.int64) * (int(PA['seg'].max()) + 1) + PA['seg'][cand][o]   # one sag per depression and
    first = o[np.r_[True, key[1:] != key[:-1]]]; cand, sd, r, c, L = cand[first], sd[first], r[first], c[first], L[first]               # segment: its lowest point
    xy = np.column_stack([PA['x'][cand], PA['y'][cand]]); under = cls[PA['seg'][cand]] == 2
    if len(nbi_xy): under |= cKDTree(nbi_xy).query(xy)[0] <= SAG_UNDER_M
    if len(deck_x): under |= cKDTree(np.column_stack([deck_x, deck_y])).query(xy)[0] <= SAG_UNDER_M
    ides = np.where(under, I50_MM, I10_MM); ip = peak1h[r, c].astype(np.float64) if peak1h is not None else np.zeros(len(cand))
    zl = ZR[r, c].astype(np.float64); objs = ndimage.find_objects(lab); vneed = np.zeros(len(cand))
    for j in range(len(cand)):
        sl = objs[L[j] - 1]; m = lab[sl] == L[j]; vneed[j] = np.clip(np.minimum(F[sl], zl[j] + SAG_MIN_M) - ZR[sl], 0, None)[m].sum() * res * res
    vex = SAG_C * np.maximum(ip - ides, 0.0) / 1000.0 * area[L]
    prain = np.zeros(len(cand)); m = vex > 0
    if m.any(): prain[m] = phi(np.log(vex[m] / np.maximum(vneed[m], 1e-6)) / SAG_SIGMA_LN)
    W = maximum_filter(np.where(H >= FB_WET_M, Z + H, -np.inf), size=2 * max(1, int(SAG_SEG_M // res)) + 1, mode='constant', cval=-np.inf)[r, c]
    ppond = np.zeros(len(cand)); m = np.isfinite(W)
    if m.any(): ppond[m] = phi((W[m] - zl[m] - SAG_MIN_M) / SIGMA_M)
    p = combine(prain, ppond)
    return [dict(x=float(xy[j, 0]), y=float(xy[j, 1]), seg=int(PA['seg'][cand[j]]), depth_m=round(float(min(sd[j], (F - ZR)[r[j], c[j]])), 2), under=bool(under[j]),
                 design=50 if under[j] else 10, i_design_mm=float(ides[j]), i_peak_mm=round(float(ip[j]), 1), area_ha=round(float(area[L[j]]) / 1e4, 2),
                 v_need_m3=round(float(vneed[j])), v_excess_m3=round(float(vex[j])), p_rain=float(prain[j]), p_pond=float(ppond[j]), p=float(p[j])) for j in range(len(cand))]


def p_freeboard(f):
    """P(road at risk) from freeboard f = road crest - adjacent peak water surface (m): Phi((0.30 - f) / 0.15); 0 where no water is near."""
    f = np.asarray(f, np.float64); out = np.zeros(f.shape)
    ok = np.isfinite(f); out[ok] = phi((FB_MARGIN_M - f[ok]) / FB_SIGMA_M) if ok.any() else out[ok]
    return out


def p_fastwater(dv, v, h, near_xing):
    """Per road point: P_dv = Phi(ln(DV / 0.3) / 0.35) (vehicle stability) and, at crossings with >= 10 cm over the road, P_wash =
    Phi(ln(V / 1.5) / 0.30) (embankment erosion); combined 1 - (1 - P_dv)(1 - P_wash).  Returns (P_fw, P_dv, P_wash)."""
    dv = np.asarray(dv, np.float64); v = np.asarray(v, np.float64); h = np.asarray(h, np.float64)
    pdv = np.zeros(dv.shape); m = dv > 1e-6
    if m.any(): pdv[m] = phi(np.log(dv[m] / DV0_M2S) / DV_SIGMA_LN)
    pw = np.zeros(v.shape); m = np.asarray(near_xing, bool) & (h >= ERODE_MIN_H_M) & (v > 1e-6)
    if m.any(): pw[m] = phi(np.log(v[m] / V_ERODE_MS) / V_SIGMA_LN)
    return 1.0 - (1.0 - pdv) * (1.0 - pw), pdv, pw


def p_overtop(f):
    """P(water beside the road reaches its crest): Phi((0 - f) / 0.15); 0 where no water is near."""
    f = np.asarray(f, np.float64); out = np.zeros(f.shape)
    ok = np.isfinite(f); out[ok] = phi((OT_MARGIN_M - f[ok]) / FB_SIGMA_M) if ok.any() else out[ok]
    return out


def combine(*ps):
    """1 - prod(1 - P_i): closure if any independent mechanism closes the road."""
    q = np.ones_like(np.asarray(ps[0], np.float64))
    for p in ps: q = q * (1.0 - np.asarray(p, np.float64))
    return 1.0 - q


def label_split(matches, P, inbox, thr=0.5):
    """Overfitting check: recall and chance-corrected lift on odd vs even label ids (L001 odd, L002 even), all groups together."""
    fl = (P >= thr) & inbox; f = float(fl[inbox].mean()) if inbox.any() else 0.0; out = {}
    for nm, par in (('odd', 1), ('even', 0)):
        M = [m for m in matches if int(''.join(ch for ch in m[0].get('id', '0') if ch.isdigit()) or 0) % 2 == par]
        if not M: continue
        hit = np.array([fl[s].any() for _, s in M]); exp_ = np.array([1 - (1 - f) ** len(s) for _, s in M])
        out[nm] = dict(n=len(M), recall=round(float(hit.mean()), 3), lift=round(float(hit.mean() / exp_.mean()), 2) if exp_.mean() > 0 else None)
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


def load_line_labels(path):
    """Closed road stretches as GeoJSON lines (e.g. proto/data/vt_roadclosures_jul2023.geojson: Road, Cause, FullorPart) -> label dicts with
    'lines' (lon/lat parts) and a type from the cause (flooding / high water -> flooded, washout, sinkhole, mudslide / trees -> other_damage,
    none -> closed), so LABEL_GROUPS and the variants machinery score them like the point labels."""
    G = json.load(open(path)); out = []
    for k, f in enumerate(G.get('features', [])):
        g = f.get('geometry') or {}; parts = g.get('coordinates') or []
        parts = parts if g.get('type') == 'MultiLineString' else [parts]; p = f.get('properties') or {}; cz = (p.get('Cause') or '').lower()
        typ = ('washout' if 'washout' in cz else 'sinkhole' if 'sinkhole' in cz else 'other_damage' if ('mud' in cz or 'slide' in cz or 'tree' in cz)
               else 'flooded' if ('flood' in cz or 'water' in cz) else 'closed')
        out.append(dict(id=f'V{k + 1:03d}', type=typ, road=p.get('Road'), name=f"{p.get('Road')}: {p.get('Cause') or 'closed'} ({p.get('FullorPart') or ''})",
                        lines=[[(float(c[0]), float(c[1])) for c in part] for part in parts if len(part) >= 1]))
    return out


def label_segments_lines(labels, Q, meta, radius=30.0, share=0.5):
    """Road segments a closed stretch (line) runs along: a segment matches when >= `share` of its road points lie within `radius` of the line, or
    >= `share` of the line's in-box points (every 5 m) have their nearest road point within `radius` on that segment (a short closure on a long
    segment).  Side streets touch the line at one end only and do not match."""
    from scipy.spatial import cKDTree
    from pyproj import Transformer
    if not labels or not len(Q['x']): return []
    tr = Transformer.from_crs(4326, 26986, always_xy=True); x0, y0, x1, y1 = meta['box']; RP = np.column_stack([Q['x'], Q['y']]); t = cKDTree(RP)
    cnt = np.bincount(Q['seg']).astype(float); out = []
    for L in labels:
        X, Y = [], []
        for part in L['lines']:
            a = np.asarray(part, float); px, py = tr.transform(a[:, 0], a[:, 1]); px, py = np.atleast_1d(px), np.atleast_1d(py)
            for k in range(max(1, len(px) - 1)):
                if len(px) == 1: X.append(px); Y.append(py); break
                m = max(1, int(math.ceil(math.hypot(px[k + 1] - px[k], py[k + 1] - py[k]) / 5.0))); u = np.arange(m + 1) / m
                X.append(px[k] + u * (px[k + 1] - px[k])); Y.append(py[k] + u * (py[k + 1] - py[k]))
        X = np.concatenate(X); Y = np.concatenate(Y); ib = (X >= x0) & (X < x1) & (Y >= y0) & (Y < y1)
        if not ib.any(): continue
        LP = np.column_stack([X[ib], Y[ib]])
        d, _ = cKDTree(LP).query(RP, distance_upper_bound=radius); near = np.isfinite(d)
        s1 = np.bincount(Q['seg'][near], minlength=len(cnt)) / np.maximum(cnt, 1)
        d2, i2 = t.query(LP, distance_upper_bound=radius); ok = np.isfinite(d2)
        s2 = np.bincount(Q['seg'][i2[ok]], minlength=len(cnt)) / len(LP)
        segs = np.nonzero((s1 >= share) | (s2 >= share))[0]
        if len(segs): out.append((L, segs.astype(int)))
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
    if r.get('p_freeboard', 0) >= 0.1 and r.get('freeboard_m') is not None:
        fb = r['freeboard_m']
        bits.append(f"water beside the road {'%.2f m above' % -fb if fb < 0 else '%.2f m below' % fb} its crest (design freeboard 0.30 m; P {r['p_freeboard']:.2f})")
    if r.get('p_dv', 0) >= 0.1 and r.get('dv_m2s') is not None: bits.append(f"fast water: depth x speed {r['dv_m2s']:.2f} m2/s (small cars unstable from 0.3)")
    if r.get('p_washout', 0) >= 0.1 and r.get('peak_speed_ms') is not None: bits.append(f"overtopping at {r['peak_speed_ms']:.1f} m/s at a stream crossing (grass-covered fill erodes from ~1.5 m/s)")
    if r.get('p_sag', 0) >= 0.1 and r.get('sag_why'): bits.append(f"{r['sag_why']} (P {r['p_sag']:.2f})")
    if r.get('p_culvert', 0) >= 0.1 and r.get('culvert_why'): bits.append(r['culvert_why'])
    elif r['culvert_overtopped_nearby']: bits.append('a culvert within 100 m is overtopped')
    if r['adds_hospital_min'] and r['adds_hospital_min'] >= 5: bits.append(f"+{r['adds_hospital_min']:.0f} min to the nearest hospital")
    if r['cut_off_hospital']: bits.append('cut off from hospitals')
    return '; '.join(bits)


def run(run_dir, out, segments, crossings, reports, facilities, repeat_csv, top=30, culvert_rule=False, labels_csv=None, blockage=True, freeboard=False, fastwater=False):
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
    bx, by, broute = [], [], []
    nbi_p = os.environ.get('PROTO_NBI') or os.path.join(ROOT, 'docs', 'network', 'nbi_ma.json')     # bridges whose decks the lidar removed
    if os.path.exists(nbi_p):
        from pyproj import Transformer as _T
        NB = json.load(open(nbi_p)); c = NB['columns']; il, ia, ic = c.index('lon'), c.index('lat'), c.index('culvert')
        rows_b = [r_ for r_ in NB['rows'] if not r_[ic]]
        bx, by = _T.from_crs(4326, 26986, always_xy=True).transform([r_[il] for r_ in rows_b], [r_[ia] for r_ in rows_b])
        bx, by = np.atleast_1d(bx), np.atleast_1d(by)
        ir = c.index('route') if 'route' in c else None
        broute = [int(''.join(ch for ch in str(r_[ir]) if ch.isdigit()) or 0) if ir is not None else 0 for r_ in rows_b]
    # ELEVATED ROADS (default on; PROTO_BRIDGES=0 for the old behaviour): (1) whole bridge decks, not just 30 m around the NBI point: points
    # in a gap of the road's own lidar profile carried by an NBI bridge of the same route (impacts.deck_points) are dropped; (2) Interstates:
    # depth on the road = max(0, water surface - lidar road crest) (impacts.point_depth with dz = z_raw_max10 - model ground), so water in a
    # 20 m cell beside or under an embankment / notch is not read as water on the travel lanes.  Other classes keep the cell depth: at local
    # crossings the cell depth is the proxy that finds the documented culvert failures (crest-relative depth everywhere: Leominster recall
    # 0.385 -> 0.08), and the 20 m crest (highest 10 m quarter) overstates a street's surface beside a bank.
    ZRf = load_npz(os.path.join(run_dir, 'z_raw.npz')); shp = tuple(meta['shape'])
    ZC_ = (ZRf['z_raw_max10'] if 'z_raw_max10' in ZRf else ZRf['z_raw']).astype(np.float32) if ZRf is not None and ZRf['z_raw'].shape == shp else None
    bridges_on = os.environ.get('PROTO_BRIDGES', '1') == '1' and ZC_ is not None and R['Z'] is not None
    geo = dict(rule='on' if bridges_on else 'off (PROTO_BRIDGES=0 or no z_raw.npz)', deck_gap_m=DECK_GAP_M, deck_radius_m=DECK_RADIUS_M, deck_nbi_m=DECK_NBI_M)
    roads_ = S['props']['road']; cls_all = np.asarray(props['cls'])
    import re as _re                                            # Interstates: class 2 named I-nn (MA class 2 is exactly the Interstates)
    interstate = np.array([k_ == 2 and bool(_re.match(r'\s*I[- ]?\d', nm_ or '')) for k_, nm_ in zip(props['cls'], roads_)], bool)
    _orig_rp = getattr(IM, '_road_points_orig', IM.road_points); IM._road_points_orig = _orig_rp; _cache = {}     # never wrap a wrapper (repeated runs)
    def road_points_no_bridges(S_, meta_, step=None):
        P_ = _orig_rp(S_, meta_, step)
        if not len(P_['x']): return P_
        keep_ = np.ones(len(P_['x']), bool)
        if WM is not None and WM.shape == tuple(meta_['shape']): keep_ &= ~WM[P_['r'], P_['c']]
        if len(bx):
            from scipy.spatial import cKDTree as _K
            d_, _ = _K(np.column_stack([bx, by])).query(np.column_stack([P_['x'], P_['y']])); keep_ &= d_ > 30
        dz_ = None
        if bridges_on and tuple(meta_['shape']) == shp:
            if 'deck' not in _cache:
                zc_ = ZC_[P_['r'], P_['c']]; _cache['G'] = IM.road_graph(P_)
                _cache['deck'] = IM.deck_points(P_, zc_, shp, res, roads_, bx, by, broute, DECK_GAP_M, DECK_RADIUS_M, DECK_NBI_M, G=_cache['G']) if len(bx) else np.zeros(len(zc_), bool)
                _cache['P'] = P_
                geo.update(deck_points_dropped=int((_cache['deck'] & keep_).sum()), deck_segments=int(len(np.unique(P_['seg'][_cache['deck'] & keep_]))))
            keep_ &= ~_cache['deck']
            dz_ = np.where(interstate[P_['seg']], np.maximum(ZC_[P_['r'], P_['c']] - R['Z'][P_['r'], P_['c']], 0.0), 0.0).astype(np.float32)
        P_ = {k: v[keep_] for k, v in P_.items()}
        if dz_ is not None: P_['dz'] = dz_[keep_]
        return P_
    IM.road_points = road_points_no_bridges

    # 4 first: the existing impacts layer (depth classes, network, crossings, report scores)
    imp, _ = IM.analyse([R], S, Xrows, rep, fac)
    seg_cols = imp['seg_columns']; net = {row[0]: dict(zip(seg_cols, row)) for row in imp['seg_rows']}

    # 1-2 hazard and flashness along every segment (same densified points as impacts)
    P = IM.road_points(S, meta); mx, mean, dv, inbox = IM.sample_segments(n, P, H, R['V'])
    use0 = ~P['end'] | (np.bincount(P['seg'][~P['end']], minlength=n)[P['seg']] == 0)
    use = ~P['end'] | (np.bincount(P['seg'][~P['end']], minlength=n)[P['seg']] == 0); Q = {k: v[use] for k, v in P.items()}
    dq = IM.point_depth(Q, H)                                                   # depth on the road (crest-relative on Interstates)
    mx = np.where(inbox, seg_top2(n, Q['seg'], dq), 0).astype(np.float32)
    # timing grids hold the cell depth; where the crest offset leaves the road below 30 / 15 cm, the road never reached it
    hrs30 = seg_reduce(n, Q['seg'], np.where(dq >= 0.30, T['tover30'][Q['r'], Q['c']], 0), 'max') if T else np.zeros(n, np.float32)
    hrs15 = seg_reduce(n, Q['seg'], np.where(dq >= 0.15, T['tover15'][Q['r'], Q['c']], 0), 'max') if T else np.zeros(n, np.float32)
    arr30 = seg_reduce(n, Q['seg'], np.where(dq >= 0.30, T['tarr30'][Q['r'], Q['c']], np.nan), 'min') if T else np.full(n, np.nan, np.float32)
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
        dzc = np.round(Q['dz'] * 100).astype(np.float32) if 'dz' in Q else 0.0
        for k in range(len(DC)): seg_t[k] = np.round(seg_top2(n, Q['seg'], np.maximum(DC[k][Q['r'], Q['c']].astype(np.float32) - dzc, 0))).astype(np.uint16)
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

    # FREEBOARD and FAST-WATER rules (per road point, second-highest point value per segment like the depth rule)
    ZRf = load_npz(os.path.join(run_dir, 'z_raw.npz')); VEL = load_npz(os.path.join(run_dir, 'vel_max.npz')); shp = tuple(meta['shape'])
    pot = np.zeros(n, np.float32); pfb = np.zeros(n, np.float32); fbm = np.full(n, np.nan, np.float32); pfw = np.zeros(n, np.float32); pdv_s = np.zeros(n, np.float32)
    pws_s = np.zeros(n, np.float32); spd = np.full(n, np.nan, np.float32); dvs = np.full(n, np.nan, np.float32); edited = np.zeros(shp, bool)
    rules = dict(freeboard='unavailable (no z_raw.npz in the run dir)', fastwater='unavailable (no vel_max.npz: run w9 with LF_VOUT=1)')
    if ZRf is not None and R['Z'] is not None and ZRf['z_raw'].shape == shp and len(Q['x']):
        ZR = ZRf['z_raw'].astype(np.float32); ZC = ZRf['z_raw_max10'].astype(np.float32) if 'z_raw_max10' in ZRf else ZR
        road_cells = np.zeros(shp, bool); road_cells[P['r'], P['c']] = True
        WA, edited = adjacent_wse(H, R['Z'], ZR, road_cells, res)
        fq = (ZC[Q['r'], Q['c']] - WA[Q['r'], Q['c']]).astype(np.float64)        # +inf: no water within 30 m
        pfb = np.where(inbox, seg_top2(n, Q['seg'], p_freeboard(fq).astype(np.float32)), 0.0).astype(np.float32)
        pot = np.where(inbox, seg_top2(n, Q['seg'], p_overtop(fq).astype(np.float32)), 0.0).astype(np.float32)
        f2 = -seg_top2(n, Q['seg'], -np.minimum(fq, 99.0).astype(np.float32)); fbm = np.where(inbox & (f2 < 99.0), f2, np.nan).astype(np.float32)
        rules['freeboard'] = dict(margin_m=FB_MARGIN_M, sigma_m=FB_SIGMA_M, radius_m=FB_RADIUS_M, wet_m=FB_WET_M, crest='z_raw_max10' if 'z_raw_max10' in ZRf else 'z_raw',
                                  road_points_with_water_near=int(np.isfinite(fq).sum()), road_points=int(len(fq)), edited_cells=int(edited.sum()))
    if VEL is not None and VEL['vmax'].shape == shp and len(Q['x']):
        Vg = np.nan_to_num(VEL['vmax']).astype(np.float32); DVg = np.nan_to_num(VEL['dvmax']).astype(np.float32)
        unm = ~edited[Q['r'], Q['c']]; near = np.zeros(len(Q['x']), bool)
        xl = [(r_['lon'], r_['lat']) for r_ in Xrows if r_.get('lon') is not None]
        if xl:
            from scipy.spatial import cKDTree as _K
            xx_, yy_ = Transformer.from_crs(4326, 26986, always_xy=True).transform([a for a, _ in xl], [b for _, b in xl])
            dq, _ = _K(np.column_stack([xx_, yy_])).query(np.column_stack([Q['x'], Q['y']])); near = dq <= XING_SEG_M
        hq = dq; vq = np.where(unm, Vg[Q['r'], Q['c']], 0.0); hc = H[Q['r'], Q['c']]            # DV scaled to the depth on the road (Interstate crest)
        fz = np.where(Q['dz'] > 0, np.where(hc > 1e-6, np.minimum(dq / np.maximum(hc, 1e-6), 1.0), 0.0), 1.0) if 'dz' in Q else 1.0
        dq_ = np.where(unm, DVg[Q['r'], Q['c']] * fz, 0.0)
        pfq, pdq, pwq = p_fastwater(dq_, vq, hq, near & unm)
        pfw = np.where(inbox, seg_top2(n, Q['seg'], pfq.astype(np.float32)), 0.0).astype(np.float32)
        pdv_s = np.where(inbox, seg_top2(n, Q['seg'], pdq.astype(np.float32)), 0.0).astype(np.float32)
        pws_s = np.where(inbox, seg_top2(n, Q['seg'], pwq.astype(np.float32)), 0.0).astype(np.float32)
        spd = np.where(inbox, seg_top2(n, Q['seg'], np.where(hq >= 0.05, vq, 0.0).astype(np.float32)), np.nan).astype(np.float32)
        dvs = np.where(inbox, seg_top2(n, Q['seg'], dq_.astype(np.float32)), np.nan).astype(np.float32)
        rules['fastwater'] = dict(dv0_m2s=DV0_M2S, dv_sigma_ln=DV_SIGMA_LN, v_erode_ms=V_ERODE_MS, v_sigma_ln=V_SIGMA_LN, erode_min_h_m=ERODE_MIN_H_M,
                                  road_points_near_crossing=int((near & unm).sum()), velocity_source=str(VEL.get('vmax_source', '')), dv_source=str(VEL.get('dv_source', '')))
    # SAG / UNDERPASS layer (optional, never in p_close): road sags whose storm drains are overwhelmed (sag_probability)
    psag = np.zeros(n, np.float32); sag_why = {}; sags = []
    if ZRf is not None and ZRf['z_raw'].shape == shp and len(Q['x']):
        PA = _cache.get('P') or IM._road_points_orig(S, meta); GA = _cache.get('G') or IM.road_graph(PA)
        dk = _cache.get('deck', np.zeros(len(PA['x']), bool))
        xl = [(r_['lon'], r_['lat']) for r_ in Xrows if r_.get('lon') is not None]
        xxy = np.column_stack(tr.transform([a for a, _ in xl], [b for _, b in xl])) if xl else np.zeros((0, 2))
        bad = dk | (WM[PA['r'], PA['c']] if WM is not None and WM.shape == shp else False)
        try:
            sags = sag_probability(PA, GA, ZRf['z_raw'].astype(np.float32), R['Z'], H, RS['peak1h'] if RS else None, res, cls_all, bad,
                                   np.column_stack([bx, by]) if len(bx) else np.zeros((0, 2)), xxy, PA['x'][dk], PA['y'][dk])
        except Exception as e_:                                  # optional layer: never stops the closure outputs
            sags = []; print('sag layer failed:', repr(e_)[:300]); rules['sag_error'] = repr(e_)[:300]
        if sags and len(Q['x']):
            tq = cKDTree(np.column_stack([Q['x'], Q['y']]))
            for g_ in sags:
                for sg in np.unique(Q['seg'][tq.query_ball_point([g_['x'], g_['y']], SAG_SEG_M)]):
                    if g_['p'] > psag[sg] or sg not in sag_why:
                        psag[sg] = max(psag[sg], g_['p'])
                        sag_why[int(sg)] = (f"road sag {g_['depth_m']:.1f} m deep ({'underpass, ' if g_['under'] else ''}drains sized for the {g_['design']}-yr hour, "
                                            f"{g_['i_design_mm']:.0f} mm; peak hour here {g_['i_peak_mm']:.0f} mm; catchment {g_['area_ha']:.1f} ha)")
        psag = np.where(inbox, psag, 0.0).astype(np.float32)
        rules['sag'] = dict(sags=len(sags), underpasses=sum(1 for g_ in sags if g_['under']), sags_p_ge_50=sum(1 for g_ in sags if g_['p'] >= 0.5),
                            from_rain=sum(1 for g_ in sags if g_['p_rain'] >= 0.5), from_model_ponding=sum(1 for g_ in sags if g_['p_pond'] >= 0.5),
                            min_depth_m=SAG_MIN_M, radius_m=SAG_RADIUS_M, i10_mm=I10_MM, i50_mm=I50_MM, runoff_c=SAG_C, sigma_ln=SAG_SIGMA_LN,
                            note='candidate layer, not in p_close; variant sag = max(p_depth, p_sag) (the ponding half re-reads the model water the depth rule reads)')
    rules['bridges'] = geo
    VAR = {'depth': p_depth, 'overtop': combine(p_depth, pot), 'freeboard': combine(p_depth, pfb), 'fastwater': combine(p_depth, pfw), 'both': combine(p_depth, pfb, pfw),
           'sag': np.maximum(p_depth, psag)}
    for k_ in list(VAR): VAR[k_ + '+culvert'] = combine(VAR[k_], pcul)
    VAR = {k_: np.where(inbox, v_, 0.0).astype(np.float32) for k_, v_ in VAR.items()}
    vkey = ('both' if freeboard and fastwater else 'freeboard' if freeboard else 'fastwater' if fastwater else 'depth') + ('+culvert' if culvert_rule else '')
    pclose = VAR[vkey]
    pmay = np.where(inbox, combine(pclose, pot), 0.0).astype(np.float32)        # 'may close' layer: main rule OR overtopping
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
                 p_overtop=round(float(pot[i]), 3), p_may_close=round(float(pmay[i]), 3), p_sag=round(float(psag[i]), 3), sag_why=sag_why.get(int(i)),
                 p_freeboard=round(float(pfb[i]), 3), freeboard_m=None if np.isnan(fbm[i]) else round(float(fbm[i]), 2),
                 p_fastwater=round(float(pfw[i]), 3), p_dv=round(float(pdv_s[i]), 3), p_washout=round(float(pws_s[i]), 3),
                 peak_speed_ms=None if np.isnan(spd[i]) else round(float(spd[i]), 2), dv_m2s=None if np.isnan(dvs[i]) else round(float(dvs[i]), 2),
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
    if labels_csv and labels_csv.endswith('.geojson') and os.path.exists(labels_csv):     # closed stretches (lines): strict 30 m, loose 100 m
        LB = load_line_labels(labels_csv); LM = label_segments_lines(LB, Q, meta, 30.0); LL = label_segments_lines(LB, Q, meta, 100.0)
    else:
        LB = load_labels(labels_csv); LM = label_segments(LB, Q, props, meta, strict=True); LL = label_segments(LB, Q, props, meta, strict=False)
    if LM or LL:
        checks['labels_segments'] = dict(note='recall = share of documented sites with a matched segment at P >= 0.5; random_recall = the same for random flagging of the '
                                              'same share of segments; lift = recall / random_recall; lift_naive = recall / flagged share. strict: segments within 30 m '
                                              'of the site; loose: 100 m (exact) / 300 m + same-name segments within 1.5 km (approx). Line labels (.geojson): '
                                              'segments with >= 50 % of their points within 30 m (loose 100 m) of the closed stretch, or holding >= 50 % of it',
                                         labels=os.path.basename(labels_csv or ''), labels_in_file=len(LB), sites_matched=len(LM),
                                         depth_rule=label_recall(LM, p_depth, inbox), with_culverts=label_recall(LM, p_comb, inbox),
                                         loose=dict(sites_matched=len(LL), depth_rule=label_recall(LL, p_depth, inbox), with_culverts=label_recall(LL, p_comb, inbox)),
                                         variants={k_: dict(strict=label_recall(LM, v_, inbox), loose=label_recall(LL, v_, inbox), split_strict=label_split(LM, v_, inbox))
                                                   for k_, v_ in VAR.items()}, applied=vkey,
                                         sites=[dict(id=L.get('id'), type=L.get('type'), name=L.get('name'), road=L.get('road'), n_segments=len(sg_),
                                                     depth_m=round(float(mx[sg_].max()), 2), freeboard_m=None if np.isnan(fbm[sg_]).all() else round(float(np.nanmin(fbm[sg_])), 2),
                                                     dv_m2s=None if np.isnan(dvs[sg_]).all() else round(float(np.nanmax(dvs[sg_])), 2),
                                                     peak_speed_ms=None if np.isnan(spd[sg_]).all() else round(float(np.nanmax(spd[sg_])), 2),
                                                     p_depth=round(float(p_depth[sg_].max()), 3), p_freeboard=round(float(pfb[sg_].max()), 3), p_fastwater=round(float(pfw[sg_].max()), 3),
                                                     p_culvert=round(float(pcul[sg_].max()), 3), p_sag=round(float(psag[sg_].max()), 3), hit=[k_ for k_, v_ in VAR.items() if (v_[sg_] >= 0.5).any()]) for L, sg_ in LM])
    checks['rules'] = dict(rules, applied=vkey, segments_p_ge_50={k_: int((v_[inbox] >= 0.5).sum()) for k_, v_ in VAR.items()})
    checks['culverts'] = dict(surveyed_in_box=len(CP), with_model_flow=sum(1 for c in CP if c['q_m3s'] is not None), p_ge_50=sum(1 for c in CP if c['p'] >= 0.5),
                              segments_raised_to_p_ge_50=int(((p_comb >= 0.5) & (p_depth < 0.5) & inbox).sum()), rule_applied_to_p_close=bool(culvert_rule),
                              blockage_factors=BLOCKAGE if blockage else {}, probability='Phi(ln(Q / Q_crest) / 0.30) = P(HDS-5 headwater > road crest)')

    # outputs
    keep = [r for r in rows if r['peak_depth_m'] >= 0.05 or r['p_close'] >= 0.1 or r['p_may_close'] >= 0.1 or r['p_sag'] >= 0.1 or r['cut_off_hospital'] or r['adds_hospital_min'] >= 5]
    write_geojson(os.path.join(out, 'segments.geojson'), S, keep)
    for r in rows: r.pop('d', None)
    with open(os.path.join(out, 'watchlist.csv'), 'w', newline='') as f:
        cols = ['rank', 'p_close', 'p_depth', 'p_culvert', 'p_freeboard', 'p_fastwater', 'p_dv', 'p_washout', 'road', 'town', 'road_class', 'peak_depth_m', 'freeboard_m',
                'peak_speed_ms', 'dv_m2s', 'hours_over_30cm', 'arrival_h', 'peak1h_mm', 'flashness_pct',
                'culvert_overtopped_nearby', 'adds_hospital_min', 'aadt', 'segment', 'why']
        w = csv.writer(f); w.writerow(cols)
        for k, r in enumerate(rows[:top]): w.writerow([k + 1] + [r[c] for c in cols[1:]])
    summ = dict(run=R['name'], model=meta.get('model'), storm_start=meta.get('t0'), box_epsg26986=meta['box'], resolution_m=res,
                segments_in_box=int(inbox.sum()), closures_expected=round(float(pclose[inbox].sum()), 1),
                segments_p_ge_50=int((pclose[inbox] >= 0.5).sum()), segments_p_ge_90=int((pclose[inbox] >= 0.9).sum()),
                segments_may_close=int(((pmay >= 0.5) & (pclose < 0.5) & inbox).sum()),
                km_may_close=round(float(np.asarray(props['len'], float)[inbox & (pmay >= 0.5) & (pclose < 0.5)].sum() / 1000), 1),
                may_close_rule='water beside the road reaches the road crest: Phi((0 - f) / 0.15), f = lidar crest - peak water surface within 30 m; candidate, '
                               'not in p_close until confirmed on a second storm',
                segments_sag=int(((psag >= 0.5) & (pclose < 0.5) & inbox).sum()),
                sag_rule='optional layer: road sag / underpass in a closed lidar depression whose drains (HEC-22 10-yr, 50-yr at underpasses) are exceeded '
                         'by the peak-hour rain on its catchment, or where the model ponds 0.30 m; not in p_close or p_may_close',
                segments_p_ge_50_depth_rule=int((p_depth[inbox] >= 0.5).sum()), segments_p_ge_50_with_culverts=int((p_comb[inbox] >= 0.5).sum()),
                km_p_ge_50=round(float(np.asarray(props['len'], float)[inbox & (pclose >= 0.5)].sum() / 1000), 1),
                culverts_overtopped=sum(1 for x in xs if x['status'] == 'overtopped'), culverts_surcharged=sum(1 for x in xs if x['status'] == 'surcharged'),
                crossings_assessed=len(xs), cut_off_from_hospitals=imp['summary']['cut_off_from_hospitals'], worst_added_minutes=imp['summary']['worst_delay_min'],
                rain_max_total_mm=meta.get('rain_total_max_mm'), rain_peak1h_max_mm=round(float(RS['peak1h'].max()), 1) if RS else None,
                flood_model_runtime_s=meta.get('runtime_s'), solver=meta.get('solver'), checks=checks,
                method=dict(closure_depth_m=FAIL_M, sigma_m=SIGMA_M, variant=vkey, probability='Phi((peak depth - 0.30) / 0.10), physics prior v0'
                            + (' ; freeboard: P_fb = Phi((0.30 - f) / 0.15), f = road crest (lidar before hydraulic edits) - peak water surface within 30 m' if freeboard else '')
                            + (' ; fast water: P_dv = Phi(ln(DV / 0.3) / 0.35) on road cells, washout Phi(ln(V / 1.5) / 0.30) at crossings' if fastwater else '')
                            + (' ; culvert overtopping: P_culvert = P(HDS-5 headwater > road crest) = Phi(ln(Q / Q_crest) / 0.30)' if culvert_rule else '')
                            + ('; combined 1 - prod(1 - P_i), second-highest road point per segment' if (freeboard or fastwater or culvert_rule) else ''),
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
         f"| Further segments that may close (stream reaches the road crest) | {s.get('segments_may_close', 0)} ({s.get('km_may_close', 0)} km) |",
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
    L += ['', f"Closure probability ({s['method'].get('variant', 'depth')}): {s['method']['probability']}. A physics prior from published thresholds, not calibrated on observed closures."]
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
<label><input type="checkbox" data-l="may" checked> May close: stream at road level</label>
<label><input type="checkbox" data-l="sag"> Sags / underpasses: drains overwhelmed (test layer)</label>
<label id="rkl" style="display:none"><input type="checkbox" data-l="risk"> Risk class (flagged segments)</label>
<div style="margin-top:6px"><span class="k" style="background:#b2182b"></span>closed now (&ge; 30 cm)<br><span class="k" style="background:#f4a582"></span>15&ndash;30 cm<br>
<span class="k" style="background:#9ecae1"></span>wet<br><span class="k" style="background:#555;height:2px"></span>closes at peak<br><span class="k" style="background:#e08214;height:3px"></span>may close (stream reaches road level)<br><span class="k" style="background:#7b3294;height:3px"></span>sag / underpass (test layer)</div>
<div id="rkk" style="display:none;margin-top:4px">Risk: <span class="k" style="background:#7f0000;width:10px"></span>Extreme <span class="k" style="background:#e34a33;width:10px"></span>High <span class="k" style="background:#fdbb84;width:10px"></span>Medium <span class="k" style="background:#c7e9c0;width:10px"></span>Low</div>
<div id="rs" style="margin-top:6px;font-size:12px"></div></div>
<div id="t"><button id="play">&#9654;</button><input id="sl" type="range" min="0" value="0"><span id="clock"></span><span id="cnt"></span><svg id="rain"></svg></div>
<script>
const S=__SUMMARY__, C=__CORNERS__, FH=S.frame_hours||[], NF=FH.length, T0=new Date(S.storm_start.replace('Z',':00Z'));
const CLS={0:'local / collector',1:'arterial',2:'highway'};
const RC={Extreme:'#7f0000',High:'#e34a33',Medium:'#fdbb84',Low:'#c7e9c0'};let RK={};
const fmt=v=>v==null?'–':Math.round(v).toLocaleString('en-US'),usd=v=>v==null?'–':v>=1e6?'$'+(v/1e6).toFixed(1)+'M':'$'+Math.round(v/1e3)+'k';
const getj=u=>fetch(u).then(r=>r.ok?r.json():null).catch(()=>null);
getj('resilience.json').then(R=>{const P=R&&R.population;if(!P||!P.worst)return;const w=P.worst,ph=P.person_hours_lost||{};
 document.getElementById('rs').innerHTML=`<b>Residents, worst time in the storm</b><br>losing coverage: fire ${fmt(w.fire_station&&w.fire_station.people)} · police ${fmt(w.police&&w.police.people)} · hospital ${fmt(w.hospital&&w.hospital.people)}<br>isolated ${fmt(P.isolated_worst&&P.isolated_worst.people)} · ${fmt(ph.sum_three_services)} person-hours without coverage`});
function riskHtml(id){const e=RK[id];if(!e)return'';let h='';const a=e.a,r=e.r;
 if(a)h+=`<hr style="margin:4px 0;border:0;border-top:1px solid #ddd"><b>If this segment closes</b> (residents losing access):<br>hospital 30 min ${fmt(a.h)} · fire 8 min ${fmt(a.f)} · police 10 min ${fmt(a.p)}<br>isolated ${fmt(a.iso)}${a.own?` <small>(+${fmt(a.own)} living on it)</small>`:''}<br>`;
 if(r)h+=`Risk class: <b style="color:${RC[r.risk]}">${r.risk}</b> (L${r.L} × C${r.C}, ${r.by})<br>repair ${usd(r.repair[0])}–${usd(r.repair[1])} + delay ${usd(r.delay)}<br>`;
 (e.x||[]).forEach(x=>{h+=`<small>crossing ${x.stream||''}: <b style="color:${RC[x.risk]}">${x.risk}</b>, replace ${usd(x.repair[0])}–${usd(x.repair[1])}</small><br>`});return h}
document.getElementById('s').innerHTML=`At peak: ${S.segments_p_ge_50} segments likely closed (${S.km_p_ge_50} km); ${S.segments_may_close??0} more may close (${S.km_may_close??0} km); ${S.culverts_overtopped} culverts overtopped.<br><br>`;
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
Promise.all([fetch('segments.geojson').then(r=>r.json()),getj('risk_segments.json')]).then(([g,rk])=>{RK=(rk&&rk.segments)||{};
g.features.forEach(f=>{const e=RK[f.properties.segment];if(e&&e.r)f.properties.risk=e.r.risk});if(Object.keys(RK).length){document.getElementById('rkl').style.display='block'}
m.addSource('s',{type:'geojson',data:g});
m.addLayer({id:'peak',type:'line',source:'s',filter:['>=',['get','p_close'],0.5],paint:{'line-color':'#555','line-width':1,'line-dasharray':[2,2]}});
m.addLayer({id:'may',type:'line',source:'s',filter:['all',['>=',['coalesce',['get','p_may_close'],0],0.5],['<',['get','p_close'],0.5]],paint:{'line-color':'#e08214','line-width':2.5,'line-dasharray':[1,1]}});
m.addLayer({id:'sag',type:'line',source:'s',layout:{visibility:'none'},filter:['all',['>=',['coalesce',['get','p_sag'],0],0.5],['<',['get','p_close'],0.5]],paint:{'line-color':'#7b3294','line-width':2.5,'line-dasharray':[1,1]}});
m.addLayer({id:'risk',type:'line',source:'s',layout:{visibility:'none'},filter:['has','risk'],paint:{'line-width':4,'line-color':['match',['get','risk'],'Extreme',RC.Extreme,'High',RC.High,'Medium',RC.Medium,RC.Low]}});
m.addLayer({id:'seg',type:'line',source:'s',paint:{'line-width':3,'line-color':'#b2182b'}});
const pop=e=>{if(e.originalEvent._pop)return;e.originalEvent._pop=1;const p=e.features[0].properties;new maplibregl.Popup().setLngLat(e.lngLat).setHTML(`<b>${p.road||'(unnamed)'}, ${p.town}</b><br>${p.road_class}<br>Chance of closing at peak: ${(+p.p_close*100).toFixed(0)}%<br>${(+(p.p_may_close||0))>=0.5&&(+p.p_close)<0.5?`<b style="color:#e08214">May close: stream reaches road level (${(+p.p_overtop*100).toFixed(0)}%)</b><br>`:''}${(+(p.p_sag||0))>=0.5&&(+p.p_close)<0.5?`<b style="color:#7b3294">Sag / underpass: drains may be overwhelmed (${(+p.p_sag*100).toFixed(0)}%, test layer)</b><br>`:''}<small>depth ${(+p.p_depth*100).toFixed(0)}% · freeboard ${(+(p.p_freeboard||0)*100).toFixed(0)}% · fast water ${(+(p.p_fastwater||0)*100).toFixed(0)}% · culvert ${(+(p.p_culvert||0)*100).toFixed(0)}%</small><br>${p.why}${riskHtml(p.segment)}`).addTo(m)};m.on('click','seg',pop);m.on('click','risk',pop);m.on('click','peak',pop);m.on('click','may',pop);m.on('click','sag',pop);
m.on('mouseenter','seg',()=>m.getCanvas().style.cursor='pointer');m.on('mouseleave','seg',()=>m.getCanvas().style.cursor='');filt();show(0);});});
function filt(){const on=[...document.querySelectorAll('[data-c]')].filter(b=>b.checked).map(b=>CLS[b.dataset.c]);const cl=['in',['get','road_class'],['literal',on]];
 if(m.getLayer('seg'))m.setFilter('seg',cl);if(m.getLayer('peak'))m.setFilter('peak',['all',['>=',['get','p_close'],0.5],cl]);
 if(m.getLayer('may'))m.setFilter('may',['all',['>=',['coalesce',['get','p_may_close'],0],0.5],['<',['get','p_close'],0.5],cl]);
 if(m.getLayer('sag'))m.setFilter('sag',['all',['>=',['coalesce',['get','p_sag'],0],0.5],['<',['get','p_close'],0.5],cl])}
document.querySelectorAll('[data-c]').forEach(b=>b.onchange=filt);
document.querySelector('[data-l=may]').onchange=e=>{if(m.getLayer('may'))m.setLayoutProperty('may','visibility',e.target.checked?'visible':'none')};
document.querySelector('[data-l=sag]').onchange=e=>{if(m.getLayer('sag'))m.setLayoutProperty('sag','visibility',e.target.checked?'visible':'none')};
document.querySelector('[data-l=risk]').onchange=e=>{document.getElementById('rkk').style.display=e.target.checked?'block':'none';if(m.getLayer('risk'))m.setLayoutProperty('risk','visibility',e.target.checked?'visible':'none')};
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
    # freeboard: road on a 1 m fill (row 3) beside a flooded field; the road's own wet cells never count, a notched culvert pool does
    Zt = np.full((7, 7), 100.0); Zt[3] = 101.0; ZRt = Zt.copy(); rc = np.zeros((7, 7), bool); rc[3] = True
    Ht = np.zeros((7, 7)); Ht[4:] = 0.5; Ht[3] = 0.5                                       # field 0.5 m deep (WSE 100.5); 0.5 m on the road itself
    WA, ed = adjacent_wse(Ht, Zt, ZRt, rc, 20.0)
    assert abs(WA[3, 1] - 100.5) < 1e-9 and not ed.any() and p_freeboard(np.array([ZRt[3, 1] - WA[3, 1]]))[0] < 0.1     # 0.5 m freeboard: low
    Ht[4:] = 0.9; WA, _ = adjacent_wse(Ht, Zt, ZRt, rc, 20.0); assert p_freeboard(np.array([101.0 - WA[3, 1]]))[0] > 0.9   # 0.1 m freeboard: high
    Ht[4:] = 0.0; Zt[3, 5] = 99.0; Ht[3, 5] = 1.8                                          # notch at (3, 5) holding a pool at 100.8
    WA, ed = adjacent_wse(Ht, Zt, ZRt, rc, 20.0); assert ed[3, 5] and abs(WA[3, 4] - 100.8) < 1e-9 and np.isneginf(WA[3, 1])
    assert abs(p_freeboard(np.array([101.0 - WA[3, 4]]))[0] - float(phi(np.array([(0.30 - 0.2) / FB_SIGMA_M]))[0])) < 1e-9
    assert p_freeboard(np.array([105.0 - 100.8, np.inf])).max() < 1e-6                         # a road 4 m above the river, and one with no water near
    pf, pd_, pw_ = p_fastwater(np.array([0.3, 0.6, 0.0, 0.0, 0.0]), np.array([0, 0, 1.5, 1.5, 3.0]), np.array([0.5, 0.5, 0.2, 0.05, 0.2]),
                               np.array([False, False, True, True, False]))
    assert abs(pd_[0] - 0.5) < 1e-9 and pd_[1] > 0.97 and abs(pw_[2] - 0.5) < 1e-9 and pw_[3] == 0 and pw_[4] == 0 and abs(pf[1] - pd_[1]) < 1e-12
    assert abs(combine(np.array([0.5]), np.array([0.5]))[0] - 0.75) < 1e-12
    # end to end with both rules: B St (0.2 m on the road, 0.2 m in the fields beside it) closes on freeboard; C St (dry) on depth x speed
    zr = np.zeros((ny, nx), np.float32); np.savez(f'{rd}/z_raw.npz', z_raw=zr, z_raw_max10=zr)
    DVt = np.zeros((ny, nx), np.float32); DVt[10] = 0.6; np.savez(f'{rd}/vel_max.npz', vmax=np.zeros((ny, nx), np.float32), dvmax=DVt, vmax_source=np.array('test'))
    s4 = run(rd, os.path.join(d, 'out4'), sp, xp, None, None, None, labels_csv=lp, freeboard=True, fastwater=True)
    rows4 = {r['road']: r for r in csv.DictReader(open(os.path.join(d, 'out4', 'watchlist.csv')))}
    assert float(rows4['B St']['p_freeboard']) > 0.99 and float(rows4['B St']['p_depth']) < 0.2 and float(rows4['B St']['freeboard_m']) == -0.2, rows4['B St']
    assert float(rows4['C St']['p_dv']) > 0.97 and float(rows4['C St']['p_fastwater']) > 0.97 and 'fast water' in rows4['C St']['why'] and 'crest' in rows4['B St']['why']
    v4 = s4['checks']['labels_segments']['variants']; assert set(v4) == {'depth', 'overtop', 'overtop+culvert', 'freeboard', 'fastwater', 'both', 'depth+culvert', 'freeboard+culvert', 'fastwater+culvert', 'both+culvert', 'sag', 'sag+culvert'}
    assert s4['segments_p_ge_50'] == 3 and {k: v for k, v in s4['checks']['rules']['segments_p_ge_50'].items() if not k.startswith(('overtop', 'sag'))} == {'depth': 1, 'freeboard': 2, 'fastwater': 2, 'both': 3, 'depth+culvert': 2,
                                                                                          'freeboard+culvert': 3, 'fastwater+culvert': 2, 'both+culvert': 3}, s4['checks']['rules']
    assert v4['fastwater']['strict']['culvert_washout']['recall'] == 1.0 and 'split_strict' in v4['both'] and s4['checks']['labels_segments']['applied'] == 'both'
    st4 = {x['id']: x for x in s4['checks']['labels_segments']['sites']}; assert 'fastwater' in st4['L1']['hit'] and 'depth' not in st4['L1']['hit']
    g4 = {f_['properties']['road'] for f_ in json.load(open(os.path.join(d, 'out4', 'segments.geojson')))['features']}; assert 'C St' in g4   # dry but flagged: on the map
    # 'may close' layer (depth rule as p_close): B St, dry road with water 0.2 m above its crest beside it, is not closed but may close
    s5 = run(rd, os.path.join(d, 'out5'), sp, xp, None, None, None, labels_csv=lp)
    rows5 = {r['road']: r for r in csv.DictReader(open(os.path.join(d, 'out5', 'watchlist.csv')))} if os.path.exists(os.path.join(d, 'out5', 'watchlist.csv')) else {}
    g5 = {f_['properties']['road']: f_['properties'] for f_ in json.load(open(os.path.join(d, 'out5', 'segments.geojson')))['features']}
    assert g5['B St']['p_close'] < 0.5 and g5['B St']['p_may_close'] >= 0.9 and abs(g5['B St']['p_overtop'] - float(phi(np.array([0.2 / FB_SIGMA_M]))[0])) < 1e-3, g5['B St']
    assert s5['segments_may_close'] >= 1
    assert 'may close' in open(os.path.join(d, 'out5', 'map.html')).read()
    # closed stretches as lines (Vermont layout): one along A St (matches A St only), one crossing all three streets (matches none)
    def ll(xa, ya, xb, yb): return [list(tr.transform(xa, ya)), list(tr.transform(xb, yb))]
    gp = os.path.join(d, 'closures.geojson')
    json.dump(dict(type='FeatureCollection', features=[
        dict(type='Feature', properties=dict(Road='A St', Cause='Flooding', FullorPart='Full'), geometry=dict(type='LineString', coordinates=ll(box[0] + 300, box[3] - 50 * res + 8, box[0] + 1200, box[3] - 50 * res + 8))),
        dict(type='Feature', properties=dict(Road='X Rd', Cause='Washout', FullorPart='Full'), geometry=dict(type='MultiLineString', coordinates=[ll(box[0] + 1000, box[3] - 5 * res, box[0] + 1000, box[3] - 95 * res)]))]), open(gp, 'w'))
    s6 = run(rd, os.path.join(d, 'out6'), sp, xp, None, None, None, labels_csv=gp)
    l6 = s6['checks']['labels_segments']; assert l6['labels_in_file'] == 2 and l6['sites_matched'] == 1 and l6['sites'][0]['road'] == 'A St', l6
    assert l6['variants']['depth']['strict']['flood_closure']['recall'] == 1.0 and l6['sites'][0]['n_segments'] == 1
    # Interstate crest: A St renamed I-99 (class 2) with its lidar crest 0.5 m above the model ground: 0.6 m in the cell is 0.1 m on the road
    import shutil
    rd7 = os.path.join(d, 'sep2023_i99'); shutil.copytree(rd, rd7)
    zc7 = np.zeros((ny, nx), np.float32); zc7[45:56] = 0.5; np.savez(f'{rd7}/z_raw.npz', z_raw=np.zeros((ny, nx), np.float32), z_raw_max10=zc7)
    S7 = json.loads(json.dumps(S)); S7['props']['road'][0] = 'I-99'; sp7 = os.path.join(d, 'segs7.json'); json.dump(S7, open(sp7, 'w'))
    s7 = run(rd7, os.path.join(d, 'out7'), sp7, xp, None, None, None)
    g7 = {f_['properties']['road']: f_['properties'] for f_ in json.load(open(os.path.join(d, 'out7', 'segments.geojson')))['features']}
    assert abs(g7['I-99']['peak_depth_m'] - 0.1) < 1e-3 and g7['I-99']['p_close'] < 0.05 and g7['I-99']['d'] == [0, 0, 10] and g7['I-99']['hours_over_30cm'] == 0, g7['I-99']
    assert s7['checks']['rules']['bridges']['rule'] == 'on' and s7['segments_p_ge_50'] == 0
    os.environ['PROTO_BRIDGES'] = '0'
    try: s8 = run(rd7, os.path.join(d, 'out8'), sp7, xp, None, None, None)
    finally: os.environ.pop('PROTO_BRIDGES')
    assert s8['segments_p_ge_50'] == 1 and s8['checks']['rules']['bridges']['rule'].startswith('off')        # old behaviour: cell depth 0.6 m
    # sags: a road across a 1 m deep bowl (no stream, no bridge) on a 10-cell grid; drains sized for the 10-yr hour (43 mm)
    from pyproj import Transformer as _T
    m9 = dict(box=[150000, 905000, 150400, 905400], res_m=20, shape=[20, 20])
    yy9, xx9 = np.mgrid[0:20, 0:20]; Z9 = (10.0 + 0.1 * np.hypot(yy9 - 9.5, xx9 - 9.5)).astype(np.float32)   # slopes in from every side
    Z9[8:12, 6:14] = 9.0; Z9[9:11, 9:11] = 8.8
    ll9 = _T.from_crs(26986, 4326, always_xy=True).transform([150010.0, 150390.0], [905200.0 - 10, 905200.0 - 10])
    S9 = dict(n=1, geo=[[[round(ll9[0][0] * 1e5), round(ll9[1][0] * 1e5), round(ll9[0][1] * 1e5) - round(ll9[0][0] * 1e5), round(ll9[1][1] * 1e5) - round(ll9[1][0] * 1e5)]]],
              props=dict(road=['B St'], town=['T'], cls=[0], low=[0], len=[380], aadt=[500]), links=[])
    P9 = IM.road_points(S9, m9); G9 = IM.road_graph(P9); H9 = np.zeros((20, 20), np.float32)
    def sp9(rain): return sag_probability(P9, G9, Z9, Z9, H9, np.full((20, 20), rain, np.float32), 20.0, np.array([0]), np.zeros(len(P9['x']), bool), np.zeros((0, 2)), np.zeros((0, 2)), [], [])
    lo9, hi9 = sp9(30.0), sp9(90.0)
    assert len(lo9) == 1 and lo9[0]['p'] == 0 and lo9[0]['design'] == 10 and lo9[0]['depth_m'] >= 1.2 and lo9[0]['area_ha'] == 16.0, lo9
    assert hi9[0]['p_rain'] > 0.9 and hi9[0]['v_excess_m3'] > hi9[0]['v_need_m3'], hi9
    H9[9:11, 9:11] = 0.6; assert sp9(30.0)[0]['p_pond'] > 0.9                                   # the model itself ponds 0.6 m there
    xy9 = np.array([[hi9[0]['x'], hi9[0]['y']]])
    sx9 = sag_probability(P9, G9, Z9, Z9, H9 * 0, None, 20.0, np.array([0]), np.zeros(len(P9['x']), bool), np.zeros((0, 2)), xy9, [], [])
    assert all(math.hypot(g_['x'] - xy9[0, 0], g_['y'] - xy9[0, 1]) > SAG_XING_M for g_ in sx9), sx9               # near a stream crossing: culvert's case
    assert sag_probability(P9, G9, Z9, Z9, H9 * 0, np.full((20, 20), 50.0, np.float32), 20.0, np.array([0]), np.zeros(len(P9['x']), bool), xy9 + 30, np.zeros((0, 2)), [], [])[0]['design'] == 50
    print('selftest ok:', out)


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--run-dir'); ap.add_argument('--out', default='proto_out'); ap.add_argument('--top', type=int, default=30)
    ap.add_argument('--segments', default=os.path.join(ROOT, 'docs', 'graph_segments.json'))
    ap.add_argument('--crossings', default=os.path.join(ROOT, 'docs', 'network', 'crossings_all.json'))
    ap.add_argument('--reports', default=os.path.join(ROOT, 'docs', 'prone', 'flood_reports.json'))
    ap.add_argument('--facilities', default=os.path.join(ROOT, 'docs', 'network', 'facilities.json'))
    ap.add_argument('--repeat', default=os.path.join(HERE, 'data', 'massdot_repeat_flood_d3.csv'))
    ap.add_argument('--storm', default=os.environ.get('STORM') or 'sep2023', help='storm id (env STORM; default sep2023) -> default labels file')
    ap.add_argument('--labels', help='default proto/data/labels_<storm>_*.csv (else .geojson)')
    ap.add_argument('--culvert-rule', action='store_true', default=os.environ.get('PROTO_CULVERT_RULE', '0') == '1',
                    help='P(close) = 1 - (1 - P_depth)(1 - P_culvert) (HDS-5 overtopping of surveyed culverts); both versions are scored either way')
    ap.add_argument('--freeboard', action='store_true', default=os.environ.get('PROTO_FREEBOARD', '0') == '1',
                    help='add P_freeboard (road crest less than 0.30 m above the water beside it); all variants are scored either way')
    ap.add_argument('--fastwater', action='store_true', default=os.environ.get('PROTO_FASTWATER', '0') == '1',
                    help='add P_fastwater (depth x speed on the road, washout speed at crossings; needs vel_max.npz from LF_VOUT=1)')
    ap.add_argument('--no-blockage', action='store_true', help='ignore NAACC inlet blockage in the culvert rule')
    ap.add_argument('--selftest', action='store_true')
    a = ap.parse_args()
    if not a.labels:
        import glob; a.labels = (sorted(glob.glob(os.path.join(HERE, 'data', f'labels_{a.storm}_*.csv'))) + sorted(glob.glob(os.path.join(HERE, 'data', f'labels_{a.storm}_*.geojson'))) or [None])[0]
    if a.selftest: selftest()
    else: run(a.run_dir, a.out, a.segments, a.crossings, a.reports, a.facilities, a.repeat, a.top, a.culvert_rule, a.labels, not a.no_blockage, a.freeboard, a.fastwater)
