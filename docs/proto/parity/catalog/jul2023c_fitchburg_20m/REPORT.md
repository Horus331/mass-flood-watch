# Road-closure prototype: jul2023c_loss_jul2023c_fitchburg_20m

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on CPU (OpenMP)), 20 m grid, storm from 2023-07-16T07:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 4,614 |
| Expected closures (sum of probabilities) | 41.8 |
| Segments with closure probability >= 50% | 22 (15.0 km) |
| Further segments that may close (stream reaches the road crest) | 33 (18.3 km) |
| Culverts overtopped / surcharged | 55 / 0 of 662 |
| Road segments cut off from hospitals | 226 |
| Worst added trip time to a hospital | 26.2 min |
| Heaviest hour of rain | 35.2 mm |
| Flood model run time | 996 s |

## Checks against what happened

- Storm-day flood reports in the area: 0; water >= 10 cm within 100 m of 0% of them, vs 48% of random points (any day).
- MassDOT repeating flood sites in the area: 4; 0 have a segment within 150 m at P >= 0.5 (share of all segments at P >= 0.5: 0.5%).

## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 1.00 | (unnamed) | Leominster | 0.76 m of water at peak; over 30 cm for 9.5 h; 30 cm reached 9.0 h into the storm; worst hour 21 mm (32% of the storm); a culvert within 100 m is overtopped |
| 2 | 1.00 | Water Street | Leominster | 0.76 m of water at peak; over 30 cm for 9.5 h; 30 cm reached 9.0 h into the storm; worst hour 21 mm (33% of the storm); a culvert within 100 m is overtopped |
| 3 | 1.00 | Depot Square | Leominster | 0.76 m of water at peak; over 30 cm for 9.5 h; 30 cm reached 9.0 h into the storm; worst hour 21 mm (33% of the storm); a culvert within 100 m is overtopped |
| 4 | 1.00 | John Fitch Highway | Fitchburg | 0.62 m of water at peak; over 30 cm for 8.0 h; 30 cm reached 8.5 h into the storm; worst hour 30 mm (38% of the storm) |
| 5 | 1.00 | Route 2 | Leominster | 0.57 m of water at peak; over 30 cm for 9.0 h; 30 cm reached 9.5 h into the storm; worst hour 16 mm (29% of the storm); a culvert within 100 m is overtopped |
| 6 | 0.98 | (unnamed) | Lunenburg | 0.51 m of water at peak; over 30 cm for 7.0 h; 30 cm reached 9.5 h into the storm; worst hour 23 mm (36% of the storm); water beside the road 0.20 m below its crest (design freeboard 0.30 m; P 0.76); a culvert within 100 m is overtopped |
| 7 | 0.98 | (unnamed) | Leominster | 0.50 m of water at peak; over 30 cm for 3.0 h; 30 cm reached 8.5 h into the storm; worst hour 28 mm (38% of the storm) |
| 8 | 0.97 | Exchange Street | Leominster | 0.49 m of water at peak; over 30 cm for 3.0 h; 30 cm reached 8.5 h into the storm; worst hour 29 mm (38% of the storm); water beside the road 0.62 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 2.6 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.94); a culvert within 100 m is overtopped |
| 9 | 0.96 | Kingman Drive | Leominster | 0.48 m of water at peak; over 30 cm for 5.0 h; 30 cm reached 8.5 h into the storm; worst hour 28 mm (37% of the storm); runoff beside / along the road at 0.8 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.33); a culvert within 100 m is overtopped |
| 10 | 0.95 | Reservoir Road | Lunenburg | 0.46 m of water at peak; over 30 cm for 6.5 h; 30 cm reached 10.5 h into the storm; worst hour 21 mm (34% of the storm) |
| 11 | 0.94 | Depot Street | Fitchburg | 0.46 m of water at peak; over 30 cm for 13.5 h; 30 cm reached 0.5 h into the storm; worst hour 25 mm (40% of the storm); runoff beside / along the road at 0.7 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.14); a culvert within 100 m is overtopped |
| 12 | 0.91 | Constitution Drive | Leominster | 0.43 m of water at peak; over 30 cm for 2.5 h; 30 cm reached 8.5 h into the storm; worst hour 29 mm (38% of the storm) |
| 13 | 0.75 | Litchfield Street | Leominster | 0.37 m of water at peak; over 30 cm for 5.5 h; 30 cm reached 13.0 h into the storm; worst hour 13 mm (25% of the storm); a culvert within 100 m is overtopped |
| 14 | 0.75 | White Street | Lunenburg | 0.37 m of water at peak; over 30 cm for 2.0 h; 30 cm reached 9.0 h into the storm; worst hour 32 mm (38% of the storm); a culvert within 100 m is overtopped |
| 15 | 0.70 | Commercial Road | Leominster | 0.35 m of water at peak; over 30 cm for 3.0 h; 30 cm reached 10.5 h into the storm; worst hour 17 mm (29% of the storm); a culvert within 100 m is overtopped |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
