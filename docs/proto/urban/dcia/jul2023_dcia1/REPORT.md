# Road-closure prototype: jul2023_loss_jul2023_dcia1

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on CPU (OpenMP)), 20 m grid, storm from 2023-07-14T08:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 6,605 |
| Expected closures (sum of probabilities) | 45.8 |
| Segments with closure probability >= 50% | 20 (11.0 km) |
| Further segments that may close (stream reaches the road crest) | 82 (44.0 km) |
| Culverts overtopped / surcharged | 40 / 0 of 1023 |
| Road segments cut off from hospitals | 60 |
| Worst added trip time to a hospital | 14.4 min |
| Heaviest hour of rain | 25.9 mm |
| Flood model run time | 513 s |

## Checks against what happened

- Storm-day flood reports in the area: 3; water >= 10 cm within 100 m of 0% of them, vs 50% of random points (any day).
- Segments flagged impassable are 0.0x as likely as an average segment to have a report within 200 m.
- MassDOT repeating flood sites in the area: 7; 0 have a segment within 150 m at P >= 0.5 (share of all segments at P >= 0.5: 0.3%).

## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 1.00 | Martin Luther King Jr Boulevard | Worcester | 3.19 m of water at peak; over 30 cm for 17.5 h; 30 cm reached 1.0 h into the storm; worst hour 21 mm (82% of the storm); water beside the road 3.11 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 1.2 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.50); road sag 3.2 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 21 mm; catchment 60.2 ha) (P 1.00); a culvert within 100 m is overtopped |
| 2 | 1.00 | Martin Luther King Jr Boulevard | Worcester | 2.49 m of water at peak; over 30 cm for 17.5 h; 30 cm reached 1.0 h into the storm; worst hour 21 mm (82% of the storm); water beside the road 2.16 m above its crest (design freeboard 0.30 m; P 1.00); fast water: depth x speed 0.23 m2/s (small cars unstable from 0.3); runoff beside / along the road at 4.6 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.85); road sag 3.2 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 21 mm; catchment 60.2 ha) (P 1.00); a culvert within 100 m is overtopped |
| 3 | 1.00 | Foster Street | Worcester | 1.46 m of water at peak; over 30 cm for 10.0 h; 30 cm reached 8.5 h into the storm; worst hour 20 mm (83% of the storm); water beside the road 0.33 m below its crest (design freeboard 0.30 m; P 0.43); a culvert within 100 m is overtopped |
| 4 | 1.00 | Foster Street | Worcester | 1.46 m of water at peak; over 30 cm for 10.0 h; 30 cm reached 8.5 h into the storm; worst hour 20 mm (83% of the storm); water beside the road 0.13 m below its crest (design freeboard 0.30 m; P 0.87); runoff beside / along the road at 1.9 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.35); a culvert within 100 m is overtopped |
| 5 | 1.00 | (unnamed) | Worcester | 1.54 m of water at peak; over 30 cm for 10.0 h; 30 cm reached 8.5 h into the storm; worst hour 22 mm (82% of the storm); a culvert within 100 m is overtopped |
| 6 | 1.00 | Major Taylor Boulevard | Worcester | 0.60 m of water at peak; over 30 cm for 6.0 h; 30 cm reached 11.5 h into the storm; worst hour 21 mm (83% of the storm); water beside the road 0.35 m above its crest (design freeboard 0.30 m; P 1.00); road sag 1.1 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 21 mm; catchment 60.2 ha) (P 0.86); a culvert within 100 m is overtopped |
| 7 | 1.00 | Major Taylor Boulevard | Worcester | 0.60 m of water at peak; over 30 cm for 6.0 h; 30 cm reached 11.5 h into the storm; worst hour 21 mm (83% of the storm); water beside the road 0.35 m above its crest (design freeboard 0.30 m; P 1.00); road sag 1.1 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 21 mm; catchment 60.2 ha) (P 0.86); a culvert within 100 m is overtopped |
| 8 | 0.89 | Bridge Street | Worcester | 0.42 m of water at peak; over 30 cm for 5.5 h; 30 cm reached 13.0 h into the storm; worst hour 20 mm (82% of the storm); water beside the road 0.12 m above its crest (design freeboard 0.30 m; P 1.00); road sag 2.3 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 20 mm; catchment 22.1 ha) (P 1.00); a culvert within 100 m is overtopped |
| 9 | 0.89 | Wellington Street | Worcester | 0.42 m of water at peak; over 30 cm for 2.5 h; 30 cm reached 9.0 h into the storm; worst hour 19 mm (84% of the storm); water beside the road 0.42 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.9 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 19 mm; catchment 15.1 ha) (P 0.98) |
| 10 | 0.89 | Murray Avenue | Worcester | 0.42 m of water at peak; over 30 cm for 2.5 h; 30 cm reached 8.5 h into the storm; worst hour 19 mm (84% of the storm); water beside the road 0.42 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 0.6 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.17); road sag 0.9 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 19 mm; catchment 15.1 ha) (P 0.98) |
| 11 | 0.80 | Coolidge Road | Worcester | 0.38 m of water at peak; over 30 cm for 4.5 h; 30 cm reached 10.5 h into the storm; worst hour 18 mm (84% of the storm); water beside the road 0.50 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 1.2 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.54); road sag 0.7 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 18 mm; catchment 17.7 ha) (P 0.98) |
| 12 | 0.67 | Ramp-West Boylston Dr To Rt 190 Nb | Worcester | 0.34 m of water at peak; over 30 cm for 5.0 h; 30 cm reached 12.5 h into the storm; worst hour 22 mm (84% of the storm); water beside the road 0.22 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.8 m deep (underpass, drains sized for the 50-yr hour, 58 mm; peak hour here 22 mm; catchment 52.2 ha) (P 0.72) |
| 13 | 0.64 | Kinnicutt Road | Worcester | 0.34 m of water at peak; over 30 cm for 2.0 h; 30 cm reached 9.0 h into the storm; worst hour 19 mm (84% of the storm); water beside the road 0.24 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 0.7 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.23) |
| 14 | 0.63 | Dewey Street | Worcester | 0.33 m of water at peak; over 30 cm for 1.5 h; 30 cm reached 8.5 h into the storm; worst hour 18 mm (85% of the storm); water beside the road 0.25 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.9 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 18 mm; catchment 12.8 ha) (P 0.64) |
| 15 | 0.63 | Parker Street | Worcester | 0.33 m of water at peak; over 30 cm for 1.5 h; 30 cm reached 8.5 h into the storm; worst hour 18 mm (86% of the storm); water beside the road 0.25 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.9 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 18 mm; catchment 12.8 ha) (P 0.64) |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
