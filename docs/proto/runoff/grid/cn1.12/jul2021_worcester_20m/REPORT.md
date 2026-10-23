# Road-closure prototype: jul2021_loss_jul2021_worcester_20m

Flood model: LISFLOOD-FP 8.3 (acceleration (local inertial, Bates et al. 2010) on CPU (OpenMP)), 20 m grid, storm from 2021-07-09T08:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 6,275 |
| Expected closures (sum of probabilities) | 141.0 |
| Segments with closure probability >= 50% | 95 (54.0 km) |
| Further segments that may close (stream reaches the road crest) | 130 (67.7 km) |
| Culverts overtopped / surcharged | 186 / 0 of 1161 |
| Road segments cut off from hospitals | 666 |
| Worst added trip time to a hospital | 27.1 min |
| Heaviest hour of rain | 19.5 mm |
| Flood model run time | 1687 s |

## Checks against what happened

- Storm-day flood reports in the area: 1; water >= 10 cm within 100 m of 0% of them, vs 65% of random points (any day).
- Segments flagged impassable are 0.86x as likely as an average segment to have a report within 200 m.
- MassDOT repeating flood sites in the area: 4; 1 have a segment within 150 m at P >= 0.5 (share of all segments at P >= 0.5: 1.5%).

## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 1.00 | Martin Luther King Jr Boulevard | Worcester | 3.61 m of water at peak; over 30 cm for 17.5 h; 30 cm reached 1.0 h into the storm; worst hour 14 mm (27% of the storm); water beside the road 3.53 m above its crest (design freeboard 0.30 m; P 1.00); fast water: depth x speed 0.35 m2/s (small cars unstable from 0.3); runoff beside / along the road at 1.4 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.74); road sag 3.2 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 14 mm; catchment 60.2 ha) (P 1.00); a culvert within 100 m is overtopped |
| 2 | 1.00 | Martin Luther King Jr Boulevard | Worcester | 2.91 m of water at peak; over 30 cm for 17.5 h; 30 cm reached 1.0 h into the storm; worst hour 14 mm (27% of the storm); water beside the road 2.59 m above its crest (design freeboard 0.30 m; P 1.00); fast water: depth x speed 0.22 m2/s (small cars unstable from 0.3); runoff beside / along the road at 0.9 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.44); road sag 3.2 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 14 mm; catchment 60.2 ha) (P 1.00); a culvert within 100 m is overtopped |
| 3 | 1.00 | Shrewsbury Street | Worcester | 0.90 m of water at peak; over 30 cm for 10.5 h; 30 cm reached 8.0 h into the storm; worst hour 14 mm (27% of the storm); water beside the road 0.82 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.8 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 14 mm; catchment 127.8 ha) (P 1.00) |
| 4 | 1.00 | Shrewsbury Street | Worcester | 1.01 m of water at peak; over 30 cm for 10.5 h; 30 cm reached 8.0 h into the storm; worst hour 14 mm (27% of the storm); water beside the road 0.92 m above its crest (design freeboard 0.30 m; P 1.00); fast water: depth x speed 0.22 m2/s (small cars unstable from 0.3); runoff beside / along the road at 1.4 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.10); road sag 0.8 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 14 mm; catchment 127.8 ha) (P 1.00) |
| 5 | 1.00 | Foster Street | Worcester | 1.89 m of water at peak; over 30 cm for 12.0 h; 30 cm reached 6.5 h into the storm; worst hour 14 mm (27% of the storm); water beside the road -0.00 m below its crest (design freeboard 0.30 m; P 0.98); road sag 1.2 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 14 mm; catchment 22.1 ha) (P 0.19); a culvert within 100 m is overtopped |
| 6 | 1.00 | Foster Street | Worcester | 1.89 m of water at peak; over 30 cm for 12.0 h; 30 cm reached 6.5 h into the storm; worst hour 14 mm (27% of the storm); water beside the road 0.03 m above its crest (design freeboard 0.30 m; P 0.98); road sag 1.2 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 14 mm; catchment 22.1 ha) (P 0.19); a culvert within 100 m is overtopped |
| 7 | 1.00 | Major Taylor Boulevard | Worcester | 1.02 m of water at peak; over 30 cm for 10.0 h; 30 cm reached 8.5 h into the storm; worst hour 14 mm (27% of the storm); water beside the road 0.77 m above its crest (design freeboard 0.30 m; P 1.00); road sag 1.1 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 14 mm; catchment 60.2 ha) (P 1.00); a culvert within 100 m is overtopped |
| 8 | 1.00 | Major Taylor Boulevard | Worcester | 1.02 m of water at peak; over 30 cm for 10.0 h; 30 cm reached 8.5 h into the storm; worst hour 14 mm (27% of the storm); water beside the road 0.77 m above its crest (design freeboard 0.30 m; P 1.00); road sag 1.1 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 14 mm; catchment 60.2 ha) (P 1.00); a culvert within 100 m is overtopped |
| 9 | 1.00 | Cambridge Street | Worcester | 0.69 m of water at peak; over 30 cm for 9.0 h; 30 cm reached 9.5 h into the storm; worst hour 13 mm (25% of the storm); water beside the road 0.55 m above its crest (design freeboard 0.30 m; P 1.00); road sag 2.0 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 13 mm; catchment 77.2 ha) (P 1.00) |
| 10 | 1.00 | Auburn Street | Auburn | 0.71 m of water at peak; over 30 cm for 7.0 h; 30 cm reached 11.5 h into the storm; worst hour 13 mm (24% of the storm) |
| 11 | 1.00 | (unnamed) | Worcester | 2.75 m of water at peak; over 30 cm for 11.0 h; 30 cm reached 7.5 h into the storm; worst hour 14 mm (27% of the storm); a culvert within 100 m is overtopped |
| 12 | 1.00 | Bridge Street | Worcester | 0.85 m of water at peak; over 30 cm for 9.0 h; 30 cm reached 9.5 h into the storm; worst hour 14 mm (27% of the storm); water beside the road 0.54 m above its crest (design freeboard 0.30 m; P 1.00); road sag 2.3 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 14 mm; catchment 22.1 ha) (P 1.00); a culvert within 100 m is overtopped |
| 13 | 1.00 | East Park Terrace | Worcester | 1.23 m of water at peak; over 30 cm for 11.5 h; 30 cm reached 7.0 h into the storm; worst hour 14 mm (26% of the storm); water beside the road 1.13 m above its crest (design freeboard 0.30 m; P 1.00); road sag 4.3 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 14 mm; catchment 127.8 ha) (P 1.00) |
| 14 | 1.00 | Washington Street | Worcester | 0.70 m of water at peak; over 30 cm for 10.5 h; 30 cm reached 8.0 h into the storm; worst hour 13 mm (26% of the storm); water beside the road 0.45 m above its crest (design freeboard 0.30 m; P 1.00); a culvert within 100 m is overtopped |
| 15 | 1.00 | Fantasia Drive | Worcester | 0.88 m of water at peak; over 30 cm for 10.0 h; 30 cm reached 8.5 h into the storm; worst hour 14 mm (26% of the storm); water beside the road 0.81 m above its crest (design freeboard 0.30 m; P 1.00); road sag 1.3 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 14 mm; catchment 127.8 ha) (P 1.00) |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
