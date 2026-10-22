# Vermont, July 10-11 2023: closure rules vs VTrans closures

Box (EPSG:26986) [107000.0, 1096000.0, 127000.0, 1116000.0], 3697 OSM road segments; 11 of the closed stretches in the box matched to road segments (strict, 30 m); storm rain max 202 mm, worst hour 29.7 mm.

| rule | recall (strict) | flagged share | lift (chance-corrected) | loose recall | Leominster (recall / flagged / lift) |
| --- | --- | --- | --- | --- | --- |
| depth rule (default p_close) | 0.455 (11) | 8.36 % | 0.97 | 0.545 | 0.385 / 4.7 % / 5.83 |
| overtop candidate (water beside the road reaches the crest) | 0.455 (11) | 10.74 % | 0.86 | 0.545 | 0.744 / 9.8 % / 5.45 |
| freeboard (water within 0.30 m of the crest) | 0.636 (11) | 12.44 % | 1.13 | 0.727 | 0.756 / 14.2 % / 3.89 |
| culvert (depth + HDS-5 culvert overtopping) | 0.727 (11) | 9.12 % | 1.49 | 0.727 |  |
| overtop + culvert | 0.727 (11) | 11.39 % | 1.34 | 0.727 |  |

Overtop vs depth: recall higher False, flags <= 10 % False, lift [0.86, 0.97].

| gauge | obs rise m | model rise m | obs peak (UTC) | model peak | obs peak Q m3/s | model peak Q m3/s |
| --- | --- | --- | --- | --- | --- | --- |
| 04286000 WINOOSKI RIVER AT MONTPELIER, VT | 4.98 | 3.5 | 2023-07-11T12:30Z | 2023-07-11T04:00Z | 654.1 | 96.255 |
| 04287000 DOG RIVER AT NORTHFIELD FALLS, VT | 3.16 | 1.79 | 2023-07-10T23:45Z | 2023-07-11T01:00Z | 311.5 | 42.434 |

Coarse (60 m, 60 x 60 km) run that feeds the edge inflows, at the same gauges:

| gauge | obs peak Q m3/s | model peak Q m3/s | model peak (h from t0) |
| --- | --- | --- | --- |
| 01135100 POPE BROOK TRIBUTARY (W-9), NR NORTH DANVILLE, VT | 0.6 | 0.682 | 37.0 |
| 01139800 EAST ORANGE BRANCH AT EAST ORANGE, VT | 18.9 | 2.684 | 31.0 |
| 04285500 NORTH BRANCH WINOOSKI RIVER AT WRIGHTSVILLE, VT | 37.4 | 1.175 | 36.0 |
| 04286000 WINOOSKI RIVER AT MONTPELIER, VT | 654.1 | 13.365 | 56.0 |
| 04287000 DOG RIVER AT NORTHFIELD FALLS, VT | 311.5 | 46.183 | 32.0 |
| 04288000 MAD RIVER NEAR MORETOWN, VT | 202.7 | 8.182 | 29.0 |
| 04288230 RANCH BROOK AT RANCH CAMP, NEAR STOWE, VT | 21.4 | 6.667 | 19.0 |
| 04288295 LITTLE RIVER NEAR STOWE, VT | 130.0 | 4.018 | 35.5 |
| 04289000 LITTLE RIVER NEAR WATERBURY, VT | 60.0 | 0.844 | 50.5 |

Edge inflows (25): IN12 16 km2 peak 36.38 m3/s, IN03 136 km2 peak 36.11 m3/s, IN01 239 km2 peak 31.38 m3/s, IN08 23 km2 peak 14.22 m3/s, IN15 8 km2 peak 8.67 m3/s, IN11 16 km2 peak 8.27 m3/s, IN20 5 km2 peak 7.86 m3/s, IN06 30 km2 peak 7.11 m3/s
