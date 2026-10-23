# Road-closure prototype: aug2021_loss_aug2021_worcester_20m

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on CPU (OpenMP)), 20 m grid, storm from 2021-08-19T09:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 8,566 |
| Expected closures (sum of probabilities) | 415.8 |
| Segments with closure probability >= 50% | 349 (202.2 km) |
| Further segments that may close (stream reaches the road crest) | 379 (188.1 km) |
| Culverts overtopped / surcharged | 357 / 7 of 1347 |
| Road segments cut off from hospitals | 1967 |
| Worst added trip time to a hospital | 38.4 min |
| Heaviest hour of rain | 89.6 mm |
| Flood model run time | 1370 s |

## Checks against what happened

- Storm-day flood reports in the area: 5; water >= 10 cm within 100 m of 60% of them, vs 67% of random points (any day).
- Segments flagged impassable are 2.15x as likely as an average segment to have a report within 200 m.
- MassDOT repeating flood sites in the area: 10; 6 have a segment within 150 m at P >= 0.5 (share of all segments at P >= 0.5: 4.1%).

## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 1.00 | (unnamed) | Worcester | 0.66 m of water at peak; over 30 cm for 10.0 h; 30 cm reached 7.5 h into the storm; worst hour 28 mm (47% of the storm); water beside the road 0.54 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 0.7 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.24); road sag 2.0 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 28 mm; catchment 77.2 ha) (P 1.00) |
| 2 | 1.00 | Route 146 | Worcester | 0.76 m of water at peak; over 30 cm for 8.5 h; 30 cm reached 8.5 h into the storm; worst hour 29 mm (44% of the storm); runoff beside / along the road at 0.7 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.19); a culvert within 100 m is overtopped |
| 3 | 1.00 | Martin Luther King Jr Boulevard | Worcester | 4.33 m of water at peak; over 30 cm for 17.5 h; 30 cm reached 1.0 h into the storm; worst hour 24 mm (43% of the storm); water beside the road 4.25 m above its crest (design freeboard 0.30 m; P 1.00); fast water: depth x speed 0.45 m2/s (small cars unstable from 0.3); runoff beside / along the road at 0.8 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.37); road sag 3.2 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 24 mm; catchment 60.2 ha) (P 1.00); a culvert within 100 m is overtopped |
| 4 | 1.00 | Martin Luther King Jr Boulevard | Worcester | 3.63 m of water at peak; over 30 cm for 17.5 h; 30 cm reached 1.0 h into the storm; worst hour 24 mm (43% of the storm); water beside the road 3.31 m above its crest (design freeboard 0.30 m; P 1.00); fast water: depth x speed 0.22 m2/s (small cars unstable from 0.3); runoff beside / along the road at 2.8 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.98); road sag 3.2 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 24 mm; catchment 60.2 ha) (P 1.00); a culvert within 100 m is overtopped |
| 5 | 1.00 | Route 70 | Worcester | 0.72 m of water at peak; over 30 cm for 10.5 h; 30 cm reached 6.0 h into the storm; worst hour 25 mm (44% of the storm); runoff beside / along the road at 2.1 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.32); a culvert within 100 m is overtopped |
| 6 | 1.00 | Route 70 | Worcester | 0.72 m of water at peak; over 30 cm for 10.5 h; 30 cm reached 6.0 h into the storm; worst hour 25 mm (44% of the storm); runoff beside / along the road at 2.4 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.36); a culvert within 100 m is overtopped |
| 7 | 1.00 | Shrewsbury Street | Worcester | 1.04 m of water at peak; over 30 cm for 13.0 h; 30 cm reached 5.5 h into the storm; worst hour 24 mm (44% of the storm); water beside the road 0.96 m above its crest (design freeboard 0.30 m; P 1.00); fast water: depth x speed 0.27 m2/s (small cars unstable from 0.3); runoff beside / along the road at 0.6 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.13); road sag 0.8 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 23 mm; catchment 127.8 ha) (P 1.00) |
| 8 | 1.00 | Shrewsbury Street | Worcester | 1.14 m of water at peak; over 30 cm for 13.0 h; 30 cm reached 5.5 h into the storm; worst hour 24 mm (44% of the storm); water beside the road 1.06 m above its crest (design freeboard 0.30 m; P 1.00); fast water: depth x speed 0.31 m2/s (small cars unstable from 0.3); runoff beside / along the road at 0.8 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.13); road sag 0.8 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 23 mm; catchment 127.8 ha) (P 1.00) |
| 9 | 1.00 | Route 9 | Worcester | 0.70 m of water at peak; over 30 cm for 10.0 h; 30 cm reached 6.0 h into the storm; worst hour 25 mm (44% of the storm); a culvert within 100 m is overtopped |
| 10 | 1.00 | Martin Luther King Jr Boulevard | Worcester | 1.30 m of water at peak; over 30 cm for 11.5 h; 30 cm reached 7.0 h into the storm; worst hour 24 mm (43% of the storm); water beside the road 1.13 m above its crest (design freeboard 0.30 m; P 1.00); a culvert within 100 m is overtopped |
| 11 | 1.00 | Foster Street | Worcester | 2.60 m of water at peak; over 30 cm for 13.5 h; 30 cm reached 5.0 h into the storm; worst hour 25 mm (44% of the storm); water beside the road 0.61 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 1.6 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.77); road sag 1.2 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 25 mm; catchment 22.1 ha) (P 1.00); a culvert within 100 m is overtopped |
| 12 | 1.00 | Thomas Street | Worcester | 1.13 m of water at peak; over 30 cm for 11.5 h; 30 cm reached 7.0 h into the storm; worst hour 25 mm (43% of the storm); water beside the road 1.09 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.5 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 24 mm; catchment 60.2 ha) (P 1.00); a culvert within 100 m is overtopped |
| 13 | 1.00 | Major Taylor Boulevard | Worcester | 1.74 m of water at peak; over 30 cm for 13.0 h; 30 cm reached 5.5 h into the storm; worst hour 25 mm (44% of the storm); water beside the road 1.49 m above its crest (design freeboard 0.30 m; P 1.00); road sag 1.1 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 24 mm; catchment 60.2 ha) (P 1.00); a culvert within 100 m is overtopped |
| 14 | 1.00 | Major Taylor Boulevard | Worcester | 1.74 m of water at peak; over 30 cm for 13.0 h; 30 cm reached 5.5 h into the storm; worst hour 25 mm (44% of the storm); water beside the road 1.49 m above its crest (design freeboard 0.30 m; P 1.00); road sag 1.1 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 24 mm; catchment 60.2 ha) (P 1.00); a culvert within 100 m is overtopped |
| 15 | 1.00 | Foster Street | Worcester | 2.60 m of water at peak; over 30 cm for 13.5 h; 30 cm reached 5.0 h into the storm; worst hour 25 mm (44% of the storm); water beside the road 0.63 m above its crest (design freeboard 0.30 m; P 1.00); road sag 1.2 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 25 mm; catchment 22.1 ha) (P 1.00); a culvert within 100 m is overtopped |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
