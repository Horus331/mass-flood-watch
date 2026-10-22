"""Learned, calibrated road-closure model (H-V-C ML core): replaces the fixed 'peak depth 0.30 m = closed' physics prior with a model fitted to
documented closure / damage sites, and scores it honestly (spatial block CV on the training storm, blind test on other storms).

    python proto/closure_ml.py extract --run-dir docs/proto/exp/edge_base/rundir --storm sep2023 \\
        --labels proto/data/labels_sep2023_leominster.csv,proto/data/labels_sep2023_leominster_dpw.csv      # -> docs/proto/ml/features_sep2023.csv
    python proto/closure_ml.py extract --run-dir docs/proto/exp/wo_rundir/rundir --storm aug2021 --labels proto/data/labels_aug2021_worcester.csv
    python proto/closure_ml.py train  --train sep2023 --towns Leominster  # final fit -> proto/ml/closure_lr.json, closure_gbm.txt, prior_platt.json
    python proto/closure_ml.py evaluate --train sep2023 --test aug2021    # -> docs/proto/ml/RESULTS.md + PNGs
    python proto/closure_ml.py map --run-dir RUN_DIR --out docs/proto/<run>  # -> <run>/ml_segments.json for the map (re-runs the prototype, ~1 min)
    python proto/closure_ml.py selftest                                   # offline, synthetic

Target.  A road segment is positive for a storm when a documented site (proto/data/labels_*) matches it with the prototype's strict rule
(a road point within 30 m, prototype.label_segments).  Unreported is not dry: the labels are positive-unlabeled (PU).  Under the usual
'selected completely at random' assumption (Elkan & Noto 2008) a classifier of labeled-vs-unlabeled ranks segments exactly like one of
damaged-vs-not, so ranking metrics (PR-AUC, recall at a fixed flagged share) are the primary scores; probabilities estimate
P(documented | x) and P(damaged | x) ~ P(documented | x) / c, c = mean predicted P over labeled positives (Elkan-Noto e1).

Features (per segment; all from the flood run + static layers, no labels):
  log_depth       ln(0.02 + peak depth on the road, m; second-highest road point, as p_close)            expected +
  log_h15         ln(1 + hours with >= 15 cm on the road)                                                 +
  overtop_m       water surface beside the road (30 m) minus road crest, m, clipped [-2, 2] (-freeboard)  +
  log_speed       ln(1 + peak flow speed on the road where >= 5 cm deep, m/s, capped 5)                   +
  p_culvert       P(HDS-5 headwater of a surveyed culvert within 30 m > road crest)                        +
  p_edge          P(edge / shoulder washout by fast shallow runoff beside the road)                        +
  log_area        log10 upstream contributing area (km2, D8 on the model ground, 3x3 max at road points)   +
  hand_m          height of the road above the nearest stream / water cell (m, Euclidean-nearest, <= 20)   -
  slope_pct       median terrain slope at the road points (%, lidar z_raw)                                 (free)
  local_road      1 for local streets                                                                     (free)
  peak1h_mm       worst-hour rain on the segment (MRMS)                                                    +   (comparison only, not in MAIN)
The logistic model drops a feature whose fitted sign contradicts its expected sign (monotone, interpretable); LightGBM gets the same signs
as monotone constraints.

Training domain.  Leominster city only (TRAIN_TOWNS): its DPW damage inventory makes unlabeled segments there close to undamaged; outside it
the Sept 2023 labels are sparse news / NWS reports, so 'unlabeled' mostly means 'unreported' and the reporting footprint (which follows the
rain core) would be learned instead of the hazard.

Optional hook: prototype.run with PROTO_ML=1 calls on_rows() and adds p_close_ml (calibrated logistic) to every segment row.  Defaults unchanged.
"""
import argparse
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
ML_DIR = os.path.join(HERE, 'ml')
OUT_DIR = os.path.join(ROOT, 'docs', 'proto', 'ml')
FEATURES = ['log_depth', 'log_h15', 'overtop_m', 'log_speed', 'p_culvert', 'p_edge', 'log_area', 'hand_m', 'slope_pct', 'local_road', 'peak1h_mm']
MAIN = [f for f in FEATURES if f != 'peak1h_mm']      # main model: hazard + terrain; rain acts through the flood model (see RESULTS.md)
TRAIN_TOWNS = ('Leominster',)   # training domain: where the city DPW damage inventory makes 'unlabeled' close to 'not damaged'
SIGN = dict(log_depth=1, log_h15=1, overtop_m=1, log_speed=1, p_culvert=1, p_edge=1, log_area=1, hand_m=-1, slope_pct=0, local_road=0, peak1h_mm=1)
STREAM_KM2 = 0.5          # channel initiation for HAND / distance to stream
BLOCK_M = 2000.0          # spatial CV blocks (2 km inside the training city; 4 km for whole-box runs)
FLAGS = (0.02, 0.05, 0.10)
ROW_KEYS = ['segment', 'road', 'town', 'road_class', 'length_m', 'aadt', 'p_close', 'peak_depth_m', 'hours_over_30cm', 'hours_over_15cm', 'arrival_h',
            'storm_total_mm', 'peak1h_mm', 'flashness_pct', 'p_depth', 'p_culvert', 'p_overtop', 'p_may_close', 'p_sag', 'p_edge', 'edge_speed_ms',
            'p_freeboard', 'freeboard_m', 'p_fastwater', 'p_dv', 'p_washout', 'peak_speed_ms', 'dv_m2s']
CAPTURE = None            # extract() sets a dict here; on_rows() fills it


