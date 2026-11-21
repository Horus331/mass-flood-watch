"""Antecedent water table before each non-locked District 3 catalogue storm (descriptive; Paper 2 groundwater section).

For every well in scout.json: the full daily record of depth to water (USGS dv, parameter 72019). For every storm: the mean depth over the
3 days before t0, expressed as a percentile of the same well's record for that calendar month (low depth = wet = high percentile is
inverted: we report the share of the month's record that was DEEPER, so 90 = wetter than 90 % of that month's history).
Per storm: the median of that wetness percentile over wells within 30 km of the storm box centre, and over the 3 nearest wells.
Then rank correlation with the model's gauge-rise ratio (parity/bias_by_storm.json). Nothing enters the model (T4 C stays stopped).
    python proto/gw_antecedent.py   (GitHub workflow gw_scout.yml with script=gw_antecedent.py; USGS is not reachable from the shell)
"""
import json, math, os, sys, datetime as dt
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gw_scout import get, UA      # same retrying fetch
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); G = f'{ROOT}/docs/proto/groundwater'


def storm_t0():
    import re
    src = open(f'{ROOT}/sim/colab/w9_lisflood.py').read()
    out = {}
    for m in re.finditer(r"'(\w+)':\s*dict\(t0='([0-9T:\-]+)Z'", src): out[m.group(1)] = m.group(2)
    return out


def dv(site):
    u = f'https://waterservices.usgs.gov/nwis/dv/?format=json&sites={site}&parameterCd=72019&startDT=1990-01-01&endDT=2026-11-01&siteStatus=all'
    r = get(u)
    if r is None or r.status_code != 200: return {}
    try:
        ts = r.json()['value']['timeSeries']
    except Exception:
        return {}
    out = {}
    for t in ts:
        for v in t['values'][0]['value']:
            try: out[v['dateTime'][:10]] = float(v['value'])
            except ValueError: pass
    return out


def main():
    from scipy.stats import spearmanr
    S = json.load(open(f'{G}/scout.json')); W = S['wells']
    B = {b['storm']: b for b in json.load(open(f'{ROOT}/docs/proto/parity/bias_by_storm.json'))['storms']}
    cat = {e['id']: e for e in json.load(open(f'{ROOT}/docs/proto/obs/catalog.json'))['events'] if e.get('id') in B}
    T0 = {k: v['t0'] for k, v in cat.items()}; T0.update({k: v for k, v in storm_t0().items() if k in B and k not in T0}); rec = {}
    for w in W:
        d = dv(w['site']); rec[w['site']] = d; print(w['name'], len(d), 'days', flush=True)
    rows = []
    for sid, b in B.items():
        if sid not in T0: continue
        t0 = dt.date.fromisoformat(T0[sid][:10]); c = cat.get(sid, {})
        bb = c.get('bbox_lonlat'); lon, lat = ((bb[0] + bb[2]) / 2, (bb[1] + bb[3]) / 2) if bb else (None, None)
        wet = []
        for w in W:
            d = rec[w['site']]
            pre = [d.get(str(t0 - dt.timedelta(days=k))) for k in (1, 2, 3)]; pre = [p for p in pre if p is not None]
            hist = [v for k, v in d.items() if int(k[5:7]) == t0.month and k[:4] != str(t0.year)]
            if not pre or len(hist) < 60: continue
            pct = 100 * float(np.mean(np.array(hist) > np.mean(pre)))
            dist = 6371 * math.acos(min(1, math.sin(math.radians(lat)) * math.sin(math.radians(w['lat'])) + math.cos(math.radians(lat)) * math.cos(math.radians(w['lat'])) * math.cos(math.radians(lon - w['lon'])))) if lat is not None else None
            wet.append((dist, pct, w['name']))
        wet.sort(key=lambda z: (z[0] is None, z[0]))
        near30 = [p for dd, p, _ in wet if dd is not None and dd <= 30]
        rows.append(dict(storm=sid, t0=T0[sid], wells_with_record=len(wet), wetness_pct_median_30km=round(float(np.median(near30)), 1) if near30 else None,
                         wells_30km=len(near30), wetness_pct_nearest3=round(float(np.median([p for _, p, _ in wet[:3]])), 1) if wet else None,
                         nearest=[(n, round(dd, 1) if dd else None, round(p, 1)) for dd, p, n in wet[:3]],
                         ratio_median=b.get('ratio_median'), bias_mean_m=b.get('bias_mean_m'), recall3=(b['hits3'] / b['sites']) if b.get('sites') else None))
    def rho(a, k):
        z = [(r[a], r[k]) for r in rows if r[a] is not None and r[k] is not None]
        return dict(n=len(z), spearman=round(float(spearmanr(*zip(*z))[0]), 2) if len(z) > 4 else None)
    out = dict(made_by='proto/gw_antecedent.py', note='descriptive only; nothing enters the model', storms=rows,
               correlations={'wetness30_vs_ratio': rho('wetness_pct_median_30km', 'ratio_median'), 'wetness30_vs_bias': rho('wetness_pct_median_30km', 'bias_mean_m'),
                             'wetness30_vs_recall3': rho('wetness_pct_median_30km', 'recall3'), 'nearest3_vs_ratio': rho('wetness_pct_nearest3', 'ratio_median')})
    json.dump(out, open(f'{G}/antecedent.json', 'w'), indent=1); print(json.dumps(out['correlations'], indent=1))


if __name__ == '__main__':
    main()
