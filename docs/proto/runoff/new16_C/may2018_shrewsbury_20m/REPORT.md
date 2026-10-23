# Road-closure prototype: may2018_loss_may2018_shrewsbury_20m

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on CPU (OpenMP)), 20 m grid, storm from 2018-05-15T14:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 9,355 |
| Expected closures (sum of probabilities) | 30.9 |
| Segments with closure probability >= 50% | 7 (2.8 km) |
| Further segments that may close (stream reaches the road crest) | 36 (22.3 km) |
| Culverts overtopped / surcharged | 19 / 0 of 1400 |
| Road segments cut off from hospitals | 56 |
| Worst added trip time to a hospital | 11.7 min |
| Heaviest hour of rain | 17.3 mm |
| Flood model run time | 999 s |

## Checks against what happened

- Storm-day flood reports in the area: 1; water >= 10 cm within 100 m of 0% of them, vs 21% of random points (any day).
- Segments flagged impassable are 0.0x as likely as an average segment to have a report within 200 m.
- MassDOT repeating flood sites in the area: 10; 0 have a segment within 150 m at P >= 0.5 (share of all segments at P >= 0.5: 0.1%).

## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 1.00 | Martin Luther King Jr Boulevard | Worcester | 2.12 m of water at peak; over 30 cm for 17.5 h; 30 cm reached 1.0 h into the storm; worst hour 12 mm (66% of the storm); water beside the road 2.05 m above its crest (design freeboard 0.30 m; P 1.00); road sag 3.2 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 12 mm; catchment 60.2 ha) (P 1.00) |
| 2 | 1.00 | Martin Luther King Jr Boulevard | Worcester | 1.43 m of water at peak; over 30 cm for 17.5 h; 30 cm reached 1.0 h into the storm; worst hour 12 mm (66% of the storm); water beside the road 0.92 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 2.3 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.81); road sag 3.2 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 12 mm; catchment 60.2 ha) (P 1.00); a culvert within 100 m is overtopped |
| 3 | 1.00 | Foster Street | Worcester | 0.96 m of water at peak; over 30 cm for 11.5 h; 30 cm reached 7.0 h into the storm; worst hour 12 mm (66% of the storm); water beside the road 0.40 m below its crest (design freeboard 0.30 m; P 0.25); a culvert within 100 m is overtopped |
| 4 | 1.00 | Foster Street | Worcester | 0.96 m of water at peak; over 30 cm for 11.5 h; 30 cm reached 7.0 h into the storm; worst hour 12 mm (66% of the storm); water beside the road 0.28 m below its crest (design freeboard 0.30 m; P 0.55); a culvert within 100 m is overtopped |
| 5 | 1.00 | (unnamed) | Worcester | 0.76 m of water at peak; over 30 cm for 8.5 h; 30 cm reached 10.0 h into the storm; worst hour 14 mm (69% of the storm); a culvert within 100 m is overtopped |
| 6 | 0.98 | East Park Terrace | Worcester | 0.52 m of water at peak; over 30 cm for 8.5 h; 30 cm reached 10.0 h into the storm; worst hour 14 mm (69% of the storm); water beside the road 0.42 m above its crest (design freeboard 0.30 m; P 1.00); road sag 4.3 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 14 mm; catchment 127.8 ha) (P 0.98) |
| 7 | 0.83 | Bearfoot Road | Northborough | 0.40 m of water at peak; worst hour 12 mm (63% of the storm); water beside the road 0.16 m below its crest (design freeboard 0.30 m; P 0.82); a culvert within 100 m is overtopped |
| 8 | 0.48 | Shrewsbury Street | Worcester | 0.30 m of water at peak; over 30 cm for 3.5 h; 30 cm reached 15.0 h into the storm; worst hour 14 mm (70% of the storm); water beside the road 0.21 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.9 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 14 mm; catchment 127.8 ha) (P 0.69) |
| 9 | 0.42 | Stafford Street | Worcester | 0.28 m of water at peak; worst hour 16 mm (71% of the storm); a culvert within 100 m is overtopped |
| 10 | 0.42 | Ludlow Street | Worcester | 0.28 m of water at peak; worst hour 16 mm (70% of the storm); a culvert within 100 m is overtopped |
| 11 | 0.39 | Ramp-West Boylston Dr To Rt 190 Nb | Worcester | 0.27 m of water at peak; worst hour 12 mm (56% of the storm); water beside the road 0.13 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.8 m deep (underpass, drains sized for the 50-yr hour, 58 mm; peak hour here 12 mm; catchment 52.2 ha) (P 0.40) |
| 12 | 0.33 | Providence Street | Millbury | 0.26 m of water at peak; worst hour 10 mm (59% of the storm); a culvert within 100 m is overtopped |
| 13 | 0.30 | Millbury Street | Grafton | 0.25 m of water at peak; worst hour 7 mm (51% of the storm) |
| 14 | 0.27 | Wellington Street | Worcester | 0.24 m of water at peak; worst hour 12 mm (66% of the storm); water beside the road 0.18 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.9 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 12 mm; catchment 15.1 ha) (P 0.89) |
| 15 | 0.27 | Murray Avenue | Worcester | 0.24 m of water at peak; worst hour 12 mm (66% of the storm); water beside the road 0.24 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.9 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 12 mm; catchment 15.1 ha) (P 0.89) |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
