"""Score a prototype flood run against USGS gauges: stage rise and timing of the peak at every gauge inside the run box.

    python proto/score.py --run-dir <w9 out dir> --obs docs/proto/obs/gauges_sep2023.json --out score.json
    python proto/score.py --run-dir docs/proto/exp/fb_base/rundir --windows docs/proto/exp/fb_base/gauge_windows.npz   # offline re-score
    python proto/score.py --selftest

Why stage *rise* and not absolute water level: the lidar DEM holds the river surface at survey time, not the bed, and gauge datums are
NAVD88 while channel bed burn is approximate, so absolute levels carry a metre-scale offset that says nothing about the flood.  The rise
(peak minus pre-storm level) and the time of the peak are what the road-closure question depends on.
Model series: water depth every 30 min (frames_cm.npz) at the gauge's channel cell = the cell with the largest peak depth within 60 m
(the river), minus its depth at the start.  Observed: 15-min stage, rise = peak - median of the 12 h before the storm start.
Offline: when the run dir has no frames_cm.npz, the 150 m gauge windows saved by an earlier score (gauge_windows.npz, SCORE_WINDOWS) give
the same series (same cell choice), so committed experiments can be re-scored without the flood model.

Timing (gap-aware).  The observed 15-min record can have holes exactly at the peak (01094500 on 12 Sept 2023: no stage 00:30-04:30Z and
04:30-15:00Z, one lone value at 04:30Z).  The time of the highest *recorded* value is then not the time of the peak.
  obs_gaps             gaps > 1 h in the observed stage record within +-6 h of the recorded maximum (start, end, hours)
  gap_flag             the recorded maximum sits in or next to such a gap (its neighbour on either side is > 1 h away)
  obs_peak_interval_utc  [earliest, latest] time the true peak can have: the recorded maximum, widened to the last record before / first
                       record after an adjacent gap.  peak_timing_error_interval_h = 0 when the model peak falls inside it, else the signed
                       distance to the nearer end.  timing_error_h (model peak - recorded maximum) is kept unchanged for compatibility.
  rise50               rising-limb time: first time stage reaches 50 % of the event rise above its pre-storm level (observed: pre-storm median;
                       model: depth at t0), linear between records; rise50_error_h = model - observed.  Insensitive to holes after the
                       crossing and to the peak plateau; rise50_in_gap flags an observed crossing interpolated across a gap > 1 h.
  centroid             hydrograph centroid time over the event window [t0, end of the model run]: sum t (h - h_pre)+ / sum (h - h_pre)+;
                       observed stage interpolated onto the model's 30-min times (gaps bridged linearly, flagged by centroid_gap_h =
                       hours of the window inside gaps).  Measures where the bulk of the event sits (shape, recession), not only the crest.
  timing_error_robust_h  rise50_error_h (peak_timing_error_interval_h when the rise50 crossing cannot be found); the mean
                       mean_abs_timing_error_h uses this robust value; the raw peak-time mean is mean_abs_peak_timing_error_h.
"""
import os, sys, json, argparse, datetime as dt
import numpy as np

GAP_H = 1.0          # a hole in the 15-min record longer than this is a gap
GAP_WIN_H = 6.0      # gaps looked for within +- this of the recorded maximum


def iso(s):
    return dt.datetime.fromisoformat(s.replace('Z', '+00:00')).astimezone(dt.timezone.utc)


def zfmt(t):
    return t.strftime('%Y-%m-%dT%H:%MZ')


def hrs(a, b):
    return (a - b).total_seconds() / 3600.0


def crossing(ts, vs, level, t_from=None, gap_h=GAP_H):
    """First time a series (datetimes, values) reaches `level` at/after t_from, linear between records -> (time, interpolated_over_gap)."""
    prev = None
    for t, v in zip(ts, vs):
        if t_from is not None and t < t_from: prev = (t, v); continue
        if v >= level:
            if prev is None or prev[1] >= level: return t, False
            f = (level - prev[1]) / (v - prev[1]); tc = prev[0] + (t - prev[0]) * f
            return tc, hrs(t, prev[0]) > gap_h
        prev = (t, v)
    return None, False


