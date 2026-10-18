"""Score a flood run against things that really happened.

    python sim/validate.py <run_dir>        run_dir holds meta.json + hmax.npy (from sim/colab/w4_flood_gpu.py)

Checks:
  1. USGS STN high-water marks (surveyed peak water elevation after the storm):  modelled peak depth at the mark vs the
     surveyed depth above ground (HWM elevation - ground elevation at that point).  Reports bias, MAE, and the share of marks
     where the model put water at all.
  2. Flood reports (docs/prone/flood_reports.json, 4,551 road flood reports with dates):  for reports on the storm days,
     the share with modelled peak depth >= 10 cm within 100 m ("hit rate"), and the same number for random road points
     ("false-alarm context").
Writes <run_dir>/validation.json and prints a plain summary.
"""
import os, sys, json, math
import numpy as np

def main(run_dir, hwm_path=None, reports_path=None):
    meta = json.load(open(os.path.join(run_dir, 'meta.json'))); hm = np.load(os.path.join(run_dir, 'hmax.npy')).astype(np.float32)
    x0, y0, x1, y1 = meta['box']; res = meta['res_m']; ny, nx = hm.shape
    from pyproj import Transformer
    tr = Transformer.from_crs(4326, 26986, always_xy=True)
    def at(lon, lat, radius_m=0):
        x, y = tr.transform(lon, lat); c = int((x - x0) / res); r = int((y1 - y) / res)
        if not (0 <= r < ny and 0 <= c < nx): return None
        if radius_m <= 0: return float(hm[r, c])
        k = int(math.ceil(radius_m / res)); return float(hm[max(0, r - k):r + k + 1, max(0, c - k):c + k + 1].max())
    out = dict(run=meta['run'], res_m=res)
    t0 = meta['t0'][:10]; days = set()
    import datetime as dt
    d0 = dt.date.fromisoformat(t0)
    for k in range(int(meta['frame_min'] * (len(meta['frames']) - 1) / 1440) + 2): days.add((d0 + dt.timedelta(days=k)).isoformat())
    # 1. high-water marks (docs/validation/stn_ma.json: compact USGS STN marks for Massachusetts)
    if hwm_path and os.path.exists(hwm_path):
        H = json.load(open(hwm_path)); C = {c: i for i, c in enumerate(H['columns'])}; rows = []
        run_start = meta['t0'][:10]
        evs = {int(k) for k, e in H['events'].items() if e['start'] <= max(days) and e['end'] >= min(days)}
        out['hwm_events'] = {k: e['name'] for k, e in H['events'].items() if int(k) in evs}
        for r in H['rows']:
            if r[C['event']] not in evs: continue
            hb = r[C['height_above_ground_ft']]
            if hb is None: continue
            obs = float(hb) * 0.3048; mod = at(r[C['lon']], r[C['lat']], 0); modw = at(r[C['lon']], r[C['lat']], 30)
            if mod is None: continue
            rows.append(dict(id=r[C['id']], lat=r[C['lat']], lon=r[C['lon']], obs_m=round(obs, 2), mod_m=round(mod, 2), mod_max30_m=round(modw, 2), env=r[C['environment']], where=r[C['waterbody']] or r[C['location']]))
        if rows:
            o = np.array([r['obs_m'] for r in rows]); m = np.array([r['mod_m'] for r in rows]); mw = np.array([r['mod_max30_m'] for r in rows])
            out['hwm'] = dict(n=len(rows), bias_m=round(float((m - o).mean()), 2), mae_m=round(float(np.abs(m - o).mean()), 2), wet_share=round(float((mw >= 0.1).mean()), 2),
                              within_50cm=round(float((np.abs(m - o) <= 0.5).mean()), 2), bias_max30_m=round(float((mw - o).mean()), 2), mae_max30_m=round(float(np.abs(mw - o).mean()), 2),
                              note='mod_m: modelled peak depth at the mark cell; mod_max30_m: deepest cell within 30 m; obs_m: surveyed height above ground', rows=rows)
    # 2. flood reports
    if reports_path and os.path.exists(reports_path):
        R = json.load(open(reports_path))['rows']; hit = [];
        for lon, lat, date, src in R:
            if date in days:
                v = at(lon, lat, 100)
                if v is not None: hit.append(v >= 0.1)
        rng = np.random.default_rng(0); rand = []
        for lon, lat, date, src in [R[i] for i in rng.choice(len(R), min(3000, len(R)), replace=False)]:
            v = at(lon, lat, 100)
            if v is not None: rand.append(v >= 0.1)
        out['reports'] = dict(n_storm_day=len(hit), hit_rate=round(float(np.mean(hit)), 3) if hit else None, any_day_rate=round(float(np.mean(rand)), 3) if rand else None)
    json.dump(out, open(os.path.join(run_dir, 'validation.json'), 'w'), indent=1)
    print(json.dumps({k: v for k, v in out.items() if k != 'hwm'} | ({'hwm': {k: v for k, v in out['hwm'].items() if k != 'rows'}} if 'hwm' in out else {}), indent=1))
    return out

if __name__ == '__main__':
    rd = sys.argv[1]; base = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
    main(rd, hwm_path=sys.argv[2] if len(sys.argv) > 2 else os.path.join(base, 'docs', 'validation', 'stn_ma.json'), reports_path=os.path.join(base, 'docs', 'prone', 'flood_reports.json'))
