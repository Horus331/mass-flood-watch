# Road-closure prototype: sep2022_proto_dm_sep2022_a_m0506z

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on GPU (cuda)), 20 m grid, storm from 2022-09-05T06:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 45,099 |
| Expected closures (sum of probabilities) | 123.9 |
| Segments with closure probability >= 50% | 40 (31.6 km) |
| Further segments that may close (stream reaches the road crest) | 74 (54.6 km) |
| Culverts overtopped / surcharged | 152 / 3 of 10736 |
| Road segments cut off from hospitals | 419 |
| Worst added trip time to a hospital | 23.7 min |
| Heaviest hour of rain | 34.6 mm |
| Flood model run time | 212 s |

## Checks against what happened

- Storm-day flood reports in the area: 6; water >= 10 cm within 100 m of 17% of them, vs 7% of random points (any day).
- Segments flagged impassable are 0.0x as likely as an average segment to have a report within 200 m.
- MassDOT repeating flood sites in the area: 30; 0 have a segment within 150 m at P >= 0.5 (share of all segments at P >= 0.5: 0.1%).

## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 1.00 | Paine Street | Bellingham | 0.82 m of water at peak; over 30 cm for 5.0 h; 30 cm reached 13.5 h into the storm; worst hour 19 mm (19% of the storm); a culvert within 100 m is overtopped |
| 2 | 1.00 | Pine Grove Avenue | Bellingham | 0.84 m of water at peak; over 30 cm for 5.5 h; 30 cm reached 13.0 h into the storm; worst hour 19 mm (19% of the storm); water beside the road 0.43 m below its crest (design freeboard 0.30 m; P 0.20); a culvert within 100 m is overtopped |
| 3 | 1.00 | Wrentham Road | Bellingham | 0.61 m of water at peak; over 30 cm for 5.5 h; 30 cm reached 13.0 h into the storm; worst hour 19 mm (19% of the storm); water beside the road 0.04 m above its crest (design freeboard 0.30 m; P 0.99); road sag 0.9 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 19 mm; catchment 171.4 ha) (P 0.58); a culvert within 100 m is overtopped |
| 4 | 0.99 | Bellingham Street | Mendon | 0.52 m of water at peak; over 30 cm for 4.0 h; 30 cm reached 14.5 h into the storm; worst hour 19 mm (20% of the storm); a culvert within 100 m is overtopped |
| 5 | 0.98 | (unnamed) | Blackstone | 0.51 m of water at peak; over 30 cm for 6.0 h; 30 cm reached 12.5 h into the storm; worst hour 19 mm (19% of the storm); a culvert within 100 m is overtopped |
| 6 | 0.96 | Cemetery Street | Mendon | 0.48 m of water at peak; over 30 cm for 4.5 h; 30 cm reached 14.0 h into the storm; worst hour 19 mm (20% of the storm); a culvert within 100 m is overtopped |
| 7 | 0.94 | Little Tree Lane | Framingham | 0.46 m of water at peak; over 30 cm for 2.0 h; 30 cm reached 1.0 h into the storm; worst hour 6 mm (23% of the storm); a culvert within 100 m is overtopped |
| 8 | 0.93 | (unnamed) | Berlin | 0.44 m of water at peak; over 30 cm for 0.5 h; 30 cm reached 0.5 h into the storm; worst hour 3 mm (29% of the storm); water beside the road 0.42 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 0.9 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.15) |
| 9 | 0.91 | Belknap Road | Framingham | 0.44 m of water at peak; over 30 cm for 0.5 h; 30 cm reached 0.5 h into the storm; worst hour 6 mm (23% of the storm); a culvert within 100 m is overtopped |
| 10 | 0.91 | (unnamed) | Bellingham | 0.43 m of water at peak; over 30 cm for 5.0 h; 30 cm reached 13.5 h into the storm; worst hour 21 mm (21% of the storm); a culvert within 100 m is overtopped |
| 11 | 0.90 | Bartlett Street | Northborough | 0.43 m of water at peak; over 30 cm for 1.5 h; 30 cm reached 0.5 h into the storm; worst hour 6 mm (34% of the storm); a culvert within 100 m is overtopped |
| 12 | 0.90 | Route 62 | Berlin | 0.43 m of water at peak; over 30 cm for 0.5 h; 30 cm reached 0.5 h into the storm; worst hour 3 mm (29% of the storm); runoff beside / along the road at 0.6 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.14) |
| 13 | 0.89 | Maple Street | Northborough | 0.42 m of water at peak; over 30 cm for 0.5 h; 30 cm reached 0.5 h into the storm; worst hour 6 mm (37% of the storm); a culvert within 100 m is overtopped |
| 14 | 0.85 | Railroad Street | Bellingham | 0.41 m of water at peak; over 30 cm for 4.5 h; 30 cm reached 14.0 h into the storm; worst hour 20 mm (20% of the storm); water beside the road 0.49 m below its crest (design freeboard 0.30 m; P 0.11); a culvert within 100 m is overtopped |
| 15 | 0.84 | (unnamed) | Uxbridge | 0.40 m of water at peak; over 30 cm for 4.0 h; 30 cm reached 14.5 h into the storm; worst hour 23 mm (20% of the storm); water beside the road 0.28 m below its crest (design freeboard 0.30 m; P 0.56); runoff beside / along the road at 0.6 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.21); a culvert within 100 m is overtopped |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
