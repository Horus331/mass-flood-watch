# Road-closure prototype: sep2023_loss_pm_cs

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on CPU (OpenMP)), 20 m grid, storm from 2023-09-11T16:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 4,542 |
| Expected closures (sum of probabilities) | 152.0 |
| Segments with closure probability >= 50% | 116 (77.2 km) |
| Further segments that may close (stream reaches the road crest) | 246 (155.2 km) |
| Culverts overtopped / surcharged | 100 / 23 of 616 |
| Road segments cut off from hospitals | 650 |
| Worst added trip time to a hospital | 25.7 min |
| Heaviest hour of rain | 89.3 mm |
| Flood model run time | 2656 s |

## Checks against what happened

- Storm-day flood reports in the area: 10; water >= 10 cm within 100 m of 100% of them, vs 77% of random points (any day).
- Segments flagged impassable are 2.95x as likely as an average segment to have a report within 200 m.
- MassDOT repeating flood sites in the area: 4; 2 have a segment within 150 m at P >= 0.5 (share of all segments at P >= 0.5: 2.6%).

## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 1.00 | Route 12 | Fitchburg | 0.64 m of water at peak; over 30 cm for 30.0 h; 30 cm reached 6.5 h into the storm; worst hour 52 mm (51% of the storm); water beside the road 0.61 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 0.8 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.31); a culvert within 100 m is overtopped |
| 2 | 1.00 | (unnamed) | Fitchburg | 0.68 m of water at peak; over 30 cm for 23.0 h; 30 cm reached 6.5 h into the storm; worst hour 29 mm (34% of the storm); water beside the road 0.73 m above its crest (design freeboard 0.30 m; P 1.00); fast water: depth x speed 0.48 m2/s (small cars unstable from 0.3); runoff beside / along the road at 0.9 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.38) |
| 3 | 1.00 | Litchfield Street | Leominster | 5.49 m of water at peak; over 30 cm for 35.5 h; 30 cm reached 1.0 h into the storm; worst hour 66 mm (43% of the storm); water beside the road 2.15 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 1.9 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.53); road sag 2.2 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 65 mm; catchment 85.6 ha) (P 1.00); a culvert within 100 m is overtopped |
| 4 | 1.00 | Depot Street | Fitchburg | 1.51 m of water at peak; over 30 cm for 32.5 h; 30 cm reached 0.5 h into the storm; worst hour 31 mm (31% of the storm); water beside the road 1.08 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 2.0 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.76); a culvert within 100 m is overtopped |
| 5 | 1.00 | West Main Street | Westminster | 0.67 m of water at peak; over 30 cm for 34.0 h; 30 cm reached 2.5 h into the storm; worst hour 30 mm (29% of the storm); a culvert within 100 m is overtopped |
| 6 | 1.00 | Route 12 | Leominster | 0.92 m of water at peak; over 30 cm for 8.5 h; 30 cm reached 6.0 h into the storm; worst hour 78 mm (45% of the storm); water beside the road 0.52 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 0.8 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.29); a culvert within 100 m is overtopped |
| 7 | 1.00 | Route 12 | Leominster | 1.04 m of water at peak; over 30 cm for 6.5 h; 30 cm reached 7.0 h into the storm; worst hour 85 mm (45% of the storm); water beside the road 0.22 m above its crest (design freeboard 0.30 m; P 1.00); a culvert within 100 m is overtopped |
| 8 | 1.00 | Merriam Avenue | Leominster | 0.85 m of water at peak; over 30 cm for 5.0 h; 30 cm reached 5.5 h into the storm; worst hour 84 mm (46% of the storm); water beside the road 0.66 m above its crest (design freeboard 0.30 m; P 1.00); fast water: depth x speed 0.29 m2/s (small cars unstable from 0.3); runoff beside / along the road at 1.2 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.65); road sag 0.4 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 81 mm; catchment 13.0 ha) (P 1.00) |
| 9 | 1.00 | Route 140 | Princeton | 0.95 m of water at peak; over 30 cm for 9.5 h; 30 cm reached 6.5 h into the storm; worst hour 42 mm (30% of the storm); water beside the road 0.21 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 2.2 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.60); a culvert within 100 m is overtopped |
| 10 | 1.00 | Kingman Drive | Leominster | 1.30 m of water at peak; over 30 cm for 16.0 h; 30 cm reached 5.5 h into the storm; worst hour 85 mm (46% of the storm); water beside the road 0.54 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 2.5 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.88); a culvert within 100 m is overtopped |
| 11 | 1.00 | Litchfield Street | Leominster | 1.35 m of water at peak; over 30 cm for 11.5 h; 30 cm reached 5.5 h into the storm; worst hour 73 mm (45% of the storm); water beside the road 0.24 m below its crest (design freeboard 0.30 m; P 0.66) |
| 12 | 1.00 | Meadowbrook Acres | Leominster | 3.49 m of water at peak; over 30 cm for 29.5 h; 30 cm reached 7.0 h into the storm; worst hour 73 mm (44% of the storm); water beside the road 3.45 m above its crest (design freeboard 0.30 m; P 1.00) |
| 13 | 1.00 | Meadowbrook Acres | Leominster | 3.31 m of water at peak; over 30 cm for 29.5 h; 30 cm reached 7.0 h into the storm; worst hour 73 mm (44% of the storm); water beside the road 3.15 m above its crest (design freeboard 0.30 m; P 1.00) |
| 14 | 1.00 | Meadowbrook Acres | Leominster | 3.22 m of water at peak; over 30 cm for 29.5 h; 30 cm reached 7.0 h into the storm; worst hour 72 mm (44% of the storm); water beside the road 3.09 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.5 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 71 mm; catchment 85.6 ha) (P 1.00) |
| 15 | 1.00 | Meadowbrook Acres | Leominster | 3.13 m of water at peak; over 30 cm for 29.5 h; 30 cm reached 7.0 h into the storm; worst hour 71 mm (44% of the storm); water beside the road 2.97 m above its crest (design freeboard 0.30 m; P 1.00); fast water: depth x speed 0.31 m2/s (small cars unstable from 0.3); runoff beside / along the road at 1.0 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.47); road sag 0.6 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 70 mm; catchment 85.6 ha) (P 1.00) |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
