## Note on pooled metrics

"Concatenated" ROC-AUC / PR-AUC rank all 54 352 segments of all storms on one scale. The rule's p_close is an absolute depth threshold, so its level carries
across storms. The learned model's level does not (it predicts 16 closures for Sept 2023 Leominster against 97 labeled, and 76 for Aug 2023 against 7),
because each storm's reporting completeness is different and the model is trained to the average. Concatenated scores therefore mostly measure
between-storm calibration. For "which roads in this storm", the relevant number is the **stratified** ROC-AUC (only positive/negative pairs from the same
storm), the per-storm table, and recall at the rule's flagged share (each storm flagged at its own rule share).

## Conclusions

1. **Overall ranking: the learned model beats the rule out of storm, modestly.** Stratified ROC-AUC is 0.783 against 0.757. The per-storm mean is
   0.765 against 0.700, with the mean per-storm difference +0.065 [0.011, 0.118]. The learned model wins on 7 of 9 storms on the whole box and on 9 of 9 inside the
   reporting towns. The gains are largest where the rule is weakest (rule ROC-AUC 0.58-0.69): Aug 2023 MetroWest, Aug 2023b Millbury and Sept 2022 Webster.
   In Millbury and Webster the rule flags none of the reported segments, and the learned model still puts them on average in the top 20-30 %
   (ROC-AUC 0.75 and 0.72; Webster is the only storm whose per-storm interval excludes zero). The result holds when overlapping boxes are held
   out together (leave-one-area-out 0.782), so it does not come from remembering repeat sites.
2. **Top of the list: the learned model loses to the rule, and this is the operational number.** Suppose the learned model flags as many segments as the rule
   does (2.1 % of the box). It then finds 12 % of the labeled segments, while the rule finds 22 % (difference -0.10 [-0.15, 0.00]). Its lift is 5.8 against 10.4. PR-AUC is lower too,
   0.007 against 0.018. The learned model wins on recall at the rule's share in only 1 storm (Jul 2021) and loses clearly in Aug 2021, Aug 2023 and Sept 2023.
   With few positives the model learns gentle slopes: depth is about as heavy as road class and slope, so deep water on the road no longer dominates. The rule's hard
   30 cm threshold is the sharper top-k signal. Adding the rule's own logit as a feature did not help, because its fitted weight came out negative next to log_depth and the sign check
   dropped it.
3. **Best of both (post hoc, so treat it as a hypothesis for the next storm).** Rank the rule's flagged set first and order everything, including the inside of that set, by the
   learned P. This keeps the rule's top recall (0.22). It reaches that recall with **1.4 %** of segments instead of 2.1 %, by breaking the rule's ties. Its
   stratified ROC-AUC is 0.788, and it has the best recall at the may-close share (0.34 against 0.33). It wins ROC-AUC on 8 of 9 storms.
4. **The may-close overtop layer** ranks about like the rule (stratified 0.747) and adds nothing at the top that the learned model does not have.
5. **Model class.** The monotone HistGB is worse than the logistic model (stratified 0.753, per-storm 0.716, 5 of 9 wins), as it was with LightGBM on one storm. Weighting
   barely matters for ranking: unweighted 0.782 against balanced 0.783. Unweighted gets slightly better top recall (0.15) because Leominster's denser labels sharpen it.
6. **Reporting footprint.** Training on whole boxes instead of reporting towns costs a little ranking quality inside reporting towns (0.766 against 0.788). It gains top recall
   on the whole box (0.17 against 0.12) by learning where reports come from. That gain is the confound, so the domain restriction stays. The largest coefficient is
   **local_road (-0.23 / SD, CI excludes 0)**: reports favour named arterials. That is partly real (more traffic, more exposure, culverts sized for streets) and partly reporting
   bias (news names main roads). It cannot be separated with these labels, and it is the main reason not to read the learned P as a physical closure probability.
7. **Drivers (all-storm fit).** After road class, the drivers are depth, slope (negative), flow speed, overtopping beside the road, HAND (negative) and hours over 15 cm.
   Every hazard coefficient has the expected sign, and none is dropped in the final fit. Their 90 % intervals touch 0, because the sign check zeroes a feature in 13-37 % of
   cluster-bootstrap replicates. Culvert overtopping carries almost no out-of-storm weight (permutation importance about 0, kept in 63 % of replicates).
8. **Calibration.** The learned P is far better calibrated than p_close (Brier 0.0035 against 0.0199; expected 479 against 1453 for 163 labeled), but it still runs high
   outside the reporting towns and has negative skill against the base rate (BSS -0.17). It is P(documented), and documentation completeness changes from storm to storm. The Elkan-Noto
   c (0.019) is not usable as a PU correction here: e1 needs a classifier that is near-certain somewhere, and this one is not. The probabilities should be shown as a relative
   ranking, not as a percentage chance of closure.
9. **Uncertainty.** Eight of the nine storms have 5-13 labeled segments from 2-12 sites. Every per-storm interval for the difference in ROC-AUC except
   Sept 2022's includes zero. The pooled sign test (7 of 9) gives p = 0.09. The pooled per-storm mean difference is the only ranking gain whose 90 % interval excludes zero.

## Recommendation

- The all-storm logistic (`docs/proto/ml/closure_lr_all.json`) replaces the Sept 2023-only fit as the learned layer. `closure_ml.py map` now uses it by default
  (`--model` or `$PROTO_ML_MODEL` overrides). Keep `p_close` as the alert layer. Use the learned P to order segments within and beyond the rule's flags (the hybrid),
  and test that ordering on the next storm before claiming it.
- The highest-value next data is a second complete inventory, a DPW list like Leominster's for one Worcester storm. With news-only labels, top-of-list
  comparisons will stay inside the noise.
