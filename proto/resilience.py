"""Quantitative network resilience of the road network through one storm: functionality curves Q(t) and resilience-triangle metrics.

    python proto/resilience.py --out docs/proto/leominster_sep2023            # post-step: reads that run's outputs
    python proto/resilience.py --selftest                                     # offline, synthetic 5-segment network

Runs after proto/prototype.py on its output folder: summary.json (box, frame_hours, closed_per_frame) and segments.geojson (per segment the
depth series 'd', cm at every 30-min snapshot, for every segment that got >= 5 cm; all other segments stay dry), with the road graph
docs/graph_segments.json and the facilities docs/network/facilities.json.  Nothing here changes p_close or any prototype output.

Writes into the same folder
  resilience.json            Q(t) per variant, resilience metrics per variant, access, vehicle-hours of delay, definitions + sources
  resilience.png             Q(t) per variant
  resilience_segments.csv    per segment: hours closed, vehicle-hours of delay it causes (detours + slow wet driving); read by proto/risk.py

Network state per snapshot k (dt = 30 min):
  closed      depth on the segment >= 30 cm (the prototype's closure depth; speed 0 in Pregnolato et al. 2017; small cars float, Shand et al. 2011)
  slowed      5-30 cm: speed x f(depth), the Pregnolato et al. 2017 depth-disruption curve (as in sim/infra/impacts.py)
  travel time free-flow time by class (45 / 65 / 95 km/h local / arterial / highway, as sim/infra/impacts.py), node weighted (a segment's
              time is paid on entering it)
  Sensitivity: the same at a 15 cm closure depth (sim/infra/impacts.py removes segments from 15 cm, NWS 'Turn Around Don't Drown').

Functionality Q(t), % of the dry network (three variants, each defensible on its own):
  Q_eff      global efficiency ratio E(t) / E_dry x 100.  E = 1 / (N (N - 1)) sum_{i != j} 1 / tau_ij, tau = shortest travel time
             (Latora & Marchiori 2001; used for road-network resilience by Ganin et al. 2017).  N stays the dry in-box segment count, so a closed
             segment contributes 0 to every pair it belongs to.  Measures how well the whole box network still moves people.
  Q_access   critical-access share, population-weighted: residents of the box within the response-time standard of the nearest open
             facility, now / dry, averaged over hospital (30 min; Carr et al. 2009 report access to emergency departments as share of the
             population within 30 / 60 min), fire station (8 min travel = NFPA 1710 (2020) 4.1.2.1.1 full first-alarm 480 s) and police
             (10 min; no national standard, a planning assumption).  Facility routing uses the whole MA graph, so hospitals outside the box
             count; a facility whose own segment is closed is not a source.
             Population: 2020 Census blocks (docs/network/census_blocks_ma.npz from proto/census_blocks.py: POP20 at the block's internal
             point).  Each populated block whose internal point is in the box is assigned to the in-box segment with the nearest road
             point (densified every res/2); blocks more than 500 m from any road are still assigned to the nearest one and counted
             (population_beyond_500m).  A block's residents use their segment: when it is closed they have no coverage.
             Reported per service: people within the standard dry, people losing it at the worst snapshot, and person-hours of lost
             coverage = integral (people within the standard dry but not now) dt (trapezoid).  Isolated: residents with no route at all to
             any open hospital, fire station or police station (their segment closed, or its strongly connected component of the open
             graph holds no open facility).
  Q_access_km  the earlier road-km version (in-box road-km within the standard, now / dry), kept for comparison and used when the census
             file is missing.
  Q_traffic  AADT-weighted serviceable lane capacity: sum AADT_i L_i f_i(t) / sum AADT_i L_i x 100, f = Pregnolato speed ratio (0 when
             closed).  Serviceability weighted by use, as in the traffic-weighted functionality of transport resilience reviews (Sun, Bocchini &
             Davison 2020).

Metrics per variant over the modelled window [0, T] (Bruneau et al. 2003; Cimellaro, Reinhorn & Bruneau 2010; Ouyang, Duenas-Osorio & Min 2012):
  resilience_loss_pct_h   RL = integral (100 - Q(t)) dt  (Bruneau et al. 2003, the area of the resilience triangle), trapezoid rule, % x h
  resilience_index        R = integral Q dt / (100 T)   (Cimellaro et al. 2010 / Ouyang et al. 2012 normalised form; 1 = no loss)
  robustness_pct          min Q, and the hour it happens
  rapidity                hours from the minimum to recovery to 90 % and 95 % (null = not recovered inside the window), and the mean
                          recovery rate (Q_end - Q_min) / (T - t_min), % per hour (Bruneau's rapidity as a rate)
  t_disruption_h          first hour Q < 99 %
Vehicle-hours of delay (VHD), AADT-weighted: per snapshot every segment carries AADT / 24 vehicles per hour (flat daily profile).
  closed stretch (closed segments that touch count as one closure, so through traffic is not counted once per segment): the stretch's
                  largest AADT detours from its busiest open entry to its busiest open exit at another junction; extra time = wet minus dry
                  shortest time between them (whole MA graph, closed segments removed, wet slowdowns); no detour within 30 min -> 30 min (trip
                  lost or postponed; counted separately as unserved vehicle-trips); shared over the stretch's segments by AADT x length.
  slowed segment: t_dry x (1 / f - 1).
  No traffic assignment: detour traffic does not congest the detour roads, so VHD is a lower bound for the vehicles on the closed roads.
"""
import os, sys, json, csv, math, argparse, time
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.normpath(os.path.join(HERE, '..'))
sys.path.insert(0, os.path.join(ROOT, 'sim', 'infra'))
import impacts as IM

