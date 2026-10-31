# Pre-registration: NWM soil saturation as the antecedent-wetness input of the curve-number loss (`LF_CN_AMC=nwm`)

Written and committed **31 Oct 2026, before any run of either arm below was started or scored.** It follows `docs/proto/PROTOCOL.md` v2
(held-out 23 decision set, §5a ranking route). Nothing here may change after the first run is queued. If something has to change for a
technical reason, the change is logged in `NWM_AMC.md` as a deviation, with the reason, before any score is looked at.

## 1. Hypothesis

The calibrated model uses NRCS curve numbers at a fixed AMC II × 0.88 for every storm (calibrated on Sept 2023 Leominster). The 5-day-rain
AMC rule (`LF_CN_AMC=auto`) was tested on 23 Oct 2026 and not adopted (`AMC.md`): 5-day rain does not capture why the soil was wet. NOAA
National Water Model soil saturation is a direct, physically based estimate of the antecedent state. **H1:** a continuous CN adjustment from
the NWM top-soil saturation at the run start (`SOILSAT_TOP` at t0, box mean), mapped as fixed in advance below, improves held-out site
recall at the 3 % budget without degrading the USGS gauge rises. **H0:** no improvement (the verdict rule in §5 decides).

## 2. The input (fixed; computed on Actions before this file, `docs/proto/runoff/nwm_soilsat.json`)

`proto/runoff/nwm_soilsat.py storms` (workflow `nwm_soil.yml`, mode `storms`, main commit e868a5b0). For each catalogue storm
(`docs/proto/parity/catalog/<storm>_<area>_20m/config.json`: box, hours; t0 from `docs/proto/obs/catalog.json`) the box mean of
`SOILSAT_TOP` (fraction of saturation of the top 40 cm, NWM 1 km cells whose centre lies inside the 20 × 20 km box, ~370 cells):

- **Primary source: the NWM operational analysis** (`analysis_assim`, `land`, `tm00`) at the hour t0, from the public archive
  (Google Cloud `national-water-model`, then AWS `noaa-nwm-pds`). It covers 23 of the 25 storms, including the calibration storm.
- **Fallback: the NWM v3.0 retrospective** (AWS `noaa-nwm-retrospective-3-0-pds`, 3-hourly `LDASOUT`, the last step at or before t0). It
  ends on 1 Feb 2023 and has **no `SOILSAT_TOP`**, so it is rebuilt as the 0.1/0.3 m-weighted `SOIL_M` of layers 1–2 divided by each cell's
  porosity. The porosity is taken from operational files that carry both fields (`porosity = top-40-cm SOIL_M / SOILSAT_TOP`). Two dates
  agree to a median of 0.003 per cell. Used for **may2018 and aug2018b only**: the operational archive has no land file at their t0.
- Missing → the storm would run at AMC II. No storm is missing.

Why the operational analysis is primary and not the retrospective: the brief suggested the retrospective for the history. But it ends
before 8 of the 25 storms, including the calibration storm sep2023. On the 15 storms covered by both, the two sources differ by −0.14 to
+0.13 with no stable sign (`nwm_soilsat.json`, `operational.mean` vs `retrospective.mean`), and that offset is as large as the spread
between storms. Mixing sources around the calibration anchor would therefore move storms by source rather than by wetness. The
operational analysis is the same product the live system reads (`ground_state.py`) and the one the calibration value comes from. Its
known weakness is that the NWM version changed over 2018–2026 (v1.2 → v2.0 → v2.1 → v3.0), which is reported as a limitation.

