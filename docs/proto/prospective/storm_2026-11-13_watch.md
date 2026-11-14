# Storm watch: 12–14 Nov 2026 (cold, windswept rain; snow possible on the hills)

Second storm of the forward test. Written 12 Nov 2026 ~19:30Z, when the rain had just begun (19Z hour: District 3 box mean 0.4 mm,
max 3.9 mm), **before any report or radar replay of this storm was looked at.** Everything below the "Plan" heading is fixed now.

NWS Boston: "A widespread cold rain is expected late today through Friday"; snow mixing in on the higher terrain Friday and Friday night
("a coating to 2 inches are possible across the higher elevations"). No Flood Watch for Massachusetts at writing. Our 12Z forecast:
"No road closures expected in District 3 in the next 48 h".

## Record (automatic)

`proto/storm_watch.py` (workflow `storm_watch.yml`, hourly via the keeper) appends to `storm_2026-11-13/record.jsonl`, per hour:
observed MRMS rain (box mean / max / wet share), MRMS precipitation type (share flagged snow / hail), HRRR's forecast of the same hour at
leads 1–6 h, the published forecast (headline, likely / possible, top roads with k of 8) with a snapshot of every new cycle's road list in
`storm_2026-11-13/forecasts/`, sentinel state, NWS alerts and MassDOT water-related events. Labels follow from the archive follow-up
(IEM storm reports, NOAA Storm Events when published, MassDOT events, SeeClickFix).

## Plan (fixed before the storm)

### 1. Error budget: why the forecast was right or wrong
For every forecast cycle issued 12 Nov 12Z – 14 Nov 00Z:
- **Rain error:** forecast vs MRMS (gauge-corrected Pass2 once out) over the District 3 box and each forecast box: total, peak hour, timing
  of the peak, by lead time.
- **Physics error:** a radar-driven replay of the same boxes (frozen live settings) against the reports. If the replay with observed
  rain is right where the forecast was wrong, the error is the rain; if the replay is also wrong, the error is the model.
- **Each missed or false road** gets one class: rain (amount / placement / timing), phase (snow counted as rain), terrain, drainage
  (storm drains, inlets), culvert / crossing, edge erosion, label.

### 2. Physics candidates, defined now, tested after the storm
Each is tested on this storm's replay **and** on the held-out set with the PROTOCOL v2 adoption rule (§5a ranking route, or §A artifact
fix where it removes a stated artefact). None is adopted on this storm alone.

- **C1 Precipitation phase.** The model treats all precipitation as rain. Candidate: liquid fraction from the 2 m air temperature of the
  same hour (HRRR analysis for observed hours, the member's own forecast for forecast hours): 1 above 2 °C, 0 below 0 °C, linear between
  (a common rain–snow partition, e.g. US Army Corps snowmelt practice); the frozen part is held as snow and not melted within the run.
  Check on this storm: replay with vs without C1, closures and depth; on the held-out set C1 changes nothing in warm storms (must hold).
- **C2 Storm-drain sink on curbed urban roads.** The first storm's forecast put Worcester streets that sit in closed depressions (East Park
  Terrace) in the likely list; storm drains carry that water away and are not modelled. Candidate: a sink of 25 mm/h on road cells in
  areas ≥ 50 % impervious (NLCD), i.e. inlets sized for about a 2–10-year design intensity in central Massachusetts (NOAA Atlas 14,
  Worcester 1 h: 2-yr ≈ 30 mm, 10-yr ≈ 45 mm). Tested with the §5a ranking route on the held-out 23.
- **C3 Edge-erosion flag (output, not depth).** From the Leominster deep dive (`phase1/LEOMINSTER_MISSES.md`): roads fail by erosion at
  the edge with little standing water. Candidate: flag a segment when the modelled unit discharge along it (depth × speed) exceeds
  0.1 m²/s for at least 15 min. Tested on Leominster DPW edge washouts (development) and reported for this storm; adopted only as a
  separate "edge erosion risk" column, never mixed into closures.

### 3. What is reported, whatever happens
A results file `storm_2026-11-13_results.md` within 48 h of the end of the rain: the error budget, the per-road classes, and each
candidate's test with its adoption decision. If nothing floods, that is a result too: the false-alarm side of the forward test.

## Running log

- **12 Nov 19Z.** First hour recorded: District 3 box mean 0.4 mm, max 3.9 mm; HRRR 1 h earlier said 0.1 mm. No snow flagged, no
  MassDOT water events. Sentinel QUIET. Forecast 12Z: no closures in 48 h.
- **12 Nov ~19:30Z, C1 smoke test** (parity_test run 43289609204, hills box 155000,910000–165000,920000, HRRR 18Z cycle, 18 h, live
  settings): with LF_PHASE=1, 5.2 % of the forecast precipitation is frozen (max 1.3 mm water as snow; lowest 2 m temperature 0.7 °C);
  without it, all counted as rain. HRRR 18Z total for this box: max 6 mm, mean 5 mm over 18 h, a light event for the model. Both runs
  stopped after the solver at a post-processing step that needs a storm gauge file (`gauges_forecast.json`) the parity workflow does not
  have for STORM=forecast; the C1 code itself ran cleanly.
