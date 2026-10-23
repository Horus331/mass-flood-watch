# Scoring v2 on the expanded storm set (parity baseline, 25 storms)

**Plain summary.**
- **Statistical power.** The held-out pool grows from **7 storms / 29 sites** (the OOS-7 parity baseline in `BASELINE_v2_parity.md`) to **23 storms / 90 sites** (OOS-7 plus the 16 label-expansion storms). That is 3.1 times as many held-out sites. The 90 % CI on pooled site recall at 3 % flagged narrows from [0.00, 0.34] (width 0.34; 29 sites) to [0.08, 0.26] (width 0.18). OOS-7 itself now has 32 sites, because aug2026 gained 3 sites from the news-sourced label rows.
- **Out-of-sample skill holds only as weak ranking skill. The deployed rule does not transfer to the new storms.**
  - **The rule (p_close ≥ 0.5)** catches **1 of 58** sites on the 16 new storms. It flags a mean of only 0.23 % of in-box segments; on OOS-7 that figure is 0.91 %.
  - **At a fixed 3 % flagged share**, the new storms give **9 / 58 = 0.16** (chance 0.065, lift 2.4, CI [0.06, 0.26]). That is in line with OOS-7: 6 / 32 = 0.19, lift 2.9. Pooled over all 23 held-out storms: **15 / 90 = 0.17**, lift 2.6, CI [0.08, 0.26]. The lower bound is now above chance (0.064), which OOS-7 alone could not show.
  - **Spatial skill is at chance outside the dev storms.** Pooled FSS at 300 m, 3 % flagged, is 0.019 on the new storms, 0.021 on OOS-7 and 0.234 on dev.
- **Gauges are fine and slightly better on the new storms.** The mean per-storm absolute rise error is **0.31 m** over 15 storms and 26 gauges, against 0.51 m on OOS-7. The model under-predicts throughout (bias −0.28 m). 9 of the 26 gauges have no model rise; these are mostly small-catchment gauges with a median observed rise of only 0.42 m. So the hydraulics and the rain are not what fails on these storms. What fails is that a light convective storm (mean storm rain 16–71 mm) seldom drives a 20 m road segment past the 0.30 m rule.
- **Locked set.** None of the 16 new storms is in the PROTOCOL.md §2 locked list (aug2015, aug2018, aug2020, jul2018, oct2016), so all were run and scored. The label expansion also appended rows to locked jul2018 and aug2020. Those storms were **not run, not scored and not looked at**. `score_v2.py --catalog` now skips locked storms unless `SCORE_LOCKED=1`. `aug2020b` (27 Aug 2020) and `aug2018b` (11 Aug 2018) are distinct storms from the locked aug2020 (23 Aug) and aug2018 (8 Aug).
- **Dev storms** (in-sample, never pooled into the headline): sep2023 30 / 79 at 3 %, aug2021 3 / 12. aug2021 gained 1 site, and its rerun reproduces the earlier hydraulics exactly.

## What was run

- **Model.** The 16 storms from the label expansion are `docs/proto/obs/CATALOG.md` section C and `LABELS_EXPANSION.md`: 12 in the `iem` era (2018 to Oct 2020) and 4 in the `aws` era. Each was run on CPU through `.github/workflows/parity_test.yml` with `dest=docs/proto/parity/catalog`, using exactly the clean parity baseline (`parity/BASELINE.md`): `LF_PARITY=1`, `LF_LOSS=cn`, `LF_CN_SCALE=0.88`, `LF_INFIL_MMH=2`, `LF_QOUT=1`, `LF_VOUT=1`, 20 m, and the catalogue box, t0 and hours (`catalog.json`). Outputs are in `docs/proto/parity/catalog/<id>_<area>_20m/`, in the same layout as the 9 earlier storms.
- **Rain for the `iem` era.** `sim/colab/w9_lisflood.py` now falls back to the IEM mtarchive. It uses `GaugeCorr_QPE_01H` (MRMS v11 gauge-corrected hourly) before 2020-10-14. When AWS lacks an hour it uses IEM `MultiSensor_QPE_01H_Pass2`, with RadarOnly as the last resort. The grid handling is unchanged, and the product used for each hour is recorded in `flood_meta.json` `inputs.rain_products`.
  - All 12 `iem` storms ran entirely on GaugeCorr and all 4 `aws` storms entirely on AWS Pass2, with 0 missing hours.
  - **The check** (`docs/proto/rain/iem_check/jul2019.json`, `proto/rain/iem_qpe_check.py`). On 6 Jul 2019, Worcester ASOS (ORH) recorded 26.9 mm in the hour ending 22Z; GaugeCorr read 23.6 mm. Over the storm window ASOS had 31.0 mm and GaugeCorr 29.0 mm, with hourly r = 1.00. At FIT, OWD, BDL and PVD the hourly r was 0.97–0.99 where it rained.
  - IEM Pass2 and AWS Pass2 are identical at all 5 stations for 2021-07-09 15Z.
  - IEM keeps 24 GaugeCorr files per day (hourly, `GaugeCorr_QPE_01H_00.00_YYYYMMDD-HH0000.grib2.gz`). The "48" in `mrms_check.json` counted each file twice in the listing HTML.
- **Rescored existing storms.** aug2021 (`aug2021_worcester_20m`, `worcester_aug2021_48h`) and aug2026 gained label rows, so they were rerun with the same settings to rebuild `features_`/`matches_` against the current labels. Their hmax statistics and gauge scores are identical to the earlier runs. jul2018 and aug2020 are locked and not in the parity catalogue (see above).
- **Scoring.** `python proto/score_v2.py --catalog --out docs/proto/scoring/BASELINE_v2_expanded.json`. The metrics, matching, sites and bootstrap follow PROTOCOL.md v1 unchanged. The new storms get role `heldout-new`, and three pools were added: `new16`, `heldout23` (OOS-7 + new16) and `all25`. **The OOS-7 decision set of PROTOCOL.md §5 is not changed by this report.** Making `heldout23` the decision set would be a protocol v2 decision.

## Pooled (box-wide, parity group)

Each cell gives sites hit, recall and the 90 % CI from the two-stage cluster bootstrap (2000 replicates). Chance is exact random recall at the same share. Lift = recall / chance.

