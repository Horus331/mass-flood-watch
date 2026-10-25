# Road-closure prototype: jul2021h_transfer_jul2021h_melrose_20m

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on CPU (OpenMP)), 20 m grid, storm from 2021-07-09T09:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 27,538 |
| Expected closures (sum of probabilities) | 74.1 |
| Segments with closure probability >= 50% | 6 (1.7 km) |
| Further segments that may close (stream reaches the road crest) | 94 (14.4 km) |
| Culverts overtopped / surcharged | 52 / 0 of 601 |
| Road segments cut off from hospitals | 0 |
| Worst added trip time to a hospital | 0.0 min |
| Heaviest hour of rain | 17.6 mm |
| Flood model run time | 1599 s |


## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 0.83 | Quincy Street | Malden | 0.40 m of water at peak; over 30 cm for 3.5 h; 30 cm reached 15.0 h into the storm; worst hour 15 mm (28% of the storm); water beside the road 0.26 m above its crest (design freeboard 0.30 m; P 1.00); road sag 1.0 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 15 mm; catchment 94.2 ha) (P 0.83) |
| 2 | 0.77 | Russell Street | Peabody | 0.38 m of water at peak; over 30 cm for 7.0 h; 30 cm reached 11.5 h into the storm; worst hour 16 mm (24% of the storm); water beside the road 0.12 m below its crest (design freeboard 0.30 m; P 0.88); a culvert within 100 m is overtopped |
| 3 | 0.69 | I-93 | Medford | 0.35 m of water at peak; over 30 cm for 4.0 h; 30 cm reached 7.5 h into the storm; worst hour 15 mm (27% of the storm); water beside the road 0.34 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 1.8 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.90); road sag 1.6 m deep (underpass, drains sized for the 50-yr hour, 58 mm; peak hour here 15 mm; catchment 25.1 ha) (P 0.90) |
| 4 | 0.67 | Howley Street | Peabody | 0.34 m of water at peak; over 30 cm for 7.5 h; 30 cm reached 11.0 h into the storm; worst hour 12 mm (23% of the storm) |
| 5 | 0.52 | Brookline Street | Lynn | 0.31 m of water at peak; over 30 cm for 1.5 h; 30 cm reached 14.0 h into the storm; worst hour 14 mm (26% of the storm); water beside the road 0.19 m above its crest (design freeboard 0.30 m; P 1.00); road sag 2.0 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 14 mm; catchment 32.8 ha) (P 0.53) |
| 6 | 0.52 | Suffolk Street | Malden | 0.30 m of water at peak; over 30 cm for 1.5 h; 30 cm reached 11.5 h into the storm; worst hour 15 mm (28% of the storm); water beside the road 0.20 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.5 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 15 mm; catchment 84.6 ha) (P 0.91) |
| 7 | 0.43 | Rutledge Road | Peabody | 0.28 m of water at peak; worst hour 16 mm (24% of the storm); water beside the road 0.33 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.8 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 16 mm; catchment 8.2 ha) (P 0.45) |
| 8 | 0.42 | Eagen Place | Peabody | 0.28 m of water at peak; worst hour 13 mm (23% of the storm); a culvert within 100 m is overtopped |
| 9 | 0.42 | Linden Avenue | Peabody | 0.28 m of water at peak; worst hour 13 mm (23% of the storm); a culvert within 100 m is overtopped |
| 10 | 0.42 | Main Street | Peabody | 0.28 m of water at peak; worst hour 13 mm (23% of the storm); a culvert within 100 m is overtopped |
| 11 | 0.42 | Main Street | Peabody | 0.28 m of water at peak; worst hour 13 mm (23% of the storm); a culvert within 100 m is overtopped |
| 12 | 0.42 | Walnut Street | Peabody | 0.28 m of water at peak; worst hour 13 mm (23% of the storm); water beside the road 0.40 m above its crest (design freeboard 0.30 m; P 1.00) |
| 13 | 0.41 | Clement Avenue | Peabody | 0.28 m of water at peak; worst hour 13 mm (24% of the storm); a culvert within 100 m is overtopped |
| 14 | 0.40 | Boston Street | Peabody | 0.28 m of water at peak; worst hour 15 mm (24% of the storm); a culvert within 100 m is overtopped |
| 15 | 0.40 | Boston Street | Peabody | 0.28 m of water at peak; worst hour 15 mm (24% of the storm) |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
