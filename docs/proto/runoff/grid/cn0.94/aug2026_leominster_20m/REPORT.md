# Road-closure prototype: aug2026_loss_aug2026_leominster_20m

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on CPU (OpenMP)), 20 m grid, storm from 2026-08-03T04:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 4,542 |
| Expected closures (sum of probabilities) | 107.6 |
| Segments with closure probability >= 50% | 91 (56.0 km) |
| Further segments that may close (stream reaches the road crest) | 126 (83.4 km) |
| Culverts overtopped / surcharged | 122 / 0 of 616 |
| Road segments cut off from hospitals | 533 |
| Worst added trip time to a hospital | 25.0 min |
| Heaviest hour of rain | 46.0 mm |
| Flood model run time | 1632 s |

## Checks against what happened

- Storm-day flood reports in the area: 3; water >= 10 cm within 100 m of 67% of them, vs 60% of random points (any day).
- Segments flagged impassable are 2.62x as likely as an average segment to have a report within 200 m.
- MassDOT repeating flood sites in the area: 4; 1 have a segment within 150 m at P >= 0.5 (share of all segments at P >= 0.5: 2.0%).

## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 1.00 | Route 2 | Leominster | 1.54 m of water at peak; over 30 cm for 10.0 h; 30 cm reached 8.5 h into the storm; worst hour 26 mm (40% of the storm); a culvert within 100 m is overtopped |
| 2 | 1.00 | (unnamed) | Leominster | 1.26 m of water at peak; over 30 cm for 10.0 h; 30 cm reached 8.5 h into the storm; worst hour 32 mm (40% of the storm); water beside the road 0.23 m below its crest (design freeboard 0.30 m; P 0.68); a culvert within 100 m is overtopped |
| 3 | 1.00 | Depot Street | Fitchburg | 1.17 m of water at peak; over 30 cm for 14.0 h; 30 cm reached 0.5 h into the storm; worst hour 25 mm (30% of the storm); runoff beside / along the road at 0.8 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.32); a culvert within 100 m is overtopped |
| 4 | 1.00 | Litchfield Street | Leominster | 0.76 m of water at peak; over 30 cm for 9.0 h; 30 cm reached 9.5 h into the storm; worst hour 24 mm (37% of the storm); a culvert within 100 m is overtopped |
| 5 | 1.00 | Water Street | Leominster | 1.26 m of water at peak; over 30 cm for 10.0 h; 30 cm reached 8.5 h into the storm; worst hour 30 mm (39% of the storm); a culvert within 100 m is overtopped |
| 6 | 1.00 | Kingman Drive | Leominster | 0.97 m of water at peak; over 30 cm for 10.5 h; 30 cm reached 8.0 h into the storm; worst hour 38 mm (41% of the storm); water beside the road 0.40 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 1.7 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.70); a culvert within 100 m is overtopped |
| 7 | 1.00 | Depot Square | Leominster | 1.26 m of water at peak; over 30 cm for 10.0 h; 30 cm reached 8.5 h into the storm; worst hour 30 mm (39% of the storm); a culvert within 100 m is overtopped |
| 8 | 1.00 | Commercial Road | Leominster | 1.02 m of water at peak; over 30 cm for 7.0 h; 30 cm reached 9.5 h into the storm; worst hour 27 mm (40% of the storm); a culvert within 100 m is overtopped |
| 9 | 1.00 | Exchange Street | Leominster | 0.97 m of water at peak; over 30 cm for 5.5 h; 30 cm reached 7.5 h into the storm; worst hour 36 mm (40% of the storm); water beside the road 0.81 m above its crest (design freeboard 0.30 m; P 1.00); fast water: depth x speed 0.44 m2/s (small cars unstable from 0.3); runoff beside / along the road at 3.0 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.99); culvert (Unknown): headwater 2.53 m vs road crest 2.96 m, 25.5 m3/s |
| 10 | 1.00 | (unnamed) | Leominster | 0.97 m of water at peak; over 30 cm for 5.5 h; 30 cm reached 7.5 h into the storm; worst hour 36 mm (40% of the storm); culvert (Unknown): headwater 2.44 m vs road crest 3.05 m, 26.2 m3/s |
| 11 | 1.00 | Sanborn Street | Fitchburg | 0.71 m of water at peak; over 30 cm for 5.0 h; 30 cm reached 7.5 h into the storm; worst hour 24 mm (29% of the storm); overtopping at 4.2 m/s at a stream crossing (grass-covered fill erodes from ~1.5 m/s); runoff beside / along the road at 1.7 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.76); a culvert within 100 m is overtopped |
| 12 | 1.00 | Constitution Drive | Leominster | 0.83 m of water at peak; over 30 cm for 4.5 h; 30 cm reached 7.5 h into the storm; worst hour 36 mm (40% of the storm) |
| 13 | 1.00 | Sack Boulevard | Leominster | 0.64 m of water at peak; over 30 cm for 2.0 h; 30 cm reached 9.5 h into the storm; worst hour 27 mm (40% of the storm); water beside the road 0.55 m above its crest (design freeboard 0.30 m; P 1.00); fast water: depth x speed 0.20 m2/s (small cars unstable from 0.3) |
| 14 | 1.00 | Houghton Road | Princeton | 0.72 m of water at peak; over 30 cm for 4.0 h; 30 cm reached 8.5 h into the storm; worst hour 36 mm (42% of the storm); water beside the road 0.54 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 0.8 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.34); a culvert within 100 m is overtopped |
| 15 | 1.00 | Bullard Road | Princeton | 0.66 m of water at peak; over 30 cm for 4.0 h; 30 cm reached 8.5 h into the storm; worst hour 33 mm (42% of the storm); water beside the road 0.07 m above its crest (design freeboard 0.30 m; P 0.99); runoff beside / along the road at 0.6 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.14); a culvert within 100 m is overtopped |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
