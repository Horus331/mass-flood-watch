# Hindcast: the road-closure model driven by the rain FORECAST

**Question:** if the system had been running on the morning of a known storm, with only the NOAA HRRR forecast available that morning, would it
have flagged the roads that actually flooded?

**Method.** We re-ran the same storm, the same 20 x 20 km box, the same 20 m LISFLOOD-FP set-up (`LF_LOSS=cn LF_CN_SCALE=0.91
LF_INFIL_MMH=2 LF_QOUT=1`, CPU on GitHub Actions) and the same `proto/prototype.py`, scored against the same labels. The only change is the
rain: `LF_RAIN=hrrr LF_HRRR_INIT=<cycle>` instead of MRMS radar. Each forecast run starts at the cycle's issue time and ends when the MRMS run
ends. The control is MRMS on the same CPU code, which separates the effect of the rain from solver differences with the published GPU
reference.

The scores are `proto/prototype.py` label recall, `proto/validate_points.py` report hits and `proto/score.py` gauges:

- **Label recall (strict):** the share of documented flood or closure sites (`proto/data/labels_<storm>_*.csv`) that have a segment within
  30 m at P(close) >= 0.5.
- **Flagged share:** the share of all road segments in the box at P >= 0.5.
- **Lift:** recall divided by the recall that random flagging of the same share would get.

Workflow: `.github/workflows/forecast_hindcast.yml` (`what=hindcast`). Per-run files: `docs/proto/forecast/hindcast/<case>/`. All numbers:
`hindcast.json`. Regenerate the tables with `python proto/forecast.py report --md docs/proto/forecast/HINDCAST.md`.

<!-- tables -->
### Sept 11, 2023, Leominster-Fitchburg (20 x 20 km box, 20 m)

| rain | box max / mean rain (mm) | peak hour (mm) | segments P >= 0.5 | flagged share | label recall (strict) | random recall | lift | loose recall | reports with >= 30 cm (LSR / StormEvents / labels) | random road points | gauge rise error (m) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| MRMS radar, GPU (published reference) | 207 / 107 | 89.3 | 134 | 2.6 % | 0.359 (78 sites) | 0.038 | 9.45 | 0.689 | 0.92 / 0.64 / 0.84 | 0.40 | 0.25 |
| MRMS radar, CPU (control: same code and solver as the HRRR runs) | 198 / 99 | 89.3 | 114 | 2.2 % | 0.359 (78 sites) | 0.032 | 11.09 | 0.667 | 0.85 / 0.64 / 0.79 | 0.33 | 0.17 |
| HRRR 12z (08:00 EDT, 9.2 h before the first report) | 97 / 22 | 56.0 | 4 | 0.1 % | 0.0 (78 sites) | 0.001 | 0.0 | 0.0 | 0.00 / 0.00 / 0.00 | 0.01 | 1.77 |
| HRRR 12z (08:00 EDT, 9.2 h before the first report), neighbourhood 20 km / 90th pct | 121 / 79 | 15.7 | 17 | 0.3 % | 0.077 (78 sites) | 0.005 | 15.8 | 0.2 | 0.00 / 0.36 / 0.23 | 0.08 | 0.94 |
| HRRR 18z (14:00 EDT, 3.2 h before the first report) | 105 / 50 | 32.0 | 13 | 0.3 % | 0.051 (78 sites) | 0.004 | 13.77 | 0.178 | 0.00 / 0.36 / 0.17 | 0.05 | 1.51 |
| HRRR 18z (14:00 EDT, 3.2 h before the first report), neighbourhood 20 km / 90th pct | 141 / 120 | 35.1 | 103 | 2.0 % | 0.269 (78 sites) | 0.029 | 9.19 | 0.533 | 0.85 / 0.46 / 0.65 | 0.33 | 0.21 |

### Aug 19, 2021, Worcester (Fred; 20 x 20 km box, 20 m)

