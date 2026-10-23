# Road-closure prototype: sep2023_fc_sep2023_hrrr18z_nb20p90

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on CPU (OpenMP)), 20 m grid, storm from 2023-09-11T18:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 5,096 |
| Expected closures (sum of probabilities) | 132.4 |
| Segments with closure probability >= 50% | 103 (74.0 km) |
| Further segments that may close (stream reaches the road crest) | 126 (77.1 km) |
| Culverts overtopped / surcharged | 148 / 1 of 713 |
| Road segments cut off from hospitals | 745 |
| Worst added trip time to a hospital | 25.7 min |
| Heaviest hour of rain | 35.1 mm |
| Flood model run time | 892 s |

## Checks against what happened

- Storm-day flood reports in the area: 10; water >= 10 cm within 100 m of 60% of them, vs 63% of random points (any day).
- Segments flagged impassable are 2.33x as likely as an average segment to have a report within 200 m.
- MassDOT repeating flood sites in the area: 4; 1 have a segment within 150 m at P >= 0.5 (share of all segments at P >= 0.5: 2.0%).

## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 1.00 | Route 2 | Leominster | 3.45 m of water at peak; over 30 cm for 28.0 h; 30 cm reached 6.5 h into the storm; worst hour 20 mm (19% of the storm); a culvert within 100 m is overtopped |
| 2 | 1.00 | (unnamed) | Leominster | 1.17 m of water at peak; over 30 cm for 27.5 h; 30 cm reached 7.0 h into the storm; worst hour 22 mm (19% of the storm); water beside the road 0.21 m below its crest (design freeboard 0.30 m; P 0.73); a culvert within 100 m is overtopped |
| 3 | 1.00 | Depot Street | Fitchburg | 1.31 m of water at peak; over 30 cm for 27.0 h; 30 cm reached 0.5 h into the storm; worst hour 24 mm (19% of the storm); a culvert within 100 m is overtopped |
| 4 | 1.00 | Litchfield Street | Leominster | 1.01 m of water at peak; over 30 cm for 18.5 h; 30 cm reached 7.5 h into the storm; worst hour 24 mm (20% of the storm); a culvert within 100 m is overtopped |
| 5 | 1.00 | Water Street | Leominster | 1.18 m of water at peak; over 30 cm for 27.5 h; 30 cm reached 7.0 h into the storm; worst hour 22 mm (19% of the storm); a culvert within 100 m is overtopped |
| 6 | 1.00 | Route 117 | Leominster | 0.65 m of water at peak; over 30 cm for 6.5 h; 30 cm reached 8.0 h into the storm; worst hour 24 mm (20% of the storm); a culvert within 100 m is overtopped |
| 7 | 1.00 | Route 70 | Clinton | 0.83 m of water at peak; over 30 cm for 6.0 h; 30 cm reached 7.5 h into the storm; worst hour 25 mm (19% of the storm); a culvert within 100 m is overtopped |
| 8 | 1.00 | Route 70 | Lancaster | 1.34 m of water at peak; over 30 cm for 7.5 h; 30 cm reached 9.5 h into the storm; worst hour 25 mm (21% of the storm); a culvert within 100 m is overtopped |
| 9 | 1.00 | Route 70 | Lancaster | 1.34 m of water at peak; over 30 cm for 7.5 h; 30 cm reached 9.5 h into the storm; worst hour 26 mm (21% of the storm); a culvert within 100 m is overtopped |
| 10 | 1.00 | John Fitch Highway | Fitchburg | 0.70 m of water at peak; over 30 cm for 4.5 h; 30 cm reached 6.5 h into the storm; worst hour 30 mm (25% of the storm); water beside the road 0.45 m below its crest (design freeboard 0.30 m; P 0.16) |
| 11 | 1.00 | Route 110 | Lancaster | 0.70 m of water at peak; over 30 cm for 12.0 h; 30 cm reached 6.5 h into the storm; worst hour 26 mm (20% of the storm); water beside the road 0.40 m below its crest (design freeboard 0.30 m; P 0.25); a culvert within 100 m is overtopped |
| 12 | 1.00 | (unnamed) | Sterling | 0.91 m of water at peak; over 30 cm for 28.5 h; 30 cm reached 6.0 h into the storm; worst hour 26 mm (19% of the storm); water beside the road 0.19 m above its crest (design freeboard 0.30 m; P 1.00); road sag 7.2 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 26 mm; catchment 8.7 ha) (P 1.00) |
| 13 | 1.00 | Kingman Drive | Leominster | 0.88 m of water at peak; over 30 cm for 14.5 h; 30 cm reached 6.5 h into the storm; worst hour 22 mm (18% of the storm); water beside the road 0.37 m above its crest (design freeboard 0.30 m; P 1.00); a culvert within 100 m is overtopped |
| 14 | 1.00 | Litchfield Street | Leominster | 0.90 m of water at peak; over 30 cm for 13.5 h; 30 cm reached 7.5 h into the storm; worst hour 24 mm (20% of the storm) |
| 15 | 1.00 | Depot Square | Leominster | 1.17 m of water at peak; over 30 cm for 27.5 h; 30 cm reached 7.0 h into the storm; worst hour 22 mm (19% of the storm); a culvert within 100 m is overtopped |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
