# Road-closure prototype: aug2023_proto_dm_aug2023_a_m0806z

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on GPU (cuda)), 20 m grid, storm from 2023-08-08T06:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 45,099 |
| Expected closures (sum of probabilities) | 82.7 |
| Segments with closure probability >= 50% | 12 (10.3 km) |
| Further segments that may close (stream reaches the road crest) | 62 (47.1 km) |
| Culverts overtopped / surcharged | 57 / 5 of 10736 |
| Road segments cut off from hospitals | 149 |
| Worst added trip time to a hospital | 14.1 min |
| Heaviest hour of rain | 23.2 mm |
| Flood model run time | 175 s |

## Checks against what happened

- Storm-day flood reports in the area: 6; water >= 10 cm within 100 m of 17% of them, vs 5% of random points (any day).
- Segments flagged impassable are 0.0x as likely as an average segment to have a report within 200 m.
- MassDOT repeating flood sites in the area: 30; 0 have a segment within 150 m at P >= 0.5 (share of all segments at P >= 0.5: 0.0%).

## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 0.78 | Belknap Road | Framingham | 0.38 m of water at peak; over 30 cm for 0.5 h; 30 cm reached 0.5 h into the storm; worst hour 13 mm (40% of the storm); a culvert within 100 m is overtopped |
| 2 | 0.77 | Maple Street | Northborough | 0.37 m of water at peak; over 30 cm for 0.5 h; 30 cm reached 0.5 h into the storm; worst hour 6 mm (45% of the storm); a culvert within 100 m is overtopped |
| 3 | 0.70 | (unnamed) | Berlin | 0.35 m of water at peak; over 30 cm for 0.5 h; 30 cm reached 0.5 h into the storm; worst hour 5 mm (41% of the storm); water beside the road 0.42 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 0.9 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.15) |
| 4 | 0.68 | Route 62 | Berlin | 0.35 m of water at peak; over 30 cm for 0.5 h; 30 cm reached 0.5 h into the storm; worst hour 5 mm (41% of the storm); runoff beside / along the road at 0.6 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.14) |
| 5 | 0.58 | Bartlett Street | Northborough | 0.32 m of water at peak; over 30 cm for 1.5 h; 30 cm reached 0.5 h into the storm; worst hour 6 mm (38% of the storm); a culvert within 100 m is overtopped |
| 6 | 0.58 | Amy Road | Framingham | 0.32 m of water at peak; worst hour 13 mm (40% of the storm); water beside the road 1.53 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.5 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 13 mm; catchment 15.6 ha) (P 0.99) |
| 7 | 0.56 | Belknap Road | Framingham | 0.32 m of water at peak; over 30 cm for 0.5 h; 30 cm reached 0.5 h into the storm; worst hour 13 mm (42% of the storm); a culvert within 100 m is overtopped |
| 8 | 0.54 | Ramp-Solomon Pond Rd To Rt 290 Eb | Northborough | 0.31 m of water at peak; over 30 cm for 0.5 h; 30 cm reached 0.5 h into the storm; worst hour 6 mm (42% of the storm); water beside the road 0.53 m above its crest (design freeboard 0.30 m; P 1.00); a culvert within 100 m is overtopped |
| 9 | 0.54 | Ramp-Rt 290 Eb To Solomon Pond Rd Nb | Northborough | 0.31 m of water at peak; over 30 cm for 0.5 h; 30 cm reached 0.5 h into the storm; worst hour 6 mm (42% of the storm); water beside the road 0.37 m below its crest (design freeboard 0.30 m; P 0.32); a culvert within 100 m is overtopped |
| 10 | 0.54 | Hudson Street | Northborough | 0.31 m of water at peak; worst hour 6 mm (44% of the storm); water beside the road 0.48 m below its crest (design freeboard 0.30 m; P 0.12); a culvert within 100 m is overtopped |
| 11 | 0.53 | Little Tree Lane | Framingham | 0.31 m of water at peak; over 30 cm for 2.0 h; 30 cm reached 1.0 h into the storm; worst hour 13 mm (40% of the storm); a culvert within 100 m is overtopped |
| 12 | 0.52 | Ruthellen Road | Framingham | 0.30 m of water at peak; worst hour 13 mm (40% of the storm); water beside the road 0.36 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.5 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 13 mm; catchment 15.6 ha) (P 0.99) |
| 13 | 0.48 | Millwood Street | Framingham | 0.29 m of water at peak; worst hour 13 mm (42% of the storm); a culvert within 100 m is overtopped |
| 14 | 0.38 | Blackberry Lane | Framingham | 0.27 m of water at peak; worst hour 13 mm (41% of the storm); a culvert within 100 m is overtopped |
| 15 | 0.37 | Chestnut Hill Road | Southborough | 0.27 m of water at peak; worst hour 10 mm (42% of the storm); a culvert within 100 m is overtopped |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
