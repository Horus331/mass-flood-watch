# Road-closure prototype: aug2021_proto_dm_aug2021_a_m1909z

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on GPU (cuda)), 20 m grid, storm from 2021-08-19T09:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 45,099 |
| Expected closures (sum of probabilities) | 1065.1 |
| Segments with closure probability >= 50% | 747 (534.1 km) |
| Further segments that may close (stream reaches the road crest) | 935 (582.0 km) |
| Culverts overtopped / surcharged | 1523 / 23 of 10736 |
| Road segments cut off from hospitals | 6949 |
| Worst added trip time to a hospital | 67.4 min |
| Heaviest hour of rain | 47.0 mm |
| Flood model run time | 288 s |

## Checks against what happened

- Storm-day flood reports in the area: 10; water >= 10 cm within 100 m of 70% of them, vs 57% of random points (any day).
- Segments flagged impassable are 4.01x as likely as an average segment to have a report within 200 m.
- MassDOT repeating flood sites in the area: 30; 10 have a segment within 150 m at P >= 0.5 (share of all segments at P >= 0.5: 1.7%).

## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 1.00 | (unnamed) | Worcester | 1.32 m of water at peak; over 30 cm for 11.0 h; 30 cm reached 7.5 h into the storm; worst hour 43 mm (41% of the storm); water beside the road 1.20 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.7 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 43 mm; catchment 77.2 ha) (P 1.00) |
| 2 | 1.00 | (unnamed) | Framingham | 1.78 m of water at peak; over 30 cm for 11.0 h; 30 cm reached 7.5 h into the storm; worst hour 32 mm (40% of the storm); water beside the road 1.51 m above its crest (design freeboard 0.30 m; P 1.00); road sag 2.9 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 32 mm; catchment 15.3 ha) (P 1.00) |
| 3 | 1.00 | Route 70 | Worcester | 0.66 m of water at peak; over 30 cm for 11.5 h; 30 cm reached 7.0 h into the storm; worst hour 42 mm (42% of the storm); a culvert within 100 m is overtopped |
| 4 | 1.00 | Route 70 | Worcester | 0.67 m of water at peak; over 30 cm for 11.5 h; 30 cm reached 7.0 h into the storm; worst hour 42 mm (42% of the storm); a culvert within 100 m is overtopped |
| 5 | 1.00 | Shrewsbury Street | Worcester | 1.04 m of water at peak; over 30 cm for 12.0 h; 30 cm reached 6.5 h into the storm; worst hour 42 mm (42% of the storm); water beside the road 0.95 m above its crest (design freeboard 0.30 m; P 1.00); fast water: depth x speed 0.26 m2/s (small cars unstable from 0.3); runoff beside / along the road at 0.6 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.12); road sag 0.8 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 42 mm; catchment 127.8 ha) (P 1.00) |
| 6 | 1.00 | Route 117 | Lancaster | 2.02 m of water at peak; over 30 cm for 18.0 h; 30 cm reached 0.5 h into the storm; worst hour 29 mm (34% of the storm); water beside the road 0.38 m below its crest (design freeboard 0.30 m; P 0.30); culvert (Trib to Still River): headwater 23.38 m vs road crest 2.74 m, 69.0 m3/s |
| 7 | 1.00 | Shrewsbury Street | Worcester | 1.14 m of water at peak; over 30 cm for 12.0 h; 30 cm reached 6.5 h into the storm; worst hour 42 mm (42% of the storm); water beside the road 1.06 m above its crest (design freeboard 0.30 m; P 1.00); fast water: depth x speed 0.30 m2/s (small cars unstable from 0.3); runoff beside / along the road at 0.6 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.12); road sag 0.8 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 42 mm; catchment 127.8 ha) (P 1.00) |
| 8 | 1.00 | Martin Luther King Jr Boulevard | Worcester | 1.43 m of water at peak; over 30 cm for 12.5 h; 30 cm reached 6.0 h into the storm; worst hour 42 mm (42% of the storm); water beside the road 1.50 m above its crest (design freeboard 0.30 m; P 1.00); road sag 3.2 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 42 mm; catchment 60.2 ha) (P 1.00); a culvert within 100 m is overtopped |
| 9 | 1.00 | Martin Luther King Jr Boulevard | Worcester | 0.66 m of water at peak; over 30 cm for 12.5 h; 30 cm reached 6.0 h into the storm; worst hour 42 mm (42% of the storm); water beside the road 0.37 m above its crest (design freeboard 0.30 m; P 1.00); road sag 3.2 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 42 mm; catchment 60.2 ha) (P 1.00); a culvert within 100 m is overtopped |
| 10 | 1.00 | (unnamed) | Leominster | 0.94 m of water at peak; over 30 cm for 11.0 h; 30 cm reached 7.5 h into the storm; worst hour 44 mm (38% of the storm); water beside the road 0.20 m below its crest (design freeboard 0.30 m; P 0.75); a culvert within 100 m is overtopped |
| 11 | 1.00 | Stafford Street | Worcester | 0.68 m of water at peak; over 30 cm for 12.5 h; 30 cm reached 6.0 h into the storm; worst hour 43 mm (38% of the storm); water beside the road 0.67 m above its crest (design freeboard 0.30 m; P 1.00); fast water: depth x speed 0.22 m2/s (small cars unstable from 0.3); runoff beside / along the road at 0.6 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.20); a culvert within 100 m is overtopped |
| 12 | 1.00 | Southbridge Street | Worcester | 1.50 m of water at peak; over 30 cm for 11.5 h; 30 cm reached 7.0 h into the storm; worst hour 43 mm (41% of the storm); water beside the road 1.43 m above its crest (design freeboard 0.30 m; P 1.00); road sag 1.2 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 43 mm; catchment 13.4 ha) (P 1.00); a culvert within 100 m is overtopped |
| 13 | 1.00 | James Street | Worcester | 0.65 m of water at peak; over 30 cm for 12.5 h; 30 cm reached 6.0 h into the storm; worst hour 43 mm (38% of the storm); runoff beside / along the road at 0.5 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.19); a culvert within 100 m is overtopped |
| 14 | 1.00 | Cambridge Street | Worcester | 1.95 m of water at peak; over 30 cm for 12.0 h; 30 cm reached 6.5 h into the storm; worst hour 43 mm (40% of the storm); water beside the road 1.80 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 0.6 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.10); road sag 0.7 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 43 mm; catchment 77.2 ha) (P 1.00); a culvert within 100 m is overtopped |
| 15 | 1.00 | Route 131 | Southbridge | 0.98 m of water at peak; over 30 cm for 12.0 h; 30 cm reached 6.5 h into the storm; worst hour 47 mm (41% of the storm); water beside the road 0.04 m below its crest (design freeboard 0.30 m; P 0.96); a culvert within 100 m is overtopped |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
