"""P1 rise-rule test (docs/proto/prospective/CHANGE_PROPOSAL_2026-11-07.md), on the published storm runs (docs/proto/turing, docs/proto/parity/catalog).

Three versions of the alert tier (p_close >= 0.5), scored with proto/score_v2.py on the same runs and labels:
  R0  published:      p_close >= 0.5
  RA  forecast rule:  R0 and depth < 30 cm at rain onset (forecast.onset_frame; what the live k-of-8 count does)
  RB  P1 rise rule:   RA and the depth rises >= 30 cm above its rain-onset depth at some frame after onset
A segment that fails a rule gets p_close 0 in a scratch copy of the run (segments.geojson and features_<storm>.csv), then score_v2 scores
the copy.  Nothing in the model or the live forecast changes.  Usage: python proto/p1_rise_test.py --out docs/proto/prospective/p1_rise_test.json
"""
import argparse, csv, json, os, shutil, sys, tempfile
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import score_v2 as SV
from forecast import onset_frame

RISE_CM = 30.0
SKIP = {'frames', 'map.html', 'figure.png', 'depth.png', 'points.json', 'REPORT.md'}


def keep_masks(run):
    S = json.load(open(os.path.join(run, 'summary.json')))
    i0 = onset_frame(S.get('rain_hourly_mean_mm') or [], None, S.get('frame_hours'))
    F = json.load(open(os.path.join(run, 'segments.geojson')))['features']
    out = {}
    for f in F:
        q = f['properties']; p = q.get('p_close') or 0
        if p < 0.5: continue
        d = np.asarray([v or 0 for v in (q.get('d') or [0])], float); j = min(i0, len(d) - 1)
        ra = d[j] < 30; rb = ra and (d[j:] - d[j]).max() >= RISE_CM
        out[int(q['segment'])] = (bool(ra), bool(rb))
    return i0, out


def variant(run, tmp, drop):
    dst = os.path.join(tmp, os.path.basename(run))
    shutil.copytree(run, dst, ignore=lambda d, names: [n for n in names if n in SKIP])
    g = os.path.join(dst, 'segments.geojson'); G = json.load(open(g))
    for f in G['features']:
        if int(f['properties']['segment']) in drop: f['properties']['p_close'] = 0.0
    json.dump(G, open(g, 'w'))
    for fn in os.listdir(dst):
        if fn.startswith('features_') and fn.endswith('.csv'):
            p = os.path.join(dst, fn); R = list(csv.DictReader(open(p)))
            if not R: continue
            for r in R:
                if int(r['segment']) in drop: r['p_close'] = '0'
            w = csv.DictWriter(open(p, 'w', newline=''), fieldnames=list(R[0])); w.writeheader(); w.writerows(R)
    return dst


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--out', default='docs/proto/prospective/p1_rise_test.json')
    ap.add_argument('--runs', nargs='*', help='run folders to test instead of the published catalogue (e.g. the T2 runs on Turing, results/site_*_t2); '
                    'the storm is read from the folder name')
    ap.add_argument('--group', default='given'); a = ap.parse_args()
    if a.runs:
        cat = [(os.path.abspath(r), SV.storm_of(os.path.basename(r.rstrip('/'))), a.group, True) for r in a.runs]
        cat = [c for c in cat if c[1] and c[1] not in SV.LOCKED and SV.label_files(c[1]) and os.path.exists(os.path.join(c[0], 'segments.geojson'))]   # PROTOCOL.md §2: locked storms stay closed
    else: cat = SV.find_runs()
    rows = []
    for run, storm, grp, prim in cat:
        if not prim or not os.path.exists(os.path.join(run, 'summary.json')): continue
        i0, K = keep_masks(run)
        drops = dict(R0=set(), RA={s for s, (ra, rb) in K.items() if not ra}, RB={s for s, (ra, rb) in K.items() if not rb})
        r = dict(run=os.path.relpath(run, SV.ROOT) if run.startswith(SV.ROOT) else run, storm=storm, group=grp, onset_frame=i0, flagged_R0=len(K))
        with tempfile.TemporaryDirectory() as tmp:
            for v, drop in drops.items():
                src = run if v == 'R0' else variant(run, os.path.join(tmp, v), drop)
                B = SV.score_run(SV.load_run(src, storm))['domains']['box']['rule']
                r[v] = dict(flagged=len(K) - len(drop), share=B['share'], site_hits=B['site_hits'], sites=len(B['_hits']), site_recall=B['site_recall'],
                            fss300=(B['fss'].get('300') or {}).get('fss'))
        rows.append(r)
        print(f"{r['run']:45s} {storm:9s} sites {r['R0']['sites']:3d} | flagged R0/RA/RB {r['R0']['flagged']}/{r['RA']['flagged']}/{r['RB']['flagged']} | "
              f"hits {r['R0']['site_hits']:.0f}/{r['RA']['site_hits']:.0f}/{r['RB']['site_hits']:.0f}", flush=True)
    pools = {}
    for name, st in (('heldout7', SV.HELDOUT), ('new16', SV.NEW16), ('dev2', SV.DEV)):
        for grp in sorted({r['group'] for r in rows}):
            sel = [r for r in rows if r['storm'] in st and r['group'] == grp]
            if not sel: continue
            pools[f'{grp}:{name}'] = {v: dict(storms=len(sel), sites=sum(r[v]['sites'] for r in sel), site_hits=sum(r[v]['site_hits'] for r in sel),
                                             flagged=sum(r[v]['flagged'] for r in sel), mean_share=float(np.mean([r[v]['share'] for r in sel])),
                                             worst_storm_change=min(r[v]['site_hits'] - r['R0']['site_hits'] for r in sel)) for v in ('R0', 'RA', 'RB')}
    res = dict(made_by='proto/p1_rise_test.py', rise_cm=RISE_CM, note=__doc__.strip().splitlines()[0], runs=rows, pools=pools)
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True); json.dump(res, open(a.out, 'w'), indent=1)
    for k, v in pools.items(): print(k, {x: (v[x]['site_hits'], v[x]['sites'], v[x]['flagged'], round(v[x]['mean_share'], 4)) for x in v})


if __name__ == '__main__':
    main()
