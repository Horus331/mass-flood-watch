"""Compare rain-forcing variants on the catalogue storms (docs/proto/rain/RAIN.md).

    python proto/rain/rain_compare.py     -> docs/proto/rain/rain.json (runs part) + markdown tables on stdout

Runs: .github/workflows/rain_test.yml mode=sim -> docs/proto/rain/runs/<storm>_<variant>/ (all 20 m, catalogue box and hours,
LF_PARITY=1, LF_LOSS=cn LF_CN_SCALE=0.91 LF_INFIL_MMH=2). Variant 'hourly' = the baseline (MRMS Pass2 hourly records),
'dt5' / 'dt15' = LF_RAIN_DT, 'gauge' = gauge-adjusted (if run).
Per run: labelled sites caught (depth rule, p_close >= 0.5) / labelled, flagged share, lift (recall / flagged share), gauge rises
(model vs observed), mean |rise error|, mean |peak timing error| (gap-aware interval), report points wet >= 0.3 m (validate_points).
"""
import json, os, sys, glob

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')
sys.path.insert(0, os.path.join(ROOT, 'proto'))
from dcia_compare import read  # noqa: E402

RUNS = f'{ROOT}/docs/proto/rain/runs'
VERDICT = dict(
    subhourly_default=False,
    subhourly='keep opt-in (LF_RAIN_DT=5). It works as intended: totals kept exactly, the radar timing matches ASOS 1-min gauges better than an even split, and the '
              'peak 15-min forcing rate rises 1.3-2.6x (median, Pass2 >= 5 mm/h). But on 20 m LISFLOOD-FP it moves peak depths by ~1 cm on average, catches no '
              'additional labelled site on any of the 7 storms, raises the flagged share slightly (lift down) and does not improve gauge rise or peak timing.',
    gauge_default=False,
    gauge='keep opt-in (LF_RAIN_GAUGE=idw), hindcast only. Daily CoCoRaHS/COOP gauges are dense enough (12-33 per storm within the box + 0.1 deg) and show '
          'Pass2 under-catch on aug2021 (gauge/Pass2 1.32) and jul2021 (1.22); adjusting catches 3 more sites on aug2021 and 1 on jul2021 and fixes the Millbury '
          'rise, but over-shoots Northbridge, lowers lift on the 3 storms that already caught sites (aug2023, sep2023, aug2021), and the daily reports arrive the next morning, so it cannot be used live. '
          'Hourly gauges (ASOS 1-min, USGS) are too sparse (0-2 in a box) for a local hourly adjustment; they agree with Pass2 to 0.97 overall '
          'but Pass2 under-reads the >= 25 mm/h hours (0.76, n 12).')
STORMS = [('jul2023', 'flash'), ('aug2023b', 'flash'), ('sep2022', 'flash'), ('aug2023', 'flash'), ('sep2023', 'good'), ('aug2021', 'good'), ('jul2021', 'good')]


def one(d):
    r = read(d)
    if r is None: return None
    if os.path.exists(f'{d}/score.json'):
        sc = json.load(open(f'{d}/score.json'))
        r['peak_timing_abs_h'] = sc.get('mean_abs_peak_timing_error_interval_h'); r['rise50_abs_h'] = sc.get('mean_abs_rise50_error_h')
        r['gauges'] = [dict(site=g['site'], obs=g.get('obs_rise_m'), model=g.get('model_rise_m'), peak_err_h=g.get('peak_timing_error_interval_h')) for g in sc.get('gauges', [])]
    if os.path.exists(f'{d}/points.json'):
        s = json.load(open(f'{d}/points.json')).get('summary', {})
        r['reports_hit30'] = {k: s[k].get('hit_30') for k in ('LSR', 'labels', 'all', 'random_road_points') if k in s}
    if os.path.exists(f'{d}/flood_meta.json'):
        m = json.load(open(f'{d}/flood_meta.json')); sub = m.get('inputs', {}).get('rain_subhourly')
        r['runtime_s'] = m.get('runtime_s')
        if sub: r['subhourly'] = dict(dt=sub.get('dt_min'), hours_uniform=sub.get('hours_uniform'), probe_units=(sub.get('probe') or {}).get('units'),
                                     file=sub.get('file'))
    return r


