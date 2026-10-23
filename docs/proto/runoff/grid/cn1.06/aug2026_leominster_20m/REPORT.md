# Road-closure prototype: aug2026_loss_aug2026_leominster_20m

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on CPU (OpenMP)), 20 m grid, storm from 2026-08-03T04:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 4,542 |
| Expected closures (sum of probabilities) | 158.3 |
| Segments with closure probability >= 50% | 134 (86.0 km) |
| Further segments that may close (stream reaches the road crest) | 194 (129.5 km) |
| Culverts overtopped / surcharged | 148 / 4 of 616 |
| Road segments cut off from hospitals | 723 |
| Worst added trip time to a hospital | 28.3 min |
| Heaviest hour of rain | 46.0 mm |
| Flood model run time | 1808 s |

## Checks against what happened

- Storm-day flood reports in the area: 3; water >= 10 cm within 100 m of 67% of them, vs 68% of random points (any day).
- Segments flagged impassable are 3.93x as likely as an average segment to have a report within 200 m.
- MassDOT repeating flood sites in the area: 4; 3 have a segment within 150 m at P >= 0.5 (share of all segments at P >= 0.5: 3.0%).

## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 1.00 | Route 2 | Leominster | 2.76 m of water at peak; over 30 cm for 11.0 h; 30 cm reached 7.5 h into the storm; worst hour 26 mm (40% of the storm); runoff beside / along the road at 2.0 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.27); a culvert within 100 m is overtopped |
| 2 | 1.00 | (unnamed) | Leominster | 1.54 m of water at peak; over 30 cm for 10.5 h; 30 cm reached 8.0 h into the storm; worst hour 32 mm (40% of the storm); water beside the road 0.18 m below its crest (design freeboard 0.30 m; P 0.79); a culvert within 100 m is overtopped |
| 3 | 1.00 | Depot Street | Fitchburg | 1.59 m of water at peak; over 30 cm for 14.0 h; 30 cm reached 0.5 h into the storm; worst hour 25 mm (30% of the storm); water beside the road 1.10 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 1.0 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.49); a culvert within 100 m is overtopped |
| 4 | 1.00 | Litchfield Street | Leominster | 1.04 m of water at peak; over 30 cm for 10.0 h; 30 cm reached 8.5 h into the storm; worst hour 24 mm (37% of the storm); a culvert within 100 m is overtopped |
| 5 | 1.00 | Route 117 | Leominster | 0.67 m of water at peak; over 30 cm for 6.5 h; 30 cm reached 9.0 h into the storm; worst hour 24 mm (38% of the storm); cut off from hospitals |
| 6 | 1.00 | Route 117 | Leominster | 0.67 m of water at peak; over 30 cm for 6.5 h; 30 cm reached 9.0 h into the storm; worst hour 24 mm (38% of the storm); runoff beside / along the road at 0.4 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.13); a culvert within 100 m is overtopped |
| 7 | 1.00 | Water Street | Leominster | 1.55 m of water at peak; over 30 cm for 10.5 h; 30 cm reached 8.0 h into the storm; worst hour 30 mm (39% of the storm); a culvert within 100 m is overtopped |
| 8 | 1.00 | John Fitch Highway | Fitchburg | 0.72 m of water at peak; over 30 cm for 4.0 h; 30 cm reached 8.0 h into the storm; worst hour 29 mm (34% of the storm); water beside the road 0.42 m below its crest (design freeboard 0.30 m; P 0.22) |
| 9 | 1.00 | Route 140 | Princeton | 0.67 m of water at peak; over 30 cm for 8.0 h; 30 cm reached 8.0 h into the storm; worst hour 39 mm (40% of the storm); runoff beside / along the road at 1.6 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.17); a culvert within 100 m is overtopped |
| 10 | 1.00 | Kingman Drive | Leominster | 1.21 m of water at peak; over 30 cm for 11.5 h; 30 cm reached 7.0 h into the storm; worst hour 38 mm (41% of the storm); water beside the road 0.45 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 1.7 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.77); a culvert within 100 m is overtopped |
| 11 | 1.00 | Litchfield Street | Leominster | 0.91 m of water at peak; over 30 cm for 9.5 h; 30 cm reached 8.0 h into the storm; worst hour 28 mm (42% of the storm) |
| 12 | 1.00 | Main Street | Fitchburg | 0.87 m of water at peak; over 30 cm for 8.0 h; 30 cm reached 8.0 h into the storm; worst hour 23 mm (27% of the storm); runoff beside / along the road at 1.1 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.58); a culvert within 100 m is overtopped |
| 13 | 1.00 | Oakmont Avenue | Westminster | 0.65 m of water at peak; over 30 cm for 11.5 h; 30 cm reached 7.0 h into the storm; worst hour 27 mm (31% of the storm); runoff beside / along the road at 1.0 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.47); a culvert within 100 m is overtopped |
| 14 | 1.00 | Depot Square | Leominster | 1.54 m of water at peak; over 30 cm for 10.5 h; 30 cm reached 8.0 h into the storm; worst hour 30 mm (39% of the storm); a culvert within 100 m is overtopped |
| 15 | 1.00 | Commercial Road | Leominster | 1.53 m of water at peak; over 30 cm for 10.0 h; 30 cm reached 8.5 h into the storm; worst hour 27 mm (40% of the storm); water beside the road 0.15 m above its crest (design freeboard 0.30 m; P 1.00); a culvert within 100 m is overtopped |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
