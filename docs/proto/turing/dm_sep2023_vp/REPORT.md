# Road-closure prototype: sep2023_proto_dm_sep2023_vp

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on GPU (cuda)), 20 m grid, storm from 2023-09-11T18:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 45,099 |
| Expected closures (sum of probabilities) | 81.7 |
| Segments with closure probability >= 50% | 9 (6.7 km) |
| Further segments that may close (stream reaches the road crest) | 80 (57.0 km) |
| Culverts overtopped / surcharged | 30 / 5 of 10736 |
| Road segments cut off from hospitals | 107 |
| Worst added trip time to a hospital | 13.2 min |
| Heaviest hour of rain | 19.9 mm |
| Flood model run time | 414 s |

## Checks against what happened

- Storm-day flood reports in the area: 11; water >= 10 cm within 100 m of 0% of them, vs 6% of random points (any day).
- Segments flagged impassable are 0.0x as likely as an average segment to have a report within 200 m.
- MassDOT repeating flood sites in the area: 30; 1 have a segment within 150 m at P >= 0.5 (share of all segments at P >= 0.5: 0.0%).

## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 1.00 | Ash Street | Clinton | 1.39 m of water at peak; over 30 cm for 15.5 h; 30 cm reached 19.0 h into the storm; worst hour 10 mm (19% of the storm); water beside the road 1.18 m above its crest (design freeboard 0.30 m; P 1.00) |
| 2 | 1.00 | Ash Street | Clinton | 1.06 m of water at peak; over 30 cm for 12.0 h; 30 cm reached 22.5 h into the storm; worst hour 10 mm (19% of the storm); water beside the road 0.98 m above its crest (design freeboard 0.30 m; P 1.00) |
| 3 | 0.98 | Route 117 | Lancaster | 0.50 m of water at peak; over 30 cm for 34.0 h; 30 cm reached 0.5 h into the storm; worst hour 10 mm (23% of the storm) |
| 4 | 0.97 | East Park Terrace | Worcester | 0.49 m of water at peak; over 30 cm for 22.5 h; 30 cm reached 12.0 h into the storm; worst hour 9 mm (19% of the storm); water beside the road 0.39 m above its crest (design freeboard 0.30 m; P 1.00); road sag 4.3 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 9 mm; catchment 127.8 ha) (P 0.97) |
| 5 | 0.72 | Route 9 | Framingham | 0.36 m of water at peak; over 30 cm for 2.0 h; 30 cm reached 2.0 h into the storm; worst hour 7 mm (33% of the storm); a culvert within 100 m is overtopped |
| 6 | 0.72 | Route 9 | Framingham | 0.36 m of water at peak; over 30 cm for 2.0 h; 30 cm reached 2.0 h into the storm; worst hour 7 mm (33% of the storm); a culvert within 100 m is overtopped |
| 7 | 0.56 | (unnamed) | Berlin | 0.31 m of water at peak; over 30 cm for 0.5 h; 30 cm reached 0.5 h into the storm; worst hour 9 mm (18% of the storm); water beside the road 0.41 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 0.9 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.15) |
| 8 | 0.53 | Route 62 | Berlin | 0.31 m of water at peak; over 30 cm for 0.5 h; 30 cm reached 0.5 h into the storm; worst hour 9 mm (18% of the storm); runoff beside / along the road at 0.5 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.14) |
| 9 | 0.52 | Salem End Road | Framingham | 0.30 m of water at peak; over 30 cm for 1.5 h; 30 cm reached 2.5 h into the storm; worst hour 7 mm (33% of the storm); a culvert within 100 m is overtopped |
| 10 | 0.37 | Shrewsbury Street | Worcester | 0.27 m of water at peak; over 30 cm for 11.0 h; 30 cm reached 23.5 h into the storm; worst hour 9 mm (19% of the storm); water beside the road 0.18 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.9 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 9 mm; catchment 127.8 ha) (P 0.58) |
| 11 | 0.34 | Maple Street | Framingham | 0.26 m of water at peak; worst hour 7 mm (34% of the storm); a culvert within 100 m is overtopped |
| 12 | 0.34 | Cambridge Street | Worcester | 0.26 m of water at peak; worst hour 9 mm (20% of the storm); water beside the road 0.11 m above its crest (design freeboard 0.30 m; P 1.00); road sag 2.0 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 9 mm; catchment 77.2 ha) (P 0.34) |
| 13 | 0.27 | Amy Road | Framingham | 0.24 m of water at peak; worst hour 7 mm (32% of the storm); water beside the road 1.52 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.5 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 7 mm; catchment 15.6 ha) (P 0.98) |
| 14 | 0.26 | Maple Street | Northborough | 0.23 m of water at peak; worst hour 8 mm (20% of the storm); a culvert within 100 m is overtopped |
| 15 | 0.25 | Coolidge Road | Worcester | 0.23 m of water at peak; worst hour 9 mm (19% of the storm); water beside the road 0.23 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.7 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 9 mm; catchment 17.7 ha) (P 0.80) |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
