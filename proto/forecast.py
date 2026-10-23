"""Road-closure FORECAST for MassDOT District 3: NOAA HRRR rain -> gate -> (LISFLOOD-FP + prototype.py on the boxes with heavy rain) -> status.

    python proto/forecast.py gate   [--init 2023-09-11T12Z] [--force] --out gate.json [--github-output $GITHUB_OUTPUT]
    python proto/forecast.py status --gate gate.json [--run key=<prototype out dir>[,<flood out dir>] ...] --out docs/site/data/forecast_status.json
    python proto/forecast.py calib  --out docs/proto/forecast/gate_calibration.json          # catalogue storms: HRRR (and MRMS) rain vs the gate
    python proto/forecast.py background --start 2023-06-01 --end 2023-09-30 --out ...      # one 12z cycle a day: how often the gate fires
    python proto/forecast.py selftest

Gate (the cheap step that runs every 6 h): the HRRR hourly rain buckets of one cycle (48 h for 00/06/12/18z) on the native 3 km grid, the
maximum 1 h / 6 h / 24 h running accumulation at every HRRR point, and per District 3 town the maximum over the points inside it (the nearest
point for towns smaller than a cell).  The flood model runs only when a town's 6 h maximum reaches GATE_6H_MM or its 24 h maximum
GATE_24H_MM (thresholds and their derivation: docs/proto/forecast/GATE.md, numbers in gate_calibration.json).  Then up to MAX_BOXES 20 x 20 km
boxes (the validated prototype set-up) are centred on the heaviest forecast rain, greedily, each removing the points it covers.
"""
import os, sys, json, math, argparse, time, datetime as dt
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.normpath(os.path.join(HERE, '..'))
sys.path.insert(0, os.path.join(ROOT, 'sim', 'colab'))
import hrrr_rain  # noqa: E402

D3_BOX = (128000.0, 856000.0, 206000.0, 946000.0)      # EPSG:26986, as proto/turing/run_storm.slurm and sim/colab/lf_domain.py
BOX_KM = 20; MAX_BOXES = int(os.environ.get('FORECAST_MAX_BOXES', '4'))
# Gate thresholds (mm of HRRR forecast rain, maximum over the HRRR points of one District 3 town).  Set from gate_calibration.json: every
# catalogue closure storm whose HRRR forecast was available before the first report must fire it (see GATE.md for the numbers).
GATE_6H_MM = float(os.environ.get('GATE_6H_MM', '25'))
GATE_24H_MM = float(os.environ.get('GATE_24H_MM', '40'))
CLOSE_P = 0.5


def log(*a): print(*a, flush=True)


# ------------------------------------------------------------------ District 3 towns
def d3_towns():
    """[(name, label lon/lat, [rings lon/lat])] for the 73 District 3 towns (docs/towns.json polygons, district from docs/data.json)."""
    B = json.load(open(os.path.join(ROOT, 'docs', 'major.json')))['origin']; OX, OY, Q = B
    D = json.load(open(os.path.join(ROOT, 'docs', 'data.json')))
    names = {f['properties']['name'] for f in D['towns']['features'] if str(f['properties'].get('district')).split('.')[0] == '3'}
    out = []
    for t in json.load(open(os.path.join(ROOT, 'docs', 'towns.json')))['towns']:
        if t['n'] not in names: continue
        rings = []
        for poly in t['p']:
            for ring in poly:
                x = np.cumsum(ring[0::2]) / Q + OX; y = np.cumsum(ring[1::2]) / Q + OY; rings.append(np.c_[x, y])
        out.append((t['n'], t['l'], rings))
    return out


