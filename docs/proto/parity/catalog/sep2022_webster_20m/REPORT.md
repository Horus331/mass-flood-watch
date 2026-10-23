# Road-closure prototype: sep2022_loss_sep2022_webster_20m

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on CPU (OpenMP)), 20 m grid, storm from 2022-09-05T06:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 2,472 |
| Expected closures (sum of probabilities) | 29.7 |
| Segments with closure probability >= 50% | 15 (9.5 km) |
| Further segments that may close (stream reaches the road crest) | 28 (13.6 km) |
| Culverts overtopped / surcharged | 69 / 0 of 642 |
| Road segments cut off from hospitals | 183 |
| Worst added trip time to a hospital | 29.1 min |
| Heaviest hour of rain | 85.7 mm |
| Flood model run time | 1381 s |

## Checks against what happened

- Storm-day flood reports in the area: 4; water >= 10 cm within 100 m of 50% of them, vs 42% of random points (any day).
- Segments flagged impassable are 1.32x as likely as an average segment to have a report within 200 m.

## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 0.99 | Route 12 | Dudley | 0.56 m of water at peak; over 30 cm for 4.0 h; 30 cm reached 9.5 h into the storm; worst hour 83 mm (81% of the storm); runoff beside / along the road at 1.0 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.29); a culvert within 100 m is overtopped |
| 2 | 0.99 | Mason Road Extension | Dudley | 0.55 m of water at peak; over 30 cm for 3.5 h; 30 cm reached 9.0 h into the storm; worst hour 50 mm (64% of the storm); water beside the road 0.04 m below its crest (design freeboard 0.30 m; P 0.96); a culvert within 100 m is overtopped |
| 3 | 0.99 | (unnamed) | Southbridge | 0.52 m of water at peak; over 30 cm for 12.0 h; 30 cm reached 0.5 h into the storm; worst hour 35 mm (74% of the storm); a culvert within 100 m is overtopped |
| 4 | 0.98 | Village Drive | Southbridge | 0.51 m of water at peak; over 30 cm for 0.5 h; 30 cm reached 0.5 h into the storm; worst hour 33 mm (70% of the storm); a culvert within 100 m is overtopped |
| 5 | 0.98 | Healy Road | Dudley | 0.50 m of water at peak; over 30 cm for 2.0 h; 30 cm reached 9.0 h into the storm; worst hour 54 mm (60% of the storm); a culvert within 100 m is overtopped |
| 6 | 0.92 | Mason Road | Dudley | 0.44 m of water at peak; over 30 cm for 1.5 h; 30 cm reached 9.5 h into the storm; worst hour 78 mm (76% of the storm); a culvert within 100 m is overtopped |
| 7 | 0.85 | Fabyan Road | Dudley | 0.41 m of water at peak; over 30 cm for 1.5 h; 30 cm reached 9.0 h into the storm; worst hour 58 mm (68% of the storm); a culvert within 100 m is overtopped |
| 8 | 0.72 | Fairview Avenue | Dudley | 0.36 m of water at peak; over 30 cm for 1.5 h; 30 cm reached 10.0 h into the storm; worst hour 77 mm (81% of the storm); a culvert within 100 m is overtopped |
| 9 | 0.67 | Route 197 | Dudley | 0.34 m of water at peak; over 30 cm for 1.0 h; 30 cm reached 9.5 h into the storm; worst hour 85 mm (79% of the storm); water beside the road 0.34 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 0.5 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.11); a culvert within 100 m is overtopped |
| 10 | 0.67 | Route 131 | Southbridge | 0.34 m of water at peak; worst hour 34 mm (72% of the storm); a culvert within 100 m is overtopped |
| 11 | 0.66 | (unnamed) | Dudley | 0.34 m of water at peak; over 30 cm for 1.0 h; 30 cm reached 9.5 h into the storm; worst hour 80 mm (77% of the storm); a culvert within 100 m is overtopped |
| 12 | 0.65 | Village Drive | Southbridge | 0.34 m of water at peak; worst hour 33 mm (72% of the storm); a culvert within 100 m is overtopped |
| 13 | 0.62 | Route 131 | Southbridge | 0.33 m of water at peak; worst hour 36 mm (76% of the storm); water beside the road 0.46 m below its crest (design freeboard 0.30 m; P 0.15); a culvert within 100 m is overtopped |
| 14 | 0.58 | (unnamed) | Webster | 0.32 m of water at peak; over 30 cm for 0.5 h; 30 cm reached 9.0 h into the storm; worst hour 75 mm (76% of the storm); water beside the road 0.29 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.6 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 75 mm; catchment 11.3 ha) (P 1.00) |
| 15 | 0.50 | Center Road | Dudley | 0.30 m of water at peak; worst hour 58 mm (64% of the storm); water beside the road 0.37 m below its crest (design freeboard 0.30 m; P 0.31); runoff beside / along the road at 0.5 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.11); a culvert within 100 m is overtopped |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