# ---------------------------------------------------------------- geometry features
def flow_acc(z):
    """D8 flow accumulation (cells, incl. itself) on grid z; pits keep their water (no filling: the model ground is channel-burned)."""
    z = np.nan_to_num(np.asarray(z, np.float64), nan=1e9); H, W = z.shape; zp = np.pad(z, 1, constant_values=np.inf)
    best = np.zeros((H, W)); rec = np.full((H, W), -1, np.int64); rr, cc = np.mgrid[0:H, 0:W]
    for dr in (-1, 0, 1):
        for dc in (-1, 0, 1):
            if dr == 0 and dc == 0: continue
            drop = (z - zp[1 + dr:1 + dr + H, 1 + dc:1 + dc + W]) / (math.sqrt(2.0) if dr and dc else 1.0)
            b = drop > best; best = np.where(b, drop, best); rec = np.where(b, (rr + dr) * W + (cc + dc), rec)
    acc = np.ones(H * W); recf = rec.ravel().tolist(); a = acc.tolist()
    for i in np.argsort(-z.ravel(), kind='stable').tolist():
        j = recf[i]
        if j >= 0: a[j] += a[i]
    return np.asarray(a).reshape(H, W)


def geo_features(run_dir, Q, n, res):
    """Per-segment upstream area, HAND, distance to stream, slope, from the run dir grids and the road points Q (r, c, seg)."""
    from scipy.ndimage import maximum_filter
    from scipy.spatial import cKDTree
    Z = np.load(os.path.join(run_dir, 'z.npy')).astype(np.float64)
    zr = os.path.join(run_dir, 'z_raw.npz'); ZR = np.load(zr)['z_raw'].astype(np.float64) if os.path.exists(zr) else Z
    wm = os.path.join(run_dir, 'watermask.npy'); WM = np.load(wm).astype(bool) if os.path.exists(wm) else np.zeros(Z.shape, bool)
    A = flow_acc(Z) * res * res / 1e6; A3 = maximum_filter(A, 3)
    st = (A >= STREAM_KM2) | WM; sr, sc = np.nonzero(st)
    r, c, seg = Q['r'], Q['c'], Q['seg']
    d, k = cKDTree(np.column_stack([sr, sc])).query(np.column_stack([r, c]))
    hand = np.clip(np.nan_to_num(ZR[r, c] - Z[sr[k], sc[k]], nan=20.0), 0, 20)
    gy, gx = np.gradient(np.nan_to_num(ZR), res); slope = 100 * np.hypot(gx, gy)[r, c]
    out = dict(area_km2=np.zeros(n), hand_m=np.full(n, 20.0), stream_dist_m=np.full(n, 5000.0), slope_pct=np.zeros(n), cx=np.full(n, np.nan), cy=np.full(n, np.nan))
    for s in np.unique(seg):
        m = seg == s
        out['area_km2'][s] = A3[r[m], c[m]].max(); out['hand_m'][s] = hand[m].min(); out['stream_dist_m'][s] = d[m].min() * res
        out['slope_pct'][s] = np.median(slope[m]); out['cx'][s] = Q['x'][m].mean(); out['cy'][s] = Q['y'][m].mean()
    return out


def design(rows):
    """rows: list of dicts (or a dict of arrays) with the ROW_KEYS + geo columns -> X (n, len(FEATURES))."""
    def col(k, fill=np.nan):
        v = np.array([np.nan if (r.get(k) is None or r.get(k) == '') else float(r[k]) for r in rows], float) if isinstance(rows, list) else np.asarray(rows[k], float)
        return np.where(np.isfinite(v), v, fill)
    cls = [r.get('road_class') for r in rows] if isinstance(rows, list) else list(rows['road_class'])
    X = np.column_stack([
        np.log(0.02 + np.clip(col('peak_depth_m', 0), 0, 3)),
        np.log1p(np.clip(col('hours_over_15cm', 0), 0, 48)),
        np.clip(-col('freeboard_m', 2.0), -2, 2),
        np.log1p(np.clip(col('peak_speed_ms', 0), 0, 5)),
        col('p_culvert', 0), col('p_edge', 0),
        np.log10(np.clip(col('area_km2', 0.0004), 0.0004, 1e4)),
        np.clip(col('hand_m', 20), 0, 20), np.clip(col('slope_pct', 0), 0, 40),
        np.array([1.0 if str(c_).startswith('local') else 0.0 for c_ in cls]), col('peak1h_mm', 0)])
    return X


def prior(rows):
    """The physics prior p_close = Phi((peak depth - 0.30) / 0.10), recomputed unrounded (rounded p_close ties at 0 / 1)."""
    from scipy.stats import norm
    d = np.array([float(r['peak_depth_m']) if isinstance(rows, list) else 0 for r in rows], float) if isinstance(rows, list) else np.asarray(rows['peak_depth_m'], float)
    return norm.cdf((d - 0.30) / 0.10)


# ---------------------------------------------------------------- prototype hook
def on_rows(rows, run_dir, Q, meta, props):
    """Called by prototype.run (PROTO_ML=1) once the segment rows exist: adds p_close_ml; stores everything for extract()."""
    n = len(props['road']); G = geo_features(run_dir, Q, n, float(meta['res_m']))
    for r in rows:
        s = r['segment']
        for k in ('area_km2', 'hand_m', 'stream_dist_m', 'slope_pct', 'cx', 'cy'): r[k] = round(float(G[k][s]), 3)
    lr = os.path.join(ML_DIR, 'closure_lr.json')
    if os.path.exists(lr) and rows:
        p = LR.load(lr).predict(design(rows))
        for r, v in zip(rows, p): r['p_close_ml'] = round(float(v), 4)
    for r in rows:                               # geo columns are model inputs only; keep the map's segment properties as they were
        for k in ('area_km2', 'hand_m', 'stream_dist_m', 'slope_pct', 'cx', 'cy'):
            if CAPTURE is not None: r.setdefault('_geo', {})[k] = r[k]
            r.pop(k)
    if CAPTURE is not None: CAPTURE.update(rows=rows, Q=Q, meta=meta, props=props)


