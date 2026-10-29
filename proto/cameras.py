"""USGS stream-gauge cameras (NIMS) as a public image record of District 3 storms (docs/proto/cameras/CAMERAS.md).

The USGS National Imagery Management System serves the stills of its stream-gauge cameras, with history, through a public API
(https://api.waterdata.usgs.gov/nims/v0; no key needed, a free key in API_USGS_PAT raises the rate limit). USGS images are public domain.
The cameras look at streams, not roads, but several sit at road crossings, so a still can show a culvert or bridge overtopping and when.

    python proto/cameras.py list   [--out docs/proto/cameras/usgs_cameras.csv]          # cameras in / near District 3
    python proto/cameras.py fetch  --t0 2023-09-11T12:00Z --hours 36 [--every-min 15] [--cams ID,ID | --near-km 0] --out DIR
    python proto/cameras.py storm  --storm arc20261105 [--root docs/proto/archive] --out DIR     # an archived storm's window
    python proto/cameras.py catalog [--ids sep2023,aug2021] --out DIR                          # the catalogue storms (history test)
    python proto/cameras.py sheet  DIR                                                          # contact sheet per camera (PNG)
    python proto/cameras.py upload DIR --prefix cameras/<name>                                  # images -> HF dataset (HF_TOKEN)
    python proto/cameras.py selftest

Images are NOT committed to git (size; every push restarts the site deploy). They go to the Hugging Face dataset used for the run backups;
only the per-storm index (camera, time, URL) and the contact sheets' list are committed.
"""
import os, sys, csv, json, time, argparse, datetime as dt

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.normpath(os.path.join(HERE, '..')); sys.path.insert(0, HERE)
BASE = os.environ.get('NIMS_BASE', 'https://api.waterdata.usgs.gov/nims/v0')
UA = {'User-Agent': 'mass-flood-watch research (github.com/Horus331/mass-flood-watch)'}
MA_BBOX = (-73.6, 41.2, -69.8, 42.95)
OUT_LIST = os.path.join('docs', 'proto', 'cameras', 'usgs_cameras.csv')


def log(*a): print(*a, flush=True)


def utc(s):
    s = str(s).strip().replace(' ', 'T')
    if s.endswith('Z'): s = s[:-1] + '+00:00'
    if len(s) == 13: s += ':00'
    d = dt.datetime.fromisoformat(s)
    return d.astimezone(dt.timezone.utc).replace(tzinfo=None) if d.tzinfo else d


def api(path, params=None, tries=4):
    import requests
    h = dict(UA); k = os.environ.get('API_USGS_PAT')
    if k: h['X-Api-Key'] = k
    for i in range(tries):
        try:
            r = requests.get(BASE + path, params=params, headers=h, timeout=90)
            if r.status_code == 200: return r.json()
            log('NIMS', path, r.status_code, r.text[:200])
            if r.status_code in (400, 404): return None
        except Exception as e: log('NIMS', path, repr(e)[:200])
        time.sleep(5 * (i + 1))
    return None


def cameras():
    """Every NIMS camera inside Massachusetts' bbox, with town / District 3 flag and distance to District 3 (km)."""
    import storm_archive as SA
    from shapely.geometry import Point
    J = api('/cameras') or []
    D = SA.d3(); U = D['union']; out = []
    for c in J:
        try: lat, lon = float(c.get('lat')), float(c.get('lng'))
        except Exception: continue
        if not (MA_BBOX[0] <= lon <= MA_BBOX[2] and MA_BBOX[1] <= lat <= MA_BBOX[3]): continue
        p = Point(lon, lat); dkm = 0.0 if U.contains(p) else U.distance(p) * 85.0          # degrees -> km at 42 N (approx.)
        out.append(dict(camId=c.get('camId'), camName=c.get('camName'), lat=lat, lon=lon, siteId=c.get('siteId') or c.get('nwisId') or '',
                        town=SA.town_of(lon, lat) or '', in_d3=bool(U.contains(p)), d3_km=round(dkm, 1), createdDate=c.get('createdDate'),
                        newestImageDT=c.get('newestImageDT'), smallDir=c.get('smallDir'), overlayDir=c.get('overlayDir')))
    return sorted(out, key=lambda r: (not r['in_d3'], r['d3_km'], r['camId'] or ''))


def cmd_list(a):
    C = cameras(); os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    cols = ['camId', 'camName', 'lat', 'lon', 'siteId', 'town', 'in_d3', 'd3_km', 'createdDate', 'newestImageDT', 'smallDir', 'overlayDir']
    with open(a.out, 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction='ignore'); w.writeheader(); w.writerows(C)
    log(f"{len(C)} NIMS camera(s) in the MA bbox, {sum(c['in_d3'] for c in C)} in District 3, {sum(c['d3_km'] <= 10 for c in C)} within 10 km -> {a.out}")
    for c in C[:40]: log(f"  {c['camId']:<45} {c['town'] or '-':<18} d3 {c['d3_km']:5.1f} km  {c['createdDate']} .. {c['newestImageDT']}")


