"""Scoring v2 for the road-closure model (ROADMAP_research.md T1; the protocol is docs/proto/PROTOCOL.md).

    python proto/score_v2.py --run docs/proto/turing/jul2023_worcester_20m --storm jul2023 --out /tmp/s.json
    python proto/score_v2.py --catalog --out docs/proto/scoring/BASELINE_v2.json --md docs/proto/scoring/baseline_table.md
    python proto/score_v2.py --compare BASE.json CAND.json        # paired bootstrap + the pre-registered adoption rule (PROTOCOL.md §5)
    python proto/score_v2.py --selftest

Input: one run folder as prototype.py writes it (flood_meta.json, segments.geojson; features_<storm>.csv and matches_<storm>.json when
closure_ml.extract has run) and the label CSVs proto/data/labels_<storm>_*.csv.  Nothing is run; nothing in the run folder is changed.

Units.
  segment   a road segment of docs/graph_segments.json inside the run box.  Universe = rows of features_<storm>.csv when present (the model's
            own in-box set), else every segment with a densified road point in the box (impacts.road_points; a few % more segments).
  label     one row of a label CSV.  Strict match: segments with a road point within 30 m (prototype.label_segments, strict=True; town-level
            coordinates are not matched).  The published matches_<storm>.json is used when present, so counts equal RECALL/LOSO.
  site      matched labels clustered single-link within 150 m count once; a site is hit when any of its segments is flagged.
Scores.  ranking key = p_close, ties broken by peak depth, then at random (5 seeds averaged).  'rule' = p_close >= 0.5 (the published flag);
  'may' = rule or p_may_close >= 0.5.  Fixed shares 1/2/3/5/10 % = top-k segments of the domain.
Metrics (per domain: 'box' = whole run box; 'towns' = the storm's reporting towns, i.e. towns of matched segments; sep2023: Leominster city):
  site / segment recall at each share and at the rule; chance recall (random k of n, exact hypergeometric per site) and lift = recall / chance;
  CSI = H / (H + M + F): segment level (F = flagged unlabelled segments) and site level (F = clusters of flagged non-site segments joined by
  graph links).  CSI is only meaningful in a complete domain (COMPLETE: Leominster DPW for sep2023); elsewhere it is reported but flagged;
  PR-AUC (average precision) at segment level and site level (each site collapsed to one unit scored by its best segment);
  FSS (Roberts & Lean 2008) on the road network: P_f, P_o = flagged / observed share of road length in a window around every road cell
  (20 m raster of road length; window = square of equal area to a disk of radius 100 / 300 / 1000 m; uniform filter).  This is the Euclidean
  approximation of an along-road window: it can pull in parallel roads and grade-separated crossings within r, which matters little at <= 300 m.
  Observed field: an exact label observes its strictly matched segments (the unit the model flags); an approximate / town label carries the
  same road length (its matched segments, else the median segment length) spread evenly over the road within its position uncertainty U
  (approx 500 m, town 1500 m), capped at the road length per cell - a thin smear.  FSS is weighted by road length; f0 = observed share; 'useful' = 0.5 + f0 / 2;
  chance = mean FSS of 8 random segment sets of the same size.
Pooled numbers (catalogue / compare): sums over storms of hits and sites (recall, CSI), of FSS numerators and denominators; mean over storms
  of PR-AUC.  CIs: two-stage cluster bootstrap (storms, then sites within storm; FSS and PR-AUC storm-level only), 2000 replicates, 90 % two-sided
  (5 % one-sided lower bound used by the adoption rule).
"""
import argparse
import csv
import glob
import json
import os
import re
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
LABELS_DIR = os.path.join(HERE, 'data')
SHARES = (0.01, 0.02, 0.03, 0.05, 0.10)
RADII = (100, 300, 1000)
CELL = 20.0
MATCH_M = 30.0
SITE_LINK_M = 150.0
UNC_M = dict(exact=30.0, approx=500.0, town=1500.0)
SEEDS = 5
FSS_DRAWS = 8
NBOOT = 2000
# storm roles (PROTOCOL.md §2)
LOSO9 = ('aug2021', 'aug2023', 'aug2023b', 'aug2026', 'jul2021', 'jul2023', 'sep2021', 'sep2022', 'sep2023')
DEV = ('sep2023', 'aug2021')                                                            # rules were built on these: in-sample
HELDOUT = ('aug2023', 'aug2023b', 'aug2026', 'jul2021', 'jul2023', 'sep2021', 'sep2022')  # OOS-7: the headline
LOCKED = ('aug2015', 'aug2018', 'aug2020', 'jul2018', 'oct2016')                       # pre-Oct-2020 IEM storms: opened once
# label expansion 2026-10-23 (docs/proto/obs/LABELS_EXPANSION.md): 16 new storms, none locked; never used for tuning -> held out.
# Reported as their own pool and pooled with OOS-7 ('heldout23'); the frozen OOS-7 decision set (PROTOCOL.md §5) is unchanged.
NEW16 = ('may2018', 'aug2018b', 'sep2018', 'sep2018w', 'sep2018m', 'sep2018b', 'jul2019', 'aug2019', 'sep2019', 'jun2020', 'jun2020b', 'aug2020b',
         'jul2021b', 'jul2023b', 'jul2023c', 'jul2023d')
DOMAIN_OVERRIDE = dict(sep2023=('Leominster',))
COMPLETE = dict(sep2023=('Leominster',))                                                # domains with a complete inventory (DPW)
# adoption rule (PROTOCOL.md §5) - fixed 23 Oct 2026 before any candidate was scored
ADOPT = dict(share=0.03, min_gain=0.05, max_storm_site_loss=1, fss_radius=300, fss_tol=0.0, lift_frac=0.8, alpha=0.05)
# adoption rule v2 (PROTOCOL.md "v2", fixed 23 Oct 2026 before any candidate was scored with it): decision set = held-out 23 (OOS-7 + NEW16,
# 90 sites); the per-storm loss check applies only to storms with >= loss_min_sites sites; alpha is divided by k in the caller.
# level='share' (ranking route, top 3 %) or 'rule' (alert-tier route: the p_close >= 0.5 tier; adds the budget cap of PROTOCOL v2 §5b).
ADOPT_V2 = dict(share=0.03, min_gain=0.04, max_storm_site_loss=1, loss_min_sites=3, fss_radius=300, fss_tol=0.0, lift_frac=0.8, alpha=0.05,
                storms='heldout23', level='share')


