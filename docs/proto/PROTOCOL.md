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

---

# PROTOCOL v2 (fixed 23 Oct 2026, before any candidate was scored with it)

v1 above stays as written and still governs every candidate scored before this date (drains, DCIA, learned v2, pluvial). v2 applies to
every candidate scored from now on. What changed and why: the label expansion (`obs/LABELS_EXPANSION.md`) and the 16 new parity runs
(`scoring/BASELINE_v2_expanded.md`) grew the held-out pool from 7 storms / 32 sites to 23 storms / 90 sites. v1's +0.05 gain was sized for
~27 sites; on 90 sites the same rule is both coarser per site and easier to clear by noise in one storm, so the decision set and the rule are
re-sized together. §1 (unit and matching), §3 (baseline: the parity catalogue `docs/proto/parity/catalog/`, scored in
`scoring/BASELINE_v2_expanded.json`, commit 1258b8ee) and §4 (metrics, bootstrap) are unchanged.

## v2 §2. Storm roles

| role | storms | use |
|---|---|---|
| development (in-sample) | sep2023, aug2021 | Unchanged from v1: may be used for tuning, reported separately, never pooled into the headline, never adopted on alone. |
| **held-out decision set ("held-out 23")** | OOS-7 (aug2023, aug2023b, aug2026, jul2021, jul2023, sep2021, sep2022) + NEW16 (may2018, aug2018b, sep2018, sep2018w, sep2018m, sep2018b, jul2019, aug2019, sep2019, jun2020, jun2020b, aug2020b, jul2021b, jul2023b, jul2023c, jul2023d) — 90 sites | Decision set. No parameter may be chosen by looking at their scores. OOS-7 and NEW16 are still reported as sub-pools. |
| locked test | aug2015, aug2018, aug2020, jul2018, oct2016 | **Unchanged and still locked.** Not run, not scored, not used in any fold. `score_v2.compare` refuses an input that contains one. |

- **"Small" storms** (`catalog.json`: may2018, aug2018b, sep2018w, aug2019, sep2019, aug2020b, jul2023b) and every other storm with < 3 sites
  **are included in all pooled metrics and in the bootstrap**. The per-storm loss rule (condition 4) applies only to storms with ≥ 3 sites,
  because with 2 sites a one-site loss is half the storm and is noise.
- **LOSO.** Anything fitted to labels is fitted inside the folds over **all 25 non-locked storms** (dev storms included): for held-out storm *t*
  fit on the other 24; thresholds or tier sizes chosen inside a fold are chosen on that fold's training storms only (nested LOSO). Pooled
  held-out scores are made from fold predictions only.

## v2 §5. Adoption rule

`python proto/score_v2.py --compare BASE.json CAND.json --protocol v2 --k K [--level share|rule]` (`score_v2.ADOPT_V2`).

**§5a Ranking route** (default; every candidate). Adopted only if all five hold on held-out 23, box-wide:

1. **Gain.** Pooled site recall at 3 % flagged improves by **≥ +0.04** (≈ 3.6 of 90 sites).
2. **Significance.** The one-sided lower bound of that gain (paired two-stage bootstrap, 2000 replicates, the **α / k** percentile, α = 0.05,
   *k* = number of variants scored on held-out 23 in the same pre-registration) is **> 0**.
3. **Spatial skill.** Pooled FSS at 300 m at 3 % flagged does not drop (Δ ≥ 0).
4. **No storm left behind.** No held-out storm **with ≥ 3 sites** loses more than 1 site at 3 %.
5. **Calibration of the alert tier.** The pooled chance-corrected lift of the candidate's alert tier (its `p_close ≥ 0.5` set) is
   **≥ 0.8 ×** the deployed depth rule's.

**§5b Alert-tier route** (only for a candidate that changes the alert tier and not the ranking, e.g. a new threshold; `--level rule`).
Conditions 1–5 are applied to the tier instead of the top 3 %: tier site recall gain ≥ +0.04 with lower bound > 0 at α / k, tier FSS@300 not
lower, no ≥ 3-site storm loses > 1 tier site, tier lift ≥ 0.8 × the rule's — **plus**
6. **Budget cap.** The candidate's mean held-out tier share is ≤ the deployed rule's mean share on the dev storms (where the 0.30 m rule was
   calibrated; 1.65 % on the parity baseline). A tier that buys recall by flagging more than the rule does where it works is rejected.

