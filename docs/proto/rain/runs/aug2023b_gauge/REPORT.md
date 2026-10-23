# Road-closure prototype: aug2023b_rain_aug2023b_gauge

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on CPU (OpenMP)), 20 m grid, storm from 2023-08-18T05:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 8,013 |
| Expected closures (sum of probabilities) | 39.5 |
| Segments with closure probability >= 50% | 11 (6.2 km) |
| Further segments that may close (stream reaches the road crest) | 23 (13.1 km) |
| Culverts overtopped / surcharged | 62 / 0 of 1291 |
| Road segments cut off from hospitals | 218 |
| Worst added trip time to a hospital | 19.0 min |
| Heaviest hour of rain | 57.6 mm |
| Flood model run time | 920 s |

## Checks against what happened

- Storm-day flood reports in the area: 0; water >= 10 cm within 100 m of 0% of them, vs 17% of random points (any day).
- MassDOT repeating flood sites in the area: 8; 0 have a segment within 150 m at P >= 0.5 (share of all segments at P >= 0.5: 0.1%).

## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 1.00 | Martin Luther King Jr Boulevard | Worcester | 1.72 m of water at peak; over 30 cm for 17.5 h; 30 cm reached 1.0 h into the storm; worst hour 22 mm (71% of the storm); water beside the road 1.64 m above its crest (design freeboard 0.30 m; P 1.00); road sag 3.2 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 22 mm; catchment 60.2 ha) (P 1.00) |
| 2 | 1.00 | Martin Luther King Jr Boulevard | Worcester | 1.02 m of water at peak; over 30 cm for 17.5 h; 30 cm reached 1.0 h into the storm; worst hour 22 mm (71% of the storm); water beside the road 0.51 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 2.2 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.41); road sag 3.2 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 22 mm; catchment 60.2 ha) (P 1.00) |
| 3 | 1.00 | Foster Street | Worcester | 0.84 m of water at peak; over 30 cm for 11.5 h; 30 cm reached 7.0 h into the storm; worst hour 23 mm (72% of the storm); water beside the road 0.40 m below its crest (design freeboard 0.30 m; P 0.25); a culvert within 100 m is overtopped |
| 4 | 1.00 | Foster Street | Worcester | 0.84 m of water at peak; over 30 cm for 11.5 h; 30 cm reached 7.0 h into the storm; worst hour 23 mm (72% of the storm); water beside the road 0.28 m below its crest (design freeboard 0.30 m; P 0.55); a culvert within 100 m is overtopped |
| 5 | 1.00 | (unnamed) | Worcester | 1.19 m of water at peak; over 30 cm for 9.0 h; 30 cm reached 9.5 h into the storm; worst hour 23 mm (65% of the storm); a culvert within 100 m is overtopped |
| 6 | 0.99 | East Park Terrace | Worcester | 0.53 m of water at peak; over 30 cm for 6.5 h; 30 cm reached 12.0 h into the storm; worst hour 23 mm (65% of the storm); water beside the road 0.43 m above its crest (design freeboard 0.30 m; P 1.00); road sag 4.3 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 23 mm; catchment 127.8 ha) (P 0.99) |
| 7 | 0.99 | Providence Street | Millbury | 0.53 m of water at peak; over 30 cm for 10.5 h; 30 cm reached 8.0 h into the storm; worst hour 43 mm (69% of the storm); a culvert within 100 m is overtopped |
| 8 | 0.99 | Providence Road | Sutton | 0.52 m of water at peak; over 30 cm for 8.0 h; 30 cm reached 8.0 h into the storm; worst hour 54 mm (76% of the storm); a culvert within 100 m is overtopped |
| 9 | 0.98 | Millbury Street | Grafton | 0.50 m of water at peak; over 30 cm for 10.0 h; 30 cm reached 8.5 h into the storm; worst hour 53 mm (67% of the storm) |
| 10 | 0.84 | Fitzpatrick Road | Grafton | 0.40 m of water at peak; over 30 cm for 4.5 h; 30 cm reached 10.5 h into the storm; worst hour 52 mm (65% of the storm) |
| 11 | 0.55 | Shrewsbury Street | Worcester | 0.31 m of water at peak; over 30 cm for 4.0 h; 30 cm reached 14.5 h into the storm; worst hour 23 mm (63% of the storm); water beside the road 0.23 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.9 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 23 mm; catchment 127.8 ha) (P 0.74) |
| 12 | 0.48 | Sycamore Street | Millbury | 0.29 m of water at peak; worst hour 40 mm (69% of the storm); a culvert within 100 m is overtopped |
| 13 | 0.46 | Blanchard Road | Grafton | 0.29 m of water at peak; worst hour 56 mm (69% of the storm) |
| 14 | 0.46 | Carleton Road | Millbury | 0.29 m of water at peak; worst hour 35 mm (65% of the storm); a culvert within 100 m is overtopped |
| 15 | 0.42 | (unnamed) | Sutton | 0.28 m of water at peak; worst hour 50 mm (90% of the storm); a culvert within 100 m is overtopped |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
