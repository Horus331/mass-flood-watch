# Road-closure prototype: aug2023_loss_aug2023_metrowest_20m

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on CPU (OpenMP)), 20 m grid, storm from 2023-08-08T07:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 6,679 |
| Expected closures (sum of probabilities) | 119.2 |
| Segments with closure probability >= 50% | 95 (75.9 km) |
| Further segments that may close (stream reaches the road crest) | 83 (46.1 km) |
| Culverts overtopped / surcharged | 154 / 1 of 998 |
| Road segments cut off from hospitals | 490 |
| Worst added trip time to a hospital | 23.9 min |
| Heaviest hour of rain | 63.6 mm |
| Flood model run time | 1573 s |

## Checks against what happened

- Storm-day flood reports in the area: 5; water >= 10 cm within 100 m of 20% of them, vs 35% of random points (any day).
- Segments flagged impassable are 4.97x as likely as an average segment to have a report within 200 m.
- MassDOT repeating flood sites in the area: 8; 2 have a segment within 150 m at P >= 0.5 (share of all segments at P >= 0.5: 1.4%).

## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 1.00 | (unnamed) | Framingham | 1.34 m of water at peak; over 30 cm for 10.5 h; 30 cm reached 8.0 h into the storm; worst hour 17 mm (26% of the storm); water beside the road 1.07 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 1.1 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.54); road sag 2.9 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 16 mm; catchment 15.3 ha) (P 1.00) |
| 2 | 1.00 | Coolidge Street | Sherborn | 0.80 m of water at peak; over 30 cm for 18.0 h; 30 cm reached 0.5 h into the storm; worst hour 37 mm (46% of the storm); a culvert within 100 m is overtopped |
| 3 | 1.00 | Cottage Street | Natick | 0.78 m of water at peak; over 30 cm for 13.5 h; 30 cm reached 0.5 h into the storm; worst hour 40 mm (61% of the storm); a culvert within 100 m is overtopped |
| 4 | 1.00 | (unnamed) | Natick | 0.77 m of water at peak; over 30 cm for 18.0 h; 30 cm reached 0.5 h into the storm; worst hour 41 mm (56% of the storm); culvert (Indian Brook): headwater 4.91 m vs road crest 1.22 m, 1.9 m3/s |
| 5 | 1.00 | Route 126 | Wayland | 0.72 m of water at peak; worst hour 36 mm (45% of the storm); water beside the road 1.15 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 0.7 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.25); a culvert within 100 m is overtopped |
| 6 | 1.00 | Irving Street | Framingham | 0.61 m of water at peak; over 30 cm for 17.0 h; 30 cm reached 0.5 h into the storm; worst hour 34 mm (46% of the storm); a culvert within 100 m is overtopped |
| 7 | 1.00 | (unnamed) | Framingham | 0.60 m of water at peak; over 30 cm for 1.0 h; 30 cm reached 0.5 h into the storm; worst hour 26 mm (38% of the storm); water beside the road 0.33 m below its crest (design freeboard 0.30 m; P 0.41); a culvert within 100 m is overtopped |
| 8 | 1.00 | Wild Meadow Lane | Natick | 0.60 m of water at peak; worst hour 41 mm (57% of the storm); a culvert within 100 m is overtopped |
| 9 | 1.00 | (unnamed) | Framingham | 0.59 m of water at peak; worst hour 25 mm (36% of the storm); water beside the road 2.31 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 2.2 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.96); a culvert within 100 m is overtopped |
| 10 | 1.00 | School Street | Wayland | 0.59 m of water at peak; worst hour 40 mm (54% of the storm); water beside the road 0.33 m above its crest (design freeboard 0.30 m; P 1.00); a culvert within 100 m is overtopped |
| 11 | 1.00 | Beaver Street | Framingham | 0.57 m of water at peak; over 30 cm for 16.0 h; 30 cm reached 0.5 h into the storm; worst hour 36 mm (47% of the storm); water beside the road 0.11 m below its crest (design freeboard 0.30 m; P 0.89); a culvert within 100 m is overtopped |
| 12 | 0.99 | Route 135 | Natick | 0.56 m of water at peak; over 30 cm for 14.0 h; 30 cm reached 1.5 h into the storm; worst hour 34 mm (46% of the storm); a culvert within 100 m is overtopped |
| 13 | 0.99 | Little Tree Lane | Framingham | 0.56 m of water at peak; over 30 cm for 6.0 h; 30 cm reached 1.0 h into the storm; worst hour 22 mm (33% of the storm); a culvert within 100 m is overtopped |
| 14 | 0.99 | Route 126 | Framingham | 0.55 m of water at peak; over 30 cm for 2.5 h; 30 cm reached 0.5 h into the storm; worst hour 32 mm (46% of the storm); a culvert within 100 m is overtopped |
| 15 | 0.99 | Water Street | Framingham | 0.54 m of water at peak; over 30 cm for 1.0 h; 30 cm reached 0.5 h into the storm; worst hour 27 mm (38% of the storm); water beside the road 0.24 m below its crest (design freeboard 0.30 m; P 0.66); a culvert within 100 m is overtopped |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
