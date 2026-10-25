# Road-closure prototype: aug2018g_transfer_aug2018g_wellfleet_20m

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on CPU (OpenMP)), 20 m grid, storm from 2018-08-04T16:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 3,093 |
| Expected closures (sum of probabilities) | 4.2 |
| Segments with closure probability >= 50% | 0 (0.0 km) |
| Further segments that may close (stream reaches the road crest) | 0 (0.0 km) |
| Culverts overtopped / surcharged | 0 / 0 of 81 |
| Road segments cut off from hospitals | 0 |
| Worst added trip time to a hospital | 0.0 min |
| Heaviest hour of rain | 28.2 mm |
| Flood model run time | 2448 s |


## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 0.02 | Briar Lane | Wellfleet | 0.09 m of water at peak; worst hour 20 mm (40% of the storm) |
| 2 | 0.01 | Pole Dike Road | Wellfleet | 0.06 m of water at peak; worst hour 17 mm (38% of the storm) |
| 3 | 0.01 | Route 6 | Wellfleet | 0.05 m of water at peak; worst hour 20 mm (33% of the storm) |
| 4 | 0.01 | Governor Prence Road | Eastham | 0.04 m of water at peak; worst hour 23 mm (68% of the storm) |
| 5 | 0.01 | School House Hill Road | Wellfleet | 0.04 m of water at peak; worst hour 14 mm (34% of the storm) |
| 6 | 0.00 | Freedom Trail | Orleans | 0.03 m of water at peak; worst hour 19 mm (76% of the storm) |
| 7 | 0.00 | Liberty Lane | Orleans | 0.03 m of water at peak; worst hour 19 mm (76% of the storm) |
| 8 | 0.00 | Old County Road | Truro | 0.02 m of water at peak; worst hour 9 mm (30% of the storm) |
| 9 | 0.00 | Marconi Station Road | Wellfleet | 0.02 m of water at peak; worst hour 20 mm (33% of the storm) |
| 10 | 0.00 | West Road | Wellfleet | 0.02 m of water at peak; worst hour 19 mm (34% of the storm) |
| 11 | 0.00 | Old County Road | Truro | 0.01 m of water at peak; worst hour 7 mm (25% of the storm) |
| 12 | 0.00 | Cove Road | Wellfleet | 0.01 m of water at peak; worst hour 23 mm (39% of the storm) |
| 13 | 0.00 | Old County Road | Wellfleet | 0.01 m of water at peak; worst hour 11 mm (31% of the storm) |
| 14 | 0.00 | Gull Pond Road | Wellfleet | 0.01 m of water at peak; worst hour 18 mm (38% of the storm) |
| 15 | 0.00 | Chequessett Neck Road | Wellfleet | 0.01 m of water at peak; worst hour 17 mm (37% of the storm) |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
