"""Experimental HRRR rain treatments for the forecast flood model (docs/proto/forecast/ENSEMBLE.md).  Off unless the env flags are set;
hrrr_rain.hourly() hands over to model_hourly() only when it samples for the model grid and LF_HRRR_LAG or LF_HRRR_QMAP is set, so the live
forecast (forecast.yml) and the gate are unchanged.

LF_HRRR_LAG='1,2,3,4,6,12,18'   time-lagged ensemble: besides the cycle `init` (lag 0), the cycles issued 1, 2, ... hours earlier, each read at the
                                forecast hour valid for the same model hour (fh + lag).  A member whose horizon ends before a model hour is left
                                out of that hour.  Each member is sampled the same way as the main cycle (bilinear, LF_HRRR_NBHD if set, QM if set).
LF_HRRR_LAG_STAT=mean|max|pNN   how the members are combined, cell by cell and hour by hour (default mean).
LF_HRRR_QMAP='file.json#key'    quantile mapping of the sampled hourly accumulations (HRRR -> MRMS), map maps[key] = {x: [...], y: [...]} from
                                proto/forecast_ens.py qmfit (leave-one-storm-out keys 'loso_<storm>/<variant>').  Below x[0] the ratio y0/x0 is
                                applied, above x[-1] the ratio y[-1]/x[-1]; zero stays zero.
"""
import os, json, time
import numpy as np


def load_qmap(spec=None):
    spec = spec if spec is not None else os.environ.get('LF_HRRR_QMAP')
    if not spec: return None
    path, key = spec.split('#', 1); M = json.load(open(path))['maps'][key]
    return np.asarray(M['x'], np.float64), np.asarray(M['y'], np.float64)


def apply_qmap(v, qm):
    if qm is None: return v
    x, y = qm; v = np.asarray(v, np.float32); out = np.interp(v, x, y).astype(np.float32)
    lo = v < x[0]; out[lo] = v[lo] * (y[0] / x[0]); hi = v > x[-1]; out[hi] = v[hi] * (y[-1] / x[-1]); out[v <= 0] = 0
    return np.maximum(out, 0)


def combine(vals, stat):
    A = np.stack(vals)
    if stat == 'mean': return A.mean(0)
    if stat == 'max': return A.max(0)
    if stat.startswith('p'): return np.percentile(A, float(stat[1:]), axis=0).astype(np.float32)
    raise ValueError(stat)


def model_hourly(init, hours, sample, workers=12, log=print):
    """Model hours 0..hours-1 (forecast hours 1..hours of `init`), optionally a time-lagged ensemble of earlier cycles, optionally quantile-mapped."""
    import pandas as pd, hrrr_rain
    from concurrent.futures import ThreadPoolExecutor
    lags = [0] + [int(v) for v in (os.environ.get('LF_HRRR_LAG') or '').split(',') if v.strip()]
    stat = os.environ.get('LF_HRRR_LAG_STAT', 'mean'); qm = load_qmap(); init = pd.Timestamp(init)
    jobs = []
    for L in lags:
        c = init - pd.Timedelta(hours=L); H = hrrr_rain.horizon(c)
        for k in range(hours):
            if k + 1 + L <= H: jobs.append((L, c, k, k + 1 + L))

    def one(j):
        L, c, k, fh = j
        for t in range(3):
            try:
                m = hrrr_rain.apcp(c, fh)
                return j, (None if m is None else apply_qmap(sample(m), qm))
            except Exception as e:
                if t == 2: log(f'  HRRR {c:%d %H}z f{fh:02d} failed: {e!r}'[:160])
                time.sleep(3 + 5 * t)
        return j, None
    got = {}
    with ThreadPoolExecutor(workers) as ex:
        for (L, c, k, fh), v in ex.map(one, jobs):
            if v is not None: got.setdefault(k, {})[L] = v
    out, used = [], []
    for k in range(hours):
        d = got.get(k, {})
        if not d: out.append(None); used.append(0); continue
        out.append(d[0] if len(lags) == 1 else combine(list(d.values()), stat).astype(np.float32)); used.append(len(d))
    log(f'hrrr_ens: init {init:%Y-%m-%d %H}z lags {lags} stat {stat if len(lags) > 1 else "-"} qmap {os.environ.get("LF_HRRR_QMAP") or "-"}; '
        f'members per hour min/max {min(used)}/{max(used)}')
    return out
