# Road-closure prototype: jul2020g_transfer_jul2020g_beverly_20m

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on CPU (OpenMP)), 20 m grid, storm from 2020-07-23T12:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 7,722 |
| Expected closures (sum of probabilities) | 14.1 |
| Segments with closure probability >= 50% | 0 (0.0 km) |
| Further segments that may close (stream reaches the road crest) | 5 (0.5 km) |
| Culverts overtopped / surcharged | 9 / 0 of 475 |
| Road segments cut off from hospitals | 0 |
| Worst added trip time to a hospital | 0.0 min |
| Heaviest hour of rain | 56.1 mm |
| Flood model run time | 2216 s |


## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 0.24 | Magnolia Avenue | Gloucester | 0.23 m of water at peak; worst hour 42 mm (75% of the storm); a culvert within 100 m is overtopped |
| 2 | 0.19 | School Street | Manchester-By-The-Sea | 0.21 m of water at peak; worst hour 42 mm (75% of the storm); a culvert within 100 m is overtopped |
| 3 | 0.13 | Mansfield Street | Gloucester | 0.19 m of water at peak; worst hour 53 mm (74% of the storm); water beside the road 0.03 m above its crest (design freeboard 0.30 m; P 0.99) |
| 4 | 0.11 | Longham Road | Beverly | 0.18 m of water at peak; worst hour 17 mm (73% of the storm); a culvert within 100 m is overtopped |
| 5 | 0.11 | Route 127 | Manchester-By-The-Sea | 0.18 m of water at peak; worst hour 43 mm (75% of the storm); a culvert within 100 m is overtopped |
| 6 | 0.11 | Beach Street | Manchester-By-The-Sea | 0.18 m of water at peak; worst hour 44 mm (73% of the storm); a culvert within 100 m is overtopped |
| 7 | 0.10 | Lewis Court | Gloucester | 0.17 m of water at peak; worst hour 54 mm (74% of the storm); water beside the road 0.02 m below its crest (design freeboard 0.30 m; P 0.97) |
| 8 | 0.09 | Mill Street | Manchester-By-The-Sea | 0.17 m of water at peak; worst hour 42 mm (78% of the storm); a culvert within 100 m is overtopped |
| 9 | 0.08 | Gould Court | Gloucester | 0.16 m of water at peak; worst hour 53 mm (75% of the storm); water beside the road 0.06 m above its crest (design freeboard 0.30 m; P 0.99) |
| 10 | 0.07 | Route 127 | Manchester-By-The-Sea | 0.15 m of water at peak; worst hour 44 mm (74% of the storm); a culvert within 100 m is overtopped |
| 11 | 0.06 | Route 128 | Gloucester | 0.14 m of water at peak; worst hour 37 mm (77% of the storm) |
| 12 | 0.06 | Route 128 | Gloucester | 0.14 m of water at peak; worst hour 36 mm (76% of the storm) |
| 13 | 0.05 | Magnolia Avenue | Gloucester | 0.13 m of water at peak; worst hour 43 mm (75% of the storm); a culvert within 100 m is overtopped |
| 14 | 0.04 | Grove Street | Essex | 0.13 m of water at peak; worst hour 20 mm (71% of the storm) |
| 15 | 0.04 | Apple Street | Essex | 0.13 m of water at peak; worst hour 17 mm (72% of the storm) |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
