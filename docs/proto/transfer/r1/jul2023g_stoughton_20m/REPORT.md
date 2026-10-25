# Road-closure prototype: jul2023g_transfer_jul2023g_stoughton_20m

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on CPU (OpenMP)), 20 m grid, storm from 2023-07-16T11:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 16,553 |
| Expected closures (sum of probabilities) | 33.7 |
| Segments with closure probability >= 50% | 4 (0.5 km) |
| Further segments that may close (stream reaches the road crest) | 5 (0.9 km) |
| Culverts overtopped / surcharged | 22 / 0 of 694 |
| Road segments cut off from hospitals | 0 |
| Worst added trip time to a hospital | 0.0 min |
| Heaviest hour of rain | 41.2 mm |
| Flood model run time | 1382 s |


## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 1.00 | Route 1A | Westwood | 0.74 m of water at peak; over 30 cm for 8.5 h; 30 cm reached 10.0 h into the storm; worst hour 12 mm (26% of the storm); a culvert within 100 m is overtopped |
| 2 | 0.69 | Bolivar Street | Canton | 0.35 m of water at peak; over 30 cm for 5.0 h; 30 cm reached 13.5 h into the storm; worst hour 30 mm (45% of the storm) |
| 3 | 0.57 | Mechanic Street | Canton | 0.32 m of water at peak; over 30 cm for 3.5 h; 30 cm reached 14.5 h into the storm; worst hour 30 mm (45% of the storm) |
| 4 | 0.57 | Mechanic Street | Canton | 0.32 m of water at peak; over 30 cm for 3.5 h; 30 cm reached 14.5 h into the storm; worst hour 30 mm (45% of the storm) |
| 5 | 0.40 | South Street | Walpole | 0.27 m of water at peak; worst hour 12 mm (28% of the storm) |
| 6 | 0.38 | Mill Street | Stoughton | 0.27 m of water at peak; worst hour 33 mm (48% of the storm); a culvert within 100 m is overtopped |
| 7 | 0.38 | Mill Street | Stoughton | 0.27 m of water at peak; worst hour 33 mm (47% of the storm) |
| 8 | 0.34 | Ramp | Randolph | 0.26 m of water at peak; worst hour 36 mm (48% of the storm); a culvert within 100 m is overtopped |
| 9 | 0.34 | Revolution Way | Canton | 0.26 m of water at peak; worst hour 28 mm (43% of the storm); water beside the road 0.48 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.3 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 28 mm; catchment 8.4 ha) (P 1.00) |
| 10 | 0.28 | Route 28 | Quincy | 0.24 m of water at peak; worst hour 35 mm (48% of the storm); a culvert within 100 m is overtopped |
| 11 | 0.28 | Route 28 | Randolph | 0.24 m of water at peak; worst hour 35 mm (48% of the storm); a culvert within 100 m is overtopped |
| 12 | 0.28 | Route 28 | Randolph | 0.24 m of water at peak; worst hour 35 mm (48% of the storm); a culvert within 100 m is overtopped |
| 13 | 0.26 | Ramp | Quincy | 0.24 m of water at peak; worst hour 34 mm (47% of the storm); a culvert within 100 m is overtopped |
| 14 | 0.26 | I-93 | Quincy | 0.24 m of water at peak; worst hour 34 mm (48% of the storm) |
| 15 | 0.23 | Ramp | Randolph | 0.23 m of water at peak; worst hour 36 mm (49% of the storm); a culvert within 100 m is overtopped |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
