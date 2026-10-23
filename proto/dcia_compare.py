"""Compare runoff-loss variants on the catalogue storms (docs/proto/urban/DCIA.md).

    python proto/dcia_compare.py            -> docs/proto/urban/dcia.json + a markdown table on stdout

Reads the published GPU runs (docs/proto/turing/<id>_<area>_20m, LF_LOSS=cn) and the CPU runs of .github/workflows/loss_test.yml
(docs/proto/urban/dcia/<id>_<variant>/). Per run: labels caught / labelled and flagged share from
summary.json checks.labels_segments.depth_rule (flagged = p_close >= 0.5), lift = recall / flagged share (lift_naive),
gauge rise bias (score.json mean_rise_bias_m), effective rain share from the w9 log.
"""
import json, os, re, glob

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
STORMS = [('jul2023', 'worcester', 'miss'), ('aug2023b', 'millbury', 'miss'), ('sep2022', 'webster', 'miss'), ('aug2023', 'metrowest', 'miss'),
          ('sep2023', 'leominster', 'good'), ('aug2021', 'worcester', 'good'), ('jul2021', 'worcester', 'good'), ('sep2021', 'worcester', 'good'),
          ('aug2026', 'leominster', 'good')]


def read(d):
    if not os.path.exists(f'{d}/summary.json'): return None
    s = json.load(open(f'{d}/summary.json')); dr = s.get('checks', {}).get('labels_segments', {}).get('depth_rule', {})
    a = dr.get('all', {}); r = dict(n=a.get('n'), caught=round((a.get('recall') or 0) * (a.get('n') or 0)), recall=a.get('recall'),
                                     flagged_share=dr.get('flagged_share'), n_flagged=dr.get('n_flagged'), lift=a.get('lift_naive'), lift_adj=a.get('lift'))
    r['sites'] = {x['id']: dict(depth_m=x.get('depth_m'), p_depth=x.get('p_depth'), hit=bool(x.get('hit'))) for x in s.get('checks', {}).get('labels_segments', {}).get('sites', [])}
    if os.path.exists(f'{d}/score.json'):
        sc = json.load(open(f'{d}/score.json')); r['rise_bias_m'] = sc.get('mean_rise_bias_m'); r['abs_rise_err_m'] = sc.get('mean_abs_rise_error_m')
        r['gauges'] = [dict(site=g['site'], obs=g.get('obs_rise_m'), model=g.get('model_rise_m')) for g in sc.get('gauges', [])]
    for f in (f'{d}/w9_stdout.txt', f'{d}/_logs/w9_stdout.txt'):
        if os.path.exists(f):
            m = re.findall(r'effective rain \((CN[^)]*)\) mean (\d+) mm of (\d+) mm \((\d+)%\)', open(f, errors='replace').read())
            if m: r['eff_rain_pct'] = int(m[-1][3]); r['rain_mean_mm'] = int(m[-1][2])
    if os.path.exists(f'{d}/hmax_stats.json'): r.update(json.load(open(f'{d}/hmax_stats.json')))
    return r


def main():
    out = {}
    variants = sorted({os.path.basename(p).split('_', 1)[1] for p in glob.glob(f'{ROOT}/docs/proto/urban/dcia/*_*')})
    for sid, area, kind in STORMS:
        e = dict(kind=kind, gpu_cn=read(f'{ROOT}/docs/proto/turing/{sid}_{area}_20m'))
        for v in variants: e[v] = read(f'{ROOT}/docs/proto/urban/dcia/{sid}_{v}')
        out[sid] = e
    cols = ['gpu_cn'] + variants
    def cell(r):
        if not r: return '–'
        b = r.get('rise_bias_m'); return f"{r['caught']}/{r['n']} · {100 * (r['flagged_share'] or 0):.2f}% · {r['lift'] or 0:.1f} · {'' if b is None else f'{b:+.2f}'}"
    print('| storm | ' + ' | '.join(cols) + ' |'); print('|---' * (len(cols) + 1) + '|')
    for sid, e in out.items(): print(f'| {sid} ({e["kind"]}) | ' + ' | '.join(cell(e[c]) for c in cols) + ' |')
    AGG = {}
    for grp in ('miss', 'good'):
        for c in cols:
            rs = [e[c] for e in out.values() if e['kind'] == grp and e.get(c)]
            if not rs: continue
            ae = [r['abs_rise_err_m'] for r in rs if r.get('abs_rise_err_m') is not None]; bi = [r['rise_bias_m'] for r in rs if r.get('rise_bias_m') is not None]
            agg = dict(storms=len(rs), caught=sum(r['caught'] for r in rs), labels=sum(r['n'] for r in rs), n_flagged=sum(r['n_flagged'] for r in rs),
                       mean_flagged_share=round(sum(r['flagged_share'] for r in rs) / len(rs), 4), mean_lift=round(sum(r['lift'] or 0 for r in rs) / len(rs), 2),
                       pooled_lift=round((sum(r['caught'] for r in rs) / sum(r['n'] for r in rs)) / (sum(r['n_flagged'] for r in rs) / sum(r['n_flagged'] / r['flagged_share'] for r in rs if r['flagged_share'])), 2),
                       mean_rise_bias_m=round(sum(bi) / len(bi), 3) if bi else None, mean_abs_rise_err_m=round(sum(ae) / len(ae), 3) if ae else None)
            AGG.setdefault(grp, {})[c] = agg
            print(f'{grp} {c}: ' + ', '.join(f'{k} {v}' for k, v in agg.items()))
    out['_aggregate'] = AGG; json.dump(out, open(f'{ROOT}/docs/proto/urban/dcia.json', 'w'), indent=1)


if __name__ == '__main__':
    main()
