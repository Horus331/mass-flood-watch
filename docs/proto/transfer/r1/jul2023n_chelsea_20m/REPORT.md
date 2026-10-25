# Road-closure prototype: jul2023n_transfer_jul2023n_chelsea_20m

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on CPU (OpenMP)), 20 m grid, storm from 2023-07-21T18:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 46,482 |
| Expected closures (sum of probabilities) | 102.1 |
| Segments with closure probability >= 50% | 23 (3.0 km) |
| Further segments that may close (stream reaches the road crest) | 68 (9.4 km) |
| Culverts overtopped / surcharged | 16 / 0 of 347 |
| Road segments cut off from hospitals | 0 |
| Worst added trip time to a hospital | 0.0 min |
| Heaviest hour of rain | 37.1 mm |
| Flood model run time | 966 s |


## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 1.00 | Route 99 | Boston | 0.88 m of water at peak; over 30 cm for 5.0 h; 30 cm reached 13.5 h into the storm; worst hour 27 mm (62% of the storm); road sag 4.3 m deep (underpass, drains sized for the 50-yr hour, 58 mm; peak hour here 26 mm; catchment 13.2 ha) (P 1.00) |
| 2 | 1.00 | Rutherford Avenue | Boston | 0.88 m of water at peak; over 30 cm for 5.0 h; 30 cm reached 13.5 h into the storm; worst hour 26 mm (60% of the storm); road sag 4.3 m deep (underpass, drains sized for the 50-yr hour, 58 mm; peak hour here 26 mm; catchment 13.2 ha) (P 1.00) |
| 3 | 0.99 | Tyler Terrace | Newton | 0.53 m of water at peak; worst hour 21 mm (51% of the storm) |
| 4 | 0.99 | Pleasant Street | Newton | 0.53 m of water at peak; worst hour 21 mm (51% of the storm); water beside the road 3.98 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 2.0 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.85); a culvert within 100 m is overtopped |
| 5 | 0.98 | Clinton Road | Brookline | 0.50 m of water at peak; over 30 cm for 7.5 h; 30 cm reached 11.0 h into the storm; worst hour 13 mm (37% of the storm); water beside the road 0.46 m above its crest (design freeboard 0.30 m; P 1.00); road sag 1.2 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 13 mm; catchment 102.5 ha) (P 1.00) |
| 6 | 0.95 | Willow Street | Newton | 0.47 m of water at peak; worst hour 21 mm (50% of the storm); a culvert within 100 m is overtopped |
| 7 | 0.95 | Lyman Street | Newton | 0.47 m of water at peak; worst hour 21 mm (50% of the storm); a culvert within 100 m is overtopped |
| 8 | 0.95 | Sumner Street | Newton | 0.47 m of water at peak; worst hour 21 mm (50% of the storm); a culvert within 100 m is overtopped |
| 9 | 0.94 | Beacon Street | Newton | 0.46 m of water at peak; worst hour 21 mm (49% of the storm); water beside the road 0.20 m below its crest (design freeboard 0.30 m; P 0.74); a culvert within 100 m is overtopped |
| 10 | 0.94 | Gray Cliff Road | Newton | 0.46 m of water at peak; worst hour 21 mm (49% of the storm); water beside the road 0.13 m below its crest (design freeboard 0.30 m; P 0.87); a culvert within 100 m is overtopped |
| 11 | 0.93 | Tyler Terrace | Newton | 0.45 m of water at peak; worst hour 21 mm (50% of the storm); water beside the road 2.02 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 1.7 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.20); a culvert within 100 m is overtopped |
| 12 | 0.91 | Mill Street | Arlington | 0.43 m of water at peak; over 30 cm for 10.5 h; 30 cm reached 8.0 h into the storm; worst hour 10 mm (48% of the storm); a culvert within 100 m is overtopped |
| 13 | 0.90 | Lyman Street | Newton | 0.43 m of water at peak; worst hour 21 mm (50% of the storm); a culvert within 100 m is overtopped |
| 14 | 0.84 | Chesley Road | Newton | 0.40 m of water at peak; worst hour 21 mm (50% of the storm); a culvert within 100 m is overtopped |
| 15 | 0.83 | Gray Cliff Road | Newton | 0.40 m of water at peak; worst hour 21 mm (50% of the storm); a culvert within 100 m is overtopped |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