- **12 Nov 19–23Z (hours 20–21Z backfilled).** Light rain so far: District 3 box mean 0.36, 0.19, 0.17, 0.05, 0.08 mm per hour (max
  5.9 mm). HRRR 1 h earlier said 0.14, 0.06, 0.03, 0.01, 0.01: about 3–5 × too little in these light hours (all leads 1–6 h similar). No
  snow flagged, no MassDOT water events, sentinel QUIET, forecast "no closures". The recorder now backfills hours GitHub's schedule skips.
- **13 Nov 00Z.** Hour mean 0.10 mm (max 3.4), HRRR 1 h earlier 0.02: the light-rain low bias holds (6 hours, observed / HRRR-1h
  ≈ 2.6–6 ×). Still no snow, no MassDOT water events. **Pipeline finding:** the 18Z forecast cycle (run 43311579673, started 21:34Z) is
  still running at 00:30Z: per member the flood solve takes 55–95 min and the road-closure step 45–75 min (5-min frames), so a cycle is
  published about 7 h after the HRRR cycle time. In a fast storm that is too late; candidate fix (pipeline, not physics): compute the
  closure statistics from 15-min frames while keeping 5-min frames for the map, checked on the golden storm before use.
- **13 Nov ~01:30Z, C3 on its development set (Leominster DPW, 9 segments with edge washouts):** as defined (peak unit discharge
  ≥ 0.1 m²/s) it flags 2.8 % of Leominster's segments and **0 of the 9** edge-washout segments (≥ 0.05: 1 of 9). C3 as written is dropped
  before any test. What does separate the edge-washout segments from the other 1,512 (ROC-AUC, exploratory, 9 positives): segment length
  0.93 (exposure: more road edge), peak speed 0.88, freeboard 0.83, peak depth 0.81, AADT 0.74, slope 0.74. A replacement (expected eroded
  length = length × P(speed above a permissible velocity)) needs damage-type labels from another town to be tested; none exist yet.
- **Live forecast speed-up:** the 7 non-issue members now skip the 5-min frame images they never publish (commit deff33b2b); measured on
  the next cycle.
- **C1 for the live forecast:** pre-registered as an artifact fix (`PREREG_PHASE_LIVE.md`); held-out check running.
- **13 Nov 01–02Z.** Rain picking up: box mean 0.30 then 0.94 mm/h (max 6.7 mm). HRRR 1 h earlier: 0.15, 0.35; leads 3–6 h were closer
  (0.53–0.90 for 02Z), so the shortest lead is the worst one here. No snow flagged, no MassDOT water events, sentinel QUIET.
  The whatif_diag1 Turing job was rejected by the queue (spaces in an env value); the script now takes comma-separated pairs and the job
  is queued again as whatif_diag2. The forecast run in progress (43323977755, 18Z cycle) predates the LF_PHASE and frame-image commits;
  the 00Z cycle is the first with both.
- **13 Nov 03–04Z.** Rain steadier: box mean 1.13 then 1.93 mm/h (max 9.0 mm). HRRR 1 h earlier 0.54, 1.13: still about 2 × too little at
  the shortest lead; 3–4 h leads closer (1.65, 2.3). No snow flagged, no MassDOT water events, sentinel QUIET. Recorder: all 10 hours
  19Z–04Z present.
- **Pipeline fault found (13 Nov 03:39Z run).** The 00Z cycle fired the gate (Uxbridge 6 h 25.0 mm, 24 h 28.3 mm) but chose no box, so
  no flood model ran and the outlook said "Flood model run failed" for Thu–Sat. Cause: the town test used the 0.1 mm-rounded value, the
  box score the unrounded one (just under 25 mm). Fixed (`proto/forecast.py`: unrounded test, and a fired trigger always gets a box);
  the 00Z cycle re-run by hand (run 43366123146, box 176000,859000–196000,879000, 8 members, first cycle with LF_PHASE and the frame skip).
- **Latency finding.** In the 18Z cycle's issue member the "road closures" step took 64 min, of which prototype.py took **1 min** and
  `proto/resilience.py` **~63 min** (all-pairs network efficiency per 40-min frame, then again at 15 cm). The forecast never publishes
  efficiency; only `resilience_segments.csv` (closed hours, delay) feeds `risk.py` → `risk_segments.json` in the replay pack. Candidate
  fix (pipeline only): `resilience.py --no-eff` (skip efficiency and the 15 cm curve) for the issue member, and no resilience / risk for
  the other 7 members (their outputs are never read). Check before use: `resilience_segments.csv` and `risk_segments.json` byte-identical
  with and without `--no-eff` on the Sept 2023 Leominster run.
