# Road-closure prototype: sep2022_proto_dm_sep2022_ref

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on GPU (cuda)), 20 m grid, storm from 2022-09-05T06:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 45,099 |
| Expected closures (sum of probabilities) | 99.7 |
| Segments with closure probability >= 50% | 19 (16.0 km) |
| Further segments that may close (stream reaches the road crest) | 85 (57.8 km) |
| Culverts overtopped / surcharged | 105 / 5 of 10736 |
| Road segments cut off from hospitals | 355 |
| Worst added trip time to a hospital | 21.8 min |
| Heaviest hour of rain | 85.7 mm |
| Flood model run time | 214 s |

## Checks against what happened

- Storm-day flood reports in the area: 6; water >= 10 cm within 100 m of 33% of them, vs 7% of random points (any day).
- Segments flagged impassable are 10.5x as likely as an average segment to have a report within 200 m.
- MassDOT repeating flood sites in the area: 30; 0 have a segment within 150 m at P >= 0.5 (share of all segments at P >= 0.5: 0.0%).

## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 0.99 | Route 12 | Dudley | 0.53 m of water at peak; over 30 cm for 3.5 h; 30 cm reached 9.5 h into the storm; worst hour 83 mm (81% of the storm); runoff beside / along the road at 0.6 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.14); a culvert within 100 m is overtopped |
| 2 | 0.92 | Healy Road | Dudley | 0.44 m of water at peak; over 30 cm for 2.0 h; 30 cm reached 9.0 h into the storm; worst hour 52 mm (59% of the storm); a culvert within 100 m is overtopped |
| 3 | 0.88 | Mason Road Extension | Dudley | 0.42 m of water at peak; over 30 cm for 2.5 h; 30 cm reached 9.0 h into the storm; worst hour 48 mm (62% of the storm); water beside the road 0.10 m below its crest (design freeboard 0.30 m; P 0.91); a culvert within 100 m is overtopped |
| 4 | 0.78 | Belknap Road | Framingham | 0.38 m of water at peak; over 30 cm for 0.5 h; 30 cm reached 0.5 h into the storm; worst hour 4 mm (30% of the storm); a culvert within 100 m is overtopped |
| 5 | 0.77 | Maple Street | Northborough | 0.37 m of water at peak; over 30 cm for 0.5 h; 30 cm reached 0.5 h into the storm; worst hour 12 mm (54% of the storm); a culvert within 100 m is overtopped |
| 6 | 0.70 | (unnamed) | Berlin | 0.35 m of water at peak; over 30 cm for 0.5 h; 30 cm reached 0.5 h into the storm; worst hour 7 mm (43% of the storm); water beside the road 0.42 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 0.9 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.15) |
| 7 | 0.68 | Route 62 | Berlin | 0.35 m of water at peak; over 30 cm for 0.5 h; 30 cm reached 0.5 h into the storm; worst hour 7 mm (43% of the storm); runoff beside / along the road at 0.6 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.14) |
| 8 | 0.67 | Midstate Trail | Douglas | 0.34 m of water at peak; over 30 cm for 2.5 h; 30 cm reached 10.5 h into the storm; worst hour 44 mm (53% of the storm); runoff beside / along the road at 1.3 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.48); a culvert within 100 m is overtopped |
| 9 | 0.66 | Fairview Avenue | Dudley | 0.34 m of water at peak; over 30 cm for 1.0 h; 30 cm reached 10.0 h into the storm; worst hour 77 mm (80% of the storm); a culvert within 100 m is overtopped |
| 10 | 0.60 | (unnamed) | Webster | 0.33 m of water at peak; over 30 cm for 0.5 h; 30 cm reached 9.0 h into the storm; worst hour 75 mm (76% of the storm); water beside the road 0.29 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.6 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 75 mm; catchment 11.3 ha) (P 1.00) |
| 11 | 0.59 | Mason Road | Dudley | 0.32 m of water at peak; over 30 cm for 0.5 h; 30 cm reached 9.5 h into the storm; worst hour 76 mm (74% of the storm); a culvert within 100 m is overtopped |
| 12 | 0.58 | Bartlett Street | Northborough | 0.32 m of water at peak; over 30 cm for 1.5 h; 30 cm reached 0.5 h into the storm; worst hour 10 mm (50% of the storm); a culvert within 100 m is overtopped |
| 13 | 0.58 | Amy Road | Framingham | 0.32 m of water at peak; worst hour 3 mm (30% of the storm); water beside the road 1.53 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.5 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 3 mm; catchment 15.6 ha) (P 0.99) |
| 14 | 0.56 | Belknap Road | Framingham | 0.32 m of water at peak; over 30 cm for 0.5 h; 30 cm reached 0.5 h into the storm; worst hour 4 mm (30% of the storm); a culvert within 100 m is overtopped |
| 15 | 0.54 | Ramp-Solomon Pond Rd To Rt 290 Eb | Northborough | 0.31 m of water at peak; over 30 cm for 0.5 h; 30 cm reached 0.5 h into the storm; worst hour 10 mm (52% of the storm); water beside the road 0.53 m above its crest (design freeboard 0.30 m; P 1.00); a culvert within 100 m is overtopped |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
