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

## 2. Result: not adopted; the watch tier stays on v1

Run: `python proto/closure_v2.py loso --boot 2000`. All four variants and the v1 refit were scored in one run after the pre-registration commit
(d60a7615). Outputs:
- `docs/proto/ml/v2/loso.json`: everything.
- `docs/proto/ml/v2/score_<variant>.json`: score_v2 run files, so `python proto/score_v2.py --compare docs/proto/ml/v2/score_base.json docs/proto/ml/v2/score_v2_pairlr.json` reproduces a verdict, with α = 0.05 there rather than 0.0125.
- `docs/proto/ml/LEARNED_v2.json`: the summary.

### 2.1 Adoption rule against the depth rule (OOS-7, 29 sites, 3 % flagged, α = 0.0125)

| variant | hits @3 % (rule 5) | Δ recall | one-sided lower bound | ΔFSS300 @3 % | worst storm | tier lift (rule 4.67) | verdict |
|---|---|---|---|---|---|---|---|
| A `v2_lambdamart` | 4 | −0.034 | −0.161 | −0.0036 | −1 (sep2021) | 6.31 | **reject** (gain, CI, FSS) |
| B `v2_pairlr` | 5 | 0.000 | −0.143 | −0.0032 | −1 (sep2021; jul2021 +1) | 4.78 | **reject** (gain, CI, FSS) |
| `v2_pairlr_nograph` (ablation) | 5 | 0.000 | −0.143 | −0.0036 | −1 | 6.24 | reject |
| `v2_pairlr_nopu` (ablation) | 7 | +0.069 | 0.000 | +0.0013 | 0 | 4.89 | reject (CI only; not eligible anyway) |
| *v1 refit in the same folds (context)* | 8 | +0.103 | −0.094 | +0.0040 | −1 | 4.48 | reject (CI) |

Against learned v1, both A and B lose 3 to 4 OOS-7 sites at 3 %. Against "eq" (the depth rule set to the candidate's tier size), the 3 % numbers
are the same as against the rule.

### 2.2 Recall curve and dev storms

Pooled site recall, whole box:

| | OOS-7 @1 / 2 / 3 / 5 / 10 % (29 sites) | FSS300 @3 % | dev2 @3 % (90 sites) | dev2 FSS300 @3 % | all 9 @3 % (119 sites) |
|---|---|---|---|---|---|
| depth rule | .069 / .138 / .172 / .241 / .393 | .0174 | .367 | .231 | .319 |
| v1 | .069 / .172 / **.276** / **.448** / .552 | .0214 | .200 | .113 | .218 |
| A | .069 / .138 / .138 / .276 / .566 | .0138 | **.389** | .229 | .328 |
| B | .103 / .138 / .172 / .276 / **.586** | .0142 | .367 | **.246** | .319 |
| B − graph | .103 / .138 / .172 / .241 / .552 | .0138 | .356 | .237 | .311 |
| B − PU | .103 / .138 / .241 / .345 / .586 | .0187 | .367 | .251 | .336 |

**OOS-7 hits at 3 %, per storm** (aug2023 / aug2023b / aug2026 / jul2021 / jul2023 / sep2021 / sep2022):

| | per storm | total |
|---|---|---|
| rule | 1 / 0 / 1 / 0 / 0 / 3 / 0 | 5 |
| v1 | 2 / 2 / 1 / 1 / 0 / 2 / 0 | 8 |
| A | 1 / 0 / 1 / 0 / 0 / 2 / 0 | 4 |
| B | 1 / 0 / 1 / 1 / 0 / 2 / 0 | 5 |

**Dev storms.**
- sep2023 (79 sites): rule 30, A 32, B 30, v1 15.
- aug2021: every model gets 3 of 11.

**Full-resolution within-storm ranking** (mean over OOS-7 storms, no 3-decimal encoding):

| | ROC-AUC | PR-AUC |
|---|---|---|
| rule | 0.645 | 0.0057 |
| v1 | 0.750 | 0.0074 |
| A | 0.655 | 0.0067 |
| B | 0.718 | 0.0071 |
| B − PU | 0.739 | 0.0081 |

On sep2023, ROC / PR: rule 0.803 / 0.178, B 0.810 / 0.191, v1 0.795 / 0.105.

**Leave-one-area-out** (leakage check): A 5/29 at 3 % and B 6/29, against the rule's 5. No sign that the LOSO numbers come from overlapping
boxes.

**Reading.**
- The offset did what it was designed to do: v2 keeps the rule's strength at the top of the list. In Leominster it matches or beats the rule
  (30 to 32 of 79), where v1 drops to 15.
- But v2 also keeps the rule's blindness in the small held-out storms. Where the depth rule has nothing (Millbury, Elsa, Webster), a correction
  layer of ±1 logit cannot lift dry roads above the ones it ranks deep. v1 can, because it ignores the 30 cm threshold.
- So no single ranking wins both storm types. The OOS-7 decision set is the small-storm type, where v2 ties the rule.
- The fitted corrections are mostly terrain and road class. In B, the hazard coefficients go to 0 because the offset already carries depth.
  What remains: log_area +0.60/SD, local road −0.41, upslope-neighbour overtop +0.21, HAND −0.13, slope −0.09, neighbour max depth +0.06.
- The graph features add little: B vs B − graph, ±1 site everywhere.
- The SAR-PU weights did not help. B − PU gets 7/29 against 5/29, and 0.739 against 0.718 ROC. That is within noise, but in the wrong
  direction.

### 2.3 Roadmap success criteria (T5)

- **Recall at the rule's share ≥ the rule's:** met only trivially. B's tier is the rule's tier: same size, OOS-7 tier recall 3/29 for both.
- **Stratified AUC ≥ 0.78:** not met. The OOS-7 mean per-storm ROC-AUC is 0.72 for B and 0.66 for A, against 0.75 for v1.

### 2.4 Watch tier: should v2 replace v1?

**No.** Today's watch tier (p_close ≥ 0.5 OR v1 P ≥ 0.02) was compared with the same number of segments per storm (mean share 6.7 % on OOS-7,
7.1 % on dev):

