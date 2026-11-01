# Road-closure prototype: jul2019_loss_jul2019_spencer_20m

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on CPU (OpenMP)), 20 m grid, storm from 2019-07-06T14:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 6,236 |
| Expected closures (sum of probabilities) | 14.0 |
| Segments with closure probability >= 50% | 0 (0.0 km) |
| Further segments that may close (stream reaches the road crest) | 8 (4.2 km) |
| Culverts overtopped / surcharged | 16 / 0 of 1121 |
| Road segments cut off from hospitals | 21 |
| Worst added trip time to a hospital | 13.0 min |
| Heaviest hour of rain | 32.6 mm |
| Flood model run time | 736 s |

## Checks against what happened

- Storm-day flood reports in the area: 3; water >= 10 cm within 100 m of 0% of them, vs 11% of random points (any day).
- Segments flagged impassable are 0.0x as likely as an average segment to have a report within 200 m.
- MassDOT repeating flood sites in the area: 7; 0 have a segment within 150 m at P >= 0.5 (share of all segments at P >= 0.5: 0.0%).

## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 0.40 | (unnamed) | Spencer | 0.27 m of water at peak; worst hour 24 mm (78% of the storm) |
| 2 | 0.35 | Stafford Street | Worcester | 0.26 m of water at peak; worst hour 18 mm (81% of the storm); a culvert within 100 m is overtopped |
| 3 | 0.21 | Martin Luther King Jr Boulevard | Worcester | 0.22 m of water at peak; worst hour 26 mm (85% of the storm); water beside the road 0.14 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 0.7 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.19); road sag 3.2 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 26 mm; catchment 60.2 ha) (P 0.21) |
| 4 | 0.17 | Donnelly Cross Road | Spencer | 0.21 m of water at peak; worst hour 27 mm (61% of the storm); a culvert within 100 m is overtopped |
| 5 | 0.17 | Route 12 | Auburn | 0.20 m of water at peak; worst hour 16 mm (70% of the storm); runoff beside / along the road at 1.5 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.12); a culvert within 100 m is overtopped |
| 6 | 0.17 | Wire Village Road | Spencer | 0.20 m of water at peak; worst hour 27 mm (62% of the storm); a culvert within 100 m is overtopped |
| 7 | 0.16 | James Street | Worcester | 0.20 m of water at peak; worst hour 18 mm (79% of the storm); a culvert within 100 m is overtopped |
| 8 | 0.13 | Hastings Road | Spencer | 0.19 m of water at peak; worst hour 25 mm (71% of the storm); a culvert within 100 m is overtopped |
| 9 | 0.12 | (unnamed) | Spencer | 0.18 m of water at peak; worst hour 24 mm (59% of the storm); a culvert within 100 m is overtopped |
| 10 | 0.11 | (unnamed) | Charlton | 0.17 m of water at peak; worst hour 19 mm (74% of the storm); a culvert within 100 m is overtopped |
| 11 | 0.10 | Hampton Street | Auburn | 0.17 m of water at peak; worst hour 16 mm (70% of the storm); water beside the road 0.42 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 0.7 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.21); a culvert within 100 m is overtopped |
| 12 | 0.07 | Brookfield Road | Charlton | 0.15 m of water at peak; worst hour 22 mm (78% of the storm); a culvert within 100 m is overtopped |
| 13 | 0.07 | Green Street | Leicester | 0.15 m of water at peak; worst hour 16 mm (73% of the storm); a culvert within 100 m is overtopped |
| 14 | 0.06 | South Sturbridge Road | Charlton | 0.14 m of water at peak; worst hour 23 mm (79% of the storm); a culvert within 100 m is overtopped |
| 15 | 0.05 | Carleton Road | Millbury | 0.14 m of water at peak; worst hour 12 mm (52% of the storm) |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
