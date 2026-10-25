# Road-closure prototype: aug2019f_transfer_aug2019f_tuftscollege_20m

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on CPU (OpenMP)), 20 m grid, storm from 2019-08-07T21:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 46,463 |
| Expected closures (sum of probabilities) | 170.9 |
| Segments with closure probability >= 50% | 54 (7.2 km) |
| Further segments that may close (stream reaches the road crest) | 337 (49.2 km) |
| Culverts overtopped / surcharged | 39 / 1 of 543 |
| Road segments cut off from hospitals | 0 |
| Worst added trip time to a hospital | 0.0 min |
| Heaviest hour of rain | 26.7 mm |
| Flood model run time | 1302 s |


## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 1.00 | Route 99 | Boston | 0.90 m of water at peak; over 30 cm for 5.0 h; 30 cm reached 13.5 h into the storm; worst hour 14 mm (33% of the storm); road sag 4.3 m deep (underpass, drains sized for the 50-yr hour, 58 mm; peak hour here 14 mm; catchment 13.2 ha) (P 1.00) |
| 2 | 1.00 | Mill Street | Arlington | 1.29 m of water at peak; over 30 cm for 11.0 h; 30 cm reached 7.5 h into the storm; worst hour 21 mm (38% of the storm); a culvert within 100 m is overtopped |
| 3 | 1.00 | Highland Avenue | Winchester | 2.62 m of water at peak; over 30 cm for 10.0 h; 30 cm reached 8.5 h into the storm; worst hour 15 mm (32% of the storm); a culvert within 100 m is overtopped |
| 4 | 1.00 | Clinton Road | Brookline | 0.87 m of water at peak; over 30 cm for 10.0 h; 30 cm reached 8.5 h into the storm; worst hour 22 mm (42% of the storm); water beside the road 0.83 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 0.9 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.20); road sag 1.2 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 22 mm; catchment 102.5 ha) (P 1.00) |
| 5 | 1.00 | Rutherford Avenue | Boston | 0.90 m of water at peak; over 30 cm for 5.0 h; 30 cm reached 13.5 h into the storm; worst hour 14 mm (33% of the storm); road sag 4.3 m deep (underpass, drains sized for the 50-yr hour, 58 mm; peak hour here 14 mm; catchment 13.2 ha) (P 1.00) |
| 6 | 0.99 | Tyler Terrace | Newton | 0.53 m of water at peak; worst hour 22 mm (44% of the storm) |
| 7 | 0.99 | Pleasant Street | Newton | 0.53 m of water at peak; worst hour 22 mm (44% of the storm); water beside the road 3.98 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 2.1 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.65); a culvert within 100 m is overtopped |
| 8 | 0.98 | Quincy Street | Malden | 0.51 m of water at peak; over 30 cm for 5.5 h; 30 cm reached 13.0 h into the storm; worst hour 16 mm (32% of the storm); water beside the road 0.37 m above its crest (design freeboard 0.30 m; P 1.00); road sag 1.0 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 16 mm; catchment 94.2 ha) (P 0.98) |
| 9 | 0.98 | I-93 | Medford | 0.50 m of water at peak; over 30 cm for 4.5 h; 30 cm reached 8.0 h into the storm; worst hour 18 mm (33% of the storm); water beside the road 0.50 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 2.2 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.41); road sag 1.6 m deep (underpass, drains sized for the 50-yr hour, 58 mm; peak hour here 18 mm; catchment 25.1 ha) (P 1.00) |
| 10 | 0.95 | Willow Street | Newton | 0.47 m of water at peak; worst hour 22 mm (43% of the storm); a culvert within 100 m is overtopped |
| 11 | 0.95 | Lyman Street | Newton | 0.47 m of water at peak; worst hour 22 mm (43% of the storm); a culvert within 100 m is overtopped |
| 12 | 0.95 | Sumner Street | Newton | 0.47 m of water at peak; worst hour 22 mm (43% of the storm); a culvert within 100 m is overtopped |
| 13 | 0.94 | Route 28 | Somerville | 0.46 m of water at peak; over 30 cm for 8.0 h; 30 cm reached 10.5 h into the storm; worst hour 16 mm (32% of the storm); road sag 2.4 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 16 mm; catchment 72.9 ha) (P 0.94) |
| 14 | 0.94 | Beacon Street | Newton | 0.46 m of water at peak; worst hour 22 mm (43% of the storm); water beside the road 0.20 m below its crest (design freeboard 0.30 m; P 0.74); a culvert within 100 m is overtopped |
| 15 | 0.94 | Gray Cliff Road | Newton | 0.46 m of water at peak; worst hour 22 mm (43% of the storm); water beside the road 0.13 m below its crest (design freeboard 0.30 m; P 0.87); a culvert within 100 m is overtopped |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
