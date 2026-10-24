"""Network side of label round 2 (docs/proto/obs/LABELS_ROUND2.md); run on GitHub Actions (.github/workflows/labels_round2.yml).
The sandbox proxy blocks wx1box.org, gis.crashdata.dot.mass.gov and S3, so every fetch lives here and commits small text/CSV/JSON.

    python proto/labels_round2_fetch.py wx1box       # WX1BOX SKYWARN storm-report PDFs for catalogue dates -> docs/proto/obs/round2/wx1box/*.txt
    python proto/labels_round2_fetch.py crash        # MassDOT IMPACT crashes, road surface 'Water (standing or moving)' -> round2/crash_water_d3.csv
    python proto/labels_round2_fetch.py flash        # MRMS FLASH archive check (AWS noaa-mrms-pds; IEM mtarchive for pre-Oct-2020) -> round2/mrms_flash_check.json

Locked storms (PROTOCOL.md §2) are skipped everywhere: their dates are never queried.
"""
import os, sys, re, csv, json, subprocess, datetime as dt
import requests

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, 'docs', 'proto', 'obs', 'round2'); os.makedirs(OUT, exist_ok=True)
LOCKED = ('aug2015', 'aug2018', 'aug2020', 'jul2018', 'oct2016')
UA = {'User-Agent': 'mass-flood-watch research (github.com/Horus331/mass-flood-watch)'}


def storms():
    C = json.load(open(os.path.join(ROOT, 'docs', 'proto', 'obs', 'catalog.json')))['events']
    return [e for e in C if e['id'] not in LOCKED]


def days(e):
    t0 = dt.datetime.strptime(e['t0'], '%Y-%m-%dT%H:00Z'); t1 = t0 + dt.timedelta(hours=int(e['hours']))
    d = (t0 - dt.timedelta(hours=4)).date(); out = []
    while d <= (t1 - dt.timedelta(hours=4)).date(): out.append(d); d += dt.timedelta(days=1)
    return out


# ------------------------------------------------------------------------------------------------ WX1BOX
LOG = []


def wx1box():
    """Storm-report compilations are WordPress uploads named reports_<M>_<D>_<YY>.pdf.  Candidates come from the WP media REST listing
    (search 'reports') plus guessed upload paths (storm month and the next month); only files whose name date is a catalogue day are kept."""
    want = {}
    for e in storms():
        for d in days(e): want[f'{d.month}_{d.day}_{d:%y}'] = (e['id'], d)
    found = {}
    for page in range(1, 40):
        try:
            r = requests.get('https://wx1box.org/wp-json/wp/v2/media', params=dict(search='reports', per_page=100, page=page), headers=UA, timeout=60)
        except Exception as ex: LOG.append(f'media listing error {ex!r}'[:300]); break
        LOG.append(f'media page {page}: HTTP {r.status_code}, {len(r.content)} bytes')
        if r.status_code != 200: print('media listing', page, r.status_code, r.text[:200]); break
        J = r.json()
        if not J: break
        for m in J:
            u = m.get('source_url', ''); n = os.path.basename(u)
            mm = re.match(r'reports_(\d+_\d+_\d\d)\.pdf$', n, re.I)
            if mm and mm.group(1) in want: found[n] = u
        if len(J) < 100: break
    print('media listing matched', len(found))
    for k, (sid, d) in want.items():
        n = f'reports_{k}.pdf'
        if n in found: continue
        for y, m in {(d.year, d.month), ((d.replace(day=28) + dt.timedelta(days=5)).year, (d.replace(day=28) + dt.timedelta(days=5)).month)}:
            u = f'https://wx1box.org/wp-content/uploads/{y}/{m:02d}/{n}'
            try:
                sc = requests.head(u, headers=UA, timeout=30, allow_redirects=True).status_code; LOG.append(f'HEAD {u} {sc}')
                if sc == 200: found[n] = u; break
            except Exception as ex: LOG.append(f'HEAD {u} {ex!r}'[:300])
    D = os.path.join(OUT, 'wx1box'); os.makedirs(D, exist_ok=True); idx = []
    for n, u in sorted(found.items()):
        k = re.match(r'reports_(\d+_\d+_\d\d)', n).group(1); sid, d = want[k]
        try: r = requests.get(u, headers=UA, timeout=120)
        except Exception as ex: idx.append(dict(storm=sid, date=str(d), url=u, status=repr(ex)[:200])); continue
        if r.status_code != 200: idx.append(dict(storm=sid, date=str(d), url=u, status=r.status_code)); continue
        pdf = os.path.join('/tmp', n); open(pdf, 'wb').write(r.content)
        txt = os.path.join(D, n.replace('.pdf', '.txt'))
        subprocess.run(['pdftotext', '-layout', pdf, txt], check=False)
        idx.append(dict(storm=sid, date=str(d), url=u, status=200, bytes=len(r.content), txt=os.path.relpath(txt, ROOT)))
    for k, (sid, d) in sorted(want.items(), key=lambda x: x[1][1]):
        if f'reports_{k}.pdf' not in found: idx.append(dict(storm=sid, date=str(d), url=None, status='not found'))
    json.dump(dict(index=idx, log=LOG), open(os.path.join(D, 'index.json'), 'w'), indent=1)
    print(json.dumps(idx, indent=0))


