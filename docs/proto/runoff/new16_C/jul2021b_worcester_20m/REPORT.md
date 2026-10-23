# Road-closure prototype: jul2021b_loss_jul2021b_worcester_20m

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on CPU (OpenMP)), 20 m grid, storm from 2021-07-17T14:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 8,553 |
| Expected closures (sum of probabilities) | 209.0 |
| Segments with closure probability >= 50% | 154 (78.5 km) |
| Further segments that may close (stream reaches the road crest) | 211 (114.1 km) |
| Culverts overtopped / surcharged | 204 / 0 of 1186 |
| Road segments cut off from hospitals | 999 |
| Worst added trip time to a hospital | 35.0 min |
| Heaviest hour of rain | 46.9 mm |
| Flood model run time | 2303 s |

## Checks against what happened

- Storm-day flood reports in the area: 3; water >= 10 cm within 100 m of 33% of them, vs 64% of random points (any day).
- Segments flagged impassable are 0.63x as likely as an average segment to have a report within 200 m.
- MassDOT repeating flood sites in the area: 9; 4 have a segment within 150 m at P >= 0.5 (share of all segments at P >= 0.5: 1.8%).

## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 1.00 | Martin Luther King Jr Boulevard | Worcester | 4.21 m of water at peak; over 30 cm for 23.5 h; 30 cm reached 1.0 h into the storm; worst hour 21 mm (40% of the storm); water beside the road 4.13 m above its crest (design freeboard 0.30 m; P 1.00); fast water: depth x speed 0.21 m2/s (small cars unstable from 0.3); runoff beside / along the road at 0.7 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.23); road sag 3.2 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 21 mm; catchment 60.2 ha) (P 1.00); a culvert within 100 m is overtopped |
| 2 | 1.00 | Martin Luther King Jr Boulevard | Worcester | 3.51 m of water at peak; over 30 cm for 23.5 h; 30 cm reached 1.0 h into the storm; worst hour 21 mm (40% of the storm); water beside the road 3.19 m above its crest (design freeboard 0.30 m; P 1.00); fast water: depth x speed 0.26 m2/s (small cars unstable from 0.3); runoff beside / along the road at 2.7 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.98); road sag 3.2 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 21 mm; catchment 60.2 ha) (P 1.00); a culvert within 100 m is overtopped |
| 3 | 1.00 | Shrewsbury Street | Worcester | 0.82 m of water at peak; over 30 cm for 16.0 h; 30 cm reached 8.5 h into the storm; worst hour 21 mm (42% of the storm); water beside the road 0.74 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.9 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 20 mm; catchment 127.8 ha) (P 1.00) |
| 4 | 1.00 | Shrewsbury Street | Worcester | 0.93 m of water at peak; over 30 cm for 16.5 h; 30 cm reached 8.0 h into the storm; worst hour 21 mm (42% of the storm); water beside the road 0.85 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.9 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 20 mm; catchment 127.8 ha) (P 1.00) |
| 5 | 1.00 | Foster Street | Worcester | 2.47 m of water at peak; over 30 cm for 17.5 h; 30 cm reached 7.0 h into the storm; worst hour 22 mm (41% of the storm); water beside the road 0.49 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 1.7 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.79); road sag 1.2 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 21 mm; catchment 22.1 ha) (P 1.00); a culvert within 100 m is overtopped |
| 6 | 1.00 | Stafford Street | Worcester | 0.97 m of water at peak; over 30 cm for 17.0 h; 30 cm reached 7.5 h into the storm; worst hour 28 mm (39% of the storm); water beside the road 0.61 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 0.5 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.10); a culvert within 100 m is overtopped |
| 7 | 1.00 | Major Taylor Boulevard | Worcester | 1.62 m of water at peak; over 30 cm for 15.5 h; 30 cm reached 9.0 h into the storm; worst hour 21 mm (40% of the storm); water beside the road 1.38 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 0.8 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.30); road sag 1.1 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 21 mm; catchment 60.2 ha) (P 1.00); a culvert within 100 m is overtopped |
| 8 | 1.00 | Foster Street | Worcester | 2.47 m of water at peak; over 30 cm for 17.5 h; 30 cm reached 7.0 h into the storm; worst hour 22 mm (41% of the storm); water beside the road 0.50 m above its crest (design freeboard 0.30 m; P 1.00); road sag 1.2 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 21 mm; catchment 22.1 ha) (P 1.00); a culvert within 100 m is overtopped |
| 9 | 1.00 | Martin Luther King Jr Boulevard | Worcester | 1.18 m of water at peak; over 30 cm for 12.5 h; 30 cm reached 12.0 h into the storm; worst hour 21 mm (39% of the storm); water beside the road 1.01 m above its crest (design freeboard 0.30 m; P 1.00); a culvert within 100 m is overtopped |
| 10 | 1.00 | Major Taylor Boulevard | Worcester | 1.62 m of water at peak; over 30 cm for 15.5 h; 30 cm reached 9.0 h into the storm; worst hour 21 mm (40% of the storm); water beside the road 1.38 m above its crest (design freeboard 0.30 m; P 1.00); road sag 1.1 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 21 mm; catchment 60.2 ha) (P 1.00); a culvert within 100 m is overtopped |
| 11 | 1.00 | James Street | Worcester | 0.69 m of water at peak; over 30 cm for 16.5 h; 30 cm reached 8.0 h into the storm; worst hour 28 mm (41% of the storm); a culvert within 100 m is overtopped |
| 12 | 1.00 | Cambridge Street | Worcester | 0.86 m of water at peak; over 30 cm for 15.5 h; 30 cm reached 9.0 h into the storm; worst hour 28 mm (45% of the storm); water beside the road 0.71 m above its crest (design freeboard 0.30 m; P 1.00); road sag 2.0 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 26 mm; catchment 77.2 ha) (P 1.00) |
| 13 | 1.00 | Thomas Street | Worcester | 1.01 m of water at peak; over 30 cm for 11.0 h; 30 cm reached 13.5 h into the storm; worst hour 21 mm (39% of the storm); water beside the road 0.97 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.5 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 21 mm; catchment 60.2 ha) (P 1.00); a culvert within 100 m is overtopped |
| 14 | 1.00 | Providence Street | Millbury | 1.08 m of water at peak; over 30 cm for 17.5 h; 30 cm reached 7.0 h into the storm; worst hour 33 mm (72% of the storm); a culvert within 100 m is overtopped |
| 15 | 1.00 | Major Taylor Boulevard | Worcester | 0.85 m of water at peak; over 30 cm for 9.5 h; 30 cm reached 15.0 h into the storm; worst hour 20 mm (39% of the storm); water beside the road 0.37 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 0.6 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.15); road sag 0.8 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 20 mm; catchment 60.2 ha) (P 0.86); a culvert within 100 m is overtopped |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
