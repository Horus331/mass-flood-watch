# Road-closure prototype: jul2019_loss_jul2019_spencer_20m

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on CPU (OpenMP)), 20 m grid, storm from 2019-07-06T14:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 6,236 |
| Expected closures (sum of probabilities) | 20.4 |
| Segments with closure probability >= 50% | 6 (1.8 km) |
| Further segments that may close (stream reaches the road crest) | 11 (6.5 km) |
| Culverts overtopped / surcharged | 24 / 0 of 1121 |
| Road segments cut off from hospitals | 39 |
| Worst added trip time to a hospital | 14.1 min |
| Heaviest hour of rain | 32.6 mm |
| Flood model run time | 1289 s |

## Checks against what happened

- Storm-day flood reports in the area: 3; water >= 10 cm within 100 m of 0% of them, vs 13% of random points (any day).
- Segments flagged impassable are 0.0x as likely as an average segment to have a report within 200 m.
- MassDOT repeating flood sites in the area: 7; 1 have a segment within 150 m at P >= 0.5 (share of all segments at P >= 0.5: 0.1%).

## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 1.00 | Martin Luther King Jr Boulevard | Worcester | 1.52 m of water at peak; over 30 cm for 17.5 h; 30 cm reached 1.0 h into the storm; worst hour 26 mm (85% of the storm); water beside the road 1.44 m above its crest (design freeboard 0.30 m; P 1.00); road sag 3.2 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 26 mm; catchment 60.2 ha) (P 1.00) |
| 2 | 1.00 | Martin Luther King Jr Boulevard | Worcester | 0.82 m of water at peak; over 30 cm for 17.5 h; 30 cm reached 1.0 h into the storm; worst hour 26 mm (85% of the storm); water beside the road 0.31 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 2.3 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.26); road sag 3.2 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 26 mm; catchment 60.2 ha) (P 1.00) |
| 3 | 1.00 | Foster Street | Worcester | 0.79 m of water at peak; over 30 cm for 11.5 h; 30 cm reached 7.0 h into the storm; worst hour 25 mm (85% of the storm); water beside the road 0.40 m below its crest (design freeboard 0.30 m; P 0.25); a culvert within 100 m is overtopped |
| 4 | 1.00 | Foster Street | Worcester | 0.79 m of water at peak; over 30 cm for 11.5 h; 30 cm reached 7.0 h into the storm; worst hour 25 mm (85% of the storm); water beside the road 0.28 m below its crest (design freeboard 0.30 m; P 0.55); a culvert within 100 m is overtopped |
| 5 | 1.00 | (unnamed) | Worcester | 0.77 m of water at peak; over 30 cm for 9.0 h; 30 cm reached 9.5 h into the storm; worst hour 28 mm (85% of the storm); a culvert within 100 m is overtopped |
| 6 | 0.73 | (unnamed) | Spencer | 0.36 m of water at peak; over 30 cm for 2.0 h; 30 cm reached 10.5 h into the storm; worst hour 24 mm (78% of the storm) |
| 7 | 0.42 | Stafford Street | Worcester | 0.28 m of water at peak; worst hour 18 mm (81% of the storm); a culvert within 100 m is overtopped |
| 8 | 0.42 | Ludlow Street | Worcester | 0.28 m of water at peak; worst hour 19 mm (82% of the storm); a culvert within 100 m is overtopped |
| 9 | 0.21 | James Street | Worcester | 0.22 m of water at peak; worst hour 18 mm (79% of the storm); a culvert within 100 m is overtopped |
| 10 | 0.18 | Route 12 | Auburn | 0.21 m of water at peak; worst hour 16 mm (70% of the storm); a culvert within 100 m is overtopped |
| 11 | 0.15 | Wire Village Road | Spencer | 0.20 m of water at peak; worst hour 27 mm (62% of the storm); a culvert within 100 m is overtopped |
| 12 | 0.13 | Washington Street | Worcester | 0.19 m of water at peak; worst hour 23 mm (85% of the storm); water beside the road 0.17 m below its crest (design freeboard 0.30 m; P 0.80); a culvert within 100 m is overtopped |
| 13 | 0.13 | Hastings Road | Spencer | 0.19 m of water at peak; worst hour 25 mm (71% of the storm); a culvert within 100 m is overtopped |
| 14 | 0.12 | Cooney Road | Spencer | 0.18 m of water at peak; worst hour 25 mm (68% of the storm); a culvert within 100 m is overtopped |
| 15 | 0.12 | (unnamed) | Spencer | 0.18 m of water at peak; worst hour 24 mm (59% of the storm); a culvert within 100 m is overtopped |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
