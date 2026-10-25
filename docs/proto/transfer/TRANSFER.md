# Transfer test: the frozen District 3 model on Districts 4–6 storms (run r1, 25 Oct 2026)

**Plain verdict: the model transfers, but only as the weak ranking skill it already has in District 3.** On 81 independent storms
(498 road-level sites) in MassDOT Districts 4, 5 and 6, run once with the frozen District 3 settings and no retuning, the top 3 % of road
segments ranked by the model catch **21 % of the documented flood sites (104 / 498; 90 % CI 0.17–0.25)**. Random flagging would catch
8.6 %, so the lift is **2.5 (CI 1.96–2.97)**. That clears the pre-registered *transfers* rule (lift CI above 1 **and** recall not below
the District 3 held-out lower bound 0.104), and the recall is the same as on the 23 District 3 held-out storms (0.204). The same weaknesses
carry over too:

- **The deployed 0.30 m alert rule rarely fires.** It flags a mean 0.14 % of segments (District 3 held-out: 0.43 %) and catches **18 of
  498 sites (3.6 %, CI 1.5–5.8 %)**, against 9.2 % in District 3. When it fires it is well placed (lift 6.7, District 3 6.4), but most
  storms here are short convective bursts that never push a 20 m road cell past 0.30 m.
- **Spatial skill is at chance.** FSS at 300 m is 0.017 at 3 % flagged (random flagging at the same share: 0.023; "useful" ≈ 0.50) and
  0.045 at the rule (random 0.009). District 3 held-out: 0.023 and 0.051.
- **Gauges look like District 3.** Mean per-storm absolute stage-rise error is 0.35 m over 74 storms (District 3 held-out 0.38 m), with the
  same under-prediction (bias −0.27 m vs −0.36 m).
- **Part of the gap is the road map, not the model.** Districts 4–6 have no MassDOT segment graph in the repo, so the test used OpenStreetMap
  roads. On two District 3 storms run with identical physics, swapping the MassDOT graph for OSM roads alone lowered the hits at 3 % from
  5 / 14 to 3 / 14 and roughly halved the lift. The District 4–6 numbers are therefore, if anything, a slight underestimate.

Pre-registration: `docs/proto/PROTOCOL.md` "Transfer test (Districts 4–6)" (main commit ba470bb2), committed before the catalogue was built
or any storm was run. Catalogue: `docs/proto/obs/CATALOG_D456.md`. Code: `proto/transfer_d456.py`, `proto/score_v2.py --d456`,
`.github/workflows/transfer_test.yml`.

## 1. What was run

- **Storms.** 81 storms, 2018-01 to 2026-09 (District 4: 30, District 5: 31, District 6: 20; 44 on IEM GaugeCorr rain before Oct 2020, 37 on
  AWS MRMS Pass2). Each storm is a 20 × 20 km box with at least 3 road-level sites, chosen by the pre-registered rule. Coastal-surge,
  tidal and snowmelt events are excluded. The pre-registration aimed for 15–25 storms; the record supported 81, and all 81 were run and scored.
  MRMS was listed for every storm (`obs/catalog/mrms_check.json`), and every run had complete hourly rain: 44 on IEM GaugeCorr, 39 on AWS
  Pass2 (this count includes the 2 controls) and 1 on IEM Pass2 (`flood_meta.json` `inputs.rain_products`).
- **Labels.** 659 rows: 395 NWS LSR, 199 Storm Events, 61 SeeClickFix, 4 Boston 311. 544 are road-level (155 `exact` and 389 `approx`); 115
  could not be placed and stay `town`. 498 sites (150 m clusters) matched road segments at 30 m.
- **Model, frozen.** CPU LISFLOOD-FP through `sim/colab/w9_lisflood.py`, unchanged: `LF_PARITY=1 LF_LOSS=cn LF_CN_SCALE=0.88 LF_INFIL_MMH=2
  LF_QOUT=1 LF_VOUT=1`, 20 m. Then `proto/prototype.py` at its defaults, with the deployed rule `p_close ≥ 0.5`. The watch tier is
  `closure_lr_all.json` at P ≥ 0.02.
  - Each storm's t0 and hours were put only into the runner's copy of `catalog.json` for w9's storm lookup; that copy was never committed.
