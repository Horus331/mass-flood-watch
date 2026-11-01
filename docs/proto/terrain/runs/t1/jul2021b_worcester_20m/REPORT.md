# Road-closure prototype: jul2021b_loss_jul2021b_worcester_20m

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on CPU (OpenMP)), 20 m grid, storm from 2021-07-17T14:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 8,553 |
| Expected closures (sum of probabilities) | 61.2 |
| Segments with closure probability >= 50% | 30 (15.4 km) |
| Further segments that may close (stream reaches the road crest) | 83 (46.2 km) |
| Culverts overtopped / surcharged | 54 / 0 of 1186 |
| Road segments cut off from hospitals | 159 |
| Worst added trip time to a hospital | 20.0 min |
| Heaviest hour of rain | 46.9 mm |
| Flood model run time | 1453 s |

## Checks against what happened

- Storm-day flood reports in the area: 3; water >= 10 cm within 100 m of 33% of them, vs 29% of random points (any day).
- Segments flagged impassable are 2.38x as likely as an average segment to have a report within 200 m.
- MassDOT repeating flood sites in the area: 9; 0 have a segment within 150 m at P >= 0.5 (share of all segments at P >= 0.5: 0.4%).

## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 1.00 | Martin Luther King Jr Boulevard | Worcester | 2.88 m of water at peak; over 30 cm for 23.5 h; 30 cm reached 1.0 h into the storm; worst hour 21 mm (40% of the storm); water beside the road 2.80 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 0.9 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.37); road sag 3.2 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 21 mm; catchment 60.2 ha) (P 1.00); a culvert within 100 m is overtopped |
| 2 | 1.00 | Martin Luther King Jr Boulevard | Worcester | 2.18 m of water at peak; over 30 cm for 23.5 h; 30 cm reached 1.0 h into the storm; worst hour 21 mm (40% of the storm); water beside the road 1.86 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 2.2 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.75); road sag 3.2 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 21 mm; catchment 60.2 ha) (P 1.00); a culvert within 100 m is overtopped |
| 3 | 1.00 | Foster Street | Worcester | 1.14 m of water at peak; over 30 cm for 22.0 h; 30 cm reached 2.5 h into the storm; worst hour 22 mm (41% of the storm); water beside the road 0.40 m below its crest (design freeboard 0.30 m; P 0.25); a culvert within 100 m is overtopped |
| 4 | 1.00 | Ramp-West Boylston Dr To Rt 190 Nb | Worcester | 0.67 m of water at peak; over 30 cm for 5.5 h; 30 cm reached 19.0 h into the storm; worst hour 18 mm (29% of the storm); water beside the road 0.52 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.8 m deep (underpass, drains sized for the 50-yr hour, 58 mm; peak hour here 18 mm; catchment 52.2 ha) (P 1.00) |
| 5 | 1.00 | Ramp-Rt 12 Nb To Rt 190 Nb | Worcester | 0.62 m of water at peak; over 30 cm for 4.5 h; 30 cm reached 20.0 h into the storm; worst hour 18 mm (29% of the storm); water beside the road 0.55 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.8 m deep (underpass, drains sized for the 50-yr hour, 58 mm; peak hour here 18 mm; catchment 52.2 ha) (P 1.00) |
| 6 | 1.00 | Norton Drive | Worcester | 0.60 m of water at peak; over 30 cm for 5.5 h; 30 cm reached 19.0 h into the storm; worst hour 18 mm (28% of the storm); water beside the road 0.47 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.8 m deep (underpass, drains sized for the 50-yr hour, 58 mm; peak hour here 18 mm; catchment 52.2 ha) (P 1.00) |
| 7 | 1.00 | West Boylston Drive | Worcester | 0.60 m of water at peak; over 30 cm for 3.5 h; 30 cm reached 21.0 h into the storm; worst hour 18 mm (30% of the storm) |
| 8 | 1.00 | West Boylston Drive | Worcester | 0.60 m of water at peak; over 30 cm for 3.5 h; 30 cm reached 21.0 h into the storm; worst hour 18 mm (29% of the storm) |
| 9 | 1.00 | Norton Drive | Worcester | 0.60 m of water at peak; over 30 cm for 4.5 h; 30 cm reached 20.0 h into the storm; worst hour 18 mm (29% of the storm); water beside the road 0.47 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.8 m deep (underpass, drains sized for the 50-yr hour, 58 mm; peak hour here 18 mm; catchment 52.2 ha) (P 1.00) |
| 10 | 1.00 | Stafford Street | Worcester | 0.58 m of water at peak; over 30 cm for 10.5 h; 30 cm reached 0.5 h into the storm; worst hour 28 mm (39% of the storm); water beside the road 0.16 m above its crest (design freeboard 0.30 m; P 1.00); a culvert within 100 m is overtopped |
| 11 | 1.00 | Coolidge Road | Worcester | 0.58 m of water at peak; over 30 cm for 4.5 h; 30 cm reached 20.0 h into the storm; worst hour 26 mm (39% of the storm); water beside the road 0.57 m above its crest (design freeboard 0.30 m; P 1.00); fast water: depth x speed 0.21 m2/s (small cars unstable from 0.3); runoff beside / along the road at 0.6 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.16); road sag 0.7 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 25 mm; catchment 17.7 ha) (P 1.00) |
| 12 | 0.99 | Kinnicutt Road | Worcester | 0.56 m of water at peak; over 30 cm for 4.5 h; 30 cm reached 20.0 h into the storm; worst hour 25 mm (35% of the storm); water beside the road 0.77 m above its crest (design freeboard 0.30 m; P 1.00); fast water: depth x speed 0.20 m2/s (small cars unstable from 0.3) |
| 13 | 0.97 | Rockland Road | Auburn | 0.49 m of water at peak; over 30 cm for 17.0 h; 30 cm reached 7.5 h into the storm; worst hour 29 mm (51% of the storm); a culvert within 100 m is overtopped |
| 14 | 0.97 | Maybrook Place | Worcester | 0.49 m of water at peak; over 30 cm for 4.0 h; 30 cm reached 20.5 h into the storm; worst hour 27 mm (41% of the storm); water beside the road 0.42 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.7 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 27 mm; catchment 61.6 ha) (P 0.99) |
| 15 | 0.94 | James Street | Worcester | 0.45 m of water at peak; over 30 cm for 9.0 h; 30 cm reached 10.0 h into the storm; worst hour 28 mm (41% of the storm); a culvert within 100 m is overtopped |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
