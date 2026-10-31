**Verdict: NOT ADOPTED** (held-out storms scored: 23 / 23)

| PROTOCOL v2 §5a condition | value | pass |
|---|---|---|
| 1. pooled site recall gain at 3 % >= +0.04 | 0.000 (98 sites) | False |
| 2. one-sided 5 % lower bound > 0 (k = 1) | -0.033 | False |
| 3. FSS 300 m at 3 % does not drop | -0.0009 | False |
| 4. no storm with >= 3 sites loses > 1 site at 3 % | worst -1.0 | True |
| 5. rule lift >= 0.8 x base | 6.62 vs 6.27 | True |

| held-out pooled (box) | base | LF_INLETS |
|---|---|---|
| site recall at 3 % | 0.194 | 0.194 |
| lift at 3 % | 3.040 | 3.040 |
| site recall at rule | 0.082 | 0.071 |
| lift at rule | 6.270 | 6.620 |
| FSS 300 m at 3 % | 0.022 | 0.021 |
| mean flagged share at rule | 0.0043 | 0.0036 |

Failure-mode check (DRAINS.md; reported, not a decision): rule-flagged segments 586 -> 479 (drop 0.183), rule-hit sites 8.0 -> 7.0 (drop 0.125); ratio 0.68; sites removed in proportion: **False**

| storm | sites | base 3 % hits | inlets 3 % hits | base rule hits / share | inlets rule hits / share | inlet sink m3/s (inlets, cells) |
|---|---|---|---|---|---|---|
| aug2023 | 6 | 1.0 | 1.0 | 1 / 0.0162 | 0 / 0.0157 | 297.27 (3648, 2796) |
| aug2023b | 3 | 0.0 | 0.0 | 0 / 0.0011 | 0 / 0.0009 | 373.39 (4981, 3474) |
| aug2026 | 10 | 4.0 | 4.0 | 2 / 0.0137 | 2 / 0.0110 | 581.73 (14389, 8775) |
| jul2021 | 4 | 0.0 | 0.0 | 0 / 0.0019 | 0 / 0.0014 | 295.62 (4058, 2734) |
| jul2023 | 5 | 0.0 | 0.0 | 0 / 0.0007 | 0 / 0.0006 | 320.88 (4177, 3016) |
| sep2021 | 8 | 4.0 | 4.0 | 3 / 0.0241 | 3 / 0.0175 | 362.97 (4727, 3375) |
| sep2022 | 4 | 1.0 | 1.0 | 1 / 0.0061 | 1 / 0.0053 | 126.72 (1625, 1225) |
| may2018 | 3 | 1.0 | 1.0 | 0 / 0.0006 | 0 / 0.0005 | 434.14 (5607, 4049) |
| aug2018b | 3 | 0.0 | 0.0 | 0 / 0.0016 | 0 / 0.0016 | 280.43 (3421, 2663) |
| sep2018 | 5 | 1.0 | 1.0 | 1 / 0.0023 | 1 / 0.0023 | 147.15 (2058, 1465) |
| sep2018w | 4 | 0.0 | 1.0 | 0 / 0.0056 | 0 / 0.0056 | 266.8 (3292, 2647) |
| sep2018m | 4 | 1.0 | 1.0 | 0 / 0.0030 | 0 / 0.0026 | 181.4 (2291, 1762) |
| sep2018b | 5 | 0.0 | 0.0 | 0 / 0.0000 | 0 / 0.0000 | 151.28 (1877, 1450) |
| jul2019 | 5 | 0.0 | 0.0 | 0 / 0.0010 | 0 / 0.0008 | 293.45 (3951, 2749) |
| aug2019 | 2 | 0.0 | 0.0 | 0 / 0.0003 | 0 / 0.0003 | 270.28 (3743, 2515) |
| sep2019 | 2 | 1.0 | 1.0 | 0 / 0.0004 | 0 / 0.0004 | 168.21 (2145, 1637) |
| jun2020 | 6 | 2.0 | 2.0 | 0 / 0.0052 | 0 / 0.0052 | 153.54 (1927, 1488) |
| jun2020b | 4 | 0.0 | 0.0 | 0 / 0.0005 | 0 / 0.0005 | 151.98 (1933, 1457) |
| aug2020b | 3 | 0.0 | 0.0 | 0 / 0.0006 | 0 / 0.0005 | 415.74 (5488, 3860) |
| jul2021b | 4 | 2.0 | 2.0 | 0 / 0.0039 | 0 / 0.0025 | 414.18 (5430, 3864) |
| jul2023b | 2 | 0.0 | 0.0 | 0 / 0.0027 | 0 / 0.0014 | 351.08 (4379, 3305) |
| jul2023c | 4 | 1.0 | 0.0 | 0 / 0.0048 | 0 / 0.0035 | 526.07 (13832, 8280) |
| jul2023d | 2 | 0.0 | 0.0 | 0 / 0.0038 | 0 / 0.0038 | 110.84 (1386, 1085) |

| sep2023 (calibration, report only) | box 3 % hits | box rule hits / share | Leominster city rule hits / flagged | sink m3/s | gauge mean abs rise error m |
|---|---|---|---|---|---|
| base | 30.0 / 79 | 29 / 0.0216 | 29 / 58 | None | 0.23 |
| inlets | 29.0 / 79 | 26 / 0.0165 | 26 / 37 | 581.73 | 0.49 |
| inlets_clog0 | 27.0 / 79 | 25 / 0.0156 | 25 / 34 | 918.67 | 0.53 |
| inlets_clog065 | 29.0 / 79 | 26 / 0.0167 | 26 / 38 | 446.68 | 0.47 |

sep2023 inlets failure-mode check: city flags 58 -> 37, city rule-hit sites 29.0 -> 26.0, ratio 0.29, in proportion: False

sep2023 inlets_clog0 failure-mode check: city flags 58 -> 34, city rule-hit sites 29.0 -> 25.0, ratio 0.33, in proportion: False

sep2023 inlets_clog065 failure-mode check: city flags 58 -> 38, city rule-hit sites 29.0 -> 26.0, ratio 0.30, in proportion: False
