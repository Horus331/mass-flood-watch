"""Score the LF_INLETS test exactly as pre-registered (docs/proto/drains/INLETS_PREREG.md) from the collected Turing scores.

    python proto/inlets_eval.py [--dir docs/proto/drains/inlets_v1] [--boot 2000]
        -> <dir>/BASE.json, <dir>/CAND.json (score_v2 run lists), <dir>/compare.json (score_v2.compare, PROTOCOL v2 §5a, k = 1),
           <dir>/eval.json (secondary + failure-mode check + calibration storm + clog sensitivity), <dir>/eval.md (tables)
    python proto/inlets_eval.py --selftest

Inputs: <dir>/inl1_<storm>_<area>_20m_<arm>/score_v2.json (+ flood_meta.json, score.json), written by proto/turing/run_inlets.slurm and
pushed by proto/turing/collect_scores.slurm.  Nothing here is tuned; every number and rule is fixed in INLETS_PREREG.md.
"""
import argparse, glob, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import score_v2 as SV

DIR = os.path.join(ROOT, 'docs', 'proto', 'drains', 'inlets_v1')
NAME = re.compile(r'^inl1_(?P<cat>(?P<storm>[a-z]{3}20\d\d[a-z]?)_[a-z]+_20m)_(?P<arm>base|inlets|inlets_clog0|inlets_clog065)$')
HELD = SV.HELDOUT + SV.NEW16
CALIB = 'sep2023'
PROP_RATIO = 0.8        # failure-mode flag (pre-registered): sites lost at the rule >= 0.8 x the share of flagged segments removed


def load(d):
    runs = {}
    for p in sorted(glob.glob(os.path.join(d, 'inl1_*', 'score_v2.json'))):
        m = NAME.match(os.path.basename(os.path.dirname(p)))
        if not m: continue
        r = json.load(open(p)); r['primary'] = True; r['storm'] = m['storm']
        fm = os.path.join(os.path.dirname(p), 'flood_meta.json'); sc = os.path.join(os.path.dirname(p), 'score.json')
        r['_meta'] = json.load(open(fm)) if os.path.exists(fm) else {}
        r['_gauges'] = json.load(open(sc)) if os.path.exists(sc) else {}
        runs[(m['storm'], m['arm'])] = r
    return runs


def blk(r, dom='box'):
    D = r['domains'][dom]; ru = D['rule']; s3 = D['shares']['0.03']
    return dict(sites=D['n_sites'], n_seg=D['n_segments'], rule_share=ru['share'], rule_k=ru['k'], rule_hits=ru['site_hits'], rule_recall=ru['site_recall'],
                rule_lift=ru['lift'], rule_chance=sum(ru['_chance']), s3_hits=s3['site_hits'], s3_recall=s3['site_recall'], s3_lift=s3['lift'],
                fss300_s3=s3['fss'].get('300', {}).get('fss'))


def failure_mode(pairs, dom='box'):
    """DRAINS.md failure mode: the sink removes flags and documented sites in proportion.  Pooled over the pairs: share of rule-flagged
    segments removed (1 - k_cand / k_base) and share of rule-hit sites lost (1 - hits_cand / hits_base)."""
    kb = sum(blk(b, dom)['rule_k'] for b, c in pairs); kc = sum(blk(c, dom)['rule_k'] for b, c in pairs)
    hb = sum(blk(b, dom)['rule_hits'] for b, c in pairs); hc = sum(blk(c, dom)['rule_hits'] for b, c in pairs)
    f_drop = 1 - kc / kb if kb else None; s_drop = 1 - hc / hb if hb else None
    ratio = (s_drop / f_drop) if (f_drop and f_drop > 0 and s_drop is not None) else None
    return dict(flagged_base=kb, flagged_cand=kc, flag_drop=f_drop, rule_hits_base=hb, rule_hits_cand=hc, site_drop=s_drop, ratio=ratio,
                present=bool(ratio is not None and ratio >= PROP_RATIO and f_drop > 0))


def inlet_q(r):
    i = (r.get('_meta') or {}).get('inputs', {}).get('inlets')
    return dict(q=i.get('total_q_m3s'), inlets=i.get('inlets'), cells=i.get('cells'), clog=i.get('clog')) if isinstance(i, dict) else None


def gauges(r):
    g = r.get('_gauges') or {}
    return dict(mean_abs_rise_error_m=g.get('mean_abs_rise_error_m'), bias=g.get('mean_rise_bias_m') or g.get('rise_bias_m'))


