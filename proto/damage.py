"""Crossing DAMAGE layer (roadmap T7): probability that a road-stream crossing is damaged (culvert washout, bridge / abutment damage,
embankment / road-edge washout at the crossing), separate from the closure layer (p_close).  Many Leominster labels are damage, not standing
water (docs/proto/recall/RECALL.md), so this is its own map layer, never added to p_close.

    python proto/damage.py extract --run-dir <w9 out/> --storm sep2023 --out crossings_sep2023.csv   # after a LF_QOUT=1 run (xings.json)
    python proto/damage.py evaluate [--runs docs/proto/damage/runs] [--out docs/proto/damage]       # LOSO fit + held-out scores -> damage.json
    python proto/damage.py layer --crossings crossings_<storm>.csv --out damage_<storm>.geojson      # map layer: damage_p, omega, why, $ expected
    python proto/damage.py --selftest

Physics (per crossing, from the flood run):
  Q      peak discharge through the crossing's notch block (w9 LF_QOUT=1 face fluxes -> xings.json q_peak_m3s, 30-min snapshots)
  S      channel slope: least-squares gradient of the run's routed DEM (z.npy: channels burnt, crossings notched) along the D8 flow path
         from ~50 m upstream to ~50 m downstream of the crossing's channel cell (max D8 accumulation within 60 m), notch block cells left
         out, clipped to [0.0005, 0.3]
  w      bankfull width: surveyed (MA Stream Crossings Project bf_w) > channels30 width (NHDPlus HR, Bieger et al. 2015) >
         Bieger et al. 2015 W = 2.70 A^0.352 from the drainage area A (channels30, else D8 on z.npy, truncated at the box edge)
  omega  specific stream power gamma Q S / w (W/m2), gamma = 9810 N/m3 (Anderson et al. 2017, J. Bridge Eng. 22(5): Irene bridge damage
         mapped on stream power; Magilligan 1992: ~300 W/m2 as the lower bound of major channel change in extreme floods)
  over   overtopping: peak upstream water surface (max of z + hmax on wet cells within 60 m outside the notch) minus the road crest
         (highest DEM cell of the notch block before it was cut); for NAACC-surveyed culverts also the HDS-5 ratio Q / Q_crest
         (prototype.culvert_probability: P = Phi(ln(Q / Q_crest) / 0.30)).

Fragility:  P(damage) = 1 / (1 + exp(-(b0 + b1 ln(omega / 300) + b2 clip(over, -1, 1))))
  prior (no labels):     b0 = 0, b1 = 1.5, b2 = 0  -> P = 0.5 at 300 W/m2 (Magilligan 1992 threshold), x10 omega -> P 0.97
  fitted (LOSO):         b0, b1, b2 by L2-regularised logistic regression on crossings with damage labels, leave-one-storm-out
Expected repair cost = damage_p x replacement cost of the crossing (proto/risk.py culvert_cost: MA Stream Crossing Standards 1.2 x
bankfull span, VTrans 2014 Irene unit costs, 2023 $).
Labels: damage types only (culvert_failure, washout, sinkhole, bridge_damage, other_damage) in proto/data/labels_<storm>_*.csv; a crossing
is damaged when a damage label lies within MATCH_M of it.  Closure-only types (flooded / closed / impassable) are not used.
"""
import os, sys, json, math, csv, argparse, glob
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.normpath(os.path.join(HERE, '..'))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(ROOT, 'sim', 'infra'))

GAMMA = 9810.0                 # unit weight of water, N/m3
OMEGA50 = 300.0                # W/m2, prior median: Magilligan (1992) minimum unit stream power for major geomorphic adjustment
PRIOR_B1 = 1.5                 # prior slope on ln(omega / 300): x10 omega -> logit +3.45
SLOPE_M = 50.0                 # slope measured over +-50 m along the flow path
S_MIN, S_MAX = 0.0005, 0.30
CHAN_R_M = 60.0                # channel cell: max drainage area within 60 m of the crossing (as impacts.channel_cell)
RING_M = 60.0                  # up/downstream water surface: wet cells within 60 m outside the notch block
WET_M = 0.05
MATCH_M = 50.0                 # a damage label within 50 m of a crossing marks it damaged
SITE_M = 150.0                 # labels joined single-link within 150 m count as one site (PROTOCOL.md)
DAMAGE_TYPES = ('culvert_failure', 'washout', 'sinkhole', 'bridge_damage', 'other_damage')
SHARES = (0.02, 0.05, 0.10)
COLS = ['id', 'src', 'lon', 'lat', 'x', 'y', 'road', 'stream', 'kind', 'shape', 'span_m', 'rise_m', 'fill_m', 'bf_w_inv', 'nbi_id', 'mdot_cat',
        'q_peak_m3s', 'q_peak_h', 'crest_m', 'wse_up_m', 'h_up_m', 'wse_dn_m', 'h_dn_m', 'h_block_m', 'over_m', 'v_max_ms',
        'area_km2', 'area_src', 'width_m', 'width_src', 'slope', 'omega_wm2', 'omega_span_wm2', 'q_crest_m3s', 'hds5_ratio', 'p_hds5']


