# Road-closure prototype: sep2023_proto_leominster_sep2023_10m

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on GPU (cuda)), 10 m grid, storm from 2023-09-11T16:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 5,120 |
| Expected closures (sum of probabilities) | 571.6 |
| Segments with closure probability >= 50% | 552 (270.7 km) |
| Further segments that may close (stream reaches the road crest) | 675 (360.4 km) |
| Culverts overtopped / surcharged | 284 / 63 of 713 |
| Road segments cut off from hospitals | 928 |
| Worst added trip time to a hospital | 36.8 min |
| Heaviest hour of rain | 89.3 mm |
| Flood model run time | 678 s |

## Checks against what happened

- Storm-day flood reports in the area: 10; water >= 10 cm within 100 m of 100% of them, vs 82% of random points (any day).
- Segments flagged impassable are 2.61x as likely as an average segment to have a report within 200 m.
- MassDOT repeating flood sites in the area: 4; 2 have a segment within 150 m at P >= 0.5 (share of all segments at P >= 0.5: 10.8%).

## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 1.00 | Route 2 | Leominster | 10.98 m of water at peak; over 30 cm for 48.0 h; 30 cm reached 0.5 h into the storm; worst hour 67 mm (40% of the storm); water beside the road 1.04 m above its crest (design freeboard 0.30 m; P 1.00); a culvert within 100 m is overtopped |
| 2 | 1.00 | Route 2 | Lancaster | 3.51 m of water at peak; over 30 cm for 41.0 h; 30 cm reached 7.5 h into the storm; worst hour 42 mm (48% of the storm); water beside the road 0.33 m below its crest (design freeboard 0.30 m; P 0.42); a culvert within 100 m is overtopped |
| 3 | 1.00 | I-190 | Sterling | 1.64 m of water at peak; over 30 cm for 48.0 h; 30 cm reached 0.5 h into the storm; worst hour 19 mm (26% of the storm); water beside the road 6.03 m above its crest (design freeboard 0.30 m; P 1.00); a culvert within 100 m is overtopped |
| 4 | 1.00 | I-190 | Lancaster | 2.24 m of water at peak; over 30 cm for 48.5 h; 30 cm reached 0.0 h into the storm; worst hour 28 mm (29% of the storm); water beside the road 8.59 m above its crest (design freeboard 0.30 m; P 1.00); a culvert within 100 m is overtopped |
| 5 | 1.00 | Route 2 | Fitchburg | 5.36 m of water at peak; over 30 cm for 33.0 h; 30 cm reached 0.0 h into the storm; worst hour 46 mm (45% of the storm); water beside the road 9.92 m above its crest (design freeboard 0.30 m; P 1.00); a culvert within 100 m is overtopped |
| 6 | 1.00 | Route 2 | Fitchburg | 10.72 m of water at peak; over 30 cm for 21.0 h; 30 cm reached 0.0 h into the storm; worst hour 38 mm (30% of the storm); water beside the road 6.09 m above its crest (design freeboard 0.30 m; P 1.00); a culvert within 100 m is overtopped |
| 7 | 1.00 | Route 12 | Leominster | 3.33 m of water at peak; over 30 cm for 48.0 h; 30 cm reached 0.5 h into the storm; worst hour 78 mm (43% of the storm); water beside the road 1.67 m above its crest (design freeboard 0.30 m; P 1.00); road sag 1.4 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 72 mm; catchment 115.6 ha) (P 1.00); a culvert within 100 m is overtopped |
| 8 | 1.00 | Route 12 | Sterling | 2.60 m of water at peak; over 30 cm for 48.0 h; 30 cm reached 0.0 h into the storm; worst hour 16 mm (25% of the storm); water beside the road 0.80 m above its crest (design freeboard 0.30 m; P 1.00); a culvert within 100 m is overtopped |
| 9 | 1.00 | Route 12 | Sterling | 2.60 m of water at peak; over 30 cm for 48.0 h; 30 cm reached 0.0 h into the storm; worst hour 16 mm (25% of the storm); water beside the road 0.71 m above its crest (design freeboard 0.30 m; P 1.00); a culvert within 100 m is overtopped |
| 10 | 1.00 | (unnamed) | Sterling | 2.46 m of water at peak; over 30 cm for 48.0 h; 30 cm reached 0.0 h into the storm; worst hour 16 mm (25% of the storm); water beside the road 0.80 m above its crest (design freeboard 0.30 m; P 1.00); a culvert within 100 m is overtopped |
| 11 | 1.00 | Route 12 | Sterling | 0.83 m of water at peak; over 30 cm for 48.0 h; 30 cm reached 0.5 h into the storm; worst hour 15 mm (24% of the storm); water beside the road 2.31 m above its crest (design freeboard 0.30 m; P 1.00); a culvert within 100 m is overtopped |
| 12 | 1.00 | (unnamed) | Leominster | 5.34 m of water at peak; over 30 cm for 19.5 h; 30 cm reached 0.5 h into the storm; worst hour 84 mm (43% of the storm); water beside the road 5.93 m above its crest (design freeboard 0.30 m; P 1.00); a culvert within 100 m is overtopped |
| 13 | 1.00 | Litchfield Street | Leominster | 3.46 m of water at peak; over 30 cm for 42.0 h; 30 cm reached 6.5 h into the storm; worst hour 66 mm (41% of the storm); water beside the road 6.96 m above its crest (design freeboard 0.30 m; P 1.00); road sag 4.3 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 66 mm; catchment 115.6 ha) (P 1.00); a culvert within 100 m is overtopped |
| 14 | 1.00 | Route 2 | Leominster | 1.03 m of water at peak; over 30 cm for 6.0 h; 30 cm reached 6.0 h into the storm; worst hour 74 mm (46% of the storm); water beside the road 1.04 m above its crest (design freeboard 0.30 m; P 1.00); road sag 3.5 m deep (underpass, drains sized for the 50-yr hour, 58 mm; peak hour here 74 mm; catchment 31.8 ha) (P 1.00) |
| 15 | 1.00 | Route 2 | Leominster | 0.90 m of water at peak; over 30 cm for 5.0 h; 30 cm reached 6.0 h into the storm; worst hour 79 mm (45% of the storm); water beside the road 1.52 m above its crest (design freeboard 0.30 m; P 1.00); road sag 3.5 m deep (underpass, drains sized for the 50-yr hour, 58 mm; peak hour here 74 mm; catchment 31.8 ha) (P 1.00) |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
