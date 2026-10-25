# Road-closure prototype: sep2019e_transfer_sep2019e_clematisbrook_20m

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on CPU (OpenMP)), 20 m grid, storm from 2019-09-02T15:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 24,773 |
| Expected closures (sum of probabilities) | 116.6 |
| Segments with closure probability >= 50% | 79 (19.8 km) |
| Further segments that may close (stream reaches the road crest) | 89 (20.5 km) |
| Culverts overtopped / surcharged | 86 / 2 of 869 |
| Road segments cut off from hospitals | 0 |
| Worst added trip time to a hospital | 0.0 min |
| Heaviest hour of rain | 32.3 mm |
| Flood model run time | 1294 s |


## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 1.00 | Ramp | Weston | 0.73 m of water at peak; over 30 cm for 18.0 h; 30 cm reached 0.5 h into the storm; worst hour 13 mm (72% of the storm); a culvert within 100 m is overtopped |
| 2 | 1.00 | Route 126 | Wayland | 0.71 m of water at peak; worst hour 16 mm (66% of the storm); water beside the road 1.19 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 0.8 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.33); a culvert within 100 m is overtopped |
| 3 | 1.00 | Davelin Road | Wayland | 0.70 m of water at peak; worst hour 18 mm (70% of the storm); water beside the road 3.06 m above its crest (design freeboard 0.30 m; P 1.00); fast water: depth x speed 0.51 m2/s (small cars unstable from 0.3); runoff beside / along the road at 3.8 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 1.00); road sag 0.5 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 18 mm; catchment 3.0 ha) (P 1.00) |
| 4 | 0.99 | Arlo Road | Newton | 0.55 m of water at peak; worst hour 10 mm (77% of the storm); a culvert within 100 m is overtopped |
| 5 | 0.99 | Chestnut Street | Newton | 0.54 m of water at peak; over 30 cm for 18.0 h; 30 cm reached 0.5 h into the storm; worst hour 10 mm (78% of the storm); water beside the road 2.42 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 2.0 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.91); a culvert within 100 m is overtopped |
| 6 | 0.99 | Wallace Road | Wayland | 0.54 m of water at peak; worst hour 15 mm (63% of the storm); a culvert within 100 m is overtopped |
| 7 | 0.99 | Tyler Terrace | Newton | 0.53 m of water at peak; worst hour 12 mm (77% of the storm) |
| 8 | 0.99 | Pleasant Street | Newton | 0.53 m of water at peak; worst hour 12 mm (77% of the storm); water beside the road 3.98 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 1.8 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.90); a culvert within 100 m is overtopped |
| 9 | 0.99 | Highland Street | Weston | 0.53 m of water at peak; worst hour 20 mm (72% of the storm); a culvert within 100 m is overtopped |
| 10 | 0.98 | Saddlebrook Road | Natick | 0.51 m of water at peak; worst hour 15 mm (70% of the storm); a culvert within 100 m is overtopped |
| 11 | 0.98 | Wellesley Street | Weston | 0.50 m of water at peak; worst hour 18 mm (70% of the storm); a culvert within 100 m is overtopped |
| 12 | 0.97 | Bayfield Road | Wayland | 0.49 m of water at peak; worst hour 19 mm (71% of the storm); water beside the road 1.32 m above its crest (design freeboard 0.30 m; P 1.00); fast water: depth x speed 0.28 m2/s (small cars unstable from 0.3); runoff beside / along the road at 1.9 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.86); road sag 2.7 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 18 mm; catchment 114.7 ha) (P 0.40) |
| 13 | 0.97 | Mill Street | Arlington | 0.48 m of water at peak; over 30 cm for 10.5 h; 30 cm reached 8.0 h into the storm; worst hour 26 mm (82% of the storm); a culvert within 100 m is overtopped |
| 14 | 0.97 | Ramp | Weston | 0.48 m of water at peak; over 30 cm for 3.0 h; 30 cm reached 1.0 h into the storm; worst hour 13 mm (70% of the storm); a culvert within 100 m is overtopped |
| 15 | 0.96 | School Street | Wayland | 0.48 m of water at peak; worst hour 19 mm (72% of the storm) |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
