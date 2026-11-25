# Observed-rain trigger: result (25 Nov 2026) — fails, not adopted

Pre-registration: `OBS_TRIGGER_PREREG.md` (frozen in e9247212d before any number was computed). Code `proto/obs_trigger.py`, workflow
`obs_trigger.yml`; raw output `obs_trigger.json` and `obs_trigger/` (per-storm and per-month files).

| Measure | Result | Pass rule | |
|---|---|---|---|
| M1 timing: R fires ≥ 30 min before the first flood report | 11 of 13 storms; median lead 138 min | ≥ 10 of 13 | pass |
| M2 placement: reports inside the boxes (106 reports, 13 storms) | R boxes 24 (22.6 %), HRRR boxes 8 (7.5 %) | R ≥ HRRR + 10 points | pass |
| M3 false triggers, Jun–Sep 2023 (5,864 half-hour steps, 3 missing) | R fires on 40 days, 21 of them with no District 3 report | ≤ 14 | **fail** |

**Verdict: fail (M3).** Nothing in the live forecast changes.

Notes (descriptive, not part of the pass rule):
- Missed in time: jul2021 (R never fired: radar 1 h stayed below 25 mm and QPE/FFG below 1.0 in 4 cells) and sep2021 (fired 5 min after
  the first report).
- Radar 1 h ≥ 25 mm made R fire first in 11 of the 12 storms where it fired; QPE/FFG ≥ 1.0 alone only in sep2021 (both at once in jul2023d).
- Placement is low for both: storm-day reports are spread across the district, and at the moment R first fires (median 2.3 h before
  the first report) the heaviest observed rain is often not yet where the reports come from. The HRRR boxes compared are those of the
  latest cycle before the first report.
- 11 of the 21 false-trigger days are in June 2023; heavy radar rain in a few cells is common on days when no road floods is reported.

Execution fixes made after the first run, before the final numbers (rule and thresholds unchanged): the HRRR gate step for the 4 storms
missing from `gate_calibration.json` needed matplotlib (9a341a244); the R boxes read the hourly 3 h radar total, which a 10-minute
search window had missed (e02109ef7). Only the storm part was rerun; the summer scans (M3) were not affected.
