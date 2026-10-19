# Ideas backlog — ranked (pass of 19 Oct 2026)

Ranked by (expected gain × confidence) / effort, with the steep-reach high bias first because every downstream product (surrogate corpus, crossings L2,
road warnings) inherits it. Effort: **S** ≤ 1 day, **M** 2–5 days, **L** > 1 week. Data references point to `data_sources.md` (§ numbers).
Every test uses `docs/validation/protocol.md`: reach-level WSE error (bias, MAE, share within ±0.5 m, dry-within-R), road hit rate **next to** the
any-day baseline, gauge peak stage/timing, LOSO + HUC10 splits for anything learned.

**Overfitting guard (proposed protocol amendment, to write down before running the fixes):** South River, Avery Brook and West Brook are now *development*
reaches. Any change motivated by them must also be scored, unchanged, on held-out sets: Whetstone Brook and North Branch Deerfield (VT), the 547 Vermont July
2023 HWMs (§1.7), Sept 2023 (Leominster) and Dec 2023 road reports, Jan 2018 coastal marks, and gauge peaks for all four storms. Report development and held-out
numbers side by side.

---

## A. Diagnose the steep-reach high bias (South River +2.8 m at 10 m; Avery bias +1.8 m; West Brook +0.8 m) and the over-wet Dec 2023 roads

**Status in the repo while this pass was written (commits f76bc5e9, 4c03ab91, 4dc291ea):** South River bias is real under deepest/nearest/median WSE
metrics (+2.2 to +2.8 m); **Avery Brook's bias is mostly the metric** (nearest-wet 0.0 vs deepest +1.8) — so A10 is partly answered. The bed profile shows a
**1.3 m sill in the burnt channel at Conway village and a flat 6 m-deep pool upstream** — direct support for A3 (30 m channel grid misses the 10 m thalweg) and
possibly A2 (if the sill coincides with a crossing). `BREACH=1` (priority-flood carving of channel sills ≤ 4 m) is queued. What this backlog adds: constrain the
carving with **independent inverts** (USIE/DSIE at crossings, §1.5) and the NID dam list (§1.8) so real steps and dams are not carved away, and check discharge
(A1) so a WSE improvement is not hiding a compensating Q error.

A back-of-envelope frame for all hypotheses: for a wide channel at normal depth, h ≈ (n·Q / (W·√S))^(3/5). If the true peak depth on the South River was ~3 m and the
model's is ~5.8 m (+2.8 m), the ratio 1.93 needs **n·Q/W about 3× too large** (1.93^(5/3) ≈ 3.0). No single knob within its plausible range gives 3×
(n × 1.3, Q × 1.3, W × 0.6 each give ~1.3–1.7×), so expect **two or three causes stacked**, or a structural one (a dam in the DEM) that is not captured by this formula.

