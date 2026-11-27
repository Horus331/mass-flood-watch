# Road-closure prototype: jul2023_proto_dm_jul2023_a_m1410z

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on GPU (cuda)), 20 m grid, storm from 2023-07-14T10:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 45,099 |
| Expected closures (sum of probabilities) | 94.3 |
| Segments with closure probability >= 50% | 21 (16.9 km) |
| Further segments that may close (stream reaches the road crest) | 62 (46.9 km) |
| Culverts overtopped / surcharged | 77 / 3 of 10736 |
| Road segments cut off from hospitals | 186 |
| Worst added trip time to a hospital | 15.2 min |
| Heaviest hour of rain | 7.1 mm |
| Flood model run time | 206 s |

## Checks against what happened

- Storm-day flood reports in the area: 4; water >= 10 cm within 100 m of 0% of them, vs 5% of random points (any day).
- Segments flagged impassable are 0.0x as likely as an average segment to have a report within 200 m.
- MassDOT repeating flood sites in the area: 30; 0 have a segment within 150 m at P >= 0.5 (share of all segments at P >= 0.5: 0.0%).

## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 0.95 | Little Tree Lane | Framingham | 0.47 m of water at peak; over 30 cm for 2.0 h; 30 cm reached 1.0 h into the storm; worst hour 2 mm (45% of the storm); a culvert within 100 m is overtopped |
| 2 | 0.93 | (unnamed) | Berlin | 0.44 m of water at peak; over 30 cm for 0.5 h; 30 cm reached 0.5 h into the storm; worst hour 4 mm (51% of the storm); water beside the road 0.42 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 1.0 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.16) |
| 3 | 0.92 | Bartlett Street | Northborough | 0.44 m of water at peak; over 30 cm for 1.5 h; 30 cm reached 0.5 h into the storm; worst hour 4 mm (51% of the storm); a culvert within 100 m is overtopped |
| 4 | 0.91 | Belknap Road | Framingham | 0.44 m of water at peak; over 30 cm for 0.5 h; 30 cm reached 0.5 h into the storm; worst hour 2 mm (43% of the storm); a culvert within 100 m is overtopped |
| 5 | 0.90 | Route 62 | Berlin | 0.43 m of water at peak; over 30 cm for 0.5 h; 30 cm reached 0.5 h into the storm; worst hour 4 mm (50% of the storm); runoff beside / along the road at 1.0 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.16) |
| 6 | 0.89 | Maple Street | Northborough | 0.42 m of water at peak; over 30 cm for 0.5 h; 30 cm reached 0.5 h into the storm; worst hour 4 mm (52% of the storm); a culvert within 100 m is overtopped |
| 7 | 0.88 | Boundary Street | Marlborough | 0.42 m of water at peak; over 30 cm for 16.0 h; 30 cm reached 0.5 h into the storm; worst hour 4 mm (49% of the storm); runoff beside / along the road at 0.7 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.12); a culvert within 100 m is overtopped |
| 8 | 0.80 | Water Street | Clinton | 0.38 m of water at peak; over 30 cm for 4.5 h; 30 cm reached 0.5 h into the storm; worst hour 4 mm (51% of the storm) |
| 9 | 0.76 | Ramp-Solomon Pond Rd To Rt 290 Eb | Northborough | 0.37 m of water at peak; over 30 cm for 0.5 h; 30 cm reached 0.5 h into the storm; worst hour 4 mm (50% of the storm); water beside the road 0.53 m above its crest (design freeboard 0.30 m; P 1.00); a culvert within 100 m is overtopped |
| 10 | 0.76 | Ramp-Rt 290 Eb To Solomon Pond Rd Nb | Northborough | 0.37 m of water at peak; over 30 cm for 0.5 h; 30 cm reached 0.5 h into the storm; worst hour 4 mm (50% of the storm); water beside the road 0.37 m below its crest (design freeboard 0.30 m; P 0.32); a culvert within 100 m is overtopped |
| 11 | 0.74 | Belknap Road | Framingham | 0.37 m of water at peak; over 30 cm for 0.5 h; 30 cm reached 0.5 h into the storm; worst hour 2 mm (43% of the storm); a culvert within 100 m is overtopped |
| 12 | 0.72 | Knight Road | Framingham | 0.36 m of water at peak; over 30 cm for 2.0 h; 30 cm reached 1.0 h into the storm; worst hour 2 mm (44% of the storm); a culvert within 100 m is overtopped |
| 13 | 0.66 | Amy Road | Framingham | 0.34 m of water at peak; worst hour 2 mm (42% of the storm); water beside the road 1.53 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.5 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 2 mm; catchment 15.6 ha) (P 0.99) |
| 14 | 0.66 | Hudson Street | Northborough | 0.34 m of water at peak; worst hour 4 mm (51% of the storm); water beside the road 0.48 m below its crest (design freeboard 0.30 m; P 0.12); a culvert within 100 m is overtopped |
| 15 | 0.64 | Ruthellen Road | Framingham | 0.34 m of water at peak; worst hour 2 mm (43% of the storm); water beside the road 0.36 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.5 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 2 mm; catchment 15.6 ha) (P 0.99) |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
