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

## 4. Results

### 4.1 Road-edge stream power separates damaged segments, but length and crossings carry much of it
The index was computed for 712 of the 716 Leominster segments in the storm box (540,000 edge points), 21 of them damaged. As
pre-registered it reads **promising** (Table 1): the AUC of the segment maximum is 0.85 [0.78, 0.92]; adding it to modelled depth and
traffic improves the model (likelihood-ratio p = 0.0001; AUC 0.90 → 0.92); and 5 of the 8 washout segments the closure rule missed are in
the top 10 % of segments by the index. The result holds for washouts alone (AUC 0.86), without the most clustered street (0.84) and for
the other summaries (0.80–0.86).
<!-- src: paper2/RQ1_RESULT.md (pre-registered table); rq1_eval.json -->

The post-hoc checks temper this. Segment length alone separates damaged segments almost as well (AUC 0.87), because a long segment has
more chances to contain one of 54 points, and the maximum of more edge points is higher (rank correlation with length 0.65). Eighteen of
the 21 damaged segments lie within 60 m of a road–stream crossing, and proximity to a crossing alone gives AUC 0.83. With depth, traffic,
log length and distance to the nearest crossing all in the model, the index still adds information (p = 0.016; AUC 0.937 → 0.941), and
among segments near crossings it separates damaged ones with AUC 0.74. The empirical damage rate rises from 0.3 % in the lower half of
segments to 22 % in the 90–95th percentile band, then falls to 11 % in the top 5 %, where the largest values are edge points sitting on
streams at crossings (Fig. 1). Version 2 of the index, built to remove both effects, is much less tied to length (rank correlation 0.36)
and has been computed for Leominster, Fitchburg, Worcester and Northbridge without being compared with any damage.
<!-- src: paper2/RQ1_RESULT.md (post-hoc and fragility sections); fragility_spi.json; RQ1_V2_CHECK.md -->

### 4.2 A shallow water table goes with damage, but just as much with flooding
Twenty-one damaged segments among 1,517 Leominster segments with a water-table value; 646 segments have a seasonal water table within 50 cm.
Holding height above drainage and slope constant, damage is more likely on a shallow water table: Mantel–Haenszel odds ratio 2.70 [1.02,
7.12], which meets the pre-registered rule (Table 2). It weakens without Wachusett Street (2.00 [0.72, 5.54]) and for washouts alone
(2.49 [0.85, 7.29]), and strengthens when road class is also held constant (3.19 [1.14, 8.90]). The negative control decides the reading:
the model's surface-water closures show the same association (2.68 [1.46, 4.91]). With this data a groundwater effect on the road
structure cannot be told apart from wet, low ground flooding.
<!-- src: groundwater/PREREG_A_RESULT.md; prereg_a.json -->

The wells explain why. Around the district the water table rises a median 0.09 m within a week of a large storm, up to 0.93 m at shallow
wells, and peaks 4–7 days after the rain, long after roads reopen. Across the 25 catalogue storms the ground was usually already wet
(median wetness percentile 80), but pre-storm wetness does not track how well the flood model reproduced the storm (rank correlations
−0.35 to +0.05). In a normal year 36 % of the district's road length lies where the water table comes within 50 cm of the surface.
Groundwater therefore acts on the road over days, through the base and subgrade, not through same-storm runoff.
<!-- src: groundwater/SCOUT.md §2–3, §5; ANTECEDENT_DESCRIPTIVE.md -->

### 4.3 Blocked culverts close nearby roads but do not explain the damage
Fully blocking every culvert raises the median pool upstream of a crossing by 2.3 m and closes 80 more segments near crossings; half
blockage closes 8 more and 20 % blockage none. No blockage scenario reaches any of the 33 damage points the closure model missed. The
crossings whose blockage would close roads come down to seven locations; three combine a large model effect with a Poor rating in the
stream-crossing surveys (Beaman Road, Commercial Street and Route 2 at Dewey Street) and head the inspection list (Table 3).
<!-- src: phase1/PARAMETRIC_T2.md §1–3; paper2/RQ3_INSPECTION_LIST.md -->

**Table 1. Road-edge stream-power index (version 1) against damage, Leominster, September 2023 (in-sample).**

| Outcome / variant | Segments (damaged) | AUC [95 %] | Added to depth + traffic: LR p (AUC before → after) |
|---|---|---|---|
| Any damage, segment maximum | 712 (21) | 0.85 [0.78, 0.92] | 0.0001 (0.90 → 0.92) |
| Washouts only | 712 (17) | 0.86 [0.77, 0.93] | 0.0001 (0.89 → 0.93) |
| Without Wachusett Street | (17) | 0.84 [0.75, 0.92] | 0.0007 |
| 90th percentile instead of maximum | 712 (21) | 0.80 [0.72, 0.87] | 0.0008 |
| Post-hoc: also length and crossing distance | 712 (21) | — | 0.016 (0.937 → 0.941) |
| Post-hoc: segment length alone | 712 (21) | 0.87 | — |
| Post-hoc: crossing proximity alone | 712 (21) | 0.83 | — |
<!-- src: paper2/RQ1_RESULT.md; rq1_eval.json -->

**Table 2. Seasonal water table within 50 cm vs damage, height above drainage × slope held constant (Mantel–Haenszel).**