| storm | role | t0 (UTC) | SOILSAT_TOP | source | CN of an HSG-C cell (73 at AMC II) → |
|---|---|---|---|---|---|
| sep2023 | dev (calibration) | 2023-09-11 16 | 0.7262 | operational | 73.0 (unchanged by construction) |
| aug2021 | dev | 2021-08-19 09 | 0.6587 | operational | 68.4 |
| jul2021 | OOS-7 | 2021-07-09 08 | 0.7254 | operational | 72.9 |
| sep2021 | OOS-7 | 2021-09-01 18 | 0.6911 | operational | 70.6 |
| sep2022 | OOS-7 | 2022-09-05 06 | 0.5434 | operational | 61.9 |
| jul2023 | OOS-7 | 2023-07-14 08 | 0.7715 | operational | 76.4 |
| aug2023 | OOS-7 | 2023-08-08 07 | 0.6828 | operational | 70.0 |
| aug2023b | OOS-7 | 2023-08-18 05 | 0.7168 | operational | 72.3 |
| aug2026 | OOS-7 | 2026-08-03 04 | 0.6524 | operational | 68.0 |
| may2018 | NEW16 | 2018-05-15 14 | 0.5420 | retrospective (12Z) | 61.8 |
| aug2018b | NEW16 | 2018-08-11 08 | 0.6460 | retrospective (06Z) | 67.6 |
| sep2018 | NEW16 | 2018-09-18 06 | 0.6176 | operational | 65.9 |
| sep2018w | NEW16 | 2018-09-18 07 | 0.6098 | operational | 65.5 |
| sep2018m | NEW16 | 2018-09-18 08 | 0.6133 | operational | 65.7 |
| sep2018b | NEW16 | 2018-09-26 18 | 0.7229 | operational | 72.8 |
| jul2019 | NEW16 | 2019-07-06 14 | 0.5988 | operational | 64.9 |
| aug2019 | NEW16 | 2019-08-07 19 | 0.6529 | operational | 68.1 |
| sep2019 | NEW16 | 2019-09-02 14 | 0.5904 | operational | 64.4 |
| jun2020 | NEW16 | 2020-06-28 14 | 0.5092 | operational | 60.1 |
| jun2020b | NEW16 | 2020-06-28 16 | 0.5415 | operational | 61.8 |
| aug2020b | NEW16 | 2020-08-27 11 | 0.6855 | operational | 70.2 |
| jul2021b | NEW16 | 2021-07-17 14 | 0.7514 | operational | 74.9 |
| jul2023b | NEW16 | 2023-07-10 08 | 0.6978 | operational | 71.0 |
| jul2023c | NEW16 | 2023-07-16 07 | 0.7062 | operational | 71.6 |
| jul2023d | NEW16 | 2023-07-21 15 | 0.7237 | operational | 72.8 |

These are inputs, not scores. The same numbers (from slightly different cell sets) were already public in `AMC.md` and
`antecedent_new16.csv` before this test. Note what they imply: the calibration storm is wetter than 22 of the other 24, so the mapping moves
most storms toward drier soil (lower CN). That consequence is accepted in advance.

## 3. The mapping (fixed; `sim/colab/lf_nwm_soil.py`, w9 block delimited `LF_CN_AMC=nwm`)

With CN_II the composite CN that `LF_LOSS=cn` builds today (HSG + NLCD impervious, per 20 m cell, before `LF_CN_SCALE`):

    S_II = 25400 / CN_II − 254                       (mm, TR-55 potential retention)
    S    = S_II · (1 − θ) / (1 − θ_cal)              θ = SOILSAT_TOP of the storm, θ_cal = 0.7262 (sep2023)
    CN   = 25400 / (254 + S), clipped to [CN_I, CN_III] of the same cell (Chow, Maidment & Mays 1988 closed forms)

Then `LF_CN_SCALE` (0.88) and the water-cell override are applied, unchanged.