def list_files(cam, t0, t1, limit=5000):
    """Image items of one camera between t0 and t1 (UTC), oldest first, paged with the 'after' cursor as flowcam does."""
    items, after = [], f'{t0:%Y-%m-%dT%H:%M:%S}'
    while True:
        page = api('/listFiles', dict(camId=cam, limit=limit, recent='false', after=after, before=f'{t1:%Y-%m-%dT%H:%M:%S}', rawItem='true'))
        if not page: break
        items += page
        if len(page) < limit: break
        after = (utc(page[-1]['timestamp']) + dt.timedelta(seconds=1)).strftime('%Y-%m-%dT%H:%M:%S')
    return items


def thin(items, every_min):
    """Keep at most one image per every_min minutes (the first in each slot)."""
    out, last = [], None
    for x in sorted(items, key=lambda x: x.get('timestamp') or ''):
        try: t = utc(x['timestamp'])
        except Exception: continue
        if last is None or (t - last).total_seconds() >= every_min * 60 - 1: out.append(x); last = t
    return out


def fetch(t0, t1, out, cams=None, near_km=10.0, every_min=15, size='small', download=True, label=''):
    import requests
    C = [c for c in cameras() if (c['camId'] in cams if cams else (c['in_d3'] or c['d3_km'] <= near_km))]
    os.makedirs(out, exist_ok=True); rows = []; per = {}
    for c in C:
        try:
            cr = utc(c['createdDate']) if c.get('createdDate') else None; nw = utc(c['newestImageDT']) if c.get('newestImageDT') else None
        except Exception: cr = nw = None
        if (cr and cr > t1) or (nw and nw < t0): per[c['camId']] = dict(n=0, note='camera not running in the window'); continue
        it = thin(list_files(c['camId'], t0, t1), every_min); per[c['camId']] = dict(n=len(it), town=c['town'], in_d3=c['in_d3'])
        base = (c['smallDir'] if size == 'small' else c['overlayDir']) or ''
        for x in it:
            url = base.rstrip('/') + '/' + x['filename']; loc = os.path.join(c['camId'], x['filename'])
            ok = False
            if download:
                p = os.path.join(out, loc); os.makedirs(os.path.dirname(p), exist_ok=True)
                if not os.path.exists(p):
                    try:
                        r = requests.get(url, headers=UA, timeout=60)
                        if r.status_code == 200 and r.content[:3] == b'\xff\xd8\xff': open(p, 'wb').write(r.content); ok = True
                    except Exception as e: log('image', url, repr(e)[:120])
                else: ok = True
            rows.append(dict(camId=c['camId'], town=c['town'], in_d3=c['in_d3'], lat=c['lat'], lon=c['lon'], timestamp=x.get('timestamp'), filename=x['filename'],
                             bytes=x.get('fs'), url=url, local=loc if ok else ''))
        log(f"  {c['camId']}: {len(it)} image(s) {t0:%Y-%m-%d %H:%M}..{t1:%Y-%m-%d %H:%M}")
    with open(os.path.join(out, 'index.csv'), 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=['camId', 'town', 'in_d3', 'lat', 'lon', 'timestamp', 'filename', 'bytes', 'url', 'local']); w.writeheader(); w.writerows(rows)
    S = dict(label=label, t0=f'{t0:%Y-%m-%dT%H:%MZ}', t1=f'{t1:%Y-%m-%dT%H:%MZ}', every_min=every_min, size=size, cameras=per, images=len(rows),
             downloaded=sum(bool(r['local']) for r in rows), source=BASE, licence='USGS imagery, public domain')
    json.dump(S, open(os.path.join(out, 'summary.json'), 'w'), indent=1)
    log(f"{label or 'fetch'}: {len(C)} camera(s), {len(rows)} image(s), {S['downloaded']} downloaded -> {out}")
    return S


def cmd_fetch(a):
    t0 = utc(a.t0); fetch(t0, t0 + dt.timedelta(hours=a.hours), a.out, cams=a.cams.split(',') if a.cams else None, near_km=a.near_km,
                          every_min=a.every_min, size=a.size, download=not a.no_download, label=a.label or '')


def cmd_storm(a):
    import storm_archive as SA
    S = SA.find_storm(a.root, a.storm); w0, w1 = SA.storm_window(S, pad_h=12)
    fetch(w0, w1, a.out, near_km=a.near_km, every_min=a.every_min, size=a.size, download=not a.no_download, label=S['id'])


