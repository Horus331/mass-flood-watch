# Road-closure prototype: out

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on CPU (OpenMP)), 20 m grid, storm from 2023-09-11T16:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 1,699 |
| Expected closures (sum of probabilities) | 451.0 |
| Segments with closure probability >= 50% | 432 (265.1 km) |
| Culverts overtopped / surcharged | 194 / 0 of 350 |
| Road segments cut off from hospitals | 747 |
| Worst added trip time to a hospital | 47.1 min |
| Heaviest hour of rain | 46.7 mm |
| Flood model run time | 1600 s |

## Checks against what happened

- Storm-day flood reports in the area: 0; water >= 10 cm within 100 m of 0% of them, vs 73% of random points (any day).
- MassDOT repeating flood sites in the area: 1; 1 have a segment within 150 m at P >= 0.5 (share of all segments at P >= 0.5: 25.4%).

## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 1.00 | Route 2 | Westminster | 1.14 m of water at peak; over 30 cm for 34.0 h; 30 cm reached 2.5 h into the storm; worst hour 37 mm (32% of the storm) |
| 2 | 1.00 | Route 2 | Gardner | 1.02 m of water at peak; over 30 cm for 35.5 h; 30 cm reached 1.0 h into the storm; worst hour 16 mm (23% of the storm); a culvert within 100 m is overtopped |
| 3 | 1.00 | Route 2 | Westminster | 1.16 m of water at peak; over 30 cm for 31.0 h; 30 cm reached 5.5 h into the storm; worst hour 25 mm (26% of the storm); a culvert within 100 m is overtopped |
| 4 | 1.00 | Route 2 | Gardner | 6.22 m of water at peak; over 30 cm for 36.0 h; 30 cm reached 0.5 h into the storm; worst hour 22 mm (31% of the storm); a culvert within 100 m is overtopped |
| 5 | 1.00 | Route 2 | Gardner | 3.98 m of water at peak; over 30 cm for 36.0 h; 30 cm reached 0.5 h into the storm; worst hour 25 mm (33% of the storm); a culvert within 100 m is overtopped |
| 6 | 1.00 | Route 2 | Westminster | 0.67 m of water at peak; over 30 cm for 30.0 h; 30 cm reached 5.5 h into the storm; worst hour 37 mm (32% of the storm) |
| 7 | 1.00 | Route 2 | Gardner | 1.98 m of water at peak; over 30 cm for 35.5 h; 30 cm reached 1.0 h into the storm; worst hour 16 mm (23% of the storm); a culvert within 100 m is overtopped |
| 8 | 1.00 | Route 2 | Gardner | 5.08 m of water at peak; over 30 cm for 36.0 h; 30 cm reached 0.5 h into the storm; worst hour 23 mm (31% of the storm); a culvert within 100 m is overtopped |
| 9 | 1.00 | Route 2 | Gardner | 3.89 m of water at peak; over 30 cm for 36.0 h; 30 cm reached 0.5 h into the storm; worst hour 25 mm (33% of the storm); a culvert within 100 m is overtopped |
| 10 | 1.00 | Route 2 | Westminster | 0.93 m of water at peak; over 30 cm for 31.0 h; 30 cm reached 5.5 h into the storm; worst hour 19 mm (24% of the storm) |
| 11 | 1.00 | Route 2 | Gardner | 3.24 m of water at peak; over 30 cm for 35.0 h; 30 cm reached 1.5 h into the storm; worst hour 23 mm (31% of the storm); a culvert within 100 m is overtopped |
| 12 | 1.00 | Route 2 | Gardner | 0.66 m of water at peak; over 30 cm for 34.5 h; 30 cm reached 2.0 h into the storm; worst hour 25 mm (33% of the storm) |
| 13 | 1.00 | Route 2 | Gardner | 0.91 m of water at peak; over 30 cm for 36.0 h; 30 cm reached 0.5 h into the storm; worst hour 26 mm (33% of the storm); a culvert within 100 m is overtopped |
| 14 | 1.00 | Route 68 | Gardner | 3.85 m of water at peak; over 30 cm for 36.0 h; 30 cm reached 0.5 h into the storm; worst hour 26 mm (33% of the storm); a culvert within 100 m is overtopped |
| 15 | 1.00 | Route 2 | Gardner | 2.98 m of water at peak; over 30 cm for 34.5 h; 30 cm reached 2.0 h into the storm; worst hour 24 mm (31% of the storm); a culvert within 100 m is overtopped |

Closure probability v0 = Phi((peak depth - 0.30 m) / 0.10 m): a physics prior, not yet calibrated on observed closures.
