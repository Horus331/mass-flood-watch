# Road-closure prototype: sep2023_loss_C50W

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on CPU (OpenMP)), 20 m grid, storm from 2023-09-11T16:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 4,542 |
| Expected closures (sum of probabilities) | 148.6 |
| Segments with closure probability >= 50% | 114 (73.7 km) |
| Further segments that may close (stream reaches the road crest) | 246 (156.8 km) |
| Culverts overtopped / surcharged | 79 / 20 of 616 |
| Road segments cut off from hospitals | 596 |
| Worst added trip time to a hospital | 25.7 min |
| Heaviest hour of rain | 89.3 mm |
| Flood model run time | 3294 s |

## Checks against what happened

- Storm-day flood reports in the area: 10; water >= 10 cm within 100 m of 100% of them, vs 76% of random points (any day).
- Segments flagged impassable are 2.92x as likely as an average segment to have a report within 200 m.
- MassDOT repeating flood sites in the area: 4; 2 have a segment within 150 m at P >= 0.5 (share of all segments at P >= 0.5: 2.5%).

## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 1.00 | Route 12 | Fitchburg | 0.64 m of water at peak; over 30 cm for 30.2 h; 30 cm reached 5.9 h into the storm; worst hour 52 mm (51% of the storm); water beside the road 0.61 m above its crest (design freeboard 0.30 m; P 1.00); a culvert within 100 m is overtopped |
| 2 | 1.00 | (unnamed) | Fitchburg | 0.74 m of water at peak; over 30 cm for 23.3 h; 30 cm reached 6.1 h into the storm; worst hour 29 mm (34% of the storm); water beside the road 0.78 m above its crest (design freeboard 0.30 m; P 1.00); fast water: depth x speed 0.55 m2/s (small cars unstable from 0.3); runoff beside / along the road at 0.9 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.43) |
| 3 | 1.00 | Boulder Drive | Fitchburg | 0.66 m of water at peak; over 30 cm for 20.8 h; 30 cm reached 6.2 h into the storm; worst hour 29 mm (33% of the storm); water beside the road 0.74 m above its crest (design freeboard 0.30 m; P 1.00); fast water: depth x speed 0.55 m2/s (small cars unstable from 0.3); runoff beside / along the road at 0.9 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.43) |
| 4 | 1.00 | Litchfield Street | Leominster | 5.04 m of water at peak; over 30 cm for 35.4 h; 30 cm reached 0.7 h into the storm; worst hour 66 mm (43% of the storm); water beside the road 2.15 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 1.9 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.56); road sag 2.2 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 65 mm; catchment 85.6 ha) (P 1.00); a culvert within 100 m is overtopped |
| 5 | 1.00 | Depot Street | Fitchburg | 1.38 m of water at peak; over 30 cm for 32.8 h; 30 cm reached 0.1 h into the storm; worst hour 31 mm (31% of the storm); water beside the road 1.08 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 2.0 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.76); a culvert within 100 m is overtopped |
| 6 | 1.00 | Route 31 | Fitchburg | 0.65 m of water at peak; over 30 cm for 16.0 h; 30 cm reached 7.2 h into the storm; worst hour 31 mm (29% of the storm); a culvert within 100 m is overtopped |
| 7 | 1.00 | Route 12 | Leominster | 0.82 m of water at peak; over 30 cm for 8.3 h; 30 cm reached 5.7 h into the storm; worst hour 78 mm (45% of the storm); water beside the road 0.51 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 0.9 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.38); a culvert within 100 m is overtopped |
| 8 | 1.00 | Route 12 | Leominster | 0.83 m of water at peak; over 30 cm for 6.6 h; 30 cm reached 6.7 h into the storm; worst hour 85 mm (45% of the storm); water beside the road 0.21 m above its crest (design freeboard 0.30 m; P 1.00); a culvert within 100 m is overtopped |
| 9 | 1.00 | Merriam Avenue | Leominster | 0.85 m of water at peak; over 30 cm for 4.9 h; 30 cm reached 5.3 h into the storm; worst hour 84 mm (46% of the storm); water beside the road 0.66 m above its crest (design freeboard 0.30 m; P 1.00); fast water: depth x speed 0.30 m2/s (small cars unstable from 0.3); runoff beside / along the road at 1.2 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.65); road sag 0.4 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 81 mm; catchment 13.0 ha) (P 1.00) |
| 10 | 1.00 | Route 140 | Princeton | 0.91 m of water at peak; over 30 cm for 9.5 h; 30 cm reached 6.4 h into the storm; worst hour 42 mm (30% of the storm); water beside the road 0.21 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 2.2 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.61); a culvert within 100 m is overtopped |
| 11 | 1.00 | Kingman Drive | Leominster | 1.28 m of water at peak; over 30 cm for 15.7 h; 30 cm reached 5.3 h into the storm; worst hour 85 mm (46% of the storm); water beside the road 0.52 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 2.5 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.83); a culvert within 100 m is overtopped |
| 12 | 1.00 | Marguerite Avenue | Leominster | 1.96 m of water at peak; over 30 cm for 30.8 h; 30 cm reached 5.2 h into the storm; worst hour 80 mm (45% of the storm); water beside the road 0.26 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 2.0 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.84); road sag 1.4 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 78 mm; catchment 85.6 ha) (P 1.00); a culvert within 100 m is overtopped |
| 13 | 1.00 | Dewey Street | Fitchburg | 1.19 m of water at peak; over 30 cm for 29.9 h; 30 cm reached 6.2 h into the storm; worst hour 51 mm (50% of the storm); a culvert within 100 m is overtopped |
| 14 | 1.00 | Meadowbrook Acres | Leominster | 3.12 m of water at peak; over 30 cm for 29.5 h; 30 cm reached 6.6 h into the storm; worst hour 71 mm (44% of the storm); water beside the road 2.96 m above its crest (design freeboard 0.30 m; P 1.00); fast water: depth x speed 0.36 m2/s (small cars unstable from 0.3); runoff beside / along the road at 0.9 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.38); road sag 0.6 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 70 mm; catchment 85.6 ha) (P 1.00) |
| 15 | 1.00 | Meadowbrook Acres | Leominster | 3.49 m of water at peak; over 30 cm for 29.4 h; 30 cm reached 6.7 h into the storm; worst hour 73 mm (44% of the storm); water beside the road 3.45 m above its crest (design freeboard 0.30 m; P 1.00) |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
