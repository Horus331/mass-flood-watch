"""Cascade engine: how road flooding spreads its consequences across the network, frame by frame.

    python proto/cascade.py pack <site key> [<site key> ...]   # from the public replay packs docs/site/data/<key>/ -> docs/site/data/<key>/cascade.json
    python proto/cascade.py outdir <prototype --out folder>     # from a prototype.py output (segments.geojson 'd' + summary.json) -> <out>/cascade.json
    python proto/cascade.py --selftest                          # offline, synthetic ladder network

Write-up: docs/proto/cascade/CASCADE.md.  Nothing here changes p_close or any prototype / resilience output.  proto/prototype.py calls
`from_outdir` after a run only when PROTO_CASCADE=1 (opt-in).

Per output frame k (every 30 min of model time; the 5-min packs are sampled every 6th frame, frame ids are the viewer's):
  closed        road depth d >= 30 cm (= the deployed rule p_close = Phi((d - 0.30) / 0.10) >= 0.5)
  slowed        5 cm <= d < 30 cm: speed x f(d), Pregnolato et al. (2017) f = (0.0009 d^2 - 0.5529 d + 86.94) / 86.94 (d in mm), 0 at 30 cm
  detours       closed segments that touch form one stretch; its through traffic (largest AADT in the stretch) re-routes from the busiest open
                entry to the busiest open exit at another junction on the wet shortest path (whole District 3 graph, node-weighted by free-flow
                minutes x 1/f); extra minutes = wet - dry shortest time, capped at 30 min (no route within the cap: trips unserved)
                (proto/resilience.py closure_detours, extended here to return the detour path)
  delay         vehicle-hours per hour = sum_stretches q_s dt_s / 60 + sum_slowed q_i t0_i (1/f_i - 1) / 60, q = AADT / 24 (flat day)
  overload      every detour path carries its stretch's daytime volume H x AADT (H = 0.06 of AADT per daytime hour); per segment
                V/C = H (AADT_j + sum of detour AADT through j) / CAP[class]; overloaded when V/C > 1 and it carries detour traffic
  connectivity  2020 Census blocks (pop > 0) in the box on their nearest road segment; a block loses a service when it was within the standard
                dry (hospital 30 min, fire 8 min (NFPA 1710 travel), police 10 min) and is not now (its own segment closed, or no open
                facility within the standard); isolated = no route to any open hospital / fire / police (resilience.isolated_mask)
  culverts      road-stream crossings (docs/network/crossings_all.json) within 30 m of an in-box road: overtopped from the first frame the
                road there carries >= 15 cm (risk.py's 'water on the road within 30 m' rule, P = Phi((d - 0.15) / 0.10) >= 0.5).  Repair-cost
                exposure = risk.culvert_cost range of every crossing overtopped so far.  Stream knock-on: crossings on the same named stream
                within 3 km (downstream = larger drainage area drn_km2 where both have one, ~1 % of crossings; otherwise direction unresolved);
                reported whether they overtop too, the lag, and the linked crossings that stay dry (exposed to debris / surge, not modelled)
Outputs: cascade.json (per-frame series, totals, top closures / detour corridors with graph segment ids, cut-off census blocks as centroids with
frame intervals, overtopped culverts with downstream links); kept < 3 MB.
"""
import argparse
import json
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.normpath(os.path.join(HERE, '..'))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(ROOT, 'sim', 'infra'))
import impacts as IM  # noqa: E402
import resilience as RS  # noqa: E402

SITE = os.path.join(ROOT, 'docs', 'site', 'data')
SEGMENTS = os.path.join(ROOT, 'docs', 'graph_segments.json')
FACILITIES = os.path.join(ROOT, 'docs', 'network', 'facilities.json')
CROSSINGS = os.path.join(ROOT, 'docs', 'network', 'crossings_all.json')
CLOSE_CM = 30.0                 # deployed closure rule
SLOW_CM = 5.0                   # Pregnolato: no effect below 5 cm
CULVERT_CM = 15.0               # risk.py: overtopped from the water on the road within 30 m
XING_SNAP_M = 30.0
DOWN_M = 3000.0                 # same-named-stream link radius (drainage area, hence direction, is known for ~1 % of crossings)
OUT_MIN = 30.0                  # output cadence (model minutes)
H_DAY = 0.06                    # daytime hourly share of AADT (between 1 / 24 = 0.042 and a K30 design-hour factor ~0.09)
CAP_VPH = (1000.0, 2000.0, 4000.0)   # per graph segment: local / collector, arterial, highway (one segment per direction on divided roads)
TOP = 25
MAX_BLOCKS = 1500
OCC, VOT = 1.67, 18.13          # proto/risk.py: persons per vehicle (NHTS 2017), $ per person-hour (USDOT, 2023 $)


