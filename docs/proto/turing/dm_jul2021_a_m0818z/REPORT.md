# Road-closure prototype: jul2021_proto_dm_jul2021_a_m0818z

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on GPU (cuda)), 20 m grid, storm from 2021-07-08T18:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 45,099 |
| Expected closures (sum of probabilities) | 732.3 |
| Segments with closure probability >= 50% | 464 (315.8 km) |
| Further segments that may close (stream reaches the road crest) | 642 (379.6 km) |
| Culverts overtopped / surcharged | 1155 / 13 of 10736 |
| Road segments cut off from hospitals | 4630 |
| Worst added trip time to a hospital | 62.0 min |
| Heaviest hour of rain | 27.9 mm |
| Flood model run time | 448 s |

## Checks against what happened

- Storm-day flood reports in the area: 9; water >= 10 cm within 100 m of 44% of them, vs 54% of random points (any day).
- Segments flagged impassable are 1.67x as likely as an average segment to have a report within 200 m.
- MassDOT repeating flood sites in the area: 30; 7 have a segment within 150 m at P >= 0.5 (share of all segments at P >= 0.5: 1.0%).

## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 1.00 | (unnamed) | Framingham | 1.93 m of water at peak; over 30 cm for 9.5 h; 30 cm reached 23.0 h into the storm; worst hour 24 mm (26% of the storm); water beside the road 1.66 m above its crest (design freeboard 0.30 m; P 1.00); road sag 2.9 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 24 mm; catchment 15.3 ha) (P 1.00) |
| 2 | 1.00 | (unnamed) | Worcester | 1.14 m of water at peak; over 30 cm for 8.0 h; 30 cm reached 24.5 h into the storm; worst hour 28 mm (27% of the storm); water beside the road 1.02 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.7 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 28 mm; catchment 77.2 ha) (P 1.00) |
| 3 | 1.00 | Route 117 | Lancaster | 1.31 m of water at peak; over 30 cm for 32.0 h; 30 cm reached 0.5 h into the storm; worst hour 24 mm (26% of the storm); culvert (Trib to Still River): headwater 5.11 m vs road crest 2.74 m, 27.2 m3/s |
| 4 | 1.00 | Route 70 | Worcester | 0.65 m of water at peak; over 30 cm for 9.0 h; 30 cm reached 23.5 h into the storm; worst hour 28 mm (27% of the storm); a culvert within 100 m is overtopped |
| 5 | 1.00 | Route 70 | Worcester | 0.65 m of water at peak; over 30 cm for 9.0 h; 30 cm reached 23.5 h into the storm; worst hour 28 mm (27% of the storm); a culvert within 100 m is overtopped |
| 6 | 1.00 | Shrewsbury Street | Worcester | 1.07 m of water at peak; over 30 cm for 9.5 h; 30 cm reached 23.0 h into the storm; worst hour 28 mm (27% of the storm); water beside the road 0.99 m above its crest (design freeboard 0.30 m; P 1.00); fast water: depth x speed 0.28 m2/s (small cars unstable from 0.3); runoff beside / along the road at 0.6 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.14); road sag 0.8 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 28 mm; catchment 127.8 ha) (P 1.00) |
| 7 | 1.00 | Martin Luther King Jr Boulevard | Worcester | 1.42 m of water at peak; over 30 cm for 10.0 h; 30 cm reached 22.5 h into the storm; worst hour 28 mm (27% of the storm); water beside the road 1.49 m above its crest (design freeboard 0.30 m; P 1.00); road sag 3.2 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 28 mm; catchment 60.2 ha) (P 1.00); a culvert within 100 m is overtopped |
| 8 | 1.00 | Martin Luther King Jr Boulevard | Worcester | 0.66 m of water at peak; over 30 cm for 10.0 h; 30 cm reached 22.5 h into the storm; worst hour 28 mm (27% of the storm); water beside the road 0.36 m above its crest (design freeboard 0.30 m; P 1.00); road sag 3.2 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 28 mm; catchment 60.2 ha) (P 1.00); a culvert within 100 m is overtopped |
| 9 | 1.00 | Shrewsbury Street | Worcester | 1.18 m of water at peak; over 30 cm for 9.5 h; 30 cm reached 23.0 h into the storm; worst hour 28 mm (27% of the storm); water beside the road 1.09 m above its crest (design freeboard 0.30 m; P 1.00); fast water: depth x speed 0.32 m2/s (small cars unstable from 0.3); runoff beside / along the road at 0.6 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.14); road sag 0.8 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 28 mm; catchment 127.8 ha) (P 1.00) |
| 10 | 1.00 | Cambridge Street | Worcester | 1.76 m of water at peak; over 30 cm for 9.5 h; 30 cm reached 23.0 h into the storm; worst hour 28 mm (27% of the storm); water beside the road 1.62 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.7 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 28 mm; catchment 77.2 ha) (P 1.00) |
| 11 | 1.00 | Southbridge Street | Worcester | 1.28 m of water at peak; over 30 cm for 8.5 h; 30 cm reached 24.0 h into the storm; worst hour 28 mm (27% of the storm); water beside the road 1.22 m above its crest (design freeboard 0.30 m; P 1.00); road sag 1.2 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 28 mm; catchment 13.4 ha) (P 1.00); a culvert within 100 m is overtopped |
| 12 | 1.00 | Boundary Street | Marlborough | 1.05 m of water at peak; over 30 cm for 32.0 h; 30 cm reached 0.5 h into the storm; worst hour 25 mm (24% of the storm); runoff beside / along the road at 0.6 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.12) |
| 13 | 1.00 | Route 20 | Worcester | 0.65 m of water at peak; over 30 cm for 5.0 h; 30 cm reached 23.5 h into the storm; worst hour 28 mm (27% of the storm); water beside the road 1.17 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 0.6 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.14); road sag 1.0 m deep (underpass, drains sized for the 50-yr hour, 58 mm; peak hour here 28 mm; catchment 12.1 ha) (P 1.00) |
| 14 | 1.00 | Gilboa Street | Douglas | 0.67 m of water at peak; over 30 cm for 10.0 h; 30 cm reached 22.5 h into the storm; worst hour 28 mm (28% of the storm); water beside the road 0.49 m below its crest (design freeboard 0.30 m; P 0.11); a culvert within 100 m is overtopped |
| 15 | 1.00 | Francis J. Mcgrath Boulevard | Worcester | 0.72 m of water at peak; over 30 cm for 5.0 h; 30 cm reached 23.0 h into the storm; worst hour 28 mm (27% of the storm); water beside the road 0.56 m above its crest (design freeboard 0.30 m; P 1.00); fast water: depth x speed 0.30 m2/s (small cars unstable from 0.3); runoff beside / along the road at 0.8 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.28); road sag 2.6 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 28 mm; catchment 9.4 ha) (P 1.00) |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
