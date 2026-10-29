# Latent true-flooding label model (28 Oct 2026)

**Plain verdict.** Under PROTOCOL v2 the candidate ranking (L1) passes all five adoption conditions on the held-out 23 storms. Its 3 %
site recall is 0.204 → 0.327 (+0.122, lower bound +0.017 at α/k = 0.025). The pre-registered **naive control N0** uses the same features
and folds but treats unreported as dry. It passes too, and by slightly more (+0.133). So the ranking gain comes from the **extra learned
hazard terms** (mainly peak-1 h rain and segment length), **not from the latent label model**. The label model's real contribution is
**calibration**. On the Leominster complete-inventory domain, held out, it predicts 155 flooded segments against 104 observed (naive: 16,
which is 6.6× too few), with Brier skill 0.14 against 0.00. Two more results limit what can be claimed:

- **The DPW layer is not complete.** EM puts its detection near 0.24, not the assumed 0.90.
- **The ranking gain does not show up clearly in Districts 4–6.** The change there is +0.02 with a CI of −0.017 to 0.060.

**Nothing has been wired into the defaults.** See §5 for why.

Pre-registration: `PREREG.md` (main commit 9fc09f0e), committed before any held-out score. Code: `proto/latent_label.py`.

## 1. Model

Unit: segment *i*, storm *t*. The data are the 25 non-locked parity storms: 139,938 segment-storms with 423 reported segment-storms
(any source).

```
Z_it ~ Bernoulli(π_it)          logit π_it = b_o·o_it + b_0 + b·h_it
o_it = 1.7·clip((peak depth − 0.30 m)/0.10, −6, 6)              (deployed rule's probit on the logit scale, the offset)
Y_its | Z ~ Bernoulli(Z·d_its + (1 − Z)·f_s)                    only where source s operates; elsewhere Y is missing, not 0
logit d_its = a_s + g·r_it  (DPW: a_s only)                     r = (major road, log1p AADT, town reporting activity)
```

- **Hazard terms h (11, standardized).** log1p hours > 15 cm, area, HAND, slope, p_culvert, p_overtop, p_sag, p_edge, log1p peak-1 h rain,
  stream distance and segment length.
- **Town activity.** log1p of the mean number of matched reports per storm in the town, counted over the *other* storms in the fit.
- **Sources** (`label_tiers.family`, strict 30 m match through `score_v2.load_run`):
  - Operate everywhere: NWS (LSR + Storm Events), news, WX1BOX and MassDOT water-surface crashes.
  - SeeClickFix: towns with any SCF issue in the storm window.
  - DPW: Leominster city in sep2023 only.
  - MA_state, and future `waze_*` / `massdot_closure_*` files: box-wide in storms where they have rows. The schema is ready, and these
    sources are picked up automatically when the importer writes them.
- **USGS gauges** are not used as labels. They act only through the physics features.
- **Priors.**
  - π model: b_o ~ N(1, 0.3), b_0 ~ N(0, 3), b ~ N(0, 1).
  - Detection: a_s ~ N(−1.5, 1.5); a_DPW ~ N(2.2, 0.5), i.e. d ≈ 0.90 (the complete-inventory assumption); g ~ N(0, 1).
  - False reports: f_s ~ Beta(1, 2000).
- **Fit.** MAP-EM. The E-step is
  q = π·∏_s d^y(1 − d)^(1 − y) / [π·∏_s d^y(1 − d)^(1 − y) + (1 − π)·∏_s f^y(1 − f)^(1 − y)].
  The M-step is a soft-label logistic for π, a q-weighted logistic for d and a closed-form Beta-MAP for f.
  - All-storm fit: 210 iterations to max |Δq| < 1e-5.
  - Several LOSO folds stopped at the 300-iteration cap, with tiny remaining changes.
- **CIs.** Storm-cluster bootstrap of the all-storm fit, 90 %. **Deviation from PREREG:** 30 replicates of at most 100 warm-started EM
  iterations instead of 100 full replicates (run time ≈ 3 min per replicate on 2 shared cores). The CIs are therefore approximate.
  They are descriptive only and do not enter the decision.
- **Selftest.** `python proto/latent_label.py selftest` runs on synthetic data and recovers every d_s within ±0.01, f, g and b.

## 2. Source estimates (all-storm fit; `fit_all.json`)

