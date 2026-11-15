# Leominster parametric study: results (15 Nov 2026)

Pre-registration: `PARAMETRIC_PREREG.md` (committed before any run). Readout: `proto/parametric_eval.py` → `parametric.json`.
Figure: `fig/parametric.png` (`proto/parametric_figure.py`). Runs: GitHub Actions run 43713215284, 10 of 10 succeeded.

**What this is.** One condition changed at a time on the calibration storm (Leominster, 11–12 Sep 2023), 20 m, MRMS radar rain.
In-sample by design: it shows what each condition does to the modelled flood and closures. It is not a skill test, and no scenario
becomes the default.

## 1. Base check
The rerun reproduces the published base exactly: 35 of 89 storm reports and 21 of 54 City DPW damage points (`cycles/LEOMINSTER_COUNTS.md`).
98 of 4,542 segments in the box are closed (2.2 %).

## 2. Results

| Scenario | Segments closed | Storm reports matched (of 89) | DPW points matched (of 54) | Newly closed, no report within 150 m | Base DPW misses now hit (of 33) | Residents losing access to any service (peak) |
|---|---|---|---|---|---|---|
| Base (AMC II × 0.88, culverts open) | 98 | 35 | 21 | — | — | 35,108 |
| Dry soil (AMC I) | 47 | 28 | 21 | 0 | 0 | 26,038 |
| Wet soil (AMC III) | 145 | 39 | 21 | 41 | 0 | 45,034 |
| Calibration factor removed (× 1.00) | 147 | 37 | 21 | 45 | 0 | 44,573 |
| Frozen ground (Knisel CN 95/98, no soak-in) | 224 | 40 | 22 | 111 | 1 | 55,295 |
| All culverts 20 % blocked | 94 | 33 | 20 | 11 | 0 | 34,189 |
| All culverts 50 % blocked | 84 | 26 | 15 | 15 | 0 | 32,709 |
| All culverts 100 % blocked | 93 | 21 | 8 | 27 | 0 | 32,250 |
| Smallest third of culverts 100 % blocked | 111 | 35 | 21 | 13 | 0 | 35,236 |
| 50 % blocked + wet soil | 116 | 34 | 19 | 28 | 0 | 41,989 |

Chance recall at the same share of segments closed is 0.02–0.08 for every row (`parametric.json`, `reports_chance`, `dpw_chance`).

## 3. Readings (rules fixed in the pre-registration)

1. **No factor matters for the DPW misses.** The bar was ≥ 3 of the 33 base misses turned into hits. The best is frozen ground with 1
   (a crossing miss), at the cost of 111 newly closed roads with no report nearby.
2. **No scenario reaches a Wachusett St miss** (25 of the 33 misses). By the pre-registered rule, the missing piece is an erosion /
   washout mechanism, not an input.
3. **Hamilton St** (railroad-embankment debris closure) is not reached by any scenario; the deepest is 22 cm (frozen ground).
4. **Ground wetness is the strongest factor.** Wet soil and removing the calibration factor both add about 50 closed segments and
   4 or 2 storm reports, with no DPW gain; 41 and 45 of the new closures have no report nearby. Dry soil halves the closed segments
   and loses 7 storm reports. AMC III is the physically expected state for Sept 2023, and it over-floods relative to the reports, so by
   the pre-registered reading the × 0.88 factor stands in for something the model lacks (storm-drain capacity, soak-in of standing
   water); it is not evidence that the soil was dry.
5. **Culvert blockage cannot be read from closure counts on this base.** Blocking removes closures instead of adding them: 39 of the
   42 segments that stop closing under full blockage lie within 60 m of a crossing, and their median peak depth falls from 0.44 m to
   0.13 m (13 of 15 at 20 %, 28 of 31 at 50 %). The base uses the pre-T2 terrain, as pre-registered, where water held in the crossing
   notch counts as road water; filling the notch removes that water. The same artifact was found and fixed for the what-if explorer
   (`whatif/BLOCKED_V3.md`). The pool-rise readout behind the culvert priority list (§4) is not affected.
6. **Targeted blockage** (smallest third of surveyed culverts) adds 13 closures, all without a report nearby, and changes no match.

## 4. Culvert priority list (model-based candidates)
Crossings whose full blockage closes the most extra road segments within 300 m, with the rise of the pool behind them. Duplicate
records of the same crossing are merged. Needs NAACC / MassDOT condition data to confirm.

| # | Crossing (stream) | NAACC condition | Roads that close only when blocked | Pool rise |
|---|---|---|---|---|
| 1 | Route 2 / Dewey St | OK | Route 2, ramp from South St to Route 2 WB (7 segments) | +0.7 m |
| 2 | Meadow Pond Dr | no data | Meadowbrook Acres (4) | +2.5 m |
| 3 | Commercial St / Putnam St (North Nashua River) | Poor (Commercial St) | Boulder Dr, Putnam St (3) | +2.1 to +3.8 m |
| 4 | Columbia Ave / Dewey St (0.46 m pipe) | OK | Columbia Ave, Dewey St, Minneapolis Ave (3) | +1.5 m |
| 5 | Tisdale St / Manchester St | no data | Sylvan Ave, Sylvan Terr, Tisdale St (3) | +1.4 m |
| 6 | Bathrick Rd | OK | Bathrick Rd (1) | +2.1 m |
| 7 | Justice Hill Rd (Rocky Brook) | OK | Justice Hill Rd (1) | +1.1 m |
| 8 | Beaman Rd (Wilder Brook) | Poor | Tanglewood Rd (1) | +0.7 m |
| 9 | Pierce Ave | OK | Harvard Ave (1) | +0.6 m |
| 10 | Olin Ave | OK | Route 2 (1) | +0.4 m |

Rows 1 and 6–10 come from the targeted run (`pm_ct`), rows 2–5 from full blockage (`pm_c100`). 103 of the 470 crossings blocked in
`pm_c100` close at least one extra segment within 300 m.

## 5. Next step
Rerun the blockage scenarios on the deployed T2 terrain (`LF_NOTCH_FIX=1 LF_CHAN_ENFORCE=1`), with the crest-relative road readout,
as a new pre-registration, so that blockage can be read from closures.
