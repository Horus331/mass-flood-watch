"""Mass Flood Watch live refresh: tide gauges + NOAA STOFS surge forecast, NWS rain forecast per town, buoys, alerts.
Run by GitHub Actions every 6 hours; writes docs/live.json."""
import os, re, json, gzip, base64, time, requests, numpy as np, pandas as pd
from concurrent.futures import ThreadPoolExecutor
t0 = time.time()
USE_STOFS = False  # False = forecast peak is the higher of NOAA STOFS and tide+current surge (best in Overnight 6: 13/18 storms caught vs 10 STOFS-only, 5 shortcut-only); True = STOFS only
H = {'User-Agent': 'WPI-flood-research'}
# built-in constants (no Google Drive needed): gauge storm statistics at 2030 sea level, town centre points
GAUGES = {"8443970": {"mu": 2.3656, "beta": 0.1342, "rate": 0.00462}, "8447386": {"mu": 1.5185, "beta": 0.1397, "rate": 0.0065}, "8447435": {"mu": 1.8439, "beta": 0.1499, "rate": 0.01015}, "8447930": {"mu": 0.9879, "beta": 0.1147, "rate": 0.00522}}
import tempfile
TMP = tempfile.mkdtemp()
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOWNS = json.load(open(os.path.join(ROOT, 'refresh', 'town_points.json')))   # town label points (MassGIS towns, Districts 3-6)
live = {'asof': __import__('datetime').datetime.now(__import__('zoneinfo').ZoneInfo('America/New_York')).strftime('%Y-%m-%d %H:%M ET'), 'gauges': {}, 'towns_qpf24': {}, 'alerts': [], 'tsunami': []}
API = 'https://api.tidesandcurrents.noaa.gov/api/prod/datagetter'
# NOAA STOFS-2D-Global surge+tide forecast at the 4 gauges (newest 6-hourly cycle on NOMADS), levelled to each gauge on the last 6 h
STOFS = {}
try:
    import xarray as xr
    _b = 'https://nomads.ncep.noaa.gov/pub/data/nccf/com/stofs/prod/'
    _dirs = sorted(set(re.findall(r'(stofs_2d_glo\.\d{8})/', requests.get(_b, headers=H, timeout=60).text)))[-2:]
    for _d in reversed(_dirs):
        _fs = sorted(set(re.findall(r'(stofs_2d_glo\.t\d\dz\.points\.cwl\.nc)', requests.get(_b + _d + '/', headers=H, timeout=60).text)))
        if not _fs: continue
        open(os.path.join(TMP, 'stofs_live.nc'), 'wb').write(requests.get(_b + _d + '/' + _fs[-1], headers=H, timeout=300).content)
        _ds = xr.open_dataset(os.path.join(TMP, 'stofs_live.nc')).load(); _nm = [x.decode() if isinstance(x, bytes) else str(x) for x in _ds.station_name.values]
        for sid in GAUGES:
            _k = [i for i, n in enumerate(_nm) if f' {sid} ' in n]
            if _k: _z = _ds.zeta.isel(station=_k[0]).to_series(); _z[_z < -900] = np.nan; STOFS[sid] = _z.resample('1h').mean()
        live['stofs_cycle'] = _d.split('.')[-1] + ' ' + _fs[-1].split('.')[1]; break
