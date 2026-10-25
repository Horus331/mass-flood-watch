# Road-closure prototype: sep2019f_transfer_sep2019f_eastlynn_20m

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on CPU (OpenMP)), 20 m grid, storm from 2019-09-02T15:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 33,995 |
| Expected closures (sum of probabilities) | 51.4 |
| Segments with closure probability >= 50% | 1 (0.1 km) |
| Further segments that may close (stream reaches the road crest) | 8 (1.9 km) |
| Culverts overtopped / surcharged | 1 / 0 of 557 |
| Road segments cut off from hospitals | 0 |
| Worst added trip time to a hospital | 0.0 min |
| Heaviest hour of rain | 34.4 mm |
| Flood model run time | 1569 s |


## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 1.00 | Highland Avenue | Winchester | 0.88 m of water at peak; over 30 cm for 8.5 h; 30 cm reached 10.0 h into the storm; worst hour 21 mm (76% of the storm) |
| 2 | 0.42 | I-93 | Medford | 0.28 m of water at peak; worst hour 27 mm (85% of the storm); water beside the road 0.28 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 1.4 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.74); road sag 1.6 m deep (underpass, drains sized for the 50-yr hour, 58 mm; peak hour here 26 mm; catchment 25.1 ha) (P 0.70) |
| 3 | 0.10 | Central Street | Saugus | 0.17 m of water at peak; worst hour 15 mm (75% of the storm); a culvert within 100 m is overtopped |
| 4 | 0.10 | Elm Street | Saugus | 0.17 m of water at peak; worst hour 15 mm (75% of the storm); a culvert within 100 m is overtopped |
| 5 | 0.10 | Elm Street | Saugus | 0.17 m of water at peak; worst hour 15 mm (75% of the storm) |
| 6 | 0.05 | Powder House Boulevard | Somerville | 0.13 m of water at peak; worst hour 27 mm (85% of the storm); water beside the road 0.09 m above its crest (design freeboard 0.30 m; P 1.00) |
| 7 | 0.05 | Pearson Road | Somerville | 0.13 m of water at peak; worst hour 26 mm (84% of the storm); water beside the road 0.01 m above its crest (design freeboard 0.30 m; P 0.98) |
| 8 | 0.05 | Maple Park Avenue | Medford | 0.13 m of water at peak; worst hour 27 mm (85% of the storm); runoff beside / along the road at 1.3 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.41) |
| 9 | 0.03 | Valley Street | Medford | 0.12 m of water at peak; worst hour 27 mm (85% of the storm) |
| 10 | 0.03 | Metcalf Street | Medford | 0.11 m of water at peak; worst hour 27 mm (85% of the storm); water beside the road 0.06 m above its crest (design freeboard 0.30 m; P 0.99) |
| 11 | 0.03 | Boston Avenue | Medford | 0.11 m of water at peak; worst hour 26 mm (84% of the storm); water beside the road 0.05 m above its crest (design freeboard 0.30 m; P 0.99) |
| 12 | 0.03 | Bromfield Road | Somerville | 0.11 m of water at peak; worst hour 27 mm (84% of the storm) |
| 13 | 0.03 | Howley Street | Peabody | 0.10 m of water at peak; worst hour 11 mm (70% of the storm) |
| 14 | 0.02 | Newcomb Street | Arlington | 0.10 m of water at peak; worst hour 33 mm (86% of the storm) |
| 15 | 0.02 | Herschel Street | Lynn | 0.10 m of water at peak; worst hour 22 mm (81% of the storm) |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
