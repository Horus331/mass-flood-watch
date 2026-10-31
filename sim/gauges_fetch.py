"""River inflow at the model's edge and observed stage/flow inside it, from the USGS Water Data OGC API (free, no key).

    python sim/gauges_fetch.py              -> out/gauges_<run>.json for every storm in STORMS, uploaded to HF data/gauges_v2/

Two uses in the flood engine:
  * boundary inflow: rivers that enter Massachusetts carry water that fell outside the grid.  Discharge at the last gauge
    upstream of the state line is injected as a point source at the cell where the river crosses the edge.
  * validation: peak flow/stage at gauges inside the state.  Each site also carries its gauge datum (altitude, ft, and the
    vertical datum) so peak stage can be turned into a water-surface elevation and compared with the model's z + peak depth.
Discharge in cubic feet per second (USGS parameter 00060) and gage height in feet (00065), thinned to hourly.

Moved off waterservices.usgs.gov (legacy NWIS, being retired Nov 2026 - early 2027; it already answers 403 to some clients)
to api.waterdata.usgs.gov/ogcapi (v1; collections 'continuous', 'time-series-metadata', 'monitoring-locations') via proto/usgs_api.py.  Same layout as before except
times are UTC hours ('2023-07-10T15', hourly max) where the legacy files held local times, plus 'sites' {id: {name, lat, lon,
datum_ft, vdatum, drain_mi2}}.  Written to data/gauges_v2/ so the engine's inflow input (data/gauges/, local times) is untouched.
"""
import os, sys, json, time
STORMS = {'dec2023': ('2023-12-17', '2023-12-21'), 'sep2023': ('2023-09-10', '2023-09-14'), 'jul2023': ('2023-07-09', '2023-07-13'), 'jan2018': ('2018-01-03', '2018-01-07'), 'jan2024': ('2024-01-08', '2024-01-12')}
BOUNDARY = {'01154500': 'Connecticut River at North Walpole, NH', '01156000': 'West River at Newfane, VT (joins the Connecticut above the state line)', '01161000': 'Ashuelot River at Hinsdale, NH (joins the Connecticut above the state line)',
            '01092000': 'Merrimack River near Goffs Falls, NH', '01094000': 'Souhegan River at Merrimack, NH (joins the Merrimack above the state line)', '01096500': 'Nashua River at East Pepperell, MA',
            '01168500': 'Deerfield River at Charlemont, MA (basin mostly in Vermont)', '01170000': 'Deerfield River near West Deerfield, MA', '01333000': 'Green River at Williamstown, MA', '01197500': 'Housatonic River near Great Barrington, MA'}
log = lambda *a: print(time.strftime('%H:%M:%S'), *a, flush=True)

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'proto'))
import usgs_api as U      # one shared reader: OGC API, legacy WaterServices fallback until 22 Feb 2027 (env USGS_SOURCE=auto|ogc|legacy)

def series(G, param):
    """usgs_api.iv() result -> {site: {lat, lon, values: [(UTC hour 'YYYY-MM-DDTHH', hourly max), ...]}}."""
    out = {}
    for sid, g in G.items():
        hv = {}
        for t, v in g['series'].get(param) or []: hv[t[:13]] = max(v, hv.get(t[:13], -1e9))      # hourly max (UTC hour)
        if hv: out[sid] = dict(lat=g['lat'], lon=g['lon'], values=sorted(hv.items()))
    return out

def site_info(ids):
    return {s: {k: m[k] for k in ('name', 'datum_ft', 'vdatum', 'drain_mi2', 'lon', 'lat')} for s, m in U.ogc_sites_meta(sites=ids).items()}

os.makedirs('out', exist_ok=True)
for run, (s, e) in STORMS.items():
    res = dict(run=run, start=s, end=e, boundary=BOUNDARY, flow={}, stage={}, source='api.waterdata.usgs.gov OGC continuous, hourly max (UTC)')
    tw = f'{s}T00:00:00Z/{e}T23:59:59Z'
    for param, key in (('00060', 'flow'), ('00065', 'stage')):
        G, used = U.iv(state='25', start=f'{s}T00:00:00Z', end=f'{e}T23:59:59Z', params=(param,), meta=False)
        res[key].update(series(G, param))
        if used == 'legacy': res['source'] += ' (+ legacy WaterServices fallback)'
        if used == 'none': log(run, key, 'state query failed on both services')
        miss = [sid for sid in BOUNDARY if sid not in res[key]]
        if miss:
            G, used = U.iv(sites=miss, start=f'{s}T00:00:00Z', end=f'{e}T23:59:59Z', params=(param,), meta=False)
            res[key].update(series(G, param))
    ids = sorted(set(res['flow']) | set(res['stage']))
    res['sites'] = site_info(ids)
    if ids and not res['sites']: log(run, 'site info failed')
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
