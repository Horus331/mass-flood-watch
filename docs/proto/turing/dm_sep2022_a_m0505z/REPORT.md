# Road-closure prototype: sep2022_proto_dm_sep2022_a_m0505z

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on GPU (cuda)), 20 m grid, storm from 2022-09-05T05:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 45,099 |
| Expected closures (sum of probabilities) | 106.8 |
| Segments with closure probability >= 50% | 25 (20.2 km) |
| Further segments that may close (stream reaches the road crest) | 64 (48.3 km) |
| Culverts overtopped / surcharged | 102 / 3 of 10736 |
| Road segments cut off from hospitals | 257 |
| Worst added trip time to a hospital | 16.2 min |
| Heaviest hour of rain | 29.7 mm |
| Flood model run time | 234 s |

## Checks against what happened

- Storm-day flood reports in the area: 6; water >= 10 cm within 100 m of 17% of them, vs 7% of random points (any day).
- Segments flagged impassable are 0.0x as likely as an average segment to have a report within 200 m.
- MassDOT repeating flood sites in the area: 30; 0 have a segment within 150 m at P >= 0.5 (share of all segments at P >= 0.5: 0.1%).

## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 0.99 | Pine Grove Avenue | Bellingham | 0.56 m of water at peak; over 30 cm for 6.0 h; 30 cm reached 13.5 h into the storm; worst hour 19 mm (26% of the storm); a culvert within 100 m is overtopped |
| 2 | 0.98 | Paine Street | Bellingham | 0.52 m of water at peak; over 30 cm for 5.5 h; 30 cm reached 14.0 h into the storm; worst hour 19 mm (26% of the storm); a culvert within 100 m is overtopped |
| 3 | 0.95 | Little Tree Lane | Framingham | 0.47 m of water at peak; over 30 cm for 2.0 h; 30 cm reached 1.0 h into the storm; worst hour 15 mm (31% of the storm); a culvert within 100 m is overtopped |
| 4 | 0.93 | (unnamed) | Berlin | 0.44 m of water at peak; over 30 cm for 0.5 h; 30 cm reached 0.5 h into the storm; worst hour 2 mm (46% of the storm); water beside the road 0.42 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 0.9 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.15) |
| 5 | 0.92 | Bartlett Street | Northborough | 0.44 m of water at peak; over 30 cm for 1.5 h; 30 cm reached 0.5 h into the storm; worst hour 7 mm (37% of the storm); a culvert within 100 m is overtopped |
| 6 | 0.91 | Belknap Road | Framingham | 0.44 m of water at peak; over 30 cm for 0.5 h; 30 cm reached 0.5 h into the storm; worst hour 15 mm (32% of the storm); a culvert within 100 m is overtopped |
| 7 | 0.90 | Route 62 | Berlin | 0.43 m of water at peak; over 30 cm for 0.5 h; 30 cm reached 0.5 h into the storm; worst hour 2 mm (45% of the storm); runoff beside / along the road at 0.6 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.14) |
| 8 | 0.89 | Maple Street | Northborough | 0.42 m of water at peak; over 30 cm for 0.5 h; 30 cm reached 0.5 h into the storm; worst hour 4 mm (35% of the storm); a culvert within 100 m is overtopped |
| 9 | 0.88 | Boundary Street | Marlborough | 0.42 m of water at peak; over 30 cm for 19.0 h; 30 cm reached 0.5 h into the storm; worst hour 4 mm (36% of the storm); runoff beside / along the road at 0.7 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.12); a culvert within 100 m is overtopped |
| 10 | 0.85 | Wrentham Road | Bellingham | 0.41 m of water at peak; over 30 cm for 5.5 h; 30 cm reached 14.0 h into the storm; worst hour 20 mm (27% of the storm); water beside the road 0.17 m below its crest (design freeboard 0.30 m; P 0.81); a culvert within 100 m is overtopped |
| 11 | 0.80 | Water Street | Clinton | 0.38 m of water at peak; over 30 cm for 4.5 h; 30 cm reached 0.5 h into the storm; worst hour 1 mm (42% of the storm) |
| 12 | 0.76 | Ramp-Solomon Pond Rd To Rt 290 Eb | Northborough | 0.37 m of water at peak; over 30 cm for 0.5 h; 30 cm reached 0.5 h into the storm; worst hour 3 mm (34% of the storm); water beside the road 0.53 m above its crest (design freeboard 0.30 m; P 1.00); a culvert within 100 m is overtopped |
| 13 | 0.76 | Ramp-Rt 290 Eb To Solomon Pond Rd Nb | Northborough | 0.37 m of water at peak; over 30 cm for 0.5 h; 30 cm reached 0.5 h into the storm; worst hour 3 mm (34% of the storm); water beside the road 0.37 m below its crest (design freeboard 0.30 m; P 0.32); a culvert within 100 m is overtopped |
| 14 | 0.74 | Belknap Road | Framingham | 0.37 m of water at peak; over 30 cm for 0.5 h; 30 cm reached 0.5 h into the storm; worst hour 15 mm (32% of the storm); a culvert within 100 m is overtopped |
| 15 | 0.72 | Knight Road | Framingham | 0.36 m of water at peak; over 30 cm for 2.0 h; 30 cm reached 1.0 h into the storm; worst hour 15 mm (31% of the storm); a culvert within 100 m is overtopped |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