| source | segment-storms operating | reported | d at mean r [90 % CI] | mean d over likely-flooded rows [CI] | f (false-report rate) |
|---|---|---|---|---|---|
| NWS (LSR + Storm Events) | 139,938 | 222 | 0.060 [0.003, 0.072] | 0.080 [0.008, 0.103] | 1.3e-4 [0, 1.5e-3] (≈ 19 of 222 reports) |
| news | 139,938 | 43 | 0.012 [0.003, 0.025] | 0.017 [0.005, 0.061] | ≈ 0 |
| WX1BOX | 139,938 | 43 | 0.012 [0.001, 0.036] | 0.017 [0.001, 0.080] | ≈ 0 |
| MassDOT water crash | 139,938 | 15 | 0.005 [0.001, 0.005] | 0.007 [0.003, 0.009] | ≈ 0 |
| SeeClickFix | 36,378 | 49 | 0.032 [0.001, 0.069] | 0.052 [0.006, 0.099] | 3.8e-4 [0, 1.8e-3] (≈ 14 of 49) |
| Leominster DPW | 1,521 | 29 | **0.24 [0.18, 0.26]** (prior 0.90) | 0.24 | ≈ 0 |
| MA state damage table | 4,542 | 54 | 0.17 [0.05, 0.18] | 0.20 [0.17, 0.24] | ≈ 0 |

**Detection slopes g** (per SD), with 90 % CIs:

- log AADT: **+0.51 [0.22, 0.72]**. Busy roads get reported.
- town activity: +0.15 [−0.04, 0.54].
- major road: −0.06 [−0.12, 0.03].

**Prevalence π.**

- The physics offset is shrunk hard: b_o = 0.10 [−0.04, 0.23] against its N(1, 0.3) prior.
- The strongest terms are peak-1 h rain (+0.84 [0.46, 1.70]), segment length (+0.86 [0.49, 1.35]) and slope (−0.35 [−0.48, −0.23]).
- Implied flooded segment-storms: Σq = 2,547 [1,376, 3,667], against 423 reported. About **1 in 6 flooded segment-storms is reported by any
  source.**

**Reading.** Most storms have a single source (NWS), so overlap between sources ("capture-recapture") is informative only in sep2023, and
weakly in aug2021, aug2023, aug2026 and jul2023c. The split between prevalence and detection rests mostly on those storms, on the DPW
anchor and on the priors. The absolute d values for NWS, news and WX1BOX are therefore **weakly identified** (wide CIs). Their ratios and the
AADT effect are firmer.

**DPW is not near-complete for "flooded".** In Leominster:

| source | segments | of which also DPW |
|---|---|---|
| MA_state | 54 | 10 |
| WX1BOX | 30 | 8 |
| news | 20 | 7 |

The data override the strong 0.90 prior. The likely reason is that the DPW layer is a *damage* inventory (washouts, headwalls: 54
points, 29 segments), not a record of water on the road. Strict 30 m matching of approximate coordinates also lowers the overlaps, which
biases capture-recapture toward a higher prevalence. The complete-domain assumption used by `score_v2.COMPLETE` (CSI) should be read with
this in mind.

## 3. Outputs

- `posterior/<storm>.csv`: per segment-storm, π, the posterior **q = P(Z = 1 | reports)** (a better "truth" estimate than the raw labels),
  P(report | flooded) and the reporting sources. Rows with q ≥ 0.05 or any report are kept.
- `reporting_bias.png` and `reporting_bias_towns.json`: P(any source reports | flooded) per segment-storm, overlaid for all 25 storms, and
  the town means. Leominster has the highest (0.28; DPW plus the state table). Fitchburg is 0.18. Rural Rutland, Oakham and Ashby are about
  0.06. A flood on a quiet road in a quiet town is about **4–5× less likely to be in the labels.**

## 4. Results

### (a) Ranking, held-out 23, PROTOCOL v2 §5a, k = 2

Default decision labels. 98 sites. BASE was re-scored on the same code and labels, and equals `obs/round2/score_round2.json`
(0.204, 98 sites).

| | 3 % site recall [90 % CI] | lift | FSS@300 at 3 % | PR-AUC seg / site | rule-size tier recall (lift) |
|---|---|---|---|---|---|
| BASE (parity p_close) | 0.204 [0.104, 0.303] | 3.10 | 0.023 | 0.008 / 0.010 | 0.092 (6.4) |
| **L1 latent π (LOSO)** | **0.327 [0.224, 0.431]** | 4.96 | 0.025 | 0.018 / 0.028 | 0.122 (8.6) |
| N0 naive π (LOSO, control) | 0.337 [0.233, 0.442] | 5.12 | 0.025 | 0.018 / 0.028 | 0.133 (9.3) |

`--compare` (`compare_L1_vs_base.json`, `compare_N0_vs_base.json`):

| | Δ recall | lower bound (α = 0.025) | ΔFSS@300 | worst storm | tier lift | adopt |
|---|---|---|---|---|---|---|
| L1 | +0.122 | +0.017 | +0.002 | −1 site (jul2021b, jun2020) | 8.6 ≥ 0.8 × 6.4 | **all 5 pass** |
| N0 | +0.133 | +0.022 | +0.002 | −1 site | 9.3 | all 5 pass |

