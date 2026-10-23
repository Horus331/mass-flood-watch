# Pre-registered evaluation protocol for closure-model changes (v1, fixed 23 Oct 2026)

This protocol applies to every change to the road-closure model from now on: physics, rain input, rules, the learned layer and thresholds.
It implements T1 and §3 of `ROADMAP_research.md`. The scorer is `proto/score_v2.py`. The reference numbers are in `scoring/BASELINE_v2.md`.
Everything below was fixed **before any candidate was scored with it**. If it changes, it becomes v2 with a date, and v2 applies only to
candidates scored after that date.

## 1. Unit and matching (frozen)

- **Labels.** These are the CSVs in `proto/data/labels_<storm>_*.csv` as committed today. If a label file changes, re-score the baseline and
  the candidate on the same files. `--compare` refuses site lists that differ.
- **Strict match.** A label matches a segment when it is within 30 m of one of that segment's road points. Town-level labels are not matched.
  When a run has `matches_<storm>.json`, that published match is used.
- **Site.** Matched labels are joined single-link within 150 m, and each joined group counts once. A site is hit when any of its segments is
  flagged.

## 2. Storm roles (frozen)

| role | storms | use |
|---|---|---|
| development (in-sample) | sep2023 (Leominster), aug2021 (Worcester) | The rules and the tier threshold were built on these. They may be used for tuning. Report them separately. Never pool them into the headline, and never adopt a change on their gains alone. |
| held-out headline (OOS-7) | aug2023, aug2023b, aug2026, jul2021, jul2023, sep2021, sep2022 | Decision set. No parameter may be chosen by looking at their scores. |
| locked test | aug2015, aug2018, aug2020, jul2018, oct2016 (pre-Oct-2020, IEM GaugeCorr) | Opened once, after T3–T6 are frozen. The result is reported whatever it is. |

- **Leave-one-storm-out (LOSO).** Anything fitted to labels is chosen inside the folds. This covers thresholds, `c_clog`, density gates,
  learned weights and tier cut-offs. For each held-out storm *t*, fit or select on the other 8 of the 9 AWS-era storms (dev storms included),
  then predict *t*. When a threshold has to be chosen inside a fold, it is chosen on the other storms of that fold (nested LOSO). Pooled held-out
  scores are made from the fold predictions only.
- **Physics changes with no fitted parameter** are scored directly on all 9 storms.
- **Leakage check.** Leave-one-area-out (Worcester, Leominster, MetroWest and Webster boxes overlap) is reported next to LOSO. It is not part of
  the decision.

## 3. Baseline

- The baseline is the published Turing catalogue (`docs/proto/turing/<storm>_<area>_20m`), scored in `scoring/BASELINE_v2.json`.
- When T0 lands (the parity catalogue in `docs/proto/parity/catalog/`, run at `LF_PARITY=1`), re-score it with `--catalog`. That becomes the
  baseline, recorded with its commit.
- A candidate is always compared on the same commit and the same solver: CPU with CPU, or GPU with GPU.

## 4. Metrics (fixed; all from `score_v2.py`)

**Primary.** Held-out (OOS-7) site recall, box-wide, with the model's top 3 % of segments flagged (ranked by `p_close`, then depth).

**Secondary.** These are always reported and are not part of the decision unless §5 names them.

- Site and label recall at 1, 2, 3, 5 and 10 % flagged and at the rule (`p_close` ≥ 0.5). Each comes with exact chance recall and lift.
- Segment recall.
- FSS on the road network at 100, 300 and 1000 m, with the chance FSS for random flagging at the same share and the "useful" level 0.5 + f₀/2.
- PR-AUC at segment level and site level.
- CSI at segment and site level. It is read only in the complete domain, the Leominster DPW inventory (sep2023, Leominster city). Elsewhere,
  false alarms are undefined.
- Everything is reported both box-wide and inside the reporting towns.
- USGS gauge rise and peak-time error, from `proto/score.py`.

**Uncertainty.** A two-stage cluster bootstrap with 2000 replicates: storms first, then sites within each storm. FSS and PR-AUC are resampled
at storm level only. CIs are 5–95 %. A comparison is paired: the same resamples are applied to the baseline and the candidate.

## 5. Adoption rule

`python proto/score_v2.py --compare BASE.json CAND.json` checks all five conditions. A change is adopted only if all five hold on OOS-7.

1. **Gain.** Pooled site recall at 3 % flagged improves by **≥ +0.05** (about 2 of the 27 sites).
2. **Significance.** The one-sided 95 % lower bound of that gain (paired two-stage bootstrap, 5th percentile) is **> 0**.
3. **Spatial skill.** Pooled FSS at 300 m, at 3 % flagged, **does not drop** (Δ ≥ 0).
4. **No storm left behind.** No held-out storm loses **more than 1 site** at 3 %.
5. **Calibration of the rule.** The pooled chance-corrected lift of the deployed rule (`p_close` ≥ 0.5) is **≥ 0.8 ×** the baseline's, so a
   gain bought by flagging much more is rejected.

**Several variants of one task** (for example, three `c_clog` values tried outside LOSO): use α = 0.05 / *k* in condition 2, where *k* is the
number of variants scored on OOS-7.

**Dev storms.** A drop of more than 2 sites on sep2023 or aug2021 at 3 % must be explained in the write-up. It does not block adoption.

**Process.**

- Every candidate scored on OOS-7 is logged, adopted or not, with its `--compare` output, in `docs/proto/<topic>/`. This is how the drains and
  DCIA negative results were handled.
- Nobody looks at OOS-7 numbers for a variant before the variant's settings are written down in the commit that produces it.
- The locked set is never used in a `--compare` until it is opened (§2).
