"""Snowpack, melt and frozen ground for the flood engine (hourly, per cell; numpy or cupy).

Why: the engine treated every millimetre of winter precipitation as rain landing on unfrozen soil.  In Massachusetts the big
winter floods are rain-on-snow on frozen ground (Dec 18 2023, Jan 1996), so three things matter:
  1. phase: snow is stored on the ground instead of running off;
  2. melt: the pack releases water later (temperature-index melt plus extra melt from warm rain falling on it);
  3. frozen soil: infiltration is cut when the ground has been below freezing.

State per cell (mm of water):  swe (ice), liq (liquid held in the pack), frost (continuous frozen-ground index, degC-days).
Each hour:  inputs precip P (mm/h, all phases), air temperature T (degC), optional snow fraction from the radar phase flag.
Outputs:    water reaching the ground (rain passing through + melt released, mm/h) and the infiltration multiplier.

Methods (standard, simple, documented so they can be cited and swapped):
  * rain/snow partition: radar phase flag when given, else linear ramp between T_SNOW and T_RAIN (U.S. Army Corps 1956 style).
  * melt: degree-day  M = DDF * max(T - T_MELT, 0) / 24  (mm/h) + rain-on-snow  M_r = P_rain * c_w * max(T, 0) / L_f
    (heat carried by rain: c_w/L_f = 4.19/334 per degC  -> 0.0125 mm melt per mm rain per degC).
  * pack liquid storage: up to LWHC x swe is held; the rest drains (refreezes when T < 0).
  * frozen ground: continuous frozen-ground index (Molnau & Bissell 1983):  CFGI_t = A * CFGI_{t-1} - T * exp(-0.4 * K * D)
    with A = 0.97 daily decay, K = 0.5 /cm, D = snow depth (cm); soil is treated as frozen above CFGI_FROZEN (83 degC-days),
    which cuts infiltration to FROZEN_INF.  Applied hourly with A ** (1/24) and T / 24.
Parameter values are defaults pending the research note docs/research/snow.md; every one is a module constant.
"""
import math

T_SNOW, T_RAIN = 0.0, 2.0        # degC: all snow below T_SNOW, all rain above T_RAIN, linear between
T_MELT = 0.0                     # degC
DDF = 3.0                        # mm / degC / day (forested New England pack; open terrain ~4-5)
LWHC = 0.05                      # liquid water holding capacity, fraction of swe
REFREEZE = 1.0                   # mm / degC / day of held liquid refreezing below 0 degC
RHO_SNOW = 0.25                  # bulk density (water = 1) to turn swe into depth for the frost index
CFGI_A, CFGI_K = 0.97, 0.5
CFGI_FROZEN = 83.0               # degC-days
FROZEN_INF = 0.1                 # infiltration multiplier on frozen soil


