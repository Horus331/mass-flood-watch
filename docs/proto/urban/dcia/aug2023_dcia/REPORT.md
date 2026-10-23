# Road-closure prototype: aug2023_loss_aug2023_dcia

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on CPU (OpenMP)), 20 m grid, storm from 2023-08-08T07:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 6,587 |
| Expected closures (sum of probabilities) | 181.3 |
| Segments with closure probability >= 50% | 148 (109.1 km) |
| Further segments that may close (stream reaches the road crest) | 134 (71.7 km) |
| Culverts overtopped / surcharged | 225 / 1 of 998 |
| Road segments cut off from hospitals | 754 |
| Worst added trip time to a hospital | 27.1 min |
| Heaviest hour of rain | 63.6 mm |
| Flood model run time | 505 s |

## Checks against what happened

- Storm-day flood reports in the area: 5; water >= 10 cm within 100 m of 60% of them, vs 60% of random points (any day).
- Segments flagged impassable are 3.02x as likely as an average segment to have a report within 200 m.
- MassDOT repeating flood sites in the area: 8; 1 have a segment within 150 m at P >= 0.5 (share of all segments at P >= 0.5: 2.2%).

## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 1.00 | (unnamed) | Framingham | 1.77 m of water at peak; over 30 cm for 13.0 h; 30 cm reached 5.5 h into the storm; worst hour 17 mm (26% of the storm); water beside the road 1.50 m above its crest (design freeboard 0.30 m; P 1.00); fast water: depth x speed 1.12 m2/s (small cars unstable from 0.3); runoff beside / along the road at 4.0 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.75); road sag 2.9 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 16 mm; catchment 15.3 ha) (P 1.00) |
| 2 | 1.00 | Beaver Street | Framingham | 0.77 m of water at peak; over 30 cm for 18.0 h; 30 cm reached 0.5 h into the storm; worst hour 36 mm (47% of the storm); water beside the road 0.06 m below its crest (design freeboard 0.30 m; P 0.95); a culvert within 100 m is overtopped |
| 3 | 1.00 | Route 30 | Framingham | 0.65 m of water at peak; over 30 cm for 7.5 h; 30 cm reached 8.0 h into the storm; worst hour 30 mm (44% of the storm); a culvert within 100 m is overtopped |
| 4 | 1.00 | Route 30 | Framingham | 0.65 m of water at peak; over 30 cm for 7.5 h; 30 cm reached 8.0 h into the storm; worst hour 30 mm (44% of the storm); water beside the road 0.30 m below its crest (design freeboard 0.30 m; P 0.51); a culvert within 100 m is overtopped |
| 5 | 1.00 | Route 135 | Natick | 0.83 m of water at peak; over 30 cm for 16.0 h; 30 cm reached 2.5 h into the storm; worst hour 34 mm (46% of the storm); a culvert within 100 m is overtopped |
| 6 | 1.00 | Route 30 | Framingham | 0.65 m of water at peak; over 30 cm for 7.5 h; 30 cm reached 8.0 h into the storm; worst hour 30 mm (44% of the storm); a culvert within 100 m is overtopped |
| 7 | 1.00 | (unnamed) | Framingham | 0.70 m of water at peak; over 30 cm for 10.5 h; 30 cm reached 8.0 h into the storm; worst hour 29 mm (41% of the storm); water beside the road 0.15 m below its crest (design freeboard 0.30 m; P 0.83); runoff beside / along the road at 1.3 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.16); a culvert within 100 m is overtopped |
| 8 | 1.00 | Irving Street | Framingham | 0.79 m of water at peak; over 30 cm for 18.0 h; 30 cm reached 0.5 h into the storm; worst hour 34 mm (46% of the storm); a culvert within 100 m is overtopped |
| 9 | 1.00 | Little Tree Lane | Framingham | 0.68 m of water at peak; over 30 cm for 12.0 h; 30 cm reached 1.0 h into the storm; worst hour 22 mm (33% of the storm); a culvert within 100 m is overtopped |
| 10 | 1.00 | Millwood Street | Framingham | 0.89 m of water at peak; over 30 cm for 9.0 h; 30 cm reached 0.5 h into the storm; worst hour 21 mm (29% of the storm); water beside the road 0.24 m below its crest (design freeboard 0.30 m; P 0.67); runoff beside / along the road at 2.3 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.19); a culvert within 100 m is overtopped |
| 11 | 1.00 | Merchant Road | Framingham | 0.64 m of water at peak; over 30 cm for 11.0 h; 30 cm reached 7.5 h into the storm; worst hour 35 mm (45% of the storm); water beside the road 0.47 m below its crest (design freeboard 0.30 m; P 0.12); a culvert within 100 m is overtopped |
| 12 | 1.00 | Queens Way | Framingham | 0.70 m of water at peak; over 30 cm for 10.5 h; 30 cm reached 8.0 h into the storm; worst hour 27 mm (39% of the storm); a culvert within 100 m is overtopped |
| 13 | 1.00 | Nicholas Road | Framingham | 0.72 m of water at peak; over 30 cm for 2.5 h; 30 cm reached 0.5 h into the storm; worst hour 27 mm (37% of the storm); water beside the road 0.42 m above its crest (design freeboard 0.30 m; P 1.00); a culvert within 100 m is overtopped |
| 14 | 1.00 | Wild Meadow Lane | Natick | 0.74 m of water at peak; over 30 cm for 0.5 h; 30 cm reached 0.0 h into the storm; worst hour 41 mm (57% of the storm); a culvert within 100 m is overtopped |
| 15 | 1.00 | School Street | Wayland | 1.04 m of water at peak; over 30 cm for 0.5 h; 30 cm reached 0.0 h into the storm; worst hour 40 mm (54% of the storm); water beside the road 0.18 m above its crest (design freeboard 0.30 m; P 1.00); a culvert within 100 m is overtopped |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
