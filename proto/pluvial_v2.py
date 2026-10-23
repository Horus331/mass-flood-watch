"""Pluvial rule v2 (ROADMAP_research.md T3; protocol docs/proto/PROTOCOL.md; write-up docs/proto/urban/PLUVIAL_v2.md).

v1 (PROTO_PLUVIAL=1, docs/proto/urban/FINDINGS.md): Q = 0.6 * i_peak1h * A_up vs a fixed 0.5 m3/s, HAND <= 0.5 m, >= 15 road segments in 300 m.
v2 replaces each fixed piece by its engineering form (all constants below were fixed before any held-out storm was scored):

    Tc      Kirpich on the longest D8 flow path L (m) and its mean slope S = (z_head - z_segment) / L:
            Tc = 0.0195 L^0.77 S^-0.385 min, x (1 - 0.6 TIA_up) (Kirpich's 0.4 factor for paved surfaces, scaled by the upstream impervious
            share), clipped to 5-120 min
    i(Tc)   peak Tc-minute intensity at the segment, log-log interpolated between the 5/10/15/20/30/45/60/90/120-min maxima of MRMS PrecipRate
            (2 min) volume-matched to hourly Pass2 (`rain` below; table docs/proto/urban/pluvial_v2/intensity_<storm>.csv)
    C       0.90 DCIA_up + 0.20 (1 - DCIA_up); DCIA per 20 m cell = Sutherland (1995) average 0.1 TIA%^1.5 from NLCD 2021 impervious (as LF_LOSS=cn_dcia)
    Q       C i(Tc) A_up / 3.6   (m3/s; i mm/h, A km2)
    Q_cap   n_in Q_inlet (1 - c_clog);  n_in = max(1, road length in the D8 catchment / 100 m);  Q_inlet = HEC-22 sag grate at d = 0.10 m:
            0.6 x 0.6 m grate against the curb, weir 1.66 (2W + L) d^1.5 = 0.0945 m3/s (orifice 0.67 A_open sqrt(2 g d) = 0.169 does not control);
            on grade (segment slope > 1 %) the grate intercepts half of that (HEC-22 frontal-flow efficiency ~0.5 for a 0.6 m grate in gutter flow)
    P       Phi(ln(Q / Q_cap) / 0.5) on HAND <= 0.5 m and >= D road segments within 300 m (as v1), else 0;  p_close = max(p_close, P)
    LOSO    c_clog in {0.3, 0.5, 0.7} and D in {0, 10, 15, 20} chosen on the 8 other storms: max pooled site hits at 3 % flagged, subject to mean rule
            share <= default + 1 pt; ties -> lower mean rule share.

Subcommands
    python proto/pluvial_v2.py geo  --run docs/proto/parity/catalog/<run> --storm S --out docs/proto/urban/pluvial_v2/geo_S.csv   (GitHub Actions:
                                    needs HF_TOKEN for the 10 m DEM / NLCD tiles; .github/workflows/pluvial_v2.yml)
    python proto/pluvial_v2.py rain --storm S      (offline: docs/proto/rain/data/S/mrms_box.npz -> docs/proto/urban/pluvial_v2/intensity_S.csv)
    python proto/pluvial_v2.py loso                (offline: LOSO + score_v2 scoring + --compare against default and v1)
    python proto/pluvial_v2.py --selftest
"""
import argparse
import csv
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
OUTD = os.path.join(ROOT, 'docs', 'proto', 'urban', 'pluvial_v2')
PAR = os.path.join(ROOT, 'docs', 'proto', 'parity', 'catalog')
TUR = os.path.join(ROOT, 'docs', 'proto', 'turing')
AREA = dict(aug2021='worcester', aug2023='metrowest', aug2023b='millbury', aug2026='leominster', jul2021='worcester', jul2023='worcester',
            sep2021='worcester', sep2022='webster', sep2023='leominster')
REPO = 'mohabeldokla/mass-flood-watch-tiles'

# ---- v2 constants (fixed 23 Oct 2026 before any held-out score) ----
DUR_MIN = (5, 10, 15, 20, 30, 45, 60, 90, 120)
TC_MIN, TC_MAX = 5.0, 120.0
KIRPICH_PAVED = 0.6           # Tc x (1 - 0.6 TIA_up): 0.4 x Kirpich on fully paved ground
S_MIN, S_MAX = 0.005, 0.30
C_IMP, C_PERV = 0.90, 0.20
INLET_SPACING_M = 100.0
Q_SAG = 1.66 * (2 * 0.6 + 0.6) * 0.10 ** 1.5    # 0.0945 m3/s, HEC-22 sag grate weir at d = 0.10 m
GRADE_EFF = 0.5
GRADE_SLOPE_PCT = 1.0
SIGMA_LN = 0.5
HAND_M = 0.5
DENS_R_M = 300.0
CLOG_GRID = (0.3, 0.5, 0.7)
DENS_GRID = (0, 10, 15, 20)
SHARE = 0.03
SHARE_TOL = 0.01
V1 = dict(c=0.6, qcap=0.5, dens=15)


def phi(x):
    from scipy.special import ndtr
    return ndtr(x)


