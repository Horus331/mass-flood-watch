# Road-closure prototype: sep2023g_transfer_sep2023g_tauntonap_20m

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on CPU (OpenMP)), 20 m grid, storm from 2023-09-11T11:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 6,655 |
| Expected closures (sum of probabilities) | 15.6 |
| Segments with closure probability >= 50% | 4 (1.0 km) |
| Further segments that may close (stream reaches the road crest) | 2 (0.3 km) |
| Culverts overtopped / surcharged | 12 / 0 of 464 |
| Road segments cut off from hospitals | 0 |
| Worst added trip time to a hospital | 0.0 min |
| Heaviest hour of rain | 37.4 mm |
| Flood model run time | 1404 s |


## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 0.61 | Ocean Spray Drive | Middleborough | 0.33 m of water at peak; over 30 cm for 5.0 h; 30 cm reached 13.5 h into the storm; worst hour 25 mm (34% of the storm); a culvert within 100 m is overtopped |
| 2 | 0.60 | (unnamed) | Taunton | 0.33 m of water at peak; over 30 cm for 2.5 h; 30 cm reached 11.0 h into the storm; worst hour 18 mm (33% of the storm); a culvert within 100 m is overtopped |
| 3 | 0.60 | (unnamed) | Taunton | 0.33 m of water at peak; over 30 cm for 2.5 h; 30 cm reached 11.0 h into the storm; worst hour 18 mm (33% of the storm); a culvert within 100 m is overtopped |
| 4 | 0.60 | (unnamed) | Taunton | 0.33 m of water at peak; over 30 cm for 2.5 h; 30 cm reached 11.0 h into the storm; worst hour 18 mm (32% of the storm) |
| 5 | 0.41 | Mayflower Avenue | Middleborough | 0.28 m of water at peak; worst hour 24 mm (33% of the storm); water beside the road 0.01 m below its crest (design freeboard 0.30 m; P 0.97) |
| 6 | 0.39 | Vernon Street | Middleborough | 0.27 m of water at peak; worst hour 22 mm (33% of the storm); a culvert within 100 m is overtopped |
| 7 | 0.32 | Route 140 | Lakeville | 0.25 m of water at peak; worst hour 24 mm (47% of the storm); a culvert within 100 m is overtopped |
| 8 | 0.21 | Mill Street | Middleborough | 0.22 m of water at peak; worst hour 25 mm (35% of the storm); a culvert within 100 m is overtopped |
| 9 | 0.11 | Taunton Street | Lakeville | 0.18 m of water at peak; worst hour 24 mm (32% of the storm); a culvert within 100 m is overtopped |
| 10 | 0.11 | Dean Street | Raynham | 0.18 m of water at peak; worst hour 22 mm (30% of the storm); a culvert within 100 m is overtopped |
| 11 | 0.09 | Mayflower Avenue | Middleborough | 0.17 m of water at peak; worst hour 24 mm (34% of the storm); water beside the road 0.16 m above its crest (design freeboard 0.30 m; P 1.00) |
| 12 | 0.09 | Susan Lane | Lakeville | 0.17 m of water at peak; worst hour 26 mm (46% of the storm); a culvert within 100 m is overtopped |
| 13 | 0.08 | Stetson Street | Lakeville | 0.16 m of water at peak; worst hour 30 mm (33% of the storm); runoff beside / along the road at 0.4 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.13); a culvert within 100 m is overtopped |
| 14 | 0.07 | Kingman Street | Lakeville | 0.15 m of water at peak; worst hour 19 mm (36% of the storm); a culvert within 100 m is overtopped |
| 15 | 0.05 | North Walker Street | Taunton | 0.14 m of water at peak; worst hour 22 mm (35% of the storm) |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
