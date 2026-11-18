# DRAFT: pre-registration for groundwater proposal A (not approved, not run)

**Status: DRAFT, waiting for Mo's choice between proposals A / B / C (`SCOUT.md` §4).** Nothing below has been run. If Mo picks A, this
file is frozen (renamed `PREREG_A.md`, committed) before any code runs on the labels. Written 18 Nov 2026.

## Question
Is a shallow seasonal water table associated with Sept 2023 road damage in Leominster **after holding the terrain constant**? §6 of
`SCOUT.md` found damage on shallow water tables at 81 % vs 43 % for all Leominster segments, but shallow water tables mark low ground,
where surface water also collects. This test asks whether the association survives when damaged and undamaged segments sit at the same
height above drainage and the same slope.

This is a descriptive, in-sample association test on one storm and one town. A pass is a reason to collect subgrade or pavement data
(the mechanism); it does not put groundwater into the model.

## Data (all already in the repo)
- Factor: `shallow` = segment's shallowest seasonal high water table ≤ 50 cm (`roads_wtd.json`, SSURGO via `soils30` `wtd`). Fixed
  before the test; no other cut-off will be reported as the result.
- Outcome: `damaged` = segment matched to at least one Leominster DPW damage point (54 points, same 30 m matching as `SCOUT.md` §6).
  **Unit = segment, not point**, so the 32 Wachusett St points count as 4 segments.
- Terrain covariates, per segment, from the existing feature rows (`proto/closure_ml.py`): `hand_m` (height above the nearest stream or
  water cell, minimum along the segment, capped at 20 m) and `slope_pct`.
- Population: all Leominster segments inside the model box with a water-table value (no-data segments dropped; their count reported).

## Method (fixed)
1. **Strata.** HAND bins 0–1, 1–2, 2–5, 5–10, ≥ 10 m × slope bins < 2 %, 2–5 %, ≥ 5 % (15 strata). Strata with no damaged segment
   drop out; their count is reported.
2. **Main statistic.** Mantel–Haenszel common odds ratio of `damaged` on `shallow` across strata, with its 95 % interval
   (Robins–Breslow–Greenland variance), and the Cochran–Mantel–Haenszel test.
3. **Sensitivity (reported, not used for the verdict):**
   - (a) Leave out the Wachusett St segments.
   - (b) Water-table cut-off 25 cm instead of 50 cm.
   - (c) Logistic regression `damaged ~ shallow + hand_m + slope_pct`.
   - (d) Also hold road class constant (local vs other).
   - (e) Damage types: washout only (50 of 54 points).
4. **Negative control.** Repeat step 2 with the model's own Sept 2023 closures (T2 run, p ≥ 0.5) as the outcome. Closures are surface
   water only, so if `shallow` is just low ground, it should also show up here. Reported next to the main result.

## Reading rules (fixed before any run)
- **Pass (worth pursuing):** MH odds ratio ≥ 2, the 95 % interval excludes 1, **and** sensitivity (a), without Wachusett St, still has
  an odds ratio > 1.
- **Inconclusive:** odds ratio ≥ 2 but the interval includes 1, or (a) falls to ≤ 1. Likely with 23 damaged segments; the report
  then states the smallest effect the data could have detected.
- **Fail:** MH odds ratio < 2. Then §6's association is read as low ground, and proposal A goes ahead only with new data (pavement or
  subgrade observations, or damage lists from other storms).
- **Negative control:** if closures show an equal or larger odds ratio than damage, the result is reported as "not separable from
  surface flooding", whatever the verdict above.
- No changes after the first run: no new strata, cut-offs or outcome definitions. If the code fails 3 times, stop and ask Mo.

## Output (if run)
`docs/proto/groundwater/PREREG_A_RESULT.md` and `prereg_a.json` (counts per stratum, MH odds ratio and interval, sensitivities, negative
control). Script `proto/gw_prereg_a.py`. Runs on a free GitHub runner or locally; no Turing, nothing paid.

## Limits stated up front
One storm, one town, 23 damaged segments; SSURGO describes natural soils, not road fill or drained ground; the water table is seasonal,
not measured on 11 Sept 2023 (no well in Leominster); matching within 30 m can attach a point to the wrong segment at junctions.
