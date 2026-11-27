# Whole-District 3 forecast map, candidate (b) volume-preserving HRRR: result (scored once, 27 Nov 2026)

Pre-registration `DISTRICT_MAP_PREREG.md` (3db11469c, execution note 20e673c72). Code `proto/district_map_eval.py score --cand vp`,
numbers `district_map_vp.json`. 18 Turing runs (9 storms x candidate + radar reference), all published to `docs/proto/turing/dm_*`.
One solve (sep2022 candidate) failed on a transient Turing disk-write error (BlockingIOError) and was rerun once unchanged.

## Verdict: **fail** (2 of 3 conditions)

| Condition | Bar | Result | |
|---|---|---|---|
| ratio_n (pooled, 7 out-of-sample storms) | 0.7–1.5 | 1.24 | pass |
| Site recall (29 sites, district-wide) | >= 0.276 | 0.069 (2 of 29) | **fail** |
| Lift | >= 2 | 36.6 (0.19 % of segments flagged) | pass |
| CSI vs radar run (ranking only) | — | 0.43 | |

## Per storm

| Storm | Role | Flagged (cand.) | Flagged (radar) | ratio_n | CSI | Sites hit |
|---|---|---|---|---|---|---|
| jul2021 | out-of-sample | 6 | 20 | 0.30 | 0.18 | 0 / 5 |
| sep2021 | out-of-sample | 529 | 354 | 1.49 | 0.47 | 2 / 5 |
| sep2022 | out-of-sample | 21 | 19 | 1.11 | 0.43 | 0 / 4 |
| jul2023 | out-of-sample | 6 | 6 | 1.00 | 1.00 | 0 / 5 |
| aug2023 | out-of-sample | 6 | 8 | 0.75 | 0.17 | 0 / 4 |
| aug2023b | out-of-sample | 20 | 18 | 1.11 | 0.81 | 0 / 2 |
| aug2026 | out-of-sample | 7 | 53 | 0.13 | 0.02 | 0 / 4 |
| sep2023 | development (reported only) | 9 | 135 | 0.07 | 0.04 | 0 / 90 |
| aug2021 | development (reported only) | 12 | 166 | 0.07 | 0.06 | 1 / 14 |

## Reading (descriptive, not used to change anything)
- The volume rescaling removes the ~3x over-forecast: pooled, the district map now flags about as many segments as the radar run.
  The pooled ratio is carried by sep2021 (529 of 601 flagged); on 3 of 7 storms the candidate flags far less than the radar run.
- Site recall fails by a wide margin. Diagnostic after scoring: the **radar reference itself** catches only 3 of the 29 sites at
  P >= 0.5 district-wide (0.10). So a single district run with the right rain volume cannot reach the box forecast's 0.276: the box
  result rests on the 2-of-8 ensemble, whose extra members (and the 20,90 surplus) add the flags that catch sites.
- The boxes stay public (pre-registration: "If neither passes, the boxes stay"). Next by the pre-registration: candidate (a),
  the whole district for each of the 8 ensemble members, 2 of 8.
