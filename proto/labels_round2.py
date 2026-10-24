"""Label round 2 (docs/proto/obs/LABELS_ROUND2.md): multi-road split of NWS report text, WX1BOX SKYWARN compilations, MassDOT
water-surface crashes as a separate label source.

    python proto/labels_round2.py audit      # split every in-box/in-window LSR + Storm Events text into roads; list roads missing from the labels
    python proto/labels_round2.py queries    # OSM queries for the new road rows -> docs/proto/obs/labels_round2_queries.json (label_geocode.yml)
    python proto/labels_round2.py build      # geocode (OSM, else graph_segments) and write the rows into proto/data/labels_<storm>_*.csv
    python proto/labels_round2.py crash      # docs/proto/obs/round2/crash_water_d3.csv -> proto/data/crashwater_<storm>.csv + candidate storm days

Row ids: <PREFIX>-S<nn> = road recovered by the multi-road split of an NWS report; <PREFIX>-X<nn> = WX1BOX compilation road.  `build` is
idempotent: it drops the previous -S/-X rows of a file and writes them again.  REMOVE lists rows deleted from the catalogue files (with reason).
Locked storms (PROTOCOL.md §2) are never read or written.
"""
import os, sys, re, csv, json, argparse, datetime as dt
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import labels_expand as LE  # noqa: E402

OBS = os.path.join(ROOT, 'docs', 'proto', 'obs')
Q_PATH = os.path.join(OBS, 'labels_round2_queries.json')
AUDIT_PATH = os.path.join(OBS, 'labels_round2_sites.json')
LOCKED = ('aug2015', 'aug2018', 'aug2020', 'jul2018', 'oct2016')

# ------------------------------------------------------------------------------------------------ road splitter
SUF = {'st': 'Street', 'street': 'Street', 'rd': 'Road', 'road': 'Road', 'ave': 'Avenue', 'av': 'Avenue', 'avenue': 'Avenue', 'dr': 'Drive', 'drive': 'Drive',
       'ln': 'Lane', 'lane': 'Lane', 'hwy': 'Highway', 'highway': 'Highway', 'blvd': 'Boulevard', 'boulevard': 'Boulevard', 'sq': 'Square', 'square': 'Square',
       'pl': 'Place', 'place': 'Place', 'ct': 'Court', 'court': 'Court', 'pkwy': 'Parkway', 'parkway': 'Parkway', 'way': 'Way', 'tpke': 'Turnpike',
       'turnpike': 'Turnpike', 'cir': 'Circle', 'circle': 'Circle', 'ter': 'Terrace', 'terrace': 'Terrace', 'cutoff': 'Cutoff', 'pike': 'Pike'}
STOP = {'waters', 'basement', 'intersection', 'curb', 'over', 'along', 'road', 'banks', 'its', 'people', 'culvert', 'locations', 'following', 'inches', 'deep', 'covers', 'popped', 'lot', 'parking', 'there', 'numerous', 'impassable', 'due', 'reported', 'flooding.', 'in', 'on', 'at', 'the', 'and', 'of', 'by', 'near', 'between', 'from', 'to', 'with', 'flooded', 'flooding', 'closed', 'street', 'reports',
        'car', 'cars', 'vehicle', 'vehicles', 'water', 'also', 'several', 'portions', 'parts', 'flash', 'flood', 'heavy', 'rain', 'stuck', 'a', 'an',
        'was', 'were', 'is', 'are', 'has', 'had', 'significant', 'major', 'minor', 'localized', 'relayed', 'amateur', 'radio', 'est', 'edt', 'pm', 'am'}
ROAD_RE = re.compile(r"\b((?:[A-Z][a-zA-Z'\.]+|\d+(?:st|nd|rd|th))(?:\s+(?:[A-Z][a-zA-Z'\.]+|\d+(?:st|nd|rd|th))){0,3})\s+"
                     r"(St|Street|Rd|Road|Ave|Av|Avenue|Dr|Drive|Ln|Lane|Hwy|Highway|Blvd|Boulevard|Sq|Square|Pl|Place|Ct|Court|Pkwy|Parkway|Way|Tpke|Turnpike|"
                     r"Cir|Circle|Ter|Terrace|Cutoff|Pike)\b\.?", re.I)
