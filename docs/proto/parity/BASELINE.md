# Consistent CPU baseline at LF_PARITY=1

**Short answer.** This is a new baseline in which every storm uses the same converged physics. It replaces the published GPU catalogue (`docs/proto/turing/*`, which has the artefacts in PARITY.md). Settings: CPU, `LF_PARITY=1`, CN × **0.88** (recalibrated, section 1), and current scoring with the bridge-deck matching. Results:
- **Gauges:** much better. The mean of the per-storm gauge rise errors falls from 0.82 to **0.46 m**. Model gauges stuck at zero rise fall from 9 of 16 to 3 of 16, and peak timing errors shrink on 7 of 9 storms.
- **Flags:** far fewer. The mean flagged share falls from 2.13 % to **1.07 %**.
- **Labels:** about the same. 38/119 → **41/132** sites are caught.
- **Lift on the big storms rises.** Leominster goes from 8.9 to **11.7**, Ida from 4.6 to 7.1, MetroWest from 4.0 to 5.2.
- **The light storms lose their few hits** (Elsa jul2021, aug2026, and 2 of 5 Worcester Aug 2021 sites). These are not artefacts. Under the new physics those sites peak at 0.28–0.29 m, just under the 0.30 m rule.
- **The learned model's ranking advantage survives.** The "watch" tier's advantage over simply flagging more by depth no longer clears zero (section 4).



* **Storm and box:** sep2023 on the original Leominster box `168000,908000,188000,928000`, 48 h, 20 m (the box of the old headline run
  `leominster_sep2023_gpu`). Chosen over the catalogue box (`162000…182000 E`, 36 h) because the Leominster gauge 01094500 lies 244 m from the
  catalogue box's free east edge, so its rise there depends on the boundary (PARITY.md 2.3). Both gauges are well inside this box.
* **Settings:** `LF_PARITY=1` (`LF_INFIL_MODE=rain`, `LF_INIT_TSTEP=1`), `LF_LOSS=cn`, AMC II, `LF_INFIL_MMH=2`, `LF_QOUT=1`, `LF_VOUT=1`, CPU (Actions).
* **Grid:** `LF_CN_SCALE` in {0.85, 0.88, 0.91, 0.94, 0.97, 1.00}.
* **Objective:** minimise `mean_abs_rise_error_m` from `proto/score.py` over Fitchburg 01094400 and Leominster 01094500 (values as rounded by
  `score.py`, 0.01 m). Tie (equal at 0.01 m) → lower `mean_abs_peak_timing_error_interval_h` (gap-aware peak timing). Still tied → the value
  closest to 0.91 (the current setting).
* Label recall, flagged share and lift are reported alongside and are **not** used to choose.

Runs: `.github/workflows/parity_test.yml` with `dest=docs/proto/parity/calib` → `docs/proto/parity/calib/leo48_cn<scale>/`.

### Result

All six runs: sep2023, Leominster box, 48 h, `LF_PARITY=1`, CPU. Observed rises: Fitchburg 1.00 m, Leominster 2.92 m. Strict labels are scored against `labels_sep2023_leominster.csv`, with 89 sites matched.

| `LF_CN_SCALE` | Fitchburg rise (m) | Leominster rise (m) | **mean abs rise error (m)** | bias (m) | mean abs peak timing, gap-aware (h) | rise50 timing (h) | sites caught / 89 | flagged share | lift |
|---|---|---|---|---|---|---|---|---|---|
| 0.85 | 0.86 | 3.22 | **0.22** | +0.08 | 0.4 | 0.6 | 35 | 1.76 % | 14.4 |
| **0.88** | 0.96 | 3.32 | **0.22** | +0.18 | 0.4 | 0.6 | 35 | 1.97 % | 12.8 |
| 0.91 | 1.07 | 3.42 | 0.29 | +0.29 | 0.1 | 0.6 | 35 | 2.20 % | 11.5 |
| 0.94 | 1.18 | 3.51 | 0.39 | +0.39 | 0.1 | 0.5 | 35 | 2.45 % | 10.3 |
| 0.97 | 1.29 | 3.60 | 0.48 | +0.48 | 0.1 | 0.4 | 37 | 2.76 % | 9.7 |
| 1.00 | 1.40 | 3.69 | 0.58 | +0.58 | 0.1 | 0.4 | 37 | 3.01 % | 8.9 |

