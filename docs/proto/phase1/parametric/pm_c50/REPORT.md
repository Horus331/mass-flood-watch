# Road-closure prototype: sep2023_loss_pm_c50

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on CPU (OpenMP)), 20 m grid, storm from 2023-09-11T16:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 4,542 |
| Expected closures (sum of probabilities) | 108.4 |
| Segments with closure probability >= 50% | 84 (56.7 km) |
| Further segments that may close (stream reaches the road crest) | 152 (99.2 km) |
| Culverts overtopped / surcharged | 67 / 22 of 616 |
| Road segments cut off from hospitals | 468 |
| Worst added trip time to a hospital | 23.5 min |
| Heaviest hour of rain | 89.3 mm |
| Flood model run time | 2535 s |

## Checks against what happened

- Storm-day flood reports in the area: 10; water >= 10 cm within 100 m of 90% of them, vs 69% of random points (any day).
- Segments flagged impassable are 3.5x as likely as an average segment to have a report within 200 m.
- MassDOT repeating flood sites in the area: 4; 2 have a segment within 150 m at P >= 0.5 (share of all segments at P >= 0.5: 1.8%).

## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 1.00 | Litchfield Street | Leominster | 5.15 m of water at peak; over 30 cm for 35.5 h; 30 cm reached 1.0 h into the storm; worst hour 66 mm (43% of the storm); water beside the road 1.81 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 1.3 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.36); road sag 2.2 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 65 mm; catchment 85.6 ha) (P 1.00); a culvert within 100 m is overtopped |
| 2 | 1.00 | Depot Street | Fitchburg | 1.03 m of water at peak; over 30 cm for 32.5 h; 30 cm reached 0.5 h into the storm; worst hour 31 mm (31% of the storm); runoff beside / along the road at 1.6 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.73); a culvert within 100 m is overtopped |
| 3 | 1.00 | Route 12 | Leominster | 0.80 m of water at peak; over 30 cm for 8.0 h; 30 cm reached 6.0 h into the storm; worst hour 78 mm (45% of the storm); water beside the road 0.11 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 0.7 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.14); a culvert within 100 m is overtopped |
| 4 | 1.00 | Route 12 | Leominster | 0.73 m of water at peak; over 30 cm for 5.5 h; 30 cm reached 7.5 h into the storm; worst hour 85 mm (45% of the storm); a culvert within 100 m is overtopped |
| 5 | 1.00 | Merriam Avenue | Leominster | 0.72 m of water at peak; over 30 cm for 4.5 h; 30 cm reached 5.5 h into the storm; worst hour 84 mm (46% of the storm); water beside the road 0.53 m above its crest (design freeboard 0.30 m; P 1.00); fast water: depth x speed 0.22 m2/s (small cars unstable from 0.3); runoff beside / along the road at 1.1 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.61); road sag 0.4 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 81 mm; catchment 13.0 ha) (P 1.00) |
| 6 | 1.00 | Route 140 | Princeton | 0.76 m of water at peak; over 30 cm for 8.0 h; 30 cm reached 7.5 h into the storm; worst hour 42 mm (30% of the storm); water beside the road 0.20 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 1.4 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.48); a culvert within 100 m is overtopped |
| 7 | 1.00 | Kingman Drive | Leominster | 1.14 m of water at peak; over 30 cm for 13.0 h; 30 cm reached 5.5 h into the storm; worst hour 85 mm (46% of the storm); water beside the road 0.49 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 1.7 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.83); a culvert within 100 m is overtopped |
| 8 | 1.00 | Litchfield Street | Leominster | 1.20 m of water at peak; over 30 cm for 11.0 h; 30 cm reached 6.0 h into the storm; worst hour 73 mm (45% of the storm); water beside the road 0.41 m below its crest (design freeboard 0.30 m; P 0.24) |
| 9 | 1.00 | Meadowbrook Acres | Leominster | 2.79 m of water at peak; over 30 cm for 29.5 h; 30 cm reached 7.0 h into the storm; worst hour 71 mm (44% of the storm); water beside the road 2.63 m above its crest (design freeboard 0.30 m; P 1.00); fast water: depth x speed 0.24 m2/s (small cars unstable from 0.3); runoff beside / along the road at 0.9 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.40); road sag 0.6 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 70 mm; catchment 85.6 ha) (P 1.00) |
| 10 | 1.00 | Meadowbrook Acres | Leominster | 3.15 m of water at peak; over 30 cm for 29.0 h; 30 cm reached 7.5 h into the storm; worst hour 73 mm (44% of the storm); water beside the road 3.11 m above its crest (design freeboard 0.30 m; P 1.00) |
| 11 | 1.00 | Meadowbrook Acres | Leominster | 2.98 m of water at peak; over 30 cm for 29.0 h; 30 cm reached 7.5 h into the storm; worst hour 73 mm (44% of the storm); water beside the road 2.81 m above its crest (design freeboard 0.30 m; P 1.00) |
| 12 | 1.00 | Meadowbrook Acres | Leominster | 2.88 m of water at peak; over 30 cm for 29.0 h; 30 cm reached 7.5 h into the storm; worst hour 72 mm (44% of the storm); water beside the road 2.75 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.5 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 71 mm; catchment 85.6 ha) (P 1.00) |
| 13 | 1.00 | Meadowbrook Acres | Leominster | 2.70 m of water at peak; over 30 cm for 28.5 h; 30 cm reached 8.0 h into the storm; worst hour 73 mm (44% of the storm); water beside the road 2.55 m above its crest (design freeboard 0.30 m; P 1.00) |
| 14 | 1.00 | Meadowbrook Acres | Leominster | 2.51 m of water at peak; over 30 cm for 28.5 h; 30 cm reached 8.0 h into the storm; worst hour 72 mm (44% of the storm); water beside the road 2.44 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 0.6 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.17); road sag 0.6 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 70 mm; catchment 85.6 ha) (P 1.00) |
| 15 | 1.00 | Meadowbrook Acres | Leominster | 2.23 m of water at peak; over 30 cm for 28.0 h; 30 cm reached 8.5 h into the storm; worst hour 73 mm (44% of the storm); water beside the road 2.12 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 0.7 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.26) |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
