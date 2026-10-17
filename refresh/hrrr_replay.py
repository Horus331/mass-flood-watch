"""Forecast replay: how well does the District 3 segment model do when it only has the NOAA HRRR rain FORECAST?

For every test storm day (2018-08 onward, when HRRR runs out to 48 h), rebuild the inputs exactly as the live
refresh does (HRRR runs issued before the day starts, 20 km neighbourhood, 90th percentile; PRISM wetness via ACIS),
score every segment with the published models, and compare with the same models fed the observed rain that was used
in Colab. Scores: mean daily AUC on the segments that really got >= 20 mm (the paper metric), and the share of
recorded floods inside the top 5% of all District 3 segments (what an engineer would see on the live map).
Writes docs/graph_replay_hrrr.json.   Usage: python refresh/hrrr_replay.py [max_days]
"""
import os, sys, json, time, pickle, datetime as dt, requests, numpy as np, pandas as pd
from concurrent.futures import ThreadPoolExecutor
from sklearn.metrics import roc_auc_score
t0 = time.time(); ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); MD = os.path.join(ROOT, 'refresh', 'graph_model'); RP = os.path.join(ROOT, 'refresh', 'replay')
H = {'User-Agent': 'mass-flood-watch (student research)'}
Z = np.load(os.path.join(MD, 'static.npz')); T = pickle.load(open(os.path.join(MD, 'trees.pkl'), 'rb'))
Xs, hist, cell, cell_ll, D = Z['Xs'], Z['hist'], Z['cell'], Z['cell_ll'], Z['D']; nS = len(Xs)
OBS = np.load(os.path.join(RP, 'test_rain_obs.npz'), allow_pickle=True); LAB = json.load(open(os.path.join(RP, 'test_labels.json')))
CDF = pd.read_csv(os.path.join(RP, 'test_days_colab.csv'))
fl = set(CDF[CDF.floods > 0].day); days = [d for d in OBS['days'].tolist() if d >= '2018-08-01' and d in fl]
if len(sys.argv) > 1: days = days[:int(sys.argv[1])]
print(f'{len(days)} test storm days with a recorded flood and 48-h HRRR runs')
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
GEO = None
def geo(g):
    global GEO
    if GEO is None:
        HL, HO = g.latlons(); wh = np.where(((HL > 41.7) & (HL < 43.05) & (HO > -72.7) & (HO < -70.9)).ravel())[0]; hl, ho = HL.ravel()[wh], HO.ravel()[wh]
        GEO = (wh, [np.where(((hl - a) * 111) ** 2 + ((ho - b) * 82) ** 2 <= 20 ** 2)[0] for a, b in cell_ll])
    return GEO
def member(init, win0, win1):
    fhs = [fh for fh in range(1, 49) if win0 < init + pd.Timedelta(hours=fh) <= win1]
    if len(fhs) < 12: return None
    with ThreadPoolExecutor(12) as ex: G = list(ex.map(lambda fh: grab(init, fh), fhs))
    G = [g for g in G if g is not None]
    if len(G) < 12: return None
    wh, NB = geo(G[0]); M = np.array([g.values.ravel()[wh] for g in G], dtype=np.float32)
    cs = np.vstack([np.zeros((1, M.shape[1])), np.cumsum(M, 0)]); roll = lambda w: (cs[w:] - cs[:-w]).max(0)
    Sx = np.c_[M.max(0), roll(3), roll(6), M.sum(0)]
    return np.array([np.percentile(Sx[n], 90, axis=0) if len(n) else [0, 0, 0, 0] for n in NB], np.float32)
lat0, lat1, lon0, lon1 = float(Z['seg_plat'].min()) - 0.1, float(Z['seg_plat'].max()) + 0.1, float(Z['seg_plon'].min()) - 0.1, float(Z['seg_plon'].max()) + 0.1
GI = None
def api_for(day):
    global GI
    d = dt.date.fromisoformat(day); sd = d - dt.timedelta(days=45); ed = d - dt.timedelta(days=1)
    for k in range(3):
        try:
            j = requests.post('https://data.rcc-acis.org/GridData', json=dict(bbox=f'{lon0},{lat0},{lon1},{lat1}', sdate=f'{sd}', edate=f'{ed}', grid='21', elems='pcpn', meta='ll'), headers=H, timeout=180).json()
            P = np.array([r[1] for r in j['data']], np.float32); P[P < 0] = np.nan; P *= 25.4
            if GI is None:
                from scipy.spatial import cKDTree
                glat, glon = np.array(j['meta']['lat']), np.array(j['meta']['lon']); _, GI = cKDTree(np.c_[glat.ravel(), glon.ravel()]).query(np.c_[Z['seg_plat'], Z['seg_plon']])
            A = np.zeros(P[0].size)
            for t in range(len(P)): A = 0.85 * A + np.nan_to_num(P[t].ravel())
            return (A[GI] * 1.484).astype(np.float32)
        except Exception as ex: print('  ACIS retry', repr(ex)[:80]); time.sleep(5)
    return np.zeros(nS, np.float32)
