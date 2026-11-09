"""Radar nowcast vs HRRR vs MRMS truth over past storms: docs/proto/forecast/NOWCAST_WINDOWS_PREREG.md part A, checks 1-2 (rain only).

    python proto/nowcast_hindcast.py --storms sep2023,aug2023 --out docs/proto/forecast/nowcast_hindcast.json
    python proto/nowcast_hindcast.py selftest

For each storm (docs/proto/obs/catalog.json: t0, hours, bbox_lonlat) the issue times tau run every 3 h from t0 to t0 + hours - 3 (on the
hour).  At tau, as the live forecast would have it:
  nowcast  MRMS PrecipRate frames at tau-20/-10/0 min over District 3 + upstream margin, advected 3 h (proto/live_feeds.advect_pysteps,
           else phase correlation), 10-min steps -> hourly mm for the hours ending tau+1..tau+3
  HRRR     the cycle tau-1 h (the newest one on the web at tau), APCP of the hours ending tau+1..tau+6 (forecast hours 2..7)
  blend    hour 1 nowcast, hour 2 half and half, hour 3+ HRRR (weight on radar 1 at 1 h, 0 at 3 h)
  truth    MRMS MultiSensor_QPE_01H_Pass2 for the hours ending tau+1..tau+6
All three on the 1 km MRMS grid over the storm's catalogue box (HRRR nearest 3 km cell).  Error per hour: box-mean |error| (mm) and the
1 km mean |error|.  The prereg's check 1 = box-mean, leads 1-3; check 2 = leads 4-6 (blend = HRRR there: equal by construction, reported).
Locked storms (score_v2.LOCKED) are refused.
"""
import argparse, datetime as dt, json, os, sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(ROOT, 'sim', 'colab'))
W_RADAR = {1: 1.0, 2: 0.5}            # hour (ending tau+h) -> weight on the nowcast; 0 from hour 3 on


def nowcast_hourly(tau, LF):
    """3 hourly nowcast fields (mm) on the NC grid, plus lat/lon; None when frames are missing."""
    L = LF.mrms_recent('PrecipRate_00.00', tau - dt.timedelta(minutes=40), tau)
    if not L: return None
    pick = []
    for k in (2, 1, 0):
        w = tau - dt.timedelta(minutes=LF.STEP_MIN * k); c = min(L, key=lambda x: abs((x[0] - w).total_seconds()))
        if abs((c[0] - w).total_seconds()) <= 120: pick.append(c)
    if len(pick) < 2: return None
    fr = []; lat = lon = None
    for t, u in pick: V, lat, lon = LF.mrms_box(u, LF.NC_LAT, LF.NC_LON); fr.append(np.nan_to_num(V, nan=0.0))
    LF.NSTEP = 18                                                    # 3 h of 10-min steps (module default is 2 h)
    if max(f.max() for f in fr) < 0.1: F = np.zeros((18,) + fr[-1].shape, np.float32); how = 'dry'
    else:
        try: F, _, how = LF.advect_pysteps(fr)
        except Exception: F, _, how = LF.advect_phase(fr)
    H = [F[6 * h:6 * h + 6].sum(0) * LF.STEP_MIN / 60.0 for h in range(3)]
    return H, lat, lon, how


def crop(V, lat, lon, box):
    lo0, la0, lo1, la1 = box; i = (lat >= la0) & (lat <= la1); j = (lon >= lo0) & (lon <= lo1)
    return V[np.ix_(i, j)], lat[i], lon[j]


def truth(t_end, box, LF):
    u = (f'{LF.MRMS}/CONUS/MultiSensor_QPE_01H_Pass2_00.00/{t_end:%Y%m%d}/MRMS_MultiSensor_QPE_01H_Pass2_00.00_{t_end:%Y%m%d-%H%M%S}.grib2.gz')
    try: V, la, lo = LF.mrms_box(u, (box[1], box[3]), (box[0], box[2])); return np.nan_to_num(V, nan=0.0), la, lo
    except Exception: return None


def hrrr_on(init, fh, la, lo):
    import hrrr_rain as HR
    m = HR.apcp(init, fh)
    if m is None: return None
    v = np.ma.filled(m.values, 0.0).astype(np.float32); glat, glon = m.latlons(); glon = np.where(glon > 180, glon - 360, glon)
    from scipy.spatial import cKDTree
    T = cKDTree(np.column_stack([glat.ravel(), glon.ravel() * np.cos(np.radians(42.4))]))
    LA, LO = np.meshgrid(la, lo, indexing='ij'); _, k = T.query(np.column_stack([LA.ravel(), LO.ravel() * np.cos(np.radians(42.4))]))
    return np.maximum(v.ravel()[k].reshape(LA.shape), 0)


