"""River inflow at the model's edge and observed stage/flow inside it, from the USGS Water Data OGC API (free, no key).

    python sim/gauges_fetch.py              -> out/gauges_<run>.json for every storm in STORMS, uploaded to HF data/gauges_v2/

Two uses in the flood engine:
  * boundary inflow: rivers that enter Massachusetts carry water that fell outside the grid.  Discharge at the last gauge
    upstream of the state line is injected as a point source at the cell where the river crosses the edge.
  * validation: peak flow/stage at gauges inside the state.  Each site also carries its gauge datum (altitude, ft, and the
    vertical datum) so peak stage can be turned into a water-surface elevation and compared with the model's z + peak depth.
Discharge in cubic feet per second (USGS parameter 00060) and gage height in feet (00065), thinned to hourly.

Moved off waterservices.usgs.gov (legacy NWIS, being retired Nov 2026 - early 2027; it already answers 403 to some clients)
to api.waterdata.usgs.gov/ogcapi/v0 (collections 'continuous' and 'monitoring-locations').  Same layout as before except
times are UTC hours ('2023-07-10T15', hourly max) where the legacy files held local times, plus 'sites' {id: {name, lat, lon,
datum_ft, vdatum, drain_mi2}}.  Written to data/gauges_v2/ so the engine's inflow input (data/gauges/, local times) is untouched.
"""
import os, json, time, requests
API = 'https://api.waterdata.usgs.gov/ogcapi/v0/collections'
H = {'User-Agent': 'mass-flood-watch research (github.com/Horus331/mass-flood-watch)'}
if os.environ.get('API_USGS_PAT'): H['X-Api-Key'] = os.environ['API_USGS_PAT']          # optional key: higher rate limits
STORMS = {'dec2023': ('2023-12-17', '2023-12-21'), 'sep2023': ('2023-09-10', '2023-09-14'), 'jul2023': ('2023-07-09', '2023-07-13'), 'jan2018': ('2018-01-03', '2018-01-07'), 'jan2024': ('2024-01-08', '2024-01-12')}
BOUNDARY = {'01154500': 'Connecticut River at North Walpole, NH', '01156000': 'West River at Newfane, VT (joins the Connecticut above the state line)', '01161000': 'Ashuelot River at Hinsdale, NH (joins the Connecticut above the state line)',
            '01092000': 'Merrimack River near Goffs Falls, NH', '01094000': 'Souhegan River at Merrimack, NH (joins the Merrimack above the state line)', '01096500': 'Nashua River at East Pepperell, MA',
            '01168500': 'Deerfield River at Charlemont, MA (basin mostly in Vermont)', '01170000': 'Deerfield River near West Deerfield, MA', '01333000': 'Green River at Williamstown, MA', '01197500': 'Housatonic River near Great Barrington, MA'}
log = lambda *a: print(time.strftime('%H:%M:%S'), *a, flush=True)

def get_all(url, params):
    """All features of an OGC items query, following rel=next links, with retries (429/5xx back off)."""
    feats, nxt, p = [], url, dict(params, f='json', limit=10000)
    while nxt:
        for k in range(6):
            try:
                r = requests.get(nxt, params=p, headers=H, timeout=300)
                if r.status_code in (429, 500, 502, 503, 504): raise RuntimeError(f'HTTP {r.status_code}')
                r.raise_for_status(); j = r.json(); break
            except Exception as e: log('  retry', k, repr(e)[:100]); time.sleep(15 * (k + 1))
        else: raise SystemExit(f'USGS API unreachable: {url}')
        feats += j.get('features', []); nxt = next((l['href'] for l in j.get('links', []) if l.get('rel') == 'next'), None); p = None
    return feats

def series(feats):
    out = {}
    for f in feats:
        q = f['properties']; sid = q['monitoring_location_id'].split('-', 1)[-1]
        try: v = float(q['value'])
        except (TypeError, ValueError): continue
        if v <= -999: continue
        d = out.setdefault(sid, dict(lon=f['geometry']['coordinates'][0] if f.get('geometry') else None, lat=f['geometry']['coordinates'][1] if f.get('geometry') else None, v={}))
        d['v'][q['time'][:13]] = max(v, d['v'].get(q['time'][:13], -1e9))      # hourly max (UTC hour)
    return {s: dict(lat=d['lat'], lon=d['lon'], values=sorted(d['v'].items())) for s, d in out.items()}

