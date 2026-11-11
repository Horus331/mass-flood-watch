"""Sentinel: storm state QUIET / WATCH / ACTIVE for District 3, and when every live source last updated (docs/proto/live/SENTINEL.md).

    python proto/sentinel.py run [--github-output $GITHUB_OUTPUT]     # every ~10 min on GitHub Actions (sentinel.yml)
    python proto/sentinel.py selftest

Light by design (< 1 min): it reads NWS alerts (api.weather.gov), the newest MRMS radar 1 h rain over the District 3 box, the newest HRRR
cycle on AWS, and the freshness of the files the other workflows write (forecast, live feeds, USGS gauges).  It writes
docs/site/data/status.json.  It does not start any model run; what each state should start is wired in a later phase.

States (fixed 11 Nov 2026 before the first run; SENTINEL.md):
  ACTIVE  a Flash Flood Warning or Flood Warning in force touching District 3, or radar 1 h rain >= 25 mm anywhere in the District 3 box
  WATCH   a Flood Watch / Flash Flood Watch / Flood Advisory in force touching District 3, or radar 1 h rain >= 10 mm, or the newest forecast's
          rain gate triggered (not forced) with its window still open
  QUIET   otherwise
  Hysteresis: a lower state is entered only after 60 min with no condition of the higher one.
Commit rule (sentinel.yml): when the state changes, else when status.json is older than 60 min (QUIET) or 15 min (WATCH/ACTIVE).
"""
import argparse, datetime as dt, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
DATA = os.path.join(ROOT, 'docs', 'site', 'data'); OUT = os.path.join(DATA, 'status.json')
WARN = ('Flash Flood Warning', 'Flood Warning'); WATCHEV = ('Flood Watch', 'Flash Flood Watch', 'Flood Advisory')
RAIN_ACTIVE, RAIN_WATCH = 25.0, 10.0; HOLD_MIN = 60; ORDER = ('QUIET', 'WATCH', 'ACTIVE')
HRRR = 'https://noaa-hrrr-bdp-pds.s3.amazonaws.com'


def utcnow(): return dt.datetime.now(dt.timezone.utc).replace(tzinfo=None, second=0, microsecond=0)


def iso(t): return t.strftime('%Y-%m-%dT%H:%MZ') if t else None


def pt(s):
    if not s: return None
    s = str(s).replace('Z', '').replace('+00:00', '')
    for f in ('%Y-%m-%dT%H:%M:%S', '%Y-%m-%dT%H:%M'):
        try: return dt.datetime.strptime(s[:19 if f.endswith('%S') else 16], f)
        except ValueError: pass
    return None


def jload(p):
    try: return json.load(open(p))
    except Exception: return None


def src_nws(now):
    os.environ['ARCHIVE_ALERT_EVENTS'] = ','.join(WARN + WATCHEV)
    import storm_archive as SA
    A = SA.alerts_live(0.25, now)
    if A.get('query') is None and not A.get('alerts'): raise RuntimeError('api.weather.gov unreachable')
    live = [a for a in A['alerts'] if (pt(a.get('end')) or now) >= now and (pt(a.get('start')) or now) <= now + dt.timedelta(minutes=5)]
    return dict(last=iso(now), next='real time (checked every run)', alerts=[dict(event=a['event'], start=a['start'], end=a['end'], towns=a['towns'][:12]) for a in live])


def src_radar(now):
    import live_feeds as LF
    t, u = LF.mrms_latest('RadarOnly_QPE_01H_00.00', 30, now); V, _, _ = LF.mrms_box(u)
    import numpy as np
    return dict(last=iso(t), next=iso(t + dt.timedelta(minutes=2)), product='MRMS RadarOnly QPE 1 h', max_1h_mm=round(float(np.nanmax(V)) if np.isfinite(V).any() else 0.0, 1))


