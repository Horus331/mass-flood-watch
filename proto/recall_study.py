"""Why the closure model misses documented sites, and what raises recall without flagging half the network (docs/proto/recall/RECALL.md).

    python proto/recall_study.py anatomy     # Leominster Sept 2023 miss anatomy (GPU run, the 36 % headline) -> docs/proto/recall/anatomy_*.csv/json
    python proto/recall_study.py curves      # operating curves (recall vs flagged share), Leominster + pooled held-out storms -> curves.json
    python proto/recall_study.py tiers       # two-tier alert scheme, thresholds chosen leave-one-storm-out, bootstrap CIs -> tiers.json
    python proto/recall_study.py all         # all three, then RECALL.md is written by hand from the json (numbers quoted there come from here)
    python proto/recall_study.py all --runs docs/proto/parity/catalog --headline docs/proto/parity/calib/leo48_cn091
                                             # other run set (env PROTO_RUNS / PROTO_HEADLINE); output then defaults to <runs>/recall (PROTO_RECALL_OUT / --out)

Published data only: docs/proto/turing/leominster_sep2023_gpu (headline run) and docs/proto/turing/<storm>_<area>_20m/features_*.csv +
matches_*.json (the 9 LOSO storms).  Site = a documented label with >= 1 strictly matched segment (30 m; prototype.label_segments).  Recall is
site-level (share of sites with a flagged matched segment), the unit of the 36 % (28 / 78) headline.  Nothing here is tuned on a held-out storm.
"""
import csv
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(ROOT, 'sim', 'infra'))

def _opt(flag, env):
    """--flag value on the command line wins, then the env variable (set so closure_loso, imported later, reads the same run set)."""
    if flag in sys.argv:
        i = sys.argv.index(flag); v = sys.argv[i + 1]; del sys.argv[i:i + 2]; os.environ[env] = v
    return os.path.abspath(os.path.join(ROOT, os.environ[env])) if os.environ.get(env) else None


TUR_DEFAULT = os.path.join(ROOT, 'docs', 'proto', 'turing')
TUR = _opt('--runs', 'PROTO_RUNS') or TUR_DEFAULT                     # folder of <storm>_<area>_20m runs (LOSO storms)
GPU = _opt('--headline', 'PROTO_HEADLINE') or os.path.join(TUR_DEFAULT, 'leominster_sep2023_gpu')   # headline Leominster sep2023 run
OUT = _opt('--out', 'PROTO_RECALL_OUT') or (os.path.join(TUR, 'recall') if TUR != TUR_DEFAULT else os.path.join(ROOT, 'docs', 'proto', 'recall'))
# features of the headline box's segments (bridges): the published GPU run has none, the dams run on the same box does
GPU_FEAT = os.path.join(GPU, 'features_sep2023.csv') if os.path.exists(os.path.join(GPU, 'features_sep2023.csv')) else os.path.join(TUR_DEFAULT, 'leominster_sep2023_dams', 'features_sep2023.csv')
LAB = os.path.join(HERE, 'data', 'labels_sep2023_leominster.csv')
DPW = os.path.join(HERE, 'data', 'labels_sep2023_leominster_dpw.csv')
STANDING = ('flooded', 'closed', 'impassable')                     # standing water on the road: what the depth rule represents
EROSION = ('culvert_failure', 'washout', 'bridge_damage')          # flowing-water damage: culvert / edge / speed layers, not depth
NONFLOOD = ('other_damage', 'sinkhole')                            # dams, drainage systems, retaining walls, buckled pavement, sinkholes


def F(x, d=np.nan):
    try: return float(x)
    except (TypeError, ValueError): return d


# ------------------------------------------------------------------------------------------------ 1. miss anatomy (GPU run)
def load_gpu():
    import impacts as IM
    meta = json.load(open(os.path.join(GPU, 'flood_meta.json'))); S = json.load(open(os.path.join(ROOT, 'docs', 'graph_segments.json')))
    n = S['n']; Q = IM.road_points(S, meta, 10.0)
    G = json.load(open(os.path.join(GPU, 'segments.geojson')))['features']
    A = {k: np.zeros(n) for k in ('p_depth', 'p_close', 'p_may_close', 'p_overtop', 'p_culvert', 'p_edge', 'p_sag', 'depth', 'fb')}
    A['fb'][:] = np.nan; A['culv_near'] = np.zeros(n, bool)
    for f in G:                       # rows not kept in segments.geojson have depth < 5 cm and every P < 0.1: zero here
        p = f['properties']; i = p['segment']
        for k in ('p_depth', 'p_close', 'p_may_close', 'p_overtop', 'p_culvert', 'p_edge', 'p_sag'): A[k][i] = p[k]
        A['depth'][i] = p['peak_depth_m']; A['fb'][i] = F(p.get('freeboard_m')); A['culv_near'][i] = bool(p['culvert_overtopped_nearby'])
    return S, meta, Q, A, n


