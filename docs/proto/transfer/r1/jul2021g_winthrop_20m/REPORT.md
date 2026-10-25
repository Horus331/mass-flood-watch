# Road-closure prototype: jul2021g_transfer_jul2021g_winthrop_20m

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on CPU (OpenMP)), 20 m grid, storm from 2021-07-09T07:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 44,411 |
| Expected closures (sum of probabilities) | 159.3 |
| Segments with closure probability >= 50% | 56 (8.8 km) |
| Further segments that may close (stream reaches the road crest) | 265 (46.6 km) |
| Culverts overtopped / surcharged | 55 / 0 of 447 |
| Road segments cut off from hospitals | 0 |
| Worst added trip time to a hospital | 0.0 min |
| Heaviest hour of rain | 19.7 mm |
| Flood model run time | 1775 s |


## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 1.00 | Route 99 | Boston | 0.95 m of water at peak; over 30 cm for 4.5 h; 30 cm reached 14.0 h into the storm; worst hour 16 mm (30% of the storm); road sag 4.3 m deep (underpass, drains sized for the 50-yr hour, 58 mm; peak hour here 16 mm; catchment 13.2 ha) (P 1.00) |
| 2 | 1.00 | Clinton Road | Brookline | 0.82 m of water at peak; over 30 cm for 8.5 h; 30 cm reached 10.0 h into the storm; worst hour 16 mm (28% of the storm); water beside the road 0.78 m above its crest (design freeboard 0.30 m; P 1.00); road sag 1.2 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 16 mm; catchment 102.5 ha) (P 1.00) |
| 3 | 1.00 | Rutherford Avenue | Boston | 0.95 m of water at peak; over 30 cm for 4.5 h; 30 cm reached 14.0 h into the storm; worst hour 16 mm (30% of the storm); road sag 4.3 m deep (underpass, drains sized for the 50-yr hour, 58 mm; peak hour here 16 mm; catchment 13.2 ha) (P 1.00) |
| 4 | 0.99 | Croftdale Road | Newton | 0.53 m of water at peak; over 30 cm for 8.0 h; 30 cm reached 10.5 h into the storm; worst hour 16 mm (27% of the storm) |
| 5 | 0.99 | Tyler Terrace | Newton | 0.53 m of water at peak; worst hour 17 mm (28% of the storm) |
| 6 | 0.99 | Pleasant Street | Newton | 0.53 m of water at peak; worst hour 17 mm (28% of the storm); water beside the road 3.98 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 2.1 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.84); a culvert within 100 m is overtopped |
| 7 | 0.95 | Willow Street | Newton | 0.47 m of water at peak; over 30 cm for 2.5 h; 30 cm reached 12.5 h into the storm; worst hour 17 mm (27% of the storm); a culvert within 100 m is overtopped |
| 8 | 0.95 | Lyman Street | Newton | 0.47 m of water at peak; over 30 cm for 2.5 h; 30 cm reached 12.5 h into the storm; worst hour 17 mm (27% of the storm); a culvert within 100 m is overtopped |
| 9 | 0.95 | Sumner Street | Newton | 0.47 m of water at peak; over 30 cm for 2.5 h; 30 cm reached 12.5 h into the storm; worst hour 17 mm (27% of the storm); a culvert within 100 m is overtopped |
| 10 | 0.94 | Beacon Street | Newton | 0.46 m of water at peak; worst hour 17 mm (27% of the storm); water beside the road 0.20 m below its crest (design freeboard 0.30 m; P 0.74); a culvert within 100 m is overtopped |
| 11 | 0.94 | Gray Cliff Road | Newton | 0.46 m of water at peak; worst hour 17 mm (27% of the storm); water beside the road 0.13 m below its crest (design freeboard 0.30 m; P 0.87); a culvert within 100 m is overtopped |
| 12 | 0.94 | Mountfort Road | Newton | 0.45 m of water at peak; worst hour 17 mm (28% of the storm); a culvert within 100 m is overtopped |
| 13 | 0.94 | Wood End Road | Newton | 0.45 m of water at peak; worst hour 17 mm (28% of the storm) |
| 14 | 0.94 | Wood End Road | Newton | 0.45 m of water at peak; worst hour 17 mm (28% of the storm) |
| 15 | 0.93 | Tyler Terrace | Newton | 0.45 m of water at peak; worst hour 17 mm (28% of the storm); water beside the road 2.02 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 1.8 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.19); a culvert within 100 m is overtopped |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