# ------------------------------------------------------------------------------------------------ small helpers
def F(x, d=0.0):
    try:
        v = float(x); return d if np.isnan(v) else v
    except (TypeError, ValueError): return d


def components(n, pairs):
    from scipy.sparse import coo_matrix
    from scipy.sparse.csgraph import connected_components
    pairs = np.asarray(pairs, int).reshape(-1, 2)
    A = coo_matrix((np.ones(len(pairs)), (pairs[:, 0], pairs[:, 1])), shape=(n, n))
    return connected_components(A, directed=False)[1]


def link_clusters(xy, d):
    from scipy.spatial import cKDTree
    if len(xy) == 0: return np.zeros(0, int)
    return components(len(xy), cKDTree(xy).query_pairs(d, output_type='ndarray'))


def rank_key(p, depth):
    """Lexicographic (p_close, depth) as one number: p_close is stored to 3 decimals, the depth term is < 1."""
    return np.round(np.asarray(p, float), 3) * 1e4 + np.clip(np.asarray(depth, float), 0, 9.99) / 10.0


def topk_masks(key, k, seeds=SEEDS):
    n = len(key); out = []
    for s in range(seeds):
        o = np.lexsort((np.random.default_rng(s).random(n), -key)); m = np.zeros(n, bool); m[o[:k]] = True; out.append(m)
    return out


def chance_hit(n, k, m):
    """P(at least one of m given segments is among k drawn at random from n)."""
    m = np.asarray(m, int); out = np.ones(len(m))
    for i, mi in enumerate(m):
        if n - k < mi: continue
        j = np.arange(mi); out[i] = 1.0 - np.exp(np.sum(np.log((n - k - j) / (n - j))))
    return out


def avg_precision(y, s):
    y = np.asarray(y, bool)
    if y.sum() == 0: return None
    from sklearn.metrics import average_precision_score
    return float(average_precision_score(y, s))


# ------------------------------------------------------------------------------------------------ loading a run
_GRAPH = {}


def graph():
    if not _GRAPH: _GRAPH['S'] = json.load(open(os.path.join(ROOT, 'docs', 'graph_segments.json')))
    return _GRAPH['S']


def label_files(storm):
    return sorted(glob.glob(os.path.join(LABELS_DIR, f'labels_{storm}_*.csv')))


def load_labels(storm, box):
    from pyproj import Transformer
    tr = Transformer.from_crs(4326, 26986, always_xy=True); x0, y0, x1, y1 = box; out = []
    for f in label_files(storm):
        for r in csv.DictReader(open(f)):
            try: lon, lat = float(r['lon']), float(r['lat'])
            except (TypeError, ValueError, KeyError): continue
            x, y = tr.transform(lon, lat)
            if not (x0 <= x < x1 and y0 <= y < y1): continue
            out.append(dict(key=f'{os.path.basename(f)}:{r["id"]}', id=r['id'], type=r.get('type', ''), coord=(r.get('coord_quality') or 'approx').strip(),
                            x=float(x), y=float(y), town=r.get('town', '')))
    return out


def load_run(run_dir, storm):
    """-> run dict (arrays over the in-box segment universe) for score_run."""
    sys.path.insert(0, os.path.join(ROOT, 'sim', 'infra'))
    import impacts as IM
    S = graph(); meta = json.load(open(os.path.join(run_dir, 'flood_meta.json'))); box = [float(v) for v in meta['box']]
    Q = IM.road_points(S, meta); step = float(meta['res_m']) / 2
    feat = os.path.join(run_dir, f'features_{storm}.csv')
    if os.path.exists(feat):
        rows = list(csv.DictReader(open(feat))); seg = np.array([int(r['segment']) for r in rows])
        p = np.array([F(r['p_close']) for r in rows]); pm = np.array([F(r.get('p_may_close')) for r in rows])
        d = np.array([F(r.get('peak_depth_m')) for r in rows]); town = np.array([r.get('town', '') for r in rows], dtype=object); src = 'features'
    else:
        seg = np.unique(Q['seg']).astype(int); n = len(seg); pos = {s: i for i, s in enumerate(seg)}
        p = np.zeros(n); pm = np.zeros(n); d = np.zeros(n)
        for f in json.load(open(os.path.join(run_dir, 'segments.geojson')))['features']:
            q = f['properties']; i = pos.get(int(q['segment']))
            if i is None: continue
            p[i] = F(q.get('p_close')); pm[i] = F(q.get('p_may_close')); d[i] = F(q.get('peak_depth_m'))
        town = np.array([S['props']['town'][s] for s in seg], dtype=object); src = 'segments.geojson'
    pos = {s: i for i, s in enumerate(seg)}
    keep = np.array([s in pos for s in Q['seg']]); pidx = np.array([pos[s] for s in Q['seg'][keep]], int)
    px, py = Q['x'][keep], Q['y'][keep]
    L = load_labels(storm, box); mfile = os.path.join(run_dir, f'matches_{storm}.json')
    if os.path.exists(mfile):
        M = json.load(open(mfile))['matches']; match_src = 'published'
        matches = {k: sorted({pos[s] for s in v['segs'] if s in pos}) for k, v in M.items()}
    else:
        from scipy.spatial import cKDTree
        t = cKDTree(np.column_stack([px, py])); match_src = 'strict 30 m (own)'; matches = {}
        for lab in L:
            if lab['coord'] == 'town': continue
            matches[lab['key']] = sorted(set(pidx[t.query_ball_point([lab['x'], lab['y']], MATCH_M)].tolist()))
    matches = {k: v for k, v in matches.items() if v}
    links = [(pos[a], pos[b]) for a, b in S['links'] if a in pos and b in pos]
    return dict(run=os.path.relpath(run_dir, ROOT), storm=storm, box=box, seg=seg, p=p, pm=pm, depth=d, town=town, px=px, py=py, pidx=pidx,
                step=step, labels=L, matches=matches, links=np.array(links, int).reshape(-1, 2), universe=src, match_src=match_src)


