# Road-closure prototype: jul2023c_loss_jul2023c_fitchburg_20m

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on CPU (OpenMP)), 20 m grid, storm from 2023-07-16T07:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 4,614 |
| Expected closures (sum of probabilities) | 112.8 |
| Segments with closure probability >= 50% | 91 (55.4 km) |
| Further segments that may close (stream reaches the road crest) | 112 (66.3 km) |
| Culverts overtopped / surcharged | 114 / 0 of 662 |
| Road segments cut off from hospitals | 638 |
| Worst added trip time to a hospital | 33.1 min |
| Heaviest hour of rain | 35.2 mm |
| Flood model run time | 1319 s |

## Checks against what happened

- Storm-day flood reports in the area: 0; water >= 10 cm within 100 m of 0% of them, vs 61% of random points (any day).
- MassDOT repeating flood sites in the area: 4; 1 have a segment within 150 m at P >= 0.5 (share of all segments at P >= 0.5: 2.0%).

## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 1.00 | Route 2 | Leominster | 1.86 m of water at peak; over 30 cm for 10.0 h; 30 cm reached 8.5 h into the storm; worst hour 16 mm (29% of the storm); a culvert within 100 m is overtopped |
| 2 | 1.00 | (unnamed) | Leominster | 1.20 m of water at peak; over 30 cm for 10.5 h; 30 cm reached 8.0 h into the storm; worst hour 21 mm (32% of the storm); water beside the road 0.23 m below its crest (design freeboard 0.30 m; P 0.69); a culvert within 100 m is overtopped |
| 3 | 1.00 | John Fitch Highway | Fitchburg | 1.06 m of water at peak; over 30 cm for 11.0 h; 30 cm reached 7.5 h into the storm; worst hour 30 mm (38% of the storm); water beside the road 0.42 m below its crest (design freeboard 0.30 m; P 0.22) |
| 4 | 1.00 | Depot Street | Fitchburg | 0.98 m of water at peak; over 30 cm for 14.5 h; 30 cm reached 0.5 h into the storm; worst hour 25 mm (40% of the storm); runoff beside / along the road at 0.8 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.25); a culvert within 100 m is overtopped |
| 5 | 1.00 | Litchfield Street | Leominster | 0.80 m of water at peak; over 30 cm for 9.0 h; 30 cm reached 9.5 h into the storm; worst hour 13 mm (25% of the storm); a culvert within 100 m is overtopped |
| 6 | 1.00 | Water Street | Leominster | 1.20 m of water at peak; over 30 cm for 10.5 h; 30 cm reached 8.0 h into the storm; worst hour 21 mm (33% of the storm); a culvert within 100 m is overtopped |
| 7 | 1.00 | Kingman Drive | Leominster | 0.90 m of water at peak; over 30 cm for 11.0 h; 30 cm reached 7.5 h into the storm; worst hour 28 mm (37% of the storm); water beside the road 0.37 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 1.7 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.60); a culvert within 100 m is overtopped |
| 8 | 1.00 | Litchfield Street | Leominster | 0.66 m of water at peak; over 30 cm for 8.5 h; 30 cm reached 9.0 h into the storm; worst hour 15 mm (28% of the storm) |
| 9 | 1.00 | White Street | Lunenburg | 0.76 m of water at peak; over 30 cm for 5.5 h; 30 cm reached 7.5 h into the storm; worst hour 32 mm (38% of the storm); runoff beside / along the road at 0.8 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.24); a culvert within 100 m is overtopped |
| 10 | 1.00 | Depot Square | Leominster | 1.20 m of water at peak; over 30 cm for 10.5 h; 30 cm reached 8.0 h into the storm; worst hour 21 mm (33% of the storm); a culvert within 100 m is overtopped |
| 11 | 1.00 | Reservoir Road | Lunenburg | 0.95 m of water at peak; over 30 cm for 10.0 h; 30 cm reached 8.5 h into the storm; worst hour 21 mm (34% of the storm); runoff beside / along the road at 0.7 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.13); culvert (N. Branch Catacunemaug): headwater 5.17 m vs road crest 1.07 m, 2.8 m3/s |
| 12 | 1.00 | Sanborn Street | Fitchburg | 0.76 m of water at peak; over 30 cm for 9.5 h; 30 cm reached 7.5 h into the storm; worst hour 23 mm (38% of the storm); runoff beside / along the road at 1.8 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.77); a culvert within 100 m is overtopped |
| 13 | 1.00 | (unnamed) | Lunenburg | 0.73 m of water at peak; over 30 cm for 9.5 h; 30 cm reached 8.0 h into the storm; worst hour 23 mm (36% of the storm); water beside the road 0.12 m above its crest (design freeboard 0.30 m; P 1.00); a culvert within 100 m is overtopped |
| 14 | 1.00 | Commercial Road | Leominster | 1.23 m of water at peak; over 30 cm for 7.5 h; 30 cm reached 9.0 h into the storm; worst hour 17 mm (29% of the storm); a culvert within 100 m is overtopped |
| 15 | 1.00 | (unnamed) | Leominster | 0.81 m of water at peak; over 30 cm for 6.0 h; 30 cm reached 7.0 h into the storm; worst hour 28 mm (38% of the storm) |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