def src_hrrr(now):
    import requests
    for h in range(0, 6):
        c = now.replace(minute=0) - dt.timedelta(hours=h)
        u = f'{HRRR}/hrrr.{c:%Y%m%d}/conus/hrrr.t{c:%H}z.wrfsfcf18.grib2.idx'
        if requests.head(u, timeout=20).status_code == 200:
            return dict(last=iso(c), next=iso(c + dt.timedelta(hours=1, minutes=50)), cycle=f'{c:%Y-%m-%d %H}Z', note='newest cycle with 18 h out on AWS')
    raise RuntimeError('no HRRR cycle in the last 6 h on AWS')


def src_files(now):
    """Freshness of what the other workflows write (no fetching)."""
    out = {}
    F = jload(os.path.join(DATA, 'forecast_status.json')) or {}
    out['forecast'] = dict(last=F.get('built'), issued=F.get('issued'), next='every 6 h (HRRR 00/06/12/18Z cycles, ~4 h later)', state=F.get('state'),
                           headline=F.get('headline'), gate=bool((F.get('gate') or {}).get('trigger')) and not (F.get('gate') or {}).get('forced'),
                           valid=F.get('valid'))
    L = jload(os.path.join(DATA, 'live', 'status.json')) or {}
    mk = pt(L.get('made'))
    out['live_feeds'] = dict(last=L.get('made'), next=iso(mk + dt.timedelta(hours=1)) if mk else None,
                             feeds={k: v.get('state') for k, v in (L.get('feeds') or {}).items()})
    G = jload(os.path.join(DATA, 'live', 'gauges.json')) or {}
    gt = pt(G.get('generated'))
    out['usgs_gauges'] = dict(last=iso(gt) if gt else None, next=iso(gt + dt.timedelta(hours=1)) if gt else None, gauges=G.get('n'),
                              note='USGS updates every ~15 min; this site reads them hourly (live feeds)')
    return out


def decide(S, now):
    """-> (raw state, [reasons])"""
    R = {'ACTIVE': [], 'WATCH': []}
    for a in (S.get('nws') or {}).get('alerts', []):
        (R['ACTIVE'] if a['event'] in WARN else R['WATCH']).append(f"{a['event']} until {a['end']} ({', '.join(a['towns'][:4])})")
    m = (S.get('radar') or {}).get('max_1h_mm')
    if m is not None:
        if m >= RAIN_ACTIVE: R['ACTIVE'].append(f'radar 1 h rain {m:g} mm >= {RAIN_ACTIVE:g}')
        elif m >= RAIN_WATCH: R['WATCH'].append(f'radar 1 h rain {m:g} mm >= {RAIN_WATCH:g}')
    f = S.get('forecast') or {}
    v1 = pt((f.get('valid') or [None, None])[1])
    if f.get('gate') and v1 and v1 >= now: R['WATCH'].append(f"forecast rain over the flood-model trigger (issued {f.get('issued')})")
    st = 'ACTIVE' if R['ACTIVE'] else 'WATCH' if R['WATCH'] else 'QUIET'
    return st, R['ACTIVE'] + R['WATCH']


def hysteresis(raw, prev, now):
    """-> (state, since, last_condition).  Up (or same) at once; down only after HOLD_MIN minutes without the current state's condition.
    last_condition = when the current state's own condition was last seen."""
    N = iso(now)
    if not prev or prev.get('state') not in ORDER: return raw, N, N
    ps = prev['state']; lc = pt(prev.get('last_condition')) or now
    if ORDER.index(raw) >= ORDER.index(ps): return raw, (prev.get('since') or N) if raw == ps else N, N
    if (now - lc).total_seconds() >= HOLD_MIN * 60: return raw, N, N
    return ps, prev.get('since') or N, iso(lc)


