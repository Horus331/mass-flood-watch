"""Leominster parametric study: the readout of docs/proto/phase1/PARAMETRIC_PREREG.md.

    python proto/parametric_eval.py      # reads docs/proto/phase1/parametric/<id>/ -> docs/proto/phase1/parametric.json (+ prints the table)

Matching is geometric and the same in every run: the base catalogue run's matches_sep2023.json (strict 30 m, the counts of LEOMINSTER_COUNTS.md).
"""
import csv, glob, gzip, json, math, os
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); PH = f'{ROOT}/docs/proto/phase1'; RUNS = f'{PH}/parametric'
MATCH = f'{ROOT}/docs/proto/parity/catalog/sep2023_leominster_20m/matches_sep2023.json'
ORDER = ['pm_base', 'pm_c20', 'pm_c50', 'pm_c100', 'pm_ct', 'pm_s1', 'pm_s3', 'pm_s2raw', 'pm_f', 'pm_cs']
LABEL = {'pm_base': 'base (AMC II × 0.88, culverts open)', 'pm_c20': 'culverts 20 % blocked', 'pm_c50': 'culverts 50 % blocked',
         'pm_c100': 'culverts 100 % blocked', 'pm_ct': 'smallest third of culverts 100 % blocked', 'pm_s1': 'dry soil (AMC I)',
         'pm_s3': 'wet soil (AMC III)', 'pm_s2raw': 'calibration removed (AMC II × 1.00)', 'pm_f': 'frozen ground (Knisel CN 95/98, no soak-in)',
         'pm_cs': '50 % blocked + wet soil (AMC III)'}
BOX = (162000, 908000, 182000, 928000)


def load_run(d):
    p = f'{d}/segments.geojson'
    G = json.load(gzip.open(p + '.gz')) if not os.path.exists(p) and os.path.exists(p + '.gz') else json.load(open(p))
    seg = {int(f['properties']['segment']): f for f in G['features']}
    S = json.load(open(f'{d}/summary.json'))
    C = json.load(open(f'{d}/cascade.json')) if os.path.exists(f'{d}/cascade.json') else None
    H = np.load(f'{d}/hmax_cm.npz') if os.path.exists(f'{d}/hmax_cm.npz') else None
    return dict(seg=seg, S=S, C=C, H=H)


def flagged(R): return {s for s, f in R['seg'].items() if (f['properties'].get('p_close') or 0) >= 0.5}


def depth(R, segs): return max([R['seg'][s]['properties'].get('peak_depth_m') or 0 for s in segs if s in R['seg']] or [0.0])


def chance(n_segs, k, N):
    """P(a label with n matched segments is hit when k of N segments are flagged at random)."""
    if k <= 0: return 0.0
    return 1.0 - math.exp(math.lgamma(N - n_segs + 1) - math.lgamma(N - n_segs - k + 1) - math.lgamma(N + 1) + math.lgamma(N - k + 1)) if N - n_segs >= k else 1.0


def seg_xy(f, tr):
    g = f['geometry']; parts = g['coordinates'] if g['type'] == 'MultiLineString' else [g['coordinates']]
    return np.array([tr.transform(*p) for line in parts for p in line])


