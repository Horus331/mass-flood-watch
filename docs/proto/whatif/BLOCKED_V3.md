# Blocked culverts, version 3: result (13 Nov 2026)

Pre-registration: `PREREG_BLOCKED_V3.md` (committed before any number). Turing job `whatif_v3a`, CPU, the existing open / blocked solves.
Raw: `blocked_v3.json` (`proto/whatif_v3.py`). Diagnostic that led here: `diag_*.json` (`proto/whatif_diag.py`).

| check | needed | result |
|---|---|---|
| 1 closures near blocked crossings (crest-relative), blocked ≥ open | ≥ 9 of 12 pairs | **12 of 12** |
| 2 pool behind blocked crossings, median blocked − open ≥ 0 | ≥ 9 of 12 pairs | **12 of 12** |

**Decision: adopted.** In the what-if explorer, the culvert switch is now read against the road surface near crossings, and the value of
maintenance below is reported. The live forecast is not changed (there the notch depth is the deliberate culvert-failure proxy).

| rain_ground | closed near crossings, open → blocked | crossings overtopped, open → blocked | crossings wet in both | median pool rise | share of those with a higher pool |
|---|---|---|---|---|---|
| r050_dry | 0 → 1 | 0 → 6 | 204 | +1.62 | 100% |
| r050_wet | 0 → 2 | 1 → 9 | 281 | +1.54 | 98% |
| r075_dry | 0 → 2 | 1 → 9 | 275 | +1.53 | 97% |
| r075_frozen | 2 → 6 | 3 → 20 | 463 | +1.69 | 99% |
| r075_normal | 1 → 3 | 1 → 10 | 326 | +1.52 | 98% |
| r075_wet | 2 → 4 | 2 → 11 | 390 | +1.48 | 95% |
| r100_frozen | 2 → 16 | 7 → 37 | 502 | +1.43 | 96% |
| r100_normal | 2 → 4 | 2 → 14 | 403 | +1.48 | 96% |
| r100_wet | 2 → 6 | 4 → 17 | 447 | +1.42 | 97% |
| r125_dry | 2 → 4 | 3 → 13 | 378 | +1.44 | 95% |
| r125_normal | 2 → 9 | 5 → 17 | 448 | +1.45 | 97% |
| r125_wet | 2 → 10 | 6 → 26 | 471 | +1.39 | 96% |

The check-2 median in the summary file is 1.0 in several pairs because crossings wet in only one run count as ±1 m (pre-registered,
sign only); the columns above use only crossings wet in both runs: the pool behind a blocked crossing stands about 1.4–1.7 m higher,
at 95–100 % of them.

**Value of maintenance (Leominster / Fitchburg, Sept 2023 storm, 542 assessed crossings):** with all culverts clear, 0–2 road segments
near crossings close; with all blocked, 1–16 (most with frozen or saturated ground and more rain), and 6–37 crossings are overtopped
instead of 0–7. Every segment closed with the culverts open is also closed with them blocked, so the difference is added closures, not
a reshuffle. Not measured: run-to-run churn (no repeated open runs exist). Limits: "blocked" means every mapped culvert fully blocked
at once (an upper bound); the closure threshold is 30 cm over the lidar road surface; one storm, one area.

Why version 2 failed: in the open run, stream water standing in the notch cut through the road (median 2.3 m deep) was read as water on
the road; blocking removed the notch and with it that reading, so blocked runs looked drier (27 of 27 open-only closures).

**In the explorer:** the "culverts overtopped" tile now uses this reading (water surface on the low side above the road crest) for clear
and blocked culverts alike, wherever a version-3 number exists (the 12 rain × ground pairs above); elsewhere the old count stays. With
blocked culverts the road and people totals are shown without a comparison to the clear run, because away from the culverts they move
with small terrain changes (paired overlap Jaccard 0.0–0.45); the near-culvert numbers are in the note under the tiles.
