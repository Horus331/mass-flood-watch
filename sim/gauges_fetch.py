"""River inflow at the model's edge and observed stage/flow inside it, from USGS instantaneous values (free, no key).

    python sim/gauges_fetch.py              -> out/gauges_<run>.json for every storm in STORMS, uploaded to HF data/gauges/

Two uses in the flood engine (Stage 3):
  * boundary inflow: rivers that enter Massachusetts carry water that fell outside the grid.  Discharge at the last gauge
    upstream of the state line is injected as a point source at the cell where the river crosses the edge.
  * validation: peak flow/stage at gauges inside the state, to compare with modelled peak depth (Stage 4).
Discharge in cubic feet per second (USGS parameter 00060) and gage height in feet (00065), 15-minute values.
"""
import os, json, time, requests
IV = 'https://waterservices.usgs.gov/nwis/iv/'
STORMS = {'dec2023': ('2023-12-17', '2023-12-21'), 'sep2023': ('2023-09-10', '2023-09-14'), 'jul2023': ('2023-07-09', '2023-07-13'), 'jan2018': ('2018-01-03', '2018-01-07')}
# rivers entering the state (gauge just upstream of the line) -> entry point in EPSG:26986 handled by the engine via lon/lat
BOUNDARY = {'01154500': 'Connecticut River at North Walpole, NH', '01156000': 'West River at Newfane, VT (joins the Connecticut above the state line)', '01161000': 'Ashuelot River at Hinsdale, NH (joins the Connecticut above the state line)',
            '01092000': 'Merrimack River near Goffs Falls, NH', '01094000': 'Souhegan River at Merrimack, NH (joins the Merrimack above the state line)', '01096500': 'Nashua River at East Pepperell, MA',
            '01168500': 'Deerfield River at Charlemont, MA (basin mostly in Vermont)', '01170000': 'Deerfield River near West Deerfield, MA', '01333000': 'Green River at Williamstown, MA', '01197500': 'Housatonic River near Great Barrington, MA'}
log = lambda *a: print(time.strftime('%H:%M:%S'), *a, flush=True)
def fetch(sites, start, end, param):
    r = requests.get(IV, params=dict(format='json', sites=','.join(sites), startDT=start, endDT=end, parameterCd=param, siteStatus='all'), timeout=300)
    r.raise_for_status(); out = {}
    for ts in r.json()['value']['timeSeries']:
        sid = ts['sourceInfo']['siteCode'][0]['value']; loc = ts['sourceInfo']['geoLocation']['geogLocation']
        vals = [(v['dateTime'], float(v['value'])) for v in ts['values'][0]['value'] if v['value'] not in ('', None) and float(v['value']) > -999]
        out[sid] = dict(name=ts['sourceInfo']['siteName'], lat=loc['latitude'], lon=loc['longitude'], values=vals)
    return out
os.makedirs('out', exist_ok=True)
for run, (s, e) in STORMS.items():
    res = dict(run=run, start=s, end=e, boundary=BOUNDARY, flow={}, stage={})
    # every active gauge in MA plus the boundary gauges, one state query (stateCd=ma) and one by site list
    for param, key in (('00060', 'flow'), ('00065', 'stage')):
        try:
            r = requests.get(IV, params=dict(format='json', stateCd='ma', startDT=s, endDT=e, parameterCd=param, siteStatus='all'), timeout=600); r.raise_for_status()
            for ts in r.json()['value']['timeSeries']:
                sid = ts['sourceInfo']['siteCode'][0]['value']; loc = ts['sourceInfo']['geoLocation']['geogLocation']
                vals = [(v['dateTime'][:16], float(v['value'])) for v in ts['values'][0]['value'] if v['value'] not in ('', None) and float(v['value']) > -999]
                if vals: res[key][sid] = dict(name=ts['sourceInfo']['siteName'], lat=loc['latitude'], lon=loc['longitude'], values=vals[::4])   # hourly is enough
        except Exception as ex: log(run, key, 'state query failed', repr(ex)[:120])
        try:
            for sid, d in fetch(list(BOUNDARY), s, e, param).items():
                d['values'] = [(t[:16], v) for t, v in d['values'][::4]]; res[key].setdefault(sid, d)
        except Exception as ex: log(run, key, 'boundary query failed', repr(ex)[:120])
    log(run, 'flow gauges', len(res['flow']), 'stage gauges', len(res['stage']), 'boundary present', [k for k in BOUNDARY if k in res['flow']])
    json.dump(res, open(f'out/gauges_{run}.json', 'w'), separators=(',', ':'))
if os.environ.get('HF_TOKEN'):
    from huggingface_hub import HfApi
    api = HfApi(token=os.environ['HF_TOKEN'])
    for run in STORMS:
        api.upload_file(path_or_fileobj=f'out/gauges_{run}.json', path_in_repo=f'data/gauges/gauges_{run}.json', repo_id='mohabeldokla/mass-flood-watch-tiles', repo_type='dataset')
    log('uploaded to Hugging Face data/gauges/')
