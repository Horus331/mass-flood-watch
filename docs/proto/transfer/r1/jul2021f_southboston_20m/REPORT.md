# Road-closure prototype: jul2021f_transfer_jul2021f_southboston_20m

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on CPU (OpenMP)), 20 m grid, storm from 2021-07-03T15:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 40,968 |
| Expected closures (sum of probabilities) | 59.7 |
| Segments with closure probability >= 50% | 0 (0.0 km) |
| Further segments that may close (stream reaches the road crest) | 3 (2.9 km) |
| Culverts overtopped / surcharged | 5 / 0 of 356 |
| Road segments cut off from hospitals | 0 |
| Worst added trip time to a hospital | 0.0 min |
| Heaviest hour of rain | 23.9 mm |
| Flood model run time | 1564 s |


## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 0.15 | Blue Hills Parkway | Milton | 0.20 m of water at peak; worst hour 15 mm (26% of the storm); a culvert within 100 m is overtopped |
| 2 | 0.15 | Blue Hills Parkway | Milton | 0.20 m of water at peak; worst hour 14 mm (25% of the storm); a culvert within 100 m is overtopped |
| 3 | 0.11 | Middle Street | Braintree | 0.18 m of water at peak; worst hour 8 mm (19% of the storm) |
| 4 | 0.11 | Middle Street | Braintree | 0.18 m of water at peak; worst hour 8 mm (19% of the storm); a culvert within 100 m is overtopped |
| 5 | 0.09 | Thacher Street | Milton | 0.17 m of water at peak; worst hour 12 mm (22% of the storm) |
| 6 | 0.09 | Thacher Street | Milton | 0.17 m of water at peak; worst hour 12 mm (22% of the storm) |
| 7 | 0.08 | Adams Street | Braintree | 0.16 m of water at peak; worst hour 8 mm (19% of the storm); a culvert within 100 m is overtopped |
| 8 | 0.08 | Adams Street | Braintree | 0.16 m of water at peak; worst hour 8 mm (19% of the storm) |
| 9 | 0.07 | Canton Avenue | Milton | 0.15 m of water at peak; worst hour 15 mm (26% of the storm); a culvert within 100 m is overtopped |
| 10 | 0.07 | Canton Avenue | Milton | 0.15 m of water at peak; worst hour 15 mm (26% of the storm); a culvert within 100 m is overtopped |
| 11 | 0.05 | Arnold Street | Braintree | 0.14 m of water at peak; worst hour 8 mm (19% of the storm) |
| 12 | 0.05 | Adams Street | Braintree | 0.14 m of water at peak; worst hour 8 mm (19% of the storm) |
| 13 | 0.05 | Adams Street | Braintree | 0.14 m of water at peak; worst hour 8 mm (19% of the storm) |
| 14 | 0.05 | Otis Street | Milton | 0.14 m of water at peak; worst hour 11 mm (18% of the storm) |
| 15 | 0.04 | Harland Street | Milton | 0.13 m of water at peak; worst hour 17 mm (28% of the storm) |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
