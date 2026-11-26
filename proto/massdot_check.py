"""After-storm check from the MassDOT events record (rules: docs/proto/prospective/MASSDOT_EVENTS_PREREG.md, frozen e82b274fb). Reporting only.

    python proto/massdot_check.py                      # every archived storm in the forward-test window -> massdot_check.json + MASSDOT_CHECK.md
    python proto/massdot_check.py --storm arc20261126
    python proto/massdot_check.py --selftest

Nothing in the live model, the forecast, PROSPECTIVE.md or RESULTS.md is read back from this output.
"""
import argparse
import csv
import datetime as dt
import json
import os
import re
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import storm_archive as A                     # noqa: E402
from live_feeds import CLOSE_RE               # noqa: E402

ROOT = A.ROOT
EV_DIR = os.path.join(ROOT, 'docs', 'proto', 'obs', 'massdot_events')
ARCH = os.path.join(ROOT, 'docs', 'proto', 'archive')
OUT_MD = os.path.join(ROOT, 'docs', 'proto', 'prospective', 'MASSDOT_CHECK.md')
R_STRICT, R_NAME, R_SITE = 30.0, 100.0, 150.0          # prereg §2
PRE_H, POST_H, LEAD_H = 6, 12, 1                       # window: evidence start - 6 h .. end + 12 h; cycles >= 1 h before the first event
NOT_C = re.compile(r'crash|dmv|disabled|fire|police|planned|scheduled|construction|work ?zone|roadwork|special event|bridge lift|drawbridge|'
                   r'treating|maintenance', re.I)
FIELDS = ('EventType', 'EventSubType', 'LocationDescription', 'LaneBlockageDescription', 'EventDescription', 'Description', 'Cause')


def text(e): return ' '.join(str(e.get(k, '') or '') for k in FIELDS)


def classify(e):
    """'F' flood-related (scored), 'C' closure without a stated cause (reported only), None."""
    t = text(e)
    if re.search(r'crews treating roadway', t, re.I): return None
    if A.FLOOD_RE.search(t) and not A.NOT_FLOOD.search(t): return 'F'
    if CLOSE_RE.search(t) and not NOT_C.search(t): return 'C'
    return None


def events(w0, w1):
    """Class F / C events created in [w0, w1] (UTC) at a District 3 town, one per EventId."""
    out, seen = [], set(); m, end = dt.date(w0.year, w0.month, 1), dt.date(w1.year, w1.month, 1)
    months = []
    while m <= end:
        months.append(f'{m:%Y-%m}'); m = dt.date(m.year + (m.month == 12), m.month % 12 + 1, 1)
    for mo in months:
        p = os.path.join(EV_DIR, f'{mo}.jsonl')
        if not os.path.exists(p): continue
        for line in open(p):
            try: e = json.loads(line)
            except Exception: continue
            c = classify(e)
            if not c or e.get('EventId') in seen: continue
            try:
                t = A.utc(A.local_naive(e.get('EventCreatedDate') or e.get('EventStartDate')))
                lon, lat = float(e['PrimaryLongitude']), float(e['PrimaryLatitude'])
            except Exception: continue
            if not (w0 <= t <= w1): continue
            tw = A.town_of(lon, lat)
            if not tw: continue
            seen.add(e.get('EventId'))
            out.append(dict(id=e.get('EventId'), cls=c, t=t, lon=lon, lat=lat, town=tw, road=e.get('RoadwayName', '') or '',
                            type=f"{e.get('EventType', '')} / {e.get('EventSubType', '')}", where=(e.get('LocationDescription') or '')[:160]))
    return out


_RP = {}


def road_pts():
    """Densified road points of graph_segments.json every 10 m (massdot_import.road_points), the points score_v2's strict match uses."""
    if not _RP:
        from scipy.spatial import cKDTree
        import massdot_import as MI
        from prototype import norm_road
        x, y, sg, S = MI.road_points(None, 10.0)
        _RP.update(x=x, y=y, seg=sg, t=cKDTree(np.column_stack([x, y])), name=np.array([norm_road(v) for v in S['props']['road']], dtype=object), norm=norm_road)
    return _RP


def match(ev):
    """Prereg §2: segments with a road point within 30 m; else the nearest road point within 100 m of a segment named like RoadwayName."""
    R = road_pts(); x, y = A.to26986(ev['lon'], ev['lat']); ev['x'], ev['y'] = float(x), float(y)
    near = R['t'].query_ball_point([ev['x'], ev['y']], R_STRICT)
    if near: ev['segs'] = sorted({int(s) for s in R['seg'][near]}); ev['how'] = 'strict'; return ev
    k = R['norm'](re.sub(r'^(?:route|rte|rt)[\s\-]*', 'rt ', ev['road'].lower())) if ev['road'] else None
    if k:
        c = np.array(R['t'].query_ball_point([ev['x'], ev['y']], R_NAME), int)
        c = c[R['name'][R['seg'][c]] == k] if len(c) else c
        if len(c):
            d2 = (R['x'][c] - ev['x']) ** 2 + (R['y'][c] - ev['y']) ** 2
            ev['segs'] = [int(R['seg'][c[np.argmin(d2)]])]; ev['how'] = 'name'; return ev
    ev['segs'] = []; ev['how'] = 'unmatched'; return ev


