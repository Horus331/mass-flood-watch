"""Radar rain frames for the storm replay (docs/site/data/<run>/rain.png + rain.json).

For each replay run, reads the window (meta.json storm_start, nf * frame_min) and box (meta.json corners plus a
margin, so the rain is seen arriving), fetches NOAA MRMS rain for every STEP minutes of that window from the public
noaa-mrms-pds bucket, crops the native 0.01 degree grid and packs all frames into one PNG atlas:
  frame f -> atlas cell f // 3 (row-major, `cols` cells per row), colour channel f % 3,
  byte v = round(255 * log1p(mm/h) / log1p(MAX)), so the viewer decodes mm/h = expm1(v / 255 * log1p(MAX)).
Source: MRMS PrecipRate (2-min instantaneous radar rate). Storms before 14 Oct 2020 are not in the AWS bucket: PrecipRate is then read
from the IEM mtarchive mirror. If a run still has too many missing PrecipRate times it falls back to the hourly gauge-corrected QPE the
flood model is driven with (AWS MultiSensor QPE Pass2, else IEM Pass2 / GaugeCorr_QPE_01H, as sim/colab/w9_lisflood.py), interpolated in time.
Needs network access to AWS (run by .github/workflows/site_rain.yml):  python3 docs/site/build_rain.py [run ...]
"""
import concurrent.futures as cf
import datetime as dt
import gzip
import json
import math
import os
import sys
import tempfile
import time

import numpy as np
import requests
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, 'data')
BUCKET = 'https://noaa-mrms-pds.s3.amazonaws.com/CONUS/'
STEP = 6            # minutes between rain frames
MAX = 150.0         # mm/h at byte 255
MARGIN = 0.35       # degrees of context around the model box
S = requests.Session()


def get(url, tries=4):
    for k in range(tries):
        try:
            r = S.get(url, timeout=90)
            if r.status_code == 200:
                return r.content
            if r.status_code in (403, 404):
                return None
        except Exception:
            pass
        time.sleep(2 * (k + 1))
    return None


def decode(job):
    """(gzip'd GRIB2, (w, s, e, n)) -> (crop north-to-south in mm/h, cell-edge bounds [[w, s], [e, n]])"""
    import pygrib
    raw, (W, Sth, E, N) = job
    with tempfile.NamedTemporaryFile(suffix='.grib2') as fh:
        fh.write(gzip.decompress(raw)); fh.flush()
        g = pygrib.open(fh.name); m = g[1]
        v = np.ma.filled(m.values, -1).astype(np.float32)
        la1, lo1 = m['latitudeOfFirstGridPointInDegrees'], m['longitudeOfFirstGridPointInDegrees']
        dj, di = m['jDirectionIncrementInDegrees'], m['iDirectionIncrementInDegrees']
        if m['jScansPositively']:
            v = v[::-1]; la1 = la1 + dj * (v.shape[0] - 1)
        g.close()
    if lo1 > 180:
        lo1 -= 360
    i0 = int(math.floor((la1 - N) / dj)); i1 = int(math.ceil((la1 - Sth) / dj)) + 1
    j0 = int(math.floor((W - lo1) / di)); j1 = int(math.ceil((E - lo1) / di)) + 1
    a = v[i0:i1, j0:j1].copy()
    a[a < 0] = 0
    bounds = [[round(lo1 + (j0 - .5) * di, 5), round(la1 - (i1 - .5) * dj, 5)],
              [round(lo1 + (j1 - .5) * di, 5), round(la1 - (i0 - .5) * dj, 5)]]
    return a, bounds


IEM = 'https://mtarchive.geol.iastate.edu/{y}/{m}/{d}/mrms/ncep/{p}/{p}_00.00_{f}.grib2.gz'


def url_iem(p, ts):
    return IEM.format(y=ts.strftime('%Y'), m=ts.strftime('%m'), d=ts.strftime('%d'), p=p, f=ts.strftime('%Y%m%d-%H%M%S'))


def url_rate_iem(ts):
    return url_iem('PrecipRate', ts)


def url_rate(ts):
    return BUCKET + 'PrecipRate_00.00/%s/MRMS_PrecipRate_00.00_%s.grib2.gz' % (ts.strftime('%Y%m%d'), ts.strftime('%Y%m%d-%H%M%S'))


