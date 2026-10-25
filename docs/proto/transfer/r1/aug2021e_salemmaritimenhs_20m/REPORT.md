# Road-closure prototype: aug2021e_transfer_aug2021e_salemmaritimenhs_20m

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on CPU (OpenMP)), 20 m grid, storm from 2021-08-19T09:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 35,327 |
| Expected closures (sum of probabilities) | 312.4 |
| Segments with closure probability >= 50% | 157 (20.4 km) |
| Further segments that may close (stream reaches the road crest) | 733 (98.6 km) |
| Culverts overtopped / surcharged | 80 / 0 of 536 |
| Road segments cut off from hospitals | 0 |
| Worst added trip time to a hospital | 0.0 min |
| Heaviest hour of rain | 60.0 mm |
| Flood model run time | 1482 s |


## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 1.00 | Route 28 | Somerville | 0.82 m of water at peak; over 30 cm for 10.0 h; 30 cm reached 8.5 h into the storm; worst hour 44 mm (60% of the storm); water beside the road 0.39 m below its crest (design freeboard 0.30 m; P 0.28); runoff beside / along the road at 1.1 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.47); road sag 2.4 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 43 mm; catchment 72.9 ha) (P 1.00) |
| 2 | 1.00 | Route 99 | Boston | 1.30 m of water at peak; over 30 cm for 9.0 h; 30 cm reached 9.5 h into the storm; worst hour 33 mm (54% of the storm); water beside the road 0.45 m below its crest (design freeboard 0.30 m; P 0.15); runoff beside / along the road at 1.8 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.74); road sag 4.1 m deep (underpass, drains sized for the 50-yr hour, 58 mm; peak hour here 29 mm; catchment 13.2 ha) (P 1.00) |
| 3 | 1.00 | Route 28 | Somerville | 0.65 m of water at peak; over 30 cm for 6.0 h; 30 cm reached 8.5 h into the storm; worst hour 42 mm (59% of the storm); water beside the road 0.11 m above its crest (design freeboard 0.30 m; P 1.00); road sag 1.8 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 42 mm; catchment 72.9 ha) (P 1.00) |
| 4 | 1.00 | Highland Avenue | Winchester | 3.44 m of water at peak; over 30 cm for 10.5 h; 30 cm reached 8.0 h into the storm; worst hour 23 mm (42% of the storm); a culvert within 100 m is overtopped |
| 5 | 1.00 | Howley Street | Peabody | 0.93 m of water at peak; over 30 cm for 10.0 h; 30 cm reached 8.5 h into the storm; worst hour 40 mm (50% of the storm) |
| 6 | 1.00 | Brookline Street | Lynn | 0.81 m of water at peak; over 30 cm for 10.0 h; 30 cm reached 8.5 h into the storm; worst hour 33 mm (49% of the storm); water beside the road 0.71 m above its crest (design freeboard 0.30 m; P 1.00); road sag 2.0 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 33 mm; catchment 32.8 ha) (P 1.00) |
| 7 | 1.00 | Rutherford Avenue | Boston | 1.30 m of water at peak; over 30 cm for 9.0 h; 30 cm reached 9.5 h into the storm; worst hour 28 mm (50% of the storm); water beside the road 0.45 m below its crest (design freeboard 0.30 m; P 0.15); runoff beside / along the road at 1.4 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.74); road sag 4.3 m deep (underpass, drains sized for the 50-yr hour, 58 mm; peak hour here 28 mm; catchment 13.2 ha) (P 1.00) |
| 8 | 1.00 | Suffolk Street | Malden | 0.64 m of water at peak; over 30 cm for 7.0 h; 30 cm reached 8.5 h into the storm; worst hour 58 mm (65% of the storm); water beside the road 0.42 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.5 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 58 mm; catchment 84.6 ha) (P 1.00) |
| 9 | 1.00 | Pennybrook Gardens | Saugus | 0.73 m of water at peak; over 30 cm for 5.5 h; 30 cm reached 8.5 h into the storm; worst hour 47 mm (60% of the storm); a culvert within 100 m is overtopped |
| 10 | 1.00 | Main Street | Peabody | 0.72 m of water at peak; over 30 cm for 4.5 h; 30 cm reached 9.0 h into the storm; worst hour 40 mm (50% of the storm); runoff beside / along the road at 0.9 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.44); a culvert within 100 m is overtopped |
| 11 | 1.00 | Eagen Place | Peabody | 0.72 m of water at peak; over 30 cm for 4.5 h; 30 cm reached 9.0 h into the storm; worst hour 40 mm (50% of the storm); runoff beside / along the road at 1.6 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.78); a culvert within 100 m is overtopped |
| 12 | 1.00 | Linden Avenue | Peabody | 0.72 m of water at peak; over 30 cm for 4.5 h; 30 cm reached 9.0 h into the storm; worst hour 40 mm (50% of the storm); runoff beside / along the road at 1.6 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.78); a culvert within 100 m is overtopped |
| 13 | 1.00 | Main Street | Peabody | 0.72 m of water at peak; over 30 cm for 4.5 h; 30 cm reached 9.0 h into the storm; worst hour 40 mm (50% of the storm); runoff beside / along the road at 0.9 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.44); a culvert within 100 m is overtopped |
| 14 | 1.00 | Pleasant Street | Peabody | 0.65 m of water at peak; over 30 cm for 4.5 h; 30 cm reached 8.5 h into the storm; worst hour 40 mm (49% of the storm); a culvert within 100 m is overtopped |
| 15 | 1.00 | Clement Avenue | Peabody | 0.65 m of water at peak; over 30 cm for 4.0 h; 30 cm reached 8.5 h into the storm; worst hour 39 mm (48% of the storm); a culvert within 100 m is overtopped |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