| pool | storms | sites | metric | rule (p_close ≥ 0.5) | 1 % | 2 % | 3 % | 5 % | 10 % |
|---|---|---|---|---|---|---|---|---|---|
| OOS-7 (frozen decision set) | 7 | 32 | sites hit (recall) [CI] | 4 (0.12) [0.00, 0.25] | 3 (0.09) [0.00, 0.22] | 5 (0.16) [0.03, 0.29] | 6 (0.19) [0.03, 0.35] | 8 (0.25) [0.09, 0.41] | 12 (0.39) [0.21, 0.56] |
| | | | chance / lift | 0.023 / 5.4 | 0.022 / 4.3 | 0.043 / 3.6 | 0.064 / 2.9 | 0.105 / 2.4 | 0.200 / 1.9 |
| | | | FSS300 [CI] | 0.038 [0.007, 0.061] | 0.023 [0.004, 0.048] | 0.019 [0.005, 0.037] | 0.021 [0.009, 0.037] | 0.020 [0.012, 0.029] | 0.016 [0.011, 0.022] |
| new 16 | 16 | 58 | sites hit (recall) [CI] | 1 (0.02) [0.00, 0.06] | 2 (0.03) [0.00, 0.09] | 5 (0.09) [0.02, 0.16] | 9 (0.16) [0.06, 0.26] | 15 (0.26) [0.13, 0.40] | 26 (0.45) [0.29, 0.61] |
| | | | chance / lift | 0.005 / 3.2 | 0.022 / 1.6 | 0.043 / 2.0 | 0.065 / 2.4 | 0.106 / 2.5 | 0.202 / 2.2 |
| | | | FSS300 [CI] | 0.023 [0.001, 0.061] | 0.018 [0.008, 0.031] | 0.016 [0.010, 0.024] | 0.019 [0.012, 0.026] | 0.018 [0.013, 0.022] | 0.015 [0.011, 0.020] |
| held-out 23 = OOS-7 + new 16 | 23 | 90 | sites hit (recall) [CI] | 5 (0.06) [0.01, 0.11] | 5 (0.06) [0.01, 0.11] | 10 (0.11) [0.04, 0.18] | 15 (0.17) [0.08, 0.26] | 23 (0.26) [0.16, 0.36] | 38 (0.43) [0.31, 0.55] |
| | | | chance / lift | 0.012 / 4.8 | 0.022 / 2.6 | 0.043 / 2.6 | 0.064 / 2.6 | 0.105 / 2.4 | 0.201 / 2.1 |
| | | | FSS300 [CI] | 0.031 [0.010, 0.053] | 0.019 [0.010, 0.031] | 0.017 [0.010, 0.024] | 0.019 [0.013, 0.026] | 0.018 [0.014, 0.022] | 0.015 [0.012, 0.019] |
| dev (sep2023, aug2021) | 2 | 91 | sites hit (recall) [CI] | 31 (0.34) [0.08, 0.42] | 24 (0.26) [0.08, 0.33] | 32 (0.35) [0.17, 0.43] | 33 (0.36) [0.17, 0.44] | 44 (0.48) [0.33, 0.57] | 62 (0.68) [0.60, 0.83] |
| | | | chance / lift | 0.035 / 9.8 | 0.018 / 15.1 | 0.035 / 10.1 | 0.052 / 7.0 | 0.085 / 5.7 | 0.163 / 4.2 |
| | | | FSS300 [CI] | 0.332 [0.078, 0.407] | 0.302 [0.076, 0.382] | 0.290 [0.057, 0.425] | 0.234 [0.057, 0.362] | 0.243 [0.052, 0.417] | 0.190 [0.045, 0.354] |
| all 25 | 25 | 181 | sites hit (recall) [CI] | 36 (0.20) [0.03, 0.29] | 29 (0.16) [0.03, 0.23] | 42 (0.23) [0.08, 0.31] | 48 (0.27) [0.12, 0.34] | 67 (0.37) [0.21, 0.45] | 101 (0.56) [0.38, 0.64] |
| | | | chance / lift | 0.023 / 8.5 | 0.020 / 8.2 | 0.039 / 5.9 | 0.058 / 4.6 | 0.095 / 3.9 | 0.182 / 3.1 |
| | | | FSS300 [CI] | 0.137 [0.023, 0.245] | 0.070 [0.015, 0.142] | 0.053 [0.014, 0.113] | 0.045 [0.016, 0.088] | 0.042 [0.017, 0.082] | 0.032 [0.014, 0.062] |

**Before → after for the held-out pool (box, 3 % flagged):** 5 / 29 = 0.17, CI [0.00, 0.34] (OOS-7, `BASELINE_v2_parity.json`) → 6 / 32 = 0.19 (OOS-7 with current labels) → **15 / 90 = 0.17, CI [0.08, 0.26]** (held-out 23).

**Splits of the new 16 at 3 % flagged (box):**

| subset | sites | rule hits | hits at 3 % | expected by chance |
|---|---|---|---|---|
| IEM era (12 storms) | 46 | 1 | 6 | 3.0 |
| AWS era (4 storms) | 12 | 0 | 3 | 0.8 |
| storms marked "Small" in `catalog.json` (7) | 19 | 0 | 2 | 1.4 |

The "Small" storms are may2018, aug2018b, sep2018w, aug2019, sep2019, aug2020b and jul2023b, each with 2–3 road sites. jul2023d also has only 2 in-box sites, but it is not marked Small. Together they add little power: 19 sites spread over 7 storms, and both of their hits come at 3 %. Because the bootstrap resamples storms first, these storms each carry the same weight in the CI as the larger ones.

**Gauges** (`proto/score.py`, model vs USGS rise; peak timing is gap-aware):

| pool | storms with gauges | gauges | mean of per-storm mean abs rise error (m) | pooled mean abs rise error (m) | mean bias (m) | gauges with zero model rise | mean peak timing error (h) | median observed rise (m) |
|---|---|---|---|---|---|---|---|---|
| OOS-7 | 7 | 11 | 0.51 | 0.50 | −0.50 | 3 | 5.9 | 0.93 |
| new 16 | 15 (sep2018 has no gauge in its box) | 26 | **0.31** | 0.31 | −0.28 | 9 | 9.6 | 0.42 |
| dev | 2 | 5 | 0.32 | 0.33 | −0.25 | 0 | 2.6 | 1.42 |

## Per storm (box)

Columns:
- **Sites:** clustered strict-match sites.
- **Rule:** p_close ≥ 0.5.
- **FSS300 @3 %:** chance FSS in brackets.
- **Gauges:** from `score.json`.
- **Rain products:** "pre-meta" means a run made before products were recorded, which is always AWS Pass2.

Storm-mean MRMS rain (mm, mean over the box / max cell):
- **New storms:** may2018 19/24, aug2018b 40/78, sep2018 71/85, sep2018w 34/49, sep2018m 56/109, sep2018b 28/47, jul2019 27/50, aug2019 46/74, sep2019 25/43, jun2020 66/91, jun2020b 26/60, aug2020b 16/25, jul2021b 56/98, jul2023b 52/76, jul2023c 61/85, jul2023d 57/97.
- **Existing storms, for comparison:** sep2023 101/198, sep2021 102/116, aug2026 81/118, aug2021 68/121.

