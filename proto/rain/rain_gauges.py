"""Gauge check of the MRMS rain and of its sub-hourly timing, offline from proto/rain/rain_fetch.py output (docs/proto/rain/RAIN.md).

    python proto/rain/rain_gauges.py      -> docs/proto/rain/gauges.json + tables on stdout

Per storm:
  * hourly: IEM ASOS 1-min precip (summed to clock hours, >= 54 of 60 minutes reported) and USGS 00045 gauges vs MRMS Pass2 at the
    gauge's 0.01 deg pixel, over the run window; ratio sum(MRMS) / sum(gauge) over wet hours (either >= 0.25 mm), by gauge intensity class
  * daily: ACIS (CoCoRaHS, COOP, GHCN-D) 24-h totals vs Pass2 summed over the same 24 h (the gauge's observation hour, local standard
    time = UTC-5); gauge-days overlapping the run window by >= 6 h, pairs where either is >= 2.5 mm
  * timing: at ASOS 1-min gauges inside the box, the gauge's 15-min rain vs Pass2 spread evenly over the hour (the hourly run) and vs Pass2
    split by the PrecipRate (2-min) radar timing (LF_RAIN_DT): peak 15-min intensity, and the within-hour shares (hours with >= 2 mm in both)
  * intensity: over the box, the peak 5- and 15-min rate after the radar split / the hourly rate, where the Pass2 hour >= 5 mm
  * radar-only vs Pass2: box-mean PrecipRate-integrated hour / Pass2 hour
"""
import json, os, sys, glob
import numpy as np
import pandas as pd

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')
sys.path.insert(0, os.path.join(ROOT, 'sim', 'colab'))
import lf_subhourly as SH  # noqa: E402

DATA = f'{ROOT}/docs/proto/rain/data'
STORMS = [('jul2023', 'flash'), ('aug2023b', 'flash'), ('sep2022', 'flash'), ('aug2023', 'flash'), ('sep2023', 'good'), ('aug2021', 'good'), ('jul2021', 'good')]
CLASSES = [(0.25, 2.5), (2.5, 10.0), (10.0, 25.0), (25.0, 1e9)]


def ts(a): return [pd.Timestamp(str(x)) for x in a]


def load_npz(p):
    if not os.path.exists(p): return None
    z = np.load(p, allow_pickle=False); return {k: z[k] for k in z.files}


def pix(lat, lon, la, lo):
    i = int(np.argmin(np.abs(lat - la))); j = int(np.argmin(np.abs(lon - lo)))
    if abs(lat[i] - la) > 0.006 or abs(lon[j] - lo) > 0.006: return None
    return i, j


def inside(bb, lo, la): return bb[0] <= lo <= bb[2] and bb[1] <= la <= bb[3]


def gauge_hourly(g, hours):
    """{hour_end: mm} for clock hours (h-1, h]."""
    out = {}
    if g.get('five_min'):
        s = pd.Series({pd.Timestamp(t): (v, c) for t, v, c in g['five_min']})
        for h in hours:
            b = [s.get(h - pd.Timedelta(minutes=5 * k)) for k in range(12)]
            if any(x is None for x in b): continue
            n = sum(x[1] for x in b); v = [x[0] for x in b]
            if n >= 54 and all(x is not None for x in v): out[h] = float(sum(v))
    elif g.get('series'):     # USGS iv increments
        s = pd.Series({pd.Timestamp(t): v for t, v in g['series'] if v is not None})
        for h in hours:
            w = s[(s.index > h - pd.Timedelta(hours=1)) & (s.index <= h)]
            if len(w) >= 3: out[h] = float(w.sum())
    return out


