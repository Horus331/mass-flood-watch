# Road-closure prototype: sep2023_exp_dm_leo_d4dams

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on CPU (OpenMP)), 20 m grid, storm from 2023-09-11T16:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 5,096 |
| Expected closures (sum of probabilities) | 209.2 |
| Segments with closure probability >= 50% | 177 (115.5 km) |
| Further segments that may close (stream reaches the road crest) | 229 (144.0 km) |
| Culverts overtopped / surcharged | 155 / 9 of 713 |
| Road segments cut off from hospitals | 832 |
| Worst added trip time to a hospital | 27.0 min |
| Heaviest hour of rain | 89.3 mm |
| Flood model run time | 1998 s |

## Checks against what happened

- Storm-day flood reports in the area: 10; water >= 10 cm within 100 m of 100% of them, vs 75% of random points (any day).
- Segments flagged impassable are 3.16x as likely as an average segment to have a report within 200 m.
- MassDOT repeating flood sites in the area: 4; 2 have a segment within 150 m at P >= 0.5 (share of all segments at P >= 0.5: 3.5%).

## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 1.00 | Route 2 | Leominster | 17.32 m of water at peak; over 30 cm for 41.0 h; 30 cm reached 5.5 h into the storm; worst hour 67 mm (40% of the storm); a culvert within 100 m is overtopped |
| 2 | 1.00 | Route 12 | Leominster | 2.29 m of water at peak; over 30 cm for 42.5 h; 30 cm reached 6.0 h into the storm; worst hour 78 mm (43% of the storm); water beside the road 1.09 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.8 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 73 mm; catchment 85.6 ha) (P 1.00); a culvert within 100 m is overtopped |
| 3 | 1.00 | Route 2 | Fitchburg | 1.70 m of water at peak; over 30 cm for 11.5 h; 30 cm reached 6.0 h into the storm; worst hour 50 mm (46% of the storm); water beside the road 1.24 m above its crest (design freeboard 0.30 m; P 1.00); a culvert within 100 m is overtopped |
| 4 | 1.00 | Route 117 | Leominster | 2.05 m of water at peak; over 30 cm for 42.0 h; 30 cm reached 6.5 h into the storm; worst hour 61 mm (39% of the storm); water beside the road 0.67 m above its crest (design freeboard 0.30 m; P 1.00); a culvert within 100 m is overtopped |
| 5 | 1.00 | Route 70 | Lancaster | 1.94 m of water at peak; over 30 cm for 40.0 h; 30 cm reached 8.5 h into the storm; worst hour 24 mm (34% of the storm); a culvert within 100 m is overtopped |
| 6 | 1.00 | Route 70 | Lancaster | 1.94 m of water at peak; over 30 cm for 40.0 h; 30 cm reached 8.5 h into the storm; worst hour 25 mm (35% of the storm); a culvert within 100 m is overtopped |
| 7 | 1.00 | (unnamed) | Leominster | 1.78 m of water at peak; over 30 cm for 19.5 h; 30 cm reached 6.0 h into the storm; worst hour 84 mm (43% of the storm); water beside the road 0.07 m above its crest (design freeboard 0.30 m; P 0.99); a culvert within 100 m is overtopped |
| 8 | 1.00 | Litchfield Street | Leominster | 3.47 m of water at peak; over 30 cm for 42.5 h; 30 cm reached 6.0 h into the storm; worst hour 66 mm (41% of the storm); water beside the road 0.19 m above its crest (design freeboard 0.30 m; P 1.00); a culvert within 100 m is overtopped |
| 9 | 1.00 | Route 2 | Fitchburg | 3.20 m of water at peak; over 30 cm for 6.0 h; 30 cm reached 10.5 h into the storm; worst hour 46 mm (45% of the storm); water beside the road 3.55 m above its crest (design freeboard 0.30 m; P 1.00); a culvert within 100 m is overtopped |
| 10 | 1.00 | Depot Street | Fitchburg | 1.54 m of water at peak; over 30 cm for 26.5 h; 30 cm reached 0.5 h into the storm; worst hour 31 mm (29% of the storm); water beside the road 1.08 m above its crest (design freeboard 0.30 m; P 1.00); a culvert within 100 m is overtopped |
| 11 | 1.00 | Route 110 | Lancaster | 1.24 m of water at peak; over 30 cm for 37.0 h; 30 cm reached 11.5 h into the storm; worst hour 9 mm (30% of the storm); a culvert within 100 m is overtopped |
| 12 | 1.00 | Litchfield Street | Leominster | 3.50 m of water at peak; over 30 cm for 43.0 h; 30 cm reached 5.5 h into the storm; worst hour 74 mm (42% of the storm); water beside the road 0.25 m below its crest (design freeboard 0.30 m; P 0.64) |
| 13 | 1.00 | Water Street | Leominster | 1.78 m of water at peak; over 30 cm for 19.5 h; 30 cm reached 6.0 h into the storm; worst hour 85 mm (43% of the storm); a culvert within 100 m is overtopped |
| 14 | 1.00 | Route 12 | Leominster | 0.93 m of water at peak; over 30 cm for 6.0 h; 30 cm reached 6.0 h into the storm; worst hour 85 mm (43% of the storm); water beside the road 0.19 m above its crest (design freeboard 0.30 m; P 1.00); a culvert within 100 m is overtopped |
| 15 | 1.00 | Merriam Avenue | Leominster | 0.87 m of water at peak; over 30 cm for 5.0 h; 30 cm reached 5.5 h into the storm; worst hour 84 mm (44% of the storm); water beside the road 0.67 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.4 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 81 mm; catchment 13.0 ha) (P 1.00) |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
