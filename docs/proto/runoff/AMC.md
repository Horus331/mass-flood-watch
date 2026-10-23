# T4: antecedent moisture in the curve-number loss (closed 23 Oct 2026: no variant adopted, defaults unchanged)

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

## 1. Results (final, 23 Oct 2026)

**Scoring note (deviation from §0, procedural only).** The label set changed after §0 was written. aug2021 gained 1 site and aug2026 gained 3
news-sourced sites, and the catalogue runs for aug2021, aug2026 and `worcester_aug2021_48h` were rerun with identical settings and identical
hydraulics to rebuild their matches (`docs/proto/scoring/BASELINE_v2_expanded.md`). The candidate runs still carried the old matches files, so
`score_v2.compare` refused them ("site lists differ"). `amc_compare.py` now scores **both arms against the current labels**. The baseline is the
catalogue as it now stands. Each candidate run takes its label→segment matches from its catalogue counterpart (`load_current`, remapped by
segment id). The matching is pure geometry on the same box and resolution, so it is the same for every arm. OOS-7 therefore has **32 sites**
(was 29) and the baseline hits **6/32** (was 5/29). A and B1 were rescored the same way, so all four variants share identical site lists. Both
scripts now use an explicit list of the pre-registered runs (`T4_RUNS` / `T4_PRIMARY`), so the 16 label-expansion storms later added to
`docs/proto/parity/catalog/` cannot enter the T4 verdict. Nothing else in §0 changed.

Made by `proto/runoff/amc_compare.py` (closures and pooled gauges) and `proto/runoff/cn_loso.py` (C fit). Gauge columns pool all 16 USGS rises
on the 9 primary runs. "storm-mean" is the §0 objective, the mean over storms of each storm's mean |rise error|. The closure columns are
`score_v2.compare` on OOS-7 at the top 3 % flagged, with the condition-2 lower bound at α = 0.05/4. Detail is in `amc.json` (A), `infil1.json`
(B1), `infil0.json` (B0), `loso.json` (C) and `cn_loso.json` (C fit). In those files the candidate arm's key is `auto`.

| variant | gauge MAE all (m) | bias (m) | storm-mean MAE | Elsa+Ida MAE (3) | other 7 MAE | OOS-7 hits @3 % (recall) | Δ recall [lower, α=.0125] | FSS300 Δ | rule hits OOS-7 / lift | conditions failed | adopt |
|---|---|---|---|---|---|---|---|---|---|---|---|
| default (parity catalogue) | 0.445 | −0.42 | 0.464 | 1.11 | 0.29 | 6/32 (0.188) | – | – | 4/32 / 5.4 | – | – |
| A `LF_CN_AMC=auto` | 0.554 | −0.50 | 0.558 | 1.24 | 0.40 | 7/32 (0.219) | +0.031 [0.000] | −0.002 | 4/32 / 6.3 | gain, CI, FSS | **no** |
| B1 `LF_INFIL_MMH=1` | 0.417 | −0.35 | 0.436 | 1.02 | 0.28 | 6/32 (0.188) | 0.000 [0.000] | −0.001 | 6/32 / 6.9 | gain, CI, FSS | **no** |
| B0 `LF_INFIL_MMH=0` | **0.394** | −0.27 | **0.404** | **0.91** | **0.28** | 7/32 (0.219) | +0.031 [0.000] | +0.001 | 6/32 / 5.8 | gain, CI | **no** |
| C NWM-wetness CN scale, LOSO on gauges | 0.457 | −0.13 | 0.454 | 0.92 | 0.35 | **9/32 (0.281)** | **+0.094** [0.000] | **+0.006** | 7/32 / 5.5 | CI | **no** |
| C0 (b = 0, LOSO global scale; gauges only, interpolated) | – | – | 0.453 (interp.; base 0.465, C 0.455) | – | – | not run (§0) | | | | | – |

No storm loses a site under any variant (worst per-storm change 0), and the rule lift stays at ≥ 0.8 × baseline under all four. The dev storms are
in-sample and never pooled into the decision: sep2023 is 30/79 at baseline and stays there under B0, B1 and C, but drops to 29 under A. aug2021 goes from 3 to 2 (A), 4 (B1), 4 (B0) and 6 (C).

