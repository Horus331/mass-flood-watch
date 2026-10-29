# Research roadmap: improving the District 3 flash-flood road-closure model (23 Oct 2026)

## Status (25 Oct 2026)

Full ledger and open items: `STATUS.md`.

| task | status | where |
|---|---|---|
| T0 re-baseline at parity | **done** on CPU (25 storms, `LF_PARITY=1`, CN × 0.88); GPU confirmation landed, `parity_compare.py` + GPU catalogue rerun **open** | `parity/BASELINE.md` |
| T1 scoring v2 / PROTOCOL v2 | **done** | `PROTOCOL.md`, `scoring/BASELINE_v2_expanded.md` |
| T2 sub-hourly MRMS forcing | **not adopted** (opt-in `LF_RAIN_DT=5`) | `rain/RAIN.md` |
| T3 pluvial rule v2 | **not adopted** | `urban/PLUVIAL_v2.md` |
| T4 antecedent moisture | A, B1 **not adopted**; B0, C **open** (unfinished) | `runoff/AMC.md` |
| T5 learned layer v2 | **not adopted** (also failed on held-out 23) | `ml/LEARNED_v2.md`, `ml/EXPANDED.md` |
| T6 depth × velocity / duration rule | **open** (not started) | |
| T7 crossing damage fragility | **not adopted** (opt-in `PROTO_DAMAGE=1`) | `damage/DAMAGE.md` |
| T8 report-conditioned live update | **open** (not started) | |
| T9 drains v2 | **open** (not started; v1 not adopted) | `drains/DRAINS.md` |
| T10 10 m urban sub-boxes | **open** (start-up fix not done; `PROTO_RES_CONSISTENT=1` opt-in) | `res10m/FINDINGS.md` |
| T11 nowcast + REFS logging | **open** (REFS logging from 3 Nov 2026) | |
| T12 gauge-merging diagnostic | **open** (gauge-ratio checks in `rain/RAIN.md` only) | |

This is a plan only. No code was changed. It builds on the repo's own diagnoses: `recall/RECALL.md`, `urban/FINDINGS.md`, `urban/DCIA.md`,
`drains/DRAINS.md`, `res10m/FINDINGS.md`, `parity/PARITY.md`, `ml/LOSO.md`, `forecast/{HINDCAST,GATE,ENSEMBLE}.md`, `exp/DAMS_2026-10-22.md`
and `obs/CATALOG.md`. It also builds on the earlier scan in `docs/research/sota_2026-10-19.md`. Literature is cited inline as [n], and the
list is at the end.

## 0. What the evidence says, in order of weight

1. **The published baseline is not trustworthy yet.** PARITY.md found three problems in every Turing GPU number: GPU `hmax` spikes, missing
   infiltration, and a wrong gauge start level. On the four flash-miss storms, 53–65 % of GPU-flagged segments are spike-only. Every
   comparison below needs one baseline first: a CPU/GPU-consistent catalogue at `LF_PARITY=1`. Doing that is task T0.
2. **About half of the misses are label, matching or representability problems, not physics** (RECALL.md: 27 of 50 Leominster misses). Better
   labels and scoring that tolerates spatial displacement are the cheapest real gains. They also have to come before any claim that "model X is
   better".
3. **The physics misses split into three groups:**
   - **(a) Short urban convective bursts.** These are jul2023, aug2023b, sep2022 and aug2023, 1 of 15 caught. The cause is not the CN loss:
     with all pavement connected, `dcia1` still leaves ≤ 0.07 m on the street. The likely causes are pipe and inlet capacity being exceeded,
     sub-20 m street geometry and, for jul2023, radar under-catch.
   - **(b) Steep-street gutter and edge flow.** Wachusett St has 24 DPW misses. The model puts about 3 cm of slow water there.
   - **(c) Riverine under-prediction on wet storms.** Elsa and Ida gauge rises are 1.2–1.4 m low.
4. **At long lead, forecast skill is limited by where the rain falls, not how much.** Quantile mapping failed (ENSEMBLE.md). The time-lagged
   2-of-8 rule works. In 0–6 h, nowcasting and newer convection-allowing ensembles are the levers.
5. **The learned layer ranks better within a storm but worse at the top of the list** (LOSO.md: stratified AUC 0.783 vs 0.757, recall at the rule's
   share 0.12 vs 0.22). With 163 labelled segments, model capacity is not the limit. Labels and the training objective are.

**Already shown not to help (do not repeat without a new reason):**

| idea | result | where |
|---|---|---|
| storm drains as a 1:1 sink | equal-budget recall same or worse, gauge bias flips low | DRAINS.md |
| DCIA loss as a fix for flash misses | 1/15 caught, unchanged | DCIA.md |
| quantile mapping of HRRR | lift falls | ENSEMBLE.md |
| raw 10 m runs | 4× flags, mostly artefacts | res10m |
| monotone HistGB | worse than logistic | LOSO.md |
| generic design drains | removes 21 % of excess box-wide | DRAINS.md |
| dams + CFL 0.3 | lift falls in both storms | DAMS |

## 1. Research areas

### A. Rainfall input

**A1. Sub-hourly forcing (high value, cheap).** w9 drives LISFLOOD-FP with hourly MRMS Pass2, held constant over each hour (`rain_records`
'forward'). The flash-miss storms put 70–85 % of their rain in one hour (FINDINGS §1), and most of that probably fell in 15–30 min. MRMS
`PrecipRate` (2-min radar rate) is already read from AWS by `docs/site/build_rain.py`. The standard fix is **volume-preserving temporal
disaggregation**. Within each hour h and cell x:

    r_k(x) = Q1H_Pass2(x, h) · P_k(x) / Σ_k P_k(x)     (k = 5- or 10-min sub-steps; P_k = mean PrecipRate in the sub-step)
    fallback r_k = Q1H / n_k  where Σ_k P_k = 0 or more than 20 % of P_k are missing.

This keeps the gauge-adjusted hourly volume and imposes the radar's within-hour timing. LISFLOOD-FP's `dynamicrainfile` accepts any record
interval. The probe and convention code in w9 already handles the time stamps.

The literature is mixed:
- In urban sewer models, aggregating rain in time mainly shifts peaks by minutes. Spatial resolution matters more for depth (Bruni et al. 2015
  [12]: 10–30 % depth deviation from spatial aggregation).
- Ochoa-Rodriguez et al. 2015 [13] found that small urban catchments need ≤ 5 min rain to resolve peak flows.