# ------------------------------------------------------------------------------------------------ grids (catchment attributes)
def priority_fill(Z, eps=1e-4):
    """Priority-flood depression filling with an epsilon gradient (Barnes et al. 2014): every cell drains to the box edge."""
    import heapq
    H, W = Z.shape; z = np.nan_to_num(Z.astype(np.float64), nan=-1e3).ravel().copy(); done = np.zeros(H * W, bool); pq = []
    for r in range(H):
        for c in (0, W - 1):
            i = r * W + c
            if not done[i]: done[i] = True; heapq.heappush(pq, (z[i], i))
    for c in range(W):
        for r in (0, H - 1):
            i = r * W + c
            if not done[i]: done[i] = True; heapq.heappush(pq, (z[i], i))
    zl = z.tolist(); dl = done.tolist(); nb = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
    while pq:
        zi, i = heapq.heappop(pq); r, c = divmod(i, W)
        for dr, dc in nb:
            rr, cc = r + dr, c + dc
            if rr < 0 or rr >= H or cc < 0 or cc >= W: continue
            j = rr * W + cc
            if dl[j]: continue
            dl[j] = True
            if zl[j] <= zi: zl[j] = zi + eps
            heapq.heappush(pq, (zl[j], j))
    return np.asarray(zl).reshape(H, W)


def catchment_grids(Z, TIA, ROAD, res):
    """Per cell: upstream area (km2), longest flow path L (m) and the raw elevation at its head, upstream mean impervious share (TIA) and
    directly connected share (DCIA, Sutherland average), upstream road length (m).  D8 on the priority-filled DEM."""
    Zf = priority_fill(Z); H, W = Zf.shape; zp = np.pad(Zf, 1, constant_values=-np.inf)
    best = np.zeros((H, W)); rec = np.full((H, W), -1, np.int64); dist = np.zeros((H, W)); rr, cc = np.mgrid[0:H, 0:W]
    for dr in (-1, 0, 1):
        for dc in (-1, 0, 1):
            if dr == 0 and dc == 0: continue
            d = res * (math.sqrt(2.0) if dr and dc else 1.0)
            drop = (Zf - zp[1 + dr:1 + dr + H, 1 + dc:1 + dc + W]) / d
            out = (rr + dr < 0) | (rr + dr >= H) | (cc + dc < 0) | (cc + dc >= W)
            b = (drop > best) & ~out; best = np.where(b, drop, best); rec = np.where(b, (rr + dr) * W + (cc + dc), rec); dist = np.where(b, d, dist)
    tia = np.clip(np.nan_to_num(TIA), 0, 1); dcia = np.where(tia >= 0.01, np.minimum(1.0, 0.1 * (100 * tia) ** 1.5 / 100), 0.0)
    acc = np.ones(H * W).tolist(); st = tia.ravel().tolist(); sd = dcia.ravel().tolist(); rd = np.nan_to_num(ROAD).ravel().astype(float).tolist()
    L = np.zeros(H * W).tolist(); zh = np.nan_to_num(Z.astype(float), nan=0.0).ravel().tolist(); recf = rec.ravel().tolist(); df = dist.ravel().tolist()
    for i in np.argsort(-Zf.ravel(), kind='stable').tolist():
        j = recf[i]
        if j < 0: continue
        acc[j] += acc[i]; st[j] += st[i]; sd[j] += sd[i]; rd[j] += rd[i]
        l_ = L[i] + df[i]
        if l_ > L[j]: L[j] = l_; zh[j] = zh[i]
    a = np.asarray(acc).reshape(H, W)
    return dict(area_km2=a * res * res / 1e6, L_m=np.asarray(L).reshape(H, W), zhead=np.asarray(zh).reshape(H, W),
                tia_up=np.asarray(st).reshape(H, W) / a, dcia_up=np.asarray(sd).reshape(H, W) / a, road_up_m=np.asarray(rd).reshape(H, W))


def segment_attrs(G, Z, Q, n):
    """Per segment: the attributes of the cell with the largest upstream area within one cell of any of its road points (as
    closure_ml.geo_features takes A3 = 3x3 max of A)."""
    H, W = G['area_km2'].shape; r0, c0, seg = np.asarray(Q['r']), np.asarray(Q['c']), np.asarray(Q['seg'])
    bestA = np.full(len(r0), -1.0); bi = np.zeros(len(r0), int)
    for dr in (-1, 0, 1):
        for dc in (-1, 0, 1):
            r = np.clip(r0 + dr, 0, H - 1); c = np.clip(c0 + dc, 0, W - 1); a = G['area_km2'][r, c]; b = a > bestA
            bestA = np.where(b, a, bestA); bi = np.where(b, r * W + c, bi)
    keys = ('area_km2', 'L_m', 'zhead', 'tia_up', 'dcia_up', 'road_up_m')
    out = {k: np.full(n, np.nan) for k in keys + ('zout',)}
    order = np.lexsort((bestA, seg)); last = np.r_[seg[order][1:] != seg[order][:-1], True]
    for p in order[last]:
        s = seg[p]; i = bi[p]
        for k in keys: out[k][s] = G[k].ravel()[i]
        out['zout'][s] = Z.ravel()[i]
    return out


