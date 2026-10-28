# Latent true-flooding label model: pre-registration (PROTOCOL v2, 28 Oct 2026)

This file was committed before any held-out-23 or District 4–6 score of a latent-model candidate was computed. Code: `proto/latent_label.py`
at this commit. Results will go to `LATENT.md` whatever they are.

## Model (fixed)

Unit: segment *i* in storm *t* (the 25 non-locked parity storms, `docs/proto/parity/catalog/<storm>_<area>_20m`, features universe of `score_v2`).

- Latent state: Z ~ Bernoulli(π), logit π = b_o·o + b_0 + b·h.
  - o = 1.7 · clip((peak depth − 0.30) / 0.10, −6, 6). This is the deployed rule's probit, put on the logit scale, and it is the offset.
  - h = 11 standardized hazard terms: log1p hours > 15 cm, log1p area, log1p HAND, log1p slope, p_culvert, p_overtop, p_sag, p_edge, log1p peak-1 h
    rain, log1p stream distance and log1p segment length.
- Sources: s ∈ {NWS (LSR + Storm Events), news, WX1BOX, MassDOT_crash, SeeClickFix, DPW, MA_state, Waze, MassDOT_closure}. The family rules
  are `label_tiers.family`; `waze_*` and `massdot_closure_*` files are their own families. A report is a strict 30 m match, using
  `score_v2.load_run` on every source file.
- Observation: Y_s ~ Bernoulli(Z·d_s + (1 − Z)·f_s), but only where s **operates**. Elsewhere Y_s is missing (unknown, not 0).
  - NWS, news, WX1BOX and MassDOT crashes operate everywhere. Crash data were fetched for all 25 storms.
  - SeeClickFix operates in towns that had any SeeClickFix issue in the storm window (`obs/round3/scf_window_<storm>.json`).
  - DPW operates only in Leominster city, sep2023.
  - MA_state, Waze and MassDOT_closure operate box-wide in storms where they have rows.
  - Any report found outside a source's assumed domain marks that source as operating there.
- Detection: logit d_s = a_s + g·r, with r = (major road, log1p AADT, town activity). Town activity is log1p of the mean matched reports per
  storm in the town over the other storms in the fit. g is shared across sources. DPW gets an intercept only.
- Priors: b_o ~ N(1, 0.3), b_0 ~ N(0, 3), b ~ N(0, 1); a_s ~ N(−1.5, 1.5); a_DPW ~ N(2.2, 0.5), i.e. d ≈ 0.90, the complete-inventory
  assumption; g ~ N(0, 1); f_s ~ Beta(1, 2000).
- Fit: MAP-EM until max |Δq| < 1e-5 (at most 300 iterations). The E-step gives q = P(Z = 1 | Y, x). The M-step is a soft-label logistic for π,
  a q-weighted logistic for d, and a closed-form Beta-MAP for f.
- CIs come from a storm-cluster bootstrap of the all-storm fit: 100 replicates, warm-started, 90 %.

## Candidates scored on held-out 23 (k = 2)

- **L1 (candidate).** The ranking is the leave-one-storm-out π(x). For held-out storm *t*, EM is fitted on the other 24 non-locked storms, so
  no label of *t* is used.
- **N0 (control).** The same π design and priors, fitted by ordinary MAP logistic on y = any matched report from any source (unreported =
  dry), with the same folds. It separates the effect of the label model from the effect of the extra features.
- **Score mapping.** Candidate p_close is the rank of π. The top n_rule segments, where n_rule is the size of the deployed rule's
  `p_close ≥ 0.5` set in that storm, get 0.999, 0.998, … The rest get 0.499, 0.498, … This keeps the candidate's alert tier at the
  deployed tier's size.
- **No label-chosen hyperparameter, threshold or tier size exists.** The nested-LOSO requirement is therefore met trivially: priors and
  features are fixed here.
- **Decision.** `score_v2.py --compare BASE L1 --protocol v2 --k 2` (§5a, ranking route, default label setting, i.e. the decision labels
  `labels_*`). BASE = the parity catalogue re-scored now with the same code and labels (the round-2 reference `obs/round2/score_round2.json`
  is quoted next to it). Nothing is wired into defaults unless L1 passes all five conditions.
- **Secondary, reported but not part of the decision:** N0 vs BASE (same rule, k = 2), L1 vs N0, the OOS-7 / NEW16 / dev sub-pools, PR-AUC
  and FSS@300.

## Calibration (b)

Leominster city, sep2023 (the DPW domain). The sep2023-held-out π (fit without sep2023, hence without the DPW anchor) is compared with the
observed flooded set: segments with any matched report from any source. The quantities are expected count vs observed, Brier, Brier skill
vs a constant, and quintile reliability. The same is reported for N0, for the in-sample all-storm fit and for the physics p_close.

## Districts 4–6 (c), test only

The all-25-storm L1 and N0 fits are frozen and applied to the r1 transfer runs (features from the transfer pipeline; OSM roads), with the same
rank mapping. The comparison is pooled 3 % site recall vs the frozen baseline, with a paired two-stage bootstrap 90 % CI. Nothing is
fitted, tuned or `--compare`d on these storms (PROTOCOL "Transfer test").

## Seen before this commit (disclosed)

- Synthetic selftest.
- Per-source report counts and overlaps.
- One in-sample all-storm fit without bootstrap (parameters only, no ranking score).
- A mechanics check of the rank mapping on the dev storm sep2023.
- The in-sample fit already shows that the Leominster DPW layer is **not** near-complete for "flooded" at the segment level. It matches 10
  of the 54 MA_state segments and 8 of the 30 WX1BOX segments in Leominster, and EM pulls d_DPW from the 0.90 prior to ≈ 0.24. The prior is
  kept as stated (not changed after seeing this), and the conflict is reported.
