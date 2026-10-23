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

## 2. Result: no candidate passes PROTOCOL v2; nothing is wired

Run: `python proto/closure_expanded.py run --boot 2000`, once, after the pre-registration commit (464b7af6). Outputs:
`docs/proto/ml/EXPANDED.json` (everything) and `docs/proto/ml/expanded/score_<name>.json` (score_v2 run files), so e.g.
`python proto/score_v2.py --compare docs/proto/ml/expanded/score_base.json docs/proto/ml/expanded/score_d_twotier.json --protocol v2 --k 5`
reproduces a verdict.

### 2.1 Verdicts (held-out 23, 90 sites, box, α = 0.01)

| test | Δ recall @3 % (sites) | one-sided lower bound (1st pct) | ΔFSS300 | worst ≥3-site storm | tier lift (rule 4.78) | verdict |
|---|---|---|---|---|---|---|
| (a) `a_v1` §5a | **+0.122 (+11)** | **0.000** | +0.0056 | −1 (sep2021) | 6.18 | reject (condition 2 only) |
| (b) `b_v2nopu` §5a | +0.078 (+7) | −0.039 | +0.0037 | −1 | 4.87 | reject (condition 2) |
| (c) `c_stormrel` §5a | 0.000 | 0.000 | −0.0001 | 0 | 2.42 | reject (gain, CI, FSS, lift) |
| (c) `c_stormrel` §5b (tier) | +0.022 (+2) | −0.043 | −0.0132 | −1 (aug2023) | 2.42 | reject (gain, CI, FSS, lift; budget cap met: 1.49 % ≤ 1.65 %) |
| (d) `d_twotier` §5a, B = 3 % | **+0.122 (+11)** | **0.000** | +0.0049 | −1 (sep2021) | 4.78 (= rule) | reject (condition 2 only) |

(a) and (d) clear every condition except significance, and that one by the narrowest margin the bootstrap allows: the 1st percentile of
the paired Δ is exactly 0, P(Δ ≤ 0) = 0.014 against the 0.01 required. The lower bound is +0.019 at α = 0.025 and +0.033 at α = 0.05, so they
would have passed with k ≤ 2. Under the pre-registered k = 5 they do not pass, and the rule is not re-read after the fact. As context only, the
PROTOCOL v1 (OOS-7) verdict is also reject for all four (a, d: +0.125, lower bound −0.079).

### 2.2 Pooled site recall (box; hits / sites, recall, 90 % CI; lift)

| | tier ("rule") | 1 % | 3 % | 5 % | FSS300 @3 % | mean tier share |
|---|---|---|---|---|---|---|
| **held-out 23 (90 sites)** | | | | | | |
| baseline (deployed 0.30 m rule / p_close order) | 5, 0.056 [0.01, 0.11]; 4.8 | 5, 0.056; 2.6 | 15, 0.167 [0.08, 0.26]; 2.6 | 23, 0.256 [0.16, 0.36]; 2.4 | 0.019 | 0.43 % |
| (a) v1 refit | 7, 0.078; 6.2 | **11, 0.122; 5.6** | **26, 0.289 [0.19, 0.39]; 4.5** | **35, 0.389 [0.28, 0.50]; 3.7** | 0.025 | 0.47 % |
| (b) v2 B − PU | 5, 0.056; 4.9 | 9, 0.100; 4.6 | 22, 0.244 [0.16, 0.34]; 3.8 | 33, 0.367; 3.5 | 0.023 | 0.43 % |
| (c) storm-relative depth | 7, 0.078; 2.4 | 5, 0.056; 2.6 | 15, 0.167; 2.6 | 23, 0.256; 2.4 | 0.019 | 1.49 % |
| (d) two-tier (rule + v1 watch) | 5, 0.056; 4.8 | 9, 0.100; 4.6 | **26, 0.289 [0.19, 0.39]; 4.5** | **35, 0.389 [0.28, 0.50]; 3.7** | 0.024 | 0.43 % |
| **OOS-7 (32) @3 %** | base 6 · a 10 · b 7 · c 6 · d 10 | | | | | |
| **NEW16 (58) @3 %** | base 9 · a 16 · b 15 · c 9 · d 16 | | | | | |
| **dev: sep2023 (79) / aug2021 (12) @3 %** | base 30 / 3 · a **22** / 5 · b 30 / 3 · c 30 / 3 · d 31 / 4 | | | | | |