def main():
    from pyproj import Transformer
    tr = Transformer.from_crs(4326, 26986, always_xy=True)
    M = json.load(open(MATCH))['matches']
    REP = {k: v['segs'] for k, v in M.items() if k.startswith('labels_sep2023_leominster.csv') and v['segs']}
    DPW = {k.split(':')[1]: v['segs'] for k, v in M.items() if 'dpw' in k and v['segs']}
    dpw_rows = {r['id']: r for r in csv.DictReader(open(f'{ROOT}/proto/data/labels_sep2023_leominster_dpw.csv'))}
    rep_rows = {r['id']: r for r in csv.DictReader(open(f'{ROOT}/proto/data/labels_sep2023_leominster.csv'))}
    LM = {p['id']: p for p in json.load(open(f'{PH}/leominster_misses.json'))['points']}
    ham = [k for k in REP if 'hamilton' in (rep_rows.get(k.split(':')[1], {}).get('name', '') + rep_rows.get(k.split(':')[1], {}).get('road', '')).lower()]
    lab_xy = np.array([tr.transform(float(r['lon']), float(r['lat'])) for r in list(rep_rows.values()) + list(dpw_rows.values()) if r.get('lon')])
    runs = {i: load_run(f'{RUNS}/{i}') for i in ORDER if os.path.exists(f'{RUNS}/{i}/summary.json')}
    if 'pm_base' not in runs: raise SystemExit('pm_base missing')
    N = runs['pm_base']['S']['segments_in_box']; B = runs['pm_base']; FB = flagged(B)
    base_miss = [i for i, s in DPW.items() if not set(s) & FB]
    wach = [i for i in base_miss if dpw_rows[i]['road'] == 'wa']; xmiss = [i for i in base_miss if LM.get(i, {}).get('cls_amended') == 'culvert']
    out = dict(made_by='proto/parametric_eval.py', prereg='docs/proto/phase1/PARAMETRIC_PREREG.md', segments_in_box=N,
               base_dpw_misses=len(base_miss), wachusett_misses=len(wach), crossing_misses=len(xmiss), hamilton_labels=ham, rows=[])
    for i, R in runs.items():
        F = flagged(R); k = len(F)
        rh = sum(1 for s in REP.values() if set(s) & F); dh = sum(1 for s in DPW.values() if set(s) & F)
        new = sorted(F - FB); gone = sorted(FB - F)
        newhit = [m for m in base_miss if set(DPW[m]) & F]
        over = []
        for s in new:
            xy = seg_xy(R['seg'][s], tr)
            if not len(lab_xy) or np.min(np.hypot(*(xy[:, None, :] - lab_xy[None, :, :]).transpose(2, 0, 1))) > 150: over.append(s)
        C = (R['C'] or {}).get('totals', {}).get('peak', {})
        row = dict(id=i, scenario=LABEL[i], flagged=k, flagged_share=round(k / N, 4),
                   reports_hit=rh, reports=len(REP), reports_recall=round(rh / len(REP), 3),
                   reports_chance=round(float(np.mean([chance(len(s), k, N) for s in REP.values()])), 3),
                   dpw_hit=dh, dpw=len(DPW), dpw_recall=round(dh / len(DPW), 3), dpw_chance=round(float(np.mean([chance(len(s), k, N) for s in DPW.values()])), 3),
                   newly_closed=len(new), no_longer_closed=len(gone), newly_closed_unreported=len(over),
                   base_misses_now_hit=len(newhit), wachusett_now_hit=sum(1 for m in newhit if m in wach), crossing_misses_now_hit=sum(1 for m in newhit if m in xmiss),
                   median_depth_base_misses_cm=round(100 * float(np.median([depth(R, DPW[m]) for m in base_miss])), 1),
                   median_depth_wachusett_cm=round(100 * float(np.median([depth(R, DPW[m]) for m in wach])), 1) if wach else None,
                   median_depth_crossing_misses_cm=round(100 * float(np.median([depth(R, DPW[m]) for m in xmiss])), 1) if xmiss else None,
                   hamilton_reached=any(set(REP[h]) & F for h in ham) if ham else None,
                   hamilton_depth_cm=round(100 * max([depth(R, REP[h]) for h in ham] or [0]), 1) if ham else None,
                   pop_lost_any=C.get('pop_lost_any'), pop_lost_hospital=C.get('pop_lost_hospital'), pop_lost_fire=C.get('pop_lost_fire'),
                   pop_lost_police=C.get('pop_lost_police'), pop_isolated=C.get('pop_isolated'),
                   rain_max_total_mm=R['S'].get('rain_max_total_mm'), culverts_overtopped=R['S'].get('culverts_overtopped'))
        out['rows'].append(row)
    out['culvert_priority'] = priority(runs, tr, FB)
    json.dump(out, open(f'{PH}/parametric.json', 'w'), indent=1)
    keys = ['id', 'flagged', 'reports_hit', 'dpw_hit', 'newly_closed', 'newly_closed_unreported', 'base_misses_now_hit', 'wachusett_now_hit',
            'crossing_misses_now_hit', 'median_depth_base_misses_cm', 'hamilton_reached', 'pop_lost_any']
    print(' | '.join(keys))
    for r in out['rows']: print(' | '.join(str(r[k]) for k in keys))
    return out


def priority(runs, tr, FB, near_m=300.0, pool_m=40.0):
    """Culvert priority (prereg item 7): for every culvert blocked in pm_c100 / pm_ct, the segments within near_m that close only in the
    blocked run, and the rise of the peak depth within pool_m (the pool behind the road), from hmax_cm.npz."""
    import importlib.util
    src = open(f'{ROOT}/sim/colab/w9_lisflood.py').read(); ns = {'np': np}
    exec(src[src.index('def is_bridge'):src.index('def block_crossings')], ns); exec(src[src.index('def small_third'):src.index('def partial_block')], ns)
    X = json.load(open(f'{ROOT}/docs/network/crossings_all.json')); C = X['columns']
    rows = [dict(zip(C, r)) for r in X['rows'] if r[C.index('lon')] is not None]
    x0, y0, x1, y1 = BOX; res = 20.0; out = {}
    for rid in ('pm_c100', 'pm_ct'):
        if rid not in runs or runs[rid]['H'] is None or runs['pm_base']['H'] is None: continue
        R = runs[rid]; F = flagged(R); new = F - FB
        newxy = {s: seg_xy(R['seg'][s], tr) for s in new}
        HB = runs['pm_base']['H']['hmax_cm'].astype(float); HR = R['H']['hmax_cm'].astype(float)
        xs, ys = tr.transform([r['lon'] for r in rows], [r['lat'] for r in rows])
        keep = ns['small_third'](rows, xs, ys, BOX) if rid == 'pm_ct' else None
        L = []
        for r, x, y in zip(rows, xs, ys):
            if not (x0 <= x < x1 and y0 <= y < y1) or ns['is_bridge'](r) or (keep is not None and r['id'] not in keep): continue
            rr, cc = int((y1 - y) // res), int((x - x0) // res); k = int(pool_m // res)
            sl = (slice(max(0, rr - k), rr + k + 1), slice(max(0, cc - k), cc + k + 1))
            rise = float(HR[sl].max() - HB[sl].max()) / 100
            segs = [s for s, xy in newxy.items() if np.min(np.hypot(xy[:, 0] - x, xy[:, 1] - y)) <= near_m]
            L.append(dict(id=r['id'], lon=round(r['lon'], 5), lat=round(r['lat'], 5), road=r.get('road') or '', stream=r.get('stream') or '',
                          naacc_condition=r.get('condition'), inlet_blockage=r.get('inlet_blockage'), span_m=r.get('span_m'), rise_m=r.get('rise_m'),
                          newly_closed_within_300m=len(segs), newly_closed_roads=sorted({R['seg'][s]['properties'].get('road') or '' for s in segs} - {''}),
                          pool_rise_m=round(rise, 2)))
        L.sort(key=lambda d: (-d['newly_closed_within_300m'], -d['pool_rise_m']))
        out[rid] = dict(n_blocked=len(L), n_with_new_closures=sum(1 for d in L if d['newly_closed_within_300m']), top=L[:10])
    return out


if __name__ == '__main__':
    main()
