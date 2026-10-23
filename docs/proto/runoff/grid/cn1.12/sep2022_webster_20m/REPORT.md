# Road-closure prototype: sep2022_loss_sep2022_webster_20m

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on CPU (OpenMP)), 20 m grid, storm from 2022-09-05T06:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 2,472 |
| Expected closures (sum of probabilities) | 74.2 |
| Segments with closure probability >= 50% | 58 (38.3 km) |
| Further segments that may close (stream reaches the road crest) | 68 (37.1 km) |
| Culverts overtopped / surcharged | 115 / 2 of 642 |
| Road segments cut off from hospitals | 381 |
| Worst added trip time to a hospital | 30.6 min |
| Heaviest hour of rain | 85.7 mm |
| Flood model run time | 914 s |

## Checks against what happened

- Storm-day flood reports in the area: 4; water >= 10 cm within 100 m of 75% of them, vs 54% of random points (any day).
- Segments flagged impassable are 2.28x as likely as an average segment to have a report within 200 m.

## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 1.00 | (unnamed) | Southbridge | 0.83 m of water at peak; over 30 cm for 14.0 h; 30 cm reached 0.5 h into the storm; worst hour 35 mm (74% of the storm); a culvert within 100 m is overtopped |
| 2 | 1.00 | Route 12 | Dudley | 1.14 m of water at peak; over 30 cm for 6.5 h; 30 cm reached 9.0 h into the storm; worst hour 83 mm (81% of the storm); runoff beside / along the road at 1.2 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.58); a culvert within 100 m is overtopped |
| 3 | 1.00 | Healy Road | Dudley | 0.77 m of water at peak; over 30 cm for 9.5 h; 30 cm reached 8.5 h into the storm; worst hour 54 mm (60% of the storm); runoff beside / along the road at 0.9 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.35); a culvert within 100 m is overtopped |
| 4 | 1.00 | Mason Road | Dudley | 0.69 m of water at peak; over 30 cm for 2.0 h; 30 cm reached 9.0 h into the storm; worst hour 78 mm (76% of the storm); a culvert within 100 m is overtopped |
| 5 | 1.00 | Mason Road Extension | Dudley | 0.79 m of water at peak; over 30 cm for 4.0 h; 30 cm reached 9.0 h into the storm; worst hour 50 mm (64% of the storm); water beside the road 0.20 m above its crest (design freeboard 0.30 m; P 1.00); a culvert within 100 m is overtopped |
| 6 | 1.00 | Brookline Street | Webster | 0.66 m of water at peak; over 30 cm for 4.0 h; 30 cm reached 9.0 h into the storm; worst hour 84 mm (82% of the storm); water beside the road 0.48 m above its crest (design freeboard 0.30 m; P 1.00); fast water: depth x speed 0.23 m2/s (small cars unstable from 0.3); road sag 0.3 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 84 mm; catchment 2.9 ha) (P 1.00) |
| 7 | 1.00 | (unnamed) | Webster | 0.67 m of water at peak; over 30 cm for 2.5 h; 30 cm reached 9.0 h into the storm; worst hour 76 mm (77% of the storm); a culvert within 100 m is overtopped |
| 8 | 1.00 | Fairview Avenue | Dudley | 0.71 m of water at peak; over 30 cm for 2.5 h; 30 cm reached 9.0 h into the storm; worst hour 77 mm (81% of the storm); water beside the road 0.40 m above its crest (design freeboard 0.30 m; P 1.00); a culvert within 100 m is overtopped |
| 9 | 1.00 | Fabyan Road | Dudley | 0.66 m of water at peak; over 30 cm for 2.0 h; 30 cm reached 9.0 h into the storm; worst hour 58 mm (68% of the storm); a culvert within 100 m is overtopped |
| 10 | 1.00 | Laurel Hill Road | Southbridge | 0.62 m of water at peak; over 30 cm for 9.5 h; 30 cm reached 9.0 h into the storm; worst hour 34 mm (72% of the storm); a culvert within 100 m is overtopped |
| 11 | 1.00 | Center Road | Dudley | 0.61 m of water at peak; over 30 cm for 1.0 h; 30 cm reached 9.0 h into the storm; worst hour 58 mm (64% of the storm); water beside the road 0.06 m below its crest (design freeboard 0.30 m; P 0.95); runoff beside / along the road at 0.9 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.39); a culvert within 100 m is overtopped |
| 12 | 1.00 | (unnamed) | Southbridge | 0.58 m of water at peak; over 30 cm for 3.5 h; 30 cm reached 9.5 h into the storm; worst hour 35 mm (65% of the storm); runoff beside / along the road at 1.0 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.14); culvert (Unnamed tributary): headwater 2.49 m vs road crest 0.49 m, 0.2 m3/s |
| 13 | 1.00 | Route 12 | Oxford | 0.56 m of water at peak; over 30 cm for 2.0 h; 30 cm reached 9.0 h into the storm; worst hour 70 mm (76% of the storm); water beside the road 0.82 m above its crest (design freeboard 0.30 m; P 1.00); fast water: depth x speed 0.20 m2/s (small cars unstable from 0.3); runoff beside / along the road at 1.0 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.31); culvert (Unnamed): headwater 5.23 m vs road crest 1.07 m, 3.7 m3/s |
| 14 | 1.00 | Dresser Hill Road | Southbridge | 0.56 m of water at peak; over 30 cm for 9.0 h; 30 cm reached 8.5 h into the storm; worst hour 42 mm (81% of the storm); water beside the road 0.20 m below its crest (design freeboard 0.30 m; P 0.74); fast water: depth x speed 0.58 m2/s (small cars unstable from 0.3); runoff beside / along the road at 2.9 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.98); a culvert within 100 m is overtopped |
| 15 | 1.00 | Park Street | Webster | 0.57 m of water at peak; over 30 cm for 1.5 h; 30 cm reached 9.0 h into the storm; worst hour 85 mm (82% of the storm); water beside the road 0.44 m above its crest (design freeboard 0.30 m; P 1.00) |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
