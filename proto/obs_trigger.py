"""Observed-rain trigger test (docs/proto/forecast/OBS_TRIGGER_PREREG.md, frozen 24 Nov 2026 before any number was computed).

    python proto/obs_trigger.py scan --start 2023-06-01T00:00Z --end 2023-07-01T00:00Z --out scan_jun.json   # 30-min steps: does R fire?
    python proto/obs_trigger.py storms --out storms.json [--calib-extra calib_extra.json]                      # M1 timing + M2 placement
    python proto/obs_trigger.py report --storms storms.json --scans scan_*.json --out docs/proto/forecast/obs_trigger.json

R fires when, inside the District 3 box (proto/live_feeds.py LAT/LON), MRMS FLASH QPE_FFGMAX >= 1.0 (stored in percent: >= 100) or
RadarOnly QPE 1 h >= 25 mm, in at least 4 cells.  R boxes: up to four 20 x 20 km boxes on the highest RadarOnly QPE 3 h, placed as the HRRR
gate places them (proto/forecast.py evaluate: centre on the maximum rounded to 1 km, clamped to D3_BOX, retire the box + 5 km).
Nothing here changes the live forecast.
"""
import os, sys, re, json, argparse, datetime as dt, concurrent.futures as cf
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); sys.path.insert(0, HERE)
import live_feeds as LF

FFG = 'FLASH_QPE_FFGMAX_00.00'; Q1 = 'RadarOnly_QPE_01H_00.00'; Q3 = 'RadarOnly_QPE_03H_00.00'
FFG_PCT, Q1_MM, MIN_CELLS = 100.0, 25.0, 4
STORMS = ['jul2021', 'jul2021b', 'aug2021', 'sep2021', 'sep2022', 'jul2023', 'jul2023b', 'jul2023c', 'jul2023d', 'aug2023', 'aug2023b', 'sep2023', 'aug2026']
D3_BOX = (128000.0, 856000.0, 206000.0, 946000.0); BOX_KM = 20; MAX_BOXES = 4
LOG = LF.log


def tparse(s): return dt.datetime.strptime(s.rstrip('Z')[:16], '%Y-%m-%dT%H:%M')
def iso(t): return t.strftime('%Y-%m-%dT%H:%MZ')


_lists = {}
def files(product, day):
    """{valid time: url} for one product and UTC day (cached)."""
    k = (product, day)
    if k not in _lists:
        pre = f'CONUS/{product}/{day:%Y%m%d}/'; d = {}
        for key in LF.s3_list(LF.MRMS, pre):
            m = re.search(r'_(\d{8}-\d{6})\.grib2\.gz$', key)
            if m: d[dt.datetime.strptime(m.group(1), '%Y%m%d-%H%M%S')] = f'{LF.MRMS}/{key}'
        _lists[k] = d
    return _lists[k]


def nearest(product, t, tol_min=10):
    """URL of the file valid at or just before t (within tol), else None."""
    best = None
    for day in {t.date(), (t - dt.timedelta(minutes=tol_min)).date()}:
        for v, u in files(product, dt.datetime.combine(day, dt.time())).items():
            if t - dt.timedelta(minutes=tol_min) <= v <= t and (best is None or v > best[0]): best = (v, u)
    return best


def grid(product, t):
    b = nearest(product, t, 70 if product == Q3 else 10)   # the 3 h radar total is published hourly (execution fix, 25 Nov: 10 min missed it)
    if not b: return None
    V, la, lo = LF.mrms_box(b[1]); return b[0], np.nan_to_num(V, nan=0.0), la, lo


def fires_at(t):
    """(fires?, why, n_ffg_cells, n_q1_cells, available) at time t."""
    out = dict(t=iso(t))
    g = grid(FFG, t); q = grid(Q1, t)
    out['ffg_cells'] = int((g[1] >= FFG_PCT).sum()) if g else None
    out['q1_cells'] = int((q[1] >= Q1_MM).sum()) if q else None
    out['ffg_max_pct'] = float(g[1].max()) if g else None; out['q1_max_mm'] = round(float(q[1].max()), 1) if q else None
    out['fires'] = bool((out['ffg_cells'] or 0) >= MIN_CELLS or (out['q1_cells'] or 0) >= MIN_CELLS)
    out['available'] = dict(ffg=g is not None, q1=q is not None)
    return out


