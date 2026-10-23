# Road-closure prototype: sep2018b_loss_sep2018b_gardner_20m

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on CPU (OpenMP)), 20 m grid, storm from 2018-09-26T18:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 1,927 |
| Expected closures (sum of probabilities) | 6.3 |
| Segments with closure probability >= 50% | 0 (0.0 km) |
| Further segments that may close (stream reaches the road crest) | 0 (0.0 km) |
| Culverts overtopped / surcharged | 12 / 0 of 451 |
| Road segments cut off from hospitals | 8 |
| Worst added trip time to a hospital | 12.0 min |
| Heaviest hour of rain | 28.2 mm |
| Flood model run time | 1245 s |

## Checks against what happened

- Storm-day flood reports in the area: 0; water >= 10 cm within 100 m of 0% of them, vs 25% of random points (any day).
- MassDOT repeating flood sites in the area: 1; 0 have a segment within 150 m at P >= 0.5 (share of all segments at P >= 0.5: 0.0%).

## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 0.34 | Oakmont Avenue | Westminster | 0.26 m of water at peak; worst hour 23 mm (72% of the storm); a culvert within 100 m is overtopped |
| 2 | 0.12 | Ramp-Rt 68 To Rt 2 Eb | Gardner | 0.18 m of water at peak; worst hour 25 mm (66% of the storm); a culvert within 100 m is overtopped |
| 3 | 0.12 | Route 12 | Ashburnham | 0.18 m of water at peak; worst hour 21 mm (68% of the storm); a culvert within 100 m is overtopped |
| 4 | 0.12 | Route 2 | Gardner | 0.18 m of water at peak; worst hour 25 mm (66% of the storm); a culvert within 100 m is overtopped |
| 5 | 0.12 | Route 2 | Gardner | 0.18 m of water at peak; worst hour 25 mm (67% of the storm); a culvert within 100 m is overtopped |
| 6 | 0.12 | Route 68 | Gardner | 0.18 m of water at peak; worst hour 24 mm (64% of the storm) |
| 7 | 0.12 | Route 68 | Gardner | 0.18 m of water at peak; worst hour 24 mm (64% of the storm); a culvert within 100 m is overtopped |
| 8 | 0.12 | American Legion Circle | Gardner | 0.18 m of water at peak; worst hour 24 mm (64% of the storm); a culvert within 100 m is overtopped |
| 9 | 0.12 | Route 68 | Gardner | 0.18 m of water at peak; worst hour 24 mm (64% of the storm) |
| 10 | 0.12 | Veterans Of Foreign Wars Circle | Gardner | 0.18 m of water at peak; worst hour 25 mm (69% of the storm); a culvert within 100 m is overtopped |
| 11 | 0.11 | Pearson Boulevard | Gardner | 0.18 m of water at peak; worst hour 25 mm (69% of the storm); a culvert within 100 m is overtopped |
| 12 | 0.11 | Pearson Boulevard | Gardner | 0.17 m of water at peak; worst hour 25 mm (69% of the storm); a culvert within 100 m is overtopped |
| 13 | 0.10 | Victoria Street | Gardner | 0.17 m of water at peak; worst hour 25 mm (69% of the storm); a culvert within 100 m is overtopped |
| 14 | 0.10 | Dyer Street | Gardner | 0.17 m of water at peak; worst hour 23 mm (66% of the storm) |
| 15 | 0.08 | Temple Street | Gardner | 0.16 m of water at peak; worst hour 26 mm (68% of the storm); a culvert within 100 m is overtopped |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
