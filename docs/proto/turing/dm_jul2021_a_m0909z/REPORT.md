# Road-closure prototype: jul2021_proto_dm_jul2021_a_m0909z

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on GPU (cuda)), 20 m grid, storm from 2021-07-09T09:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 45,099 |
| Expected closures (sum of probabilities) | 907.9 |
| Segments with closure probability >= 50% | 615 (428.1 km) |
| Further segments that may close (stream reaches the road crest) | 714 (429.5 km) |
| Culverts overtopped / surcharged | 1391 / 20 of 10736 |
| Road segments cut off from hospitals | 5582 |
| Worst added trip time to a hospital | 59.3 min |
| Heaviest hour of rain | 29.6 mm |
| Flood model run time | 258 s |

## Checks against what happened

- Storm-day flood reports in the area: 9; water >= 10 cm within 100 m of 67% of them, vs 61% of random points (any day).
- Segments flagged impassable are 1.39x as likely as an average segment to have a report within 200 m.
- MassDOT repeating flood sites in the area: 30; 10 have a segment within 150 m at P >= 0.5 (share of all segments at P >= 0.5: 1.4%).

## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 1.00 | (unnamed) | Worcester | 1.35 m of water at peak; over 30 cm for 9.0 h; 30 cm reached 8.5 h into the storm; worst hour 26 mm (22% of the storm); water beside the road 1.23 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.7 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 26 mm; catchment 77.2 ha) (P 1.00) |
| 2 | 1.00 | (unnamed) | Framingham | 2.02 m of water at peak; over 30 cm for 10.5 h; 30 cm reached 7.0 h into the storm; worst hour 22 mm (20% of the storm); water beside the road 1.76 m above its crest (design freeboard 0.30 m; P 1.00); road sag 2.9 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 22 mm; catchment 15.3 ha) (P 1.00) |
| 3 | 1.00 | Route 70 | Worcester | 0.69 m of water at peak; over 30 cm for 10.0 h; 30 cm reached 7.5 h into the storm; worst hour 25 mm (22% of the storm); a culvert within 100 m is overtopped |
| 4 | 1.00 | Route 9 | Worcester | 0.64 m of water at peak; over 30 cm for 8.0 h; 30 cm reached 9.5 h into the storm; worst hour 26 mm (22% of the storm); water beside the road 0.64 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 1.4 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.21) |
| 5 | 1.00 | Route 70 | Worcester | 0.70 m of water at peak; over 30 cm for 9.5 h; 30 cm reached 8.0 h into the storm; worst hour 25 mm (22% of the storm); a culvert within 100 m is overtopped |
| 6 | 1.00 | Route 9 | Worcester | 0.64 m of water at peak; over 30 cm for 8.0 h; 30 cm reached 9.5 h into the storm; worst hour 26 mm (22% of the storm); water beside the road 0.64 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 0.6 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.16) |
| 7 | 1.00 | Route 117 | Lancaster | 1.64 m of water at peak; over 30 cm for 17.0 h; 30 cm reached 0.5 h into the storm; worst hour 21 mm (21% of the storm); culvert (Trib to Still River): headwater 8.81 m vs road crest 2.74 m, 39.5 m3/s |
| 8 | 1.00 | Shrewsbury Street | Worcester | 1.17 m of water at peak; over 30 cm for 10.5 h; 30 cm reached 7.0 h into the storm; worst hour 26 mm (22% of the storm); water beside the road 1.09 m above its crest (design freeboard 0.30 m; P 1.00); fast water: depth x speed 0.25 m2/s (small cars unstable from 0.3); runoff beside / along the road at 0.6 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.11); road sag 0.8 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 26 mm; catchment 127.8 ha) (P 1.00) |
| 9 | 1.00 | Martin Luther King Jr Boulevard | Worcester | 1.55 m of water at peak; over 30 cm for 11.5 h; 30 cm reached 6.0 h into the storm; worst hour 25 mm (22% of the storm); water beside the road 1.62 m above its crest (design freeboard 0.30 m; P 1.00); road sag 3.2 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 25 mm; catchment 60.2 ha) (P 1.00); a culvert within 100 m is overtopped |
| 10 | 1.00 | Shrewsbury Street | Worcester | 1.27 m of water at peak; over 30 cm for 11.0 h; 30 cm reached 6.5 h into the storm; worst hour 26 mm (22% of the storm); water beside the road 1.19 m above its crest (design freeboard 0.30 m; P 1.00); fast water: depth x speed 0.28 m2/s (small cars unstable from 0.3); runoff beside / along the road at 0.6 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.11); road sag 0.8 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 26 mm; catchment 127.8 ha) (P 1.00) |
| 11 | 1.00 | Martin Luther King Jr Boulevard | Worcester | 0.79 m of water at peak; over 30 cm for 11.5 h; 30 cm reached 6.0 h into the storm; worst hour 25 mm (22% of the storm); water beside the road 0.49 m above its crest (design freeboard 0.30 m; P 1.00); road sag 3.2 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 25 mm; catchment 60.2 ha) (P 1.00); a culvert within 100 m is overtopped |
| 12 | 1.00 | Cambridge Street | Worcester | 1.98 m of water at peak; over 30 cm for 10.5 h; 30 cm reached 7.0 h into the storm; worst hour 26 mm (22% of the storm); water beside the road 1.84 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.7 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 26 mm; catchment 77.2 ha) (P 1.00); a culvert within 100 m is overtopped |
| 13 | 1.00 | Southbridge Street | Worcester | 1.50 m of water at peak; over 30 cm for 9.5 h; 30 cm reached 8.0 h into the storm; worst hour 25 mm (22% of the storm); water beside the road 1.44 m above its crest (design freeboard 0.30 m; P 1.00); road sag 1.2 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 25 mm; catchment 13.4 ha) (P 1.00); a culvert within 100 m is overtopped |
| 14 | 1.00 | Route 20 | Northborough | 0.69 m of water at peak; over 30 cm for 9.0 h; 30 cm reached 8.5 h into the storm; worst hour 23 mm (20% of the storm); a culvert within 100 m is overtopped |
| 15 | 1.00 | Route 20 | Worcester | 0.67 m of water at peak; over 30 cm for 6.5 h; 30 cm reached 7.5 h into the storm; worst hour 27 mm (23% of the storm); water beside the road 1.17 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 0.9 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.48); road sag 1.0 m deep (underpass, drains sized for the 50-yr hour, 58 mm; peak hour here 27 mm; catchment 12.1 ha) (P 1.00) |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
