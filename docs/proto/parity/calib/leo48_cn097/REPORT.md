# Road-closure prototype: sep2023_loss_leo48_cn097

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on CPU (OpenMP)), 20 m grid, storm from 2023-09-11T16:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 5,183 |
| Expected closures (sum of probabilities) | 172.5 |
| Segments with closure probability >= 50% | 143 (93.9 km) |
| Further segments that may close (stream reaches the road crest) | 194 (119.8 km) |
| Culverts overtopped / surcharged | 143 / 6 of 713 |
| Road segments cut off from hospitals | 814 |
| Worst added trip time to a hospital | 25.8 min |
| Heaviest hour of rain | 89.3 mm |
| Flood model run time | 2852 s |

## Checks against what happened

- Storm-day flood reports in the area: 10; water >= 10 cm within 100 m of 100% of them, vs 74% of random points (any day).
- Segments flagged impassable are 3.23x as likely as an average segment to have a report within 200 m.
- MassDOT repeating flood sites in the area: 4; 2 have a segment within 150 m at P >= 0.5 (share of all segments at P >= 0.5: 2.8%).

## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 1.00 | Route 2 | Leominster | 10.63 m of water at peak; over 30 cm for 43.0 h; 30 cm reached 5.5 h into the storm; worst hour 67 mm (40% of the storm); runoff beside / along the road at 2.5 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.84); a culvert within 100 m is overtopped |
| 2 | 1.00 | (unnamed) | Leominster | 1.73 m of water at peak; over 30 cm for 29.5 h; 30 cm reached 5.5 h into the storm; worst hour 84 mm (43% of the storm); water beside the road 0.06 m above its crest (design freeboard 0.30 m; P 0.99); a culvert within 100 m is overtopped |
| 3 | 1.00 | Depot Street | Fitchburg | 1.33 m of water at peak; over 30 cm for 30.5 h; 30 cm reached 0.5 h into the storm; worst hour 31 mm (29% of the storm); runoff beside / along the road at 1.5 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.56); a culvert within 100 m is overtopped |
| 4 | 1.00 | Water Street | Leominster | 1.74 m of water at peak; over 30 cm for 29.5 h; 30 cm reached 5.5 h into the storm; worst hour 85 mm (43% of the storm); a culvert within 100 m is overtopped |
| 5 | 1.00 | Litchfield Street | Leominster | 1.88 m of water at peak; over 30 cm for 15.0 h; 30 cm reached 6.0 h into the storm; worst hour 66 mm (41% of the storm); a culvert within 100 m is overtopped |
| 6 | 1.00 | Route 12 | Leominster | 1.02 m of water at peak; over 30 cm for 8.5 h; 30 cm reached 6.0 h into the storm; worst hour 78 mm (43% of the storm); water beside the road 0.53 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 0.9 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.20); a culvert within 100 m is overtopped |
| 7 | 1.00 | Route 117 | Leominster | 1.19 m of water at peak; over 30 cm for 9.5 h; 30 cm reached 6.5 h into the storm; worst hour 59 mm (39% of the storm); cut off from hospitals |
| 8 | 1.00 | Route 117 | Leominster | 1.19 m of water at peak; over 30 cm for 9.5 h; 30 cm reached 6.5 h into the storm; worst hour 61 mm (39% of the storm); water beside the road 0.05 m below its crest (design freeboard 0.30 m; P 0.95); runoff beside / along the road at 1.5 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.42); a culvert within 100 m is overtopped |
| 9 | 1.00 | Route 12 | Leominster | 0.92 m of water at peak; over 30 cm for 6.0 h; 30 cm reached 6.0 h into the storm; worst hour 85 mm (43% of the storm); water beside the road 0.19 m above its crest (design freeboard 0.30 m; P 1.00); a culvert within 100 m is overtopped |
| 10 | 1.00 | Route 70 | Lancaster | 1.76 m of water at peak; over 30 cm for 9.5 h; 30 cm reached 8.5 h into the storm; worst hour 24 mm (34% of the storm); a culvert within 100 m is overtopped |
| 11 | 1.00 | Route 70 | Lancaster | 1.76 m of water at peak; over 30 cm for 9.5 h; 30 cm reached 8.5 h into the storm; worst hour 25 mm (35% of the storm); runoff beside / along the road at 2.1 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.54); a culvert within 100 m is overtopped |
| 12 | 1.00 | Merriam Avenue | Leominster | 0.83 m of water at peak; over 30 cm for 5.0 h; 30 cm reached 5.5 h into the storm; worst hour 84 mm (44% of the storm); water beside the road 0.64 m above its crest (design freeboard 0.30 m; P 1.00); fast water: depth x speed 0.27 m2/s (small cars unstable from 0.3); runoff beside / along the road at 1.2 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.64); road sag 0.4 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 81 mm; catchment 13.0 ha) (P 1.00) |
| 13 | 1.00 | Route 140 | Princeton | 0.89 m of water at peak; over 30 cm for 9.0 h; 30 cm reached 7.0 h into the storm; worst hour 42 mm (28% of the storm); water beside the road 0.21 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 2.2 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.58); a culvert within 100 m is overtopped |
| 14 | 1.00 | Catacunemaug Road | Shirley | 0.87 m of water at peak; over 30 cm for 37.0 h; 30 cm reached 9.0 h into the storm; worst hour 40 mm (37% of the storm); water beside the road 0.48 m below its crest (design freeboard 0.30 m; P 0.12); a culvert within 100 m is overtopped |
| 15 | 1.00 | Kingman Drive | Leominster | 1.30 m of water at peak; over 30 cm for 15.5 h; 30 cm reached 5.5 h into the storm; worst hour 85 mm (44% of the storm); water beside the road 0.54 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 1.8 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.88); a culvert within 100 m is overtopped |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
