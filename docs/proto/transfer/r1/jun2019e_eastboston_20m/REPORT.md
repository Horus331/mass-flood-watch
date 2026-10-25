# Road-closure prototype: jun2019e_transfer_jun2019e_eastboston_20m

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on CPU (OpenMP)), 20 m grid, storm from 2019-06-29T13:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 37,664 |
| Expected closures (sum of probabilities) | 52.4 |
| Segments with closure probability >= 50% | 1 (0.1 km) |
| Further segments that may close (stream reaches the road crest) | 3 (0.7 km) |
| Culverts overtopped / surcharged | 1 / 0 of 315 |
| Road segments cut off from hospitals | 0 |
| Worst added trip time to a hospital | 0.0 min |
| Heaviest hour of rain | 32.4 mm |
| Flood model run time | 1209 s |


## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 1.00 | Highland Avenue | Winchester | 0.58 m of water at peak; over 30 cm for 6.5 h; 30 cm reached 12.0 h into the storm; worst hour 16 mm (85% of the storm) |
| 2 | 0.06 | Central Street | Saugus | 0.14 m of water at peak; worst hour 10 mm (89% of the storm); a culvert within 100 m is overtopped |
| 3 | 0.06 | Elm Street | Saugus | 0.14 m of water at peak; worst hour 10 mm (89% of the storm); a culvert within 100 m is overtopped |
| 4 | 0.06 | Elm Street | Saugus | 0.14 m of water at peak; worst hour 10 mm (89% of the storm) |
| 5 | 0.02 | South Street | Boston | 0.09 m of water at peak; worst hour 4 mm (78% of the storm) |
| 6 | 0.02 | Sunset Road | Winchester | 0.09 m of water at peak; worst hour 16 mm (84% of the storm) |
| 7 | 0.02 | Zito Drive | Saugus | 0.09 m of water at peak; worst hour 10 mm (92% of the storm) |
| 8 | 0.01 | Washington Street | Winchester | 0.08 m of water at peak; worst hour 16 mm (84% of the storm) |
| 9 | 0.01 | Washington Street | Winchester | 0.08 m of water at peak; worst hour 16 mm (84% of the storm) |
| 10 | 0.01 | Washington Street | Winchester | 0.08 m of water at peak; worst hour 16 mm (84% of the storm) |
| 11 | 0.01 | Washington Street | Winchester | 0.08 m of water at peak; worst hour 16 mm (84% of the storm) |
| 12 | 0.01 | Charles Street | Malden | 0.08 m of water at peak; worst hour 16 mm (100% of the storm) |
| 13 | 0.01 | I-93 | Medford | 0.08 m of water at peak; worst hour 11 mm (95% of the storm); water beside the road 0.07 m above its crest (design freeboard 0.30 m; P 0.99) |
| 14 | 0.01 | Jackson Street | Malden | 0.07 m of water at peak; worst hour 16 mm (100% of the storm) |
| 15 | 0.01 | Route 60 | Malden | 0.07 m of water at peak; worst hour 16 mm (100% of the storm); water beside the road 0.04 m above its crest (design freeboard 0.30 m; P 0.99) |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
