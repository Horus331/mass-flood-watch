# Consistent CPU baseline at LF_PARITY=1 (in progress)

## 1. CN-scale recalibration: fixed before any run

* **Storm and box:** sep2023 on the original Leominster box `168000,908000,188000,928000`, 48 h, 20 m (the box of the old headline run
  `leominster_sep2023_gpu`). Chosen over the catalogue box (`162000…182000 E`, 36 h) because the Leominster gauge 01094500 lies 244 m from the
  catalogue box's free east edge, so its rise there depends on the boundary (PARITY.md 2.3). Both gauges are well inside this box.
* **Settings:** `LF_PARITY=1` (`LF_INFIL_MODE=rain`, `LF_INIT_TSTEP=1`), `LF_LOSS=cn`, AMC II, `LF_INFIL_MMH=2`, `LF_QOUT=1`, `LF_VOUT=1`, CPU (Actions).
* **Grid:** `LF_CN_SCALE` in {0.85, 0.88, 0.91, 0.94, 0.97, 1.00}.
* **Objective:** minimise `mean_abs_rise_error_m` from `proto/score.py` over Fitchburg 01094400 and Leominster 01094500 (values as rounded by
  `score.py`, 0.01 m). Tie (equal at 0.01 m) → lower `mean_abs_peak_timing_error_interval_h` (gap-aware peak timing). Still tied → the value
  closest to 0.91 (the current setting).
* Label recall, flagged share and lift are reported alongside and are **not** used to choose.

Runs: `.github/workflows/parity_test.yml` with `dest=docs/proto/parity/calib` → `docs/proto/parity/calib/leo48_cn<scale>/`.

### Result

All six runs: sep2023, Leominster box, 48 h, `LF_PARITY=1`, CPU. Observed rises: Fitchburg 1.00 m, Leominster 2.92 m. Strict labels are scored against `labels_sep2023_leominster.csv`, with 89 sites matched.

| `LF_CN_SCALE` | Fitchburg rise (m) | Leominster rise (m) | **mean abs rise error (m)** | bias (m) | mean abs peak timing, gap-aware (h) | rise50 timing (h) | sites caught / 89 | flagged share | lift |
|---|---|---|---|---|---|---|---|---|---|
| 0.85 | 0.86 | 3.22 | **0.22** | +0.08 | 0.4 | 0.6 | 35 | 1.76 % | 14.4 |
| **0.88** | 0.96 | 3.32 | **0.22** | +0.18 | 0.4 | 0.6 | 35 | 1.97 % | 12.8 |
| 0.91 | 1.07 | 3.42 | 0.29 | +0.29 | 0.1 | 0.6 | 35 | 2.20 % | 11.5 |
| 0.94 | 1.18 | 3.51 | 0.39 | +0.39 | 0.1 | 0.5 | 35 | 2.45 % | 10.3 |
| 0.97 | 1.29 | 3.60 | 0.48 | +0.48 | 0.1 | 0.4 | 37 | 2.76 % | 9.7 |
| 1.00 | 1.40 | 3.69 | 0.58 | +0.58 | 0.1 | 0.4 | 37 | 3.01 % | 8.9 |

**Chosen value: `LF_CN_SCALE=0.88`.** The pre-set rule decided it. 0.85 and 0.88 tie on the objective at 0.22 m and on peak timing at 0.4 h, so the last tie-break, the value closest to 0.91, picks 0.88. The objective is flat at the low end. Lower scales cut Fitchburg's rise below the observed value while Leominster stays too high, so the two gauges pull in opposite directions. The scale cannot fix both at once, and the gauge data do not pin the scale more tightly than about 0.85–0.88. At the converged step, the old ×0.91 over-predicts both gauges (+0.29 m). It was tuned at the default step, where the catalogue box put the Leominster gauge 244 m from a free edge and the recession oscillated. Labels did not decide anything here. Recall is flat at 35/89 from 0.85 to 0.94, and only the flagged share moves.
