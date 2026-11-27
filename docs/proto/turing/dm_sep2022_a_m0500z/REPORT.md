# Road-closure prototype: sep2022_proto_dm_sep2022_a_m0500z

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on GPU (cuda)), 20 m grid, storm from 2022-09-05T00:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 45,099 |
| Expected closures (sum of probabilities) | 103.8 |
| Segments with closure probability >= 50% | 31 (25.0 km) |
| Further segments that may close (stream reaches the road crest) | 62 (46.2 km) |
| Culverts overtopped / surcharged | 90 / 3 of 10736 |
| Road segments cut off from hospitals | 232 |
| Worst added trip time to a hospital | 15.4 min |
| Heaviest hour of rain | 33.6 mm |
| Flood model run time | 310 s |

## Checks against what happened

- Storm-day flood reports in the area: 6; water >= 10 cm within 100 m of 17% of them, vs 6% of random points (any day).
- Segments flagged impassable are 0.0x as likely as an average segment to have a report within 200 m.
- MassDOT repeating flood sites in the area: 30; 1 have a segment within 150 m at P >= 0.5 (share of all segments at P >= 0.5: 0.1%).

## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 0.99 | Pine Grove Avenue | Bellingham | 0.52 m of water at peak; over 30 cm for 6.0 h; 30 cm reached 18.5 h into the storm; worst hour 25 mm (38% of the storm); a culvert within 100 m is overtopped |
| 2 | 0.98 | Boundary Street | Marlborough | 0.51 m of water at peak; over 30 cm for 20.5 h; 30 cm reached 0.5 h into the storm; worst hour 2 mm (24% of the storm); runoff beside / along the road at 0.7 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.12); a culvert within 100 m is overtopped |
| 3 | 0.98 | Little Tree Lane | Framingham | 0.50 m of water at peak; over 30 cm for 2.0 h; 30 cm reached 1.0 h into the storm; worst hour 2 mm (19% of the storm); a culvert within 100 m is overtopped |
| 4 | 0.95 | Bartlett Street | Northborough | 0.47 m of water at peak; over 30 cm for 1.5 h; 30 cm reached 0.5 h into the storm; worst hour 2 mm (23% of the storm); a culvert within 100 m is overtopped |
| 5 | 0.95 | Paine Street | Bellingham | 0.47 m of water at peak; over 30 cm for 5.5 h; 30 cm reached 19.0 h into the storm; worst hour 25 mm (37% of the storm); a culvert within 100 m is overtopped |
| 6 | 0.95 | (unnamed) | Berlin | 0.46 m of water at peak; over 30 cm for 0.5 h; 30 cm reached 0.5 h into the storm; worst hour 2 mm (25% of the storm); water beside the road 0.42 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 0.9 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.15) |
| 7 | 0.94 | Belknap Road | Framingham | 0.46 m of water at peak; over 30 cm for 0.5 h; 30 cm reached 0.5 h into the storm; worst hour 2 mm (20% of the storm); a culvert within 100 m is overtopped |
| 8 | 0.93 | Route 62 | Berlin | 0.45 m of water at peak; over 30 cm for 0.5 h; 30 cm reached 0.5 h into the storm; worst hour 2 mm (25% of the storm); runoff beside / along the road at 0.6 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.14) |
| 9 | 0.93 | Maple Street | Northborough | 0.44 m of water at peak; over 30 cm for 0.5 h; 30 cm reached 0.5 h into the storm; worst hour 2 mm (24% of the storm); a culvert within 100 m is overtopped |
| 10 | 0.91 | Wrentham Road | Bellingham | 0.44 m of water at peak; over 30 cm for 5.5 h; 30 cm reached 18.5 h into the storm; worst hour 25 mm (37% of the storm); water beside the road 0.15 m below its crest (design freeboard 0.30 m; P 0.85); a culvert within 100 m is overtopped |
| 11 | 0.87 | Water Street | Clinton | 0.41 m of water at peak; over 30 cm for 4.5 h; 30 cm reached 0.5 h into the storm; worst hour 1 mm (22% of the storm) |
| 12 | 0.81 | Knight Road | Framingham | 0.39 m of water at peak; over 30 cm for 2.0 h; 30 cm reached 1.0 h into the storm; worst hour 2 mm (19% of the storm); a culvert within 100 m is overtopped |
| 13 | 0.79 | Ramp-Solomon Pond Rd To Rt 290 Eb | Northborough | 0.38 m of water at peak; over 30 cm for 0.5 h; 30 cm reached 0.5 h into the storm; worst hour 2 mm (24% of the storm); water beside the road 0.53 m above its crest (design freeboard 0.30 m; P 1.00); a culvert within 100 m is overtopped |
| 14 | 0.79 | Ramp-Rt 290 Eb To Solomon Pond Rd Nb | Northborough | 0.38 m of water at peak; over 30 cm for 0.5 h; 30 cm reached 0.5 h into the storm; worst hour 2 mm (24% of the storm); water beside the road 0.37 m below its crest (design freeboard 0.30 m; P 0.32); a culvert within 100 m is overtopped |
| 15 | 0.78 | Belknap Road | Framingham | 0.38 m of water at peak; over 30 cm for 0.5 h; 30 cm reached 0.5 h into the storm; worst hour 2 mm (20% of the storm); a culvert within 100 m is overtopped |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
