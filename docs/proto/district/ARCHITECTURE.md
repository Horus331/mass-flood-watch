# District-scale Mass Flood Watch: recommended architecture

Written 1 Nov 2026. Scope: all of MassDOT District 3 (73 towns, box 128000,856000 to 206000,946000 in EPSG:26986, 78 × 90 km,
3900 × 4500 = **17.55 M cells at 20 m**), for storm replays and the live forecast, with a path to the other districts. The aim is a
product an agency can rely on, not a demo. Numbers marked **(measured)** come from runs in this repo. **(published)** means a cited
paper or document. **(estimate)** means it is worked out here and still needs measuring. Anything uncertain is marked as such.

## 0. Recommendations in brief

1. **Solver: keep LISFLOOD-FP 8.2 (acceleration solver, CUDA) and run District 3 as one 20 m domain on one GPU.** It already works:
   22.7 min of solver time for 48 h of the Sept 2023 storm (`turing/d3_sep2023_p`) and 29 min for a 54 h HRRR forecast. Splitting the
   district into tiles would add seams and boundary conditions without a speed benefit. Multi-GPU solvers (TRITON, RIM2D, HiPIMS)
   matter only for 10 m statewide or finer grids.
2. **Resolution: solve at 20 m and add street-level detail in two ways.** (a) 10 m nested runs on watersheds (HUC10/HUC12, cut at
   divides) where the 20 m run puts roads near the 30 cm threshold. (b) In the viewer, downscale the water surface onto a 1–3 m lidar
   terrain near roads. The 20 m road-segment result stays the official answer; the downscaled picture is labelled as a visualisation.
3. **Forecast: one Slurm job holding several GPUs runs the 8 HRRR members** (Turing allows only about 4 submitted jobs per user). Start
   each member from a warm state (a radar-driven analysis run plus LISFLOOD-FP checkpoint/`startfile`). The current latency is roughly
   cycle + 3.5–4.5 h for the full ensemble; the deterministic member can be out about 1 h earlier. Most of the time goes to HRRR
   availability, Slurm queue wait and the Python post-processing (17–29 min per district run today, longer than the solver).
4. **Data: stream tiles in the model's own grid (EPSG:26986), not Web-Mercator reprojections.** Use 256 × 256 cell tiles (5.12 km at
   20 m), 5 overview levels (20 → 320 m, built by max-pooling), 10-minute frames grouped into 2-hour chunks, and depth stored as 1 byte
   per cell (1 cm steps to 1 m, 5 cm steps above). Permanent water is left out. From the Sept 2023 District 3 peak-depth grid, this is
   **≤ 0.8 MB per frame for the whole pyramid**, so **≤ 220 MB per 48 h storm** (upper bound; probably 70–150 MB).
5. **Hosting: Cloudflare R2 behind a custom domain for the large data** (no egress fees, CORS and range requests supported; about $0 to
   a few $/month at this scale). GitHub Pages keeps only the app. Hugging Face stays the archive and staging store. As of Jan 2026,
   browser range requests on HF `resolve` URLs failed CORS preflight, and anonymous downloads are capped at 3,000 per 5 min per IP. Zenodo
   gets DOIs for frozen validation packs.
