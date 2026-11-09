"""Check 3 of docs/proto/forecast/NOWCAST_WINDOWS_PREREG.md (amendment 1): closures with HRRR rain, with the radar-nowcast blend, and with
the radar rain that fell (truth), one member per issue time, 12 h runs on each storm's catalogue box.

    python proto/nowcast_flood.py plan [--min-mm 3]        # -> GitHub matrix JSON (issue time x arm) on stdout
    python proto/nowcast_flood.py closures --run <prototype out> --out <json>
    python proto/nowcast_flood.py score --dir <folder of closures_<storm>_<tau>_<arm>.json> --out docs/proto/forecast/nowcast_flood.json
"""
import argparse, datetime as dt, glob, json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); sys.path.insert(0, HERE)
ARMS = ('hrrr', 'blend', 'radar')


def boxes():
    P = json.load(open(os.path.join(ROOT, 'proto', 'turing', 'plans', 'amcnwm_v1.json')))
    return {t['storm']: t['env']['BOX'] for t in P['tasks']}


def plan(min_mm=3.0):
    R = json.load(open(os.path.join(ROOT, 'docs', 'proto', 'forecast', 'nowcast_hindcast.json'))); B = boxes(); M = []
    for c in R['cycles']:
        if sum(r['truth_mean'] for r in c['leads'] if r['lead_h'] <= 3) < min_mm or c['storm'] not in B: continue
        tau = dt.datetime.strptime(c['tau'], '%Y-%m-%dT%H:%MZ'); init = tau - dt.timedelta(hours=1)
        for a in ARMS:
            M.append(dict(storm=c['storm'], tau=c['tau'], tag=f"{c['storm']}_{tau:%Y%m%d%H}_{a}", arm=a, box=B[c['storm']],
                          init=f'{init:%Y-%m-%dT%HZ}', t0=f'{init:%Y-%m-%dT%H:00Z}'))
    return M


def closures(run, out):
    import numpy as np
    from forecast import onset_frame, rises
    S = json.load(open(os.path.join(run, 'summary.json'))); i0 = onset_frame(S.get('rain_hourly_mean_mm') or [], None, S.get('frame_hours'))
    C = []
    for f in json.load(open(os.path.join(run, 'segments.geojson')))['features']:
        q = f['properties']
        if (q.get('p_close') or 0) >= 0.5 and rises(q.get('d') or [], i0): C.append(int(q['segment']))
    json.dump(dict(closed=sorted(C), onset_frame=i0), open(out, 'w')); print(len(C), 'closures')


def score(d, out):
    F = {}
    for f in glob.glob(os.path.join(d, '**', 'closures_*.json'), recursive=True):
        tag = os.path.basename(f)[9:-5]; base, arm = tag.rsplit('_', 1); F.setdefault(base, {})[arm] = set(json.load(open(f))['closed'])
    rows = []; tot = {a: [0, 0, 0] for a in ('hrrr', 'blend')}
    for base, A in sorted(F.items()):
        if not all(a in A for a in ARMS): rows.append(dict(cycle=base, complete=False)); continue
        T = A['radar']; r = dict(cycle=base, complete=True, radar=len(T))
        for a in ('hrrr', 'blend'):
            tp = len(A[a] & T); fp = len(A[a] - T); fn = len(T - A[a]); tot[a][0] += tp; tot[a][1] += fp; tot[a][2] += fn
            r[a] = dict(n=len(A[a]), tp=tp, fp=fp, fn=fn)
        rows.append(r)
    f1 = {a: (2 * t[0] / max(1, 2 * t[0] + t[1] + t[2])) for a, t in tot.items()}
    res = dict(made_by='proto/nowcast_flood.py', prereg='NOWCAST_WINDOWS_PREREG.md check 3 (amendment 1)', pooled={a: dict(tp=t[0], fp=t[1], fn=t[2], f1=f1[a]) for a, t in tot.items()},
               check3_pass=bool(f1['blend'] >= f1['hrrr'] - 0.02), complete_cycles=sum(r['complete'] for r in rows), cycles=rows)
    json.dump(res, open(out, 'w'), indent=1); print(json.dumps({k: res[k] for k in ('pooled', 'check3_pass', 'complete_cycles')}, indent=1))


if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('cmd', choices=['plan', 'closures', 'score']); ap.add_argument('--min-mm', type=float, default=3.0)
    ap.add_argument('--run'); ap.add_argument('--out'); ap.add_argument('--dir'); a = ap.parse_args()
    if a.cmd == 'plan': print(json.dumps(plan(a.min_mm)))
    elif a.cmd == 'closures': closures(a.run, a.out)
    else: score(a.dir, a.out)
