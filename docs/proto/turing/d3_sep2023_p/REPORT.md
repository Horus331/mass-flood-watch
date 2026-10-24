# Road-closure prototype: sep2023_proto_d3_sep2023_p

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on GPU (cuda)), 20 m grid, storm from 2023-09-11T16:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 45,099 |
| Expected closures (sum of probabilities) | 405.4 |
| Segments with closure probability >= 50% | 276 (197.0 km) |
| Further segments that may close (stream reaches the road crest) | 268 (179.5 km) |
| Culverts overtopped / surcharged | 493 / 14 of 10736 |
| Road segments cut off from hospitals | 1951 |
| Worst added trip time to a hospital | 33.6 min |
| Heaviest hour of rain | 102.0 mm |
| Flood model run time | 1364 s |

## Checks against what happened

- Storm-day flood reports in the area: 11; water >= 10 cm within 100 m of 82% of them, vs 20% of random points (any day).
- Segments flagged impassable are 10.73x as likely as an average segment to have a report within 200 m.
- MassDOT repeating flood sites in the area: 30; 4 have a segment within 150 m at P >= 0.5 (share of all segments at P >= 0.5: 0.6%).

## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 1.00 | Route 2 | Leominster | 8.42 m of water at peak; over 30 cm for 43.0 h; 30 cm reached 5.5 h into the storm; worst hour 66 mm (40% of the storm); runoff beside / along the road at 2.0 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.42); a culvert within 100 m is overtopped |
| 2 | 1.00 | Route 2 | Harvard | 0.73 m of water at peak; over 30 cm for 27.5 h; 30 cm reached 21.0 h into the storm; worst hour 29 mm (41% of the storm); a culvert within 100 m is overtopped |
| 3 | 1.00 | Route 2 | Harvard | 0.73 m of water at peak; over 30 cm for 27.5 h; 30 cm reached 21.0 h into the storm; worst hour 33 mm (43% of the storm); a culvert within 100 m is overtopped |
| 4 | 1.00 | Martin Luther King Jr Boulevard | Worcester | 2.98 m of water at peak; over 30 cm for 47.5 h; 30 cm reached 1.0 h into the storm; worst hour 10 mm (29% of the storm); water beside the road 2.90 m above its crest (design freeboard 0.30 m; P 1.00); road sag 3.2 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 10 mm; catchment 60.2 ha) (P 1.00); a culvert within 100 m is overtopped |
| 5 | 1.00 | Martin Luther King Jr Boulevard | Worcester | 2.28 m of water at peak; over 30 cm for 47.5 h; 30 cm reached 1.0 h into the storm; worst hour 10 mm (30% of the storm); water beside the road 1.95 m above its crest (design freeboard 0.30 m; P 1.00); road sag 3.2 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 10 mm; catchment 60.2 ha) (P 1.00); a culvert within 100 m is overtopped |
| 6 | 1.00 | Foster Street | Worcester | 1.25 m of water at peak; over 30 cm for 41.5 h; 30 cm reached 7.0 h into the storm; worst hour 9 mm (28% of the storm); water beside the road 0.40 m below its crest (design freeboard 0.30 m; P 0.25); a culvert within 100 m is overtopped |
| 7 | 1.00 | Foster Street | Worcester | 1.25 m of water at peak; over 30 cm for 41.5 h; 30 cm reached 7.0 h into the storm; worst hour 9 mm (28% of the storm); water beside the road 0.28 m below its crest (design freeboard 0.30 m; P 0.55); a culvert within 100 m is overtopped |
| 8 | 1.00 | (unnamed) | Leominster | 1.57 m of water at peak; over 30 cm for 27.5 h; 30 cm reached 5.5 h into the storm; worst hour 84 mm (43% of the storm); water beside the road 0.04 m above its crest (design freeboard 0.30 m; P 0.99); a culvert within 100 m is overtopped |
| 9 | 1.00 | Depot Street | Fitchburg | 1.09 m of water at peak; over 30 cm for 46.5 h; 30 cm reached 0.5 h into the storm; worst hour 31 mm (29% of the storm); runoff beside / along the road at 0.6 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.12); a culvert within 100 m is overtopped |
| 10 | 1.00 | Water Street | Clinton | 1.05 m of water at peak; over 30 cm for 48.0 h; 30 cm reached 0.5 h into the storm; worst hour 6 mm (25% of the storm) |
| 11 | 1.00 | Water Street | Leominster | 1.57 m of water at peak; over 30 cm for 27.5 h; 30 cm reached 5.5 h into the storm; worst hour 84 mm (43% of the storm); a culvert within 100 m is overtopped |
| 12 | 1.00 | Route 12 | Leominster | 1.06 m of water at peak; over 30 cm for 9.5 h; 30 cm reached 6.0 h into the storm; worst hour 77 mm (43% of the storm); water beside the road 0.10 m above its crest (design freeboard 0.30 m; P 1.00); a culvert within 100 m is overtopped |
| 13 | 1.00 | Litchfield Street | Leominster | 1.65 m of water at peak; over 30 cm for 14.0 h; 30 cm reached 6.5 h into the storm; worst hour 65 mm (41% of the storm); a culvert within 100 m is overtopped |
| 14 | 1.00 | Route 117 | Leominster | 1.06 m of water at peak; over 30 cm for 9.5 h; 30 cm reached 6.5 h into the storm; worst hour 58 mm (38% of the storm); cut off from hospitals |
| 15 | 1.00 | Route 117 | Leominster | 1.06 m of water at peak; over 30 cm for 9.5 h; 30 cm reached 6.5 h into the storm; worst hour 60 mm (39% of the storm); water beside the road 0.10 m below its crest (design freeboard 0.30 m; P 0.91); runoff beside / along the road at 0.8 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.27); a culvert within 100 m is overtopped |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
