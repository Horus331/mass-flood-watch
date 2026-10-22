# Road-closure prototype: sep2023_exp_rc_d4

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on CPU (OpenMP)), 20 m grid, storm from 2023-09-11T16:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 5,096 |
| Expected closures (sum of probabilities) | 190.0 |
| Segments with closure probability >= 50% | 161 (110.0 km) |
| Further segments that may close (stream reaches the road crest) | 223 (142.0 km) |
| Culverts overtopped / surcharged | 159 / 7 of 713 |
| Road segments cut off from hospitals | 853 |
| Worst added trip time to a hospital | 26.6 min |
| Heaviest hour of rain | 89.3 mm |
| Flood model run time | 1793 s |

## Checks against what happened

- Storm-day flood reports in the area: 10; water >= 10 cm within 100 m of 100% of them, vs 75% of random points (any day).
- Segments flagged impassable are 2.94x as likely as an average segment to have a report within 200 m.
- MassDOT repeating flood sites in the area: 4; 2 have a segment within 150 m at P >= 0.5 (share of all segments at P >= 0.5: 3.2%).

## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 1.00 | I-190 | Lancaster | 4.07 m of water at peak; over 30 cm for 48.0 h; 30 cm reached 0.5 h into the storm; worst hour 47 mm (38% of the storm); a culvert within 100 m is overtopped |
| 2 | 1.00 | Route 2 | Leominster | 9.75 m of water at peak; over 30 cm for 43.0 h; 30 cm reached 5.5 h into the storm; worst hour 67 mm (40% of the storm); a culvert within 100 m is overtopped |
| 3 | 1.00 | I-190 | Leominster | 15.37 m of water at peak; over 30 cm for 38.5 h; 30 cm reached 5.5 h into the storm; worst hour 71 mm (41% of the storm); a culvert within 100 m is overtopped |
| 4 | 1.00 | I-190 | Leominster | 2.08 m of water at peak; over 30 cm for 39.0 h; 30 cm reached 7.0 h into the storm; worst hour 71 mm (41% of the storm); a culvert within 100 m is overtopped |
| 5 | 1.00 | (unnamed) | Leominster | 1.77 m of water at peak; over 30 cm for 24.5 h; 30 cm reached 5.5 h into the storm; worst hour 84 mm (43% of the storm); water beside the road 0.07 m above its crest (design freeboard 0.30 m; P 0.99); a culvert within 100 m is overtopped |
| 6 | 1.00 | I-190 | Lancaster | 0.74 m of water at peak; over 30 cm for 6.0 h; 30 cm reached 7.5 h into the storm; worst hour 31 mm (30% of the storm); a culvert within 100 m is overtopped |
| 7 | 1.00 | Depot Street | Fitchburg | 1.44 m of water at peak; over 30 cm for 25.5 h; 30 cm reached 0.5 h into the storm; worst hour 31 mm (29% of the storm); water beside the road 1.08 m above its crest (design freeboard 0.30 m; P 1.00); a culvert within 100 m is overtopped |
| 8 | 1.00 | Water Street | Leominster | 1.78 m of water at peak; over 30 cm for 24.5 h; 30 cm reached 5.5 h into the storm; worst hour 85 mm (43% of the storm); a culvert within 100 m is overtopped |
| 9 | 1.00 | Route 12 | Leominster | 1.06 m of water at peak; over 30 cm for 8.5 h; 30 cm reached 6.0 h into the storm; worst hour 78 mm (43% of the storm); water beside the road 0.54 m above its crest (design freeboard 0.30 m; P 1.00); a culvert within 100 m is overtopped |
| 10 | 1.00 | Litchfield Street | Leominster | 1.95 m of water at peak; over 30 cm for 13.0 h; 30 cm reached 6.0 h into the storm; worst hour 66 mm (41% of the storm); a culvert within 100 m is overtopped |
| 11 | 1.00 | Route 117 | Leominster | 1.23 m of water at peak; over 30 cm for 9.0 h; 30 cm reached 6.5 h into the storm; worst hour 61 mm (39% of the storm); water beside the road 0.10 m above its crest (design freeboard 0.30 m; P 1.00); a culvert within 100 m is overtopped |
| 12 | 1.00 | Route 12 | Leominster | 0.95 m of water at peak; over 30 cm for 6.0 h; 30 cm reached 6.0 h into the storm; worst hour 85 mm (43% of the storm); water beside the road 0.20 m above its crest (design freeboard 0.30 m; P 1.00); a culvert within 100 m is overtopped |
| 13 | 1.00 | Route 70 | Lancaster | 1.91 m of water at peak; over 30 cm for 10.0 h; 30 cm reached 8.5 h into the storm; worst hour 24 mm (34% of the storm); a culvert within 100 m is overtopped |
| 14 | 1.00 | Route 70 | Lancaster | 1.91 m of water at peak; over 30 cm for 10.0 h; 30 cm reached 8.5 h into the storm; worst hour 25 mm (35% of the storm); a culvert within 100 m is overtopped |
| 15 | 1.00 | Merriam Avenue | Leominster | 0.87 m of water at peak; over 30 cm for 5.0 h; 30 cm reached 5.5 h into the storm; worst hour 84 mm (44% of the storm); water beside the road 0.67 m above its crest (design freeboard 0.30 m; P 1.00) |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
