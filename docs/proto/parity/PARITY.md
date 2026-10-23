# CPU / GPU parity of the LISFLOOD-FP runs

**Short answer.** The CPU (GitHub Actions) and GPU (Turing, CUDA) runs differ for three reasons. Infiltration is only one of them, and on the light storms it is the smallest.

1. **Infiltration (physics).** The CUDA acceleration solver has no infiltration call, so `LF_INFIL_MMH=2` was applied on the CPU only. This matters on the big storm. Turned off on the CPU, sep2023 goes from 2.44 % to 2.77 % flagged (published GPU: 2.80 %). Land area ≥ 0.3 m goes from 4.0 to 4.8 km², and the Leominster gauge rise from 2.36 to 3.16 m. On the light storms it explains little: jul2023 0.10 → 0.12 % (GPU 0.65 %), aug2023b 0.11 → 0.19 % (GPU 0.51 %).
2. **GPU depth spikes and start-up water (solver output).** 28 of the 43 GPU-flagged segments on jul2023, and 21 of 40 on aug2023b, have a solver maximum depth (`hmax`) more than 0.10 m above every 30-min snapshot. For example, Hampton St has a 3.08 m peak while every snapshot shows 5 cm or less. The CPU runs have 0 such segments of 7 (jul2023) and of 15 (aug2023b), and 2 of 111 on sep2023 (GPU: 14 of 125). GPU roads are also wetter in the first half hour (jul2023: 85 segments ≥ 10 cm at 0.5 h on the GPU against 20 on the CPU). **This is most of the light-storm gap.**
3. **The gauge "rise" on the GPU is a start-level artefact, not lower peaks.** Fitchburg in sep2023 peaks at the same stage and time on both solvers: water surface 120.93 m on the GPU, 120.89 m on the CPU without infiltration, both at 01:30Z. The GPU rise reads 0.35 m because the GPU run's t = 0 snapshot is not the initial state. `score.py` then takes the start level from the 0.5 h frame, which is already raised by the start-up water. The other GPU run (`leominster_sep2023_gpu`) has the same Fitchburg peak (120.87 m) and reads 1.16 m. Its box is 6 km further east and it runs 48 h, but that is not what changes the number.

There is also a CPU-side finding. **At the default time step the CPU run is not converged after the storm peak.** In sep2023, Fitchburg gets a spurious second rise to 1.95 m 8 h after the observed peak, and boundary outflow stays at 60–140 m³/s through the recession. Capped at 1 s, the hydrograph recedes smoothly and the Fitchburg peak lands at 01:30Z (observed 01:15Z, 1.10 m against 1.00 m). The gauge rise error falls from 0.60 to 0.22 m. The published CPU "Fitchburg 1.60 m" is therefore itself a numerical artefact.

**Fix (implemented, env switches):**
* `LF_INFIL_MODE=rain`: infiltration taken out of the hourly rain excess before the solver, identical on both solvers.
* `LF_INIT_TSTEP=1`: both solvers step at ≤ 1 s. On CUDA this is also the cap on every step and the length of the first step.
* `LF_PARITY=1` sets both of these.
* On CUDA, the t = 0 snapshot is now the start file (default on).

On the CPU, `rain` reproduces `solver` within tolerance on all three test storms. **Every published Turing number needs a re-run** (section 6).

Code: `sim/colab/w9_lisflood.py` (`rain_minus_infil`, `LF_INFIL_MODE`, `LF_INIT_TSTEP`, `LF_PARITY`, `LF_CUDA_T0_FROM_START`, `inputs.infiltration` / `initial_tstep_s` / `t0_snapshot` in the run metadata). Runs: `.github/workflows/parity_test.yml` → `docs/proto/parity/<storm>_<variant>/`. Per-run files: `proto/parity_pack.py` (hmax and snapshot peak in cm, `.mass` file). Comparison: `python proto/parity_compare.py` → `docs/proto/parity/parity.json`.

## 1. Setting and input differences between the paired runs

The pairs are the CPU control `docs/proto/urban/dcia/<id>_cn` (and the re-runs here) against the GPU catalogue run `docs/proto/turing/<id>_<area>_20m`, read from `flood_meta.json`.