# ------------------------------------------------------------------------------------------------ FSS on the road raster
class RoadRaster:
    def __init__(self, px, py, pidx, step, w_obs, box, cell=CELL):
        x0, y0 = box[0], box[1]; c = np.floor((px - x0) / cell).astype(int); r = np.floor((py - y0) / cell).astype(int)
        r0, c0 = r.min() - 1, c.min() - 1; r -= r0; c -= c0; self.shape = (r.max() + 2, c.max() + 2)
        self.flat = r * self.shape[1] + c; self.pidx = pidx; self.step = step; N = self.shape[0] * self.shape[1]
        self.R = np.bincount(self.flat, minlength=N).astype(np.float32) * step
        self.O = np.minimum(np.bincount(self.flat, weights=w_obs, minlength=N), self.R).astype(np.float32)
        self.road = self.R > 0; self.w = self.R[self.road]; self.cell = cell; self._m = {}

    def _filt(self, a, radius):
        from scipy.ndimage import uniform_filter
        size = max(1, int(round(radius * np.sqrt(np.pi) / self.cell))); size += 1 - size % 2
        return uniform_filter(a.reshape(self.shape), size=size, mode='constant').ravel()[self.road]

    def base(self, radius):
        if radius not in self._m:
            mR = self._filt(self.R, radius); self._m[radius] = (mR, self._filt(self.O, radius))
        return self._m[radius]

    def fss(self, seg_flag, radius):
        """-> (num, den): FSS = 1 - num / den."""
        mR, mO = self.base(radius)
        Fr = np.bincount(self.flat, weights=seg_flag[self.pidx].astype(float), minlength=len(self.R)).astype(np.float32) * self.step
        mF = self._filt(Fr, radius); ok = mR > 0
        pf = np.where(ok, mF / np.where(ok, mR, 1), 0); po = np.where(ok, mO / np.where(ok, mR, 1), 0)
        return float(np.sum(self.w * (pf - po) ** 2)), float(np.sum(self.w * pf ** 2) + np.sum(self.w * po ** 2))

    @property
    def f0(self): return float(self.O.sum() / self.R.sum())


def observed_weights(px, py, pidx, step, labels, matches):
    """Per road point: observed road length (module docstring).  An exact label observes its strictly matched segments (the unit the model
    flags); an approximate / town label carries the same length (its matched segments, else the median segment length) spread evenly over the
    road within its position uncertainty U."""
    from scipy.spatial import cKDTree
    w = np.zeros(len(px))
    if not len(px): return w
    t = cKDTree(np.column_stack([px, py])); seglen = np.bincount(pidx) * step; med = float(np.median(seglen[seglen > 0]))
    for lab in labels:
        segs = [s for s in matches.get(lab['key'], []) if s < len(seglen) and seglen[s] > 0]
        if lab['coord'] == 'exact' and segs:
            w[np.isin(pidx, segs)] = step; continue
        mass = float(seglen[segs].sum()) if segs else med
        idx = t.query_ball_point([lab['x'], lab['y']], UNC_M.get(lab['coord'], 500.0))
        if idx: w[idx] += mass / len(idx)
    return w


def fss_pack(num_den):
    num, den = num_den; return None if den <= 0 else 1.0 - num / den


