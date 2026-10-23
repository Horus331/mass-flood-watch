# Road-closure prototype: aug2019_loss_aug2019_oxford_20m

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on CPU (OpenMP)), 20 m grid, storm from 2019-08-07T19:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 6,290 |
| Expected closures (sum of probabilities) | 36.0 |
| Segments with closure probability >= 50% | 15 (9.4 km) |
| Further segments that may close (stream reaches the road crest) | 44 (26.0 km) |
| Culverts overtopped / surcharged | 63 / 0 of 1136 |
| Road segments cut off from hospitals | 156 |
| Worst added trip time to a hospital | 18.0 min |
| Heaviest hour of rain | 32.7 mm |
| Flood model run time | 1379 s |

## Checks against what happened

- Storm-day flood reports in the area: 3; water >= 10 cm within 100 m of 33% of them, vs 42% of random points (any day).
- Segments flagged impassable are 0.0x as likely as an average segment to have a report within 200 m.
- MassDOT repeating flood sites in the area: 4; 0 have a segment within 150 m at P >= 0.5 (share of all segments at P >= 0.5: 0.2%).

## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 0.97 | Providence Street | Millbury | 0.49 m of water at peak; over 30 cm for 11.5 h; 30 cm reached 7.0 h into the storm; worst hour 19 mm (38% of the storm); a culvert within 100 m is overtopped |
| 2 | 0.89 | Wellington Street | Worcester | 0.42 m of water at peak; over 30 cm for 3.0 h; 30 cm reached 8.0 h into the storm; worst hour 25 mm (57% of the storm); water beside the road 0.42 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.9 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 25 mm; catchment 15.1 ha) (P 0.98) |
| 3 | 0.89 | Murray Avenue | Worcester | 0.42 m of water at peak; over 30 cm for 3.0 h; 30 cm reached 8.0 h into the storm; worst hour 26 mm (57% of the storm); water beside the road 0.42 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.9 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 25 mm; catchment 15.1 ha) (P 0.98) |
| 4 | 0.85 | Foster Street | Worcester | 0.41 m of water at peak; over 30 cm for 7.5 h; 30 cm reached 11.0 h into the storm; worst hour 24 mm (56% of the storm); water beside the road 0.34 m below its crest (design freeboard 0.30 m; P 0.40); a culvert within 100 m is overtopped |
| 5 | 0.85 | Foster Street | Worcester | 0.41 m of water at peak; over 30 cm for 7.5 h; 30 cm reached 11.0 h into the storm; worst hour 24 mm (55% of the storm); water beside the road 0.28 m below its crest (design freeboard 0.30 m; P 0.56); a culvert within 100 m is overtopped |
| 6 | 0.74 | Providence Road | Sutton | 0.36 m of water at peak; over 30 cm for 3.5 h; 30 cm reached 8.0 h into the storm; worst hour 21 mm (38% of the storm); a culvert within 100 m is overtopped |
| 7 | 0.72 | Dewey Street | Worcester | 0.36 m of water at peak; over 30 cm for 2.5 h; 30 cm reached 8.0 h into the storm; worst hour 27 mm (58% of the storm); water beside the road 0.27 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.9 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 27 mm; catchment 12.8 ha) (P 0.72) |
| 8 | 0.72 | Parker Street | Worcester | 0.36 m of water at peak; over 30 cm for 2.5 h; 30 cm reached 8.0 h into the storm; worst hour 27 mm (58% of the storm); water beside the road 0.27 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.9 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 27 mm; catchment 12.8 ha) (P 0.72) |
| 9 | 0.56 | Francis J. Mcgrath Boulevard | Worcester | 0.31 m of water at peak; over 30 cm for 1.0 h; 30 cm reached 10.0 h into the storm; worst hour 25 mm (56% of the storm); water beside the road 0.35 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 1.5 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.82); road sag 2.6 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 25 mm; catchment 9.4 ha) (P 1.00) |
| 10 | 0.56 | Hermon Street | Worcester | 0.31 m of water at peak; over 30 cm for 1.0 h; 30 cm reached 10.0 h into the storm; worst hour 25 mm (56% of the storm); water beside the road 0.16 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 0.7 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.21); road sag 2.6 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 25 mm; catchment 9.4 ha) (P 1.00) |
| 11 | 0.55 | Maybrook Place | Worcester | 0.31 m of water at peak; over 30 cm for 1.0 h; 30 cm reached 9.5 h into the storm; worst hour 27 mm (58% of the storm); water beside the road 0.27 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.7 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 27 mm; catchment 61.6 ha) (P 0.81) |
| 12 | 0.53 | James Street | Worcester | 0.31 m of water at peak; over 30 cm for 0.5 h; 30 cm reached 9.5 h into the storm; worst hour 28 mm (57% of the storm); a culvert within 100 m is overtopped |
| 13 | 0.51 | Stafford Street | Worcester | 0.30 m of water at peak; over 30 cm for 0.5 h; 30 cm reached 8.5 h into the storm; worst hour 27 mm (56% of the storm); water beside the road 0.12 m above its crest (design freeboard 0.30 m; P 1.00); a culvert within 100 m is overtopped |
| 14 | 0.51 | Ludlow Street | Worcester | 0.30 m of water at peak; over 30 cm for 0.5 h; 30 cm reached 8.5 h into the storm; worst hour 26 mm (56% of the storm); a culvert within 100 m is overtopped |
| 15 | 0.50 | Jackson Street | Worcester | 0.30 m of water at peak; over 30 cm for 0.5 h; 30 cm reached 10.5 h into the storm; worst hour 25 mm (57% of the storm); water beside the road 0.21 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 1.0 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.53); road sag 3.0 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 25 mm; catchment 9.4 ha) (P 0.75) |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