ROUTE_RE = re.compile(r'\b(?:Route|Rte|Rt|State Route|US|U\.S\.|I|Interstate)[\s\-\.]*(\d{1,3}[A-Z]?)\b', re.I)


def roads(text):
    """Every road named in a free-text report, normalised ('Sunny Hill Rd' -> 'Sunny Hill Road', 'RT 2' -> 'Route 2')."""
    t = re.sub(r'_', ',', text or ''); out = []
    if t.isupper(): t = t.title()
    for m in ROAD_RE.finditer(t):
        w = m.group(1).split(); cut = 0
        for k, x in enumerate(w):          # keep the words after the last stop word, inner road suffix or sentence end
            if x.lower().strip('.') in STOP or x.lower().strip('.') in SUF or x.endswith('.'): cut = k + 1
        w = w[cut:]
        if not w: continue
        nm = ' '.join(x.capitalize() if x.islower() else x for x in w) + ' ' + SUF[m.group(2).lower().strip('.')]
        out.append(nm)
    for m in ROUTE_RE.finditer(t):
        p = m.group(0).lower(); n = m.group(1).upper()
        out.append(('I-' if p.startswith(('i', 'interstate')) and not p.startswith('in ') else 'Route ') + n)
    seen = []; [seen.append(x) for x in out if x not in seen]
    return seen


def norm(s): return re.sub(r'[^a-z0-9]', '', s.lower())


def storm_rows(e):
    """In-box, in-window LSR (FLOOD / FLASH FLOOD) and Storm Events (Flood / Flash Flood) rows of a catalogue storm: (source, time_utc, town, text, lon, lat, id)."""
    from pyproj import Transformer
    T = Transformer.from_crs(4326, 26986, always_xy=True); bx = e['box_26986']
    t0 = dt.datetime.strptime(e['t0'], '%Y-%m-%dT%H:00Z'); t1 = t0 + dt.timedelta(hours=int(e['hours']))
    inb = lambda lo, la: (lambda p: bx[0] <= p[0] < bx[2] and bx[1] <= p[1] < bx[3])(T.transform(lo, la))
    out = []; p = os.path.join(OBS, f"lsr_{e['id']}.csv")
    if os.path.exists(p):
        for r in csv.DictReader(open(p)):
            if r['TYPETEXT'].upper() not in ('FLOOD', 'FLASH FLOOD', 'HEAVY RAIN'): continue
            t = dt.datetime.strptime(r['VALID'], '%Y%m%d%H%M')
            if t0 <= t <= t1 and inb(float(r['LON']), float(r['LAT'])): out.append(('LSR', t, r['CITY'], r['REMARK'], float(r['LON']), float(r['LAT']), r['VALID']))
    p = os.path.join(OBS, f"stormevents_{e['id']}.csv")
    if os.path.exists(p):
        for r in csv.DictReader(open(p)):
            if r['EVENT_TYPE'] not in ('Flood', 'Flash Flood') or not r['BEGIN_LAT']: continue
            t = dt.datetime.strptime(r['BEGIN_DATE_TIME'], '%d-%b-%y %H:%M:%S') + dt.timedelta(hours=5)      # Storm Events times are EST
            if t0 <= t <= t1 and inb(float(r['BEGIN_LON']), float(r['BEGIN_LAT'])):
                out.append(('StormEvents', t, r['BEGIN_LOCATION'].title(), r['EVENT_NARRATIVE'], float(r['BEGIN_LON']), float(r['BEGIN_LAT']), r['EVENT_ID']))
    return out


def catalog():
    return [e for e in json.load(open(os.path.join(OBS, 'catalog.json')))['events'] if e['id'] not in LOCKED]


def label_paths(sid):
    import glob
    return [p for p in sorted(glob.glob(os.path.join(HERE, 'data', f'labels_{sid}_*.csv'))) if not p.endswith('_dpw.csv')]


def audit():
    rep = {}
    for e in catalog():
        L = [r for p in label_paths(e['id']) for r in csv.DictReader(open(p))]
        have = {norm(x) for r in L for x in [r['road']] + roads(r['name']) + roads(r['quote'])}
        miss = []
        for src, t, town, text, lo, la, rid in storm_rows(e):
            R = roads(text)
            m = [x for x in R if norm(x) not in have]
            if m: miss.append(dict(source=src, id=rid, time_utc=t.strftime('%Y-%m-%dT%H:%MZ'), town=town, roads_in_text=R, missing=m, text=text))
        if miss: rep[e['id']] = miss
    for sid, M in rep.items():
        print('==', sid)
        for m in M: print('  ', m['source'], m['id'], m['town'], '| missing:', m['missing'], '|', m['text'][:260])
    json.dump(rep, open(os.path.join(OBS, 'round2', 'split_audit.json'), 'w'), indent=1)


