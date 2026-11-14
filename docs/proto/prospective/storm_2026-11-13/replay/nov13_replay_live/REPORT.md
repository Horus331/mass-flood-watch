# Road-closure prototype: arc20261113_loss_nov13_replay_live

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on CPU (OpenMP)), 20 m grid, storm from 2026-11-12T18:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 2,600 |
| Expected closures (sum of probabilities) | 6.0 |
| Segments with closure probability >= 50% | 2 (1.4 km) |
| Further segments that may close (stream reaches the road crest) | 1 (0.3 km) |
| Culverts overtopped / surcharged | 6 / 0 of 681 |
| Road segments cut off from hospitals | 12 |
| Worst added trip time to a hospital | 5.2 min |
| Heaviest hour of rain | 3.7 mm |
| Flood model run time | 2211 s |

## Checks against what happened

- Storm-day flood reports in the area: 0; water >= 10 cm within 100 m of 0% of them, vs 12% of random points (any day).
- MassDOT repeating flood sites in the area: 5; 0 have a segment within 150 m at P >= 0.5 (share of all segments at P >= 0.5: 0.1%).

## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 0.95 | Rogerson Crossing | Uxbridge | 0.47 m of water at peak; over 30 cm for 0.5 h; 30 cm reached 0.5 h into the storm; worst hour 3 mm (36% of the storm); a culvert within 100 m is overtopped |
| 2 | 0.50 | Gilboa Street | Douglas | 0.30 m of water at peak; worst hour 3 mm (30% of the storm); water beside the road 0.49 m below its crest (design freeboard 0.30 m; P 0.11); a culvert within 100 m is overtopped |
| 3 | 0.11 | Mumford Street | Douglas | 0.17 m of water at peak; worst hour 2 mm (27% of the storm); a culvert within 100 m is overtopped |
| 4 | 0.10 | West Street | Douglas | 0.17 m of water at peak; worst hour 2 mm (23% of the storm); a culvert within 100 m is overtopped |
| 5 | 0.07 | Route 146 | Uxbridge | 0.15 m of water at peak; worst hour 2 mm (29% of the storm); a culvert within 100 m is overtopped |
| 6 | 0.07 | Main Street | Sutton | 0.15 m of water at peak; worst hour 2 mm (28% of the storm); a culvert within 100 m is overtopped |
| 7 | 0.05 | Conservation Drive | Douglas | 0.14 m of water at peak; worst hour 2 mm (24% of the storm); cut off from hospitals |
| 8 | 0.04 | Rivulet Street | Uxbridge | 0.12 m of water at peak; worst hour 3 mm (37% of the storm) |
| 9 | 0.03 | Elm Street | Uxbridge | 0.11 m of water at peak; worst hour 3 mm (37% of the storm) |
| 10 | 0.03 | Quaker Highway | Uxbridge | 0.11 m of water at peak; worst hour 2 mm (28% of the storm) |
| 11 | 0.03 | West River Street | Upton | 0.10 m of water at peak; worst hour 3 mm (25% of the storm) |
| 12 | 0.02 | Pond Street | Uxbridge | 0.10 m of water at peak; worst hour 3 mm (30% of the storm); +5 min to the nearest hospital |
| 13 | 0.02 | Mill Street | Uxbridge | 0.10 m of water at peak; worst hour 2 mm (30% of the storm) |
| 14 | 0.02 | Hollis Street | Uxbridge | 0.10 m of water at peak; worst hour 3 mm (30% of the storm) |
| 15 | 0.01 | State Forest Road | Sutton | 0.07 m of water at peak; worst hour 3 mm (27% of the storm) |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
