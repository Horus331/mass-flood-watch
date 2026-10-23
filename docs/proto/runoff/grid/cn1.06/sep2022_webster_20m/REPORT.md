# Road-closure prototype: sep2022_loss_sep2022_webster_20m

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on CPU (OpenMP)), 20 m grid, storm from 2022-09-05T06:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 2,472 |
| Expected closures (sum of probabilities) | 60.8 |
| Segments with closure probability >= 50% | 44 (28.0 km) |
| Further segments that may close (stream reaches the road crest) | 66 (36.2 km) |
| Culverts overtopped / surcharged | 104 / 0 of 642 |
| Road segments cut off from hospitals | 347 |
| Worst added trip time to a hospital | 29.9 min |
| Heaviest hour of rain | 85.7 mm |
| Flood model run time | 1031 s |

## Checks against what happened

- Storm-day flood reports in the area: 4; water >= 10 cm within 100 m of 75% of them, vs 51% of random points (any day).
- Segments flagged impassable are 1.88x as likely as an average segment to have a report within 200 m.

## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 1.00 | (unnamed) | Southbridge | 0.68 m of water at peak; over 30 cm for 14.0 h; 30 cm reached 0.5 h into the storm; worst hour 35 mm (74% of the storm); a culvert within 100 m is overtopped |
| 2 | 1.00 | Route 12 | Dudley | 0.99 m of water at peak; over 30 cm for 5.5 h; 30 cm reached 9.0 h into the storm; worst hour 83 mm (81% of the storm); runoff beside / along the road at 1.2 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.58); a culvert within 100 m is overtopped |
| 3 | 1.00 | Mason Road | Dudley | 0.63 m of water at peak; over 30 cm for 2.0 h; 30 cm reached 9.0 h into the storm; worst hour 78 mm (76% of the storm); a culvert within 100 m is overtopped |
| 4 | 1.00 | Mason Road Extension | Dudley | 0.72 m of water at peak; over 30 cm for 4.0 h; 30 cm reached 9.0 h into the storm; worst hour 50 mm (64% of the storm); water beside the road 0.14 m above its crest (design freeboard 0.30 m; P 1.00); a culvert within 100 m is overtopped |
| 5 | 1.00 | Healy Road | Dudley | 0.70 m of water at peak; over 30 cm for 2.5 h; 30 cm reached 8.5 h into the storm; worst hour 54 mm (60% of the storm); runoff beside / along the road at 0.7 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.28); a culvert within 100 m is overtopped |
| 6 | 1.00 | Fairview Avenue | Dudley | 0.62 m of water at peak; over 30 cm for 2.0 h; 30 cm reached 9.5 h into the storm; worst hour 77 mm (81% of the storm); water beside the road 0.38 m above its crest (design freeboard 0.30 m; P 1.00); a culvert within 100 m is overtopped |
| 7 | 1.00 | Fabyan Road | Dudley | 0.61 m of water at peak; over 30 cm for 1.5 h; 30 cm reached 9.0 h into the storm; worst hour 58 mm (68% of the storm); a culvert within 100 m is overtopped |
| 8 | 1.00 | (unnamed) | Webster | 0.59 m of water at peak; over 30 cm for 2.5 h; 30 cm reached 9.0 h into the storm; worst hour 76 mm (77% of the storm); a culvert within 100 m is overtopped |
| 9 | 1.00 | Brookline Street | Webster | 0.56 m of water at peak; over 30 cm for 4.0 h; 30 cm reached 9.0 h into the storm; worst hour 84 mm (82% of the storm); water beside the road 0.38 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.3 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 84 mm; catchment 2.9 ha) (P 1.00) |
| 10 | 0.99 | Center Road | Dudley | 0.54 m of water at peak; over 30 cm for 1.0 h; 30 cm reached 9.0 h into the storm; worst hour 58 mm (64% of the storm); water beside the road 0.13 m below its crest (design freeboard 0.30 m; P 0.87); runoff beside / along the road at 0.7 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.28); a culvert within 100 m is overtopped |
| 11 | 0.98 | Village Drive | Southbridge | 0.51 m of water at peak; over 30 cm for 0.5 h; 30 cm reached 0.5 h into the storm; worst hour 33 mm (70% of the storm); a culvert within 100 m is overtopped |
| 12 | 0.98 | Route 12 | Oxford | 0.50 m of water at peak; over 30 cm for 2.0 h; 30 cm reached 9.0 h into the storm; worst hour 70 mm (76% of the storm); water beside the road 0.81 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 1.0 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.25); culvert (Unnamed): headwater 3.78 m vs road crest 1.07 m, 3.1 m3/s |
| 13 | 0.96 | Route 197 | Dudley | 0.48 m of water at peak; over 30 cm for 2.0 h; 30 cm reached 9.0 h into the storm; worst hour 85 mm (79% of the storm); water beside the road 0.49 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 0.8 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.26); a culvert within 100 m is overtopped |
| 14 | 0.96 | Dresser Hill Road | Southbridge | 0.47 m of water at peak; over 30 cm for 7.0 h; 30 cm reached 9.0 h into the storm; worst hour 42 mm (81% of the storm); water beside the road 0.28 m below its crest (design freeboard 0.30 m; P 0.56); fast water: depth x speed 0.42 m2/s (small cars unstable from 0.3); runoff beside / along the road at 2.9 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.98); a culvert within 100 m is overtopped |
| 15 | 0.96 | (unnamed) | Southbridge | 0.47 m of water at peak; over 30 cm for 7.0 h; 30 cm reached 9.0 h into the storm; worst hour 42 mm (81% of the storm); a culvert within 100 m is overtopped |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