class Gate:
    """HRRR points over District 3 and which town each belongs to."""
    def __init__(self, msg, towns=None):
        from matplotlib.path import Path
        G = hrrr_rain.LccGrid(msg); self.G = G
        towns = towns or d3_towns(); self.towns = towns
        allx = np.concatenate([r[:, 0] for _, _, rr in towns for r in rr]); ally = np.concatenate([r[:, 1] for _, _, rr in towns for r in rr])
        m = (G.lat > ally.min() - 0.08) & (G.lat < ally.max() + 0.08) & (G.lon > allx.min() - 0.08) & (G.lon < allx.max() + 0.08)
        rr_, cc_ = np.nonzero(m); self.r0, self.r1, self.c0, self.c1 = rr_.min(), rr_.max() + 1, cc_.min(), cc_.max() + 1
        la = G.lat[self.r0:self.r1, self.c0:self.c1]; lo = G.lon[self.r0:self.r1, self.c0:self.c1]; self.lat, self.lon = la, lo
        P = np.c_[lo.ravel(), la.ravel()]; self.town_pts = []; inside = np.zeros(len(P), bool)
        for n, lab, rings in towns:
            k = np.zeros(len(P), bool)
            for r in rings: k |= Path(r).contains_points(P)
            idx = np.nonzero(k)[0]
            if not len(idx): idx = np.array([int(np.argmin((P[:, 0] - lab[0]) ** 2 + (P[:, 1] - lab[1]) ** 2))])
            self.town_pts.append(idx); inside[idx] = True
        self.inside = inside
        from pyproj import Transformer
        X, Y = Transformer.from_crs(4326, 26986, always_xy=True).transform(P[:, 0], P[:, 1]); self.X, self.Y = np.asarray(X), np.asarray(Y)

    def cut(self, v): return v[self.r0:self.r1, self.c0:self.c1].ravel()


def running_max(R, w):
    """R (H, n) hourly rain -> (max over windows of w hours (n,), start hour index of that window (n,))."""
    H = R.shape[0]; w = min(w, H)
    C = np.concatenate([np.zeros_like(R[:1]), np.cumsum(R, 0)]); S = C[w:] - C[:-w]
    return S.max(0), S.argmax(0)


def stats(R):
    m1, a1 = running_max(R, 1); m6, a6 = running_max(R, 6); m24, a24 = running_max(R, 24)
    return dict(max1h=m1, max6h=m6, max24h=m24, total=R.sum(0), t6=a6, t24=a24)


