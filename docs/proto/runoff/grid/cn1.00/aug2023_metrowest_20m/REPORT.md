# Road-closure prototype: aug2023_loss_aug2023_metrowest_20m

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on CPU (OpenMP)), 20 m grid, storm from 2023-08-08T07:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 6,679 |
| Expected closures (sum of probabilities) | 191.4 |
| Segments with closure probability >= 50% | 157 (116.4 km) |
| Further segments that may close (stream reaches the road crest) | 169 (94.4 km) |
| Culverts overtopped / surcharged | 253 / 3 of 998 |
| Road segments cut off from hospitals | 882 |
| Worst added trip time to a hospital | 29.7 min |
| Heaviest hour of rain | 63.6 mm |
| Flood model run time | 1688 s |

## Checks against what happened

- Storm-day flood reports in the area: 5; water >= 10 cm within 100 m of 80% of them, vs 66% of random points (any day).
- Segments flagged impassable are 2.77x as likely as an average segment to have a report within 200 m.
- MassDOT repeating flood sites in the area: 8; 1 have a segment within 150 m at P >= 0.5 (share of all segments at P >= 0.5: 2.4%).

## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 1.00 | (unnamed) | Framingham | 1.82 m of water at peak; over 30 cm for 12.0 h; 30 cm reached 6.5 h into the storm; worst hour 17 mm (26% of the storm); water beside the road 1.55 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 1.6 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.35); road sag 2.9 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 16 mm; catchment 15.3 ha) (P 1.00) |
| 2 | 1.00 | Route 30 | Framingham | 0.72 m of water at peak; over 30 cm for 9.0 h; 30 cm reached 8.0 h into the storm; worst hour 30 mm (44% of the storm); a culvert within 100 m is overtopped |
| 3 | 1.00 | Route 30 | Framingham | 0.72 m of water at peak; over 30 cm for 9.0 h; 30 cm reached 8.0 h into the storm; worst hour 30 mm (44% of the storm); water beside the road 0.30 m below its crest (design freeboard 0.30 m; P 0.51); a culvert within 100 m is overtopped |
| 4 | 1.00 | Beaver Street | Framingham | 0.84 m of water at peak; over 30 cm for 17.0 h; 30 cm reached 0.5 h into the storm; worst hour 36 mm (47% of the storm); water beside the road 0.04 m below its crest (design freeboard 0.30 m; P 0.96); a culvert within 100 m is overtopped |
| 5 | 1.00 | Route 135 | Natick | 0.89 m of water at peak; over 30 cm for 15.0 h; 30 cm reached 2.5 h into the storm; worst hour 34 mm (46% of the storm); a culvert within 100 m is overtopped |
| 6 | 1.00 | Route 30 | Framingham | 0.72 m of water at peak; over 30 cm for 9.0 h; 30 cm reached 8.0 h into the storm; worst hour 30 mm (44% of the storm); a culvert within 100 m is overtopped |
| 7 | 1.00 | Speen Street | Framingham | 0.68 m of water at peak; over 30 cm for 9.5 h; 30 cm reached 8.5 h into the storm; worst hour 32 mm (44% of the storm); a culvert within 100 m is overtopped |
| 8 | 1.00 | (unnamed) | Framingham | 0.77 m of water at peak; over 30 cm for 10.0 h; 30 cm reached 8.5 h into the storm; worst hour 29 mm (41% of the storm); water beside the road 0.15 m below its crest (design freeboard 0.30 m; P 0.83); a culvert within 100 m is overtopped |
| 9 | 1.00 | Old Connecticut Path | Framingham | 0.65 m of water at peak; over 30 cm for 10.0 h; 30 cm reached 8.5 h into the storm; worst hour 29 mm (40% of the storm); a culvert within 100 m is overtopped |
| 10 | 1.00 | Irving Street | Framingham | 0.87 m of water at peak; over 30 cm for 17.0 h; 30 cm reached 0.5 h into the storm; worst hour 34 mm (46% of the storm); a culvert within 100 m is overtopped |
| 11 | 1.00 | Middlesex Street | Millis | 0.74 m of water at peak; over 30 cm for 10.5 h; 30 cm reached 8.0 h into the storm; worst hour 53 mm (59% of the storm) |
| 12 | 1.00 | Little Tree Lane | Framingham | 0.70 m of water at peak; over 30 cm for 13.0 h; 30 cm reached 1.0 h into the storm; worst hour 22 mm (33% of the storm); a culvert within 100 m is overtopped |
| 13 | 1.00 | Millwood Street | Framingham | 0.91 m of water at peak; over 30 cm for 9.5 h; 30 cm reached 0.5 h into the storm; worst hour 21 mm (29% of the storm); water beside the road 0.13 m below its crest (design freeboard 0.30 m; P 0.86); a culvert within 100 m is overtopped |
| 14 | 1.00 | Orchard Street | Millis | 0.73 m of water at peak; over 30 cm for 11.0 h; 30 cm reached 7.5 h into the storm; worst hour 49 mm (56% of the storm); culvert (Bogastow Brook): headwater 2.06 m vs road crest 2.41 m, 12.5 m3/s |
| 15 | 1.00 | Merchant Road | Framingham | 0.72 m of water at peak; over 30 cm for 11.0 h; 30 cm reached 7.5 h into the storm; worst hour 35 mm (45% of the storm); water beside the road 0.39 m below its crest (design freeboard 0.30 m; P 0.28); a culvert within 100 m is overtopped |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