def run(a):
    now = utcnow(); prev = jload(OUT); S = {}; errors = {}
    for name, fn in (('nws', src_nws), ('radar', src_radar), ('hrrr', src_hrrr)):
        try: S[name] = fn(now)
        except Exception as e: errors[name] = repr(e)[:300]; S[name] = dict(error=errors[name], last=((prev or {}).get('sources', {}).get(name) or {}).get('last'))
    S.update(src_files(now))
    raw, reasons = decide(S, now); state, since, lastc = hysteresis(raw, prev, now)
    blind = 'nws' in errors and 'radar' in errors
    if blind:   # cannot see warnings or rain: keep the previous state, say so, and fail the job so an Issue is opened
        state, since, lastc = ((prev or {}).get('state') or 'QUIET'), ((prev or {}).get('since') or iso(now)), (prev or {}).get('last_condition')
        reasons = reasons + ['NWS alerts and radar both unreachable: state held from the last good check']
    out = dict(made=iso(now), made_by='proto/sentinel.py', doc='docs/proto/live/SENTINEL.md', state=state, blind=blind, since=since, raw_state=raw,
               last_condition=lastc, reasons=reasons or ['no warning, watch or heavy rain in District 3'], sources=S, errors=errors,
               rules=dict(ACTIVE=f'Flash Flood / Flood Warning in District 3, or radar 1 h rain >= {RAIN_ACTIVE:g} mm',
                          WATCH=f'Flood Watch / Flash Flood Watch / Flood Advisory in District 3, radar 1 h rain >= {RAIN_WATCH:g} mm, or forecast rain over the model trigger',
                          QUIET='otherwise', hold_min=HOLD_MIN))
    json.dump(out, open(OUT, 'w'), indent=1)
    changed = not prev or prev.get('state') != state
    age = (now - (pt((prev or {}).get('made')) or now - dt.timedelta(days=1))).total_seconds() / 60
    commit = changed or age >= (60 if state == 'QUIET' else 15) - 3
    print(f"state {state} (raw {raw}, since {since}); {'; '.join(reasons) or 'quiet'}; errors {list(errors)}; commit {commit}", flush=True)
    if a.github_output:
        with open(a.github_output, 'a') as f: f.write(f"state={state}\nchanged={'true' if changed else 'false'}\ncommit={'true' if commit else 'false'}\nerrors={','.join(errors)}\n")
    return 1 if blind else 0


def selftest():
    now = dt.datetime(2026, 11, 11, 12, 0)
    S = dict(nws=dict(alerts=[]), radar=dict(max_1h_mm=3.0), forecast=dict(gate=False))
    assert decide(S, now)[0] == 'QUIET'
    S['radar']['max_1h_mm'] = 12; assert decide(S, now)[0] == 'WATCH'
    S['nws']['alerts'] = [dict(event='Flash Flood Warning', end='2026-11-11T14:00Z', towns=['Worcester'])]; assert decide(S, now)[0] == 'ACTIVE'
    S = dict(nws=dict(alerts=[]), radar=dict(max_1h_mm=0), forecast=dict(gate=True, valid=['2026-11-11T06:00Z', '2026-11-13T06:00Z'], issued='x'))
    assert decide(S, now)[0] == 'WATCH'
    # hysteresis: up at once, down only after 60 min
    st, since, lc = hysteresis('ACTIVE', dict(state='QUIET', since='2026-11-11T10:00Z'), now); assert st == 'ACTIVE' and since == '2026-11-11T12:00Z'
    p = dict(state='ACTIVE', since='2026-11-11T11:00Z', last_condition='2026-11-11T11:30Z')
    assert hysteresis('QUIET', p, now)[0] == 'ACTIVE'
    assert hysteresis('QUIET', p, now + dt.timedelta(minutes=31))[0] == 'QUIET'
    assert hysteresis('WATCH', p, now + dt.timedelta(minutes=31))[0] == 'WATCH'
    print('sentinel selftest ok')


if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('cmd'); ap.add_argument('--github-output'); a = ap.parse_args()
    sys.exit(selftest() or 0 if a.cmd == 'selftest' else run(a))
