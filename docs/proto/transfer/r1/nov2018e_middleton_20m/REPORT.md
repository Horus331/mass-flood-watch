# Road-closure prototype: nov2018e_transfer_nov2018e_middleton_20m

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on CPU (OpenMP)), 20 m grid, storm from 2018-11-03T04:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 13,284 |
| Expected closures (sum of probabilities) | 20.7 |
| Segments with closure probability >= 50% | 0 (0.0 km) |
| Further segments that may close (stream reaches the road crest) | 1 (0.4 km) |
| Culverts overtopped / surcharged | 6 / 0 of 927 |
| Road segments cut off from hospitals | 0 |
| Worst added trip time to a hospital | 0.0 min |
| Heaviest hour of rain | 8.5 mm |
| Flood model run time | 869 s |


## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 0.23 | Sutton Street | Lawrence | 0.23 m of water at peak; worst hour 6 mm (17% of the storm); a culvert within 100 m is overtopped |
| 2 | 0.16 | Sutton Street | Lawrence | 0.20 m of water at peak; worst hour 6 mm (17% of the storm); a culvert within 100 m is overtopped |
| 3 | 0.13 | Lockwood Lane | Boxford | 0.19 m of water at peak; worst hour 7 mm (21% of the storm); a culvert within 100 m is overtopped |
| 4 | 0.13 | Lockwood Lane | Boxford | 0.19 m of water at peak; worst hour 7 mm (21% of the storm) |
| 5 | 0.08 | Route 125 | North Andover | 0.16 m of water at peak; worst hour 6 mm (18% of the storm); a culvert within 100 m is overtopped |
| 6 | 0.08 | Boston Street | Peabody | 0.16 m of water at peak; worst hour 8 mm (24% of the storm); a culvert within 100 m is overtopped |
| 7 | 0.08 | Boston Street | Peabody | 0.16 m of water at peak; worst hour 8 mm (24% of the storm) |
| 8 | 0.06 | Marblehead Street | Lawrence | 0.14 m of water at peak; worst hour 6 mm (17% of the storm); water beside the road 0.30 m below its crest (design freeboard 0.30 m; P 0.51); a culvert within 100 m is overtopped |
| 9 | 0.06 | Sutton Street | Lawrence | 0.14 m of water at peak; worst hour 6 mm (17% of the storm) |
| 10 | 0.06 | Merrimack Street | Lawrence | 0.14 m of water at peak; worst hour 6 mm (17% of the storm) |
| 11 | 0.06 | Middleton Road | Boxford | 0.14 m of water at peak; worst hour 6 mm (20% of the storm) |
| 12 | 0.06 | Middleton Road | Boxford | 0.14 m of water at peak; worst hour 6 mm (20% of the storm) |
| 13 | 0.06 | Enmore Street | Andover | 0.14 m of water at peak; worst hour 7 mm (21% of the storm) |
| 14 | 0.06 | Enmore Street | Andover | 0.14 m of water at peak; worst hour 7 mm (21% of the storm) |
| 15 | 0.06 | Linwood Street | Andover | 0.14 m of water at peak; worst hour 7 mm (21% of the storm) |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