# ------------------------------------------------------------------------------------------------ scoring one run
def score_domain(R, dm, towns):
    n_all = len(R['seg']); ix = np.nonzero(dm)[0]; n = len(ix); remap = -np.ones(n_all, int); remap[ix] = np.arange(n)
    key = rank_key(R['p'], R['depth'])[ix]; rule = (R['p'] >= 0.5)[ix]; may = ((R['p'] >= 0.5) | (R['pm'] >= 0.5))[ix]
    # sites (strict matches restricted to the domain), clustered within 150 m
    labs = {l['key']: l for l in R['labels']}
    mk = [k for k, v in R['matches'].items() if k in labs and (remap[v] >= 0).any()]
    cl = link_clusters(np.array([[labs[k]['x'], labs[k]['y']] for k in mk]).reshape(-1, 2), SITE_LINK_M)
    sites = []
    for c in (np.unique(cl) if len(cl) else []):
        ks = [mk[i] for i in np.nonzero(cl == c)[0]]; sg = sorted({int(remap[s]) for k in ks for s in R['matches'][k] if remap[s] >= 0})
        sites.append(dict(id='+'.join(sorted(labs[k]['id'] for k in ks)), labels=ks, segs=sg, types=sorted({labs[k]['type'] for k in ks})))
    yseg = np.zeros(n, bool)
    for s in sites: yseg[s['segs']] = True
    # false-alarm clusters: flagged non-site segments joined by graph links
    lk = R['links']; lk = lk[(remap[lk[:, 0]] >= 0) & (remap[lk[:, 1]] >= 0)] if len(lk) else lk; lk = remap[lk] if len(lk) else lk

    def csi(fl):
        h = sum(bool(fl[s['segs']].any()) for s in sites); m_ = len(sites) - h
        fa = fl & ~yseg; fi = np.nonzero(fa)[0]
        if len(fi):
            sub = np.full(n, -1); sub[fi] = np.arange(len(fi)); e = lk[(sub[lk[:, 0]] >= 0) & (sub[lk[:, 1]] >= 0)] if len(lk) else lk
            nf = len(np.unique(components(len(fi), sub[e] if len(e) else np.zeros((0, 2), int))))
        else: nf = 0
        H = int((fl & yseg).sum()); M_ = int((~fl & yseg).sum()); Fs = int(fa.sum())
        return dict(site=[h, m_, nf], seg=[H, M_, Fs], csi_site=h / max(1, h + m_ + nf), csi_seg=H / max(1, H + M_ + Fs))

    # FSS raster restricted to the domain's road
    pk = remap[R['pidx']] >= 0; px, py, pidx = R['px'][pk], R['py'][pk], remap[R['pidx'][pk]]
    mloc = {k: sorted({int(remap[s]) for s in v if remap[s] >= 0}) for k, v in R['matches'].items()}
    obs = observed_weights(px, py, pidx, R['step'], R['labels'], mloc)
    RR = RoadRaster(px, py, pidx, R['step'], obs, R['box']) if len(px) else None
    rng = np.random.default_rng(12345)

    def fss_block(fl):
        out = {}
        if RR is None: return out
        k = int(fl.sum())
        for r in RADII:
            nd = RR.fss(fl, r); ch = []
            for _ in range(FSS_DRAWS):
                rf = np.zeros(n, bool); rf[rng.choice(n, k, replace=False)] = True; ch.append(fss_pack(RR.fss(rf, r)))
            out[str(r)] = dict(fss=fss_pack(nd), num=nd[0], den=nd[1], chance=float(np.mean([c for c in ch if c is not None])) if k else 0.0)
        return out

    msz = np.array([len(s['segs']) for s in sites], int)
    lsegs = {k_: [int(remap[x]) for x in R['matches'][k_] if remap[x] >= 0] for k_ in mk}   # unclustered labels (the RECALL.md / LOSO unit)

    def block(masks, k):
        fl = masks[0]; hits = np.mean([[bool(m[s['segs']].any()) for s in sites] for m in masks], axis=0) if sites else np.zeros(0)
        ch = chance_hit(n, k, msz) if sites else np.zeros(0)
        rec = float(hits.mean()) if sites else None; chr_ = float(ch.mean()) if sites else None
        segrec = float(np.mean([(m & yseg).sum() / max(1, yseg.sum()) for m in masks])) if yseg.any() else None
        lh = float(np.mean([sum(bool(m[lsegs[k_]].any()) for k_ in mk) for m in masks])) if mk else 0.0
        return dict(k=int(k), share=k / max(1, n), site_recall=rec, site_hits=float(hits.sum()), chance_recall=chr_,
                    label_hits=lh, label_recall=lh / len(mk) if mk else None,
                    lift=(rec / chr_ if rec is not None and chr_ else None), seg_recall=segrec, csi=csi(fl), fss=fss_block(fl),
                    _hits=hits.round(3).tolist(), _chance=ch.round(5).tolist())

    res = dict(n_segments=n, towns=list(towns) if towns else None, n_sites=len(sites), n_label_segments=int(yseg.sum()),
               n_labels_matched=len(mk), f0=RR.f0 if RR else None, fss_useful=(0.5 + RR.f0 / 2) if RR else None,
               complete=bool(towns and R['storm'] in COMPLETE and set(towns) == set(COMPLETE[R['storm']])),
               sites=[dict(id=s['id'], n_segs=len(s['segs']), types=s['types']) for s in sites])
    res['rule'] = block([rule], int(rule.sum())); res['may'] = block([may], int(may.sum()))
    res['shares'] = {}
    for sh in SHARES:
        k = int(round(sh * n)); res['shares'][f'{sh:g}'] = block(topk_masks(key, k), k)
    unit_s = np.array([key[s['segs']].max() for s in sites] + list(key[~yseg])); unit_y = np.r_[np.ones(len(sites), bool), np.zeros((~yseg).sum(), bool)]
    res['pr_auc'] = dict(seg=avg_precision(yseg, key), seg_chance=float(yseg.mean()) if yseg.any() else None,
                         site=avg_precision(unit_y, unit_s), site_chance=float(unit_y.mean()) if len(sites) else None)
    return res


def score_run(R):
    """All metrics for one loaded run, box-wide and inside the reporting towns."""
    out = dict(run=R['run'], storm=R['storm'], role=('dev' if R['storm'] in DEV else 'heldout' if R['storm'] in HELDOUT else 'heldout-new' if R['storm'] in NEW16 else
                                                       'locked' if R['storm'] in LOCKED else 'other'),
               universe=R['universe'], matches=R['match_src'], label_files=[os.path.basename(f) for f in label_files(R['storm'])],
               labels_in_box=len(R['labels']), domains={})
    out['domains']['box'] = score_domain(R, np.ones(len(R['seg']), bool), None)
    towns = DOMAIN_OVERRIDE.get(R['storm']) or tuple(sorted({R['town'][s] for v in R['matches'].values() for s in v}))
    if towns: out['domains']['towns'] = score_domain(R, np.isin(R['town'], list(towns)), towns)
    return out


# ------------------------------------------------------------------------------------------------ pooling and bootstrap
def _get(d, path):
    for p in path: d = d[p]
    return d


