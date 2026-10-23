"""Live 'closed in k of the last n cycles' layer for the road-closure forecast (time-lagged ensemble, docs/proto/forecast/ENSEMBLE.md).
OFF by default: forecast.yml runs it only when the repository variable FORECAST_KOFN is '1'.

    python proto/forecast_kofn.py record  --gate gate.json [--run key=<prototype out dir> ...] --store docs/proto/forecast/live_cycles
    python proto/forecast_kofn.py combine --gate gate.json --store docs/proto/forecast/live_cycles [--n 4] --out kofn.json
    python proto/forecast_kofn.py selftest

record: one small file per 00/06/12/18z cycle (<store>/<YYYYmmddHH>.json): gate decision, boxes, and every segment at P(close) >= 0.5 (the
        same rule and start-state filter as forecast.py status) with its centre in EPSG:26986.
combine: for the current cycle and the n - 1 synoptic cycles before it, k = how many flag the segment and n = how many could have flagged it:
        a quiet cycle (gate not fired) counts as a forecast of no closure everywhere; a cycle that ran covers its boxes only; a missing cycle
        or a failed run is left out of n.  proto/forecast.py status --kofn kofn.json writes it to forecast_status.json (k_of_n and runs[].k_of_n).
Hindcast (ENSEMBLE.md section 4, 9 storms, rules fixed before the 7 out-of-sample storms): k >= 2 of 8 (n=4 --hourly 4) beat the single cycle on
every storm; with the synoptic cycles only, k >= 1 of 4 raises recall at about twice the flagged share and k >= 2 of 4 is mixed.
"""
import os, sys, json, argparse
import numpy as np

CLOSE_P = 0.5


def log(*a): print(*a, flush=True)


def _ts(s):
    import pandas as pd
    t = pd.Timestamp(s.replace('Z', ''))
    return t.tz_convert('UTC').tz_localize(None) if t.tzinfo is not None else t


def closures(pdir):
    """Segments at P >= 0.5 in one prototype run (segments.geojson), minus water already standing at the start (as forecast.run_summary)."""
    from pyproj import Transformer
    S = json.load(open(os.path.join(pdir, 'summary.json'))); g = json.load(open(os.path.join(pdir, 'segments.geojson')))
    rain = S.get('rain_hourly_mean_mm') or []; early = 2 if sum(rain[:1]) < 2 else 0
    tr = Transformer.from_crs(4326, 26986, always_xy=True); out = []
    for f in g['features']:
        q = f['properties']
        if q.get('p_close', 0) < CLOSE_P: continue
        d = q.get('d') or []
        if early and len(d) > early and max(d[:early + 1]) >= 30: continue
        c = np.array(_coords(f['geometry']), float)
        if not len(c): continue
        x, y = tr.transform(float(c[:, 0].mean()), float(c[:, 1].mean()))
        out.append(dict(segment=int(q['segment']), p=round(float(q['p_close']), 2), x=round(x), y=round(y), road=q.get('road') or '', town=q.get('town') or ''))
    return out


def _coords(geom):
    t, c = geom.get('type'), geom.get('coordinates') or []
    if t == 'LineString': return c
    if t == 'MultiLineString': return [p for part in c for p in part]
    if t == 'Point': return [c]
    return []


def cmd_record(a):
    G = json.load(open(a.gate)); init = _ts(G['issued']); runs = []
    for spec in a.run or []:
        key, _, pdir = spec.partition('='); pdir = pdir.split(',')[0]
        bid = key.rsplit('_', 1)[-1] if key.rsplit('_', 1)[-1].startswith('b') else 'b1'      # forecast.yml: forecast_latest = b1, forecast_latest_bN
        box = next((b['box'] for b in G['boxes'] if b['id'] == bid), None)
        try: runs.append(dict(key=key, box=box, ok=True, segments=closures(pdir)))
        except Exception as e: runs.append(dict(key=key, box=box, ok=False, error=repr(e)[:200]))
    if G['trigger'] and not runs: runs = [dict(key=b['id'], box=b['box'], ok=False, error='no run output') for b in G['boxes']]
    rec = dict(issued=G['issued'], trigger=bool(G['trigger']), boxes=[b['box'] for b in G['boxes']], runs=runs)
    os.makedirs(a.store, exist_ok=True); p = os.path.join(a.store, f'{init:%Y%m%d%H}.json'); json.dump(rec, open(p, 'w'), separators=(',', ':'))
    log('recorded', p, 'trigger', rec['trigger'], 'closures', sum(len(r.get('segments', [])) for r in runs))


