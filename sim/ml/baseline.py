"""Gradient-boosting baseline for the flood-depth surrogate, evaluated with the two pre-registered splits (docs/validation/protocol.md).

    python baseline.py --dataset ml/ds_v3 --out ml/ds_v3/baseline            (LightGBM when installed, else sklearn HistGradientBoosting; CPU is fine)
    python baseline.py --selftest                                            (synthetic dataset from dataset.py -> trains -> checks the report)
    ML_DATASET=ml/datasets/v3_30m HF_TOKEN=... python baseline.py           (queue step "baseline": shards from Hugging Face, report uploaded next to them)

Models (one set per held-out fold):  P(wet) classifier (hmax >= 10 cm), depth regressor on log1p(hmax) fitted on wet cells, arrival-time
and duration regressors (hours) fitted on wet cells.  Predicted depth = 0 where P(wet) < 0.5.
Splits:  `loso`  leave-one-storm-out (group = storm; every parameter variant and sub-box of the storm is held out together);
         `huc10` spatial block CV (group = fold, a hash of the HUC10 id; `block_src` in the manifest says whether real HUC10 ids were used).
Metrics (out-of-fold, pooled and per fold):  wet hit rate / precision / F1 / CSI at P >= 0.5, PR-AUC, Brier and Brier skill vs climatology;
CSI/F1 at 10 / 30 / 50 cm of predicted vs modelled depth; depth MAE and share within 50 cm on modelled-wet cells; arrival-time and duration MAE
on cells wet in both.  Rate metrics are reported twice: unweighted on the sampled rows and weighted by the dataset's `weight` (inverse
sampling probability -> population-equivalent, the number a map user would see).  Reliability diagram data for P(wet) (10 equal-width bins,
weighted and unweighted counts, bins with < 50 positives flagged as the protocol asks) are written as reliability_<split>.csv.
Writes <out>/report.json, reliability_<split>.csv, importance.csv.
"""
import os, sys, json, time, argparse, tempfile
import numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import dataset as DS
log = lambda *a: print(time.strftime('%H:%M:%S'), *a, flush=True)
WET_M = DS.WET_M; DEPTH_TH = (0.10, 0.30, 0.50); WITHIN_M = 0.50; REL_BINS = 10; MIN_POS = 50

# ---------------------------------------------------------------- models (LightGBM if available, else sklearn) ----
try:
    import lightgbm as lgb; BACKEND = 'lightgbm'
except ImportError:
    lgb = None; BACKEND = 'sklearn'

def fit_cls(X, y, w, n_iter, seed):
    if lgb is not None:
        m = lgb.LGBMClassifier(n_estimators=n_iter, learning_rate=0.05, num_leaves=63, subsample=0.8, subsample_freq=1, colsample_bytree=0.8, min_child_samples=50, random_state=seed, verbose=-1)
        m.fit(X, y, sample_weight=w); return lambda Xq: m.predict_proba(Xq)[:, 1], m
    from sklearn.ensemble import HistGradientBoostingClassifier
    m = HistGradientBoostingClassifier(max_iter=n_iter, learning_rate=0.08, max_leaf_nodes=63, min_samples_leaf=50, random_state=seed); m.fit(X, y, sample_weight=w)
    return lambda Xq: m.predict_proba(Xq)[:, 1], m

def fit_reg(X, y, n_iter, seed):
    if lgb is not None:
        m = lgb.LGBMRegressor(objective='huber', n_estimators=n_iter, learning_rate=0.05, num_leaves=63, subsample=0.8, subsample_freq=1, colsample_bytree=0.8, min_child_samples=50, random_state=seed, verbose=-1)
        m.fit(X, y); return m.predict
    from sklearn.ensemble import HistGradientBoostingRegressor
    m = HistGradientBoostingRegressor(loss='absolute_error', max_iter=n_iter, learning_rate=0.08, max_leaf_nodes=63, min_samples_leaf=50, random_state=seed); m.fit(X, y); return m.predict

def importance(model, cols):
    imp = getattr(model, 'feature_importances_', None)
    if imp is None: return None
    return pd.Series(imp, index=cols).sort_values(ascending=False)

# ---------------------------------------------------------------- metrics ----
def rates(obs, pred, w):
    """Hit rate (recall), precision, F1 and CSI of a boolean forecast, weighted by w."""
    hit = float(w[obs & pred].sum()); miss = float(w[obs & ~pred].sum()); fa = float(w[~obs & pred].sum())
    return dict(hit_rate=hit / max(hit + miss, 1e-9), precision=hit / max(hit + fa, 1e-9), f1=2 * hit / max(2 * hit + miss + fa, 1e-9), csi=hit / max(hit + miss + fa, 1e-9), n_obs=hit + miss, n_pred=hit + fa)

