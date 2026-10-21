"""Check a run against point observations of road flooding: was there water where and when people reported it?

    python proto/validate_points.py --run-dir <w9 out dir> --out points.json
        [--lsr docs/proto/obs/lsr_sep2023.csv] [--stormevents docs/proto/obs/stormevents_sep2023.csv] [--labels proto/data/labels_sep2023_leominster.csv]

For every observation inside the run box (road/flood types only), using the 30-min depth frames (frames_cm.npz):
  hit_10 / hit_30   any cell within R m (100 m; 300 m for town-level coordinates) reached 10 / 30 cm during the storm
  wet_by_report     that depth was already there at the report time (+ 1 h tolerance): did the model flood the place in time?
  lead_h            report time minus the first time 30 cm was reached nearby (positive = model was early)
Baseline: the same statistics at 2,000 random road points, so a hit rate means something only above that ("any-day" rate).
Times: LSR VALID is UTC; Storm Events BEGIN_DATE_TIME is local standard time (EST, UTC-5); labels time_local is EDT (UTC-4).
"""
import os, csv, json, argparse, datetime as dt
import numpy as np

UTC = dt.timezone.utc

def parse_obs(lsr=None, se=None, labels=None):
    obs = []
    if lsr and os.path.exists(lsr):
        for r in csv.DictReader(open(lsr)):
            ty = (r.get('TYPETEXT') or '').upper()
            if 'FLOOD' not in ty: continue
            t = dt.datetime.strptime(r['VALID'], '%Y%m%d%H%M').replace(tzinfo=UTC)
            obs.append(dict(src='LSR', lon=float(r['LON']), lat=float(r['LAT']), t=t, text=(r.get('REMARK') or '')[:120], radius=300.0))   # LSR points are rounded to 0.01 deg
    if se and os.path.exists(se):
        for r in csv.DictReader(open(se)):
            if not r.get('BEGIN_LAT'): continue
            t = dt.datetime.strptime(r['BEGIN_DATE_TIME'], '%d-%b-%y %H:%M:%S').replace(tzinfo=dt.timezone(dt.timedelta(hours=-5)))
            obs.append(dict(src='StormEvents', lon=float(r['BEGIN_LON']), lat=float(r['BEGIN_LAT']), t=t.astimezone(UTC), text=r['EVENT_NARRATIVE'][:120], radius=150.0))
    if labels and os.path.exists(labels):
        for r in csv.DictReader(open(labels)):
            try: lon, lat = float(r['lon']), float(r['lat'])
            except Exception: continue
            t = None
            if r.get('time_local'):
                for fmt in ('%Y-%m-%d %H:%M', '%Y-%m-%dT%H:%M', '%Y-%m-%d'):
                    try: t = dt.datetime.strptime(r['time_local'][:16], fmt).replace(tzinfo=dt.timezone(dt.timedelta(hours=-4))).astimezone(UTC); break
                    except Exception: pass
            q = r.get('coord_quality', 'approx')
            obs.append(dict(src='labels:' + r.get('type', ''), lon=lon, lat=lat, t=t, text=r.get('name', '')[:120], radius=100.0 if q == 'exact' else 300.0 if q == 'approx' else 1000.0))
    return obs

def run(run_dir, obs, seed=0):
    from pyproj import Transformer
    meta = json.load(open(os.path.join(run_dir, 'meta.json'))); x0, y0, x1, y1 = meta['box']; res = meta['res_m']
    F = np.load(os.path.join(run_dir, 'frames_cm.npz')); D = F['depth_cm']; hrs = F['hours']
    WM = np.load(os.path.join(run_dir, 'watermask.npy')).astype(bool) if os.path.exists(os.path.join(run_dir, 'watermask.npy')) else np.zeros(D.shape[1:], bool)
    t0 = dt.datetime.fromisoformat(meta['t0'].replace('Z', '+00:00')); tr = Transformer.from_crs(4326, 26986, always_xy=True)
    def at(x, y, radius, t=None):
        r, c = int((y1 - y) // res), int((x - x0) // res); k = max(1, int(np.ceil(radius / res)))
        sl = (slice(None), slice(max(0, r - k), r + k + 1), slice(max(0, c - k), c + k + 1))
        w = np.where(WM[sl[1:]], 0, D[sl]).reshape(len(D), -1).max(axis=1) / 100.0
        f30 = np.nonzero(w >= 0.3)[0]; first30 = t0 + dt.timedelta(hours=float(hrs[f30[0]])) if len(f30) else None
        res_ = dict(max_m=round(float(w.max()), 2), hit_10=bool(w.max() >= 0.1), hit_30=bool(w.max() >= 0.3), first30=first30.strftime('%Y-%m-%dT%H:%MZ') if first30 else None)
        if t is not None:
            j = int(np.searchsorted(hrs, (t - t0).total_seconds() / 3600 + 1.0, side='right')) - 1
            res_['wet_by_report'] = bool(j >= 0 and w[:j + 1].max() >= 0.1)
            res_['lead_h'] = round((t - first30).total_seconds() / 3600, 1) if first30 else None
        return res_
    rows = []
    for o in obs:
        x, y = tr.transform(o['lon'], o['lat'])
        if not (x0 <= x < x1 and y0 <= y < y1): continue
        rows.append(dict(src=o['src'], lon=o['lon'], lat=o['lat'], t=o['t'].strftime('%Y-%m-%dT%H:%MZ') if o['t'] else None, text=o['text'], radius=o['radius'], **at(x, y, o['radius'], o['t'])))
    # random-road-point baseline at the observations' radii
    S = json.load(open(os.path.join(os.path.dirname(__file__), '..', 'docs', 'graph_segments.json')))
    import sys; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'sim', 'infra')); import impacts as IM
    P = IM.road_points(S, meta); rng = np.random.default_rng(seed); idx = rng.choice(len(P['x']), min(2000, len(P['x'])), replace=False) if len(P['x']) else []
    radii = [o['radius'] for o in rows] or [100.0]
    base = [at(P['x'][i], P['y'][i], float(rng.choice(radii))) for i in idx]
    def rate(L, k): return round(float(np.mean([b[k] for b in L])), 3) if L else None
    by = {}
    for o in rows: by.setdefault(o['src'].split(':')[0], []).append(o)
    summ = {s: dict(n=len(L), hit_10=rate(L, 'hit_10'), hit_30=rate(L, 'hit_30'), wet_by_report=rate([o for o in L if 'wet_by_report' in o], 'wet_by_report'),
                    median_lead_h=float(np.median([o['lead_h'] for o in L if o.get('lead_h') is not None])) if any(o.get('lead_h') is not None for o in L) else None) for s, L in by.items()}
    summ['all'] = dict(n=len(rows), hit_10=rate(rows, 'hit_10'), hit_30=rate(rows, 'hit_30'))
    summ['random_road_points'] = dict(n=len(base), hit_10=rate(base, 'hit_10'), hit_30=rate(base, 'hit_30'))
    return dict(run=meta.get('run'), summary=summ, points=rows)

if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('--run-dir', required=True); ap.add_argument('--out')
    ap.add_argument('--lsr', default='docs/proto/obs/lsr_sep2023.csv'); ap.add_argument('--stormevents', default='docs/proto/obs/stormevents_sep2023.csv')
    ap.add_argument('--labels', default='proto/data/labels_sep2023_leominster.csv')
    a = ap.parse_args(); R = run(a.run_dir, parse_obs(a.lsr, a.stormevents, a.labels)); print(json.dumps(R['summary'], indent=1))
    if a.out: json.dump(R, open(a.out, 'w'), indent=1, default=str)
