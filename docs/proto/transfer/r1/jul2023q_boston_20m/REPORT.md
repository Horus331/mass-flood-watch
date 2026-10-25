# Road-closure prototype: jul2023q_transfer_jul2023q_boston_20m

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on CPU (OpenMP)), 20 m grid, storm from 2023-07-29T10:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 49,897 |
| Expected closures (sum of probabilities) | 242.0 |
| Segments with closure probability >= 50% | 111 (17.7 km) |
| Further segments that may close (stream reaches the road crest) | 445 (67.9 km) |
| Culverts overtopped / surcharged | 51 / 0 of 448 |
| Road segments cut off from hospitals | 0 |
| Worst added trip time to a hospital | 0.0 min |
| Heaviest hour of rain | 45.9 mm |
| Flood model run time | 976 s |


## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 1.00 | Route 99 | Boston | 0.98 m of water at peak; over 30 cm for 2.0 h; 30 cm reached 16.5 h into the storm; worst hour 18 mm (32% of the storm); runoff beside / along the road at 2.1 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.90); road sag 4.3 m deep (underpass, drains sized for the 50-yr hour, 58 mm; peak hour here 18 mm; catchment 13.2 ha) (P 1.00) |
| 2 | 1.00 | Clinton Road | Brookline | 1.04 m of water at peak; over 30 cm for 6.5 h; 30 cm reached 12.0 h into the storm; worst hour 28 mm (34% of the storm); water beside the road 1.00 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 0.9 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.40); road sag 1.2 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 28 mm; catchment 102.5 ha) (P 1.00) |
| 3 | 1.00 | Quincy Street | Boston | 0.71 m of water at peak; over 30 cm for 5.5 h; 30 cm reached 13.0 h into the storm; worst hour 28 mm (39% of the storm); water beside the road 0.63 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 0.9 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.41); road sag 2.1 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 28 mm; catchment 45.8 ha) (P 1.00) |
| 4 | 1.00 | Ramp | Boston | 0.68 m of water at peak; over 30 cm for 5.5 h; 30 cm reached 13.0 h into the storm; worst hour 40 mm (53% of the storm); runoff beside / along the road at 1.0 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.52); road sag 4.2 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 39 mm; catchment 2.8 ha) (P 1.00) |
| 5 | 1.00 | Ramp | Boston | 0.68 m of water at peak; over 30 cm for 5.5 h; 30 cm reached 13.0 h into the storm; worst hour 39 mm (53% of the storm); runoff beside / along the road at 1.0 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.52); road sag 4.2 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 39 mm; catchment 2.8 ha) (P 1.00) |
| 6 | 1.00 | Quincy Street | Boston | 0.63 m of water at peak; over 30 cm for 5.5 h; 30 cm reached 13.0 h into the storm; worst hour 30 mm (40% of the storm); water beside the road 0.50 m above its crest (design freeboard 0.30 m; P 1.00); road sag 1.0 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 30 mm; catchment 45.8 ha) (P 1.00) |
| 7 | 1.00 | Quincy Street | Boston | 0.63 m of water at peak; over 30 cm for 5.5 h; 30 cm reached 13.0 h into the storm; worst hour 30 mm (40% of the storm) |
| 8 | 1.00 | Riverway | Boston | 0.80 m of water at peak; over 30 cm for 5.0 h; 30 cm reached 13.5 h into the storm; worst hour 35 mm (38% of the storm) |
| 9 | 1.00 | Riverway | Boston | 0.80 m of water at peak; over 30 cm for 5.0 h; 30 cm reached 13.5 h into the storm; worst hour 35 mm (38% of the storm) |
| 10 | 1.00 | Brookline Avenue | Boston | 0.76 m of water at peak; over 30 cm for 5.0 h; 30 cm reached 13.5 h into the storm; worst hour 35 mm (39% of the storm) |
| 11 | 1.00 | Brookline Avenue | Boston | 0.76 m of water at peak; over 30 cm for 5.0 h; 30 cm reached 13.5 h into the storm; worst hour 35 mm (39% of the storm) |
| 12 | 1.00 | Ramp | Boston | 1.09 m of water at peak; over 30 cm for 3.5 h; 30 cm reached 15.0 h into the storm; worst hour 43 mm (56% of the storm); water beside the road 0.24 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 2.6 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.57) |
| 13 | 1.00 | Ramp | Boston | 1.09 m of water at peak; over 30 cm for 3.5 h; 30 cm reached 15.0 h into the storm; worst hour 43 mm (56% of the storm); water beside the road 0.24 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 2.6 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.57); road sag 6.5 m deep (underpass, drains sized for the 50-yr hour, 58 mm; peak hour here 42 mm; catchment 281.0 ha) (P 1.00) |
| 14 | 1.00 | Rutherford Avenue | Boston | 0.98 m of water at peak; over 30 cm for 2.0 h; 30 cm reached 16.5 h into the storm; worst hour 18 mm (33% of the storm); runoff beside / along the road at 2.1 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.90); road sag 4.3 m deep (underpass, drains sized for the 50-yr hour, 58 mm; peak hour here 18 mm; catchment 13.2 ha) (P 1.00) |
| 15 | 1.00 | Quincy Street | Boston | 0.59 m of water at peak; over 30 cm for 5.5 h; 30 cm reached 13.0 h into the storm; worst hour 30 mm (41% of the storm); water beside the road 0.41 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 0.6 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.11); road sag 1.0 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 30 mm; catchment 45.8 ha) (P 1.00) |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
