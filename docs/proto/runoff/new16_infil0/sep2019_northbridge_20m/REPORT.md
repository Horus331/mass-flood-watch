# Road-closure prototype: sep2019_loss_sep2019_northbridge_20m

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on CPU (OpenMP)), 20 m grid, storm from 2019-09-02T14:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 4,536 |
| Expected closures (sum of probabilities) | 11.7 |
| Segments with closure probability >= 50% | 2 (1.2 km) |
| Further segments that may close (stream reaches the road crest) | 1 (0.3 km) |
| Culverts overtopped / surcharged | 6 / 0 of 959 |
| Road segments cut off from hospitals | 25 |
| Worst added trip time to a hospital | 10.9 min |
| Heaviest hour of rain | 28.4 mm |
| Flood model run time | 1230 s |

## Checks against what happened

- Storm-day flood reports in the area: 2; water >= 10 cm within 100 m of 0% of them, vs 12% of random points (any day).
- Segments flagged impassable are 0.0x as likely as an average segment to have a report within 200 m.
- MassDOT repeating flood sites in the area: 6; 1 have a segment within 150 m at P >= 0.5 (share of all segments at P >= 0.5: 0.0%).

## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 0.99 | Route 122 | Northbridge | 0.52 m of water at peak; over 30 cm for 10.5 h; 30 cm reached 0.5 h into the storm; worst hour 12 mm (76% of the storm); a culvert within 100 m is overtopped |
| 2 | 0.93 | Rogerson Crossing | Uxbridge | 0.45 m of water at peak; over 30 cm for 11.5 h; 30 cm reached 0.5 h into the storm; worst hour 22 mm (63% of the storm); a culvert within 100 m is overtopped |
| 3 | 0.45 | Rivulet Street | Uxbridge | 0.29 m of water at peak; worst hour 24 mm (67% of the storm); a culvert within 100 m is overtopped |
| 4 | 0.30 | (unnamed) | Blackstone | 0.25 m of water at peak; worst hour 19 mm (66% of the storm); a culvert within 100 m is overtopped |
| 5 | 0.30 | Millbury Street | Grafton | 0.25 m of water at peak; worst hour 8 mm (75% of the storm) |
| 6 | 0.14 | Cemetery Street | Mendon | 0.19 m of water at peak; worst hour 15 mm (51% of the storm); a culvert within 100 m is overtopped |
| 7 | 0.09 | Bellingham Street | Mendon | 0.17 m of water at peak; worst hour 15 mm (54% of the storm); a culvert within 100 m is overtopped |
| 8 | 0.08 | (unnamed) | Holliston | 0.16 m of water at peak; worst hour 14 mm (63% of the storm) |
| 9 | 0.06 | Hartford Avenue East | Mendon | 0.15 m of water at peak; worst hour 14 mm (48% of the storm); +6 min to the nearest hospital |
| 10 | 0.06 | Route 146 | Uxbridge | 0.14 m of water at peak; worst hour 13 mm (49% of the storm); +8 min to the nearest hospital |
| 11 | 0.06 | Route 16 | Mendon | 0.14 m of water at peak; worst hour 19 mm (56% of the storm) |
| 12 | 0.05 | Pond Street | Uxbridge | 0.14 m of water at peak; worst hour 14 mm (53% of the storm); +11 min to the nearest hospital |
| 13 | 0.05 | Mill Street | Uxbridge | 0.14 m of water at peak; worst hour 13 mm (50% of the storm); +8 min to the nearest hospital |
| 14 | 0.05 | (unnamed) | Hopedale | 0.14 m of water at peak; worst hour 18 mm (61% of the storm) |
| 15 | 0.05 | Hopedale Street | Mendon | 0.13 m of water at peak; worst hour 23 mm (70% of the storm) |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
