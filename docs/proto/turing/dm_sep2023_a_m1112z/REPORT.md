# Road-closure prototype: sep2023_proto_dm_sep2023_a_m1112z

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on GPU (cuda)), 20 m grid, storm from 2023-09-11T12:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 45,099 |
| Expected closures (sum of probabilities) | 184.8 |
| Segments with closure probability >= 50% | 75 (56.3 km) |
| Further segments that may close (stream reaches the road crest) | 143 (106.0 km) |
| Culverts overtopped / surcharged | 250 / 5 of 10736 |
| Road segments cut off from hospitals | 773 |
| Worst added trip time to a hospital | 42.3 min |
| Heaviest hour of rain | 35.7 mm |
| Flood model run time | 534 s |

## Checks against what happened

- Storm-day flood reports in the area: 11; water >= 10 cm within 100 m of 0% of them, vs 11% of random points (any day).
- Segments flagged impassable are 3.07x as likely as an average segment to have a report within 200 m.
- MassDOT repeating flood sites in the area: 30; 0 have a segment within 150 m at P >= 0.5 (share of all segments at P >= 0.5: 0.2%).

## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 1.00 | Route 117 | Lancaster | 1.27 m of water at peak; over 30 cm for 40.0 h; 30 cm reached 0.5 h into the storm; worst hour 7 mm (14% of the storm); culvert (Trib to Still River): headwater 4.99 m vs road crest 2.74 m, 26.7 m3/s |
| 2 | 1.00 | Depot Street | Fitchburg | 1.04 m of water at peak; over 30 cm for 35.5 h; 30 cm reached 0.5 h into the storm; worst hour 14 mm (12% of the storm); a culvert within 100 m is overtopped |
| 3 | 1.00 | Paine Street | Bellingham | 1.37 m of water at peak; over 30 cm for 33.0 h; 30 cm reached 7.5 h into the storm; worst hour 30 mm (16% of the storm); a culvert within 100 m is overtopped |
| 4 | 1.00 | Wrentham Road | Bellingham | 1.06 m of water at peak; over 30 cm for 33.0 h; 30 cm reached 7.5 h into the storm; worst hour 30 mm (17% of the storm); water beside the road 0.50 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.9 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 30 mm; catchment 171.4 ha) (P 1.00); a culvert within 100 m is overtopped |
| 5 | 1.00 | Wrentham Road | Bellingham | 0.67 m of water at peak; over 30 cm for 13.5 h; 30 cm reached 7.5 h into the storm; worst hour 33 mm (18% of the storm); a culvert within 100 m is overtopped |
| 6 | 1.00 | Oakmont Avenue | Westminster | 0.71 m of water at peak; over 30 cm for 30.0 h; 30 cm reached 10.5 h into the storm; worst hour 16 mm (13% of the storm); runoff beside / along the road at 0.9 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.33); a culvert within 100 m is overtopped |
| 7 | 1.00 | Pine Grove Avenue | Bellingham | 1.36 m of water at peak; over 30 cm for 33.5 h; 30 cm reached 7.0 h into the storm; worst hour 30 mm (17% of the storm); water beside the road 0.13 m above its crest (design freeboard 0.30 m; P 1.00); a culvert within 100 m is overtopped |
| 8 | 1.00 | Lackey Lane | Barre | 0.82 m of water at peak; over 30 cm for 26.0 h; 30 cm reached 14.5 h into the storm; worst hour 16 mm (14% of the storm); water beside the road 0.14 m below its crest (design freeboard 0.30 m; P 0.85); a culvert within 100 m is overtopped |
| 9 | 1.00 | (unnamed) | Blackstone | 0.70 m of water at peak; over 30 cm for 25.5 h; 30 cm reached 7.0 h into the storm; worst hour 26 mm (18% of the storm); a culvert within 100 m is overtopped |
| 10 | 1.00 | (unnamed) | Bellingham | 0.69 m of water at peak; over 30 cm for 13.0 h; 30 cm reached 8.0 h into the storm; worst hour 30 mm (18% of the storm); a culvert within 100 m is overtopped |
| 11 | 1.00 | Railroad Street | Bellingham | 0.65 m of water at peak; over 30 cm for 11.5 h; 30 cm reached 8.5 h into the storm; worst hour 31 mm (18% of the storm); water beside the road 0.42 m below its crest (design freeboard 0.30 m; P 0.21); a culvert within 100 m is overtopped |
| 12 | 1.00 | (unnamed) | Bellingham | 0.66 m of water at peak; over 30 cm for 13.0 h; 30 cm reached 7.5 h into the storm; worst hour 32 mm (17% of the storm); a culvert within 100 m is overtopped |
| 13 | 1.00 | (unnamed) | Bellingham | 0.66 m of water at peak; over 30 cm for 12.5 h; 30 cm reached 9.5 h into the storm; worst hour 32 mm (18% of the storm); a culvert within 100 m is overtopped |
| 14 | 1.00 | Ash Street | Clinton | 1.33 m of water at peak; over 30 cm for 15.0 h; 30 cm reached 25.5 h into the storm; worst hour 7 mm (15% of the storm); water beside the road 1.12 m above its crest (design freeboard 0.30 m; P 1.00) |
| 15 | 1.00 | Ash Street | Clinton | 1.01 m of water at peak; over 30 cm for 10.5 h; 30 cm reached 30.0 h into the storm; worst hour 8 mm (15% of the storm); water beside the road 0.93 m above its crest (design freeboard 0.30 m; P 1.00) |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
