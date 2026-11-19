# Supplementary tables (CSV), Paper 1

Copied from the scoring outputs; no new numbers. One row per storm.

**S2a_district3_heldout.csv**: the 23 held-out District 3 storms (parity runs, round-2 labels), from `obs/round2/score_round2.json`.
**S2b_districts456_transfer.csv**: the 81 storms of Districts 4–6, frozen settings, from `transfer/r1/score_d456.json` (branch `transfer-d456`).

| Column | Meaning |
|---|---|
| storm, run, role | storm id, model run folder, role in the protocol (heldout / heldout-new / d456) |
| segments | road segments in the storm's box |
| sites | documented flood sites matched to the road graph |
| rule_flag_share, rule_site_hits | share of segments the fixed 0.30 m rule flags, and sites it catches |
| pr_auc | precision–recall area over segments (labelled segments as positives) |
| hits_topXpct | sites caught when the top X % of segments (ranked by closure probability, ties by depth) are flagged; fractional where equal scores straddle the cut (expected value over the ties) |
| chance_topXpct | expected share of sites caught by flagging the same share at random |

Pooled recall = sum of hits / sum of sites (District 3: 20 / 98 = 0.204; Districts 4–6: 104.8 / 498 = 0.210 at 3 %).

**S2c_bias_by_storm.csv**: gauge-rise bias and rain per storm, all non-locked District 3 storms (`parity/bias_by_storm.json`): number of
gauges, mean observed rise (m), mean signed rise error (model − observed, m), median modelled/observed ratio, box mean and 99th-percentile
storm rain (mm), maximum segment peak-hour rain (mm), sites, top-3 % hits, chance.

**S2d_forecast_ensemble.csv**: forecast ensemble per storm and lead (`forecast/ensemble_ci.json`): sites, hits of the newest single cycle
and of the 2-of-8 rule.