def anatomy():
    from scipy.spatial import cKDTree
    from pyproj import Transformer
    import prototype as P
    S, meta, Q, A, n = load_gpu()
    summ = json.load(open(os.path.join(GPU, 'summary.json'))); LS = {s['id']: s for s in summ['checks']['labels_segments']['sites']}
    inbox = np.zeros(n, bool); inbox[np.unique(Q['seg'])] = True
    tr = Transformer.from_crs(4326, 26986, always_xy=True); t = cKDTree(np.column_stack([Q['x'], Q['y']]))
    flag = A['p_depth'] >= 0.5; may = A['p_may_close'] >= 0.5
    fx = np.nonzero(flag[Q['seg']])[0]; tf = cKDTree(np.column_stack([Q['x'][fx], Q['y'][fx]]))
    mx_ = np.nonzero(may[Q['seg']])[0]; tm = cKDTree(np.column_stack([Q['x'][mx_], Q['y'][mx_]]))
    nm = np.array([P.norm_road(v) for v in S['props']['road']], dtype=object)
    rows = []; mism = []
    for src, path in (('news/agency', LAB), ('DPW', DPW)):
        L = P.load_labels(path); M = {m[0]['id']: m[1] for m in P.label_segments(L, Q, S['props'], meta, strict=True)}
        for lab in L:
            x, y = tr.transform(lab['lon'], lab['lat']); x0, y0, x1, y1 = meta['box']
            if not (x0 <= x < x1 and y0 <= y < y1): continue
            segs = M.get(lab['id']); d_road, _ = t.query([x, y])
            r = dict(src=src, id=lab['id'], type=lab['type'], road=lab.get('road') or '', name=(lab.get('name') or '')[:60], coord=lab.get('coord_quality', ''),
                     matched=segs is not None, n_segs=0 if segs is None else len(segs), d_road_m=round(float(d_road), 1), x=round(x, 1), y=round(y, 1))
            if segs is not None:
                r.update(depth_seg=round(float(A['depth'][segs].max()), 2), p_depth=round(float(A['p_depth'][segs].max()), 3),
                         p_may=round(float(A['p_may_close'][segs].max()), 3), p_culvert=round(float(A['p_culvert'][segs].max()), 3),
                         p_edge=round(float(A['p_edge'][segs].max()), 3), p_sag=round(float(A['p_sag'][segs].max()), 3),
                         culv_near=bool(A['culv_near'][segs].any()),
                         fb_seg=None if np.isnan(A['fb'][segs]).all() else round(float(np.nanmin(A['fb'][segs])), 2))
            for R_ in (50, 100, 300):
                sg = np.unique(Q['seg'][t.query_ball_point([x, y], R_)]); r[f'depth_{R_}'] = round(float(A['depth'][sg].max()), 2) if len(sg) else 0.0
            r['d_flag_m'] = round(float(tf.query([x, y])[0]), 0) if len(fx) else None
            r['d_may_m'] = round(float(tm.query([x, y])[0]), 0) if len(mx_) else None
            names = {P.norm_road(v) for v in (lab.get('road') or '').replace(')', '(').split('(') if v.strip()}
            cand = np.unique(Q['seg'][t.query_ball_point([x, y], 1500.0)]); same = [int(s) for s in cand if nm[s] in names]
            r['same_name_flag_1500'] = bool(len(same) and flag[same].any())
            r['hit'] = bool(segs is not None and flag[segs].any()); r['hit_may'] = bool(segs is not None and may[segs].any())
            if src == 'news/agency':        # the published run's own match is authoritative (its road points drop bridge decks / water cells)
                pub = LS.get(lab['id'])
                if (pub is None) != (segs is None) or (pub is not None and r['hit'] != ('depth' in pub['hit'])): mism.append((lab['id'], pub is not None, segs is not None, r['hit']))
                if pub is None: r.update(matched=False, n_segs=0, hit=False, hit_may=False)
                else:
                    r.update(matched=True, n_segs=pub['n_segments'], depth_seg=pub['depth_m'], p_depth=pub['p_depth'], p_may=1.0 if 'overtop' in pub['hit'] else 0.0,
                             p_culvert=pub['p_culvert'], p_edge=pub['p_edge'], p_sag=pub['p_sag'], fb_seg=pub['freeboard_m'],
                             hit='depth' in pub['hit'], hit_may='overtop' in pub['hit'])
                    if segs is not None: r['culv_near'] = bool(A['culv_near'][segs].any())
            r['cls'] = classify(r); rows.append(r)
    print('match differences vs published run:', mism)
    os.makedirs(OUT, exist_ok=True)
    keys = list(rows[0].keys()) + [k for k in ('depth_seg', 'p_depth', 'p_may', 'p_culvert', 'p_edge', 'p_sag', 'culv_near', 'fb_seg') if k not in rows[0]]
    with open(os.path.join(OUT, 'anatomy_leominster_sep2023.csv'), 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=keys); w.writeheader(); [w.writerow(r) for r in rows]
    res = summarise(rows, float(flag[inbox].mean()), float(may[inbox].mean()))
    json.dump(res, open(os.path.join(OUT, 'anatomy.json'), 'w'), indent=1)
    print(json.dumps(res, indent=1)); return res


