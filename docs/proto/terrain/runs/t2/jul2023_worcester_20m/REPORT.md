# Road-closure prototype: jul2023_loss_jul2023_worcester_20m

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on CPU (OpenMP)), 20 m grid, storm from 2023-07-14T08:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 6,775 |
| Expected closures (sum of probabilities) | 13.3 |
| Segments with closure probability >= 50% | 0 (0.0 km) |
| Further segments that may close (stream reaches the road crest) | 7 (3.4 km) |
| Culverts overtopped / surcharged | 13 / 0 of 1023 |
| Road segments cut off from hospitals | 18 |
| Worst added trip time to a hospital | 12.8 min |
| Heaviest hour of rain | 25.9 mm |
| Flood model run time | 1260 s |

## Checks against what happened

- Storm-day flood reports in the area: 3; water >= 10 cm within 100 m of 0% of them, vs 12% of random points (any day).
- Segments flagged impassable are 0.0x as likely as an average segment to have a report within 200 m.
- MassDOT repeating flood sites in the area: 7; 0 have a segment within 150 m at P >= 0.5 (share of all segments at P >= 0.5: 0.0%).

## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 0.35 | Stafford Street | Worcester | 0.26 m of water at peak; worst hour 20 mm (89% of the storm); a culvert within 100 m is overtopped |
| 2 | 0.17 | Martin Luther King Jr Boulevard | Worcester | 0.20 m of water at peak; worst hour 21 mm (82% of the storm); water beside the road 0.12 m above its crest (design freeboard 0.30 m; P 1.00); road sag 3.2 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 21 mm; catchment 60.2 ha) (P 0.17) |
| 3 | 0.17 | Route 12 | Auburn | 0.20 m of water at peak; worst hour 17 mm (82% of the storm); runoff beside / along the road at 1.3 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.12); a culvert within 100 m is overtopped |
| 4 | 0.17 | Wire Village Road | Spencer | 0.20 m of water at peak; worst hour 24 mm (78% of the storm); a culvert within 100 m is overtopped |
| 5 | 0.16 | James Street | Worcester | 0.20 m of water at peak; worst hour 21 mm (89% of the storm); a culvert within 100 m is overtopped |
| 6 | 0.13 | Hastings Road | Spencer | 0.19 m of water at peak; worst hour 23 mm (76% of the storm); a culvert within 100 m is overtopped |
| 7 | 0.11 | (unnamed) | Spencer | 0.17 m of water at peak; worst hour 19 mm (68% of the storm) |
| 8 | 0.10 | Hampton Street | Auburn | 0.17 m of water at peak; worst hour 17 mm (82% of the storm); water beside the road 0.42 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 0.7 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.21); a culvert within 100 m is overtopped |
| 9 | 0.10 | Donnelly Cross Road | Spencer | 0.17 m of water at peak; worst hour 25 mm (85% of the storm); a culvert within 100 m is overtopped |
| 10 | 0.07 | Green Street | Leicester | 0.15 m of water at peak; worst hour 24 mm (91% of the storm); a culvert within 100 m is overtopped |
| 11 | 0.07 | Rockland Road | Auburn | 0.15 m of water at peak; worst hour 19 mm (86% of the storm) |
| 12 | 0.05 | (unnamed) | Spencer | 0.13 m of water at peak; worst hour 14 mm (56% of the storm); +6 min to the nearest hospital |
| 13 | 0.05 | Auburn Street | Auburn | 0.13 m of water at peak; worst hour 21 mm (88% of the storm) |
| 14 | 0.05 | Dawson Road | Worcester | 0.13 m of water at peak; worst hour 17 mm (85% of the storm) |
| 15 | 0.04 | Washington Street | Worcester | 0.13 m of water at peak; worst hour 19 mm (83% of the storm); water beside the road 0.21 m below its crest (design freeboard 0.30 m; P 0.74) |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