def d8(Z, res):
    """D8 receivers (flat index, -1 = pit / edge) and accumulated cell counts on Z."""
    ny, nx = Z.shape; Zp = np.pad(Z.astype(np.float64), 1, constant_values=np.inf)
    best = np.zeros((ny, nx)); rec = np.full((ny, nx), -1, np.int64)
    rr, cc = np.mgrid[0:ny, 0:nx]
    for dr in (-1, 0, 1):
        for dc in (-1, 0, 1):
            if dr == 0 and dc == 0: continue
            dist = res * math.hypot(dr, dc); zn = Zp[1 + dr:1 + dr + ny, 1 + dc:1 + dc + nx]
            s = (Z - zn) / dist; s = np.where(np.isfinite(s), s, -np.inf); m = s > best
            best = np.where(m, s, best); rec = np.where(m, (rr + dr) * nx + (cc + dc), rec)
    recf = rec.ravel(); acc = np.ones(ny * nx, np.float64)
    order = np.argsort(-Z.ravel(), kind='stable'); rl = recf[order].tolist(); ol = order.tolist(); a = acc.tolist()
    for i, r in zip(ol, rl):
        if r >= 0: a[r] += a[i]
    return recf, np.array(a).reshape(ny, nx)


def flow_slope(Z, rec, acc, r, c, res, dist_m=SLOPE_M, skip=None):
    """(slope, path length m) along the D8 path from dist_m upstream (max-accumulation donors) to dist_m downstream of (r, c): minus the
    least-squares gradient of Z against distance along the path, cells in `skip` (the notch block: r0, r1, c0, c1) left out.  A pit on the way
    down is left through its lowest unvisited neighbour, so a notch or a burnt-channel dip does not end the path."""
    ny, nx = Z.shape; k = max(2, int(round(dist_m / res))); i = r * nx + c; Zr = Z.ravel()
    path = [(0.0, i)]; seen = {i}; dn, s_ = i, 0.0
    for _ in range(k):
        j = rec[dn]
        if j < 0 or j in seen:
            dr_, dc_ = dn // nx, dn % nx
            nb = [(Zr[(dr_ + a) * nx + dc_ + b], (dr_ + a) * nx + dc_ + b) for a in (-1, 0, 1) for b in (-1, 0, 1)
                  if (a or b) and 0 <= dr_ + a < ny and 0 <= dc_ + b < nx and (dr_ + a) * nx + dc_ + b not in seen]
            if not nb: break
            j = min(nb)[1]
        s_ += res * math.hypot(j // nx - dn // nx, j % nx - dn % nx); dn = j; seen.add(j); path.append((s_, j))
    up, s_ = i, 0.0
    for _ in range(k):
        ur, uc = up // nx, up % nx; cand = []
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                rr_, cc_ = ur + dr, uc + dc
                if (dr or dc) and 0 <= rr_ < ny and 0 <= cc_ < nx and rec[rr_ * nx + cc_] == up and rr_ * nx + cc_ not in seen: cand.append((acc[rr_, cc_], rr_ * nx + cc_))
        if not cand: break
        j = max(cand)[1]; s_ -= res * math.hypot(j // nx - ur, j % nx - uc); up = j; seen.add(j); path.append((s_, j))
    if skip is not None:
        r0, r1, c0, c1 = skip; path = [(d, j) for d, j in path if not (r0 <= j // nx < r1 and c0 <= j % nx < c1)]
    if len(path) < 2: return None, 0.0
    d = np.array([p[0] for p in path]); z = np.array([float(Zr[p[1]]) for p in path])
    if d.max() - d.min() <= 0: return None, 0.0
    g = np.polyfit(d, z, 1)[0]
    return float(np.clip(-g, S_MIN, S_MAX)), float(d.max() - d.min())


def bieger_width(A):
    return 2.70 * A ** 0.352 if A and A > 0 else None


def load_channels_grid(meta):
    """channels30 (NHDPlus HR drainage area km2, Bieger bankfull width m) cut to the run grid, from Hugging Face; None when unavailable."""
    try:
        from huggingface_hub import hf_hub_download
        sys.path.insert(0, os.path.join(ROOT, 'sim'))
        from crossings_capacity import load_channels
        repo = 'mohabeldokla/mass-flood-watch-tiles'; tok = os.environ.get('HF_TOKEN')
        cp = hf_hub_download(repo, 'data/channels30/channels30.npz', repo_type='dataset', token=tok)
        cm = hf_hub_download(repo, 'data/channels30/channels30_meta.json', repo_type='dataset', token=tok)
        return load_channels(cp, cm, meta)
    except Exception as e:
        print('channels30 unavailable, D8 area used:', repr(e)[:120]); return None


def crossing_kind(row):
    cat = (row.get('mdot_cat') or '').lower(); span = row.get('span_m') or 0
    if row.get('nbi_id') or 'bridge' in cat or span >= 6.1: return 'bridge'
    if row.get('shape') or 'culvert' in cat or row.get('naacc_code'): return 'culvert'
    return 'unknown'


def extract(run_dir, out, storm=None, channels=True):
    """One row per crossing the run opened (xings.json): peak Q, up/downstream water, overtopping, speed, slope, width, omega, HDS-5."""
    from pyproj import Transformer
    import prototype as PR
    meta = json.load(open(os.path.join(run_dir, 'meta.json'))); x0, y0, x1, y1 = meta['box']; res = float(meta['res_m'])
    XJ = json.load(open(os.path.join(run_dir, 'xings.json'))); XG = XJ.get('crossings', [])
    H = np.nan_to_num(np.load(os.path.join(run_dir, 'hmax.npy')).astype(np.float32)); Z = np.load(os.path.join(run_dir, 'z.npy')).astype(np.float32)
    ny, nx = H.shape; Zf = np.where(np.isfinite(Z), Z, np.nanmax(Z) + 100.0)
    vp = os.path.join(run_dir, 'vel_max.npz'); V = np.nan_to_num(np.load(vp)['vmax'].astype(np.float32)) if os.path.exists(vp) else None
    CH = load_channels_grid(meta) if channels else None
    rec, acc = d8(Zf, res); Ad8 = acc * res * res / 1e6
    XA = json.load(open(os.path.join(ROOT, 'docs', 'network', 'crossings_all.json'))); C = XA['columns']
    byid = {r_[C.index('id')]: dict(zip(C, r_)) for r_ in XA['rows']}
    xq = {g['id']: g for g in XG if g.get('q_peak_m3s') is not None}
    rows_hds = [byid[g['id']] for g in XG if g['id'] in byid]
    hds = {c['id']: c for c in PR.culvert_probability(rows_hds, xq, {}, meta, True)}
    tr = Transformer.from_crs(4326, 26986, always_xy=True); kc = int(math.ceil(CHAN_R_M / res)); kr = int(math.ceil(RING_M / res)); out_rows = []
    for g in XG:
        if not all(k in g for k in ('r', 'c', 'r0', 'r1', 'c0', 'c1', 'zcrest')): continue      # older xings.json without the notch block
        row = byid.get(g['id'], {}); r, c = int(g['r']), int(g['c'])
        if not (0 <= r < ny and 0 <= c < nx): continue
        x, y = (tr.transform(row['lon'], row['lat']) if row.get('lon') is not None else (x0 + (c + 0.5) * res, y1 - (r + 0.5) * res))
        b0, b1, c0, c1 = g['r0'], g['r1'], g['c0'], g['c1']
        R0, R1, C0, C1 = max(0, r - kr), min(ny, r + kr + 1), max(0, c - kr), min(nx, c + kr + 1)
        rr, cc = np.mgrid[R0:R1, C0:C1]; d = np.hypot(rr - r, cc - c) * res
        ring = (d <= RING_M) & ~((rr >= b0) & (rr < b1) & (cc >= c0) & (cc < c1))
        h = H[R0:R1, C0:C1]; wse = Z[R0:R1, C0:C1] + h; wet = ring & (h >= WET_M)
        crest = float(g.get('zcrest')); rec_ = dict(id=g['id'], src=row.get('src'), lon=row.get('lon'), lat=row.get('lat'), x=round(x, 1), y=round(y, 1),
                                                   road=row.get('road'), stream=row.get('stream'), kind=crossing_kind(row), shape=row.get('shape'),
                                                   span_m=row.get('span_m'), rise_m=row.get('rise_m'), fill_m=row.get('fill_m'), bf_w_inv=row.get('bf_w'),
                                                   nbi_id=row.get('nbi_id'), mdot_cat=row.get('mdot_cat'), q_peak_m3s=g.get('q_peak_m3s'), q_peak_h=g.get('q_peak_h'),
                                                   crest_m=round(crest, 2), h_block_m=round(float(H[b0:b1, c0:c1].max()), 3))
        if wet.any():
            iu = np.argmax(np.where(wet, wse, -np.inf)); idn = np.argmin(np.where(wet, wse, np.inf))
            rec_.update(wse_up_m=round(float(wse.ravel()[iu]), 2), h_up_m=round(float(h.ravel()[iu]), 3), wse_dn_m=round(float(wse.ravel()[idn]), 2),
                        h_dn_m=round(float(h.ravel()[idn]), 3), over_m=round(float(wse.ravel()[iu]) - crest, 3))
        else:
            rec_.update(wse_up_m=None, h_up_m=0.0, wse_dn_m=None, h_dn_m=0.0, over_m=round(float((Z[b0:b1, c0:c1] + H[b0:b1, c0:c1]).max()) - crest, 3))
        if V is not None: rec_['v_max_ms'] = round(float(V[R0:R1, C0:C1][d <= 2 * res].max()), 2)
        # channel cell: largest drainage area within 60 m (nearest among cells within 20 % of it)
        Q0, Q1, P0, P1 = max(0, r - kc), min(ny, r + kc + 1), max(0, c - kc), min(nx, c + kc + 1)
        qr, qc = np.mgrid[Q0:Q1, P0:P1]; dq = np.hypot(qr - r, qc - c) * res; win = dq <= CHAN_R_M
        A_src = 'channels30' if (CH is not None and (CH['area'][Q0:Q1, P0:P1][win] > 0).any()) else 'd8'
        Agrid = CH['area'] if A_src == 'channels30' else Ad8
        sc = np.where(win, Agrid[Q0:Q1, P0:P1], -1.0); best = sc >= 0.8 * sc.max(); k_ = int(np.argmin(np.where(best, dq, np.inf)))
        cr, ccn = int(qr.ravel()[k_]), int(qc.ravel()[k_]); A = float(Agrid[cr, ccn])
        # slope along the D8 path through the max-D8-accumulation cell near the channel cell (the routed DEM's own channel)
        s3 = np.where(win, Ad8[Q0:Q1, P0:P1], -1.0); k3 = int(np.argmax(s3)); S, L = flow_slope(Zf, rec, acc, int(qr.ravel()[k3]), int(qc.ravel()[k3]), res, skip=(b0, b1, c0, c1))
        if row.get('bf_w'): W, wsrc = float(row['bf_w']), 'surveyed bankfull'
        elif CH is not None and CH['width'][cr, ccn] > 0 and A_src == 'channels30': W, wsrc = float(CH['width'][cr, ccn]), 'channels30 (Bieger 2015)'
        else: W, wsrc = bieger_width(A), 'Bieger 2015 from area'
        W = max(W or 1.0, 1.0); Q = float(g.get('q_peak_m3s') or 0.0)
        om = GAMMA * Q * (S or S_MIN) / W
        span = row.get('span_m'); om_s = GAMMA * Q * (S or S_MIN) / max(float(span), 0.3) if span else None
        rec_.update(area_km2=round(A, 3), area_src=A_src, width_m=round(W, 2), width_src=wsrc, slope=None if S is None else round(S, 4),
                    omega_wm2=round(om, 1), omega_span_wm2=None if om_s is None else round(om_s, 1))
        hc = hds.get(g['id'])
        if hc and hc.get('q_crest_m3s') is not None:
            rec_.update(q_crest_m3s=hc['q_crest_m3s'], hds5_ratio=round(Q / max(hc['q_crest_m3s'], 1e-6), 3), p_hds5=round(hc['p'], 3))
        out_rows.append(rec_)
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    with open(out, 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=COLS); w.writeheader()
        for r_ in out_rows: w.writerow({k: r_.get(k) for k in COLS})
    print(f'{len(out_rows)} crossings -> {out}; with Q > 0: {sum(1 for r_ in out_rows if (r_["q_peak_m3s"] or 0) > 0)}; '
          f'omega >= 300: {sum(1 for r_ in out_rows if r_["omega_wm2"] >= 300)}; channels30: {CH is not None}')
    return out_rows



# ---------------------------------------------------------------- fragility, labels, evaluation
def fnum(v, d=None):
    try:
        f = float(v); return f if math.isfinite(f) else d
    except (TypeError, ValueError): return d


def features(r):
    om = max(fnum(r.get('omega_wm2'), 0.0), 1.0); ov = fnum(r.get('over_m'), -1.0)
    return [math.log(om / OMEGA50), float(np.clip(ov, -1.0, 1.0))]


def fragility(rows, model=None):
    """damage_p per crossing row: logistic in ln(omega / 300) and clipped overtopping; model None = the literature prior."""
    m = model or dict(b0=0.0, b1=PRIOR_B1, b2=0.0)
    X = np.array([features(r) for r in rows]) if rows else np.zeros((0, 2))
    z = m['b0'] + m['b1'] * X[:, 0] + m['b2'] * X[:, 1]
    return 1.0 / (1.0 + np.exp(-z))


def fit(rows, y, C=1.0):
    from sklearn.linear_model import LogisticRegression
    X = np.array([features(r) for r in rows]); lr = LogisticRegression(C=C, max_iter=1000).fit(X, y)
    return dict(b0=float(lr.intercept_[0]), b1=float(lr.coef_[0, 0]), b2=float(lr.coef_[0, 1]), n=len(y), n_pos=int(sum(y)), C=C)


def hds5_layer(r):
    """The existing overtopping layer at a crossing: HDS-5 P(HW > crest) where the NAACC barrel is surveyed, else Phi(over / 0.10)."""
    p = fnum(r.get('p_hds5'))
    if p is not None: return p
    return 0.5 * (1.0 + math.erf(fnum(r.get('over_m'), -1.0) / 0.10 / math.sqrt(2.0)))


def why(r, p):
    Q, S, W, om = fnum(r.get('q_peak_m3s'), 0), fnum(r.get('slope'), 0), fnum(r.get('width_m'), 0), fnum(r.get('omega_wm2'), 0)
    t = f"stream power {om:,.0f} W/m2 ({Q:.1f} m3/s on a {S * 100:.1f} % slope, {W:.1f} m wide channel)"
    t += ' - above' if om >= OMEGA50 else ' - below'
    t += f" the ~{OMEGA50:.0f} W/m2 at which floods rework channels and scour fills"
    ov = fnum(r.get('over_m'))
    if ov is not None and ov > 0: t += f"; water {ov:.2f} m over the road crest"
    if fnum(r.get('hds5_ratio')) is not None: t += f"; culvert at {fnum(r['hds5_ratio']):.1f} x its HDS-5 capacity at the crest"
    return t


def repair(r):
    import risk as RK
    lab, (lo, hi), need = RK.culvert_cost(fnum(r.get('span_m')), fnum(r.get('bf_w_inv')) or fnum(r.get('width_m')))
    return lab, lo, hi


def layer(rows, model=None):
    """Map-layer records: damage_p, omega, why, expected repair cost (2023 $) = damage_p x geometric mean of the replacement range."""
    P = fragility(rows, model); out = []
    for r, p in zip(rows, P):
        lab, lo, hi = repair(r)
        out.append(dict(id=r['id'], lon=fnum(r.get('lon')), lat=fnum(r.get('lat')), road=r.get('road'), stream=r.get('stream'), kind=r.get('kind'),
                        damage_p=round(float(p), 3), omega=fnum(r.get('omega_wm2')), q_peak_m3s=fnum(r.get('q_peak_m3s')), over_m=fnum(r.get('over_m')),
                        p_overtop=round(hds5_layer(r), 3), repair_class=lab, repair_low_usd=round(lo, -3), repair_high_usd=round(hi, -3),
                        expected_cost_usd=round(float(p) * math.sqrt(lo * hi), -2), why=why(r, p)))
    return out


def write_geojson(path, recs):
    F = [dict(type='Feature', geometry=dict(type='Point', coordinates=[r['lon'], r['lat']]), properties={k: v for k, v in r.items() if k not in ('lon', 'lat')})
         for r in recs if r['lon'] is not None]
    json.dump(dict(type='FeatureCollection', name='crossing_damage', features=F), open(path, 'w'))



def run_layer(run_dir, out, model=None):
    """prototype.py hook (PROTO_DAMAGE=1): crossing table from the run dir -> <out>/damage.geojson (+ damage_crossings.csv); summary dict."""
    if not os.path.exists(os.path.join(run_dir, 'xings.json')): return dict(error='no xings.json in the run dir (needs w9 with LF_QOUT=1)')
    rows = extract(run_dir, os.path.join(out, 'damage_crossings.csv'), channels=os.environ.get('PROTO_DAMAGE_CHANNELS', '1') == '1')
    rows = [{k: ('' if v is None else v) for k, v in r.items()} for r in rows]
    if model is None:
        mp = os.path.join(ROOT, 'docs', 'proto', 'damage', 'damage_model.json')
        model = json.load(open(mp)).get('model') if os.path.exists(mp) else None
    recs = layer(rows, model); write_geojson(os.path.join(out, 'damage.geojson'), recs)
    return dict(crossings=len(recs), damage_p_ge_50=sum(r['damage_p'] >= 0.5 for r in recs), expected_repair_usd=round(sum(r['expected_cost_usd'] for r in recs), -3),
                model='fitted' if model else 'prior: P = 1 / (1 + (omega / 300 W/m2)^-1.5)', layer='damage.geojson (separate from p_close)')


def load_damage_labels(storm, box):
    from pyproj import Transformer
    tr = Transformer.from_crs(4326, 26986, always_xy=True); L = []
    for f in sorted(glob.glob(os.path.join(HERE, 'data', f'labels_{storm}_*.csv'))):
        src = 'dpw' if f.endswith('_dpw.csv') else 'news'
        for r in csv.DictReader(open(f)):
            if r.get('type') not in DAMAGE_TYPES: continue
            lon, lat = fnum(r.get('lon')), fnum(r.get('lat'))
            if lon is None or lat is None: continue
            x, y = tr.transform(lon, lat)
            if box[0] <= x < box[2] and box[1] <= y < box[3]:
                L.append(dict(id=r['id'], type=r['type'], road=r.get('road'), q=r.get('coord_quality'), src=src, x=x, y=y, name=r.get('name')))
    return L


def sites(labels, radius=SITE_M):
    """single-link clusters of labels within radius -> list of index lists"""
    n = len(labels); par = list(range(n))
    def f(a):
        while par[a] != a: par[a] = par[par[a]]; a = par[a]
        return a
    for i in range(n):
        for j in range(i + 1, n):
            if math.hypot(labels[i]['x'] - labels[j]['x'], labels[i]['y'] - labels[j]['y']) <= radius: par[f(i)] = f(j)
    g = {}
    for i in range(n): g.setdefault(f(i), []).append(i)
    return list(g.values())


def match(rows, labels, tolerant=False):
    """Sites with their candidate crossings.  strict: exact-coordinate labels, crossings within MATCH_M.  tolerant (context only): approximate
    labels, crossings on the same normalised road name within 1.5 km."""
    import prototype as PR
    xy = np.array([[fnum(r['x']), fnum(r['y'])] for r in rows]) if rows else np.zeros((0, 2)); roads = [PR.norm_road(r.get('road') if isinstance(r.get('road'), str) else '') for r in rows]
    L = [l for l in labels if (l['q'] == 'exact') != tolerant and l['q'] != 'town']
    out = []
    for s in sites(L):
        cand = set()
        for i in s:
            d = np.hypot(xy[:, 0] - L[i]['x'], xy[:, 1] - L[i]['y'])
            if tolerant:
                rn = PR.norm_road(L[i]['road'] or '')
                cand |= set(np.where((d <= 1500.0) & np.array([rn != '' and (rn in r_ or r_ in rn) and r_ != '' for r_ in roads]))[0].tolist())
            else: cand |= set(np.where(d <= MATCH_M)[0].tolist())
        out.append(dict(labels=[L[i]['id'] for i in s], types=sorted({L[i]['type'] for i in s}), src=sorted({L[i]['src'] for i in s}), cand=sorted(cand)))
    return out


def recall_at(score, S_, share, seeds=20):
    """site recall (all sites, reachable sites) with the top share of crossings flagged, ties broken at random (mean over seeds); exact chance."""
    N = len(score); n = max(1, int(math.ceil(share * N))); rng = np.random.default_rng(0); hits = np.zeros(len(S_))
    for _ in range(seeds):
        o = np.lexsort((rng.random(N), -np.asarray(score, float))); fl = np.zeros(N, bool); fl[o[:n]] = True
        hits += np.array([fl[s['cand']].any() if s['cand'] else False for s in S_], float)
    hits /= seeds
    ch = np.array([1.0 - math.exp(math.lgamma(N - len(s['cand']) + 1) + math.lgamma(N - n + 1) - math.lgamma(N - len(s['cand']) - n + 1) - math.lgamma(N + 1))
                   if s['cand'] and N - len(s['cand']) >= n else (1.0 if s['cand'] else 0.0) for s in S_])
    reach = np.array([bool(s['cand']) for s in S_])
    return dict(share=share, flagged=n, sites=len(S_), reachable=int(reach.sum()), hit=round(float(hits.sum()), 2),
                recall=round(float(hits.mean()), 3) if len(S_) else None, recall_reachable=round(float(hits[reach].mean()), 3) if reach.any() else None,
                chance=round(float(ch.mean()), 3) if len(S_) else None, lift=round(float(hits.mean() / ch.mean()), 2) if len(S_) and ch.mean() > 0 else None)


def aucs(score, y):
    from sklearn.metrics import roc_auc_score, average_precision_score
    y = np.asarray(y); s = np.asarray(score, float)
    if y.sum() == 0 or y.sum() == len(y): return None, None
    return float(roc_auc_score(y, s)), float(average_precision_score(y, s))


def block_bootstrap(xy, y, scores, ref, B=2000, block=2000.0, seed=1):
    """paired 2 km block bootstrap of ROC-AUC and PR-AUC: each score minus `ref`.  -> {name: dict(auc, ci, d_auc vs ref, ci, pr...)}"""
    from sklearn.metrics import roc_auc_score, average_precision_score
    bid = np.floor(xy[:, 0] / block).astype(int) * 100000 + np.floor(xy[:, 1] / block).astype(int)
    ub = np.unique(bid); idx = {b: np.where(bid == b)[0] for b in ub}; rng = np.random.default_rng(seed); y = np.asarray(y)
    res = {k: dict(auc=[], pr=[], dauc=[], dpr=[]) for k in scores}
    for _ in range(B):
        ii = np.concatenate([idx[b] for b in rng.choice(ub, len(ub))]); yy = y[ii]
        if yy.sum() == 0 or yy.sum() == len(yy): continue
        ra = roc_auc_score(yy, np.asarray(scores[ref], float)[ii]); rp = average_precision_score(yy, np.asarray(scores[ref], float)[ii])
        for k, s in scores.items():
            a = roc_auc_score(yy, np.asarray(s, float)[ii]); p = average_precision_score(yy, np.asarray(s, float)[ii])
            res[k]['auc'].append(a); res[k]['pr'].append(p); res[k]['dauc'].append(a - ra); res[k]['dpr'].append(p - rp)
    q = lambda v: [round(float(np.percentile(v, 5)), 3), round(float(np.percentile(v, 95)), 3)] if v else None
    return {k: dict(roc_auc_ci=q(v['auc']), pr_auc_ci=q(v['pr']), d_roc_auc_vs_ref_ci=q(v['dauc']), d_pr_auc_vs_ref_ci=q(v['dpr']), replicates=len(v['auc'])) for k, v in res.items()}


def baseline_scores(rows):
    return {'omega (prior fragility)': [fnum(r.get('omega_wm2'), 0.0) for r in rows],
            'overtopped yes/no': [1.0 if fnum(r.get('over_m'), -1.0) > 0 else 0.0 for r in rows],
            'HDS-5 / overtopping layer': [hds5_layer(r) for r in rows],
            'upstream area': [fnum(r.get('area_km2'), 0.0) for r in rows],
            'peak Q': [fnum(r.get('q_peak_m3s'), 0.0) for r in rows],
            'peak speed': [fnum(r.get('v_max_ms'), 0.0) for r in rows]}


def load_runs(runs_dir):
    R = []
    for d in sorted(glob.glob(os.path.join(runs_dir, '*'))):
        cf = glob.glob(os.path.join(d, 'crossings_*.csv'))
        if not cf or not os.path.exists(os.path.join(d, 'flood_meta.json')): continue
        cfg = json.load(open(os.path.join(d, 'config.json'))); meta = json.load(open(os.path.join(d, 'flood_meta.json')))
        rows = list(csv.DictReader(open(cf[0])))
        R.append(dict(name=os.path.basename(d), storm=cfg['storm'], box=meta['box'], rows=rows))
    return R


def evaluate(runs_dir, out_dir, headline_exclude=('leo48_cn088',), B=2000):
    runs = load_runs(runs_dir); os.makedirs(out_dir, exist_ok=True)
    for R in runs:
        R['labels'] = load_damage_labels(R['storm'], R['box']); R['S'] = match(R['rows'], R['labels']); R['St'] = match(R['rows'], R['labels'], tolerant=True)
        y = np.zeros(len(R['rows']), int)
        for s in R['S']: y[s['cand']] = 1
        R['y'] = y
    cat = [R for R in runs if R['name'] not in headline_exclude]
    res = dict(settings=dict(omega50_wm2=OMEGA50, prior_b1=PRIOR_B1, match_m=MATCH_M, site_m=SITE_M, damage_types=DAMAGE_TYPES, shares=SHARES,
                             features='ln(omega / 300), clip(over_m, -1, 1)', fit='sklearn LogisticRegression C=1 (L2), leave-one-storm-out; prior when < 5 positive crossings in training'),
               runs={}, loso={})
    # leave-one-storm-out fragility (fit on the other catalogue storms' crossings; strict damage labels only)
    for R in runs:
        tr = [Q for Q in cat if Q['storm'] != R['storm']]
        rows = [r for Q in tr for r in Q['rows']]; y = np.concatenate([Q['y'] for Q in tr]) if tr else np.zeros(0, int)
        m = fit(rows, y) if y.sum() >= 5 else None
        R['p_loso'] = fragility(R['rows'], m); res['loso'][R['name']] = m or 'prior (fewer than 5 positive crossings outside this storm)'
        R['p_prior'] = fragility(R['rows'])
    for R in runs:
        sc = {'fragility LOSO': R['p_loso'].tolist(), **baseline_scores(R['rows'])}; N = len(R['rows'])
        e = dict(storm=R['storm'], crossings=N, with_q=int(sum(1 for r in R['rows'] if fnum(r.get('q_peak_m3s'), 0) > 0)),
                 damage_labels=len(R['labels']), damage_labels_exact=sum(1 for l in R['labels'] if l['q'] == 'exact'),
                 strict_sites=len(R['S']), strict_sites_reachable=sum(1 for s in R['S'] if s['cand']), positive_crossings=int(R['y'].sum()),
                 tolerant_sites=len(R['St']), omega_ge_300=int(sum(1 for r in R['rows'] if fnum(r.get('omega_wm2'), 0) >= OMEGA50)),
                 damage_p_ge_50_prior=int((R['p_prior'] >= 0.5).sum()), damage_p_ge_50_loso=int((R['p_loso'] >= 0.5).sum()),
                 omega_pctl=[round(float(np.percentile([fnum(r.get('omega_wm2'), 0) for r in R['rows']], q)), 1) for q in (50, 90, 99)] if N else None,
                 scores={})
        for k, s in sc.items():
            a, p = aucs(s, R['y'])
            e['scores'][k] = dict(roc_auc=None if a is None else round(a, 3), pr_auc=None if p is None else round(p, 3),
                                  strict=[recall_at(s, R['S'], f) for f in SHARES], tolerant=[recall_at(s, R['St'], f) for f in SHARES])
        if R['y'].sum() >= 3:
            xy = np.array([[fnum(r['x']), fnum(r['y'])] for r in R['rows']])
            e['bootstrap_2km_blocks'] = dict(ref='HDS-5 / overtopping layer', B=B, **{'scores': block_bootstrap(xy, R['y'], sc, 'HDS-5 / overtopping layer', B=B)})
        e['sites'] = [dict(labels=s['labels'], types=s['types'], src=s['src'], crossings=[R['rows'][i]['id'] for i in s['cand']],
                           omega=[fnum(R['rows'][i].get('omega_wm2')) for i in s['cand']], over_m=[fnum(R['rows'][i].get('over_m')) for i in s['cand']],
                           p_loso=[round(float(R['p_loso'][i]), 3) for i in s['cand']],
                           rank_pct_omega=[round(float((np.asarray(sc['omega (prior fragility)']) > fnum(R['rows'][i].get('omega_wm2'), 0)).mean() * 100), 1) for i in s['cand']])
                      for s in R['S']]
        res['runs'][R['name']] = e
    # within-storm spatial CV (in-sample storm; context for what a fitted fragility could add with more labelled storms)
    for R in runs:
        if R['y'].sum() < 10: continue
        xy = np.array([[fnum(r['x']), fnum(r['y'])] for r in R['rows']]); bid = (np.floor(xy[:, 0] / 4000) * 1000 + np.floor(xy[:, 1] / 4000)).astype(int)
        p = np.zeros(len(R['rows']))
        for b in np.unique(bid):
            te = bid == b; trn = ~te
            if R['y'][trn].sum() < 5: p[te] = fragility([R['rows'][i] for i in np.where(te)[0]]); continue
            m = fit([R['rows'][i] for i in np.where(trn)[0]], R['y'][trn]); p[te] = fragility([R['rows'][i] for i in np.where(te)[0]], m)
        a, pr = aucs(p, R['y'])
        res['runs'][R['name']]['spatial_cv_4km'] = dict(roc_auc=round(a, 3), pr_auc=round(pr, 3), strict=[recall_at(p, R['S'], f) for f in SHARES],
                                                        note='leave-one-4-km-block-out within this storm (in-sample storm, not a held-out result)')
    # all-storm fit (for the layer, only if adopted)
    rows = [r for Q in cat for r in Q['rows']]; y = np.concatenate([Q['y'] for Q in cat]) if cat else np.zeros(0, int)
    res['fit_all'] = fit(rows, y) if y.sum() >= 5 else None
    json.dump(res, open(os.path.join(out_dir, 'damage.json'), 'w'), indent=1)
    return res



def selftest():
    import tempfile
    rd = tempfile.mkdtemp(); ny = nx = 60; res = 20.0; yy, xx = np.mgrid[0:ny, 0:nx]
    Z = (100 - 0.02 * yy * res + 0.01 * np.abs(xx - 30) * res).astype(np.float32); Z[30, 25:36] += 3; Z[29:32, 29:32] -= 3   # valley S = 0.02, road fill, notch
    H = np.zeros_like(Z); H[:, 30] = 0.5; H[25:30, 28:33] = 3.2
    np.save(f'{rd}/z.npy', Z); np.save(f'{rd}/hmax.npy', H)
    json.dump(dict(box=[100000, 800000, 100000 + nx * res, 800000 + ny * res], res_m=res, shape=[ny, nx]), open(f'{rd}/meta.json', 'w'))
    json.dump(dict(crossings=[dict(id='t1', r=30, c=30, r0=29, r1=32, c0=29, c1=32, zcrest=float(Z[30, 30] + 3), q_peak_m3s=10.0)]), open(f'{rd}/xings.json', 'w'))
    r = extract(rd, f'{rd}/x.csv', channels=False)[0]
    assert r['slope'] == 0.02 and r['over_m'] > 1.0 and r['area_src'] == 'd8', r
    assert abs(r['omega_wm2'] - GAMMA * 10 * 0.02 / r['width_m']) < 1.0, r
    p = fragility([dict(omega_wm2=300, over_m=0), dict(omega_wm2=3000, over_m=0), dict(omega_wm2=30, over_m=0)])
    assert abs(p[0] - 0.5) < 1e-9 and p[1] > 0.96 and p[2] < 0.04, p
    S_ = [dict(cand=[0]), dict(cand=[1, 2]), dict(cand=[])]
    rr = recall_at([3, 2, 1, 0], S_, 0.25); assert rr['hit'] == 1 and abs(rr['chance'] - (0.25 + 0.5 + 0) / 3) < 1e-3 and rr['reachable'] == 2, rr
    rr = recall_at([1, 1, 1, 1], S_, 0.5); assert abs(rr['recall'] - rr['chance']) < 0.12, rr     # all tied = random flagging
    L = layer([dict(id='a', lon=-71.7, lat=42.5, omega_wm2=900, over_m=0.2, q_peak_m3s=5, slope=0.02, width_m=3, span_m=1.0)])[0]
    assert L['damage_p'] > 0.8 and L['repair_class'] == 'box 1.8-3.7 m' and L['expected_cost_usd'] > 0 and 'stream power' in L['why'], L
    print('selftest ok')


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest='cmd')
    e = sub.add_parser('extract'); e.add_argument('--run-dir', required=True); e.add_argument('--out', required=True); e.add_argument('--storm')
    e.add_argument('--no-channels', action='store_true')
    v = sub.add_parser('evaluate'); v.add_argument('--runs', default=os.path.join(ROOT, 'docs', 'proto', 'damage', 'runs'))
    v.add_argument('--out', default=os.path.join(ROOT, 'docs', 'proto', 'damage')); v.add_argument('--boot', type=int, default=2000)
    l = sub.add_parser('layer'); l.add_argument('--crossings', required=True); l.add_argument('--out', required=True)
    l.add_argument('--model', help='fragility json (b0, b1, b2); default: the literature prior')
    ap.add_argument('--selftest', action='store_true')
    a = ap.parse_args()
    if a.selftest: selftest()
    elif a.cmd == 'extract': extract(a.run_dir, a.out, a.storm, not a.no_channels)
    elif a.cmd == 'evaluate': evaluate(a.runs, a.out, B=a.boot)
    elif a.cmd == 'layer':
        rows = list(csv.DictReader(open(a.crossings))); m = json.load(open(a.model)) if a.model else None
        recs = layer(rows, m); write_geojson(a.out, recs); print(f'{len(recs)} crossings -> {a.out}; damage_p >= 0.5: {sum(r["damage_p"] >= 0.5 for r in recs)}')
    else: ap.print_help()


if __name__ == '__main__':
    main()
