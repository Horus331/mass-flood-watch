# Road-closure prototype: sep2023_proto_leominster_sep2023

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on CPU (OpenMP)), 20 m grid, storm from 2023-09-11T16:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 5,102 |
| Expected closures (sum of probabilities) | 524.3 |
| Segments with closure probability >= 50% | 480 (293.9 km) |
| Culverts overtopped / surcharged | 209 / 0 of 536 |
| Road segments cut off from hospitals | 2141 |
| Worst added trip time to a hospital | 32.9 min |
| Heaviest hour of rain | 89.3 mm |
| Flood model run time | 1281 s |

## Checks against what happened

- Storm-day flood reports in the area: 10; water >= 10 cm within 100 m of 100% of them, vs 87% of random points (any day).
- Segments flagged impassable are 2.35x as likely as an average segment to have a report within 200 m.
- MassDOT repeating flood sites in the area: 4; 2 have a segment within 150 m at P >= 0.5 (share of all segments at P >= 0.5: 9.4%).

## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 1.00 | Route 2 | Leominster | 3.40 m of water at peak; over 30 cm for 31.5 h; 30 cm reached 5.0 h into the storm; worst hour 79 mm (47% of the storm) |
| 2 | 1.00 | Route 2 | Leominster | 1.84 m of water at peak; over 30 cm for 34.0 h; 30 cm reached 2.5 h into the storm; worst hour 81 mm (45% of the storm) |
| 3 | 1.00 | Route 2 | Leominster | 1.16 m of water at peak; over 30 cm for 30.5 h; 30 cm reached 6.0 h into the storm; worst hour 71 mm (43% of the storm); a culvert within 100 m is overtopped |
| 4 | 1.00 | Route 2 | Leominster | 3.48 m of water at peak; over 30 cm for 31.5 h; 30 cm reached 5.0 h into the storm; worst hour 74 mm (48% of the storm) |
| 5 | 1.00 | Route 2 | Leominster | 3.16 m of water at peak; over 30 cm for 31.5 h; 30 cm reached 5.0 h into the storm; worst hour 80 mm (46% of the storm) |
| 6 | 1.00 | Route 2 | Leominster | 0.89 m of water at peak; over 30 cm for 31.5 h; 30 cm reached 5.0 h into the storm; worst hour 58 mm (40% of the storm) |
| 7 | 1.00 | I-190 | Leominster | 2.46 m of water at peak; over 30 cm for 33.0 h; 30 cm reached 3.5 h into the storm; worst hour 71 mm (43% of the storm); a culvert within 100 m is overtopped |
| 8 | 1.00 | I-190 | Lancaster | 1.17 m of water at peak; over 30 cm for 29.5 h; 30 cm reached 7.0 h into the storm; worst hour 31 mm (33% of the storm); a culvert within 100 m is overtopped |
| 9 | 1.00 | I-190 | Sterling | 1.60 m of water at peak; over 30 cm for 30.0 h; 30 cm reached 6.5 h into the storm; worst hour 20 mm (29% of the storm); a culvert within 100 m is overtopped |
| 10 | 1.00 | I-190 | Lancaster | 1.17 m of water at peak; over 30 cm for 29.5 h; 30 cm reached 7.0 h into the storm; worst hour 38 mm (36% of the storm); a culvert within 100 m is overtopped |
| 11 | 1.00 | I-190 | Sterling | 1.60 m of water at peak; over 30 cm for 30.0 h; 30 cm reached 6.5 h into the storm; worst hour 20 mm (30% of the storm); a culvert within 100 m is overtopped |
| 12 | 1.00 | Massachusetts Avenue | Lunenburg | 2.10 m of water at peak; over 30 cm for 36.0 h; 30 cm reached 0.5 h into the storm; worst hour 26 mm (29% of the storm) |
| 13 | 1.00 | John Fitch Highway | Fitchburg | 3.89 m of water at peak; over 30 cm for 36.0 h; 30 cm reached 0.5 h into the storm; worst hour 35 mm (43% of the storm) |
| 14 | 1.00 | John Fitch Highway | Fitchburg | 3.23 m of water at peak; over 30 cm for 36.0 h; 30 cm reached 0.5 h into the storm; worst hour 30 mm (36% of the storm) |
| 15 | 1.00 | Route 117 | Lancaster | 1.46 m of water at peak; over 30 cm for 31.0 h; 30 cm reached 5.5 h into the storm; worst hour 25 mm (37% of the storm) |

Closure probability v0 = Phi((peak depth - 0.30 m) / 0.10 m): a physics prior, not yet calibrated on observed closures.
