# Road-closure prototype: aug2023b_loss_aug2023b_millbury_20m

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on CPU (OpenMP)), 20 m grid, storm from 2023-08-18T05:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 8,013 |
| Expected closures (sum of probabilities) | 26.1 |
| Segments with closure probability >= 50% | 8 (5.4 km) |
| Further segments that may close (stream reaches the road crest) | 10 (5.5 km) |
| Culverts overtopped / surcharged | 34 / 0 of 1291 |
| Road segments cut off from hospitals | 85 |
| Worst added trip time to a hospital | 13.0 min |
| Heaviest hour of rain | 47.2 mm |
| Flood model run time | 1319 s |

## Checks against what happened

- Storm-day flood reports in the area: 0; water >= 10 cm within 100 m of 0% of them, vs 14% of random points (any day).
- MassDOT repeating flood sites in the area: 8; 0 have a segment within 150 m at P >= 0.5 (share of all segments at P >= 0.5: 0.1%).

## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 1.00 | Martin Luther King Jr Boulevard | Worcester | 2.12 m of water at peak; over 30 cm for 17.5 h; 30 cm reached 1.0 h into the storm; worst hour 21 mm (71% of the storm); water beside the road 2.04 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 0.9 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.40); road sag 3.2 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 21 mm; catchment 60.2 ha) (P 1.00) |
| 2 | 1.00 | Martin Luther King Jr Boulevard | Worcester | 1.42 m of water at peak; over 30 cm for 17.5 h; 30 cm reached 1.0 h into the storm; worst hour 21 mm (71% of the storm); water beside the road 0.91 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 0.6 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.11); road sag 3.2 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 21 mm; catchment 60.2 ha) (P 1.00); a culvert within 100 m is overtopped |
| 3 | 1.00 | Foster Street | Worcester | 1.03 m of water at peak; over 30 cm for 16.0 h; 30 cm reached 2.5 h into the storm; worst hour 22 mm (72% of the storm); water beside the road 0.40 m below its crest (design freeboard 0.30 m; P 0.25); a culvert within 100 m is overtopped |
| 4 | 0.89 | Providence Road | Sutton | 0.42 m of water at peak; over 30 cm for 2.5 h; 30 cm reached 9.0 h into the storm; worst hour 44 mm (76% of the storm); a culvert within 100 m is overtopped |
| 5 | 0.74 | East Park Terrace | Worcester | 0.37 m of water at peak; over 30 cm for 3.5 h; 30 cm reached 15.0 h into the storm; worst hour 22 mm (65% of the storm); water beside the road 0.27 m above its crest (design freeboard 0.30 m; P 1.00); road sag 4.3 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 22 mm; catchment 127.8 ha) (P 0.75) |
| 6 | 0.68 | Stafford Street | Worcester | 0.35 m of water at peak; over 30 cm for 0.5 h; 30 cm reached 0.5 h into the storm; worst hour 25 mm (82% of the storm); a culvert within 100 m is overtopped |
| 7 | 0.58 | Rockland Road | Auburn | 0.32 m of water at peak; over 30 cm for 1.0 h; 30 cm reached 9.0 h into the storm; worst hour 29 mm (84% of the storm); a culvert within 100 m is overtopped |
| 8 | 0.53 | Millbury Street | Grafton | 0.31 m of water at peak; over 30 cm for 5.0 h; 30 cm reached 9.0 h into the storm; worst hour 37 mm (68% of the storm) |
| 9 | 0.35 | James Street | Worcester | 0.26 m of water at peak; worst hour 25 mm (83% of the storm); a culvert within 100 m is overtopped |
| 10 | 0.32 | Sycamore Street | Millbury | 0.25 m of water at peak; worst hour 34 mm (69% of the storm); a culvert within 100 m is overtopped |
| 11 | 0.26 | Carleton Road | Millbury | 0.24 m of water at peak; worst hour 31 mm (66% of the storm); a culvert within 100 m is overtopped |
| 12 | 0.18 | Route 12 | Auburn | 0.21 m of water at peak; worst hour 30 mm (82% of the storm); a culvert within 100 m is overtopped |
| 13 | 0.17 | Fitzpatrick Road | Grafton | 0.20 m of water at peak; worst hour 37 mm (66% of the storm) |
| 14 | 0.16 | (unnamed) | Sutton | 0.20 m of water at peak; worst hour 43 mm (85% of the storm); a culvert within 100 m is overtopped |
| 15 | 0.14 | Washington Street | Worcester | 0.19 m of water at peak; worst hour 24 mm (73% of the storm); water beside the road 0.17 m below its crest (design freeboard 0.30 m; P 0.81); a culvert within 100 m is overtopped |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
