"""Score one or more arms of a re-run parity catalogue with the frozen PROTOCOL v2 scorer (proto/score_v2.py) and summarise the depth
artefacts per arm (docs/proto/terrain/, docs/proto/runoff/B0_V2.md).

    python proto/score_arms.py score --dir docs/proto/terrain/runs/base --out docs/proto/terrain/score_base.json
    python proto/score_arms.py depths --dirs base=DIR1 notch=DIR2 ... --out docs/proto/terrain/depths.json
    python proto/score_v2.py --compare score_base.json score_<arm>.json --protocol v2 --k K      (the decision, unchanged)

An arm folder holds one run folder per storm, named like the parity catalogue (<storm>_<area>_20m), each with flood_meta.json,
features_<storm>.csv and matches_<storm>.json (as written by .github/workflows/parity_test.yml).  Only primary folders are scored; locked and
District 4-6 storms are refused by score_v2 itself."""
import os, sys, json, csv, re, argparse, time
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import score_v2 as SV


def runs_in(d):
    for n in sorted(os.listdir(d)):
        p = os.path.join(d, n); s = SV.storm_of(n)
        if s and re.fullmatch(rf'{s}_[a-z]+_20m', n) and os.path.exists(os.path.join(p, 'flood_meta.json')) and os.path.exists(os.path.join(p, f'features_{s}.csv')):
            if s in SV.LOCKED: print('locked storm, not scored:', n); continue
            yield p, s


def cmd_score(a):
    runs = []
    for p, s in runs_in(a.dir):
        t = time.time(); r = SV.score_run(SV.load_run(p, s)); r.update(group=os.path.basename(os.path.normpath(a.dir)), primary=True); runs.append(r)
        b = r['domains']['box']
        print(f"{r['run']:50s} {s:9s} sites {b['n_sites']:3d} rule {SV.fmt(b['rule']['share'])} rec {SV.fmt(b['rule']['site_recall'], 2)} 3% {SV.fmt(b['shares']['0.03']['site_recall'], 2)} ({time.time() - t:.0f}s)", flush=True)
    pools = {}
    P = {r['storm']: r for r in runs}
    for name, st in (('heldout23', SV.HELDOUT + SV.NEW16), ('heldout7', SV.HELDOUT), ('new16', SV.NEW16), ('dev2', SV.DEV)):
        sel = [P[s] for s in st if s in P]
        if sel: pools[name] = {'box': SV.pooled(sel, 'box', a.boot)}
    json.dump(dict(made_by='proto/score_arms.py score', dir=a.dir, runs=runs, pools=pools), open(a.out, 'w'), indent=0)
    for k, v in pools.items():
        pt = v['box']['point']; ci = v['box']['ci90']
        print(k, 'sites', pt.get('n_sites'), 'rule', round(pt['rule']['site_recall'], 3), 'lift', round(pt['rule'].get('lift', float('nan')), 2),
              '3%', round(pt['share_0.03']['site_recall'], 3), ci['share_0.03']['site_recall'])


def feats(p, s):
    rows = list(csv.DictReader(open(os.path.join(p, f'features_{s}.csv'))))
    return {int(r['segment']): (SV.F(r['peak_depth_m']), SV.F(r['p_close']), r.get('road', ''), r.get('town', '')) for r in rows}


def cmd_depths(a):
    arms = dict(x.split('=', 1) for x in a.dirs); names = list(arms); out = dict(arms=arms, storms={}, affected={})
    base = names[0]
    B = {s: (p, s) for p, s in runs_in(arms[base])}
    for arm in names:
        for p, s in runs_in(arms[arm]):
            f = feats(p, s); d = np.array([v[0] for v in f.values()]); pc = np.array([v[1] for v in f.values()])
            out['storms'].setdefault(s, {})[arm] = dict(segments=len(f), flagged=int((pc >= 0.5).sum()), depth_gt1m=int((d > 1).sum()), depth_gt2m=int((d > 2).sum()),
                                                        depth_gt3m=int((d > 3).sum()), max_depth=round(float(d.max()), 2))
            if arm != base and s in B:
                fb = feats(*B[s]); ch = []
                for seg, (dd, pp, road, town) in f.items():
                    db, pb = fb.get(seg, (0.0, 0.0, '', ''))[:2]
                    if abs(dd - db) >= a.min_change or (pb >= 0.5) != (pp >= 0.5):
                        ch.append(dict(segment=seg, road=road, town=town, depth_base=round(db, 2), depth=round(dd, 2), p_base=round(pb, 3), p=round(pp, 3)))
                ch.sort(key=lambda r: r['depth'] - r['depth_base'])
                out['affected'].setdefault(arm, {})[s] = ch
    tot = {arm: {k: sum(out['storms'][s][arm][k] for s in out['storms'] if arm in out['storms'][s]) for k in ('flagged', 'depth_gt1m', 'depth_gt2m', 'depth_gt3m')} for arm in names}
    out['totals'] = tot; json.dump(out, open(a.out, 'w'), indent=1); print(json.dumps(tot, indent=1))


def main():
    ap = argparse.ArgumentParser(); sp = ap.add_subparsers(dest='cmd', required=True)
    s = sp.add_parser('score'); s.add_argument('--dir', required=True); s.add_argument('--out', required=True); s.add_argument('--boot', type=int, default=SV.NBOOT)
    d = sp.add_parser('depths'); d.add_argument('--dirs', nargs='+', required=True); d.add_argument('--out', required=True); d.add_argument('--min-change', type=float, default=0.5)
    a = ap.parse_args(); {'score': cmd_score, 'depths': cmd_depths}[a.cmd](a)


if __name__ == '__main__':
    main()
