"""Continuous antecedent-wetness curve number from NWM soil saturation (opt-in LF_CN_AMC=nwm in w9_lisflood.py; docs/proto/runoff/NWM_AMC.md,
pre-registration docs/proto/runoff/NWM_AMC_PREREG.md).

Input: theta = NOAA National Water Model SOILSAT_TOP (fraction of saturation of the top 40 cm of soil, 0-1) at the run's t0, averaged over
the model box.  Read, in this order, from
    LF_NWM_SOILSAT=<value>                         (explicit override)
    LF_NWM_SOILSAT_JSON=<path>[storms][STORM]       (default docs/proto/runoff/nwm_soilsat.json, made on Actions by proto/runoff/nwm_soilsat.py;
                                                    no network is needed where the model runs, e.g. on Turing)
A missing value stops the run (it never silently falls back to AMC II).

Mapping (fixed before any run; no parameter is fitted to any storm's score):
    S_II  = 25400 / CN_II - 254                     (mm; the TR-55 potential retention at AMC II, per cell, composite CN as LF_LOSS=cn builds it)
    S     = S_II * (1 - theta) / (1 - THETA_CAL)    (retention proportional to the unfilled share of the soil store)
    CN    = 25400 / (254 + S), clipped to [CN_I, CN_III] of that cell (Chow, Maidment & Mays 1988 closed forms, as LF_CN_AMC=I / III)
then LF_CN_SCALE and the water-cell override follow exactly as for every other AMC.

  * The form "retention = unfilled soil storage, falling linearly as antecedent soil water rises" is the soil-moisture-accounting reading
    of SCS-CN (Mishra & Singh 2002, 2003; Michel, Andreassian & Perrin 2005, Water Resour. Res. 41, W02011, doi:10.1029/2004WR003191).
  * The single anchor THETA_CAL is the calibration storm only: LF_CN_SCALE = 0.88 was calibrated at AMC II on the Sept 2023 Leominster
    storm, so the mapping gives AMC II (CN unchanged) at the SOILSAT_TOP of that storm at its t0 (sep2023 in nwm_soilsat.json).  Wetter
    than sep2023 -> CN rises toward CN_III; drier -> falls toward CN_I.  sep2023 itself is reproduced exactly.
"""
import os, json
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_JSON = os.path.normpath(os.path.join(HERE, '..', '..', 'docs', 'proto', 'runoff', 'nwm_soilsat.json'))
THETA_CAL = 0.7262  # sep2023 (calibration storm) box-mean SOILSAT_TOP at t0 2023-09-11T16Z, docs/proto/runoff/nwm_soilsat.json; fixed in NWM_AMC_PREREG.md


def cn_bounds(cn2):
    cn2 = np.asarray(cn2, np.float64)
    return 4.2 * cn2 / (10.0 - 0.058 * cn2), 23.0 * cn2 / (10.0 + 0.13 * cn2)


def cn_nwm(cn2, theta, theta_cal=None):
    """Composite CN at AMC II (array) + box-mean SOILSAT_TOP -> CN (float64 array)."""
    tc = THETA_CAL if theta_cal is None else theta_cal
    if tc is None: raise SystemExit('lf_nwm_soil.THETA_CAL is not set')
    cn2 = np.asarray(cn2, np.float64); th = float(np.clip(theta, 0.0, 1.0))
    s2 = 25400.0 / np.maximum(cn2, 1e-6) - 254.0
    s = np.maximum(s2, 0.0) * (1.0 - th) / (1.0 - tc)
    lo, hi = cn_bounds(cn2)
    return np.clip(25400.0 / (254.0 + s), lo, hi)


def position(cn, cn2):
    """Where CN sits between CN_I (0) and CN_III (1); AMC II is at the CN_II position of each cell."""
    lo, hi = cn_bounds(cn2); return (np.asarray(cn, np.float64) - lo) / np.maximum(hi - lo, 1e-9)


def resolve(storm, t0=None, log=print):
    """-> (theta, source string)."""
    if os.environ.get('LF_NWM_SOILSAT'):
        return float(os.environ['LF_NWM_SOILSAT']), 'LF_NWM_SOILSAT'
    p = os.environ.get('LF_NWM_SOILSAT_JSON') or DEFAULT_JSON
    if not os.path.isabs(p) and not os.path.exists(p): p = os.path.normpath(os.path.join(HERE, '..', '..', p))
    J = json.load(open(p)); r = (J.get('storms') or {}).get(storm)
    if not r or r.get('soilsat_top') is None: raise SystemExit(f'LF_CN_AMC=nwm: no SOILSAT_TOP for storm {storm!r} in {p}')
    if t0 and r.get('t0') and str(r['t0'])[:13] != str(t0)[:13]:
        raise SystemExit(f"LF_CN_AMC=nwm: {p} has t0 {r['t0']} for {storm}, the run starts {t0}")
    return float(r['soilsat_top']), f"{os.path.relpath(p, os.path.join(HERE, '..', '..'))} ({r.get('soilsat_source')})"


def selftest():
    ok = []
    cn2 = np.array([36.0, 60.0, 73.0, 79.0, 98.0])
    assert np.allclose(cn_nwm(cn2, 0.7, 0.7), cn2), 'theta = theta_cal must leave CN_II unchanged'
    lo, hi = cn_bounds(cn2)
    assert np.all(cn_nwm(cn2, 0.0, 0.7) >= lo - 1e-9) and np.all(cn_nwm(cn2, 1.0, 0.7) <= hi + 1e-9)
    assert np.allclose(cn_nwm(cn2, 1.0, 0.7), hi), 'saturated top soil -> CN_III'
    w = cn_nwm(cn2, 0.75, 0.7); d = cn_nwm(cn2, 0.6, 0.7)
    assert np.all(w > cn2) and np.all(d < cn2), (w, d)
    seq = [float(cn_nwm(73.0, t, 0.7)) for t in np.linspace(0.4, 0.95, 12)]; assert all(b >= a for a, b in zip(seq, seq[1:])), seq
    # HSG C woods/grass 73 at theta_cal 0.73: theta 0.51 -> about 60 (between CN_I 53 and CN_II), theta 0.77 -> about 76
    assert 58 < float(cn_nwm(73.0, 0.51, 0.73)) < 62 and 75 < float(cn_nwm(73.0, 0.77, 0.73)) < 78
    ok.append('LF_CN_AMC=nwm mapping: identity at theta_cal, monotone in theta, inside [CN_I, CN_III]')
    os.environ['LF_NWM_SOILSAT'] = '0.66'
    try: assert resolve('x') == (0.66, 'LF_NWM_SOILSAT')
    finally: del os.environ['LF_NWM_SOILSAT']
    ok.append('LF_NWM_SOILSAT override')
    return ok


if __name__ == '__main__':
    print(selftest())
