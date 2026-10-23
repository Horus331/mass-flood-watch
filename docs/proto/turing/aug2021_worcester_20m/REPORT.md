# Road-closure prototype: aug2021_proto_aug2021_worcester_20m

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on GPU (cuda)), 20 m grid, storm from 2021-08-19T09:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 8,353 |
| Expected closures (sum of probabilities) | 240.5 |
| Segments with closure probability >= 50% | 187 (114.6 km) |
| Further segments that may close (stream reaches the road crest) | 248 (125.2 km) |
| Culverts overtopped / surcharged | 297 / 3 of 1347 |
| Road segments cut off from hospitals | 1194 |
| Worst added trip time to a hospital | 28.0 min |
| Heaviest hour of rain | 89.6 mm |
| Flood model run time | 49 s |

## Checks against what happened

- Storm-day flood reports in the area: 5; water >= 10 cm within 100 m of 60% of them, vs 64% of random points (any day).
- Segments flagged impassable are 1.86x as likely as an average segment to have a report within 200 m.
- MassDOT repeating flood sites in the area: 10; 4 have a segment within 150 m at P >= 0.5 (share of all segments at P >= 0.5: 2.2%).

## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 1.00 | Martin Luther King Jr Boulevard | Worcester | 3.88 m of water at peak; over 30 cm for 18.0 h; 30 cm reached 0.5 h into the storm; worst hour 24 mm (43% of the storm); water beside the road 3.80 m above its crest (design freeboard 0.30 m; P 1.00); fast water: depth x speed 0.32 m2/s (small cars unstable from 0.3); road sag 3.2 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 24 mm; catchment 60.2 ha) (P 1.00); a culvert within 100 m is overtopped |
| 2 | 1.00 | Martin Luther King Jr Boulevard | Worcester | 3.18 m of water at peak; over 30 cm for 18.0 h; 30 cm reached 0.5 h into the storm; worst hour 24 mm (43% of the storm); water beside the road 2.86 m above its crest (design freeboard 0.30 m; P 1.00); fast water: depth x speed 0.20 m2/s (small cars unstable from 0.3); road sag 3.2 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 24 mm; catchment 60.2 ha) (P 1.00); a culvert within 100 m is overtopped |
| 3 | 1.00 | Foster Street | Worcester | 2.15 m of water at peak; over 30 cm for 18.0 h; 30 cm reached 0.5 h into the storm; worst hour 25 mm (44% of the storm); water beside the road 0.17 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 1.2 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.10); road sag 0.7 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 25 mm; catchment 22.1 ha) (P 0.80); a culvert within 100 m is overtopped |
| 4 | 1.00 | Shrewsbury Street | Worcester | 0.73 m of water at peak; over 30 cm for 12.5 h; 30 cm reached 6.0 h into the storm; worst hour 24 mm (44% of the storm); water beside the road 0.64 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.9 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 23 mm; catchment 127.8 ha) (P 1.00) |
| 5 | 1.00 | Foster Street | Worcester | 2.15 m of water at peak; over 30 cm for 18.0 h; 30 cm reached 0.5 h into the storm; worst hour 25 mm (44% of the storm); water beside the road 0.42 m above its crest (design freeboard 0.30 m; P 1.00); fast water: depth x speed 0.24 m2/s (small cars unstable from 0.3); runoff beside / along the road at 2.4 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.79); road sag 0.7 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 25 mm; catchment 22.1 ha) (P 0.80); a culvert within 100 m is overtopped |
| 6 | 1.00 | Major Taylor Boulevard | Worcester | 1.20 m of water at peak; over 30 cm for 12.0 h; 30 cm reached 6.5 h into the storm; worst hour 25 mm (44% of the storm); water beside the road 1.04 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 5.0 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 1.00); road sag 1.2 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 24 mm; catchment 60.2 ha) (P 1.00); a culvert within 100 m is overtopped |
| 7 | 1.00 | Martin Luther King Jr Boulevard | Worcester | 0.85 m of water at peak; over 30 cm for 10.0 h; 30 cm reached 8.5 h into the storm; worst hour 24 mm (43% of the storm); water beside the road 0.68 m above its crest (design freeboard 0.30 m; P 1.00); a culvert within 100 m is overtopped |
| 8 | 1.00 | Major Taylor Boulevard | Worcester | 1.29 m of water at peak; over 30 cm for 12.0 h; 30 cm reached 6.5 h into the storm; worst hour 25 mm (44% of the storm); water beside the road 1.04 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 5.0 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 1.00); road sag 1.2 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 24 mm; catchment 60.2 ha) (P 1.00); a culvert within 100 m is overtopped |
| 9 | 1.00 | Thomas Street | Worcester | 0.68 m of water at peak; over 30 cm for 9.5 h; 30 cm reached 9.0 h into the storm; worst hour 25 mm (43% of the storm); water beside the road 0.64 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.5 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 24 mm; catchment 60.2 ha) (P 1.00); a culvert within 100 m is overtopped |
| 10 | 1.00 | Cambridge Street | Worcester | 0.85 m of water at peak; over 30 cm for 12.0 h; 30 cm reached 6.5 h into the storm; worst hour 29 mm (48% of the storm); water beside the road 0.71 m above its crest (design freeboard 0.30 m; P 1.00); road sag 2.0 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 28 mm; catchment 77.2 ha) (P 1.00); a culvert within 100 m is overtopped |
| 11 | 1.00 | Providence Street | Millbury | 2.15 m of water at peak; over 30 cm for 18.0 h; 30 cm reached 0.5 h into the storm; worst hour 49 mm (54% of the storm); a culvert within 100 m is overtopped |
| 12 | 1.00 | Route 122 | Northbridge | 2.39 m of water at peak; over 30 cm for 18.0 h; 30 cm reached 0.5 h into the storm; worst hour 70 mm (68% of the storm); a culvert within 100 m is overtopped |
| 13 | 1.00 | Stafford Street | Worcester | 1.23 m of water at peak; over 30 cm for 9.5 h; 30 cm reached 0.5 h into the storm; worst hour 34 mm (53% of the storm); water beside the road 0.60 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.4 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 33 mm; catchment 16.0 ha) (P 0.20); a culvert within 100 m is overtopped |
| 14 | 1.00 | Route 20 | Worcester | 0.68 m of water at peak; over 30 cm for 6.5 h; 30 cm reached 6.5 h into the storm; worst hour 35 mm (44% of the storm); water beside the road 1.15 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 0.6 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.11); road sag 1.0 m deep (underpass, drains sized for the 50-yr hour, 58 mm; peak hour here 34 mm; catchment 12.1 ha) (P 1.00) |
| 15 | 1.00 | Route 12 | Auburn | 0.71 m of water at peak; over 30 cm for 10.5 h; 30 cm reached 8.0 h into the storm; worst hour 34 mm (48% of the storm) |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