# ------------------------------------------------------------------------------------------------ new rows
# (storm, town, road, name, type, t_utc | date, quote, url, source, geocode[, source_detail])  -- same tuple as labels_expand.S
LSR, SE = LE.LSR, LE.SE
WX = 'https://wx1box.org/wp-content/uploads/'
S2 = [
 # ---- multi-road split: roads named in an NWS report but lost by the first catalogue parser (it kept one point per report) ----
 ('aug2026', 'Leominster', 'West Street', 'West Street at Hillary Road: impassable (car stuck to the passenger compartment)', 'impassable', '2026-08-03T11:47Z',
  'West Street at Hillary Road - car stuck in flood waters and up to the passenger compartment - person needs assistance getting out of the car.',
  LSR('2026-08-03T11:47Z'), 'LSR', dict(g='pair', a='West Street', b='Hillary Road', near=(-71.77, 42.52))),
 ('aug2026', 'Leominster', 'Union Street', 'Union Street: closed', 'closed', '2026-08-03T11:47Z',
  'Union Street closed due to flooding.', LSR('2026-08-03T11:47Z'), 'LSR', dict(g='cent', a='Union Street', near=(-71.77, 42.52))),
 ('aug2026', 'Leominster', 'Washington Street', 'Washington Street at Washington Square: closed', 'closed', '2026-08-03T11:47Z',
  'Washington street at Washington square closed due to flooding.', LSR('2026-08-03T11:47Z'), 'LSR',
  dict(g='pair', a='Washington Street', b='Washington Square', near=(-71.77, 42.52), q='approx')),
 ('aug2026', 'Lunenburg', 'Sunny Hill Road', 'Sunny Hill Road between West Street and Massachusetts Avenue: impassable', 'impassable', '2026-08-03T11:52Z',
  'Sunny Hill Road between West Street and Massachusetts Avenue flooded and impassable.', LSR('2026-08-03T11:52Z'), 'LSR',
  dict(g='cent', a='Sunny Hill Road', near=(-71.73, 42.59))),
 ('aug2023', 'Natick', 'Speen Street', 'Speen Street near Nottingham Drive: impassable (vehicles stuck)', 'impassable', '2023-08-08T15:01Z',
  'Vehicles stuck in water on Speen Street near Nottingham Drive.', LSR('2023-08-08T15:01Z'), 'LSR',
  dict(g='pair', a='Speen Street', b='Nottingham Drive', near=(-71.35, 42.28), q='approx')),
 ('sep2022', 'Webster', 'West Main Street', 'West Main Street (Route 197) at Mason Road: closed', 'closed', '2022-09-05T15:05Z',
  'WEST MAIN STREET (RTE 197) AT MASON ROAD CLOSED DUE TO FLOODING PER LAW ENFORCEMENT REPORTED BY AMATEUR RADIO.', LSR('2022-09-05T15:05Z'), 'LSR',
  dict(g='pair', a='West Main Street|ref:MA 197', b='Mason Road|Mason Lane', near=(-71.8688, 42.0746))),
 ('sep2021', 'Worcester', 'Quinsigamond Avenue', 'Quinsigamond Avenue (parts): closed', 'closed', '2021-09-02T06:30Z',
  'At 230 AM EDT, parts of Southbridge Street and parts of Quinsigamond Avenue were closed due to flooding.', SE(984615), 'StormEvents',
  dict(g='cent', a='Quinsigamond Avenue', near=(-71.80, 42.25))),
 # ---- WX1BOX SKYWARN storm-report compilations: road reports that reached no NWS LSR / Storm Events row (local times EDT) ----
 ('aug2026', 'Princeton', 'Mirick Road', 'Mirick Road from East Princeton Road to Beaman Road: closed', 'closed', '2026-08-03T14:00Z',
  'Princeton, MA: Mirick Road closed from East Princeton Road to Beaman Road due to flooding', WX + '2026/08/reports_8_3_26.pdf', 'WX1BOX',
  dict(g='cent', a='Mirick Road', near=(-71.84, 42.47))),
 ('jul2023b', 'Westminster', 'Main Street', 'Main Street (section): impassable', 'impassable', '2023-07-10T21:15Z',
  'Westminster, MA: section of Main Street flooded and impassable', WX + '2023/07/reports_7_10_23.pdf', 'WX1BOX',
  dict(g='cent', a='Main Street', near=(-71.91, 42.55))),
]
REMOVE = [('labels_aug2026_leominster.csv', 'AUG2026-01', 'LSR is a flooded basement on Allen Hill Road, not a road report')]      # (file, id, reason)


