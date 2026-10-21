# Road-closure prototype: sep2023_proto_diag

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on CPU (OpenMP)), 20 m grid, storm from 2023-09-11T16:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 5,102 |
| Expected closures (sum of probabilities) | 138.0 |
| Segments with closure probability >= 50% | 126 (67.5 km) |
| Culverts overtopped / surcharged | 29 / 0 of 536 |
| Road segments cut off from hospitals | 270 |
| Worst added trip time to a hospital | 15.6 min |
| Heaviest hour of rain | 19.8 mm |
| Flood model run time | 47 s |

## Checks against what happened

- Storm-day flood reports in the area: 10; water >= 10 cm within 100 m of 0% of them, vs 34% of random points (any day).
- Segments flagged impassable are 0.0x as likely as an average segment to have a report within 200 m.
- MassDOT repeating flood sites in the area: 4; 0 have a segment within 150 m at P >= 0.5 (share of all segments at P >= 0.5: 2.5%).

## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 1.00 | Massachusetts Avenue | Lunenburg | 2.09 m of water at peak; over 30 cm for 2.0 h; 30 cm reached 0.5 h into the storm; worst hour 0 mm (100% of the storm) |
| 2 | 1.00 | John Fitch Highway | Fitchburg | 3.85 m of water at peak; over 30 cm for 2.0 h; 30 cm reached 0.5 h into the storm; worst hour 0 mm (100% of the storm) |
| 3 | 1.00 | John Fitch Highway | Fitchburg | 3.20 m of water at peak; over 30 cm for 2.0 h; 30 cm reached 0.5 h into the storm; worst hour 1 mm (100% of the storm) |
| 4 | 1.00 | Massachusetts Avenue | Lunenburg | 1.59 m of water at peak; over 30 cm for 2.0 h; 30 cm reached 0.5 h into the storm; worst hour 1 mm (100% of the storm); a culvert within 100 m is overtopped |
| 5 | 1.00 | Route 13 | Lunenburg | 1.00 m of water at peak; over 30 cm for 2.5 h; 30 cm reached 0.0 h into the storm; worst hour 1 mm (100% of the storm) |
| 6 | 1.00 | John Fitch Highway | Fitchburg | 0.98 m of water at peak; over 30 cm for 2.0 h; 30 cm reached 0.5 h into the storm; worst hour 2 mm (100% of the storm) |
| 7 | 1.00 | John Fitch Highway | Fitchburg | 3.19 m of water at peak; over 30 cm for 2.0 h; 30 cm reached 0.5 h into the storm; worst hour 1 mm (100% of the storm) |
| 8 | 1.00 | Lunenburg Street | Fitchburg | 1.27 m of water at peak; over 30 cm for 2.0 h; 30 cm reached 0.5 h into the storm; worst hour 1 mm (100% of the storm) |
| 9 | 1.00 | Summer Street | Fitchburg | 3.20 m of water at peak; over 30 cm for 1.5 h; 30 cm reached 1.0 h into the storm; worst hour 0 mm (100% of the storm) |
| 10 | 1.00 | Massachusetts Avenue | Lunenburg | 3.04 m of water at peak; over 30 cm for 2.0 h; 30 cm reached 0.5 h into the storm; worst hour 0 mm (0% of the storm); a culvert within 100 m is overtopped |
| 11 | 1.00 | Massachusetts Avenue | Lunenburg | 2.33 m of water at peak; over 30 cm for 2.0 h; 30 cm reached 0.5 h into the storm; worst hour 0 mm (100% of the storm); a culvert within 100 m is overtopped |
| 12 | 1.00 | John Fitch Highway | Fitchburg | 1.21 m of water at peak; over 30 cm for 1.0 h; 30 cm reached 1.5 h into the storm; worst hour 4 mm (100% of the storm); a culvert within 100 m is overtopped |
| 13 | 1.00 | Bemis Road | Fitchburg | 0.68 m of water at peak; over 30 cm for 1.0 h; 30 cm reached 1.5 h into the storm; worst hour 0 mm (100% of the storm) |
| 14 | 1.00 | Summer Street | Lunenburg | 3.84 m of water at peak; over 30 cm for 1.5 h; 30 cm reached 1.0 h into the storm; worst hour 0 mm (0% of the storm) |
| 15 | 1.00 | John Fitch Highway | Fitchburg | 1.21 m of water at peak; over 30 cm for 1.0 h; 30 cm reached 1.5 h into the storm; worst hour 4 mm (100% of the storm); a culvert within 100 m is overtopped |

Closure probability v0 = Phi((peak depth - 0.30 m) / 0.10 m): a physics prior, not yet calibrated on observed closures.