- **Form, from the literature.** Retention S is the unfilled part of the soil store, so it falls linearly as antecedent soil water rises.
  This is the soil-moisture-accounting reading of SCS-CN (Mishra & Singh 2002, 2003; Michel, Andréassian & Perrin 2005, *Water Resour.
  Res.* 41, W02011, [doi:10.1029/2004WR003191](https://doi.org/10.1029/2004WR003191)). S → 0 at saturation, and the clip keeps CN inside
  the NEH-4 AMC I–III envelope.
- **Anchor, from the calibration storm only.** `LF_CN_SCALE = 0.88` was calibrated at AMC II on sep2023, so CN_II is assigned to
  sep2023's own θ. The sep2023 nwm run therefore has exactly the baseline CN, which also gives a solver-reproducibility control.
- **No free parameter.** Nothing was fitted to any storm's labels, gauges or scores. In particular the variant-C slope of `AMC.md` (fitted on
  OOS-7 gauges) is **not** used. One box-mean θ per storm is used, not per-cell 1 km values (a per-cell variant is not part of this test).
- Default path: with `LF_CN_AMC` unset (or I / II / III / auto) the CN array is byte-identical to main before this change. This was checked
  by executing the old and new CN block on the same synthetic inputs (`/tmp` harness, reported in `NWM_AMC.md`), and `w9_lisflood.py
  --selftest` passes (35 checks).

## 4. Arms and runs (Turing GPU, the same solver for both arms; PROTOCOL §3)

The arms are identical except for one variable. Each storm runs on its catalogue box and hours at RES 20 with `LF_PARITY=1 LF_LOSS=cn
LF_CN_SCALE=0.88 LF_INFIL_MMH=2 LF_QOUT=1 LF_VOUT=1 PUBLISH=0` (= the parity catalogue settings), queued as `run_storm` with
`NAME=amcnwm_<arm>_<storm>`:

- **base**: nothing else (AMC II).
- **nwm**: `LF_CN_AMC=nwm LF_NWM_SOILSAT_JSON=docs/proto/runoff/nwm_soilsat.json`.

Storms: all 25 primary catalogue storms, i.e. the held-out 23 (decision set) plus sep2023 and aug2021 (dev, reported separately). That makes
50 runs. Both arms are re-run on Turing (GPU) rather than reusing the CPU parity catalogue, because PROTOCOL §3 requires the same solver.
`worcester_aug2021_48h` is not run.

Scoring path: `proto/turing/collect_group.py` (queue kind `collect_group`) scores every finished run on Turing with `score_v2.score_run`
on `flood_meta.json` + `segments.geojson` only. The universe is the segments of `segments.geojson`, and labels are matched by score_v2's
own strict 30 m rule. This is the same for both arms, so the comparison is paired. `features_<storm>.csv` / `matches_<storm>.json` are not
used, because concurrent jobs can overwrite them through the shared `docs/proto/ml/` path. Gauges come from `proto/score.py`. The small json
files are pushed to `docs/proto/runoff/nwm_amc/runs/`. The comparison is made by `proto/runoff/nwm_amc_score.py`.

**District 4–6 transfer pool: not included.** PROTOCOL "Transfer test" forbids any District 4–6 storm in a `--compare`, a fit or a
decision, and those runs need the OSM road pipeline of `transfer_d456.py`, which `run_storm` does not have. A later, separate
pre-registration could report the nwm arm on that pool descriptively.

## 5. Metrics and verdict rule (k = 1)

Primary, on the held-out 23, box-wide: **site recall at the top 3 % flagged**, with
`score_v2.compare(BASE, CAND, rule = ADOPT_V2 (level share), α = 0.05 / 1)` (= `score_v2.py --compare --protocol v2 --k 1`).

**Adopt `LF_CN_AMC=nwm` only if all of these hold:**

1. PROTOCOL v2 §5a, all five conditions:
   - pooled gain ≥ +0.04;
   - **one-sided 95 % lower bound (= lower end of the 90 % two-sided CI) of the paired two-stage bootstrap difference > 0**;
   - ΔFSS300 at 3 % ≥ 0;
   - no held-out storm with ≥ 3 sites loses more than 1 site;
   - rule lift ≥ 0.8 × base.
2. **Gauges:** the held-out storm-mean USGS rise MAE (mean over held-out storms of `score.py` `mean_abs_rise_error_m`) of nwm ≤ **1.10 ×**
   base.
3. All 23 held-out storms are present in both arms. If a run fails for a technical reason it is re-queued unchanged. If it still cannot be
   run, the verdict is "incomplete", not a pass.

Reported, not deciding: OOS-7 and NEW16 sub-pools, rule site recall and lift, recall at the other shares, all-gauge MAE and bias, dev
storms (sep2023 must equal base up to GPU run-to-run noise, which is a control), per-storm CN shift and hits.

The result is written to `docs/proto/runoff/NWM_AMC.md` whatever it is.
