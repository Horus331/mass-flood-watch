# Road-closure prototype: jul2023b_loss_jul2023b_worcester_20m

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on CPU (OpenMP)), 20 m grid, storm from 2023-07-10T08:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 7,372 |
| Expected closures (sum of probabilities) | 86.4 |
| Segments with closure probability >= 50% | 47 (24.7 km) |
| Further segments that may close (stream reaches the road crest) | 119 (63.4 km) |
| Culverts overtopped / surcharged | 93 / 0 of 978 |
| Road segments cut off from hospitals | 359 |
| Worst added trip time to a hospital | 19.4 min |
| Heaviest hour of rain | 31.4 mm |
| Flood model run time | 1126 s |

## Checks against what happened

- Storm-day flood reports in the area: 1; water >= 10 cm within 100 m of 0% of them, vs 54% of random points (any day).
- Segments flagged impassable are 0.0x as likely as an average segment to have a report within 200 m.
- MassDOT repeating flood sites in the area: 8; 1 have a segment within 150 m at P >= 0.5 (share of all segments at P >= 0.5: 0.6%).

## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 1.00 | Martin Luther King Jr Boulevard | Worcester | 3.20 m of water at peak; over 30 cm for 17.5 h; 30 cm reached 1.0 h into the storm; worst hour 16 mm (32% of the storm); water beside the road 3.12 m above its crest (design freeboard 0.30 m; P 1.00); road sag 3.2 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 16 mm; catchment 60.2 ha) (P 1.00); a culvert within 100 m is overtopped |
| 2 | 1.00 | Martin Luther King Jr Boulevard | Worcester | 2.50 m of water at peak; over 30 cm for 17.5 h; 30 cm reached 1.0 h into the storm; worst hour 16 mm (32% of the storm); water beside the road 2.18 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 2.5 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.96); road sag 3.2 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 16 mm; catchment 60.2 ha) (P 1.00); a culvert within 100 m is overtopped |
| 3 | 1.00 | Foster Street | Worcester | 1.47 m of water at peak; over 30 cm for 11.5 h; 30 cm reached 7.0 h into the storm; worst hour 16 mm (32% of the storm); water beside the road 0.40 m below its crest (design freeboard 0.30 m; P 0.25); a culvert within 100 m is overtopped |
| 4 | 1.00 | Foster Street | Worcester | 1.47 m of water at peak; over 30 cm for 11.5 h; 30 cm reached 7.0 h into the storm; worst hour 16 mm (32% of the storm); water beside the road 0.28 m below its crest (design freeboard 0.30 m; P 0.55); a culvert within 100 m is overtopped |
| 5 | 1.00 | Ramp-Rt 12 Nb To Rt 190 Nb | Worcester | 0.69 m of water at peak; over 30 cm for 5.0 h; 30 cm reached 13.5 h into the storm; worst hour 14 mm (26% of the storm); water beside the road 0.62 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.8 m deep (underpass, drains sized for the 50-yr hour, 58 mm; peak hour here 14 mm; catchment 52.2 ha) (P 1.00) |
| 6 | 1.00 | Norton Drive | Worcester | 0.67 m of water at peak; over 30 cm for 6.0 h; 30 cm reached 12.5 h into the storm; worst hour 15 mm (27% of the storm); water beside the road 0.53 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.8 m deep (underpass, drains sized for the 50-yr hour, 58 mm; peak hour here 14 mm; catchment 52.2 ha) (P 1.00) |
| 7 | 1.00 | Ramp-West Boylston Dr To Rt 190 Nb | Worcester | 0.73 m of water at peak; over 30 cm for 6.0 h; 30 cm reached 12.5 h into the storm; worst hour 14 mm (26% of the storm); water beside the road 0.59 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.8 m deep (underpass, drains sized for the 50-yr hour, 58 mm; peak hour here 14 mm; catchment 52.2 ha) (P 1.00) |
| 8 | 1.00 | (unnamed) | Worcester | 2.95 m of water at peak; over 30 cm for 9.5 h; 30 cm reached 9.0 h into the storm; worst hour 15 mm (31% of the storm); a culvert within 100 m is overtopped |
| 9 | 1.00 | East Park Terrace | Worcester | 0.81 m of water at peak; over 30 cm for 7.5 h; 30 cm reached 11.0 h into the storm; worst hour 16 mm (32% of the storm); water beside the road 0.71 m above its crest (design freeboard 0.30 m; P 1.00); road sag 4.3 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 16 mm; catchment 127.8 ha) (P 1.00) |
| 10 | 1.00 | West Boylston Drive | Worcester | 0.67 m of water at peak; over 30 cm for 5.0 h; 30 cm reached 13.5 h into the storm; worst hour 14 mm (26% of the storm) |
| 11 | 1.00 | West Boylston Drive | Worcester | 0.67 m of water at peak; over 30 cm for 5.0 h; 30 cm reached 13.5 h into the storm; worst hour 14 mm (26% of the storm) |
| 12 | 1.00 | Coolidge Road | Worcester | 0.66 m of water at peak; over 30 cm for 5.0 h; 30 cm reached 13.5 h into the storm; worst hour 18 mm (34% of the storm); water beside the road 0.62 m above its crest (design freeboard 0.30 m; P 1.00); fast water: depth x speed 0.26 m2/s (small cars unstable from 0.3); runoff beside / along the road at 0.6 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.16); road sag 0.7 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 17 mm; catchment 17.7 ha) (P 1.00) |
| 13 | 1.00 | Norton Drive | Worcester | 0.67 m of water at peak; over 30 cm for 5.0 h; 30 cm reached 13.5 h into the storm; worst hour 15 mm (27% of the storm); water beside the road 0.53 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 0.6 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.14); road sag 0.8 m deep (underpass, drains sized for the 50-yr hour, 58 mm; peak hour here 14 mm; catchment 52.2 ha) (P 1.00) |
| 14 | 1.00 | Major Taylor Boulevard | Worcester | 0.61 m of water at peak; over 30 cm for 2.5 h; 30 cm reached 16.0 h into the storm; worst hour 16 mm (32% of the storm); water beside the road 0.37 m above its crest (design freeboard 0.30 m; P 1.00); road sag 1.1 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 16 mm; catchment 60.2 ha) (P 0.89); a culvert within 100 m is overtopped |
| 15 | 1.00 | Major Taylor Boulevard | Worcester | 0.61 m of water at peak; over 30 cm for 2.5 h; 30 cm reached 16.0 h into the storm; worst hour 16 mm (32% of the storm); water beside the road 0.37 m above its crest (design freeboard 0.30 m; P 1.00); road sag 1.1 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 16 mm; catchment 60.2 ha) (P 0.89); a culvert within 100 m is overtopped |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
