# Road-closure prototype: sep2023_loss_sep2023_infil0

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on CPU (OpenMP)), 20 m grid, storm from 2023-09-11T16:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 4,542 |
| Expected closures (sum of probabilities) | 161.0 |
| Segments with closure probability >= 50% | 126 (85.3 km) |
| Further segments that may close (stream reaches the road crest) | 183 (119.4 km) |
| Culverts overtopped / surcharged | 153 / 4 of 616 |
| Road segments cut off from hospitals | 755 |
| Worst added trip time to a hospital | 26.0 min |
| Heaviest hour of rain | 89.3 mm |
| Flood model run time | 1654 s |

## Checks against what happened

- Storm-day flood reports in the area: 10; water >= 10 cm within 100 m of 100% of them, vs 74% of random points (any day).
- Segments flagged impassable are 2.58x as likely as an average segment to have a report within 200 m.
- MassDOT repeating flood sites in the area: 4; 3 have a segment within 150 m at P >= 0.5 (share of all segments at P >= 0.5: 2.8%).

## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 1.00 | Route 2 | Leominster | 15.54 m of water at peak; over 30 cm for 31.0 h; 30 cm reached 5.5 h into the storm; worst hour 67 mm (42% of the storm); runoff beside / along the road at 5.0 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.51); a culvert within 100 m is overtopped |
| 2 | 1.00 | (unnamed) | Leominster | 1.65 m of water at peak; over 30 cm for 30.0 h; 30 cm reached 5.5 h into the storm; worst hour 84 mm (45% of the storm); water beside the road 0.05 m above its crest (design freeboard 0.30 m; P 0.99); a culvert within 100 m is overtopped |
| 3 | 1.00 | Depot Street | Fitchburg | 1.58 m of water at peak; over 30 cm for 36.0 h; 30 cm reached 0.5 h into the storm; worst hour 31 mm (31% of the storm); runoff beside / along the road at 4.9 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.83); a culvert within 100 m is overtopped |
| 4 | 1.00 | Route 31 | Fitchburg | 0.73 m of water at peak; over 30 cm for 28.5 h; 30 cm reached 8.0 h into the storm; worst hour 31 mm (29% of the storm); a culvert within 100 m is overtopped |
| 5 | 1.00 | Water Street | Leominster | 1.66 m of water at peak; over 30 cm for 30.0 h; 30 cm reached 5.5 h into the storm; worst hour 85 mm (45% of the storm); a culvert within 100 m is overtopped |
| 6 | 1.00 | Litchfield Street | Leominster | 1.80 m of water at peak; over 30 cm for 15.5 h; 30 cm reached 6.0 h into the storm; worst hour 66 mm (43% of the storm); a culvert within 100 m is overtopped |
| 7 | 1.00 | Route 12 | Leominster | 0.98 m of water at peak; over 30 cm for 9.0 h; 30 cm reached 6.0 h into the storm; worst hour 78 mm (45% of the storm); water beside the road 0.52 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 2.6 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.49); a culvert within 100 m is overtopped |
| 8 | 1.00 | Route 117 | Leominster | 1.15 m of water at peak; over 30 cm for 10.0 h; 30 cm reached 6.5 h into the storm; worst hour 58 mm (41% of the storm); cut off from hospitals |
| 9 | 1.00 | Route 117 | Leominster | 1.15 m of water at peak; over 30 cm for 10.0 h; 30 cm reached 6.5 h into the storm; worst hour 61 mm (42% of the storm); water beside the road 0.07 m below its crest (design freeboard 0.30 m; P 0.94); runoff beside / along the road at 3.4 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.88); a culvert within 100 m is overtopped |
| 10 | 1.00 | Route 12 | Leominster | 0.88 m of water at peak; over 30 cm for 6.5 h; 30 cm reached 6.0 h into the storm; worst hour 85 mm (45% of the storm); water beside the road 0.18 m above its crest (design freeboard 0.30 m; P 1.00); a culvert within 100 m is overtopped |
| 11 | 1.00 | Merriam Avenue | Leominster | 0.79 m of water at peak; over 30 cm for 5.5 h; 30 cm reached 5.5 h into the storm; worst hour 84 mm (46% of the storm); water beside the road 0.60 m above its crest (design freeboard 0.30 m; P 1.00); fast water: depth x speed 0.26 m2/s (small cars unstable from 0.3); runoff beside / along the road at 4.8 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.99); road sag 0.4 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 81 mm; catchment 13.0 ha) (P 1.00) |
| 12 | 1.00 | Route 140 | Princeton | 0.88 m of water at peak; over 30 cm for 9.5 h; 30 cm reached 7.0 h into the storm; worst hour 42 mm (30% of the storm); water beside the road 0.21 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 4.0 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.51); a culvert within 100 m is overtopped |
| 13 | 1.00 | Main Street | Fitchburg | 0.67 m of water at peak; over 30 cm for 15.5 h; 30 cm reached 7.5 h into the storm; worst hour 27 mm (32% of the storm); a culvert within 100 m is overtopped |
| 14 | 1.00 | Kingman Drive | Leominster | 1.23 m of water at peak; over 30 cm for 16.0 h; 30 cm reached 5.5 h into the storm; worst hour 85 mm (46% of the storm); water beside the road 0.51 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 5.0 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.94); a culvert within 100 m is overtopped |
| 15 | 1.00 | Litchfield Street | Leominster | 1.44 m of water at peak; over 30 cm for 12.5 h; 30 cm reached 5.5 h into the storm; worst hour 73 mm (45% of the storm); water beside the road 0.26 m below its crest (design freeboard 0.30 m; P 0.61) |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