- **Roads.** OSM (Geofabrik extract of 25 Oct 2026), split like the District 3 graph, with the District 3 class convention:
  `proto/transfer_d456.py osm-roads`.
- **Scoring.** `score_v2.py --d456`: strict 30 m match, 150 m sites, exact chance, and a two-stage bootstrap (2000 replicates, 90 % CIs). The
  rule + watch tier was recomputed the same way for District 3 and Districts 4–6. Gauges came from `proto/score.py`.
- **Scored once.** The CI collect job wrote `score_d456.json`, then failed in a later formatting step (a dictionary key name). The summary was
  finished locally from that same `score_d456.json`. Nothing was rerun or changed.

## 2. Pooled result vs District 3 (box-wide, parity physics)

| | **Districts 4–6 (81 storms, 498 sites)** | District 3 held-out 23 (98 sites; `obs/round2/score_round2.json`) |
|---|---|---|
| rule (p_close ≥ 0.5): mean share flagged | 0.14 % | 0.43 % |
| rule: site recall [90 % CI] | **0.036** [0.015, 0.058] (18 sites) | 0.092 [0.022, 0.167] |
| rule: lift [CI] | **6.7** [3.2, 10.6] | 6.4 [2.2, 10.6] |
| rule: FSS 300 m (pooled) | 0.045 [0.018, 0.077] | 0.051 [0.017, 0.085] |
| top 1 % / 2 % / 5 % / 10 %: recall (lift) | 0.10 (3.3) / 0.16 (2.7) / 0.28 (2.0) / 0.40 (1.5) | – / – / – / 0.44 (2.2) |
| **top 3 %: site recall [CI]** | **0.210 [0.167, 0.254]** (104.8 of 498) | 0.204 [0.104, 0.303] |
| top 3 %: chance recall | 0.086 | 0.066 |
| **top 3 %: lift [CI]** | **2.46 [1.96, 2.97]** | 3.10 [1.57, 4.60] |
| top 3 %: FSS 300 m [CI] | 0.017 [0.014, 0.022] (random 0.023) | 0.023 [0.015, 0.034] |
| PR-AUC, site level (storm mean) | 0.006 | 0.010 |
| rule + watch tier: recall / mean share / lift | 0.139 / 0.92 % / 4.5 | 0.337 / 3.05 % / 4.3 |
| gauges: mean per-storm abs rise error / bias | 0.35 m / −0.27 m (74 storms, 417 gauges) | 0.38 m / −0.36 m (22 storms, 37 gauges) |
| gauges with zero model rise | 234 / 417 | 12 / 37 |
| peak timing, mean per-storm abs (h) | 7.8 | 8.4 |

**Verdict under the pre-registered rule: *Transfers*.** The 3 % lift CI lower bound is 1.96, above 1. The pooled 3 % recall (0.210) is
not below the District 3 held-out lower bound (0.104).

Reading the table:

- **The 3 % budget.** Recall is the same as in District 3. Lift is lower because chance is higher: OSM cuts roads into about 1.7 times as
  many, shorter segments, so a site covers more segments.
- **The rule.** It is as precise per flag as in District 3, but it flags a third as much and catches about 40 % as many sites.
- **The watch tier.** It also fires less here (0.9 % of segments vs 3.0 %) with the same lift, so it adds about 10 points of recall
  instead of about 25.
- **Gauges.** Errors are similar. The legacy bBox query takes every gauge in the box, while District 3 used its catalogue gauges, so the
  counts are not like for like. Most zero-rise gauges barely rose in reality either (median observed rise 0.25 m; 56 % under 0.3 m).

## 3. Breakdowns (descriptive; not part of the verdict)