def pooled(runs, dom='box', boot=NBOOT, seed=0):
    """runs: list of score_run outputs (one per storm). -> pooled metrics with two-stage bootstrap CIs."""
    runs = [r for r in runs if dom in r['domains']]
    if not runs: return None
    blocks = ['rule', 'may'] + [('shares', f'{s:g}') for s in SHARES]

    def stat(sel, site_idx):
        o = {}
        for b in blocks:
            path = (b,) if isinstance(b, str) else b; name = b if isinstance(b, str) else 'share_' + b[1]
            LH = LN = 0.0; H = N = C = 0.0; num = {str(r): 0.0 for r in RADII}; den = {str(r): 0.0 for r in RADII}; cs = np.zeros(3)
            for i, j in zip(sel, site_idx):
                B = _get(runs[i]['domains'][dom], path); h = np.asarray(B['_hits']); c = np.asarray(B['_chance'])
                H += h[j].sum(); C += c[j].sum(); N += len(j); cs += np.asarray(B['csi']['site'])
                LH += B['label_hits']; LN += runs[i]['domains'][dom]['n_labels_matched']
                for r in num:
                    if r in B['fss']: num[r] += B['fss'][r]['num']; den[r] += B['fss'][r]['den']
            o[name] = dict(label_recall=LH / LN if LN else None, site_recall=H / N if N else None, chance=C / N if N else None, lift=(H / C if C else None),
                           csi_site=cs[0] / cs.sum() if cs.sum() else None, **{f'fss{r}': (1 - num[r] / den[r]) if den[r] else None for r in num})
        for lv in ('seg', 'site'):
            v = [runs[i]['domains'][dom]['pr_auc'][lv] for i in sel]; v = [x for x in v if x is not None]; o[f'pr_auc_{lv}'] = float(np.mean(v)) if v else None
        return o

    nsite = [len(r['domains'][dom]['sites']) for r in runs]
    point = stat(range(len(runs)), [np.arange(m) for m in nsite]); rng = np.random.default_rng(seed); reps = []
    for _ in range(boot):
        sel = rng.integers(0, len(runs), len(runs)); reps.append(stat(sel, [rng.integers(0, nsite[i], nsite[i]) for i in sel]))
    ci = {}
    for k, v in point.items():
        if isinstance(v, dict):
            ci[k] = {}
            for m in v:
                xs = [r[k][m] for r in reps if r[k][m] is not None]
                ci[k][m] = [float(np.percentile(xs, 5)), float(np.percentile(xs, 95))] if xs else None
        else:
            xs = [r[k] for r in reps if r[k] is not None]; ci[k] = [float(np.percentile(xs, 5)), float(np.percentile(xs, 95))] if xs else None
    return dict(storms=[r['storm'] for r in runs], n_sites=int(sum(nsite)), point=point, ci90=ci, boot=boot)


def compare(base, cand, boot=NBOOT, seed=0, rule=ADOPT):
    """Paired two-stage bootstrap of candidate - baseline on the held-out storms, and the adoption verdict (PROTOCOL.md §5)."""
    sh = f"{rule['share']:g}"; dom = 'box'; R = str(rule['fss_radius'])
    B = {r['storm']: r for r in base['runs'] if r.get('primary')}; C = {r['storm']: r for r in cand['runs'] if r.get('primary')}
    pool = HELDOUT + NEW16 if rule.get('storms') == 'heldout23' else HELDOUT
    if any(s in LOCKED for s in list(B) + list(C)): raise SystemExit('locked storm in a --compare input (PROTOCOL.md §2)')
    storms = [s for s in pool if s in B and s in C]
    blk = (lambda X, s: X[s]['domains'][dom]['rule']) if rule.get('level') == 'rule' else (lambda X, s: X[s]['domains'][dom]['shares'][sh])
    hb, hc, per = [], [], {}
    for s in storms:
        sb = [x['id'] for x in B[s]['domains'][dom]['sites']]; sc = [x['id'] for x in C[s]['domains'][dom]['sites']]
        if sb != sc: raise SystemExit(f'{s}: site lists differ between baseline and candidate (labels or matching changed); re-score both')
        hb.append(np.asarray(blk(B, s)['_hits'])); hc.append(np.asarray(blk(C, s)['_hits']))
        per[s] = dict(sites=len(sb), base_hits=float(hb[-1].sum()), cand_hits=float(hc[-1].sum()))
    fb = [blk(B, s)['fss'][R] for s in storms]; fc = [blk(C, s)['fss'][R] for s in storms]
    fss = lambda L, idx: 1 - sum(L[i]['num'] for i in idx) / sum(L[i]['den'] for i in idx)
    N = sum(len(h) for h in hb); d0 = (sum(h.sum() for h in hc) - sum(h.sum() for h in hb)) / N
    rng = np.random.default_rng(seed); dd = []
    for _ in range(boot):
        sel = rng.integers(0, len(storms), len(storms)); a = b = n = 0.0
        for i in sel:
            j = rng.integers(0, len(hb[i]), len(hb[i])); a += hc[i][j].sum(); b += hb[i][j].sum(); n += len(j)
        dd.append((a - b) / n if n else 0.0)
    lo = float(np.percentile(dd, 100 * rule['alpha']))
    lift_b = sum(B[s]['domains'][dom]['rule']['site_hits'] for s in storms) / max(1e-9, sum(sum(B[s]['domains'][dom]['rule']['_chance']) for s in storms))
    lift_c = sum(C[s]['domains'][dom]['rule']['site_hits'] for s in storms) / max(1e-9, sum(sum(C[s]['domains'][dom]['rule']['_chance']) for s in storms))
    dfss = fss(fc, range(len(storms))) - fss(fb, range(len(storms)))
    lossable = [p for p in per.values() if p['sites'] >= rule.get('loss_min_sites', 0)]
    worst = min(p['cand_hits'] - p['base_hits'] for p in lossable) if lossable else 0
    checks = dict(gain=bool(d0 >= rule['min_gain']), ci_lower_gt_0=bool(lo > 0), fss_no_drop=bool(dfss >= -rule['fss_tol']),
                  no_storm_loses_gt_1=bool(worst >= -rule['max_storm_site_loss']), lift_ge_0p8=bool(lift_c >= rule['lift_frac'] * lift_b))
    extra = {}
    if rule.get('level') == 'rule':      # PROTOCOL v2 §5b budget cap: mean held-out tier share <= the deployed rule's mean share on the dev storms
        cap = [B[s]['domains'][dom]['rule']['share'] for s in DEV if s in B]; cs = float(np.mean([C[s]['domains'][dom]['rule']['share'] for s in storms]))
        extra = dict(tier_share_cand=cs, tier_share_cap=float(np.mean(cap)) if cap else None)
        checks['budget_cap'] = bool(cap and cs <= np.mean(cap) + 1e-9)
    return dict(rule=rule, storms=storms, n_sites=int(N), delta_recall=float(d0), delta_recall_lower=lo, delta_fss=float(dfss), worst_storm_change=float(worst),
                lift_rule=dict(base=float(lift_b), cand=float(lift_c)), per_storm=per, checks=checks, adopt=all(checks.values()), **extra)


