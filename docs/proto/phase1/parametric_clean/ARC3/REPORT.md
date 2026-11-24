# Road-closure prototype: sep2023_loss_ARC3

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on CPU (OpenMP)), 20 m grid, storm from 2023-09-11T16:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 4,542 |
| Expected closures (sum of probabilities) | 155.4 |
| Segments with closure probability >= 50% | 118 (82.0 km) |
| Further segments that may close (stream reaches the road crest) | 228 (141.9 km) |
| Culverts overtopped / surcharged | 148 / 3 of 616 |
| Road segments cut off from hospitals | 757 |
| Worst added trip time to a hospital | 25.7 min |
| Heaviest hour of rain | 89.3 mm |
| Flood model run time | 2119 s |

## Checks against what happened

- Storm-day flood reports in the area: 10; water >= 10 cm within 100 m of 100% of them, vs 75% of random points (any day).
- Segments flagged impassable are 2.66x as likely as an average segment to have a report within 200 m.
- MassDOT repeating flood sites in the area: 4; 3 have a segment within 150 m at P >= 0.5 (share of all segments at P >= 0.5: 2.6%).

## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 1.00 | (unnamed) | Leominster | 1.50 m of water at peak; over 30 cm for 23.8 h; 30 cm reached 5.4 h into the storm; worst hour 84 mm (45% of the storm); water beside the road 0.08 m above its crest (design freeboard 0.30 m; P 0.99); a culvert within 100 m is overtopped |
| 2 | 1.00 | Depot Street | Fitchburg | 1.47 m of water at peak; over 30 cm for 33.7 h; 30 cm reached 0.1 h into the storm; worst hour 31 mm (31% of the storm); water beside the road 1.08 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 2.0 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.76); a culvert within 100 m is overtopped |
| 3 | 1.00 | Water Street | Leominster | 1.50 m of water at peak; over 30 cm for 24.0 h; 30 cm reached 5.4 h into the storm; worst hour 85 mm (45% of the storm); a culvert within 100 m is overtopped |
| 4 | 1.00 | Route 12 | Leominster | 0.94 m of water at peak; over 30 cm for 8.8 h; 30 cm reached 5.7 h into the storm; worst hour 78 mm (45% of the storm); water beside the road 0.54 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 0.8 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.14); a culvert within 100 m is overtopped |
| 5 | 1.00 | Route 31 | Fitchburg | 0.66 m of water at peak; over 30 cm for 15.8 h; 30 cm reached 7.2 h into the storm; worst hour 31 mm (29% of the storm); a culvert within 100 m is overtopped |
| 6 | 1.00 | Litchfield Street | Leominster | 1.81 m of water at peak; over 30 cm for 13.1 h; 30 cm reached 5.8 h into the storm; worst hour 66 mm (43% of the storm); runoff beside / along the road at 0.5 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.18); a culvert within 100 m is overtopped |
| 7 | 1.00 | Route 117 | Leominster | 1.20 m of water at peak; over 30 cm for 9.6 h; 30 cm reached 6.0 h into the storm; worst hour 58 mm (41% of the storm); cut off from hospitals |
| 8 | 1.00 | Route 117 | Leominster | 1.20 m of water at peak; over 30 cm for 9.6 h; 30 cm reached 6.0 h into the storm; worst hour 61 mm (42% of the storm); water beside the road 0.11 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 1.6 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.51); a culvert within 100 m is overtopped |
| 9 | 1.00 | Merriam Avenue | Leominster | 0.85 m of water at peak; over 30 cm for 4.9 h; 30 cm reached 5.3 h into the storm; worst hour 84 mm (46% of the storm); water beside the road 0.66 m above its crest (design freeboard 0.30 m; P 1.00); fast water: depth x speed 0.30 m2/s (small cars unstable from 0.3); runoff beside / along the road at 1.2 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.65); road sag 0.4 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 81 mm; catchment 13.0 ha) (P 1.00) |
| 10 | 1.00 | Route 12 | Leominster | 0.69 m of water at peak; over 30 cm for 4.1 h; 30 cm reached 5.8 h into the storm; worst hour 85 mm (45% of the storm); water beside the road 0.22 m above its crest (design freeboard 0.30 m; P 1.00); a culvert within 100 m is overtopped |
| 11 | 1.00 | Route 140 | Princeton | 0.92 m of water at peak; over 30 cm for 9.5 h; 30 cm reached 6.4 h into the storm; worst hour 42 mm (30% of the storm); water beside the road 0.21 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 2.2 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.61); a culvert within 100 m is overtopped |
| 12 | 1.00 | Kingman Drive | Leominster | 1.29 m of water at peak; over 30 cm for 15.7 h; 30 cm reached 5.3 h into the storm; worst hour 85 mm (46% of the storm); water beside the road 0.52 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 2.5 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.83); a culvert within 100 m is overtopped |
| 13 | 1.00 | Adams Street | Leominster | 1.43 m of water at peak; over 30 cm for 28.3 h; 30 cm reached 5.2 h into the storm; worst hour 87 mm (45% of the storm); water beside the road 0.49 m above its crest (design freeboard 0.30 m; P 1.00); fast water: depth x speed 0.27 m2/s (small cars unstable from 0.3); runoff beside / along the road at 0.6 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.12); a culvert within 100 m is overtopped |
| 14 | 1.00 | Depot Square | Leominster | 1.50 m of water at peak; over 30 cm for 23.8 h; 30 cm reached 5.4 h into the storm; worst hour 85 mm (45% of the storm); water beside the road 0.04 m above its crest (design freeboard 0.30 m; P 0.99); a culvert within 100 m is overtopped |
| 15 | 1.00 | Litchfield Street | Leominster | 1.03 m of water at peak; over 30 cm for 8.9 h; 30 cm reached 5.5 h into the storm; worst hour 73 mm (45% of the storm); water beside the road 0.24 m below its crest (design freeboard 0.30 m; P 0.66); runoff beside / along the road at 0.9 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.43) |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