**Chosen value: `LF_CN_SCALE=0.88`.** The pre-set rule decided it. 0.85 and 0.88 tie on the objective at 0.22 m and on peak timing at 0.4 h, so the last tie-break, the value closest to 0.91, picks 0.88. The objective is flat at the low end. Lower scales cut Fitchburg's rise below the observed value while Leominster stays too high, so the two gauges pull in opposite directions. The scale cannot fix both at once, and the gauge data do not pin the scale more tightly than about 0.85–0.88. At the converged step, the old ×0.91 over-predicts both gauges (+0.29 m). It was tuned at the default step, where the catalogue box put the Leominster gauge 244 m from a free edge and the recession oscillated. Labels did not decide anything here. Recall is flat at 35/89 from 0.85 to 0.94, and only the flagged share moves.

## 2. The catalogue rerun

The runs:
- **Catalogue storms:** all 9 catalogue storms with era `aws`, each on its catalogue box, t0 and hours, at 20 m.
- **Worcester Aug 2021:** its blind-test box `168000,875000,188000,895000`, 48 h. The published `worcester_aug2021_gpu` was in fact 18 h (37 half-hour frames) and is identical to the catalogue aug2021 run.
- **Settings:** CPU (Actions), `LF_PARITY=1`, `LF_LOSS=cn`, `LF_CN_SCALE=0.88`, `LF_INFIL_MMH=2`, `LF_QOUT=1`, `LF_VOUT=1`.

Scoring used `proto/prototype.py` (current defaults, bridge-deck matching), `proto/score.py` and `proto/validate_points.py`. Per-segment learned-model features came from `closure_ml.py extract`, with the label files `proto/data/labels_<storm>_*.csv`, as in `run_storm.slurm`.

Files are in `docs/proto/parity/catalog/<storm>_<area>_20m/` and `catalog/worcester_aug2021_48h/`: summary.json, score.json, points.json, flood_meta.json, segments.geojson, features_/matches_<storm>.json, hmax_cm.npz, lisflood.mass and gauge_windows.npz. The headline Leominster box run is `docs/proto/parity/calib/leo48_cn088/`.

How to read the table:
- **Sites:** strict labels (30 m), against the storm's primary label file (`checks.labels_segments`).
- **Flagged share and lift:** for the depth rule p_close ≥ 0.5. Lift is chance-corrected (recall / random recall at the same share).
- **Gauges:** from `score.py`. Peak timing is gap-aware (`mean_abs_peak_timing_error_interval_h`). rise50 is the rising-limb 50 % time ("-" means the model never crosses it).
- **Old:** the published GPU run in `docs/proto/turing/`. Note that the old runs used the earlier matching (no bridge decks), so their label counts are lower: Leominster 78 sites instead of 89.