def extract(run_dir, storm, labels, out_dir=OUT_DIR, tmp=None):
    """Run the prototype on run_dir (PROTO_ML=1), keep every in-box segment's row + geo features, and match the label files (strict 30 m)."""
    global CAPTURE
    import csv
    import tempfile
    sys.path.insert(0, HERE); sys.modules.setdefault('closure_ml', sys.modules[__name__]); import prototype as PT
    CAPTURE = {}; os.environ['PROTO_ML'] = '1'
    try:
        PT.run(run_dir, tmp or tempfile.mkdtemp(prefix='mlx_'), os.path.join(ROOT, 'docs', 'graph_segments.json'),
               os.path.join(ROOT, 'docs', 'network', 'crossings_all.json'), os.path.join(ROOT, 'docs', 'prone', 'flood_reports.json'),
               os.path.join(ROOT, 'docs', 'network', 'facilities.json'), None, 30, False, labels[0] if labels else None)
    finally:
        os.environ.pop('PROTO_ML', None)
    C = CAPTURE; CAPTURE = None; rows = C['rows']
    y = {r['segment']: 0 for r in rows}; src = {r['segment']: '' for r in rows}; matches = {}
    for path in labels:
        L = PT.load_line_labels(path) if path.endswith('.geojson') else PT.load_labels(path)
        M = PT.label_segments_lines(L, C['Q'], C['meta'], 30.0) if path.endswith('.geojson') else PT.label_segments(L, C['Q'], C['props'], C['meta'], strict=True)
        for lab, segs in M:
            segs = [int(s) for s in segs if int(s) in y]
            if not segs: continue
            matches[f"{os.path.basename(path)}:{lab.get('id')}"] = dict(type=lab.get('type'), segs=segs)
            for s in segs: y[s] = 1; src[s] = (src[s] + ' ' + str(lab.get('id'))).strip()
    os.makedirs(out_dir, exist_ok=True); cols = ROW_KEYS + ['area_km2', 'hand_m', 'stream_dist_m', 'slope_pct', 'cx', 'cy', 'y', 'label_ids']
    fn = os.path.join(out_dir, f'features_{storm}.csv')
    with open(fn, 'w', newline='') as f:
        w = csv.writer(f); w.writerow(cols)
        for r in rows:
            g = r['_geo']; w.writerow([r.get(k) for k in ROW_KEYS] + [g[k] for k in ('area_km2', 'hand_m', 'stream_dist_m', 'slope_pct', 'cx', 'cy')] + [y[r['segment']], src[r['segment']]])
    json.dump(dict(storm=storm, run_dir=os.path.relpath(os.path.abspath(run_dir), ROOT), labels=[os.path.relpath(os.path.abspath(p), ROOT) for p in labels],
                   segments=len(rows), positives=int(sum(y.values())), sites_matched=len(matches), matches=matches),
              open(os.path.join(out_dir, f'matches_{storm}.json'), 'w'), indent=0)
    print(f'{fn}: {len(rows)} segments, {sum(y.values())} positive, {len(matches)} sites matched')
    return fn


def map_segments(run_dir, out, tmp=None):
    """p_close_ml for every in-box segment of a run -> <out>/ml_segments.json (map layer 'Learned closure chance'; the map works without it).
    Re-runs the prototype on run_dir (PROTO_ML=1) into a temp dir; nothing else in <out> changes.  The model uses peak flow speed (log_speed):
    without vel_max.npz (w9 LF_VOUT=1) the speed feature is 0 and the file says velocity=false."""
    global CAPTURE
    import tempfile
    sys.path.insert(0, HERE); sys.modules.setdefault('closure_ml', sys.modules[__name__]); import prototype as PT
    CAPTURE = {}; os.environ['PROTO_ML'] = '1'; td = tempfile.TemporaryDirectory(prefix='mlmap_')
    try:
        PT.run(run_dir, tmp or td.name, os.path.join(ROOT, 'docs', 'graph_segments.json'),
               os.path.join(ROOT, 'docs', 'network', 'crossings_all.json'), os.path.join(ROOT, 'docs', 'prone', 'flood_reports.json'),
               os.path.join(ROOT, 'docs', 'network', 'facilities.json'), None, 30, False, None)
    finally:
        os.environ.pop('PROTO_ML', None); td.cleanup()
    rows = CAPTURE['rows']; CAPTURE = None
    gj = os.path.join(out, 'segments.geojson')                  # compact: only the segments drawn on the map, when the map exists
    if os.path.exists(gj):
        on_map = {int(f['properties']['segment']) for f in json.load(open(gj))['features']}; rows = [r for r in rows if r['segment'] in on_map]
    vel = os.path.exists(os.path.join(run_dir, 'vel_max.npz')); M = json.load(open(os.path.join(ML_DIR, 'closure_lr.json')))
    doc = dict(model='closure_lr (proto/ml/closure_lr.json), candidate', trained_on=M.get('trained_on'), domain_towns=M.get('domain_towns'),
               run_dir=os.path.relpath(os.path.abspath(run_dir), ROOT), velocity=vel, pu_c_e1=round(float(M.get('pu_c_e1') or 0), 3),
               note='P(documented closure / damage) at Leominster-city reporting completeness; see docs/proto/ml/RESULTS.md'
                    + ('' if vel else '; NO velocity in this run: speed feature set to 0 (rankings biased low where water is fast)'),
               segments={str(r['segment']): round(float(r['p_close_ml']), 3) for r in rows if 'p_close_ml' in r})
    os.makedirs(out, exist_ok=True); fn = os.path.join(out, 'ml_segments.json')
    json.dump(doc, open(fn, 'w'), separators=(',', ':'))
    print(f"{fn}: {len(doc['segments'])} segments, velocity={vel}")
    return fn