# ------------------------------------------------------------------------------------------------ MassDOT crashes
CRASH_BASE = 'https://gis.crashdata.dot.mass.gov/arcgis/rest/services'
FIELDS = ['CRASH_NUMB', 'CITY_TOWN_NAME', 'CRASH_DATE_TEXT', 'CRASH_TIME_2', 'CRASH_HOUR', 'CRASH_SEVERITY_DESCR', 'NUMB_VEHC', 'MANR_COLL_DESCR',
          'WEATH_COND_DESCR', 'ROAD_SURF_COND_DESCR', 'AMBNT_LIGHT_DESCR', 'RDWY', 'STREET_NUMB', 'NEAR_INT_RDWY', 'DIST_DIRC_FROM_INT', 'MILEMARKER', 'EXIT_NUMB',
          'LANDMARK', 'FIRST_HRMF_EVENT_DESCR', 'IS_GEOCODED', 'GEOCODING_METHOD_NAME', 'X', 'Y', 'LAT', 'LON', 'DISTRICT_NUM', 'YEAR']
D3X = (118000.0, 846000.0, 216000.0, 956000.0)      # D3_BOX of labels_expand.py plus 10 km (the catalogue boxes reach x = 213 km)


def _j(u, **p):
    p.setdefault('f', 'json'); r = requests.get(u, params=p, headers=UA, timeout=180); r.raise_for_status(); return r.json()


def crash():
    svcs, allsv = [], []
    root = _j(CRASH_BASE); folders = [''] + root.get('folders', [])
    for folder in folders:
        try: J = root if not folder else _j(f'{CRASH_BASE}/{folder}')
        except Exception as ex: print('list', folder, ex); continue
        allsv += [s['name'] + ':' + s['type'] for s in J.get('services', [])]
        svcs += [s for s in J.get('services', []) if re.search(r'ODP|CRASH', s['name'], re.I) and s['type'] in ('FeatureServer', 'MapServer')]
    print('ODP services', [(s['name'], s['type']) for s in svcs])
    log = dict(services=[s['name'] + ':' + s['type'] for s in svcs], all_services=allsv, years={}); rows = []
    for y in range(2018, 2027):
        cand = sorted([s for s in svcs if str(y) in s['name'] and 'OPEN' in s['name'].upper()], key=lambda s: s['type'] != 'FeatureServer') or \
               sorted([s for s in svcs if str(y) in s['name']], key=lambda s: s['type'] != 'FeatureServer')
        if not cand: log['years'][y] = 'no service'; continue
        s = cand[0]; u = f"{CRASH_BASE}/{s['name']}/{s['type']}"
        try:
            L = _j(u)['layers']; lay = next((l for l in L if l['name'].lower().startswith('crash')), L[0])
            q = f"{u}/{lay['id']}/query"
            vals = _j(q, where='1=1', outFields='ROAD_SURF_COND_DESCR', returnDistinctValues='true', returnGeometry='false')
            dv = sorted({f['attributes']['ROAD_SURF_COND_DESCR'] or '' for f in vals.get('features', [])})
            wv = [v for v in dv if 'water' in v.lower()]
            where = ' OR '.join(f"ROAD_SURF_COND_DESCR = '{v}'" for v in wv) or "ROAD_SURF_COND_DESCR LIKE '%Water%'"
            n_all, off, got = 0, 0, []
            while True:
                J = _j(q, where=where, outFields=','.join(FIELDS), returnGeometry='false', resultOffset=off, resultRecordCount=2000, orderByFields='OBJECTID')
                F = [f['attributes'] for f in J.get('features', [])]; got += F; off += len(F)
                if not F or not J.get('exceededTransferLimit'): break
            n_all = len(got)
            for a in got:
                try: x, yy = float(a['X']), float(a['Y'])
                except (TypeError, ValueError): x = yy = None
                if a.get('DISTRICT_NUM') in (3, '3') or (x is not None and D3X[0] <= x < D3X[2] and D3X[1] <= yy < D3X[3]): rows.append(a)
            log['years'][y] = dict(service=s['name'], layer=lay['name'], surface_values=dv, water_values=wv, statewide=n_all,
                                   kept=sum(1 for r in rows if str(r.get('YEAR')) == str(y) or (r.get('CRASH_DATE_TEXT') or '').endswith(str(y))))
        except Exception as ex: log['years'][y] = f'error {ex!r}'[:300]
        print(y, log['years'][y] if isinstance(log['years'][y], str) else {k: v for k, v in log['years'][y].items() if k != 'surface_values'})
    with open(os.path.join(OUT, 'crash_water_d3.csv'), 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=FIELDS, extrasaction='ignore'); w.writeheader(); w.writerows(rows)
    log['rows'] = len(rows); log['source'] = CRASH_BASE; log['fetched'] = dt.datetime.utcnow().strftime('%Y-%m-%dT%H:%MZ')
    json.dump(log, open(os.path.join(OUT, 'crash_water_fetch.json'), 'w'), indent=1); print('rows', len(rows))


