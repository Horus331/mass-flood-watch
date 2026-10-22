# Road-closure prototype: jul2023vt_proto

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on CPU (OpenMP)), 20 m grid, storm from 2023-07-09T18:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 3,483 |
| Expected closures (sum of probabilities) | 275.0 |
| Segments with closure probability >= 50% | 253 (108.3 km) |
| Further segments that may close (stream reaches the road crest) | 111 (28.3 km) |
| Culverts overtopped / surcharged | 452 / 53 of 1329 |
| Road segments cut off from hospitals | 1443 |
| Worst added trip time to a hospital | 40.4 min |
| Heaviest hour of rain | 29.7 mm |
| Flood model run time | 2916 s |


## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 1.00 | (unnamed) | Berlin Corners | 1.60 m of water at peak; over 30 cm for 46.0 h; 30 cm reached 14.5 h into the storm; worst hour 19 mm (11% of the storm); water beside the road 0.87 m above its crest (design freeboard 0.30 m; P 1.00) |
| 2 | 1.00 | (unnamed) | Berlin Corners | 1.60 m of water at peak; over 30 cm for 46.0 h; 30 cm reached 14.5 h into the storm; worst hour 18 mm (10% of the storm) |
| 3 | 1.00 | I 89 | Northfield | 27.36 m of water at peak; over 30 cm for 45.0 h; 30 cm reached 15.5 h into the storm; worst hour 11 mm (7% of the storm); water beside the road 4.74 m above its crest (design freeboard 0.30 m; P 1.00); culvert (stream): headwater 4270.87 m vs road crest 16.46 m, 138.1 m3/s |
| 4 | 1.00 | I 89 | Montpelier Junction | 1.56 m of water at peak; over 30 cm for 45.0 h; 30 cm reached 15.5 h into the storm; worst hour 24 mm (13% of the storm); water beside the road 0.48 m below its crest (design freeboard 0.30 m; P 0.12); culvert (Sunny Brook): headwater 285.05 m vs road crest 3.51 m, 4.9 m3/s |
| 5 | 1.00 | I 89 | Montpelier Junction | 1.56 m of water at peak; over 30 cm for 45.0 h; 30 cm reached 15.5 h into the storm; worst hour 24 mm (13% of the storm); culvert (Sunny Brook): headwater 285.05 m vs road crest 3.51 m, 4.9 m3/s |
| 6 | 1.00 | I 89 | Montpelier Junction | 1.11 m of water at peak; over 30 cm for 44.5 h; 30 cm reached 16.0 h into the storm; worst hour 19 mm (11% of the storm); water beside the road 0.14 m below its crest (design freeboard 0.30 m; P 0.85); a culvert within 100 m is overtopped |
| 7 | 1.00 | I 89 | Berlin Corners | 0.89 m of water at peak; over 30 cm for 44.0 h; 30 cm reached 16.5 h into the storm; worst hour 9 mm (7% of the storm); a culvert within 100 m is overtopped |
| 8 | 1.00 | I 89 | South Northfield | 0.84 m of water at peak; over 30 cm for 44.0 h; 30 cm reached 16.5 h into the storm; worst hour 12 mm (8% of the storm); water beside the road 0.31 m above its crest (design freeboard 0.30 m; P 1.00) |
| 9 | 1.00 | I 89 | Berlin Corners | 1.42 m of water at peak; over 30 cm for 42.5 h; 30 cm reached 18.0 h into the storm; worst hour 12 mm (9% of the storm); a culvert within 100 m is overtopped |
| 10 | 1.00 | (unnamed) | Berlin Corners | 1.27 m of water at peak; over 30 cm for 42.0 h; 30 cm reached 18.5 h into the storm; worst hour 9 mm (7% of the storm); water beside the road 0.80 m above its crest (design freeboard 0.30 m; P 1.00) |
| 11 | 1.00 | (unnamed) | Montpelier Junction | 0.65 m of water at peak; over 30 cm for 41.0 h; 30 cm reached 19.5 h into the storm; worst hour 20 mm (12% of the storm) |
| 12 | 1.00 | U.S. Route 2 (US 2) | East Montpelier | 0.82 m of water at peak; over 30 cm for 37.5 h; 30 cm reached 23.0 h into the storm; worst hour 8 mm (9% of the storm); culvert (Mallory Brook): headwater 12937.47 m vs road crest -29.93 m, 8.3 m3/s |
| 13 | 1.00 | I 89 | Berlin Corners | 0.83 m of water at peak; over 30 cm for 37.0 h; 30 cm reached 23.5 h into the storm; worst hour 9 mm (7% of the storm); water beside the road 0.21 m below its crest (design freeboard 0.30 m; P 0.73); a culvert within 100 m is overtopped |
| 14 | 1.00 | I 89 | Berlin Corners | 0.82 m of water at peak; over 30 cm for 37.0 h; 30 cm reached 23.5 h into the storm; worst hour 9 mm (7% of the storm); culvert (stream): headwater 10.98 m vs road crest 1.82 m, 0.5 m3/s |
| 15 | 1.00 | I 89 | Northfield | 7.63 m of water at peak; over 30 cm for 36.5 h; 30 cm reached 24.0 h into the storm; worst hour 11 mm (7% of the storm); water beside the road 0.37 m below its crest (design freeboard 0.30 m; P 0.33); culvert (stream): headwater 4483.89 m vs road crest 16.46 m, 132.2 m3/s |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
