"""Forward-only feed archives for District 3 (docs/proto/archive_feeds/FEEDS.md).  GitHub Actions only; nothing is committed to the repo.
The Hugging Face dataset mohabeldokla/mass-flood-watch-tiles is the archive, and is also the state (what is already archived).

    python proto/archive_feeds.py refs [--max-cycles N] [--dates YYYYMMDD,...] [--dry]
        NOAA REFS flash-flood / recurrence-interval exceedance probabilities (refs.tCCz.ffri.fFF.conus.grib2) from NOMADS com/refs/prod
        and com/refs/para (and the AWS RRFS buckets if NOMADS has nothing), clipped to District 3 + margin -> HF refs/ffri/YYYYMMDD/tCCz/,
        plus the REFS precipitation (APCP from the pmmn / mean / avrg product, byte ranges via .idx) -> HF refs/qpf/YYYYMMDD/tCCz/.
    python proto/archive_feeds.py sportlis [--dry]
        NASA SPoRT-LIS soil moisture ImageServers (NRT lis_rsm_2m, lis_vsm_percentile_40cm / 100cm / 200cm): exportImage over District 3
        at native resolution for every time step the service offers that is not archived yet -> HF sportlis/YYYYMMDD_HH/<layer>.tif
    python proto/archive_feeds.py stormwater --date 2026-10-29 [--dry]
        MassDOT Stormwater Asset Database (gisstg FeatureServer, layers + tables), statewide -> HF massdot_stormwater/<date>/ and a summary
        (counts per layer per District 3 town, field lists) returned as ::notice annotations ('sw i/n sha'; decode with `swdecode`).
    python proto/archive_feeds.py swdecode --run RUN_ID --out summary.json     # local: rebuild the stormwater summary from annotations
    python proto/archive_feeds.py swmd summary.json --out docs/proto/stormwater/SNAPSHOT.md
"""
import argparse
import base64
import datetime as dt
import gzip
import hashlib
import io
import json
import os
import re
import sys
import tempfile
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
REPO = 'mohabeldokla/mass-flood-watch-tiles'
D3_BOX = (128000.0, 856000.0, 206000.0, 946000.0)          # EPSG:26986, as proto/forecast.py / proto/storm_archive.py
MARGIN_M = 15000.0                                          # small margin around District 3 (5 REFS / SPoRT 3 km cells)
UA = {'User-Agent': 'mass-flood-watch research archive (github.com/Horus331/mass-flood-watch)'}
NOMADS = {'prod': 'https://nomads.ncep.noaa.gov/pub/data/nccf/com/refs/prod/', 'para': 'https://nomads.ncep.noaa.gov/pub/data/nccf/com/refs/para/'}
AWS_BUCKETS = ('noaa-rrfs-ops', 'noaa-rrfs-pds')
FFRI_RE = re.compile(r'refs\.t(\d\d)z\.ffri\.f(\d+)\.conus\.grib2$')
QPF_RE = re.compile(r'refs\.t(\d\d)z\.(pmmn|mean|avrg|lpmm)\.f(\d+)\.conus\.grib2$')
QPF_PREF = ('pmmn', 'lpmm', 'mean', 'avrg')
SPORT = 'https://maps.disasters.nasa.gov/ags03/rest/services/NRT/{}/ImageServer'
SPORT_HOSTS = ('https://maps.disasters.nasa.gov/ags03/rest/services', 'https://maps.disasters.nasa.gov/ags04/rest/services',
               'https://maps.disasters.nasa.gov/arcgis/rest/services')
SPORT_LAYERS = ('lis_rsm_2m', 'lis_vsm_percentile_40cm', 'lis_vsm_percentile_100cm', 'lis_vsm_percentile_200cm')
SW = 'https://gisstg.massdot.state.ma.us/arcgis/rest/services/Assets/Stormwater/FeatureServer'
CHUNK = 4000


def log(*a):
    print(*a, flush=True)


def note(title, msg):
    """One GitHub ::notice annotation (the read-back channel; artifacts cannot be downloaded from the workspace)."""
    msg = str(msg).replace('%', '%25').replace('\r', '').replace('\n', '%0A')[:3900]
    print(f'::notice title={title}::{msg}', flush=True)


def get(url, params=None, tries=5, timeout=120, stream=False, headers=None, ok=(200,), method='GET', data=None):
    import requests
    last = None
    for i in range(tries):
        try:
            r = requests.request(method, url, params=params, data=data, timeout=timeout, stream=stream, headers={**UA, **(headers or {})})
            if r.status_code in ok: return r
            last = f'HTTP {r.status_code}'
            if r.status_code in (403, 404): return r
        except Exception as e:
            last = repr(e)[:200]
        time.sleep(min(60, 3 * 2 ** i))
    raise RuntimeError(f'{url}: {last}')


def d3_lonlat(margin=MARGIN_M):
    from pyproj import Transformer
    tr = Transformer.from_crs(26986, 4326, always_xy=True); x0, y0, x1, y1 = D3_BOX
    xs = np.linspace(x0 - margin, x1 + margin, 21); ys = np.linspace(y0 - margin, y1 + margin, 21)
    X, Y = np.meshgrid(xs, ys); lon, lat = tr.transform(X.ravel(), Y.ravel())
    return float(lon.min()), float(lat.min()), float(lon.max()), float(lat.max())


# ------------------------------------------------------------------------------------------------ Hugging Face (archive + state)
def hf():
    from huggingface_hub import HfApi
    return HfApi(token=os.environ.get('HF_TOKEN'))


