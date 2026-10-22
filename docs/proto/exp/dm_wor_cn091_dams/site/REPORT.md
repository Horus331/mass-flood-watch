# Road-closure prototype: aug2021_exp_dm_wor_cn091_dams

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on CPU (OpenMP)), 20 m grid, storm from 2021-08-19T09:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 8,354 |
| Expected closures (sum of probabilities) | 197.0 |
| Segments with closure probability >= 50% | 150 (93.4 km) |
| Further segments that may close (stream reaches the road crest) | 201 (102.3 km) |
| Culverts overtopped / surcharged | 240 / 7 of 1347 |
| Road segments cut off from hospitals | 982 |
| Worst added trip time to a hospital | 25.1 min |
| Heaviest hour of rain | 89.6 mm |
| Flood model run time | 1009 s |

## Checks against what happened

- Storm-day flood reports in the area: 5; water >= 10 cm within 100 m of 60% of them, vs 60% of random points (any day).
- Segments flagged impassable are 1.3x as likely as an average segment to have a report within 200 m.
- MassDOT repeating flood sites in the area: 10; 4 have a segment within 150 m at P >= 0.5 (share of all segments at P >= 0.5: 1.8%).

## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 1.00 | Martin Luther King Jr Boulevard | Worcester | 3.42 m of water at peak; over 30 cm for 17.5 h; 30 cm reached 1.0 h into the storm; worst hour 24 mm (43% of the storm); water beside the road 3.34 m above its crest (design freeboard 0.30 m; P 1.00); fast water: depth x speed 0.22 m2/s (small cars unstable from 0.3); road sag 3.2 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 24 mm; catchment 60.2 ha) (P 1.00); a culvert within 100 m is overtopped |
| 2 | 1.00 | Martin Luther King Jr Boulevard | Worcester | 2.72 m of water at peak; over 30 cm for 17.5 h; 30 cm reached 1.0 h into the storm; worst hour 24 mm (43% of the storm); water beside the road 2.40 m above its crest (design freeboard 0.30 m; P 1.00); fast water: depth x speed 0.21 m2/s (small cars unstable from 0.3); road sag 3.2 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 24 mm; catchment 60.2 ha) (P 1.00); a culvert within 100 m is overtopped |
| 3 | 1.00 | Route 20 | Worcester | 0.64 m of water at peak; over 30 cm for 10.5 h; 30 cm reached 7.0 h into the storm; worst hour 35 mm (44% of the storm); water beside the road 0.01 m below its crest (design freeboard 0.30 m; P 0.97); road sag 1.0 m deep (underpass, drains sized for the 50-yr hour, 58 mm; peak hour here 34 mm; catchment 12.1 ha) (P 1.00) |
| 4 | 1.00 | Foster Street | Worcester | 1.68 m of water at peak; over 30 cm for 11.5 h; 30 cm reached 7.0 h into the storm; worst hour 25 mm (44% of the storm); water beside the road 0.30 m below its crest (design freeboard 0.30 m; P 0.49); a culvert within 100 m is overtopped |
| 5 | 1.00 | Foster Street | Worcester | 1.68 m of water at peak; over 30 cm for 11.5 h; 30 cm reached 7.0 h into the storm; worst hour 25 mm (44% of the storm); water beside the road 0.29 m below its crest (design freeboard 0.30 m; P 0.54); a culvert within 100 m is overtopped |
| 6 | 1.00 | Major Taylor Boulevard | Worcester | 0.83 m of water at peak; over 30 cm for 10.0 h; 30 cm reached 8.5 h into the storm; worst hour 25 mm (44% of the storm); water beside the road 0.58 m above its crest (design freeboard 0.30 m; P 1.00); road sag 1.1 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 24 mm; catchment 60.2 ha) (P 1.00); a culvert within 100 m is overtopped |
| 7 | 1.00 | Major Taylor Boulevard | Worcester | 0.83 m of water at peak; over 30 cm for 10.0 h; 30 cm reached 8.5 h into the storm; worst hour 25 mm (44% of the storm); water beside the road 0.58 m above its crest (design freeboard 0.30 m; P 1.00); road sag 1.1 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 24 mm; catchment 60.2 ha) (P 1.00); a culvert within 100 m is overtopped |
| 8 | 1.00 | Providence Street | Millbury | 1.25 m of water at peak; over 30 cm for 17.0 h; 30 cm reached 1.5 h into the storm; worst hour 49 mm (54% of the storm); a culvert within 100 m is overtopped |
| 9 | 1.00 | Route 122 | Northbridge | 1.65 m of water at peak; over 30 cm for 16.0 h; 30 cm reached 2.5 h into the storm; worst hour 70 mm (68% of the storm); a culvert within 100 m is overtopped |
| 10 | 1.00 | Route 146 | Sutton | 0.77 m of water at peak; over 30 cm for 3.0 h; 30 cm reached 6.5 h into the storm; worst hour 72 mm (72% of the storm); water beside the road 0.11 m above its crest (design freeboard 0.30 m; P 1.00); a culvert within 100 m is overtopped |
| 11 | 1.00 | Route 12 | Auburn | 0.68 m of water at peak; over 30 cm for 8.5 h; 30 cm reached 10.0 h into the storm; worst hour 34 mm (48% of the storm) |
| 12 | 1.00 | Depot Road | Oxford | 0.81 m of water at peak; over 30 cm for 16.0 h; 30 cm reached 0.5 h into the storm; worst hour 41 mm (48% of the storm); a culvert within 100 m is overtopped |
| 13 | 1.00 | Auburn Street | Auburn | 0.96 m of water at peak; over 30 cm for 8.5 h; 30 cm reached 10.0 h into the storm; worst hour 31 mm (48% of the storm); water beside the road 0.18 m below its crest (design freeboard 0.30 m; P 0.79) |
| 14 | 1.00 | Benson Road | Northbridge | 0.63 m of water at peak; over 30 cm for 3.0 h; 30 cm reached 6.0 h into the storm; worst hour 76 mm (69% of the storm); water beside the road 0.29 m below its crest (design freeboard 0.30 m; P 0.54); a culvert within 100 m is overtopped |
| 15 | 1.00 | Ramp-Rt 395 Nb To Depot Rd | Oxford | 0.76 m of water at peak; over 30 cm for 9.0 h; 30 cm reached 0.5 h into the storm; worst hour 38 mm (46% of the storm); a culvert within 100 m is overtopped |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
