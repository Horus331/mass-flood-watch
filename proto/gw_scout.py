"""Scout USGS groundwater wells (depth to water, 72019) in and around District 3 and their response to two storms.
Writes docs/proto/groundwater/scout.json and prints a summary. Data: USGS Water Services (site + iv/dv), falling back to the
Water Data OGC API. Scouting only: nothing here enters the model."""
import json, os, sys, io, datetime as dt
import requests
OUT = os.path.join(os.path.dirname(__file__), '..', 'docs', 'proto', 'groundwater')
BBOX = (-72.35, 41.95, -71.30, 42.75)        # District 3 and margin (lon/lat)
STORMS = {'aug2021': ('2021-08-14', '2021-09-10', '2021-08-19'), 'sep2023': ('2023-09-01', '2023-10-05', '2023-09-11')}
UA = {'User-Agent': 'mass-flood-watch research (WPI)'}


def get(u):
    import time
    for i in range(5):
        try:
            r = requests.get(u, headers=UA, timeout=120)
            if r.status_code < 500: return r
        except requests.RequestException as e:
            print('retry', i + 1, type(e).__name__)
        time.sleep(5 * (i + 1))
    return None


def rdb(text):
    rows = [l.split('\t') for l in text.splitlines() if l and not l.startswith('#')]
    if not rows: return []
    hdr = rows[0]; return [dict(zip(hdr, r)) for r in rows[2:]]


def sites():
    out = {}
    for dtype in ('iv', 'dv'):
        u = ('https://waterservices.usgs.gov/nwis/site/?format=rdb&bBox=%.2f,%.2f,%.2f,%.2f&parameterCd=72019&siteType=GW'
             '&hasDataTypeCd=%s&siteStatus=all&outputDataTypeCd=%s' % (*BBOX, dtype, dtype))
        r = get(u)
        print(dtype, 'site query', r.status_code if r else None, len(r.text) if r else 0)
        if not r or r.status_code != 200: continue
        for s in rdb(r.text):
            if s.get('parm_cd') not in (None, '', '72019'): continue
            d = out.setdefault(s['site_no'], dict(site=s['site_no'], name=s.get('station_nm'), lat=float(s['dec_lat_va']), lon=float(s['dec_long_va']), types={}))
            d['types'][dtype] = dict(begin=s.get('begin_date'), end=s.get('end_date'), count=s.get('count_nu'))
    return list(out.values())


def series(site, dtype, a, b):
    u = f'https://waterservices.usgs.gov/nwis/{dtype}/?format=json&sites={site}&parameterCd=72019&startDT={a}&endDT={b}&siteStatus=all'
    r = get(u)
    if not r or r.status_code != 200: return []
    ts = r.json().get('value', {}).get('timeSeries', [])
    vals = []
    for t in ts:
        for blk in t['values']:
            for v in blk['value']:
                try: vals.append((v['dateTime'][:16], float(v['value'])))
                except Exception: pass
    return sorted(vals)


def response(vals, onset):
    """Depth to water falls when the water table rises. Rise = pre-storm depth (mean of the 3 days before onset) minus the
    shallowest depth after onset; lag = days from onset to that minimum."""
    if len(vals) < 5: return None
    t0 = dt.datetime.fromisoformat(onset)
    pre = [v for t, v in vals if t0 - dt.timedelta(days=3) <= dt.datetime.fromisoformat(t) < t0]
    post = [(t, v) for t, v in vals if dt.datetime.fromisoformat(t) >= t0]
    if not pre or not post: return None
    tmin, vmin = min(post, key=lambda x: x[1]); base = sum(pre) / len(pre)
    wk = [(t, v) for t, v in post if dt.datetime.fromisoformat(t) < t0 + dt.timedelta(days=7)]
    t7, v7 = min(wk, key=lambda x: x[1]) if wk else (tmin, vmin)
    return dict(rise7_m=round((base - v7) * 0.3048, 2), lag7_h=round((dt.datetime.fromisoformat(t7) - t0).total_seconds() / 3600, 1),pre_depth_m=round(base * 0.3048, 2), min_depth_m=round(vmin * 0.3048, 2), rise_m=round((base - vmin) * 0.3048, 2),
                lag_days=round((dt.datetime.fromisoformat(tmin) - t0).total_seconds() / 86400, 1), n=len(vals))


def main():
    os.makedirs(OUT, exist_ok=True)
    S = sites(); print('wells with 72019:', len(S))
    for s in S:
        s['storms'] = {}
        for k, (a, b, onset) in STORMS.items():
            for dtype in ('iv', 'dv'):
                if dtype not in s['types']: continue
                ty = s['types'][dtype]
                if (ty.get('begin') or '9999') > a or (ty.get('end') or '0000') < b: continue
                v = series(s['site'], dtype, a, b); r = response(v, onset)
                if r:
                    hourly = {}
                    for t, x in v: hourly.setdefault(t[:13], x)
                    s['storms'][k] = dict(r, data=dtype, hourly_depth_ft=[[t, x] for t, x in sorted(hourly.items())]); break
    json.dump(dict(made=dt.datetime.utcnow().isoformat(timespec='minutes') + 'Z', bbox=BBOX, storms=STORMS, wells=S), open(f'{OUT}/scout.json', 'w'), indent=1)
    for s in S:
        if s['storms']: print(s['site'], s['name'], s['storms'])


if __name__ == '__main__':
    main()
