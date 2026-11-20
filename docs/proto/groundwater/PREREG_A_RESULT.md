# Groundwater proposal A: result (20 Nov 2026)

Run once, exactly as frozen in `PREREG_A.md` (commit fc234f10b, before the script existed). Script `proto/gw_prereg_a.py`, numbers
`prereg_a.json`. No re-runs, no changes after seeing the result.

**Population.** 1,517 Leominster segments of the Sept 2023 T2 run with a water-table value (4 without). 52 of the 54 DPW points lie within
30 m of one of these segments → **21 damaged segments**, 14 of them on a seasonal water table within 50 cm; 646 shallow segments in all.
Damaged segments fall in 4 of the 15 height-above-drainage × slope strata.

| | Mantel–Haenszel odds ratio | 95 % interval | CMH p |
|---|---|---|---|
| **Main: damage vs water table ≤ 50 cm, terrain held constant** | **2.70** | 1.02 – 7.12 | 0.069 |
| (a) without Wachusett St | 2.00 | 0.72 – 5.54 | 0.27 |
| (b) cut-off 25 cm | 2.62 | 1.02 – 6.73 | 0.079 |
| (c) logistic regression with HAND and slope (odds ratio for shallow) | 2.94 | — | — |
| (d) road class also held constant | 3.19 | 1.14 – 8.90 | 0.040 |
| (e) washouts only | 2.49 | 0.85 – 7.29 | 0.15 |
| **Negative control: model closures (surface water) vs water table** | **2.68** | 1.46 – 4.91 | 0.001 |

**Verdict by the frozen rules: pass** (odds ratio ≥ 2, interval above 1, and still > 1 without Wachusett St), and the negative control is
formally below the main result (2.68 < 2.70), so the "not separable" flag is not raised.

**What that means, plainly.** The rules are met, but only just, and the negative control is the important line: surface-water closures
are associated with a shallow water table almost exactly as strongly as damage is (2.68 vs 2.70), even after holding height above
drainage and slope constant. So the data cannot tell a groundwater effect on the road structure apart from "wet, low-lying places flood".
The interval's lower end (1.02) and the CMH test (p = 0.07) are both at the edge; without Wachusett St the effect is not distinguishable
from none. With 21 damaged segments from one storm in one town, this is as far as the existing data go.

**Next (per the pre-registration, proposal A goes ahead only with new data):** pavement or subgrade observations (MassDOT pavement
condition, deflection tests, borings) or damage lists from other storms (the MEMA / FEMA Public Assistance Category C request). Nothing
in the live model changes.
