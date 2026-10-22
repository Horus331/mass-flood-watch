# Road-closure prototype: jul2023_proto_jul2023_worcester_20m

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on GPU (cuda)), 20 m grid, storm from 2023-07-14T08:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 6,605 |
| Expected closures (sum of probabilities) | 62.3 |
| Segments with closure probability >= 50% | 43 (30.4 km) |
| Further segments that may close (stream reaches the road crest) | 48 (29.0 km) |
| Culverts overtopped / surcharged | 90 / 0 of 1023 |
| Road segments cut off from hospitals | 168 |
| Worst added trip time to a hospital | 15.0 min |
| Heaviest hour of rain | 25.9 mm |
| Flood model run time | 39 s |

## Checks against what happened

- Storm-day flood reports in the area: 3; water >= 10 cm within 100 m of 0% of them, vs 29% of random points (any day).
- Segments flagged impassable are 0.0x as likely as an average segment to have a report within 200 m.
- MassDOT repeating flood sites in the area: 7; 1 have a segment within 150 m at P >= 0.5 (share of all segments at P >= 0.5: 0.7%).

## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 1.00 | Martin Luther King Jr Boulevard | Worcester | 2.90 m of water at peak; over 30 cm for 18.0 h; 30 cm reached 0.5 h into the storm; worst hour 21 mm (82% of the storm); water beside the road 2.82 m above its crest (design freeboard 0.30 m; P 1.00); road sag 3.2 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 21 mm; catchment 60.2 ha) (P 1.00); a culvert within 100 m is overtopped |
| 2 | 1.00 | Martin Luther King Jr Boulevard | Worcester | 2.20 m of water at peak; over 30 cm for 18.0 h; 30 cm reached 0.5 h into the storm; worst hour 21 mm (82% of the storm); water beside the road 1.87 m above its crest (design freeboard 0.30 m; P 1.00); road sag 3.2 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 21 mm; catchment 60.2 ha) (P 1.00); a culvert within 100 m is overtopped |
| 3 | 1.00 | Foster Street | Worcester | 1.17 m of water at peak; over 30 cm for 18.0 h; 30 cm reached 0.5 h into the storm; worst hour 20 mm (83% of the storm); water beside the road 0.03 m below its crest (design freeboard 0.30 m; P 0.96); road sag 0.7 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 20 mm; catchment 22.1 ha) (P 0.80); a culvert within 100 m is overtopped |
| 4 | 1.00 | Foster Street | Worcester | 1.17 m of water at peak; over 30 cm for 18.0 h; 30 cm reached 0.5 h into the storm; worst hour 20 mm (83% of the storm); water beside the road 0.42 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.7 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 20 mm; catchment 22.1 ha) (P 0.80); a culvert within 100 m is overtopped |
| 5 | 1.00 | Stafford Street | Worcester | 1.23 m of water at peak; over 30 cm for 3.5 h; 30 cm reached 0.5 h into the storm; worst hour 20 mm (89% of the storm); water beside the road 0.02 m above its crest (design freeboard 0.30 m; P 0.98); road sag 0.4 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 19 mm; catchment 16.0 ha) (P 0.20); a culvert within 100 m is overtopped |
| 6 | 1.00 | James Street | Worcester | 0.72 m of water at peak; over 30 cm for 2.5 h; 30 cm reached 0.5 h into the storm; worst hour 21 mm (89% of the storm); a culvert within 100 m is overtopped |
| 7 | 1.00 | Ludlow Street | Worcester | 1.23 m of water at peak; over 30 cm for 3.5 h; 30 cm reached 0.5 h into the storm; worst hour 19 mm (89% of the storm); a culvert within 100 m is overtopped |
| 8 | 1.00 | (unnamed) | Worcester | 1.54 m of water at peak; over 30 cm for 17.0 h; 30 cm reached 1.5 h into the storm; worst hour 22 mm (82% of the storm); a culvert within 100 m is overtopped |
| 9 | 1.00 | (unnamed) | Spencer | 0.85 m of water at peak; over 30 cm for 9.5 h; 30 cm reached 0.5 h into the storm; worst hour 19 mm (68% of the storm) |
| 10 | 1.00 | Hastings Road | Spencer | 0.70 m of water at peak; over 30 cm for 1.0 h; 30 cm reached 0.5 h into the storm; worst hour 23 mm (76% of the storm); a culvert within 100 m is overtopped |
| 11 | 1.00 | Wire Village Road | Spencer | 0.73 m of water at peak; over 30 cm for 0.5 h; 30 cm reached 0.5 h into the storm; worst hour 24 mm (78% of the storm); a culvert within 100 m is overtopped |
| 12 | 1.00 | Black Hill Road | Paxton | 0.70 m of water at peak; over 30 cm for 0.5 h; 30 cm reached 0.0 h into the storm; worst hour 20 mm (79% of the storm); a culvert within 100 m is overtopped |
| 13 | 1.00 | Hampton Street | Auburn | 3.08 m of water at peak; worst hour 17 mm (82% of the storm); water beside the road 1.63 m above its crest (design freeboard 0.30 m; P 1.00); a culvert within 100 m is overtopped |
| 14 | 1.00 | Route 12 | Auburn | 2.09 m of water at peak; worst hour 17 mm (82% of the storm); water beside the road 3.66 m above its crest (design freeboard 0.30 m; P 1.00); a culvert within 100 m is overtopped |
| 15 | 1.00 | Gauthier Road | Spencer | 0.85 m of water at peak; worst hour 23 mm (77% of the storm); a culvert within 100 m is overtopped |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