def r_boxes(t):
    """R boxes on the RadarOnly 3 h rain at t (EPSG:26986), as proto/forecast.py places the HRRR boxes."""
    from pyproj import Transformer
    g = grid(Q3, t)
    if not g: return None
    _, V, la, lo = g; LO, LA = np.meshgrid(lo, la); X, Y = Transformer.from_crs(4326, 26986, always_xy=True).transform(LO, LA)
    X, Y, S = X.ravel(), Y.ravel(), V.ravel()
    x0d, y0d, x1d, y1d = D3_BOX; half = BOX_KM * 500.0
    left = (X >= x0d) & (X < x1d) & (Y >= y0d) & (Y < y1d) & (S > 0); boxes = []
    while left.any() and len(boxes) < MAX_BOXES:
        k = int(np.argmax(np.where(left, S, -1)))
        cx = min(max(round(X[k] / 1000) * 1000, x0d + half), x1d - half); cy = min(max(round(Y[k] / 1000) * 1000, y0d + half), y1d - half)
        b = [int(cx - half), int(cy - half), int(cx + half), int(cy + half)]
        if b not in boxes: boxes.append(b)
        cov = (X >= b[0] - 5000) & (X < b[2] + 5000) & (Y >= b[1] - 5000) & (Y < b[3] + 5000)
        left &= ~(cov | (np.hypot(X - X[k], Y - Y[k]) < half + 5000))
    return dict(t3=iso(g[0]), max3h_mm=round(float(S.max()), 1), boxes=boxes)


def steps(a, b, minutes=30):
    t = a
    while t <= b: yield t; t += dt.timedelta(minutes=minutes)


# ------------------------------------------------------------------------------------------------ scan (false-trigger background)
def cmd_scan(a):
    T = list(steps(tparse(a.start), tparse(a.end) - dt.timedelta(minutes=30)))
    with cf.ThreadPoolExecutor(a.workers) as ex: R = list(ex.map(fires_at, T))
    json.dump(dict(made=iso(LF.utcnow()), prereg='docs/proto/forecast/OBS_TRIGGER_PREREG.md', start=a.start, end=a.end, steps=R), open(a.out, 'w'))
    LOG('scan', a.start, a.end, 'steps', len(R), 'fires', sum(r['fires'] for r in R), 'missing', sum(not all(r['available'].values()) for r in R))


# ------------------------------------------------------------------------------------------------ storms (M1 timing, M2 placement)
def reports_for(first):
    """District 3 flood reports (docs/prone/flood_reports.json) on the local date of the first report and the next day."""
    from pyproj import Transformer
    R = json.load(open(os.path.join(ROOT, 'docs', 'prone', 'flood_reports.json')))
    loc = first - dt.timedelta(hours=4)   # EDT (all storms are in summer)
    days = {loc.date().isoformat(), (loc.date() + dt.timedelta(days=1)).isoformat()}
    pts = [(r[0], r[1]) for r in R['rows'] if r[2] in days and LF.LON[0] <= r[0] <= LF.LON[1] and LF.LAT[0] <= r[1] <= LF.LAT[1]]
    if not pts: return []
    X, Y = Transformer.from_crs(4326, 26986, always_xy=True).transform([p[0] for p in pts], [p[1] for p in pts])
    return list(zip(X, Y))


def inside(pts, boxes): return sum(any(b[0] <= x < b[2] and b[1] <= y < b[3] for b in boxes) for x, y in pts)


