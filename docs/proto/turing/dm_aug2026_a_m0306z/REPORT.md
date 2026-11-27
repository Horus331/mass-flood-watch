# Road-closure prototype: aug2026_proto_dm_aug2026_a_m0306z

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on GPU (cuda)), 20 m grid, storm from 2026-08-03T06:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 45,099 |
| Expected closures (sum of probabilities) | 562.6 |
| Segments with closure probability >= 50% | 306 (216.2 km) |
| Further segments that may close (stream reaches the road crest) | 505 (309.7 km) |
| Culverts overtopped / surcharged | 913 / 16 of 10736 |
| Road segments cut off from hospitals | 3843 |
| Worst added trip time to a hospital | 48.5 min |
| Heaviest hour of rain | 34.8 mm |
| Flood model run time | 251 s |

## Checks against what happened

- Storm-day flood reports in the area: 3; water >= 10 cm within 100 m of 67% of them, vs 48% of random points (any day).
- Segments flagged impassable are 2.17x as likely as an average segment to have a report within 200 m.
- MassDOT repeating flood sites in the area: 30; 6 have a segment within 150 m at P >= 0.5 (share of all segments at P >= 0.5: 0.7%).

## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 1.00 | (unnamed) | Worcester | 1.02 m of water at peak; over 30 cm for 7.0 h; 30 cm reached 9.5 h into the storm; worst hour 25 mm (21% of the storm); water beside the road 0.90 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.7 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 25 mm; catchment 77.2 ha) (P 1.00) |
| 2 | 1.00 | (unnamed) | Framingham | 1.28 m of water at peak; over 30 cm for 8.0 h; 30 cm reached 8.5 h into the storm; worst hour 20 mm (25% of the storm); water beside the road 1.01 m above its crest (design freeboard 0.30 m; P 1.00); road sag 2.9 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 19 mm; catchment 15.3 ha) (P 1.00) |
| 3 | 1.00 | Route 117 | Lancaster | 1.44 m of water at peak; over 30 cm for 16.0 h; 30 cm reached 0.5 h into the storm; worst hour 22 mm (21% of the storm); culvert (Trib to Still River): headwater 5.18 m vs road crest 2.74 m, 27.6 m3/s |
| 4 | 1.00 | Shrewsbury Street | Worcester | 0.89 m of water at peak; over 30 cm for 9.0 h; 30 cm reached 7.5 h into the storm; worst hour 25 mm (22% of the storm); water beside the road 0.80 m above its crest (design freeboard 0.30 m; P 1.00); road sag 1.3 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 25 mm; catchment 127.8 ha) (P 1.00) |
| 5 | 1.00 | Martin Luther King Jr Boulevard | Worcester | 1.08 m of water at peak; over 30 cm for 10.0 h; 30 cm reached 6.5 h into the storm; worst hour 25 mm (22% of the storm); water beside the road 1.15 m above its crest (design freeboard 0.30 m; P 1.00); road sag 3.2 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 25 mm; catchment 60.2 ha) (P 1.00) |
| 6 | 1.00 | Shrewsbury Street | Worcester | 0.99 m of water at peak; over 30 cm for 9.0 h; 30 cm reached 7.5 h into the storm; worst hour 25 mm (22% of the storm); water beside the road 0.91 m above its crest (design freeboard 0.30 m; P 1.00); road sag 1.3 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 25 mm; catchment 127.8 ha) (P 1.00) |
| 7 | 1.00 | Cambridge Street | Worcester | 1.65 m of water at peak; over 30 cm for 9.0 h; 30 cm reached 7.5 h into the storm; worst hour 25 mm (21% of the storm); water beside the road 1.50 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.7 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 25 mm; catchment 77.2 ha) (P 1.00) |
| 8 | 1.00 | Route 131 | Southbridge | 0.97 m of water at peak; over 30 cm for 7.0 h; 30 cm reached 9.5 h into the storm; worst hour 21 mm (13% of the storm); a culvert within 100 m is overtopped |
| 9 | 1.00 | Southbridge Street | Worcester | 1.17 m of water at peak; over 30 cm for 8.0 h; 30 cm reached 8.5 h into the storm; worst hour 25 mm (21% of the storm); water beside the road 1.10 m above its crest (design freeboard 0.30 m; P 1.00); road sag 1.2 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 25 mm; catchment 13.4 ha) (P 1.00) |
| 10 | 1.00 | Route 131 | Southbridge | 0.95 m of water at peak; over 30 cm for 7.5 h; 30 cm reached 9.0 h into the storm; worst hour 21 mm (14% of the storm); water beside the road 0.06 m below its crest (design freeboard 0.30 m; P 0.94); a culvert within 100 m is overtopped |
| 11 | 1.00 | Depot Street | Fitchburg | 1.29 m of water at peak; over 30 cm for 14.0 h; 30 cm reached 0.5 h into the storm; worst hour 16 mm (13% of the storm); a culvert within 100 m is overtopped |
| 12 | 1.00 | John Fitch Highway | Fitchburg | 0.81 m of water at peak; over 30 cm for 6.5 h; 30 cm reached 8.0 h into the storm; worst hour 16 mm (14% of the storm) |
| 13 | 1.00 | Boundary Street | Marlborough | 0.68 m of water at peak; over 30 cm for 16.0 h; 30 cm reached 0.5 h into the storm; worst hour 24 mm (24% of the storm) |
| 14 | 1.00 | John Fitch Highway | Fitchburg | 0.69 m of water at peak; over 30 cm for 4.0 h; 30 cm reached 7.5 h into the storm; worst hour 16 mm (14% of the storm); runoff beside / along the road at 0.6 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.24); a culvert within 100 m is overtopped |
| 15 | 1.00 | Millbury Street | Grafton | 0.76 m of water at peak; over 30 cm for 10.0 h; 30 cm reached 6.5 h into the storm; worst hour 25 mm (23% of the storm) |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
