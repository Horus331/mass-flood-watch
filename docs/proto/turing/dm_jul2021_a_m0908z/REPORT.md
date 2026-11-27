# Road-closure prototype: jul2021_proto_dm_jul2021_a_m0908z

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on GPU (cuda)), 20 m grid, storm from 2021-07-09T08:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 45,099 |
| Expected closures (sum of probabilities) | 1213.8 |
| Segments with closure probability >= 50% | 893 (626.4 km) |
| Further segments that may close (stream reaches the road crest) | 928 (550.8 km) |
| Culverts overtopped / surcharged | 1757 / 35 of 10736 |
| Road segments cut off from hospitals | 7670 |
| Worst added trip time to a hospital | 78.1 min |
| Heaviest hour of rain | 31.3 mm |
| Flood model run time | 275 s |

## Checks against what happened

- Storm-day flood reports in the area: 9; water >= 10 cm within 100 m of 67% of them, vs 64% of random points (any day).
- Segments flagged impassable are 1.1x as likely as an average segment to have a report within 200 m.
- MassDOT repeating flood sites in the area: 30; 11 have a segment within 150 m at P >= 0.5 (share of all segments at P >= 0.5: 2.0%).

## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 1.00 | (unnamed) | Worcester | 1.62 m of water at peak; over 30 cm for 10.0 h; 30 cm reached 8.5 h into the storm; worst hour 27 mm (21% of the storm); water beside the road 1.50 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.7 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 27 mm; catchment 77.2 ha) (P 1.00) |
| 2 | 1.00 | (unnamed) | Framingham | 2.17 m of water at peak; over 30 cm for 11.5 h; 30 cm reached 7.0 h into the storm; worst hour 24 mm (19% of the storm); water beside the road 1.90 m above its crest (design freeboard 0.30 m; P 1.00); road sag 2.9 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 24 mm; catchment 15.3 ha) (P 1.00) |
| 3 | 1.00 | I-290 | Shrewsbury | 0.74 m of water at peak; over 30 cm for 9.5 h; 30 cm reached 9.0 h into the storm; worst hour 26 mm (20% of the storm); water beside the road 0.74 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 0.5 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.12) |
| 4 | 1.00 | Route 9 | Framingham | 0.71 m of water at peak; over 30 cm for 11.5 h; 30 cm reached 2.0 h into the storm; worst hour 23 mm (19% of the storm); water beside the road 0.10 m above its crest (design freeboard 0.30 m; P 1.00); a culvert within 100 m is overtopped |
| 5 | 1.00 | Route 9 | Framingham | 0.71 m of water at peak; over 30 cm for 11.5 h; 30 cm reached 2.0 h into the storm; worst hour 24 mm (19% of the storm); a culvert within 100 m is overtopped |
| 6 | 1.00 | Route 9 | Worcester | 0.80 m of water at peak; over 30 cm for 9.0 h; 30 cm reached 9.5 h into the storm; worst hour 27 mm (20% of the storm); water beside the road 0.80 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 1.4 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.29) |
| 7 | 1.00 | Route 70 | Worcester | 0.81 m of water at peak; over 30 cm for 10.5 h; 30 cm reached 8.0 h into the storm; worst hour 27 mm (21% of the storm); a culvert within 100 m is overtopped |
| 8 | 1.00 | Route 70 | Worcester | 0.81 m of water at peak; over 30 cm for 10.5 h; 30 cm reached 8.0 h into the storm; worst hour 27 mm (21% of the storm); a culvert within 100 m is overtopped |
| 9 | 1.00 | Route 9 | Worcester | 0.80 m of water at peak; over 30 cm for 9.0 h; 30 cm reached 9.5 h into the storm; worst hour 27 mm (20% of the storm); water beside the road 0.80 m above its crest (design freeboard 0.30 m; P 1.00) |
| 10 | 1.00 | Route 117 | Lancaster | 1.78 m of water at peak; over 30 cm for 18.0 h; 30 cm reached 0.5 h into the storm; worst hour 23 mm (20% of the storm); culvert (Trib to Still River): headwater 13.89 m vs road crest 2.74 m, 51.7 m3/s |
| 11 | 1.00 | Shrewsbury Street | Worcester | 1.32 m of water at peak; over 30 cm for 11.0 h; 30 cm reached 7.5 h into the storm; worst hour 27 mm (20% of the storm); water beside the road 1.23 m above its crest (design freeboard 0.30 m; P 1.00); fast water: depth x speed 0.30 m2/s (small cars unstable from 0.3); runoff beside / along the road at 0.6 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.15); road sag 0.8 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 27 mm; catchment 127.8 ha) (P 1.00) |
| 12 | 1.00 | Martin Luther King Jr Boulevard | Worcester | 1.84 m of water at peak; over 30 cm for 11.5 h; 30 cm reached 7.0 h into the storm; worst hour 27 mm (21% of the storm); water beside the road 1.91 m above its crest (design freeboard 0.30 m; P 1.00); road sag 3.2 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 27 mm; catchment 60.2 ha) (P 1.00); a culvert within 100 m is overtopped |
| 13 | 1.00 | Shrewsbury Street | Worcester | 1.42 m of water at peak; over 30 cm for 11.0 h; 30 cm reached 7.5 h into the storm; worst hour 27 mm (20% of the storm); water beside the road 1.34 m above its crest (design freeboard 0.30 m; P 1.00); fast water: depth x speed 0.34 m2/s (small cars unstable from 0.3); runoff beside / along the road at 0.6 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.15); road sag 0.8 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 27 mm; catchment 127.8 ha) (P 1.00) |
| 14 | 1.00 | Martin Luther King Jr Boulevard | Worcester | 1.08 m of water at peak; over 30 cm for 11.5 h; 30 cm reached 7.0 h into the storm; worst hour 27 mm (21% of the storm); water beside the road 0.78 m above its crest (design freeboard 0.30 m; P 1.00); road sag 3.2 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 27 mm; catchment 60.2 ha) (P 1.00); a culvert within 100 m is overtopped |
| 15 | 1.00 | Stafford Street | Worcester | 0.72 m of water at peak; over 30 cm for 11.0 h; 30 cm reached 7.5 h into the storm; worst hour 26 mm (21% of the storm); water beside the road 0.65 m above its crest (design freeboard 0.30 m; P 1.00); fast water: depth x speed 0.19 m2/s (small cars unstable from 0.3); runoff beside / along the road at 0.6 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.17); a culvert within 100 m is overtopped |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
