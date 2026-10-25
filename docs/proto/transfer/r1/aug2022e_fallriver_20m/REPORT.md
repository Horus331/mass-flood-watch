# Road-closure prototype: aug2022e_transfer_aug2022e_fallriver_20m

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on CPU (OpenMP)), 20 m grid, storm from 2022-08-09T15:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 11,790 |
| Expected closures (sum of probabilities) | 18.7 |
| Segments with closure probability >= 50% | 0 (0.0 km) |
| Further segments that may close (stream reaches the road crest) | 7 (1.1 km) |
| Culverts overtopped / surcharged | 4 / 0 of 504 |
| Road segments cut off from hospitals | 0 |
| Worst added trip time to a hospital | 0.0 min |
| Heaviest hour of rain | 44.0 mm |
| Flood model run time | 1002 s |


## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 0.32 | Reed Road | Westport | 0.25 m of water at peak; worst hour 11 mm (100% of the storm); a culvert within 100 m is overtopped |
| 2 | 0.12 | Union Avenue | Westport | 0.18 m of water at peak; worst hour 15 mm (100% of the storm); a culvert within 100 m is overtopped |
| 3 | 0.12 | Purchase Street | New Bedford | 0.18 m of water at peak; worst hour 32 mm (91% of the storm); water beside the road 0.45 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 1.4 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.75); road sag 0.5 m deep (underpass, drains sized for the 50-yr hour, 58 mm; peak hour here 30 mm; catchment 4.3 ha) (P 0.95) |
| 4 | 0.10 | Purchase Street | New Bedford | 0.17 m of water at peak; worst hour 38 mm (92% of the storm); water beside the road 0.40 m above its crest (design freeboard 0.30 m; P 1.00) |
| 5 | 0.10 | Deane Street | New Bedford | 0.17 m of water at peak; worst hour 38 mm (92% of the storm); water beside the road 0.40 m above its crest (design freeboard 0.30 m; P 1.00) |
| 6 | 0.07 | Route 177 | Westport | 0.15 m of water at peak; worst hour 11 mm (100% of the storm); a culvert within 100 m is overtopped |
| 7 | 0.06 | Logan Street | New Bedford | 0.15 m of water at peak; worst hour 27 mm (89% of the storm) |
| 8 | 0.06 | Logan Street | New Bedford | 0.15 m of water at peak; worst hour 26 mm (89% of the storm); water beside the road 0.24 m below its crest (design freeboard 0.30 m; P 0.65) |
| 9 | 0.06 | Logan Street | New Bedford | 0.15 m of water at peak; worst hour 26 mm (89% of the storm); water beside the road 0.24 m below its crest (design freeboard 0.30 m; P 0.65) |
| 10 | 0.06 | Route 6 | Dartmouth | 0.15 m of water at peak; worst hour 18 mm (98% of the storm) |
| 11 | 0.04 | Purchase Street | New Bedford | 0.13 m of water at peak; worst hour 35 mm (92% of the storm); water beside the road 0.14 m above its crest (design freeboard 0.30 m; P 1.00) |
| 12 | 0.04 | Ramp | Dartmouth | 0.12 m of water at peak; worst hour 31 mm (96% of the storm) |
| 13 | 0.03 | Drift Road | Westport | 0.12 m of water at peak; worst hour 7 mm (96% of the storm) |
| 14 | 0.03 | Route 6 | Westport | 0.12 m of water at peak; worst hour 21 mm (100% of the storm) |
| 15 | 0.03 | Drift Road | Westport | 0.12 m of water at peak; worst hour 7 mm (97% of the storm) |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
