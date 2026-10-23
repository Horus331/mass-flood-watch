# Road-closure prototype: sep2023_loss_sep2023_leominster_20m

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on CPU (OpenMP)), 20 m grid, storm from 2023-09-11T16:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 4,542 |
| Expected closures (sum of probabilities) | 67.3 |
| Segments with closure probability >= 50% | 47 (34.9 km) |
| Further segments that may close (stream reaches the road crest) | 61 (34.3 km) |
| Culverts overtopped / surcharged | 74 / 0 of 616 |
| Road segments cut off from hospitals | 377 |
| Worst added trip time to a hospital | 20.4 min |
| Heaviest hour of rain | 89.3 mm |
| Flood model run time | 2689 s |

## Checks against what happened

- Storm-day flood reports in the area: 10; water >= 10 cm within 100 m of 60% of them, vs 57% of random points (any day).
- Segments flagged impassable are 3.61x as likely as an average segment to have a report within 200 m.
- MassDOT repeating flood sites in the area: 4; 1 have a segment within 150 m at P >= 0.5 (share of all segments at P >= 0.5: 1.0%).

## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 1.00 | Route 2 | Leominster | 4.91 m of water at peak; over 30 cm for 30.5 h; 30 cm reached 6.0 h into the storm; worst hour 67 mm (42% of the storm); runoff beside / along the road at 2.3 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.39); a culvert within 100 m is overtopped |
| 2 | 1.00 | (unnamed) | Leominster | 1.25 m of water at peak; over 30 cm for 20.0 h; 30 cm reached 6.0 h into the storm; worst hour 84 mm (45% of the storm); water beside the road 0.15 m below its crest (design freeboard 0.30 m; P 0.84); a culvert within 100 m is overtopped |
| 3 | 1.00 | Litchfield Street | Leominster | 1.25 m of water at peak; over 30 cm for 14.0 h; 30 cm reached 6.5 h into the storm; worst hour 66 mm (43% of the storm); a culvert within 100 m is overtopped |
| 4 | 1.00 | Water Street | Leominster | 1.25 m of water at peak; over 30 cm for 20.0 h; 30 cm reached 6.0 h into the storm; worst hour 85 mm (45% of the storm); a culvert within 100 m is overtopped |
| 5 | 1.00 | Route 12 | Leominster | 0.71 m of water at peak; over 30 cm for 7.5 h; 30 cm reached 7.0 h into the storm; worst hour 78 mm (45% of the storm); a culvert within 100 m is overtopped |
| 6 | 1.00 | Route 117 | Leominster | 0.82 m of water at peak; over 30 cm for 8.5 h; 30 cm reached 7.0 h into the storm; worst hour 58 mm (41% of the storm); cut off from hospitals |
| 7 | 1.00 | Route 117 | Leominster | 0.82 m of water at peak; over 30 cm for 8.5 h; 30 cm reached 7.0 h into the storm; worst hour 61 mm (42% of the storm); runoff beside / along the road at 0.4 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.13); a culvert within 100 m is overtopped |
| 8 | 1.00 | Litchfield Street | Leominster | 1.07 m of water at peak; over 30 cm for 11.0 h; 30 cm reached 6.0 h into the storm; worst hour 73 mm (45% of the storm) |
| 9 | 1.00 | Depot Square | Leominster | 1.25 m of water at peak; over 30 cm for 20.0 h; 30 cm reached 6.0 h into the storm; worst hour 85 mm (45% of the storm); a culvert within 100 m is overtopped |
| 10 | 1.00 | Kingman Drive | Leominster | 0.90 m of water at peak; over 30 cm for 8.0 h; 30 cm reached 6.0 h into the storm; worst hour 85 mm (46% of the storm); water beside the road 0.41 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 1.7 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.72); a culvert within 100 m is overtopped |
| 11 | 1.00 | Exchange Street | Leominster | 1.01 m of water at peak; over 30 cm for 7.0 h; 30 cm reached 5.5 h into the storm; worst hour 86 mm (46% of the storm); water beside the road 0.82 m above its crest (design freeboard 0.30 m; P 1.00); fast water: depth x speed 0.48 m2/s (small cars unstable from 0.3); runoff beside / along the road at 3.0 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.99); culvert (Unknown): headwater 2.67 m vs road crest 2.96 m, 27.6 m3/s |
| 12 | 1.00 | (unnamed) | Leominster | 1.01 m of water at peak; over 30 cm for 7.0 h; 30 cm reached 5.5 h into the storm; worst hour 84 mm (47% of the storm); culvert (Unknown): headwater 2.58 m vs road crest 3.05 m, 28.4 m3/s |
| 13 | 1.00 | Constitution Drive | Leominster | 0.86 m of water at peak; over 30 cm for 6.0 h; 30 cm reached 5.5 h into the storm; worst hour 82 mm (47% of the storm) |
| 14 | 1.00 | Commercial Road | Leominster | 0.83 m of water at peak; over 30 cm for 6.0 h; 30 cm reached 7.0 h into the storm; worst hour 77 mm (44% of the storm); water beside the road 0.10 m above its crest (design freeboard 0.30 m; P 1.00); a culvert within 100 m is overtopped |
| 15 | 1.00 | Decicco Drive | Leominster | 0.73 m of water at peak; over 30 cm for 5.5 h; 30 cm reached 6.0 h into the storm; worst hour 71 mm (44% of the storm); culvert (Fall Brook): headwater 9.42 m vs road crest 2.44 m, 25% blocked, 20.7 m3/s |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
