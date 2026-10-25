# Road-closure prototype: oct2018e_transfer_oct2018e_somerville_20m

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on CPU (OpenMP)), 20 m grid, storm from 2018-10-29T06:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 37,371 |
| Expected closures (sum of probabilities) | 52.5 |
| Segments with closure probability >= 50% | 1 (0.1 km) |
| Further segments that may close (stream reaches the road crest) | 3 (0.7 km) |
| Culverts overtopped / surcharged | 1 / 0 of 541 |
| Road segments cut off from hospitals | 0 |
| Worst added trip time to a hospital | 0.0 min |
| Heaviest hour of rain | 13.3 mm |
| Flood model run time | 869 s |


## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 0.82 | Highland Avenue | Winchester | 0.39 m of water at peak; over 30 cm for 3.5 h; 30 cm reached 15.0 h into the storm; worst hour 8 mm (52% of the storm) |
| 2 | 0.10 | Central Street | Saugus | 0.17 m of water at peak; worst hour 10 mm (62% of the storm); a culvert within 100 m is overtopped |
| 3 | 0.10 | Elm Street | Saugus | 0.17 m of water at peak; worst hour 10 mm (62% of the storm); a culvert within 100 m is overtopped |
| 4 | 0.10 | Elm Street | Saugus | 0.17 m of water at peak; worst hour 10 mm (62% of the storm) |
| 5 | 0.03 | Garden Street | Arlington | 0.12 m of water at peak; worst hour 8 mm (53% of the storm); water beside the road 0.06 m below its crest (design freeboard 0.30 m; P 0.95) |
| 6 | 0.02 | Howley Street | Peabody | 0.10 m of water at peak; worst hour 10 mm (52% of the storm) |
| 7 | 0.02 | Washington Circle | Woburn | 0.10 m of water at peak; worst hour 7 mm (52% of the storm) |
| 8 | 0.02 | Foster Street | Peabody | 0.09 m of water at peak; worst hour 10 mm (49% of the storm) |
| 9 | 0.02 | Sunset Road | Winchester | 0.09 m of water at peak; worst hour 8 mm (52% of the storm) |
| 10 | 0.02 | Washington Street | Winchester | 0.09 m of water at peak; worst hour 8 mm (52% of the storm) |
| 11 | 0.02 | Washington Street | Winchester | 0.09 m of water at peak; worst hour 8 mm (52% of the storm) |
| 12 | 0.02 | Washington Street | Winchester | 0.09 m of water at peak; worst hour 8 mm (52% of the storm) |
| 13 | 0.02 | Washington Street | Winchester | 0.09 m of water at peak; worst hour 8 mm (52% of the storm) |
| 14 | 0.02 | Salem Street | Wakefield | 0.09 m of water at peak; worst hour 9 mm (58% of the storm) |
| 15 | 0.02 | Salem Street | Lynnfield | 0.09 m of water at peak; worst hour 9 mm (58% of the storm) |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