CLS = {
    'hit': 'caught (p_close >= 0.5 on the matched segment)',
    'A_near_flag': 'model floods a road within 100 m but not the matched segment (matching / placement / which-segment issue)',
    'B_layer': 'matched segment wet or raised by a layer the default does not use (may-close, culvert HDS-5, edge, sag) or 10-30 cm deep',
    'C_name_far': 'approximate (road-centroid) point; the same road is flagged within 1.5 km (true spot uncertain)',
    'D_nonflood_dry': 'not a standing/flowing-water phenomenon (dam, drainage system, wall, pavement, sinkhole) and model dry: depth model cannot represent',
    'E_dry': 'model dry: < 10 cm on the segment, no layer, nothing flagged within 100 m (true model miss)',
    'unmatched': 'no road segment within 30 m (point off the road or town-level coordinate)',
}


def classify(r):
    if not r['matched']: return 'unmatched'
    if r['hit']: return 'hit'
    if r['d_flag_m'] is not None and r['d_flag_m'] <= 100: return 'A_near_flag'
    if r['depth_seg'] >= 0.10 or r['p_may'] >= 0.5 or r['p_culvert'] >= 0.5 or r['p_edge'] >= 0.5 or r['p_sag'] >= 0.5: return 'B_layer'
    if r['coord'] != 'exact' and r['same_name_flag_1500']: return 'C_name_far'
    if r['type'] in NONFLOOD: return 'D_nonflood_dry'
    return 'E_dry'


def summarise(rows, flag_share, may_share):
    out = dict(classes=CLS, flagged_share=round(flag_share, 4), may_close_share=round(may_share, 4))
    for src in ('news/agency', 'DPW'):
        R = [r for r in rows if r['src'] == src]; M = [r for r in R if r['matched']]
        grp = lambda r: 'standing water' if r['type'] in STANDING else 'erosion/culvert' if r['type'] in EROSION else 'non-flood damage'
        tab = {}
        for r in M: tab.setdefault(r['cls'], {}).setdefault(grp(r), 0); tab[r['cls']][grp(r)] += 1
        miss = [r for r in M if not r['hit']]
        o = dict(in_box=len(R), matched=len(M), hits=sum(r['hit'] for r in M), hits_may_close=sum(r['hit_may'] for r in M),
                 by_class={k: sum(r['cls'] == k for r in R) for k in CLS}, class_x_type=tab,
                 misses=len(miss),
                 miss_median_depth_seg=float(np.median([r['depth_seg'] for r in miss])) if miss else None,
                 miss_depth_ge_10cm_within={R_: sum(r[f'depth_{R_}'] >= 0.10 for r in miss) for R_ in (50, 100, 300)},
                 miss_depth_ge_30cm_within={R_: sum(r[f'depth_{R_}'] >= 0.30 for r in miss) for R_ in (50, 100, 300)},
                 miss_flag_within={d: sum((r['d_flag_m'] or 1e9) <= d for r in miss) for d in (50, 100, 200, 300, 500)},
                 miss_may_within={d: sum((r['d_may_m'] or 1e9) <= d for r in miss) for d in (0, 30, 100)},
                 miss_coord={q: sum(r['coord'] == q for r in miss) for q in ('exact', 'approx', 'town')},
                 hit_coord={q: sum(r['coord'] == q for r in M if r['hit']) for q in ('exact', 'approx', 'town')},
                 miss_point_off_road_gt15m=sum(r['d_road_m'] > 15 for r in miss),
                 recall_by_group={g: [sum(r['hit'] for r in M if grp(r) == g), sum(grp(r) == g for r in M)] for g in ('standing water', 'erosion/culvert', 'non-flood damage')},
                 recall_by_coord={q: [sum(r['hit'] for r in M if r['coord'] == q), sum(r['coord'] == q for r in M)] for q in ('exact', 'approx')},
                 by_road_top=sorted(([rd, sum(r['hit'] for r in M if r['road'] == rd), sum(r['road'] == rd for r in M)] for rd in {r['road'] for r in M}), key=lambda v: -v[2])[:5])
        # distinct locations: labels within 150 m of each other (single link) count once; a location is caught when any of its labels is
        from scipy.sparse.csgraph import connected_components
        from scipy.spatial import cKDTree
        if M:
            xy = np.array([[r['x'], r['y']] for r in M]); pr = cKDTree(xy).query_pairs(150.0, output_type='ndarray'); import scipy.sparse as sp
            A_ = sp.coo_matrix((np.ones(len(pr)), (pr[:, 0], pr[:, 1])), shape=(len(M), len(M))) if len(pr) else sp.coo_matrix((len(M), len(M)))
            nc, lab = connected_components(A_, directed=False); hit = np.zeros(nc, bool); np.logical_or.at(hit, lab, [r['hit'] for r in M])
            hm = np.zeros(nc, bool); np.logical_or.at(hm, lab, [r['hit_may'] for r in M])
            o['distinct_locations_150m'] = dict(n=int(nc), hits=int(hit.sum()), hits_may_close=int(hm.sum()))
        out[src] = o
    return out


