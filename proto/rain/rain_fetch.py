"""Fetch everything the rain-forcing study needs for one catalogue storm, small enough to commit (docs/proto/rain/RAIN.md).

    python proto/rain/rain_fetch.py --storm jul2023 --out docs/proto/rain/data

Needs the internet (GitHub Actions: .github/workflows/rain_test.yml mode=fetch). Writes <out>/<storm>/:
  products.json      MRMS products on AWS for the storm days (file count and spacing): which sub-hourly products exist
  gauges.json        rain gauges in the storm box + 0.35 deg: IEM ASOS 1-min precip (clock-hour and 5-min sums), USGS 00045, ACIS daily
                     (CoCoRaHS / COOP / GHCN-D, with the observation hour)
  mrms_box.npz       over the run window, on the native 0.01 deg grid, box + 0.06 deg: Pass2 hourly, PrecipRate 2-min (mm/h, float16),
                     RadarOnly_QPE_15M (if on AWS) -> sub-hourly analysis offline
  mrms_region.npz    Pass2 hourly over the gauge region for the daily-gauge window (run day -1 .. +1, 72 h), float16
"""
import argparse, io, json, os, sys, time
import numpy as np
import pandas as pd

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')
sys.path.insert(0, os.path.join(ROOT, 'sim', 'colab'))
import lf_subhourly as SH  # noqa: E402

BUF = 0.35


def get(url, tries=4, timeout=120, **kw):
    import requests
    for k in range(tries):
        try:
            r = requests.get(url, timeout=timeout, **kw)
            if r.status_code == 200: return r
            print('  HTTP', r.status_code, url[:140])
            if r.status_code in (400, 404): return None
        except Exception as e: print('  err', repr(e)[:100], url[:120])
        time.sleep(3 * (k + 1))
    return None


def products(days):
    out = {}
    r = get(f'{SH.S3}/?list-type=2&prefix=CONUS/&delimiter=/')
    allp = [] if r is None else sorted(set(__import__('re').findall(r'<Prefix>CONUS/([^<]+)/</Prefix>', r.text)))
    out['_all_products'] = allp
    want = [p for p in allp if any(s in p for s in ('PrecipRate', 'QPE', 'RadarOnly', 'MultiSensor', 'PrecipFlag', 'SeamlessHSR'))]
    for p in want:
        e = {}
        for d in days:
            ks = sorted(SH.list_keys(p, d))
            if ks:
                gaps = np.diff([k.value for k in ks]) / 6e10
                e[f'{d:%Y-%m-%d}'] = dict(n=len(ks), first=f'{ks[0]:%H:%M:%S}', last=f'{ks[-1]:%H:%M:%S}', median_step_min=float(np.median(gaps)) if len(gaps) else None)
            else: e[f'{d:%Y-%m-%d}'] = dict(n=0)
        out[p] = e
    return out


def asos_stations(bb):
    st = []
    for net in ('MA_ASOS', 'CT_ASOS', 'RI_ASOS', 'NH_ASOS'):
        r = get(f'https://mesonet.agron.iastate.edu/geojson/network/{net}.geojson')
        if r is None: continue
        for f in r.json().get('features', []):
            lo, la = f['geometry']['coordinates'][:2]
            if bb[0] - BUF <= lo <= bb[2] + BUF and bb[1] - BUF <= la <= bb[3] + BUF:
                st.append(dict(id=f['properties'].get('sid') or f['id'], name=f['properties'].get('sname'), lon=lo, lat=la, network=net))
    return st


def asos_1min(sid, t0, t1):
    u = (f'https://mesonet.agron.iastate.edu/cgi-bin/request/asos1min.py?station={sid}&vars=precip&sts={t0:%Y-%m-%dT%H:%MZ}'
         f'&ets={t1:%Y-%m-%dT%H:%MZ}&sample=1min&what=download&delim=comma&tz=UTC')
    r = get(u, timeout=180)
    if r is None or not r.text.strip(): return None
    df = pd.read_csv(io.StringIO(r.text))
    tc = [c for c in df.columns if 'valid' in c.lower()]; pc = [c for c in df.columns if 'precip' in c.lower()]
    if not tc or not pc or df.empty: return None
    df['t'] = pd.to_datetime(df[tc[0]], utc=True).dt.tz_convert(None)
    df['p'] = pd.to_numeric(df[pc[0]], errors='coerce')
    return df[['t', 'p']]