def pr_auc(y, p, w):
    """Area under the precision-recall curve (average precision), weighted; sklearn when present, else a direct computation."""
    try:
        from sklearn.metrics import average_precision_score; return float(average_precision_score(y, p, sample_weight=w))
    except Exception:
        o = np.argsort(-p); y = y[o].astype(float); w = w[o]; tp = np.cumsum(w * y); fp = np.cumsum(w * (1 - y)); prec = tp / np.maximum(tp + fp, 1e-9); rec = tp / max(tp[-1], 1e-9)
        return float(np.sum(np.diff(np.r_[0, rec]) * prec))

def reliability(y, p, w):
    """Reliability diagram rows for P(wet): per equal-width bin the count, positives, mean forecast and observed frequency (weighted too)."""
    b = np.clip((p * REL_BINS).astype(int), 0, REL_BINS - 1); rows = []
    for k in range(REL_BINS):
        m = b == k; n = int(m.sum()); npos = int(y[m].sum()); wn = float(w[m].sum()); wpos = float(w[m & (y == 1)].sum())
        rows.append(dict(bin=k, p_lo=k / REL_BINS, p_hi=(k + 1) / REL_BINS, n=n, n_pos=npos, mean_p=float(p[m].mean()) if n else np.nan, obs_freq=npos / n if n else np.nan,
                         w_n=wn, w_pos=wpos, w_mean_p=float(np.average(p[m], weights=w[m])) if n else np.nan, w_obs_freq=wpos / wn if wn > 0 else np.nan, enough=npos >= MIN_POS))
    return pd.DataFrame(rows)

def score(df, P, H, T, D):
    """All metrics for one set of out-of-fold predictions; keys with the 'w_' prefix are weighted by df.weight."""
    y = df['wet'].values.astype(bool); w = df['weight'].values.astype(float); one = np.ones_like(w); out = dict(n=int(len(df)), n_wet=int(y.sum()), wet_frac=float(y.mean()), w_wet_frac=float(w[y].sum() / w.sum()))
    pw = P >= 0.5
    for pre, ww in (('', one), ('w_', w)):
        r = rates(y, pw, ww); out.update({pre + k: v for k, v in r.items() if k in ('hit_rate', 'precision', 'f1', 'csi')})
        clim = float(np.average(y, weights=ww)); brier = float(np.average((P - y) ** 2, weights=ww)); out[pre + 'pr_auc'] = pr_auc(y.astype(int), P, ww)
        out[pre + 'brier'] = brier; out[pre + 'brier_skill'] = 1 - brier / max(clim * (1 - clim), 1e-9)
        for th in DEPTH_TH: out[f'{pre}csi_{int(th * 100)}cm'] = rates(df['hmax'].values >= th, H >= th, ww)['csi']; out[f'{pre}f1_{int(th * 100)}cm'] = rates(df['hmax'].values >= th, H >= th, ww)['f1']
    err = np.abs(H[y] - df['hmax'].values[y]); out['depth_mae_wet_m'] = float(err.mean()) if y.any() else np.nan; out['depth_within50_wet'] = float((err <= WITHIN_M).mean()) if y.any() else np.nan
    both = y & pw; out['n_both_wet'] = int(both.sum())
    out['t_first_mae_h'] = float(np.nanmean(np.abs(T[both] - df['t_first_h'].values[both]))) if both.any() else np.nan
    out['dur_mae_h'] = float(np.nanmean(np.abs(D[both] - df['dur_h'].values[both]))) if both.any() else np.nan
    out['depth_mae_all_m'] = float(np.average(np.abs(H - df['hmax'].values), weights=w))                      # population-weighted, dry cells included (pred 0 where P < 0.5)
    return out

