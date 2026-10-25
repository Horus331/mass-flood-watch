# Road-closure prototype: jun2018f_transfer_jun2018f_belmont_20m

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on CPU (OpenMP)), 20 m grid, storm from 2018-06-24T22:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 47,429 |
| Expected closures (sum of probabilities) | 102.5 |
| Segments with closure probability >= 50% | 37 (4.6 km) |
| Further segments that may close (stream reaches the road crest) | 43 (8.7 km) |
| Culverts overtopped / surcharged | 33 / 0 of 654 |
| Road segments cut off from hospitals | 0 |
| Worst added trip time to a hospital | 0.0 min |
| Heaviest hour of rain | 16.6 mm |
| Flood model run time | 797 s |


## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 0.99 | Arlo Road | Newton | 0.55 m of water at peak; worst hour 5 mm (38% of the storm); a culvert within 100 m is overtopped |
| 2 | 0.99 | Chestnut Street | Newton | 0.54 m of water at peak; over 30 cm for 18.0 h; 30 cm reached 0.5 h into the storm; worst hour 5 mm (38% of the storm); water beside the road 2.42 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 2.1 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.91); a culvert within 100 m is overtopped |
| 3 | 0.99 | Tyler Terrace | Newton | 0.53 m of water at peak; worst hour 5 mm (33% of the storm) |
| 4 | 0.99 | Pleasant Street | Newton | 0.53 m of water at peak; worst hour 5 mm (33% of the storm); water beside the road 3.98 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 1.8 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.90); a culvert within 100 m is overtopped |
| 5 | 0.95 | Willow Street | Newton | 0.47 m of water at peak; worst hour 5 mm (33% of the storm); a culvert within 100 m is overtopped |
| 6 | 0.95 | Lyman Street | Newton | 0.47 m of water at peak; worst hour 5 mm (33% of the storm); a culvert within 100 m is overtopped |
| 7 | 0.95 | Sumner Street | Newton | 0.47 m of water at peak; worst hour 5 mm (33% of the storm); a culvert within 100 m is overtopped |
| 8 | 0.94 | Beacon Street | Newton | 0.46 m of water at peak; worst hour 5 mm (34% of the storm); water beside the road 0.20 m below its crest (design freeboard 0.30 m; P 0.74); a culvert within 100 m is overtopped |
| 9 | 0.94 | Gray Cliff Road | Newton | 0.46 m of water at peak; worst hour 5 mm (34% of the storm); water beside the road 0.13 m below its crest (design freeboard 0.30 m; P 0.87); a culvert within 100 m is overtopped |
| 10 | 0.94 | Mountfort Road | Newton | 0.45 m of water at peak; worst hour 5 mm (36% of the storm); a culvert within 100 m is overtopped |
| 11 | 0.94 | Wood End Road | Newton | 0.45 m of water at peak; worst hour 5 mm (36% of the storm) |
| 12 | 0.94 | Wood End Road | Newton | 0.45 m of water at peak; worst hour 5 mm (37% of the storm) |
| 13 | 0.93 | Tyler Terrace | Newton | 0.45 m of water at peak; worst hour 5 mm (33% of the storm); water beside the road 2.02 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 1.7 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.20); a culvert within 100 m is overtopped |
| 14 | 0.91 | Mill Street | Arlington | 0.44 m of water at peak; over 30 cm for 10.5 h; 30 cm reached 8.0 h into the storm; worst hour 13 mm (48% of the storm); a culvert within 100 m is overtopped |
| 15 | 0.90 | Lyman Street | Newton | 0.43 m of water at peak; worst hour 5 mm (33% of the storm); a culvert within 100 m is overtopped |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
