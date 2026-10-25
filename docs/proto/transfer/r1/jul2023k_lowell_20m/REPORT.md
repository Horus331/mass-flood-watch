# Road-closure prototype: jul2023k_transfer_jul2023k_lowell_20m

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on CPU (OpenMP)), 20 m grid, storm from 2023-07-21T15:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 16,599 |
| Expected closures (sum of probabilities) | 34.8 |
| Segments with closure probability >= 50% | 1 (0.2 km) |
| Further segments that may close (stream reaches the road crest) | 19 (2.4 km) |
| Culverts overtopped / surcharged | 27 / 0 of 906 |
| Road segments cut off from hospitals | 0 |
| Worst added trip time to a hospital | 0.0 min |
| Heaviest hour of rain | 50.2 mm |
| Flood model run time | 1400 s |


## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 0.66 | Turnpike Road | Chelmsford | 0.34 m of water at peak; over 30 cm for 6.0 h; 30 cm reached 11.5 h into the storm; worst hour 32 mm (58% of the storm); water beside the road 0.15 m above its crest (design freeboard 0.30 m; P 1.00) |
| 2 | 0.39 | North Billerica Road | Tewksbury | 0.27 m of water at peak; worst hour 49 mm (80% of the storm); culvert (Marginal Brook): headwater 31.66 m vs road crest 1.22 m, 1.1 m3/s |
| 3 | 0.30 | Pinnacle Street | Tewksbury | 0.25 m of water at peak; worst hour 28 mm (68% of the storm) |
| 4 | 0.21 | Summer Street | Chelmsford | 0.22 m of water at peak; worst hour 31 mm (54% of the storm) |
| 5 | 0.18 | Felton Street | Lowell | 0.21 m of water at peak; worst hour 47 mm (75% of the storm) |
| 6 | 0.18 | Felton Street | Lowell | 0.21 m of water at peak; worst hour 47 mm (74% of the storm); runoff beside / along the road at 0.8 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.35); a culvert within 100 m is overtopped |
| 7 | 0.17 | Route 110 | Chelmsford | 0.20 m of water at peak; worst hour 28 mm (46% of the storm); a culvert within 100 m is overtopped |
| 8 | 0.15 | Ramp | Tewksbury | 0.20 m of water at peak; worst hour 47 mm (80% of the storm); water beside the road 0.39 m above its crest (design freeboard 0.30 m; P 1.00); road sag 1.4 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 47 mm; catchment 13.7 ha) (P 1.00) |
| 9 | 0.14 | Acton Street | Lowell | 0.19 m of water at peak; worst hour 46 mm (73% of the storm); a culvert within 100 m is overtopped |
| 10 | 0.13 | River Road | Tewksbury | 0.19 m of water at peak; worst hour 38 mm (72% of the storm); a culvert within 100 m is overtopped |
| 11 | 0.12 | (unnamed) | Dracut | 0.18 m of water at peak; worst hour 35 mm (70% of the storm) |
| 12 | 0.12 | Methuen Street | Dracut | 0.18 m of water at peak; worst hour 35 mm (70% of the storm); a culvert within 100 m is overtopped |
| 13 | 0.11 | Route 3A | Chelmsford | 0.18 m of water at peak; worst hour 24 mm (44% of the storm); a culvert within 100 m is overtopped |
| 14 | 0.11 | Burdette Road | Dracut | 0.18 m of water at peak; worst hour 23 mm (38% of the storm); a culvert within 100 m is overtopped |
| 15 | 0.10 | Wheeler Road | Dracut | 0.17 m of water at peak; worst hour 26 mm (54% of the storm); a culvert within 100 m is overtopped |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
