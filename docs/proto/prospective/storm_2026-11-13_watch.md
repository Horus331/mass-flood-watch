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
