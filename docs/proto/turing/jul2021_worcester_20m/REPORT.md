# Road-closure prototype: jul2021_proto_jul2021_worcester_20m

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on GPU (cuda)), 20 m grid, storm from 2021-07-09T08:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 6,083 |
| Expected closures (sum of probabilities) | 105.6 |
| Segments with closure probability >= 50% | 74 (47.7 km) |
| Further segments that may close (stream reaches the road crest) | 105 (57.5 km) |
| Culverts overtopped / surcharged | 154 / 0 of 1161 |
| Road segments cut off from hospitals | 473 |
| Worst added trip time to a hospital | 18.6 min |
| Heaviest hour of rain | 19.5 mm |
| Flood model run time | 48 s |

## Checks against what happened

- Storm-day flood reports in the area: 1; water >= 10 cm within 100 m of 0% of them, vs 57% of random points (any day).
- Segments flagged impassable are 2.46x as likely as an average segment to have a report within 200 m.
- MassDOT repeating flood sites in the area: 4; 1 have a segment within 150 m at P >= 0.5 (share of all segments at P >= 0.5: 1.2%).

## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 1.00 | Martin Luther King Jr Boulevard | Worcester | 3.24 m of water at peak; over 30 cm for 18.0 h; 30 cm reached 0.5 h into the storm; worst hour 14 mm (27% of the storm); water beside the road 3.16 m above its crest (design freeboard 0.30 m; P 1.00); fast water: depth x speed 0.26 m2/s (small cars unstable from 0.3); road sag 3.2 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 14 mm; catchment 60.2 ha) (P 1.00); a culvert within 100 m is overtopped |
| 2 | 1.00 | Martin Luther King Jr Boulevard | Worcester | 2.54 m of water at peak; over 30 cm for 18.0 h; 30 cm reached 0.5 h into the storm; worst hour 14 mm (27% of the storm); water beside the road 2.22 m above its crest (design freeboard 0.30 m; P 1.00); road sag 3.2 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 14 mm; catchment 60.2 ha) (P 1.00); a culvert within 100 m is overtopped |
| 3 | 1.00 | Foster Street | Worcester | 1.51 m of water at peak; over 30 cm for 18.0 h; 30 cm reached 0.5 h into the storm; worst hour 14 mm (27% of the storm); water beside the road 0.03 m below its crest (design freeboard 0.30 m; P 0.96); runoff beside / along the road at 1.2 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.10); road sag 0.7 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 14 mm; catchment 22.1 ha) (P 0.80); a culvert within 100 m is overtopped |
| 4 | 1.00 | Foster Street | Worcester | 1.51 m of water at peak; over 30 cm for 18.0 h; 30 cm reached 0.5 h into the storm; worst hour 14 mm (27% of the storm); water beside the road 0.42 m above its crest (design freeboard 0.30 m; P 1.00); fast water: depth x speed 0.24 m2/s (small cars unstable from 0.3); runoff beside / along the road at 2.4 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.79); road sag 0.7 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 14 mm; catchment 22.1 ha) (P 0.80); a culvert within 100 m is overtopped |
| 5 | 1.00 | Stafford Street | Worcester | 1.23 m of water at peak; over 30 cm for 15.5 h; 30 cm reached 0.5 h into the storm; worst hour 14 mm (28% of the storm); water beside the road 0.16 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.4 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 14 mm; catchment 16.0 ha) (P 0.20); a culvert within 100 m is overtopped |
| 6 | 1.00 | Shrewsbury Street | Worcester | 0.73 m of water at peak; over 30 cm for 9.5 h; 30 cm reached 9.0 h into the storm; worst hour 14 mm (27% of the storm); water beside the road 0.65 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.9 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 14 mm; catchment 127.8 ha) (P 1.00) |
| 7 | 1.00 | James Street | Worcester | 0.72 m of water at peak; over 30 cm for 13.0 h; 30 cm reached 0.5 h into the storm; worst hour 14 mm (27% of the storm); a culvert within 100 m is overtopped |
| 8 | 1.00 | Major Taylor Boulevard | Worcester | 0.65 m of water at peak; over 30 cm for 8.5 h; 30 cm reached 10.0 h into the storm; worst hour 14 mm (27% of the storm); water beside the road 0.70 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 5.0 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 1.00); road sag 1.2 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 14 mm; catchment 60.2 ha) (P 0.95); a culvert within 100 m is overtopped |
| 9 | 1.00 | Ludlow Street | Worcester | 1.23 m of water at peak; over 30 cm for 16.0 h; 30 cm reached 0.5 h into the storm; worst hour 14 mm (28% of the storm); a culvert within 100 m is overtopped |
| 10 | 1.00 | (unnamed) | Worcester | 1.95 m of water at peak; over 30 cm for 16.5 h; 30 cm reached 2.0 h into the storm; worst hour 14 mm (27% of the storm); a culvert within 100 m is overtopped |
| 11 | 1.00 | East Park Terrace | Worcester | 0.95 m of water at peak; over 30 cm for 10.0 h; 30 cm reached 8.5 h into the storm; worst hour 14 mm (26% of the storm); water beside the road 0.85 m above its crest (design freeboard 0.30 m; P 1.00); road sag 4.3 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 14 mm; catchment 127.8 ha) (P 1.00) |
| 12 | 1.00 | (unnamed) | Oxford | 0.69 m of water at peak; over 30 cm for 6.5 h; 30 cm reached 12.0 h into the storm; worst hour 10 mm (22% of the storm); water beside the road 0.05 m below its crest (design freeboard 0.30 m; P 0.95); a culvert within 100 m is overtopped |
| 13 | 1.00 | A Young Road | Charlton | 0.95 m of water at peak; over 30 cm for 2.0 h; 30 cm reached 10.0 h into the storm; worst hour 12 mm (26% of the storm); water beside the road 0.73 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 3.1 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.60); a culvert within 100 m is overtopped |
| 14 | 1.00 | Wire Village Road | Spencer | 0.73 m of water at peak; over 30 cm for 0.5 h; 30 cm reached 0.5 h into the storm; worst hour 13 mm (30% of the storm); runoff beside / along the road at 3.5 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.70); a culvert within 100 m is overtopped |
| 15 | 1.00 | Hastings Road | Spencer | 0.70 m of water at peak; over 30 cm for 0.5 h; 30 cm reached 0.5 h into the storm; worst hour 12 mm (28% of the storm); a culvert within 100 m is overtopped |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
