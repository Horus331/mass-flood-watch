# Rain timeline: past 48 h radar + next 48 h forecast (Forecast tab)

The Forecast tab's time slider runs from 2 days ago to 2 days ahead. It plays the rain that fell over District 3 in the past 48 h, then the
forecast rain for the next 48 h, on the same map layer as the storm replays.

- Builder: `proto/rain_timeline.py build --out <dir>` (`selftest` checks the packing without a network).
- Live: the `rain` job of `.github/workflows/forecast.yml` (every 6 h, in parallel with the gate). The publish job copies the result to
  `docs/site/data/forecast_rain/rain.json` + `rain.png` in the cycle's single commit. Test prefixes write `docs/site/data/<prefix>_rain/`.
- Hand test that never commits: `.github/workflows/rain_timeline_test.yml` (inputs `init`, `now`, and `code` for development).

## Frames

- One frame per hour, from now − 48 h to now + 48 h: **97 frames, `step_min` 60, `now_frame` 48** (`past_n` 49 incl. now, `future_n` 48).
- `now` is the whole UTC hour when the job runs. For a dispatched cycle more than 8 h old, `now` is that cycle's issue time.
- **The frame at time t shows the mean rain rate (mm/h) over the hour ending at t.**
  - The `now` frame is the last observed hour.
  - Frame now + 1 h is the first forecast hour.

### Past frames (t ≤ now): NOAA MRMS hourly QPE

- Source: public bucket `noaa-mrms-pds`, native 0.01° grid.
- For each hour, the first product that is posted is used:
  1. **MultiSensor QPE 01H Pass 2**: gauge-corrected, about 1–2 h latency.
  2. **Pass 1**.
  3. **RadarOnly QPE 01H**: available within minutes.
- In practice the older hours come from Pass 2 and the last one or two from Pass 1 or RadarOnly.
- `frame_src` gives the product per frame: `P2`, `P1`, `RO`.
- Hourly QPE is used instead of the 2-min PrecipRate. It is the product the flood model is driven with, and it is a true hourly mean, so an
  hourly frame does not miss a short burst between samples.

### Future frames (t > now): NOAA HRRR

- The 48 h HRRR cycle (00/06/12/18z) is chosen with the gate's rule (`hrrr_rain.latest_cycle`). It is normally the same cycle the gate uses.
- For each hour, the 1-h APCP bucket ending at t is used (forecast hour t − init). These are byte-range reads from the AWS `.idx` files, via
  `sim/colab/hrrr_rain.py`.
- The HRRR is used **raw**, with no 20 km / 90th-percentile neighbourhood. It is interpolated bilinearly in its Lambert plane onto the MRMS cell
  centres. `frame_src` = `HRRR`.
- The cycle is issued 2 to 7 h before `now`, depending on GitHub's schedule delay, and it ends at init + 48 h. Because of this, **the last few
  future frames (typically 2–7) have no forecast**. They are listed in `missing` and drawn as no rain.
- The hours between init and now are shown from MRMS, not HRRR.

## Format (same as the replay rain, `docs/site/build_rain.py`)

- Grid and box:
  - The box is the District 3 model box (`proto/forecast.py` D3_BOX) + 0.35°.
  - `bounds` [[−72.74, 41.59], [−71.07, 43.12]], `w` 167, `h` 153.
  - This is the grid of `docs/site/data/d3_sep2023/rain.json`.
- Atlas packing:
  - Frame f goes to atlas cell f // 3 (row-major, `cols` cells per row; 6 × 6 cells), colour channel f % 3.
  - Byte = round(255·log1p(mm/h)/log1p(150)). The viewer decodes mm/h = expm1(byte/255·log1p(`max_mmh`)). Values of 150 mm/h and above are
    clipped.
- Fields:
  - The replay fields: `start`, `step_min`, `n`, `w`, `h`, `cols`, `rows`, `bounds`, `max_mmh`, `peak_mmh`, `source`, `missing`, `sheet`.
  - Plus: `now`, `now_frame`, `past_n`, `future_n`, `past_source`, `future_source`, `hrrr_init`, `hrrr_horizon_h`, `frame_src[97]`,
    `frame_peak_mmh[97]`, `past_peak_mmh`, `future_peak_mmh`, `district_mean_mm` {`past48h`, `next48h`} (box-mean depth, mm),
    `frame_means`, `built`, `build_s`.
- Size: the PNG is a few kB on a dry day. On a wet day it is a few hundred kB, up to about 1 MB for widespread rain over all 97 frames. This is
  far under the 3 MB budget.

## Failure behaviour

- The builder never raises for missing data. Any hour it cannot fetch is drawn as zero and listed in `missing`. If HRRR fails completely,
  `future_source` says so.
- The `rain` job is `continue-on-error`. If it writes nothing, publish keeps the previous atlas, and its `now` shows its age.
- Either way, the forecast itself (gate, flood model, status) is unaffected.

## Limits

- **The HRRR underestimates local peaks.** Inside past storm boxes, HRRR 6 h maxima from the same morning were often half the observed MRMS
  value or less (Aug 2021: 62 vs 121 mm; Jul 2023: 20 vs 32 mm; `GATE.md`).
  - Convective cells are often displaced by 10–30 km or mistimed by hours.
  - The forecast frames show where and roughly when rain is expected. They are not a reliable peak intensity.
  - The road-closure gate accounts for this with low thresholds and the neighbourhood / time-lagged ensemble (`ENSEMBLE.md`). This map layer
    does not.
- Where the slider crosses `now`, the source changes from observed to forecast. A storm can jump in position or intensity at that frame.
- Hourly means smooth out sub-hourly bursts. A 10-minute 100 mm/h cell shows as about 17 mm/h for that hour. The storm replays use 6-min
  PrecipRate frames for detail.
- MRMS has radar beam blockage and overshoot in the hills of north-west District 3, and gauge correction can lag in Pass 1 / RadarOnly hours.
  The latest one or two hours may be revised upward when Pass 2 arrives in the next cycle.
- The layer is refreshed every 6 h (plus GitHub schedule delay). Between cycles, `now` lags real time by up to about 8 h.