# ------------------------------------------------------------------------------------------------ shared: the 9 LOSO storms
SHARES = (0.02, 0.05, 0.10)
NEVER_USED = ('aug2023', 'aug2023b', 'aug2026', 'jul2021', 'jul2023', 'sep2021', 'sep2022')   # storms no rule was built on (not sep2023 / aug2021)
_S = {}


def load_storms(nested=True):
    """closure_loso.load per storm + site lists (strict, published matches; tolerant 100 m) + layer arrays + LOSO learned predictions.
    nested: also learned predictions for storm t made without storms {h, t} (for choosing tier thresholds inside a LOSO fold)."""
    if _S: return _S
    import closure_loso as CL
    import prototype as P
    S = {s: CL.load(s) for s in CL.STORMS}
    for s, D in S.items():
        R = D['rows']; idx = {int(r['segment']): i for i, r in enumerate(R)}
        g = lambda k, d=np.nan: np.array([F(r.get(k), d) for r in R])
        D.update(depth=g('peak_depth_m', 0.0), fb=g('freeboard_m'), p_close=g('p_close', 0.0), p_may=g('p_may_close', 0.0), p_culvert=g('p_culvert', 0.0),
                 p_edge=g('p_edge', 0.0), p_sag=g('p_sag', 0.0), idx=idx)
        D['p_pluv'], D['q_pluv'], _ = P.pluvial_probability(g('peak1h_mm', 0.0), g('area_km2', 0.0), g('hand_m', 20.0), g('cx'), g('cy'), np.ones(len(R), bool))
        D['sites'] = {k: [idx[x] for x in m['segs'] if x in idx] for k, m in D['matches'].items()}
        D['sites'] = {k: v for k, v in D['sites'].items() if v}
        D['loose'] = loose_sites(s, D)
    pred = CL.loso(S, 'lr')
    for s in S: S[s]['q'] = pred[s]
    if nested:
        for h in CL.STORMS:
            for t in CL.STORMS:
                if t == h: continue
                m = CL.fit_model('lr', S, [u for u in CL.STORMS if u not in (h, t)]); S[t].setdefault('q_wo', {})[h] = m.predict(S[t]['X'])
    _S.update(S); return _S


def loose_sites(storm, D):
    """Tolerant matching (prototype.label_segments strict=False: 100 m exact / 300 m + same-name 1.5 km approx) on this run's segments.  Road points
    are rebuilt from docs/graph_segments.json, so they keep bridge decks / water cells the published run dropped: context only."""
    import impacts as IM
    import prototype as P
    d = os.path.join(TUR, f'{storm}_{AREA_OF(storm)}_20m'); meta = json.load(open(os.path.join(d, 'flood_meta.json')))
    M = json.load(open(os.path.join(d, f'matches_{storm}.json')))
    if 'GS' not in _S: _S['GS'] = json.load(open(os.path.join(ROOT, 'docs', 'graph_segments.json')))
    GS = _S['GS']; Q = IM.road_points(GS, meta, 10.0); out = {}
    for path in M['labels']:
        L = P.load_labels(os.path.join(ROOT, path))
        for lab, segs in P.label_segments(L, Q, GS['props'], meta, strict=False):
            v = [D['idx'][int(x)] for x in segs if int(x) in D['idx']]
            if v: out[f'{os.path.basename(path)}:{lab["id"]}'] = v
    return out


def AREA_OF(s):
    import closure_loso as CL
    return CL.AREA[s]


def site_recall(flag, sites):
    v = [bool(flag[x].any()) for x in sites.values()]; return (sum(v), len(v))


def chance(share, sites):
    return float(np.mean([1 - (1 - share) ** len(x) for x in sites.values()])) if sites else np.nan


