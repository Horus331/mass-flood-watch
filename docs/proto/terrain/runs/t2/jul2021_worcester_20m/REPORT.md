# Road-closure prototype: jul2021_loss_jul2021_worcester_20m

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on CPU (OpenMP)), 20 m grid, storm from 2021-07-09T08:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 6,275 |
| Expected closures (sum of probabilities) | 29.0 |
| Segments with closure probability >= 50% | 9 (5.7 km) |
| Further segments that may close (stream reaches the road crest) | 40 (21.9 km) |
| Culverts overtopped / surcharged | 39 / 0 of 1161 |
| Road segments cut off from hospitals | 101 |
| Worst added trip time to a hospital | 13.2 min |
| Heaviest hour of rain | 19.5 mm |
| Flood model run time | 1211 s |

## Checks against what happened

- Storm-day flood reports in the area: 1; water >= 10 cm within 100 m of 0% of them, vs 33% of random points (any day).
- Segments flagged impassable are 0.0x as likely as an average segment to have a report within 200 m.
- MassDOT repeating flood sites in the area: 4; 0 have a segment within 150 m at P >= 0.5 (share of all segments at P >= 0.5: 0.1%).

## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 1.00 | East Park Terrace | Worcester | 0.69 m of water at peak; over 30 cm for 9.5 h; 30 cm reached 9.0 h into the storm; worst hour 14 mm (26% of the storm); water beside the road 0.59 m above its crest (design freeboard 0.30 m; P 1.00); road sag 4.3 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 14 mm; catchment 127.8 ha) (P 1.00) |
| 2 | 0.96 | Shrewsbury Street | Worcester | 0.47 m of water at peak; over 30 cm for 8.0 h; 30 cm reached 10.5 h into the storm; worst hour 14 mm (27% of the storm); water beside the road 0.39 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.9 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 14 mm; catchment 127.8 ha) (P 0.99) |
| 3 | 0.83 | Cambridge Street | Worcester | 0.39 m of water at peak; over 30 cm for 5.5 h; 30 cm reached 13.0 h into the storm; worst hour 13 mm (25% of the storm); water beside the road 0.25 m above its crest (design freeboard 0.30 m; P 1.00); road sag 2.0 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 13 mm; catchment 77.2 ha) (P 0.83) |
| 4 | 0.76 | Shrewsbury Street | Worcester | 0.37 m of water at peak; over 30 cm for 6.5 h; 30 cm reached 12.0 h into the storm; worst hour 14 mm (27% of the storm); water beside the road 0.29 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.9 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 14 mm; catchment 127.8 ha) (P 0.99) |
| 5 | 0.74 | Martin Luther King Jr Boulevard | Worcester | 0.36 m of water at peak; over 30 cm for 3.5 h; 30 cm reached 10.0 h into the storm; worst hour 14 mm (27% of the storm); water beside the road 0.28 m above its crest (design freeboard 0.30 m; P 1.00); road sag 3.2 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 14 mm; catchment 60.2 ha) (P 0.74) |
| 6 | 0.68 | Fantasia Drive | Worcester | 0.35 m of water at peak; over 30 cm for 6.0 h; 30 cm reached 12.5 h into the storm; worst hour 14 mm (26% of the storm); water beside the road 0.28 m above its crest (design freeboard 0.30 m; P 1.00); road sag 1.3 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 14 mm; catchment 127.8 ha) (P 0.69) |
| 7 | 0.54 | Wellington Street | Worcester | 0.31 m of water at peak; over 30 cm for 1.0 h; 30 cm reached 10.5 h into the storm; worst hour 12 mm (25% of the storm); water beside the road 0.36 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.9 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 12 mm; catchment 15.1 ha) (P 0.93) |
| 8 | 0.54 | Murray Avenue | Worcester | 0.31 m of water at peak; over 30 cm for 1.0 h; 30 cm reached 10.5 h into the storm; worst hour 13 mm (25% of the storm); water beside the road 0.36 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.9 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 12 mm; catchment 15.1 ha) (P 0.93) |
| 9 | 0.53 | Auburn Street | Auburn | 0.31 m of water at peak; over 30 cm for 1.5 h; 30 cm reached 14.5 h into the storm; worst hour 13 mm (24% of the storm) |
| 10 | 0.44 | Carleton Road | Millbury | 0.28 m of water at peak; worst hour 15 mm (24% of the storm); a culvert within 100 m is overtopped |
| 11 | 0.37 | Route 12 | Auburn | 0.27 m of water at peak; worst hour 13 mm (24% of the storm) |
| 12 | 0.35 | Stafford Street | Worcester | 0.26 m of water at peak; worst hour 14 mm (28% of the storm); water beside the road 0.11 m above its crest (design freeboard 0.30 m; P 1.00); a culvert within 100 m is overtopped |
| 13 | 0.29 | Dewey Street | Worcester | 0.25 m of water at peak; worst hour 13 mm (26% of the storm); water beside the road 0.16 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.9 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 12 mm; catchment 12.8 ha) (P 0.30) |
| 14 | 0.29 | Parker Street | Worcester | 0.25 m of water at peak; worst hour 13 mm (27% of the storm); water beside the road 0.16 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.9 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 12 mm; catchment 12.8 ha) (P 0.30) |
| 15 | 0.28 | Sycamore Street | Millbury | 0.24 m of water at peak; worst hour 16 mm (26% of the storm); a culvert within 100 m is overtopped |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
