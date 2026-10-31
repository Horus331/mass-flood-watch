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
# Primary: USGS Water Data OGC API (api.waterdata.usgs.gov/ogcapi/v1, collections 'continuous' + 'time-series-metadata' + 'monitoring-locations').
# Fallback: legacy WaterServices (waterservices.usgs.gov/nwis/iv + /site), retired Nov 2026 - Q1 2027; used only if the new API
# returns nothing.  Both paths write the same records: times in the gauge's local time with offset (e.g. 2023-09-11T21:15:00.000-04:00),
# 15-min [time, value] lists, peak_* = first maximum, datum_ft / vdatum / drain_mi2 from the site record.
# Both are read through proto/usgs_api.py (one shared reader; env USGS_SOURCE=auto|ogc|legacy, optional key API_USGS_PAT).
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
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

def _records(G, bbox=None):
    """proto/usgs_api.iv() result -> the gauges_<storm>.json records (local times, peak_* = first maximum, legacy precision)."""
    out = {}
    for sid, g in sorted(G.items()):
        if g.get('lon') is None or (bbox and not (bbox[0] <= g['lon'] <= bbox[2] and bbox[1] <= g['lat'] <= bbox[3])): continue
        r8 = lambda v: round(float(v), 8) if v is not None else None
        rec = out.setdefault(sid, dict(site=sid, name=g['name'], lon=r8(g['lon']), lat=r8(g['lat'])))
        for pc, key in (('00060', 'q_cfs'), ('00065', 'stage_ft')):
            vals = [(_local(t), v) for t, v in g['series'].get(pc) or []]
            if not vals: continue
            rec[key] = vals; rec['peak_' + key] = max(vals, key=lambda x: x[1])
        rec.update(datum_ft=g.get('datum_ft'), vdatum=g.get('vdatum'), drain_mi2=g.get('drain_mi2'))
    return out

def gauges_ogc(bbox, start, end, states=('25',)):
    """Gauges inside bbox with 00060/00065 instantaneous values from the OGC API via proto/usgs_api.py (bbox discovery through
    'time-series-metadata'; `states` is no longer needed and kept only for the call signature)."""
    import usgs_api as U
    a, b = _window_utc(start, end).split('/')
    G, used = U.iv(bbox=bbox, start=a, end=b, source='ogc')
    return _records(G, bbox)

def gauges_legacy(bbox, start, end):
    """The pre-migration WaterServices path (bBox query + /site metadata), via proto/usgs_api.py; works until 22 Feb 2027."""
    import usgs_api as U
    a, b = _window_utc(start, end).split('/')
    G, used = U.iv(bbox=bbox, start=a, end=b, source='legacy')
    return _records(G)

def gauges(bbox, start, end, source=None, states=('25',)):
    """source: 'ogc' (new API only), 'legacy' (WaterServices only), 'auto' (OGC, then legacy if OGC gave nothing).
    The env switch USGS_SOURCE, when set, overrides the argument.  Returns ({site: rec}, used)."""
    source = os.environ.get('USGS_SOURCE') or source or 'auto'
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
    ap.add_argument('--gauge-source', default=os.environ.get('USGS_SOURCE') or 'auto', choices=['auto', 'ogc', 'legacy']); ap.add_argument('--states', default='25', help='USGS state codes to query (25 MA, 33 NH, 50 VT, 09 CT, 44 RI, 36 NY)')
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
