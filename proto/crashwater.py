"""MassDOT crashes with road surface 'Water (standing, moving)' (crash report code 6) as a separate label source (docs/proto/obs/LABELS_ROUND2.md).

    python proto/crashwater.py            # docs/proto/obs/round2/crash_water_d3.csv -> proto/data/crashwater_<storm>.csv + round2/crashwater_days.json

Input: the IMPACT Crash Open Data feature services (gis.crashdata.dot.mass.gov, MASSDOT_ODP_OPEN_<year>), pulled on Actions by
proto/labels_round2_fetch.py crash.  One row per crash inside a catalogue storm's window (t0 - 2 h .. t0 + hours + 6 h, local crash time) and
inside the storm box: type `water_crash`, time_quality `report` (crash time = water on the road), coord_quality `exact` (MassDOT X/Y).
These files are never named labels_*.csv, so score_v2.py ignores them unless SCORE_CRASHWATER=1.  Locked storms are skipped.

Storm discovery: every local calendar day 2021-2026 with >= 3 water-surface crashes inside one 20 x 20 km window in District 3 is listed as a
candidate storm day, independent of NWS reports (2018-2020 have no open-data service).
"""
import os, re, csv, json, datetime as dt
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
R2 = os.path.join(ROOT, 'docs', 'proto', 'obs', 'round2')
LOCKED = ('aug2015', 'aug2018', 'aug2020', 'jul2018', 'oct2016')
COLS = ['id', 'name', 'road', 'town', 'type', 'time_local', 'time_quality', 'lon', 'lat', 'coord_quality', 'source_url', 'quote', 'source', 'crash_numb']
SVC = 'https://gis.crashdata.dot.mass.gov/arcgis/rest/services/MassDOT/MASSDOT_ODP_OPEN_{y}/FeatureServer/0/query?where=CRASH_NUMB%3D{n}&outFields=*&f=json'
D3 = (128000.0, 856000.0, 206000.0, 946000.0)


def t_local(r):
    s = re.sub(r'[/-]', ' ', r['CRASH_DATE_TEXT'].strip())[:10]
    d = dt.datetime.strptime(s, '%m %d %Y')                                     # IMPACT open data: 'MM DD YYYY'
    tt = (r.get('CRASH_TIME_2') or '').strip()
    for f in ('%I:%M %p', '%H:%M', '%I:%M:%S %p', '%H:%M:%S'):
        try: x = dt.datetime.strptime(tt, f); return d.replace(hour=x.hour, minute=x.minute), True
        except ValueError: pass
    return d.replace(hour=12), False


def load():
    out = []
    P = [os.path.join(R2, f) for f in ('crash_water_d3.csv', 'crash_water_d3_2018_2020.csv') if os.path.exists(os.path.join(R2, f))]
    for r in (r for p in P for r in csv.DictReader(open(p))):
        try: x, y = float(r['X']), float(r['Y']); lon, lat = float(r['LON']), float(r['LAT'])
        except (TypeError, ValueError): continue
        try: t, ok = t_local(r)
        except Exception: continue
        out.append(dict(r=r, x=x, y=y, lon=lon, lat=lat, t=t, timed=ok))
    return out


def road_of(r):
    a = (r.get('RDWY') or '').strip().title(); b = (r.get('NEAR_INT_RDWY') or '').strip().title()
    return a or b, (f'{a} at {b}' if a and b else a or b or 'unknown road')


