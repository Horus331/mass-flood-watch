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

## Workload over the next year

| Work | Runs | GPU hours (estimate) |
| --- | --- | --- |
| Historical storm corpus for training (District 3, 20 m; ~20 storms 2014–2026) | ~20 | 20–80 |
| Same storms at 10 m for checks against USGS high-water marks | ~6 | 15–150 |
| Forecast replays: each storm with 6–10 forecast rain members, 6–48 h ahead | ~150 | 50–300 |
| Machine-learning training (gradient boosting / graph neural network on ~50 k segments × storms) | — | 20–50 |
| **Total** | | **~100–600 GPU hours** |

**Storage:** a District 3 run at 20 m with depth saved every 30 min is ~5 GB (about 20 GB at 10 m). Keeping the storm corpus plus
forecast replays needs about **0.5–1 TB** of project storage.

**Why not the free services:** Colab and Kaggle sessions end after 12 h and give no persistent storage; a District 3 run at 10 m
does not fit in one session, and the storm corpus does not fit in their storage.

**Software:** CMake, a C++ compiler, CUDA, netCDF-C and libnuma to build LISFLOOD-FP (`proto/turing/setup_lisflood.sh`);
Python 3.11 with the packages in `proto/turing/environment.yml`. Job script: `proto/turing/run_storm.slurm`.
