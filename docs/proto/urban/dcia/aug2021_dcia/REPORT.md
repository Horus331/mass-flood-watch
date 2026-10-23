# Road-closure prototype: aug2021_loss_aug2021_dcia

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on CPU (OpenMP)), 20 m grid, storm from 2021-08-19T09:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 8,354 |
| Expected closures (sum of probabilities) | 238.3 |
| Segments with closure probability >= 50% | 178 (107.7 km) |
| Further segments that may close (stream reaches the road crest) | 260 (126.9 km) |
| Culverts overtopped / surcharged | 279 / 4 of 1347 |
| Road segments cut off from hospitals | 1175 |
| Worst added trip time to a hospital | 34.0 min |
| Heaviest hour of rain | 89.6 mm |
| Flood model run time | 654 s |

## Checks against what happened

- Storm-day flood reports in the area: 5; water >= 10 cm within 100 m of 60% of them, vs 62% of random points (any day).
- Segments flagged impassable are 2.62x as likely as an average segment to have a report within 200 m.
- MassDOT repeating flood sites in the area: 10; 4 have a segment within 150 m at P >= 0.5 (share of all segments at P >= 0.5: 2.1%).

## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 1.00 | Martin Luther King Jr Boulevard | Worcester | 3.92 m of water at peak; over 30 cm for 17.5 h; 30 cm reached 1.0 h into the storm; worst hour 24 mm (43% of the storm); water beside the road 3.84 m above its crest (design freeboard 0.30 m; P 1.00); fast water: depth x speed 0.35 m2/s (small cars unstable from 0.3); runoff beside / along the road at 2.3 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.97); road sag 3.2 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 24 mm; catchment 60.2 ha) (P 1.00); a culvert within 100 m is overtopped |
| 2 | 1.00 | Martin Luther King Jr Boulevard | Worcester | 3.22 m of water at peak; over 30 cm for 17.5 h; 30 cm reached 1.0 h into the storm; worst hour 24 mm (43% of the storm); water beside the road 2.89 m above its crest (design freeboard 0.30 m; P 1.00); fast water: depth x speed 0.30 m2/s (small cars unstable from 0.3); runoff beside / along the road at 4.5 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.98); road sag 3.2 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 24 mm; catchment 60.2 ha) (P 1.00); a culvert within 100 m is overtopped |
| 3 | 1.00 | Shrewsbury Street | Worcester | 0.71 m of water at peak; over 30 cm for 12.5 h; 30 cm reached 6.0 h into the storm; worst hour 24 mm (44% of the storm); water beside the road 0.63 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.9 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 23 mm; catchment 127.8 ha) (P 1.00) |
| 4 | 1.00 | Shrewsbury Street | Worcester | 0.81 m of water at peak; over 30 cm for 13.0 h; 30 cm reached 5.5 h into the storm; worst hour 24 mm (44% of the storm); water beside the road 0.73 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 1.0 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.19); road sag 0.9 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 23 mm; catchment 127.8 ha) (P 1.00) |
| 5 | 1.00 | Foster Street | Worcester | 2.19 m of water at peak; over 30 cm for 13.0 h; 30 cm reached 5.5 h into the storm; worst hour 25 mm (44% of the storm); water beside the road 0.20 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 3.2 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.40); road sag 1.2 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 25 mm; catchment 22.1 ha) (P 0.86); a culvert within 100 m is overtopped |
| 6 | 1.00 | Martin Luther King Jr Boulevard | Worcester | 0.89 m of water at peak; over 30 cm for 10.5 h; 30 cm reached 8.0 h into the storm; worst hour 24 mm (43% of the storm); water beside the road 0.72 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 0.9 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.11); a culvert within 100 m is overtopped |
| 7 | 1.00 | Major Taylor Boulevard | Worcester | 1.33 m of water at peak; over 30 cm for 12.5 h; 30 cm reached 6.0 h into the storm; worst hour 25 mm (44% of the storm); water beside the road 1.08 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 1.6 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.54); road sag 1.1 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 24 mm; catchment 60.2 ha) (P 1.00); a culvert within 100 m is overtopped |
| 8 | 1.00 | Major Taylor Boulevard | Worcester | 1.33 m of water at peak; over 30 cm for 12.5 h; 30 cm reached 6.0 h into the storm; worst hour 25 mm (44% of the storm); water beside the road 1.08 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 1.1 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.54); road sag 1.1 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 24 mm; catchment 60.2 ha) (P 1.00); a culvert within 100 m is overtopped |
| 9 | 1.00 | Thomas Street | Worcester | 0.71 m of water at peak; over 30 cm for 10.0 h; 30 cm reached 8.5 h into the storm; worst hour 25 mm (43% of the storm); water beside the road 0.68 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.5 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 24 mm; catchment 60.2 ha) (P 1.00); a culvert within 100 m is overtopped |
| 10 | 1.00 | Foster Street | Worcester | 2.19 m of water at peak; over 30 cm for 13.0 h; 30 cm reached 5.5 h into the storm; worst hour 25 mm (44% of the storm); water beside the road 0.21 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 2.1 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.19); road sag 1.2 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 25 mm; catchment 22.1 ha) (P 0.86); a culvert within 100 m is overtopped |
| 11 | 1.00 | Cambridge Street | Worcester | 0.72 m of water at peak; over 30 cm for 11.5 h; 30 cm reached 7.0 h into the storm; worst hour 29 mm (48% of the storm); water beside the road 0.58 m above its crest (design freeboard 0.30 m; P 1.00); road sag 2.0 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 28 mm; catchment 77.2 ha) (P 1.00) |
| 12 | 1.00 | Route 122 | Northbridge | 2.08 m of water at peak; over 30 cm for 18.0 h; 30 cm reached 0.5 h into the storm; worst hour 70 mm (68% of the storm); a culvert within 100 m is overtopped |
| 13 | 1.00 | Route 20 | Worcester | 0.73 m of water at peak; over 30 cm for 6.0 h; 30 cm reached 6.0 h into the storm; worst hour 35 mm (44% of the storm); water beside the road 1.16 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 5.0 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.95); road sag 1.0 m deep (underpass, drains sized for the 50-yr hour, 58 mm; peak hour here 34 mm; catchment 12.1 ha) (P 1.00) |
| 14 | 1.00 | Providence Street | Millbury | 1.38 m of water at peak; over 30 cm for 14.0 h; 30 cm reached 4.5 h into the storm; worst hour 49 mm (54% of the storm); runoff beside / along the road at 0.6 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.22); a culvert within 100 m is overtopped |
| 15 | 1.00 | Route 12 | Auburn | 0.64 m of water at peak; over 30 cm for 10.0 h; 30 cm reached 8.5 h into the storm; worst hour 34 mm (48% of the storm) |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
