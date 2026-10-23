# Road-closure prototype: aug2023_loss_aug2023_metrowest_20m

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on CPU (OpenMP)), 20 m grid, storm from 2023-08-08T07:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 6,679 |
| Expected closures (sum of probabilities) | 157.7 |
| Segments with closure probability >= 50% | 121 (92.9 km) |
| Further segments that may close (stream reaches the road crest) | 132 (73.3 km) |
| Culverts overtopped / surcharged | 208 / 1 of 998 |
| Road segments cut off from hospitals | 673 |
| Worst added trip time to a hospital | 26.9 min |
| Heaviest hour of rain | 63.6 mm |
| Flood model run time | 1051 s |

## Checks against what happened

- Storm-day flood reports in the area: 5; water >= 10 cm within 100 m of 80% of them, vs 52% of random points (any day).
- Segments flagged impassable are 3.45x as likely as an average segment to have a report within 200 m.
- MassDOT repeating flood sites in the area: 8; 0 have a segment within 150 m at P >= 0.5 (share of all segments at P >= 0.5: 1.8%).

## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 1.00 | (unnamed) | Framingham | 1.78 m of water at peak; over 30 cm for 11.5 h; 30 cm reached 7.0 h into the storm; worst hour 17 mm (26% of the storm); water beside the road 1.51 m above its crest (design freeboard 0.30 m; P 1.00); fast water: depth x speed 1.19 m2/s (small cars unstable from 0.3); runoff beside / along the road at 1.5 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.50); road sag 2.9 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 16 mm; catchment 15.3 ha) (P 1.00) |
| 2 | 1.00 | Beaver Street | Framingham | 0.69 m of water at peak; over 30 cm for 16.0 h; 30 cm reached 0.5 h into the storm; worst hour 36 mm (47% of the storm); water beside the road 0.09 m below its crest (design freeboard 0.30 m; P 0.92); a culvert within 100 m is overtopped |
| 3 | 1.00 | Route 135 | Natick | 0.71 m of water at peak; over 30 cm for 13.5 h; 30 cm reached 2.5 h into the storm; worst hour 34 mm (46% of the storm); a culvert within 100 m is overtopped |
| 4 | 1.00 | Irving Street | Framingham | 0.71 m of water at peak; over 30 cm for 16.0 h; 30 cm reached 0.5 h into the storm; worst hour 34 mm (46% of the storm); a culvert within 100 m is overtopped |
| 5 | 1.00 | Millwood Street | Framingham | 0.81 m of water at peak; over 30 cm for 8.5 h; 30 cm reached 0.5 h into the storm; worst hour 21 mm (29% of the storm); water beside the road 0.25 m below its crest (design freeboard 0.30 m; P 0.62); a culvert within 100 m is overtopped |
| 6 | 1.00 | Route 126 | Wayland | 0.71 m of water at peak; worst hour 36 mm (45% of the storm); water beside the road 1.19 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 1.0 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.50); a culvert within 100 m is overtopped |
| 7 | 1.00 | (unnamed) | Framingham | 0.62 m of water at peak; over 30 cm for 10.0 h; 30 cm reached 8.5 h into the storm; worst hour 29 mm (41% of the storm); a culvert within 100 m is overtopped |
| 8 | 1.00 | Middlesex Street | Millis | 0.62 m of water at peak; over 30 cm for 10.0 h; 30 cm reached 8.5 h into the storm; worst hour 53 mm (59% of the storm) |
| 9 | 1.00 | Little Tree Lane | Framingham | 0.62 m of water at peak; over 30 cm for 13.0 h; 30 cm reached 1.0 h into the storm; worst hour 22 mm (33% of the storm); a culvert within 100 m is overtopped |
| 10 | 1.00 | Orchard Street | Millis | 0.61 m of water at peak; over 30 cm for 11.0 h; 30 cm reached 7.5 h into the storm; worst hour 49 mm (56% of the storm) |
| 11 | 1.00 | Merchant Road | Framingham | 0.61 m of water at peak; over 30 cm for 10.5 h; 30 cm reached 8.0 h into the storm; worst hour 35 mm (45% of the storm); a culvert within 100 m is overtopped |
| 12 | 1.00 | Queens Way | Framingham | 0.62 m of water at peak; over 30 cm for 10.0 h; 30 cm reached 8.5 h into the storm; worst hour 27 mm (39% of the storm); a culvert within 100 m is overtopped |
| 13 | 1.00 | Nicholas Road | Framingham | 0.60 m of water at peak; over 30 cm for 1.0 h; 30 cm reached 0.5 h into the storm; worst hour 27 mm (37% of the storm); water beside the road 0.41 m above its crest (design freeboard 0.30 m; P 1.00); a culvert within 100 m is overtopped |
| 14 | 1.00 | Wild Meadow Lane | Natick | 0.62 m of water at peak; worst hour 41 mm (57% of the storm); runoff beside / along the road at 1.9 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.15); a culvert within 100 m is overtopped |
| 15 | 1.00 | School Street | Wayland | 0.59 m of water at peak; worst hour 40 mm (54% of the storm); water beside the road 0.33 m above its crest (design freeboard 0.30 m; P 1.00); a culvert within 100 m is overtopped |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
