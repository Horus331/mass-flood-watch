"""Roads reported flooded in past storms (proto/data/labels_*.csv: NWS reports, MassDOT, town DPWs, SeeClickFix, news), District 3 and
its edge -> docs/site/data/known_sites.json for the map: each road row says 'Reported flooded before: <dates>' and a layer shows the points.

Reported places, not model output.  Coordinates are as good as the report (coord_quality); 'town' quality points sit on the town centre and
are left out.  Usage: python proto/known_sites.py
"""
import csv, glob, json, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BOX = (-72.45, 41.93, -71.38, 42.80)          # District 3 and a 5 km edge (lon0, lat0, lon1, lat1)
OUT = os.path.join(ROOT, 'docs', 'site', 'data', 'known_sites.json')
KEEP_TYPES = {'flooded', 'closed', 'washout', 'damage', 'road_closed', 'impassable', 'culvert_failure', ''}


def main():
    rows, seen = [], set()
    for f in sorted(glob.glob(os.path.join(ROOT, 'proto', 'data', 'labels_*.csv'))):
        storm = re.sub(r'^labels_|\.csv$', '', os.path.basename(f)).split('_')[0]   # several label files per storm (sep2023 DPW, NWS, ...): one storm id
        for r in csv.DictReader(open(f, encoding='utf-8', errors='replace')):
            try: lon, lat = float(r.get('lon') or 'x'), float(r.get('lat') or 'x')
            except ValueError: continue
            if not (BOX[0] <= lon <= BOX[2] and BOX[1] <= lat <= BOX[3]): continue
            if (r.get('coord_quality') or '').strip().lower() in ('town', 'county', 'zip'): continue
            if (r.get('type') or '').strip().lower() not in KEEP_TYPES: continue
            day = (r.get('time_local') or '')[:10]
            key = (round(lon, 4), round(lat, 4), day)
            if key in seen: continue
            seen.add(key)
            src = (r.get('source') or '').strip() or re.sub(r'^https?://(www\.)?([^/]+).*', r'\2', r.get('source_url') or '')
            rows.append([round(lon, 5), round(lat, 5), (r.get('road') or '').strip()[:60], (r.get('town') or '').strip()[:30], day,
                         (r.get('type') or 'flooded').strip() or 'flooded', src[:40], (r.get('name') or '')[:90], storm])
    first = {}
    for r in rows:
        if r[4] and (r[8] not in first or r[4] < first[r[8]]): first[r[8]] = r[4]
    for r in rows: r.append(first.get(r[8], r[4]))   # the storm's first report day: one date per storm on a road row
    rows.sort(key=lambda x: x[4], reverse=True)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    json.dump(dict(made_by='proto/known_sites.py', note='roads reported flooded in past storms (reports, not model output)',
                   fields=['lon', 'lat', 'road', 'town', 'date', 'type', 'source', 'what', 'storm', 'storm_day'], sites=rows), open(OUT, 'w'), separators=(',', ':'))
    print(len(rows), 'sites from', len({r[8] for r in rows}), 'storms ->', OUT)


if __name__ == '__main__':
    main()
