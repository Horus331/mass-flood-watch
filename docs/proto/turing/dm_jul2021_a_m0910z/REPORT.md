# Road-closure prototype: jul2021_proto_dm_jul2021_a_m0910z

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on GPU (cuda)), 20 m grid, storm from 2021-07-09T10:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 45,099 |
| Expected closures (sum of probabilities) | 667.1 |
| Segments with closure probability >= 50% | 400 (287.5 km) |
| Further segments that may close (stream reaches the road crest) | 576 (358.8 km) |
| Culverts overtopped / surcharged | 1064 / 17 of 10736 |
| Road segments cut off from hospitals | 4492 |
| Worst added trip time to a hospital | 60.0 min |
| Heaviest hour of rain | 28.1 mm |
| Flood model run time | 239 s |

## Checks against what happened

- Storm-day flood reports in the area: 9; water >= 10 cm within 100 m of 44% of them, vs 55% of random points (any day).
- Segments flagged impassable are 1.84x as likely as an average segment to have a report within 200 m.
- MassDOT repeating flood sites in the area: 30; 7 have a segment within 150 m at P >= 0.5 (share of all segments at P >= 0.5: 0.9%).

## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 1.00 | (unnamed) | Framingham | 2.11 m of water at peak; over 30 cm for 12.0 h; 30 cm reached 4.5 h into the storm; worst hour 23 mm (19% of the storm); water beside the road 1.84 m above its crest (design freeboard 0.30 m; P 1.00); road sag 2.9 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 23 mm; catchment 15.3 ha) (P 1.00) |
| 2 | 1.00 | (unnamed) | Worcester | 0.89 m of water at peak; over 30 cm for 9.0 h; 30 cm reached 7.5 h into the storm; worst hour 17 mm (17% of the storm); water beside the road 0.78 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.7 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 17 mm; catchment 77.2 ha) (P 1.00) |
| 3 | 1.00 | Route 146 | Uxbridge | 0.66 m of water at peak; over 30 cm for 12.5 h; 30 cm reached 4.0 h into the storm; worst hour 27 mm (21% of the storm); a culvert within 100 m is overtopped |
| 4 | 1.00 | Shrewsbury Street | Worcester | 0.95 m of water at peak; over 30 cm for 11.0 h; 30 cm reached 5.5 h into the storm; worst hour 17 mm (17% of the storm); water beside the road 0.87 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.8 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 17 mm; catchment 127.8 ha) (P 1.00) |
| 5 | 1.00 | Route 117 | Lancaster | 1.53 m of water at peak; over 30 cm for 16.0 h; 30 cm reached 0.5 h into the storm; worst hour 18 mm (19% of the storm); culvert (Trib to Still River): headwater 6.73 m vs road crest 2.74 m, 33.2 m3/s |
| 6 | 1.00 | Martin Luther King Jr Boulevard | Worcester | 1.14 m of water at peak; over 30 cm for 12.0 h; 30 cm reached 4.5 h into the storm; worst hour 16 mm (17% of the storm); water beside the road 1.21 m above its crest (design freeboard 0.30 m; P 1.00); road sag 3.2 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 16 mm; catchment 60.2 ha) (P 1.00); a culvert within 100 m is overtopped |
| 7 | 1.00 | Shrewsbury Street | Worcester | 1.06 m of water at peak; over 30 cm for 11.5 h; 30 cm reached 5.0 h into the storm; worst hour 17 mm (17% of the storm); water beside the road 0.98 m above its crest (design freeboard 0.30 m; P 1.00); fast water: depth x speed 0.19 m2/s (small cars unstable from 0.3); road sag 0.8 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 17 mm; catchment 127.8 ha) (P 1.00) |
| 8 | 1.00 | Cambridge Street | Worcester | 1.52 m of water at peak; over 30 cm for 11.0 h; 30 cm reached 5.5 h into the storm; worst hour 17 mm (17% of the storm); water beside the road 1.38 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.7 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 17 mm; catchment 77.2 ha) (P 1.00) |
| 9 | 1.00 | Route 16 | Hopedale | 0.76 m of water at peak; over 30 cm for 11.0 h; 30 cm reached 5.5 h into the storm; worst hour 27 mm (21% of the storm); a culvert within 100 m is overtopped |
| 10 | 1.00 | Southbridge Street | Worcester | 1.02 m of water at peak; over 30 cm for 9.5 h; 30 cm reached 7.0 h into the storm; worst hour 17 mm (17% of the storm); water beside the road 0.96 m above its crest (design freeboard 0.30 m; P 1.00); road sag 1.2 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 17 mm; catchment 13.4 ha) (P 1.00) |
| 11 | 1.00 | Gilboa Street | Douglas | 1.08 m of water at peak; over 30 cm for 14.5 h; 30 cm reached 2.0 h into the storm; worst hour 27 mm (21% of the storm); water beside the road 0.49 m below its crest (design freeboard 0.30 m; P 0.11); a culvert within 100 m is overtopped |
| 12 | 1.00 | Main Street | Ashland | 0.88 m of water at peak; over 30 cm for 10.5 h; 30 cm reached 6.0 h into the storm; worst hour 25 mm (20% of the storm); a culvert within 100 m is overtopped |
| 13 | 1.00 | Hartford Avenue East | Mendon | 0.68 m of water at peak; over 30 cm for 6.0 h; 30 cm reached 5.5 h into the storm; worst hour 27 mm (21% of the storm); a culvert within 100 m is overtopped |
| 14 | 1.00 | Auburn Street | Auburn | 0.75 m of water at peak; over 30 cm for 10.0 h; 30 cm reached 6.5 h into the storm; worst hour 18 mm (18% of the storm); water beside the road 0.46 m below its crest (design freeboard 0.30 m; P 0.15) |
| 15 | 1.00 | Central Street | Acton | 0.67 m of water at peak; over 30 cm for 9.0 h; 30 cm reached 7.5 h into the storm; worst hour 18 mm (17% of the storm); a culvert within 100 m is overtopped |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
