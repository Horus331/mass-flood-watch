# Road-closure prototype: sep2023_rain_sep2023_gauge_dt5

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on CPU (OpenMP)), 20 m grid, storm from 2023-09-11T16:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 4,542 |
| Expected closures (sum of probabilities) | 143.6 |
| Segments with closure probability >= 50% | 113 (76.9 km) |
| Further segments that may close (stream reaches the road crest) | 158 (105.7 km) |
| Culverts overtopped / surcharged | 139 / 6 of 616 |
| Road segments cut off from hospitals | 694 |
| Worst added trip time to a hospital | 24.9 min |
| Heaviest hour of rain | 91.6 mm |
| Flood model run time | 3021 s |

## Checks against what happened

- Storm-day flood reports in the area: 10; water >= 10 cm within 100 m of 90% of them, vs 68% of random points (any day).
- Segments flagged impassable are 2.87x as likely as an average segment to have a report within 200 m.
- MassDOT repeating flood sites in the area: 4; 2 have a segment within 150 m at P >= 0.5 (share of all segments at P >= 0.5: 2.5%).

## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 1.00 | Route 2 | Leominster | 8.55 m of water at peak; over 30 cm for 30.5 h; 30 cm reached 6.0 h into the storm; worst hour 65 mm (42% of the storm); runoff beside / along the road at 2.3 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.84); a culvert within 100 m is overtopped |
| 2 | 1.00 | (unnamed) | Leominster | 1.61 m of water at peak; over 30 cm for 27.5 h; 30 cm reached 6.0 h into the storm; worst hour 82 mm (45% of the storm); water beside the road 0.04 m above its crest (design freeboard 0.30 m; P 0.99); a culvert within 100 m is overtopped |
| 3 | 1.00 | Depot Street | Fitchburg | 1.13 m of water at peak; over 30 cm for 33.5 h; 30 cm reached 0.5 h into the storm; worst hour 30 mm (31% of the storm); runoff beside / along the road at 2.0 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.76); a culvert within 100 m is overtopped |
| 4 | 1.00 | Water Street | Leominster | 1.61 m of water at peak; over 30 cm for 28.0 h; 30 cm reached 6.0 h into the storm; worst hour 82 mm (45% of the storm); a culvert within 100 m is overtopped |
| 5 | 1.00 | Litchfield Street | Leominster | 1.80 m of water at peak; over 30 cm for 15.0 h; 30 cm reached 6.0 h into the storm; worst hour 66 mm (43% of the storm); a culvert within 100 m is overtopped |
| 6 | 1.00 | Route 12 | Leominster | 0.99 m of water at peak; over 30 cm for 8.5 h; 30 cm reached 6.0 h into the storm; worst hour 78 mm (45% of the storm); water beside the road 0.52 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 1.0 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.20); a culvert within 100 m is overtopped |
| 7 | 1.00 | Route 117 | Leominster | 1.15 m of water at peak; over 30 cm for 9.5 h; 30 cm reached 6.5 h into the storm; worst hour 58 mm (41% of the storm); cut off from hospitals |
| 8 | 1.00 | Route 117 | Leominster | 1.15 m of water at peak; over 30 cm for 9.5 h; 30 cm reached 6.5 h into the storm; worst hour 60 mm (42% of the storm); water beside the road 0.07 m below its crest (design freeboard 0.30 m; P 0.94); runoff beside / along the road at 0.9 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.40); a culvert within 100 m is overtopped |
| 9 | 1.00 | Route 12 | Leominster | 0.85 m of water at peak; over 30 cm for 5.5 h; 30 cm reached 6.0 h into the storm; worst hour 83 mm (45% of the storm); water beside the road 0.17 m above its crest (design freeboard 0.30 m; P 1.00); a culvert within 100 m is overtopped |
| 10 | 1.00 | Merriam Avenue | Leominster | 0.75 m of water at peak; over 30 cm for 4.5 h; 30 cm reached 5.5 h into the storm; worst hour 81 mm (46% of the storm); water beside the road 0.56 m above its crest (design freeboard 0.30 m; P 1.00); fast water: depth x speed 0.24 m2/s (small cars unstable from 0.3); runoff beside / along the road at 1.1 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.62); road sag 0.4 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 79 mm; catchment 13.0 ha) (P 1.00) |
| 11 | 1.00 | Route 140 | Princeton | 0.88 m of water at peak; over 30 cm for 9.0 h; 30 cm reached 7.0 h into the storm; worst hour 50 mm (31% of the storm); water beside the road 0.23 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 2.2 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.62); a culvert within 100 m is overtopped |
| 12 | 1.00 | Kingman Drive | Leominster | 1.20 m of water at peak; over 30 cm for 14.5 h; 30 cm reached 5.5 h into the storm; worst hour 84 mm (46% of the storm); water beside the road 0.51 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 1.8 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.85); a culvert within 100 m is overtopped |
| 13 | 1.00 | Litchfield Street | Leominster | 1.46 m of water at peak; over 30 cm for 12.0 h; 30 cm reached 5.5 h into the storm; worst hour 75 mm (45% of the storm); water beside the road 0.25 m below its crest (design freeboard 0.30 m; P 0.62) |
| 14 | 1.00 | Depot Square | Leominster | 1.61 m of water at peak; over 30 cm for 27.5 h; 30 cm reached 6.0 h into the storm; worst hour 82 mm (45% of the storm); water beside the road 0.02 m above its crest (design freeboard 0.30 m; P 0.98); a culvert within 100 m is overtopped |
| 15 | 1.00 | Commercial Road | Leominster | 1.33 m of water at peak; over 30 cm for 10.0 h; 30 cm reached 6.5 h into the storm; worst hour 74 mm (44% of the storm); water beside the road 0.20 m above its crest (design freeboard 0.30 m; P 1.00); a culvert within 100 m is overtopped |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
