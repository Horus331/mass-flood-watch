# Road-closure prototype: jul2023c_loss_jul2023c_fitchburg_20m

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on CPU (OpenMP)), 20 m grid, storm from 2023-07-16T07:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 4,614 |
| Expected closures (sum of probabilities) | 36.9 |
| Segments with closure probability >= 50% | 18 (11.8 km) |
| Further segments that may close (stream reaches the road crest) | 35 (18.5 km) |
| Culverts overtopped / surcharged | 45 / 0 of 662 |
| Road segments cut off from hospitals | 204 |
| Worst added trip time to a hospital | 27.6 min |
| Heaviest hour of rain | 35.2 mm |
| Flood model run time | 1429 s |

## Checks against what happened

- Storm-day flood reports in the area: 0; water >= 10 cm within 100 m of 0% of them, vs 46% of random points (any day).
- MassDOT repeating flood sites in the area: 4; 1 have a segment within 150 m at P >= 0.5 (share of all segments at P >= 0.5: 0.4%).

## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 1.00 | (unnamed) | Leominster | 0.62 m of water at peak; over 30 cm for 9.5 h; 30 cm reached 9.0 h into the storm; worst hour 21 mm (32% of the storm); a culvert within 100 m is overtopped |
| 2 | 1.00 | Water Street | Leominster | 0.62 m of water at peak; over 30 cm for 9.5 h; 30 cm reached 9.0 h into the storm; worst hour 21 mm (33% of the storm); a culvert within 100 m is overtopped |
| 3 | 1.00 | Depot Square | Leominster | 0.62 m of water at peak; over 30 cm for 9.5 h; 30 cm reached 9.0 h into the storm; worst hour 21 mm (33% of the storm); a culvert within 100 m is overtopped |
| 4 | 1.00 | John Fitch Highway | Fitchburg | 0.57 m of water at peak; over 30 cm for 6.5 h; 30 cm reached 8.5 h into the storm; worst hour 30 mm (38% of the storm) |
| 5 | 0.98 | Kingman Drive | Leominster | 0.50 m of water at peak; over 30 cm for 4.5 h; 30 cm reached 8.5 h into the storm; worst hour 28 mm (37% of the storm); runoff beside / along the road at 0.8 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.28); a culvert within 100 m is overtopped |
| 6 | 0.93 | Depot Street | Fitchburg | 0.45 m of water at peak; over 30 cm for 12.5 h; 30 cm reached 0.5 h into the storm; worst hour 25 mm (40% of the storm); runoff beside / along the road at 0.7 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.14); a culvert within 100 m is overtopped |
| 7 | 0.90 | Reservoir Road | Lunenburg | 0.43 m of water at peak; over 30 cm for 5.5 h; 30 cm reached 10.5 h into the storm; worst hour 21 mm (34% of the storm) |
| 8 | 0.85 | Exchange Street | Leominster | 0.41 m of water at peak; over 30 cm for 2.5 h; 30 cm reached 8.5 h into the storm; worst hour 29 mm (38% of the storm); water beside the road 0.61 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 1.8 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.89); a culvert within 100 m is overtopped |
| 9 | 0.80 | Commercial Road | Leominster | 0.38 m of water at peak; over 30 cm for 2.5 h; 30 cm reached 10.5 h into the storm; worst hour 17 mm (29% of the storm); a culvert within 100 m is overtopped |
| 10 | 0.80 | Constitution Drive | Leominster | 0.38 m of water at peak; over 30 cm for 2.0 h; 30 cm reached 8.5 h into the storm; worst hour 29 mm (38% of the storm) |
| 11 | 0.79 | (unnamed) | Lunenburg | 0.38 m of water at peak; over 30 cm for 3.0 h; 30 cm reached 10.0 h into the storm; worst hour 23 mm (36% of the storm); water beside the road 0.22 m below its crest (design freeboard 0.30 m; P 0.71); a culvert within 100 m is overtopped |
| 12 | 0.70 | (unnamed) | Leominster | 0.35 m of water at peak; over 30 cm for 2.0 h; 30 cm reached 8.5 h into the storm; worst hour 28 mm (38% of the storm) |
| 13 | 0.66 | Route 13 | Lunenburg | 0.34 m of water at peak; over 30 cm for 1.0 h; 30 cm reached 9.0 h into the storm; worst hour 32 mm (42% of the storm); water beside the road 0.16 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 0.9 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.15); a culvert within 100 m is overtopped |
| 14 | 0.62 | White Street | Lunenburg | 0.33 m of water at peak; over 30 cm for 1.5 h; 30 cm reached 9.0 h into the storm; worst hour 32 mm (38% of the storm); a culvert within 100 m is overtopped |
| 15 | 0.59 | Litchfield Street | Leominster | 0.32 m of water at peak; over 30 cm for 3.0 h; 30 cm reached 13.0 h into the storm; worst hour 13 mm (25% of the storm); a culvert within 100 m is overtopped |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
