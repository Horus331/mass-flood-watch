# Road-closure prototype: jul2023f_transfer_jul2023f_wswrevere_20m

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on CPU (OpenMP)), 20 m grid, storm from 2023-07-16T10:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 29,906 |
| Expected closures (sum of probabilities) | 46.7 |
| Segments with closure probability >= 50% | 1 (0.1 km) |
| Further segments that may close (stream reaches the road crest) | 11 (2.6 km) |
| Culverts overtopped / surcharged | 5 / 1 of 663 |
| Road segments cut off from hospitals | 0 |
| Worst added trip time to a hospital | 0.0 min |
| Heaviest hour of rain | 22.5 mm |
| Flood model run time | 1524 s |


## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 1.00 | Highland Avenue | Winchester | 1.33 m of water at peak; over 30 cm for 10.0 h; 30 cm reached 8.5 h into the storm; worst hour 16 mm (30% of the storm); a culvert within 100 m is overtopped |
| 2 | 0.43 | Rutledge Road | Peabody | 0.28 m of water at peak; worst hour 19 mm (28% of the storm); water beside the road 0.34 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.8 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 18 mm; catchment 8.2 ha) (P 0.45) |
| 3 | 0.24 | Russell Street | Peabody | 0.23 m of water at peak; worst hour 21 mm (35% of the storm); water beside the road 0.27 m below its crest (design freeboard 0.30 m; P 0.59); a culvert within 100 m is overtopped |
| 4 | 0.12 | America Drive | Peabody | 0.18 m of water at peak; worst hour 20 mm (29% of the storm); water beside the road 0.06 m above its crest (design freeboard 0.30 m; P 0.99); road sag 0.6 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 20 mm; catchment 14.1 ha) (P 0.16) |
| 5 | 0.10 | Central Street | Saugus | 0.17 m of water at peak; worst hour 13 mm (29% of the storm); a culvert within 100 m is overtopped |
| 6 | 0.10 | Elm Street | Saugus | 0.17 m of water at peak; worst hour 13 mm (29% of the storm); a culvert within 100 m is overtopped |
| 7 | 0.10 | Elm Street | Saugus | 0.17 m of water at peak; worst hour 13 mm (29% of the storm) |
| 8 | 0.09 | Skinner Lane | Lynnfield | 0.17 m of water at peak; worst hour 17 mm (28% of the storm); a culvert within 100 m is overtopped |
| 9 | 0.07 | Roosevelt Avenue | Peabody | 0.15 m of water at peak; worst hour 20 mm (34% of the storm); water beside the road 0.03 m above its crest (design freeboard 0.30 m; P 0.99) |
| 10 | 0.07 | Harrison Avenue | Peabody | 0.15 m of water at peak; worst hour 20 mm (32% of the storm); water beside the road 0.09 m above its crest (design freeboard 0.30 m; P 0.99) |
| 11 | 0.06 | Boston Street | Peabody | 0.15 m of water at peak; worst hour 18 mm (25% of the storm) |
| 12 | 0.06 | Boston Street | Peabody | 0.15 m of water at peak; worst hour 18 mm (25% of the storm) |
| 13 | 0.05 | Mill Street | Reading | 0.14 m of water at peak; worst hour 6 mm (23% of the storm) |
| 14 | 0.05 | Mill Street | Reading | 0.14 m of water at peak; worst hour 6 mm (23% of the storm) |
| 15 | 0.05 | Conant Road | Winchester | 0.14 m of water at peak; worst hour 20 mm (36% of the storm); water beside the road 0.05 m above its crest (design freeboard 0.30 m; P 0.99) |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