CLOSE_CM = 30          # closure depth (prototype FAIL_M)
CLOSE_CM_SENS = 15     # sensitivity: impacts.py network cut
ACCESS_MIN = {'hospital': 30.0, 'fire_station': 8.0, 'police': 10.0}
DETOUR_CAP_MIN = 30.0
_trapz = getattr(np, 'trapezoid', None) or getattr(np, 'trapz')
SNAP_M = 3000.0        # facility snapped to the nearest segment midpoint within 3 km (as impacts.py)
POP_SNAP_M = 500.0     # census block internal point -> nearest in-box road point; farther blocks are still assigned, and counted
BLOCKS = os.path.join(ROOT, 'docs', 'network', 'census_blocks_ma.npz')
SOURCES = dict(
    bruneau='Bruneau M., Chang S.E., Eguchi R.T., Lee G.C., O\'Rourke T.D., Reinhorn A.M., Shinozuka M., Tierney K., Wallace W.A., von Winterfeldt D. (2003) '
            'A framework to quantitatively assess and enhance the seismic resilience of communities. Earthquake Spectra 19(4), 733-752 (resilience loss = integral [100 - Q(t)] dt; robustness, rapidity)',
    cimellaro='Cimellaro G.P., Reinhorn A.M., Bruneau M. (2010) Framework for analytical quantification of disaster resilience. Engineering Structures 32(11), 3639-3649 (normalised resilience index over a control time)',
    ouyang='Ouyang M., Duenas-Osorio L., Min X. (2012) A three-stage resilience analysis framework for urban infrastructure systems. Structural Safety 36-37, 23-31 (resilience = integral of performance / integral of target performance)',
    latora='Latora V., Marchiori M. (2001) Efficient behavior of small-world networks. Physical Review Letters 87(19), 198701 (global efficiency)',
    ganin='Ganin A.A., Kitsak M., Marchese D., Keisler J.M., Seager T., Linkov I. (2017) Resilience and efficiency in transportation networks. Science Advances 3(12), e1701079',
    sun='Sun W., Bocchini P., Davison B.D. (2020) Resilience metrics and measurement methods for transportation infrastructure: the state of the art. Sustainable and Resilient Infrastructure 5(3), 168-199',
    pregnolato='Pregnolato M., Ford A., Wilkinson S., Dawson R. (2017) The impact of flooding on road transport: a depth-disruption function. Transportation Research Part D 55, 67-81',
    nfpa='NFPA 1710 (2020) Standard for the organization and deployment of fire suppression operations ... by career fire departments, 4.1.2.1.1: 240 s travel for the first engine, 480 s for the full first alarm',
    census='US Census Bureau (2021) 2020 TIGER/Line Shapefiles, tabulation blocks (TABBLOCK20), POP20 / HOUSING20 = 2020 Census P.L. 94-171 counts; '
           'internal point INTPTLAT20 / INTPTLON20',
    carr='Carr B.G., Branas C.C., Metlay J.P., Sullivan A.F., Camargo C.A. (2009) Access to emergency care in the United States. Annals of Emergency Medicine 54(2), 261-269 (population within 30 / 60 min of an emergency department)')


def seg_geometry(S):
    """Per segment: (x, y) EPSG:26986 of its first vertex, last vertex and midpoint."""
    from pyproj import Transformer
    tr = Transformer.from_crs(4326, 26986, always_xy=True); F, Lst, M = [], [], []
    for parts in S['geo']:
        d0 = parts[0]; d1 = parts[-1]
        lo0 = np.cumsum(d0[0::2]) / 1e5; la0 = np.cumsum(d0[1::2]) / 1e5; lo1 = np.cumsum(d1[0::2]) / 1e5; la1 = np.cumsum(d1[1::2]) / 1e5
        j = len(lo0) // 2; F.append((lo0[0], la0[0])); Lst.append((lo1[-1], la1[-1])); M.append((lo0[j], la0[j]))
    out = {}
    for k, A in (('first', F), ('last', Lst), ('mid', M)):
        A = np.array(A); x, y = tr.transform(A[:, 0], A[:, 1]); out[k] = np.column_stack([x, y])
    return out


class Net:
    """Whole-MA segment graph (node = segment, edge = shared junction), node-weighted by free-flow minutes."""
    def __init__(self, S):
        n = S['n']; self.n = n
        L = np.asarray(S['links'], np.int64).reshape(-1, 2) if len(S['links']) else np.zeros((0, 2), np.int64)
        E = np.unique(np.sort(L, axis=1), axis=0); E = E[E[:, 0] != E[:, 1]]
        self.a = np.r_[E[:, 0], E[:, 1]]; self.b = np.r_[E[:, 1], E[:, 0]]
        self.cls = np.asarray(S['props']['cls']); self.len_m = np.asarray([v or 30 for v in S['props']['len']], float)
        self.aadt = np.asarray([v or 0 for v in S['props']['aadt']], float)
        self.t0 = self.len_m / 1000.0 / np.array(IM.CLASS_KMH)[np.minimum(self.cls, 2)] * 60.0
        self.nbr = [[] for _ in range(n)]
        for u, v in E: self.nbr[u].append(int(v)); self.nbr[v].append(int(u))

    def graph(self, mult, nodes=None):
        """CSR graph with weight t0[b] * mult[b] on a -> b; inf mult = node removed.  nodes: restrict to this index array (renumbered)."""
        from scipy.sparse import csr_matrix
        a, b = self.a, self.b
        if nodes is not None:
            m = -np.ones(self.n, np.int64); m[nodes] = np.arange(len(nodes)); k = (m[a] >= 0) & (m[b] >= 0); a, b = m[a[k]], m[b[k]]
            w = (self.t0[nodes] * mult[nodes])[b]; N = len(nodes)
        else:
            w = self.t0[b] * mult[b]; N = self.n
        k = np.isfinite(w); return csr_matrix((np.maximum(w[k], 1e-6), (a[k], b[k])), shape=(N, N))


