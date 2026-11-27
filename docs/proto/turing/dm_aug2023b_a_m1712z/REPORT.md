# Road-closure prototype: aug2023b_proto_dm_aug2023b_a_m1712z

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on GPU (cuda)), 20 m grid, storm from 2023-08-17T12:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 45,099 |
| Expected closures (sum of probabilities) | 256.7 |
| Segments with closure probability >= 50% | 91 (67.6 km) |
| Further segments that may close (stream reaches the road crest) | 220 (139.8 km) |
| Culverts overtopped / surcharged | 423 / 5 of 10736 |
| Road segments cut off from hospitals | 1239 |
| Worst added trip time to a hospital | 50.6 min |
| Heaviest hour of rain | 40.2 mm |
| Flood model run time | 461 s |

## Checks against what happened

- Storm-day flood reports in the area: 3; water >= 10 cm within 100 m of 33% of them, vs 32% of random points (any day).
- Segments flagged impassable are 0.0x as likely as an average segment to have a report within 200 m.
- MassDOT repeating flood sites in the area: 30; 2 have a segment within 150 m at P >= 0.5 (share of all segments at P >= 0.5: 0.2%).

## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 1.00 | (unnamed) | Framingham | 0.66 m of water at peak; over 30 cm for 6.0 h; 30 cm reached 29.5 h into the storm; worst hour 23 mm (48% of the storm); road sag 2.9 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 23 mm; catchment 15.3 ha) (P 1.00) |
| 2 | 1.00 | Cambridge Street | Worcester | 0.81 m of water at peak; over 30 cm for 7.0 h; 30 cm reached 28.5 h into the storm; worst hour 39 mm (61% of the storm); water beside the road 0.67 m above its crest (design freeboard 0.30 m; P 1.00); road sag 2.0 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 39 mm; catchment 77.2 ha) (P 1.00) |
| 3 | 1.00 | (unnamed) | Spencer | 0.77 m of water at peak; over 30 cm for 8.5 h; 30 cm reached 27.0 h into the storm; worst hour 40 mm (50% of the storm) |
| 4 | 1.00 | (unnamed) | Southbridge | 1.08 m of water at peak; over 30 cm for 7.5 h; 30 cm reached 28.0 h into the storm; worst hour 40 mm (58% of the storm); culvert (Unnamed tributary): headwater 28.19 m vs road crest 0.49 m, 0.7 m3/s |
| 5 | 1.00 | Ash Street | Clinton | 0.98 m of water at peak; over 30 cm for 8.0 h; 30 cm reached 27.5 h into the storm; worst hour 26 mm (59% of the storm); water beside the road 0.77 m above its crest (design freeboard 0.30 m; P 1.00) |
| 6 | 1.00 | East Park Terrace | Worcester | 0.80 m of water at peak; over 30 cm for 8.0 h; 30 cm reached 27.5 h into the storm; worst hour 36 mm (60% of the storm); water beside the road 0.70 m above its crest (design freeboard 0.30 m; P 1.00); road sag 4.3 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 36 mm; catchment 127.8 ha) (P 1.00) |
| 7 | 1.00 | Ash Street | Clinton | 0.65 m of water at peak; over 30 cm for 3.5 h; 30 cm reached 32.0 h into the storm; worst hour 26 mm (59% of the storm); water beside the road 0.57 m above its crest (design freeboard 0.30 m; P 1.00) |
| 8 | 1.00 | Coolidge Road | Worcester | 0.61 m of water at peak; over 30 cm for 7.0 h; 30 cm reached 28.5 h into the storm; worst hour 38 mm (59% of the storm); water beside the road 0.59 m above its crest (design freeboard 0.30 m; P 1.00); fast water: depth x speed 0.23 m2/s (small cars unstable from 0.3); runoff beside / along the road at 0.6 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.12); road sag 0.7 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 38 mm; catchment 17.7 ha) (P 1.00) |
| 9 | 1.00 | Shrewsbury Street | Worcester | 0.58 m of water at peak; over 30 cm for 7.5 h; 30 cm reached 28.0 h into the storm; worst hour 37 mm (60% of the storm); water beside the road 0.50 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.9 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 36 mm; catchment 127.8 ha) (P 1.00) |
| 10 | 0.99 | Warren Road | Sturbridge | 0.56 m of water at peak; over 30 cm for 3.0 h; 30 cm reached 28.0 h into the storm; worst hour 40 mm (49% of the storm) |
| 11 | 0.99 | Kinnicutt Road | Worcester | 0.54 m of water at peak; over 30 cm for 4.5 h; 30 cm reached 28.0 h into the storm; worst hour 37 mm (57% of the storm); water beside the road 0.78 m above its crest (design freeboard 0.30 m; P 1.00); fast water: depth x speed 0.22 m2/s (small cars unstable from 0.3) |
| 12 | 0.99 | Wellington Street | Worcester | 0.53 m of water at peak; over 30 cm for 3.5 h; 30 cm reached 27.5 h into the storm; worst hour 38 mm (60% of the storm); water beside the road 0.50 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.9 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 38 mm; catchment 15.1 ha) (P 1.00) |
| 13 | 0.99 | Murray Avenue | Worcester | 0.53 m of water at peak; over 30 cm for 3.5 h; 30 cm reached 27.5 h into the storm; worst hour 38 mm (60% of the storm); water beside the road 0.50 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.9 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 38 mm; catchment 15.1 ha) (P 1.00) |
| 14 | 0.98 | Kansas Street | Worcester | 0.52 m of water at peak; over 30 cm for 5.5 h; 30 cm reached 30.0 h into the storm; worst hour 39 mm (61% of the storm); water beside the road 0.29 m above its crest (design freeboard 0.30 m; P 1.00); road sag 2.0 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 39 mm; catchment 77.2 ha) (P 0.98) |
| 15 | 0.98 | Meadow Road | Spencer | 0.50 m of water at peak; over 30 cm for 4.5 h; 30 cm reached 28.0 h into the storm; worst hour 40 mm (50% of the storm); a culvert within 100 m is overtopped |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
