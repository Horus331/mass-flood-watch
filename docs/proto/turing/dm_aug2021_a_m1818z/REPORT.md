# Road-closure prototype: aug2021_proto_dm_aug2021_a_m1818z

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on GPU (cuda)), 20 m grid, storm from 2021-08-18T18:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 45,099 |
| Expected closures (sum of probabilities) | 559.3 |
| Segments with closure probability >= 50% | 297 (194.9 km) |
| Further segments that may close (stream reaches the road crest) | 517 (292.5 km) |
| Culverts overtopped / surcharged | 927 / 8 of 10736 |
| Road segments cut off from hospitals | 3716 |
| Worst added trip time to a hospital | 48.9 min |
| Heaviest hour of rain | 34.4 mm |
| Flood model run time | 422 s |

## Checks against what happened

- Storm-day flood reports in the area: 10; water >= 10 cm within 100 m of 50% of them, vs 48% of random points (any day).
- Segments flagged impassable are 4.91x as likely as an average segment to have a report within 200 m.
- MassDOT repeating flood sites in the area: 30; 7 have a segment within 150 m at P >= 0.5 (share of all segments at P >= 0.5: 0.7%).

## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 1.00 | (unnamed) | Worcester | 0.87 m of water at peak; over 30 cm for 9.5 h; 30 cm reached 24.0 h into the storm; worst hour 31 mm (32% of the storm); water beside the road 0.75 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.7 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 30 mm; catchment 77.2 ha) (P 1.00) |
| 2 | 1.00 | (unnamed) | Framingham | 1.73 m of water at peak; over 30 cm for 10.5 h; 30 cm reached 23.0 h into the storm; worst hour 34 mm (47% of the storm); water beside the road 1.47 m above its crest (design freeboard 0.30 m; P 1.00); road sag 2.9 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 34 mm; catchment 15.3 ha) (P 1.00) |
| 3 | 1.00 | Route 117 | Lancaster | 0.73 m of water at peak; over 30 cm for 33.0 h; 30 cm reached 0.5 h into the storm; worst hour 29 mm (36% of the storm); culvert (Trib to Still River): headwater 3.20 m vs road crest 2.74 m, 17.9 m3/s |
| 4 | 1.00 | Shrewsbury Street | Worcester | 0.93 m of water at peak; over 30 cm for 10.5 h; 30 cm reached 23.0 h into the storm; worst hour 31 mm (34% of the storm); water beside the road 0.85 m above its crest (design freeboard 0.30 m; P 1.00); fast water: depth x speed 0.25 m2/s (small cars unstable from 0.3); runoff beside / along the road at 0.6 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.12); road sag 0.8 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 31 mm; catchment 127.8 ha) (P 1.00) |
| 5 | 1.00 | Shrewsbury Street | Worcester | 1.03 m of water at peak; over 30 cm for 11.0 h; 30 cm reached 22.5 h into the storm; worst hour 31 mm (34% of the storm); water beside the road 0.95 m above its crest (design freeboard 0.30 m; P 1.00); fast water: depth x speed 0.29 m2/s (small cars unstable from 0.3); runoff beside / along the road at 0.6 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.12); road sag 0.8 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 31 mm; catchment 127.8 ha) (P 1.00) |
| 6 | 1.00 | Martin Luther King Jr Boulevard | Worcester | 1.14 m of water at peak; over 30 cm for 11.0 h; 30 cm reached 22.5 h into the storm; worst hour 29 mm (32% of the storm); water beside the road 1.21 m above its crest (design freeboard 0.30 m; P 1.00); road sag 3.2 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 29 mm; catchment 60.2 ha) (P 1.00); a culvert within 100 m is overtopped |
| 7 | 1.00 | Cambridge Street | Worcester | 1.50 m of water at peak; over 30 cm for 11.0 h; 30 cm reached 22.5 h into the storm; worst hour 31 mm (32% of the storm); water beside the road 1.36 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.7 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 30 mm; catchment 77.2 ha) (P 1.00) |
| 8 | 1.00 | Southbridge Street | Worcester | 1.01 m of water at peak; over 30 cm for 10.0 h; 30 cm reached 23.5 h into the storm; worst hour 31 mm (32% of the storm); water beside the road 0.95 m above its crest (design freeboard 0.30 m; P 1.00); road sag 1.2 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 30 mm; catchment 13.4 ha) (P 1.00) |
| 9 | 1.00 | Boundary Street | Marlborough | 1.05 m of water at peak; over 30 cm for 33.0 h; 30 cm reached 0.5 h into the storm; worst hour 34 mm (43% of the storm); runoff beside / along the road at 0.7 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.12); a culvert within 100 m is overtopped |
| 10 | 1.00 | Auburn Street | Auburn | 0.74 m of water at peak; over 30 cm for 10.5 h; 30 cm reached 23.0 h into the storm; worst hour 31 mm (34% of the storm); water beside the road 0.33 m above its crest (design freeboard 0.30 m; P 1.00) |
| 11 | 1.00 | Francis J. Mcgrath Boulevard | Worcester | 0.67 m of water at peak; over 30 cm for 4.5 h; 30 cm reached 22.5 h into the storm; worst hour 29 mm (31% of the storm); water beside the road 0.53 m above its crest (design freeboard 0.30 m; P 1.00); fast water: depth x speed 0.26 m2/s (small cars unstable from 0.3); runoff beside / along the road at 0.7 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.25); road sag 2.6 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 28 mm; catchment 9.4 ha) (P 1.00) |
| 12 | 1.00 | Millbury Street | Grafton | 0.87 m of water at peak; over 30 cm for 11.0 h; 30 cm reached 22.5 h into the storm; worst hour 33 mm (38% of the storm) |
| 13 | 1.00 | Village Drive | Southbridge | 0.74 m of water at peak; over 30 cm for 11.5 h; 30 cm reached 22.0 h into the storm; worst hour 29 mm (31% of the storm); a culvert within 100 m is overtopped |
| 14 | 1.00 | (unnamed) | Southbridge | 1.38 m of water at peak; over 30 cm for 11.0 h; 30 cm reached 22.5 h into the storm; worst hour 30 mm (32% of the storm); culvert (Unnamed tributary): headwater 672.35 m vs road crest 0.49 m, 3.4 m3/s |
| 15 | 1.00 | Pine Grove Avenue | Bellingham | 0.68 m of water at peak; over 30 cm for 9.0 h; 30 cm reached 24.5 h into the storm; worst hour 24 mm (35% of the storm); a culvert within 100 m is overtopped |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
