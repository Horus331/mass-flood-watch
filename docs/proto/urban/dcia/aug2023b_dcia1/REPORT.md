# Road-closure prototype: aug2023b_loss_aug2023b_dcia1

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on CPU (OpenMP)), 20 m grid, storm from 2023-08-18T05:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 7,807 |
| Expected closures (sum of probabilities) | 85.2 |
| Segments with closure probability >= 50% | 41 (23.2 km) |
| Further segments that may close (stream reaches the road crest) | 125 (69.8 km) |
| Culverts overtopped / surcharged | 109 / 0 of 1291 |
| Road segments cut off from hospitals | 511 |
| Worst added trip time to a hospital | 18.6 min |
| Heaviest hour of rain | 47.2 mm |
| Flood model run time | 746 s |

## Checks against what happened

- Storm-day flood reports in the area: 0; water >= 10 cm within 100 m of 0% of them, vs 55% of random points (any day).
- MassDOT repeating flood sites in the area: 8; 2 have a segment within 150 m at P >= 0.5 (share of all segments at P >= 0.5: 0.5%).

## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 1.00 | Martin Luther King Jr Boulevard | Worcester | 3.25 m of water at peak; over 30 cm for 17.5 h; 30 cm reached 1.0 h into the storm; worst hour 21 mm (71% of the storm); water beside the road 3.17 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 2.1 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.95); road sag 3.2 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 21 mm; catchment 60.2 ha) (P 1.00); a culvert within 100 m is overtopped |
| 2 | 1.00 | Martin Luther King Jr Boulevard | Worcester | 2.55 m of water at peak; over 30 cm for 17.5 h; 30 cm reached 1.0 h into the storm; worst hour 21 mm (71% of the storm); water beside the road 2.23 m above its crest (design freeboard 0.30 m; P 1.00); fast water: depth x speed 0.28 m2/s (small cars unstable from 0.3); runoff beside / along the road at 4.6 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.81); road sag 3.2 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 21 mm; catchment 60.2 ha) (P 1.00); a culvert within 100 m is overtopped |
| 3 | 1.00 | Foster Street | Worcester | 1.52 m of water at peak; over 30 cm for 10.0 h; 30 cm reached 8.5 h into the storm; worst hour 22 mm (72% of the storm); water beside the road 0.31 m below its crest (design freeboard 0.30 m; P 0.48); a culvert within 100 m is overtopped |
| 4 | 1.00 | Foster Street | Worcester | 1.52 m of water at peak; over 30 cm for 10.0 h; 30 cm reached 8.5 h into the storm; worst hour 22 mm (72% of the storm); water beside the road 0.21 m below its crest (design freeboard 0.30 m; P 0.73); runoff beside / along the road at 2.1 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.19); a culvert within 100 m is overtopped |
| 5 | 1.00 | Major Taylor Boulevard | Worcester | 0.66 m of water at peak; over 30 cm for 6.5 h; 30 cm reached 11.5 h into the storm; worst hour 22 mm (72% of the storm); water beside the road 0.41 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 1.1 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.11); road sag 1.1 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 21 mm; catchment 60.2 ha) (P 0.96); a culvert within 100 m is overtopped |
| 6 | 1.00 | Major Taylor Boulevard | Worcester | 0.66 m of water at peak; over 30 cm for 6.5 h; 30 cm reached 11.5 h into the storm; worst hour 22 mm (72% of the storm); water beside the road 0.41 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 1.1 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.11); road sag 1.1 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 21 mm; catchment 60.2 ha) (P 0.96); a culvert within 100 m is overtopped |
| 7 | 1.00 | (unnamed) | Worcester | 2.19 m of water at peak; over 30 cm for 10.0 h; 30 cm reached 8.5 h into the storm; worst hour 21 mm (65% of the storm); a culvert within 100 m is overtopped |
| 8 | 1.00 | East Park Terrace | Worcester | 0.84 m of water at peak; over 30 cm for 10.5 h; 30 cm reached 8.0 h into the storm; worst hour 22 mm (65% of the storm); water beside the road 0.74 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 1.2 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.17); road sag 4.3 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 22 mm; catchment 127.8 ha) (P 1.00) |
| 9 | 1.00 | Shrewsbury Street | Worcester | 0.62 m of water at peak; over 30 cm for 9.5 h; 30 cm reached 9.0 h into the storm; worst hour 22 mm (64% of the storm); water beside the road 0.54 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.9 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 22 mm; catchment 127.8 ha) (P 1.00) |
| 10 | 1.00 | Providence Road | Sutton | 0.58 m of water at peak; over 30 cm for 7.5 h; 30 cm reached 8.0 h into the storm; worst hour 44 mm (76% of the storm); a culvert within 100 m is overtopped |
| 11 | 0.99 | Providence Street | Millbury | 0.54 m of water at peak; over 30 cm for 10.0 h; 30 cm reached 8.5 h into the storm; worst hour 35 mm (69% of the storm); a culvert within 100 m is overtopped |
| 12 | 0.99 | Wellington Street | Worcester | 0.52 m of water at peak; over 30 cm for 3.5 h; 30 cm reached 8.5 h into the storm; worst hour 24 mm (77% of the storm); water beside the road 0.49 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.9 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 24 mm; catchment 15.1 ha) (P 1.00) |
| 13 | 0.99 | Murray Avenue | Worcester | 0.52 m of water at peak; over 30 cm for 3.5 h; 30 cm reached 8.5 h into the storm; worst hour 24 mm (78% of the storm); water beside the road 0.49 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 0.8 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.21); road sag 0.9 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 24 mm; catchment 15.1 ha) (P 1.00) |
| 14 | 0.98 | Shrewsbury Street | Worcester | 0.52 m of water at peak; over 30 cm for 9.0 h; 30 cm reached 9.5 h into the storm; worst hour 22 mm (64% of the storm); water beside the road 0.43 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.9 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 22 mm; catchment 127.8 ha) (P 1.00) |
| 15 | 0.98 | Chasm Loop Trail | Sutton | 0.50 m of water at peak; over 30 cm for 10.5 h; 30 cm reached 8.0 h into the storm; worst hour 34 mm (90% of the storm); runoff beside / along the road at 5.0 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.68) |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
