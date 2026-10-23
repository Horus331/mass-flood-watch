# Rain forcing for flash floods: sub-hourly timing and gauge adjustment

**Verdict.** Keep both options opt-in and leave the default as it is (hourly MRMS MultiSensor QPE Pass2).

* **Sub-hourly forcing (`LF_RAIN_DT=5`)** works as designed. It keeps every hourly total exactly, its timing inside the hour matches ASOS 1-min gauges about twice as well as an even split, and it raises peak forcing rates 1.3–2.6× (median 15-min rate over the hourly rate). It still **does not change the flood answer** at 20 m. Peak depths move by about 1 cm, no extra labelled site is caught on any of the 7 storms, the flagged share rises slightly (so lift falls), and gauge rise and peak timing are unchanged.
* **Gauge adjustment (`LF_RAIN_GAUGE=idw`)** does change results. On the two storms where Pass2 under-reads the daily gauges (aug2021 ×1.32, jul2021 ×1.22) it catches 3 + 1 more sites and fixes the Millbury rise. But it also flags more roads (lift falls on the 3 storms that already caught sites) and overshoots Northbridge. It needs next-morning CoCoRaHS reports, so it is **hindcast-only** and cannot drive the live forecast.
* **Neither option rescues the flash storms.** jul2023, aug2023b, sep2022 and aug2023 stay at 1 of 16 labelled sites under every variant. The gauges show no large radar under-catch on those storms (jul2023 in-box daily gauges / Pass2 = 1.14, Worcester ASOS 3.3 mm against 3.0 mm). The miss is not a rain-timing or rain-amount problem the gauges can see.

Runs: `.github/workflows/rain_test.yml` (mode `sim`), 35 CPU runs, 20 m, catalogue boxes and hours, `LF_PARITY=1`, `LF_LOSS=cn LF_CN_SCALE=0.91 LF_INFIL_MMH=2`, all from the same code, so the hourly baselines are re-run here rather than mixed with older commits (the parity agent had no `docs/proto/parity/catalog/` runs yet). Each run's files are in `docs/proto/rain/runs/<storm>_<variant>/`. Tables: `python proto/rain/rain_compare.py` → `runs.json` + `rain.json`. Gauge check: `python proto/rain/rain_gauges.py` → `gauges.json`, `gauge_factors.json`, from the data that `rain_fetch.py` committed in `docs/proto/rain/data/<storm>/`.

## 1. What was built

### 1.1 `LF_RAIN_DT` (sim/colab/lf_subhourly.py, opt-in; default unchanged)

* Every MRMS product needed is on AWS for all catalogue storm eras (2021–2023): `PrecipRate_00.00` every 2 min (720 files/day), `RadarOnly_QPE_15M_00.00` every 15 min, and `RadarOnly_QPE_01H` every 2 min. Source: `data/<storm>/products.json`.
* Each hour's **rain excess**, after the hourly CN loss and `LF_INFIL_MODE=rain` exactly as in the hourly run, is split into `LF_RAIN_DT`-minute records in proportion to the radar's own accumulation in each sub-interval (`LF_RAIN_SUB=preciprate`, the default, or `qpe15m`). PrecipRate (mm/h) is integrated over ±1 min of each 2-min stamp and binned by overlap. The weights are computed on the native 0.01° grid and interpolated bilinearly, as Pass2 is. Where the radar hour is below 0.1 mm, or less than half the hour has files, the hour stays uniform. In all 7 storms, 0 hours fell back to uniform.
* **Hourly totals are kept exactly.** For example, jul2023's box-mean excess is 1.595 mm in both runs. Only the timing inside the hour changes.
* **DynamicRain units (important).** A new probe run (`probe_subhourly`) puts 360 in one 5-min record. The solver produced 0.360 m, so **LISFLOOD-FP 8.2 reads a record as mm per record interval** (the TUFLOW "rainfall_depth" convention), not as mm/h. The hourly runs could not tell these apart, because with 1-h records the two readings are the same. The writer uses whatever the probe finds, and the run stops if neither reading fits. The probe also confirmed that sub-hourly time stamps are honoured: the forward convention, records stamped at the interval start, a closing zero record, y descending. The 217-record file streams one hour at a time.
* `LF_RAIN_DT_INFIL=sub` (opt-in) takes the 2 mm/h loss out of each 5-min record instead of out of the hour, so a burst keeps more of its water. This is the `dt5i` variant.
* Selftest: `python sim/colab/w9_lisflood.py --selftest` (binning, missing files, weights, writer identical to `write_rain_nc`, probe logic).