def gaps_near(ts, t_ref, win_h=GAP_WIN_H, gap_h=GAP_H):
    out = []
    for a, b in zip(ts[:-1], ts[1:]):
        if hrs(b, a) > gap_h and hrs(b, t_ref) >= -win_h and hrs(a, t_ref) <= win_h:
            out.append(dict(start_utc=zfmt(a), end_utc=zfmt(b), hours=round(hrs(b, a), 2)))
    return out


def peak_interval(ts, i, gap_h=GAP_H):
    """Recorded maximum at index i -> (lo, hi, gap_flag): widened to the neighbouring record across an adjacent gap."""
    lo = hi = ts[i]; flag = False
    if i > 0 and hrs(ts[i], ts[i - 1]) > gap_h: lo = ts[i - 1]; flag = True
    if i < len(ts) - 1 and hrs(ts[i + 1], ts[i]) > gap_h: hi = ts[i + 1]; flag = True
    return lo, hi, flag


def centroid(t_h, h, base):
    w = np.clip(np.asarray(h, float) - base, 0, None)
    return float((w * t_h).sum() / w.sum()) if w.sum() > 0 else None


def timing(t0, hours, ms, st, pre_level, o_rise, win_end):
    """Gap-aware timing metrics for one gauge.  ms: model depth series at `hours` after t0; st: observed [(datetime, stage m)]."""
    hours = np.asarray(hours, float); ms = np.asarray(ms, float)
    ts = [t for t, _ in st]; vs = [v for _, v in st]
    win = [k for k, t in enumerate(ts) if t0 <= t <= win_end]
    i = max(win, key=lambda k: vs[k])
    lo, hi, flag = peak_interval(ts, i)
    m_tpk = t0 + dt.timedelta(hours=float(hours[int(np.argmax(ms))]))
    e_lo, e_hi = hrs(m_tpk, hi), hrs(m_tpk, lo)          # model - true peak, over the possible true-peak times
    e_int = 0.0 if e_lo <= 0 <= e_hi else (e_lo if e_lo > 0 else e_hi)
    # rising limb, 50 % of the event rise
    m_rise = float(ms.max() - ms[0])
    mts = [t0 + dt.timedelta(hours=float(h)) for h in hours]
    m50, _ = crossing(mts, list(ms), ms[0] + 0.5 * m_rise) if m_rise > 0 else (None, False)
    o50, o50_gap = crossing(ts, vs, pre_level + 0.5 * o_rise, t_from=t0) if o_rise > 0 else (None, False)
    r50 = round(hrs(m50, o50), 2) if (m50 is not None and o50 is not None) else None
    # centroid over the event window, observed interpolated onto the model times
    tsec = np.array([hrs(t, t0) for t in ts]); inwin = hours <= hrs(win_end, t0) + 1e-9
    oh = np.interp(hours[inwin], tsec, vs); mc = centroid(hours[inwin], ms[inwin], ms[0]); oc = centroid(hours[inwin], oh, pre_level)
    gap_in_win = 0.0
    for a, b in zip(tsec[:-1], tsec[1:]):
        if b - a > GAP_H: gap_in_win += max(0.0, min(b, hours[inwin][-1]) - max(a, 0.0))
    robust = r50 if r50 is not None else round(e_int, 2)
    return dict(gap_flag=bool(flag), obs_gaps=gaps_near(ts, ts[i]), obs_peak_interval_utc=[zfmt(lo), zfmt(hi)],
                peak_timing_error_interval_h=round(e_int, 2), peak_timing_error_range_h=[round(e_lo, 2), round(e_hi, 2)],
                obs_rise50_utc=zfmt(o50) if o50 else None, model_rise50_utc=zfmt(m50) if m50 else None, rise50_error_h=r50, rise50_in_gap=bool(o50_gap),
                obs_centroid_utc=zfmt(t0 + dt.timedelta(hours=oc)) if oc is not None else None,
                model_centroid_utc=zfmt(t0 + dt.timedelta(hours=mc)) if mc is not None else None,
                centroid_error_h=round(mc - oc, 2) if (mc is not None and oc is not None) else None, centroid_gap_h=round(gap_in_win, 2),
                timing_error_robust_h=robust, timing_metric='rise50' if r50 is not None else 'peak_interval')


