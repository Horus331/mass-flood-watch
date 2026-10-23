"""T4: default CN loss (AMC II) vs LF_CN_AMC=auto on the 9 catalogue storms (+ the Worcester aug2021 48 h box), docs/proto/runoff/AMC.md.

    python proto/runoff/amc_compare.py [CAND_DIR OUT_JSON]   -> docs/proto/runoff/amc.json (default: the auto-AMC runs) + markdown tables on stdout
    e.g. python proto/runoff/amc_compare.py docs/proto/runoff/infil0 docs/proto/runoff/infil0.json
    python proto/runoff/amc_compare.py --new16 docs/proto/runoff/new16_infil0 docs/proto/runoff/new16_infil0.json   (secondary OOS check)

Default arm = the T0 parity catalogue as published (docs/proto/parity/catalog/<name>, LF_PARITY=1 LF_CN_SCALE=0.88, CPU, git 37177775),
reused, not rerun (aug2021 / aug2026 were rerun with identical settings and hydraulics to rebuild matches against the current labels,
BASELINE_v2_expanded.md).  Only the explicit pre-registered T4_RUNS are used.  Every candidate run is scored against the CURRENT labels by
taking the label->segment matches from its catalogue counterpart (load_current), so both arms have identical site lists.  Auto arm = the same cases with LF_CN_AMC=auto added (parity_test.yml dest=docs/proto/runoff/runs/<name>), CPU.
Gauges: proto/score.py (score.json of each run).  Closures: proto/score_v2.py score_run on each run and --compare logic (PROTOCOL.md §5,
OOS-7 held-out storms, primary run per storm = <storm>_<area>_20m; worcester_aug2021_48h is reported but is not part of any pool).
"""
import os, sys, json, glob
import numpy as np

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'proto'))
import score_v2 as V  # noqa: E402

BASE = os.path.join(ROOT, 'docs', 'proto', 'parity', 'catalog')
CAND = os.path.join(ROOT, 'docs', 'proto', 'runoff', 'runs')
OUT = os.path.join(ROOT, 'docs', 'proto', 'runoff', 'amc.json')
FOCUS = ('jul2021', 'sep2021')        # Elsa, Ida: the under-predicted gauge rises T4 targets
# The pre-registered T4 set (AMC.md §0): the 9 primary catalogue runs + the Worcester aug2021 48 h box. Explicit, so the 16 label-expansion
# storms added to docs/proto/parity/catalog/ later (BASELINE_v2_expanded.md) do not enter the T4 verdict.
T4_RUNS = ('aug2021_worcester_20m', 'aug2023_metrowest_20m', 'aug2023b_millbury_20m', 'aug2026_leominster_20m', 'jul2021_worcester_20m',
           'jul2023_worcester_20m', 'sep2021_worcester_20m', 'sep2022_webster_20m', 'sep2023_leominster_20m', 'worcester_aug2021_48h')


def load_current(run_dir, storm, ref_dir):
    """Load a run and score it against the CURRENT labels: the label->segment matches are taken from the reference (catalogue) run's
    matches_<storm>.json, which was rebuilt against the current labels (aug2021/aug2026 reruns, BASELINE_v2_expanded.md).  Matching is
    pure geometry (label point vs the road points of the same box at the same resolution), so it is the same for every arm on that box;
    candidate runs made before the label update carry stale matches files, and this replaces them."""
    R = V.load_run(run_dir, storm); Rf = V.load_run(ref_dir, storm)
    if set(R['seg'].tolist()) != set(Rf['seg'].tolist()): raise SystemExit(f'{run_dir}: segment universe differs from {ref_dir}')
    pos = {int(s): i for i, s in enumerate(R['seg'])}          # matches are indices into the run's own segment order: remap by segment id
    R['matches'] = {k: sorted(pos[int(Rf['seg'][i])] for i in v) for k, v in Rf['matches'].items()}
    R['labels'], R['match_src'] = Rf['labels'], 'current labels (' + os.path.relpath(ref_dir, ROOT) + ')'
    return R