# ------------------------------------------------------------------------------------------------ inputs
def box_from_corners(C):
    from pyproj import Transformer
    x, y = Transformer.from_crs(4326, 26986, always_xy=True).transform([c[0] for c in C], [c[1] for c in C])
    return [round(min(x), -1), round(min(y), -1), round(max(x), -1), round(max(y), -1)]


def load_pack(key, n):
    """Public replay pack -> (frame ids, hours, D (frames x n) cm, box, meta)."""
    d = os.path.join(SITE, key); meta = json.load(open(os.path.join(d, 'meta.json'))); R = json.load(open(os.path.join(d, 'roads.json')))['features']
    nf = int(meta['nf']); fm = float(meta['frame_min']); step = max(1, int(round(OUT_MIN / fm)))
    fr = list(range(0, nf, step)); fr += [nf - 1] if fr[-1] != nf - 1 else []
    D = np.zeros((len(fr), n), np.float32); have = 0
    for f in R:
        dd = f['properties'].get('d')
        if not dd: continue
        a = np.asarray(dd, np.float32)
        if len(a) < nf: a = np.r_[a, np.full(nf - len(a), a[-1] if len(a) else 0, np.float32)]
        D[:, int(f['id'])] = a[fr]; have += 1
    return fr, np.array(fr) * fm / 60.0, D, box_from_corners(meta['corners']), dict(meta, series_segments=have, frame_step=step)


def load_outdir(out, n):
    summ = json.load(open(os.path.join(out, 'summary.json'))); hours = np.asarray(summ.get('frame_hours') or [], float)
    D = np.zeros((len(hours), n), np.float32); have = 0
    for f in json.load(open(os.path.join(out, 'segments.geojson')))['features']:
        p = f['properties']
        if p.get('d') is not None and len(p['d']) == len(hours): D[:, int(p['segment'])] = p['d']; have += 1
    return list(range(len(hours))), hours, D, summ['box_epsg26986'], dict(storm_start=summ.get('storm_start'), frame_min=None, series_segments=have, frame_step=1)


def load_crossings(box, path=CROSSINGS):
    if not os.path.exists(path): return []
    from pyproj import Transformer
    X = json.load(open(path)); c = X['columns']; ix = {k: c.index(k) for k in ('lon', 'lat', 'id', 'road', 'stream', 'span_m', 'bf_w', 'drn_km2')}
    lon = np.array([r[ix['lon']] for r in X['rows']], float); lat = np.array([r[ix['lat']] for r in X['rows']], float)
    x, y = Transformer.from_crs(4326, 26986, always_xy=True).transform(lon, lat)
    k = np.nonzero((x >= box[0]) & (x < box[2]) & (y >= box[1]) & (y < box[3]))[0]
    return [dict(i=int(i), lon=float(lon[i]), lat=float(lat[i]), x=float(x[i]), y=float(y[i]), **{f: X['rows'][i][ix[f]] for f in ('id', 'road', 'stream', 'span_m', 'bf_w', 'drn_km2')}) for i in k]


def block_table(box, P, n):
    """Populated 2020 Census blocks in the box -> (lon, lat, pop, segment)."""
    import census_blocks as CB
    from pyproj import Transformer
    from scipy.spatial import cKDTree
    B = CB.load(RS.BLOCKS)
    if B is None or not len(P['x']): return None
    x, y = Transformer.from_crs(4326, 26986, always_xy=True).transform(B['lon'], B['lat'])
    k = (x >= box[0]) & (x < box[2]) & (y >= box[1]) & (y < box[3]) & (B['pop'] > 0)
    if not k.any(): return None
    _, j = cKDTree(np.column_stack([P['x'], P['y']])).query(np.column_stack([x[k], y[k]]))
    return dict(lon=B['lon'][k], lat=B['lat'][k], pop=B['pop'][k], seg=np.asarray(P['seg'])[j].astype(np.int64))