def hf_ls(path):
    """Paths directly under path in the dataset ([] when the folder does not exist)."""
    try:
        return [e.path for e in hf().list_repo_tree(REPO, path_in_repo=path, repo_type='dataset')]
    except Exception:
        return []


def hf_json(path):
    try:
        from huggingface_hub import hf_hub_download
        return json.load(open(hf_hub_download(REPO, path, repo_type='dataset', token=os.environ.get('HF_TOKEN'))))
    except Exception:
        return None


def hf_put(files, message, dry=False):
    """files: {path_in_repo: bytes | local path}; one dataset commit."""
    if dry or not files:
        log(f'(dry) would upload {len(files)} files: {sorted(files)[:6]}'); return
    from huggingface_hub import CommitOperationAdd
    ops = [CommitOperationAdd(path_in_repo=k, path_or_fileobj=v) for k, v in files.items()]
    for i in range(4):
        try:
            hf().create_commit(REPO, repo_type='dataset', operations=ops, commit_message=message); return
        except Exception as e:
            log(f'HF commit try {i}: {repr(e)[:300]}'); time.sleep(20 * (i + 1))
    raise RuntimeError('HF upload failed')


# ------------------------------------------------------------------------------------------------ REFS
def html_links(url):
    r = get(url, timeout=60, tries=3)
    if r.status_code != 200: return None
    return [h for h in re.findall(r'href="([^"?#]+)"', r.text) if not h.startswith(('/', 'http', '..'))]


def nomads_cycles(dates, stats):
    """{(date, cc): {'ffri': {fh: url}, 'qpf': {kind: {fh: url}}, 'src': 'nomads-prod|para', 'base': dir}} by crawling the HTML directory
    listings under refs.YYYYMMDD/ (depth <= 3).  A cycle comes wholly from prod when prod has its ffri files, else wholly from para."""
    per = {}
    for src in ('prod', 'para'):
        base = NOMADS[src]; top = html_links(base); stats[f'nomads_{src}_top'] = (top[-8:] if top else top) if top is not None else 'unreachable'
        out = per[src] = {}
        if not top: continue
        for d in dates:
            root = f'refs.{d}/'
            if root not in top: continue
            stack = [(base + root, 0)]; nreq = 0
            while stack and nreq < 40:
                url, depth = stack.pop(); L = html_links(url); nreq += 1; time.sleep(0.4)
                if not L: continue
                files = [h for h in L if not h.endswith('/')]; dirs = [h for h in L if h.endswith('/')]
                stats.setdefault(f'nomads_{src}_sample', {})[url.replace(base, '')] = dirs[:8] + files[:6] + [f'({len(files)} files)']
                for h in files:
                    m = FFRI_RE.search(h)
                    if m: out.setdefault((d, m.group(1)), dict(ffri={}, qpf={}, src=f'nomads-{src}', base=url))['ffri'][int(m.group(2))] = url + h
                    m = QPF_RE.search(h)
                    if m: out.setdefault((d, m.group(1)), dict(ffri={}, qpf={}, src=f'nomads-{src}', base=url))['qpf'].setdefault(m.group(2), {})[int(m.group(3))] = url + h
                if depth < 3:
                    stack += [(url + h, depth + 1) for h in dirs if depth == 0 or re.fullmatch(r'(\d\d|ensprod|enspost|products?|conus|refs|ens|post)/', h)]
    C = {}
    for k in set(per['prod']) | set(per['para']):
        C[k] = per['prod'][k] if per['prod'].get(k, {}).get('ffri') else per['para'].get(k) or per['prod'][k]
    return C


def s3_list(bucket, prefix, delim='/'):
    import xml.etree.ElementTree as ET
    keys, pre, token = [], [], None
    for _ in range(20):
        p = {'list-type': '2', 'prefix': prefix, 'max-keys': '1000'}
        if delim: p['delimiter'] = delim
        if token: p['continuation-token'] = token
        r = get(f'https://{bucket}.s3.amazonaws.com/', params=p, timeout=60, tries=3)
        if r.status_code != 200: return None, None
        t = ET.fromstring(r.content); ns = {'s': t.tag.split('}')[0].strip('{')} if '}' in t.tag else {}
        q = (lambda n: f's:{n}') if ns else (lambda n: n)
        keys += [(c.find(q('Key')).text, int(c.find(q('Size')).text)) for c in t.findall(q('Contents'), ns)]
        pre += [c.find(q('Prefix')).text for c in t.findall(q('CommonPrefixes'), ns)]
        tr = t.find(q('IsTruncated'), ns)
        if tr is not None and tr.text == 'true': token = t.find(q('NextContinuationToken'), ns).text
        else: break
    return keys, pre


