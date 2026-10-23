# Road-closure prototype: sep2023_fc_sep2023_hrrr12z_nb30max

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on CPU (OpenMP)), 20 m grid, storm from 2023-09-11T12:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 5,096 |
| Expected closures (sum of probabilities) | 522.3 |
| Segments with closure probability >= 50% | 478 (304.5 km) |
| Further segments that may close (stream reaches the road crest) | 515 (286.9 km) |
| Culverts overtopped / surcharged | 222 / 28 of 713 |
| Road segments cut off from hospitals | 2417 |
| Worst added trip time to a hospital | 47.5 min |
| Heaviest hour of rain | 62.3 mm |
| Flood model run time | 3334 s |

## Checks against what happened

- Storm-day flood reports in the area: 10; water >= 10 cm within 100 m of 100% of them, vs 93% of random points (any day).
- Segments flagged impassable are 2.04x as likely as an average segment to have a report within 200 m.
- MassDOT repeating flood sites in the area: 4; 2 have a segment within 150 m at P >= 0.5 (share of all segments at P >= 0.5: 9.4%).

## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 1.00 | Route 2 | Fitchburg | 1.44 m of water at peak; over 30 cm for 35.0 h; 30 cm reached 5.5 h into the storm; worst hour 62 mm (10% of the storm); water beside the road 0.11 m above its crest (design freeboard 0.30 m; P 1.00); a culvert within 100 m is overtopped |
| 2 | 1.00 | Route 2 | Fitchburg | 1.27 m of water at peak; over 30 cm for 34.0 h; 30 cm reached 6.5 h into the storm; worst hour 62 mm (10% of the storm); water beside the road 0.15 m below its crest (design freeboard 0.30 m; P 0.84); culvert (Wyman): headwater 12.23 m vs road crest 2.73 m, 67.9 m3/s |
| 3 | 1.00 | Route 2 | Leominster | 18.28 m of water at peak; over 30 cm for 33.5 h; 30 cm reached 6.0 h into the storm; worst hour 62 mm (11% of the storm); water beside the road 0.99 m above its crest (design freeboard 0.30 m; P 1.00); a culvert within 100 m is overtopped |
| 4 | 1.00 | Route 2 | Fitchburg | 0.97 m of water at peak; over 30 cm for 19.0 h; 30 cm reached 6.5 h into the storm; worst hour 62 mm (10% of the storm); water beside the road 0.61 m above its crest (design freeboard 0.30 m; P 1.00); a culvert within 100 m is overtopped |
| 5 | 1.00 | Route 2 | Fitchburg | 0.88 m of water at peak; over 30 cm for 19.0 h; 30 cm reached 6.5 h into the storm; worst hour 62 mm (10% of the storm); a culvert within 100 m is overtopped |
| 6 | 1.00 | Route 2 | Leominster | 0.73 m of water at peak; over 30 cm for 15.0 h; 30 cm reached 7.0 h into the storm; worst hour 62 mm (11% of the storm); water beside the road 0.65 m above its crest (design freeboard 0.30 m; P 1.00); road sag 3.4 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 62 mm; catchment 39.6 ha) (P 1.00) |
| 7 | 1.00 | (unnamed) | Leominster | 2.72 m of water at peak; over 30 cm for 34.0 h; 30 cm reached 6.5 h into the storm; worst hour 62 mm (11% of the storm); water beside the road 0.10 m above its crest (design freeboard 0.30 m; P 1.00); a culvert within 100 m is overtopped |
| 8 | 1.00 | Route 117 | Lancaster | 9.22 m of water at peak; over 30 cm for 29.5 h; 30 cm reached 11.0 h into the storm; worst hour 62 mm (12% of the storm); water beside the road 10.83 m above its crest (design freeboard 0.30 m; P 1.00) |
| 9 | 1.00 | Route 117 | Lancaster | 1.97 m of water at peak; over 30 cm for 31.5 h; 30 cm reached 9.0 h into the storm; worst hour 62 mm (12% of the storm); water beside the road 1.68 m above its crest (design freeboard 0.30 m; P 1.00); culvert (Trib to Still River): headwater 908.15 m vs road crest 2.74 m, 446.9 m3/s |
| 10 | 1.00 | Route 12 | Leominster | 1.42 m of water at peak; over 30 cm for 32.5 h; 30 cm reached 7.0 h into the storm; worst hour 62 mm (11% of the storm); water beside the road 0.68 m above its crest (design freeboard 0.30 m; P 1.00); a culvert within 100 m is overtopped |
| 11 | 1.00 | Route 12 | Leominster | 1.16 m of water at peak; over 30 cm for 25.0 h; 30 cm reached 7.0 h into the storm; worst hour 62 mm (11% of the storm); water beside the road 0.70 m above its crest (design freeboard 0.30 m; P 1.00); a culvert within 100 m is overtopped |
| 12 | 1.00 | Route 117 | Bolton | 1.11 m of water at peak; over 30 cm for 26.0 h; 30 cm reached 14.5 h into the storm; worst hour 62 mm (12% of the storm); water beside the road 0.84 m above its crest (design freeboard 0.30 m; P 1.00); a culvert within 100 m is overtopped |
| 13 | 1.00 | Route 117 | Leominster | 1.63 m of water at peak; over 30 cm for 33.0 h; 30 cm reached 7.0 h into the storm; worst hour 62 mm (11% of the storm); water beside the road 0.44 m above its crest (design freeboard 0.30 m; P 1.00); a culvert within 100 m is overtopped |
| 14 | 1.00 | Route 70 | Clinton | 1.64 m of water at peak; over 30 cm for 30.5 h; 30 cm reached 8.0 h into the storm; worst hour 62 mm (12% of the storm); water beside the road 0.97 m above its crest (design freeboard 0.30 m; P 1.00); a culvert within 100 m is overtopped |
| 15 | 1.00 | Merriam Avenue | Leominster | 1.02 m of water at peak; over 30 cm for 22.5 h; 30 cm reached 6.0 h into the storm; worst hour 62 mm (11% of the storm); water beside the road 0.82 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.4 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 62 mm; catchment 13.0 ha) (P 1.00) |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
