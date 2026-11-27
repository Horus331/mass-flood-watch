# Road-closure prototype: aug2026_proto_dm_aug2026_a_m0212z

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on GPU (cuda)), 20 m grid, storm from 2026-08-02T12:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 45,099 |
| Expected closures (sum of probabilities) | 343.8 |
| Segments with closure probability >= 50% | 142 (104.3 km) |
| Further segments that may close (stream reaches the road crest) | 343 (226.0 km) |
| Culverts overtopped / surcharged | 595 / 7 of 10736 |
| Road segments cut off from hospitals | 2199 |
| Worst added trip time to a hospital | 57.9 min |
| Heaviest hour of rain | 29.9 mm |
| Flood model run time | 426 s |

## Checks against what happened

- Storm-day flood reports in the area: 3; water >= 10 cm within 100 m of 33% of them, vs 36% of random points (any day).
- Segments flagged impassable are 0.0x as likely as an average segment to have a report within 200 m.
- MassDOT repeating flood sites in the area: 30; 3 have a segment within 150 m at P >= 0.5 (share of all segments at P >= 0.5: 0.3%).

## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 1.00 | (unnamed) | Framingham | 0.99 m of water at peak; over 30 cm for 6.0 h; 30 cm reached 28.5 h into the storm; worst hour 21 mm (34% of the storm); water beside the road 0.73 m above its crest (design freeboard 0.30 m; P 1.00); road sag 2.9 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 21 mm; catchment 15.3 ha) (P 1.00) |
| 2 | 1.00 | Martin Luther King Jr Boulevard | Worcester | 0.72 m of water at peak; over 30 cm for 6.5 h; 30 cm reached 28.0 h into the storm; worst hour 17 mm (19% of the storm); water beside the road 0.64 m above its crest (design freeboard 0.30 m; P 1.00); road sag 3.2 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 17 mm; catchment 60.2 ha) (P 1.00) |
| 3 | 1.00 | Shrewsbury Street | Worcester | 0.74 m of water at peak; over 30 cm for 6.0 h; 30 cm reached 28.5 h into the storm; worst hour 17 mm (20% of the storm); water beside the road 0.66 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.9 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 17 mm; catchment 127.8 ha) (P 1.00) |
| 4 | 1.00 | Shrewsbury Street | Worcester | 0.64 m of water at peak; over 30 cm for 5.0 h; 30 cm reached 29.5 h into the storm; worst hour 17 mm (20% of the storm); water beside the road 0.55 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.9 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 17 mm; catchment 127.8 ha) (P 1.00) |
| 5 | 1.00 | Cambridge Street | Worcester | 0.82 m of water at peak; over 30 cm for 5.5 h; 30 cm reached 29.0 h into the storm; worst hour 19 mm (20% of the storm); water beside the road 0.78 m above its crest (design freeboard 0.30 m; P 1.00); road sag 2.0 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 19 mm; catchment 77.2 ha) (P 1.00) |
| 6 | 1.00 | Paine Street | Bellingham | 0.93 m of water at peak; over 30 cm for 4.0 h; 30 cm reached 30.5 h into the storm; worst hour 20 mm (20% of the storm); a culvert within 100 m is overtopped |
| 7 | 1.00 | Wrentham Road | Bellingham | 0.70 m of water at peak; over 30 cm for 4.0 h; 30 cm reached 30.5 h into the storm; worst hour 20 mm (20% of the storm); water beside the road 0.11 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.9 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 20 mm; catchment 171.4 ha) (P 0.81); a culvert within 100 m is overtopped |
| 8 | 1.00 | Pine Grove Avenue | Bellingham | 0.96 m of water at peak; over 30 cm for 4.5 h; 30 cm reached 30.0 h into the storm; worst hour 20 mm (20% of the storm); water beside the road 0.35 m below its crest (design freeboard 0.30 m; P 0.38); a culvert within 100 m is overtopped |
| 9 | 1.00 | East Park Terrace | Worcester | 0.96 m of water at peak; over 30 cm for 7.0 h; 30 cm reached 27.5 h into the storm; worst hour 17 mm (19% of the storm); water beside the road 0.86 m above its crest (design freeboard 0.30 m; P 1.00); road sag 4.3 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 17 mm; catchment 127.8 ha) (P 1.00) |
| 10 | 1.00 | Ash Street | Clinton | 0.94 m of water at peak; over 30 cm for 7.0 h; 30 cm reached 27.5 h into the storm; worst hour 15 mm (21% of the storm); water beside the road 0.72 m above its crest (design freeboard 0.30 m; P 1.00) |
| 11 | 1.00 | Cemetery Street | Mendon | 0.75 m of water at peak; over 30 cm for 4.5 h; 30 cm reached 30.0 h into the storm; worst hour 22 mm (22% of the storm); a culvert within 100 m is overtopped |
| 12 | 1.00 | Bellingham Street | Mendon | 0.81 m of water at peak; over 30 cm for 3.5 h; 30 cm reached 31.0 h into the storm; worst hour 21 mm (22% of the storm); a culvert within 100 m is overtopped |
| 13 | 1.00 | Fantasia Drive | Worcester | 0.61 m of water at peak; over 30 cm for 4.5 h; 30 cm reached 30.0 h into the storm; worst hour 17 mm (20% of the storm); water beside the road 0.54 m above its crest (design freeboard 0.30 m; P 1.00); road sag 1.3 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 17 mm; catchment 127.8 ha) (P 1.00) |
| 14 | 1.00 | (unnamed) | Southbridge | 0.61 m of water at peak; over 30 cm for 3.0 h; 30 cm reached 31.5 h into the storm; worst hour 17 mm (19% of the storm); culvert (Unnamed tributary): headwater 0.87 m vs road crest 0.49 m, 0.1 m3/s |
| 15 | 1.00 | Kansas Street | Worcester | 0.62 m of water at peak; over 30 cm for 3.0 h; 30 cm reached 31.5 h into the storm; worst hour 19 mm (20% of the storm); water beside the road 0.40 m above its crest (design freeboard 0.30 m; P 1.00); road sag 2.0 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 19 mm; catchment 77.2 ha) (P 1.00) |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
