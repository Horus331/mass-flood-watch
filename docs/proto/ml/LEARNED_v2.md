# Learned closure layer v2 (T5): rule-offset ranking, road-graph neighbours, SAR-PU weights

Code: `proto/closure_v2.py` (`selftest`, `loso`, `fit`). Data: the parity catalogue `docs/proto/parity/catalog/<storm>_<area>_20m/`
(features and strict matches; baseline `docs/proto/scoring/BASELINE_v2_parity.json`, commit 26e6498f). Protocol: `docs/proto/PROTOCOL.md` v1.

## 1. Pre-registration (committed before any held-out number of a v2 variant was computed)

**What changes against v1** (`proto/closure_ml.py` + `proto/closure_loso.py`, results in `docs/proto/parity/catalog/ml/LOSO.md`):

1. **Rule offset.** score = o(x) + f(x), where o(x) = logit(Φ((peak depth − 0.30) / 0.10)) clipped to [−6, 6] is the depth rule's own score.
   f is learned. With LightGBM, o is the `init_score`; in the linear model it has a fixed coefficient of 1. The learned part can only add
   corrections to the physics, so the top of the rule's list stays unless the data move it. v1 lost exactly there.
2. **Learning to rank within storm.** Query = storm (its reporting domain); pairs are formed only inside a storm.
3. **Road-graph neighbour features** (no labels used), over segments within 300 m along `docs/graph_segments.json` links. The edge length is
   the mean of the two segment lengths, capped at 300 m, so a direct neighbour always counts. Features, all monotone +:
   - `nb_logdepth_max`, `nb_logdepth_mean` (length-weighted);
   - `nb_pmay_max` (max may-close probability);
   - `nb_up_overtop`: max overtopping among upslope neighbours, meaning neighbours with HAND above this segment's;
   - `nb_up_road` = ln(1 + upslope neighbour road length / 100 m).
4. **SAR-PU propensity weights.**
   - The propensity model is ê(x) = logistic P(labelled | rule-flagged), fitted on the training storms' rule-flagged segments (p_close ≥ 0.5,
     whole boxes, storm-balanced).
   - Its inputs: town reporting completeness (the Jeffreys-smoothed share of training storms with the town in the box, ≥ 50 segments, in which
     the town reported anything), local road, and ln(1 + AADT/1000).
   - Labelled positives get weight 1/ê. The weights are normalised to mean 1 within each storm and clipped to [0.25, 4]. Unlabelled rows get
     weight 1. Only relative propensities are used.
   - Everything is fitted inside the folds.

**Kept from v1:**
- training rows = each storm's reporting domain (sep2023: Leominster city);
- the 10 hazard and terrain features `closure_ml.MAIN`, with the same monotone signs (depth, overtop, speed, culvert, edge, area +; HAND −;
  slope and local road free).

**Variants scored on OOS-7 (k = 4, so α = 0.05 / 4 = 0.0125 in condition 2):**

| name | model | features | PU | eligible for adoption |
|---|---|---|---|---|
| `v2_lambdamart` (A) | LightGBM `lambdarank`, query = storm. Settings: 200 trees, lr 0.03, 7 leaves, min 50 rows/leaf, subsample 0.8, colsample 0.8, λ2 = 5, truncation 300. Monotone constraints, init score = o(x) | MAIN + 5 graph | yes | yes |
| `v2_pairlr` (B) | linear pairwise logistic (RankNet-linear). score = o(x) + z(x)·β. Loss = storm-mean of the PU-weighted mean pair loss, + 0.01/2·‖β‖². β sign-bounded (L-BFGS-B) | MAIN + 5 graph | yes | yes |
| `v2_pairlr_nograph` | B without neighbour features | MAIN | yes | no (ablation) |
| `v2_pairlr_nopu` | B without PU weights | MAIN + 5 graph | no | no (ablation) |

**Evaluation (nested LOSO, PROTOCOL.md §2):**
- For each held-out storm, the model is fitted on the other 8.
- An inner LOSO over those 8 gives out-of-fold scores. From these the fold chooses:
  - the **Platt calibration**, fitted on the training reporting domains, unweighted; isotonic is reported as a check only;
  - the **tier threshold**: the score at which the storm-averaged flagged share on the training storms equals the depth rule's (p_close ≥ 0.5)
    storm-averaged share on the same storms. This is the candidate's "deployed rule" for adoption condition 5.
- Nothing else is chosen on labels. All settings above were fixed before the first LOSO run. The only run before this commit was a smoke test
  of the sep2023 fold, which is a development storm.

**Scoring:**
- Scorer: `proto/score_v2.py` (`score_run`, `pooled`, `compare`) on the same 9 runs. Candidate orders are written as distinct 3-decimal
  `p_close` values, with the tier at ≥ 0.5 and depth breaking the remaining ties, because the scorer ranks by `round(p_close, 3)` and then depth.
- Comparisons:
  1. each variant against the depth rule (the adoption decision);
  2. against learned v1, refitted in the same folds;
  3. against the "eq" baseline: the depth rule lowered or raised to the candidate's tier size in every storm.
- The dev storms (sep2023, aug2021) are reported separately.
- Leave-one-area-out (overlapping boxes held out together) is reported for A and B as a leakage check only.

**Watch-tier question.** Today's watch tier is p_close ≥ 0.5 OR v1 P ≥ 0.02 (`prototype.TIER_WATCH_P`). Three alternatives flag the same
number of segments per storm:
- v2 top-k;
- rule first, then v2 order;
- the depth rule.

Each is compared with today's tier using a paired two-stage bootstrap of site hits.

**Decision rule.**
- v2 is adopted only if A or B passes all five conditions of PROTOCOL.md §5 against the depth rule, with α = 0.0125.
- It replaces v1 in the watch tier only if, at equal share, it beats today's watch tier with a 90 % CI above zero on OOS-7 and does not lose more
  than 2 sites on either dev storm.