Mean per-storm ROC-AUC (full resolution, segment level): depth / rule 0.673 on held-out 23 (0.646 OOS-7, 0.684 NEW16, 0.744 dev);
v1 0.763 (0.766, 0.762, 0.794); v2 B − PU 0.757 (0.746, 0.761, 0.814).

**Per-storm changes at 3 % (a and d are identical on held-out 23):** +1 at aug2023, aug2023b, aug2026, jul2021, sep2022, may2018, aug2018b,
sep2018m, jul2019, aug2020b, jul2023b; +2 at sep2018w; −1 at sep2021 and sep2019 (2 sites, exempt). The gain is spread over 12 storms rather than
carried by one, which is what the storm-first bootstrap rewards; it is still 11 sites.

**Dev storms.** (a) loses 8 sites at 3 % on sep2023 (30 → 22) and its tier halves there (29 → 15): the PROTOCOL "explain" clause applies —
v1 ignores the 0.30 m threshold and so gives up the top of the rule's list in the one storm where the rule works (as in `LEARNED_v2.md`).
(d) keeps the rule's tier and gets 31 / 4, so it is the only candidate that gains on held-out without losing on dev.

### 2.3 Reading

1. **The storm-relative depth rule (c) does not work, and the reason is informative.** In 23 of 25 folds the in-fold choice ran to the cap,
   q = 1.5 % (0.5 % in the sep2023 fold, 1.25 % in two Worcester folds). On held-out storms it raises tier recall from 5 to 7 of 90 but at
   3.5× the share, so its lift halves (4.8 → 2.4) and FSS drops. Re-thresholding the model's depth does not help because the depth *ranking*
   itself is weak on held-out storms (ROC 0.67). The under-prediction (gauge bias −0.28 m) explains why the 0.30 m rule flags almost nothing
   on light storms; it does not explain why reported sites are missed, which is mostly that they are not among the deepest modelled roads.
2. **What carries held-out skill is the learned terrain/road prior, not the depth.** v1 (and the two-tier scheme, whose watch layer is v1)
   is the only thing that moves the held-out numbers: 0.167 → 0.289 at 3 %, lift 2.6 → 4.5, ROC 0.67 → 0.76, consistent across OOS-7 and NEW16.
   v2 B − PU sits in between, because its offset keeps the depth order at the top.
3. **The two-tier scheme is the right shape** (rule for the alert, v1 for the watch): it adds the v1 gain on held-out storms and keeps the
   rule's dev performance. It misses adoption on significance alone (P(Δ ≤ 0) = 0.014 vs 0.010).

## 3. Decision and what to report

- **No variant passes PROTOCOL v2.** Nothing is wired; `prototype.py` is unchanged. The deployed alert stays `p_close ≥ 0.5`; the existing
  opt-in watch tier (`PROTO_TIERS=1`: rule + v1 P ≥ 0.02) stays opt-in. (d) is that design at a fixed 3 % budget, and it is the candidate to
  re-test first when more storms are labelled — as a new pre-registration, with the locked set still closed.
- **Honest out-of-sample skill for the dissertation** (held-out 23 storms, 90 sites, nested LOSO, box-wide):
  - deployed alert rule: **5 / 90 sites = 0.056 [0.01, 0.11]** at a mean 0.43 % of segments flagged (lift 4.8);
  - deployed ranking at a 3 % budget: **15 / 90 = 0.167 [0.08, 0.26]**, chance 0.064, lift 2.6; FSS@300 0.019 (≈ chance);
  - pre-registered but not adopted: rule + learned watch at 3 % budget **26 / 90 = 0.289 [0.19, 0.39]**, lift 4.5 — report it as a
    candidate whose gain (+11 sites) failed the multiplicity-corrected significance test (one-sided P ≈ 0.014, k = 5), not as the model's skill.
  - in-sample (dev) numbers (sep2023 30 / 79 at 3 %) are never the headline.