**A: auto-AMC. Do not adopt.** Elsa has P5 = 29.7 mm and Ida 8.6 mm. Both fall in AMC I, so the standard NEH-4 rule makes them drier. Elsa's
Millbury gauge goes from −1.32 to −1.36 m, and Ida's goes from −1.24 to −1.58 m. sep2023 (P5 32.8 mm, AMC I) breaks its calibration: gauge MAE
rises from 0.23 to 0.71 m and rule hits fall from 29 to 26. The OOS-7 +1 is jul2021 at 3 % share, which is ranking noise: rule hits are
unchanged. 5-day rain does not capture why Elsa and Ida were wet. Elsa's wetness is 10-day rain (P10 129 mm). Ida's is the river baseflow left
by Henri, 9 days before.

**B1: 1 mm/h. Do not adopt.** The gauges improve (all −6 %, Elsa+Ida −8 %) and the rule catches +2 OOS-7 sites (aug2026, sep2021). Recall at
3 % is unchanged, and FSS drops by 0.0006.

**B0: no constant infiltration. Do not adopt. It is the best gauge variant.** All-gauge MAE −11 % (0.445 → 0.394 m), storm-mean −13 %,
Elsa+Ida −18 % (1.11 → 0.91 m), bias −0.42 → −0.27 m. It has no free parameter. The other 7 storms also improve (0.29 → 0.28), but some gauges
now over-predict (sep2023 01094400 +0.31 m, aug2021 01110500 +0.43 m). Closures: +1 OOS-7 site (jul2021), +2 rule hits, FSS +0.001. The gain
condition fails (+0.031 < 0.05) and so does the CI (lower bound 0).

**C: wetness-scaled CN. Do not adopt. It is the best closure variant, but only condition 2 fails, and it is worse on gauges.** All-9 fit:
a = 1.035, b = +1.75 per unit θ. The fold slopes are all positive (wetter soil, higher CN, as expected), but 4 of 9 folds sit on the b = +2 edge
of the search grid. The held-out scales range from 0.88 (sep2022, θ 0.54) to 1.12 (jul2023, sep2023). OOS-7 recall goes from 6/32 to 9/32
(jul2021 +2, jul2023 +1), which passes the 0.05 gain bar, and FSS +0.006. The paired two-stage bootstrap lower bound is 0.000. It is still 0.000
at α = 0.05 and 0.10, because all 3 gained sites come from 2 small storms. Gauges: Elsa+Ida −17 %, and the bias almost vanishes (−0.13 m), but
all-gauge MAE gets worse (0.445 → 0.457). sep2023 goes from 0.23 to 0.61 m at scale 1.12, and its rule share doubles (2.2 % → 4.3 %, lift 10.0 →
5.6). So the deployed rule's calibration would have to be revisited if C were adopted. LOSO on the gauges themselves is a near-tie: C 0.455, C0
0.453, base 0.465 (storm-mean, interpolated). The θ slope adds nothing over a single recalibrated global scale on the gauge objective. C's
closure gain therefore cannot be told apart from "CN a bit higher everywhere".

## 2. Verdict (PROTOCOL.md §5, k = 4, α = 0.05/4)

**No T4 variant is adopted. Defaults stay as they are (`LF_CN_AMC` II, `LF_INFIL_MMH=2`, `LF_CN_SCALE` per the catalogue).** None of the four
has a paired-bootstrap lower bound above 0 on OOS-7. C is the only one that passes the gain condition. The T4 target was Elsa/Ida rise MAE −30
to −50 %. The best result is −18 % (B0) or −17 % (C). That is a real but partial fix: antecedent wetness explains part of the Elsa/Ida
under-prediction, not most of it. The rest is plausibly baseflow and channel initial conditions, which a CN loss cannot represent.
Recommendations carried forward: (i) B0 (`LF_INFIL_MMH=0`) is the zero-parameter gauge improvement. Re-test it under PROTOCOL v2 on the
held-out 23 rather than adopting it here. (ii) C's signal (positive θ slope, +3 OOS-7 sites) is worth one pre-registered retest on the larger
pool, with the b grid widened and the rule recalibrated jointly. (iii) Elsa/Ida need a baseflow / initial-stage term (T-next), not a loss
tweak.

