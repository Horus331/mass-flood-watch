# Road-closure prototype: aug2023_proto_aug2023_metrowest_20m

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on GPU (cuda)), 20 m grid, storm from 2023-08-08T07:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 6,587 |
| Expected closures (sum of probabilities) | 269.0 |
| Segments with closure probability >= 50% | 236 (171.4 km) |
| Further segments that may close (stream reaches the road crest) | 133 (63.0 km) |
| Culverts overtopped / surcharged | 252 / 2 of 998 |
| Road segments cut off from hospitals | 822 |
| Worst added trip time to a hospital | 37.1 min |
| Heaviest hour of rain | 63.6 mm |
| Flood model run time | 48 s |

## Checks against what happened

- Storm-day flood reports in the area: 5; water >= 10 cm within 100 m of 80% of them, vs 69% of random points (any day).
- Segments flagged impassable are 2.47x as likely as an average segment to have a report within 200 m.
- MassDOT repeating flood sites in the area: 8; 1 have a segment within 150 m at P >= 0.5 (share of all segments at P >= 0.5: 3.6%).

## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 1.00 | (unnamed) | Framingham | 1.82 m of water at peak; over 30 cm for 12.0 h; 30 cm reached 6.5 h into the storm; worst hour 17 mm (26% of the storm); water beside the road 1.55 m above its crest (design freeboard 0.30 m; P 1.00); road sag 2.9 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 16 mm; catchment 15.3 ha) (P 1.00) |
| 2 | 1.00 | Route 30 | Framingham | 0.63 m of water at peak; over 30 cm for 8.5 h; 30 cm reached 8.0 h into the storm; worst hour 30 mm (44% of the storm); a culvert within 100 m is overtopped |
| 3 | 1.00 | Beaver Street | Framingham | 0.76 m of water at peak; over 30 cm for 18.0 h; 30 cm reached 0.5 h into the storm; worst hour 36 mm (47% of the storm); water beside the road 0.07 m below its crest (design freeboard 0.30 m; P 0.94); a culvert within 100 m is overtopped |
| 4 | 1.00 | Route 30 | Framingham | 0.63 m of water at peak; over 30 cm for 8.5 h; 30 cm reached 8.0 h into the storm; worst hour 30 mm (44% of the storm); water beside the road 0.31 m below its crest (design freeboard 0.30 m; P 0.47); a culvert within 100 m is overtopped |
| 5 | 1.00 | Route 135 | Natick | 0.80 m of water at peak; over 30 cm for 17.5 h; 30 cm reached 1.0 h into the storm; worst hour 34 mm (46% of the storm); a culvert within 100 m is overtopped |
| 6 | 1.00 | Route 9 | Framingham | 0.65 m of water at peak; over 30 cm for 5.0 h; 30 cm reached 1.5 h into the storm; worst hour 26 mm (39% of the storm); water beside the road 0.08 m above its crest (design freeboard 0.30 m; P 0.99); a culvert within 100 m is overtopped |
| 7 | 1.00 | Route 9 | Framingham | 0.66 m of water at peak; over 30 cm for 5.0 h; 30 cm reached 1.5 h into the storm; worst hour 25 mm (38% of the storm); a culvert within 100 m is overtopped |
| 8 | 1.00 | Route 30 | Framingham | 0.63 m of water at peak; over 30 cm for 8.5 h; 30 cm reached 8.0 h into the storm; worst hour 30 mm (44% of the storm); a culvert within 100 m is overtopped |
| 9 | 1.00 | Route 30 | Framingham | 0.87 m of water at peak; over 30 cm for 7.5 h; 30 cm reached 0.5 h into the storm; worst hour 23 mm (35% of the storm); a culvert within 100 m is overtopped |
| 10 | 1.00 | Route 126 | Wayland | 6.61 m of water at peak; over 30 cm for 14.5 h; 30 cm reached 0.5 h into the storm; worst hour 36 mm (45% of the storm); water beside the road 6.89 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 0.7 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.21); a culvert within 100 m is overtopped |
| 11 | 1.00 | (unnamed) | Framingham | 0.71 m of water at peak; over 30 cm for 13.5 h; 30 cm reached 0.5 h into the storm; worst hour 29 mm (41% of the storm); water beside the road 0.16 m below its crest (design freeboard 0.30 m; P 0.82); runoff beside / along the road at 1.9 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.87); a culvert within 100 m is overtopped |
| 12 | 1.00 | Irving Street | Framingham | 0.79 m of water at peak; over 30 cm for 18.0 h; 30 cm reached 0.5 h into the storm; worst hour 34 mm (46% of the storm); a culvert within 100 m is overtopped |
| 13 | 1.00 | Salem End Road | Framingham | 0.87 m of water at peak; over 30 cm for 16.0 h; 30 cm reached 1.5 h into the storm; worst hour 26 mm (39% of the storm); a culvert within 100 m is overtopped |
| 14 | 1.00 | Middlesex Street | Millis | 0.68 m of water at peak; over 30 cm for 10.5 h; 30 cm reached 8.0 h into the storm; worst hour 53 mm (59% of the storm) |
| 15 | 1.00 | Route 27 | Sherborn | 1.00 m of water at peak; over 30 cm for 2.0 h; 30 cm reached 0.0 h into the storm; worst hour 42 mm (51% of the storm); a culvert within 100 m is overtopped |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
