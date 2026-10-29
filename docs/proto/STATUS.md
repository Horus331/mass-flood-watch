# Project status (25 Oct 2026): the single source of truth

If another doc disagrees with this page about what is deployed or what a result means, this page wins. Paths are relative to `docs/proto/`.

## 1. What is deployed

| | setting | source |
|---|---|---|
| Flood model | LISFLOOD-FP 8.2, 20 m, **`LF_PARITY=1`** (infiltration in the rain, step ≤ 1 s, same physics on CPU and GPU), `LF_LOSS=cn`, AMC II, **`LF_CN_SCALE=0.88`**, `LF_INFIL_MMH=2`, `LF_QOUT=1`, hourly MRMS Pass2 rain, no dams, no drains | `parity/BASELINE.md` |
| Closure rule | **p_close ≥ 0.5**, P = Φ((d − 0.30 m) / 0.10), d = second-highest road point per segment; bridge decks read depth from their approaches | `recall/RECALL.md` §4, `proto/prototype.py` |
| Live forecast | gate 25 mm / 6 h or 40 mm / 24 h on HRRR; 8-member time-lagged HRRR ensemble, **likely closed = 2 of 8**, possible = 1 of 8; same model settings as above since 25 Oct 2026 (was CN × 0.91, default step) | `forecast/GATE.md`, `forecast/ENSEMBLE.md` |
| Opt-in layers (default off, never change `p_close` unless noted) | `PROTO_TIERS=1` watch tier (rule + learned v1 P ≥ 0.02); `PROTO_PLUVIAL=1` pluvial v1 (adds to p_close when on); `PROTO_DAMAGE=1` crossing damage; `PROTO_RES_CONSISTENT=1` resolution-consistent depth; `PROTO_FLASH=1` MRMS FLASH features; `LF_DRAINS`; `LF_DAMS=1`; `LF_RAIN_DT=5`; `LF_RAIN_GAUGE=idw` (hindcast only); `SCORE_CRASHWATER=1`; `FORECAST_KOFN`; `FORECAST_ENSEMBLE=0` (single cycle) | the experiment files below |
| Protocol | PROTOCOL v2: decision set = held-out 23 storms; locked storms aug2015, aug2018, aug2020, jul2018, oct2016 never run or read | `PROTOCOL.md` |

## 2. Honest headline numbers (the ones to quote)

- **Held-out skill, deployed rule** (23 storms, nested LOSO, box-wide; `ml/EXPANDED.md` §3, labels before round 2): **5 / 90 sites = 0.056
  [0.01, 0.11]** at 0.43 % of segments flagged (lift 4.8). Ranking at a 3 % budget: **15 / 90 = 0.167 [0.08, 0.26]**, chance 0.064, lift 2.6.
  FSS@300 0.019 ≈ chance. On the 16 new storms alone the rule catches 1 / 58 (`scoring/BASELINE_v2_expanded.md`).
- **After label round 2** (same runs, 98 sites; `obs/LABELS_ROUND2.md` §4): rule 0.092 (lift 6.4); 3 %: **0.204 [0.10, 0.30]**, lift 3.1.
  This is a measurement change, not a model gain. **Every later `--compare` must use `obs/round2/score_round2.json` as its baseline.**
- **Best candidate, not adopted:** rule + learned watch at 3 % budget, 26 / 90 = 0.289 [0.19, 0.39]; failed the k = 5 significance test
  (P ≈ 0.014 vs 0.01). Report as a candidate only (`ml/EXPANDED.md`).
- **Gauges:** mean per-storm rise error 0.46 m on the 9-storm parity catalogue, 0.31 m on the 16 new storms (bias −0.28 m)
  (`parity/BASELINE.md`, `scoring/BASELINE_v2_expanded.md`).
- **Forecast** (`forecast/ENSEMBLE.md` §4, 7 out-of-sample storms, 29 sites, run at CN × 0.91): 2-of-8 pooled recall 0.21 → 0.34 at
  ~9–10 h lead and 0.07 → 0.28 at ~3–4 h vs the single cycle; lift lower than the single cycle at long lead (4.0 vs 5.3).
- **In-sample** numbers (Leominster sep2023 30 / 79 at 3 %, Worcester aug2021) are development storms and are never the headline.

## 3. Experiment ledger