def aws_cycles(dates, stats):
    """Same as nomads_cycles from the AWS RRFS buckets: crawl prefixes that mention refs or one of the dates (depth <= 5)."""
    out = {}
    for b in AWS_BUCKETS:
        k, top = s3_list(b, '')
        stats[f'aws_{b}_top'] = top[:15] if top is not None else 'unreachable'
        if top is None: continue
        stack = [(p, 0) for p in top if 'refs' in p.lower() or 'rrfs' in p.lower() or any(d in p for d in dates)]; nreq = 0
        while stack and nreq < 60:
            p, depth = stack.pop(); keys, pre = s3_list(b, p); nreq += 1
            if keys is None: continue
            stats.setdefault(f'aws_{b}_sample', {})[p] = (pre[:6] + [x for x, _ in keys[:4]])
            for key, size in keys:
                m = FFRI_RE.search(key)
                for d in dates:
                    if m and d in key:
                        out.setdefault((d, m.group(1)), dict(ffri={}, qpf={}, src=f'aws-{b}', base=f'https://{b}.s3.amazonaws.com/'))['ffri'][int(m.group(2))] = f'https://{b}.s3.amazonaws.com/{key}'
                m2 = QPF_RE.search(key)
                for d in dates:
                    if m2 and d in key:
                        out.setdefault((d, m2.group(1)), dict(ffri={}, qpf={}, src=f'aws-{b}', base=f'https://{b}.s3.amazonaws.com/'))['qpf'].setdefault(m2.group(2), {})[int(m2.group(3))] = f'https://{b}.s3.amazonaws.com/{key}'
            if depth < 5:
                for q in pre:
                    tail = q[len(p):].strip('/').lower()
                    if ('refs' in tail or any(d in tail for d in dates) or re.fullmatch(r'\d\d|ensprod|enspost|conus|products?', tail)
                            or (depth == 0 and 'refs' in p.lower())):
                        stack.append((q, depth + 1))
    return out


GRIB_KEYS = ('discipline', 'parameterCategory', 'parameterNumber', 'shortName', 'name', 'units', 'typeOfLevel', 'level', 'stepType', 'stepRange',
             'startStep', 'endStep', 'probabilityType', 'probabilityTypeName', 'scaleFactorOfLowerLimit', 'scaledValueOfLowerLimit',
             'scaleFactorOfUpperLimit', 'scaledValueOfUpperLimit', 'lowerLimit', 'upperLimit', 'percentileValue', 'derivedForecast',
             'typeOfStatisticalProcessing', 'lengthOfTimeRange', 'dataDate', 'dataTime')


def grib_clip(path, window, keep=lambda m: True):
    """-> (window, lat, lon, [(meta, array)]) for the messages of a GRIB2 file inside the lon/lat window (subgrid index box)."""
    import pygrib
    G = pygrib.open(path); out = []; lat = lon = None
    for i, m in enumerate(G, 1):
        try:
            if not keep(m): continue
        except Exception:
            continue
        meta = {'msg': i, 'str': str(m)[:300]}
        for k in GRIB_KEYS:
            try:
                v = m[k]; meta[k] = v if isinstance(v, (int, float, str)) else str(v)
            except Exception:
                pass
        if window is None or lat is None:
            la, lo = m.latlons(); lo = np.where(lo > 180, lo - 360, lo)
            if window is None:
                b = d3_lonlat(); inside = (lo >= b[0]) & (lo <= b[2]) & (la >= b[1]) & (la <= b[3])
                if not inside.any(): raise RuntimeError('District 3 window not on the grid')
                r, c = np.nonzero(inside); window = (int(r.min()), int(r.max()) + 1, int(c.min()), int(c.max()) + 1)
            i0, i1, j0, j1 = window; lat = la[i0:i1, j0:j1].astype(np.float32); lon = lo[i0:i1, j0:j1].astype(np.float32)
        i0, i1, j0, j1 = window; v = m.values
        a = np.ma.filled(np.ma.asarray(v, dtype=np.float32)[i0:i1, j0:j1], np.nan).astype(np.float32)
        out.append((meta, a))
    G.close()
    return window, lat, lon, out


def download(url, dest, max_mb=600):
    r = get(url, stream=True, timeout=300)
    if r.status_code != 200: raise RuntimeError(f'{url}: HTTP {r.status_code}')
    n = 0
    with open(dest, 'wb') as f:
        for b in r.iter_content(1 << 20):
            f.write(b); n += len(b)
            if n > max_mb * 2 ** 20: raise RuntimeError(f'{url}: larger than {max_mb} MB')
    return n


def idx_ranges(url, pat=re.compile(r':APCP:')):
    """Byte ranges of the APCP records of a GRIB2 file from its .idx (None when there is no .idx)."""
    r = get(url + '.idx', timeout=60, tries=2)
    if r.status_code != 200: return None
    L = [l.split(':') for l in r.text.strip().splitlines() if l.count(':') >= 4]; out = []
    for i, l in enumerate(L):
        if pat.search(':' + ':'.join(l[3:])):
            s = int(l[1]); e = int(L[i + 1][1]) - 1 if i + 1 < len(L) else ''
            out.append((s, e, ':'.join(l[3:6])))
    return out


