# Road-closure prototype: jul2023_proto_dm_jul2023_ref

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on GPU (cuda)), 20 m grid, storm from 2023-07-14T08:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 45,099 |
| Expected closures (sum of probabilities) | 73.7 |
| Segments with closure probability >= 50% | 6 (5.8 km) |
| Further segments that may close (stream reaches the road crest) | 63 (46.8 km) |
| Culverts overtopped / surcharged | 16 / 4 of 10736 |
| Road segments cut off from hospitals | 16 |
| Worst added trip time to a hospital | 8.5 min |
| Heaviest hour of rain | 35.6 mm |
| Flood model run time | 228 s |

## Checks against what happened

- Storm-day flood reports in the area: 4; water >= 10 cm within 100 m of 0% of them, vs 6% of random points (any day).
- Segments flagged impassable are 0.0x as likely as an average segment to have a report within 200 m.
- MassDOT repeating flood sites in the area: 30; 1 have a segment within 150 m at P >= 0.5 (share of all segments at P >= 0.5: 0.0%).

## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 0.98 | Little Tree Lane | Framingham | 0.50 m of water at peak; over 30 cm for 2.0 h; 30 cm reached 1.0 h into the storm; worst hour 2 mm (41% of the storm); a culvert within 100 m is overtopped |
| 2 | 0.96 | Route 117 | Lancaster | 0.47 m of water at peak; over 30 cm for 18.0 h; 30 cm reached 0.5 h into the storm; worst hour 19 mm (83% of the storm) |
| 3 | 0.84 | Knight Road | Framingham | 0.40 m of water at peak; over 30 cm for 2.0 h; 30 cm reached 1.0 h into the storm; worst hour 3 mm (45% of the storm); a culvert within 100 m is overtopped |
| 4 | 0.75 | Route 9 | Framingham | 0.37 m of water at peak; over 30 cm for 2.0 h; 30 cm reached 2.0 h into the storm; worst hour 2 mm (50% of the storm); a culvert within 100 m is overtopped |
| 5 | 0.75 | Route 9 | Framingham | 0.37 m of water at peak; over 30 cm for 2.0 h; 30 cm reached 2.0 h into the storm; worst hour 2 mm (49% of the storm); a culvert within 100 m is overtopped |
| 6 | 0.52 | Salem End Road | Framingham | 0.30 m of water at peak; over 30 cm for 1.5 h; 30 cm reached 2.5 h into the storm; worst hour 2 mm (52% of the storm); a culvert within 100 m is overtopped |
| 7 | 0.45 | South Street | Berlin | 0.29 m of water at peak; worst hour 13 mm (60% of the storm); a culvert within 100 m is overtopped |
| 8 | 0.42 | Route 30 | Framingham | 0.28 m of water at peak; worst hour 2 mm (43% of the storm); a culvert within 100 m is overtopped |
| 9 | 0.34 | Maple Street | Framingham | 0.26 m of water at peak; worst hour 2 mm (56% of the storm); a culvert within 100 m is overtopped |
| 10 | 0.12 | (unnamed) | Holden | 0.18 m of water at peak; worst hour 25 mm (92% of the storm); a culvert within 100 m is overtopped |
| 11 | 0.11 | Boundary Street | Marlborough | 0.18 m of water at peak; worst hour 15 mm (61% of the storm); runoff beside / along the road at 0.6 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.10) |
| 12 | 0.06 | Route 31 | Fitchburg | 0.15 m of water at peak; worst hour 0 mm (100% of the storm) |
| 13 | 0.06 | Abbot Mill Lane | Westford | 0.14 m of water at peak; worst hour 21 mm (60% of the storm); water beside the road 0.10 m above its crest (design freeboard 0.30 m; P 1.00) |
| 14 | 0.05 | Brook Street | Framingham | 0.13 m of water at peak; worst hour 2 mm (41% of the storm) |
| 15 | 0.04 | Ayer Road | Shirley | 0.13 m of water at peak; worst hour 34 mm (94% of the storm) |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
