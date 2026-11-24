# Road-closure prototype: sep2023_loss_ARC1

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on CPU (OpenMP)), 20 m grid, storm from 2023-09-11T16:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 4,542 |
| Expected closures (sum of probabilities) | 54.8 |
| Segments with closure probability >= 50% | 41 (29.2 km) |
| Further segments that may close (stream reaches the road crest) | 54 (32.0 km) |
| Culverts overtopped / surcharged | 54 / 0 of 616 |
| Road segments cut off from hospitals | 325 |
| Worst added trip time to a hospital | 18.0 min |
| Heaviest hour of rain | 89.3 mm |
| Flood model run time | 2097 s |

## Checks against what happened

- Storm-day flood reports in the area: 10; water >= 10 cm within 100 m of 60% of them, vs 53% of random points (any day).
- Segments flagged impassable are 4.1x as likely as an average segment to have a report within 200 m.
- MassDOT repeating flood sites in the area: 4; 2 have a segment within 150 m at P >= 0.5 (share of all segments at P >= 0.5: 0.9%).

## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 1.00 | (unnamed) | Leominster | 0.98 m of water at peak; over 30 cm for 15.0 h; 30 cm reached 5.8 h into the storm; worst hour 84 mm (45% of the storm); water beside the road 0.15 m below its crest (design freeboard 0.30 m; P 0.84); a culvert within 100 m is overtopped |
| 2 | 1.00 | Litchfield Street | Leominster | 1.07 m of water at peak; over 30 cm for 12.0 h; 30 cm reached 6.4 h into the storm; worst hour 66 mm (43% of the storm); a culvert within 100 m is overtopped |
| 3 | 1.00 | Route 117 | Leominster | 0.78 m of water at peak; over 30 cm for 8.3 h; 30 cm reached 6.8 h into the storm; worst hour 58 mm (41% of the storm); cut off from hospitals |
| 4 | 1.00 | Route 117 | Leominster | 0.78 m of water at peak; over 30 cm for 8.3 h; 30 cm reached 6.8 h into the storm; worst hour 61 mm (42% of the storm); runoff beside / along the road at 0.4 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.13); a culvert within 100 m is overtopped |
| 5 | 1.00 | Water Street | Leominster | 0.98 m of water at peak; over 30 cm for 15.2 h; 30 cm reached 5.8 h into the storm; worst hour 85 mm (45% of the storm); a culvert within 100 m is overtopped |
| 6 | 1.00 | Kingman Drive | Leominster | 0.88 m of water at peak; over 30 cm for 8.2 h; 30 cm reached 5.7 h into the storm; worst hour 85 mm (46% of the storm); water beside the road 0.40 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 1.3 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.67); a culvert within 100 m is overtopped |
| 7 | 1.00 | Litchfield Street | Leominster | 0.66 m of water at peak; over 30 cm for 7.6 h; 30 cm reached 6.4 h into the storm; worst hour 73 mm (45% of the storm); runoff beside / along the road at 1.0 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.29) |
| 8 | 1.00 | Adams Street | Leominster | 0.86 m of water at peak; over 30 cm for 18.8 h; 30 cm reached 5.5 h into the storm; worst hour 87 mm (45% of the storm); water beside the road 0.09 m above its crest (design freeboard 0.30 m; P 0.99); a culvert within 100 m is overtopped |
| 9 | 1.00 | Depot Square | Leominster | 0.97 m of water at peak; over 30 cm for 15.1 h; 30 cm reached 5.8 h into the storm; worst hour 85 mm (45% of the storm); a culvert within 100 m is overtopped |
| 10 | 1.00 | Commercial Road | Leominster | 0.85 m of water at peak; over 30 cm for 5.8 h; 30 cm reached 6.8 h into the storm; worst hour 77 mm (44% of the storm); water beside the road 0.10 m above its crest (design freeboard 0.30 m; P 1.00); a culvert within 100 m is overtopped |
| 11 | 1.00 | Exchange Street | Leominster | 0.75 m of water at peak; over 30 cm for 5.8 h; 30 cm reached 5.5 h into the storm; worst hour 86 mm (46% of the storm); water beside the road 0.77 m above its crest (design freeboard 0.30 m; P 1.00); fast water: depth x speed 0.46 m2/s (small cars unstable from 0.3); runoff beside / along the road at 2.5 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.98); culvert (Unknown): headwater 2.75 m vs road crest 2.96 m, 28.9 m3/s |
| 12 | 1.00 | Constitution Drive | Leominster | 0.70 m of water at peak; over 30 cm for 5.3 h; 30 cm reached 5.5 h into the storm; worst hour 82 mm (47% of the storm) |
| 13 | 1.00 | (unnamed) | Leominster | 0.66 m of water at peak; over 30 cm for 4.9 h; 30 cm reached 5.7 h into the storm; worst hour 84 mm (47% of the storm); culvert (Unknown): headwater 2.64 m vs road crest 3.05 m, 29.5 m3/s |
| 14 | 1.00 | Route 12 | Leominster | 0.62 m of water at peak; over 30 cm for 7.3 h; 30 cm reached 6.6 h into the storm; worst hour 78 mm (45% of the storm); a culvert within 100 m is overtopped |
| 15 | 1.00 | Decicco Drive | Leominster | 0.62 m of water at peak; over 30 cm for 5.0 h; 30 cm reached 5.8 h into the storm; worst hour 71 mm (44% of the storm); culvert (Fall Brook): headwater 9.91 m vs road crest 2.44 m, 25% blocked, 21.3 m3/s |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
