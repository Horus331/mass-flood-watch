# Vermont, July 10-11 2023: closure rules vs VTrans closures

Box (EPSG:26986) [107000.0, 1096000.0, 127000.0, 1116000.0], 3483 OSM road segments; 11 of the closed stretches in the box matched to road segments (strict, 30 m); storm rain max 202 mm, worst hour 29.7 mm.

| rule | recall (strict) | flagged share | lift (chance-corrected) | loose recall | Leominster (recall / flagged / lift) |
| --- | --- | --- | --- | --- | --- |
| depth rule (default p_close) | 0.273 (11) | 7.26 % | 0.68 | 0.364 | 0.385 / 4.7 % / 5.83 |
| overtop candidate (water beside the road reaches the crest) | 0.364 (11) | 10.45 % | 0.75 | 0.364 | 0.744 / 9.8 % / 5.45 |
| freeboard (water within 0.30 m of the crest) | 0.636 (11) | 14.27 % | 1.14 | 0.636 | 0.756 / 14.2 % / 3.89 |
| culvert (depth + HDS-5 culvert overtopping) | 0.545 (11) | 7.81 % | 1.3 | 0.545 |  |
| overtop + culvert | 0.545 (11) | 10.94 % | 1.1 | 0.545 |  |

Overtop vs depth: recall higher True, flags <= 10 % False, lift [0.75, 0.68].

| gauge | obs rise m | model rise m | obs peak (UTC) | model peak | obs peak Q m3/s | model peak Q m3/s |
| --- | --- | --- | --- | --- | --- | --- |
| 04286000 WINOOSKI RIVER AT MONTPELIER, VT | 4.98 | 0.0 | 2023-07-11T12:30Z | 2023-07-09T18:00Z | 654.1 | 146.668 |
| 04287000 DOG RIVER AT NORTHFIELD FALLS, VT | 3.16 | 0.01 | 2023-07-10T23:45Z | 2023-07-10T13:00Z | 311.5 | 20.582 |