For a 2-D surface model with no rate-limited sinks, ponded volume in a sag depends mainly on volume, so the depth gain may be small. The gain
should appear where **rates** matter:
- the constant infiltration (2 mm/h) and any inlet capacity, both less able to keep up with intense rain;
- gutter and edge velocity (Wachusett St);
- the pluvial rule, whose physics is the rational method Q = C·i(Tc)·A. Here i(Tc) is the intensity over the time of concentration (5–15 min
  for a street catchment), not the 60-min mean.

On a 15-min burst, i15 is typically 2–3× i60. So the expected gain lies more in the closure rules (A1 + C2) than in the solver.

- *Expected gain:* +1 to +4 of the 14 flash-miss sites through the pluvial rule. In the solver, probably ±1 site. A better arrival time on all storms.
- *Cost:* 1–2 days. Disk: 30 files/h × 18 h × about 1 MB, which is fine.
- *Risk:* PrecipRate is radar-only, with bright-band and hail contamination. The ratio form cancels the absolute bias.
- *Test:* the 4 flash storms plus 5 good storms, CPU on GitHub Actions, `cn` at `LF_PARITY=1`. Compare against the same runs with hourly rain.

**A2. Radar–gauge merging / local bias.** MRMS Pass2 already includes about 60 % of gauges, hourly, with a regional or local bias field (Zhang
et al. 2016 [1]; NOAA WDTD). Further merging could add:
- **Conditional merging** (Sinclair & Pegram 2005 [2]): M(x) = R(x) + [K_G(x) − K_R(x)]. Here K_G is the kriged gauge field, and K_R is the kriged
  field of radar values at the gauge locations. It keeps the radar's pattern and forces the gauge values.
- **Kriging with external drift** (radar as the drift).
- **Local multiplicative bias:** B(x) = Σ w_i G_i / Σ w_i R_i, with Gaussian weights of length about 10–20 km.

Ochoa-Rodriguez et al. 2019 [3] review these for urban use. Conditional merging and KED beat mean-field bias where gauges are dense. Merging
gives little benefit at the 5–15 km gauge spacings of central MA. Hourly gauges near District 3 are ASOS ORH, FIT and BED, USGS rain gauges, and
CoCoRaHS (daily only). That is too sparse to fix a 5-km convective cell.

- *Value:* **diagnostic.** It answers whether jul2023 was under-caught (FINDINGS §2c) before anyone tunes a rain multiplier.
- *Test:* leave-one-gauge-out error of the hourly maximum and the storm total, for Pass2 vs merged.
- *Expected gain:* jul2023 only, 0–2 sites. Low priority as a model change.

**A3. 0–2 h radar nowcasting.** pysteps [4] is open source and maintained. It provides:
- Lagrangian extrapolation;
- STEPS stochastic ensembles;
- since 2023, scale-dependent blending with NWP (Imhoff et al. 2023 [5]). NWP weights are set per cascade level from recent skill.

Imhoff et al. report that convective nowcasts beat NWP only for about 1–2.5 h (CSI crossover at the 5 mm/h threshold: 2–2.5 h). Blending gains up
to about 1 h of skill in the transition. For us this is the **only path to warnings during the burst itself**. Many reports come 0–2 h after rain
onset, so 0–2 h is operationally relevant. A full flood run per member is too slow on Actions (25–35 min/run). The cheap version drives the
pluvial rule and a "rain-to-closure" lookup. It needs only i_Tc and the 1–3 h totals per segment, from 20 pysteps members in about 2 min of CPU.
- *Test:* replay MRMS on the 9 storms. Issue the nowcast every 15 min and score lead-time-resolved recall against report times. Report times are
  "flooded by", so lead is a lower bound.

**A4. HRRR post-processing and new ensembles.** The live 20 km / 90th-percentile neighbourhood and the 2-of-8 lagged ensemble match the
standard methods (Schwartz & Sobash 2017 [6]). The neighbourhood maximum ensemble probability (NMEP) is the right statistic for the gate:
P(any point within r km exceeds X), averaged over members.

**News (verified):** NWS SCN26-48 [7] puts **RRFS and REFS into operations on 3 Nov 2026**. They replace HREF, NAM and SREF:
- RRFS deterministic: 3 km, 84 h at the synoptic cycles.
- RRFS ensemble: 5 members.
- REFS: current plus 6-h-old RRFS members plus 2 HRRR members, out to 60 h.
- Data on NOMADS (`com/rrfs/prod`, `com/refs/prod`). AWS is not mentioned in the notice.

REFS is a real multi-physics ensemble, which the lagged HRRR is not. But there is no archive to hindcast, so it must be validated forward:
log REFS from day one, score it alongside the 2-of-8 rule, and keep 2-of-8 until REFS has more than 5 scored storms.

### B. Runoff generation and urban hydrology

- **CN with Ia/S = 0.05.** Hawkins et al. [8] (307 watersheds; median λ ≈ 0.05) give S₀.₀₅ = 1.33·S₀.₂^1.15 (inches) and
  Q = (P − 0.05S)² / (P + 0.95S).
  - For pervious HSG C (CN 73, S₀.₂ = 94 mm), a 25 mm hour gives 1.8 mm with λ = 0.05 against 0.4 mm with λ = 0.2.
  - That is 4× more, but still small. DCIA showed that even 20 mm of extra excess on pavement does not make 0.3 m at 20 m.
  - **Expected effect on flash misses: about zero.** It may help the low-volume gauge responses. Run it only as part of B2's calibration grid.
- **Green-Ampt** f = K_s(1 + ψΔθ/F) or **Horton** f = f_c + (f₀ − f_c)e^(−kt). These are rate-based, so they respond to intensity, unlike the
  cumulative CN. With A1's sub-hourly rain, infiltration-excess on pervious ground in a 60 mm/h burst becomes real.
  - The sister engine (sota doc, "engine v3") already has Horton plus SSURGO plus a 14-day antecedent store. That code can be ported as
    `LF_LOSS=horton`.
  - Its value is on the **pervious hillside streets** (Wachusett St, rural washouts), not on paved downtowns.
- **B2. Antecedent moisture (high value for riverine).** Elsa (jul2021) and Ida (sep2021) gauge rises are 1.2–1.4 m low, while sep2023 is about
  right with the same ×0.91. Ida followed Henri by 10 days and Elsa followed a wet early July: these are textbook AMC-III cases.
  - Replace the one-storm CN×0.91 with AMC classes from 5-day antecedent MRMS (TR-55 AMC I/II/III), or with NWM v3 soil-moisture percentiles.
    NWM retrospective soil moisture has been evaluated for drought monitoring [9]. SMAP L3 is 36 km, too coarse but usable as a check.
  - Calibrate on **USGS gauge rise, LOSO**: fit the AMC-to-scale mapping on 8 storms and test on the 9th.
  - This targets riverine and culvert closures (most Leominster sites), where 30 % recall changes are possible.
