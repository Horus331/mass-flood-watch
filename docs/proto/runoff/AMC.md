# T4: antecedent moisture in the curve-number loss (in progress)

## 0. Pre-registration (written 23 Oct 2026, before any OOS-7 closure score of any variant below was looked at)

Default arm for every comparison: the T0 parity catalogue, reused as published (`docs/proto/parity/catalog/`, `LF_PARITY=1 LF_CN_SCALE=0.88`,
`LF_LOSS=cn`, AMC II, `LF_INFIL_MMH=2`, CPU, git 37177775). The `w9_lisflood.py` default path has not changed since that commit. All variants are
the same cases (9 catalogue storms on their catalogue boxes at 20 m, plus `worcester_aug2021_48h`) with one setting added, CPU on Actions
(`parity_test.yml`). Gauges are scored with `proto/score.py` and closures with `proto/score_v2.py` (PROTOCOL.md §5 adoption rule, OOS-7).
`proto/runoff/amc_compare.py` makes all the tables.

**Antecedent index.** `docs/proto/runoff/antecedent.json` / `.csv` (`proto/runoff/antecedent.py`, run on Actions with `runoff.yml`):

| storm | P5 (mm) | P10 (mm) | NEH-4 AMC from P5 | NWM SOILSAT_TOP at t0 | NWM SOIL_M layer 1 |
|---|---|---|---|---|---|
| jul2021 (Elsa) | 29.7 | 128.9 | I | 0.738 | 0.339 |
| aug2021 | 0.1 | 8.0 | I | 0.640 | 0.280 |
| sep2021 (Ida) | 8.6 | 32.6 | I | 0.689 | 0.317 |
| sep2022 | 2.0 | 25.2 | I | 0.544 | 0.252 |
| jul2023 | 66.4 | 76.0 | III | 0.771 | 0.363 |
| aug2023 | 2.7 | 32.7 | I | 0.686 | 0.310 |
| aug2023b | 24.8 | 71.4 | I | 0.708 | 0.314 |
| sep2023 | 32.8 | 33.1 | I | 0.728 | 0.322 |
| aug2026 | 98.4 | 109.5 | III | 0.653 | 0.291 |

P5/P10 = box-mean MRMS MultiSensor QPE 24H Pass2 over the 5 / 10 days before t0. NWM = operational `analysis_assim` land file at t0
(1 km, box mean, Google Cloud NWM archive). The table was made before any variant run finished.

**Variants (all fixed now):**

- **A. `LF_CN_AMC=auto`**: NEH-4 growing-season class from P5 (< 35 mm I, 35–53 mm II, > 53 mm III), with no free parameter. It is scored
  directly. From the table, 7 storms go to AMC I (drier) and jul2023 and aug2026 go to AMC III. That includes Elsa and Ida, the two storms T4
  was meant to fix, so we expect A to make their under-prediction worse. It is run anyway because it is the standard method and it was set in
  advance.
- **B. Constant infiltration** `LF_INFIL_MMH` = 1 and 0 (default 2). With `LF_PARITY=1` this is subtracted from each hour of rain. These are
  fixed alternatives with no fitting, scored directly.
- **C. Wetness-scaled CN, calibrated LOSO on USGS gauge rises only.** `LF_CN_SCALE_s = clip(a + b · (θ_s − θ̄), 0.88, 1.12)`, with
  θ = NWM SOILSAT_TOP at t0, θ̄ = 0.69 (the 9-storm mean, fixed), AMC II.
  - Grid runs: `LF_CN_SCALE` ∈ {0.88 (the baseline runs), 0.94, 1.00, 1.06, 1.12} on the 9 primary cases (`docs/proto/runoff/grid/cn<scale>/`).
    For each gauge, the rise is interpolated linearly in the scale between grid runs.
  - Objective on the 8 training storms of each fold: the mean over storms of the storm's mean |rise error| (`score.py`, storm-weighted so
    sep2023's 10 gauges do not dominate).
  - Search: a over 0.88–1.12 and b over −2 to +2 per unit θ, on a 0.005 × 0.05 grid. Ties go to smaller |b|, then to a closest to 0.88.
  - The held-out storm is then run at its predicted scale, rounded to 0.01. Those 9 runs (`docs/proto/runoff/loso/`) are the candidate C
    that gets scored on closures.
  - A control C0 with b = 0 (a single LOSO-recalibrated global scale) is reported for gauges from the interpolated grid. It is not run
    separately.
  - Labels play no part in choosing a or b.
- Variants scored on OOS-7 for T4: A, B1, B0, C. That makes k = 4, so the condition 2 lower bound is taken at α = 0.05 / 4 (the 1.25th
  percentile).

The verdict follows in §2 once the runs are in.