6. **Agency-grade means a few concrete things.** A published verification record (segment POD/FAR/CSI, ensemble reliability), an
   on-time and latency record, fallbacks with a visible staleness banner, and outputs agencies can load directly: GeoJSON/CSV segment feed
   with time fields, Web-Mercator XYZ tiles and COGs of peak depth and closure probability, and CAP 1.2 alerts. Also needed: a model card
   and an operations manual. Before any of this is advertised, the known district over-forecast (`forecast/DISTRICT.md`: 3.2× the radar
   run's flagged segments) has to be fixed.

## 1. Starting point (measured, this repo)

| Run | Cells | Solver time | Total job time | Notes |
| --- | --- | --- | --- | --- |
| District 3, Sept 2023, 48 h, default step (`d3_sep2023_20m`) | 17.55 M | 994 s | 2,144 s | 1 GPU, Turing |
| District 3, Sept 2023, 48 h, parity (dt ≤ 1 s) (`d3_sep2023_p`) | 17.55 M | 1,364 s | 3,111 s | live settings |
| District 3, HRRR 18z hindcast, 54 h (`hindcast_d3_sep2023_18z`) | 17.55 M | 1,755 s | 2,776 s | forecast set-up |
| Leominster box, 20 m, 48 h | 1.0 M | 45–146 s | 150–850 s | GPU mostly idle at this size |
| Leominster box, 10 m, 48 h | 4.0 M | 678 s | 1,051 s | 10 m ≈ 4.6–8× the 20 m cost |
| Same box on 4 CPU cores (GitHub Actions) | 1.0 M | 27–45 min | — | `COMPUTE.md` |

- **GPU vs CPU throughput.** The GPU does about 1.6 s per M cells per simulated hour (1,364 s / (17.55 M × 48 h)). The 4-core CPU does
  46–75 s, so the GPU is about 30–45× faster.
- **Post-processing is the larger cost.** It takes 17–29 min per district run (total minus solver), against 17–29 min for the solver.
- **The peak wet area is small.** Land wet ≥ 30 cm is 14 km², or 0.2 % of the district (`hmax_stats.json`). Cells ≥ 3 cm are 5.8 %
  including permanent water and 2.0 % on land only (computed here from `hmax_cm.npz`).
- **The current viewer cannot scale to 20 m.** The District 3 replay is downsampled to 80 m (975 × 1125, 97 half-hour frames, 9.7 MB).
  `viewer.js` decodes every frame into GPU textures up front, which works at 80 m but not at 20 m across the district.
- **Code facts checked in the LISFLOOD-FP 8.2 source.**
  - The CUDA acceleration solver has checkpoint/restart (`write_checkpoint` / `read_checkpoint` in `cuda/acc/cuda_acc_simulate.cu`).
    The checkpoint interval is in hours of wall-clock time.
  - The default build is double precision (`_NUMERIC_MODE=1`).
  - The CUDA code has no multi-GPU or MPI path.

## 2. Compute

### 2.1 Solver options

| Solver | Equations / GPU | Published performance near our size | Fit for us |
| --- | --- | --- | --- |
| **LISFLOOD-FP 8.2 ACC (current)** | Local inertial; single GPU, CUDA; also DG2/FV1 and multiwavelet adaptive solvers (8.1/8.2) | GPU 2–28× faster than its CPU version, with the gain growing with element count (Sharifian et al. 2023, RTX 2070S). **Ours: 17.55 M cells, 48 h, 23 min on 1 GPU.** | Validated here (parity, hindcasts). Stay. |
| RIM2D (GFZ) | Local inertial; CUDA, multi-GPU | Berlin, 891.8 km², **10 m = 16.7 M cells, 48 h event: 16 min on 1 A100, ~8 min on 8 A100**. 5 m (67 M): 116 min on 1, 34 min on 8. 2 m (419 M): 5.5 h on 8 (Khosh Bin Ghomash et al. 2026) | Same physics family, similar speed. Code on request, EUPL-1.2 (fees for commercial use). Good as a second-model check, not a replacement. |
| TRITON (ORNL) | Full SWE, Roe solver; MPI + multi-GPU | "Promising runtimes"; communication and I/O limit scaling (Morales-Hernández et al. 2021). Harvey 10-day run: one GPU node beat 64 CPU nodes (press coverage, no cell counts) | Option if we need full SWE or multi-GPU statewide at 10 m. Revalidation cost. |
| HiPIMS (Loughborough/Newcastle) | Full SWE; multi-GPU | Eden catchment 2,500 km² at 10 m (~25 M cells): 36 h NWP forecast run in **1.75 h** (Met Office/UK case study; GPU count not stated) | Proven operational demo; heavier per cell than local inertial. |
| SFINCS (Deltares) | Linear/local inertial + subgrid; GPU via OpenACC | Subgrid: about 35–50× speed-up for equal accuracy (van Ormondt et al. 2025, CPU). Docs: GPU Docker build "not fully functional", contact Deltares | Subgrid idea is attractive (§2.3). GPU build not public-ready. |
| HEC-RAS 2D | Full SWE / diffusion wave; CPU | No GPU solver in the releases I could verify (**uncertain**; check HEC's current release notes) | Familiar to DOT engineers; useful for site checks, not district ensembles. |
| ANUGA, Iber+ | Full SWE; Iber+ CUDA | Iber+ reports large GPU speed-ups (García-Feal et al. 2018); no comparable district numbers found | No reason to switch. |

**Decision.** At 17.55 M cells the model fits on one GPU and takes about as long as the RIM2D figure published for a 16.7 M-cell city
(16 min, 1 A100). That is the speed class operational groups report. A solver change would reset the validation record (parity, OOS-7,
hindcasts) without gaining speed. Revisit it only when going 10 m statewide (about 270 M cells), for which none of the single-GPU
options suffice.

**GPU type matters (estimate, check).** The build is FP64, and its arch list includes L40S and RTX Pro 6000, which have weak FP64. A100,
H100 and H200 are the safe partitions. Benchmark the same District 3 run on each Turing GPU type (Phase 0). If the gap is large, test a
`_NUMERIC_MODE=0` (float) build against the parity baseline. Elevations of 100–400 m in float32 resolve to about 3 × 10⁻⁵ m, which is
probably fine, but the parity check must confirm it.

**Memory (estimate).** The ACC CUDA state is about 10–15 double arrays per cell (H, Qx, Qy, maxH, time-of-max arrays, DEM, Manning,
rain), so about 100–150 B/cell:

| Grid | Cells | Estimated GPU memory |
| --- | --- | --- |
| District 3, 20 m | 17.6 M | 2–3 GB |
| District 3, 10 m | 70 M | 7–11 GB |
| Massachusetts, 20 m | about 70 M | 7–11 GB |

All fit on a 40–80 GB card. Measure with `nvidia-smi --query-gpu=memory.used` during a run.

### 2.2 One domain, tiles, or watersheds?

- **District at 20 m: one rectangular domain.** It fits one GPU and leaves no internal boundaries to handle. Free outflow on the box edges
  is the existing set-up. The only error source is flow entering from outside the box (Nashua, Blackstone and Quinebaug start partly
  outside District 3). Those headwaters are small next to the storm runoff for flash floods, and USGS inflow hydrographs can be added as
  boundary inflows where they matter.
- **Not overlapping rectangular tiles.** Overlap halos with discarded margins still leak flow across tile edges and need a nesting
  scheme. Our domains are small enough not to need them.
- **10 m nests and other districts: watershed domains** (`LF_DOMAIN=basin`, already built: `domain_d3_hu8_*`). Watersheds cut at divides
  need only an outlet boundary and, for nests, an inflow hydrograph taken from the 20 m parent run at the nest's upstream edge.
  - District 3 by HU8 basins at 10 m: 84.7 M active cells in total, the largest basin 19.2 M (`COMPUTE.md`).
  - Expected cost at 10 m: about 1.7–3 h on one GPU for the whole district, scaled from the measured 4.6–8× cost of 10 m vs 20 m.
- **Other districts.** Each district gets one 20 m job of 15–25 M cells, or HU8 basin jobs. Massachusetts at 20 m (~27,000 km² box,
  about 68 M cells) would fit one 80 GB GPU at about 1.5–2 h per 48 h storm (estimate). That is too slow for an 8-member forecast on
  shared hardware, so run districts as separate parallel jobs.

### 2.3 Resolution

- **20 m for every district run** (replays and forecast). 10 m costs 4.6–8× more (measured).
- **10 m for validation and hotspots.** That means the storm catalogue for checks against high-water marks, plus nests where the 20 m
  ensemble puts segments between about 10 and 60 cm.
- **Agencies use finer grids for static maps.** England's surface-water risk map uses a 2 m terrain grid with 1 km rain, but says the
  map is not for individual properties and that surface-water warnings are not issued because rain timing is too uncertain (EA/gov.uk).
  For a rain-forecast-driven product, forecast skill is limited by rain placement (our `DISTRICT.md`, `GATE.md`), not by grid size. That
  argues for spending GPU time on ensemble members before resolution.
- **Subgrid as a later research option.** SFINCS-style subgrid tables at 40–50 m could match 10–20 m accuracy at much lower cost
  (published 35–50×). This would need LISFLOOD-FP's subgrid channel mode or a solver change, so it is a research item, not Phase 1.

### 2.4 Ensemble on Turing (job-cap aware)

- **The constraint.** About 4 submitted jobs per user (`QOSMaxSubmitJobPerUserLimit`), and the queue runner takes one of them. Its 30 min
  tick adds up to 30 min of latency.
- **Recommendation: one forecast job per cycle that asks for several GPUs on one node** (`--gres=gpu:4`, **check** the partition allows
  it) and runs members in parallel, 2 per GPU in sequence, so 8 members take about 2 × 29 min ≈ 1 h. If multi-GPU jobs are not allowed,
  run 2 jobs × 4 members using `run_plan_gpu.slurm`'s task loop. Array tasks probably count against the submit cap one by one
  (**uncertain**; test).
- **Order members newest first:** T, then T-1h … T-4h, then T-6h … T-18h. Publish the deterministic member as soon as it finishes,
  then refresh the probabilities as members arrive (2 of 8 rule, `ENSEMBLE.md`).
- **Ensemble cost per fired cycle:** 8 × 1,755 s ≈ **3.9 GPU-h**.
  - The gate fired on 33 of 122 days in the record-wet summer of 2023, so assume 40–80 fired days a year (estimate).
  - Every fired cycle: about **620–1,250 GPU-h/yr**.
  - Two ensemble cycles per fired day, deterministic member on the others: about **350–700 GPU-h/yr**.
  - Recommended policy: run the ensemble on 00z and 12z (plus any cycle with gate score ≥ 1.5×), and the deterministic member every
    fired cycle.
- **Cloud fallback.** A100-class GPUs rent for roughly $1.5–4 per GPU-hour (**approximate**; check current prices), so one fired cycle
  costs about $6–16. Keep a container image (Apptainer/Docker) of the CUDA build so the job runs unchanged on a rented GPU when Turing is
  down.

### 2.5 Warm start and checkpoint

- **A cold start loses antecedent water.** Today each run starts dry, apart from base flow and the channels.
- **Proposed.** While the gate is armed, run an hourly **analysis run** that drives the district with MRMS to "now" (roughly a minute or
  two of GPU time per simulated hour, estimate). It ends with a LISFLOOD-FP checkpoint or a depth `startfile` (both supported; the CUDA
  ACC source has `read_checkpoint`/`write_checkpoint`). Forecast members start from it. NWM's analysis-and-assimilation cycle is the
  model for this.
- **Long replays and 10 m runs.** Turn on `checkpoint` with `checkfreq` of about 0.5 h so pre-emption or a time limit does not lose the
  run.

## 3. Pipeline and operations

### 3.1 Forecast cycle: latency budget (00/06/12/18z cycles)

| Step | Now | Target |
| --- | --- | --- |
| HRRR 48 h cycle available | T + 1:45 (`GATE.md`) | same (outside our control) |
| Gate on GitHub Actions | about 5–10 min | same |
| Request reaches Turing (git queue tick) | 0–30 min | ≤ 5 min: shorten `TICK_MIN` while the gate is armed, or pre-queue the forecast job with `--begin` |
| Slurm queue wait | **unknown**: measure with `sacct` | report it as a monitored metric |
| Input staging (HRRR members, static inputs cached) | about 5–10 min | ≤ 5 min (static layers pre-staged) |
| Solver | 29 min per member | deterministic 29 min; 8 members ≈ 60 min on 4 GPUs |
| Post-processing (closures, scores, packs) | 17–29 min | ≤ 10 min (parallel tiling; only the forecast products) |
| Upload to R2 + status JSON | — | ≤ 5 min |
| **Total** | about T + 3:30 to 4:30 (estimate) | deterministic **≈ T + 2:45**, ensemble **≈ T + 3:45** |

**For comparison**, NOAA's FIM services publish with latencies of about 45 min (NWM analysis), 15–45 min (RFC forecasts) and 6.5 h
(NBM 5-day). An HRRR-driven 2D model at T + 3–4 h is in line with the slower of those. Lead time is the real limit: storms starting
within about 3 h of a cycle are in practice forecast by the previous cycle (`GATE.md`).

### 3.2 Reliability (what agencies expect)

- **Status and freshness.**
  - Every cycle writes `status.json` (cycle, members done, time of each step, solver version, git SHA).
  - The viewer shows a **staleness banner** when the newest product is more than 7 h old.
  - Report the on-time rate monthly. The UK Flood Forecasting Centre, for example, reports 99.8 % of its Flood Guidance Statements issued
    on time.
- **Fallback chain**, so something is always published and labelled with its source:
  1. Turing district ensemble.
  2. Turing deterministic member.
  3. GitHub Actions 20 × 20 km boxes (the existing CPU path).
  4. Rain-only gate outlook.
  5. "Model not run this cycle".
- **Monitoring.** A watchdog Action every 30 min checks that `status.json` is fresh. When it is stale or a step fails, it opens a GitHub
  issue or sends an e-mail.
  - Track queue wait, solver time, post-processing time and mass-balance error per run.
  - Track the share of members finished by the deadline.
- **Reproducibility.** Pin the code commit per cycle (as `run_plan_gpu.slurm` does). Archive the inputs (HRRR subset, MRMS) and outputs of
  every fired cycle to HF, so any forecast can be re-run exactly.
- **Turing has no SLA.** Before agencies depend on the forecast, write down maintenance windows, the allocation owner (Prof. Tao's group)
  and the cloud fallback.

### 3.3 Verification program (the credibility core)

- **Segment level.** POD, FAR, CSI and frequency bias for closure (P ≥ 0.5) against MassDOT incident and closure logs, Waze jams and
  closures, 311 and news reports. Use a stated spatial tolerance (the 100–200 m used now) and stated time windows. Report by lead time,
  by storm type (convective vs synoptic) and by road class.
- **Ensemble.** Brier score, a reliability diagram and ROC for P(closure) at 1 of 8, 2 of 8 and so on, pooled over fired cycles. Keep
  pre-registration (`PROTOCOL.md`) for any setting change.
- **Physics checks.** USGS gauge stage and peak timing at the 20–30 District 3 gauges, and high-water marks where they exist (10 m
  runs).
- **Operational record.** Publish a rolling verification page updated after every event. The UK FFC reports surface-water POD by lead
  time over 1-year and 36-month windows, and publishes poor scores too (48 % POD over 36 months, rated Red). That openness is what
  agencies trust.
- **Open item before district launch:** the district-wide over-forecast (`DISTRICT.md`, 888 vs 276 segments). It comes from the 90th
  percentile rain spreading. Two options:
  1. Apply neighbourhood or percentile treatment to the **impact** (segment probability) instead of inflating the rain.
  2. Use a district-specific spreading setting, scored on the storm catalogue.

  Pre-register the choice before scoring.

### 3.4 What comparable systems do

| System | What it predicts | Model / cadence | Delivery |
| --- | --- | --- | --- |
| NWS/NSSL **FLASH** | Flash-flood unit streamflow | CREST, 1 km, 10 min, MRMS-forced; EF5 ensemble framework; at NCEP since 2016 | NWS operations |
| NOAA **FIM services** | River inundation extent | HAND on NWM/RFC flows; hourly and 6-hourly | water.noaa.gov, NWS GIS viewer |
| **Google Flood Hub, flash floods** (Mar 2026) | Urban flash-flood likelihood, up to 24 h | ML trained on news-report archives; weaker in rural areas | Flood Hub web |
| **UK FFC** surface water | County-scale surface-water risk, day 1–5 | Rain ensembles + hazard-impact lookups; verification published | Flood Guidance Statement |
| **HiPIMS** (UK demo) | 10 m inundation, 2,500 km² | Full SWE, multi-GPU; 36 h forecast in 1.75 h | Research to DAFNI |
| **RIM2D** Berlin | City-wide pluvial inundation, 10 m to 2 m | Local inertial, 1–8 A100; 10 m 48 h in 8–16 min | Research, aimed at operations |
| **NC FIMAN-T** (NCDOT + NCEM) | Inundation depth at roads and bridges, bridge freeboard | Gauge-driven; LiDAR road elevations | Web dashboards, PDF export |
| **TxDOT FAST** (UT Austin, USGS, KISTERS) | Flooded roads, bridges, culverts by maintenance section | Forecast discharge and water surface; bridge radar gauges | Overlaid web maps |
| **Iowa DOT BridgeWatch / IFC** | Bridge flood warnings, extending to ungauged bridges | Streamflow forecasts + IFC sensors | DOT platform |
| **Hampton Roads (HRPDC)** | Observed road flooding | 45 roadside water-level sensors (2026) | Dashboard + feeds to Waze |
| **VIMS street-level model** (Virginia) | Coastal street flooding, 36 h ahead | Hourly flood rasters in storms | ArcGIS time-aware layers and Web 3D |

**Take-away.** DOT tools are mostly river- or gauge-driven and show results on dashboards keyed to assets: segments, bridges, culverts,
maintenance sections. A rain-driven 2D road-closure ensemble over a whole district would be unusual. That is a selling point, but it also
means verification has to carry the case for adoption.

### 3.5 What to hand agencies

1. **Segment feed (primary).**
   - Content: `segments_<cycle>.geojson` plus `.csv`, with segment id (MassDOT route/segment keys), P(closure), peak depth, time water
     first reaches 30 cm, duration, and why (culvert, sag, stream).
   - Updated every cycle at a stable URL.
   - ArcGIS Online adds GeoJSON and CSV layers by URL. For a hosted feature layer, MassDOT's GIS team can schedule a pull.
   - Optionally a Waze CIFS closure feed for "likely closed" segments, but **only** after a verification season and with MassDOT's
     agreement.
2. **Raster products.**
   - **COG (EPSG:26986)** of peak depth and of P(depth ≥ 30 cm) per cycle and per replay, for GIS analysts.
   - **XYZ Web-Mercator PNG tiles** of the same, because ArcGIS Online tile layers must be Web Mercator `{z}/{x}/{y}`.
   - WMS/WMTS needs a server (GeoServer/TiTiler), so it is a Phase 5 option if an agency asks for it.
3. **Alerts.** CAP 1.2 XML per cycle for towns or segments over the 2 of 8 threshold, with polygons. These are static files plus an
   Atom index. Treat them as **advisory**: IPAWS distribution needs an authorised alerting authority, which we are not.
4. **Documents.**
   - A model card: inputs, physics, thresholds, known biases (HRRR displacement, culverts, no storm drains on GPU).
   - The verification report (§3.3) and an operations manual (cycle, fallbacks, contacts).
   - A data dictionary (`docs/proto/arcgis/FIELDS.csv` is a start) and licence and attribution terms (OSM ODbL, MassGIS, MassDOT).

## 4. Data delivery

### 4.1 Measured sizes (Sept 2023, District 3, 20 m)

Computed here from `docs/proto/turing/d3_sep2023_p/hmax_cm.npz`, the peak over the storm, which bounds any single frame from above:

| Encoding of the peak-depth grid (cells ≥ 3 cm, permanent water left out) | Size |
| --- | --- |
| 288 tiles (256 × 256 cells), uint8 depth code, WebP lossless | 0.39 MB |
| Same, PNG | 0.56 MB |
| Overviews 40 / 80 / 160 / 320 m (max-pooled), WebP lossless | 0.20 / 0.10 / 0.05 / 0.02 MB |
| **Whole pyramid, one frame (upper bound)** | **≈ 0.77 MB** |
| Same, with permanent water included | 0.96 MB at native resolution alone (2.16 M water-mask cells) |

**Every 5 km tile has some wet cell (streams), so dropping empty tiles saves nothing at this tile size.** The savings come from
compression and from leaving out permanent water.

### 4.2 Recommended scheme

- **Grid.** The model's grid in EPSG:26986, no reprojection. Cells stay exact and line up with the closure computation. The custom WebGL
  layer already places quads by projecting the tile corners.
- **Tiles.** 256 × 256 cells:

  | Level | Cell size | Tile size | Tiles |
  | --- | --- | --- | --- |
  | L0 | 20 m | 5.12 km | 16 × 18 = 288 |
  | L1 | 40 m | | 72 |
  | L2 | 80 m | | 18 |
  | L3 | 160 m | | 6 |
  | L4 | 320 m | | 2 |

  Overviews use **max-pooling**, so a flooded road cell does not vanish at district zoom.
- **Depth code (uint8).** 0 means dry (< 3 cm). 1–100 is depth in cm, so the 30 cm threshold is exact. 101–255 is 1 m + 5 cm × (code −
  100), up to about 8.8 m. Velocity stays out of the tiles; the flow layer only for 5-min hotspot runs.
- **Frames.** 10 min, with time interpolation in the shader as now: 288 frames for 48 h and 324 for a 54 h forecast. The 30 min frames
  used for 80 m now are too coarse for watching water reach a road.
- **Time chunks.** 12 frames (2 h) per file, `L/x_y/c###.u8.gz`: the 12 frames of uint8 rows, gzip-compressed.
  - The browser decompresses with the built-in `DecompressionStream('gzip')` and uploads to one R8 `TEXTURE_2D_ARRAY` layer per frame.
  - Each file is about 15–40 KB, and about 9,300 files per storm.
  - Alternative: 4 frames in the RGBA channels of a WebP lossless image, decoded with `createImageBitmap`, about 10–15 % smaller (§4.1).
  - Trying delta-coding frames within a chunk is worthwhile, because water changes slowly; the saving is **unmeasured**.
- **Container.** Plain files work on any static host, HF included. On R2 the chunks can later be bundled one PMTiles archive per level
  and chunk, used purely as a range-addressable container with custom tile semantics, to cut the object count to about 120 per storm.
- **Static layers, once per district.**
  - 20 m model terrain, 16-bit, about 10–20 MB.
  - Permanent-water mask.
  - Road segments as vector tiles (PMTiles/MVT) with ids. The current `segments.geojson` is 5.8 MB.
  - Optional high-resolution terrain near roads for downscaling (§5): 2–3 m, 16-bit, only within about 100 m of roads, **estimated
    0.3–0.8 GB**. Measure it, and load it only at street zoom.
- **Segment time series.** One binary per run (segment-major, uint8 depth in cm per frame, sparse), about 1–3 MB for 45,099 segments ×
  288 frames (estimate). Road colours come from this file, not from raster sampling.
- **Manifest.** `manifest.json` per run: grid, levels, frame times, chunk length, code table, model version, git SHA, run status.

### 4.3 Expected totals

| Product | Size (estimate; upper bound from §4.1) |
| --- | --- |
| Storm replay, 48 h, 10 min frames, full pyramid | ≤ 220 MB (likely 70–150 MB) |
| Forecast cycle: deterministic member animated (54 h) + P(≥ 30 cm) every 3 h + 8-member segment probabilities | ≈ 100–250 MB |
| Rolling forecast archive online (last 8 cycles) | ≈ 1–2 GB; older cycles move to HF |
| 15-storm District 3 catalogue | ≈ 1.5–3 GB |

### 4.4 Browser and phone budget

- **Phones run out of memory.** iOS Safari kills tabs at roughly 1–1.5 GB in community reports (**uncertain**, device-dependent). Plan
  for **≤ 256 MB of GPU textures on phones** and about 1 GB on desktop.
- **Never decode a whole storm.** Keep only the tiles in view at the current level, for the current time chunk ± 1. A phone screen at
  street zoom shows about 50 tiles: 50 × 36 frames × 64 KB ≈ 115 MB. District overview (L3/L4) for the whole storm is under 10 MB.
- **Prefetch and evict.** Prefetch the next chunk while playing, and evict least-recently-used chunks. On a phone, fall back to 30 min
  frames when the network is slow.

### 4.5 Hosting

| Host | Limits that matter | Verdict |
| --- | --- | --- |
| GitHub Pages | Published site ≤ 1 GB; 100 GB/month soft bandwidth; 10 min deploy timeout | App shell and small JSON only. **Note:** `git ls-files docs` already totals 2.56 GB, over the 1 GB published-site limit. Check what Pages actually serves and move run data out. |
| **Cloudflare R2** | $0.015/GB-month, $0.36 per million reads, no egress fee; free 10 GB and 10 M reads per month. `r2.dev` is rate-limited and for development only; production needs a custom domain on Cloudflare. CORS rules allow GET/HEAD and Range | **Primary data host.** 20 GB costs about $0.15/month plus reads. Free tier: 10 M reads ≈ 5,000–20,000 viewer sessions a month. |
| Hugging Face dataset | Free public storage, best effort; ≤ 10k files per folder; ≤ 100k files per repo; ≤ 50 GB per file. Anonymous `/resolve/` limit **3,000 per 5 min per IP**. Browser **Range + CORS** through the Xet bridge failed preflight (forum and issue, Jan 2026; fix status unclear) | **Archive and Turing staging** (as now). Not for live tile serving. I could not test it from here (the sandbox proxy blocks huggingface.co). Run a browser test with `fetch(url, {headers: {Range: 'bytes=0-99'}})` from horus331.github.io before relying on it. |
| Zenodo | 50 GB and 100 files per record (one-time increase to 200 GB) | DOIs for frozen validation packs and papers. |
| Agency-hosted (MassGIS/MassDOT ArcGIS) | Their terms | Phase 5, if adopted. |

## 5. Viewer

- **Overview to detail.** Open on the district at L3/L4 with the storm's rain (MRMS/HRRR) and roads coloured by state. Zooming in loads
  L2 → L0 tiles for the current time. Above street zoom, show closures as segments plus a per-town summary; draw the depth raster
  underneath.
- **Street level ("where water meets the road").**
  - Render the 20 m water surface (model terrain + depth, interpolated only between wet cells) minus a 2–3 m lidar terrain near roads,
    computed in the shader.
  - Wet/dry edges then follow curbs and road crowns. Valid where water is ponded or slow; less so on steep flow paths.
  - Label it "downscaled view of the 20 m model". The segment's state (from the 20 m model with road-crest elevations) stays
    authoritative.
  - Where a 10 m nest exists, show it instead.
- **Time.**
  - A scrubber with the rain hyetograph and a closed-segment count curve behind it (`cascade.json` already has `closed_n`).
  - Chunk-aware playback speed, and keyboard steps of 10 min, 1 h and 6 h.
  - For forecasts: a member selector and "probability" vs "one member" modes.
- **Tours.**
  - JSON keyframes (camera, time range, caption) built automatically from the run: the first closure, the largest cluster, the longest
    closure, hospital access losses. Allow hand edits.
  - Follow the existing six-scene story, but over the district. Prefetch the next stop's tiles and chunk during the current stop.
- **Shareable state.** The URL hash holds run, time, centre, zoom and layer, so an engineer can send "Route 2, Leominster, 21:30".
- **Accessible equivalent.** A sortable table of closed segments synced to the time slider, and CSV download.
- **Examples to borrow from.**
  - NWS GIS viewer / water.noaa.gov: layers and a time list.
  - Esri time-aware layers and time slider (the VIMS street-level forecast used them).
  - CarbonPlan and Development Seed client-side raster rendering (zarr-layer, deck.gl-raster), for the tile-streaming pattern.

## 6. Phased plan

| Phase | Work | Exit criteria |
| --- | --- | --- |
| **0. Measure (1–2 weeks)** | District 3 benchmark on each Turing GPU type (A100/H100 vs L40S); GPU memory per cell; Slurm queue-wait statistics; whether multi-GPU jobs and arrays work under the submit cap; browser test of HF Range/CORS; set up R2 with a custom domain and CORS | Table of runtime, memory and wait per partition; hosting decision confirmed |
| **1. District replay at 20 m (3–4 weeks)** | Re-run `d3_sep2023_p` with 10 min frames (`LF_SAVEINT=600`); write the tiler (§4.2) and the segment series; upload to R2; streaming viewer layer with LOD, chunks, eviction and the phone budget | Sept 2023 District 3 plays smoothly on a mid-range phone and a laptop; ≤ 250 MB per storm; first frame shown in < 3 s on 4G |
| **2. Catalogue and credibility (4–6 weeks, mostly GPU time)** | All about 15 District 3 storms at 20 m (≈ 0.4 GPU-h each); 10 m nests in 2–3 hotspot basins; district verification report (§3.3); fix and pre-register the district rain treatment | Published verification page; over-forecast ratio within ±30 % of radar on the catalogue |
| **3. Operational forecast, shadow mode (one warm season)** | Armed-gate fast queue; multi-GPU ensemble job; warm start from MRMS analysis; post-processing ≤ 10 min; `status.json`, watchdog, fallback chain; container for cloud fallback | ≥ 95 % of fired cycles published by T + 4 h; latency and verification logged per cycle |
| **4. Agency package** | Segment GeoJSON/CSV feed, COG and XYZ products, CAP files, model card, operations manual; test with MassDOT District 3 GIS / operations staff | MassDOT can load the feed in ArcGIS; written feedback |
| **5. Expansion** | Other districts as separate 20 m jobs or HU8 basin jobs; capacity plan (Turing allocation vs cloud); WMS/WMTS server only if requested | Per-district verification before each goes public |

## 7. Risks

| Risk | Effect | Mitigation |
| --- | --- | --- |
| Turing is shared, has no SLA, a ~4-job cap, and queue waits | Late or missing forecasts | Measure waits; one multi-GPU job per cycle; fallback chain; cloud container; ask Research Computing about a reservation or priority for the storm season |
| HRRR misplaces convective rain | Misses and false alarms | Time-lagged ensemble; publish probabilities, not single runs; verify by lead time |
| District over-forecast from the 90th percentile rain spreading (3.2×) | Loss of credibility | Fix in Phase 2 with a pre-registered setting before launch |
| The closure probability is an uncalibrated physics prior (Φ((d − 0.30)/0.10), per the run report); no storm drains on the GPU | Over-flagging in drained urban streets | Calibrate on catalogue labels; document it; drains as a CPU or patched-CUDA research item |
| Post-processing in single-threaded Python | Latency | Parallelise; produce only the forecast products in the critical path |
| FP64 on weak-FP64 GPUs | Slow runs on L40S / RTX Pro | Pin to A100/H100 partitions; test a float build |
| Phone memory and network | Viewer crashes | Texture budget, chunk eviction, coarse-frame fallback |
| Hosting limits (Pages 1 GB; HF CORS and rate limits) | Broken or slow site | R2 for data; Pages for the app; HF archive only |
| Liability and misuse (people driving on the strength of a "not closed" segment) | Harm, reputational damage | "Advisory, not an official closure" wording; no CAP to IPAWS; agency sign-off before public alerts |
| One maintainer | Stops when the student is busy | Runbook, automation, a status page; hand-over plan with advisors |

## 8. Things not verified here

- Turing GPU types per partition, multi-GPU limits, and whether array tasks count against the cap.
- LISFLOOD-FP GPU memory per cell, and the FP64 vs FP32 speed difference.
- The current state of HF browser Range/CORS (I could not reach huggingface.co from this environment).
- Exact cloud GPU prices.
- iOS per-tab memory limits.
- HEC-RAS GPU status.
- TRITON runtimes at our size (no numbers in the abstract or press coverage).
- The size of chunk delta-coding gains and of the near-road lidar layer.

## Sources

- LISFLOOD-FP 8.1 GPU solvers: Sharifian et al. 2023, GMD 16:2391. https://gmd.copernicus.org/articles/16/2391/2023/
- LISFLOOD-FP 8.2 multiwavelet DG2 on GPU: Chowdhury & Kesserwani 2025, GMD 18:9827. https://gmd.copernicus.org/articles/18/9827/2025/
- LISFLOOD-FP 8.2 source (checkpoint in `cuda/acc/cuda_acc_simulate.cu`, `_NUMERIC_MODE`): Zenodo 10.5281/zenodo.13121102
- RIM2D Berlin real-time forecasting: Khosh Bin Ghomash, Deng & Apel 2026, NHESS 26:85. https://nhess.copernicus.org/articles/26/85/2026/
- RIM2D availability and licence: https://directed-eu.gitbook.io/data-fabric-manual/model-documentation/rim2d
- TRITON: Morales-Hernández et al. 2021, EMS. https://www.osti.gov/pages/biblio/1783054-triton-multi-gpu-open-source-hydrodynamic-flood-model ; https://www.hpcwire.com/2022/08/03/ornls-supercomputer-powered-triton-tool-models-flooding/
- HiPIMS real-time forecasting: https://www.gov.uk/government/case-studies/forecasting-floods-with-unprecedented-detail ; https://repository.lboro.ac.uk/articles/Real_time_flood_forecasting_based_on_a_high_performance_2D_hydrodynamic_model_and_numerical_weather_predictions/12363788
- SFINCS subgrid: van Ormondt et al. 2025, GMD 18:843. https://gmd.copernicus.org/articles/18/843/2025/ ; GPU status: https://sfincs.readthedocs.io/en/v2.3.3/developments.html
- Iber+ GPU: https://ruc.udc.es/dspace/handle/2183/21431
- NSSL FLASH: https://nssl.noaa.gov/projects/flash
- NOAA FIM services fact sheet: https://www.weather.gov/media/owp/operations/FIM_Services_Factsheet.pdf
- Google flash-flood Flood Hub (Mar 2026): https://fox5sandiego.com/news/google-rolls-out-ai-tool-to-predict-flash-floods-up-to-24-hours-ahead/amp/
- UK FFC annual review 2024–25 (surface-water verification, on-time rate): https://www.gov.uk/government/publications/flood-forecasting-centre-annual-review-2024-to-2025/flood-forecasting-centre-annual-review-2024-to-2025
- EA risk of flooding from surface water (2 m terrain, limitations): https://www.gov.uk/government/publications/flood-risk-maps-for-surface-water-how-to-use-the-map/risk-of-flooding-from-surface-water-understanding-and-using-the-map
- NC FIMAN-T: https://fimant.nc.gov/About.aspx
- TxDOT FAST: https://www.caee.utexas.edu/prof/Maidment/StreamflowII/Documents/FAST_OnePager.pdf
- Iowa DOT BridgeWatch research: https://trid.trb.org/View/2362137
- Hampton Roads road-flood sensors (2026): https://www.wvtf.org/2026-01-27/which-roads-flood-in-hampton-roads-a-new-sensor-network-will-help-track
- VIMS street-level forecasts in ArcGIS: https://www.esri.com/about/newsroom/arcuser/leveraging-web-3d-for-street-level-flood-forecasts
- CAP 1.2 and the IPAWS profile: https://docs.oasis-open.org/emergency/cap/v1.2/CAP-v1.2.html ; https://docs.oasis-open.org/emergency/cap/v1.2/ipaws-profile/v1.0/cap-v1.2-ipaws-profile-v1.0.html
- Waze CIFS closure feed: https://developers.google.com/waze/data-feed/cifs-specification
- ArcGIS Online layers from URL (GeoJSON, CSV, Web-Mercator tile layers, WMTS, OGC API): https://doc.arcgis.com/en/arcgis-online/create-maps/add-layers-from-url.htm
- GitHub Pages limits: https://docs.github.com/en/pages/getting-started-with-github-pages/github-pages-limits
- Cloudflare R2 pricing and public buckets: https://developers.cloudflare.com/r2/pricing/index.md ; https://developers.cloudflare.com/r2/buckets/public-buckets/index.md
- PMTiles on cloud storage (CORS, Range): https://docs.protomaps.com/pmtiles/cloud-storage ; spec: https://github.com/protomaps/PMTiles/blob/main/spec/v3/spec.md
- Hugging Face storage limits and rate limits: https://huggingface.co/docs/hub/storage-limits ; https://huggingface.co/docs/hub/rate-limits
- HF Range/CORS problem reports (Jan 2026): https://discuss.huggingface.co/t/cors-support-for-http-range-requests-on-dataset-files/172172 ; https://github.com/huggingface/datasets/issues/7931
- Zenodo limits: https://support.zenodo.org/help/en-gb/1-upload-deposit/80-what-are-the-size-limitations-of-zenodo
- Client-side raster rendering comparison: https://developmentseed.org/datacube-guide/latest/visualization/client-side-comparison.html
- Mapbox raster-array/MRT (time bands in tiles; proprietary, for reference): https://docs.mapbox.com/mapbox-tiling-service/guides/raster-mts/
- Repo: `proto/turing/COMPUTE.md`, `docs/proto/forecast/GATE.md`, `docs/proto/forecast/DISTRICT.md`, `docs/proto/turing/*/flood_meta.json`, `docs/site/viewer.js`
