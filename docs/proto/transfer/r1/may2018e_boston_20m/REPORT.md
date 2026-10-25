# Road-closure prototype: may2018e_transfer_may2018e_boston_20m

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on CPU (OpenMP)), 20 m grid, storm from 2018-05-15T15:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 45,137 |
| Expected closures (sum of probabilities) | 79.7 |
| Segments with closure probability >= 50% | 19 (2.0 km) |
| Further segments that may close (stream reaches the road crest) | 18 (2.4 km) |
| Culverts overtopped / surcharged | 14 / 0 of 386 |
| Road segments cut off from hospitals | 0 |
| Worst added trip time to a hospital | 0.0 min |
| Heaviest hour of rain | 15.6 mm |
| Flood model run time | 794 s |


## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 0.99 | Tyler Terrace | Newton | 0.53 m of water at peak; worst hour 7 mm (63% of the storm) |
| 2 | 0.99 | Pleasant Street | Newton | 0.53 m of water at peak; worst hour 7 mm (63% of the storm); water beside the road 3.98 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 1.8 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.90); a culvert within 100 m is overtopped |
| 3 | 0.95 | Willow Street | Newton | 0.47 m of water at peak; worst hour 8 mm (68% of the storm); a culvert within 100 m is overtopped |
| 4 | 0.95 | Lyman Street | Newton | 0.47 m of water at peak; worst hour 8 mm (68% of the storm); a culvert within 100 m is overtopped |
| 5 | 0.95 | Sumner Street | Newton | 0.47 m of water at peak; worst hour 8 mm (68% of the storm); a culvert within 100 m is overtopped |
| 6 | 0.94 | Beacon Street | Newton | 0.46 m of water at peak; worst hour 9 mm (73% of the storm); water beside the road 0.20 m below its crest (design freeboard 0.30 m; P 0.74); a culvert within 100 m is overtopped |
| 7 | 0.94 | Gray Cliff Road | Newton | 0.46 m of water at peak; worst hour 9 mm (73% of the storm); water beside the road 0.13 m below its crest (design freeboard 0.30 m; P 0.87); a culvert within 100 m is overtopped |
| 8 | 0.93 | Tyler Terrace | Newton | 0.45 m of water at peak; worst hour 7 mm (64% of the storm); water beside the road 2.02 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 1.7 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.20); a culvert within 100 m is overtopped |
| 9 | 0.90 | Lyman Street | Newton | 0.43 m of water at peak; worst hour 8 mm (66% of the storm); a culvert within 100 m is overtopped |
| 10 | 0.84 | Chesley Road | Newton | 0.40 m of water at peak; worst hour 8 mm (69% of the storm); a culvert within 100 m is overtopped |
| 11 | 0.83 | Gray Cliff Road | Newton | 0.40 m of water at peak; worst hour 10 mm (73% of the storm); a culvert within 100 m is overtopped |
| 12 | 0.83 | Centre Street | Newton | 0.40 m of water at peak; worst hour 7 mm (65% of the storm); a culvert within 100 m is overtopped |
| 13 | 0.83 | Centre Street | Newton | 0.40 m of water at peak; worst hour 7 mm (65% of the storm); a culvert within 100 m is overtopped |
| 14 | 0.82 | Gray Cliff Road | Newton | 0.39 m of water at peak; worst hour 9 mm (72% of the storm); a culvert within 100 m is overtopped |
| 15 | 0.80 | Bracebridge Road | Newton | 0.39 m of water at peak; worst hour 7 mm (62% of the storm); water beside the road 4.42 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 2.4 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.97); a culvert within 100 m is overtopped |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
