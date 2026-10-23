# Road-closure prototype: sep2023_loss_sep2023_leominster_20m

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on CPU (OpenMP)), 20 m grid, storm from 2023-09-11T16:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 4,542 |
| Expected closures (sum of probabilities) | 204.5 |
| Segments with closure probability >= 50% | 180 (118.3 km) |
| Further segments that may close (stream reaches the road crest) | 252 (162.4 km) |
| Culverts overtopped / surcharged | 173 / 7 of 616 |
| Road segments cut off from hospitals | 924 |
| Worst added trip time to a hospital | 28.6 min |
| Heaviest hour of rain | 89.3 mm |
| Flood model run time | 2269 s |

## Checks against what happened

- Storm-day flood reports in the area: 10; water >= 10 cm within 100 m of 100% of them, vs 80% of random points (any day).
- Segments flagged impassable are 2.55x as likely as an average segment to have a report within 200 m.
- MassDOT repeating flood sites in the area: 4; 3 have a segment within 150 m at P >= 0.5 (share of all segments at P >= 0.5: 4.0%).

## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 1.00 | Route 2 | Leominster | 11.75 m of water at peak; over 30 cm for 31.0 h; 30 cm reached 5.5 h into the storm; worst hour 67 mm (42% of the storm); runoff beside / along the road at 2.5 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.91); a culvert within 100 m is overtopped |
| 2 | 1.00 | (unnamed) | Leominster | 1.89 m of water at peak; over 30 cm for 30.5 h; 30 cm reached 5.5 h into the storm; worst hour 84 mm (45% of the storm); water beside the road 0.09 m above its crest (design freeboard 0.30 m; P 0.99); a culvert within 100 m is overtopped |
| 3 | 1.00 | Depot Street | Fitchburg | 1.75 m of water at peak; over 30 cm for 34.0 h; 30 cm reached 0.5 h into the storm; worst hour 31 mm (31% of the storm); water beside the road 1.09 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 1.5 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.46); a culvert within 100 m is overtopped |
| 4 | 1.00 | Water Street | Leominster | 1.90 m of water at peak; over 30 cm for 30.5 h; 30 cm reached 5.5 h into the storm; worst hour 85 mm (45% of the storm); a culvert within 100 m is overtopped |
| 5 | 1.00 | Route 2 | Leominster | 0.64 m of water at peak; over 30 cm for 2.5 h; 30 cm reached 5.5 h into the storm; worst hour 79 mm (47% of the storm); water beside the road 0.62 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 1.8 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.79); road sag 3.4 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 74 mm; catchment 39.6 ha) (P 1.00) |
| 6 | 1.00 | Litchfield Street | Leominster | 2.10 m of water at peak; over 30 cm for 15.0 h; 30 cm reached 6.0 h into the storm; worst hour 66 mm (43% of the storm); a culvert within 100 m is overtopped |
| 7 | 1.00 | Route 31 | Fitchburg | 0.74 m of water at peak; over 30 cm for 17.0 h; 30 cm reached 7.5 h into the storm; worst hour 31 mm (29% of the storm); a culvert within 100 m is overtopped |
| 8 | 1.00 | Route 12 | Leominster | 1.12 m of water at peak; over 30 cm for 8.5 h; 30 cm reached 6.0 h into the storm; worst hour 78 mm (45% of the storm); water beside the road 0.57 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 1.0 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.23); a culvert within 100 m is overtopped |
| 9 | 1.00 | Route 117 | Leominster | 1.31 m of water at peak; over 30 cm for 10.0 h; 30 cm reached 6.0 h into the storm; worst hour 58 mm (41% of the storm); cut off from hospitals |
| 10 | 1.00 | Route 117 | Leominster | 1.31 m of water at peak; over 30 cm for 10.0 h; 30 cm reached 6.0 h into the storm; worst hour 61 mm (42% of the storm); water beside the road 0.12 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 1.6 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.61); a culvert within 100 m is overtopped |
| 11 | 1.00 | Route 12 | Leominster | 1.03 m of water at peak; over 30 cm for 6.0 h; 30 cm reached 6.0 h into the storm; worst hour 85 mm (45% of the storm); water beside the road 0.22 m above its crest (design freeboard 0.30 m; P 1.00); a culvert within 100 m is overtopped |
| 12 | 1.00 | Narrows Road | Westminster | 0.72 m of water at peak; over 30 cm for 27.0 h; 30 cm reached 7.0 h into the storm; worst hour 40 mm (35% of the storm); water beside the road 0.61 m above its crest (design freeboard 0.30 m; P 1.00); a culvert within 100 m is overtopped |
| 13 | 1.00 | Merriam Avenue | Leominster | 0.93 m of water at peak; over 30 cm for 5.0 h; 30 cm reached 5.5 h into the storm; worst hour 84 mm (46% of the storm); water beside the road 0.74 m above its crest (design freeboard 0.30 m; P 1.00); fast water: depth x speed 0.34 m2/s (small cars unstable from 0.3); runoff beside / along the road at 1.2 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.67); road sag 0.4 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 81 mm; catchment 13.0 ha) (P 1.00) |
| 14 | 1.00 | Narrows Road | Westminster | 0.64 m of water at peak; over 30 cm for 24.5 h; 30 cm reached 7.5 h into the storm; worst hour 39 mm (33% of the storm); water beside the road 0.21 m below its crest (design freeboard 0.30 m; P 0.72); runoff beside / along the road at 1.6 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.80); a culvert within 100 m is overtopped |
| 15 | 1.00 | Route 140 | Princeton | 1.01 m of water at peak; over 30 cm for 10.0 h; 30 cm reached 6.5 h into the storm; worst hour 42 mm (30% of the storm); water beside the road 0.22 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 2.8 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.58); a culvert within 100 m is overtopped |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
