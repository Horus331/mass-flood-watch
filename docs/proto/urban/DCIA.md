# Connected-pavement runoff loss (`LF_LOSS=cn_dcia`): does it fix the urban flash misses?

**Short answer: no.** The physically standard split (directly connected pavement sheds rain minus 2 mm; TR-55 CN only on the pervious part) raises urban runoff as expected, but on the four flash-miss storms the model still catches **1 of 15** labels. That is the same label as before (Glen St, Marlborough). Depth at the 13 missed sites rises by at most 0.06 m, to ≤ 0.07 m, far below a closure. On the five good storms it is roughly neutral: **36 → 37 of 104** labels, flagged segments +10 % (601 → 659), and gauge rise error smaller on 6 of 9 storms (the same on 2, 0.01 m worse on 1). No re-calibration was needed (section 4). Defaults are unchanged.

Code: `sim/colab/w9_lisflood.py` (`cn_dcia_excess`, `dcia_fraction`; `--selftest` checks it against the FINDINGS table). Runs: `.github/workflows/loss_test.yml`, with results in `docs/proto/urban/dcia/<storm>_<variant>/`. Comparison: `python proto/dcia_compare.py` → `docs/proto/urban/dcia.json`.

## 1. Method

Each 20 m cell has total impervious share TIA = NLCD impervious (10 m tiles averaged to 20 m, the same `IMP` that `cn` uses). It is split three ways:

* **DCIA** (directly connected impervious) follows Sutherland (1995), "average" connection: DCIA % = 0.1 · TIA %^1.5 (zero below 1 % TIA). This is the relation used in EPA SWMM / Lee & Heaney (2003) guidance. It gives 0.16 of the cell at TIA 0.3, 0.35 at 0.5, 0.72 at 0.8 and 1.0 at 1.0. `LF_DCIA=sutherland_high` (0.4 · TIA^1.2) and a fixed fraction of TIA (`LF_DCIA=1` = all pavement connected) are also available.
  DCIA excess = cumulative rain − `LF_DCIA_IA` (default 2 mm depression storage).
* **Unconnected impervious** (TIA − DCIA) sheds the same depth onto the pervious part of the cell (run-on, spread evenly).
* **Pervious part**: TR-55 CN on the pervious CN (same HSG table as `cn`: A 36, B 60, C 73, D 79, unknown 77). AMC III is applied if `LF_CN_AMC=III`, then × `LF_CN_SCALE`, clipped to 30–98. Its input is the rain plus the run-on.
* Cell excess = DCIA · Q_imp + (1 − TIA) · Q_perv. Water cells pass the rain through unchanged. Like `cn`, the calculation is cumulative over the event and then differenced to hourly values. A cell with no pavement gives exactly the `cn` result.

Selftest (hand numbers from FINDINGS §2, HSG C, ×0.91). `cn` reproduces the "model runoff" column to ±0.05 mm. `cn_dcia` with `LF_DCIA=1`, minus the pervious term, reproduces the IMP·(P − 2 mm) column. Runoff from one hour of rain (mm):

| TIA | P (mm) 20 / 30 / 45 / 60 / 106 | `cn` | `cn_dcia` (Sutherland) | `cn_dcia` LF_DCIA=1 |
|---|---|---|---|---|
| 0.3 | | 0.0 / 1.3 / 5.9 / 12.8 / 42.4 | 3.0 / 5.1 / 10.5 / 17.9 / 48.0 | 5.4 / 8.5 / 14.7 / 22.5 / 52.8 |
| 0.5 | | 0.4 / 2.7 / 9.0 / 17.6 / 51.1 | 6.4 / 10.5 / 18.4 / 27.8 / 62.4 | 9.0 / 14.1 / 22.8 / 32.6 / 67.5 |
| 0.8 | | 2.0 / 6.5 / 15.6 / 26.6 / 65.5 | 12.9 / 20.4 / 32.5 / 45.2 / 86.6 | 14.4 / 22.4 / 34.9 / 47.8 / 89.4 |

## 2. Runs

These are GitHub Actions CPU runs (LISFLOOD-FP 8.2, OpenMP), one per storm, on the catalogue box at 20 m over the catalogue hours. They use the Turing catalogue settings (`LF_LOSS=cn LF_CN_SCALE=0.91 LF_INFIL_MMH=2 LF_QOUT=1 LF_VOUT=1`, current code with 4-connected breaching) and then the variant on top. Variants:

* `cn`: CPU control at the current default, for all 9 storms.
* `dcia`: `LF_LOSS=cn_dcia` (Sutherland, 2 mm, pervious CN × 0.91).
* `dcia1`: all pavement connected (`LF_DCIA=1`), as an upper bound.
* `cnrep`: `cn` re-run for jul2021, aug2021 and sep2021. Results were identical to the bit, so the CPU runs are deterministic: any difference between `cn` and `dcia` comes from the loss and is not noise.

**The published GPU numbers are not a usable baseline.** On the same boxes, the CPU control at current defaults differs from the published Turing GPU runs (`docs/proto/turing/<id>_<area>_20m`) by much more than "slightly":
* It flags 25–85 % fewer segments on the light storms (jul2023 0.11 % vs 0.65 %, aug2023b 0.12 % vs 0.51 %).
* Its rivers rise much more (Fitchburg in sep2023: 1.60 m vs 0.35 m; observed 1.00 m).

The GPU runs probably come from an older checkout (for example, before 4-connected breaching, or before CN × 0.91 reached the Turing job), or from a CUDA solver difference. Their `flood_meta.json` does not record the git sha. Every comparison below is CPU against CPU. The GPU column is shown for reference only.

## 3. Results per storm

Cell = labels caught / labelled · flagged share (`p_close ≥ 0.5`, `checks.labels_segments.depth_rule`) · lift (recall / flagged share) · mean gauge rise bias (m, model − observed).

| storm | GPU published (cn) | CPU `cn` (control) | CPU `cn_dcia` | CPU `cn_dcia` all connected |
|---|---|---|---|---|
| jul2023 (miss) | 0/5 · 0.65 % · 0 · −0.24 | 0/5 · 0.11 % · 0 · −0.22 | 0/5 · 0.21 % · 0 · −0.22 | 0/5 · 0.30 % · 0 · −0.22 |
| aug2023b (miss) | 0/2 · 0.51 % · 0 · −0.54 | 0/2 · 0.12 % · 0 · −0.51 | 0/2 · 0.41 % · 0 · −0.46 | 0/2 · 0.53 % · 0 · −0.42 |
| sep2022 (miss) | 0/4 · 1.87 % · 0 · −0.14 | 0/4 · 0.79 % · 0 · −0.14 | 0/4 · 0.96 % · 0 · −0.14 | 0/4 · 0.96 % · 0 · −0.14 |
| aug2023 (miss) | 1/4 · 3.58 % · 7.0 · −0.69 | 1/4 · 1.90 % · 13.2 · −0.35 | 1/4 · 2.25 % · 11.1 · −0.28 | 1/4 · 2.38 % · 10.5 · −0.24 |
| sep2023 (good, tuning storm) | 28/78 · 2.80 % · 12.8 · −0.93 | 28/78 · 2.47 % · 14.6 · +0.02 | 28/78 · 2.73 % · 13.1 · +0.08 | 28/78 · 2.78 % · 12.9 · +0.17 |
| aug2021 (good) | 5/12 · 2.24 % · 18.6 · −0.76 | 4/12 · 1.45 % · 23.0 · −0.26 | 5/12 · 2.13 % · 19.6 · −0.14 | 6/12 · 2.36 % · 21.2 · −0.08 |
| jul2021 (good) | 1/5 · 1.22 % · 16.4 · −1.68 | 0/5 · 0.33 % · 0 · −1.39 | 1/5 · 0.67 % · 29.7 · −1.19 | 1/5 · 0.84 % · 23.9 · −1.11 |
| sep2021 (good) | 2/5 · 4.07 % · 9.8 · −1.46 | 3/5 · 3.67 % · 16.4 · −1.02 | 2/5 · 3.12 % · 12.8 · −0.97 | 3/5 · 4.83 % · 12.4 · −0.95 |
| aug2026 (good) | 1/4 · 2.20 % · 11.4 · −0.90 | 1/4 · 1.61 % · 15.5 · −0.32 | 1/4 · 1.82 % · 13.8 · −0.18 | 1/4 · 2.02 % · 12.4 · −0.12 |

Totals. Pooled lift = pooled recall / pooled flagged share.

| | CPU `cn` | CPU `cn_dcia` | all connected |
|---|---|---|---|
| flash misses (4 storms): labels caught | 1/15 | 1/15 | 1/15 |
| flash misses: flagged segments (mean share) | 160 (0.73 %) | 217 (0.96 %) | 241 (1.04 %) |
| good storms (5): labels caught | 36/104 | 37/104 | 39/104 |
| good storms: flagged segments (mean share) | 601 (1.91 %) | 659 (2.09 %) | 828 (2.57 %) |
| good storms: pooled lift | 17.8 | 16.7 | 14.0 |
| gauge mean abs rise error, misses / good (m) | 0.31 / 0.74 | 0.28 / 0.64 | 0.26 / 0.62 |
| effective rain, share of box rain (range over storms) | 10–37 % | 17–40 % | 19–41 % |