# ---------------------------------------------------------------- cross-validation ----
def crossval(df, feats, group, n_iter, seed, min_group_rows=200):
    """Out-of-fold predictions P(wet), depth, t_first, dur with one model set per held-out group value."""
    P = np.full(len(df), np.nan); H = np.zeros(len(df)); T = np.full(len(df), np.nan); D = np.full(len(df), np.nan); X = df[feats].values.astype(np.float32); per_fold = {}; imps = []
    groups = [g for g in pd.unique(df[group]) if (df[group] == g).sum() >= min_group_rows]
    if len(groups) < 2: log(f'   only {len(groups)} group(s) of {group} with >= {min_group_rows} rows: nothing to hold out'); groups = []
    for g in groups:
        te = (df[group] == g).values; tr = ~te; wet_tr = tr & (df['wet'].values == 1)
        if df['wet'].values[tr].min() == df['wet'].values[tr].max() or wet_tr.sum() < 20: log(f'   skip fold {g}: training wet/dry degenerate'); continue
        pc, mc = fit_cls(X[tr], df['wet'].values[tr], df['weight'].values[tr], n_iter, seed); P[te] = pc(X[te]); imps.append(importance(mc, feats))
        H[te] = np.expm1(fit_reg(X[wet_tr], np.log1p(df['hmax'].values[wet_tr]), n_iter, seed)(X[te])) * (P[te] >= 0.5)
        tf_ok = wet_tr & np.isfinite(df['t_first_h'].values); du_ok = wet_tr & np.isfinite(df['dur_h'].values)      # a cell can peak >= 10 cm between frames and never be wet in a saved frame: no arrival time
        T[te] = fit_reg(X[tf_ok], df['t_first_h'].values[tf_ok], n_iter, seed)(X[te]); D[te] = fit_reg(X[du_ok], df['dur_h'].values[du_ok], n_iter, seed)(X[te])
        per_fold[str(g)] = score(df[te], P[te], H[te], T[te], D[te]); log(f"   {group}={g}: n {te.sum():,}  hit {per_fold[str(g)]['hit_rate']:.2f}  prec {per_fold[str(g)]['precision']:.2f}  PR-AUC {per_fold[str(g)]['pr_auc']:.3f}  depth MAE {per_fold[str(g)]['depth_mae_wet_m']:.2f} m  t_first MAE {per_fold[str(g)]['t_first_mae_h']:.1f} h")
    ok = ~np.isnan(P)
    pooled = score(df[ok], P[ok], H[ok], T[ok], D[ok]) if ok.any() else {}
    rel = reliability(df['wet'].values[ok].astype(int), P[ok], df['weight'].values[ok].astype(float)) if ok.any() else pd.DataFrame()
    imp = pd.concat([i for i in imps if i is not None], axis=1).mean(axis=1).sort_values(ascending=False) if any(i is not None for i in imps) else None
    return dict(pooled=pooled, per_fold=per_fold, folds=[str(g) for g in groups]), rel, imp

def run(args):
    df, man = DS.load_dataset(args.dataset); feats = [f for f in man['features'] if f in df.columns and df[f].notna().any()]
    if args.drop: feats = [f for f in feats if f not in args.drop]
    df = df[df['fold'] >= 0].reset_index(drop=True); log(f"dataset {args.dataset}: {len(df):,} rows, {df.storm.nunique()} storms, {df.run.nunique()} runs, wet {df.wet.mean():.2f}; {len(feats)} features; backend {BACKEND}")
    if args.max_rows and len(df) > args.max_rows: df = df.sample(args.max_rows, random_state=args.seed).reset_index(drop=True); log(f'   subsampled to {len(df):,} rows')
    os.makedirs(args.out, exist_ok=True); report = dict(created=time.strftime('%Y-%m-%dT%H:%MZ', time.gmtime()), dataset=args.dataset, backend=BACKEND, n_iter=args.n_iter, features=feats, rows=int(len(df)), wet_m=WET_M,
                                                       block_src=sorted({r.get('block_src', '?') for r in man['runs']}), splits={})
    for name, group in (('loso', 'storm'), ('huc10', 'fold')):
        if args.splits and name not in args.splits: continue
        log(f'split {name} (group = {group}, {df[group].nunique()} groups)'); res, rel, imp = crossval(df, feats, group, args.n_iter, args.seed); report['splits'][name] = res
        if len(rel): rel.to_csv(os.path.join(args.out, f'reliability_{name}.csv'), index=False)
        if imp is not None: imp.rename('importance').to_csv(os.path.join(args.out, f'importance_{name}.csv'))
        p = res['pooled']
        if p: log(f"   pooled: hit {p['hit_rate']:.2f} (w {p['w_hit_rate']:.2f})  prec {p['precision']:.2f} (w {p['w_precision']:.2f})  CSI10 {p['csi_10cm']:.2f} CSI30 {p['csi_30cm']:.2f} CSI50 {p['csi_50cm']:.2f}  PR-AUC {p['pr_auc']:.3f}  Brier skill {p['brier_skill']:.2f} (w {p['w_brier_skill']:.2f})  depth MAE {p['depth_mae_wet_m']:.2f} m within50 {p['depth_within50_wet']:.2f}  t_first MAE {p['t_first_mae_h']:.1f} h  dur MAE {p['dur_mae_h']:.1f} h")
    json.dump(report, open(os.path.join(args.out, 'report.json'), 'w'), indent=1); log('report ->', os.path.join(args.out, 'report.json'))
    if args.upload and os.environ.get('HF_TOKEN'):
        from huggingface_hub import HfApi
        api = HfApi(token=os.environ['HF_TOKEN'])
        for f in sorted(os.listdir(args.out)): api.upload_file(path_or_fileobj=os.path.join(args.out, f), path_in_repo=f'{args.upload}/{f}', repo_id=DS.REPO, repo_type='dataset', commit_message=f'ml baseline {args.upload}: {f}')
    return report