def topk_flag(score, share, seed=0):
    n = len(score); k = int(round(share * n)); fl = np.zeros(n, bool)
    fl[np.lexsort((np.random.default_rng(seed).random(n), -score))[:k]] = True; return fl


def scores(D):
    """Ranking scores (higher = flagged first) for the operating curves."""
    d = D['depth']; zd = (d - 0.30) / 0.10; zo = np.where(np.isfinite(D['fb']), -np.nan_to_num(D['fb'], nan=9) / 0.15, -99)
    zp = np.where(D['p_pluv'] > 0, np.log(np.maximum(D['q_pluv'], 1e-9) / 0.5) / 0.5, -99)
    q = D['q']
    return {'rule p_close (depth)': zd + 1e-6 * q, 'may-close (overtop) alone': zo + 1e-6 * q, 'union depth OR overtop': np.maximum(zd, zo) + 1e-6 * q,
            'pluvial union (depth OR pluvial)': np.maximum(zd, zp) + 1e-6 * q, 'learned (LOSO logistic)': q,
            'hybrid: rule flags first, then learned': q + 10 * (D['p_close'] >= 0.5),
            'hybrid: rule, then may-close, then learned': q + 10 * (D['p_close'] >= 0.5) + 10 * (D['p_may'] >= 0.5)}


def curves(seeds=5):
    S = load_storms(); res = dict(note='site recall when each storm flags its own top x % of segments by the score (ties random, mean of 5 seeds); '
                                       'Leominster = sep2023 20 m run (same 36 % headline as the GPU run); learned = leave-one-storm-out', shares=list(SHARES))
    grid = [0.005, 0.01, 0.02, 0.03, 0.05, 0.075, 0.10, 0.15, 0.20]
    def part(keys, sitekey='sites', sub=None):
        out = {}
        for nm in scores(S[keys[0]]):
            row = {}
            for sh in grid:
                h = n = 0; ch = []
                for s in keys:
                    D = S[s]; sites = D[sitekey] if sub is None else {k: v for k, v in D[sitekey].items() if sub(k)}
                    sc = scores(D)[nm]; hh = np.mean([site_recall(topk_flag(sc, sh, z), sites)[0] for z in range(seeds)])
                    h += hh; n += len(sites); ch.append(chance(sh, sites) * len(sites))
                row[f'{sh:.3f}'] = dict(recall=round(h / n, 3), hits=round(h, 1), n=n, lift=round(h / n / (sum(ch) / n), 2) if sum(ch) else None)
            out[nm] = row
        return out
    res['leominster_news'] = part(['sep2023'], sub=lambda k: 'dpw' not in k)
    res['leominster_dpw'] = part(['sep2023'], sub=lambda k: 'dpw' in k)
    res['leominster_all'] = part(['sep2023'])
    res['other8_pooled'] = part([s for s in S if s in ('aug2021',) + NEVER_USED])
    res['never_used7_pooled'] = part(list(NEVER_USED))
    res['all9_pooled'] = part([s for s in S if s != 'GS'])
    res['tolerant_leominster_news'] = part(['sep2023'], 'loose', sub=lambda k: 'dpw' not in k)
    res['tolerant_other8_pooled'] = part([s for s in S if s in ('aug2021',) + NEVER_USED], 'loose')
    # the default rule's own operating point per storm
    res['default_point'] = {s: dict(share=round(float((S[s]['p_close'] >= 0.5).mean()), 4), may_share=round(float((S[s]['p_may'] >= 0.5).mean()), 4),
                                    sites=site_recall(S[s]['p_close'] >= 0.5, S[s]['sites']), may_sites=site_recall(S[s]['p_may'] >= 0.5, S[s]['sites']),
                                    loose_sites=site_recall(S[s]['p_close'] >= 0.5, S[s]['loose']))
                            for s in S if s != 'GS'}
    os.makedirs(OUT, exist_ok=True); json.dump(res, open(os.path.join(OUT, 'curves.json'), 'w'), indent=1)
    for k in ('leominster_news', 'leominster_dpw', 'other8_pooled', 'never_used7_pooled', 'tolerant_leominster_news'):
        print('\n##', k)
        for nm, row in res[k].items(): print(f'  {nm:45s}', '  '.join(f"{sh}:{row[f'{sh:.3f}']['recall']:.2f}" for sh in SHARES))
    print(json.dumps(res['default_point'], indent=0))
    return res


