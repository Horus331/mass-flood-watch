# Light storms: no constant infiltration on top of the curve number (B0 retest, pre-registered 1 Nov 2026, PROTOCOL v2)

Fixed and committed **before any run below was started or scored**. No held-out-23 number for this setting at the parity configuration
has been looked at (the v1 test in `AMC.md` used the old × 0.91 set-up on OOS-7 only).

## 1. Why this one idea

The deployed rule catches 1 of 58 sites on the 16 newer storms, most of them light (20–50 mm). Already tested and not adopted: storm drains,
sub-hourly rain, connected-pavement runoff (DCIA), gauge-adjusted rain. One cheap idea is tested here, chosen before looking at any score:

The model removes rain twice. The NRCS curve number (TR-55) is already an event infiltration model (initial abstraction plus a loss that grows
with the storm). The deployed set-up then also subtracts a constant 2 mm/h from every hour's rain excess (`LF_INFIL_MMH=2`, applied to the
excess in parity mode). In a 20–40 mm storm the excess is a few mm per hour, so the second loss removes a large share of it (jul2023:
28 % of the excess), much more than in the big storms the set-up was calibrated on. `AMC.md` (v1, OOS-7, CN × 0.91) already found B0 the
best gauge variant (all-gauge rise MAE −11 %, bias −0.42 → −0.27 m), with +1 OOS-7 site, and recommended this retest under v2 on the
held-out 23. It has no free parameter.

## 2. Candidate

**B0 `LF_INFIL_MMH=0`** on top of the deployed set-up (`LF_PARITY=1 LF_CN_SCALE=0.88`, `LF_LOSS=cn`, AMC II, `LF_QOUT=1`, `LF_VOUT=1`, 20 m, CPU).
The CN scale is not re-fitted (that would be a second, label-free calibration and a different candidate).

## 3. Runs

`parity_test.yml` on branch `terrain-fix`, the 25 non-locked catalogue storms, `docs/proto/runoff/b0v2/runs/b0/`. Baseline: the in-run
baseline of `terrain/PREREG.md` (`docs/proto/terrain/runs/base/`, same commit, same solver).

## 4. Decision (PROTOCOL v2 §5a, k = 1)

`python proto/score_v2.py --compare docs/proto/terrain/score_base.json docs/proto/runoff/b0v2/score_b0.json --protocol v2 --k 1`: adopted only if
all five §5a conditions hold on the held-out 23. The alert tier is not re-thresholded.

**Reported whatever the verdict:** the light-storm sub-pool (NEW16) rule-tier recall and share against the baseline's 1 / 58 (the target of
this idea; reported, not a decision condition), per-storm 3 % and rule recall, dev storms separately, flagged-segment counts, and USGS gauge
rise MAE / bias from each run's `score.json`. Results go to `docs/proto/runoff/B0_V2.md`.
