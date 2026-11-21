# Antecedent water table before each storm vs the model's gauge bias (21 Nov 2026; descriptive only)

`proto/gw_antecedent.py` (GitHub run 44857879613) → `antecedent.json`. For each of the 25 non-locked District 3 catalogue storms: the
mean depth to water over the 3 days before the storm at every USGS well with a daily record (11–17 wells per storm), expressed as a
**wetness percentile**: the share of that well's own record for the same calendar month (other years) that was deeper. 90 = wetter than
90 % of that month's history. Per storm: median over wells within 30 km of the storm box (2–9 wells). Nothing enters the model; the
soil-wetness model test (T4 C) stays stopped.

**Results.**
- Most catalogue storms fell on wet ground: median wetness percentile 80; 11 of 25 storms above 90 (all four July 2023 storms, Aug 2023,
  Sep 2021, Sep 2018b, Jul 2021b). Dry exceptions: Aug 2020b (10), Jun 2020b (12), Jun 2020 (24).
- **No clear relationship with the model's errors** (rank correlations, n = 24–25): with the modelled/observed river-rise ratio −0.04;
  with the signed rise error −0.35 (wetter ground, slightly larger under-prediction, weak); with top-3 % site recall −0.01; nearest-3-wells
  version vs ratio +0.05.

**Reading.** Pre-storm water-table wetness does not explain which storms the model under-predicts or misses; the storm-size effect
(`parity/BIAS_BY_STORM.md`, rank correlation 0.41 with storm total) is much stronger. The weak negative link with the signed error is
consistent with the model's fixed, drier-than-average soil setting (curve-number scale 0.88) missing some runoff on wet ground, but it is
not strong enough to act on, and testing a wetness adjustment is proposal B / T4 C, which Mo has not asked for. For Paper 2 this
supports treating groundwater as a slow, subgrade link (A) rather than a same-storm runoff driver.
