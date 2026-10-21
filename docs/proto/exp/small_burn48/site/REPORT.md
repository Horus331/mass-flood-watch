# Road-closure prototype: sep2023_exp_small_burn48

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on CPU (OpenMP)), 20 m grid, storm from 2023-09-11T16:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 5,100 |
| Expected closures (sum of probabilities) | 477.3 |
| Segments with closure probability >= 50% | 436 (267.8 km) |
| Culverts overtopped / surcharged | 205 / 0 of 536 |
| Road segments cut off from hospitals | 1868 |
| Worst added trip time to a hospital | 33.5 min |
| Heaviest hour of rain | 89.3 mm |
| Flood model run time | 2003 s |

## Checks against what happened

- Storm-day flood reports in the area: 10; water >= 10 cm within 100 m of 100% of them, vs 87% of random points (any day).
- Segments flagged impassable are 2.34x as likely as an average segment to have a report within 200 m.
- MassDOT repeating flood sites in the area: 4; 2 have a segment within 150 m at P >= 0.5 (share of all segments at P >= 0.5: 8.5%).

## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 1.00 | Route 2 | Leominster | 3.32 m of water at peak; over 30 cm for 43.5 h; 30 cm reached 5.0 h into the storm; worst hour 79 mm (45% of the storm) |
| 2 | 1.00 | Route 2 | Leominster | 1.82 m of water at peak; over 30 cm for 46.0 h; 30 cm reached 2.5 h into the storm; worst hour 81 mm (44% of the storm) |
| 3 | 1.00 | Route 2 | Leominster | 1.14 m of water at peak; over 30 cm for 42.5 h; 30 cm reached 6.0 h into the storm; worst hour 71 mm (41% of the storm); a culvert within 100 m is overtopped |
| 4 | 1.00 | Route 2 | Leominster | 3.40 m of water at peak; over 30 cm for 43.5 h; 30 cm reached 5.0 h into the storm; worst hour 74 mm (46% of the storm) |
| 5 | 1.00 | Route 2 | Leominster | 3.08 m of water at peak; over 30 cm for 43.5 h; 30 cm reached 5.0 h into the storm; worst hour 80 mm (44% of the storm) |
| 6 | 1.00 | Route 2 | Leominster | 0.88 m of water at peak; over 30 cm for 43.5 h; 30 cm reached 5.0 h into the storm; worst hour 58 mm (38% of the storm) |
| 7 | 1.00 | I-190 | Leominster | 2.42 m of water at peak; over 30 cm for 45.0 h; 30 cm reached 3.5 h into the storm; worst hour 71 mm (41% of the storm); a culvert within 100 m is overtopped |
| 8 | 1.00 | I-190 | Lancaster | 1.17 m of water at peak; over 30 cm for 41.5 h; 30 cm reached 7.0 h into the storm; worst hour 31 mm (30% of the storm); a culvert within 100 m is overtopped |
| 9 | 1.00 | I-190 | Sterling | 1.60 m of water at peak; over 30 cm for 42.0 h; 30 cm reached 6.5 h into the storm; worst hour 20 mm (26% of the storm); a culvert within 100 m is overtopped |
| 10 | 1.00 | I-190 | Lancaster | 1.17 m of water at peak; over 30 cm for 41.5 h; 30 cm reached 7.0 h into the storm; worst hour 38 mm (34% of the storm); a culvert within 100 m is overtopped |
| 11 | 1.00 | I-190 | Sterling | 1.60 m of water at peak; over 30 cm for 42.0 h; 30 cm reached 6.5 h into the storm; worst hour 20 mm (27% of the storm); a culvert within 100 m is overtopped |
| 12 | 1.00 | Massachusetts Avenue | Lunenburg | 2.06 m of water at peak; over 30 cm for 48.0 h; 30 cm reached 0.5 h into the storm; worst hour 26 mm (27% of the storm) |
| 13 | 1.00 | Route 117 | Lancaster | 1.41 m of water at peak; over 30 cm for 43.0 h; 30 cm reached 5.5 h into the storm; worst hour 25 mm (34% of the storm) |
| 14 | 1.00 | John Fitch Highway | Fitchburg | 3.87 m of water at peak; over 30 cm for 48.0 h; 30 cm reached 0.5 h into the storm; worst hour 35 mm (39% of the storm) |
| 15 | 1.00 | John Fitch Highway | Fitchburg | 3.20 m of water at peak; over 30 cm for 48.0 h; 30 cm reached 0.5 h into the storm; worst hour 30 mm (32% of the storm) |

Closure probability v0 = Phi((peak depth - 0.30 m) / 0.10 m): a physics prior, not yet calibrated on observed closures.