# ------------------------------------------------------------------------------------------------ 3. two-tier alert scheme, LOSO
# Tier 1 'likely closed' = the current default (p_close >= 0.5, unchanged).  Tier 2 'watch' = one family below with one threshold.  Each fold
# chooses the threshold (and, in the 'pick family' scheme, the family) on the 8 training storms only: highest storm-averaged site recall with
# the storm-averaged total flagged share <= the budget.  The learned score inside a fold comes from a model that never saw the held-out storm
# (nor, for a training storm's own score, that training storm).
FAMILIES = {
    'depth >= t': (lambda D, q, t: D['depth'] >= t, [0.05, 0.08, 0.10, 0.12, 0.15, 0.18, 0.20, 0.25]),
    'overtop: freeboard <= t': (lambda D, q, t: np.nan_to_num(D['fb'], nan=9) <= t, [-0.3, -0.2, -0.1, 0.0, 0.1, 0.2, 0.3, 0.5]),
    'learned P >= t': (lambda D, q, t: q >= t, [0.005, 0.0075, 0.01, 0.015, 0.02, 0.03, 0.05, 0.08, 0.12, 0.2]),
    'may-close OR learned P >= t': (lambda D, q, t: (D['p_may'] >= 0.5) | (q >= t), [0.005, 0.0075, 0.01, 0.015, 0.02, 0.03, 0.05, 0.08, 0.12, 0.2, 9]),
    'may-close OR depth >= t': (lambda D, q, t: (D['p_may'] >= 0.5) | (D['depth'] >= t), [0.05, 0.08, 0.10, 0.15, 0.20, 9]),
    'all physics layers (may-close|culvert|edge|sag|pluvial) P >= t': (
        lambda D, q, t: (D['p_may'] >= t) | (D['p_culvert'] >= t) | (D['p_edge'] >= t) | (D['p_sag'] >= t) | (D['p_pluv'] >= t), [0.2, 0.3, 0.5, 0.7, 0.9]),
}
BUDGETS = (0.05, 0.08, 0.10)


def scheme_flag(D, fam, t, q):
    return (D['p_close'] >= 0.5) | FAMILIES[fam][0](D, q, t)


def fold_choose(S, h, fam_list, budget):
    tr = [s for s in S if s not in ('GS', h)]; best = None
    for fam in fam_list:
        for t in FAMILIES[fam][1]:
            rec, sh = [], []
            for s in tr:
                fl = scheme_flag(S[s], fam, t, S[s]['q_wo'][h]); k, n = site_recall(fl, S[s]['sites']); rec.append(k / n); sh.append(fl.mean())
            r, m = float(np.mean(rec)), float(np.mean(sh))
            if m <= budget and (best is None or r > best[0] + 1e-9 or (abs(r - best[0]) < 1e-9 and m < best[1])): best = (r, m, fam, t)
    return best


def tiers(reps=2000):
    S = load_storms(); storms = [s for s in S if s != 'GS']; res = dict(budgets=list(BUDGETS), families=list(FAMILIES), schemes={})
    for budget in BUDGETS:
        for label, fl_ in [('pick family', list(FAMILIES))] + [(f, [f]) for f in FAMILIES]:
            per = {}
            for h in storms:
                b = fold_choose(S, h, fl_, budget)
                if b is None: continue
                D = S[h]; fl = scheme_flag(D, b[2], b[3], D['q']); base = D['p_close'] >= 0.5
                eq = topk_flag(np.maximum((D['depth'] - 0.30) / 0.10, -99) + 1e-6 * D['q'], fl.mean())     # rule relaxed to the same share
                # tier 2 on its own: sites it adds, and what random flagging of the same number of extra segments would add
                t2 = fl & ~base; k0 = site_recall(base, D['sites'])[0]; rng = np.random.default_rng(0); pool = np.nonzero(~base)[0]; rand = []
                for _ in range(200):
                    f_ = base.copy(); f_[rng.choice(pool, int(t2.sum()), replace=False)] = True; rand.append(site_recall(f_, D['sites'])[0] - k0)
                per[h] = dict(family=b[2], t=b[3], train_recall=round(b[0], 3), train_share=round(b[1], 4), share=round(float(fl.mean()), 4),
                              share_t1=round(float(base.mean()), 4), hits=site_recall(fl, D['sites'])[0], hits_t1=k0, n=len(D['sites']),
                              hits_eq_share_rule=site_recall(eq, D['sites'])[0], t2_added=site_recall(fl, D['sites'])[0] - k0, t2_added_random=round(float(np.mean(rand)), 2),
                              hit_vec=[bool(fl[x].any()) for x in D['sites'].values()], hit_vec_t1=[bool(base[x].any()) for x in D['sites'].values()],
                              hit_vec_eq=[bool(eq[x].any()) for x in D['sites'].values()])
            res['schemes'][f'{label} | budget {budget:.0%}'] = dict(per_storm={k: {kk: vv for kk, vv in v.items() if not kk.startswith('hit_vec')} for k, v in per.items()},
                                                                   summary=summarise_tiers(per, reps))
            sm = res['schemes'][f'{label} | budget {budget:.0%}']['summary']
            print(f"{budget:.0%} {label[:55]:55s} all9 {sm['all9']['recall']:.3f} (t1 {sm['all9']['recall_t1']:.3f}, eq-share rule {sm['all9']['recall_eq']:.3f}) "
                  f"share {sm['all9']['mean_share']:.3f}  never7 {sm['never7']['recall']:.3f} (t1 {sm['never7']['recall_t1']:.3f}, eq {sm['never7']['recall_eq']:.3f})  "
                  f"leo {sm['sep2023']['recall']:.3f} share {sm['sep2023']['mean_share']:.3f}  d_eq CI {sm['all9']['d_vs_eq_ci']}")
    json.dump(res, open(os.path.join(OUT, 'tiers.json'), 'w'), indent=1, default=lambda o: o.item() if hasattr(o, 'item') else str(o))
    return res


