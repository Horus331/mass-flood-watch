# Road-closure prototype: jun2018e_transfer_jun2018e_concord_20m

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on CPU (OpenMP)), 20 m grid, storm from 2018-06-24T22:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 10,199 |
| Expected closures (sum of probabilities) | 23.3 |
| Segments with closure probability >= 50% | 8 (4.5 km) |
| Further segments that may close (stream reaches the road crest) | 3 (0.9 km) |
| Culverts overtopped / surcharged | 19 / 1 of 711 |
| Road segments cut off from hospitals | 0 |
| Worst added trip time to a hospital | 0.0 min |
| Heaviest hour of rain | 18.1 mm |
| Flood model run time | 926 s |


## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 0.99 | Highland Street | Weston | 0.53 m of water at peak; worst hour 7 mm (34% of the storm); a culvert within 100 m is overtopped |
| 2 | 0.98 | Wellesley Street | Weston | 0.50 m of water at peak; worst hour 8 mm (36% of the storm); a culvert within 100 m is overtopped |
| 3 | 0.95 | Herland Way | Wayland | 0.46 m of water at peak; worst hour 6 mm (32% of the storm); water beside the road 0.27 m below its crest (design freeboard 0.30 m; P 0.59); runoff beside / along the road at 1.0 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.51); a culvert within 100 m is overtopped |
| 4 | 0.90 | Newton Street | Weston | 0.43 m of water at peak; worst hour 5 mm (32% of the storm); a culvert within 100 m is overtopped |
| 5 | 0.89 | Forty Acres Drive | Wayland | 0.42 m of water at peak; worst hour 7 mm (33% of the storm); water beside the road 5.26 m above its crest (design freeboard 0.30 m; P 1.00); fast water: depth x speed 0.51 m2/s (small cars unstable from 0.3); runoff beside / along the road at 3.7 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 1.00); culvert (Trib. to Pine Brook): headwater 2.09 m vs road crest 1.83 m, 1.0 m3/s |
| 6 | 0.76 | Route 27 | Wayland | 0.37 m of water at peak; over 30 cm for 1.5 h; 30 cm reached 1.0 h into the storm; worst hour 7 mm (34% of the storm) |
| 7 | 0.69 | Pinebrook Road | Wayland | 0.35 m of water at peak; over 30 cm for 0.5 h; 30 cm reached 0.5 h into the storm; worst hour 8 mm (35% of the storm); water beside the road 2.61 m above its crest (design freeboard 0.30 m; P 1.00); fast water: depth x speed 0.33 m2/s (small cars unstable from 0.3); runoff beside / along the road at 2.0 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.92); culvert (UNT to Pine Brook): headwater 35.02 m vs road crest 0.61 m, 1.2 m3/s |
| 8 | 0.60 | Young Road | Weston | 0.33 m of water at peak; worst hour 5 mm (33% of the storm) |
| 9 | 0.26 | Ware Street | Weston | 0.23 m of water at peak; worst hour 5 mm (33% of the storm); a culvert within 100 m is overtopped |
| 10 | 0.16 | Route 126 | Wayland | 0.20 m of water at peak; worst hour 6 mm (32% of the storm); runoff beside / along the road at 0.9 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.18) |
| 11 | 0.15 | Davelin Road | Wayland | 0.20 m of water at peak; worst hour 6 mm (32% of the storm); water beside the road 1.54 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 1.4 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.67); road sag 0.5 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 6 mm; catchment 1.1 ha) (P 0.15) |
| 12 | 0.15 | Route 126 | Wayland | 0.20 m of water at peak; worst hour 6 mm (32% of the storm); a culvert within 100 m is overtopped |
| 13 | 0.11 | Shawsheen Road | Bedford | 0.18 m of water at peak; worst hour 5 mm (40% of the storm); a culvert within 100 m is overtopped |
| 14 | 0.11 | Page Road | Bedford | 0.18 m of water at peak; worst hour 5 mm (40% of the storm) |
| 15 | 0.11 | Page Road | Bedford | 0.18 m of water at peak; worst hour 5 mm (40% of the storm) |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
