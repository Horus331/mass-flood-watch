# Road-closure prototype: aug2021_proto_dm_aug2021_ref

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on GPU (cuda)), 20 m grid, storm from 2021-08-19T09:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 45,099 |
| Expected closures (sum of probabilities) | 333.4 |
| Segments with closure probability >= 50% | 165 (120.6 km) |
| Further segments that may close (stream reaches the road crest) | 374 (228.0 km) |
| Culverts overtopped / surcharged | 476 / 7 of 10736 |
| Road segments cut off from hospitals | 1870 |
| Worst added trip time to a hospital | 33.2 min |
| Heaviest hour of rain | 93.6 mm |
| Flood model run time | 239 s |

## Checks against what happened

- Storm-day flood reports in the area: 10; water >= 10 cm within 100 m of 40% of them, vs 34% of random points (any day).
- Segments flagged impassable are 4.07x as likely as an average segment to have a report within 200 m.
- MassDOT repeating flood sites in the area: 30; 4 have a segment within 150 m at P >= 0.5 (share of all segments at P >= 0.5: 0.4%).

## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 1.00 | (unnamed) | Framingham | 1.23 m of water at peak; over 30 cm for 11.0 h; 30 cm reached 7.5 h into the storm; worst hour 26 mm (47% of the storm); water beside the road 0.97 m above its crest (design freeboard 0.30 m; P 1.00); road sag 2.9 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 24 mm; catchment 15.3 ha) (P 1.00) |
| 2 | 1.00 | Route 117 | Lancaster | 0.80 m of water at peak; over 30 cm for 18.0 h; 30 cm reached 0.5 h into the storm; worst hour 24 mm (40% of the storm); culvert (Trib to Still River): headwater 2.61 m vs road crest 2.74 m, 15.4 m3/s |
| 3 | 1.00 | Cambridge Street | Worcester | 0.99 m of water at peak; over 30 cm for 11.5 h; 30 cm reached 7.0 h into the storm; worst hour 29 mm (48% of the storm); water beside the road 0.84 m above its crest (design freeboard 0.30 m; P 1.00); road sag 2.0 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 28 mm; catchment 77.2 ha) (P 1.00) |
| 4 | 1.00 | Gilboa Street | Douglas | 1.10 m of water at peak; over 30 cm for 14.0 h; 30 cm reached 4.5 h into the storm; worst hour 73 mm (67% of the storm); water beside the road 0.49 m below its crest (design freeboard 0.30 m; P 0.11); a culvert within 100 m is overtopped |
| 5 | 1.00 | Auburn Street | Auburn | 0.80 m of water at peak; over 30 cm for 11.5 h; 30 cm reached 7.0 h into the storm; worst hour 30 mm (48% of the storm); water beside the road 0.41 m below its crest (design freeboard 0.30 m; P 0.23) |
| 6 | 1.00 | Linwood Avenue | Northbridge | 0.71 m of water at peak; over 30 cm for 12.0 h; 30 cm reached 6.5 h into the storm; worst hour 60 mm (60% of the storm); a culvert within 100 m is overtopped |
| 7 | 1.00 | (unnamed) | Southbridge | 1.55 m of water at peak; over 30 cm for 13.5 h; 30 cm reached 5.0 h into the storm; worst hour 59 mm (66% of the storm); culvert (Unnamed tributary): headwater 1652.88 m vs road crest 0.49 m, 5.3 m3/s |
| 8 | 1.00 | Village Drive | Southbridge | 0.83 m of water at peak; over 30 cm for 13.5 h; 30 cm reached 5.0 h into the storm; worst hour 62 mm (67% of the storm); a culvert within 100 m is overtopped |
| 9 | 1.00 | Chasm Loop Trail | Sutton | 0.93 m of water at peak; over 30 cm for 12.5 h; 30 cm reached 6.0 h into the storm; worst hour 64 mm (69% of the storm); road sag 0.5 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 63 mm; catchment 2.0 ha) (P 0.93); a culvert within 100 m is overtopped |
| 10 | 1.00 | Rogerson Crossing | Uxbridge | 1.19 m of water at peak; over 30 cm for 13.5 h; 30 cm reached 0.5 h into the storm; worst hour 20 mm (34% of the storm); a culvert within 100 m is overtopped |
| 11 | 1.00 | (unnamed) | Holliston | 0.68 m of water at peak; over 30 cm for 6.0 h; 30 cm reached 7.5 h into the storm; worst hour 40 mm (62% of the storm); a culvert within 100 m is overtopped |
| 12 | 1.00 | East Park Terrace | Worcester | 0.77 m of water at peak; over 30 cm for 12.5 h; 30 cm reached 6.0 h into the storm; worst hour 23 mm (44% of the storm); water beside the road 0.66 m above its crest (design freeboard 0.30 m; P 1.00); road sag 4.3 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 23 mm; catchment 127.8 ha) (P 1.00) |
| 13 | 1.00 | (unnamed) | Oxford | 0.76 m of water at peak; over 30 cm for 8.5 h; 30 cm reached 10.0 h into the storm; worst hour 43 mm (52% of the storm); water beside the road 0.06 m above its crest (design freeboard 0.30 m; P 0.99); road sag 1.8 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 42 mm; catchment 475.3 ha) (P 0.46); a culvert within 100 m is overtopped |
| 14 | 1.00 | Kansas Street | Worcester | 0.69 m of water at peak; over 30 cm for 9.5 h; 30 cm reached 9.0 h into the storm; worst hour 28 mm (48% of the storm); water beside the road 0.47 m above its crest (design freeboard 0.30 m; P 1.00); road sag 2.0 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 28 mm; catchment 77.2 ha) (P 1.00) |
| 15 | 1.00 | Coolidge Road | Worcester | 0.65 m of water at peak; over 30 cm for 9.0 h; 30 cm reached 7.0 h into the storm; worst hour 28 mm (45% of the storm); water beside the road 0.61 m above its crest (design freeboard 0.30 m; P 1.00); fast water: depth x speed 0.25 m2/s (small cars unstable from 0.3); runoff beside / along the road at 0.6 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.15); road sag 0.7 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 28 mm; catchment 17.7 ha) (P 1.00) |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
