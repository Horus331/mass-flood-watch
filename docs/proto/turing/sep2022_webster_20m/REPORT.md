# Road-closure prototype: sep2022_proto_sep2022_webster_20m

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on GPU (cuda)), 20 m grid, storm from 2022-09-05T06:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 2,408 |
| Expected closures (sum of probabilities) | 65.0 |
| Segments with closure probability >= 50% | 45 (31.1 km) |
| Further segments that may close (stream reaches the road crest) | 48 (27.4 km) |
| Culverts overtopped / surcharged | 111 / 1 of 642 |
| Road segments cut off from hospitals | 368 |
| Worst added trip time to a hospital | 22.4 min |
| Heaviest hour of rain | 85.7 mm |
| Flood model run time | 36 s |

## Checks against what happened

- Storm-day flood reports in the area: 4; water >= 10 cm within 100 m of 75% of them, vs 51% of random points (any day).
- Segments flagged impassable are 1.19x as likely as an average segment to have a report within 200 m.

## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 1.00 | (unnamed) | Southbridge | 1.82 m of water at peak; over 30 cm for 18.0 h; 30 cm reached 0.5 h into the storm; worst hour 35 mm (74% of the storm); a culvert within 100 m is overtopped |
| 2 | 1.00 | Route 12 | Dudley | 0.72 m of water at peak; over 30 cm for 5.0 h; 30 cm reached 9.0 h into the storm; worst hour 83 mm (81% of the storm); a culvert within 100 m is overtopped |
| 3 | 1.00 | Dresser Hill Road | Southbridge | 1.14 m of water at peak; over 30 cm for 5.0 h; 30 cm reached 0.5 h into the storm; worst hour 42 mm (81% of the storm); water beside the road 1.17 m above its crest (design freeboard 0.30 m; P 1.00); a culvert within 100 m is overtopped |
| 4 | 1.00 | Village Drive | Southbridge | 1.26 m of water at peak; over 30 cm for 7.5 h; 30 cm reached 0.0 h into the storm; worst hour 33 mm (70% of the storm); a culvert within 100 m is overtopped |
| 5 | 1.00 | Route 131 | Southbridge | 1.84 m of water at peak; over 30 cm for 0.5 h; 30 cm reached 0.0 h into the storm; worst hour 36 mm (76% of the storm); water beside the road 1.76 m above its crest (design freeboard 0.30 m; P 1.00); a culvert within 100 m is overtopped |
| 6 | 1.00 | Route 131 | Southbridge | 1.27 m of water at peak; over 30 cm for 0.5 h; 30 cm reached 0.5 h into the storm; worst hour 34 mm (72% of the storm); a culvert within 100 m is overtopped |
| 7 | 1.00 | (unnamed) | Southbridge | 0.65 m of water at peak; over 30 cm for 5.0 h; 30 cm reached 0.5 h into the storm; worst hour 42 mm (81% of the storm); a culvert within 100 m is overtopped |
| 8 | 1.00 | Route 169 | Charlton | 0.81 m of water at peak; over 30 cm for 0.5 h; 30 cm reached 0.5 h into the storm; worst hour 33 mm (68% of the storm); a culvert within 100 m is overtopped |
| 9 | 1.00 | (unnamed) | Southbridge | 1.42 m of water at peak; over 30 cm for 3.0 h; 30 cm reached 0.5 h into the storm; worst hour 35 mm (65% of the storm); culvert (Unnamed tributary): headwater 102.70 m vs road crest 0.49 m, 1.3 m3/s |
| 10 | 1.00 | Village Drive | Southbridge | 1.25 m of water at peak; over 30 cm for 0.5 h; 30 cm reached 0.5 h into the storm; worst hour 33 mm (72% of the storm); a culvert within 100 m is overtopped |
| 11 | 1.00 | Potter Village Road | Charlton | 2.19 m of water at peak; over 30 cm for 0.5 h; 30 cm reached 0.5 h into the storm; worst hour 28 mm (59% of the storm); water beside the road 0.76 m above its crest (design freeboard 0.30 m; P 1.00); a culvert within 100 m is overtopped |
| 12 | 1.00 | (unnamed) | Southbridge | 2.19 m of water at peak; worst hour 35 mm (74% of the storm); water beside the road 2.54 m above its crest (design freeboard 0.30 m; P 1.00) |
| 13 | 1.00 | Dudley Southbridge Road |  | 0.71 m of water at peak; worst hour 36 mm (69% of the storm); a culvert within 100 m is overtopped |
| 14 | 1.00 | Mason Road Extension | Dudley | 0.62 m of water at peak; over 30 cm for 3.5 h; 30 cm reached 9.0 h into the storm; worst hour 50 mm (64% of the storm); water beside the road 0.03 m above its crest (design freeboard 0.30 m; P 0.99); a culvert within 100 m is overtopped |
| 15 | 1.00 | (unnamed) | Southbridge | 0.61 m of water at peak; over 30 cm for 0.5 h; 30 cm reached 0.5 h into the storm; worst hour 39 mm (79% of the storm); a culvert within 100 m is overtopped |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
