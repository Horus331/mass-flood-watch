# Road-closure prototype: sep2023_exp_bd_square_t07

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on CPU (OpenMP)), 20 m grid, storm from 2023-09-11T16:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 5,096 |
| Expected closures (sum of probabilities) | 165.9 |
| Segments with closure probability >= 50% | 140 (96.5 km) |
| Further segments that may close (stream reaches the road crest) | 152 (91.1 km) |
| Culverts overtopped / surcharged | 141 / 10 of 713 |
| Road segments cut off from hospitals | 715 |
| Worst added trip time to a hospital | 23.9 min |
| Heaviest hour of rain | 89.3 mm |
| Flood model run time | 2700 s |

## Checks against what happened

- Storm-day flood reports in the area: 10; water >= 10 cm within 100 m of 100% of them, vs 74% of random points (any day).
- Segments flagged impassable are 3.44x as likely as an average segment to have a report within 200 m.
- MassDOT repeating flood sites in the area: 4; 2 have a segment within 150 m at P >= 0.5 (share of all segments at P >= 0.5: 2.7%).

## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 1.00 | Route 2 | Leominster | 8.88 m of water at peak; over 30 cm for 42.5 h; 30 cm reached 6.0 h into the storm; worst hour 67 mm (40% of the storm); a culvert within 100 m is overtopped |
| 2 | 1.00 | (unnamed) | Leominster | 1.54 m of water at peak; over 30 cm for 37.5 h; 30 cm reached 6.0 h into the storm; worst hour 84 mm (43% of the storm); water beside the road 0.04 m above its crest (design freeboard 0.30 m; P 0.99); a culvert within 100 m is overtopped |
| 3 | 1.00 | Route 70 | Lancaster | 1.62 m of water at peak; over 30 cm for 35.0 h; 30 cm reached 13.5 h into the storm; worst hour 24 mm (34% of the storm); a culvert within 100 m is overtopped |
| 4 | 1.00 | Route 70 | Lancaster | 1.62 m of water at peak; over 30 cm for 35.0 h; 30 cm reached 13.5 h into the storm; worst hour 25 mm (35% of the storm); a culvert within 100 m is overtopped |
| 5 | 1.00 | Depot Street | Fitchburg | 2.11 m of water at peak; over 30 cm for 42.5 h; 30 cm reached 0.5 h into the storm; worst hour 31 mm (29% of the storm); a culvert within 100 m is overtopped |
| 6 | 1.00 | Water Street | Leominster | 1.56 m of water at peak; over 30 cm for 37.5 h; 30 cm reached 6.0 h into the storm; worst hour 85 mm (43% of the storm); a culvert within 100 m is overtopped |
| 7 | 1.00 | Litchfield Street | Leominster | 2.46 m of water at peak; over 30 cm for 23.5 h; 30 cm reached 6.0 h into the storm; worst hour 66 mm (41% of the storm); a culvert within 100 m is overtopped |
| 8 | 1.00 | Route 12 | Leominster | 1.12 m of water at peak; over 30 cm for 13.5 h; 30 cm reached 6.0 h into the storm; worst hour 78 mm (43% of the storm); water beside the road 0.58 m above its crest (design freeboard 0.30 m; P 1.00); a culvert within 100 m is overtopped |
| 9 | 1.00 | Route 117 | Leominster | 1.16 m of water at peak; over 30 cm for 14.0 h; 30 cm reached 6.5 h into the storm; worst hour 61 mm (39% of the storm); water beside the road 0.10 m below its crest (design freeboard 0.30 m; P 0.91); a culvert within 100 m is overtopped |
| 10 | 1.00 | Route 12 | Leominster | 0.87 m of water at peak; over 30 cm for 9.0 h; 30 cm reached 6.0 h into the storm; worst hour 85 mm (43% of the storm); water beside the road 0.17 m above its crest (design freeboard 0.30 m; P 1.00); a culvert within 100 m is overtopped |
| 11 | 1.00 | Merriam Avenue | Leominster | 0.99 m of water at peak; over 30 cm for 8.0 h; 30 cm reached 5.5 h into the storm; worst hour 84 mm (44% of the storm); water beside the road 0.79 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.4 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 81 mm; catchment 13.0 ha) (P 1.00) |
| 12 | 1.00 | John Fitch Highway | Fitchburg | 0.92 m of water at peak; over 30 cm for 8.5 h; 30 cm reached 7.5 h into the storm; worst hour 26 mm (28% of the storm) |
| 13 | 1.00 | Route 110 | Lancaster | 0.71 m of water at peak; over 30 cm for 25.5 h; 30 cm reached 23.0 h into the storm; worst hour 9 mm (30% of the storm); a culvert within 100 m is overtopped |
| 14 | 1.00 | Kingman Drive | Leominster | 1.45 m of water at peak; over 30 cm for 30.5 h; 30 cm reached 5.5 h into the storm; worst hour 85 mm (44% of the storm); water beside the road 0.48 m above its crest (design freeboard 0.30 m; P 1.00); a culvert within 100 m is overtopped |
| 15 | 1.00 | Route 140 | Princeton | 1.10 m of water at peak; over 30 cm for 11.5 h; 30 cm reached 7.5 h into the storm; worst hour 42 mm (28% of the storm); water beside the road 0.20 m above its crest (design freeboard 0.30 m; P 1.00); a culvert within 100 m is overtopped |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
