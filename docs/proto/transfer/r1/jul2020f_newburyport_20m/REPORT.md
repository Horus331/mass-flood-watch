# Road-closure prototype: jul2020f_transfer_jul2020f_newburyport_20m

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on CPU (OpenMP)), 20 m grid, storm from 2020-07-23T12:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 4,407 |
| Expected closures (sum of probabilities) | 7.9 |
| Segments with closure probability >= 50% | 0 (0.0 km) |
| Further segments that may close (stream reaches the road crest) | 0 (0.0 km) |
| Culverts overtopped / surcharged | 2 / 0 of 453 |
| Road segments cut off from hospitals | 0 |
| Worst added trip time to a hospital | 0.0 min |
| Heaviest hour of rain | 30.7 mm |
| Flood model run time | 1190 s |


## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 0.21 | Glen Street | Rowley | 0.22 m of water at peak; worst hour 17 mm (55% of the storm); a culvert within 100 m is overtopped |
| 2 | 0.20 | Glen Street | Rowley | 0.21 m of water at peak; worst hour 17 mm (55% of the storm) |
| 3 | 0.20 | Glen Street | Rowley | 0.21 m of water at peak; worst hour 17 mm (55% of the storm); a culvert within 100 m is overtopped |
| 4 | 0.15 | Route 1 | Rowley | 0.20 m of water at peak; worst hour 16 mm (54% of the storm); a culvert within 100 m is overtopped |
| 5 | 0.06 | Larkin Road | Newbury | 0.15 m of water at peak; worst hour 28 mm (59% of the storm) |
| 6 | 0.06 | Boston Road | Newbury | 0.14 m of water at peak; worst hour 26 mm (50% of the storm) |
| 7 | 0.05 | Indian Hill Street | West Newbury | 0.14 m of water at peak; worst hour 25 mm (54% of the storm) |
| 8 | 0.04 | School Street | Rowley | 0.12 m of water at peak; worst hour 13 mm (51% of the storm) |
| 9 | 0.04 | School Street | Newbury | 0.12 m of water at peak; worst hour 24 mm (56% of the storm) |
| 10 | 0.04 | Green Street | Newbury | 0.12 m of water at peak; worst hour 26 mm (50% of the storm) |
| 11 | 0.03 | Central Street | Rowley | 0.12 m of water at peak; worst hour 13 mm (51% of the storm) |
| 12 | 0.03 | Central Street | Rowley | 0.12 m of water at peak; worst hour 13 mm (51% of the storm) |
| 13 | 0.03 | Church Street | Rowley | 0.12 m of water at peak; worst hour 13 mm (51% of the storm) |
| 14 | 0.03 | Meadowview Road | Georgetown | 0.11 m of water at peak; worst hour 30 mm (56% of the storm) |
| 15 | 0.03 | Scotland Road | Newbury | 0.11 m of water at peak; worst hour 26 mm (55% of the storm) |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
