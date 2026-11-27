# Road-closure prototype: aug2026_proto_dm_aug2026_a_m0305z

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on GPU (cuda)), 20 m grid, storm from 2026-08-03T05:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 45,099 |
| Expected closures (sum of probabilities) | 683.0 |
| Segments with closure probability >= 50% | 427 (288.7 km) |
| Further segments that may close (stream reaches the road crest) | 581 (341.7 km) |
| Culverts overtopped / surcharged | 1078 / 13 of 10736 |
| Road segments cut off from hospitals | 4396 |
| Worst added trip time to a hospital | 44.8 min |
| Heaviest hour of rain | 41.4 mm |
| Flood model run time | 259 s |

## Checks against what happened

- Storm-day flood reports in the area: 3; water >= 10 cm within 100 m of 33% of them, vs 52% of random points (any day).
- Segments flagged impassable are 0.0x as likely as an average segment to have a report within 200 m.
- MassDOT repeating flood sites in the area: 30; 8 have a segment within 150 m at P >= 0.5 (share of all segments at P >= 0.5: 0.9%).

## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 1.00 | (unnamed) | Worcester | 1.09 m of water at peak; over 30 cm for 9.0 h; 30 cm reached 8.5 h into the storm; worst hour 36 mm (35% of the storm); water beside the road 0.97 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.7 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 36 mm; catchment 77.2 ha) (P 1.00) |
| 2 | 1.00 | (unnamed) | Framingham | 1.81 m of water at peak; over 30 cm for 10.0 h; 30 cm reached 7.5 h into the storm; worst hour 26 mm (28% of the storm); water beside the road 1.54 m above its crest (design freeboard 0.30 m; P 1.00); road sag 2.9 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 26 mm; catchment 15.3 ha) (P 1.00) |
| 3 | 1.00 | Route 117 | Lancaster | 1.30 m of water at peak; over 30 cm for 17.0 h; 30 cm reached 0.5 h into the storm; worst hour 28 mm (31% of the storm); culvert (Trib to Still River): headwater 4.25 m vs road crest 2.74 m, 23.5 m3/s |
| 4 | 1.00 | Shrewsbury Street | Worcester | 0.98 m of water at peak; over 30 cm for 10.0 h; 30 cm reached 7.5 h into the storm; worst hour 35 mm (34% of the storm); water beside the road 0.90 m above its crest (design freeboard 0.30 m; P 1.00); fast water: depth x speed 0.25 m2/s (small cars unstable from 0.3); runoff beside / along the road at 0.6 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.12); road sag 0.8 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 35 mm; catchment 127.8 ha) (P 1.00) |
| 5 | 1.00 | Martin Luther King Jr Boulevard | Worcester | 1.28 m of water at peak; over 30 cm for 11.0 h; 30 cm reached 6.5 h into the storm; worst hour 35 mm (35% of the storm); water beside the road 1.36 m above its crest (design freeboard 0.30 m; P 1.00); road sag 3.2 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 35 mm; catchment 60.2 ha) (P 1.00); a culvert within 100 m is overtopped |
| 6 | 1.00 | Shrewsbury Street | Worcester | 1.08 m of water at peak; over 30 cm for 10.5 h; 30 cm reached 7.0 h into the storm; worst hour 35 mm (34% of the storm); water beside the road 1.00 m above its crest (design freeboard 0.30 m; P 1.00); fast water: depth x speed 0.29 m2/s (small cars unstable from 0.3); runoff beside / along the road at 0.6 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.12); road sag 0.8 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 35 mm; catchment 127.8 ha) (P 1.00) |
| 7 | 1.00 | Southbridge Street | Worcester | 1.26 m of water at peak; over 30 cm for 9.5 h; 30 cm reached 8.0 h into the storm; worst hour 37 mm (36% of the storm); water beside the road 1.20 m above its crest (design freeboard 0.30 m; P 1.00); road sag 1.2 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 37 mm; catchment 13.4 ha) (P 1.00); a culvert within 100 m is overtopped |
| 8 | 1.00 | Cambridge Street | Worcester | 1.72 m of water at peak; over 30 cm for 10.0 h; 30 cm reached 7.5 h into the storm; worst hour 37 mm (36% of the storm); water beside the road 1.58 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.7 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 36 mm; catchment 77.2 ha) (P 1.00) |
| 9 | 1.00 | Route 131 | Southbridge | 1.00 m of water at peak; over 30 cm for 9.5 h; 30 cm reached 8.0 h into the storm; worst hour 39 mm (30% of the storm); water beside the road 0.02 m below its crest (design freeboard 0.30 m; P 0.97); a culvert within 100 m is overtopped |
| 10 | 1.00 | Gilboa Street | Douglas | 0.76 m of water at peak; over 30 cm for 13.0 h; 30 cm reached 4.5 h into the storm; worst hour 39 mm (35% of the storm); water beside the road 0.49 m below its crest (design freeboard 0.30 m; P 0.11); a culvert within 100 m is overtopped |
| 11 | 1.00 | Route 131 | Southbridge | 0.94 m of water at peak; over 30 cm for 7.0 h; 30 cm reached 8.0 h into the storm; worst hour 39 mm (29% of the storm); a culvert within 100 m is overtopped |
| 12 | 1.00 | Route 12 | Auburn | 0.68 m of water at peak; over 30 cm for 9.5 h; 30 cm reached 8.0 h into the storm; worst hour 40 mm (35% of the storm) |
| 13 | 1.00 | Francis J. Mcgrath Boulevard | Worcester | 0.72 m of water at peak; over 30 cm for 5.0 h; 30 cm reached 7.0 h into the storm; worst hour 36 mm (35% of the storm); water beside the road 0.56 m above its crest (design freeboard 0.30 m; P 1.00); fast water: depth x speed 0.29 m2/s (small cars unstable from 0.3); runoff beside / along the road at 0.8 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.32); road sag 2.6 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 36 mm; catchment 9.4 ha) (P 1.00) |
| 14 | 1.00 | Auburn Street | Auburn | 0.88 m of water at peak; over 30 cm for 10.0 h; 30 cm reached 7.5 h into the storm; worst hour 40 mm (35% of the storm); water beside the road 0.34 m above its crest (design freeboard 0.30 m; P 1.00) |
| 15 | 1.00 | Quinsigamond Avenue | Worcester | 0.70 m of water at peak; over 30 cm for 8.5 h; 30 cm reached 9.0 h into the storm; worst hour 36 mm (35% of the storm) |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
