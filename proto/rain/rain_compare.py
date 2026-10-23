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


if __name__ == '__main__':
    main()
