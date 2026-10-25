"""Automatic storm archive for MassDOT District 3 (docs/proto/archive/README.md): every future storm becomes a test case.

A storm is ARCHIVED when, on any 6-hourly forecast cycle (.github/workflows/forecast.yml), the forecast gate fires (proto/forecast.py) OR the
NWS has issued a Flash Flood Warning / Flood Advisory whose polygon touches a District 3 town (Worcester, western Middlesex, the Franklin /
Hampshire towns in D3).  Then:
  forecast.yml       keeps that cycle's forecast under <root>/<YYYYMMDD>_<id>/forecast/<YYYYMMDDHH>/ (status, gate, alerts, k-of-n table);
  archive_followup.yml (twice a day) 24-36 h after the event: collects labels for the storm window (IEM LSR, NOAA Storm Events when published,
                     MassDOT roadway events log, SeeClickFix) -> proto/data/labels_<id>_auto.csv; runs the flood model on the same boxes with
                     the observed MRMS radar rain (frozen docs/proto/parity/BASELINE.md settings); verifies the archived forecasts against
                     the radar run and the labels (score_v2); refreshes <root>/ARCHIVE.md, skill.json and catalog_candidates.json.

    python proto/storm_archive.py alerts  --out alerts.json [--window 2023-09-11T00:00Z/2023-09-12T06:00Z] [--lookback-h 6.5]
    python proto/storm_archive.py archive --gate gate.json --alerts alerts.json --status forecast_status.json [--kofn kofn.json] [--root R]
    python proto/storm_archive.py due     [--root R] [--now ISO] [--storm ID] --plan plan.json [--github-output F]
    python proto/storm_archive.py labels  --storm ID [--root R] [--labels-dir D] [--now ISO]
    python proto/storm_archive.py segcsv  <prototype out dir>/segments.geojson <dest>/segments.csv
    python proto/storm_archive.py finalize --plan plan.json [--root R] [--labels-dir D]      # radar results -> storm.json, verify, index
    python proto/storm_archive.py verify  --storm ID [--root R] [--labels-dir D]
    python proto/storm_archive.py index   [--root R]
    python proto/storm_archive.py selftest

Alerts: live = api.weather.gov (alerts sent / in force in the last --lookback-h hours, the time since the previous cycle); --window = the IEM
archive of NWS storm-based warnings (VTEC FF.W = Flash Flood Warning, FA.Y = Flood Advisory) for a past period (tests, backfill).
"""
import os, sys, re, io, csv, json, gzip, time, glob, shutil, argparse, datetime as dt
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.normpath(os.path.join(HERE, '..'))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(ROOT, 'sim', 'colab')); sys.path.insert(0, os.path.join(ROOT, 'sim', 'infra'))
ARCHIVE = os.path.join('docs', 'proto', 'archive')
LABELS_DIR = os.path.join('proto', 'data')
UA = {'User-Agent': 'mass-flood-watch research (github.com/Horus331/mass-flood-watch)', 'Accept': 'application/geo+json, application/json'}
D3_BOX = (128000.0, 856000.0, 206000.0, 946000.0)          # EPSG:26986, as proto/forecast.py
BOX_M = 20000.0; MAX_BOXES = 4
# NWS products that archive a storm (event names as api.weather.gov; VTEC phenomena.significance as IEM)
ALERT_EVENTS = tuple(s.strip() for s in os.environ.get('ARCHIVE_ALERT_EVENTS', 'Flash Flood Warning,Flood Advisory').split(','))
VTEC = {'FF.W': 'Flash Flood Warning', 'FA.Y': 'Flood Advisory', 'FL.Y': 'Flood Advisory', 'FA.W': 'Flood Warning', 'FL.W': 'Flood Warning'}
MERGE_H = 12          # a trigger whose evidence window starts within 12 h of an archived storm's evidence joins that storm
DUE_AFTER_H = 24      # radar run + labels once the evidence window has ended 24 h ago (twice-daily follow-up -> 24-36 h after the event)
BASELINE_ENV = dict(LF_PARITY='1', LF_LOSS='cn', LF_CN_AMC='II', LF_CN_SCALE='0.88', LF_INFIL_MMH='2', LF_QOUT='1', LF_VOUT='1', RES='20')
TZ = 'America/New_York'


def log(*a): print(*a, flush=True)


def utc(s):
    """ISO string / datetime -> naive UTC datetime."""
    if s is None: return None
    if isinstance(s, dt.datetime): d = s
    else:
        s = str(s).strip().replace(' ', 'T')
        if re.match(r'^\d{12}$', s): return dt.datetime.strptime(s, '%Y%m%d%H%M')
        if s.endswith('Z'): s = s[:-1] + '+00:00'
        if re.search(r'T\d\d$', s): s += ':00'
        d = dt.datetime.fromisoformat(s)
    return d.astimezone(dt.timezone.utc).replace(tzinfo=None) if d.tzinfo else d


def _utcnow(): return dt.datetime.now(dt.timezone.utc).replace(tzinfo=None, microsecond=0)


def iso(d): return None if d is None else d.strftime('%Y-%m-%dT%H:%MZ')


def now_utc(a=None): return utc(a.now) if a is not None and getattr(a, 'now', None) else _utcnow()


def local(d):
    from zoneinfo import ZoneInfo
    return d.replace(tzinfo=dt.timezone.utc).astimezone(ZoneInfo(TZ))


def jload(p, default=None):
    try: return json.load(open(p))
    except Exception: return default


def jsave(p, obj, indent=1):
    os.makedirs(os.path.dirname(os.path.abspath(p)), exist_ok=True)
    with open(p, 'w') as f: json.dump(obj, f, indent=indent, default=str); f.write('\n')


def get(url, params=None, tries=4, timeout=90, headers=None):
    import requests
    for k in range(tries):
        try:
            r = requests.get(url, params=params, headers=headers or UA, timeout=timeout)
            if r.status_code == 200: return r
            log('  HTTP', r.status_code, url[:120], (r.text or '')[:160].replace('\n', ' '))
            if r.status_code in (400, 404): return None
        except Exception as e: log('  error', url[:120], repr(e)[:160])
        time.sleep(4 * (k + 1))
    return None


# ------------------------------------------------------------------ District 3 geometry
_D3 = {}


def d3():
    """{'towns': [(name, shapely polygon lon/lat)], 'union': polygon} for the 73 District 3 towns (forecast.d3_towns)."""
    if not _D3:
        from shapely.geometry import Polygon
        from shapely.ops import unary_union
        import forecast as FC
        T = []
        for n, lab, rings in FC.d3_towns():
            ps = [Polygon(r).buffer(0) for r in rings if len(r) >= 3]
            T.append((n.title(), unary_union(ps)))
        _D3.update(towns=T, union=unary_union([p for _, p in T]))
    return _D3


def town_of(lon, lat):
    from shapely.geometry import Point
    p = Point(lon, lat)
    for n, g in d3()['towns']:
        if g.contains(p): return n
    return None


def to26986(lon, lat):
    from pyproj import Transformer
    if not hasattr(to26986, 'tr'): to26986.tr = Transformer.from_crs(4326, 26986, always_xy=True)
    return to26986.tr.transform(lon, lat)


def box_at(x, y):
    """20 x 20 km box centred on (x, y) EPSG:26986, snapped to 1 km and kept inside the District 3 box (as forecast.evaluate)."""
    half = BOX_M / 2; x0d, y0d, x1d, y1d = D3_BOX
    cx = min(max(round(x / 1000) * 1000, x0d + half), x1d - half); cy = min(max(round(y / 1000) * 1000, y0d + half), y1d - half)
    return [int(cx - half), int(cy - half), int(cx + half), int(cy + half)]


def overlap(a, b):
    w = max(0, min(a[2], b[2]) - max(a[0], b[0])); h = max(0, min(a[3], b[3]) - max(a[1], b[1]))
    return w * h / float((a[2] - a[0]) * (a[3] - a[1]))


