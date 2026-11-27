# Road-closure prototype: aug2026_proto_dm_aug2026_a_m0304z

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on GPU (cuda)), 20 m grid, storm from 2026-08-03T04:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 45,099 |
| Expected closures (sum of probabilities) | 356.6 |
| Segments with closure probability >= 50% | 180 (141.7 km) |
| Further segments that may close (stream reaches the road crest) | 335 (240.9 km) |
| Culverts overtopped / surcharged | 560 / 10 of 10736 |
| Road segments cut off from hospitals | 2469 |
| Worst added trip time to a hospital | 59.7 min |
| Heaviest hour of rain | 34.9 mm |
| Flood model run time | 259 s |

## Checks against what happened

- Storm-day flood reports in the area: 3; water >= 10 cm within 100 m of 67% of them, vs 19% of random points (any day).
- Segments flagged impassable are 7.42x as likely as an average segment to have a report within 200 m.
- MassDOT repeating flood sites in the area: 30; 2 have a segment within 150 m at P >= 0.5 (share of all segments at P >= 0.5: 0.4%).

## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 1.00 | Route 117 | Lancaster | 1.27 m of water at peak; over 30 cm for 18.0 h; 30 cm reached 0.5 h into the storm; worst hour 19 mm (25% of the storm); culvert (Trib to Still River): headwater 5.48 m vs road crest 2.74 m, 28.7 m3/s |
| 2 | 1.00 | (unnamed) | Leominster | 0.69 m of water at peak; over 30 cm for 9.5 h; 30 cm reached 9.0 h into the storm; worst hour 23 mm (20% of the storm); water beside the road 0.23 m below its crest (design freeboard 0.30 m; P 0.69); a culvert within 100 m is overtopped |
| 3 | 1.00 | John Fitch Highway | Fitchburg | 0.67 m of water at peak; over 30 cm for 10.5 h; 30 cm reached 8.0 h into the storm; worst hour 23 mm (19% of the storm); runoff beside / along the road at 0.7 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.32); a culvert within 100 m is overtopped |
| 4 | 1.00 | John Fitch Highway | Fitchburg | 0.95 m of water at peak; over 30 cm for 10.0 h; 30 cm reached 8.5 h into the storm; worst hour 23 mm (19% of the storm); water beside the road 0.48 m below its crest (design freeboard 0.30 m; P 0.12) |
| 5 | 1.00 | Depot Street | Fitchburg | 1.75 m of water at peak; over 30 cm for 14.5 h; 30 cm reached 0.5 h into the storm; worst hour 23 mm (19% of the storm); water beside the road 1.08 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 0.7 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.22); a culvert within 100 m is overtopped |
| 6 | 1.00 | Water Street | Leominster | 0.69 m of water at peak; over 30 cm for 9.5 h; 30 cm reached 9.0 h into the storm; worst hour 22 mm (20% of the storm); a culvert within 100 m is overtopped |
| 7 | 1.00 | Route 12 | Fitchburg | 0.84 m of water at peak; over 30 cm for 10.0 h; 30 cm reached 8.5 h into the storm; worst hour 24 mm (19% of the storm); runoff beside / along the road at 0.7 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.21); a culvert within 100 m is overtopped |
| 8 | 1.00 | Wrentham Road | Bellingham | 0.75 m of water at peak; over 30 cm for 5.0 h; 30 cm reached 13.5 h into the storm; worst hour 28 mm (24% of the storm); water beside the road 0.19 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.9 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 28 mm; catchment 171.4 ha) (P 0.96); a culvert within 100 m is overtopped |
| 9 | 1.00 | Paine Street | Bellingham | 0.97 m of water at peak; over 30 cm for 4.5 h; 30 cm reached 14.0 h into the storm; worst hour 27 mm (24% of the storm); a culvert within 100 m is overtopped |
| 10 | 1.00 | Route 12 | Ashburnham | 0.73 m of water at peak; over 30 cm for 6.5 h; 30 cm reached 9.0 h into the storm; worst hour 24 mm (18% of the storm); water beside the road 0.35 m below its crest (design freeboard 0.30 m; P 0.38); runoff beside / along the road at 0.9 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.42); a culvert within 100 m is overtopped |
| 11 | 1.00 | Kingman Drive | Leominster | 0.70 m of water at peak; over 30 cm for 7.5 h; 30 cm reached 8.5 h into the storm; worst hour 22 mm (19% of the storm); runoff beside / along the road at 0.9 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.44); a culvert within 100 m is overtopped |
| 12 | 1.00 | Oakmont Avenue | Westminster | 0.88 m of water at peak; over 30 cm for 10.5 h; 30 cm reached 8.0 h into the storm; worst hour 24 mm (18% of the storm); a culvert within 100 m is overtopped |
| 13 | 1.00 | (unnamed) | Barre | 0.70 m of water at peak; over 30 cm for 10.0 h; 30 cm reached 8.5 h into the storm; worst hour 21 mm (14% of the storm); water beside the road 0.45 m above its crest (design freeboard 0.30 m; P 1.00); fast water: depth x speed 0.25 m2/s (small cars unstable from 0.3); runoff beside / along the road at 0.8 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.28); a culvert within 100 m is overtopped |
| 14 | 1.00 | Route 67 | Barre | 0.70 m of water at peak; over 30 cm for 10.0 h; 30 cm reached 8.5 h into the storm; worst hour 21 mm (14% of the storm); a culvert within 100 m is overtopped |
| 15 | 1.00 | Lackey Lane | Barre | 1.02 m of water at peak; over 30 cm for 9.0 h; 30 cm reached 9.5 h into the storm; worst hour 23 mm (16% of the storm); water beside the road 0.06 m above its crest (design freeboard 0.30 m; P 0.99); runoff beside / along the road at 0.4 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.14); a culvert within 100 m is overtopped |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
