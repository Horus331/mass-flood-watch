# Road-closure prototype: aug2021_proto_dm_aug2021_a_m1911z

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on GPU (cuda)), 20 m grid, storm from 2021-08-19T11:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 45,099 |
| Expected closures (sum of probabilities) | 161.3 |
| Segments with closure probability >= 50% | 49 (40.9 km) |
| Further segments that may close (stream reaches the road crest) | 122 (82.5 km) |
| Culverts overtopped / surcharged | 196 / 8 of 10736 |
| Road segments cut off from hospitals | 635 |
| Worst added trip time to a hospital | 29.2 min |
| Heaviest hour of rain | 55.7 mm |
| Flood model run time | 236 s |

## Checks against what happened

- Storm-day flood reports in the area: 10; water >= 10 cm within 100 m of 30% of them, vs 18% of random points (any day).
- Segments flagged impassable are 1.88x as likely as an average segment to have a report within 200 m.
- MassDOT repeating flood sites in the area: 30; 2 have a segment within 150 m at P >= 0.5 (share of all segments at P >= 0.5: 0.1%).

## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 1.00 | Route 117 | Lancaster | 0.81 m of water at peak; over 30 cm for 16.0 h; 30 cm reached 0.5 h into the storm; worst hour 12 mm (19% of the storm); culvert (Trib to Still River): headwater 2.53 m vs road crest 2.74 m, 14.7 m3/s |
| 2 | 1.00 | Wrentham Road | Bellingham | 0.78 m of water at peak; over 30 cm for 11.0 h; 30 cm reached 5.5 h into the storm; worst hour 44 mm (44% of the storm); water beside the road 0.21 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.9 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 44 mm; catchment 171.4 ha) (P 0.97); a culvert within 100 m is overtopped |
| 3 | 1.00 | Paine Street | Bellingham | 1.04 m of water at peak; over 30 cm for 10.5 h; 30 cm reached 6.0 h into the storm; worst hour 46 mm (45% of the storm); a culvert within 100 m is overtopped |
| 4 | 1.00 | Pine Grove Avenue | Bellingham | 1.05 m of water at peak; over 30 cm for 11.0 h; 30 cm reached 5.5 h into the storm; worst hour 44 mm (44% of the storm); water beside the road 0.24 m below its crest (design freeboard 0.30 m; P 0.65); a culvert within 100 m is overtopped |
| 5 | 1.00 | (unnamed) | Southbridge | 1.04 m of water at peak; over 30 cm for 11.5 h; 30 cm reached 5.0 h into the storm; worst hour 20 mm (26% of the storm); culvert (Unnamed tributary): headwater 22.08 m vs road crest 0.49 m, 0.6 m3/s |
| 6 | 1.00 | East Park Terrace | Worcester | 0.66 m of water at peak; over 30 cm for 10.0 h; 30 cm reached 6.5 h into the storm; worst hour 16 mm (27% of the storm); water beside the road 0.56 m above its crest (design freeboard 0.30 m; P 1.00); road sag 4.3 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 16 mm; catchment 127.8 ha) (P 1.00) |
| 7 | 1.00 | (unnamed) | Blackstone | 0.63 m of water at peak; over 30 cm for 11.0 h; 30 cm reached 5.5 h into the storm; worst hour 35 mm (40% of the storm); a culvert within 100 m is overtopped |
| 8 | 0.99 | Bellingham Street | Mendon | 0.54 m of water at peak; over 30 cm for 6.0 h; 30 cm reached 8.0 h into the storm; worst hour 30 mm (36% of the storm); a culvert within 100 m is overtopped |
| 9 | 0.98 | Cambridge Street | Worcester | 0.50 m of water at peak; over 30 cm for 6.5 h; 30 cm reached 10.0 h into the storm; worst hour 15 mm (26% of the storm); water beside the road 0.36 m above its crest (design freeboard 0.30 m; P 1.00); road sag 2.0 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 15 mm; catchment 77.2 ha) (P 0.98) |
| 10 | 0.98 | Little Tree Lane | Framingham | 0.50 m of water at peak; over 30 cm for 2.0 h; 30 cm reached 1.0 h into the storm; worst hour 19 mm (32% of the storm); a culvert within 100 m is overtopped |
| 11 | 0.97 | Cemetery Street | Mendon | 0.49 m of water at peak; over 30 cm for 4.5 h; 30 cm reached 7.5 h into the storm; worst hour 31 mm (38% of the storm); a culvert within 100 m is overtopped |
| 12 | 0.96 | Wrentham Road | Bellingham | 0.47 m of water at peak; over 30 cm for 4.5 h; 30 cm reached 5.5 h into the storm; worst hour 44 mm (44% of the storm); a culvert within 100 m is overtopped |
| 13 | 0.95 | (unnamed) | Bellingham | 0.47 m of water at peak; over 30 cm for 4.0 h; 30 cm reached 5.5 h into the storm; worst hour 44 mm (44% of the storm); a culvert within 100 m is overtopped |
| 14 | 0.95 | West Street | Wrentham | 0.46 m of water at peak; over 30 cm for 5.0 h; 30 cm reached 5.0 h into the storm; worst hour 44 mm (43% of the storm); runoff beside / along the road at 0.8 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.34); a culvert within 100 m is overtopped |
| 15 | 0.94 | West Brookfield Road | New Braintree | 0.45 m of water at peak; over 30 cm for 5.0 h; 30 cm reached 5.5 h into the storm; worst hour 20 mm (24% of the storm); a culvert within 100 m is overtopped |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
