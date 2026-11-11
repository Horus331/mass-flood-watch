# Model + traffic ranking: result (11 Nov 2026)

Pre-registration: `PREREG_HYBRID.md`. Code: `proto/bench_v3.py` (method H). Raw: `benchmark_v3.json`.

Fitted on Leominster sep2023 only: logit P = −7.82 + 3.01 · p_close + 1.50 · log10(1 + AADT).

| share of report sites in the top 3 % | model | model + traffic | static H×V×C | chance |
|---|---|---|---|---|
| Test 2: 81 District 4–6 storms (primary) | **0.206** | 0.196 | 0.096 | 0.086 |
| Test 1: 23 District 3 storms | 0.204 | **0.286** | 0.316 | 0.066 |
| Worcester aug2021 (dev) | 0.25 | 0.33 | 0.58 | 0.06 |

Model + traffic minus model, 95 % interval over storms: Test 2 **[−0.041, +0.021]**; Test 1 [−0.010, +0.171].

**Decision (as pre-registered): not adopted.** The primary test needed an interval above 0 on Districts 4–6; it is centred on no change.
The model ranking stays.

What it means: adding traffic helps where reports come from MassDOT and the news (District 3), and does nothing where reports are more
varied (Districts 4–6). That is what one would expect if most of traffic's value is in predicting which floods get *reported*. For an
operations product, a consequence weight (traffic, detours, emergency access) belongs in the crew checklist as a separate, stated column,
not mixed into the chance of flooding.