# ------------------------------------------------------------------------------------------------ mechanics
def detours(net, G, G0, mult, closed, cap=RS.DETOUR_CAP_MIN):
    """resilience.closure_detours with the detour path: [(stretch segs, AADT, extra min, served, path segs)]."""
    from scipy.sparse import csr_matrix
    from scipy.sparse.csgraph import dijkstra, connected_components
    idx = np.nonzero(closed)[0]
    if not len(idx): return []
    m = -np.ones(net.n, np.int64); m[idx] = np.arange(len(idx)); k = (m[net.a] >= 0) & (m[net.b] >= 0)
    _, lab = connected_components(csr_matrix((np.ones(k.sum()), (m[net.a[k]], m[net.b[k]])), shape=(len(idx), len(idx))), directed=False)
    out = []
    for c in np.unique(lab):
        K = idx[lab == c]; Ks = set(K.tolist()); q = float(net.aadt[K].max())
        fr = sorted({j for i in K for j in net.nbr[i] if j not in Ks and np.isfinite(mult[j])})
        if not fr: out.append((K, q, cap, False, [])); continue
        u = max(fr, key=lambda j: (net.aadt[j], -j)); nu = set(net.nbr[u]); cand = [j for j in fr if j != u and j not in nu]
        if not cand: out.append((K, q, cap, False, [])); continue
        v = max(cand, key=lambda j: (net.aadt[j], -j))
        d0 = dijkstra(G0, directed=True, indices=u, limit=600.0)[v]
        if not np.isfinite(d0): out.append((K, q, cap, False, [])); continue
        d1, pr = dijkstra(G, directed=True, indices=u, limit=d0 * max(1.0, float(mult[v])) + cap + 1.0, return_predecessors=True)
        ex = float(d1[v] - d0) if np.isfinite(d1[v]) else np.inf
        path = []
        if ex <= cap:
            j = v
            while j >= 0 and j != u: path.append(int(j)); j = pr[j]
            path.append(int(u))
        out.append((K, q, min(max(ex, 0.0), cap), bool(ex <= cap), path[::-1]))
    return out


def intervals(mask):
    """bool per output frame -> [[k0, k1], ...] inclusive output-frame index runs."""
    out = []; k0 = None
    for k, v in enumerate(mask):
        if v and k0 is None: k0 = k
        if not v and k0 is not None: out.append([k0, k - 1]); k0 = None
    if k0 is not None: out.append([k0, len(mask) - 1])
    return out


