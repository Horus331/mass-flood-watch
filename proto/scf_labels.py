"""SeeClickFix 311 flooding issues as a SEPARATE label source (docs/proto/obs/LABELS_ROUND3.md).

    python proto/scf_labels.py        # docs/proto/obs/round3/scf_window_<storm>.json -> proto/data/scf_<storm>.csv
                                      # docs/proto/obs/round3/scf_flood_d3.csv       -> docs/proto/obs/round3/scf_days.json (candidate storm days)

Input: pulled on Actions by proto/scf_fetch.py (seeclickfix.com /api/v2/issues; every issue of every type inside each non-locked catalogue
storm box, created t0 .. t0 + hours + 24 h UTC).  Kept (label_ok): issues whose request type names flooding or a washout (Flooding Condition on
Street, Storm Water Drainage/Flooding, Washout On Street, Catch Basin Not Taking Water) or whose type / summary / description says flood,
standing water, ponding, water over the road or washed out; routine drain-clog and sweeping requests without such words are not labels,
nor basement-only reports that never mention the street.  The broad drainage net (flood_like) is kept for the window counts.
One row per issue, in the label CSV schema: lon / lat exact from the issue, time_local = created_at (local), name = summary, quote =
description, type `reported_flooding`, time_quality / coord_quality `exact`, source_url = issue page, source `SeeClickFix`.
Files are named scf_<storm>.csv (never labels_*.csv), so score_v2.py ignores them unless SCORE_SCF=1.  Locked storms are never read or written.

Candidate storms: local days 2018-2026 with >= 5 flooding-type issues (catch-basin-only complaints excluded) inside one 20 x 20 km window
(EPSG:26986, inside the union of the catalogue boxes), not overlapping a catalogue window.  Locked-storm days were dropped before the fetch committed anything.
"""
import csv, json, os, re, datetime as dt
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
R3 = os.path.join(ROOT, 'docs', 'proto', 'obs', 'round3'); DATA = os.path.join(HERE, 'data')
MIN_DAY = 5
LOCKED = ('aug2015', 'aug2018', 'aug2020', 'jul2018', 'oct2016')
COLS = ['id', 'name', 'road', 'town', 'type', 'time_local', 'time_quality', 'lon', 'lat', 'coord_quality', 'source_url', 'quote', 'source',
        'request_type', 'status']
TYPE_RE = re.compile(r'flood|catch ?basin|drain|storm ?water|stormwater|culvert|ponding', re.I)
TEXT_RE = re.compile(r'flood|standing water|ponding|puddl|water (is )?(on|in|across|over|covering) (the )?(road|street|roadway)|under ?water|'
                     r'washed out|washout|catch ?basin|storm drain|drain', re.I)
STRONG_RE = re.compile(r'flood|standing water|ponding|water (is )?(on|in|across|over|covering) (the )?(road|street|roadway)|under ?water|washed out|washout', re.I)
SUFFIX = r'(?:St|Street|Ave|Avenue|Rd|Road|Dr|Drive|Ln|Lane|Pl|Place|Ct|Court|Blvd|Boulevard|Pkwy|Parkway|Ter|Terrace|Way|Hwy|Highway|Tpke|Turnpike|Cir|Circle|Sq|Square|Sq)'
ADDR_RE = re.compile(rf'^\s*(?:[\d\-A-Za-z]*\d[\d\-A-Za-z]*\s+)?(.+?\b{SUFFIX}\.?)\s+(.+?),\s*(?:Massachusetts|MA)\b', re.I)


def catalog():
    return json.load(open(os.path.join(ROOT, 'docs', 'proto', 'obs', 'catalog.json')))['events']


LABEL_TYPE_RE = re.compile(r'flood|washout|wash out|not taking water', re.I)
ROAD_WORD = re.compile(r'street|road|\bst\b|\brd\b|\bave|roadway|intersection|corner', re.I)


def flood_like(i):      # broad net, used for the window counts
    t = str(i.get('request_type') or ''); txt = f"{i.get('summary') or ''} {i.get('description') or ''}"
    return bool(TYPE_RE.search(t) or TEXT_RE.search(txt))


def label_ok(i):
    """Label rows: a flooding / washout request type, or flooding words in the text; routine drain-clog or sweeping requests without
    flooding words are not labels, nor basement-only reports that never mention the street."""
    t = str(i.get('request_type') or ''); txt = f"{i.get('summary') or ''} {i.get('description') or ''}"
    if not (LABEL_TYPE_RE.search(t) or STRONG_RE.search(f'{t} {txt}')): return False
    if re.search(r'basement', txt, re.I) and not ROAD_WORD.search(txt): return False
    return True


def strong(i):      # flooding proper, not a routine catch-basin complaint
    t = str(i.get('request_type') or ''); txt = f"{t} {i.get('summary') or ''} {i.get('description') or ''}"
    return bool(STRONG_RE.search(txt))


def road_town(addr):
    m = ADDR_RE.match(addr or '')
    if m:
        road, town = m.group(1).strip(), re.split(rf'\b{SUFFIX}\.?\s+', m.group(2).strip())[-1].strip()
        if m.group(2).lstrip().startswith(('&', 'and ', '@', 'at ')): road = f"{road} & {m.group(2).strip().lstrip('&@ ').rsplit(' ' + town, 1)[0]}"
        return road, town
    parts = [p.strip() for p in (addr or '').split(',')]
    return (parts[0] if parts else ''), ''