def load_table(storm, out_dir=OUT_DIR):
    import csv
    rows = list(csv.DictReader(open(os.path.join(out_dir, f'features_{storm}.csv'))))
    M = json.load(open(os.path.join(out_dir, f'matches_{storm}.json')))
    return rows, M


# ---------------------------------------------------------------- models
class LR:
    """Standardised L2 logistic regression on the named features with sign-constrained selection (a feature whose fitted sign contradicts SIGN
    is dropped and the model refitted); stored as plain JSON."""
    def __init__(self, C=0.5): self.C = C
    def fit(self, X, y, feats=MAIN):
        from sklearn.linear_model import LogisticRegression
        keep = [FEATURES.index(f) for f in feats]; self.dropped = []
        while True:
            mu = X[:, keep].mean(0); sd = X[:, keep].std(0) + 1e-9
            m = LogisticRegression(C=self.C, max_iter=2000).fit((X[:, keep] - mu) / sd, y)
            bad = [(abs(b), j) for j, b in zip(keep, m.coef_[0]) if SIGN[FEATURES[j]] * b < 0]
            if not bad: break
            j = max(bad)[1]; keep.remove(j); self.dropped.append(FEATURES[j])
        self.keep, self.mu, self.sd, self.coef, self.b0, self.names = keep, mu, sd, m.coef_[0], float(m.intercept_[0]), [FEATURES[j] for j in keep]
        return self
    def decision(self, X): return ((X[:, self.keep] - self.mu) / self.sd) @ self.coef + self.b0
    def predict(self, X): return 1.0 / (1.0 + np.exp(-self.decision(X)))
    def save(self, path, extra=None):
        json.dump(dict(model='logistic', C=self.C, features=self.names, all_features=FEATURES, keep=self.keep, mean=self.mu.tolist(), scale=self.sd.tolist(),
                       coef_std=self.coef.tolist(), intercept=self.b0, dropped_for_sign=self.dropped, **(extra or {})), open(path, 'w'), indent=1)
    @classmethod
    def load(cls, path):
        d = json.load(open(path)); m = cls(d['C'])
        assert d['all_features'] == FEATURES, 'feature list changed: retrain'
        m.keep, m.mu, m.sd, m.coef, m.b0, m.names, m.dropped = d['keep'], np.array(d['mean']), np.array(d['scale']), np.array(d['coef_std']), d['intercept'], d['features'], d['dropped_for_sign']
        return m


class GBM:
    """LightGBM with monotone constraints (SIGN), Platt-calibrated on its own out-of-fold (spatial block) predictions within the training data."""
    P = dict(n_estimators=250, learning_rate=0.03, num_leaves=7, min_child_samples=30, subsample=0.8, subsample_freq=1, colsample_bytree=0.8,
             reg_lambda=2.0, verbose=-1, random_state=0)
    def __init__(self, feats=MAIN): self.feats = list(feats); self.idx = [FEATURES.index(f) for f in feats]
    def _fit(self, X, y):
        import lightgbm as lgb
        return lgb.LGBMClassifier(monotone_constraints=[SIGN[f] for f in self.feats], **self.P).fit(X[:, self.idx], y)
    def fit(self, X, y, groups):
        from sklearn.model_selection import GroupKFold
        oof = np.zeros(len(y))
        for tr, te in GroupKFold(3).split(X, y, groups): oof[te] = self._fit(X[tr], y[tr]).predict_proba(X[te][:, self.idx])[:, 1]
        self.platt = platt_fit(oof, y); self.m = self._fit(X, y); return self
    def predict(self, X): return platt_apply(self.platt, self.m.predict_proba(X[:, self.idx])[:, 1])
    def shap(self, X): return self.m.booster_.predict(X[:, self.idx], pred_contrib=True)[:, :-1]
    def save(self, path):
        self.m.booster_.save_model(path)
        json.dump(dict(platt=self.platt, features=self.feats, monotone=[SIGN[f] for f in self.feats], params=self.P), open(path.replace('.txt', '_calib.json'), 'w'), indent=1)


def _logit(p): p = np.clip(p, 1e-6, 1 - 1e-6); return np.log(p / (1 - p))
def platt_fit(p, y):
    from sklearn.linear_model import LogisticRegression
    m = LogisticRegression(C=1e4, max_iter=1000).fit(_logit(p)[:, None], y); return [float(m.coef_[0][0]), float(m.intercept_[0])]
def platt_apply(ab, p): return 1.0 / (1.0 + np.exp(-(ab[0] * _logit(p) + ab[1])))


# ---------------------------------------------------------------- metrics
def recall_at(score, y, share, seeds=10, matches=None, segidx=None):
    """Segment recall (share of positive segments flagged) and site recall (share of documented sites with a flagged segment) when the top
    `share` of segments is flagged; ties broken at random, averaged over seeds."""
    n = len(score); k = int(round(share * n)); rs, rsite = [], []
    for s in range(seeds):
        o = np.lexsort((np.random.default_rng(s).random(n), -score))[:k]; fl = np.zeros(n, bool); fl[o] = True
        rs.append(fl[y == 1].mean() if y.sum() else np.nan)
        if matches:
            sites = [[segidx[g] for g in m['segs'] if g in segidx] for m in matches.values()]
            rsite.append(np.mean([fl[s_].any() for s_ in sites if s_]))
    return float(np.mean(rs)), (float(np.mean(rsite)) if rsite else None)