- **What not to do:** DCIA variants, or per-storm CN tuning on labels (overfits 9 storms).

### C. Urban drainage

The DRAINS result is clear: a full-flow 1:1 sink with 100 % inlet efficiency and no return flow acts as a higher depth threshold and adds no
skill. Real dual-drainage models exchange flow between pipes and surface in both directions:
- **inlet capture** by weir/orifice equations (HEC-22 [10]):
  - sag grate as a weir: Q = C_w·P·d^1.5 (C_w = 1.66 SI);
  - sag grate as an orifice: Q = C_o·A·√(2gd) (C_o = 0.67);
  - HEC-22 design clogging of 50 % for sag grates;
- **surcharge return** at manholes when the pipe hydraulic grade line (HGL) rises above the ground, using the same orifice law with Δh = HGL − η;
- **outfall return** to the receiving stream.

Coupled SWMM–2D tools (Itzï, Iber–SWMM, TUFLOW, InfoWorks ICM) all use this exchange. Doing it fully needs pipe inverts, inlets and outfalls,
which only Leominster has.

**C1. Drains v2 for Leominster (medium value, medium cost; CPU because of the `mfw-drains` patch):**
1. Capture rate per inlet cell: q_in = min(HEC-22 capacity × (1 − c_clog), remaining network capacity), with c_clog ∈ {0.3, 0.5}.
2. Route the captured water per network with a lumped capacity from the outlet pipe (Manning full-flow).
3. Return the excess over network capacity as **surcharge at the lowest-rim inlets** of that network.
4. Return the captured volume at the **outfall** cells as point inflows. This fixes the gauge bias that flipped low.

This converts the sink into a redistribution. It can create flooding at surcharging low points, which a pure sink never can. That is the
mechanism behind the downtown standing-water labels.
- *Success:* at **equal flag budget**, city recall ≥ base + 2 sites. Mean gauge-rise bias within ±0.15 m.

**C2. Pluvial rule v2 (high value, cheap, no pipes needed).** Keep `PROTO_PLUVIAL`, with three changes:
- use i(Tc) from A1, with Tc from the Kirpich or kinematic-wave formula on the upstream path, instead of i_peak1h;
- write capacity as N_inlets × HEC-22 sag capacity × (1 − c_clog). N_inlets comes from road length times a design spacing (90–120 m). A pipe
  limit Q_pipe is used where pipes are known;
- use NLCD impervious for the runoff coefficient: C = 0.95·DCIA + 0.3·(1 − DCIA).

Re-select only the capacity and gate, by LOSO, exactly as in FINDINGS §3. The current rule already gains +4 of 29 OOS sites (5/29 → 9/29) at
+0.6 points of flagged share. Intensity at Tc is the variable the physics calls for.

### D. 2-D hydrodynamics numerics

- **Time step and spikes.** LISFLOOD-FP ACC [14,15] is explicit and limited by Δt = α·Δx/√(g·h_max). θ-weighting (de Almeida et al. 2012 [15];
  θ = 0.7) damps the checkerboard oscillations that create single-step `hmax` spikes.
  - PARITY showed that ≤ 1 s is converged on the CPU, and that the CUDA "never-increasing dt plus 10 s first step" policy creates spikes.
  - Independently of the fix, **stop reading closures from every-step `hmax`.** Use the max over 5-min snapshots (`LF_SAVEINT=300`), or require
    persistence: depth ≥ 0.30 m in ≥ 2 consecutive snapshots. A road is not closed by a 1 s spike. Cost: disk only.
- **Local-inertial limits.** ACC is valid for Fr below about 0.5–1 (Cozzolino et al. 2019, in sota doc). Steep streets with supercritical gutter
  flow are outside it.
  - LISFLOOD-FP 8.0 ships **FV1/DG2 full-SWE solvers on GPU** (Shaw et al. 2021 [16]). The same code base means no new toolchain.
  - A 10 m FV1 run on the Leominster urban sub-box is the cheapest test of the Wachusett-St class. Watch the cost: DG2 is about 10× ACC.
  - TRITON, SERGHEI and HiPIMS are also full-SWE GPU solvers. They offer no accuracy gain over LISFLOOD-FP FV1/DG2 and would cost a pipeline
    rewrite. **Not recommended.**
- **Sub-grid channels (SGC; Neal et al. 2012 [17]).** These replace the volume-equivalent channel burn and its `0.3·burn` start water. That
  water is the main suspect for the 10 m start-up artefact (res10m §2b) and for gauge timing. SGC runs only in the ACC CPU build in 8.x, so it is
  a CPU/Turing-CPU job. It is useful for gauge and culvert-overtopping timing. It is not a fix for street flooding.
- **Resolution and roads.** Ozdemir et al. 2013 [18] show that kerbs and road cambers control urban flow paths at metre scale. Roughness cannot
  stand in for missing geometry.
  - At 20 m, streets are not channels. The cheap substitute already exists in `prototype.py`: the crest snap, sags, and the edge layer.
  - A real step is **10 m (or 5 m) urban sub-boxes**, about 4 M cells per 20 km box at 10 m (1.5 min of GPU per hour of storm), run after
    fixing the start-up water: per-resolution burn depth, a breach cap scaled with resolution, `initial_tstep` ≤ 1 s, θ = 0.7, CFL 0.5.
  - Burn kerbs only where the MassGIS road edge lines exist, as a −0.10 m gutter strip. That is a research option, not in the top 12.

### E. Road-closure physics