| storm | role | sites | rule share | rule hits | rule lift | hits @3 % | FSS300 @3 % (chance) | gauge mean abs rise err (m) | bias (m) | gauges (zero model rise) | rain products |
|---|---|---|---|---|---|---|---|---|---|---|---|
| aug2021 | dev | 12 | 0.011 | 2.0 | 7.3 | 3.0 | 0.057 (0.077) | 0.40 | -0.26 | 3 (0) | {'AWS MultiSensor_QPE_01H_Pass2': 18} |
| sep2023 | dev | 79 | 0.022 | 29.0 | 10.0 | 30.0 | 0.362 (0.089) | 0.23 | -0.23 | 2 (0) | AWS Pass2 (pre-meta) |
| aug2023 | heldout | 5 | 0.016 | 1.0 | 5.2 | 1.0 | 0.011 (0.028) | 0.19 | -0.19 | 2 (0) | AWS Pass2 (pre-meta) |
| aug2023b | heldout | 2 | 0.001 | 0.0 | 0.0 | 0.0 | 0.005 (0.014) | 0.43 | -0.43 | 2 (1) | AWS Pass2 (pre-meta) |
| aug2026 | heldout | 7 | 0.014 | 1.0 | 5.3 | 2.0 | 0.048 (0.043) | 0.29 | -0.29 | 2 (0) | {'AWS MultiSensor_QPE_01H_Pass2': 18} |
| jul2021 | heldout | 4 | 0.002 | 0.0 | 0.0 | 0.0 | 0.021 (0.029) | 1.32 | -1.32 | 1 (0) | AWS Pass2 (pre-meta) |
| jul2023 | heldout | 5 | 0.001 | 0.0 | 0.0 | 0.0 | 0.003 (0.028) | 0.18 | -0.18 | 1 (0) | AWS Pass2 (pre-meta) |
| sep2021 | heldout | 6 | 0.024 | 2.0 | 7.1 | 3.0 | 0.070 (0.019) | 1.00 | -1.00 | 2 (1) | AWS Pass2 (pre-meta) |
| sep2022 | heldout | 3 | 0.006 | 0.0 | 0.0 | 0.0 | 0.004 (0.036) | 0.14 | -0.14 | 1 (1) | AWS Pass2 (pre-meta) |
| aug2018b (Small) | heldout-new | 3 | 0.002 | 0.0 | 0.0 | 0.0 | 0.014 (0.019) | 0.39 | -0.27 | 4 (1) | {'IEM GaugeCorr_QPE_01H': 22} |
| aug2019 (Small) | heldout-new | 2 | 0.000 | 0.0 | 0.0 | 0.0 | 0.000 (0.018) | 0.80 | -0.80 | 1 (0) | {'IEM GaugeCorr_QPE_01H': 18} |
| aug2020b (Small) | heldout-new | 3 | 0.001 | 0.0 | 0.0 | 0.0 | 0.006 (0.016) | 0.27 | -0.27 | 2 (1) | {'IEM GaugeCorr_QPE_01H': 18} |
| jul2019 | heldout-new | 5 | 0.001 | 0.0 | 0.0 | 0.0 | 0.008 (0.034) | 0.18 | -0.18 | 1 (0) | {'IEM GaugeCorr_QPE_01H': 18} |
| jul2021b | heldout-new | 4 | 0.004 | 0.0 | 0.0 | 2.0 | 0.052 (0.022) | 0.48 | -0.48 | 2 (1) | {'AWS MultiSensor_QPE_01H_Pass2': 24} |
| jul2023b (Small) | heldout-new | 2 | 0.003 | 0.0 | 0.0 | 0.0 | 0.004 (0.007) | 0.56 | -0.56 | 2 (1) | {'AWS MultiSensor_QPE_01H_Pass2': 18} |
| jul2023c | heldout-new | 4 | 0.005 | 0.0 | 0.0 | 1.0 | 0.028 (0.024) | 0.39 | -0.39 | 2 (0) | {'AWS MultiSensor_QPE_01H_Pass2': 18} |
| jul2023d | heldout-new | 2 | 0.004 | 0.0 | 0.0 | 0.0 | 0.000 (0.002) | 0.06 | 0.06 | 2 (1) | {'AWS MultiSensor_QPE_01H_Pass2': 18} |
| jun2020 | heldout-new | 6 | 0.005 | 0.0 | 0.0 | 2.0 | 0.041 (0.037) | 0.18 | -0.18 | 2 (0) | {'IEM GaugeCorr_QPE_01H': 18} |
| jun2020b | heldout-new | 4 | 0.000 | 0.0 | 0.0 | 0.0 | 0.016 (0.013) | 0.31 | -0.31 | 1 (1) | {'IEM GaugeCorr_QPE_01H': 18} |
| may2018 (Small) | heldout-new | 3 | 0.001 | 0.0 | 0.0 | 1.0 | 0.027 (0.027) | 0.28 | -0.28 | 2 (1) | {'IEM GaugeCorr_QPE_01H': 18} |
| sep2018 | heldout-new | 5 | 0.002 | 1.0 | 49.2 | 1.0 | 0.050 (0.027) | – | – | 0 (0) | {'IEM GaugeCorr_QPE_01H': 18} |
| sep2018b | heldout-new | 5 | 0.000 | 0.0 | – | 0.0 | 0.034 (0.018) | 0.36 | -0.36 | 1 (1) | {'IEM GaugeCorr_QPE_01H': 18} |
| sep2018m | heldout-new | 4 | 0.003 | 0.0 | 0.0 | 1.0 | 0.015 (0.031) | 0.15 | -0.15 | 1 (0) | {'IEM GaugeCorr_QPE_01H': 18} |
| sep2018w (Small) | heldout-new | 4 | 0.006 | 0.0 | 0.0 | 0.0 | 0.001 (0.022) | 0.19 | -0.19 | 1 (1) | {'IEM GaugeCorr_QPE_01H': 18} |
| sep2019 (Small) | heldout-new | 2 | 0.000 | 0.0 | 0.0 | 1.0 | 0.014 (0.010) | 0.12 | 0.01 | 2 (0) | {'IEM GaugeCorr_QPE_01H': 18} |

sep2018's single rule hit sits at a rule share of 0.2 %, so its lift of 49 rests on one site.

## Reading

1. **More power, same answer.** Tripling the held-out sites confirms what OOS-7 suggested but could not establish.
   - **What holds:** the parity model's ranking carries a modest out-of-sample signal, at 2–2.6× chance at 3–10 % flagged with the CI now clear of chance.
   - **What does not hold:** the deployed 0.30 m rule. It is tuned on sep2023 and aug2021, where storm rain was 70–100 mm, and on the lighter storms it flags almost nothing. Its pooled held-out recall is 5 / 90.
   - The dev storms (0.35 at 3 %, FSS 0.29) remain far above every held-out pool.
2. **The IEM storms behave like the AWS storms** (6 / 46 vs 3 / 12 at 3 %), and the GaugeCorr rain matches ASOS. The older rain product does not explain the low skill.
3. **For PROTOCOL v2 (not decided here).** With 90 sites, the §5 gain of +0.05 is about 4.5 sites, and a paired bootstrap on held-out 23 would have a CI roughly half as wide as on OOS-7. Pre-registering held-out 23 as the decision set before the next candidate is scored is the obvious next step.

## Full table

`proto/score_v2.py --catalog` table (parity group, box and towns). The Turing group rows are in `BASELINE_v2_expanded.json`.