def _windows(path):
    if not path or not os.path.exists(path): return None
    Z = np.load(path); return {k: Z[k] for k in Z.files}


def score(run_dir, obs_path, windows=None):
    meta_p = os.path.join(run_dir, 'meta.json')
    for alt in (os.path.join(run_dir, 'flood_meta.json'), os.path.join(os.path.dirname(os.path.abspath(run_dir)), 'flood_meta.json')):
        if not os.path.exists(meta_p): meta_p = alt
    meta = json.load(open(meta_p)); x0, y0, x1, y1 = meta['box']; res = meta['res_m']
    fp = os.path.join(run_dir, 'frames_cm.npz'); GW = None
    if os.path.exists(fp):
        F = np.load(fp); D = F['depth_cm'].astype(np.float32) / 100.0; hours = F['hours']
    else:
        GW = _windows(windows or os.path.join(run_dir, 'gauge_windows.npz')) or _windows(os.path.join(os.path.dirname(os.path.abspath(run_dir)), 'gauge_windows.npz'))
        if GW is None: raise FileNotFoundError('no frames_cm.npz and no gauge_windows.npz for ' + run_dir)
        D = None; hours = GW['hours']
    t0 = iso(meta['t0']); G = json.load(open(obs_path))['gauges']; WIN = {}
    WM = np.load(os.path.join(run_dir, 'watermask.npy')).astype(bool) if os.path.exists(os.path.join(run_dir, 'watermask.npy')) else None
    Z = np.load(os.path.join(run_dir, 'z.npy')) if os.path.exists(os.path.join(run_dir, 'z.npy')) else None
    from pyproj import Transformer
    tr = Transformer.from_crs(4326, 26986, always_xy=True); out = []
    for g in G:
        x, y = tr.transform(g['lon'], g['lat'])
        if not (x0 <= x < x1 and y0 <= y < y1) or not g.get('stage_ft'): continue
        r, c = int((y1 - y) // res), int((x - x0) // res); k = max(1, int(np.ceil(60 / res)))
        kw = max(1, int(np.ceil(150 / res)))
        if D is not None:
            win = D[:, max(0, r - k):r + k + 1, max(0, c - k):c + k + 1]
            sl = (slice(max(0, r - kw), r + kw + 1), slice(max(0, c - kw), c + kw + 1))
            WIN[g['site']] = dict(depth_cm=(D[(slice(None),) + sl] * 100).astype(np.uint16), z=Z[sl] if Z is not None else None, wm=WM[sl] if WM is not None else None, r0=sl[0].start, c0=sl[1].start, r=r, c=c)
            wm = WM[max(0, r - k):r + k + 1, max(0, c - k):c + k + 1] if WM is not None else None
            zw = Z[max(0, r - k):r + k + 1, max(0, c - k):c + k + 1] if Z is not None else None
            lr, lc = r - max(0, r - k), c - max(0, c - k)
        else:                                    # saved 150 m window -> the same 60 m window around the gauge cell
            key = g['site'] + '_depth_cm'
            if key not in GW: continue
            r0, c0 = max(0, r - kw), max(0, c - kw); a0, b0 = max(0, r - k) - r0, max(0, c - k) - c0
            Wd = GW[key].astype(np.float32) / 100.0; win = Wd[:, a0:a0 + (r - max(0, r - k)) + k + 1, b0:b0 + (c - max(0, c - k)) + k + 1]
            sub = lambda A: A[a0:a0 + win.shape[1], b0:b0 + win.shape[2]] if A is not None else None
            wm = sub(GW.get(g['site'] + '_wm')); wm = wm.astype(bool) if wm is not None else None; zw = sub(GW.get(g['site'] + '_z'))
            lr, lc = r - max(0, r - k), c - max(0, c - k)
        pk = win.max(axis=0)
        if wm is not None and wm.any():          # prefer the river: nearest channel/water cell to the gauge
            rr_, cc_ = np.nonzero(wm); d2 = (rr_ - lr) ** 2 + (cc_ - lc) ** 2; j = int(np.argmin(d2)); i = (rr_[j], cc_[j])
        else: i = np.unravel_index(np.argmax(pk), pk.shape)
        ms = win[:, i[0], i[1]]; m_rise = float(ms.max() - ms[0]); m_tpk = t0 + dt.timedelta(hours=float(hours[int(np.argmax(ms))]))
        st = [(iso(t), v * 0.3048) for t, v in g['stage_ft']]
        pre = [v for t, v in st if t0 - dt.timedelta(hours=12) <= t <= t0] or [st[0][1]]
        win_end = t0 + dt.timedelta(hours=float(hours[-1]))
        win_obs = [(t, v) for t, v in st if t0 <= t <= win_end]
        if not win_obs: continue
        o_t, o_v = max(win_obs, key=lambda a: a[1]); pre_level = float(np.median(pre)); o_rise = o_v - pre_level
        q = g.get('peak_q_cfs')
        wse = None
        if zw is not None and g.get('datum_ft') is not None and (g.get('vdatum') or '').upper().startswith('NAVD'):
            wse_m = float(zw[i] + ms.max())
            wse = dict(obs_peak_wse_m=round(g['datum_ft'] * 0.3048 + o_v, 2), model_peak_wse_m=round(wse_m, 2), wse_error_m=round(wse_m - (g['datum_ft'] * 0.3048 + o_v), 2))
        out.append(dict(site=g['site'], name=g['name'], drain_km2=round((g.get('drain_mi2') or 0) * 2.59, 1), obs_rise_m=round(o_rise, 2), model_rise_m=round(m_rise, 2),
                        rise_error_m=round(m_rise - o_rise, 2), obs_peak_utc=zfmt(o_t), model_peak_utc=zfmt(m_tpk),
                        timing_error_h=round((m_tpk - o_t).total_seconds() / 3600, 1), obs_peak_q_m3s=round(q[1] * 0.0283168, 1) if q else None, **(wse or {}),
                        **timing(t0, hours, ms, st, pre_level, o_rise, win_end)))
    if D is not None:
        try:
            np.savez_compressed(os.environ.get('SCORE_WINDOWS', '/tmp/gauge_windows.npz'),
                                **{f'{k}_{f}': v[f] for k, v in WIN.items() for f in ('depth_cm', 'z', 'wm') if v[f] is not None}, hours=hours)
        except Exception as e: print('windows not saved', e)
    m = lambda key, nd=1: round(float(np.mean(np.abs(v))), nd) if (v := [o[key] for o in out if o.get(key) is not None]) else None
    errs = [o['rise_error_m'] for o in out]
    return dict(run=meta.get('run'), gauges=out, mean_abs_rise_error_m=m('rise_error_m', 2),
                mean_rise_bias_m=round(float(np.mean(errs)), 2) if errs else None,
                mean_abs_timing_error_h=m('timing_error_robust_h'), mean_abs_peak_timing_error_h=m('timing_error_h'),
                mean_abs_peak_timing_error_interval_h=m('peak_timing_error_interval_h'), mean_abs_rise50_error_h=m('rise50_error_h'),
                mean_abs_centroid_error_h=m('centroid_error_h'), gauges_gap_flagged=sum(1 for o in out if o['gap_flag']),
                timing_note='mean_abs_timing_error_h = mean |timing_error_robust_h| (rising-limb 50 % time; peak interval when no crossing); '
                            'raw peak-time mean in mean_abs_peak_timing_error_h (until 22 Oct 2026 mean_abs_timing_error_h held that)',
                mean_abs_wse_error_m=m('wse_error_m', 2))


def selftest():
    ok = True
    def check(name, cond, det=''):
        nonlocal ok; ok &= bool(cond); print(('ok   ' if cond else 'FAIL ') + name, '' if cond else det)
    t0 = iso('2023-09-11T16:00Z'); hours = np.arange(0, 24.01, 0.5)
    # observed: rise 0 -> 2 m peaking at 9 h, 15-min record with holes 8.5-12.5 h and 12.5-23 h (lone value at 12.5 h = recorded max)
    tq = np.arange(-12, 24.01, 0.25); ov = np.clip(2.0 * np.exp(-((tq - 9.0) / 3.0) ** 2), 0, None)
    keep = (tq <= 8.5) | (np.abs(tq - 12.5) < 1e-9) | (tq >= 23)
    ov = ov.copy(); ov[np.abs(tq - 12.5) < 1e-9] = 2.1           # lone recorded value is the highest
    st = [(t0 + dt.timedelta(hours=float(h)), float(v)) for h, v, kk in zip(tq, ov, keep) if kk]
    ms = 2.0 * np.exp(-((hours - 8.0) / 3.0) ** 2); ms = ms - ms[0]
    T = timing(t0, hours, ms, st, 0.0, 2.1, t0 + dt.timedelta(hours=24))
    check('gap flagged', T['gap_flag'] and len(T['obs_gaps']) == 2, T['obs_gaps'])
    check('interval 8.5-23 h', T['obs_peak_interval_utc'] == [zfmt(t0 + dt.timedelta(hours=8.5)), zfmt(t0 + dt.timedelta(hours=23))], T['obs_peak_interval_utc'])
    check('model peak (8 h) before the interval -> -0.5 h', abs(T['peak_timing_error_interval_h'] + 0.5) < 1e-6, T['peak_timing_error_interval_h'])
    check('rise50 error ~ -1 h', T['rise50_error_h'] is not None and abs(T['rise50_error_h'] + 1.0) < 0.3, T['rise50_error_h'])
    check('robust = rise50', T['timing_error_robust_h'] == T['rise50_error_h'] and T['timing_metric'] == 'rise50')
    check('centroid gap hours', T['centroid_gap_h'] > 10, T['centroid_gap_h'])
    # no gaps: same shapes 1 h apart -> every error -1 h
    st2 = [(t0 + dt.timedelta(hours=float(h)), float(2.0 * np.exp(-((h - 9.0) / 3.0) ** 2))) for h in tq]
    T2 = timing(t0, hours, ms, st2, 0.0, 2.0, t0 + dt.timedelta(hours=24))
    check('no gap: not flagged, interval = point', not T2['gap_flag'] and T2['obs_peak_interval_utc'][0] == T2['obs_peak_interval_utc'][1])
    check('no gap: peak, rise50, centroid all ~ -1 h', abs(T2['peak_timing_error_interval_h'] + 1) < 0.01 and abs(T2['rise50_error_h'] + 1) < 0.1
          and abs(T2['centroid_error_h'] + 1) < 0.3, (T2['peak_timing_error_interval_h'], T2['rise50_error_h'], T2['centroid_error_h']))
    print('score selftest', 'OK' if ok else 'FAILED'); return ok


if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('--run-dir'); ap.add_argument('--obs', help='default docs/proto/obs/gauges_<storm>.json'); ap.add_argument('--out')
    ap.add_argument('--storm', default=os.environ.get('STORM') or None, help='storm id (env STORM; default from the run name, else sep2023) -> default obs file')
    ap.add_argument('--windows', help='gauge_windows.npz from an earlier score (offline re-score when the run dir has no frames_cm.npz)')
    ap.add_argument('--selftest', action='store_true')
    a = ap.parse_args()
    if a.selftest: sys.exit(0 if selftest() else 1)
    storm = a.storm
    if not storm and not a.obs:
        mp = os.path.join(a.run_dir, 'meta.json'); mp = mp if os.path.exists(mp) else os.path.join(os.path.dirname(os.path.abspath(a.run_dir)), 'flood_meta.json')
        run = (json.load(open(mp)).get('run') or '') if os.path.exists(mp) else ''; storm = run.split('_')[0] if os.path.exists(f"docs/proto/obs/gauges_{run.split('_')[0]}.json") else 'sep2023'
    s = score(a.run_dir, a.obs or f'docs/proto/obs/gauges_{storm or "sep2023"}.json', a.windows); print(json.dumps(s, indent=1))
    if a.out: json.dump(s, open(a.out, 'w'), indent=1)
