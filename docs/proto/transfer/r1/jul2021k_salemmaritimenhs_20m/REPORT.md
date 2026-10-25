# Road-closure prototype: jul2021k_transfer_jul2021k_salemmaritimenhs_20m

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on CPU (OpenMP)), 20 m grid, storm from 2021-07-12T05:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 20,028 |
| Expected closures (sum of probabilities) | 30.1 |
| Segments with closure probability >= 50% | 0 (0.0 km) |
| Further segments that may close (stream reaches the road crest) | 2 (0.1 km) |
| Culverts overtopped / surcharged | 5 / 1 of 669 |
| Road segments cut off from hospitals | 0 |
| Worst added trip time to a hospital | 0.0 min |
| Heaviest hour of rain | 25.9 mm |
| Flood model run time | 1179 s |


## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 0.29 | Longham Road | Beverly | 0.24 m of water at peak; worst hour 22 mm (55% of the storm); a culvert within 100 m is overtopped |
| 2 | 0.14 | Larch Row | Wenham | 0.19 m of water at peak; worst hour 22 mm (54% of the storm); a culvert within 100 m is overtopped |
| 3 | 0.10 | Central Street | Saugus | 0.17 m of water at peak; worst hour 10 mm (32% of the storm); a culvert within 100 m is overtopped |
| 4 | 0.10 | Elm Street | Saugus | 0.17 m of water at peak; worst hour 10 mm (32% of the storm); a culvert within 100 m is overtopped |
| 5 | 0.10 | Elm Street | Saugus | 0.17 m of water at peak; worst hour 10 mm (32% of the storm) |
| 6 | 0.08 | Russell Street | Peabody | 0.16 m of water at peak; worst hour 14 mm (41% of the storm); water beside the road 0.34 m below its crest (design freeboard 0.30 m; P 0.41); a culvert within 100 m is overtopped |
| 7 | 0.06 | Goodwin Road | Beverly | 0.15 m of water at peak; worst hour 23 mm (60% of the storm); water beside the road 0.38 m below its crest (design freeboard 0.30 m; P 0.30) |
| 8 | 0.06 | Greenwood Avenue | Beverly | 0.15 m of water at peak; worst hour 23 mm (60% of the storm) |
| 9 | 0.06 | Boston Street | Peabody | 0.14 m of water at peak; worst hour 10 mm (34% of the storm) |
| 10 | 0.06 | Boston Street | Peabody | 0.14 m of water at peak; worst hour 10 mm (34% of the storm) |
| 11 | 0.05 | Howley Street | Peabody | 0.14 m of water at peak; worst hour 11 mm (34% of the storm) |
| 12 | 0.05 | Foster Street | Peabody | 0.13 m of water at peak; worst hour 12 mm (36% of the storm); water beside the road 0.03 m above its crest (design freeboard 0.30 m; P 0.99) |
| 13 | 0.05 | Holly Lane | Beverly | 0.13 m of water at peak; worst hour 26 mm (57% of the storm) |
| 14 | 0.05 | Holly Lane | Beverly | 0.13 m of water at peak; worst hour 26 mm (57% of the storm) |
| 15 | 0.04 | Route 22 | Beverly | 0.13 m of water at peak; worst hour 26 mm (58% of the storm) |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