# ------------------------------------------------------------------------------------------------ catalogue
STORM_RE = re.compile(r'(?<![a-z])((?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)20\d\d[a-z]?)(?![0-9])')


def storm_of(name):
    m = STORM_RE.search(name); return m.group(1) if m else None


def find_runs():
    """(folder, storm, group, primary) for every published run.  primary = the LOSO run of a storm (<storm>_<area>_20m) in that group."""
    out = []
    for grp, base in (('turing', os.path.join(ROOT, 'docs', 'proto', 'turing')), ('parity', os.path.join(ROOT, 'docs', 'proto', 'parity', 'catalog'))):
        if not os.path.isdir(base): continue
        for d in sorted(os.listdir(base)):
            p = os.path.join(base, d)
            if not (os.path.exists(os.path.join(p, 'flood_meta.json')) and os.path.exists(os.path.join(p, 'segments.geojson'))): continue
            s = storm_of(d)
            if not s or not label_files(s): continue
            if s in LOCKED and os.environ.get('SCORE_LOCKED') != '1': print('locked storm, not scored:', d); continue   # PROTOCOL.md §2
            out.append((p, s, grp, bool(re.fullmatch(rf'{s}_[a-z]+_20m', d))))
    return out


def fmt(v, nd=3):
    return '–' if v is None else f'{v:.{nd}f}' if isinstance(v, float) else str(v)


def table_md(runs, pools):
    L = ['| run | storm | role | domain | n seg | sites | rule share | rule site recall | lift | CSI site | FSS100 / 300 / 1000 (chance @300) | useful | '
         'recall @1/2/3/5/10 % | PR-AUC seg / site |', '|' + '---|' * 12]
    for r in runs:
        for dom, D in r['domains'].items():
            ru = D['rule']; f = ru['fss']
            L.append(f"| {r['run'].split('/')[-1]} | {r['storm']} | {r['role']}{'' if r.get('primary') else ' (extra)'} | {dom}{' (complete)' if D['complete'] else ''} | "
                     f"{D['n_segments']} | {D['n_sites']} | {fmt(ru['share'])} | {fmt(ru['site_recall'], 2)} ({fmt(ru['site_hits'], 0)}) | {fmt(ru['lift'], 1)} | "
                     f"{fmt(ru['csi']['csi_site'], 3)} | {' / '.join(fmt(f.get(str(x), {}).get('fss')) for x in RADII)} ({fmt(f.get('300', {}).get('chance'))}) | "
                     f"{fmt(D['fss_useful'])} | {' / '.join(fmt(D['shares'][f'{s:g}']['site_recall'], 2) for s in SHARES)} | "
                     f"{fmt(D['pr_auc']['seg'])} / {fmt(D['pr_auc']['site'])} |")
    P = ['', '| pool | domain | storms | sites | metric | rule | 1 % | 2 % | 3 % | 5 % | 10 % |', '|' + '---|' * 11]
    for name, byd in pools.items():
        for dom, pl in byd.items():
            if not pl: continue
            for met in ('label_recall', 'site_recall', 'chance', 'lift', 'csi_site', 'fss100', 'fss300', 'fss1000'):
                cells = []
                for b in ['rule'] + [f'share_{s:g}' for s in SHARES]:
                    v = pl['point'][b][met]; ci = pl['ci90'][b][met]
                    cells.append(fmt(v) + (f' [{fmt(ci[0])}, {fmt(ci[1])}]' if ci and met in ('site_recall', 'fss300') else ''))
                P.append(f"| {name} | {dom} | {len(pl['storms'])} | {pl['n_sites']} | {met} | " + ' | '.join(cells) + ' |')
            P.append(f"| {name} | {dom} | | | matched labels (unclustered) | {int(sum(r['domains'][dom]['n_labels_matched'] for r in runs if r['primary'] and r['group'] == name.split(':')[0] and r['storm'] in pl['storms'] and dom in r['domains']))} | | | | | |")
            P.append(f"| {name} | {dom} | | | PR-AUC seg / site (storm mean) | {fmt(pl['point']['pr_auc_seg'])} {pl['ci90']['pr_auc_seg'] and [round(x, 3) for x in pl['ci90']['pr_auc_seg']]} / "
                     f"{fmt(pl['point']['pr_auc_site'])} {pl['ci90']['pr_auc_site'] and [round(x, 3) for x in pl['ci90']['pr_auc_site']]} | | | | | |")
    return '\n'.join(L + P) + '\n'


def catalog(out, md=None, boot=NBOOT):
    import time
    runs = []
    for p, s, grp, prim in find_runs():
        t = time.time(); r = score_run(load_run(p, s)); r.update(group=grp, primary=prim); runs.append(r)
        b = r['domains']['box']; print(f"{r['run']:55s} {s:9s} sites {b['n_sites']:3d} rule {fmt(b['rule']['share'])} rec {fmt(b['rule']['site_recall'], 2)} "
                                        f"fss300 {fmt(b['rule']['fss'].get('300', {}).get('fss'))} ({time.time() - t:.0f} s)", flush=True)
    pools = {}
    for grp in sorted({r['group'] for r in runs}):
        P = {s: r for r in runs if r['group'] == grp and r['primary'] for s in [r['storm']]}
        for name, st in (('all9', LOSO9), ('heldout7', HELDOUT), ('dev2', DEV), ('new16', NEW16), ('heldout23', HELDOUT + NEW16), ('all25', LOSO9 + NEW16)):
            sel = [P[s] for s in st if s in P]
            if sel: pools[f'{grp}:{name}'] = {dom: pooled(sel, dom, boot) for dom in ('box', 'towns')}
    res = dict(made_by='proto/score_v2.py --catalog', settings=dict(shares=SHARES, radii=RADII, cell_m=CELL, match_m=MATCH_M, site_link_m=SITE_LINK_M,
               uncertainty_m=UNC_M, seeds=SEEDS, fss_draws=FSS_DRAWS, boot=boot, adopt=ADOPT), runs=runs, pools=pools)
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True); json.dump(res, open(out, 'w'), indent=0)
    if md: open(md, 'w').write(table_md(runs, pools))
    return res