def amc_of(d):
    try:
        env = json.load(open(os.path.join(d, 'flood_meta.json')))['inputs']['env']; return env.get('LF_CN_AMC_RESOLVED', env.get('LF_CN_AMC', 'II'))
    except Exception: return None


def gauges(d):
    p = os.path.join(d, 'score.json')
    if not os.path.exists(p): return None
    s = json.load(open(p))
    return dict(mae=s.get('mean_abs_rise_error_m'), bias=s.get('mean_rise_bias_m'), peak_abs_h=s.get('mean_abs_peak_timing_error_interval_h'),
                rise50_abs_h=s.get('mean_abs_rise50_error_h'),
                g=[dict(site=g['site'], name=g.get('name', '')[:40], obs=g.get('obs_rise_m'), model=g.get('model_rise_m'), err=g.get('rise_error_m'),
                        peak_h=g.get('peak_timing_error_interval_h')) for g in s.get('gauges', []) if g.get('obs_rise_m') is not None])


def closure(r):
    b = r['domains']['box']; s3 = b['shares']['0.03']
    return dict(sites=b['n_sites'], hits3=s3['site_hits'], recall3=s3['site_recall'], fss300_3=s3['fss'].get('300', {}).get('fss'),
                rule_share=b['rule']['share'], rule_hits=b['rule']['site_hits'], rule_lift=b['rule']['lift'], pr_auc_site=b['pr_auc']['site'])