def evaluate(init, H, R, gate, force=False):
    """Gate decision + summary from hourly HRRR rain R (H, n points of the gate window)."""
    import pandas as pd
    init = pd.Timestamp(init); S = stats(R); ins = gate.inside
    def iso(h): return (init + pd.Timedelta(hours=int(h))).strftime('%Y-%m-%dT%H:%MZ')
    towns = []
    for (n, lab, _), idx in zip(gate.towns, gate.town_pts):
        k = idx[int(np.argmax(S['max6h'][idx]))]; k24 = idx[int(np.argmax(S['max24h'][idx]))]
        towns.append(dict(town=n.title(), max1h_mm=round(float(S['max1h'][idx].max()), 1), max6h_mm=round(float(S['max6h'][k]), 1),
                          max6h_window=[iso(S['t6'][k]), iso(S['t6'][k] + min(6, H))], max24h_mm=round(float(S['max24h'][k24]), 1),
                          total_mm=round(float(S['total'][idx].max()), 1), mean_total_mm=round(float(S['total'][idx].mean()), 1)))
    towns.sort(key=lambda t: -t['max6h_mm'])
    hit = [t for t in towns if t['max6h_mm'] >= GATE_6H_MM or t['max24h_mm'] >= GATE_24H_MM]
    trig = bool(hit) or force
    # boxes: greedy on the exceedance score over points inside District 3
    score = np.where(ins, np.maximum(S['max6h'] / GATE_6H_MM, S['max24h'] / GATE_24H_MM), 0.0)
    boxes, left = [], score >= (1.0 if hit else 0.0)
    if trig:
        if not hit: left = ins.copy()      # forced with no exceedance: one box on the wettest point
        x0d, y0d, x1d, y1d = D3_BOX; half = BOX_KM * 500.0
        while left.any() and len(boxes) < MAX_BOXES:
            k = int(np.argmax(np.where(left, score, -1)))
            cx = min(max(round(gate.X[k] / 1000) * 1000, x0d + half), x1d - half); cy = min(max(round(gate.Y[k] / 1000) * 1000, y0d + half), y1d - half)
            b = [cx - half, cy - half, cx + half, cy + half]
            inb = (gate.X >= b[0]) & (gate.X < b[2]) & (gate.Y >= b[1]) & (gate.Y < b[3])
            cov = (gate.X >= b[0] - 5000) & (gate.X < b[2] + 5000) & (gate.Y >= b[1] - 5000) & (gate.Y < b[3] + 5000)
            tw = sorted({t['town'] for t, idx in zip([dict(town=n.title()) for n, _, _ in gate.towns], gate.town_pts) if inb[idx].any()})
            boxes.append(dict(id=f'b{len(boxes) + 1}', box=[int(v) for v in b], center_lonlat=[round(float(gate.lon.ravel()[k]), 3), round(float(gate.lat.ravel()[k]), 3)],
                              max6h_mm=round(float(S['max6h'][inb & ins].max()), 1) if (inb & ins).any() else 0.0,
                              max24h_mm=round(float(S['max24h'][inb & ins].max()), 1) if (inb & ins).any() else 0.0,
                              max6h_window=[iso(S['t6'][k]), iso(S['t6'][k] + min(6, H))], towns=tw))
            left &= ~cov
    k6 = int(np.argmax(np.where(ins, S['max6h'], -1)))
    d3 = dict(max1h_mm=round(float(S['max1h'][ins].max()), 1), max6h_mm=round(float(S['max6h'][ins].max()), 1), max24h_mm=round(float(S['max24h'][ins].max()), 1),
              max_total_mm=round(float(S['total'][ins].max()), 1), mean_total_mm=round(float(S['total'][ins].mean()), 1),
              max6h_window=[iso(S['t6'][k6]), iso(S['t6'][k6] + min(6, H))], max6h_lonlat=[round(float(gate.lon.ravel()[k6]), 3), round(float(gate.lat.ravel()[k6]), 3)])
    hr = R[:, ins]
    return dict(issued=init.strftime('%Y-%m-%dT%H:%MZ'), horizon_h=int(H), valid=[iso(0), iso(H)], source='NOAA HRRR (3 km), hourly APCP buckets',
                thresholds=dict(max6h_mm=GATE_6H_MM, max24h_mm=GATE_24H_MM, rule='flood model runs when any District 3 town has a forecast 6 h maximum >= max6h_mm '
                                'or a 24 h maximum >= max24h_mm (maximum over the HRRR 3 km points in the town)', basis='docs/proto/forecast/GATE.md'),
                trigger=trig, forced=bool(force and not hit), towns_over=[t['town'] for t in hit], district=d3, boxes=boxes, towns=towns,
                hourly=dict(t0=iso(0), mean_mm=[round(float(v), 2) for v in hr.mean(1)], max_mm=[round(float(v), 1) for v in hr.max(1)]))


def fetch_gate(init, H):
    """Hourly HRRR rain on the gate window for forecast hours 1..H -> (R (H, n), gate, missing hours)."""
    m1 = hrrr_rain.apcp(init, 1)
    if m1 is None: raise SystemExit(f'HRRR {init} f01 not on AWS')
    g = Gate(m1)
    F = hrrr_rain.hourly(init, H, None, log=log)
    miss = [i + 1 for i, v in enumerate(F) if v is None]
    R = np.stack([g.cut(v) if v is not None else np.zeros(len(g.X), np.float32) for v in F]).astype(np.float32)
    return R, g, miss


