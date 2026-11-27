# Road-closure prototype: jul2021_proto_dm_jul2021_vp

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on GPU (cuda)), 20 m grid, storm from 2021-07-09T12:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 45,099 |
| Expected closures (sum of probabilities) | 74.3 |
| Segments with closure probability >= 50% | 6 (5.8 km) |
| Further segments that may close (stream reaches the road crest) | 63 (46.8 km) |
| Culverts overtopped / surcharged | 16 / 4 of 10736 |
| Road segments cut off from hospitals | 20 |
| Worst added trip time to a hospital | 8.5 min |
| Heaviest hour of rain | 13.0 mm |
| Flood model run time | 193 s |

## Checks against what happened

- Storm-day flood reports in the area: 9; water >= 10 cm within 100 m of 11% of them, vs 6% of random points (any day).
- Segments flagged impassable are 103.11x as likely as an average segment to have a report within 200 m.
- MassDOT repeating flood sites in the area: 30; 1 have a segment within 150 m at P >= 0.5 (share of all segments at P >= 0.5: 0.0%).

## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 0.98 | Little Tree Lane | Framingham | 0.50 m of water at peak; over 30 cm for 2.0 h; 30 cm reached 1.0 h into the storm; worst hour 12 mm (36% of the storm); a culvert within 100 m is overtopped |
| 2 | 0.94 | Route 117 | Lancaster | 0.45 m of water at peak; over 30 cm for 14.0 h; 30 cm reached 0.5 h into the storm; worst hour 9 mm (28% of the storm) |
| 3 | 0.84 | Knight Road | Framingham | 0.40 m of water at peak; over 30 cm for 2.0 h; 30 cm reached 1.0 h into the storm; worst hour 12 mm (35% of the storm); a culvert within 100 m is overtopped |
| 4 | 0.76 | Route 9 | Framingham | 0.37 m of water at peak; over 30 cm for 2.5 h; 30 cm reached 2.0 h into the storm; worst hour 12 mm (36% of the storm); a culvert within 100 m is overtopped |
| 5 | 0.76 | Route 9 | Framingham | 0.37 m of water at peak; over 30 cm for 2.5 h; 30 cm reached 2.0 h into the storm; worst hour 12 mm (36% of the storm); a culvert within 100 m is overtopped |
| 6 | 0.52 | Salem End Road | Framingham | 0.31 m of water at peak; over 30 cm for 1.5 h; 30 cm reached 2.5 h into the storm; worst hour 12 mm (36% of the storm); a culvert within 100 m is overtopped |
| 7 | 0.50 | South Street | Berlin | 0.30 m of water at peak; worst hour 11 mm (33% of the storm); a culvert within 100 m is overtopped |
| 8 | 0.43 | Route 30 | Framingham | 0.28 m of water at peak; worst hour 12 mm (36% of the storm); a culvert within 100 m is overtopped |
| 9 | 0.35 | Maple Street | Framingham | 0.26 m of water at peak; worst hour 12 mm (36% of the storm); a culvert within 100 m is overtopped |
| 10 | 0.12 | Boundary Street | Marlborough | 0.18 m of water at peak; worst hour 12 mm (34% of the storm) |
| 11 | 0.09 | Gilboa Street | Douglas | 0.16 m of water at peak; worst hour 11 mm (41% of the storm); water beside the road 0.49 m below its crest (design freeboard 0.30 m; P 0.11); a culvert within 100 m is overtopped |
| 12 | 0.06 | Route 31 | Fitchburg | 0.15 m of water at peak; worst hour 4 mm (26% of the storm) |
| 13 | 0.06 | (unnamed) | Holden | 0.14 m of water at peak; worst hour 8 mm (34% of the storm) |
| 14 | 0.06 | Rivulet Street | Uxbridge | 0.14 m of water at peak; worst hour 11 mm (38% of the storm) |
| 15 | 0.06 | Abbot Mill Lane | Westford | 0.14 m of water at peak; worst hour 8 mm (29% of the storm); water beside the road 0.07 m above its crest (design freeboard 0.30 m; P 0.99) |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
