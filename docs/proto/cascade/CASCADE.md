# Cascading impacts of road flooding: engine, outputs and cascade-aware prediction

Code: `proto/cascade.py` (engine), `proto/cascade_ml.py` (cascade-aware features, nested LOSO). Outputs: `docs/site/data/<run>/cascade.json`
for `leominster_sep2023`, `worcester_aug2021` and `d3_sep2023`, and `docs/proto/cascade/CASCADE_ML.json` + `score_*.json`.
Nothing here changes `p_close`, the deployed rule or any published prototype / resilience output.

## 1. What the engine models

The flood model gives depth on every road segment at every frame. A closure is a local event. Its consequences are not local:

> closure → traffic re-routes → detour corridors load up → delay spreads to roads that never got wet → residents lose emergency-service
> coverage on dry roads → crossings overtop along the same stream → repair-cost exposure accumulates

The engine follows that chain on the District 3 road graph (`docs/graph_segments.json`, 52,698 segments, junction links), one output frame
every 30 min of model time.

### 1.1 Network state per frame

- **Closed.** The deployed rule: road depth *d* ≥ 0.30 m (equivalent to `p_close = Φ((d − 0.30)/0.10) ≥ 0.5`).
- **Slowed.** 0.05 ≤ *d* < 0.30 m. Speed is scaled by the Pregnolato et al. (2017) depth–disruption curve,
  f(d) = (0.0009 d² − 0.5529 d + 86.94) / 86.94, with *d* in mm, floored at 0.05. Below 5 cm f = 1; at 30 cm the segment is closed.
- **Travel time.** Free-flow minutes t₀ = L / v(class), with v = 45 / 65 / 95 km/h for local / arterial / highway (as in `sim/infra/impacts.py`).
  The graph is node-weighted: you pay a segment's time t₀ / f when you enter it.

### 1.2 Detours and delay

- Closed segments that touch form one **stretch**, so a flooded chain is one closure. Its through traffic is the largest AADT in the stretch.
- That traffic enters at the busiest open neighbour *u* and leaves at the busiest open neighbour *v* at another junction.
  Extra time Δτ = τ_wet(u→v) − τ_dry(u→v), on the whole graph, capped at 30 min. If there is no route within the cap, the trips are counted
  as **unserved**. This is `resilience.closure_detours`, extended to return the detour path.
- **Delay rate**, in vehicle-hours per hour, with q = AADT / 24:
  - D(t) = Σ_stretches q_s Δτ_s / 60 + Σ_slowed q_i t₀,i (1/f_i − 1) / 60.
  - Vehicle-hours = ∫ D dt, by trapezoid.
  - User cost = vehicle-hours × 1.67 persons per vehicle × $18.13 per person-hour (the `proto/risk.py` constants).

### 1.3 Overloaded detour corridors

- Each served stretch adds its daytime volume H · AADT_s to every segment on its detour path, with H = 0.06 of AADT per daytime hour.
- Per segment, V/C = H (AADT_j + Σ detour AADT through j) / CAP[class], with CAP = 1,000 / 2,000 / 4,000 veh/h for local-collector /
  arterial / highway segments (divided roads are one segment per direction). These are order-of-magnitude planning capacities.
- A segment is **overloaded** when it carries detour traffic and V/C > 1.
- Each stretch uses one shortest path and there is no equilibrium assignment. So per-corridor overload is an upper bound, and the network
  delay is a lower bound.

### 1.4 Connectivity loss

- Population comes from 2020 Census blocks (`docs/network/census_blocks_ma.npz`, POP20 > 0) whose internal point is in the box. Each block
  is placed on its nearest road segment.
- A block **loses** a service when it was within the standard dry and is not within it now. The standards are hospital 30 min, fire station
  8 min (NFPA 1710 travel) and police 10 min. A block loses the service if its own segment is closed, or if no open facility is within the
  standard over the wet network.