def cmd_gate(a):
    if a.init: init = hrrr_rain.parse_init(a.init); H = hrrr_rain.horizon(init)
    else: init, H = hrrr_rain.latest_cycle()
    if init is None: raise SystemExit('no complete HRRR cycle found')
    if a.hours: H = min(H, a.hours)
    log(f'HRRR cycle {init:%Y-%m-%d %H}z, {H} forecast hours')
    t_ = time.time(); R, g, miss = fetch_gate(init, H)
    out = evaluate(init, H, R, g, a.force); out['missing_hours'] = miss; out['fetch_s'] = round(time.time() - t_)
    d = out['district']
    log(f"District 3: max 1 h {d['max1h_mm']} mm, 6 h {d['max6h_mm']} mm ({d['max6h_window'][0]}), 24 h {d['max24h_mm']} mm, total {d['max_total_mm']} mm; "
        f"trigger {out['trigger']} ({', '.join(out['towns_over'][:8]) or 'no town over'}); boxes {[b['box'] for b in out['boxes']]}")
    for t in out['towns'][:8]: log(f"  {t['town']:<18} 6 h {t['max6h_mm']:5.1f}  24 h {t['max24h_mm']:5.1f}  total {t['total_mm']:5.1f}")
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True); json.dump(out, open(a.out, 'w'), indent=1)
    if a.github_output:
        with open(a.github_output, 'a') as f:
            f.write(f"trigger={'true' if out['trigger'] else 'false'}\n")
            f.write('boxes=' + json.dumps([dict(id=b['id'], box=','.join(str(v) for v in b['box'])) for b in out['boxes']]) + '\n')
            f.write(f"init={init:%Y-%m-%dT%H}Z\nhours={H}\n")


# ------------------------------------------------------------------ status for the viewer
def run_summary(key, pdir, fdir=None, box=None):
    """Forecast closures from one prototype run.  Segments already at >= 30 cm in the first hour of the run while the box has had < 2 mm of
    rain are the model's start state (river / pond cells beside the road, channels start a third full), not forecast closures: listed apart."""
    S = json.load(open(os.path.join(pdir, 'summary.json'))); g = json.load(open(os.path.join(pdir, 'segments.geojson')))
    import pandas as pd
    T0 = pd.Timestamp(S['storm_start'].replace('Z', ''))
    def at(h): return (T0 + pd.Timedelta(hours=h)).strftime('%Y-%m-%dT%H:%MZ')
    rain = S.get('rain_hourly_mean_mm') or []; early = 2 if sum(rain[:1]) < 2 else 0
    segs, standing = [], 0
    for f in g['features']:
        q = f['properties']
        if q['p_close'] < CLOSE_P: continue
        d = q.get('d') or []
        if early and len(d) > early and max(d[:early + 1]) >= 30: standing += 1; continue
        k = int(np.argmax(d)) if d else None; f30 = next((i for i, v in enumerate(d) if v >= 30), None)
        segs.append(dict(segment=q['segment'], road=q.get('road') or '', town=q.get('town') or '', road_class=q.get('road_class'), p=round(q['p_close'], 2),
                         peak_depth_m=q.get('peak_depth_m'), first30_h=None if f30 is None else f30 * 0.5, peak_h=None if k is None else k * 0.5,
                         first30=None if f30 is None else at(f30 * 0.5), peak=None if k is None else at(k * 0.5),
                         why=q.get('why') or ''))
    segs.sort(key=lambda s: (-s['p'], -(s['peak_depth_m'] or 0)))
    cls = {}
    for s in segs: cls[s['road_class'] or 'other'] = cls.get(s['road_class'] or 'other', 0) + 1
    towns = {}
    for s in segs: towns[s['town']] = towns.get(s['town'], 0) + 1
    out = dict(key=key, box=box or S.get('box_epsg26986'), viewer=f'data/{key}/', segments_in_box=S.get('segments_in_box'),
               likely_closed=len(segs), likely_closed_km=None, by_class=cls, by_town=dict(sorted(towns.items(), key=lambda kv: -kv[1])),
               standing_water_at_start=standing, may_close=S.get('segments_may_close'), culverts_overtopped=S.get('culverts_overtopped'),
               rain_max_total_mm=S.get('rain_max_total_mm'), rain_peak1h_max_mm=S.get('rain_peak1h_max_mm'),
               flood_model_runtime_s=S.get('flood_model_runtime_s'), solver=S.get('solver'), resolution_m=S.get('resolution_m'), top=segs[:25])
    ids = {s['segment'] for s in segs}
    out['likely_closed_km'] = round(sum((f['properties'].get('length_m') or 0) for f in g['features'] if f['properties']['segment'] in ids) / 1000, 1)
    return out