def classes(pairs):
    out = []
    for lo, hi in CLASSES:
        p = [(g, r) for g, r in pairs if lo <= g < hi]
        if not p: out.append(dict(gauge_mm=f'{lo:g}-{hi:g}' if hi < 1e8 else f'>={lo:g}', n=0)); continue
        G = sum(x[0] for x in p); R = sum(x[1] for x in p)
        out.append(dict(gauge_mm=f'{lo:g}-{hi:g}' if hi < 1e8 else f'>={lo:g}', n=len(p), gauge_sum=round(G, 1), mrms_sum=round(R, 1), ratio=round(R / G, 2),
                        mean_diff_mm=round(float(np.mean([r - g for g, r in p])), 2)))
    return out


def ratio(pairs, thr):
    p = [(g, r) for g, r in pairs if max(g, r) >= thr]
    if not p: return dict(n=0)
    G = sum(x[0] for x in p); R = sum(x[1] for x in p)
    return dict(n=len(p), gauge_sum=round(G, 1), mrms_sum=round(R, 1), ratio=round(R / G, 2) if G > 0 else None,
                median_pair_ratio=round(float(np.median([r / g for g, r in p if g >= thr])), 2) if any(g >= thr for g, _ in p) else None)


def storm(sid):
    D = f'{DATA}/{sid}'
    if not os.path.exists(f'{D}/gauges.json'): return None
    G = json.load(open(f'{D}/gauges.json')); bb = G['box_lonlat']; t0 = pd.Timestamp(G['t0']).tz_localize(None); H = G['hours']
    hours = [t0 + pd.Timedelta(hours=h + 1) for h in range(H)]
    R = load_npz(f'{D}/mrms_region.npz'); B = load_npz(f'{D}/mrms_box.npz')
    out = dict(storm=sid, t0=G['t0'], hours=H)
    pr = json.load(open(f'{D}/products.json')) if os.path.exists(f'{D}/products.json') else {}
    day = f'{t0:%Y-%m-%d}'
    out['products_on_t0_day'] = {k: v.get(day, {}) for k, v in pr.items() if not k.startswith('_')}
    if R is None: return out
    rt = ts(R['pass2_t']); rix = {t: k for k, t in enumerate(rt)}; P2 = R['pass2'].astype(np.float32)
    # ---------------- hourly gauges
    hp, hp_box, per_g = [], [], []
    for g in G['asos'] + G['usgs']:
        if not (g.get('five_min') or g.get('series')): continue
        ij = pix(R['lat'], R['lon'], g['lat'], g['lon'])
        if ij is None: continue
        gh = gauge_hourly(g, hours); pairs = []
        for h, v in gh.items():
            if h in rix:
                r = float(np.nan_to_num(P2[rix[h], ij[0], ij[1]]))
                if max(v, r) >= 0.25: pairs.append((v, r))
        ib = inside(bb, g['lon'], g['lat'])
        per_g.append(dict(id=g['id'], name=g.get('name'), kind='asos_1min' if g.get('five_min') else 'usgs', in_box=ib, hours=len(gh),
                          gauge_total_mm=round(sum(gh.values()), 1), mrms_total_mm=round(sum(float(np.nan_to_num(P2[rix[h], ij[0], ij[1]])) for h in gh if h in rix), 1)))
        hp += pairs
        if ib: hp_box += pairs
    out['hourly'] = dict(gauges=per_g, n_gauges=len([g for g in per_g if g['hours']]), n_in_box=len([g for g in per_g if g['hours'] and g['in_box']]),
                         all=ratio(hp, 0.25), in_box=ratio(hp_box, 0.25), by_class=classes(hp))
    out['_hourly_pairs'] = hp
    # ---------------- daily gauges (ACIS)
    dp, dp_box, dg = [], [], []
    for g in G['acis']:
        ij = pix(R['lat'], R['lon'], g['lat'], g['lon'])
        if ij is None: continue
        for d, mm, hr in g['daily']:
            if mm is None: continue
            if hr is None or hr in ('', -1): hr = 7 if g.get('cocorahs') else None
            if hr is None: continue
            try: hr = int(hr)
            except (TypeError, ValueError): continue
            hr = 24 if hr == 0 else hr          # hour 0 / 24 = midnight
            end = pd.Timestamp(d) + pd.Timedelta(hours=hr + 5); start = end - pd.Timedelta(hours=24)
            ov = (min(end, hours[-1]) - max(start, t0)).total_seconds() / 3600
            if ov < 6: continue
            hh = [start + pd.Timedelta(hours=k + 1) for k in range(24)]
            if not all(h in rix for h in hh): continue
            r = float(sum(np.nan_to_num(P2[rix[h], ij[0], ij[1]]) for h in hh))
            if max(mm, r) < 2.5: continue
            ib = inside(bb, g['lon'], g['lat'])
            dp.append((mm, r)); dg.append(dict(id=g['id'], name=g['name'], cocorahs=g.get('cocorahs'), in_box=ib, date=d, obs_hour_lst=hr, gauge_mm=mm, mrms_mm=round(r, 1)))
            if ib: dp_box.append((mm, r))
    out['daily'] = dict(pairs=dg, n_gauges=len({x['id'] for x in dg}), n_in_box=len({x['id'] for x in dg if x['in_box']}), all=ratio(dp, 2.5), in_box=ratio(dp_box, 2.5),
                        cocorahs=ratio([(x['gauge_mm'], x['mrms_mm']) for x in dg if x['cocorahs']], 2.5))
    # ---------------- radar timing and intensity in the box
    if B is None or not len(B.get('preciprate_t', [])): return out
    bt = ts(B['pass2_t']); bix = {t: k for k, t in enumerate(bt)}; BP2 = np.nan_to_num(B['pass2'].astype(np.float32))
    prt = ts(B['preciprate_t']); PR = B['preciprate'].astype(np.float32)
    files = {t: PR[k] for k, t in enumerate(prt)}
    W5, W15, rad_h = {}, {}, {}
    for h in hours:
        hs = h - pd.Timedelta(hours=1); fh = {t: c for t, c in files.items() if hs - pd.Timedelta(minutes=2) <= t <= h + pd.Timedelta(minutes=2)}
        A5, cov = SH.hour_bins('preciprate', fh, hs, 5) if fh else (None, 0)
        if A5 is None: continue
        W5[h] = SH.weights_from_bins(A5); W15[h] = SH.weights_from_bins(A5.reshape(4, 3, *A5.shape[1:]).sum(1)); rad_h[h] = A5.sum(0)
    # radar-only vs Pass2 (box mean, hours with Pass2 box mean >= 1 mm)
    rr = [(float(BP2[bix[h]].mean()), float(rad_h[h].mean())) for h in hours if h in bix and h in rad_h and BP2[bix[h]].mean() >= 1.0]
    out['radar_vs_pass2'] = dict(hours=len(rr), pass2_mm=round(sum(a for a, _ in rr), 1), radar_mm=round(sum(b for _, b in rr), 1),
                                 ratio=round(sum(b for _, b in rr) / max(sum(a for a, _ in rr), 1e-6), 2) if rr else None)
    # intensity: peak sub-hourly rate after the split / hourly rate, pixels-hours with Pass2 >= 5 mm
    f5, f15, top = [], [], []
    for h in hours:
        if h not in bix or h not in W5: continue
        m = BP2[bix[h]] >= 5.0
        if m.any(): f5 += list(W5[h].max(0)[m] * 12); f15 += list(W15[h].max(0)[m] * 4); top += list(BP2[bix[h]][m])
    pk_h = max((float(BP2[bix[h]].max()) for h in hours if h in bix), default=0.0)
    pk_5 = max((float((BP2[bix[h]][None] * W5[h]).max() * 12) for h in hours if h in bix and h in W5), default=0.0)
    pk_15 = max((float((BP2[bix[h]][None] * W15[h]).max() * 4) for h in hours if h in bix and h in W15), default=0.0)
    out['intensity'] = dict(pixel_hours_ge5mm=len(f5), peak_factor_5min_median=round(float(np.median(f5)), 2) if f5 else None,
                            peak_factor_15min_median=round(float(np.median(f15)), 2) if f15 else None,
                            peak_factor_5min_p90=round(float(np.percentile(f5, 90)), 2) if f5 else None,
                            box_max_rate_mmh=dict(hourly=round(pk_h, 1), split_15min=round(pk_15, 1), split_5min=round(pk_5, 1)),
                            hours_with_radar_timing=len(W5), hours=H)
    # timing at ASOS 1-min gauges inside the crop
    tim = []
    for g in G['asos']:
        if not g.get('five_min'): continue
        ij = pix(B['lat'], B['lon'], g['lat'], g['lon'])
        if ij is None: continue
        s = {pd.Timestamp(t): (v, c) for t, v, c in g['five_min']}
        rows = []
        for h in hours:
            b = [s.get(h - pd.Timedelta(minutes=5 * (11 - k))) for k in range(12)]       # 5-min bins in time order
            if any(x is None or x[0] is None for x in b) or sum(x[1] for x in b) < 54 or h not in bix or h not in W5: continue
            g5 = np.array([x[0] for x in b]); p = float(BP2[bix[h], ij[0], ij[1]]); w = W5[h][:, ij[0], ij[1]]
            rows.append((h, g5, p, w))
        if not rows: continue
        g15 = np.concatenate([r[1].reshape(4, 3).sum(1) for r in rows]); flat15 = np.concatenate([np.full(4, r[2] / 4) for r in rows])
        rad15 = np.concatenate([(r[2] * r[3]).reshape(4, 3).sum(1) for r in rows])
        sh = [(r[1].reshape(4, 3).sum(1) / r[1].sum(), r[3].reshape(4, 3).sum(1)) for r in rows if r[1].sum() >= 2 and r[2] >= 2]
        e = dict(id=g['id'], name=g['name'], in_box=inside(bb, g['lon'], g['lat']), hours=len(rows), gauge_total_mm=round(float(g15.sum()), 1), pass2_total_mm=round(float(flat15.sum()), 1),
                 peak15_mmh=dict(gauge=round(float(g15.max() * 4), 1), hourly_flat=round(float(flat15.max() * 4), 1), radar_split=round(float(rad15.max() * 4), 1)),
                 wet_hours_2mm=len(sh))
        if sh:
            e['share_mae'] = dict(hourly_flat=round(float(np.mean([np.abs(a - 0.25).mean() for a, _ in sh])), 3),
                                  radar_split=round(float(np.mean([np.abs(a - b).mean() for a, b in sh])), 3))
            e['peak_quarter_hit'] = dict(radar_split=round(float(np.mean([np.argmax(a) == np.argmax(b) for a, b in sh])), 2), chance=0.25)
        if g15.max() > 0:
            pk = int(np.argmax(g15)); e['peak15_time_error_min'] = dict(radar_split=int((int(np.argmax(rad15)) - pk) * 15))
        tim.append(e)
    out['timing_asos'] = tim
    return out