### 1.2 `LF_RAIN_GAUGE=mfb|idw` (sim/colab/lf_raingauge.py, opt-in)

The factor is gauge / Pass2 from daily ACIS gauges (CoCoRaHS + COOP) within the box + 0.1°. Each gauge is summed over the gauge-days that overlap the run, using pairs of 10 mm or more. Gauges with a ratio outside 1/3–3 are dropped as QC failures (zero or multi-day reports). The `idw` field weights each gauge's log ratio by inverse distance squared, with a mean-field pseudo-gauge at 10 km. Factors are capped at 0.67–1.5. The field multiplies the hourly Pass2 before the CN loss. Factors are in `gauge_factors.json`, and the runs used `idw`.

## 2. Gauge check (proto/rain/rain_gauges.py → gauges.json)

| storm | hourly gauges (in box) | hourly Pass2/gauge | daily gauges (in box) | daily Pass2/gauge (in box) | radar-only/Pass2 | gauge factor (mfb, n) |
|---|---|---|---|---|---|---|
| jul2023 | 7 (2) | 1.06 | 72 (7) | 0.95 (0.88) | 1.16 | 1.11, 16 |
| aug2023b | 6 (1) | 1.01 | 112 (11) | 1.01 (0.97) | 0.97 | 1.16, 17 |
| sep2022 | 8 (0) | 0.96 | 98 (5) | 0.97 (1.00) | 1.17 | 1.03, 12 |
| aug2023 | 14 (0) | 0.96 | 155 (11) | 0.92 (0.91) | 1.13 | 1.16, 33 |
| sep2023 | 9 (1) | 1.01 | 96 (5) | 0.98 (1.20) | 0.93 | 0.98, 23 |
| aug2021 | 10 (1) | 0.83 | 114 (10) | **0.81 (0.81)** | 1.10 | **1.32**, 24 |
| jul2021 | 11 (1) | 1.04 | 116 (9) | **0.88 (0.79)** | 0.91 | **1.22**, 24 |

* **Hourly gauges** are IEM ASOS 1-min summed to clock hours plus USGS 00045, within 0.35° of the box (wet hours ≥ 0.25 mm). Pooled over 514 gauge-hours, Pass2/gauge = 0.97.
  * By gauge intensity: 0.25–2.5 mm 0.98, 2.5–10 mm 1.05, 10–25 mm 0.94, **≥ 25 mm/h 0.76** (n 12, −9 mm per hour).
  * Pass2 under-reads the heaviest hours, but there are only 0–2 hourly gauges inside a 20 km box. That is too sparse for a local hourly adjustment.
* **Daily gauges** (CoCoRaHS, COOP; 24-h totals against Pass2 over the same 24 h) are dense: 5–11 per box, 12–33 within the box + 0.1°. They support a storm-total mean-field or IDW factor. Pass2 under-reads on aug2021 (Worcester ASOS 80.7 mm against Pass2 58.7 mm) and jul2021. On jul2023, the storm with the "foot of water" reports, the gauges show no under-catch large enough to matter: in-box daily gauges are 1.14 × Pass2, and ASOS Worcester saw 3.3 mm.
* **Timing at ASOS 1-min gauges in the box** (peak 15-min rate in mm/h: gauge / Pass2 split evenly / Pass2 split by radar timing; mean absolute error of the within-hour 15-min shares in hours ≥ 2 mm: even → radar):