- A block is **isolated** when it has no route to any open hospital, fire or police station (`resilience.isolated_mask`). Blocks already
  isolated in dry conditions are excluded.
- The knock-on share separates two groups of people who lose access:
  - those on dry roads (their own segment is open, but the routes to the service are cut);
  - those on flooded roads.

### 1.5 Culverts and stream links

- Road–stream crossings come from `docs/network/crossings_all.json`. A crossing counts if it is within 30 m of an in-box road.
- It is **overtopped** from the first frame its road carries ≥ 15 cm. This is `risk.py`'s "water on the road within 30 m" rule,
  P = Φ((d − 0.15)/0.10) ≥ 0.5. The packs hold no headwater series.
- **Repair-cost exposure** is the `risk.culvert_cost` replacement range of every crossing overtopped so far. It is exposure, not
  expected loss.
- **Stream links** connect crossings on the same named stream within 3 km.
  - Downstream is the crossing with the larger drainage area, where both crossings have one. That is true for only ~1 % of MA crossings,
    so in these three runs every link is direction-unresolved.
  - For each link the engine reports whether the linked crossing also overtops, and with what lag.
  - Linked crossings that stay dry are listed as exposed to debris and surge. That exposure is not modelled.

### 1.6 Inputs and outputs

- **Input.** The public replay packs `docs/site/data/<run>/roads.json`: depth on the road per viewer frame, in cm, for every flagged
  segment. Segments that are not in the pack are dry.
  - Leominster and Worcester: 5-min packs, sampled every 6th frame. The viewer frame ids are kept in `frames`.
  - `d3_sep2023`: 30-min frames.
- `python proto/cascade.py outdir <prototype out>` runs the engine on a prototype output instead (the `segments.geojson` series of every
  segment ≥ 5 cm). `PROTO_CASCADE=1 python proto/prototype.py …` does this after a run. It is opt-in.

`cascade.json` (0.1–0.3 MB) contains:

- `frames`, `t_h`;
- `series`, per output frame: closed / slowed count and km, stretches, delay (detour, slow), unserved AADT, detour-carrying and overloaded
  segments, people losing hospital / fire / police / any service, people isolated, people losing access on dry roads, culverts overtopped,
  cost exposure;
- `totals`: peaks and their times, vehicle-hours, person-hours, the knock-on block, culverts;
- `closures`: the top 25 closed segments by delay caused, with graph segment ids;
- `corridors`: the top 25 detour corridors, with segment id, peak V/C, hours over capacity and over-capacity `intervals` in output-frame
  indices;
- `areas`: blocks that lose any service, as centroid lon/lat, pop, service mask, hours and intervals;
- `culverts`: lon/lat, road, stream, first hour, cost range, stream links.

## 2. Results: three storms

Run with `python proto/cascade.py pack leominster_sep2023 worcester_aug2021 d3_sep2023`, about 20–50 s per run. Every window is 48 h
(97 output frames).

**Network effects**

| run | in-box segments | peak closed (time) | segments ever closed / carrying detours / over capacity | spread ratio |
|---|---|---|---|---|
| leominster_sep2023 | 5,183 | 71 at 7.5 h | 101 / 282 / 69 | 3.6 |
| worcester_aug2021 | 8,566 | 56 at 6.5 h | 97 / 285 / 84 | 3.9 |
| d3_sep2023 | 45,099 | 112 at 9.0 h | 221 / 797 / 165 | 4.5 |

**Delay and access**

| run | peak delay, veh-h/h | vehicle-hours (detour / slow) and user cost | peak people losing a service (H / F / P) | peak isolated | person-hours lost on dry roads |
|---|---|---|---|---|---|
| leominster_sep2023 | 5,254 at 7.0 h | 59,108 (26,721 / 32,388); $1.8M | 30,271 (11,543 / 27,391 / 18,687) | 9,796 | 95 % |
| worcester_aug2021 | 4,150 at 7.0 h | 62,580 (25,538 / 37,042); $1.9M | 25,194 (5,638 / 20,602 / 18,933) | 4,898 | 90 % |
| d3_sep2023 | 6,614 at 8.5 h | 166,239 (85,586 / 80,653); $5.0M | 51,421 (16,982 / 38,189 / 31,846) | 11,077 | 94 % |