def cmd_catalog(a):
    cat = json.load(open(os.path.join(ROOT, 'docs', 'proto', 'obs', 'catalog.json')))
    ev = cat['events'] if isinstance(cat, dict) else cat; ids = set(a.ids.split(',')) if a.ids else None; tot = {}
    for e in ev:
        if ids and e['id'] not in ids: continue
        if not e.get('t0'): continue
        t0 = utc(e['t0']); S = fetch(t0, t0 + dt.timedelta(hours=int(e.get('hours', 36)) + 12), os.path.join(a.out, e['id']), near_km=a.near_km,
                                     every_min=a.every_min, size=a.size, download=not a.no_download, label=e['id'])
        tot[e['id']] = dict(date=e.get('date_local') or e['t0'][:10], images=S['images'], cameras_with_images=sum(v.get('n', 0) > 0 for v in S['cameras'].values()))
    json.dump(tot, open(os.path.join(a.out, 'catalog_summary.json'), 'w'), indent=1)
    log('catalogue:', json.dumps(tot)[:2000])


def cmd_sheet(a):
    """One contact sheet per camera: up to 24 thumbnails across the window, time-stamped (for a quick look; and for labelling by eye)."""
    from PIL import Image, ImageDraw
    rows = list(csv.DictReader(open(os.path.join(a.dir, 'index.csv'))))
    for cam in sorted({r['camId'] for r in rows}):
        R = [r for r in rows if r['camId'] == cam and r['local']]
        if not R: continue
        step = max(1, len(R) // 24); R = R[::step][:24]; W, H, cols = 240, 150, 6
        sheet = Image.new('RGB', (W * cols, (H + 16) * ((len(R) + cols - 1) // cols)), 'white'); d = ImageDraw.Draw(sheet)
        for i, r in enumerate(R):
            try: im = Image.open(os.path.join(a.dir, r['local'])).convert('RGB'); im.thumbnail((W, H))
            except Exception: continue
            x, y = (i % cols) * W, (i // cols) * (H + 16); sheet.paste(im, (x, y + 16)); d.text((x + 3, y + 2), r['timestamp'][:16].replace('T', ' ') + 'Z', fill='black')
        p = os.path.join(a.dir, f'sheet_{cam}.jpg'); sheet.save(p, quality=80); log('sheet', p, len(R))


def cmd_upload(a):
    from huggingface_hub import HfApi
    api_ = HfApi(token=os.environ.get('HF_TOKEN') or None)
    api_.upload_folder(folder_path=a.dir, path_in_repo=a.prefix, repo_id=a.repo, repo_type='dataset', commit_message=f'cameras: {a.prefix}')
    log(f'uploaded {a.dir} -> https://huggingface.co/datasets/{a.repo}/tree/main/{a.prefix}')


def selftest():
    it = [dict(timestamp='2023-09-11T12:00:00Z', filename='a'), dict(timestamp='2023-09-11T12:05:00Z', filename='b'),
          dict(timestamp='2023-09-11T12:15:00Z', filename='c'), dict(timestamp='2023-09-11T12:31:00Z', filename='d')]
    assert [x['filename'] for x in thin(it, 15)] == ['a', 'c', 'd'], thin(it, 15)
    assert utc('2023-09-11T12Z') == dt.datetime(2023, 9, 11, 12) and utc('2023-09-11T12:00:00Z') == dt.datetime(2023, 9, 11, 12)
    print('cameras selftest ok')


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0]); sp = ap.add_subparsers(dest='cmd', required=True)
    p = sp.add_parser('list'); p.add_argument('--out', default=OUT_LIST)
    for name in ('fetch', 'storm', 'catalog'):
        p = sp.add_parser(name); p.add_argument('--out', required=True); p.add_argument('--every-min', type=int, default=15); p.add_argument('--near-km', type=float, default=10.0)
        p.add_argument('--size', default='small', choices=['small', 'overlay']); p.add_argument('--no-download', action='store_true')
        if name == 'fetch':
            p.add_argument('--t0', required=True); p.add_argument('--hours', type=float, default=36); p.add_argument('--cams'); p.add_argument('--label')
        if name == 'storm': p.add_argument('--storm', required=True); p.add_argument('--root', default=os.path.join('docs', 'proto', 'archive'))
        if name == 'catalog': p.add_argument('--ids')
    p = sp.add_parser('sheet'); p.add_argument('dir')
    p = sp.add_parser('upload'); p.add_argument('dir'); p.add_argument('--prefix', required=True); p.add_argument('--repo', default='mohabeldokla/mass-flood-watch-tiles')
    sp.add_parser('selftest')
    a = ap.parse_args()
    dict(list=cmd_list, fetch=cmd_fetch, storm=cmd_storm, catalog=cmd_catalog, sheet=cmd_sheet, upload=cmd_upload, selftest=lambda a: selftest())[a.cmd](a)
