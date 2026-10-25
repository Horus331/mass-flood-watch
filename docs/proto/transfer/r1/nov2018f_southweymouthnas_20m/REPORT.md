# Road-closure prototype: nov2018f_transfer_nov2018f_southweymouthnas_20m

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on CPU (OpenMP)), 20 m grid, storm from 2018-11-03T05:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 19,568 |
| Expected closures (sum of probabilities) | 33.7 |
| Segments with closure probability >= 50% | 3 (1.3 km) |
| Further segments that may close (stream reaches the road crest) | 0 (0.0 km) |
| Culverts overtopped / surcharged | 10 / 0 of 922 |
| Road segments cut off from hospitals | 0 |
| Worst added trip time to a hospital | 0.0 min |
| Heaviest hour of rain | 15.8 mm |
| Flood model run time | 1225 s |


## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 1.00 | Ramp | Braintree | 0.58 m of water at peak; over 30 cm for 7.0 h; 30 cm reached 11.5 h into the storm; worst hour 13 mm (40% of the storm); a culvert within 100 m is overtopped |
| 2 | 1.00 | Ramp | Braintree | 0.58 m of water at peak; over 30 cm for 7.0 h; 30 cm reached 11.5 h into the storm; worst hour 13 mm (40% of the storm); a culvert within 100 m is overtopped |
| 3 | 1.00 | Ramp | Braintree | 0.58 m of water at peak; over 30 cm for 7.0 h; 30 cm reached 11.5 h into the storm; worst hour 13 mm (40% of the storm); a culvert within 100 m is overtopped |
| 4 | 0.17 | Middle Street | Braintree | 0.20 m of water at peak; worst hour 14 mm (39% of the storm) |
| 5 | 0.17 | Middle Street | Braintree | 0.20 m of water at peak; worst hour 14 mm (40% of the storm); a culvert within 100 m is overtopped |
| 6 | 0.11 | Adams Street | Braintree | 0.18 m of water at peak; worst hour 14 mm (40% of the storm); a culvert within 100 m is overtopped |
| 7 | 0.11 | Adams Street | Braintree | 0.18 m of water at peak; worst hour 14 mm (39% of the storm) |
| 8 | 0.11 | Free Street | Hingham | 0.17 m of water at peak; worst hour 14 mm (40% of the storm); a culvert within 100 m is overtopped |
| 9 | 0.10 | McCusker Drive | Braintree | 0.17 m of water at peak; worst hour 14 mm (37% of the storm) |
| 10 | 0.10 | McCusker Drive | Braintree | 0.17 m of water at peak; worst hour 14 mm (37% of the storm) |
| 11 | 0.09 | Ellsworth Street | Brockton | 0.17 m of water at peak; worst hour 12 mm (40% of the storm); a culvert within 100 m is overtopped |
| 12 | 0.09 | Ellsworth Street | Brockton | 0.17 m of water at peak; worst hour 12 mm (40% of the storm) |
| 13 | 0.09 | Ellsworth Street | Brockton | 0.17 m of water at peak; worst hour 12 mm (40% of the storm); a culvert within 100 m is overtopped |
| 14 | 0.09 | Carleton Street | Brockton | 0.17 m of water at peak; worst hour 12 mm (40% of the storm); a culvert within 100 m is overtopped |
| 15 | 0.09 | Carleton Street | Brockton | 0.17 m of water at peak; worst hour 12 mm (40% of the storm); a culvert within 100 m is overtopped |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
