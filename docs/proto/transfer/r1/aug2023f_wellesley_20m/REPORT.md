# Road-closure prototype: aug2023f_transfer_aug2023f_wellesley_20m

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on CPU (OpenMP)), 20 m grid, storm from 2023-08-08T07:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 47,365 |
| Expected closures (sum of probabilities) | 265.5 |
| Segments with closure probability >= 50% | 133 (29.2 km) |
| Further segments that may close (stream reaches the road crest) | 500 (79.4 km) |
| Culverts overtopped / surcharged | 107 / 2 of 729 |
| Road segments cut off from hospitals | 0 |
| Worst added trip time to a hospital | 0.0 min |
| Heaviest hour of rain | 71.2 mm |
| Flood model run time | 1447 s |


## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 1.00 | Route 99 | Boston | 1.29 m of water at peak; over 30 cm for 8.0 h; 30 cm reached 10.5 h into the storm; worst hour 34 mm (60% of the storm); water beside the road 0.46 m below its crest (design freeboard 0.30 m; P 0.15); runoff beside / along the road at 3.0 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.59); road sag 4.1 m deep (underpass, drains sized for the 50-yr hour, 58 mm; peak hour here 34 mm; catchment 13.2 ha) (P 1.00) |
| 2 | 1.00 | Ramp | Weston | 1.14 m of water at peak; over 30 cm for 18.0 h; 30 cm reached 0.5 h into the storm; worst hour 33 mm (66% of the storm); a culvert within 100 m is overtopped |
| 3 | 1.00 | Mill Street | Arlington | 1.78 m of water at peak; over 30 cm for 11.0 h; 30 cm reached 7.5 h into the storm; worst hour 34 mm (71% of the storm); a culvert within 100 m is overtopped |
| 4 | 1.00 | Clinton Road | Brookline | 1.14 m of water at peak; over 30 cm for 10.5 h; 30 cm reached 8.0 h into the storm; worst hour 45 mm (60% of the storm); water beside the road 1.10 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 0.9 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.45); road sag 1.2 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 45 mm; catchment 102.5 ha) (P 1.00) |
| 5 | 1.00 | Croftdale Road | Newton | 0.80 m of water at peak; over 30 cm for 10.5 h; 30 cm reached 8.0 h into the storm; worst hour 50 mm (69% of the storm); water beside the road 0.75 m above its crest (design freeboard 0.30 m; P 1.00) |
| 6 | 1.00 | White Place | Brookline | 0.65 m of water at peak; over 30 cm for 8.5 h; 30 cm reached 10.0 h into the storm; worst hour 27 mm (50% of the storm); water beside the road 0.90 m above its crest (design freeboard 0.30 m; P 1.00); fast water: depth x speed 0.22 m2/s (small cars unstable from 0.3); runoff beside / along the road at 1.4 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.40); road sag 1.5 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 27 mm; catchment 16.6 ha) (P 1.00) |
| 7 | 1.00 | Rutherford Avenue | Boston | 1.29 m of water at peak; over 30 cm for 8.0 h; 30 cm reached 10.5 h into the storm; worst hour 34 mm (60% of the storm); water beside the road 0.46 m below its crest (design freeboard 0.30 m; P 0.15); runoff beside / along the road at 1.4 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.59); road sag 4.3 m deep (underpass, drains sized for the 50-yr hour, 58 mm; peak hour here 34 mm; catchment 13.2 ha) (P 1.00) |
| 8 | 1.00 | Willow Street | Newton | 0.74 m of water at peak; over 30 cm for 7.5 h; 30 cm reached 8.5 h into the storm; worst hour 49 mm (70% of the storm); a culvert within 100 m is overtopped |
| 9 | 1.00 | Lyman Street | Newton | 0.74 m of water at peak; over 30 cm for 7.5 h; 30 cm reached 8.5 h into the storm; worst hour 49 mm (70% of the storm); a culvert within 100 m is overtopped |
| 10 | 1.00 | Sumner Street | Newton | 0.74 m of water at peak; over 30 cm for 7.5 h; 30 cm reached 8.5 h into the storm; worst hour 49 mm (70% of the storm); a culvert within 100 m is overtopped |
| 11 | 1.00 | Electric Avenue | Boston | 0.63 m of water at peak; over 30 cm for 7.5 h; 30 cm reached 11.0 h into the storm; worst hour 46 mm (72% of the storm); water beside the road 0.60 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 1.8 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.57); road sag 2.1 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 46 mm; catchment 15.5 ha) (P 1.00) |
| 12 | 1.00 | Riverway | Boston | 0.61 m of water at peak; over 30 cm for 6.0 h; 30 cm reached 12.5 h into the storm; worst hour 33 mm (59% of the storm) |
| 13 | 1.00 | Riverway | Boston | 0.61 m of water at peak; over 30 cm for 6.0 h; 30 cm reached 12.5 h into the storm; worst hour 33 mm (59% of the storm) |
| 14 | 1.00 | I-90 | Newton | 0.59 m of water at peak; over 30 cm for 6.5 h; 30 cm reached 12.0 h into the storm; worst hour 38 mm (79% of the storm); water beside the road 0.66 m above its crest (design freeboard 0.30 m; P 1.00); fast water: depth x speed 0.23 m2/s (small cars unstable from 0.3); runoff beside / along the road at 1.2 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.64); road sag 0.4 m deep (underpass, drains sized for the 50-yr hour, 58 mm; peak hour here 37 mm; catchment 32.1 ha) (P 1.00) |
| 15 | 1.00 | Route 99 | Boston | 0.58 m of water at peak; over 30 cm for 6.5 h; 30 cm reached 12.0 h into the storm; worst hour 34 mm (61% of the storm); road sag 3.9 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 34 mm; catchment 16.2 ha) (P 1.00) |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
