# Road-closure prototype: sep2023_proto_dm_sep2023_a_m1100z

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on GPU (cuda)), 20 m grid, storm from 2023-09-11T00:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 45,099 |
| Expected closures (sum of probabilities) | 942.9 |
| Segments with closure probability >= 50% | 691 (506.9 km) |
| Further segments that may close (stream reaches the road crest) | 812 (491.6 km) |
| Culverts overtopped / surcharged | 1412 / 25 of 10736 |
| Road segments cut off from hospitals | 5852 |
| Worst added trip time to a hospital | 64.9 min |
| Heaviest hour of rain | 56.4 mm |
| Flood model run time | 719 s |

## Checks against what happened

- Storm-day flood reports in the area: 11; water >= 10 cm within 100 m of 0% of them, vs 50% of random points (any day).
- Segments flagged impassable are 0.0x as likely as an average segment to have a report within 200 m.
- MassDOT repeating flood sites in the area: 30; 9 have a segment within 150 m at P >= 0.5 (share of all segments at P >= 0.5: 1.5%).

## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 1.00 | (unnamed) | Framingham | 2.06 m of water at peak; over 30 cm for 26.5 h; 30 cm reached 26.0 h into the storm; worst hour 34 mm (26% of the storm); water beside the road 1.80 m above its crest (design freeboard 0.30 m; P 1.00); road sag 2.9 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 34 mm; catchment 15.3 ha) (P 1.00) |
| 2 | 1.00 | (unnamed) | Worcester | 1.14 m of water at peak; over 30 cm for 16.0 h; 30 cm reached 27.0 h into the storm; worst hour 37 mm (34% of the storm); water beside the road 1.02 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.7 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 37 mm; catchment 77.2 ha) (P 1.00) |
| 3 | 1.00 | (unnamed) | Milford | 0.63 m of water at peak; over 30 cm for 14.5 h; 30 cm reached 26.5 h into the storm; worst hour 50 mm (26% of the storm); culvert (Charles River): headwater 10.70 m vs road crest 2.19 m, 13.4 m3/s |
| 4 | 1.00 | Shrewsbury Street | Worcester | 0.96 m of water at peak; over 30 cm for 26.5 h; 30 cm reached 26.0 h into the storm; worst hour 37 mm (35% of the storm); water beside the road 0.88 m above its crest (design freeboard 0.30 m; P 1.00); fast water: depth x speed 0.20 m2/s (small cars unstable from 0.3); road sag 0.8 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 37 mm; catchment 127.8 ha) (P 1.00) |
| 5 | 1.00 | Shrewsbury Street | Worcester | 1.07 m of water at peak; over 30 cm for 27.0 h; 30 cm reached 25.5 h into the storm; worst hour 37 mm (35% of the storm); water beside the road 0.98 m above its crest (design freeboard 0.30 m; P 1.00); fast water: depth x speed 0.24 m2/s (small cars unstable from 0.3); road sag 0.8 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 37 mm; catchment 127.8 ha) (P 1.00) |
| 6 | 1.00 | Martin Luther King Jr Boulevard | Worcester | 1.27 m of water at peak; over 30 cm for 27.5 h; 30 cm reached 25.0 h into the storm; worst hour 37 mm (35% of the storm); water beside the road 1.36 m above its crest (design freeboard 0.30 m; P 1.00); road sag 3.2 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 37 mm; catchment 60.2 ha) (P 1.00); a culvert within 100 m is overtopped |
| 7 | 1.00 | Route 146 | Uxbridge | 0.86 m of water at peak; over 30 cm for 16.0 h; 30 cm reached 25.5 h into the storm; worst hour 33 mm (17% of the storm); a culvert within 100 m is overtopped |
| 8 | 1.00 | Route 126 | Bellingham | 0.89 m of water at peak; over 30 cm for 25.5 h; 30 cm reached 27.0 h into the storm; worst hour 50 mm (22% of the storm); a culvert within 100 m is overtopped |
| 9 | 1.00 | Cambridge Street | Worcester | 1.77 m of water at peak; over 30 cm for 27.0 h; 30 cm reached 25.5 h into the storm; worst hour 37 mm (34% of the storm); water beside the road 1.63 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.7 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 37 mm; catchment 77.2 ha) (P 1.00); a culvert within 100 m is overtopped |
| 10 | 1.00 | Route 126 | Bellingham | 0.63 m of water at peak; over 30 cm for 19.0 h; 30 cm reached 26.5 h into the storm; worst hour 50 mm (21% of the storm); water beside the road 0.20 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 0.7 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.19); a culvert within 100 m is overtopped |
| 11 | 1.00 | Route 16 | Hopedale | 1.05 m of water at peak; over 30 cm for 26.5 h; 30 cm reached 26.0 h into the storm; worst hour 50 mm (24% of the storm); water beside the road 0.48 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 0.8 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.32); a culvert within 100 m is overtopped |
| 12 | 1.00 | Southbridge Street | Worcester | 1.32 m of water at peak; over 30 cm for 22.5 h; 30 cm reached 26.5 h into the storm; worst hour 37 mm (34% of the storm); water beside the road 1.26 m above its crest (design freeboard 0.30 m; P 1.00); road sag 1.2 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 37 mm; catchment 13.4 ha) (P 1.00); a culvert within 100 m is overtopped |
| 13 | 1.00 | Stafford Street | Worcester | 0.83 m of water at peak; over 30 cm for 20.0 h; 30 cm reached 25.0 h into the storm; worst hour 36 mm (32% of the storm); water beside the road 0.65 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 0.6 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.17); a culvert within 100 m is overtopped |
| 14 | 1.00 | Gilboa Street | Douglas | 0.96 m of water at peak; over 30 cm for 28.0 h; 30 cm reached 24.5 h into the storm; worst hour 33 mm (23% of the storm); water beside the road 0.49 m below its crest (design freeboard 0.30 m; P 0.11); a culvert within 100 m is overtopped |
| 15 | 1.00 | Route 16 | Uxbridge | 0.79 m of water at peak; over 30 cm for 21.0 h; 30 cm reached 26.5 h into the storm; worst hour 44 mm (23% of the storm); water beside the road 0.22 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 0.8 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.30); a culvert within 100 m is overtopped |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
