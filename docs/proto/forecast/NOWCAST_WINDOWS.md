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

Check 3 (flood outcome with the blended rain against the radar-rain run) comes next: it needs the blend inside the forecast member rain
(w9), then box runs for these cycles. Nothing changes on the live forecast before check 3 passes.
