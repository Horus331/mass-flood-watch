# Closure ranking and alert candidates on the expanded set (PROTOCOL v2, held-out 23 storms / 90 sites)

Code: `proto/closure_expanded.py` (reuses `proto/closure_v2.py` and `proto/score_v2.py`). Protocol: `docs/proto/PROTOCOL.md` **v2**
(commit 1466f7e6). Baseline: the clean parity catalogue `docs/proto/parity/catalog/`, as scored in `docs/proto/scoring/BASELINE_v2_expanded.md`.

## 1. Pre-registration (committed before any held-out-23 number of these candidates was computed)

**Folds.** Nested leave-one-storm-out over all 25 non-locked parity storms (2 dev + 23 held-out). For each storm *t*, everything label-fitted is
fitted on the other 24; tier thresholds / sizes are chosen inside the fold on those 24 only (inner LOSO for the learned models). Locked storms
(aug2015, aug2018, aug2020, jul2018, oct2016) are not loaded. Pooled held-out numbers use fold predictions only.

**Candidates** (k = 5 tests, so α = 0.05 / 5 = **0.01** in condition 2):

| name | ranking | alert tier ("p_close ≥ 0.5" set) | route |
|---|---|---|---|
| (a) `a_v1` | learned v1 logistic (`closure_ml.LR`, MAIN features, storm-balanced, reporting domains), refitted on 24 storms per fold | v1 score ≥ in-fold equal-share threshold (storm-mean training share = depth rule's storm-mean training share; inner LOSO) | §5a |
| (b) `b_v2nopu` | learned v2 variant B without propensity weights (`closure_v2` `v2_pairlr_nopu`: rule-logit offset + sign-bounded pairwise linear correction, MAIN + 5 graph features) | same recipe as (a) | §5a |
| (c) `c_stormrel` | modelled peak road depth (ties: p_close) | top *q* of the storm's in-box segments; *q* chosen in-fold from {0.25, 0.5, 0.75, 1.0, 1.25, 1.5} %: the **largest** *q* whose pooled training site lift is ≥ 0.8 × the depth rule's pooled training lift on the same 24 storms (else the smallest) | §5a **and** §5b |
| (d) `d_twotier` | tier 1 = depth rule (in its own order), then the in-fold v1 score fills the budget; budget B = 1 / 3 / 5 %, decision at **B = 3 %** | the depth rule (unchanged) | §5a |

Physical motivation for (c): the model under-predicts depth on light storms (gauge bias −0.28 m on NEW16) so the fixed 0.30 m rule flags only
0.23 % of segments there, but its *ranking* still carries 2–2.6× chance skill. (c) trusts the ranking, not the absolute depth. Its 3 % ranking is
essentially the baseline's, so (c) can only pass through §5b (it is an alert-tier change).

**Decision.** A variant passes if `score_v2.compare(..., rule=ADOPT_V2, alpha=0.01)` adopts it on held-out 23 (§5a; for (c) also §5b with
`level='rule'`, including the 1.65 % budget cap). Reported for every variant: held-out-23 site recall at 1 / 3 / 5 % and at the tier, chance
and lift, FSS@300, per-storm changes, OOS-7 / NEW16 / dev sub-pools, per-storm ROC-AUC; the PROTOCOL v1 (OOS-7) verdict as context only.

**Wiring.** If a variant passes, it is wired as an opt-in env flag in `proto/prototype.py` (default unchanged). If none passes, nothing is wired
and the deployed rule's held-out-23 numbers are what the dissertation reports.
