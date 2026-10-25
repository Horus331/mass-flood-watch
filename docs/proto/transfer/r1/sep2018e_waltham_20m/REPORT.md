# Road-closure prototype: sep2018e_transfer_sep2018e_waltham_20m

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on CPU (OpenMP)), 20 m grid, storm from 2018-09-18T07:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 48,301 |
| Expected closures (sum of probabilities) | 120.4 |
| Segments with closure probability >= 50% | 50 (6.6 km) |
| Further segments that may close (stream reaches the road crest) | 66 (11.8 km) |
| Culverts overtopped / surcharged | 46 / 1 of 647 |
| Road segments cut off from hospitals | 0 |
| Worst added trip time to a hospital | 0.0 min |
| Heaviest hour of rain | 27.9 mm |
| Flood model run time | 1213 s |


## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 1.00 | Highland Avenue | Winchester | 1.02 m of water at peak; over 30 cm for 9.0 h; 30 cm reached 9.5 h into the storm; worst hour 19 mm (51% of the storm); a culvert within 100 m is overtopped |
| 2 | 1.00 | Mill Street | Arlington | 0.58 m of water at peak; over 30 cm for 10.5 h; 30 cm reached 8.0 h into the storm; worst hour 18 mm (48% of the storm); a culvert within 100 m is overtopped |
| 3 | 0.99 | Arlo Road | Newton | 0.55 m of water at peak; worst hour 13 mm (48% of the storm); a culvert within 100 m is overtopped |
| 4 | 0.99 | Chestnut Street | Newton | 0.54 m of water at peak; over 30 cm for 18.0 h; 30 cm reached 0.5 h into the storm; worst hour 12 mm (49% of the storm); water beside the road 2.42 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 2.0 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.91); a culvert within 100 m is overtopped |
| 5 | 0.99 | Tyler Terrace | Newton | 0.53 m of water at peak; worst hour 14 mm (48% of the storm) |
| 6 | 0.99 | Pleasant Street | Newton | 0.53 m of water at peak; worst hour 14 mm (48% of the storm); water beside the road 3.98 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 1.8 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.90); a culvert within 100 m is overtopped |
| 7 | 0.95 | Willow Street | Newton | 0.47 m of water at peak; worst hour 14 mm (46% of the storm); a culvert within 100 m is overtopped |
| 8 | 0.95 | Lyman Street | Newton | 0.47 m of water at peak; worst hour 14 mm (46% of the storm); a culvert within 100 m is overtopped |
| 9 | 0.95 | Sumner Street | Newton | 0.47 m of water at peak; worst hour 14 mm (46% of the storm); a culvert within 100 m is overtopped |
| 10 | 0.95 | Wellesley Avenue Extension | Needham | 0.47 m of water at peak; worst hour 11 mm (49% of the storm); a culvert within 100 m is overtopped |
| 11 | 0.94 | Beacon Street | Newton | 0.46 m of water at peak; worst hour 13 mm (45% of the storm); water beside the road 0.20 m below its crest (design freeboard 0.30 m; P 0.74); a culvert within 100 m is overtopped |
| 12 | 0.94 | Gray Cliff Road | Newton | 0.46 m of water at peak; worst hour 13 mm (45% of the storm); water beside the road 0.13 m below its crest (design freeboard 0.30 m; P 0.87); a culvert within 100 m is overtopped |
| 13 | 0.94 | Mountfort Road | Newton | 0.45 m of water at peak; worst hour 12 mm (46% of the storm); a culvert within 100 m is overtopped |
| 14 | 0.94 | Wood End Road | Newton | 0.45 m of water at peak; worst hour 13 mm (46% of the storm) |
| 15 | 0.94 | Wood End Road | Newton | 0.45 m of water at peak; worst hour 13 mm (46% of the storm) |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
