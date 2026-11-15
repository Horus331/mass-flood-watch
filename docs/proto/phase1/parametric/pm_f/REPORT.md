# Road-closure prototype: sep2023_loss_pm_f

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on CPU (OpenMP)), 20 m grid, storm from 2023-09-11T16:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 4,542 |
| Expected closures (sum of probabilities) | 256.8 |
| Segments with closure probability >= 50% | 224 (147.8 km) |
| Further segments that may close (stream reaches the road crest) | 341 (216.1 km) |
| Culverts overtopped / surcharged | 190 / 9 of 616 |
| Road segments cut off from hospitals | 1317 |
| Worst added trip time to a hospital | 30.7 min |
| Heaviest hour of rain | 89.3 mm |
| Flood model run time | 2815 s |

## Checks against what happened

- Storm-day flood reports in the area: 10; water >= 10 cm within 100 m of 100% of them, vs 81% of random points (any day).
- Segments flagged impassable are 2.29x as likely as an average segment to have a report within 200 m.
- MassDOT repeating flood sites in the area: 4; 3 have a segment within 150 m at P >= 0.5 (share of all segments at P >= 0.5: 4.9%).

## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 1.00 | Route 2 | Leominster | 11.82 m of water at peak; over 30 cm for 31.0 h; 30 cm reached 5.5 h into the storm; worst hour 67 mm (42% of the storm); runoff beside / along the road at 2.3 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.86); a culvert within 100 m is overtopped |
| 2 | 1.00 | Route 2 | Fitchburg | 0.79 m of water at peak; over 30 cm for 25.5 h; 30 cm reached 6.0 h into the storm; worst hour 38 mm (33% of the storm); runoff beside / along the road at 1.7 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.68); culvert (Wyman): headwater 3.77 m vs road crest 2.73 m, 29.8 m3/s |
| 3 | 1.00 | (unnamed) | Leominster | 1.95 m of water at peak; over 30 cm for 31.0 h; 30 cm reached 5.5 h into the storm; worst hour 84 mm (45% of the storm); water beside the road 0.31 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 0.6 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.13); a culvert within 100 m is overtopped |
| 4 | 1.00 | Route 2 | Leominster | 0.65 m of water at peak; over 30 cm for 4.5 h; 30 cm reached 5.5 h into the storm; worst hour 74 mm (48% of the storm); water beside the road 0.42 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 1.0 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.53); road sag 1.9 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 74 mm; catchment 39.6 ha) (P 1.00) |
| 5 | 1.00 | Depot Street | Fitchburg | 2.59 m of water at peak; over 30 cm for 35.0 h; 30 cm reached 0.5 h into the storm; worst hour 31 mm (31% of the storm); water beside the road 1.47 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 1.6 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.62); a culvert within 100 m is overtopped |
| 6 | 1.00 | Water Street | Leominster | 1.96 m of water at peak; over 30 cm for 31.0 h; 30 cm reached 5.5 h into the storm; worst hour 85 mm (45% of the storm); a culvert within 100 m is overtopped |
| 7 | 1.00 | Route 2 | Leominster | 0.79 m of water at peak; over 30 cm for 2.5 h; 30 cm reached 5.5 h into the storm; worst hour 79 mm (47% of the storm); water beside the road 0.71 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 2.8 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.82); road sag 3.4 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 74 mm; catchment 39.6 ha) (P 1.00) |
| 8 | 1.00 | Route 31 | Fitchburg | 1.04 m of water at peak; over 30 cm for 19.5 h; 30 cm reached 6.5 h into the storm; worst hour 31 mm (29% of the storm); a culvert within 100 m is overtopped |
| 9 | 1.00 | Litchfield Street | Leominster | 2.36 m of water at peak; over 30 cm for 16.0 h; 30 cm reached 5.5 h into the storm; worst hour 66 mm (43% of the storm); water beside the road 0.09 m below its crest (design freeboard 0.30 m; P 0.92); runoff beside / along the road at 0.7 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.31); a culvert within 100 m is overtopped |
| 10 | 1.00 | Route 12 | Leominster | 1.20 m of water at peak; over 30 cm for 9.5 h; 30 cm reached 5.5 h into the storm; worst hour 78 mm (45% of the storm); water beside the road 0.61 m above its crest (design freeboard 0.30 m; P 1.00); fast water: depth x speed 0.20 m2/s (small cars unstable from 0.3); runoff beside / along the road at 1.5 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.39); a culvert within 100 m is overtopped |
| 11 | 1.00 | Route 117 | Leominster | 1.46 m of water at peak; over 30 cm for 10.5 h; 30 cm reached 6.0 h into the storm; worst hour 58 mm (41% of the storm); cut off from hospitals |
| 12 | 1.00 | Route 117 | Leominster | 1.46 m of water at peak; over 30 cm for 10.5 h; 30 cm reached 6.0 h into the storm; worst hour 61 mm (42% of the storm); water beside the road 0.41 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 1.4 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.78); a culvert within 100 m is overtopped |
| 13 | 1.00 | Route 12 | Leominster | 1.28 m of water at peak; over 30 cm for 7.0 h; 30 cm reached 5.5 h into the storm; worst hour 85 mm (45% of the storm); water beside the road 0.58 m above its crest (design freeboard 0.30 m; P 1.00); a culvert within 100 m is overtopped |
| 14 | 1.00 | Narrows Road | Westminster | 0.98 m of water at peak; over 30 cm for 30.5 h; 30 cm reached 6.0 h into the storm; worst hour 40 mm (35% of the storm); water beside the road 0.68 m above its crest (design freeboard 0.30 m; P 1.00); fast water: depth x speed 0.19 m2/s (small cars unstable from 0.3); runoff beside / along the road at 1.3 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.28); a culvert within 100 m is overtopped |
| 15 | 1.00 | Merriam Avenue | Leominster | 0.96 m of water at peak; over 30 cm for 6.0 h; 30 cm reached 5.5 h into the storm; worst hour 84 mm (46% of the storm); water beside the road 0.77 m above its crest (design freeboard 0.30 m; P 1.00); fast water: depth x speed 0.35 m2/s (small cars unstable from 0.3); runoff beside / along the road at 1.3 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.69); road sag 0.4 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 81 mm; catchment 13.0 ha) (P 1.00) |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