| group | sites | rule recall (lift) | 3 % recall (lift) | 10 % recall (lift) |
|---|---|---|---|---|
| District 4 (MetroWest / North Shore / Merrimack) | 202 | 0.035 (5.7) | 0.175 (2.1) | 0.38 (1.5) |
| District 5 (SE MA / South Shore / Cape) | 159 | 0.038 (8.9) | 0.226 (2.8) | 0.43 (1.7) |
| District 6 (Boston metro) | 137 | 0.036 (6.5) | 0.244 (2.6) | 0.38 (1.4) |
| AWS-era rain (MRMS Pass2, 37 storms) | 230 | 0.048 (6.2) | 0.233 (2.9) | 0.43 (1.8) |
| IEM-era rain (GaugeCorr, 44 storms) | 268 | 0.026 (7.7) | 0.191 (2.1) | 0.37 (1.4) |
| sites with NWS labels only | 440 | 0.034 (6.2) | 0.213 (2.4) | 0.41 (1.5) |
| sites with a SeeClickFix / 311 label | 58 | 0.052 (12.0) | 0.193 (3.7) | 0.28 (1.7) |

- No district stands out: all three sit at 3 % lift 2.1–2.8.
- Storms after Oct 2020 (AWS Pass2 rain) score a little better than the 2018–2020 GaugeCorr storms, as in District 3.
- 26 of the 81 storms have no site in the top 3 %. Most of them are 3–5-site storms.
- Inside the reporting towns only, the 3 % recall is 0.195 (lift 2.3).

## 4. Road-source control (same physics, two road networks)

Both control storms are District 3 held-out storms, rerun on their catalogue boxes with the frozen settings. The rerun reproduced the
published parity hydraulics exactly (identical `hmax_stats.json`). Scored on `graph_segments.json`, it reproduced the published scores
exactly too.

| storm | road network | segments | sites | rule share / hits | 3 % hits / recall / lift | FSS300 at rule |
|---|---|---|---|---|---|---|
| sep2021 Worcester | MassDOT graph (District 3) | 7,775 | 8 | 2.41 % / 3 | 4 / 0.50 / 8.0 | 0.078 |
| sep2021 Worcester | OSM (as used for Districts 4–6) | 13,177 | 8 | 1.88 % / 2 | 3 / 0.38 / 4.0 | 0.023 |
| aug2023 MetroWest | MassDOT graph | 6,679 | 6 | 1.62 % / 1 | 1 / 0.17 / 2.6 | 0.007 |
| aug2023 MetroWest | OSM | 10,795 | 6 | 0.76 % / 0 | 0 / 0 / 0 | 0.000 |

Switching the road source alone costs 2 of 14 sites at 3 % and halves the lift. The likely cause is that OSM splits roads more finely, so
segments are shorter and more numerous. This affects ranking and chance at a fixed share. It also affects the depth read on each segment,
which is the top-2 point depth per segment. With only two storms, this control is indicative, not a correction. Nothing was adjusted on it.

## 5. Per storm

Columns:
- **Sites:** strict-matched sites in the box.
- **Rule:** share flagged / sites hit / lift.
- **3 %:** sites hit (averaged over 5 tie seeds) / recall (chance) / lift.
- **Gauges:** number of USGS gauges in the box / mean abs rise error / bias / mean abs peak timing.