**Culverts**

| run | overtopped | replacement-cost exposure | stream links also overtopped |
|---|---|---|---|
| leominster_sep2023 | 113 | $13–61M | 248 of 752 (73 later) |
| worcester_aug2021 | 120 | $5–60M | 80 of 604 (17 later) |
| d3_sep2023 | 290 | $27–152M | 374 of 1,445 (103 later) |

Column notes:
- **Spread ratio**: segments ever affected (closed or carrying detour traffic) ÷ segments ever closed.
- **H / F / P**: hospital, fire station, police.
- **Person-hours lost on dry roads**: the share of person-hours of lost coverage borne by people whose own road is open.
- **Stream links "later"**: the linked crossing overtopped after the first one. The median positive lag is 0.5 h, which is one output frame.

**What the cascade view adds.**

- **Spread.** Closures are a small, local set. Their consequences reach 3.6–4.5× as many segments.
- **Most lost access is on dry roads.** At the peak, 90–95 % of the person-hours of lost emergency coverage fall on people whose own road
  never closes; their routes to a station are cut. A closure map alone shows none of this.
- **Timing.** The peak of delay and access loss arrives 6–8 h after the first closure, together with the peak closure count.
  - Delay then decays more slowly than closures do. Ponded closures persist, and their detours keep loading the same corridors to the end
    of the window. In Worcester, 19 segments are still over capacity at 48 h.
- **Where the knock-on lands.**
  - Leominster: the Route 2 / I-190 closures load the Leominster Connector and the I-190 ramps (peak V/C 2.9–4.2, about 42 h over
    capacity).
  - District 3: Route 2 closures in Harvard push through-traffic onto local streets in Ayer (Rogers / Mill / Shirley St, peak V/C ≈ 7,
    27 h over capacity). This is the kind of "dry road, real consequence" result emergency managers ask for.
  - Worcester: detours concentrate downtown (Front St, Washington Sq; V/C ≈ 3).
- **Culverts.**
  - 113–290 crossings are overtopped per run. The replacement-cost exposure is wide, $5–152M: crossing size is unknown for most of them,
    so the cost range spans pipe to large box.
  - Same-stream links mostly overtop in the same 30-min frame. Where a lag exists, it is one frame. At 30-min resolution the engine cannot
    yet resolve upstream→downstream propagation timing, and drainage-area direction is missing for 99 % of crossings.

**Check against `resilience.py`.** The `outdir` path on `docs/proto/worcester_aug2021` (the prototype output, every segment ≥ 5 cm)
reproduces `resilience.json`:

| metric | cascade.py (outdir) | resilience.json |
|---|---|---|
| vehicle-hours | 51,186 | 51,478 (the difference is the trapezoid end weights) |
| peak people losing hospital / fire / police / any service | identical: 11,599 / 53,134 / 48,704 / 67,695 | same |
| isolated | 6,836 | 11,341 (cascade.py leaves out people already isolated in the dry network) |

The same storm from the public pack gives 25,194 people losing any service, not 67,695. The pack keeps only flagged segments, so many
5–30 cm slow-downs are missing. **The pack numbers above are therefore lower bounds on slow-wet delay and access loss.** The closure-driven
parts (detours, corridors) are the same in kind.

## 3. Limits

- **Depth source.** The deployed closure rule on modelled depth. Its held-out skill is modest (3 % site recall 0.20 on held-out 23,
  `obs/LABELS_ROUND2.md`), so every knock-on number inherits that uncertainty. Packs omit unflagged wet segments (see §2).
- **Traffic.**
  - There is no equilibrium assignment. One wet shortest path per stretch, flat daily profile (q = AADT / 24) for delay, H = 0.06 for
    overload.
  - Capacities are by class only.
  - 75 % of local AADT is the 1,000 vpd default.
  - So overload is per-corridor plausible and an upper bound. Delay is a lower bound: there is no congestion feedback, and the detour cap
    is 30 min.