def asos_hourly(sid, t0, t1):
    """Fallback: METAR p01i (inches since the last routine report ~:51-:56) -> hour ending at the routine report."""
    u = (f'https://mesonet.agron.iastate.edu/cgi-bin/request/asos.py?station={sid}&data=p01i&year1={t0.year}&month1={t0.month}&day1={t0.day}'
         f'&hour1={t0.hour}&year2={t1.year}&month2={t1.month}&day2={t1.day}&hour2={t1.hour}&tz=Etc/UTC&format=onlycomma&missing=empty&trace=0.0001&report_type=3')
    r = get(u, timeout=180)
    if r is None or not r.text.strip(): return None
    df = pd.read_csv(io.StringIO(r.text)); df['t'] = pd.to_datetime(df['valid']); df['p'] = pd.to_numeric(df['p01i'], errors='coerce')
    df = df[(df['t'].dt.minute >= 50) & (df['t'].dt.minute <= 59)]
    return df[['t', 'p']]


def usgs_rain(bb, t0, t1):
    """USGS 00045 (precipitation, inches per 15-min/5-min increment) in the box + BUF, via proto/usgs_api.py (OGC API; the legacy
    WaterServices bBox query is its fallback until 22 Feb 2027).  t0/t1: naive UTC timestamps."""
    sys.path.insert(0, os.path.join(ROOT, 'proto')); import usgs_api as U
    G, used = U.iv(bbox=(bb[0] - BUF, bb[1] - BUF, bb[2] + BUF, bb[3] + BUF), start=f'{t0:%Y-%m-%dT%H:%M}Z', end=f'{t1:%Y-%m-%dT%H:%M}Z',
                   params=('00045',), meta=False)
    out = []
    for sid, g in sorted(G.items()):
        vals = g['series'].get('00045') or []
        if not vals: continue
        t = pd.to_datetime([v[0] for v in vals], utc=True).tz_convert(None); p = np.array([v[1] for v in vals], float) * 25.4
        out.append(dict(id='USGS' + sid, name=g['name'], lon=g['lon'], lat=g['lat'], kind='usgs_iv',
                        series=[[f'{a:%Y-%m-%dT%H:%M}', None if not np.isfinite(b) else round(float(b), 2)] for a, b in zip(t, p)]))
    return out


