# Road-closure prototype: may2020e_transfer_may2020e_oakbluffs_20m

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on CPU (OpenMP)), 20 m grid, storm from 2020-05-23T07:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 4,269 |
| Expected closures (sum of probabilities) | 5.9 |
| Segments with closure probability >= 50% | 0 (0.0 km) |
| Further segments that may close (stream reaches the road crest) | 0 (0.0 km) |
| Culverts overtopped / surcharged | 0 / 0 of 60 |
| Road segments cut off from hospitals | 0 |
| Worst added trip time to a hospital | 0.0 min |
| Heaviest hour of rain | 17.8 mm |
| Flood model run time | 1359 s |


## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 0.02 | Scotchmans Lane | West Tisbury | 0.09 m of water at peak; worst hour 8 mm (16% of the storm) |
| 2 | 0.01 | Stone Bridge Road | West Tisbury | 0.08 m of water at peak; worst hour 8 mm (16% of the storm) |
| 3 | 0.01 | Stone Bridge Road | West Tisbury | 0.08 m of water at peak; worst hour 8 mm (16% of the storm) |
| 4 | 0.01 | Blackwater Hollow Road | West Tisbury | 0.07 m of water at peak; worst hour 9 mm (17% of the storm) |
| 5 | 0.01 | Tiasquam Road | West Tisbury | 0.06 m of water at peak; worst hour 8 mm (17% of the storm) |
| 6 | 0.01 | Cottle Lane | West Tisbury | 0.06 m of water at peak; worst hour 9 mm (17% of the storm) |
| 7 | 0.01 | Tiahs Cove Road | West Tisbury | 0.04 m of water at peak; worst hour 8 mm (17% of the storm) |
| 8 | 0.01 | Lenssen Way | Edgartown | 0.04 m of water at peak; worst hour 8 mm (20% of the storm) |
| 9 | 0.01 | Tiahs Cove Road | West Tisbury | 0.04 m of water at peak; worst hour 7 mm (16% of the storm) |
| 10 | 0.01 | Farm Road | Tisbury | 0.04 m of water at peak; worst hour 8 mm (18% of the storm) |
| 11 | 0.00 | Scrubby Neck Road | West Tisbury | 0.03 m of water at peak; worst hour 8 mm (18% of the storm) |
| 12 | 0.00 | Butlers Pond Road | West Tisbury | 0.03 m of water at peak; worst hour 8 mm (18% of the storm) |
| 13 | 0.00 | John Presbury Norton Farm Road | West Tisbury | 0.03 m of water at peak; worst hour 12 mm (22% of the storm) |
| 14 | 0.00 | Black Brook Crossing | West Tisbury | 0.02 m of water at peak; worst hour 9 mm (17% of the storm) |
| 15 | 0.00 | Brook Hollow Road | West Tisbury | 0.02 m of water at peak; worst hour 8 mm (17% of the storm) |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
