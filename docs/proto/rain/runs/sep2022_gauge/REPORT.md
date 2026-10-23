# Road-closure prototype: sep2022_rain_sep2022_gauge

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on CPU (OpenMP)), 20 m grid, storm from 2022-09-05T06:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 2,472 |
| Expected closures (sum of probabilities) | 32.4 |
| Segments with closure probability >= 50% | 17 (10.9 km) |
| Further segments that may close (stream reaches the road crest) | 31 (16.3 km) |
| Culverts overtopped / surcharged | 79 / 0 of 642 |
| Road segments cut off from hospitals | 239 |
| Worst added trip time to a hospital | 18.7 min |
| Heaviest hour of rain | 82.8 mm |
| Flood model run time | 1416 s |

## Checks against what happened

- Storm-day flood reports in the area: 4; water >= 10 cm within 100 m of 75% of them, vs 44% of random points (any day).
- Segments flagged impassable are 1.64x as likely as an average segment to have a report within 200 m.

## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 0.99 | Mason Road Extension | Dudley | 0.54 m of water at peak; over 30 cm for 3.5 h; 30 cm reached 9.0 h into the storm; worst hour 50 mm (64% of the storm); water beside the road 0.04 m below its crest (design freeboard 0.30 m; P 0.96); a culvert within 100 m is overtopped |
| 2 | 0.99 | Route 12 | Dudley | 0.54 m of water at peak; over 30 cm for 4.0 h; 30 cm reached 9.5 h into the storm; worst hour 78 mm (81% of the storm); runoff beside / along the road at 1.0 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.28); a culvert within 100 m is overtopped |
| 3 | 0.99 | (unnamed) | Southbridge | 0.52 m of water at peak; over 30 cm for 13.0 h; 30 cm reached 0.5 h into the storm; worst hour 38 mm (74% of the storm); a culvert within 100 m is overtopped |
| 4 | 0.98 | Village Drive | Southbridge | 0.51 m of water at peak; over 30 cm for 0.5 h; 30 cm reached 0.5 h into the storm; worst hour 34 mm (70% of the storm); a culvert within 100 m is overtopped |
| 5 | 0.98 | Healy Road | Dudley | 0.50 m of water at peak; over 30 cm for 2.0 h; 30 cm reached 9.0 h into the storm; worst hour 50 mm (60% of the storm); a culvert within 100 m is overtopped |
| 6 | 0.89 | Mason Road | Dudley | 0.42 m of water at peak; over 30 cm for 1.5 h; 30 cm reached 9.5 h into the storm; worst hour 72 mm (76% of the storm); a culvert within 100 m is overtopped |
| 7 | 0.83 | Fabyan Road | Dudley | 0.40 m of water at peak; over 30 cm for 1.5 h; 30 cm reached 9.0 h into the storm; worst hour 55 mm (68% of the storm); a culvert within 100 m is overtopped |
| 8 | 0.70 | (unnamed) | Webster | 0.35 m of water at peak; over 30 cm for 1.0 h; 30 cm reached 9.0 h into the storm; worst hour 76 mm (76% of the storm); water beside the road 0.32 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.6 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 76 mm; catchment 11.3 ha) (P 1.00) |
| 9 | 0.68 | (unnamed) | Webster | 0.35 m of water at peak; over 30 cm for 1.0 h; 30 cm reached 9.5 h into the storm; worst hour 76 mm (76% of the storm); a culvert within 100 m is overtopped |
| 10 | 0.67 | Route 131 | Southbridge | 0.34 m of water at peak; worst hour 36 mm (72% of the storm); a culvert within 100 m is overtopped |
| 11 | 0.67 | Fairview Avenue | Dudley | 0.34 m of water at peak; over 30 cm for 1.0 h; 30 cm reached 10.0 h into the storm; worst hour 72 mm (82% of the storm); a culvert within 100 m is overtopped |
| 12 | 0.65 | Village Drive | Southbridge | 0.34 m of water at peak; worst hour 35 mm (72% of the storm); a culvert within 100 m is overtopped |
| 13 | 0.64 | Route 197 | Dudley | 0.34 m of water at peak; over 30 cm for 0.5 h; 30 cm reached 10.0 h into the storm; worst hour 80 mm (80% of the storm); water beside the road 0.33 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 0.7 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.11); a culvert within 100 m is overtopped |
| 14 | 0.62 | Route 12 | Oxford | 0.33 m of water at peak; over 30 cm for 0.5 h; 30 cm reached 10.0 h into the storm; worst hour 72 mm (76% of the storm); water beside the road 0.30 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 0.7 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.25); culvert (Unnamed): headwater 0.97 m vs road crest 1.07 m, 1.3 m3/s |
| 15 | 0.62 | (unnamed) | Dudley | 0.33 m of water at peak; over 30 cm for 0.5 h; 30 cm reached 10.0 h into the storm; worst hour 74 mm (77% of the storm); a culvert within 100 m is overtopped |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
