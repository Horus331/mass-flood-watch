# Road-closure prototype: aug2023b_proto_aug2023b_millbury_20m

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on GPU (cuda)), 20 m grid, storm from 2023-08-18T05:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 7,806 |
| Expected closures (sum of probabilities) | 72.8 |
| Segments with closure probability >= 50% | 40 (29.3 km) |
| Further segments that may close (stream reaches the road crest) | 56 (30.7 km) |
| Culverts overtopped / surcharged | 127 / 0 of 1291 |
| Road segments cut off from hospitals | 384 |
| Worst added trip time to a hospital | 17.3 min |
| Heaviest hour of rain | 47.2 mm |
| Flood model run time | 46 s |

## Checks against what happened

- Storm-day flood reports in the area: 0; water >= 10 cm within 100 m of 0% of them, vs 36% of random points (any day).
- MassDOT repeating flood sites in the area: 8; 0 have a segment within 150 m at P >= 0.5 (share of all segments at P >= 0.5: 0.5%).

## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 1.00 | Martin Luther King Jr Boulevard | Worcester | 3.00 m of water at peak; over 30 cm for 18.0 h; 30 cm reached 0.5 h into the storm; worst hour 21 mm (71% of the storm); water beside the road 2.92 m above its crest (design freeboard 0.30 m; P 1.00); road sag 3.2 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 21 mm; catchment 60.2 ha) (P 1.00); a culvert within 100 m is overtopped |
| 2 | 1.00 | Martin Luther King Jr Boulevard | Worcester | 2.30 m of water at peak; over 30 cm for 18.0 h; 30 cm reached 0.5 h into the storm; worst hour 21 mm (71% of the storm); water beside the road 1.97 m above its crest (design freeboard 0.30 m; P 1.00); road sag 3.2 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 21 mm; catchment 60.2 ha) (P 1.00); a culvert within 100 m is overtopped |
| 3 | 1.00 | Foster Street | Worcester | 1.27 m of water at peak; over 30 cm for 18.0 h; 30 cm reached 0.5 h into the storm; worst hour 22 mm (72% of the storm); water beside the road 0.03 m below its crest (design freeboard 0.30 m; P 0.96); runoff beside / along the road at 1.2 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.10); road sag 0.7 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 22 mm; catchment 22.1 ha) (P 0.80); a culvert within 100 m is overtopped |
| 4 | 1.00 | Foster Street | Worcester | 1.27 m of water at peak; over 30 cm for 18.0 h; 30 cm reached 0.5 h into the storm; worst hour 22 mm (72% of the storm); water beside the road 0.42 m above its crest (design freeboard 0.30 m; P 1.00); fast water: depth x speed 0.24 m2/s (small cars unstable from 0.3); runoff beside / along the road at 2.4 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.79); road sag 0.7 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 22 mm; catchment 22.1 ha) (P 0.80); a culvert within 100 m is overtopped |
| 5 | 1.00 | Providence Street | Millbury | 2.15 m of water at peak; over 30 cm for 18.0 h; 30 cm reached 0.5 h into the storm; worst hour 35 mm (69% of the storm); a culvert within 100 m is overtopped |
| 6 | 1.00 | Stafford Street | Worcester | 1.23 m of water at peak; over 30 cm for 5.0 h; 30 cm reached 0.5 h into the storm; worst hour 25 mm (82% of the storm); water beside the road 0.09 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.4 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 24 mm; catchment 16.0 ha) (P 0.20); a culvert within 100 m is overtopped |
| 7 | 1.00 | Millbury Street | Grafton | 0.69 m of water at peak; over 30 cm for 14.0 h; 30 cm reached 0.5 h into the storm; worst hour 37 mm (68% of the storm); runoff beside / along the road at 1.2 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.56) |
| 8 | 1.00 | James Street | Worcester | 0.72 m of water at peak; over 30 cm for 2.5 h; 30 cm reached 0.5 h into the storm; worst hour 25 mm (83% of the storm); a culvert within 100 m is overtopped |
| 9 | 1.00 | Ludlow Street | Worcester | 1.23 m of water at peak; over 30 cm for 5.0 h; 30 cm reached 0.5 h into the storm; worst hour 24 mm (83% of the storm); a culvert within 100 m is overtopped |
| 10 | 1.00 | (unnamed) | Worcester | 2.21 m of water at peak; over 30 cm for 17.0 h; 30 cm reached 1.5 h into the storm; worst hour 21 mm (65% of the storm); a culvert within 100 m is overtopped |
| 11 | 1.00 | Grafton Street | Millbury | 0.83 m of water at peak; over 30 cm for 1.0 h; 30 cm reached 1.5 h into the storm; worst hour 34 mm (68% of the storm); a culvert within 100 m is overtopped |
| 12 | 1.00 | East Park Terrace | Worcester | 0.67 m of water at peak; over 30 cm for 8.5 h; 30 cm reached 10.0 h into the storm; worst hour 22 mm (65% of the storm); water beside the road 0.57 m above its crest (design freeboard 0.30 m; P 1.00); road sag 4.3 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 22 mm; catchment 127.8 ha) (P 1.00) |
| 13 | 1.00 | Hampton Street | Auburn | 3.08 m of water at peak; worst hour 30 mm (82% of the storm); water beside the road 1.63 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 4.5 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.90); a culvert within 100 m is overtopped |
| 14 | 1.00 | Route 12 | Auburn | 2.09 m of water at peak; worst hour 30 mm (82% of the storm); water beside the road 3.66 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 4.5 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.90); a culvert within 100 m is overtopped |
| 15 | 1.00 | Cataract Street | Worcester | 0.63 m of water at peak; worst hour 23 mm (78% of the storm) |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