| Analysis | Odds ratio | 95 % interval |
|---|---|---|
| Main: any damage | 2.70 | 1.02 – 7.12 |
| Without Wachusett Street | 2.00 | 0.72 – 5.54 |
| Cut-off 25 cm | 2.62 | 1.02 – 6.73 |
| Road class also held constant | 3.19 | 1.14 – 8.90 |
| Washouts only | 2.49 | 0.85 – 7.29 |
| Negative control: model closures | 2.68 | 1.46 – 4.91 |
<!-- src: groundwater/PREREG_A_RESULT.md -->

**Table 3. Culvert locations whose blockage closes roads in the September 2023 run (Leominster).** Pool rise = rise upstream of the
crossing with the culvert fully blocked; condition from NAACC surveys.

| Location (stream) | Roads that close only when blocked | Pool rise | Survey rating |
|---|---|---|---|
| Route 2 / Dewey St / Columbia Ave | Route 2 and ramp, Dewey St, Columbia Ave, Minneapolis Ave | +0.4 to +2.0 m | OK; one inlet Poor |
| Commercial St / Putnam St / railroad (North Nashua River) | Boulder Dr, Putnam St | +2.1 to +4.0 m | Commercial St: **Poor** |
| Meadow Pond Dr | Meadowbrook Acres | +2.6 m | not surveyed |
| Bathrick Rd | Bathrick Rd | +2.1 m | OK / Poor |
| Justice Hill Rd (Rocky Brook) | Justice Hill Rd | +0.3 to +1.1 m | OK |
| Beaman Rd (Wilder Brook) | Tanglewood Rd | +0.7 m | **Poor; inlet Critical** |
| Pierce Ave / Olin Ave | Harvard Ave, Route 2 | +0.5 to +0.6 m | OK; one inlet Poor |
<!-- src: phase1/PARAMETRIC_T2.md §3; paper2/RQ3_INSPECTION_LIST.md -->

## 5. Discussion

**Two failure modes, two indicators.** Flood depth predicts where water closes a road; it does not predict where the road is damaged. In
Leominster most damage was edge washout on segments with almost no modelled water, and a measure of how much water runs along the road
edge, and how steeply, finds those segments where depth does not. A screen for road agencies therefore needs both lists: one of roads
likely to close, for warnings and detours, and one of road edges likely to wash out, for inspection after the storm.
<!-- src: §4.1; paper/MANUSCRIPT.md -->

**What the index measures.** Much of the raw signal of version 1 is length and stream crossings: long segments and segments next to
crossings are where damage was recorded. That is not only an artefact. Crossings are where road and stream meet and where flow
concentrates, and the culvert results show that blockage there floods nearby roads. But a useful index must say something beyond "long
road near a stream", and the evidence that it does is modest (p = 0.016 once both are controlled). Version 2 separates the two mechanisms
by design, scoring curb-line flow away from crossings and leaving crossings to the culvert readout.
<!-- src: RQ1_RESULT.md post-hoc; PREREG_RQ1_V2_DRAFT.md; §4.3 -->

**Groundwater as the slow link.** The association of damage with a shallow water table is real in the data but indistinguishable from the
association of flooding with low, wet ground. The wells show why a same-storm signal is unlikely: the water table peaks days after the
rain. The mechanism that would matter for the road is the saturated base and subgrade that pavement studies describe (Mallick et al.;
Tao and Mallick, 2020); testing it needs pavement condition and deflection data, not more flood runs.
<!-- src: §4.2; LITERATURE.md -->

**For practice.** A town or district could compute the index for every road from public lidar in minutes per town, and use it with the
closure list and the culvert list after a storm: inspect first the road edges with high index values, the culverts at the seven listed
locations, and the closed roads.
<!-- src: RQ1_RESULT.md (16 min, 712 segments); RQ1_V2_CHECK.md -->

## 6. Limitations
- **One storm, one town, in-sample.** Every Leominster result uses the closure model's calibration storm and 21 damaged segments. The
  index has not yet been tested out of sample; version 2 is ready for four towns and waits for a second damage inventory.
- **Damage labels.** A municipal list of 54 points, assigned to segments within 30 m; points cluster on a few streets.
- **Terrain.** Lidar shows no storm drains or inlets, so the index describes flow along the edge if inlets are full or absent; D8 on a
  filled surface; the acquisition date is the service's best available.
- **Groundwater.** The seasonal water table comes from a soil survey of natural soils, not road fill; wells are 10–30 km apart; no
  pavement or subgrade observations.
- **Culverts.** Blockage scenarios are uniform what-ifs, not observed blockage; survey ratings are partial and may be dated.

## Abstract (draft, ≤ 200 words)
Road-flood models predict where water closes roads, but road agencies repair damage, and damage does not need deep water. After the
11 September 2023 flash flood in Leominster, Massachusetts, 50 of 54 recorded damage points were washouts, many on roads a closure model
left almost dry. We test, with pre-registered analyses, three links that follow flooding: flow along road edges, groundwater under the
road, and blocked culverts. A road-edge stream-power index from 1 m lidar separates the 21 damaged segments from 691 undamaged ones
(AUC 0.85 [0.78, 0.92]) and adds to modelled depth and traffic, but segment length and stream crossings explain much of it, and it still
adds only modestly once they are controlled. Damage is more common where the seasonal water table is shallow (odds ratio 2.7 with terrain
held constant), but surface flooding shows the same association, and wells show the water table peaking days after the storm. Blocked
culverts flood nearby roads but explain none of the missed damage; seven locations form an inspection list. All results are in-sample;
a revised index is ready for an out-of-sample test when a second damage inventory becomes available.
