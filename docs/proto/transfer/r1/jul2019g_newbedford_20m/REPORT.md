# Road-closure prototype: jul2019g_transfer_jul2019g_newbedford_20m

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on CPU (OpenMP)), 20 m grid, storm from 2019-07-22T18:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 10,297 |
| Expected closures (sum of probabilities) | 16.6 |
| Segments with closure probability >= 50% | 1 (0.0 km) |
| Further segments that may close (stream reaches the road crest) | 1 (0.7 km) |
| Culverts overtopped / surcharged | 7 / 0 of 470 |
| Road segments cut off from hospitals | 0 |
| Worst added trip time to a hospital | 0.0 min |
| Heaviest hour of rain | 26.5 mm |
| Flood model run time | 1950 s |


## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 0.79 | River Road | Mattapoisett | 0.38 m of water at peak; over 30 cm for 16.0 h; 30 cm reached 2.5 h into the storm; worst hour 18 mm (91% of the storm) |
| 2 | 0.30 | New Bedford Road | Rochester | 0.25 m of water at peak; worst hour 21 mm (89% of the storm); a culvert within 100 m is overtopped |
| 3 | 0.21 | (unnamed) | Rochester | 0.22 m of water at peak; worst hour 20 mm (89% of the storm); a culvert within 100 m is overtopped |
| 4 | 0.11 | Route 105 | Rochester | 0.18 m of water at peak; worst hour 18 mm (84% of the storm); water beside the road 0.21 m below its crest (design freeboard 0.30 m; P 0.73); a culvert within 100 m is overtopped |
| 5 | 0.09 | Acushnet Road | Mattapoisett | 0.17 m of water at peak; worst hour 21 mm (92% of the storm); a culvert within 100 m is overtopped |
| 6 | 0.06 | Route 6 | Dartmouth | 0.15 m of water at peak; worst hour 22 mm (90% of the storm) |
| 7 | 0.05 | Dexter Lane | Rochester | 0.14 m of water at peak; worst hour 20 mm (89% of the storm) |
| 8 | 0.05 | Manchester Lane | Acushnet | 0.13 m of water at peak; worst hour 25 mm (91% of the storm) |
| 9 | 0.04 | Route 105 | Marion | 0.12 m of water at peak; worst hour 20 mm (88% of the storm) |
| 10 | 0.03 | Hartley Road | Rochester | 0.12 m of water at peak; worst hour 17 mm (80% of the storm) |
| 11 | 0.02 | Route 6 | Fairhaven | 0.10 m of water at peak; worst hour 25 mm (94% of the storm) |
| 12 | 0.02 | Leonard Street | Acushnet | 0.10 m of water at peak; worst hour 22 mm (88% of the storm) |
| 13 | 0.02 | Elm Street | Dartmouth | 0.09 m of water at peak; worst hour 21 mm (90% of the storm) |
| 14 | 0.02 | Flag Swamp Road | Dartmouth | 0.09 m of water at peak; worst hour 18 mm (79% of the storm) |
| 15 | 0.02 | Flag Swamp Road | Dartmouth | 0.09 m of water at peak; worst hour 18 mm (79% of the storm) |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