- **Depth–velocity (DV) instead of depth only.**

  | criterion | small car | large car | large 4WD |
  |---|---|---|---|
  | still-water depth limit | 0.30 m | 0.40 m | 0.50 m |
  | depth limit at high velocity | 0.10 m | 0.15 m | 0.20 m |
  | v·y limit | ≤ 0.3 m²/s | ≤ 0.45 m²/s | ≤ 0.6 m²/s |
  | maximum velocity | 3.0 m/s | 3.0 m/s | 3.0 m/s |

  These are the Australian Rainfall & Runoff interim criteria (Shand et al. 2011; Smith, Davey & Cox 2014 [19]). Martínez-Gomariz et al. 2018
  [20] call them the safest available. Kramer et al. 2016 [21] give trafficability limits for emergency vehicles, and pedestrians are unstable at
  roughly v·y ≥ 0.22 m²/s (Martínez-Gomariz et al. 2016 [22]).

  Proposed closure rule:

      p_close_DV = Φ( max( (h − 0.30)/0.10 , ln(h·v / 0.30)/0.35 ) )   with h·v from 5-min snapshots (LF_VOUT, vsnap)

  For traffic disruption below closure, add the depth–speed function of Pregnolato et al. 2017 [23]: v_kmh = 0.0009w² − 0.5529w + 86.9448
  (w in mm), with v = 0 at w ≥ 300 mm. That serves the advisors' resilience and cost layer (vehicle-hours lost).
  - *Expected gain:* small on standing-water labels. Moderate on "impassable / washout" labels at 10–30 cm of fast water, which is class B in
    RECALL, 15 sites.
  - *Risk:* 20 m velocities are cell means and understate gutter velocity. They are also spiky, so persistence filtering is needed.
- **Duration.** Agencies close a road when water persists. Require at least 10–15 min above threshold (snapshot count), and add arrival time
  so a closure has a when as well as a where.
- **Washout and damage labels.** The DPW inventory is mostly edge washouts. The current edge layer (`p_edge`: permissible velocity
  1.0 m/s and permissible shear γhS, 11 Pa, HEC-15 [24]) is well grounded. Its failure on Wachusett St is a **hydraulics** failure (3 cm of slow
  water at 20 m), not a threshold failure.
  - For culvert and bridge damage, add **specific stream power** ω = γQS/w at crossings, the predictor that separated damaged from undamaged
    Vermont bridges after Irene (Anderson et al. 2017 [25]). NCHRP Synthesis 496 [26] documents the overtopping damage modes: toe erosion that
    head-cuts upstream, and pavement undermining on the downstream side.
  - Fragility form: P(damage) = Φ(ln(ω/ω₅₀)/β), with ω₅₀ fitted LOSO on the DPW and culvert labels.

### F. ML / AI

- **The objective matches the use case: rank within a storm, best at the top.** LOSO showed AUC gains but losses in the top 2 %. Two fixes:
  1. **Within-storm pairwise ranking.** LambdaMART [27] uses the storm as the "query" and optimises NDCG@k, k = 2 % of segments. It keeps the
     monotone constraints and uses the rule's logit as a base margin (offset), so the model learns a correction and cannot discard depth.
     LOSO.md showed that a plain feature for the rule logit got a negative coefficient. An offset avoids that.
  2. **Graph-neighbour features.** Add max depth / p_close within 100 and 300 m **along the road graph**, upstream crossing overtopping, and
     segment position relative to a sag. This targets RECALL class A (9 sites flooded within 100 m but on another segment) without loosening the
     scoring. It is cheaper and better posed than a GNN with 163 positives. Defer GNNs until there are more than 1000 labelled segments.
- **Positive-unlabelled learning.** Labels are "documented", not "closed". Use the SAR-PU framework (Bekker & Davis 2020 [28]):
  - P(label | closed, x) = e(x), a *propensity* that depends on reporting (town, road class, AADT).
  - Weight positives by 1/e(x) and treat unlabelled data as a mixture.
  - e(x) can be estimated from the MassDOT events log and the LSR density per town.
  - Li et al. 2022 [29] found that PU (PBLC) kept AUC but fixed the probabilities that ordinary training biased toward 0. That matches our
    calibration complaint (BSS −0.17).
  - The Elkan–Noto c failed here (LOSO.md) because no region is near-certain. SAR-PU with an explicit propensity is the fix.
- **Calibration and conformal.** Ranking is the operational output. For honest probabilities, use **Venn–Abers or isotonic calibration per
  storm-type stratum**, fitted LOSO. Conformal guarantees [30,31] assume exchangeable storms. With 9 storms the intervals would be wide, so use
  conformal only for the **gauge-rise and depth regressions**, where hundreds of gauge-hours exist. Low priority.
- **Spatial cross-validation.** LOSO plus leave-one-area-out is already right (Roberts et al. 2017 [32]). Add 2 km block bootstrap for all
  intervals (already done) and **pre-register** metrics (Section 3).
- **Surrogates / emulators.** CNN surrogates of 2-D pluvial models now report CSI ≈ 0.8 at about 100× speed-up on one city (Asif, Bentivoglio &
  Albano 2026 [33]). Mesh GNNs generalise better (Bentivoglio et al. 2025 [34]). We do not need one yet: District 3 at 20 m takes 17 min per GPU,
  so 8 members on 4 Turing GPUs take about 35 min. Revisit only for 50+ member nowcast ensembles (A3) or a probabilistic design-storm atlas.
  **Update 29 Oct 2026: now needed.** `forecast/DISTRICT.md` showed that the District 3 map needs the 2-of-8 ensemble district-wide every
  6 h, and Turing is not on that schedule. A surrogate that runs on GitHub Actions CPUs would make that possible. Pre-registered in
  `surrogate/SURROGATE.md` (district-wide / ensemble layer only; not run yet).
- **Data assimilation.**
  - *Gauges:* an EnKF on water levels (Annis et al. 2022 [35]: NSE +5–40 %, bias −80 % with gauges plus SAR). That is heavy for a 2-D grid. The
    cheap and effective version for us is a **rain-multiplier particle filter**: run K = 5–8 rain scalings (0.7–1.6) as members, weight them by
    the likelihood of the observed USGS rise so far, and re-weight the closure ensemble.
  - *Reports:* treat each incoming MassDOT event or LSR as an observation. Raise P on segments sharing the same sub-catchment or road within
    500 m via a spatial likelihood ratio. This is simple Bayesian conditioning, and it fixes the "nearby segment" misses in real time.

### G. Labels and validation

- **Sources.**
  - The MassDOT roadway-events XML is already logged every 15 min (`events_log.yml`, since Oct 2026). Keep it. It will be the first source
    with closure **times and durations**, but it covers state roads only.
  - The other feeds (GoTime, Connected Work Zone WZDx) are listed in [36]. WZDx is for work zones, not floods.
  - **Waze for Cities** (data-sharing partnership) gives timestamped flood alerts. Safaei-Moghadam et al. 2023 [37] showed Waze flood alerts in
    Dallas cluster at **local surface depressions, not river flood zones**. That is exactly our pluvial miss class, and a depression and catchment
    model predicted them. A Norfolk study found 72 % of Waze flood reports trustworthy [38].
  - Also: municipal 311 (Worcester), DPW work orders, and **OpenFEMA Public Assistance project worksheets** for declared events (site-level
    road repairs with costs, also useful for the repair-cost layer).
  - **A second complete DPW inventory (Worcester, one storm)** remains the highest-value single dataset (LOSO.md).
