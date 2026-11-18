"""Gauge-rise bias against storm size, all non-locked District 3 catalogue storms (parity runs, operational physics), and how it relates to
each storm's site recall. Descriptive only (Paper 1 review M8): no model change, nothing fitted.

    python proto/bias_by_storm.py  ->  docs/proto/parity/bias_by_storm.json (table in BIAS_BY_STORM.md)
Rain per storm from the run's own features table: box mean and 99th percentile of segment storm totals, max segment peak-hour rain.
Recall from docs/proto/obs/round2/score_round2.json (parity runs, box domain, top 3 %, round-2 labels)."""
import glob, json, os
import numpy as np, pandas as pd
from scipy.stats import spearmanr
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); P = f'{ROOT}/docs/proto'


def main():
    R = json.load(open(f'{P}/obs/round2/score_round2.json'))['runs']
    rec = {}
    for r in R:
        if r.get('group', '').startswith('parity') or 'parity' in str(r.get('run', '')):
            b = r['domains']['box']; s = b['shares']['0.03']
            rec[os.path.basename(r['run'].rstrip('/'))] = dict(role=r.get('role'), sites=b['n_sites'], hits3=s['site_hits'], chance3=s['chance_recall'],
                                                              rule_hits=b['rule']['site_hits'])
    rows = []
    for f in sorted(glob.glob(f'{P}/parity/catalog/*_20m/score.json')):
        run = os.path.basename(os.path.dirname(f)); S = json.load(open(f))
        G = [g for g in S.get('gauges', []) if g.get('obs_rise_m') is not None and g.get('model_rise_m') is not None]
        ft = glob.glob(os.path.dirname(f) + '/features_*.csv*'); fe = pd.read_csv(ft[0], low_memory=False) if ft else None
        rows.append(dict(run=run, storm=run.split('_')[0], gauges=len(G),
                         obs_rise_mean_m=round(float(np.mean([g['obs_rise_m'] for g in G])), 2) if G else None,
                         bias_mean_m=round(float(np.mean([g['rise_error_m'] for g in G])), 2) if G else None,
                         ratio_median=round(float(np.median([g['model_rise_m'] / g['obs_rise_m'] for g in G if g['obs_rise_m'] > 0.05])), 2) if G else None,
                         rain_total_mean_mm=round(float(fe.storm_total_mm.mean()), 1) if fe is not None else None,
                         rain_total_p99_mm=round(float(fe.storm_total_mm.quantile(0.99)), 1) if fe is not None else None,
                         peak1h_max_mm=round(float(fe.peak1h_mm.max()), 1) if fe is not None else None,
                         **rec.get(run, {})))
    D = pd.DataFrame(rows)
    def rho(a, b):
        m = D[[a, b]].dropna(); return dict(n=len(m), spearman=round(float(spearmanr(m[a], m[b])[0]), 2) if len(m) > 3 else None)
    D['recall3'] = D.hits3 / D.sites
    out = dict(made_by='proto/bias_by_storm.py', storms=rows, correlations={
        'ratio_vs_rain_total_p99': rho('ratio_median', 'rain_total_p99_mm'), 'ratio_vs_peak1h_max': rho('ratio_median', 'peak1h_max_mm'),
        'ratio_vs_obs_rise': rho('ratio_median', 'obs_rise_mean_m'), 'recall3_vs_rain_total_p99': rho('recall3', 'rain_total_p99_mm'),
        'recall3_vs_ratio': rho('recall3', 'ratio_median')})
    json.dump(out, open(f'{P}/parity/bias_by_storm.json', 'w'), indent=1, default=float)
    print(D.to_string()); print(json.dumps(out['correlations'], indent=1))


if __name__ == '__main__':
    main()
