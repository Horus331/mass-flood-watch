# Compute needed, from the measured prototype run

**Measured (GitHub Actions, 4 CPU cores, Oct 21 2026):** LISFLOOD-FP 8.2 local-inertial solver, 20 × 20 km box at 20 m
(1.0 M cells), 36 h of the Sept 11, 2023 storm with hourly radar rain: **26.7 min** of model time, ~3 min to build the model and
~3 min to fetch inputs. The road-closure step takes about a minute.

## Scaling to the dissertation (estimates)

| Run | Cells | CPU, 4 cores (scaled from the measured run) | 1 GPU (LISFLOOD-FP GPU solver, 2–28× faster than CPU per Sharifian et al. 2023) |
| --- | --- | --- | --- |
| Leominster box, 20 m, 36 h (measured) | 1.0 M | 27 min | ~1–15 min |
| All of MassDOT District 3 (78 × 90 km), 20 m | 17.6 M | ~8 h | ~20 min – 4 h |
| District 3 at 10 m (road-scale detail; half the time step) | 70 M | ~60 h | ~2 – 30 h |

Time scales with cells × steps; halving the grid size gives 4× the cells and about 2× the steps.

## Watershed-shaped domains (`LF_DOMAIN=basin`, `sim/colab/lf_domain.py`, job `proto/turing/run_basin.slurm`)

A basin domain runs only the cells that drain to the chosen outlets (USGS gauge basins from NLDI, or WBD HU8/HU12 units); the rest of
the bounding box is NODATA, which LISFLOOD-FP turns into walls that get no rain and cost only the full-grid bookkeeping passes.

**Measured (GitHub Actions, 4 CPU cores, 22 Oct 2026, Sept 2023 storm, 48 h, 20 m):**

| Run | Active cells (box) | LISFLOOD-FP time | s per M active cells per simulated hour |
| --- | --- | --- | --- |
| 20 × 20 km square box (default solver) | 1.00 M (1.00 M) | 36.9 min | 46 |
| North Nashua basin to Leominster (default solver) | 0.71 M (1.82 M) | 30.8 min | 54 |
| 20 × 20 km square, `LF_THETA=0.7 LF_CFL=0.5` | 1.00 M | 45.0 min | 56 |
| North Nashua basin, `LF_THETA=0.7 LF_CFL=0.5` | 0.71 M (1.82 M) | 41.4 min | 73 |

Estimates below use **50–75 s per M active cells per simulated hour at 20 m** on 4 cores, and twice that per cell at 10 m (half the
time step), so 10 m costs about 8× the 20 m run. GPU: the LISFLOOD-FP 8.1+ GPU local-inertial solver is 2–28× faster than its multicore
CPU version (Sharifian et al. 2023, GMD 16:2391, doi:10.5194/gmd-16-2391-2023); the high end applies to large, mostly wet grids,
so the low end is the safe assumption for small basins.

| Domain (file in `docs/network/basins/`) | Area | Active cells 20 m (box) | 20 m, 4 CPU cores | 10 m active cells | 10 m, 4 CPU cores | 10 m, 1 GPU |
| --- | --- | --- | --- | --- | --- | --- |
| (a) North Nashua to Leominster 01094500 (+ Fitchburg 01094400 nested), 48 h (`domain_leominster_nn`) | 285 km² | 0.71 M (1.82 M) | 31–41 min (measured) | 2.85 M | 3.8–5.7 h | 8 min – 2.9 h |
| (b) Blackstone to Millbury 01109730 + Quinsigamond 01110000 (Worcester), 18 h Aug 2021 storm (`domain_worcester_bq`) | 254 km² | 0.64 M (1.74 M) | 10–14 min | 2.54 M | 1.3–1.9 h | 3 min – 1 h |
| (c) MassDOT District 3 by HUC8: Nashua, Concord, Millers, Chicopee, Blackstone, Quinebaug (6 independent jobs, `domain_d3_hu8_*`), 48 h | 8,470 km² | 21.2 M total, largest 4.8 M (50.5 M) | 14–21 h total; largest job 3.2–4.8 h | 84.7 M total, largest 19.2 M | 113–170 h total; largest 26–38 h | 4–85 h total; largest 0.9–19 h |
| Vermont: Winooski to Montpelier 04286000 + Dog River 04287000, 60 h July 2023 storm (`domain_winooski_montpelier`, `run_vt_basin.slurm`) | 1,240 km² | 3.11 M (7.14 M) | 2.6–3.9 h | 12.4 M | 21–31 h | 0.8–16 h |

