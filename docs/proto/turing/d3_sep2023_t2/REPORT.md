# Road-closure prototype: sep2023_proto_d3_sep2023_t2

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on GPU (cuda)), 20 m grid, storm from 2023-09-11T16:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 45,099 |
| Expected closures (sum of probabilities) | 265.4 |
| Segments with closure probability >= 50% | 134 (94.5 km) |
| Further segments that may close (stream reaches the road crest) | 265 (179.9 km) |
| Culverts overtopped / surcharged | 307 / 12 of 10736 |
| Road segments cut off from hospitals | 1226 |
| Worst added trip time to a hospital | 30.6 min |
| Heaviest hour of rain | 102.0 mm |
| Flood model run time | 575 s |

## Checks against what happened

- Storm-day flood reports in the area: 11; water >= 10 cm within 100 m of 82% of them, vs 15% of random points (any day).
- Segments flagged impassable are 13.65x as likely as an average segment to have a report within 200 m.
- MassDOT repeating flood sites in the area: 30; 3 have a segment within 150 m at P >= 0.5 (share of all segments at P >= 0.5: 0.3%).

## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 1.00 | Route 2 | Harvard | 0.75 m of water at peak; over 30 cm for 27.5 h; 30 cm reached 21.0 h into the storm; worst hour 29 mm (41% of the storm); a culvert within 100 m is overtopped |
| 2 | 1.00 | Route 2 | Harvard | 0.75 m of water at peak; over 30 cm for 27.5 h; 30 cm reached 21.0 h into the storm; worst hour 33 mm (43% of the storm); a culvert within 100 m is overtopped |
| 3 | 1.00 | Route 117 | Lancaster | 1.69 m of water at peak; over 30 cm for 48.0 h; 30 cm reached 0.5 h into the storm; worst hour 23 mm (43% of the storm); water beside the road 0.49 m below its crest (design freeboard 0.30 m; P 0.10) |
| 4 | 1.00 | (unnamed) | Leominster | 1.30 m of water at peak; over 30 cm for 21.0 h; 30 cm reached 6.0 h into the storm; worst hour 84 mm (43% of the storm); water beside the road 0.04 m above its crest (design freeboard 0.30 m; P 0.99); a culvert within 100 m is overtopped |
| 5 | 1.00 | Depot Street | Fitchburg | 0.90 m of water at peak; over 30 cm for 46.0 h; 30 cm reached 0.5 h into the storm; worst hour 31 mm (29% of the storm); a culvert within 100 m is overtopped |
| 6 | 1.00 | Route 12 | Leominster | 0.93 m of water at peak; over 30 cm for 9.0 h; 30 cm reached 6.0 h into the storm; worst hour 77 mm (43% of the storm); water beside the road 0.04 m above its crest (design freeboard 0.30 m; P 0.99); a culvert within 100 m is overtopped |
| 7 | 1.00 | Water Street | Leominster | 1.30 m of water at peak; over 30 cm for 21.0 h; 30 cm reached 6.0 h into the storm; worst hour 84 mm (43% of the storm); a culvert within 100 m is overtopped |
| 8 | 1.00 | Litchfield Street | Leominster | 1.49 m of water at peak; over 30 cm for 13.0 h; 30 cm reached 6.0 h into the storm; worst hour 65 mm (41% of the storm); a culvert within 100 m is overtopped |
| 9 | 1.00 | Route 117 | Leominster | 0.99 m of water at peak; over 30 cm for 9.0 h; 30 cm reached 6.5 h into the storm; worst hour 58 mm (38% of the storm); cut off from hospitals |
| 10 | 1.00 | Route 117 | Leominster | 0.99 m of water at peak; over 30 cm for 9.0 h; 30 cm reached 6.5 h into the storm; worst hour 60 mm (39% of the storm); water beside the road 0.10 m below its crest (design freeboard 0.30 m; P 0.91); a culvert within 100 m is overtopped |
| 11 | 1.00 | Route 70 | Lancaster | 1.47 m of water at peak; over 30 cm for 9.5 h; 30 cm reached 9.0 h into the storm; worst hour 24 mm (34% of the storm); a culvert within 100 m is overtopped |
| 12 | 1.00 | Route 70 | Lancaster | 1.47 m of water at peak; over 30 cm for 9.5 h; 30 cm reached 9.0 h into the storm; worst hour 25 mm (35% of the storm); a culvert within 100 m is overtopped |
| 13 | 1.00 | Shirley Street | Pepperell | 0.69 m of water at peak; over 30 cm for 34.0 h; 30 cm reached 9.5 h into the storm; worst hour 37 mm (32% of the storm) |
| 14 | 1.00 | Merriam Avenue | Leominster | 0.73 m of water at peak; over 30 cm for 4.5 h; 30 cm reached 5.5 h into the storm; worst hour 84 mm (44% of the storm); water beside the road 0.54 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.4 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 82 mm; catchment 13.0 ha) (P 1.00) |
| 15 | 1.00 | James Brook Way | Ayer | 1.18 m of water at peak; over 30 cm for 42.5 h; 30 cm reached 6.0 h into the storm; worst hour 63 mm (43% of the storm); a culvert within 100 m is overtopped |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
