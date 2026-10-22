## How the design was chosen (and what was seen when)

1. **First run (v0).** All 11 features, including worst-hour rain, trained on the whole Leominster box with 4 km spatial blocks. In spatial CV it looked strong: PR-AUC 0.24 against 0.13 for the prior. It was then scored once on Worcester and **collapsed**, to below the prior (row "v0" in the tables).
2. **Diagnosis on the training storm alone.** 89 of the 97 labeled segments lie in Leominster city. The DPW damage inventory covers only Leominster, and the city sits under the rain core (median worst hour 78 mm at labeled segments against 38 mm box-wide). Rain alone had univariate AUC 0.87, so the model was learning the reporting footprint. Inside Leominster, where reporting is near-complete, adding rain changes nothing (2 km CV PR-AUC 0.261 with rain, 0.264 without). Rain also acts on closures through the flood model's depth and speed already.
3. **Adopted design.** The main model uses hazard and terrain features only, with rain kept as a comparison row. It is trained on Leominster city only, so "unlabeled" there is close to "not damaged". CV uses 2 km blocks inside that domain. The Worcester numbers for the adopted design were computed once, after this choice. Worcester was seen in step 1, so it is not a perfectly untouched test, but no parameter was fitted or tuned on it. The C = 0.5 penalty, the LightGBM settings and the feature transforms were fixed before any Worcester run.

## Caveats

- **Small, incomplete labels.** Leominster city has 89 labeled segments. Worcester has 15 labeled segments from 12 sites, so its bootstrap intervals are wide (PR-AUC [0.01, 0.17]). None of the differences on the blind test is statistically secure.
- **Calibration does not transfer across reporting regimes.** The model outputs P(documented) at Leominster-DPW completeness. Worcester labels are news and NWS reports, about 30x sparser per segment. The logistic model therefore expects 385 closures there against 15 labeled. That gap measures under-reporting as much as model error. The raw prior over-predicts by the same order (405 against 15).
- **Run settings differ between storms.** Worcester uses `wo_rundir`, which has the older defaults: CN x 1.0 and no D4 breaching, though it does have `vel_max.npz`. No Worcester run with the current defaults and velocity (`wo_edge`) existed when this was made. `dm_wor_d4dams` has D4 but no velocity. Edge-washout speeds come from snapshot speeds in Leominster and from `vmax` in Worcester.
- **HAND is approximate.** It uses the Euclidean-nearest stream cell, with streams at 0.5 km2 or more of D8 area on the channel-burned model ground. It is not a flow-path HAND.
- **Not tested on Vermont.** No Vermont run dir existed when this was made.
- **LightGBM** is weaker than the logistic model with about 90 positives. It is kept as a check, not as a candidate.

## Recommendation

- **Use the logistic hazard model as the dissertation's learned closure layer.** Its 11 coefficients are interpretable and sign-checked. On ranking it is at least as good as the 30 cm prior where labels are complete. On the blind storm it is better on PR-AUC, ROC-AUC and recall at 10 % (equal at 5 %, lower at 2 %). Its probabilities are calibrated on the training storm (BSS +0.09 against -0.15 for the prior). The main drivers are flow speed on the road, depth, how far the water beside the road rises above the crest, culvert overtopping and duration over 15 cm.
- **Keep `p_close` (the physics prior) as the map default for now.** Show `p_close_ml` (`PROTO_ML=1`) as a candidate layer until a second fully-reported storm is available for training or testing. That would be a DPW inventory for Worcester 2021, or Vermont 2023.
- **Never feed storm-scale rain or other footprint variables directly** while the labels come from a single city's inventory.
