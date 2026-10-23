# Road-closure prototype: sep2021_loss_sep2021_cnrep

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on CPU (OpenMP)), 20 m grid, storm from 2021-09-01T18:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 7,585 |
| Expected closures (sum of probabilities) | 321.0 |
| Segments with closure probability >= 50% | 278 (137.6 km) |
| Further segments that may close (stream reaches the road crest) | 236 (115.5 km) |
| Culverts overtopped / surcharged | 230 / 3 of 1074 |
| Road segments cut off from hospitals | 978 |
| Worst added trip time to a hospital | 36.5 min |
| Heaviest hour of rain | 21.5 mm |
| Flood model run time | 1095 s |

## Checks against what happened

- Storm-day flood reports in the area: 4; water >= 10 cm within 100 m of 50% of them, vs 69% of random points (any day).
- Segments flagged impassable are 1.85x as likely as an average segment to have a report within 200 m.
- MassDOT repeating flood sites in the area: 7; 3 have a segment within 150 m at P >= 0.5 (share of all segments at P >= 0.5: 3.7%).

## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 1.00 | I-190 | Worcester | 0.69 m of water at peak; over 30 cm for 12.0 h; 30 cm reached 12.5 h into the storm; worst hour 18 mm (17% of the storm); water beside the road 0.69 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 0.8 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.26); road sag 1.7 m deep (underpass, drains sized for the 50-yr hour, 58 mm; peak hour here 18 mm; catchment 52.2 ha) (P 1.00) |
| 2 | 1.00 | Martin Luther King Jr Boulevard | Worcester | 4.70 m of water at peak; over 30 cm for 23.5 h; 30 cm reached 1.0 h into the storm; worst hour 19 mm (18% of the storm); water beside the road 4.62 m above its crest (design freeboard 0.30 m; P 1.00); fast water: depth x speed 0.49 m2/s (small cars unstable from 0.3); runoff beside / along the road at 2.1 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.95); road sag 3.2 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 19 mm; catchment 60.2 ha) (P 1.00); a culvert within 100 m is overtopped |
| 3 | 1.00 | Martin Luther King Jr Boulevard | Worcester | 4.00 m of water at peak; over 30 cm for 23.5 h; 30 cm reached 1.0 h into the storm; worst hour 19 mm (18% of the storm); water beside the road 3.67 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 4.5 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.94); road sag 3.2 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 19 mm; catchment 60.2 ha) (P 1.00); a culvert within 100 m is overtopped |
| 4 | 1.00 | Route 70 | Worcester | 0.73 m of water at peak; over 30 cm for 12.5 h; 30 cm reached 12.0 h into the storm; worst hour 19 mm (18% of the storm); a culvert within 100 m is overtopped |
| 5 | 1.00 | Route 70 | Worcester | 0.73 m of water at peak; over 30 cm for 12.5 h; 30 cm reached 12.0 h into the storm; worst hour 19 mm (18% of the storm); runoff beside / along the road at 4.7 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.98); a culvert within 100 m is overtopped |
| 6 | 1.00 | Shrewsbury Street | Worcester | 1.38 m of water at peak; over 30 cm for 13.0 h; 30 cm reached 11.5 h into the storm; worst hour 19 mm (18% of the storm); water beside the road 1.29 m above its crest (design freeboard 0.30 m; P 1.00); fast water: depth x speed 0.22 m2/s (small cars unstable from 0.3); runoff beside / along the road at 2.9 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.13); road sag 0.8 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 19 mm; catchment 127.8 ha) (P 1.00) |
| 7 | 1.00 | Shrewsbury Street | Worcester | 1.48 m of water at peak; over 30 cm for 14.0 h; 30 cm reached 10.5 h into the storm; worst hour 19 mm (18% of the storm); water beside the road 1.40 m above its crest (design freeboard 0.30 m; P 1.00); fast water: depth x speed 0.25 m2/s (small cars unstable from 0.3); runoff beside / along the road at 2.6 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.13); road sag 0.8 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 19 mm; catchment 127.8 ha) (P 1.00) |
| 8 | 1.00 | Route 9 | Worcester | 0.71 m of water at peak; over 30 cm for 12.5 h; 30 cm reached 12.0 h into the storm; worst hour 19 mm (18% of the storm); a culvert within 100 m is overtopped |
| 9 | 1.00 | Foster Street | Worcester | 2.95 m of water at peak; over 30 cm for 15.5 h; 30 cm reached 9.0 h into the storm; worst hour 19 mm (18% of the storm); water beside the road 0.96 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 3.2 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.87); road sag 1.2 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 19 mm; catchment 22.1 ha) (P 1.00); a culvert within 100 m is overtopped |
| 10 | 1.00 | Foster Street | Worcester | 2.95 m of water at peak; over 30 cm for 15.5 h; 30 cm reached 9.0 h into the storm; worst hour 19 mm (18% of the storm); water beside the road 0.98 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 2.1 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.55); road sag 1.2 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 19 mm; catchment 22.1 ha) (P 1.00); a culvert within 100 m is overtopped |
| 11 | 1.00 | Martin Luther King Jr Boulevard | Worcester | 1.66 m of water at peak; over 30 cm for 11.0 h; 30 cm reached 13.5 h into the storm; worst hour 19 mm (18% of the storm); water beside the road 1.49 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 1.4 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.37); a culvert within 100 m is overtopped |
| 12 | 1.00 | Stafford Street | Worcester | 0.83 m of water at peak; over 30 cm for 14.0 h; 30 cm reached 10.5 h into the storm; worst hour 16 mm (16% of the storm); water beside the road 0.59 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 0.7 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.23); a culvert within 100 m is overtopped |
| 13 | 1.00 | Thomas Street | Worcester | 1.49 m of water at peak; over 30 cm for 11.0 h; 30 cm reached 13.5 h into the storm; worst hour 19 mm (18% of the storm); water beside the road 1.46 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 0.9 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.20); road sag 0.5 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 19 mm; catchment 60.2 ha) (P 1.00); a culvert within 100 m is overtopped |
| 14 | 1.00 | Major Taylor Boulevard | Worcester | 2.10 m of water at peak; over 30 cm for 12.5 h; 30 cm reached 12.0 h into the storm; worst hour 19 mm (18% of the storm); water beside the road 1.86 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 1.7 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.58); road sag 1.1 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 19 mm; catchment 60.2 ha) (P 1.00); a culvert within 100 m is overtopped |
| 15 | 1.00 | Major Taylor Boulevard | Worcester | 2.10 m of water at peak; over 30 cm for 12.5 h; 30 cm reached 12.0 h into the storm; worst hour 19 mm (18% of the storm); water beside the road 1.86 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 1.1 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.58); road sag 1.1 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 19 mm; catchment 60.2 ha) (P 1.00); a culvert within 100 m is overtopped |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
