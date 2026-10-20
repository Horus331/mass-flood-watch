# LISFLOOD-FP benchmark for the GPU flood engine (`sim/colab/w9_lisflood.py`)

This benchmark runs the Sept 11, 2023 Leominster flash flood twice on the same inputs. One run uses our rain-on-grid engine (`w4_flood_gpu.py` + `sim/solver.py`). The other uses LISFLOOD-FP, the University of Bristol's open-source reference model for the same numerical family: local-inertial, after Bates et al. 2010. The question is whether our solver agrees with the established implementation, and where it does not, whether the gap comes from the hydraulics or from the parts that only our engine has (losses, sub-grid channels, the q-centred scheme).

- **Run:** `RUN_DIR=runs/sep2023_lisflood_20m BOX=150000,905000,170000,925000 RES=20 python w9_lisflood.py`. It needs a GPU runtime and `HF_TOKEN`. `HOURS` can shorten the window to 12–36 h, and `RES=30` is available if 20 m is too heavy.
- **Offline check:** `python sim/colab/w9_lisflood.py --selftest`. It checks the DEM and Manning ASCII grids, the rain NetCDF, the boundary and parameter files, the probe logic and the output reader. It passed in the agent sandbox (8 checks).
- **Score:** `RUN_DIR=runs/sep2023_lisflood_20m python w6_validate.py`, unchanged. The run name starts with `sep2023_`, so w6 picks up `gauges_sep2023.json`.

## Version and source
| item | value | source |
|---|---|---|
| model | LISFLOOD-FP **8.2**: GPU ACC (uniform and non-uniform), FV1, DG2, and MWDG2 adaptivity added in 8.2 | Chowdhury & Kesserwani, GMD 18, 9827 (2025) |
| code | Zenodo `10.5281/zenodo.13121102` (v8.2). The script falls back to concept record `4073010`, which resolves to the newest version (it listed `LISFLOOD-FP-v8.2.zip`, 348 MB, published 2024-07-29). Older versions: 8.1 = `6912932`, 8.0 = `4073011`. | zenodo.org/record/4073010; GMD 2025 code availability |
| licence | GPL v3, "for non-commercial use" (as stated in the 8.1 paper) | Sharifian et al., GMD 16, 2391 (2023) |
| GPU local-inertial | 8.1 added GPU parallelisation of the uniform ACC solver, 2–28× faster than the CPU ACC solver | GMD 16, 2391 (2023) |
| rain-on-grid | `.rain` text file (spatially uniform) or NetCDF `.nc` (spatially and temporally varying), "imposes the prescribed rainfall at grid elements" after the mass update. The `.nc` file uses the TUFLOW NetCDF rainfall format. | GMD 16, 2391; Shaw et al., GMD 14, 3577 (2021) and preprint gmd-2020-340; TUFLOW wiki "TUFLOW NetCDF Rainfall Format" |
| build | CMake since 8.0 ("new CMake-based build system"), OpenMP CPU build, CUDA GPU build | GMD 16, 2391; GMD 14, 3577 |

**Not confirmed.** The official user guide (seamlesswave.com/LISFLOOD8.0) could not be fetched from the agent sandbox, so the exact CMake switch names and the parameter keywords are not checked against it. The script handles this in three ways:
- **Build switches.** It reads the switch names from the downloaded source: every `option()`/`set()` name in `CMakeLists.txt` and `*.cmake` that contains CUDA or NETCDF. It copies an example `config.cmake` if one is shipped, turns NetCDF on (and CUDA on when `nvcc` and a GPU exist), and logs all of it.
- **CPU fallback.** If the CUDA build fails, it builds for CPU.
- **Keywords.** The keywords used are the long-standing ones: `DEMfile resroot dirroot sim_time initial_tstep massint saveint fpfric acceleration manningfile dynamicrainfile bcifile startfile`, plus `cuda` for the GPU. `fv1`/`cuda` appear in GMD 14, 3577 Appendix A and in a public 8.2 user pipeline (github.com/ihaseeburrehman/ai-nwp-lisflood-fp-coupling), along with `dynamicrainfile`, `sim_time` and `saveint`.

The first Colab log is the real check. Read the `build switches found` and `par:` lines and the end of `lisflood_stdout.txt`.

Everything (zip, source, build, probes, run) lives under `/content/lisflood`. System packages: `cmake libnetcdf-dev netcdf-bin` via apt.