def speed_mult(d_cm, close_cm):
    """Travel-time multiplier per segment from depth (cm): 1 dry, 1/f (Pregnolato) when slowed, inf when closed."""
    f = IM.speed_factor(d_cm / 100.0)
    return np.where(d_cm >= close_cm, np.inf, 1.0 / np.maximum(f, 1e-6)), np.where(d_cm >= close_cm, 0.0, f)


def efficiency(G, nodes_n, sources=None):
    """Global efficiency over the graph's nodes (Latora & Marchiori 2001); sources: optional sample of row indices (unbiased estimator)."""
    from scipy.sparse.csgraph import dijkstra
    idx = np.arange(nodes_n) if sources is None else sources
    tot = 0.0
    for c in range(0, len(idx), 500):
        D = dijkstra(G, directed=True, indices=idx[c:c + 500])
        with np.errstate(divide='ignore'): inv = np.where(np.isfinite(D) & (D > 0), 1.0 / D, 0.0)
        tot += inv.sum()
    return tot / (len(idx) * (nodes_n - 1))


def closure_detours(net, G, G0, mult, closed, cap=DETOUR_CAP_MIN):
    """Detour per closed stretch.  Closed segments that touch form one stretch (a flooded chain of Route 2 segments is one closure, so its
    through traffic is counted once).  Through traffic = the largest AADT in the stretch; it enters at u, the open neighbour with the largest
    AADT, and leaves at v, the open neighbour with the largest AADT that is not at u's junction.  Extra minutes = wet shortest time u -> v
    (closed segments removed, wet slowdowns) - dry shortest time u -> v.  No v (dead end) or no path within cap -> cap, trips unserved.
    Returns [(segments of the stretch, vehicles per hour through it, extra minutes, served)]."""
    from scipy.sparse import csr_matrix
    from scipy.sparse.csgraph import dijkstra, connected_components
    idx = np.nonzero(closed)[0]
    if not len(idx): return []
    m = -np.ones(net.n, np.int64); m[idx] = np.arange(len(idx)); k = (m[net.a] >= 0) & (m[net.b] >= 0)
    _, lab = connected_components(csr_matrix((np.ones(k.sum()), (m[net.a[k]], m[net.b[k]])), shape=(len(idx), len(idx))), directed=False)
    out = []
    for c in np.unique(lab):
        K = idx[lab == c]; Ks = set(K.tolist()); vph = float(net.aadt[K].max()) / 24.0
        fr = sorted({j for i in K for j in net.nbr[i] if j not in Ks and np.isfinite(mult[j])})
        if not fr: out.append((K, vph, cap, False)); continue
        u = max(fr, key=lambda j: (net.aadt[j], -j)); nu = set(net.nbr[u])
        cand = [j for j in fr if j != u and j not in nu]
        if not cand: out.append((K, vph, cap, False)); continue
        v = max(cand, key=lambda j: (net.aadt[j], -j))
        d0 = dijkstra(G0, directed=True, indices=u, limit=600.0)[v]
        if not np.isfinite(d0): out.append((K, vph, cap, False)); continue
        d1 = dijkstra(G, directed=True, indices=u, limit=d0 * max(1.0, float(mult[v])) + cap + 1.0)[v]
        ex = float(d1 - d0) if np.isfinite(d1) else np.inf
        out.append((K, vph, min(max(ex, 0.0), cap), bool(ex <= cap)))
    return out


def access_minutes(net, G, src_nodes):
    from scipy.sparse.csgraph import dijkstra
    if len(src_nodes) == 0: return np.full(net.n, np.inf)
    return dijkstra(G, directed=True, indices=np.asarray(src_nodes), min_only=True, limit=max(ACCESS_MIN.values()) * 3)


def snap_facilities(fac, geom):
    from scipy.spatial import cKDTree
    from pyproj import Transformer
    tr = Transformer.from_crs(4326, 26986, always_xy=True); tree = cKDTree(geom['mid']); out = {}
    for k in ACCESS_MIN:
        F = fac.get(k) or []
        if not F: out[k] = np.zeros(0, int); continue
        x, y = tr.transform([f[0] for f in F], [f[1] for f in F]); d, ii = tree.query(np.column_stack([x, y])); out[k] = np.unique(ii[d < SNAP_M])
    return out


def assign_blocks(path, P, box):
    """Populated census blocks with internal point in the box -> nearest in-box road point's segment.
    Returns (seg index per block, distance m, pop, housing, meta) or None when the file is missing / no block is in the box."""
    sys.path.insert(0, HERE); import census_blocks as CB
    B = CB.load(path)
    if B is None or not len(P['x']): return None
    from pyproj import Transformer
    from scipy.spatial import cKDTree
    x, y = Transformer.from_crs(4326, 26986, always_xy=True).transform(B['lon'], B['lat'])
    k = (x >= box[0]) & (x < box[2]) & (y >= box[1]) & (y < box[3])
    if not k.any(): return None
    d, j = cKDTree(np.column_stack([P['x'], P['y']])).query(np.column_stack([x[k], y[k]]))
    return np.asarray(P['seg'])[j].astype(np.int64), d, B['pop'][k], B['housing'][k], B['meta']


