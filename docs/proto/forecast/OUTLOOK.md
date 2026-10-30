# 7-day storm outlook (`docs/site/data/outlook.json`)

The flood model looks only 48 h ahead, because the HRRR stops at 48 h (`GATE.md`). The Live tab also shows a **week view**: rain and risk
for District 3 over the next 7 local days, refreshed every 6 h, with a health chip.

- **Code:** `proto/outlook.py`.
- **Workflow:** `.github/workflows/forecast.yml`:
  - the `outlook` job fetches the sources alongside the gate;
  - a publish step writes `outlook.json` in the **same commit** as `forecast_status.json`.
- **Test prefixes:** `prefix` other than `forecast_latest` writes `docs/site/data/<prefix>_outlook.json`; `publish=false` commits nothing.
- **Manual check:** `outlook_test.yml` prints the JSON into the job summary and annotations and never commits.

**The week view is a rain outlook, not a flood forecast.** Road closures come only from the flood model, and it runs only when the 48 h HRRR
gate fires.

## 1. Schema (`schema: "outlook/1"`)

All times are UTC ISO `YYYY-MM-DDTHH:MMZ`; local dates are `America/New_York`. Rain is in mm. A field can be `null` when its source is missing.

```text
{
  schema      "outlook/1"
  issued      when this file was built (= health.issued)
  tz          "America/New_York"
  headline    one line for the strip, e.g. "No storm in District 3 in the next 7 days",
              "Heavy rain possible Sat–Sun, up to 48 mm in a town", "Rain Tue, up to 14 mm in a town, below the flood threshold",
              "Flood model running for the storm Fri", "Week outlook unavailable (rain forecast missing)"
  thresholds  {max6h_mm 25, max24h_mm 40   (the flood-model gate, GATE.md),
               rain_day_mm 10 (town max from which a day is a rain day), light_mm 2 (below = quiet), basis}
  days[7]     day 1 = today (local), in order:
    day           1..7
    date          local date "2026-10-31";  label "Sat 31 Oct"
    start, end    local midnight to midnight, in UTC
    hours         hours of forecast rain counted in the day (day 1 is partial: only the rest of today; 23/25 on DST days)
    partial       true when hours < 22
    rain          null when the rain source is missing, else
      d3_mean_mm      mean of the day total over the grid points inside District 3
      town_max_mm     the wettest town's day total (town value = max over its grid points, as the gate)
      town_max        that town, or null when town_max_mm < 0.1
      max6h_mm        highest 6 h bucket in any town that day
      max24h_mm       highest running 24 h total (4 buckets) attributed to the day (the day of its wettest 6 h bucket)
      six_hourly_start[], six_hourly_mean_mm[], six_hourly_max_mm[]   the day's 6 h buckets (start time, district mean, town max)
    towns_over       towns reaching a gate threshold that day (union of the next two)
    towns_over_6h    6 h bucket >= 25 mm
    towns_over_24h   running 24 h >= 40 mm
    ero           null (no ERO for this day: days 6-7, or source missing), else
                  {day 1-5, category "none"|"marginal"|"slight"|"moderate"|"high", level 0-4, valid [start, end], towns[] touched at that level}
    alerts        names of NWS alerts touching District 3 in force during the day, e.g. ["Flood Watch"]
    flood_model   {in_window: day overlaps the 48 h HRRR window of the current forecast cycle,
                   state: forecast_status.state ("quiet"|"run"|"error") when in_window else null, trigger: gate fired (null outside)}
    level         0 quiet | 1 light rain | 2 rain, below flood threshold | 3 heavy rain possible | 4 flood model running / failed | null no data
    verdict       plain words for the level (see §3)
    detail        one short reason, e.g. "up to 14 mm in a town", "3 towns over the flood-model threshold; WPC slight risk of excessive rain."
  storms[]    runs of consecutive days with level >= 2, in time order:
    id "s1"..; start_date, end_date (local); days [day numbers]; peak_day, peak_date (highest level, then wettest)
    start, end      first / last 6 h bucket with >= 1 mm in some town (UTC)
    d3_mean_mm      storm total, district mean;  town_max_mm, town_max  storm total in the wettest town
    max6h_mm, max24h_mm;  level (max of its days);  verdict (of the peak day);  ero_max;  alerts[];  towns_over[]
  alerts[]    NWS alerts touching a District 3 town (flood-related first), max 20:
    {event, flood (true for flood / flash flood / hurricane / tropical storm products), severity, urgency, headline, onset, ends, sent,
     towns_n, towns[] (first 15), id}
  sources     rain   {ok, model "NBM"|"GFS", run "2026-10-29T21Z", source, resolution_km, horizon_h, files, missing_buckets, n_points, notes[]}
                     or {ok false, error}
              ero    {ok, partial, source, errors[], days[{day, ok, category, level, valid, issued, n_features, via "geojson"|"mapserver"}]}
              alerts {ok, source, fetched, n_ma (alerts in MA)} or {ok false, error}
  health
    status        "ok"      every source present
                  "partial" rain present, the ERO or the alerts missing
                  "failed"  no rain forecast; the file then also carries
                            previous {issued, headline, days, storms}, the last good outlook, and days_from_previous
    problems[]    one line per missing source
    issued        build time;  fetched  source fetch time;  rain_run  model cycle used
    next_update   next scheduled forecast.yml start (cron); results usually land 10-60 min later (typical_delay_min [10, 60])
    schedule_cron "40 2,8,14,20 * * *";  schedule_utc ["02:40","08:40","14:40","20:40"]
    stale_after_h 7
    workflow, run_url (the Actions run that built the file)
    forecast_cycle {issued, built, state, headline, valid}  copied from forecast_status.json of the same cycle
  method      one paragraph, for a tooltip
}
```