| storm, gauge | peak 15-min gauge / even / radar (mm/h) | share error even → radar | radar hits the gauge's peak quarter |
|---|---|---|---|
| jul2023 ORH | 5.1 / 3.0 / 6.1 | 0.125 → 0.072 | 1 of 1 h |
| aug2023b ORH | 40.6 / 21.7 / 34.9 | 0.218 → 0.123 | 3 of 3 |
| sep2023 FIT | 78.2 / 67.4 / 78.2 | 0.126 → 0.053 | 6 of 6 |
| aug2021 ORH | 78.2 / 31.2 / 51.5 | 0.127 → 0.068 | 3 of 5 |
| jul2021 ORH | 25.4 / 18.9 / 25.9 | 0.079 → 0.040 | 4 of 5 |

  The radar split roughly halves the timing error and recovers most of the 15-min peak. Over each box, the median peak 15-min rate after the split is 1.34–2.55× the hourly rate (5-min: 1.65–3.56×) where Pass2 is at least 5 mm/h. Box-maximum rates: for example, jul2023 goes from 34 mm/h (hourly) to 96 (15-min) and 126 (5-min); aug2023 from 70 to 111 and 185 (`gauges.json` `intensity`).

## 3. Flood runs (20 m, LF_PARITY=1)

Each cell shows: labelled sites caught / labelled · flagged share (p_close ≥ 0.5) · lift · gauge rise model/observed (m) · mean |peak timing error|.

| storm | hourly (baseline) | dt5 | dt5i (loss per record) | gauge (idw) | gauge + dt5 |
|---|---|---|---|---|---|
| jul2023 (flash) | 0/5 · 0.07% · – · 0.06/0.24 · 3.2 h | 0/5 · 0.07% · 0.06 · 3.8 h | 0/5 · 0.07% · 0.07 · 3.8 h | 0/5 · 0.07% · 0.06 · 3.2 h | 0/5 · 0.07% · 0.07 · 3.8 h |
| aug2023b (flash) | 0/2 · 0.11% · – · 0.28/0.93, 0.00/0.21 · 8.5 h | 0/2 · 0.11% · 0.28 | 0/2 · 0.12% · 0.30 | 0/2 · 0.14% · 0.33 | 0/2 · 0.14% · 0.33 |
| sep2022 (flash) | 0/4 · 0.77% · – · 0.00/0.14 · 14.5 h | 0/4 · 0.81% | 0/4 · 0.97% | 0/4 · 0.69% | 0/4 · 0.81% |
| aug2023 (flash) | 1/5 · 1.74% · 11.5 · 0.08/0.27, 0.97/1.10 · 5.8 h | 1/5 · 1.74% · 11.5 · 0.97 · 6.0 h | 1/5 · 1.84% · 10.9 · 1.04 | 1/5 · 2.01% · 10.0 · 1.21 | 1/5 · 2.07% · 9.7 · 1.21 |
| sep2023 (good) | 35/89 · 2.33% · 16.9 · 1.10/1.00, 2.58/2.92 · 0.1 h | 35/89 · 2.44% · 16.1 · same | 35/89 · 2.47% · 15.9 | 35/89 · 2.42% · 16.2 | 35/89 · 2.49% · 15.8 |
| aug2021 (good) | 4/12 · 1.49% · 22.3 · 1.09/1.64, 0.03/0.36, 1.73/1.42 · 5.0 h | 4/12 · 1.74% · 19.2 · 1.13, 0.03, 1.75 | 4/12 · 1.88% · 17.7 | **7/12** · 2.87% · 20.3 · **1.66**, 0.08, 2.37 · 5.3 h | 7/12 · 3.30% · 17.7 · 1.70, 0.10, 2.40 |
| jul2021 (good) | 0/5 · 0.25% · – · 0.39/1.68 · 1.0 h | 0/5 · 0.25% · 0.39 | 0/5 · 0.29% · 0.40 | **1/5** · 0.81% · 24.6 · **0.68** · 0.5 h | 1/5 · 0.83% · 24.1 · 0.68 |

Aggregates (`runs.json` `_aggregate`):

