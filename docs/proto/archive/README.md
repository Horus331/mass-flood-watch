# Storm archive: every District 3 storm becomes a test case

The catalogue (`docs/proto/obs/catalog.json`) was built by hand from past storms. This folder grows on its own. Each time heavy rain is
forecast or the NWS warns for flooding in MassDOT District 3, the forecast of that moment is kept. A day or so later the same area is run
with the radar rain that actually fell, the public flood reports are collected, and the forecast is scored against both. Forecast skill
therefore accumulates storm by storm without anyone having to remember to do it.

Code: `proto/storm_archive.py`. Workflows: `.github/workflows/forecast.yml` (trigger and forecast copy) and
`.github/workflows/archive_followup.yml` (everything after the storm).

## When a storm is archived

On every 6-hourly forecast cycle, either of these archives the storm:

- **The forecast gate fires.** A District 3 town has an HRRR forecast 6 h maximum of 25 mm or more, or a 24 h maximum of 40 mm or more
  (`docs/proto/forecast/GATE.md`). A gate forced by hand does not count.
- **The NWS has a Flash Flood Warning or Flood Advisory touching a District 3 town.** The same forecast job asks `api.weather.gov` for
  Massachusetts alerts sent or in force since the previous cycle (6.5 h look-back). It keeps those whose polygon (or, for zone alerts,
  the zones' polygons) overlaps one of the 73 District 3 towns: Worcester County, the western Middlesex towns and the Franklin / Hampshire
  towns in the district. Past periods (tests, backfill) use the IEM archive of NWS storm-based warnings (VTEC `FF.W`, `FA.Y`). The event
  list can be changed with `ARCHIVE_ALERT_EVENTS`.

A cycle whose evidence window starts within 12 h of an archived storm's window joins that storm, as long as its radar run has not been done
yet. A storm can therefore hold several forecast cycles, which gives forecasts at several lead times. Quiet cycles write nothing.

## What a storm folder holds

`docs/proto/archive/<YYYYMMDD>_<id>/`, where `<id>` = `arc<YYYYMMDD>` (local date of the first evidence; `b`, `c`... if a date repeats):

| path | written by | content |
| --- | --- | --- |
| `storm.json` | both | evidence window, trigger per cycle (gate / NWS alerts), boxes, radar window, radar / label / verification status |
| `forecast/<YYYYMMDDHH>/status.json` | forecast.yml | that cycle's `forecast_status.json` (headline, rain summary, runs, k of n) |
| `forecast/<YYYYMMDDHH>/gate.json`, `alerts.json` | forecast.yml | the gate decision and boxes, and the NWS alerts that touched District 3 |
| `forecast/<YYYYMMDDHH>/kofn.csv`, `kofn_meta.json` | forecast.yml | every segment closed by at least one member: k, n, likely / possible, box, centre (EPSG:26986) |
| `obs/lsr.csv`, `obs/stormevents.csv`, `obs/gauges.json` | follow-up | raw LSRs, Storm Events rows, USGS gauges for the boxes |
| `radar/<box>/` | follow-up | radar-driven run: `summary.json`, `score.json` (gauges), `points.json`, `features_<id>.csv` + `matches_<id>.json`, `segments.csv`, `flood_meta.json`, `config.json` |
| `verify.json` | follow-up | forecast vs radar run vs labels, per box and archived cycle |

No viewer frame packs are copied. The live viewer pack of a cycle stays only as long as the next cycle does not overwrite it.

Folder-level files are written only by the follow-up job (one writer, so the two workflows never conflict). A newly archived storm is listed at
the next follow-up run, within 12 h. The files are `ARCHIVE.md` (index and accumulated skill tables), `skill.json` (every verification row
plus pooled totals), and
`catalog_candidates.json` (archived storms that have labels, in the `catalog.json` event format, with `selected: false`). Candidates are
**not** added to `docs/proto/obs/catalog.json` automatically. A person reviews the labels first.

## The follow-up job (24-36 h after the storm)

`archive_followup.yml` runs at 04:23 and 16:23 UTC. A storm is due once its evidence window (gate rain windows and alert periods) ended
24 h ago, so it is processed 24-36 h after the event. Nothing due means no further jobs and no commit. When something is due:

1. **Labels** → `proto/data/labels_<id>_auto.csv`, in the catalogue label schema plus a `quality` column. Rows are kept only if they fall
   inside a District 3 town and in the radar window plus 12 h.

   | source | what | coordinates | quality |
   | --- | --- | --- | --- |
   | NWS LSR (IEM) | FLOOD / FLASH FLOOD reports, and HEAVY RAIN reports whose text mentions road flooding | snapped to the named road nearest the report point (`approx`), else `town` | medium (low if `town`) |
   | NOAA Storm Events | Flash Flood / Flood / Heavy Rain narratives, one row per road sentence | snapped to the named road, else the 4-decimal event point (`approx`) | medium |
   | MassDOT roadway events log | events whose text mentions flooding, water on the road, washouts, sinkholes or culverts (not water mains) | MassDOT point (`exact`) | high |
   | SeeClickFix | 311 issues in the storm boxes, created up to 24 h after the window, with flood-like text | the issue pin (`approx`) | low |

   NOAA publishes Storm Events about 2-4 months late. The follow-up re-checks weekly between 45 and 200 days after the storm, until rows
   appear, then rewrites the label file and the verification. Labels are unreviewed. A storm becomes a catalogue storm only after review.
2. **Radar-driven run.** The storm's boxes (gate boxes first, then a 20 × 20 km box on each NWS alert polygon in District 3; at most 4,
   overlap at most 25 %) are run with the observed MRMS Pass2 radar rain. The window runs from 6 h before the evidence start to 12 h after
   its end, clamped to 24-48 h. Each box runs on CPU on Actions with the frozen settings of `docs/proto/parity/BASELINE.md`: `LF_PARITY=1`,
   `LF_LOSS=cn`, AMC II, `LF_CN_SCALE=0.88`, `LF_INFIL_MMH=2`, `LF_QOUT=1`, `LF_VOUT=1`, 20 m. Then `prototype.py`, `score.py` (gauges),
   `validate_points.py` and `closure_ml.py extract` run as for the catalogue. A failed box is retried once on the next follow-up.