**Health chip, viewer rule.**

| condition | chip |
| --- | --- |
| `now − health.issued > stale_after_h` | **stale** |
| `health.status == "failed"` | **broken** |
| `health.status == "partial"` | **partial** |
| otherwise | **OK** |

Show the chip as "updated X h ago, next at HH:MM", from `health.issued` and `health.next_update` in local time.
`health.forecast_cycle.built` is when the flood forecast itself was last refreshed. A cycle whose gate fires publishes later, after the flood
runs (up to about 5 h after the cron start).

## 2. Sources

| | source | what is used |
| --- | --- | --- |
| Daily rain | **NOAA NBM v4** (National Blend of Models, 2.5 km), AWS open data `noaa-nbm-grib2-pds`, `blend.YYYYMMDD/HH/core/blend.tHHz.core.fFFF.co.grib2`, no key | Deterministic QPF: the `APCP:surface:a-b hour acc fcst:` records without `prob` / `std` qualifiers. The newest hourly cycle with `f168` posted is used, in 6 h buckets ending at 00/06/12/18z (the first bucket after init can be 3 h). Each record is read by an HTTP byte range from the `.idx`. NBM cycles reach f153–f264 depending on the hour, enough for the end of local day 7. |
| Fallback rain | **NOAA GFS 0.25°**, AWS `noaa-gfs-bdp-pds`, `gfs.tHHz.pgrb2.0p25.fFFF` | The same 6 h buckets (`b-6-b hour acc`; `day acc` records are parsed too). Used only when no NBM cycle works. 25 km is coarse: most towns get their nearest point. |
| Excessive Rainfall Outlook | **NWS WPC**, `https://www.wpc.ncep.noaa.gov/exper/eromap/geojson/Day{1..5}_Latest.geojson`; fallback `https://mapservices.weather.noaa.gov/vector/rest/services/hazards/wpc_precip_hazards/MapServer` (layer per day, envelope query) | Highest category of the polygons intersecting a District 3 town polygon. Valid period from the feature's `start_time` / `end_time` (else 12z–12z). An ERO day maps to the local day holding its mid-point. |
| Alerts | **api.weather.gov** `/alerts/active?area=MA` | Every alert whose polygon, or the union of its zones, touches a District 3 town (`storm_archive._d3_hit`). `flood=true` for flood, flash flood and tropical products. |
| Flood-model state | `docs/site/data/forecast_status.json` of the same cycle | `valid`, `state`, `gate.trigger`, `headline`. |