| storm / run | sites caught / labelled (old GPU → new) | flagged share | lift | gauge mean abs rise error (m) | rise bias (m) | peak timing, gap-aware (h) | rise50 timing (h) |
|---|---|---|---|---|---|---|---|
| jul2021_worcester_20m | 1/5 → **0/5** | 1.22 % → **0.19 %** | 8.3 → **0.0** | 1.68 → **1.32** | -1.68 → -1.32 | 12.0 → 1.0 | - → 0.9 |
| aug2021_worcester_20m | 5/12 → **3/12** | 2.24 % → **1.11 %** | 16.0 → **10.5** | 0.76 → **0.40** | -0.76 → -0.26 | 7.7 → 4.8 | 2.4 → 1.4 |
| sep2021_worcester_20m | 2/5 → **2/6** | 4.07 % → **2.41 %** | 4.6 → **7.1** | 1.46 → **1.00** | -1.46 → -1.00 | 15.4 → 7.4 | - → 3.0 |
| sep2022_webster_20m | 0/4 → **0/4** | 1.87 % → **0.61 %** | 0.0 → **0.0** | 0.14 → **0.14** | -0.14 → -0.14 | 14.5 → 14.5 | - → - |
| jul2023_worcester_20m | 0/5 → **0/5** | 0.65 % → **0.07 %** | 0.0 → **0.0** | 0.24 → **0.18** | -0.24 → -0.18 | 11.8 → 3.2 | - → 7.1 |
| aug2023_metrowest_20m | 1/4 → **1/5** | 3.58 % → **1.62 %** | 4.0 → **5.2** | 0.69 → **0.19** | -0.69 → -0.19 | 15.0 → 6.0 | - → 1.6 |
| aug2023b_millbury_20m | 0/2 → **0/2** | 0.51 % → **0.11 %** | 0.0 → **0.0** | 0.54 → **0.43** | -0.54 → -0.43 | 9.0 → 8.5 | 10.4 → 8.8 |
| sep2023_leominster_20m | 28/78 → **35/89** | 2.80 % → **2.16 %** | 8.9 → **11.7** | 0.93 → **0.23** | -0.93 → -0.23 | 0.1 → 0.4 | 2.6 → 0.5 |
| aug2026_leominster_20m | 1/4 → **0/4** | 2.20 % → **1.37 %** | 6.6 → **0.0** | 0.90 → **0.29** | -0.90 → -0.29 | 0.8 → 0.5 | 5.7 → 1.0 |
| Worcester Aug 2021 blind box (old 18 h GPU `worcester_aug2021_gpu` → new 48 h) | 5/12 → **3/12** | 2.24 % → **1.13 %** | 16.0 → **10.3** | 0.76 → **0.40** | -0.76 → -0.26 | 7.7 → 4.8 | 2.4 → 1.4 |
| Leominster Sep 2023, headline box 48 h (old `leominster_sep2023_gpu` → new `calib/leo48_cn088`) | 28/78 → **35/89** | 2.63 % → **1.97 %** | 9.4 → **12.8** | 0.25 → **0.22** | 0.25 → 0.18 | 0.1 → 0.4 | 5.3 → 0.6 |
| **9 catalogue storms** | 38/119 → **41/132** | mean 2.13 % → **1.07 %** | | | | | |

Gauges (16 gauge-storm pairs over the 9 catalogue storms):

| | mean of per-storm mean abs rise error | pooled mean abs rise error | gauges with zero model rise |
|---|---|---|---|
| old GPU | 0.82 m | 0.83 m | 9 / 16 |
| new parity | **0.46 m** | **0.45 m** | 3 / 16 |

## 3. What changed, in plain terms

- **The GPU gauge zeros were artefacts.**
  - On 7 of 9 storms the GPU runs read a zero or near-zero rise at most gauges, with peak "timing errors" of 10–18 h. The cause was the wrong start level (PARITY.md 2.3).
  - Under parity most of these become real hydrographs. Leominster Sep 2023 (catalogue box): 0.93 → 0.23 m error. aug2026: 0.90 → 0.29 m. MetroWest: 0.69 → 0.19 m. Worcester Aug 2021: 0.76 → 0.40 m.
- **Three gauges still read zero.**
  - Assabet 01095434 in Ida, Little River 01123600 in Webster and Kettle Brook 01110000 in Millbury.
  - The bias is negative on 8 of 9 storms. **CN × 0.88 tuned on Leominster under-predicts gauge rise on the other storms:** Elsa −1.32 m, Ida −1.00 m, Millbury −0.43 m.
  - The gauges therefore say the light and medium storms need less loss, not more. A single global CN scale does not fit both the big Leominster storm and the summer storms. Candidates are an AMC or season-dependent loss, and the 2 mm/h `rain`-mode infiltration, which removes 30–40 % of the light-storm excess (PARITY.md 2.1).
  - This was **not** re-tuned here. The objective used one storm only, by design.
