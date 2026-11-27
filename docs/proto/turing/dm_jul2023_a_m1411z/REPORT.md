# Road-closure prototype: jul2023_proto_dm_jul2023_a_m1411z

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on GPU (cuda)), 20 m grid, storm from 2023-07-14T11:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 45,099 |
| Expected closures (sum of probabilities) | 91.0 |
| Segments with closure probability >= 50% | 20 (16.8 km) |
| Further segments that may close (stream reaches the road crest) | 62 (46.9 km) |
| Culverts overtopped / surcharged | 77 / 3 of 10736 |
| Road segments cut off from hospitals | 188 |
| Worst added trip time to a hospital | 15.0 min |
| Heaviest hour of rain | 3.7 mm |
| Flood model run time | 194 s |

## Checks against what happened

- Storm-day flood reports in the area: 4; water >= 10 cm within 100 m of 0% of them, vs 5% of random points (any day).
- Segments flagged impassable are 0.0x as likely as an average segment to have a report within 200 m.
- MassDOT repeating flood sites in the area: 30; 0 have a segment within 150 m at P >= 0.5 (share of all segments at P >= 0.5: 0.0%).

## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 0.93 | Little Tree Lane | Framingham | 0.45 m of water at peak; over 30 cm for 2.0 h; 30 cm reached 1.0 h into the storm; worst hour 3 mm (55% of the storm); a culvert within 100 m is overtopped |
| 2 | 0.91 | Belknap Road | Framingham | 0.44 m of water at peak; over 30 cm for 0.5 h; 30 cm reached 0.5 h into the storm; worst hour 3 mm (56% of the storm); a culvert within 100 m is overtopped |
| 3 | 0.91 | (unnamed) | Berlin | 0.43 m of water at peak; over 30 cm for 0.5 h; 30 cm reached 0.5 h into the storm; worst hour 1 mm (35% of the storm); water beside the road 0.42 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 0.9 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.15) |
| 4 | 0.89 | Maple Street | Northborough | 0.42 m of water at peak; over 30 cm for 0.5 h; 30 cm reached 0.5 h into the storm; worst hour 2 mm (41% of the storm); a culvert within 100 m is overtopped |
| 5 | 0.89 | Bartlett Street | Northborough | 0.42 m of water at peak; over 30 cm for 1.5 h; 30 cm reached 0.5 h into the storm; worst hour 3 mm (44% of the storm); a culvert within 100 m is overtopped |
| 6 | 0.88 | Route 62 | Berlin | 0.42 m of water at peak; over 30 cm for 0.5 h; 30 cm reached 0.5 h into the storm; worst hour 1 mm (35% of the storm); runoff beside / along the road at 0.6 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.14) |
| 7 | 0.73 | Ramp-Solomon Pond Rd To Rt 290 Eb | Northborough | 0.36 m of water at peak; over 30 cm for 0.5 h; 30 cm reached 0.5 h into the storm; worst hour 2 mm (39% of the storm); water beside the road 0.53 m above its crest (design freeboard 0.30 m; P 1.00); a culvert within 100 m is overtopped |
| 8 | 0.73 | Ramp-Rt 290 Eb To Solomon Pond Rd Nb | Northborough | 0.36 m of water at peak; over 30 cm for 0.5 h; 30 cm reached 0.5 h into the storm; worst hour 2 mm (39% of the storm); water beside the road 0.37 m below its crest (design freeboard 0.30 m; P 0.32); a culvert within 100 m is overtopped |
| 9 | 0.71 | Belknap Road | Framingham | 0.36 m of water at peak; over 30 cm for 0.5 h; 30 cm reached 0.5 h into the storm; worst hour 3 mm (54% of the storm); a culvert within 100 m is overtopped |
| 10 | 0.70 | Water Street | Clinton | 0.35 m of water at peak; over 30 cm for 4.5 h; 30 cm reached 0.5 h into the storm; worst hour 1 mm (41% of the storm) |
| 11 | 0.66 | Hudson Street | Northborough | 0.34 m of water at peak; worst hour 2 mm (38% of the storm); water beside the road 0.48 m below its crest (design freeboard 0.30 m; P 0.12); a culvert within 100 m is overtopped |
| 12 | 0.65 | Knight Road | Framingham | 0.34 m of water at peak; over 30 cm for 2.0 h; 30 cm reached 1.0 h into the storm; worst hour 3 mm (55% of the storm); a culvert within 100 m is overtopped |
| 13 | 0.64 | Ruthellen Road | Framingham | 0.34 m of water at peak; worst hour 4 mm (58% of the storm); water beside the road 0.36 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.5 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 4 mm; catchment 15.6 ha) (P 0.99) |
| 14 | 0.62 | Amy Road | Framingham | 0.33 m of water at peak; worst hour 4 mm (58% of the storm); water beside the road 1.53 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.5 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 4 mm; catchment 15.6 ha) (P 0.99) |
| 15 | 0.59 | Millwood Street | Framingham | 0.32 m of water at peak; worst hour 3 mm (56% of the storm); a culvert within 100 m is overtopped |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
