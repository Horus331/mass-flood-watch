# Paper 2 manuscript draft: where a flash flood damages the road (working title)

Status: §1 drafted 21 Nov 2026. Every number carries a `<!-- src -->` pointer; citations are checked in `LITERATURE.md`.

## 1. Introduction

Road-flood models are judged on whether they put water on the right road. That is the question a closure warning needs, and it is the
one our first study answered for central Massachusetts: a physics-based screen that ranks road segments by modelled depth and catches
about one in five documented flood sites in the top 3 % of segments on storms it never saw. But the cost that a road agency carries after
the water recedes is damage to the road itself, and damage does not need deep water. When the City of Leominster surveyed its roads after
the storm of 11 September 2023, 50 of the 54 damage points it recorded were washouts, and 33 of the 54 lay on segments the closure rule did
not flag, most of them edges eroded where the model put about 2 cm of water.
<!-- src: paper/MANUSCRIPT.md §4.2–4.3 (0.204 / 0.210 at 3 %); groundwater/SCOUT.md §6 (damage types: 50 washout, 2 culvert, 2 other); phase1/LEOMINSTER_MISSES.md (33 misses, 26 edge washouts, median 2.4 cm) -->

Closure and damage are different links of the same cascade. Rain becomes surface flow; flow that runs along a road concentrates at curbs
and shoulders and erodes them; water that stays in the ground raises the water table under the pavement and weakens its base for days.
The distinction between a hazard that triggers the next one and hazards that merely coincide is central to the cascading-hazard
literature (Gill and Malamud, 2014; Pescaroli and Alexander, 2015; Yanites et al., 2025), but road-flood studies rarely follow the chain
past inundation.
<!-- src: PROJECT_LOG §4 (14 Nov, cascading framing); RESEARCH_LOG 3.3 (Gill & Malamud 2014, Rev. Geophys. 52:680–722; Pescaroli & Alexander 2015, Planet@Risk 3(1); Yanites et al. 2025, Science 388, eadp9559) -->

Two strands of work point to the missing link. For bridges, stream power separates structures damaged by Tropical Storm Irene in
Vermont from undamaged ones (313 damaged against 951 undamaged; Anderson et al., 2017), and has been turned into damage-probability
curves; but the analysis works at the scale of stream reaches, with design flows rather than the storm's own, and reports no predictive
test. For pavements, the time a flooded base takes to saturate and the surface to fail has been modelled (Mallick et al., 2015 [year to confirm: 2014 or 2015]), and
practice for assessing flood damage to roads has been reviewed, showing that water in the unbound layers does the most structural damage
(Tao and Mallick, 2020). Neither has been applied to the road edges of an ordinary town network, or tested against a recorded damage list.
<!-- src: paper2/LITERATURE.md (Anderson et al. 2017 VTrans report, ch. 3–4; Tao & Mallick 2020 LTRC 615; Mallick, Tao et al. 2014/15) -->

This paper asks three questions, each pre-registered before it was run. (1) Does a road-edge stream-power index computed from 1 m lidar
identify the segments that were damaged, beyond what flood depth and traffic already explain? (2) Is damage more common where the seasonal
water table is shallow once terrain is held constant, or is that association just low ground? (3) Which culverts would turn a storm into a
road failure if blocked, as a list for inspection? We answer them for Leominster, where a complete municipal damage inventory exists, report
those answers as in-sample, and set up the out-of-sample test of the index for the next inventory.
<!-- src: paper2/PREREG_RQ1.md; groundwater/PREREG_A.md; paper2/RQ3_INSPECTION_LIST.md; paper2/PREREG_RQ1_V2_DRAFT.md -->

## 2. Study area and data

**Storm and town.** The storm of 11 September 2023 brought intense convective rain to Leominster and Fitchburg in north-central
Massachusetts. It is the calibration storm of the closure model in our first study, so every Leominster result in this paper is in-sample.
The flood simulation used here is that study's operational run for the Leominster box (20 m LISFLOOD-FP on the conditioned terrain, radar
rain), which also supplies modelled peak depth and road traffic for each segment.
<!-- src: paper/MANUSCRIPT.md §2–3; phase1/parametric_t2/t2_base (features_sep2023.csv: peak_depth_m, aadt, hand_m, slope_pct) -->

**Damage inventory.** The City of Leominster Department of Public Works listed 54 damage points after the storm: 50 washouts, 2 culvert
failures and 2 others. A point is assigned to the nearest road segment within 30 m; the unit of analysis is the segment, so clusters of
points on one street count once.
<!-- src: proto/data/labels_sep2023_leominster_dpw.csv; groundwater/SCOUT.md §6; groundwater/PREREG_A.md (30 m, unit = segment) -->

