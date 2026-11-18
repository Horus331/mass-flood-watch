# Paper 1 manuscript draft

Working title: *How well can a physics-only 2-D flood model tell which roads will close? A pre-registered out-of-sample evaluation in
central Massachusetts.* Structure and numbers follow `OUTLINE.md`; every number below comes from the repository file named in the
trailing `<!-- src: -->` comment of its paragraph (comments are removed before submission). References are the `R#` list of
`docs/proto/ROADMAP_research.md`; a missing reference is marked **[ref needed]**.

Status: complete first draft (17 Nov 2026): abstract, sections 1–7, Figs 1–8, Tables 1–8, references. Next: full consistency read.

---

## Abstract
Transportation agencies need to know which road segments will flood, but road-flood models are rarely tested against named
alternatives on storms they were not tuned on. We evaluate a physics-based screen for MassDOT Highway District 3, central
Massachusetts: LISFLOOD-FP local-inertial simulation at 20 m driven by hourly MRMS radar rain, with road depth turned into a chance
of closure and no parameter fitted to closures. All tests were fixed in advance. On 81 storms in three other districts (498
documented sites) the frozen model's top 3 % of segments contain 21 % of the sites, against 9 % for NWS flash-flood warnings, 7 % for
the FEMA 100-year zone, 10 % for terrain alone and 10 % for a static hazard × vulnerability × consequence score (chance 9 %), all
significant; ranking by a chance-of-flooding score raises this to 25 %. On 23 held-out District 3 storms (98 sites) the model reaches
20 %, but a traffic-weighted static score is not worse, which we trace to reports concentrating on busy roads. Traffic, a
stream-crossing flag and storm-drain sinks did not improve held-out skill. Driven by forecast rain, an eight-member time-lagged
ensemble catches 33 % of sites 8–14 h ahead against 26 % for a single forecast. A solver audit shows that GPU and CPU builds agree only
with a ≤ 1 s time step. For the September 2023 storm the closures leave about 76,000 residents without timely access to a hospital,
fire or police station, 99 % of them on roads that stay dry. A complete municipal damage inventory shows the misses are mostly edge
erosion with little modelled ponding. The screen ranks roads usefully for inspection but cannot yet issue segment-level warnings;
labels, not model complexity, limit it.
<!-- src: OUTLINE.md §3b (v2) + forecast/ENSEMBLE_PARITY.md §1 + paper/data/d3_sep2023_t2_cascade.json -->

---

## 1. Introduction
For a state department of transportation, the most frequent impact of a flash flood is a closed road. Crews close, barricade and
reopen roads one segment at a time, and emergency services route around them one segment at a time; yet most flood guidance comes
as areas: a warning polygon, a flood zone, an inundation map. Turning water depth into a road decision has a long literature on its own:
depth thresholds at which vehicles stall or float (Smith et al. 2014, R19; Kramer et al. 2016, R21; Martínez-Gomariz et al. 2018, R20)
and depth–speed functions for disruption (Pregnolato et al. 2017, R23). Data-driven models estimate road-flood likelihood from past
reports (Safaei-Moghadam et al. 2023, R37), and machine-learning surrogates now emulate hydrodynamic models quickly (Bentivoglio et al.
2025, R34; Asif et al. 2026, R33).

What is missing is a test of road-segment skill that an agency could trust: many storms the model was not tuned on, documented
reports rather than modelled truth, and metrics corrected for chance, because flagging more roads always catches more reports. Most
evaluations use one or a few events, judge the flood extent rather than the road, or report skill without saying what random
flagging of the same share would achieve.

This paper evaluates a physics-only 2-D flood model as a road-closure screen in central Massachusetts under a protocol fixed before
any candidate was scored. It asks four questions. (1) How well does the model rank road segments by flood risk on held-out storms,
compared with chance and with what agencies use today? (2) Does that skill transfer, with every setting frozen, to districts it never
saw? (3) How sensitive are the results to the numerical solver? (4) Do learned models or road-network context add to the physics?
It then shows, for one storm, what the closures do to travel and to access to emergency services, and how much of the skill survives
when the rain is a forecast.

---

## 2. Study area and data

### 2.1 Study area
The study covers MassDOT Highway District 3, central Massachusetts: Worcester County and neighbouring towns, a glaciated upland of
till-mantled hills, steep small streams and dense mill-town centres. The District road graph has 52,698 segments (MassDOT Road Inventory,
split at intersections). Flash floods here are short, convective or tropical-remnant storms on small, fast catchments; in the September 2023
Leominster storm most damage was to local roads, culverts and road edges rather than to river floodplains.
<!-- src: cascade/CASCADE.md §1 (52,698 segments); cycles/LEOMINSTER_COUNTS.md; phase1/LEOMINSTER_MISSES.md. -->

### 2.2 Storms
The storm catalogue holds 30 District 3 storms (25 run, 5 locked) with documented road impacts, 2015–2026 (`parity/catalog`). Their roles were fixed
before any candidate was scored (Section 3.4): one calibration storm (Leominster, 11–12 Sep 2023), development storms, a held-out
decision set of 23 storms with 90 documented flood sites at the time of freezing (98 after label round 2), and five locked storms
(aug2015, aug2018, aug2020, jul2018, oct2016) that are neither run nor read. A further 81 storms in MassDOT Districts 4–6 (498 sites)
were added for the transfer test and never entered any fit or selection.
<!-- src: PROTOCOL.md v2 §2; obs/LABELS_ROUND2.md §4; transfer/TRANSFER.md §2. parity/catalog (25 storm folders) -->

