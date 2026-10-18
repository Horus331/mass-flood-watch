"""National Bridge Inventory for Massachusetts (FHWA, free): bridges and culverts over 20 ft with condition and hydraulic ratings.
Writes docs/network/nbi_ma.json: rows [lon, lat, id, year, type_code, culvert(0/1), waterway_adequacy(71), scour_critical(113),
deck(58), super(59), sub(60), culvert_rating(62), channel(61), adt(29), route]. Run by nbi.yml.
"""
import csv, io, json, time, os, requests
os.makedirs('docs/network', exist_ok=True)
yr = None; txt = None
for y in (2024, 2023, 2022):
    for url in (f'https://www.fhwa.dot.gov/bridge/nbi/{y}/delimited/MA{str(y)[2:]}.txt', f'https://www.fhwa.dot.gov/bridge/nbi/{y}/delimited/MA{str(y)[2:]}.TXT'):
        try:
            r = requests.get(url, timeout=120, headers={'User-Agent': 'mass-flood-watch research'}); r.raise_for_status(); txt = r.text; yr = y; print('got', url, len(txt) // 1024, 'KB'); break
        except Exception as e: print('no', url, repr(e)[:80])
    if txt: break
if not txt: raise SystemExit('NBI file not found')
def dms(v, lon=False):
    v = (v or '').strip()
    if not v.isdigit() or int(v) == 0: return None
    if lon: d, m, s = int(v[:3]), int(v[3:5]), int(v[5:]) / 100
    else: d, m, s = int(v[:2]), int(v[2:4]), int(v[4:]) / 100
    x = d + m / 60 + s / 3600
    return -x if lon else x
rows = []; rd = csv.DictReader(io.StringIO(txt))
for r in rd:
    lat = dms(r.get('LAT_016')); lon = dms(r.get('LONG_017'), lon=True)
    if lat is None or lon is None or not (41 < lat < 43.1 and -73.7 < lon < -69.8): continue
    g = lambda k: (r.get(k) or '').strip()
    t = g('STRUCTURE_TYPE_043B'); culv = 1 if t == '19' else 0
    rows.append([round(lon, 5), round(lat, 5), g('STRUCTURE_NUMBER_008'), g('YEAR_BUILT_027'), t, culv, g('WATERWAY_EVAL_071'), g('SCOUR_CRITICAL_113'), g('DECK_COND_058'), g('SUPERSTRUCTURE_COND_059'), g('SUBSTRUCTURE_COND_060'), g('CULVERT_COND_062'), g('CHANNEL_COND_061'), g('ADT_029'), g('ROUTE_NUMBER_005D')])
json.dump(dict(source=f'FHWA National Bridge Inventory {yr}, Massachusetts', fetched=time.strftime('%Y-%m-%d'), n=len(rows), culverts=sum(x[5] for x in rows),
               columns=['lon', 'lat', 'id', 'year', 'type', 'culvert', 'waterway_71', 'scour_113', 'deck_58', 'super_59', 'sub_60', 'culvert_62', 'channel_61', 'adt', 'route'], rows=rows), open('docs/network/nbi_ma.json', 'w'), separators=(',', ':'))
print(len(rows), 'structures,', sum(x[5] for x in rows), 'culverts; waterway adequacy <= 4:', sum(1 for x in rows if x[6].isdigit() and int(x[6]) <= 4), '; scour critical (<=3):', sum(1 for x in rows if x[7].isdigit() and int(x[7]) <= 3))
