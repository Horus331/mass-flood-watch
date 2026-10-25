# Road-closure prototype: sep2018f_transfer_sep2018f_lawrence_20m

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on CPU (OpenMP)), 20 m grid, storm from 2018-09-18T07:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 11,876 |
| Expected closures (sum of probabilities) | 38.1 |
| Segments with closure probability >= 50% | 6 (1.0 km) |
| Further segments that may close (stream reaches the road crest) | 14 (2.0 km) |
| Culverts overtopped / surcharged | 46 / 1 of 1019 |
| Road segments cut off from hospitals | 0 |
| Worst added trip time to a hospital | 0.0 min |
| Heaviest hour of rain | 30.3 mm |
| Flood model run time | 1465 s |


## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 0.96 | Enmore Street | Andover | 0.47 m of water at peak; over 30 cm for 9.5 h; 30 cm reached 9.0 h into the storm; worst hour 16 mm (28% of the storm); a culvert within 100 m is overtopped |
| 2 | 0.96 | Enmore Street | Andover | 0.47 m of water at peak; over 30 cm for 9.5 h; 30 cm reached 9.0 h into the storm; worst hour 16 mm (27% of the storm) |
| 3 | 0.96 | Linwood Street | Andover | 0.47 m of water at peak; over 30 cm for 9.5 h; 30 cm reached 9.0 h into the storm; worst hour 16 mm (27% of the storm); a culvert within 100 m is overtopped |
| 4 | 0.59 | Route 125 | North Andover | 0.32 m of water at peak; over 30 cm for 5.5 h; 30 cm reached 10.0 h into the storm; worst hour 16 mm (27% of the storm); a culvert within 100 m is overtopped |
| 5 | 0.53 | River Road | Topsfield | 0.31 m of water at peak; over 30 cm for 1.5 h; 30 cm reached 10.5 h into the storm; worst hour 25 mm (42% of the storm); a culvert within 100 m is overtopped |
| 6 | 0.53 | Fuller Lane | Boxford | 0.31 m of water at peak; over 30 cm for 1.5 h; 30 cm reached 10.5 h into the storm; worst hour 25 mm (41% of the storm); a culvert within 100 m is overtopped |
| 7 | 0.45 | Whittier Court | Andover | 0.29 m of water at peak; worst hour 18 mm (30% of the storm); a culvert within 100 m is overtopped |
| 8 | 0.41 | Lockwood Lane | Boxford | 0.28 m of water at peak; worst hour 21 mm (36% of the storm); a culvert within 100 m is overtopped |
| 9 | 0.41 | Lockwood Lane | Boxford | 0.28 m of water at peak; worst hour 21 mm (36% of the storm) |
| 10 | 0.33 | Winter Street | Georgetown | 0.26 m of water at peak; worst hour 20 mm (30% of the storm); a culvert within 100 m is overtopped |
| 11 | 0.33 | Winter Street | Georgetown | 0.26 m of water at peak; worst hour 20 mm (30% of the storm); a culvert within 100 m is overtopped |
| 12 | 0.31 | Brookview Road | Boxford | 0.25 m of water at peak; worst hour 19 mm (30% of the storm); a culvert within 100 m is overtopped |
| 13 | 0.31 | Brookview Road | Boxford | 0.25 m of water at peak; worst hour 19 mm (30% of the storm) |
| 14 | 0.28 | Boston Street | Peabody | 0.24 m of water at peak; worst hour 23 mm (46% of the storm); a culvert within 100 m is overtopped |
| 15 | 0.28 | Boston Street | Peabody | 0.24 m of water at peak; worst hour 23 mm (46% of the storm) |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