def boot_ci(score, y, reps=300, seed=0):
    """5-95 % bootstrap interval (segments resampled) of PR-AUC and recall at 5 % flagged."""
    from sklearn.metrics import average_precision_score
    rng = np.random.default_rng(seed); a, r = [], []
    for _ in range(reps):
        i = rng.integers(0, len(y), len(y))
        if y[i].sum() == 0: continue
        a.append(average_precision_score(y[i], score[i])); r.append(recall_at(score[i], y[i], 0.05, seeds=1)[0])
    return [float(np.percentile(a, 5)), float(np.percentile(a, 95))], [float(np.percentile(r, 5)), float(np.percentile(r, 95))]


def metrics(score, y, matches=None, segidx=None, p=None, ci=False):
    from sklearn.metrics import average_precision_score, roc_auc_score
    out = dict(n=len(y), pos=int(y.sum()), base_rate=float(y.mean()), pr_auc=float(average_precision_score(y, score)), roc_auc=float(roc_auc_score(y, score)))
    for f in FLAGS:
        a, b = recall_at(score, y, f, matches=matches, segidx=segidx); out[f'rec{int(round(f * 100))}'] = a; out[f'site{int(round(f * 100))}'] = b
    if p is not None:
        out.update(brier=float(np.mean((p - y) ** 2)), brier_base=float(y.mean() * (1 - y.mean())), expected=float(p.sum()))
        out['bss'] = 1 - out['brier'] / out['brier_base']
    if ci: out['pr_auc_ci'], out['rec5_ci'] = boot_ci(score, y)
    return out


BINS = np.array([0, 0.005, 0.01, 0.02, 0.05, 0.1, 0.2, 0.4, 0.7, 1.0001])
def reliability(p, y):
    i = np.digitize(p, BINS) - 1; out = []
    for b in range(len(BINS) - 1):
        m = i == b
        if m.sum(): out.append((float(p[m].mean()), float(y[m].mean()), int(m.sum()), int(y[m].sum())))
    return out


# ---------------------------------------------------------------- train / evaluate
def arrays(rows, block=BLOCK_M):
    X = design(rows); y = np.array([int(r['y']) for r in rows]); seg = [int(r['segment']) for r in rows]
    cx = np.nan_to_num(np.array([float(r['cx'] or 'nan') for r in rows])); cy = np.nan_to_num(np.array([float(r['cy'] or 'nan') for r in rows]))
    g = (np.floor(cx / block) * 1000 + np.floor(cy / block)).astype(int)
    return X, y, seg, g


def domain(rows, towns):
    return np.array([not towns or r['town'] in towns for r in rows])


def train(storm, towns=TRAIN_TOWNS, save=True):
    """Final fits on the training storm's reporting domain; returns the models, the prior's Platt map and the Elkan-Noto c (from spatial-CV OOF)."""
    from sklearn.model_selection import GroupKFold
    rows, M = load_table(storm); X, y, seg, g = arrays(rows); D = domain(rows, towns); X, y, g = X[D], y[D], g[D]; pr = prior(rows)[D]
    lr = LR().fit(X, y); gb = GBM().fit(X, y, g); cal = platt_fit(pr, y)
    oof = np.zeros(len(y))
    for tr, te in GroupKFold(5).split(X, y, g): oof[te] = LR().fit(X[tr], y[tr]).predict(X[te])
    c = float(oof[y == 1].mean())
    if save:
        os.makedirs(ML_DIR, exist_ok=True)
        lr.save(os.path.join(ML_DIR, 'closure_lr.json'), dict(trained_on=storm, domain_towns=list(towns), n=int(len(y)), positives=int(y.sum()), pu_c_e1=c,
                note="P(documented closure/damage | x) at the training city's reporting completeness; P(damaged) ~ P / pu_c_e1 (Elkan-Noto e1, upper-bound style). See docs/proto/ml/RESULTS.md"))
        gb.save(os.path.join(ML_DIR, 'closure_gbm.txt')); json.dump(dict(prior_platt=cal, trained_on=storm, domain_towns=list(towns)), open(os.path.join(ML_DIR, 'prior_platt.json'), 'w'))
    return lr, gb, cal, c