**Sub-pools:**

| | OOS-7 (40 sites) | NEW16 (58 sites) | dev2, in-sample (91 sites) |
|---|---|---|---|
| BASE | 0.275 | 0.155 | 0.363 |
| L1 | 0.400 | 0.276 | 0.484 |
| N0 | 0.400 | 0.293 | 0.495 |

No dev storm lost sites: sep2023 went 30 → 40 and aug2021 went 3 → 4.

**L1 vs N0.** The two rankings are almost the same: equal on OOS-7, and N0 is 1 site ahead on NEW16. With prevalence about 2 %, the label
model mostly rescales π (up by about 6×). Within a storm it barely reorders segments, so it **does not improve ranking**.

**Caveat: length budget.** The 3 % budget counts segments, not road length. Both learned rankings favour long segments (log length is one
of the two largest coefficients). They flag on average **8.6 % of the road length against 6.1 % for BASE** in the top 3 %. Part of the
recall gain is therefore bought with more road per flag. FSS (which is length-weighted) did not drop, so condition 3 holds, but the
chance-recall and lift in `score_v2` are per segment and do not correct for this.

### (b) Calibration in the complete domain

Leominster city, sep2023: 1,521 segments, 104 with a report from any source.

| prediction | expected | obs / exp | Brier | Brier skill vs constant | top quintile pred → obs | bottom quintile pred → obs |
|---|---|---|---|---|---|---|
| **L1, LOSO** (fit without sep2023, so no DPW anchor) | 155 | 0.67 | 0.055 | **+0.14** | 0.28 → 0.24 | 0.03 → 0.003 |
| L1, in-sample | 161 | 0.65 | 0.053 | +0.16 | 0.32 → 0.25 | 0.02 → 0.003 |
| N0, LOSO | 16 | **6.6** | 0.064 | 0.00 | 0.04 → 0.25 | 0.001 → 0.003 |
| physics p_close | 66 | 1.57 | 0.065 | −0.02 | 0.21 → 0.23 | 0.001 → 0.016 |

The latent π is the only one of the four predictions with Brier skill (+0.14 against 0.00 for N0 and −0.02 for physics) and with a monotone
quintile reliability. It over-predicts the *reported* count by 1.5×. That is consistent with §2: DPW plus the others are themselves
incomplete. The naive model's probabilities are about 6× too small, which is what treating "no report" as "dry" does.

### (c) Districts 4–6 (test only)

Frozen all-storm fits, 81 storms, 498 sites, OSM roads.

| | 3 % recall [CI] | lift | FSS@300 at 3 % | rule-size tier recall (lift) |
|---|---|---|---|---|
| BASE | 0.210 [0.168, 0.253] | 2.46 | 0.017 | 0.036 (6.7) |
| L1 | 0.231 [0.185, 0.277] | 2.70 | 0.010 | 0.028 (5.2) |
| N0 | 0.229 [0.183, 0.274] | 2.67 | 0.010 | 0.030 (5.6) |

Paired Δ 3 % recall: L1 +0.020 [−0.017, +0.060], N0 +0.018 [−0.019, +0.058]. The direction matches District 3, but it is about a sixth of
the District 3 gain, not significant, and comes with lower FSS and lower tier lift. On the evidence so far the District 3 gain does not
transfer convincingly.

## 5. Decision and what to do next

- **Not wired into defaults.** L1 formally passes PROTOCOL v2 §5a. But (i) the pre-registered control shows the gain is not due to the
  latent label model, (ii) part of it is a length-budget effect the metric does not correct for, and (iii) the gain is not confirmed in
  Districts 4–6. Adopting a learned ranking layer (the N0/L1 feature set) is the owner's call. A fair version would first be re-checked at
  an equal road-length budget, as a new pre-registration.
- **Use of the label model.** Use the posterior q (`posterior/`) and π as the calibrated "truth" and probability layer: expected counts,
  reporting-bias maps, and soft labels for any future learner. Do not use it as a ranking improvement.
- **Waze and MassDOT closures** will add overlapping sources across many storms. That is what the model needs to separate detection from
  prevalence outside sep2023, so rerun `cache → fit → loso → score` once those files land. This would be a new pre-registration, because
  the labels change.
- **The DPW "complete domain"** should be described as complete for damage, not for flooding.

Reproduce: `LATENT_SCRATCH=<dir> python proto/latent_label.py cache | fit | loso | write-runs | score`, then
`LATENT_D456_SRC=<transfer r1 with features_*.csv.gz> python proto/latent_label.py d456`. Results are in `results.json`.
