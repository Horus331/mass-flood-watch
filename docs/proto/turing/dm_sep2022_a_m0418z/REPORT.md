# Road-closure prototype: sep2022_proto_dm_sep2022_a_m0418z

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on GPU (cuda)), 20 m grid, storm from 2022-09-04T18:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 45,099 |
| Expected closures (sum of probabilities) | 708.0 |
| Segments with closure probability >= 50% | 468 (349.6 km) |
| Further segments that may close (stream reaches the road crest) | 459 (281.9 km) |
| Culverts overtopped / surcharged | 1083 / 23 of 10736 |
| Road segments cut off from hospitals | 4156 |
| Worst added trip time to a hospital | 38.6 min |
| Heaviest hour of rain | 34.6 mm |
| Flood model run time | 409 s |

## Checks against what happened

- Storm-day flood reports in the area: 6; water >= 10 cm within 100 m of 67% of them, vs 44% of random points (any day).
- Segments flagged impassable are 2.51x as likely as an average segment to have a report within 200 m.
- MassDOT repeating flood sites in the area: 30; 5 have a segment within 150 m at P >= 0.5 (share of all segments at P >= 0.5: 1.0%).

## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 1.00 | (unnamed) | Worcester | 1.23 m of water at peak; over 30 cm for 9.5 h; 30 cm reached 21.0 h into the storm; worst hour 16 mm (12% of the storm); water beside the road 1.11 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.7 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 16 mm; catchment 77.2 ha) (P 1.00) |
| 2 | 1.00 | (unnamed) | Framingham | 1.76 m of water at peak; over 30 cm for 10.0 h; 30 cm reached 20.5 h into the storm; worst hour 12 mm (12% of the storm); water beside the road 1.50 m above its crest (design freeboard 0.30 m; P 1.00); road sag 2.9 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 12 mm; catchment 15.3 ha) (P 1.00) |
| 3 | 1.00 | Shrewsbury Street | Worcester | 0.98 m of water at peak; over 30 cm for 11.0 h; 30 cm reached 19.5 h into the storm; worst hour 15 mm (12% of the storm); water beside the road 0.89 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.8 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 15 mm; catchment 127.8 ha) (P 1.00) |
| 4 | 1.00 | Martin Luther King Jr Boulevard | Worcester | 1.29 m of water at peak; over 30 cm for 12.5 h; 30 cm reached 18.0 h into the storm; worst hour 16 mm (12% of the storm); water beside the road 1.38 m above its crest (design freeboard 0.30 m; P 1.00); road sag 3.2 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 16 mm; catchment 60.2 ha) (P 1.00); a culvert within 100 m is overtopped |
| 5 | 1.00 | Shrewsbury Street | Worcester | 1.08 m of water at peak; over 30 cm for 11.5 h; 30 cm reached 19.0 h into the storm; worst hour 15 mm (12% of the storm); water beside the road 1.00 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.8 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 15 mm; catchment 127.8 ha) (P 1.00) |
| 6 | 1.00 | Stafford Street | Worcester | 0.89 m of water at peak; over 30 cm for 12.0 h; 30 cm reached 18.5 h into the storm; worst hour 19 mm (13% of the storm); water beside the road 0.62 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 0.5 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.11); a culvert within 100 m is overtopped |
| 7 | 1.00 | James Street | Worcester | 0.70 m of water at peak; over 30 cm for 11.5 h; 30 cm reached 19.0 h into the storm; worst hour 19 mm (12% of the storm); a culvert within 100 m is overtopped |
| 8 | 1.00 | Cambridge Street | Worcester | 1.86 m of water at peak; over 30 cm for 11.0 h; 30 cm reached 19.5 h into the storm; worst hour 17 mm (12% of the storm); water beside the road 1.71 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.7 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 16 mm; catchment 77.2 ha) (P 1.00); a culvert within 100 m is overtopped |
| 9 | 1.00 | Southbridge Street | Worcester | 1.40 m of water at peak; over 30 cm for 10.0 h; 30 cm reached 20.5 h into the storm; worst hour 17 mm (12% of the storm); water beside the road 1.34 m above its crest (design freeboard 0.30 m; P 1.00); road sag 1.2 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 17 mm; catchment 13.4 ha) (P 1.00); a culvert within 100 m is overtopped |
| 10 | 1.00 | Route 131 | Southbridge | 1.59 m of water at peak; over 30 cm for 8.0 h; 30 cm reached 22.5 h into the storm; worst hour 20 mm (13% of the storm); a culvert within 100 m is overtopped |
| 11 | 1.00 | Route 131 | Southbridge | 1.56 m of water at peak; over 30 cm for 8.0 h; 30 cm reached 22.5 h into the storm; worst hour 19 mm (13% of the storm); water beside the road 0.55 m above its crest (design freeboard 0.30 m; P 1.00); fast water: depth x speed 0.19 m2/s (small cars unstable from 0.3); runoff beside / along the road at 0.5 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.10); a culvert within 100 m is overtopped |
| 12 | 1.00 | Boundary Street | Marlborough | 0.77 m of water at peak; over 30 cm for 30.0 h; 30 cm reached 0.5 h into the storm; worst hour 13 mm (14% of the storm); runoff beside / along the road at 0.7 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.12); a culvert within 100 m is overtopped |
| 13 | 1.00 | Route 131 | Southbridge | 0.86 m of water at peak; over 30 cm for 8.0 h; 30 cm reached 22.5 h into the storm; worst hour 19 mm (13% of the storm); a culvert within 100 m is overtopped |
| 14 | 1.00 | Route 16 | Hopedale | 0.70 m of water at peak; over 30 cm for 7.0 h; 30 cm reached 23.5 h into the storm; worst hour 21 mm (14% of the storm); a culvert within 100 m is overtopped |
| 15 | 1.00 | Gilboa Street | Douglas | 0.71 m of water at peak; over 30 cm for 9.5 h; 30 cm reached 21.0 h into the storm; worst hour 22 mm (17% of the storm); water beside the road 0.49 m below its crest (design freeboard 0.30 m; P 0.11); a culvert within 100 m is overtopped |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
