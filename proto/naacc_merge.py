"""Join NAACC road-stream crossing surveys (naacc.org Data Center exports, Massachusetts) onto docs/network/crossings_all.json.

    python proto/naacc_merge.py --naacc <naacc-crossings-detailed.csv> --umass <umass-crossings-detailed.csv> --cond <condition-crossings.csv>

For each survey (newest first per crossing code) within 40 m of an inventory crossing: shape, span/rise (inlet width/height, ft -> m),
material, inlet edge (HDS-5 classes), number of barrels, road fill height, NAACC evaluation, crossing condition, plus from the 2018
condition protocol: condition score (0-1), inlet/outlet blockage, performance problems.  Surveys with no inventory crossing nearby are
appended as new rows (src 'N').  Also writes docs/network/naacc_ma.json (the cleaned surveys).
"""
import os, sys, json, argparse, math
import numpy as np, pandas as pd

FT = 0.3048
SHAPE = {'Round Culvert': 'circular', 'Box Culvert': 'box', 'Pipe Arch/Elliptical Culvert': 'pipe_arch', 'Open Bottom Arch Bridge/Culvert': 'arch_open',
         'Box/Bridge with Abutments': 'bridge', 'Bridge with Side Slopes': 'bridge', 'Bridge with Abutments and Side Slopes': 'bridge', 'Ford': None}
INLET = {'Headwall': 'headwall', 'Headwall and Wingwalls': 'headwall', 'Wingwalls': 'headwall', 'Projecting': 'projecting', 'Mitered to Slope': 'mitered',
         'Flared End Section': 'mitered', 'Other': None, 'None': None}
MAT = {'Concrete': 'concrete', 'Metal': 'metal', 'Plastic': 'plastic', 'Combination': 'other', 'Rock/Stone': 'stone', 'Wood': 'other'}

def num(v, scale=1.0):
    try: v = float(v)
    except Exception: return None
    return None if (v < 0 or math.isnan(v)) else round(v * scale, 3)

def clean_naacc(path):
    d = pd.read_csv(path, low_memory=False, encoding='latin-1')
    d['date'] = pd.to_datetime(d['Date_Observed'], errors='coerce'); d = d.sort_values('date', ascending=False)
    rows = {}
    for _, r in d.iterrows():
        code = r['Crossing_Code']
        if code in rows:            # newest survey wins; add barrels of the same survey as count already given
            continue
        lat, lon = num(r['GIS_Latitude']), r['GIS_Longitude']
        try: lon = float(lon)
        except Exception: continue
        if lat is None or math.isnan(lon): continue
        rows[code] = dict(code=code, lon=lon, lat=lat, src='NAACC', date=str(r['Date_Observed']), road=r.get('Road'), stream=r.get('Stream_Name'), town=r.get('Town'),
                          xtype=r.get('Crossing_Type'), shape=SHAPE.get(str(r.get('Inlet_Structure_Type')).strip()), span_m=num(r.get('Inlet_Width'), FT),
                          rise_m=num(r.get('Inlet_Height'), FT), material=MAT.get(str(r.get('Material')).strip()), inlet=INLET.get(str(r.get('Inlet_Type')).strip()),
                          n_barrels=int(num(r.get('Number_Of_Culverts')) or 1), fill_m=num(r.get('Road_Fill_Height'), FT), slope_pct=num(r.get('Slope_Percent')),
                          length_m=num(r.get('Crossing_Structure_Length'), FT), evaluation=r.get('Evaluation'), condition=r.get('Crossing_Condition'),
                          openness=num(r.get('Inlet_Openness')), comment=str(r.get('Crossing_Comment') or '')[:200])
    return rows

def clean_umass(path):
    d = pd.read_csv(path, low_memory=False, encoding='latin-1'); out = {}
    for _, r in d.iterrows():
        code = r['Crossing_Code']
        try: lat, lon = float(r['GIS_Latitude']), float(r['GIS_Longitude'])
        except Exception: continue
        if math.isnan(lat) or math.isnan(lon) or code in out: continue
        out[code] = dict(code=code, lon=lon, lat=lat, src='UMass', date=str(r.get('Date_Observed')), road=r.get('Road'), stream=r.get('Stream_Name'), town=r.get('Town'),
                         xtype=r.get('Crossing_Type'), rise_m=num(r.get('Structure_Height'), FT), evaluation=r.get('Evaluation'), condition=r.get('Crossing_Condition'),
                         comment=str(r.get('Comment') or '')[:200])
    return out