def main():
    global CAND, OUT
    args = [a for a in sys.argv[1:] if not a.startswith('--')]; new16 = '--new16' in sys.argv
    if len(args) == 2: CAND, OUT = os.path.join(ROOT, args[0]), os.path.join(ROOT, args[1])
    # --new16: SECONDARY out-of-sample check only (AMC.md §1), never the T4 decision: the 16 label-expansion storms' primary catalogue runs
    names = [f"{c['name']}" for c in (json.load(open(p)) for p in sorted(glob.glob(os.path.join(BASE, '*_20m', 'config.json')))) if c['storm'] in V.NEW16] \
        if new16 else list(T4_RUNS)
    rows, base_runs, cand_runs = [], [], []
    for n in names:
        db, dc = os.path.join(BASE, n), os.path.join(CAND, n)
        if not os.path.exists(os.path.join(dc, 'flood_meta.json')): raise SystemExit(f'missing candidate run {dc}')
        s = json.load(open(os.path.join(db, 'config.json')))['storm']; prim = n == f'{s}_' + n.split('_')[1] + '_20m'
        row = dict(name=n, storm=s, primary=prim, role=('dev' if s in V.DEV else 'heldout-new' if s in V.NEW16 else 'heldout'), amc=amc_of(dc), gauges_base=gauges(db), gauges_auto=gauges(dc))
        try:
            mb = json.load(open(os.path.join(db, 'flood_meta.json'))); mc = json.load(open(os.path.join(dc, 'flood_meta.json')))
            row['git'] = dict(base=mb.get('git_sha'), auto=mc.get('git_sha'))
        except Exception: pass
        rb = V.score_run(V.load_run(db, s)); rc = V.score_run(load_current(dc, s, db))
        rb['primary'] = rc['primary'] = prim; row['closure_base'] = closure(rb); row['closure_auto'] = closure(rc)
        if prim: base_runs.append(rb); cand_runs.append(rc)
        rows.append(row); print(n, row['amc'], row['closure_base']['hits3'], '->', row['closure_auto']['hits3'], flush=True)
    if new16:   # descriptive paired bootstrap on the 16 new storms (pool 'heldout23' restricted to the runs given = NEW16), alpha 0.05, no verdict
        cmp_ = V.compare(dict(runs=base_runs), dict(runs=cand_runs), rule=dict(V.ADOPT, storms='heldout23', alpha=0.05)); cmp_['note'] = 'secondary, not a decision'
    else:
        cmp_ = V.compare(dict(runs=base_runs), dict(runs=cand_runs), rule=dict(V.ADOPT, alpha=0.05 / 4))     # k = 4 T4 variants on OOS-7 (AMC.md §0)
    pools = {}
    for arm, R in (('base', base_runs), ('auto', cand_runs)):
        for nm, st in ((('new16', V.NEW16),) if new16 else (('heldout7', V.HELDOUT), ('dev2', V.DEV), ('all9', V.LOSO9))):
            pl = V.pooled([r for r in R if r['storm'] in st], 'box', boot=500)
            pools[f'{arm}:{nm}'] = dict(recall3=pl['point']['share_0.03']['site_recall'], fss300_3=pl['point']['share_0.03']['fss300'],
                                        rule_recall=pl['point']['rule']['site_recall'], rule_lift=pl['point']['rule']['lift'], n_sites=pl['n_sites'])

    def gstat(sel, arm):
        e = [g['err'] for r in rows if r['primary'] and r['storm'] in sel and r[f'gauges_{arm}'] for g in r[f'gauges_{arm}']['g'] if g['err'] is not None]
        return dict(n=len(e), mae=round(float(np.mean(np.abs(e))), 3) if e else None, bias=round(float(np.mean(e)), 3) if e else None)
    others = tuple(s for s in V.LOSO9 if s not in FOCUS)
    gsets = (('new16', V.NEW16),) if new16 else (('all9', V.LOSO9), ('elsa_ida', FOCUS), ('other7', others))
    gsum = {k: dict(base=gstat(st, 'base'), auto=gstat(st, 'auto')) for k, st in gsets}
    res = dict(made_by='proto/runoff/amc_compare.py', base=BASE.replace(ROOT + '/', ''), cand=CAND.replace(ROOT + '/', ''), rows=rows, gauge_summary=gsum,
               pools=pools, compare=cmp_)
    json.dump(res, open(OUT, 'w'), indent=1)
    # markdown
    print('\n| storm (run) | role | AMC (P5) | gauge | obs rise (m) | default model / err | auto model / err |\n|---|---|---|---|---|---|---|')
    for r in rows:
        gb = {g['site']: g for g in (r['gauges_base'] or {}).get('g', [])}; ga = {g['site']: g for g in (r['gauges_auto'] or {}).get('g', [])}
        for site in gb:
            b, a = gb[site], ga.get(site, {})
            print(f"| {r['storm']} ({r['name']}) | {r['role']} | {r['amc']} | {site} | {b['obs']} | {b['model']} / {b['err']:+.2f} | {a.get('model')} / {a.get('err', float('nan')):+.2f} |")
    print('\n| storm (run) | AMC | sites | hits @3 % default -> auto | FSS300 @3 % | rule share | rule hits | rule lift | gauge MAE (m) | peak timing (h) |\n|---|---|---|---|---|---|---|---|---|---|')
    for r in rows:
        b, a = r['closure_base'], r['closure_auto']; gb, ga = r['gauges_base'] or {}, r['gauges_auto'] or {}
        f = lambda x, d=3: '–' if x is None else f'{x:.{d}f}'
        print(f"| {r['storm']} ({r['name']}) | {r['amc']} | {b['sites']} | {b['hits3']:g} -> {a['hits3']:g} | {f(b['fss300_3'])} -> {f(a['fss300_3'])} | "
              f"{f(b['rule_share'], 4)} -> {f(a['rule_share'], 4)} | {b['rule_hits']:g} -> {a['rule_hits']:g} | {f(b['rule_lift'], 1)} -> {f(a['rule_lift'], 1)} | "
              f"{gb.get('mae')} -> {ga.get('mae')} | {gb.get('peak_abs_h')} -> {ga.get('peak_abs_h')} |")
    print('\ngauges', json.dumps(gsum)); print('pools', json.dumps(pools, indent=0))
    print('compare', json.dumps({k: v for k, v in cmp_.items() if k != 'rule'}, indent=0))


if __name__ == '__main__':
    main()
