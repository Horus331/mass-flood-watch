# Road-closure prototype: jul2023e_transfer_jul2023e_swansea_20m

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on CPU (OpenMP)), 20 m grid, storm from 2023-07-04T12:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 4,856 |
| Expected closures (sum of probabilities) | 14.7 |
| Segments with closure probability >= 50% | 4 (0.8 km) |
| Further segments that may close (stream reaches the road crest) | 2 (0.6 km) |
| Culverts overtopped / surcharged | 24 / 0 of 412 |
| Road segments cut off from hospitals | 0 |
| Worst added trip time to a hospital | 0.0 min |
| Heaviest hour of rain | 46.2 mm |
| Flood model run time | 1211 s |


## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 0.81 | Wilmarth Bridge Road | Rehoboth | 0.39 m of water at peak; over 30 cm for 8.5 h; 30 cm reached 10.0 h into the storm; worst hour 32 mm (66% of the storm) |
| 2 | 0.81 | Wilmarth Bridge Road | Rehoboth | 0.39 m of water at peak; over 30 cm for 8.5 h; 30 cm reached 10.0 h into the storm; worst hour 32 mm (66% of the storm) |
| 3 | 0.80 | Route 152 | Seekonk | 0.38 m of water at peak; over 30 cm for 6.5 h; 30 cm reached 9.0 h into the storm; worst hour 28 mm (46% of the storm); a culvert within 100 m is overtopped |
| 4 | 0.63 | Tompson Drive | Seekonk | 0.33 m of water at peak; over 30 cm for 4.0 h; 30 cm reached 8.5 h into the storm; worst hour 28 mm (46% of the storm); a culvert within 100 m is overtopped |
| 5 | 0.24 | Greenwood Avenue | Seekonk | 0.23 m of water at peak; worst hour 27 mm (55% of the storm); a culvert within 100 m is overtopped |
| 6 | 0.21 | Colletti Lane | Swansea | 0.22 m of water at peak; worst hour 41 mm (80% of the storm); a culvert within 100 m is overtopped |
| 7 | 0.21 | River Street | Rehoboth | 0.22 m of water at peak; worst hour 36 mm (68% of the storm) |
| 8 | 0.18 | Pond Street | Rehoboth | 0.21 m of water at peak; worst hour 35 mm (68% of the storm); a culvert within 100 m is overtopped |
| 9 | 0.15 | Brown Avenue | Seekonk | 0.20 m of water at peak; worst hour 28 mm (45% of the storm); a culvert within 100 m is overtopped |
| 10 | 0.14 | Blanding Road | Rehoboth | 0.19 m of water at peak; worst hour 32 mm (65% of the storm); a culvert within 100 m is overtopped |
| 11 | 0.14 | Ledge Road | Seekonk | 0.19 m of water at peak; worst hour 27 mm (55% of the storm); a culvert within 100 m is overtopped |
| 12 | 0.13 | Hope Street | Seekonk | 0.19 m of water at peak; worst hour 25 mm (52% of the storm); a culvert within 100 m is overtopped |
| 13 | 0.12 | Barney Avenue | Rehoboth | 0.18 m of water at peak; worst hour 35 mm (74% of the storm); a culvert within 100 m is overtopped |
| 14 | 0.11 | Route 118 | Rehoboth | 0.17 m of water at peak; worst hour 36 mm (71% of the storm); a culvert within 100 m is overtopped |
| 15 | 0.11 | Route 118 | Rehoboth | 0.17 m of water at peak; worst hour 36 mm (70% of the storm) |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