def evaluate(train_storm, test_storms, towns=TRAIN_TOWNS, out_dir=OUT_DIR):
    import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
    from sklearn.model_selection import GroupKFold
    rows, M = load_table(train_storm); X, y, seg, g = arrays(rows); idx = {s: i for i, s in enumerate(seg)}
    X4, _, _, g4 = arrays(rows, 4000.0); D = domain(rows, towns); pr = prior(rows); pm = np.array([float(r['p_may_close']) for r in rows])
    # (A) spatial block CV inside the reporting domain: 2 km blocks, 5 folds
    Xd, yd, gd, prd = X[D], y[D], g[D], pr[D]; o = {k: np.zeros(len(yd)) for k in ('lr', 'lr_rain', 'gbm', 'prior_cal')}
    for tr, te in GroupKFold(5).split(Xd, yd, gd):
        o['lr'][te] = LR().fit(Xd[tr], yd[tr]).predict(Xd[te]); o['lr_rain'][te] = LR().fit(Xd[tr], yd[tr], FEATURES).predict(Xd[te])
        o['gbm'][te] = GBM().fit(Xd[tr], yd[tr], gd[tr]).predict(Xd[te]); o['prior_cal'][te] = platt_apply(platt_fit(prd[tr], yd[tr]), prd[te])
    # (v0) the first configuration: logistic with rain on the whole box, 4 km blocks
    v0 = np.zeros(len(y))
    for tr, te in GroupKFold(5).split(X, y, g4): v0[te] = LR().fit(X[tr], y[tr], FEATURES).predict(X[te])
    lr, gb, cal, c = train(train_storm, towns); lr_r = LR().fit(Xd, yd, FEATURES); v0m = LR().fit(X, y, FEATURES)
    dom = [s for s, d_ in zip(seg, D) if d_]; idd = {s: i for i, s in enumerate(dom)}
    Md = {k: dict(m, segs=[s for s in m['segs'] if s in idd]) for k, m in M['matches'].items()}; Md = {k: m for k, m in Md.items() if m['segs']}
    name_a = f"{train_storm} {'+'.join(towns) or 'box'}"
    res = {name_a: dict(prior=metrics(prd, yd, Md, idd, prd, ci=True), prior_cal=metrics(prd, yd, Md, idd, o['prior_cal']),
                        lr=metrics(o['lr'], yd, Md, idd, o['lr'], ci=True), lr_rain=metrics(o['lr_rain'], yd, Md, idd, o['lr_rain']),
                        gbm=metrics(o['gbm'], yd, Md, idd, o['gbm'], ci=True))}
    rel = {name_a: dict(prior=reliability(prd, yd), lr=reliability(o['lr'], yd), gbm=reliability(o['gbm'], yd))}
    # (B) whole training box: in-domain out-of-fold, out-of-domain from the final fit (never trained on)
    def stitch(oof, full):
        z = full.copy(); z[np.nonzero(D)[0]] = oof; return z
    pl_b, pg_b = stitch(o['lr'], lr.predict(X)), stitch(o['gbm'], gb.predict(X))
    name_b = f'{train_storm} whole box'
    res[name_b] = dict(prior=metrics(pr, y, M['matches'], idx, pr, ci=True), may_close=metrics(pm, y, M['matches'], idx, pm),
                       lr=metrics(pl_b, y, M['matches'], idx, pl_b, ci=True), gbm=metrics(pg_b, y, M['matches'], idx, pg_b), v0=metrics(v0, y, M['matches'], idx, v0))
    ens = os.path.join(ROOT, 'docs', 'proto', 'ens', 'leominster_sep2023_n12', 'ens_segments.geojson')
    if train_storm == 'sep2023' and os.path.exists(ens):
        E = {f['properties']['segment']: f['properties'] for f in json.load(open(ens))['features']}
        pe = np.array([float(E.get(s, {}).get('p_mean') or 0) for s in seg]); res[name_b]['ensemble'] = metrics(pe, y, M['matches'], idx, pe)
    # (C) blind test storms: whole box, final models, no refit / recalibration
    for ts in test_storms:
        R2, M2 = load_table(ts); X2, y2, s2, _ = arrays(R2); i2 = {s: i for i, s in enumerate(s2)}; p2 = prior(R2)
        pl, pg, pc, pr2, pv = lr.predict(X2), gb.predict(X2), platt_apply(cal, p2), lr_r.predict(X2), v0m.predict(X2)
        pm2 = np.array([float(r['p_may_close']) for r in R2]); mm = M2['matches']
        res[ts] = dict(prior=metrics(p2, y2, mm, i2, p2, ci=True), prior_cal=metrics(p2, y2, mm, i2, pc), may_close=metrics(pm2, y2, mm, i2, pm2),
                       lr=metrics(pl, y2, mm, i2, pl, ci=True), lr_rain=metrics(pr2, y2, mm, i2, pr2), gbm=metrics(pg, y2, mm, i2, pg, ci=True), v0=metrics(pv, y2, mm, i2, pv))
        rel[ts] = dict(prior=reliability(p2, y2), lr=reliability(pl, y2), gbm=reliability(pg, y2))
    # drivers
    imp = dict(zip(gb.feats, np.abs(gb.shap(Xd)).mean(0).tolist())); coef = dict(zip(lr.names, lr.coef.tolist()))
    os.makedirs(out_dir, exist_ok=True); figures(rel, coef, imp, lr, name_a, out_dir)
    meta = dict(train=train_storm, towns=list(towns), test=list(test_storms), pu_c=c, lr_dropped=lr.dropped, lr_coef_std=coef, lr_intercept=lr.b0,
                lr_rain_coef_std=dict(zip(lr_r.names, lr_r.coef.tolist())), v0_coef_std=dict(zip(v0m.names, v0m.coef.tolist())), shap_mean_abs=imp,
                runs={k: json.load(open(os.path.join(out_dir, f'matches_{k}.json')))['run_dir'] for k in [train_storm] + list(test_storms)})
    json.dump(dict(results=res, reliability=rel, **meta), open(os.path.join(out_dir, 'results.json'), 'w'), indent=1)
    write_results(res, rel, meta, out_dir)
    return res