| # | Hypothesis | Why it would raise WSE | Test (cheap → decisive) | Effort | Data |
|---|---|---|---|---|---|
| **A1** | **Hydrology vs hydraulics split** (diagnostic, do first) | — | Sum face fluxes across a transect at gauges 01169900 (South River nr Conway) and 01171100 (West Brook nr Whately) in the existing 10 m run; compare modelled peak Q and hydrograph with USGS IV and the WY2023 peak (likely an indirect measurement). Also compare modelled stage with gauge stage converted to NAVD88 with the gauge datum. If Q is right and WSE high → A2–A6; if Q is high → A7–A9. | **S** | §1.1, §1.2 |
| **A2** | **Culverts/road fills are digital dams** — the USGS lidar spec removes bridges but keeps culverts and road fill; our burn follows NHD only if the 30 m channel cell happens to cut the fill | Ponding behind every tributary/side-road crossing; backwater into the reach | (1) Longitudinal profile of `z.npy` along the burnt flowline through each reach: list adverse steps > 0.3 m and check if they sit within 30 m of a crossing (`crossings_ma.json`); the crossings module already flagged 23 crossings at 30 m where the channel cell is above the deck. (2) Breach: lower cells along the flowline between USIE and DSIE (§1.5) to the invert line, width = span; rerun the 10 m box. Expect WSE drops concentrated just upstream of crossings; a uniform 2 m drop along the whole reach would point elsewhere. | **S** (1), **M** (2) | §1.5, §1.9 |
| **A3** | **Channel burn misaligned at 10 m** — `channels30` is rasterised at 30 m (`all_touched=True`) and nearest-resampled to 10 m, so the 10 m run burns a 30–60 m band of cells, each D below *its own* elevation; if NHDPlus HR is offset from the lidar thalweg, the burnt trench can sit on a bank/terrace while the real thalweg stays unburnt | Effective conveyance below bank is wrong; flow forced over unburnt terrain | Per reach: share of channel cells whose 10 m DEM elevation exceeds the minimum within 30 m by > 0.5 m (misalignment index); compare `z` at channel cells with crossing inverts USIE/DSIE (§1.5) — a systematic positive offset = bed too high. Fix: snap the burn to the D8 thalweg traced on the 10 m (or 1 m) DEM seeded by NHD, one cell wide, width/depth from geometry. | **S** test, **M** fix | §1.5, §1.9, §1.10 |
| **A4** | **Bankfull geometry too small** — national Bieger 2015 curves (W = 2.70 A^0.352, D = 0.30 A^0.213); for South River at Conway (A ≈ 60–65 km²) that is W ≈ 11–12 m, D ≈ 0.7 m | Too little in-bank conveyance; water goes overbank onto n = 0.08 terrain early | **First look done (19 Oct, local 365-row sample of `crossings_ma.json`, drainage areas 0.03–20 km²):** the MA-regression bankfull values are median **1.27× wider and 0.78× shallower** than Bieger at the same drainage area → bankfull *area* nearly identical (~0.99×). So in-bank geometry is unlikely to explain 2 m at flood depths of several metres; what matters is the valley section, i.e. A3/A2/A10. Still worth: compare with USGS channel measurements at high Q (width/area) at 01169900 and ~20 western gauges, and repeat the comparison on the full statewide crossings file (larger basins). | **S** | §1.3, §1.5 |
| **A5** | **Roughness**: channel n = 0.035 is *low* for steep cobble beds (Jarrett 1984: n = 0.39 S^0.38 R^-0.16 → 0.05–0.10 on 1–4 % slopes; [summary](https://kleinschmidtgroup.com/ras-post/n-values-in-steep-streams)), but floodplain n = 0.08 everywhere may be high for pasture/developed valley floors | Physically, higher channel n raises stage — so the bias is unlikely to be "channel n too high"; floodplain n could contribute | Read the queued N_SCALE ×0.7 / ×1.3 runs against the 3× frame: if ×0.7 reduces the bias by ≤ 25 %, roughness is not the main cause. Then a land-cover n map from MassGIS 1 m (§3.1). Back-calculate channel n from USGS measurements (§1.3) and the FIS (§1.6). Note: local-inertial calibrated n is *effective* (Cea & Bladé 2015), keep it out of physical claims. | **S** | §1.3, §1.6, §3.1 |
| **A6** | **Local-inertial numerics on a stepped bed** — LInA is outside its validity for Fr > ~0.5–0.8 and over bed discontinuities comparable to the depth ([Cozzolino et al. 2019](https://arxiv.org/abs/1904.12564)); our Fr ≤ 2 cap clips flux and θ = 0.7 adds diffusion; single-step spikes inflate `hmax` | Flux limiting → depth builds to pass the flow; spikes inflate peaks | (1) `hsnap` vs `hmax` (queued). (2) Log the share of channel faces at the Fr cap during the peak hour. (3) **Reference run**: same 10 m box, same inflow/rain, in a full-SWE GPU solver (TRITON or SERGHEI open source; or HEC-RAS 2D SWE-EM on a sub-box) — if full SWE gives a much lower WSE with identical geometry/n, the local-inertial scheme is the cause and a hybrid scheme (B3) is justified. | **S** (1–2), **M** (3) | — |
| **A7** | **MRMS rain too high in the hill towns** (beam blockage / bright band over the Berkshires; CSU found MRMS overestimation in mountains, worse far from radar) | More runoff → more Q | MRMS 48-h totals at CoCoRaHS/COOP sites in Conway, Ashfield, Goshen, Williamsburg, Shelburne vs gauge catches; plot ratio vs RQI (§2.2). Run rain ×0.8 member on the South River box and check Q at 01169900 (A1). | **S** | §2.1, §2.2 |
| **A8** | **Too much runoff: storage cap too small / deep drainage too slow** — `Scap` uses aws0100 cut by brockdepmin/wtd and `KDEEP` 0.5–5 mm/h by hydgrp; till-over-bedrock vs stratified drift is not represented | Q too high | Queued ANTE ×0.5 / KDEEP ×3 runs; judge by Q at the gauge (A1), not by WSE alone. Add surficial-geology KDEEP/Scap (§3.3). | **S** | §3.3 |
| **A9** | **Hillslope routing too efficient** — n = 0.08 sheet flow on steep forest moves water fast; no subsurface stormflow delay | Sharper, higher peaks | Compare modelled vs observed time of rise and peak at 01169900 / 01171100; a too-early, too-sharp modelled peak with right volume = routing. Test a depth-dependent n (higher for h < 0.1 m, Kalyanapu 2009-style). | **S** | §1.1 |
| **A10** | **Metric / survey artefacts** — deepest cell within 60 m may be a pit or a burnt cell from a parallel tributary; marks are edge-of-water at local superelevation; bed scoured during the event (July 2023 South River widened/avulsed its channel) so the pre-event lidar bed is too high at peak | Apparent bias without a model error | Plot per-mark modelled WSE profile vs surveyed profile along the reach (distance downstream), not just the mean; check that every mark's chosen cell is on the main stem (use the crossings module's largest-drainage-area rule instead of the deepest cell); look for post-2023 lidar or field reports of channel change. | **S** | — |
| **A11** | **Dec 2023 over-wet roads**: road segments sampled by **max** depth over vertices at 30 m pick up channel/ditch water at every stream crossing and artificial ponds behind culvert fills (A2) | Inflated hit rate on all days → poor discrimination (66.7 % vs 59.4 % baseline) | Re-score with (a) channel cells and cells within 30 m of a crossing excluded, (b) mean/p50 instead of max (`roads_mean_cm.npy` already exists), (c) only road-surface cells from MassGIS impervious (§3.1). If discrimination recovers, it was sampling, not physics. Then A2 breaching statewide. | **S** | §3.1 |
| **A12** | **Winter precipitation phase** — MRMS QPE includes snow liquid equivalent; Jan 2018 was largely a blizzard and Dec 2023 had mountain snow, but the engine applies all QPE as instant rain | Over-wet winter runs | Mask with MRMS PrecipFlag (§2.2) and add a degree-day snowpack seeded by SNODAS (§2.6); re-score Dec 2023 roads and Jan 2018. | **S–M** | §2.2, §2.6 |

**Suggested order:** A1 → A10 → A3 test → A2 test → A11 → A7 → read queued A5/A6/A8 runs → A4 (full file + gauges) → fixes (A3, A2) → held-out scoring.

---

## B. Engine accuracy and speed

| # | Idea | Why | Effort | Data | Test |
|---|---|---|---|---|---|
| B1 | **Migrate `sim/gauges_fetch.py` to the USGS OGC Water Data API** and archive peaks/ratings for all MA gauges now | Legacy WaterServices dies Nov 2026 – Q1 2027; inflow injection and gauge validation would silently break | **S** (urgent) | §0 | Re-fetch the four storms and diff against existing `data/gauges/` files. |
| B2 | **Crossing-aware DEM (statewide)**: breach every crossing in the MA inventory to its lidar invert; optionally keep a weir crest at the deck elevation for overtopping | Removes thousands of digital dams; makes the crossings module's freeboard meaningful | **M** | §1.5, §5.1 | Road hit rate and discrimination (Dec/Sept 2023), July reach WSE, crossings "not assessable" count → ~0. |
| B3 | **Hybrid numerics**: keep local-inertial on gentle cells, switch faces with Fr > 0.8 or bed step > 0.5·h to a full-SWE flux (HLL + hydrostatic reconstruction) | Fixes the regime where LInA is invalid without paying full-SWE cost everywhere | **L** | — | A6 reference run as truth; then July reaches + held-out marks. |
| B4 | **Culverts as 1-D links** (HDS-5 inlet control, outlet control, road-overtopping weir) between upstream/downstream cells | Real capacity and backwater; physically correct L2 hazard instead of post-processing | **M** | §1.5, §5.1 (NAACC needs Mo) | Repeating MassDOT flood points; NBI item 71; Dec 2023 reports near crossings. |
| B5 | **MA hydraulic geometry + measured n**: replace Bieger 2015 by regressions fitted to USGS channel measurements (W, A, V vs Q, A_drainage, slope) | Data-driven channel conveyance; publishable as a by-product | **S–M** | §1.3 | A4 + gauge peak stage at all in-box gauges (held-out gauges by HUC10). |
| B6 | **SFINCS-style sub-grid lookup tables** from the 10 m (or 1 m) DEM on a 30 m grid (depth, wet fraction, conveyance per face vs water level) | Van Ormondt et al. 2025 report 35–50× net speed-up for equal accuracy; statewide 30 m with 10 m skill | **L** | §1.9 | Compare 30 m sub-grid vs 10 m explicit on the two test boxes (WSE, CSI of wet area), then statewide runtime. |
| B7 | **Active-cell compute** (skip dry, rain-free tiles) + **HUC8 tiling with inflow coupling** + float16 state where safe | 2–5× fewer cell updates in most storms [estimate]; enables the 20-storm corpus faster | **M** | — | Bit-for-bit (or < 1 cm) agreement with the dense run on a district box; wall-clock. |
| B8 | **Seasonal ET and geology-aware drainage**: GridMET PET for the antecedent store; KDEEP/Scap from surficial materials (till vs stratified drift) | Antecedent and baseflow realism in winter and on valley aquifers | **S** | §2.6, §3.3 | Gauge baseflow before each storm; road reports; Dec 2023. |
| B9 | **Rain uncertainty field**: scale the protocol's rain ensemble per cell by MRMS RQI and the gauge-ratio from A7 | Uncertainty where radar is blind (Berkshires), not uniform ×0.8–1.2 | **S** | §2.1, §2.2 | Spread–skill at gauges; PIT histograms. |

---

## C. ML surrogate, labels and novelty

| # | Idea | Why | Effort | Data | Test |
|---|---|---|---|---|---|
| C1 | **TabPFN coreset baseline** next to LightGBM in `sim/ml/baseline.py` | Huang et al. 2026 show a tabular foundation model matching XGBoost with ~1 % of rows and winning out of distribution; cheap comparison for Paper 1 | **S** | existing table | LOSO + HUC10 CSI/Brier exactly as GBM. |
| C2 | **Multi-fidelity surrogate**: learn 30 m → 10 m correction (U-Net or latent diffusion conditioned on DEM, as Flood-LDM / FIMserv) | Statewide at 30 m cost with 10 m accuracy; complements B6 | **M** | paired 30/10 m runs on boxes | Held-out boxes: WSE vs marks, CSI of wet area vs the 10 m run. |
| C3 | **Positive-unlabelled (PU) learning for road flooding** from weak labels: MassDOT reports + NFIP block groups + Storm Events + Groundsource + 311 | An unreported flooded road is not a negative; current metrics punish true but unreported floods (Google notes the same for its precision) | **M** | §4.1–4.4, §4.9 | Hit rate at fixed false-alarm budget; reliability on held-out storms; compare with current ranker AUC 0.93–0.94. |
| C4 | **Heterogeneous stream–road GNN** (nodes: road segments, crossings, channel reaches; edges: downhill flow, road adjacency, crossing links), physics features from the engine, mass-plausibility check like Bentivoglio's ARME | Novel combination: surrogate for both hazard and consequence; crossings are the natural coupling nodes | **L** | engine corpus, §1.5 | LOSO; per-node CSI; ARME vs error correlation. |
| C5 | **GP-emulator Bayesian calibration** (history matching) of 5–6 knobs (channel n, land n, width scale, rain scale, KDEEP, Scap scale) on 10 m boxes, with gauges + HWMs as joint likelihood | Replaces one-at-a-time sensitivity runs; gives parameter posteriors to feed the ensemble | **M** | §1.1–1.3 | Held-out reaches and storms; posterior-predictive coverage of marks. |
| C6 | **Differentiable solver** (port `solver.py` to JAX/PyTorch; it is ~180 lines of array code) → gradient-based calibration of spatial n/width fields | High novelty (few differentiable 2-D flood engines are validated on real HWMs); makes C5 scale to fields | **L** | as C5 | As C5, plus check against finite differences. |

---

## D. Cascading / failure side

| # | Idea | Why | Effort | Data | Test |
|---|---|---|---|---|---|
| D1 | **Crossing L2 from the ensemble → P(overtop), P(HW/D > 1.2)**, after B2/B4 | Turns crossings into calibrated probabilities with uncertainty | **M** | §1.5, §5.1 | MassDOT repeating flood points; NBI item 71 code vs modelled freeboard tail; reliability where ≥ 50 positives. |
| D2 | **Fragility (L2 → L3) fitted on Vermont July 2023 damage** (same storm, same glacial geology), applied to MA crossings | The only nearby source of actual failures; honest "assumed→fitted" upgrade of L3 | **M–L** | §4.10, §1.7, NBI/NAACC | Spatial CV across VT counties; transfer check on Franklin County damage reports/PA projects (§4.2). |
| D3 | **Stream-power / bed-shear washout index** at crossings and road–stream adjacencies (ω = ρgQS/W from the engine) | Most July 2023 road losses in hill towns were erosion, not inundation | **M** | engine Q, §1.5 | Rank-AUC vs VT damage sites and Franklin County washout reports. |
| D4 | **Event-scale flood → groundwater link**: recharge from ponded depth × duration into the planned 150–300 m Boussinesq layer; check water-table response at USGS real-time wells after Dec 2023 / Jan 2024 | First validated link in the cascade chain | **L** | §5.3, §2.5 | Well peak rise and timing; no tuning on the test wells. |
| D5 | **Collaborate or benchmark with UMass Boakye/Asgari (Deerfield culvert-condition AI, 2026)**: their condition model × our L2 hazard = risk | Avoids duplicate work in the same watershed; Mo's decision | **S** (Mo) | — | — |
| D6 | **CReDo-style Bayesian network for L3** including dependencies (power at pump stations, access for repair crews via our accessibility layer) | Structured, auditable assumed probabilities | **M** | facilities.json, roads | Sensitivity only (no failure data) — keep as L3 "assumed". |

---

## E. Uncertainty and early warning

| # | Idea | Why | Effort | Data | Test |
|---|---|---|---|---|---|
| E1 | **Swap HRRR members for REFS** (operational 3 Nov 2026; HREF retired) in forecast mode | Keeps the forecast ensemble alive; larger ensemble | **M** | §2.8 | Replay 2023 storms with archived HRRR/REFS-parallel; spread–skill. |
| E2 | **Conformal calibration** of surrogate depth and P(wet) with LOSO folds; extreme-value conformal for tails ([arXiv 2505.08578](https://arxiv.org/abs/2505.08578)) | Distribution-free coverage guarantees for published probabilities | **S–M** | corpus | Empirical coverage on held-out storms. |
| E3 | **Baselines from the field**: NWS experimental FIM (now covers MA) and NWS Flash Flood Warnings scored on our road reports; also Google's 20 km / 24 h recall-precision framing (NWS FFW: 22 % recall, 44 % precision on their grid) | Puts our warnings against what forecasters already have | **S** | NWS archives | Same protocol metrics; add to the baseline list in `protocol.md`. |

---

## F. Publications (novelty)

1. **"A New England flash-flood hydraulic benchmark"** (ESSD-style, cf. Godet et al. 2025 for France): raw and corrected 10 m DEMs, crossing-breached DEM, MRMS/AORC rain, gauges with NAVD88 stage, STN + Vermont HWMs, crossings with inverts, road reports, NFIP block-group counts. Low risk, citable, useful to others. **M.**
2. **"Culverts as digital dams"**: quantified effect of crossing-aware terrain (B2/B4) on statewide 2-D skill for HWMs, gauges and roads — directly motivated by the USGS lidar spec and the EGU26 Loughborough work. **M.**
3. **Paper 1 as planned** (open GPU statewide engine + surrogate) gains a stronger story if A1–A4 explain the bias: "diagnosing steep-reach bias in local-inertial models with gauges and crossing inventories".
4. **Weak-label road-flood warning** (C3) vs NWS FFW and Google's flash-flood product (E3).

## Lead notes, 19 Oct 2026 (from inspecting the South River 10 m run)
- **Speed: one pit sets the time step for the whole grid.** `stable_dt` uses the single deepest cell. In jul2023_southriver_v3_10m a 165-cell hole at 42.5625,-72.6995 (bed 67.3 m, rim 82.2 m: a 15 m pit next to the Deerfield gorge) holds 22.5 m of water, so dt = 0.5 s instead of about 1.6 s at 2 m depth. That makes the run about 3× slower. Options: check whether the pit is real (quarry or pond) or a lidar/burn artefact and fill artefacts below the rim before the run; or use per-cell local time stepping. Effort S–M. Test by rerunning the same storm and checking runtime and validation (unchanged scores, under 1/2 runtime).
- **Gauge discharge check (A1) done by hand:** USGS 01169900 observed 175 m³/s, model about 220–300 m³/s through the narrowest transect. Discharge is about 1.3–1.7× too high, a secondary issue to the hydraulic sill. Worth adding a cross-section discharge output at gauges to the engine (sum of q across a transect each frame) so this becomes automatic.
