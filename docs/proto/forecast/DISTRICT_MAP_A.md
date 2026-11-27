# Whole-District 3 forecast map, candidate (a) 2 of 8 ensemble members: result (scored once, 27 Nov 2026)

Pre-registration `DISTRICT_MAP_PREREG.md` (3db11469c, execution note for (a) d62bfc127). Code `proto/district_map_eval.py score --cand a`,
numbers `district_map_a.json`. 72 Turing member runs (9 storms x 8 HRRR cycles), compared with the radar references of (b) (`dm_<storm>_ref`).
All 144 jobs completed; one run (`dm_sep2021_a_m0112z`) finished but its publish push was lost, and its post stage was rerun once unchanged
(CPU only) to publish it. Scored only when all 72 were in.

## Verdict: **fail** (1 of 3 conditions)

| Condition | Bar | Result | |
|---|---|---|---|
| ratio_n (pooled, 7 out-of-sample storms) | 0.7–1.5 | 7.50 | **fail** |
| Site recall (29 sites, district-wide) | >= 0.276 | 0.207 (6 of 29) | **fail** |
| Lift | >= 2 | 18.2 (1.14 % of segments flagged) | pass |
| CSI vs radar run (ranking only) | — | 0.13 | |

## Per storm

| Storm | Role | Flagged (cand.) | Flagged (radar) | ratio_n | CSI | Sites hit |
|---|---|---|---|---|---|---|
| sep2023 | development (reported only) | 757 | 135 | 5.61 | 0.09 | 17 / 90 |
| aug2021 | development (reported only) | 548 | 166 | 3.30 | 0.17 | 5 / 14 |
| jul2021 | out-of-sample | 675 | 20 | 33.75 | 0.03 | 3 / 5 |
| sep2021 | out-of-sample | 1630 | 354 | 4.61 | 0.22 | 2 / 5 |
| sep2022 | out-of-sample | 47 | 19 | 2.47 | 0.22 | 0 / 4 |
| jul2023 | out-of-sample | 116 | 6 | 19.33 | 0.05 | 0 / 5 |
| aug2023 | out-of-sample | 206 | 8 | 25.75 | 0.04 | 1 / 4 |
| aug2023b | out-of-sample | 110 | 18 | 6.11 | 0.16 | 0 / 2 |
| aug2026 | out-of-sample | 801 | 53 | 15.11 | 0.06 | 0 / 4 |

## Reading (descriptive, not used to change anything)
- The 2-of-8 rule over the whole district over-forecasts on every storm (ratio 2.5 to 34 per storm, 7.5 pooled): the 8 HRRR
  cycles place the rain in different parts of the district, and any segment closed in 2 of them is flagged, so the false flags add up
  over the large domain. Inside a 20 km box this union is much smaller.
- Site recall (6 of 29) is higher than (b) (2 of 29) but still below the box forecast's 0.276.
- Both pre-registered candidates fail (`DISTRICT_MAP_VP.md`, this file). The boxes stay public (pre-registration: "If neither passes,
  the boxes stay"). Any further district-map variant is a new pre-registration.
