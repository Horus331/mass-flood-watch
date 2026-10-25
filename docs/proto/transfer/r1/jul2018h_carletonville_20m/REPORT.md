# Road-closure prototype: jul2018h_transfer_jul2018h_carletonville_20m

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on CPU (OpenMP)), 20 m grid, storm from 2018-07-26T13:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 35,960 |
| Expected closures (sum of probabilities) | 49.8 |
| Segments with closure probability >= 50% | 0 (0.0 km) |
| Further segments that may close (stream reaches the road crest) | 2 (0.1 km) |
| Culverts overtopped / surcharged | 1 / 0 of 518 |
| Road segments cut off from hospitals | 0 |
| Worst added trip time to a hospital | 0.0 min |
| Heaviest hour of rain | 13.9 mm |
| Flood model run time | 1530 s |


## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 0.11 | Highland Avenue | Winchester | 0.17 m of water at peak; worst hour 4 mm (65% of the storm) |
| 2 | 0.10 | Central Street | Saugus | 0.17 m of water at peak; worst hour 7 mm (75% of the storm); a culvert within 100 m is overtopped |
| 3 | 0.10 | Elm Street | Saugus | 0.17 m of water at peak; worst hour 7 mm (75% of the storm); a culvert within 100 m is overtopped |
| 4 | 0.10 | Elm Street | Saugus | 0.17 m of water at peak; worst hour 7 mm (75% of the storm) |
| 5 | 0.02 | Washington Circle | Woburn | 0.10 m of water at peak; worst hour 3 mm (54% of the storm) |
| 6 | 0.02 | Howley Street | Peabody | 0.10 m of water at peak; worst hour 9 mm (72% of the storm) |
| 7 | 0.02 | Sunset Road | Winchester | 0.09 m of water at peak; worst hour 4 mm (64% of the storm) |
| 8 | 0.02 | Washington Street | Winchester | 0.09 m of water at peak; worst hour 4 mm (64% of the storm) |
| 9 | 0.02 | Washington Street | Winchester | 0.09 m of water at peak; worst hour 4 mm (64% of the storm) |
| 10 | 0.02 | Washington Street | Winchester | 0.09 m of water at peak; worst hour 4 mm (64% of the storm) |
| 11 | 0.02 | Washington Street | Winchester | 0.09 m of water at peak; worst hour 4 mm (64% of the storm) |
| 12 | 0.02 | Salem Street | Wakefield | 0.09 m of water at peak; worst hour 3 mm (64% of the storm) |
| 13 | 0.02 | Salem Street | Lynnfield | 0.09 m of water at peak; worst hour 3 mm (64% of the storm) |
| 14 | 0.02 | Foster Street | Peabody | 0.09 m of water at peak; worst hour 10 mm (77% of the storm) |
| 15 | 0.02 | Salem Street | Lynnfield | 0.09 m of water at peak; worst hour 3 mm (64% of the storm) |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
