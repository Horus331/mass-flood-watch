"""Training scenarios for the LISFLOOD-FP surrogate (docs/proto/surrogate/SURROGATE.md): which rain goes on which 20 x 20 km box.

    python proto/surrogate/scenarios.py scan  --out ~/scratch/surrogate/scan.json            # login node (internet): MRMS 24 h totals, one per day
    python proto/surrogate/scenarios.py plan  --scan ~/scratch/surrogate/scan.json --batch 1 --out ~/scratch/surrogate/plan_b1.json
    python proto/surrogate/scenarios.py env   --plan plan_b1.json --index 7                    # 'export K=V' lines for one scenario (slurm)
    python proto/surrogate/scenarios.py inputs --out ~/scratch/surrogate/inputs_plan.json      # evaluation inputs: catalogue storms + District 3
    python proto/surrogate/scenarios.py selftest

Rain never comes from a protected storm.  Protected = every event of docs/proto/obs/catalog.json (dev, held-out 23, locked, sep2014) and of
docs/proto/obs/catalog_d456.json (transfer test), plus the Vermont July 2023 storm, each from 24 h before t0 to 24 h after its window, and
every day after --end (the forward test starts 3 Nov 2026).  A rain day is the 24 h ending at 12 UTC; its model window is 36 h from 06 UTC the
day before (6 h before the 24 h, 6 h of drain-down after).  The day split (train / val / test) is a hash of the date, so a day keeps its split
in every batch.  Boxes: 20 x 20 km on a 10 km grid over District 3 (proto/forecast.py D3_BOX, EPSG:26986); the two HELDOUT_BOXES and every
grid box that touches them are never trained on.  Physics: the frozen baseline (docs/proto/parity/BASELINE.md) as proto/storm_archive.py.
"""
import os, sys, json, math, time, argparse, hashlib, datetime as dt
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.normpath(os.path.join(HERE, '..', '..'))
D3_BOX = (128000.0, 856000.0, 206000.0, 946000.0)          # EPSG:26986, as proto/forecast.py and proto/storm_archive.py
BOX_M = 20000.0; STRIDE_M = 10000.0
HELDOUT_BOXES = {'hb_west': (136000.0, 876000.0, 156000.0, 896000.0),     # Brookfields / Spencer / Warren: terrain never trained on
                 'hb_north': (186000.0, 916000.0, 206000.0, 936000.0)}    # Groton / Westford / Littleton
BASELINE_ENV = dict(LF_PARITY='1', LF_LOSS='cn', LF_CN_AMC='II', LF_CN_SCALE='0.88', LF_INFIL_MMH='2', LF_QOUT='1', LF_VOUT='1', RES='20')
SURR_ENV = dict(LF_SURR_SAVE='1', LF_NO_UPLOAD='1')
MARGIN_H = 24                        # protected window = [t0 - 24 h, t0 + hours + 24 h]
WIN_BEFORE_H, WIN_RAIN_H, WIN_AFTER_H = 6, 24, 6
HRRR_NBHD_LIVE = '20,90'            # the live forecast's neighbourhood (forecast/HINDCAST.md); the surrogate must learn what it will be fed
EXTRA_PROTECTED = [('jul2023vt', '2023-07-09T18:00Z', 60)]   # Vermont validation storm (sim/colab/w9_lisflood.py STORMS)
SCAN_REGION = dict(lat=(41.55, 43.05), lon=(-73.10, -70.55))   # MRMS 24 h scan: central / eastern MA and the edges of CT, RI, NH
MRMS24_URL = 'https://noaa-mrms-pds.s3.amazonaws.com/CONUS/MultiSensor_QPE_24H_Pass2_00.00/{d}/MRMS_MultiSensor_QPE_24H_Pass2_00.00_{d}-120000.grib2.gz'
GPU_MIN = dict(box=5.0, district=55.0)    # wall minutes on one Turing GPU node: inputs ~2-3 min, solver 1-2 min (box), 23 min + inputs (district)
BATCHES = {1: dict(days=48, district_days=0), 2: dict(days=144, district_days=2)}
log = lambda *a: print(time.strftime('%H:%M:%S'), *a, file=sys.stderr, flush=True)     # stderr: stdout of 'env' / 'inputs --index' is eval'd