def one_cycle(storm, box, tau, LF):
    import pandas as pd
    N = nowcast_hourly(tau, LF); init = pd.Timestamp(tau - dt.timedelta(hours=1)).to_pydatetime()
    rows = []
    for h in range(1, 7):
        T = truth(tau + dt.timedelta(hours=h), box, LF)
        if T is None: continue
        Tv, la, lo = T; Hv = hrrr_on(init, h + 1, la, lo)
        if Hv is None or Hv.shape != Tv.shape: continue
        r = dict(lead_h=h, truth_mean=float(Tv.mean()), hrrr_mean=float(Hv.mean()), hrrr_abs_box=abs(float(Hv.mean() - Tv.mean())),
                 hrrr_abs_1km=float(np.abs(Hv - Tv).mean()))
        if N is not None and h <= 3:
            Nv, nla, nlo = crop(N[0][h - 1], N[1], N[2], box)
            if Nv.shape == Tv.shape:
                w = W_RADAR.get(h, 0.0); Bv = w * Nv + (1 - w) * Hv
                r.update(nowcast_mean=float(Nv.mean()), blend_mean=float(Bv.mean()), blend_abs_box=abs(float(Bv.mean() - Tv.mean())),
                         blend_abs_1km=float(np.abs(Bv - Tv).mean()), nowcast_how=N[3])
        if h > 3: r.update(blend_mean=r['hrrr_mean'], blend_abs_box=r['hrrr_abs_box'], blend_abs_1km=r['hrrr_abs_1km'])
        rows.append(r)
    return dict(storm=storm, tau=tau.strftime('%Y-%m-%dT%H:%MZ'), hrrr_init=init.strftime('%Y-%m-%dT%HZ'), leads=rows)


def summarise(C):
    S = {}
    for name, leads in (('lead_1_3', (1, 2, 3)), ('lead_4_6', (4, 5, 6))):
        per = []
        for c in C:
            L = [r for r in c['leads'] if r['lead_h'] in leads and 'blend_abs_box' in r]
            if len(L) == len(leads): per.append((np.mean([r['hrrr_abs_box'] for r in L]), np.mean([r['blend_abs_box'] for r in L]),
                                                 np.mean([r['hrrr_abs_1km'] for r in L]), np.mean([r['blend_abs_1km'] for r in L])))
        if not per: S[name] = dict(cycles=0); continue
        P = np.array(per)
        S[name] = dict(cycles=len(P), hrrr_mae_box=float(P[:, 0].mean()), blend_mae_box=float(P[:, 1].mean()), ratio_box=float(P[:, 1].mean() / max(P[:, 0].mean(), 1e-9)),
                       share_cycles_blend_worse=float((P[:, 1] > P[:, 0] + 1e-9).mean()), hrrr_mae_1km=float(P[:, 2].mean()), blend_mae_1km=float(P[:, 3].mean()))
    a, b = S.get('lead_1_3', {}), S.get('lead_4_6', {})
    S['check1_pass'] = bool(a.get('cycles') and a['ratio_box'] <= 0.85 and a['share_cycles_blend_worse'] <= 1 / 3)
    S['check2_pass'] = bool(b.get('cycles') and abs(b['ratio_box'] - 1) <= 0.05)
    return S


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('cmd', nargs='?', default='run'); ap.add_argument('--storms', default='')
    ap.add_argument('--out', default='docs/proto/forecast/nowcast_hindcast.json'); a = ap.parse_args()
    import live_feeds as LF, score_v2 as SV
    if a.cmd == 'selftest':
        assert W_RADAR[1] == 1 and W_RADAR[2] == 0.5 and 3 not in W_RADAR
        C = [dict(leads=[dict(lead_h=h, hrrr_abs_box=2.0, blend_abs_box=(1.0 if h <= 3 else 2.0), hrrr_abs_1km=3.0, blend_abs_1km=2.5) for h in range(1, 7)])] * 3
        S = summarise(C); assert S['check1_pass'] and S['check2_pass'] and abs(S['lead_1_3']['ratio_box'] - 0.5) < 1e-9, S
        print('nowcast_hindcast selftest ok'); return
    cat = {e['id']: e for e in json.load(open(os.path.join(ROOT, 'docs', 'proto', 'obs', 'catalog.json')))['events']}
    C = []
    for s in [x for x in a.storms.split(',') if x]:
        if s in SV.LOCKED: print('locked, skipped:', s); continue
        e = cat[s]; t0 = dt.datetime.strptime(e['t0'], '%Y-%m-%dT%H:%MZ')
        for k in range(0, max(1, e['hours'] - 2), 3):
            tau = t0 + dt.timedelta(hours=k)
            try: c = one_cycle(s, e['bbox_lonlat'], tau, LF)
            except Exception as ex: print('cycle failed', s, tau, repr(ex)[:160]); continue
            C.append(c); L = c['leads']
            print(s, c['tau'], ' '.join(f"h{r['lead_h']} T{r['truth_mean']:.1f} H{r['hrrr_mean']:.1f}" + (f" N{r['nowcast_mean']:.1f}" if 'nowcast_mean' in r else '') for r in L), flush=True)
    S = summarise(C)
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    json.dump(dict(made_by='proto/nowcast_hindcast.py', prereg='docs/proto/forecast/NOWCAST_WINDOWS_PREREG.md (part A, checks 1-2)', summary=S, cycles=C), open(a.out, 'w'), indent=1)
    print(json.dumps(S, indent=1))


if __name__ == '__main__':
    main()
