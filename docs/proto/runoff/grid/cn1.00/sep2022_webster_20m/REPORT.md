# Road-closure prototype: sep2022_loss_sep2022_webster_20m

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on CPU (OpenMP)), 20 m grid, storm from 2022-09-05T06:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 2,472 |
| Expected closures (sum of probabilities) | 47.5 |
| Segments with closure probability >= 50% | 27 (17.2 km) |
| Further segments that may close (stream reaches the road crest) | 54 (30.0 km) |
| Culverts overtopped / surcharged | 88 / 0 of 642 |
| Road segments cut off from hospitals | 266 |
| Worst added trip time to a hospital | 22.8 min |
| Heaviest hour of rain | 85.7 mm |
| Flood model run time | 1450 s |

## Checks against what happened

- Storm-day flood reports in the area: 4; water >= 10 cm within 100 m of 75% of them, vs 49% of random points (any day).
- Segments flagged impassable are 1.78x as likely as an average segment to have a report within 200 m.

## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 1.00 | Route 12 | Dudley | 0.83 m of water at peak; over 30 cm for 5.0 h; 30 cm reached 9.0 h into the storm; worst hour 83 mm (81% of the storm); runoff beside / along the road at 1.0 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.46); a culvert within 100 m is overtopped |
| 2 | 1.00 | Mason Road Extension | Dudley | 0.66 m of water at peak; over 30 cm for 3.5 h; 30 cm reached 9.0 h into the storm; worst hour 50 mm (64% of the storm); water beside the road 0.08 m above its crest (design freeboard 0.30 m; P 0.99); a culvert within 100 m is overtopped |
| 3 | 1.00 | Healy Road | Dudley | 0.64 m of water at peak; over 30 cm for 2.5 h; 30 cm reached 8.5 h into the storm; worst hour 54 mm (60% of the storm); runoff beside / along the road at 0.6 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.22); a culvert within 100 m is overtopped |
| 4 | 1.00 | Mason Road | Dudley | 0.57 m of water at peak; over 30 cm for 2.0 h; 30 cm reached 9.0 h into the storm; worst hour 78 mm (76% of the storm); a culvert within 100 m is overtopped |
| 5 | 0.99 | Fabyan Road | Dudley | 0.55 m of water at peak; over 30 cm for 1.5 h; 30 cm reached 9.0 h into the storm; worst hour 58 mm (68% of the storm); a culvert within 100 m is overtopped |
| 6 | 0.99 | (unnamed) | Southbridge | 0.54 m of water at peak; over 30 cm for 13.5 h; 30 cm reached 0.5 h into the storm; worst hour 35 mm (74% of the storm); a culvert within 100 m is overtopped |
| 7 | 0.99 | Fairview Avenue | Dudley | 0.53 m of water at peak; over 30 cm for 2.0 h; 30 cm reached 9.5 h into the storm; worst hour 77 mm (81% of the storm); water beside the road 0.29 m below its crest (design freeboard 0.30 m; P 0.53); a culvert within 100 m is overtopped |
| 8 | 0.98 | Village Drive | Southbridge | 0.51 m of water at peak; over 30 cm for 0.5 h; 30 cm reached 0.5 h into the storm; worst hour 33 mm (70% of the storm); a culvert within 100 m is overtopped |
| 9 | 0.97 | (unnamed) | Webster | 0.49 m of water at peak; over 30 cm for 1.5 h; 30 cm reached 9.5 h into the storm; worst hour 76 mm (77% of the storm); a culvert within 100 m is overtopped |
| 10 | 0.95 | Center Road | Dudley | 0.46 m of water at peak; over 30 cm for 1.0 h; 30 cm reached 9.0 h into the storm; worst hour 58 mm (64% of the storm); water beside the road 0.21 m below its crest (design freeboard 0.30 m; P 0.73); runoff beside / along the road at 0.7 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.25); a culvert within 100 m is overtopped |
| 11 | 0.95 | Brookline Street | Webster | 0.46 m of water at peak; over 30 cm for 3.5 h; 30 cm reached 9.0 h into the storm; worst hour 84 mm (82% of the storm); water beside the road 0.28 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.3 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 84 mm; catchment 2.9 ha) (P 1.00) |
| 12 | 0.92 | Route 197 | Dudley | 0.44 m of water at peak; over 30 cm for 1.0 h; 30 cm reached 9.5 h into the storm; worst hour 85 mm (79% of the storm); water beside the road 0.45 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 0.8 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.19); a culvert within 100 m is overtopped |
| 13 | 0.90 | Route 12 | Oxford | 0.43 m of water at peak; over 30 cm for 1.5 h; 30 cm reached 9.5 h into the storm; worst hour 70 mm (76% of the storm); water beside the road 0.40 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 0.7 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.25); culvert (Unnamed): headwater 2.26 m vs road crest 1.07 m, 2.3 m3/s |
| 14 | 0.90 | (unnamed) | Dudley | 0.43 m of water at peak; over 30 cm for 1.0 h; 30 cm reached 9.5 h into the storm; worst hour 80 mm (77% of the storm); a culvert within 100 m is overtopped |
| 15 | 0.90 | (unnamed) | Webster | 0.43 m of water at peak; over 30 cm for 1.0 h; 30 cm reached 9.0 h into the storm; worst hour 75 mm (76% of the storm); water beside the road 0.39 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.6 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 75 mm; catchment 11.3 ha) (P 1.00) |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
