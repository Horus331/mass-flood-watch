# Road-closure prototype: jul2023r_transfer_jul2023r_lynn_20m

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on CPU (OpenMP)), 20 m grid, storm from 2023-07-29T17:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 22,216 |
| Expected closures (sum of probabilities) | 59.2 |
| Segments with closure probability >= 50% | 8 (0.7 km) |
| Further segments that may close (stream reaches the road crest) | 49 (8.7 km) |
| Culverts overtopped / surcharged | 42 / 1 of 685 |
| Road segments cut off from hospitals | 0 |
| Worst added trip time to a hospital | 0.0 min |
| Heaviest hour of rain | 32.8 mm |
| Flood model run time | 1921 s |


## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 0.84 | Howley Street | Peabody | 0.40 m of water at peak; over 30 cm for 8.5 h; 30 cm reached 10.0 h into the storm; worst hour 22 mm (45% of the storm) |
| 2 | 0.77 | Brookline Street | Lynn | 0.38 m of water at peak; over 30 cm for 6.5 h; 30 cm reached 12.0 h into the storm; worst hour 24 mm (52% of the storm); water beside the road 0.26 m above its crest (design freeboard 0.30 m; P 1.00); road sag 2.0 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 24 mm; catchment 32.8 ha) (P 0.78) |
| 3 | 0.59 | Main Street | Peabody | 0.32 m of water at peak; over 30 cm for 1.5 h; 30 cm reached 10.0 h into the storm; worst hour 22 mm (45% of the storm); a culvert within 100 m is overtopped |
| 4 | 0.58 | Eagen Place | Peabody | 0.32 m of water at peak; over 30 cm for 1.5 h; 30 cm reached 10.0 h into the storm; worst hour 22 mm (45% of the storm); a culvert within 100 m is overtopped |
| 5 | 0.58 | Linden Avenue | Peabody | 0.32 m of water at peak; over 30 cm for 1.5 h; 30 cm reached 10.0 h into the storm; worst hour 22 mm (45% of the storm); a culvert within 100 m is overtopped |
| 6 | 0.58 | Main Street | Peabody | 0.32 m of water at peak; over 30 cm for 1.5 h; 30 cm reached 10.0 h into the storm; worst hour 22 mm (45% of the storm); a culvert within 100 m is overtopped |
| 7 | 0.57 | Clement Avenue | Peabody | 0.32 m of water at peak; over 30 cm for 1.0 h; 30 cm reached 9.5 h into the storm; worst hour 22 mm (43% of the storm); a culvert within 100 m is overtopped |
| 8 | 0.56 | Ayer Street | Peabody | 0.31 m of water at peak; over 30 cm for 1.0 h; 30 cm reached 9.5 h into the storm; worst hour 22 mm (44% of the storm); water beside the road 0.10 m above its crest (design freeboard 0.30 m; P 1.00); a culvert within 100 m is overtopped |
| 9 | 0.49 | Pleasant Street | Peabody | 0.30 m of water at peak; worst hour 22 mm (45% of the storm); a culvert within 100 m is overtopped |
| 10 | 0.47 | Shaws Lane | Peabody | 0.29 m of water at peak; worst hour 22 mm (45% of the storm); a culvert within 100 m is overtopped |
| 11 | 0.44 | Foster Street | Peabody | 0.29 m of water at peak; worst hour 21 mm (42% of the storm); water beside the road 0.24 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.4 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 21 mm; catchment 7.0 ha) (P 0.80) |
| 12 | 0.44 | Pierpont Street | Peabody | 0.29 m of water at peak; worst hour 22 mm (45% of the storm); water beside the road 0.06 m below its crest (design freeboard 0.30 m; P 0.94); a culvert within 100 m is overtopped |
| 13 | 0.43 | Walnut Street | Peabody | 0.28 m of water at peak; worst hour 21 mm (42% of the storm); water beside the road 0.40 m above its crest (design freeboard 0.30 m; P 1.00) |
| 14 | 0.34 | Erie Street | Lynn | 0.26 m of water at peak; worst hour 22 mm (51% of the storm); water beside the road 0.08 m above its crest (design freeboard 0.30 m; P 0.99); road sag 0.4 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 22 mm; catchment 6.6 ha) (P 0.35) |
| 15 | 0.32 | Normandy Road | Lynn | 0.25 m of water at peak; worst hour 25 mm (55% of the storm); water beside the road 0.16 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.5 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 25 mm; catchment 4.0 ha) (P 0.47) |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
