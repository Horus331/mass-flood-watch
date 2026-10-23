# Road-closure prototype: jul2021_rain_jul2021_hourly

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on CPU (OpenMP)), 20 m grid, storm from 2021-07-09T08:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 6,275 |
| Expected closures (sum of probabilities) | 41.6 |
| Segments with closure probability >= 50% | 16 (9.0 km) |
| Further segments that may close (stream reaches the road crest) | 56 (29.5 km) |
| Culverts overtopped / surcharged | 61 / 0 of 1161 |
| Road segments cut off from hospitals | 155 |
| Worst added trip time to a hospital | 15.3 min |
| Heaviest hour of rain | 19.5 mm |
| Flood model run time | 1209 s |

## Checks against what happened

- Storm-day flood reports in the area: 1; water >= 10 cm within 100 m of 0% of them, vs 40% of random points (any day).
- Segments flagged impassable are 0.0x as likely as an average segment to have a report within 200 m.
- MassDOT repeating flood sites in the area: 4; 0 have a segment within 150 m at P >= 0.5 (share of all segments at P >= 0.5: 0.3%).

## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 1.00 | Martin Luther King Jr Boulevard | Worcester | 2.82 m of water at peak; over 30 cm for 17.5 h; 30 cm reached 1.0 h into the storm; worst hour 14 mm (27% of the storm); water beside the road 2.74 m above its crest (design freeboard 0.30 m; P 1.00); fast water: depth x speed 0.33 m2/s (small cars unstable from 0.3); runoff beside / along the road at 1.2 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.66); road sag 3.2 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 14 mm; catchment 60.2 ha) (P 1.00); a culvert within 100 m is overtopped |
| 2 | 1.00 | Martin Luther King Jr Boulevard | Worcester | 2.12 m of water at peak; over 30 cm for 17.5 h; 30 cm reached 1.0 h into the storm; worst hour 14 mm (27% of the storm); water beside the road 1.80 m above its crest (design freeboard 0.30 m; P 1.00); fast water: depth x speed 0.20 m2/s (small cars unstable from 0.3); runoff beside / along the road at 2.3 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.97); road sag 3.2 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 14 mm; catchment 60.2 ha) (P 1.00); a culvert within 100 m is overtopped |
| 3 | 1.00 | Foster Street | Worcester | 1.09 m of water at peak; over 30 cm for 11.0 h; 30 cm reached 7.5 h into the storm; worst hour 14 mm (27% of the storm); water beside the road 0.37 m below its crest (design freeboard 0.30 m; P 0.33); a culvert within 100 m is overtopped |
| 4 | 1.00 | Foster Street | Worcester | 1.09 m of water at peak; over 30 cm for 11.0 h; 30 cm reached 7.5 h into the storm; worst hour 14 mm (27% of the storm); water beside the road 0.28 m below its crest (design freeboard 0.30 m; P 0.55); a culvert within 100 m is overtopped |
| 5 | 1.00 | (unnamed) | Worcester | 0.97 m of water at peak; over 30 cm for 9.5 h; 30 cm reached 9.0 h into the storm; worst hour 14 mm (27% of the storm); a culvert within 100 m is overtopped |
| 6 | 1.00 | East Park Terrace | Worcester | 0.76 m of water at peak; over 30 cm for 9.5 h; 30 cm reached 9.0 h into the storm; worst hour 14 mm (26% of the storm); water beside the road 0.66 m above its crest (design freeboard 0.30 m; P 1.00); road sag 4.3 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 14 mm; catchment 127.8 ha) (P 1.00) |
| 7 | 0.99 | Shrewsbury Street | Worcester | 0.54 m of water at peak; over 30 cm for 9.0 h; 30 cm reached 9.5 h into the storm; worst hour 14 mm (27% of the storm); water beside the road 0.46 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.9 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 14 mm; catchment 127.8 ha) (P 1.00) |
| 8 | 0.92 | Shrewsbury Street | Worcester | 0.44 m of water at peak; over 30 cm for 8.0 h; 30 cm reached 10.5 h into the storm; worst hour 14 mm (27% of the storm); water beside the road 0.36 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.9 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 14 mm; catchment 127.8 ha) (P 1.00) |
| 9 | 0.88 | Fantasia Drive | Worcester | 0.42 m of water at peak; over 30 cm for 7.5 h; 30 cm reached 11.0 h into the storm; worst hour 14 mm (26% of the storm); water beside the road 0.35 m above its crest (design freeboard 0.30 m; P 1.00); road sag 1.3 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 14 mm; catchment 127.8 ha) (P 0.88) |
| 10 | 0.80 | Wellington Street | Worcester | 0.38 m of water at peak; over 30 cm for 2.5 h; 30 cm reached 9.5 h into the storm; worst hour 12 mm (25% of the storm); water beside the road 0.40 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.9 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 12 mm; catchment 15.1 ha) (P 0.97) |
| 11 | 0.80 | Murray Avenue | Worcester | 0.38 m of water at peak; over 30 cm for 2.5 h; 30 cm reached 9.5 h into the storm; worst hour 13 mm (25% of the storm); water beside the road 0.40 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.9 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 12 mm; catchment 15.1 ha) (P 0.97) |
| 12 | 0.64 | Carleton Road | Millbury | 0.34 m of water at peak; over 30 cm for 2.5 h; 30 cm reached 10.0 h into the storm; worst hour 15 mm (24% of the storm); a culvert within 100 m is overtopped |
| 13 | 0.59 | Auburn Street | Auburn | 0.32 m of water at peak; over 30 cm for 2.0 h; 30 cm reached 16.5 h into the storm; worst hour 13 mm (24% of the storm) |
| 14 | 0.51 | James Street | Worcester | 0.30 m of water at peak; over 30 cm for 0.5 h; 30 cm reached 10.5 h into the storm; worst hour 14 mm (27% of the storm); a culvert within 100 m is overtopped |
| 15 | 0.50 | Dewey Street | Worcester | 0.30 m of water at peak; worst hour 13 mm (26% of the storm); water beside the road 0.21 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.9 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 12 mm; catchment 12.8 ha) (P 0.51) |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