def refs(max_cycles=4, dates=None, dry=False, min_age_h=6.0):
    now = dt.datetime.now(dt.timezone.utc)
    dates = dates or [(now - dt.timedelta(days=k)).strftime('%Y%m%d') for k in (2, 1, 0)]
    stats = {}; C = nomads_cycles(dates, stats)
    if not any(c['ffri'] for c in C.values()):
        log('no ffri on NOMADS for', dates, '- trying AWS'); C.update({k: v for k, v in aws_cycles(dates, stats).items() if k not in C or not C[k]['ffri']})
    note('refs listing', json.dumps(dict(dates=dates, cycles={f'{d}t{c}z': dict(src=v['src'], ffri=len(v['ffri']), qpf={k: len(x) for k, x in v['qpf'].items()})
                                                          for (d, c), v in sorted(C.items())}))[:3800])
    note('refs crawl sample', json.dumps(stats)[:3800])
    todo = []
    for (d, cc), c in sorted(C.items()):
        if not c['ffri']: continue
        age = (now - dt.datetime.strptime(d + cc, '%Y%m%d%H').replace(tzinfo=dt.timezone.utc)).total_seconds() / 3600
        if age < min_age_h: log(f'{d} t{cc}z: {age:.1f} h old, waiting until {min_age_h} h (still posting)'); continue
        prev = hf_json(f'refs/ffri/{d}/t{cc}z/meta.json')
        if prev and prev.get('n_files', 0) >= len(c['ffri']): log(f'{d} t{cc}z: archived ({prev.get("n_files")} files)'); continue
        todo.append((d, cc, c, age))
    log(f'{len(todo)} cycles to archive; doing at most {max_cycles} (oldest first)')
    done = []
    for d, cc, c, age in todo[:max_cycles]:
        t = time.time(); tmp = tempfile.mkdtemp(prefix='refs_'); arrays = {}; metas = []; window = None; lat = lon = None; nbytes = 0; errors = []
        for fh in sorted(c['ffri']):
            url = c['ffri'][fh]; p = os.path.join(tmp, 'f.grib2')
            try:
                nbytes += download(url, p); window, la, lo, msgs = grib_clip(p, window)
                if lat is None: lat, lon = la, lo
                for j, (m, a) in enumerate(msgs):
                    k = f'f{fh:03d}_m{j:02d}'; arrays[k] = a; metas.append(dict(key=k, fh=fh, url=url, **m))
            except Exception as e:
                errors.append(f'f{fh:03d}: {repr(e)[:200]}'); log('ffri', d, cc, fh, repr(e)[:300])
            time.sleep(0.3)
        if not arrays: note('refs failed', f'{d} t{cc}z: no message decoded; {errors[:3]}'); continue
        buf = io.BytesIO(); np.savez_compressed(buf, lat=lat, lon=lon, **arrays)
        meta = dict(product='NOAA REFS ffri (flash flood and recurrence-interval exceedance probabilities)', date=d, cycle=f'{cc}z', source=c['src'],
                    source_dir=c['base'], n_files=len(c['ffri']), hours=sorted(c['ffri']), n_messages=len(metas), window_ij=window,
                    grid_shape=list(lat.shape), bbox_lonlat=d3_lonlat(), d3_box_26986=D3_BOX, margin_m=MARGIN_M, bytes_downloaded=nbytes,
                    archived_utc=now.strftime('%Y-%m-%dT%H:%MZ'), age_h=round(age, 1), errors=errors, messages=metas,
                    read_back="np.load('ffri_d3.npz'): lat, lon (2-D subgrid) and one 2-D array per message key; messages[] gives each key's GRIB fields")
        files = {f'refs/ffri/{d}/t{cc}z/ffri_d3.npz': buf.getvalue(), f'refs/ffri/{d}/t{cc}z/meta.json': json.dumps(meta, indent=0, default=str).encode()}
        # REFS precipitation (APCP) for District 3, from the first available of pmmn / lpmm / mean / avrg, by byte range when an .idx exists
        q = next((k for k in QPF_PREF if k in c['qpf']), None); qn = 0
        if q:
            qa = {}; qm = []; qwin = None; qerr = []
            for fh in sorted(c['qpf'][q]):
                url = c['qpf'][q][fh]; p = os.path.join(tmp, 'q.grib2')
                try:
                    R = idx_ranges(url)
                    if R:
                        with open(p, 'wb') as f:
                            for s, e, _ in R:
                                r = get(url, headers={'Range': f'bytes={s}-{e}'}, ok=(200, 206), timeout=120)
                                f.write(r.content)
                    elif R is None:
                        h = get(url, method='HEAD', timeout=60)
                        if int(h.headers.get('Content-Length') or 0) > 60 * 2 ** 20: qerr.append(f'f{fh:03d}: no .idx and > 60 MB, skipped'); continue
                        download(url, p, 60)
                    else:
                        continue
                    qwin, la, lo, msgs = grib_clip(p, qwin, keep=lambda m: m['shortName'] in ('tp', 'apcp', 'acpcp') or (m['discipline'] == 0 and m['parameterCategory'] == 1 and m['parameterNumber'] == 8))
                    for j, (m, a) in enumerate(msgs):
                        k = f'f{fh:03d}_m{j:02d}'; qa[k] = a; qm.append(dict(key=k, fh=fh, url=url, **m))
                    if 'lat' not in qa: qa['lat'], qa['lon'] = la, lo
                except Exception as e:
                    qerr.append(f'f{fh:03d}: {repr(e)[:160]}')
                time.sleep(0.3)
            if qm:
                b2 = io.BytesIO(); np.savez_compressed(b2, **qa); qn = len(qm)
                files[f'refs/qpf/{d}/t{cc}z/qpf_d3.npz'] = b2.getvalue()
                files[f'refs/qpf/{d}/t{cc}z/meta.json'] = json.dumps(dict(product=f'NOAA REFS {q} APCP (precipitation)', date=d, cycle=f'{cc}z', source=c['src'],
                                                                        n_files=len(c['qpf'][q]), n_messages=qn, window_ij=qwin, errors=qerr[:20], messages=qm),
                                                                   indent=0, default=str).encode()
            elif qerr: log('qpf errors', qerr[:5])
        hf_put(files, f'refs ffri {d} t{cc}z ({c["src"]})', dry)
        sz = {k.split('/')[-1]: len(v) for k, v in files.items()}
        note(f'refs archived {d} t{cc}z', f"source {c['src']}; ffri files {len(c['ffri'])} (f{min(c['ffri']):03d}-f{max(c['ffri']):03d}), messages {len(metas)}, "
                                          f"grid {lat.shape}, downloaded {nbytes / 2 ** 20:.0f} MB, qpf {q} messages {qn}, sizes {sz}, errors {len(errors)}, "
                                          f"{time.time() - t:.0f} s; first message: {metas[0].get('str', '')[:200]}")
        done.append(f'{d}t{cc}z')
    if not dry:
        for d in dates:
            ls = hf_ls(f'refs/ffri/{d}')
            if ls: note(f'refs on HF {d}', ' '.join(sorted(x.split('/')[-1] for x in ls)))
    return done


