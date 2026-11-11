# Benchmark v3: the model vs NWS warnings, FEMA zones and MassDOT repeat points (Test 1: 10 Nov; Test 2: 11 Nov 2026)

Rules: `docs/proto/PROTOCOL_v3.md` (committed c91b0587 before any of this was scored). Code: `proto/bench_v3.py`. Raw: `benchmark_v3.json`.
Full tables: `BENCHMARK_v3_tables.md`. Model = the clean CPU parity runs (`docs/proto/parity/catalog`), the frozen runs scored in
BASELINE_v2_expanded. Test 2 uses the frozen r1 transfer runs (work branch `transfer-d456`) and the SFHA overlaps of HYBRID.md (run 40966174644).
Not in yet: B4 rain threshold, B5 HAND, B6 H×V×C. B3 is District 3 only (MassDOT's list covers District 3).

## In plain words

**Districts 4–6 (81 storms, never used to build or tune anything): the model beats both NWS warnings and the FEMA 100-yr zone on all five
measures, every one significant.** At 3 % of roads it finds 21 % of report sites; FEMA 7 %, NWS warnings 9 %, chance 9 %. FEMA and the
warnings are no better than chance there. This settles the open question from District 3 for FEMA (below).

District 3 (23 held-out storms):

- **The model clearly beats NWS flash-flood warnings.** Warnings covered half of all road segments in the test storms; at the same number
  of flagged roads the model finds 9 % of report sites vs 1 % for the warnings (chance 1.4 %), and at 3 % of roads 20 % vs 5 %. All four
  ranking/yes-no comparisons are significant over the 23 storms.
- **Against the FEMA 100-yr zone and MassDOT's repeat-flood list the model is ahead on every number but not significantly.** At 3 % of roads:
  model 20 %, FEMA 12 %, MassDOT points 14 % of sites (chance 7 %). The 95 % intervals include 0. The one significant difference is the
  Brier score against FEMA (FEMA's probabilities are worse).
- **Probabilities fitted on Leominster do not carry over.** Roads the Leominster-calibrated model gives about 60 % flooded about 3 % of the
  time in the other 23 storms (reliability table below). Part of this is that outside Leominster most flooded roads are never reported, but
  it confirms the master-prompt rule: the site keeps "k of N", no percentage, until held-out calibration works.
- **Absolute skill is low.** At its own rule (p_close ≥ 0.5) the model catches 5 % of reported segments with 97 % of its flags unreported
  (CSI 0.018). It is a ranking that beats chance by about 3–6 x, not yet a warning tool on its own.

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
