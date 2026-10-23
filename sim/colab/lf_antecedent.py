"""Antecedent moisture condition (AMC) for the curve-number loss in w9_lisflood.py (opt-in LF_CN_AMC=auto; docs/proto/runoff/AMC.md).

LF_LOSS=cn uses the TR-55 curve number at AMC II (average antecedent wetness) for every storm unless LF_CN_AMC says otherwise.
LF_CN_AMC=auto chooses AMC I / II / III per run from the 5-day antecedent rain P5 (box mean, mm), with the standard NEH-4
growing-season thresholds, fixed in advance and never fitted:

    P5 < 35 mm  -> AMC I   (dry)        35 <= P5 <= 53 mm -> AMC II        P5 > 53 mm -> AMC III (wet)

(NEH-4 table 4.2: 1.4 / 2.1 in.).  All catalogue storms are June-September, i.e. growing season.

P5 = sum of the five MRMS MultiSensor QPE 24H Pass2 grids valid at t0, t0 - 24 h, ... t0 - 96 h (AWS noaa-mrms-pds), i.e. the
120 h of rain before the model start t0, averaged over the MRMS pixels inside the box.  A missing 24H grid is rebuilt from the 24
hourly Pass2 grids of that day; if that fails too the run stops (a partial sum would silently look dry).  LF_ANTE_P5_MM=<mm>
skips the download (e.g. from docs/proto/runoff/antecedent.json).

The class conversions are the usual closed forms of the NEH-4 table 10.1 columns (Chow, Maidment & Mays 1988, eq. 5.5.4-5.5.5),
applied to the composite (pervious + impervious) CN before LF_CN_SCALE, as LF_LOSS=cn already did for LF_CN_AMC=III:

    CN(I) = 4.2 CN(II) / (10 - 0.058 CN(II))        CN(III) = 23 CN(II) / (10 + 0.13 CN(II))
"""
import os, gzip, time
import numpy as np

S3 = 'https://noaa-mrms-pds.s3.amazonaws.com/CONUS'
THRESH_MM = (35.0, 53.0)        # NEH-4 growing season: < 1.4 in AMC I, > 2.1 in AMC III (fixed in advance, docs/proto/runoff/AMC.md)


def amc_class(p5_mm, thresh=THRESH_MM):
    return 'I' if p5_mm < thresh[0] else ('III' if p5_mm > thresh[1] else 'II')


def cn_amc(cn, amc):
    """CN at AMC II -> CN at AMC `amc` ('I', 'II', 'III')."""
    cn = np.asarray(cn, np.float64)
    if amc == 'I': return 4.2 * cn / (10.0 - 0.058 * cn)
    if amc == 'III': return 23.0 * cn / (10.0 + 0.13 * cn)
    return cn


def _get(url, tries=3):
    import requests
    for k in range(tries):
        try:
            r = requests.get(url, timeout=120)
            if r.status_code == 200: return r.content
            if r.status_code == 404: return None
        except Exception: pass
        time.sleep(3 * (k + 1))
    return None


def _grid(raw, lat_rng, lon_rng):
    """MRMS grib2.gz bytes -> values of the native pixels inside the lat/lon box (mm), or None."""
    import pygrib, tempfile
    with tempfile.NamedTemporaryFile(suffix='.grib2', delete=False) as f: f.write(gzip.decompress(raw)); p = f.name
    try:
        g = pygrib.open(p); m = g[1]; la, lo = m.latlons(); v = np.ma.filled(m.values, np.nan).astype(np.float64); g.close()
    finally: os.remove(p)
    lat1d = la[:, 0]; lon1d = lo[0, :]; lon1d = np.where(lon1d > 180, lon1d - 360, lon1d)
    i = (lat1d >= lat_rng[0]) & (lat1d <= lat_rng[1]); j = (lon1d >= lon_rng[0]) & (lon1d <= lon_rng[1])
    s = v[np.ix_(i, j)]; s[s < 0] = np.nan
    return s


def mrms_acc(ts, product, lat_rng, lon_rng):
    """One MRMS accumulation grid (MultiSensor_QPE_<product>_Pass2) valid at `ts` (pandas Timestamp, UTC) over the box."""
    url = f'{S3}/MultiSensor_QPE_{product}_Pass2_00.00/{ts:%Y%m%d}/MRMS_MultiSensor_QPE_{product}_Pass2_00.00_{ts:%Y%m%d-%H%M%S}.grib2.gz'
    raw = _get(url)
    return None if raw is None else _grid(raw, lat_rng, lon_rng)


