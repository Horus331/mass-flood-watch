"""Precipitation phase for w9_lisflood (LF_PHASE=1; candidate C1 of docs/proto/prospective/storm_2026-11-13_watch.md).

The model otherwise treats all precipitation as rain.  With LF_PHASE=1 each hour's precipitation is split by the 2 m air temperature of
the same hour: liquid fraction 1 above T_HI (2 C), 0 below T_LO (0 C), linear between.  Temperature: HRRR TMP 2 m, the member's own
cycle for forecast hours (fh = hour index after the spin-up), the HRRR analysis (f00) of the hour's end for observed hours.  The frozen
part is kept as snow and not melted within the run (cold storms are short; melt is future work).  Off by default.
"""
import os
import numpy as np

T_LO, T_HI = 0.0, 2.0


def liquid_fraction(t_c):
    return np.clip((np.asarray(t_c, np.float32) - T_LO) / (T_HI - T_LO), 0.0, 1.0)


def tmp2m(init, fh):
    """pygrib message of HRRR 2 m temperature (K) for cycle init at forecast hour fh (0 = analysis), or None."""
    import pygrib, hrrr_rain as HR
    u = HR.url(init, fh); idx = HR._get(u + '.idx')
    if idx is None: return None
    lines = idx.text.strip().split('\n'); tag = ':TMP:2 m above ground:' + ('anl' if fh == 0 else f'{fh} hour fcst')
    for i, ln in enumerate(lines):
        if tag in ln:
            st = int(ln.split(':')[1]); en = int(lines[i + 1].split(':')[1]) - 1 if i + 1 < len(lines) else ''
            r = HR._get(u, headers={'Range': f'bytes={st}-{en}'}, timeout=120)
            return pygrib.fromstring(r.content) if r is not None else None
    return None


def apply(RAIN, hour_ends, XX, YY, init=None, spinup=0, log=print):
    """RAIN (h, ny, nx) mm per hour ending hour_ends[k] -> (liquid RAIN, snow water equivalent per cell, summary).
    init: HRRR cycle of a forecast member (None = observed rain for every hour)."""
    import pandas as pd, hrrr_rain as HR
    from concurrent.futures import ThreadPoolExecutor
    def job(k):
        ts = pd.Timestamp(hour_ends[k])
        if init is not None and k >= spinup: cyc, fh = pd.Timestamp(init), k - spinup + 1
        else: cyc, fh = ts, 0
        err = None
        for _ in range(3):
            try:
                m = tmp2m(cyc, fh)
                if m is None and fh == 0: m = tmp2m(ts - pd.Timedelta(hours=1), 1)      # analysis not posted yet: last cycle's f01
                return k, m
            except Exception as e: err = e
        log(f'  LF_PHASE: no 2 m temperature for hour {ts}: {err!r}'[:160]); return k, None
    wet = [k for k in range(len(RAIN)) if float(RAIN[k].max()) > 0]
    with ThreadPoolExecutor(8) as ex: MSG = dict(ex.map(job, wet))
    T = {}; first = next((m for m in MSG.values() if m is not None), None)
    if first is not None:
        nb = os.environ.pop('LF_HRRR_NBHD', None)          # the rain neighbourhood percentile must not touch temperature
        try: samp = HR.LccGrid(first).bilinear(XX, YY)
        finally:
            if nb is not None: os.environ['LF_HRRR_NBHD'] = nb
        for k, m in MSG.items(): T[k] = None if m is None else samp(m) - 273.15
    OUT = RAIN.astype(np.float32).copy(); SWE = np.zeros(RAIN.shape[1:], np.float32); miss = 0; tmin = None
    for k in wet:
        if T.get(k) is None: miss += 1; continue
        f = liquid_fraction(T[k]); SWE += RAIN[k] * (1 - f); OUT[k] = RAIN[k] * f
        tmin = float(T[k].min()) if tmin is None else min(tmin, float(T[k].min()))
    tot = float(RAIN.sum()); S = dict(precip_total_mm_cellsum=tot, frozen_share=float(SWE.sum() / tot) if tot > 0 else 0.0,
                                     swe_max_mm=float(SWE.max()), hours_wet=len(wet), hours_without_temperature=miss, t2m_min_c=tmin)
    log(f"LF_PHASE: {100 * S['frozen_share']:.1f}% of the precipitation frozen (max {S['swe_max_mm']:.1f} mm water as snow), "
        f"min 2 m temperature {tmin if tmin is None else round(tmin, 1)} C; {miss} of {len(wet)} wet hours without a temperature (kept as rain)")
    return OUT, SWE, S


def selftest():
    f = liquid_fraction([-5, 0, 1, 2, 10]); assert np.allclose(f, [0, 0, 0.5, 1, 1]), f
    print('lf_phase selftest ok')


if __name__ == '__main__':
    selftest()