# ------------------------------------------------------------------------------------------------ SPoRT-LIS
def sport_times(url, info):
    """Every time step the service offers (epoch ms), from the raster catalog when it has a date field, else the time extent's end."""
    times = set()
    try:
        r = get(url + '/query', params=dict(where='1=1', outFields='*', returnGeometry='false', f='json', resultRecordCount=1000), timeout=120, tries=3).json()
        flds = [f['name'] for f in r.get('fields', []) if f.get('type') == 'esriFieldTypeDate']
        tf = (info.get('timeInfo') or {}).get('startTimeField')
        if tf and tf not in flds: flds.insert(0, tf)
        for f in r.get('features', []):
            a = f.get('attributes', {})
            for k in flds[:1]:
                if isinstance(a.get(k), (int, float)): times.add(int(a[k]))
    except Exception as e:
        log('catalog query', url, repr(e)[:200])
    te = (info.get('timeInfo') or {}).get('timeExtent')
    if te and te[-1]: times.add(int(te[-1]))
    return sorted(times)


def sport_json(url, params):
    """-> (json or None, diagnostic string: HTTP status, content type and the first bytes when the reply is not JSON)."""
    try:
        r = get(url, params=params, timeout=60, tries=3)
        try:
            j = r.json()
            if isinstance(j, dict) and 'error' in j: return None, f"{url}: ArcGIS error {str(j['error'])[:150]}"
            return j, f'{url}: ok'
        except Exception:
            return None, f"{url}: HTTP {r.status_code} {r.headers.get('Content-Type')} {r.text[:200]!r}"
    except Exception as e:
        return None, f'{url}: {repr(e)[:150]}'


def sport_service(lay):
    """The layer's ImageServer: the documented ags03 path, then sibling hosts, then any NRT service whose name contains the layer name.
    -> (url, info, diagnostics)."""
    diag = []
    for h in SPORT_HOSTS:
        url = f'{h}/NRT/{lay}/ImageServer'; j, d = sport_json(url, dict(f='json')); diag.append(d)
        if j and ('extent' in j or 'pixelSizeX' in j): return url, j, diag
    for h in SPORT_HOSTS[:2]:
        j, d = sport_json(f'{h}/NRT', dict(f='json')); diag.append(d)
        for sv in (j or {}).get('services', []):
            if lay.lower() in sv.get('name', '').lower() and sv.get('type') == 'ImageServer':
                url = f"{h}/{sv['name']}/ImageServer"; jj, dd = sport_json(url, dict(f='json')); diag.append(dd)
                if jj: return url, jj, diag
        if j: diag.append('NRT lis services: ' + ' '.join(sv.get('name', '') for sv in j.get('services', []) if 'lis' in sv.get('name', '').lower())[:600])
    return None, None, diag


