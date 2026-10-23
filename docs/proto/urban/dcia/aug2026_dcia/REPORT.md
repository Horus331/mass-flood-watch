# Road-closure prototype: aug2026_loss_aug2026_dcia

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on CPU (OpenMP)), 20 m grid, storm from 2026-08-03T04:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 4,462 |
| Expected closures (sum of probabilities) | 104.9 |
| Segments with closure probability >= 50% | 81 (50.6 km) |
| Further segments that may close (stream reaches the road crest) | 129 (82.1 km) |
| Culverts overtopped / surcharged | 127 / 0 of 616 |
| Road segments cut off from hospitals | 585 |
| Worst added trip time to a hospital | 24.8 min |
| Heaviest hour of rain | 46.0 mm |
| Flood model run time | 766 s |

## Checks against what happened

- Storm-day flood reports in the area: 3; water >= 10 cm within 100 m of 67% of them, vs 62% of random points (any day).
- Segments flagged impassable are 2.51x as likely as an average segment to have a report within 200 m.
- MassDOT repeating flood sites in the area: 4; 1 have a segment within 150 m at P >= 0.5 (share of all segments at P >= 0.5: 1.8%).

## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 1.00 | Route 2 | Leominster | 1.83 m of water at peak; over 30 cm for 11.0 h; 30 cm reached 7.5 h into the storm; worst hour 26 mm (40% of the storm); runoff beside / along the road at 4.6 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.14); a culvert within 100 m is overtopped |
| 2 | 1.00 | (unnamed) | Leominster | 1.32 m of water at peak; over 30 cm for 10.5 h; 30 cm reached 8.0 h into the storm; worst hour 32 mm (40% of the storm); a culvert within 100 m is overtopped |
| 3 | 1.00 | Depot Street | Fitchburg | 1.12 m of water at peak; over 30 cm for 14.0 h; 30 cm reached 0.5 h into the storm; worst hour 25 mm (30% of the storm); runoff beside / along the road at 4.1 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.79); a culvert within 100 m is overtopped |
| 4 | 1.00 | Litchfield Street | Leominster | 0.84 m of water at peak; over 30 cm for 9.5 h; 30 cm reached 9.0 h into the storm; worst hour 24 mm (37% of the storm); a culvert within 100 m is overtopped |
| 5 | 1.00 | Water Street | Leominster | 1.32 m of water at peak; over 30 cm for 10.5 h; 30 cm reached 8.0 h into the storm; worst hour 30 mm (39% of the storm); a culvert within 100 m is overtopped |
| 6 | 1.00 | Kingman Drive | Leominster | 1.02 m of water at peak; over 30 cm for 11.0 h; 30 cm reached 7.0 h into the storm; worst hour 38 mm (41% of the storm); water beside the road 0.41 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 5.0 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.94); a culvert within 100 m is overtopped |
| 7 | 1.00 | Litchfield Street | Leominster | 0.72 m of water at peak; over 30 cm for 7.5 h; 30 cm reached 9.0 h into the storm; worst hour 28 mm (42% of the storm) |
| 8 | 1.00 | Depot Square | Leominster | 1.32 m of water at peak; over 30 cm for 10.5 h; 30 cm reached 8.0 h into the storm; worst hour 30 mm (39% of the storm); a culvert within 100 m is overtopped |
| 9 | 1.00 | Commercial Road | Leominster | 1.11 m of water at peak; over 30 cm for 7.5 h; 30 cm reached 9.0 h into the storm; worst hour 27 mm (40% of the storm); water beside the road 0.10 m below its crest (design freeboard 0.30 m; P 0.91); a culvert within 100 m is overtopped |
| 10 | 1.00 | Exchange Street | Leominster | 0.97 m of water at peak; over 30 cm for 5.5 h; 30 cm reached 7.0 h into the storm; worst hour 36 mm (40% of the storm); water beside the road 0.81 m above its crest (design freeboard 0.30 m; P 1.00); fast water: depth x speed 0.42 m2/s (small cars unstable from 0.3); runoff beside / along the road at 5.0 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 1.00); culvert (Unknown): headwater 2.53 m vs road crest 2.96 m, 25.5 m3/s |
| 11 | 1.00 | Sanborn Street | Fitchburg | 0.69 m of water at peak; over 30 cm for 5.5 h; 30 cm reached 6.5 h into the storm; worst hour 24 mm (29% of the storm); overtopping at 18.2 m/s at a stream crossing (grass-covered fill erodes from ~1.5 m/s); runoff beside / along the road at 4.0 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.80); a culvert within 100 m is overtopped |
| 12 | 1.00 | (unnamed) | Leominster | 0.98 m of water at peak; over 30 cm for 5.5 h; 30 cm reached 7.0 h into the storm; worst hour 36 mm (40% of the storm); culvert (Unknown): headwater 2.44 m vs road crest 3.05 m, 26.2 m3/s |
| 13 | 1.00 | Constitution Drive | Leominster | 0.84 m of water at peak; over 30 cm for 4.5 h; 30 cm reached 7.0 h into the storm; worst hour 36 mm (40% of the storm) |
| 14 | 1.00 | Sack Boulevard | Leominster | 0.73 m of water at peak; over 30 cm for 2.5 h; 30 cm reached 9.0 h into the storm; worst hour 27 mm (40% of the storm); water beside the road 0.64 m above its crest (design freeboard 0.30 m; P 1.00); fast water: depth x speed 0.25 m2/s (small cars unstable from 0.3); runoff beside / along the road at 1.9 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.92) |
| 15 | 1.00 | Bullard Road | Princeton | 0.63 m of water at peak; over 30 cm for 4.0 h; 30 cm reached 8.5 h into the storm; worst hour 33 mm (42% of the storm); water beside the road 0.05 m above its crest (design freeboard 0.30 m; P 0.99); runoff beside / along the road at 1.6 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.63); a culvert within 100 m is overtopped |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
