"""Score a prototype flood run against USGS gauges: stage rise and timing of the peak at every gauge inside the run box.

    python proto/score.py --run-dir <w9 out dir> --obs docs/proto/obs/gauges_sep2023.json --out score.json

Why stage *rise* and not absolute water level: the lidar DEM holds the river surface at survey time, not the bed, and gauge datums are
NAVD88 while channel bed burn is approximate, so absolute levels carry a metre-scale offset that says nothing about the flood.  The rise
(peak minus pre-storm level) and the time of the peak are what the road-closure question depends on.
Model series: water depth every 30 min (frames_cm.npz) at the gauge's channel cell = the cell with the largest peak depth within 60 m
(the river), minus its depth at the start.  Observed: 15-min stage, rise = peak - median of the 12 h before the storm start.
"""
import os, json, argparse, datetime as dt
import numpy as np

def iso(s):
    return dt.datetime.fromisoformat(s.replace('Z', '+00:00')).astimezone(dt.timezone.utc)

def score(run_dir, obs_path):
    meta = json.load(open(os.path.join(run_dir, 'meta.json'))); x0, y0, x1, y1 = meta['box']; res = meta['res_m']
    F = np.load(os.path.join(run_dir, 'frames_cm.npz')); D = F['depth_cm'].astype(np.float32) / 100.0; hours = F['hours']
    t0 = iso(meta['t0']); G = json.load(open(obs_path))['gauges']; WIN = {}
    WM = np.load(os.path.join(run_dir, 'watermask.npy')).astype(bool) if os.path.exists(os.path.join(run_dir, 'watermask.npy')) else None
    Z = np.load(os.path.join(run_dir, 'z.npy')) if os.path.exists(os.path.join(run_dir, 'z.npy')) else None
    from pyproj import Transformer
    tr = Transformer.from_crs(4326, 26986, always_xy=True); out = []
    for g in G:
        x, y = tr.transform(g['lon'], g['lat'])
        if not (x0 <= x < x1 and y0 <= y < y1) or not g.get('stage_ft'): continue
        r, c = int((y1 - y) // res), int((x - x0) // res); k = max(1, int(np.ceil(60 / res)))
        win = D[:, max(0, r - k):r + k + 1, max(0, c - k):c + k + 1]; pk = win.max(axis=0)
        kw = max(1, int(np.ceil(150 / res))); sl = (slice(max(0, r - kw), r + kw + 1), slice(max(0, c - kw), c + kw + 1))
        WIN[g['site']] = dict(depth_cm=(D[(slice(None),) + sl] * 100).astype(np.uint16), z=Z[sl] if Z is not None else None, wm=WM[sl] if WM is not None else None, r0=sl[0].start, c0=sl[1].start, r=r, c=c)
        wm = WM[max(0, r - k):r + k + 1, max(0, c - k):c + k + 1] if WM is not None else None
        if wm is not None and wm.any():          # prefer the river: nearest channel/water cell to the gauge
            rr_, cc_ = np.nonzero(wm); d2 = (rr_ - (r - max(0, r - k))) ** 2 + (cc_ - (c - max(0, c - k))) ** 2; j = int(np.argmin(d2)); i = (rr_[j], cc_[j])
        else: i = np.unravel_index(np.argmax(pk), pk.shape)
        ms = win[:, i[0], i[1]]; m_rise = float(ms.max() - ms[0]); m_tpk = t0 + dt.timedelta(hours=float(hours[int(np.argmax(ms))]))
        st = [(iso(t), v * 0.3048) for t, v in g['stage_ft']]
        pre = [v for t, v in st if t0 - dt.timedelta(hours=12) <= t <= t0] or [st[0][1]]
        win_obs = [(t, v) for t, v in st if t0 <= t <= t0 + dt.timedelta(hours=float(hours[-1]))]
        if not win_obs: continue
        o_t, o_v = max(win_obs, key=lambda a: a[1]); o_rise = o_v - float(np.median(pre))
        q = g.get('peak_q_cfs')
        out.append(dict(site=g['site'], name=g['name'], drain_km2=round((g.get('drain_mi2') or 0) * 2.59, 1), obs_rise_m=round(o_rise, 2), model_rise_m=round(m_rise, 2),
                        rise_error_m=round(m_rise - o_rise, 2), obs_peak_utc=o_t.strftime('%Y-%m-%dT%H:%MZ'), model_peak_utc=m_tpk.strftime('%Y-%m-%dT%H:%MZ'),
                        timing_error_h=round((m_tpk - o_t).total_seconds() / 3600, 1), obs_peak_q_m3s=round(q[1] * 0.0283168, 1) if q else None))
    try:
        np.savez_compressed(os.path.join(os.path.dirname(os.path.abspath(obs_path)), '..', '..', '..', 'gauge_windows.npz') if False else os.environ.get('SCORE_WINDOWS', '/tmp/gauge_windows.npz'),
                            **{f'{k}_{f}': v[f] for k, v in WIN.items() for f in ('depth_cm', 'z', 'wm') if v[f] is not None}, hours=hours)
    except Exception as e: print('windows not saved', e)
    errs = [o['rise_error_m'] for o in out]; terr = [o['timing_error_h'] for o in out]
    return dict(run=meta.get('run'), gauges=out, mean_abs_rise_error_m=round(float(np.mean(np.abs(errs))), 2) if errs else None,
                mean_rise_bias_m=round(float(np.mean(errs)), 2) if errs else None, mean_abs_timing_error_h=round(float(np.mean(np.abs(terr))), 1) if terr else None)

if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('--run-dir', required=True); ap.add_argument('--obs', default='docs/proto/obs/gauges_sep2023.json'); ap.add_argument('--out')
    a = ap.parse_args(); s = score(a.run_dir, a.obs); print(json.dumps(s, indent=1))
    if a.out: json.dump(s, open(a.out, 'w'), indent=1)
