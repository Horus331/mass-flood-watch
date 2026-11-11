# Benchmark v3: the model vs six named baselines (10–11 Nov 2026)

Rules: `docs/proto/PROTOCOL_v3.md` (committed c91b0587 before any of this was scored). Code: `proto/bench_v3.py`. Raw: `benchmark_v3.json`.
Full tables: `BENCHMARK_v3_tables.md`. Model = the clean CPU parity runs (`docs/proto/parity/catalog`), the frozen runs scored in
BASELINE_v2_expanded. Test 2 uses the frozen r1 transfer runs (work branch `transfer-d456`) and the SFHA overlaps of HYBRID.md (run 40966174644).
B4–B6 as defined in PROTOCOL_v3 amendment 1 (tuned on Leominster sep2023: peak hour ≥ 85 mm, storm total off; HAND ≤ 0 m). B3 is District 3
only (MassDOT's list covers District 3). All rows for all methods: `BENCHMARK_v3_tables.md`; the tables below are from the first run (M, B1–B3).

## In plain words (all six baselines, 11 Nov 2026)

Share of report sites found when each method flags its top 3 % of roads (chance in brackets):

| method | District 3, 23 held-out storms | Districts 4–6, 81 storms |
|---|---|---|
| **Model** | 20 % | **21 %** |
| NWS flash-flood warnings | 5 % | 9 % |
| FEMA 100-yr zone | 12 % | 7 % |
| MassDOT repeat flood points | 14 % | (District 3 list only) |
| Radar rain threshold (tuned on Leominster) | 5 % | 6 % |
| Terrain only (HAND) | 8 % | 10 % |
| **Static H×V×C** (flood zone + low ground × road type × traffic) | **32 %** | 10 % |
| chance | 7 % | 9 % |

- **Districts 4–6 (never used to build or tune anything): the model beats all five baselines there on CSI, PR-AUC and site recall, every
  difference significant.** The baselines are at or near chance.
- **District 3: the model beats NWS warnings, the rain threshold and terrain alone significantly, is ahead of FEMA and MassDOT but not
  significantly, and is behind the static H×V×C score** (32 % vs 20 % at 3 %; 95 % interval of model minus H×V×C [−0.23, 0.00], just short of
  significant). The likely reason is who reports: in District 3 the reported segments are 25 % arterials against 4 % of all roads, with a
  median traffic of 5,300 vs 1,000 vehicles a day (most District 3 reports come from MassDOT and the news). A score that ranks busy roads
  first finds reports, not necessarily floods. In Districts 4–6, where reports are more varied, the same score is at chance (10 % vs 9 %).
  This is a finding to take seriously, not to explain away: (1) the label set of District 3 is biased to busy roads, and (2) traffic is a
  strong predictor of *reported* closures, which is what an operations user sees.
- **The rain threshold tuned on Leominster (peak hour ≥ 85 mm) almost never fires elsewhere**, so it is near chance; its good Brier score only
  means it predicts "no" everywhere. Brier and BSS reward low predictions when reports are this rare; ranking measures are the ones to read.
- **Probabilities fitted on Leominster do not carry over** (reliability below): the site keeps "k of N".
- **Absolute skill is low.** At its own rule the model catches 3–5 % of reported segments (CSI ≈ 0.02). It ranks roads 2–3× better than
  chance at 3 %.

## Test 1: 23 held-out District 3 storms (65,958 segments in the reported domain, 222 reported; 126,830 segments in the boxes)

| method | POD | FAR | CSI | flagged share | Brier | PR-AUC | ROC-AUC | site recall at model's share (chance) | site recall at 3 % (chance) |
|---|---|---|---|---|---|---|---|---|---|
| Model (p_close) | 0.050 | 0.972 | **0.018** | 0.5 % | **0.0063** | **0.008** | **0.651** | **0.092** (0.014) | **0.204** (0.066) |
| NWS flash-flood warning | 0.658 | 0.996 | 0.004 | 51.0 % | 0.0074 | 0.004 | 0.552 | 0.010 (0.014) | 0.051 (0.066) |
| FEMA 100-yr zone (≥ 30 % of length) | 0.090 | 0.987 | 0.011 | 2.1 % | 0.0114 | 0.006 | 0.602 | 0.057 (0.014) | 0.120 (0.066) |
| MassDOT repeat flood points (≤ 30 m) | 0.014 | 0.857 | 0.013 | 0.0 % | 0.0069 | 0.008 | 0.489 | 0.041 (0.014) | 0.143 (0.066) |

Model minus baseline, 95 % interval over storms (paired bootstrap, 2000 draws; Brier as baseline minus model; * = excludes 0):

| vs | CSI | Brier | PR-AUC | site recall at model's share | site recall at 3 % |
|---|---|---|---|---|---|
| NWS warnings | [+0.003, +0.021] * | [-0.000, +0.002] | [+0.001, +0.008] * | [+0.015, +0.149] * | [+0.042, +0.251] * |
| FEMA zone | [-0.006, +0.019] | [+0.003, +0.006] * | [-0.004, +0.005] | [-0.023, +0.099] | [-0.021, +0.189] |
| MassDOT points | [-0.017, +0.021] | [-0.001, +0.002] | [-0.012, +0.004] | [-0.021, +0.110] | [-0.039, +0.147] |

Model reliability on Test 1 (isotonic map fitted on Leominster sep2023, frozen):

| predicted bin | segments | mean predicted | observed (reported) |
|---|---|---|---|
| 0–0.1 | 61,342 | 0.021 | 0.003 |
| 0.1–0.2 | 3,446 | 0.144 | 0.006 |
| 0.2–0.3 | 980 | 0.227 | 0.016 |
| 0.6–0.7 | 181 | 0.611 | 0.028 |

## Test 2: 81 District 4–6 storms (668,830 segments in the reported domain, 1,487 reported; 1,756,867 segments in the boxes)

| method | POD | FAR | CSI | flagged share | Brier | PR-AUC | ROC-AUC | site recall at model's share (chance) | site recall at 3 % (chance) |
|---|---|---|---|---|---|---|---|---|---|
| Model (p_close) | 0.028 | 0.961 | **0.017** | 0.1 % | **0.0034** | **0.005** | **0.586** | **0.036** (0.005) | **0.206** (0.086) |
| NWS flash-flood warning | 0.504 | 0.998 | 0.002 | 44.7 % | 0.0064 | 0.002 | 0.474 | 0.006 (0.005) | 0.088 (0.086) |
| FEMA 100-yr zone (≥ 30 % of length) | 0.085 | 0.997 | 0.003 | 5.3 % | 0.0118 | 0.002 | 0.517 | 0.006 (0.005) | 0.070 (0.086) |

| vs | CSI | Brier | PR-AUC | site recall at model's share | site recall at 3 % |
|---|---|---|---|---|---|
| NWS warnings | [+0.004, +0.026] * | [+0.003, +0.003] * | [+0.001, +0.007] * | [+0.013, +0.050] * | [+0.081, +0.156] * |
| FEMA zone | [+0.002, +0.025] * | [+0.008, +0.009] * | [+0.001, +0.007] * | [+0.011, +0.050] * | [+0.089, +0.180] * |

Check: the model's 3 % recall (0.206) matches the transfer result of TRANSFER.md (0.21), so the scorer reproduces the earlier score.

## Tuning storm (Leominster sep2023, complete DPW inventory; in-sample, for reference only)

| method | POD | FAR | CSI |
|---|---|---|---|
| Model | 0.255 | 0.552 | 0.194 |
| NWS warnings | 1.000 | 0.933 | 0.067 |
| FEMA zone | 0.049 | 0.808 | 0.041 |
| MassDOT points | 0.000 | 1.000 | 0.000 |

Worcester aug2021 (development storm, reported separately): model site recall at 3 % 0.25, FEMA 0.17, MassDOT 0.08, NWS 0 (the warning covered
the whole box). Tables in `BENCHMARK_v3_tables.md`.

## Notes and limits

- The reported-domain negatives (≥ 500 m from any report, in towns with a report) favour scores that are smooth in space; this is why
  MassDOT inverse distance looks strong in Leominster (ROC 0.88) but not in Test 1 (0.49). Site recall at equal share does not depend on
  that choice.
- MassDOT's repeat-flood list (38 points) is undated, so it is used for every storm, including storms before it was compiled. That favours it.
- NWS warnings are taken as issued over the storm window (WFO BOX); a warning issued later in the storm counts for the whole storm. That also
  favours the warnings.
