# Road-closure prototype: sep2023_exp_rc_d4_ch05_lc

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on CPU (OpenMP)), 20 m grid, storm from 2023-09-11T16:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 5,096 |
| Expected closures (sum of probabilities) | 205.6 |
| Segments with closure probability >= 50% | 180 (124.0 km) |
| Further segments that may close (stream reaches the road crest) | 233 (148.9 km) |
| Culverts overtopped / surcharged | 164 / 8 of 713 |
| Road segments cut off from hospitals | 866 |
| Worst added trip time to a hospital | 27.5 min |
| Heaviest hour of rain | 89.3 mm |
| Flood model run time | 1963 s |

## Checks against what happened

- Storm-day flood reports in the area: 10; water >= 10 cm within 100 m of 100% of them, vs 79% of random points (any day).
- Segments flagged impassable are 2.99x as likely as an average segment to have a report within 200 m.
- MassDOT repeating flood sites in the area: 4; 2 have a segment within 150 m at P >= 0.5 (share of all segments at P >= 0.5: 3.5%).

## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 1.00 | I-190 | Lancaster | 4.19 m of water at peak; over 30 cm for 48.0 h; 30 cm reached 0.5 h into the storm; worst hour 47 mm (38% of the storm); a culvert within 100 m is overtopped |
| 2 | 1.00 | I-190 | Leominster | 15.63 m of water at peak; over 30 cm for 41.5 h; 30 cm reached 5.5 h into the storm; worst hour 71 mm (41% of the storm); a culvert within 100 m is overtopped |
| 3 | 1.00 | Route 2 | Leominster | 17.86 m of water at peak; over 30 cm for 32.0 h; 30 cm reached 5.5 h into the storm; worst hour 67 mm (40% of the storm); a culvert within 100 m is overtopped |
| 4 | 1.00 | (unnamed) | Leominster | 1.85 m of water at peak; over 30 cm for 28.5 h; 30 cm reached 5.5 h into the storm; worst hour 84 mm (43% of the storm); water beside the road 0.12 m above its crest (design freeboard 0.30 m; P 1.00); a culvert within 100 m is overtopped |
| 5 | 1.00 | I-190 | Lancaster | 0.84 m of water at peak; over 30 cm for 7.0 h; 30 cm reached 7.5 h into the storm; worst hour 31 mm (30% of the storm); a culvert within 100 m is overtopped |
| 6 | 1.00 | Depot Street | Fitchburg | 1.58 m of water at peak; over 30 cm for 32.5 h; 30 cm reached 0.5 h into the storm; worst hour 31 mm (29% of the storm); water beside the road 1.09 m above its crest (design freeboard 0.30 m; P 1.00); a culvert within 100 m is overtopped |
| 7 | 1.00 | Water Street | Leominster | 1.85 m of water at peak; over 30 cm for 29.0 h; 30 cm reached 5.5 h into the storm; worst hour 85 mm (43% of the storm); a culvert within 100 m is overtopped |
| 8 | 1.00 | Route 12 | Leominster | 1.11 m of water at peak; over 30 cm for 10.5 h; 30 cm reached 6.0 h into the storm; worst hour 78 mm (43% of the storm); water beside the road 0.56 m above its crest (design freeboard 0.30 m; P 1.00); a culvert within 100 m is overtopped |
| 9 | 1.00 | Litchfield Street | Leominster | 2.13 m of water at peak; over 30 cm for 16.5 h; 30 cm reached 6.0 h into the storm; worst hour 66 mm (41% of the storm); a culvert within 100 m is overtopped |
| 10 | 1.00 | Route 117 | Leominster | 1.30 m of water at peak; over 30 cm for 11.5 h; 30 cm reached 6.5 h into the storm; worst hour 61 mm (39% of the storm); water beside the road 0.11 m above its crest (design freeboard 0.30 m; P 1.00); a culvert within 100 m is overtopped |
| 11 | 1.00 | Route 70 | Lancaster | 1.97 m of water at peak; over 30 cm for 13.5 h; 30 cm reached 9.0 h into the storm; worst hour 24 mm (34% of the storm); a culvert within 100 m is overtopped |
| 12 | 1.00 | Route 70 | Lancaster | 1.97 m of water at peak; over 30 cm for 13.5 h; 30 cm reached 9.0 h into the storm; worst hour 25 mm (35% of the storm); a culvert within 100 m is overtopped |
| 13 | 1.00 | Route 12 | Leominster | 0.94 m of water at peak; over 30 cm for 6.5 h; 30 cm reached 6.0 h into the storm; worst hour 85 mm (43% of the storm); water beside the road 0.22 m above its crest (design freeboard 0.30 m; P 1.00); a culvert within 100 m is overtopped |
| 14 | 1.00 | Route 140 | Princeton | 1.02 m of water at peak; over 30 cm for 11.5 h; 30 cm reached 7.0 h into the storm; worst hour 42 mm (28% of the storm); water beside the road 0.23 m above its crest (design freeboard 0.30 m; P 1.00); a culvert within 100 m is overtopped |
| 15 | 1.00 | Merriam Avenue | Leominster | 0.86 m of water at peak; over 30 cm for 5.0 h; 30 cm reached 5.5 h into the storm; worst hour 84 mm (44% of the storm); water beside the road 0.67 m above its crest (design freeboard 0.30 m; P 1.00) |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
