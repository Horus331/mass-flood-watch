# Road-closure prototype: aug2023b_loss_aug2023b_dcia

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on CPU (OpenMP)), 20 m grid, storm from 2023-08-18T05:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 7,807 |
| Expected closures (sum of probabilities) | 68.6 |
| Segments with closure probability >= 50% | 32 (19.1 km) |
| Further segments that may close (stream reaches the road crest) | 99 (55.1 km) |
| Culverts overtopped / surcharged | 86 / 0 of 1291 |
| Road segments cut off from hospitals | 321 |
| Worst added trip time to a hospital | 17.1 min |
| Heaviest hour of rain | 47.2 mm |
| Flood model run time | 543 s |

## Checks against what happened

- Storm-day flood reports in the area: 0; water >= 10 cm within 100 m of 0% of them, vs 48% of random points (any day).
- MassDOT repeating flood sites in the area: 8; 0 have a segment within 150 m at P >= 0.5 (share of all segments at P >= 0.5: 0.4%).

## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 1.00 | Martin Luther King Jr Boulevard | Worcester | 3.09 m of water at peak; over 30 cm for 17.5 h; 30 cm reached 1.0 h into the storm; worst hour 21 mm (71% of the storm); water beside the road 3.01 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 1.2 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.46); road sag 3.2 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 21 mm; catchment 60.2 ha) (P 1.00); a culvert within 100 m is overtopped |
| 2 | 1.00 | Martin Luther King Jr Boulevard | Worcester | 2.39 m of water at peak; over 30 cm for 17.5 h; 30 cm reached 1.0 h into the storm; worst hour 21 mm (71% of the storm); water beside the road 2.06 m above its crest (design freeboard 0.30 m; P 1.00); fast water: depth x speed 0.21 m2/s (small cars unstable from 0.3); runoff beside / along the road at 4.5 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.83); road sag 3.2 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 21 mm; catchment 60.2 ha) (P 1.00); a culvert within 100 m is overtopped |
| 3 | 1.00 | Foster Street | Worcester | 1.36 m of water at peak; over 30 cm for 9.5 h; 30 cm reached 9.0 h into the storm; worst hour 22 mm (72% of the storm); water beside the road 0.37 m below its crest (design freeboard 0.30 m; P 0.31); a culvert within 100 m is overtopped |
| 4 | 1.00 | Foster Street | Worcester | 1.36 m of water at peak; over 30 cm for 9.5 h; 30 cm reached 9.0 h into the storm; worst hour 22 mm (72% of the storm); water beside the road 0.21 m below its crest (design freeboard 0.30 m; P 0.73); runoff beside / along the road at 2.1 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.19); a culvert within 100 m is overtopped |
| 5 | 1.00 | (unnamed) | Worcester | 1.77 m of water at peak; over 30 cm for 9.5 h; 30 cm reached 9.0 h into the storm; worst hour 21 mm (65% of the storm); a culvert within 100 m is overtopped |
| 6 | 1.00 | East Park Terrace | Worcester | 0.77 m of water at peak; over 30 cm for 10.0 h; 30 cm reached 8.5 h into the storm; worst hour 22 mm (65% of the storm); water beside the road 0.67 m above its crest (design freeboard 0.30 m; P 1.00); road sag 4.3 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 22 mm; catchment 127.8 ha) (P 1.00) |
| 7 | 0.99 | Shrewsbury Street | Worcester | 0.55 m of water at peak; over 30 cm for 9.5 h; 30 cm reached 9.0 h into the storm; worst hour 22 mm (64% of the storm); water beside the road 0.47 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.9 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 22 mm; catchment 127.8 ha) (P 1.00) |
| 8 | 0.99 | Providence Road | Sutton | 0.53 m of water at peak; over 30 cm for 7.5 h; 30 cm reached 8.0 h into the storm; worst hour 44 mm (76% of the storm); a culvert within 100 m is overtopped |
| 9 | 0.98 | Major Taylor Boulevard | Worcester | 0.50 m of water at peak; over 30 cm for 5.0 h; 30 cm reached 13.5 h into the storm; worst hour 22 mm (72% of the storm); water beside the road 0.25 m above its crest (design freeboard 0.30 m; P 1.00); road sag 1.1 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 21 mm; catchment 60.2 ha) (P 0.54); a culvert within 100 m is overtopped |
| 10 | 0.98 | Major Taylor Boulevard | Worcester | 0.50 m of water at peak; over 30 cm for 5.0 h; 30 cm reached 13.5 h into the storm; worst hour 22 mm (72% of the storm); water beside the road 0.25 m above its crest (design freeboard 0.30 m; P 1.00); road sag 1.1 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 21 mm; catchment 60.2 ha) (P 0.54); a culvert within 100 m is overtopped |
| 11 | 0.97 | Providence Street | Millbury | 0.49 m of water at peak; over 30 cm for 10.0 h; 30 cm reached 8.5 h into the storm; worst hour 35 mm (69% of the storm); a culvert within 100 m is overtopped |
| 12 | 0.97 | Wellington Street | Worcester | 0.49 m of water at peak; over 30 cm for 3.5 h; 30 cm reached 8.5 h into the storm; worst hour 24 mm (77% of the storm); water beside the road 0.47 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.9 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 24 mm; catchment 15.1 ha) (P 0.99) |
| 13 | 0.97 | Murray Avenue | Worcester | 0.49 m of water at peak; over 30 cm for 3.5 h; 30 cm reached 8.5 h into the storm; worst hour 24 mm (78% of the storm); water beside the road 0.47 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 1.0 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.20); road sag 0.9 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 24 mm; catchment 15.1 ha) (P 0.99) |
| 14 | 0.93 | Shrewsbury Street | Worcester | 0.45 m of water at peak; over 30 cm for 8.5 h; 30 cm reached 10.0 h into the storm; worst hour 22 mm (64% of the storm); water beside the road 0.37 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.9 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 22 mm; catchment 127.8 ha) (P 1.00) |
| 15 | 0.90 | Fantasia Drive | Worcester | 0.43 m of water at peak; over 30 cm for 8.0 h; 30 cm reached 10.5 h into the storm; worst hour 22 mm (66% of the storm); water beside the road 0.36 m above its crest (design freeboard 0.30 m; P 1.00); road sag 1.3 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 22 mm; catchment 127.8 ha) (P 0.90) |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
