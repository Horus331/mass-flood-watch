# Road-closure prototype: jul2018g_transfer_jul2018g_lawrence_20m

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on CPU (OpenMP)), 20 m grid, storm from 2018-07-26T12:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 13,982 |
| Expected closures (sum of probabilities) | 20.7 |
| Segments with closure probability >= 50% | 0 (0.0 km) |
| Further segments that may close (stream reaches the road crest) | 0 (0.0 km) |
| Culverts overtopped / surcharged | 3 / 0 of 908 |
| Road segments cut off from hospitals | 0 |
| Worst added trip time to a hospital | 0.0 min |
| Heaviest hour of rain | 18.8 mm |
| Flood model run time | 1159 s |


## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 0.23 | Sutton Street | Lawrence | 0.23 m of water at peak; worst hour 8 mm (88% of the storm); a culvert within 100 m is overtopped |
| 2 | 0.16 | Sutton Street | Lawrence | 0.20 m of water at peak; worst hour 8 mm (88% of the storm); a culvert within 100 m is overtopped |
| 3 | 0.09 | West Lowell Avenue | Haverhill | 0.17 m of water at peak; worst hour 7 mm (87% of the storm) |
| 4 | 0.06 | Marblehead Street | Lawrence | 0.14 m of water at peak; worst hour 8 mm (88% of the storm); water beside the road 0.30 m below its crest (design freeboard 0.30 m; P 0.51); a culvert within 100 m is overtopped |
| 5 | 0.06 | Sutton Street | Lawrence | 0.14 m of water at peak; worst hour 8 mm (88% of the storm) |
| 6 | 0.06 | Merrimack Street | Lawrence | 0.14 m of water at peak; worst hour 8 mm (88% of the storm) |
| 7 | 0.05 | Essex Street | Haverhill | 0.14 m of water at peak; worst hour 5 mm (88% of the storm); water beside the road 0.31 m below its crest (design freeboard 0.30 m; P 0.46) |
| 8 | 0.05 | Essex Street | Haverhill | 0.14 m of water at peak; worst hour 5 mm (88% of the storm); water beside the road 0.31 m below its crest (design freeboard 0.30 m; P 0.46) |
| 9 | 0.04 | Route 125 | North Andover | 0.12 m of water at peak; worst hour 7 mm (90% of the storm) |
| 10 | 0.03 | Enmore Street | Andover | 0.11 m of water at peak; worst hour 5 mm (88% of the storm) |
| 11 | 0.03 | Enmore Street | Andover | 0.11 m of water at peak; worst hour 5 mm (88% of the storm) |
| 12 | 0.03 | Linwood Street | Andover | 0.11 m of water at peak; worst hour 5 mm (88% of the storm) |
| 13 | 0.02 | Research Drive | Haverhill | 0.09 m of water at peak; worst hour 6 mm (68% of the storm) |
| 14 | 0.01 | Curtis Street | Methuen | 0.08 m of water at peak; worst hour 13 mm (94% of the storm) |
| 15 | 0.01 | Bicknell Avenue | Methuen | 0.08 m of water at peak; worst hour 13 mm (94% of the storm) |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