- **Metrics for rare, displaced events.** Keep strict recall at equal flagged share and chance-corrected lift. Add:
  - **PR-AUC within reporting domains.**
  - **Critical success index**, CSI = H/(H + M + F), only inside "complete" domains (Leominster DPW city). Elsewhere false alarms are undefined.
  - **Road-network fractions skill score**: FSS = 1 − Σ(P_f − P_o)² / (ΣP_f² + ΣP_o²) over windows of 100, 300 and 1000 m of along-road
    distance (Roberts & Lean 2008 [39]). FSS > 0.5 + f_o/2 is "useful".
  - FSS replaces the ad hoc tolerant matching. It credits near misses but penalises flagging everything, which RECALL §2 showed tolerant
    matching does not.
- **Reporting bias.** Model it explicitly (the PU propensity above). Report all scores both inside reporting towns and box-wide, as LOSO.md
  already does.

## 2. Ranked plan (expected gain per effort)

Legend: **GHA** = GitHub Actions (4 CPU, 6 h); **TUR** = Turing GPU (or CPU partition). "Sites" = documented label sites. "Flash" = jul2023,
aug2023b, sep2022 and aug2023 (14 sites); "OOS-7" = the 7 storms no rule was built on (29 sites).

| # | task | expected gain | effort | compute |
|---|---|---|---|---|
| T0 | Re-baseline the catalogue at parity, with persistence-filtered depth | correctness; flash-storm false flags −50 % | 1 d plus queue | TUR (GPU), GHA spot checks |
| T1 | Scoring v2: pre-registration, road-network FSS, propensity strata | honest numbers; no recall change by design | 2 d | GHA |
| T2 | Sub-hourly MRMS forcing (PrecipRate disaggregation) | +0 to +3 flash sites via rules; better timing | 2 d | GHA (9 storms × 2 variants) |
| T3 | Pluvial rule v2: i(Tc), HEC-22 inlet capacity with clogging | +2 to +5 OOS-7 sites at ≤ +1 pt share | 1–2 d | GHA (reprocess only) |
| T4 | Antecedent-moisture loss, calibrated LOSO on gauges | gauge MAE −30 to −50 % on Elsa/Ida; +1 to +3 riverine sites | 3 d | GHA |
| T5 | Learned layer v2: rule-offset ranking, graph-neighbour features, SAR-PU weights | top-2 % recall ≥ rule; +3 to +8 pooled at 5–8 % | 3–4 d | GHA |
| T6 | DV and duration closure rule, plus Pregnolato disruption | +0 to +4 class-B sites; resilience metric | 1–2 d | GHA (needs `LF_VOUT`/vsnap re-runs → TUR) |
| T7 | Stream-power culvert/bridge damage fragility | culvert/washout labels: +2 to +6 of 36 | 2–3 d | GHA |
| T8 | Report-conditioned real-time update plus gauge rain-multiplier filter | live: catches "next segment" misses after the first report | 3–4 d | GHA |
| T9 | Drains v2 (capture/surcharge/outfall return), Leominster | ±2 city sites; fixes gauge bias | 4–5 d | GHA/TUR CPU |
| T10 | 10 m urban sub-boxes after the start-up fix; FV1 test on steep streets | Wachusett class: unknown, 0 to +10 DPW points | 4–6 d | TUR |
| T11 | Nowcast 0–2 h (pysteps) feeding the rules; REFS logging from 3 Nov 2026 | lead time during bursts; forward validation only | 4–5 d | GHA |
| T12 | Gauge-merging diagnostic for jul2023/aug2023b | resolves under-catch question; 0–2 sites | 1–2 d | GHA |

### Task details

**T0 — Re-baseline (prerequisite for everything).**
- *Change:*
  - Run the Turing catalogue with `LF_PARITY=1 LF_SAVEINT=300 LF_VOUT=1`, recording `GIT_SHA`. Run all 9 storms plus the Leominster GPU and
    D3 runs.
  - In `prototype.py`, add `PROTO_DEPTH_SRC=snap` (closure depth = max over 5-min snapshots; a spike needs 2 consecutive snapshots).
  - Re-derive `features_*.csv`, RECALL, LOSO and the tier threshold.
- *Data:* existing.
- *Validate:* `parity_compare.py` MATCH between GPU and CPU on jul2023 and sep2023. `hmax_above_snapshots` ≤ 2 segments per storm.
- *Success:* GPU and CPU flagged-segment Jaccard ≥ 0.9.
- *Compute:* about 9 × 10 min GPU, plus a 10 m rerun.
- *Depends on:* nothing. Note: CN×0.91 must be re-checked here (PARITY §6).

**T1 — Scoring v2 and pre-registration.**
- *Change:*
  - Add `proto/score_v2.py`: road-network FSS at 100/300/1000 m along-road windows; PR-AUC and CSI in complete domains; equal-budget recall.
  - Add a `PREREG.md` that fixes, before any new run:
    - the metrics, storms and confidence intervals (2-stage cluster bootstrap);
    - the adoption rule: adopt a change if equal-budget pooled recall gain has a 5 % lower bound ≥ 0 **and** no storm loses more than 1 site
      **and** lift ≥ 0.8 × baseline.
- *Data:* labels plus a `coord_quality`-specific uncertainty radius: exact 30 m, approx 500 m, town 1500 m, used in FSS.
- *Success:* reproduces current numbers. All later tasks report through it.
- *Compute:* GHA.

**T2 — Sub-hourly rain.**
- *Change:* add `LF_RAIN_SUBH=10` to w9, reusing the `build_rain.py` fetcher. Records every 10 min, volume-matched to Pass2. Write i10, i15 and
  i30 maxima to `rainstats.npz`.
- *Validate:* run all 9 storms, hourly vs 10-min, `cn`, `LF_PARITY=1`. Check:
  - flash-site depth;
  - edge and DV layers on Wachusett;
  - gauge rise and peak-time error against USGS 15-min data;
  - equal-budget recall.
- *Success:* gauge peak-timing MAE improves, and no loss of lift. A recall gain is not required; the value is mainly as input to T3 and T6.
- *Compute:* GHA, about 18 runs × 30–40 min. *Depends on:* T0 (settings) and T1.

