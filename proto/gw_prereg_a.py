"""Groundwater proposal A, run exactly as frozen in docs/proto/groundwater/PREREG_A.md (20 Nov 2026).

    python proto/gw_prereg_a.py  ->  docs/proto/groundwater/prereg_a.json

Population: Leominster segments of the Sept 2023 T2 base run (phase1/parametric_t2/t2_base) with a water-table value.
Factor: shallowest seasonal high water table <= 50 cm (groundwater/roads_wtd.json, District graph ids).
Outcome: >= 1 Leominster DPW damage point within 30 m (labels_sep2023_leominster_dpw.csv). Unit = segment.
Strata: HAND {0-1, 1-2, 2-5, 5-10, >=10 m} x slope {<2, 2-5, >=5 %}. Mantel-Haenszel OR with Robins-Breslow-Greenland 95 % CI, CMH test.
"""
import csv, json, math, os
import numpy as np, pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); P = f'{ROOT}/docs/proto'
RUN = f'{P}/phase1/parametric_t2/t2_base'
HB = [0, 1, 2, 5, 10, np.inf]; SB = [0, 2, 5, np.inf]


def mh(y, x, strata):
    """MH common OR, RBG 95 % CI, CMH chi2 (continuity-corrected) and p; strata without both outcome levels contribute nothing."""
    from scipy.stats import chi2
    R = S = PR = PSQS = QS = 0.0; num = var = 0.0; used = 0; per = []
    for s in np.unique(strata):
        m = strata == s; a = int(((x == 1) & (y == 1) & m).sum()); b = int(((x == 1) & (y == 0) & m).sum())
        c = int(((x == 0) & (y == 1) & m).sum()); d = int(((x == 0) & (y == 0) & m).sum()); n = a + b + c + d
        per.append(dict(stratum=str(s), a=a, b=b, c=c, d=d))
        if n < 2 or (a + c) == 0 or (b + d) == 0 or (a + b) == 0 or (c + d) == 0: continue
        used += 1; r, s_ = a * d / n, b * c / n; Pp, Q = (a + d) / n, (b + c) / n
        R += r; S += s_; PR += Pp * r; PSQS += Pp * s_ + Q * r; QS += Q * s_
        num += a - (a + b) * (a + c) / n; var += (a + b) * (c + d) * (a + c) * (b + d) / (n * n * (n - 1))
    if S == 0 or R == 0: return dict(or_mh=None, strata_used=used, cells=per)
    OR = R / S; se = math.sqrt(PR / (2 * R * R) + PSQS / (2 * R * S) + QS / (2 * S * S))
    stat = (abs(num) - 0.5) ** 2 / var if var > 0 else None
    return dict(or_mh=round(OR, 3), ci95=[round(math.exp(math.log(OR) - 1.96 * se), 3), round(math.exp(math.log(OR) + 1.96 * se), 3)],
                cmh_chi2=round(stat, 3) if stat is not None else None, p=round(float(chi2.sf(stat, 1)), 4) if stat is not None else None,
                strata_used=used, cells=per)


