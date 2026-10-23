# Road-closure prototype: sep2023_loss_leo48_cn085

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on CPU (OpenMP)), 20 m grid, storm from 2023-09-11T16:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 5,183 |
| Expected closures (sum of probabilities) | 118.1 |
| Segments with closure probability >= 50% | 91 (61.4 km) |
| Further segments that may close (stream reaches the road crest) | 118 (71.6 km) |
| Culverts overtopped / surcharged | 118 / 2 of 713 |
| Road segments cut off from hospitals | 666 |
| Worst added trip time to a hospital | 16.9 min |
| Heaviest hour of rain | 89.3 mm |
| Flood model run time | 3354 s |

## Checks against what happened

- Storm-day flood reports in the area: 10; water >= 10 cm within 100 m of 90% of them, vs 63% of random points (any day).
- Segments flagged impassable are 3.57x as likely as an average segment to have a report within 200 m.
- MassDOT repeating flood sites in the area: 4; 2 have a segment within 150 m at P >= 0.5 (share of all segments at P >= 0.5: 1.8%).

## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 1.00 | Route 2 | Leominster | 7.85 m of water at peak; over 30 cm for 43.0 h; 30 cm reached 5.5 h into the storm; worst hour 67 mm (40% of the storm); runoff beside / along the road at 2.4 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.55); a culvert within 100 m is overtopped |
| 2 | 1.00 | (unnamed) | Leominster | 1.49 m of water at peak; over 30 cm for 26.0 h; 30 cm reached 6.0 h into the storm; worst hour 84 mm (43% of the storm); water beside the road 0.03 m above its crest (design freeboard 0.30 m; P 0.98); a culvert within 100 m is overtopped |
| 3 | 1.00 | Depot Street | Fitchburg | 0.92 m of water at peak; over 30 cm for 24.0 h; 30 cm reached 0.5 h into the storm; worst hour 31 mm (29% of the storm); runoff beside / along the road at 1.6 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.64); a culvert within 100 m is overtopped |
| 4 | 1.00 | Water Street | Leominster | 1.49 m of water at peak; over 30 cm for 26.0 h; 30 cm reached 6.0 h into the storm; worst hour 85 mm (43% of the storm); a culvert within 100 m is overtopped |
| 5 | 1.00 | Route 12 | Leominster | 0.86 m of water at peak; over 30 cm for 8.5 h; 30 cm reached 6.0 h into the storm; worst hour 78 mm (43% of the storm); water beside the road 0.09 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 0.8 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.24); a culvert within 100 m is overtopped |
| 6 | 1.00 | Litchfield Street | Leominster | 1.57 m of water at peak; over 30 cm for 14.0 h; 30 cm reached 6.5 h into the storm; worst hour 66 mm (41% of the storm); a culvert within 100 m is overtopped |
| 7 | 1.00 | Route 117 | Leominster | 1.02 m of water at peak; over 30 cm for 9.5 h; 30 cm reached 6.5 h into the storm; worst hour 59 mm (39% of the storm); cut off from hospitals |
| 8 | 1.00 | Route 117 | Leominster | 1.02 m of water at peak; over 30 cm for 9.5 h; 30 cm reached 6.5 h into the storm; worst hour 61 mm (39% of the storm); runoff beside / along the road at 0.8 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.30); a culvert within 100 m is overtopped |
| 9 | 1.00 | Route 12 | Leominster | 0.78 m of water at peak; over 30 cm for 5.5 h; 30 cm reached 6.0 h into the storm; worst hour 85 mm (43% of the storm); water beside the road 0.45 m below its crest (design freeboard 0.30 m; P 0.16); a culvert within 100 m is overtopped |
| 10 | 1.00 | Route 70 | Lancaster | 1.37 m of water at peak; over 30 cm for 8.0 h; 30 cm reached 9.0 h into the storm; worst hour 24 mm (34% of the storm); a culvert within 100 m is overtopped |
| 11 | 1.00 | Route 70 | Lancaster | 1.38 m of water at peak; over 30 cm for 8.0 h; 30 cm reached 9.0 h into the storm; worst hour 25 mm (35% of the storm); runoff beside / along the road at 2.1 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.15); a culvert within 100 m is overtopped |
| 12 | 1.00 | Merriam Avenue | Leominster | 0.69 m of water at peak; over 30 cm for 4.5 h; 30 cm reached 5.5 h into the storm; worst hour 84 mm (44% of the storm); water beside the road 0.49 m above its crest (design freeboard 0.30 m; P 1.00); fast water: depth x speed 0.20 m2/s (small cars unstable from 0.3); runoff beside / along the road at 1.1 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.61); road sag 0.4 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 81 mm; catchment 13.0 ha) (P 1.00) |
| 13 | 1.00 | Route 140 | Princeton | 0.73 m of water at peak; over 30 cm for 8.0 h; 30 cm reached 7.5 h into the storm; worst hour 42 mm (28% of the storm); runoff beside / along the road at 1.4 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.43); a culvert within 100 m is overtopped |
| 14 | 1.00 | Kingman Drive | Leominster | 1.09 m of water at peak; over 30 cm for 12.5 h; 30 cm reached 5.5 h into the storm; worst hour 85 mm (44% of the storm); water beside the road 0.47 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 1.7 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.85); a culvert within 100 m is overtopped |
| 15 | 1.00 | Litchfield Street | Leominster | 1.28 m of water at peak; over 30 cm for 11.5 h; 30 cm reached 6.0 h into the storm; worst hour 74 mm (42% of the storm) |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