def isolated_mask(net, mult, sources):
    """Segments with no route to any source: closed themselves, or in a strongly connected component of the open graph without a source."""
    from scipy.sparse.csgraph import connected_components
    G = net.graph(mult); _, lab = connected_components(G, directed=True, connection='strong')
    ok = np.zeros(lab.max() + 1, bool); src = np.asarray([j for j in sources if np.isfinite(mult[j])], np.int64)
    if len(src): ok[lab[src]] = True
    return ~ok[lab] | ~np.isfinite(mult)


def curve_metrics(t, Q):
    t = np.asarray(t, float); Q = np.asarray(Q, float); T = t[-1] - t[0]
    rl = float(_trapz(100.0 - Q, t)); R = float(_trapz(Q, t) / (100.0 * T)) if T > 0 else 1.0
    k = int(np.argmin(Q)); qmin = float(Q[k]); tmin = float(t[k])
    def rec(level):
        if qmin >= level: return 0.0
        after = np.nonzero(Q[k:] >= level)[0]
        return None if not len(after) else round(float(t[k + after[0]] - tmin), 2)
    dis = np.nonzero(Q < 99.0)[0]
    rate = (float(Q[-1]) - qmin) / (t[-1] - tmin) if t[-1] > tmin else None
    return dict(resilience_loss_pct_h=round(rl, 1), resilience_index=round(R, 4), robustness_pct=round(qmin, 2), t_min_h=round(tmin, 2),
                t_disruption_h=None if not len(dis) else round(float(t[dis[0]]), 2),
                recovery_to_90_h=rec(90.0), recovery_to_95_h=rec(95.0), recovery_rate_pct_per_h=None if rate is None else round(float(rate), 3),
                q_end_pct=round(float(Q[-1]), 2), window_h=round(float(T), 2))


def load_inputs(out, segments):
    summ = json.load(open(os.path.join(out, 'summary.json'))); S = json.load(open(segments)); n = S['n']
    box = summ['box_epsg26986']; res = summ['resolution_m']
    meta = dict(box=box, res_m=res, shape=[int(round((box[3] - box[1]) / res)), int(round((box[2] - box[0]) / res))])
    P = IM.road_points(S, meta); inbox = np.bincount(P['seg'], minlength=n) > 0
    hours = np.asarray(summ.get('frame_hours') or [], float)
    G = json.load(open(os.path.join(out, 'segments.geojson')))
    D = np.zeros((len(hours), n), np.float32); props = {}
    for f in G['features']:
        p = f['properties']; i = int(p['segment']); props[i] = p
        if p.get('d') is not None and len(p['d']) == len(hours): D[:, i] = p['d']
    return summ, S, inbox, hours, D, props, P