def main():
    from pyproj import Transformer
    from shapely.geometry import shape, Point
    from shapely.ops import transform as stx
    from shapely.strtree import STRtree
    tr = Transformer.from_crs(4326, 26986, always_xy=True).transform
    F = pd.read_csv(f'{RUN}/features_sep2023.csv', low_memory=False)
    F = F[F.town.astype(str).str.upper() == 'LEOMINSTER'].copy()
    W = json.load(open(f'{P}/groundwater/roads_wtd.json'))['seg_wtd_min_cm']
    F['wtd'] = [W[s] if s < len(W) else None for s in F.segment]
    n_all = len(F); F = F[F.wtd.notna()].copy(); n_nodata = n_all - len(F)
    G = {f['properties']['segment']: stx(tr, shape(f['geometry'])) for f in json.load(open(f'{RUN}/segments.geojson'))['features']
         if f['properties']['segment'] in set(F.segment)}
    ids = list(G); tree = STRtree([G[i] for i in ids])
    pts = list(csv.DictReader(open(f'{ROOT}/proto/data/labels_sep2023_leominster_dpw.csv')))
    dmg, wash, matched = set(), set(), 0
    for p in pts:
        q = Point(tr(float(p['lon']), float(p['lat']))); near = [ids[i] for i in tree.query(q.buffer(30))]
        near = [i for i in near if G[i].distance(q) <= 30]
        if not near: continue
        matched += 1; best = min(near, key=lambda i: G[i].distance(q)); dmg.add(best)
        if p['type'] == 'washout': wash.add(best)
    F['damaged'] = F.segment.isin(dmg).astype(int); F['washout'] = F.segment.isin(wash).astype(int)
    F['shallow'] = (F.wtd <= 50).astype(int); F['shallow25'] = (F.wtd <= 25).astype(int)
    F['closed'] = (F.p_close >= 0.5).astype(int)
    F['wach'] = F.road.astype(str).str.upper().str.contains('WACHUSETT')
    F['local'] = F.road_class.astype(str).str.startswith('0') | F.road_class.astype(str).str.lower().str.startswith('local')
    hb = np.digitize(np.clip(F.hand_m.fillna(20), 0, 20), HB[1:-1]); sb = np.digitize(F.slope_pct.fillna(0), SB[1:-1])
    F['stratum'] = [f'h{h}s{s}' for h, s in zip(hb, sb)]
    st = F.stratum.values
    out = dict(spec='docs/proto/groundwater/PREREG_A.md', population=dict(leominster_segments=n_all, no_water_table=n_nodata, used=len(F)),
               dpw_points=len(pts), dpw_points_matched=matched, damaged_segments=int(F.damaged.sum()),
               shallow_segments=int(F.shallow.sum()), damaged_and_shallow=int((F.damaged & F.shallow).sum()),
               strata_with_damage=int(F[F.damaged == 1].stratum.nunique()),
               main=mh(F.damaged.values, F.shallow.values, st))
    nw = ~F.wach.values
    out['sens_a_no_wachusett'] = mh(F.damaged.values[nw], F.shallow.values[nw], st[nw])
    out['sens_b_cut25'] = mh(F.damaged.values, F.shallow25.values, st)
    try:
        from sklearn.linear_model import LogisticRegression
        X = np.column_stack([F.shallow, np.clip(F.hand_m.fillna(20), 0, 20), F.slope_pct.fillna(0)])
        lr = LogisticRegression(C=1e6, max_iter=2000).fit(X, F.damaged); out['sens_c_logit_or_shallow'] = round(float(np.exp(lr.coef_[0][0])), 3)
    except Exception as e:
        out['sens_c_logit_or_shallow'] = repr(e)[:100]
    st_d = np.array([f'{s}_{"L" if l else "O"}' for s, l in zip(st, F.local)])
    out['sens_d_road_class'] = mh(F.damaged.values, F.shallow.values, st_d)
    out['sens_e_washout_only'] = mh(F.washout.values, F.shallow.values, st)
    out['negative_control_closures'] = mh(F.closed.values, F.shallow.values, st)
    m = out['main']; a = out['sens_a_no_wachusett']; nc = out['negative_control_closures']
    if m.get('or_mh') is None: verdict = 'not estimable'
    elif m['or_mh'] >= 2 and m['ci95'][0] > 1 and (a.get('or_mh') or 0) > 1: verdict = 'pass'
    elif m['or_mh'] >= 2: verdict = 'inconclusive'
    else: verdict = 'fail'
    out['verdict'] = verdict
    out['not_separable_from_surface_flooding'] = bool(nc.get('or_mh') is not None and m.get('or_mh') is not None and nc['or_mh'] >= m['or_mh'])
    json.dump(out, open(f'{P}/groundwater/prereg_a.json', 'w'), indent=1)
    print(json.dumps({k: (v if not isinstance(v, dict) else {kk: vv for kk, vv in v.items() if kk != 'cells'}) for k, v in out.items()}, indent=1))


if __name__ == '__main__':
    main()