def cmd_status(a):
    import pandas as pd
    G = json.load(open(a.gate)); runs = []
    for spec in a.run or []:
        key, _, dirs = spec.partition('='); pdir = dirs.split(',')[0]
        box = next((b['box'] for b in G['boxes'] if key.endswith(b['id'])), None)
        try: runs.append(run_summary(key, pdir, box=box))
        except Exception as e: log('run', key, 'unreadable:', repr(e)[:200]); runs.append(dict(key=key, box=box, error=repr(e)[:200]))
    ok = [r for r in runs if 'error' not in r]
    n = sum(r['likely_closed'] for r in ok)
    if not G['trigger']: state, head = 'quiet', f"No road closures expected in District 3 in the next {G['horizon_h']} h"
    elif not ok: state, head = 'error', 'Heavy rain forecast, but the flood model run failed; see the rain summary'
    elif n == 0: state, head = 'run', f"Heavy rain forecast; the flood model expects no road closures in the next {G['horizon_h']} h"
    else: state, head = 'run', f"{n} road segment{'s' if n != 1 else ''} likely closed (P >= {CLOSE_P:.1f}) in the next {G['horizon_h']} h"
    d = G['district']
    out = dict(state=state, headline=head, issued=G['issued'], valid=G['valid'], horizon_h=G['horizon_h'], source=G['source'],
               built=pd.Timestamp.now(tz='UTC').strftime('%Y-%m-%dT%H:%MZ'), gate=dict(thresholds=G['thresholds'], trigger=G['trigger'], forced=G.get('forced', False), towns_over=G['towns_over']),
               rain=dict(district=d, towns=[{k: t[k] for k in ('town', 'max1h_mm', 'max6h_mm', 'max24h_mm', 'total_mm', 'max6h_window')} for t in G['towns']], hourly=G['hourly']),
               boxes=G['boxes'], runs=runs, likely_closed=n,
               method=('Rain: NOAA HRRR forecast (latest 00/06/12/18z cycle, 48 h). Gate: flood model only when a town forecast 6 h / 24 h maximum reaches the '
                       'thresholds. Flood: LISFLOOD-FP 8.2, 20 m, 20 x 20 km boxes on the heaviest rain, NRCS curve-number losses (calibrated on the Sept 2023 '
                       'Leominster storm). Closure: P = Phi((peak depth - 0.30 m) / 0.10 m) along the segment (proto/prototype.py). Hindcast skill: '
                       'docs/proto/forecast/HINDCAST.md.'))
    if a.extra: out.update(json.load(open(a.extra)))
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True); json.dump(out, open(a.out, 'w'), separators=(',', ':'))
    log(f"status {state}: {head}; {len(runs)} run(s)")


# ------------------------------------------------------------------ calibration on the storm catalogue
def cycles_before(t_report, n=3, lag_h=3):
    """The n latest 00/06/12/18z cycles whose 48 h run would have been on the web lag_h hours after issue, before t_report."""
    import pandas as pd
    t = pd.Timestamp(t_report).tz_localize(None) if pd.Timestamp(t_report).tzinfo is None else pd.Timestamp(t_report).tz_convert('UTC').tz_localize(None)
    t = (t - pd.Timedelta(hours=lag_h)).floor('6h'); return [t - pd.Timedelta(hours=6 * k) for k in range(n)]


