# Road-closure prototype: jul2020e_transfer_jul2020e_lawrence_20m

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on CPU (OpenMP)), 20 m grid, storm from 2020-07-23T12:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 13,553 |
| Expected closures (sum of probabilities) | 23.4 |
| Segments with closure probability >= 50% | 0 (0.0 km) |
| Further segments that may close (stream reaches the road crest) | 0 (0.0 km) |
| Culverts overtopped / surcharged | 11 / 0 of 967 |
| Road segments cut off from hospitals | 0 |
| Worst added trip time to a hospital | 0.0 min |
| Heaviest hour of rain | 35.5 mm |
| Flood model run time | 1286 s |


## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 0.29 | Morrow Lane | Groveland | 0.24 m of water at peak; worst hour 24 mm (49% of the storm); a culvert within 100 m is overtopped |
| 2 | 0.23 | Sutton Street | Lawrence | 0.23 m of water at peak; worst hour 19 mm (54% of the storm); a culvert within 100 m is overtopped |
| 3 | 0.18 | Route 125 | North Andover | 0.21 m of water at peak; worst hour 20 mm (56% of the storm); a culvert within 100 m is overtopped |
| 4 | 0.16 | Sutton Street | Lawrence | 0.20 m of water at peak; worst hour 19 mm (54% of the storm); a culvert within 100 m is overtopped |
| 5 | 0.10 | Route 97 | Groveland | 0.17 m of water at peak; worst hour 24 mm (50% of the storm); a culvert within 100 m is overtopped |
| 6 | 0.10 | Center Street | Groveland | 0.17 m of water at peak; worst hour 24 mm (50% of the storm); a culvert within 100 m is overtopped |
| 7 | 0.09 | West Lowell Avenue | Haverhill | 0.17 m of water at peak; worst hour 7 mm (49% of the storm) |
| 8 | 0.08 | Pandora Drive | Groveland | 0.16 m of water at peak; worst hour 25 mm (50% of the storm) |
| 9 | 0.08 | Johnson Street | North Andover | 0.16 m of water at peak; worst hour 22 mm (55% of the storm); a culvert within 100 m is overtopped |
| 10 | 0.07 | Enmore Street | Andover | 0.16 m of water at peak; worst hour 21 mm (74% of the storm); a culvert within 100 m is overtopped |
| 11 | 0.07 | Enmore Street | Andover | 0.16 m of water at peak; worst hour 21 mm (76% of the storm) |
| 12 | 0.07 | Linwood Street | Andover | 0.16 m of water at peak; worst hour 20 mm (74% of the storm); a culvert within 100 m is overtopped |
| 13 | 0.07 | Whittier Court | Andover | 0.15 m of water at peak; worst hour 19 mm (60% of the storm); a culvert within 100 m is overtopped |
| 14 | 0.07 | Main Street | Groveland | 0.15 m of water at peak; worst hour 22 mm (52% of the storm) |
| 15 | 0.07 | Morton Street | Andover | 0.15 m of water at peak; worst hour 18 mm (56% of the storm); a culvert within 100 m is overtopped |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