def build_box(meta, tok):
    """20 m mean DEM and NLCD impervious share on the run box from the 10 m tiles (as w9_lisflood.build_inputs, without channel burn,
    crossing notches or breaching: depressions are filled instead)."""
    from huggingface_hub import hf_hub_download
    from PIL import Image
    x0, y0, x1, y1 = meta['box']; RES = float(meta['res_m']); T = 20000; k = int(round(RES / 10))
    idx = json.load(open(hf_hub_download(REPO, 'data/dem10/index.json', repo_type='dataset', token=tok)))
    nx10, ny10 = int((x1 - x0) / 10), int((y1 - y0) / 10)
    Z10 = np.full((ny10, nx10), np.nan, np.float32); I10 = np.zeros((ny10, nx10), np.float32)
    need = [(key, v) for key, v in idx.items() if v['valid'] > 0 and v['x'] < x1 and v['x'] + T > x0 and v['y'] < y1 and v['y'] + T > y0]

    def paste(dst, a, v):
        c0 = int((v['x'] - x0) / 10); r0 = int((y1 - (v['y'] + T)) / 10)
        rs, cs = max(r0, 0), max(c0, 0); re_, ce = min(r0 + a.shape[0], ny10), min(c0 + a.shape[1], nx10)
        dst[rs:re_, cs:ce] = a[rs - r0:re_ - r0, cs - c0:ce - c0]
    got = 0
    for key, v in need:
        paste(Z10, np.load(hf_hub_download(REPO, f'data/dem10/{key}.npy', repo_type='dataset', token=tok)), v)
        try: paste(I10, np.asarray(Image.open(hf_hub_download(REPO, f'data/nlcd10/{key}.png', repo_type='dataset', token=tok))).astype(np.float32), v); got += 1
        except Exception as e: print('nlcd tile missing', key, repr(e)[:80])
    ny, nx = ny10 // k, nx10 // k
    Z = np.nanmean(Z10[:ny * k, :nx * k].reshape(ny, k, nx, k), axis=(1, 3)).astype(np.float32)
    Z = np.where(np.isnan(Z), -2.0, Z)
    IMP = I10[:ny * k, :nx * k].reshape(ny, k, nx, k).mean(axis=(1, 3)) / 100.0
    print(f'tiles {len(need)}, nlcd {got}; grid {Z.shape}; mean impervious {IMP.mean() * 100:.1f} %', flush=True)
    return Z, IMP


def cmd_geo(a):
    import time
    sys.path.insert(0, os.path.join(ROOT, 'sim', 'infra')); import impacts as IM
    meta = json.load(open(os.path.join(a.run, 'flood_meta.json'))); res = float(meta['res_m']); t = time.time()
    Z, IMP = build_box(meta, os.environ.get('HF_TOKEN'))
    meta = dict(meta, shape=list(Z.shape))
    S = json.load(open(os.path.join(ROOT, 'docs', 'graph_segments.json'))); Q = IM.road_points(S, meta); n = len(S['props']['road'])
    ROAD = np.zeros(Z.shape); np.add.at(ROAD, (Q['r'], Q['c']), res / 2)
    G = catchment_grids(Z, IMP, ROAD, res); print(f'catchment grids {time.time() - t:.0f} s', flush=True)
    A = segment_attrs(G, Z, Q, n)
    feat = os.path.join(a.run, f'features_{a.storm}.csv'); segs = [int(r['segment']) for r in csv.DictReader(open(feat))]
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    with open(a.out, 'w', newline='') as f:
        w = csv.writer(f); w.writerow(['segment', 'area_km2', 'L_m', 'zhead_m', 'zout_m', 'tia_up', 'dcia_up', 'road_up_m'])
        for s in segs:
            w.writerow([s] + [('' if not np.isfinite(A[k][s]) else round(float(A[k][s]), nd)) for k, nd in
                              (('area_km2', 5), ('L_m', 0), ('zhead', 2), ('zout', 2), ('tia_up', 3), ('dcia_up', 3), ('road_up_m', 0))])
    print('wrote', a.out, len(segs), f'{time.time() - t:.0f} s')


