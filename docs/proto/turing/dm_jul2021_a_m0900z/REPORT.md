# Road-closure prototype: jul2021_proto_dm_jul2021_a_m0900z

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on GPU (cuda)), 20 m grid, storm from 2021-07-09T00:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 45,099 |
| Expected closures (sum of probabilities) | 121.5 |
| Segments with closure probability >= 50% | 30 (25.2 km) |
| Further segments that may close (stream reaches the road crest) | 88 (65.1 km) |
| Culverts overtopped / surcharged | 115 / 4 of 10736 |
| Road segments cut off from hospitals | 413 |
| Worst added trip time to a hospital | 23.8 min |
| Heaviest hour of rain | 25.5 mm |
| Flood model run time | 439 s |

## Checks against what happened

- Storm-day flood reports in the area: 9; water >= 10 cm within 100 m of 11% of them, vs 10% of random points (any day).
- Segments flagged impassable are 10.89x as likely as an average segment to have a report within 200 m.
- MassDOT repeating flood sites in the area: 30; 2 have a segment within 150 m at P >= 0.5 (share of all segments at P >= 0.5: 0.1%).

## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 1.00 | (unnamed) | Framingham | 0.67 m of water at peak; over 30 cm for 7.5 h; 30 cm reached 19.0 h into the storm; worst hour 11 mm (18% of the storm); road sag 2.9 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 11 mm; catchment 15.3 ha) (P 1.00) |
| 2 | 1.00 | Wrentham Road | Bellingham | 0.86 m of water at peak; over 30 cm for 11.5 h; 30 cm reached 15.0 h into the storm; worst hour 23 mm (21% of the storm); water beside the road 0.29 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.9 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 23 mm; catchment 171.4 ha) (P 1.00); a culvert within 100 m is overtopped |
| 3 | 1.00 | Paine Street | Bellingham | 1.16 m of water at peak; over 30 cm for 11.0 h; 30 cm reached 15.5 h into the storm; worst hour 23 mm (21% of the storm); a culvert within 100 m is overtopped |
| 4 | 1.00 | Pine Grove Avenue | Bellingham | 1.16 m of water at peak; over 30 cm for 11.5 h; 30 cm reached 15.0 h into the storm; worst hour 22 mm (20% of the storm); water beside the road 0.14 m below its crest (design freeboard 0.30 m; P 0.86); a culvert within 100 m is overtopped |
| 5 | 1.00 | (unnamed) | Blackstone | 0.72 m of water at peak; over 30 cm for 10.0 h; 30 cm reached 16.5 h into the storm; worst hour 19 mm (20% of the storm); a culvert within 100 m is overtopped |
| 6 | 1.00 | (unnamed) | Bellingham | 0.58 m of water at peak; over 30 cm for 8.5 h; 30 cm reached 16.5 h into the storm; worst hour 22 mm (21% of the storm); a culvert within 100 m is overtopped |
| 7 | 1.00 | Bellingham Street | Mendon | 0.59 m of water at peak; over 30 cm for 7.0 h; 30 cm reached 18.0 h into the storm; worst hour 18 mm (21% of the storm); a culvert within 100 m is overtopped |
| 8 | 0.99 | Railroad Street | Bellingham | 0.54 m of water at peak; over 30 cm for 7.5 h; 30 cm reached 16.5 h into the storm; worst hour 23 mm (21% of the storm); water beside the road 0.46 m below its crest (design freeboard 0.30 m; P 0.15); a culvert within 100 m is overtopped |
| 9 | 0.99 | (unnamed) | Bellingham | 0.53 m of water at peak; over 30 cm for 8.0 h; 30 cm reached 18.0 h into the storm; worst hour 23 mm (21% of the storm); a culvert within 100 m is overtopped |
| 10 | 0.98 | Wrentham Road | Bellingham | 0.50 m of water at peak; over 30 cm for 6.5 h; 30 cm reached 15.0 h into the storm; worst hour 24 mm (21% of the storm); a culvert within 100 m is overtopped |
| 11 | 0.98 | West Street | Wrentham | 0.50 m of water at peak; over 30 cm for 7.5 h; 30 cm reached 14.5 h into the storm; worst hour 24 mm (21% of the storm); runoff beside / along the road at 0.8 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.36); a culvert within 100 m is overtopped |
| 12 | 0.98 | (unnamed) | Bellingham | 0.50 m of water at peak; over 30 cm for 6.0 h; 30 cm reached 15.0 h into the storm; worst hour 24 mm (21% of the storm); a culvert within 100 m is overtopped |
| 13 | 0.98 | Little Tree Lane | Framingham | 0.50 m of water at peak; over 30 cm for 2.0 h; 30 cm reached 1.0 h into the storm; worst hour 11 mm (17% of the storm); a culvert within 100 m is overtopped |
| 14 | 0.97 | Cemetery Street | Mendon | 0.49 m of water at peak; over 30 cm for 6.0 h; 30 cm reached 17.0 h into the storm; worst hour 18 mm (21% of the storm); a culvert within 100 m is overtopped |
| 15 | 0.97 | Pulaski Boulevard | Bellingham | 0.49 m of water at peak; over 30 cm for 5.0 h; 30 cm reached 18.5 h into the storm; worst hour 24 mm (21% of the storm); a culvert within 100 m is overtopped |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