def summarise_tiers(per, reps):
    out = {}
    for nm, keys in (('all9', list(per)), ('never7', [s for s in per if s in NEVER_USED]), ('other8', [s for s in per if s != 'sep2023']), ('sep2023', ['sep2023'])):
        keys = [k for k in keys if k in per]
        if not keys: continue
        hv = {k: np.array(per[k]['hit_vec']) for k in keys}; h1 = {k: np.array(per[k]['hit_vec_t1']) for k in keys}; he = {k: np.array(per[k]['hit_vec_eq']) for k in keys}
        sh = {k: per[k]['share'] for k in keys}; s1 = {k: per[k]['share_t1'] for k in keys}
        def stat(ks, idx):
            a = np.concatenate([hv[k][i] for k, i in zip(ks, idx)]); b = np.concatenate([h1[k][i] for k, i in zip(ks, idx)]); e = np.concatenate([he[k][i] for k, i in zip(ks, idx)])
            ms = np.mean([sh[k] for k in ks]); m1 = np.mean([s1[k] for k in ks])
            return a.mean(), b.mean(), e.mean(), ms, m1
        r, r1, re, ms, m1 = stat(keys, [np.arange(len(hv[k])) for k in keys])
        rng = np.random.default_rng(7); B = []
        for _ in range(reps):          # two-stage cluster bootstrap: storms, then sites within storm
            ks = [keys[i] for i in rng.integers(0, len(keys), len(keys))] if len(keys) > 1 else keys
            B.append(stat(ks, [rng.integers(0, len(hv[k]), len(hv[k])) for k in ks]))
        B = np.array(B); ci = lambda v: [round(float(np.percentile(v, 5)), 3), round(float(np.percentile(v, 95)), 3)]
        out[nm] = dict(sites=int(sum(len(hv[k]) for k in keys)), hits=int(sum(hv[k].sum() for k in keys)), hits_t1=int(sum(h1[k].sum() for k in keys)),
                       recall=round(float(r), 3), recall_ci=ci(B[:, 0]), recall_t1=round(float(r1), 3), recall_t1_ci=ci(B[:, 1]), recall_eq=round(float(re), 3),
                       d_vs_t1_ci=ci(B[:, 0] - B[:, 1]), d_vs_eq=round(float(r - re), 3), d_vs_eq_ci=ci(B[:, 0] - B[:, 2]), p_beats_eq=round(float(np.mean(B[:, 0] - B[:, 2] > 0)), 3),
                       mean_share=round(float(ms), 4), mean_share_t1=round(float(m1), 4), lift=round(float(r / ms), 2) if ms else None, lift_ci=ci(B[:, 0] / B[:, 3]),
                       lift_t1=round(float(r1 / m1), 2) if m1 else None,
                       t2_added=int(sum(per[k]['t2_added'] for k in keys)), t2_added_random=round(float(sum(per[k]['t2_added_random'] for k in keys)), 1))
    return out


