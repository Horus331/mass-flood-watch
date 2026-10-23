# Road-closure prototype: aug2021_rain_aug2021_gauge_dt5

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on CPU (OpenMP)), 20 m grid, storm from 2021-08-19T09:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 8,566 |
| Expected closures (sum of probabilities) | 366.4 |
| Segments with closure probability >= 50% | 283 (166.3 km) |
| Further segments that may close (stream reaches the road crest) | 380 (184.2 km) |
| Culverts overtopped / surcharged | 339 / 7 of 1347 |
| Road segments cut off from hospitals | 1872 |
| Worst added trip time to a hospital | 26.4 min |
| Heaviest hour of rain | 92.7 mm |
| Flood model run time | 1275 s |

## Checks against what happened

- Storm-day flood reports in the area: 5; water >= 10 cm within 100 m of 60% of them, vs 68% of random points (any day).
- Segments flagged impassable are 2.3x as likely as an average segment to have a report within 200 m.
- MassDOT repeating flood sites in the area: 10; 5 have a segment within 150 m at P >= 0.5 (share of all segments at P >= 0.5: 3.3%).

## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 1.00 | Martin Luther King Jr Boulevard | Worcester | 4.10 m of water at peak; over 30 cm for 17.5 h; 30 cm reached 1.0 h into the storm; worst hour 32 mm (43% of the storm); water beside the road 4.02 m above its crest (design freeboard 0.30 m; P 1.00); fast water: depth x speed 0.43 m2/s (small cars unstable from 0.3); runoff beside / along the road at 0.6 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.17); road sag 3.2 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 32 mm; catchment 60.2 ha) (P 1.00); a culvert within 100 m is overtopped |
| 2 | 1.00 | Martin Luther King Jr Boulevard | Worcester | 3.40 m of water at peak; over 30 cm for 17.5 h; 30 cm reached 1.0 h into the storm; worst hour 32 mm (43% of the storm); water beside the road 3.08 m above its crest (design freeboard 0.30 m; P 1.00); fast water: depth x speed 0.38 m2/s (small cars unstable from 0.3); runoff beside / along the road at 2.5 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.98); road sag 3.2 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 32 mm; catchment 60.2 ha) (P 1.00); a culvert within 100 m is overtopped |
| 3 | 1.00 | Route 70 | Worcester | 0.64 m of water at peak; over 30 cm for 9.5 h; 30 cm reached 6.0 h into the storm; worst hour 33 mm (44% of the storm); runoff beside / along the road at 1.9 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.55); a culvert within 100 m is overtopped |
| 4 | 1.00 | Shrewsbury Street | Worcester | 0.82 m of water at peak; over 30 cm for 12.5 h; 30 cm reached 6.0 h into the storm; worst hour 30 mm (44% of the storm); water beside the road 0.73 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.9 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 30 mm; catchment 127.8 ha) (P 1.00) |
| 5 | 1.00 | Route 70 | Worcester | 0.64 m of water at peak; over 30 cm for 9.5 h; 30 cm reached 6.0 h into the storm; worst hour 33 mm (44% of the storm); runoff beside / along the road at 2.1 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.61); a culvert within 100 m is overtopped |
| 6 | 1.00 | Shrewsbury Street | Worcester | 0.92 m of water at peak; over 30 cm for 12.5 h; 30 cm reached 6.0 h into the storm; worst hour 30 mm (44% of the storm); water beside the road 0.84 m above its crest (design freeboard 0.30 m; P 1.00); fast water: depth x speed 0.23 m2/s (small cars unstable from 0.3); road sag 0.9 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 30 mm; catchment 127.8 ha) (P 1.00) |
| 7 | 1.00 | Martin Luther King Jr Boulevard | Worcester | 1.07 m of water at peak; over 30 cm for 11.0 h; 30 cm reached 7.5 h into the storm; worst hour 33 mm (43% of the storm); water beside the road 0.90 m above its crest (design freeboard 0.30 m; P 1.00); a culvert within 100 m is overtopped |
| 8 | 1.00 | Foster Street | Worcester | 2.37 m of water at peak; over 30 cm for 13.0 h; 30 cm reached 5.5 h into the storm; worst hour 32 mm (44% of the storm); water beside the road 0.39 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 1.7 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.60); road sag 1.2 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 32 mm; catchment 22.1 ha) (P 1.00); a culvert within 100 m is overtopped |
| 9 | 1.00 | Thomas Street | Worcester | 0.90 m of water at peak; over 30 cm for 11.0 h; 30 cm reached 7.5 h into the storm; worst hour 33 mm (43% of the storm); water beside the road 0.86 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.5 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 33 mm; catchment 60.2 ha) (P 1.00); a culvert within 100 m is overtopped |
| 10 | 1.00 | Major Taylor Boulevard | Worcester | 1.51 m of water at peak; over 30 cm for 12.5 h; 30 cm reached 6.0 h into the storm; worst hour 33 mm (44% of the storm); water beside the road 1.27 m above its crest (design freeboard 0.30 m; P 1.00); road sag 1.1 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 32 mm; catchment 60.2 ha) (P 1.00); a culvert within 100 m is overtopped |
| 11 | 1.00 | Major Taylor Boulevard | Worcester | 1.51 m of water at peak; over 30 cm for 12.5 h; 30 cm reached 6.0 h into the storm; worst hour 33 mm (44% of the storm); water beside the road 1.27 m above its crest (design freeboard 0.30 m; P 1.00); road sag 1.1 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 32 mm; catchment 60.2 ha) (P 1.00); a culvert within 100 m is overtopped |
| 12 | 1.00 | Foster Street | Worcester | 2.37 m of water at peak; over 30 cm for 13.0 h; 30 cm reached 5.5 h into the storm; worst hour 32 mm (44% of the storm); water beside the road 0.40 m above its crest (design freeboard 0.30 m; P 1.00); road sag 1.2 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 32 mm; catchment 22.1 ha) (P 1.00); a culvert within 100 m is overtopped |
| 13 | 1.00 | Southbridge Street | Worcester | 0.77 m of water at peak; over 30 cm for 11.5 h; 30 cm reached 7.0 h into the storm; worst hour 38 mm (48% of the storm); water beside the road 0.70 m above its crest (design freeboard 0.30 m; P 1.00); road sag 1.2 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 37 mm; catchment 13.4 ha) (P 1.00); a culvert within 100 m is overtopped |
| 14 | 1.00 | Major Taylor Boulevard | Worcester | 0.74 m of water at peak; over 30 cm for 11.5 h; 30 cm reached 7.0 h into the storm; worst hour 33 mm (44% of the storm); water beside the road 0.26 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.8 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 33 mm; catchment 60.2 ha) (P 0.49); a culvert within 100 m is overtopped |
| 15 | 1.00 | Cambridge Street | Worcester | 1.12 m of water at peak; over 30 cm for 12.0 h; 30 cm reached 6.5 h into the storm; worst hour 39 mm (48% of the storm); water beside the road 0.97 m above its crest (design freeboard 0.30 m; P 1.00); road sag 2.0 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 36 mm; catchment 77.2 ha) (P 1.00) |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