def clean_cond(path):
    d = pd.read_csv(path, low_memory=False, encoding='latin-1'); out = {}
    for _, r in d.iterrows():
        code = r['Crossing_Code']
        if code in out: continue
        out[code] = dict(cond_score=num(r.get('Condition_Score')), inlet_blockage=str(r.get('Inlet_Blockage') or '').strip() or None,
                         outlet_blockage=str(r.get('Outlet_Blockage') or '').strip() or None, perf_problems=str(r.get('Performance_Problems') or '').strip()[:120] or None,
                         cond_material=r.get('Culvert_Material'), cond_date=str(r.get('Date_Observed')))
    return out

def main(a):
    from pyproj import Transformer
    from scipy.spatial import cKDTree
    S = clean_naacc(a.naacc); U = clean_umass(a.umass) if a.umass else {}; C = clean_cond(a.cond) if a.cond else {}
    for code, extra in C.items():
        if code in S: S[code].update(extra)
    for code, u in U.items():
        if code not in S: S[code] = u
    surveys = list(S.values()); tr = Transformer.from_crs(4326, 26986, always_xy=True)
    X = json.load(open(a.crossings)); Ccol = X['columns']; R = X['rows']
    for c in ('naacc_code', 'naacc_date', 'condition', 'cond_score', 'inlet_blockage', 'perf_problems', 'slope_pct', 'length_m', 'naacc_comment'):
        if c not in Ccol: Ccol.append(c); [r.append(None) for r in R]
    ix = {c: i for i, c in enumerate(Ccol)}
    xx, yy = tr.transform([r[ix['lon']] for r in R], [r[ix['lat']] for r in R]); tree = cKDTree(np.column_stack([xx, yy]))
    sx, sy = tr.transform([s['lon'] for s in surveys], [s['lat'] for s in surveys]); d, j = tree.query(np.column_stack([sx, sy]))
    matched = added = 0; used = set()
    for k, s in enumerate(surveys):
        if d[k] <= a.radius and j[k] not in used:
            row = R[j[k]]; used.add(j[k]); matched += 1
        else:
            row = [None] * len(Ccol); row[ix['lon']], row[ix['lat']] = s['lon'], s['lat']; row[ix['src']] = 'N'; row[ix['id']] = 'naacc:' + str(s['code']); R.append(row); added += 1
        for f_src, f_dst in (('shape', 'shape'), ('span_m', 'span_m'), ('rise_m', 'rise_m'), ('material', 'material'), ('inlet', 'inlet'), ('n_barrels', 'n_barrels'),
                             ('fill_m', 'fill_m'), ('evaluation', 'naacc_eval'), ('road', 'road'), ('stream', 'stream')):
            if s.get(f_src) is not None and (row[ix[f_dst]] is None or f_src in ('shape', 'span_m', 'rise_m', 'inlet', 'n_barrels', 'fill_m')): row[ix[f_dst]] = s[f_src]
        row[ix['naacc_code']] = s['code']; row[ix['naacc_date']] = s.get('date'); row[ix['condition']] = s.get('condition'); row[ix['cond_score']] = s.get('cond_score')
        row[ix['inlet_blockage']] = s.get('inlet_blockage'); row[ix['perf_problems']] = s.get('perf_problems'); row[ix['slope_pct']] = s.get('slope_pct')
        row[ix['length_m']] = s.get('length_m'); row[ix['naacc_comment']] = s.get('comment') or None
    X['columns'] = Ccol; X['rows'] = R
    X.setdefault('sources', {})['naacc'] = dict(note='NAACC Data Center exports (naacc.org), Massachusetts: NAACC after 6/1/2015 (detailed), UMass Stream Continuity 2005-2017 (Leominster, Fitchburg), Culvert Condition 2018 protocol', surveys=len(surveys), matched=matched, added=added, radius_m=a.radius)
    json.dump(X, open(a.crossings, 'w'), separators=(',', ':'), default=str)
    json.dump(dict(columns=list(surveys[0].keys()) if surveys else [], surveys=surveys), open(a.out, 'w'), separators=(',', ':'), default=str)
    geo = sum(1 for r in R if r[ix['rise_m']]); print(f'surveys {len(surveys)}, matched {matched}, added {added}; crossings with rise now {geo} of {len(R)}')

if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('--naacc', required=True); ap.add_argument('--umass'); ap.add_argument('--cond'); ap.add_argument('--radius', type=float, default=40.0)
    ap.add_argument('--crossings', default='docs/network/crossings_all.json'); ap.add_argument('--out', default='docs/network/naacc_ma.json')
    main(ap.parse_args())