def box_lonlat(b):
    from pyproj import Transformer
    tr = Transformer.from_crs(26986, 4326, always_xy=True); lo, la = tr.transform([b[0], b[2], b[0], b[2]], [b[1], b[1], b[3], b[3]])
    return [round(min(lo), 3), round(min(la), 3), round(max(lo), 3), round(max(la), 3)]


# ------------------------------------------------------------------ NWS alerts
def _d3_hit(geom_lonlat):
    """shapely geometry (lon/lat) -> (touches D3, [towns], representative point of the D3 part) ."""
    D = d3(); g = geom_lonlat.buffer(0)
    if not g.intersects(D['union']): return False, [], None
    part = g.intersection(D['union']); towns = sorted(n for n, t in D['towns'] if t.intersects(g) and t.intersection(g).area > 1e-7)
    rp = part.representative_point() if not part.is_empty else g.representative_point()
    return bool(towns) or part.area > 0, towns, (round(rp.x, 4), round(rp.y, 4))


def alerts_live(lookback_h=6.5, now=None):
    """api.weather.gov alerts for MA in force or sent in the last lookback_h hours, filtered to ALERT_EVENTS and District 3."""
    from shapely.geometry import shape
    from shapely.ops import unary_union
    now = now or _utcnow(); w0 = now - dt.timedelta(hours=lookback_h)
    feats, used = [], None
    for params in (dict(area='MA', start=iso(w0).replace('Z', ':00Z'), status='actual'), dict(area='MA', status='actual'), dict(area='MA')):
        r = get('https://api.weather.gov/alerts', params)
        if r is not None:
            feats = r.json().get('features', []); used = params; break
    rows, zone_cache = [], {}
    for f in feats:
        p = f.get('properties') or {}
        if p.get('event') not in ALERT_EVENTS: continue
        t0 = utc(p.get('onset') or p.get('effective') or p.get('sent')); t1 = utc(p.get('ends') or p.get('expires'))
        if t1 is not None and t1 < w0: continue
        if t0 is not None and t0 > now + dt.timedelta(hours=48): continue
        g = f.get('geometry')
        if g: geom = shape(g)
        else:                                            # zone-based alert: union of the affected zones' polygons
            parts = []
            for z in p.get('affectedZones') or []:
                if z not in zone_cache:
                    zr = get(z, tries=2); zone_cache[z] = shape(zr.json()['geometry']) if zr is not None and (zr.json().get('geometry')) else None
                if zone_cache[z] is not None: parts.append(zone_cache[z])
            if not parts: continue
            geom = unary_union(parts)
        hit, towns, rp = _d3_hit(geom)
        if not hit: continue
        rows.append(dict(id=p.get('id') or f.get('id'), event=p.get('event'), source='api.weather.gov', sent=iso(utc(p.get('sent'))), start=iso(t0), end=iso(t1),
                         area=p.get('areaDesc'), towns=towns, point=rp, polygon=bool(g), headline=(p.get('headline') or '')[:200],
                         vtec=((p.get('parameters') or {}).get('VTEC') or [''])[0], geometry=geom.simplify(0.002).__geo_interface__))
    return dict(source='api.weather.gov/alerts', query=used, window=[iso(w0), iso(now)], events=list(ALERT_EVENTS), n_ma=len(feats), alerts=rows)


def alerts_iem(w0, w1):
    """IEM archive of NWS storm-based warnings (polygons) from WFO BOX between w0 and w1 (UTC), filtered to ALERT_EVENTS and District 3."""
    from shapely.geometry import shape
    tries = [('https://mesonet.agron.iastate.edu/api/1/vtec/sbw_interval.geojson', dict(begints=iso(w0), endts=iso(w1), wfo='BOX')),
             ('https://mesonet.agron.iastate.edu/geojson/sbw.py', dict(sts=f'{w0:%Y%m%d%H%M}', ets=f'{w1:%Y%m%d%H%M}', wfos='BOX')),
             ('https://mesonet.agron.iastate.edu/geojson/sbw.geojson', dict(sts=f'{w0:%Y%m%d%H%M}', ets=f'{w1:%Y%m%d%H%M}', wfo='BOX'))]
    feats, used = None, None
    for u, prm in tries:
        r = get(u, prm, tries=2)
        if r is None: continue
        try: J = r.json()
        except Exception: continue
        if isinstance(J, dict) and 'features' in J: feats, used = J['features'], u; break
    if feats is None: raise RuntimeError('IEM storm-based warning archive unreachable')
    rows = []
    for f in feats:
        p = {k.lower(): v for k, v in (f.get('properties') or {}).items()}
        ph = (p.get('phenomena') or '').upper(); sg = (p.get('significance') or '').upper(); ev = VTEC.get(f'{ph}.{sg}')
        if ev not in ALERT_EVENTS or not f.get('geometry'): continue
        t0 = utc(p.get('polygon_begin') or p.get('issue') or p.get('utc_issue')); t1 = utc(p.get('polygon_end') or p.get('expire') or p.get('utc_expire'))
        if t1 and t1 < w0 or t0 and t0 > w1: continue
        geom = shape(f['geometry']); hit, towns, rp = _d3_hit(geom)
        if not hit: continue
        rows.append(dict(id=f"{p.get('wfo', 'BOX')}.{ph}.{sg}.{p.get('eventid')}.{t0:%Y%m%d%H%M}" if t0 else str(p.get('eventid')), event=ev, source='IEM sbw archive',
                         sent=iso(t0), start=iso(t0), end=iso(t1), area=p.get('status') or '', towns=towns, point=rp, polygon=True, headline=f'{ev} (VTEC {ph}.{sg} #{p.get("eventid")})',
                         vtec=f"{ph}.{sg}.{p.get('eventid')}", geometry=geom.simplify(0.002).__geo_interface__))
    # one row per warning (a warning's polygon may be updated several times: keep the first polygon, extend the end time)
    seen = {}
    for r in sorted(rows, key=lambda r: r['start'] or ''):
        k = (r['vtec'], (r['start'] or '')[:10])
        if k in seen: seen[k]['end'] = max(seen[k]['end'] or '', r['end'] or ''); seen[k]['towns'] = sorted(set(seen[k]['towns']) | set(r['towns']))
        else: seen[k] = r
    return dict(source='IEM storm-based warnings', query=used, window=[iso(w0), iso(w1)], events=list(ALERT_EVENTS), n_box=len(feats), alerts=list(seen.values()))


def cmd_alerts(a):
    try:
        if a.window:
            w0, w1 = (utc(s) for s in a.window.split('/')); A = alerts_iem(w0, w1)
        else: A = alerts_live(a.lookback_h, now_utc(a))
    except Exception as e:
        A = dict(error=repr(e)[:300], alerts=[]); log('alerts failed:', A['error'])
    jsave(a.out, A)
    log(f"NWS alerts touching District 3: {len(A['alerts'])} ({A.get('source')}, window {A.get('window')}); "
        + '; '.join(f"{x['event']} {x['start']}..{x['end']} {', '.join(x['towns'][:5])}" for x in A['alerts'][:6]))
    if a.github_output:
        with open(a.github_output, 'a') as f: f.write(f"nws={'true' if A['alerts'] else 'false'}\n")


