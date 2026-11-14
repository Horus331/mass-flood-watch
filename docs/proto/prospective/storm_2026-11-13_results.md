# Storm of 12–13 Nov 2026: results (prospective record)

Running log: `storm_2026-11-13_watch.md` (candidates fixed 12 Nov, before the storm). This file is the summary after the rain.

## What happened
- Rain 12 Nov 19Z – 13 Nov ~17Z over the D3 forecast box (Uxbridge area, 176000,859000–196000,879000 EPSG:26986).
- **19.9 mm box mean** (MRMS RadarOnly). Peak hour 2.2 mm box mean; wettest cell-hour 10.9 mm. A long, light rain, well below flooding intensity.
- Snow on at most 14 % of precipitating pixels (14Z, the hills); none after 17Z.
- **Reports:** no MassDOT water events, no NWS flood alerts, no LSR flood reports (checked by every cycle's storm_archive report); sentinel QUIET except one WATCH hour (05Z).

## Forecast
- Every published cycle (12 Nov 12Z – 13 Nov 12Z) said **"no road closures in 48 h"**, which matches the reports.
- **Rain error by lead (HRRR, summed over the 25 storm hours, vs 19.9 mm observed):** 1 h 13.2 mm, 2 h 9.2 mm, 3–6 h 12.5–13.0 mm.
  So about **35 % too little at every lead** (46 % at 2 h). The bias flipped to slightly too much while the rain eased (08–12Z), then back to about 1.5× too little in the light rain of 13–16Z.
- On this storm the rain error did not change the answer: even the observed rain did not close a road in the model (replay below).

## Replay on radar rain (same box, T0 12 Nov 18Z, 36 h, live physics)
| case | closure rules | segments p ≥ 0.5 | summed p (expected closures, 2,600 segments) |
|---|---|---|---|
| `nov13_replay_live` | start-up water **not** subtracted (replay set-up error) | 2 | 6.0 |
| `nov13_replay_phase` | same, with rain/snow split | 2 | 6.0 |
| `nov13_replay_c2` | same, with C2 drains | 2 | 6.0 |
| **`nov13_replay_live2`** | **live rules** (`PROTO_RES_CONSISTENT=1`, `PROTO_RC_START_H=rain`) | **0** | 4.1 |
| `nov13_replay_c2_2` | live rules + C2 drains | 0 | 4.1 |

- The first replay flagged Rogerson Crossing (Uxbridge, p 0.95) and Gilboa Street (Douglas, p 0.5). Both read 15–40 cm from 0.5 h in, before any meaningful rain. That is stream water standing in the culvert notch and baseflow at the crossing, not flooding.
- The live forecast subtracts water that is there before the rain starts. The replay workflow did not pass that setting to the closure step (fixed: `parity_test.yml` now exports the case env). With the live rules, both flags are gone: **0 roads, which matches the reports.**
- Summed probability 4.1 against 0 reported closures: one storm, and small local roads are under-reported, so this is noted, not scored.

## Candidates fixed before the storm
- **C1, rain/snow split (`LF_PHASE`):** live from the 00Z cycle. Frozen share 0.0–0.2 % (lowest 2 m temperature 1.5–1.6 °C), so no effect on this storm; costs about 4 min per run.
- **C2, storm-drain sink on built-up road cells:** pre-registered in `docs/proto/drains/PREREG_C2_ROADS.md`; held-out test (23 storms × {base, C2}): **not adopted** (site recall at 3 % −0.010, lower bound −0.050, FSS down; `docs/proto/drains/C2_ROADS.md`). On this storm C2 changes nothing (no flags with or without it; 1,075 of 55,787 road cells drained, 2.99 m³/s).
- **C3:** dropped (see watch log).

## Faults found and fixed during the storm
1. **Gate rounding:** the 00Z cycle fired the gate on rounded rain but had no box. The test now uses unrounded values, with a fallback box on the wettest D3 point. The cycle was re-run by hand.
2. **Zenodo outage** (08:29Z run failed): the LISFLOOD-FP source zip is now cached in Actions.
3. **Latency:** the closure step went from 7–19 min to 0–2 min (`resilience --no-eff` on the issue member only). A cycle now takes about 1 h 45 min; the solver (about 1.5 h at 302 % CPU on 4 cores) is the next target.
4. **Replay set-up** (above): replays and benchmarks must use the live start-up subtraction, or culvert-notch water reads as road flooding.

## Lessons
- **HRRR runs low on long stratiform rain** (about 35 % here). For a flooding storm, that bias would matter. A bias-corrected or radar-blended rain for the first hours is worth a pre-registered test on past storms.
- **Notch water at crossings** reads as road depth unless start-up water is subtracted. The live forecast does this; any offline evaluation has to do it too.