**T3 — Pluvial rule v2.**
- *Change:* `PROTO_PLUVIAL=2` in `prototype.py`:
  - Tc per segment from the D8 path (Kirpich, minimum 5 min);
  - i(Tc) from T2;
  - C from NLCD DCIA;
  - capacity Q_cap = n_in · Q_HEC22(d = 0.10 m) · (1 − c_clog), with n_in = road length / 100 m in the upstream catchment;
  - LOSO selection of c_clog ∈ {0.3, 0.5, 0.7} and the density gate only.
- *Validate:* LOSO on the 9 storms, OOS-7 headline. Null models: random extra segments; `PROTO_PLUVIAL=1`.
- *Success:* OOS-7 ≥ 11/29 at mean share ≤ 3 %, beating v1 (9/29 at 2.6 %).
- *Compute:* GHA, reprocess only. *Depends on:* T2 (needs i(Tc); with hourly rain it degenerates to v1).

**T4 — Antecedent moisture.**
- *Change:*
  - Add `LF_CN_AMC=auto` to w9: 5-day antecedent MRMS → AMC I/II/III (TR-55 thresholds), or an NWM soil-moisture percentile mapped to the CN
    scale.
  - Calibrate a single scale curve LOSO on USGS rises: about 20 gauges over 9 storms.
- *Data:* MRMS 5 days before t0 (already on AWS); NWM v3 retrospective/analysis on AWS (`nwm.yml` exists).
- *Validate:* gauge rise MAE and peak timing, LOSO; then label recall.
- *Success:* mean absolute rise error on the 5 good storms drops from 0.64 to ≤ 0.4 m, with no flash-storm increase in false flags.
- *Compute:* GHA (9 storms × 3 variants). *Depends on:* T0.

**T5 — Learned layer v2.**
- *Change:* in `closure_ml.py`, add `rank` mode:
  - LightGBM `lambdarank`, query = storm, monotone constraints on the hazard features, init score = rule logit;
  - graph features from `docs/graph_segments.json` links (k-hop max depth, max p_may, upstream crossing overtop);
  - SAR-PU weights 1/ê(x), where ê(x) is a logistic model of "reported | flagged by rule" on town reporting rate, road class and AADT.
- *Validate:* nested LOSO plus leave-one-area-out. Score with T1 metrics. The tier threshold is chosen inside the folds.
- *Success:* recall at the rule's share ≥ the rule's (0.22), and stratified AUC ≥ 0.78. Otherwise keep the hybrid.
- *Compute:* GHA. *Depends on:* T0 (features re-derived) and T1.

**T6 — DV, duration and disruption.**
- *Change:*
  - `PROTO_DV=1`: p_close = max(depth term, DV term) from snapshot h·v, with a persistence of ≥ 2 snapshots of 5 min.
  - Add `speed_kmh` per segment from Pregnolato for the resilience layer (vehicle-hours lost).
- *Validate:* class-B and washout labels; equal-budget recall; OOS-7.
- *Success:* +2 class-B sites at ≤ +0.5 points share, and no loss on standing water.
- *Compute:* GHA reprocess when vsnap exists (it requires T0 runs with `LF_VOUT=1`).

**T7 — Crossing damage fragility.**
- *Change:* compute ω = γQS/w at each crossing from `LF_QOUT` face fluxes (S from lidar over ±50 m, w = bankfull width). Add a `p_damage`
  layer with ω₅₀ and β fitted LOSO on culvert-failure, washout and bridge labels. It is a separate map layer, not added to p_close.
- *Validate:* AUC among crossings with labels (Leominster DPW plus news) against the HDS-5 overtopping layer.
- *Success:* the damage AUC CI excludes the HDS-5 layer's AUC, or the layer is dropped.
- *Compute:* GHA. *Depends on:* T0.

**T8 — Real-time conditioning.**
- *Change:* in `forecast_kofn.py`, add:
  - a report likelihood update (closure event → segments in the same HUC-12 sub-catchment or same road within 500 m get odds × LR, with LR
    fitted LOSO from label clustering);
  - K rain-multiplier members weighted by the USGS rise likelihood (Gaussian, σ = 0.2 m).
- *Validate:* replay the 9 storms in time order and reveal labels by `time_local`. Measure recall of not-yet-reported sites at 1–2 h after
  the first report.
- *Success:* conditional recall of the remaining sites +0.1 over unconditioned, at the same share.
- *Compute:* GHA.

**T9 — Drains v2.**
- *Change:* in `lf_drains.py`, add capture capped by HEC-22 with clogging, network capacity, surcharge return at the lowest-rim inlets, and
  outfall point sources.
- *Validate:* Sep 2023 and Aug 2026 Leominster, equal-budget city recall, gauge bias. Add a third, moderate Leominster storm from the events log
  when one occurs.
- *Success:* see C1. If it fails, close the drains line of work for the dissertation, with this as the documented negative result.
- *Compute:* CPU (GHA ≤ 6 h or Turing CPU).

**T10 — 10 m urban sub-boxes and a full-SWE check.**
- *Change:*
  - In w9: per-resolution burn depth (scale by min(CW/RES, 1) on the 30 m raster, resampled area-weighted, not nearest); breach cap ∝ RES;
    `LF_THETA=0.7 LF_CFL=0.5`.
  - Then 10 m runs of the Leominster and Worcester urban 8 × 8 km sub-boxes.
  - One FV1 (GPU) run on Leominster at 10 m.
- *Validate:* first-snapshot wet area ≈ 20 m value (0.8 km²); Wachusett DPW points; flash-storm sites; equal-budget recall.
- *Success:* the DPW distinct-location recall on Wachusett rises without the flagged share exceeding 1.5× the 20 m share.
- *Compute:* TUR.

**T11 — Nowcasting and REFS.**
- *Change:*
  - A `nowcast.yml` every 15 min when MRMS Pass1 (or PrecipRate) shows > 20 mm/h in District 3: pysteps STEPS, 20 members, 0–2 h, blended with
    HRRR beyond 1 h.
  - Per-segment i(Tc) and 1 h exceedance probabilities feed T3's rule and the T5 ranker.
  - Log REFS from NOMADS from 3 Nov 2026.
- *Validate:* MRMS replay of the 9 storms for the nowcast. REFS forward only.
- *Success:* the median warning arrives ≥ 30 min before the first report time on 50 % of storms, at the T3 rule's precision.
- *Compute:* GHA.

