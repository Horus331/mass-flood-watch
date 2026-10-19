"""USGS / UMass / MassDEP Massachusetts Stream Crossings Project (free ArcGIS feature service): every modelled road-stream crossing
with drainage area, StreamStats peak flows (10/25/50/100/500-yr), bankfull geometry, road deck elevation and the HEC-RAS preliminary
designs. Writes docs/network/crossings_ma.json rows:
 [lon, lat, naacc_code, road, stream, town, drn_area_km2, pk10, pk25, pk50, pk100, pk500 (m3/s), bf_width_m, bf_depth_m,
  road_deck_elev_m (original, from the 100-yr box design), hwy_class, design_flood]
Peak flows and deck elevation let the engine turn modelled channel flow at a crossing into a return period and an overtopping check.
Run by crossings.yml.
"""
import json, time, os, requests
os.makedirs('docs/network', exist_ok=True)
B = 'https://services.arcgis.com/v01gqwM5QqNysAAi/ArcGIS/rest/services/Massachusetts_Stream_Crossings_Project_Web_Map_Service/FeatureServer/0/query'
F = ['CrosCode', 'ROAD', 'STREAM', 'TOWN', 'DRNAREA', 'PK10AEP', 'PK4AEP', 'PK2AEP', 'PK1AEP', 'PK02AEP', 'BFWDTH', 'BFDPTH', 'BCORDE1HYR', 'HWYCLASS', 'HWYHDF', 'LAT', 'LON']
H = {'User-Agent': 'mass-flood-watch research (github.com/Horus331/mass-flood-watch)'}
n = requests.get(B, params=dict(where='1=1', returnCountOnly='true', f='json'), headers=H, timeout=120).json(); print('count', n)
feats = []; off = 0
while True:
    r = requests.get(B, params=dict(where='1=1', outFields=','.join(F), returnGeometry='false', outSR=4326, f='json', orderByFields='OBJECTID', resultOffset=off, resultRecordCount=2000), headers=H, timeout=180).json()
    if 'error' in r: raise SystemExit(r['error'])
    fs = r.get('features', []); feats += fs; off += len(fs); print('got', off, flush=True)
    if not r.get('exceededTransferLimit') or not fs: break
    time.sleep(1)
CFS = 0.0283168; FT = 0.3048; SQMI = 2.58999
def num(v, k=1.0):
    try: return None if v is None or float(v) <= -999 else round(float(v) * k, 3)      # -999/-9999 = no data in the service
    except Exception: return None
rows = []
for f in feats:
    a = f['attributes']; lat, lon = (float(a['LAT']) if a.get('LAT') is not None else None), (float(a['LON']) if a.get('LON') is not None else None)     # full precision (3 decimals = 100 m)
    if lat is None or lon is None: continue
    rows.append([round(lon, 5), round(lat, 5), a.get('CrosCode'), a.get('ROAD'), a.get('STREAM'), a.get('TOWN'), num(a.get('DRNAREA'), SQMI),
                 num(a.get('PK10AEP'), CFS), num(a.get('PK4AEP'), CFS), num(a.get('PK2AEP'), CFS), num(a.get('PK1AEP'), CFS), num(a.get('PK02AEP'), CFS),
                 num(a.get('BFWDTH'), FT), num(a.get('BFDPTH'), FT), num(a.get('BCORDE1HYR'), FT), a.get('HWYCLASS'), a.get('HWYHDF')])
json.dump(dict(source='Massachusetts Stream Crossings Project (USGS, UMass Amherst, MassDEP) ArcGIS feature service; units converted to SI', fetched=time.strftime('%Y-%m-%d'), n=len(rows),
               columns=['lon', 'lat', 'naacc', 'road', 'stream', 'town', 'drn_km2', 'pk10', 'pk25', 'pk50', 'pk100', 'pk500', 'bf_w', 'bf_d', 'deck_m', 'hwy_class', 'design_flood'],
               note='peak flows m3/s from StreamStats regression; deck_m = original road deck elevation (NAVD88 m) from the 100-yr box design record; sample fields first-run, verify units against the data dictionary (table 2)', rows=rows),
          open('docs/network/crossings_ma.json', 'w'), separators=(',', ':'))
print(len(rows), 'crossings; with 100-yr flow:', sum(1 for x in rows if x[10]), '; sample:', rows[0] if rows else None)
