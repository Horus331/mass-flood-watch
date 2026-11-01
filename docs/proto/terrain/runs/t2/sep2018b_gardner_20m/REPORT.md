# Road-closure prototype: sep2018b_loss_sep2018b_gardner_20m

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on CPU (OpenMP)), 20 m grid, storm from 2018-09-26T18:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 1,927 |
| Expected closures (sum of probabilities) | 4.3 |
| Segments with closure probability >= 50% | 0 (0.0 km) |
| Further segments that may close (stream reaches the road crest) | 0 (0.0 km) |
| Culverts overtopped / surcharged | 2 / 0 of 451 |
| Road segments cut off from hospitals | 0 |
| Worst added trip time to a hospital | 11.6 min |
| Heaviest hour of rain | 28.2 mm |
| Flood model run time | 1198 s |

## Checks against what happened

- Storm-day flood reports in the area: 0; water >= 10 cm within 100 m of 0% of them, vs 25% of random points (any day).
- MassDOT repeating flood sites in the area: 1; 0 have a segment within 150 m at P >= 0.5 (share of all segments at P >= 0.5: 0.0%).

## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 0.31 | Oakmont Avenue | Westminster | 0.25 m of water at peak; worst hour 23 mm (72% of the storm); a culvert within 100 m is overtopped |
| 2 | 0.11 | Route 12 | Ashburnham | 0.18 m of water at peak; worst hour 21 mm (68% of the storm); a culvert within 100 m is overtopped |
| 3 | 0.05 | (unnamed) | Gardner | 0.14 m of water at peak; worst hour 26 mm (64% of the storm); water beside the road 0.25 m below its crest (design freeboard 0.30 m; P 0.63) |
| 4 | 0.04 | Pearson Boulevard | Gardner | 0.13 m of water at peak; worst hour 25 mm (69% of the storm) |
| 5 | 0.04 | Pearson Boulevard | Gardner | 0.12 m of water at peak; worst hour 25 mm (69% of the storm) |
| 6 | 0.04 | Victoria Street | Gardner | 0.12 m of water at peak; worst hour 25 mm (69% of the storm) |
| 7 | 0.03 | South Main Street | Gardner | 0.12 m of water at peak; worst hour 25 mm (69% of the storm) |
| 8 | 0.03 | Mill Street | Gardner | 0.12 m of water at peak; worst hour 24 mm (68% of the storm) |
| 9 | 0.03 | Temple Street | Gardner | 0.12 m of water at peak; worst hour 26 mm (68% of the storm) |
| 10 | 0.03 | Lombard Road | Hubbardston | 0.11 m of water at peak; worst hour 9 mm (44% of the storm) |
| 11 | 0.03 | South Main Street | Ashburnham | 0.11 m of water at peak; worst hour 24 mm (69% of the storm) |
| 12 | 0.03 | American Legion Circle | Gardner | 0.11 m of water at peak; worst hour 24 mm (64% of the storm) |
| 13 | 0.03 | Ramp-Rt 68 To Rt 2 Eb | Gardner | 0.11 m of water at peak; worst hour 25 mm (66% of the storm) |
| 14 | 0.03 | Route 68 | Gardner | 0.11 m of water at peak; worst hour 24 mm (64% of the storm) |
| 15 | 0.03 | Route 68 | Gardner | 0.11 m of water at peak; worst hour 24 mm (64% of the storm) |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
