# Road-closure prototype: jul2023vt_proto

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on CPU (OpenMP)), 20 m grid, storm from 2023-07-09T18:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 3,697 |
| Expected closures (sum of probabilities) | 333.1 |
| Segments with closure probability >= 50% | 309 (109.2 km) |
| Further segments that may close (stream reaches the road crest) | 88 (17.2 km) |
| Culverts overtopped / surcharged | 664 / 40 of 1329 |
| Road segments cut off from hospitals | 3872 |
| Worst added trip time to a hospital | 0.6 min |
| Heaviest hour of rain | 29.7 mm |
| Flood model run time | 3455 s |


## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 1.00 | U.S. Route 2 (US 2) | East Montpelier | 1.19 m of water at peak; over 30 cm for 33.5 h; 30 cm reached 27.0 h into the storm; worst hour 9 mm (9% of the storm); culvert (stream): headwater 11.86 m vs road crest 2.43 m, 5.4 m3/s |
| 2 | 1.00 | U.S. Route 2 (US 2) | East Montpelier | 1.07 m of water at peak; over 30 cm for 32.5 h; 30 cm reached 28.0 h into the storm; worst hour 9 mm (10% of the storm); culvert (stream): headwater 13.06 m vs road crest 2.43 m, 5.4 m3/s |
| 3 | 1.00 | U.S. Route 2 (US 2) | East Montpelier | 0.82 m of water at peak; over 30 cm for 31.5 h; 30 cm reached 27.0 h into the storm; worst hour 13 mm (10% of the storm); culvert (stream): headwater 60859.37 m vs road crest 7.85 m, 7.3 m3/s |
| 4 | 1.00 | School Street (US 2) | Plainfield | 0.78 m of water at peak; over 30 cm for 24.0 h; 30 cm reached 36.5 h into the storm; worst hour 10 mm (11% of the storm); culvert (stream): headwater 553.27 m vs road crest 1.67 m, 0.9 m3/s |
| 5 | 1.00 | U.S. Route 2 (US 2) | Plainfield | 0.70 m of water at peak; over 30 cm for 23.5 h; 30 cm reached 37.0 h into the storm; worst hour 10 mm (11% of the storm); culvert (Wells Brook): headwater 33.96 m vs road crest 1.90 m, 1.6 m3/s |
| 6 | 1.00 | Vermont Route 12 (VT 12) | West Berlin | 2.67 m of water at peak; over 30 cm for 44.5 h; 30 cm reached 16.0 h into the storm; worst hour 16 mm (10% of the storm); water beside the road 0.22 m above its crest (design freeboard 0.30 m; P 1.00); culvert (stream): headwater 4161.41 m vs road crest 1.90 m, 19.7 m3/s |
| 7 | 1.00 | Vermont Route 12 (VT 12) | West Berlin | 2.24 m of water at peak; over 30 cm for 44.5 h; 30 cm reached 16.0 h into the storm; worst hour 17 mm (10% of the storm); a culvert within 100 m is overtopped |
| 8 | 1.00 | State Street (US 2) | Montpelier | 3.85 m of water at peak; over 30 cm for 43.5 h; 30 cm reached 17.0 h into the storm; worst hour 17 mm (11% of the storm); water beside the road 0.91 m above its crest (design freeboard 0.30 m; P 1.00); a culvert within 100 m is overtopped |
| 9 | 1.00 | Vermont Route 62 (VT 62) | Barre | 2.80 m of water at peak; over 30 cm for 43.5 h; 30 cm reached 17.0 h into the storm; worst hour 21 mm (13% of the storm); water beside the road 0.66 m above its crest (design freeboard 0.30 m; P 1.00); culvert (Stevens Branch): headwater 24675.88 m vs road crest 1.98 m, 61.0 m3/s |
| 10 | 1.00 | Vermont Route 62 (VT 62) | Barre | 2.79 m of water at peak; over 30 cm for 43.5 h; 30 cm reached 17.0 h into the storm; worst hour 21 mm (14% of the storm); water beside the road 0.66 m above its crest (design freeboard 0.30 m; P 1.00); culvert (Stevens Branch): headwater 24675.88 m vs road crest 1.98 m, 61.0 m3/s |
| 11 | 1.00 | VT 14 | Barre | 2.55 m of water at peak; over 30 cm for 41.5 h; 30 cm reached 19.0 h into the storm; worst hour 21 mm (13% of the storm); a culvert within 100 m is overtopped |
| 12 | 1.00 | North Main Street (VT 14) | Barre | 2.55 m of water at peak; over 30 cm for 41.5 h; 30 cm reached 19.0 h into the storm; worst hour 21 mm (13% of the storm); a culvert within 100 m is overtopped |
| 13 | 1.00 | Washington Street (US 302 / VT 14) | Barre | 2.47 m of water at peak; over 30 cm for 41.5 h; 30 cm reached 19.0 h into the storm; worst hour 21 mm (13% of the storm); a culvert within 100 m is overtopped |
| 14 | 1.00 | Vermont Route 14 (VT 14) | Graniteville | 1.62 m of water at peak; over 30 cm for 36.0 h; 30 cm reached 19.0 h into the storm; worst hour 7 mm (8% of the storm); water beside the road 0.26 m below its crest (design freeboard 0.30 m; P 0.61); culvert (stream): headwater 15660.85 m vs road crest 3.43 m, 19.9 m3/s |
| 15 | 1.00 | Vermont Route 63 (VT 63) | South Barre | 1.45 m of water at peak; over 30 cm for 36.0 h; 30 cm reached 23.0 h into the storm; worst hour 14 mm (11% of the storm); water beside the road 0.08 m below its crest (design freeboard 0.30 m; P 0.93); culvert (Stevens Branch): headwater 46712.42 m vs road crest 7.92 m, 25.6 m3/s |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