def acis_daily(bb, d0, d1):
    body = dict(bbox=f'{bb[0] - BUF:.3f},{bb[1] - BUF:.3f},{bb[2] + BUF:.3f},{bb[3] + BUF:.3f}', sdate=f'{d0:%Y-%m-%d}', edate=f'{d1:%Y-%m-%d}',
                elems=[dict(name='pcpn', add='t')], meta='name,ll,sids')
    import requests
    for k in range(4):
        try:
            r = requests.post('https://data.rcc-acis.org/MultiStnData', json=body, timeout=180)
            if r.status_code == 200: break
        except Exception as e: print('  acis', repr(e)[:100])
        time.sleep(5)
    else: return []
    out = []
    days = pd.date_range(d0, d1, freq='D')
    for s in r.json().get('data', []):
        m = s.get('meta', {}); ll = m.get('ll')
        if not ll: continue
        rows = []
        for d, v in zip(days, s.get('data', [])):
            if isinstance(v, list) and len(v) == 1 and isinstance(v[0], list): v = v[0]      # one element per day: [[value, obs hour]]
            val, hr = (v[0] if isinstance(v, list) else v), (v[1] if isinstance(v, list) and len(v) > 1 else None)
            if val in ('M', '', None, 'S'): mm = None
            elif val == 'T': mm = 0.0
            else:
                try: mm = round(float(str(val).rstrip('A')) * 25.4, 1)
                except ValueError: mm = None
            rows.append([f'{d:%Y-%m-%d}', mm, hr])
        sids = m.get('sids', []); kinds = [x.split()[-1] for x in sids]
        out.append(dict(id=(sids[0].split()[0] if sids else m.get('name')), sids=sids, name=m.get('name'), lon=ll[0], lat=ll[1], kind='acis_daily',
                        cocorahs=any(k == '10' for k in kinds) or any(x.startswith('US1') for x in sids), daily=rows))
    return out


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--storm', required=True); ap.add_argument('--out', default=f'{ROOT}/docs/proto/rain/data')
    ap.add_argument('--skip-mrms', action='store_true'); a = ap.parse_args()
    ev = {e['id']: e for e in json.load(open(f'{ROOT}/docs/proto/obs/catalog.json'))['events']}[a.storm]
    bb = ev['bbox_lonlat']; t0 = pd.Timestamp(ev['t0']).tz_localize(None); H = ev['hours']; t1 = t0 + pd.Timedelta(hours=H)
    D = f'{a.out}/{a.storm}'; os.makedirs(D, exist_ok=True)
    days = list(pd.date_range(t0.normalize() - pd.Timedelta(days=1), t1.normalize() + pd.Timedelta(days=1), freq='D'))
    if not a.skip_mrms: print('products ...'); json.dump(products(days), open(f'{D}/products.json', 'w'), indent=1)
    # gauges
    G = dict(storm=a.storm, box_lonlat=bb, buffer_deg=BUF, t0=f'{t0:%Y-%m-%dT%H:%MZ}', hours=H, asos=[], usgs=[], acis=[])
    w0, w1 = t0 - pd.Timedelta(hours=6), t1 + pd.Timedelta(hours=6)
    for s in asos_stations(bb):
        df = asos_1min(s['id'], w0, w1); src = '1min'
        if df is None or df['p'].notna().sum() < 60:
            df = asos_hourly(s['id'], w0, w1); src = 'metar_p01i'
        if df is None or df.empty: s['series'] = None; G['asos'].append(s); continue
        if src == '1min':
            df = df.set_index('t')['p'] * 25.4
            n = df.notna().resample('5min', label='right', closed='right').sum()
            p5 = df.resample('5min', label='right', closed='right').sum(min_count=1)
            s['five_min'] = [[f'{t:%Y-%m-%dT%H:%M}', None if not np.isfinite(v) else round(float(v), 2), int(c)] for t, v, c in zip(p5.index, p5.values, n.values)]
        else:
            s['metar_hourly'] = [[f'{t:%Y-%m-%dT%H:%M}', None if not np.isfinite(v) else round(float(v) * 25.4, 2)] for t, v in zip(df['t'], df['p'])]
        s['source'] = src; G['asos'].append(s); print('asos', s['id'], src)
    G['usgs'] = usgs_rain(bb, w0, w1); print('usgs', len(G['usgs']))
    G['acis'] = acis_daily(bb, days[0], days[-1]); print('acis', len(G['acis']))
    json.dump(G, open(f'{D}/gauges.json', 'w'))
    if a.skip_mrms: return
    # MRMS crops
    bx = (bb[1] - 0.06, bb[3] + 0.06, bb[0] - 0.06, bb[2] + 0.06)
    hours = [t0 + pd.Timedelta(hours=h + 1) for h in range(H)]
    la, lo, P2 = SH.fetch_series('pass2', hours[0], hours[-1], bx)
    lr, lor, PR = SH.fetch_series('preciprate', t0 - pd.Timedelta(minutes=4), t1 + pd.Timedelta(minutes=4), bx)
    lq, loq, Q15 = SH.fetch_series('qpe15m', t0, t1 + pd.Timedelta(minutes=2), bx)
    Q15 = {t: c for t, c in Q15.items() if t.minute % 15 == 0 and t.second == 0}
    def pack(dct):
        ts = sorted(dct); return np.array([f'{t:%Y-%m-%dT%H:%M:%S}' for t in ts]), (np.stack([dct[t] for t in ts]).astype(np.float16) if ts else np.zeros((0, 1, 1), np.float16))
    t_p2, a_p2 = pack(P2); t_pr, a_pr = pack(PR); t_q, a_q = pack(Q15)
    np.savez_compressed(f'{D}/mrms_box.npz', lat=la if la is not None else lr, lon=lo if lo is not None else lor, pass2_t=t_p2, pass2=a_p2,
                        preciprate_t=t_pr, preciprate=a_pr, qpe15m_t=t_q, qpe15m=a_q,
                        note='native MRMS 0.01 deg crops, rows north->south; pass2/qpe15m mm per file interval ending at the stamp; preciprate mm/h at the stamp; NaN = no coverage')
    rg = (bb[1] - BUF - 0.02, bb[3] + BUF + 0.02, bb[0] - BUF - 0.02, bb[2] + BUF + 0.02)
    rh0 = days[1] - pd.Timedelta(hours=12); rh1 = days[-1] + pd.Timedelta(hours=12)
    lr2, lo2, P2R = SH.fetch_series('pass2', rh0, rh1, rg)
    t_r, a_r = pack(P2R)
    np.savez_compressed(f'{D}/mrms_region.npz', lat=lr2, lon=lo2, pass2_t=t_r, pass2=a_r, note='Pass2 hourly (mm, hour ending at the stamp), gauge region')
    print('done', {k: os.path.getsize(f'{D}/{k}') for k in os.listdir(D)})


if __name__ == '__main__':
    main()
