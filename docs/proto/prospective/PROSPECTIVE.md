# Forward test (pre-registered, written 29 Oct 2026)

Every hindcast in this project was scored after the event. A forward test removes that doubt: each forecast is committed to the public
repository **before** the storm, and scored automatically afterwards against reports the model never saw. This file fixes the rules before
the first storm in the window, so they cannot be tuned to the results. Results: `RESULTS.md` (rebuilt after every storm follow-up).

## Window and model

- **Start:** 3 Nov 2026 00:00 UTC (`PROSPECTIVE_START`). **Main reading:** 31 Oct 2027. **Interim reading:** after 5 storms with reports.
- **Model:** the live forecast as it runs on the start date: HRRR 48 h, gate 25 mm / 6 h or 40 mm / 24 h, 2-of-8 time-lagged ensemble,
  neighbourhood 20 km / 90th percentile, LISFLOOD-FP 8.2 20 m CPU, `LF_PARITY=1`, CN × 0.88, AMC II, infiltration 2 mm/h
  (`.github/workflows/forecast.yml`, `docs/proto/forecast/GATE.md`, `ENSEMBLE.md`, `DISTRICT.md`).
- **Changes during the window** are allowed only if they are pre-registered in their own file first. Each ledger row records the commit and
  settings that produced it, so every storm is scored with the model that actually issued it. Results are reported per model version
  when a change happens.

## What is recorded

| record | where | written by |
| --- | --- | --- |
| every live cycle, quiet ones too (gate, district rain maxima, state, likely / possible counts, alerts, reports, commit, settings, SHA-256 of the status) | `ledger.csv` | `forecast.yml` (same commit as the forecast) |
| the forecast of every cycle that touches a storm (k-of-n table) | `docs/proto/archive/<storm>/forecast/` | `forecast.yml` |
| labels, radar-driven run, verification | `docs/proto/archive/<storm>/`, `proto/data/labels_<id>_auto.csv` | `archive_followup.yml` |
| USGS stream-camera stills of the storm window | `docs/proto/archive/<storm>/cameras/` (index), HF dataset `cameras/<id>/` (images) | `archive_followup.yml` |

A storm is archived when **any** of three things happens: the gate fires, the NWS issues a Flash Flood Warning / Flood Advisory touching
District 3, or a **flood report** appears in District 3 (an NWS Local Storm Report of flooding, or a MassDOT roadway event about water on the
road). The third trigger is new: it makes storms the system did not see coming enter the record, so misses are counted.

## Scoring (fixed)

Labels: automatic, medium or high quality only (LSR, NOAA Storm Events, MassDOT log). SeeClickFix (low) is excluded from the scores.
"First report" = the earliest such label. A forecast counts only if it was issued at least 1 h before the first report.

Per storm, one class:

| class | rule |
| --- | --- |
| **hit** | the gate fired before the first report and the likely-closed set hits at least one report site (score_v2: 30 m, sites clustered at 150 m) |
| **right storm, wrong roads** | the gate fired before the first report, no site hit |
| **missed** | reports exist, the gate did not fire before the first report |
| **false alarm** | the gate fired, no report |
| no flooding reported | archived by an NWS alert only, no report (not scored) |

Pooled measures:

1. **Storm detection:** hits + wrong roads over storms with reports (primary).
2. **Site recall:** report sites caught by the forecast over all report sites, with the radar-driven run of the same boxes as the ceiling.
3. **Lead time:** first gate fire to first report, median and range.
4. **False alarms:** false-alarm storms; and the share of live cycles with the gate fired that belong to no storm with reports.
5. Segment agreement with the radar-driven run (POD, FAR, CSI, 1 km neighbourhood) as already in `docs/proto/archive/ARCHIVE.md`.

Reference points from the hindcasts, for reading the result (not pass/fail lines): the 2-of-8 ensemble on the 7 out-of-sample storms
(`docs/proto/forecast/ENSEMBLE.md`) and the radar-driven site recall on the held-out storms (`docs/proto/scoring/BASELINE_v2*.md`).

## Known limits

- Automatic labels are unreviewed and miss most flooded roads (about 1 in 6 flooded segment-storms is reported; `docs/proto/latent/LATENT.md`).
  Recall is therefore measured against reported sites only.
- NOAA Storm Events arrive 2–4 months late. The follow-up re-scores when they land, so results for recent storms can still change.
- The district-wide map is not a warning yet (`docs/proto/forecast/DISTRICT.md`); scores are per forecast box.
