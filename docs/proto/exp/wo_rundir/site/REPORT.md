# Road-closure prototype: aug2021_exp_wo_rundir

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on CPU (OpenMP)), 20 m grid, storm from 2021-08-19T09:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 8,373 |
| Expected closures (sum of probabilities) | 416.8 |
| Segments with closure probability >= 50% | 349 (209.1 km) |
| Further segments that may close (stream reaches the road crest) | 315 (164.9 km) |
| Culverts overtopped / surcharged | 293 / 33 of 1347 |
| Road segments cut off from hospitals | 1754 |
| Worst added trip time to a hospital | 29.3 min |
| Heaviest hour of rain | 89.6 mm |
| Flood model run time | 916 s |

## Checks against what happened

- Storm-day flood reports in the area: 5; water >= 10 cm within 100 m of 80% of them, vs 72% of random points (any day).
- Segments flagged impassable are 2.11x as likely as an average segment to have a report within 200 m.
- MassDOT repeating flood sites in the area: 10; 5 have a segment within 150 m at P >= 0.5 (share of all segments at P >= 0.5: 4.2%).

## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 1.00 | I-290 | Worcester | 0.93 m of water at peak; over 30 cm for 13.0 h; 30 cm reached 5.5 h into the storm; worst hour 26 mm (47% of the storm); water beside the road 0.59 m above its crest (design freeboard 0.30 m; P 1.00) |
| 2 | 1.00 | I-290 | Worcester | 0.98 m of water at peak; over 30 cm for 13.5 h; 30 cm reached 5.0 h into the storm; worst hour 27 mm (46% of the storm); water beside the road 0.31 m above its crest (design freeboard 0.30 m; P 1.00); fast water: depth x speed 0.52 m2/s (small cars unstable from 0.3) |
| 3 | 1.00 | I-290 | Worcester | 0.88 m of water at peak; over 30 cm for 13.0 h; 30 cm reached 5.5 h into the storm; worst hour 24 mm (44% of the storm); water beside the road 0.02 m above its crest (design freeboard 0.30 m; P 0.98); a culvert within 100 m is overtopped |
| 4 | 1.00 | I-290 | Worcester | 1.00 m of water at peak; over 30 cm for 13.5 h; 30 cm reached 5.0 h into the storm; worst hour 24 mm (44% of the storm); water beside the road 0.51 m above its crest (design freeboard 0.30 m; P 1.00); a culvert within 100 m is overtopped |
| 5 | 1.00 | I-90 | Auburn | 1.33 m of water at peak; over 30 cm for 13.0 h; 30 cm reached 5.5 h into the storm; worst hour 38 mm (46% of the storm); a culvert within 100 m is overtopped |
| 6 | 1.00 | I-190 | Worcester | 0.90 m of water at peak; over 30 cm for 13.0 h; 30 cm reached 5.5 h into the storm; worst hour 29 mm (48% of the storm); water beside the road 0.63 m above its crest (design freeboard 0.30 m; P 1.00) |
| 7 | 1.00 | I-395 | Oxford | 0.92 m of water at peak; over 30 cm for 13.0 h; 30 cm reached 5.5 h into the storm; worst hour 38 mm (46% of the storm); a culvert within 100 m is overtopped |
| 8 | 1.00 | Route 20 | Worcester | 1.21 m of water at peak; over 30 cm for 13.0 h; 30 cm reached 5.5 h into the storm; worst hour 35 mm (44% of the storm); water beside the road 0.20 m above its crest (design freeboard 0.30 m; P 1.00) |
| 9 | 1.00 | Martin Luther King Jr Boulevard | Worcester | 3.23 m of water at peak; over 30 cm for 18.0 h; 30 cm reached 0.5 h into the storm; worst hour 24 mm (43% of the storm); water beside the road 3.15 m above its crest (design freeboard 0.30 m; P 1.00); fast water: depth x speed 0.33 m2/s (small cars unstable from 0.3); a culvert within 100 m is overtopped |
| 10 | 1.00 | Martin Luther King Jr Boulevard | Worcester | 2.53 m of water at peak; over 30 cm for 18.0 h; 30 cm reached 0.5 h into the storm; worst hour 24 mm (43% of the storm); water beside the road 2.21 m above its crest (design freeboard 0.30 m; P 1.00); fast water: depth x speed 0.36 m2/s (small cars unstable from 0.3); a culvert within 100 m is overtopped |
| 11 | 1.00 | Route 20 | Shrewsbury | 1.17 m of water at peak; over 30 cm for 12.0 h; 30 cm reached 6.5 h into the storm; worst hour 30 mm (52% of the storm); water beside the road 0.10 m below its crest (design freeboard 0.30 m; P 0.91); a culvert within 100 m is overtopped |
| 12 | 1.00 | Shrewsbury Street | Worcester | 0.68 m of water at peak; over 30 cm for 12.5 h; 30 cm reached 6.0 h into the storm; worst hour 24 mm (44% of the storm); water beside the road 0.59 m above its crest (design freeboard 0.30 m; P 1.00) |
| 13 | 1.00 | Route 20 | Worcester | 1.21 m of water at peak; over 30 cm for 13.0 h; 30 cm reached 5.5 h into the storm; worst hour 35 mm (44% of the storm); water beside the road 0.13 m below its crest (design freeboard 0.30 m; P 0.86) |
| 14 | 1.00 | Shrewsbury Street | Worcester | 0.78 m of water at peak; over 30 cm for 13.0 h; 30 cm reached 5.5 h into the storm; worst hour 24 mm (44% of the storm); water beside the road 0.70 m above its crest (design freeboard 0.30 m; P 1.00) |
| 15 | 1.00 | Southbridge Street | Worcester | 0.82 m of water at peak; over 30 cm for 12.5 h; 30 cm reached 6.0 h into the storm; worst hour 27 mm (47% of the storm); a culvert within 100 m is overtopped |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