def run(out, segments=None, facilities=None, eff_sources=0, close_cm=CLOSE_CM, sens=True, png=True, blocks=BLOCKS):
    t_start = time.time()
    segments = segments or os.path.join(ROOT, 'docs', 'graph_segments.json'); facilities = facilities or os.path.join(ROOT, 'docs', 'network', 'facilities.json')
    summ, S, inbox, hours, D, props, P = load_inputs(out, segments)
    if not len(hours) or not D.any():
        print('resilience: no depth time series in', out); return None
    D[:, ~inbox] = 0
    net = Net(S); geom = seg_geometry(S); n = net.n; nodes = np.nonzero(inbox)[0]
    fac = json.load(open(facilities))['facilities'] if facilities and os.path.exists(facilities) else {}
    FS = snap_facilities(fac, geom)
    dt_h = float(np.median(np.diff(hours))) if len(hours) > 1 else 0.5
    rng = np.random.default_rng(0)
    srcs = None if not eff_sources or eff_sources >= len(nodes) else np.sort(rng.choice(len(nodes), eff_sources, replace=False))
    lw = net.len_m / 1000.0; aw = net.aadt * net.len_m
    # dry baselines
    mult0 = np.ones(n); G0 = net.graph(mult0); Gb0 = net.graph(mult0, nodes)
    E0 = efficiency(Gb0, len(nodes), srcs)
    acc0 = {k: access_minutes(net, G0, FS[k]) for k in ACCESS_MIN}
    ok0 = {k: inbox & (acc0[k] <= ACCESS_MIN[k]) for k in ACCESS_MIN}
    km0 = {k: float(lw[ok0[k]].sum()) for k in ACCESS_MIN}
    # population per segment (2020 Census blocks)
    BA = assign_blocks(blocks, P, summ['box_epsg26986'])
    if BA is not None:
        bseg, bdist, bpop, bhou, bmeta = BA; pop = np.bincount(bseg, bpop, minlength=n); pop[~inbox] = 0
    else:
        pop = None; print('resilience: no census blocks (%s): Q_access falls back to road-km' % blocks)
    if pop is not None:
        pop_tot = float(pop.sum()); p0 = {k: float(pop[ok0[k]].sum()) for k in ACCESS_MIN}
        allsrc = sorted(set().union(*[set(FS[k].tolist()) for k in ACCESS_MIN]))
        iso0 = float(pop[isolated_mask(net, mult0, allsrc)].sum())
        lostp = {k: [] for k in ACCESS_MIN}; anyl = []; iso_t = []; iso_fl = []; pacc_t = {k: [] for k in ACCESS_MIN}
    # time loop
    vhd_close = np.zeros(n); vhd_slow = np.zeros(n); unserved = np.zeros(n); hrs_closed = np.zeros(n); detour_max = np.zeros(n)
    Qe, Qa, Qk, Qt, Qs, acc_t = [], [], [], [], [], {k: [] for k in ACCESS_MIN}; ncl = []; vhd_t = []; nodet = []
    for k, h in enumerate(hours):
        d = D[k].astype(float); mult, f = speed_mult(d, close_cm); closed = inbox & ~np.isfinite(mult); ncl.append(int(closed.sum()))
        G = net.graph(mult); Gb = net.graph(mult, nodes)
        Qe.append(100.0 * efficiency(Gb, len(nodes), srcs) / E0 if E0 > 0 else 100.0)
        sh = []; shp = []; lost_any = np.zeros(n, bool)
        for s in ACCESS_MIN:
            src = [j for j in FS[s] if np.isfinite(mult[j])]; A = access_minutes(net, G, src)
            okt = ok0[s] & (A <= ACCESS_MIN[s]) & ~closed
            km = float(lw[okt].sum()); r = 100.0 * km / km0[s] if km0[s] > 0 else 100.0
            acc_t[s].append(round(r, 2)); sh.append(r)
            if pop is not None:
                pc = float(pop[okt].sum()); rp = 100.0 * pc / p0[s] if p0[s] > 0 else 100.0
                pacc_t[s].append(round(rp, 2)); shp.append(rp); lostp[s].append(round(p0[s] - pc)); lost_any |= ok0[s] & ~okt
        Qk.append(float(np.mean(sh)))
        if pop is not None:
            Qa.append(float(np.mean(shp))); anyl.append(round(float(pop[lost_any].sum())))
            im = isolated_mask(net, mult, [j for s in ACCESS_MIN for j in FS[s]]); iso_t.append(round(float(pop[im].sum())))
            iso_fl.append(round(float(pop[im & closed].sum())))
        else: Qa.append(Qk[-1])
        Qt.append(100.0 * float((aw * np.where(inbox, f, 0)).sum() / aw[inbox].sum()))
        vph = net.aadt / 24.0
        slow = inbox & np.isfinite(mult) & (mult > 1.0)
        vhd_slow[slow] += vph[slow] * dt_h * net.t0[slow] * (mult[slow] - 1.0) / 60.0
        nd = 0
        for K, v_, ex, served in closure_detours(net, G, G0, mult, closed):
            wK = net.aadt[K] * net.len_m[K]; wK = wK / wK.sum() if wK.sum() > 0 else np.full(len(K), 1.0 / len(K))
            vhd_close[K] += v_ * dt_h * ex / 60.0 * wK; detour_max[K] = np.maximum(detour_max[K], ex)
            if not served: unserved[K] += v_ * dt_h * wK; nd += 1
        hrs_closed[closed] += dt_h
        nodet.append(nd); vhd_t.append(round(float(vhd_close.sum() + vhd_slow.sum()), 1))
        if sens and k % 8 == 0: print(f'  t={h:5.1f} h closed {closed.sum():4d}  Q_eff {Qe[-1]:6.2f}  Q_access {Qa[-1]:6.2f}  Q_traffic {Qt[-1]:6.2f}', flush=True)
    # sensitivity: efficiency at the 15 cm cut
    if sens:
        for k in range(len(hours)):
            mult, _ = speed_mult(D[k].astype(float), CLOSE_CM_SENS); Qs.append(100.0 * efficiency(net.graph(mult, nodes), len(nodes), srcs) / E0)
    V = {'Q_eff': Qe, 'Q_access': Qa, 'Q_traffic': Qt, 'Q_access_km': Qk}
    res = dict(run=summ.get('run'), storm_start=summ.get('storm_start'), box_epsg26986=summ['box_epsg26986'], made=time.strftime('%Y-%m-%d %H:%M'),
               segments_in_box=int(inbox.sum()), road_km_in_box=round(float(lw[inbox].sum()), 1), frame_hours=[round(float(h), 2) for h in hours], dt_h=dt_h,
               closure_depth_cm=close_cm, closed_segments=ncl,
               Q={k: [round(float(v), 3) for v in q] for k, q in V.items()},
               metrics={k: curve_metrics(hours, q) for k, q in V.items()},
               access=dict(thresholds_min=ACCESS_MIN, facilities_snapped={k: int(len(v)) for k, v in FS.items()},
                           dry_km_within={k: round(v, 1) for k, v in km0.items()}, dry_share_of_box_km={k: round(100 * v / max(float(lw[inbox].sum()), 1e-9), 1) for k, v in km0.items()},
                           share_pct=acc_t, metrics={k: curve_metrics(hours, v) for k, v in acc_t.items()}),
               efficiency=dict(E_dry_per_min=round(float(E0), 6), sources='all' if srcs is None else int(len(srcs)), weight='free-flow minutes x Pregnolato slowdown'),
               delay=dict(vehicle_hours_total=round(float(vhd_close.sum() + vhd_slow.sum()), 1), vehicle_hours_detour=round(float(vhd_close.sum()), 1),
                          vehicle_hours_slow_wet=round(float(vhd_slow.sum()), 1), unserved_vehicle_trips=round(float(unserved.sum()), 0),
                          detour_cap_min=DETOUR_CAP_MIN, cumulative_vehicle_hours=vhd_t, closed_stretches_without_detour=nodet,
                          aadt_note='hourly volume = AADT / 24 (flat profile); 75 % of in-box local segments carry the 1,000 vpd default of graph_segments.json',
                          method='closed stretch (touching closed segments): its largest AADT detours from the busiest open entry to the busiest open exit at '
                                 'another junction, extra = wet - dry shortest time (whole MA graph); no detour within 30 min -> 30 min and the trips '
                                 'counted unserved; shared over the stretch by AADT x length; slowed: t_dry (1/f - 1); no traffic assignment (lower bound)'),
               definitions=dict(
                   Q_eff='E(t) / E_dry x 100, E = global efficiency (Latora & Marchiori 2001) of the in-box segment graph, travel-time weighted; N fixed at the dry count',
                   Q_access=('mean over hospital (30 min), fire station (8 min), police (10 min) of in-box residents (2020 Census blocks) within the standard of an open facility, now / dry x 100'
                             if pop is not None else 'road-km version (no census file): see Q_access_km'),
                   Q_access_km='mean over hospital (30 min), fire station (8 min), police (10 min) of in-box road-km within the standard of an open facility, now / dry x 100',
                   Q_traffic='sum AADT L f(t) / sum AADT L x 100, f = Pregnolato speed ratio, 0 when closed',
                   resilience_loss_pct_h='integral (100 - Q) dt over the window (Bruneau et al. 2003)', resilience_index='integral Q dt / (100 T) (Cimellaro et al. 2010; Ouyang et al. 2012)',
                   robustness_pct='min Q', recovery_to_90_h='hours from the minimum until Q >= 90 % (null: not inside the window)',
                   closure='segment depth >= %d cm closed; 5-%d cm slowed by Pregnolato et al. 2017' % (close_cm, close_cm)),
               caveats=['The modelled window ends 48 h after t0; water ponded in closed depressions of the lidar DEM (no storm drains beyond 2 mm/h) keeps '
                        'about 115 segments closed at the end, so recovery times are lower bounds / null and RL depends on the window length.',
                        ('Population: 2020 Census block counts at block internal points, each block on its nearest road segment; residents of a closed segment count as without coverage and isolated '
                         '(stay-at-home is not modelled); night-time (residential) population, not daytime.' if pop is not None else 'No census file: road-km is the access proxy.'), 'AADT of local roads is mostly a 1,000 vpd default.',
                        'Delay has no traffic assignment (no congestion on detours) and a flat daily volume profile.'],
               sources=SOURCES, runtime_s=None)
    if pop is not None:
        ph = {k: round(float(_trapz(np.asarray(v, float), hours))) for k, v in lostp.items()}
        res['population'] = dict(
            source=bmeta.get('source'), census=bmeta, blocks_in_box=int(len(bpop)), population_in_box=round(pop_tot), housing_units_in_box=round(float(bhou.sum())),
            population_beyond_500m=round(float(bpop[bdist > POP_SNAP_M].sum())), blocks_beyond_500m=int((bdist > POP_SNAP_M).sum()),
            block_to_road_m=dict(median=round(float(np.median(bdist)), 1), p90=round(float(np.percentile(bdist, 90)), 1), max=round(float(bdist.max()), 1)),
            dry_within={k: round(v) for k, v in p0.items()}, dry_share_pct={k: round(100 * v / max(pop_tot, 1e-9), 1) for k, v in p0.items()},
            share_pct=pacc_t, metrics={k: curve_metrics(hours, v) for k, v in pacc_t.items()},
            people_losing=lostp, people_losing_any=anyl,
            worst={k: dict(people=int(max(v)), hour=round(float(hours[int(np.argmax(v))]), 2)) for k, v in lostp.items()}
                  | {'any_service': dict(people=int(max(anyl)), hour=round(float(hours[int(np.argmax(anyl))]), 2))},
            person_hours_lost=ph | {'sum_three_services': int(sum(ph.values()))}, person_hours_lost_any=round(float(_trapz(np.asarray(anyl, float), hours))),
            isolated=iso_t, isolated_on_flooded_segment=iso_fl, isolated_dry=round(iso0),
            isolated_worst=dict(people=int(max(iso_t)), hour=round(float(hours[int(np.argmax(iso_t))]), 2),
                                on_flooded_segment=int(iso_fl[int(np.argmax(iso_t))])),
            isolated_person_hours=round(float(_trapz(np.asarray(iso_t, float), hours))),
            method='2020 Census blocks (POP20 > 0) with internal point in the box -> nearest in-box road point (segment); losing = within the standard dry, '
                   'not now (segment closed, or no open facility within the standard); person-hours = trapezoid of people losing over the window; '
                   'isolated = no route to any open hospital / fire / police (strongly connected component of the open whole-MA graph)')
    res['access']['variant'] = 'population (2020 Census blocks)' if pop is not None else 'road-km (no census file)'
    if sens:
        res['sensitivity_15cm'] = dict(Q_eff=[round(float(v), 3) for v in Qs], metrics=curve_metrics(hours, Qs))
    res['runtime_s'] = round(time.time() - t_start, 1)
    json.dump(res, open(os.path.join(out, 'resilience.json'), 'w'), indent=1)
    with open(os.path.join(out, 'resilience_segments.csv'), 'w', newline='') as fh:
        w = csv.writer(fh); w.writerow(['segment', 'road', 'town', 'aadt', 'length_m', 'hours_closed', 'max_detour_min', 'vehicle_hours_detour', 'vehicle_hours_slow', 'unserved_vehicle_trips'])
        for i in np.nonzero((vhd_close + vhd_slow + hrs_closed) > 0)[0]:
            w.writerow([int(i), S['props']['road'][i] or '', S['props']['town'][i] or '', int(net.aadt[i]), int(net.len_m[i]), round(float(hrs_closed[i]), 1),
                        round(float(detour_max[i]), 1), round(float(vhd_close[i]), 1), round(float(vhd_slow[i]), 1), round(float(unserved[i]), 0)])
    if png: plot(os.path.join(out, 'resilience.png'), res)
    print(json.dumps({k: res[k] for k in ('metrics', 'delay')}, indent=1)[:3000])
    if 'population' in res: print(json.dumps({k: res['population'][k] for k in ('population_in_box', 'dry_within', 'worst', 'person_hours_lost', 'isolated_worst', 'isolated_person_hours')}))
    print('wrote', os.path.join(out, 'resilience.json'))
    return res


