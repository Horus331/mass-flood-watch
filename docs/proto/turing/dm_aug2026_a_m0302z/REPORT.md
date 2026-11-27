# Road-closure prototype: aug2026_proto_dm_aug2026_a_m0302z

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on GPU (cuda)), 20 m grid, storm from 2026-08-03T02:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 45,099 |
| Expected closures (sum of probabilities) | 646.6 |
| Segments with closure probability >= 50% | 390 (265.7 km) |
| Further segments that may close (stream reaches the road crest) | 567 (334.8 km) |
| Culverts overtopped / surcharged | 1075 / 19 of 10736 |
| Road segments cut off from hospitals | 4229 |
| Worst added trip time to a hospital | 47.6 min |
| Heaviest hour of rain | 35.7 mm |
| Flood model run time | 193 s |

## Checks against what happened

- Storm-day flood reports in the area: 3; water >= 10 cm within 100 m of 67% of them, vs 51% of random points (any day).
- Segments flagged impassable are 0.0x as likely as an average segment to have a report within 200 m.
- MassDOT repeating flood sites in the area: 30; 7 have a segment within 150 m at P >= 0.5 (share of all segments at P >= 0.5: 0.9%).

## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 1.00 | (unnamed) | Framingham | 1.95 m of water at peak; over 30 cm for 5.0 h; 30 cm reached 15.5 h into the storm; worst hour 20 mm (20% of the storm); water beside the road 1.68 m above its crest (design freeboard 0.30 m; P 1.00); road sag 2.9 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 20 mm; catchment 15.3 ha) (P 1.00) |
| 2 | 1.00 | (unnamed) | Worcester | 1.00 m of water at peak; over 30 cm for 3.5 h; 30 cm reached 17.0 h into the storm; worst hour 22 mm (21% of the storm); water beside the road 0.88 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.7 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 22 mm; catchment 77.2 ha) (P 1.00) |
| 3 | 1.00 | Martin Luther King Jr Boulevard | Worcester | 1.19 m of water at peak; over 30 cm for 8.5 h; 30 cm reached 12.0 h into the storm; worst hour 21 mm (20% of the storm); water beside the road 1.28 m above its crest (design freeboard 0.30 m; P 1.00); road sag 3.2 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 21 mm; catchment 60.2 ha) (P 1.00); a culvert within 100 m is overtopped |
| 4 | 1.00 | Shrewsbury Street | Worcester | 1.07 m of water at peak; over 30 cm for 6.5 h; 30 cm reached 14.0 h into the storm; worst hour 21 mm (21% of the storm); water beside the road 0.99 m above its crest (design freeboard 0.30 m; P 1.00); fast water: depth x speed 0.23 m2/s (small cars unstable from 0.3); road sag 0.8 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 21 mm; catchment 127.8 ha) (P 1.00) |
| 5 | 1.00 | Gilboa Street | Douglas | 0.72 m of water at peak; over 30 cm for 12.0 h; 30 cm reached 6.5 h into the storm; worst hour 25 mm (24% of the storm); water beside the road 0.49 m below its crest (design freeboard 0.30 m; P 0.11); a culvert within 100 m is overtopped |
| 6 | 1.00 | Shrewsbury Street | Worcester | 0.97 m of water at peak; over 30 cm for 5.0 h; 30 cm reached 15.5 h into the storm; worst hour 21 mm (21% of the storm); water beside the road 0.88 m above its crest (design freeboard 0.30 m; P 1.00); fast water: depth x speed 0.20 m2/s (small cars unstable from 0.3); road sag 0.8 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 21 mm; catchment 127.8 ha) (P 1.00) |
| 7 | 1.00 | Cambridge Street | Worcester | 1.63 m of water at peak; over 30 cm for 5.5 h; 30 cm reached 15.0 h into the storm; worst hour 22 mm (21% of the storm); water beside the road 1.49 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.7 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 22 mm; catchment 77.2 ha) (P 1.00) |
| 8 | 1.00 | Boundary Street | Marlborough | 0.85 m of water at peak; over 30 cm for 20.0 h; 30 cm reached 0.5 h into the storm; worst hour 20 mm (20% of the storm) |
| 9 | 1.00 | Route 131 | Southbridge | 0.88 m of water at peak; over 30 cm for 3.5 h; 30 cm reached 17.0 h into the storm; worst hour 23 mm (20% of the storm); a culvert within 100 m is overtopped |
| 10 | 1.00 | Southbridge Street | Worcester | 1.11 m of water at peak; over 30 cm for 4.0 h; 30 cm reached 16.5 h into the storm; worst hour 22 mm (21% of the storm); water beside the road 1.05 m above its crest (design freeboard 0.30 m; P 1.00); road sag 1.2 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 22 mm; catchment 13.4 ha) (P 1.00) |
| 11 | 1.00 | Route 131 | Southbridge | 1.03 m of water at peak; over 30 cm for 3.5 h; 30 cm reached 17.0 h into the storm; worst hour 23 mm (20% of the storm); water beside the road 0.02 m above its crest (design freeboard 0.30 m; P 0.98); a culvert within 100 m is overtopped |
| 12 | 1.00 | Route 169 | Charlton | 0.63 m of water at peak; over 30 cm for 7.0 h; 30 cm reached 13.5 h into the storm; worst hour 23 mm (20% of the storm); overtopping at 2.5 m/s at a stream crossing (grass-covered fill erodes from ~1.5 m/s); runoff beside / along the road at 0.5 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.17); a culvert within 100 m is overtopped |
| 13 | 1.00 | Route 12 | Auburn | 0.64 m of water at peak; over 30 cm for 4.0 h; 30 cm reached 16.5 h into the storm; worst hour 24 mm (22% of the storm) |
| 14 | 1.00 | Millbury Street | Grafton | 0.85 m of water at peak; over 30 cm for 8.5 h; 30 cm reached 12.0 h into the storm; worst hour 23 mm (22% of the storm) |
| 15 | 1.00 | Auburn Street | Auburn | 0.83 m of water at peak; over 30 cm for 4.0 h; 30 cm reached 16.5 h into the storm; worst hour 24 mm (22% of the storm); water beside the road 0.34 m above its crest (design freeboard 0.30 m; P 1.00) |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
