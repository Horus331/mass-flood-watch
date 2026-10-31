"""Score the pre-registered NWM antecedent-wetness test (docs/proto/runoff/NWM_AMC_PREREG.md) from the collected Turing runs.

    python proto/runoff/nwm_amc_score.py [--runs docs/proto/runoff/amcnwm_v1] [--out docs/proto/runoff/nwm_amc.json] [--boot 2000]

Input: <runs>/amcnwm_<arm>_<storm>/score_v2.json (+ score.json, flood_meta.json), made on Turing by proto/turing/run_plan_gpu.slurm (plan
proto/turing/plans/amcnwm_v1.json) and pushed by proto/turing/collect_scores.slurm.
Arms: base (LF_CN_AMC unset = AMC II) and nwm (LF_CN_AMC=nwm).  Output: the paired score_v2 --compare (PROTOCOL v2 §5a, k = 1) on the
held-out 23, pooled recall / lift / FSS per arm for held-out 23, OOS-7, NEW16 and the dev storms, gauge MAE, the verdict per the
pre-registration, and a markdown table on stdout.  Only storms present in BOTH arms are compared; missing ones are listed.
"""
import os, sys, json, glob, argparse
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.normpath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'proto')); import score_v2 as SV  # noqa: E402

ARMS = ('base', 'nwm')
GAUGE_TOL = 0.10          # pre-registered: held-out storm-mean gauge MAE may not rise by more than 10 %


def load(runs):
    """<runs>/amcnwm_<arm>_<storm>/{score_v2.json, score.json, flood_meta.json} as collect_scores.slurm writes them."""
    R = {a: {} for a in ARMS}; G = {a: {} for a in ARMS}; M = {a: {} for a in ARMS}
    for f in sorted(glob.glob(os.path.join(runs, 'amcnwm_*', 'score_v2.json'))):
        d = os.path.dirname(f); name = os.path.basename(d); arm = name.split('_')[1]
        if arm not in ARMS: continue
        r = json.load(open(f)); r['primary'] = True; s = r['storm']; R[arm][s] = r
        if os.path.exists(os.path.join(d, 'score.json')): G[arm][s] = json.load(open(os.path.join(d, 'score.json')))
        if os.path.exists(os.path.join(d, 'flood_meta.json')):
            m = json.load(open(os.path.join(d, 'flood_meta.json'))); M[arm][s] = dict(git_sha=m.get('git_sha'), env=(m.get('inputs') or {}).get('env'))
    return R, G, M