Gauges. Mean abs rise error with `cn_dcia` is better on 6 storms, the same on jul2023 and sep2022 (0.22 and 0.14 m: the one gauge in each box barely responds in any run) and 0.01 m worse on aug2021 (Northbridge overshoots 1.59 → 1.78 m against 1.42 m observed). Rise bias moves toward zero on every storm with a responding gauge, but the models stay well under on Elsa and Ida (Millbury 0.29 → 0.49 m vs 1.68 m; 0.87 → 0.97 m vs 2.14 m). sep2023: Fitchburg 1.60 → 1.55 m (observed 1.00 m), Leominster 2.36 → 2.53 m (observed 2.92 m).

Depth at the missed sites (segment depth, m: `cn` → `cn_dcia` → all connected):

| storm | sites |
|---|---|
| jul2023 | Main St 0 → 0 → 0; S Spencer Rd 0.03 → 0.03 → 0.03; Franklin St 0 → 0.01 → 0.01; Shrewsbury St 0.01 → 0.06 → 0.06; Southbridge St 0.01 → 0.07 → 0.07 |
| aug2023b | Route 146 0 → 0 → 0; Providence Rd 0.02 → 0.02 → 0.02 |
| sep2022 | Dresser St 0 → 0 → 0; Oxford 0 → 0.05 → 0.05; Worcester Rd ×2 0.05 → 0.07 → 0.07 |
| aug2023 | W Main St 0.01 → 0.01; Henry St 0 → 0; Ashland St 0.06 → 0.06 (Glen St, the hit: 0.33 → 0.47) |

Good-storm label changes with `cn_dcia`:
* Gained: aug2021 W005 (0.11 → 0.51 m) and jul2021 Cambridge St (0.08 → 0.38 m), both Fred/Elsa sags that fill further.
* Lost: sep2021-01 (0.41 → 0.09 m). That site goes to 1.25 m in the all-connected run, so its depth is set by which way the routing tips, not by the amount of runoff. Single-site changes of this size are within routing sensitivity.

## 4. Re-calibration (step 3): not triggered

`cn_dcia` does not over-wet the good storms:
* Mean flagged share rises 0.18 points (1.91 → 2.09 %), still below the published GPU 2.51 %.
* Gauge rises stay too low on average (good-storm bias −0.59 → −0.48 m).
* On the tuning storm (sep2023), gauge abs rise error improves (0.58 → 0.47 m) at the unchanged pervious CN × 0.91, with the same 28/78 labels.

Lowering pervious CN further would push the gauges the wrong way, and raising it would only add pervious runoff in large storms. So no re-tuning was done, and no per-storm tuning.

## 5. Verdict

* **The CN loss is not what limits the flash misses.** Even with every square metre of pavement connected (`dcia1`, the most runoff this loss family can make), the 13 missed sites get at most 0.07 m and the misses stay at 1/15. 20–30 mm bursts give 6–20 mm of excess on half-to-mostly paved cells. Spread over a 20 m grid with free surface routing, that does not pond 0.3 m on a street. The closures need what the grid lacks: inlet/pipe capacity being exceeded (drains as a real-world bottleneck, the `PROTO_PLUVIAL` idea), sub-20 m street geometry, or more rain than MRMS shows (jul2023). FINDINGS §2(a) is right that the CN step removes most of a short burst, but restoring that water is not enough to make closures at 20 m.
* **Should `cn_dcia` become the default? A qualified yes, at the next full catalogue re-run, not as a fix for the misses.**
  * For: it is the standard urban-hydrology treatment (`cn` lets pavement absorb water). It improves gauge rise error on 6 of 9 storms (the same on 2, 0.01 m worse on 1), including sep2023 at the existing ×0.91. It adds about 10 % more flagged segments for +1 good-storm label.
  * Against: pooled lift on the good storms is about 6 % lower (17.8 → 16.7), and it changes every published baseline. If those baselines must stay comparable, keep `cn`.
  * If adopted, first re-run the GPU catalogue with the current code at both settings. The published GPU numbers differ from current CPU code far more than the `cn` → `cn_dcia` change does (section 2), and that gap is the bigger open issue.
* Do not adopt `LF_DCIA=1`: it adds 38 % more flags than `cn` for +3 labels (pooled lift 14.0).
