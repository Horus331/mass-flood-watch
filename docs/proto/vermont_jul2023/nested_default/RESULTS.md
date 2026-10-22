# Vermont, July 10-11 2023: closure rules vs VTrans closures

Box (EPSG:26986) [107000.0, 1096000.0, 127000.0, 1116000.0], 3483 OSM road segments; 11 of the closed stretches in the box matched to road segments (strict, 30 m); storm rain max 202 mm, worst hour 29.7 mm.

| rule | recall (strict) | flagged share | lift (chance-corrected) | loose recall | Leominster (recall / flagged / lift) |
| --- | --- | --- | --- | --- | --- |
| depth rule (default p_close) | 0.273 (11) | 6.57 % | 0.72 | 0.364 | 0.385 / 4.7 % / 5.83 |
| overtop candidate (water beside the road reaches the crest) | 0.364 (11) | 9.91 % | 0.77 | 0.364 | 0.744 / 9.8 % / 5.45 |
| freeboard (water within 0.30 m of the crest) | 0.636 (11) | 13.87 % | 1.15 | 0.636 | 0.756 / 14.2 % / 3.89 |
| culvert (depth + HDS-5 culvert overtopping) | 0.545 (11) | 7.15 % | 1.37 | 0.545 |  |
| overtop + culvert | 0.545 (11) | 10.42 % | 1.13 | 0.545 |  |

Overtop vs depth: recall higher True, flags <= 10 % True, lift [0.77, 0.72].

| gauge | obs rise m | model rise m | obs peak (UTC) | model peak | obs peak Q m3/s | model peak Q m3/s |
| --- | --- | --- | --- | --- | --- | --- |
| 04286000 WINOOSKI RIVER AT MONTPELIER, VT | 4.98 | 0.0 | 2023-07-11T12:30Z | 2023-07-09T18:00Z | 654.1 | 124.857 |
| 04287000 DOG RIVER AT NORTHFIELD FALLS, VT | 3.16 | 0.01 | 2023-07-10T23:45Z | 2023-07-10T13:00Z | 311.5 | 24.726 |

Coarse (60 m, 60 x 60 km) run that feeds the edge inflows, at the same gauges:

| gauge | obs peak Q m3/s | model peak Q m3/s | model peak (h from t0) |
| --- | --- | --- | --- |
| 01135100 POPE BROOK TRIBUTARY (W-9), NR NORTH DANVILLE, VT | 0.6 | 0.978 | 0.0 |
| 01139800 EAST ORANGE BRANCH AT EAST ORANGE, VT | 18.9 | 1.711 | 0.0 |
| 04285500 NORTH BRANCH WINOOSKI RIVER AT WRIGHTSVILLE, VT | 37.4 | 3.652 | 0.0 |
| 04286000 WINOOSKI RIVER AT MONTPELIER, VT | 654.1 | 2.505 | 0.0 |
| 04287000 DOG RIVER AT NORTHFIELD FALLS, VT | 311.5 | 3.189 | 58.5 |
| 04288000 MAD RIVER NEAR MORETOWN, VT | 202.7 | 2.885 | 0.0 |
| 04288230 RANCH BROOK AT RANCH CAMP, NEAR STOWE, VT | 21.4 | 6.522 | 19.0 |
| 04288295 LITTLE RIVER NEAR STOWE, VT | 130.0 | 0.588 | 30.5 |
| 04289000 LITTLE RIVER NEAR WATERBURY, VT | 60.0 | 5.977 | 0.0 |

Edge inflows (25): IN03 136 km2 peak 15.28 m3/s, IN12 16 km2 peak 13.45 m3/s, IN02 189 km2 peak 12.48 m3/s, IN08 23 km2 peak 7.56 m3/s, IN18 5 km2 peak 6.51 m3/s, IN01 239 km2 peak 6.4 m3/s, IN15 8 km2 peak 6.29 m3/s, IN14 9 km2 peak 6.03 m3/s
