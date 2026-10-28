# Paper 1 outline: road-closure screening from radar-driven 2-D flood simulation, evaluated out of sample

Status: outline, 28 Oct 2026. Every number below is copied from a results file in this repo; the file is named next to it. The paper uses
no number that is not in one of those files. References are restricted to those already listed in `docs/proto/ROADMAP_research.md`
(numbered as there, "R#") and `docs/proto/DATA_IDEAS.md` (Sources). If a needed reference is not on those lists, the gap is marked
**[ref needed]**; nothing is invented.

## 1. Working title

**"How well can a physics-only 2-D flood model tell which roads will close? An out-of-sample evaluation over 106 storms in Massachusetts"**

Alternatives:
- "From radar rain to road closures: honest skill, solver parity and network consequences of a 20 m flash-flood screen for a state DOT district"
- "Screening road-segment flood closures with LISFLOOD-FP and MRMS: pre-registered evaluation on held-out and transferred storms"

## 2. Target journals (in order)

| journal | why it fits | risk |
|---|---|---|
| **Natural Hazards and Earth System Sciences (NHESS)** | Its scope is hazard prediction with evaluation against impact data, and it publishes road and pluvial work close to ours: Safaei-Moghadam et al. 2023, roadway pluvial flooding from Waze and DEM depressions (R37), and Bentivoglio et al. 2025, GNN flood surrogates (R34). Open access, open review, and it welcomes negative or weak-skill results that are reported honestly. | Reviewers will ask for a stronger hydrological novelty than "the rule is weak". The parity audit and the transfer test have to carry that weight. |
| **Journal of Hydrology** | Hydrodynamic-modelling audience. Our solver is the Bates et al. 2010 local-inertial scheme (R14, published in this journal), and the parity / time-step finding is a numerical-hydraulics result. Asif et al. 2026 (R33) shows the journal takes urban flash-flood depth-prediction papers. | The impact-label evaluation is less central for this audience. The cascade section would have to shrink. |
| **Transportation Research Record (TRR)** | The practitioner audience (state DOTs). The Norfolk Waze trustworthiness study (R38) is in TRR. The MassDOT District 3 deliverable (`docs/proto/arcgis/`) and the closure-consequence numbers speak to it directly. | Short format (about 7,500 words including tables), and TRB's submission timing. Best as a second, applied paper (see §9). |

Also considered: *Journal of Infrastructure Systems* (ASCE), for a later paper on the cascade / consequence model alone. With the data in
hand, cascade structure does not improve prediction (CASCADE.md §4.2), so it is a consequence paper, not a prediction paper.

## 3. Abstract draft (≤ 250 words; currently 250)

> Agencies need to know which road segments will close in a flash flood, yet road-flood models are usually judged in-sample
> on one or two storms. We evaluate a transparent closure screen for MassDOT Highway District 3, central Massachusetts. LISFLOOD-FP
> local-inertial 2-D simulation at 20 m is driven by hourly MRMS radar rain, and closure probability is Φ((d − 0.30 m)/0.10 m) on modelled
> road depth, with no parameter fitted to closures. A solver audit traced GPU gauge errors to start-up and time-step artefacts;
> with matched physics, CPU and GPU agree cell for cell and the mean gauge rise error over nine storms falls from 0.82 to 0.46 m. Under a pre-registered protocol on 23 held-out storms (98 documented sites), the rule catches 0.092 of sites at 0.43 % of segments
> flagged (lift 6.4). Ranking the top 3 % of segments catches 0.204 [0.104, 0.303] (lift 3.1). On 81
> independent storms in Districts 4–6 (498 sites), the frozen model keeps this skill: top-3 % recall 0.210 [0.167, 0.254], lift 2.46
> [1.96, 2.97]. Spatial skill (FSS at 300 m) is at chance. Learned closure models and network features add 2 to 13 held-out sites but fail
> multiplicity-corrected tests. In the September 2023 storm, 94 % of person-hours of lost emergency coverage fall on people
> whose own road stays dry. A time-lagged HRRR ensemble raises out-of-sample forecast recall from 0.21 to 0.34 at
> long lead. The screen ranks roads usefully but cannot yet issue segment-level warnings; label coverage, not model complexity, limits it.

