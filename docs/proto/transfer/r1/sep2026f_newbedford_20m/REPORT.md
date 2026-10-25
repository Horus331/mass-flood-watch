# Road-closure prototype: sep2026f_transfer_sep2026f_newbedford_20m

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on CPU (OpenMP)), 20 m grid, storm from 2026-09-26T12:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 11,669 |
| Expected closures (sum of probabilities) | 20.7 |
| Segments with closure probability >= 50% | 1 (0.2 km) |
| Further segments that may close (stream reaches the road crest) | 7 (0.6 km) |
| Culverts overtopped / surcharged | 7 / 0 of 476 |
| Road segments cut off from hospitals | 0 |
| Worst added trip time to a hospital | 0.0 min |
| Heaviest hour of rain | 31.8 mm |
| Flood model run time | 1459 s |


## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 0.57 | Reed Road | Westport | 0.32 m of water at peak; over 30 cm for 6.5 h; 30 cm reached 12.0 h into the storm; worst hour 29 mm (45% of the storm); a culvert within 100 m is overtopped |
| 2 | 0.26 | Union Avenue | Westport | 0.23 m of water at peak; worst hour 29 mm (45% of the storm); a culvert within 100 m is overtopped |
| 3 | 0.12 | Pleasant Street | Fall River | 0.18 m of water at peak; worst hour 15 mm (29% of the storm); water beside the road 0.09 m above its crest (design freeboard 0.30 m; P 1.00); road sag 1.2 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 15 mm; catchment 28.9 ha) (P 0.12) |
| 4 | 0.12 | County Street | Fall River | 0.18 m of water at peak; worst hour 15 mm (29% of the storm); water beside the road 0.09 m above its crest (design freeboard 0.30 m; P 1.00); road sag 1.2 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 15 mm; catchment 28.9 ha) (P 0.12) |
| 5 | 0.12 | Pleasant Street | Fall River | 0.18 m of water at peak; worst hour 15 mm (29% of the storm); water beside the road 0.09 m above its crest (design freeboard 0.30 m; P 1.00); road sag 1.2 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 15 mm; catchment 28.9 ha) (P 0.12) |
| 6 | 0.10 | Route 6 | Dartmouth | 0.17 m of water at peak; worst hour 31 mm (47% of the storm); a culvert within 100 m is overtopped |
| 7 | 0.09 | Route 6 | Dartmouth | 0.17 m of water at peak; worst hour 31 mm (47% of the storm); a culvert within 100 m is overtopped |
| 8 | 0.08 | Carlisa Drive | Fall River | 0.16 m of water at peak; worst hour 14 mm (27% of the storm); water beside the road 0.12 m above its crest (design freeboard 0.30 m; P 1.00) |
| 9 | 0.07 | North Main Street | Fall River | 0.16 m of water at peak; worst hour 13 mm (24% of the storm); a culvert within 100 m is overtopped |
| 10 | 0.07 | Route 177 | Westport | 0.15 m of water at peak; worst hour 29 mm (45% of the storm); a culvert within 100 m is overtopped |
| 11 | 0.06 | Route 6 | Dartmouth | 0.15 m of water at peak; worst hour 22 mm (41% of the storm) |
| 12 | 0.06 | Chase Road | Dartmouth | 0.14 m of water at peak; worst hour 25 mm (42% of the storm) |
| 13 | 0.06 | Bedford Street | Fall River | 0.14 m of water at peak; worst hour 14 mm (27% of the storm); water beside the road 0.11 m above its crest (design freeboard 0.30 m; P 1.00) |
| 14 | 0.04 | Gifford Road | Westport | 0.13 m of water at peak; worst hour 28 mm (44% of the storm) |
| 15 | 0.04 | Flag Swamp Road | Dartmouth | 0.13 m of water at peak; worst hour 14 mm (25% of the storm) |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
