# Road-closure prototype: aug2026_proto_dm_aug2026_vp

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on GPU (cuda)), 20 m grid, storm from 2026-08-03T06:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 45,099 |
| Expected closures (sum of probabilities) | 78.5 |
| Segments with closure probability >= 50% | 7 (6.0 km) |
| Further segments that may close (stream reaches the road crest) | 71 (52.8 km) |
| Culverts overtopped / surcharged | 16 / 4 of 10736 |
| Road segments cut off from hospitals | 23 |
| Worst added trip time to a hospital | 8.4 min |
| Heaviest hour of rain | 19.4 mm |
| Flood model run time | 229 s |

## Checks against what happened

- Storm-day flood reports in the area: 3; water >= 10 cm within 100 m of 0% of them, vs 6% of random points (any day).
- Segments flagged impassable are 0.0x as likely as an average segment to have a report within 200 m.
- MassDOT repeating flood sites in the area: 30; 1 have a segment within 150 m at P >= 0.5 (share of all segments at P >= 0.5: 0.0%).

## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 0.98 | Route 117 | Lancaster | 0.50 m of water at peak; over 30 cm for 16.0 h; 30 cm reached 0.5 h into the storm; worst hour 12 mm (24% of the storm) |
| 2 | 0.98 | Little Tree Lane | Framingham | 0.50 m of water at peak; over 30 cm for 2.0 h; 30 cm reached 1.0 h into the storm; worst hour 10 mm (28% of the storm); a culvert within 100 m is overtopped |
| 3 | 0.84 | Knight Road | Framingham | 0.40 m of water at peak; over 30 cm for 2.0 h; 30 cm reached 1.0 h into the storm; worst hour 10 mm (28% of the storm); a culvert within 100 m is overtopped |
| 4 | 0.83 | East Park Terrace | Worcester | 0.40 m of water at peak; over 30 cm for 3.5 h; 30 cm reached 13.0 h into the storm; worst hour 13 mm (25% of the storm); water beside the road 0.30 m above its crest (design freeboard 0.30 m; P 1.00); road sag 4.3 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 13 mm; catchment 127.8 ha) (P 0.84) |
| 5 | 0.75 | Route 9 | Framingham | 0.37 m of water at peak; over 30 cm for 2.0 h; 30 cm reached 2.0 h into the storm; worst hour 10 mm (28% of the storm); a culvert within 100 m is overtopped |
| 6 | 0.75 | Route 9 | Framingham | 0.37 m of water at peak; over 30 cm for 2.0 h; 30 cm reached 2.0 h into the storm; worst hour 10 mm (28% of the storm); a culvert within 100 m is overtopped |
| 7 | 0.52 | Salem End Road | Framingham | 0.30 m of water at peak; over 30 cm for 1.5 h; 30 cm reached 2.5 h into the storm; worst hour 10 mm (28% of the storm); a culvert within 100 m is overtopped |
| 8 | 0.43 | South Street | Berlin | 0.28 m of water at peak; worst hour 12 mm (27% of the storm); a culvert within 100 m is overtopped |
| 9 | 0.42 | Route 30 | Framingham | 0.28 m of water at peak; worst hour 10 mm (28% of the storm); a culvert within 100 m is overtopped |
| 10 | 0.34 | Maple Street | Framingham | 0.26 m of water at peak; worst hour 10 mm (28% of the storm); a culvert within 100 m is overtopped |
| 11 | 0.17 | Coolidge Road | Worcester | 0.21 m of water at peak; worst hour 13 mm (24% of the storm); water beside the road 0.21 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.7 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 13 mm; catchment 17.7 ha) (P 0.75) |
| 12 | 0.17 | Cambridge Street | Worcester | 0.20 m of water at peak; worst hour 13 mm (24% of the storm); water beside the road 0.06 m above its crest (design freeboard 0.30 m; P 0.99); road sag 2.0 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 13 mm; catchment 77.2 ha) (P 0.17) |
| 13 | 0.14 | Kinnicutt Road | Worcester | 0.19 m of water at peak; worst hour 13 mm (24% of the storm); water beside the road 0.09 m above its crest (design freeboard 0.30 m; P 0.99) |
| 14 | 0.11 | (unnamed) | Holden | 0.18 m of water at peak; worst hour 13 mm (24% of the storm); a culvert within 100 m is overtopped |
| 15 | 0.11 | Boundary Street | Marlborough | 0.18 m of water at peak; worst hour 12 mm (27% of the storm) |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
