# Road-closure prototype: sep2023_loss_t2_c100

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on CPU (OpenMP)), 20 m grid, storm from 2023-09-11T16:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 4,542 |
| Expected closures (sum of probabilities) | 118.5 |
| Segments with closure probability >= 50% | 97 (60.7 km) |
| Further segments that may close (stream reaches the road crest) | 201 (138.1 km) |
| Culverts overtopped / surcharged | 54 / 32 of 616 |
| Road segments cut off from hospitals | 400 |
| Worst added trip time to a hospital | 20.6 min |
| Heaviest hour of rain | 89.3 mm |
| Flood model run time | 2814 s |

## Checks against what happened

- Storm-day flood reports in the area: 10; water >= 10 cm within 100 m of 90% of them, vs 69% of random points (any day).
- Segments flagged impassable are 2.65x as likely as an average segment to have a report within 200 m.
- MassDOT repeating flood sites in the area: 4; 2 have a segment within 150 m at P >= 0.5 (share of all segments at P >= 0.5: 2.1%).

## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 1.00 | Route 12 | Fitchburg | 0.68 m of water at peak; over 30 cm for 29.5 h; 30 cm reached 7.0 h into the storm; worst hour 52 mm (51% of the storm); water beside the road 0.59 m above its crest (design freeboard 0.30 m; P 1.00); a culvert within 100 m is overtopped |
| 2 | 1.00 | (unnamed) | Fitchburg | 0.83 m of water at peak; over 30 cm for 26.5 h; 30 cm reached 5.0 h into the storm; worst hour 29 mm (34% of the storm); water beside the road 0.86 m above its crest (design freeboard 0.30 m; P 1.00); fast water: depth x speed 0.66 m2/s (small cars unstable from 0.3); runoff beside / along the road at 1.0 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.50) |
| 3 | 1.00 | Boulder Drive | Fitchburg | 0.73 m of water at peak; over 30 cm for 24.0 h; 30 cm reached 5.5 h into the storm; worst hour 29 mm (33% of the storm); water beside the road 0.80 m above its crest (design freeboard 0.30 m; P 1.00); fast water: depth x speed 0.66 m2/s (small cars unstable from 0.3); runoff beside / along the road at 1.0 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.50) |
| 4 | 1.00 | Route 12 | Leominster | 0.81 m of water at peak; over 30 cm for 30.0 h; 30 cm reached 6.5 h into the storm; worst hour 61 mm (42% of the storm); water beside the road 1.37 m above its crest (design freeboard 0.30 m; P 1.00); overtopping at 1.4 m/s at a stream crossing (grass-covered fill erodes from ~1.5 m/s); runoff beside / along the road at 1.2 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.67); culvert (Tributary to Fall Brook): headwater 2.38 m vs road crest 1.98 m, 3.2 m3/s |
| 5 | 1.00 | Litchfield Street | Leominster | 4.78 m of water at peak; over 30 cm for 35.5 h; 30 cm reached 1.0 h into the storm; worst hour 66 mm (43% of the storm); water beside the road 1.44 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 1.9 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.24); road sag 2.2 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 65 mm; catchment 85.6 ha) (P 1.00); a culvert within 100 m is overtopped |
| 6 | 1.00 | Depot Street | Fitchburg | 1.05 m of water at peak; over 30 cm for 26.5 h; 30 cm reached 0.5 h into the storm; worst hour 31 mm (31% of the storm); runoff beside / along the road at 1.6 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.73); a culvert within 100 m is overtopped |
| 7 | 1.00 | West Main Street | Westminster | 1.90 m of water at peak; over 30 cm for 34.0 h; 30 cm reached 2.5 h into the storm; worst hour 30 mm (29% of the storm); water beside the road 0.09 m above its crest (design freeboard 0.30 m; P 0.99); runoff beside / along the road at 0.6 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.19); a culvert within 100 m is overtopped |
| 8 | 1.00 | Route 12 | Leominster | 0.76 m of water at peak; over 30 cm for 9.5 h; 30 cm reached 6.5 h into the storm; worst hour 78 mm (45% of the storm); water beside the road 0.30 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 0.6 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.11); a culvert within 100 m is overtopped |
| 9 | 1.00 | Litchfield Street | Leominster | 0.80 m of water at peak; over 30 cm for 29.5 h; 30 cm reached 6.0 h into the storm; worst hour 73 mm (45% of the storm); water beside the road 1.06 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 1.6 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.84); a culvert within 100 m is overtopped |
| 10 | 1.00 | Merriam Avenue | Leominster | 0.72 m of water at peak; over 30 cm for 4.5 h; 30 cm reached 5.5 h into the storm; worst hour 84 mm (46% of the storm); water beside the road 0.53 m above its crest (design freeboard 0.30 m; P 1.00); fast water: depth x speed 0.22 m2/s (small cars unstable from 0.3); runoff beside / along the road at 1.1 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.61); road sag 0.4 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 81 mm; catchment 13.0 ha) (P 1.00) |
| 11 | 1.00 | Route 140 | Princeton | 0.74 m of water at peak; over 30 cm for 8.0 h; 30 cm reached 7.5 h into the storm; worst hour 42 mm (30% of the storm); water beside the road 0.20 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 1.4 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.47); a culvert within 100 m is overtopped |
| 12 | 1.00 | Kingman Drive | Leominster | 1.07 m of water at peak; over 30 cm for 12.5 h; 30 cm reached 6.0 h into the storm; worst hour 85 mm (46% of the storm); water beside the road 0.44 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 1.7 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.87); a culvert within 100 m is overtopped |
| 13 | 1.00 | Columbia Avenue | Fitchburg | 1.58 m of water at peak; over 30 cm for 30.5 h; 30 cm reached 6.0 h into the storm; worst hour 50 mm (50% of the storm); water beside the road 1.47 m above its crest (design freeboard 0.30 m; P 1.00); fast water: depth x speed 0.26 m2/s (small cars unstable from 0.3); runoff beside / along the road at 0.6 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.15); road sag 0.7 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 49 mm; catchment 6.8 ha) (P 1.00); a culvert within 100 m is overtopped |
| 14 | 1.00 | Marguerite Avenue | Leominster | 1.41 m of water at peak; over 30 cm for 30.5 h; 30 cm reached 6.0 h into the storm; worst hour 80 mm (45% of the storm); water beside the road 0.06 m above its crest (design freeboard 0.30 m; P 0.99); runoff beside / along the road at 0.9 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.34); a culvert within 100 m is overtopped |
| 15 | 1.00 | Dewey Street | Fitchburg | 2.24 m of water at peak; over 30 cm for 29.5 h; 30 cm reached 7.0 h into the storm; worst hour 51 mm (50% of the storm); water beside the road 0.18 m above its crest (design freeboard 0.30 m; P 1.00); a culvert within 100 m is overtopped |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
