"""Rain timeline for the Forecast tab: observed radar rain for the past 48 h + HRRR forecast rain for the next 48 h over District 3.

    python proto/rain_timeline.py build [--init 2026-11-01T12Z] [--now 2026-11-01T14:00Z] --out <dir>   -> <dir>/rain.json + rain.png
    python proto/rain_timeline.py selftest

One hourly frame per hour from now - 48 h to now + 48 h (97 frames, `now_frame` = 48).  Frame time t = the END of the hour it shows:
frame t is the mean rain rate in mm/h over (t - 1 h, t].
  t <= now   NOAA MRMS hourly QPE stamped t, per hour the best product posted: MultiSensor QPE 01H Pass 2 (gauge-corrected, ~1-2 h latency),
             else Pass 1, else RadarOnly QPE 01H (minutes latency) -- public noaa-mrms-pds bucket, native 0.01 deg grid.
  t >  now   NOAA HRRR 1-h APCP bucket ending at t (forecast hour t - init) of the forecast cycle the gate uses (sim/colab/hrrr_rain.py),
             raw (no neighbourhood), bilinear in the HRRR's Lambert plane onto the MRMS cell centres.  Hours past the cycle's horizon
             (now is ~2-3 h after the cycle's init) are listed in `missing` and drawn as no rain.
Box: the District 3 model box (proto/forecast.py D3_BOX) + 0.35 deg, cropped like docs/site/build_rain.py, so the grid, `bounds`
and atlas packing are those of the replay rain (docs/site/data/d3_sep2023/rain.json): frame f -> cell f // 3, channel f % 3,
byte = round(255 * log1p(mm/h) / log1p(150)).  Never raises for missing data: whatever was fetched is written with `missing`.
Docs: docs/proto/forecast/RAIN_TIMELINE.md.
"""
import os, sys, json, math, argparse, time, datetime as dt
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.normpath(os.path.join(HERE, '..'))
sys.path.insert(0, os.path.join(ROOT, 'sim', 'colab')); sys.path.insert(0, os.path.join(ROOT, 'docs', 'site'))

D3_CORNERS = [(-72.37959865, 42.76126136), (-71.42669753, 42.76458002), (-71.42763044, 41.95433655), (-72.36840497, 41.95105953)]  # D3_BOX in lon/lat
MARGIN = 0.35; MAX = 150.0; PAST_H = 48; FUT_H = 48
MRMS_LA1, MRMS_LO1, MRMS_D = 54.995, -129.995, 0.01       # CONUS MRMS grid: first (NW) cell centre, step
BUCKET = 'https://noaa-mrms-pds.s3.amazonaws.com/CONUS/'
PRODUCTS = [('P2', 'MultiSensor_QPE_01H_Pass2'), ('P1', 'MultiSensor_QPE_01H_Pass1'), ('RO', 'RadarOnly_QPE_01H')]
NAMES = {'P2': 'MultiSensor QPE 1-h Pass 2 (gauge-corrected)', 'P1': 'MultiSensor QPE 1-h Pass 1', 'RO': 'RadarOnly QPE 1-h'}


def log(*a): print(*a, flush=True)
def iso(t): return t.strftime('%Y-%m-%dT%H:%MZ')


def grid():
    """(wesn, i0, i1, j0, j1, bounds, lon centres, lat centres) of the crop -- the same index arithmetic as build_rain.decode."""
    lo = [c[0] for c in D3_CORNERS]; la = [c[1] for c in D3_CORNERS]
    W, S, E, N = min(lo) - MARGIN, min(la) - MARGIN, max(lo) + MARGIN, max(la) + MARGIN
    d = MRMS_D
    i0 = int(math.floor((MRMS_LA1 - N) / d)); i1 = int(math.ceil((MRMS_LA1 - S) / d)) + 1
    j0 = int(math.floor((W - MRMS_LO1) / d)); j1 = int(math.ceil((E - MRMS_LO1) / d)) + 1
    bounds = [[round(MRMS_LO1 + (j0 - .5) * d, 5), round(MRMS_LA1 - (i1 - .5) * d, 5)],
              [round(MRMS_LO1 + (j1 - .5) * d, 5), round(MRMS_LA1 - (i0 - .5) * d, 5)]]
    lons = MRMS_LO1 + np.arange(j0, j1) * d; lats = MRMS_LA1 - np.arange(i0, i1) * d
    return (W, S, E, N), bounds, lons, lats


def mrms_url(prod, t):
    return BUCKET + '%s_00.00/%s/MRMS_%s_00.00_%s.grib2.gz' % (prod, t.strftime('%Y%m%d'), prod, t.strftime('%Y%m%d-%H%M%S'))


