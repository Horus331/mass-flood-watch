# Road-closure prototype: sep2019g_transfer_sep2019g_nnewinterscorner_20m

Flood model: LISFLOOD-FP 8.3 (acceleration (local inertial, Bates et al. 2010) on CPU (OpenMP)), 20 m grid, storm from 2019-09-02T17:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 14,685 |
| Expected closures (sum of probabilities) | 24.3 |
| Segments with closure probability >= 50% | 0 (0.0 km) |
| Further segments that may close (stream reaches the road crest) | 0 (0.0 km) |
| Culverts overtopped / surcharged | 8 / 0 of 827 |
| Road segments cut off from hospitals | 0 |
| Worst added trip time to a hospital | 0.0 min |
| Heaviest hour of rain | 29.1 mm |
| Flood model run time | 1204 s |


## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 0.44 | North Central Street | East Bridgewater | 0.29 m of water at peak; worst hour 14 mm (50% of the storm) |
| 2 | 0.44 | Pleasant Street | East Bridgewater | 0.29 m of water at peak; worst hour 14 mm (50% of the storm) |
| 3 | 0.18 | United Drive | West Bridgewater | 0.21 m of water at peak; worst hour 16 mm (62% of the storm); a culvert within 100 m is overtopped |
| 4 | 0.18 | Manley Street | West Bridgewater | 0.21 m of water at peak; worst hour 16 mm (62% of the storm); a culvert within 100 m is overtopped |
| 5 | 0.18 | Manley Street | West Bridgewater | 0.21 m of water at peak; worst hour 16 mm (62% of the storm); a culvert within 100 m is overtopped |
| 6 | 0.16 | South Street | Easton | 0.20 m of water at peak; worst hour 18 mm (76% of the storm); a culvert within 100 m is overtopped |
| 7 | 0.08 | Turnpike Street | Easton | 0.16 m of water at peak; worst hour 18 mm (70% of the storm); a culvert within 100 m is overtopped |
| 8 | 0.08 | Turnpike Street | Easton | 0.16 m of water at peak; worst hour 18 mm (70% of the storm) |
| 9 | 0.08 | Ellsworth Street | Brockton | 0.16 m of water at peak; worst hour 19 mm (81% of the storm); a culvert within 100 m is overtopped |
| 10 | 0.08 | Ellsworth Street | Brockton | 0.16 m of water at peak; worst hour 20 mm (81% of the storm); a culvert within 100 m is overtopped |
| 11 | 0.08 | Ellsworth Street | Brockton | 0.16 m of water at peak; worst hour 19 mm (81% of the storm) |
| 12 | 0.08 | Carleton Street | Brockton | 0.16 m of water at peak; worst hour 20 mm (81% of the storm); a culvert within 100 m is overtopped |
| 13 | 0.08 | Carleton Street | Brockton | 0.16 m of water at peak; worst hour 20 mm (81% of the storm); a culvert within 100 m is overtopped |
| 14 | 0.07 | Highland Street | Easton | 0.15 m of water at peak; worst hour 18 mm (76% of the storm); a culvert within 100 m is overtopped |
| 15 | 0.06 | Mill Street | Stoughton | 0.14 m of water at peak; worst hour 16 mm (91% of the storm) |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
