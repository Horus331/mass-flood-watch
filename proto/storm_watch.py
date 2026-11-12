"""Storm watch recorder: one line per hour of what fell, what was forecast, and what happened (docs/proto/prospective/storm_<id>/).

    python proto/storm_watch.py record --watch docs/proto/prospective/active_watch.json
    python proto/storm_watch.py selftest

Active only while docs/proto/prospective/active_watch.json exists and the current time is inside its window.  Each run (hourly, via the
keeper) appends to <dir>/record.jsonl, for the hour that ended at the last top of the hour (skipped if already recorded):
  rain        MRMS RadarOnly QPE 1 h over the District 3 box (mean, max, wet share >= 1 mm) - observed, available minutes after the hour
  phase       MRMS PrecipFlag at the end of the hour: share of precipitating District 3 pixels flagged snow (3) or hail (7)
  hrrr        the same hour as forecast by each HRRR cycle 1..6 h before (box mean on the MRMS grid): rain-forecast error by lead
  forecast    the newest published forecast (issued, headline, likely / possible closures, top roads with k of N)
  sentinel    state and reasons (status.json)
  alerts      NWS flood alerts in force touching District 3
  events      MassDOT roadway events in the hour that mention flooding / water / washout / closure, inside the District 3 box
Snapshots each newly published forecast's road list to <dir>/forecasts/<issued>.json (what we said before it happened).
"""
import argparse, datetime as dt, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); sys.path.insert(0, HERE)
DATA = os.path.join(ROOT, 'docs', 'site', 'data')
WATER = re.compile(r'flood|water|washout|wash out|ponding|standing|sinkhole|road closed|closure|culvert', re.I)


def iso(t): return t.strftime('%Y-%m-%dT%H:%MZ')


def jl(p, d=None):
    try: return json.load(open(p))
    except Exception: return d


def rain_hour(t_end):
    import numpy as np, live_feeds as LF
    L = LF.mrms_recent('RadarOnly_QPE_01H_00.00', t_end - dt.timedelta(minutes=5), t_end + dt.timedelta(minutes=10))
    if not L: raise RuntimeError('no RadarOnly_QPE_01H file at ' + iso(t_end))
    t, u = min(L, key=lambda x: abs((x[0] - t_end).total_seconds())); V, la, lo = LF.mrms_box(u); V = np.nan_to_num(V, nan=0.0)
    return dict(product='MRMS RadarOnly_QPE_01H', file_time=iso(t), mean_mm=round(float(V.mean()), 2), max_mm=round(float(V.max()), 1),
                wet_share=round(float((V >= 1).mean()), 3)), (V, la, lo)


def phase(t_end):
    import numpy as np, live_feeds as LF
    L = LF.mrms_recent('PrecipFlag_00.00', t_end - dt.timedelta(minutes=10), t_end + dt.timedelta(minutes=5))   # past hours: AWS keeps the 2-min files
    if not L: return None
    t, u = min(L, key=lambda x: abs((x[0] - t_end).total_seconds())); F, _, _ = LF.mrms_box(u); F = np.nan_to_num(F, nan=-3)
    p = F > 0
    return dict(file_time=iso(t), precip_pixels=int(p.sum()), snow_share=round(float(((F == 3) & p).sum() / max(1, p.sum())), 3),
                hail_share=round(float(((F == 7) & p).sum() / max(1, p.sum())), 3))


def hrrr_leads(t_end, grid):
    import nowcast_hindcast as NH
    V, la, lo = grid; out = {}
    for lead in range(1, 7):
        init = t_end - dt.timedelta(hours=lead)
        try:
            H = NH.hrrr_on(init.replace(tzinfo=None), lead, la, lo)
            if H is not None and H.shape == V.shape: out[str(lead)] = dict(cycle=f'{init:%Y-%m-%d %H}Z', mean_mm=round(float(H.mean()), 2), max_mm=round(float(H.max()), 1))
        except Exception as e: out[str(lead)] = dict(error=repr(e)[:120])
    return out


def events(t0, t1):
    import live_feeds as LF
    p = os.path.join(ROOT, 'docs', 'proto', 'obs', 'massdot_events', f'{t1:%Y-%m}.jsonl'); out = {}
    if not os.path.exists(p): return []
    for line in open(p):
        try: e = json.loads(line)
        except ValueError: continue
        lg = e.get('logged', '')
        if not (iso(t0) <= lg[:16] + 'Z' <= iso(t1) or iso(t0) <= lg <= iso(t1)): continue
        txt = ' '.join(str(e.get(k, '')) for k in ('EventType', 'EventSubType', 'LocationDescription', 'LaneBlockageDescription', 'Description'))
        if not WATER.search(txt): continue
        try: la, lo = float(e['PrimaryLatitude']), float(e['PrimaryLongitude'])
        except (KeyError, ValueError): continue
        if not (LF.LAT[0] <= la <= LF.LAT[1] and LF.LON[0] <= lo <= LF.LON[1]): continue
        out[e['EventId']] = dict(id=e['EventId'], type=e.get('EventSubType'), road=e.get('RoadwayName'), where=e.get('LocationDescription'), lat=la, lon=lo, created=e.get('EventCreatedDate'))
    return list(out.values())