def cascade(D, hours, frames, box, S=None, facilities=FACILITIES, crossings=CROSSINGS, label='', verbose=True):
    t_start = time.time(); S = S or json.load(open(SEGMENTS)); n = S['n']
    meta = dict(box=box, res_m=20.0, shape=[int(round((box[3] - box[1]) / 20.0)), int(round((box[2] - box[0]) / 20.0))])
    P = IM.road_points(S, meta); inbox = np.bincount(P['seg'], minlength=n)[:n] > 0
    D = D.copy(); D[:, ~inbox] = 0; T = len(hours); hours = np.asarray(hours, float)
    dt = np.gradient(hours) if T > 1 else np.full(T, 0.5)          # hours each output frame stands for (trapezoid weights)
    if T > 1: dt[0] = (hours[1] - hours[0]) / 2; dt[-1] = (hours[-1] - hours[-2]) / 2
    net = RS.Net(S); geom = RS.seg_geometry(S)
    fac = json.load(open(facilities))['facilities'] if facilities and os.path.exists(facilities) else {}
    FS = RS.snap_facilities(fac, geom); allsrc = sorted(set().union(*[set(v.tolist()) for v in FS.values()]))
    G0 = net.graph(np.ones(n)); acc0 = {s: RS.access_minutes(net, G0, FS[s]) for s in RS.ACCESS_MIN}
    ok0 = {s: acc0[s] <= RS.ACCESS_MIN[s] for s in RS.ACCESS_MIN}; iso0 = RS.isolated_mask(net, np.ones(n), allsrc)
    BT = block_table(box, P, n); nb = 0 if BT is None else len(BT['pop'])
    cap = np.array(CAP_VPH)[np.minimum(net.cls, 2)]; q = net.aadt / 24.0
    SV = ('hospital', 'fire_station', 'police')
    ser = {k: np.zeros(T) for k in ('closed_n', 'closed_km', 'slowed_n', 'slowed_km', 'stretches', 'delay_vehh_per_h', 'detour_vehh_per_h', 'slow_vehh_per_h',
                                    'unserved_aadt', 'detour_segments', 'overloaded_n', 'pop_lost_any', 'pop_isolated', 'pop_lost_dry_segment',
                                    'blocks_lost_any', 'culverts_overtopped', 'culvert_cost_lo', 'culvert_cost_hi')}
    for s in SV: ser[f'pop_lost_{s}'] = np.zeros(T)
    vh_det = np.zeros(n); vh_slow = np.zeros(n); hrs_closed = np.zeros(n); det_max = np.zeros(n)
    add_peak = np.zeros(n); vc_peak = np.zeros(n); over_h = np.zeros(n); add_vh = np.zeros(n); over_mask = np.zeros((T, n), bool) if T * n < 4e7 else None
    over_first = np.full(n, np.inf)
    blk_lost = np.zeros((T, nb), bool); blk_iso = np.zeros((T, nb), bool); blk_mask = np.zeros(nb, np.int64)
    cache_key = None; cache = None
    for k in range(T):
        d = D[k].astype(float); mult, f = RS.speed_mult(d, CLOSE_CM); closed = inbox & ~np.isfinite(mult); slowed = inbox & np.isfinite(mult) & (mult > 1.0)
        key = (np.nonzero(closed)[0].tobytes(), np.round(np.where(slowed, mult, 1.0), 2).tobytes())
        if key != cache_key:
            G = net.graph(mult); DT = detours(net, G, G0, mult, closed)
            added = np.zeros(n)
            for K, qa, ex, served, path in DT:
                if served and len(path) > 2: added[np.asarray(path[1:-1], int)] += qa
            lost = {}
            for s in SV:
                src = [j for j in FS[s] if np.isfinite(mult[j])]; A = RS.access_minutes(net, G, src)
                lost[s] = ok0[s] & ~((A <= RS.ACCESS_MIN[s]) & ~closed)
            iso = RS.isolated_mask(net, mult, allsrc) & ~iso0
            cache_key = key; cache = (DT, added, lost, iso)
        DT, added, lost, iso = cache
        lw = net.len_m / 1000.0
        ser['closed_n'][k] = closed.sum(); ser['closed_km'][k] = lw[closed].sum(); ser['slowed_n'][k] = slowed.sum(); ser['slowed_km'][k] = lw[slowed].sum()
        ser['stretches'][k] = len(DT)
        sv = q[slowed] * net.t0[slowed] * (mult[slowed] - 1.0) / 60.0; vh_slow[slowed] += sv * dt[k]; ser['slow_vehh_per_h'][k] = sv.sum()
        det = 0.0; uns = 0.0
        for K, qa, ex, served, path in DT:
            v = qa / 24.0 * ex / 60.0; det += v
            wK = net.aadt[K] * net.len_m[K]; wK = wK / wK.sum() if wK.sum() > 0 else np.full(len(K), 1.0 / len(K))
            vh_det[K] += v * dt[k] * wK; det_max[K] = np.maximum(det_max[K], ex)
            if not served: uns += qa
        hrs_closed[closed] += dt[k]
        ser['detour_vehh_per_h'][k] = det; ser['delay_vehh_per_h'][k] = det + sv.sum(); ser['unserved_aadt'][k] = uns
        vc = H_DAY * (net.aadt + added) / cap; ov = (added > 0) & (vc > 1.0) & ~closed
        ser['detour_segments'][k] = (added > 0).sum(); ser['overloaded_n'][k] = ov.sum()
        add_peak = np.maximum(add_peak, H_DAY * added); vc_peak = np.where(added > 0, np.maximum(vc_peak, vc), vc_peak)
        over_h[ov] += dt[k]; add_vh += H_DAY * added * dt[k]; over_first[ov & ~np.isfinite(over_first)] = hours[k]
        if over_mask is not None: over_mask[k] = ov
        if nb:
            bs = BT['seg']; la = np.zeros(nb, bool)
            for bit, s in enumerate(SV):
                L = lost[s][bs]; ser[f'pop_lost_{s}'][k] = BT['pop'][L].sum(); la |= L; blk_mask[L] |= 1 << bit
            bi = iso[bs]; blk_mask[bi] |= 8; blk_lost[k] = la; blk_iso[k] = bi
            ser['pop_lost_any'][k] = BT['pop'][la].sum(); ser['pop_isolated'][k] = BT['pop'][bi].sum(); ser['blocks_lost_any'][k] = la.sum()
            ser['pop_lost_dry_segment'][k] = BT['pop'][la & ~closed[bs]].sum()
        if verbose and k % 16 == 0:
            print(f'  {label} t={hours[k]:5.1f} h closed {int(closed.sum()):4d} stretches {len(DT):3d} delay {ser["delay_vehh_per_h"][k]:8.1f} veh-h/h '
                  f'overloaded {int(ov.sum()):3d} pop lost {int(ser["pop_lost_any"][k]):6d} isolated {int(ser["pop_isolated"][k]):5d}', flush=True)
    # culverts: overtopping timeline and downstream knock-on
    import risk as RK
    from scipy.spatial import cKDTree
    X = load_crossings(box, crossings) if crossings else []; cul = []
    if X and len(P['x']):
        dd, jj = cKDTree(np.column_stack([P['x'], P['y']])).query(np.array([[c['x'], c['y']] for c in X]))
        for c, di, ji in zip(X, dd, jj):
            if di > XING_SNAP_M: continue
            sg = int(P['seg'][ji]); wet = np.nonzero(D[:, sg] >= CULVERT_CM)[0]
            if not len(wet): continue
            lab, (lo, hi), need = RK.culvert_cost(c['span_m'], c['bf_w'])
            cul.append(dict(c, seg=sg, k0=int(wet[0]), t0=float(hours[wet[0]]), cost=(lo, hi), size=lab))
        allX = {c['i']: c for c in X}
        for c in cul:
            ds = []
            if c['stream']:
                for o in X:
                    if o['i'] == c['i'] or o['stream'] != c['stream'] or np.hypot(o['x'] - c['x'], o['y'] - c['y']) > DOWN_M: continue
                    if c['drn_km2'] and o['drn_km2']:
                        if o['drn_km2'] > c['drn_km2']: ds.append((o['i'], True))           # resolved: larger drainage area = downstream
                    else: ds.append((o['i'], False))                                           # same stream, direction unresolved
            c['down'] = ds
        t_of = {c['i']: c['t0'] for c in cul}
        for k in range(T):
            on = [c for c in cul if c['k0'] <= k]
            ser['culverts_overtopped'][k] = len(on); ser['culvert_cost_lo'][k] = sum(c['cost'][0] for c in on); ser['culvert_cost_hi'][k] = sum(c['cost'][1] for c in on)
    # ---------------------------------------------------------------- summary
    nm = S['props']['road']; tw = S['props']['town']
    vh_tot = float(vh_det.sum() + vh_slow.sum())
    closures = []
    for i in np.argsort(-(vh_det + vh_slow))[:TOP]:
        if vh_det[i] + vh_slow[i] <= 0: break
        closures.append(dict(seg=int(i), road=nm[i] or '', town=tw[i] or '', cls=int(net.cls[i]), aadt=int(net.aadt[i]), hours_closed=round(float(hrs_closed[i]), 1),
                             max_detour_min=round(float(det_max[i]), 1), vehh_detour=round(float(vh_det[i]), 1), vehh_slow=round(float(vh_slow[i]), 1)))
    corridors = []
    for i in np.argsort(-add_vh)[:TOP]:
        if add_vh[i] <= 0: break
        corridors.append(dict(seg=int(i), road=nm[i] or '', town=tw[i] or '', cls=int(net.cls[i]), aadt=int(net.aadt[i]), peak_detour_vph=round(float(add_peak[i])),
                              detour_veh=round(float(add_vh[i])), peak_vc=round(float(vc_peak[i]), 2), hours_over_capacity=round(float(over_h[i]), 1),
                              first_over_h=None if not np.isfinite(over_first[i]) else round(float(over_first[i]), 2),
                              over=intervals(over_mask[:, i]) if over_mask is not None else None))
    areas = []
    if nb:
        hrs_b = (blk_lost * dt[:, None]).sum(0); ever = np.nonzero(blk_lost.any(0) | blk_iso.any(0))[0]
        ever = ever[np.argsort(-(BT['pop'][ever] * hrs_b[ever]))][:MAX_BLOCKS]
        for b in ever:
            areas.append([round(float(BT['lon'][b]), 5), round(float(BT['lat'][b]), 5), int(BT['pop'][b]), int(blk_mask[b]), round(float(hrs_b[b]), 1),
                          intervals(blk_lost[:, b] | blk_iso[:, b])])
    culverts = []
    if cul:
        idx_of = {c['i']: j for j, c in enumerate(sorted(cul, key=lambda c: c['t0']))}
        for c in sorted(cul, key=lambda c: c['t0']):
            dl = [dict(lon=round(allX[o]['lon'], 5), lat=round(allX[o]['lat'], 5), road=allX[o]['road'] or '', downstream=dr, overtops_h=None if o not in t_of else round(t_of[o], 2),
                       lag_h=None if o not in t_of else round(t_of[o] - c['t0'], 2)) for o, dr in c['down']]
            culverts.append(dict(lon=round(c['lon'], 5), lat=round(c['lat'], 5), id=c['id'], road=c['road'] or '', stream=c['stream'] or '', seg=c['seg'], first_h=round(c['t0'], 2),
                                 size=c['size'], cost_usd=[round(c['cost'][0], -3), round(c['cost'][1], -3)], downstream=dl))
    downs = [o for c in culverts for o in c['downstream']]
    def tpeak(a): return None if not a.any() else round(float(hours[int(np.argmax(a))]), 2)
    first_close = np.nonzero(ser['closed_n'] > 0)[0]
    direct_people = float((ser['pop_lost_any'] - ser['pop_lost_dry_segment']).max()) if nb else 0.0
    totals = dict(
        segments_in_box=int(inbox.sum()), road_km_in_box=round(float((net.len_m[inbox] / 1000).sum()), 1), output_frames=T, window_h=round(float(hours[-1] - hours[0]), 2),
        first_closure_h=None if not len(first_close) else round(float(hours[first_close[0]]), 2),
        peak=dict(closed_n=int(ser['closed_n'].max()), closed_h=tpeak(ser['closed_n']), delay_vehh_per_h=round(float(ser['delay_vehh_per_h'].max()), 1),
                  delay_h=tpeak(ser['delay_vehh_per_h']), overloaded_n=int(ser['overloaded_n'].max()), overloaded_h=tpeak(ser['overloaded_n']),
                  pop_lost_any=int(ser['pop_lost_any'].max()), pop_lost_h=tpeak(ser['pop_lost_any']), pop_isolated=int(ser['pop_isolated'].max()),
                  pop_isolated_h=tpeak(ser['pop_isolated']), **{f'pop_lost_{s}': int(ser[f'pop_lost_{s}'].max()) for s in SV}),
        vehicle_hours=dict(total=round(vh_tot), detour=round(float(vh_det.sum())), slow_wet=round(float(vh_slow.sum())),
                           user_cost_usd=round(vh_tot * OCC * VOT, -3), unserved_aadt_hours=round(float((ser['unserved_aadt'] * dt).sum()))),
        person_hours_lost={s: round(float((ser[f'pop_lost_{s}'] * dt).sum())) for s in SV} | dict(any=round(float((ser['pop_lost_any'] * dt).sum())),
                                                                                               isolated=round(float((ser['pop_isolated'] * dt).sum()))),
        detour=dict(segments_ever_carrying=int((add_vh > 0).sum()), segments_ever_over_capacity=int((over_h > 0).sum()), segments_ever_closed=int((hrs_closed > 0).sum())),
        knock_on=dict(
            spread_ratio=round(float(((add_vh > 0) | (hrs_closed > 0)).sum() / max((hrs_closed > 0).sum(), 1)), 2),
            people_losing_access_on_dry_roads_peak=int(ser['pop_lost_dry_segment'].max()) if nb else 0,
            people_losing_access_on_flooded_roads_peak=int(direct_people),
            share_of_person_hours_on_dry_roads=round(float((ser['pop_lost_dry_segment'] * dt).sum() / max((ser['pop_lost_any'] * dt).sum(), 1e-9)), 3) if nb else None,
            lag_first_closure_to_peak_access_loss_h=None if not len(first_close) or not nb else round(float(hours[int(np.argmax(ser['pop_lost_any']))] - hours[first_close[0]]), 2),
            lag_first_closure_to_peak_delay_h=None if not len(first_close) else round(float(hours[int(np.argmax(ser['delay_vehh_per_h']))] - hours[first_close[0]]), 2)),
        culverts=dict(overtopped=len(culverts), cost_exposure_usd=[round(float(ser['culvert_cost_lo'][-1]), -3), round(float(ser['culvert_cost_hi'][-1]), -3)] if culverts else [0, 0],
                      with_stream_links=sum(1 for c in culverts if c['downstream']), stream_links=len(downs), links_direction_resolved=sum(1 for o in downs if o['downstream']),
                      linked_crossings_not_overtopped=len({(o['lon'], o['lat']) for o in downs if o['overtops_h'] is None}),
                      links_also_overtopped=sum(1 for o in downs if o['overtops_h'] is not None),
                      links_overtopped_later=sum(1 for o in downs if o['lag_h'] is not None and o['lag_h'] > 0),
                      median_positive_lag_h=None if not any(o['lag_h'] is not None and o['lag_h'] > 0 for o in downs) else round(float(np.median([o['lag_h'] for o in downs if o['lag_h'] is not None and o['lag_h'] > 0])), 2)))
    rnd = {k: (np.round(v, 1) if k.endswith(('km', 'per_h')) else np.round(v)).tolist() for k, v in ser.items()}
    res = dict(made_by='proto/cascade.py', made=time.strftime('%Y-%m-%d %H:%M'), box_epsg26986=box, frames=[int(x) for x in frames], t_h=[round(float(h), 2) for h in hours],
               params=dict(close_cm=CLOSE_CM, slow_cm=SLOW_CM, culvert_cm=CULVERT_CM, access_min=RS.ACCESS_MIN, detour_cap_min=RS.DETOUR_CAP_MIN, daytime_share=H_DAY,
                           cap_vph=dict(zip(('local_collector', 'arterial', 'highway'), CAP_VPH)), downstream_m=DOWN_M, occupancy=OCC, vot_usd=VOT),
               series=rnd, totals=totals, closures=closures, corridors=corridors,
               areas=dict(columns=['lon', 'lat', 'pop', 'lost_mask(1 hospital, 2 fire, 4 police, 8 isolated)', 'hours_lost', 'intervals(output frame idx)'], rows=areas,
                          blocks_ever=int((blk_lost.any(0) | blk_iso.any(0)).sum()) if nb else 0),
               culverts=culverts, runtime_s=round(time.time() - t_start, 1),
               notes=['closures are the deployed rule (depth >= 30 cm) on the modelled depth; segments outside the pack/series are dry',
                      'no traffic assignment: detour volumes are added on the single wet shortest path, so overload is an upper bound per corridor and delay a lower bound overall',
                      'AADT of most local roads is the 1,000 vpd default of graph_segments.json; population is night-time (2020 Census blocks)',
                      'culvert overtopping uses the water-on-road proxy (no headwater series in the packs); cost is replacement-cost exposure, not expected loss'])
    return res