# ------------------------------------------------------------------------------------------------ 4. bridge approaches (PROTO_BRIDGE_APPROACH)
def bridges():
    """Approximate effect of matching labels against all road points (decks included) and scoring deck-only segments from their approaches,
    from published outputs.  Matching is exact (the new rule rebuilds the same points from docs/graph_segments.json); the deck-only segments'
    depth needs point depths the published outputs do not hold, so it is bracketed: low = deck segment never flagged (matching fix only),
    high = deck segment takes the highest p_depth of the segments it links to (whole segments, so an upper bound on 50 m approaches)."""
    import impacts as IM
    import prototype as P
    GS = json.load(open(os.path.join(ROOT, 'docs', 'graph_segments.json'))); n = GS['n']; res = {}
    hn = os.path.basename(GPU)
    runs = [(f'{hn} (headline)', GPU, GPU_FEAT, [LAB], 'gpu'), (f'{hn} DPW', GPU, GPU_FEAT, [DPW], 'gpu')]
    import closure_loso as CL
    for st in CL.STORMS:
        d = os.path.join(TUR, f'{st}_{CL.AREA[st]}_20m'); M = json.load(open(os.path.join(d, f'matches_{st}.json')))
        runs.append((st, d, os.path.join(d, f'features_{st}.csv'), [os.path.join(ROOT, x) for x in M['labels']], 'feat'))
    for name, d, fcsv, labs, kind in runs:
        meta = json.load(open(os.path.join(d, 'flood_meta.json'))); rows = list(csv.DictReader(open(fcsv)))
        inbox_old = np.zeros(n, bool); inbox_old[[int(r['segment']) for r in rows]] = True
        pd_ = np.zeros(n)
        if kind == 'gpu':
            for f in json.load(open(os.path.join(d, 'segments.geojson')))['features']: pd_[f['properties']['segment']] = f['properties']['p_depth']
            summ = json.load(open(os.path.join(d, 'summary.json'))); pub = {x['id']: 'depth' in x['hit'] for x in summ['checks']['labels_segments']['sites']}
        else:
            for r in rows: pd_[int(r['segment'])] = F(r['p_depth'], 0.0)
            Mj = json.load(open(os.path.join(d, os.path.basename(fcsv).replace('features_', 'matches_').replace('.csv', '.json'))))['matches']
            idx = set(np.nonzero(inbox_old)[0].tolist())
            pub = {k: bool(any(pd_[g] >= 0.5 for g in m['segs'] if g in idx)) for k, m in Mj.items()}
        Pall = IM.road_points(GS, meta); ue = ~Pall['end'] | (np.bincount(Pall['seg'][~Pall['end']], minlength=n)[Pall['seg']] == 0)
        Qm = {k: v[ue] for k, v in Pall.items()}
        has = np.bincount(Pall['seg'], minlength=n) > 0; deck = np.nonzero(has & ~inbox_old)[0]
        adj = {}
        for a_, b_ in GS['links']: adj.setdefault(a_, []).append(b_); adj.setdefault(b_, []).append(a_)
        isdeck = np.zeros(n, bool); isdeck[deck] = True; hi = pd_.copy()
        for s_ in deck:
            seen, stack, nb = {int(s_)}, [int(s_)], []
            while stack:
                for t in adj.get(stack.pop(), []):
                    if t in seen: continue
                    seen.add(t); (stack if isdeck[t] else nb).append(t)
            hi[s_] = max([pd_[t] for t in nb if inbox_old[t]] + [0.0])
        inbox_new = inbox_old | isdeck
        L = []
        for lp in labs: L += [dict(x, _f=os.path.basename(lp)) for x in P.load_labels(lp)]
        new = P.label_segments(L, Qm, GS['props'], meta, strict=True)
        def score(matches, p, ib):
            fl = (p >= 0.5) & ib; f = fl[ib].mean(); hit = np.array([fl[s].any() for _, s in matches]); ex = np.array([1 - (1 - f) ** len(s) for _, s in matches])
            return dict(sites=len(matches), hits=int(hit.sum()), recall=round(float(hit.mean()), 3), flagged_share=round(float(f), 4), lift=round(float(hit.mean() / ex.mean()), 2))
        if 'DPW' in name: pub = {}          # the published GPU run did not score the DPW points
        old_hits = sum(pub.values())
        o = dict(segments_in_box_old=int(inbox_old.sum()), deck_only_segments=int(len(deck)), deck_only_hi_flagged=int((hi[deck] >= 0.5).sum()),
                 old=dict(sites=len(pub), hits=int(old_hits), recall=round(old_hits / len(pub), 3) if pub else None, flagged_share=round(float(((pd_ >= 0.5) & inbox_old)[inbox_old].mean()), 4)),
                 new_low=score(new, pd_, inbox_new), new_high=score(new, hi, inbox_new),
                 new_sites_on_deck_only=int(sum(isdeck[s].any() for _, s in new)))
        if kind == 'gpu':
            oldid = set(pub) if pub else set(); o['newly_matched'] = sorted(m[0]['id'] for m in new if m[0]['id'] not in oldid)
            o['lost'] = sorted(i for i in oldid if pub if i not in {m[0]['id'] for m in new})
        res[name] = o; print(name, json.dumps(o))
    json.dump(res, open(os.path.join(OUT, 'bridges.json'), 'w'), indent=1); return res


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'all'
    os.makedirs(OUT, exist_ok=True); print(f'runs {TUR}\nheadline {GPU}\nout {OUT}')
    if cmd in ('anatomy', 'all'): anatomy()
    if cmd in ('curves', 'all'): curves()
    if cmd in ('tiers', 'all'): tiers()
    if cmd in ('bridges', 'all'): bridges()