class Snowpack:
    def __init__(self, shape, xp, swe0=None, frost0=None):
        self.xp = xp
        self.swe = xp.zeros(shape, xp.float32) if swe0 is None else xp.asarray(swe0, xp.float32).copy()
        self.liq = xp.zeros(shape, xp.float32)
        self.frost = xp.zeros(shape, xp.float32) if frost0 is None else xp.asarray(frost0, xp.float32).copy()
        self.melt_total = xp.zeros(shape, xp.float32)     # diagnostics
        self.snow_total = xp.zeros(shape, xp.float32)

    def snow_fraction(self, T, flag_snow=None):
        """Share of precipitation falling as snow: the radar phase flag when given (1 snow, 0 rain, between = mixed), else temperature."""
        xp = self.xp
        if flag_snow is not None: return xp.clip(xp.asarray(flag_snow, xp.float32), 0, 1)
        return xp.clip((T_RAIN - T) / (T_RAIN - T_SNOW), 0, 1).astype(xp.float32)

    def step(self, P, T, flag_snow=None, hours=1.0):
        """Advance one interval.  P mm over the interval, T degC.  Returns (water_to_ground_mm, infiltration_multiplier)."""
        xp = self.xp
        P = xp.asarray(P, xp.float32); T = xp.asarray(T, xp.float32)
        fs = self.snow_fraction(T, flag_snow)
        snow = P * fs; rain = P - snow
        self.swe += snow; self.snow_total += snow
        has = self.swe > 0
        warm = xp.maximum(T - T_MELT, 0)
        melt = DDF * warm * (hours / 24.0) + rain * 0.0125 * xp.maximum(T, 0)
        melt = xp.where(has, xp.minimum(melt, self.swe), 0).astype(xp.float32)
        self.swe -= melt; self.melt_total += melt
        # rain and melt enter the pack's liquid store; what it cannot hold drains to the ground
        self.liq = xp.where(has, self.liq + rain + melt, 0)
        refr = xp.where(T < 0, xp.minimum(self.liq, REFREEZE * (-T) * (hours / 24.0)), 0)
        self.liq -= refr; self.swe += refr
        cap = LWHC * self.swe
        out = xp.where(has, xp.maximum(self.liq - cap, 0), rain).astype(xp.float32)
        self.liq = xp.where(has, xp.minimum(self.liq, cap), 0).astype(xp.float32)
        # frozen-ground index (decays when warm, grows when cold, insulated by snow depth)
        depth_cm = self.swe / RHO_SNOW / 10.0
        a = CFGI_A ** (hours / 24.0)
        self.frost = xp.maximum(a * self.frost - T * (hours / 24.0) * xp.exp(-0.4 * CFGI_K * depth_cm), 0).astype(xp.float32)
        inf = xp.where(self.frost >= CFGI_FROZEN, FROZEN_INF, 1.0).astype(xp.float32)
        return out, inf


def spinup_frost(daily_mean_T, xp, depth_cm=None):
    """Frozen-ground index at storm start from daily mean temperatures before it (list of grids, oldest first)."""
    f = None
    for T in daily_mean_T:
        T = xp.asarray(T, xp.float32); d = 0 if depth_cm is None else depth_cm
        f = xp.maximum((0 if f is None else CFGI_A * f) - T * xp.exp(-0.4 * CFGI_K * d), 0)
    return f


def selftest():
    import numpy as np
    xp = np
    # 1. cold storm: 20 mm at -5 degC all stays on the ground as snow
    s = Snowpack((1,), xp); out, inf = s.step(np.array([20.0]), np.array([-5.0]))
    assert out[0] == 0 and abs(s.swe[0] - 20) < 1e-5, (out, s.swe)
    # 2. warm rain on that pack: 10 mm at +8 degC over 6 h melts some snow; mass is conserved
    tot_out = 0.0
    for _ in range(6): o, _ = s.step(np.array([10 / 6]), np.array([8.0])); tot_out += float(o[0])
    stored = float(s.swe[0] + s.liq[0])
    assert abs((20 + 10) - (tot_out + stored)) < 1e-3, ('mass', tot_out, stored)
    assert tot_out > 10, 'rain-on-snow should release more than the rain alone'
    # 3. no snow, warm: rain passes straight through
    s2 = Snowpack((1,), xp); o, inf = s2.step(np.array([5.0]), np.array([10.0])); assert abs(o[0] - 5) < 1e-6
    # 4. two cold weeks freeze the ground; snow cover insulates it
    bare = spinup_frost([np.array([-8.0])] * 14, xp); covered = spinup_frost([np.array([-8.0])] * 14, xp, depth_cm=30)
    assert bare[0] >= CFGI_FROZEN > covered[0], (bare, covered)
    # 5. phase flag overrides temperature
    s3 = Snowpack((1,), xp); o, _ = s3.step(np.array([4.0]), np.array([3.0]), flag_snow=np.array([1.0])); assert s3.swe[0] > 3.5 and o[0] < 0.5, (s3.swe, o)     # stored as snow, only the hour's melt drains
    print('snow selftest ok: cold storm stored, rain-on-snow releases', round(tot_out, 1), 'mm from 10 mm rain, frost index bare',
          round(float(bare[0])), 'vs under 30 cm snow', round(float(covered[0])))


if __name__ == '__main__': selftest()
