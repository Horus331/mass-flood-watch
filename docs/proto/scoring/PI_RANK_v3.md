# Ranking roads by the chance of flooding (π): result (12 Nov 2026)

Pre-registration: `PREREG_PI_RANK.md`. Code: `proto/bench_v3.py` (method P). Raw: `benchmark_v3.json`.

| | share of report sites in the top 3 % | PR-AUC | ROC-AUC |
|---|---|---|---|
| **Test 2, 81 District 4–6 storms (decides; never in the fit)** | depth rule **0.206** → π **0.251** (chance 0.086) | 0.0050 → 0.0052 | 0.59 → 0.62 |
| Test 1, 23 District 3 storms (in the fit, reported only) | 0.204 → 0.337 | 0.008 → 0.021 | 0.65 → 0.78 |
| Worcester aug2021 (dev) | 0.25 → 0.33 | 0.029 → 0.048 | 0.68 → 0.80 |

π minus depth rule, site recall at 3 %, 95 % interval over the 81 storms: **[+0.002, +0.086]**.

**Decision (as pre-registered): adopted.** Both conditions hold (interval above 0; PR-AUC not lower). The forecast's road list is now ordered
by π ("Roads, most likely to flood first"); the k-of-8 count stays the headline and no percentage is shown (`PI_HELDOUT.md`). Other runs
(replays, what-if) keep "most severe first".

Caveat: the margin on Districts 4–6 is small (lower bound +0.002); the forward test will show whether it holds.