def legacy_series(param, s, e, **where):
    """Fallback while legacy WaterServices still answers (switched off Nov 2026 - Q1 2027): same {site: {lat, lon, values}} as series()."""
    import datetime as dt
    try:
        r = requests.get('https://waterservices.usgs.gov/nwis/iv/', params=dict(format='json', startDT=f'{s}T00:00Z', endDT=f'{e}T23:59Z', parameterCd=param,
                         siteStatus='all', **where), headers=H, timeout=300); r.raise_for_status()
    except Exception as ex: log('  legacy fallback failed', repr(ex)[:100]); return {}
    out = {}
    for ts in r.json()['value']['timeSeries']:
        si = ts['sourceInfo']; sid = si['siteCode'][0]['value']; gl = si['geoLocation']['geogLocation']; hv = {}
        for v in ts['values'][0]['value']:
            try: x = float(v['value'])
            except (TypeError, ValueError): continue
            if x <= -999: continue
            hr = dt.datetime.fromisoformat(v['dateTime']).astimezone(dt.timezone.utc).strftime('%Y-%m-%dT%H'); hv[hr] = max(x, hv.get(hr, -1e9))
        if hv and sid not in out: out[sid] = dict(lat=gl['latitude'], lon=gl['longitude'], values=sorted(hv.items()))
    return out

def site_info(ids):
    info = {}
    for i in range(0, len(ids), 40):
        for f in get_all(f'{API}/monitoring-locations/items', dict(id=','.join('USGS-' + s for s in ids[i:i + 40]))):
            q = f['properties']; sid = f['id'].split('-', 1)[-1]
            info[sid] = dict(name=q.get('monitoring_location_name'), datum_ft=q.get('altitude'), vdatum=q.get('vertical_datum'), drain_mi2=q.get('drainage_area'),
                             lon=f['geometry']['coordinates'][0] if f.get('geometry') else None, lat=f['geometry']['coordinates'][1] if f.get('geometry') else None)
    return info

os.makedirs('out', exist_ok=True)
for run, (s, e) in STORMS.items():
    res = dict(run=run, start=s, end=e, boundary=BOUNDARY, flow={}, stage={}, source='api.waterdata.usgs.gov OGC continuous, hourly max (UTC)')
    tw = f'{s}T00:00:00Z/{e}T23:59:59Z'
    for param, key in (('00060', 'flow'), ('00065', 'stage')):
        try: res[key].update(series(get_all(f'{API}/continuous/items', dict(state_code='25', parameter_code=param, time=tw))))
        except SystemExit as ex:
            log(run, key, 'state query failed', ex, '- trying legacy WaterServices'); res[key].update(legacy_series(param, s, e, stateCd='ma'))
            res['source'] += ' (+ legacy WaterServices fallback)'
        for sid in BOUNDARY:
            if sid in res[key]: continue
            try: res[key].update(series(get_all(f'{API}/continuous/items', dict(monitoring_location_id='USGS-' + sid, parameter_code=param, time=tw))))
            except SystemExit as ex: log(run, key, sid, 'failed', ex, '- trying legacy'); res[key].update(legacy_series(param, s, e, sites=sid))
    ids = sorted(set(res['flow']) | set(res['stage']))
    try: res['sites'] = site_info(ids)
    except SystemExit as ex: log(run, 'site info failed', ex); res['sites'] = {}
    for key in ('flow', 'stage'):
        for sid, d in res[key].items(): d['name'] = res['sites'].get(sid, {}).get('name') or BOUNDARY.get(sid, sid)
    log(run, 'flow gauges', len(res['flow']), 'stage gauges', len(res['stage']), 'with datum', sum(1 for v in res['sites'].values() if v.get('datum_ft') is not None),
        'boundary present', [k for k in BOUNDARY if k in res['flow']])
    json.dump(res, open(f'out/gauges_{run}.json', 'w'), separators=(',', ':'))
if os.environ.get('HF_TOKEN'):
    from huggingface_hub import HfApi
    api = HfApi(token=os.environ['HF_TOKEN'])
    for run in STORMS:
        api.upload_file(path_or_fileobj=f'out/gauges_{run}.json', path_in_repo=f'data/gauges_v2/gauges_{run}.json', repo_id='mohabeldokla/mass-flood-watch-tiles', repo_type='dataset')
    log('uploaded to Hugging Face data/gauges_v2/')
