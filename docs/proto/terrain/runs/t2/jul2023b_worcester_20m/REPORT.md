# Road-closure prototype: jul2023b_loss_jul2023b_worcester_20m

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on CPU (OpenMP)), 20 m grid, storm from 2023-07-10T08:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 7,372 |
| Expected closures (sum of probabilities) | 32.1 |
| Segments with closure probability >= 50% | 6 (4.3 km) |
| Further segments that may close (stream reaches the road crest) | 51 (29.2 km) |
| Culverts overtopped / surcharged | 27 / 0 of 978 |
| Road segments cut off from hospitals | 124 |
| Worst added trip time to a hospital | 17.3 min |
| Heaviest hour of rain | 31.4 mm |
| Flood model run time | 1175 s |

## Checks against what happened

- Storm-day flood reports in the area: 1; water >= 10 cm within 100 m of 0% of them, vs 34% of random points (any day).
- Segments flagged impassable are 0.0x as likely as an average segment to have a report within 200 m.
- MassDOT repeating flood sites in the area: 8; 0 have a segment within 150 m at P >= 0.5 (share of all segments at P >= 0.5: 0.1%).

## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 0.99 | East Park Terrace | Worcester | 0.55 m of water at peak; over 30 cm for 4.0 h; 30 cm reached 14.5 h into the storm; worst hour 16 mm (32% of the storm); water beside the road 0.45 m above its crest (design freeboard 0.30 m; P 1.00); road sag 4.3 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 16 mm; catchment 127.8 ha) (P 0.99) |
| 2 | 0.95 | Coolidge Road | Worcester | 0.46 m of water at peak; over 30 cm for 2.5 h; 30 cm reached 16.0 h into the storm; worst hour 18 mm (34% of the storm); water beside the road 0.53 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 0.6 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.16); road sag 0.7 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 17 mm; catchment 17.7 ha) (P 1.00) |
| 3 | 0.94 | Kinnicutt Road | Worcester | 0.46 m of water at peak; over 30 cm for 3.5 h; 30 cm reached 15.0 h into the storm; worst hour 16 mm (30% of the storm); water beside the road 0.72 m above its crest (design freeboard 0.30 m; P 1.00) |
| 4 | 0.90 | Martin Luther King Jr Boulevard | Worcester | 0.43 m of water at peak; over 30 cm for 4.0 h; 30 cm reached 14.5 h into the storm; worst hour 16 mm (32% of the storm); water beside the road 0.35 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 1.1 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.56); road sag 3.2 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 16 mm; catchment 60.2 ha) (P 0.90) |
| 5 | 0.60 | Shrewsbury Street | Worcester | 0.33 m of water at peak; over 30 cm for 2.0 h; 30 cm reached 16.5 h into the storm; worst hour 16 mm (33% of the storm); water beside the road 0.24 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.9 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 16 mm; catchment 127.8 ha) (P 0.78) |
| 6 | 0.60 | Mill Street | Holden | 0.33 m of water at peak; over 30 cm for 0.5 h; 30 cm reached 0.5 h into the storm; worst hour 26 mm (45% of the storm) |
| 7 | 0.42 | Maybrook Place | Worcester | 0.28 m of water at peak; worst hour 18 mm (35% of the storm); water beside the road 0.26 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.7 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 18 mm; catchment 61.6 ha) (P 0.76) |
| 8 | 0.42 | Westbrook Road | Worcester | 0.28 m of water at peak; worst hour 15 mm (28% of the storm); water beside the road 0.33 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 0.4 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.10) |
| 9 | 0.38 | (unnamed) | Holden | 0.27 m of water at peak; worst hour 27 mm (46% of the storm); runoff beside / along the road at 1.1 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.57); a culvert within 100 m is overtopped |
| 10 | 0.37 | Raymond Huntington Highway | West Boylston | 0.27 m of water at peak; worst hour 26 mm (38% of the storm) |
| 11 | 0.35 | Stafford Street | Worcester | 0.26 m of water at peak; worst hour 19 mm (36% of the storm); water beside the road 0.13 m above its crest (design freeboard 0.30 m; P 1.00); a culvert within 100 m is overtopped |
| 12 | 0.32 | Wellington Street | Worcester | 0.25 m of water at peak; worst hour 16 mm (34% of the storm); water beside the road 0.20 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.9 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 16 mm; catchment 15.1 ha) (P 0.89) |
| 13 | 0.32 | Murray Avenue | Worcester | 0.25 m of water at peak; worst hour 16 mm (34% of the storm); water beside the road 0.24 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.9 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 16 mm; catchment 15.1 ha) (P 0.89) |
| 14 | 0.30 | (unnamed) | Worcester | 0.25 m of water at peak; worst hour 16 mm (34% of the storm); a culvert within 100 m is overtopped |
| 15 | 0.30 | Washington Street | Worcester | 0.25 m of water at peak; worst hour 15 mm (33% of the storm); water beside the road 0.11 m below its crest (design freeboard 0.30 m; P 0.90); a culvert within 100 m is overtopped |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
