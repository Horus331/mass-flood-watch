"""District 3 segment graph: live flood chance for every road segment (next 24 h).

Inputs (all free): NOAA HRRR rain forecast (AWS open data, 4 time-lagged runs), PRISM daily rain via ACIS for
ground wetness, NOAA Atlas 14 storm rarity. Model: the segment model trained in Colab (Graph step 2).
Writes docs/graph_live.json. Run by GitHub Actions every 6 hours.
"""
import os, json, time, pickle, datetime as dt, requests, numpy as np, pandas as pd
from concurrent.futures import ThreadPoolExecutor
t0 = time.time(); ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); MD = os.path.join(ROOT, 'refresh', 'graph_model')
H = {'User-Agent': 'mass-flood-watch (student research)'}
Z = np.load(os.path.join(MD, 'static.npz')); T = pickle.load(open(os.path.join(MD, 'trees.pkl'), 'rb')); VER = json.load(open(os.path.join(MD, 'versions.json')))
Xs, hist, cell, cell_ll, D = Z['Xs'], Z['hist'], Z['cell'], Z['cell_ll'], Z['D']; nS = len(Xs)
# ---------------- 1. HRRR rain forecast: 4 time-lagged runs, 20 km neighbourhood, 90th percentile per rain cell ----------------
import pygrib
HB = 'https://noaa-hrrr-bdp-pds.s3.amazonaws.com'
def grab(init, fh):
    u = f'{HB}/hrrr.{init:%Y%m%d}/conus/hrrr.t{init:%H}z.wrfsfcf{fh:02d}.grib2'
    for k in range(3):
        try:
            idx = requests.get(u + '.idx', timeout=60)
            if idx.status_code != 200: return None
            lines = idx.text.strip().split('\n'); tag = f':APCP:surface:{fh - 1}-{fh} hour acc'
            for i, ln in enumerate(lines):
                if tag in ln:
                    st = int(ln.split(':')[1]); en = int(lines[i + 1].split(':')[1]) - 1 if i + 1 < len(lines) else ''
                    return pygrib.fromstring(requests.get(u, headers={'Range': f'bytes={st}-{en}'}, timeout=120).content)
            return None
        except Exception: time.sleep(3 + 3 * k)
    return None
now = pd.Timestamp.now(tz='UTC').tz_localize(None).floor('h')
def latest_synoptic():
    for h in range(0, 30):
        t = now - pd.Timedelta(hours=h)
        if t.hour % 6 == 0 and requests.head(f'{HB}/hrrr.{t:%Y%m%d}/conus/hrrr.t{t:%H}z.wrfsfcf48.grib2.idx', timeout=30).status_code == 200: return t
issue = latest_synoptic(); inits = [issue - pd.Timedelta(hours=h) for h in (0, 6, 12, 18)]
win0, win1 = now, now + pd.Timedelta(hours=24)                       # scored window: the next 24 hours
g0 = grab(issue, 1); HL, HO = g0.latlons(); wh = np.where(((HL > 41.7) & (HL < 43.05) & (HO > -72.7) & (HO < -70.9)).ravel())[0]; hl, ho = HL.ravel()[wh], HO.ravel()[wh]
NB = [np.where(((hl - a) * 111) ** 2 + ((ho - b) * 82) ** 2 <= 20 ** 2)[0] for a, b in cell_ll]
def member(init):
    fhs = [fh for fh in range(1, 49) if win0 < init + pd.Timedelta(hours=fh) <= win1]
    with ThreadPoolExecutor(8) as ex: G = list(ex.map(lambda fh: grab(init, fh), fhs))
    M = np.array([g.values.ravel()[wh] for g in G if g is not None], dtype=np.float32)
    if len(M) < 12: return None
    cs = np.vstack([np.zeros((1, M.shape[1])), np.cumsum(M, 0)]); roll = lambda w: (cs[w:] - cs[:-w]).max(0)
    Sx = np.c_[M.max(0), roll(3), roll(6), M.sum(0)]
    return np.array([np.percentile(Sx[n], 90, axis=0) if len(n) else [0, 0, 0, 0] for n in NB], np.float32)   # rain cells x (1h, 3h, 6h, 24h total)
