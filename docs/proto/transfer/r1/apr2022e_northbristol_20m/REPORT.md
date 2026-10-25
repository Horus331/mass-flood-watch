# Road-closure prototype: apr2022e_transfer_apr2022e_northbristol_20m

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on CPU (OpenMP)), 20 m grid, storm from 2022-04-08T02:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 10,360 |
| Expected closures (sum of probabilities) | 17.5 |
| Segments with closure probability >= 50% | 1 (0.0 km) |
| Further segments that may close (stream reaches the road crest) | 1 (0.7 km) |
| Culverts overtopped / surcharged | 9 / 0 of 489 |
| Road segments cut off from hospitals | 0 |
| Worst added trip time to a hospital | 0.0 min |
| Heaviest hour of rain | 23.7 mm |
| Flood model run time | 1395 s |


## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 0.88 | River Road | Mattapoisett | 0.41 m of water at peak; over 30 cm for 16.0 h; 30 cm reached 2.5 h into the storm; worst hour 17 mm (54% of the storm) |
| 2 | 0.47 | New Bedford Road | Rochester | 0.29 m of water at peak; worst hour 17 mm (53% of the storm); a culvert within 100 m is overtopped |
| 3 | 0.39 | (unnamed) | Rochester | 0.27 m of water at peak; worst hour 19 mm (56% of the storm); a culvert within 100 m is overtopped |
| 4 | 0.16 | Route 105 | Rochester | 0.20 m of water at peak; worst hour 18 mm (60% of the storm); water beside the road 0.21 m below its crest (design freeboard 0.30 m; P 0.73); a culvert within 100 m is overtopped |
| 5 | 0.13 | Acushnet Road | Mattapoisett | 0.19 m of water at peak; worst hour 19 mm (55% of the storm); a culvert within 100 m is overtopped |
| 6 | 0.11 | Dexter Lane | Rochester | 0.18 m of water at peak; worst hour 19 mm (55% of the storm); a culvert within 100 m is overtopped |
| 7 | 0.06 | Route 6 | Dartmouth | 0.15 m of water at peak; worst hour 17 mm (59% of the storm) |
| 8 | 0.04 | Route 105 | Rochester | 0.13 m of water at peak; worst hour 20 mm (58% of the storm) |
| 9 | 0.04 | Manchester Lane | Acushnet | 0.12 m of water at peak; worst hour 15 mm (45% of the storm) |
| 10 | 0.04 | Hartley Road | Rochester | 0.12 m of water at peak; worst hour 19 mm (62% of the storm) |
| 11 | 0.03 | Purchase Street | New Bedford | 0.11 m of water at peak; worst hour 19 mm (56% of the storm); water beside the road 0.08 m below its crest (design freeboard 0.30 m; P 0.93) |
| 12 | 0.03 | Purchase Street | New Bedford | 0.11 m of water at peak; worst hour 16 mm (52% of the storm); runoff beside / along the road at 1.5 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.32) |
| 13 | 0.03 | Deane Street | New Bedford | 0.11 m of water at peak; worst hour 19 mm (56% of the storm); water beside the road 0.08 m below its crest (design freeboard 0.30 m; P 0.93) |
| 14 | 0.02 | Leonard Street | Acushnet | 0.10 m of water at peak; worst hour 19 mm (53% of the storm) |
| 15 | 0.02 | Elm Street | Dartmouth | 0.09 m of water at peak; worst hour 16 mm (60% of the storm) |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
