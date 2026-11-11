# Sentinel: storm state for District 3 (Phase 0.4, 11 Nov 2026)

`proto/sentinel.py`, run by `.github/workflows/sentinel.yml` every ~10 min (GitHub cron can run late). Light: about a minute, no model run.
Output: `docs/site/data/status.json`, shown at **/status/** on the site.

## States (fixed before the first run)

| state | when |
|---|---|
| **ACTIVE** | a Flash Flood Warning or Flood Warning in force touching District 3, or MRMS radar 1 h rain ≥ 25 mm anywhere in the District 3 box |
| **WATCH** | a Flood Watch, Flash Flood Watch or Flood Advisory in force touching District 3, or radar 1 h rain ≥ 10 mm, or the newest forecast's rain gate triggered (not a forced run) with its window still open |
| **QUIET** | otherwise |

Up at once; down only after 60 min without the higher state's condition. The 10 / 25 mm levels are the live-feeds alert levels
(`proto/live_feeds.py RAIN_LEVELS`, NWS heavy-rain rates ~0.4 / 1 in/h). If NWS alerts and radar are both unreachable the state is held from
the last good check, `blind` is set, and the job fails so an Issue is opened.

## Sources and refresh

| source | how the sentinel reads it | refresh at the source |
|---|---|---|
| NWS alerts | api.weather.gov, every run | real time |
| MRMS radar 1 h rain | newest RadarOnly QPE 1 h file on AWS, District 3 box maximum | ~2 min |
| HRRR | newest cycle with 18 h out on AWS | hourly (~1 h 50 min latency) |
| road-closure forecast | `forecast_status.json` (forecast.yml) | 6-hourly |
| live feeds | `live/status.json` (live_feeds.yml) | hourly |
| USGS gauges | `live/gauges.json` (live feeds) | ~15 min at USGS; read hourly here |

## What each state will start (not wired yet)

QUIET: hourly refresh. WATCH: pre-stage the ensemble. ACTIVE: full physics ensemble, refresh every 5–10 min. Wiring waits for the engine
work (Phase 3) and for ARC's answer on recurring Turing jobs.

## Failures

`.github/workflows/failure_issue.yml` opens one GitHub Issue per failing live workflow ("Failing: <name>"), comments on repeat failures and
closes it on the next success.
