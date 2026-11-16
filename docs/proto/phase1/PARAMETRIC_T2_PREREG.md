# Leominster culvert blockage on the deployed (T2) terrain: pre-registration (16 Nov 2026)

Follows `PARAMETRIC.md` §3.5 and §5. Committed before any run. Results go to `PARAMETRIC_T2.md` and `parametric_t2.json` whatever they are.

**Why.** In the first parametric study (pre-T2 terrain, as pre-registered), blocking culverts *removed* closures: 39 of the 42 segments
that stopped closing under full blockage lie within 60 m of a crossing. Stream water held in the crossing notch was counted as road
water, and filling the notch removed it. The live model now runs the corrected terrain (T2: `LF_NOTCH_FIX=1 LF_CHAN_ENFORCE=1`,
`docs/proto/terrain/TERRAIN.md`), and the what-if explorer reads roads near culverts against the road crest (`whatif/BLOCKED_V3.md`).
This rerun asks whether blockage can now be read from closures, and redoes the culvert priority list on the deployed terrain.

**What this is.** One factor (culvert blockage) on the calibration storm (Leominster, 11–12 Sep 2023). In-sample by design: a
sensitivity study, not a skill claim. No scenario becomes a default, and nothing here changes the live site or forecast.

## Runs (5, GitHub Actions CPU, `parity_test.yml`, dest `docs/proto/phase1/parametric_t2`)
All as the first study's base (catalogue box `162000,908000,182000,928000`, 36 h, 20 m, MRMS Pass2 rain, `LF_PARITY=1`, `LF_LOSS=cn`,
AMC II × 0.88, `LF_INFIL_MMH=2`, `LF_QOUT=1`, `LF_VOUT=1`, `PROTO_CASCADE=1`) **plus `LF_NOTCH_FIX=1 LF_CHAN_ENFORCE=1`**, and
`PM_KEEP_Z=1` (saves the ground grids for the crest readout, `proto/crest_pack.py`; no effect on the model).

| id | blockage | same as |
|---|---|---|
| `t2_base` | none | `pm_base` + T2 |
| `t2_c20`, `t2_c50`, `t2_c100` | every culvert in the box, `LF_XINGS_PARTIAL` = 0.2 / 0.5 / 1.0 (bridges stay open) | `pm_c20/50/100` + T2 |
| `t2_ct` | smallest-capacity third of the NAACC-sized culverts at 100 % | `pm_ct` + T2 |

Blocked notches are protected from channel enforcement and depression breaching (`partial_block` → `XPROT`, already in the code), so
no carved path replaces a blocked opening. A technical failure is rerun unchanged; no run is dropped after a result is seen.

## What is reported (`proto/parametric_eval.py` with `PM_SET=t2`, plus the crest readout)
1. The first study's table for the 5 runs: segments closed (p ≥ 0.5, the deployed readout), storm reports (of 89) and DPW points (of 54)
   matched (same matching file as before), newly closed with no report within 150 m, base DPW misses now hit, Wachusett St, Hamilton St,
   residents losing access.
2. **Notch-artifact check:** of the segments closed in `t2_base` but not in `t2_c100`, how many lie within 60 m of a crossing, and their
   median peak depth in both runs (pre-T2: 39 of 42, 0.44 → 0.13 m).
3. **Crest readout** (`whatif_v3` definitions, unchanged): segments within 60 m of a crossing whose second-highest water surface over the
   lidar road crest is ≥ 0.30 m, open vs each blocked run; crossings overtopped (pool within 40 m above the crest within 20 m); median pool
   rise at crossings wet in both runs.
4. **Culvert priority list** (same method as `PARAMETRIC.md` §4, from `t2_c100` and `t2_ct` vs `t2_base`), top 10, and its overlap with
   the pre-T2 list. Route 2 / Dewey St (pre-T2 #1) is flagged for a check: the T2 study found an 8.5 m chained-notch pit on Route 2 at the
   I-190 interchange (`terrain/TERRAIN.md`).

## Reading rules (fixed now)
- **Blockage is readable from closures on T2** if, at 100 % blockage, (a) the closed count is ≥ `t2_base`'s, and (b) fewer than half of
  the segments that stop closing lie within 60 m of a crossing. Otherwise the deployed readout still mixes notch water into road depth,
  and blockage is reported only through the crest readout and the pool rise.
- **Crest readout works on T2** if closures near crossings (crest-relative) are blocked ≥ open in all 4 blocked runs, and the median
  pool rise is ≥ 0 in all 4.
- Same rules as the first study for the DPW misses: a scenario "matters" if it turns ≥ 3 of the `t2_base` misses into hits; no Wachusett
  St hit → the missing piece is erosion / washout. A scenario that gains matches but closes many unreported roads is not called better.
- The priority list stays "model-based candidates"; a crossing counts as robust only if it is in both the pre-T2 and T2 top 10.

**Cost.** 5 runs, ~35–60 min each on free GitHub runners (about 4 runner-hours).
