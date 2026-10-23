# Road-closure prototype: jul2023_loss_jul2023_worcester_20m

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on CPU (OpenMP)), 20 m grid, storm from 2023-07-14T08:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 6,775 |
| Expected closures (sum of probabilities) | 66.4 |
| Segments with closure probability >= 50% | 40 (17.5 km) |
| Further segments that may close (stream reaches the road crest) | 104 (57.5 km) |
| Culverts overtopped / surcharged | 56 / 0 of 1023 |
| Road segments cut off from hospitals | 293 |
| Worst added trip time to a hospital | 14.8 min |
| Heaviest hour of rain | 25.9 mm |
| Flood model run time | 1380 s |

## Checks against what happened

- Storm-day flood reports in the area: 3; water >= 10 cm within 100 m of 0% of them, vs 50% of random points (any day).
- Segments flagged impassable are 0.0x as likely as an average segment to have a report within 200 m.
- MassDOT repeating flood sites in the area: 7; 1 have a segment within 150 m at P >= 0.5 (share of all segments at P >= 0.5: 0.6%).

## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 1.00 | Martin Luther King Jr Boulevard | Worcester | 3.65 m of water at peak; over 30 cm for 17.5 h; 30 cm reached 1.0 h into the storm; worst hour 21 mm (82% of the storm); water beside the road 3.58 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 1.2 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.65); road sag 3.2 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 21 mm; catchment 60.2 ha) (P 1.00); a culvert within 100 m is overtopped |
| 2 | 1.00 | Martin Luther King Jr Boulevard | Worcester | 2.96 m of water at peak; over 30 cm for 17.5 h; 30 cm reached 1.0 h into the storm; worst hour 21 mm (82% of the storm); water beside the road 2.63 m above its crest (design freeboard 0.30 m; P 1.00); fast water: depth x speed 0.22 m2/s (small cars unstable from 0.3); runoff beside / along the road at 1.9 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.73); road sag 3.2 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 21 mm; catchment 60.2 ha) (P 1.00); a culvert within 100 m is overtopped |
| 3 | 1.00 | Foster Street | Worcester | 1.93 m of water at peak; over 30 cm for 11.5 h; 30 cm reached 7.0 h into the storm; worst hour 20 mm (83% of the storm); water beside the road 0.06 m below its crest (design freeboard 0.30 m; P 0.95); a culvert within 100 m is overtopped |
| 4 | 1.00 | Foster Street | Worcester | 1.93 m of water at peak; over 30 cm for 11.5 h; 30 cm reached 7.0 h into the storm; worst hour 20 mm (83% of the storm); water beside the road 0.05 m below its crest (design freeboard 0.30 m; P 0.95); a culvert within 100 m is overtopped |
| 5 | 1.00 | Major Taylor Boulevard | Worcester | 1.06 m of water at peak; over 30 cm for 8.0 h; 30 cm reached 10.5 h into the storm; worst hour 21 mm (83% of the storm); water beside the road 0.82 m above its crest (design freeboard 0.30 m; P 1.00); road sag 1.1 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 21 mm; catchment 60.2 ha) (P 1.00); a culvert within 100 m is overtopped |
| 6 | 1.00 | Major Taylor Boulevard | Worcester | 1.06 m of water at peak; over 30 cm for 8.0 h; 30 cm reached 10.5 h into the storm; worst hour 21 mm (83% of the storm); water beside the road 0.82 m above its crest (design freeboard 0.30 m; P 1.00); road sag 1.1 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 21 mm; catchment 60.2 ha) (P 1.00); a culvert within 100 m is overtopped |
| 7 | 1.00 | (unnamed) | Worcester | 2.39 m of water at peak; over 30 cm for 10.5 h; 30 cm reached 8.0 h into the storm; worst hour 22 mm (82% of the storm); a culvert within 100 m is overtopped |
| 8 | 1.00 | Bridge Street | Worcester | 0.89 m of water at peak; over 30 cm for 7.5 h; 30 cm reached 11.0 h into the storm; worst hour 20 mm (82% of the storm); water beside the road 0.58 m above its crest (design freeboard 0.30 m; P 1.00); road sag 2.3 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 20 mm; catchment 22.1 ha) (P 1.00); a culvert within 100 m is overtopped |
| 9 | 1.00 | Commercial Street | Worcester | 0.66 m of water at peak; over 30 cm for 5.0 h; 30 cm reached 13.5 h into the storm; worst hour 21 mm (83% of the storm); water beside the road 0.62 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 1.7 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.42); road sag 0.9 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 21 mm; catchment 60.2 ha) (P 1.00); a culvert within 100 m is overtopped |
| 10 | 1.00 | Martin Luther King Jr Boulevard | Worcester | 0.62 m of water at peak; over 30 cm for 5.0 h; 30 cm reached 13.5 h into the storm; worst hour 21 mm (83% of the storm); water beside the road 0.45 m above its crest (design freeboard 0.30 m; P 1.00); a culvert within 100 m is overtopped |
| 11 | 0.98 | Ramp-West Boylston Dr To Rt 190 Nb | Worcester | 0.52 m of water at peak; over 30 cm for 8.5 h; 30 cm reached 10.0 h into the storm; worst hour 22 mm (84% of the storm); water beside the road 0.37 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.8 m deep (underpass, drains sized for the 50-yr hour, 58 mm; peak hour here 22 mm; catchment 52.2 ha) (P 0.99) |
| 12 | 0.96 | Ramp-Rt 12 Nb To Rt 190 Nb | Worcester | 0.48 m of water at peak; over 30 cm for 8.0 h; 30 cm reached 10.5 h into the storm; worst hour 22 mm (84% of the storm); water beside the road 0.40 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.8 m deep (underpass, drains sized for the 50-yr hour, 58 mm; peak hour here 22 mm; catchment 52.2 ha) (P 0.99) |
| 13 | 0.94 | Coolidge Road | Worcester | 0.46 m of water at peak; over 30 cm for 6.5 h; 30 cm reached 10.5 h into the storm; worst hour 18 mm (84% of the storm); water beside the road 0.53 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 0.7 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.29); road sag 0.7 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 18 mm; catchment 17.7 ha) (P 1.00) |
| 14 | 0.94 | Thomas Street | Worcester | 0.45 m of water at peak; over 30 cm for 3.0 h; 30 cm reached 15.5 h into the storm; worst hour 21 mm (82% of the storm); water beside the road 0.29 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.7 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 21 mm; catchment 60.2 ha) (P 0.94); a culvert within 100 m is overtopped |
| 15 | 0.93 | Thomas Street | Worcester | 0.45 m of water at peak; over 30 cm for 3.0 h; 30 cm reached 15.5 h into the storm; worst hour 21 mm (83% of the storm); water beside the road 0.41 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.5 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 21 mm; catchment 60.2 ha) (P 0.68); a culvert within 100 m is overtopped |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
