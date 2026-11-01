# Road-closure prototype: aug2023b_loss_aug2023b_millbury_20m

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on CPU (OpenMP)), 20 m grid, storm from 2023-08-18T05:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 8,013 |
| Expected closures (sum of probabilities) | 21.0 |
| Segments with closure probability >= 50% | 3 (2.0 km) |
| Further segments that may close (stream reaches the road crest) | 10 (6.6 km) |
| Culverts overtopped / surcharged | 26 / 0 of 1291 |
| Road segments cut off from hospitals | 81 |
| Worst added trip time to a hospital | 13.0 min |
| Heaviest hour of rain | 47.2 mm |
| Flood model run time | 1135 s |

## Checks against what happened

- Storm-day flood reports in the area: 0; water >= 10 cm within 100 m of 0% of them, vs 13% of random points (any day).
- MassDOT repeating flood sites in the area: 8; 0 have a segment within 150 m at P >= 0.5 (share of all segments at P >= 0.5: 0.0%).

## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 0.74 | East Park Terrace | Worcester | 0.37 m of water at peak; over 30 cm for 3.5 h; 30 cm reached 15.0 h into the storm; worst hour 22 mm (65% of the storm); water beside the road 0.27 m above its crest (design freeboard 0.30 m; P 1.00); road sag 4.3 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 22 mm; catchment 127.8 ha) (P 0.75) |
| 2 | 0.57 | Millbury Street | Grafton | 0.32 m of water at peak; over 30 cm for 6.0 h; 30 cm reached 9.0 h into the storm; worst hour 37 mm (68% of the storm) |
| 3 | 0.55 | Providence Road | Sutton | 0.31 m of water at peak; over 30 cm for 0.5 h; 30 cm reached 9.0 h into the storm; worst hour 44 mm (76% of the storm); a culvert within 100 m is overtopped |
| 4 | 0.37 | Boston Road | Sutton | 0.27 m of water at peak; worst hour 44 mm (81% of the storm); water beside the road 0.12 m below its crest (design freeboard 0.30 m; P 0.89); runoff beside / along the road at 0.6 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.15) |
| 5 | 0.35 | Stafford Street | Worcester | 0.26 m of water at peak; worst hour 25 mm (82% of the storm); a culvert within 100 m is overtopped |
| 6 | 0.24 | Sycamore Street | Millbury | 0.23 m of water at peak; worst hour 34 mm (69% of the storm); a culvert within 100 m is overtopped |
| 7 | 0.24 | Carleton Road | Millbury | 0.23 m of water at peak; worst hour 31 mm (66% of the storm); a culvert within 100 m is overtopped |
| 8 | 0.21 | Auburn Street | Auburn | 0.22 m of water at peak; worst hour 30 mm (86% of the storm) |
| 9 | 0.20 | Martin Luther King Jr Boulevard | Worcester | 0.21 m of water at peak; worst hour 21 mm (71% of the storm); water beside the road 0.13 m above its crest (design freeboard 0.30 m; P 1.00); road sag 3.2 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 21 mm; catchment 60.2 ha) (P 0.20) |
| 10 | 0.17 | Route 12 | Auburn | 0.20 m of water at peak; worst hour 30 mm (82% of the storm); runoff beside / along the road at 1.5 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.11); a culvert within 100 m is overtopped |
| 11 | 0.16 | Route 12 | Auburn | 0.20 m of water at peak; worst hour 30 mm (85% of the storm) |
| 12 | 0.16 | James Street | Worcester | 0.20 m of water at peak; worst hour 25 mm (83% of the storm); a culvert within 100 m is overtopped |
| 13 | 0.12 | (unnamed) | Sutton | 0.18 m of water at peak; worst hour 44 mm (90% of the storm); a culvert within 100 m is overtopped |
| 14 | 0.10 | Grafton Street | Millbury | 0.17 m of water at peak; worst hour 34 mm (68% of the storm); a culvert within 100 m is overtopped |
| 15 | 0.10 | Hampton Street | Auburn | 0.17 m of water at peak; worst hour 30 mm (82% of the storm); water beside the road 0.42 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 0.7 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.21); a culvert within 100 m is overtopped |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
