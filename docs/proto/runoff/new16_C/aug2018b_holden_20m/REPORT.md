# Road-closure prototype: aug2018b_loss_aug2018b_holden_20m

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on CPU (OpenMP)), 20 m grid, storm from 2018-08-11T08:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 4,422 |
| Expected closures (sum of probabilities) | 30.0 |
| Segments with closure probability >= 50% | 11 (8.0 km) |
| Further segments that may close (stream reaches the road crest) | 12 (10.5 km) |
| Culverts overtopped / surcharged | 31 / 1 of 864 |
| Road segments cut off from hospitals | 85 |
| Worst added trip time to a hospital | 12.5 min |
| Heaviest hour of rain | 24.1 mm |
| Flood model run time | 997 s |

## Checks against what happened

- Storm-day flood reports in the area: 0; water >= 10 cm within 100 m of 0% of them, vs 31% of random points (any day).
- MassDOT repeating flood sites in the area: 2; 0 have a segment within 150 m at P >= 0.5 (share of all segments at P >= 0.5: 0.2%).

## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 1.00 | Water Street | Clinton | 0.72 m of water at peak; over 30 cm for 22.0 h; 30 cm reached 0.5 h into the storm; worst hour 6 mm (16% of the storm) |
| 2 | 1.00 | Route 62 | Berlin | 1.01 m of water at peak; over 30 cm for 1.0 h; 30 cm reached 0.5 h into the storm; worst hour 5 mm (20% of the storm); water beside the road 0.42 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 1.3 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.29) |
| 3 | 1.00 | (unnamed) | Clinton | 0.60 m of water at peak; worst hour 6 mm (17% of the storm); a culvert within 100 m is overtopped |
| 4 | 0.97 | Route 70 | Clinton | 0.49 m of water at peak; over 30 cm for 3.0 h; 30 cm reached 18.0 h into the storm; worst hour 11 mm (20% of the storm); a culvert within 100 m is overtopped |
| 5 | 0.97 | Barnes Hill Road | Berlin | 0.49 m of water at peak; worst hour 5 mm (23% of the storm); water beside the road 0.80 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 1.4 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.77); a culvert within 100 m is overtopped |
| 6 | 0.92 | (unnamed) | Berlin | 0.44 m of water at peak; over 30 cm for 0.5 h; 30 cm reached 0.5 h into the storm; worst hour 5 mm (21% of the storm); water beside the road 0.49 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 1.3 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.24) |
| 7 | 0.89 | Route 62 | Berlin | 0.42 m of water at peak; over 30 cm for 0.5 h; 30 cm reached 0.5 h into the storm; worst hour 5 mm (22% of the storm) |
| 8 | 0.78 | Mill Street | Holden | 0.38 m of water at peak; over 30 cm for 1.0 h; 30 cm reached 0.5 h into the storm; worst hour 8 mm (18% of the storm) |
| 9 | 0.76 | Parker Road | Lancaster | 0.37 m of water at peak; over 30 cm for 2.0 h; 30 cm reached 18.0 h into the storm; worst hour 13 mm (23% of the storm) |
| 10 | 0.71 | Ramp-West Boylston Dr To Rt 190 Nb | Worcester | 0.35 m of water at peak; over 30 cm for 2.5 h; 30 cm reached 20.0 h into the storm; worst hour 7 mm (25% of the storm); water beside the road 0.23 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.8 m deep (underpass, drains sized for the 50-yr hour, 58 mm; peak hour here 7 mm; catchment 40.0 ha) (P 0.72) |
| 11 | 0.56 | Ramp-Rt 12 Nb To Rt 190 Nb | Worcester | 0.32 m of water at peak; over 30 cm for 1.5 h; 30 cm reached 21.0 h into the storm; worst hour 7 mm (25% of the storm); water beside the road 0.24 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.8 m deep (underpass, drains sized for the 50-yr hour, 58 mm; peak hour here 7 mm; catchment 40.0 ha) (P 0.72) |
| 12 | 0.47 | Goss Lane | Lancaster | 0.29 m of water at peak; worst hour 15 mm (24% of the storm); culvert (Ropers Brook): headwater 2.38 m vs road crest 1.83 m, 2.3 m3/s |
| 13 | 0.46 | Norton Drive | Worcester | 0.29 m of water at peak; over 30 cm for 2.5 h; 30 cm reached 20.0 h into the storm; worst hour 8 mm (25% of the storm); water beside the road 0.16 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.8 m deep (underpass, drains sized for the 50-yr hour, 58 mm; peak hour here 7 mm; catchment 40.0 ha) (P 0.72) |
| 14 | 0.46 | Norton Drive | Worcester | 0.29 m of water at peak; over 30 cm for 1.5 h; 30 cm reached 21.0 h into the storm; worst hour 8 mm (25% of the storm); water beside the road 0.16 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.8 m deep (underpass, drains sized for the 50-yr hour, 58 mm; peak hour here 7 mm; catchment 40.0 ha) (P 0.72) |
| 15 | 0.46 | West Boylston Drive | Worcester | 0.29 m of water at peak; worst hour 7 mm (26% of the storm) |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
