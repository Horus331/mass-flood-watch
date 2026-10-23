# Road-closure prototype: aug2026_loss_aug2026_leominster_20m

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on CPU (OpenMP)), 20 m grid, storm from 2026-08-03T04:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 4,542 |
| Expected closures (sum of probabilities) | 179.3 |
| Segments with closure probability >= 50% | 157 (101.9 km) |
| Further segments that may close (stream reaches the road crest) | 214 (140.7 km) |
| Culverts overtopped / surcharged | 160 / 6 of 616 |
| Road segments cut off from hospitals | 877 |
| Worst added trip time to a hospital | 26.1 min |
| Heaviest hour of rain | 46.0 mm |
| Flood model run time | 1456 s |

## Checks against what happened

- Storm-day flood reports in the area: 3; water >= 10 cm within 100 m of 67% of them, vs 68% of random points (any day).
- Segments flagged impassable are 3.55x as likely as an average segment to have a report within 200 m.
- MassDOT repeating flood sites in the area: 4; 3 have a segment within 150 m at P >= 0.5 (share of all segments at P >= 0.5: 3.5%).

## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 1.00 | Route 2 | Leominster | 3.36 m of water at peak; over 30 cm for 11.0 h; 30 cm reached 7.5 h into the storm; worst hour 26 mm (40% of the storm); runoff beside / along the road at 2.0 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.30); a culvert within 100 m is overtopped |
| 2 | 1.00 | (unnamed) | Leominster | 1.64 m of water at peak; over 30 cm for 11.0 h; 30 cm reached 7.5 h into the storm; worst hour 32 mm (40% of the storm); water beside the road 0.16 m below its crest (design freeboard 0.30 m; P 0.83); a culvert within 100 m is overtopped |
| 3 | 1.00 | Depot Street | Fitchburg | 1.78 m of water at peak; over 30 cm for 14.0 h; 30 cm reached 0.5 h into the storm; worst hour 25 mm (30% of the storm); water beside the road 1.47 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 0.9 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.39); a culvert within 100 m is overtopped |
| 4 | 1.00 | Litchfield Street | Leominster | 1.14 m of water at peak; over 30 cm for 10.0 h; 30 cm reached 8.5 h into the storm; worst hour 24 mm (37% of the storm); a culvert within 100 m is overtopped |
| 5 | 1.00 | Route 12 | Leominster | 0.66 m of water at peak; over 30 cm for 6.0 h; 30 cm reached 8.5 h into the storm; worst hour 25 mm (38% of the storm); water beside the road 0.04 m above its crest (design freeboard 0.30 m; P 0.99); a culvert within 100 m is overtopped |
| 6 | 1.00 | Route 31 | Fitchburg | 0.73 m of water at peak; over 30 cm for 10.5 h; 30 cm reached 8.0 h into the storm; worst hour 30 mm (32% of the storm); a culvert within 100 m is overtopped |
| 7 | 1.00 | Route 117 | Leominster | 0.74 m of water at peak; over 30 cm for 7.0 h; 30 cm reached 9.0 h into the storm; worst hour 24 mm (38% of the storm); cut off from hospitals |
| 8 | 1.00 | Route 117 | Leominster | 0.74 m of water at peak; over 30 cm for 7.0 h; 30 cm reached 9.0 h into the storm; worst hour 24 mm (38% of the storm); runoff beside / along the road at 0.4 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.13); a culvert within 100 m is overtopped |
| 9 | 1.00 | John Fitch Highway | Fitchburg | 0.79 m of water at peak; over 30 cm for 5.0 h; 30 cm reached 7.0 h into the storm; worst hour 29 mm (34% of the storm); water beside the road 0.40 m below its crest (design freeboard 0.30 m; P 0.24) |
| 10 | 1.00 | Water Street | Leominster | 1.64 m of water at peak; over 30 cm for 11.0 h; 30 cm reached 7.5 h into the storm; worst hour 30 mm (39% of the storm); a culvert within 100 m is overtopped |
| 11 | 1.00 | Route 140 | Princeton | 0.76 m of water at peak; over 30 cm for 8.5 h; 30 cm reached 7.5 h into the storm; worst hour 39 mm (40% of the storm); water beside the road 0.20 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 1.4 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.48); a culvert within 100 m is overtopped |
| 12 | 1.00 | Merriam Avenue | Leominster | 0.66 m of water at peak; over 30 cm for 3.5 h; 30 cm reached 7.5 h into the storm; worst hour 38 mm (42% of the storm); water beside the road 0.47 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 1.1 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.60); road sag 0.4 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 37 mm; catchment 13.0 ha) (P 1.00) |
| 13 | 1.00 | Heywood Street | Fitchburg | 0.64 m of water at peak; over 30 cm for 3.5 h; 30 cm reached 7.5 h into the storm; worst hour 35 mm (38% of the storm); water beside the road 1.52 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 3.2 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.99); culvert (Unknown): headwater 10.32 m vs road crest 1.61 m, 5.7 m3/s |
| 14 | 1.00 | Kingman Drive | Leominster | 1.28 m of water at peak; over 30 cm for 11.5 h; 30 cm reached 7.0 h into the storm; worst hour 38 mm (41% of the storm); water beside the road 0.47 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 1.7 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.79); a culvert within 100 m is overtopped |
| 15 | 1.00 | Main Street | Fitchburg | 1.05 m of water at peak; over 30 cm for 10.0 h; 30 cm reached 7.5 h into the storm; worst hour 23 mm (27% of the storm); runoff beside / along the road at 1.2 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.59); a culvert within 100 m is overtopped |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
