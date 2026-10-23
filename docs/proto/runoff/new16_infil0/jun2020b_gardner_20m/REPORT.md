# Road-closure prototype: jun2020b_loss_jun2020b_gardner_20m

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on CPU (OpenMP)), 20 m grid, storm from 2020-06-28T16:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 2,219 |
| Expected closures (sum of probabilities) | 9.0 |
| Segments with closure probability >= 50% | 1 (0.8 km) |
| Further segments that may close (stream reaches the road crest) | 1 (0.9 km) |
| Culverts overtopped / surcharged | 21 / 0 of 483 |
| Road segments cut off from hospitals | 12 |
| Worst added trip time to a hospital | 14.6 min |
| Heaviest hour of rain | 41.2 mm |
| Flood model run time | 1177 s |

## Checks against what happened

- Storm-day flood reports in the area: 1; water >= 10 cm within 100 m of 100% of them, vs 43% of random points (any day).
- Segments flagged impassable are 0.0x as likely as an average segment to have a report within 200 m.
- MassDOT repeating flood sites in the area: 1; 0 have a segment within 150 m at P >= 0.5 (share of all segments at P >= 0.5: 0.0%).

## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 0.79 | Oakmont Avenue | Westminster | 0.38 m of water at peak; over 30 cm for 6.0 h; 30 cm reached 8.0 h into the storm; worst hour 39 mm (68% of the storm); a culvert within 100 m is overtopped |
| 2 | 0.24 | Route 31 | Fitchburg | 0.23 m of water at peak; worst hour 31 mm (77% of the storm); a culvert within 100 m is overtopped |
| 3 | 0.21 | Veterans Of Foreign Wars Circle | Gardner | 0.22 m of water at peak; worst hour 28 mm (71% of the storm); a culvert within 100 m is overtopped |
| 4 | 0.20 | Pearson Boulevard | Gardner | 0.22 m of water at peak; worst hour 28 mm (71% of the storm); a culvert within 100 m is overtopped |
| 5 | 0.19 | Pearson Boulevard | Gardner | 0.21 m of water at peak; worst hour 28 mm (71% of the storm); a culvert within 100 m is overtopped |
| 6 | 0.19 | Victoria Street | Gardner | 0.21 m of water at peak; worst hour 28 mm (71% of the storm); a culvert within 100 m is overtopped |
| 7 | 0.16 | Route 2 | Gardner | 0.20 m of water at peak; worst hour 28 mm (68% of the storm); a culvert within 100 m is overtopped |
| 8 | 0.16 | Route 2 | Gardner | 0.20 m of water at peak; worst hour 28 mm (68% of the storm); a culvert within 100 m is overtopped |
| 9 | 0.16 | Ramp-Rt 68 To Rt 2 Eb | Gardner | 0.20 m of water at peak; worst hour 28 mm (68% of the storm); a culvert within 100 m is overtopped |
| 10 | 0.16 | Route 68 | Gardner | 0.20 m of water at peak; worst hour 27 mm (68% of the storm); a culvert within 100 m is overtopped |
| 11 | 0.16 | Route 68 | Gardner | 0.20 m of water at peak; worst hour 27 mm (68% of the storm) |
| 12 | 0.15 | American Legion Circle | Gardner | 0.20 m of water at peak; worst hour 27 mm (68% of the storm); a culvert within 100 m is overtopped |
| 13 | 0.15 | Route 68 | Gardner | 0.20 m of water at peak; worst hour 27 mm (68% of the storm) |
| 14 | 0.15 | Narrows Road | Westminster | 0.20 m of water at peak; worst hour 24 mm (78% of the storm); water beside the road 0.30 m below its crest (design freeboard 0.30 m; P 0.51); a culvert within 100 m is overtopped |
| 15 | 0.15 | Temple Street | Gardner | 0.20 m of water at peak; worst hour 30 mm (69% of the storm); water beside the road 0.48 m below its crest (design freeboard 0.30 m; P 0.12); a culvert within 100 m is overtopped |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
