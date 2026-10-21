"""Observed data for checking a prototype storm: USGS gauges (15-min stage + discharge), NWS Local Storm Reports, NOAA Storm Events.

    python proto/obs_fetch.py --storm sep2023 --bbox -72.15,42.40,-71.55,42.75 --start 2023-09-10 --end 2023-09-14 --out docs/proto/obs

Writes gauges_<storm>.json (site, name, lon, lat, datum, drainage area, series of t/stage_ft/q_cfs, peaks), lsr_<storm>.csv,
stormevents_<storm>.csv.  Runs where these hosts are reachable (GitHub Actions); the agent sandbox cannot reach them.
"""
import os, sys, json, csv, io, gzip, argparse, time
import requests

def get(url, params=None, tries=4, **kw):
    for k in range(tries):
        try:
            r = requests.get(url, params=params, timeout=120, **kw)
            if r.status_code == 200: return r
            print('  http', r.status_code, url[:100])
        except Exception as e: print('  err', repr(e)[:100])
        time.sleep(3 * (k + 1))
    return None

def gauges(bbox, start, end):
    w, s, e, n = bbox
    r = get('https://waterservices.usgs.gov/nwis/iv/', dict(format='json', bBox=f'{w:.4f},{s:.4f},{e:.4f},{n:.4f}', startDT=start, endDT=end,
                                                         parameterCd='00060,00065', siteStatus='all'))
    out = {}
    if r is None: return out
    for ts in r.json()['value']['timeSeries']:
        si = ts['sourceInfo']; code = si['siteCode'][0]['value']; var = ts['variable']['variableCode'][0]['value']
        g = out.setdefault(code, dict(site=code, name=si['siteName'], lon=si['geoLocation']['geogLocation']['longitude'], lat=si['geoLocation']['geogLocation']['latitude']))
        vals = [(v['dateTime'], float(v['value'])) for v in ts['values'][0]['value'] if v['value'] not in ('', None) and float(v['value']) > -999]
        key = 'q_cfs' if var == '00060' else 'stage_ft'
        g[key] = vals
        if vals: g['peak_' + key] = max(vals, key=lambda x: x[1])
    # site metadata: datum (ft), vertical datum, drainage area
    for code, g in out.items():
        m = get('https://waterservices.usgs.gov/nwis/site/', dict(format='rdb', sites=code, siteOutput='expanded'))
        if m is None: continue
        L = [l for l in m.text.splitlines() if l and not l.startswith('#')]
        if len(L) >= 3:
            H = L[0].split('\t'); V = L[2].split('\t'); d = dict(zip(H, V))
            g.update(datum_ft=float(d['alt_va']) if d.get('alt_va') else None, vdatum=d.get('alt_datum_cd'), drain_mi2=float(d['drain_area_va']) if d.get('drain_area_va') else None)
    return out

def lsr(bbox, start, end):
    r = get('https://mesonet.agron.iastate.edu/cgi-bin/request/gis/lsr.py', dict(sts=f'{start}T00:00Z', ets=f'{end}T23:59Z', fmt='csv', states='MA'))
    if r is None: return []
    w, s, e, n = bbox; rows = list(csv.DictReader(io.StringIO(r.text)))
    keep = []
    for x in rows:
        try: lo, la = float(x.get('LON') or x.get('lon')), float(x.get('LAT') or x.get('lat'))
        except Exception: continue
        if w <= lo <= e and s <= la <= n: keep.append(x)
    return keep

def stormevents(year, start, end, bbox):
    idx = get('https://www.ncei.noaa.gov/pub/data/swdi/stormevents/csvfiles/')
    if idx is None: return []
    import re
    f = sorted(set(re.findall(rf'StormEvents_details-ftp_v1\.0_d{year}_c\d+\.csv\.gz', idx.text)))
    if not f: return []
    r = get('https://www.ncei.noaa.gov/pub/data/swdi/stormevents/csvfiles/' + f[-1])
    rows = list(csv.DictReader(io.StringIO(gzip.decompress(r.content).decode('latin-1'))))
    w, s, e, n = bbox; out = []
    for x in rows:
        if x['STATE'] != 'MASSACHUSETTS' or x['EVENT_TYPE'] not in ('Flash Flood', 'Flood', 'Heavy Rain'): continue
        d = f"{x['BEGIN_YEARMONTH'][:4]}-{x['BEGIN_YEARMONTH'][4:]}-{int(x['BEGIN_DAY']):02d}"
        if not (start <= d <= end): continue
        out.append({k: x[k] for k in ('EVENT_ID', 'EVENT_TYPE', 'CZ_NAME', 'BEGIN_DATE_TIME', 'END_DATE_TIME', 'BEGIN_LAT', 'BEGIN_LON', 'END_LAT', 'END_LON',
                                       'DAMAGE_PROPERTY', 'EPISODE_NARRATIVE', 'EVENT_NARRATIVE', 'BEGIN_LOCATION', 'END_LOCATION')})
    return out

if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('--storm', default='sep2023'); ap.add_argument('--bbox', default='-72.15,42.40,-71.55,42.75')
    ap.add_argument('--start', default='2023-09-10'); ap.add_argument('--end', default='2023-09-14'); ap.add_argument('--out', default='docs/proto/obs')
    a = ap.parse_args(); bb = [float(v) for v in a.bbox.split(',')]; os.makedirs(a.out, exist_ok=True)
    G = gauges(bb, a.start, a.end); json.dump(dict(bbox=bb, start=a.start, end=a.end, gauges=list(G.values())), open(f'{a.out}/gauges_{a.storm}.json', 'w'))
    print('gauges', len(G), [(g['site'], g['name'], g.get('peak_stage_ft'), g.get('peak_q_cfs')) for g in G.values()])
    L = lsr(bb, a.start, a.end)
    if L:
        with open(f'{a.out}/lsr_{a.storm}.csv', 'w', newline='') as f: w_ = csv.DictWriter(f, fieldnames=list(L[0].keys())); w_.writeheader(); w_.writerows(L)
    print('LSR', len(L))
    E = stormevents(a.start[:4], a.start, a.end, bb)
    if E:
        with open(f'{a.out}/stormevents_{a.storm}.csv', 'w', newline='') as f: w_ = csv.DictWriter(f, fieldnames=list(E[0].keys())); w_.writeheader(); w_.writerows(E)
    print('Storm Events', len(E))
