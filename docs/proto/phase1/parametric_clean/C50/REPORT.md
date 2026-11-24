# Road-closure prototype: sep2023_loss_C50

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on CPU (OpenMP)), 20 m grid, storm from 2023-09-11T16:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 4,542 |
| Expected closures (sum of probabilities) | 103.1 |
| Segments with closure probability >= 50% | 79 (51.1 km) |
| Further segments that may close (stream reaches the road crest) | 152 (96.7 km) |
| Culverts overtopped / surcharged | 61 / 18 of 616 |
| Road segments cut off from hospitals | 449 |
| Worst added trip time to a hospital | 23.3 min |
| Heaviest hour of rain | 89.3 mm |
| Flood model run time | 2781 s |

## Checks against what happened

- Storm-day flood reports in the area: 10; water >= 10 cm within 100 m of 90% of them, vs 68% of random points (any day).
- Segments flagged impassable are 3.31x as likely as an average segment to have a report within 200 m.
- MassDOT repeating flood sites in the area: 4; 2 have a segment within 150 m at P >= 0.5 (share of all segments at P >= 0.5: 1.7%).

## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 1.00 | Litchfield Street | Leominster | 4.70 m of water at peak; over 30 cm for 35.4 h; 30 cm reached 0.7 h into the storm; worst hour 66 mm (43% of the storm); water beside the road 1.81 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 1.5 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.54); road sag 2.2 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 65 mm; catchment 85.6 ha) (P 1.00); a culvert within 100 m is overtopped |
| 2 | 1.00 | Depot Street | Fitchburg | 0.84 m of water at peak; over 30 cm for 32.8 h; 30 cm reached 0.1 h into the storm; worst hour 31 mm (31% of the storm); runoff beside / along the road at 1.6 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.73); a culvert within 100 m is overtopped |
| 3 | 1.00 | Route 12 | Leominster | 0.70 m of water at peak; over 30 cm for 8.0 h; 30 cm reached 5.8 h into the storm; worst hour 78 mm (45% of the storm); water beside the road 0.10 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 0.7 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.14); a culvert within 100 m is overtopped |
| 4 | 1.00 | Merriam Avenue | Leominster | 0.72 m of water at peak; over 30 cm for 4.4 h; 30 cm reached 5.5 h into the storm; worst hour 84 mm (46% of the storm); water beside the road 0.53 m above its crest (design freeboard 0.30 m; P 1.00); fast water: depth x speed 0.22 m2/s (small cars unstable from 0.3); runoff beside / along the road at 1.1 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.61); road sag 0.4 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 81 mm; catchment 13.0 ha) (P 1.00) |
| 5 | 1.00 | Route 140 | Princeton | 0.71 m of water at peak; over 30 cm for 8.3 h; 30 cm reached 7.0 h into the storm; worst hour 42 mm (30% of the storm); water beside the road 0.20 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 1.4 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.51); a culvert within 100 m is overtopped |
| 6 | 1.00 | Kingman Drive | Leominster | 1.12 m of water at peak; over 30 cm for 12.6 h; 30 cm reached 5.5 h into the storm; worst hour 85 mm (46% of the storm); water beside the road 0.47 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 1.5 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.78); a culvert within 100 m is overtopped |
| 7 | 1.00 | Marguerite Avenue | Leominster | 1.64 m of water at peak; over 30 cm for 30.6 h; 30 cm reached 5.5 h into the storm; worst hour 80 mm (45% of the storm); water beside the road 0.10 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 1.7 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.74); road sag 1.4 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 78 mm; catchment 85.6 ha) (P 0.57); a culvert within 100 m is overtopped |
| 8 | 1.00 | Dewey Street | Fitchburg | 1.15 m of water at peak; over 30 cm for 29.7 h; 30 cm reached 6.4 h into the storm; worst hour 51 mm (50% of the storm); a culvert within 100 m is overtopped |
| 9 | 1.00 | Meadowbrook Acres | Leominster | 2.78 m of water at peak; over 30 cm for 29.3 h; 30 cm reached 6.8 h into the storm; worst hour 71 mm (44% of the storm); water beside the road 2.62 m above its crest (design freeboard 0.30 m; P 1.00); fast water: depth x speed 0.25 m2/s (small cars unstable from 0.3); runoff beside / along the road at 0.8 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.29); road sag 0.6 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 70 mm; catchment 85.6 ha) (P 1.00) |
| 10 | 1.00 | Meadowbrook Acres | Leominster | 3.15 m of water at peak; over 30 cm for 28.9 h; 30 cm reached 7.2 h into the storm; worst hour 73 mm (44% of the storm); water beside the road 3.11 m above its crest (design freeboard 0.30 m; P 1.00) |
| 11 | 1.00 | Meadowbrook Acres | Leominster | 2.97 m of water at peak; over 30 cm for 28.8 h; 30 cm reached 7.3 h into the storm; worst hour 73 mm (44% of the storm); water beside the road 2.81 m above its crest (design freeboard 0.30 m; P 1.00) |
| 12 | 1.00 | Meadowbrook Acres | Leominster | 2.87 m of water at peak; over 30 cm for 28.7 h; 30 cm reached 7.4 h into the storm; worst hour 72 mm (44% of the storm); water beside the road 2.75 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.5 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 71 mm; catchment 85.6 ha) (P 1.00) |
| 13 | 1.00 | Meadowbrook Acres | Leominster | 2.69 m of water at peak; over 30 cm for 28.6 h; 30 cm reached 7.5 h into the storm; worst hour 73 mm (44% of the storm); water beside the road 2.55 m above its crest (design freeboard 0.30 m; P 1.00) |
| 14 | 1.00 | Meadowbrook Acres | Leominster | 2.50 m of water at peak; over 30 cm for 28.3 h; 30 cm reached 7.8 h into the storm; worst hour 72 mm (44% of the storm); water beside the road 2.44 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 0.6 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.17); road sag 0.6 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 70 mm; catchment 85.6 ha) (P 1.00) |
| 15 | 1.00 | Meadowbrook Acres | Leominster | 2.22 m of water at peak; over 30 cm for 27.8 h; 30 cm reached 8.2 h into the storm; worst hour 73 mm (44% of the storm); water beside the road 2.12 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 0.7 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.26) |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
