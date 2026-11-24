# Road-closure prototype: sep2023_loss_B

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on CPU (OpenMP)), 20 m grid, storm from 2023-09-11T16:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 4,542 |
| Expected closures (sum of probabilities) | 101.9 |
| Segments with closure probability >= 50% | 70 (49.0 km) |
| Further segments that may close (stream reaches the road crest) | 141 (88.1 km) |
| Culverts overtopped / surcharged | 109 / 2 of 616 |
| Road segments cut off from hospitals | 628 |
| Worst added trip time to a hospital | 24.1 min |
| Heaviest hour of rain | 89.3 mm |
| Flood model run time | 2329 s |

## Checks against what happened

- Storm-day flood reports in the area: 10; water >= 10 cm within 100 m of 90% of them, vs 65% of random points (any day).
- Segments flagged impassable are 3.15x as likely as an average segment to have a report within 200 m.
- MassDOT repeating flood sites in the area: 4; 2 have a segment within 150 m at P >= 0.5 (share of all segments at P >= 0.5: 1.5%).

## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 1.00 | (unnamed) | Leominster | 1.29 m of water at peak; over 30 cm for 21.1 h; 30 cm reached 5.6 h into the storm; worst hour 84 mm (45% of the storm); water beside the road 0.04 m above its crest (design freeboard 0.30 m; P 0.99); a culvert within 100 m is overtopped |
| 2 | 1.00 | Depot Street | Fitchburg | 0.92 m of water at peak; over 30 cm for 33.7 h; 30 cm reached 0.1 h into the storm; worst hour 31 mm (31% of the storm); runoff beside / along the road at 1.6 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.73); a culvert within 100 m is overtopped |
| 3 | 1.00 | Route 12 | Leominster | 0.81 m of water at peak; over 30 cm for 8.4 h; 30 cm reached 5.8 h into the storm; worst hour 78 mm (45% of the storm); water beside the road 0.04 m above its crest (design freeboard 0.30 m; P 0.99); runoff beside / along the road at 0.7 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.20); a culvert within 100 m is overtopped |
| 4 | 1.00 | Water Street | Leominster | 1.29 m of water at peak; over 30 cm for 21.3 h; 30 cm reached 5.6 h into the storm; worst hour 85 mm (45% of the storm); a culvert within 100 m is overtopped |
| 5 | 1.00 | Litchfield Street | Leominster | 1.49 m of water at peak; over 30 cm for 12.7 h; 30 cm reached 6.0 h into the storm; worst hour 66 mm (43% of the storm); a culvert within 100 m is overtopped |
| 6 | 1.00 | Route 117 | Leominster | 1.02 m of water at peak; over 30 cm for 9.2 h; 30 cm reached 6.3 h into the storm; worst hour 58 mm (41% of the storm); cut off from hospitals |
| 7 | 1.00 | Route 117 | Leominster | 1.02 m of water at peak; over 30 cm for 9.2 h; 30 cm reached 6.3 h into the storm; worst hour 61 mm (42% of the storm); water beside the road 0.10 m below its crest (design freeboard 0.30 m; P 0.91); runoff beside / along the road at 0.8 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.34); a culvert within 100 m is overtopped |
| 8 | 1.00 | Merriam Avenue | Leominster | 0.72 m of water at peak; over 30 cm for 4.4 h; 30 cm reached 5.5 h into the storm; worst hour 84 mm (46% of the storm); water beside the road 0.53 m above its crest (design freeboard 0.30 m; P 1.00); fast water: depth x speed 0.22 m2/s (small cars unstable from 0.3); runoff beside / along the road at 1.1 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.61); road sag 0.4 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 81 mm; catchment 13.0 ha) (P 1.00) |
| 9 | 1.00 | Route 140 | Princeton | 0.73 m of water at peak; over 30 cm for 8.4 h; 30 cm reached 7.0 h into the storm; worst hour 42 mm (30% of the storm); water beside the road 0.20 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 1.4 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.54); a culvert within 100 m is overtopped |
| 10 | 1.00 | Kingman Drive | Leominster | 1.13 m of water at peak; over 30 cm for 13.1 h; 30 cm reached 5.4 h into the storm; worst hour 85 mm (46% of the storm); water beside the road 0.47 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 1.5 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.78); a culvert within 100 m is overtopped |
| 11 | 1.00 | Adams Street | Leominster | 1.21 m of water at peak; over 30 cm for 25.5 h; 30 cm reached 5.3 h into the storm; worst hour 87 mm (45% of the storm); water beside the road 0.38 m above its crest (design freeboard 0.30 m; P 1.00); a culvert within 100 m is overtopped |
| 12 | 1.00 | Litchfield Street | Leominster | 0.88 m of water at peak; over 30 cm for 8.7 h; 30 cm reached 5.7 h into the storm; worst hour 73 mm (45% of the storm); runoff beside / along the road at 0.9 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.49) |
| 13 | 1.00 | Depot Square | Leominster | 1.29 m of water at peak; over 30 cm for 21.1 h; 30 cm reached 5.6 h into the storm; worst hour 85 mm (45% of the storm); water beside the road 0.01 m above its crest (design freeboard 0.30 m; P 0.98); a culvert within 100 m is overtopped |
| 14 | 1.00 | Commercial Road | Leominster | 1.29 m of water at peak; over 30 cm for 10.2 h; 30 cm reached 6.2 h into the storm; worst hour 77 mm (44% of the storm); water beside the road 0.16 m above its crest (design freeboard 0.30 m; P 1.00); a culvert within 100 m is overtopped |
| 15 | 1.00 | Pleasant Street | Leominster | 0.63 m of water at peak; over 30 cm for 2.8 h; 30 cm reached 5.5 h into the storm; worst hour 87 mm (45% of the storm); runoff beside / along the road at 0.6 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.10); a culvert within 100 m is overtopped |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
