# Road-closure prototype: aug2021_proto_dm_aug2021_a_m1908z

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on GPU (cuda)), 20 m grid, storm from 2021-08-19T08:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 45,099 |
| Expected closures (sum of probabilities) | 88.4 |
| Segments with closure probability >= 50% | 8 (7.6 km) |
| Further segments that may close (stream reaches the road crest) | 71 (50.9 km) |
| Culverts overtopped / surcharged | 77 / 7 of 10736 |
| Road segments cut off from hospitals | 252 |
| Worst added trip time to a hospital | 13.5 min |
| Heaviest hour of rain | 44.3 mm |
| Flood model run time | 255 s |

## Checks against what happened

- Storm-day flood reports in the area: 10; water >= 10 cm within 100 m of 0% of them, vs 4% of random points (any day).
- Segments flagged impassable are 0.0x as likely as an average segment to have a report within 200 m.
- MassDOT repeating flood sites in the area: 30; 0 have a segment within 150 m at P >= 0.5 (share of all segments at P >= 0.5: 0.0%).

## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 0.85 | (unnamed) | Berlin | 0.40 m of water at peak; over 30 cm for 0.5 h; 30 cm reached 0.5 h into the storm; worst hour 6 mm (31% of the storm); water beside the road 0.42 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 0.9 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.15) |
| 2 | 0.81 | Route 62 | Berlin | 0.39 m of water at peak; over 30 cm for 0.5 h; 30 cm reached 0.5 h into the storm; worst hour 6 mm (31% of the storm); runoff beside / along the road at 0.6 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.14) |
| 3 | 0.74 | Route 117 | Lancaster | 0.36 m of water at peak; over 30 cm for 19.0 h; 30 cm reached 0.5 h into the storm; worst hour 6 mm (26% of the storm) |
| 4 | 0.64 | Belknap Road | Framingham | 0.34 m of water at peak; over 30 cm for 0.5 h; 30 cm reached 0.5 h into the storm; worst hour 7 mm (45% of the storm); a culvert within 100 m is overtopped |
| 5 | 0.63 | Maple Street | Northborough | 0.33 m of water at peak; over 30 cm for 0.5 h; 30 cm reached 0.5 h into the storm; worst hour 7 mm (36% of the storm); a culvert within 100 m is overtopped |
| 6 | 0.59 | Depot Street | Fitchburg | 0.32 m of water at peak; over 30 cm for 13.5 h; 30 cm reached 0.5 h into the storm; worst hour 19 mm (33% of the storm); a culvert within 100 m is overtopped |
| 7 | 0.54 | Tuckerman Road | Ashburnham | 0.31 m of water at peak; over 30 cm for 5.5 h; 30 cm reached 11.0 h into the storm; worst hour 30 mm (33% of the storm); a culvert within 100 m is overtopped |
| 8 | 0.50 | Amy Road | Framingham | 0.30 m of water at peak; worst hour 7 mm (44% of the storm); water beside the road 1.53 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.5 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 7 mm; catchment 15.6 ha) (P 0.99) |
| 9 | 0.48 | Young Road | Ashburnham | 0.29 m of water at peak; worst hour 30 mm (34% of the storm); a culvert within 100 m is overtopped |
| 10 | 0.46 | Hudson Street | Northborough | 0.29 m of water at peak; worst hour 6 mm (35% of the storm); water beside the road 0.48 m below its crest (design freeboard 0.30 m; P 0.12); a culvert within 100 m is overtopped |
| 11 | 0.44 | Belknap Road | Framingham | 0.29 m of water at peak; worst hour 7 mm (46% of the storm); a culvert within 100 m is overtopped |
| 12 | 0.44 | Ruthellen Road | Framingham | 0.28 m of water at peak; worst hour 7 mm (44% of the storm); water beside the road 0.35 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.5 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 7 mm; catchment 15.6 ha) (P 0.99) |
| 13 | 0.39 | Ramp-Rt 290 Eb To Solomon Pond Rd Nb | Northborough | 0.27 m of water at peak; worst hour 6 mm (34% of the storm); water beside the road 0.37 m below its crest (design freeboard 0.30 m; P 0.32); a culvert within 100 m is overtopped |
| 14 | 0.39 | Ramp-Solomon Pond Rd To Rt 290 Eb | Northborough | 0.27 m of water at peak; worst hour 6 mm (34% of the storm); water beside the road 0.53 m above its crest (design freeboard 0.30 m; P 1.00); a culvert within 100 m is overtopped |
| 15 | 0.38 | Maple Street | Framingham | 0.27 m of water at peak; worst hour 7 mm (46% of the storm); a culvert within 100 m is overtopped |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
