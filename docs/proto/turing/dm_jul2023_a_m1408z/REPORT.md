# Road-closure prototype: jul2023_proto_dm_jul2023_a_m1408z

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on GPU (cuda)), 20 m grid, storm from 2023-07-14T08:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 45,099 |
| Expected closures (sum of probabilities) | 76.7 |
| Segments with closure probability >= 50% | 7 (6.8 km) |
| Further segments that may close (stream reaches the road crest) | 66 (48.5 km) |
| Culverts overtopped / surcharged | 22 / 4 of 10736 |
| Road segments cut off from hospitals | 26 |
| Worst added trip time to a hospital | 8.6 min |
| Heaviest hour of rain | 27.8 mm |
| Flood model run time | 224 s |

## Checks against what happened

- Storm-day flood reports in the area: 4; water >= 10 cm within 100 m of 0% of them, vs 6% of random points (any day).
- Segments flagged impassable are 0.0x as likely as an average segment to have a report within 200 m.
- MassDOT repeating flood sites in the area: 30; 1 have a segment within 150 m at P >= 0.5 (share of all segments at P >= 0.5: 0.0%).

## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 0.98 | Little Tree Lane | Framingham | 0.51 m of water at peak; over 30 cm for 2.0 h; 30 cm reached 1.0 h into the storm; worst hour 12 mm (47% of the storm); a culvert within 100 m is overtopped |
| 2 | 0.85 | Knight Road | Framingham | 0.40 m of water at peak; over 30 cm for 2.0 h; 30 cm reached 1.0 h into the storm; worst hour 12 mm (47% of the storm); a culvert within 100 m is overtopped |
| 3 | 0.84 | Route 117 | Lancaster | 0.40 m of water at peak; over 30 cm for 18.0 h; 30 cm reached 0.5 h into the storm; worst hour 9 mm (48% of the storm) |
| 4 | 0.78 | Route 9 | Framingham | 0.38 m of water at peak; over 30 cm for 2.5 h; 30 cm reached 2.0 h into the storm; worst hour 12 mm (46% of the storm); a culvert within 100 m is overtopped |
| 5 | 0.78 | Route 9 | Framingham | 0.38 m of water at peak; over 30 cm for 2.5 h; 30 cm reached 2.0 h into the storm; worst hour 12 mm (46% of the storm); a culvert within 100 m is overtopped |
| 6 | 0.60 | South Street | Berlin | 0.33 m of water at peak; over 30 cm for 5.0 h; 30 cm reached 1.0 h into the storm; worst hour 13 mm (46% of the storm); a culvert within 100 m is overtopped |
| 7 | 0.55 | Salem End Road | Framingham | 0.31 m of water at peak; over 30 cm for 1.5 h; 30 cm reached 2.5 h into the storm; worst hour 12 mm (46% of the storm); a culvert within 100 m is overtopped |
| 8 | 0.44 | Route 30 | Framingham | 0.28 m of water at peak; worst hour 12 mm (47% of the storm); a culvert within 100 m is overtopped |
| 9 | 0.40 | East Park Terrace | Worcester | 0.27 m of water at peak; worst hour 14 mm (47% of the storm); water beside the road 0.17 m above its crest (design freeboard 0.30 m; P 1.00); road sag 4.3 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 14 mm; catchment 127.8 ha) (P 0.40) |
| 10 | 0.37 | Maple Street | Framingham | 0.27 m of water at peak; worst hour 11 mm (46% of the storm); a culvert within 100 m is overtopped |
| 11 | 0.27 | Ash Street | Clinton | 0.24 m of water at peak; worst hour 11 mm (47% of the storm); water beside the road 0.02 m above its crest (design freeboard 0.30 m; P 0.98) |
| 12 | 0.16 | Boundary Street | Marlborough | 0.20 m of water at peak; worst hour 13 mm (46% of the storm); runoff beside / along the road at 0.7 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.12) |
| 13 | 0.10 | Gilboa Street | Douglas | 0.17 m of water at peak; worst hour 28 mm (74% of the storm); water beside the road 0.49 m below its crest (design freeboard 0.30 m; P 0.11); a culvert within 100 m is overtopped |
| 14 | 0.08 | Sycamore Street | Millbury | 0.16 m of water at peak; worst hour 20 mm (61% of the storm); a culvert within 100 m is overtopped |
| 15 | 0.08 | Cambridge Street | Worcester | 0.16 m of water at peak; worst hour 15 mm (50% of the storm); water beside the road 0.02 m above its crest (design freeboard 0.30 m; P 0.98) |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
