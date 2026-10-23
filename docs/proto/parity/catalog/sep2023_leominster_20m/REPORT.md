# Road-closure prototype: sep2023_loss_sep2023_leominster_20m

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on CPU (OpenMP)), 20 m grid, storm from 2023-09-11T16:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 4,542 |
| Expected closures (sum of probabilities) | 124.1 |
| Segments with closure probability >= 50% | 98 (68.7 km) |
| Further segments that may close (stream reaches the road crest) | 131 (82.7 km) |
| Culverts overtopped / surcharged | 130 / 3 of 616 |
| Road segments cut off from hospitals | 682 |
| Worst added trip time to a hospital | 24.1 min |
| Heaviest hour of rain | 89.3 mm |
| Flood model run time | 3037 s |

## Checks against what happened

- Storm-day flood reports in the area: 10; water >= 10 cm within 100 m of 90% of them, vs 67% of random points (any day).
- Segments flagged impassable are 2.94x as likely as an average segment to have a report within 200 m.
- MassDOT repeating flood sites in the area: 4; 2 have a segment within 150 m at P >= 0.5 (share of all segments at P >= 0.5: 2.2%).

## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 1.00 | Route 2 | Leominster | 8.49 m of water at peak; over 30 cm for 31.0 h; 30 cm reached 5.5 h into the storm; worst hour 67 mm (42% of the storm); runoff beside / along the road at 2.0 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.60); a culvert within 100 m is overtopped |
| 2 | 1.00 | (unnamed) | Leominster | 1.55 m of water at peak; over 30 cm for 27.5 h; 30 cm reached 5.5 h into the storm; worst hour 84 mm (45% of the storm); water beside the road 0.04 m above its crest (design freeboard 0.30 m; P 0.99); a culvert within 100 m is overtopped |
| 3 | 1.00 | Depot Street | Fitchburg | 1.06 m of water at peak; over 30 cm for 34.0 h; 30 cm reached 0.5 h into the storm; worst hour 31 mm (31% of the storm); runoff beside / along the road at 1.6 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.73); a culvert within 100 m is overtopped |
| 4 | 1.00 | Water Street | Leominster | 1.56 m of water at peak; over 30 cm for 27.5 h; 30 cm reached 5.5 h into the storm; worst hour 85 mm (45% of the storm); a culvert within 100 m is overtopped |
| 5 | 1.00 | Litchfield Street | Leominster | 1.65 m of water at peak; over 30 cm for 15.0 h; 30 cm reached 6.0 h into the storm; worst hour 66 mm (43% of the storm); a culvert within 100 m is overtopped |
| 6 | 1.00 | Route 12 | Leominster | 0.90 m of water at peak; over 30 cm for 8.5 h; 30 cm reached 6.0 h into the storm; worst hour 78 mm (45% of the storm); water beside the road 0.10 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 0.9 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.20); a culvert within 100 m is overtopped |
| 7 | 1.00 | Route 117 | Leominster | 1.06 m of water at peak; over 30 cm for 9.5 h; 30 cm reached 6.5 h into the storm; worst hour 58 mm (41% of the storm); cut off from hospitals |
| 8 | 1.00 | Route 117 | Leominster | 1.06 m of water at peak; over 30 cm for 9.5 h; 30 cm reached 6.5 h into the storm; worst hour 61 mm (42% of the storm); water beside the road 0.10 m below its crest (design freeboard 0.30 m; P 0.91); runoff beside / along the road at 0.8 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.34); a culvert within 100 m is overtopped |
| 9 | 1.00 | Route 12 | Leominster | 0.81 m of water at peak; over 30 cm for 5.5 h; 30 cm reached 6.0 h into the storm; worst hour 85 mm (45% of the storm); water beside the road 0.41 m below its crest (design freeboard 0.30 m; P 0.23); a culvert within 100 m is overtopped |
| 10 | 1.00 | Merriam Avenue | Leominster | 0.72 m of water at peak; over 30 cm for 4.5 h; 30 cm reached 5.5 h into the storm; worst hour 84 mm (46% of the storm); water beside the road 0.53 m above its crest (design freeboard 0.30 m; P 1.00); fast water: depth x speed 0.22 m2/s (small cars unstable from 0.3); runoff beside / along the road at 1.1 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.61); road sag 0.4 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 81 mm; catchment 13.0 ha) (P 1.00) |
| 11 | 1.00 | Route 140 | Princeton | 0.77 m of water at peak; over 30 cm for 8.5 h; 30 cm reached 7.5 h into the storm; worst hour 42 mm (30% of the storm); water beside the road 0.20 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 1.4 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.52); a culvert within 100 m is overtopped |
| 12 | 1.00 | Kingman Drive | Leominster | 1.15 m of water at peak; over 30 cm for 13.5 h; 30 cm reached 5.5 h into the storm; worst hour 85 mm (46% of the storm); water beside the road 0.49 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 1.7 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.83); a culvert within 100 m is overtopped |
| 13 | 1.00 | Litchfield Street | Leominster | 1.34 m of water at peak; over 30 cm for 11.5 h; 30 cm reached 6.0 h into the storm; worst hour 73 mm (45% of the storm) |
| 14 | 1.00 | Depot Square | Leominster | 1.55 m of water at peak; over 30 cm for 27.5 h; 30 cm reached 5.5 h into the storm; worst hour 85 mm (45% of the storm); water beside the road 0.01 m above its crest (design freeboard 0.30 m; P 0.98); a culvert within 100 m is overtopped |
| 15 | 1.00 | Pleasant Street | Leominster | 0.79 m of water at peak; over 30 cm for 4.0 h; 30 cm reached 5.5 h into the storm; worst hour 87 mm (45% of the storm); runoff beside / along the road at 0.6 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.10); a culvert within 100 m is overtopped |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
