# Why the model misses two-thirds of Leominster's damaged roads, and what raises recall

Reproduce with `python proto/recall_study.py all` (about 2 minutes, published data only). Numbers: `recall.json` (headline), `anatomy.json` and `anatomy_leominster_sep2023.csv` (one row per label), `curves.json`, `tiers.json`.

## One-minute summary

- **The 36 % (28 of 78) mixes three different problems.** 50 sites are missed. Their causes split roughly evenly between the labels/matching and the model:
  - **27 of 50 (54 %) are mostly label or matching problems.**
    - 9: the model floods a road within 100 m, but not the one segment the point was matched to.
    - 8: the point is a road-centroid guess, and the same road is flagged within 1.5 km.
    - 10: dam, drainage-system or pavement damage with no water on the road. A depth model cannot represent these.
  - **15 of 50 (30 %) are cheap model fixes.** The model already has a signal there: 10–30 cm on the road, or the may-close / culvert layer fires. These need a second alert tier, not new physics.
  - **8 of 50 (16 %) are real physics misses.** The model is dry: under 10 cm, and nothing flagged within 100 m.
- **The DPW inventory looks different.** 30 of its 54 points are missed. 24 of those 30 lie on one street: Wachusett St, 32 edge-washout points along about 4 km of hillside road, where the model puts 3 cm. That is a real model limit. The model cannot resolve fast gutter and edge flow on a steep street at 20 m. Counted as distinct locations (points within 150 m merged), the DPW recall is 17 of 27 (63 %). For the news/agency sites it is 19 of 57 (33 %).
- **Coordinate quality matters.** Exact coordinates are caught 48 % of the time (11 of 23). Road-centroid coordinates are caught 31 % of the time (17 of 55).
- **Best achievable recall at a sane flagged share.** The pool is all 9 storms, held out: 168 sites. CIs are 5–95 % bootstrap intervals.
  - **About 2 % flagged:** nothing beats the current rule. Recall is about 0.33 pooled and 0.33 for Leominster news.
  - **About 5 % flagged:** nothing beats simply lowering the depth threshold. Recall is about 0.45 pooled and 0.45–0.50 for Leominster.
  - **About 7–9 % flagged:** a two-tier scheme reaches 0.55–0.57 pooled. The tiers are "likely closed" (the current rule) plus "watch" (the learned model's P ≥ 0.02).
    - The default reaches 0.34 at 2.1 %. Lowering the depth rule to the same share reaches 0.49.
    - Held out, Leominster news reaches 49 of 78 (63 %) at 9 % flagged, up from 28 of 78.
    - On the 7 storms no rule was built on, recall is 15 of 29, against 5 of 29 for the default and 9 of 29 for the lowered depth rule.
  - **The price is precision.** Lift (recall divided by flagged share) falls from about 16 to about 7.6, so each flagged segment is worth about half as much as it is now.
- **Tolerant matching (100 m / same road name) is not a fix, only context.** It lifts Leominster to 0.64 at 2 % flagged and 0.84 at 5 %. But chance recall rises with it: the chance-corrected lift drops from about 11 to about 2–3.
- **Implemented:** `PROTO_TIERS=1` in `proto/prototype.py`, off by default. It adds a `tier` field ("likely closed" / "watch") to every segment. The default output is unchanged.

## 1. Miss anatomy, Leominster 11–12 Sept 2023

**Run.** The GPU LISFLOOD run `docs/proto/turing/leominster_sep2023_gpu`, the source of the 36 % / lift 9.45 headline.

**Matching.** News/agency labels use the published run's own strict matches and per-site values (`summary.json → checks.labels_segments.sites`). DPW points are not in that run's label file. They were matched here with the same rule (30 m), using road points rebuilt from `docs/graph_segments.json`. Those rebuilt points keep bridge decks and water cells that the published run drops, so the DPW numbers are approximate.

**Columns in the per-site CSV:**
- peak depth on the matched segment, and the maximum within 50 / 100 / 300 m
- distance to the nearest flagged (p_close ≥ 0.5) and may-close road point
- layer probabilities (may-close, culvert HDS-5, edge, sag)
- coordinate quality, and the distance from the point to the road

**Classes.** Misses are assigned in this order of precedence:

| class | meaning | news/agency (78 matched) | DPW (54) |
|---|---|---|---|
| hit | p_close ≥ 0.5 on the matched segment | 28 | 24 |
| A near-flag | a flagged road within 100 m, but not the matched segment (which-segment / placement / 30 m window) | 9 | 2 |
| B layer / sub-threshold | matched segment 10–30 cm deep, or may-close / culvert / edge / sag ≥ 0.5 | 15 | 7 |
| C location uncertain | road-centroid ("approx") point; same road flagged within 1.5 km | 8 | 0 |
| D not representable | dam, drainage system, retaining wall, buckled pavement, sinkhole, with the model dry | 10 | 0 |
| E model dry | under 10 cm on the segment, no layer, nothing flagged within 100 m | 8 | 21 |
| (not in the 78) | no segment within 30 m (14 labels in the box) | 14 | 0 |

**By label type (news/agency, recall by mechanism):**

| group | recall |
|---|---|
| standing water (flooded / closed / impassable) | 10 of 24 |
| erosion and culverts (culvert failure / washout / bridge) | 13 of 36 |
| non-flood damage | 5 of 18 |

The 50 misses by mechanism group:
- **Standing water (14):** A 4, B 6, C 1, E 3.
- **Erosion / culvert (23):** A 3, B 8, C 7, E 5.
- **Non-flood (13):** A 2, B 1, D 10.

**Where the water is.** For the 50 misses:
- The median depth on the matched segment is 8 cm.
- 30 of the 50 have at least 10 cm of water within 100 m; 9 have at least 30 cm within 100 m; 28 have at least 30 cm within 300 m.
- A flagged segment lies within 100 m for 9 of them, within 200 m for 21, and within 500 m for 37.
- The may-close layer catches 14 of them (42 of 78 caught, against 28), but at 6.4 % of segments flagged, not 2.6 %.

**Fragile matching:**
- Only 1 missed point sits more than 15 m off the road. Points placed off the road are not the problem.
- Approximate (road-centroid) points are 38 of the 50 misses. The labels README warns these can be 0.5–1.5 km off.
- Labels at bridges drop out of the strict match entirely, because the published run removes bridge-deck road points. 14 labels in the box have no 30 m match. Several of them sit in deep model water, so most would probably be hits. Examples:
  - Adams St: 0.57 m
  - Central St downtown: 0.90 m
  - Pleasant St Culvert 2 at Fall Brook: 0.72 m
  - Water St retaining wall: 1.67 m
  - Whitney Field mall lot: 1.47 m

  These labels are excluded from the denominator, so this cuts both ways.
- Clustering inflates both the hit counts and the miss counts. For example, the 49 DPW sites in the 20 m run map to only 22 distinct segment sets.

**What is fixable where (news/agency misses):**

| | sites | share of 50 misses |
|---|---|---|
| better labels or matching (A + C), or not a flood phenomenon (D) | 27 | 54 % |
| cheap model fix: a second tier or a layer already in the code (B) | 15 | 30 % |
| needs new physics (E): mainly small culverts and drainage the 20 m model does not see | 8 | 16 % |

For DPW, 21 of the 30 misses are E, and 20 of those are Wachusett St. That is gutter and edge flow on a steep street. The edge layer (`p_edge`) gives 0 there, because the 20 m model carries about 3 cm of slow water. The other E-class DPW misses are single points on other streets.

## 2. Operating curves (recall vs flagged share)

**Setup:**
- Each storm flags its own top x % of segments by the score. Ties are broken at random, averaged over 5 seeds.
- Recall is at the site level, with strict 30 m published matches.
- Runs: the 20 m runs `docs/proto/turing/<storm>_<area>_20m`. The Leominster 20 m run gives the same 36 % (28 of 78) as the GPU run.
- The learned model is the leave-one-storm-out (LOSO) logistic from `closure_loso.py`.
- In the cells below, the first number is recall and the second is the chance-corrected lift (recall divided by the recall random flagging would get).

| score | Leominster news (78) 2 / 5 / 10 % | Leominster DPW (49) | all 9 storms (168) | 7 never-used storms (29) |
|---|---|---|---|---|
| rule p_close (depth) | 0.32/11.1 · 0.45/6.3 · 0.63/4.5 | 0.39 · 0.43 · 0.49 | 0.32/11.0 · 0.42/6.0 · 0.55/4.0 | 0.14 · 0.28 · 0.41 |
| may-close (overtop) alone | 0.22 · 0.39 · 0.56 | 0.18 · 0.18 · 0.35 | 0.21 · 0.34 · 0.51 | 0.17 · 0.34 · 0.55 |
| union depth OR overtop | 0.33 · 0.47 · 0.61 | 0.18 · 0.39 · 0.49 | 0.27 · 0.43 · 0.55 | 0.17 · 0.28 · 0.41 |
| pluvial union | 0.28 · 0.42 · 0.53 | 0.24 · 0.39 · 0.43 | 0.28 · 0.42 · 0.51 | 0.28 · 0.41 · 0.48 |
| learned (LOSO) | 0.15 · 0.35 · 0.69 | 0.14 · 0.22 · 0.45 | 0.19 · 0.34 · 0.61 | 0.31 · 0.45 · 0.62 |
| hybrid: rule flags first, then learned | 0.33 · 0.44 · 0.69 | 0.35 · 0.43 · 0.47 | 0.32 · 0.44 · **0.62** | 0.21 · 0.45 · 0.62 |
| hybrid: rule, then may-close, then learned | 0.33 · **0.50** · 0.64 | 0.35 · 0.39 · 0.43 | **0.33** · **0.46** · 0.58 | 0.24 · 0.38 · 0.62 |
| *tolerant 100 m matching, rule* (context) | 0.64/2.9 · 0.84/1.9 · 0.94/1.5 | - | other 8 storms: 0.40 · 0.64 · 0.84 | - |

**Reading:**
1. **Top of the list (2 % or less).** The depth rule is the best ranking. Nothing tested improves it. The learned model is worst there.
2. **Middle (about 5 %).** Every rule-first ordering is within about 4 points of the plain rule. That is within noise (see section 3).
3. **About 10 %.** Adding the learned order after the rule's flags gains about 7 points pooled (0.62 against 0.55). Most of the gain is in Leominster news (0.69 against 0.63) and in the never-used storms (0.62 against 0.41).
4. **May-close.** Its 54 % recall in Leominster comes mostly from flagging 2.5 times more segments. At an equal share, may-close is not better than the depth rule in Leominster (for example, 0.39 against 0.45 at 5 %). It is better in the small storms (0.34 against 0.28 at 5 %).

## 3. Two-tier alert scheme, thresholds chosen LOSO

**The tiers:**
- **Tier 1, "likely closed":** p_close ≥ 0.5, the current default, unchanged.
- **Tier 2, "watch":** one family with one threshold t.

**How t is chosen.** For each held-out storm, t is chosen on the other 8 storms only. The criterion is the highest storm-averaged site recall, subject to a storm-averaged total flagged share at or below a budget of 5, 8 or 10 %. Inside a fold, each training storm's learned score comes from a model fitted without that storm and without the held-out storm (nested LOSO).

**The three baselines:**
- **"t1":** the default alone.
- **"eq":** the depth rule relaxed so that each storm flags the same share as the scheme. This is the "just flag more" null.
- **"random":** the same number of extra segments drawn at random.

**Intervals.** These are 5–95 % two-stage cluster bootstrap intervals (storms, then sites; 2000 replicates).

**Fully nested result.** The family is also picked inside each fold ("pick family"). This is the honest number for "choose a scheme from these candidates":

| budget | all 9: recall [CI] | mean flagged | lift | recall of eq | scheme − eq [CI] | 7 never-used | Leominster held out |
|---|---|---|---|---|---|---|---|
| 5 % | 74/168 = 0.44 [0.18, 0.50] | 5.0 % | 8.9 | 0.46 | −0.02 [−0.06, +0.05] | 6/29 (eq 5) | 62/127 at 8.7 % |
| **8 %** | **93/168 = 0.55 [0.40, 0.67]** | **7.4 %** | **7.5** | 0.49 | **+0.065 [0.00, +0.24]** | 14/29 (eq 9) | 71/127 at 9.0 % |
| 10 % | 100/168 = 0.59 [0.40, 0.68] | 8.7 % | 6.9 | 0.59 | +0.01 [−0.05, +0.24] | 14/29 (eq 9) | 78/127 at 12.3 % |

For comparison, the default (tier 1 alone) catches 57/168 = 0.34 [0.14, 0.40] at 2.1 % flagged, with lift 16.0.

**Each family with its threshold chosen LOSO, budget 8 %:**

| watch family | all 9 | flagged | scheme − eq [CI] | P(> eq) | 7 never-used | Leominster |
|---|---|---|---|---|---|---|
| depth ≥ t (= relaxing the rule) | 77/168 = 0.46 | 6.8 % | 0 | - | 8/29 | 61/127 at 6.3 % |
| freeboard ≤ t (overtop) | 88/168 = 0.52 | 7.0 % | −0.02 [−0.06, +0.11] | - | 10/29 | 70/127 at 10.8 % |
| **learned P ≥ t** | **95/168 = 0.57 [0.44, 0.71]** | **7.4 %** | **+0.077 [+0.02, +0.29]** | 0.97 | **15/29** (eq 9, default 5) | 71/127 at 9.0 % (news 49/78, DPW 22/49) |
| may-close OR learned ≥ t | 90/168 = 0.54 | 6.3 % | +0.01 [−0.04, +0.14] | - | 10/29 | 72/127 at 10.5 % |
| may-close OR depth ≥ t | 76/168 = 0.45 | 7.0 % | −0.02 [−0.07, +0.01] | - | 7/29 | 61/127 at 7.1 % |
| all physics layers (may-close, culvert, edge, sag, pluvial ≥ t) | 100/168 = 0.60 | 7.5 % | 0.00 [−0.04, +0.23] | - | 14/29 | 78/127 at 13.4 % |

**Detail for the learned watch tier:**
- LOSO chose t = 0.02 in 8 of 9 folds. The exception is the Leominster fold, where t = 0.0075: without Leominster in training, the model's probability level in Leominster is lower.
- The watch tier adds 38 held-out sites, against 9.1 for the same number of random extra segments.
- Recall gain over the default: +0.23 [0.17, 0.46].
- Lift: 7.6 [5.9, 10.6], against 16.0 for the default.
- Per storm, the held-out flagged share is 3–11 %. It adapts to the storm: 3 % in Jul 2023, 11 % in Ida (Sept 2021), 9 % in Leominster.
- In Leominster itself, the watch tier is not clearly better than lowering the depth threshold to the same 9 %: +0.047 [−0.02, +0.12]. The gain comes from the small storms, where the depth rule has nothing to lower (Millbury, Webster, Elsa).

**Verdict:**
- The two-tier scheme clearly beats the default out of sample on recall: +0.21 to +0.23, with intervals well above zero. It costs 3.5 times the flags, and the lift (recall per flagged share) halves.
- Against the stronger null (just flag more by depth), the gain is positive but small and uncertain: +0.065 fully nested, +0.077 for the learned-watch family. The lower bounds are 0.00 and +0.02.
- At a 5 % budget, no tested scheme beats a lowered depth threshold.
- The learned-watch family is the best family post hoc, and it is the one the nested selection picks in Leominster and in the small storms. It was implemented because it is the only family whose interval against "eq" excludes zero.
- **Implemented in `proto/prototype.py` behind `PROTO_TIERS=1` (default off):**
  - `tier` = "likely closed" if p_close ≥ 0.5; else "watch" if `p_close_ml` ≥ `TIER_WATCH_P` = 0.02. `p_close_ml` comes from the all-storm logistic, `docs/proto/ml/closure_lr_all.json`, through the `closure_ml.on_rows` hook.
  - A "watch" reason is appended to `why`.
  - Scored as variant `tiers` in `checks.labels_segments.variants`.
  - `segments_watch` and `km_watch` are added to `summary.json`.
  - If the learned model fails, the watch tier is left empty, with the error in `checks.rules.tiers_error`.
  - With the final all-storm model, t = 0.02 flags 2.7–10.6 % per storm (in sample). Leominster: 10.6 %.

## Caveats

- **Few storms.** The 8 non-Leominster storms have only 41 sites, so every pooled interval is wide. "Never-used" means no rule was built on those storms. The learned model is still LOSO everywhere.
- **Clustering.** Site recall counts every label point. Clusters such as Wachusett St (32 DPW points) and Granite St (4 culverts) weight a few roads heavily.
- **Selection of the implemented family.** The chosen family (learned watch) is the best of the 6 families after the fact. The "pick family" row is the estimate free of that selection.
- **Matching.** The DPW anatomy and the tolerant matching use road points rebuilt without the run's water mask or bridge-deck removal, so they are approximate. The news/agency anatomy uses the published matches exactly.
- **Files not touched.** `sim/colab/w9_lisflood.py` (the runoff loss, being edited elsewhere) was not touched. Fixing class E (the model-dry sites) probably needs the loss and drainage work in `docs/proto/urban/FINDINGS.md`, not a new threshold.
