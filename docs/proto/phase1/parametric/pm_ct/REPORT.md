# Road-closure prototype: sep2023_loss_pm_ct

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on CPU (OpenMP)), 20 m grid, storm from 2023-09-11T16:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 4,542 |
| Expected closures (sum of probabilities) | 134.5 |
| Segments with closure probability >= 50% | 111 (76.9 km) |
| Further segments that may close (stream reaches the road crest) | 136 (84.8 km) |
| Culverts overtopped / surcharged | 139 / 18 of 616 |
| Road segments cut off from hospitals | 684 |
| Worst added trip time to a hospital | 24.1 min |
| Heaviest hour of rain | 89.3 mm |
| Flood model run time | 2571 s |

## Checks against what happened

- Storm-day flood reports in the area: 10; water >= 10 cm within 100 m of 90% of them, vs 67% of random points (any day).
- Segments flagged impassable are 2.89x as likely as an average segment to have a report within 200 m.
- MassDOT repeating flood sites in the area: 4; 2 have a segment within 150 m at P >= 0.5 (share of all segments at P >= 0.5: 2.4%).

## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 1.00 | Route 2 | Leominster | 0.70 m of water at peak; over 30 cm for 29.5 h; 30 cm reached 7.0 h into the storm; worst hour 58 mm (51% of the storm); road sag 1.5 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 55 mm; catchment 19.0 ha) (P 0.13); a culvert within 100 m is overtopped |
| 2 | 1.00 | Route 2 | Fitchburg | 1.01 m of water at peak; over 30 cm for 29.5 h; 30 cm reached 7.0 h into the storm; worst hour 52 mm (50% of the storm); cut off from hospitals |
| 3 | 1.00 | Route 2 | Fitchburg | 1.01 m of water at peak; over 30 cm for 29.5 h; 30 cm reached 7.0 h into the storm; worst hour 51 mm (50% of the storm); a culvert within 100 m is overtopped |
| 4 | 1.00 | Route 2 | Fitchburg | 1.01 m of water at peak; over 30 cm for 29.5 h; 30 cm reached 7.0 h into the storm; worst hour 51 mm (50% of the storm); a culvert within 100 m is overtopped |
| 5 | 1.00 | Route 2 | Leominster | 0.70 m of water at peak; over 30 cm for 29.5 h; 30 cm reached 7.0 h into the storm; worst hour 59 mm (50% of the storm); runoff beside / along the road at 0.7 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.11); road sag 1.5 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 55 mm; catchment 19.0 ha) (P 0.13); a culvert within 100 m is overtopped |
| 6 | 1.00 | Route 2 | Leominster | 8.49 m of water at peak; over 30 cm for 31.0 h; 30 cm reached 5.5 h into the storm; worst hour 67 mm (42% of the storm); runoff beside / along the road at 2.0 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.60); a culvert within 100 m is overtopped |
| 7 | 1.00 | (unnamed) | Leominster | 1.55 m of water at peak; over 30 cm for 27.0 h; 30 cm reached 5.5 h into the storm; worst hour 84 mm (45% of the storm); water beside the road 0.04 m above its crest (design freeboard 0.30 m; P 0.99); a culvert within 100 m is overtopped |
| 8 | 1.00 | Depot Street | Fitchburg | 1.05 m of water at peak; over 30 cm for 34.0 h; 30 cm reached 0.5 h into the storm; worst hour 31 mm (31% of the storm); runoff beside / along the road at 1.6 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.73); a culvert within 100 m is overtopped |
| 9 | 1.00 | Water Street | Leominster | 1.56 m of water at peak; over 30 cm for 27.5 h; 30 cm reached 5.5 h into the storm; worst hour 85 mm (45% of the storm); a culvert within 100 m is overtopped |
| 10 | 1.00 | Litchfield Street | Leominster | 1.64 m of water at peak; over 30 cm for 15.0 h; 30 cm reached 6.0 h into the storm; worst hour 66 mm (43% of the storm); a culvert within 100 m is overtopped |
| 11 | 1.00 | Route 12 | Leominster | 0.90 m of water at peak; over 30 cm for 8.5 h; 30 cm reached 6.0 h into the storm; worst hour 78 mm (45% of the storm); water beside the road 0.10 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 0.9 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.20); a culvert within 100 m is overtopped |
| 12 | 1.00 | Route 117 | Leominster | 1.06 m of water at peak; over 30 cm for 9.5 h; 30 cm reached 6.5 h into the storm; worst hour 58 mm (41% of the storm); cut off from hospitals |
| 13 | 1.00 | Route 117 | Leominster | 1.06 m of water at peak; over 30 cm for 9.5 h; 30 cm reached 6.5 h into the storm; worst hour 61 mm (42% of the storm); water beside the road 0.10 m below its crest (design freeboard 0.30 m; P 0.91); runoff beside / along the road at 0.8 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.33); a culvert within 100 m is overtopped |
| 14 | 1.00 | Route 12 | Leominster | 0.81 m of water at peak; over 30 cm for 5.5 h; 30 cm reached 6.0 h into the storm; worst hour 85 mm (45% of the storm); water beside the road 0.41 m below its crest (design freeboard 0.30 m; P 0.23); a culvert within 100 m is overtopped |
| 15 | 1.00 | Merriam Avenue | Leominster | 0.72 m of water at peak; over 30 cm for 4.5 h; 30 cm reached 5.5 h into the storm; worst hour 84 mm (46% of the storm); water beside the road 0.53 m above its crest (design freeboard 0.30 m; P 1.00); fast water: depth x speed 0.22 m2/s (small cars unstable from 0.3); runoff beside / along the road at 1.1 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.61); road sag 0.4 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 81 mm; catchment 13.0 ha) (P 1.00) |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