def write(res, path):
    s = json.dumps(res, separators=(',', ':'), default=float)
    if len(s) > 3e6:     # trim the long lists first
        res['areas']['rows'] = res['areas']['rows'][:500]; s = json.dumps(res, separators=(',', ':'), default=float)
    open(path, 'w').write(s); return len(s)


def from_pack(key, S=None):
    S = S or json.load(open(SEGMENTS)); fr, h, D, box, meta = load_pack(key, S['n'])
    res = cascade(D, h, fr, box, S, label=key); res.update(run=key, storm_start=meta.get('storm_start'), viewer_frame_min=meta.get('frame_min'),
                                                           frame_step=meta['frame_step'], series_segments=meta['series_segments'], source='docs/site/data/%s/roads.json' % key)
    p = os.path.join(SITE, key, 'cascade.json'); nbytes = write(res, p); print(f'wrote {p} ({nbytes / 1e6:.2f} MB, {res["runtime_s"]} s)'); return res


def from_outdir(out, S=None):
    S = S or json.load(open(SEGMENTS)); fr, h, D, box, meta = load_outdir(out, S['n'])
    if not len(h) or not D.any(): print('cascade: no depth series in', out); return None
    res = cascade(D, h, fr, box, S, label=os.path.basename(out.rstrip('/'))); res.update(run=os.path.basename(out.rstrip('/')), storm_start=meta.get('storm_start'), source=out)
    p = os.path.join(out, 'cascade.json'); write(res, p); print('wrote', p); return res


