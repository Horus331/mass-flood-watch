# Road-closure prototype: sep2023_loss_pm_c100

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on CPU (OpenMP)), 20 m grid, storm from 2023-09-11T16:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 4,542 |
| Expected closures (sum of probabilities) | 114.0 |
| Segments with closure probability >= 50% | 93 (56.8 km) |
| Further segments that may close (stream reaches the road crest) | 205 (143.2 km) |
| Culverts overtopped / surcharged | 55 / 33 of 616 |
| Road segments cut off from hospitals | 400 |
| Worst added trip time to a hospital | 20.6 min |
| Heaviest hour of rain | 89.3 mm |
| Flood model run time | 3117 s |

## Checks against what happened

- Storm-day flood reports in the area: 10; water >= 10 cm within 100 m of 90% of them, vs 69% of random points (any day).
- Segments flagged impassable are 2.64x as likely as an average segment to have a report within 200 m.
- MassDOT repeating flood sites in the area: 4; 2 have a segment within 150 m at P >= 0.5 (share of all segments at P >= 0.5: 2.0%).

## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 1.00 | (unnamed) | Fitchburg | 0.78 m of water at peak; over 30 cm for 25.0 h; 30 cm reached 5.5 h into the storm; worst hour 29 mm (34% of the storm); water beside the road 0.81 m above its crest (design freeboard 0.30 m; P 1.00); fast water: depth x speed 0.60 m2/s (small cars unstable from 0.3); runoff beside / along the road at 1.0 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.46) |
| 2 | 1.00 | Boulder Drive | Fitchburg | 0.69 m of water at peak; over 30 cm for 21.0 h; 30 cm reached 6.0 h into the storm; worst hour 29 mm (33% of the storm); water beside the road 0.76 m above its crest (design freeboard 0.30 m; P 1.00); fast water: depth x speed 0.60 m2/s (small cars unstable from 0.3); runoff beside / along the road at 1.0 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.46) |
| 3 | 1.00 | Route 12 | Leominster | 0.81 m of water at peak; over 30 cm for 30.0 h; 30 cm reached 6.5 h into the storm; worst hour 61 mm (42% of the storm); water beside the road 1.37 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 0.8 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.27); culvert (Tributary to Fall Brook): headwater 2.55 m vs road crest 1.98 m, 3.4 m3/s |
| 4 | 1.00 | Litchfield Street | Leominster | 4.78 m of water at peak; over 30 cm for 35.5 h; 30 cm reached 1.0 h into the storm; worst hour 66 mm (43% of the storm); water beside the road 1.44 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 1.9 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.26); road sag 2.2 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 65 mm; catchment 85.6 ha) (P 1.00); a culvert within 100 m is overtopped |
| 5 | 1.00 | Depot Street | Fitchburg | 0.97 m of water at peak; over 30 cm for 26.0 h; 30 cm reached 0.5 h into the storm; worst hour 31 mm (31% of the storm); runoff beside / along the road at 1.6 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.73); a culvert within 100 m is overtopped |
| 6 | 1.00 | West Main Street | Westminster | 1.90 m of water at peak; over 30 cm for 34.0 h; 30 cm reached 2.5 h into the storm; worst hour 30 mm (29% of the storm); water beside the road 0.08 m above its crest (design freeboard 0.30 m; P 0.99); runoff beside / along the road at 0.6 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.19); a culvert within 100 m is overtopped |
| 7 | 1.00 | Route 12 | Leominster | 0.76 m of water at peak; over 30 cm for 9.5 h; 30 cm reached 6.5 h into the storm; worst hour 78 mm (45% of the storm); water beside the road 0.30 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 0.6 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.11); a culvert within 100 m is overtopped |
| 8 | 1.00 | Litchfield Street | Leominster | 1.14 m of water at peak; over 30 cm for 29.5 h; 30 cm reached 6.0 h into the storm; worst hour 73 mm (45% of the storm); water beside the road 1.06 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 1.6 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.84); a culvert within 100 m is overtopped |
| 9 | 1.00 | Merriam Avenue | Leominster | 0.72 m of water at peak; over 30 cm for 4.5 h; 30 cm reached 5.5 h into the storm; worst hour 84 mm (46% of the storm); water beside the road 0.53 m above its crest (design freeboard 0.30 m; P 1.00); fast water: depth x speed 0.22 m2/s (small cars unstable from 0.3); runoff beside / along the road at 1.1 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.61); road sag 0.4 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 81 mm; catchment 13.0 ha) (P 1.00) |
| 10 | 1.00 | Route 140 | Princeton | 0.73 m of water at peak; over 30 cm for 8.0 h; 30 cm reached 7.5 h into the storm; worst hour 42 mm (30% of the storm); water beside the road 0.20 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 1.4 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.43); a culvert within 100 m is overtopped |
| 11 | 1.00 | Kingman Drive | Leominster | 1.06 m of water at peak; over 30 cm for 12.5 h; 30 cm reached 6.0 h into the storm; worst hour 85 mm (46% of the storm); water beside the road 0.45 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 1.7 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.79); a culvert within 100 m is overtopped |
| 12 | 1.00 | Columbia Avenue | Fitchburg | 1.58 m of water at peak; over 30 cm for 30.0 h; 30 cm reached 6.5 h into the storm; worst hour 50 mm (50% of the storm); water beside the road 1.47 m above its crest (design freeboard 0.30 m; P 1.00); fast water: depth x speed 0.24 m2/s (small cars unstable from 0.3); runoff beside / along the road at 0.8 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.27); road sag 0.7 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 49 mm; catchment 6.8 ha) (P 1.00); a culvert within 100 m is overtopped |
| 13 | 1.00 | Commercial Road | Leominster | 0.83 m of water at peak; over 30 cm for 29.0 h; 30 cm reached 7.5 h into the storm; worst hour 77 mm (44% of the storm); water beside the road 0.67 m above its crest (design freeboard 0.30 m; P 1.00); fast water: depth x speed 0.28 m2/s (small cars unstable from 0.3); runoff beside / along the road at 0.8 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.36); a culvert within 100 m is overtopped |
| 14 | 1.00 | Sack Boulevard | Leominster | 1.20 m of water at peak; over 30 cm for 29.5 h; 30 cm reached 7.0 h into the storm; worst hour 71 mm (43% of the storm); water beside the road 0.96 m above its crest (design freeboard 0.30 m; P 1.00); fast water: depth x speed 0.36 m2/s (small cars unstable from 0.3) |
| 15 | 1.00 | Meadowbrook Acres | Leominster | 2.42 m of water at peak; over 30 cm for 29.0 h; 30 cm reached 7.5 h into the storm; worst hour 71 mm (44% of the storm); water beside the road 2.26 m above its crest (design freeboard 0.30 m; P 1.00); fast water: depth x speed 0.22 m2/s (small cars unstable from 0.3); runoff beside / along the road at 0.8 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.36); road sag 0.6 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 70 mm; catchment 85.6 ha) (P 1.00) |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
