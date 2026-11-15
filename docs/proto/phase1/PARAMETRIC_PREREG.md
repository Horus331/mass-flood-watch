# Leominster parametric study: pre-registration (15 Nov 2026)

Advisor action items 12–13 (Nov 3, Prof. Tao): validate first, then change **one condition at a time** (clogged culverts, wetter soil,
frozen ground) and show each one's impact. Committed before any run. Results go to `PARAMETRIC.md` and `parametric.json` whatever they are.

**What this is.** A sensitivity study on the storm the model was calibrated on (Leominster, 11–12 Sep 2023). It is **in-sample by
design**: it shows what each condition does to the modelled flood and closures. It is **not a skill claim**, and no scenario becomes
the default ("no tuning"). Nothing here changes the live site or production settings.

## Base case
The frozen run behind the reconciled counts (`docs/proto/cycles/LEOMINSTER_COUNTS.md`): catalogue box `162000,908000,182000,928000`,
36 h from the catalogue t0, 20 m, `LF_PARITY=1`, `LF_LOSS=cn`, AMC II × 0.88, `LF_INFIL_MMH=2`, `LF_QOUT=1`, `LF_VOUT=1`, MRMS Pass2 radar
rain, the pre-T2 terrain (no `LF_NOTCH_FIX` / `LF_CHAN_ENFORCE`, as that run). Closures p_close ≥ 0.5 (`proto/prototype.py` defaults).
It is **rerun** in the same workflow as the scenarios (`parity_test.yml`, GitHub Actions CPU), so all ten runs share code and machine; the
rerun must reproduce the published base within one site (35/89 storm reports; 21/54 DPW points), else the difference is reported.

## Scenarios (one factor at a time from the base; 9 runs + base)
| id | factor | setting | source of the values |
|---|---|---|---|
| `pm_c20`, `pm_c50`, `pm_c100` | culvert blockage, every culvert in the box (bridges stay open: NBI, MassDOT bridge, span ≥ 6 m) | `LF_XINGS_PARTIAL` = 0.2 / 0.5 / 1.0 | ARR 2016 Book 6 Ch 6 (Weeks et al. 2013): design blockage 20 % for small inlets, 50 % for screened inlets, severe 100 % |
| `pm_ct` | targeted blockage: only the smallest-capacity third of the NAACC-sized culverts in the box (span × rise × barrels) at 100 %, all others clear | `LF_XINGS_PARTIAL=1.0 LF_XINGS_SET=small` | ARR: test plausible patterns, not severe blockage everywhere |
| `pm_s1`, `pm_s3` | antecedent wetness: AMC I / AMC III (the × 0.88 calibration kept, so only the wetness changes) | `LF_CN_AMC=I` / `III` | NRCS NEH 630 Ch 10 Table 10-1; the model converts with Chow et al. (1988), e.g. 70 → 49.5 / 84.3 (NEH table 51 / 85) |
| `pm_s2raw` | the calibration removed: AMC II, CN × 1.00 | `LF_CN_SCALE=1.0` | shows what the 0.88 scale does (Mo's question) |
| `pm_f` | frozen ground ("the same storm in early spring", not a September claim): CN 95 where the unfrozen CN ≤ 80, else 98, before the 0.88 scale like every CN; no steady soak-in | `LF_CN_FROZEN=knisel LF_INFIL_MMH=0` | Knisel (1980, CREAMS), as used in SWAT |
| `pm_cs` | worst plausible combination: 50 % blockage + AMC III | `LF_XINGS_PARTIAL=0.5 LF_CN_AMC=III` | shows whether the effects add up or interact |

**How blockage is modelled** (`sim/colab/w9_lisflood.py partial_block`, new, opt-in). The model has no culvert barrel: each mapped
crossing is a 3 × 3-cell notch cut through the road fill to the lowest ground within 40 m (`open_crossings`). A blockage fraction f raises
the notch floor to zcut + f (crest − zcut), i.e. the opening is filled from the bottom (sediment / debris), and the block around it is
protected from depression breaching so no carved path replaces the opening. f = 1 is solid fill (water leaves only over the road). This
is a geometric proxy for an inlet-area reduction, stated as such.

## What is reported (one table, base first; `proto/parametric_eval.py`)
1. Recall on the 54 DPW points (flagged segment within 30 m) and on the 89 storm-report sites (`score_v2` matching), % of segments flagged,
   and the chance recall at that flagged share.
2. Segments closed (p ≥ 0.5), newly closed vs the base, and no longer closed.
3. The 33 DPW misses of the base: how many become hits; median peak depth at them; separately Wachusett St (25 non-crossing misses) and the
   6 crossing misses.
4. Hamilton St (railroad-embankment debris closure): reached by any scenario (segment p ≥ 0.5)?
5. Emergency access (`PROTO_CASCADE=1`, `proto/cascade.py`): peak residents losing hospital / fire / police access within the standard.
6. Over-prediction: newly closed segments with no report within 150 m.
7. **Culvert priority list** (from `pm_c100` and `pm_ct` vs base): for each blocked crossing, the segments within 300 m that close only
   in the blocked run and the rise of the pool behind it (the `whatif_v3` pool readout); ranked, top 10 with location. Model-based; needs
   NAACC / MassDOT condition data to confirm.

## Reading rules (fixed now)
- A factor "matters for the DPW misses" if it turns **≥ 3 of the 33** base misses into hits; otherwise it does not.
- If no scenario turns a Wachusett St miss into a hit, the reading is: the missing piece is an erosion / washout mechanism, not an input.
- The effect of a factor is reported as the change from the base, with the over-prediction alongside; a scenario that gains DPW hits but
  closes many unreported roads is not called better.
- AMC III is the physically expected state for Sept 2023 (second-wettest summer on record). If `pm_s3` over-floods relative to the reports,
  the reading is that the × 0.88 scale stands in for something the model lacks (storm-drain capacity, infiltration of standing water),
  not that the soil was dry; reported as such.

**Cost.** 10 runs on GitHub Actions CPU, ~35–60 min each (the parity CPU run took 35 min): about 8 runner-hours.
