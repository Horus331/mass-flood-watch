# Road-closure prototype: jul2018f_transfer_jul2018f_cambridge_20m

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on CPU (OpenMP)), 20 m grid, storm from 2018-07-17T11:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 41,687 |
| Expected closures (sum of probabilities) | 66.9 |
| Segments with closure probability >= 50% | 0 (0.0 km) |
| Further segments that may close (stream reaches the road crest) | 23 (2.8 km) |
| Culverts overtopped / surcharged | 1 / 0 of 272 |
| Road segments cut off from hospitals | 0 |
| Worst added trip time to a hospital | 0.0 min |
| Heaviest hour of rain | 26.2 mm |
| Flood model run time | 1613 s |


## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 0.49 | Mill Street | Arlington | 0.30 m of water at peak; worst hour 15 mm (34% of the storm); a culvert within 100 m is overtopped |
| 2 | 0.12 | I-93 | Medford | 0.18 m of water at peak; worst hour 11 mm (29% of the storm); water beside the road 0.18 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 0.7 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.24); road sag 1.6 m deep (underpass, drains sized for the 50-yr hour, 58 mm; peak hour here 11 mm; catchment 25.1 ha) (P 0.33) |
| 3 | 0.09 | Clinton Road | Brookline | 0.17 m of water at peak; worst hour 12 mm (31% of the storm); water beside the road 0.13 m above its crest (design freeboard 0.30 m; P 1.00); road sag 1.2 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 12 mm; catchment 102.5 ha) (P 0.60) |
| 4 | 0.09 | Quincy Street | Boston | 0.17 m of water at peak; worst hour 15 mm (37% of the storm); water beside the road 0.01 m above its crest (design freeboard 0.30 m; P 0.98); runoff beside / along the road at 1.2 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.68) |
| 5 | 0.08 | Quincy Street | Boston | 0.16 m of water at peak; worst hour 14 mm (36% of the storm); water beside the road 0.02 m above its crest (design freeboard 0.30 m; P 0.98) |
| 6 | 0.08 | Quincy Street | Boston | 0.16 m of water at peak; worst hour 14 mm (36% of the storm) |
| 7 | 0.08 | Route 28 | Somerville | 0.16 m of water at peak; worst hour 11 mm (26% of the storm) |
| 8 | 0.06 | Route 28 | Somerville | 0.14 m of water at peak; worst hour 12 mm (27% of the storm) |
| 9 | 0.05 | Suffolk Street | Malden | 0.14 m of water at peak; worst hour 11 mm (25% of the storm); water beside the road 0.10 m below its crest (design freeboard 0.30 m; P 0.91) |
| 10 | 0.05 | Bryant Street | Malden | 0.14 m of water at peak; worst hour 11 mm (25% of the storm); water beside the road 0.04 m below its crest (design freeboard 0.30 m; P 0.96) |
| 11 | 0.05 | Notre Dame Street | Boston | 0.13 m of water at peak; worst hour 14 mm (33% of the storm); water beside the road 0.06 m above its crest (design freeboard 0.30 m; P 0.99) |
| 12 | 0.05 | Charlame Place | Boston | 0.13 m of water at peak; worst hour 14 mm (35% of the storm); water beside the road 0.01 m below its crest (design freeboard 0.30 m; P 0.97) |
| 13 | 0.05 | Charlame Street | Boston | 0.13 m of water at peak; worst hour 14 mm (35% of the storm); water beside the road 0.01 m below its crest (design freeboard 0.30 m; P 0.97) |
| 14 | 0.04 | Rockland Street | Boston | 0.13 m of water at peak; worst hour 14 mm (34% of the storm); water beside the road 0.03 m below its crest (design freeboard 0.30 m; P 0.96) |
| 15 | 0.04 | Dalton Road | Belmont | 0.13 m of water at peak; worst hour 15 mm (32% of the storm); water beside the road 0.05 m above its crest (design freeboard 0.30 m; P 0.99) |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
