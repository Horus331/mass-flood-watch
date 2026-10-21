# Road-closure prototype: sep2023_exp_small_cn3

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on CPU (OpenMP)), 20 m grid, storm from 2023-09-11T16:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 5,100 |
| Expected closures (sum of probabilities) | 491.3 |
| Segments with closure probability >= 50% | 446 (275.9 km) |
| Culverts overtopped / surcharged | 220 / 0 of 536 |
| Road segments cut off from hospitals | 1906 |
| Worst added trip time to a hospital | 32.2 min |
| Heaviest hour of rain | 89.3 mm |
| Flood model run time | 2688 s |

## Checks against what happened

- Storm-day flood reports in the area: 10; water >= 10 cm within 100 m of 100% of them, vs 88% of random points (any day).
- Segments flagged impassable are 2.18x as likely as an average segment to have a report within 200 m.
- MassDOT repeating flood sites in the area: 4; 2 have a segment within 150 m at P >= 0.5 (share of all segments at P >= 0.5: 8.7%).

## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 1.00 | Route 2 | Leominster | 3.29 m of water at peak; over 30 cm for 43.0 h; 30 cm reached 5.5 h into the storm; worst hour 79 mm (45% of the storm) |
| 2 | 1.00 | Route 2 | Leominster | 1.87 m of water at peak; over 30 cm for 46.0 h; 30 cm reached 2.5 h into the storm; worst hour 81 mm (44% of the storm) |
| 3 | 1.00 | Route 2 | Leominster | 1.18 m of water at peak; over 30 cm for 42.5 h; 30 cm reached 6.0 h into the storm; worst hour 71 mm (41% of the storm); a culvert within 100 m is overtopped |
| 4 | 1.00 | Route 2 | Leominster | 3.37 m of water at peak; over 30 cm for 43.0 h; 30 cm reached 5.5 h into the storm; worst hour 74 mm (46% of the storm) |
| 5 | 1.00 | Route 2 | Leominster | 3.04 m of water at peak; over 30 cm for 43.0 h; 30 cm reached 5.5 h into the storm; worst hour 80 mm (44% of the storm) |
| 6 | 1.00 | Route 2 | Leominster | 0.91 m of water at peak; over 30 cm for 43.5 h; 30 cm reached 5.0 h into the storm; worst hour 58 mm (38% of the storm) |
| 7 | 1.00 | Route 2 | Fitchburg | 0.65 m of water at peak; over 30 cm for 42.0 h; 30 cm reached 6.5 h into the storm; worst hour 51 mm (46% of the storm); a culvert within 100 m is overtopped |
| 8 | 1.00 | Route 2 | Leominster | 0.73 m of water at peak; over 30 cm for 40.0 h; 30 cm reached 7.0 h into the storm; worst hour 57 mm (47% of the storm); a culvert within 100 m is overtopped |
| 9 | 1.00 | Route 2 | Fitchburg | 0.65 m of water at peak; over 30 cm for 42.0 h; 30 cm reached 6.5 h into the storm; worst hour 51 mm (46% of the storm); a culvert within 100 m is overtopped |
| 10 | 1.00 | I-190 | Leominster | 2.40 m of water at peak; over 30 cm for 45.0 h; 30 cm reached 3.5 h into the storm; worst hour 71 mm (41% of the storm); a culvert within 100 m is overtopped |
| 11 | 1.00 | Route 2 | Leominster | 0.74 m of water at peak; over 30 cm for 40.0 h; 30 cm reached 7.0 h into the storm; worst hour 59 mm (47% of the storm); a culvert within 100 m is overtopped |
| 12 | 1.00 | I-190 | Lancaster | 1.17 m of water at peak; over 30 cm for 41.5 h; 30 cm reached 7.0 h into the storm; worst hour 31 mm (30% of the storm); a culvert within 100 m is overtopped |
| 13 | 1.00 | I-190 | Sterling | 1.60 m of water at peak; over 30 cm for 41.5 h; 30 cm reached 7.0 h into the storm; worst hour 20 mm (26% of the storm); a culvert within 100 m is overtopped |
| 14 | 1.00 | I-190 | Lancaster | 1.17 m of water at peak; over 30 cm for 41.5 h; 30 cm reached 7.0 h into the storm; worst hour 38 mm (34% of the storm); a culvert within 100 m is overtopped |
| 15 | 1.00 | I-190 | Sterling | 1.60 m of water at peak; over 30 cm for 41.5 h; 30 cm reached 7.0 h into the storm; worst hour 20 mm (27% of the storm); a culvert within 100 m is overtopped |

Closure probability v0 = Phi((peak depth - 0.30 m) / 0.10 m): a physics prior, not yet calibrated on observed closures.
