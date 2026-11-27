# Road-closure prototype: aug2026_proto_dm_aug2026_ref

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on GPU (cuda)), 20 m grid, storm from 2026-08-03T04:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 45,099 |
| Expected closures (sum of probabilities) | 167.1 |
| Segments with closure probability >= 50% | 53 (35.0 km) |
| Further segments that may close (stream reaches the road crest) | 169 (117.0 km) |
| Culverts overtopped / surcharged | 209 / 4 of 10736 |
| Road segments cut off from hospitals | 721 |
| Worst added trip time to a hospital | 45.8 min |
| Heaviest hour of rain | 52.5 mm |
| Flood model run time | 250 s |

## Checks against what happened

- Storm-day flood reports in the area: 3; water >= 10 cm within 100 m of 67% of them, vs 12% of random points (any day).
- Segments flagged impassable are 18.36x as likely as an average segment to have a report within 200 m.
- MassDOT repeating flood sites in the area: 30; 1 have a segment within 150 m at P >= 0.5 (share of all segments at P >= 0.5: 0.1%).

## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 1.00 | Route 117 | Lancaster | 1.43 m of water at peak; over 30 cm for 18.0 h; 30 cm reached 0.5 h into the storm; worst hour 11 mm (39% of the storm); culvert (Trib to Still River): headwater 7.71 m vs road crest 2.74 m, 36.3 m3/s |
| 2 | 1.00 | (unnamed) | Leominster | 0.86 m of water at peak; over 30 cm for 10.0 h; 30 cm reached 8.5 h into the storm; worst hour 31 mm (40% of the storm); a culvert within 100 m is overtopped |
| 3 | 1.00 | Depot Street | Fitchburg | 0.88 m of water at peak; over 30 cm for 15.0 h; 30 cm reached 0.5 h into the storm; worst hour 26 mm (30% of the storm); runoff beside / along the road at 0.6 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.10); a culvert within 100 m is overtopped |
| 4 | 1.00 | Water Street | Leominster | 0.86 m of water at peak; over 30 cm for 10.0 h; 30 cm reached 8.5 h into the storm; worst hour 30 mm (39% of the storm); a culvert within 100 m is overtopped |
| 5 | 1.00 | Kingman Drive | Leominster | 0.81 m of water at peak; over 30 cm for 9.5 h; 30 cm reached 8.0 h into the storm; worst hour 38 mm (41% of the storm); water beside the road 0.37 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 1.1 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.58); a culvert within 100 m is overtopped |
| 6 | 1.00 | Depot Square | Leominster | 0.86 m of water at peak; over 30 cm for 10.0 h; 30 cm reached 8.5 h into the storm; worst hour 30 mm (39% of the storm); a culvert within 100 m is overtopped |
| 7 | 1.00 | Adams Street | Leominster | 0.72 m of water at peak; over 30 cm for 10.0 h; 30 cm reached 8.5 h into the storm; worst hour 32 mm (40% of the storm); water beside the road 0.11 m below its crest (design freeboard 0.30 m; P 0.90); a culvert within 100 m is overtopped |
| 8 | 1.00 | Commercial Road | Leominster | 0.82 m of water at peak; over 30 cm for 6.5 h; 30 cm reached 9.5 h into the storm; worst hour 27 mm (40% of the storm); a culvert within 100 m is overtopped |
| 9 | 1.00 | Exchange Street | Leominster | 0.64 m of water at peak; over 30 cm for 3.5 h; 30 cm reached 8.0 h into the storm; worst hour 36 mm (40% of the storm); water beside the road 0.72 m above its crest (design freeboard 0.30 m; P 1.00); fast water: depth x speed 0.31 m2/s (small cars unstable from 0.3); runoff beside / along the road at 2.2 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.96); a culvert within 100 m is overtopped |
| 10 | 1.00 | Reservoir Road | Lunenburg | 0.59 m of water at peak; over 30 cm for 7.5 h; 30 cm reached 9.5 h into the storm; worst hour 26 mm (38% of the storm); culvert (N. Branch Catacunemaug): headwater 4.73 m vs road crest 1.07 m, 2.7 m3/s |
| 11 | 1.00 | Constitution Drive | Leominster | 0.59 m of water at peak; over 30 cm for 3.0 h; 30 cm reached 8.0 h into the storm; worst hour 36 mm (40% of the storm) |
| 12 | 0.99 | (unnamed) | Leominster | 0.55 m of water at peak; over 30 cm for 3.0 h; 30 cm reached 8.0 h into the storm; worst hour 36 mm (40% of the storm) |
| 13 | 0.99 | Route 70 | Lancaster | 0.53 m of water at peak; over 30 cm for 3.5 h; 30 cm reached 13.5 h into the storm; worst hour 10 mm (36% of the storm); a culvert within 100 m is overtopped |
| 14 | 0.99 | Route 70 | Lancaster | 0.53 m of water at peak; over 30 cm for 3.5 h; 30 cm reached 13.5 h into the storm; worst hour 10 mm (36% of the storm); a culvert within 100 m is overtopped |
| 15 | 0.99 | Houghton Road | Princeton | 0.53 m of water at peak; over 30 cm for 3.5 h; 30 cm reached 8.5 h into the storm; worst hour 35 mm (42% of the storm); water beside the road 0.16 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 0.7 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.25); a culvert within 100 m is overtopped |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