| pool | today (v1 watch) | depth rule, same share | A, same share | B, same share | B − today, 90 % CI |
|---|---|---|---|---|---|
| OOS-7 (29) | **13** | 8 | 10 | 11 | −0.069 [−0.25, +0.07] |
| dev2 (90) | 44 | 48 | **50** | 48 | +0.044 [−0.01, +0.11] (A: +0.067 [0.00, +0.13]) |
| all 9 (119) | 57 | 56 | **60** | 59 | +0.017 [−0.13, +0.08] |

- "Rule first, then v2" is identical to plain v2, because the offset already puts the rule's flags first.
- v2 loses held-out sites against today's tier, so the pre-registered replacement condition fails.
- Today's tier against the depth rule at the same share: +0.17 [−0.03, +0.39] on OOS-7. This is the "two-tier edge ≈ 0" from the recall study:
  positive but not significant.

### 2.5 Calibration (Platt within training folds; held-out reliability)

The probabilities mean P(documented closure or damage | x). Pooled held-out results:

| | whole box: expected / labelled | whole box: Brier (BSS) | reporting towns: expected / labelled | reporting towns: Brier (BSS) |
|---|---|---|---|---|
| B | 334 / 199 | 0.00369 (−0.036) | 204 / 188 | 0.00643 (−0.030) |
| A | 349 / 199 | 0.00369 (−0.036) | 209 / 188 | 0.00642 (−0.029) |
| v1 (raw logistic) | 502 / 199 | 0.00411 (−0.154) | 308 / 188 | 0.00693 (−0.109) |

Isotonic in place of Platt changes the BSS by less than 0.01 (B: −0.023 in the reporting towns).

**Reliability of B in the reporting towns** (mean P → observed share, segments):

| mean P | observed share | segments |
|---|---|---|
| 0.004 | 0.0041 | 20 257 |
| 0.006 | 0.0067 | 7 468 |
| 0.013 | 0.0163 | 1 163 |
| 0.031 | 0.0302 | 529 |
| 0.067 | 0.086 | 151 |
| 0.146 | 0.011 | 93 |
| 0.278 | 0.041 | 73 |
| 0.46 | 0 | 5 |

- Calibration is good up to P ≈ 0.1.
- Above that, it is badly over-confident. The roads deeper than about 0.65 m (the offset's +6 tie) were documented in only 4 of 171 cases.
- Per storm, the level follows reporting completeness, not hazard:
  - sep2023 (DPW inventory): 16 expected against 113 labelled;
  - sep2021: 80 against 12.
- So a displayed "P" is a pooled P(reported) and should not be read as P(closed).
- The fold tier threshold sat at P ≈ 0.034 (0.013 in the Leominster fold).

### 2.6 Caveats

- **SAR-PU.** The propensity model fits "labelled | rule-flagged" because no flooded-but-unreported ground truth exists. Rule-flagged is
  not flooded (the precision is a few %), so ê mostly measures which towns report.
  - Town rate dominates: +2.2/SD, against local road −0.29 and AADT −0.13.
  - Weights from it reweight Leominster-like towns down and silent towns up. That did not improve held-out ranking.
- **Sample size.** With 29 OOS-7 sites, ±2 sites is noise. No variant, v1 included, clears the one-sided lower bound.
- **Encoding.** Scores pass through score_v2 as 3-decimal ranks, with up to about 1000 distinct levels per storm. That is exact for the 1–5 %
  shares and slightly coarse at 10 %. The full-resolution ROC and PR above are not affected.

### 2.7 Decision

- **v2 is not adopted.** Neither eligible variant passes PROTOCOL.md §5. The gain is 0 or −1 site, the FSS drops, and the CI includes 0.
- **Nothing is wired into `closure_ml.py map`.** The default and the `PROTO_TIERS` watch tier (v1 at 0.02) are unchanged.
- `closure_v2.py fit` / `on_rows_v2` exist but were not run, and no model file was written.
- **Next, if T5 is revisited.** Re-registered as a new variant, with the locked set still unopened:
  - let the offset's weight be learned per storm regime: a free coefficient on o(x), or a gate on storm-wide rule share;
  - or keep the depth rule for tier 1 and v1 for the watch tier. That is today's design, and these results support it.
