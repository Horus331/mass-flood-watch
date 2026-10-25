# Road-closure prototype: aug2018p_transfer_aug2018p_provincetown_20m

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on CPU (OpenMP)), 20 m grid, storm from 2018-08-18T14:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 1,055 |
| Expected closures (sum of probabilities) | 1.4 |
| Segments with closure probability >= 50% | 0 (0.0 km) |
| Further segments that may close (stream reaches the road crest) | 0 (0.0 km) |
| Culverts overtopped / surcharged | 0 / 0 of 11 |
| Road segments cut off from hospitals | 0 |
| Worst added trip time to a hospital | 0.0 min |
| Heaviest hour of rain | 19.2 mm |
| Flood model run time | 2638 s |


## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 0.00 | Old County Road | Truro | 0.04 m of water at peak; worst hour 16 mm (74% of the storm) |
| 2 | 0.00 | Old County Road | Truro | 0.02 m of water at peak; worst hour 19 mm (76% of the storm) |
| 3 | 0.00 | Mill Pond Road | Truro | 0.01 m of water at peak; worst hour 16 mm (73% of the storm) |
| 4 | 0.00 | Route 6 | Provincetown | 0.00 m of water at peak; worst hour 14 mm (48% of the storm) |
| 5 | 0.00 | Pond Road | Truro | 0.00 m of water at peak; worst hour 14 mm (53% of the storm) |
| 6 | 0.00 | Harry Kemp Way | Provincetown | 0.00 m of water at peak; worst hour 14 mm (52% of the storm) |
| 7 | 0.00 | Conwell Street | Provincetown | 0.00 m of water at peak; worst hour 14 mm (52% of the storm) |
| 8 | 0.00 | Priscilla Alden Road | Provincetown | 0.00 m of water at peak; worst hour 14 mm (52% of the storm) |
| 9 | 0.00 | Cook Street | Provincetown | 0.00 m of water at peak; worst hour 14 mm (50% of the storm) |
| 10 | 0.00 | Brewster Street | Provincetown | 0.00 m of water at peak; worst hour 14 mm (52% of the storm) |
| 11 | 0.00 | Route 6 | Provincetown | 0.00 m of water at peak; worst hour 14 mm (47% of the storm) |
| 12 | 0.00 | Route 6 | Provincetown | 0.00 m of water at peak; worst hour 14 mm (47% of the storm) |
| 13 | 0.00 | Mayflower Avenue | Provincetown | 0.00 m of water at peak; worst hour 13 mm (46% of the storm) |
| 14 | 0.00 | Pearl Street | Provincetown | 0.00 m of water at peak; worst hour 14 mm (52% of the storm) |
| 15 | 0.00 | Johnson Street | Provincetown | 0.00 m of water at peak; worst hour 14 mm (52% of the storm) |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