MEM = [m for m in (member(i) for i in inits) if m is not None]
print(f'HRRR runs used: {len(MEM)}/4 (latest {issue:%Y-%m-%d %H}Z) | window {win0:%m-%d %H}Z–{win1:%m-%d %H}Z | heaviest 1-h rain {max(m[:, 0].max() for m in MEM):.1f} mm ({time.time() - t0:.0f}s)')
# ---------------- 2. ground wetness: antecedent index from PRISM daily rain (ACIS), k = 0.85, as in training ----------------
lat0, lat1, lon0, lon1 = float(Z['seg_plat'].min()) - 0.1, float(Z['seg_plat'].max()) + 0.1, float(Z['seg_plon'].min()) - 0.1, float(Z['seg_plon'].max()) + 0.1
api = np.zeros(nS, np.float32); api_note = 'unavailable (0 used)'
try:
    ed = dt.date.today(); sd = ed - dt.timedelta(days=45)
    j = requests.post('https://data.rcc-acis.org/GridData', json=dict(bbox=f'{lon0},{lat0},{lon1},{lat1}', sdate=f'{sd}', edate=f'{ed}', grid='21', elems='pcpn', meta='ll'), headers=H, timeout=180).json()
    days = [r[0] for r in j['data']]; P = np.array([r[1] for r in j['data']], np.float32); P[P < 0] = np.nan; P *= 25.4
    glat, glon = np.array(j['meta']['lat']), np.array(j['meta']['lon'])
    from scipy.spatial import cKDTree
    _, gi = cKDTree(np.c_[glat.ravel(), glon.ravel()]).query(np.c_[Z['seg_plat'], Z['seg_plon']])
    last = max(i for i in range(len(days)) if np.isfinite(P[i]).mean() > 0.5)
    A = np.zeros(glat.size)
    for t in range(last + 1): A = 0.85 * A + np.nan_to_num(P[t].ravel())          # index for the day after the last PRISM day
    api = (A[gi] * 1.484).astype(np.float32); api_note = f'PRISM through {days[last]}'   # x1.484: matches the stored training index (checked in Colab: correlation 0.98)
except Exception as ex: print('ACIS:', repr(ex)[:120])
# ---------------- 3. features exactly as in training, then the model ----------------
ARI = np.array([1, 2, 5, 10, 25, 50, 100, 200, 500, 1000], float)
def storm_ari(r):                                                    # r: segments x 4 (1h, 3h, 6h, total)
    best = np.zeros(nS, np.float32)
    for k, di in ((0, 0), (2, 1), (3, 2)):
        d = np.maximum(r[:, k], 1e-3); Dk = D[:, di, :]; ld = np.log(Dk); lx = np.log(d)[:, None]
        idx = np.clip((lx > ld).sum(1), 1, 9); lo = np.take_along_axis(ld, (idx - 1)[:, None], 1)[:, 0]; hi = np.take_along_axis(ld, idx[:, None], 1)[:, 0]
        a = np.exp(np.log(ARI)[idx - 1] + np.clip((lx[:, 0] - lo) / np.maximum(hi - lo, 1e-6), -3, 1) * (np.log(ARI)[idx] - np.log(ARI)[idx - 1]))
        a = np.where(d < Dk[:, 0], d / Dk[:, 0], a); best = np.maximum(best, a.astype(np.float32))
    return best
m = now.month; probs = []; XS = []
for Mc in MEM:
    r = Mc[cell]; ari = storm_ari(r)
    HF = np.interp(np.log10(np.maximum(ari, 1e-3)), np.log10([1, 2, 5, 10, 25, 50, 100]), [0.25, 0.5, 1, 2, 3, 4, 5], left=0, right=5).astype(np.float32)
    X = np.column_stack([Xs, r, np.log1p(r), api, np.log1p(ari), HF, np.full(nS, np.sin(2 * np.pi * m / 12)), np.full(nS, np.cos(2 * np.pi * m / 12)), np.log1p(hist)]).astype(np.float32)
    p = T['GB'].predict_proba(X)[:, 1]; p[r[:, 3] < 20] = 0.0            # as in training: only segments with >= 20 mm are scored
    probs.append(p); XS.append((X, p.copy()))