# ------------------------------------------------------------------------------------------------ selftest (synthetic)
def synthetic(nx=30, ny=30, seg_len=100.0, step=10.0, seed=0, storm='jul2023'):
    """A grid road network: horizontal and vertical segments of seg_len m between nodes; returns a run dict like load_run."""
    segs = []; pts = []; links = []; nid = {}
    for j in range(ny):
        for i in range(nx - 1): nid[('h', i, j)] = len(segs); segs.append(((i * seg_len, j * seg_len), ((i + 1) * seg_len, j * seg_len)))
    for i in range(nx):
        for j in range(ny - 1): nid[('v', i, j)] = len(segs); segs.append(((i * seg_len, j * seg_len), (i * seg_len, (j + 1) * seg_len)))
    PX, PY, PI = [], [], []
    for k, ((a, b), (c, d)) in enumerate(segs):
        t = (np.arange(int(seg_len / step)) + 0.5) / (seg_len / step); PX += list(a + t * (c - a)); PY += list(b + t * (d - b)); PI += [k] * len(t)
    ends = {}
    for k, (u, v) in enumerate(segs):
        for e in (u, v): ends.setdefault(e, []).append(k)
    for ks in ends.values():
        for a in ks:
            for b in ks:
                if a < b: links.append((a, b))
    n = len(segs); rng = np.random.default_rng(seed)
    town = np.array(['A' if s[0][0] < nx * seg_len / 2 else 'B' for s in segs], dtype=object)
    return dict(run='synthetic', storm=storm, box=[-50.0, -50.0, nx * seg_len + 50, ny * seg_len + 50], seg=np.arange(n), p=np.zeros(n), pm=np.zeros(n),
                depth=rng.random(n) * 0.05, town=town, px=np.array(PX), py=np.array(PY), pidx=np.array(PI), step=step, labels=[], matches={},
                links=np.array(links), universe='synthetic', match_src='synthetic', mid=np.array([((a + c) / 2, (b + d) / 2) for (a, b), (c, d) in segs]))


def add_labels(R, segs, coord='exact', jitter=0.0, seed=1):
    rng = np.random.default_rng(seed)
    for k, s in enumerate(segs):
        x, y = R['mid'][s] + rng.normal(0, jitter, 2) if jitter else R['mid'][s]
        key = f'syn.csv:S{len(R["labels"]) + 1:03d}'; R['labels'].append(dict(key=key, id=key.split(':')[1], type='flooded', coord=coord, x=float(x), y=float(y), town=''))
        d = np.hypot(R['px'] - x, R['py'] - y); m = sorted(set(R['pidx'][d <= MATCH_M].tolist()))
        if m and coord != 'town': R['matches'][key] = m


