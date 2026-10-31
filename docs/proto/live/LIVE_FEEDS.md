# Live feeds for MassDOT District 3 (started 31 Oct 2026)

Six live feeds, refreshed hourly by GitHub Actions and written as small JSON files to `docs/site/data/live/`. They give context
next to the forecast: rain now, where the rain is heading, stream response, flow at culverts, snow. A seventh output stores reports for
later scoring. **None of these feed the flood model**, and none has been checked against what actually flooded.

- Code: `proto/live_feeds.py` (one subcommand per feed, plus `run`, `map-comids`, `nowcast-check`, `selftest`)
- Workflow: `.github/workflows/live_feeds.yml`. Runs hourly at `:26`, and can also be started by hand (`workflow_dispatch`, inputs `feeds`, `force`, `map_comids`, `nowcast_check`)
- District box: lat 41.98–42.75, lon −72.25 to −71.25. Per-town values use the 73 District 3 town polygons (`proto/forecast.py d3_towns()`).

## How a run works

- **Separate processes.** Each feed runs in its own Python process (`run` → `_child <feed>`) with its own timeout (300 s; 900 s for `nwm`).
  If one feed raises an exception, segfaults or hangs, only that feed fails. In the first Actions run, netCDF4 aborted inside a thread pool
  and took the whole job down. That bug is fixed, and the isolation now contains that kind of crash.
- **Status file.** `docs/site/data/live/status.json` holds `feeds.<name>` = `{state: ok|failed, last_success, last_attempt, seconds, error, file}`.
  When a feed fails, its previous output file is kept and `last_success` still points at it.
- **When a run commits.** A run makes at most one commit, and only when `decide()` says so:
  1. *immediately* when an alert signature changes. The signatures are: the rain level (1 h max ≥ 10 / 25 / 50 mm), the nowcast level (same thresholds), the set of FLASH-flagged towns, and the set of culverts over capacity in NWM;
  2. when the material digest has changed and the last commit is ≥ 3 h old. The digest covers rounded district values, wet towns, new report ids and feed states, and ignores timestamps;
  3. a 24 h heartbeat, so a reader can tell the feed is alive.

  A quiet hour makes no commit, which keeps GitHub Pages from rebuilding on every run.
- **Reading the logs.** Log lines are echoed as `::notice` annotations. Read them with
  `gh api repos/Horus331/mass-flood-watch/check-runs/<job id>/annotations`, because raw run logs cannot be downloaded from every client.

## Feeds, endpoints and what was verified in Actions

Verified runs: 41219698432, 41221040778 and 41222378352 (31 Oct 2026, 16:26–17:05 UTC, dry weather). In the last two, all six feeds were `ok`.

