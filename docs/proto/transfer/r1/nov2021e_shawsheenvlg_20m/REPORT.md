# Road-closure prototype: nov2021e_transfer_nov2021e_shawsheenvlg_20m

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on CPU (OpenMP)), 20 m grid, storm from 2021-11-12T14:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 12,282 |
| Expected closures (sum of probabilities) | 22.9 |
| Segments with closure probability >= 50% | 0 (0.0 km) |
| Further segments that may close (stream reaches the road crest) | 0 (0.0 km) |
| Culverts overtopped / surcharged | 9 / 0 of 1053 |
| Road segments cut off from hospitals | 0 |
| Worst added trip time to a hospital | 0.0 min |
| Heaviest hour of rain | 28.7 mm |
| Flood model run time | 1266 s |


## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 0.30 | River Road | Topsfield | 0.25 m of water at peak; worst hour 15 mm (39% of the storm); a culvert within 100 m is overtopped |
| 2 | 0.30 | Fuller Lane | Boxford | 0.25 m of water at peak; worst hour 15 mm (39% of the storm); a culvert within 100 m is overtopped |
| 3 | 0.24 | Lockwood Lane | Boxford | 0.23 m of water at peak; worst hour 12 mm (36% of the storm); a culvert within 100 m is overtopped |
| 4 | 0.24 | Lockwood Lane | Boxford | 0.23 m of water at peak; worst hour 12 mm (36% of the storm) |
| 5 | 0.23 | Sutton Street | Lawrence | 0.23 m of water at peak; worst hour 23 mm (64% of the storm); a culvert within 100 m is overtopped |
| 6 | 0.17 | Enmore Street | Andover | 0.20 m of water at peak; worst hour 19 mm (56% of the storm); a culvert within 100 m is overtopped |
| 7 | 0.17 | Enmore Street | Andover | 0.20 m of water at peak; worst hour 19 mm (56% of the storm) |
| 8 | 0.17 | Linwood Street | Andover | 0.20 m of water at peak; worst hour 19 mm (55% of the storm); a culvert within 100 m is overtopped |
| 9 | 0.16 | Sutton Street | Lawrence | 0.20 m of water at peak; worst hour 23 mm (64% of the storm); a culvert within 100 m is overtopped |
| 10 | 0.16 | Route 125 | North Andover | 0.20 m of water at peak; worst hour 21 mm (59% of the storm); a culvert within 100 m is overtopped |
| 11 | 0.12 | Pinnacle Street | Tewksbury | 0.18 m of water at peak; worst hour 16 mm (53% of the storm) |
| 12 | 0.09 | Morrow Lane | Groveland | 0.17 m of water at peak; worst hour 22 mm (57% of the storm); a culvert within 100 m is overtopped |
| 13 | 0.06 | Marblehead Street | Lawrence | 0.14 m of water at peak; worst hour 23 mm (64% of the storm); water beside the road 0.30 m below its crest (design freeboard 0.30 m; P 0.51); a culvert within 100 m is overtopped |
| 14 | 0.06 | Sutton Street | Lawrence | 0.14 m of water at peak; worst hour 23 mm (64% of the storm) |
| 15 | 0.06 | Merrimack Street | Lawrence | 0.14 m of water at peak; worst hour 23 mm (64% of the storm) |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
