# Road-closure prototype: sep2023_proto_dm_sep2023_a_m1106z

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on GPU (cuda)), 20 m grid, storm from 2023-09-11T06:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 45,099 |
| Expected closures (sum of probabilities) | 743.1 |
| Segments with closure probability >= 50% | 495 (327.7 km) |
| Further segments that may close (stream reaches the road crest) | 618 (351.6 km) |
| Culverts overtopped / surcharged | 1017 / 16 of 10736 |
| Road segments cut off from hospitals | 4415 |
| Worst added trip time to a hospital | 48.7 min |
| Heaviest hour of rain | 43.3 mm |
| Flood model run time | 614 s |

## Checks against what happened

- Storm-day flood reports in the area: 11; water >= 10 cm within 100 m of 18% of them, vs 48% of random points (any day).
- Segments flagged impassable are 0.59x as likely as an average segment to have a report within 200 m.
- MassDOT repeating flood sites in the area: 30; 7 have a segment within 150 m at P >= 0.5 (share of all segments at P >= 0.5: 1.1%).

## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 1.00 | (unnamed) | Framingham | 1.70 m of water at peak; over 30 cm for 27.5 h; 30 cm reached 19.0 h into the storm; worst hour 21 mm (22% of the storm); water beside the road 1.44 m above its crest (design freeboard 0.30 m; P 1.00); road sag 2.9 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 20 mm; catchment 15.3 ha) (P 1.00) |
| 2 | 1.00 | (unnamed) | Worcester | 1.38 m of water at peak; over 30 cm for 16.5 h; 30 cm reached 18.0 h into the storm; worst hour 41 mm (29% of the storm); water beside the road 1.26 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.7 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 40 mm; catchment 77.2 ha) (P 1.00) |
| 3 | 1.00 | Route 117 | Lancaster | 1.24 m of water at peak; over 30 cm for 46.0 h; 30 cm reached 0.5 h into the storm; worst hour 26 mm (24% of the storm); culvert (Trib to Still River): headwater 5.46 m vs road crest 2.74 m, 28.6 m3/s |
| 4 | 1.00 | Shrewsbury Street | Worcester | 1.20 m of water at peak; over 30 cm for 29.0 h; 30 cm reached 17.5 h into the storm; worst hour 38 mm (28% of the storm); water beside the road 1.12 m above its crest (design freeboard 0.30 m; P 1.00); fast water: depth x speed 0.34 m2/s (small cars unstable from 0.3); runoff beside / along the road at 0.7 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.18); road sag 0.8 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 38 mm; catchment 127.8 ha) (P 1.00) |
| 5 | 1.00 | Route 70 | Worcester | 0.65 m of water at peak; over 30 cm for 19.5 h; 30 cm reached 17.5 h into the storm; worst hour 35 mm (27% of the storm); a culvert within 100 m is overtopped |
| 6 | 1.00 | Shrewsbury Street | Worcester | 1.30 m of water at peak; over 30 cm for 29.5 h; 30 cm reached 17.0 h into the storm; worst hour 38 mm (28% of the storm); water beside the road 1.22 m above its crest (design freeboard 0.30 m; P 1.00); fast water: depth x speed 0.39 m2/s (small cars unstable from 0.3); runoff beside / along the road at 0.7 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.18); road sag 0.8 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 38 mm; catchment 127.8 ha) (P 1.00) |
| 7 | 1.00 | Route 70 | Worcester | 0.65 m of water at peak; over 30 cm for 19.5 h; 30 cm reached 17.5 h into the storm; worst hour 35 mm (27% of the storm); a culvert within 100 m is overtopped |
| 8 | 1.00 | Martin Luther King Jr Boulevard | Worcester | 1.52 m of water at peak; over 30 cm for 29.5 h; 30 cm reached 17.0 h into the storm; worst hour 37 mm (28% of the storm); water beside the road 1.60 m above its crest (design freeboard 0.30 m; P 1.00); fast water: depth x speed 0.20 m2/s (small cars unstable from 0.3); road sag 3.2 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 36 mm; catchment 60.2 ha) (P 1.00); a culvert within 100 m is overtopped |
| 9 | 1.00 | Martin Luther King Jr Boulevard | Worcester | 0.77 m of water at peak; over 30 cm for 29.5 h; 30 cm reached 17.0 h into the storm; worst hour 37 mm (28% of the storm); water beside the road 0.47 m above its crest (design freeboard 0.30 m; P 1.00); road sag 3.2 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 36 mm; catchment 60.2 ha) (P 1.00); a culvert within 100 m is overtopped |
| 10 | 1.00 | Cambridge Street | Worcester | 2.01 m of water at peak; over 30 cm for 29.0 h; 30 cm reached 17.5 h into the storm; worst hour 41 mm (30% of the storm); water beside the road 1.86 m above its crest (design freeboard 0.30 m; P 1.00); fast water: depth x speed 0.20 m2/s (small cars unstable from 0.3); runoff beside / along the road at 0.6 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.17); road sag 0.7 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 40 mm; catchment 77.2 ha) (P 1.00); a culvert within 100 m is overtopped |
| 11 | 1.00 | Southbridge Street | Worcester | 1.56 m of water at peak; over 30 cm for 24.0 h; 30 cm reached 18.0 h into the storm; worst hour 41 mm (30% of the storm); water beside the road 1.50 m above its crest (design freeboard 0.30 m; P 1.00); road sag 1.2 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 40 mm; catchment 13.4 ha) (P 1.00); a culvert within 100 m is overtopped |
| 12 | 1.00 | Gilboa Street | Douglas | 1.08 m of water at peak; over 30 cm for 29.0 h; 30 cm reached 17.5 h into the storm; worst hour 41 mm (21% of the storm); water beside the road 0.49 m below its crest (design freeboard 0.30 m; P 0.11); a culvert within 100 m is overtopped |
| 13 | 1.00 | Stafford Street | Worcester | 0.81 m of water at peak; over 30 cm for 16.0 h; 30 cm reached 17.5 h into the storm; worst hour 43 mm (33% of the storm); water beside the road 0.69 m above its crest (design freeboard 0.30 m; P 1.00); fast water: depth x speed 0.25 m2/s (small cars unstable from 0.3); runoff beside / along the road at 0.9 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.36); a culvert within 100 m is overtopped |
| 14 | 1.00 | Concord Street | Worcester | 0.68 m of water at peak; over 30 cm for 21.0 h; 30 cm reached 17.5 h into the storm; worst hour 34 mm (27% of the storm); water beside the road 0.43 m below its crest (design freeboard 0.30 m; P 0.19); a culvert within 100 m is overtopped |
| 15 | 1.00 | Auburn Street | Auburn | 1.17 m of water at peak; over 30 cm for 23.5 h; 30 cm reached 18.0 h into the storm; worst hour 43 mm (29% of the storm); water beside the road 0.38 m above its crest (design freeboard 0.30 m; P 1.00) |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
