**Verdict: NOT ADOPTED** (held-out storms scored: 23 / 23)

| PROTOCOL v2 §5a condition | value | pass |
|---|---|---|
| 1. pooled site recall gain at 3 % >= +0.04 | -0.010 (98 sites) | False |
| 2. one-sided 5 % lower bound > 0 (k = 1) | -0.050 | False |
| 3. FSS 300 m at 3 % does not drop | -0.0023 | False |
| 4. no storm with >= 3 sites loses > 1 site at 3 % | worst -1.0 | True |
| 5. rule lift >= 0.8 x base | 5.99 vs 7.19 | True |

| held-out pooled (box) | base | LF_INLETS |
|---|---|---|
| site recall at 3 % | 0.194 | 0.184 |
| lift at 3 % | 3.040 | 2.880 |
| site recall at rule | 0.071 | 0.051 |
| lift at rule | 7.194 | 5.994 |
| FSS 300 m at 3 % | 0.022 | 0.020 |
| mean flagged share at rule | 0.0033 | 0.0029 |

Failure-mode check (DRAINS.md; reported, not a decision): rule-flagged segments 428 -> 363 (drop 0.152), rule-hit sites 7.0 -> 5.0 (drop 0.286); ratio 1.88; sites removed in proportion: **True**

| storm | sites | base 3 % hits | inlets 3 % hits | base rule hits / share | inlets rule hits / share | inlet sink m3/s (inlets, cells) |
|---|---|---|---|---|---|---|
| aug2023 | 6 | 1.0 | 1.0 | 1 / 0.0142 | 0 / 0.0136 | None (None, None) |
| aug2023b | 3 | 0.0 | 0.0 | 0 / 0.0004 | 0 / 0.0002 | None (None, None) |
| aug2026 | 10 | 3.0 | 3.0 | 1 / 0.0101 | 1 / 0.0095 | None (None, None) |
| jul2021 | 4 | 1.0 | 1.0 | 1 / 0.0014 | 0 / 0.0005 | None (None, None) |
| jul2023 | 5 | 0.0 | 0.0 | 0 / 0.0000 | 0 / 0.0000 | None (None, None) |
| sep2021 | 8 | 5.0 | 4.0 | 3 / 0.0168 | 3 / 0.0123 | None (None, None) |
| sep2022 | 4 | 1.0 | 1.0 | 0 / 0.0044 | 0 / 0.0040 | None (None, None) |
| may2018 | 3 | 1.0 | 1.0 | 0 / 0.0001 | 0 / 0.0001 | None (None, None) |
| aug2018b | 3 | 0.0 | 0.0 | 0 / 0.0020 | 0 / 0.0020 | None (None, None) |
| sep2018 | 5 | 1.0 | 1.0 | 1 / 0.0029 | 1 / 0.0029 | None (None, None) |
| sep2018w | 4 | 0.0 | 0.0 | 0 / 0.0054 | 0 / 0.0054 | None (None, None) |
| sep2018m | 4 | 1.0 | 1.0 | 0 / 0.0026 | 0 / 0.0026 | None (None, None) |
| sep2018b | 5 | 0.0 | 0.0 | 0 / 0.0000 | 0 / 0.0000 | None (None, None) |
| jul2019 | 5 | 0.0 | 0.0 | 0 / 0.0000 | 0 / 0.0000 | None (None, None) |
| aug2019 | 2 | 0.0 | 0.0 | 0 / 0.0000 | 0 / 0.0000 | None (None, None) |
| sep2019 | 2 | 0.0 | 0.0 | 0 / 0.0002 | 0 / 0.0002 | None (None, None) |
| jun2020 | 6 | 2.0 | 2.0 | 0 / 0.0047 | 0 / 0.0038 | None (None, None) |
| jun2020b | 4 | 0.0 | 0.0 | 0 / 0.0005 | 0 / 0.0005 | None (None, None) |
| aug2020b | 3 | 0.0 | 0.0 | 0 / 0.0000 | 0 / 0.0000 | None (None, None) |
| jul2021b | 4 | 2.0 | 1.0 | 0 / 0.0020 | 0 / 0.0013 | None (None, None) |
| jul2023b | 2 | 0.0 | 1.0 | 0 / 0.0008 | 0 / 0.0005 | None (None, None) |
| jul2023c | 4 | 1.0 | 1.0 | 0 / 0.0039 | 0 / 0.0033 | None (None, None) |
| jul2023d | 2 | 0.0 | 0.0 | 0 / 0.0030 | 0 / 0.0030 | None (None, None) |

| sep2023 (calibration, report only) | box 3 % hits | box rule hits / share | Leominster city rule hits / flagged | sink m3/s | gauge mean abs rise error m |
|---|---|---|---|---|---|
| base | 29.0 / 79 | 28 / 0.0187 | 28 / 50 | None | 0.1 |
| inlets | 31.0 / 79 | 28 / 0.0183 | 28 / 48 | None | 0.1 |

sep2023 inlets failure-mode check: city flags 50 -> 48, city rule-hit sites 28.0 -> 28.0, ratio 0.00, in proportion: False
