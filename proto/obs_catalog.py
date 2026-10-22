"""Storm catalogue helper (run on GitHub Actions: .github/workflows/obs_catalog.yml).

  discover: every Massachusetts NWS Local Storm Report (IEM) of type FLOOD / FLASH FLOOD / HEAVY RAIN and every NOAA Storm Events
            row (Flash Flood / Flood / Heavy Rain) for --years, written to docs/proto/obs/catalog/ for ranking offline.
  fetch:    for every event in docs/proto/obs/catalog.json run proto/obs_fetch.py's gauges / LSR / Storm Events pulls for the event's
            lon/lat box and dates (same outputs as obs.yml: gauges_<id>.json, lsr_<id>.csv, stormevents_<id>.csv).

    python proto/obs_catalog.py discover --years 2014-2026
    python proto/obs_catalog.py fetch --catalog docs/proto/obs/catalog.json
"""
import os, sys, csv, io, gzip, json, re, argparse
sys.path.insert(0, os.path.dirname(__file__))
import obs_fetch as OF

SE = 'https://www.ncei.noaa.gov/pub/data/swdi/stormevents/csvfiles/'
SE_COLS = ('EVENT_ID', 'EPISODE_ID', 'EVENT_TYPE', 'CZ_NAME', 'CZ_TIMEZONE', 'BEGIN_DATE_TIME', 'END_DATE_TIME', 'BEGIN_LAT', 'BEGIN_LON',
           'END_LAT', 'END_LON', 'DAMAGE_PROPERTY', 'FLOOD_CAUSE', 'BEGIN_LOCATION', 'END_LOCATION', 'EPISODE_NARRATIVE', 'EVENT_NARRATIVE')


def discover(y0, y1, out):
    os.makedirs(out, exist_ok=True)
    L = []
    for y in range(y0, y1 + 1):
        r = OF.get('https://mesonet.agron.iastate.edu/cgi-bin/request/gis/lsr.py', dict(sts=f'{y}-01-01T00:00Z', ets=f'{y}-12-31T23:59Z', fmt='csv', states='MA'))
        rows = list(csv.DictReader(io.StringIO(r.text))) if r is not None else []
        keep = [x for x in rows if (x.get('TYPETEXT') or '').upper() in ('FLOOD', 'FLASH FLOOD', 'HEAVY RAIN')]
        print('LSR', y, len(rows), 'flood/rain', len(keep)); L += keep
    if L:
        with open(f'{out}/lsr_ma_flood_{y0}_{y1}.csv', 'w', newline='') as f:
            w = csv.DictWriter(f, fieldnames=list(L[0].keys()), extrasaction='ignore'); w.writeheader(); w.writerows(L)
    idx = OF.get(SE); E = []
    for y in range(y0, y1 + 1):
        fs = sorted(set(re.findall(rf'StormEvents_details-ftp_v1\.0_d{y}_c\d+\.csv\.gz', idx.text))) if idx is not None else []
        if not fs: print('Storm Events', y, 'no file'); continue
        r = OF.get(SE + fs[-1])
        if r is None: print('Storm Events', y, 'download failed'); continue
        rows = list(csv.DictReader(io.StringIO(gzip.decompress(r.content).decode('latin-1'))))
        keep = [{k: x.get(k, '') for k in SE_COLS} for x in rows
                if x['STATE'] == 'MASSACHUSETTS' and x['EVENT_TYPE'] in ('Flash Flood', 'Flood', 'Heavy Rain')]
        print('Storm Events', y, fs[-1], 'MA flood/rain', len(keep)); E += keep
    if E:
        with open(f'{out}/stormevents_ma_flood_{y0}_{y1}.csv', 'w', newline='') as f:
            w = csv.DictWriter(f, fieldnames=list(SE_COLS)); w.writeheader(); w.writerows(E)


def fetch(cat, out):
    C = json.load(open(cat))
    for ev in C['events']:
        sid, bb, a, b = ev['id'], ev['bbox_lonlat'], ev['start'], ev['end']
        print('==', sid, bb, a, b, flush=True)
        try:
            G, used = OF.gauges(bb, a, b, 'auto', ('25',))
            json.dump(dict(bbox=bb, start=a, end=b, gauges=list(G.values())), open(f'{out}/gauges_{sid}.json', 'w'))
            print('  gauges', len(G), used, [(g['site'], g.get('peak_stage_ft'), g.get('peak_q_cfs')) for g in G.values()])
        except Exception as e: print('  gauges failed', repr(e)[:200])
        for name, fn in (('lsr', lambda: OF.lsr(bb, a, b)), ('stormevents', lambda: OF.stormevents(a[:4], a, b, bb))):
            try:
                R = fn()
                if R:
                    with open(f'{out}/{name}_{sid}.csv', 'w', newline='') as f:
                        w = csv.DictWriter(f, fieldnames=list(R[0].keys())); w.writeheader(); w.writerows(R)
                print(' ', name, len(R))
            except Exception as e: print(' ', name, 'failed', repr(e)[:200])


if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('mode', choices=['discover', 'fetch']); ap.add_argument('--years', default='2014-2026')
    ap.add_argument('--catalog', default='docs/proto/obs/catalog.json'); ap.add_argument('--out', default='docs/proto/obs')
    a = ap.parse_args()
    if a.mode == 'discover':
        y0, y1 = (int(v) for v in a.years.split('-')); discover(y0, y1, f'{a.out}/catalog')
    else: fetch(a.catalog, a.out)
