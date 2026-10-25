"""Network side of label round 3 (docs/proto/obs/LABELS_ROUND3.md): SeeClickFix 311 issues for District 3.  Run on GitHub Actions
(.github/workflows/scf_fetch.yml); the sandbox proxy blocks seeclickfix.com.  Writes small JSON / CSV to docs/proto/obs/round3/.

    python proto/scf_fetch.py types      # request types offered across D3 (grid of points, /api/v2/issues/new) -> round3/scf_request_types.json
    python proto/scf_fetch.py windows    # every issue (all types) inside each non-locked catalogue storm box and window -> round3/scf_window_<storm>.json
    python proto/scf_fetch.py d3         # flood-type issues 2018-01-01 .. today, D3 box (request-type ids + text search) -> round3/scf_flood_d3.csv
    python proto/scf_fetch.py all

Window = t0 .. t0 + hours + 24 h (UTC).  Locked storms (PROTOCOL.md §2) are never queried, and the D3-wide list drops issues created within
+/- 1 day of a locked storm's window before anything is written.
"""
import os, sys, re, csv, json, time, datetime as dt
import requests

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, 'docs', 'proto', 'obs', 'round3'); os.makedirs(OUT, exist_ok=True)
LOCKED = ('aug2015', 'aug2018', 'aug2020', 'jul2018', 'oct2016')
UA = {'User-Agent': 'mass-flood-watch research (github.com/Horus331/mass-flood-watch)', 'Accept': 'application/json'}
API = 'https://seeclickfix.com/api/v2'
D3 = (-72.20, 41.90, -71.30, 42.72)                      # lon0, lat0, lon1, lat1: union of the catalogue boxes, padded
FLOOD_RE = re.compile(r'flood|drain|catch ?basin|storm ?water|stormwater|standing water|ponding|puddl|culvert|sewer back|washout|washed out|'
                      r'water (on|in|across|over) (the )?(road|street)|manhole', re.I)
SEARCH = ('flood',)      # text search is slow on SCF (60 s timeouts seen); request-type ids carry the bulk
STATUS = 'open,acknowledged,closed,archived'
LOG = []


def log(*a):
    s = ' '.join(str(x) for x in a); print(s, flush=True); LOG.append(s[:400])


def get(url, params, tries=6):
    for i in range(tries):
        try:
            r = requests.get(url, params=params, headers=UA, timeout=120)
        except Exception as ex:
            log('error', url, repr(ex)[:200]); time.sleep(5 * (i + 1)); continue
        if r.status_code == 429 or r.status_code >= 500:
            w = int(r.headers.get('Retry-After') or 10 * (i + 1)); log('HTTP', r.status_code, url, 'wait', w); time.sleep(min(w, 90)); continue
        if r.status_code != 200:
            log('HTTP', r.status_code, url, json.dumps(params)[:300], r.text[:200]); return None
        time.sleep(0.6)
        try: return r.json()
        except Exception: log('bad json', url); return None
    return None


def storms():
    C = json.load(open(os.path.join(ROOT, 'docs', 'proto', 'obs', 'catalog.json')))['events']
    return C


def window(e, pad_h=0):
    t0 = dt.datetime.strptime(e['t0'], '%Y-%m-%dT%H:00Z').replace(tzinfo=dt.timezone.utc)
    return t0 - dt.timedelta(hours=pad_h), t0 + dt.timedelta(hours=int(e['hours']) + 24 + pad_h)


def compact(i):
    rt = i.get('request_type') or {}; md = i.get('media') or {}
    return dict(id=i.get('id'), created_at=i.get('created_at'), acknowledged_at=i.get('acknowledged_at'), closed_at=i.get('closed_at'),
                status=i.get('status'), lat=i.get('lat'), lng=i.get('lng'), address=i.get('address'), summary=i.get('summary'),
                description=(i.get('description') or '')[:600], request_type=rt.get('title'), request_type_id=rt.get('id'),
                organization=rt.get('organization'), html_url=i.get('html_url'),
                photo=bool(md.get('image_full') or md.get('image_square_100x100') or md.get('representative_image_url')),
                reporter_kind=((i.get('reporter') or {}).get('role') or (i.get('reporter') or {}).get('civic_points') and 'citizen'))


def issues(params, max_pages=200):
    out = []; p = dict(params, per_page=100, status=STATUS)
    for page in range(1, max_pages + 1):
        p['page'] = page; J = get(f'{API}/issues', p)
        if not J: break
        I = J.get('issues') or []; out += [compact(i) for i in I]
        pg = (J.get('metadata') or {}).get('pagination') or {}
        if page == 1: log('  query', json.dumps({k: v for k, v in params.items()})[:240], 'entries', pg.get('entries'), 'pages', pg.get('pages'))
        if not pg.get('next_page') or not I: break
    return out


# ------------------------------------------------------------------------------------------------ request types
def types():
    seen = {}
    lon0, lat0, lon1, lat1 = D3
    lats = [round(lat0 + 0.1 * k, 2) for k in range(int((lat1 - lat0) / 0.1) + 1)]
    lons = [round(lon0 + 0.1 * k, 2) for k in range(int((lon1 - lon0) / 0.1) + 1)]
    for la in lats:
        for lo in lons:
            J = get(f'{API}/issues/new', dict(lat=la, lng=lo))
            if not J: continue
            for t in J.get('request_types') or []:
                k = t.get('id')
                if k not in seen: seen[k] = dict(id=k, title=t.get('title'), organization=t.get('organization'), url=t.get('url'), points=[])
                if len(seen[k]['points']) < 3: seen[k]['points'].append([lo, la])
    T = sorted(seen.values(), key=lambda t: (str(t['organization']), str(t['title'])))
    for t in T: t['flood_like'] = bool(FLOOD_RE.search(f"{t['title']}"))
    json.dump(dict(made_by='proto/scf_fetch.py types', grid_deg=0.1, box=D3, n=len(T), request_types=T, log=LOG[-50:]),
              open(os.path.join(OUT, 'scf_request_types.json'), 'w'), indent=1)
    log('request types', len(T), 'flood-like', sum(t['flood_like'] for t in T))
    return T


