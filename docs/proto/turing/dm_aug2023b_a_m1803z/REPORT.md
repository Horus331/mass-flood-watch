# Road-closure prototype: aug2023b_proto_dm_aug2023b_a_m1803z

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on GPU (cuda)), 20 m grid, storm from 2023-08-18T03:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 45,099 |
| Expected closures (sum of probabilities) | 231.9 |
| Segments with closure probability >= 50% | 76 (53.2 km) |
| Further segments that may close (stream reaches the road crest) | 175 (119.8 km) |
| Culverts overtopped / surcharged | 376 / 5 of 10736 |
| Road segments cut off from hospitals | 1381 |
| Worst added trip time to a hospital | 49.4 min |
| Heaviest hour of rain | 41.6 mm |
| Flood model run time | 186 s |

## Checks against what happened

- Storm-day flood reports in the area: 3; water >= 10 cm within 100 m of 33% of them, vs 25% of random points (any day).
- Segments flagged impassable are 0.0x as likely as an average segment to have a report within 200 m.
- MassDOT repeating flood sites in the area: 30; 1 have a segment within 150 m at P >= 0.5 (share of all segments at P >= 0.5: 0.2%).

## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 1.00 | Depot Street | Fitchburg | 0.68 m of water at peak; over 30 cm for 9.0 h; 30 cm reached 0.5 h into the storm; worst hour 39 mm (69% of the storm); a culvert within 100 m is overtopped |
| 2 | 1.00 | East Park Terrace | Worcester | 0.65 m of water at peak; over 30 cm for 6.5 h; 30 cm reached 14.0 h into the storm; worst hour 26 mm (57% of the storm); water beside the road 0.55 m above its crest (design freeboard 0.30 m; P 1.00); road sag 4.3 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 26 mm; catchment 127.8 ha) (P 1.00) |
| 3 | 1.00 | Route 117 | Lancaster | 0.57 m of water at peak; over 30 cm for 20.0 h; 30 cm reached 0.5 h into the storm; worst hour 34 mm (60% of the storm); culvert (Trib to Still River): headwater 2.83 m vs road crest 2.74 m, 16.4 m3/s |
| 4 | 0.99 | (unnamed) | Spencer | 0.54 m of water at peak; over 30 cm for 7.0 h; 30 cm reached 13.5 h into the storm; worst hour 28 mm (43% of the storm) |
| 5 | 0.98 | Route 12 | Fitchburg | 0.51 m of water at peak; over 30 cm for 6.5 h; 30 cm reached 14.0 h into the storm; worst hour 39 mm (66% of the storm); a culvert within 100 m is overtopped |
| 6 | 0.98 | (unnamed) | Framingham | 0.50 m of water at peak; over 30 cm for 3.5 h; 30 cm reached 17.0 h into the storm; worst hour 27 mm (60% of the storm); road sag 2.9 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 27 mm; catchment 15.3 ha) (P 0.98) |
| 7 | 0.96 | Little Tree Lane | Framingham | 0.48 m of water at peak; over 30 cm for 2.0 h; 30 cm reached 1.0 h into the storm; worst hour 27 mm (63% of the storm); a culvert within 100 m is overtopped |
| 8 | 0.95 | Route 12 | Ashburnham | 0.46 m of water at peak; over 30 cm for 3.0 h; 30 cm reached 13.5 h into the storm; worst hour 39 mm (63% of the storm); a culvert within 100 m is overtopped |
| 9 | 0.94 | Lackey Lane | Barre | 0.46 m of water at peak; over 30 cm for 5.0 h; 30 cm reached 15.5 h into the storm; worst hour 34 mm (50% of the storm); a culvert within 100 m is overtopped |
| 10 | 0.94 | Oakmont Avenue | Westminster | 0.45 m of water at peak; over 30 cm for 7.5 h; 30 cm reached 13.0 h into the storm; worst hour 38 mm (61% of the storm); a culvert within 100 m is overtopped |
| 11 | 0.93 | Bartlett Street | Northborough | 0.45 m of water at peak; over 30 cm for 1.5 h; 30 cm reached 0.5 h into the storm; worst hour 22 mm (46% of the storm); a culvert within 100 m is overtopped |
| 12 | 0.93 | Boundary Street | Marlborough | 0.45 m of water at peak; over 30 cm for 20.0 h; 30 cm reached 0.5 h into the storm; worst hour 22 mm (48% of the storm); runoff beside / along the road at 0.7 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.12); a culvert within 100 m is overtopped |
| 13 | 0.93 | Belknap Road | Framingham | 0.45 m of water at peak; over 30 cm for 0.5 h; 30 cm reached 0.5 h into the storm; worst hour 27 mm (62% of the storm); a culvert within 100 m is overtopped |
| 14 | 0.93 | (unnamed) | Berlin | 0.44 m of water at peak; over 30 cm for 0.5 h; 30 cm reached 0.5 h into the storm; worst hour 25 mm (57% of the storm); water beside the road 0.42 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 1.1 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.13) |
| 15 | 0.92 | Route 62 | Berlin | 0.44 m of water at peak; over 30 cm for 0.5 h; 30 cm reached 0.5 h into the storm; worst hour 24 mm (56% of the storm); runoff beside / along the road at 1.1 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.13) |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
