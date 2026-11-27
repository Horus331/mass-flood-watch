# Road-closure prototype: sep2023_proto_dm_sep2023_a_m1118z

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on GPU (cuda)), 20 m grid, storm from 2023-09-11T18:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 45,099 |
| Expected closures (sum of probabilities) | 835.5 |
| Segments with closure probability >= 50% | 611 (427.2 km) |
| Further segments that may close (stream reaches the road crest) | 711 (435.5 km) |
| Culverts overtopped / surcharged | 957 / 22 of 10736 |
| Road segments cut off from hospitals | 4603 |
| Worst added trip time to a hospital | 56.0 min |
| Heaviest hour of rain | 48.2 mm |
| Flood model run time | 498 s |

## Checks against what happened

- Storm-day flood reports in the area: 11; water >= 10 cm within 100 m of 55% of them, vs 44% of random points (any day).
- Segments flagged impassable are 2.9x as likely as an average segment to have a report within 200 m.
- MassDOT repeating flood sites in the area: 30; 10 have a segment within 150 m at P >= 0.5 (share of all segments at P >= 0.5: 1.4%).

## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 1.00 | (unnamed) | Worcester | 1.41 m of water at peak; over 30 cm for 19.0 h; 30 cm reached 8.0 h into the storm; worst hour 22 mm (19% of the storm); water beside the road 1.30 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.7 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 22 mm; catchment 77.2 ha) (P 1.00) |
| 2 | 1.00 | (unnamed) | Framingham | 0.67 m of water at peak; over 30 cm for 21.0 h; 30 cm reached 13.5 h into the storm; worst hour 19 mm (30% of the storm); road sag 2.9 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 19 mm; catchment 15.3 ha) (P 1.00) |
| 3 | 1.00 | I-290 | Shrewsbury | 0.68 m of water at peak; over 30 cm for 26.5 h; 30 cm reached 8.0 h into the storm; worst hour 23 mm (18% of the storm); water beside the road 0.68 m above its crest (design freeboard 0.30 m; P 1.00) |
| 4 | 1.00 | Route 9 | Worcester | 0.72 m of water at peak; over 30 cm for 26.0 h; 30 cm reached 8.5 h into the storm; worst hour 22 mm (19% of the storm); water beside the road 0.72 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 1.4 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.17) |
| 5 | 1.00 | Route 9 | Worcester | 0.72 m of water at peak; over 30 cm for 26.0 h; 30 cm reached 8.5 h into the storm; worst hour 22 mm (19% of the storm); water beside the road 0.72 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 1.3 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.32) |
| 6 | 1.00 | Route 70 | Worcester | 0.77 m of water at peak; over 30 cm for 28.0 h; 30 cm reached 6.5 h into the storm; worst hour 23 mm (18% of the storm); a culvert within 100 m is overtopped |
| 7 | 1.00 | Route 70 | Worcester | 0.77 m of water at peak; over 30 cm for 28.0 h; 30 cm reached 6.5 h into the storm; worst hour 23 mm (18% of the storm); a culvert within 100 m is overtopped |
| 8 | 1.00 | Route 2 | Harvard | 1.10 m of water at peak; over 30 cm for 14.0 h; 30 cm reached 20.5 h into the storm; worst hour 18 mm (22% of the storm); a culvert within 100 m is overtopped |
| 9 | 1.00 | Route 2 | Harvard | 1.10 m of water at peak; over 30 cm for 14.0 h; 30 cm reached 20.5 h into the storm; worst hour 18 mm (22% of the storm); a culvert within 100 m is overtopped |
| 10 | 1.00 | Shrewsbury Street | Worcester | 1.19 m of water at peak; over 30 cm for 28.0 h; 30 cm reached 6.5 h into the storm; worst hour 22 mm (19% of the storm); water beside the road 1.11 m above its crest (design freeboard 0.30 m; P 1.00); fast water: depth x speed 0.26 m2/s (small cars unstable from 0.3); runoff beside / along the road at 0.6 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.12); road sag 0.8 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 22 mm; catchment 127.8 ha) (P 1.00) |
| 11 | 1.00 | Shrewsbury Street | Worcester | 1.29 m of water at peak; over 30 cm for 28.5 h; 30 cm reached 6.0 h into the storm; worst hour 22 mm (19% of the storm); water beside the road 1.21 m above its crest (design freeboard 0.30 m; P 1.00); fast water: depth x speed 0.29 m2/s (small cars unstable from 0.3); runoff beside / along the road at 0.6 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.12); road sag 0.8 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 22 mm; catchment 127.8 ha) (P 1.00) |
| 12 | 1.00 | Martin Luther King Jr Boulevard | Worcester | 1.70 m of water at peak; over 30 cm for 29.0 h; 30 cm reached 5.5 h into the storm; worst hour 23 mm (19% of the storm); water beside the road 1.77 m above its crest (design freeboard 0.30 m; P 1.00); road sag 3.2 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 22 mm; catchment 60.2 ha) (P 1.00); a culvert within 100 m is overtopped |
| 13 | 1.00 | Martin Luther King Jr Boulevard | Worcester | 0.94 m of water at peak; over 30 cm for 29.0 h; 30 cm reached 5.5 h into the storm; worst hour 22 mm (19% of the storm); water beside the road 0.64 m above its crest (design freeboard 0.30 m; P 1.00); road sag 3.2 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 22 mm; catchment 60.2 ha) (P 1.00); a culvert within 100 m is overtopped |
| 14 | 1.00 | Route 117 | Lancaster | 2.02 m of water at peak; over 30 cm for 34.0 h; 30 cm reached 0.5 h into the storm; worst hour 26 mm (22% of the storm); water beside the road 0.34 m below its crest (design freeboard 0.30 m; P 0.39); culvert (Trib to Still River): headwater 24.86 m vs road crest 2.74 m, 71.4 m3/s |
| 15 | 1.00 | (unnamed) | Leominster | 0.83 m of water at peak; over 30 cm for 26.5 h; 30 cm reached 7.5 h into the storm; worst hour 22 mm (19% of the storm); water beside the road 0.22 m below its crest (design freeboard 0.30 m; P 0.69); a culvert within 100 m is overtopped |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