def evaluate(d=DIR, boot=SV.NBOOT):
    runs = load(d)
    held = [s for s in HELD if (s, 'base') in runs and (s, 'inlets') in runs]
    missing = [s for s in HELD if s not in held]
    base = dict(runs=[dict(runs[(s, 'base')], primary=True) for s in held]); cand = dict(runs=[dict(runs[(s, 'inlets')], primary=True) for s in held])
    strip = lambda X: dict(runs=[{k: v for k, v in r.items() if not k.startswith('_m') and k != '_gauges'} for r in X['runs']])
    json.dump(strip(base), open(os.path.join(d, 'BASE.json'), 'w')); json.dump(strip(cand), open(os.path.join(d, 'CAND.json'), 'w'))
    rule = dict(SV.ADOPT_V2, level='share'); rule['alpha'] = rule['alpha'] / 1       # k = 1 (one candidate on the decision set)
    v = SV.compare(base, cand, boot, rule=rule) if held else None
    if v: json.dump(v, open(os.path.join(d, 'compare.json'), 'w'), indent=1)
    pairs = [(runs[(s, 'base')], runs[(s, 'inlets')]) for s in held]
    per = {s: dict(base=blk(runs[(s, 'base')]), inlets=blk(runs[(s, 'inlets')]), inlet_sink=inlet_q(runs[(s, 'inlets')]),
                   gauges=dict(base=gauges(runs[(s, 'base')]), inlets=gauges(runs[(s, 'inlets')]))) for s in held}
    pooled = {}
    for arm, X in (('base', base), ('inlets', cand)):
        P = SV.pooled(X['runs'], 'box', boot); pooled[arm] = dict(rule=P['point']['rule'], share_0_03=P['point']['share_0.03'], ci90=dict(rule=P['ci90']['rule'], share_0_03=P['ci90']['share_0.03']),
                                                                   mean_rule_share=sum(blk(r)['rule_share'] for r in X['runs']) / len(X['runs']) if X['runs'] else None)
    cal = {}
    for arm in ('base', 'inlets', 'inlets_clog0', 'inlets_clog065'):
        r = runs.get((CALIB, arm))
        if r: cal[arm] = dict(box=blk(r), city=blk(r, 'towns'), inlet_sink=inlet_q(r), gauges=gauges(r))
    cal_fm = {}
    if (CALIB, 'base') in runs:
        for arm in ('inlets', 'inlets_clog0', 'inlets_clog065'):
            if (CALIB, arm) in runs: cal_fm[arm] = dict(box=failure_mode([(runs[(CALIB, 'base')], runs[(CALIB, arm)])]),
                                                       city=failure_mode([(runs[(CALIB, 'base')], runs[(CALIB, arm)])], 'towns'))
    E = dict(made_by='proto/inlets_eval.py', prereg='docs/proto/drains/INLETS_PREREG.md', decision_storms=held, missing_decision_storms=missing,
             verdict=('ADOPT' if v and v['adopt'] else 'NOT ADOPTED') if not missing else 'INCOMPLETE (decision storms missing: rerun them unchanged, PREREG §6)',
             compare=v and {k: v[k] for k in ('n_sites', 'delta_recall', 'delta_recall_lower', 'delta_fss', 'worst_storm_change', 'lift_rule', 'checks', 'adopt')},
             pooled=pooled, failure_mode_heldout=failure_mode(pairs) if pairs else None, per_storm=per, calibration_sep2023=cal, calibration_failure_mode=cal_fm)
    json.dump(E, open(os.path.join(d, 'eval.json'), 'w'), indent=1, default=float)
    open(os.path.join(d, 'eval.md'), 'w').write(md(E)); print(md(E)); return E


def f(v, n=3):
    return '–' if v is None else (f'{v:.{n}f}' if isinstance(v, float) else str(v))


