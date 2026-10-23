# Road-closure prototype: aug2021_fc_aug2021_hrrr12z_nb30max

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on CPU (OpenMP)), 20 m grid, storm from 2021-08-19T12:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 8,354 |
| Expected closures (sum of probabilities) | 813.0 |
| Segments with closure probability >= 50% | 752 (386.3 km) |
| Further segments that may close (stream reaches the road crest) | 543 (254.4 km) |
| Culverts overtopped / surcharged | 461 / 34 of 1347 |
| Road segments cut off from hospitals | 3107 |
| Worst added trip time to a hospital | 51.3 min |
| Heaviest hour of rain | 48.6 mm |
| Flood model run time | 764 s |

## Checks against what happened

- Storm-day flood reports in the area: 5; water >= 10 cm within 100 m of 60% of them, vs 76% of random points (any day).
- Segments flagged impassable are 2.13x as likely as an average segment to have a report within 200 m.
- MassDOT repeating flood sites in the area: 10; 7 have a segment within 150 m at P >= 0.5 (share of all segments at P >= 0.5: 9.0%).

## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 1.00 | (unnamed) | Worcester | 2.16 m of water at peak; over 30 cm for 11.5 h; 30 cm reached 4.0 h into the storm; worst hour 47 mm (21% of the storm); water beside the road 2.05 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.7 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 47 mm; catchment 77.2 ha) (P 1.00) |
| 2 | 1.00 | I-290 | Shrewsbury | 1.03 m of water at peak; over 30 cm for 11.5 h; 30 cm reached 4.0 h into the storm; worst hour 49 mm (21% of the storm); water beside the road 1.03 m above its crest (design freeboard 0.30 m; P 1.00) |
| 3 | 1.00 | I-290 | Shrewsbury | 0.74 m of water at peak; over 30 cm for 11.0 h; 30 cm reached 4.5 h into the storm; worst hour 49 mm (21% of the storm); water beside the road 0.74 m above its crest (design freeboard 0.30 m; P 1.00) |
| 4 | 1.00 | Route 146 | Worcester | 2.56 m of water at peak; over 30 cm for 11.5 h; 30 cm reached 4.0 h into the storm; worst hour 46 mm (21% of the storm); water beside the road 0.06 m above its crest (design freeboard 0.30 m; P 0.99); a culvert within 100 m is overtopped |
| 5 | 1.00 | Route 9 | Northborough | 0.75 m of water at peak; over 30 cm for 10.5 h; 30 cm reached 3.5 h into the storm; worst hour 49 mm (23% of the storm); water beside the road 0.33 m above its crest (design freeboard 0.30 m; P 1.00); a culvert within 100 m is overtopped |
| 6 | 1.00 | Route 146 | Millbury | 1.44 m of water at peak; over 30 cm for 10.5 h; 30 cm reached 5.0 h into the storm; worst hour 46 mm (24% of the storm); a culvert within 100 m is overtopped |
| 7 | 1.00 | Route 9 | Worcester | 1.11 m of water at peak; over 30 cm for 11.0 h; 30 cm reached 4.5 h into the storm; worst hour 49 mm (22% of the storm); water beside the road 1.11 m above its crest (design freeboard 0.30 m; P 1.00) |
| 8 | 1.00 | Route 70 | Worcester | 1.37 m of water at peak; over 30 cm for 12.5 h; 30 cm reached 3.0 h into the storm; worst hour 49 mm (21% of the storm); a culvert within 100 m is overtopped |
| 9 | 1.00 | Route 9 | Worcester | 1.11 m of water at peak; over 30 cm for 11.0 h; 30 cm reached 4.5 h into the storm; worst hour 49 mm (22% of the storm); water beside the road 1.11 m above its crest (design freeboard 0.30 m; P 1.00) |
| 10 | 1.00 | Route 70 | Worcester | 1.37 m of water at peak; over 30 cm for 12.5 h; 30 cm reached 3.0 h into the storm; worst hour 49 mm (21% of the storm); a culvert within 100 m is overtopped |
| 11 | 1.00 | Route 9 | Northborough | 0.74 m of water at peak; over 30 cm for 8.5 h; 30 cm reached 3.5 h into the storm; worst hour 49 mm (23% of the storm); water beside the road 0.09 m above its crest (design freeboard 0.30 m; P 1.00); a culvert within 100 m is overtopped |
| 12 | 1.00 | Route 146 | Worcester | 0.67 m of water at peak; over 30 cm for 6.0 h; 30 cm reached 6.0 h into the storm; worst hour 46 mm (21% of the storm); water beside the road 0.26 m below its crest (design freeboard 0.30 m; P 0.61); road sag 0.6 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 46 mm; catchment 6.4 ha) (P 0.47); a culvert within 100 m is overtopped |
| 13 | 1.00 | Route 20 | Worcester | 1.10 m of water at peak; over 30 cm for 12.0 h; 30 cm reached 3.5 h into the storm; worst hour 46 mm (22% of the storm); a culvert within 100 m is overtopped |
| 14 | 1.00 | Route 20 | Shrewsbury | 1.53 m of water at peak; over 30 cm for 12.5 h; 30 cm reached 3.0 h into the storm; worst hour 48 mm (22% of the storm); water beside the road 0.15 m above its crest (design freeboard 0.30 m; P 1.00); culvert (Big Bummet Brook): headwater 52.12 m vs road crest 1.83 m, 57.0 m3/s |
| 15 | 1.00 | Shrewsbury Street | Worcester | 2.51 m of water at peak; over 30 cm for 12.5 h; 30 cm reached 3.0 h into the storm; worst hour 49 mm (21% of the storm); water beside the road 2.43 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.8 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 48 mm; catchment 127.8 ha) (P 1.00) |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