# ------------------------------------------------------------------ archive (forecast.yml publish job)
def evidence(G, A):
    """Trigger evidence of one cycle -> dict(gate, alerts, start, end, boxes) or None when nothing triggers."""
    gate = bool(G.get('trigger')) and not G.get('forced')
    al = (A or {}).get('alerts') or []
    if not gate and not al: return None
    ts, te = [], []
    if gate:
        for b in G.get('boxes') or []:
            w = b.get('max6h_window') or []
            if len(w) == 2: ts.append(utc(w[0])); te.append(utc(w[1]))
        if not ts:
            w = G['district']['max6h_window']; ts.append(utc(w[0])); te.append(utc(w[1]))
    for x in al:
        if x.get('start'): ts.append(utc(x['start']))
        if x.get('end'): te.append(utc(x['end']))
    boxes = []
    if gate:
        for b in G.get('boxes') or []: boxes.append(dict(box=[int(v) for v in b['box']], source='gate ' + (b.get('member') or G['issued'][:13] + 'Z'), towns=b.get('towns', [])))
    for x in al:
        if not x.get('point'): continue
        bx = box_at(*to26986(*x['point']))
        boxes.append(dict(box=bx, source=f"NWS {x['event']} {x['start']}", towns=x.get('towns', [])))
    return dict(gate=gate, alerts=[{k: x[k] for k in ('id', 'event', 'start', 'end', 'towns', 'source')} for x in al], start=min(ts), end=max(te), boxes=boxes,
                towns_over=G.get('towns_over', []) if gate else [])


def merge_boxes(old, new):
    out = list(old)
    for b in new:
        if len(out) >= MAX_BOXES: break
        if all(overlap(b['box'], c['box']) <= 0.25 for c in out): out.append(dict(b))
    for i, b in enumerate(out): b['id'] = f'b{i + 1}'
    return out


def storms(root):
    out = []
    for p in sorted(glob.glob(os.path.join(root, '*_*', 'storm.json'))):
        S = jload(p)
        if S: S['_dir'] = os.path.dirname(p); out.append(S)
    return out


def window_of(S):
    """Radar-run window: 6 h before the evidence start to 12 h after its end (rain + drain-down), 24..48 h, whole hours."""
    t0 = utc(S['evidence']['start']).replace(minute=0) - dt.timedelta(hours=6)
    t1 = utc(S['evidence']['end']) + dt.timedelta(hours=12)
    h = int(np.clip(np.ceil((t1 - t0).total_seconds() / 3600), 24, 48))
    return dict(t0=f'{t0:%Y-%m-%dT%H}:00Z', hours=h)


def new_id(root, start):
    d = local(start).strftime('%Y%m%d'); sid = f'arc{d}'; taken = {S['id'] for S in storms(root)}; k = 0
    while sid in taken: k += 1; sid = f'arc{d}{chr(ord("a") + k)}'
    return sid, f'{d}_{sid}'


def kofn_rows(K, single_ok=True):
    rows = []
    for e in (K or {}).get('segments', []):
        n_mem = K.get('n_members', 1)
        cls = 'likely' if e['k'] >= 2 or (n_mem == 1 and e['k'] >= 1) else 'possible'
        rows.append(dict(segment=e['segment'], road=e.get('road', ''), town=e.get('town', ''), box=e.get('box') or '', k=e['k'], n=e.get('n', ''), n_members=n_mem,
                         p_max=e.get('p_max', ''), cls=cls, x=e.get('x', ''), y=e.get('y', '')))
    return rows


def write_csv(path, rows, cols):
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction='ignore'); w.writeheader(); w.writerows(rows)


def cmd_archive(a):
    G = jload(a.gate); A = jload(a.alerts, {}) if a.alerts else {}
    E = evidence(G, A)
    if E is None:
        log('archive: quiet cycle (gate not fired, no NWS flood alert in District 3): nothing archived'); return
    root = a.root; S = None; cyc = utc(G['issued'])
    for s in storms(root):
        es, ee = utc(s['evidence']['start']), utc(s['evidence']['end'])
        if E['start'] <= ee + dt.timedelta(hours=MERGE_H) and E['end'] >= es - dt.timedelta(hours=MERGE_H) and s['radar']['status'] in ('pending', 'failed'):
            S = s; break
    nowt = now_utc(a)
    if S is None:
        sid, folder = new_id(root, E['start'])
        S = dict(id=sid, folder=folder, created=iso(nowt), evidence=dict(start=iso(E['start']), end=iso(E['end'])), cycles=[], boxes=[],
                 radar=dict(status='pending', attempts=0, boxes={}), labels=dict(collected_at=None, checks=0, counts={}, stormevents_found=False), verify=None)
        S['_dir'] = os.path.join(root, folder); log('archive: new storm', sid)
    else:
        S['evidence'] = dict(start=iso(min(utc(S['evidence']['start']), E['start'])), end=iso(max(utc(S['evidence']['end']), E['end'])))
        log('archive: cycle joins storm', S['id'])
    S['boxes'] = merge_boxes(S['boxes'], E['boxes']); S['window'] = window_of(S); S['updated'] = iso(nowt)
    cdir = os.path.join(S['_dir'], 'forecast', f'{cyc:%Y%m%d%H}'); os.makedirs(cdir, exist_ok=True)
    shutil.copy(a.gate, os.path.join(cdir, 'gate.json'))
    if a.alerts and os.path.exists(a.alerts): shutil.copy(a.alerts, os.path.join(cdir, 'alerts.json'))
    St = jload(a.status) if a.status and os.path.exists(a.status) else None
    if St: jsave(os.path.join(cdir, 'status.json'), St, indent=None)
    K = jload(a.kofn) if a.kofn and os.path.exists(a.kofn) else None
    rows = kofn_rows(K)
    write_csv(os.path.join(cdir, 'kofn.csv'), rows, ['segment', 'road', 'town', 'box', 'k', 'n', 'n_members', 'p_max', 'cls', 'x', 'y'])
    if K: jsave(os.path.join(cdir, 'kofn_meta.json'), {k: v for k, v in K.items() if k != 'segments'})
    ent = dict(cycle=iso(cyc), gate=E['gate'], forced=bool(G.get('forced')), towns_over=E['towns_over'][:20], alerts=E['alerts'], state=(St or {}).get('state'),
               likely_closed=(St or {}).get('likely_closed'), possible=(St or {}).get('possible'), forecast_boxes=[b['box'] for b in G.get('boxes') or []] if G.get('trigger') else [],
               n_members=(K or {}).get('n_members'), dir=os.path.relpath(cdir, S['_dir']))
    S['cycles'] = [c for c in S['cycles'] if c['cycle'] != ent['cycle']] + [ent]; S['cycles'].sort(key=lambda c: c['cycle'])
    save_storm(S)
    open(a.flag or 'archived.txt', 'w').write(S['id'] + '\n')
    log(f"archived cycle {iso(cyc)} -> {S['_dir']} (gate {E['gate']}, {len(E['alerts'])} NWS alert(s), {len(rows)} k-of-n rows, boxes {[b['box'] for b in S['boxes']]}, "
        f"radar window {S['window']})")


def save_storm(S):
    d = S['_dir']; jsave(os.path.join(d, 'storm.json'), {k: v for k, v in S.items() if not k.startswith('_')})


def find_storm(root, sid):
    for S in storms(root):
        if S['id'] == sid: return S
    raise SystemExit(f'storm {sid} not in {root}')


# ------------------------------------------------------------------ follow-up planning
def cmd_due(a):
    nowt = now_utc(a); radar, labels = [], []
    for S in storms(a.root):
        if a.storm and S['id'] not in a.storm.split(','): continue
        end = utc(S['evidence']['end']); age = nowt - end; L = S.get('labels') or {}
        ready = age >= dt.timedelta(hours=DUE_AFTER_H) or bool(a.storm)
        if ready and (S['radar']['status'] == 'pending' or (S['radar']['status'] == 'failed' and S['radar'].get('attempts', 0) < 2) or a.force_radar):
            for b in S['boxes']:
                radar.append(dict(sid=S['id'], folder=S['folder'], id=b['id'], box=','.join(str(v) for v in b['box']), t0=S['window']['t0'], hours=str(S['window']['hours'])))
        last = utc(L.get('checked_at')) if L.get('checked_at') else None
        backfill = (not L.get('stormevents_found') and dt.timedelta(days=45) <= age <= dt.timedelta(days=200) and (last is None or nowt - last >= dt.timedelta(days=7)))
        if ready and (not L.get('collected_at') or backfill or any(r['sid'] == S['id'] for r in radar)): labels.append(S['id'])
    if a.max_jobs and len(radar) > a.max_jobs: radar = radar[:a.max_jobs]
    P = dict(made=iso(nowt), root=a.root, radar=radar, labels=labels)
    jsave(a.plan, P); log(f"due: {len(radar)} radar job(s) {[(r['sid'], r['id']) for r in radar]}, labels for {labels}")
    if a.github_output:
        with open(a.github_output, 'a') as f:
            f.write('radar=' + json.dumps(radar) + '\n'); f.write(f"any={'true' if (radar or labels) else 'false'}\n")


