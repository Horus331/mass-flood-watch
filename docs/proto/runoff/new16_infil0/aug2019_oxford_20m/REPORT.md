# Road-closure prototype: aug2019_loss_aug2019_oxford_20m

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on CPU (OpenMP)), 20 m grid, storm from 2019-08-07T19:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 6,290 |
| Expected closures (sum of probabilities) | 43.2 |
| Segments with closure probability >= 50% | 15 (10.9 km) |
| Further segments that may close (stream reaches the road crest) | 53 (27.8 km) |
| Culverts overtopped / surcharged | 84 / 0 of 1136 |
| Road segments cut off from hospitals | 206 |
| Worst added trip time to a hospital | 24.5 min |
| Heaviest hour of rain | 32.7 mm |
| Flood model run time | 1496 s |

## Checks against what happened

- Storm-day flood reports in the area: 3; water >= 10 cm within 100 m of 33% of them, vs 42% of random points (any day).
- Segments flagged impassable are 0.0x as likely as an average segment to have a report within 200 m.
- MassDOT repeating flood sites in the area: 4; 0 have a segment within 150 m at P >= 0.5 (share of all segments at P >= 0.5: 0.2%).

## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 1.00 | Providence Street | Millbury | 0.60 m of water at peak; over 30 cm for 12.0 h; 30 cm reached 6.5 h into the storm; worst hour 19 mm (38% of the storm); a culvert within 100 m is overtopped |
| 2 | 0.97 | Foster Street | Worcester | 0.49 m of water at peak; over 30 cm for 8.5 h; 30 cm reached 10.0 h into the storm; worst hour 24 mm (56% of the storm); water beside the road 0.34 m below its crest (design freeboard 0.30 m; P 0.40); a culvert within 100 m is overtopped |
| 3 | 0.97 | Foster Street | Worcester | 0.49 m of water at peak; over 30 cm for 8.5 h; 30 cm reached 10.0 h into the storm; worst hour 24 mm (55% of the storm); water beside the road 0.28 m below its crest (design freeboard 0.30 m; P 0.56); a culvert within 100 m is overtopped |
| 4 | 0.86 | Providence Road | Sutton | 0.41 m of water at peak; over 30 cm for 9.0 h; 30 cm reached 7.5 h into the storm; worst hour 21 mm (38% of the storm); a culvert within 100 m is overtopped |
| 5 | 0.83 | Wellington Street | Worcester | 0.40 m of water at peak; over 30 cm for 3.0 h; 30 cm reached 8.5 h into the storm; worst hour 25 mm (57% of the storm); water beside the road 0.40 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.9 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 25 mm; catchment 15.1 ha) (P 0.97) |
| 6 | 0.83 | Murray Avenue | Worcester | 0.40 m of water at peak; over 30 cm for 3.0 h; 30 cm reached 8.5 h into the storm; worst hour 26 mm (57% of the storm); water beside the road 0.40 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.9 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 25 mm; catchment 15.1 ha) (P 0.97) |
| 7 | 0.69 | (unnamed) | Oxford | 0.35 m of water at peak; over 30 cm for 1.5 h; 30 cm reached 17.0 h into the storm; worst hour 18 mm (39% of the storm); water beside the road 0.39 m below its crest (design freeboard 0.30 m; P 0.27); a culvert within 100 m is overtopped |
| 8 | 0.66 | James Street | Worcester | 0.34 m of water at peak; over 30 cm for 5.0 h; 30 cm reached 8.5 h into the storm; worst hour 28 mm (57% of the storm); a culvert within 100 m is overtopped |
| 9 | 0.64 | Stafford Street | Worcester | 0.34 m of water at peak; over 30 cm for 5.5 h; 30 cm reached 8.0 h into the storm; worst hour 27 mm (56% of the storm); water beside the road 0.14 m above its crest (design freeboard 0.30 m; P 1.00); a culvert within 100 m is overtopped |
| 10 | 0.64 | Ludlow Street | Worcester | 0.34 m of water at peak; over 30 cm for 5.5 h; 30 cm reached 8.0 h into the storm; worst hour 26 mm (56% of the storm); a culvert within 100 m is overtopped |
| 11 | 0.62 | Auburn Street | Auburn | 0.33 m of water at peak; over 30 cm for 3.5 h; 30 cm reached 15.0 h into the storm; worst hour 30 mm (58% of the storm) |
| 12 | 0.57 | Dewey Street | Worcester | 0.32 m of water at peak; over 30 cm for 2.0 h; 30 cm reached 8.5 h into the storm; worst hour 27 mm (58% of the storm); water beside the road 0.23 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.9 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 27 mm; catchment 12.8 ha) (P 0.58) |
| 13 | 0.57 | Parker Street | Worcester | 0.32 m of water at peak; over 30 cm for 2.0 h; 30 cm reached 8.5 h into the storm; worst hour 27 mm (58% of the storm); water beside the road 0.23 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.9 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 27 mm; catchment 12.8 ha) (P 0.58) |
| 14 | 0.52 | Francis J. Mcgrath Boulevard | Worcester | 0.30 m of water at peak; over 30 cm for 0.5 h; 30 cm reached 10.5 h into the storm; worst hour 25 mm (56% of the storm); water beside the road 0.35 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 1.9 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.91); road sag 2.6 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 25 mm; catchment 9.4 ha) (P 1.00) |
| 15 | 0.52 | Hermon Street | Worcester | 0.30 m of water at peak; over 30 cm for 0.5 h; 30 cm reached 10.5 h into the storm; worst hour 25 mm (56% of the storm); water beside the road 0.15 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 0.7 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.21); road sag 2.6 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 25 mm; catchment 9.4 ha) (P 1.00) |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