Sources for each number: gauges 0.82 → 0.46 m and parity `parity/BASELINE.md` §2 and `parity/PARITY.md` "GPU confirmation"; held-out 23
`obs/LABELS_ROUND2.md` §4 and `transfer/TRANSFER.md` §2; Districts 4–6 `transfer/TRANSFER.md` §2; learned / network
`ml/EXPANDED.md` §3 (+11) and `cascade/CASCADE.md` §4.2 (+2 for T3, +13 for T2); 94 % `cascade/CASCADE.md` §2; ensemble
`forecast/ENSEMBLE.md` §4 (long lead = 8–14 h, run at CN × 0.91; see §8).

## 4. Contributions

1. **A pre-registered, storm-held-out evaluation of a physics-prior road-closure screen.** The protocol was frozen before scoring
   (`PROTOCOL.md` v2). The scoring uses an exact chance baseline, a storm-clustered bootstrap and FSS (Roberts & Lean 2008, R39). It is
   applied to 23 held-out storms. Five locked storms are never opened.
2. **A transfer test to 81 independent storms in three other DOT districts**, with frozen settings. It includes a road-network control:
   switching from the MassDOT graph to OSM alone halves the lift.
3. **A solver-parity audit for GPU vs CPU LISFLOOD-FP in rain-on-grid mode.** The audit identifies the time-step policy and the t = 0
   snapshot as the source of spurious depth spikes and gauge "rises". The fix (`LF_PARITY=1`) gives identical floods on both builds. This
   is a practical warning for every GPU rain-on-grid study.
4. **A negative result on learned and network-aware prediction at this label density.** Logistic, pairwise and cascade-feature models
   rank better within storms but do not pass the pre-registered held-out test. The bottleneck is labels, not model capacity.
5. **A consequence ("cascade") model** linking closures to detours, overloaded corridors and lost emergency coverage on the District
   graph. It shows that most impact lands on dry roads.
6. **An open, reproducible pipeline and a DOT-ready layer.** Code, runs and labels are in the repository. The District 3 vulnerability
   layer is in `docs/proto/arcgis/`.

## 5. Structure, section by section

**1. Introduction**
- Road closures are the most frequent flash-flood impact for a DOT. Agencies act on segments, not on inundation maps.
- Prior work: depth thresholds for trafficability (Kramer et al. 2016, R21; Martínez-Gomariz et al. 2018, R20; Smith et al. 2014, R19);
  depth–disruption functions (Pregnolato et al. 2017, R23); data-driven road-flood likelihood (Safaei-Moghadam et al. 2023, R37);
  ML surrogates (Bentivoglio et al. 2025, R34; Asif et al. 2026, R33).
- The gap: few studies test road-segment skill on many held-out storms against documented reports, with chance-corrected metrics.
- Aim and the four questions: skill, transfer, solver robustness, and whether learning or network context helps.

**2. Study area and data**
- MassDOT Highway District 3: road graph of 52,698 segments (`cascade/CASCADE.md` §1); the 25 non-locked catalogue storms (2018–2026);
  81 storms in Districts 4–6.
- Rain: MRMS MultiSensor QPE Pass2 (Zhang et al. 2016, R1); IEM GaugeCorr before Oct 2020. Terrain: 3DEP 10 m. Channels: NHDPlus HR.
  Soils: SSURGO. Imperviousness: NLCD. Crossings: NBI and the MA Stream Crossings Project / NAACC (`advisors/datasets.md`).
- Labels: NWS LSR / Storm Events, news, WX1BOX, Leominster DPW, MassDOT water-surface crashes, SeeClickFix. Tiers and coordinate
  quality, 150 m site clustering and a strict 30 m match (`PROTOCOL.md`, `obs/LABELS_ROUND2.md`).