# ------------------------------------------------------------------------------------------------ MRMS FLASH archive check
S3 = 'https://noaa-mrms-pds.s3.amazonaws.com'


def s3_list(prefix, delim=None):
    import xml.etree.ElementTree as ET
    out, pre, tok = [], [], None
    while True:
        p = {'list-type': '2', 'prefix': prefix}
        if delim: p['delimiter'] = delim
        if tok: p['continuation-token'] = tok
        r = requests.get(S3 + '/', params=p, timeout=120); r.raise_for_status()   # noqa
        X = ET.fromstring(r.content); ns = {'s': X.tag.split('}')[0].strip('{')}
        out += [c.find('s:Key', ns).text for c in X.findall('s:Contents', ns)]
        pre += [c.find('s:Prefix', ns).text for c in X.findall('s:CommonPrefixes', ns)]
        t = X.find('s:NextContinuationToken', ns)
        if t is None: break
        tok = t.text
    return out, pre


def flash():
    _, P = s3_list('CONUS/', '/'); fl = sorted(p.split('/')[1] for p in P if 'FLASH' in p.upper())
    print('AWS FLASH prefixes', fl)
    res = dict(aws_flash_products=fl, storms={})
    for e in storms():
        t0 = dt.datetime.strptime(e['t0'], '%Y-%m-%dT%H:00Z'); t1 = t0 + dt.timedelta(hours=int(e['hours']))
        dd = sorted({(t0 + dt.timedelta(hours=h)).date() for h in range(int(e['hours']) + 1)}); R = {}
        for p in fl:
            n = 0; first = last = None
            for d in dd:
                K, _ = s3_list(f'CONUS/{p}/{d:%Y%m%d}/')
                for k in K:
                    m = re.search(r'_(\d{8}-\d{6})\.grib2', k)
                    if not m: continue
                    t = dt.datetime.strptime(m.group(1), '%Y%m%d-%H%M%S')
                    if t0 <= t <= t1: n += 1; first = first or k; last = k
            R[p] = dict(n_in_window=n, first=first, last=last)
        if e.get('era') == 'iem':      # pre-Oct-2020: AWS bucket starts later; check the IEM mtarchive mirror
            I = {}
            try:
                txt = requests.get(f'https://mtarchive.geol.iastate.edu/{t0:%Y/%m/%d}/mrms/ncep/', timeout=60).text
                I = dict(flash_dirs=sorted(set(x.strip('/') for x in re.findall(r'href="(FLASH[^"]+)"', txt))))
            except Exception as ex: I = dict(error=repr(ex)[:200])
            R['_iem'] = I
        res['storms'][e['id']] = dict(era=e.get('era'), t0=e['t0'], hours=e['hours'], products=R)
        print(e['id'], {k: v['n_in_window'] if 'n_in_window' in v else v for k, v in R.items()})
    json.dump(res, open(os.path.join(OUT, 'mrms_flash_check.json'), 'w'), indent=1)


if __name__ == '__main__':
    dict(wx1box=wx1box, crash=crash, flash=flash)[sys.argv[1]]()
