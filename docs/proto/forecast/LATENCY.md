# Forecast latency: where the time goes (14 Nov 2026)

Measured on the cycles of 12–14 Nov (GitHub Actions `forecast.yml`, 4-core runners).

| step | time | note |
|---|---|---|
| HRRR 48 h cycle on AWS | ~1 h 45 min after issue | fixed by NOAA; the workflow waits for it |
| gate + rain timeline | a few minutes | |
| flood solve, issue member (66 h = 12 h spin-up + 48 h + 6 h drain) | 1 h 20 – 1 h 35 min | 1000 × 1000 cells at 20 m, 302 % CPU: the runner is already saturated |
| closure step | 0–2 min | was 7–19 min before `resilience --no-eff` (12 Nov) |
| publish | minutes | older members are cached, so only the issue member runs each cycle |

So a cycle publishes about **3.5–4 h after its issue time**, about 2 h of it ours, and the solve is ~80 % of that.

## Options for the solve, and why none is taken now
1. **Default time step instead of ≤ 1 s** (`LF_PARITY`): about 2 × faster (`parity/PARITY.md` §2.5: 18 vs 35 min on sep2023), flags almost the
   same (Jaccard 0.96), but the recession oscillates and gauges get worse (Fitchburg 1.63 m at 10:30Z vs 1.10 m at 01:30Z, observed 1.00 m at 01:15Z).
   It would undo the parity baseline every result since 25 Oct rests on.
2. **Trim dry hours** (end the run 6 h after the last forecast rain instead of at the horizon + 6 h): saves time only when the rain ends
   early, i.e. not in the storms that matter; it changes the frame count every downstream step reads.
3. **Issue member on Turing GPU** (the District 3 shadow run already goes there): minutes of solve, but the queue wait is not bounded.
4. **Larger runners**: paid.

None is worth its cost while the forecast horizon is 48 h and the issue member already uses radar for its first hours
(`NOWCAST_WINDOWS.md`). Revisit if a flooding storm shows the 4 h delay mattering.