def main():
    res = {}
    for sid, kind in STORMS:
        r = storm(sid)
        if r is None: print(sid, 'no data'); continue
        r['kind'] = kind; res[sid] = r
    # gauge factors for LF_RAIN_GAUGE (sim/colab/lf_raingauge.py): daily gauges within the box + 0.1 deg, pairs >= 10 mm
    FAC = dict(_about='per storm: daily gauges (ACIS: CoCoRaHS / COOP) within the box + 0.1 deg, gauge-days overlapping the run by >= 6 h with gauge or '
                      'Pass2 >= 10 mm; ratio = sum(gauge) / sum(Pass2) per gauge, gauges with a ratio outside 1/3-3 dropped (QC); mfb over all of them; min_gauges 5 for a factor (else mfb null)')
    for sid, r in res.items():
        G = json.load(open(f'{DATA}/{sid}/gauges.json')); bb = G['box_lonlat']; acc = {}
        for x in r.get('daily', {}).get('pairs', []):
            g = next(a for a in G['acis'] if a['id'] == x['id'])
            if not (bb[0] - 0.1 <= g['lon'] <= bb[2] + 0.1 and bb[1] - 0.1 <= g['lat'] <= bb[3] + 0.1): continue
            if max(x['gauge_mm'], x['mrms_mm']) < 10: continue
            a = acc.setdefault(x['id'], dict(id=x['id'], name=x['name'], lat=g['lat'], lon=g['lon'], g=0.0, r=0.0)); a['g'] += x['gauge_mm']; a['r'] += x['mrms_mm']
        gs = [dict(a, ratio=round(a['g'] / a['r'], 3)) for a in acc.values() if a['r'] >= 10]
        qc = [a['id'] for a in gs if not (1 / 3 <= a['ratio'] <= 3)]          # QC: a zero / multi-day report, not a rain measurement
        gs = [a for a in gs if a['id'] not in qc]
        sg, sr = sum(a['g'] for a in gs), sum(a['r'] for a in gs)
        FAC[sid] = dict(mfb=round(sg / sr, 3) if len(gs) >= 5 and sr > 0 else None, n=len(gs), qc_dropped=qc, gauge_sum_mm=round(sg, 1), pass2_sum_mm=round(sr, 1),
                        gauges=[dict(id=a['id'], name=a['name'], lat=a['lat'], lon=a['lon'], ratio=a['ratio'], gauge_mm=round(a['g'], 1), pass2_mm=round(a['r'], 1)) for a in gs])
        print(f"gauge factors {sid}: {len(gs)} gauges, mfb {FAC[sid]['mfb']}, per-gauge ratio range "
              f"{min((a['ratio'] for a in gs), default=None)}-{max((a['ratio'] for a in gs), default=None)}")
    json.dump(FAC, open(f'{ROOT}/docs/proto/rain/gauge_factors.json', 'w'), indent=1)
    allp = [p for r in res.values() for p in r.pop('_hourly_pairs', [])]
    res['_pooled'] = dict(hourly_all=ratio(allp, 0.25), hourly_by_class=classes(allp))
    json.dump(res, open(f'{ROOT}/docs/proto/rain/gauges.json', 'w'), indent=1)
    print('| storm | hourly gauges (box) | hourly MRMS/gauge | daily gauges (box) | daily MRMS/gauge (box) | radar/Pass2 | max rate h / 15 / 5 min | ASOS peak 15-min gauge / flat / split |')
    print('|---|---|---|---|---|---|---|---|')
    for sid, r in res.items():
        if sid.startswith('_'): continue
        h = r.get('hourly', {}); d = r.get('daily', {}); i = r.get('intensity', {}); rv = r.get('radar_vs_pass2', {})
        t = '; '.join(f"{e['id']} {e['peak15_mmh']['gauge']}/{e['peak15_mmh']['hourly_flat']}/{e['peak15_mmh']['radar_split']}" for e in r.get('timing_asos', []))
        bm = i.get('box_max_rate_mmh', {})
        print(f"| {sid} | {h.get('n_gauges')} ({h.get('n_in_box')}) | {h.get('all', {}).get('ratio')} (n {h.get('all', {}).get('n')}) | {d.get('n_gauges')} ({d.get('n_in_box')}) | "
              f"{d.get('all', {}).get('ratio')} ({d.get('in_box', {}).get('ratio')}) | {rv.get('ratio')} | {bm.get('hourly')} / {bm.get('split_15min')} / {bm.get('split_5min')} | {t} |")
    print('pooled hourly:', res['_pooled'])


if __name__ == '__main__':
    main()
