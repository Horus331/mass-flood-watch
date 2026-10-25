# Road-closure prototype: aug2023k_transfer_aug2023k_wswcanton_20m

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on CPU (OpenMP)), 20 m grid, storm from 2023-08-18T07:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 24,184 |
| Expected closures (sum of probabilities) | 41.3 |
| Segments with closure probability >= 50% | 4 (1.4 km) |
| Further segments that may close (stream reaches the road crest) | 3 (0.4 km) |
| Culverts overtopped / surcharged | 12 / 0 of 710 |
| Road segments cut off from hospitals | 0 |
| Worst added trip time to a hospital | 0.0 min |
| Heaviest hour of rain | 36.1 mm |
| Flood model run time | 1209 s |


## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 1.00 | Route 1A | Westwood | 0.78 m of water at peak; over 30 cm for 9.5 h; 30 cm reached 9.0 h into the storm; worst hour 22 mm (67% of the storm); a culvert within 100 m is overtopped |
| 2 | 1.00 | Ramp | Braintree | 0.90 m of water at peak; over 30 cm for 7.5 h; 30 cm reached 11.0 h into the storm; worst hour 31 mm (68% of the storm); a culvert within 100 m is overtopped |
| 3 | 1.00 | Ramp | Braintree | 0.90 m of water at peak; over 30 cm for 7.5 h; 30 cm reached 11.0 h into the storm; worst hour 31 mm (68% of the storm); a culvert within 100 m is overtopped |
| 4 | 1.00 | Ramp | Braintree | 0.90 m of water at peak; over 30 cm for 7.5 h; 30 cm reached 11.0 h into the storm; worst hour 31 mm (68% of the storm); a culvert within 100 m is overtopped |
| 5 | 0.16 | Blue Hills Parkway | Milton | 0.20 m of water at peak; worst hour 28 mm (78% of the storm); a culvert within 100 m is overtopped |
| 6 | 0.16 | Blue Hills Parkway | Milton | 0.20 m of water at peak; worst hour 28 mm (77% of the storm); a culvert within 100 m is overtopped |
| 7 | 0.14 | Mill Street | Stoughton | 0.19 m of water at peak; worst hour 33 mm (92% of the storm); a culvert within 100 m is overtopped |
| 8 | 0.14 | Mill Street | Stoughton | 0.19 m of water at peak; worst hour 33 mm (92% of the storm) |
| 9 | 0.14 | Revolution Way | Canton | 0.19 m of water at peak; worst hour 26 mm (81% of the storm); water beside the road 0.03 m above its crest (design freeboard 0.30 m; P 0.99); road sag 0.3 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 26 mm; catchment 8.4 ha) (P 0.14) |
| 10 | 0.10 | Bolivar Street | Canton | 0.17 m of water at peak; worst hour 29 mm (82% of the storm) |
| 11 | 0.08 | Pond Street | Braintree | 0.16 m of water at peak; worst hour 32 mm (72% of the storm) |
| 12 | 0.07 | West Street | Braintree | 0.16 m of water at peak; worst hour 28 mm (67% of the storm); a culvert within 100 m is overtopped |
| 13 | 0.06 | Condlin Drive | Randolph | 0.15 m of water at peak; worst hour 33 mm (84% of the storm); water beside the road 0.05 m above its crest (design freeboard 0.30 m; P 0.99) |
| 14 | 0.06 | West Street | Braintree | 0.15 m of water at peak; worst hour 30 mm (67% of the storm); culvert (Unnamed trib to Farm River): headwater 6.08 m vs road crest 0.92 m, 0.5 m3/s |
| 15 | 0.06 | Thacher Street | Milton | 0.14 m of water at peak; worst hour 29 mm (81% of the storm) |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