p = np.mean(probs, 0) if probs else np.zeros(nS)
MODEL_NAME = 'segment-only ML (boosted trees)'
# graph neural network (used when it won the comparison): same features, messages passed between connected segments
if 'graph' in VER.get('best', '') and os.path.exists(os.path.join(MD, 'gnn.pt')) and probs:
    try:
        import torch
        from scipy import sparse
        CK = torch.load(os.path.join(MD, 'gnn.pt'), map_location='cpu', weights_only=False); cfg = CK['cfg']
        A = sparse.csr_matrix((np.ones(len(Z['adj_r'])), (Z['adj_r'], Z['adj_c'])), shape=(nS, nS)); deg = np.asarray(A.sum(1)).ravel()
        An = (sparse.diags(1 / np.maximum(deg, 1)) @ A).tocoo(); At = torch.sparse_coo_tensor(np.vstack([An.row, An.col]), An.data.astype(np.float32), (nS, nS)).coalesce()
        class SAGE(torch.nn.Module):
            def __init__(s, fin, h=64, L=3, p=0.3):
                super().__init__(); s.inp = torch.nn.Linear(fin, h); s.self_ = torch.nn.ModuleList([torch.nn.Linear(h, h) for _ in range(L)]); s.nb = torch.nn.ModuleList([torch.nn.Linear(h, h) for _ in range(L)])
                s.norm = torch.nn.ModuleList([torch.nn.LayerNorm(h) for _ in range(L)]); s.out = torch.nn.Linear(h, 1); s.p = p
            def forward(s, x):
                h = torch.relu(s.inp(x))
                for a, b, n in zip(s.self_, s.nb, s.norm): h = h + torch.relu(n(a(h) + b(torch.sparse.mm(At, h))))
                return s.out(h).squeeze(-1)
        use2 = 'top of trees' in VER['best'] and CK.get('nets2')
        nets = []
        for sd_ in (CK['nets2'] if use2 else CK['nets']):
            net = SAGE(len(CK['FEATS']) + (1 if use2 else 0), cfg.get('h', 64), cfg.get('L', 3)); net.load_state_dict(sd_); net.eval(); nets.append(net)
        gp = []
        for X, pt in XS:
            Xn = np.nan_to_num((X - CK['mu']) / CK['sd'])
            if use2:
                lg = np.log(np.clip(pt, 1e-6, 1 - 1e-6)) - np.log1p(-np.clip(pt, 1e-6, 1 - 1e-6)); lg = (lg - CK['lg_mu']) / CK['lg_sd']; Xn = np.column_stack([Xn, lg])
            with torch.no_grad(): q_ = np.mean([torch.sigmoid(n(torch.tensor(Xn, dtype=torch.float32))).numpy() for n in nets], 0)
            q_[X[:, len(Xs[0]) + 3] < 20] = 0.0; gp.append(q_)
        pg = np.mean(gp, 0)
        if 'average' in VER['best']: p = 0.5 * p + 0.5 * pg; MODEL_NAME = 'average of trees and graph neural network'
        else: p = pg; MODEL_NAME = VER['best']
    except Exception as ex: print('GNN scoring failed, trees used:', repr(ex)[:160])
CALP = os.path.join(MD, 'calibration.json'); calibrated = False
if os.path.exists(CALP) and 'average' in MODEL_NAME:                 # isotonic map fitted on the test storms (Colab, Graph step 4b)
    CAL = json.load(open(CALP)); raw = p.copy(); p = np.where(p > 0, np.interp(p, CAL['x'], CAL['y']), 0.0); calibrated = True
q = np.round(np.clip(p, 0, 1) * (1e5 if calibrated else 1000)).astype(int)            # calibrated: per 100,000
top = np.argsort(-(p + 1e-9 * (raw if calibrated else p)))[:25]          # ties on the calibrated steps broken by the raw score
out = dict(asof=pd.Timestamp.now(tz='America/New_York').strftime('%Y-%m-%d %H:%M ET'), hrrr_latest=f'{issue:%Y-%m-%d %H}Z', runs=len(probs),
           window=[f'{win0:%Y-%m-%dT%H}Z', f'{win1:%Y-%m-%dT%H}Z'], wetness=api_note, model=MODEL_NAME,
           max_rain_1h_mm=round(float(max(m_[:, 0].max() for m_ in MEM)) if MEM else 0, 1), max_rain_24h_mm=round(float(max(m_[:, 3].max() for m_ in MEM)) if MEM else 0, 1),
           n_scored=int((p > 0).sum()), calibrated=calibrated, expected_reports=round(float(p.sum()), 2),
           rank100=np.where(p > 0, np.ceil(pd.Series(np.where(p > 0, p + 1e-9 * (raw if calibrated else p), np.nan)).rank(pct=True).fillna(0).values * 99), 0).astype(int).tolist(), p1000=q.tolist(), scale=(100000 if calibrated else 1000), top=[[int(i), int(q[i])] for i in top if q[i] > 0])
json.dump(out, open(os.path.join(ROOT, 'docs', 'graph_live.json'), 'w'), separators=(',', ':'))
print(f'graph live: {out["n_scored"]:,} segments with >= 20 mm forecast | top chance {p.max():.1%} | {time.time() - t0:.0f}s')