def combine(store, issued, n=4, hourly=0):
    """Members: this cycle and the n - 1 synoptic cycles 6, 12, ... h before it, plus (hourly > 0) the hourly cycles 1..hourly h before it if
    they were recorded (forecast.yml run on those cycles by hand / a separate schedule); the 2-of-8 hindcast rule is n=4, hourly=4."""
    import pandas as pd
    T = _ts(issued); cyc = []
    for t in [T - pd.Timedelta(hours=6 * j) for j in range(n)] + [T - pd.Timedelta(hours=h) for h in range(1, hourly + 1)]:
        p = os.path.join(store, f'{t:%Y%m%d%H}.json')
        cyc.append(dict(issued=f'{t:%Y-%m-%dT%H:%M}Z', rec=json.load(open(p)) if os.path.exists(p) else None))
    seg = {}
    for c in cyc:
        r = c['rec']
        if not r: continue
        for run in r['runs']:
            for s in run.get('segments', []):
                e = seg.setdefault(s['segment'], dict(segment=s['segment'], road=s['road'], town=s['town'], x=s['x'], y=s['y'], cycles=[], p_max=0.0))
                if c['issued'] not in e['cycles']: e['cycles'].append(c['issued'])
                e['p_max'] = max(e['p_max'], s['p'])
    def covers(r, x, y):
        if r is None: return None                       # cycle missing: unknown
        if not r['trigger']: return True                # quiet: forecast of no closure everywhere
        ok = [run for run in r['runs'] if run.get('ok') and run.get('box')]
        return any(b[0] <= x < b[2] and b[1] <= y < b[3] for b in (run['box'] for run in ok)) or None
    out = []
    for e in seg.values():
        cov = [covers(c['rec'], e['x'], e['y']) for c in cyc]
        e['k'] = len(e['cycles']); e['n'] = sum(1 for v in cov if v); out.append(e)
    out.sort(key=lambda e: (-e['k'], -e['p_max']))
    n = len(cyc)
    return dict(n_cycles=n, issued=issued, cycles=[dict(issued=c['issued'], available=c['rec'] is not None, trigger=(c['rec'] or {}).get('trigger'),
                                                        boxes=(c['rec'] or {}).get('boxes')) for c in cyc],
                counts={f'k>={k}': sum(1 for e in out if e['k'] >= k) for k in range(1, n + 1)},
                note=(f'k = how many of the last {n} HRRR cycles (00/06/12/18z, this one included) put the segment at P(close) >= 0.5; n = how many of them '
                      'could have (a quiet cycle counts as a forecast of no closure; a cycle that ran covers its boxes only; missing cycles are left out). '
                      'Hindcast skill of the rule: docs/proto/forecast/ENSEMBLE.md.'),
                segments=out)


def cmd_combine(a):
    G = json.load(open(a.gate)); K = combine(a.store, G['issued'], a.n, a.hourly)
    json.dump(K, open(a.out, 'w'), separators=(',', ':')); log('k of n:', K['counts'], [(c['issued'], c['available'], c['trigger']) for c in K['cycles']])


def selftest():
    import tempfile
    d = tempfile.mkdtemp(); B = [100000, 800000, 120000, 820000]
    def w(name, rec): json.dump(rec, open(os.path.join(d, name), 'w'))
    w('2026102312.json', dict(issued='2026-10-23T12:00Z', trigger=True, boxes=[B], runs=[dict(key='b1', box=B, ok=True, segments=[dict(segment=1, p=0.9, x=110000, y=810000, road='A', town='T'), dict(segment=2, p=0.6, x=110500, y=810000, road='B', town='T')])]))
    w('2026102306.json', dict(issued='2026-10-23T06:00Z', trigger=True, boxes=[B], runs=[dict(key='b1', box=B, ok=True, segments=[dict(segment=1, p=0.7, x=110000, y=810000, road='A', town='T')])]))
    w('2026102300.json', dict(issued='2026-10-23T00:00Z', trigger=False, boxes=[], runs=[]))
    # 2026-10-22T18 missing
    K = combine(d, '2026-10-23T12:00Z', 4); S = {e['segment']: e for e in K['segments']}
    assert S[1]['k'] == 2 and S[1]['n'] == 3 and S[2]['k'] == 1 and S[2]['n'] == 3, S
    w('2026102318.json', dict(issued='2026-10-23T18:00Z', trigger=True, boxes=[[0, 0, 1, 1]], runs=[dict(key='b1', box=[0, 0, 1, 1], ok=True, segments=[])]))
    K = combine(d, '2026-10-23T18:00Z', 4); S = {e['segment']: e for e in K['segments']}
    assert S[1]['k'] == 2 and S[1]['n'] == 3, S[1]           # the 18z box is elsewhere: not counted in n; the 18z of the 22nd is now out of range
    assert K['counts'] == {'k>=1': 2, 'k>=2': 1, 'k>=3': 0, 'k>=4': 0}, K['counts']
    w('2026102317.json', dict(issued='2026-10-23T17:00Z', trigger=True, boxes=[B], runs=[dict(key='b1', box=B, ok=True, segments=[dict(segment=1, p=0.8, x=110000, y=810000, road='A', town='T')])]))
    K = combine(d, '2026-10-23T18:00Z', 4, hourly=4); S = {e['segment']: e for e in K['segments']}
    assert K['n_cycles'] == 8 and S[1]['k'] == 3 and S[1]['n'] == 4, S[1]      # + 17z (covers); 16z-14z missing
    print('kofn selftest ok')


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0]); sp = ap.add_subparsers(dest='cmd', required=True)
    p = sp.add_parser('record'); p.add_argument('--gate', required=True); p.add_argument('--run', action='append'); p.add_argument('--store', required=True)
    p = sp.add_parser('combine'); p.add_argument('--gate', required=True); p.add_argument('--store', required=True); p.add_argument('--n', type=int, default=4); p.add_argument('--hourly', type=int, default=0); p.add_argument('--out', required=True)
    sp.add_parser('selftest')
    a = ap.parse_args()
    {'record': cmd_record, 'combine': cmd_combine, 'selftest': lambda a: selftest()}[a.cmd](a)
