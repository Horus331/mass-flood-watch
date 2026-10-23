# Road-closure prototype: jul2023_rain_jul2023_gauge

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on CPU (OpenMP)), 20 m grid, storm from 2023-07-14T08:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 6,775 |
| Expected closures (sum of probabilities) | 22.6 |
| Segments with closure probability >= 50% | 5 (1.7 km) |
| Further segments that may close (stream reaches the road crest) | 22 (12.6 km) |
| Culverts overtopped / surcharged | 20 / 0 of 1023 |
| Road segments cut off from hospitals | 34 |
| Worst added trip time to a hospital | 14.8 min |
| Heaviest hour of rain | 29.0 mm |
| Flood model run time | 1268 s |

## Checks against what happened

- Storm-day flood reports in the area: 3; water >= 10 cm within 100 m of 0% of them, vs 16% of random points (any day).
- Segments flagged impassable are 0.0x as likely as an average segment to have a report within 200 m.
- MassDOT repeating flood sites in the area: 7; 0 have a segment within 150 m at P >= 0.5 (share of all segments at P >= 0.5: 0.1%).

## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 1.00 | Martin Luther King Jr Boulevard | Worcester | 2.21 m of water at peak; over 30 cm for 17.5 h; 30 cm reached 1.0 h into the storm; worst hour 28 mm (82% of the storm); water beside the road 2.13 m above its crest (design freeboard 0.30 m; P 1.00); road sag 3.2 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 28 mm; catchment 60.2 ha) (P 1.00) |
| 2 | 1.00 | Martin Luther King Jr Boulevard | Worcester | 1.51 m of water at peak; over 30 cm for 17.5 h; 30 cm reached 1.0 h into the storm; worst hour 28 mm (82% of the storm); water beside the road 1.00 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 2.5 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.80); road sag 3.2 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 28 mm; catchment 60.2 ha) (P 1.00); a culvert within 100 m is overtopped |
| 3 | 1.00 | Foster Street | Worcester | 0.99 m of water at peak; over 30 cm for 11.5 h; 30 cm reached 7.0 h into the storm; worst hour 28 mm (83% of the storm); water beside the road 0.40 m below its crest (design freeboard 0.30 m; P 0.25); a culvert within 100 m is overtopped |
| 4 | 1.00 | Foster Street | Worcester | 0.99 m of water at peak; over 30 cm for 11.5 h; 30 cm reached 7.0 h into the storm; worst hour 28 mm (83% of the storm); water beside the road 0.28 m below its crest (design freeboard 0.30 m; P 0.55); a culvert within 100 m is overtopped |
| 5 | 1.00 | (unnamed) | Worcester | 1.02 m of water at peak; over 30 cm for 9.5 h; 30 cm reached 9.0 h into the storm; worst hour 27 mm (82% of the storm); a culvert within 100 m is overtopped |
| 6 | 0.42 | Stafford Street | Worcester | 0.28 m of water at peak; worst hour 25 mm (89% of the storm); a culvert within 100 m is overtopped |
| 7 | 0.42 | Ludlow Street | Worcester | 0.28 m of water at peak; worst hour 24 mm (89% of the storm); a culvert within 100 m is overtopped |
| 8 | 0.37 | Ramp-West Boylston Dr To Rt 190 Nb | Worcester | 0.27 m of water at peak; worst hour 25 mm (84% of the storm); water beside the road 0.12 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.8 m deep (underpass, drains sized for the 50-yr hour, 58 mm; peak hour here 25 mm; catchment 52.2 ha) (P 0.38) |
| 9 | 0.30 | (unnamed) | Spencer | 0.25 m of water at peak; worst hour 21 mm (68% of the storm) |
| 10 | 0.24 | Ramp-Rt 12 Nb To Rt 190 Nb | Worcester | 0.23 m of water at peak; worst hour 25 mm (84% of the storm); water beside the road 0.15 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.8 m deep (underpass, drains sized for the 50-yr hour, 58 mm; peak hour here 25 mm; catchment 52.2 ha) (P 0.38) |
| 11 | 0.21 | James Street | Worcester | 0.22 m of water at peak; worst hour 26 mm (89% of the storm); a culvert within 100 m is overtopped |
| 12 | 0.20 | Kendall Road | Holden | 0.22 m of water at peak; worst hour 19 mm (86% of the storm); a culvert within 100 m is overtopped |
| 13 | 0.18 | Route 12 | Auburn | 0.21 m of water at peak; worst hour 20 mm (82% of the storm); runoff beside / along the road at 1.5 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.12); a culvert within 100 m is overtopped |
| 14 | 0.16 | West Boylston Drive | Worcester | 0.20 m of water at peak; worst hour 25 mm (84% of the storm) |
| 15 | 0.16 | West Boylston Drive | Worcester | 0.20 m of water at peak; worst hour 25 mm (84% of the storm) |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