- **People.**
  - 2020 night-time population on the nearest segment.
  - Residents of closed segments count as having no coverage (stay-at-home is not modelled).
  - Facility locations come from OSM. The response standards are planning thresholds.
- **Culverts.**
  - Overtopping is the water-on-road proxy, not hydraulics. The packs carry no headwater series; `risk.py` uses the HDS-5 / headwater
    rules when a run directory is available.
  - Costs are replacement exposure, not expected loss. `proto/damage.py` needs discharge for fragility.
  - Stream links have no direction.
- **No validation data for knock-on effects.** No detour counts, no EMS response logs. The cascade outputs are scenario consequences of
  the modelled flood, not observed impacts.

## 4. Does cascade structure improve held-out road-flood prediction?

### 4.1 Pre-registration (committed before any held-out-23 number of these candidates was computed)

**Prior evidence.**
- Learned v2 already had five 300 m neighbour-depth features. In the ablation they moved ±1 site (`ml/LEARNED_v2.md` §2.2).
- Deep GNNs were judged too data-hungry for ~160 positives (`ROADMAP_research.md`).
- The question is therefore asked with the simplest model that can use the features: the v1 logistic. On held-out 23 it is the strongest
  learned ranking (`ml/EXPANDED.md`: +11 sites at 3 %, lower bound 0.000).

**Cascade features.** No labels are used. They are computed per storm from `features_<storm>.csv` and the graph links. The catalogue holds
peaks and durations but no frame series, so "lags" are graph hops and closure durations.

| feature | definition | sign |
|---|---|---|
| `cl_logkm` | ln(1 + km of the connected wet cluster, peak depth ≥ 0.15 m, containing the segment; for a dry segment, the largest wet cluster it touches) | + |
| `nb2_h30` | ln(1 + max hours over 30 cm among neighbours within 2 hops) | + |
| `nb2_closed` | ln(1 + number of neighbours within 2 hops that close) | + |
| `up_wet_km` | ln(1 + km of road within 1 km network distance that is upslope, i.e. higher HAND, and wet, ≥ 0.05 m): drainage-connected inflow along the road | + |

**Candidates.** PROTOCOL v2 §5a. Folds are nested LOSO over the 25 non-locked parity storms. Tests: *k* = 3, so α = 0.05 / 3 = 0.0167.

| test | candidate | base | question |
|---|---|---|---|
| T1 | `cas_v1`: v1 logistic recipe (C = 0.5, standardised, sign-constrained drop, storm-balanced, reporting domains) on MAIN + 4 cascade features; tier = in-fold equal-share threshold | depth rule | adoption |
| T2 | `cas_twotier`: depth rule first, then the rest of the budget in `cas_v1` order | depth rule | adoption |
| T3 | `cas_v1` | `a_v1`, the same recipe on MAIN only, same folds, refitted in the same run | do the cascade features add held-out skill? |

**Step (b).** The graph-regularised / label-propagation model is run **only if T3 meets conditions 1 and 2** (gain ≥ +0.04, lower bound
> 0 at α/k). Otherwise it is not run.

**Baseline.** The parity runs as published, scored in the same run on the current labels. They must match
`obs/round2/score_round2.json` (parity group) site for site, and the `--compare` against that file is also reported.

**Also reported:**
- per-storm ROC-AUC;
- the univariate within-storm AUC of each cascade feature;
- the coefficients of an all-storm fit (description only).

### 4.2 Result: no test passes; cascade features add nothing measurable; step (b) not run

