# Observed-rain trigger: pre-registration (frozen 24 Nov 2026, before any number below is computed)

Mo agreed on 24 Nov 2026 to test whether the NOAA flash-flood signal (MRMS FLASH) and the radar rain could start the flood model as an
extra trigger, next to the HRRR rain gate (`GATE.md`). The radar nowcast blend for the first hours is **not** part of this test: it was
pre-registered, passed and adopted on 9 Nov 2026 (`NOWCAST_WINDOWS.md`, `LF_NOWCAST=1`).

## Why

The HRRR gate fires for 35 of 38 pre-storm cycles (`GATE.md`), but it reads only the forecast. Two weaknesses are documented there:
(1) a storm the HRRR misses (Jul 14 2023, latest cycle 22 mm in 6 h) is caught only by older cycles; (2) the boxes are placed on the
forecast rain, and HRRR convective rain is often displaced by tens of km (Aug 2021: 40 mm in District 3 but 7 mm in the Worcester box).
An observation-based trigger fires on rain that is already falling, so it cannot be displaced, but it gives less lead time.

## Trigger R (fixed now, values from the literature and the existing alert levels, not tuned)

Evaluated every 30 min from the MRMS archive on AWS (from 14 Oct 2020), District 3 box as in `proto/live_feeds.py` (`LAT`, `LON`):

- **R fires** when, inside District 3, either
  - MRMS FLASH `QPE_FFGMAX` (max ratio of observed rain to flash-flood guidance over 1/3/6 h) is ≥ 1.0 in at least 4 cells (~1 km each;
    1.0 = rain has reached the guidance, NWS FLASH usage; 4 cells so that one noisy pixel does not fire it), or
  - MRMS RadarOnly 1 h rain is ≥ 25 mm in at least 4 cells (the Sentinel ACTIVE level, `docs/proto/live/SENTINEL.md`).
- **Boxes for R:** up to four 20 × 20 km boxes placed one at a time on the highest observed 3 h rain (RadarOnly QPE 3 h), with the same
  placement rule as the HRRR gate (`GATE.md`, centred on the maximum, next box on the maximum outside the earlier boxes).

## Storms

All non-locked catalogue storms (`docs/proto/obs/catalog.json`) after 14 Oct 2020: jul2021, jul2021b, aug2021, sep2021, sep2022,
jul2023, jul2023b, jul2023c, jul2023d, aug2023, aug2023b, sep2023, aug2026 (13 storms). The 5 locked storms are not opened.
Background for false triggers: 1 Jun – 30 Sep 2023, the same summer as `gate_background_2023-06-01.json`.

## Measures

- **M1 timing:** for each storm, the first time R fires, compared with the first flood report (`first_report_utc`,
  `gate_calibration.json`). Fires "in time" if at least 30 min before the first report.
- **M2 placement:** flood reports of the storm (`docs/prone/flood_reports.json`, District 3, the storm's local date and the next day)
  that fall inside the R boxes at the time R first fires, versus inside the boxes of the latest HRRR cycle published before the first
  report (`gate_calibration.json`, `boxes`). Pooled over storms; also per storm.
- **M3 false triggers:** days in the background summer on which R fires with no District 3 report that day or the next, compared with
  the HRRR gate's 14 such days in the same summer (`GATE.md`).

## Pass rule (all three)

1. R fires in time (M1) for at least 10 of the 13 storms.
2. Pooled M2: the R boxes contain at least 10 percentage points more of the reports than the HRRR boxes.
3. M3: no more than 14 false-trigger days.

**If it passes:** R becomes an extra trigger. When R fires and the HRRR gate's boxes do not already cover R's boxes, the flood model
runs on R's boxes with the radar rain so far, the nowcast blend for the next 2 h and the HRRR after that (the adopted `LF_NOWCAST`
member). Nothing else in the live forecast changes. **If it fails:** nothing changes; the result is recorded in `PROJECT_LOG.md` §6.
**Either way:** no threshold above is changed after seeing the numbers; a changed rule would be a new pre-registration.

Code (to be written after this file is committed): `proto/obs_trigger.py`; result: `OBS_TRIGGER.md`, `obs_trigger.json`.
