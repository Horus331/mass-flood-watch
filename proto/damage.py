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


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest='cmd')
    e = sub.add_parser('extract'); e.add_argument('--run-dir', required=True); e.add_argument('--out', required=True); e.add_argument('--storm')
    e.add_argument('--no-channels', action='store_true')
    ap.add_argument('--selftest', action='store_true')
    a = ap.parse_args()
    if a.cmd == 'extract': extract(a.run_dir, a.out, a.storm, not a.no_channels)
    else: ap.print_help()


if __name__ == '__main__':
    main()
