# Road-closure prototype: jul2021_loss_jul2021_cn

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on CPU (OpenMP)), 20 m grid, storm from 2021-07-09T08:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 6,083 |
| Expected closures (sum of probabilities) | 45.1 |
| Segments with closure probability >= 50% | 20 (11.9 km) |
| Further segments that may close (stream reaches the road crest) | 61 (32.5 km) |
| Culverts overtopped / surcharged | 65 / 0 of 1161 |
| Road segments cut off from hospitals | 166 |
| Worst added trip time to a hospital | 15.8 min |
| Heaviest hour of rain | 19.5 mm |
| Flood model run time | 892 s |

## Checks against what happened

- Storm-day flood reports in the area: 1; water >= 10 cm within 100 m of 0% of them, vs 49% of random points (any day).
- Segments flagged impassable are 0.0x as likely as an average segment to have a report within 200 m.
- MassDOT repeating flood sites in the area: 4; 0 have a segment within 150 m at P >= 0.5 (share of all segments at P >= 0.5: 0.3%).

## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 1.00 | Martin Luther King Jr Boulevard | Worcester | 2.77 m of water at peak; over 30 cm for 17.5 h; 30 cm reached 1.0 h into the storm; worst hour 14 mm (27% of the storm); water beside the road 2.69 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 3.1 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.99); road sag 3.2 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 14 mm; catchment 60.2 ha) (P 1.00) |
| 2 | 1.00 | Martin Luther King Jr Boulevard | Worcester | 2.07 m of water at peak; over 30 cm for 17.5 h; 30 cm reached 1.0 h into the storm; worst hour 14 mm (27% of the storm); water beside the road 1.74 m above its crest (design freeboard 0.30 m; P 1.00); fast water: depth x speed 0.21 m2/s (small cars unstable from 0.3); runoff beside / along the road at 4.3 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.84); road sag 3.2 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 14 mm; catchment 60.2 ha) (P 1.00); a culvert within 100 m is overtopped |
| 3 | 1.00 | Foster Street | Worcester | 1.04 m of water at peak; over 30 cm for 9.5 h; 30 cm reached 9.0 h into the storm; worst hour 14 mm (27% of the storm); water beside the road 0.34 m below its crest (design freeboard 0.30 m; P 0.40); a culvert within 100 m is overtopped |
| 4 | 1.00 | Foster Street | Worcester | 1.04 m of water at peak; over 30 cm for 9.5 h; 30 cm reached 9.0 h into the storm; worst hour 14 mm (27% of the storm); water beside the road 0.15 m below its crest (design freeboard 0.30 m; P 0.84); runoff beside / along the road at 2.0 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.31); a culvert within 100 m is overtopped |
| 5 | 1.00 | (unnamed) | Worcester | 0.96 m of water at peak; over 30 cm for 9.5 h; 30 cm reached 9.0 h into the storm; worst hour 14 mm (27% of the storm); a culvert within 100 m is overtopped |
| 6 | 1.00 | East Park Terrace | Worcester | 0.77 m of water at peak; over 30 cm for 10.0 h; 30 cm reached 8.5 h into the storm; worst hour 14 mm (26% of the storm); water beside the road 0.67 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 1.2 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.17); road sag 4.3 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 14 mm; catchment 127.8 ha) (P 1.00) |
| 7 | 0.99 | Shrewsbury Street | Worcester | 0.55 m of water at peak; over 30 cm for 9.0 h; 30 cm reached 9.5 h into the storm; worst hour 14 mm (27% of the storm); water beside the road 0.47 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 0.7 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.10); road sag 0.9 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 14 mm; catchment 127.8 ha) (P 1.00) |
| 8 | 0.93 | Shrewsbury Street | Worcester | 0.45 m of water at peak; over 30 cm for 8.0 h; 30 cm reached 10.5 h into the storm; worst hour 14 mm (27% of the storm); water beside the road 0.37 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.9 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 14 mm; catchment 127.8 ha) (P 1.00) |
| 9 | 0.90 | Fantasia Drive | Worcester | 0.43 m of water at peak; over 30 cm for 8.0 h; 30 cm reached 10.5 h into the storm; worst hour 14 mm (26% of the storm); water beside the road 0.36 m above its crest (design freeboard 0.30 m; P 1.00); road sag 1.3 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 14 mm; catchment 127.8 ha) (P 0.90) |
| 10 | 0.85 | Wellington Street | Worcester | 0.40 m of water at peak; over 30 cm for 2.5 h; 30 cm reached 9.5 h into the storm; worst hour 12 mm (25% of the storm); water beside the road 0.41 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.9 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 12 mm; catchment 15.1 ha) (P 0.97) |
| 11 | 0.85 | Murray Avenue | Worcester | 0.40 m of water at peak; over 30 cm for 2.5 h; 30 cm reached 9.0 h into the storm; worst hour 13 mm (25% of the storm); water beside the road 0.41 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 1.0 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.17); road sag 0.9 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 12 mm; catchment 15.1 ha) (P 0.97) |
| 12 | 0.73 | Carleton Road | Millbury | 0.36 m of water at peak; over 30 cm for 3.0 h; 30 cm reached 9.5 h into the storm; worst hour 15 mm (24% of the storm); a culvert within 100 m is overtopped |
| 13 | 0.57 | James Street | Worcester | 0.32 m of water at peak; over 30 cm for 2.0 h; 30 cm reached 10.0 h into the storm; worst hour 14 mm (27% of the storm); a culvert within 100 m is overtopped |
| 14 | 0.55 | Dewey Street | Worcester | 0.31 m of water at peak; over 30 cm for 1.0 h; 30 cm reached 9.5 h into the storm; worst hour 13 mm (26% of the storm); water beside the road 0.23 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.9 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 12 mm; catchment 12.8 ha) (P 0.56) |
| 15 | 0.55 | Parker Street | Worcester | 0.31 m of water at peak; over 30 cm for 1.0 h; 30 cm reached 9.5 h into the storm; worst hour 13 mm (27% of the storm); water beside the road 0.23 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.9 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 12 mm; catchment 12.8 ha) (P 0.56) |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
