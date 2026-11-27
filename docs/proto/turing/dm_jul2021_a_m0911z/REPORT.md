# Road-closure prototype: jul2021_proto_dm_jul2021_a_m0911z

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on GPU (cuda)), 20 m grid, storm from 2021-07-09T11:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 45,099 |
| Expected closures (sum of probabilities) | 563.2 |
| Segments with closure probability >= 50% | 321 (218.7 km) |
| Further segments that may close (stream reaches the road crest) | 487 (287.5 km) |
| Culverts overtopped / surcharged | 896 / 13 of 10736 |
| Road segments cut off from hospitals | 3405 |
| Worst added trip time to a hospital | 41.2 min |
| Heaviest hour of rain | 28.4 mm |
| Flood model run time | 252 s |

## Checks against what happened

- Storm-day flood reports in the area: 9; water >= 10 cm within 100 m of 44% of them, vs 49% of random points (any day).
- Segments flagged impassable are 2.14x as likely as an average segment to have a report within 200 m.
- MassDOT repeating flood sites in the area: 30; 7 have a segment within 150 m at P >= 0.5 (share of all segments at P >= 0.5: 0.7%).

## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 1.00 | (unnamed) | Framingham | 1.78 m of water at peak; over 30 cm for 10.0 h; 30 cm reached 5.5 h into the storm; worst hour 20 mm (26% of the storm); water beside the road 1.51 m above its crest (design freeboard 0.30 m; P 1.00); road sag 2.9 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 20 mm; catchment 15.3 ha) (P 1.00) |
| 2 | 1.00 | (unnamed) | Worcester | 1.03 m of water at peak; over 30 cm for 8.5 h; 30 cm reached 7.0 h into the storm; worst hour 25 mm (26% of the storm); water beside the road 0.92 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.7 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 25 mm; catchment 77.2 ha) (P 1.00) |
| 3 | 1.00 | Shrewsbury Street | Worcester | 0.99 m of water at peak; over 30 cm for 10.0 h; 30 cm reached 5.5 h into the storm; worst hour 25 mm (25% of the storm); water beside the road 0.91 m above its crest (design freeboard 0.30 m; P 1.00); fast water: depth x speed 0.20 m2/s (small cars unstable from 0.3); road sag 0.8 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 25 mm; catchment 127.8 ha) (P 1.00) |
| 4 | 1.00 | Route 117 | Lancaster | 1.46 m of water at peak; over 30 cm for 15.0 h; 30 cm reached 0.5 h into the storm; worst hour 21 mm (25% of the storm); culvert (Trib to Still River): headwater 5.43 m vs road crest 2.74 m, 28.5 m3/s |
| 5 | 1.00 | Martin Luther King Jr Boulevard | Worcester | 1.28 m of water at peak; over 30 cm for 11.0 h; 30 cm reached 4.5 h into the storm; worst hour 25 mm (25% of the storm); water beside the road 1.35 m above its crest (design freeboard 0.30 m; P 1.00); road sag 3.2 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 25 mm; catchment 60.2 ha) (P 1.00); a culvert within 100 m is overtopped |
| 6 | 1.00 | Shrewsbury Street | Worcester | 1.10 m of water at peak; over 30 cm for 10.0 h; 30 cm reached 5.5 h into the storm; worst hour 25 mm (25% of the storm); water beside the road 1.01 m above its crest (design freeboard 0.30 m; P 1.00); fast water: depth x speed 0.23 m2/s (small cars unstable from 0.3); road sag 0.8 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 25 mm; catchment 127.8 ha) (P 1.00) |
| 7 | 1.00 | Cambridge Street | Worcester | 1.66 m of water at peak; over 30 cm for 10.0 h; 30 cm reached 5.5 h into the storm; worst hour 25 mm (26% of the storm); water beside the road 1.52 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.7 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 25 mm; catchment 77.2 ha) (P 1.00) |
| 8 | 1.00 | Southbridge Street | Worcester | 1.18 m of water at peak; over 30 cm for 9.0 h; 30 cm reached 6.5 h into the storm; worst hour 25 mm (26% of the storm); water beside the road 1.12 m above its crest (design freeboard 0.30 m; P 1.00); road sag 1.2 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 25 mm; catchment 13.4 ha) (P 1.00) |
| 9 | 1.00 | Gilboa Street | Douglas | 0.77 m of water at peak; over 30 cm for 13.5 h; 30 cm reached 2.0 h into the storm; worst hour 25 mm (25% of the storm); water beside the road 0.49 m below its crest (design freeboard 0.30 m; P 0.11); a culvert within 100 m is overtopped |
| 10 | 1.00 | Auburn Street | Auburn | 0.75 m of water at peak; over 30 cm for 9.5 h; 30 cm reached 6.0 h into the storm; worst hour 25 mm (26% of the storm); water beside the road 0.46 m below its crest (design freeboard 0.30 m; P 0.14) |
| 11 | 1.00 | Francis J. Mcgrath Boulevard | Worcester | 0.66 m of water at peak; over 30 cm for 4.5 h; 30 cm reached 6.0 h into the storm; worst hour 25 mm (25% of the storm); water beside the road 0.52 m above its crest (design freeboard 0.30 m; P 1.00); fast water: depth x speed 0.25 m2/s (small cars unstable from 0.3); runoff beside / along the road at 0.7 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.23); road sag 2.6 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 25 mm; catchment 9.4 ha) (P 1.00) |
| 12 | 1.00 | Grafton Street | Millbury | 0.67 m of water at peak; over 30 cm for 9.5 h; 30 cm reached 6.0 h into the storm; worst hour 25 mm (25% of the storm); a culvert within 100 m is overtopped |
| 13 | 1.00 | Quinsigamond Avenue | Worcester | 0.64 m of water at peak; over 30 cm for 7.5 h; 30 cm reached 8.0 h into the storm; worst hour 25 mm (26% of the storm) |
| 14 | 1.00 | Millbury Street | Grafton | 0.96 m of water at peak; over 30 cm for 11.0 h; 30 cm reached 4.5 h into the storm; worst hour 25 mm (25% of the storm) |
| 15 | 1.00 | Boundary Street | Marlborough | 0.95 m of water at peak; over 30 cm for 15.0 h; 30 cm reached 0.5 h into the storm; worst hour 21 mm (24% of the storm) |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
