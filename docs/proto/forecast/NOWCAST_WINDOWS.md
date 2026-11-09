# Radar nowcast in the first hours, and chance by time window: results

Pre-registration: `NOWCAST_WINDOWS_PREREG.md` (9 Nov 2026). Part A (rain) checks 1-2: `proto/nowcast_hindcast.py`, workflow
`nowcast_hindcast.yml` (run 42663558101), raw output `nowcast_hindcast.json`.

## A. Rain, checks 1-2 (9 Nov 2026): pass

44 issue times (every 3 h through the storm) on the 6 non-locked catalogue storms with MRMS on AWS (aug2023, aug2026, jul2023, sep2021,
sep2022, sep2023), each storm's catalogue box, MRMS Pass2 hourly as truth, HRRR = the cycle 1 h before issue.

| | HRRR | blend (radar hour 1, half hour 2, HRRR from hour 3) | threshold | |
|---|---|---|---|---|
| box-mean hourly error, hours 1-3 | 2.41 mm | 1.99 mm (x0.83) | ≤ 0.85 x HRRR | pass |
| cycles where the blend is worse, hours 1-3 | | 27 % | ≤ 1/3 | pass |
| 1 km error, hours 1-3 (reported) | 2.93 mm | 2.42 mm | | |
| box-mean error, hours 4-6 | 2.30 mm | 2.30 mm | within ±5 % | pass |

In the heaviest hours HRRR often had little rain where the radar already showed it (aug2023, 13Z: 20 mm fell in the next hour; radar
extrapolation gave 11 mm, HRRR 0.5 mm).

## A. Flood outcome, check 3 (9 Nov 2026): pass -> adopted

Amendment 1 design (one member per issue time; `proto/nowcast_flood.py`, workflow `nowcast_flood.yml` run 42670155765, 51 runs, all
succeeded; raw `nowcast_flood.json`). 17 issue times with at least 3 mm observed in hours 1-3; truth = the radar-rain run of the same box
and window; closures = p_close >= 0.5 with the P1 rise rule.

| pooled over 17 issue times | HRRR | blend |
|---|---|---|
| closures matching the radar run (TP) | 269 | 260 |
| closures the radar run did not have (FP) | 290 | 231 |
| radar-run closures missed (FN) | 240 | 249 |
| F1 | 0.504 | **0.520** (pass: ≥ 0.484) |

The blend mostly removes false closures (290 -> 231) at nearly the same hits; on single issue times it can swing either way (aug2023 13Z:
3 -> 13 of 15; sep2021 21Z: 42 -> 26 of 84; aug2026 07Z: 7 -> 0 of 34), so the gain is modest and pooled.

**Adopted 9 Nov 2026** (checks 1-3 passed): the issue cycle's member of the live forecast runs with `LF_NOWCAST=1` (forecast.yml); the
older 7 members stay pure HRRR (and cached), as tested. Part B (time windows) is still to be run.
