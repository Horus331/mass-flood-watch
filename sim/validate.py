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
    meta = json.load(open(os.path.join(run_dir, 'meta.json'))); hm = np.nan_to_num(np.load(os.path.join(run_dir, os.environ.get('HMAX_FILE', 'hmax.npy'))).astype(np.float32), nan=0.0, posinf=0.0)     # a NaN cell would poison argmax and write bare NaN into the JSON
    x0, y0, x1, y1 = meta['box']; res = meta['res_m']; ny, nx = hm.shape
    from pyproj import Transformer
    tr = Transformer.from_crs(4326, 26986, always_xy=True)
    def at(lon, lat, radius_m=0):
        x, y = tr.transform(lon, lat); c = int(math.floor((x - x0) / res)); r = int(math.floor((y1 - y) / res))
        if not (0 <= r < ny and 0 <= c < nx): return None
        if radius_m <= 0: return float(hm[r, c])
        k = int(math.ceil(radius_m / res)); return float(hm[max(0, r - k):r + k + 1, max(0, c - k):c + k + 1].max())
    out = dict(run=meta['run'], res_m=res)
    t0 = meta['t0'][:10]; days = set()
    import datetime as dt
    d0 = dt.date.fromisoformat(t0)
    for k in range(int(meta['frame_min'] * (len(meta['frames']) - 1) / 1440) + 2): days.add((d0 + dt.timedelta(days=k)).isoformat())
    # 1. high-water marks (docs/validation/stn_ma.json: compact USGS STN marks for Massachusetts)
    #    Two comparisons: (a) water-surface elevation: surveyed mark elevation (NAVD88) vs the model's z+hmax within 60 m
    #    (the standard test; marks often sit on walls or banks whose ground differs from the 30 m cell mean);
    #    (b) depth above ground at the mark cell (old metric, kept).  Marks with height_above_ground = 0 are edge-of-water
    #    points: for them only the WSE and the 'is there water nearby' test mean anything.  Scores are also given per
    #    waterbody/reach, because surveys cluster (July 2023 = 5 reaches), and coastal still-water vs wave/debris marks apart.
    Z = None
    zpath = os.path.join(run_dir, 'z.npy')
    if os.path.exists(zpath): Z = np.load(zpath).astype(np.float32)
    def wse_near(lon, lat, radius_m=60):
        if Z is None: return None
        x, y = tr.transform(lon, lat); c = int(math.floor((x - x0) / res)); r = int(math.floor((y1 - y) / res))
        k = int(math.ceil(radius_m / res)); r0, r1, c0, c1 = max(0, r - k), min(ny, r + k + 1), max(0, c - k), min(nx, c + k + 1)
        if r0 >= r1 or c0 >= c1: return None
        hh = hm[r0:r1, c0:c1]; zz = Z[r0:r1, c0:c1]
        if hh.max() < 0.05: return None
        i = int(np.argmax(hh)); return float(zz.ravel()[i] + hh.ravel()[i])     # WSE at the deepest cell (the channel / flooded floor), not the highest wet cell: a hillside with 5 cm of sheet flow 6 m up-slope would otherwise win
    def wse_alt(lon, lat, radius_m=60):
        """Sensitivity metrics (reported, not primary): WSE at the nearest wet cell, and the median WSE of wet cells within 60 m.
        On steep reaches the deepest cell can lie up- or down-stream of the mark, so the primary metric can carry a slope error."""
        if Z is None: return None, None
        x, y = tr.transform(lon, lat); c = int(math.floor((x - x0) / res)); r = int(math.floor((y1 - y) / res))
        k = int(math.ceil(radius_m / res)); r0, r1, c0, c1 = max(0, r - k), min(ny, r + k + 1), max(0, c - k), min(nx, c + k + 1)
        if r0 >= r1 or c0 >= c1: return None, None
        hh = hm[r0:r1, c0:c1]; w = Z[r0:r1, c0:c1] + hh; wet = hh >= 0.05
        if not wet.any(): return None, None
        ii, jj = np.nonzero(wet); dd = (ii + r0 - r) ** 2 + (jj + c0 - c) ** 2; n_ = int(np.argmin(dd))
        return float(w[ii[n_], jj[n_]]), float(np.median(w[wet]))
    if hwm_path and os.path.exists(hwm_path):
        H = json.load(open(hwm_path)); C = {c: i for i, c in enumerate(H['columns'])}; rows = []
        evs = {int(k) for k, e in H['events'].items() if e['start'] <= max(days) and e['end'] >= min(days)}
        out['hwm_events'] = {k: e['name'] for k, e in H['events'].items() if int(k) in evs}
        for r in H['rows']:
            if r[C['event']] not in evs: continue
            lon, lat = r[C['lon']], r[C['lat']]
            x, y = tr.transform(lon, lat)
            if not (x0 <= x < x1 and y0 <= y < y1): continue
            hb = r[C['height_above_ground_ft']]; el = r[C['elev_ft']]
            obs_d = None if hb is None else float(hb) * 0.3048
            obs_wse = None if (el is None or r[C['vdatum']] not in (2, None)) else float(el) * 0.3048     # vdatum 2 = NAVD88 in STN
            mod = at(lon, lat, 0); modw = at(lon, lat, 30); mwse = wse_near(lon, lat, 60); wnear, wmed = wse_alt(lon, lat, 60)
            if mod is None: continue
            rows.append(dict(id=r[C['id']], lat=lat, lon=lon, reach=(r[C['waterbody']] or r[C['location']] or '')[:40], env=r[C['environment']], still=int(r[C['stillwater']] or 0),
                             obs_m=None if obs_d is None else round(obs_d, 2), mod_m=round(mod, 2), mod_max30_m=round(modw, 2),
                             obs_wse_m=None if obs_wse is None else round(obs_wse, 2), mod_wse_m=None if mwse is None else round(mwse, 2),
                             wse_err_m=None if (obs_wse is None or mwse is None) else round(mwse - obs_wse, 2),
                             wse_err_nearest_m=None if (obs_wse is None or wnear is None) else round(wnear - obs_wse, 2),
                             wse_err_median_m=None if (obs_wse is None or wmed is None) else round(wmed - obs_wse, 2)))
        if rows:
            def score(rs):
                o = np.array([x['obs_m'] for x in rs if x['obs_m'] is not None]); m = np.array([x['mod_m'] for x in rs if x['obs_m'] is not None]); mw = np.array([x['mod_max30_m'] for x in rs])
                we = np.array([x['wse_err_m'] for x in rs if x['wse_err_m'] is not None]); nwse = sum(1 for x in rs if x['obs_wse_m'] is not None)
                d = dict(n=len(rs), wet_within_30m=round(float((mw >= 0.1).mean()), 2), n_wse=int(nwse), wse_found=round(float(len(we) / nwse), 2) if nwse else None)
                if len(we): d.update(wse_bias_m=round(float(we.mean()), 2), wse_mae_m=round(float(np.abs(we).mean()), 2), wse_within_50cm=round(float((np.abs(we) <= 0.5).mean()), 2))
                for key, lab in (('wse_err_nearest_m', 'nearest'), ('wse_err_median_m', 'median')):
                    e_ = np.array([x[key] for x in rs if x.get(key) is not None])
                    if len(e_): d[f'wse_{lab}_bias_m'] = round(float(e_.mean()), 2); d[f'wse_{lab}_mae_m'] = round(float(np.abs(e_).mean()), 2)
                dep = [(x['obs_m'], x['mod_m']) for x in rs if x['obs_m'] is not None and x['obs_m'] > 0]
                if dep:
                    o2 = np.array([a for a, _ in dep]); m2 = np.array([b for _, b in dep])
                    d.update(n_depth=len(dep), bias_m=round(float((m2 - o2).mean()), 2), mae_m=round(float(np.abs(m2 - o2).mean()), 2), within_50cm=round(float((np.abs(m2 - o2) <= 0.5).mean()), 2))
                return d
            out['hwm'] = score(rows); out['hwm']['note'] = ('wse_*: model water-surface elevation (z + peak depth at the deepest cell within 60 m) vs surveyed mark elevation NAVD88; '
                                                            'bias/mae/within_50cm: depth above ground at the mark cell, marks with height above ground > 0 only; wet_within_30m: any water >= 10 cm within 30 m')
            out['hwm']['by_reach'] = {k: score([x for x in rows if x['reach'] == k]) for k in sorted({x['reach'] for x in rows}) if sum(1 for x in rows if x['reach'] == k) >= 3}
            cst = [x for x in rows if x['env'] == 'Coastal']
            if cst: out['hwm']['coastal'] = dict(still_water=score([x for x in cst if x['still']]) if any(x['still'] for x in cst) else None, wave_debris=score([x for x in cst if not x['still']]) if any(not x['still'] for x in cst) else None)
            out['hwm']['rows'] = rows
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
    hf = os.environ.get('HMAX_FILE', 'hmax.npy'); out['hmax_file'] = hf
    json.dump(out, open(os.path.join(run_dir, 'validation.json' if hf == 'hmax.npy' else f'validation_{hf[:-4]}.json'), 'w'), indent=1, allow_nan=False)     # a snapshot-peak score never overwrites the main one
    print(json.dumps({k: v for k, v in out.items() if k != 'hwm'} | ({'hwm': {k: v for k, v in out['hwm'].items() if k not in ('rows',)}} if 'hwm' in out else {}), indent=1))
    return out

if __name__ == '__main__':
    rd = sys.argv[1]; base = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
    main(rd, hwm_path=sys.argv[2] if len(sys.argv) > 2 else os.path.join(base, 'docs', 'validation', 'stn_ma.json'), reports_path=os.path.join(base, 'docs', 'prone', 'flood_reports.json'))
