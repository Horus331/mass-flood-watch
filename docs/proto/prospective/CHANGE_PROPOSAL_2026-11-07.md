# Proposed changes after the 6 Nov 2026 storm (pre-registered, not adopted)

Written 7 Nov 2026 before any of these were tested. None changes the live forecast until it passes the tests below and Mo and the
advisors approve it. Evidence: `storm_2026-11-06_watch.md`, sections of 7 Nov.

## P1. Closure needs water the storm added ("rise rule")

**Problem.** In the radar-driven rerun of box b4, 8 of the 11 closed segments reach 30 cm within 0.5 h, before the storm's rain: the water
was already beside the road at the start of the run (streams, ponds). The same roads appear in the forecasts (for example the Route 290 /
Solomon Pond Road ramps, "up to 27 cm at Fri 5:00 AM", the first frame).

**Change.** A segment counts as closed only where depth >= 30 cm AND depth minus its depth at rain onset >= 30 cm, at the same frame.
(v2 already measures depth from rain onset in the probability; this applies the same to the closure rule and to the k-of-8 count.)
Note 7 Nov 23:30Z: the forecast count already drops segments at >= 30 cm at onset; on the b4 radar run that removes 1 of 11. The other 10
are below 30 cm at onset and reach it within about 0.5 h, so the test must look at the rise, not only at the onset depth.

**Test.** All archived storms with labels (`docs/proto/forecast/ensemble.json` storms and the 23 district T2 storms): site recall (score_v2)
and flagged share, current rule vs rise rule. Adopt only if pooled recall does not drop by more than 1 site and flagged share falls.

### P1 test result, 8 Nov 2026 (`proto/p1_rise_test.py`, `p1_rise_test.json`)

Scored with `score_v2.py` on the published labelled runs; alert tier = p_close >= 0.5. R0 published, RA = R0 and < 30 cm at rain onset
(the live k-of-8 rule), RB = RA and a rise >= 30 cm above the onset depth (P1). Site hits / sites, flagged segments, mean flagged share:

| pool | runs | R0 | RA | RB |
| --- | --- | --- | --- | --- |
| held-out 7 | parity catalog (clean baseline, the live model's base) | 8 / 40, 398, 0.91 % | 8 / 40, 386, 0.89 % | **8 / 40, 251, 0.56 %** |
| new 16 | parity catalog | 1 / 58, 188, 0.23 % | 1 / 58, 180, 0.22 % | **1 / 58, 108, 0.14 %** |
| dev 2 (in-sample) | parity catalog | 31 / 91, 193, 1.63 % | 31 / 91, 190 | 31 / 91, 154, 1.31 % |
| held-out 7 | older Turing runs (pre-parity model) | 12 / 40, 845, 2.01 % | 12 / 40, 791 | 10 / 40, 423, 0.97 % (aug2026 -1, sep2021 -1) |
| dev 2 | older Turing runs | 34 / 91, 312 | 31 / 91, 294 (sep2023 -3) | 31 / 91, 221 |

Pre-registered rule (pooled recall drops by at most 1 site and flagged share falls): **passes on the parity catalog** (no site lost in any
pool, 37 % to 42 % fewer flagged segments out of sample); fails on the older Turing runs (2 held-out sites lost). Not adopted: the parity
runs are the baseline model without terrain fix T2 and without depth-from-onset; the test must be repeated on T2 + onset runs (the live
model) before a decision, and the decision is Mo's and the advisors'.

#### Repeat on terrain-fix (T2) runs, 8 Nov 2026 (Turing job `p1test_t2c`, `p1_rise_test_t2.json`)

The 9 labelled T2 site runs kept on Turing (`results/site_*_t2`; T2 terrain, depth not yet measured from rain onset):

| pool | R0 published | RA not standing at onset | RB rise >= 30 cm (P1) |
| --- | --- | --- | --- |
| held-out (aug2023, aug2026, jul2023, jun2020, sep2021, sep2022: 33 sites) | 4 hits, 215 flagged, 0.66 % | 4, 203, 0.63 % | **4, 112, 0.34 %** |
| new (sep2018 Fitchburg, sep2018 Milford: 15 sites) | 1, 42, 0.34 % | 1, 42 | **1, 34, 0.28 %** |
| dev (sep2023 Leominster district box: 80 sites) | 28, 242, 0.54 % | 28, 232 | **28, 124, 0.27 %** |

Per storm, P1 removes flags without losing a hit: aug2023 96 -> 24, sep2023 242 -> 124, sep2021 104 -> 81, jun2020 20 -> 15,
sep2022 11 -> 7, sep2018 Milford 13 -> 10, aug2026 4 -> 0 (0 hits either way), jul2023 0, sep2018 Fitchburg 9 -> 9.

**Verdict under the pre-registered rule: passes on T2 runs as well** (0 sites lost in every pool; flagged roads down 48 % held-out,
19 % new, 49 % dev). Together with the parity-catalogue result, P1 is ready for Mo and the advisors to decide. Still open before switching
it on: the live model also measures depth from rain onset (`PROTO_RES_CONSISTENT`), not in these runs; and the 6 Nov storm shows what it
would change live (b4 Clinton/Berlin: most of its 10 radar closures rise to 30 cm within 0.5 h of onset, so P1's effect there needs the
frame-level check, not assumed).

## P2. Rain agreement before "likely" (location-agreement check)

**Problem.** Most "likely" roads in this storm were closed by exactly 2 of 8 members, and the place of the heavy rain moved every cycle.
A stricter k (3 of 8) costs 2 of 29 past sites at long lead (7 Nov analysis), so k alone is not the fix.

**Change.** "Likely" requires k >= 2 AND at least 3 of the 8 members put >= 70 % of the box's heaviest 3 h rain within 10 km of the road.
Otherwise the road is shown as "possible".

**Test.** Needs each member's rain per cycle. Step 1 (safe, no model change; in place from 7 Nov): each member writes `rain_km.json`
(storm total and wettest 3 h, 1 km grid, from rainstats.npz) and the ensemble step keeps them in `kofn_meta.json` of the storm archive. Step 2: evaluate on this storm and on hindcasts of the 7 out-of-sample storms. Adopt only if no past site is lost.

## P3. Radar boxes follow the forecasts (done, operations only)

The storm archive's radar reruns used the first 4 forecast boxes; the Worcester box of the 6 Nov 06Z forecast (22 likely) had no rerun.
Cap raised to 8 on 7 Nov. Further proposal: choose boxes by the number of likely closures they held in any cycle, not first come.

## P4. Worcester hot spots: get evidence before changing the model

East Park Terrace, Shrewsbury Street, Cambridge Street and Fantasia Drive close in the model with 66 mm over 48 h and 16 mm in the worst
hour. No report this storm. Before any model change: request Worcester DPW / 311 street-flooding records for these streets, and check
MassDOT cameras near Shrewsbury Street during the next storm. If they do flood, keep them; if not, they become the test set for a
drainage term (the earlier drain experiments are in `docs/proto/drains`).
