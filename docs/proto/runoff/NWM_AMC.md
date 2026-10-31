# NWM soil saturation as the antecedent-wetness input (T4 follow-up, 31 Oct 2026)

**Status: runs queued on Turing, results pending. No verdict yet.** The pre-registration is
[`NWM_AMC_PREREG.md`](NWM_AMC_PREREG.md) (main commit c7d43c0f), committed before any run was queued.

## 1. What was built

| piece | file | what it does |
|---|---|---|
| NWM fetcher | `proto/runoff/nwm_soilsat.py`, workflow `.github/workflows/nwm_soil.yml` (modes `probe`, `storms`, `clim`, `live`; the run log is committed to `nwm_logs/<mode>.txt`) | Box statistics of NWM `SOILSAT_TOP` on the 1 km Lambert grid (cells whose centre is inside the box polygon) |
| per-storm input | `docs/proto/runoff/nwm_soilsat.json` | `SOILSAT_TOP` at t0 for the 25 catalogue storms: operational analysis and retrospective side by side, plus the value used (see the PREREG table) |
| climatology | `docs/proto/runoff/nwm_soilsat_clim.json` | District 3 daily mean 1979-02-01 … 2023-02-01 (16 072 days) from the NWM v3.0 retrospective zarr, on the `SOILSAT_TOP` scale |
| live context | `proto/ground_state.py` → `docs/site/data/ground.json`, new key **`soil`** | Latest operational analysis: District 3 mean, cell percentiles, and its percentile in the climatology for ±15 days of the date. Every other key is unchanged, and `soil` does not enter `ground`. `forecast.yml` (publish job) now installs netCDF4 for it |
| model option | `sim/colab/lf_nwm_soil.py` + the delimited `LF_CN_AMC=nwm` block in `w9_lisflood.py` | Continuous CN between CN(I) and CN(III) from the box-mean `SOILSAT_TOP` at t0 (formula and sources in PREREG §3); reads `LF_NWM_SOILSAT_JSON` (no network on Turing) or `LF_NWM_SOILSAT` |
| Turing runner | `proto/turing/run_plan_gpu.slurm`, queue kind **`run_plan_gpu`** (env `PLAN`, `PIN`, `IDXS`; all pattern-checked); plan `proto/turing/plans/amcnwm_v1.json` (`proto/runoff/nwm_amc_plan.py`; plan format and checks from `inlets_plan.py`) | Runs several plan tasks one after another in ONE GPU job, at a pinned commit (a git worktree shared by the tasks), each task in its own `LF_WORK`. Each task: w9 → `prototype.py` → `closure_ml.extract` into a private folder → `score_v2.py --run` + `score.py` → `DONE` / `FAILED` |
| Turing collector | the existing `collect_scores` kind (`proto/turing/collect_scores.slurm`, added for the LF_INLETS test) | Waits until every plan task has `DONE`/`FAILED`, then pushes only small whitelisted files (`score_v2.json`, `score.json`, `points.json`, `flood_meta.json`, `w9_tail.txt`, ≤ 400 kB each) to `docs/proto/runoff/amcnwm_v1/<name>/`, plus `manifest.json` |
| comparison | `proto/runoff/nwm_amc_score.py` | Paired `score_v2.compare` (v2 §5a, k = 1), pooled tables, gauge MAE, the pre-registered verdict → `docs/proto/runoff/nwm_amc.json` |

### Data sources (verified from Actions on 31 Oct 2026)

