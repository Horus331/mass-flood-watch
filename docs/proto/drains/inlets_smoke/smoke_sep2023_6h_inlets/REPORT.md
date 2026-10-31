# Road-closure prototype: sep2023_loss_smoke_sep2023_6h_inlets

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on CPU (OpenMP)), 20 m grid, storm from 2023-09-11T16:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 4,542 |
| Expected closures (sum of probabilities) | 38.2 |
| Segments with closure probability >= 50% | 24 (16.4 km) |
| Further segments that may close (stream reaches the road crest) | 33 (22.6 km) |
| Culverts overtopped / surcharged | 42 / 1 of 616 |
| Road segments cut off from hospitals | 271 |
| Worst added trip time to a hospital | 14.8 min |
| Heaviest hour of rain | 89.3 mm |
| Flood model run time | 371 s |

## Checks against what happened

- Storm-day flood reports in the area: 10; water >= 10 cm within 100 m of 20% of them, vs 40% of random points (any day).
- Segments flagged impassable are 2.15x as likely as an average segment to have a report within 200 m.
- MassDOT repeating flood sites in the area: 4; 0 have a segment within 150 m at P >= 0.5 (share of all segments at P >= 0.5: 0.5%).

## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 1.00 | Route 2 | Leominster | 0.88 m of water at peak; over 30 cm for 0.5 h; 30 cm reached 6.0 h into the storm; worst hour 67 mm (64% of the storm); a culvert within 100 m is overtopped |
| 2 | 1.00 | Pleasant Street | Leominster | 0.69 m of water at peak; over 30 cm for 1.0 h; 30 cm reached 5.5 h into the storm; worst hour 76 mm (64% of the storm); culvert (Wilder Brook): headwater 13.15 m vs road crest 3.05 m, 11.3 m3/s |
| 3 | 1.00 | Pleasant Street | Leominster | 0.69 m of water at peak; over 30 cm for 1.0 h; 30 cm reached 5.5 h into the storm; worst hour 87 mm (62% of the storm); a culvert within 100 m is overtopped |
| 4 | 1.00 | Pond Street | Leominster | 0.70 m of water at peak; over 30 cm for 1.0 h; 30 cm reached 5.5 h into the storm; worst hour 87 mm (62% of the storm); culvert (Reservoir Brook): headwater 56.95 m vs road crest 2.53 m, 14.0 m3/s |
| 5 | 1.00 | Kingman Drive | Leominster | 0.90 m of water at peak; over 30 cm for 0.5 h; 30 cm reached 6.0 h into the storm; worst hour 85 mm (63% of the storm); water beside the road 0.44 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 1.7 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.79); a culvert within 100 m is overtopped |
| 6 | 1.00 | Exchange Street | Leominster | 1.18 m of water at peak; over 30 cm for 1.0 h; 30 cm reached 5.5 h into the storm; worst hour 86 mm (63% of the storm); water beside the road 0.89 m above its crest (design freeboard 0.30 m; P 1.00); fast water: depth x speed 0.65 m2/s (small cars unstable from 0.3); runoff beside / along the road at 3.2 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.99); culvert (Unknown): headwater 4.11 m vs road crest 2.96 m, 42.2 m3/s |
| 7 | 1.00 | Constitution Drive | Leominster | 1.04 m of water at peak; over 30 cm for 1.0 h; 30 cm reached 5.5 h into the storm; worst hour 82 mm (66% of the storm); a culvert within 100 m is overtopped |
| 8 | 1.00 | (unnamed) | Leominster | 1.19 m of water at peak; over 30 cm for 1.0 h; 30 cm reached 5.5 h into the storm; worst hour 84 mm (64% of the storm); culvert (Unknown): headwater 3.59 m vs road crest 3.05 m, 40.7 m3/s |
| 9 | 1.00 | Decicco Drive | Leominster | 0.69 m of water at peak; over 30 cm for 0.5 h; 30 cm reached 6.0 h into the storm; worst hour 71 mm (67% of the storm); runoff beside / along the road at 0.8 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.35); culvert (Fall Brook): headwater 8.40 m vs road crest 2.44 m, 25% blocked, 19.3 m3/s |
| 10 | 0.99 | Theresa Avenue | Leominster | 0.56 m of water at peak; over 30 cm for 0.5 h; 30 cm reached 6.0 h into the storm; worst hour 80 mm (63% of the storm); a culvert within 100 m is overtopped |
| 11 | 0.99 | Elm Street | Leominster | 0.54 m of water at peak; over 30 cm for 1.0 h; 30 cm reached 5.5 h into the storm; worst hour 79 mm (65% of the storm); water beside the road 1.07 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 1.2 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.65); a culvert within 100 m is overtopped |
| 12 | 0.98 | Granite Street | Leominster | 0.52 m of water at peak; over 30 cm for 0.5 h; 30 cm reached 6.0 h into the storm; worst hour 80 mm (66% of the storm); water beside the road 0.03 m below its crest (design freeboard 0.30 m; P 0.96); runoff beside / along the road at 1.1 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.54); culvert (Unknown): headwater 10.48 m vs road crest 2.56 m, 7.3 m3/s |
| 13 | 0.95 | Wachusett Street | Leominster | 0.47 m of water at peak; over 30 cm for 1.0 h; 30 cm reached 5.5 h into the storm; worst hour 74 mm (63% of the storm); runoff beside / along the road at 1.2 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.58); culvert (Fall Brook): headwater 47.71 m vs road crest 1.83 m, 12.5 m3/s |
| 14 | 0.92 | Litchfield Street | Leominster | 0.44 m of water at peak; over 30 cm for 0.5 h; 30 cm reached 6.0 h into the storm; worst hour 73 mm (67% of the storm) |
| 15 | 0.91 | Depot Street | Fitchburg | 0.43 m of water at peak; over 30 cm for 3.0 h; 30 cm reached 0.5 h into the storm; worst hour 31 mm (54% of the storm); runoff beside / along the road at 0.7 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.24); a culvert within 100 m is overtopped |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
