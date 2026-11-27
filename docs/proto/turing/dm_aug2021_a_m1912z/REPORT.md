# Road-closure prototype: aug2021_proto_dm_aug2021_a_m1912z

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on GPU (cuda)), 20 m grid, storm from 2021-08-19T12:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 45,099 |
| Expected closures (sum of probabilities) | 770.8 |
| Segments with closure probability >= 50% | 499 (357.0 km) |
| Further segments that may close (stream reaches the road crest) | 759 (484.5 km) |
| Culverts overtopped / surcharged | 1129 / 16 of 10736 |
| Road segments cut off from hospitals | 4859 |
| Worst added trip time to a hospital | 67.7 min |
| Heaviest hour of rain | 51.0 mm |
| Flood model run time | 236 s |

## Checks against what happened

- Storm-day flood reports in the area: 10; water >= 10 cm within 100 m of 60% of them, vs 52% of random points (any day).
- Segments flagged impassable are 3.57x as likely as an average segment to have a report within 200 m.
- MassDOT repeating flood sites in the area: 30; 9 have a segment within 150 m at P >= 0.5 (share of all segments at P >= 0.5: 1.1%).

## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 1.00 | (unnamed) | Worcester | 0.94 m of water at peak; over 30 cm for 10.0 h; 30 cm reached 5.5 h into the storm; worst hour 28 mm (31% of the storm); water beside the road 0.83 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.7 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 28 mm; catchment 77.2 ha) (P 1.00) |
| 2 | 1.00 | (unnamed) | Framingham | 1.76 m of water at peak; over 30 cm for 11.0 h; 30 cm reached 4.5 h into the storm; worst hour 35 mm (46% of the storm); water beside the road 1.49 m above its crest (design freeboard 0.30 m; P 1.00); road sag 2.9 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 35 mm; catchment 15.3 ha) (P 1.00) |
| 3 | 1.00 | Shrewsbury Street | Worcester | 0.90 m of water at peak; over 30 cm for 11.0 h; 30 cm reached 4.5 h into the storm; worst hour 30 mm (32% of the storm); water beside the road 0.82 m above its crest (design freeboard 0.30 m; P 1.00); fast water: depth x speed 0.20 m2/s (small cars unstable from 0.3); road sag 0.8 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 30 mm; catchment 127.8 ha) (P 1.00) |
| 4 | 1.00 | Martin Luther King Jr Boulevard | Worcester | 1.21 m of water at peak; over 30 cm for 12.0 h; 30 cm reached 3.5 h into the storm; worst hour 30 mm (32% of the storm); water beside the road 1.28 m above its crest (design freeboard 0.30 m; P 1.00); road sag 3.2 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 30 mm; catchment 60.2 ha) (P 1.00); a culvert within 100 m is overtopped |
| 5 | 1.00 | Shrewsbury Street | Worcester | 1.00 m of water at peak; over 30 cm for 11.5 h; 30 cm reached 4.0 h into the storm; worst hour 30 mm (32% of the storm); water beside the road 0.92 m above its crest (design freeboard 0.30 m; P 1.00); fast water: depth x speed 0.24 m2/s (small cars unstable from 0.3); road sag 0.8 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 30 mm; catchment 127.8 ha) (P 1.00) |
| 6 | 1.00 | Route 117 | Lancaster | 2.07 m of water at peak; over 30 cm for 15.0 h; 30 cm reached 0.5 h into the storm; worst hour 34 mm (30% of the storm); water beside the road 0.33 m below its crest (design freeboard 0.30 m; P 0.42); culvert (Trib to Still River): headwater 25.02 m vs road crest 2.74 m, 71.6 m3/s |
| 7 | 1.00 | (unnamed) | Leominster | 1.00 m of water at peak; over 30 cm for 11.0 h; 30 cm reached 4.5 h into the storm; worst hour 33 mm (26% of the storm); water beside the road 0.18 m below its crest (design freeboard 0.30 m; P 0.79); a culvert within 100 m is overtopped |
| 8 | 1.00 | Southbridge Street | Worcester | 1.08 m of water at peak; over 30 cm for 10.5 h; 30 cm reached 5.0 h into the storm; worst hour 28 mm (31% of the storm); water beside the road 1.02 m above its crest (design freeboard 0.30 m; P 1.00); road sag 1.2 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 28 mm; catchment 13.4 ha) (P 1.00) |
| 9 | 1.00 | Cambridge Street | Worcester | 1.57 m of water at peak; over 30 cm for 11.0 h; 30 cm reached 4.5 h into the storm; worst hour 28 mm (30% of the storm); water beside the road 1.43 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.7 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 28 mm; catchment 77.2 ha) (P 1.00) |
| 10 | 1.00 | John Fitch Highway | Fitchburg | 0.64 m of water at peak; over 30 cm for 11.5 h; 30 cm reached 4.0 h into the storm; worst hour 32 mm (28% of the storm); runoff beside / along the road at 0.6 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.18); a culvert within 100 m is overtopped |
| 11 | 1.00 | John Fitch Highway | Fitchburg | 0.81 m of water at peak; over 30 cm for 11.0 h; 30 cm reached 4.5 h into the storm; worst hour 32 mm (28% of the storm); water beside the road 0.48 m below its crest (design freeboard 0.30 m; P 0.11) |
| 12 | 1.00 | Route 12 | Leominster | 0.63 m of water at peak; over 30 cm for 7.5 h; 30 cm reached 5.0 h into the storm; worst hour 33 mm (26% of the storm); a culvert within 100 m is overtopped |
| 13 | 1.00 | Depot Street | Fitchburg | 1.79 m of water at peak; over 30 cm for 14.5 h; 30 cm reached 0.5 h into the storm; worst hour 32 mm (27% of the storm); runoff beside / along the road at 0.7 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.19); a culvert within 100 m is overtopped |
| 14 | 1.00 | Route 12 | West Boylston | 1.02 m of water at peak; over 30 cm for 9.0 h; 30 cm reached 6.5 h into the storm; worst hour 34 mm (30% of the storm); water beside the road 1.06 m above its crest (design freeboard 0.30 m; P 1.00); fast water: depth x speed 0.58 m2/s (small cars unstable from 0.3); runoff beside / along the road at 0.6 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.12) |
| 15 | 1.00 | Francis J. Mcgrath Boulevard | Worcester | 0.65 m of water at peak; over 30 cm for 4.5 h; 30 cm reached 4.0 h into the storm; worst hour 29 mm (31% of the storm); water beside the road 0.52 m above its crest (design freeboard 0.30 m; P 1.00); fast water: depth x speed 0.24 m2/s (small cars unstable from 0.3); runoff beside / along the road at 0.7 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.22); road sag 2.6 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 29 mm; catchment 9.4 ha) (P 1.00) |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
