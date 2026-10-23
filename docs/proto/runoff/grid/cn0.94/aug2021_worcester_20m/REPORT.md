# Road-closure prototype: aug2021_loss_aug2021_worcester_20m

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on CPU (OpenMP)), 20 m grid, storm from 2021-08-19T09:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 8,566 |
| Expected closures (sum of probabilities) | 212.5 |
| Segments with closure probability >= 50% | 159 (95.6 km) |
| Further segments that may close (stream reaches the road crest) | 229 (115.4 km) |
| Culverts overtopped / surcharged | 251 / 4 of 1347 |
| Road segments cut off from hospitals | 1046 |
| Worst added trip time to a hospital | 26.8 min |
| Heaviest hour of rain | 89.6 mm |
| Flood model run time | 1251 s |

## Checks against what happened

- Storm-day flood reports in the area: 5; water >= 10 cm within 100 m of 60% of them, vs 62% of random points (any day).
- Segments flagged impassable are 1.8x as likely as an average segment to have a report within 200 m.
- MassDOT repeating flood sites in the area: 10; 4 have a segment within 150 m at P >= 0.5 (share of all segments at P >= 0.5: 1.9%).

## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 1.00 | Martin Luther King Jr Boulevard | Worcester | 3.81 m of water at peak; over 30 cm for 17.5 h; 30 cm reached 1.0 h into the storm; worst hour 24 mm (43% of the storm); water beside the road 3.73 m above its crest (design freeboard 0.30 m; P 1.00); fast water: depth x speed 0.31 m2/s (small cars unstable from 0.3); runoff beside / along the road at 1.3 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.72); road sag 3.2 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 24 mm; catchment 60.2 ha) (P 1.00); a culvert within 100 m is overtopped |
| 2 | 1.00 | Martin Luther King Jr Boulevard | Worcester | 3.11 m of water at peak; over 30 cm for 17.5 h; 30 cm reached 1.0 h into the storm; worst hour 24 mm (43% of the storm); water beside the road 2.79 m above its crest (design freeboard 0.30 m; P 1.00); fast water: depth x speed 0.29 m2/s (small cars unstable from 0.3); runoff beside / along the road at 2.5 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.96); road sag 3.2 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 24 mm; catchment 60.2 ha) (P 1.00); a culvert within 100 m is overtopped |
| 3 | 1.00 | Shrewsbury Street | Worcester | 0.69 m of water at peak; over 30 cm for 12.5 h; 30 cm reached 6.0 h into the storm; worst hour 24 mm (44% of the storm); water beside the road 0.61 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.9 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 23 mm; catchment 127.8 ha) (P 1.00) |
| 4 | 1.00 | Foster Street | Worcester | 2.09 m of water at peak; over 30 cm for 13.0 h; 30 cm reached 5.5 h into the storm; worst hour 25 mm (44% of the storm); water beside the road 0.10 m above its crest (design freeboard 0.30 m; P 1.00); road sag 1.2 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 25 mm; catchment 22.1 ha) (P 0.53); a culvert within 100 m is overtopped |
| 5 | 1.00 | Major Taylor Boulevard | Worcester | 1.22 m of water at peak; over 30 cm for 12.0 h; 30 cm reached 6.5 h into the storm; worst hour 25 mm (44% of the storm); water beside the road 0.98 m above its crest (design freeboard 0.30 m; P 1.00); road sag 1.1 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 24 mm; catchment 60.2 ha) (P 1.00); a culvert within 100 m is overtopped |
| 6 | 1.00 | Foster Street | Worcester | 2.09 m of water at peak; over 30 cm for 13.0 h; 30 cm reached 5.5 h into the storm; worst hour 25 mm (44% of the storm); water beside the road 0.11 m above its crest (design freeboard 0.30 m; P 1.00); road sag 1.2 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 25 mm; catchment 22.1 ha) (P 0.53); a culvert within 100 m is overtopped |
| 7 | 1.00 | Martin Luther King Jr Boulevard | Worcester | 0.78 m of water at peak; over 30 cm for 9.5 h; 30 cm reached 9.0 h into the storm; worst hour 24 mm (43% of the storm); water beside the road 0.61 m above its crest (design freeboard 0.30 m; P 1.00); a culvert within 100 m is overtopped |
| 8 | 1.00 | Major Taylor Boulevard | Worcester | 1.22 m of water at peak; over 30 cm for 12.0 h; 30 cm reached 6.5 h into the storm; worst hour 25 mm (44% of the storm); water beside the road 0.98 m above its crest (design freeboard 0.30 m; P 1.00); road sag 1.1 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 24 mm; catchment 60.2 ha) (P 1.00); a culvert within 100 m is overtopped |
| 9 | 1.00 | Cambridge Street | Worcester | 0.70 m of water at peak; over 30 cm for 10.5 h; 30 cm reached 8.0 h into the storm; worst hour 29 mm (48% of the storm); water beside the road 0.55 m above its crest (design freeboard 0.30 m; P 1.00); road sag 2.0 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 28 mm; catchment 77.2 ha) (P 1.00) |
| 10 | 1.00 | Route 122 | Northbridge | 2.08 m of water at peak; over 30 cm for 18.0 h; 30 cm reached 0.5 h into the storm; worst hour 70 mm (68% of the storm); a culvert within 100 m is overtopped |
| 11 | 1.00 | Providence Street | Millbury | 1.37 m of water at peak; over 30 cm for 14.0 h; 30 cm reached 4.5 h into the storm; worst hour 49 mm (54% of the storm); a culvert within 100 m is overtopped |
| 12 | 1.00 | Route 12 | Auburn | 0.67 m of water at peak; over 30 cm for 10.0 h; 30 cm reached 8.5 h into the storm; worst hour 34 mm (48% of the storm) |
| 13 | 1.00 | Auburn Street | Auburn | 0.92 m of water at peak; over 30 cm for 10.0 h; 30 cm reached 8.5 h into the storm; worst hour 31 mm (48% of the storm); water beside the road 0.29 m below its crest (design freeboard 0.30 m; P 0.54); runoff beside / along the road at 0.4 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.10) |
| 14 | 1.00 | Route 146 | Sutton | 0.66 m of water at peak; over 30 cm for 2.5 h; 30 cm reached 6.0 h into the storm; worst hour 72 mm (72% of the storm); water beside the road 0.17 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 0.9 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.41); a culvert within 100 m is overtopped |
| 15 | 1.00 | Millbury Street | Grafton | 0.71 m of water at peak; over 30 cm for 12.5 h; 30 cm reached 6.0 h into the storm; worst hour 31 mm (56% of the storm) |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
