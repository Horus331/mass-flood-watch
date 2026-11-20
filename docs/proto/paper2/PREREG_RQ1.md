# Pre-registration: Paper 2 RQ1, road-edge stream-power index vs Leominster damage (frozen 20 Nov 2026)

Mo approved the Paper 2 direction on 20 Nov 2026 (07:23 ET). Frozen while the index run (GitHub 44734954765) is still computing and
before any index value has been seen or compared with damage. Index definition: `RQ1_INDEX_SPEC.md` (unchanged).

**Question.** Does the road-edge stream-power index (SPI) separate segments damaged in the Sept 2023 Leominster storm from undamaged ones,
beyond what modelled depth and traffic already do? In-sample (Sept 2023 is the calibration storm), so the result is descriptive; it
decides whether the index is worth an out-of-sample test with a second damage inventory.

**Data.** Leominster segments of the Sept 2023 T2 run with an index value (`edge_spi_leominster.json`); outcome = ≥ 1 DPW damage point
within 30 m (same matching as `groundwater/gw_prereg_a.py`, unit = segment). Comparators from the same run's features: `peak_depth_m`,
`aadt`.

**Statistics (fixed).**
1. AUC of `spi_max` for damaged vs undamaged segments, with a 95 % interval (DeLong, or 2,000 bootstrap draws over segments if DeLong is
   unavailable).
2. Incremental value: logistic regression `damaged ~ log(depth + 0.02) + log1p(aadt)` vs the same plus `log1p(spi_max)`; likelihood-ratio
   test, and the in-sample AUC of each.
3. Washout-only outcome (washout points only) for 1 and 2.
4. Sensitivity (reported, not used for the verdict): without Wachusett St; `spi_p90` instead of `spi_max`; `edge_len_over_p95_m`.
5. The 26 edge-washout misses of `phase1/LEOMINSTER_MISSES.md`: share of them in the top 10 % of segments by `spi_max`, vs 10 % by chance.

**Reading rules (fixed).**
- **Promising:** AUC of `spi_max` ≥ 0.70 with the interval above 0.5, **and** the likelihood-ratio test p < 0.05 for adding SPI to depth +
  traffic, **and** the top-10 % share of the edge-washout misses ≥ 2 × chance.
- **Weak:** AUC above 0.5 (interval excludes 0.5) but one of the other two conditions fails.
- **No signal:** the AUC interval includes 0.5.
- Whatever the result, nothing enters the live model; a promising result leads to an out-of-sample test when a second damage inventory
  exists. No change to the index or these rules after the first run; if the code fails 3 times, stop and ask Mo.