def plot(path, res):
    import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
    t = res['frame_hours']; fig, ax = plt.subplots(figsize=(8, 3.6), dpi=130)
    style = {'Q_eff': ('#2b6cb0', 'efficiency  E(t)/E$_{dry}$'), 'Q_access': ('#c05621', 'critical access (hospital / fire / police)'),
             'Q_traffic': ('#2f855a', 'AADT-weighted serviceable km'), 'Q_access_km': ('#c05621', 'critical access, road-km version')}
    if 'population' in res: style['Q_access'] = ('#c05621', 'critical access, residents (hospital / fire / police)')
    for k, (c, lab) in style.items():
        if k not in res['Q'] or (k == 'Q_access_km' and 'population' not in res): continue
        m = res['metrics'][k]; ax.plot(t, res['Q'][k], color=c, lw=1 if k == 'Q_access_km' else 2, ls=':' if k == 'Q_access_km' else '-', label=f"{lab}: min {m['robustness_pct']:.1f} %, RL {m['resilience_loss_pct_h']:.0f} %·h")
    if res.get('sensitivity_15cm'): ax.plot(t, res['sensitivity_15cm']['Q_eff'], color='#2b6cb0', lw=1, ls='--', label='efficiency, closure at 15 cm')
    lo = min(min(min(v) for v in res['Q'].values()), min(res.get('sensitivity_15cm', {}).get('Q_eff') or [100]))
    ax.axhline(90, color='#999', lw=0.7, ls=':'); ax.set_ylim(max(0, math.floor(lo / 5) * 5 - 5), 100.5); ax.set_xlim(t[0], t[-1])
    ax.set_xlabel(f"hours after {res.get('storm_start') or 't0'}"); ax.set_ylabel('functionality Q(t), % of dry')
    ax.set_title('Road-network functionality through the storm (Leominster box)' if 'leominster' in str(res.get('run')) else 'Road-network functionality through the storm', fontsize=10)
    ax.legend(fontsize=7, loc='lower right', frameon=False); ax.grid(alpha=0.25); fig.tight_layout(); fig.savefig(path); plt.close(fig)


