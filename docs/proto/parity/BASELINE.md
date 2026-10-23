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
