# Road-closure prototype: jul2023p_transfer_jul2023p_sswboston_20m

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on CPU (OpenMP)), 20 m grid, storm from 2023-07-25T12:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 35,592 |
| Expected closures (sum of probabilities) | 78.7 |
| Segments with closure probability >= 50% | 23 (3.4 km) |
| Further segments that may close (stream reaches the road crest) | 37 (4.7 km) |
| Culverts overtopped / surcharged | 24 / 0 of 563 |
| Road segments cut off from hospitals | 0 |
| Worst added trip time to a hospital | 0.0 min |
| Heaviest hour of rain | 27.8 mm |
| Flood model run time | 1438 s |


## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 1.00 | Route 1A | Westwood | 0.66 m of water at peak; over 30 cm for 7.5 h; 30 cm reached 11.0 h into the storm; worst hour 18 mm (68% of the storm); a culvert within 100 m is overtopped |
| 2 | 0.99 | Tyler Terrace | Newton | 0.53 m of water at peak; worst hour 8 mm (43% of the storm) |
| 3 | 0.99 | Pleasant Street | Newton | 0.53 m of water at peak; worst hour 8 mm (44% of the storm); water beside the road 3.98 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 1.8 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.90); a culvert within 100 m is overtopped |
| 4 | 0.98 | Ramp | Braintree | 0.52 m of water at peak; over 30 cm for 4.0 h; 30 cm reached 14.5 h into the storm; worst hour 17 mm (66% of the storm); a culvert within 100 m is overtopped |
| 5 | 0.98 | Ramp | Braintree | 0.52 m of water at peak; over 30 cm for 4.0 h; 30 cm reached 14.5 h into the storm; worst hour 17 mm (68% of the storm); a culvert within 100 m is overtopped |
| 6 | 0.98 | Ramp | Braintree | 0.52 m of water at peak; over 30 cm for 4.0 h; 30 cm reached 14.5 h into the storm; worst hour 17 mm (68% of the storm); a culvert within 100 m is overtopped |
| 7 | 0.95 | Willow Street | Newton | 0.47 m of water at peak; worst hour 8 mm (38% of the storm); a culvert within 100 m is overtopped |
| 8 | 0.95 | Lyman Street | Newton | 0.47 m of water at peak; worst hour 8 mm (38% of the storm); a culvert within 100 m is overtopped |
| 9 | 0.95 | Sumner Street | Newton | 0.47 m of water at peak; worst hour 8 mm (38% of the storm); a culvert within 100 m is overtopped |
| 10 | 0.94 | Beacon Street | Newton | 0.46 m of water at peak; worst hour 8 mm (37% of the storm); water beside the road 0.20 m below its crest (design freeboard 0.30 m; P 0.74); a culvert within 100 m is overtopped |
| 11 | 0.94 | Gray Cliff Road | Newton | 0.46 m of water at peak; worst hour 8 mm (36% of the storm); water beside the road 0.13 m below its crest (design freeboard 0.30 m; P 0.87); a culvert within 100 m is overtopped |
| 12 | 0.93 | Tyler Terrace | Newton | 0.45 m of water at peak; worst hour 8 mm (41% of the storm); water beside the road 2.02 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 1.7 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.20); a culvert within 100 m is overtopped |
| 13 | 0.90 | Lyman Street | Newton | 0.43 m of water at peak; worst hour 8 mm (39% of the storm); a culvert within 100 m is overtopped |
| 14 | 0.84 | Chesley Road | Newton | 0.40 m of water at peak; worst hour 8 mm (37% of the storm); a culvert within 100 m is overtopped |
| 15 | 0.83 | Gray Cliff Road | Newton | 0.40 m of water at peak; worst hour 7 mm (36% of the storm); a culvert within 100 m is overtopped |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
