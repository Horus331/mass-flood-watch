# Road-closure prototype: jan2018e_transfer_jan2018e_newbedford_20m

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on CPU (OpenMP)), 20 m grid, storm from 2018-01-12T18:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 10,199 |
| Expected closures (sum of probabilities) | 24.8 |
| Segments with closure probability >= 50% | 4 (2.0 km) |
| Further segments that may close (stream reaches the road crest) | 19 (3.9 km) |
| Culverts overtopped / surcharged | 19 / 0 of 482 |
| Road segments cut off from hospitals | 0 |
| Worst added trip time to a hospital | 0.0 min |
| Heaviest hour of rain | 16.0 mm |
| Flood model run time | 2621 s |


## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 0.99 | Reed Road | Westport | 0.53 m of water at peak; over 30 cm for 17.0 h; 30 cm reached 11.5 h into the storm; worst hour 13 mm (15% of the storm); a culvert within 100 m is overtopped |
| 2 | 0.85 | Union Avenue | Westport | 0.40 m of water at peak; over 30 cm for 11.5 h; 30 cm reached 17.0 h into the storm; worst hour 13 mm (15% of the storm); a culvert within 100 m is overtopped |
| 3 | 0.66 | Route 177 | Westport | 0.34 m of water at peak; over 30 cm for 5.5 h; 30 cm reached 16.5 h into the storm; worst hour 13 mm (15% of the storm); a culvert within 100 m is overtopped |
| 4 | 0.54 | Route 6 | Westport | 0.31 m of water at peak; over 30 cm for 2.5 h; 30 cm reached 18.0 h into the storm; worst hour 14 mm (16% of the storm); a culvert within 100 m is overtopped |
| 5 | 0.37 | Route 6 | Dartmouth | 0.27 m of water at peak; worst hour 12 mm (15% of the storm); a culvert within 100 m is overtopped |
| 6 | 0.29 | Drift Road | Westport | 0.24 m of water at peak; worst hour 12 mm (15% of the storm); a culvert within 100 m is overtopped |
| 7 | 0.29 | Drift Road | Westport | 0.24 m of water at peak; worst hour 12 mm (15% of the storm) |
| 8 | 0.26 | Old Bedford Road | Westport | 0.23 m of water at peak; worst hour 14 mm (15% of the storm); a culvert within 100 m is overtopped |
| 9 | 0.19 | Drift Road | Westport | 0.21 m of water at peak; worst hour 13 mm (15% of the storm); a culvert within 100 m is overtopped |
| 10 | 0.16 | Gifford Road | Westport | 0.20 m of water at peak; worst hour 14 mm (15% of the storm); a culvert within 100 m is overtopped |
| 11 | 0.15 | Flag Swamp Road | Dartmouth | 0.20 m of water at peak; worst hour 13 mm (14% of the storm) |
| 12 | 0.15 | Flag Swamp Road | Dartmouth | 0.20 m of water at peak; worst hour 13 mm (14% of the storm); water beside the road 0.49 m below its crest (design freeboard 0.30 m; P 0.10); a culvert within 100 m is overtopped |
| 13 | 0.14 | Mosher Street | New Bedford | 0.19 m of water at peak; worst hour 11 mm (16% of the storm); water beside the road 0.13 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.5 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 11 mm; catchment 6.6 ha) (P 0.15) |
| 14 | 0.13 | Chase Road | Dartmouth | 0.19 m of water at peak; worst hour 12 mm (16% of the storm); a culvert within 100 m is overtopped |
| 15 | 0.10 | Route 88 | Westport | 0.17 m of water at peak; worst hour 14 mm (16% of the storm); a culvert within 100 m is overtopped |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
