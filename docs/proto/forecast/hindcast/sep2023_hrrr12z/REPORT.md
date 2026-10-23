# Road-closure prototype: sep2023_fc_sep2023_hrrr12z

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on CPU (OpenMP)), 20 m grid, storm from 2023-09-11T12:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 5,096 |
| Expected closures (sum of probabilities) | 15.1 |
| Segments with closure probability >= 50% | 4 (3.7 km) |
| Further segments that may close (stream reaches the road crest) | 5 (4.5 km) |
| Culverts overtopped / surcharged | 18 / 0 of 713 |
| Road segments cut off from hospitals | 20 |
| Worst added trip time to a hospital | 15.1 min |
| Heaviest hour of rain | 56.0 mm |
| Flood model run time | 419 s |

## Checks against what happened

- Storm-day flood reports in the area: 10; water >= 10 cm within 100 m of 0% of them, vs 24% of random points (any day).
- Segments flagged impassable are 0.0x as likely as an average segment to have a report within 200 m.
- MassDOT repeating flood sites in the area: 4; 0 have a segment within 150 m at P >= 0.5 (share of all segments at P >= 0.5: 0.1%).

## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 0.99 | Houghton Road | Princeton | 0.52 m of water at peak; over 30 cm for 2.0 h; 30 cm reached 13.5 h into the storm; worst hour 26 mm (65% of the storm); water beside the road 0.12 m above its crest (design freeboard 0.30 m; P 1.00); a culvert within 100 m is overtopped |
| 2 | 0.96 | Depot Street | Fitchburg | 0.47 m of water at peak; over 30 cm for 1.0 h; 30 cm reached 0.5 h into the storm; worst hour 9 mm (32% of the storm); a culvert within 100 m is overtopped |
| 3 | 0.94 | Bullard Road | Princeton | 0.46 m of water at peak; over 30 cm for 2.0 h; 30 cm reached 13.5 h into the storm; worst hour 20 mm (59% of the storm); water beside the road 0.08 m below its crest (design freeboard 0.30 m; P 0.92); a culvert within 100 m is overtopped |
| 4 | 0.89 | Mirick Road | Princeton | 0.42 m of water at peak; over 30 cm for 0.5 h; 30 cm reached 12.5 h into the storm; worst hour 45 mm (61% of the storm); a culvert within 100 m is overtopped |
| 5 | 0.42 | Route 31 | Fitchburg | 0.28 m of water at peak; worst hour 11 mm (33% of the storm); a culvert within 100 m is overtopped |
| 6 | 0.41 | Sanborn Street | Fitchburg | 0.28 m of water at peak; worst hour 9 mm (32% of the storm); a culvert within 100 m is overtopped |
| 7 | 0.35 | Hobbs Road | Princeton | 0.26 m of water at peak; worst hour 31 mm (65% of the storm); a culvert within 100 m is overtopped |
| 8 | 0.22 | Flanagan Hill Road | Sterling | 0.22 m of water at peak; worst hour 2 mm (26% of the storm) |
| 9 | 0.21 | John Fitch Highway | Fitchburg | 0.22 m of water at peak; worst hour 6 mm (25% of the storm) |
| 10 | 0.19 | (unnamed) | Princeton | 0.21 m of water at peak; worst hour 52 mm (68% of the storm); water beside the road 0.16 m above its crest (design freeboard 0.30 m; P 1.00) |
| 11 | 0.15 | Narrows Road | Westminster | 0.20 m of water at peak; worst hour 14 mm (34% of the storm); water beside the road 0.12 m below its crest (design freeboard 0.30 m; P 0.88); a culvert within 100 m is overtopped |
| 12 | 0.15 | (unnamed) | Leominster | 0.20 m of water at peak; worst hour 7 mm (46% of the storm); a culvert within 100 m is overtopped |
| 13 | 0.14 | Gleason Road | Princeton | 0.19 m of water at peak; worst hour 26 mm (69% of the storm); a culvert within 100 m is overtopped |
| 14 | 0.12 | Route 140 | Princeton | 0.18 m of water at peak; worst hour 28 mm (53% of the storm); a culvert within 100 m is overtopped |
| 15 | 0.09 | Route 31 | Princeton | 0.16 m of water at peak; worst hour 28 mm (55% of the storm); a culvert within 100 m is overtopped |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
