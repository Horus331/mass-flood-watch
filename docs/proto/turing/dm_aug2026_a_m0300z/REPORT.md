# Road-closure prototype: aug2026_proto_dm_aug2026_a_m0300z

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on GPU (cuda)), 20 m grid, storm from 2026-08-03T00:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 45,099 |
| Expected closures (sum of probabilities) | 1930.2 |
| Segments with closure probability >= 50% | 1612 (1116.7 km) |
| Further segments that may close (stream reaches the road crest) | 1410 (868.7 km) |
| Culverts overtopped / surcharged | 2305 / 79 of 10736 |
| Road segments cut off from hospitals | 13216 |
| Worst added trip time to a hospital | 95.4 min |
| Heaviest hour of rain | 56.4 mm |
| Flood model run time | 340 s |

## Checks against what happened

- Storm-day flood reports in the area: 3; water >= 10 cm within 100 m of 67% of them, vs 69% of random points (any day).
- Segments flagged impassable are 3.31x as likely as an average segment to have a report within 200 m.
- MassDOT repeating flood sites in the area: 30; 15 have a segment within 150 m at P >= 0.5 (share of all segments at P >= 0.5: 3.6%).

## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 1.00 | (unnamed) | Worcester | 2.26 m of water at peak; over 30 cm for 10.5 h; 30 cm reached 12.0 h into the storm; worst hour 36 mm (20% of the storm); water beside the road 2.14 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.7 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 36 mm; catchment 77.2 ha) (P 1.00) |
| 2 | 1.00 | (unnamed) | Framingham | 2.06 m of water at peak; over 30 cm for 11.5 h; 30 cm reached 11.0 h into the storm; worst hour 24 mm (19% of the storm); water beside the road 1.79 m above its crest (design freeboard 0.30 m; P 1.00); road sag 2.9 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 24 mm; catchment 15.3 ha) (P 1.00) |
| 3 | 1.00 | I-290 | Shrewsbury | 1.03 m of water at peak; over 30 cm for 9.5 h; 30 cm reached 13.0 h into the storm; worst hour 36 mm (21% of the storm); water beside the road 1.03 m above its crest (design freeboard 0.30 m; P 1.00) |
| 4 | 1.00 | I-290 | Shrewsbury | 0.73 m of water at peak; over 30 cm for 9.0 h; 30 cm reached 13.5 h into the storm; worst hour 36 mm (21% of the storm); water beside the road 0.74 m above its crest (design freeboard 0.30 m; P 1.00) |
| 5 | 1.00 | Ramp-Rt 84 Eb To Rt 90 Wb | Sturbridge | 0.67 m of water at peak; over 30 cm for 11.5 h; 30 cm reached 11.0 h into the storm; worst hour 56 mm (24% of the storm) |
| 6 | 1.00 | Route 2 | Harvard | 0.63 m of water at peak; over 30 cm for 9.5 h; 30 cm reached 13.0 h into the storm; worst hour 36 mm (22% of the storm); water beside the road 0.56 m above its crest (design freeboard 0.30 m; P 1.00); a culvert within 100 m is overtopped |
| 7 | 1.00 | Route 2 | Harvard | 0.65 m of water at peak; over 30 cm for 10.0 h; 30 cm reached 12.5 h into the storm; worst hour 36 mm (23% of the storm); runoff beside / along the road at 1.2 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.53); a culvert within 100 m is overtopped |
| 8 | 1.00 | Route 9 | Worcester | 1.09 m of water at peak; over 30 cm for 9.5 h; 30 cm reached 13.0 h into the storm; worst hour 36 mm (20% of the storm); water beside the road 1.09 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 1.4 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.76) |
| 9 | 1.00 | Route 70 | Worcester | 0.93 m of water at peak; over 30 cm for 11.0 h; 30 cm reached 11.5 h into the storm; worst hour 37 mm (20% of the storm); a culvert within 100 m is overtopped |
| 10 | 1.00 | Route 70 | Worcester | 0.93 m of water at peak; over 30 cm for 11.0 h; 30 cm reached 11.5 h into the storm; worst hour 37 mm (20% of the storm); a culvert within 100 m is overtopped |
| 11 | 1.00 | Route 9 | Worcester | 1.09 m of water at peak; over 30 cm for 9.5 h; 30 cm reached 13.0 h into the storm; worst hour 36 mm (20% of the storm); water beside the road 1.09 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 1.4 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.58) |
| 12 | 1.00 | Route 117 | Lancaster | 1.96 m of water at peak; over 30 cm for 22.0 h; 30 cm reached 0.5 h into the storm; worst hour 37 mm (22% of the storm); water beside the road 0.13 m below its crest (design freeboard 0.30 m; P 0.88); culvert (Trib to Still River): headwater 31.54 m vs road crest 2.74 m, 81.0 m3/s |
| 13 | 1.00 | Route 20 | Worcester | 0.66 m of water at peak; over 30 cm for 11.0 h; 30 cm reached 11.5 h into the storm; worst hour 36 mm (20% of the storm); runoff beside / along the road at 0.6 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.14); a culvert within 100 m is overtopped |
| 14 | 1.00 | Shrewsbury Street | Worcester | 1.40 m of water at peak; over 30 cm for 11.5 h; 30 cm reached 11.0 h into the storm; worst hour 37 mm (20% of the storm); water beside the road 1.32 m above its crest (design freeboard 0.30 m; P 1.00); fast water: depth x speed 0.40 m2/s (small cars unstable from 0.3); runoff beside / along the road at 0.7 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.21); road sag 0.8 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 37 mm; catchment 127.8 ha) (P 1.00) |
| 15 | 1.00 | Route 20 | Charlton | 0.65 m of water at peak; over 30 cm for 12.5 h; 30 cm reached 10.0 h into the storm; worst hour 56 mm (24% of the storm); a culvert within 100 m is overtopped |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