# ------------------------------------------------------------------ labels
COLS = ['id', 'name', 'road', 'town', 'type', 'time_local', 'time_quality', 'lon', 'lat', 'coord_quality', 'source_url', 'quote', 'source', 'quality']
ROAD_RE = re.compile(r"\b((?:(?:north|south|east|west|old|upper|lower|new)\s+)?(?:[a-z0-9'\.]+\s+){0,2}?(?:street|st|road|rd|avenue|ave|drive|dr|lane|ln|boulevard|blvd|"
                     r"highway|hwy|turnpike|tpke|parkway|pkwy|place|pl|way|court|ct|circle|terrace|pike)\b\.?|(?:route|rte|rt|interstate|i)[\s\-]*\d{1,3}[a-z]?\b|"
                     r"(?:us|state)\s+(?:route|highway)\s*\d{1,3})", re.I)
FLOOD_RE = re.compile(r'flood|washout|washed out|wash out|ponding|standing water|high water|water (on|in|across|over|covering) (the )?(road|street|roadway|lanes?)|'
                      r'impassable|sinkhole|culvert|storm ?drain|catch ?basin|stormwater|road closed due to water|submerged', re.I)
NOT_FLOOD = re.compile(r'water main|hydrant|sewer odor|ice\b|icing|frozen', re.I)


def ltype(t):
    t = (t or '').lower()
    if re.search(r'wash ?out|washed out|undermin|collapse', t): return 'washout'
    if 'sinkhole' in t: return 'sinkhole'
    if 'culvert' in t: return 'culvert_failure'
    if re.search(r'impassable|stranded|submerged', t): return 'impassable'
    if re.search(r'closed|closure|shut down', t): return 'closed'
    return 'flooded'


_SEG = {}


def seg_index():
    """Road vertices of docs/graph_segments.json (lon, lat, x, y, normalised name, town) for snapping a named road near a report point."""
    if not _SEG:
        import impacts as IM
        from prototype import norm_road
        S = json.load(open(os.path.join(ROOT, 'docs', 'graph_segments.json'))); P = S['props']; L = []
        for s, lo, la in IM.decode_segments(S):
            for x, y in zip(lo, la): L.append((s, x, y))
        A = np.array([(lo, la) for _, lo, la in L]); sg = np.array([s for s, _, _ in L])
        X, Y = to26986(A[:, 0], A[:, 1])
        _SEG.update(lon=A[:, 0], lat=A[:, 1], x=np.asarray(X), y=np.asarray(Y), seg=sg, name=np.array([norm_road(v) for v in P['road']], dtype=object), norm=norm_road)
    return _SEG


def snap(lon, lat, text, radius=4000.0):
    """-> (lon, lat, coord_quality, road).  A road named in the text that runs within `radius` of the report point: its vertex nearest the point
    ('approx', the labels_expand 'near' mode); otherwise the report point itself with coord_quality 'town'."""
    names = [m.group(1).strip() for m in ROAD_RE.finditer(text or '')]
    if not names: return lon, lat, 'town', ''
    S = seg_index(); x, y = to26986(lon, lat); d2 = (S['x'] - x) ** 2 + (S['y'] - y) ** 2; near = d2 < radius ** 2
    for n in names:
        w = n.split()
        for j in range(max(1, len(w) - 1)):          # 'over Main Street' -> 'Main Street': drop leading words the pattern took in
            sub = ' '.join(w[j:]); k = S['norm'](re.sub(r'^(?:route|rte|rt)[\s\-]*', 'rt ', sub.lower()))
            cand = np.nonzero(near & (S['name'][S['seg']] == k))[0]
            if len(cand):
                i = cand[np.argmin(d2[cand])]; return round(float(S['lon'][i]), 5), round(float(S['lat'][i]), 5), 'approx', sub.title()
    return lon, lat, 'town', names[0].title()


def storm_window(S, pad_h=12):
    t0 = utc(S['window']['t0']); return t0, t0 + dt.timedelta(hours=int(S['window']['hours']) + pad_h)


def lab_lsr(S, w0, w1):
    r = get('https://mesonet.agron.iastate.edu/cgi-bin/request/gis/lsr.py', dict(sts=iso(w0), ets=iso(w1), fmt='csv', states='MA'))
    if r is None: return [], dict(ok=False)
    rows = list(csv.DictReader(io.StringIO(r.text))); out = []
    for x in rows:
        tt = (x.get('TYPETEXT') or '').upper()
        if not ('FLOOD' in tt or 'HEAVY RAIN' in tt): continue
        rem = x.get('REMARK') or ''
        if 'HEAVY RAIN' in tt and not FLOOD_RE.search(rem): continue
        try: lon, lat = float(x['LON']), float(x['LAT'])
        except Exception: continue
        tw = town_of(lon, lat)
        if not tw: continue
        t = utc(x['VALID']); lo, la, cq, road = snap(lon, lat, rem)
        out.append(dict(name=f"{road or x.get('CITY', '').title()}: {tt.lower()}", road=road, town=tw, type=ltype(rem + ' ' + tt), time_local=local(t).strftime('%Y-%m-%dT%H:%M'),
                        time_quality='report', lon=lo, lat=la, coord_quality=cq,
                        source_url=f"https://mesonet.agron.iastate.edu/lsr/#BOX/{t - dt.timedelta(hours=1):%Y%m%d%H%M}/{t + dt.timedelta(hours=1):%Y%m%d%H%M}",
                        quote=rem[:300], source='LSR', quality='medium' if cq != 'town' else 'low'))
    return out, dict(ok=True, rows_ma=len(rows), kept=len(out), raw=rows)


def lab_stormevents(S, w0, w1):
    years = sorted({w0.year, w1.year}); out = []; found = False; meta = dict(ok=False)
    idx = get('https://www.ncei.noaa.gov/pub/data/swdi/stormevents/csvfiles/')
    if idx is None: return [], meta
    meta['ok'] = True
    for y in years:
        f = sorted(set(re.findall(rf'StormEvents_details-ftp_v1\.0_d{y}_c\d+\.csv\.gz', idx.text)))
        if not f: continue
        r = get('https://www.ncei.noaa.gov/pub/data/swdi/stormevents/csvfiles/' + f[-1], timeout=300)
        if r is None: continue
        rows = list(csv.DictReader(io.StringIO(gzip.decompress(r.content).decode('latin-1')))); meta[f'file_{y}'] = f[-1]
        for x in rows:
            if x['STATE'] != 'MASSACHUSETTS' or x['EVENT_TYPE'] not in ('Flash Flood', 'Flood', 'Heavy Rain'): continue
            try:
                tz = int(re.sub(r'[^\d\-]', '', x.get('CZ_TIMEZONE', 'EST-5').split('-')[-1]) or 5)
                t = dt.datetime.strptime(x['BEGIN_DATE_TIME'], '%d-%b-%y %H:%M:%S') + dt.timedelta(hours=tz)
            except Exception: continue
            if not (w0 - dt.timedelta(hours=6) <= t <= w1): continue
            found = True
            try: lon, lat = float(x['BEGIN_LON']), float(x['BEGIN_LAT'])
            except Exception: continue
            tw = town_of(lon, lat)
            if not tw: continue
            nar = (x.get('EVENT_NARRATIVE') or '').strip()
            for k, sent in enumerate([s for s in re.split(r'(?<=[\.;])\s+', nar) if FLOOD_RE.search(s) or ROAD_RE.search(s)] or [nar]):
                lo, la, cq, road = snap(lon, lat, sent)
                if cq == 'town' and lon == round(lon, 4) and len(str(x['BEGIN_LON']).split('.')[-1]) >= 4: cq = 'approx'     # Storm Events points carry 4 decimals: the reported place
                out.append(dict(name=f"{road or x.get('BEGIN_LOCATION', '').title()}: {x['EVENT_TYPE'].lower()}", road=road, town=tw, type=ltype(sent), time_local=local(t).strftime('%Y-%m-%dT%H:%M'),
                                time_quality='report', lon=lo, lat=la, coord_quality=cq, source_url=f"https://www.ncdc.noaa.gov/stormevents/eventdetails.jsp?id={x['EVENT_ID']}",
                                quote=sent[:300], source='StormEvents', quality='medium'))
    meta['events_in_window'] = found
    return out, meta