**T12 — Gauge merging diagnostic.**
- *Change:* add `proto/rain_check.py`: conditional merging of Pass2 with ASOS 5-min (IEM), USGS precipitation gauges and CoCoRaHS (daily
  totals); leave-one-gauge-out.
- *Success criterion:* a quantified under-catch factor for jul2023 with a CI. Adopt a merged field only if LOO error falls by more than 20 %.
- *Compute:* GHA.

**Order and dependencies.** T0 → T1 → (T2 → T3, T6), T4, T5, T7 in parallel → T8, T9, T10, T11. T12 can run any time and should run before
anyone tunes rain multipliers.

## 3. Validation protocol (fixed in advance; applies to every task)

1. **Baseline:** the T0 catalogue at `LF_PARITY=1`. Every variant is CPU against CPU or GPU against GPU on the same commit.
2. **Splits:**
   - LOSO over the 9 AWS-era storms. Leave-one-area-out (overlapping Worcester and Leominster boxes) as a leakage check.
   - The OOS-7 storms are the headline. sep2023 and aug2021 are development storms.
   - The 5 pre-2020 IEM storms (CATALOG §B) are a **locked test set**, opened once, after T3–T6 are frozen. That needs the IEM GaugeCorr reader.
3. **Metrics:**
   - strict site recall at equal flagged share (2, 5 and 8 %);
   - chance-corrected lift;
   - stratified ROC-AUC and PR-AUC within reporting domains;
   - road-network FSS at 300 m;
   - CSI in the Leominster DPW domain;
   - USGS gauge rise and peak-time error.
4. **Uncertainty:** two-stage cluster bootstrap (storms, then 2 km blocks or sites), 2000 replicates.
5. **Adoption rule:** see T1. Every negative result is published in `docs/proto/<topic>/` as the drains and DCIA results were.

## 4. What is unlikely to help (given our evidence)

- **Drains as a sink.** Revisit only as redistribution (T9).
- **More loss-model variants for the flash misses.** DCIA all-connected leaves ≤ 0.07 m. λ = 0.05 adds less still.
- **Per-storm tuning of CN or rain multipliers on labels.** That overfits 9 storms. Calibrate on gauges, LOSO (T4).
- **Distribution bias correction of HRRR.** Placement, not intensity, is the error. Use ensembles and neighbourhoods.
- **Raw 10 m everywhere.** It is mostly artefacts until T10's start-up fix.
- **Switching solver family** (TRITON, SERGHEI, HiPIMS). No accuracy case beyond LISFLOOD-FP's own FV1/DG2.
- **GNNs, foundation tabular models, deep surrogates now.** 163 positive segments. Revisit after T5 and new labels. (Exception, 29 Oct 2026:
  a surrogate trained on the physics, not on labels, for the district-wide ensemble; `surrogate/SURROGATE.md`.)
- **Tolerant matching as a score.** Its chance recall inflates. Use FSS with a chance baseline.

## References

