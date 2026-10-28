# MassDOT District 3 data: the day the files arrive

This page covers the District 3 data request handled by David Henriques (MassDOT GIS). The request has four parts:

1. Waze flooded-road, hazard and road-closure alerts.
2. The Repeating Flood Areas (RFA) layer.
3. Flood-related closure and incident logs, such as Highway Operations Center (HOC) logs.
4. Stormwater drainage structures and known flooding locations.

Each part takes one command. The importer is `proto/massdot_import.py`, and its docstring has the full rules. It reads:

- shapefiles (`.shp`, or a `.zip` holding one)
- file geodatabases (`.gdb` or `.gdb.zip`, every layer)
- GeoJSON, CSV and XLSX files
- Waze feed JSON snapshots
- a folder of any of these
- an ArcGIS REST `FeatureServer` or `MapServer` URL (it pages through the layer)

Coordinates are reprojected to EPSG:4326 and 26986. When the CRS is missing, it is guessed from the value range (WGS84, 26986, 2249 ftUS or 3857).

## 0. Check (2 min, writes nothing)

```
python proto/massdot_import.py selftest                      # ~20 s; every format x every kind on synthetic fixtures
python proto/massdot_import.py inspect <file|folder|url>     # columns, detected mapping, CRS, time range
```

If a column is mapped wrongly, or not mapped at all, add `--map field=Column` (comma-separated or repeated) to `inspect` and `ingest`. The fields
are `time`, `time_only`, `end_time`, `lon`, `lat`, `x`, `y`, `road`, `cross`, `town`, `uuid`, `type`, `subtype`, `desc`, `cause`, `closure`, `thumbs`, `not_there`,
`reliability`, `struct`, `flood_flag` and `dates`. Text times are read as Eastern local time. Columns named `*utc*` and epoch numbers are read as UTC. Use `--tz UTC` to override.

## 1. Ingest (one command per kind; pass every file of a kind in one call, because a later call overwrites that kind's outputs)

```
python proto/massdot_import.py ingest waze_export.csv            --kind waze
python proto/massdot_import.py ingest HOC_flood_log.xlsx         --kind closures
python proto/massdot_import.py ingest RepeatingFloodAreas.gdb    --kind rfa
python proto/massdot_import.py ingest D3_Drainage.gdb            --kind drains
python proto/massdot_import.py ingest https://…/FeatureServer/3  --kind rfa      # an ArcGIS feature layer URL works too
```

| kind | writes | used by |
|---|---|---|
| waze | `proto/data/waze_<storm>.csv` (label schema plus tier, n_reports, uuids, thumbs, reliability); `proto/data/massdot/waze_negcand_<storm>.csv` | `score` (SCORE_WAZE=1) |
| closures | `proto/data/massdot_closure_<storm>.csv` | `score` (SCORE_MASSDOT=1) |
| rfa | `proto/data/massdot/rfa_points.csv`, `rfa_segments.csv` (dist_rfa_m, n_rfa_250m / 1km, rfa_closure, rfa_dated_incidents per segment); dated incidents go to `proto/data/massdot_rfa_<storm>.csv` | learned-model feature (inside LOSO only), validation check |
| drains | `proto/data/massdot/inlets_segments.csv` (n_inlets / culverts / manholes / outfalls, inlets_per_100m, q_inlet_m3s, n_in_pluvial, n_flood_known per segment) | table for `lf_drains.py` / `pluvial_v2.py` (no model change) |

Every run writes `docs/proto/massdot/ingest_<kind>.md` and `.json`. These hold the mapping used, dropped rows by reason, the dedupe counts, rows per storm and per
tier, the locked-storm drop count, and unmatched rows. For RFA they also hold the validation check: the share of RFA segments in each run's top 3 %, the lift, and how the layer compares with the 38 known
sites. `docs/proto/massdot/candidate_storms_<kind>.json` lists local days with at least `--min-alerts` (default 5) rows that match no catalogue storm, each with a
suggested 20 km box. Add those days through `proto/obs_catalog.py` before scoring them.

**Rules fixed before any MassDOT row existed (28 Oct 2026).**

- **Assignment.** A row belongs to every storm in `catalog.json` or `catalog_d456.json` whose window contains it and whose box, padded by 2 km, contains it. The window runs from t0 − 6 h to t0 + hours + 12 h.
- **Locked storms.** Rows that fall in the locked storms (aug2015, aug2018, aug2020, jul2018, oct2016) are counted and dropped. Nothing is written for them.
- **Dedupe.** Rows with the same uuid or incident id are one row. After that, rows within 150 m and 2 h of a kept row are merged into it.
- **Waze tiers.** A Waze row is `corroborated` (1.0) when it has nThumbsUp ≥ 2, reliability ≥ 8, or ≥ 2 merged uuids. Otherwise it is `reported` (0.6).
- **Closure tiers.** A closure with a flood cause is `confirmed_closure`. A flood cause plus an observation on the road (impassable, stuck, depth, washout) is
  `confirmed_inundation`. Any other flood-cause incident is `reported`. Rows with no flood cause are dropped. Waze construction and event closures are dropped.
- **Negative candidates.** 'Not there' alerts and alerts removed early (under 20 min, no thumbs, not high reliability) go only to `waze_negcand_*`. They are never scored
  and never become negatives.
- **Rows without coordinates.** These are kept with `coord_quality=none`, so they are never matched. A `proto/label_geocode.py` query file is written for them.

## 2. Score (same day)

```
python proto/massdot_import.py score                 # storms with new files: before / after (sites, hits and recall at 3 %, rule hits)
python proto/massdot_import.py score --pool          # + every held-out-23 storm, pooled before / after (~3 min)
SCORE_TIERS=1 python proto/massdot_import.py score   # + weighted recall with the tiers above
```

This calls `proto/score_v2.py` unchanged. A runtime hook adds the new files to `label_files` and to `label_tiers` (families `Waze`, `MassDOT_closure` and
`MassDOT_RFA`), and no shared file is edited. The result goes to `docs/proto/massdot/score_massdot.json`. This is a **secondary label analysis**, not a model
`--compare`. PROTOCOL.md §1 applies: a label change re-scores the baseline and the candidate on the same files. Storms without a published run are listed and
not scored.

## 3. Before committing

- **Sharing terms.** Check the terms MassDOT attaches. Waze data comes under the Waze for Cities agreement. Label rows (points, times) are needed for scoring. Raw
  exports and drainage points are never written by the importer, and the drains table is per-segment aggregates only. If the terms forbid publishing points, keep
  `proto/data/waze_*.csv` and `massdot_*` out of git and score locally.
- **Commit size.** Commit the outputs and reports in **one** commit. Every push to main redeploys the public site.
- **Making it permanent.** To have `label_tiers.py build` see the new families, add the three file patterns and families to its `source_files` and `family`. The hook
  in `massdot_import.install_hooks` shows the exact rules.
