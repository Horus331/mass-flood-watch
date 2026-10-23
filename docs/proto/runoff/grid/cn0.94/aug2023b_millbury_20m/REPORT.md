# Road-closure prototype: aug2023b_loss_aug2023b_millbury_20m

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on CPU (OpenMP)), 20 m grid, storm from 2023-08-18T05:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 8,013 |
| Expected closures (sum of probabilities) | 34.8 |
| Segments with closure probability >= 50% | 10 (5.7 km) |
| Further segments that may close (stream reaches the road crest) | 20 (10.6 km) |
| Culverts overtopped / surcharged | 44 / 0 of 1291 |
| Road segments cut off from hospitals | 190 |
| Worst added trip time to a hospital | 14.8 min |
| Heaviest hour of rain | 47.2 mm |
| Flood model run time | 1375 s |

## Checks against what happened

- Storm-day flood reports in the area: 0; water >= 10 cm within 100 m of 0% of them, vs 17% of random points (any day).
- MassDOT repeating flood sites in the area: 8; 0 have a segment within 150 m at P >= 0.5 (share of all segments at P >= 0.5: 0.1%).

## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 1.00 | Martin Luther King Jr Boulevard | Worcester | 1.93 m of water at peak; over 30 cm for 17.5 h; 30 cm reached 1.0 h into the storm; worst hour 21 mm (71% of the storm); water beside the road 1.85 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 1.1 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.42); road sag 3.2 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 21 mm; catchment 60.2 ha) (P 1.00) |
| 2 | 1.00 | Martin Luther King Jr Boulevard | Worcester | 1.23 m of water at peak; over 30 cm for 17.5 h; 30 cm reached 1.0 h into the storm; worst hour 21 mm (71% of the storm); water beside the road 0.72 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 2.4 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.66); road sag 3.2 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 21 mm; catchment 60.2 ha) (P 1.00) |
| 3 | 1.00 | Foster Street | Worcester | 0.90 m of water at peak; over 30 cm for 11.5 h; 30 cm reached 7.0 h into the storm; worst hour 22 mm (72% of the storm); water beside the road 0.40 m below its crest (design freeboard 0.30 m; P 0.25); a culvert within 100 m is overtopped |
| 4 | 1.00 | Foster Street | Worcester | 0.90 m of water at peak; over 30 cm for 11.5 h; 30 cm reached 7.0 h into the storm; worst hour 22 mm (72% of the storm); water beside the road 0.28 m below its crest (design freeboard 0.30 m; P 0.55); a culvert within 100 m is overtopped |
| 5 | 1.00 | (unnamed) | Worcester | 1.13 m of water at peak; over 30 cm for 9.0 h; 30 cm reached 9.5 h into the storm; worst hour 21 mm (65% of the storm); a culvert within 100 m is overtopped |
| 6 | 1.00 | East Park Terrace | Worcester | 0.57 m of water at peak; over 30 cm for 8.0 h; 30 cm reached 10.5 h into the storm; worst hour 22 mm (65% of the storm); water beside the road 0.47 m above its crest (design freeboard 0.30 m; P 1.00); road sag 4.3 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 22 mm; catchment 127.8 ha) (P 1.00) |
| 7 | 0.95 | Providence Street | Millbury | 0.46 m of water at peak; over 30 cm for 10.0 h; 30 cm reached 8.0 h into the storm; worst hour 35 mm (69% of the storm); a culvert within 100 m is overtopped |
| 8 | 0.94 | Providence Road | Sutton | 0.46 m of water at peak; over 30 cm for 6.5 h; 30 cm reached 9.0 h into the storm; worst hour 44 mm (76% of the storm); a culvert within 100 m is overtopped |
| 9 | 0.70 | Millbury Street | Grafton | 0.35 m of water at peak; over 30 cm for 9.0 h; 30 cm reached 9.0 h into the storm; worst hour 37 mm (68% of the storm) |
| 10 | 0.68 | Shrewsbury Street | Worcester | 0.35 m of water at peak; over 30 cm for 5.0 h; 30 cm reached 13.5 h into the storm; worst hour 22 mm (64% of the storm); water beside the road 0.26 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.9 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 22 mm; catchment 127.8 ha) (P 0.84) |
| 11 | 0.42 | Stafford Street | Worcester | 0.28 m of water at peak; worst hour 25 mm (82% of the storm); a culvert within 100 m is overtopped |
| 12 | 0.42 | Ludlow Street | Worcester | 0.28 m of water at peak; worst hour 24 mm (83% of the storm); a culvert within 100 m is overtopped |
| 13 | 0.39 | Carleton Road | Millbury | 0.27 m of water at peak; worst hour 31 mm (66% of the storm); a culvert within 100 m is overtopped |
| 14 | 0.33 | (unnamed) | Sutton | 0.26 m of water at peak; worst hour 44 mm (90% of the storm); a culvert within 100 m is overtopped |
| 15 | 0.33 | Sycamore Street | Millbury | 0.26 m of water at peak; worst hour 34 mm (69% of the storm); a culvert within 100 m is overtopped |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
