# Road-closure prototype: aug2023_proto_dm_aug2023_vp

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on GPU (cuda)), 20 m grid, storm from 2023-08-08T12:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 45,099 |
| Expected closures (sum of probabilities) | 75.4 |
| Segments with closure probability >= 50% | 6 (6.4 km) |
| Further segments that may close (stream reaches the road crest) | 65 (48.1 km) |
| Culverts overtopped / surcharged | 30 / 4 of 10736 |
| Road segments cut off from hospitals | 95 |
| Worst added trip time to a hospital | 13.2 min |
| Heaviest hour of rain | 10.8 mm |
| Flood model run time | 172 s |

## Checks against what happened

- Storm-day flood reports in the area: 6; water >= 10 cm within 100 m of 17% of them, vs 6% of random points (any day).
- Segments flagged impassable are 0.0x as likely as an average segment to have a report within 200 m.
- MassDOT repeating flood sites in the area: 30; 1 have a segment within 150 m at P >= 0.5 (share of all segments at P >= 0.5: 0.0%).

## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 0.84 | Route 117 | Lancaster | 0.40 m of water at peak; over 30 cm for 13.0 h; 30 cm reached 0.5 h into the storm; worst hour 8 mm (38% of the storm) |
| 2 | 0.72 | Route 9 | Framingham | 0.36 m of water at peak; over 30 cm for 2.0 h; 30 cm reached 2.0 h into the storm; worst hour 3 mm (34% of the storm); a culvert within 100 m is overtopped |
| 3 | 0.72 | Route 9 | Framingham | 0.36 m of water at peak; over 30 cm for 2.0 h; 30 cm reached 2.0 h into the storm; worst hour 3 mm (34% of the storm); a culvert within 100 m is overtopped |
| 4 | 0.56 | (unnamed) | Berlin | 0.31 m of water at peak; over 30 cm for 0.5 h; 30 cm reached 0.5 h into the storm; worst hour 9 mm (39% of the storm); water beside the road 0.41 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 0.9 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.15) |
| 5 | 0.53 | Route 62 | Berlin | 0.31 m of water at peak; over 30 cm for 0.5 h; 30 cm reached 0.5 h into the storm; worst hour 9 mm (39% of the storm); runoff beside / along the road at 0.5 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.14) |
| 6 | 0.52 | Salem End Road | Framingham | 0.30 m of water at peak; over 30 cm for 1.5 h; 30 cm reached 2.5 h into the storm; worst hour 3 mm (34% of the storm); a culvert within 100 m is overtopped |
| 7 | 0.34 | Maple Street | Framingham | 0.26 m of water at peak; worst hour 3 mm (34% of the storm); a culvert within 100 m is overtopped |
| 8 | 0.27 | Amy Road | Framingham | 0.24 m of water at peak; worst hour 3 mm (33% of the storm); water beside the road 1.52 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.5 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 3 mm; catchment 15.6 ha) (P 0.98) |
| 9 | 0.26 | Maple Street | Northborough | 0.23 m of water at peak; worst hour 8 mm (39% of the storm); a culvert within 100 m is overtopped |
| 10 | 0.24 | Hudson Street | Northborough | 0.23 m of water at peak; worst hour 8 mm (39% of the storm); water beside the road 0.48 m below its crest (design freeboard 0.30 m; P 0.12); a culvert within 100 m is overtopped |
| 11 | 0.23 | Ruthellen Road | Framingham | 0.23 m of water at peak; worst hour 3 mm (33% of the storm); water beside the road 0.33 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.5 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 3 mm; catchment 15.6 ha) (P 0.98) |
| 12 | 0.17 | Belknap Road | Framingham | 0.21 m of water at peak; worst hour 3 mm (34% of the storm); a culvert within 100 m is overtopped |
| 13 | 0.15 | Belknap Road | Framingham | 0.20 m of water at peak; worst hour 3 mm (34% of the storm); a culvert within 100 m is overtopped |
| 14 | 0.14 | Ramp-Rt 290 Eb To Solomon Pond Rd Nb | Northborough | 0.19 m of water at peak; worst hour 8 mm (39% of the storm); water beside the road 0.37 m below its crest (design freeboard 0.30 m; P 0.32); a culvert within 100 m is overtopped |
| 15 | 0.14 | Ramp-Solomon Pond Rd To Rt 290 Eb | Northborough | 0.19 m of water at peak; worst hour 8 mm (39% of the storm); water beside the road 0.53 m above its crest (design freeboard 0.30 m; P 1.00); a culvert within 100 m is overtopped |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