def fetch_mrms(times, wesn, shape):
    """{t: (array mm, product code)} for the hours found; per hour the first product of PRODUCTS that is posted."""
    import build_rain
    class B: pass
    box = B(); box.wesn = wesn; box.bounds = None
    out = {}
    for code, prod in PRODUCTS:
        need = [t for t in times if t not in out]
        if not need: break
        try:
            got = build_rain.fetch_many([mrms_url(prod, t) for t in need], box)
        except Exception as e:
            log(f'MRMS {prod} fetch failed: {e!r}'[:200]); continue
        k = 0
        for t in need:
            a = got.get(mrms_url(prod, t))
            if a is not None and a.shape == shape:
                out[t] = (np.clip(a, 0, None).astype(np.float32), code); k += 1
            elif a is not None:
                log(f'MRMS {prod} {iso(t)}: crop {a.shape} != {shape}, skipped')
        log(f'MRMS {prod}: {k} of {len(need)} hours' + (f'; decoded bounds {box.bounds}' if box.bounds else ''))
    return out


def hrrr_sampler(msg, lons, lats):
    """bilinear sampler of an HRRR APCP message at the lon/lat cell centres (2-D, north row first)."""
    import hrrr_rain
    G = hrrr_rain.LccGrid(msg)
    LO, LA = np.meshgrid(lons, lats)
    FI, FJ = G.frac_index(LO.ravel(), LA.ravel())
    ny, nx = G.shape
    i0 = np.clip(np.floor(FI).astype(np.int64), 0, ny - 2); j0 = np.clip(np.floor(FJ).astype(np.int64), 0, nx - 2)
    wi = np.clip(FI - i0, 0, 1).astype(np.float32); wj = np.clip(FJ - j0, 0, 1).astype(np.float32)

    def sample(m):
        v = hrrr_rain.values(m)
        o = v[i0, j0] * (1 - wi) * (1 - wj) + v[i0 + 1, j0] * wi * (1 - wj) + v[i0, j0 + 1] * (1 - wi) * wj + v[i0 + 1, j0 + 1] * wi * wj
        return np.maximum(o, 0).reshape(LO.shape).astype(np.float32)
    return sample


def fetch_hrrr(init, H, lons, lats):
    """[field mm or None] for forecast hours 1..H on the crop grid."""
    import hrrr_rain
    m1 = hrrr_rain.apcp(init, 1)
    if m1 is None:
        log(f'HRRR {init} f01 not on AWS'); return [None] * H
    return hrrr_rain.hourly(init, H, hrrr_sampler(m1, lons, lats), workers=12, log=log)


def pack(frames, out_dir, info):
    """frames: list of (h, w) mm/h arrays -> rain.png atlas + rain.json (build_rain.build's packing)."""
    from PIL import Image
    n = len(frames); h, w = frames[0].shape
    cells = (n + 2) // 3
    cols = max(1, min(cells, int(math.ceil(math.sqrt(cells * h / w))))); rows = (cells + cols - 1) // cols
    atlas = np.zeros((rows * h, cols * w, 3), np.uint8)
    for f, a in enumerate(frames):
        v = np.round(255 * np.log1p(np.clip(a, 0, MAX)) / math.log1p(MAX)).astype(np.uint8)
        c = f // 3; cy, cx = divmod(c, cols)
        atlas[cy * h:(cy + 1) * h, cx * w:(cx + 1) * w, f % 3] = v
    os.makedirs(out_dir, exist_ok=True)
    Image.fromarray(atlas, 'RGB').save(os.path.join(out_dir, 'rain.png'), optimize=True)
    info.update(n=n, w=w, h=h, cols=cols, rows=rows, max_mmh=MAX, sheet='rain.png')
    json.dump(info, open(os.path.join(out_dir, 'rain.json'), 'w'), separators=(',', ':'))
    return atlas