def sportlis(dry=False, max_steps=60):
    from pyproj import Transformer
    files = {}; summary = {}; folders = set(x.split('/')[-1] for x in hf_ls('sportlis')); LS = {}
    for lay in SPORT_LAYERS:
        url, info, diag = sport_service(lay)
        if info is None:
            summary[lay] = dict(error='service not reachable as JSON', tried=diag); continue
        sr = info.get('spatialReference', {}); wk = sr.get('latestWkid') or sr.get('wkid'); px = float(info.get('pixelSizeX') or 0); py = float(info.get('pixelSizeY') or 0)
        tr = Transformer.from_crs(26986, wk, always_xy=True); x0, y0, x1, y1 = D3_BOX; m = MARGIN_M
        X, Y = np.meshgrid(np.linspace(x0 - m, x1 + m, 21), np.linspace(y0 - m, y1 + m, 21)); bx, by = tr.transform(X.ravel(), Y.ravel())
        bb = [float(bx.min()), float(by.min()), float(bx.max()), float(by.max())]
        if px > 0:      # snap to the service's pixel grid so every pixel is a native cell (nearest neighbour, no resampling)
            ex = info.get('extent', {}); ox, oy = float(ex.get('xmin', 0)), float(ex.get('ymax', 0))
            bb = [ox + np.floor((bb[0] - ox) / px) * px, oy - np.ceil((oy - bb[1]) / py) * py, ox + np.ceil((bb[2] - ox) / px) * px, oy - np.floor((oy - bb[3]) / py) * py]
        w = max(1, int(round((bb[2] - bb[0]) / px))) if px else 64; h = max(1, int(round((bb[3] - bb[1]) / py))) if py else 64
        T = sport_times(url, info); untimed = not T
        if untimed:     # not time-enabled: the current image, keyed by the 6-hourly slot it was fetched in
            n_ = dt.datetime.now(dt.timezone.utc); T = [int(dt.datetime(n_.year, n_.month, n_.day, n_.hour // 6 * 6, tzinfo=dt.timezone.utc).timestamp() * 1000)]
        new = 0; summary[lay] = dict(untimed=untimed, wkid=wk, pixel=[px, py], size=[w, h], times_offered=len(T),
                                                                   first=fmt_ms(T[0]) if T else None, last=fmt_ms(T[-1]) if T else None, archived=[])
        for t in T[-max_steps:]:
            key = fmt_ms(t, '%Y%m%d_%H'); path = f'sportlis/{key}/{lay}.tif'
            if key in folders:
                if key not in LS: LS[key] = set(hf_ls(f'sportlis/{key}'))
                if path in LS[key]: continue
            p = dict(bbox=','.join(f'{v:.3f}' for v in bb), bboxSR=wk, imageSR=wk, size=f'{w},{h}', format='tiff', pixelType='F32',
                     interpolation='RSP_NearestNeighbor', f='image')
            if not untimed: p['time'] = f'{t},{t}'
            try:
                r = get(url + '/exportImage', params=p, timeout=120, tries=4)
                if r.status_code != 200 or not r.content[:4] in (b'II*\x00', b'MM\x00*'):
                    summary[lay].setdefault('errors', []).append(f'{key}: HTTP {r.status_code} {r.content[:120]!r}'); continue
            except Exception as e:
                summary[lay].setdefault('errors', []).append(f'{key}: {repr(e)[:150]}'); continue
            files[path] = r.content; new += 1; summary[lay]['archived'].append(key)
            st = tif_stats(r.content)
            mp = f'sportlis/{key}/meta_{lay}.json'
            files[mp] = json.dumps(dict(layer=lay, service=url, time_ms=t, time_utc=fmt_ms(t, '%Y-%m-%dT%H:%MZ'), request=p, stats=st,
                                        units=info.get('description', '')[:300], service_name=info.get('name'), bands=info.get('bandCount'),
                                        archived_utc=dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%dT%H:%MZ')), indent=0).encode()
            summary[lay]['last_stats'] = st
            time.sleep(0.2)
        summary[lay]['new'] = new
    hf_put(files, f'sportlis: {len([k for k in files if k.endswith(".tif")])} rasters', dry)
    for lay, s in summary.items():
        arch = s.get('archived', []); s2 = dict(s, archived=(arch[:3] + ['...'] + arch[-3:]) if len(arch) > 8 else arch)
        note(f'sportlis {lay}', json.dumps(s2, default=str))
    if not dry:
        ls = sorted(x.split('/')[-1] for x in hf_ls('sportlis')); note('sportlis on HF', f'{len(ls)} time folders: {ls[:3]} ... {ls[-3:]}')
    return summary


def fmt_ms(t, f='%Y-%m-%dT%H:%MZ'):
    return dt.datetime.fromtimestamp(t / 1000, dt.timezone.utc).strftime(f)


def tif_stats(b):
    try:
        import rasterio
        with rasterio.MemoryFile(b) as mf, mf.open() as ds:
            a = ds.read(1, masked=True).astype(float); nd = ds.nodata
            a = np.ma.masked_invalid(a)
            if a.count() == 0: return dict(shape=list(a.shape), valid=0, nodata=nd)
            return dict(shape=list(a.shape), valid=int(a.count()), min=float(a.min()), mean=round(float(a.mean()), 3), max=float(a.max()), nodata=nd, crs=str(ds.crs))
    except Exception as e:
        return dict(error=repr(e)[:150], bytes=len(b))


# ------------------------------------------------------------------------------------------------ MassDOT Stormwater Asset Database
def esri_to_geojson(f, gtype):
    g = f.get('geometry'); geom = None
    if g:
        if 'x' in g: geom = dict(type='Point', coordinates=[g['x'], g['y']])
        elif 'points' in g: geom = dict(type='MultiPoint', coordinates=g['points'])
        elif 'paths' in g: geom = dict(type='MultiLineString', coordinates=g['paths'])
        elif 'rings' in g: geom = dict(type='Polygon' if len(g['rings']) == 1 else 'MultiPolygon', coordinates=g['rings'] if len(g['rings']) == 1 else [[r] for r in g['rings']])
    return dict(type='Feature', properties=f.get('attributes', {}), geometry=geom)


def district_num(v):
    if v is None: return None
    m = re.search(r'\d+', str(v)); return int(m.group()) if m else None


def stormwater(date, dry=False):
    import csv
    svc = get(SW, params=dict(f='json'), timeout=120).json()
    items = [('layer', l) for l in svc.get('layers', [])] + [('table', t) for t in svc.get('tables', [])]
    S = dict(service=SW, snapshot=date, made_utc=dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%dT%H:%MZ'), copyrightText=svc.get('copyrightText'),
             serviceDescription=(svc.get('serviceDescription') or svc.get('description') or '')[:1500], currentVersion=svc.get('currentVersion'),
             spatialReference=svc.get('spatialReference'), layers=[])
    files = {}
    for kind, it in items:
        lid = it['id']; url = f'{SW}/{lid}'; t = time.time()
        try:
            info = get(url, params=dict(f='json'), timeout=120).json()
        except Exception as e:
            S['layers'].append(dict(id=lid, name=it.get('name'), kind=kind, error=repr(e)[:200])); continue
        fields = [dict(name=f['name'], type=f.get('type', '').replace('esriFieldType', ''), alias=f.get('alias')) for f in info.get('fields', [])]
        fn = {f['name'].lower(): f['name'] for f in fields}
        oid = info.get('objectIdField') or next((f['name'] for f in info.get('fields', []) if f.get('type') == 'esriFieldTypeOID'), 'OBJECTID')
        mr = int(info.get('maxRecordCount') or 1000)
        try:
            ids = get(url + '/query', params=dict(where='1=1', returnIdsOnly='true', f='json'), timeout=300).json().get('objectIds') or []
        except Exception as e:
            ids = []; log(lid, 'ids', e)
        ids = sorted(ids); feats = []; geo = kind == 'layer' and info.get('geometryType')
        for i in range(0, len(ids), min(mr, 1000)):
            chunk = ids[i:i + min(mr, 1000)]
            data = dict(objectIds=','.join(map(str, chunk)), outFields='*', returnGeometry='true' if geo else 'false', f='json')
            if geo: data['outSR'] = 4326
            j = get(url + '/query', method='POST', data=data, timeout=300).json()
            if 'error' in j: raise RuntimeError(f"{url}: {j['error']}")
            feats += j.get('features', [])
        name = re.sub(r'[^A-Za-z0-9]+', '_', it.get('name', f'layer{lid}')).strip('_')
        stem = f'massdot_stormwater/{date}/{lid:02d}_{name}'
        cols = [f['name'] for f in fields]
        sio = io.StringIO(); w = csv.writer(sio); w.writerow(cols + (['lon', 'lat'] if geo == 'esriGeometryPoint' else []))
        for f in feats:
            a = f.get('attributes', {}); row = [a.get(c) for c in cols]
            if geo == 'esriGeometryPoint': g = f.get('geometry') or {}; row += [g.get('x'), g.get('y')]
            w.writerow(row)
        files[stem + '.csv.gz'] = gzip.compress(sio.getvalue().encode(), 6, mtime=0)
        if geo:
            gj = dict(type='FeatureCollection', name=it.get('name'), crs=dict(type='name', properties=dict(name='EPSG:4326')),
                      features=[esri_to_geojson(f, geo) for f in feats])
            files[stem + '.geojson.gz'] = gzip.compress(json.dumps(gj, separators=(',', ':')).encode(), 6, mtime=0)
        files[stem + '.layer.json'] = json.dumps(info, indent=0).encode()
        dk = fn.get('district'); tk = fn.get('town') or fn.get('municipality') or fn.get('city')
        by_d = {}; d3_town = {}
        for f in feats:
            a = f.get('attributes', {}); dn = district_num(a.get(dk)) if dk else None; by_d[str(dn)] = by_d.get(str(dn), 0) + 1
            if dn == 3 and tk: tn = str(a.get(tk)).strip().title(); d3_town[tn] = d3_town.get(tn, 0) + 1
        dvals = sorted({str(f.get('attributes', {}).get(dk)) for f in feats[:5000]})[:12] if dk else []
        L = dict(id=lid, kind=kind, name=it.get('name'), geometryType=info.get('geometryType'), count=len(feats), ids=len(ids), maxRecordCount=mr,
                 copyrightText=info.get('copyrightText'), description=(info.get('description') or '')[:400], district_field=dk, town_field=tk,
                 district_values_sample=dvals, by_district=by_d, d3_by_town=dict(sorted(d3_town.items())), fields=fields,
                 relationships=[dict(id=r.get('id'), name=r.get('name'), related=r.get('relatedTableId'), key=r.get('keyField')) for r in info.get('relationships', [])],
                 files=[k.split('/')[-1] for k in files if k.startswith(stem)], bytes=sum(len(v) for k, v in files.items() if k.startswith(stem)))
        S['layers'].append(L); log(f"{kind} {lid} {it.get('name')}: {len(feats)} records ({time.time() - t:.0f} s); D3 {by_d.get('3', 0)}")
    files[f'massdot_stormwater/{date}/summary.json'] = json.dumps(S, indent=0).encode()
    hf_put(files, f'MassDOT Stormwater Asset Database snapshot {date}', dry)
    json.dump(S, open('stormwater_summary.json', 'w'))
    note('stormwater layers', json.dumps([(l['id'], l.get('name'), l.get('count'), l.get('by_district', {}).get('3')) for l in S['layers']]))
    if not dry:
        ls = hf_ls(f'massdot_stormwater/{date}'); note('stormwater on HF', f'{len(ls)} files: ' + ' '.join(sorted(x.split('/')[-1] for x in ls))[:3500])
    raw = gzip.compress(json.dumps(S, separators=(',', ':')).encode(), 9, mtime=0); b = base64.b64encode(raw).decode()
    sha = hashlib.sha256(b.encode()).hexdigest()[:12]; ch = [b[i:i + CHUNK] for i in range(0, len(b), CHUNK)]
    if len(ch) > 40: note('stormwater summary', f'summary too large for annotations ({len(ch)} chunks); read summary.json from HF')
    for i, c in enumerate(ch[:40]): print(f'::notice title=sw {i}/{len(ch)} {sha}::{c}', flush=True)
    return S


def swdecode(run_id, out, repo='Horus331/mass-flood-watch'):
    import subprocess
    gh = lambda p: json.loads(subprocess.run(['gh', 'api', '--paginate', p], capture_output=True, text=True, check=True).stdout.replace('][', ','))
    jobs = gh(f'repos/{repo}/actions/runs/{run_id}/jobs?per_page=100'); jobs = jobs['jobs'] if isinstance(jobs, dict) else [x for j in jobs for x in j['jobs']]
    got = {}; n = sha = None
    for jb in jobs:
        for a in gh(f"repos/{repo}/check-runs/{jb['id']}/annotations?per_page=100"):
            t = a.get('title') or ''
            if t.startswith('sw '):
                i, rest = t[3:].split('/', 1); n_, s_ = rest.split(); n, sha = int(n_), s_; got[int(i)] = a['message']
    b = ''.join(got[i] for i in range(n)) if n and len(got) == n else None
    if not b or hashlib.sha256(b.encode()).hexdigest()[:12] != sha: raise SystemExit(f'incomplete summary ({len(got)}/{n})')
    S = json.loads(gzip.decompress(base64.b64decode(b))); S['transport'] = dict(run_id=int(run_id), sha=sha); json.dump(S, open(out, 'w'), indent=0); return S


def swmd(path, out):
    S = json.load(open(path)); L = S['layers']
    towns = sorted({t for l in L for t in l.get('d3_by_town', {})})
    md = [f"# MassDOT Stormwater Asset Database: snapshot {S['snapshot']}", '',
          f"Source: `{S['service']}` (MassDOT **staging** GIS server; it can change or disappear without notice). Snapshot taken "
          f"{S['made_utc']} by `.github/workflows/stormwater_snapshot.yml` (`proto/archive_feeds.py stormwater`), statewide, every layer and table, "
          f"all fields, geometry in EPSG:4326.", '',
          f"**Copyright / licence (service `copyrightText`, verbatim):** {S.get('copyrightText') or '(empty)'}", '']
    lc = sorted({l.get('copyrightText') for l in L if l.get('copyrightText')})
    if lc: md += ['Layer-level `copyrightText`: ' + ' | '.join(f'"{c}"' for c in lc), '']
    md += [f"**Full copy:** Hugging Face dataset `{REPO}`, folder `massdot_stormwater/{S['snapshot']}/`: per layer `NN_<name>.geojson.gz` "
           "(layers), `NN_<name>.csv.gz` (attributes; points also get lon / lat), `NN_<name>.layer.json` (the layer's REST metadata), and "
           "`summary.json` (this page's numbers). Read back: `huggingface_hub.hf_hub_download('" + REPO + "', 'massdot_stormwater/" + S['snapshot'] +
           "/<file>', repo_type='dataset')`, then `geopandas.read_file` or `pandas.read_csv`.", '',
           '## Layers and tables', '',
           '| id | kind | name | geometry | records statewide | District 3 | District field | Town field |', '|---|---|---|---|---|---|---|---|']
    for l in L:
        md.append(f"| {l['id']} | {l.get('kind')} | {l.get('name')} | {(l.get('geometryType') or '–').replace('esriGeometry', '')} | {l.get('count', l.get('error', '–'))} | "
                  f"{l.get('by_district', {}).get('3', '–') if l.get('district_field') else '–'} | {l.get('district_field') or '–'} | {l.get('town_field') or '–'} |")
    md += ['', 'Records by District (statewide; `None` = no District value):', '']
    for l in L:
        if l.get('by_district'): md.append(f"- {l['id']} {l.get('name')}: " + ', '.join(f'{k}: {v}' for k, v in sorted(l['by_district'].items(), key=lambda x: (x[0] == 'None', x[0]))))
    if towns:
        md += ['', '## District 3: records per town', '', '| town | ' + ' | '.join(f"{l['id']} {l.get('name')}" for l in L if l.get('d3_by_town')) + ' |',
               '|---|' + '---|' * len([l for l in L if l.get('d3_by_town')])]
        for t in towns:
            md.append(f'| {t} | ' + ' | '.join(str(l['d3_by_town'].get(t, 0)) for l in L if l.get('d3_by_town')) + ' |')
    md += ['', '## Fields', '']
    for l in L:
        md.append(f"- **{l['id']} {l.get('name')}** ({len(l.get('fields', []))} fields): " + ', '.join(f"`{f['name']}` ({f['type']})" for f in l.get('fields', [])))
        if l.get('relationships'): md.append(f"  - relationships: {l['relationships']}")
    open(out, 'w').write('\n'.join(md) + '\n'); print(out)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0]); sp = ap.add_subparsers(dest='cmd', required=True)
    p = sp.add_parser('refs'); p.add_argument('--max-cycles', type=int, default=4); p.add_argument('--dates', default=''); p.add_argument('--dry', action='store_true')
    p.add_argument('--min-age-h', type=float, default=6.0)
    p = sp.add_parser('sportlis'); p.add_argument('--dry', action='store_true'); p.add_argument('--max-steps', type=int, default=60)
    p = sp.add_parser('stormwater'); p.add_argument('--date', default=dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%d')); p.add_argument('--dry', action='store_true')
    p = sp.add_parser('swdecode'); p.add_argument('--run', required=True); p.add_argument('--out', required=True)
    p = sp.add_parser('swmd'); p.add_argument('path'); p.add_argument('--out', required=True)
    a = ap.parse_args()
    if a.cmd == 'refs': refs(a.max_cycles, [d for d in a.dates.split(',') if d] or None, a.dry, a.min_age_h)
    elif a.cmd == 'sportlis': sportlis(a.dry, a.max_steps)
    elif a.cmd == 'stormwater': stormwater(a.date, a.dry)
    elif a.cmd == 'swdecode': swdecode(a.run, a.out)
    else: swmd(a.path, a.out)


if __name__ == '__main__':
    main()
