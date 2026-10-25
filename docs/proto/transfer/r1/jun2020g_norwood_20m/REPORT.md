# Road-closure prototype: jun2020g_transfer_jun2020g_norwood_20m

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on CPU (OpenMP)), 20 m grid, storm from 2020-06-28T13:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 16,053 |
| Expected closures (sum of probabilities) | 38.4 |
| Segments with closure probability >= 50% | 3 (0.6 km) |
| Further segments that may close (stream reaches the road crest) | 20 (2.6 km) |
| Culverts overtopped / surcharged | 37 / 0 of 824 |
| Road segments cut off from hospitals | 0 |
| Worst added trip time to a hospital | 0.0 min |
| Heaviest hour of rain | 47.7 mm |
| Flood model run time | 1340 s |


## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 0.89 | Nahatan Street | Norwood | 0.42 m of water at peak; over 30 cm for 2.5 h; 30 cm reached 8.5 h into the storm; worst hour 45 mm (60% of the storm); water beside the road 0.83 m above its crest (design freeboard 0.30 m; P 1.00); fast water: depth x speed 0.22 m2/s (small cars unstable from 0.3); runoff beside / along the road at 0.8 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.36); road sag 0.6 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 45 mm; catchment 11.2 ha) (P 1.00) |
| 2 | 0.63 | Allen Road | Norwood | 0.33 m of water at peak; over 30 cm for 1.5 h; 30 cm reached 10.0 h into the storm; worst hour 41 mm (62% of the storm); water beside the road 0.27 m above its crest (design freeboard 0.30 m; P 1.00) |
| 3 | 0.55 | Route 1A | Norwood | 0.31 m of water at peak; over 30 cm for 1.5 h; 30 cm reached 17.0 h into the storm; worst hour 46 mm (59% of the storm); water beside the road 0.17 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 2.4 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.18); a culvert within 100 m is overtopped |
| 4 | 0.29 | Ellsworth Street | Brockton | 0.24 m of water at peak; worst hour 26 mm (69% of the storm); a culvert within 100 m is overtopped |
| 5 | 0.29 | Ellsworth Street | Brockton | 0.24 m of water at peak; worst hour 26 mm (69% of the storm) |
| 6 | 0.28 | Ellsworth Street | Brockton | 0.24 m of water at peak; worst hour 26 mm (69% of the storm); a culvert within 100 m is overtopped |
| 7 | 0.28 | Carleton Street | Brockton | 0.24 m of water at peak; worst hour 26 mm (69% of the storm); a culvert within 100 m is overtopped |
| 8 | 0.28 | Carleton Street | Brockton | 0.24 m of water at peak; worst hour 26 mm (69% of the storm); a culvert within 100 m is overtopped |
| 9 | 0.25 | Route 1 | Norwood | 0.23 m of water at peak; worst hour 46 mm (59% of the storm); a culvert within 100 m is overtopped |
| 10 | 0.24 | Spring Street | Foxborough | 0.23 m of water at peak; worst hour 32 mm (76% of the storm) |
| 11 | 0.24 | Spring Street | Foxborough | 0.23 m of water at peak; worst hour 32 mm (76% of the storm); a culvert within 100 m is overtopped |
| 12 | 0.24 | Spring Street | Foxborough | 0.23 m of water at peak; worst hour 32 mm (76% of the storm) |
| 13 | 0.24 | Hope Avenue | Foxborough | 0.23 m of water at peak; worst hour 32 mm (76% of the storm) |
| 14 | 0.23 | Torrey Street | Brockton | 0.23 m of water at peak; worst hour 27 mm (64% of the storm); a culvert within 100 m is overtopped |
| 15 | 0.22 | Route 123 | Brockton | 0.22 m of water at peak; worst hour 25 mm (58% of the storm); a culvert within 100 m is overtopped |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