District 3 = the 73 towns of `forecast.d3_towns()`. A town's value is the maximum over the grid points inside it, or the nearest point for a
town smaller than a cell. This matches the HRRR gate.

## 3. Verdicts (per day, first rule that applies)

| level | verdict | rule |
| --- | --- | --- |
| 4 | Flood model running | The day is inside the 48 h HRRR window and the cycle's `state` is `run`; `detail` = the forecast headline. |
| 4 | Flood model run failed | The same, with `state` `error`. |
| 3 | Heavy rain possible: flood model runs when within 48 h | Beyond the HRRR window, and any of: a town over a gate threshold (NBM/GFS), WPC slight or higher, or a flood-related watch / warning in force. |
| 3 | Heavy rain possible, below the flood-model threshold in the 48 h forecast | The same triggers inside the HRRR window while the HRRR gate stays quiet. |
| 2 | Rain, below flood threshold | Town max ≥ 10 mm, or WPC marginal risk. |
| 1 | Light rain | Town max ≥ 2 mm. |
| 0 | Quiet | Otherwise. |
| null | No data | No rain source and no ERO for that day. |

**Storms** are runs of consecutive days at level ≥ 2. The headline names the highest-level storm, the wettest when levels tie.

## 4. Caveats

- **Week-ahead rain is uncertain.** The NBM is a calibrated blend. Its deterministic QPF is smooth and spreads rain: it rarely shows the local
  6 h peaks that flood roads, and day 4–7 amounts and timing often move by a day or more between cycles. Read days 3–7 as "a storm is
  possible", not as amounts.
- **The gate thresholds were set on the HRRR** (3 km, hourly, running windows; `GATE.md`). Here they are applied to 6 h *buckets* of a smoother
  model, so `towns_over` is a rough flag. It usually under-calls compared with the HRRR gate: aligned buckets miss the peak window, and the
  blend is lower than any single member.
- **The flood model only runs within 48 h.** A level-3 day beyond 48 h means "watch this storm". Road closures appear only once the HRRR gate
  fires for it, typically 1–2 days before.
- **Local days are approximate.** Each 6 h bucket counts in the local day holding its mid-point, so a day runs about 02:00–02:00 EDT
  (01:00–01:00 EST). A running 24 h total counts, per town, in the day of its wettest 6 h bucket.
- **The ERO is a national product** at the scale of WFO areas. A marginal or slight polygon touching one town colours the whole day.
  Days 6–7 have no ERO.
- **Never fails the forecast.** The fetch job and the publish step are `continue-on-error`. If the fetch fails, `outlook.json` is still written,
  with `health.status = "failed"` and the previous outlook under `previous`. If the whole publish job fails, the file keeps its old `issued`
  and the viewer shows it as stale.

## 5. Verification (29–30 Oct 2026)

- `python proto/outlook.py selftest` covers:
  - local-day assignment;
  - gate exceedances, including 24 h spill-over across midnight;
  - ERO day mapping;
  - verdicts, storms;
  - health ok / partial / failed.
- **Live run (NBM 2026-10-29 21z):** every source answered, `status ok`. District 3 is dry for the week ("No storm in District 3 in the next
  7 days"). The GFS 18z fallback agreed: ≤ 0.8 mm in any town on any day. WPC ERO days 1–5: none. One Special Weather Statement covered the
  73 towns.
- **Replay at 2023-09-10 14z** (NBM 13z cycle, the day before the Sept 11, 2023 Leominster storm; the ERO and alerts were live, not
  historical):
  - Sun 42 mm and Mon 44 mm town max; 6 h max 34 mm; 24 h max 46 mm; 22 towns over the gate; both days level 3.
  - Storm s1 Sun–Mon: total 64 mm in Worcester.
  - Tue (1 mm): quiet. Before the 24 h attribution fix it was wrongly level 3, from Monday-evening rain.
  - Wed 28 mm and Sat 26 mm: rain, below flood threshold (storms s2 and s3).
- **`forecast.yml` dispatch** with `prefix=outlooktest publish=false`:
  - the outlook job ran alongside the gate (~1 min);
  - publish wrote `outlooktest_outlook.json`;
  - nothing was committed.
