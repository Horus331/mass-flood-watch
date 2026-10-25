# Road-closure prototype: jun2020e_transfer_jun2020e_holbrook_20m

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on CPU (OpenMP)), 20 m grid, storm from 2020-06-21T13:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 18,230 |
| Expected closures (sum of probabilities) | 29.9 |
| Segments with closure probability >= 50% | 0 (0.0 km) |
| Further segments that may close (stream reaches the road crest) | 3 (0.3 km) |
| Culverts overtopped / surcharged | 7 / 0 of 979 |
| Road segments cut off from hospitals | 0 |
| Worst added trip time to a hospital | 0.0 min |
| Heaviest hour of rain | 43.1 mm |
| Flood model run time | 1025 s |


## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 0.22 | Ramp | Braintree | 0.22 m of water at peak; worst hour 6 mm (78% of the storm); a culvert within 100 m is overtopped |
| 2 | 0.22 | Ramp | Braintree | 0.22 m of water at peak; worst hour 6 mm (80% of the storm); a culvert within 100 m is overtopped |
| 3 | 0.22 | Ramp | Braintree | 0.22 m of water at peak; worst hour 6 mm (78% of the storm); a culvert within 100 m is overtopped |
| 4 | 0.17 | Middle Street | Braintree | 0.20 m of water at peak; worst hour 11 mm (87% of the storm) |
| 5 | 0.17 | Middle Street | Braintree | 0.20 m of water at peak; worst hour 10 mm (87% of the storm); a culvert within 100 m is overtopped |
| 6 | 0.11 | Adams Street | Braintree | 0.18 m of water at peak; worst hour 11 mm (89% of the storm); a culvert within 100 m is overtopped |
| 7 | 0.11 | Adams Street | Braintree | 0.18 m of water at peak; worst hour 11 mm (90% of the storm) |
| 8 | 0.10 | McCusker Drive | Braintree | 0.17 m of water at peak; worst hour 13 mm (92% of the storm) |
| 9 | 0.10 | McCusker Drive | Braintree | 0.17 m of water at peak; worst hour 14 mm (92% of the storm) |
| 10 | 0.09 | Condlin Drive | Randolph | 0.17 m of water at peak; worst hour 24 mm (78% of the storm); water beside the road 0.07 m above its crest (design freeboard 0.30 m; P 0.99) |
| 11 | 0.09 | Lori Lane | Randolph | 0.16 m of water at peak; worst hour 38 mm (79% of the storm); water beside the road 0.16 m below its crest (design freeboard 0.30 m; P 0.82); road sag 1.2 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 38 mm; catchment 8.8 ha) (P 0.26) |
| 12 | 0.09 | South Shore Road | Holbrook | 0.16 m of water at peak; worst hour 39 mm (73% of the storm); a culvert within 100 m is overtopped |
| 13 | 0.08 | Ellsworth Street | Brockton | 0.16 m of water at peak; worst hour 6 mm (97% of the storm); a culvert within 100 m is overtopped |
| 14 | 0.08 | Ellsworth Street | Brockton | 0.16 m of water at peak; worst hour 6 mm (97% of the storm) |
| 15 | 0.08 | Ellsworth Street | Brockton | 0.16 m of water at peak; worst hour 6 mm (97% of the storm); a culvert within 100 m is overtopped |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