Whole HU8s include their parts in NH, RI and CT (the Nashua HU8 runs to the Merrimack; Blackstone to Pawtucket; Quinebaug into CT); those
need inputs from public services rather than the MA Hugging Face tiles: `proto/turing/stage_inputs.sh` with `VT=1` builds them with
`sim/colab/vt_inputs.py` for any box. The HU12 alternative (all HU12s touching District 3 + everything upstream by WBD `tohuc`) is
15,150 km² (37.9 M cells at 20 m) because it pulls in whole upstream river systems; HUC8 jobs are smaller and independent.
The Winooski basin above Essex Junction (04290500, about 2,700 km²) would be ~6.8 M cells at 20 m (5.7–8.5 h on 4 cores).

**Before the solver:** the domain mask and depression breaching are pure-Python priority floods over the *box* (not only the basin):
about 2 s per M cells each for the domain routing and the breaching at 20 m (measured on the 1.8 M-cell North Nashua box); a 48 M-cell box (Quinebaug HU8 at 10 m) needs
several GB of RAM and ~10–20 min for these steps, within a 64 GB node.

**Offline compute nodes:** stage inputs on a login node (`proto/turing/stage_inputs.sh`: Hugging Face tiles into the HF cache, or
`vt_inputs.py` for out-of-state boxes, and MRMS radar into `LF_MRMS_DIR`), then run with `LF_EXE` (the LISFLOOD-FP built by
`setup_lisflood.sh`) and `HF_HUB_OFFLINE=1`; nothing in the job then needs the internet.

## Workload over the next year

| Work | Runs | GPU hours (estimate) |
| --- | --- | --- |
| Historical storm corpus for training (District 3, 20 m; ~20 storms 2014–2026) | ~20 | 20–80 |
| Same storms at 10 m for checks against USGS high-water marks | ~6 | 15–150 |
| Forecast replays: each storm with 6–10 forecast rain members, 6–48 h ahead | ~150 | 50–300 |
| Machine-learning training (gradient boosting / graph neural network on ~50 k segments × storms) | — | 20–50 |
| **Total** | | **~100–600 GPU hours** |

## Storm drains (`LF_DRAINS`, `sim/colab/lf_drains.py`, job `proto/turing/run_drains.slurm`)

The drain sink runs on the **CPU** build only (patched `FPInfiltration`; the CUDA acceleration solver has no per-cell sink unless built
with the untested `LF_PATCH_CUDA_SINK=1`). The job builds `$LF_WORK/build_cpu/lisflood` with the patch, sets `LF_EXE` to it (env.sh
would pick the GPU build) and runs Leominster (box 168000,908000,188000,928000, 20 m) for Sept 2023 (48 h) and Aug 3, 2026 (t0
2026-08-03T04:00Z, 18 h), each without and with `LF_DRAINS=~/private/leominster_drain_pipe.zip` (copied there by hand, never into the
repo): 4 CPU runs of ~15–25 min on 16 cores (`-p long`). Results stay on Turing unless `PUBLISH=1` (then only score/points/meta json).

**Storage:** a District 3 run at 20 m with depth saved every 30 min is ~5 GB (about 20 GB at 10 m). Keeping the storm corpus plus
forecast replays needs about **0.5–1 TB** of project storage.

**Why not the free services:** Colab and Kaggle sessions end after 12 h and give no persistent storage; a District 3 run at 10 m
does not fit in one session, and the storm corpus does not fit in their storage.

**Software:** CMake, a C++ compiler, CUDA, netCDF-C and libnuma to build LISFLOOD-FP (`proto/turing/setup_lisflood.sh`);
Python 3.11 with the packages in `proto/turing/environment.yml`. Job scripts: `proto/turing/run_storm.slurm` (square box), `run_basin.slurm`
(watershed domain), `run_vt_basin.slurm` (Vermont Winooski basin); staging `stage_inputs.sh`.
