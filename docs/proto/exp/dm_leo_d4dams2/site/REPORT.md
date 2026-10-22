# Road-closure prototype: sep2023_exp_dm_leo_d4dams2

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on CPU (OpenMP)), 20 m grid, storm from 2023-09-11T16:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 5,096 |
| Expected closures (sum of probabilities) | 212.0 |
| Segments with closure probability >= 50% | 189 (122.7 km) |
| Further segments that may close (stream reaches the road crest) | 230 (142.9 km) |
| Culverts overtopped / surcharged | 163 / 13 of 713 |
| Road segments cut off from hospitals | 881 |
| Worst added trip time to a hospital | 27.0 min |
| Heaviest hour of rain | 89.3 mm |
| Flood model run time | 3251 s |

## Checks against what happened

- Storm-day flood reports in the area: 10; water >= 10 cm within 100 m of 100% of them, vs 78% of random points (any day).
- Segments flagged impassable are 3.26x as likely as an average segment to have a report within 200 m.
- MassDOT repeating flood sites in the area: 4; 2 have a segment within 150 m at P >= 0.5 (share of all segments at P >= 0.5: 3.7%).

## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 1.00 | Route 2 | Leominster | 11.15 m of water at peak; over 30 cm for 43.0 h; 30 cm reached 5.5 h into the storm; worst hour 67 mm (40% of the storm); a culvert within 100 m is overtopped |
| 2 | 1.00 | (unnamed) | Leominster | 1.69 m of water at peak; over 30 cm for 30.0 h; 30 cm reached 5.5 h into the storm; worst hour 84 mm (43% of the storm); water beside the road 0.07 m above its crest (design freeboard 0.30 m; P 0.99); a culvert within 100 m is overtopped |
| 3 | 1.00 | Depot Street | Fitchburg | 2.99 m of water at peak; over 30 cm for 48.0 h; 30 cm reached 0.5 h into the storm; worst hour 31 mm (29% of the storm); water beside the road 1.09 m above its crest (design freeboard 0.30 m; P 1.00); a culvert within 100 m is overtopped |
| 4 | 1.00 | Route 70 | Lancaster | 1.77 m of water at peak; over 30 cm for 36.0 h; 30 cm reached 12.5 h into the storm; worst hour 24 mm (34% of the storm); a culvert within 100 m is overtopped |
| 5 | 1.00 | Route 70 | Lancaster | 1.77 m of water at peak; over 30 cm for 36.0 h; 30 cm reached 12.5 h into the storm; worst hour 25 mm (35% of the storm); a culvert within 100 m is overtopped |
| 6 | 1.00 | Route 12 | Leominster | 1.00 m of water at peak; over 30 cm for 19.0 h; 30 cm reached 6.0 h into the storm; worst hour 78 mm (43% of the storm); water beside the road 0.54 m above its crest (design freeboard 0.30 m; P 1.00); a culvert within 100 m is overtopped |
| 7 | 1.00 | Litchfield Street | Leominster | 2.40 m of water at peak; over 30 cm for 30.5 h; 30 cm reached 6.0 h into the storm; worst hour 66 mm (41% of the storm); a culvert within 100 m is overtopped |
| 8 | 1.00 | Route 117 | Leominster | 1.20 m of water at peak; over 30 cm for 18.5 h; 30 cm reached 6.5 h into the storm; worst hour 61 mm (39% of the storm); a culvert within 100 m is overtopped |
| 9 | 1.00 | Route 2 | Leominster | 0.72 m of water at peak; over 30 cm for 2.5 h; 30 cm reached 6.0 h into the storm; worst hour 79 mm (45% of the storm); water beside the road 0.64 m above its crest (design freeboard 0.30 m; P 1.00); road sag 3.4 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 74 mm; catchment 39.6 ha) (P 1.00) |
| 10 | 1.00 | Water Street | Leominster | 1.71 m of water at peak; over 30 cm for 30.0 h; 30 cm reached 5.5 h into the storm; worst hour 85 mm (43% of the storm); a culvert within 100 m is overtopped |
| 11 | 1.00 | Route 12 | Leominster | 0.98 m of water at peak; over 30 cm for 9.0 h; 30 cm reached 6.0 h into the storm; worst hour 85 mm (43% of the storm); water beside the road 0.30 m above its crest (design freeboard 0.30 m; P 1.00); a culvert within 100 m is overtopped |
| 12 | 1.00 | John Fitch Highway | Fitchburg | 1.12 m of water at peak; over 30 cm for 11.0 h; 30 cm reached 1.5 h into the storm; worst hour 26 mm (28% of the storm); water beside the road 0.45 m below its crest (design freeboard 0.30 m; P 0.15) |
| 13 | 1.00 | Merriam Avenue | Leominster | 1.12 m of water at peak; over 30 cm for 8.5 h; 30 cm reached 5.5 h into the storm; worst hour 84 mm (44% of the storm); water beside the road 0.93 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.4 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 81 mm; catchment 13.0 ha) (P 1.00) |
| 14 | 1.00 | Route 110 | Lancaster | 0.84 m of water at peak; over 30 cm for 27.5 h; 30 cm reached 21.0 h into the storm; worst hour 9 mm (30% of the storm); a culvert within 100 m is overtopped |
| 15 | 1.00 | Main Street | Fitchburg | 1.92 m of water at peak; over 30 cm for 25.5 h; 30 cm reached 6.5 h into the storm; worst hour 27 mm (29% of the storm); a culvert within 100 m is overtopped |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