def lab_massdot(S, w0, w1):
    """MassDOT roadway-events log (proto/events_logger.py): events created in the window, in a District 3 town, with a flood / water cause."""
    out, n = [], 0; seen = set()
    for m in sorted({f'{w0:%Y-%m}', f'{w1:%Y-%m}'}):
        p = os.path.join(ROOT, 'docs', 'proto', 'obs', 'massdot_events', f'{m}.jsonl')
        if not os.path.exists(p): continue
        for line in open(p):
            try: e = json.loads(line)
            except Exception: continue
            n += 1; txt = ' '.join(str(e.get(k, '')) for k in ('EventType', 'EventSubType', 'LocationDescription', 'LaneBlockageDescription', 'EventDescription', 'Description', 'Cause'))
            if not FLOOD_RE.search(txt) or NOT_FLOOD.search(txt): continue
            try:
                t = utc(local_naive(e.get('EventCreatedDate') or e.get('EventStartDate'))); lon, lat = float(e['PrimaryLongitude']), float(e['PrimaryLatitude'])
            except Exception: continue
            if not (w0 - dt.timedelta(hours=6) <= t <= w1) or e.get('EventId') in seen: continue
            tw = town_of(lon, lat)
            if not tw: continue
            seen.add(e.get('EventId'))
            out.append(dict(name=f"{e.get('RoadwayName', '')}: {e.get('EventSubType') or e.get('EventType')}", road=e.get('RoadwayName', ''), town=tw, type=ltype(txt),
                            time_local=local(t).strftime('%Y-%m-%dT%H:%M'), time_quality='exact', lon=round(lon, 5), lat=round(lat, 5), coord_quality='exact',
                            source_url=f"massdot_events/{m}.jsonl#EventId={e.get('EventId')}", quote=(e.get('LocationDescription', '') + ' | ' + e.get('LaneBlockageDescription', ''))[:300],
                            source='MassDOT', quality='high'))
    return out, dict(ok=True, events_scanned=n, kept=len(out))


def local_naive(s):
    """MassDOT feed times are local wall-clock without an offset."""
    from zoneinfo import ZoneInfo
    d = dt.datetime.fromisoformat(str(s)[:19])
    return d.replace(tzinfo=ZoneInfo(TZ)) if d.tzinfo is None else d


def lab_scf(S, w0, w1):
    """SeeClickFix 311 issues created in the window (+24 h) inside the storm boxes, flood-like text, in a District 3 town."""
    out, n = [], 0; seen = set(); meta = dict(ok=False)
    for b in S['boxes']:
        lo0, la0, lo1, la1 = box_lonlat(b['box']); page = 1
        while page <= 30:
            r = get('https://seeclickfix.com/api/v2/issues', dict(min_lat=la0, min_lng=lo0, max_lat=la1, max_lng=lo1, after=w0.strftime('%Y-%m-%dT%H:%M:%SZ'),
                                                                  before=(w1 + dt.timedelta(hours=24)).strftime('%Y-%m-%dT%H:%M:%SZ'), per_page=100, page=page,
                                                                  status='open,acknowledged,closed,archived'), headers=dict(UA, Accept='application/json'), tries=3)
            if r is None: break
            meta['ok'] = True; J = r.json(); I = J.get('issues') or []
            for i in I:
                n += 1
                if i.get('id') in seen: continue
                seen.add(i.get('id')); rt = (i.get('request_type') or {}).get('title') or ''
                txt = f"{rt} {i.get('summary') or ''} {i.get('description') or ''}"
                if not FLOOD_RE.search(txt) or NOT_FLOOD.search(txt): continue
                try: lon, lat = float(i['lng']), float(i['lat'])
                except Exception: continue
                tw = town_of(lon, lat)
                if not tw: continue
                t = utc(i.get('created_at')); addr = i.get('address') or ''; road = (ROAD_RE.search(addr).group(1).title() if ROAD_RE.search(addr) else '')
                out.append(dict(name=f"{road or addr[:40]}: {(i.get('summary') or rt)[:60]}", road=road, town=tw, type=ltype(txt), time_local=local(t).strftime('%Y-%m-%dT%H:%M'),
                                time_quality='report', lon=round(lon, 5), lat=round(lat, 5), coord_quality='approx', source_url=i.get('html_url') or '',
                                quote=re.sub(r'\s+', ' ', (i.get('description') or i.get('summary') or ''))[:300], source='SeeClickFix', quality='low'))
            pg = (J.get('metadata') or {}).get('pagination') or {}
            if not pg.get('next_page') or not I: break
            page += 1; time.sleep(0.6)
    meta.update(issues_scanned=n, kept=len(out)); return out, meta