def main():
    C = [e for e in json.load(open(os.path.join(ROOT, 'docs', 'proto', 'obs', 'catalog.json')))['events'] if e['id'] not in LOCKED]
    K = load(); summ = {}
    for e in C:
        t0 = dt.datetime.strptime(e['t0'], '%Y-%m-%dT%H:00Z') - dt.timedelta(hours=4)          # EDT (all catalogue storms are May-Sep)
        w0, w1 = t0 - dt.timedelta(hours=2), t0 + dt.timedelta(hours=int(e['hours']) + 6); bx = e['box_26986']
        rows = []
        for k in sorted((k for k in K if w0 <= k['t'] <= w1 and bx[0] <= k['x'] < bx[2] and bx[1] <= k['y'] < bx[3]), key=lambda k: k['t']):
            r = k['r']; road, nm = road_of(r)
            q = '; '.join(f'{f}={(r.get(f) or "").strip()}' for f in ('ROAD_SURF_COND_DESCR', 'WEATH_COND_DESCR', 'CRASH_DATE_TEXT', 'CRASH_TIME_2', 'RDWY', 'NEAR_INT_RDWY',
                                                                        'CRASH_SEVERITY_DESCR', 'MANR_COLL_DESCR', 'FIRST_HRMF_EVENT_DESCR') if (r.get(f) or '').strip())
            rows.append(dict(name=f'{nm}: crash on water-covered road', road=road, town=(r.get('CITY_TOWN_NAME') or '').title(), type='water_crash',
                             time_local=k['t'].strftime('%Y-%m-%dT%H:%M'), time_quality='report' if k['timed'] else 'day', lon=f"{k['lon']:.5f}", lat=f"{k['lat']:.5f}",
                             coord_quality='exact', source_url=SVC.format(y=k['t'].year if k['t'].year != 2023 else '2023v', n=r['CRASH_NUMB']), quote=q,
                             source='MassDOT_crash', crash_numb=r['CRASH_NUMB']))
        path = os.path.join(HERE, 'data', f"crashwater_{e['id']}.csv")
        if rows:
            for i, r in enumerate(rows): r['id'] = f"CW-{e['id']}-{i + 1:02d}"
            with open(path, 'w', newline='') as f: w = csv.DictWriter(f, fieldnames=COLS); w.writeheader(); w.writerows(rows)
        elif os.path.exists(path): os.remove(path)
        cover = e['t0'] >= '2021-01-01'
        summ[e['id']] = dict(window_local=[w0.strftime('%Y-%m-%dT%H:%M'), w1.strftime('%Y-%m-%dT%H:%M')], crash_data=cover, n=len(rows))
        if rows or cover: print(e['id'], 'crash data' if cover else 'no crash data (pre-2021)', len(rows))
    # storm-day discovery: >= 3 water crashes in one 20 x 20 km window (1 km grid of window origins), District 3 box
    byday = defaultdict(list)
    for k in K:
        if D3[0] - 10000 <= k['x'] < D3[2] and D3[1] - 10000 <= k['y'] < D3[3]: byday[k['t'].date()].append(k)
    cat_days = {}
    for e in json.load(open(os.path.join(ROOT, 'docs', 'proto', 'obs', 'catalog.json')))['events']:      # dates only (locked storms: no labels read)
        if 't0' in e: cat_days[(dt.datetime.strptime(e['t0'], '%Y-%m-%dT%H:00Z') - dt.timedelta(hours=4)).date()] = e['id']
    days = []
    for d, L in sorted(byday.items()):
        if len(L) < 2: continue
        best = None
        for x0 in range(int(D3[0] / 1000) - 10, int(D3[2] / 1000) - 10, 2):
            for y0 in range(int(D3[1] / 1000) - 10, int(D3[3] / 1000) - 10, 2):
                n = [k for k in L if x0 * 1000 <= k['x'] < x0 * 1000 + 20000 and y0 * 1000 <= k['y'] < y0 * 1000 + 20000]
                if best is None or len(n) > len(best[0]): best = (n, [x0 * 1000, y0 * 1000, x0 * 1000 + 20000, y0 * 1000 + 20000])
        if len(best[0]) >= 2:
            days.append(dict(date=str(d), n_box=len(best[0]), n_d3=len(L), box_26986=best[1], catalogue=cat_days.get(d, cat_days.get(d - dt.timedelta(days=1))),
                             towns=sorted({(k['r'].get('CITY_TOWN_NAME') or '').title() for k in best[0]}),
                             times=sorted(k['t'].strftime('%H:%M') for k in best[0]),
                             weather=sorted({(k['r'].get('WEATH_COND_DESCR') or '').strip() for k in best[0]})))
    # the locked storms' dates are reported only as 'catalogue: <id>' (no crash rows are read for them; none exist before 2021 anyway)
    json.dump(dict(storms=summ, candidate_days=days, rule='>= 3 (strong) or 2 (weak) water-surface crashes (code 6) in one 20 x 20 km window, District 3 +10 km, local day'),
              open(os.path.join(R2, 'crashwater_days.json'), 'w'), indent=1)
    for d in days: print('candidate day', d['date'], d['n_box'], d['towns'], d['catalogue'], d['weather'])


if __name__ == '__main__':
    main()