def md(E):
    L = [f"**Verdict: {E['verdict']}** (held-out storms scored: {len(E['decision_storms'])} / 23)", '']
    c = E['compare']
    if c:
        L += ['| PROTOCOL v2 §5a condition | value | pass |', '|---|---|---|',
              f"| 1. pooled site recall gain at 3 % >= +0.04 | {f(c['delta_recall'])} ({c['n_sites']} sites) | {c['checks']['gain']} |",
              f"| 2. one-sided 5 % lower bound > 0 (k = 1) | {f(c['delta_recall_lower'])} | {c['checks']['ci_lower_gt_0']} |",
              f"| 3. FSS 300 m at 3 % does not drop | {f(c['delta_fss'], 4)} | {c['checks']['fss_no_drop']} |",
              f"| 4. no storm with >= 3 sites loses > 1 site at 3 % | worst {f(c['worst_storm_change'], 1)} | {c['checks']['no_storm_loses_gt_1']} |",
              f"| 5. rule lift >= 0.8 x base | {f(c['lift_rule']['cand'], 2)} vs {f(c['lift_rule']['base'], 2)} | {c['checks']['lift_ge_0p8']} |", '']
    P = E['pooled']
    if P.get('base'):
        L += ['| held-out pooled (box) | base | LF_INLETS |', '|---|---|---|']
        for lab, a, b in (('site recall at 3 %', 'share_0_03', 'site_recall'), ('lift at 3 %', 'share_0_03', 'lift'), ('site recall at rule', 'rule', 'site_recall'),
                          ('lift at rule', 'rule', 'lift'), ('FSS 300 m at 3 %', 'share_0_03', 'fss300')):
            L.append(f"| {lab} | {f(P['base'][a][b])} | {f(P['inlets'][a][b])} |")
        L.append(f"| mean flagged share at rule | {f(P['base']['mean_rule_share'], 4)} | {f(P['inlets']['mean_rule_share'], 4)} |")
    fm = E['failure_mode_heldout']
    if fm: L += ['', f"Failure-mode check (DRAINS.md; reported, not a decision): rule-flagged segments {fm['flagged_base']} -> {fm['flagged_cand']} "
                     f"(drop {f(fm['flag_drop'])}), rule-hit sites {fm['rule_hits_base']} -> {fm['rule_hits_cand']} (drop {f(fm['site_drop'])}); ratio {f(fm['ratio'], 2)}; "
                     f"sites removed in proportion: **{fm['present']}**"]
    L += ['', '| storm | sites | base 3 % hits | inlets 3 % hits | base rule hits / share | inlets rule hits / share | inlet sink m3/s (inlets, cells) |', '|---|---|---|---|---|---|---|']
    for s, p in E['per_storm'].items():
        b, i, q = p['base'], p['inlets'], p['inlet_sink'] or {}
        L.append(f"| {s} | {b['sites']} | {f(b['s3_hits'], 1)} | {f(i['s3_hits'], 1)} | {f(b['rule_hits'], 0)} / {f(b['rule_share'], 4)} | {f(i['rule_hits'], 0)} / {f(i['rule_share'], 4)} | "
                 f"{q.get('q')} ({q.get('inlets')}, {q.get('cells')}) |")
    if E['calibration_sep2023']:
        L += ['', '| sep2023 (calibration, report only) | box 3 % hits | box rule hits / share | Leominster city rule hits / flagged | sink m3/s | gauge mean abs rise error m |', '|---|---|---|---|---|---|']
        for arm, r in E['calibration_sep2023'].items():
            L.append(f"| {arm} | {f(r['box']['s3_hits'], 1)} / {r['box']['sites']} | {f(r['box']['rule_hits'], 0)} / {f(r['box']['rule_share'], 4)} | "
                     f"{f(r['city']['rule_hits'], 0)} / {r['city']['rule_k']} | {(r['inlet_sink'] or {}).get('q')} | {r['gauges']['mean_abs_rise_error_m']} |")
        for arm, x in E['calibration_failure_mode'].items():
            L.append(f"\nsep2023 {arm} failure-mode check: city flags {x['city']['flagged_base']} -> {x['city']['flagged_cand']}, city rule-hit sites "
                     f"{x['city']['rule_hits_base']} -> {x['city']['rule_hits_cand']}, ratio {f(x['city']['ratio'], 2)}, in proportion: {x['city']['present']}")
    return '\n'.join(L) + '\n'


def selftest():
    import tempfile, shutil
    td = tempfile.mkdtemp(prefix='inleval_'); ok = True
    import numpy as np
    R = SV.synthetic(storm='jul2023'); SV.add_labels(R, [3, 40, 77, 120, 300, 500], coord='exact')
    R['p'] = np.zeros(len(R['seg'])); R['p'][[3, 40, 77, 120]] = 0.9; R['p'][np.arange(600, 640)] = 0.7
    for s in ('jul2023', 'aug2023', 'sep2023'):
        R['storm'] = s; base = SV.score_run(R); R2 = dict(R); R2['p'] = np.where(R['p'] > 0.8, 0.9, R['p'] * 0.5)
        cand = SV.score_run(R2)
        for arm, x in (('base', base), ('inlets', cand)):
            d = os.path.join(td, f'inl1_{s}_worcester_20m_{arm}'); os.makedirs(d); json.dump(x, open(os.path.join(d, 'score_v2.json'), 'w'), default=float)
    E = evaluate(td, boot=50)
    ok &= E['decision_storms'] == ['aug2023', 'jul2023'] and E['verdict'].startswith('INCOMPLETE') and E['compare'] is not None
    ok &= E['failure_mode_heldout'] is not None and 'sep2023' not in E['per_storm'] and set(E['calibration_sep2023']) == {'base', 'inlets'}
    assert NAME.match('inl1_sep2018m_milford_20m_inlets_clog065') and NAME.match('inl1_aug2018b_holden_20m_base')['storm'] == 'aug2018b'
    shutil.rmtree(td); print('inlets_eval selftest', 'OK' if ok else 'FAILED'); return ok


if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('--dir', default=DIR); ap.add_argument('--boot', type=int, default=SV.NBOOT); ap.add_argument('--selftest', action='store_true')
    a = ap.parse_args()
    if a.selftest: sys.exit(0 if selftest() else 1)
    evaluate(a.dir, a.boot)