def fetch_dataset(hf_path, local):
    """Download a dataset's manifest and shards from Hugging Face into `local`."""
    from huggingface_hub import hf_hub_download
    import shutil; os.makedirs(local, exist_ok=True); tok = os.environ.get('HF_TOKEN')
    shutil.copy(hf_hub_download(DS.REPO, f'{hf_path}/manifest.json', repo_type='dataset', token=tok), os.path.join(local, 'manifest.json'))
    for s in json.load(open(os.path.join(local, 'manifest.json')))['shards']: shutil.copy(hf_hub_download(DS.REPO, f"{hf_path}/{s['file']}", repo_type='dataset', token=tok), os.path.join(local, s['file']))
    return local

def selftest():
    root = DS.selftest(); args = parse(['--dataset', f'{root}/ds', '--out', f'{root}/baseline', '--n-iter', '60']); rep = run(args)
    for name in ('loso', 'huc10'):
        p = rep['splits'][name]['pooled']; assert p and p['n'] > 1000, f'{name}: no pooled predictions'
        assert p['pr_auc'] > 0.7 and p['hit_rate'] > 0.5, f"{name}: PR-AUC {p['pr_auc']:.2f} hit {p['hit_rate']:.2f} (the synthetic depths are a smooth function of HAND and rain; the model must find it)"
        assert np.isfinite(p['depth_mae_wet_m']) and np.isfinite(p['t_first_mae_h']) and np.isfinite(p['dur_mae_h']) and 0 <= p['w_csi_30cm'] <= 1, f'{name}: metric range'
        rel = pd.read_csv(os.path.join(args.out, f'reliability_{name}.csv')); assert len(rel) == REL_BINS and rel['n'].sum() == p['n'] and {'enough', 'w_obs_freq'} <= set(rel.columns), f'{name}: reliability dump'
    assert len(rep['splits']['loso']['folds']) == 3, 'loso must hold out each of the 3 synthetic storms (variants together)'
    assert os.path.exists(os.path.join(args.out, 'report.json')); log('selftest OK (backend', BACKEND + ')')

def parse(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--dataset', default=None, help='directory with manifest.json + shards (from dataset.py)'); ap.add_argument('--out', default=None)
    ap.add_argument('--n-iter', type=int, default=400); ap.add_argument('--seed', type=int, default=0); ap.add_argument('--max-rows', type=int, default=0, help='subsample rows for a quick look (0 = all)')
    ap.add_argument('--splits', nargs='*', default=None, choices=['loso', 'huc10']); ap.add_argument('--drop', nargs='*', default=None, help='features to leave out (ablation)')
    ap.add_argument('--upload', default=None, help='HF path for report + reliability files'); ap.add_argument('--selftest', action='store_true')
    a = ap.parse_args(argv); a.out = a.out or (os.path.join(a.dataset, 'baseline') if a.dataset else None); return a

if __name__ == '__main__':
    a = parse()
    if a.selftest: selftest(); sys.exit(0)
    if a.dataset is None and (os.environ.get('ML_DATASET') or os.environ.get('ML_OUT')):     # queue step "baseline": shards from HF (ML_DATASET, or the ML_OUT the dataset step wrote), report uploaded next to them
        hfp = os.environ.get('ML_DATASET') or os.environ['ML_OUT']
        a.dataset = fetch_dataset(hfp, f"{os.environ.get('WORK', '/content')}/ml_dataset_dl"); a.out = a.out or f"{os.environ.get('WORK', '/content')}/ml_baseline"; a.upload = a.upload or f'{hfp}/baseline'
        if os.environ.get('N_ITER'): a.n_iter = int(os.environ['N_ITER'])
    if not a.dataset: sys.exit('no dataset given (--dataset DIR or ML_DATASET=...)')
    run(a)
