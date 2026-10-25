# Road-closure prototype: sep2020e_transfer_sep2020e_northreading_20m

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on CPU (OpenMP)), 20 m grid, storm from 2020-09-10T15:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 17,202 |
| Expected closures (sum of probabilities) | 25.8 |
| Segments with closure probability >= 50% | 0 (0.0 km) |
| Further segments that may close (stream reaches the road crest) | 2 (0.1 km) |
| Culverts overtopped / surcharged | 3 / 0 of 816 |
| Road segments cut off from hospitals | 0 |
| Worst added trip time to a hospital | 0.0 min |
| Heaviest hour of rain | 23.4 mm |
| Flood model run time | 1228 s |


## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 0.12 | Lockwood Lane | Boxford | 0.18 m of water at peak; worst hour 19 mm (65% of the storm); a culvert within 100 m is overtopped |
| 2 | 0.12 | Lockwood Lane | Boxford | 0.18 m of water at peak; worst hour 19 mm (65% of the storm) |
| 3 | 0.10 | River Road | Topsfield | 0.17 m of water at peak; worst hour 22 mm (70% of the storm); a culvert within 100 m is overtopped |
| 4 | 0.10 | Fuller Lane | Boxford | 0.17 m of water at peak; worst hour 22 mm (70% of the storm); a culvert within 100 m is overtopped |
| 5 | 0.08 | Boston Street | Peabody | 0.16 m of water at peak; worst hour 11 mm (50% of the storm); a culvert within 100 m is overtopped |
| 6 | 0.08 | Boston Street | Peabody | 0.16 m of water at peak; worst hour 11 mm (50% of the storm) |
| 7 | 0.06 | Russell Street | Peabody | 0.15 m of water at peak; worst hour 16 mm (50% of the storm); water beside the road 0.35 m below its crest (design freeboard 0.30 m; P 0.37) |
| 8 | 0.05 | Howley Street | Peabody | 0.13 m of water at peak; worst hour 20 mm (75% of the storm) |
| 9 | 0.04 | Highland Street | Hamilton | 0.13 m of water at peak; worst hour 14 mm (56% of the storm) |
| 10 | 0.03 | Foster Street | Peabody | 0.12 m of water at peak; worst hour 18 mm (66% of the storm); water beside the road 0.02 m above its crest (design freeboard 0.30 m; P 0.98) |
| 11 | 0.03 | Johnson Street | North Andover | 0.12 m of water at peak; worst hour 15 mm (54% of the storm) |
| 12 | 0.03 | Route 97 | Wenham | 0.11 m of water at peak; worst hour 10 mm (49% of the storm) |
| 13 | 0.03 | Crowninshield Street | Peabody | 0.10 m of water at peak; worst hour 18 mm (59% of the storm) |
| 14 | 0.02 | Walnut Street | Peabody | 0.10 m of water at peak; worst hour 19 mm (66% of the storm); water beside the road 0.19 m below its crest (design freeboard 0.30 m; P 0.76) |
| 15 | 0.02 | Longham Road | Beverly | 0.10 m of water at peak; worst hour 14 mm (50% of the storm) |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
