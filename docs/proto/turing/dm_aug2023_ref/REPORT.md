# Road-closure prototype: aug2023_proto_dm_aug2023_ref

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on GPU (cuda)), 20 m grid, storm from 2023-08-08T07:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 45,099 |
| Expected closures (sum of probabilities) | 103.0 |
| Segments with closure probability >= 50% | 8 (7.5 km) |
| Further segments that may close (stream reaches the road crest) | 93 (65.4 km) |
| Culverts overtopped / surcharged | 114 / 5 of 10736 |
| Road segments cut off from hospitals | 356 |
| Worst added trip time to a hospital | 14.2 min |
| Heaviest hour of rain | 52.8 mm |
| Flood model run time | 225 s |

## Checks against what happened

- Storm-day flood reports in the area: 6; water >= 10 cm within 100 m of 50% of them, vs 8% of random points (any day).
- Segments flagged impassable are 55.51x as likely as an average segment to have a report within 200 m.
- MassDOT repeating flood sites in the area: 30; 0 have a segment within 150 m at P >= 0.5 (share of all segments at P >= 0.5: 0.0%).

## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 1.00 | (unnamed) | Framingham | 1.33 m of water at peak; over 30 cm for 10.5 h; 30 cm reached 8.0 h into the storm; worst hour 17 mm (26% of the storm); water beside the road 1.07 m above its crest (design freeboard 0.30 m; P 1.00); road sag 2.9 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 16 mm; catchment 15.3 ha) (P 1.00) |
| 2 | 0.85 | (unnamed) | Berlin | 0.40 m of water at peak; over 30 cm for 0.5 h; 30 cm reached 0.5 h into the storm; worst hour 8 mm (50% of the storm); water beside the road 0.42 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 0.9 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.15) |
| 3 | 0.81 | Route 62 | Berlin | 0.39 m of water at peak; over 30 cm for 0.5 h; 30 cm reached 0.5 h into the storm; worst hour 9 mm (53% of the storm); runoff beside / along the road at 0.6 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.14) |
| 4 | 0.64 | Belknap Road | Framingham | 0.34 m of water at peak; over 30 cm for 0.5 h; 30 cm reached 0.5 h into the storm; worst hour 23 mm (32% of the storm); a culvert within 100 m is overtopped |
| 5 | 0.63 | Maple Street | Northborough | 0.33 m of water at peak; over 30 cm for 0.5 h; 30 cm reached 0.5 h into the storm; worst hour 34 mm (75% of the storm); a culvert within 100 m is overtopped |
| 6 | 0.59 | (unnamed) | Holliston | 0.32 m of water at peak; over 30 cm for 9.0 h; 30 cm reached 9.5 h into the storm; worst hour 27 mm (39% of the storm) |
| 7 | 0.58 | Millwood Street | Framingham | 0.32 m of water at peak; over 30 cm for 1.5 h; 30 cm reached 8.5 h into the storm; worst hour 21 mm (29% of the storm); water beside the road 0.49 m below its crest (design freeboard 0.30 m; P 0.10); a culvert within 100 m is overtopped |
| 8 | 0.50 | Amy Road | Framingham | 0.30 m of water at peak; worst hour 24 mm (35% of the storm); water beside the road 1.53 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.5 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 24 mm; catchment 15.6 ha) (P 0.99) |
| 9 | 0.47 | (unnamed) | Holliston | 0.29 m of water at peak; worst hour 27 mm (40% of the storm); a culvert within 100 m is overtopped |
| 10 | 0.46 | Gregory Road | Framingham | 0.29 m of water at peak; worst hour 28 mm (39% of the storm); water beside the road 0.26 m below its crest (design freeboard 0.30 m; P 0.60); runoff beside / along the road at 0.5 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.11); a culvert within 100 m is overtopped |
| 11 | 0.46 | Hudson Street | Northborough | 0.29 m of water at peak; worst hour 28 mm (74% of the storm); water beside the road 0.48 m below its crest (design freeboard 0.30 m; P 0.12); a culvert within 100 m is overtopped |
| 12 | 0.44 | Belknap Road | Framingham | 0.29 m of water at peak; worst hour 21 mm (29% of the storm); a culvert within 100 m is overtopped |
| 13 | 0.44 | Ruthellen Road | Framingham | 0.28 m of water at peak; worst hour 24 mm (35% of the storm); water beside the road 0.35 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.5 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 24 mm; catchment 15.6 ha) (P 0.99) |
| 14 | 0.44 | Hurley Circle | Marlborough | 0.28 m of water at peak; worst hour 47 mm (81% of the storm); water beside the road 0.47 m above its crest (design freeboard 0.30 m; P 1.00); a culvert within 100 m is overtopped |
| 15 | 0.41 | Maple Street | Framingham | 0.28 m of water at peak; worst hour 28 mm (43% of the storm); a culvert within 100 m is overtopped |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
