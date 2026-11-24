"""Readout of docs/proto/phase1/PARAMETRIC_CLEAN_PREREG.md (Leominster parametric study, clean rerun on the deployed model).

    python proto/parametric_clean_eval.py      # docs/proto/phase1/parametric_clean/<id>/ -> parametric_clean.json + .csv

Access is recomputed per run from segments.geojson with proto/cascade.py and hospital 30 / fire 8 / police 4 min (report-only; the
TAB_BOARD thresholds), whatever the run's own cascade used. Written before any result was seen (24 Nov 2026).

Inspection ranking (fixed before results): for each culvert blocked in the run, the water level in the pool within 40 m (lidar road crest
within 20 m, whatif_v3 constants) is read in the base and the blocked run; key = added water above the road crest
max(pool_blocked - crest, 0) - max(pool_base - crest, 0), ties broken by the pool rise (pool_blocked - pool_base).
"""
import csv, gzip, json, os, shutil, sys, tempfile
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); sys.path.insert(0, HERE)
import parametric_eval as PE
import parametric_t2_eval as PT
import whatif_v3 as W

PH = f'{ROOT}/docs/proto/phase1'; RUNS = f'{PH}/parametric_clean'; OUTJ = f'{PH}/parametric_clean.json'; OUTC = f'{PH}/parametric_clean.csv'
PT.RUNS = RUNS
ORDER = ['B', 'C20', 'C50', 'C100', 'CS', 'ARC1', 'ARC3', 'FZ', 'C50W']
LABEL = {'B': 'Base (deployed model)', 'C20': 'Culverts 20 % blocked', 'C50': 'Culverts 50 % blocked', 'C100': 'Culverts 100 % blocked',
         'CS': 'Smallest third of culverts 100 % blocked', 'ARC1': 'Dry soil (ARC I)', 'ARC3': 'Wet soil (ARC III)',
         'FZ': 'Frozen ground', 'C50W': '50 % blocked + wet soil'}
BLOCKED = {'C20': 'all', 'C50': 'all', 'C100': 'all', 'CS': 'small', 'C50W': 'all'}
ACCESS = {'hospital': 30.0, 'fire_station': 8.0, 'police': 4.0}


def access(d):
    """cascade.py outdir on a temp copy with the TAB_BOARD thresholds."""
    import resilience as RS, cascade as CA
    RS.ACCESS_MIN.update(ACCESS)
    t = tempfile.mkdtemp(); p = f'{d}/segments.geojson'
    if os.path.exists(p): shutil.copy(p, t)
    else:
        with gzip.open(p + '.gz') as a, open(f'{t}/segments.geojson', 'wb') as b: shutil.copyfileobj(a, b)
    shutil.copy(f'{d}/summary.json', t); CA.from_outdir(t)
    C = json.load(open(f'{t}/cascade.json')); shutil.rmtree(t); return C


def km(R, ids): return sum((R['seg'][s]['properties'].get('length_m') or 0) for s in ids) / 1000


