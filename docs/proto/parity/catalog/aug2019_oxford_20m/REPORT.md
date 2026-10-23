# Road-closure prototype: aug2019_loss_aug2019_oxford_20m

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on CPU (OpenMP)), 20 m grid, storm from 2019-08-07T19:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 6,290 |
| Expected closures (sum of probabilities) | 24.2 |
| Segments with closure probability >= 50% | 2 (2.0 km) |
| Further segments that may close (stream reaches the road crest) | 26 (15.3 km) |
| Culverts overtopped / surcharged | 43 / 0 of 1136 |
| Road segments cut off from hospitals | 104 |
| Worst added trip time to a hospital | 17.7 min |
| Heaviest hour of rain | 32.7 mm |
| Flood model run time | 1037 s |

## Checks against what happened

- Storm-day flood reports in the area: 3; water >= 10 cm within 100 m of 33% of them, vs 27% of random points (any day).
- Segments flagged impassable are 0.0x as likely as an average segment to have a report within 200 m.
- MassDOT repeating flood sites in the area: 4; 0 have a segment within 150 m at P >= 0.5 (share of all segments at P >= 0.5: 0.0%).

## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 0.95 | Providence Street | Millbury | 0.47 m of water at peak; over 30 cm for 11.5 h; 30 cm reached 7.0 h into the storm; worst hour 19 mm (38% of the storm); a culvert within 100 m is overtopped |
| 2 | 0.65 | Providence Road | Sutton | 0.34 m of water at peak; over 30 cm for 2.5 h; 30 cm reached 8.0 h into the storm; worst hour 21 mm (38% of the storm); a culvert within 100 m is overtopped |
| 3 | 0.43 | Stafford Street | Worcester | 0.28 m of water at peak; worst hour 27 mm (56% of the storm); water beside the road 0.11 m above its crest (design freeboard 0.30 m; P 1.00); a culvert within 100 m is overtopped |
| 4 | 0.43 | Ludlow Street | Worcester | 0.28 m of water at peak; worst hour 26 mm (56% of the storm); a culvert within 100 m is overtopped |
| 5 | 0.40 | James Street | Worcester | 0.28 m of water at peak; worst hour 28 mm (57% of the storm); a culvert within 100 m is overtopped |
| 6 | 0.40 | Foster Street | Worcester | 0.27 m of water at peak; worst hour 24 mm (56% of the storm); water beside the road 0.34 m below its crest (design freeboard 0.30 m; P 0.40); a culvert within 100 m is overtopped |
| 7 | 0.40 | Foster Street | Worcester | 0.27 m of water at peak; worst hour 24 mm (55% of the storm); water beside the road 0.28 m below its crest (design freeboard 0.30 m; P 0.56); a culvert within 100 m is overtopped |
| 8 | 0.34 | Wellington Street | Worcester | 0.26 m of water at peak; worst hour 25 mm (57% of the storm); water beside the road 0.20 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.9 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 25 mm; catchment 15.1 ha) (P 0.90) |
| 9 | 0.34 | Murray Avenue | Worcester | 0.26 m of water at peak; worst hour 26 mm (57% of the storm); water beside the road 0.25 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.9 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 25 mm; catchment 15.1 ha) (P 0.90) |
| 10 | 0.26 | Dewey Street | Worcester | 0.24 m of water at peak; worst hour 27 mm (58% of the storm); water beside the road 0.15 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.9 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 27 mm; catchment 12.8 ha) (P 0.27) |
| 11 | 0.26 | Parker Street | Worcester | 0.24 m of water at peak; worst hour 27 mm (58% of the storm); water beside the road 0.15 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.9 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 27 mm; catchment 12.8 ha) (P 0.27) |
| 12 | 0.22 | Carleton Road | Millbury | 0.22 m of water at peak; worst hour 19 mm (42% of the storm); a culvert within 100 m is overtopped |
| 13 | 0.22 | Mccarthy Avenue | Leicester | 0.22 m of water at peak; worst hour 26 mm (57% of the storm); road sag 0.4 m deep (underpass, drains sized for the 50-yr hour, 58 mm; peak hour here 25 mm; catchment 10.5 ha) (P 0.12); a culvert within 100 m is overtopped |
| 14 | 0.22 | Mccarthy Avenue | Leicester | 0.22 m of water at peak; worst hour 25 mm (58% of the storm); a culvert within 100 m is overtopped |
| 15 | 0.20 | Sycamore Street | Millbury | 0.22 m of water at peak; worst hour 17 mm (37% of the storm); a culvert within 100 m is overtopped |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