def local(s):
    t = dt.datetime.fromisoformat(s.replace('Z', '+00:00'))
    if t.utcoffset() is not None and t.utcoffset() == dt.timedelta(0):      # UTC -> Eastern (EDT/EST by month; good enough for labels)
        t = t + dt.timedelta(hours=-4 if 3 < t.month < 11 else -5)
    return t.replace(tzinfo=None)


def build():
    out = {}
    for e in catalog():
        s = e['id']
        if s in LOCKED: continue
        f = os.path.join(R3, f'scf_window_{s}.json')
        if not os.path.exists(f): continue
        J = json.load(open(f)); rows = []
        for i in sorted(J['issues'], key=lambda i: i['created_at']):
            if not label_ok(i) or i.get('lat') is None: continue
            lo0, la0, lo1, la1 = e['bbox_lonlat']
            if not (lo0 <= float(i['lng']) <= lo1 and la0 <= float(i['lat']) <= la1): continue
            road, town = road_town(i.get('address'))
            rows.append(dict(id=f"SCF-{s}-{i['id']}", name=(i.get('summary') or '').strip(), road=road, town=town, type='reported_flooding',
                             time_local=local(i['created_at']).strftime('%Y-%m-%dT%H:%M'), time_quality='exact', lon=round(float(i['lng']), 6),
                             lat=round(float(i['lat']), 6), coord_quality='exact', source_url=i.get('html_url') or f"https://seeclickfix.com/issues/{i['id']}",
                             quote=re.sub(r'\s+', ' ', (i.get('description') or '').strip())[:300], source='SeeClickFix',
                             request_type=i.get('request_type') or '', status=i.get('status') or ''))
        p = os.path.join(DATA, f'scf_{s}.csv')
        if rows:
            with open(p, 'w', newline='') as fh:
                w = csv.DictWriter(fh, COLS); w.writeheader(); w.writerows(rows)
        elif os.path.exists(p): os.remove(p)
        out[s] = dict(issues_in_window=J['n'], flood_rows=len(rows), strong=sum(strong(i) for i in J['issues'] if flood_like(i)),
                      types=sorted({r['request_type'] for r in rows}))
        print(f"{s:9s} window issues {J['n']:4d}  flooding rows {len(rows):3d}")
    return out


def days():
    f = os.path.join(R3, 'scf_flood_d3.csv')
    if not os.path.exists(f): return {}
    from pyproj import Transformer
    tr = Transformer.from_crs(4326, 26986, always_xy=True)
    W = []
    for e in catalog():
        t0 = dt.datetime.strptime(e['t0'], '%Y-%m-%dT%H:00Z'); a = local(t0.isoformat() + 'Z'); b = a + dt.timedelta(hours=int(e['hours']) + 24)
        W.append((e['id'], a, b))
    B = [e['box_26986'] for e in catalog()]; D3 = (min(b[0] for b in B), min(b[1] for b in B), max(b[2] for b in B), max(b[3] for b in B))
    by = defaultdict(list)
    for r in csv.DictReader(open(f)):
        if not strong(r): continue
        t = local(r['created_at']); x, y = tr.transform(float(r['lng']), float(r['lat']))
        if not (D3[0] <= x < D3[2] and D3[1] <= y < D3[3]): continue
        by[t.date()].append((x, y, r))
    cand = []
    for d, P in sorted(by.items()):
        if len(P) < 3: continue
        best = (0, None)
        xs = sorted({int(p[0] // 1000) * 1000 for p in P}); ys = sorted({int(p[1] // 1000) * 1000 for p in P})
        for x0 in {v - k * 1000 for v in xs for k in range(0, 20, 2)}:
            for y0 in {v - k * 1000 for v in ys for k in range(0, 20, 2)}:
                n = sum(x0 <= p[0] < x0 + 20000 and y0 <= p[1] < y0 + 20000 for p in P)
                if n > best[0]: best = (n, (x0, y0))
        if best[0] < MIN_DAY: continue
        inwin = [p for p in P if best[1][0] <= p[0] < best[1][0] + 20000 and best[1][1] <= p[1] < best[1][1] + 20000]
        day0 = dt.datetime.combine(d, dt.time()); day1 = day0 + dt.timedelta(days=1)
        cat = [s for s, a, b in W if a < day1 and b > day0]
        if any(s in LOCKED for s in cat): continue
        towns = sorted({road_town(p[2]['address'])[1] for p in inwin} - {''})
        cand.append(dict(date=str(d), n_day=len(P), n_window=best[0], box_26986=[best[1][0], best[1][1], best[1][0] + 20000, best[1][1] + 20000],
                         towns=towns, catalogue=cat, examples=[p[2]['summary'] + ' | ' + (p[2]['address'] or '') for p in inwin[:4]]))
    res = dict(made_by='proto/scf_labels.py', rule=f'>= {MIN_DAY} flooding-type SeeClickFix issues (catch-basin-only excluded) in one 20 x 20 km window inside the union of the catalogue boxes on a local day; catalogue = a catalogue window overlaps the day (any box)',
               n_days=len(cand), not_in_catalogue=[c for c in cand if not c['catalogue']], in_catalogue=[c for c in cand if c['catalogue']])
    json.dump(res, open(os.path.join(R3, 'scf_days.json'), 'w'), indent=1)
    print('candidate days', len(cand), 'not in catalogue', len(res['not_in_catalogue']))
    return res


if __name__ == '__main__':
    B = build(); json.dump(B, open(os.path.join(R3, 'scf_labels_summary.json'), 'w'), indent=1); days()