**Run.** `python proto/cascade_ml.py run --boot 2000`, once, after the pre-registration commit (db85b747).
- Outputs: `docs/proto/cascade/CASCADE_ML.json` and `score_{base,a_v1,cas_v1,cas_twotier}.json`.
- To reproduce a verdict: `python proto/score_v2.py --compare docs/proto/cascade/score_base.json docs/proto/cascade/score_cas_v1.json --protocol v2 --k 3`.
- The in-run baseline equals `obs/round2/score_round2.json` (parity group) site for site. The `--compare` against that file gives the
  same verdicts.

**Verdicts** (held-out 23, 98 sites, box, 3 % flagged, α = 0.0167):

| test | hits @3 % (base → candidate) | Δ recall | one-sided lower bound | ΔFSS300 | worst storm | tier lift (base) | verdict |
|---|---|---|---|---|---|---|---|
| T1 `cas_v1` vs rule | 20 → 32 | +0.122 | −0.017 | +0.0056 | −1 | 5.67 (6.43) | reject (condition 2) |
| T2 `cas_twotier` vs rule | 20 → 33 | +0.133 | 0.000 | +0.0059 | −1 | 6.43 (= rule) | reject (condition 2) |
| T3 `cas_v1` vs `a_v1` | 30 → 32 | +0.020 | −0.076 | +0.0014 | −1 | 5.67 (6.43) | reject (conditions 1, 2) |
| *context: `a_v1` vs rule* | 20 → 30 | +0.102 | −0.018 | +0.0042 | −1 | | reject (condition 2) |

**Recall at 3 %, by pool** (90 % CI for held-out 23):

| | held-out 23 (98) | OOS-7 (40) | NEW16 (58) | dev2 (91) |
|---|---|---|---|---|
| depth rule | 0.204 [0.104, 0.303] | 0.275 | 0.155 | 0.363 |
| `a_v1` (MAIN) | 0.306 [0.209, 0.400] | 0.350 | 0.276 | 0.297 |
| `cas_v1` (MAIN + cascade) | 0.327 [0.232, 0.424] | 0.350 | 0.310 | 0.253 |
| `cas_twotier` | 0.337 [0.231, 0.439] | 0.400 | 0.293 | 0.385 |

**Ranking.** Mean per-storm ROC-AUC on held-out 23: rule 0.673, `a_v1` 0.763, `cas_v1` 0.762.

**Reading.**
- **The cascade features carry signal, but no new signal.**
  - Each feature alone ranks labelled segments above chance within a storm: mean AUC 0.66–0.68.
  - In the all-storm fit, three of the four keep positive weights (cl 0.09, nb2_h30 0.15, nb2_closed 0.19 per SD). `up_wet_km` is dropped
    for sign.
  - On top of the hazard and terrain features, they buy +2 held-out sites (T3, lower bound −0.08) and no ROC gain. The features mostly
    re-express the segment's own depth and flow accumulation through its neighbours. With 98 held-out sites, a +0.02 effect cannot be told
    from zero.
- **Dev storms move the other way.** `cas_v1` loses 4 dev sites against `a_v1` (27 → 23), so 2 of the 4 lost sites need explaining under
  the protocol. This fits the picture: in Leominster, neighbourhood flooding is already in the depth field.
- **The learned layer itself is still the useful thing.** It is just short of the significance bar.
  - `cas_twotier` is the best point estimate yet: 33/98 held-out sites at 3 %, tier unchanged. But its lower bound is 0.000, not > 0.
  - This is the same outcome as `d_twotier` / `a_v1` in `ml/EXPANDED.md`. The +11 to +13 sites are real-looking, but the storm-clustered
    bootstrap cannot exclude zero at α/k.
- **Step (b) was not run.** The pre-registered gate (T3 conditions 1–2) failed. With ~2 extra sites from the cascade structure, a
  graph-regularised or label-propagation model, let alone a GNN, would be fitting noise.
- **What it means for the thesis.** Cascade structure is a **consequence model** (§1–2): where delay, overload and lost access land. It is
  not, with this data, a **predictor** of where roads flood. Prediction is limited by the depth field and by label coverage, not by missing
  network context.

**Nothing is wired.** The deployed rule and the watch tier are unchanged.