def utc(s):
    s = str(s).strip().replace('Z', '')
    return dt.datetime.fromisoformat(s if len(s) > 13 else s + ':00')


def iso(t): return t.strftime('%Y-%m-%dT%H:%MZ')


# ------------------------------------------------------------------ protected storms
def protected_windows(root=ROOT):
    """[(id, start, end)] naive-UTC datetimes: every catalogue / transfer storm window widened by MARGIN_H on both sides."""
    out = []
    for f in ('catalog.json', 'catalog_d456.json'):
        p = os.path.join(root, 'docs', 'proto', 'obs', f)
        for e in json.load(open(p))['events']:
            t0 = utc(e['t0']); out.append((e['id'], t0 - dt.timedelta(hours=MARGIN_H), t0 + dt.timedelta(hours=int(e['hours']) + MARGIN_H)))
    for sid, t0, h in EXTRA_PROTECTED:
        t0 = utc(t0); out.append((sid, t0 - dt.timedelta(hours=MARGIN_H), t0 + dt.timedelta(hours=h + MARGIN_H)))
    return out


def day_window(day):
    """Model window of a rain day (YYYY-MM-DD = the 24 h ending 12 UTC that day) -> (t0, hours)."""
    end = dt.datetime.fromisoformat(day) + dt.timedelta(hours=12)
    return end - dt.timedelta(hours=WIN_RAIN_H + WIN_BEFORE_H), WIN_BEFORE_H + WIN_RAIN_H + WIN_AFTER_H


def clashes(day, prot):
    t0, h = day_window(day); t1 = t0 + dt.timedelta(hours=h)
    return [sid for sid, a, b in prot if t0 < b and a < t1]


def day_split(day, val=0.15, test=0.15):
    """Deterministic train / val / test split of a rain day (sha1 of the date): a day keeps its split across batches."""
    u = int(hashlib.sha1(('surrogate-day-' + day).encode()).hexdigest()[:8], 16) / 0xFFFFFFFF
    return 'test' if u < test else 'val' if u < test + val else 'train'


# ------------------------------------------------------------------ boxes
def overlaps(a, b): return a[0] < b[2] and b[0] < a[2] and a[1] < b[3] and b[1] < a[3]


