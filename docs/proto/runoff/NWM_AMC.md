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
| Turing scoring | `proto/turing/collect_group.{py,slurm}`, queue kind **`collect_group`** (env `GROUP`, `DEST`, `FORCE`; values pattern-checked in the script too) | Scores finished `run_storm` results `results/<GROUP>_<arm>_<storm>/` with `score_v2` and `score.py`, and pushes small json files (about 15 kB a run) to `DEST` |
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
- `collect_group.py` + `nwm_amc_score.py` were dry-run on copies of three catalogue runs: they collect, compare and give the verdict.

## 2. What is queued (branch `turing-queue`, commit 81d631a1, submitted by the 16:25Z tick on 31 Oct 2026)

- 50 `run_storm` requests, `amcnwm_base_<storm>` and `amcnwm_nwm_<storm>` for the 25 catalogue storms (settings in PREREG §4; partition
  quick, 6 h, 96 GB, 1 GPU), Slurm jobs 2439666 onward.
- 5 `collect_group` requests, `amcnwm_collect_1` … `_5`. Each runs after its 10 runs (5 storms × 2 arms) and pushes
  `docs/proto/runoff/nwm_amc/runs/amcnwm_<arm>_<storm>.{score_v2,gauges,meta}.json` to main.

**Check progress.**

    git fetch origin turing-queue && git show origin/turing-queue:STATUS.md | grep amcnwm
    ls docs/proto/runoff/nwm_amc/runs/ | grep -c score_v2      # 50 when complete (after git pull)

**If a run failed.** Its batch's `collect_group` is rejected ("a dependency failed"). Re-queue the failed run unchanged under a new id (for
example `amcnwm_nwm_jul2019_r2`, but keep `NAME` the same). Then add a sweep with no `after`:
`{"id": "amcnwm_collect_sweep1", "kind": "collect_group", "env": {"GROUP": "amcnwm", "DEST": "docs/proto/runoff/nwm_amc/runs"}}`. The
sweep scores every finished `amcnwm_*` folder that is not collected yet.

**Score (when all 50 are in).**

    python proto/runoff/nwm_amc_score.py          # -> docs/proto/runoff/nwm_amc.json + table; prints VERDICT

Then fill §3 below exactly as the PREREG §5 rule says (adopt only if `verdict.adopt` is true).

## 3. Results

Pending.
