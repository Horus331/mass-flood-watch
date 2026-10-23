# Road-closure prototype: jul2023_loss_jul2023_infil0

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on CPU (OpenMP)), 20 m grid, storm from 2023-07-14T08:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 6,775 |
| Expected closures (sum of probabilities) | 24.8 |
| Segments with closure probability >= 50% | 8 (4.9 km) |
| Further segments that may close (stream reaches the road crest) | 21 (12.0 km) |
| Culverts overtopped / surcharged | 21 / 0 of 1023 |
| Road segments cut off from hospitals | 40 |
| Worst added trip time to a hospital | 14.2 min |
| Heaviest hour of rain | 25.9 mm |
| Flood model run time | 694 s |

## Checks against what happened

- Storm-day flood reports in the area: 3; water >= 10 cm within 100 m of 0% of them, vs 19% of random points (any day).
- Segments flagged impassable are 0.0x as likely as an average segment to have a report within 200 m.
- MassDOT repeating flood sites in the area: 7; 0 have a segment within 150 m at P >= 0.5 (share of all segments at P >= 0.5: 0.1%).

## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 1.00 | Martin Luther King Jr Boulevard | Worcester | 2.10 m of water at peak; over 30 cm for 17.5 h; 30 cm reached 1.0 h into the storm; worst hour 21 mm (82% of the storm); water beside the road 2.02 m above its crest (design freeboard 0.30 m; P 1.00); fast water: depth x speed 0.23 m2/s (small cars unstable from 0.3); runoff beside / along the road at 0.9 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.46); road sag 3.2 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 21 mm; catchment 60.2 ha) (P 1.00) |
| 2 | 1.00 | Martin Luther King Jr Boulevard | Worcester | 1.40 m of water at peak; over 30 cm for 17.5 h; 30 cm reached 1.0 h into the storm; worst hour 21 mm (82% of the storm); water beside the road 0.89 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 4.3 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.76); road sag 3.2 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 21 mm; catchment 60.2 ha) (P 1.00) |
| 3 | 1.00 | Foster Street | Worcester | 0.97 m of water at peak; over 30 cm for 11.5 h; 30 cm reached 7.0 h into the storm; worst hour 20 mm (83% of the storm); water beside the road 0.33 m below its crest (design freeboard 0.30 m; P 0.43); a culvert within 100 m is overtopped |
| 4 | 1.00 | Foster Street | Worcester | 0.97 m of water at peak; over 30 cm for 11.5 h; 30 cm reached 7.0 h into the storm; worst hour 20 mm (83% of the storm); water beside the road 0.13 m below its crest (design freeboard 0.30 m; P 0.87); runoff beside / along the road at 1.9 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.35); a culvert within 100 m is overtopped |
| 5 | 1.00 | (unnamed) | Worcester | 1.06 m of water at peak; over 30 cm for 9.5 h; 30 cm reached 9.0 h into the storm; worst hour 22 mm (82% of the storm); a culvert within 100 m is overtopped |
| 6 | 0.55 | Ludlow Street | Worcester | 0.31 m of water at peak; worst hour 19 mm (89% of the storm); a culvert within 100 m is overtopped |
| 7 | 0.54 | Stafford Street | Worcester | 0.31 m of water at peak; worst hour 20 mm (89% of the storm); a culvert within 100 m is overtopped |
| 8 | 0.52 | Kendall Road | Holden | 0.30 m of water at peak; over 30 cm for 0.5 h; 30 cm reached 18.0 h into the storm; worst hour 19 mm (86% of the storm); a culvert within 100 m is overtopped |
| 9 | 0.49 | Route 12 | Auburn | 0.30 m of water at peak; worst hour 17 mm (82% of the storm); water beside the road 3.13 m above its crest (design freeboard 0.30 m; P 1.00); fast water: depth x speed 0.29 m2/s (small cars unstable from 0.3); runoff beside / along the road at 4.9 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 1.00); a culvert within 100 m is overtopped |
| 10 | 0.44 | (unnamed) | Spencer | 0.29 m of water at peak; worst hour 19 mm (68% of the storm) |
| 11 | 0.43 | Ramp-West Boylston Dr To Rt 190 Nb | Worcester | 0.28 m of water at peak; worst hour 22 mm (84% of the storm); water beside the road 0.14 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.8 m deep (underpass, drains sized for the 50-yr hour, 58 mm; peak hour here 22 mm; catchment 52.2 ha) (P 0.44) |
| 12 | 0.29 | Ramp-Rt 12 Nb To Rt 190 Nb | Worcester | 0.24 m of water at peak; worst hour 22 mm (84% of the storm); water beside the road 0.17 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.8 m deep (underpass, drains sized for the 50-yr hour, 58 mm; peak hour here 22 mm; catchment 52.2 ha) (P 0.44) |
| 13 | 0.28 | James Street | Worcester | 0.24 m of water at peak; worst hour 21 mm (89% of the storm); a culvert within 100 m is overtopped |
| 14 | 0.21 | West Boylston Drive | Worcester | 0.22 m of water at peak; worst hour 22 mm (84% of the storm) |
| 15 | 0.21 | West Boylston Drive | Worcester | 0.22 m of water at peak; worst hour 22 mm (84% of the storm) |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