A §5b pass makes the candidate the alert tier; it says nothing about ranking skill.

**Dev storms.** Unchanged: a drop of more than 2 sites at 3 % on sep2023 or aug2021 must be explained; it does not block adoption.

**Process.** Unchanged from v1 (log every candidate with its `--compare` output; settings committed before any held-out-23 number; the locked
set is never used in a `--compare`). The honest out-of-sample skill to quote is always the held-out-23 pooled number of whatever is deployed,
with its CI.

---

# Transfer test (Districts 4–6), pre-registered 25 Oct 2026

Fixed and committed **before any District 4–6 storm was run or scored**. Agreed with the advisor: District 3 stays the case study and the
deployed product. Storms in MassDOT Highway Districts 4, 5 and 6 (MetroWest / North Shore, SE MA / South Shore, Boston metro) are used
**only** as independent test storms for the frozen District 3 model. Nothing is retuned on them. They are not part of the v2 decision set
and never enter a `--compare`, a LOSO fold or any fit. The District 3 locked storms (§2) stay locked and are not touched.

## T-1. Frozen model (exactly as deployed / baselined on 25 Oct 2026)

- **Physics.** The clean CPU parity baseline (`parity/BASELINE.md`): `sim/colab/w9_lisflood.py` unchanged, LISFLOOD-FP 8.2 on CPU (Actions),
  `LF_PARITY=1`, `LF_LOSS=cn` (AMC II), `LF_CN_SCALE=0.88`, `LF_INFIL_MMH=2`, `LF_QOUT=1`, `LF_VOUT=1`, 20 m grid, every other `LF_*` at its
  default. Statewide inputs from the same sources as District 3 (HF `data/dem10`, `nlcd10`, `soils30`, `channels30`, `docs/network/crossings_all.json`
  which covers the whole state, MRMS: AWS Pass2 from 14 Oct 2020, IEM GaugeCorr before, as w9 already does).
- **Closure rule.** `proto/prototype.py` unchanged and at its defaults: `p_close = Φ((road depth − 0.30 m) / 0.10 m)`, the deployed rule is
  `p_close ≥ 0.5`; bridge-deck and Interstate-crest handling as for District 3 (`docs/network/nbi_ma.json` is statewide).
- **Watch tier.** Unchanged: `prototype.TIER_WATCH_P = 0.02` on the all-storm logistic `docs/proto/ml/closure_lr_all.json`
  (watch = `p_close < 0.5` and `p_close_ml ≥ 0.02`; the "rule + watch" set is scored as a secondary tier).
- **The one unavoidable difference: the road network.** `docs/graph_segments.json` (MassDOT road inventory) covers District 3 only. For the
  test boxes the segments come from OpenStreetMap (Overpass, motorway … residential + links), split at junctions and at ~1 km like the
  District 3 graph, with the District 3 class convention (2 = Interstate, named `I-nn`; 1 = other numbered US / MA route; 0 = the rest).
  AADT is a class default (it does not enter `p_close`, the ranking or any metric). **Control:** two District 3 held-out storms (sep2021
  Worcester, aug2023 MetroWest) are rerun with the same frozen settings and scored twice, once on `graph_segments.json` and once on OSM roads
  built the same way, so the effect of the road source alone is measured. The control is reported; nothing is adjusted on it.

## T-2. Storm selection (the catalogue `obs/catalog_d456.json`, `obs/CATALOG_D456.md`)

- **Where.** MassDOT Highway Districts 4, 5, 6 from the MassGIS `MassDOT_Highway_Districts` polygons (town lists only if the polygons cannot
  be read). A storm's box centre and all of its scored label sites must lie in Districts 4–6.
