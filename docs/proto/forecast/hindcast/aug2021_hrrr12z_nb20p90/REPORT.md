# Road-closure prototype: aug2021_fc_aug2021_hrrr12z_nb20p90

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on CPU (OpenMP)), 20 m grid, storm from 2021-08-19T12:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 8,354 |
| Expected closures (sum of probabilities) | 267.3 |
| Segments with closure probability >= 50% | 196 (111.1 km) |
| Further segments that may close (stream reaches the road crest) | 278 (135.8 km) |
| Culverts overtopped / surcharged | 261 / 4 of 1347 |
| Road segments cut off from hospitals | 1523 |
| Worst added trip time to a hospital | 35.8 min |
| Heaviest hour of rain | 35.5 mm |
| Flood model run time | 860 s |

## Checks against what happened

- Storm-day flood reports in the area: 5; water >= 10 cm within 100 m of 60% of them, vs 65% of random points (any day).
- Segments flagged impassable are 3.38x as likely as an average segment to have a report within 200 m.
- MassDOT repeating flood sites in the area: 10; 6 have a segment within 150 m at P >= 0.5 (share of all segments at P >= 0.5: 2.3%).

## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 1.00 | Route 70 | Worcester | 0.68 m of water at peak; over 30 cm for 11.0 h; 30 cm reached 4.0 h into the storm; worst hour 30 mm (32% of the storm); a culvert within 100 m is overtopped |
| 2 | 1.00 | Route 70 | Worcester | 0.68 m of water at peak; over 30 cm for 11.0 h; 30 cm reached 4.0 h into the storm; worst hour 30 mm (32% of the storm); a culvert within 100 m is overtopped |
| 3 | 1.00 | Martin Luther King Jr Boulevard | Worcester | 4.33 m of water at peak; over 30 cm for 14.5 h; 30 cm reached 1.0 h into the storm; worst hour 30 mm (32% of the storm); water beside the road 4.25 m above its crest (design freeboard 0.30 m; P 1.00); road sag 3.2 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 30 mm; catchment 60.2 ha) (P 1.00); a culvert within 100 m is overtopped |
| 4 | 1.00 | Martin Luther King Jr Boulevard | Worcester | 3.63 m of water at peak; over 30 cm for 14.5 h; 30 cm reached 1.0 h into the storm; worst hour 30 mm (32% of the storm); water beside the road 3.31 m above its crest (design freeboard 0.30 m; P 1.00); road sag 3.2 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 30 mm; catchment 60.2 ha) (P 1.00); a culvert within 100 m is overtopped |
| 5 | 1.00 | Shrewsbury Street | Worcester | 1.04 m of water at peak; over 30 cm for 11.5 h; 30 cm reached 4.0 h into the storm; worst hour 30 mm (32% of the storm); water beside the road 0.95 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.8 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 30 mm; catchment 127.8 ha) (P 1.00) |
| 6 | 1.00 | Shrewsbury Street | Worcester | 1.14 m of water at peak; over 30 cm for 12.0 h; 30 cm reached 3.5 h into the storm; worst hour 30 mm (32% of the storm); water beside the road 1.06 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.8 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 30 mm; catchment 127.8 ha) (P 1.00) |
| 7 | 1.00 | Route 9 | Worcester | 0.67 m of water at peak; over 30 cm for 10.5 h; 30 cm reached 4.0 h into the storm; worst hour 30 mm (32% of the storm); a culvert within 100 m is overtopped |
| 8 | 1.00 | Foster Street | Worcester | 2.60 m of water at peak; over 30 cm for 12.0 h; 30 cm reached 3.5 h into the storm; worst hour 29 mm (31% of the storm); water beside the road 0.61 m above its crest (design freeboard 0.30 m; P 1.00); road sag 1.2 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 29 mm; catchment 22.1 ha) (P 1.00); a culvert within 100 m is overtopped |
| 9 | 1.00 | Martin Luther King Jr Boulevard | Worcester | 1.30 m of water at peak; over 30 cm for 10.0 h; 30 cm reached 5.5 h into the storm; worst hour 30 mm (31% of the storm); water beside the road 1.13 m above its crest (design freeboard 0.30 m; P 1.00); a culvert within 100 m is overtopped |
| 10 | 1.00 | Major Taylor Boulevard | Worcester | 1.74 m of water at peak; over 30 cm for 11.5 h; 30 cm reached 4.0 h into the storm; worst hour 30 mm (32% of the storm); water beside the road 1.49 m above its crest (design freeboard 0.30 m; P 1.00); road sag 1.1 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 30 mm; catchment 60.2 ha) (P 1.00); a culvert within 100 m is overtopped |
| 11 | 1.00 | Thomas Street | Worcester | 1.13 m of water at peak; over 30 cm for 10.0 h; 30 cm reached 5.5 h into the storm; worst hour 30 mm (31% of the storm); water beside the road 1.09 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.5 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 30 mm; catchment 60.2 ha) (P 1.00); a culvert within 100 m is overtopped |
| 12 | 1.00 | Major Taylor Boulevard | Worcester | 1.74 m of water at peak; over 30 cm for 11.5 h; 30 cm reached 4.0 h into the storm; worst hour 30 mm (32% of the storm); water beside the road 1.49 m above its crest (design freeboard 0.30 m; P 1.00); road sag 1.1 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 30 mm; catchment 60.2 ha) (P 1.00); a culvert within 100 m is overtopped |
| 13 | 1.00 | Foster Street | Worcester | 2.60 m of water at peak; over 30 cm for 12.0 h; 30 cm reached 3.5 h into the storm; worst hour 29 mm (31% of the storm); water beside the road 0.63 m above its crest (design freeboard 0.30 m; P 1.00); road sag 1.2 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 29 mm; catchment 22.1 ha) (P 1.00); a culvert within 100 m is overtopped |
| 14 | 1.00 | Route 20 | Shrewsbury | 0.64 m of water at peak; over 30 cm for 6.5 h; 30 cm reached 4.0 h into the storm; worst hour 30 mm (36% of the storm); water beside the road 0.32 m below its crest (design freeboard 0.30 m; P 0.45); culvert (Big Bummet Brook): headwater 2.09 m vs road crest 1.83 m, 8.3 m3/s |
| 15 | 1.00 | Southbridge Street | Worcester | 0.82 m of water at peak; over 30 cm for 10.5 h; 30 cm reached 5.0 h into the storm; worst hour 28 mm (31% of the storm); water beside the road 0.75 m above its crest (design freeboard 0.30 m; P 1.00); road sag 1.2 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 28 mm; catchment 13.4 ha) (P 1.00); a culvert within 100 m is overtopped |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
