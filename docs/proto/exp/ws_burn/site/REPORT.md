# Road-closure prototype: sep2023_exp_ws_burn

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on CPU (OpenMP)), 20 m grid, storm from 2023-09-11T16:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 10,607 |
| Expected closures (sum of probabilities) | 922.3 |
| Segments with closure probability >= 50% | 862 (586.2 km) |
| Culverts overtopped / surcharged | 511 / 0 of 1802 |
| Road segments cut off from hospitals | 4298 |
| Worst added trip time to a hospital | 66.2 min |
| Heaviest hour of rain | 90.7 mm |
| Flood model run time | 9673 s |

## Checks against what happened

- Storm-day flood reports in the area: 10; water >= 10 cm within 100 m of 100% of them, vs 80% of random points (any day).
- Segments flagged impassable are 2.48x as likely as an average segment to have a report within 200 m.
- MassDOT repeating flood sites in the area: 4; 3 have a segment within 150 m at P >= 0.5 (share of all segments at P >= 0.5: 8.1%).

## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 1.00 | Route 2 | Leominster | 3.33 m of water at peak; over 30 cm for 43.5 h; 30 cm reached 5.0 h into the storm; worst hour 79 mm (45% of the storm) |
| 2 | 1.00 | Route 2 | Leominster | 1.14 m of water at peak; over 30 cm for 42.5 h; 30 cm reached 6.0 h into the storm; worst hour 71 mm (41% of the storm); a culvert within 100 m is overtopped |
| 3 | 1.00 | Route 2 | Leominster | 3.42 m of water at peak; over 30 cm for 43.5 h; 30 cm reached 5.0 h into the storm; worst hour 74 mm (46% of the storm) |
| 4 | 1.00 | Route 2 | Leominster | 3.09 m of water at peak; over 30 cm for 43.5 h; 30 cm reached 5.0 h into the storm; worst hour 80 mm (44% of the storm) |
| 5 | 1.00 | Route 2 | Leominster | 0.88 m of water at peak; over 30 cm for 43.5 h; 30 cm reached 5.0 h into the storm; worst hour 58 mm (38% of the storm) |
| 6 | 1.00 | I-190 | Leominster | 1.48 m of water at peak; over 30 cm for 42.5 h; 30 cm reached 6.0 h into the storm; worst hour 71 mm (41% of the storm); a culvert within 100 m is overtopped |
| 7 | 1.00 | I-190 | Lancaster | 1.16 m of water at peak; over 30 cm for 41.5 h; 30 cm reached 7.0 h into the storm; worst hour 31 mm (30% of the storm); a culvert within 100 m is overtopped |
| 8 | 1.00 | Route 2 | Harvard | 0.80 m of water at peak; over 30 cm for 32.5 h; 30 cm reached 7.5 h into the storm; worst hour 29 mm (41% of the storm); a culvert within 100 m is overtopped |
| 9 | 1.00 | Route 2 | Harvard | 0.80 m of water at peak; over 30 cm for 33.0 h; 30 cm reached 7.5 h into the storm; worst hour 33 mm (44% of the storm); a culvert within 100 m is overtopped |
| 10 | 1.00 | I-190 | Sterling | 1.60 m of water at peak; over 30 cm for 42.0 h; 30 cm reached 6.5 h into the storm; worst hour 20 mm (26% of the storm); a culvert within 100 m is overtopped |
| 11 | 1.00 | I-190 | Lancaster | 1.17 m of water at peak; over 30 cm for 41.5 h; 30 cm reached 7.0 h into the storm; worst hour 38 mm (34% of the storm); a culvert within 100 m is overtopped |
| 12 | 1.00 | Route 2 | Gardner | 1.43 m of water at peak; over 30 cm for 42.0 h; 30 cm reached 6.5 h into the storm; worst hour 26 mm (29% of the storm); a culvert within 100 m is overtopped |
| 13 | 1.00 | I-190 | Sterling | 1.60 m of water at peak; over 30 cm for 42.0 h; 30 cm reached 6.5 h into the storm; worst hour 20 mm (27% of the storm); a culvert within 100 m is overtopped |
| 14 | 1.00 | Route 2 | Gardner | 1.43 m of water at peak; over 30 cm for 42.0 h; 30 cm reached 6.5 h into the storm; worst hour 26 mm (29% of the storm); a culvert within 100 m is overtopped |
| 15 | 1.00 | Route 2 | Templeton | 1.29 m of water at peak; over 30 cm for 43.5 h; 30 cm reached 5.0 h into the storm; worst hour 24 mm (28% of the storm) |

Closure probability v0 = Phi((peak depth - 0.30 m) / 0.10 m): a physics prior, not yet calibrated on observed closures.
