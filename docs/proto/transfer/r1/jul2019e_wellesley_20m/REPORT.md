# Road-closure prototype: jul2019e_transfer_jul2019e_wellesley_20m

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on CPU (OpenMP)), 20 m grid, storm from 2019-07-06T14:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 29,137 |
| Expected closures (sum of probabilities) | 134.5 |
| Segments with closure probability >= 50% | 92 (23.0 km) |
| Further segments that may close (stream reaches the road crest) | 98 (21.7 km) |
| Culverts overtopped / surcharged | 104 / 3 of 893 |
| Road segments cut off from hospitals | 0 |
| Worst added trip time to a hospital | 0.0 min |
| Heaviest hour of rain | 48.6 mm |
| Flood model run time | 728 s |


## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 1.00 | Ramp | Weston | 0.92 m of water at peak; over 30 cm for 18.0 h; 30 cm reached 0.5 h into the storm; worst hour 29 mm (80% of the storm); a culvert within 100 m is overtopped |
| 2 | 1.00 | Davelin Road | Wayland | 0.70 m of water at peak; worst hour 43 mm (80% of the storm); water beside the road 3.06 m above its crest (design freeboard 0.30 m; P 1.00); fast water: depth x speed 0.51 m2/s (small cars unstable from 0.3); runoff beside / along the road at 3.8 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 1.00); road sag 0.5 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 42 mm; catchment 3.0 ha) (P 1.00) |
| 3 | 1.00 | Union Street | Natick | 0.62 m of water at peak; worst hour 35 mm (84% of the storm); a culvert within 100 m is overtopped |
| 4 | 1.00 | Wild Meadow Lane | Natick | 0.62 m of water at peak; worst hour 32 mm (86% of the storm); a culvert within 100 m is overtopped |
| 5 | 0.99 | Bayfield Road | Wayland | 0.56 m of water at peak; over 30 cm for 1.5 h; 30 cm reached 0.5 h into the storm; worst hour 48 mm (83% of the storm); water beside the road 1.32 m above its crest (design freeboard 0.30 m; P 1.00); fast water: depth x speed 0.28 m2/s (small cars unstable from 0.3); runoff beside / along the road at 1.9 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.86) |
| 6 | 0.99 | Arlo Road | Newton | 0.55 m of water at peak; worst hour 23 mm (67% of the storm); a culvert within 100 m is overtopped |
| 7 | 0.99 | Chestnut Street | Newton | 0.54 m of water at peak; over 30 cm for 18.0 h; 30 cm reached 0.5 h into the storm; worst hour 24 mm (64% of the storm); water beside the road 2.42 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 2.0 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.91); a culvert within 100 m is overtopped |
| 8 | 0.99 | Tyler Terrace | Newton | 0.53 m of water at peak; worst hour 20 mm (71% of the storm) |
| 9 | 0.99 | Pleasant Street | Newton | 0.53 m of water at peak; worst hour 20 mm (71% of the storm); water beside the road 3.98 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 1.8 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.90); a culvert within 100 m is overtopped |
| 10 | 0.99 | Highland Street | Weston | 0.53 m of water at peak; worst hour 30 mm (82% of the storm); a culvert within 100 m is overtopped |
| 11 | 0.98 | Saddlebrook Road | Natick | 0.51 m of water at peak; worst hour 37 mm (83% of the storm); a culvert within 100 m is overtopped |
| 12 | 0.98 | Leach Lane | Natick | 0.50 m of water at peak; worst hour 40 mm (85% of the storm); water beside the road 1.25 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 1.9 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.84); a culvert within 100 m is overtopped |
| 13 | 0.98 | Wellesley Street | Weston | 0.50 m of water at peak; worst hour 27 mm (82% of the storm); a culvert within 100 m is overtopped |
| 14 | 0.97 | Route 27 | Sherborn | 0.49 m of water at peak; over 30 cm for 0.5 h; 30 cm reached 0.5 h into the storm; worst hour 40 mm (88% of the storm); a culvert within 100 m is overtopped |
| 15 | 0.97 | Ramp | Weston | 0.48 m of water at peak; over 30 cm for 3.5 h; 30 cm reached 1.0 h into the storm; worst hour 31 mm (81% of the storm); a culvert within 100 m is overtopped |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