def selftest():
    """Line of 5 segments + a parallel bypass; middle segment floods for 2 of 5 frames; checks Q, metrics, detours."""
    import tempfile
    from pyproj import Transformer
    d = tempfile.mkdtemp(); inv = Transformer.from_crs(26986, 4326, always_xy=True)
    box = [100000.0, 900000.0, 110000.0, 910000.0]
    def enc(xs, ys):
        lo, la = inv.transform(xs, ys); q = np.round(np.c_[lo, la] * 1e5).astype(int); dq = np.diff(np.r_[[[0, 0]], q], axis=0); return [dq.ravel().tolist()]
    X = [101000 + 1000 * k for k in range(6)]; Y = 905000.0
    geo = [enc([X[k], X[k + 1]], [Y, Y]) for k in range(5)]
    geo += [enc([X[1], X[1]], [Y, Y + 1000]), enc([X[1], X[4]], [Y + 1000, Y + 1000]), enc([X[4], X[4]], [Y + 1000, Y])]       # bypass 5-6-7
    links = [0, 1, 1, 2, 2, 3, 3, 4, 0, 5, 1, 5, 5, 6, 6, 7, 3, 7, 4, 7]
    n = 8; S = dict(n=n, geo=geo, links=links, props=dict(road=['A'] * 5 + ['B'] * 3, town=['T'] * n, cls=[0] * n, low=[0] * n, len=[1000] * 5 + [1000, 3000, 1000], aadt=[2400] * 5 + [240] * 3))
    sp = os.path.join(d, 'segs.json'); json.dump(S, open(sp, 'w'))
    lo, la = inv.transform(X[0] + 10, Y + 10)
    json.dump(dict(facilities=dict(hospital=[[lo, la, 'H']], fire_station=[[lo, la, 'F']], police=[[lo, la, 'P']])), open(os.path.join(d, 'fac.json'), 'w'))
    hrs = [0.0, 0.5, 1.0, 1.5, 2.0]; dd = [0, 40, 40, 10, 0]
    feats = [dict(type='Feature', geometry=None, properties=dict(segment=2, d=dd))]
    json.dump(dict(type='FeatureCollection', features=feats), open(os.path.join(d, 'segments.geojson'), 'w'))
    json.dump(dict(run='selftest', box_epsg26986=box, resolution_m=20.0, frame_hours=hrs, storm_start='t0'), open(os.path.join(d, 'summary.json'), 'w'))
    # census blocks: 120 people on segment 1 (always covered), 40 on segment 2 (floods), 5 far from any road (assigned anyway)
    bx, by = [102500.0, 103500.0, 108000.0], [904950.0, 905050.0, 908000.0]; blo, bla = inv.transform(bx, by)
    np.savez_compressed(os.path.join(d, 'blocks.npz'), geoid=np.arange(3, dtype=np.int64), lat=np.round(np.asarray(bla) * 1e6).astype(np.int32),
                        lon=np.round(np.asarray(blo) * 1e6).astype(np.int32), pop=np.array([120, 40, 5], np.int32), housing=np.array([50, 15, 2], np.int32),
                        meta=np.asarray(json.dumps(dict(source='selftest'))))
    r = run(d, sp, os.path.join(d, 'fac.json'), sens=False, png=True, blocks=os.path.join(d, 'blocks.npz'))
    Qt = r['Q']['Q_traffic']; ok = True
    def check(name, cond, det=''):
        nonlocal ok; ok &= bool(cond); print(('ok   ' if cond else 'FAIL ') + name, '' if cond else det)
    w = 2400 * 1000.0; tot = 5 * w + 3 * 240 * 1000.0 + 240 * 2000.0
    check('Q_traffic drops by the closed segment share', abs(Qt[1] - 100 * (1 - w / tot)) < 1e-3, Qt)
    check('Q back to 100 when dry', abs(Qt[0] - 100) < 1e-9 and abs(r['Q']['Q_eff'][4] - 100) < 1e-6, r['Q'])
    check('efficiency falls when closed', r['Q']['Q_eff'][1] < 99.0, r['Q']['Q_eff'])
    check('wet 10 cm segment slowed (Q_traffic < 100)', Qt[3] < 100.0, Qt)
    m = r['metrics']['Q_traffic']; exp_rl = _trapz(100 - np.array(Qt), hrs)
    check('RL = trapezoid of 100 - Q', abs(m['resilience_loss_pct_h'] - round(exp_rl, 1)) < 0.06, m)
    check('robustness = min Q; back to 90 % after 1 h (10 cm frame slowed), 95 % after 1.5 h', abs(m['robustness_pct'] - round(min(Qt), 2)) < 1e-6 and m['recovery_to_90_h'] == 1.0 and m['recovery_to_95_h'] == 1.5, m)
    # detour: bypass 5-6-7 = 1000/45 + 3000/45 + 1000/45 min ... from end junctions (seg 1 -> seg 3); dry through seg 2 = 1000 m
    rows = {int(x['segment']): x for x in csv.DictReader(open(os.path.join(d, 'resilience_segments.csv')))}
    exp = (5000 - 1000) / 1000 / 45 * 60 - 0          # 5-6-7 replace 2 (and the path ends on 3 either way)
    check('detour minutes through the bypass', abs(float(rows[2]['max_detour_min']) - round((5000 / 1000 / 45 * 60) - (1000 / 1000 / 45 * 60), 1)) < 0.15, rows.get(2))
    check('vehicle-hours = AADT/24 x hours closed x detour', abs(float(rows[2]['vehicle_hours_detour']) - 100 * 1.0 * float(rows[2]['max_detour_min']) / 60) < 0.2, rows.get(2))
    pp = r['population']
    check('blocks in box, one beyond 500 m', pp['population_in_box'] == 165 and pp['population_beyond_500m'] == 5 and pp['blocks_beyond_500m'] == 1, pp)
    check('hospital: 40 people lose coverage while segment 2 is closed', pp['people_losing']['hospital'] == [0, 40, 40, 0, 0] and pp['worst']['hospital']['people'] == 40, pp['people_losing'])
    check('person-hours = trapezoid (40 people x 1 h)', pp['person_hours_lost']['hospital'] == 40, pp['person_hours_lost'])
    check('isolated = residents of the flooded segment', pp['isolated'] == [0, 40, 40, 0, 0] and pp['isolated_on_flooded_segment'][1] == 40 and pp['isolated_dry'] == 0, pp['isolated'])
    check('Q_access population-weighted (hospital share 100 x 125/165 when closed)', abs(pp['share_pct']['hospital'][1] - round(100 * 125 / 165, 2)) < 0.01, pp['share_pct'])
    check('road-km variant kept', 'Q_access_km' in r['Q'] and r['Q']['Q_access_km'][1] < 100, r['Q'].get('Q_access_km'))
    check('resilience.png written', os.path.exists(os.path.join(d, 'resilience.png')))
    print('resilience selftest', 'OK' if ok else 'FAILED', d); return ok


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--out', help='prototype output folder (summary.json, segments.geojson); results are written there')
    ap.add_argument('--segments', default=os.path.join(ROOT, 'docs', 'graph_segments.json'))
    ap.add_argument('--facilities', default=os.path.join(ROOT, 'docs', 'network', 'facilities.json'))
    ap.add_argument('--blocks', default=BLOCKS, help='census blocks .npz (proto/census_blocks.py); missing -> road-km access')
    ap.add_argument('--eff-sources', type=int, default=0, help='sample this many sources for global efficiency (0 = all pairs)')
    ap.add_argument('--no-sens', action='store_true', help='skip the 15 cm sensitivity curve')
    ap.add_argument('--selftest', action='store_true')
    a = ap.parse_args()
    if a.selftest: sys.exit(0 if selftest() else 1)
    run(a.out, a.segments, a.facilities, a.eff_sources, sens=not a.no_sens, blocks=a.blocks)
