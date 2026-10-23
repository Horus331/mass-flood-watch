# Road-closure prototype: sep2022_loss_sep2022_webster_20m

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on CPU (OpenMP)), 20 m grid, storm from 2022-09-05T06:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 2,472 |
| Expected closures (sum of probabilities) | 18.4 |
| Segments with closure probability >= 50% | 8 (4.4 km) |
| Further segments that may close (stream reaches the road crest) | 8 (3.6 km) |
| Culverts overtopped / surcharged | 47 / 0 of 642 |
| Road segments cut off from hospitals | 110 |
| Worst added trip time to a hospital | 25.2 min |
| Heaviest hour of rain | 85.7 mm |
| Flood model run time | 1308 s |

## Checks against what happened

- Storm-day flood reports in the area: 4; water >= 10 cm within 100 m of 25% of them, vs 26% of random points (any day).
- Segments flagged impassable are 0.0x as likely as an average segment to have a report within 200 m.

## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 0.99 | (unnamed) | Southbridge | 0.52 m of water at peak; over 30 cm for 11.5 h; 30 cm reached 0.5 h into the storm; worst hour 35 mm (74% of the storm); a culvert within 100 m is overtopped |
| 2 | 0.98 | Village Drive | Southbridge | 0.51 m of water at peak; over 30 cm for 0.5 h; 30 cm reached 0.5 h into the storm; worst hour 33 mm (70% of the storm); a culvert within 100 m is overtopped |
| 3 | 0.82 | Mason Road Extension | Dudley | 0.39 m of water at peak; over 30 cm for 2.5 h; 30 cm reached 9.5 h into the storm; worst hour 50 mm (64% of the storm); water beside the road 0.20 m below its crest (design freeboard 0.30 m; P 0.74); a culvert within 100 m is overtopped |
| 4 | 0.69 | Healy Road | Dudley | 0.35 m of water at peak; over 30 cm for 1.0 h; 30 cm reached 9.0 h into the storm; worst hour 54 mm (60% of the storm); a culvert within 100 m is overtopped |
| 5 | 0.67 | Route 131 | Southbridge | 0.34 m of water at peak; worst hour 34 mm (72% of the storm); a culvert within 100 m is overtopped |
| 6 | 0.65 | Village Drive | Southbridge | 0.34 m of water at peak; worst hour 33 mm (72% of the storm); a culvert within 100 m is overtopped |
| 7 | 0.62 | Route 131 | Southbridge | 0.33 m of water at peak; worst hour 36 mm (76% of the storm); water beside the road 0.46 m below its crest (design freeboard 0.30 m; P 0.15); a culvert within 100 m is overtopped |
| 8 | 0.57 | Fabyan Road | Dudley | 0.32 m of water at peak; over 30 cm for 0.5 h; 30 cm reached 9.0 h into the storm; worst hour 58 mm (68% of the storm); a culvert within 100 m is overtopped |
| 9 | 0.34 | Henry Street | Southbridge | 0.26 m of water at peak; worst hour 35 mm (75% of the storm); a culvert within 100 m is overtopped |
| 10 | 0.34 | Worcester Street | Southbridge | 0.26 m of water at peak; worst hour 36 mm (75% of the storm); water beside the road 0.27 m below its crest (design freeboard 0.30 m; P 0.57); a culvert within 100 m is overtopped |
| 11 | 0.30 | Dresser Hill Road | Southbridge | 0.25 m of water at peak; worst hour 42 mm (81% of the storm); water beside the road 0.42 m below its crest (design freeboard 0.30 m; P 0.21); runoff beside / along the road at 2.9 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.74); a culvert within 100 m is overtopped |
| 12 | 0.30 | (unnamed) | Southbridge | 0.25 m of water at peak; worst hour 42 mm (81% of the storm); a culvert within 100 m is overtopped |
| 13 | 0.29 | Hayden Pond Road | Dudley | 0.24 m of water at peak; worst hour 50 mm (64% of the storm); a culvert within 100 m is overtopped |
| 14 | 0.27 | New Boston Road | Dudley | 0.24 m of water at peak; worst hour 71 mm (83% of the storm); a culvert within 100 m is overtopped |
| 15 | 0.25 | Old Southbridge Road | Dudley | 0.23 m of water at peak; worst hour 41 mm (53% of the storm); a culvert within 100 m is overtopped |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