def cmd_labels(a):
    S = find_storm(a.root, a.storm); w0, w1 = storm_window(S); odir = os.path.join(S['_dir'], 'obs'); os.makedirs(odir, exist_ok=True)
    rows, meta = [], {}
    for name, fn in (('LSR', lab_lsr), ('StormEvents', lab_stormevents), ('MassDOT', lab_massdot), ('SeeClickFix', lab_scf)):
        try: R, M = fn(S, w0, w1)
        except Exception as e: R, M = [], dict(ok=False, error=repr(e)[:200])
        if name == 'LSR' and M.get('raw'):
            raw = M.pop('raw'); write_csv(os.path.join(odir, 'lsr.csv'), raw, list(raw[0].keys()))
        meta[name] = M; rows += R; log(f'labels {name}: {len(R)} row(s) {json.dumps(M)[:200]}')
    # Storm Events rows in the validate_points layout (obs/stormevents.csv) for proto/validate_points.py
    se = [r for r in rows if r['source'] == 'StormEvents']
    if se: write_csv(os.path.join(odir, 'stormevents.csv'), [dict(EVENT_ID=r['source_url'].rsplit('=', 1)[-1], EVENT_TYPE='Flash Flood', BEGIN_LAT=r['lat'], BEGIN_LON=r['lon'],
                                                                  BEGIN_DATE_TIME=r['time_local'], EVENT_NARRATIVE=r['quote']) for r in se],
                     ['EVENT_ID', 'EVENT_TYPE', 'BEGIN_LAT', 'BEGIN_LON', 'BEGIN_DATE_TIME', 'EVENT_NARRATIVE'])
    # duplicates: same source + road + town within 2 h keep the first
    rows.sort(key=lambda r: (r['time_local'], r['source'])); keep, seen = [], set()
    for r in rows:
        k = (r['source'], (r['road'] or '').lower(), r['town'], r['time_local'][:13], r['type'])
        if k in seen: continue
        seen.add(k); keep.append(r)
    pref = S['id'].upper()
    for i, r in enumerate(keep): r['id'] = f'{pref}-{i + 1:03d}'
    path = os.path.join(a.labels_dir, f"labels_{S['id']}_auto.csv"); write_csv(path, keep, COLS)
    # gauges for proto/score.py (USGS, the union of the boxes)
    try:
        import obs_fetch as OF
        bb = [min(box_lonlat(b['box'])[0] for b in S['boxes']), min(box_lonlat(b['box'])[1] for b in S['boxes']),
              max(box_lonlat(b['box'])[2] for b in S['boxes']), max(box_lonlat(b['box'])[3] for b in S['boxes'])]
        ds, de = local(w0 - dt.timedelta(hours=12)).strftime('%Y-%m-%d'), local(w1).strftime('%Y-%m-%d')
        Gg, used = OF.gauges(bb, ds, de); jsave(os.path.join(odir, 'gauges.json'), dict(bbox=bb, start=ds, end=de, gauges=list(Gg.values())), indent=None)
        meta['gauges'] = dict(n=len(Gg), via=used)
    except Exception as e: meta['gauges'] = dict(error=repr(e)[:200])
    L = S.get('labels') or {}; nowt = now_utc(a)
    L.update(collected_at=L.get('collected_at') or iso(nowt), checked_at=iso(nowt), checks=L.get('checks', 0) + 1, file=path.replace(os.sep, '/'),
             counts={k: sum(r['source'] == k for r in keep) for k in ('LSR', 'StormEvents', 'MassDOT', 'SeeClickFix')}, n=len(keep),
             stormevents_found=bool(meta.get('StormEvents', {}).get('events_in_window')), window=[iso(w0), iso(w1)],
             sources={k: {kk: vv for kk, vv in v.items() if kk != 'raw'} for k, v in meta.items()})
    S['labels'] = L; save_storm(S); log(f"labels -> {path}: {len(keep)} rows {L['counts']}")


# ------------------------------------------------------------------ radar run helpers
def cmd_segcsv(a):
    """prototype.py segments.geojson -> compact segments.csv (every segment with depth or a closure probability; no time series)."""
    g = json.load(open(a.src)); rows = []
    for f in g['features']:
        q = f['properties']
        if not (q.get('p_close') or q.get('p_may_close') or q.get('peak_depth_m')): continue
        rows.append(dict(segment=q['segment'], road=q.get('road') or '', town=q.get('town') or '', road_class=q.get('road_class') or '', p_close=q.get('p_close'),
                         p_may_close=q.get('p_may_close'), peak_depth_m=q.get('peak_depth_m'), length_m=q.get('length_m')))
    write_csv(a.dst, rows, ['segment', 'road', 'town', 'road_class', 'p_close', 'p_may_close', 'peak_depth_m', 'length_m']); log('segcsv', len(rows), 'rows ->', a.dst)


# ------------------------------------------------------------------ verification
_CENT = {}


def seg_centres():
    if not _CENT:
        import impacts as IM
        S = json.load(open(os.path.join(ROOT, 'docs', 'graph_segments.json'))); acc = {}
        for s, lo, la in IM.decode_segments(S): acc.setdefault(s, []).append((lo.mean(), la.mean()))
        ids = np.array(sorted(acc)); c = np.array([np.mean(acc[s], axis=0) for s in ids]); X, Y = to26986(c[:, 0], c[:, 1])
        _CENT.update(ids=ids, x=np.asarray(X), y=np.asarray(Y))
    return _CENT


def pseudo_run(d, box, pmap):
    """A minimal run folder score_v2.load_run can read: flood_meta.json (box, 20 m) + segments.geojson with properties only."""
    os.makedirs(d, exist_ok=True); jsave(os.path.join(d, 'flood_meta.json'), dict(box=[float(v) for v in box], res_m=20.0, shape=[int(round((box[3] - box[1]) / 20.0)), int(round((box[2] - box[0]) / 20.0))]))
    json.dump(dict(type='FeatureCollection', features=[dict(type='Feature', geometry=None, properties=dict(segment=int(s), p_close=float(p), p_may_close=0.0, peak_depth_m=float(dp)))
                                                        for s, (p, dp) in pmap.items()]), open(os.path.join(d, 'segments.geojson'), 'w'))
    return d


def contingency(F, R, box, nb=1000.0):
    """Segment sets F (forecast likely) and R (radar run flagged) inside box -> hits / misses / false alarms, POD, FAR, CSI; and the
    neighbourhood version (a forecast segment is a hit when a radar-flagged segment centre lies within nb m, a radar segment is caught when
    a forecast segment centre lies within nb m)."""
    C = seg_centres(); pos = {s: i for i, s in enumerate(C['ids'])}
    inb = lambda s: s in pos and box[0] <= C['x'][pos[s]] < box[2] and box[1] <= C['y'][pos[s]] < box[3]
    F = {s for s in F if inb(s)}; R = {s for s in R if inb(s)}
    H = len(F & R); M = len(R - F); FA = len(F - R)
    out = dict(forecast=len(F), radar=len(R), hits=H, misses=M, false_alarms=FA, pod=H / len(R) if R else None, far=FA / len(F) if F else None,
               csi=H / (H + M + FA) if (H + M + FA) else None)
    if F and R:
        from scipy.spatial import cKDTree
        fx = np.array([[C['x'][pos[s]], C['y'][pos[s]]] for s in F]); rx = np.array([[C['x'][pos[s]], C['y'][pos[s]]] for s in R])
        tf, tr = cKDTree(fx), cKDTree(rx)
        out['nb_m'] = nb; out['nb_pod'] = float(np.mean([bool(tf.query_ball_point(p, nb)) for p in rx])); out['nb_sr'] = float(np.mean([bool(tr.query_ball_point(p, nb)) for p in fx]))
    return out


def label_block(run_dir, storm, labels_dir):
    import score_v2 as SV
    SV.LABELS_DIR = os.path.abspath(labels_dir)
    try:
        r = SV.score_run(SV.load_run(run_dir, storm)); b = r['domains']['box']; ru = b['rule']
        return dict(labels_in_box=r['labels_in_box'], sites=b['n_sites'], flagged=ru['k'], share=round(ru['share'], 5), site_hits=ru['site_hits'], site_recall=ru['site_recall'],
                    chance_recall=ru['chance_recall'], lift=ru['lift'], csi_site=ru['csi']['csi_site'], fss300=(ru['fss'].get('300') or {}).get('fss'),
                    fss_useful=b['fss_useful'], recall_top3pct=b['shares'].get('0.03', {}).get('site_recall'))
    except Exception as e:
        return dict(error=repr(e)[:200])


def read_seg_csv(p):
    return {int(r['segment']): (float(r['p_close'] or 0), float(r['peak_depth_m'] or 0)) for r in csv.DictReader(open(p))} if os.path.exists(p) else None