def sites(evs):
    """Single-link clusters within 150 m of matched events -> list of lists of events."""
    n = len(evs); par = list(range(n))
    def f(i):
        while par[i] != i: par[i] = par[par[i]]; i = par[i]
        return i
    for i in range(n):
        for j in range(i + 1, n):
            if (evs[i]['x'] - evs[j]['x']) ** 2 + (evs[i]['y'] - evs[j]['y']) ** 2 <= R_SITE ** 2: par[f(i)] = f(j)
    g = {}
    for i in range(n): g.setdefault(f(i), []).append(evs[i])
    return list(g.values())


def load_kofn(d):
    p = os.path.join(d, 'kofn.csv')
    if not os.path.exists(p): return None
    return {int(r['segment']): r['cls'] for r in csv.DictReader(open(p))}


def in_boxes(x, y, boxes): return any(b[0] <= x <= b[2] and b[1] <= y <= b[3] for b in boxes or [])


def n_segments():
    return int(json.load(open(os.path.join(ROOT, 'docs', 'graph_segments.json')))['n'])


def score_storm(S, nseg=None):
    ev = S['evidence']; w0 = A.utc(ev['start']) - dt.timedelta(hours=PRE_H); w1 = A.utc(ev['end']) + dt.timedelta(hours=POST_H)
    E = events(w0, w1); F = [match(e) for e in E if e['cls'] == 'F']; C = [e for e in E if e['cls'] == 'C']
    res = dict(storm=S['id'], window=[A.iso(w0), A.iso(w1)], rules='MASSDOT_EVENTS_PREREG.md (e82b274fb)', made=A.iso(A._utcnow()),
               n_F=len(F), n_F_strict=sum(e['how'] == 'strict' for e in F), n_F_name=sum(e['how'] == 'name' for e in F),
               n_F_unmatched=sum(e['how'] == 'unmatched' for e in F), n_C=len(C),
               closures_unstated=[dict(id=e['id'], time=A.iso(e['t']), town=e['town'], road=e['road'], type=e['type'], where=e['where']) for e in C])
    res['events'] = [dict(id=e['id'], time=A.iso(e['t']), town=e['town'], road=e['road'], type=e['type'], where=e['where'], match=e['how'],
                          segments=e['segs'], lon=round(e['lon'], 5), lat=round(e['lat'], 5)) for e in F]
    if not F:
        res.update(status='no class-F events in the window'); return res
    first = min(e['t'] for e in F)
    cyc = [c for c in S['cycles'] if c.get('dir') and A.utc(c['cycle']) <= first - dt.timedelta(hours=LEAD_H)]
    K = {c['cycle']: load_kofn(os.path.join(S['_dir'], c['dir'])) for c in cyc}
    cyc = [c for c in cyc if K[c['cycle']] is not None]
    res['first_event'] = A.iso(first); res['cycles_in_time'] = [c['cycle'] for c in cyc]
    nseg = nseg or n_segments()

    def block(evs, label):
        G = sites([e for e in evs if e['segs']]); out = dict(sites=len(G))
        if not cyc: out.update(status='no forecast cycle issued >= 1 h before the first event'); return out
        last = max(cyc, key=lambda c: c['cycle']); kl = K[last['cycle']]
        ku = {}
        for c in cyc:
            for s, v in K[c['cycle']].items():
                if ku.get(s) != 'likely': ku[s] = v
        for name, kk, boxes in (('latest', kl, last.get('forecast_boxes')),
                                ('union', ku, [b for c in cyc for b in (c.get('forecast_boxes') or [])])):
            fl_l = {s for s, v in kk.items() if v == 'likely'}; fl_p = set(kk)
            inside = [g for g in G if any(in_boxes(e['x'], e['y'], boxes) for e in g)]
            hit_l = [g for g in G if any(set(e['segs']) & fl_l for e in g)]; hit_p = [g for g in G if any(set(e['segs']) & fl_p for e in g)]
            share_l, share_p = len(fl_l) / nseg, len(fl_p) / nseg
            r = dict(cycle=last['cycle'] if name == 'latest' else None, sites_in_boxes=len(inside), sites_outside=len(G) - len(inside),
                     flagged_likely=len(fl_l), flagged_any=len(fl_p), hits_likely=len(hit_l), hits_any=len(hit_p),
                     recall_likely=len(hit_l) / len(G) if G else None, recall_any=len(hit_p) / len(G) if G else None,
                     recall_likely_in_boxes=(sum(g in hit_l for g in inside) / len(inside)) if inside else None,
                     recall_any_in_boxes=(sum(g in hit_p for g in inside) / len(inside)) if inside else None,
                     lift_likely=(len(hit_l) / len(G) / share_l) if G and share_l else None,
                     lift_any=(len(hit_p) / len(G) / share_p) if G and share_p else None)
            if name == 'union':
                leads = []
                for g in G:
                    t_site = min(e['t'] for e in g); segs = set().union(*[set(e['segs']) for e in g])
                    ok = [c for c in cyc if segs & set(K[c['cycle']])]
                    if ok: leads.append(round((t_site - A.utc(min(c['cycle'] for c in ok))).total_seconds() / 3600, 1))
                r['lead_h'] = sorted(leads); r['lead_h_median'] = sorted(leads)[len(leads) // 2] if leads else None
            out[name] = r
        return out
    res['primary'] = block([e for e in F if e['how'] == 'strict'], 'strict')
    res['with_name_fallback'] = block([e for e in F if e['how'] in ('strict', 'name')], 'strict+name')
    res['status'] = 'scored'
    return res


def fmt(v, pct=False):
    if v is None: return '-'
    return f'{v:.0%}' if pct else (f'{v:.2f}' if isinstance(v, float) else str(v))


def write_md(R):
    L = ['# After-storm check from the MassDOT events record', '',
         'Reporting only (rules `MASSDOT_EVENTS_PREREG.md`, frozen in e82b274fb before any storm was scored). Generated by '
         '`proto/massdot_check.py` after each storm follow-up. It does not feed the live model, the forward-test result (`RESULTS.md`) or any '
         'tuning. The MassDOT record covers state roads and the events its staff enter; an empty record does not mean nothing flooded.', '',
         '## Storms', '',
         '| storm | window (UTC) | flood events (30 m / name / unmatched) | closures, no cause | sites | in boxes | likely hits | likely-or-possible hits | status |',
         '|' + ' --- |' * 9]
    tot = dict(sites=0, inb=0, hl=0, hp=0)
    for r in R:
        p = (r.get('primary') or {}).get('latest') or {}
        L.append(f"| {r['storm']} | {r['window'][0]} – {r['window'][1]} | {r['n_F']} ({r['n_F_strict']} / {r['n_F_name']} / {r['n_F_unmatched']}) | "
                 f"{r['n_C']} | {(r.get('primary') or {}).get('sites', '-')} | {p.get('sites_in_boxes', '-')} | {p.get('hits_likely', '-')} | "
                 f"{p.get('hits_any', '-')} | {r['status']} |")
        if p: tot['sites'] += (r['primary'] or {}).get('sites', 0); tot['inb'] += p['sites_in_boxes']; tot['hl'] += p['hits_likely']; tot['hp'] += p['hits_any']
    if not R: L.append('| (none yet) | | | | | | | | |')
    L += ['', '## Pooled (primary: 30 m match, latest cycle issued at least 1 h before the first flood event)', '',
          f"- Sites: {tot['sites']}; inside the forecast boxes: {tot['inb']}; on a likely segment: {tot['hl']}; on a likely-or-possible segment: {tot['hp']}.",
          '', 'Per-storm details, the union-of-cycles reading, lift, lead times and the closures with no stated cause are in '
          '`docs/proto/archive/<storm>/massdot_check.json`.']
    open(OUT_MD, 'w').write('\n'.join(L) + '\n')


def selftest():
    e = dict(EventType='Traffic Incidents', EventSubType='Traffic (Roadway Obstruction)', LocationDescription='Route 9 high water both lanes')
    assert classify(e) == 'F'
    assert classify(dict(EventType='Acts of Nature', EventSubType='Crews Treating Roadway', LocationDescription='icing')) is None
    assert classify(dict(EventType='Traffic Incidents', EventSubType='Traffic (DMV/Crash)', LaneBlockageDescription='all lanes closed')) is None
    assert classify(dict(EventType='Traffic Incidents', EventSubType='Traffic (Roadway Obstruction)', LaneBlockageDescription='road closed')) == 'C'
    g = sites([dict(x=0, y=0), dict(x=100, y=0), dict(x=400, y=0)]); assert sorted(len(s) for s in g) == [1, 2]
    print('selftest ok')


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--storm'); ap.add_argument('--root', default=ARCH); ap.add_argument('--selftest', action='store_true')
    a = ap.parse_args()
    if a.selftest: return selftest()
    t0 = A.utc(A.PROSPECTIVE_START); nseg = n_segments(); R = []
    for S in A.storms(a.root):
        if A.utc(S['evidence']['end']) < t0: continue
        if a.storm and S['id'] != a.storm: continue
        if A.utc(S['evidence']['end']) + dt.timedelta(hours=POST_H) > A._utcnow():
            A.log('massdot_check:', S['id'], 'window not closed yet'); continue
        r = score_storm(S, nseg); A.jsave(os.path.join(S['_dir'], 'massdot_check.json'), r); R.append(r)
        A.log('massdot_check:', S['id'], r['status'], 'F', r['n_F'], 'C', r['n_C'])
    if not a.storm:
        write_md(R)
    else:   # rebuild the pooled table from every saved storm file
        allr = []
        for S in A.storms(a.root):
            p = os.path.join(S['_dir'], 'massdot_check.json')
            if os.path.exists(p): allr.append(A.jload(p))
        write_md(allr)


if __name__ == '__main__':
    main()
