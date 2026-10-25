# Road-closure prototype: aug2023e_transfer_aug2023e_northandover_20m

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on CPU (OpenMP)), 20 m grid, storm from 2023-08-08T07:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 14,621 |
| Expected closures (sum of probabilities) | 297.7 |
| Segments with closure probability >= 50% | 230 (50.6 km) |
| Further segments that may close (stream reaches the road crest) | 342 (79.5 km) |
| Culverts overtopped / surcharged | 222 / 9 of 867 |
| Road segments cut off from hospitals | 0 |
| Worst added trip time to a hospital | 0.0 min |
| Heaviest hour of rain | 72.1 mm |
| Flood model run time | 1793 s |


## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 1.00 | Route 125 | North Andover | 1.44 m of water at peak; over 30 cm for 11.0 h; 30 cm reached 7.5 h into the storm; worst hour 52 mm (33% of the storm); a culvert within 100 m is overtopped |
| 2 | 1.00 | Route 133 | Andover | 3.19 m of water at peak; over 30 cm for 10.5 h; 30 cm reached 8.0 h into the storm; worst hour 51 mm (40% of the storm); water beside the road 2.38 m above its crest (design freeboard 0.30 m; P 1.00); a culvert within 100 m is overtopped |
| 3 | 1.00 | Route 28 | Andover | 3.19 m of water at peak; over 30 cm for 10.5 h; 30 cm reached 8.0 h into the storm; worst hour 51 mm (40% of the storm); water beside the road 0.09 m below its crest (design freeboard 0.30 m; P 0.92); a culvert within 100 m is overtopped |
| 4 | 1.00 | Route 114 | Lawrence | 0.74 m of water at peak; over 30 cm for 10.5 h; 30 cm reached 8.0 h into the storm; worst hour 42 mm (34% of the storm); water beside the road 0.55 m above its crest (design freeboard 0.30 m; P 1.00); road sag 2.8 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 42 mm; catchment 8.1 ha) (P 1.00) |
| 5 | 1.00 | Route 114 | Lawrence | 0.74 m of water at peak; over 30 cm for 10.5 h; 30 cm reached 8.0 h into the storm; worst hour 42 mm (34% of the storm) |
| 6 | 1.00 | Route 133 | Andover | 3.05 m of water at peak; over 30 cm for 8.5 h; 30 cm reached 10.0 h into the storm; worst hour 52 mm (41% of the storm); water beside the road 2.70 m above its crest (design freeboard 0.30 m; P 1.00); road sag 4.3 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 52 mm; catchment 455.1 ha) (P 1.00) |
| 7 | 1.00 | Route 28 | Andover | 3.00 m of water at peak; over 30 cm for 8.5 h; 30 cm reached 10.0 h into the storm; worst hour 53 mm (43% of the storm); water beside the road 2.94 m above its crest (design freeboard 0.30 m; P 1.00); road sag 2.0 m deep (underpass, drains sized for the 50-yr hour, 58 mm; peak hour here 53 mm; catchment 455.1 ha) (P 1.00) |
| 8 | 1.00 | Route 28 | Andover | 2.86 m of water at peak; over 30 cm for 8.0 h; 30 cm reached 10.5 h into the storm; worst hour 52 mm (43% of the storm); water beside the road 2.78 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 0.5 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.11); road sag 2.0 m deep (underpass, drains sized for the 50-yr hour, 58 mm; peak hour here 53 mm; catchment 455.1 ha) (P 1.00) |
| 9 | 1.00 | Route 28 | Andover | 2.83 m of water at peak; over 30 cm for 8.0 h; 30 cm reached 10.5 h into the storm; worst hour 51 mm (40% of the storm); water beside the road 2.75 m above its crest (design freeboard 0.30 m; P 1.00); a culvert within 100 m is overtopped |
| 10 | 1.00 | Route 28 | Andover | 2.71 m of water at peak; over 30 cm for 8.0 h; 30 cm reached 10.5 h into the storm; worst hour 53 mm (44% of the storm); water beside the road 2.66 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 0.6 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.10) |
| 11 | 1.00 | Route 28 | Andover | 2.71 m of water at peak; over 30 cm for 8.0 h; 30 cm reached 10.5 h into the storm; worst hour 53 mm (44% of the storm) |
| 12 | 1.00 | Route 28 | Andover | 1.31 m of water at peak; over 30 cm for 3.5 h; 30 cm reached 15.0 h into the storm; worst hour 52 mm (42% of the storm); water beside the road 1.09 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 0.7 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.22); road sag 1.0 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 52 mm; catchment 455.1 ha) (P 1.00) |
| 13 | 1.00 | Route 114 | North Andover | 0.67 m of water at peak; over 30 cm for 3.0 h; 30 cm reached 8.0 h into the storm; worst hour 54 mm (39% of the storm); water beside the road 0.36 m below its crest (design freeboard 0.30 m; P 0.34); a culvert within 100 m is overtopped |
| 14 | 1.00 | Route 114 | Lawrence | 0.67 m of water at peak; over 30 cm for 3.0 h; 30 cm reached 8.0 h into the storm; worst hour 55 mm (39% of the storm); runoff beside / along the road at 1.2 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.53); a culvert within 100 m is overtopped |
| 15 | 1.00 | Route 114 | North Andover | 0.66 m of water at peak; over 30 cm for 3.0 h; 30 cm reached 8.0 h into the storm; worst hour 54 mm (39% of the storm); water beside the road 0.28 m below its crest (design freeboard 0.30 m; P 0.56); a culvert within 100 m is overtopped |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