| item | CPU (Actions) | GPU catalogue (`<id>_<area>_20m`) | GPU `leominster_sep2023_gpu` | matters? |
|---|---|---|---|---|
| solver | LISFLOOD-FP 8.2 acceleration, OpenMP build from Zenodo | same version, CUDA build (`LF_EXE` prebuilt on Turing) | CUDA | yes (sections 2.2–2.5) |
| box | catalogue box | **same** on all 9 storms | **168000–188000 E** (sep2023 catalogue box: 162000–182000 E) | for the gauges: the Leominster gauge (01094500) is **244 m** from the catalogue box's FREE east edge |
| res / t0 / hours | 20 m, catalogue t0, catalogue hours | same | 20 m, same t0, **48 h** (catalogue 36 h) | no for the peaks (both peak before 36 h) |
| rain | MRMS Pass2, totals as GPU (e.g. jul2023 max 32 / mean 23 mm, sep2023 198 / 101 mm) | identical totals, identical rain-file probe (`flip`, `scale 1.0`, `forward`) | 207 / 107 mm (other box) | no |
| loss | `LF_LOSS=cn`, `LF_CN_SCALE=0.91`, AMC II | **same**: the GPU did use the CN loss (env and `inputs.loss`). The loss is applied to the rain before the solver, so it is identical | same | no |
| `LF_INFIL_MMH=2` | applied by the solver (`infiltration 5.556e-07` m/s in the .par) | in the .par but **ignored by the CUDA solver**: the mass file's Rain−(Inf+Evap) column is 0 | ignored | **yes** (2.1) |
| `LF_QOUT` / `LF_VOUT` | 1 / 1 | 1 / 1 | 1 / **not set** (outputs only) | no |
| cfl / theta / dams | defaults (0.7 / 1), no dams | same | same | no |
| time step | reset to `initial_tstep` 10 s each step, then CFL; actual 1.2–1.9 s | per-cell dt that **never increases** (`cuda_acc_solver.cu update_dt_per_element`: min of the CFL dt and the cell's previous dt), capped at `initial_tstep`; the first step for every wet cell is `max_dt` = 10 s without CFL; actual 1.25–1.34 s fixed | same | yes (2.5) |
| t = 0 snapshot | the start file (channels a third full) | not the initial state (in jul2023, 14 segments already ≥ 10 cm at t = 0, against 0 on the CPU) | same | **yes, for the gauge rise** (2.3) |
| git sha | `d4cc3d37` | not recorded (now recorded: `GIT_SHA` in `run_storm.slurm`) | not recorded | see below |
| scoring code (`prototype.py`) | current (bridge-deck matching `dbc2d293`: sep2023 has 89 labels) | 22 Oct evening (sep2023: 78 labels) | same | for label counts only |

Code version of the GPU runs: they have `score.json` (scoring was added to `run_storm.slurm` in `b9d80525`, 22 Oct 17:31), and jul2023–aug2026 exist only from `43eba682` (18:06). So the GPU code is at least `43eba682`. That already includes 4-connected breaching and CN × 0.91 (`8d16c8f2`, 14:03). The default-path `w9` changes between `43eba682` and `d4cc3d37` are all opt-in (drains, HRRR, `cn_dcia`). The CPU `solver` re-run here is bit-identical in hydraulics to the `cn` control (jul2023 end volume 586 335 m³ in both). Its flagged share differs by 0.01 points only because `prototype.py` changed in between.

## 2. What explains the gaps

### 2.1 Infiltration (2 mm/h on every cell deeper than 1 mm, the whole run, CPU only)

Box-mean rain excess reaching the solver, from the `.mass` files (cumulative Rain − Inf). The capacity is 2 mm/h × the run length (36 mm for 18 h, 72 mm for 36 h), far above the excess on the light storms:

| storm | CN excess (no infiltration) | CPU solver infiltration leaves | removed | `rain` mode leaves | removed |
|---|---|---|---|---|---|
| jul2023 (18 h) | 2.29 mm | 0.47 mm | 79 % | 1.59 mm | 30 % |
| aug2023b (18 h) | 6.66 mm | 2.98 mm | 55 % | 4.03 mm | 40 % |
| sep2023 (36 h) | 35.3 mm | 24.2 mm | 32 % | 27.0 mm | 24 % |

The solver form removes more water than `rain` mode because it also drains standing water and thin sheet flow after the rain. That extra water does not set the peaks, so the flood metrics agree (section 4). The end-of-run volume is higher in `rain` mode (jul2023: 0.94 against 0.59 million m³), and time above 30 cm on flagged roads is 0.3–1 h longer.

The effect of switching infiltration off is shown by CPU `infil0` (`LF_INFIL_MMH=0`, the GPU's physics on the CPU):

| storm | flagged share: CPU solver → CPU infil0 (GPU) | land ≥ 0.3 m (km²) | gauge rise (m), obs | end volume (million m³), GPU |
|---|---|---|---|---|
| jul2023 | 0.10 % → 0.12 % (0.65 %) | 0.03 → 0.04 | Spencer 0.02 → 0.05 (GPU 0.00), obs 0.24 | 0.59 → 1.16 (1.39) |
| aug2023b | 0.11 % → 0.19 % (0.51 %) | 0.05 → 0.10 | Millbury 0.11 → 0.20 (GPU 0.00) | 1.43 → 2.56 (2.94) |
| sep2023 | 2.44 % → 2.77 % (2.80 %) | 4.0 → 4.8 | Fitchburg 1.60 → 1.25, Leominster 2.36 → 3.16 (GPU 0.35 / 1.71), obs 1.00 / 2.92 | 2.47 → 2.90 (2.18) |

Infiltration explains the storage gap and most of the sep2023 flag gap, but not the light-storm flags or the gauges.

### 2.2 GPU hmax spikes (most of the light-storm flag gap)

In `segments.geojson`, each segment has its peak depth (from `hmax`) and its depth in every 30-min snapshot (`d`, cm).

| storm | flagged | hmax > every snapshot + 0.10 m | snapshot peak ≥ 0.30 m |
|---|---|---|---|
| jul2023 GPU | 43 | **28** | 19 |
| jul2023 CPU solver / rain / infil0 | 7 / 7 / 8 | 0 / 0 / 0 | 5 / 5 / 7 |
| aug2023b GPU | 40 | **21** | 23 |
| aug2023b CPU infil0 | 15 | 0 | 13 |
| sep2023 GPU | 125 | 14 | 122 |
| sep2023 CPU solver / rain | 111 / 110 | 2 / 2 | 110 / 109 |

The largest GPU cases are Hampton St (hmax 3.08 m, no snapshot above 5 cm; CPU 0.00 m) and Route 12 (2.09 m, snapshots ≤ 10 cm; CPU 0.00 m). The GPU timestep evidence agrees. The CUDA dt never increases, so it equals the run's worst CFL dt: 1.2462 s on jul2023, which means a cell reached 12.9 m of water at some moment. The CPU never went below 1.93 s on jul2023 (deepest about 5.3 m). The CUDA flux kernels are line-for-line the CPU ones (`cuda_acc_solver.cu` vs `fp_acc.cpp`). What differs is the time-step policy: the uncapped 10 s first step for every wet cell, and the never-increasing dt. That policy is the prime suspect for the spikes. It is confirmed only once the GPU runs of section 5 are done.

### 2.3 Gauge rises on the GPU: start-level artefact

| sep2023 run | Fitchburg peak water surface (m) / time | rise (m) | rise50 time |
|---|---|---|---|
| GPU catalogue | 120.93 / 01:30Z | 0.35 | 16:56Z (the first hour) |
| GPU `leominster_sep2023_gpu` (other box) | 120.87 / 01:30Z | 1.16 | 16:20Z |
| CPU infil0 | 120.89 / 01:30Z | 1.25 | 22:50Z |
| CPU solver | 121.24 / **09:30Z** (spurious second rise, 2.5) | 1.60 | 23:46Z |
| observed | 01:15Z | 1.00 | 21:49Z |

The peak stages agree to within 6 cm. The GPU rise is low because its start level comes from the 0.5 h frame (`score.py` skips a dry t = 0 frame), and that frame already carries start-up water. Leominster (01094500) in the catalogue box is 244 m from the FREE east edge, so its catalogue numbers (GPU 1.71, CPU 2.36 m) depend on the boundary. Inside the shifted box the GPU gives 3.26 m (observed 2.92 m).

### 2.4 Things that do not explain the gaps

Rain-file orientation and units (the probe results are identical), the CN loss (applied before the solver, same env), box/t0/hours on the 9 catalogue pairs (identical), and the code version (section 1).

### 2.5 Time step (affects the CPU numbers too)

sep2023, `rain` mode, CPU, at the default step (≤ 10 s, CFL 0.7: 1.2–1.7 s in practice) against a 1 s cap (`LF_INIT_TSTEP=1`):

| | default | ≤ 1 s | ≤ 0.5 s |
|---|---|---|---|
| boundary outflow at 18 / 24 / 30 / 36 h (m³/s) | 139 / 102 / 62 / 87 | 79 / 38 / 21 / 13 | 79 / 38 / 21 / 13 |
| Fitchburg rise (obs 1.00), peak time (obs 01:15Z) | 1.63, 10:30Z (second rise) | 1.10, 01:30Z | 1.10, 01:30Z |
| Leominster rise (obs 2.92) | 2.35 | 2.58 | 2.58 |
| mean abs gauge rise error | 0.60 m | 0.22 m | 0.22 m |
| flagged share, labels | 2.42 %, 35/89 | 2.33 %, 35/89 | 2.33 %, 35/89 |
| flagged-segment Jaccard | (reference) | 0.96 with default | 1.00 with ≤ 1 s |
| land ≥ 0.3 m | 3.94 km² | 3.81 km² | 3.81 km² |
| CPU runtime | 18 min | 35 min | 103 min |

At the default step the recession oscillates: outflow does not decay, and Fitchburg rises a second time with no rain. Flags and flooded area hardly change (Jaccard 0.96), but the gauges do. jul2023 is insensitive: 7 → 5 flagged segments, gauge 0.03 → 0.06 m. **≤ 1 s is converged:** ≤ 0.5 s gives the same result (mean |Δ hmax| 0.000 m on wet cells, every metric identical), so 1 s is the parity setting. aug2023b moves the same way: the Millbury rise goes from 0.13 to 0.28 m (observed 0.93 m), and flagged segments go from 11 to 9.

## 3. The fix

* **`LF_INFIL_MODE=rain`** (`rain_minus_infil`): after the CN loss, each hour's excess becomes max(R − `LF_INFIL_MMH`, 0) on every cell, and the solver's `infiltration` keyword is dropped. Both solvers then receive exactly the same water. `LF_INFIL_MODE=solver` (the default) keeps the old behaviour. On a CUDA build it now logs a warning and records `inputs.infiltration.applied_by = "NONE: …"` in the metadata, so a GPU run without infiltration can no longer pass silently.
* **`LF_INIT_TSTEP`** (default 10, unchanged): on the CPU, the step is reset to this value every step before the CFL limit. On the CUDA build it is `max_dt`, which caps every step and is the whole first step. At 1 s both solvers run at a fixed 1 s while the CFL step is longer (depth < 20 m), so the time-step policy is the same.
* **`LF_PARITY=1`** = `LF_INFIL_MODE=rain` + `LF_INIT_TSTEP=1`. An explicit setting of either still wins.
* **CUDA t = 0 snapshot** (`LF_CUDA_T0_FROM_START=1`, default): after a CUDA run, `res-0000.wd` is replaced by the start file, which is what the CPU build writes. The frames, the gauge start level and start-up checks then read the same t = 0 on both solvers.
* **Metadata:** `inputs.infiltration`, `inputs.initial_tstep_s`, `inputs.t0_snapshot`. The Turing job now records `GIT_SHA`, keeps `LF_VOUT=1` by default, and writes `hmax_cm.npz` (hmax and snapshot peak), `lisflood.mass` and `gauge_windows.npz`, so GPU and CPU runs can be compared cell by cell.

## 4. Proof on the CPU: `rain` against `solver`

Tolerance (summary level, `proto/parity_compare.py` `TOL`): same labels caught; flagged share within 0.1 points or 10 %; every gauge rise within 0.10 m; land ≥ 0.3 m within 10 % or 0.05 km².

| storm | flagged `solver` / `rain` | flagged-segment Jaccard | labels | gauge rise (m) `solver` / `rain` | land ≥ 0.3 m (km²) | mean \|Δ hmax\| on wet cells | verdict |
|---|---|---|---|---|---|---|---|
| jul2023 | 0.10 % / 0.10 % | 1.00 | 0/5 both | 0.02 / 0.03 | 0.03 / 0.04 | 0.03 m | **match** |
| aug2023b | 0.11 % / 0.14 % (9 / 11 segments) | 0.82 | 0/2 both | 0.11 / 0.13 | 0.05 / 0.06 | 0.02 m | **match** |
| sep2023 | 2.44 % / 2.42 % | 0.97 | 35/89 both | 1.60 / 1.63, 2.36 / 2.35 | 4.03 / 3.94 | 0.005 m (p95 0.02) | **match** |
| sep2023, both at ≤ 1 s (`LF_INIT_TSTEP=1`; `rain` = `LF_PARITY=1`) | 2.38 % / 2.33 % | 0.98 | 35/89 both | 1.11 / 1.10, 2.58 / 2.58 | 3.99 / 3.90 | 0.003 m (p95 0.01) | **match** |

`rain` is a faithful stand-in for the solver form on the quantities the catalogue reports. The remaining differences are smaller than the time-step effect in 2.5.

## 5. Turing commands to confirm GPU parity

From the repo root on Turing, after `git pull`. Each job publishes to `docs/proto/turing/<NAME>/` as usual. Set `BOX` inline, not inside `--export`, which splits on commas.

```bash
cd ~/mass-flood-watch && git pull
# jul2023 (catalogue box, 18 h) and sep2023 (catalogue box, 36 h), parity settings: infiltration in the rain, steps <= 1 s
BOX=157000,882000,177000,902000 STORM=jul2023 HOURS=18 NAME=parity_jul2023_gpu_rain_dt1 LF_PARITY=1 sbatch --export=ALL proto/turing/run_storm.slurm
BOX=162000,908000,182000,928000 STORM=sep2023 HOURS=36 NAME=parity_sep2023_gpu_rain_dt1 LF_PARITY=1 sbatch --export=ALL proto/turing/run_storm.slurm
# the same with the default 10 s cap, to separate the time-step effect from the infiltration effect on the GPU
BOX=157000,882000,177000,902000 STORM=jul2023 HOURS=18 NAME=parity_jul2023_gpu_rain LF_INFIL_MODE=rain sbatch --export=ALL proto/turing/run_storm.slurm
BOX=162000,908000,182000,928000 STORM=sep2023 HOURS=36 NAME=parity_sep2023_gpu_rain LF_INFIL_MODE=rain sbatch --export=ALL proto/turing/run_storm.slurm
```

Then, anywhere with the repo: `git pull && python proto/parity_compare.py`. This adds `gpu_rain` / `gpu_rain_dt1` and the pairs `gpu_rain_dt1_vs_rain_dt1` and `gpu_rain_vs_rain`, including the cell-by-cell hmax and snapshot comparison. Pass: `gpu_rain_dt1_vs_rain_dt1` is `MATCH`, and the GPU's `hmax_above_snapshots` count is near the CPU's (0–2). If `gpu_rain_dt1` matches but `gpu_rain` does not, the 10 s first step and capped dt policy were the cause of the spikes. If neither matches, the CUDA build differs in some other way, and the next check is a CUDA run with `LF_INFIL_MMH=0 LF_INIT_TSTEP=1` against the CPU `infil0` with `LF_INIT_TSTEP=1`.

## 6. Verdict: which published numbers need re-running

| published | status |
|---|---|
| `docs/proto/turing/<id>_<area>_20m` (9 catalogue storms, GPU) | **re-run** with `LF_PARITY=1`. On the four flash-miss storms (jul2023, aug2023b, sep2022, aug2023), 53–65 % of GPU-flagged segments are spike-only, and flagged shares are 2–6× the CPU's. On the five good storms, 4–35 % are spike-only and the GPU flags 10–270 % more than the CPU control: sep2021 4.07 vs 3.67 %, sep2023 2.80 vs 2.47 %, aug2026 2.20 vs 1.61 %, aug2021 2.24 vs 1.45 %, jul2021 1.22 vs 0.33 %. All gauge rises use the wrong start level, and infiltration is missing throughout. |
| `leominster_sep2023_gpu`, `leominster_sep2023_10m`, `leominster_sep2023_dams`, `worcester_aug2021_gpu`, `worcester_aug2021_dams`, `d3_sep2023_20m` (GPU) | **re-run** (same three GPU issues; the dams runs also rely on weirs that the CUDA solver may ignore). |
| Anything built on them: `docs/proto/ml/` (LOSO features `features_<storm>.csv`), `docs/proto/recall/RECALL.md`, `docs/proto/res10m/FINDINGS.md`, the GPU column of `docs/proto/urban/DCIA.md` and the GPU references in `docs/proto/urban/FINDINGS.md` | **re-derive** after the re-run. |
| CPU-vs-CPU comparisons (`docs/proto/urban/DCIA.md` `cn` vs `cn_dcia`, sections 3–5) | valid as relative comparisons (same solver, same settings). Their gauge numbers carry the time-step artefact in 2.5 (e.g. Fitchburg 1.60 m). |
| CN × 0.91 calibration (on sep2023 at the default time step) | **re-check** at `LF_PARITY=1`. At ≤ 1 s, the sep2023 gauge rise bias is −0.12 m instead of +0.03 m, so ×0.91 may no longer be the best value. |

Recommended for the next catalogue run: `LF_PARITY=1` on both solvers, with GPU and CPU spot checks compared by `parity_compare.py` before any number is published.
