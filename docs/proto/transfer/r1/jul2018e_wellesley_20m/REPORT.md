# Road-closure prototype: jul2018e_transfer_jul2018e_wellesley_20m

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on CPU (OpenMP)), 20 m grid, storm from 2018-07-17T11:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 20,459 |
| Expected closures (sum of probabilities) | 115.1 |
| Segments with closure probability >= 50% | 83 (19.9 km) |
| Further segments that may close (stream reaches the road crest) | 92 (22.0 km) |
| Culverts overtopped / surcharged | 91 / 2 of 898 |
| Road segments cut off from hospitals | 0 |
| Worst added trip time to a hospital | 0.0 min |
| Heaviest hour of rain | 21.4 mm |
| Flood model run time | 848 s |


## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 1.00 | Ramp | Weston | 0.79 m of water at peak; over 30 cm for 18.0 h; 30 cm reached 0.5 h into the storm; worst hour 13 mm (29% of the storm); a culvert within 100 m is overtopped |
| 2 | 1.00 | Route 126 | Wayland | 0.71 m of water at peak; worst hour 19 mm (39% of the storm); water beside the road 1.19 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 0.8 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.33); a culvert within 100 m is overtopped |
| 3 | 1.00 | Davelin Road | Wayland | 0.70 m of water at peak; worst hour 19 mm (39% of the storm); water beside the road 3.06 m above its crest (design freeboard 0.30 m; P 1.00); fast water: depth x speed 0.51 m2/s (small cars unstable from 0.3); runoff beside / along the road at 3.8 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 1.00); road sag 0.5 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 18 mm; catchment 3.0 ha) (P 1.00) |
| 4 | 0.99 | Arlo Road | Newton | 0.55 m of water at peak; worst hour 17 mm (33% of the storm); a culvert within 100 m is overtopped |
| 5 | 0.99 | Chestnut Street | Newton | 0.54 m of water at peak; over 30 cm for 18.0 h; 30 cm reached 0.5 h into the storm; worst hour 18 mm (34% of the storm); water beside the road 2.42 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 2.0 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.91); a culvert within 100 m is overtopped |
| 6 | 0.99 | Wallace Road | Wayland | 0.54 m of water at peak; worst hour 19 mm (38% of the storm); a culvert within 100 m is overtopped |
| 7 | 0.99 | Tyler Terrace | Newton | 0.53 m of water at peak; worst hour 13 mm (28% of the storm) |
| 8 | 0.99 | Pleasant Street | Newton | 0.53 m of water at peak; worst hour 13 mm (28% of the storm); water beside the road 3.98 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 2.2 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.82); a culvert within 100 m is overtopped |
| 9 | 0.99 | Highland Street | Weston | 0.53 m of water at peak; worst hour 13 mm (32% of the storm); a culvert within 100 m is overtopped |
| 10 | 0.98 | Saddlebrook Road | Natick | 0.51 m of water at peak; worst hour 16 mm (30% of the storm); a culvert within 100 m is overtopped |
| 11 | 0.98 | Wellesley Street | Weston | 0.50 m of water at peak; worst hour 12 mm (30% of the storm); a culvert within 100 m is overtopped |
| 12 | 0.97 | Bayfield Road | Wayland | 0.49 m of water at peak; worst hour 21 mm (40% of the storm); water beside the road 1.32 m above its crest (design freeboard 0.30 m; P 1.00); fast water: depth x speed 0.28 m2/s (small cars unstable from 0.3); runoff beside / along the road at 1.9 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.86); road sag 2.7 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 21 mm; catchment 114.7 ha) (P 0.40) |
| 13 | 0.97 | Ramp | Weston | 0.48 m of water at peak; over 30 cm for 3.0 h; 30 cm reached 1.0 h into the storm; worst hour 14 mm (30% of the storm); a culvert within 100 m is overtopped |
| 14 | 0.96 | School Street | Wayland | 0.48 m of water at peak; worst hour 21 mm (39% of the storm) |
| 15 | 0.95 | Willow Street | Newton | 0.47 m of water at peak; worst hour 12 mm (26% of the storm); a culvert within 100 m is overtopped |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
