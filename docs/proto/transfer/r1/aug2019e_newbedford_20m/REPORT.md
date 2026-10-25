# Road-closure prototype: aug2019e_transfer_aug2019e_newbedford_20m

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on CPU (OpenMP)), 20 m grid, storm from 2019-08-04T15:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 10,312 |
| Expected closures (sum of probabilities) | 15.8 |
| Segments with closure probability >= 50% | 1 (0.0 km) |
| Further segments that may close (stream reaches the road crest) | 1 (0.7 km) |
| Culverts overtopped / surcharged | 6 / 0 of 482 |
| Road segments cut off from hospitals | 0 |
| Worst added trip time to a hospital | 0.0 min |
| Heaviest hour of rain | 20.7 mm |
| Flood model run time | 1018 s |


## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 0.60 | River Road | Mattapoisett | 0.33 m of water at peak; over 30 cm for 15.0 h; 30 cm reached 2.5 h into the storm; worst hour 5 mm (94% of the storm) |
| 2 | 0.29 | New Bedford Road | Rochester | 0.25 m of water at peak; worst hour 3 mm (80% of the storm); a culvert within 100 m is overtopped |
| 3 | 0.20 | Reed Road | Westport | 0.22 m of water at peak; worst hour 1 mm (67% of the storm); a culvert within 100 m is overtopped |
| 4 | 0.11 | Union Avenue | Westport | 0.18 m of water at peak; worst hour 1 mm (51% of the storm); a culvert within 100 m is overtopped |
| 5 | 0.11 | Route 105 | Rochester | 0.18 m of water at peak; worst hour 2 mm (64% of the storm); water beside the road 0.21 m below its crest (design freeboard 0.30 m; P 0.73); a culvert within 100 m is overtopped |
| 6 | 0.06 | Route 6 | Dartmouth | 0.15 m of water at peak; worst hour 6 mm (64% of the storm) |
| 7 | 0.03 | Acushnet Road | Mattapoisett | 0.12 m of water at peak; worst hour 4 mm (96% of the storm) |
| 8 | 0.02 | Elm Street | Dartmouth | 0.09 m of water at peak; worst hour 2 mm (99% of the storm) |
| 9 | 0.02 | Leonard Street | Acushnet | 0.09 m of water at peak; worst hour 3 mm (70% of the storm) |
| 10 | 0.01 | Route 105 | Rochester | 0.08 m of water at peak; worst hour 2 mm (60% of the storm) |
| 11 | 0.01 | Flag Swamp Road | Dartmouth | 0.08 m of water at peak; worst hour 10 mm (81% of the storm) |
| 12 | 0.01 | Flag Swamp Road | Dartmouth | 0.08 m of water at peak; worst hour 10 mm (81% of the storm) |
| 13 | 0.01 | (unnamed) | Rochester | 0.08 m of water at peak; worst hour 1 mm (76% of the storm) |
| 14 | 0.01 | Chase Road | Dartmouth | 0.07 m of water at peak; worst hour 2 mm (90% of the storm) |
| 15 | 0.01 | Milton Street | Dartmouth | 0.07 m of water at peak; worst hour 4 mm (94% of the storm) |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
