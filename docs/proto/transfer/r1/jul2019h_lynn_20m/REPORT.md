# Road-closure prototype: jul2019h_transfer_jul2019h_lynn_20m

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on CPU (OpenMP)), 20 m grid, storm from 2019-07-31T12:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 33,309 |
| Expected closures (sum of probabilities) | 46.1 |
| Segments with closure probability >= 50% | 0 (0.0 km) |
| Further segments that may close (stream reaches the road crest) | 2 (0.1 km) |
| Culverts overtopped / surcharged | 1 / 0 of 300 |
| Road segments cut off from hospitals | 0 |
| Worst added trip time to a hospital | 0.0 min |
| Heaviest hour of rain | 42.0 mm |
| Flood model run time | 1354 s |


## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 0.10 | Central Street | Saugus | 0.17 m of water at peak; worst hour 18 mm (97% of the storm); a culvert within 100 m is overtopped |
| 2 | 0.10 | Elm Street | Saugus | 0.17 m of water at peak; worst hour 18 mm (97% of the storm); a culvert within 100 m is overtopped |
| 3 | 0.10 | Elm Street | Saugus | 0.17 m of water at peak; worst hour 18 mm (97% of the storm) |
| 4 | 0.07 | Highland Avenue | Winchester | 0.16 m of water at peak; worst hour 4 mm (89% of the storm) |
| 5 | 0.02 | Herschel Street | Lynn | 0.09 m of water at peak; worst hour 25 mm (94% of the storm) |
| 6 | 0.02 | Normandy Road | Lynn | 0.09 m of water at peak; worst hour 25 mm (94% of the storm) |
| 7 | 0.01 | Washington Circle | Woburn | 0.08 m of water at peak; worst hour 4 mm (83% of the storm) |
| 8 | 0.01 | Charles Street | Malden | 0.08 m of water at peak; worst hour 14 mm (86% of the storm) |
| 9 | 0.01 | Archer Street | Lynn | 0.07 m of water at peak; worst hour 26 mm (94% of the storm) |
| 10 | 0.01 | Jackson Street | Malden | 0.07 m of water at peak; worst hour 15 mm (86% of the storm) |
| 11 | 0.01 | Lindenwood Road | Stoneham | 0.07 m of water at peak; worst hour 4 mm (86% of the storm) |
| 12 | 0.01 | Route 60 | Malden | 0.07 m of water at peak; worst hour 15 mm (86% of the storm); water beside the road 0.04 m above its crest (design freeboard 0.30 m; P 0.99) |
| 13 | 0.01 | Route 60 | Malden | 0.07 m of water at peak; worst hour 15 mm (86% of the storm) |
| 14 | 0.01 | Route 60 | Malden | 0.07 m of water at peak; worst hour 15 mm (86% of the storm); water beside the road 0.04 m above its crest (design freeboard 0.30 m; P 0.99) |
| 15 | 0.01 | Valley Road | Lynn | 0.07 m of water at peak; worst hour 23 mm (94% of the storm); runoff beside / along the road at 1.1 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.33) |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
