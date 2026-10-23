# Road-closure prototype: jul2021_rain_jul2021_gauge_dt5

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on CPU (OpenMP)), 20 m grid, storm from 2021-07-09T08:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 6,275 |
| Expected closures (sum of probabilities) | 85.9 |
| Segments with closure probability >= 50% | 52 (31.6 km) |
| Further segments that may close (stream reaches the road crest) | 95 (53.6 km) |
| Culverts overtopped / surcharged | 124 / 0 of 1161 |
| Road segments cut off from hospitals | 402 |
| Worst added trip time to a hospital | 24.5 min |
| Heaviest hour of rain | 22.0 mm |
| Flood model run time | 1519 s |

## Checks against what happened

- Storm-day flood reports in the area: 1; water >= 10 cm within 100 m of 0% of them, vs 57% of random points (any day).
- Segments flagged impassable are 1.37x as likely as an average segment to have a report within 200 m.
- MassDOT repeating flood sites in the area: 4; 1 have a segment within 150 m at P >= 0.5 (share of all segments at P >= 0.5: 0.8%).

## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 1.00 | Martin Luther King Jr Boulevard | Worcester | 3.13 m of water at peak; over 30 cm for 17.5 h; 30 cm reached 1.0 h into the storm; worst hour 17 mm (27% of the storm); water beside the road 3.05 m above its crest (design freeboard 0.30 m; P 1.00); fast water: depth x speed 0.31 m2/s (small cars unstable from 0.3); runoff beside / along the road at 1.2 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.65); road sag 3.2 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 17 mm; catchment 60.2 ha) (P 1.00); a culvert within 100 m is overtopped |
| 2 | 1.00 | Martin Luther King Jr Boulevard | Worcester | 2.43 m of water at peak; over 30 cm for 17.5 h; 30 cm reached 1.0 h into the storm; worst hour 17 mm (27% of the storm); water beside the road 2.11 m above its crest (design freeboard 0.30 m; P 1.00); fast water: depth x speed 0.19 m2/s (small cars unstable from 0.3); runoff beside / along the road at 2.5 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.97); road sag 3.2 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 17 mm; catchment 60.2 ha) (P 1.00); a culvert within 100 m is overtopped |
| 3 | 1.00 | Shrewsbury Street | Worcester | 0.73 m of water at peak; over 30 cm for 9.5 h; 30 cm reached 9.0 h into the storm; worst hour 18 mm (27% of the storm); water beside the road 0.65 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.9 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 17 mm; catchment 127.8 ha) (P 1.00) |
| 4 | 1.00 | Foster Street | Worcester | 1.41 m of water at peak; over 30 cm for 11.0 h; 30 cm reached 7.5 h into the storm; worst hour 17 mm (27% of the storm); water beside the road 0.19 m below its crest (design freeboard 0.30 m; P 0.77); a culvert within 100 m is overtopped |
| 5 | 1.00 | Foster Street | Worcester | 1.41 m of water at peak; over 30 cm for 11.0 h; 30 cm reached 7.5 h into the storm; worst hour 17 mm (27% of the storm); water beside the road 0.11 m below its crest (design freeboard 0.30 m; P 0.89); a culvert within 100 m is overtopped |
| 6 | 1.00 | (unnamed) | Worcester | 1.57 m of water at peak; over 30 cm for 10.0 h; 30 cm reached 8.5 h into the storm; worst hour 18 mm (27% of the storm); a culvert within 100 m is overtopped |
| 7 | 1.00 | East Park Terrace | Worcester | 0.95 m of water at peak; over 30 cm for 10.0 h; 30 cm reached 8.5 h into the storm; worst hour 17 mm (26% of the storm); water beside the road 0.85 m above its crest (design freeboard 0.30 m; P 1.00); road sag 4.3 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 17 mm; catchment 127.8 ha) (P 1.00) |
| 8 | 1.00 | Shrewsbury Street | Worcester | 0.63 m of water at peak; over 30 cm for 9.0 h; 30 cm reached 9.5 h into the storm; worst hour 18 mm (27% of the storm); water beside the road 0.54 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.9 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 17 mm; catchment 127.8 ha) (P 1.00) |
| 9 | 1.00 | Fantasia Drive | Worcester | 0.60 m of water at peak; over 30 cm for 9.0 h; 30 cm reached 9.5 h into the storm; worst hour 17 mm (26% of the storm); water beside the road 0.53 m above its crest (design freeboard 0.30 m; P 1.00); road sag 1.3 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 17 mm; catchment 127.8 ha) (P 1.00) |
| 10 | 0.99 | Auburn Street | Auburn | 0.56 m of water at peak; over 30 cm for 5.5 h; 30 cm reached 13.0 h into the storm; worst hour 16 mm (25% of the storm) |
| 11 | 0.99 | Wellington Street | Worcester | 0.56 m of water at peak; over 30 cm for 4.0 h; 30 cm reached 8.5 h into the storm; worst hour 15 mm (25% of the storm); water beside the road 0.52 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.9 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 15 mm; catchment 15.1 ha) (P 1.00) |
| 12 | 0.99 | Murray Avenue | Worcester | 0.56 m of water at peak; over 30 cm for 4.0 h; 30 cm reached 8.5 h into the storm; worst hour 16 mm (25% of the storm); water beside the road 0.52 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.9 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 15 mm; catchment 15.1 ha) (P 1.00) |
| 13 | 0.99 | Major Taylor Boulevard | Worcester | 0.54 m of water at peak; over 30 cm for 8.5 h; 30 cm reached 10.0 h into the storm; worst hour 17 mm (27% of the storm); water beside the road 0.29 m above its crest (design freeboard 0.30 m; P 1.00); road sag 1.1 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 17 mm; catchment 60.2 ha) (P 0.70); a culvert within 100 m is overtopped |
| 14 | 0.99 | Major Taylor Boulevard | Worcester | 0.54 m of water at peak; over 30 cm for 8.5 h; 30 cm reached 10.0 h into the storm; worst hour 17 mm (27% of the storm); water beside the road 0.29 m above its crest (design freeboard 0.30 m; P 1.00); road sag 1.1 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 17 mm; catchment 60.2 ha) (P 0.70); a culvert within 100 m is overtopped |
| 15 | 0.96 | Carleton Road | Millbury | 0.47 m of water at peak; over 30 cm for 4.5 h; 30 cm reached 9.0 h into the storm; worst hour 18 mm (24% of the storm); a culvert within 100 m is overtopped |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