def gauge_stats(G, storms):
    per = {s: G[s].get('mean_abs_rise_error_m') for s in storms if s in G and G[s].get('mean_abs_rise_error_m') is not None}
    errs = [g['rise_error_m'] for s in storms if s in G for g in G[s].get('gauges', []) if g.get('rise_error_m') is not None]
    return dict(storm_mean_mae=float(np.mean(list(per.values()))) if per else None, n_storms=len(per),
                all_gauge_mae=float(np.mean(np.abs(errs))) if errs else None, all_gauge_bias=float(np.mean(errs)) if errs else None, n_gauges=len(errs), per_storm=per)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--runs', default=os.path.join(ROOT, 'docs', 'proto', 'runoff', 'amcnwm_v1'))
    ap.add_argument('--out', default=os.path.join(ROOT, 'docs', 'proto', 'runoff', 'nwm_amc.json')); ap.add_argument('--boot', type=int, default=SV.NBOOT)
    a = ap.parse_args()
    R, G, M = load(a.runs)
    H23 = SV.HELDOUT + SV.NEW16
    both = [s for s in H23 if s in R['base'] and s in R['nwm']]; missing = [s for s in H23 if s not in both]
    res = dict(made_by='proto/runoff/nwm_amc_score.py', prereg='docs/proto/runoff/NWM_AMC_PREREG.md', storms_compared=both, storms_missing=missing,
               git_sha={arm: {s: (M[arm].get(s) or {}).get('git_sha') for s in R[arm]} for arm in ARMS},
               resolved={s: ((M['nwm'].get(s) or {}).get('env') or {}).get('LF_CN_AMC_RESOLVED') for s in R['nwm']})
    rule = dict(SV.ADOPT_V2, level='share'); rule['alpha'] = rule['alpha'] / 1
    if both:
        res['compare_v2'] = SV.compare(dict(runs=[R['base'][s] for s in both]), dict(runs=[R['nwm'][s] for s in both]), a.boot, rule=rule)
    pools = {}
    for pname, st in (('heldout23', both), ('heldout7', [s for s in SV.HELDOUT if s in both]), ('new16', [s for s in SV.NEW16 if s in both]),
                      ('dev2', [s for s in SV.DEV if s in R['base'] and s in R['nwm']])):
        if not st: continue
        pools[pname] = {arm: SV.pooled([R[arm][s] for s in st], 'box', a.boot) for arm in ARMS}
        for arm in ARMS:
            pools[pname][arm] = dict(n_sites=pools[pname][arm]['n_sites'], point={k: pools[pname][arm]['point'][k] for k in ('rule', 'share_0.03')},
                                     ci90={k: pools[pname][arm]['ci90'][k] for k in ('rule', 'share_0.03')}, gauges=gauge_stats(G[arm], st))
    res['pools'] = pools
    per = {}
    for s in sorted(set(R['base']) & set(R['nwm'])):
        b, c = R['base'][s]['domains']['box'], R['nwm'][s]['domains']['box']
        per[s] = dict(sites=b['n_sites'], base_hits3=b['shares']['0.03']['site_hits'], nwm_hits3=c['shares']['0.03']['site_hits'],
                      base_rule=b['rule']['site_hits'], nwm_rule=c['rule']['site_hits'], base_rule_share=b['rule']['share'], nwm_rule_share=c['rule']['share'],
                      base_gauge_mae=(G['base'].get(s) or {}).get('mean_abs_rise_error_m'), nwm_gauge_mae=(G['nwm'].get(s) or {}).get('mean_abs_rise_error_m'))
    res['per_storm'] = per
    # verdict (NWM_AMC_PREREG.md §5): score_v2 v2 §5a all five conditions (k = 1) AND held-out storm-mean gauge MAE not worse by > 10 %
    if both and 'heldout23' in pools:
        gb = pools['heldout23']['base']['gauges']['storm_mean_mae']; gc = pools['heldout23']['nwm']['gauges']['storm_mean_mae']
        gauge_ok = bool(gb is not None and gc is not None and gc <= (1 + GAUGE_TOL) * gb)
        res['verdict'] = dict(protocol_v2_checks=res['compare_v2']['checks'], protocol_v2_adopt=res['compare_v2']['adopt'], gauge_mae_base=gb, gauge_mae_nwm=gc,
                              gauge_ok=gauge_ok, complete=not missing, adopt=bool(res['compare_v2']['adopt'] and gauge_ok and not missing))
    json.dump(res, open(a.out, 'w'), indent=1)
    # table
    print(f"compared {len(both)} held-out storms; missing {missing}")
    for pname, P in pools.items():
        for arm in ARMS:
            p = P[arm]; s3 = p['point']['share_0.03']; ru = p['point']['rule']; g = p['gauges']
            print(f"{pname:9s} {arm:4s} sites {p['n_sites']:3d}  3%: recall {s3['site_recall']:.3f} lift {s3['lift']:.2f} fss300 {s3['fss300']:.4f}  "
                  f"rule: recall {ru['site_recall']:.3f} lift {(ru['lift'] or 0):.2f}  gauges storm-mean MAE {g['storm_mean_mae']} all {g['all_gauge_mae']} (n {g['n_gauges']})")
    if 'compare_v2' in res:
        c = res['compare_v2']; print('compare v2 k=1:', 'delta', round(c['delta_recall'], 4), 'lower', round(c['delta_recall_lower'], 4), 'dFSS', round(c['delta_fss'], 5),
                                     'worst', c['worst_storm_change'], 'lift', c['lift_rule'], c['checks'])
    if 'verdict' in res: print('VERDICT', json.dumps(res['verdict']))
    for s, p in per.items(): print(s, p)


if __name__ == '__main__':
    main()
