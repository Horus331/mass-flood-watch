# Road-closure prototype: aug2023b_loss_aug2023b_millbury_20m

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on CPU (OpenMP)), 20 m grid, storm from 2023-08-18T05:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 8,013 |
| Expected closures (sum of probabilities) | 136.0 |
| Segments with closure probability >= 50% | 82 (50.2 km) |
| Further segments that may close (stream reaches the road crest) | 171 (92.7 km) |
| Culverts overtopped / surcharged | 169 / 0 of 1291 |
| Road segments cut off from hospitals | 850 |
| Worst added trip time to a hospital | 25.3 min |
| Heaviest hour of rain | 47.2 mm |
| Flood model run time | 1554 s |

## Checks against what happened

- Storm-day flood reports in the area: 0; water >= 10 cm within 100 m of 0% of them, vs 61% of random points (any day).
- MassDOT repeating flood sites in the area: 8; 2 have a segment within 150 m at P >= 0.5 (share of all segments at P >= 0.5: 1.0%).

## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 1.00 | Martin Luther King Jr Boulevard | Worcester | 3.64 m of water at peak; over 30 cm for 17.5 h; 30 cm reached 1.0 h into the storm; worst hour 21 mm (71% of the storm); water beside the road 3.56 m above its crest (design freeboard 0.30 m; P 1.00); fast water: depth x speed 0.21 m2/s (small cars unstable from 0.3); runoff beside / along the road at 1.2 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.65); road sag 3.2 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 21 mm; catchment 60.2 ha) (P 1.00); a culvert within 100 m is overtopped |
| 2 | 1.00 | Martin Luther King Jr Boulevard | Worcester | 2.94 m of water at peak; over 30 cm for 17.5 h; 30 cm reached 1.0 h into the storm; worst hour 21 mm (71% of the storm); water beside the road 2.62 m above its crest (design freeboard 0.30 m; P 1.00); fast water: depth x speed 0.26 m2/s (small cars unstable from 0.3); runoff beside / along the road at 2.8 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.97); road sag 3.2 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 21 mm; catchment 60.2 ha) (P 1.00); a culvert within 100 m is overtopped |
| 3 | 1.00 | Shrewsbury Street | Worcester | 0.67 m of water at peak; over 30 cm for 9.5 h; 30 cm reached 9.0 h into the storm; worst hour 22 mm (64% of the storm); water beside the road 0.59 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.9 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 22 mm; catchment 127.8 ha) (P 1.00) |
| 4 | 1.00 | Shrewsbury Street | Worcester | 0.77 m of water at peak; over 30 cm for 10.0 h; 30 cm reached 8.5 h into the storm; worst hour 22 mm (64% of the storm); water beside the road 0.69 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.9 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 22 mm; catchment 127.8 ha) (P 1.00) |
| 5 | 1.00 | Foster Street | Worcester | 1.92 m of water at peak; over 30 cm for 11.5 h; 30 cm reached 7.0 h into the storm; worst hour 22 mm (72% of the storm); water beside the road 0.07 m below its crest (design freeboard 0.30 m; P 0.94); a culvert within 100 m is overtopped |
| 6 | 1.00 | Foster Street | Worcester | 1.92 m of water at peak; over 30 cm for 11.5 h; 30 cm reached 7.0 h into the storm; worst hour 22 mm (72% of the storm); water beside the road 0.06 m below its crest (design freeboard 0.30 m; P 0.95); a culvert within 100 m is overtopped |
| 7 | 1.00 | Major Taylor Boulevard | Worcester | 1.05 m of water at peak; over 30 cm for 8.0 h; 30 cm reached 10.5 h into the storm; worst hour 22 mm (72% of the storm); water beside the road 0.80 m above its crest (design freeboard 0.30 m; P 1.00); road sag 1.1 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 21 mm; catchment 60.2 ha) (P 1.00); a culvert within 100 m is overtopped |
| 8 | 1.00 | Major Taylor Boulevard | Worcester | 1.05 m of water at peak; over 30 cm for 8.0 h; 30 cm reached 10.5 h into the storm; worst hour 22 mm (72% of the storm); water beside the road 0.80 m above its crest (design freeboard 0.30 m; P 1.00); road sag 1.1 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 21 mm; catchment 60.2 ha) (P 1.00); a culvert within 100 m is overtopped |
| 9 | 1.00 | Providence Street | Millbury | 0.81 m of water at peak; over 30 cm for 10.5 h; 30 cm reached 8.0 h into the storm; worst hour 35 mm (69% of the storm); a culvert within 100 m is overtopped |
| 10 | 1.00 | Millbury Street | Grafton | 0.67 m of water at peak; over 30 cm for 10.0 h; 30 cm reached 8.5 h into the storm; worst hour 37 mm (68% of the storm); runoff beside / along the road at 0.6 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.12) |
| 11 | 1.00 | Providence Road | Sutton | 0.73 m of water at peak; over 30 cm for 9.5 h; 30 cm reached 8.0 h into the storm; worst hour 44 mm (76% of the storm); a culvert within 100 m is overtopped |
| 12 | 1.00 | (unnamed) | Worcester | 3.55 m of water at peak; over 30 cm for 10.0 h; 30 cm reached 8.5 h into the storm; worst hour 21 mm (65% of the storm); a culvert within 100 m is overtopped |
| 13 | 1.00 | Bridge Street | Worcester | 0.88 m of water at peak; over 30 cm for 7.5 h; 30 cm reached 11.0 h into the storm; worst hour 22 mm (71% of the storm); water beside the road 0.57 m above its crest (design freeboard 0.30 m; P 1.00); road sag 2.3 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 22 mm; catchment 22.1 ha) (P 1.00); a culvert within 100 m is overtopped |
| 14 | 1.00 | East Park Terrace | Worcester | 0.99 m of water at peak; over 30 cm for 10.5 h; 30 cm reached 8.0 h into the storm; worst hour 22 mm (65% of the storm); water beside the road 0.89 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 0.7 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.17); road sag 4.3 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 22 mm; catchment 127.8 ha) (P 1.00) |
| 15 | 1.00 | Fantasia Drive | Worcester | 0.65 m of water at peak; over 30 cm for 9.5 h; 30 cm reached 9.0 h into the storm; worst hour 22 mm (66% of the storm); water beside the road 0.58 m above its crest (design freeboard 0.30 m; P 1.00); road sag 1.3 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 22 mm; catchment 127.8 ha) (P 1.00) |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
