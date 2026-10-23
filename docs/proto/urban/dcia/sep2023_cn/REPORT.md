# Road-closure prototype: sep2023_loss_sep2023_cn

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on CPU (OpenMP)), 20 m grid, storm from 2023-09-11T16:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 4,462 |
| Expected closures (sum of probabilities) | 139.6 |
| Segments with closure probability >= 50% | 110 (79.0 km) |
| Further segments that may close (stream reaches the road crest) | 151 (94.9 km) |
| Culverts overtopped / surcharged | 143 / 4 of 616 |
| Road segments cut off from hospitals | 708 |
| Worst added trip time to a hospital | 24.4 min |
| Heaviest hour of rain | 89.3 mm |
| Flood model run time | 2025 s |

## Checks against what happened

- Storm-day flood reports in the area: 10; water >= 10 cm within 100 m of 90% of them, vs 68% of random points (any day).
- Segments flagged impassable are 2.89x as likely as an average segment to have a report within 200 m.
- MassDOT repeating flood sites in the area: 4; 3 have a segment within 150 m at P >= 0.5 (share of all segments at P >= 0.5: 2.5%).

## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 1.00 | Route 2 | Leominster | 11.09 m of water at peak; over 30 cm for 31.0 h; 30 cm reached 5.5 h into the storm; worst hour 67 mm (42% of the storm); runoff beside / along the road at 5.0 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.51); a culvert within 100 m is overtopped |
| 2 | 1.00 | (unnamed) | Leominster | 1.61 m of water at peak; over 30 cm for 23.0 h; 30 cm reached 5.5 h into the storm; worst hour 84 mm (45% of the storm); water beside the road 0.05 m above its crest (design freeboard 0.30 m; P 0.99); a culvert within 100 m is overtopped |
| 3 | 1.00 | Westminster Street | Fitchburg | 0.65 m of water at peak; over 30 cm for 22.5 h; 30 cm reached 14.0 h into the storm; worst hour 32 mm (28% of the storm); water beside the road 1.53 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 5.0 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.84); a culvert within 100 m is overtopped |
| 4 | 1.00 | Depot Street | Fitchburg | 2.07 m of water at peak; over 30 cm for 34.0 h; 30 cm reached 0.5 h into the storm; worst hour 31 mm (31% of the storm); runoff beside / along the road at 4.9 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.80); a culvert within 100 m is overtopped |
| 5 | 1.00 | Route 31 | Fitchburg | 1.12 m of water at peak; over 30 cm for 28.0 h; 30 cm reached 8.5 h into the storm; worst hour 31 mm (29% of the storm); a culvert within 100 m is overtopped |
| 6 | 1.00 | Water Street | Leominster | 1.61 m of water at peak; over 30 cm for 23.0 h; 30 cm reached 5.5 h into the storm; worst hour 85 mm (45% of the storm); a culvert within 100 m is overtopped |
| 7 | 1.00 | Route 12 | Leominster | 0.94 m of water at peak; over 30 cm for 8.5 h; 30 cm reached 6.0 h into the storm; worst hour 78 mm (45% of the storm); water beside the road 0.50 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 5.0 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.37); a culvert within 100 m is overtopped |
| 8 | 1.00 | Litchfield Street | Leominster | 1.72 m of water at peak; over 30 cm for 13.0 h; 30 cm reached 6.0 h into the storm; worst hour 66 mm (43% of the storm); runoff beside / along the road at 0.6 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.22); a culvert within 100 m is overtopped |
| 9 | 1.00 | Route 117 | Leominster | 1.10 m of water at peak; over 30 cm for 9.0 h; 30 cm reached 6.5 h into the storm; worst hour 61 mm (42% of the storm); water beside the road 0.09 m below its crest (design freeboard 0.30 m; P 0.92); runoff beside / along the road at 4.3 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.82); a culvert within 100 m is overtopped |
| 10 | 1.00 | Route 12 | Leominster | 0.84 m of water at peak; over 30 cm for 5.5 h; 30 cm reached 6.0 h into the storm; worst hour 85 mm (45% of the storm); water beside the road 0.17 m above its crest (design freeboard 0.30 m; P 1.00); a culvert within 100 m is overtopped |
| 11 | 1.00 | Main Street | Fitchburg | 1.10 m of water at peak; over 30 cm for 24.5 h; 30 cm reached 8.5 h into the storm; worst hour 27 mm (32% of the storm); a culvert within 100 m is overtopped |
| 12 | 1.00 | Merriam Avenue | Leominster | 0.76 m of water at peak; over 30 cm for 5.0 h; 30 cm reached 5.5 h into the storm; worst hour 84 mm (46% of the storm); water beside the road 0.57 m above its crest (design freeboard 0.30 m; P 1.00); fast water: depth x speed 0.24 m2/s (small cars unstable from 0.3); runoff beside / along the road at 4.8 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.98); road sag 0.4 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 81 mm; catchment 13.0 ha) (P 1.00) |
| 13 | 1.00 | Route 140 | Princeton | 0.81 m of water at peak; over 30 cm for 8.5 h; 30 cm reached 7.0 h into the storm; worst hour 42 mm (30% of the storm); water beside the road 0.20 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 3.0 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.60); a culvert within 100 m is overtopped |
| 14 | 1.00 | Kingman Drive | Leominster | 1.20 m of water at peak; over 30 cm for 13.0 h; 30 cm reached 5.5 h into the storm; worst hour 85 mm (46% of the storm); water beside the road 0.50 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 4.2 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.91); a culvert within 100 m is overtopped |
| 15 | 1.00 | Commercial Road | Leominster | 1.35 m of water at peak; over 30 cm for 30.0 h; 30 cm reached 6.5 h into the storm; worst hour 77 mm (44% of the storm); water beside the road 0.21 m above its crest (design freeboard 0.30 m; P 1.00); a culvert within 100 m is overtopped |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
