# Road-closure prototype: aug2023_transfer_aug2023_metrowest_20m

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on CPU (OpenMP)), 20 m grid, storm from 2023-08-08T07:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 10,795 |
| Expected closures (sum of probabilities) | 119.1 |
| Segments with closure probability >= 50% | 82 (23.2 km) |
| Further segments that may close (stream reaches the road crest) | 98 (20.7 km) |
| Culverts overtopped / surcharged | 156 / 1 of 998 |
| Road segments cut off from hospitals | 0 |
| Worst added trip time to a hospital | 0.0 min |
| Heaviest hour of rain | 63.6 mm |
| Flood model run time | 1584 s |


## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 1.00 | Ridge Street | Millis | 0.78 m of water at peak; over 30 cm for 11.0 h; 30 cm reached 7.5 h into the storm; worst hour 54 mm (60% of the storm) |
| 2 | 1.00 | Ridge Street | Millis | 0.78 m of water at peak; over 30 cm for 11.0 h; 30 cm reached 7.5 h into the storm; worst hour 53 mm (59% of the storm) |
| 3 | 1.00 | Route 126 | Wayland | 0.71 m of water at peak; worst hour 36 mm (45% of the storm); water beside the road 1.19 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 0.8 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.33); a culvert within 100 m is overtopped |
| 4 | 1.00 | Irving Street | Framingham | 0.61 m of water at peak; over 30 cm for 15.5 h; 30 cm reached 0.5 h into the storm; worst hour 34 mm (46% of the storm); a culvert within 100 m is overtopped |
| 5 | 1.00 | Millwood Street | Framingham | 0.60 m of water at peak; over 30 cm for 7.5 h; 30 cm reached 0.5 h into the storm; worst hour 20 mm (28% of the storm); water beside the road 0.49 m below its crest (design freeboard 0.30 m; P 0.11); a culvert within 100 m is overtopped |
| 6 | 1.00 | Wild Meadow Lane | Natick | 0.62 m of water at peak; worst hour 41 mm (57% of the storm); a culvert within 100 m is overtopped |
| 7 | 1.00 | Route 135 | Natick | 0.59 m of water at peak; over 30 cm for 13.0 h; 30 cm reached 2.5 h into the storm; worst hour 34 mm (46% of the storm); a culvert within 100 m is overtopped |
| 8 | 1.00 | Little Tree Lane | Framingham | 0.58 m of water at peak; over 30 cm for 11.5 h; 30 cm reached 1.0 h into the storm; worst hour 22 mm (32% of the storm); a culvert within 100 m is overtopped |
| 9 | 1.00 | Amy Road | Framingham | 0.57 m of water at peak; over 30 cm for 0.5 h; 30 cm reached 0.5 h into the storm; worst hour 24 mm (35% of the storm); water beside the road 1.69 m above its crest (design freeboard 0.30 m; P 1.00); fast water: depth x speed 0.40 m2/s (small cars unstable from 0.3); runoff beside / along the road at 1.3 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.70); road sag 0.5 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 24 mm; catchment 15.6 ha) (P 1.00) |
| 10 | 0.99 | Flanagan Drive | Framingham | 0.56 m of water at peak; worst hour 18 mm (24% of the storm); water beside the road 0.21 m above its crest (design freeboard 0.30 m; P 1.00); a culvert within 100 m is overtopped |
| 11 | 0.99 | Wallace Road | Wayland | 0.54 m of water at peak; worst hour 34 mm (44% of the storm); a culvert within 100 m is overtopped |
| 12 | 0.99 | Davelin Road | Wayland | 0.54 m of water at peak; worst hour 38 mm (49% of the storm); water beside the road 3.06 m above its crest (design freeboard 0.30 m; P 1.00); fast water: depth x speed 0.51 m2/s (small cars unstable from 0.3); runoff beside / along the road at 3.8 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 1.00) |
| 13 | 0.99 | Merchant Road | Framingham | 0.53 m of water at peak; over 30 cm for 10.0 h; 30 cm reached 8.0 h into the storm; worst hour 35 mm (45% of the storm); a culvert within 100 m is overtopped |
| 14 | 0.99 | Orchard Street | Millis | 0.53 m of water at peak; over 30 cm for 11.0 h; 30 cm reached 7.5 h into the storm; worst hour 44 mm (54% of the storm) |
| 15 | 0.98 | Flanagan Drive | Framingham | 0.51 m of water at peak; worst hour 17 mm (24% of the storm); water beside the road 0.28 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 0.9 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.45); a culvert within 100 m is overtopped |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