| run | storm | role | domain | n seg | sites | rule share | rule site recall | lift | CSI site | FSS100 / 300 / 1000 (chance @300) | useful | recall @1/2/3/5/10 % | PR-AUC seg / site |
|---|---|---|---|---|---|---|---|---|---|---|---|
| aug2018b_holden_20m | aug2018b | heldout-new | box | 4422 | 3 | 0.002 | 0.00 (0) | 0.0 | 0.000 | 0.000 / 0.000 / 0.000 (0.001) | 0.501 | 0.00 / 0.00 / 0.00 / 0.00 / 0.33 | 0.004 / 0.004 |
| aug2018b_holden_20m | aug2018b | heldout-new | towns | 1460 | 3 | 0.001 | 0.00 (0) | 0.0 | 0.000 | 0.000 / 0.000 / 0.000 (0.016) | 0.503 | 0.00 / 0.00 / 0.00 / 0.00 / 0.33 | 0.009 / 0.009 |
| aug2019_oxford_20m | aug2019 | heldout-new | box | 6290 | 2 | 0.000 | 0.00 (0) | 0.0 | 0.000 | -0.000 / 0.000 / 0.000 (-0.000) | 0.501 | 0.00 / 0.00 / 0.00 / 0.00 / 0.00 | 0.002 / 0.002 |
| aug2019_oxford_20m | aug2019 | heldout-new | towns | 3248 | 2 | 0.000 | 0.00 (0) | – | 0.000 | 0.000 / 0.000 / 0.000 (0.000) | 0.503 | 0.00 / 0.00 / 0.00 / 0.00 / 0.00 | 0.004 / 0.004 |
| aug2020b_worcester_20m | aug2020b | heldout-new | box | 8807 | 3 | 0.001 | 0.00 (0) | 0.0 | 0.000 | 0.000 / 0.000 / -0.000 (0.000) | 0.501 | 0.00 / 0.00 / 0.00 / 0.00 / 0.67 | 0.002 / 0.002 |
| aug2020b_worcester_20m | aug2020b | heldout-new | towns | 4270 | 3 | 0.001 | 0.00 (0) | 0.0 | 0.000 | 0.000 / 0.000 / 0.000 (0.000) | 0.502 | 0.00 / 0.00 / 0.00 / 0.33 / 0.73 | 0.006 / 0.006 |
| aug2021_worcester_20m | aug2021 | dev | box | 8566 | 12 | 0.011 | 0.17 (2) | 7.3 | 0.026 | 0.047 / 0.078 / 0.179 (0.048) | 0.504 | 0.17 / 0.25 / 0.25 / 0.42 / 0.75 | 0.014 / 0.018 |
| aug2021_worcester_20m | aug2021 | dev | towns | 4759 | 12 | 0.011 | 0.17 (2) | 7.7 | 0.047 | 0.106 / 0.200 / 0.512 (0.077) | 0.507 | 0.17 / 0.25 / 0.25 / 0.42 / 0.75 | 0.024 / 0.031 |
| aug2023_metrowest_20m | aug2023 | heldout | box | 6679 | 5 | 0.016 | 0.20 (1) | 5.2 | 0.013 | 0.010 / 0.008 / 0.013 (0.036) | 0.502 | 0.00 / 0.20 / 0.20 / 0.20 / 0.40 | 0.006 / 0.004 |
| aug2023_metrowest_20m | aug2023 | heldout | towns | 4270 | 5 | 0.017 | 0.20 (1) | 5.1 | 0.020 | 0.016 / 0.012 / 0.020 (0.060) | 0.503 | 0.00 / 0.20 / 0.20 / 0.20 / 0.20 | 0.009 / 0.006 |
| aug2023b_millbury_20m | aug2023b | heldout | box | 8013 | 2 | 0.001 | 0.00 (0) | 0.0 | 0.000 | -0.000 / 0.000 / 0.116 (0.003) | 0.501 | 0.00 / 0.00 / 0.00 / 0.00 / 0.00 | 0.001 / 0.001 |
| aug2023b_millbury_20m | aug2023b | heldout | towns | 1174 | 2 | 0.002 | 0.00 (0) | 0.0 | 0.000 | 0.000 / 0.000 / 0.153 (0.007) | 0.504 | 0.00 / 0.00 / 0.00 / 0.00 / 0.00 | 0.005 / 0.005 |
| aug2026_leominster_20m | aug2026 | heldout | box | 4542 | 7 | 0.014 | 0.14 (1) | 5.3 | 0.021 | 0.042 / 0.066 / 0.184 (0.036) | 0.503 | 0.14 / 0.29 / 0.29 / 0.29 / 0.43 | 0.013 / 0.017 |
| aug2026_leominster_20m | aug2026 | heldout | towns | 3442 | 7 | 0.018 | 0.14 (1) | 4.0 | 0.021 | 0.042 / 0.066 / 0.175 (0.069) | 0.505 | 0.14 / 0.29 / 0.29 / 0.29 / 0.43 | 0.015 / 0.019 |
| jul2019_spencer_20m | jul2019 | heldout-new | box | 6236 | 5 | 0.001 | 0.00 (0) | 0.0 | 0.000 | 0.000 / 0.000 / 0.006 (0.000) | 0.502 | 0.00 / 0.00 / 0.00 / 0.00 / 0.00 | 0.003 / 0.002 |
| jul2019_spencer_20m | jul2019 | heldout-new | towns | 4257 | 5 | 0.001 | 0.00 (0) | 0.0 | 0.000 | 0.000 / 0.000 / 0.006 (0.004) | 0.504 | 0.00 / 0.00 / 0.00 / 0.00 / 0.00 | 0.005 / 0.003 |
| jul2021_worcester_20m | jul2021 | heldout | box | 6275 | 4 | 0.002 | 0.00 (0) | 0.0 | 0.000 | 0.000 / 0.000 / 0.093 (0.007) | 0.502 | 0.00 / 0.00 / 0.00 / 0.25 / 0.50 | 0.003 / 0.003 |
| jul2021_worcester_20m | jul2021 | heldout | towns | 3362 | 4 | 0.004 | 0.00 (0) | 0.0 | 0.000 | 0.000 / 0.000 / 0.092 (0.020) | 0.505 | 0.00 / 0.00 / 0.00 / 0.25 / 0.25 | 0.005 / 0.005 |
| jul2021b_worcester_20m | jul2021b | heldout-new | box | 8553 | 4 | 0.004 | 0.00 (0) | 0.0 | 0.000 | 0.003 / 0.008 / 0.042 (0.006) | 0.501 | 0.25 / 0.25 / 0.50 / 0.50 / 1.00 | 0.016 / 0.012 |
| jul2021b_worcester_20m | jul2021b | heldout-new | towns | 4893 | 4 | 0.007 | 0.00 (0) | 0.0 | 0.000 | 0.003 / 0.009 / 0.037 (0.077) | 0.502 | 0.25 / 0.25 / 0.25 / 0.50 / 1.00 | 0.018 / 0.014 |
| jul2023_worcester_20m | jul2023 | heldout | box | 6775 | 5 | 0.001 | 0.00 (0) | 0.0 | 0.000 | 0.000 / 0.006 / 0.140 (0.004) | 0.502 | 0.00 / 0.00 / 0.00 / 0.20 / 0.20 | 0.002 / 0.001 |
| jul2023_worcester_20m | jul2023 | heldout | towns | 4887 | 5 | 0.001 | 0.00 (0) | 0.0 | 0.000 | -0.000 / 0.006 / 0.139 (0.000) | 0.503 | 0.00 / 0.00 / 0.00 / 0.20 / 0.20 | 0.002 / 0.002 |
| jul2023b_worcester_20m | jul2023b | heldout-new | box | 7372 | 2 | 0.003 | 0.00 (0) | 0.0 | 0.000 | 0.000 / 0.000 / 0.000 (0.000) | 0.501 | 0.00 / 0.00 / 0.00 / 1.00 / 1.00 | 0.004 / 0.005 |
| jul2023b_worcester_20m | jul2023b | heldout-new | towns | 4632 | 2 | 0.004 | 0.00 (0) | 0.0 | 0.000 | -0.000 / 0.000 / 0.000 (0.017) | 0.502 | 0.00 / 0.00 / 0.00 / 1.00 / 1.00 | 0.007 / 0.008 |
| jul2023c_fitchburg_20m | jul2023c | heldout-new | box | 4614 | 4 | 0.005 | 0.00 (0) | 0.0 | 0.000 | 0.006 / 0.014 / 0.077 (0.030) | 0.502 | 0.00 / 0.25 / 0.25 / 0.25 / 0.25 | 0.008 / 0.006 |
| jul2023c_fitchburg_20m | jul2023c | heldout-new | towns | 1503 | 4 | 0.003 | 0.00 (0) | 0.0 | 0.000 | 0.031 / 0.058 / 0.133 (0.013) | 0.508 | 0.00 / 0.00 / 0.25 / 0.25 / 0.25 | 0.016 / 0.013 |
| jul2023d_hubbardston_20m | jul2023d | heldout-new | box | 1317 | 2 | 0.004 | 0.00 (0) | 0.0 | 0.000 | 0.000 / 0.000 / 0.000 (0.000) | 0.502 | 0.00 / 0.00 / 0.00 / 0.00 / 0.00 | 0.004 / 0.002 |
| jul2023d_hubbardston_20m | jul2023d | heldout-new | towns | 367 | 2 | 0.008 | 0.00 (0) | 0.0 | 0.000 | 0.000 / 0.000 / -0.000 (0.060) | 0.507 | 0.00 / 0.00 / 0.00 / 0.00 / 0.00 | 0.012 / 0.006 |
| jun2020_northbridge_20m | jun2020 | heldout-new | box | 4247 | 6 | 0.005 | 0.00 (0) | 0.0 | 0.000 | 0.000 / 0.000 / 0.025 (0.032) | 0.503 | 0.00 / 0.17 / 0.33 / 0.33 / 0.67 | 0.011 / 0.015 |
| jun2020_northbridge_20m | jun2020 | heldout-new | towns | 2567 | 6 | 0.002 | 0.00 (0) | 0.0 | 0.000 | 0.000 / 0.000 / 0.000 (0.083) | 0.505 | 0.00 / 0.33 / 0.33 / 0.67 / 0.67 | 0.020 / 0.029 |
| jun2020b_gardner_20m | jun2020b | heldout-new | box | 2219 | 4 | 0.000 | 0.00 (0) | 0.0 | 0.000 | 0.000 / 0.000 / 0.000 (0.003) | 0.502 | 0.00 / 0.00 / 0.00 / 0.00 / 0.00 | 0.004 / 0.004 |
| jun2020b_gardner_20m | jun2020b | heldout-new | towns | 959 | 4 | 0.000 | 0.00 (0) | – | 0.000 | 0.000 / 0.000 / 0.000 (0.000) | 0.506 | 0.00 / 0.00 / 0.00 / 0.00 / 0.00 | 0.008 / 0.007 |
| may2018_shrewsbury_20m | may2018 | heldout-new | box | 9355 | 3 | 0.001 | 0.00 (0) | 0.0 | 0.000 | 0.000 / 0.000 / 0.010 (0.001) | 0.502 | 0.00 / 0.00 / 0.33 / 0.33 / 0.33 | 0.001 / 0.002 |
| may2018_shrewsbury_20m | may2018 | heldout-new | towns | 5755 | 3 | 0.001 | 0.00 (0) | 0.0 | 0.000 | 0.000 / 0.000 / 0.011 (0.000) | 0.503 | 0.00 / 0.00 / 0.33 / 0.33 / 0.33 | 0.002 / 0.004 |
| sep2018_fitchburg_20m | sep2018 | heldout-new | box | 3097 | 5 | 0.002 | 0.20 (1) | 49.2 | 0.091 | 0.179 / 0.236 / 0.375 (0.001) | 0.504 | 0.20 / 0.20 / 0.20 / 0.20 / 0.60 | 0.029 / 0.045 |
| sep2018_fitchburg_20m | sep2018 | heldout-new | towns | 2850 | 5 | 0.002 | 0.20 (1) | 45.3 | 0.091 | 0.179 / 0.236 / 0.375 (0.002) | 0.504 | 0.20 / 0.20 / 0.20 / 0.20 / 0.60 | 0.030 / 0.045 |
| sep2018b_gardner_20m | sep2018b | heldout-new | box | 1927 | 5 | 0.000 | 0.00 (0) | – | 0.000 | 0.000 / 0.000 / 0.000 (0.000) | 0.504 | 0.00 / 0.00 / 0.00 / 0.00 / 0.40 | 0.006 / 0.006 |
| sep2018b_gardner_20m | sep2018b | heldout-new | towns | 1427 | 5 | 0.000 | 0.00 (0) | – | 0.000 | 0.000 / 0.000 / 0.000 (0.000) | 0.506 | 0.00 / 0.00 / 0.00 / 0.00 / 0.40 | 0.009 / 0.008 |
| sep2018m_milford_20m | sep2018m | heldout-new | box | 5024 | 4 | 0.003 | 0.00 (0) | 0.0 | 0.000 | 0.000 / 0.000 / 0.002 (0.016) | 0.502 | 0.00 / 0.25 / 0.25 / 0.25 / 0.25 | 0.005 / 0.007 |
| sep2018m_milford_20m | sep2018m | heldout-new | towns | 2162 | 4 | 0.004 | 0.00 (0) | 0.0 | 0.000 | -0.000 / 0.000 / 0.002 (0.017) | 0.504 | 0.00 / 0.25 / 0.25 / 0.25 / 0.25 | 0.012 / 0.016 |
| sep2018w_shrewsbury_20m | sep2018w | heldout-new | box | 6283 | 4 | 0.006 | 0.00 (0) | 0.0 | 0.000 | 0.000 / 0.000 / 0.000 (0.060) | 0.501 | 0.00 / 0.00 / 0.00 / 0.75 / 0.75 | 0.008 / 0.007 |
| sep2018w_shrewsbury_20m | sep2018w | heldout-new | towns | 2535 | 4 | 0.002 | 0.00 (0) | 0.0 | 0.000 | 0.000 / 0.000 / -0.000 (0.023) | 0.504 | 0.00 / 0.00 / 0.50 / 0.75 / 0.75 | 0.024 / 0.021 |
| sep2019_northbridge_20m | sep2019 | heldout-new | box | 4536 | 2 | 0.000 | 0.00 (0) | 0.0 | 0.000 | 0.000 / 0.000 / 0.000 (0.000) | 0.501 | 0.00 / 0.00 / 0.50 / 1.00 / 1.00 | 0.005 / 0.010 |
| sep2019_northbridge_20m | sep2019 | heldout-new | towns | 1496 | 2 | 0.001 | 0.00 (0) | 0.0 | 0.000 | 0.000 / 0.000 / 0.000 (0.003) | 0.503 | 0.00 / 0.50 / 0.50 / 1.00 / 1.00 | 0.017 / 0.039 |
| sep2021_worcester_20m | sep2021 | heldout | box | 7775 | 6 | 0.024 | 0.33 (2) | 7.1 | 0.020 | 0.059 / 0.065 / 0.109 (0.023) | 0.501 | 0.33 / 0.33 / 0.50 / 0.50 / 0.67 | 0.020 / 0.021 |
| sep2021_worcester_20m | sep2021 | heldout | towns | 5036 | 6 | 0.032 | 0.33 (2) | 5.3 | 0.026 | 0.077 / 0.090 / 0.136 (0.074) | 0.502 | 0.33 / 0.33 / 0.33 / 0.50 / 0.50 | 0.022 / 0.021 |
| sep2022_webster_20m | sep2022 | heldout | box | 2472 | 3 | 0.006 | 0.00 (0) | 0.0 | 0.000 | 0.002 / 0.006 / 0.027 (0.035) | 0.502 | 0.00 / 0.00 / 0.00 / 0.00 / 0.13 | 0.003 / 0.002 |
| sep2022_webster_20m | sep2022 | heldout | towns | 1472 | 3 | 0.004 | 0.00 (0) | 0.0 | 0.000 | 0.006 / 0.023 / 0.086 (0.043) | 0.505 | 0.00 / 0.00 / 0.00 / 0.00 / 0.33 | 0.005 / 0.004 |
| sep2023_leominster_20m | sep2023 | dev | box | 4542 | 79 | 0.022 | 0.37 (29) | 10.0 | 0.207 | 0.342 / 0.407 / 0.530 (0.088) | 0.531 | 0.28 / 0.37 / 0.38 / 0.49 / 0.67 | 0.178 / 0.277 |
| sep2023_leominster_20m | sep2023 | dev | towns (complete) | 1521 | 73 | 0.038 | 0.40 (29) | 6.2 | 0.296 | 0.475 / 0.542 / 0.601 (0.145) | 0.608 | 0.16 / 0.29 / 0.38 / 0.44 / 0.59 | 0.307 / 0.411 |
| worcester_aug2021_48h | aug2021 | dev (extra) | box | 8566 | 12 | 0.011 | 0.17 (2) | 7.1 | 0.026 | 0.047 / 0.078 / 0.182 (0.070) | 0.504 | 0.17 / 0.25 / 0.25 / 0.42 / 0.75 | 0.014 / 0.018 |
| worcester_aug2021_48h | aug2021 | dev (extra) | towns | 4759 | 12 | 0.011 | 0.17 (2) | 7.4 | 0.047 | 0.104 / 0.197 / 0.510 (0.075) | 0.507 | 0.17 / 0.25 / 0.25 / 0.42 / 0.75 | 0.023 / 0.030 |

