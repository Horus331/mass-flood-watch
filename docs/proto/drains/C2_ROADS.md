# C2: storm-drain sink on built-up road cells: result (14 Nov 2026)

Pre-registration: `PREREG_C2_ROADS.md` (committed at 5963d0bdc before any run). Runs: GitHub Actions run 43535448793, 48 of 48 tasks
succeeded (no reruns). Scored by `python proto/inlets_eval.py --dir docs/proto/drains/c2_roads_v1` (2000 bootstrap replicates); full
tables in `c2_roads_v1/eval.md` (the script labels the candidate arm "inlets"/"LF_INLETS"; here that is C2).

## Verdict: NOT ADOPTED (fails conditions 1, 2 and 3)
| PROTOCOL v2 §5a condition | value | pass |
|---|---|---|
| 1. pooled site recall gain at 3 % >= +0.04 | -0.010 (98 sites) | no |
| 2. one-sided 5 % lower bound > 0 | -0.050 | no |
| 3. FSS 300 m at 3 % does not drop | -0.0023 | no |
| 4. no storm with >= 3 sites loses > 1 site at 3 % | worst -1 | yes |
| 5. rule lift >= 0.8 x base | 5.99 vs 7.19 (0.83) | yes |

Held-out pooled: site recall at 3 % 0.194 → 0.184; at the live rule 0.071 → 0.051 (7 → 5 sites hit); flagged share at the rule
0.0033 → 0.0029. **Failure-mode check:** rule-flagged segments −15 %, rule-hit sites −29 % (ratio 1.88): C2 removes documented sites
faster than it removes flags, the same pattern as the generic drains (`DRAINS.md`) and the inlet sink (`INLETS.md`).
Calibration storm (sep2023, report only): Leominster city rule hits 28 → 28, flags 50 → 48.

## Sink totals (C2 arm)
Built-up road cells per box: 290 (Hubbardston) to 21,851 (Shrewsbury) of 35,722–134,743 road cells; 25 mm/h; 0.8–60.7 m³/s per box.

## 13 Nov storm
Replay on radar rain with the live closure rules, with and without C2: 0 segments p ≥ 0.5 either way (nothing was reported flooded),
so C2 neither adds nor removes a false alarm there (`../prospective/storm_2026-11-13_results.md`).

## Reading
Three drain sinks in a row (generic, inlet-located, built-up roads at 25 mm/h) lower recall of the documented flood sites. The
documented sites are the places where drains were overwhelmed or blocked; a sink sized to normal capacity removes exactly that water.
A fourth sink variant is not planned. The live forecast is unchanged.
