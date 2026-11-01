# Road-closure prototype: jul2021b_loss_jul2021b_worcester_20m

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on CPU (OpenMP)), 20 m grid, storm from 2021-07-17T14:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 8,553 |
| Expected closures (sum of probabilities) | 47.2 |
| Segments with closure probability >= 50% | 17 (13.0 km) |
| Further segments that may close (stream reaches the road crest) | 69 (39.8 km) |
| Culverts overtopped / surcharged | 43 / 0 of 1186 |
| Road segments cut off from hospitals | 297 |
| Worst added trip time to a hospital | 20.2 min |
| Heaviest hour of rain | 46.9 mm |
| Flood model run time | 1522 s |

## Checks against what happened

- Storm-day flood reports in the area: 3; water >= 10 cm within 100 m of 33% of them, vs 26% of random points (any day).
- Segments flagged impassable are 2.77x as likely as an average segment to have a report within 200 m.
- MassDOT repeating flood sites in the area: 9; 0 have a segment within 150 m at P >= 0.5 (share of all segments at P >= 0.5: 0.2%).

## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 1.00 | Coolidge Road | Worcester | 0.58 m of water at peak; over 30 cm for 4.5 h; 30 cm reached 20.0 h into the storm; worst hour 26 mm (39% of the storm); water beside the road 0.57 m above its crest (design freeboard 0.30 m; P 1.00); fast water: depth x speed 0.21 m2/s (small cars unstable from 0.3); runoff beside / along the road at 0.6 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.16); road sag 0.7 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 25 mm; catchment 17.7 ha) (P 1.00) |
| 2 | 1.00 | Kinnicutt Road | Worcester | 0.56 m of water at peak; over 30 cm for 4.5 h; 30 cm reached 20.0 h into the storm; worst hour 25 mm (35% of the storm); water beside the road 0.77 m above its crest (design freeboard 0.30 m; P 1.00); fast water: depth x speed 0.21 m2/s (small cars unstable from 0.3) |
| 3 | 0.97 | Cambridge Street | Worcester | 0.48 m of water at peak; over 30 cm for 5.0 h; 30 cm reached 19.5 h into the storm; worst hour 28 mm (45% of the storm); water beside the road 0.34 m above its crest (design freeboard 0.30 m; P 1.00); road sag 2.0 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 26 mm; catchment 77.2 ha) (P 0.97) |
| 4 | 0.94 | Stafford Street | Worcester | 0.46 m of water at peak; over 30 cm for 4.5 h; 30 cm reached 19.5 h into the storm; worst hour 28 mm (39% of the storm); water beside the road 0.15 m above its crest (design freeboard 0.30 m; P 1.00); a culvert within 100 m is overtopped |
| 5 | 0.94 | Maybrook Place | Worcester | 0.45 m of water at peak; over 30 cm for 3.5 h; 30 cm reached 21.0 h into the storm; worst hour 27 mm (41% of the storm); water beside the road 0.40 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.7 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 27 mm; catchment 61.6 ha) (P 0.98) |
| 6 | 0.86 | Martin Luther King Jr Boulevard | Worcester | 0.41 m of water at peak; over 30 cm for 4.5 h; 30 cm reached 20.0 h into the storm; worst hour 21 mm (40% of the storm); water beside the road 0.33 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 1.1 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.61); road sag 3.2 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 21 mm; catchment 60.2 ha) (P 0.86) |
| 7 | 0.81 | James Street | Worcester | 0.39 m of water at peak; over 30 cm for 3.5 h; 30 cm reached 21.0 h into the storm; worst hour 28 mm (40% of the storm); runoff beside / along the road at 0.6 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.18); a culvert within 100 m is overtopped |
| 8 | 0.79 | Brookhaven Road | Worcester | 0.38 m of water at peak; over 30 cm for 1.5 h; 30 cm reached 19.5 h into the storm; worst hour 22 mm (31% of the storm); water beside the road 0.37 m below its crest (design freeboard 0.30 m; P 0.32); a culvert within 100 m is overtopped |
| 9 | 0.77 | East Park Terrace | Worcester | 0.37 m of water at peak; over 30 cm for 5.0 h; 30 cm reached 19.5 h into the storm; worst hour 20 mm (42% of the storm); water beside the road 0.27 m above its crest (design freeboard 0.30 m; P 1.00); road sag 4.3 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 20 mm; catchment 127.8 ha) (P 0.77) |
| 10 | 0.70 | Westbrook Road | Worcester | 0.35 m of water at peak; over 30 cm for 1.5 h; 30 cm reached 20.0 h into the storm; worst hour 24 mm (34% of the storm); water beside the road 0.36 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 0.7 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.19) |
| 11 | 0.69 | Green Street | Leicester | 0.35 m of water at peak; over 30 cm for 3.5 h; 30 cm reached 20.0 h into the storm; worst hour 18 mm (29% of the storm); a culvert within 100 m is overtopped |
| 12 | 0.54 | Auburn Street | Leicester | 0.31 m of water at peak; over 30 cm for 1.0 h; 30 cm reached 21.0 h into the storm; worst hour 26 mm (32% of the storm); a culvert within 100 m is overtopped |
| 13 | 0.54 | Rockland Road | Auburn | 0.31 m of water at peak; over 30 cm for 1.0 h; 30 cm reached 23.5 h into the storm; worst hour 29 mm (51% of the storm); a culvert within 100 m is overtopped |
| 14 | 0.53 | Route 9 | Leicester | 0.31 m of water at peak; over 30 cm for 0.5 h; 30 cm reached 21.0 h into the storm; worst hour 27 mm (32% of the storm); runoff beside / along the road at 1.2 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.68); a culvert within 100 m is overtopped |
| 15 | 0.53 | Wellington Street | Worcester | 0.31 m of water at peak; over 30 cm for 1.0 h; 30 cm reached 20.5 h into the storm; worst hour 24 mm (42% of the storm); water beside the road 0.35 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.9 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 24 mm; catchment 15.1 ha) (P 0.93) |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
