"""Opt-in gauge adjustment of the MRMS Pass2 rain for w9_lisflood.py (LF_RAIN_GAUGE=mfb|idw; docs/proto/rain/RAIN.md).

Factors come from docs/proto/rain/gauge_factors.json (written by proto/rain/rain_gauges.py): per storm, each daily gauge (CoCoRaHS / COOP,
24-h totals) with its storm ratio gauge / Pass2 (summed over the gauge-days that overlap the run, pairs >= 10 mm), and the mean-field
bias mfb = sum(gauge) / sum(Pass2) over the gauges in the box + 0.1 deg.

  mfb : every cell and hour x mfb (capped to [LF_RAIN_GAUGE_CAP_LO, LF_RAIN_GAUGE_CAP_HI], default 0.67-1.5)
  idw : multiplicative field, inverse-distance-squared weighting of the per-gauge log ratios (each capped), with a pseudo-gauge of the
        mfb at LF_RAIN_GAUGE_R0_KM (10 km) so that far from the gauges the field relaxes to the mean-field bias; then capped
The factor multiplies the hourly Pass2 grids before the runoff loss (so the CN loss sees the adjusted rain), constant in time.
"""
import json, os
import numpy as np

DEFAULT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'docs', 'proto', 'rain', 'gauge_factors.json')


def km_dist(lat_c, lon_c, la, lo):
    LA, LO = np.meshgrid(np.asarray(lat_c, float), np.asarray(lon_c, float), indexing='ij')
    dx = (LO - lo) * 111.32 * np.cos(np.radians(la)); dy = (LA - la) * 110.57
    return np.hypot(dx, dy)


def field(lat_c, lon_c, F, mode, cap=(0.67, 1.5), r0_km=10.0):
    mfb = float(np.clip(F['mfb'], *cap))
    if mode == 'mfb': return np.full((len(lat_c), len(lon_c)), mfb, np.float32)
    if mode != 'idw': raise SystemExit(f'LF_RAIN_GAUGE must be mfb or idw, not {mode!r}')
    num = np.full((len(lat_c), len(lon_c)), np.log(mfb) / r0_km ** 2); den = np.full_like(num, 1.0 / r0_km ** 2)
    for g in F['gauges']:
        w = 1.0 / np.maximum(km_dist(lat_c, lon_c, g['lat'], g['lon']), 1.0) ** 2
        num += w * np.log(np.clip(g['ratio'], *cap)); den += w
    return np.clip(np.exp(num / den), *cap).astype(np.float32)


def adjust(RAIN, storm, lat_c, lon_c, mode, path=None, log=print):
    """-> (RAIN x factor, report). Refuses (SystemExit) when the storm has no usable gauge factors."""
    path = path or os.environ.get('LF_RAIN_GAUGE_FILE') or DEFAULT
    allf = json.load(open(path)); F = allf.get(storm)
    if not F or F.get('mfb') is None: raise SystemExit(f'LF_RAIN_GAUGE: no gauge factors for {storm} in {path}')
    cap = (float(os.environ.get('LF_RAIN_GAUGE_CAP_LO', '0.67')), float(os.environ.get('LF_RAIN_GAUGE_CAP_HI', '1.5')))
    f = field(lat_c, lon_c, F, mode, cap, float(os.environ.get('LF_RAIN_GAUGE_R0_KM', '10')))
    rep = dict(mode=mode, mfb=F['mfb'], gauges=len(F['gauges']), cap=list(cap), factor_min=round(float(f.min()), 3), factor_mean=round(float(f.mean()), 3),
               factor_max=round(float(f.max()), 3), source=os.path.relpath(path, os.path.join(os.path.dirname(DEFAULT), '..', '..', '..')))
    log(f'LF_RAIN_GAUGE={mode}: rain x {rep["factor_min"]}-{rep["factor_max"]} (mean {rep["factor_mean"]}), mfb {F["mfb"]}, {len(F["gauges"])} gauges')
    return (np.asarray(RAIN, np.float32) * f[None]).astype(np.float32), rep


def selftest():
    lat = np.linspace(42.30, 42.20, 11); lon = np.linspace(-71.90, -71.75, 16)
    F = dict(mfb=1.2, gauges=[dict(lat=42.25, lon=-71.80, ratio=2.5), dict(lat=42.29, lon=-71.89, ratio=0.9)])
    m = field(lat, lon, F, 'mfb'); assert np.allclose(m, 1.2)
    f = field(lat, lon, F, 'idw'); assert f.max() <= 1.5 + 1e-6 and f.min() >= 0.67 - 1e-6
    i = np.argmin(abs(lat - 42.25)); j = np.argmin(abs(lon + 71.80)); assert f[i, j] > 1.45            # at the wet gauge: its (capped) ratio
    i = np.argmin(abs(lat - 42.29)); j = np.argmin(abs(lon + 71.89)); assert 0.85 < f[i, j] < 1.0     # at the dry gauge
    assert abs(field(lat, lon, dict(mfb=1.2, gauges=[]), 'idw').mean() - 1.2) < 1e-5
    return ['LF_RAIN_GAUGE: mean-field factor; IDW log-ratio field honours gauges, relaxes to the mfb, capped']
