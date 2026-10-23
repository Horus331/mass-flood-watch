# Forecast gate: when the flood model runs

Every 6 hours `.github/workflows/forecast.yml` reads the newest 00/06/12/18z NOAA HRRR run (48 h of hourly rain, 3 km grid). It works out the
largest **6 h** and **24 h** running rain total at every HRRR point inside the 73 District 3 towns. A town's value is the maximum over the points
inside it; a town smaller than one cell takes its nearest point. The LISFLOOD-FP flood model runs only when at least one town reaches

| | threshold |
| --- | --- |
| 6 h maximum | **25 mm** |
| 24 h maximum | **40 mm** |

Below both thresholds the forecast is published as quiet: "No road closures expected in District 3 in the next 48 h", with the rain summary.
When the gate fires, up to four 20 x 20 km boxes are placed, one at a time, on the heaviest forecast rain. Each box is centred on the highest
remaining exceedance score, max(6 h / 25 mm, 24 h / 40 mm), and its points plus a 5 km margin are then taken out before the next box is placed.
Each box runs at 20 m, the prototype set-up validated on Sept 2023 Leominster, as a parallel GitHub Actions job.

**Ensemble (live default).** When the gate fires, the flood model runs for the 8 time-lagged HRRR members:

- the cycles at T, T-6, T-12 and T-18 h;
- the hourly cycles at T-1 to T-4 h.

Every member runs on every box. The boxes are this cycle's, plus those the older members' own gates place on their rain after T,
deduplicated and capped at 4. A road is **likely closed when 2 or more of the 8 runs close it**, and possible at 1 of 8. That rule was
validated out of sample on 7 storms (`ENSEMBLE.md`). A quiet gate still costs one job. `FORECAST_ENSEMBLE=0` falls back to the single
cycle.
The thresholds can be changed with the env variables `GATE_6H_MM` and `GATE_24H_MM`.

## Why 25 mm / 6 h and 40 mm / 24 h

Numbers: `gate_calibration.json` (`python proto/forecast.py calib`) and `gate_background_2023-06-01.json` (`... background`).

1. **Every closure storm in the catalogue was caught by the cycles before it.** The catalogue is `docs/proto/obs/catalog.json`: 15 District 3
   storms with documented road flooding. For each storm we took the three latest 00/06/12/18z cycles that were already published (issue + 3 h)
   before the first flood report. At 25 / 40 mm, **35 of 38** of those cycles fire the gate.
   - Every storm since HRRRv3 (2018) has at least one cycle that fires. The latest cycle fires for 12 of 14 storms. One miss is Jul 14, 2023
     (12z: 22 mm in 6 h); its 06z and 00z cycles had 66 and 62 mm. The other is Aug 2015, from HRRRv1 with forecast hours missing.
   - At 30 / 40 mm the latest cycle would miss 4 of 14 storms; at 40 / 60 mm it would miss 6.
2. **The HRRR underestimates the local peak, so the gate has to sit well below what floods roads.** Inside the storm boxes, observed MRMS 6 h
   maxima were 32 to 196 mm (lowest: Jul 2023, 32 mm). The HRRR box maxima from the same mornings were often half of that or less. Examples:
   Aug 2021, 12z: 62 vs 121 mm; Jul 2023, 12z: 20 vs 32 mm. 25 mm is about half of the NOAA Atlas 14 1-year 6 h depth for central MA (~50 mm).
3. **The cost of firing is small.** A false trigger costs about 30 to 60 minutes of free Actions CPU per box. A missed storm costs the whole
   forecast. Over summer 2023 (122 days, 12z cycles), the gate would have fired on 33 days (27 %). That summer was record-wet in central MA.
   Those 33 days include 19 of the 29 days that had a District 3 storm or MassDOT flood report (not counting crash records), and 14 days with no
   report. A 20 mm gate fires on 39 days and catches 20 report days; 30 / 40 mm fires on 29 days and catches 18.

## Caveats

- The gate looks only at the HRRR. HRRR convective rain is often displaced by tens of km. Before the Aug 2021 storm, the 06z cycle put 40 mm in
  District 3 but only 7 mm in the Worcester box. The box placement follows the forecast, so a displaced forecast puts the boxes in the wrong place.
  The Turing job (`proto/turing/run_forecast.slurm`) runs all of District 3 at 20 m and has no placement problem.
- Lead time is short. The 48 h cycles appear about 1 h 45 min after issue. A storm whose rain starts within about 3 h of a cycle is in practice
  forecast by the previous cycle, 6 to 9 h ahead.
