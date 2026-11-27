# Road-closure prototype: aug2021_proto_dm_aug2021_a_m1910z

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on GPU (cuda)), 20 m grid, storm from 2021-08-19T10:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 45,099 |
| Expected closures (sum of probabilities) | 168.3 |
| Segments with closure probability >= 50% | 43 (31.8 km) |
| Further segments that may close (stream reaches the road crest) | 149 (96.5 km) |
| Culverts overtopped / surcharged | 181 / 4 of 10736 |
| Road segments cut off from hospitals | 551 |
| Worst added trip time to a hospital | 35.6 min |
| Heaviest hour of rain | 32.7 mm |
| Flood model run time | 268 s |

## Checks against what happened

- Storm-day flood reports in the area: 10; water >= 10 cm within 100 m of 30% of them, vs 20% of random points (any day).
- Segments flagged impassable are 1.72x as likely as an average segment to have a report within 200 m.
- MassDOT repeating flood sites in the area: 30; 1 have a segment within 150 m at P >= 0.5 (share of all segments at P >= 0.5: 0.1%).

## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 1.00 | Route 117 | Lancaster | 1.23 m of water at peak; over 30 cm for 17.0 h; 30 cm reached 0.5 h into the storm; worst hour 27 mm (42% of the storm); culvert (Trib to Still River): headwater 4.03 m vs road crest 2.74 m, 22.5 m3/s |
| 2 | 1.00 | Depot Street | Fitchburg | 0.59 m of water at peak; over 30 cm for 14.0 h; 30 cm reached 0.5 h into the storm; worst hour 30 mm (31% of the storm); a culvert within 100 m is overtopped |
| 3 | 1.00 | Pine Grove Avenue | Bellingham | 0.59 m of water at peak; over 30 cm for 10.5 h; 30 cm reached 7.0 h into the storm; worst hour 23 mm (33% of the storm); a culvert within 100 m is overtopped |
| 4 | 1.00 | East Park Terrace | Worcester | 0.57 m of water at peak; over 30 cm for 10.0 h; 30 cm reached 7.5 h into the storm; worst hour 21 mm (42% of the storm); water beside the road 0.47 m above its crest (design freeboard 0.30 m; P 1.00); road sag 4.3 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 21 mm; catchment 127.8 ha) (P 1.00) |
| 5 | 0.99 | Paine Street | Bellingham | 0.55 m of water at peak; over 30 cm for 10.0 h; 30 cm reached 7.5 h into the storm; worst hour 23 mm (33% of the storm); a culvert within 100 m is overtopped |
| 6 | 0.98 | Little Tree Lane | Framingham | 0.50 m of water at peak; over 30 cm for 2.0 h; 30 cm reached 1.0 h into the storm; worst hour 17 mm (37% of the storm); a culvert within 100 m is overtopped |
| 7 | 0.97 | John Fitch Highway | Fitchburg | 0.49 m of water at peak; over 30 cm for 10.0 h; 30 cm reached 7.5 h into the storm; worst hour 33 mm (33% of the storm) |
| 8 | 0.97 | Mason Road | Townsend | 0.49 m of water at peak; over 30 cm for 4.5 h; 30 cm reached 12.5 h into the storm; worst hour 32 mm (28% of the storm) |
| 9 | 0.96 | Brooks Crossing | Townsend | 0.48 m of water at peak; over 30 cm for 5.5 h; 30 cm reached 12.0 h into the storm; worst hour 32 mm (28% of the storm) |
| 10 | 0.94 | Mason Road | Townsend | 0.45 m of water at peak; over 30 cm for 3.5 h; 30 cm reached 14.0 h into the storm; worst hour 32 mm (29% of the storm); a culvert within 100 m is overtopped |
| 11 | 0.91 | Wrentham Road | Bellingham | 0.43 m of water at peak; over 30 cm for 10.0 h; 30 cm reached 7.5 h into the storm; worst hour 23 mm (33% of the storm); water beside the road 0.13 m below its crest (design freeboard 0.30 m; P 0.87); a culvert within 100 m is overtopped |
| 12 | 0.89 | John Fitch Highway | Fitchburg | 0.42 m of water at peak; over 30 cm for 9.5 h; 30 cm reached 8.0 h into the storm; worst hour 32 mm (33% of the storm); runoff beside / along the road at 0.5 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.10); a culvert within 100 m is overtopped |
| 13 | 0.88 | Ash Street | Clinton | 0.41 m of water at peak; over 30 cm for 1.5 h; 30 cm reached 16.0 h into the storm; worst hour 23 mm (38% of the storm); water beside the road 0.20 m above its crest (design freeboard 0.30 m; P 1.00) |
| 14 | 0.87 | Depot Square | Leominster | 0.41 m of water at peak; over 30 cm for 9.5 h; 30 cm reached 8.0 h into the storm; worst hour 29 mm (34% of the storm); a culvert within 100 m is overtopped |
| 15 | 0.87 | (unnamed) | Leominster | 0.41 m of water at peak; over 30 cm for 9.5 h; 30 cm reached 8.0 h into the storm; worst hour 30 mm (34% of the storm); a culvert within 100 m is overtopped |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