- **Flagged share halves**, from a 2.13 % to a 1.07 % mean. Most of the drop on the light storms is the GPU's spike-only segments disappearing: jul2023 0.65 → 0.07 %, aug2023b 0.51 → 0.11 %, sep2022 1.87 → 0.61 %. On the big storms it is mainly the lower CN scale plus infiltration: Leominster 2.80 → 2.16 %, Ida 4.07 → 2.41 %.
- **Labels: the real gains are on Leominster, the losses on the light storms.**
  - Leominster goes 28/78 → 35/89. The +11 sites are the bridge-matching fix. The recall gain from the new physics alone is small: under the old GPU run with the new matching, the estimate was 35–36/89 (RECALL.md section 4).
  - Lost hits: Elsa 1 → 0, aug2026 1 → 0, Worcester Aug 2021 5 → 3, and Ida 3 → 2 against the old run rescored with the new matching.
  - **None of the lost hits were GPU spikes.** Their old hmax equalled the snapshot peak. The sites are simply shallower now: W009 0.45 → 0.29 m, AUG2026-02 0.36 → 0.28 m, JUL2021-02 0.45 m → dry.
  - The light storms therefore get no rule hits at all now (jul2021, sep2022, jul2023, aug2023b, aug2026: 0 of 20 sites). This is the same under-prediction the gauges show.
- **Lift rises on every storm that keeps hits.** Leominster 8.9 → 11.7 (headline box: 9.4 → 12.8), Ida 4.6 → 7.1, MetroWest 4.0 → 5.2. Worcester Aug 2021 falls 16.0 → 10.5 because it lost 2 of 5 hits.
- **Blind test, Worcester Aug 2021 at 48 h:**
  - 3/12 sites at 1.13 % flagged, lift 10.3, gauge error 0.40 m.
  - Within rounding this is the same as the 18 h catalogue run (3/12, 1.11 %), so the peak falls inside 18 h.
  - The published blind-test "5/12 at 2.24 %" was the 18 h GPU run, not a separate 48 h one.

## 4. Learned model (LOSO) and two-tier scheme on the new baseline

Commands:
- `python proto/closure_loso.py --reps 200 --runs docs/proto/parity/catalog` → `docs/proto/parity/catalog/ml/`.
- `python proto/recall_study.py all --runs docs/proto/parity/catalog --headline docs/proto/parity/calib/leo48_cn088` → `docs/proto/parity/catalog/recall/`.

Neither touches `docs/proto/ml/` or `docs/proto/recall/`, and neither changes the production model `docs/proto/ml/closure_lr_all.json`. Without `--runs`, both scripts read `docs/proto/turing` exactly as before. Env equivalents: `PROTO_RUNS`, `PROTO_HEADLINE`, `PROTO_ML_OUT`, `PROTO_RECALL_OUT`.

**Learned closure model, leave-one-storm-out (logistic, main features):**

| | old GPU (`docs/proto/ml`) | new parity |
|---|---|---|
| rows / positive segments | 54 352 / 163 | 55 639 / 199 |
| pooled ROC: learned / rule / may-close | 0.605 / 0.783 / 0.775 | 0.653 / 0.772 / 0.765 |
| per-storm ROC (macro): learned / rule | 0.765 / 0.700 | 0.763 / **0.666** |
| per-storm wins of learned over rule: ROC / PR / recall at rule's share | 7 / 5 / 1 (4 ties) | 7 / **7** / 2 (5 ties) |
| pooled recall at the rule's share: rule / learned | 0.221 / 0.123 at 2.1 % | 0.166 / 0.101 at 1.1 % |
| pooled PR-AUC: learned / rule | 0.0067 / 0.0178 | 0.0095 / 0.0320 |
| final fit: dropped for sign | none | `log_area` |

