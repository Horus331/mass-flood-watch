# Road-closure prototype: aug2023b_loss_aug2023b_millbury_20m

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on CPU (OpenMP)), 20 m grid, storm from 2023-08-18T05:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 8,013 |
| Expected closures (sum of probabilities) | 55.6 |
| Segments with closure probability >= 50% | 21 (12.6 km) |
| Further segments that may close (stream reaches the road crest) | 64 (33.0 km) |
| Culverts overtopped / surcharged | 74 / 0 of 1291 |
| Road segments cut off from hospitals | 266 |
| Worst added trip time to a hospital | 17.8 min |
| Heaviest hour of rain | 47.2 mm |
| Flood model run time | 1428 s |

## Checks against what happened

- Storm-day flood reports in the area: 0; water >= 10 cm within 100 m of 0% of them, vs 34% of random points (any day).
- MassDOT repeating flood sites in the area: 8; 0 have a segment within 150 m at P >= 0.5 (share of all segments at P >= 0.5: 0.3%).

## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 1.00 | Martin Luther King Jr Boulevard | Worcester | 2.95 m of water at peak; over 30 cm for 17.5 h; 30 cm reached 1.0 h into the storm; worst hour 21 mm (71% of the storm); water beside the road 2.87 m above its crest (design freeboard 0.30 m; P 1.00); road sag 3.2 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 21 mm; catchment 60.2 ha) (P 1.00); a culvert within 100 m is overtopped |
| 2 | 1.00 | Martin Luther King Jr Boulevard | Worcester | 2.25 m of water at peak; over 30 cm for 17.5 h; 30 cm reached 1.0 h into the storm; worst hour 21 mm (71% of the storm); water beside the road 1.93 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 2.4 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.95); road sag 3.2 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 21 mm; catchment 60.2 ha) (P 1.00); a culvert within 100 m is overtopped |
| 3 | 1.00 | Foster Street | Worcester | 1.23 m of water at peak; over 30 cm for 11.5 h; 30 cm reached 7.0 h into the storm; worst hour 22 mm (72% of the storm); water beside the road 0.40 m below its crest (design freeboard 0.30 m; P 0.25); a culvert within 100 m is overtopped |
| 4 | 1.00 | Foster Street | Worcester | 1.23 m of water at peak; over 30 cm for 11.5 h; 30 cm reached 7.0 h into the storm; worst hour 22 mm (72% of the storm); water beside the road 0.28 m below its crest (design freeboard 0.30 m; P 0.55); a culvert within 100 m is overtopped |
| 5 | 1.00 | (unnamed) | Worcester | 1.66 m of water at peak; over 30 cm for 9.5 h; 30 cm reached 9.0 h into the storm; worst hour 21 mm (65% of the storm); a culvert within 100 m is overtopped |
| 6 | 1.00 | East Park Terrace | Worcester | 0.73 m of water at peak; over 30 cm for 9.5 h; 30 cm reached 9.0 h into the storm; worst hour 22 mm (65% of the storm); water beside the road 0.63 m above its crest (design freeboard 0.30 m; P 1.00); road sag 4.3 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 22 mm; catchment 127.8 ha) (P 1.00) |
| 7 | 0.99 | Providence Road | Sutton | 0.53 m of water at peak; over 30 cm for 8.0 h; 30 cm reached 8.5 h into the storm; worst hour 44 mm (76% of the storm); a culvert within 100 m is overtopped |
| 8 | 0.98 | Shrewsbury Street | Worcester | 0.51 m of water at peak; over 30 cm for 8.5 h; 30 cm reached 10.0 h into the storm; worst hour 22 mm (64% of the storm); water beside the road 0.42 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.9 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 22 mm; catchment 127.8 ha) (P 0.99) |
| 9 | 0.98 | Providence Street | Millbury | 0.51 m of water at peak; over 30 cm for 10.5 h; 30 cm reached 8.0 h into the storm; worst hour 35 mm (69% of the storm); a culvert within 100 m is overtopped |
| 10 | 0.91 | Millbury Street | Grafton | 0.43 m of water at peak; over 30 cm for 9.5 h; 30 cm reached 9.0 h into the storm; worst hour 37 mm (68% of the storm) |
| 11 | 0.85 | Shrewsbury Street | Worcester | 0.40 m of water at peak; over 30 cm for 7.5 h; 30 cm reached 11.0 h into the storm; worst hour 22 mm (64% of the storm); water beside the road 0.32 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.9 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 22 mm; catchment 127.8 ha) (P 0.99) |
| 12 | 0.82 | Wellington Street | Worcester | 0.39 m of water at peak; over 30 cm for 2.5 h; 30 cm reached 9.0 h into the storm; worst hour 24 mm (77% of the storm); water beside the road 0.40 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.9 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 24 mm; catchment 15.1 ha) (P 0.97) |
| 13 | 0.82 | Murray Avenue | Worcester | 0.39 m of water at peak; over 30 cm for 2.5 h; 30 cm reached 9.0 h into the storm; worst hour 24 mm (78% of the storm); water beside the road 0.40 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.9 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 24 mm; catchment 15.1 ha) (P 0.97) |
| 14 | 0.79 | Fantasia Drive | Worcester | 0.38 m of water at peak; over 30 cm for 7.0 h; 30 cm reached 11.5 h into the storm; worst hour 22 mm (66% of the storm); water beside the road 0.31 m above its crest (design freeboard 0.30 m; P 1.00); road sag 1.3 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 22 mm; catchment 127.8 ha) (P 0.80) |
| 15 | 0.73 | Major Taylor Boulevard | Worcester | 0.36 m of water at peak; over 30 cm for 2.0 h; 30 cm reached 16.5 h into the storm; worst hour 22 mm (72% of the storm); water beside the road 0.12 m above its crest (design freeboard 0.30 m; P 1.00); road sag 1.1 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 21 mm; catchment 60.2 ha) (P 0.10); a culvert within 100 m is overtopped |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