def cmd_storms(a):
    C = {e['id']: e for e in json.load(open(os.path.join(ROOT, 'docs', 'proto', 'obs', 'catalog.json')))['events']}
    G = {e['id']: e for e in json.load(open(os.path.join(ROOT, 'docs', 'proto', 'forecast', 'gate_calibration.json')))['events']}
    if a.calib_extra and os.path.exists(a.calib_extra): G.update({e['id']: e for e in json.load(open(a.calib_extra))['events']})
    out = {}
    for s in STORMS:
        ev = C[s]; g = G.get(s) or {}
        first = tparse(g.get('first_report_utc') or ev['first_report_utc'])
        t0 = tparse(ev['t0']); a0 = min(t0, first) - dt.timedelta(hours=6); a1 = first + dt.timedelta(hours=3)
        T = list(steps(a0.replace(minute=(a0.minute // 30) * 30), a1))
        with cf.ThreadPoolExecutor(a.workers) as ex: R = list(ex.map(fires_at, T))
        f = next((r for r in R if r['fires']), None)
        rec = dict(first_report=iso(first), window=[iso(T[0]), iso(T[-1])], steps=len(R), missing=sum(not all(r['available'].values()) for r in R),
                   first_fire=f and f['t'], why=f and dict(ffg_cells=f['ffg_cells'], q1_cells=f['q1_cells'], ffg_max_pct=f['ffg_max_pct'], q1_max_mm=f['q1_max_mm']))
        rec['lead_min'] = round((first - tparse(f['t'])).total_seconds() / 60) if f else None
        rec['in_time'] = bool(f and rec['lead_min'] >= 30)
        pts = reports_for(first); rec['reports'] = len(pts)
        cyc = (g.get('cycles') or [{}])[0]; hb = cyc.get('boxes') or []
        rec['hrrr'] = dict(init=cyc.get('init'), fires=cyc.get('fires'), boxes=hb, reports_inside=inside(pts, hb))
        if f:
            rb = r_boxes(tparse(f['t'])); rec['r'] = dict(rb or {}, reports_inside=inside(pts, (rb or {}).get('boxes') or []))
        else: rec['r'] = dict(boxes=[], reports_inside=0)
        out[s] = rec; LOG(s, json.dumps({k: v for k, v in rec.items() if k not in ('hrrr', 'r')}), 'hrrr', rec['hrrr']['reports_inside'], 'r', rec['r']['reports_inside'], 'of', len(pts))
    json.dump(dict(made=iso(LF.utcnow()), prereg='docs/proto/forecast/OBS_TRIGGER_PREREG.md', storms=out), open(a.out, 'w'), indent=1)


# ------------------------------------------------------------------------------------------------ report (pass rule, as frozen)
def cmd_report(a):
    S = json.load(open(a.storms))['storms']; steps_ = []
    for p in a.scans: steps_ += json.load(open(p))['steps']
    R = json.load(open(os.path.join(ROOT, 'docs', 'proto', 'forecast', 'gate_background_2023-06-01.json')))
    rep = {}
    for r in R['rows']: rep[r['init'][:10]] = r['reports']    # reports on the local day of issue or the next day (gate_background note)
    def local_day(t): return (tparse(t) - dt.timedelta(hours=4)).date().isoformat()
    fire_days = sorted({local_day(s['t']) for s in steps_ if s['fires']})
    false_days = [d for d in fire_days if not rep.get(d)]
    in_time = sum(v['in_time'] for v in S.values())
    tot = sum(v['reports'] for v in S.values()); r_in = sum(v['r']['reports_inside'] for v in S.values()); h_in = sum(v['hrrr']['reports_inside'] for v in S.values())
    pr = lambda n: round(100.0 * n / tot, 1) if tot else None
    c1 = in_time >= 10; c2 = tot > 0 and pr(r_in) - pr(h_in) >= 10; c3 = len(false_days) <= 14
    res = dict(made=iso(LF.utcnow()), prereg='docs/proto/forecast/OBS_TRIGGER_PREREG.md',
               M1=dict(in_time=in_time, of=len(S), median_lead_min=float(np.median([v['lead_min'] for v in S.values() if v['lead_min'] is not None])) if any(v['lead_min'] is not None for v in S.values()) else None, pass_=c1),
               M2=dict(reports=tot, inside_r_boxes=r_in, inside_hrrr_boxes=h_in, pct_r=pr(r_in), pct_hrrr=pr(h_in), pass_=bool(c2)),
               M3=dict(steps=len(steps_), missing=sum(not all(s['available'].values()) for s in steps_), fire_days=len(fire_days), false_days=len(false_days), false_day_list=false_days, pass_=c3),
               verdict='pass' if (c1 and c2 and c3) else 'fail', storms=S)
    json.dump(res, open(a.out, 'w'), indent=1); LOG(json.dumps({k: res[k] for k in ('M1', 'M2', 'verdict')}), 'M3', {k: v for k, v in res['M3'].items() if k != 'false_day_list'})


if __name__ == '__main__':
    ap = argparse.ArgumentParser(); sp = ap.add_subparsers(dest='cmd')
    p = sp.add_parser('scan'); p.add_argument('--start', required=True); p.add_argument('--end', required=True); p.add_argument('--out', required=True); p.add_argument('--workers', type=int, default=16)
    p = sp.add_parser('storms'); p.add_argument('--out', required=True); p.add_argument('--calib-extra'); p.add_argument('--workers', type=int, default=16)
    p = sp.add_parser('report'); p.add_argument('--storms', required=True); p.add_argument('--scans', nargs='+', required=True); p.add_argument('--out', required=True)
    a = ap.parse_args(); {'scan': cmd_scan, 'storms': cmd_storms, 'report': cmd_report}.get(a.cmd, lambda a: ap.print_help())(a)