What this means:
- **Same verdict as before.** Within a storm, the learned model ranks segments better than the rule (ROC 7/9, now also PR 7/9). Pooled across storms its probabilities are less comparable, and at the rule's own small flagged share it catches fewer sites.
- The rule's per-storm ROC drops (0.700 → 0.666) because the light storms now flag almost nothing.
- Coefficients keep their signs and order. Depth and speed are larger, overtop and h15 smaller, and `log_area` is dropped for a wrong sign.

**Two-tier scheme** (tier 1: p_close ≥ 0.5; tier 2: a watch family with threshold chosen LOSO; 2000-replicate cluster bootstrap). Pool: 9 storms, held out. Old pool: 168 sites. New pool: 186 sites, because of the bridge-deck matching.

| | old GPU | new parity |
|---|---|---|
| default (tier 1 alone) | 57/168 = 0.34 at 2.1 % | 62/186 = 0.33 at 1.1 % |
| **learned watch, budget 8 %** | 95/168 = 0.57 at 7.4 %; vs eq-share depth rule +0.077 [+0.02, +0.29], P(> eq) 0.97 | 108/186 = **0.58** at 7.2 %; vs eq **+0.022 [−0.03, +0.27]**, P(> eq) 0.73 |
| fully nested ("pick family"), 8 % | 93/168 = 0.55; vs eq +0.065 [0.00, +0.24] | 103/186 = 0.55; vs eq **−0.032 [−0.09, +0.23]** |
| fully nested, 5 % | 0.44; vs eq −0.02 | 0.46; vs eq −0.02 |
| fully nested, 10 % | 0.59; vs eq +0.01 | **0.67**; vs eq +0.043 [−0.01, +0.31], P 0.89 |
| relax the depth rule only, 8 % | 77/168 = 0.46 at 6.8 % | **102/186 = 0.55** at 5.8 % |
| learned watch, 7 never-used storms, 8 % | 15/29 (default 5, eq 9) | 14/31 (default 3, eq 8) |
| Leominster held out, learned watch, 8 % | 71/127 at 9.0 % | 84/143 at 9.0 % |

How the conclusions change:
- **Still true.** A two-tier scheme roughly doubles recall over the default out of sample: 0.33 → 0.55–0.58 at about 7 % flagged. The cost is about 7× the flags on this baseline, because the default now flags only 1.1 %.
- **No longer supported.** "The learned watch tier beats simply relaxing the depth rule to the same share" (old: +0.077, interval above zero). On the parity baseline, relaxing the depth rule is much stronger than it was. At 8 % it reaches 0.55 at 5.8 % flagged, against 0.46 on the GPU runs. The reason is that the converged physics puts many documented sites at 10–30 cm, just under the rule, instead of at spike depths or zero. The learned tier's edge shrinks to +0.02, with an interval spanning zero. Nested selection now loses to the eq-share rule at 8 %.
- **Where the learned tier still helps** is the small storms. On the 7 never-used storms it catches 14/31 against 8/31 for the eq-share depth rule and 3/31 for the default. That is the same pattern as before, but the 9-storm pool no longer clears zero. At 10 % budget nested selection is +0.04 (P 0.89).
- **Recommendation:**
  - Keep `PROTO_TIERS` off by default.
  - If a second tier is wanted, "depth ≥ t" (relaxed rule, chosen LOSO) is now as good as the learned tier at 8 % on the pooled data, and needs no model.
  - Re-decide only after the CN / infiltration under-prediction on the light storms (section 3) is addressed, since that is exactly where the two families differ.
- **Leominster miss anatomy (headline box, `calib/leo48_cn088`).**
  - News/agency: 35/89 caught, against 28/78. Misses: 7 near-flag, **22 layer** (was 15), 7 name-far, 8 non-flood, **10 dry** (was 8), 3 unmatched (was 14, the bridge fix).
  - DPW: unchanged at 24/54, with 18 dry instead of 21.
  - More misses now sit in "the model has a signal, below the rule" (B). This is consistent with the relaxed-depth result above.