def key(i, s): return f'r2:{s[0]}:{i:03d}'


def queries():
    Q = []
    for i, s in enumerate(S2):
        g = s[9]
        Q.append(dict(key=key(i, s), town=s[1], towns=g.get('towns'), a=g['a'], b=g.get('b') if g['g'] == 'pair' else None,
                      near=list(g['near']) if g.get('near') else None, addr=g.get('addr')))
    json.dump(Q, open(Q_PATH, 'w'), indent=1); print(len(Q), 'queries ->', Q_PATH)


def build():
    R = LE.load_osm(); G, T, TI = LE._net(); rows = {}; audit = []
    for i, s in enumerate(S2):
        storm, town, road, name, typ, t, quote, url, src, g = s[:10]
        assert storm not in LOCKED
        r = LE.pick(s, R.get(key(i, s)))
        if r is None or (g['g'] == 'pair' and r[2] != 'exact' and g.get('q') != 'approx'):
            n = LE.net_geocode(G, T, TI, s)
            if n and (r is None or n[2] == 'exact'): r = n
        if r is None: r = (g['near'][0], g['near'][1], 'town', 'not placed: report point kept')
        lon, lat, q, how = r
        if len(t) == 10: tl, tq = f'{t}T12:00', 'day'
        else: tl, tq = (dt.datetime.strptime(t, '%Y-%m-%dT%H:%MZ') - dt.timedelta(hours=4)).strftime('%Y-%m-%dT%H:%M'), 'report'
        kind = 'X' if src == 'WX1BOX' else 'S'
        rows.setdefault(storm, []).append(dict(_k=kind, name=name, road=road, town=town, type=typ, time_local=tl, time_quality=tq, lon=f'{float(lon):.5f}',
                                               lat=f'{float(lat):.5f}', coord_quality=q, source_url=url, quote=quote, source=src))
        audit.append(dict(key=key(i, s), storm=storm, town=town, road=road, source=src, coord_quality=q, how=how, lon=float(lon), lat=float(lat)))
    files = {}
    for f, rid, why in REMOVE: files.setdefault(f, [])
    for storm in rows: files.setdefault(LE.FILES.get(storm) or os.path.basename(label_paths(storm)[0]), [])
    for f in files:
        path = os.path.join(HERE, 'data', f); old = list(csv.DictReader(open(path))); hdr = list(old[0].keys())
        storm = re.match(r'labels_([a-z]+\d{4}[a-z]?)_', f).group(1); assert storm not in LOCKED
        pre = re.match(r'(.*?)-?\d+$', [o['id'] for o in old if not re.search(r'-[NSX]\d+$', o['id'])][0]).group(1)
        drop = {rid for ff, rid, _ in REMOVE if ff == f}
        keep = [o for o in old if o['id'] not in drop and not re.search(rf'^{re.escape(pre)}-[SX]\d+$', o['id'])]
        new = rows.get(storm, []); n = dict(S=0, X=0)
        for r in new: n[r['_k']] += 1; r['id'] = f"{pre}-{r['_k']}{n[r['_k']]:02d}"
        LE.write_csv(path, hdr, keep + new); print(f'{f}: {len(old)} -> {len(keep) + len(new)} rows ({len(drop)} removed, {len(new)} round-2)')
    json.dump(dict(sites=audit, removed=[dict(file=f, id=i, reason=w) for f, i, w in REMOVE]), open(AUDIT_PATH, 'w'), indent=1)


if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('cmd', choices=['audit', 'queries', 'build', 'crash']); a = ap.parse_args()
    if a.cmd == 'crash':
        import crashwater; crashwater.main()
    else: dict(audit=audit, queries=queries, build=build)[a.cmd]()