def selftest():
    """Ladder: two parallel streets (A: 0-9, B: 10-19) joined by rungs 20-24 at nodes 0, 2, 4, 6, 9.  Close A3: detour runs over B and two rungs."""
    from pyproj import Transformer
    tr = Transformer.from_crs(26986, 4326, always_xy=True); geo = []; props = dict(road=[], town=[], cls=[], low=[], len=[], aadt=[]); links = []
    def seg(x0, y0, x1, y1, name, aadt, cls=0):
        lo, la = tr.transform([x0, x1], [y0, y1]); a = [round(lo[0] * 1e5), round(la[0] * 1e5)]; b = [round(lo[1] * 1e5), round(la[1] * 1e5)]
        geo.append([[a[0], a[1], b[0] - a[0], b[1] - a[1]]]); props['road'].append(name); props['town'].append('T'); props['cls'].append(cls)
        props['low'].append(0); props['len'].append(int(np.hypot(x1 - x0, y1 - y0))); props['aadt'].append(aadt)
    X0, Y0 = 150000.0, 905000.0
    for i in range(10): seg(X0 + 200 * i, Y0, X0 + 200 * (i + 1), Y0, 'A St', 20000, 1)
    for i in range(10): seg(X0 + 200 * i, Y0 + 400, X0 + 200 * (i + 1), Y0 + 400, 'B St', 1000)
    rung_at = [0, 2, 4, 6, 9]
    for r in rung_at: seg(X0 + 200 * r, Y0, X0 + 200 * r, Y0 + 400, 'Rung', 500)
    for i in range(9): links += [[i, i + 1], [10 + i, 11 + i]]
    for j, r in enumerate(rung_at):
        for s in ([r - 1, r] if r > 0 else [r]): links.append([20 + j, s]); links.append([20 + j, 10 + s])
    S = dict(n=25, geo=geo, props=props, links=links); box = [X0 - 100, Y0 - 100, X0 + 2200, Y0 + 600]
    D = np.zeros((3, 25), np.float32); D[1, 3] = 50; D[1, 12] = 10; D[2, 3] = 20
    res = cascade(D, np.array([0.0, 0.5, 1.0]), [0, 1, 2], box, S, facilities=None, crossings=None, verbose=False)
    s = res['series']; ok = s['closed_n'] == [0, 1, 0] and s['slowed_n'] == [0, 1, 1]
    ok &= s['detour_vehh_per_h'][1] > 0 and s['detour_vehh_per_h'][0] == 0 and s['detour_vehh_per_h'][2] == 0
    segs = {c['seg'] for c in res['corridors']}; ok &= 3 not in segs and bool(segs & set(range(10, 20))) and bool(segs & set(range(20, 25)))
    ok &= res['closures'][0]['seg'] == 3 and res['totals']['detour']['segments_ever_closed'] == 1
    ok &= intervals([0, 1, 1, 0, 1]) == [[1, 2], [4, 4]]
    print('selftest', 'PASS' if ok else 'FAIL', json.dumps(dict(series={k: s[k] for k in ('closed_n', 'slowed_n', 'detour_vehh_per_h', 'overloaded_n')},
                                                                 corridors=[(c['seg'], c['peak_vc']) for c in res['corridors']]))[:600])
    return ok


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0]); ap.add_argument('cmd', nargs='?', choices=['pack', 'outdir']); ap.add_argument('args', nargs='*')
    ap.add_argument('--selftest', action='store_true'); a = ap.parse_args()
    if a.selftest: sys.exit(0 if selftest() else 1)
    S = json.load(open(SEGMENTS))
    for x in a.args: (from_pack if a.cmd == 'pack' else from_outdir)(x, S)
