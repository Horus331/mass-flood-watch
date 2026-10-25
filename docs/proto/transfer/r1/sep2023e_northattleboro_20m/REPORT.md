# Road-closure prototype: sep2023e_transfer_sep2023e_northattleboro_20m

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on CPU (OpenMP)), 20 m grid, storm from 2023-09-09T12:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 9,433 |
| Expected closures (sum of probabilities) | 32.8 |
| Segments with closure probability >= 50% | 11 (1.6 km) |
| Further segments that may close (stream reaches the road crest) | 10 (4.0 km) |
| Culverts overtopped / surcharged | 47 / 0 of 696 |
| Road segments cut off from hospitals | 0 |
| Worst added trip time to a hospital | 0.0 min |
| Heaviest hour of rain | 57.7 mm |
| Flood model run time | 1295 s |


## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 1.00 | Route 106 | Mansfield | 0.85 m of water at peak; over 30 cm for 17.5 h; 30 cm reached 1.0 h into the storm; worst hour 15 mm (58% of the storm); water beside the road 0.03 m below its crest (design freeboard 0.30 m; P 0.96); road sag 4.2 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 15 mm; catchment 8.5 ha) (P 1.00) |
| 2 | 1.00 | Route 106 | Mansfield | 0.58 m of water at peak; over 30 cm for 9.0 h; 30 cm reached 9.5 h into the storm; worst hour 15 mm (58% of the storm); water beside the road 0.21 m below its crest (design freeboard 0.30 m; P 0.72); road sag 4.2 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 15 mm; catchment 8.5 ha) (P 1.00) |
| 3 | 0.93 | Roy Avenue | Attleboro | 0.45 m of water at peak; over 30 cm for 7.0 h; 30 cm reached 11.5 h into the storm; worst hour 18 mm (69% of the storm); a culvert within 100 m is overtopped |
| 4 | 0.81 | Barrows Street | Norton | 0.39 m of water at peak; over 30 cm for 3.5 h; 30 cm reached 0.5 h into the storm; worst hour 1 mm (60% of the storm) |
| 5 | 0.81 | Barrows Street | Norton | 0.39 m of water at peak; over 30 cm for 3.5 h; 30 cm reached 0.5 h into the storm; worst hour 1 mm (61% of the storm); water beside the road 0.26 m below its crest (design freeboard 0.30 m; P 0.60) |
| 6 | 0.78 | Route 1 | North Attleborough | 0.38 m of water at peak; over 30 cm for 2.5 h; 30 cm reached 10.5 h into the storm; worst hour 43 mm (65% of the storm); a culvert within 100 m is overtopped |
| 7 | 0.76 | Riverview Drive | North Attleborough | 0.37 m of water at peak; over 30 cm for 2.0 h; 30 cm reached 10.5 h into the storm; worst hour 43 mm (63% of the storm); a culvert within 100 m is overtopped |
| 8 | 0.76 | Riverview Drive | North Attleborough | 0.37 m of water at peak; over 30 cm for 2.0 h; 30 cm reached 10.5 h into the storm; worst hour 43 mm (63% of the storm) |
| 9 | 0.76 | Route 1 | North Attleborough | 0.37 m of water at peak; over 30 cm for 2.5 h; 30 cm reached 10.5 h into the storm; worst hour 43 mm (64% of the storm); a culvert within 100 m is overtopped |
| 10 | 0.60 | Ramp | North Attleborough | 0.33 m of water at peak; over 30 cm for 1.0 h; 30 cm reached 11.0 h into the storm; worst hour 44 mm (67% of the storm); runoff beside / along the road at 1.6 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.38); a culvert within 100 m is overtopped |
| 11 | 0.57 | Read Street | Attleboro | 0.32 m of water at peak; over 30 cm for 2.0 h; 30 cm reached 14.0 h into the storm; worst hour 14 mm (61% of the storm); a culvert within 100 m is overtopped |
| 12 | 0.44 | Ramp | North Attleborough | 0.28 m of water at peak; worst hour 45 mm (69% of the storm); a culvert within 100 m is overtopped |
| 13 | 0.29 | High Street | North Attleborough | 0.24 m of water at peak; worst hour 34 mm (55% of the storm); a culvert within 100 m is overtopped |
| 14 | 0.29 | Route 140 | Norton | 0.24 m of water at peak; worst hour 1 mm (50% of the storm) |
| 15 | 0.29 | Route 140 | Norton | 0.24 m of water at peak; worst hour 1 mm (51% of the storm) |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
