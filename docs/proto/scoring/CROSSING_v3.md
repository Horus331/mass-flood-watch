# Model + stream crossings: result (12 Nov 2026)

Pre-registration: `PREREG_CROSSING.md`. Code: `proto/bench_v3.py` (methods X, BX). Raw: `benchmark_v3.json`.

Fitted on Leominster sep2023 only: logit P = −3.20 + 2.10 · p_close + 1.81 · (crossing within 30 m).

| share of report sites in the top 3 % | model | model + crossing | crossing alone | chance |
|---|---|---|---|---|
| Test 2: 81 District 4–6 storms (primary) | **0.206** | 0.143 | 0.096 | 0.086 |
| Test 1: 23 District 3 storms | 0.204 | 0.210 | 0.147 | 0.066 |
| Worcester aug2021 (dev) | 0.25 | 0.17 | 0.13 | 0.06 |

Model minus model + crossing, 95 % interval over storms: Test 2 **[+0.036, +0.094]** (the model alone is significantly better); Test 1
[−0.035, +0.024].

**Decision (as pre-registered): not adopted.** Adding the crossing flag makes the ranking worse on Districts 4–6.

What it means: in Leominster, damage clustered at crossings (16 × the road-length share), but reported flooding elsewhere does not: the
crossing flag alone is at chance in Districts 4–6 and about 2 × chance in District 3. Two readings, not separable with these labels:
crossing failures are a Leominster-type (small-stream, hilly) mechanism, or the reports elsewhere (NWS, news, MassDOT) record ponded roads
rather than culvert damage. A crossing indicator belongs to the culvert-damage question (DPW-type labels), not to the closure ranking.