def mrms_box_stats(ev):
    """MRMS Pass2 hourly (AWS) over the event box, max 1/6/24 h at any 1 km point, and the same for its District 3 window."""
    import pandas as pd, requests, gzip, tempfile, pygrib
    lo0, la0, lo1, la1 = ev['bbox_lonlat']; t0 = pd.Timestamp(ev['t0']).tz_localize(None); R = []
    for h in range(ev['hours']):
        ts = t0 + pd.Timedelta(hours=h + 1)
        u = (f'https://noaa-mrms-pds.s3.amazonaws.com/CONUS/MultiSensor_QPE_01H_Pass2_00.00/{ts:%Y%m%d}/'
             f'MRMS_MultiSensor_QPE_01H_Pass2_00.00_{ts:%Y%m%d-%H%M%S}.grib2.gz')
        r = hrrr_rain._get(u, timeout=120)
        if r is None: continue
        with tempfile.NamedTemporaryFile(suffix='.grib2') as f:
            f.write(gzip.decompress(r.content)); f.flush(); g = pygrib.open(f.name); m = g[1]
            v, la, lo = m.data(lat1=la0, lat2=la1, lon1=lo0 + 360, lon2=lo1 + 360); g.close()
        R.append(np.maximum(np.ma.filled(v, 0), 0).ravel().astype(np.float32))
    if not R: return None
    R = np.stack(R); S = stats(R)
    return dict(hours=len(R), max1h_mm=round(float(S['max1h'].max()), 1), max6h_mm=round(float(S['max6h'].max()), 1), max24h_mm=round(float(S['max24h'].max()), 1),
                max_total_mm=round(float(S['total'].max()), 1))


def cmd_calib(a):
    import pandas as pd
    C = json.load(open(os.path.join(ROOT, 'docs', 'proto', 'obs', 'catalog.json')))['events']
    if a.only: C = [e for e in C if e['id'] in a.only.split(',')]
    gate = None; rows = []
    for ev in C:
        first = ev.get('first_report_utc') or ev['t0']; r = dict(id=ev['id'], area=ev['area'], first_report_utc=first, reports=ev['counts'].get('road_reports_dedup'), cycles=[])
        for init in cycles_before(first, n=a.cycles):
            H = hrrr_rain.horizon(init)
            if init < pd.Timestamp('2014-09-30'): continue
            try:
                m1 = hrrr_rain.apcp(init, 1)
                if m1 is None: r['cycles'].append(dict(init=f'{init:%Y-%m-%dT%H}Z', missing=True)); continue
                if gate is None: gate = Gate(m1)
                F = hrrr_rain.hourly(init, H, None, log=log); miss = sum(v is None for v in F)
                R = np.stack([gate.cut(v) if v is not None else np.zeros(len(gate.X), np.float32) for v in F])
                E = evaluate(init, H, R, gate); d = E['district']
                # the event box alone (HRRR points inside the catalogue box)
                bx = ev['box_26986']; inb = (gate.X >= bx[0]) & (gate.X < bx[2]) & (gate.Y >= bx[1]) & (gate.Y < bx[3]); S = stats(R)
                r['cycles'].append(dict(init=f'{init:%Y-%m-%dT%H}Z', horizon_h=H, lead_h=round((pd.Timestamp(first).tz_localize(None) - init).total_seconds() / 3600, 1) if pd.Timestamp(first).tzinfo is None else round((pd.Timestamp(first).tz_convert('UTC').tz_localize(None) - init).total_seconds() / 3600, 1),
                                        missing_hours=miss, d3_max1h_mm=d['max1h_mm'], d3_max6h_mm=d['max6h_mm'], d3_max24h_mm=d['max24h_mm'], d3_max_total_mm=d['max_total_mm'],
                                        box_max6h_mm=round(float(S['max6h'][inb].max()), 1) if inb.any() else None, box_max24h_mm=round(float(S['max24h'][inb].max()), 1) if inb.any() else None,
                                        top_towns=[(t['town'], t['max6h_mm'], t['max24h_mm']) for t in E['towns'][:5]], fires=E['trigger'], boxes=[b['box'] for b in E['boxes']]))
                log(ev['id'], r['cycles'][-1])
            except Exception as e:
                log(ev['id'], init, 'failed', repr(e)[:200]); r['cycles'].append(dict(init=f'{init:%Y-%m-%dT%H}Z', error=repr(e)[:200]))
        if ev.get('era') == 'aws' and not a.no_mrms:
            try: r['mrms_box'] = mrms_box_stats(ev); log(ev['id'], 'MRMS', r['mrms_box'])
            except Exception as e: r['mrms_box'] = dict(error=repr(e)[:200])
        rows.append(r)
    out = dict(made=pd.Timestamp.now(tz='UTC').strftime('%Y-%m-%dT%H:%MZ'), gate_6h_mm=GATE_6H_MM, gate_24h_mm=GATE_24H_MM,
               note='cycles: the latest 00/06/12/18z HRRR cycles that were on the web (issue + 3 h) before the first flood report; d3_* = maximum over the HRRR '
                    'points inside District 3 towns of the running 1/6/24 h forecast accumulation over the cycle horizon; box_* = the same inside the catalogue '
                    'storm box; mrms_box = observed MRMS Pass2 maxima (1 km) inside the storm box over the catalogue run window', events=rows)
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True); json.dump(out, open(a.out, 'w'), indent=1)


