"""Observed data for checking a prototype storm: USGS gauges (15-min stage + discharge), NWS Local Storm Reports, NOAA Storm Events.

    python proto/obs_fetch.py --storm sep2023 --bbox -72.15,42.40,-71.55,42.75 --start 2023-09-10 --end 2023-09-14 --out docs/proto/obs

Writes gauges_<storm>.json (site, name, lon, lat, datum, drainage area, series of t/stage_ft/q_cfs, peaks), lsr_<storm>.csv,
stormevents_<storm>.csv.  Gauges come from the USGS Water Data OGC API (legacy WaterServices as fallback until it is switched off;
--gauge-source ogc|legacy|auto, --states for boxes that cross a state line).  Runs where these hosts are reachable (GitHub Actions); the agent sandbox cannot reach them.
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

# --- USGS gauges -------------------------------------------------------------------------------------------------------
# Primary: USGS Water Data OGC API (api.waterdata.usgs.gov/ogcapi/v0, collections 'continuous' + 'monitoring-locations').
# Fallback: legacy WaterServices (waterservices.usgs.gov/nwis/iv + /site), retired Nov 2026 - Q1 2027; used only if the new API
# returns nothing.  Both paths write the same records: times in the gauge's local time with offset (e.g. 2023-09-11T21:15:00.000-04:00),
# 15-min [time, value] lists, peak_* = first maximum, datum_ft / vdatum / drain_mi2 from the site record.
OGC = 'https://api.waterdata.usgs.gov/ogcapi/v0/collections'
HDR = {'User-Agent': 'mass-flood-watch research (github.com/Horus331/mass-flood-watch)'}
if os.environ.get('API_USGS_PAT'): HDR['X-Api-Key'] = os.environ['API_USGS_PAT']        # optional key (higher rate limits); never required
TZ = 'America/New_York'                                                                     # every MA / southern NH-VT gauge

def _local(t_utc):
    """'2023-09-12T04:30:00+00:00' -> '2023-09-12T00:30:00.000-04:00' (the legacy IV string layout)."""
    import datetime as dt; from zoneinfo import ZoneInfo
    d = dt.datetime.fromisoformat(t_utc.replace('Z', '+00:00')).astimezone(ZoneInfo(TZ)); z = d.strftime('%z')
    return d.strftime('%Y-%m-%dT%H:%M:%S') + '.000' + z[:3] + ':' + z[3:]

def _window_utc(start, end):
    import datetime as dt; from zoneinfo import ZoneInfo
    a = dt.datetime.fromisoformat(start).replace(tzinfo=ZoneInfo(TZ)); b = dt.datetime.fromisoformat(end).replace(tzinfo=ZoneInfo(TZ)) + dt.timedelta(days=1, seconds=-1)
    f = lambda d: d.astimezone(dt.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    return f'{f(a)}/{f(b)}'

def ogc_items(coll, params):
    """All features of an OGC API items query (follows rel=next; 429/5xx back off).  None if unreachable."""
    feats, nxt, p = [], f'{OGC}/{coll}/items', dict(params, f='json', limit=10000)
    while nxt:
        for k in range(5):
            try:
                r = requests.get(nxt, params=p, headers=HDR, timeout=300)
                if r.status_code in (429, 500, 502, 503, 504): raise RuntimeError(f'HTTP {r.status_code}')
                r.raise_for_status(); j = r.json(); break
            except Exception as e: print('  ogc retry', k, coll, repr(e)[:120]); time.sleep(10 * (k + 1))
        else: return None
        feats += j.get('features', []); nxt = next((l['href'] for l in j.get('links', []) if l.get('rel') == 'next'), None); p = None
    return feats

def gauges_ogc(bbox, start, end, states=('25',)):
    """Gauges inside bbox with 00060/00065 instantaneous values, from the OGC 'continuous' collection (queried per state, the
    pattern proven in sim/gauges_fetch.py) and site metadata from 'monitoring-locations' (altitude, vertical_datum, drainage_area)."""
    w, s, e, n = bbox; tw = _window_utc(start, end); ser = {}
    for st in states:
        for pc in ('00060', '00065'):
            F = ogc_items('continuous', dict(state_code=st, parameter_code=pc, time=tw))
            if F is None: print('  ogc continuous failed', st, pc); continue
            for f in F:
                q = f['properties']
                try: v = float(q['value'])
                except (TypeError, ValueError): continue
                if v <= -999: continue
                sid = q['monitoring_location_id'].split('-', 1)[-1]
                ser.setdefault((sid, pc), {}).setdefault(q.get('time_series_id') or '', []).append((q['time'], v))
    if not ser: return {}
    ids = sorted({sid for sid, _ in ser}); info = {}
    for i in range(0, len(ids), 40):
        F = ogc_items('monitoring-locations', dict(id=','.join('USGS-' + x for x in ids[i:i + 40])))
        for f in F or []:
            q = f['properties']; sid = f['id'].split('-', 1)[-1]; g = f.get('geometry') or {}
            c_ = g.get('coordinates') or [None, None]; r8 = lambda v: round(float(v), 8) if v is not None else None     # legacy precision (~1 mm)
            info[sid] = dict(name=q.get('monitoring_location_name'), lon=r8(c_[0]), lat=r8(c_[1]),
                             datum_ft=q.get('altitude'), vdatum=q.get('vertical_datum'), drain_mi2=q.get('drainage_area'))
    out = {}
    for (sid, pc), by_ts in sorted(ser.items()):
        m = info.get(sid)
        if not m or m['lon'] is None or not (w <= m['lon'] <= e and s <= m['lat'] <= n): continue
        rows = max(by_ts.values(), key=len)                                  # several series per parameter: keep the fullest (the primary)
        vals = [(_local(t), v) for t, v in sorted(rows)]
        g = out.setdefault(sid, dict(site=sid, name=m['name'], lon=m['lon'], lat=m['lat']))
        key = 'q_cfs' if pc == '00060' else 'stage_ft'; g[key] = vals
        if vals: g['peak_' + key] = max(vals, key=lambda x: x[1])
    for sid, g in out.items():
        m = info[sid]
        g.update(datum_ft=float(m['datum_ft']) if m['datum_ft'] is not None else None, vdatum=m['vdatum'],
                 drain_mi2=float(m['drain_mi2']) if m['drain_mi2'] is not None else None)
    return out

def gauges_legacy(bbox, start, end):
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

def gauges(bbox, start, end, source='auto', states=('25',)):
    """source: 'ogc' (new API only), 'legacy' (WaterServices only), 'auto' (OGC, then legacy if OGC gave nothing).  Returns ({site: rec}, used)."""
    if source in ('ogc', 'auto'):
        G = gauges_ogc(bbox, start, end, states)
        if G or source == 'ogc': return G, 'ogc'
        print('  OGC API returned no gauges; falling back to legacy WaterServices')
    return gauges_legacy(bbox, start, end), 'legacy'

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
    ap.add_argument('--gauge-source', default='auto', choices=['auto', 'ogc', 'legacy']); ap.add_argument('--states', default='25', help='USGS state codes to query (25 MA, 33 NH, 50 VT, 09 CT, 44 RI, 36 NY)')
    ap.add_argument('--gauges-only', action='store_true')
    a = ap.parse_args(); bb = [float(v) for v in a.bbox.split(',')]; os.makedirs(a.out, exist_ok=True)
    G, used = gauges(bb, a.start, a.end, a.gauge_source, tuple(a.states.split(',')))
    json.dump(dict(bbox=bb, start=a.start, end=a.end, gauges=list(G.values())), open(f'{a.out}/gauges_{a.storm}.json', 'w'))
    print('gauges', len(G), 'via', used, [(g['site'], g['name'], g.get('peak_stage_ft'), g.get('peak_q_cfs')) for g in G.values()])
    if a.gauges_only: sys.exit(0)
    L = lsr(bb, a.start, a.end)
    if L:
        with open(f'{a.out}/lsr_{a.storm}.csv', 'w', newline='') as f: w_ = csv.DictWriter(f, fieldnames=list(L[0].keys())); w_.writeheader(); w_.writerows(L)
    print('LSR', len(L))
    E = stormevents(a.start[:4], a.start, a.end, bb)
    if E:
        with open(f'{a.out}/stormevents_{a.storm}.csv', 'w', newline='') as f: w_ = csv.DictWriter(f, fieldnames=list(E[0].keys())); w_.writeheader(); w_.writerows(E)
    print('Storm Events', len(E))