ARI = np.array([1, 2, 5, 10, 25, 50, 100, 200, 500, 1000], float)
def storm_ari(r):
    best = np.zeros(nS, np.float32)
    for k, di in ((0, 0), (2, 1), (3, 2)):
        d = np.maximum(r[:, k], 1e-3); Dk = D[:, di, :]; ld = np.log(Dk); lx = np.log(d)[:, None]
        idx = np.clip((lx > ld).sum(1), 1, 9); lo = np.take_along_axis(ld, (idx - 1)[:, None], 1)[:, 0]; hi = np.take_along_axis(ld, idx[:, None], 1)[:, 0]
        a = np.exp(np.log(ARI)[idx - 1] + np.clip((lx[:, 0] - lo) / np.maximum(hi - lo, 1e-6), -3, 1) * (np.log(ARI)[idx] - np.log(ARI)[idx - 1]))
        a = np.where(d < Dk[:, 0], d / Dk[:, 0], a); best = np.maximum(best, a.astype(np.float32))
    return best
def features(rc, api, month):
    r = rc[cell]; ari = storm_ari(r)
    HF = np.interp(np.log10(np.maximum(ari, 1e-3)), np.log10([1, 2, 5, 10, 25, 50, 100]), [0.25, 0.5, 1, 2, 3, 4, 5], left=0, right=5).astype(np.float32)
    return np.column_stack([Xs, r, np.log1p(r), api, np.log1p(ari), HF, np.full(nS, np.sin(2 * np.pi * month / 12)), np.full(nS, np.cos(2 * np.pi * month / 12)), np.log1p(hist)]).astype(np.float32), r
# graph network (same as the live refresh)
import torch
from scipy import sparse
CK = torch.load(os.path.join(MD, 'gnn.pt'), map_location='cpu', weights_only=False); cfg = CK['cfg']
A_ = sparse.csr_matrix((np.ones(len(Z['adj_r'])), (Z['adj_r'], Z['adj_c'])), shape=(nS, nS)); deg = np.asarray(A_.sum(1)).ravel()
An = (sparse.diags(1 / np.maximum(deg, 1)) @ A_).tocoo(); At = torch.sparse_coo_tensor(np.vstack([An.row, An.col]), An.data.astype(np.float32), (nS, nS)).coalesce()
class SAGE(torch.nn.Module):
    def __init__(s, fin, h=64, L=3, p=0.3):
        super().__init__(); s.inp = torch.nn.Linear(fin, h); s.self_ = torch.nn.ModuleList([torch.nn.Linear(h, h) for _ in range(L)]); s.nb = torch.nn.ModuleList([torch.nn.Linear(h, h) for _ in range(L)])
        s.norm = torch.nn.ModuleList([torch.nn.LayerNorm(h) for _ in range(L)]); s.out = torch.nn.Linear(h, 1); s.p = p
    def forward(s, x):
        h = torch.relu(s.inp(x))
        for a, b, n in zip(s.self_, s.nb, s.norm): h = h + torch.relu(n(a(h) + b(torch.sparse.mm(At, h))))
        return s.out(h).squeeze(-1)
NETS = []
for sd_ in CK['nets']:
    net = SAGE(len(CK['FEATS']), cfg.get('h', 64), cfg.get('L', 3)); net.load_state_dict(sd_); net.eval(); NETS.append(net)
def score(X):
    pt = T['GB'].predict_proba(X)[:, 1]
    with torch.no_grad(): pg = np.mean([torch.sigmoid(n(torch.tensor(np.nan_to_num((X - CK['mu']) / CK['sd']), dtype=torch.float32))).numpy() for n in NETS], 0)
    return pt, pg
rank = lambda v: pd.Series(v).rank(pct=True).values
def metrics(p, y, elig):
    out = {}
    if elig.sum() >= 50 and 0 < y[elig].sum() < elig.sum(): out['auc_wet'] = float(roc_auc_score(y[elig], p[elig]))
    if y.sum():
        thr = np.quantile(p, 0.95); out['top5_all'] = float((p[y] >= thr).mean()) if p.max() > 0 else 0.0
        out['auc_all'] = float(roc_auc_score(y, p)) if 0 < y.sum() < len(y) else None
    return out
