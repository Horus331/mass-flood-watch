# Road-closure prototype: aug2018k_transfer_aug2018k_lawrence_20m

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on CPU (OpenMP)), 20 m grid, storm from 2018-08-11T11:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 14,965 |
| Expected closures (sum of probabilities) | 23.3 |
| Segments with closure probability >= 50% | 0 (0.0 km) |
| Further segments that may close (stream reaches the road crest) | 2 (0.2 km) |
| Culverts overtopped / surcharged | 1 / 0 of 781 |
| Road segments cut off from hospitals | 0 |
| Worst added trip time to a hospital | 0.0 min |
| Heaviest hour of rain | 16.0 mm |
| Flood model run time | 1024 s |


## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 0.37 | Curtis Street | Methuen | 0.27 m of water at peak; worst hour 14 mm (28% of the storm); a culvert within 100 m is overtopped |
| 2 | 0.37 | Bicknell Avenue | Methuen | 0.27 m of water at peak; worst hour 14 mm (28% of the storm); water beside the road 0.01 m above its crest (design freeboard 0.30 m; P 0.98); a culvert within 100 m is overtopped |
| 3 | 0.13 | Logan Street | Lawrence | 0.19 m of water at peak; worst hour 14 mm (28% of the storm); water beside the road 0.07 m below its crest (design freeboard 0.30 m; P 0.94); road sag 0.6 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 14 mm; catchment 26.0 ha) (P 0.13) |
| 4 | 0.10 | Route 110 | Lawrence | 0.17 m of water at peak; worst hour 14 mm (29% of the storm) |
| 5 | 0.10 | Knox Street | Lawrence | 0.17 m of water at peak; worst hour 14 mm (29% of the storm); water beside the road 0.10 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.3 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 14 mm; catchment 26.0 ha) (P 0.15) |
| 6 | 0.06 | Lorenzo Circle | Methuen | 0.14 m of water at peak; worst hour 15 mm (29% of the storm) |
| 7 | 0.04 | Route 110 | Methuen | 0.13 m of water at peak; worst hour 14 mm (28% of the storm) |
| 8 | 0.04 | Pinnacle Street | Tewksbury | 0.13 m of water at peak; worst hour 10 mm (36% of the storm) |
| 9 | 0.03 | Custer Street | Lawrence | 0.12 m of water at peak; worst hour 14 mm (28% of the storm); water beside the road 0.07 m below its crest (design freeboard 0.30 m; P 0.94) |
| 10 | 0.03 | Lowell Street | Methuen | 0.12 m of water at peak; worst hour 11 mm (29% of the storm) |
| 11 | 0.03 | Wheeler Street | Methuen | 0.12 m of water at peak; worst hour 10 mm (28% of the storm) |
| 12 | 0.03 | Juniper Street | Lawrence | 0.11 m of water at peak; worst hour 15 mm (31% of the storm); water beside the road 0.01 m below its crest (design freeboard 0.30 m; P 0.97) |
| 13 | 0.03 | Wheeler Road | Dracut | 0.11 m of water at peak; worst hour 10 mm (26% of the storm) |
| 14 | 0.02 | (unnamed) | Dracut | 0.10 m of water at peak; worst hour 10 mm (26% of the storm) |
| 15 | 0.02 | Methuen Street | Dracut | 0.10 m of water at peak; worst hour 10 mm (26% of the storm) |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
