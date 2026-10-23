# Road-closure prototype: jul2023_loss_jul2023_worcester_20m

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on CPU (OpenMP)), 20 m grid, storm from 2023-07-14T08:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 6,775 |
| Expected closures (sum of probabilities) | 29.5 |
| Segments with closure probability >= 50% | 8 (3.7 km) |
| Further segments that may close (stream reaches the road crest) | 43 (23.9 km) |
| Culverts overtopped / surcharged | 28 / 0 of 1023 |
| Road segments cut off from hospitals | 38 |
| Worst added trip time to a hospital | 13.8 min |
| Heaviest hour of rain | 25.9 mm |
| Flood model run time | 834 s |

## Checks against what happened

- Storm-day flood reports in the area: 3; water >= 10 cm within 100 m of 0% of them, vs 29% of random points (any day).
- Segments flagged impassable are 0.0x as likely as an average segment to have a report within 200 m.
- MassDOT repeating flood sites in the area: 7; 0 have a segment within 150 m at P >= 0.5 (share of all segments at P >= 0.5: 0.1%).

## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 1.00 | Martin Luther King Jr Boulevard | Worcester | 2.93 m of water at peak; over 30 cm for 17.5 h; 30 cm reached 1.0 h into the storm; worst hour 21 mm (82% of the storm); water beside the road 2.85 m above its crest (design freeboard 0.30 m; P 1.00); fast water: depth x speed 0.20 m2/s (small cars unstable from 0.3); road sag 3.2 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 21 mm; catchment 60.2 ha) (P 1.00); a culvert within 100 m is overtopped |
| 2 | 1.00 | Martin Luther King Jr Boulevard | Worcester | 2.23 m of water at peak; over 30 cm for 17.5 h; 30 cm reached 1.0 h into the storm; worst hour 21 mm (82% of the storm); water beside the road 1.91 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 2.5 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.93); road sag 3.2 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 21 mm; catchment 60.2 ha) (P 1.00); a culvert within 100 m is overtopped |
| 3 | 1.00 | Foster Street | Worcester | 1.21 m of water at peak; over 30 cm for 11.5 h; 30 cm reached 7.0 h into the storm; worst hour 20 mm (83% of the storm); water beside the road 0.40 m below its crest (design freeboard 0.30 m; P 0.25); a culvert within 100 m is overtopped |
| 4 | 1.00 | Foster Street | Worcester | 1.21 m of water at peak; over 30 cm for 11.5 h; 30 cm reached 7.0 h into the storm; worst hour 20 mm (83% of the storm); water beside the road 0.28 m below its crest (design freeboard 0.30 m; P 0.55); a culvert within 100 m is overtopped |
| 5 | 1.00 | (unnamed) | Worcester | 1.11 m of water at peak; over 30 cm for 9.5 h; 30 cm reached 9.0 h into the storm; worst hour 22 mm (82% of the storm); a culvert within 100 m is overtopped |
| 6 | 0.67 | Major Taylor Boulevard | Worcester | 0.34 m of water at peak; over 30 cm for 1.5 h; 30 cm reached 17.0 h into the storm; worst hour 21 mm (83% of the storm); water beside the road 0.10 m above its crest (design freeboard 0.30 m; P 1.00); a culvert within 100 m is overtopped |
| 7 | 0.67 | Major Taylor Boulevard | Worcester | 0.34 m of water at peak; over 30 cm for 1.5 h; 30 cm reached 17.0 h into the storm; worst hour 21 mm (83% of the storm); water beside the road 0.10 m above its crest (design freeboard 0.30 m; P 1.00); a culvert within 100 m is overtopped |
| 8 | 0.51 | Ramp-West Boylston Dr To Rt 190 Nb | Worcester | 0.30 m of water at peak; over 30 cm for 2.0 h; 30 cm reached 15.0 h into the storm; worst hour 22 mm (84% of the storm); water beside the road 0.20 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.8 m deep (underpass, drains sized for the 50-yr hour, 58 mm; peak hour here 22 mm; catchment 52.2 ha) (P 0.52) |
| 9 | 0.46 | Wellington Street | Worcester | 0.29 m of water at peak; worst hour 19 mm (84% of the storm); water beside the road 0.35 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.9 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 19 mm; catchment 15.1 ha) (P 0.93) |
| 10 | 0.46 | Murray Avenue | Worcester | 0.29 m of water at peak; worst hour 19 mm (84% of the storm); water beside the road 0.35 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.9 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 19 mm; catchment 15.1 ha) (P 0.93) |
| 11 | 0.42 | Stafford Street | Worcester | 0.28 m of water at peak; worst hour 20 mm (89% of the storm); a culvert within 100 m is overtopped |
| 12 | 0.42 | Ludlow Street | Worcester | 0.28 m of water at peak; worst hour 19 mm (89% of the storm); a culvert within 100 m is overtopped |
| 13 | 0.36 | Ramp-Rt 12 Nb To Rt 190 Nb | Worcester | 0.26 m of water at peak; worst hour 22 mm (84% of the storm); water beside the road 0.19 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.8 m deep (underpass, drains sized for the 50-yr hour, 58 mm; peak hour here 22 mm; catchment 52.2 ha) (P 0.52) |
| 14 | 0.32 | Dewey Street | Worcester | 0.25 m of water at peak; worst hour 18 mm (85% of the storm); water beside the road 0.16 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.9 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 18 mm; catchment 12.8 ha) (P 0.33) |
| 15 | 0.32 | Parker Street | Worcester | 0.25 m of water at peak; worst hour 18 mm (86% of the storm); water beside the road 0.16 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.9 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 18 mm; catchment 12.8 ha) (P 0.33) |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
