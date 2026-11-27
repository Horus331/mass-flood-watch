# Road-closure prototype: sep2023_proto_dm_sep2023_a_m1117z

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on GPU (cuda)), 20 m grid, storm from 2023-09-11T17:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 45,099 |
| Expected closures (sum of probabilities) | 997.0 |
| Segments with closure probability >= 50% | 695 (490.9 km) |
| Further segments that may close (stream reaches the road crest) | 838 (501.5 km) |
| Culverts overtopped / surcharged | 1423 / 32 of 10736 |
| Road segments cut off from hospitals | 6167 |
| Worst added trip time to a hospital | 54.3 min |
| Heaviest hour of rain | 49.5 mm |
| Flood model run time | 544 s |

## Checks against what happened

- Storm-day flood reports in the area: 11; water >= 10 cm within 100 m of 46% of them, vs 56% of random points (any day).
- Segments flagged impassable are 2.2x as likely as an average segment to have a report within 200 m.
- MassDOT repeating flood sites in the area: 30; 12 have a segment within 150 m at P >= 0.5 (share of all segments at P >= 0.5: 1.5%).

## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 1.00 | (unnamed) | Framingham | 1.78 m of water at peak; over 30 cm for 29.5 h; 30 cm reached 6.0 h into the storm; worst hour 34 mm (41% of the storm); water beside the road 1.52 m above its crest (design freeboard 0.30 m; P 1.00); road sag 2.9 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 32 mm; catchment 15.3 ha) (P 1.00) |
| 2 | 1.00 | (unnamed) | Worcester | 1.25 m of water at peak; over 30 cm for 17.5 h; 30 cm reached 6.0 h into the storm; worst hour 48 mm (46% of the storm); water beside the road 1.14 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.7 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 48 mm; catchment 77.2 ha) (P 1.00) |
| 3 | 1.00 | Route 70 | Worcester | 0.68 m of water at peak; over 30 cm for 29.5 h; 30 cm reached 6.0 h into the storm; worst hour 49 mm (47% of the storm); a culvert within 100 m is overtopped |
| 4 | 1.00 | Route 70 | Worcester | 0.68 m of water at peak; over 30 cm for 29.0 h; 30 cm reached 6.0 h into the storm; worst hour 49 mm (47% of the storm); a culvert within 100 m is overtopped |
| 5 | 1.00 | Shrewsbury Street | Worcester | 1.11 m of water at peak; over 30 cm for 30.0 h; 30 cm reached 5.5 h into the storm; worst hour 48 mm (46% of the storm); water beside the road 1.02 m above its crest (design freeboard 0.30 m; P 1.00); fast water: depth x speed 0.30 m2/s (small cars unstable from 0.3); runoff beside / along the road at 0.6 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.16); road sag 0.8 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 48 mm; catchment 127.8 ha) (P 1.00) |
| 6 | 1.00 | Shrewsbury Street | Worcester | 1.21 m of water at peak; over 30 cm for 30.0 h; 30 cm reached 5.5 h into the storm; worst hour 48 mm (46% of the storm); water beside the road 1.13 m above its crest (design freeboard 0.30 m; P 1.00); fast water: depth x speed 0.34 m2/s (small cars unstable from 0.3); runoff beside / along the road at 0.6 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.15); road sag 0.8 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 48 mm; catchment 127.8 ha) (P 1.00) |
| 7 | 1.00 | Martin Luther King Jr Boulevard | Worcester | 1.49 m of water at peak; over 30 cm for 30.5 h; 30 cm reached 5.0 h into the storm; worst hour 49 mm (47% of the storm); water beside the road 1.56 m above its crest (design freeboard 0.30 m; P 1.00); road sag 3.2 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 49 mm; catchment 60.2 ha) (P 1.00); a culvert within 100 m is overtopped |
| 8 | 1.00 | Martin Luther King Jr Boulevard | Worcester | 0.73 m of water at peak; over 30 cm for 30.5 h; 30 cm reached 5.0 h into the storm; worst hour 49 mm (47% of the storm); water beside the road 0.45 m above its crest (design freeboard 0.30 m; P 1.00); road sag 3.2 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 49 mm; catchment 60.2 ha) (P 1.00); a culvert within 100 m is overtopped |
| 9 | 1.00 | Route 117 | Lancaster | 1.66 m of water at peak; over 30 cm for 35.0 h; 30 cm reached 0.5 h into the storm; worst hour 44 mm (47% of the storm); culvert (Trib to Still River): headwater 9.86 m vs road crest 2.74 m, 42.3 m3/s |
| 10 | 1.00 | Route 20 | Northborough | 0.67 m of water at peak; over 30 cm for 29.0 h; 30 cm reached 6.5 h into the storm; worst hour 45 mm (43% of the storm); a culvert within 100 m is overtopped |
| 11 | 1.00 | Cambridge Street | Worcester | 1.89 m of water at peak; over 30 cm for 30.0 h; 30 cm reached 5.5 h into the storm; worst hour 48 mm (46% of the storm); water beside the road 1.74 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 0.6 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.12); road sag 0.7 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 48 mm; catchment 77.2 ha) (P 1.00); a culvert within 100 m is overtopped |
| 12 | 1.00 | Southbridge Street | Worcester | 1.41 m of water at peak; over 30 cm for 23.5 h; 30 cm reached 6.5 h into the storm; worst hour 49 mm (46% of the storm); water beside the road 1.35 m above its crest (design freeboard 0.30 m; P 1.00); road sag 1.2 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 48 mm; catchment 13.4 ha) (P 1.00); a culvert within 100 m is overtopped |
| 13 | 1.00 | Concord Street | Worcester | 0.70 m of water at peak; over 30 cm for 29.5 h; 30 cm reached 6.0 h into the storm; worst hour 49 mm (47% of the storm); water beside the road 0.43 m below its crest (design freeboard 0.30 m; P 0.20); a culvert within 100 m is overtopped |
| 14 | 1.00 | Gilboa Street | Douglas | 0.90 m of water at peak; over 30 cm for 31.0 h; 30 cm reached 4.5 h into the storm; worst hour 35 mm (33% of the storm); water beside the road 0.49 m below its crest (design freeboard 0.30 m; P 0.11); a culvert within 100 m is overtopped |
| 15 | 1.00 | Stafford Street | Worcester | 0.65 m of water at peak; over 30 cm for 19.5 h; 30 cm reached 5.0 h into the storm; worst hour 47 mm (45% of the storm); water beside the road 0.66 m above its crest (design freeboard 0.30 m; P 1.00); fast water: depth x speed 0.20 m2/s (small cars unstable from 0.3); runoff beside / along the road at 0.6 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.18); a culvert within 100 m is overtopped |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
