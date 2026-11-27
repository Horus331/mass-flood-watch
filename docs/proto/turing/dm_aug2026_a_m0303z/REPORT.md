# Road-closure prototype: aug2026_proto_dm_aug2026_a_m0303z

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on GPU (cuda)), 20 m grid, storm from 2026-08-03T03:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 45,099 |
| Expected closures (sum of probabilities) | 329.1 |
| Segments with closure probability >= 50% | 184 (149.4 km) |
| Further segments that may close (stream reaches the road crest) | 307 (217.0 km) |
| Culverts overtopped / surcharged | 474 / 11 of 10736 |
| Road segments cut off from hospitals | 1731 |
| Worst added trip time to a hospital | 57.2 min |
| Heaviest hour of rain | 51.0 mm |
| Flood model run time | 283 s |

## Checks against what happened

- Storm-day flood reports in the area: 3; water >= 10 cm within 100 m of 67% of them, vs 23% of random points (any day).
- Segments flagged impassable are 4.44x as likely as an average segment to have a report within 200 m.
- MassDOT repeating flood sites in the area: 30; 3 have a segment within 150 m at P >= 0.5 (share of all segments at P >= 0.5: 0.4%).

## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 1.00 | Route 117 | Lancaster | 1.38 m of water at peak; over 30 cm for 19.0 h; 30 cm reached 0.5 h into the storm; worst hour 17 mm (30% of the storm); culvert (Trib to Still River): headwater 9.56 m vs road crest 2.74 m, 41.5 m3/s |
| 2 | 1.00 | Depot Street | Fitchburg | 1.28 m of water at peak; over 30 cm for 13.5 h; 30 cm reached 0.5 h into the storm; worst hour 48 mm (44% of the storm); a culvert within 100 m is overtopped |
| 3 | 1.00 | Route 31 | Fitchburg | 0.63 m of water at peak; over 30 cm for 9.5 h; 30 cm reached 10.0 h into the storm; worst hour 49 mm (45% of the storm); a culvert within 100 m is overtopped |
| 4 | 1.00 | Route 12 | Fitchburg | 0.64 m of water at peak; over 30 cm for 11.0 h; 30 cm reached 8.5 h into the storm; worst hour 49 mm (44% of the storm); a culvert within 100 m is overtopped |
| 5 | 1.00 | Route 70 | Lancaster | 0.70 m of water at peak; over 30 cm for 5.5 h; 30 cm reached 14.0 h into the storm; worst hour 18 mm (30% of the storm); a culvert within 100 m is overtopped |
| 6 | 1.00 | Route 70 | Lancaster | 0.70 m of water at peak; over 30 cm for 5.5 h; 30 cm reached 14.0 h into the storm; worst hour 18 mm (30% of the storm); a culvert within 100 m is overtopped |
| 7 | 1.00 | Route 67 | North Brookfield | 0.70 m of water at peak; over 30 cm for 11.5 h; 30 cm reached 8.0 h into the storm; worst hour 44 mm (36% of the storm); water beside the road 0.35 m below its crest (design freeboard 0.30 m; P 0.36); a culvert within 100 m is overtopped |
| 8 | 1.00 | Oakmont Avenue | Westminster | 0.84 m of water at peak; over 30 cm for 11.5 h; 30 cm reached 8.0 h into the storm; worst hour 51 mm (43% of the storm); a culvert within 100 m is overtopped |
| 9 | 1.00 | (unnamed) | Barre | 1.00 m of water at peak; over 30 cm for 11.5 h; 30 cm reached 8.0 h into the storm; worst hour 44 mm (29% of the storm); water beside the road 0.66 m above its crest (design freeboard 0.30 m; P 1.00); fast water: depth x speed 0.47 m2/s (small cars unstable from 0.3); runoff beside / along the road at 1.0 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.48); a culvert within 100 m is overtopped |
| 10 | 1.00 | Route 67 | Barre | 0.99 m of water at peak; over 30 cm for 11.5 h; 30 cm reached 8.0 h into the storm; worst hour 44 mm (29% of the storm); water beside the road 0.28 m below its crest (design freeboard 0.30 m; P 0.56); a culvert within 100 m is overtopped |
| 11 | 1.00 | Lackey Lane | Barre | 1.15 m of water at peak; over 30 cm for 11.0 h; 30 cm reached 8.5 h into the storm; worst hour 50 mm (34% of the storm); water beside the road 0.20 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 0.6 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.27); road sag 0.4 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 50 mm; catchment 26.7 ha) (P 0.36); a culvert within 100 m is overtopped |
| 12 | 1.00 | West Brookfield Road | New Braintree | 0.85 m of water at peak; over 30 cm for 11.0 h; 30 cm reached 8.5 h into the storm; worst hour 44 mm (32% of the storm); a culvert within 100 m is overtopped |
| 13 | 1.00 | (unnamed) | Winchendon | 0.71 m of water at peak; over 30 cm for 11.0 h; 30 cm reached 8.5 h into the storm; worst hour 49 mm (36% of the storm); a culvert within 100 m is overtopped |
| 14 | 1.00 | (unnamed) | Spencer | 0.83 m of water at peak; over 30 cm for 11.5 h; 30 cm reached 8.0 h into the storm; worst hour 34 mm (35% of the storm) |
| 15 | 1.00 | Commercial Road | Leominster | 0.79 m of water at peak; over 30 cm for 9.5 h; 30 cm reached 10.0 h into the storm; worst hour 35 mm (44% of the storm); a culvert within 100 m is overtopped |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
