"""T4 variant C: CN scale from NWM soil wetness, calibrated leave-one-storm-out on USGS gauge rises only (docs/proto/runoff/AMC.md §0).

    python proto/runoff/cn_loso.py [--cases]   -> docs/proto/runoff/cn_loso.json (+ with --cases: the parity_test.yml cases JSON for the
                                                  held-out runs at each storm's predicted scale, on stdout)

scale_s = clip(a + b (theta_s - THETA_BAR), 0.88, 1.12), theta = NWM SOILSAT_TOP at t0 (antecedent.json). Per gauge the model rise is
interpolated linearly in the scale between the grid runs (0.88 = the parity catalogue, 0.94-1.12 = docs/proto/runoff/grid/cn<s>/).
Objective = mean over training storms of the storm's mean |rise error| (m). Grid a 0.88-1.12 step 0.005, b -2..2 step 0.05; ties: smaller
|b|, then a closest to 0.88. C0 = the same with b = 0. No labels are read.
"""
import os, sys, json
import numpy as np

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
SCALES = [0.88, 0.94, 1.00, 1.06, 1.12]
THETA_BAR = 0.69
LO, HI = 0.88, 1.12
# The pre-registered 9 primary runs (AMC.md §0), explicit: the 16 label-expansion storms later added to the catalogue are not part of T4.
T4_PRIMARY = ('aug2021_worcester_20m', 'aug2023_metrowest_20m', 'aug2023b_millbury_20m', 'aug2026_leominster_20m', 'jul2021_worcester_20m',
              'jul2023_worcester_20m', 'sep2021_worcester_20m', 'sep2022_webster_20m', 'sep2023_leominster_20m')


def run_dir(name, s):
    return os.path.join(ROOT, 'docs', 'proto', 'parity', 'catalog', name) if s == 0.88 else os.path.join(ROOT, 'docs', 'proto', 'runoff', 'grid', f'cn{s:.2f}', name)


def load():
    ante = {r['storm']: r for r in json.load(open(os.path.join(ROOT, 'docs', 'proto', 'runoff', 'antecedent.json')))['storms']}
    names = list(T4_PRIMARY)
    D = {}
    for n in names:
        cfg = json.load(open(os.path.join(run_dir(n, 0.88), 'config.json'))); s = cfg['storm']; G = {}
        for sc in SCALES:
            p = os.path.join(run_dir(n, sc), 'score.json')
            if not os.path.exists(p): raise SystemExit(f'missing {p}')
            for g in json.load(open(p))['gauges']:
                if g.get('obs_rise_m') is None or g.get('model_rise_m') is None: continue
                G.setdefault(g['site'], dict(obs=g['obs_rise_m'], model={}))['model'][sc] = g['model_rise_m']
        G = {k: v for k, v in G.items() if len(v['model']) == len(SCALES)}
        D[s] = dict(name=n, cfg=cfg, theta=ante[s]['nwm']['SOILSAT_TOP'], gauges=G)
    return D


def storm_mae(st, sc):
    e = [abs(np.interp(sc, SCALES, [g['model'][x] for x in SCALES]) - g['obs']) for g in st['gauges'].values()]
    return float(np.mean(e)) if e else None


def scale_of(a, b, theta):
    return float(np.clip(a + b * (theta - THETA_BAR), LO, HI))


def fit(D, train, b_free=True):
    best = None
    A = np.round(np.arange(LO, HI + 1e-9, 0.005), 3); B = np.round(np.arange(-2, 2 + 1e-9, 0.05), 2) if b_free else [0.0]
    for a in A:
        for b in B:
            v = [storm_mae(D[s], scale_of(a, b, D[s]['theta'])) for s in train]; v = float(np.mean([x for x in v if x is not None]))
            key = (round(v, 6), abs(b), abs(a - 0.88))
            if best is None or key < best[0]: best = (key, float(a), float(b), v)
    return dict(a=best[1], b=best[2], train_obj=round(best[3], 4))


def main():
    D = load(); storms = sorted(D); out = dict(made_by='proto/runoff/cn_loso.py', scales=SCALES, theta_bar=THETA_BAR, folds={}, summary={})
    for s in storms:
        tr = [x for x in storms if x != s and storm_mae(D[x], 0.88) is not None]
        fC = fit(D, tr); f0 = fit(D, tr, b_free=False)
        scC = scale_of(fC['a'], fC['b'], D[s]['theta']); sc0 = f0['a']
        out['folds'][s] = dict(theta=D[s]['theta'], n_gauges=len(D[s]['gauges']), C=dict(**fC, scale=round(scC, 2)), C0=dict(**f0, scale=round(sc0, 3)),
                               heldout_mae_interp=dict(base=storm_mae(D[s], 0.88), C=storm_mae(D[s], round(scC, 2)), C0=storm_mae(D[s], sc0)))
    for k in ('base', 'C', 'C0'):
        v = [f['heldout_mae_interp'][k] for f in out['folds'].values() if f['heldout_mae_interp'][k] is not None]
        out['summary'][k] = dict(storm_mean_mae=round(float(np.mean(v)), 3))
    full = fit(D, [x for x in storms if storm_mae(D[x], 0.88) is not None]); out['all9_fit'] = full
    json.dump(out, open(os.path.join(ROOT, 'docs', 'proto', 'runoff', 'cn_loso.json'), 'w'), indent=1)
    for s, f in out['folds'].items():
        print(f"{s:9s} theta {f['theta']:.3f} gauges {f['n_gauges']}  C a {f['C']['a']:.3f} b {f['C']['b']:+.2f} -> scale {f['C']['scale']:.2f}  C0 {f['C0']['scale']:.3f}  "
              f"held-out MAE base {f['heldout_mae_interp']['base']} C {f['heldout_mae_interp']['C']} C0 {f['heldout_mae_interp']['C0']}", file=sys.stderr)
    print(json.dumps(out['summary']), 'all9', json.dumps(full), file=sys.stderr)
    if '--cases' in sys.argv:
        cs = []
        for s, f in out['folds'].items():
            c = dict(D[s]['cfg']); c['env'] = f"LF_PARITY=1 LF_CN_SCALE={f['C']['scale']:.2f}"; cs.append(c)
        print(json.dumps(cs))


if __name__ == '__main__':
    main()
