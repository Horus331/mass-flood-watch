# Road-closure prototype: jun2020f_transfer_jun2020f_weston_20m

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on CPU (OpenMP)), 20 m grid, storm from 2020-06-21T14:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 25,257 |
| Expected closures (sum of probabilities) | 133.4 |
| Segments with closure probability >= 50% | 97 (23.7 km) |
| Further segments that may close (stream reaches the road crest) | 106 (23.6 km) |
| Culverts overtopped / surcharged | 110 / 3 of 922 |
| Road segments cut off from hospitals | 0 |
| Worst added trip time to a hospital | 0.0 min |
| Heaviest hour of rain | 31.1 mm |
| Flood model run time | 914 s |


## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 1.00 | Ramp | Weston | 0.75 m of water at peak; over 30 cm for 18.0 h; 30 cm reached 0.5 h into the storm; worst hour 21 mm (96% of the storm); a culvert within 100 m is overtopped |
| 2 | 1.00 | Route 126 | Wayland | 0.71 m of water at peak; worst hour 10 mm (93% of the storm); water beside the road 1.19 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 0.8 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.33); a culvert within 100 m is overtopped |
| 3 | 1.00 | Davelin Road | Wayland | 0.70 m of water at peak; worst hour 14 mm (94% of the storm); water beside the road 3.06 m above its crest (design freeboard 0.30 m; P 1.00); fast water: depth x speed 0.51 m2/s (small cars unstable from 0.3); runoff beside / along the road at 3.8 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 1.00); road sag 0.5 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 13 mm; catchment 3.0 ha) (P 1.00) |
| 4 | 1.00 | Union Street | Natick | 0.62 m of water at peak; worst hour 11 mm (59% of the storm); a culvert within 100 m is overtopped |
| 5 | 1.00 | Wild Meadow Lane | Natick | 0.62 m of water at peak; worst hour 3 mm (69% of the storm); a culvert within 100 m is overtopped |
| 6 | 0.99 | Arlo Road | Newton | 0.55 m of water at peak; worst hour 8 mm (87% of the storm); a culvert within 100 m is overtopped |
| 7 | 0.99 | Chestnut Street | Newton | 0.54 m of water at peak; over 30 cm for 18.0 h; 30 cm reached 0.5 h into the storm; worst hour 7 mm (90% of the storm); water beside the road 2.42 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 2.0 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.91); a culvert within 100 m is overtopped |
| 8 | 0.99 | Wallace Road | Wayland | 0.54 m of water at peak; worst hour 9 mm (94% of the storm); a culvert within 100 m is overtopped |
| 9 | 0.99 | Tyler Terrace | Newton | 0.53 m of water at peak; worst hour 8 mm (85% of the storm) |
| 10 | 0.99 | Pleasant Street | Newton | 0.53 m of water at peak; worst hour 8 mm (85% of the storm); water beside the road 3.98 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 1.8 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.90); a culvert within 100 m is overtopped |
| 11 | 0.99 | Highland Street | Weston | 0.53 m of water at peak; worst hour 11 mm (94% of the storm); a culvert within 100 m is overtopped |
| 12 | 0.98 | Saddlebrook Road | Natick | 0.51 m of water at peak; worst hour 12 mm (91% of the storm); a culvert within 100 m is overtopped |
| 13 | 0.98 | Leach Lane | Natick | 0.50 m of water at peak; worst hour 11 mm (63% of the storm); water beside the road 1.25 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 1.9 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.84); a culvert within 100 m is overtopped |
| 14 | 0.98 | Wellesley Street | Weston | 0.50 m of water at peak; worst hour 15 mm (95% of the storm); a culvert within 100 m is overtopped |
| 15 | 0.97 | Bayfield Road | Wayland | 0.49 m of water at peak; worst hour 18 mm (95% of the storm); water beside the road 1.32 m above its crest (design freeboard 0.30 m; P 1.00); fast water: depth x speed 0.28 m2/s (small cars unstable from 0.3); runoff beside / along the road at 1.9 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.86); road sag 2.7 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 16 mm; catchment 114.7 ha) (P 0.40) |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
