# Road-closure prototype: jun2020b_loss_jun2020b_gardner_20m

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on CPU (OpenMP)), 20 m grid, storm from 2020-06-28T16:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 2,219 |
| Expected closures (sum of probabilities) | 6.2 |
| Segments with closure probability >= 50% | 1 (0.8 km) |
| Further segments that may close (stream reaches the road crest) | 0 (0.0 km) |
| Culverts overtopped / surcharged | 5 / 0 of 483 |
| Road segments cut off from hospitals | 1 |
| Worst added trip time to a hospital | 12.1 min |
| Heaviest hour of rain | 41.2 mm |
| Flood model run time | 1217 s |

## Checks against what happened

- Storm-day flood reports in the area: 1; water >= 10 cm within 100 m of 0% of them, vs 38% of random points (any day).
- Segments flagged impassable are 0.0x as likely as an average segment to have a report within 200 m.
- MassDOT repeating flood sites in the area: 1; 0 have a segment within 150 m at P >= 0.5 (share of all segments at P >= 0.5: 0.0%).

## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 0.54 | Oakmont Avenue | Westminster | 0.31 m of water at peak; over 30 cm for 1.0 h; 30 cm reached 8.5 h into the storm; worst hour 39 mm (68% of the storm); a culvert within 100 m is overtopped |
| 2 | 0.43 | Route 12 | Fitchburg | 0.28 m of water at peak; worst hour 37 mm (68% of the storm); a culvert within 100 m is overtopped |
| 3 | 0.23 | Route 31 | Fitchburg | 0.23 m of water at peak; worst hour 31 mm (77% of the storm); a culvert within 100 m is overtopped |
| 4 | 0.15 | Narrows Road | Westminster | 0.20 m of water at peak; worst hour 24 mm (78% of the storm); water beside the road 0.30 m below its crest (design freeboard 0.30 m; P 0.51); a culvert within 100 m is overtopped |
| 5 | 0.11 | Route 12 | Ashburnham | 0.18 m of water at peak; worst hour 30 mm (88% of the storm); a culvert within 100 m is overtopped |
| 6 | 0.06 | South Ashburnham Road | Westminster | 0.14 m of water at peak; worst hour 40 mm (68% of the storm); +6 min to the nearest hospital |
| 7 | 0.06 | Pearson Boulevard | Gardner | 0.14 m of water at peak; worst hour 28 mm (71% of the storm) |
| 8 | 0.06 | (unnamed) | Gardner | 0.14 m of water at peak; worst hour 27 mm (65% of the storm); water beside the road 0.24 m below its crest (design freeboard 0.30 m; P 0.65) |
| 9 | 0.06 | Route 2 | Fitchburg | 0.14 m of water at peak; worst hour 26 mm (77% of the storm) |
| 10 | 0.06 | Pearson Boulevard | Gardner | 0.14 m of water at peak; worst hour 28 mm (71% of the storm) |
| 11 | 0.06 | Victoria Street | Gardner | 0.14 m of water at peak; worst hour 28 mm (71% of the storm) |
| 12 | 0.05 | Fred Smith Road | Westminster | 0.14 m of water at peak; worst hour 32 mm (76% of the storm) |
| 13 | 0.05 | Sanborn Street | Fitchburg | 0.14 m of water at peak; worst hour 32 mm (70% of the storm) |
| 14 | 0.05 | Temple Street | Gardner | 0.13 m of water at peak; worst hour 30 mm (69% of the storm) |
| 15 | 0.04 | South Main Street | Gardner | 0.13 m of water at peak; worst hour 28 mm (70% of the storm) |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
