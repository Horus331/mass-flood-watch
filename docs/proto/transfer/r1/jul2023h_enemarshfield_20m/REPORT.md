# Road-closure prototype: jul2023h_transfer_jul2023h_enemarshfield_20m

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on CPU (OpenMP)), 20 m grid, storm from 2023-07-16T17:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 4,746 |
| Expected closures (sum of probabilities) | 7.9 |
| Segments with closure probability >= 50% | 0 (0.0 km) |
| Further segments that may close (stream reaches the road crest) | 0 (0.0 km) |
| Culverts overtopped / surcharged | 4 / 0 of 233 |
| Road segments cut off from hospitals | 0 |
| Worst added trip time to a hospital | 0.0 min |
| Heaviest hour of rain | 27.6 mm |
| Flood model run time | 2343 s |


## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 0.24 | Route 139 | Marshfield | 0.23 m of water at peak; worst hour 13 mm (36% of the storm); a culvert within 100 m is overtopped |
| 2 | 0.10 | Old Ocean Street | Marshfield | 0.17 m of water at peak; worst hour 13 mm (36% of the storm); a culvert within 100 m is overtopped |
| 3 | 0.10 | Old Ocean Street | Marshfield | 0.17 m of water at peak; worst hour 13 mm (36% of the storm) |
| 4 | 0.07 | Route 3 | Duxbury | 0.16 m of water at peak; worst hour 15 mm (37% of the storm); a culvert within 100 m is overtopped |
| 5 | 0.07 | Harrison Street | Duxbury | 0.15 m of water at peak; worst hour 16 mm (41% of the storm); a culvert within 100 m is overtopped |
| 6 | 0.06 | Old Ocean Street | Marshfield | 0.14 m of water at peak; worst hour 14 mm (37% of the storm) |
| 7 | 0.06 | Old Ocean Street | Marshfield | 0.14 m of water at peak; worst hour 14 mm (37% of the storm) |
| 8 | 0.05 | Temple Street | Duxbury | 0.13 m of water at peak; worst hour 15 mm (38% of the storm) |
| 9 | 0.04 | Webster Street | Marshfield | 0.13 m of water at peak; worst hour 20 mm (49% of the storm) |
| 10 | 0.04 | Cross Street | Marshfield | 0.12 m of water at peak; worst hour 13 mm (36% of the storm) |
| 11 | 0.04 | Cross Street | Marshfield | 0.12 m of water at peak; worst hour 13 mm (36% of the storm) |
| 12 | 0.04 | Route 3A | Scituate | 0.12 m of water at peak; worst hour 19 mm (41% of the storm) |
| 13 | 0.03 | Route 3 | Duxbury | 0.11 m of water at peak; worst hour 15 mm (36% of the storm) |
| 14 | 0.03 | Pine Street | Duxbury | 0.11 m of water at peak; worst hour 15 mm (36% of the storm) |
| 15 | 0.02 | Birch Street | Pembroke | 0.10 m of water at peak; worst hour 14 mm (37% of the storm) |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
