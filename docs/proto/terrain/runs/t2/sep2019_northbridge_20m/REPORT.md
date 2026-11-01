# Road-closure prototype: sep2019_loss_sep2019_northbridge_20m

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on CPU (OpenMP)), 20 m grid, storm from 2019-09-02T14:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 4,536 |
| Expected closures (sum of probabilities) | 10.1 |
| Segments with closure probability >= 50% | 1 (0.0 km) |
| Further segments that may close (stream reaches the road crest) | 1 (0.3 km) |
| Culverts overtopped / surcharged | 9 / 0 of 959 |
| Road segments cut off from hospitals | 21 |
| Worst added trip time to a hospital | 7.6 min |
| Heaviest hour of rain | 28.4 mm |
| Flood model run time | 1293 s |

## Checks against what happened

- Storm-day flood reports in the area: 2; water >= 10 cm within 100 m of 0% of them, vs 8% of random points (any day).
- Segments flagged impassable are 0.0x as likely as an average segment to have a report within 200 m.
- MassDOT repeating flood sites in the area: 6; 0 have a segment within 150 m at P >= 0.5 (share of all segments at P >= 0.5: 0.0%).

## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 0.95 | Rogerson Crossing | Uxbridge | 0.47 m of water at peak; over 30 cm for 11.0 h; 30 cm reached 0.5 h into the storm; worst hour 22 mm (63% of the storm); a culvert within 100 m is overtopped |
| 2 | 0.31 | Millbury Street | Grafton | 0.25 m of water at peak; worst hour 8 mm (75% of the storm) |
| 3 | 0.31 | Rivulet Street | Uxbridge | 0.25 m of water at peak; worst hour 24 mm (67% of the storm); a culvert within 100 m is overtopped |
| 4 | 0.24 | Elm Street | Uxbridge | 0.23 m of water at peak; worst hour 24 mm (66% of the storm); a culvert within 100 m is overtopped |
| 5 | 0.21 | (unnamed) | Blackstone | 0.22 m of water at peak; worst hour 19 mm (66% of the storm); a culvert within 100 m is overtopped |
| 6 | 0.14 | Route 146 | Uxbridge | 0.19 m of water at peak; worst hour 13 mm (49% of the storm); a culvert within 100 m is overtopped |
| 7 | 0.10 | Hollis Street | Uxbridge | 0.17 m of water at peak; worst hour 22 mm (55% of the storm); a culvert within 100 m is overtopped |
| 8 | 0.06 | Pond Street | Milford | 0.14 m of water at peak; worst hour 16 mm (59% of the storm) |
| 9 | 0.05 | (unnamed) | Holliston | 0.13 m of water at peak; worst hour 14 mm (63% of the storm) |
| 10 | 0.04 | Cemetery Street | Mendon | 0.13 m of water at peak; worst hour 15 mm (51% of the storm) |
| 11 | 0.04 | (unnamed) | Hopedale | 0.13 m of water at peak; worst hour 18 mm (61% of the storm) |
| 12 | 0.04 | Quaker Highway | Uxbridge | 0.12 m of water at peak; worst hour 12 mm (44% of the storm) |
| 13 | 0.04 | West River Street | Upton | 0.12 m of water at peak; worst hour 15 mm (76% of the storm) |
| 14 | 0.03 | Pond Street | Uxbridge | 0.12 m of water at peak; worst hour 14 mm (53% of the storm); +8 min to the nearest hospital |
| 15 | 0.03 | Mellen Street | Milford | 0.12 m of water at peak; worst hour 14 mm (57% of the storm) |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
