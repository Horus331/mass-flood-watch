# Road-closure prototype: aug2026_proto_aug2026_leominster_20m

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on GPU (cuda)), 20 m grid, storm from 2026-08-03T04:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 4,462 |
| Expected closures (sum of probabilities) | 122.2 |
| Segments with closure probability >= 50% | 98 (65.5 km) |
| Further segments that may close (stream reaches the road crest) | 151 (97.3 km) |
| Culverts overtopped / surcharged | 145 / 1 of 616 |
| Road segments cut off from hospitals | 626 |
| Worst added trip time to a hospital | 25.6 min |
| Heaviest hour of rain | 46.0 mm |
| Flood model run time | 45 s |

## Checks against what happened

- Storm-day flood reports in the area: 3; water >= 10 cm within 100 m of 67% of them, vs 64% of random points (any day).
- Segments flagged impassable are 3.46x as likely as an average segment to have a report within 200 m.
- MassDOT repeating flood sites in the area: 4; 1 have a segment within 150 m at P >= 0.5 (share of all segments at P >= 0.5: 2.2%).

## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 1.00 | Route 2 | Leominster | 2.46 m of water at peak; over 30 cm for 18.0 h; 30 cm reached 0.5 h into the storm; worst hour 26 mm (40% of the storm); a culvert within 100 m is overtopped |
| 2 | 1.00 | Route 2 | Fitchburg | 1.00 m of water at peak; over 30 cm for 11.5 h; 30 cm reached 0.5 h into the storm; worst hour 40 mm (40% of the storm); water beside the road 0.43 m above its crest (design freeboard 0.30 m; P 1.00); fast water: depth x speed 0.32 m2/s (small cars unstable from 0.3); runoff beside / along the road at 3.3 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.99); a culvert within 100 m is overtopped |
| 3 | 1.00 | Route 2 | Fitchburg | 0.73 m of water at peak; over 30 cm for 11.0 h; 30 cm reached 0.5 h into the storm; worst hour 32 mm (30% of the storm); runoff beside / along the road at 1.8 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.84); a culvert within 100 m is overtopped |
| 4 | 1.00 | (unnamed) | Leominster | 1.32 m of water at peak; over 30 cm for 17.5 h; 30 cm reached 0.0 h into the storm; worst hour 32 mm (40% of the storm); water beside the road 0.22 m below its crest (design freeboard 0.30 m; P 0.71); a culvert within 100 m is overtopped |
| 5 | 1.00 | Depot Street | Fitchburg | 3.21 m of water at peak; over 30 cm for 18.0 h; 30 cm reached 0.5 h into the storm; worst hour 25 mm (30% of the storm); water beside the road 0.11 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 0.7 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.20); a culvert within 100 m is overtopped |
| 6 | 1.00 | Water Street | Leominster | 1.32 m of water at peak; over 30 cm for 17.0 h; 30 cm reached 0.5 h into the storm; worst hour 30 mm (39% of the storm); a culvert within 100 m is overtopped |
| 7 | 1.00 | Litchfield Street | Leominster | 0.83 m of water at peak; over 30 cm for 10.5 h; 30 cm reached 1.0 h into the storm; worst hour 24 mm (37% of the storm); a culvert within 100 m is overtopped |
| 8 | 1.00 | Route 31 | Fitchburg | 2.65 m of water at peak; over 30 cm for 10.0 h; 30 cm reached 8.5 h into the storm; worst hour 30 mm (32% of the storm); a culvert within 100 m is overtopped |
| 9 | 1.00 | Route 140 | Princeton | 0.84 m of water at peak; over 30 cm for 8.0 h; 30 cm reached 8.5 h into the storm; worst hour 39 mm (40% of the storm); water beside the road 1.79 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 4.2 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.85); a culvert within 100 m is overtopped |
| 10 | 1.00 | Litchfield Street | Leominster | 0.69 m of water at peak; over 30 cm for 10.5 h; 30 cm reached 0.5 h into the storm; worst hour 28 mm (42% of the storm) |
| 11 | 1.00 | Kingman Drive | Leominster | 1.02 m of water at peak; over 30 cm for 11.0 h; 30 cm reached 7.5 h into the storm; worst hour 38 mm (41% of the storm); water beside the road 0.41 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 3.2 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.98); a culvert within 100 m is overtopped |
| 12 | 1.00 | Narrows Road | Westminster | 3.03 m of water at peak; over 30 cm for 9.0 h; 30 cm reached 9.5 h into the storm; worst hour 31 mm (30% of the storm); water beside the road 2.53 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 0.7 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.17); a culvert within 100 m is overtopped |
| 13 | 1.00 | Narrows Road | Westminster | 0.89 m of water at peak; over 30 cm for 8.5 h; 30 cm reached 10.0 h into the storm; worst hour 31 mm (30% of the storm); water beside the road 0.31 m below its crest (design freeboard 0.30 m; P 0.48); runoff beside / along the road at 4.5 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.90); a culvert within 100 m is overtopped |
| 14 | 1.00 | Oakmont Avenue | Westminster | 1.10 m of water at peak; over 30 cm for 12.0 h; 30 cm reached 0.5 h into the storm; worst hour 27 mm (31% of the storm); runoff beside / along the road at 3.9 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.93); a culvert within 100 m is overtopped |
| 15 | 1.00 | John Fitch Highway | Fitchburg | 0.72 m of water at peak; over 30 cm for 1.5 h; 30 cm reached 0.0 h into the storm; worst hour 24 mm (29% of the storm); runoff beside / along the road at 1.6 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.23); a culvert within 100 m is overtopped |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