## Input mapping (same data as w4)
| input | w4 engine | LISFLOOD-FP run |
|---|---|---|
| DEM | HF `data/dem10` 20 km tiles averaged to RES, sea = low ground connected to the edge, inland lidar voids filled | same code, written as `dem.asc` (ESRI ASCII, north-up, `xllcorner/yllcorner` = box corner) |
| channels | channels30 burnt at full bankfull depth, **sub-grid** width/storage (default `SUBGRID=1`) | channels30 burnt **volume-equivalent** (`depth × min(width/RES, 1)`) = w4's `SUBGRID=0` path. LISFLOOD-FP's own sub-grid channel module is not used (support in the GPU ACC solver is not confirmed). `LF_CHAN=none` skips the burn. |
| Manning n | 0.035 water/channel, 0.10 where NLCD impervious > 30 %, 0.08 other | the same map → `manningfile n.asc` (`fpfric 0.08` as the default) |
| rain | MRMS `MultiSensor_QPE_01H_Pass2` hourly, bilinear onto cell centres (`mrms_hour`) | the same grids → `dynamicrainfile rain.nc` on the DEM grid (see below) |
| losses | Horton infiltration by SSURGO group, storage-limited, antecedent store from 14-day MRMS, storm drains 7 mm/h × paved fraction | **none** by default. Native infiltration in the GPU ACC solver is not confirmed. `LF_LOSS=fc` subtracts a steady rate from each hour of rain instead: soil fc by group × (1 − 0.9·paved) + 7·paved drains, none on water. This is a rain-excess approximation. It removes less than w4 early in the storm (no Horton f0, no store) and more on saturated ground (w4 drops to KDEEP). |
| boundaries | edge cells are a sink (open), sea a sink or tide | `bcifile`: `FREE` on N/S/E/W. The Leominster box is inland, so sea and tide do not apply. |
| start state | channels a third full (0.3 × burn) | `startfile start.wd` = 0.3 × burn on channel cells (`LF_BASEFLOW=0` turns it off) |
| inflows | USGS gauge inflows for the CT/Merrimack/Deerfield entries | none: no entry point lies in the Leominster box |
| solver | local inertial, q-centred θ = 0.7, Froude cap 2, CFL 0.7, dt ≤ 10 s, wet threshold 1 mm | `acceleration` (+ `cuda`), model defaults (θ = 1, its own CFL and depth threshold), `initial_tstep 10` |

### How rain-on-grid is fed
- **File layout.** `rain.nc` follows the TUFLOW layout:
  - variable `rainfall_depth(time, y, x)` in mm, `_FillValue` −999, plus `total_rainfall_depth(y, x)`
  - `time` in hours from the start of the run
  - `x`/`y` as cell-centre coordinates in EPSG:26986, both ascending
  - written as NetCDF-3 64-bit offset, readable by any netcdf-c
- **Grid.** The rain grid is the DEM grid, so the origin and tile size match, as LISFLOOD-FP requires.
- **Units.** Records are hourly, so depth per interval equals mm/h, and the format's depth-or-rate ambiguity does not matter.
- **Time stamps.** MRMS hour *h* covers simulation time [h, h+1) h. It is stamped at the interval start (t = h), and a zero record closes the storm. This follows the reported 8.2 behaviour of holding a record forward from its stamp; the ai-nwp-lisflood-fp-coupling v2.0 fix cut their water-balance residual from 8.69 to 0.17 mm per 6 h.
- **Probe runs.** These conventions are not taken on trust. Before the real run the script makes two 8×8 flat closed-box probe runs with the same binary:
  - **Probe A** puts 36 mm/h on the NW quadrant for 2 h. Where the water lands gives the y/x orientation, and how much lands (should be 0.072 m) gives the units.
  - **Probe B** puts 36 mm in the first record only. 0.036 m means held forward, about 0.018 m means linear interpolation, and 0 means the record covers the interval ending at its stamp.

  The main rain file is then written to match: flipped, re-stamped or rescaled as needed. The probe result is stored in `meta.rain_probe`.