| variant | sites caught, 7 storms (flash) | mean flagged share | mean \|gauge rise error\| | mean \|peak timing error\| |
|---|---|---|---|---|
| hourly | 40/122 (1/16) | 0.97 % | 0.40 m | 5.4 h |
| dt5 | 40/122 (1/16) | 1.02 % | 0.40 m | 5.6 h |
| dt5i | 40/122 (1/16) | 1.09 % | 0.39 m | 5.6 h |
| gauge | **44/122** (1/16) | 1.29 % | **0.36 m** | 5.5 h |
| gauge + dt5 | 44/122 (1/16) | 1.39 % | 0.36 m | 5.7 h |

Report points wet ≥ 0.3 m within 300 m (`points.json`; random road points in brackets). With the gauge adjustment, jul2021 goes from 0.20 to **0.80** (random 0.05 → 0.13) and aug2021 from 0.56 to 0.69 (random 0.22 → 0.36). With dt5 nothing changes beyond ±0.07.

**Why sub-hourly timing barely matters here.** Compared cell by cell with the hourly run, dt5 raises the wet-cell peak depth by 0.1–1.1 cm on average (p99 1–6 cm). Land ≥ 0.3 m grows by 0.4–6 %. The 20 m surface spreads and stores a 15-min burst, so the peak depth on a road segment, and the stream rise at a 20–200 km² gauge, are set by the hourly volume, not by the burst shape. Moving the 2 mm/h loss to the 5-min records (dt5i) keeps a little more water in the bursts: the flagged share goes up by 0.05–0.2 points, but no new sites are caught. The gauge peak-timing errors (3–14 h on the flash storms) are far larger than anything inside an hour, so they come from elsewhere: baseflow, channels and routing.

## 4. Recommendations

1. **Default stays hourly Pass2.** `LF_RAIN_DT=5` costs about 4 min of radar download on Actions and a rain file 12× larger (217 records). It gives no detection gain, so it is not worth making the default. Keep it for studies of short-duration hazards, where the burst itself matters: kerb inlets, underpasses, velocity and hazard (`LF_VOUT`), and finer grids.
2. **Gauge adjustment stays an opt-in hindcast tool.** It is the only rain change that moved results (+4 sites, rise error −0.05 m), and only where Pass2 under-reads the CoCoRaHS network (aug2021, jul2021). Before using it for any catalogue numbers, check it against a blind split, for example factors from gauges outside the box only. Report it next to the hourly run, never instead of it. It cannot run live: the reports arrive at about 07 local the next day.
3. **For the flash storms, look beyond rain.** The gauges agree with Pass2 there to within about 10 %, and the radar timing is already as sharp as it gets. The remaining candidates are drainage capacity and inlet clogging, the CN loss on urban pervious soils, and the 20 m terrain at the reported sites.

## 5. Files

* `sim/colab/lf_subhourly.py`: radar weights, sub-hourly probe, streaming writer. `sim/colab/lf_raingauge.py`: gauge factor field. `sim/colab/w9_lisflood.py`: hooks only (`LF_RAIN_DT`, `LF_RAIN_SUB`, `LF_RAIN_DT_INFIL`, `LF_RAIN_GAUGE`, `LF_RAIN_GAUGE_FILE`/`_CAP_LO`/`_CAP_HI`/`_R0_KM`). Metadata go in `inputs.rain_subhourly` / `inputs.rain_gauge_adjust`. Defaults are unchanged.
* `proto/rain/rain_fetch.py` (Actions, `rain_test.yml` mode `fetch`), `proto/rain/rain_gauges.py`, `proto/rain/rain_compare.py`.
* `docs/proto/rain/data/<storm>/`: products, gauges, and native MRMS crops (Pass2, PrecipRate 2-min, QPE 15M). `gauges.json`, `gauge_factors.json`, `runs.json`, `rain.json`, `runs/<storm>_<variant>/`.
* Caveats:
  * Gauge factors are fitted on the same storms they are tested on.
  * ACIS observation hours are taken as local standard time.
  * The ASOS timing check uses only gauges inside the box (one per storm).
  * The `aug2021` catalogue box is the Worcester blind-test box `168000,875000,188000,895000`.
