# Road-closure prototype: aug2018f_transfer_aug2018f_barnstable_20m

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on CPU (OpenMP)), 20 m grid, storm from 2018-08-04T15:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 9,686 |
| Expected closures (sum of probabilities) | 13.2 |
| Segments with closure probability >= 50% | 0 (0.0 km) |
| Further segments that may close (stream reaches the road crest) | 0 (0.0 km) |
| Culverts overtopped / surcharged | 0 / 0 of 200 |
| Road segments cut off from hospitals | 0 |
| Worst added trip time to a hospital | 0.0 min |
| Heaviest hour of rain | 18.2 mm |
| Flood model run time | 1628 s |


## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 0.02 | Route 6A | Barnstable | 0.09 m of water at peak; worst hour 7 mm (26% of the storm) |
| 2 | 0.02 | Reagan Avenue | Yarmouth | 0.09 m of water at peak; worst hour 8 mm (40% of the storm) |
| 3 | 0.01 | Buck Island Road | Yarmouth | 0.07 m of water at peak; worst hour 8 mm (41% of the storm) |
| 4 | 0.01 | Willow Street | Barnstable | 0.06 m of water at peak; worst hour 10 mm (34% of the storm) |
| 5 | 0.01 | Jefferson Avenue | Yarmouth | 0.06 m of water at peak; worst hour 9 mm (43% of the storm) |
| 6 | 0.01 | Winslow Gray Road | Yarmouth | 0.06 m of water at peak; worst hour 8 mm (47% of the storm) |
| 7 | 0.01 | Route 28 | Barnstable | 0.06 m of water at peak; worst hour 12 mm (46% of the storm) |
| 8 | 0.01 | Buck Island Road | Yarmouth | 0.06 m of water at peak; worst hour 9 mm (44% of the storm) |
| 9 | 0.01 | Horseshoe Lane | Barnstable | 0.05 m of water at peak; worst hour 12 mm (48% of the storm) |
| 10 | 0.01 | Route 6A | Barnstable | 0.04 m of water at peak; worst hour 11 mm (34% of the storm) |
| 11 | 0.01 | Thacher Street | Yarmouth | 0.04 m of water at peak; worst hour 12 mm (44% of the storm) |
| 12 | 0.00 | Nobscusset Road | Dennis | 0.04 m of water at peak; worst hour 13 mm (49% of the storm) |
| 13 | 0.00 | Weir Road | Yarmouth | 0.04 m of water at peak; worst hour 11 mm (45% of the storm) |
| 14 | 0.00 | Thacher Shore Road | Yarmouth | 0.04 m of water at peak; worst hour 11 mm (44% of the storm) |
| 15 | 0.00 | Hope Lane | Dennis | 0.03 m of water at peak; worst hour 13 mm (50% of the storm) |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