def figures(rel, coef, imp, lr, name_a, out_dir):
    import matplotlib.pyplot as plt
    COL = dict(prior='#1baf7a', lr='#2a78d6', gbm='#eb6834'); MK = dict(prior='s', lr='o', gbm='^')
    LAB = dict(prior='physics prior (30 cm)', lr='logistic (main)', gbm='LightGBM + Platt')
    fig, axs = plt.subplots(1, len(rel), figsize=(5.0 * len(rel), 4.6), squeeze=False)
    for ax, (st, R_) in zip(axs[0], rel.items()):
        ax.plot([1e-4, 1], [1e-4, 1], color='#9a9a9a', lw=1, ls='--', label='perfect calibration')
        for k, pts in R_.items():
            pts = [p_ for p_ in pts if p_[0] > 0]
            ax.plot([p_[0] for p_ in pts], [max(p_[1], 2e-4) for p_ in pts], color=COL[k], lw=2, marker=MK[k], ms=8, label=LAB[k], mec='white', mew=1.5)
        ax.set_xscale('log'); ax.set_yscale('log'); ax.set_xlim(1e-4, 1.2); ax.set_ylim(1.5e-4, 1.2)
        ax.set_xlabel('predicted probability (bin mean)'); ax.set_ylabel('observed share labeled (0 drawn at 2e-4)'); ax.grid(alpha=.25, lw=.6)
        ax.set_title(f"{st}: {'spatial-block CV, out of fold' if st == name_a else 'blind test'}", fontsize=10); ax.spines[['top', 'right']].set_visible(False)
    axs[0][0].legend(fontsize=8, frameon=False, loc='upper left'); fig.tight_layout(); fig.savefig(os.path.join(out_dir, 'reliability.png'), dpi=130); plt.close(fig)
    fig, axs = plt.subplots(1, 2, figsize=(10.5, 4.2))
    nm = MAIN; cv = [coef.get(f, 0.0) for f in nm]; o_ = np.argsort(np.abs(cv))
    axs[0].barh([nm[i] + ('' if nm[i] in coef else ' (dropped)') for i in o_], [cv[i] for i in o_], color=['#2a78d6' if cv[i] >= 0 else '#eb6834' for i in o_], height=.6)
    axs[0].axvline(0, color='#666666', lw=.8); axs[0].set_title('logistic: coefficient per SD (log-odds); blue raises risk', fontsize=10)
    k2 = sorted(imp, key=imp.get); axs[1].barh(k2, [imp[k] for k in k2], color='#2a78d6', height=.6); axs[1].set_title('LightGBM: mean |SHAP| (log-odds)', fontsize=10)
    for a in axs: a.spines[['top', 'right']].set_visible(False); a.grid(axis='x', alpha=.25, lw=.6)
    fig.tight_layout(); fig.savefig(os.path.join(out_dir, 'importance.png'), dpi=130); plt.close(fig)


NM = dict(prior='physics prior p_close (30 cm, sigma 10 cm)', prior_cal='prior, Platt-calibrated on train', may_close='prior OR overtopping (p_may_close)',
          ensemble='12-member ensemble mean P (older defaults)', lr='**logistic, hazard features (main)**', lr_rain='logistic + worst-hour rain',
          gbm='LightGBM monotone + Platt', v0='v0: logistic + rain, whole box (first run)')


def write_results(res, rel, meta, out_dir):
    f = lambda v, d=3: '-' if v is None else f'{v:.{d}f}'
    L = ['# Learned road-closure model (closure_ml): results', '',
         f"Made by `python proto/closure_ml.py evaluate` (selftest: `python proto/closure_ml.py selftest`). Train storm `{meta['train']}` "
         f"(run `{meta['runs'][meta['train']]}`), training domain: {', '.join(meta['towns']) or 'whole box'}. Blind test: "
         + ', '.join(f"`{t}` (run `{meta['runs'][t]}`)" for t in meta['test']) + '. Nothing was fitted, calibrated or selected on a test storm (see "How the design was chosen").', '',
         '## Scores', '',
         'PR-AUC = average precision with labeled segments as positives (chance = base rate). rec@k = share of labeled segments in the top k % of segments; '
         'site@k = share of documented sites with at least one matched segment in the top k %. Brier / BSS (skill vs always predicting the base rate) use each model\'s '
         'own probabilities; "expected" = sum of P against the labeled count. Ties (the prior is ~0 on most dry segments) are broken at random. [a, b] = 5-95 % bootstrap '
         'interval over segments.', '']
    for st, R in res.items():
        r0 = R['prior']
        how = 'spatial block CV (2 km blocks, 5 folds), out of fold' if st.endswith(tuple(meta['towns'])) and meta['towns'] else (
            'in-domain out of fold + out-of-domain from the final fit' if st.endswith('whole box') else 'blind test, final models as saved')
        L += [f"### {st}: {how}. {r0['n']} segments, {r0['pos']} labeled ({100 * r0['base_rate']:.2f} %)", '',
              '| model | PR-AUC | ROC-AUC | rec@2% | rec@5% | rec@10% | site@2% | site@5% | site@10% | Brier | BSS | expected / labeled |', '|' + '---|' * 12]
        for k, m in R.items():
            ci = f" [{m['pr_auc_ci'][0]:.2f}, {m['pr_auc_ci'][1]:.2f}]" if 'pr_auc_ci' in m else ''
            ci5 = f" [{m['rec5_ci'][0]:.2f}, {m['rec5_ci'][1]:.2f}]" if 'rec5_ci' in m else ''
            L.append(f"| {NM.get(k, k)} | {f(m['pr_auc'])}{ci} | {f(m['roc_auc'])} | {f(m['rec2'], 2)} | {f(m['rec5'], 2)}{ci5} | {f(m['rec10'], 2)} | {f(m['site2'], 2)} | "
                     f"{f(m['site5'], 2)} | {f(m['site10'], 2)} | {f(m.get('brier'), 4)} | {f(m.get('bss'), 3)} | {m.get('expected', 0):.0f} / {m['pos']} |")
        L.append('')
    L += ['## Reliability', '', '![reliability](reliability.png)', '',
          'Per bin (edges ' + ', '.join(f'{b:g}' for b in BINS[:-1]) + ', 1): mean P -> observed share labeled (segments, labeled).', '']
    for st, R in rel.items():
        for k, pts in R.items(): L.append(f"- {st}, {k}: " + '; '.join(f'{a:.3f} -> {b:.3f} ({n_}, {p_})' for a, b, n_, p_ in pts))
    coef, imp = meta['lr_coef_std'], meta['shap_mean_abs']
    L += ['', '## Drivers', '', '![importance](importance.png)', '',
          f"Main logistic model (intercept {meta['lr_intercept']:+.2f} on standardised features; coefficients are log-odds per standard deviation) and LightGBM mean |SHAP|, both on the training domain.", '',
          '| feature | expected sign | logistic coef / SD | LightGBM mean abs SHAP | with rain: logistic coef |', '|---|---|---|---|---|']
    for f_ in sorted(FEATURES, key=lambda f_: -abs(coef.get(f_, meta['lr_rain_coef_std'].get(f_, 0)))):
        sg = '+' if SIGN[f_] > 0 else '-' if SIGN[f_] < 0 else 'free'
        c_ = f'{coef[f_]:+.3f}' if f_ in coef else ('dropped (sign)' if f_ in meta['lr_dropped'] else 'not used')
        L.append(f"| {f_} | {sg} | {c_} | {f(imp.get(f_))} | {f(meta['lr_rain_coef_std'].get(f_))} |")
    L += ['', f"Dropped from the main logistic model because the fitted sign contradicted physics: {', '.join(meta['lr_dropped']) or 'none'}.", '',
          '## Positive-unlabeled correction', '',
          f"Unreported is not dry. Elkan & Noto (2008) e1: c = mean out-of-fold P over labeled segments in the training domain = **{meta['pu_c']:.3f}**. If the "
          f"labels were a random sample of the damaged segments, P(damaged) ~ P(documented) / c, about {1 / meta['pu_c']:.1f}x the documented count. e1 assumes the "
          'classifier is near-certain somewhere, which a weak rare-event model is not, so read it as an upper-bound style factor. Ranking metrics are unchanged by it '
          '(monotone rescaling); the saved model outputs P(documented) at Leominster-city reporting completeness and stores c alongside.', '']
    L += open(os.path.join(HERE, 'ml', 'RESULTS_notes.md')).read().splitlines() if os.path.exists(os.path.join(HERE, 'ml', 'RESULTS_notes.md')) else []
    open(os.path.join(out_dir, 'RESULTS.md'), 'w').write('\n'.join(L) + '\n')


