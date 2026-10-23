# Road-closure prototype: jul2021_loss_jul2021_dcia

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on CPU (OpenMP)), 20 m grid, storm from 2021-07-09T08:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 6,083 |
| Expected closures (sum of probabilities) | 70.5 |
| Segments with closure probability >= 50% | 41 (25.0 km) |
| Further segments that may close (stream reaches the road crest) | 82 (42.4 km) |
| Culverts overtopped / surcharged | 87 / 0 of 1161 |
| Road segments cut off from hospitals | 333 |
| Worst added trip time to a hospital | 16.6 min |
| Heaviest hour of rain | 19.5 mm |
| Flood model run time | 968 s |

## Checks against what happened

- Storm-day flood reports in the area: 1; water >= 10 cm within 100 m of 0% of them, vs 53% of random points (any day).
- Segments flagged impassable are 0.0x as likely as an average segment to have a report within 200 m.
- MassDOT repeating flood sites in the area: 4; 1 have a segment within 150 m at P >= 0.5 (share of all segments at P >= 0.5: 0.7%).

## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 1.00 | Martin Luther King Jr Boulevard | Worcester | 3.15 m of water at peak; over 30 cm for 17.5 h; 30 cm reached 1.0 h into the storm; worst hour 14 mm (27% of the storm); water beside the road 3.07 m above its crest (design freeboard 0.30 m; P 1.00); fast water: depth x speed 0.29 m2/s (small cars unstable from 0.3); runoff beside / along the road at 2.6 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.98); road sag 3.2 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 14 mm; catchment 60.2 ha) (P 1.00); a culvert within 100 m is overtopped |
| 2 | 1.00 | Martin Luther King Jr Boulevard | Worcester | 2.45 m of water at peak; over 30 cm for 17.5 h; 30 cm reached 1.0 h into the storm; worst hour 14 mm (27% of the storm); water beside the road 2.12 m above its crest (design freeboard 0.30 m; P 1.00); fast water: depth x speed 0.22 m2/s (small cars unstable from 0.3); runoff beside / along the road at 4.5 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.96); road sag 3.2 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 14 mm; catchment 60.2 ha) (P 1.00); a culvert within 100 m is overtopped |
| 3 | 1.00 | Shrewsbury Street | Worcester | 0.64 m of water at peak; over 30 cm for 9.5 h; 30 cm reached 9.0 h into the storm; worst hour 14 mm (27% of the storm); water beside the road 0.56 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.9 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 14 mm; catchment 127.8 ha) (P 1.00) |
| 4 | 1.00 | Shrewsbury Street | Worcester | 0.74 m of water at peak; over 30 cm for 10.5 h; 30 cm reached 8.0 h into the storm; worst hour 14 mm (27% of the storm); water beside the road 0.66 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 1.0 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.19); road sag 0.9 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 14 mm; catchment 127.8 ha) (P 1.00) |
| 5 | 1.00 | Foster Street | Worcester | 1.42 m of water at peak; over 30 cm for 11.0 h; 30 cm reached 7.5 h into the storm; worst hour 14 mm (27% of the storm); water beside the road 0.19 m below its crest (design freeboard 0.30 m; P 0.76); a culvert within 100 m is overtopped |
| 6 | 1.00 | Foster Street | Worcester | 1.42 m of water at peak; over 30 cm for 11.0 h; 30 cm reached 7.5 h into the storm; worst hour 14 mm (27% of the storm); water beside the road 0.12 m below its crest (design freeboard 0.30 m; P 0.89); runoff beside / along the road at 2.0 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.31); a culvert within 100 m is overtopped |
| 7 | 1.00 | (unnamed) | Worcester | 1.52 m of water at peak; over 30 cm for 10.5 h; 30 cm reached 8.0 h into the storm; worst hour 14 mm (27% of the storm); a culvert within 100 m is overtopped |
| 8 | 1.00 | East Park Terrace | Worcester | 0.97 m of water at peak; over 30 cm for 11.5 h; 30 cm reached 7.0 h into the storm; worst hour 14 mm (26% of the storm); water beside the road 0.87 m above its crest (design freeboard 0.30 m; P 1.00); road sag 4.3 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 14 mm; catchment 127.8 ha) (P 1.00) |
| 9 | 1.00 | Fantasia Drive | Worcester | 0.62 m of water at peak; over 30 cm for 9.5 h; 30 cm reached 9.0 h into the storm; worst hour 14 mm (26% of the storm); water beside the road 0.55 m above its crest (design freeboard 0.30 m; P 1.00); road sag 1.3 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 14 mm; catchment 127.8 ha) (P 1.00) |
| 10 | 1.00 | Wellington Street | Worcester | 0.59 m of water at peak; over 30 cm for 5.0 h; 30 cm reached 7.5 h into the storm; worst hour 12 mm (25% of the storm); water beside the road 0.55 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.9 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 12 mm; catchment 15.1 ha) (P 1.00) |
| 11 | 1.00 | Murray Avenue | Worcester | 0.59 m of water at peak; over 30 cm for 5.0 h; 30 cm reached 7.5 h into the storm; worst hour 13 mm (25% of the storm); water beside the road 0.55 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 1.1 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.29); road sag 0.9 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 12 mm; catchment 15.1 ha) (P 1.00) |
| 12 | 0.99 | Major Taylor Boulevard | Worcester | 0.56 m of water at peak; over 30 cm for 9.0 h; 30 cm reached 9.5 h into the storm; worst hour 14 mm (27% of the storm); water beside the road 0.31 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 1.1 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.27); road sag 1.1 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 14 mm; catchment 60.2 ha) (P 0.75); a culvert within 100 m is overtopped |
| 13 | 0.99 | Major Taylor Boulevard | Worcester | 0.56 m of water at peak; over 30 cm for 9.0 h; 30 cm reached 9.5 h into the storm; worst hour 14 mm (27% of the storm); water beside the road 0.31 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 1.1 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.27); road sag 1.1 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 14 mm; catchment 60.2 ha) (P 0.75); a culvert within 100 m is overtopped |
| 14 | 0.98 | Maybrook Place | Worcester | 0.51 m of water at peak; over 30 cm for 7.0 h; 30 cm reached 8.5 h into the storm; worst hour 13 mm (27% of the storm); water beside the road 0.44 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 1.9 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.63); road sag 0.7 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 13 mm; catchment 61.6 ha) (P 0.99) |
| 15 | 0.97 | Dewey Street | Worcester | 0.48 m of water at peak; over 30 cm for 9.0 h; 30 cm reached 7.5 h into the storm; worst hour 13 mm (26% of the storm); water beside the road 0.40 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.9 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 12 mm; catchment 12.8 ha) (P 0.97) |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
