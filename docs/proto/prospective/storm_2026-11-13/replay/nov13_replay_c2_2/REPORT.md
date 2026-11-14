# Road-closure prototype: arc20261113_loss_nov13_replay_c2_2

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on CPU (OpenMP)), 20 m grid, storm from 2026-11-12T18:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 2,600 |
| Expected closures (sum of probabilities) | 4.1 |
| Segments with closure probability >= 50% | 0 (0.0 km) |
| Further segments that may close (stream reaches the road crest) | 1 (0.3 km) |
| Culverts overtopped / surcharged | 1 / 0 of 681 |
| Road segments cut off from hospitals | 2 |
| Worst added trip time to a hospital | 3.5 min |
| Heaviest hour of rain | 3.7 mm |
| Flood model run time | 2536 s |

## Checks against what happened

- Storm-day flood reports in the area: 0; water >= 10 cm within 100 m of 0% of them, vs 12% of random points (any day).
- MassDOT repeating flood sites in the area: 5; 0 have a segment within 150 m at P >= 0.5 (share of all segments at P >= 0.5: 0.0%).

## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 0.23 | Rogerson Crossing | Uxbridge | 0.23 m of water at peak; worst hour 3 mm (36% of the storm); a culvert within 100 m is overtopped |
| 2 | 0.05 | Mumford Street | Douglas | 0.14 m of water at peak; worst hour 2 mm (27% of the storm) |
| 3 | 0.04 | West Street | Douglas | 0.12 m of water at peak; worst hour 2 mm (23% of the storm) |
| 4 | 0.02 | Conservation Drive | Douglas | 0.10 m of water at peak; worst hour 2 mm (24% of the storm) |
| 5 | 0.02 | West River Street | Upton | 0.09 m of water at peak; worst hour 3 mm (25% of the storm) |
| 6 | 0.01 | Main Street | Sutton | 0.08 m of water at peak; worst hour 2 mm (28% of the storm) |
| 7 | 0.01 | West River Street | Upton | 0.06 m of water at peak; worst hour 3 mm (22% of the storm) |
| 8 | 0.01 | State Forest Road | Sutton | 0.05 m of water at peak; worst hour 3 mm (27% of the storm) |
| 9 | 0.01 | Old Cemetery Road | Upton | 0.05 m of water at peak; worst hour 3 mm (21% of the storm) |
| 10 | 0.01 | Pond Street | Uxbridge | 0.04 m of water at peak; worst hour 3 mm (30% of the storm) |
| 11 | 0.01 | Quaker Highway | Uxbridge | 0.04 m of water at peak; worst hour 2 mm (28% of the storm) |
| 12 | 0.01 | Charles Street | Douglas | 0.04 m of water at peak; worst hour 2 mm (30% of the storm) |
| 13 | 0.01 | Mendon Road | Sutton | 0.04 m of water at peak; worst hour 3 mm (27% of the storm) |
| 14 | 0.01 | Route 16 | Mendon | 0.04 m of water at peak; worst hour 3 mm (22% of the storm) |
| 15 | 0.00 | Milk Street | Blackstone | 0.04 m of water at peak; worst hour 2 mm (21% of the storm) |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