**3. Methods**
- 3.1 Hydrodynamics: LISFLOOD-FP 8.2 acceleration solver (Bates et al. 2010, R14; de Almeida et al. 2012, R15; Shaw et al. 2021, R16),
  20 m grid, CN loss × 0.88 with 2 mm/h infiltration, `LF_PARITY=1` (`parity/BASELINE.md`). The CN-scale calibration uses a pre-set rule
  on two gauges (BASELINE §1). Curve-number background: Hawkins et al. 2002 (R8).
- 3.2 Closure rule: Φ((d − 0.30)/0.10), d = second-highest road point; freeboard, HDS-5 culvert and fast-water terms; bridge decks read
  their approaches (`STATUS.md` §1).
- 3.3 Evaluation protocol: nested LOSO, held-out 23, exact chance, lift, storm-clustered bootstrap, FSS@300 (R39); spatial / storm
  cross-validation structure after Roberts et al. 2017 (R32); the adoption rule and α/k (`PROTOCOL.md` v2).
- 3.4 Transfer design (pre-registered `PROTOCOL.md` "Transfer test") and the road-source control.
- 3.5 Learned candidates: v1 logistic, v2 pairwise, two-tier, cascade features (`ml/EXPANDED.md`, `cascade/CASCADE.md` §4). The
  positive–unlabelled framing follows Bekker & Davis 2020 (R28).
- 3.6 Consequence model: Pregnolato depth–speed, shortest-path detours, V/C, coverage loss per Census block (`cascade/CASCADE.md` §1).
- 3.7 Forecast mode: HRRR gate, neighbourhood spreading (Schwartz & Sobash 2017, R6), 8-member time-lagged ensemble, 2-of-8 rule
  (`forecast/ENSEMBLE.md`).

**4. Results**
- 4.1 Solver parity and gauges (Fig. 3, Table 3).
- 4.2 Held-out skill in District 3 (Fig. 5, Table 4).
- 4.3 Transfer to Districts 4–6 and the road-source control (Fig. 6, Table 5).
- 4.4 Learned and network candidates: what failed and by how much (Table 6).
- 4.5 Consequences of the Sept 2023 District run (Fig. 7, Table 7).
- 4.6 Forecast lead time (Fig. 8, Table 8).

**5. Discussion**
- Why ranking works and the fixed threshold does not: under-prediction on light storms (bias negative on 8 of 9 storms; `BASELINE.md` §3).
  Documented sites sit at 10–30 cm, just under the rule.
- Labels as the constraint: approximate coordinates, about 500 m uncertainty (`transfer/TRANSFER.md` §6). Reports are not inventories.
  The 4 of 30 MassDOT repeating sites near a flagged segment (`turing/d3_sep2023_p/REPORT.md`) show drainage-capacity ponding the 20 m
  model does not resolve.
- What a DOT can use now: a ranked watch list and a vulnerability layer, not segment warnings.
- Consequences land on dry roads, so closure maps alone understate impact.

**6. Limitations** (see §8 below).

**7. Conclusions and next steps.** Waze / HOC labels, the locked-set opening, damage labels from a second storm.

