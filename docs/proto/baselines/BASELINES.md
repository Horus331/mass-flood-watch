# Baseline layers for the v3 benchmark (PROTOCOL_v3.md, Phase 0.2)

Status of each named baseline. All six scored on Test 1 (D3) and Test 2 (D4–6) on 10–11 Nov: `../scoring/BENCHMARK_v3.md`.

| id | baseline | status | file |
|---|---|---|---|
| B1 | NWS flash-flood warning polygons (VTEC FF.W, WFO BOX), IEM storm-based-warning archive | fetched 9 Nov 2026 for all 107 unlocked catalogue storms (26 D3, 81 D4–6), 0 failures | `nws_ffw.json` |
| B2 | FEMA NFHL 100-yr zone | exists (`static/STATIC.md`, `static/HYBRID.md`); to be re-scored under v3 rules | `../static/static_flags.json` |
| B3 | MassDOT repeating flood points | scored (38 D3 points, undated) | `proto/data/massdot_repeat_flood_d3.csv` |
| B4 | radar rain threshold (I60 / storm total, MRMS; amendment 1) | scored; tuned on Leominster: I60 ≥ 85 mm | run features |
| B5 | HAND from the model's 20 m terrain | scored; tuned H* = 0 m | run features |
| B6 | static H×V×C | scored (amendment 1) | run features + SFHA |

## B1 notes

- Query: IEM `api/1/vtec/sbw_interval.geojson`, WFO BOX, storm window [t0, t0 + hours] of the catalogue; polygons kept unsimplified with their valid times.
- Storms with at least one FF.W polygon anywhere in the BOX area during the window: 20 of 26 in D3, 50 of 81 in D4–6. Whether a polygon
  covers the storm's box is decided at scoring (segment midpoint inside a polygon), not here.
- By year (storms with a warning / storms): 2014 1/1, 2018 17/30, 2019 6/15, 2020 6/11, 2021 9/14, 2022 3/5, 2023 23/25, 2025 1/1, 2026 4/5.