def selftest():
    ok = True

    def check(name, cond):
        nonlocal ok; ok &= bool(cond); print(('PASS ' if cond else 'FAIL ') + name)

    R = synthetic(); n = len(R['seg']); rng = np.random.default_rng(3)
    pos = rng.choice(n, 40, replace=False); add_labels(R, pos)
    # 1. perfect forecast: flags exactly the labelled segments' neighbourhood (the matched segments)
    lab = sorted({s for v in R['matches'].values() for s in v}); R['p'][:] = 0; R['p'][lab] = 1.0
    S1 = score_run(R)['domains']['box']
    check('perfect: site recall 1 at rule', S1['rule']['site_recall'] == 1.0)
    check('perfect: FSS300 > 0.99, well above chance', S1['rule']['fss']['300']['fss'] > 0.99 and S1['rule']['fss']['300']['chance'] < S1['rule']['fss']['300']['fss'] - 0.3)
    check('perfect: PR-AUC seg = 1', abs(S1['pr_auc']['seg'] - 1) < 1e-9)
    check('perfect: CSI seg = 1', S1['rule']['csi']['csi_seg'] == 1.0)
    check('useful threshold = 0.5 + f0/2', abs(S1['fss_useful'] - (0.5 + S1['f0'] / 2)) < 1e-12)
    # 2. nothing flagged: FSS 0, recall 0
    R['p'][:] = 0; S2 = score_run(R)['domains']['box']
    check('empty: FSS 0, rule recall 0', S2['rule']['fss']['300']['fss'] == 0.0 and S2['rule']['site_recall'] == 0.0)
    # 3. near miss (flag the neighbour segments, not the labelled ones): strict recall 0 but FSS rises with scale and beats chance
    nb = set(); ls = set(lab)
    for s_ in lab:
        cand = [b for a, b in R['links'] if a == s_ and b not in ls] + [a for a, b in R['links'] if b == s_ and a not in ls]
        if cand: nb.add(min(cand))
    R['p'][:] = 0; R['p'][sorted(nb)] = 1.0; S3 = score_run(R)['domains']['box']; f = S3['rule']['fss']
    check('near miss: strict recall 0', S3['rule']['site_recall'] == 0.0)
    check('near miss: FSS increases with scale', f['100']['fss'] < f['300']['fss'] < f['1000']['fss'] + 1e-9)
    check('near miss: FSS300 > chance', f['300']['fss'] > f['300']['chance'])
    # 4. flagging everything: recall 1, FSS low (penalised), lift 1
    R['p'][:] = 1.0; S4 = score_run(R)['domains']['box']
    check('all flagged: lift = 1, FSS300 < 0.2', abs(S4['rule']['lift'] - 1) < 1e-9 and S4['rule']['fss']['300']['fss'] < 0.2)
    # 5. chance formula vs Monte Carlo
    nn, kk, mm = 200, 15, 3; mc = np.mean([len(set(np.random.default_rng(i).choice(nn, kk, replace=False)) & {0, 1, 2}) > 0 for i in range(20000)])
    check(f'chance_hit exact {chance_hit(nn, kk, [mm])[0]:.4f} vs MC {mc:.4f}', abs(chance_hit(nn, kk, [mm])[0] - mc) < 0.01)
    # 6. random scores: fixed-share recall near chance; informative scores beat it
    R['p'] = rng.random(n).round(3); S6 = score_run(R)['domains']['box']['shares']['0.1']
    check(f"random scores: recall {S6['site_recall']:.2f} ~ chance {S6['chance_recall']:.2f}", abs(S6['site_recall'] - S6['chance_recall']) < 0.2)
    R['p'][:] = 0.1; R['p'][lab] = 0.9; S7 = score_run(R)['domains']['box']['shares']['0.05']
    check('informative scores: recall@5% = 1', S7['site_recall'] == 1.0)
    # 7. clustering: two labels 50 m apart on the same spot -> one site
    R2 = synthetic(); add_labels(R2, [10]); add_labels(R2, [10], jitter=20, seed=5)
    check('labels within 150 m form one site', score_run(R2)['domains']['box']['n_sites'] == 1)
    # 8. approximate labels are smeared (lower observed density per cell than exact)
    R3 = synthetic(); add_labels(R3, [300], coord='approx'); R3['p'][R3['matches'][R3['labels'][0]['key']]] = 1.0
    S8 = score_run(R3)['domains']['box']; R4 = synthetic(); add_labels(R4, [300]); R4['p'][R4['matches'][R4['labels'][0]['key']]] = 1.0
    S9 = score_run(R4)['domains']['box']
    check('approx label: FSS100 lower than the same label exact', S8['rule']['fss']['100']['fss'] < S9['rule']['fss']['100']['fss'])
    # 9. towns domain and bootstrap / compare
    R['p'][:] = 0; R['p'][lab[: len(lab) // 2]] = 1.0; base = score_run(R); base.update(primary=True)
    check('towns domain present', 'towns' in base['domains'])
    runs_b, runs_c = [], []
    for i, s in enumerate(HELDOUT):
        Rs = synthetic(seed=i, storm=s); add_labels(Rs, np.random.default_rng(10 + i).choice(len(Rs['seg']), 8, replace=False), seed=i)
        lb = sorted({x for v in Rs['matches'].values() for x in v}); Rs['p'][lb[: len(lb) // 3]] = 1.0; b = score_run(Rs); b.update(primary=True); runs_b.append(b)
        Rs['p'][lb] = 1.0; c = score_run(Rs); c.update(primary=True); runs_c.append(c)
    pl = pooled(runs_b, 'box', boot=200)
    ci = pl['ci90']['share_0.03']['site_recall']; pt = pl['point']['share_0.03']['site_recall']
    check(f'bootstrap CI {ci} contains point {pt:.3f}', ci[0] <= pt <= ci[1])
    v_same = compare(dict(runs=runs_b), dict(runs=runs_b), boot=200); v_up = compare(dict(runs=runs_b), dict(runs=runs_c), boot=200)
    check('compare: identical -> not adopted', not v_same['adopt'])
    check(f"compare: clearly better -> adopted (d={v_up['delta_recall']:.2f}, lo={v_up['delta_recall_lower']:.2f})", v_up['adopt'])
    print('selftest', 'OK' if ok else 'FAILED'); return ok


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--run'); ap.add_argument('--storm'); ap.add_argument('--out'); ap.add_argument('--md')
    ap.add_argument('--catalog', action='store_true'); ap.add_argument('--compare', nargs=2, metavar=('BASE', 'CAND'))
    ap.add_argument('--boot', type=int, default=NBOOT); ap.add_argument('--selftest', action='store_true')
    ap.add_argument('--protocol', choices=['v1', 'v2'], default='v1', help='--compare: adoption rule of PROTOCOL.md v1 (OOS-7) or v2 (held-out 23)')
    ap.add_argument('--k', type=int, default=1, help='--compare: number of variants scored on the decision set (alpha / k)')
    ap.add_argument('--level', choices=['share', 'rule'], default='share', help='--compare --protocol v2: ranking route (top 3 %%) or alert-tier route')
    a = ap.parse_args()
    if a.selftest: sys.exit(0 if selftest() else 1)
    if a.catalog:
        catalog(a.out or os.path.join(ROOT, 'docs', 'proto', 'scoring', 'catalog_v2.json'), a.md, a.boot); return
    if a.compare:
        rule = dict(ADOPT_V2, level=a.level) if a.protocol == 'v2' else dict(ADOPT); rule['alpha'] = rule['alpha'] / a.k
        v = compare(json.load(open(a.compare[0])), json.load(open(a.compare[1])), a.boot, rule=rule); print(json.dumps(v, indent=1))
        if a.out: json.dump(v, open(a.out, 'w'), indent=1)
        return
    if not a.run: ap.error('--run, --catalog, --compare or --selftest')
    storm = a.storm or storm_of(os.path.basename(os.path.normpath(a.run)))
    r = score_run(load_run(a.run, storm)); r['primary'] = True
    s = json.dumps(r, indent=0)
    if a.out: open(a.out, 'w').write(s)
    b = r['domains']['box']
    print(json.dumps(dict(run=r['run'], storm=storm, sites=b['n_sites'], rule={k: b['rule'][k] for k in ('share', 'site_recall', 'lift')},
                          fss={k: v['fss'] for k, v in b['rule']['fss'].items()}, fss_useful=b['fss_useful'],
                          recall_at={k: v['site_recall'] for k, v in b['shares'].items()}, pr_auc=b['pr_auc']), indent=1))


if __name__ == '__main__':
    main()