- **Operational analysis.** `nwm.YYYYMMDD/analysis_assim/nwm.tHHz.analysis_assim.land.tm00.conus.nc`, about 120 MB a file.
  - Live copies: [AWS noaa-nwm-pds](https://noaa-nwm-pds.s3.amazonaws.com/index.html) and [NOMADS](https://nomads.ncep.noaa.gov/pub/data/nccf/com/nwm/prod/). Both returned 200 for the last 3 hours.
  - History: the [Google Cloud `national-water-model`](https://console.cloud.google.com/storage/browser/national-water-model) archive. It has a land file with `SOILSAT_TOP` at t0 for 23 of the 25 catalogue storms (2018-09 → 2026-08). It has none for may2018 or aug2018b.
  - Variables in the v3 file: `SOILSAT_TOP` ("fraction of soil saturation, top 2 layers"), `SOIL_M` (4 layers), `SOIL_T`, snow, `ACCET`, and others.
- **NWM v3.0 retrospective.** [AWS noaa-nwm-retrospective-3-0-pds](https://noaa-nwm-retrospective-3-0-pds.s3.amazonaws.com/index.html), 1979-02-01 03Z → **2023-02-01 00Z**, 3-hourly.
  - Formats: `CONUS/netcdf/LDASOUT/YYYY/YYYYMMDDHH00.LDASOUT_DOMAIN1` (~190 MB a file) and `CONUS/zarr/ldasout.zarr`.
  - The zarr's `SOIL_M` is int32 × 0.01, with chunks of 224 times × 350 × 1 layer × 350.
  - **It has no `SOILSAT_TOP`.** Saturation is rebuilt as the top-40-cm `SOIL_M` divided by a per-cell porosity, and the porosity comes from operational files that carry both fields. The porosity is stable between two dates: median per-cell difference 0.003, mean porosity 0.44.
  - **Coverage of the catalogue:** 17 storms (2018-05 … 2022-09) fall inside it. Of the 25, 8 (jul2023 ×4, aug2023 ×2, sep2023, aug2026) fall after it ends.
- **The two sources disagree by −0.14 to +0.13** on the 15 storms covered by both. There is no stable sign, even within one summer (jun2020: operational 0.13 lower; aug2020b: 0.14 higher), plausibly because of NWM operational version changes (v1.2 → v3.0) and different forcing. This is why the test uses one source (operational) around the calibration anchor (PREREG §2). For the same reason, the live percentile (operational value against the retrospective climatology) is only approximate. It says so in `soil.clim_note`.

### Tested live

- `nwm_soil.yml` mode `live` (run 31 Oct 2026, log `nwm_logs/live.txt`): `ground.json` gained
  `soil = {state: "dry", soilsat_top: 0.6146, valid_utc: 2026-10-31T15:00Z, percentile: 8.7 (1364 climatology days), stats {p5 … p95 over 6534 cells}}`.
  The other keys are unchanged. The step in `forecast.yml` runs with `continue-on-error`, so a failed download only writes `soil.state = "unknown"`.
- Default model path byte-identical. The old (main) and new CN blocks of `w9_lisflood.py` were executed on the same synthetic inputs
  (300 × 400 cells, every HSG, random impervious and water) with `LF_CN_AMC` unset and with II, I and III, `LF_CN_SCALE` unset and 0.88.
  The arrays were identical byte for byte (sha1 equal). `w9_lisflood.py --selftest` passes (35 checks, including the new `lf_nwm_soil`
  checks). The nwm path at θ = θ_cal returns the AMC II CN (checked).
- `nwm_amc_score.py` was dry-run on the `collect_scores` layout, built from three catalogue runs: it compares and gives the verdict.
  `run_plan_gpu.slurm` passes `bash -n`, its index parsing and its env reset between tasks were tested locally, and the plan passes
  `inlets_plan.check`. The runner itself has not run yet: its first run is the queued test.

## 2. What is queued

QUEUE_PLACEHOLDER

**Check progress.**

    git fetch origin turing-queue && git show origin/turing-queue:STATUS.md | grep amcnwm
    git pull && cat docs/proto/runoff/amcnwm_v1/manifest.json      # appears when the collector has pushed: done / failed / missing per task

**Score (when the manifest shows 50 done).**

    python proto/runoff/nwm_amc_score.py          # -> docs/proto/runoff/nwm_amc.json + a table; prints VERDICT

Then fill §4 exactly as PREREG §5 says (adopt only if `verdict.adopt` is true).

**If tasks failed or timed out** (the manifest lists them): re-queue `run_plan_gpu` under a new id, with the same `PLAN` and `PIN` and only
the failed indices in `IDXS` (task *i* is entry *i* of the plan's `tasks`; base = even, nwm = odd). Then queue `collect_scores` again
under a new id, with `WAIT_H`. Nothing else may change (PREREG §5.3).

## 3. Deviation log (procedural; written before any score of either arm was seen)

- **31 Oct 2026, 16:25Z.** The first submission was 50 `run_storm` requests plus 5 `collect_group` collectors (turing-queue 81d631a1).
  - 36 of the 50 were refused by Slurm with `QOSMaxSubmitJobPerUserLimit` (too many jobs per user at once), and their collectors were
    rejected with them.
  - 14 `run_storm` jobs (aug2018b … aug2026, both arms) and `amcnwm_collect_1` were accepted.
  - Fix: one GPU job now runs ten tasks one after another (`run_plan_gpu`), so the 50 runs need 5 Slurm jobs. The jobs run at a pinned
    commit, and both arms of a storm run in the same job, on the same GPU.
  - The 14 accepted `run_storm` runs are **ignored**. The `collect_group` kind and its scripts were removed from main, so
    `amcnwm_collect_1` fails without pushing anything. Those runs stay in `results/amcnwm_*` on Turing and are never scored.
- **Scoring universe** (follows from the runner change). Each task now builds its own `features_<storm>.csv` / `matches_<storm>.json` in a
  private folder, as the LF_INLETS runner does. `score_v2` therefore uses its standard universe (the model's in-box segments) and its
  standard matching, not the `segments.geojson`-only fallback that PREREG §4 chose to avoid the shared-path race. The race no longer
  exists. This is the same for both arms, and no parameter, arm, storm, metric or threshold changed.

## 4. Results

Pending.
