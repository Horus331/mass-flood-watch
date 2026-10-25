# Road-closure prototype: apr2018e_transfer_apr2018e_farmhill_20m

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on CPU (OpenMP)), 20 m grid, storm from 2018-04-16T12:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 24,857 |
| Expected closures (sum of probabilities) | 42.7 |
| Segments with closure probability >= 50% | 2 (0.1 km) |
| Further segments that may close (stream reaches the road crest) | 5 (1.4 km) |
| Culverts overtopped / surcharged | 14 / 1 of 687 |
| Road segments cut off from hospitals | 0 |
| Worst added trip time to a hospital | 0.0 min |
| Heaviest hour of rain | 10.1 mm |
| Flood model run time | 1056 s |


## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 1.00 | Mill Street | Arlington | 0.72 m of water at peak; over 30 cm for 10.5 h; 30 cm reached 8.0 h into the storm; worst hour 8 mm (16% of the storm); a culvert within 100 m is overtopped |
| 2 | 1.00 | Highland Avenue | Winchester | 1.15 m of water at peak; over 30 cm for 9.0 h; 30 cm reached 9.5 h into the storm; worst hour 8 mm (15% of the storm); a culvert within 100 m is overtopped |
| 3 | 0.49 | Ramp-US 3 | Burlington | 0.30 m of water at peak; worst hour 8 mm (16% of the storm); a culvert within 100 m is overtopped |
| 4 | 0.49 | Ramp | Burlington | 0.30 m of water at peak; worst hour 8 mm (16% of the storm); a culvert within 100 m is overtopped |
| 5 | 0.42 | Anna Road | Woburn | 0.28 m of water at peak; worst hour 8 mm (15% of the storm); a culvert within 100 m is overtopped |
| 6 | 0.18 | Lexington Street | Woburn | 0.21 m of water at peak; worst hour 8 mm (16% of the storm); a culvert within 100 m is overtopped |
| 7 | 0.18 | Mill Street | Reading | 0.21 m of water at peak; worst hour 8 mm (16% of the storm); a culvert within 100 m is overtopped |
| 8 | 0.18 | Mill Street | Reading | 0.21 m of water at peak; worst hour 8 mm (16% of the storm) |
| 9 | 0.16 | I-93 | Medford | 0.20 m of water at peak; worst hour 9 mm (18% of the storm); water beside the road 0.20 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 0.7 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.24); road sag 1.6 m deep (underpass, drains sized for the 50-yr hour, 58 mm; peak hour here 9 mm; catchment 25.1 ha) (P 0.38) |
| 10 | 0.11 | Shawsheen Road | Bedford | 0.18 m of water at peak; worst hour 9 mm (17% of the storm); a culvert within 100 m is overtopped |
| 11 | 0.11 | Page Road | Bedford | 0.18 m of water at peak; worst hour 9 mm (17% of the storm) |
| 12 | 0.11 | Page Road | Bedford | 0.18 m of water at peak; worst hour 9 mm (17% of the storm) |
| 13 | 0.09 | Sylvester Avenue | Winchester | 0.16 m of water at peak; worst hour 8 mm (16% of the storm); a culvert within 100 m is overtopped |
| 14 | 0.08 | Sylvester Avenue | Winchester | 0.16 m of water at peak; worst hour 8 mm (16% of the storm); a culvert within 100 m is overtopped |
| 15 | 0.08 | Ramp | Burlington | 0.16 m of water at peak; worst hour 8 mm (15% of the storm); a culvert within 100 m is overtopped |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