# ---------------------------------------------------------------- selftest
def selftest():
    rng = np.random.default_rng(1)
    z = np.add.outer(np.arange(6.0), np.abs(np.arange(7.0) - 3) * 0.5)        # valley down the middle column, sloping to row 0
    A = flow_acc(z); assert A[0, 3] == A.max() and A.max() == 42, A
    n = 4000; d = rng.gamma(1.0, 0.15, n); h = rng.uniform(0, 20, n)
    rows = [dict(peak_depth_m=d[i], hours_over_15cm=10 * d[i], freeboard_m=None, peak_speed_ms=None, p_culvert=0, p_edge=0, area_km2=1, hand_m=h[i], slope_pct=2,
                 road_class='local / collector', peak1h_mm=40) for i in range(n)]
    true = 1 / (1 + np.exp(-(-5 + 6 * d - 0.1 * h))); y = (rng.random(n) < true * 0.5).astype(int)
    X = design(rows); assert X[:, FEATURES.index('local_road')].all()
    m = LR().fit(X, y); p = m.predict(X)
    assert m.coef[m.names.index('log_depth')] > 0 and 'hand_m' in m.names and m.coef[m.names.index('hand_m')] < 0
    import tempfile
    fn = os.path.join(tempfile.mkdtemp(), 'lr.json'); m.save(fn); assert np.allclose(LR.load(fn).predict(X), p)
    k = metrics(p, y, p=p); kp = metrics(prior(rows), y)
    assert k['pr_auc'] > kp['pr_auc'] - 0.02 and k['pr_auc'] > 2 * y.mean() and abs(k['expected'] - y.sum()) < 0.1 * y.sum(), (k, kp)
    assert abs(recall_at(np.zeros(n), y, 0.10)[0] - 0.10) < 0.05                    # all ties -> random flagging
    g = rng.integers(0, 10, n); gb = GBM().fit(X, y, g); assert metrics(gb.predict(X), y)['roc_auc'] > 0.7
    print('closure_ml selftest ok')


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0]); ap.add_argument('cmd', choices=['extract', 'train', 'evaluate', 'map', 'selftest'])
    ap.add_argument('--out', help='map: run output folder (docs/proto/<run>)')
    ap.add_argument('--run-dir'); ap.add_argument('--storm'); ap.add_argument('--labels', default='')
    ap.add_argument('--train', default='sep2023'); ap.add_argument('--test', default='aug2021')
    ap.add_argument('--towns', default=','.join(TRAIN_TOWNS), help='training domain: towns whose reporting is near-complete ("" = whole box)')
    a = ap.parse_args(); towns = tuple(t for t in a.towns.split(',') if t)
    if a.cmd == 'selftest': selftest()
    elif a.cmd == 'extract': extract(a.run_dir, a.storm, [p for p in a.labels.split(',') if p])
    elif a.cmd == 'map': map_segments(a.run_dir, a.out)
    elif a.cmd == 'train': print('pu_c', train(a.train, towns)[3])
    else: evaluate(a.train, [t for t in a.test.split(',') if t], towns)
