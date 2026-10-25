# Road-closure prototype: aug2018h_transfer_aug2018h_orleans_20m

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on CPU (OpenMP)), 20 m grid, storm from 2018-08-09T06:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 5,332 |
| Expected closures (sum of probabilities) | 9.3 |
| Segments with closure probability >= 50% | 0 (0.0 km) |
| Further segments that may close (stream reaches the road crest) | 1 (0.2 km) |
| Culverts overtopped / surcharged | 3 / 0 of 103 |
| Road segments cut off from hospitals | 0 |
| Worst added trip time to a hospital | 0.0 min |
| Heaviest hour of rain | 43.7 mm |
| Flood model run time | 1681 s |


## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 0.49 | Breakwater Road | Brewster | 0.30 m of water at peak; worst hour 39 mm (39% of the storm); a culvert within 100 m is overtopped |
| 2 | 0.48 | The Channel Way | Brewster | 0.29 m of water at peak; worst hour 39 mm (39% of the storm); a culvert within 100 m is overtopped |
| 3 | 0.06 | Brier Lane | Brewster | 0.14 m of water at peak; worst hour 32 mm (36% of the storm) |
| 4 | 0.05 | Azalea Drive | Harwich | 0.14 m of water at peak; worst hour 15 mm (39% of the storm) |
| 5 | 0.05 | Azalea Drive | Harwich | 0.14 m of water at peak; worst hour 15 mm (39% of the storm) |
| 6 | 0.04 | Bickford Path | Brewster | 0.13 m of water at peak; worst hour 42 mm (42% of the storm); runoff beside / along the road at 0.6 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.19) |
| 7 | 0.03 | Freedom Trail | Orleans | 0.12 m of water at peak; worst hour 41 mm (51% of the storm); water beside the road 0.01 m below its crest (design freeboard 0.30 m; P 0.97) |
| 8 | 0.03 | Liberty Lane | Orleans | 0.12 m of water at peak; worst hour 41 mm (51% of the storm); water beside the road 0.01 m below its crest (design freeboard 0.30 m; P 0.97) |
| 9 | 0.02 | Namequoit Road | Orleans | 0.10 m of water at peak; worst hour 25 mm (45% of the storm) |
| 10 | 0.02 | Namequoit Road | Orleans | 0.10 m of water at peak; worst hour 25 mm (45% of the storm) |
| 11 | 0.02 | Spring Lane | Brewster | 0.10 m of water at peak; worst hour 32 mm (36% of the storm) |
| 12 | 0.02 | Cottonwood Drive | Brewster | 0.10 m of water at peak; worst hour 40 mm (41% of the storm) |
| 13 | 0.02 | Route 6A | Brewster | 0.10 m of water at peak; worst hour 30 mm (37% of the storm) |
| 14 | 0.02 | Robbins Hill Road | Brewster | 0.09 m of water at peak; worst hour 33 mm (39% of the storm) |
| 15 | 0.02 | Governor Prence Road | Eastham | 0.09 m of water at peak; worst hour 30 mm (49% of the storm) |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
