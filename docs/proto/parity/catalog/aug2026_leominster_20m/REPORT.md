# Road-closure prototype: aug2026_loss_aug2026_leominster_20m

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on CPU (OpenMP)), 20 m grid, storm from 2026-08-03T04:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 4,542 |
| Expected closures (sum of probabilities) | 81.7 |
| Segments with closure probability >= 50% | 62 (36.3 km) |
| Further segments that may close (stream reaches the road crest) | 90 (55.9 km) |
| Culverts overtopped / surcharged | 110 / 0 of 616 |
| Road segments cut off from hospitals | 382 |
| Worst added trip time to a hospital | 23.5 min |
| Heaviest hour of rain | 46.0 mm |
| Flood model run time | 1578 s |

## Checks against what happened

- Storm-day flood reports in the area: 3; water >= 10 cm within 100 m of 67% of them, vs 59% of random points (any day).
- Segments flagged impassable are 1.55x as likely as an average segment to have a report within 200 m.
- MassDOT repeating flood sites in the area: 4; 1 have a segment within 150 m at P >= 0.5 (share of all segments at P >= 0.5: 1.4%).

## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 1.00 | Route 2 | Leominster | 1.10 m of water at peak; over 30 cm for 10.0 h; 30 cm reached 8.5 h into the storm; worst hour 26 mm (40% of the storm); a culvert within 100 m is overtopped |
| 2 | 1.00 | (unnamed) | Leominster | 1.10 m of water at peak; over 30 cm for 10.0 h; 30 cm reached 8.5 h into the storm; worst hour 32 mm (40% of the storm); a culvert within 100 m is overtopped |
| 3 | 1.00 | Depot Street | Fitchburg | 0.96 m of water at peak; over 30 cm for 14.0 h; 30 cm reached 0.5 h into the storm; worst hour 25 mm (30% of the storm); runoff beside / along the road at 0.8 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.33); a culvert within 100 m is overtopped |
| 4 | 1.00 | Water Street | Leominster | 1.11 m of water at peak; over 30 cm for 10.0 h; 30 cm reached 8.5 h into the storm; worst hour 30 mm (39% of the storm); a culvert within 100 m is overtopped |
| 5 | 1.00 | Kingman Drive | Leominster | 0.83 m of water at peak; over 30 cm for 9.5 h; 30 cm reached 8.0 h into the storm; worst hour 38 mm (41% of the storm); water beside the road 0.38 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 1.2 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.64); a culvert within 100 m is overtopped |
| 6 | 1.00 | Depot Square | Leominster | 1.10 m of water at peak; over 30 cm for 10.0 h; 30 cm reached 8.5 h into the storm; worst hour 30 mm (39% of the storm); a culvert within 100 m is overtopped |
| 7 | 1.00 | Commercial Road | Leominster | 0.76 m of water at peak; over 30 cm for 6.0 h; 30 cm reached 9.5 h into the storm; worst hour 27 mm (40% of the storm); a culvert within 100 m is overtopped |
| 8 | 1.00 | Exchange Street | Leominster | 0.85 m of water at peak; over 30 cm for 4.5 h; 30 cm reached 8.0 h into the storm; worst hour 36 mm (40% of the storm); water beside the road 0.76 m above its crest (design freeboard 0.30 m; P 1.00); fast water: depth x speed 0.33 m2/s (small cars unstable from 0.3); runoff beside / along the road at 2.9 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.98); a culvert within 100 m is overtopped |
| 9 | 1.00 | (unnamed) | Leominster | 0.85 m of water at peak; over 30 cm for 4.5 h; 30 cm reached 8.0 h into the storm; worst hour 36 mm (40% of the storm) |
| 10 | 1.00 | Constitution Drive | Leominster | 0.73 m of water at peak; over 30 cm for 4.0 h; 30 cm reached 8.0 h into the storm; worst hour 36 mm (40% of the storm) |
| 11 | 1.00 | Houghton Road | Princeton | 0.63 m of water at peak; over 30 cm for 4.0 h; 30 cm reached 8.5 h into the storm; worst hour 36 mm (42% of the storm); water beside the road 0.48 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 0.6 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.15); a culvert within 100 m is overtopped |
| 12 | 1.00 | Litchfield Street | Leominster | 0.61 m of water at peak; over 30 cm for 8.5 h; 30 cm reached 10.0 h into the storm; worst hour 24 mm (37% of the storm); a culvert within 100 m is overtopped |
| 13 | 1.00 | Sanborn Street | Fitchburg | 0.57 m of water at peak; over 30 cm for 4.0 h; 30 cm reached 8.5 h into the storm; worst hour 24 mm (29% of the storm); runoff beside / along the road at 1.4 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.72); a culvert within 100 m is overtopped |
| 14 | 1.00 | Bullard Road | Princeton | 0.57 m of water at peak; over 30 cm for 3.5 h; 30 cm reached 9.0 h into the storm; worst hour 33 mm (42% of the storm); water beside the road 0.00 m below its crest (design freeboard 0.30 m; P 0.98); a culvert within 100 m is overtopped |
| 15 | 0.98 | Granite Street | Leominster | 0.51 m of water at peak; over 30 cm for 2.0 h; 30 cm reached 8.0 h into the storm; worst hour 38 mm (39% of the storm); water beside the road 0.10 m below its crest (design freeboard 0.30 m; P 0.91); runoff beside / along the road at 0.9 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.40); culvert (Unknown): headwater 8.24 m vs road crest 2.56 m, 6.4 m3/s |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