def pools(O, B, XY):
    meta = O['meta']; res = meta['res_m']; x0, y0, x1, y1 = meta['box']; ny, nx = O['Z'].shape
    yy, xx = np.mgrid[0:ny, 0:nx]; kp, kc = int(W.POOL_M // res), max(1, int(W.CREST_M // res)); out = []
    for x, y in XY:
        r0, c0 = int((y1 - y) // res), int((x - x0) // res)
        crest = float(O['ZC'][max(0, r0 - kc):r0 + kc + 1, max(0, c0 - kc):c0 + kc + 1].max())
        sl = (slice(max(0, r0 - kp), r0 + kp + 1), slice(max(0, c0 - kp), c0 + kp + 1))
        disk = (yy[sl] - r0) ** 2 + (xx[sl] - c0) ** 2 <= kp * kp; row = dict(crest_m=round(crest, 2))
        for t, D in (('base', O), ('blocked', B)):
            m = disk & (D['H'][sl] >= W.WET_M) & (D['Z'][sl] < crest)
            row[t] = float((D['Z'][sl] + D['H'][sl])[m].max()) if m.any() else None
        out.append(row)
    return out


def inspection(G, rid, tr, town_of):
    O, B = G['B'], G[rid]; box = tuple(O['meta']['box'])
    X = json.load(open(f'{ROOT}/docs/network/crossings_all.json')); C = X['columns']
    rows = [dict(zip(C, r)) for r in X['rows'] if r[C.index('lon')] is not None]
    xs, ys = tr.transform([r['lon'] for r in rows], [r['lat'] for r in rows]); x0, y0, x1, y1 = box
    src = open(f'{ROOT}/sim/colab/w9_lisflood.py').read(); ns = {'np': np}
    exec(src[src.index('def is_bridge'):src.index('def block_crossings')], ns); exec(src[src.index('def small_third'):src.index('def partial_block')], ns)
    keep = ns['small_third'](rows, xs, ys, box) if BLOCKED[rid] == 'small' else None
    sel = [(r, x, y) for r, x, y in zip(rows, xs, ys) if x0 <= x < x1 and y0 <= y < y1 and not ns['is_bridge'](r) and (keep is None or r['id'] in keep)]
    P = pools(O, B, [(x, y) for _, x, y in sel]); L = []
    for (r, x, y), p in zip(sel, P):
        if p['blocked'] is None: continue
        ob = max((p['base'] or -1e9) - p['crest_m'], 0.0); bb = max(p['blocked'] - p['crest_m'], 0.0)
        L.append(dict(id=r['id'], lon=round(r['lon'], 5), lat=round(r['lat'], 5), road=r.get('road') or '', stream=r.get('stream') or '',
                      town=town_of(x, y), naacc_condition=(r.get('condition') if r.get('condition') not in (None, 'nan', 'No data', 'Unknown') else 'not assessed'),
                      inlet_blockage=(r.get('inlet_blockage') if r.get('inlet_blockage') not in (None, 'nan') else None),
                      span_m=r.get('span_m'), rise_m=r.get('rise_m'), crest_m=p['crest_m'],
                      over_crest_base_m=round(ob, 2), over_crest_blocked_m=round(bb, 2), added_over_crest_m=round(bb - ob, 2),
                      pool_rise_m=round(p['blocked'] - p['base'], 2) if p['base'] is not None else None))
    L.sort(key=lambda d: (-d['added_over_crest_m'], -(d['pool_rise_m'] or 0)))
    return dict(n_blocked=len(sel), n_overtopped_blocked=sum(1 for d in L if d['over_crest_blocked_m'] > 0), top=L[:10])


def main():
    from pyproj import Transformer
    from scipy.spatial import cKDTree
    tr = Transformer.from_crs(4326, 26986, always_xy=True)
    runs = {i: PE.load_run(f'{RUNS}/{i}') for i in ORDER if os.path.exists(f'{RUNS}/{i}/summary.json')}
    if 'B' not in runs: raise SystemExit('base missing')
    # town per crossing: nearest base segment's town
    sxy, stown = [], []
    for f in runs['B']['seg'].values():
        xy = PE.seg_xy(f, tr); sxy.append(xy.mean(0)); stown.append((f['properties'].get('town') or '').title())
    KT = cKDTree(np.array(sxy)); town_of = lambda x, y: stown[KT.query([x, y])[1]]
    # internal check (reports / DPW), as PARAMETRIC.md
    M = json.load(open(PE.MATCH))['matches']
    REP = {k: v['segs'] for k, v in M.items() if k.startswith('labels_sep2023_leominster.csv') and v['segs']}
    DPW = {k.split(':')[1]: v['segs'] for k, v in M.items() if 'dpw' in k and v['segs']}
    B = runs['B']; FB = PE.flagged(B); rows = []; casc = {}
    for i, R in runs.items():
        C = access(f'{RUNS}/{i}'); casc[i] = C; pk = C['totals']['peak']; s = C['series']
        F = PE.flagged(R); a = np.nansum(s['pop_lost_any']); dry = np.nansum(s['pop_lost_dry_segment'])
        ipk = int(np.nanargmax(s['pop_lost_any'])) if len(s['pop_lost_any']) else 0
        rows.append(dict(id=i, scenario=LABEL[i], closed_any=len(F), closed_any_km=round(km(R, F), 1),
                         closed_peak=pk.get('closed_n'), closed_peak_km=round(float(np.nanmax(s['closed_km'])), 1) if s.get('closed_km') else None,
                         closed_peak_h=pk.get('closed_h'),
                         pop_lost_any=pk.get('pop_lost_any'), pop_lost_hospital=pk.get('pop_lost_hospital'), pop_lost_fire=pk.get('pop_lost_fire_station'),
                         pop_lost_police=pk.get('pop_lost_police'), pop_isolated=pk.get('pop_isolated'),
                         pop_lost_dry_at_peak=int(s['pop_lost_dry_segment'][ipk]) if len(s['pop_lost_any']) else None,
                         dry_share_person_hours=round(float(dry / a), 3) if a else None,
                         delay_peak_vehh_per_h=pk.get('delay_vehh_per_h'), delay_total_vehh=(C['totals'].get('vehicle_hours') or {}).get('total'),
                         reports_hit=sum(1 for v in REP.values() if set(v) & F), reports=len(REP),
                         dpw_hit=sum(1 for v in DPW.values() if set(v) & F), dpw=len(DPW),
                         newly_closed=len(F - FB), no_longer_closed=len(FB - F)))
    b = rows[0]
    for r in rows:
        for k in ('closed_any_km', 'closed_peak_km', 'pop_lost_any', 'delay_total_vehh'):
            if r.get(k) is not None and b.get(k): r[f'd_{k}_pct'] = round(100 * (r[k] - b[k]) / b[k], 1)
    out = dict(made_by='proto/parametric_clean_eval.py', prereg='docs/proto/phase1/PARAMETRIC_CLEAN_PREREG.md', access_min=ACCESS,
               segments_in_box=B['S']['segments_in_box'], rows=rows)
    # crest readout and inspection lists
    G = {i: PT.grids(i) for i in runs if os.path.exists(f'{RUNS}/{i}/zz_cm.npz')}
    if 'B' in G:
        box = tuple(G['B']['meta']['box'])
        out['crest'] = {i: PT.crest_pair(G['B'], G[i], PT.crossings(tr, box, BLOCKED[i]), tr) for i in BLOCKED if i in G}
        out['inspection'] = {i: inspection(G, i, tr, town_of) for i in ('C100', 'CS', 'C50W') if i in G}
        if 'C100' in out['inspection']:
            top = [d['id'] for d in out['inspection']['C100']['top']]
            other = set()
            for j in ('CS', 'C50W'):
                if j in out['inspection']: other |= {d['id'] for d in out['inspection'][j]['top']}
            t2 = json.load(open(f'{PH}/parametric_t2.json')).get('culvert_priority', {}).get('t2_c100', {}).get('top', [])
            t2ids = {d['id'] for d in t2}
            for d in out['inspection']['C100']['top']:
                d['also_top_C50W'] = d['id'] in {x['id'] for x in out['inspection'].get('C50W', {}).get('top', [])}
                d['also_top_CS'] = d['id'] in {x['id'] for x in out['inspection'].get('CS', {}).get('top', [])}
                d['in_16nov_t2_list'] = d['id'] in t2ids
            n = sum(1 for i in top if i in other or i in t2ids)
            out['inspection_robust'] = dict(n_confirmed=n, rule='>= 6 of 10 also in CS / C50W top 10 or the 16 Nov T2 list', robust=n >= 6)
    json.dump(out, open(OUTJ, 'w'), indent=1)
    keys = [k for k in rows[0] if k not in ('scenario',)]
    with open(OUTC, 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=['id', 'scenario'] + [k for k in keys if k != 'id'] + sorted({k for r in rows for k in r if k.startswith('d_')} - set(keys)))
        w.writeheader(); [w.writerow(r) for r in rows]
    for r in rows: print({k: r[k] for k in ('id', 'closed_any', 'closed_any_km', 'closed_peak', 'pop_lost_any', 'delay_total_vehh', 'reports_hit', 'dpw_hit')})
    return out


if __name__ == '__main__':
    main()