def antecedent(t0, lat_rng, lon_rng, days=5, log=print):
    """Box-mean antecedent rain (mm) over the `days` x 24 h before t0, plus per-day values and sources."""
    import pandas as pd
    t0 = pd.Timestamp(t0).tz_localize(None) if pd.Timestamp(t0).tzinfo else pd.Timestamp(t0)
    per, src, tot = [], [], None
    for k in range(days):
        te = t0 - pd.Timedelta(hours=24 * k); g = mrms_acc(te, '24H', lat_rng, lon_rng); how = '24H'
        if g is None:                                  # rebuild the day from hourly Pass2
            hs = [mrms_acc(te - pd.Timedelta(hours=h), '01H', lat_rng, lon_rng) for h in range(24)]
            ok = [h for h in hs if h is not None]
            if len(ok) < 22: raise RuntimeError(f'antecedent day ending {te}: no 24H Pass2 and only {len(ok)}/24 hourly Pass2 grids')
            g = np.nansum(np.stack(ok), 0) * 24.0 / len(ok); how = f'01H x{len(ok)}'
        per.append(float(np.nanmean(g))); src.append(how); tot = g if tot is None else tot + g
        log(f'  antecedent day ending {te:%Y-%m-%d %H}Z: box mean {per[-1]:.1f} mm ({how})')
    return dict(p_mm=float(np.nanmean(tot)), p_max_mm=float(np.nanmax(tot)), p_min_mm=float(np.nanmin(tot)), days=days, per_day_mm=per, sources=src,
                window_utc=[(t0 - pd.Timedelta(hours=24 * days)).strftime('%Y-%m-%dT%H:%MZ'), t0.strftime('%Y-%m-%dT%H:%MZ')], n_pixels=int(np.isfinite(tot).sum()))


def resolve(t0, lat_c, lon_c, log=print):
    """LF_CN_AMC=auto: (class, P5 mm, info).  LF_ANTE_P5_MM overrides the download."""
    if os.environ.get('LF_ANTE_P5_MM'):
        p5 = float(os.environ['LF_ANTE_P5_MM']); info = dict(p_mm=p5, source='LF_ANTE_P5_MM')
    else:
        info = antecedent(t0, (float(np.min(lat_c)), float(np.max(lat_c))), (float(np.min(lon_c)), float(np.max(lon_c))), log=log); p5 = info['p_mm']
        info['source'] = 'MRMS MultiSensor QPE 24H Pass2 (AWS)'
    return amc_class(p5), p5, info


def selftest():
    ok = []
    assert amc_class(10) == 'I' and amc_class(34.9) == 'I' and amc_class(35) == 'II' and amc_class(53) == 'II' and amc_class(53.1) == 'III'
    ok.append('NEH-4 growing-season classes: < 35 mm I, 35-53 mm II, > 53 mm III')
    # NEH-4 table 10.1 (CN II -> I / III): 60 -> 40 / 78, 70 -> 51 / 85, 80 -> 63 / 91, 90 -> 78 / 96 (closed forms within 2)
    for c2, c1, c3 in ((60, 40, 78), (70, 51, 85), (80, 63, 91), (90, 78, 96)):
        assert abs(cn_amc(c2, 'I') - c1) < 2 and abs(cn_amc(c2, 'III') - c3) < 2, (c2, cn_amc(c2, 'I'), cn_amc(c2, 'III'))
    assert cn_amc(75.0, 'II') == 75.0 and abs(cn_amc(98, 'III') - 99.1) < 0.2 and cn_amc(98, 'I') < 98
    ok.append('CN(I), CN(III) closed forms match NEH-4 table 10.1 within 2 CN')
    os.environ['LF_ANTE_P5_MM'] = '60'
    try: assert resolve('2021-07-09T08:00Z', [42.0, 42.2], [-72.0, -71.8])[:2] == ('III', 60.0)
    finally: del os.environ['LF_ANTE_P5_MM']
    ok.append('LF_ANTE_P5_MM override (no download)')
    return ['lf_antecedent: ' + o for o in ok]


if __name__ == '__main__':
    for o in selftest(): print('ok  ', o)