def forecast_now(d):
    F = jl(os.path.join(DATA, 'forecast_status.json'), {}) or {}
    R = jl(os.path.join(DATA, 'forecast_latest', 'roads.json'), {}) or {}
    top = sorted([f for f in R.get('features', []) if f['properties'].get('k')], key=lambda f: (-(f['properties'].get('pi') or 0), -f['properties']['k']))[:15]
    rows = [dict(id=f['id'], road=f['properties'].get('n'), town=f['properties'].get('t'), k=f['properties'].get('k'), n=f['properties'].get('kn'),
                 pi=f['properties'].get('pi')) for f in top]
    out = dict(issued=F.get('issued'), headline=F.get('headline'), likely=(F.get('counts') or {}).get('likely'), possible=(F.get('counts') or {}).get('possible'), top=rows)
    if F.get('issued'):
        snap = os.path.join(d, 'forecasts', F['issued'].replace(':', '') + '.json')
        if not os.path.exists(snap):
            os.makedirs(os.path.dirname(snap), exist_ok=True)
            json.dump(dict(status=F, roads=[dict(id=f['id'], **{k: f['properties'].get(k) for k in ('n', 't', 'k', 'kn', 'pi', 'p', 'w', 'e')}) for f in R.get('features', [])]), open(snap, 'w'))
            out['snapshot'] = os.path.relpath(snap, ROOT)
    return out


def record(a):
    W = jl(a.watch)
    if not W: print('no active watch'); return
    now = dt.datetime.now(dt.timezone.utc).replace(tzinfo=None)
    w0, w1 = (dt.datetime.strptime(x, '%Y-%m-%dT%H:%MZ') for x in W['window'])
    if not (w0 <= now <= w1 + dt.timedelta(hours=2)): print('outside the watch window', W['window']); return
    d = os.path.join(ROOT, W['dir']); os.makedirs(d, exist_ok=True); rec = os.path.join(d, 'record.jsonl')
    last = now.replace(minute=0, second=0, microsecond=0)
    done = set()
    if os.path.exists(rec):
        for line in open(rec):
            try: done.add(json.loads(line)['hour_end'])
            except Exception: pass
    # every hour of the window not recorded yet, newest 12 at most (GitHub's schedule skips hours; MRMS keeps the files)
    todo = [last - dt.timedelta(hours=k) for k in range(11, -1, -1)]
    todo = [t for t in todo if w0 < t <= w1 + dt.timedelta(hours=2) and iso(t) not in done]
    if not todo: print('hour already recorded', iso(last)); forecast_now(d); return
    for t_end in todo: one_hour(t_end, now, d, rec, live=(t_end == last))


def one_hour(t_end, now, d, rec, live):
    R = dict(hour_end=iso(t_end), recorded=iso(now), backfilled=not live); errs = {}
    try: R['rain'], grid = rain_hour(t_end)
    except Exception as e: errs['rain'] = repr(e)[:200]; grid = None
    try: R['phase'] = phase(t_end)
    except Exception as e: errs['phase'] = repr(e)[:200]
    if grid is not None:
        try: R['hrrr'] = hrrr_leads(t_end, grid)
        except Exception as e: errs['hrrr'] = repr(e)[:200]
    if live:
        try: R['forecast'] = forecast_now(d)
        except Exception as e: errs['forecast'] = repr(e)[:200]
        S = jl(os.path.join(DATA, 'status.json'), {}) or {}
        R['sentinel'] = dict(state=S.get('state'), reasons=S.get('reasons')); R['alerts'] = ((S.get('sources') or {}).get('nws') or {}).get('alerts')
    try: R['events'] = events(t_end - dt.timedelta(hours=1), t_end)
    except Exception as e: errs['events'] = repr(e)[:200]
    R['errors'] = errs
    open(rec, 'a').write(json.dumps(R) + '\n')
    r = R.get('rain') or {}; h = (R.get('hrrr') or {}).get('1', {})
    print(f"{iso(t_end)}{'' if live else ' (backfill)'} rain mean {r.get('mean_mm')} max {r.get('max_mm')} | HRRR 1 h ahead {h.get('mean_mm')} | snow share "
          f"{(R.get('phase') or {}).get('snow_share')} | events {len(R.get('events') or [])} | errors {list(errs)}", flush=True)


def selftest():
    assert WATER.search('Flooding') and WATER.search('Road Closed') and not WATER.search('Crash')
    print('storm_watch selftest ok')


if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('cmd'); ap.add_argument('--watch', default='docs/proto/prospective/active_watch.json'); a = ap.parse_args()
    selftest() if a.cmd == 'selftest' else record(a)
