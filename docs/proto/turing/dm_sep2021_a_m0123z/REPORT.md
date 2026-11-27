# Road-closure prototype: sep2021_proto_dm_sep2021_a_m0123z

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on GPU (cuda)), 20 m grid, storm from 2021-09-01T23:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 45,099 |
| Expected closures (sum of probabilities) | 1206.0 |
| Segments with closure probability >= 50% | 907 (658.7 km) |
| Further segments that may close (stream reaches the road crest) | 922 (556.0 km) |
| Culverts overtopped / surcharged | 1785 / 45 of 10736 |
| Road segments cut off from hospitals | 7324 |
| Worst added trip time to a hospital | 81.7 min |
| Heaviest hour of rain | 59.0 mm |
| Flood model run time | 301 s |

## Checks against what happened

- Storm-day flood reports in the area: 10; water >= 10 cm within 100 m of 70% of them, vs 63% of random points (any day).
- Segments flagged impassable are 1.47x as likely as an average segment to have a report within 200 m.
- MassDOT repeating flood sites in the area: 30; 12 have a segment within 150 m at P >= 0.5 (share of all segments at P >= 0.5: 2.0%).

## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 1.00 | (unnamed) | Framingham | 2.12 m of water at peak; over 30 cm for 12.0 h; 30 cm reached 7.5 h into the storm; worst hour 26 mm (20% of the storm); water beside the road 1.86 m above its crest (design freeboard 0.30 m; P 1.00); road sag 2.9 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 26 mm; catchment 15.3 ha) (P 1.00) |
| 2 | 1.00 | (unnamed) | Worcester | 1.37 m of water at peak; over 30 cm for 10.0 h; 30 cm reached 9.5 h into the storm; worst hour 21 mm (17% of the storm); water beside the road 1.25 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.7 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 21 mm; catchment 77.2 ha) (P 1.00) |
| 3 | 1.00 | Route 9 | Framingham | 0.64 m of water at peak; over 30 cm for 12.0 h; 30 cm reached 2.0 h into the storm; worst hour 27 mm (20% of the storm); water beside the road 0.09 m above its crest (design freeboard 0.30 m; P 1.00); a culvert within 100 m is overtopped |
| 4 | 1.00 | Route 9 | Framingham | 0.64 m of water at peak; over 30 cm for 12.0 h; 30 cm reached 2.0 h into the storm; worst hour 27 mm (20% of the storm); a culvert within 100 m is overtopped |
| 5 | 1.00 | Route 146 | Uxbridge | 1.03 m of water at peak; over 30 cm for 12.5 h; 30 cm reached 7.0 h into the storm; worst hour 39 mm (21% of the storm); a culvert within 100 m is overtopped |
| 6 | 1.00 | Route 70 | Worcester | 0.63 m of water at peak; over 30 cm for 11.0 h; 30 cm reached 8.5 h into the storm; worst hour 20 mm (17% of the storm); a culvert within 100 m is overtopped |
| 7 | 1.00 | Route 70 | Worcester | 0.64 m of water at peak; over 30 cm for 11.0 h; 30 cm reached 8.5 h into the storm; worst hour 20 mm (17% of the storm); a culvert within 100 m is overtopped |
| 8 | 1.00 | Route 117 | Lancaster | 1.84 m of water at peak; over 30 cm for 19.0 h; 30 cm reached 0.5 h into the storm; worst hour 16 mm (14% of the storm); culvert (Trib to Still River): headwater 14.59 m vs road crest 2.74 m, 53.2 m3/s |
| 9 | 1.00 | Shrewsbury Street | Worcester | 1.14 m of water at peak; over 30 cm for 11.5 h; 30 cm reached 8.0 h into the storm; worst hour 20 mm (17% of the storm); water beside the road 1.05 m above its crest (design freeboard 0.30 m; P 1.00); fast water: depth x speed 0.20 m2/s (small cars unstable from 0.3); road sag 0.8 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 20 mm; catchment 127.8 ha) (P 1.00) |
| 10 | 1.00 | Shrewsbury Street | Worcester | 1.24 m of water at peak; over 30 cm for 12.0 h; 30 cm reached 7.5 h into the storm; worst hour 20 mm (17% of the storm); water beside the road 1.16 m above its crest (design freeboard 0.30 m; P 1.00); fast water: depth x speed 0.23 m2/s (small cars unstable from 0.3); road sag 0.8 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 20 mm; catchment 127.8 ha) (P 1.00) |
| 11 | 1.00 | Martin Luther King Jr Boulevard | Worcester | 1.46 m of water at peak; over 30 cm for 12.5 h; 30 cm reached 7.0 h into the storm; worst hour 20 mm (17% of the storm); water beside the road 1.53 m above its crest (design freeboard 0.30 m; P 1.00); road sag 3.2 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 20 mm; catchment 60.2 ha) (P 1.00); a culvert within 100 m is overtopped |
| 12 | 1.00 | Martin Luther King Jr Boulevard | Worcester | 0.70 m of water at peak; over 30 cm for 12.5 h; 30 cm reached 7.0 h into the storm; worst hour 20 mm (17% of the storm); water beside the road 0.40 m above its crest (design freeboard 0.30 m; P 1.00); road sag 3.2 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 20 mm; catchment 60.2 ha) (P 1.00); a culvert within 100 m is overtopped |
| 13 | 1.00 | Route 131 | Southbridge | 1.53 m of water at peak; over 30 cm for 11.5 h; 30 cm reached 8.0 h into the storm; worst hour 40 mm (25% of the storm); runoff beside / along the road at 0.6 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.26); a culvert within 100 m is overtopped |
| 14 | 1.00 | (unnamed) | Leominster | 0.72 m of water at peak; over 30 cm for 11.0 h; 30 cm reached 8.5 h into the storm; worst hour 17 mm (17% of the storm); water beside the road 0.25 m below its crest (design freeboard 0.30 m; P 0.63); a culvert within 100 m is overtopped |
| 15 | 1.00 | Route 126 | Bellingham | 0.88 m of water at peak; over 30 cm for 11.5 h; 30 cm reached 8.0 h into the storm; worst hour 46 mm (24% of the storm); a culvert within 100 m is overtopped |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