3. **Verification** (`verify.json`). For every radar box and every archived cycle:
   - *forecast vs radar run*: the forecast's likely-closed segments (k ≥ 2 of the 8 time-lagged members; P ≥ 0.5 for a single run) against
     the radar run's segments at P(close) ≥ 0.5, inside the box. It reports hits, misses, false alarms, POD, FAR and CSI, plus a 1 km
     neighbourhood POD and success ratio (forecast storms are often displaced). A quiet gate counts as a forecast of no closure.
   - *forecast vs labels* and *radar run vs labels*: `proto/score_v2.py` on the same box (strict 30 m matches, sites clustered at 150 m).
     It reports sites, site hits, recall, chance recall, lift, site CSI and FSS at 300 m. The forecast is scored as a run whose flagged set is
     the likely-closed set.

   `ARCHIVE.md` pools the rows over all storms. It shows the latest cycle per storm and box (the shortest lead), and all cycles.

## Running it by hand

```
# re-run the follow-up for one storm now (e.g. after fixing labels)
gh workflow run archive_followup.yml -f storm=arc20270712 -f force_radar=false
# a past storm, without touching the live archive: forecast cycle + NWS alerts from the IEM archive into a scratch folder
gh workflow run forecast.yml -f init=2023-09-11T12Z -f prefix=archtest -f archive_root=docs/proto/archive_test \
   -f alerts_window=2023-09-11T00:00Z/2023-09-12T06:00Z -f max_boxes=1 -f hours=24
gh workflow run archive_followup.yml -f root=docs/proto/archive_test -f labels_dir=docs/proto/archive_test/labels -f storm=arc20230911
python proto/storm_archive.py selftest      # offline logic checks
```

The end-to-end test above (Sept 11, 2023, Leominster) was run before the archive went live, and its scratch folder was deleted.
