# Road-closure prototype: sep2022_loss_sep2022_webster_20m

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on CPU (OpenMP)), 20 m grid, storm from 2022-09-05T06:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 2,472 |
| Expected closures (sum of probabilities) | 36.1 |
| Segments with closure probability >= 50% | 21 (12.9 km) |
| Further segments that may close (stream reaches the road crest) | 33 (18.3 km) |
| Culverts overtopped / surcharged | 83 / 0 of 642 |
| Road segments cut off from hospitals | 254 |
| Worst added trip time to a hospital | 19.1 min |
| Heaviest hour of rain | 85.7 mm |
| Flood model run time | 1230 s |

## Checks against what happened

- Storm-day flood reports in the area: 4; water >= 10 cm within 100 m of 75% of them, vs 44% of random points (any day).
- Segments flagged impassable are 1.53x as likely as an average segment to have a report within 200 m.

## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 1.00 | Route 12 | Dudley | 0.63 m of water at peak; over 30 cm for 4.5 h; 30 cm reached 9.5 h into the storm; worst hour 83 mm (81% of the storm); runoff beside / along the road at 1.0 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.32); a culvert within 100 m is overtopped |
| 2 | 1.00 | Mason Road Extension | Dudley | 0.59 m of water at peak; over 30 cm for 3.5 h; 30 cm reached 9.0 h into the storm; worst hour 50 mm (64% of the storm); water beside the road 0.01 m above its crest (design freeboard 0.30 m; P 0.98); a culvert within 100 m is overtopped |
| 3 | 0.99 | Healy Road | Dudley | 0.54 m of water at peak; over 30 cm for 2.0 h; 30 cm reached 9.0 h into the storm; worst hour 54 mm (60% of the storm); runoff beside / along the road at 0.5 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.13); a culvert within 100 m is overtopped |
| 4 | 0.99 | (unnamed) | Southbridge | 0.53 m of water at peak; over 30 cm for 14.0 h; 30 cm reached 0.5 h into the storm; worst hour 35 mm (74% of the storm); a culvert within 100 m is overtopped |
| 5 | 0.98 | Village Drive | Southbridge | 0.51 m of water at peak; over 30 cm for 0.5 h; 30 cm reached 0.5 h into the storm; worst hour 33 mm (70% of the storm); a culvert within 100 m is overtopped |
| 6 | 0.95 | Mason Road | Dudley | 0.47 m of water at peak; over 30 cm for 1.5 h; 30 cm reached 9.5 h into the storm; worst hour 78 mm (76% of the storm); a culvert within 100 m is overtopped |
| 7 | 0.92 | Fabyan Road | Dudley | 0.44 m of water at peak; over 30 cm for 1.5 h; 30 cm reached 9.0 h into the storm; worst hour 58 mm (68% of the storm); a culvert within 100 m is overtopped |
| 8 | 0.84 | Fairview Avenue | Dudley | 0.40 m of water at peak; over 30 cm for 1.5 h; 30 cm reached 10.0 h into the storm; worst hour 77 mm (81% of the storm); runoff beside / along the road at 0.6 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.11); a culvert within 100 m is overtopped |
| 9 | 0.75 | Route 197 | Dudley | 0.37 m of water at peak; over 30 cm for 1.0 h; 30 cm reached 9.5 h into the storm; worst hour 85 mm (79% of the storm); water beside the road 0.37 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 0.6 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.11); a culvert within 100 m is overtopped |
| 10 | 0.73 | (unnamed) | Dudley | 0.36 m of water at peak; over 30 cm for 1.0 h; 30 cm reached 9.5 h into the storm; worst hour 80 mm (77% of the storm); a culvert within 100 m is overtopped |
| 11 | 0.67 | (unnamed) | Webster | 0.34 m of water at peak; over 30 cm for 1.0 h; 30 cm reached 10.0 h into the storm; worst hour 76 mm (77% of the storm); a culvert within 100 m is overtopped |
| 12 | 0.67 | Route 131 | Southbridge | 0.34 m of water at peak; worst hour 34 mm (72% of the storm); a culvert within 100 m is overtopped |
| 13 | 0.67 | Dresser Hill Road | Southbridge | 0.34 m of water at peak; over 30 cm for 2.5 h; 30 cm reached 10.0 h into the storm; worst hour 42 mm (81% of the storm); water beside the road 0.37 m below its crest (design freeboard 0.30 m; P 0.31); fast water: depth x speed 0.22 m2/s (small cars unstable from 0.3); runoff beside / along the road at 2.9 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.96); a culvert within 100 m is overtopped |
| 14 | 0.66 | Center Road | Dudley | 0.34 m of water at peak; over 30 cm for 1.0 h; 30 cm reached 9.0 h into the storm; worst hour 58 mm (64% of the storm); water beside the road 0.33 m below its crest (design freeboard 0.30 m; P 0.41); runoff beside / along the road at 0.8 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.27); a culvert within 100 m is overtopped |
| 15 | 0.66 | (unnamed) | Southbridge | 0.34 m of water at peak; over 30 cm for 2.5 h; 30 cm reached 10.0 h into the storm; worst hour 42 mm (81% of the storm); a culvert within 100 m is overtopped |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
