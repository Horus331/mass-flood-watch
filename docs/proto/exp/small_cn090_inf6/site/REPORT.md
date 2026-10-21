# Road-closure prototype: sep2023_exp_small_cn090_inf6

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on CPU (OpenMP)), 20 m grid, storm from 2023-09-11T16:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 5,100 |
| Expected closures (sum of probabilities) | 318.0 |
| Segments with closure probability >= 50% | 289 (168.1 km) |
| Culverts overtopped / surcharged | 127 / 0 of 536 |
| Road segments cut off from hospitals | 1073 |
| Worst added trip time to a hospital | 22.1 min |
| Heaviest hour of rain | 89.3 mm |
| Flood model run time | 1785 s |

## Checks against what happened

- Storm-day flood reports in the area: 10; water >= 10 cm within 100 m of 90% of them, vs 78% of random points (any day).
- Segments flagged impassable are 2.3x as likely as an average segment to have a report within 200 m.
- MassDOT repeating flood sites in the area: 4; 2 have a segment within 150 m at P >= 0.5 (share of all segments at P >= 0.5: 5.7%).

## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 1.00 | Route 2 | Leominster | 1.53 m of water at peak; over 30 cm for 42.5 h; 30 cm reached 6.0 h into the storm; worst hour 79 mm (45% of the storm) |
| 2 | 1.00 | Route 2 | Leominster | 1.72 m of water at peak; over 30 cm for 46.0 h; 30 cm reached 2.5 h into the storm; worst hour 81 mm (44% of the storm) |
| 3 | 1.00 | Route 2 | Leominster | 0.89 m of water at peak; over 30 cm for 42.0 h; 30 cm reached 6.5 h into the storm; worst hour 71 mm (41% of the storm); a culvert within 100 m is overtopped |
| 4 | 1.00 | Route 2 | Leominster | 1.61 m of water at peak; over 30 cm for 42.5 h; 30 cm reached 6.0 h into the storm; worst hour 74 mm (46% of the storm) |
| 5 | 1.00 | Route 2 | Leominster | 1.29 m of water at peak; over 30 cm for 42.5 h; 30 cm reached 6.0 h into the storm; worst hour 80 mm (44% of the storm) |
| 6 | 1.00 | Route 2 | Leominster | 0.82 m of water at peak; over 30 cm for 43.0 h; 30 cm reached 5.5 h into the storm; worst hour 58 mm (38% of the storm) |
| 7 | 1.00 | I-190 | Leominster | 2.11 m of water at peak; over 30 cm for 44.5 h; 30 cm reached 4.0 h into the storm; worst hour 71 mm (41% of the storm); a culvert within 100 m is overtopped |
| 8 | 1.00 | Massachusetts Avenue | Lunenburg | 2.05 m of water at peak; over 30 cm for 48.0 h; 30 cm reached 0.5 h into the storm; worst hour 26 mm (27% of the storm) |
| 9 | 1.00 | Route 117 | Lancaster | 1.20 m of water at peak; over 30 cm for 43.0 h; 30 cm reached 5.5 h into the storm; worst hour 25 mm (34% of the storm) |
| 10 | 1.00 | John Fitch Highway | Fitchburg | 3.84 m of water at peak; over 30 cm for 48.0 h; 30 cm reached 0.5 h into the storm; worst hour 35 mm (39% of the storm) |
| 11 | 1.00 | John Fitch Highway | Fitchburg | 3.17 m of water at peak; over 30 cm for 48.0 h; 30 cm reached 0.5 h into the storm; worst hour 30 mm (32% of the storm) |
| 12 | 1.00 | Massachusetts Avenue | Lunenburg | 1.31 m of water at peak; over 30 cm for 48.0 h; 30 cm reached 0.5 h into the storm; worst hour 27 mm (28% of the storm); a culvert within 100 m is overtopped |
| 13 | 1.00 | John Fitch Highway | Fitchburg | 1.20 m of water at peak; over 30 cm for 47.0 h; 30 cm reached 1.5 h into the storm; worst hour 36 mm (39% of the storm); a culvert within 100 m is overtopped |
| 14 | 1.00 | Bemis Road | Fitchburg | 0.67 m of water at peak; over 30 cm for 47.0 h; 30 cm reached 1.5 h into the storm; worst hour 41 mm (44% of the storm) |
| 15 | 1.00 | Route 117 | Lancaster | 1.91 m of water at peak; over 30 cm for 42.5 h; 30 cm reached 0.0 h into the storm; worst hour 23 mm (43% of the storm); a culvert within 100 m is overtopped |

Closure probability v0 = Phi((peak depth - 0.30 m) / 0.10 m): a physics prior, not yet calibrated on observed closures.