| feed | output | endpoint(s) | verified in Actions |
|---|---|---|---|
| **1. Observed rain** | `rain.json`, `rain_grid.json`, `rain_1h.png` | AWS `https://noaa-mrms-pds.s3.amazonaws.com/CONUS/<product>/<YYYYMMDD>/` (S3 ListObjectsV2 + GET); products `RadarOnly_QPE_01H_00.00`, `RadarOnly_QPE_03H_00.00` (2-min), `MultiSensor_QPE_01H_Pass1_00.00`, `MultiSensor_QPE_03H_Pass1_00.00` (hourly), `PrecipRate_00.00` (2-min). Source: [NOAA MRMS on AWS](https://registry.opendata.aws/noaa-mrms-pds/) | ok, ~5 s. RadarOnly 1 h valid 16:36Z on a 16:39Z run. MultiSensor Pass1 valid 16:00Z. RadarOnly 3 h had no file within 30 min, so its window was widened to 90 min. All values were 0 (dry day). |
| **2. Nowcast 0–2 h (EXPERIMENTAL)** | `nowcast.json` | Same bucket, `PrecipRate_00.00`: 3 frames 10 min apart, over the district plus an upstream margin (lat 40.48–44.25, lon −74.45 to −70.05) | ok. **pysteps** installs on Actions (Python 3.11, `pip install pysteps opencv-python-headless`), and the Lucas-Kanade + semi-Lagrangian path ran in the spot check. The fallback is phase correlation (one uniform vector, linear shift). |
| **3. MRMS FLASH** | `flash.json` | Same bucket: `FLASH_CREST_MAXUNITSTREAMFLOW_00.00` (10-min), `FLASH_QPE_FFG01H_00.00`, `FLASH_QPE_FFG03H_00.00`, `FLASH_QPE_FFG06H_00.00` (2-min, QPE / flash-flood guidance). Source: [MRMS FLASH](https://inside.nssl.noaa.gov/flash/) | ok, ~5 s. District max unit streamflow 1.2 m³ s⁻¹ km⁻², ratios 0. |
| **4. NWM short range at culverts** | `nwm.json` (+ `docs/proto/live/nwm_baseline.json`) | AWS `https://noaa-nwm-pds.s3.amazonaws.com/nwm.YYYYMMDD/short_range/nwm.tHHz.short_range.channel_rt.f001..f018.conus.nc` ([NWM on AWS](https://registry.opendata.aws/nwm-archive/)); cross-check `https://api.water.noaa.gov/nwps/v1/reaches/{COMID}/streamflow?series=short_range` ([NWPS API](https://api.water.noaa.gov/nwps/v1/docs/)); culvert → COMID via USGS NLDI `https://api.water.usgs.gov/nldi/linked-data/hydrolocation?coords=POINT(lon lat)`, falling back to `.../comid/position` + `.../comid/{comid}` flowline geometry ([NLDI](https://api.water.usgs.gov/nldi/swagger-ui/index.html)) | ok, ~42 s, 222 MB per run (18 files). The newest cycle is often not complete about 1.5 h after its hour, so the code walks back to the latest cycle with all 18 files. NWPS returned the same series (peak 3.63 vs 3.62 m³/s; NWPS units ft³/s, converted). Its reference time was one cycle older than the S3 cycle. |
| **5. Snow (SNODAS)** | `snow.json`; extra field `frost.snodas` in `docs/site/data/ground.json` | `https://noaadata.apps.nsidc.org/NOAA/G02158/masked/YYYY/MM_Mon/SNODAS_YYYYMMDD.tar` (snow depth `ssmv11036`, SWE `ssmv11034`; [NSIDC G02158](https://nsidc.org/data/g02158)) | ok, ~2 s. Read the 2026-10-31 file. Depth and SWE were 0. Header units "Meters / 1000" were parsed to mm. |
| **6. Validation reports** | `validation.json`; archive `docs/proto/live/archive/YYYY-MM.jsonl` | MassDOT roadway events XML `http://events.massdot.evbg.net/` ([mass.gov highway data for developers](https://www.mass.gov/info-details/highway-data-for-developers); the page states no licence, attribution or rate limit for this feed and says it "does not include all incidents"); SeeClickFix `https://seeclickfix.com/api/v2/issues` (box + `after`, 24 h window; [API docs](https://dev.seeclickfix.com/)) | ok. MassDOT returned 1 event statewide and 0 kept. SeeClickFix returned 59 issues in the box over 24 h and 0 flood-like. The archive file has not been created yet because no record has been kept. |

### Output fields (UI hooks)

- `status.json`: `feeds.<name>.state | last_success | error`, `committed.utc | reason`, `alerts`
- `rain.json`:
  - `max_1h`, `max_3h`, `level` (0–3)
  - `products.<radar_1h|radar_3h|ms_1h|ms_3h|rate>.{valid, district_max, district_mean}`
  - `towns` rows per `town_fields` = `[town, radar_1h_max, radar_1h_mean, radar_3h_max, ms_1h_max, ms_3h_max, rate_max]`
  - `grid.{png, bounds_latlon [[s,w],[n,e]], ramp_mm}` for a Leaflet `imageOverlay`
  - `rain_grid.json`: `data` is ints of 0.1 mm, rows run north to south, −1 = missing, about 16 KB
- `nowcast.json`:
  - `experimental: true`, `skill` (a text caveat; show it), `issued`, `valid_to`, `method`, `motion.{speed_kmh, toward_deg}`
  - `district.{max_0_1h, max_0_2h}`
  - `towns` rows = `[town, max_0_1h_mm, mean_0_1h_mm, max_0_2h_mm, mean_0_2h_mm]`
- `flash.json`:
  - `products.<unitq|ffg01h|ffg03h|ffg06h>.{valid, district_max}`
  - `towns` rows = `[town, unitq_max, ffg01h_ratio_max, ffg03h_ratio_max, ffg06h_ratio_max]`
  - `flagged[] = {town, why[]}`. A town is flagged when unit streamflow > 2 m³ s⁻¹ km⁻² or QPE/FFG > 1.0.
- `nwm.json`:
  - `cycle`, `valid`
  - `exceed[]` = `{id, road, stream, lon, lat, comid, snap_m, q_now, q_peak, t_peak, q_crest, ratio, p_overtop, q_base}`
  - `top[]`, the 15 highest ratios, and `suspect[]`
  - `over_pk10[]`, for culverts that have StreamStats peaks
- `snow.json`: `date`, `depth_cm.{district_mean, district_max}`, `swe_mm.{...}`; `towns` rows = `[town, depth_cm_max, depth_cm_mean, swe_mm_mean]`
- `validation.json`: `sources.<massdot|seeclickfix>.state`, `recent_48h[]` = `{id, src, kind (flood|closure), town, lat, lon, t, category|type, summary}`, `attribution`

## Method notes and limits

**Rain.** The `radar_*` fields are RadarOnly QPE: real-time but not gauge-corrected. The `ms_*` fields are MultiSensor Pass1:
gauge-corrected, hourly, with about 1 h latency. The map layer uses RadarOnly 1 h, or MultiSensor 1 h when RadarOnly is missing. Values
are the 0.01° cells inside each town. A town smaller than a cell takes the nearest cell.

**Nowcast: experimental, with weak skill beyond the first hour.**
- *What it does.* It extrapolates the current PrecipRate field with a motion field and assumes no growth or decay. The 0–1 h and 0–2 h
  totals sum twelve 10-minute steps.
- *Spot check.* `python proto/live_feeds.py nowcast-check --at ...` produced `docs/proto/live/nowcast_check.json`. It ran on four issue
  times in two development storms, sep2023 (11 Sep 2023 18Z, 20Z) and aug2021 (19 Aug 2021 11Z, 14Z). No setting was chosen from these
  results. It compares town-mean rain against the RadarOnly 1 h QPE that followed.
- *0–1 h result.* pysteps had a lower MAE than Eulerian persistence in 3 of 4 cases (0.16 vs 0.20, 1.45 vs 1.93, 10.4 vs 10.6 mm). It was
  worse in 1 case (4.36 vs 4.22). Correlation was 0.42–0.87.
- *1–2 h result.* The town-mean correlation was 0.08–0.33 in three cases. In one case it was 0.92, but with a +7.5 mm bias.
- *Phase-correlation fallback.* Its 0–1 h MAE was mixed against persistence.
- *Status.* Four cases are not a verification. Every issued nowcast with ≥ 1 mm somewhere is appended to the archive (`src: nowcast`)
  for later scoring. Until then the UI should say "where current rain is heading", not "forecast".

**FLASH.** The values are the maximum MRMS cell in each town. The FLASH grids are 1 km, and CREST unit streamflow is already routed
through the basin. The thresholds (2 m³ s⁻¹ km⁻², ratio 1.0) are the usual FLASH guidance values. They have not been calibrated
against District 3 closures.

**NWM at culverts.**
- *Which culverts.* 944 District 3 crossings in `docs/network/crossings_all.json` have either an HDS-5-computable barrel (shape, rise,
  span) or StreamStats peaks. All 944 are mapped to NHDPlus v2 COMIDs in `docs/proto/live/crossing_comids.json`.
- *Mapping.* The NLDI `hydrolocation` endpoint gave the flowline snap for 294 crossings. The other 650 came from the catchment
  `comid/position` lookup, with the distance to that flowline computed. Only snaps ≤ 100 m are used, which leaves 502 culverts (500 with NWM flow) in
  343 reaches. NHDPlus v2 is 1:100k, so many small culvert streams are not in it.
- *Capacity.* `q_crest` is the flow at which HDS-5 headwater reaches the road crest. It is computed from the rise plus the NAACC fill
  (0.6 m when the fill is unknown), with NAACC blockage applied: the same quantity as `prototype.culvert_probability`.
- *What NWM measures.* The NWM flow is the flow at the reach outlet, so it covers the whole reach's drainage area. It is therefore an
  upper bound on the flow at a culvert partway along the reach.
- *Suspect culverts.* A culvert whose capacity is at or below the reach's low-flow baseline is listed under `suspect`, never under
  `exceed`. The baseline is the lowest NWM flow seen so far, first filled on a dry 31 Oct. On the first run, two such culverts
  (Barker Hill Rd and Turnpike Rd / Squannacook River, capacity 0.7–0.8 m³/s against 1.3 m³/s dry-day flow) showed as "over capacity".
  They are now among the 3 suspects.
- *Probability.* `p_overtop` = Φ(ln(Q/Q_crest)/0.30), as in the prototype.
- *Status.* Nothing here is validated.

**Snow.** SNODAS is a daily model analysis (06 UTC) at 30 arc-seconds. NSIDC posts it the same day. The feed tries today and then the 4
days before. `proto/ground_state.py` copies the district mean and max into `frost.snodas` as an extra field only. The CFGI frozen-ground
index still uses the KORH snow depth, unchanged.

**Validation reports (not truth).**
- *MassDOT.* The feed covers current events only. Events are kept when they fall inside a District 3 town and either match flood words or
  are full closures. `proto/events_logger.py` already logs the whole feed every 15 min (`docs/proto/obs/massdot_events/`), so if a quiet
  hour skips a commit, nothing is lost.
- *SeeClickFix.* Issues are licensed CC BY-NC-SA 4.0. Only the id, time, location, category and a 120-character summary are stored
  (attribution is in `validation.json`). The 24 h query window spans the 3 h commit cadence.
- *Deduplication.* Records are deduplicated by `id` across this month's and last month's archive files.

## Commands

```
python proto/live_feeds.py selftest                       # offline: phase correlation, SNODAS reader, town index, HDS-5 q_crest, commit rule, filters
python proto/live_feeds.py run --feeds rain,flash         # what the workflow runs (all feeds by default)
gh api -X POST repos/Horus331/mass-flood-watch/actions/workflows/live_feeds.yml/dispatches -f ref=main -f 'inputs[force]=true'
```