**Elevation.** Bare-earth elevation at 1 m from the USGS 3D Elevation Program image service (best available lidar), fetched in 4 km tiles
with a 1 km buffer; no cell was missing in any of the areas used.
<!-- src: paper2/RQ1_INDEX_SPEC.md; RQ1_RESULT.md (9 tiles, no missing elevation); RQ1_V2_CHECK.md (0 % missing in 4 towns) -->

**Groundwater.** The seasonal high water table (the shallowest depth to water in a normal year) comes from the SSURGO soil survey on the
model's 30 m grid and is sampled every 10 m along each road. USGS wells with continuous or daily depth-to-water records in and around
the district describe how the water table responds to storms and how wet the ground was before each storm.
<!-- src: groundwater/SCOUT.md §1–2, §5; groundwater/ANTECEDENT_DESCRIPTIVE.md -->

**Crossings.** Road–stream crossings come from the Massachusetts crossings inventory and North Atlantic Aquatic Connectivity
Collaborative (NAACC) surveys, which rate the condition of the structure and of its inlet.
<!-- src: docs/network/crossings_all.json; phase1/PARAMETRIC_T2.md §3 -->

## 3. Methods

### 3.1 Road-edge stream-power index
Along each segment, points are placed every 2 m and offset 3 m and 5 m to both sides of the centreline, where curb lines and shoulders
lie on typical two-lane roads. On the 1 m surface (pits and depressions filled, flats resolved, D8 flow directions) each point takes the
largest upslope area A within a 3 × 3 window and the local slope S, and the stream-power index is SPI = A·S (m²). Version 1 summarises a
segment by its maximum SPI (also the 90th percentile and the edge length above the area's 95th percentile). Version 2, defined after
version 1 showed that segment length and stream crossings carry much of its signal, drops edge points within 30 m of a crossing or on cells
draining more than 0.5 km², and scores fixed 50 m windows; its main measure is the share of a segment's windows above a fixed threshold.
<!-- src: paper2/RQ1_INDEX_SPEC.md; PREREG_RQ1_V2_DRAFT.md; RQ1_V2_CHECK.md; proto/edge_spi.py -->

### 3.2 Index against damage
The comparison was frozen before the index existed: the area under the ROC curve (AUC) of the segment SPI for damaged against undamaged
segments, with a bootstrap 95 % interval; a likelihood-ratio test of adding log SPI to a logistic model with log modelled depth and log
traffic; and the share of the washout segments that the closure rule missed which fall in the top 10 % of segments by SPI. Readings were
fixed as promising (AUC ≥ 0.70 with the interval above 0.5, test p < 0.05, missed washouts ≥ 2 × chance), weak or no signal. Checks that a
reviewer would ask for (segment length, distance to crossings) were added afterwards and are reported as post-hoc.
<!-- src: paper2/PREREG_RQ1.md; proto/rq1_eval.py; RQ1_RESULT.md (post-hoc section) -->

### 3.3 Water table and damage, terrain held constant
Segments are grouped into 15 strata by height above the nearest drainage (0–1, 1–2, 2–5, 5–10, ≥ 10 m) and slope (< 2, 2–5, ≥ 5 %). The
Mantel–Haenszel odds ratio of damage for segments whose seasonal water table comes within 50 cm of the surface, with its Robins–Breslow–
Greenland 95 % interval, is the main statistic. Sensitivities: without the most clustered street, a 25 cm cut-off, logistic regression,
road class as an extra stratum, washouts only. A negative control repeats the analysis with the model's surface-water closures as the
outcome: if the water table only marks low ground, closures should show the same association.
<!-- src: groundwater/PREREG_A.md; proto/gw_prereg_a.py -->

### 3.4 Blocked culverts
The flood model is rerun with every culvert 20, 50 or 100 % blocked, and with only the smallest third fully blocked. Roads near crossings
are read relative to the road crest, so that water standing in an open culvert notch is not counted as road water, and the rise of the pool
upstream of each crossing is recorded. Crossings are ranked by the number of segments that close only when they are blocked.
<!-- src: phase1/PARAMETRIC_T2_PREREG.md; PARAMETRIC_T2.md; whatif/BLOCKED_V3.md -->

### 3.5 Pre-registration
Each analysis was written down and committed to the project repository before it was run, with its reading rules; results are reported
whatever they show, and analyses added after seeing a result are labelled post-hoc.
<!-- src: paper/SUPPLEMENT.md S1 -->
