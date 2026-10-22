# Road-closure prototype: sep2023_proto_leominster_sep2023

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on CPU (OpenMP)), 20 m grid, storm from 2023-09-11T16:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 5,100 |
| Expected closures (sum of probabilities) | 272.2 |
| Segments with closure probability >= 50% | 237 (161.8 km) |
| Further segments that may close (stream reaches the road crest) | 264 (163.2 km) |
| Culverts overtopped / surcharged | 168 / 20 of 713 |
| Road segments cut off from hospitals | 1009 |
| Worst added trip time to a hospital | 27.0 min |
| Heaviest hour of rain | 89.3 mm |
| Flood model run time | 1749 s |

## Checks against what happened

- Storm-day flood reports in the area: 10; water >= 10 cm within 100 m of 100% of them, vs 84% of random points (any day).
- Segments flagged impassable are 2.62x as likely as an average segment to have a report within 200 m.
- MassDOT repeating flood sites in the area: 4; 2 have a segment within 150 m at P >= 0.5 (share of all segments at P >= 0.5: 4.6%).

## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 1.00 | Route 2 | Leominster | 2.64 m of water at peak; over 30 cm for 42.5 h; 30 cm reached 6.0 h into the storm; worst hour 79 mm (45% of the storm); water beside the road 2.43 m above its crest (design freeboard 0.30 m; P 1.00) |
| 2 | 1.00 | Route 2 | Leominster | 1.11 m of water at peak; over 30 cm for 42.5 h; 30 cm reached 6.0 h into the storm; worst hour 71 mm (41% of the storm); water beside the road 0.84 m above its crest (design freeboard 0.30 m; P 1.00); a culvert within 100 m is overtopped |
| 3 | 1.00 | Route 2 | Leominster | 2.73 m of water at peak; over 30 cm for 43.0 h; 30 cm reached 5.5 h into the storm; worst hour 74 mm (46% of the storm); water beside the road 2.65 m above its crest (design freeboard 0.30 m; P 1.00) |
| 4 | 1.00 | Route 2 | Leominster | 0.88 m of water at peak; over 30 cm for 43.5 h; 30 cm reached 5.0 h into the storm; worst hour 58 mm (38% of the storm); water beside the road 0.96 m above its crest (design freeboard 0.30 m; P 1.00) |
| 5 | 1.00 | Route 2 | Leominster | 2.40 m of water at peak; over 30 cm for 42.5 h; 30 cm reached 6.0 h into the storm; worst hour 80 mm (44% of the storm); water beside the road 0.05 m above its crest (design freeboard 0.30 m; P 0.99) |
| 6 | 1.00 | I-190 | Lancaster | 3.75 m of water at peak; over 30 cm for 44.5 h; 30 cm reached 0.5 h into the storm; worst hour 47 mm (38% of the storm); a culvert within 100 m is overtopped |
| 7 | 1.00 | I-190 | Leominster | 2.63 m of water at peak; over 30 cm for 42.5 h; 30 cm reached 6.0 h into the storm; worst hour 71 mm (41% of the storm); water beside the road 0.17 m above its crest (design freeboard 0.30 m; P 1.00); a culvert within 100 m is overtopped |
| 8 | 1.00 | Route 2 | Leominster | 2.63 m of water at peak; over 30 cm for 42.5 h; 30 cm reached 6.0 h into the storm; worst hour 67 mm (40% of the storm); water beside the road 0.43 m above its crest (design freeboard 0.30 m; P 1.00); a culvert within 100 m is overtopped |
| 9 | 1.00 | I-190 | Lancaster | 1.07 m of water at peak; over 30 cm for 40.5 h; 30 cm reached 8.0 h into the storm; worst hour 31 mm (30% of the storm); a culvert within 100 m is overtopped |
| 10 | 1.00 | I-190 | Sterling | 1.39 m of water at peak; over 30 cm for 40.5 h; 30 cm reached 8.0 h into the storm; worst hour 20 mm (26% of the storm); a culvert within 100 m is overtopped |
| 11 | 1.00 | I-190 | Lancaster | 1.07 m of water at peak; over 30 cm for 40.5 h; 30 cm reached 8.0 h into the storm; worst hour 38 mm (34% of the storm); a culvert within 100 m is overtopped |
| 12 | 1.00 | I-190 | Sterling | 1.39 m of water at peak; over 30 cm for 40.5 h; 30 cm reached 8.0 h into the storm; worst hour 20 mm (27% of the storm); water beside the road 0.22 m below its crest (design freeboard 0.30 m; P 0.70); a culvert within 100 m is overtopped |
| 13 | 1.00 | (unnamed) | Leominster | 1.70 m of water at peak; over 30 cm for 42.5 h; 30 cm reached 6.0 h into the storm; worst hour 84 mm (43% of the storm); water beside the road 0.09 m above its crest (design freeboard 0.30 m; P 0.99); a culvert within 100 m is overtopped |
| 14 | 1.00 | Rollstone Road | Fitchburg | 0.93 m of water at peak; over 30 cm for 42.5 h; 30 cm reached 6.0 h into the storm; worst hour 34 mm (34% of the storm); a culvert within 100 m is overtopped |
| 15 | 1.00 | Electric Avenue | Fitchburg | 0.93 m of water at peak; over 30 cm for 42.5 h; 30 cm reached 6.0 h into the storm; worst hour 34 mm (34% of the storm); a culvert within 100 m is overtopped |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
