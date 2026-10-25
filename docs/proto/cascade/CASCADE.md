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

_(filled in by the results commit)_

## 3. Limits

_(filled in by the results commit)_

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

### 4.2 Result

_(filled in by the results commit)_
