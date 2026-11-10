# Forecast member rain: neighbourhood percentile, judged on road closures: result (10 Nov 2026)

Pre-registration: `BOX_PERCENTILE_PREREG.md` (9 Nov). Run: GitHub Actions 42711430835, all 17 issue times complete. Raw: `box_percentile.json`.

| arm | true closures | false closures | missed | F1 | rain vs radar (box, 12 h) |
|---|---|---|---|---|---|
| p90 (live, 20,90) | 269 | 290 | 240 | **0.504** | 0.95 x |
| p80 (20,80) | 160 | 55 | 349 | 0.442 | 0.67 x |
| raw (no neighbourhood) | 109 | 45 | 400 | 0.329 | 0.50 x |

**Decision (as pre-registered): the live setting 20,90 stays.** Neither other arm reached F1(p90) + 0.02.

What it means: the live percentile is the only arm that gets the rain volume about right inside the storm box (0.95 x). The lower percentiles
cut false closures by about 5 x but miss many more real ones, because they carry a half to two-thirds of the radar's rain. The false alarms
are therefore not mainly a rain-volume problem inside the box; the trade-off between false and missed closures should be handled by how
members are counted (k of 8) and by calibration, not by shrinking the rain.
