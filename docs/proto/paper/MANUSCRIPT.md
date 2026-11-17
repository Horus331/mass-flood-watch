# Paper 1 manuscript draft

Working title: *How well can a physics-only 2-D flood model tell which roads will close? A pre-registered out-of-sample evaluation in
central Massachusetts.* Structure and numbers follow `OUTLINE.md`; every number below comes from the repository file named in the
trailing `<!-- src: -->` comment of its paragraph (comments are removed before submission). References are the `R#` list of
`docs/proto/ROADMAP_research.md`; a missing reference is marked **[ref needed]**.

Status: sections 2–4 drafted (17 Nov 2026). Sections 1, 5–7 to follow.

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
practice; Schall et al. 2012 [ref needed]); culvert overtopping, from the HDS-5 headwater of the modelled peak flow at surveyed
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
