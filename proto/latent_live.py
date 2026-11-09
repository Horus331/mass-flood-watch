"""Live calibrated flooding probability: the frozen latent model's pi (docs/proto/latent/PREREG_LIVE_PI.md) on any model run.

    python proto/latent_live.py features --run-dir <w9 out> --out <dir>      # prototype rows + geo features (closure_ml capture) -> features.csv
    python proto/latent_live.py pi --features <features.csv> [--out pi.json] # frozen pi per segment
    python proto/latent_live.py check --runs <result dirs> --out <json>     # PREREG_LIVE_PI.md checks 1-3 on runs with features_<storm>.csv
    python proto/latent_live.py selftest

pi = P(the road segment really floods | model output, rain, terrain): logit pi = b_o * o + b_0 + b . h  with theta and the standardisation
from docs/proto/latent/fit_all.json (fit 28 Oct 2026 on 25 non-locked storms; never refitted here).  o is the physics offset from the peak
depth; h the 11 hazard terms of proto/latent_label.hazard.  PREREG_LIVE_PI.md: the live peak depth is the depth ABOVE the depth at rain onset
(P1 convention), passed as peak_depth_m by the caller (forecast members) -- this module does not change rows.
"""
import argparse, csv, json, os, sys

import numpy as np
from scipy.special import expit

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
FIT = os.path.join(ROOT, 'docs', 'proto', 'latent', 'fit_all.json')


def frozen(path=FIT):
    J = json.load(open(path))
    return np.asarray(J['theta'], float), np.asarray(J['stats']['hm'], float), np.asarray(J['stats']['hs'], float)


def pi_rows(rows, fit=None):
    """rows: dicts with the closure_ml ROW_KEYS + geo columns -> pi array (same order)."""
    import latent_label as LL
    th, hm, hs = fit or frozen()
    o, H = LL.hazard(rows)
    return expit(th[0] * o + th[1] + ((H - hm) / hs) @ th[2:])


def features(run_dir, out_dir):
    """Prototype on a run (PROTO_ML capture, no labels) -> out_dir/features.csv (one row per in-box segment)."""
    import closure_ml as CM
    os.makedirs(out_dir, exist_ok=True)
    fn = CM.extract(run_dir, 'live', [], out_dir=out_dir)
    dst = os.path.join(out_dir, 'features.csv'); os.replace(fn, dst)
    m = os.path.join(out_dir, 'matches_live.json')
    if os.path.exists(m): os.remove(m)
    return dst


def cmd_pi(fcsv, out=None):
    rows = list(csv.DictReader(open(fcsv))); p = pi_rows(rows)
    R = dict(made_by='proto/latent_live.py', fit=os.path.relpath(FIT, ROOT), n=len(rows),
             segments={int(r['segment']): round(float(v), 4) for r, v in zip(rows, p)},
             summary=dict(sum_pi=round(float(p.sum()), 2), max=round(float(p.max()) if len(p) else 0, 4),
                          over_10pct=int((p >= 0.1).sum()), over_30pct=int((p >= 0.3).sum()), over_50pct=int((p >= 0.5).sum())))
    if out: json.dump(R, open(out, 'w'), separators=(',', ':'))
    print(json.dumps(R['summary']))
    return R


