# Road-closure prototype: sep2023_exp_small_sgc

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on CPU (OpenMP)), 20 m grid, storm from 2023-09-11T16:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 5,100 |
| Expected closures (sum of probabilities) | 4778.1 |
| Segments with closure probability >= 50% | 4777 (1438.5 km) |
| Culverts overtopped / surcharged | 289 / 0 of 536 |
| Road segments cut off from hospitals | 290 |
| Worst added trip time to a hospital | 28.3 min |
| Heaviest hour of rain | 89.3 mm |
| Flood model run time | 16641 s |

## Checks against what happened

- Storm-day flood reports in the area: 10; water >= 10 cm within 100 m of 100% of them, vs 99% of random points (any day).
- Segments flagged impassable are 1.06x as likely as an average segment to have a report within 200 m.
- MassDOT repeating flood sites in the area: 4; 3 have a segment within 150 m at P >= 0.5 (share of all segments at P >= 0.5: 93.7%).

## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 1.00 | Route 2 | Leominster | 410.06 m of water at peak; over 30 cm for 44.5 h; 30 cm reached 4.0 h into the storm; worst hour 81 mm (44% of the storm) |
| 2 | 1.00 | Route 2 | Leominster | 375.92 m of water at peak; over 30 cm for 44.5 h; 30 cm reached 4.0 h into the storm; worst hour 80 mm (43% of the storm) |
| 3 | 1.00 | Route 2 | Leominster | 323.90 m of water at peak; over 30 cm for 43.5 h; 30 cm reached 5.0 h into the storm; worst hour 79 mm (45% of the storm) |
| 4 | 1.00 | Route 2 | Leominster | 322.58 m of water at peak; over 30 cm for 43.5 h; 30 cm reached 5.0 h into the storm; worst hour 71 mm (41% of the storm); a culvert within 100 m is overtopped |
| 5 | 1.00 | Route 2 | Lancaster | 183.04 m of water at peak; over 30 cm for 43.5 h; 30 cm reached 5.0 h into the storm; worst hour 46 mm (38% of the storm) |
| 6 | 1.00 | Route 2 | Lancaster | 155.48 m of water at peak; over 30 cm for 43.5 h; 30 cm reached 5.0 h into the storm; worst hour 44 mm (33% of the storm) |
| 7 | 1.00 | Route 2 | Lancaster | 158.48 m of water at peak; over 30 cm for 43.5 h; 30 cm reached 5.0 h into the storm; worst hour 46 mm (44% of the storm) |
| 8 | 1.00 | Route 2 | Lancaster | 128.59 m of water at peak; over 30 cm for 43.5 h; 30 cm reached 5.0 h into the storm; worst hour 45 mm (48% of the storm) |
| 9 | 1.00 | Route 2 | Leominster | 410.06 m of water at peak; over 30 cm for 45.0 h; 30 cm reached 3.5 h into the storm; worst hour 81 mm (44% of the storm) |
| 10 | 1.00 | Route 2 | Lancaster | 140.31 m of water at peak; over 30 cm for 43.5 h; 30 cm reached 5.0 h into the storm; worst hour 42 mm (49% of the storm); a culvert within 100 m is overtopped |
| 11 | 1.00 | Route 2 | Lancaster | 217.40 m of water at peak; over 30 cm for 43.0 h; 30 cm reached 5.0 h into the storm; worst hour 41 mm (48% of the storm) |
| 12 | 1.00 | Route 2 | Leominster | 355.59 m of water at peak; over 30 cm for 44.0 h; 30 cm reached 4.5 h into the storm; worst hour 78 mm (43% of the storm) |
| 13 | 1.00 | Route 2 | Leominster | 336.33 m of water at peak; over 30 cm for 44.0 h; 30 cm reached 4.5 h into the storm; worst hour 80 mm (44% of the storm) |
| 14 | 1.00 | Route 2 | Leominster | 217.30 m of water at peak; over 30 cm for 43.5 h; 30 cm reached 5.0 h into the storm; worst hour 68 mm (46% of the storm) |
| 15 | 1.00 | Route 2 | Leominster | 172.95 m of water at peak; over 30 cm for 43.5 h; 30 cm reached 5.0 h into the storm; worst hour 57 mm (47% of the storm); a culvert within 100 m is overtopped |

Closure probability v0 = Phi((peak depth - 0.30 m) / 0.10 m): a physics prior, not yet calibrated on observed closures.
