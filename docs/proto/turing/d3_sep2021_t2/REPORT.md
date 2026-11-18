# Road-closure prototype: sep2021_proto_d3_sep2021_t2

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on GPU (cuda)), 20 m grid, storm from 2021-09-01T18:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 45,099 |
| Expected closures (sum of probabilities) | 647.1 |
| Segments with closure probability >= 50% | 371 (259.1 km) |
| Further segments that may close (stream reaches the road crest) | 530 (315.6 km) |
| Culverts overtopped / surcharged | 1048 / 21 of 10736 |
| Road segments cut off from hospitals | 3861 |
| Worst added trip time to a hospital | 33.3 min |
| Heaviest hour of rain | 24.5 mm |
| Flood model run time | 714 s |

## Checks against what happened

- Storm-day flood reports in the area: 10; water >= 10 cm within 100 m of 50% of them, vs 55% of random points (any day).
- Segments flagged impassable are 2.12x as likely as an average segment to have a report within 200 m.
- MassDOT repeating flood sites in the area: 30; 8 have a segment within 150 m at P >= 0.5 (share of all segments at P >= 0.5: 0.8%).

## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 1.00 | (unnamed) | Framingham | 1.93 m of water at peak; over 30 cm for 36.5 h; 30 cm reached 12.0 h into the storm; worst hour 19 mm (19% of the storm); water beside the road 1.66 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 0.8 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.13); road sag 2.9 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 19 mm; catchment 15.3 ha) (P 1.00) |
| 2 | 1.00 | (unnamed) | Worcester | 1.03 m of water at peak; over 30 cm for 15.5 h; 30 cm reached 13.5 h into the storm; worst hour 20 mm (18% of the storm); water beside the road 0.91 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.7 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 19 mm; catchment 77.2 ha) (P 1.00) |
| 3 | 1.00 | Shrewsbury Street | Worcester | 0.98 m of water at peak; over 30 cm for 36.5 h; 30 cm reached 12.0 h into the storm; worst hour 19 mm (18% of the storm); water beside the road 0.90 m above its crest (design freeboard 0.30 m; P 1.00); fast water: depth x speed 0.19 m2/s (small cars unstable from 0.3); road sag 0.8 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 19 mm; catchment 127.8 ha) (P 1.00) |
| 4 | 1.00 | Shrewsbury Street | Worcester | 1.09 m of water at peak; over 30 cm for 37.0 h; 30 cm reached 11.5 h into the storm; worst hour 19 mm (18% of the storm); water beside the road 1.00 m above its crest (design freeboard 0.30 m; P 1.00); fast water: depth x speed 0.23 m2/s (small cars unstable from 0.3); road sag 0.8 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 19 mm; catchment 127.8 ha) (P 1.00) |
| 5 | 1.00 | Martin Luther King Jr Boulevard | Worcester | 1.30 m of water at peak; over 30 cm for 38.0 h; 30 cm reached 10.5 h into the storm; worst hour 19 mm (18% of the storm); water beside the road 1.37 m above its crest (design freeboard 0.30 m; P 1.00); road sag 3.2 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 19 mm; catchment 60.2 ha) (P 1.00); a culvert within 100 m is overtopped |
| 6 | 1.00 | Route 117 | Lancaster | 1.68 m of water at peak; over 30 cm for 48.0 h; 30 cm reached 0.5 h into the storm; worst hour 16 mm (16% of the storm); culvert (Trib to Still River): headwater 10.21 m vs road crest 2.74 m, 43.2 m3/s |
| 7 | 1.00 | Cambridge Street | Worcester | 1.66 m of water at peak; over 30 cm for 36.5 h; 30 cm reached 12.0 h into the storm; worst hour 19 mm (18% of the storm); water beside the road 1.51 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.7 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 19 mm; catchment 77.2 ha) (P 1.00) |
| 8 | 1.00 | Gilboa Street | Douglas | 0.86 m of water at peak; over 30 cm for 44.0 h; 30 cm reached 4.5 h into the storm; worst hour 20 mm (16% of the storm); water beside the road 0.49 m below its crest (design freeboard 0.30 m; P 0.11); a culvert within 100 m is overtopped |
| 9 | 1.00 | Southbridge Street | Worcester | 1.16 m of water at peak; over 30 cm for 22.0 h; 30 cm reached 13.0 h into the storm; worst hour 19 mm (18% of the storm); water beside the road 1.09 m above its crest (design freeboard 0.30 m; P 1.00); road sag 1.2 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 19 mm; catchment 13.4 ha) (P 1.00) |
| 10 | 1.00 | Route 12 | West Boylston | 0.64 m of water at peak; over 30 cm for 32.5 h; 30 cm reached 16.0 h into the storm; worst hour 18 mm (17% of the storm); water beside the road 0.66 m above its crest (design freeboard 0.30 m; P 1.00) |
| 11 | 1.00 | Depot Street | Fitchburg | 0.69 m of water at peak; over 30 cm for 40.0 h; 30 cm reached 0.5 h into the storm; worst hour 16 mm (18% of the storm); a culvert within 100 m is overtopped |
| 12 | 1.00 | (unnamed) | Leominster | 0.66 m of water at peak; over 30 cm for 14.0 h; 30 cm reached 13.0 h into the storm; worst hour 19 mm (18% of the storm); water beside the road 0.23 m below its crest (design freeboard 0.30 m; P 0.69); a culvert within 100 m is overtopped |
| 13 | 1.00 | Linwood Avenue | Northbridge | 0.64 m of water at peak; over 30 cm for 26.0 h; 30 cm reached 13.5 h into the storm; worst hour 19 mm (16% of the storm); a culvert within 100 m is overtopped |
| 14 | 1.00 | Boundary Street | Marlborough | 0.67 m of water at peak; over 30 cm for 48.0 h; 30 cm reached 0.5 h into the storm; worst hour 19 mm (19% of the storm); runoff beside / along the road at 0.7 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.12) |
| 15 | 1.00 | Auburn Street | Auburn | 0.75 m of water at peak; over 30 cm for 15.5 h; 30 cm reached 13.0 h into the storm; worst hour 20 mm (19% of the storm); water beside the road 0.46 m below its crest (design freeboard 0.30 m; P 0.14); runoff beside / along the road at 0.6 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.14) |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
