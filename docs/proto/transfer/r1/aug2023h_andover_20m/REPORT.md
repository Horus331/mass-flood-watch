# Road-closure prototype: aug2023h_transfer_aug2023h_andover_20m

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on CPU (OpenMP)), 20 m grid, storm from 2023-08-18T07:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 19,082 |
| Expected closures (sum of probabilities) | 51.3 |
| Segments with closure probability >= 50% | 11 (1.8 km) |
| Further segments that may close (stream reaches the road crest) | 16 (2.3 km) |
| Culverts overtopped / surcharged | 37 / 0 of 956 |
| Road segments cut off from hospitals | 0 |
| Worst added trip time to a hospital | 0.0 min |
| Heaviest hour of rain | 46.9 mm |
| Flood model run time | 1524 s |


## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 1.00 | Enmore Street | Andover | 0.69 m of water at peak; over 30 cm for 9.0 h; 30 cm reached 8.5 h into the storm; worst hour 41 mm (64% of the storm); a culvert within 100 m is overtopped |
| 2 | 1.00 | Enmore Street | Andover | 0.69 m of water at peak; over 30 cm for 9.0 h; 30 cm reached 8.5 h into the storm; worst hour 41 mm (64% of the storm) |
| 3 | 1.00 | Linwood Street | Andover | 0.69 m of water at peak; over 30 cm for 9.0 h; 30 cm reached 8.5 h into the storm; worst hour 41 mm (64% of the storm); a culvert within 100 m is overtopped |
| 4 | 0.98 | Whittier Court | Andover | 0.52 m of water at peak; over 30 cm for 3.0 h; 30 cm reached 8.5 h into the storm; worst hour 39 mm (57% of the storm); a culvert within 100 m is overtopped |
| 5 | 0.83 | Morton Street | Andover | 0.40 m of water at peak; over 30 cm for 1.0 h; 30 cm reached 8.0 h into the storm; worst hour 39 mm (57% of the storm); a culvert within 100 m is overtopped |
| 6 | 0.83 | Morton Street | Andover | 0.39 m of water at peak; over 30 cm for 1.0 h; 30 cm reached 8.0 h into the storm; worst hour 39 mm (58% of the storm); a culvert within 100 m is overtopped |
| 7 | 0.76 | Pinnacle Street | Tewksbury | 0.37 m of water at peak; over 30 cm for 2.0 h; 30 cm reached 8.0 h into the storm; worst hour 34 mm (49% of the storm); culvert (Unknown): headwater 3.83 m vs road crest 2.23 m, 2.0 m3/s |
| 8 | 0.66 | Central Street | Andover | 0.34 m of water at peak; over 30 cm for 1.0 h; 30 cm reached 9.0 h into the storm; worst hour 38 mm (57% of the storm); a culvert within 100 m is overtopped |
| 9 | 0.63 | Chestnut Street | Andover | 0.33 m of water at peak; over 30 cm for 0.5 h; 30 cm reached 9.0 h into the storm; worst hour 39 mm (57% of the storm); a culvert within 100 m is overtopped |
| 10 | 0.60 | Bartlet Street | Andover | 0.33 m of water at peak; over 30 cm for 0.5 h; 30 cm reached 9.0 h into the storm; worst hour 38 mm (57% of the storm); a culvert within 100 m is overtopped |
| 11 | 0.50 | York Street | Andover | 0.30 m of water at peak; worst hour 40 mm (62% of the storm); water beside the road 0.25 m above its crest (design freeboard 0.30 m; P 1.00); road sag 2.2 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 40 mm; catchment 455.1 ha) (P 0.39); a culvert within 100 m is overtopped |
| 12 | 0.43 | Greenwood Road | Andover | 0.28 m of water at peak; worst hour 27 mm (45% of the storm) |
| 13 | 0.41 | Route 114 | Lawrence | 0.28 m of water at peak; worst hour 39 mm (68% of the storm); a culvert within 100 m is overtopped |
| 14 | 0.40 | Route 114 | North Andover | 0.28 m of water at peak; worst hour 39 mm (68% of the storm); a culvert within 100 m is overtopped |
| 15 | 0.38 | Route 114 | North Andover | 0.27 m of water at peak; worst hour 38 mm (68% of the storm); a culvert within 100 m is overtopped |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