## Outputs (run layout read by w6)
The script uploads to HF `mohabeldokla/mass-flood-watch-tiles` under `RUN_DIR`, in **one** `create_commit`:
- `hmax.npy`: float32 m. It comes from LISFLOOD-FP's `res.max` if written, otherwise from the max of the `.wd` snapshots (`meta.hmax_source`).
- `hsnap.npy`: peak of the 30-min snapshots. w6 scores this too, as `validation_hsnap.json`.
- `z.npy`: the DEM as run.
- `meta.json`: `run`, `box`, `res_m`, `shape`, `t0`, `frame_min`, `frames[]` (t, wet_km2, deep_km2 per 30 min, land only), `crs`, `model: 'LISFLOOD-FP 8.2'`, source DOI, CUDA flag, `runtime_s`, `peak_wet_km2`, `rain_probe`, last lines of the `.mass` file.
- `run.par`, `run.bci`, `lisflood_stdout.txt`, `lisflood.mass`, `w9_log.txt`.

The log records build time, run time and peak wet area (hmax ≥ 10 cm on land, plus the largest snapshot wet area).

## Differences that will show up in the comparison
1. **Losses.** LISFLOOD-FP (default) puts all the rain on the surface. w4 takes infiltration and drains off. On the same rain, LISFLOOD-FP should be wetter everywhere.
2. **Channels.** w4 runs sub-grid channels by default. The LISFLOOD-FP run uses volume-equivalent burnt channels on a full-width cell.
3. **Scheme details.** w4 uses θ = 0.7 and Fr ≤ 2. LISFLOOD-FP runs at its defaults. This should show mainly on steep cells and as single-step `hmax` spikes; compare `hmax` against `hsnap`.
4. **Precision and GPU.** LISFLOOD-FP GPU solvers compute in double precision (GMD 14, 3577); w4 uses float32.

## Like-for-like control run of w4 (recommended)
Run w4 with the same box, window and resolution, with the differences turned off:

`RUN=sep2023 BOX=150000,905000,170000,925000 RES=20 SUBGRID=0 FC_SCALE=0 TAG=_lfctl`

- `SUBGRID=0` gives the volume-equivalent channels.
- `FC_SCALE=0` removes soil infiltration.
- Storm drains (7 mm/h × paved fraction) and the antecedent store stay. w4 has no switch for those, so they remain a small known difference, mostly in town centres.

This control is compared with LISFLOOD-FP `LF_LOSS=none`. The production w4 run (all physics) is compared with LISFLOOD-FP `LF_LOSS=fc`.

## How the comparison will be read
- **Same validation metrics.** Each run gets w6's `validation.json`: USGS high-water marks (WSE bias, MAE, within 50 cm, wet within 30 m), road flood reports, and gauge stage/WSE where available. The engines are compared metric by metric on identical observations. LISFLOOD-FP is the reference, not the truth: where it scores better on the marks, our solver has something to fix.
- **Cell by cell, on the common grid** (same box and res, so the arrays line up), over land cells, with channels reported separately:
  - CSI = hits / (hits + misses + false alarms) for wet = hmax ≥ 0.10 m, with hit rate and false-alarm ratio, plus the same for ≥ 0.30 m
  - depth difference over cells wet in either run: bias (w4 − LISFLOOD-FP), MAE, RMSE, 95th-percentile |Δh|
  - peak wet area (km²) and the wet-area time series from the frames
- **Reading.** Treat the results as follows:
  - the like-for-like pair should reach CSI ≥ 0.7 with a depth bias inside ±10 cm
  - lower CSI concentrated on steep cells or along channels points to the θ/Froude settings or the channel treatment
  - a uniform dry bias of the production w4 run against LISFLOOD-FP `LF_LOSS=none` is expected (losses) and is not a solver error

  These are working thresholds, to be revised after the first pair.

## Open risks
- **Build.** The build switch names are unverified (official guide not reachable from the sandbox). The first log shows whether CUDA and NetCDF were turned on. A NetCDF-less build would fail the probe on `dynamicrainfile`.
- **GPU feature support.** It is not confirmed that `dynamicrainfile`, `bcifile FREE`, `manningfile` and `startfile` are all honoured by the **GPU** ACC solver. If the CUDA probe or run fails, rerun on the CPU build: remove `cuda` and expect hours rather than minutes at 20 m. 30 m is the fallback.
- **Rain conventions.** If the probe fails, the script assumes forward stamps, y ascending and mm, and records that assumption in `meta.rain_probe.failed`.
- **Output format.** If a GPU build writes outputs in a format other than ESRI ASCII `.max`/`.wd`, `max_depth()` stops with the list of files it found.
- **Zenodo.** The archive is 348 MB and the download is rate-limited. `LF_ZENODO=<record>` overrides the record.