1. Zhang, J. et al. (2016). Multi-Radar Multi-Sensor (MRMS) quantitative precipitation estimation: initial operating capabilities. *BAMS* 97, 621–638. https://doi.org/10.1175/BAMS-D-14-00174.1 ; product notes: https://vlab.noaa.gov/web/wdtd/-/multi-sensor-qpe
2. Sinclair, S., Pegram, G. (2005). Combining radar and rain gauge rainfall estimates using conditional merging. *Atmos. Sci. Lett.* 6, 19–22. https://doi.org/10.1002/asl.85
3. Ochoa-Rodriguez, S. et al. (2019). A review of radar–rain gauge data merging methods and their potential for urban hydrological applications. *WIREs Water* 6, e1391. https://spiral.imperial.ac.uk/entities/publication/789a9597-c1a1-44d5-9c26-e3079546a518
4. Pulkkinen, S. et al. (2019). Pysteps: an open-source Python library for probabilistic precipitation nowcasting (v1.0). *GMD* 12, 4185–4219. https://doi.org/10.5194/gmd-12-4185-2019 ; docs: https://pysteps.readthedocs.io/
5. Imhoff, R. O. et al. (2023). Scale-dependent blending of ensemble rainfall nowcasts and NWP in the open-source pysteps library. *QJRMS* 149, 1335–1364. https://pure.tudelft.nl/ws/portalfiles/portal/151585350/Quart_J_Royal_Meteoro_Soc_2023_Imhoff_Scale_dependent_blending_of_ensemble_rainfall_nowcasts_and_numerical_weather.pdf
6. Schwartz, C. S., Sobash, R. A. (2017). Generating probabilistic forecasts from convection-allowing ensembles using neighborhood approaches: a review and recommendations. *MWR* 145, 3397–3418. https://doi.org/10.1175/MWR-D-16-0400.1
7. NWS Service Change Notice 26-48 (updated): Implementation of RRFS and REFS, effective 3 Nov 2026. https://www.weather.gov/media/notification/pdf_2026/scn26-048_Updated_RRFS_and_REFS_Implementation_aae.pdf
8. Hawkins, R. H., Jiang, R., Woodward, D. E., Hjelmfelt, A. T., Van Mullem, J. A. (2002). Runoff curve number method: examination of the initial abstraction ratio. https://uon.sdsu.edu/hawkins_initial_abstraction.pdf
9. Evaluation of retrospective National Water Model soil moisture and streamflow for drought-monitoring applications (NOAA IR). https://repository.library.noaa.gov/view/noaa/67766
10. FHWA (2009, rev. 2013). *Urban Drainage Design Manual*, HEC-22, 3rd ed., FHWA-NHI-10-009 (inlet interception, weir/orifice sag equations, clogging).
11. Sadeghi, F. et al. (2022). Assessing the performance of LISFLOOD-FP and SWMM for a small watershed with scarce data. *Water* 14, 748. https://pure.coventry.ac.uk/ws/portalfiles/portal/52117812/Published.pdf
12. Bruni, G. et al. (2015). On the sensitivity of urban hydrodynamic modelling to rainfall spatial and temporal resolution. *HESS* 19, 691–709. https://hess.copernicus.org/articles/19/691/2015/
13. Ochoa-Rodriguez, S. et al. (2015). Impact of spatial and temporal resolution of rainfall inputs on urban hydrodynamic modelling outputs: a multi-catchment investigation. *J. Hydrol.* 531, 389–407. https://spiral.imperial.ac.uk/entities/publication/c96fc865-091a-428a-93f7-5fdd70696dda
14. Bates, P. D., Horritt, M. S., Fewtrell, T. J. (2010). A simple inertial formulation of the shallow water equations for efficient two-dimensional flood inundation modelling. *J. Hydrol.* 387, 33–45. https://doi.org/10.1016/j.jhydrol.2010.03.027
15. de Almeida, G. A. M., Bates, P., Freer, J. E., Souvignet, M. (2012). Improving the stability of a simple formulation of the shallow water equations for 2-D flood modeling. *WRR* 48, W05528. https://eprints.soton.ac.uk/356385/2/WRR_2012.pdf
16. Shaw, J. et al. (2021). LISFLOOD-FP 8.0: the new discontinuous Galerkin shallow-water solver for multi-core CPUs and GPUs. *GMD* 14, 3577–3602. https://gmd.copernicus.org/articles/14/3577/2021/
17. Neal, J., Schumann, G., Bates, P. (2012). A subgrid channel model for simulating river hydraulics and floodplain inundation over large and data sparse areas. *WRR* 48, W11506. https://research-information.bris.ac.uk/en/publications/a-subgrid-channel-model-for-simulating-river-hydraulics-and-flood/
18. Ozdemir, H., Sampson, C. C., de Almeida, G. A. M., Bates, P. D. (2013). Evaluating scale and roughness effects in urban flood modelling using terrestrial LIDAR data. *HESS* 17, 4015–4030. https://hess.copernicus.org/articles/17/4015/2013/hess-17-4015-2013.html
19. Smith, G. P., Davey, E. K., Cox, R. J. (2014). Flood hazard. WRL Technical Report 2014/07 (ARR Project 10 basis; includes Shand et al. 2011 vehicle criteria). https://knowledge.aidr.org.au/media/2334/wrl-flood-hazard-techinical-report-september-2014.pdf
20. Martínez-Gomariz, E., Gómez, M., Russo, B., Djordjević, S. (2018). Stability criteria for flooded vehicles: a state-of-the-art review. *J. Flood Risk Manag.* 11, S817–S826. https://doi.org/10.1111/jfr3.12262 (open copy: https://zaguan.unizar.es/record/75630/files/texto_completo.pdf)
21. Kramer, M., Terheiden, K., Wieprecht, S. (2016). Safety criteria for the trafficability of inundated roads in urban floodings. *IJDRR* 17, 77–84. https://doi.org/10.1016/j.ijdrr.2016.04.003
22. Martínez-Gomariz, E., Gómez, M., Russo, B. (2016). Experimental study of the stability of pedestrians exposed to urban pluvial flooding. *Nat. Hazards* 82, 1259–1278. https://ideas.repec.org/a/spr/nathaz/v82y2016i2d10.1007_s11069-016-2242-z.html
23. Pregnolato, M., Ford, A., Wilkinson, S. M., Dawson, R. J. (2017). The impact of flooding on road transport: a depth-disruption function. *Transp. Res. D* 55, 67–81. https://doi.org/10.1016/j.trd.2017.06.020
24. Kilgore, R. T., Cotton, G. K. (2005). *Design of Roadside Channels with Flexible Linings*, HEC-15, 3rd ed., FHWA-IF-05-114.
25. Anderson, I., Rizzo, D. M., Huston, D. R., Dewoolkar, M. M. (2017). Stream power application for bridge-damage probability mapping based on empirical evidence from Tropical Storm Irene. *J. Bridge Eng.* 22(5). https://ascelibrary.com/doi/10.1061/%28ASCE%29BE.1943-5592.0001022
26. NCHRP Synthesis 496 (2016). *Minimizing Roadway Embankment Damage from Flooding*. TRB. https://nap.nationalacademies.org/read/23604/chapter/3
27. Burges, C. J. C. (2010). From RankNet to LambdaRank to LambdaMART: an overview. Microsoft Research MSR-TR-2010-82.
28. Bekker, J., Davis, J. (2020). Learning from positive and unlabeled data: a survey. *Machine Learning* 109, 719–760. https://doi.org/10.1007/s10994-020-05877-5
29. Li, W. et al. (2022). A positive-unlabeled learning algorithm for urban flood susceptibility modeling. *Land* 11, 1971. https://www.mdpi.com/2073-445X/11/11/1971/htm
30. Auer, A. et al. (2024). A data-centric perspective on the information needed for hydrological uncertainty predictions (conformal prediction). *HESS* 28, 4099–4126. https://hess.copernicus.org/articles/28/4099/2024/
31. Conformal methods for quantifying uncertainty in spatiotemporal data: a survey. arXiv:2209.03580. https://arxiv.org/pdf/2209.03580
32. Roberts, D. R. et al. (2017). Cross-validation strategies for data with temporal, spatial, hierarchical, or phylogenetic structure. *Ecography* 40, 913–929. https://www.biometrie.uni-freiburg.de/mitarbeiter/dormann/roberts-et-al-2017-ecography.pdf
33. Asif, M., Bentivoglio, R., Albano, R. (2026). CNN model for rapid prediction of urban flash flood water depth and velocity maps. *J. Hydrol.* 675, 135601. https://repository.tudelft.nl/record/uuid:8898c07c-8ea4-40f1-8da4-6ec2534bb52c
34. Bentivoglio, R. et al. (2025). Multi-scale hydraulic graph neural networks for flood modelling (mSWE-GNN). *NHESS* 25, 335. https://nhess.copernicus.org/articles/25/335/2025/
35. Annis, A., Nardi, F., Castelli, F. (2022). Simultaneous assimilation of water levels from river gauges and satellite flood maps for near-real-time flood mapping. *HESS* 26, 1019–1041. https://hess.copernicus.org/articles/26/1019/2022/
36. MassDOT, Highway data for developers (roadway events XML, GoTime API, WZDx work zones). https://www.mass.gov/info-details/highway-data-for-developers
37. Safaei-Moghadam, A., Tarboton, D., Minsker, B. (2023). Estimating the likelihood of roadway pluvial flood based on crowdsourced traffic data and depression-based DEM analysis. *NHESS* 23, 1–19. https://nhess.copernicus.org/articles/23/1/2023/
38. Assessing trustworthiness of crowdsourced flood incident reports using Waze data: a Norfolk, Virginia case study. *Transp. Res. Rec.* https://par.nsf.gov/biblio/10291591
39. Roberts, N. M., Lean, H. W. (2008). Scale-selective verification of rainfall accumulations from high-resolution forecasts of convective events. *MWR* 136, 78–97. https://doi.org/10.1175/2007MWR2123.1