def verify(S, labels_dir, tmp):
    rows = []
    for b in S['boxes']:
        rd = os.path.join(S['_dir'], 'radar', b['id']); R = read_seg_csv(os.path.join(rd, 'segments.csv'))
        if R is None: rows.append(dict(box=b['id'], error='no radar run')); continue
        Rset = {s for s, (p, _) in R.items() if p >= 0.5}
        radar_lab = label_block(pseudo_run(os.path.join(tmp, f"{S['id']}_radar_{b['id']}"), b['box'], R), S['id'], labels_dir)
        for c in S['cycles']:
            kp = os.path.join(S['_dir'], c['dir'], 'kofn.csv'); K = list(csv.DictReader(open(kp))) if os.path.exists(kp) else []
            Fset = {int(r['segment']) for r in K if r['cls'] == 'likely'}
            pm = {}
            for r in K:
                k, n = int(r['k']), int(r['n_members'] or 1)
                pm[int(r['segment'])] = (0.5 + 0.5 * (k - 1) / max(1, n) if r['cls'] == 'likely' else 0.25, 0.0)
            fl = label_block(pseudo_run(os.path.join(tmp, f"{S['id']}_fc{c['cycle'][:13]}_{b['id']}"), b['box'], pm), S['id'], labels_dir)
            lead = (utc(S['evidence']['start']) - utc(c['cycle'])).total_seconds() / 3600
            rows.append(dict(box=b['id'], box_26986=b['box'], cycle=c['cycle'], lead_h=round(lead, 1), gate=c['gate'], n_members=c.get('n_members'),
                             box_in_forecast=any(overlap(b['box'], fb) > 0.25 for fb in c.get('forecast_boxes') or []),
                             vs_radar=contingency(Fset, Rset, b['box']), forecast_vs_labels=fl, radar_vs_labels=radar_lab))
    return dict(storm=S['id'], made=iso(_utcnow()), labels=S.get('labels', {}).get('counts'),
                note=('forecast = archived cycle, likely closed (k >= 2 of the time-lagged members; P >= 0.5 for a single run); radar = the same box run with '
                      'observed MRMS rain at the frozen BASELINE.md settings, flagged at P(close) >= 0.5; labels scored with proto/score_v2.py (box domain, '
                      'strict 30 m matches, sites clustered at 150 m). Auto labels are unreviewed.'), rows=rows)


def cmd_verify(a):
    import tempfile
    S = find_storm(a.root, a.storm); V = verify(S, a.labels_dir, tempfile.mkdtemp())
    jsave(os.path.join(S['_dir'], 'verify.json'), V); S['verify'] = dict(at=V['made'], rows=len(V['rows'])); save_storm(S)
    for r in V['rows']: log('verify', r.get('box'), r.get('cycle'), json.dumps(r.get('vs_radar'))[:200], json.dumps(r.get('forecast_vs_labels'))[:160])


def cmd_finalize(a):
    """After the follow-up jobs: radar outputs present -> storm.json radar status; verify every storm touched; rebuild the index."""
    P = jload(a.plan, {}); touched = set(P.get('labels', []))
    for sid in sorted({r['sid'] for r in P.get('radar', [])}):
        S = find_storm(a.root, sid); want = [r['id'] for r in P['radar'] if r['sid'] == sid]; st = S['radar']; st['attempts'] = st.get('attempts', 0) + 1
        for bid in want:
            rd = os.path.join(S['_dir'], 'radar', bid); st['boxes'][bid] = 'done' if os.path.exists(os.path.join(rd, 'segments.csv')) else 'failed'
        st['status'] = 'done' if all(st['boxes'].get(b['id']) == 'done' for b in S['boxes']) else 'failed'; st['at'] = iso(_utcnow())
        st['settings'] = dict(BASELINE_ENV, rain='MRMS MultiSensor QPE 01H Pass2', t0=S['window']['t0'], hours=S['window']['hours'], basis='docs/proto/parity/BASELINE.md')
        save_storm(S); touched.add(sid); log('radar', sid, st['status'], st['boxes'])
    for sid in sorted(touched):
        S = find_storm(a.root, sid)
        if any(os.path.exists(os.path.join(S['_dir'], 'radar', b['id'], 'segments.csv')) for b in S['boxes']):
            a.storm = sid; cmd_verify(a)
    cmd_index(a)


# ------------------------------------------------------------------ index, skill, catalogue candidates
def _f(v, nd=2):
    return '-' if v is None else (f'{v:.{nd}f}' if isinstance(v, float) else str(v))


def cmd_index(a):
    root = a.root; SS = storms(root); skill = []; cand = []
    lines = ['# Storm archive index', '', 'Generated by `proto/storm_archive.py index` (README.md explains the archive). One row per archived storm; '
             'forecast skill rows accumulate in `skill.json`.', '',
             '| storm | evidence (UTC) | trigger | cycles | boxes | radar run | labels (LSR / SE / MassDOT / SCF) | verified |', '|' + ' --- |' * 8]
    for S in SS:
        L = S.get('labels') or {}; c = L.get('counts') or {}
        trig = ', '.join(sorted({'gate' for x in S['cycles'] if x['gate']} | {'NWS ' + al['event'] for x in S['cycles'] for al in x['alerts']}))
        lines.append(f"| [{S['id']}]({S['folder']}/storm.json) | {S['evidence']['start']} .. {S['evidence']['end']} | {trig} | {len(S['cycles'])} | {len(S['boxes'])} | "
                     f"{S['radar']['status']} | {c.get('LSR', '-')} / {c.get('StormEvents', '-')} / {c.get('MassDOT', '-')} / {c.get('SeeClickFix', '-')} | "
                     f"{'yes' if S.get('verify') else 'no'} |")
        V = jload(os.path.join(S['_dir'], 'verify.json'))
        for r in (V or {}).get('rows', []):
            if 'vs_radar' in r: skill.append(dict(storm=S['id'], **{k: r[k] for k in ('box', 'cycle', 'lead_h', 'gate', 'n_members', 'box_in_forecast', 'vs_radar', 'forecast_vs_labels', 'radar_vs_labels')}))
        if L.get('n'):
            boxes = [b['box'] for b in S['boxes']]; bb = [box_lonlat(b) for b in boxes]
            cand.append(dict(id=S['id'], area=(S['boxes'][0].get('towns') or ['district3'])[0].lower() if S['boxes'] else 'district3',
                             date_local=local(utc(S['evidence']['start'])).strftime('%Y-%m-%d'), t0=S['window']['t0'], hours=S['window']['hours'],
                             box_26986=boxes[0] if boxes else None, boxes_26986=boxes, bbox_lonlat=[min(b[0] for b in bb), min(b[1] for b in bb), max(b[2] for b in bb), max(b[3] for b in bb)] if bb else None,
                             towns=sorted({t for b in S['boxes'] for t in b.get('towns', [])})[:12], labels=L.get('file'), label_counts=c, era='aws', selected=False,
                             archive=f"{root}/{S['folder']}".replace(os.sep, '/'), radar=S['radar']['status'],
                             note='auto-archived storm; labels unreviewed (quality column); review before adding to docs/proto/obs/catalog.json'))
    # pooled skill (latest cycle per storm and box = the shortest lead; and all cycles)
    def pool(rows):
        H = sum(r['vs_radar']['hits'] for r in rows); M = sum(r['vs_radar']['misses'] for r in rows); FA = sum(r['vs_radar']['false_alarms'] for r in rows)
        fs = sum((r['forecast_vs_labels'].get('site_hits') or 0) for r in rows); rs = sum((r['radar_vs_labels'].get('site_hits') or 0) for r in rows)
        ns = sum((r['radar_vs_labels'].get('sites') or 0) for r in rows)
        return dict(rows=len(rows), hits=H, misses=M, false_alarms=FA, csi=H / (H + M + FA) if H + M + FA else None, pod=H / (H + M) if H + M else None,
                    far=FA / (H + FA) if H + FA else None, label_sites=ns, forecast_site_hits=fs, radar_site_hits=rs)
    last = {}
    for r in skill:
        k = (r['storm'], r['box'])
        if k not in last or r['cycle'] > last[k]['cycle']: last[k] = r
    P = dict(all_cycles=pool(skill), latest_cycle=pool(list(last.values())))
    lines += ['', '## Forecast skill (accumulated)', '',
              'Forecast "likely closed" segments vs the radar-driven run (segment level, inside each radar box) and vs the auto labels (score_v2 sites hit).', '',
              '| pool | rows | hits | misses | false alarms | POD | FAR | CSI | label sites | sites hit: forecast / radar |', '|' + ' --- |' * 10]
    for k, v in P.items():
        lines.append(f"| {k.replace('_', ' ')} | {v['rows']} | {v['hits']} | {v['misses']} | {v['false_alarms']} | {_f(v['pod'])} | {_f(v['far'])} | {_f(v['csi'])} | "
                     f"{v['label_sites']} | {_f(v['forecast_site_hits'], 0)} / {_f(v['radar_site_hits'], 0)} |")
    lines += ['', '| storm | box | cycle | lead (h) | gate | forecast / radar flagged | hits | CSI | 1 km POD / SR | sites | forecast hits | radar hits |', '|' + ' --- |' * 12]
    for r in skill:
        v = r['vs_radar']; fl = r['forecast_vs_labels']; rl = r['radar_vs_labels']
        lines.append(f"| {r['storm']} | {r['box']} | {r['cycle']} | {r['lead_h']} | {'fired' if r['gate'] else 'quiet'} | {v['forecast']} / {v['radar']} | {v['hits']} | {_f(v['csi'])} | "
                     f"{_f(v.get('nb_pod'))} / {_f(v.get('nb_sr'))} | {_f(rl.get('sites'))} | {_f(fl.get('site_hits'), 0)} | {_f(rl.get('site_hits'), 0)} |")
    os.makedirs(root, exist_ok=True)
    open(os.path.join(root, 'ARCHIVE.md'), 'w').write('\n'.join(lines) + '\n')
    jsave(os.path.join(root, 'skill.json'), dict(made=iso(_utcnow()), pooled=P, rows=skill))
    jsave(os.path.join(root, 'catalog_candidates.json'), dict(about='Auto-archived District 3 storms proposed for docs/proto/obs/catalog.json (same fields). '
                                                                 'Not added automatically: review the labels first.', events=cand))
    log(f'index: {len(SS)} storm(s), {len(skill)} skill row(s), {len(cand)} candidate(s) -> {root}/ARCHIVE.md')


