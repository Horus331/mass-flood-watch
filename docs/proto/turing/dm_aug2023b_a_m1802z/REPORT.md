# Road-closure prototype: aug2023b_proto_dm_aug2023b_a_m1802z

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on GPU (cuda)), 20 m grid, storm from 2023-08-18T02:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 45,099 |
| Expected closures (sum of probabilities) | 241.5 |
| Segments with closure probability >= 50% | 69 (45.6 km) |
| Further segments that may close (stream reaches the road crest) | 262 (161.3 km) |
| Culverts overtopped / surcharged | 354 / 4 of 10736 |
| Road segments cut off from hospitals | 1257 |
| Worst added trip time to a hospital | 44.2 min |
| Heaviest hour of rain | 36.5 mm |
| Flood model run time | 282 s |

## Checks against what happened

- Storm-day flood reports in the area: 3; water >= 10 cm within 100 m of 33% of them, vs 33% of random points (any day).
- Segments flagged impassable are 0.0x as likely as an average segment to have a report within 200 m.
- MassDOT repeating flood sites in the area: 30; 1 have a segment within 150 m at P >= 0.5 (share of all segments at P >= 0.5: 0.2%).

## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 1.00 | Cambridge Street | Worcester | 0.79 m of water at peak; over 30 cm for 6.0 h; 30 cm reached 15.5 h into the storm; worst hour 25 mm (46% of the storm); water beside the road 0.64 m above its crest (design freeboard 0.30 m; P 1.00); road sag 2.0 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 25 mm; catchment 77.2 ha) (P 1.00) |
| 2 | 1.00 | East Park Terrace | Worcester | 0.85 m of water at peak; over 30 cm for 7.5 h; 30 cm reached 14.0 h into the storm; worst hour 28 mm (49% of the storm); water beside the road 0.75 m above its crest (design freeboard 0.30 m; P 1.00); road sag 4.3 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 28 mm; catchment 127.8 ha) (P 1.00) |
| 3 | 1.00 | Route 117 | Lancaster | 0.62 m of water at peak; over 30 cm for 21.0 h; 30 cm reached 0.5 h into the storm; worst hour 35 mm (64% of the storm); culvert (Trib to Still River): headwater 3.10 m vs road crest 2.74 m, 17.5 m3/s |
| 4 | 1.00 | Shrewsbury Street | Worcester | 0.63 m of water at peak; over 30 cm for 7.0 h; 30 cm reached 14.5 h into the storm; worst hour 28 mm (50% of the storm); water beside the road 0.54 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.9 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 28 mm; catchment 127.8 ha) (P 1.00) |
| 5 | 1.00 | Coolidge Road | Worcester | 0.62 m of water at peak; over 30 cm for 6.0 h; 30 cm reached 15.5 h into the storm; worst hour 27 mm (47% of the storm); water beside the road 0.59 m above its crest (design freeboard 0.30 m; P 1.00); fast water: depth x speed 0.24 m2/s (small cars unstable from 0.3); runoff beside / along the road at 0.6 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.13); road sag 0.7 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 27 mm; catchment 17.7 ha) (P 1.00) |
| 6 | 0.99 | Martin Luther King Jr Boulevard | Worcester | 0.56 m of water at peak; over 30 cm for 7.5 h; 30 cm reached 14.0 h into the storm; worst hour 27 mm (49% of the storm); water beside the road 0.48 m above its crest (design freeboard 0.30 m; P 1.00); road sag 3.2 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 27 mm; catchment 60.2 ha) (P 1.00) |
| 7 | 0.99 | Kinnicutt Road | Worcester | 0.56 m of water at peak; over 30 cm for 5.0 h; 30 cm reached 14.5 h into the storm; worst hour 28 mm (48% of the storm); water beside the road 0.79 m above its crest (design freeboard 0.30 m; P 1.00); fast water: depth x speed 0.23 m2/s (small cars unstable from 0.3) |
| 8 | 0.99 | Shrewsbury Street | Worcester | 0.52 m of water at peak; over 30 cm for 6.0 h; 30 cm reached 15.5 h into the storm; worst hour 28 mm (50% of the storm); water beside the road 0.44 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.9 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 28 mm; catchment 127.8 ha) (P 1.00) |
| 9 | 0.98 | Fantasia Drive | Worcester | 0.50 m of water at peak; over 30 cm for 6.0 h; 30 cm reached 15.5 h into the storm; worst hour 27 mm (49% of the storm); water beside the road 0.43 m above its crest (design freeboard 0.30 m; P 1.00); road sag 1.3 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 27 mm; catchment 127.8 ha) (P 0.98) |
| 10 | 0.98 | Wellington Street | Worcester | 0.50 m of water at peak; over 30 cm for 3.0 h; 30 cm reached 14.5 h into the storm; worst hour 26 mm (47% of the storm); water beside the road 0.47 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.9 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 26 mm; catchment 15.1 ha) (P 0.99) |
| 11 | 0.98 | Murray Avenue | Worcester | 0.50 m of water at peak; over 30 cm for 3.0 h; 30 cm reached 14.0 h into the storm; worst hour 26 mm (47% of the storm); water beside the road 0.47 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.9 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 26 mm; catchment 15.1 ha) (P 0.99) |
| 12 | 0.97 | Maybrook Place | Worcester | 0.49 m of water at peak; over 30 cm for 6.0 h; 30 cm reached 15.5 h into the storm; worst hour 26 mm (46% of the storm); water beside the road 0.43 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.7 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 26 mm; catchment 61.6 ha) (P 0.99) |
| 13 | 0.97 | Kansas Street | Worcester | 0.49 m of water at peak; over 30 cm for 4.5 h; 30 cm reached 17.0 h into the storm; worst hour 25 mm (46% of the storm); water beside the road 0.27 m above its crest (design freeboard 0.30 m; P 1.00); road sag 2.0 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 25 mm; catchment 77.2 ha) (P 0.97) |
| 14 | 0.96 | (unnamed) | Spencer | 0.47 m of water at peak; over 30 cm for 7.0 h; 30 cm reached 14.5 h into the storm; worst hour 26 mm (46% of the storm) |
| 15 | 0.95 | Little Tree Lane | Framingham | 0.47 m of water at peak; over 30 cm for 2.0 h; 30 cm reached 1.0 h into the storm; worst hour 15 mm (50% of the storm); a culvert within 100 m is overtopped |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