def cmd_background(a):
    """One cycle a day (12z, 24 h): District 3 forecast maxima, and whether a storm report fell in District 3 that local day or the next morning."""
    import pandas as pd
    from concurrent.futures import ThreadPoolExecutor
    days = pd.date_range(a.start, a.end, freq='D'); gate = None; rows = []
    FR = json.load(open(os.path.join(ROOT, 'docs', 'prone', 'flood_reports.json')))['rows']
    from pyproj import Transformer
    tr = Transformer.from_crs(4326, 26986, always_xy=True); rep = {}
    for lon, lat, date, src in FR:
        if src == 'crash': continue
        x, y = tr.transform(lon, lat)
        if D3_BOX[0] <= x < D3_BOX[2] and D3_BOX[1] <= y < D3_BOX[3]: rep[date] = rep.get(date, 0) + 1
    for day in days:
        init = day + pd.Timedelta(hours=a.hour)
        try:
            m1 = hrrr_rain.apcp(init, 1)
            if m1 is None: continue
            if gate is None: gate = Gate(m1)
            F = hrrr_rain.hourly(init, 24, None, workers=16, log=log)
            if sum(v is None for v in F) > 2: continue
            R = np.stack([gate.cut(v) if v is not None else np.zeros(len(gate.X), np.float32) for v in F])
            E = evaluate(init, 24, R, gate); d = E['district']; t6 = max(t['max6h_mm'] for t in E['towns']); t24 = max(t['max24h_mm'] for t in E['towns'])
            loc = (init - pd.Timedelta(hours=4)).strftime('%Y-%m-%d'); nxt = (init + pd.Timedelta(hours=20)).strftime('%Y-%m-%d')
            rows.append(dict(init=f'{init:%Y-%m-%dT%H}Z', d3_max1h_mm=d['max1h_mm'], town_max6h_mm=t6, town_max24h_mm=t24, d3_mean_mm=d['mean_total_mm'],
                             reports=rep.get(loc, 0) + (rep.get(nxt, 0) if nxt != loc else 0)))
            log(rows[-1])
        except Exception as e: log(init, 'failed', repr(e)[:160])
    out = dict(made=pd.Timestamp.now(tz='UTC').strftime('%Y-%m-%dT%H:%MZ'), cycle_hour=a.hour, hours=24,
               note='reports = NWS storm reports + MassDOT D3 reports (docs/prone/flood_reports.json, no crash records) inside the District 3 box on the local day of issue or the next day',
               rows=rows)
    sweep = []
    for t6 in (15, 20, 25, 30, 35, 40, 50):
        for t24 in (30, 40, 50, 60, 80, 999):
            f = [r for r in rows if r['town_max6h_mm'] >= t6 or r['town_max24h_mm'] >= t24]
            ev = [r for r in rows if r['reports'] > 0]
            sweep.append(dict(t6=t6, t24=t24, fires=len(f), fire_share=round(len(f) / max(len(rows), 1), 3),
                              report_days_caught=sum(1 for r in ev if r in f), report_days=len(ev),
                              fires_with_report=sum(1 for r in f if r['reports'] > 0)))
    out['sweep'] = sweep
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True); json.dump(out, open(a.out, 'w'), indent=1)