| experiment | verdict | file |
|---|---|---|
| CPU/GPU parity (`LF_PARITY=1`) | **adopted** (CPU proof done; GPU confirmation runs landed, compare pending) | `parity/PARITY.md` |
| CN recalibration at parity (× 0.91 → 0.88) | **adopted** | `parity/BASELINE.md` §1 |
| Clean parity catalogue (25 storms, CPU) | **adopted** as the baseline | `parity/BASELINE.md`, `scoring/BASELINE_v2_expanded.md` |
| Dams (`LF_DAMS=1`, cfl 0.3) | not adopted (confounded with cfl; lift falls) | `exp/DAMS_2026-10-22.md` |
| Storm drains v1 (`LF_DRAINS`) | not adopted (opt-in lower bound) | `drains/DRAINS.md` |
| DCIA loss (`cn_dcia`) | not adopted (doesn't fix misses; "qualified yes" deferred to a future re-baseline, not taken in T0) | `urban/DCIA.md` |
| Sub-hourly rain (`LF_RAIN_DT=5`) | not adopted (opt-in) | `rain/RAIN.md` |
| Forward test from 3 Nov 2026: ledger of every live cycle + flood-report trigger (catches misses) + automatic results | **live** (pre-registered 29 Oct) | `prospective/PROSPECTIVE.md`, `prospective/RESULTS.md` |
| USGS stream-camera stills (NIMS, public domain) for archived and catalogue storms | **no yield for D3** (13 MA cameras, 0 in D3, 2 within 10 km, no images in 4 catalogue storms); follow-up step left on | `cameras/CAMERAS.md` |
| Gauge-adjusted rain (`LF_RAIN_GAUGE=idw`) | not adopted (hindcast-only, opt-in) | `rain/RAIN.md` |
| T4 antecedent moisture / infiltration | A (`LF_CN_AMC=auto`) **not adopted**; B1 (`LF_INFIL_MMH=1`) **not adopted**; B0 (`LF_INFIL_MMH=0`) and C (LOSO NWM-wetness CN) **unfinished** (stopped at owner's request; retest under v2) | `runoff/AMC.md` |
| Pluvial rule v1 (`PROTO_PLUVIAL=1`) | not adopted (opt-in; fails on the parity baseline) | `urban/FINDINGS.md`, `urban/PLUVIAL_v2.md` |
| Pluvial rule v2 | not adopted (fails 3 of 5 conditions) | `urban/PLUVIAL_v2.md` |
| Learned closure model v1 | not adopted as the alert; feeds the opt-in watch tier | `ml/RESULTS.md`, `ml/LOSO.md` |
| Learned v2 (rule-offset, graph, PU weights) | not adopted | `ml/LEARNED_v2.md`, `ml/EXPANDED.md` |
| Two-tier alert (rule + learned watch) | not adopted as default (opt-in `PROTO_TIERS=1`; v2 retest failed significance narrowly) | `recall/RECALL.md`, `ml/EXPANDED.md` |
| 10 m resolution fix (`PROTO_RES_CONSISTENT=1`) | not adopted (opt-in); 10 m start-up fix and re-run unfinished | `res10m/FINDINGS.md` |
| Bridge-deck matching | **adopted** (scoring default) | `recall/RECALL.md` §4 |
| Crossing damage layer (T7) | not adopted (opt-in `PROTO_DAMAGE=1`; AUC 0.78 vs 0.68, CI includes 0) | `damage/DAMAGE.md` |
| Forecast hindcast (HRRR, neighbourhood 20 km / p90) | **adopted** (`LF_HRRR_NBHD=20,90` live) | `forecast/HINDCAST.md` |
| Forecast ensemble (8 lagged members, 2 of 8) | **adopted** (live default) | `forecast/ENSEMBLE.md` |
| Forecast quantile mapping | not adopted | `forecast/ENSEMBLE.md` §2 |
| Forecast spreading 10,90 / 20,75 / raw (District 3 over-forecast) | not adopted (box veto: −2 / −3 / −3 OOS sites under 2-of-8); 20,90 stays | `forecast/DISTRICT.md` |
| Labels round 1 (16 storms, news/agency) | **adopted** | `obs/LABELS_EXPANSION.md`, `obs/CATALOG.md` |
| Labels round 2 (split, WX1BOX, crash-water, FLASH) | **adopted** (labels); crash-water and FLASH stay opt-in sources | `obs/LABELS_ROUND2.md` |
| Static flood maps as a baseline (FEMA NFHL SFHA via MassGIS, cross-checked with FEMA REST; BSC/MRPC Leominster 100-yr) | **benchmark, nothing adopted** (pre-registered 29 Oct): held-out 23, FEMA SFHA ∩ road 32 / 98 at 7.0 % flagged (lift 2.2) vs model top-*k* at the same share 36 / 98, Δ −0.04 [−0.18, +0.11], no detectable difference; model rule lift 6.4; only 15 sites shared; on sep2023 (dev) the model wins at equal share (Δ −0.23); BSC extents flag 48 % of Leominster roads, chance at ≥ 30 % | `static/STATIC.md` |
| Surrogate of LISFLOOD-FP (U-Net, terrain + rain -> peak depth; for the district-wide 2-of-8 ensemble only) | **pre-registered, not run** (29 Oct; no run or score yet) | `surrogate/SURROGATE.md` |

## 4. Open items

**(a) Owner, on Turing** (`cd ~/mass-flood-watch && git pull`)

1. ~~Night batch of 23 Oct~~ **done (28 Oct):** the parity runs published to `docs/proto/turing/`, and the `pack_site` jobs replaced the live replays (`leominster_sep2023`, `worcester_aug2021`, `d3_sep2023`) with the `LF_PARITY=1, CN 0.88` GPU runs on 23–24 Oct.
2. ~~`parity_compare.py`~~ **done (28 Oct): GPU = CPU** with `LF_PARITY=1` on jul2023 and sep2023 (J 1.0, depth difference 0.000 m); see PARITY.md "GPU confirmation". A GPU rerun of the catalogue (item 4) is therefore optional: the CPU parity catalogue is the same physics.
3. ~~`hindcast_d3_sep2023_18z`~~ **done (28 Oct), published to `docs/proto/turing/hindcast_d3_sep2023_18z/`:** the District 3 GPU forecast from the 18z HRRR cycle (20 km / p90 spreading) flags **888 segments (615 km)** vs **276 (197 km)** in the radar-driven run, about 3x over-forecast district-wide even though its peak storm total is lower (158 vs 207 mm): the neighbourhood spreading wets a much larger area. Box-level hindcasts were fine (HINDCAST.md); district-wide the ensemble rule (2-of-8) or less spreading is needed before showing a D3 forecast map. **Follow-up (29 Oct, `forecast/DISTRICT.md`):** pre-registered test of 10,90 / 20,75 / raw keeps **20,90 live**: on the boxes every alternative loses 2-3 of 29 OOS sites under 2-of-8; the district excess is a rain-volume bias of the 90th percentile (D3 volume 1.9x MRMS; 10,90 1.8x, 20,75 0.8x), not the radius, so the D3 map needs its own fix (2-of-8 on Turing or a volume-preserving neighbourhood). The Turing runs `hindcast_d3_18z_nb10p90 / _nb20p75 / _raw` had not published after 4 h; score them with `proto/forecast_nbhd.py district` (they cannot change the default: the box veto already decides).
4. If parity matches: `LF_PARITY=1 LF_CN_SCALE=0.88 bash proto/turing/submit_catalog.sh` (the variables are inherited through `--export=ALL`;
   the script's own default is still the old × 0.91 from `run_storm.slurm`).
5. Drains job 2401314: `tail -40 roadflood_drains_2401314.out` (and `results/drains_*`); publish with `PUBLISH=1` only if useful.
6. **Surrogate, batch 1** (`surrogate/SURROGATE.md` §6). Once: `conda activate ~/envs/roadflood && pip install torch --index-url https://download.pytorch.org/whl/cu126`. Then:
   - `python proto/surrogate/scenarios.py scan --out ~/scratch/surrogate/scan.json` (login node, ~1 h).
   - `python proto/surrogate/scenarios.py plan --scan ~/scratch/surrogate/scan.json --batch 1 --out ~/scratch/surrogate/plan_b1.json` (prints the array range).
   - `sbatch --array=0-23%4 --export=ALL,PLAN=$HOME/scratch/surrogate/plan_b1.json,PER_TASK=8 proto/turing/surrogate_gen.slurm` (192 box runs, ~16 GPU-h, ~4 h on 4 GPUs; no push).
   - `sbatch proto/turing/surrogate_inputs.slurm` (CPU, ~2-3 h: inputs for the 25 catalogue storms and District 3; no push).
   - When both are done: `sbatch --export=ALL,PLANS=$HOME/scratch/surrogate/plan_b1.json proto/turing/surrogate_train.slurm` (~3 GPU-h; one push to `docs/proto/turing/surrogate_eval/` and `docs/proto/surrogate/RESULTS.md`).
   - Back up: `bash proto/turing/backup_hf.sh --runs-root ~/scratch/surrogate --results-root /nonexistent --prefix runs/surrogate`.

**(b) Owner, emails / secrets**

- Worcester DPW data request (draft ready); reply to Roseberry; CMRPC / MRPC NPMRDS request.
- Add the `GOTIME_KEY` repository secret so the traffic logger can run.
- Optional: a free USGS API key (api.waterdata.usgs.gov/signup) as the `API_USGS_PAT` secret, for the camera fetches' rate limit.
- MassDOT traffic-camera stills: request research access from TrafficLand / MassDOT (`cameras/CAMERAS.md`); nothing is collected until then.
- Waze data via Prof. Tao: on hold.

**(c) Can be done on GitHub (no owner action)**

- T4: finish B0 and C as a new PROTOCOL v2 pre-registration on held-out 23 (`runoff/AMC.md` §2 recommendations).
- Check the 13 candidate flood days from crash data (`obs/round2/crashwater_days.json`) against NWS LSR / Storm Events before any becomes a storm.
- Run `parity_compare.py` on the GPU results already in `turing/` (item a2) if the owner prefers.
- Roadmap tasks not started: T6 depth × velocity / duration rule; T8 report-conditioned live correction; T9 drains v2; T10 10 m urban
  sub-boxes; T11 nowcast + REFS logging from 3 Nov 2026; T12 gauge-merging diagnostic.
- Re-test the two-tier design (d) when more storms are labelled, as a new pre-registration.
