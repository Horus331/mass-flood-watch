# Road-closure prototype: sep2023_fc_sep2023_hrrr18z

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on CPU (OpenMP)), 20 m grid, storm from 2023-09-11T18:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 5,096 |
| Expected closures (sum of probabilities) | 27.8 |
| Segments with closure probability >= 50% | 13 (8.8 km) |
| Further segments that may close (stream reaches the road crest) | 15 (10.6 km) |
| Culverts overtopped / surcharged | 43 / 0 of 713 |
| Road segments cut off from hospitals | 90 |
| Worst added trip time to a hospital | 18.7 min |
| Heaviest hour of rain | 32.0 mm |
| Flood model run time | 560 s |

## Checks against what happened

- Storm-day flood reports in the area: 10; water >= 10 cm within 100 m of 0% of them, vs 38% of random points (any day).
- Segments flagged impassable are 0.92x as likely as an average segment to have a report within 200 m.
- MassDOT repeating flood sites in the area: 4; 0 have a segment within 150 m at P >= 0.5 (share of all segments at P >= 0.5: 0.3%).

## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 0.99 | Depot Street | Fitchburg | 0.52 m of water at peak; over 30 cm for 10.5 h; 30 cm reached 0.5 h into the storm; worst hour 21 mm (36% of the storm); a culvert within 100 m is overtopped |
| 2 | 0.98 | (unnamed) | Leominster | 0.52 m of water at peak; over 30 cm for 12.0 h; 30 cm reached 9.5 h into the storm; worst hour 18 mm (38% of the storm); a culvert within 100 m is overtopped |
| 3 | 0.98 | Water Street | Leominster | 0.52 m of water at peak; over 30 cm for 12.5 h; 30 cm reached 9.5 h into the storm; worst hour 17 mm (37% of the storm); a culvert within 100 m is overtopped |
| 4 | 0.98 | Depot Square | Leominster | 0.52 m of water at peak; over 30 cm for 12.0 h; 30 cm reached 9.5 h into the storm; worst hour 17 mm (36% of the storm); a culvert within 100 m is overtopped |
| 5 | 0.96 | Houghton Road | Princeton | 0.47 m of water at peak; over 30 cm for 4.5 h; 30 cm reached 8.0 h into the storm; worst hour 21 mm (27% of the storm); water beside the road 0.08 m above its crest (design freeboard 0.30 m; P 0.99); a culvert within 100 m is overtopped |
| 6 | 0.89 | Bullard Road | Princeton | 0.42 m of water at peak; over 30 cm for 3.5 h; 30 cm reached 8.5 h into the storm; worst hour 20 mm (26% of the storm); water beside the road 0.11 m below its crest (design freeboard 0.30 m; P 0.89); a culvert within 100 m is overtopped |
| 7 | 0.82 | Hobbs Road | Princeton | 0.39 m of water at peak; over 30 cm for 3.5 h; 30 cm reached 9.0 h into the storm; worst hour 24 mm (28% of the storm); water beside the road 0.45 m below its crest (design freeboard 0.30 m; P 0.16); a culvert within 100 m is overtopped |
| 8 | 0.79 | (unnamed) | Leominster | 0.38 m of water at peak; over 30 cm for 2.5 h; 30 cm reached 8.0 h into the storm; worst hour 19 mm (34% of the storm) |
| 9 | 0.78 | Exchange Street | Leominster | 0.38 m of water at peak; over 30 cm for 2.5 h; 30 cm reached 8.0 h into the storm; worst hour 19 mm (33% of the storm); water beside the road 0.58 m above its crest (design freeboard 0.30 m; P 1.00); a culvert within 100 m is overtopped |
| 10 | 0.77 | Gleason Road | Princeton | 0.38 m of water at peak; over 30 cm for 3.0 h; 30 cm reached 27.5 h into the storm; worst hour 21 mm (28% of the storm); water beside the road 0.83 m above its crest (design freeboard 0.30 m; P 1.00); a culvert within 100 m is overtopped |
| 11 | 0.63 | Constitution Drive | Leominster | 0.33 m of water at peak; over 30 cm for 2.0 h; 30 cm reached 8.0 h into the storm; worst hour 18 mm (32% of the storm) |
| 12 | 0.54 | Mirick Road | Princeton | 0.31 m of water at peak; worst hour 25 mm (28% of the storm); a culvert within 100 m is overtopped |
| 13 | 0.53 | Kingman Drive | Leominster | 0.31 m of water at peak; over 30 cm for 0.5 h; 30 cm reached 10.5 h into the storm; worst hour 18 mm (34% of the storm); a culvert within 100 m is overtopped |
| 14 | 0.48 | Route 140 | Princeton | 0.30 m of water at peak; worst hour 23 mm (28% of the storm); a culvert within 100 m is overtopped |
| 15 | 0.42 | Route 31 | Fitchburg | 0.28 m of water at peak; worst hour 26 mm (38% of the storm); a culvert within 100 m is overtopped |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
