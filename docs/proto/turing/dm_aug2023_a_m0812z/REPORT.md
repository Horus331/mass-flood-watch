# Road-closure prototype: aug2023_proto_dm_aug2023_a_m0812z

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on GPU (cuda)), 20 m grid, storm from 2023-08-08T12:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 45,099 |
| Expected closures (sum of probabilities) | 189.3 |
| Segments with closure probability >= 50% | 53 (36.0 km) |
| Further segments that may close (stream reaches the road crest) | 257 (148.5 km) |
| Culverts overtopped / surcharged | 198 / 6 of 10736 |
| Road segments cut off from hospitals | 686 |
| Worst added trip time to a hospital | 26.2 min |
| Heaviest hour of rain | 26.4 mm |
| Flood model run time | 180 s |

## Checks against what happened

- Storm-day flood reports in the area: 6; water >= 10 cm within 100 m of 33% of them, vs 29% of random points (any day).
- Segments flagged impassable are 0.0x as likely as an average segment to have a report within 200 m.
- MassDOT repeating flood sites in the area: 30; 3 have a segment within 150 m at P >= 0.5 (share of all segments at P >= 0.5: 0.1%).

## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 1.00 | Route 117 | Lancaster | 0.97 m of water at peak; over 30 cm for 13.0 h; 30 cm reached 0.5 h into the storm; worst hour 20 mm (37% of the storm); culvert (Trib to Still River): headwater 2.89 m vs road crest 2.74 m, 16.7 m3/s |
| 2 | 1.00 | Martin Luther King Jr Boulevard | Worcester | 0.64 m of water at peak; over 30 cm for 9.5 h; 30 cm reached 4.0 h into the storm; worst hour 26 mm (41% of the storm); water beside the road 0.56 m above its crest (design freeboard 0.30 m; P 1.00); road sag 3.2 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 26 mm; catchment 60.2 ha) (P 1.00) |
| 3 | 1.00 | Shrewsbury Street | Worcester | 0.69 m of water at peak; over 30 cm for 9.0 h; 30 cm reached 4.5 h into the storm; worst hour 26 mm (41% of the storm); water beside the road 0.61 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.9 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 26 mm; catchment 127.8 ha) (P 1.00) |
| 4 | 1.00 | Cambridge Street | Worcester | 0.96 m of water at peak; over 30 cm for 8.5 h; 30 cm reached 5.0 h into the storm; worst hour 26 mm (40% of the storm); water beside the road 0.82 m above its crest (design freeboard 0.30 m; P 1.00); road sag 2.0 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 26 mm; catchment 77.2 ha) (P 1.00) |
| 5 | 1.00 | East Park Terrace | Worcester | 0.91 m of water at peak; over 30 cm for 9.5 h; 30 cm reached 4.0 h into the storm; worst hour 26 mm (41% of the storm); water beside the road 0.81 m above its crest (design freeboard 0.30 m; P 1.00); road sag 4.3 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 26 mm; catchment 127.8 ha) (P 1.00) |
| 6 | 1.00 | Coolidge Road | Worcester | 0.66 m of water at peak; over 30 cm for 8.0 h; 30 cm reached 5.5 h into the storm; worst hour 26 mm (40% of the storm); water beside the road 0.63 m above its crest (design freeboard 0.30 m; P 1.00); fast water: depth x speed 0.26 m2/s (small cars unstable from 0.3); runoff beside / along the road at 0.6 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.16); road sag 0.7 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 26 mm; catchment 17.7 ha) (P 1.00) |
| 7 | 1.00 | Kansas Street | Worcester | 0.67 m of water at peak; over 30 cm for 7.5 h; 30 cm reached 6.0 h into the storm; worst hour 26 mm (40% of the storm); water beside the road 0.45 m above its crest (design freeboard 0.30 m; P 1.00); road sag 2.0 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 26 mm; catchment 77.2 ha) (P 1.00) |
| 8 | 1.00 | Kinnicutt Road | Worcester | 0.62 m of water at peak; over 30 cm for 5.0 h; 30 cm reached 4.5 h into the storm; worst hour 26 mm (40% of the storm); water beside the road 0.80 m above its crest (design freeboard 0.30 m; P 1.00); fast water: depth x speed 0.24 m2/s (small cars unstable from 0.3) |
| 9 | 1.00 | Shrewsbury Street | Worcester | 0.58 m of water at peak; over 30 cm for 8.5 h; 30 cm reached 5.0 h into the storm; worst hour 26 mm (41% of the storm); water beside the road 0.50 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.9 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 26 mm; catchment 127.8 ha) (P 1.00) |
| 10 | 1.00 | Wellington Street | Worcester | 0.58 m of water at peak; over 30 cm for 3.5 h; 30 cm reached 4.0 h into the storm; worst hour 26 mm (40% of the storm); water beside the road 0.54 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.9 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 26 mm; catchment 15.1 ha) (P 1.00) |
| 11 | 1.00 | Murray Avenue | Worcester | 0.58 m of water at peak; over 30 cm for 3.5 h; 30 cm reached 4.0 h into the storm; worst hour 26 mm (40% of the storm); water beside the road 0.54 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.9 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 26 mm; catchment 15.1 ha) (P 1.00) |
| 12 | 1.00 | Fantasia Drive | Worcester | 0.56 m of water at peak; over 30 cm for 8.5 h; 30 cm reached 5.0 h into the storm; worst hour 26 mm (41% of the storm); water beside the road 0.49 m above its crest (design freeboard 0.30 m; P 1.00); road sag 1.3 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 26 mm; catchment 127.8 ha) (P 1.00) |
| 13 | 0.99 | (unnamed) | Oxford | 0.56 m of water at peak; over 30 cm for 3.0 h; 30 cm reached 10.5 h into the storm; worst hour 24 mm (38% of the storm); water beside the road 0.14 m below its crest (design freeboard 0.30 m; P 0.85); a culvert within 100 m is overtopped |
| 14 | 0.99 | (unnamed) | Spencer | 0.55 m of water at peak; over 30 cm for 10.0 h; 30 cm reached 3.5 h into the storm; worst hour 23 mm (34% of the storm) |
| 15 | 0.99 | (unnamed) | Southbridge | 0.53 m of water at peak; over 30 cm for 7.0 h; 30 cm reached 6.0 h into the storm; worst hour 24 mm (41% of the storm); culvert (Unnamed tributary): headwater 1.01 m vs road crest 0.49 m, 0.1 m3/s |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