| rain | box max / mean rain (mm) | peak hour (mm) | segments P >= 0.5 | flagged share | label recall (strict) | random recall | lift | loose recall | reports with >= 30 cm (LSR / StormEvents / labels) | random road points | gauge rise error (m) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| MRMS radar, GPU (published reference) | 121 / 68 | 89.6 | 187 | 2.2 % | 0.417 (12 sites) | 0.026 | 16.0 | 0.5 | 1.00 / 1.00 / 0.61 | 0.29 | 0.76 |
| MRMS radar, CPU (control: same code and solver as the HRRR runs) | 121 / 68 | 89.6 | 121 | 1.5 % | 0.333 (12 sites) | 0.017 | 19.77 | 0.417 | 1.00 / 0.00 / 0.54 | 0.22 | 0.37 |
| HRRR 06z (02:00 EDT, 9.6 h before the first report) | 7 / 4 | 6.1 | 5 | 0.1 % | 0.0 (12 sites) | 0.001 | 0.0 | 0.0 | 0.00 / 0.00 / 0.00 | 0.02 | 0.94 |
| HRRR 06z (02:00 EDT, 9.6 h before the first report), neighbourhood 20 km / 90th pct | 17 / 10 | 8.0 | 5 | 0.1 % | 0.0 (12 sites) | 0.001 | 0.0 | 0.0 | 0.00 / 0.00 / 0.00 | 0.02 | 0.94 |
| HRRR 12z (08:00 EDT, 3.6 h before the first report) | 65 / 39 | 39.3 | 51 | 0.6 % | 0.167 (12 sites) | 0.007 | 23.42 | 0.25 | 1.00 / 0.00 / 0.23 | 0.11 | 0.76 |
| HRRR 12z (08:00 EDT, 3.6 h before the first report), neighbourhood 20 km / 90th pct | 104 / 84 | 35.5 | 196 | 2.4 % | 0.583 (12 sites) | 0.027 | 21.38 | 0.667 | 1.00 / 1.00 / 0.54 | 0.31 | 0.34 |
| HRRR 12z (08:00 EDT, 3.6 h before the first report), neighbourhood 30 km / max | 246 / 198 | 48.6 | 752 | 9.0 % | 0.667 (12 sites) | 0.104 | 6.43 | 0.917 | 1.00 / 1.00 / 0.85 | 0.60 | 1.6 |
<!-- /tables -->

## What this shows

1. **The raw HRRR point forecast is not good enough to drive the road model.** On both storms the HRRR had the storm, but put the core in the
   wrong place or made it too weak over the box.
   - Sept 2023, 12z: the box mean was 22 mm against 99 to 107 mm observed. The forecast core of 116 mm in 6 h sat about 10 to 15 km west, over
     Westminster.
   - Aug 2021, 06z: 7 mm in the Worcester box.
   - Because curve-number losses and the 30 cm closure depth are both thresholds, a factor of 2 to 5 in rain becomes a factor of 10 to 30 in
     flagged roads. The raw-HRRR runs flag 0.1 to 0.6 % of segments and recover 0 to 17 % of the labelled sites.
2. **Spreading each hour's rain over a 20 km neighbourhood (90th percentile) recovers most of the skill when the cycle is within about 4 h of
   the storm.** This is the usual treatment of convection-allowing forecasts, and the same 20 km / 90th percentile used in
   `refresh/hrrr_replay.py`.
   - Sept 2023, 18z (14:00 EDT, about 3 h before the first report): recall 0.27 at 2.0 % flagged, lift 9.2. The MRMS control gets 0.36 at
     2.2 %, lift 11.1. Gauge rise error is 0.21 m (MRMS 0.17 m).
   - Aug 2021, 12z (08:00 EDT, about 4 h before): recall 0.58 at 2.4 % flagged, lift 21. The MRMS control gets 0.33 at 1.5 %, lift 20, so it
     is as good as the radar run here. A 30 km maximum spreads too much: 9 % of segments flagged, lift 6.4.
   - The neighbourhood does not fix forecasts that are wrong 9 to 10 h ahead: Sept 2023 12z gets 0.08, and Aug 2021 06z puts the rain
     somewhere else.
3. **What is live:** the forecast runs the flood model on `LF_HRRR_NBHD=20,90` rain. That is a reasonable-worst-case rain field for the
   next 48 h. The gate (`GATE.md`) and the box placement use the raw HRRR. Honest skill statement: **useful a few hours ahead of
   convective storms (lift ~9 to 21, comparable to the radar-driven model), not yet at 9 to 12 h lead.** The forecast refreshes every 6 h, so a
   storm is re-forecast by each new cycle as it approaches.
4. **The gate works where it matters.** Run on the Sept 11, 2023 12z cycle, the live gate fires with 116 mm in 6 h at Westminster and puts its
   first two boxes over Westminster / Fitchburg / Leominster. The end-to-end triggered run (gate, four 20 m boxes in parallel, viewer packs)
   took 34 min on GitHub Actions: 21 to 31 min per 54 h box, about 11 min of it LISFLOOD-FP. Dry forecast boxes take 7 to 14 min.

## Not done / next

- More storms. The catalogue has 9 storms with MRMS on AWS and HRRRv4 48 h cycles; at least Jul 2021, Sep 2021 and Aug 2026 should be added
  before the lift numbers are quoted as general.
- Probabilistic closures: time-lagged HRRR members (the last 3 to 4 cycles) or neighbourhood shifts, giving P(close) from the spread of runs
  instead of one reasonable-worst-case run.
- Days 3 to 7: the gate only sees the 48 h HRRR. An NBM / GFS outlook was not added because nothing cheap and validated was at hand.
