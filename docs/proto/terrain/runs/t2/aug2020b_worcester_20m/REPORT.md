# Road-closure prototype: aug2020b_loss_aug2020b_worcester_20m

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on CPU (OpenMP)), 20 m grid, storm from 2020-08-27T11:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 8,807 |
| Expected closures (sum of probabilities) | 15.3 |
| Segments with closure probability >= 50% | 0 (0.0 km) |
| Further segments that may close (stream reaches the road crest) | 4 (1.5 km) |
| Culverts overtopped / surcharged | 8 / 0 of 1326 |
| Road segments cut off from hospitals | 22 |
| Worst added trip time to a hospital | 11.9 min |
| Heaviest hour of rain | 17.8 mm |
| Flood model run time | 1253 s |

## Checks against what happened

- Storm-day flood reports in the area: 0; water >= 10 cm within 100 m of 0% of them, vs 10% of random points (any day).
- MassDOT repeating flood sites in the area: 9; 0 have a segment within 150 m at P >= 0.5 (share of all segments at P >= 0.5: 0.0%).

## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 0.35 | Stafford Street | Worcester | 0.26 m of water at peak; worst hour 12 mm (62% of the storm); a culvert within 100 m is overtopped |
| 2 | 0.31 | Millbury Street | Grafton | 0.25 m of water at peak; worst hour 10 mm (64% of the storm) |
| 3 | 0.17 | Route 12 | Auburn | 0.20 m of water at peak; worst hour 15 mm (66% of the storm); a culvert within 100 m is overtopped |
| 4 | 0.16 | James Street | Worcester | 0.20 m of water at peak; worst hour 12 mm (61% of the storm); a culvert within 100 m is overtopped |
| 5 | 0.10 | Hampton Street | Auburn | 0.17 m of water at peak; worst hour 16 mm (66% of the storm); water beside the road 0.42 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 0.7 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.21); a culvert within 100 m is overtopped |
| 6 | 0.10 | Martin Luther King Jr Boulevard | Worcester | 0.17 m of water at peak; worst hour 12 mm (70% of the storm); water beside the road 0.09 m above its crest (design freeboard 0.30 m; P 0.99) |
| 7 | 0.05 | Providence Road | Sutton | 0.14 m of water at peak; worst hour 10 mm (60% of the storm) |
| 8 | 0.05 | Auburn Street | Auburn | 0.13 m of water at peak; worst hour 11 mm (58% of the storm) |
| 9 | 0.05 | Dawson Road | Worcester | 0.13 m of water at peak; worst hour 12 mm (59% of the storm) |
| 10 | 0.04 | Washington Street | Worcester | 0.13 m of water at peak; worst hour 14 mm (71% of the storm); water beside the road 0.21 m below its crest (design freeboard 0.30 m; P 0.74) |
| 11 | 0.04 | Rockland Road | Auburn | 0.12 m of water at peak; worst hour 13 mm (62% of the storm) |
| 12 | 0.03 | Auburn Street | Leicester | 0.12 m of water at peak; worst hour 11 mm (60% of the storm) |
| 13 | 0.03 | Route 12 | Auburn | 0.11 m of water at peak; worst hour 12 mm (63% of the storm) |
| 14 | 0.03 | Pakachoag Street | Auburn | 0.11 m of water at peak; worst hour 15 mm (67% of the storm) |
| 15 | 0.03 | Cambridge Street | Worcester | 0.11 m of water at peak; worst hour 14 mm (70% of the storm); water beside the road 0.04 m below its crest (design freeboard 0.30 m; P 0.96) |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