def url_qpe(ts):
    return BUCKET + 'MultiSensor_QPE_01H_Pass2_00.00/%s/MRMS_MultiSensor_QPE_01H_Pass2_00.00_%s.grib2.gz' % (ts.strftime('%Y%m%d'), ts.strftime('%Y%m%d-%H%M%S'))


class Box:
    def __init__(self, corners):
        lo = [c[0] for c in corners]; la = [c[1] for c in corners]
        self.wesn = (min(lo) - MARGIN, min(la) - MARGIN, max(lo) + MARGIN, max(la) + MARGIN)
        self.bounds = None


def fetch_many(urls, box):
    """url -> cropped array (or None); downloads in threads, decodes in processes"""
    out = {}
    with cf.ThreadPoolExecutor(16) as tp:
        raws = dict(zip(urls, tp.map(get, urls)))
    have = [u for u in urls if raws[u]]
    with cf.ProcessPoolExecutor(max(2, os.cpu_count() or 2)) as pp:
        for u, (a, b) in zip(have, pp.map(decode, [(raws[u], box.wesn) for u in have], chunksize=4)):
            out[u] = a
            box.bounds = b
    for u in urls:
        out.setdefault(u, None)
    return out


def build(run):
    d = os.path.join(DATA, run)
    meta = json.load(open(os.path.join(d, 'meta.json')))
    t0 = dt.datetime.strptime(meta['storm_start'], '%Y-%m-%dT%H:%MZ')
    minutes = (meta['nf'] - 1) * meta['frame_min']
    n = minutes // STEP + 1
    times = [t0 + dt.timedelta(minutes=STEP * i) for i in range(n)]
    box = Box(meta['corners'])

    # PrecipRate is every 2 minutes; take the file at each frame time, or its nearest neighbour within 4 min
    want = {}
    for ts in times:
        want[ts] = [ts + dt.timedelta(minutes=o) for o in (0, -2, 2, -4, 4)]
    urls = sorted({url_rate(x) for xs in want.values() for x in xs[:1]})
    got = fetch_many(urls, box)
    frames, missing = [], []
    for ts in times:
        a = got.get(url_rate(ts))
        if a is None:
            alt = [url_rate(x) for x in want[ts][1:]]
            more = fetch_many(alt, box)
            a = next((more[u] for u in alt if more[u] is not None), None)
        if a is None:
            missing.append(ts)
        frames.append(a)
    source = 'NOAA MRMS PrecipRate (radar rain rate, 2-min product, sampled every %d min)' % STEP
    if len(missing) > 0.1 * n:      # pre-Oct-2020 storms: the AWS bucket starts 2020-10-14; the IEM mtarchive mirror has older files
        print(run, 'AWS PrecipRate missing for', len(missing), 'of', n, 'times; trying the IEM mirror')
        alt = {ts: [url_rate_iem(x) for x in want[ts]] for ts in missing}
        got2 = fetch_many(sorted({u[0] for u in alt.values()}), box)
        still = []
        for i, ts in enumerate(times):
            if ts not in alt:
                continue
            a = got2.get(alt[ts][0])
            if a is None:
                more = fetch_many(alt[ts][1:], box)
                a = next((more[u] for u in alt[ts][1:] if more[u] is not None), None)
            if a is None:
                still.append(ts)
            frames[i] = a
        if len(still) < len(missing):
            source = 'NOAA MRMS PrecipRate (radar rain rate, 2-min product, sampled every %d min; %s)' % (
                STEP, 'IEM mtarchive' if len(still) < 0.5 * n else 'AWS + IEM mtarchive')
        missing = still
    if len(missing) > 0.1 * n or all(f is None for f in frames):
        print(run, 'PrecipRate missing for', len(missing), 'of', n, 'times; using hourly QPE')
        hrs = [t0 + dt.timedelta(hours=h) for h in range(0, minutes // 60 + 2)]
        # per hour: AWS Pass2, else IEM Pass2, else IEM GaugeCorr_QPE_01H (the v11 product; what the model reads before Oct 2020)
        chain = [('MultiSensor QPE 1-h Pass 2', url_qpe), ('MultiSensor QPE 1-h Pass 2 (IEM)', lambda h: url_iem('MultiSensor_QPE_01H_Pass2', h)),
                 ('GaugeCorr QPE 1-h (IEM)', lambda h: url_iem('GaugeCorr_QPE_01H', h))]
        Q, used = [None] * len(hrs), set()
        for name, fn in chain:
            need = [k for k in range(len(hrs)) if Q[k] is None]
            if not need:
                break
            q = fetch_many([fn(hrs[k]) for k in need], box)
            for k in need:
                if q[fn(hrs[k])] is not None:
                    Q[k] = q[fn(hrs[k])]; used.add(name)
        # QPE at hour h = rain over (h-1, h], placed at h - 30 min
        ref = next(x for x in Q if x is not None)
        Q = [x if x is not None else np.zeros_like(ref) for x in Q]
        mids = [(h - t0).total_seconds() / 60 - 30 for h in hrs]
        frames = []
        for ts in times:
            m = (ts - t0).total_seconds() / 60
            k = int(np.clip(np.searchsorted(mids, m) - 1, 0, len(mids) - 2))
            w = float(np.clip((m - mids[k]) / 60, 0, 1))
            frames.append((1 - w) * Q[k] + w * Q[k + 1])
        source = 'NOAA MRMS %s, interpolated to %d min' % (' + '.join(n for n, _ in chain if n in used), STEP)
        if any(x is None for x in Q):
            print(run, 'hourly QPE missing for', sum(x is None for x in Q), 'of', len(Q), 'hours (drawn as no rain)')
        missing = []
    else:
        ref = next(f for f in frames if f is not None)
        for i, f in enumerate(frames):     # fill isolated gaps from neighbours
            if f is None:
                prev = next((frames[j] for j in range(i - 1, -1, -1) if frames[j] is not None), ref)
                frames[i] = prev
    shapes = [f.shape for f in frames]
    main = max(set(shapes), key=shapes.count)      # one crop size for the atlas (an archive with a shifted grid would crop differently)
    if any(sh != main for sh in shapes):
        print(run, sum(sh != main for sh in shapes), 'frames with a different grid crop; replaced by their neighbour')
        for i in range(len(frames)):
            if frames[i].shape != main:
                frames[i] = next((frames[j] for j in list(range(i - 1, -1, -1)) + list(range(i + 1, len(frames))) if frames[j].shape == main))
    h, w = frames[0].shape
    cells = (n + 2) // 3
    cols = max(1, min(cells, int(math.ceil(math.sqrt(cells * h / w)))))
    rows = (cells + cols - 1) // cols
    atlas = np.zeros((rows * h, cols * w, 3), np.uint8)
    peak = 0.0
    for f, a in enumerate(frames):
        peak = max(peak, float(a.max()))
        v = np.round(255 * np.log1p(np.clip(a, 0, MAX)) / math.log1p(MAX)).astype(np.uint8)
        c = f // 3; cy, cx = divmod(c, cols)
        atlas[cy * h:(cy + 1) * h, cx * w:(cx + 1) * w, f % 3] = v
    Image.fromarray(atlas, 'RGB').save(os.path.join(d, 'rain.png'), optimize=True)
    info = {'start': t0.strftime('%Y-%m-%dT%H:%MZ'), 'step_min': STEP, 'n': n, 'w': w, 'h': h, 'cols': cols, 'rows': rows,
            'bounds': box.bounds, 'max_mmh': MAX, 'peak_mmh': round(peak, 1), 'source': source,
            'missing': [m.strftime('%Y-%m-%dT%H:%MZ') for m in missing], 'sheet': 'rain.png'}
    json.dump(info, open(os.path.join(d, 'rain.json'), 'w'), separators=(',', ':'))
    print(run, n, 'frames', '%dx%d' % (w, h), 'atlas %dx%d' % (cols * w, rows * h), 'peak %.0f mm/h' % peak, source,
          'missing', len(missing))


if __name__ == '__main__':
    runs = sys.argv[1:] or sorted(r for r in os.listdir(DATA) if os.path.exists(os.path.join(DATA, r, 'meta.json')))
    for r in runs:
        build(r)
