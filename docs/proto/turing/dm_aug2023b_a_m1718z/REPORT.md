# Road-closure prototype: aug2023b_proto_dm_aug2023b_a_m1718z

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on GPU (cuda)), 20 m grid, storm from 2023-08-17T18:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 45,099 |
| Expected closures (sum of probabilities) | 177.6 |
| Segments with closure probability >= 50% | 57 (42.7 km) |
| Further segments that may close (stream reaches the road crest) | 126 (86.8 km) |
| Culverts overtopped / surcharged | 223 / 4 of 10736 |
| Road segments cut off from hospitals | 869 |
| Worst added trip time to a hospital | 28.0 min |
| Heaviest hour of rain | 46.4 mm |
| Flood model run time | 263 s |

## Checks against what happened

- Storm-day flood reports in the area: 3; water >= 10 cm within 100 m of 0% of them, vs 20% of random points (any day).
- Segments flagged impassable are 0.0x as likely as an average segment to have a report within 200 m.
- MassDOT repeating flood sites in the area: 30; 1 have a segment within 150 m at P >= 0.5 (share of all segments at P >= 0.5: 0.1%).

## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 1.00 | Wrentham Road | Bellingham | 0.72 m of water at peak; over 30 cm for 7.5 h; 30 cm reached 22.0 h into the storm; worst hour 41 mm (43% of the storm); water beside the road 0.13 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.9 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 41 mm; catchment 171.4 ha) (P 0.86); a culvert within 100 m is overtopped |
| 2 | 1.00 | Paine Street | Bellingham | 0.91 m of water at peak; over 30 cm for 7.0 h; 30 cm reached 22.5 h into the storm; worst hour 41 mm (43% of the storm); a culvert within 100 m is overtopped |
| 3 | 1.00 | Pine Grove Avenue | Bellingham | 0.95 m of water at peak; over 30 cm for 7.0 h; 30 cm reached 22.5 h into the storm; worst hour 41 mm (43% of the storm); water beside the road 0.35 m below its crest (design freeboard 0.30 m; P 0.36); a culvert within 100 m is overtopped |
| 4 | 1.00 | Ash Street | Clinton | 0.63 m of water at peak; over 30 cm for 3.5 h; 30 cm reached 26.0 h into the storm; worst hour 20 mm (49% of the storm); water beside the road 0.42 m above its crest (design freeboard 0.30 m; P 1.00) |
| 5 | 1.00 | East Park Terrace | Worcester | 0.59 m of water at peak; over 30 cm for 7.5 h; 30 cm reached 22.0 h into the storm; worst hour 21 mm (50% of the storm); water beside the road 0.49 m above its crest (design freeboard 0.30 m; P 1.00); road sag 4.3 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 21 mm; catchment 127.8 ha) (P 1.00) |
| 6 | 1.00 | (unnamed) | Blackstone | 0.58 m of water at peak; over 30 cm for 7.0 h; 30 cm reached 22.5 h into the storm; worst hour 39 mm (44% of the storm); a culvert within 100 m is overtopped |
| 7 | 0.99 | Wrentham Road | Bellingham | 0.53 m of water at peak; over 30 cm for 2.5 h; 30 cm reached 22.0 h into the storm; worst hour 42 mm (43% of the storm); a culvert within 100 m is overtopped |
| 8 | 0.99 | Boundary Street | Marlborough | 0.53 m of water at peak; over 30 cm for 29.0 h; 30 cm reached 0.5 h into the storm; worst hour 20 mm (54% of the storm); runoff beside / along the road at 0.7 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.12); a culvert within 100 m is overtopped |
| 9 | 0.99 | (unnamed) | Bellingham | 0.53 m of water at peak; over 30 cm for 2.5 h; 30 cm reached 22.0 h into the storm; worst hour 42 mm (43% of the storm); a culvert within 100 m is overtopped |
| 10 | 0.99 | Cemetery Street | Mendon | 0.52 m of water at peak; over 30 cm for 4.0 h; 30 cm reached 23.5 h into the storm; worst hour 35 mm (43% of the storm); a culvert within 100 m is overtopped |
| 11 | 0.99 | Bellingham Street | Mendon | 0.52 m of water at peak; over 30 cm for 5.0 h; 30 cm reached 24.0 h into the storm; worst hour 37 mm (45% of the storm); a culvert within 100 m is overtopped |
| 12 | 0.98 | West Street | Wrentham | 0.50 m of water at peak; over 30 cm for 2.5 h; 30 cm reached 22.0 h into the storm; worst hour 42 mm (42% of the storm); runoff beside / along the road at 0.9 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.42); a culvert within 100 m is overtopped |
| 13 | 0.98 | Little Tree Lane | Framingham | 0.50 m of water at peak; over 30 cm for 2.0 h; 30 cm reached 1.0 h into the storm; worst hour 19 mm (45% of the storm); a culvert within 100 m is overtopped |
| 14 | 0.96 | Bartlett Street | Northborough | 0.48 m of water at peak; over 30 cm for 1.5 h; 30 cm reached 0.5 h into the storm; worst hour 20 mm (54% of the storm); a culvert within 100 m is overtopped |
| 15 | 0.95 | (unnamed) | Berlin | 0.46 m of water at peak; over 30 cm for 0.5 h; 30 cm reached 0.5 h into the storm; worst hour 21 mm (53% of the storm); water beside the road 0.42 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 0.9 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.15) |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
