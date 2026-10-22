# Road-closure prototype: aug2021_exp_mb_d4

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on CPU (OpenMP)), 20 m grid, storm from 2021-08-19T09:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 8,354 |
| Expected closures (sum of probabilities) | 281.8 |
| Segments with closure probability >= 50% | 216 (137.4 km) |
| Further segments that may close (stream reaches the road crest) | 282 (136.3 km) |
| Culverts overtopped / surcharged | 314 / 4 of 1347 |
| Road segments cut off from hospitals | 1404 |
| Worst added trip time to a hospital | 23.6 min |
| Heaviest hour of rain | 89.6 mm |
| Flood model run time | 747 s |

## Checks against what happened

- Storm-day flood reports in the area: 5; water >= 10 cm within 100 m of 60% of them, vs 64% of random points (any day).
- Segments flagged impassable are 2.73x as likely as an average segment to have a report within 200 m.
- MassDOT repeating flood sites in the area: 10; 5 have a segment within 150 m at P >= 0.5 (share of all segments at P >= 0.5: 2.6%).

## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 1.00 | I-395 | Oxford | 0.78 m of water at peak; over 30 cm for 6.5 h; 30 cm reached 5.5 h into the storm; worst hour 38 mm (46% of the storm); a culvert within 100 m is overtopped |
| 2 | 1.00 | Martin Luther King Jr Boulevard | Worcester | 3.96 m of water at peak; over 30 cm for 17.5 h; 30 cm reached 1.0 h into the storm; worst hour 24 mm (43% of the storm); water beside the road 3.88 m above its crest (design freeboard 0.30 m; P 1.00); a culvert within 100 m is overtopped |
| 3 | 1.00 | Martin Luther King Jr Boulevard | Worcester | 3.26 m of water at peak; over 30 cm for 17.5 h; 30 cm reached 1.0 h into the storm; worst hour 24 mm (43% of the storm); water beside the road 2.94 m above its crest (design freeboard 0.30 m; P 1.00); a culvert within 100 m is overtopped |
| 4 | 1.00 | Shrewsbury Street | Worcester | 0.73 m of water at peak; over 30 cm for 12.5 h; 30 cm reached 6.0 h into the storm; worst hour 24 mm (44% of the storm); water beside the road 0.65 m above its crest (design freeboard 0.30 m; P 1.00) |
| 5 | 1.00 | Shrewsbury Street | Worcester | 0.83 m of water at peak; over 30 cm for 13.0 h; 30 cm reached 5.5 h into the storm; worst hour 24 mm (44% of the storm); water beside the road 0.75 m above its crest (design freeboard 0.30 m; P 1.00) |
| 6 | 1.00 | Foster Street | Worcester | 2.23 m of water at peak; over 30 cm for 13.0 h; 30 cm reached 5.5 h into the storm; worst hour 25 mm (44% of the storm); water beside the road 0.25 m above its crest (design freeboard 0.30 m; P 1.00); a culvert within 100 m is overtopped |
| 7 | 1.00 | Martin Luther King Jr Boulevard | Worcester | 0.93 m of water at peak; over 30 cm for 10.5 h; 30 cm reached 8.0 h into the storm; worst hour 24 mm (43% of the storm); water beside the road 0.76 m above its crest (design freeboard 0.30 m; P 1.00); a culvert within 100 m is overtopped |
| 8 | 1.00 | Major Taylor Boulevard | Worcester | 1.37 m of water at peak; over 30 cm for 12.5 h; 30 cm reached 6.0 h into the storm; worst hour 25 mm (44% of the storm); water beside the road 1.12 m above its crest (design freeboard 0.30 m; P 1.00); a culvert within 100 m is overtopped |
| 9 | 1.00 | Major Taylor Boulevard | Worcester | 1.37 m of water at peak; over 30 cm for 12.5 h; 30 cm reached 6.0 h into the storm; worst hour 25 mm (44% of the storm); water beside the road 1.12 m above its crest (design freeboard 0.30 m; P 1.00); a culvert within 100 m is overtopped |
| 10 | 1.00 | Thomas Street | Worcester | 0.76 m of water at peak; over 30 cm for 10.0 h; 30 cm reached 8.5 h into the storm; worst hour 25 mm (43% of the storm); water beside the road 0.72 m above its crest (design freeboard 0.30 m; P 1.00); a culvert within 100 m is overtopped |
| 11 | 1.00 | Foster Street | Worcester | 2.23 m of water at peak; over 30 cm for 13.0 h; 30 cm reached 5.5 h into the storm; worst hour 25 mm (44% of the storm); water beside the road 0.26 m above its crest (design freeboard 0.30 m; P 1.00); a culvert within 100 m is overtopped |
| 12 | 1.00 | Cambridge Street | Worcester | 0.86 m of water at peak; over 30 cm for 11.5 h; 30 cm reached 7.0 h into the storm; worst hour 29 mm (48% of the storm); water beside the road 0.72 m above its crest (design freeboard 0.30 m; P 1.00) |
| 13 | 1.00 | Route 122 | Northbridge | 2.33 m of water at peak; over 30 cm for 18.0 h; 30 cm reached 0.5 h into the storm; worst hour 70 mm (68% of the storm); a culvert within 100 m is overtopped |
| 14 | 1.00 | Route 20 | Worcester | 0.78 m of water at peak; over 30 cm for 6.0 h; 30 cm reached 6.0 h into the storm; worst hour 35 mm (44% of the storm); water beside the road 1.17 m above its crest (design freeboard 0.30 m; P 1.00) |
| 15 | 1.00 | Providence Street | Millbury | 1.55 m of water at peak; over 30 cm for 14.0 h; 30 cm reached 4.5 h into the storm; worst hour 49 mm (54% of the storm); a culvert within 100 m is overtopped |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
