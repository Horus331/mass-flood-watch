# Road-closure prototype: aug2023b_proto_dm_aug2023b_a_m1806z

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on GPU (cuda)), 20 m grid, storm from 2023-08-18T06:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 45,099 |
| Expected closures (sum of probabilities) | 99.5 |
| Segments with closure probability >= 50% | 20 (16.8 km) |
| Further segments that may close (stream reaches the road crest) | 63 (47.6 km) |
| Culverts overtopped / surcharged | 79 / 3 of 10736 |
| Road segments cut off from hospitals | 194 |
| Worst added trip time to a hospital | 16.5 min |
| Heaviest hour of rain | 30.4 mm |
| Flood model run time | 227 s |

## Checks against what happened

- Storm-day flood reports in the area: 3; water >= 10 cm within 100 m of 33% of them, vs 7% of random points (any day).
- Segments flagged impassable are 0.0x as likely as an average segment to have a report within 200 m.
- MassDOT repeating flood sites in the area: 30; 0 have a segment within 150 m at P >= 0.5 (share of all segments at P >= 0.5: 0.0%).

## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 0.93 | Little Tree Lane | Framingham | 0.45 m of water at peak; over 30 cm for 2.0 h; 30 cm reached 1.0 h into the storm; worst hour 20 mm (62% of the storm); a culvert within 100 m is overtopped |
| 2 | 0.91 | Belknap Road | Framingham | 0.44 m of water at peak; over 30 cm for 0.5 h; 30 cm reached 0.5 h into the storm; worst hour 20 mm (62% of the storm); a culvert within 100 m is overtopped |
| 3 | 0.91 | (unnamed) | Berlin | 0.43 m of water at peak; over 30 cm for 0.5 h; 30 cm reached 0.5 h into the storm; worst hour 17 mm (46% of the storm); water beside the road 0.42 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 0.9 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.15) |
| 4 | 0.89 | Maple Street | Northborough | 0.42 m of water at peak; over 30 cm for 0.5 h; 30 cm reached 0.5 h into the storm; worst hour 17 mm (44% of the storm); a culvert within 100 m is overtopped |
| 5 | 0.89 | Bartlett Street | Northborough | 0.42 m of water at peak; over 30 cm for 1.5 h; 30 cm reached 0.5 h into the storm; worst hour 17 mm (43% of the storm); a culvert within 100 m is overtopped |
| 6 | 0.88 | Route 62 | Berlin | 0.42 m of water at peak; over 30 cm for 0.5 h; 30 cm reached 0.5 h into the storm; worst hour 17 mm (46% of the storm); runoff beside / along the road at 0.6 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.14) |
| 7 | 0.73 | Ramp-Solomon Pond Rd To Rt 290 Eb | Northborough | 0.36 m of water at peak; over 30 cm for 0.5 h; 30 cm reached 0.5 h into the storm; worst hour 17 mm (44% of the storm); water beside the road 0.53 m above its crest (design freeboard 0.30 m; P 1.00); a culvert within 100 m is overtopped |
| 8 | 0.73 | Ramp-Rt 290 Eb To Solomon Pond Rd Nb | Northborough | 0.36 m of water at peak; over 30 cm for 0.5 h; 30 cm reached 0.5 h into the storm; worst hour 17 mm (44% of the storm); water beside the road 0.37 m below its crest (design freeboard 0.30 m; P 0.32); a culvert within 100 m is overtopped |
| 9 | 0.71 | Belknap Road | Framingham | 0.36 m of water at peak; over 30 cm for 0.5 h; 30 cm reached 0.5 h into the storm; worst hour 20 mm (61% of the storm); a culvert within 100 m is overtopped |
| 10 | 0.70 | Water Street | Clinton | 0.35 m of water at peak; over 30 cm for 5.0 h; 30 cm reached 0.5 h into the storm; worst hour 17 mm (48% of the storm) |
| 11 | 0.66 | Hudson Street | Northborough | 0.34 m of water at peak; worst hour 17 mm (44% of the storm); water beside the road 0.48 m below its crest (design freeboard 0.30 m; P 0.12); a culvert within 100 m is overtopped |
| 12 | 0.65 | Knight Road | Framingham | 0.34 m of water at peak; over 30 cm for 2.0 h; 30 cm reached 1.0 h into the storm; worst hour 20 mm (62% of the storm); a culvert within 100 m is overtopped |
| 13 | 0.64 | Ruthellen Road | Framingham | 0.34 m of water at peak; worst hour 20 mm (64% of the storm); water beside the road 0.36 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.5 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 20 mm; catchment 15.6 ha) (P 0.99) |
| 14 | 0.62 | Amy Road | Framingham | 0.33 m of water at peak; worst hour 20 mm (64% of the storm); water beside the road 1.53 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.5 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 20 mm; catchment 15.6 ha) (P 0.99) |
| 15 | 0.59 | Millwood Street | Framingham | 0.32 m of water at peak; worst hour 20 mm (62% of the storm); a culvert within 100 m is overtopped |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