# ------------------------------------------------------------------------------------------------ storm windows (all types)
def windows():
    S = {}
    for e in storms():
        if e['id'] in LOCKED or e['id'] == 'sep2014': continue
        a, b = window(e); lo0, la0, lo1, la1 = e['bbox_lonlat']
        log(e['id'], a.isoformat(), b.isoformat())
        I = issues(dict(min_lat=la0, min_lng=lo0, max_lat=la1, max_lng=lo1, after=a.strftime('%Y-%m-%dT%H:%M:%SZ'), before=b.strftime('%Y-%m-%dT%H:%M:%SZ')))
        I = [i for i in I if i['created_at']]
        S[e['id']] = len(I)
        json.dump(dict(storm=e['id'], window_utc=[a.isoformat(), b.isoformat()], bbox_lonlat=e['bbox_lonlat'], n=len(I), issues=I),
                  open(os.path.join(OUT, f'scf_window_{e["id"]}.json'), 'w'), indent=0)
        log('  ', e['id'], 'issues', len(I), 'flood-like', sum(bool(FLOOD_RE.search(f"{i['request_type']} {i['summary']} {i['description']}")) for i in I))
    return S


# ------------------------------------------------------------------------------------------------ D3-wide flood-type issues
def d3(T=None):
    if T is None:
        f = os.path.join(OUT, 'scf_request_types.json'); T = json.load(open(f))['request_types'] if os.path.exists(f) else types()
    ids = {t['id'] for t in T if t['flood_like']}
    for f in sorted(os.listdir(OUT)):          # historic request-type ids seen in the storm windows (types get renumbered over the years)
        if f.startswith('scf_window_'):
            for i in json.load(open(os.path.join(OUT, f)))['issues']:
                if i.get('request_type_id') and FLOOD_RE.search(str(i.get('request_type'))): ids.add(i['request_type_id'])
    ids = sorted(ids); log('flood-like request type ids', ids)
    lon0, lat0, lon1, lat1 = D3; box = dict(min_lat=lat0, min_lng=lon0, max_lat=lat1, max_lng=lon1)
    got = {}; today = dt.date.today()
    for y in range(2018, today.year + 1):
        for half in ((f'{y}-01-01', f'{y}-07-01'), (f'{y}-07-01', f'{y + 1}-01-01')):
            q = dict(box, after=half[0] + 'T00:00:00Z', before=half[1] + 'T00:00:00Z')
            for k in range(0, len(ids), 10):
                for i in issues(dict(q, request_types=','.join(str(x) for x in ids[k:k + 10]))): i['via'] = 'type'; got.setdefault(i['id'], i)
            for s in SEARCH:
                for i in issues(dict(q, search=s)):
                    if i['id'] not in got: i['via'] = f'search:{s}'; got[i['id']] = i
    locked = [window(e, 24) for e in storms() if e['id'] in LOCKED]

    def is_locked(t):
        try: t = dt.datetime.fromisoformat(t.replace('Z', '+00:00'))
        except Exception: return False
        return any(a <= t <= b for a, b in locked)
    rows = [i for i in got.values() if i['created_at'] and not is_locked(i['created_at'])]
    nl = len(got) - len(rows)
    rows = [i for i in rows if FLOOD_RE.search(f"{i['request_type']} {i['summary']} {i['description']}")]
    rows.sort(key=lambda i: i['created_at'])
    keys = ['id', 'created_at', 'lat', 'lng', 'address', 'request_type', 'summary', 'description', 'status', 'via']     # compact: committed file
    for i in rows:
        i['description'] = (i['description'] or '').replace('\n', ' ')[:80]; i['lat'] = f"{float(i['lat']):.5f}"; i['lng'] = f"{float(i['lng']):.5f}"
        i['address'] = (i['address'] or '').replace(', United States', '').replace(', USA', '')
    with open(os.path.join(OUT, 'scf_flood_d3.csv'), 'w', newline='') as fh:
        w = csv.DictWriter(fh, keys, extrasaction='ignore'); w.writeheader(); w.writerows(rows)
    log('D3 flood-like issues', len(rows), 'dropped (locked windows)', nl, 'type ids', len(ids))
    return rows


def main():
    m = sys.argv[1] if len(sys.argv) > 1 else 'all'
    T = None
    if m == 'probe':      # raw shapes of the three endpoints (debugging only)
        P = dict(places=get(f'{API}/places', dict(search='Worcester')),
                 new=get(f'{API}/issues/new', dict(lat=42.2626, lng=-71.8023)),
                 issues=get(f'{API}/issues', dict(place_url='worcester', per_page=2, search='flood', status=STATUS)),
                 open311=get('https://seeclickfix.com/open311/v2/services.json', dict(lat=42.2626, long=-71.8023)))
        json.dump(P, open(os.path.join(OUT, 'scf_probe.json'), 'w'), indent=1, default=str)
    if m in ('types', 'all'): T = types()
    if m in ('windows', 'all'): windows()
    if m in ('d3', 'all'): d3(T)
    json.dump(dict(mode=m, utc=dt.datetime.now(dt.timezone.utc).isoformat(), log=LOG[-400:]), open(os.path.join(OUT, f'scf_fetch_{m}.json'), 'w'), indent=0)


if __name__ == '__main__':
    main()