oidx = {d: i for i, d in enumerate(OBS['days'].tolist())}
ROWS = []
for n_, day in enumerate(days):
    y = np.zeros(nS, bool); y[LAB[day]] = True
    d0 = pd.Timestamp(day).tz_localize('America/New_York').tz_convert('UTC').tz_localize(None); win0, win1 = d0, d0 + pd.Timedelta(hours=33)   # training window: local midnight + 33 h
    month = pd.Timestamp(day).month; api = api_for(day); CACHE = {}
    ro = OBS['R'][oidx[day]]; Xo, r_o = features(ro, api, month); elig = r_o[:, 3] >= 20
    pto, pgo = score(Xo); po = {'trees': pto, 'gnn': pgo, 'average': 0.5 * rank(pto) + 0.5 * rank(pgo)}
    for k_ in po: po[k_] = np.where(elig, po[k_], 0)
    row = dict(day=day, floods=int(y.sum()), floods_wet=int(y[elig].sum()), obs={k_: metrics(v, y, elig) for k_, v in po.items()})
    for lead, back in (('same_day', 0), ('day_ahead', 12)):          # same_day: runs from 00Z on the day back to 06Z the day before; day_ahead: 12 h earlier
        issue = (win0 - pd.Timedelta(hours=back)).floor('6h')
        if issue > win0 - pd.Timedelta(hours=back): issue -= pd.Timedelta(hours=6)
        inits = [issue - pd.Timedelta(hours=h) for h in (0, 6, 12, 18)]
        todo = [i for i in inits if i not in CACHE]
        with ThreadPoolExecutor(3) as ex: res = list(ex.map(lambda i: member(i, win0, win1), todo))
        CACHE.update(zip(todo, res))
        MEM = [CACHE[i] for i in inits if CACHE[i] is not None]
        if not MEM: row[lead] = None; continue
        PT, PG, RF = [], [], []
        for Mc in MEM:
            Xf, rf = features(Mc, api, month); pt, pg = score(Xf); m_ = rf[:, 3] >= 20; PT.append(np.where(m_, pt, 0)); PG.append(np.where(m_, pg, 0)); RF.append(rf)
        pt, pg = np.mean(PT, 0), np.mean(PG, 0); rf = np.mean(RF, 0)
        pf = {'trees': pt, 'gnn': pg, 'average': 0.5 * pt + 0.5 * pg}
        row[lead] = dict(issue=f'{issue:%Y-%m-%d %H}Z', runs=len(MEM), rain_max_24h_fcst=round(float(rf[:, 3].max()), 1), rain_max_obs=round(float(r_o[:, 3].max()), 1),
                         wet_fcst=int((rf[:, 3] >= 20).sum()), wet_obs=int(elig.sum()), wet_overlap=int(((rf[:, 3] >= 20) & elig).sum()),
                         floods_in_fcst_wet=int(y[rf[:, 3] >= 20].sum()), **{k_: metrics(v, y, elig) for k_, v in pf.items()})
    ROWS.append(row)
    s = row.get('same_day') or {}
    print(f"{n_ + 1:3d}/{len(days)} {day} floods {row['floods']:3d} | obs AUC {row['obs']['average'].get('auc_wet', float('nan')):.3f} | HRRR same-day AUC {s.get('average', {}).get('auc_wet', float('nan')):.3f} "
          f"top5 {s.get('average', {}).get('top5_all', float('nan')):.2f} | rain fcst {s.get('rain_max_24h_fcst', '-')} obs {s.get('rain_max_obs', '-')} mm ({time.time() - t0:.0f}s)", flush=True)
    if (n_ + 1) % 10 == 0 or n_ + 1 == len(days):
        def summ(key, model, m):
            v = [r[key][model].get(m) for r in ROWS if r.get(key) and r[key].get(model, {}).get(m) is not None] if key != 'obs' else [r['obs'][model].get(m) for r in ROWS if r['obs'][model].get(m) is not None]
            return dict(mean=round(float(np.mean(v)), 3), n=len(v)) if v else None
        SUM = {key: {mo: {m: summ(key, mo, m) for m in ('auc_wet', 'top5_all', 'auc_all')} for mo in ('trees', 'gnn', 'average')} for key in ('obs', 'same_day', 'day_ahead')}
        caught = lambda key: int(sum(r[key]['floods_in_fcst_wet'] for r in ROWS if r.get(key))); tot = int(sum(r['floods'] for r in ROWS if r.get('same_day')))
        OUT = dict(built=time.strftime('%Y-%m-%d %H:%M UTC', time.gmtime()), days=len(ROWS), summary=SUM,
                   floods_total=tot, floods_where_hrrr_forecast_20mm=dict(same_day=caught('same_day'), day_ahead=caught('day_ahead')), rows=ROWS,
                   colab_check=dict(mean_auc_trees=round(float(CDF[CDF.day.isin(days)].auc_ML.mean()), 3), mean_auc_gnn=round(float(CDF[CDF.day.isin(days)].auc_GNN.mean()), 3)),
                   note='auc_wet: mean daily AUC over segments that observed >= 20 mm (paper metric). top5_all: share of recorded floods inside the day\'s top 5% of all District 3 segments. same_day: 4 HRRR runs, the latest issued at or before local midnight; day_ahead: 12 h earlier.')
        json.dump(OUT, open(os.path.join(ROOT, 'docs', 'graph_replay_hrrr.json'), 'w'), separators=(',', ':'))
        print('SUMMARY', json.dumps(SUM))
print(f'done in {time.time() - t0:.0f}s')