- **When / rain.** 2018-01-01 … 2026-10-24, MRMS hourly QPE available for the whole window (AWS Pass2 or IEM GaugeCorr / Pass2).
- **Kind (scope).** Flash / pluvial and riverine **rain** floods only. Excluded: coastal surge, tidal or wave flooding (a storm whose
  reports are mostly coastal is dropped; a single report whose text names tide / surge / ocean / waves / seawall / coastal flooding is
  dropped), snowmelt and ice jams (reports or narratives naming snow / ice / melt), and broken water mains.
- **Sources.** NWS Local Storm Reports (BOX, IEM archive), NOAA NCEI Storm Events, Boston 311 requests whose type or text is flooding
  (Boston open data, kept only inside storm windows), SeeClickFix issues in District 4–6 towns inside storm windows, and news. Every label
  row is a road-level report with its source URL and a short verbatim quote, in the `proto/data/labels_<id>_<area>.csv` schema, geocoded with
  OpenStreetMap as in the District 3 pipeline (`proto/label_geocode.py`). Reports without a street-level location stay `town` and are not
  matched (PROTOCOL §1). Basement-only, private-property and water-main reports are not road labels.
- **Inclusion.** **≥ 3 road-level sourced sites** (non-`town` coordinates, after the 150 m site clustering) inside one 20 × 20 km box.
  Box = the 1 km-aligned 20 × 20 km EPSG:26986 square holding the most such sites (tie: the cluster closest to the box centre), as for the
  District 3 catalogue. A box may not overlap a District 3 catalogue box of the same date. One day can give two storms if two separate boxes
  each pass. Window: `t0` = first report − 7 h (floored to the hour), `hours` = max(18, last report − t0 + 5 h), as in District 3.
- **Target** 15–25 storms and 150+ sites if the record supports it; the count actually found is reported whatever it is. Storm ids are
  `<mon><yyyy><letter>` not used by any District 3 storm.

## T-3. Metrics (all from the frozen scorers; scored **once**)

`proto/score_v2.py` (pool `d456`, box domain primary, towns domain secondary; strict 30 m match, 150 m sites, 2000-replicate two-stage
bootstrap, 90 % CIs) and `proto/score.py` for gauges. Reported per storm and pooled:

1. **Site recall at the deployed rule** (`p_close ≥ 0.5`) with its share, exact chance and **lift**.
2. **Site recall at 3 % flagged** (top 3 % by `p_close`, then depth) with chance and **lift** — the primary number.
3. **FSS at 300 m** (road network), at the rule and at 3 %, with chance FSS and the useful level 0.5 + f₀ / 2.
4. **Gauges:** USGS stage rise error and peak-timing error (`score.py`: mean abs rise error, bias, gap-aware peak timing).
5. Secondary: the rule + watch tier (recall, share, lift), recall at 1 / 2 / 5 / 10 %, PR-AUC, towns domain.

**Comparison** is with the District 3 held-out results on the same parity physics: held-out 23 after label round 2
(`obs/LABELS_ROUND2.md`, `obs/round2/score_round2.json`: 98 sites, rule recall 0.092 lift 6.4, 3 % recall 0.204 [0.104, 0.303] lift 3.1,
FSS300 at rule 0.051) and the gauge errors of `scoring/BASELINE_v2_expanded.md` / `parity/BASELINE.md`.

**Verdict rule (fixed now).**
- *Transfers* — the pooled District 4–6 3 % lift has a 90 % CI lower bound > 1 (skill above chance) **and** the pooled 3 % site recall is not
  below the District 3 held-out-23 lower bound (0.104).
- *Partial transfer* — the first condition holds, the second does not (ranking skill survives but at a lower level).
- *Does not transfer* — the 3 % lift CI includes 1.
- The rule-level recall / lift, FSS and gauge errors are reported next to the verdict and described in plain words; they do not change it.

**Process.** The catalogue (storms, boxes, windows, labels) is committed before any test run. Runs use `.github/workflows/` on CPU with
exactly the settings above and commit once per workflow run to `docs/proto/transfer/<run>/`. If a run fails for a technical reason
(download, timeout) it is rerun unchanged; no storm is dropped or re-boxed after its result is seen. Results go to
`docs/proto/transfer/TRANSFER.md` whatever they are.
