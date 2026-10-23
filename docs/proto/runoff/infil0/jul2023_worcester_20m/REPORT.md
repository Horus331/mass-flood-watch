# Road-closure prototype: jul2023_loss_jul2023_worcester_20m

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on CPU (OpenMP)), 20 m grid, storm from 2023-07-14T08:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 6,775 |
| Expected closures (sum of probabilities) | 22.7 |
| Segments with closure probability >= 50% | 5 (1.7 km) |
| Further segments that may close (stream reaches the road crest) | 18 (10.2 km) |
| Culverts overtopped / surcharged | 19 / 0 of 1023 |
| Road segments cut off from hospitals | 34 |
| Worst added trip time to a hospital | 14.2 min |
| Heaviest hour of rain | 25.9 mm |
| Flood model run time | 1098 s |

## Checks against what happened

- Storm-day flood reports in the area: 3; water >= 10 cm within 100 m of 0% of them, vs 15% of random points (any day).
- Segments flagged impassable are 0.0x as likely as an average segment to have a report within 200 m.
- MassDOT repeating flood sites in the area: 7; 0 have a segment within 150 m at P >= 0.5 (share of all segments at P >= 0.5: 0.1%).

## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 1.00 | Martin Luther King Jr Boulevard | Worcester | 1.83 m of water at peak; over 30 cm for 17.5 h; 30 cm reached 1.0 h into the storm; worst hour 21 mm (82% of the storm); water beside the road 1.75 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 1.1 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.10); road sag 3.2 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 21 mm; catchment 60.2 ha) (P 1.00) |
| 2 | 1.00 | Martin Luther King Jr Boulevard | Worcester | 1.13 m of water at peak; over 30 cm for 17.5 h; 30 cm reached 1.0 h into the storm; worst hour 21 mm (82% of the storm); water beside the road 0.62 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 2.5 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.38); road sag 3.2 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 21 mm; catchment 60.2 ha) (P 1.00) |
| 3 | 1.00 | Foster Street | Worcester | 0.89 m of water at peak; over 30 cm for 11.5 h; 30 cm reached 7.0 h into the storm; worst hour 20 mm (83% of the storm); water beside the road 0.40 m below its crest (design freeboard 0.30 m; P 0.25); a culvert within 100 m is overtopped |
| 4 | 1.00 | Foster Street | Worcester | 0.89 m of water at peak; over 30 cm for 11.5 h; 30 cm reached 7.0 h into the storm; worst hour 20 mm (83% of the storm); water beside the road 0.28 m below its crest (design freeboard 0.30 m; P 0.55); a culvert within 100 m is overtopped |
| 5 | 1.00 | (unnamed) | Worcester | 0.93 m of water at peak; over 30 cm for 9.0 h; 30 cm reached 9.5 h into the storm; worst hour 22 mm (82% of the storm); a culvert within 100 m is overtopped |
| 6 | 0.46 | Kendall Road | Holden | 0.29 m of water at peak; worst hour 19 mm (86% of the storm); a culvert within 100 m is overtopped |
| 7 | 0.43 | Ludlow Street | Worcester | 0.28 m of water at peak; worst hour 19 mm (89% of the storm); a culvert within 100 m is overtopped |
| 8 | 0.42 | Stafford Street | Worcester | 0.28 m of water at peak; worst hour 20 mm (89% of the storm); a culvert within 100 m is overtopped |
| 9 | 0.41 | (unnamed) | Spencer | 0.28 m of water at peak; worst hour 19 mm (68% of the storm) |
| 10 | 0.39 | Ramp-West Boylston Dr To Rt 190 Nb | Worcester | 0.27 m of water at peak; worst hour 22 mm (84% of the storm); water beside the road 0.13 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.8 m deep (underpass, drains sized for the 50-yr hour, 58 mm; peak hour here 22 mm; catchment 52.2 ha) (P 0.40) |
| 11 | 0.25 | Ramp-Rt 12 Nb To Rt 190 Nb | Worcester | 0.23 m of water at peak; worst hour 22 mm (84% of the storm); water beside the road 0.16 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.8 m deep (underpass, drains sized for the 50-yr hour, 58 mm; peak hour here 22 mm; catchment 52.2 ha) (P 0.40) |
| 12 | 0.21 | James Street | Worcester | 0.22 m of water at peak; worst hour 21 mm (89% of the storm); a culvert within 100 m is overtopped |
| 13 | 0.18 | Route 12 | Auburn | 0.21 m of water at peak; worst hour 17 mm (82% of the storm); a culvert within 100 m is overtopped |
| 14 | 0.18 | West Boylston Drive | Worcester | 0.21 m of water at peak; worst hour 22 mm (84% of the storm) |
| 15 | 0.18 | West Boylston Drive | Worcester | 0.21 m of water at peak; worst hour 22 mm (84% of the storm) |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
