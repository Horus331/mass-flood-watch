# Road-closure prototype: sep2021_loss_sep2021_worcester_20m

Flood model: LISFLOOD-FP 8.3 (acceleration (local inertial, Bates et al. 2010) on CPU (OpenMP)), 20 m grid, storm from 2021-09-01T18:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 7,775 |
| Expected closures (sum of probabilities) | 413.5 |
| Segments with closure probability >= 50% | 369 (180.1 km) |
| Further segments that may close (stream reaches the road crest) | 298 (150.8 km) |
| Culverts overtopped / surcharged | 299 / 3 of 1074 |
| Road segments cut off from hospitals | 1596 |
| Worst added trip time to a hospital | 37.5 min |
| Heaviest hour of rain | 21.5 mm |
| Flood model run time | 2717 s |

## Checks against what happened

- Storm-day flood reports in the area: 4; water >= 10 cm within 100 m of 50% of them, vs 72% of random points (any day).
- Segments flagged impassable are 1.96x as likely as an average segment to have a report within 200 m.
- MassDOT repeating flood sites in the area: 7; 4 have a segment within 150 m at P >= 0.5 (share of all segments at P >= 0.5: 4.7%).

## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 1.00 | (unnamed) | Worcester | 1.18 m of water at peak; over 30 cm for 12.0 h; 30 cm reached 12.5 h into the storm; worst hour 20 mm (18% of the storm); water beside the road 1.06 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 1.2 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.64); road sag 0.7 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 19 mm; catchment 77.2 ha) (P 1.00) |
| 2 | 1.00 | I-190 | Worcester | 1.12 m of water at peak; over 30 cm for 14.0 h; 30 cm reached 10.5 h into the storm; worst hour 18 mm (17% of the storm); water beside the road 1.12 m above its crest (design freeboard 0.30 m; P 1.00); road sag 1.7 m deep (underpass, drains sized for the 50-yr hour, 58 mm; peak hour here 18 mm; catchment 52.2 ha) (P 1.00); a culvert within 100 m is overtopped |
| 3 | 1.00 | I-290 | Shrewsbury | 0.65 m of water at peak; over 30 cm for 12.0 h; 30 cm reached 12.5 h into the storm; worst hour 19 mm (19% of the storm); water beside the road 0.65 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 2.0 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.41) |
| 4 | 1.00 | Route 146 | Worcester | 1.19 m of water at peak; over 30 cm for 11.5 h; 30 cm reached 13.0 h into the storm; worst hour 20 mm (19% of the storm); runoff beside / along the road at 0.9 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.12); a culvert within 100 m is overtopped |
| 5 | 1.00 | Martin Luther King Jr Boulevard | Worcester | 5.26 m of water at peak; over 30 cm for 23.5 h; 30 cm reached 1.0 h into the storm; worst hour 19 mm (18% of the storm); water beside the road 5.18 m above its crest (design freeboard 0.30 m; P 1.00); fast water: depth x speed 0.46 m2/s (small cars unstable from 0.3); runoff beside / along the road at 1.1 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.57); road sag 3.2 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 19 mm; catchment 60.2 ha) (P 1.00); a culvert within 100 m is overtopped |
| 6 | 1.00 | Route 70 | Worcester | 1.01 m of water at peak; over 30 cm for 14.5 h; 30 cm reached 10.0 h into the storm; worst hour 19 mm (18% of the storm); runoff beside / along the road at 2.1 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.25); a culvert within 100 m is overtopped |
| 7 | 1.00 | Martin Luther King Jr Boulevard | Worcester | 4.56 m of water at peak; over 30 cm for 23.5 h; 30 cm reached 1.0 h into the storm; worst hour 19 mm (18% of the storm); water beside the road 4.23 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 2.2 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.96); road sag 3.2 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 19 mm; catchment 60.2 ha) (P 1.00); a culvert within 100 m is overtopped |
| 8 | 1.00 | Route 70 | Worcester | 1.01 m of water at peak; over 30 cm for 14.5 h; 30 cm reached 10.0 h into the storm; worst hour 19 mm (18% of the storm); runoff beside / along the road at 2.3 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.85); a culvert within 100 m is overtopped |
| 9 | 1.00 | Route 9 | Worcester | 0.65 m of water at peak; over 30 cm for 11.0 h; 30 cm reached 13.5 h into the storm; worst hour 19 mm (20% of the storm); water beside the road 0.65 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 1.4 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.32) |
| 10 | 1.00 | Route 9 | Worcester | 0.65 m of water at peak; over 30 cm for 11.0 h; 30 cm reached 13.5 h into the storm; worst hour 19 mm (20% of the storm); water beside the road 0.65 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 1.4 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.44) |
| 11 | 1.00 | Shrewsbury Street | Worcester | 1.94 m of water at peak; over 30 cm for 15.5 h; 30 cm reached 9.0 h into the storm; worst hour 19 mm (18% of the storm); water beside the road 1.86 m above its crest (design freeboard 0.30 m; P 1.00); fast water: depth x speed 0.30 m2/s (small cars unstable from 0.3); runoff beside / along the road at 1.5 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.15); road sag 0.8 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 19 mm; catchment 127.8 ha) (P 1.00) |
| 12 | 1.00 | Route 9 | Worcester | 0.98 m of water at peak; over 30 cm for 14.5 h; 30 cm reached 10.0 h into the storm; worst hour 19 mm (18% of the storm); a culvert within 100 m is overtopped |
| 13 | 1.00 | Shrewsbury Street | Worcester | 2.04 m of water at peak; over 30 cm for 16.0 h; 30 cm reached 8.5 h into the storm; worst hour 19 mm (18% of the storm); water beside the road 1.96 m above its crest (design freeboard 0.30 m; P 1.00); fast water: depth x speed 0.34 m2/s (small cars unstable from 0.3); runoff beside / along the road at 1.4 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.15); road sag 0.8 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 19 mm; catchment 127.8 ha) (P 1.00) |
| 14 | 1.00 | Foster Street | Worcester | 3.49 m of water at peak; over 30 cm for 18.0 h; 30 cm reached 6.5 h into the storm; worst hour 19 mm (18% of the storm); water beside the road 1.51 m above its crest (design freeboard 0.30 m; P 1.00); fast water: depth x speed 0.27 m2/s (small cars unstable from 0.3); runoff beside / along the road at 1.7 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.86); road sag 1.2 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 19 mm; catchment 22.1 ha) (P 1.00); a culvert within 100 m is overtopped |
| 15 | 1.00 | Foster Street | Worcester | 3.49 m of water at peak; over 30 cm for 18.0 h; 30 cm reached 6.5 h into the storm; worst hour 19 mm (18% of the storm); water beside the road 1.53 m above its crest (design freeboard 0.30 m; P 1.00); fast water: depth x speed 0.29 m2/s (small cars unstable from 0.3); runoff beside / along the road at 0.8 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.24); road sag 1.2 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 19 mm; catchment 22.1 ha) (P 1.00); a culvert within 100 m is overtopped |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