def check(runs, out):
    """PREREG_LIVE_PI.md checks 1-3 on result folders (features_<storm>.csv + segments.geojson, as proto/turing/run_storm.slurm writes them).
    1 calibration in the large: sum over segments of pi * P(some operating source reports | flooded) vs segments with a matched report;
    2 ranking at the 3 % flag budget (score_v2 box domain): pi's top segments vs the published p_close (rank_to_p, same alert-tier size);
    3 Leominster sep2023 (DPW complete domain): Brier skill vs a constant, top fifth predicted vs observed."""
    import tempfile
    import latent_label as LL, score_v2 as SV
    J = json.load(open(FIT)); ph = np.asarray(J['phi'], float); th, hm, hs = frozen()
    rm = np.asarray(J['stats']['rm'], float); rs = np.asarray(J['stats']['rs'], float)
    # town activity (reports per storm in the town, over the fit storms): from the catalogue, as at fit time
    try: D = LL.get_cache()
    except Exception: D = {s_: LL.load_storm(s_, d_) for s_, d_ in LL.run_dirs().items()}
    ref = [x for x in J['storms'] if x in D]
    rows_out = []
    for rd in runs:
        storm = SV.storm_of(os.path.basename(rd.rstrip('/')))
        fc = os.path.join(rd, f'features_{storm}.csv') if storm else ''
        if not storm or storm in LL.LOCKED or not os.path.exists(fc) or not os.path.exists(os.path.join(rd, 'segments.geojson')):
            print('skip', rd); continue
        Dt = LL.load_storm(storm, rd, fc)
        ta = np.array([np.log1p(sum(D[u]['nrep_town'].get(t, 0) for u in ref if u != storm) / max(1, len([u for u in ref if u != storm]))) for t in Dt['town']])
        R = (np.column_stack([Dt['R2'], ta]) - rm) / rs
        pi = expit(th[0] * Dt['o'] + th[1] + ((Dt['H'] - hm) / hs) @ th[2:])
        pdet = LL.p_detect(ph, R, Dt['Y']); yany = np.nan_to_num(Dt['Y'], nan=0).max(1)
        r = dict(run=rd, storm=storm, segments=int(len(pi)), sum_pi=float(pi.sum()), expected_reports=float((pi * pdet).sum()),
                 observed_reported_segments=int(yany.sum()), max_pi=float(pi.max()), n_pi_ge_50=int((pi >= 0.5).sum()))
        r['ratio_obs_exp'] = r['observed_reported_segments'] / max(r['expected_reports'], 1e-9)
        with tempfile.TemporaryDirectory() as tmp:
            dst = os.path.join(tmp, os.path.basename(rd.rstrip('/')))
            LL.write_run(rd, dst, storm, LL.rank_to_p(pi, Dt['n_rule']), features_csv=fc)
            for name, d_ in (('published', rd), ('pi', dst)):
                B = SV.score_run(SV.load_run(d_, storm))['domains']['box']['rule']
                r[name] = dict(share=B['share'], site_hits=B['site_hits'], sites=len(B['_hits']), site_recall=B['site_recall'])
        if storm in LL.COMPLETE:
            dom = np.isin(Dt['town'], LL.COMPLETE[storm]); y = yany[dom]; p = pi[dom]; e = np.argsort(-p); top = np.array_split(e, 5)[0]
            r['complete_domain'] = dict(n=int(dom.sum()), observed=int(y.sum()), expected=float(p.sum()),
                                        brier_skill=float(1 - ((p - y) ** 2).mean() / max(((y.mean() - y) ** 2).mean(), 1e-12)),
                                        top_fifth_pred=float(p[top].mean()), top_fifth_obs=float(y[top].mean()))
        rows_out.append(r)
        print(f"{storm:9s} obs/exp {r['ratio_obs_exp']:.2f} (obs {r['observed_reported_segments']}, exp {r['expected_reports']:.1f}) | "
              f"sites hit published {r['published']['site_hits']:.0f} pi {r['pi']['site_hits']:.0f} of {r['published']['sites']}", flush=True)
    obs = sum(r['observed_reported_segments'] for r in rows_out); exp = sum(r['expected_reports'] for r in rows_out)
    rec = lambda k: sum(r[k]['site_hits'] for r in rows_out) / max(1, sum(r[k]['sites'] for r in rows_out))
    cd = [r['complete_domain'] for r in rows_out if 'complete_domain' in r]
    C = dict(c1_pooled_ratio=obs / max(exp, 1e-9), c1_storm_ratios=[round(r['ratio_obs_exp'], 3) for r in rows_out],
             c2_recall_published=rec('published'), c2_recall_pi=rec('pi'))
    C['c1_pass'] = bool(0.67 <= C['c1_pooled_ratio'] <= 1.5 and all(1 / 3 <= x <= 3 for x in C['c1_storm_ratios'] if x > 0) and all(x > 0 for x in C['c1_storm_ratios']))
    C['c2_pass'] = bool(C['c2_recall_pi'] >= C['c2_recall_published'] - 0.03)
    if cd: C['c3'] = cd[0]; C['c3_pass'] = bool(cd[0]['brier_skill'] > 0 and abs(cd[0]['top_fifth_pred'] - cd[0]['top_fifth_obs']) <= 0.1)
    res = dict(made_by='proto/latent_live.py check', prereg='docs/proto/latent/PREREG_LIVE_PI.md', fit=os.path.relpath(FIT, ROOT), checks=C, runs=rows_out)
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True); json.dump(res, open(out, 'w'), indent=1)
    print(json.dumps(C, indent=1))
    return res


def selftest():
    th, hm, hs = frozen()
    assert len(th) == 2 + len(hm) == 13 and np.all(hs > 0)
    base = dict(segment=0, road='x', town='y', road_class='local / collector', length_m=100, aadt=500, p_close=0, peak_depth_m=0.0,
                hours_over_15cm=0, area_km2=0.01, hand_m=5, slope_pct=2, p_culvert=0, p_overtop=0, p_sag=0, p_edge=0, peak1h_mm=5,
                stream_dist_m=500)
    wet = dict(base, segment=1, peak_depth_m=0.8, hours_over_15cm=6, peak1h_mm=40, p_overtop=1)
    p = pi_rows([base, wet])
    assert 0 < p[0] < p[1] < 1, p
    # the catalogue features (score_v2 universe) give the fit's per-storm sum of pi back (same model, same rows)
    import latent_label as LL
    J = json.load(open(FIT)); runs = LL.run_dirs(); s = 'sep2023'
    if s in runs:
        rows = list(csv.DictReader(open(os.path.join(runs[s], f'features_{s}.csv'))))
        sp = float(pi_rows(rows).sum()); ref = J['per_storm'][s]['sum_pi']
        print(f'sep2023 sum pi {sp:.1f} vs fit {ref:.1f}')
        assert abs(sp - ref) / ref < 0.35, (sp, ref)   # fit-time town activity / design differences only
    print('latent_live selftest ok')


if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('cmd', choices=['features', 'pi', 'check', 'selftest'])
    ap.add_argument('--run-dir'); ap.add_argument('--out'); ap.add_argument('--features'); ap.add_argument('--runs', nargs='*'); a = ap.parse_args()
    if a.cmd == 'selftest': selftest()
    elif a.cmd == 'check': check(a.runs, a.out)
    elif a.cmd == 'features': print(features(a.run_dir, a.out))
    else: cmd_pi(a.features, a.out)