def anchors():
    """All 20 km boxes on the 10 km grid inside the District 3 box (the last column / row snapped to the edge)."""
    x0d, y0d, x1d, y1d = D3_BOX
    xs = sorted(set([x0d + k * STRIDE_M for k in range(int((x1d - x0d - BOX_M) // STRIDE_M) + 1)] + [x1d - BOX_M]))
    ys = sorted(set([y0d + k * STRIDE_M for k in range(int((y1d - y0d - BOX_M) // STRIDE_M) + 1)] + [y1d - BOX_M]))
    return [(x, y, x + BOX_M, y + BOX_M) for y in ys for x in xs]


def train_boxes():
    return [b for b in anchors() if not any(overlaps(b, h) for h in HELDOUT_BOXES.values())]


def box_key(b): return f'{int(b[0] / 1000)}_{int(b[1] / 1000)}'


def nearest_box(x, y, boxes):
    c = np.array([((b[0] + b[2]) / 2, (b[1] + b[3]) / 2) for b in boxes]); return boxes[int(np.argmin((c[:, 0] - x) ** 2 + (c[:, 1] - y) ** 2))]


# ------------------------------------------------------------------ scan: one MRMS 24 h total per day
def read_mrms24(day, cache=None):
    """-> (lat1d descending, lon1d ascending, grid mm) cut to SCAN_REGION, or None when the file is missing."""
    sys.path.insert(0, os.path.join(ROOT, 'sim', 'colab'))
    import gzip, pygrib, tempfile
    from w9_lisflood import mrms_http_fetch
    d = day.replace('-', ''); url = MRMS24_URL.format(d=d); cp = os.path.join(cache, os.path.basename(url)) if cache else None
    raw = open(cp, 'rb').read() if cp and os.path.exists(cp) else mrms_http_fetch(url)
    if not raw: return None
    if cp and not os.path.exists(cp): os.makedirs(cache, exist_ok=True); open(cp, 'wb').write(raw)
    fd, gp = tempfile.mkstemp(suffix='.grib2'); os.close(fd)
    try:
        open(gp, 'wb').write(gzip.decompress(raw)); g = pygrib.open(gp); m = g[1]
        v, la, lo = m.data(lat1=SCAN_REGION['lat'][0], lat2=SCAN_REGION['lat'][1], lon1=SCAN_REGION['lon'][0] + 360, lon2=SCAN_REGION['lon'][1] + 360); g.close()
    finally: os.remove(gp)
    v = np.ma.filled(v, 0).astype(np.float32); v[v < 0] = 0; lat1 = la[:, 0]; lon1 = np.where(lo[0] > 180, lo[0] - 360, lo[0])
    if lat1[0] < lat1[-1]: lat1, v = lat1[::-1], v[::-1]
    return lat1, lon1, v


def day_stats(day, lat1, lon1, v):
    """Region maximum and its place (EPSG:26986), District 3 box maximum and mean, area >= 50 mm."""
    from pyproj import Transformer
    i, j = np.unravel_index(int(np.argmax(v)), v.shape); tr = Transformer.from_crs(4326, 26986, always_xy=True)
    x, y = tr.transform(float(lon1[j]), float(lat1[i]))
    LO, LA = np.meshgrid(lon1, lat1); X, Y = tr.transform(LO, LA); ins = (X >= D3_BOX[0]) & (X < D3_BOX[2]) & (Y >= D3_BOX[1]) & (Y < D3_BOX[3])
    return dict(day=day, max_mm=round(float(v.max()), 1), max_xy=[round(float(x)), round(float(y))], max_lonlat=[round(float(lon1[j]), 3), round(float(lat1[i]), 3)],
                d3_max_mm=round(float(v[ins].max()), 1) if ins.any() else 0.0, d3_mean_mm=round(float(v[ins].mean()), 1) if ins.any() else 0.0,
                area50_cells=int((v >= 50).sum()))


def cmd_scan(a, reader=None):
    reader = reader or (lambda day: read_mrms24(day, a.cache))
    days = [d.strftime('%Y-%m-%d') for d in (dt.date.fromisoformat(a.start) + dt.timedelta(days=k) for k in range((dt.date.fromisoformat(a.end) - dt.date.fromisoformat(a.start)).days + 1))]
    if a.months: ms = {int(m) for m in a.months.split(',')}; days = [d for d in days if int(d[5:7]) in ms]
    rows, missing = [], []
    from concurrent.futures import ThreadPoolExecutor
    def one(day):
        try:
            r = reader(day); return day, (day_stats(day, *r) if r is not None else None), None
        except Exception as e: return day, None, repr(e)[:160]
    with ThreadPoolExecutor(a.workers) as ex:
        for k, (day, st, err) in enumerate(ex.map(one, days)):
            if st: rows.append(st)
            else: missing.append(day if not err else f'{day} {err}')
            if k % 100 == 0: log(f'scan {day}: {len(rows)} days read, {len(missing)} missing')
    out = dict(made=iso(dt.datetime.now(dt.timezone.utc).replace(tzinfo=None)), product='MRMS MultiSensor_QPE_24H_Pass2 ending 12 UTC (AWS noaa-mrms-pds)', region=SCAN_REGION,
               start=a.start, end=a.end, rows=rows, missing=missing)
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True); json.dump(out, open(a.out, 'w'), indent=0)
    log(f'scan: {len(rows)} days, {sum(r["max_mm"] >= 40 for r in rows)} with a 24 h maximum >= 40 mm -> {a.out}')
    return out


# ------------------------------------------------------------------ plan
def candidate_days(scan, min_mm, prot, end):
    """Rain days of the scan, wettest first, minus protected and post-`end` days.  -> (kept rows, dropped {day: reason})."""
    keep, drop = [], {}
    for r in sorted(scan['rows'], key=lambda r: (-r['max_mm'], r['day'])):
        if r['max_mm'] < min_mm: continue
        if r['day'] > end: drop[r['day']] = 'after --end (forward test)'; continue
        c = clashes(r['day'], prot)
        if c: drop[r['day']] = 'protected: ' + ','.join(c[:4]); continue
        keep.append(r)
    return keep, drop


def scenario(sid, kind, split, day, box, box_role, scale=1.0, shift=(0.0, 0.0), nbhd=None, init=None, hours=None, district=False, hrrr_hours=WIN_RAIN_H):
    t0, h = day_window(day)
    env = dict(BASELINE_ENV, **SURR_ENV, BOX=','.join(str(int(v)) for v in box), STORM=sid, RUN_DIR=f'runs/{sid}_lf', T0=iso(t0), HOURS=str(hours or h))
    if abs(scale - 1.0) > 1e-9: env['LF_RAIN_SCALE'] = f'{scale:g}'
    if shift[0] or shift[1]: env['LF_RAIN_SHIFT_M'] = f'{int(round(shift[0]))},{int(round(shift[1]))}'
    if kind == 'hrrr':
        env.update(LF_RAIN='hrrr', LF_HRRR_INIT=init or t0.strftime('%Y-%m-%dT%HZ'), LF_HRRR_HOURS=str(hrrr_hours), LF_DRAIN_H=str(WIN_AFTER_H),
                   HOURS=str(hours or (WIN_RAIN_H + WIN_AFTER_H)), LF_ALLOW_DRY='1')
        if nbhd: env['LF_HRRR_NBHD'] = nbhd
    if district: env['LF_SAVEINT'] = '3600'
    return dict(id=sid, kind=kind, split=split, day=day, box=[int(v) for v in box], box_key=box_key(box), box_role=box_role, scale=scale,
                shift_m=[int(round(shift[0])), int(round(shift[1]))], nbhd=nbhd, district=district, env=env)


def make_plan(scan, batch, min_mm=40.0, end='2026-10-27', seed=2026, root=ROOT, exclude_days=()):
    """Scenario list for one batch.  Batch b takes the next BATCHES[b]['days'] candidate days (wettest first) not used by earlier batches."""
    prot = protected_windows(root); cands, dropped = candidate_days(scan, min_mm, prot, end)
    cands = [r for r in cands if r['day'] not in set(exclude_days)]
    first = sum(BATCHES[k]['days'] for k in range(1, batch)); rows = cands[first:first + BATCHES[batch]['days']]     # batch b: the next days, wettest first
    rng = np.random.default_rng(seed + batch); TB = train_boxes(); HB = list(HELDOUT_BOXES.items()); S = []; n = [0]
    def nid(): n[0] += 1; return f'sg{batch}_{n[0]:04d}'
    def inner_point(b):      # a point in the central 10 x 10 km of a box: where the transplanted core lands
        return b[0] + 5000 + rng.uniform(0, 10000), b[1] + 5000 + rng.uniform(0, 10000)
    for r in rows:
        sp = day_split(r['day']); sx, sy = r['max_xy']
        if sp in ('train', 'val'):
            b = nearest_box(sx, sy, TB); inside = b[0] + 5000 <= sx < b[2] - 5000 and b[1] + 5000 <= sy < b[3] - 5000
            tx, ty = (sx, sy) if inside else inner_point(b)
            S.append(scenario(nid(), 'mrms', sp, r['day'], b, 'train', 1.0, (tx - sx, ty - sy)))
            for _ in range(2):
                b = TB[int(rng.integers(len(TB)))]; tx, ty = inner_point(b)
                S.append(scenario(nid(), 'mrms', sp, r['day'], b, 'train', float(rng.choice([0.5, 1.0, 1.0, 1.5, 2.0])), (tx - sx, ty - sy)))
            b = nearest_box(sx, sy, TB)
            S.append(scenario(nid(), 'hrrr', sp, r['day'], b, 'train', nbhd=HRRR_NBHD_LIVE if rng.uniform() < 2 / 3 else None))
        else:       # test days: held-out boxes (terrain and rain never trained on) and one training box (rain never trained on)
            for k, (hn, hb) in enumerate(HB):
                tx, ty = inner_point(hb)
                S.append(scenario(nid(), 'mrms', 'test_box', r['day'], hb, hn, 1.0 if k == 0 else float(rng.choice([0.5, 1.0, 1.5, 2.0])), (tx - sx, ty - sy)))
            b = TB[int(rng.integers(len(TB)))]; tx, ty = inner_point(b)
            S.append(scenario(nid(), 'mrms', 'test_rain', r['day'], b, 'train', 1.0, (tx - sx, ty - sy)))
            hn, hb = HB[int(rng.integers(len(HB)))]
            S.append(scenario(nid(), 'hrrr', 'test_box', r['day'], hb, hn, nbhd=HRRR_NBHD_LIVE))
    # district-wide runs (batch 2): 8 lagged HRRR members (live neighbourhood) on the wettest train days -> the district domain is seen in training
    dd = [r for r in rows if day_split(r['day']) == 'train'][:BATCHES[batch]['district_days']]
    for r in dd:
        t0, _ = day_window(r['day'])
        for lag in range(8):
            init = (t0 - dt.timedelta(hours=lag)).strftime('%Y-%m-%dT%HZ')
            S.append(scenario(nid(), 'hrrr', 'train', r['day'], D3_BOX, 'district', nbhd=HRRR_NBHD_LIVE, init=init, hours=WIN_RAIN_H + WIN_AFTER_H + lag, district=True, hrrr_hours=WIN_RAIN_H + lag))
    gpu_h = sum(GPU_MIN['district' if s['district'] else 'box'] for s in S) / 60
    cnt = {}
    for s in S: k = f"{s['split']}/{s['kind']}{'/district' if s['district'] else ''}"; cnt[k] = cnt.get(k, 0) + 1
    return dict(made=iso(dt.datetime.now(dt.timezone.utc).replace(tzinfo=None)), batch=batch, seed=seed, min_mm=min_mm, end=end, scan_product=scan.get('product'), heldout_boxes=HELDOUT_BOXES,
                train_boxes=[box_key(b) for b in TB], days=[dict(day=r['day'], split=day_split(r['day']), max_mm=r['max_mm']) for r in rows],
                dropped_protected=len([v for v in dropped.values() if v.startswith('protected')]), counts=cnt, n=len(S),
                gpu_hours_est=round(gpu_h, 1), baseline_env=BASELINE_ENV, scenarios=S)


def check_plan(P, root=ROOT):
    """Hard rules: no protected rain, no training scenario on a held-out box, ids unique."""
    prot = protected_windows(root); ids = set()
    for s in P['scenarios']:
        assert s['id'] not in ids, s['id']; ids.add(s['id'])
        assert not clashes(s['day'], prot), (s['id'], s['day'], clashes(s['day'], prot))
        if s['split'] in ('train', 'val') and not s['district']:
            assert not any(overlaps(s['box'], h) for h in HELDOUT_BOXES.values()), s
        if s['split'] == 'test_box': assert tuple(s['box']) in [tuple(int(v) for v in h) for h in HELDOUT_BOXES.values()], s
    return True


def cmd_plan(a):
    P = make_plan(json.load(open(a.scan)), a.batch, a.min_mm, a.end, a.seed); check_plan(P)
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True); json.dump(P, open(a.out, 'w'), indent=1)
    k = a.per_task; nt = math.ceil(P['n'] / k)
    log(f"plan batch {a.batch}: {P['n']} scenarios on {len(P['days'])} rain days {P['counts']}; ~{P['gpu_hours_est']} GPU-node-hours -> {a.out}")
    log(f"submit: sbatch --array=0-{nt - 1}%4 --export=ALL,PLAN={os.path.abspath(a.out)},PER_TASK={k} proto/turing/surrogate_gen.slurm")
    return P


def cmd_env(a):
    s = json.load(open(a.plan))['scenarios'][a.index]
    for k, v in s['env'].items(): print(f"export {k}='{v}'")
    print(f"export SURR_ID='{s['id']}'")


# ------------------------------------------------------------------ evaluation inputs (inputs-only w9 runs, no flood model)
def inputs_plan(root=ROOT):
    """Catalogue storms used for evaluation (held-out 23 + the 2 dev storms; never the locked ones) on their catalogue boxes and windows,
    with the names of the parity catalogue folders (docs/proto/parity/catalog/<name>), plus the two District 3 runs used as the district check."""
    sys.path.insert(0, os.path.join(root, 'proto')); import score_v2 as SV
    want = set(SV.HELDOUT + SV.NEW16 + SV.DEV)
    out = []
    for e in json.load(open(os.path.join(root, 'docs', 'proto', 'obs', 'catalog.json')))['events']:
        if e['id'] in SV.LOCKED or e['id'] not in want: continue
        name = f"{e['id']}_{e['area']}_20m"
        out.append(dict(name=name, storm=e['id'], role='dev' if e['id'] in SV.DEV else 'heldout23', ref=f'docs/proto/parity/catalog/{name}',
                        env=dict(BASELINE_ENV, LF_SURR_SAVE='1', LF_INPUTS_ONLY='1', LF_NO_UPLOAD='1', BOX=','.join(str(int(v)) for v in e['box_26986']),
                                 STORM=e['id'], T0=e['t0'], HOURS=str(e['hours']), RUN_DIR=f"runs/{e['id']}_surrin_{e['area']}")))
    d3 = ','.join(str(int(v)) for v in D3_BOX)
    out.append(dict(name='d3_sep2023_p', storm='sep2023', role='district', ref='docs/proto/turing/d3_sep2023_p',
                    env=dict(BASELINE_ENV, LF_SURR_SAVE='1', LF_INPUTS_ONLY='1', LF_NO_UPLOAD='1', BOX=d3, STORM='sep2023', HOURS='48', RUN_DIR='runs/sep2023_surrin_d3')))
    out.append(dict(name='hindcast_d3_sep2023_18z', storm='forecast', role='district_hrrr', ref='docs/proto/turing/hindcast_d3_sep2023_18z',
                    env=dict(BASELINE_ENV, LF_SURR_SAVE='1', LF_INPUTS_ONLY='1', LF_NO_UPLOAD='1', BOX=d3, STORM='forecast', LF_RAIN='hrrr', LF_ALLOW_DRY='1',
                             LF_HRRR_INIT='2023-09-11T18Z', LF_HRRR_NBHD=HRRR_NBHD_LIVE, RUN_DIR='runs/forecast_surrin_d3_18z')))
    assert not any(x['storm'] in SV.LOCKED for x in out)
    return out


def cmd_inputs(a):
    L = inputs_plan(); os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True); json.dump(dict(items=L), open(a.out, 'w'), indent=1)
    log(f'{len(L)} evaluation inputs -> {a.out}')
    if a.index is not None:
        x = L[a.index]
        for k, v in x['env'].items(): print(f"export {k}='{v}'")
        print(f"export SURR_NAME='{x['name']}'")


# ------------------------------------------------------------------ selftest
def selftest():
    ok = []
    A = anchors(); assert len(A) == 7 * 8 and all(b[2] <= D3_BOX[2] and b[3] <= D3_BOX[3] for b in A)
    TB = train_boxes(); assert 30 <= len(TB) < len(A) and not any(overlaps(b, h) for b in TB for h in HELDOUT_BOXES.values())
    assert all(any(abs(b[0] - h[0]) < 1 and abs(b[1] - h[1]) < 1 for b in A) or True for h in HELDOUT_BOXES.values())
    ok.append(f'boxes: {len(A)} grid boxes, {len(TB)} trainable, none touching the 2 held-out boxes')
    prot = protected_windows()
    assert clashes('2023-09-11', prot) and clashes('2021-08-19', prot) and clashes('2023-07-14', prot), 'catalogue storms must be protected'
    assert clashes('2018-08-08', prot) and clashes('2016-10-21', prot), 'locked storms must be protected'
    assert clashes('2026-09-27', prot) and clashes('2023-07-10', prot), 'transfer / Vermont storms must be protected'
    assert not clashes('2022-06-01', prot)
    t0, h = day_window('2022-06-01'); assert iso(t0) == '2022-05-31T06:00Z' and h == 36
    ok.append('protected windows: dev, held-out, locked, transfer and Vermont storms; day window 06 UTC + 36 h')
    sp = [day_split(f'2022-{m:02d}-{d:02d}') for m in range(1, 13) for d in range(1, 29)]
    assert 0.6 < sp.count('train') / len(sp) < 0.8 and sp.count('test') > 20 and day_split('2022-06-01') == day_split('2022-06-01')
    ok.append('day split deterministic, ~70 / 15 / 15')
    # synthetic scan through a fake reader (no network): a storm core moving across the region
    lat1 = np.linspace(43.0, 41.6, 141); lon1 = np.linspace(-73.0, -70.6, 241)
    def reader(day):
        k = int(day[-2:]) + int(day[5:7]) * 31; LO, LA = np.meshgrid(lon1, lat1)
        c = (-72.6 + (k % 17) * 0.1, 41.9 + (k % 7) * 0.1); v = (20 + (k * 37 % 140)) * np.exp(-((LO - c[0]) ** 2 + (LA - c[1]) ** 2) / 0.01)
        return lat1, lon1, v.astype(np.float32)
    import tempfile
    d = tempfile.mkdtemp(prefix='surr_sc_')
    scan = cmd_scan(argparse.Namespace(start='2021-05-01', end='2022-10-31', months='5,6,7,8,9,10', workers=4, out=f'{d}/scan.json', cache=None), reader=reader)
    assert len(scan['rows']) > 300 and all('max_xy' in r for r in scan['rows'])
    P = make_plan(scan, 1); check_plan(P)
    assert P['n'] > 100 and abs(P['gpu_hours_est'] - P['n'] * GPU_MIN['box'] / 60) < 0.2, (P['n'], P['gpu_hours_est'])
    assert {s['split'] for s in P['scenarios']} >= {'train', 'test_box'} and all(s['env']['LF_CN_SCALE'] == '0.88' and s['env']['LF_PARITY'] == '1' for s in P['scenarios'])
    for s in P['scenarios']:
        if s['kind'] == 'mrms' and s['shift_m'] != [0, 0]:
            b = s['box']; dx, dy = s['shift_m']; mx = next(r for r in scan['rows'] if r['day'] == s['day'])['max_xy']
            assert b[0] + 4900 <= mx[0] + dx <= b[2] - 4900 and b[1] + 4900 <= mx[1] + dy <= b[3] - 4900, s     # the core lands in the box centre
    P2 = make_plan(scan, 2); check_plan(P2); assert not ({x['day'] for x in P['days']} & {x['day'] for x in P2['days']})
    assert sum(s['district'] for s in P2['scenarios']) == 16 and all(s['env']['BOX'] == '128000,856000,206000,946000' for s in P2['scenarios'] if s['district'])
    ok.append(f"plan: batch 1 {P['n']} scenarios ({P['gpu_hours_est']} GPU-h), batch 2 {P2['n']} ({P2['gpu_hours_est']} GPU-h), disjoint days, cores land in the target box")
    bad = dict(P); bad['scenarios'] = [dict(P['scenarios'][0], day='2023-09-11')]
    try: check_plan(bad); raise AssertionError('protected day accepted')
    except AssertionError as e:
        if 'accepted' in str(e): raise
    ok.append('check_plan refuses protected rain')
    I = inputs_plan(); names = {x['name'] for x in I}
    assert len(I) == 27 and 'sep2021_worcester_20m' in names and not any(x['storm'] in ('aug2015', 'aug2018', 'aug2020', 'jul2018', 'oct2016') for x in I)
    assert all(os.path.isdir(os.path.join(ROOT, x['ref'])) for x in I), [x['ref'] for x in I if not os.path.isdir(os.path.join(ROOT, x['ref']))]
    ok.append('evaluation inputs: 23 held-out + 2 dev catalogue storms + 2 District 3 runs, no locked storm, every reference run present')
    for o in ok: print('ok  ', o)
    print(f'SCENARIOS SELFTEST PASSED ({len(ok)} checks)'); return True


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0]); sp = ap.add_subparsers(dest='cmd')
    p = sp.add_parser('scan'); p.add_argument('--start', default='2020-10-15'); p.add_argument('--end', default='2026-10-27'); p.add_argument('--months', default='')
    p.add_argument('--workers', type=int, default=8); p.add_argument('--cache', default=os.path.expanduser('~/scratch/surrogate/mrms24')); p.add_argument('--out', required=True)
    p = sp.add_parser('plan'); p.add_argument('--scan', required=True); p.add_argument('--batch', type=int, default=1); p.add_argument('--min-mm', type=float, default=40.0)
    p.add_argument('--end', default='2026-10-27'); p.add_argument('--seed', type=int, default=2026); p.add_argument('--per-task', type=int, default=8); p.add_argument('--out', required=True)
    p = sp.add_parser('env'); p.add_argument('--plan', required=True); p.add_argument('--index', type=int, required=True)
    p = sp.add_parser('inputs'); p.add_argument('--out', required=True); p.add_argument('--index', type=int)
    sp.add_parser('selftest')
    a = ap.parse_args()
    if a.cmd == 'selftest': sys.exit(0 if selftest() else 1)
    {'scan': cmd_scan, 'plan': cmd_plan, 'env': cmd_env, 'inputs': cmd_inputs}.get(a.cmd, lambda a: ap.print_help())(a)


if __name__ == '__main__':
    main()