except Exception as ex: print('stofs', repr(ex)[:80])
for sid, g in GAUGES.items():
    try:
        o = requests.get(API, params=dict(station=sid, product='water_level', date='recent', datum='NAVD', units='metric', time_zone='gmt', format='json', application='WPI_research'), headers=H, timeout=60).json().get('data', [])
        p = requests.get(API, params=dict(station=sid, product='predictions', begin_date=(pd.Timestamp.utcnow() - pd.Timedelta(hours=26)).strftime('%Y%m%d %H:%M'), range=74, datum='NAVD', units='metric',
                                          time_zone='gmt', interval='6', format='json', application='WPI_research'), headers=H, timeout=60).json().get('predictions', [])
        if not o or not p: continue
        ob = pd.Series([float(x['v']) for x in o if x['v']], index=pd.to_datetime([x['t'] for x in o if x['v']]))
        pr = pd.Series([float(x['v']) for x in p], index=pd.to_datetime([x['t'] for x in p]))
        surge_now = float((ob - pr.reindex(ob.index, method='nearest')).tail(10).mean())
        fut = pr[pr.index > ob.index.max()].head(48 * 10)
        fc_max = float(fut.max() + max(surge_now, 0)); obs_max24 = float(ob.tail(240).max()); st_max = None
        if sid in STOFS:                                                # NOAA surge model, levelled to the gauge over the last 6 h
            z = STOFS[sid]; oh_ = ob.resample('1h').mean(); last = oh_.index.max()
            past = z[(z.index > last - pd.Timedelta(hours=6)) & (z.index <= last)]; off = float((oh_.reindex(past.index) - past).mean())
            zf = z[(z.index > last) & (z.index <= last + pd.Timedelta(hours=48))]
            if np.isfinite(off) and len(zf): st_max = float(zf.max() + off); STOFS[sid] = z + off
        if st_max is not None: fc_max = st_max if USE_STOFS else max(fc_max, st_max)
        x = max(fc_max, obs_max24) + g['rate'] * (2030 - pd.Timestamp.now().year)
        live['gauges'][sid] = dict(now=round(float(ob.iloc[-1]), 3), surge_now=round(surge_now, 3), next48_max=round(fc_max, 3), last24_max=round(obs_max24, 3), stofs_next48=None if st_max is None else round(st_max, 3),
                                   aep=round(float(1 - np.exp(-np.exp(-(x - g['mu']) / g['beta']))), 4))
        ph = pr.resample('1h').mean(); oh = ob.resample('1h').mean().reindex(ph.index)   # hourly tide curve: 26 h back, 48 h ahead
        live['gauges'][sid]['curve'] = dict(t0=ph.index[0].strftime('%Y-%m-%dT%H:00Z'), pred=[round(float(v), 2) for v in ph.values],
                                            obs=[None if pd.isna(v) else round(float(v), 2) for v in oh.values])
        if sid in STOFS: live['gauges'][sid]['curve']['stofs'] = [None if pd.isna(v) else round(float(v), 2) for v in STOFS[sid].reindex(ph.index).values]
    except Exception as ex: print('gauge', sid, repr(ex)[:80])
def qpf(item):
    town, lat, lon = item
    try:
        pt = requests.get(f'https://api.weather.gov/points/{lat:.4f},{lon:.4f}', headers=H, timeout=30).json()['properties']
        gp = requests.get(pt['forecastGridData'], headers=H, timeout=30).json()['properties']['quantitativePrecipitation']['values']
        now = pd.Timestamp.utcnow(); tot = 0.0
        for v in gp:
            st_ = pd.Timestamp(v['validTime'].split('/')[0]); hrs = pd.Timedelta(v['validTime'].split('/')[1]).total_seconds() / 3600
            if now - pd.Timedelta(hours=hrs) <= st_ <= now + pd.Timedelta(hours=24) and v['value'] is not None: tot += float(v['value'])
        return town, round(tot, 1)
    except Exception: return town, None
with ThreadPoolExecutor(8) as ex: live['towns_qpf24'] = dict(ex.map(qpf, [(t, ll[0], ll[1]) for t, ll in TOWNS.items()]))
live['waves'] = {}
for bid, bname in (('44013', 'Boston Harbor approach'), ('44029', 'Massachusetts Bay'), ('44020', 'Nantucket Sound'), ('44097', 'Block Island Sound')):
    try:
        rows = [r.split() for r in requests.get(f'https://www.ndbc.noaa.gov/data/realtime2/{bid}.txt', headers=H, timeout=60).text.splitlines() if r and not r.startswith('#')]
        for r in rows[:12]:                                             # newest first; take the first line with a wave height
            if r[8] != 'MM':
                live['waves'][bid] = dict(name=bname, hs_m=float(r[8]), period_s=None if r[9] == 'MM' else float(r[9]), time=f'{r[0]}-{r[1]}-{r[2]}T{r[3]}:{r[4]}Z'); break
    except Exception as ex: print('buoy', bid, repr(ex)[:60])
try:
    al = requests.get('https://api.weather.gov/alerts/active?area=MA', headers=H, timeout=60).json()
    live['alerts'] = [dict(event=f['properties']['event'], area=f['properties']['areaDesc'][:160], ends=f['properties'].get('ends') or f['properties'].get('expires')) for f in al['features']][:15]
    x = requests.get('https://www.tsunami.gov/events/xml/PAAQAtom.xml', headers=H, timeout=60).text
    live['tsunami'] = [dict(title=t, updated=u) for t, u in zip(re.findall(r'<entry>.*?<title>(.*?)</title>', x, re.S)[:3], re.findall(r'<entry>.*?<updated>(.*?)</updated>', x, re.S)[:3])]
except Exception as ex: print('alerts', repr(ex)[:80])
json.dump(live, open(os.path.join(ROOT, 'docs', 'live.json'), 'w'), separators=(',', ':'))
print(f'live refresh {live["asof"]} | gauges {len(live["gauges"])} | STOFS {live.get("stofs_cycle")} | towns with rain forecast {sum(v is not None for v in live["towns_qpf24"].values())} | alerts {[a["event"] for a in live["alerts"]]} | {time.time() - t0:.0f}s')