def build(init=None, now=None, out='rain_out'):
    import pandas as pd
    import hrrr_rain
    t_ = time.time()
    H = 0
    try:
        if init is None: init, H = hrrr_rain.latest_cycle()
        else: init = hrrr_rain.parse_init(init); H = hrrr_rain.horizon(init)
    except Exception as e:
        log(f'HRRR cycle lookup failed: {e!r}'[:200]); init = None
    wall = pd.Timestamp.now(tz='UTC').tz_localize(None).floor('h')
    if now is not None: now = hrrr_rain.parse_init(now).floor('h')
    elif init is not None and wall - init > pd.Timedelta(hours=8): now = init      # a dispatched hindcast cycle: 'now' = its issue time
    else: now = wall
    now = now.to_pydatetime(); init_py = init.to_pydatetime() if init is not None else None
    wesn, bounds, lons, lats = grid(); shape = (len(lats), len(lons))
    times = [now + dt.timedelta(hours=k) for k in range(-PAST_H, FUT_H + 1)]
    past = [t for t in times if t <= now]; fut = [t for t in times if t > now]
    log(f'rain timeline: now {iso(now)}, HRRR {iso(init_py) if init_py else "none"} ({H} h), grid {shape[1]}x{shape[0]} {bounds}')

    try: M = fetch_mrms(past, wesn, shape)
    except Exception as e: log(f'MRMS failed: {e!r}'[:200]); M = {}
    F = [None] * H
    if init_py is not None and H:
        try: F = fetch_hrrr(init, H, lons, lats)
        except Exception as e: log(f'HRRR failed: {e!r}'[:200]); F = [None] * H

    frames, src, missing = [], [], []
    zero = np.zeros(shape, np.float32)
    for t in times:
        a, s = None, '-'
        if t <= now:
            if t in M: a, s = M[t]
        elif init_py is not None:
            fh = int(round((t - init_py).total_seconds() / 3600))
            if 1 <= fh <= H and F[fh - 1] is not None: a, s = F[fh - 1], 'HRRR'
        if a is None: missing.append(iso(t)); a = zero
        frames.append(a); src.append(s)
    pk = [float(a.max()) for a in frames]; k_now = PAST_H
    cnt = {c: src[:k_now + 1].count(c) for c, _ in PRODUCTS}
    past_source = 'NOAA MRMS hourly QPE (noaa-mrms-pds), per hour the best product posted: ' + ', '.join(
        f'{NAMES[c]} {cnt[c]} h' for c, _ in PRODUCTS if cnt[c]) if any(cnt.values()) else 'NOAA MRMS hourly QPE: none fetched'
    nf = src[k_now + 1:].count('HRRR')
    future_source = (f'NOAA HRRR 3 km, cycle {iso(init_py)} ({H} h), hourly APCP buckets, raw (no neighbourhood), bilinear to the 0.01 deg grid; '
                     f'{nf} of {FUT_H} h' if init_py else 'NOAA HRRR: no cycle found')
    info = dict(start=iso(times[0]), step_min=60, bounds=bounds, peak_mmh=round(max(pk), 1),
                source=f'past 48 h: {past_source}; next 48 h: {future_source}',
                now=iso(now), now_frame=k_now, past_n=k_now + 1, future_n=FUT_H, past_source=past_source, future_source=future_source,
                hrrr_init=iso(init_py) if init_py else None, hrrr_horizon_h=int(H),
                frame_means='mean rain rate (mm/h) over the hour ENDING at the frame time; frames <= now observed (MRMS), > now forecast (HRRR)',
                frame_src=src, past_peak_mmh=round(max(pk[:k_now + 1]), 1), future_peak_mmh=round(max(pk[k_now + 1:]), 1),
                frame_peak_mmh=[round(p, 1) for p in pk],
                district_mean_mm=dict(past48h=round(float(sum(a.mean() for a in frames[1:k_now + 1])), 1),
                                      next48h=round(float(sum(a.mean() for a in frames[k_now + 1:])), 1)),
                missing=missing, built=iso(dt.datetime.utcnow()), build_s=round(time.time() - t_))
    pack(frames, out, info)
    sz = os.path.getsize(os.path.join(out, 'rain.png'))
    log(f"rain timeline -> {out}: {len(frames)} frames {shape[1]}x{shape[0]}, atlas {info['cols']}x{info['rows']} cells, png {sz / 1e6:.2f} MB; "
        f"peak past {info['past_peak_mmh']} / next {info['future_peak_mmh']} mm/h; missing {len(missing)}; {past_source}; {future_source}")
    return info


def selftest():
    """packing round trip on a synthetic field (no network)."""
    import tempfile
    from PIL import Image
    wesn, bounds, lons, lats = grid(); shape = (len(lats), len(lons))
    assert bounds == [[-72.74, 41.59], [-71.07, 43.12]] and shape == (153, 167), (bounds, shape)     # = docs/site/data/d3_sep2023/rain.json
    fr = [np.full(shape, v, np.float32) for v in np.linspace(0, 120, 97)]
    with tempfile.TemporaryDirectory() as d:
        info = dict(start='x'); pack(fr, d, info)
        A = np.asarray(Image.open(os.path.join(d, 'rain.png')))
        for f in (0, 1, 2, 47, 48, 96):
            c = f // 3; cy, cx = divmod(c, info['cols'])
            v = A[cy * info['h'] + 5, cx * info['w'] + 5, f % 3]
            mm = math.expm1(v / 255 * math.log1p(MAX)); want = float(fr[f][0, 0])
            assert abs(mm - want) <= 0.03 * want + 0.02, (f, mm, want)
    print('selftest ok', info['cols'], info['rows'])


if __name__ == '__main__':
    ap = argparse.ArgumentParser(); sp = ap.add_subparsers(dest='cmd', required=True)
    b = sp.add_parser('build'); b.add_argument('--init', default=''); b.add_argument('--now', default=''); b.add_argument('--out', required=True)
    sp.add_parser('selftest')
    a = ap.parse_args()
    if a.cmd == 'selftest': selftest()
    else: build(a.init or None, a.now or None, a.out)