# ------------------------------------------------------------------ selftest (offline)
def selftest():
    import tempfile
    root = tempfile.mkdtemp()
    G = dict(issued='2023-09-11T12:00Z', trigger=True, forced=False, towns_over=['Leominster'], district=dict(max6h_window=['2023-09-11T18:00Z', '2023-09-12T00:00Z']),
             boxes=[dict(id='b1', box=[168000, 908000, 188000, 928000], max6h_window=['2023-09-11T18:00Z', '2023-09-12T00:00Z'], towns=['Leominster'])])
    A = dict(alerts=[dict(id='x', event='Flash Flood Warning', start='2023-09-11T20:00Z', end='2023-09-12T02:00Z', towns=['Worcester'], point=(-71.80, 42.27), source='t')])
    E = evidence(G, A); assert E['gate'] and len(E['boxes']) == 2 and E['end'] == utc('2023-09-12T02:00Z'), E
    assert evidence(dict(G, trigger=False), {}) is None and evidence(dict(G, trigger=True, forced=True), {}) is None
    gp, ap_ = os.path.join(root, 'g.json'), os.path.join(root, 'a.json'); jsave(gp, G); jsave(ap_, A)
    K = dict(n_members=8, segments=[dict(segment=10, road='A', town='T', box='b1', k=3, n=8, p_max=0.9, x=1, y=2), dict(segment=11, road='B', town='T', box='b1', k=1, n=8, p_max=0.6, x=1, y=2)])
    kp = os.path.join(root, 'k.json'); jsave(kp, K)
    ns = argparse.Namespace(gate=gp, alerts=ap_, status=None, kofn=kp, root=os.path.join(root, 'arch'), now='2023-09-11T14:00Z', flag=os.path.join(root, 'f.txt'))
    cmd_archive(ns); SS = storms(ns.root); assert len(SS) == 1 and SS[0]['id'] == 'arc20230911' and len(SS[0]['boxes']) == 2, SS
    G2 = dict(G, issued='2023-09-11T18:00Z'); jsave(gp, G2); cmd_archive(ns); SS = storms(ns.root)
    assert len(SS) == 1 and len(SS[0]['cycles']) == 2 and SS[0]['window']['t0'] == '2023-09-11T12:00Z', SS[0]['window']
    rows = list(csv.DictReader(open(os.path.join(SS[0]['_dir'], 'forecast', '2023091118', 'kofn.csv')))); assert [r['cls'] for r in rows] == ['likely', 'possible'], rows
    pl = os.path.join(root, 'plan.json')
    cmd_due(argparse.Namespace(root=ns.root, now='2023-09-12T12:00Z', storm=None, plan=pl, github_output=None, max_jobs=0, force_radar=False)); assert not jload(pl)['radar']
    cmd_due(argparse.Namespace(root=ns.root, now='2023-09-13T03:00Z', storm=None, plan=pl, github_output=None, max_jobs=0, force_radar=False))
    P = jload(pl); assert len(P['radar']) == 2 and P['labels'] == ['arc20230911'], P
    G3 = dict(G, issued='2023-09-20T12:00Z', boxes=[dict(G['boxes'][0], max6h_window=['2023-09-20T18:00Z', '2023-09-21T00:00Z'])]); jsave(gp, G3); jsave(ap_, {})
    cmd_archive(ns); assert len(storms(ns.root)) == 2
    assert ltype('Road washed out') == 'washout' and ltype('Main St impassable') == 'impassable' and ltype('street flooding') == 'flooded'
    assert box_at(0, 0)[0] == D3_BOX[0] and overlap([0, 0, 2, 2], [1, 0, 3, 2]) == 0.5
    c = contingency({1, 2}, {2, 3}, [-1e9, -1e9, 1e9, 1e9]); assert c['hits'] == 1 and c['misses'] == 1 and c['false_alarms'] == 1 and abs(c['csi'] - 1 / 3) < 1e-9, c
    cmd_index(argparse.Namespace(root=ns.root)); assert os.path.exists(os.path.join(ns.root, 'ARCHIVE.md'))
    print('storm_archive selftest ok')


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0]); sp = ap.add_subparsers(dest='cmd', required=True)
    p = sp.add_parser('alerts'); p.add_argument('--out', required=True); p.add_argument('--window'); p.add_argument('--lookback-h', type=float, default=6.5)
    p.add_argument('--now'); p.add_argument('--github-output')
    p = sp.add_parser('archive'); p.add_argument('--gate', required=True); p.add_argument('--alerts'); p.add_argument('--status'); p.add_argument('--kofn')
    p.add_argument('--root', default=ARCHIVE); p.add_argument('--now'); p.add_argument('--flag', default='archived.txt')
    p = sp.add_parser('due'); p.add_argument('--root', default=ARCHIVE); p.add_argument('--now'); p.add_argument('--storm'); p.add_argument('--plan', required=True)
    p.add_argument('--github-output'); p.add_argument('--max-jobs', type=int, default=8); p.add_argument('--force-radar', action='store_true')
    p = sp.add_parser('labels'); p.add_argument('--storm', required=True); p.add_argument('--root', default=ARCHIVE); p.add_argument('--labels-dir', default=LABELS_DIR); p.add_argument('--now')
    p = sp.add_parser('segcsv'); p.add_argument('src'); p.add_argument('dst')
    p = sp.add_parser('finalize'); p.add_argument('--plan', required=True); p.add_argument('--root', default=ARCHIVE); p.add_argument('--labels-dir', default=LABELS_DIR)
    p = sp.add_parser('verify'); p.add_argument('--storm', required=True); p.add_argument('--root', default=ARCHIVE); p.add_argument('--labels-dir', default=LABELS_DIR)
    p = sp.add_parser('index'); p.add_argument('--root', default=ARCHIVE)
    sp.add_parser('selftest')
    a = ap.parse_args()
    dict(alerts=cmd_alerts, archive=cmd_archive, due=cmd_due, labels=cmd_labels, segcsv=cmd_segcsv, finalize=cmd_finalize, verify=cmd_verify, index=cmd_index,
         selftest=lambda a: selftest())[a.cmd](a)