def selftest():
    """Synthetic HRRR-like grid: town masks, running maxima, gate decision and boxes."""
    class FakeG:
        pass
    towns = [('WORCESTER', [-71.81, 42.27], [np.array([[-71.9, 42.2], [-71.7, 42.2], [-71.7, 42.35], [-71.9, 42.35]])]),
             ('TINY', [-71.5, 42.5], [np.array([[-71.501, 42.499], [-71.499, 42.499], [-71.499, 42.501], [-71.501, 42.501]])])]
    g = Gate.__new__(Gate); g.towns = towns
    lo, la = np.meshgrid(np.arange(-72.0, -71.4, 0.03), np.arange(42.1, 42.6, 0.027)); g.lon, g.lat = lo, la
    from matplotlib.path import Path
    from pyproj import Transformer
    P = np.c_[lo.ravel(), la.ravel()]; g.town_pts = []; g.inside = np.zeros(len(P), bool)
    for n, lab, rings in towns:
        k = np.zeros(len(P), bool)
        for r in rings: k |= Path(r).contains_points(P)
        idx = np.nonzero(k)[0]
        if not len(idx): idx = np.array([int(np.argmin((P[:, 0] - lab[0]) ** 2 + (P[:, 1] - lab[1]) ** 2))])
        g.town_pts.append(idx); g.inside[idx] = True
    X, Y = Transformer.from_crs(4326, 26986, always_xy=True).transform(P[:, 0], P[:, 1]); g.X, g.Y = np.asarray(X), np.asarray(Y)
    H = 48; R = np.zeros((H, len(P)), np.float32)
    assert not evaluate('2026-10-22T12', H, R, g)['trigger'], 'dry must be quiet'
    w = g.town_pts[0][len(g.town_pts[0]) // 2]; R[20:26, w] = 6.0      # 36 mm in 6 h at one Worcester point
    E = evaluate('2026-10-22T12', H, R, g)
    assert E['trigger'] and E['towns'][0]['town'] == 'Worcester' and abs(E['towns'][0]['max6h_mm'] - 36) < 1e-3, E['towns'][0]
    assert E['towns'][0]['max6h_window'] == ['2026-10-23T08:00Z', '2026-10-23T14:00Z'], E['towns'][0]['max6h_window']
    b = E['boxes'][0]['box']; assert b[2] - b[0] == 20000 and b[0] >= D3_BOX[0] and b[2] <= D3_BOX[2] and b[0] <= g.X[w] < b[2] and b[1] <= g.Y[w] < b[3], b
    assert len(g.town_pts[1]) == 1, 'tiny town gets its nearest point'
    m, i = running_max(np.array([[1.0], [5.0], [5.0], [0.0]]), 2); assert m[0] == 10 and i[0] == 1
    print('forecast selftest ok:', E['district'], E['boxes'][0]['box'])


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0]); sp = ap.add_subparsers(dest='cmd')
    p = sp.add_parser('gate'); p.add_argument('--init'); p.add_argument('--hours', type=int); p.add_argument('--force', action='store_true')
    p.add_argument('--out', default='gate.json'); p.add_argument('--github-output')
    p = sp.add_parser('status'); p.add_argument('--gate', required=True); p.add_argument('--run', action='append'); p.add_argument('--extra'); p.add_argument('--out', required=True)
    p = sp.add_parser('calib'); p.add_argument('--out', required=True); p.add_argument('--only'); p.add_argument('--cycles', type=int, default=3); p.add_argument('--no-mrms', action='store_true')
    p = sp.add_parser('background'); p.add_argument('--start', required=True); p.add_argument('--end', required=True); p.add_argument('--hour', type=int, default=12); p.add_argument('--out', required=True)
    sp.add_parser('selftest')
    a = ap.parse_args()
    {'gate': cmd_gate, 'status': cmd_status, 'calib': cmd_calib, 'background': cmd_background, 'selftest': lambda a: selftest()}.get(a.cmd, lambda a: ap.print_help())(a)
