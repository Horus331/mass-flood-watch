"""Baseline B1 of docs/proto/PROTOCOL_v3.md: NWS flash-flood warning polygons (VTEC FF.W) from the IEM storm-based-warning archive.

    python proto/baseline_nws_ffw.py fetch --out docs/proto/baselines/nws_ffw.json      # needs the web (GitHub Actions)
    python proto/baseline_nws_ffw.py selftest

For every storm of docs/proto/obs/catalog.json and catalog_d456.json (locked storms skipped, never queried) all FF.W polygons of WFO BOX
valid at any time in the storm window [t0, t0 + hours] are kept with their valid times, unsimplified.  Polygon updates (SVS) of one
warning are kept as separate rows (same vtec id): the scorer counts a segment inside a warning if its midpoint is inside any polygon of it,
and its hours inside = union of the polygons' valid intervals that contain it.  Fetching only; nothing is scored here.
"""
import argparse, datetime as dt, json, os, sys, time

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
LOCKED = ('aug2015', 'aug2018', 'aug2020', 'jul2018', 'oct2016')        # = score_v2.LOCKED (kept here so fetch needs no model deps)
UA = {'User-Agent': 'mass-flood-watch research (github.com/Horus331/mass-flood-watch)'}


def utc(s):
    if not s: return None
    s = str(s).replace('Z', '+00:00')
    try: t = dt.datetime.fromisoformat(s)
    except ValueError: t = dt.datetime.strptime(s[:12], '%Y%m%d%H%M').replace(tzinfo=dt.timezone.utc)
    return (t if t.tzinfo else t.replace(tzinfo=dt.timezone.utc)).astimezone(dt.timezone.utc)


def iso(t): return t.strftime('%Y-%m-%dT%H:%MZ') if t else None


def storms():
    out = []
    for f, grp in (('catalog.json', 'D3'), ('catalog_d456.json', 'D456')):
        for e in json.load(open(os.path.join(ROOT, 'docs', 'proto', 'obs', f)))['events']:
            if e['id'] in LOCKED: continue
            t0 = utc(e['t0']); out.append(dict(id=e['id'], group=grp, w0=t0, w1=t0 + dt.timedelta(hours=e['hours']), bbox=e['bbox_lonlat']))
    return out


def fetch_window(w0, w1):
    import requests
    tries = [('https://mesonet.agron.iastate.edu/api/1/vtec/sbw_interval.geojson', dict(begints=iso(w0), endts=iso(w1), wfo='BOX')),
             ('https://mesonet.agron.iastate.edu/geojson/sbw.py', dict(sts=f'{w0:%Y%m%d%H%M}', ets=f'{w1:%Y%m%d%H%M}', wfos='BOX')),
             ('https://mesonet.agron.iastate.edu/geojson/sbw.geojson', dict(sts=f'{w0:%Y%m%d%H%M}', ets=f'{w1:%Y%m%d%H%M}', wfo='BOX'))]
    errs = []
    for u, prm in tries:
        for k in range(3):
            try:
                r = requests.get(u, params=prm, headers=UA, timeout=60)
                if r.status_code == 200:
                    J = r.json()
                    if isinstance(J, dict) and 'features' in J: return J['features'], u
                errs.append(f'{u} {r.status_code}'); break
            except Exception as e: errs.append(f'{u} {repr(e)[:80]}'); time.sleep(3 * (k + 1))
    raise RuntimeError('; '.join(errs))


def keep_ffw(feats, w0, w1):
    rows = []
    for f in feats:
        p = {k.lower(): v for k, v in (f.get('properties') or {}).items()}
        if (p.get('phenomena') or '').upper() != 'FF' or (p.get('significance') or '').upper() != 'W' or not f.get('geometry'): continue
        t0 = utc(p.get('polygon_begin') or p.get('issue') or p.get('utc_issue')); t1 = utc(p.get('polygon_end') or p.get('expire') or p.get('utc_expire'))
        if (t1 and t1 < w0) or (t0 and t0 > w1): continue
        rows.append(dict(vtec=f"BOX.FF.W.{p.get('eventid')}.{(t0 or w0):%Y}", status=p.get('status'), begin=iso(t0), end=iso(t1), geometry=f['geometry']))
    return rows


def cmd_fetch(a):
    S = storms(); R = dict(made_by='proto/baseline_nws_ffw.py', protocol='docs/proto/PROTOCOL_v3.md (B1)', made=iso(dt.datetime.now(dt.timezone.utc)), storms={})
    for s in S:
        try:
            feats, used = fetch_window(s['w0'], s['w1']); rows = keep_ffw(feats, s['w0'], s['w1'])
            R['storms'][s['id']] = dict(group=s['group'], window=[iso(s['w0']), iso(s['w1'])], source=used, n_box_all=len(feats),
                                        n_warnings=len({r['vtec'] for r in rows}), polygons=rows)
            print(s['id'], s['group'], 'FFW polygons', len(rows), 'warnings', R['storms'][s['id']]['n_warnings'], flush=True)
        except Exception as e:
            R['storms'][s['id']] = dict(group=s['group'], window=[iso(s['w0']), iso(s['w1'])], error=repr(e)[:300]); print(s['id'], 'FAILED', repr(e)[:200], flush=True)
        time.sleep(1)
    ok = [k for k, v in R['storms'].items() if 'error' not in v]
    R['summary'] = dict(storms=len(S), fetched=len(ok), failed=len(S) - len(ok),
                        with_ffw={g: sum(1 for k in ok if R['storms'][k]['group'] == g and R['storms'][k]['n_warnings']) for g in ('D3', 'D456')})
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True); json.dump(R, open(a.out, 'w'))
    print(json.dumps(R['summary']))
    if len(ok) < len(S): sys.exit(1)


def selftest():
    w0, w1 = utc('2023-09-11T18:00Z'), utc('2023-09-12T06:00Z')
    F = [dict(properties=dict(phenomena='FF', significance='W', eventid=12, polygon_begin='2023-09-11T22:00Z', polygon_end='2023-09-12T02:00Z'), geometry={'type': 'Polygon', 'coordinates': []}),
         dict(properties=dict(phenomena='FA', significance='W', eventid=3, polygon_begin='2023-09-11T22:00Z', polygon_end='2023-09-12T02:00Z'), geometry={'type': 'Polygon'}),
         dict(properties=dict(phenomena='FF', significance='W', eventid=9, polygon_begin='2023-09-10T22:00Z', polygon_end='2023-09-11T02:00Z'), geometry={'type': 'Polygon'})]
    R = keep_ffw(F, w0, w1); assert len(R) == 1 and R[0]['vtec'] == 'BOX.FF.W.12.2023', R
    S = storms(); assert S and not any(s['id'] in LOCKED for s in S)
    print('baseline_nws_ffw selftest ok;', len(S), 'storms (D3', sum(s['group'] == 'D3' for s in S), ')')


if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('cmd'); ap.add_argument('--out', default='docs/proto/baselines/nws_ffw.json'); a = ap.parse_args()
    selftest() if a.cmd == 'selftest' else cmd_fetch(a)
