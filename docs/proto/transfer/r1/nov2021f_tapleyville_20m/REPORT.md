# Road-closure prototype: nov2021f_transfer_nov2021f_tapleyville_20m

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on CPU (OpenMP)), 20 m grid, storm from 2021-11-12T14:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 29,822 |
| Expected closures (sum of probabilities) | 42.6 |
| Segments with closure probability >= 50% | 1 (0.1 km) |
| Further segments that may close (stream reaches the road crest) | 3 (0.7 km) |
| Culverts overtopped / surcharged | 1 / 0 of 546 |
| Road segments cut off from hospitals | 0 |
| Worst added trip time to a hospital | 0.0 min |
| Heaviest hour of rain | 12.9 mm |
| Flood model run time | 1294 s |


## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 0.98 | Highland Avenue | Winchester | 0.51 m of water at peak; over 30 cm for 6.0 h; 30 cm reached 12.5 h into the storm; worst hour 7 mm (29% of the storm) |
| 2 | 0.10 | Central Street | Saugus | 0.17 m of water at peak; worst hour 7 mm (38% of the storm); a culvert within 100 m is overtopped |
| 3 | 0.10 | Elm Street | Saugus | 0.17 m of water at peak; worst hour 7 mm (38% of the storm); a culvert within 100 m is overtopped |
| 4 | 0.10 | Elm Street | Saugus | 0.17 m of water at peak; worst hour 7 mm (38% of the storm) |
| 5 | 0.05 | Mill Street | Reading | 0.14 m of water at peak; worst hour 11 mm (44% of the storm) |
| 6 | 0.05 | Mill Street | Reading | 0.14 m of water at peak; worst hour 11 mm (44% of the storm) |
| 7 | 0.03 | Russell Street | Peabody | 0.11 m of water at peak; worst hour 12 mm (43% of the storm); water beside the road 0.39 m below its crest (design freeboard 0.30 m; P 0.28) |
| 8 | 0.03 | I-93 | Medford | 0.10 m of water at peak; worst hour 8 mm (38% of the storm); water beside the road 0.10 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 0.7 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.22); road sag 1.6 m deep (underpass, drains sized for the 50-yr hour, 58 mm; peak hour here 8 mm; catchment 25.1 ha) (P 0.10) |
| 9 | 0.02 | Howley Street | Peabody | 0.10 m of water at peak; worst hour 5 mm (32% of the storm) |
| 10 | 0.02 | Foster Street | Peabody | 0.09 m of water at peak; worst hour 6 mm (34% of the storm) |
| 11 | 0.02 | Salem Street | Wakefield | 0.09 m of water at peak; worst hour 8 mm (38% of the storm) |
| 12 | 0.02 | Salem Street | Lynnfield | 0.09 m of water at peak; worst hour 8 mm (38% of the storm) |
| 13 | 0.02 | Salem Street | Lynnfield | 0.09 m of water at peak; worst hour 8 mm (38% of the storm) |
| 14 | 0.02 | Kimball Lane | Lynnfield | 0.09 m of water at peak; worst hour 8 mm (38% of the storm) |
| 15 | 0.01 | Washington Circle | Woburn | 0.08 m of water at peak; worst hour 8 mm (33% of the storm) |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
