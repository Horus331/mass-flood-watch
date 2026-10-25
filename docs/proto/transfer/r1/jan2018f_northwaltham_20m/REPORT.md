# Road-closure prototype: jan2018f_transfer_jan2018f_northwaltham_20m

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on CPU (OpenMP)), 20 m grid, storm from 2018-01-12T21:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 42,542 |
| Expected closures (sum of probabilities) | 119.0 |
| Segments with closure probability >= 50% | 57 (11.1 km) |
| Further segments that may close (stream reaches the road crest) | 81 (16.5 km) |
| Culverts overtopped / surcharged | 54 / 1 of 794 |
| Road segments cut off from hospitals | 0 |
| Worst added trip time to a hospital | 0.0 min |
| Heaviest hour of rain | 10.7 mm |
| Flood model run time | 933 s |


## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 1.00 | Ramp | Weston | 0.68 m of water at peak; over 30 cm for 18.0 h; 30 cm reached 0.5 h into the storm; worst hour 7 mm (21% of the storm); a culvert within 100 m is overtopped |
| 2 | 0.99 | Arlo Road | Newton | 0.55 m of water at peak; worst hour 8 mm (21% of the storm); a culvert within 100 m is overtopped |
| 3 | 0.99 | Chestnut Street | Newton | 0.54 m of water at peak; over 30 cm for 18.0 h; 30 cm reached 0.5 h into the storm; worst hour 9 mm (22% of the storm); water beside the road 2.42 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 2.0 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.91); a culvert within 100 m is overtopped |
| 4 | 0.99 | Tyler Terrace | Newton | 0.53 m of water at peak; worst hour 7 mm (21% of the storm) |
| 5 | 0.99 | Pleasant Street | Newton | 0.53 m of water at peak; worst hour 7 mm (21% of the storm); water beside the road 3.98 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 2.0 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.78); a culvert within 100 m is overtopped |
| 6 | 0.97 | Wellesley Street | Weston | 0.48 m of water at peak; worst hour 6 mm (18% of the storm); a culvert within 100 m is overtopped |
| 7 | 0.95 | Willow Street | Newton | 0.47 m of water at peak; worst hour 7 mm (21% of the storm); a culvert within 100 m is overtopped |
| 8 | 0.95 | Lyman Street | Newton | 0.47 m of water at peak; worst hour 7 mm (21% of the storm); a culvert within 100 m is overtopped |
| 9 | 0.95 | Sumner Street | Newton | 0.47 m of water at peak; worst hour 7 mm (21% of the storm); a culvert within 100 m is overtopped |
| 10 | 0.95 | Wellesley Avenue Extension | Needham | 0.47 m of water at peak; worst hour 9 mm (21% of the storm); a culvert within 100 m is overtopped |
| 11 | 0.94 | Beacon Street | Newton | 0.46 m of water at peak; worst hour 8 mm (20% of the storm); water beside the road 0.20 m below its crest (design freeboard 0.30 m; P 0.74); a culvert within 100 m is overtopped |
| 12 | 0.94 | Gray Cliff Road | Newton | 0.46 m of water at peak; worst hour 8 mm (20% of the storm); water beside the road 0.13 m below its crest (design freeboard 0.30 m; P 0.87); a culvert within 100 m is overtopped |
| 13 | 0.94 | Mountfort Road | Newton | 0.45 m of water at peak; worst hour 7 mm (21% of the storm); a culvert within 100 m is overtopped |
| 14 | 0.94 | Wood End Road | Newton | 0.45 m of water at peak; worst hour 7 mm (21% of the storm) |
| 15 | 0.94 | Wood End Road | Newton | 0.45 m of water at peak; worst hour 7 mm (21% of the storm) |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
