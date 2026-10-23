# Road-closure prototype: aug2023b_rain_aug2023b_gauge_dt5

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on CPU (OpenMP)), 20 m grid, storm from 2023-08-18T05:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 8,013 |
| Expected closures (sum of probabilities) | 41.5 |
| Segments with closure probability >= 50% | 11 (6.2 km) |
| Further segments that may close (stream reaches the road crest) | 25 (14.5 km) |
| Culverts overtopped / surcharged | 63 / 0 of 1291 |
| Road segments cut off from hospitals | 238 |
| Worst added trip time to a hospital | 19.9 min |
| Heaviest hour of rain | 57.6 mm |
| Flood model run time | 1026 s |

## Checks against what happened

- Storm-day flood reports in the area: 0; water >= 10 cm within 100 m of 0% of them, vs 17% of random points (any day).
- MassDOT repeating flood sites in the area: 8; 0 have a segment within 150 m at P >= 0.5 (share of all segments at P >= 0.5: 0.1%).

## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 1.00 | Martin Luther King Jr Boulevard | Worcester | 1.73 m of water at peak; over 30 cm for 17.5 h; 30 cm reached 1.0 h into the storm; worst hour 22 mm (71% of the storm); water beside the road 1.65 m above its crest (design freeboard 0.30 m; P 1.00); road sag 3.2 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 22 mm; catchment 60.2 ha) (P 1.00) |
| 2 | 1.00 | Martin Luther King Jr Boulevard | Worcester | 1.03 m of water at peak; over 30 cm for 17.5 h; 30 cm reached 1.0 h into the storm; worst hour 22 mm (71% of the storm); water beside the road 0.52 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 2.3 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.37); road sag 3.2 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 22 mm; catchment 60.2 ha) (P 1.00) |
| 3 | 1.00 | Foster Street | Worcester | 0.85 m of water at peak; over 30 cm for 11.5 h; 30 cm reached 7.0 h into the storm; worst hour 23 mm (72% of the storm); water beside the road 0.40 m below its crest (design freeboard 0.30 m; P 0.25); a culvert within 100 m is overtopped |
| 4 | 1.00 | Foster Street | Worcester | 0.85 m of water at peak; over 30 cm for 11.5 h; 30 cm reached 7.0 h into the storm; worst hour 23 mm (72% of the storm); water beside the road 0.28 m below its crest (design freeboard 0.30 m; P 0.55); a culvert within 100 m is overtopped |
| 5 | 1.00 | (unnamed) | Worcester | 1.20 m of water at peak; over 30 cm for 9.0 h; 30 cm reached 9.5 h into the storm; worst hour 23 mm (65% of the storm); a culvert within 100 m is overtopped |
| 6 | 0.99 | East Park Terrace | Worcester | 0.54 m of water at peak; over 30 cm for 7.0 h; 30 cm reached 11.5 h into the storm; worst hour 23 mm (65% of the storm); water beside the road 0.44 m above its crest (design freeboard 0.30 m; P 1.00); road sag 4.3 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 23 mm; catchment 127.8 ha) (P 0.99) |
| 7 | 0.99 | Providence Street | Millbury | 0.53 m of water at peak; over 30 cm for 10.5 h; 30 cm reached 8.0 h into the storm; worst hour 43 mm (69% of the storm); a culvert within 100 m is overtopped |
| 8 | 0.99 | Providence Road | Sutton | 0.53 m of water at peak; over 30 cm for 8.0 h; 30 cm reached 8.0 h into the storm; worst hour 54 mm (76% of the storm); a culvert within 100 m is overtopped |
| 9 | 0.98 | Millbury Street | Grafton | 0.51 m of water at peak; over 30 cm for 10.0 h; 30 cm reached 8.5 h into the storm; worst hour 53 mm (67% of the storm) |
| 10 | 0.85 | Fitzpatrick Road | Grafton | 0.41 m of water at peak; over 30 cm for 4.5 h; 30 cm reached 9.0 h into the storm; worst hour 52 mm (65% of the storm) |
| 11 | 0.56 | Shrewsbury Street | Worcester | 0.32 m of water at peak; over 30 cm for 4.5 h; 30 cm reached 14.0 h into the storm; worst hour 23 mm (63% of the storm); water beside the road 0.23 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.9 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 23 mm; catchment 127.8 ha) (P 0.76) |
| 12 | 0.49 | Sycamore Street | Millbury | 0.30 m of water at peak; worst hour 40 mm (69% of the storm); a culvert within 100 m is overtopped |
| 13 | 0.49 | Blanchard Road | Grafton | 0.30 m of water at peak; worst hour 56 mm (69% of the storm) |
| 14 | 0.47 | Carleton Road | Millbury | 0.29 m of water at peak; worst hour 35 mm (65% of the storm); a culvert within 100 m is overtopped |
| 15 | 0.44 | (unnamed) | Sutton | 0.28 m of water at peak; worst hour 50 mm (90% of the storm); a culvert within 100 m is overtopped |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