| pool | domain | storms | sites | metric | rule | 1 % | 2 % | 3 % | 5 % | 10 % |
|---|---|---|---|---|---|---|---|---|---|---|
| parity:all9 | box | 9 | 123 | label_recall | 0.332 | 0.242 | 0.342 | 0.358 | 0.432 | 0.605 |
| parity:all9 | box | 9 | 123 | site_recall | 0.285 [0.070, 0.362] | 0.220 [0.045, 0.285] | 0.301 [0.106, 0.371] | 0.317 [0.119, 0.391] | 0.423 [0.205, 0.500] | 0.607 [0.364, 0.684] |
| parity:all9 | box | 9 | 123 | chance | 0.032 | 0.019 | 0.037 | 0.055 | 0.090 | 0.172 |
| parity:all9 | box | 9 | 123 | lift | 8.959 | 11.801 | 8.114 | 5.772 | 4.696 | 3.519 |
| parity:all9 | box | 9 | 123 | csi_site | 0.073 | 0.055 | 0.047 | 0.036 | 0.033 | 0.031 |
| parity:all9 | box | 9 | 123 | fss100 | 0.133 | 0.101 | 0.078 | 0.061 | 0.058 | 0.045 |
| parity:all9 | box | 9 | 123 | fss300 | 0.183 [0.029, 0.313] | 0.138 [0.018, 0.249] | 0.106 [0.015, 0.221] | 0.084 [0.017, 0.174] | 0.080 [0.018, 0.175] | 0.060 [0.015, 0.134] |
| parity:all9 | box | 9 | 123 | fss1000 | 0.307 | 0.248 | 0.202 | 0.159 | 0.138 | 0.088 |
| parity:all9 | box | | | matched labels (unclustered) | 190 | | | | | |
| parity:all9 | box | | | PR-AUC seg / site (storm mean) | 0.027 [0.005, 0.064] / 0.038 [0.006, 0.097] | | | | | |
| parity:all9 | towns | 9 | 117 | label_recall | 0.344 | 0.158 | 0.257 | 0.339 | 0.404 | 0.546 |
| parity:all9 | towns | 9 | 117 | site_recall | 0.299 [0.070, 0.386] | 0.145 [0.047, 0.203] | 0.248 [0.100, 0.313] | 0.308 [0.100, 0.387] | 0.385 [0.196, 0.458] | 0.530 [0.290, 0.618] |
| parity:all9 | towns | 9 | 117 | chance | 0.050 | 0.019 | 0.037 | 0.055 | 0.090 | 0.173 |
| parity:all9 | towns | 9 | 117 | lift | 6.019 | 7.807 | 6.741 | 5.555 | 4.260 | 3.065 |
| parity:all9 | towns | 9 | 117 | csi_site | 0.100 | 0.055 | 0.062 | 0.059 | 0.052 | 0.051 |
| parity:all9 | towns | 9 | 117 | fss100 | 0.191 | 0.087 | 0.110 | 0.105 | 0.093 | 0.080 |
| parity:all9 | towns | 9 | 117 | fss300 | 0.261 [0.045, 0.427] | 0.106 [0.033, 0.149] | 0.149 [0.031, 0.260] | 0.146 [0.034, 0.278] | 0.129 [0.040, 0.256] | 0.105 [0.029, 0.233] |
| parity:all9 | towns | 9 | 117 | fss1000 | 0.387 | 0.170 | 0.247 | 0.246 | 0.205 | 0.145 |
| parity:all9 | towns | | | matched labels (unclustered) | 183 | | | | | |
| parity:all9 | towns | | | PR-AUC seg / site (storm mean) | 0.044 [0.008, 0.109] / 0.056 [0.008, 0.144] | | | | | |
| parity:heldout7 | box | 7 | 32 | label_recall | 0.118 | 0.088 | 0.147 | 0.176 | 0.235 | 0.376 |
| parity:heldout7 | box | 7 | 32 | site_recall | 0.125 [0.000, 0.250] | 0.094 [0.000, 0.219] | 0.156 [0.032, 0.294] | 0.188 [0.033, 0.350] | 0.250 [0.094, 0.406] | 0.388 [0.205, 0.556] |
| parity:heldout7 | box | 7 | 32 | chance | 0.023 | 0.022 | 0.043 | 0.064 | 0.105 | 0.200 |
| parity:heldout7 | box | 7 | 32 | lift | 5.435 | 4.319 | 3.631 | 2.940 | 2.390 | 1.938 |
| parity:heldout7 | box | 7 | 32 | csi_site | 0.015 | 0.009 | 0.009 | 0.008 | 0.007 | 0.007 |
| parity:heldout7 | box | 7 | 32 | fss100 | 0.032 | 0.020 | 0.016 | 0.015 | 0.014 | 0.012 |
| parity:heldout7 | box | 7 | 32 | fss300 | 0.038 [0.007, 0.061] | 0.023 [0.004, 0.048] | 0.019 [0.005, 0.037] | 0.021 [0.009, 0.037] | 0.020 [0.012, 0.029] | 0.016 [0.011, 0.022] |
| parity:heldout7 | box | 7 | 32 | fss1000 | 0.078 | 0.076 | 0.051 | 0.049 | 0.038 | 0.026 |
| parity:heldout7 | box | | | matched labels (unclustered) | 34 | | | | | |
| parity:heldout7 | box | | | PR-AUC seg / site (storm mean) | 0.007 [0.003, 0.011] / 0.007 [0.002, 0.012] | | | | | |
| parity:heldout7 | towns | 7 | 32 | label_recall | 0.118 | 0.088 | 0.147 | 0.147 | 0.235 | 0.324 |
| parity:heldout7 | towns | 7 | 32 | site_recall | 0.125 [0.000, 0.250] | 0.094 [0.000, 0.219] | 0.156 [0.032, 0.294] | 0.156 [0.032, 0.294] | 0.250 [0.094, 0.406] | 0.312 [0.148, 0.467] |
| parity:heldout7 | towns | 7 | 32 | chance | 0.028 | 0.022 | 0.043 | 0.064 | 0.105 | 0.200 |
| parity:heldout7 | towns | 7 | 32 | lift | 4.391 | 4.310 | 3.647 | 2.448 | 2.389 | 1.563 |
| parity:heldout7 | towns | 7 | 32 | csi_site | 0.019 | 0.016 | 0.015 | 0.012 | 0.013 | 0.011 |
| parity:heldout7 | towns | 7 | 32 | fss100 | 0.043 | 0.035 | 0.030 | 0.029 | 0.029 | 0.022 |
| parity:heldout7 | towns | 7 | 32 | fss300 | 0.052 [0.011, 0.078] | 0.041 [0.009, 0.081] | 0.036 [0.012, 0.063] | 0.038 [0.019, 0.063] | 0.042 [0.029, 0.057] | 0.030 [0.022, 0.040] |
| parity:heldout7 | towns | 7 | 32 | fss1000 | 0.100 | 0.127 | 0.096 | 0.092 | 0.076 | 0.050 |
| parity:heldout7 | towns | | | matched labels (unclustered) | 34 | | | | | |
| parity:heldout7 | towns | | | PR-AUC seg / site (storm mean) | 0.009 [0.005, 0.013] / 0.009 [0.004, 0.014] | | | | | |
| parity:dev2 | box | 2 | 91 | label_recall | 0.378 | 0.276 | 0.385 | 0.397 | 0.474 | 0.655 |
| parity:dev2 | box | 2 | 91 | site_recall | 0.341 [0.083, 0.418] | 0.264 [0.083, 0.333] | 0.352 [0.167, 0.429] | 0.363 [0.167, 0.440] | 0.484 [0.333, 0.571] | 0.684 [0.602, 0.833] |
| parity:dev2 | box | 2 | 91 | chance | 0.035 | 0.018 | 0.035 | 0.052 | 0.085 | 0.163 |
| parity:dev2 | box | 2 | 91 | lift | 9.777 | 15.062 | 10.054 | 6.997 | 5.694 | 4.203 |
| parity:dev2 | box | 2 | 91 | csi_site | 0.144 | 0.139 | 0.130 | 0.102 | 0.103 | 0.096 |
| parity:dev2 | box | 2 | 91 | fss100 | 0.257 | 0.242 | 0.220 | 0.179 | 0.182 | 0.147 |
| parity:dev2 | box | 2 | 91 | fss300 | 0.332 [0.078, 0.407] | 0.302 [0.076, 0.382] | 0.290 [0.057, 0.425] | 0.234 [0.057, 0.362] | 0.243 [0.052, 0.417] | 0.190 [0.045, 0.354] |
| parity:dev2 | box | 2 | 91 | fss1000 | 0.473 | 0.391 | 0.426 | 0.368 | 0.383 | 0.264 |
| parity:dev2 | box | | | matched labels (unclustered) | 156 | | | | | |
| parity:dev2 | box | | | PR-AUC seg / site (storm mean) | 0.096 [0.014, 0.178] / 0.148 [0.018, 0.277] | | | | | |
| parity:dev2 | towns | 2 | 85 | label_recall | 0.396 | 0.174 | 0.282 | 0.383 | 0.443 | 0.597 |
| parity:dev2 | towns | 2 | 85 | site_recall | 0.365 [0.083, 0.447] | 0.165 [0.083, 0.250] | 0.282 [0.167, 0.370] | 0.365 [0.167, 0.447] | 0.435 [0.329, 0.541] | 0.612 [0.529, 0.833] |
| parity:dev2 | towns | 2 | 85 | chance | 0.058 | 0.017 | 0.034 | 0.052 | 0.085 | 0.163 |
| parity:dev2 | towns | 2 | 85 | lift | 6.321 | 9.450 | 8.188 | 6.985 | 5.129 | 3.760 |
| parity:dev2 | towns | 2 | 85 | csi_site | 0.220 | 0.117 | 0.162 | 0.172 | 0.164 | 0.176 |
| parity:dev2 | towns | 2 | 85 | fss100 | 0.401 | 0.161 | 0.266 | 0.294 | 0.284 | 0.279 |
| parity:dev2 | towns | 2 | 85 | fss300 | 0.497 [0.200, 0.542] | 0.175 [0.174, 0.185] | 0.332 [0.133, 0.402] | 0.381 [0.148, 0.489] | 0.370 [0.121, 0.556] | 0.360 [0.095, 0.683] |
| parity:dev2 | towns | 2 | 85 | fss1000 | 0.595 | 0.193 | 0.406 | 0.483 | 0.504 | 0.450 |
| parity:dev2 | towns | | | matched labels (unclustered) | 149 | | | | | |
| parity:dev2 | towns | | | PR-AUC seg / site (storm mean) | 0.166 [0.024, 0.307] / 0.221 [0.031, 0.411] | | | | | |
| parity:new16 | box | 16 | 58 | label_recall | 0.017 | 0.034 | 0.086 | 0.155 | 0.259 | 0.448 |
| parity:new16 | box | 16 | 58 | site_recall | 0.017 [0.000, 0.062] | 0.034 [0.000, 0.091] | 0.086 [0.018, 0.164] | 0.155 [0.056, 0.258] | 0.259 [0.127, 0.397] | 0.448 [0.286, 0.609] |
| parity:new16 | box | 16 | 58 | chance | 0.005 | 0.022 | 0.043 | 0.065 | 0.106 | 0.202 |
| parity:new16 | box | 16 | 58 | lift | 3.220 | 1.582 | 1.989 | 2.406 | 2.451 | 2.219 |
| parity:new16 | box | 16 | 58 | csi_site | 0.005 | 0.003 | 0.004 | 0.006 | 0.006 | 0.007 |
| parity:new16 | box | 16 | 58 | fss100 | 0.015 | 0.012 | 0.010 | 0.012 | 0.013 | 0.011 |
| parity:new16 | box | 16 | 58 | fss300 | 0.023 [0.001, 0.061] | 0.018 [0.008, 0.031] | 0.016 [0.010, 0.024] | 0.019 [0.012, 0.026] | 0.018 [0.013, 0.022] | 0.015 [0.011, 0.020] |
| parity:new16 | box | 16 | 58 | fss1000 | 0.050 | 0.045 | 0.038 | 0.036 | 0.030 | 0.023 |
| parity:new16 | box | | | matched labels (unclustered) | 58 | | | | | |
| parity:new16 | box | | | PR-AUC seg / site (storm mean) | 0.007 [0.005, 0.01] / 0.008 [0.005, 0.013] | | | | | |
| parity:new16 | towns | 16 | 58 | label_recall | 0.017 | 0.034 | 0.103 | 0.172 | 0.310 | 0.452 |
| parity:new16 | towns | 16 | 58 | site_recall | 0.017 [0.000, 0.062] | 0.034 [0.000, 0.091] | 0.103 [0.020, 0.191] | 0.172 [0.070, 0.274] | 0.310 [0.161, 0.464] | 0.452 [0.289, 0.615] |
| parity:new16 | towns | 16 | 58 | chance | 0.005 | 0.022 | 0.043 | 0.065 | 0.105 | 0.202 |
| parity:new16 | towns | 16 | 58 | lift | 3.653 | 1.566 | 2.390 | 2.670 | 2.942 | 2.234 |
| parity:new16 | towns | 16 | 58 | csi_site | 0.007 | 0.006 | 0.010 | 0.012 | 0.015 | 0.015 |
| parity:new16 | towns | 16 | 58 | fss100 | 0.025 | 0.023 | 0.024 | 0.027 | 0.029 | 0.024 |
| parity:new16 | towns | 16 | 58 | fss300 | 0.038 [0.001, 0.090] | 0.037 [0.018, 0.058] | 0.039 [0.025, 0.055] | 0.042 [0.031, 0.054] | 0.041 [0.031, 0.052] | 0.034 [0.025, 0.042] |
| parity:new16 | towns | 16 | 58 | fss1000 | 0.075 | 0.093 | 0.088 | 0.088 | 0.072 | 0.050 |
| parity:new16 | towns | | | matched labels (unclustered) | 58 | | | | | |
| parity:new16 | towns | | | PR-AUC seg / site (storm mean) | 0.012 [0.009, 0.015] / 0.014 [0.01, 0.019] | | | | | |
| parity:heldout23 | box | 23 | 90 | label_recall | 0.054 | 0.054 | 0.109 | 0.163 | 0.250 | 0.422 |
| parity:heldout23 | box | 23 | 90 | site_recall | 0.056 [0.009, 0.114] | 0.056 [0.010, 0.114] | 0.111 [0.044, 0.183] | 0.167 [0.080, 0.255] | 0.256 [0.156, 0.359] | 0.427 [0.306, 0.547] |
| parity:heldout23 | box | 23 | 90 | chance | 0.012 | 0.022 | 0.043 | 0.064 | 0.105 | 0.201 |
| parity:heldout23 | box | 23 | 90 | lift | 4.778 | 2.552 | 2.570 | 2.594 | 2.429 | 2.119 |
| parity:heldout23 | box | 23 | 90 | csi_site | 0.011 | 0.005 | 0.006 | 0.006 | 0.006 | 0.007 |
| parity:heldout23 | box | 23 | 90 | fss100 | 0.024 | 0.014 | 0.012 | 0.013 | 0.013 | 0.011 |
| parity:heldout23 | box | 23 | 90 | fss300 | 0.031 [0.010, 0.053] | 0.019 [0.010, 0.031] | 0.017 [0.010, 0.024] | 0.019 [0.013, 0.026] | 0.018 [0.014, 0.022] | 0.015 [0.012, 0.019] |
| parity:heldout23 | box | 23 | 90 | fss1000 | 0.066 | 0.054 | 0.042 | 0.040 | 0.033 | 0.024 |
| parity:heldout23 | box | | | matched labels (unclustered) | 92 | | | | | |
| parity:heldout23 | box | | | PR-AUC seg / site (storm mean) | 0.007 [0.005, 0.009] / 0.008 [0.005, 0.011] | | | | | |
| parity:heldout23 | towns | 23 | 90 | label_recall | 0.054 | 0.054 | 0.120 | 0.163 | 0.283 | 0.404 |
| parity:heldout23 | towns | 23 | 90 | site_recall | 0.056 [0.009, 0.114] | 0.056 [0.010, 0.114] | 0.122 [0.048, 0.200] | 0.167 [0.084, 0.250] | 0.289 [0.180, 0.400] | 0.402 [0.284, 0.521] |
| parity:heldout23 | towns | 23 | 90 | chance | 0.013 | 0.022 | 0.043 | 0.064 | 0.105 | 0.201 |
| parity:heldout23 | towns | 23 | 90 | lift | 4.220 | 2.534 | 2.834 | 2.592 | 2.747 | 1.998 |
| parity:heldout23 | towns | 23 | 90 | csi_site | 0.015 | 0.009 | 0.012 | 0.012 | 0.014 | 0.014 |
| parity:heldout23 | towns | 23 | 90 | fss100 | 0.036 | 0.027 | 0.026 | 0.027 | 0.029 | 0.024 |
| parity:heldout23 | towns | 23 | 90 | fss300 | 0.046 [0.016, 0.073] | 0.038 [0.021, 0.057] | 0.038 [0.026, 0.052] | 0.040 [0.030, 0.051] | 0.041 [0.034, 0.050] | 0.032 [0.026, 0.039] |
| parity:heldout23 | towns | 23 | 90 | fss1000 | 0.091 | 0.105 | 0.091 | 0.089 | 0.073 | 0.050 |
| parity:heldout23 | towns | | | matched labels (unclustered) | 92 | | | | | |
| parity:heldout23 | towns | | | PR-AUC seg / site (storm mean) | 0.011 [0.009, 0.014] / 0.013 [0.009, 0.017] | | | | | |
| parity:all25 | box | 25 | 181 | label_recall | 0.258 | 0.194 | 0.282 | 0.310 | 0.391 | 0.569 |
| parity:all25 | box | 25 | 181 | site_recall | 0.199 [0.030, 0.290] | 0.160 [0.032, 0.228] | 0.232 [0.081, 0.309] | 0.265 [0.121, 0.338] | 0.370 [0.213, 0.451] | 0.556 [0.383, 0.640] |
| parity:all25 | box | 25 | 181 | chance | 0.023 | 0.020 | 0.039 | 0.058 | 0.095 | 0.182 |
| parity:all25 | box | 25 | 181 | lift | 8.536 | 8.164 | 5.937 | 4.572 | 3.896 | 3.056 |
| parity:all25 | box | 25 | 181 | csi_site | 0.053 | 0.026 | 0.021 | 0.018 | 0.017 | 0.017 |
| parity:all25 | box | 25 | 181 | fss100 | 0.099 | 0.050 | 0.037 | 0.032 | 0.030 | 0.024 |
| parity:all25 | box | 25 | 181 | fss300 | 0.137 [0.023, 0.245] | 0.070 [0.015, 0.142] | 0.053 [0.014, 0.113] | 0.045 [0.016, 0.088] | 0.042 [0.017, 0.082] | 0.032 [0.014, 0.062] |
| parity:all25 | box | 25 | 181 | fss1000 | 0.248 | 0.144 | 0.110 | 0.088 | 0.073 | 0.049 |
| parity:all25 | box | | | matched labels (unclustered) | 248 | | | | | |
| parity:all25 | box | | | PR-AUC seg / site (storm mean) | 0.014 [0.006, 0.028] / 0.019 [0.006, 0.04] | | | | | |
| parity:all25 | towns | 25 | 175 | label_recall | 0.266 | 0.129 | 0.220 | 0.299 | 0.382 | 0.524 |
| parity:all25 | towns | 25 | 175 | site_recall | 0.206 [0.035, 0.307] | 0.109 [0.034, 0.155] | 0.200 [0.090, 0.265] | 0.263 [0.128, 0.344] | 0.360 [0.238, 0.434] | 0.504 [0.365, 0.585] |
| parity:all25 | towns | 25 | 175 | chance | 0.035 | 0.020 | 0.039 | 0.058 | 0.095 | 0.183 |
| parity:all25 | towns | 25 | 175 | lift | 5.912 | 5.499 | 5.137 | 4.498 | 3.777 | 2.760 |
| parity:all25 | towns | 25 | 175 | csi_site | 0.074 | 0.029 | 0.032 | 0.031 | 0.031 | 0.030 |
| parity:all25 | towns | 25 | 175 | fss100 | 0.149 | 0.053 | 0.061 | 0.059 | 0.055 | 0.047 |
| parity:all25 | towns | 25 | 175 | fss300 | 0.204 [0.038, 0.349] | 0.071 [0.032, 0.105] | 0.088 [0.034, 0.159] | 0.086 [0.037, 0.158] | 0.077 [0.039, 0.136] | 0.062 [0.030, 0.114] |
| parity:all25 | towns | 25 | 175 | fss1000 | 0.329 | 0.138 | 0.168 | 0.160 | 0.128 | 0.089 |
| parity:all25 | towns | | | matched labels (unclustered) | 241 | | | | | |
| parity:all25 | towns | | | PR-AUC seg / site (storm mean) | 0.024 [0.01, 0.047] / 0.029 [0.011, 0.061] | | | | | |
