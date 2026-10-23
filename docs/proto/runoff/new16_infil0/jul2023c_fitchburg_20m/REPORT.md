# Road-closure prototype: jul2023c_loss_jul2023c_fitchburg_20m

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on CPU (OpenMP)), 20 m grid, storm from 2023-07-16T07:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 4,614 |
| Expected closures (sum of probabilities) | 64.7 |
| Segments with closure probability >= 50% | 37 (25.9 km) |
| Further segments that may close (stream reaches the road crest) | 54 (30.7 km) |
| Culverts overtopped / surcharged | 91 / 0 of 662 |
| Road segments cut off from hospitals | 405 |
| Worst added trip time to a hospital | 25.7 min |
| Heaviest hour of rain | 35.2 mm |
| Flood model run time | 1321 s |

## Checks against what happened

- Storm-day flood reports in the area: 0; water >= 10 cm within 100 m of 0% of them, vs 55% of random points (any day).
- MassDOT repeating flood sites in the area: 4; 1 have a segment within 150 m at P >= 0.5 (share of all segments at P >= 0.5: 0.8%).

## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 1.00 | Route 2 | Leominster | 1.31 m of water at peak; over 30 cm for 10.0 h; 30 cm reached 8.5 h into the storm; worst hour 16 mm (29% of the storm); a culvert within 100 m is overtopped |
| 2 | 1.00 | (unnamed) | Leominster | 0.94 m of water at peak; over 30 cm for 10.0 h; 30 cm reached 8.5 h into the storm; worst hour 21 mm (32% of the storm); a culvert within 100 m is overtopped |
| 3 | 1.00 | John Fitch Highway | Fitchburg | 0.77 m of water at peak; over 30 cm for 10.5 h; 30 cm reached 8.0 h into the storm; worst hour 30 mm (38% of the storm); water beside the road 0.49 m below its crest (design freeboard 0.30 m; P 0.10) |
| 4 | 1.00 | Depot Street | Fitchburg | 0.65 m of water at peak; over 30 cm for 15.5 h; 30 cm reached 0.5 h into the storm; worst hour 25 mm (40% of the storm); runoff beside / along the road at 0.8 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.33); a culvert within 100 m is overtopped |
| 5 | 1.00 | Water Street | Leominster | 0.94 m of water at peak; over 30 cm for 10.0 h; 30 cm reached 8.5 h into the storm; worst hour 21 mm (33% of the storm); a culvert within 100 m is overtopped |
| 6 | 1.00 | Kingman Drive | Leominster | 0.64 m of water at peak; over 30 cm for 8.0 h; 30 cm reached 8.0 h into the storm; worst hour 28 mm (37% of the storm); runoff beside / along the road at 0.9 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.43); a culvert within 100 m is overtopped |
| 7 | 1.00 | Depot Square | Leominster | 0.94 m of water at peak; over 30 cm for 10.0 h; 30 cm reached 8.5 h into the storm; worst hour 21 mm (33% of the storm); a culvert within 100 m is overtopped |
| 8 | 1.00 | Reservoir Road | Lunenburg | 0.66 m of water at peak; over 30 cm for 9.0 h; 30 cm reached 9.5 h into the storm; worst hour 21 mm (34% of the storm); runoff beside / along the road at 0.5 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.13); culvert (N. Branch Catacunemaug): headwater 1.30 m vs road crest 1.07 m, 1.2 m3/s |
| 9 | 1.00 | Commercial Road | Leominster | 0.66 m of water at peak; over 30 cm for 5.0 h; 30 cm reached 10.0 h into the storm; worst hour 17 mm (29% of the storm); a culvert within 100 m is overtopped |
| 10 | 1.00 | (unnamed) | Lunenburg | 0.60 m of water at peak; over 30 cm for 9.0 h; 30 cm reached 9.0 h into the storm; worst hour 23 mm (36% of the storm); water beside the road 0.06 m below its crest (design freeboard 0.30 m; P 0.94); a culvert within 100 m is overtopped |
| 11 | 1.00 | (unnamed) | Leominster | 0.60 m of water at peak; over 30 cm for 4.5 h; 30 cm reached 8.0 h into the storm; worst hour 28 mm (38% of the storm) |
| 12 | 1.00 | Exchange Street | Leominster | 0.59 m of water at peak; over 30 cm for 4.5 h; 30 cm reached 8.0 h into the storm; worst hour 29 mm (38% of the storm); water beside the road 0.66 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 2.7 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.95); a culvert within 100 m is overtopped |
| 13 | 1.00 | Litchfield Street | Leominster | 0.57 m of water at peak; over 30 cm for 8.0 h; 30 cm reached 10.5 h into the storm; worst hour 13 mm (25% of the storm); a culvert within 100 m is overtopped |
| 14 | 0.98 | Constitution Drive | Leominster | 0.52 m of water at peak; over 30 cm for 4.0 h; 30 cm reached 8.0 h into the storm; worst hour 29 mm (38% of the storm) |
| 15 | 0.98 | Sanborn Street | Fitchburg | 0.51 m of water at peak; over 30 cm for 7.5 h; 30 cm reached 8.5 h into the storm; worst hour 23 mm (38% of the storm); runoff beside / along the road at 1.3 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.68); a culvert within 100 m is overtopped |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
