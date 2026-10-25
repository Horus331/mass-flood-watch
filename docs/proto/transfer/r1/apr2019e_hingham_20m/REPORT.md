# Road-closure prototype: apr2019e_transfer_apr2019e_hingham_20m

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on CPU (OpenMP)), 20 m grid, storm from 2019-04-15T04:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 12,105 |
| Expected closures (sum of probabilities) | 20.2 |
| Segments with closure probability >= 50% | 3 (1.3 km) |
| Further segments that may close (stream reaches the road crest) | 0 (0.0 km) |
| Culverts overtopped / surcharged | 8 / 0 of 473 |
| Road segments cut off from hospitals | 0 |
| Worst added trip time to a hospital | 0.0 min |
| Heaviest hour of rain | 15.5 mm |
| Flood model run time | 1711 s |


## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 0.61 | Ramp | Braintree | 0.33 m of water at peak; over 30 cm for 1.5 h; 30 cm reached 17.0 h into the storm; worst hour 10 mm (57% of the storm); a culvert within 100 m is overtopped |
| 2 | 0.61 | Ramp | Braintree | 0.33 m of water at peak; over 30 cm for 1.5 h; 30 cm reached 17.0 h into the storm; worst hour 10 mm (58% of the storm); a culvert within 100 m is overtopped |
| 3 | 0.61 | Ramp | Braintree | 0.33 m of water at peak; over 30 cm for 1.5 h; 30 cm reached 17.0 h into the storm; worst hour 10 mm (58% of the storm); a culvert within 100 m is overtopped |
| 4 | 0.17 | Middle Street | Braintree | 0.20 m of water at peak; worst hour 10 mm (62% of the storm) |
| 5 | 0.17 | Middle Street | Braintree | 0.20 m of water at peak; worst hour 10 mm (62% of the storm); a culvert within 100 m is overtopped |
| 6 | 0.11 | Adams Street | Braintree | 0.18 m of water at peak; worst hour 10 mm (62% of the storm); a culvert within 100 m is overtopped |
| 7 | 0.11 | Adams Street | Braintree | 0.18 m of water at peak; worst hour 10 mm (62% of the storm) |
| 8 | 0.10 | McCusker Drive | Braintree | 0.17 m of water at peak; worst hour 12 mm (69% of the storm) |
| 9 | 0.10 | McCusker Drive | Braintree | 0.17 m of water at peak; worst hour 12 mm (69% of the storm) |
| 10 | 0.10 | Henry Turner Bailey Road | Scituate | 0.17 m of water at peak; worst hour 10 mm (51% of the storm); a culvert within 100 m is overtopped |
| 11 | 0.09 | Leavitt Street | Hingham | 0.17 m of water at peak; worst hour 13 mm (60% of the storm); a culvert within 100 m is overtopped |
| 12 | 0.09 | Leavitt Street | Hingham | 0.17 m of water at peak; worst hour 13 mm (60% of the storm); a culvert within 100 m is overtopped |
| 13 | 0.07 | Free Street | Hingham | 0.15 m of water at peak; worst hour 11 mm (60% of the storm); a culvert within 100 m is overtopped |
| 14 | 0.06 | Arnold Street | Braintree | 0.15 m of water at peak; worst hour 11 mm (63% of the storm) |
| 15 | 0.06 | Adams Street | Braintree | 0.15 m of water at peak; worst hour 11 mm (64% of the storm) |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
