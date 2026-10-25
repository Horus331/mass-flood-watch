# Road-closure prototype: jul2019f_transfer_jul2019f_newbedford_20m

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on CPU (OpenMP)), 20 m grid, storm from 2019-07-12T03:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 10,321 |
| Expected closures (sum of probabilities) | 21.4 |
| Segments with closure probability >= 50% | 3 (1.1 km) |
| Further segments that may close (stream reaches the road crest) | 3 (0.8 km) |
| Culverts overtopped / surcharged | 16 / 0 of 460 |
| Road segments cut off from hospitals | 0 |
| Worst added trip time to a hospital | 0.0 min |
| Heaviest hour of rain | 38.3 mm |
| Flood model run time | 1957 s |


## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 0.97 | River Road | Mattapoisett | 0.49 m of water at peak; over 30 cm for 16.0 h; 30 cm reached 2.5 h into the storm; worst hour 31 mm (65% of the storm) |
| 2 | 0.61 | (unnamed) | Rochester | 0.33 m of water at peak; over 30 cm for 1.5 h; 30 cm reached 9.0 h into the storm; worst hour 26 mm (55% of the storm); a culvert within 100 m is overtopped |
| 3 | 0.57 | New Bedford Road | Rochester | 0.32 m of water at peak; over 30 cm for 1.5 h; 30 cm reached 9.0 h into the storm; worst hour 26 mm (52% of the storm); a culvert within 100 m is overtopped |
| 4 | 0.22 | Dexter Lane | Rochester | 0.22 m of water at peak; worst hour 26 mm (55% of the storm); a culvert within 100 m is overtopped |
| 5 | 0.22 | Route 6 | Dartmouth | 0.22 m of water at peak; worst hour 24 mm (51% of the storm); a culvert within 100 m is overtopped |
| 6 | 0.17 | Route 6 | Dartmouth | 0.21 m of water at peak; worst hour 25 mm (48% of the storm); a culvert within 100 m is overtopped |
| 7 | 0.17 | Route 6 | Dartmouth | 0.20 m of water at peak; worst hour 25 mm (48% of the storm); a culvert within 100 m is overtopped |
| 8 | 0.16 | Acushnet Road | Mattapoisett | 0.20 m of water at peak; worst hour 31 mm (65% of the storm); a culvert within 100 m is overtopped |
| 9 | 0.14 | Chase Road | Dartmouth | 0.19 m of water at peak; worst hour 24 mm (54% of the storm); a culvert within 100 m is overtopped |
| 10 | 0.11 | Flag Swamp Road | Dartmouth | 0.18 m of water at peak; worst hour 24 mm (43% of the storm) |
| 11 | 0.11 | Flag Swamp Road | Dartmouth | 0.18 m of water at peak; worst hour 24 mm (44% of the storm); a culvert within 100 m is overtopped |
| 12 | 0.11 | Route 105 | Rochester | 0.18 m of water at peak; worst hour 32 mm (51% of the storm); water beside the road 0.21 m below its crest (design freeboard 0.30 m; P 0.73); a culvert within 100 m is overtopped |
| 13 | 0.08 | Ramp | Dartmouth | 0.16 m of water at peak; worst hour 25 mm (46% of the storm); a culvert within 100 m is overtopped |
| 14 | 0.06 | Route 105 | Rochester | 0.14 m of water at peak; worst hour 35 mm (54% of the storm) |
| 15 | 0.06 | Leonard Street | Acushnet | 0.14 m of water at peak; worst hour 30 mm (53% of the storm) |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