- **13 Nov 05–07Z.** Steady light rain: box mean 2.14, 1.98, 1.62 mm/h (max 10.9 mm). HRRR 1 h earlier 1.55, 1.36, 0.96: the low bias
  shrinks as the rain becomes widespread (observed / HRRR-1h ≈ 1.4–1.7). No snow flagged, no MassDOT water events; sentinel WATCH for
  the 05Z hour, otherwise QUIET. Recorder: all 13 hours 19Z–07Z present.
- **00Z cycle (hand re-run 43366123146, published 06:38Z):** box 176000,859000–196000,879000 (Uxbridge area), 8 members, "no road
  closures in 48 h". First cycle with LF_PHASE: 0.0 % of the precipitation frozen (lowest 2 m temperature 1.6 °C; max 0.1 mm as snow),
  28 of 28 wet hours had a temperature; the temperature fetch adds about 4 min. Rain in the box: max 36 mm, mean 32 mm over 66 h.
- **Latency after the fixes:** road-closure step 7–19 min per member with the frame skip only (00Z run), **0–2 min** with
  `resilience --no-eff` (next run 43380569651). What is left is the solver: 38–100 min per member (issue member 1 h 21 min wall clock),
  so a cycle now takes about 1 h 45 min from start to publish. The next latency target is the solver.
- **13 Nov 08–12Z.** Rain easing: box mean 2.21, 2.24, 1.21, 0.70, 0.43 mm/h (max 7.1 mm); 17.8 mm box-mean total since 19Z. HRRR 1 h
  earlier 1.29, 1.51, 0.89, 0.92, 0.99: the low bias of the night has turned into a small high bias as the rain eases. First snow flag:
  0.4 % of precipitating pixels at 12Z. No MassDOT water events; sentinel QUIET. Recorder: all 18 hours 19Z–12Z present.
- **06Z cycle** published 11:59Z ("no road closures in 48 h"); LF_PHASE 0.2 % frozen (min 2 m temperature 1.5 °C). Issue member: solver
  1 h 33 min wall clock at 302 % CPU (the 4-core runner is already used), grid 1000 × 1000 at 20 m.
- **Failure 08:29Z run:** one member got non-JSON answers from Zenodo for 3 min (LISFLOOD-FP source download) and the run failed; the
  source zip is now cached in Actions (`forecast.yml`, `w9_lisflood.get_lisflood`).
- **13 Nov 13–16Z.** Light rain with some snow: box mean 0.43, 0.57, 0.62, 0.38 mm/h (max 2.2 mm); snow flags on 4.8 %, 14 %, 4 %, 1.7 %
  of precipitating pixels (the hills). HRRR 1 h earlier 0.30, 0.36, 0.39, 0.20 (about 1.5 × too little again). No MassDOT water
  events; sentinel QUIET; recorder: all 22 hours 19Z–16Z present. The 12Z cycle did not fire the gate (no flood run, "no road closures
  in 48 h"); the 13Z–15Z runs also stayed below it, so the LISFLOOD zip cache is not exercised yet. Golden storm passed after the cache
  commit (run 43426065279).
- **C2 note (before testing):** the storm-drain sink is close to two candidates already tested: generic design drains on Leominster
  (`drains/DRAINS.md`) and the inlet sink on the 23 held-out storms (`drains/INLETS.md`, not adopted under §5a). C2 as fixed here (25 mm/h
  on road cells in areas ≥ 50 % impervious) differs in rate and placement, so the held-out test stands as planned; it needs 23 GPU
  solves on Turing (about 4–6 h), which needs Mo's OK (rule: ask before Turing jobs over ~3 h).
- **13 Nov 17–19Z: rain over** (box mean 0.10, 0.00, 0.00 mm/h). Storm so far (25 hours 19Z–19Z, all recorded): **19.9 mm** box mean
  (MRMS RadarOnly; gauge-corrected Pass2 to come), peak hour 2.2 mm box mean, wettest cell-hour 10.9 mm: a long, light rain, well
  below flooding intensity. HRRR, summed by lead over the same 25 hours: 13.2 mm at 1 h, 9.2 at 2 h, 12.8–13.0 at 3–6 h, i.e. **about
  35 % too little at every lead** (46 % at 2 h). Snow: at most 14 % of precipitating pixels (14Z), none after 17Z. No MassDOT water
  events, no NWS flood alerts, sentinel QUIET throughout; every published cycle (12 Nov 12Z – 13 Nov 12Z) said "no road closures in
  48 h". Post-storm work starts after 6 dry hours (from ~23Z): reports, radar replay, results file.
- **Replay rerun with the live closure rules** (parity_test 43535831025, `PROTO_RES_CONSISTENT=1 PROTO_RC_START_H=rain`): 0 segments
  p ≥ 0.5 with and without C2 (first replay: 2, both culvert-notch start-up water). Matches the reports (none). Summary:
  `storm_2026-11-13_results.md`.