def main():
    out = {}
    variants = sorted({os.path.basename(p).split('_', 1)[1] for p in glob.glob(f'{RUNS}/*_*')})
    for sid, kind in STORMS:
        e = dict(kind=kind)
        for v in variants: e[v] = one(f'{RUNS}/{sid}_{v}')
        out[sid] = e

    def cell(r):
        if not r: return '–'
        g = ', '.join(f"{x['model']:.2f}/{x['obs']:.2f}" for x in r.get('gauges', []) if x.get('model') is not None and x.get('obs') is not None)
        pt = r.get('peak_timing_abs_h')
        return (f"{r['caught']}/{r['n']} · {100 * (r['flagged_share'] or 0):.2f}% · {r['lift'] or 0:.1f} · rise {g or '–'} · "
                f"peak {'–' if pt is None else f'{pt:.1f} h'}")
    print('cell: caught/labelled · flagged share · lift · gauge rise model/obs (m) · mean |peak timing error|\n')
    print('| storm | ' + ' | '.join(variants) + ' |'); print('|---' * (len(variants) + 1) + '|')
    for sid, e in out.items(): print(f'| {sid} ({e["kind"]}) | ' + ' | '.join(cell(e.get(v)) for v in variants) + ' |')
    AGG = {}
    for grp in ('flash', 'good', 'all'):
        for v in variants:
            rs = [e[v] for e in out.values() if (grp == 'all' or e['kind'] == grp) and e.get(v)]
            if not rs: continue
            ae = [r['abs_rise_err_m'] for r in rs if r.get('abs_rise_err_m') is not None]; pt = [r['peak_timing_abs_h'] for r in rs if r.get('peak_timing_abs_h') is not None]
            fl = sum(r['n_flagged'] or 0 for r in rs); seg = sum((r['n_flagged'] or 0) / r['flagged_share'] for r in rs if r['flagged_share'])
            AGG.setdefault(grp, {})[v] = dict(storms=len(rs), caught=sum(r['caught'] for r in rs), labels=sum(r['n'] or 0 for r in rs), n_flagged=fl,
                                              mean_flagged_share=round(sum(r['flagged_share'] or 0 for r in rs) / len(rs), 4),
                                              pooled_lift=round((sum(r['caught'] for r in rs) / max(sum(r['n'] or 0 for r in rs), 1)) / (fl / seg), 2) if fl and seg else None,
                                              mean_abs_rise_err_m=round(sum(ae) / len(ae), 3) if ae else None,
                                              mean_abs_peak_timing_h=round(sum(pt) / len(pt), 2) if pt else None)
            print(f'{grp} {v}: ' + ', '.join(f'{k} {x}' for k, x in AGG[grp][v].items()))
    out['_aggregate'] = AGG
    json.dump(out, open(f'{ROOT}/docs/proto/rain/runs.json', 'w'), indent=1)
    # docs/proto/rain/rain.json: the headline numbers of RAIN.md (gauge check + runs), the verdict is in VERDICT
    gj = json.load(open(f'{ROOT}/docs/proto/rain/gauges.json')) if os.path.exists(f'{ROOT}/docs/proto/rain/gauges.json') else {}
    fac = json.load(open(f'{ROOT}/docs/proto/rain/gauge_factors.json')) if os.path.exists(f'{ROOT}/docs/proto/rain/gauge_factors.json') else {}
    G = {sid: dict(hourly_gauges=g.get('hourly', {}).get('n_gauges'), hourly_in_box=g.get('hourly', {}).get('n_in_box'), hourly_mrms_over_gauge=g.get('hourly', {}).get('all', {}).get('ratio'),
                   daily_gauges=g.get('daily', {}).get('n_gauges'), daily_in_box=g.get('daily', {}).get('n_in_box'), daily_mrms_over_gauge=g.get('daily', {}).get('all', {}).get('ratio'),
                   daily_mrms_over_gauge_in_box=g.get('daily', {}).get('in_box', {}).get('ratio'), radar_only_over_pass2=g.get('radar_vs_pass2', {}).get('ratio'),
                   box_max_rate_mmh=g.get('intensity', {}).get('box_max_rate_mmh'), peak_factor_15min_median=g.get('intensity', {}).get('peak_factor_15min_median'),
                   asos_timing=[dict(id=t['id'], peak15_mmh=t['peak15_mmh'], share_mae=t.get('share_mae')) for t in g.get('timing_asos', [])],
                   gauge_factor_mfb=(fac.get(sid) or {}).get('mfb'), gauge_factor_n=(fac.get(sid) or {}).get('n'))
         for sid, g in gj.items() if not sid.startswith('_')}
    runs = {sid: {v: (dict(caught=r['caught'], labels=r['n'], flagged_share=r['flagged_share'], lift=r['lift'], abs_rise_err_m=r.get('abs_rise_err_m'),
                           peak_timing_abs_h=r.get('peak_timing_abs_h'), gauges=r.get('gauges'), reports_hit30=r.get('reports_hit30')) if r else None)
                  for v, r in e.items() if v != 'kind'} for sid, e in out.items() if not sid.startswith('_')}
    json.dump(dict(about='docs/proto/rain/RAIN.md; runs: docs/proto/rain/runs/<storm>_<variant>/ (20 m, LF_PARITY=1, CN x 0.91); gauge check: proto/rain/rain_gauges.py',
                   verdict=VERDICT, pooled_hourly_gauge=gj.get('_pooled'), gauges=G, runs=runs, aggregate=AGG), open(f'{ROOT}/docs/proto/rain/rain.json', 'w'), indent=1)


if __name__ == '__main__':
    main()