### 2.3 Rain
Hourly MRMS MultiSensor QPE Pass 2 (Zhang et al. 2016, R1) on its 1 km grid drives every replay; storms before October 2020, when
Pass 2 is not archived, use the Iowa Environmental Mesonet gauge-corrected MRMS product. The hourly totals are applied uniformly within
each hour on the 20 m model grid. Forecast mode (Section 3.7) uses NOAA HRRR 3 km hourly precipitation.

### 2.4 Terrain, land and soils
Ground elevation is the USGS 3DEP 10 m DEM averaged to 20 m, with road crests kept from the 10 m maximum. Stream channels come from
NHDPlus HR flowlines, burned to their bankfull depth. Land cover and imperviousness come from NLCD 2021 (Manning's n per class), and
hydrologic soil groups from SSURGO; together they set the NRCS curve number of each cell. Road–stream crossings combine the National
Bridge Inventory, the MassDOT structure inventory and the UMass stream-crossing survey (NAACC protocol), the last giving culvert
dimensions and condition for most surveyed crossings.
<!-- src: STATUS.md §1; model-tree CHECK.md; advisors/datasets.md -->

### 2.5 Labels
Documented flood sites come from NWS Local Storm Reports and the Storm Events Database, news reports, amateur radio (WX1BOX), MassDOT
water-surface crash records, SeeClickFix service requests and, for the calibration storm, the City of Leominster Department of Public
Works' complete damage inventory (54 surveyed points). Each label carries a source tier and a coordinate-quality class. A label matches a
road segment when it lies within 30 m of one of the segment's road points (points every 10 m); town-level labels are not matched.
Matched labels within 150 m of each other are joined into one site, and a site counts as hit when any of its segments is flagged.
Reports are not inventories: outside Leominster, an unflagged dry road may simply not have been reported, so false alarms are undefined
and the evaluation uses recall at a fixed share of flagged segments.
<!-- src: PROTOCOL.md §1; obs/LABELS_ROUND2.md; phase1/LEOMINSTER_MISSES.md -->

---

## 3. Methods

### 3.1 Flood simulation
Water depth comes from LISFLOOD-FP 8.2 with its acceleration (local-inertial) solver (Bates et al. 2010, R14; de Almeida et al. 2012,
R15; Shaw et al. 2021, R16), run rain-on-grid at 20 m with free outflow on all edges. Rain excess is computed hourly before the solver
from the NRCS curve-number method (Hawkins et al. 2002, R8) at antecedent condition II, with all curve numbers scaled by 0.88, and a
constant 2 mm/h soak-in of standing water. Channels start at base flow. There are no storm drains, dams or inflows from outside the box.

**Solver parity.** The GPU build of LISFLOOD-FP ignores the infiltration keyword and caps each step at the initial time step, while the
CPU build adapts the step. On rain-on-grid runs this made the two builds produce different floods and spurious gauge rises at start-up.
All runs here use a parity mode (`LF_PARITY=1`): infiltration is removed from the rain before the solver, and the time step is capped
at 1 s on both builds, which then agree cell for cell (Section 4.1).
<!-- src: parity/PARITY.md; parity/BASELINE.md -->

**Calibration.** The curve-number scale is the only calibrated parameter. It was chosen on the calibration storm by a rule fixed in
advance: the value in {0.85, 0.88, …, 1.00} minimising the mean absolute gauge-rise error at the two USGS gauges in the box, with ties
broken by peak timing and then by closeness to the previous value 0.91. 0.85 and 0.88 tied on error (0.22 m) and timing (0.4 h); 0.88
was chosen. No closure label entered the choice; recall of the calibration storm's reports was flat (35 of 89) between 0.85 and 0.94.
<!-- src: parity/BASELINE.md §1 -->

**Terrain correction.** At road–stream crossings the 10 m DEM shows the road embankment as a dam. The model cuts a notch through the
embankment along the mapped flowline at each crossing, joins it to the downstream channel, and enforces a continuous downhill channel
along every flowline (`LF_NOTCH_FIX`, `LF_CHAN_ENFORCE`; "T2"). Without it, chained notches could leave pits several metres deep, such as
an 8.5 m pit on Route 2 at the I-190 interchange.
<!-- src: terrain/TERRAIN.md -->

### 3.2 From water depth to a closure probability
Each segment is sampled every 10 m along its centreline. Its depth *d* is the second-highest point depth, so that a segment closes only
when the water covers more than a single low point. Only water added by the storm counts (depth minus the depth at rain onset). The
closure probability is

  P(close) = Φ((d − 0.30 m) / 0.10 m),

where 0.30 m is about the depth at which a passenger car stalls or floats (Kramer et al. 2016, R21; Martínez-Gomariz et al. 2018,
R20) and 0.10 m represents the combined error of lidar road height and modelled depth. A segment is "closed" when P ≥ 0.5, i.e. d ≥
0.30 m. Three further terms can raise P: water beside the road within the design freeboard of its crest (0.30 m, after FHWA HDS-5
practice; Schall et al. 2012, R40); culvert overtopping, from the HDS-5 headwater of the modelled peak flow at surveyed
culverts, with NAACC condition setting a blockage factor; and fast shallow water. Bridge decks are read from their approaches, so a
river under a bridge does not close the deck. The terms are combined as independent failure modes, P = 1 − Π(1 − Pᵢ). No parameter of
this rule was fitted to closure labels.
<!-- src: STATUS.md §1; proto/prototype.py (constants and docstrings); recall/RECALL.md §4 -->

At crossings, the depth of an open culvert notch is read as depth on the road. This is deliberate: it is the model's proxy for culvert
failure, and reading depth relative to the road crest instead lowers the calibration storm's recall from 0.385 to 0.08. For questions
about culvert blockage, where the notch itself is filled, depth is read relative to the crest (Section 4.7).
<!-- src: proto/prototype.py; whatif/PREREG_BLOCKED_V3.md; phase1/PARAMETRIC_T2.md -->

### 3.3 Baselines
The model is compared with named alternatives that an agency could use instead, each ranked over the same segments: NWS flash-flood
warning polygons in force during the storm; the FEMA 1 % annual-chance flood zone; terrain alone (height above the nearest drainage);
a static hazard × vulnerability × consequence score; and the same score weighted by traffic. Chance is computed exactly for each storm
as the expected recall of flagging the same share of segments at random.
<!-- src: scoring/BENCHMARK_v3.md -->

### 3.4 Evaluation protocol
The protocol was fixed and committed before any candidate was scored (PROTOCOL v1, 23 Oct 2026; v2, the same day, after the label round
enlarged the held-out pool). The unit is the site (Section 2.5). The primary metric is held-out site recall with the model's top 3 % of
segments flagged, ranked by P and then by depth; secondary metrics are recall at 1, 2, 5 and 10 % and at the rule, segment recall, the
fractions skill score on the road network at 100, 300 and 1000 m (Roberts and Lean 2008, R39) against its chance value, PR-AUC, and, in
the one complete inventory (Leominster), the critical success index. Uncertainty comes from a two-stage cluster bootstrap (2000
replicates; storms, then sites within storms), with paired resamples for comparisons.

Anything fitted to labels is fitted by leave-one-storm-out over the 25 non-locked storms, and held-out scores come only from fold
predictions (Roberts et al. 2017, R32). A model change is adopted only if, on the held-out 23 storms, all of: the top-3 % site recall
gains at least 0.04; the one-sided lower bound of the gain at α/k (α = 0.05, k = variants tested) is above zero; the 300 m FSS does not
drop; no storm with three or more sites loses more than one site; and the lift of the alert tier stays at least 0.8 of the baseline's.
Every candidate, adopted or not, is reported.
<!-- src: PROTOCOL.md v1 §1, §4; v2 §2, §5a -->

### 3.5 Transfer test
The frozen model was run on 81 storms in MassDOT Districts 4–6 with no change of any setting, under a separate pre-registration (25 Oct
2026). A road-source control repeats the scoring on the OpenStreetMap road network alone, to check how much of the skill depends on
the MassDOT segment graph.
<!-- src: PROTOCOL.md "Transfer test"; transfer/TRANSFER.md -->

### 3.6 Learned and network candidates
Four learned closure models were tested against the physics rule: a logistic model on model and site features, a pairwise ranking
model, a two-tier model, and a model adding cascade (network) features. Because unreported roads are not known to be dry, they are
treated as unlabelled rather than negative (Bekker and Davis 2020, R28). All were fitted inside the leave-one-storm-out folds.
<!-- src: ml/EXPANDED.md; cascade/CASCADE.md §4 -->

### 3.7 Consequences
Closed segments are removed from the District graph, and wet but open segments are slowed with the depth–speed function of Pregnolato
et al. (2017, R23). Shortest-path detours give the added vehicle-hours, volume-to-capacity ratios show overloaded corridors, and Census
2020 block populations are assigned to the nearest hospital (30 min), fire station (8 min) and police station (10 min) to count
residents who lose emergency coverage in time.
<!-- src: cascade/CASCADE.md §1; model-tree CHECK.md (response times) -->

### 3.7b A chance-of-flooding score
Besides the depth rule, segments can be ranked by π, the probability that a segment truly floods, from a latent-label model fitted on
the 25 non-locked District 3 storms (139,938 segment-storms, 423 reported). It treats reports as an incomplete detection of true
flooding and combines modelled depth with hazard terms such as peak 1-hour rain and segment length. The fit was frozen on 28 Oct 2026;
it is tested only on Districts 4–6, which it never saw.
<!-- src: latent/LATENT.md §1; scoring/PREREG_PI_RANK.md -->

### 3.8 Forecast mode
For forecasts, a gate runs the flood model when any District 3 town has an HRRR forecast of at least 25 mm in 6 h or 40 mm in 24 h.
Each cycle runs eight members: the four newest 48-hour HRRR runs (every 6 h) and the four newest hourly runs, each with its rain spread over a 20 km
neighbourhood at the 90th percentile (Schwartz and Sobash 2017, R6), a 12 h MRMS spin-up, and radar nowcast rain in the first hours. A
segment is listed as likely to close when it closes in at least 2 of the 8 members.
<!-- src: forecast/GATE.md; forecast/ENSEMBLE.md; STATUS.md §1 -->

---

## 4. Results

### 4.1 Solver parity and gauges
Without the parity mode, the GPU and CPU builds disagreed sharply on the same storm: on the July 2023 Worcester storm the GPU flagged
0.63 % of segments and the CPU 0.10 %, with little overlap (Jaccard 0.16). Of the 43 segments flagged on the GPU, 28 had a peak depth
more than 0.10 m above every saved snapshot, a sign of single-step spikes; the CPU had none of 7. With the parity mode the two builds
flag identical segments (Jaccard 1.0) with a mean depth difference of 0.000 m on two storms. Across nine catalogue storms, the mean
per-storm gauge-rise error fell from 0.82 to 0.46 m, gauges with no modelled rise from 9 of 16 to 3 of 16, and the mean flagged share
from 2.13 % to 1.07 %. The model under-predicts on light storms: the bias is negative on 8 of 9 storms (Elsa −1.32 m, Ida −1.00 m),
and the rule hits none of the 20 sites of the light storms.
<!-- src: parity/PARITY.md; parity/BASELINE.md §2–3 -->

### 4.2 Held-out skill in District 3
On the 23 held-out storms (98 sites), the depth rule flags 0.43 % of segments and catches 0.092 of sites [90 % CI 0.022, 0.167], a lift
of 6.4 over chance. Ranking the top 3 % of segments catches 0.204 [0.104, 0.303] against 0.066 by chance (lift 3.1), and the top 10 %
catches 0.44. Spatial skill is low: the 300 m fractions skill score at 3 % flagged is 0.023 [0.015, 0.034].
Among named alternatives (Table 4), the model beats NWS flash-flood warnings (0.05), a radar-rain threshold (0.05) and terrain alone
(0.08) significantly. A static hazard × vulnerability × consequence score that weights busy roads reaches 0.32, ahead of the model but
not significantly; Section 5 traces this to reports concentrating on busy roads.
<!-- src: transfer/TRANSFER.md §2 (District 3 column, round-2 labels); scoring/BENCHMARK_v3.md -->

### 4.3 Transfer to Districts 4–6
On 81 storms in three other districts (498 sites), with every setting frozen, the top 3 % of segments catch 0.210 of sites [0.167,
0.254] against 0.086 by chance (lift 2.46 [1.96, 2.97]), the same recall as in District 3. The pre-registered verdict is that the model
transfers. Here the model beats all named alternatives significantly: NWS warnings 0.09, the FEMA 1 % zone 0.07, terrain alone 0.10,
the static score 0.10 and the rain threshold 0.06. Ranking by π instead of depth raises the top-3 % recall from 0.206 to 0.251 (95 %
interval of the gain +0.002 to +0.086), and π was adopted to order the forecast's road list. The rule alone flags only 0.14 % of segments
and catches 0.036 of sites, at a lift (6.7) similar to District 3's. The road network matters: scoring the same floods on OpenStreetMap
roads alone loses 2 of 14 sites at 3 % and halves the lift. 26 of the 81 storms have no site in the top 3 %, and the 300 m fractions skill score (0.017) is below that of random flagging
(0.023): the model ranks roads but does not place floods to within 300 m.
<!-- src: transfer/TRANSFER.md §2; scoring/BENCHMARK_v3.md; scoring/PI_RANK_v3.md -->

### 4.4 What did not help
No learned or network-aware candidate passed the protocol (Table 6). The best, the rule plus a learned watch tier, caught 26 of 90
sites at 3 % (0.289, lift 4.5) but missed the significance condition (one-sided P ≈ 0.014 against α/k = 0.01). Cascade features lifted
one variant from 20 to 33 hits but with a lower bound of 0.000; against the same model without them, they added 2 sites (lower bound
−0.076). Within storms, learned models ranked better (mean ROC-AUC 0.76 against 0.67 for the rule) without turning that into more
sites at a fixed budget. Adding traffic to the model ranking, a crossing flag, a catch-basin sink and a storm-drain sink on built-up
roads were each rejected: none raised held-out recall, and the drain sinks removed documented sites faster than they removed flags.
<!-- src: ml/EXPANDED.md; cascade/CASCADE.md §4.2; scoring/HYBRID_v3.md; scoring/CROSSING_v3.md; drains/INLETS.md; drains/C2_ROADS.md -->

### 4.5 Consequences of the September 2023 storm
Run over the whole District (78 × 90 km at 20 m, 17.6 million cells, 48 h) on the terrain and readout used in operation, the
September 2023 storm closes 127 road segments at some time; 70 are closed at once at the peak, 8 hours after the start of the run
(Fig. 7). Detours and slowed traffic cost about 7,400 vehicle-hours per hour at the peak and 120,000 vehicle-hours over the 48 hours.
At the peak, 76,450 residents can no longer reach a hospital, fire station or police station within the response time (hospital 30
min, fire 8 min, police 10 min): 45,700 lose the fire station, 38,600 the police and 26,500 the hospital, and 7,900 can reach none
of them. Almost all of them, 75,700 or 99 %, live on roads that stay dry: they are cut off by closures elsewhere on the network, and
98 % of the person-hours of lost access fall on people whose own road never floods. The access loss peaks 1.5 hours after the
closures themselves. Fourteen segments are still closed at the end of the run; the model has no storm
drains, so water that ponds in closed low ground drains only by soak-in, and these long closures are an upper bound.
<!-- src: turing/d3_sep2023_t2 (T2 terrain, PROTO_RES_CONSISTENT=1, start at rain onset; Turing 17 Nov 2026); paper/data/d3_sep2023_t2_cascade.json totals and series -->

### 4.6 Forecast lead time
At the deployed physics, on the seven out-of-sample storms (43 sites), listing a segment when it closes in at least 2 of the 8 forecast
members catches 0.33 of sites at long lead (8–14 h) and 0.30 at short lead (2–8 h), against 0.26 and 0.14 for the newest forecast alone,
while flagging 2.8 % and 1.9 % of segments. The check fixed in advance (recall at least the single cycle's, flags at most twice its share
plus one point) passes at both leads, and also on a like-for-like rescoring of the 28 sites matched in both evaluations (Fig. 8).
Two live storms in November 2026 test the forecast forward in time. On 12–13 November it correctly listed no closures. On 5–7
November it listed 80 roads as likely closures and none was reported; the main error was the HRRR rain: on the observed radar rain
the model closes 8 segments, none of them reported, and the forecast had been changed to a new version during the storm.
<!-- src: forecast/ENSEMBLE_PARITY.md §1–3; prospective/storm_2026-11-13_results.md; model_colab 2026-11-15_Nov5-6_Storm_Slide.md -->

### 4.7 Sensitivity on the calibration storm
On the calibration storm, wet antecedent soil (condition III) adds about 50 closed segments but only 4 reports, and 41 of the new
closures have no report nearby; frozen ground more than doubles the closures and adds one damage point; dry soil halves the closures.
No condition reaches the 25 missed damage points along Wachusett Street, which failed by edge erosion with almost no modelled ponding.
Blocking culverts raises the pool behind them by a median 0.6, 1.6 and 2.3 m at 20, 50 and 100 % blockage, overtopping up to 24
crossings; a list of nine crossings whose blockage closes roads is stable under the terrain correction.
<!-- src: phase1/PARAMETRIC.md; phase1/PARAMETRIC_T2.md; phase1/LEOMINSTER_MISSES.md -->

---

## 5. Discussion

### 5.1 Ranking works, the threshold does not
The model ranks roads better than every named alternative an agency has today, in District 3 and, with all settings frozen, in three
districts it never saw. Its fixed closure rule is far less useful: it flags well under 1 % of segments and catches 4–9 % of sites. The
two results have one cause. The model under-predicts on all but the largest storms: the gauge-rise bias is negative on 8 of 9
storms, and on the five light storms the rule hits none of the 20 documented sites, which peak in the model at 0.28–0.29 m, just under
the 0.30 m threshold. Their order is right but their depths are low. A ranked list is robust to that; a threshold is not.
<!-- src: parity/BASELINE.md §2–3; transfer/TRANSFER.md §2 -->

### 5.2 Labels set the ceiling
Documented sites are reports, not inventories. Most carry approximate coordinates, about 500 m of uncertainty, and are matched at
30 m; many storms have two to five sites. Spatial skill at 300 m is therefore hard to separate from label placement, and an
unreported flagged road cannot be called a false alarm. The one complete inventory, Leominster's damage list, shows the second
constraint: most of what the model misses there failed by edge erosion or washout with little ponding, a mechanism a depth-based
rule cannot see. Of 30 MassDOT repeat-flooding sites in the District, 3 have a segment closed within 150 m in the September 2023 run;
these are mostly drainage-capacity problems at a scale the 20 m model does not resolve.
<!-- src: transfer/TRANSFER.md §6; phase1/LEOMINSTER_MISSES.md; turing/d3_sep2023_t2/REPORT.md -->

### 5.3 What an agency can use now
The evidence supports two uses: a ranked watch list for a coming storm (the forecast's 2-of-8 list, ordered by π) and a standing
vulnerability layer for planning inspections, including the crossings whose blockage would close roads. It does not support
segment-level closure warnings.

### 5.4 Consequences fall on dry roads
In the September 2023 run, 99 % of the residents who lose timely access to emergency services live on roads that stay dry, and 98 %
of the person-hours of lost access fall on them. A closure map alone understates the impact of a flash flood; the network position
of a closed road matters as much as its depth.
<!-- src: paper/data/d3_sep2023_t2_cascade.json totals.knock_on -->

---

## 6. Limitations
- **Labels.** Reports are positive-only and incomplete (Bekker and Davis 2020, R28); approximate locations; few sites per storm.
- **Under-prediction on light storms.** One curve-number scale, chosen on the calibration storm, under-predicts gauge rise on most
  other storms. Tests of antecedent moisture are not finished.
- **Processes not modelled:** storm drains, dams, sub-hourly rain, erosion and washout.
- **Spatial placement.** The fractions skill score at 300 m is at or below chance: the model ranks roads but does not place floods to
  within 300 m.
- **Road network.** 25 % of District 3 traffic counts are defaults; the transfer road-source control shows that the network used
  changes the lift.
- **Consequences.** No traffic assignment (detours are added on single shortest paths), a flat daily traffic profile, capacities by road
  class, facility locations from OpenStreetMap, night-time population, and no observed data to validate them against.
- **Development storms.** The calibration storm and one Worcester storm were used for design choices and are reported apart from the
  held-out set.
- **Scoring code.** Matching of approximate-location reports was widened during the study (29 → 43 out-of-sample forecast sites); the
  forecast results are given both as produced and on the 28 sites matched in both versions.
<!-- src: OUTLINE.md §8; advisors/datasets.md D14; forecast/ENSEMBLE_PARITY.md §2–3 -->

---

## 7. Conclusions and next steps
A physics-only flood model, run at 20 m on radar rain and read along every road, ranks road segments by flood risk better than the
alternatives an agency has today, and keeps that skill in districts it was never tuned on. It is a screen, not a warning: its fixed
closure rule catches few sites, its spatial placement is coarse, and its errors are dominated by the labels it is judged against
and by processes it does not represent, such as road-edge erosion and storm-drain capacity. The same model shows that the cost of a
flash flood falls mostly on people whose own roads stay dry.

Three steps would most improve the evidence: road-closure records with exact locations and times (agency operations logs or
crowdsourced traffic reports) in place of approximate news and spotter reports; damage inventories from a second storm, to test an
erosion term outside the calibration storm; and the one-time opening of the five locked storms once the model is frozen.

---

## Tables (drafts)

**Table 1. Data sources.**

| Data | Source | Use |
|---|---|---|
| Ground elevation, 1/3 arc-second (~10 m) | USGS 3D Elevation Program | terrain, road crests |
| Hourly rain, MultiSensor QPE Pass 2 (1 km) | NOAA MRMS | replays from Oct 2020 |
| Hourly gauge-corrected radar rain | Iowa Environmental Mesonet (MRMS archive) | replays before Oct 2020 |
| Hourly forecast rain (3 km) | NOAA HRRR | forecast mode |
| Land cover and imperviousness (NLCD 2021) | USGS / MRLC | curve number, Manning's n |
| Soils (SSURGO) | USDA NRCS | hydrologic soil group, curve number |
| Stream channels (NHDPlus HR) | USGS | channels, crossing notches |
| Stream gauges (stage, discharge) | USGS Water Data | calibration, checks |
| Road network (52,698 segments) | MassDOT road inventory | road readout, network |
| Bridges | FHWA National Bridge Inventory | bridge-deck rule |
| Road–stream crossings and culvert surveys | USGS, MA Stream Crossings Project, NAACC | culvert terms, notches |
| Emergency facilities | OpenStreetMap | access analysis |
| Population (2020 census blocks) | U.S. Census Bureau | access analysis |
| Flood reports | NWS Local Storm Reports, NOAA Storm Events, news, WX1BOX, SeeClickFix, MassDOT crash records | labels |
| Damage inventory, Sep 2023 | City of Leominster DPW | labels (calibration storm) |
| Warning polygons; 1 % annual-chance zone | NWS (IEM archive); FEMA NFHL | named alternatives |
<!-- src: advisors/datasets.md D01–D23 -->

**Table 2. District 3 storm catalogue and roles** (fixed before scoring).

| Storm | Area | Date | Hours | Rain | Role |
|---|---|---|---|---|---|
| sep2014 | Worcester | 2014-09-01 | 18 | none archived | not used (no radar rain) |
| aug2015 | Natick | 2015-08-15 | 18 | IEM gauge-corrected | locked |
| oct2016 | Worcester | 2016-10-21 | 18 | IEM gauge-corrected | locked |
| may2018 | Shrewsbury | 2018-05-15 | 18 | IEM gauge-corrected | held-out (added) |
| jul2018 | Worcester | 2018-07-17 | 18 | IEM gauge-corrected | locked |
| aug2018 | Natick | 2018-08-08 | 18 | IEM gauge-corrected | locked |
| aug2018b | Holden | 2018-08-11 | 22 | IEM gauge-corrected | held-out (added) |
| sep2018 | Fitchburg | 2018-09-18 | 18 | IEM gauge-corrected | held-out (added) |
| sep2018w | Shrewsbury | 2018-09-18 | 18 | IEM gauge-corrected | held-out (added) |
| sep2018m | Milford | 2018-09-18 | 18 | IEM gauge-corrected | held-out (added) |
| sep2018b | Gardner | 2018-09-26 | 18 | IEM gauge-corrected | held-out (added) |
| jul2019 | Spencer | 2019-07-06 | 18 | IEM gauge-corrected | held-out (added) |
| aug2019 | Oxford | 2019-08-07 | 18 | IEM gauge-corrected | held-out (added) |
| sep2019 | Northbridge | 2019-09-02 | 18 | IEM gauge-corrected | held-out (added) |
| jun2020 | Northbridge | 2020-06-28 | 18 | IEM gauge-corrected | held-out (added) |
| jun2020b | Gardner | 2020-06-28 | 18 | IEM gauge-corrected | held-out (added) |
| aug2020 | Worcester | 2020-08-23 | 18 | IEM gauge-corrected | locked |
| aug2020b | Worcester | 2020-08-27 | 18 | IEM gauge-corrected | held-out (added) |
| jul2021 | Worcester | 2021-07-09 | 18 | MRMS Pass 2 | held-out (OOS-7) |
| jul2021b | Worcester | 2021-07-17 | 24 | MRMS Pass 2 | held-out (added) |
| aug2021 | Worcester | 2021-08-19 | 18 | MRMS Pass 2 | development |
| sep2021 | Worcester | 2021-09-01/02 | 24 | MRMS Pass 2 | held-out (OOS-7) |
| sep2022 | Webster | 2022-09-05 | 18 | MRMS Pass 2 | held-out (OOS-7) |
| jul2023b | Worcester | 2023-07-10 | 18 | MRMS Pass 2 | held-out (added) |
| jul2023 | Worcester | 2023-07-14 | 18 | MRMS Pass 2 | held-out (OOS-7) |
| jul2023c | Fitchburg | 2023-07-16 | 18 | MRMS Pass 2 | held-out (added) |
| jul2023d | Hubbardston | 2023-07-21 | 18 | MRMS Pass 2 | held-out (added) |
| aug2023 | Metrowest | 2023-08-08 | 18 | MRMS Pass 2 | held-out (OOS-7) |
| aug2023b | Millbury | 2023-08-18 | 18 | MRMS Pass 2 | held-out (OOS-7) |
| sep2023 | Leominster | 2023-09-11 | 36 | MRMS Pass 2 | development |
| aug2026 | Leominster | 2026-08-03 | 18 | MRMS Pass 2 | held-out (OOS-7) |

Districts 4–6: 81 further storms (498 sites), all held out (transfer test). <!-- src: obs/catalog.json; PROTOCOL.md v2 §2; transfer/TRANSFER.md -->

**Table 3. Old GPU runs against the parity baseline, nine catalogue storms** (sites caught / labelled, share flagged by the rule, lift,
mean absolute gauge-rise error).

| Storm | Sites | Flagged | Lift | Gauge rise error (m) |
|---|---|---|---|---|
| Jul 2021, Worcester | 1/5 → 0/5 | 1.22 → 0.19 % | 8.3 → 0.0 | 1.68 → 1.32 |
| Aug 2021, Worcester | 5/12 → 3/12 | 2.24 → 1.11 % | 16.0 → 10.5 | 0.76 → 0.40 |
| Sep 2021, Worcester | 2/5 → 2/6 | 4.07 → 2.41 % | 4.6 → 7.1 | 1.46 → 1.00 |
| Sep 2022, Webster | 0/4 → 0/4 | 1.87 → 0.61 % | 0.0 → 0.0 | 0.14 → 0.14 |
| Jul 2023, Worcester | 0/5 → 0/5 | 0.65 → 0.07 % | 0.0 → 0.0 | 0.24 → 0.18 |
| Aug 2023, MetroWest | 1/4 → 1/5 | 3.58 → 1.62 % | 4.0 → 5.2 | 0.69 → 0.19 |
| Aug 2023, Millbury | 0/2 → 0/2 | 0.51 → 0.11 % | 0.0 → 0.0 | 0.54 → 0.43 |
| Sep 2023, Leominster (calibration) | 28/78 → 35/89 | 2.80 → 2.16 % | 8.9 → 11.7 | 0.93 → 0.23 |
| Aug 2026, Leominster | 1/4 → 0/4 | 2.20 → 1.37 % | 6.6 → 0.0 | 0.90 → 0.29 |
| **All nine** | 38/119 → 41/132 | mean 2.13 → 1.07 % | | per-storm mean 0.82 → 0.46 |

Old runs matched labels without bridge decks, hence fewer labelled sites. <!-- src: parity/BASELINE.md §2 -->

**Table 4. Site recall in the top 3 % of segments, by method** (District 3: 23 held-out storms, 98 sites; Districts 4–6: 81 storms,
498 sites).

| Method | District 3 | Districts 4–6 |
|---|---|---|
| Model (depth rule order) | 0.20 | **0.21** |
| Model ranked by π | – | **0.25** |
| NWS flash-flood warnings | 0.05 | 0.09 |
| FEMA 1 % annual-chance zone | 0.12 | 0.07 |
| MassDOT repeat-flood points | 0.14 | – |
| Radar-rain threshold (tuned on calibration storm) | 0.05 | 0.06 |
| Terrain only (height above nearest drainage) | 0.08 | 0.10 |
| Static hazard × vulnerability × consequence | **0.32** | 0.10 |
| Chance | 0.07 | 0.09 |

District 3: the model beats warnings, rain threshold and terrain significantly; it is ahead of the FEMA zone and repeat points, and behind
the static score, without significance either way. Districts 4–6: the model beats every alternative significantly.
<!-- src: scoring/BENCHMARK_v3.md; scoring/PI_RANK_v3.md -->

**Table 5. Transfer: Districts 4–6 against District 3** (90 % CI).

| | Districts 4–6 (81 storms, 498 sites) | District 3 held-out (23 storms, 98 sites) |
|---|---|---|
| Rule: share flagged / site recall | 0.14 % / 0.036 [0.015, 0.058] | 0.43 % / 0.092 [0.022, 0.167] |
| Rule: lift | 6.7 [3.2, 10.6] | 6.4 [2.2, 10.6] |
| Top 3 %: site recall | 0.210 [0.167, 0.254] | 0.204 [0.104, 0.303] |
| Top 3 %: chance / lift | 0.086 / 2.46 [1.96, 2.97] | 0.066 / 3.10 [1.57, 4.60] |
| Top 3 %: FSS at 300 m | 0.017 (random 0.023) | 0.023 [0.015, 0.034] |
| Top 1 / 2 / 5 / 10 %: recall | 0.10 / 0.16 / 0.28 / 0.40 | – / – / – / 0.44 |
| Gauges: mean abs rise error / bias | 0.35 / −0.27 m (417 gauges) | 0.38 / −0.36 m (37 gauges) |
<!-- src: transfer/TRANSFER.md §2 -->

**Table 6. Learned and network candidates against the adoption rule** (held-out 23 storms; gain needs ≥ +0.04 at 3 % and a one-sided
lower bound above 0 at α/k).

| Candidate | Hits at 3 % (base → candidate) | Δ recall | Lower bound | Verdict |
|---|---|---|---|---|
| (a) Learned logistic, refitted per fold | 15 → 26 | +0.122 | 0.000 | rejected (significance) |
| (b) Pairwise ranking correction | 15 → 22 | +0.078 | −0.039 | rejected (significance) |
| (c) Storm-relative depth budget | 15 → 15 | 0.000 | 0.000 | rejected |
| (d) Rule first, learned score fills the budget | 15 → 26 | +0.122 | 0.000 | rejected (significance) |
| T1 Learned logistic + cascade features | 20 → 32 | +0.122 | −0.017 | rejected (significance) |
| T2 Rule first + cascade-feature score | 20 → 33 | +0.133 | 0.000 | rejected (significance) |
| T3 Cascade features against (a) | 30 → 32 | +0.020 | −0.076 | rejected (gain, significance) |
(a)–(d) were scored on the 90 sites of the first label round, T1–T3 on the 98 sites after the second.
<!-- src: ml/EXPANDED.md (90 sites: +11 sites = +0.122); cascade/CASCADE.md §4.2 -->

**Table 7. Consequences of the September 2023 storm, District 3 (T2 terrain, operational readout).**

| Quantity | Value |
|---|---|
| Road segments closed at some time / at the peak | 127 / 70 (at 8.0 h) |
| Delay at the peak (vehicle-hours per hour) | 7,379 |
| Delay over 48 h (vehicle-hours: detours / slowed traffic) | 119,739 (63,160 / 56,579) |
| Residents losing timely access at the peak (any service) | 76,450 |
| … to a hospital (30 min) / fire station (8 min) / police (10 min) | 26,518 / 45,686 / 38,617 |
| Residents cut off from every service at the peak | 7,886 |
| Of those losing access, living on roads that stay dry | 75,700 (99%) |
| Share of lost-access person-hours on dry roads | 98% |
<!-- src: paper/data/d3_sep2023_t2_cascade.json totals -->

**Table 8. Forecast rules, seven out-of-sample storms, operational physics** (site recall / mean share of segments flagged).

| Rule | Long lead (8–14 h) | Short lead (2–8 h) |
|---|---|---|
| Newest forecast only | 0.26 / 1.6 % | 0.14 / 1.0 % |
| Any of 4 | 0.37 / 3.7 % | 0.33 / 2.7 % |
| 2 of 4 | 0.28 / 2.0 % | 0.23 / 1.7 % |
| 2 of 8 (operational) | 0.33 / 2.8 % | 0.30 / 1.9 % |

43 sites. <!-- src: forecast/ensemble_parity.json pooled -->

---

## References (cited R numbers)

- R1. Zhang, J. et al. (2016). Multi-Radar Multi-Sensor (MRMS) quantitative precipitation estimation: initial operating capabilities. *BAMS* 97, 621–638. https://doi.org/10.1175/BAMS-D-14-00174.1 ; product notes: https://vlab.noaa.gov/web/wdtd/-/multi-sensor-qpe
- R6. Schwartz, C. S., Sobash, R. A. (2017). Generating probabilistic forecasts from convection-allowing ensembles using neighborhood approaches: a review and recommendations. *MWR* 145, 3397–3418. https://doi.org/10.1175/MWR-D-16-0400.1
- R8. Hawkins, R. H., Jiang, R., Woodward, D. E., Hjelmfelt, A. T., Van Mullem, J. A. (2002). Runoff curve number method: examination of the initial abstraction ratio. https://uon.sdsu.edu/hawkins_initial_abstraction.pdf
- R14. Bates, P. D., Horritt, M. S., Fewtrell, T. J. (2010). A simple inertial formulation of the shallow water equations for efficient two-dimensional flood inundation modelling. *J. Hydrol.* 387, 33–45. https://doi.org/10.1016/j.jhydrol.2010.03.027
- R15. de Almeida, G. A. M., Bates, P., Freer, J. E., Souvignet, M. (2012). Improving the stability of a simple formulation of the shallow water equations for 2-D flood modeling. *WRR* 48, W05528. https://eprints.soton.ac.uk/356385/2/WRR_2012.pdf
- R16. Shaw, J. et al. (2021). LISFLOOD-FP 8.0: the new discontinuous Galerkin shallow-water solver for multi-core CPUs and GPUs. *GMD* 14, 3577–3602. https://gmd.copernicus.org/articles/14/3577/2021/
- R19. Smith, G. P., Davey, E. K., Cox, R. J. (2014). Flood hazard. WRL Technical Report 2014/07 (ARR Project 10 basis; includes Shand et al. 2011 vehicle criteria). https://knowledge.aidr.org.au/media/2334/wrl-flood-hazard-techinical-report-september-2014.pdf
- R20. Martínez-Gomariz, E., Gómez, M., Russo, B., Djordjević, S. (2018). Stability criteria for flooded vehicles: a state-of-the-art review. *J. Flood Risk Manag.* 11, S817–S826. https://doi.org/10.1111/jfr3.12262 (open copy: https://zaguan.unizar.es/record/75630/files/texto_completo.pdf)
- R21. Kramer, M., Terheiden, K., Wieprecht, S. (2016). Safety criteria for the trafficability of inundated roads in urban floodings. *IJDRR* 17, 77–84. https://doi.org/10.1016/j.ijdrr.2016.04.003
- R23. Pregnolato, M., Ford, A., Wilkinson, S. M., Dawson, R. J. (2017). The impact of flooding on road transport: a depth-disruption function. *Transp. Res. D* 55, 67–81. https://doi.org/10.1016/j.trd.2017.06.020
- R28. Bekker, J., Davis, J. (2020). Learning from positive and unlabeled data: a survey. *Machine Learning* 109, 719–760. https://doi.org/10.1007/s10994-020-05877-5
- R32. Roberts, D. R. et al. (2017). Cross-validation strategies for data with temporal, spatial, hierarchical, or phylogenetic structure. *Ecography* 40, 913–929. https://www.biometrie.uni-freiburg.de/mitarbeiter/dormann/roberts-et-al-2017-ecography.pdf
- R33. Asif, M., Bentivoglio, R., Albano, R. (2026). CNN model for rapid prediction of urban flash flood water depth and velocity maps. *J. Hydrol.* 675, 135601. https://repository.tudelft.nl/record/uuid:8898c07c-8ea4-40f1-8da4-6ec2534bb52c
- R34. Bentivoglio, R. et al. (2025). Multi-scale hydraulic graph neural networks for flood modelling (mSWE-GNN). *NHESS* 25, 335. https://nhess.copernicus.org/articles/25/335/2025/
- R37. Safaei-Moghadam, A., Tarboton, D., Minsker, B. (2023). Estimating the likelihood of roadway pluvial flood based on crowdsourced traffic data and depression-based DEM analysis. *NHESS* 23, 1–19. https://nhess.copernicus.org/articles/23/1/2023/
- R39. Roberts, N. M., Lean, H. W. (2008). Scale-selective verification of rainfall accumulations from high-resolution forecasts of convective events. *MWR* 136, 78–97. https://doi.org/10.1175/2007MWR2123.1
- R40. Schall, J. D. et al. (2012). *Hydraulic Design of Highway Culverts*, 3rd ed., HDS 5, FHWA-HIF-12-026. Federal Highway Administration. https://rosap.ntl.bts.gov/view/dot/41317