| storm | district | sites | rule: share / hits / lift | 3 %: hits / recall (chance) / lift | FSS300 rule (chance) | rule + watch: share / hits | gauges: n / mean abs rise err (m) / bias / timing (h) |
|---|---|---|---|---|---|---|---|
| apr2018e | 4 | 3 | 0.01 % / 0 / 0.0 | 0.0 / 0.00 (0.11) / 0.0 | 0.000 (0.000) | 0.5 % / 0 | 7 / 0.50 / -0.50 / 9.7 |
| apr2018f | 6 | 5 | 0.09 % / 0 / 0.0 | 1.0 / 0.20 (0.12) / 1.7 | 0.064 (0.006) | 0.7 % / 0 | 11 / 0.51 / -0.51 / 11.1 |
| apr2019e | 5 | 3 | 0.02 % / 0 / 0.0 | 0.0 / 0.00 (0.08) / 0.0 | 0.000 (0.004) | 0.1 % / 0 | 8 / 0.24 / -0.24 / 7.3 |
| apr2022e | 5 | 5 | 0.01 % / 0 / 0.0 | 1.0 / 0.20 (0.06) / 3.1 | -0.000 (0.000) | 0.3 % / 0 | 2 / 0.28 / 0.05 / 9.2 |
| aug2018e | 5 | 4 | 0.07 % / 1 / 147.4 | 3.0 / 0.75 (0.07) / 10.3 | 0.086 (0.005) | 1.4 % / 2 | 0 / – / – / – |
| aug2018f | 5 | 3 | 0.00 % / 0 / – | 1.0 / 0.33 (0.05) / 6.8 | 0.000 (0.000) | 0.0 % / 0 | 1 / 1.46 / -1.46 / 6.5 |
| aug2018g | 5 | 7 | 0.00 % / 0 / – | 1.0 / 0.14 (0.09) / 1.7 | 0.000 (0.000) | 0.1 % / 0 | 1 / 0.48 / -0.48 / 8.5 |
| aug2018h | 5 | 4 | 0.00 % / 0 / – | 1.0 / 0.25 (0.11) / 2.2 | 0.000 (0.000) | 0.2 % / 0 | 0 / – / – / – |
| aug2018k | 4 | 3 | 0.00 % / 0 / – | 1.0 / 0.33 (0.10) / 3.5 | 0.000 (0.000) | 0.2 % / 0 | 5 / 0.16 / -0.13 / 5.5 |
| aug2018n | 4 | 38 | 0.45 % / 4 / 7.6 | 10.0 / 0.26 (0.09) / 3.0 | 0.118 (0.061) | 1.8 % / 12 | 4 / 0.26 / -0.26 / 11.7 |
| aug2018p | 5 | 3 | 0.00 % / 0 / – | 0.0 / 0.00 (0.08) / 0.0 | 0.000 (0.000) | 0.0 % / 0 | 0 / – / – / – |
| aug2019e | 5 | 5 | 0.01 % / 0 / 0.0 | 1.0 / 0.20 (0.10) / 1.9 | 0.000 (-0.000) | 0.1 % / 0 | 2 / 0.02 / -0.02 / 9.0 |
| aug2019f | 4 | 5 | 0.12 % / 0 / 0.0 | 0.0 / 0.00 (0.10) / 0.0 | 0.042 (0.020) | 1.3 % / 0 | 7 / 0.62 / -0.57 / 8.0 |
| aug2021e | 4 | 10 | 0.44 % / 3 / 25.2 | 5.0 / 0.50 (0.08) / 6.5 | 0.138 (0.029) | 3.2 % / 5 | 6 / 0.58 / -0.58 / 5.3 |
| aug2022e | 5 | 6 | 0.00 % / 0 / – | 1.0 / 0.17 (0.09) / 1.8 | 0.000 (0.000) | 0.3 % / 0 | 1 / 0.35 / 0.35 / 0.5 |
| aug2023e | 4 | 11 | 1.57 % / 0 / 0.0 | 0.0 / 0.00 (0.07) / 0.0 | 0.006 (0.030) | 5.3 % / 2 | 3 / 1.39 / 0.78 / 5.6 |
| aug2023f | 6 | 7 | 0.28 % / 0 / 0.0 | 2.0 / 0.29 (0.06) / 4.9 | 0.002 (0.008) | 1.9 % / 0 | 17 / 0.44 / -0.38 / 6.1 |
| aug2023g | 5 | 5 | 0.05 % / 0 / 0.0 | 1.0 / 0.20 (0.09) / 2.2 | -0.000 (0.042) | 1.0 % / 0 | 2 / 0.14 / -0.01 / 9.8 |
| aug2023h | 4 | 5 | 0.06 % / 0 / 0.0 | 1.0 / 0.20 (0.05) / 3.8 | 0.126 (0.012) | 1.0 % / 2 | 5 / 0.39 / -0.10 / 10.7 |
| aug2023k | 6 | 3 | 0.02 % / 0 / 0.0 | 0.0 / 0.00 (0.09) / 0.0 | 0.000 (0.001) | 0.3 % / 0 | 7 / 0.29 / -0.29 / 5.2 |
| jan2018e | 5 | 4 | 0.04 % / 1 / 196.2 | 1.0 / 0.25 (0.09) / 2.7 | 0.224 (0.002) | 1.2 % / 2 | 1 / 0.67 / -0.67 / 0.2 |
| jan2018f | 6 | 6 | 0.13 % / 0 / 0.0 | 0.0 / 0.00 (0.07) / 0.0 | 0.000 (0.013) | 0.5 % / 0 | 19 / 0.34 / -0.34 / 11.8 |
| jul2018e | 6 | 3 | 0.41 % / 0 / 0.0 | 0.0 / 0.00 (0.05) / 0.0 | 0.000 (0.005) | 1.1 % / 0 | 16 / 0.43 / -0.43 / 9.1 |
| jul2018f | 6 | 6 | 0.00 % / 0 / – | 1.6 / 0.27 (0.14) / 1.9 | 0.000 (0.000) | 0.3 % / 1 | 6 / 0.45 / -0.44 / 6.5 |
| jul2018g | 4 | 6 | 0.00 % / 0 / – | 1.0 / 0.17 (0.08) / 2.2 | 0.000 (0.000) | 0.0 % / 0 | 4 / 0.33 / -0.33 / 9.1 |
| jul2018h | 4 | 4 | 0.00 % / 0 / – | 0.0 / 0.00 (0.10) / 0.0 | 0.000 (0.000) | 0.0 % / 0 | 6 / 0.13 / -0.13 / 6.4 |
| jul2019e | 6 | 3 | 0.32 % / 0 / 0.0 | 1.0 / 0.33 (0.08) / 4.3 | 0.000 (0.027) | 0.7 % / 0 | 14 / 0.16 / -0.16 / 7.9 |
| jul2019f | 5 | 4 | 0.03 % / 0 / 0.0 | 1.0 / 0.25 (0.11) / 2.3 | 0.000 (0.008) | 0.7 % / 1 | 2 / 0.18 / -0.18 / 8.9 |
| jul2019g | 5 | 9 | 0.01 % / 0 / 0.0 | 2.0 / 0.22 (0.09) / 2.5 | 0.000 (0.000) | 0.2 % / 1 | 2 / 0.06 / -0.06 / 12.2 |
| jul2019h | 4 | 4 | 0.00 % / 0 / – | 0.2 / 0.05 (0.08) / 0.6 | 0.000 (0.000) | 0.0 % / 0 | 5 / 0.19 / -0.19 / 10.5 |
| jul2020e | 4 | 11 | 0.00 % / 0 / – | 1.0 / 0.09 (0.07) / 1.2 | 0.000 (0.000) | 0.1 % / 0 | 4 / 0.43 / -0.40 / 5.8 |
| jul2020f | 4 | 3 | 0.00 % / 0 / – | 0.0 / 0.00 (0.06) / 0.0 | 0.000 (0.000) | 0.5 % / 0 | 2 / 0.69 / -0.69 / 4.6 |
| jul2020g | 4 | 4 | 0.00 % / 0 / – | 0.0 / 0.00 (0.09) / 0.0 | 0.000 (0.000) | 0.7 % / 0 | 1 / 0.03 / -0.03 / 10.5 |
| jul2021e | 4 | 5 | 0.13 % / 0 / 0.0 | 0.0 / 0.00 (0.12) / 0.0 | 0.002 (0.009) | 2.1 % / 1 | 7 / 0.70 / -0.61 / 6.7 |
| jul2021f | 6 | 4 | 0.00 % / 0 / – | 1.0 / 0.25 (0.06) / 4.2 | 0.000 (0.000) | 0.1 % / 0 | 8 / 0.35 / -0.34 / 9.5 |
| jul2021g | 6 | 5 | 0.13 % / 0 / 0.0 | 1.0 / 0.20 (0.08) / 2.7 | 0.011 (0.017) | 1.1 % / 0 | 8 / 0.56 / -0.56 / 9.6 |
| jul2021h | 4 | 6 | 0.02 % / 0 / 0.0 | 3.0 / 0.50 (0.06) / 8.5 | 0.001 (0.000) | 1.3 % / 1 | 2 / 0.29 / -0.29 / 5.4 |
| jul2021k | 4 | 4 | 0.00 % / 0 / – | 1.0 / 0.25 (0.08) / 3.2 | 0.000 (0.000) | 0.1 % / 0 | 2 / 0.10 / -0.07 / 14.2 |
| jul2023e | 5 | 5 | 0.08 % / 0 / 0.0 | 2.0 / 0.40 (0.05) / 8.4 | 0.000 (0.010) | 1.0 % / 3 | 2 / 0.39 / -0.39 / 11.8 |
| jul2023f | 4 | 4 | 0.00 % / 0 / 0.0 | 1.0 / 0.25 (0.09) / 2.9 | 0.000 (-0.000) | 0.2 % / 0 | 5 / 0.35 / -0.35 / 9.3 |
| jul2023g | 5 | 4 | 0.02 % / 0 / 0.0 | 0.0 / 0.00 (0.04) / 0.0 | -0.000 (0.000) | 0.6 % / 0 | 8 / 0.23 / -0.23 / 9.3 |
| jul2023h | 5 | 3 | 0.00 % / 0 / – | 0.0 / 0.00 (0.06) / 0.0 | 0.000 (0.000) | 0.2 % / 0 | 0 / – / – / – |
| jul2023k | 4 | 8 | 0.01 % / 0 / 0.0 | 1.0 / 0.12 (0.07) / 1.7 | -0.000 (-0.000) | 0.9 % / 1 | 3 / 0.11 / -0.09 / 10.6 |
| jul2023n | 6 | 13 | 0.05 % / 0 / 0.0 | 3.0 / 0.23 (0.13) / 1.7 | 0.000 (0.024) | 0.5 % / 2 | 7 / 0.28 / -0.22 / 7.5 |
| jul2023p | 6 | 5 | 0.06 % / 0 / 0.0 | 3.0 / 0.60 (0.14) / 4.3 | 0.000 (0.011) | 0.3 % / 2 | 9 / 0.37 / -0.37 / 10.7 |
| jul2023q | 6 | 21 | 0.22 % / 2 / 12.4 | 7.6 / 0.36 (0.10) / 3.7 | 0.201 (0.046) | 1.6 % / 5 | 9 / 0.38 / -0.30 / 9.1 |
| jul2023r | 4 | 5 | 0.04 % / 0 / 0.0 | 1.0 / 0.20 (0.09) / 2.2 | 0.000 (0.002) | 1.3 % / 1 | 2 / 0.34 / -0.30 / 5.0 |
| jul2025e | 6 | 12 | 0.63 % / 2 / 10.0 | 3.0 / 0.25 (0.08) / 3.3 | 0.261 (0.059) | 1.9 % / 3 | 10 / 0.37 / -0.35 / 5.5 |
| jun2018e | 4 | 3 | 0.08 % / 0 / 0.0 | 1.0 / 0.33 (0.07) / 4.9 | 0.000 (0.000) | 0.3 % / 0 | 13 / 0.24 / -0.23 / 8.7 |
| jun2018f | 4 | 12 | 0.08 % / 0 / 0.0 | 1.0 / 0.08 (0.13) / 0.7 | 0.000 (0.032) | 0.2 % / 0 | 10 / 0.21 / -0.18 / 9.6 |
| jun2019e | 6 | 4 | 0.00 % / 0 / 0.0 | 0.8 / 0.20 (0.08) / 2.5 | 0.000 (-0.000) | 0.0 % / 0 | 7 / 0.20 / -0.20 / 9.1 |
| jun2020e | 5 | 6 | 0.00 % / 0 / – | 5.0 / 0.83 (0.08) / 10.8 | 0.000 (0.000) | 0.2 % / 2 | 8 / 0.10 / -0.09 / 6.8 |
| jun2020f | 6 | 5 | 0.38 % / 0 / 0.0 | 1.0 / 0.20 (0.06) / 3.4 | 0.005 (0.017) | 0.8 % / 0 | 13 / 0.19 / -0.18 / 8.0 |
| jun2020g | 5 | 5 | 0.02 % / 0 / 0.0 | 0.0 / 0.00 (0.10) / 0.0 | 0.032 (0.000) | 0.8 % / 1 | 4 / 0.50 / -0.49 / 3.9 |
| jun2026e | 5 | 5 | 0.42 % / 0 / 0.0 | 1.0 / 0.20 (0.10) / 2.1 | 0.000 (0.025) | 2.8 % / 1 | 1 / 0.54 / 0.54 / 0.0 |
| may2018e | 6 | 5 | 0.04 % / 0 / 0.0 | 0.4 / 0.08 (0.10) / 0.8 | 0.000 (0.016) | 0.1 % / 0 | 9 / 0.35 / -0.35 / 8.6 |
| may2020e | 5 | 6 | 0.00 % / 0 / – | 0.0 / 0.00 (0.10) / 0.0 | 0.000 (0.000) | 0.0 % / 0 | 0 / – / – / – |
| nov2018e | 4 | 3 | 0.00 % / 0 / – | 0.0 / 0.00 (0.07) / 0.0 | 0.000 (0.000) | 0.0 % / 0 | 4 / 0.60 / -0.60 / 12.9 |
| nov2018f | 6 | 3 | 0.02 % / 0 / 0.0 | 0.0 / 0.00 (0.06) / 0.0 | 0.019 (0.002) | 0.2 % / 0 | 8 / 0.31 / -0.31 / 5.4 |
| nov2021e | 4 | 6 | 0.00 % / 0 / – | 0.0 / 0.00 (0.06) / 0.0 | 0.000 (0.000) | 0.4 % / 0 | 2 / 0.56 / -0.56 / 4.4 |
| nov2021f | 4 | 4 | 0.00 % / 0 / 0.0 | 0.0 / 0.00 (0.10) / 0.0 | 0.000 (0.000) | 0.0 % / 0 | 2 / 0.21 / -0.21 / 10.6 |
| oct2018e | 4 | 8 | 0.00 % / 0 / 0.0 | 1.2 / 0.15 (0.09) / 1.7 | 0.000 (0.000) | 0.0 % / 0 | 6 / 0.18 / -0.18 / 10.4 |
| oct2019e | 5 | 10 | 0.15 % / 1 / 16.4 | 4.0 / 0.40 (0.12) / 3.4 | 0.344 (0.019) | 1.6 % / 2 | 2 / 0.22 / -0.22 / 11.2 |
| sep2018e | 6 | 15 | 0.10 % / 0 / 0.0 | 3.0 / 0.20 (0.08) / 2.4 | 0.036 (0.029) | 0.4 % / 0 | 9 / 0.34 / -0.30 / 7.6 |
| sep2018f | 4 | 8 | 0.05 % / 0 / 0.0 | 3.0 / 0.38 (0.08) / 4.8 | 0.002 (0.003) | 1.3 % / 2 | 3 / 0.41 / -0.39 / 9.4 |
| sep2018g | 6 | 6 | 0.09 % / 0 / 0.0 | 1.0 / 0.17 (0.09) / 2.0 | 0.039 (0.006) | 0.9 % / 2 | 9 / 0.50 / -0.50 / 5.0 |
| sep2019e | 4 | 3 | 0.32 % / 0 / 0.0 | 0.0 / 0.00 (0.08) / 0.0 | -0.000 (0.010) | 0.7 % / 0 | 14 / 0.26 / -0.26 / 5.9 |
| sep2019f | 4 | 9 | 0.00 % / 0 / 0.0 | 2.0 / 0.22 (0.09) / 2.5 | 0.000 (0.000) | 0.2 % / 0 | 5 / 0.34 / -0.34 / 8.8 |
| sep2019g | 5 | 4 | 0.00 % / 0 / – | 0.0 / 0.00 (0.07) / 0.0 | 0.000 (0.000) | 0.1 % / 0 | 1 / 0.17 / -0.17 / 15.0 |
| sep2020e | 4 | 3 | 0.00 % / 0 / – | 0.0 / 0.00 (0.07) / 0.0 | 0.000 (0.000) | 0.2 % / 0 | 1 / 0.04 / 0.04 / 0.5 |
| sep2021e | 5 | 5 | 1.48 % / 2 / 10.5 | 3.0 / 0.60 (0.08) / 7.9 | 0.059 (0.027) | 6.4 % / 5 | 0 / – / – / – |
| sep2021f | 6 | 6 | 0.50 % / 1 / 8.8 | 3.0 / 0.50 (0.11) / 4.7 | 0.011 (0.025) | 3.0 % / 2 | 14 / 0.65 / -0.56 / 9.5 |
| sep2022e | 4 | 4 | 0.03 % / 0 / 0.0 | 1.0 / 0.25 (0.06) / 4.3 | 0.000 (0.002) | 0.3 % / 0 | 2 / 0.16 / -0.16 / 7.6 |
| sep2022f | 5 | 4 | 0.01 % / 0 / 0.0 | 0.0 / 0.00 (0.07) / 0.0 | 0.000 (0.000) | 0.2 % / 0 | 2 / 0.08 / -0.08 / 9.5 |
| sep2023e | 5 | 8 | 0.12 % / 0 / 0.0 | 2.0 / 0.25 (0.06) / 4.0 | 0.131 (0.004) | 1.1 % / 1 | 1 / 0.01 / 0.01 / 2.0 |
| sep2023f | 5 | 4 | 0.08 % / 0 / 0.0 | 1.0 / 0.25 (0.06) / 4.3 | -0.000 (0.003) | 0.5 % / 1 | 8 / 0.14 / -0.14 / 8.4 |
| sep2023g | 5 | 6 | 0.06 % / 0 / 0.0 | 1.0 / 0.17 (0.04) / 3.7 | -0.000 (0.004) | 1.2 % / 1 | 3 / 0.44 / -0.44 / 12.5 |
| sep2023h | 5 | 3 | 0.55 % / 0 / 0.0 | 0.0 / 0.00 (0.07) / 0.0 | 0.004 (0.016) | 3.9 % / 0 | 1 / 0.13 / 0.13 / 3.0 |
| sep2026e | 5 | 4 | 0.62 % / 1 / 7.5 | 2.0 / 0.50 (0.15) / 3.3 | 0.051 (0.020) | 4.3 % / 2 | 0 / – / – / – |
| sep2026f | 5 | 6 | 0.01 % / 0 / 0.0 | 1.0 / 0.17 (0.10) / 1.7 | 0.000 (0.000) | 0.7 % / 0 | 1 / 0.22 / -0.22 / 1.0 |
| sep2026g | 5 | 9 | 0.76 % / 0 / 0.0 | 0.0 / 0.00 (0.05) / 0.0 | 0.006 (0.017) | 2.9 % / 0 | 1 / 0.56 / -0.56 / 4.3 |

