# Road-closure prototype: sep2021_proto_dm_sep2021_a_m0122z

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on GPU (cuda)), 20 m grid, storm from 2021-09-01T22:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 45,099 |
| Expected closures (sum of probabilities) | 1684.0 |
| Segments with closure probability >= 50% | 1355 (975.6 km) |
| Further segments that may close (stream reaches the road crest) | 1146 (704.3 km) |
| Culverts overtopped / surcharged | 2131 / 55 of 10736 |
| Road segments cut off from hospitals | 11399 |
| Worst added trip time to a hospital | 77.6 min |
| Heaviest hour of rain | 42.4 mm |
| Flood model run time | 335 s |

## Checks against what happened

- Storm-day flood reports in the area: 10; water >= 10 cm within 100 m of 70% of them, vs 67% of random points (any day).
- Segments flagged impassable are 1.32x as likely as an average segment to have a report within 200 m.
- MassDOT repeating flood sites in the area: 30; 13 have a segment within 150 m at P >= 0.5 (share of all segments at P >= 0.5: 3.0%).

## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 1.00 | (unnamed) | Framingham | 2.24 m of water at peak; over 30 cm for 13.0 h; 30 cm reached 7.5 h into the storm; worst hour 18 mm (11% of the storm); water beside the road 1.97 m above its crest (design freeboard 0.30 m; P 1.00); road sag 2.9 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 18 mm; catchment 15.3 ha) (P 1.00) |
| 2 | 1.00 | (unnamed) | Worcester | 1.99 m of water at peak; over 30 cm for 11.0 h; 30 cm reached 9.5 h into the storm; worst hour 18 mm (12% of the storm); water beside the road 1.87 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.7 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 18 mm; catchment 77.2 ha) (P 1.00) |
| 3 | 1.00 | I-290 | Shrewsbury | 0.98 m of water at peak; over 30 cm for 10.5 h; 30 cm reached 10.0 h into the storm; worst hour 19 mm (12% of the storm); water beside the road 0.98 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 1.4 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.52) |
| 4 | 1.00 | I-290 | Shrewsbury | 0.68 m of water at peak; over 30 cm for 9.5 h; 30 cm reached 11.0 h into the storm; worst hour 19 mm (12% of the storm); water beside the road 0.68 m above its crest (design freeboard 0.30 m; P 1.00) |
| 5 | 1.00 | Route 9 | Framingham | 0.74 m of water at peak; over 30 cm for 14.0 h; 30 cm reached 2.0 h into the storm; worst hour 18 mm (11% of the storm); water beside the road 0.09 m above its crest (design freeboard 0.30 m; P 0.99); a culvert within 100 m is overtopped |
| 6 | 1.00 | Route 9 | Framingham | 0.74 m of water at peak; over 30 cm for 14.0 h; 30 cm reached 2.0 h into the storm; worst hour 18 mm (11% of the storm); a culvert within 100 m is overtopped |
| 7 | 1.00 | Route 2 | Harvard | 0.69 m of water at peak; over 30 cm for 11.5 h; 30 cm reached 9.0 h into the storm; worst hour 20 mm (12% of the storm); water beside the road 0.54 m above its crest (design freeboard 0.30 m; P 1.00); a culvert within 100 m is overtopped |
| 8 | 1.00 | Route 2 | Harvard | 0.71 m of water at peak; over 30 cm for 12.0 h; 30 cm reached 8.5 h into the storm; worst hour 19 mm (12% of the storm); runoff beside / along the road at 0.6 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.10); a culvert within 100 m is overtopped |
| 9 | 1.00 | Route 70 | Worcester | 0.90 m of water at peak; over 30 cm for 12.0 h; 30 cm reached 8.5 h into the storm; worst hour 19 mm (12% of the storm); a culvert within 100 m is overtopped |
| 10 | 1.00 | Route 146 | Uxbridge | 0.93 m of water at peak; over 30 cm for 12.0 h; 30 cm reached 8.5 h into the storm; worst hour 31 mm (18% of the storm); a culvert within 100 m is overtopped |
| 11 | 1.00 | Route 9 | Worcester | 1.02 m of water at peak; over 30 cm for 10.0 h; 30 cm reached 10.5 h into the storm; worst hour 18 mm (11% of the storm); water beside the road 1.02 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 1.4 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.72) |
| 12 | 1.00 | Route 70 | Worcester | 0.91 m of water at peak; over 30 cm for 12.0 h; 30 cm reached 8.5 h into the storm; worst hour 19 mm (12% of the storm); a culvert within 100 m is overtopped |
| 13 | 1.00 | Route 9 | Worcester | 1.02 m of water at peak; over 30 cm for 10.0 h; 30 cm reached 10.5 h into the storm; worst hour 18 mm (11% of the storm); water beside the road 1.02 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 0.8 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.29) |
| 14 | 1.00 | Route 117 | Lancaster | 2.26 m of water at peak; over 30 cm for 20.0 h; 30 cm reached 0.5 h into the storm; worst hour 20 mm (13% of the storm); water beside the road 0.13 m below its crest (design freeboard 0.30 m; P 0.87); culvert (Trib to Still River): headwater 31.03 m vs road crest 2.74 m, 80.3 m3/s |
| 15 | 1.00 | Shrewsbury Street | Worcester | 1.40 m of water at peak; over 30 cm for 12.5 h; 30 cm reached 8.0 h into the storm; worst hour 19 mm (12% of the storm); water beside the road 1.32 m above its crest (design freeboard 0.30 m; P 1.00); fast water: depth x speed 0.26 m2/s (small cars unstable from 0.3); runoff beside / along the road at 0.6 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.10); road sag 0.8 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 19 mm; catchment 127.8 ha) (P 1.00) |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
