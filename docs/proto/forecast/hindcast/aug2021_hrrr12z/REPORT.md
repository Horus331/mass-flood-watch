# Road-closure prototype: aug2021_fc_aug2021_hrrr12z

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on CPU (OpenMP)), 20 m grid, storm from 2021-08-19T12:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 8,354 |
| Expected closures (sum of probabilities) | 90.1 |
| Segments with closure probability >= 50% | 51 (26.1 km) |
| Further segments that may close (stream reaches the road crest) | 144 (77.9 km) |
| Culverts overtopped / surcharged | 80 / 1 of 1347 |
| Road segments cut off from hospitals | 441 |
| Worst added trip time to a hospital | 13.3 min |
| Heaviest hour of rain | 39.3 mm |
| Flood model run time | 372 s |

## Checks against what happened

- Storm-day flood reports in the area: 5; water >= 10 cm within 100 m of 60% of them, vs 50% of random points (any day).
- Segments flagged impassable are 2.19x as likely as an average segment to have a report within 200 m.
- MassDOT repeating flood sites in the area: 10; 2 have a segment within 150 m at P >= 0.5 (share of all segments at P >= 0.5: 0.6%).

## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 1.00 | Martin Luther King Jr Boulevard | Worcester | 3.69 m of water at peak; over 30 cm for 14.5 h; 30 cm reached 1.0 h into the storm; worst hour 30 mm (48% of the storm); water beside the road 3.61 m above its crest (design freeboard 0.30 m; P 1.00); road sag 3.2 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 30 mm; catchment 60.2 ha) (P 1.00); a culvert within 100 m is overtopped |
| 2 | 1.00 | Martin Luther King Jr Boulevard | Worcester | 2.99 m of water at peak; over 30 cm for 14.5 h; 30 cm reached 1.0 h into the storm; worst hour 30 mm (48% of the storm); water beside the road 2.67 m above its crest (design freeboard 0.30 m; P 1.00); road sag 3.2 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 30 mm; catchment 60.2 ha) (P 1.00); a culvert within 100 m is overtopped |
| 3 | 1.00 | Shrewsbury Street | Worcester | 0.65 m of water at peak; over 30 cm for 11.0 h; 30 cm reached 4.5 h into the storm; worst hour 33 mm (52% of the storm); water beside the road 0.56 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.9 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 33 mm; catchment 127.8 ha) (P 1.00) |
| 4 | 1.00 | Shrewsbury Street | Worcester | 0.75 m of water at peak; over 30 cm for 11.0 h; 30 cm reached 4.5 h into the storm; worst hour 33 mm (52% of the storm); water beside the road 0.67 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.9 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 33 mm; catchment 127.8 ha) (P 1.00) |
| 5 | 1.00 | Foster Street | Worcester | 1.96 m of water at peak; over 30 cm for 11.0 h; 30 cm reached 4.5 h into the storm; worst hour 30 mm (48% of the storm); water beside the road 0.02 m below its crest (design freeboard 0.30 m; P 0.97); road sag 1.2 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 30 mm; catchment 22.1 ha) (P 0.13); a culvert within 100 m is overtopped |
| 6 | 1.00 | Major Taylor Boulevard | Worcester | 1.10 m of water at peak; over 30 cm for 10.0 h; 30 cm reached 5.5 h into the storm; worst hour 30 mm (48% of the storm); water beside the road 0.85 m above its crest (design freeboard 0.30 m; P 1.00); road sag 1.1 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 29 mm; catchment 60.2 ha) (P 1.00); a culvert within 100 m is overtopped |
| 7 | 1.00 | Foster Street | Worcester | 1.96 m of water at peak; over 30 cm for 11.0 h; 30 cm reached 4.5 h into the storm; worst hour 30 mm (48% of the storm); water beside the road 0.01 m below its crest (design freeboard 0.30 m; P 0.97); road sag 1.2 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 30 mm; catchment 22.1 ha) (P 0.13); a culvert within 100 m is overtopped |
| 8 | 1.00 | Major Taylor Boulevard | Worcester | 1.10 m of water at peak; over 30 cm for 10.0 h; 30 cm reached 5.5 h into the storm; worst hour 30 mm (48% of the storm); water beside the road 0.85 m above its crest (design freeboard 0.30 m; P 1.00); road sag 1.1 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 29 mm; catchment 60.2 ha) (P 1.00); a culvert within 100 m is overtopped |
| 9 | 1.00 | Martin Luther King Jr Boulevard | Worcester | 0.66 m of water at peak; over 30 cm for 7.0 h; 30 cm reached 8.5 h into the storm; worst hour 29 mm (47% of the storm); water beside the road 0.49 m above its crest (design freeboard 0.30 m; P 1.00); a culvert within 100 m is overtopped |
| 10 | 1.00 | Route 122 | Northbridge | 1.00 m of water at peak; over 30 cm for 15.0 h; 30 cm reached 0.5 h into the storm; worst hour 14 mm (62% of the storm); a culvert within 100 m is overtopped |
| 11 | 1.00 | (unnamed) | Worcester | 4.37 m of water at peak; over 30 cm for 11.5 h; 30 cm reached 4.0 h into the storm; worst hour 31 mm (48% of the storm); a culvert within 100 m is overtopped |
| 12 | 1.00 | Bridge Street | Worcester | 0.93 m of water at peak; over 30 cm for 9.0 h; 30 cm reached 6.5 h into the storm; worst hour 30 mm (49% of the storm); water beside the road 0.62 m above its crest (design freeboard 0.30 m; P 1.00); road sag 2.3 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 30 mm; catchment 22.1 ha) (P 1.00); a culvert within 100 m is overtopped |
| 13 | 1.00 | East Park Terrace | Worcester | 0.97 m of water at peak; over 30 cm for 11.5 h; 30 cm reached 4.0 h into the storm; worst hour 33 mm (51% of the storm); water beside the road 0.87 m above its crest (design freeboard 0.30 m; P 1.00); road sag 4.3 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 33 mm; catchment 127.8 ha) (P 1.00) |
| 14 | 1.00 | Commercial Street | Worcester | 0.69 m of water at peak; over 30 cm for 7.0 h; 30 cm reached 8.5 h into the storm; worst hour 29 mm (47% of the storm); water beside the road 0.66 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.9 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 29 mm; catchment 60.2 ha) (P 1.00); a culvert within 100 m is overtopped |
| 15 | 1.00 | Providence Street | Millbury | 0.62 m of water at peak; over 30 cm for 12.0 h; 30 cm reached 3.5 h into the storm; worst hour 11 mm (48% of the storm); a culvert within 100 m is overtopped |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