## 6. Caveats

- **Labels are reports, not inventories.** 389 of the 544 road-level rows are `approx`: the road vertex nearest the NWS point, or a short
  road's centroid. Their uncertainty is about 500 m, and they are matched at 30 m, so individual hits depend on placement. That holds for
  District 3 as well.
- **Boston 311 adds little.** Its open data has few requests whose text says "flood" (4 rows used). SeeClickFix adds 61, but SeeClickFix
  reports often say a drain is clogged rather than that the road was impassable.
- **Gauges.** District 4–6 gauge files come from the legacy WaterServices bBox query, so they include every gauge in the box (about 20 of
  them tidal). District 3 used curated catalogue gauges. Compare the per-storm means, not the counts.
- **Files kept off main.** The OSM road graphs (`roads_osm/`, 61 MB), the per-run `features_<id>.csv.gz` (77 MB) and the gauge series
  (`gauges/`, 15 MB) are on the work branch `transfer-d456` (run r1 collect commit aef36592). They were left off main to keep the
  site deploy small. Rescoring needs them: check them out next to `docs/proto/transfer/r1/` and run
  `TRANSFER_REUSE=0 python proto/transfer_d456.py score --run r1`.

## 7. Files

- `r1/score_d456.json`, `r1/score_d456_table.md`: every metric, per storm and pooled (`score_v2.py --d456`).
- `r1/transfer_summary.json`: per-storm digest, rule + watch tier, gauges, the District 3 reference and the control.
- `r1/<id>_<area>_20m/`: `config.json` (box, t0, hours), `settings.txt`, `flood_meta.json`, `score.json` (gauges), `matches_<id>.json`, `hmax_stats.json`.
- `obs/catalog/mrms_check.json`: MRMS availability per storm.
- `raw/`: the discovery and label audit trail (district polygons, candidates, NWS drafts, geocodes, 311 / SeeClickFix windows, `build_audit.json`).
