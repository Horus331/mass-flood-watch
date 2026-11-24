# Road-closure prototype: sep2023_loss_C20

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on CPU (OpenMP)), 20 m grid, storm from 2023-09-11T16:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 4,542 |
| Expected closures (sum of probabilities) | 102.3 |
| Segments with closure probability >= 50% | 80 (52.4 km) |
| Further segments that may close (stream reaches the road crest) | 142 (88.6 km) |
| Culverts overtopped / surcharged | 76 / 7 of 616 |
| Road segments cut off from hospitals | 464 |
| Worst added trip time to a hospital | 21.6 min |
| Heaviest hour of rain | 89.3 mm |
| Flood model run time | 2396 s |

## Checks against what happened

- Storm-day flood reports in the area: 10; water >= 10 cm within 100 m of 90% of them, vs 67% of random points (any day).
- Segments flagged impassable are 3.21x as likely as an average segment to have a report within 200 m.
- MassDOT repeating flood sites in the area: 4; 2 have a segment within 150 m at P >= 0.5 (share of all segments at P >= 0.5: 1.8%).

## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 1.00 | Litchfield Street | Leominster | 2.51 m of water at peak; over 30 cm for 35.4 h; 30 cm reached 0.7 h into the storm; worst hour 66 mm (43% of the storm); water beside the road 0.38 m below its crest (design freeboard 0.30 m; P 0.30); a culvert within 100 m is overtopped |
| 2 | 1.00 | Depot Street | Fitchburg | 0.90 m of water at peak; over 30 cm for 33.2 h; 30 cm reached 0.1 h into the storm; worst hour 31 mm (31% of the storm); runoff beside / along the road at 1.6 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.73); a culvert within 100 m is overtopped |
| 3 | 1.00 | (unnamed) | Leominster | 0.71 m of water at peak; over 30 cm for 7.5 h; 30 cm reached 6.1 h into the storm; worst hour 84 mm (45% of the storm); water beside the road 0.04 m above its crest (design freeboard 0.30 m; P 0.99); runoff beside / along the road at 2.5 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.98); a culvert within 100 m is overtopped |
| 4 | 1.00 | Route 12 | Leominster | 0.81 m of water at peak; over 30 cm for 8.3 h; 30 cm reached 5.8 h into the storm; worst hour 78 mm (45% of the storm); water beside the road 0.09 m above its crest (design freeboard 0.30 m; P 0.99); runoff beside / along the road at 0.8 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.20); a culvert within 100 m is overtopped |
| 5 | 1.00 | Route 117 | Leominster | 0.93 m of water at peak; over 30 cm for 9.2 h; 30 cm reached 7.2 h into the storm; worst hour 58 mm (41% of the storm); cut off from hospitals |
| 6 | 1.00 | Route 117 | Leominster | 0.93 m of water at peak; over 30 cm for 9.2 h; 30 cm reached 7.2 h into the storm; worst hour 61 mm (42% of the storm); runoff beside / along the road at 0.8 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.27); a culvert within 100 m is overtopped |
| 7 | 1.00 | Merriam Avenue | Leominster | 0.72 m of water at peak; over 30 cm for 4.4 h; 30 cm reached 5.5 h into the storm; worst hour 84 mm (46% of the storm); water beside the road 0.53 m above its crest (design freeboard 0.30 m; P 1.00); fast water: depth x speed 0.22 m2/s (small cars unstable from 0.3); runoff beside / along the road at 1.1 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.61); road sag 0.4 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 81 mm; catchment 13.0 ha) (P 1.00) |
| 8 | 1.00 | Route 140 | Princeton | 0.73 m of water at peak; over 30 cm for 8.3 h; 30 cm reached 7.0 h into the storm; worst hour 42 mm (30% of the storm); water beside the road 0.20 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 1.4 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.54); a culvert within 100 m is overtopped |
| 9 | 1.00 | Water Street | Leominster | 0.73 m of water at peak; over 30 cm for 8.3 h; 30 cm reached 6.1 h into the storm; worst hour 85 mm (45% of the storm); runoff beside / along the road at 2.5 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.98); a culvert within 100 m is overtopped |
| 10 | 1.00 | Kingman Drive | Leominster | 1.13 m of water at peak; over 30 cm for 12.9 h; 30 cm reached 5.5 h into the storm; worst hour 85 mm (46% of the storm); water beside the road 0.47 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 1.5 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.78); a culvert within 100 m is overtopped |
| 11 | 1.00 | Campbell Avenue | Leominster | 0.90 m of water at peak; over 30 cm for 30.3 h; 30 cm reached 5.8 h into the storm; worst hour 82 mm (46% of the storm); water beside the road 0.31 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 0.6 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.14); culvert (unnamed): headwater 2.22 m vs road crest 2.13 m, 2.2 m3/s |
| 12 | 1.00 | Litchfield Street | Leominster | 0.89 m of water at peak; over 30 cm for 8.6 h; 30 cm reached 5.7 h into the storm; worst hour 73 mm (45% of the storm); runoff beside / along the road at 0.9 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.15) |
| 13 | 1.00 | Commercial Road | Leominster | 0.97 m of water at peak; over 30 cm for 10.8 h; 30 cm reached 6.2 h into the storm; worst hour 77 mm (44% of the storm); water beside the road 0.18 m above its crest (design freeboard 0.30 m; P 1.00); a culvert within 100 m is overtopped |
| 14 | 1.00 | Meadowbrook Acres | Leominster | 0.98 m of water at peak; over 30 cm for 9.4 h; 30 cm reached 6.9 h into the storm; worst hour 73 mm (44% of the storm); water beside the road 0.94 m above its crest (design freeboard 0.30 m; P 1.00) |
| 15 | 1.00 | Depot Square | Leominster | 0.72 m of water at peak; over 30 cm for 7.9 h; 30 cm reached 6.1 h into the storm; worst hour 85 mm (45% of the storm); a culvert within 100 m is overtopped |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
