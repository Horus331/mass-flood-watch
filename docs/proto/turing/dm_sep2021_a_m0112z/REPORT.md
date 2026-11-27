# Road-closure prototype: sep2021_proto_dm_sep2021_a_m0112z

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on GPU (cuda)), 20 m grid, storm from 2021-09-01T12:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 45,099 |
| Expected closures (sum of probabilities) | 2173.4 |
| Segments with closure probability >= 50% | 1850 (1290.9 km) |
| Further segments that may close (stream reaches the road crest) | 1520 (906.1 km) |
| Culverts overtopped / surcharged | 2524 / 96 of 10736 |
| Road segments cut off from hospitals | 15034 |
| Worst added trip time to a hospital | 79.9 min |
| Heaviest hour of rain | 64.1 mm |
| Flood model run time | 458 s |

## Checks against what happened

- Storm-day flood reports in the area: 10; water >= 10 cm within 100 m of 70% of them, vs 70% of random points (any day).
- Segments flagged impassable are 1.84x as likely as an average segment to have a report within 200 m.
- MassDOT repeating flood sites in the area: 30; 16 have a segment within 150 m at P >= 0.5 (share of all segments at P >= 0.5: 4.1%).

## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 1.00 | (unnamed) | Framingham | 2.33 m of water at peak; over 30 cm for 14.0 h; 30 cm reached 16.5 h into the storm; worst hour 27 mm (16% of the storm); water beside the road 2.06 m above its crest (design freeboard 0.30 m; P 1.00); road sag 2.9 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 27 mm; catchment 15.3 ha) (P 1.00) |
| 2 | 1.00 | (unnamed) | Worcester | 2.24 m of water at peak; over 30 cm for 11.5 h; 30 cm reached 19.0 h into the storm; worst hour 30 mm (18% of the storm); water beside the road 2.13 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.7 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 30 mm; catchment 77.2 ha) (P 1.00) |
| 3 | 1.00 | (unnamed) | Milford | 0.85 m of water at peak; over 30 cm for 12.5 h; 30 cm reached 18.0 h into the storm; worst hour 36 mm (17% of the storm) |
| 4 | 1.00 | I-290 | Shrewsbury | 0.97 m of water at peak; over 30 cm for 11.0 h; 30 cm reached 19.5 h into the storm; worst hour 24 mm (15% of the storm); water beside the road 0.98 m above its crest (design freeboard 0.30 m; P 1.00) |
| 5 | 1.00 | I-290 | Shrewsbury | 0.68 m of water at peak; over 30 cm for 10.5 h; 30 cm reached 20.0 h into the storm; worst hour 24 mm (15% of the storm); water beside the road 0.68 m above its crest (design freeboard 0.30 m; P 1.00) |
| 6 | 1.00 | Ramp-Rt 84 Eb To Rt 90 Wb | Sturbridge | 0.68 m of water at peak; over 30 cm for 12.0 h; 30 cm reached 18.5 h into the storm; worst hour 43 mm (22% of the storm) |
| 7 | 1.00 | Route 9 | Framingham | 0.63 m of water at peak; over 30 cm for 12.5 h; 30 cm reached 2.0 h into the storm; worst hour 27 mm (16% of the storm); water beside the road 0.11 m above its crest (design freeboard 0.30 m; P 1.00); a culvert within 100 m is overtopped |
| 8 | 1.00 | Route 9 | Framingham | 0.63 m of water at peak; over 30 cm for 12.5 h; 30 cm reached 2.0 h into the storm; worst hour 27 mm (16% of the storm); a culvert within 100 m is overtopped |
| 9 | 1.00 | Route 117 | Lancaster | 1.74 m of water at peak; over 30 cm for 30.0 h; 30 cm reached 0.5 h into the storm; worst hour 18 mm (13% of the storm); water beside the road 0.34 m below its crest (design freeboard 0.30 m; P 0.41) |
| 10 | 1.00 | Route 146 | Uxbridge | 1.71 m of water at peak; over 30 cm for 13.5 h; 30 cm reached 17.0 h into the storm; worst hour 51 mm (19% of the storm); a culvert within 100 m is overtopped |
| 11 | 1.00 | Route 9 | Worcester | 1.02 m of water at peak; over 30 cm for 11.0 h; 30 cm reached 19.5 h into the storm; worst hour 26 mm (16% of the storm); water beside the road 1.03 m above its crest (design freeboard 0.30 m; P 1.00) |
| 12 | 1.00 | Route 70 | Worcester | 0.93 m of water at peak; over 30 cm for 12.5 h; 30 cm reached 18.0 h into the storm; worst hour 27 mm (17% of the storm); a culvert within 100 m is overtopped |
| 13 | 1.00 | Route 9 | Worcester | 1.02 m of water at peak; over 30 cm for 11.0 h; 30 cm reached 19.5 h into the storm; worst hour 26 mm (16% of the storm); water beside the road 1.03 m above its crest (design freeboard 0.30 m; P 1.00) |
| 14 | 1.00 | Route 70 | Worcester | 0.93 m of water at peak; over 30 cm for 12.5 h; 30 cm reached 18.0 h into the storm; worst hour 27 mm (17% of the storm); a culvert within 100 m is overtopped |
| 15 | 1.00 | Shrewsbury Street | Worcester | 1.48 m of water at peak; over 30 cm for 13.0 h; 30 cm reached 17.5 h into the storm; worst hour 27 mm (17% of the storm); water beside the road 1.40 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.8 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 27 mm; catchment 127.8 ha) (P 1.00) |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