# ------------------------------------------------------------------------------------------------ sub-hourly intensity
def intensity_grids(npz, t0, hours):
    """Max D-minute intensity (mm/h) per MRMS cell over the run window, for D in DUR_MIN.  PrecipRate (mm/h, 2-min stamps, each holding
    for +-1 min) gives the timing inside each Pass2 hour; the hour's Pass2 depth is distributed in proportion (volume-matched, as
    lf_subhourly LF_RAIN_SUB=preciprate).  Hours with < 0.1 mm radar depth or < half the minutes covered are spread evenly."""
    import pandas as pd
    z = np.load(npz); t0 = pd.Timestamp(t0).tz_localize(None)
    p2t = pd.to_datetime(z['pass2_t']); P2 = np.nan_to_num(z['pass2'].astype(np.float32)); prt = pd.to_datetime(z['preciprate_t']); PR = z['preciprate'].astype(np.float32)
    ny, nx = P2.shape[1:]; M = int(hours * 60); minute = np.zeros((M, ny, nx), np.float32); cover = np.zeros(M, int)
    idx = {int((t - t0).total_seconds() // 60): k for k, t in enumerate(prt)}
    R1 = np.full((M, ny, nx), np.nan, np.float32)
    for m in range(M):                     # minute m covers [t0+m, t0+m+1); the 2-min stamp s holds for [s-1, s+1)
        k = idx.get(m + 1) if (m + 1) in idx else idx.get(m)
        if k is not None: R1[m] = PR[k]
    uni = 0
    for h in range(hours):
        te = t0 + pd.Timedelta(hours=h + 1); j = np.nonzero(p2t == te)[0]
        if not len(j): continue
        p2 = P2[j[0]]; blk = R1[h * 60:(h + 1) * 60]; ok = np.isfinite(blk).sum(0) >= 30
        raw = np.nansum(np.maximum(blk, 0), 0) / 60.0; use = ok & (raw >= 0.1)
        w = np.where(use[None], np.nan_to_num(np.maximum(blk, 0)) / 60.0 / np.where(use, raw, 1)[None], 1.0 / 60)
        minute[h * 60:(h + 1) * 60] = w * p2[None]; uni += int(((~use) & (p2 > 0.1)).sum())
    cum = np.concatenate([np.zeros((1, ny, nx), np.float32), np.cumsum(minute, 0, dtype=np.float64).astype(np.float32)])
    out = {}
    for D in DUR_MIN:
        D_ = min(D, M); out[D] = (cum[D_:] - cum[:-D_]).max(0) * 60.0 / D
    out['clock1h'] = P2.max(0)
    return out, z['lat'], z['lon'], dict(minutes=M, uniform_hours_cells=uni)


def cmd_rain(a):
    from scipy.interpolate import RegularGridInterpolator
    from pyproj import Transformer
    ev = {e['id']: e for e in json.load(open(os.path.join(ROOT, 'docs', 'proto', 'obs', 'catalog.json')))['events']}[a.storm]
    run = os.path.join(PAR, f'{a.storm}_{AREA[a.storm]}_20m'); meta = json.load(open(os.path.join(run, 'flood_meta.json')))
    hours = int(json.load(open(os.path.join(run, 'config.json')))['hours'])
    assert meta['t0'] == ev['t0'], (meta['t0'], ev['t0'])
    I, lat, lon, info = intensity_grids(os.path.join(ROOT, 'docs', 'proto', 'rain', 'data', a.storm, 'mrms_box.npz'), ev['t0'], hours)
    rows = list(csv.DictReader(open(os.path.join(run, f'features_{a.storm}.csv'))))
    cx = np.array([float(r['cx'] or 'nan') for r in rows]); cy = np.array([float(r['cy'] or 'nan') for r in rows])
    lo, la = Transformer.from_crs(26986, 4326, always_xy=True).transform(cx, cy)
    inside = (la <= lat.max()) & (la >= lat.min()) & (lo >= lon.min()) & (lo <= lon.max())
    print(a.storm, 'segments', len(rows), 'outside the MRMS crop', int((~inside & np.isfinite(cx)).sum()), info)
    pts = np.column_stack([np.clip(la, lat.min(), lat.max()), np.clip(lo, lon.min(), lon.max())])
    cols = {}
    for k, g in I.items():
        f = RegularGridInterpolator((lat[::-1], lon), g[::-1].astype(np.float64), bounds_error=False, fill_value=np.nan); cols[k] = f(pts)
    os.makedirs(OUTD, exist_ok=True); out = os.path.join(OUTD, f'intensity_{a.storm}.csv')
    with open(out, 'w', newline='') as f:
        w = csv.writer(f); w.writerow(['segment'] + [f'i{D}' for D in DUR_MIN] + ['p1h_clock', 'peak1h_mm_run'])
        for j, r in enumerate(rows):
            w.writerow([r['segment']] + ['' if not np.isfinite(cols[k][j]) else round(float(cols[k][j]), 1) for k in list(DUR_MIN) + ['clock1h']] + [r['peak1h_mm']])
    p1 = np.array([float(r['peak1h_mm'] or 0) for r in rows]); ok = np.isfinite(cols['clock1h']) & (p1 > 5)
    print('  Pass2 clock-hour max here / run peak1h (median):', np.round(np.median(cols['clock1h'][ok] / p1[ok]), 3) if ok.any() else None,
          '| i15 / i60 median where i60 >= 5:', np.round(np.median((cols[15] / cols[60])[cols[60] >= 5]), 2) if (cols[60] >= 5).any() else None)
    print('wrote', out)


# ------------------------------------------------------------------------------------------------ the rule
def interp_idf(I, tc):
    """I: (n, len(DUR_MIN)) intensities; tc (n,) minutes -> i(Tc), log-log between the tabulated durations (clamped at the ends)."""
    d = np.log(np.asarray(DUR_MIN, float)); x = np.log(np.clip(tc, DUR_MIN[0], DUR_MIN[-1])); k = np.clip(np.searchsorted(d, x) - 1, 0, len(d) - 2)
    w = (x - d[k]) / (d[k + 1] - d[k]); lo = np.log(np.maximum(I[np.arange(len(tc)), k], 1e-3)); hi = np.log(np.maximum(I[np.arange(len(tc)), k + 1], 1e-3))
    return np.exp(lo + w * (hi - lo)) * (I[np.arange(len(tc)), k] > 0)


def v2_terms(area_km2, L_m, zhead, zout, tia_up, dcia_up, road_up_m, slope_pct, I):
    """-> dict(tc, i, C, Q, Qcap1 = Q_cap at c_clog 0) per segment.  I: (n, len(DUR_MIN)) or (n,) hourly (then i = I)."""
    L = np.maximum(np.nan_to_num(L_m), 20.0); S = np.clip(np.nan_to_num((zhead - zout) / L), S_MIN, S_MAX); tia = np.clip(np.nan_to_num(tia_up), 0, 1)
    tc = np.clip(0.0195 * L ** 0.77 * S ** -0.385 * (1 - KIRPICH_PAVED * tia), TC_MIN, TC_MAX)
    i = interp_idf(np.nan_to_num(I), tc) if np.ndim(I) == 2 else np.nan_to_num(I)
    C = C_IMP * np.clip(np.nan_to_num(dcia_up), 0, 1) + C_PERV * (1 - np.clip(np.nan_to_num(dcia_up), 0, 1))
    Q = C * i * np.nan_to_num(area_km2) / 3.6
    n_in = np.maximum(1.0, np.nan_to_num(road_up_m) / INLET_SPACING_M); q_in = np.where(np.nan_to_num(slope_pct) <= GRADE_SLOPE_PCT, Q_SAG, GRADE_EFF * Q_SAG)
    return dict(tc=tc, i=i, C=C, Q=Q, Qcap1=n_in * q_in)


def v2_probability(T, hand_m, dens, c_clog, dmin):
    gate = (np.nan_to_num(hand_m, nan=20.0) <= HAND_M) & (dens >= dmin)
    return np.where(gate, phi(np.log(np.maximum(T['Q'], 1e-9) / (T['Qcap1'] * (1 - c_clog))) / SIGMA_LN), 0.0)


def density(cx, cy, ok):
    from scipy.spatial import cKDTree
    dens = np.zeros(len(cx)); ok = ok & np.isfinite(cx) & np.isfinite(cy)
    if ok.any():
        xy = np.column_stack([cx[ok], cy[ok]]); dens[ok] = [len(v) for v in cKDTree(xy).query_ball_point(xy, DENS_R_M)]
    return dens


# ------------------------------------------------------------------------------------------------ LOSO evaluation
def F(x):
    try: return float(x)
    except (TypeError, ValueError): return np.nan


def load_storm(storm, base_dir):
    """Features + v2 inputs of one storm's catalogue run, and the score_v2 run dict (sites as score_v2 builds them)."""
    import score_v2 as SV
    run = os.path.join(base_dir, f'{storm}_{AREA[storm]}_20m'); rows = list(csv.DictReader(open(os.path.join(run, f'features_{storm}.csv'))))
    col = lambda k: np.array([F(r[k]) for r in rows])
    D = dict(storm=storm, run=run, rows=rows, seg=np.array([int(r['segment']) for r in rows]), p=np.nan_to_num(col('p_close')), depth=np.nan_to_num(col('peak_depth_m')),
             p_depth=np.nan_to_num(col('p_depth')), hand=col('hand_m'), area=col('area_km2'), slope=col('slope_pct'), cx=col('cx'), cy=col('cy'), p1h=np.nan_to_num(col('peak1h_mm')))
    D['dens'] = density(D['cx'], D['cy'], np.ones(len(rows), bool))
    gf = os.path.join(OUTD, f'geo_{storm}.csv'); inf = os.path.join(OUTD, f'intensity_{storm}.csv')
    G = {int(r['segment']): r for r in csv.DictReader(open(gf))} if os.path.exists(gf) else {}
    IT = {int(r['segment']): r for r in csv.DictReader(open(inf))} if os.path.exists(inf) else {}
    D['has_geo'] = bool(G); D['has_rain'] = bool(IT)
    g = lambda k: np.array([F(G.get(s, {}).get(k)) for s in D['seg']])
    D['geo'] = {k: g(k) for k in ('area_km2', 'L_m', 'zhead_m', 'zout_m', 'tia_up', 'dcia_up', 'road_up_m')}
    D['I'] = np.array([[F(IT.get(s, {}).get(f'i{d}')) for d in DUR_MIN] for s in D['seg']]) if IT else None
    R = SV.load_run(run, storm); assert np.array_equal(R['seg'], D['seg'])
    D['R'] = R; D['sites'] = sites_of(R)
    return D


def sites_of(R):
    import score_v2 as SV
    labs = {l['key']: l for l in R['labels']}; mk = [k for k, v in R['matches'].items() if k in labs and v]
    cl = SV.link_clusters(np.array([[labs[k]['x'], labs[k]['y']] for k in mk]).reshape(-1, 2), SV.SITE_LINK_M)
    return [sorted({s for i in np.nonzero(cl == c)[0] for s in R['matches'][mk[i]]}) for c in (np.unique(cl) if len(cl) else [])]


def hits_at_share(D, p, share=SHARE):
    import score_v2 as SV
    n = len(p); k = int(round(share * n)); key = SV.rank_key(p, D['depth'])
    return float(np.mean([[bool(m[s].any()) for s in D['sites']] for m in SV.topk_masks(key, k)], axis=0).sum()) if D['sites'] else 0.0


def v2_inputs(D, hourly=False):
    G = D['geo']; A = np.where(np.isfinite(G['area_km2']), G['area_km2'], D['area'])
    I = D['p1h'] if (hourly or D['I'] is None) else D['I']
    return v2_terms(A, G['L_m'], G['zhead_m'], G['zout_m'], G['tia_up'], G['dcia_up'], G['road_up_m'], D['slope'], I)


def v1_p(D):
    q = V1['c'] * D['p1h'] / 3.6 * np.nan_to_num(D['area'])
    gate = (np.nan_to_num(D['hand'], nan=20.0) <= HAND_M) & (D['dens'] >= V1['dens'])
    return np.where(gate, phi(np.log(np.maximum(q, 1e-9) / V1['qcap']) / SIGMA_LN), 0.0)


def write_candidate(D, p, dest):
    """A scoring folder: the run's flood_meta / matches, and features with p_close replaced (score_v2 reads nothing else)."""
    import shutil
    os.makedirs(dest, exist_ok=True); s = D['storm']
    for f in ('flood_meta.json', f'matches_{s}.json'): shutil.copy(os.path.join(D['run'], f), dest)
    with open(os.path.join(dest, f'features_{s}.csv'), 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(D['rows'][0].keys())); w.writeheader()
        for r, v in zip(D['rows'], p): w.writerow(dict(r, p_close=round(float(v), 3)))
    return dest


def cmd_loso(a):
    sys.path.insert(0, HERE); import score_v2 as SV
    import tempfile
    base_dir = PAR if all(os.path.exists(os.path.join(PAR, f'{s}_{AREA[s]}_20m', f'features_{s}.csv')) for s in AREA) else TUR
    print('baseline catalogue:', os.path.relpath(base_dir, ROOT), flush=True)
    S = {s: load_storm(s, base_dir) for s in SV.LOSO9}
    for s, D in S.items(): print(f"{s:9s} segs {len(D['seg']):5d} sites {len(D['sites']):3d} geo {D['has_geo']} subhourly {D['has_rain']}", flush=True)
    base = {s: D['p'] for s, D in S.items()}
    T = {s: v2_inputs(D) for s, D in S.items()}; TH = {s: v2_inputs(D, hourly=True) for s, D in S.items()}
    grid = [(c, d) for c in CLOG_GRID for d in DENS_GRID]

    def cand(s, par, terms): return np.maximum(base[s], v2_probability(terms[s], S[s]['hand'], S[s]['dens'], *par))

    def select(train, terms):
        sh0 = np.mean([(base[s] >= 0.5).mean() for s in train]); best = None; tab = []
        for par in grid:
            ps = {s: cand(s, par, terms) for s in train}; h = sum(hits_at_share(S[s], ps[s]) for s in train); sh = np.mean([(ps[s] >= 0.5).mean() for s in ps])
            tab.append(dict(c_clog=par[0], dens=par[1], hits=round(h, 2), rule_share=round(sh, 4)))
            if sh <= sh0 + SHARE_TOL and (best is None or h > best[0] + 1e-9 or (abs(h - best[0]) < 1e-9 and sh < best[1])): best = (h, sh, par)
        return (best[2] if best else (0.7, 20)), tab
    res = dict(baseline_dir=os.path.relpath(base_dir, ROOT), constants=dict(DUR_MIN=DUR_MIN, TC=[TC_MIN, TC_MAX], KIRPICH_PAVED=KIRPICH_PAVED, C=[C_IMP, C_PERV],
               Q_SAG=Q_SAG, GRADE_EFF=GRADE_EFF, INLET_SPACING_M=INLET_SPACING_M, SIGMA_LN=SIGMA_LN, HAND_M=HAND_M, CLOG_GRID=CLOG_GRID, DENS_GRID=DENS_GRID,
               share=SHARE, share_tol=SHARE_TOL, v1=V1), folds={}, folds_hourly={})
    P2 = {}; PH = {}
    for s in SV.LOSO9:
        tr = [t for t in SV.LOSO9 if t != s]
        par, tab = select(tr, T); P2[s] = cand(s, par, T); res['folds'][s] = dict(c_clog=par[0], dens=par[1])
        parh, _ = select(tr, TH); PH[s] = cand(s, parh, TH); res['folds_hourly'][s] = dict(c_clog=parh[0], dens=parh[1])
        print(f'fold {s}: v2 {par}  v2-hourly {parh}', flush=True)
    P1 = {s: np.maximum(base[s], v1_p(S[s])) for s in SV.LOSO9}
    # diagnostics per storm (rule share, hits at 3 %, terms at the sites)
    diag = {}
    for s, D in S.items():
        t = T[s]; site_terms = []
        for st in D['sites']:
            j = st[int(np.argmax(t['Q'][st] / t['Qcap1'][st]))]
            site_terms.append(dict(seg=int(D['seg'][j]), road=D['rows'][j]['road'], town=D['rows'][j]['town'], hand=F(D['rows'][j]['hand_m']), dens=int(D['dens'][j]),
                                   A_km2=round(float(v2_inputs(D)['Q'][j] * 0 + np.nan_to_num(D['geo']['area_km2'][j])), 4), tc_min=round(float(t['tc'][j]), 1),
                                   i_tc=round(float(t['i'][j]), 1), p1h=round(float(D['p1h'][j]), 1), C=round(float(t['C'][j]), 2), Q=round(float(t['Q'][j]), 3),
                                   Qcap_c0=round(float(t['Qcap1'][j]), 3), p_v2=round(float(P2[s][j]), 3), p_base=round(float(base[s][j]), 3)))
        diag[s] = dict(rule_share=dict(base=float((base[s] >= 0.5).mean()), v1=float((P1[s] >= 0.5).mean()), v2=float((P2[s] >= 0.5).mean()), v2_hourly=float((PH[s] >= 0.5).mean())),
                       hits3=dict(base=hits_at_share(D, base[s]), v1=hits_at_share(D, P1[s]), v2=hits_at_share(D, P2[s]), v2_hourly=hits_at_share(D, PH[s])),
                       sites=len(D['sites']), site_terms=site_terms,
                       tc_median=float(np.median(t['tc'])), i_over_p1h_median_hand_low=float(np.nanmedian((t['i'] / np.maximum(D['p1h'], 0.1))[(D['hand'] <= 0.5) & (D['p1h'] > 5)])) if ((D['hand'] <= 0.5) & (D['p1h'] > 5)).any() else None)
    res['diag'] = diag
    # null model: v2's extra rule-flagged segments drawn at random from the gate pool (HAND <= 0.5, dens >= the fold's D)
    rng = np.random.default_rng(0); null = {}
    for s in SV.HELDOUT:
        D = S[s]; add = int(((P2[s] >= 0.5) & ~(base[s] >= 0.5)).sum()); pool = np.nonzero(~(base[s] >= 0.5) & (np.nan_to_num(D['hand'], nan=20) <= HAND_M) & (D['dens'] >= res['folds'][s]['dens']))[0]
        g = []
        for _ in range(200):
            p = base[s].copy(); p[rng.choice(pool, min(add, len(pool)), replace=False)] = 1.0; g.append(hits_at_share(D, p) - hits_at_share(D, base[s]))
        null[s] = dict(added=add, mean_gain_at_3pct=float(np.mean(g)))
    res['null_random_extra'] = null
    # full score_v2 scoring of the fold predictions, and the pre-registered comparison
    tmp = tempfile.mkdtemp(prefix='pluv2_'); scored = {}
    for name, P in (('base', base), ('v1', P1), ('v2', P2), ('v2_hourly', PH)):
        runs = []
        for s in SV.LOSO9:
            d = write_candidate(S[s], P[s], os.path.join(tmp, name, s)); r = SV.score_run(SV.load_run(d, s)); r.update(primary=True, group=name); runs.append(r)
        scored[name] = dict(runs=runs); print('scored', name, flush=True)
    os.makedirs(OUTD, exist_ok=True)
    k_var = 2
    cmp = {}
    for b, c in (('base', 'v2'), ('v1', 'v2'), ('base', 'v1'), ('base', 'v2_hourly')):
        cmp[f'{c}_vs_{b}'] = SV.compare(scored[b], scored[c], rule=dict(SV.ADOPT, alpha=SV.ADOPT['alpha'] / k_var))
    res['compare'] = cmp; res['k_variants'] = k_var
    pools = {}
    for name, sc in scored.items():
        P = {r['storm']: r for r in sc['runs']}
        pools[name] = {pn: SV.pooled([P[s] for s in st], 'box', boot=a.boot) for pn, st in (('heldout7', SV.HELDOUT), ('dev2', SV.DEV), ('all9', SV.LOSO9))}
    res['pools'] = {n_: {pn: dict(point={k: v for k, v in pl['point'].items() if k in ('rule', 'share_0.03', 'share_0.05', 'share_0.01', 'pr_auc_seg', 'pr_auc_site')},
                                  ci90={k: v for k, v in pl['ci90'].items() if k in ('rule', 'share_0.03')}, n_sites=pl['n_sites']) for pn, pl in d.items()} for n_, d in pools.items()}
    res['per_storm'] = {n_: {r['storm']: dict(sites=r['domains']['box']['n_sites'], hits3=r['domains']['box']['shares']['0.03']['site_hits'],
                                              rule_share=r['domains']['box']['rule']['share'], rule_hits=r['domains']['box']['rule']['site_hits'], rule_lift=r['domains']['box']['rule']['lift'],
                                              fss300_3pct=r['domains']['box']['shares']['0.03']['fss']['300']['fss'], fss300_chance=r['domains']['box']['shares']['0.03']['fss']['300']['chance'])
                         for r in sc['runs']} for n_, sc in scored.items()}
    for name, sc in scored.items():                       # the hit vectors --compare needs, small enough to commit
        json.dump(dict(made_by='proto/pluvial_v2.py loso', variant=name, runs=sc['runs']), open(os.path.join(OUTD, f'score_{name}.json'), 'w'))
    json.dump(res, open(os.path.join(OUTD, 'loso.json'), 'w'), indent=1, default=float)
    for k, v in cmp.items():
        print(k, 'adopt' if v['adopt'] else 'reject', {kk: round(vv, 3) if isinstance(vv, float) else vv for kk, vv in v.items() if kk in ('delta_recall', 'delta_recall_lower', 'delta_fss', 'worst_storm_change')},
              v['lift_rule'], v['checks'])
    for name in scored:
        pl = res['pools'][name]['heldout7']['point']
        print(f"{name:10s} OOS-7 recall@3% {pl['share_0.03']['site_recall']:.3f} fss300@3% {pl['share_0.03']['fss300']:.4f} rule recall {pl['rule']['site_recall']:.3f} "
              f"rule lift {pl['rule']['lift']:.2f}  shares " + ' '.join(f"{s}:{res['per_storm'][name][s]['rule_share'] * 100:.2f}" for s in SV.HELDOUT))


# ------------------------------------------------------------------------------------------------ selftest
def selftest():
    ok = True

    def check(name, c):
        nonlocal ok; ok &= bool(c); print(('PASS ' if c else 'FAIL ') + name)
    # tilted plane draining south: the bottom-row cell of column j collects the whole column
    H, W = 40, 30; Z = np.add.outer(np.arange(H)[::-1] * 0.5, np.zeros(W)) + 100; TIA = np.full((H, W), 0.5); ROAD = np.zeros((H, W)); ROAD[:, 10] = 20.0
    G = catchment_grids(Z, TIA, ROAD, 20.0)
    check('plane: column outlet area = H cells', abs(G['area_km2'][H - 1, 10] - H * 400 / 1e6) < 1e-9 or G['area_km2'][H - 1, 10] >= H * 400 / 1e6 - 1e-9)
    check('plane: longest path = (H-1) x 20 m', abs(G['L_m'][H - 1, 10] - (H - 1) * 20) < 1e-6)
    check('plane: head elevation = top row', abs(G['zhead'][H - 1, 10] - Z[0, 10]) < 1e-9)
    check('plane: TIA_up = 0.5, DCIA_up = Sutherland(50 %) = 0.354', abs(G['tia_up'][H - 1, 10] - 0.5) < 1e-9 and abs(G['dcia_up'][H - 1, 10] - 0.1 * 50 ** 1.5 / 100) < 1e-6)
    check('plane: road upstream = column road', abs(G['road_up_m'][H - 1, 10] - 20 * H) < 1e-6)
    # a pit is filled and passes its water on
    Z2 = Z.copy(); Z2[20, 10] -= 5; G2 = catchment_grids(Z2, TIA, ROAD, 20.0)
    check('pit filled: outlet still collects the column', G2['area_km2'][H - 1, 10] >= H * 400 / 1e6 - 1e-9)
    # Kirpich: L 300 m, S 2 %, unpaved -> 0.0195 * 300^0.77 * 0.02^-0.385 = 7.1 min
    T = v2_terms(np.array([0.05]), np.array([300.0]), np.array([106.0]), np.array([100.0]), np.array([0.0]), np.array([0.0]), np.array([500.0]), np.array([0.5]),
                 np.array([[100, 80, 70, 60, 50, 40, 30, 20, 15]], float))
    check(f"Kirpich 300 m at 2 % = {T['tc'][0]:.2f} min (7.1)", abs(T['tc'][0] - 0.0195 * 300 ** 0.77 * 0.02 ** -0.385) < 1e-9 and 7.0 < T["tc"][0] < 7.2)
    check('i(Tc) between i5 and i10', 80 < T['i'][0] < 100)
    check('HEC-22 sag grate 0.0945 m3/s; 5 inlets', abs(Q_SAG - 0.0945) < 5e-4 and abs(T['Qcap1'][0] - 5 * Q_SAG) < 1e-9)
    check('C = 0.2 unpaved', abs(T['C'][0] - 0.2) < 1e-12)
    p = v2_probability(T, np.array([0.0]), np.array([20]), 0.5, 15); pg = v2_probability(T, np.array([2.0]), np.array([20]), 0.5, 15)
    check('gate: HAND > 0.5 -> 0', pg[0] == 0 and p[0] > 0)
    check('IDF clamps below 5 min to i5', abs(interp_idf(np.array([[100, 80, 70, 60, 50, 40, 30, 20, 15]], float), np.array([3.0]))[0] - 100) < 1e-9)
    print('selftest', 'OK' if ok else 'FAILED'); return ok


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0]); ap.add_argument('cmd', nargs='?', choices=('geo', 'rain', 'loso'))
    ap.add_argument('--run'); ap.add_argument('--storm'); ap.add_argument('--out'); ap.add_argument('--boot', type=int, default=2000); ap.add_argument('--selftest', action='store_true')
    a = ap.parse_args()
    if a.selftest: sys.exit(0 if selftest() else 1)
    sys.path.insert(0, HERE)
    {'geo': cmd_geo, 'rain': cmd_rain, 'loso': cmd_loso}[a.cmd](a)


if __name__ == '__main__':
    main()
