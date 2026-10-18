"""Emergency facilities for the accessibility layer, from OpenStreetMap (free): hospitals, fire stations, police, ambulance stations
in and just around Massachusetts.  Writes docs/network/facilities.json = {kind: [[lon, lat, name], ...]}.  Run by facilities.yml.
"""
import json, time, requests
Q = """[out:json][timeout:180];
(
  nwr["amenity"="hospital"](41.1,-73.6,43.0,-69.8);
  nwr["amenity"="fire_station"](41.1,-73.6,43.0,-69.8);
  nwr["amenity"="police"](41.1,-73.6,43.0,-69.8);
  nwr["emergency"="ambulance_station"](41.1,-73.6,43.0,-69.8);
);
out center tags;"""
for url in ('https://overpass-api.de/api/interpreter', 'https://overpass.kumi.systems/api/interpreter'):
    try:
        r = requests.post(url, data={'data': Q}, timeout=300); r.raise_for_status(); els = r.json()['elements']; break
    except Exception as e:
        print('overpass failed', url, repr(e)[:100]); time.sleep(10)
out = {'hospital': [], 'fire_station': [], 'police': [], 'ambulance_station': []}
for e in els:
    t = e.get('tags', {}); kind = t.get('amenity') or t.get('emergency')
    if kind not in out: continue
    if kind == 'hospital' and t.get('emergency') == 'no': continue
    lon = e.get('lon') or e.get('center', {}).get('lon'); lat = e.get('lat') or e.get('center', {}).get('lat')
    if lon is None: continue
    out[kind].append([round(lon, 5), round(lat, 5), (t.get('name') or '')[:60]])
json.dump(dict(source='OpenStreetMap via Overpass, ' + time.strftime('%Y-%m-%d'), counts={k: len(v) for k, v in out.items()}, facilities=out), open('docs/network/facilities.json', 'w'), separators=(',', ':'))
print({k: len(v) for k, v in out.items()})
