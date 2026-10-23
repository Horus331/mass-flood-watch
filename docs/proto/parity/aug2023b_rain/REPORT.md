# Road-closure prototype: aug2023b_loss_aug2023b_rain

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on CPU (OpenMP)), 20 m grid, storm from 2023-08-18T05:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 8,013 |
| Expected closures (sum of probabilities) | 31.6 |
| Segments with closure probability >= 50% | 11 (6.6 km) |
| Further segments that may close (stream reaches the road crest) | 15 (8.8 km) |
| Culverts overtopped / surcharged | 43 / 0 of 1291 |
| Road segments cut off from hospitals | 155 |
| Worst added trip time to a hospital | 14.1 min |
| Heaviest hour of rain | 47.2 mm |
| Flood model run time | 445 s |

## Checks against what happened

- Storm-day flood reports in the area: 0; water >= 10 cm within 100 m of 0% of them, vs 18% of random points (any day).
- MassDOT repeating flood sites in the area: 8; 0 have a segment within 150 m at P >= 0.5 (share of all segments at P >= 0.5: 0.1%).

## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 1.00 | Martin Luther King Jr Boulevard | Worcester | 1.60 m of water at peak; over 30 cm for 17.5 h; 30 cm reached 1.0 h into the storm; worst hour 21 mm (71% of the storm); water beside the road 1.52 m above its crest (design freeboard 0.30 m; P 1.00); fast water: depth x speed 0.24 m2/s (small cars unstable from 0.3); runoff beside / along the road at 2.1 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.18); road sag 3.2 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 21 mm; catchment 60.2 ha) (P 1.00) |
| 2 | 1.00 | Martin Luther King Jr Boulevard | Worcester | 0.90 m of water at peak; over 30 cm for 17.5 h; 30 cm reached 1.0 h into the storm; worst hour 21 mm (71% of the storm); water beside the road 0.39 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 3.8 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.73); road sag 3.2 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 21 mm; catchment 60.2 ha) (P 1.00) |
| 3 | 1.00 | Foster Street | Worcester | 0.81 m of water at peak; over 30 cm for 11.5 h; 30 cm reached 7.0 h into the storm; worst hour 22 mm (72% of the storm); water beside the road 0.37 m below its crest (design freeboard 0.30 m; P 0.31); a culvert within 100 m is overtopped |
| 4 | 1.00 | Foster Street | Worcester | 0.81 m of water at peak; over 30 cm for 11.5 h; 30 cm reached 7.0 h into the storm; worst hour 22 mm (72% of the storm); water beside the road 0.21 m below its crest (design freeboard 0.30 m; P 0.73); runoff beside / along the road at 2.1 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.19); a culvert within 100 m is overtopped |
| 5 | 1.00 | (unnamed) | Worcester | 1.03 m of water at peak; over 30 cm for 8.5 h; 30 cm reached 10.0 h into the storm; worst hour 21 mm (65% of the storm); a culvert within 100 m is overtopped |
| 6 | 0.94 | East Park Terrace | Worcester | 0.46 m of water at peak; over 30 cm for 5.5 h; 30 cm reached 13.0 h into the storm; worst hour 22 mm (65% of the storm); water beside the road 0.36 m above its crest (design freeboard 0.30 m; P 1.00); road sag 4.3 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 22 mm; catchment 127.8 ha) (P 0.94) |
| 7 | 0.94 | Providence Street | Millbury | 0.46 m of water at peak; over 30 cm for 8.5 h; 30 cm reached 8.0 h into the storm; worst hour 35 mm (69% of the storm); a culvert within 100 m is overtopped |
| 8 | 0.91 | Providence Road | Sutton | 0.43 m of water at peak; over 30 cm for 3.0 h; 30 cm reached 9.0 h into the storm; worst hour 44 mm (76% of the storm); a culvert within 100 m is overtopped |
| 9 | 0.61 | Millbury Street | Grafton | 0.33 m of water at peak; over 30 cm for 7.0 h; 30 cm reached 9.0 h into the storm; worst hour 37 mm (68% of the storm) |
| 10 | 0.51 | Ludlow Street | Worcester | 0.30 m of water at peak; worst hour 24 mm (83% of the storm); a culvert within 100 m is overtopped |
| 11 | 0.51 | Stafford Street | Worcester | 0.30 m of water at peak; worst hour 25 mm (82% of the storm); a culvert within 100 m is overtopped |
| 12 | 0.33 | Carleton Road | Millbury | 0.26 m of water at peak; worst hour 31 mm (66% of the storm); a culvert within 100 m is overtopped |
| 13 | 0.33 | Route 12 | Auburn | 0.26 m of water at peak; worst hour 30 mm (82% of the storm); water beside the road 3.09 m above its crest (design freeboard 0.30 m; P 1.00); fast water: depth x speed 0.35 m2/s (small cars unstable from 0.3); runoff beside / along the road at 5.0 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 1.00); a culvert within 100 m is overtopped |
| 14 | 0.32 | Sycamore Street | Millbury | 0.25 m of water at peak; worst hour 34 mm (69% of the storm); a culvert within 100 m is overtopped |
| 15 | 0.27 | Shrewsbury Street | Worcester | 0.24 m of water at peak; worst hour 22 mm (64% of the storm); water beside the road 0.16 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.9 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 22 mm; catchment 127.8 ha) (P 0.47) |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
