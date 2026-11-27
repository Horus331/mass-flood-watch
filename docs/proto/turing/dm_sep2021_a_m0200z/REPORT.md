# Road-closure prototype: sep2021_proto_dm_sep2021_a_m0200z

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on GPU (cuda)), 20 m grid, storm from 2021-09-02T00:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 45,099 |
| Expected closures (sum of probabilities) | 1712.7 |
| Segments with closure probability >= 50% | 1397 (992.4 km) |
| Further segments that may close (stream reaches the road crest) | 1287 (756.9 km) |
| Culverts overtopped / surcharged | 2180 / 67 of 10736 |
| Road segments cut off from hospitals | 10633 |
| Worst added trip time to a hospital | 91.7 min |
| Heaviest hour of rain | 74.6 mm |
| Flood model run time | 292 s |

## Checks against what happened

- Storm-day flood reports in the area: 10; water >= 10 cm within 100 m of 70% of them, vs 68% of random points (any day).
- Segments flagged impassable are 1.53x as likely as an average segment to have a report within 200 m.
- MassDOT repeating flood sites in the area: 30; 15 have a segment within 150 m at P >= 0.5 (share of all segments at P >= 0.5: 3.1%).

## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 1.00 | (unnamed) | Worcester | 1.88 m of water at peak; over 30 cm for 10.5 h; 30 cm reached 8.0 h into the storm; worst hour 28 mm (19% of the storm); water beside the road 1.76 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.7 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 28 mm; catchment 77.2 ha) (P 1.00) |
| 2 | 1.00 | (unnamed) | Framingham | 2.29 m of water at peak; over 30 cm for 12.0 h; 30 cm reached 6.5 h into the storm; worst hour 42 mm (26% of the storm); water beside the road 2.02 m above its crest (design freeboard 0.30 m; P 1.00); road sag 2.9 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 42 mm; catchment 15.3 ha) (P 1.00) |
| 3 | 1.00 | (unnamed) | Milford | 0.74 m of water at peak; over 30 cm for 11.0 h; 30 cm reached 7.5 h into the storm; worst hour 52 mm (26% of the storm); culvert (Charles River): headwater 21.89 m vs road crest 2.19 m, 19.5 m3/s |
| 4 | 1.00 | I-290 | Shrewsbury | 0.84 m of water at peak; over 30 cm for 10.0 h; 30 cm reached 8.5 h into the storm; worst hour 25 mm (18% of the storm); water beside the road 0.84 m above its crest (design freeboard 0.30 m; P 1.00) |
| 5 | 1.00 | Route 9 | Framingham | 0.83 m of water at peak; over 30 cm for 13.0 h; 30 cm reached 2.0 h into the storm; worst hour 44 mm (27% of the storm); water beside the road 0.15 m above its crest (design freeboard 0.30 m; P 1.00); a culvert within 100 m is overtopped |
| 6 | 1.00 | Route 9 | Framingham | 0.83 m of water at peak; over 30 cm for 13.0 h; 30 cm reached 2.0 h into the storm; worst hour 44 mm (27% of the storm); water beside the road 0.15 m above its crest (design freeboard 0.30 m; P 1.00); a culvert within 100 m is overtopped |
| 7 | 1.00 | Route 146 | Uxbridge | 1.43 m of water at peak; over 30 cm for 12.0 h; 30 cm reached 6.5 h into the storm; worst hour 50 mm (23% of the storm); a culvert within 100 m is overtopped |
| 8 | 1.00 | Route 9 | Worcester | 0.89 m of water at peak; over 30 cm for 9.5 h; 30 cm reached 9.0 h into the storm; worst hour 26 mm (18% of the storm); water beside the road 0.89 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 1.4 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.53) |
| 9 | 1.00 | Route 70 | Worcester | 0.85 m of water at peak; over 30 cm for 11.0 h; 30 cm reached 7.5 h into the storm; worst hour 26 mm (18% of the storm); a culvert within 100 m is overtopped |
| 10 | 1.00 | Route 70 | Worcester | 0.85 m of water at peak; over 30 cm for 11.0 h; 30 cm reached 7.5 h into the storm; worst hour 26 mm (18% of the storm); a culvert within 100 m is overtopped |
| 11 | 1.00 | Route 9 | Worcester | 0.89 m of water at peak; over 30 cm for 9.5 h; 30 cm reached 9.0 h into the storm; worst hour 26 mm (18% of the storm); water beside the road 0.89 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 0.8 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.29) |
| 12 | 1.00 | Shrewsbury Street | Worcester | 1.37 m of water at peak; over 30 cm for 11.5 h; 30 cm reached 7.0 h into the storm; worst hour 27 mm (19% of the storm); water beside the road 1.28 m above its crest (design freeboard 0.30 m; P 1.00); fast water: depth x speed 0.29 m2/s (small cars unstable from 0.3); runoff beside / along the road at 0.6 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.14); road sag 0.8 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 26 mm; catchment 127.8 ha) (P 1.00) |
| 13 | 1.00 | Route 117 | Lancaster | 1.96 m of water at peak; over 30 cm for 18.0 h; 30 cm reached 0.5 h into the storm; worst hour 21 mm (17% of the storm); water beside the road 0.44 m below its crest (design freeboard 0.30 m; P 0.18); culvert (Trib to Still River): headwater 20.57 m vs road crest 2.74 m, 64.4 m3/s |
| 14 | 1.00 | Shrewsbury Street | Worcester | 1.47 m of water at peak; over 30 cm for 12.0 h; 30 cm reached 6.5 h into the storm; worst hour 27 mm (19% of the storm); water beside the road 1.39 m above its crest (design freeboard 0.30 m; P 1.00); fast water: depth x speed 0.33 m2/s (small cars unstable from 0.3); runoff beside / along the road at 0.6 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.14); road sag 0.8 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 26 mm; catchment 127.8 ha) (P 1.00) |
| 15 | 1.00 | Martin Luther King Jr Boulevard | Worcester | 1.92 m of water at peak; over 30 cm for 12.5 h; 30 cm reached 6.0 h into the storm; worst hour 26 mm (19% of the storm); water beside the road 1.99 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 0.6 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.10); road sag 3.2 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 26 mm; catchment 60.2 ha) (P 1.00); a culvert within 100 m is overtopped |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