**Data and code availability.** Repository, Zenodo snapshot **[to create]**, LISFLOOD-FP source DOI
(https://doi.org/10.5281/zenodo.13121102, from `flood_meta.json`).

## 6. Figures and tables, mapped to data and scripts

| # | content | data | script |
|---|---|---|---|
| Fig. 1 | Study area: District 3 graph, 25 catalogue boxes, the District run box (128–206 km E, 856–946 km N, EPSG:26986), 81 District 4–6 boxes | `docs/graph_segments.json`, `obs/catalog.json`, `obs/catalog_d456.json`, `turing/d3_sep2023_p/flood_meta.json` | **to write** (`proto/paper_figs.py fig1`) |
| Fig. 2 | Pipeline: rain → 2-D flood → road depth → p_close → scoring / cascade / forecast | `advisors/pipeline.html` | redraw from pipeline.html |
| Fig. 3 | Parity: Fitchburg and Leominster hydrographs, GPU default vs `LF_PARITY=1` vs CPU vs observed; depth-spike example (Hampton St) | `parity/<storm>_<variant>/gauge_windows.npz`, `parity/parity.json`, `turing/parity_sep2023_gpu_rain*/` | `proto/parity_compare.py` (numbers); plot **to write** |
| Fig. 4 | CN-scale calibration: rise error and flagged share against `LF_CN_SCALE` | `parity/calib/leo48_cn0{85..100}/score.json`; table in `parity/BASELINE.md` §1 | **to write** |
| Fig. 5 | Held-out 23: site recall against flagged share (1–10 %), rule point, chance line, 90 % CI | `obs/round2/score_round2.json` | `proto/score_v2.py --catalog` (numbers); plot **to write** |
| Fig. 6 | Transfer: recall and lift curves for Districts 4–6 vs District 3; per-district bars | `transfer/r1/score_d456.json`, `transfer/r1/transfer_summary.json` | `proto/score_v2.py --d456`; plot **to write** |
| Fig. 7 | Sept 2023 District run: depth map with flagged segments; cascade time series (closed, delay, people losing coverage, dry-road share) | `turing/d3_sep2023_p/figure.png` (existing, `prototype.write_figure`), `docs/site/data/d3_sep2023/cascade.json` `series` | existing figure + `proto/cascade.py pack d3_sep2023`; plot **to write** |
| Fig. 8 | Forecast: recall and flagged share by rule (single, any-of-4, 2-of-4, 2-of-8) at long / short lead, 7 OOS storms | `forecast/ensemble.json` (`pooled`) | `proto/forecast_ens.py report`; plot **to write** |
| Fig. 9 (SI) | District 3 vulnerability layer (High / Medium / Low) | `docs/proto/arcgis/d3_road_flood_vulnerability.geojson` | `proto/arcgis_export.py` |
| Fig. 10 (SI) | Learned-model reliability and coefficient importance (LOSO) | `parity/catalog/ml/loso_reliability.png`, `loso_importance.png` | `proto/closure_loso.py` (existing figures) |
| Table 1 | Data sources | `advisors/datasets.md` / `datasets.csv` | – |
| Table 2 | Storm catalogue: 25 District 3 storms (dev 2 / held-out 23 / locked 5 not used) and 81 District 4–6 storms | `obs/catalog.json`, `obs/CATALOG_D456.md` | – |
| Table 3 | Old GPU vs parity baseline per storm: sites, flagged share, lift, gauge error | `parity/BASELINE.md` §2 | – |
| Table 4 | Held-out 23 skill before and after label round 2, OOS-7 sub-pool | `obs/LABELS_ROUND2.md` §4, `obs/round2/score_round2.json` | `proto/score_v2.py --catalog` |
| Table 5 | Districts 4–6 vs District 3 (pooled) and the road-source control | `transfer/TRANSFER.md` §2, §4 | `proto/score_v2.py --d456` |
| Table 6 | Pre-registered candidates and verdicts (EXPANDED a–d; cascade T1–T3) | `ml/EXPANDED.json`, `cascade/CASCADE_ML.json` | `proto/score_v2.py --compare …` |
| Table 7 | Cascade totals for 3 runs | `cascade/CASCADE.md` §2, `docs/site/data/*/cascade.json` | `proto/cascade.py pack` |
| Table 8 | Forecast ensemble pooled results | `forecast/ENSEMBLE.md` §4, `forecast/ensemble.json` | `proto/forecast_ens.py report` |

## 7. The honest results to report (exact numbers and their source)

**Solver parity and calibration** (`parity/PARITY.md`, `parity/BASELINE.md`)
- GPU vs CPU with `LF_PARITY=1`: flagged segments identical (J 1.0) and mean depth difference 0.000 m on jul2023 and sep2023. Without
  it (rain mode only, default step): 0.63 % vs 0.10 % flagged on jul2023 (J 0.16).
- GPU spikes: 28 of 43 GPU-flagged segments on jul2023 have hmax more than 0.10 m above every snapshot. The CPU has 0 of 7.
- CN scale 0.88 chosen by the pre-set rule. Its mean abs rise error is 0.22 m, tied with 0.85, on the Leominster box.
- Catalogue (9 storms): mean per-storm gauge rise error 0.82 → 0.46 m; zero-rise gauges 9/16 → 3/16; sites 38/119 → 41/132; mean
  flagged share 2.13 % → 1.07 %.
- Bias is negative on 8 of 9 storms (Elsa −1.32 m, Ida −1.00 m). The light storms get no rule hits (0 of 20 sites).

**Held-out District 3** (`ml/EXPANDED.md` §3; `obs/LABELS_ROUND2.md` §4; `STATUS.md` §2)
- Labels before round 2 (90 sites). Rule: 5/90 = 0.056 [0.01, 0.11] at 0.43 % flagged, lift 4.8. Top 3 %: 15/90 = 0.167 [0.08, 0.26],
  chance 0.064, lift 2.6. FSS@300 0.019.
- After round 2 (98 sites; a measurement change, not a model gain): rule 0.092, lift 6.4; top 3 % 0.204 [0.104, 0.303], lift 3.1;
  top 10 % 0.443.
- 16 new storms alone: the rule catches 1 of 58 sites; mean flagged share 0.23 % (`scoring/BASELINE_v2_expanded.md`).
- Gauges: 0.31 m mean per-storm rise error on 15 storms / 26 gauges, bias −0.28 m (`scoring/BASELINE_v2_expanded.md`).
- In-sample Leominster numbers (for example 35/89 at 1.97 %, lift 12.8 on the headline box) are dev storms. They are **never** the
  headline.

**Transfer, Districts 4–6** (`transfer/TRANSFER.md`)
- 81 storms, 498 sites. Top 3 %: 0.210 [0.167, 0.254], chance 0.086, lift 2.46 [1.96, 2.97]. Verdict: *transfers* under the
  pre-registered rule.
- Rule: 0.036 [0.015, 0.058] (18 sites) at 0.14 % flagged, lift 6.7 [3.2, 10.6].
- FSS 300 m at 3 %: 0.017, against 0.023 for random flagging.
- Gauges: 0.35 m mean abs rise error, bias −0.27 m (74 storms, 417 gauges); 234 / 417 with zero model rise.
- Road-source control: MassDOT → OSM costs 2 of 14 sites at 3 % and halves the lift.
- 26 of 81 storms have no site in the top 3 %.

**Learned and network candidates** (`ml/EXPANDED.md`; `cascade/CASCADE.md` §4.2; `parity/BASELINE.md` §4)
- None passes PROTOCOL v2. Best candidate, rule + learned watch at 3 %: 26/90 = 0.289 [0.19, 0.39], lift 4.5. One-sided P ≈ 0.014
  against α = 0.01.
- Cascade features: T2 20 → 33 hits at 3 %, lower bound 0.000. T3 against the same model without the features: +2 sites, lower bound
  −0.076. Step (b) (graph model) was not run because the gate failed.
- Within-storm ranking: mean per-storm ROC-AUC on held-out 23 is 0.673 (rule), 0.763 (`a_v1`), 0.762 (`cas_v1`).

**Consequences** (`cascade/CASCADE.md` §2, `d3_sep2023`)
- Peak 112 segments closed at 9.0 h. 166,239 vehicle-hours (85,586 detour / 80,653 slow); $5.0M user cost.
- Peak 51,421 people losing a service (H 16,982 / F 38,189 / P 31,846); 11,077 isolated. 94 % of person-hours lost fall on dry roads.
- Spread ratio 4.5. 290 crossings overtopped, $27–152M replacement-cost exposure (exposure, not loss).
- These are scenario consequences with no traffic assignment, and lower bounds from the pack. They are not validated.

**Forecast** (`forecast/ENSEMBLE.md` §4; `STATUS.md` §4 a3; `forecast/DISTRICT.md`)
- 7 OOS storms, 29 sites. 2-of-8 against the single cycle: long lead 0.207 → 0.345 (lift 5.27 → 5.43), short lead 0.069 → 0.276
  (lift 2.71 → 5.7). It is never worse on the 14 storm-lead cases.
- District-wide hindcast (18z HRRR, 20 km / p90): 888 segments (615 km) flagged against 276 (197 km) for radar. That is about 3×
  over-forecast; the spreading setting is pre-registered for a fix (`DISTRICT.md`).

**Crossing damage** (`damage/DAMAGE.md`; supplement only)
- Stream power ranks Leominster damage at ROC-AUC 0.78 against 0.68 for overtopping, but the interval includes 0 [−0.06, +0.19].
  PR-AUC 0.155 vs 0.094, interval [+0.005, +0.16]. One labelled storm. Not adopted.

## 8. Limitations to state in the paper

- **Labels.** Reports, not inventories: a site absent from the reports is not a dry road (positive-unlabelled; R28). Most new rows are
  `approx` (about 500 m uncertainty) matched at 30 m. Few sites per storm (2–5 on many storms).
- **Light-storm under-prediction.** One global CN scale tuned on Leominster under-predicts gauge rise elsewhere. T4 antecedent-moisture
  tests B0 and C are unfinished (`STATUS.md` §3).
- **Not modelled:** storm drains (default off; `drains/DRAINS.md`), dams (`exp/DAMS_2026-10-22.md`), sub-hourly rain.
- **Spatial skill at chance** (FSS). The screen ranks; it does not place floods at 300 m accuracy.
- **Road network.** Districts 4–6 use OSM, which biases lift down. 25 % of District 3 AADT values are defaults (`advisors/datasets.md`
  D14). The graph build script is not in the repo.
- **Forecast numbers were run at CN × 0.91 with the default step**, before the parity baseline (`STATUS.md` §2). They must be rerun at
  `LF_PARITY=1`, CN × 0.88 before submission, or reported as such.
- **Cascade:** no equilibrium assignment, flat daily traffic profile, class capacities, OSM facilities, night-time population. No
  validation data.
- **Development storms** (sep2023, aug2021) were used for design choices, so they are reported separately.

## 9. What is still needed before submission

1. **MassDOT data.** Waze partner alerts and the Highway Operations Center event log for 2018–2026 (`DATA_IDEAS.md` §0 item 4;
   `STATUS.md` §4b: "Waze data via Prof. Tao: on hold"). These are the only realistic source of more sites and of labelled false alarms.
   The paper can go without them, but Waze is the single largest expected improvement in the label base. Re-score on held-out 23 with
   no rule change first.
2. **Open the locked test set once** (aug2015, aug2018, aug2020, jul2018, oct2016), after the model is frozen (`PROTOCOL.md` §2). Report
   the result whatever it is. This gives the paper a truly untouched test.
3. **Rerun the forecast evaluation** (`ENSEMBLE.md` §4) at the deployed parity settings. Settle the District-wide spreading decision
   (`forecast/DISTRICT.md`).
4. **Finish or drop T4** (B0 / C antecedent moisture) as a PROTOCOL v2 pre-registration. Either way, state it.
5. **Figure scripts** (`proto/paper_figs.py`) for Figs. 1, 3–8, from the committed JSON only.
6. **A frozen, citable snapshot**: tag the commit, Zenodo DOI, and the data licence for each label source (`DATA_IDEAS.md` Sources).
7. **Literature gaps marked [ref needed].** Prior road-segment closure-skill studies, and DOT flood-closure practice. Only the R# list
   is currently cited. Add sources the owner has reviewed; do not cite from memory.
8. **Advisor review** of the framing and the journal choice (Prof. Tao, Prof. Albano, Prof. Graff), and a decision on whether the
   transfer test or the parity audit leads the paper.
9. Optional: a second damage-labelled storm (Vermont July 2023 or FEMA PA sites; `damage/DAMAGE.md`), only if the damage layer moves
   from the supplement into the paper.
