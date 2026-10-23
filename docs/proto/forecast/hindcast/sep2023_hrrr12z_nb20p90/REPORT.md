# Road-closure prototype: sep2023_fc_sep2023_hrrr12z_nb20p90

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on CPU (OpenMP)), 20 m grid, storm from 2023-09-11T12:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 5,096 |
| Expected closures (sum of probabilities) | 33.6 |
| Segments with closure probability >= 50% | 17 (12.3 km) |
| Further segments that may close (stream reaches the road crest) | 25 (14.6 km) |
| Culverts overtopped / surcharged | 46 / 0 of 713 |
| Road segments cut off from hospitals | 185 |
| Worst added trip time to a hospital | 14.0 min |
| Heaviest hour of rain | 15.7 mm |
| Flood model run time | 1012 s |

## Checks against what happened

- Storm-day flood reports in the area: 10; water >= 10 cm within 100 m of 40% of them, vs 47% of random points (any day).
- Segments flagged impassable are 1.31x as likely as an average segment to have a report within 200 m.
- MassDOT repeating flood sites in the area: 4; 0 have a segment within 150 m at P >= 0.5 (share of all segments at P >= 0.5: 0.3%).

## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 1.00 | Route 2 | Leominster | 0.91 m of water at peak; over 30 cm for 27.5 h; 30 cm reached 13.0 h into the storm; worst hour 11 mm (14% of the storm); a culvert within 100 m is overtopped |
| 2 | 1.00 | Depot Street | Fitchburg | 0.80 m of water at peak; over 30 cm for 23.5 h; 30 cm reached 0.5 h into the storm; worst hour 14 mm (12% of the storm); a culvert within 100 m is overtopped |
| 3 | 1.00 | (unnamed) | Leominster | 0.63 m of water at peak; over 30 cm for 25.5 h; 30 cm reached 12.5 h into the storm; worst hour 11 mm (13% of the storm); a culvert within 100 m is overtopped |
| 4 | 1.00 | Water Street | Leominster | 0.63 m of water at peak; over 30 cm for 25.5 h; 30 cm reached 12.5 h into the storm; worst hour 11 mm (13% of the storm); a culvert within 100 m is overtopped |
| 5 | 1.00 | Depot Square | Leominster | 0.63 m of water at peak; over 30 cm for 25.5 h; 30 cm reached 12.5 h into the storm; worst hour 11 mm (13% of the storm); a culvert within 100 m is overtopped |
| 6 | 1.00 | Sanborn Street | Fitchburg | 0.56 m of water at peak; over 30 cm for 8.0 h; 30 cm reached 11.0 h into the storm; worst hour 14 mm (13% of the storm); a culvert within 100 m is overtopped |
| 7 | 0.83 | (unnamed) | Lunenburg | 0.40 m of water at peak; over 30 cm for 6.5 h; 30 cm reached 13.0 h into the storm; worst hour 8 mm (11% of the storm); water beside the road 0.29 m below its crest (design freeboard 0.30 m; P 0.52); a culvert within 100 m is overtopped |
| 8 | 0.81 | (unnamed) | Leominster | 0.39 m of water at peak; over 30 cm for 4.0 h; 30 cm reached 12.0 h into the storm; worst hour 11 mm (12% of the storm) |
| 9 | 0.81 | Exchange Street | Leominster | 0.39 m of water at peak; over 30 cm for 4.0 h; 30 cm reached 12.0 h into the storm; worst hour 11 mm (12% of the storm); water beside the road 0.58 m above its crest (design freeboard 0.30 m; P 1.00); a culvert within 100 m is overtopped |
| 10 | 0.79 | Kingman Drive | Leominster | 0.38 m of water at peak; over 30 cm for 6.0 h; 30 cm reached 12.5 h into the storm; worst hour 11 mm (12% of the storm); a culvert within 100 m is overtopped |
| 11 | 0.72 | Houghton Road | Princeton | 0.36 m of water at peak; over 30 cm for 2.5 h; 30 cm reached 16.5 h into the storm; worst hour 11 mm (13% of the storm); water beside the road 0.01 m below its crest (design freeboard 0.30 m; P 0.97); a culvert within 100 m is overtopped |
| 12 | 0.66 | Constitution Drive | Leominster | 0.34 m of water at peak; over 30 cm for 2.0 h; 30 cm reached 12.0 h into the storm; worst hour 11 mm (12% of the storm) |
| 13 | 0.63 | Bullard Road | Princeton | 0.33 m of water at peak; over 30 cm for 1.0 h; 30 cm reached 32.0 h into the storm; worst hour 11 mm (13% of the storm); water beside the road 0.23 m below its crest (design freeboard 0.30 m; P 0.68); a culvert within 100 m is overtopped |
| 14 | 0.63 | Westminster Hill Road | Fitchburg | 0.33 m of water at peak; over 30 cm for 2.5 h; 30 cm reached 12.5 h into the storm; worst hour 14 mm (13% of the storm); a culvert within 100 m is overtopped |
| 15 | 0.59 | Hobbs Road | Princeton | 0.32 m of water at peak; over 30 cm for 3.0 h; 30 cm reached 15.5 h into the storm; worst hour 11 mm (12% of the storm); a culvert within 100 m is overtopped |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
