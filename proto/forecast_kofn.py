"""Live time-lagged HRRR ensemble for the road-closure forecast (docs/proto/forecast/ENSEMBLE.md): 'closed in k of 8 forecasts'.

LIVE (forecast.yml, default on; repository variable FORECAST_ENSEMBLE=0 or the workflow input ensemble=0 falls back to the single cycle):
    python proto/forecast_kofn.py members  --gate gate.json [--single] --github-output $GITHUB_OUTPUT
        when the gate of the issue cycle T fires: the 8 validated members (T, T-6, T-12, T-18 h synoptic + T-1..T-4 h hourly), each member's
        own gate on the hours after T, and the boxes = issue-cycle boxes first, then the members' boxes, overlaps > 25 % dropped, at most
        FORECAST_MAX_BOXES; writes the box list back into gate.json and the member x box job matrix ('jobs').
    python proto/forecast_kofn.py ensemble --gate gate.json --member <init>:<box id>=<prototype dir> ... --out kofn.json [--viewers v.txt --prefix forecast_latest]
        per segment k = members that close it (P(close) >= 0.5 in a run whose box holds it), n = members with a finished run covering it;
        likely = k >= 2 (the rule validated out of sample), possible = k = 1.  v.txt: one 'key dir box' line per box for the viewer replay
        (the issue cycle's run, else the newest member that finished).
    python proto/forecast_kofn.py pack --kofn kofn.json --key forecast_latest --box b1
        adds k / kn to docs/site/data/<key>/roads.json (and the segments only other members close, geometry from docs/graph_segments.json)
        and a 'kofn' summary to its meta.json, for the viewer's agreement colouring.

Cross-cycle variant (not used by forecast.yml any more):

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
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'sim', 'colab'))
import numpy as np

CLOSE_P = 0.5


def log(*a): print(*a, flush=True)


def _ts(s):
    import pandas as pd
    t = pd.Timestamp(s.replace('Z', '') if isinstance(s, str) else s)
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


# ------------------------------------------------------------------ live 8-member ensemble
HOURLY_LAGS = (1, 2, 3, 4); SYN_LAGS = (6, 12, 18)


def member_inits(T, single=False):
    import pandas as pd
    T = _ts(T)
    if single: return [T]
    return [T] + [T - pd.Timedelta(hours=h) for h in SYN_LAGS] + [T - pd.Timedelta(hours=h) for h in HOURLY_LAGS]


def _overlap(a, b):
    w = max(0, min(a[2], b[2]) - max(a[0], b[0])); h = max(0, min(a[3], b[3]) - max(a[1], b[1]))
    return w * h / float((a[2] - a[0]) * (a[3] - a[1]))


def cmd_members(a):
    import forecast as FC, hrrr_rain
    G = json.load(open(a.gate)); T = _ts(G['issued']); mem = member_inits(T, a.single)
    boxes = [dict(b, member=f'{T:%Y-%m-%dT%H}Z') for b in G['boxes']]
    if G['trigger'] and not a.single and len(boxes) < FC.MAX_BOXES:
        for m in mem[1:]:
            try:
                H = hrrr_rain.horizon(m); R, g, miss = FC.fetch_gate(m, H)
                lag = int((T - m).total_seconds() // 3600); R = R[lag:]          # only the hours after the issue time
                if len(R) < 3: continue
                E = FC.evaluate(T, len(R), R, g)
                log(f'member {m:%d %H}z: towns over {E["towns_over"][:5]}, boxes {[b["box"] for b in E["boxes"]]}')
                for b in E['boxes'] if E['towns_over'] else []:
                    if len(boxes) >= FC.MAX_BOXES: break
                    if all(_overlap(b['box'], c['box']) <= 0.25 for c in boxes): boxes.append(dict(b, member=f'{m:%Y-%m-%dT%H}Z'))
            except (Exception, SystemExit) as e: log(f'member {m} gate failed: {e!r}'[:200])
    for i, b in enumerate(boxes): b['id'] = f'b{i + 1}'
    G['boxes_issue'] = G['boxes']; G['boxes'] = boxes
    G['ensemble'] = dict(members=[f'{m:%Y-%m-%dT%H}Z' for m in mem], rule='likely closed: >= 2 of the 8 members; possible: 1 of 8' if len(mem) > 1 else 'single cycle',
                         basis='docs/proto/forecast/ENSEMBLE.md')
    json.dump(G, open(a.gate, 'w'), indent=1)
    jobs = [dict(id=b['id'], box=','.join(str(int(v)) for v in b['box']), init=f'{m:%Y-%m-%dT%H}Z', m=f'{m:%d%H}') for m in mem for b in boxes] if G['trigger'] else []
    log(f'{len(mem)} member(s), {len(boxes)} box(es), {len(jobs)} flood job(s)')
    if a.github_output:
        with open(a.github_output, 'a') as f: f.write('jobs=' + json.dumps(jobs) + '\n')


def _box_of(key, G):
    bid = key.rsplit('_', 1)[-1]
    return next((b for b in G['boxes'] if b['id'] == bid), None)


def ensemble(G, members):
    """members: list of (init str, box id, prototype dir or None).  -> kofn dict."""
    mem = G.get('ensemble', {}).get('members') or sorted({m for m, _, _ in members}, reverse=True)
    B = {b['id']: b['box'] for b in G['boxes']}
    runs = {}
    for m, bid, d in members:
        try: runs[(m, bid)] = closures(d) if d and os.path.exists(os.path.join(d, 'summary.json')) else None
        except Exception as e: log('member', m, bid, 'unreadable', repr(e)[:120]); runs[(m, bid)] = None
    seg = {}
    for (m, bid), cl in runs.items():
        for s_ in cl or []:
            e = seg.setdefault(s_['segment'], dict(segment=s_['segment'], road=s_['road'], town=s_['town'], x=s_['x'], y=s_['y'], members=[], p_max=0.0))
            if m not in e['members']: e['members'].append(m)
            e['p_max'] = max(e['p_max'], s_['p'])
    out = []
    for e in seg.values():
        inb = [bid for bid, b in B.items() if b[0] <= e['x'] < b[2] and b[1] <= e['y'] < b[3]]
        e['n'] = sum(1 for m in mem if any(runs.get((m, bid)) is not None for bid in inb)); e['k'] = len(e['members'])
        e['box'] = inb[0] if inb else None; e['members'].sort(reverse=True)
        e['class'] = 'likely' if e['k'] >= 2 else 'possible'; out.append(e)
    out.sort(key=lambda e: (-e['k'], -e['p_max']))
    done = {bid: [m for m in mem if runs.get((m, bid)) is not None] for bid in B}
    return dict(rule='likely closed = closed (P >= 0.5) in >= 2 of the 8 time-lagged HRRR members; possible = 1 of 8 (ENSEMBLE.md, validated on 9 storms)',
                members=mem, n_members=len(mem), finished=done, likely=sum(e['k'] >= 2 for e in out), possible=sum(e['k'] == 1 for e in out),
                counts={f'k>={k}': sum(1 for e in out if e['k'] >= k) for k in range(1, len(mem) + 1)}, segments=out)


def cmd_ensemble(a):
    G = json.load(open(a.gate)); M = []
    for spec in a.member or []:
        mb, _, d = spec.partition('='); m, _, bid = mb.partition(':'); M.append((m, bid, d or None))
    K = ensemble(G, M); json.dump(K, open(a.out, 'w'), separators=(',', ':'))
    log('ensemble:', K['likely'], 'likely,', K['possible'], 'possible; finished', {k: len(v) for k, v in K['finished'].items()})
    if a.viewers:
        mem = K['members']; lines = []
        for b in G['boxes']:
            have = {m: d for m, bid, d in M if bid == b['id'] and d and os.path.exists(os.path.join(d, 'summary.json'))}
            m = next((m for m in mem if m in have), None)        # the issue cycle first, then the members in order
            if m: lines.append(f"{a.prefix if b['id'] == 'b1' else a.prefix + '_' + b['id']} {have[m]} {b['id']} {m}")
        open(a.viewers, 'w').write('\n'.join(lines) + ('\n' if lines else ''))


def cmd_memberargs(a):
    G = json.load(open(a.gate)); out = []
    for m in G.get('ensemble', {}).get('members', []) if G.get('trigger') else []:
        t = _ts(m)
        for b in G['boxes']:
            n = f"proto_{t:%d%H}_{b['id']}"; out.append(f"--member {m}:{b['id']}={os.path.join(a.arts, n, n)}")
    print(' '.join(out))


def _seg_lines(S, i):
    return [[[round(float(x), 5), round(float(y), 5)] for x, y in zip(np.cumsum(d[0::2]) / 1e5, np.cumsum(d[1::2]) / 1e5)] for d in S['geo'][i]]


def cmd_pack(a):
    root = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
    od = a.dir or os.path.join(root, 'docs', 'site', 'data', a.key)
    K = json.load(open(a.kofn)); mine = {e['segment']: e for e in K['segments'] if e.get('box') == a.box}
    R = json.load(open(os.path.join(od, 'roads.json'))); have = set()
    for f in R['features']:
        e = mine.get(int(f['id']))
        if e: f['properties']['k'] = e['k']; f['properties']['kn'] = e['n']; have.add(int(f['id']))
    miss = [e for sid, e in mine.items() if sid not in have]
    if miss:
        S = json.load(open(a.segments or os.path.join(root, 'docs', 'graph_segments.json'))); P = S['props']
        cls = {'interstate': 1, 'arterial': 2}
        for e in miss:
            i = e['segment']
            R['features'].append(dict(type='Feature', id=i, geometry=dict(type='MultiLineString', coordinates=_seg_lines(S, i)),
                                      properties=dict(n=P['road'][i] or e['road'] or '', t=P['town'][i] or e['town'] or '', c=0, p=0, m=0, k=e['k'], kn=e['n'],
                                                      w=f"closed in {e['k']} of the {K['n_members']} forecast runs (not in the run shown)")))
    json.dump(R, open(os.path.join(od, 'roads.json'), 'w'), separators=(',', ':'))
    M = json.load(open(os.path.join(od, 'meta.json')))
    M['kofn'] = dict(n=K['n_members'], finished=len(K['finished'].get(a.box, [])), likely=sum(e['k'] >= 2 for e in mine.values()),
                     possible=sum(e['k'] == 1 for e in mine.values()), rule='likely closed: >= 2 of 8 forecast runs agree; possible: 1 of 8')
    json.dump(M, open(os.path.join(od, 'meta.json'), 'w'), separators=(',', ':'))
    log('pack', od, M['kofn'], 'added', len(miss), 'segments')


def selftest_ensemble():
    import tempfile
    d = tempfile.mkdtemp()
    def mk(name, segs):
        p = os.path.join(d, name); os.makedirs(p)
        json.dump(dict(storm_start='2026-10-23T12:00Z', rain_hourly_mean_mm=[5]), open(os.path.join(p, 'summary.json'), 'w'))
        json.dump(dict(type='FeatureCollection', features=[dict(type='Feature', geometry=dict(type='LineString', coordinates=[[-73.3, 41.6], [-73.299, 41.6]]),
                                                               properties=dict(segment=s_, p_close=0.9, d=[0, 40], road='A', town='T')) for s_ in segs]), open(os.path.join(p, 'segments.geojson'), 'w'))
        return p
    G = dict(boxes=[dict(id='b1', box=[40000, 810000, 60000, 830000])], ensemble=dict(members=['2026-10-23T12Z', '2026-10-23T06Z', '2026-10-23T11Z']))
    K = ensemble(G, [('2026-10-23T12Z', 'b1', mk('a', [1])), ('2026-10-23T06Z', 'b1', mk('b', [1, 2])), ('2026-10-23T11Z', 'b1', None)])
    S = {e['segment']: e for e in K['segments']}
    assert S[1]['k'] == 2 and S[1]['n'] == 2 and S[1]['class'] == 'likely' and S[2]['k'] == 1 and K['likely'] == 1 and K['possible'] == 1, S
    assert len(member_inits('2026-10-23T12:00Z')) == 8 and abs(_overlap([0, 0, 2, 2], [1, 0, 3, 2]) - 0.5) < 1e-9


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
    selftest_ensemble()
    print('kofn selftest ok')


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0]); sp = ap.add_subparsers(dest='cmd', required=True)
    p = sp.add_parser('record'); p.add_argument('--gate', required=True); p.add_argument('--run', action='append'); p.add_argument('--store', required=True)
    p = sp.add_parser('combine'); p.add_argument('--gate', required=True); p.add_argument('--store', required=True); p.add_argument('--n', type=int, default=4); p.add_argument('--hourly', type=int, default=0); p.add_argument('--out', required=True)
    p = sp.add_parser('members'); p.add_argument('--gate', required=True); p.add_argument('--single', action='store_true'); p.add_argument('--github-output')
    p = sp.add_parser('ensemble'); p.add_argument('--gate', required=True); p.add_argument('--member', action='append'); p.add_argument('--out', required=True)
    p.add_argument('--viewers'); p.add_argument('--prefix', default='forecast_latest')
    p = sp.add_parser('memberargs'); p.add_argument('--gate', required=True); p.add_argument('--arts', default='arts')
    p = sp.add_parser('pack'); p.add_argument('--kofn', required=True); p.add_argument('--key', required=True); p.add_argument('--box', required=True); p.add_argument('--dir'); p.add_argument('--segments')
    sp.add_parser('selftest')
    a = ap.parse_args()
    {'record': cmd_record, 'combine': cmd_combine, 'members': cmd_members, 'ensemble': cmd_ensemble, 'pack': cmd_pack, 'memberargs': cmd_memberargs, 'selftest': lambda a: selftest()}[a.cmd](a)
