# Road-closure prototype: aug2020b_loss_aug2020b_worcester_20m

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on CPU (OpenMP)), 20 m grid, storm from 2020-08-27T11:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 8,807 |
| Expected closures (sum of probabilities) | 21.8 |
| Segments with closure probability >= 50% | 5 (1.7 km) |
| Further segments that may close (stream reaches the road crest) | 9 (4.3 km) |
| Culverts overtopped / surcharged | 16 / 0 of 1326 |
| Road segments cut off from hospitals | 48 |
| Worst added trip time to a hospital | 12.5 min |
| Heaviest hour of rain | 17.8 mm |
| Flood model run time | 1215 s |

## Checks against what happened

- Storm-day flood reports in the area: 0; water >= 10 cm within 100 m of 0% of them, vs 13% of random points (any day).
- MassDOT repeating flood sites in the area: 9; 0 have a segment within 150 m at P >= 0.5 (share of all segments at P >= 0.5: 0.1%).

## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 1.00 | Martin Luther King Jr Boulevard | Worcester | 1.22 m of water at peak; over 30 cm for 17.5 h; 30 cm reached 1.0 h into the storm; worst hour 12 mm (70% of the storm); water beside the road 1.14 m above its crest (design freeboard 0.30 m; P 1.00); road sag 3.2 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 12 mm; catchment 60.2 ha) (P 1.00) |
| 2 | 1.00 | Foster Street | Worcester | 0.68 m of water at peak; over 30 cm for 11.5 h; 30 cm reached 7.0 h into the storm; worst hour 13 mm (71% of the storm); water beside the road 0.40 m below its crest (design freeboard 0.30 m; P 0.25); a culvert within 100 m is overtopped |
| 3 | 1.00 | Foster Street | Worcester | 0.68 m of water at peak; over 30 cm for 11.5 h; 30 cm reached 7.0 h into the storm; worst hour 13 mm (71% of the storm); water beside the road 0.28 m below its crest (design freeboard 0.30 m; P 0.55); a culvert within 100 m is overtopped |
| 4 | 0.99 | Martin Luther King Jr Boulevard | Worcester | 0.52 m of water at peak; over 30 cm for 17.5 h; 30 cm reached 1.0 h into the storm; worst hour 12 mm (70% of the storm); water beside the road 0.01 m above its crest (design freeboard 0.30 m; P 0.98); runoff beside / along the road at 0.6 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.11); road sag 3.2 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 12 mm; catchment 60.2 ha) (P 1.00) |
| 5 | 0.63 | (unnamed) | Worcester | 0.33 m of water at peak; over 30 cm for 2.5 h; 30 cm reached 16.0 h into the storm; worst hour 11 mm (68% of the storm); a culvert within 100 m is overtopped |
| 6 | 0.42 | Stafford Street | Worcester | 0.28 m of water at peak; worst hour 12 mm (62% of the storm); a culvert within 100 m is overtopped |
| 7 | 0.42 | Ludlow Street | Worcester | 0.28 m of water at peak; worst hour 12 mm (61% of the storm); a culvert within 100 m is overtopped |
| 8 | 0.34 | Providence Street | Millbury | 0.26 m of water at peak; worst hour 10 mm (61% of the storm); a culvert within 100 m is overtopped |
| 9 | 0.30 | Millbury Street | Grafton | 0.25 m of water at peak; worst hour 10 mm (64% of the storm) |
| 10 | 0.21 | James Street | Worcester | 0.22 m of water at peak; worst hour 12 mm (61% of the storm); a culvert within 100 m is overtopped |
| 11 | 0.18 | Route 12 | Auburn | 0.21 m of water at peak; worst hour 15 mm (66% of the storm); a culvert within 100 m is overtopped |
| 12 | 0.13 | Washington Street | Worcester | 0.19 m of water at peak; worst hour 14 mm (71% of the storm); water beside the road 0.17 m below its crest (design freeboard 0.30 m; P 0.80); a culvert within 100 m is overtopped |
| 13 | 0.11 | Ramp-West Boylston Dr To Rt 190 Nb | Worcester | 0.18 m of water at peak; worst hour 7 mm (54% of the storm); water beside the road 0.03 m above its crest (design freeboard 0.30 m; P 0.99); road sag 0.8 m deep (underpass, drains sized for the 50-yr hour, 58 mm; peak hour here 7 mm; catchment 52.2 ha) (P 0.11) |
| 14 | 0.11 | Providence Road | Sutton | 0.18 m of water at peak; worst hour 10 mm (60% of the storm); a culvert within 100 m is overtopped |
| 15 | 0.11 | Hampton Street | Auburn | 0.18 m of water at peak; worst hour 16 mm (66% of the storm); water beside the road 0.42 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 0.7 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.21); a culvert within 100 m is overtopped |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
