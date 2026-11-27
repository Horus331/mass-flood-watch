# Road-closure prototype: aug2023_proto_dm_aug2023_a_m0800z

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on GPU (cuda)), 20 m grid, storm from 2023-08-08T00:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 45,099 |
| Expected closures (sum of probabilities) | 146.2 |
| Segments with closure probability >= 50% | 46 (36.6 km) |
| Further segments that may close (stream reaches the road crest) | 116 (80.4 km) |
| Culverts overtopped / surcharged | 144 / 5 of 10736 |
| Road segments cut off from hospitals | 633 |
| Worst added trip time to a hospital | 26.0 min |
| Heaviest hour of rain | 38.7 mm |
| Flood model run time | 307 s |

## Checks against what happened

- Storm-day flood reports in the area: 7; water >= 10 cm within 100 m of 29% of them, vs 13% of random points (any day).
- Segments flagged impassable are 4.93x as likely as an average segment to have a report within 200 m.
- MassDOT repeating flood sites in the area: 30; 2 have a segment within 150 m at P >= 0.5 (share of all segments at P >= 0.5: 0.1%).

## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 1.00 | (unnamed) | Framingham | 1.97 m of water at peak; over 30 cm for 14.0 h; 30 cm reached 11.5 h into the storm; worst hour 25 mm (20% of the storm); water beside the road 1.71 m above its crest (design freeboard 0.30 m; P 1.00); road sag 2.9 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 25 mm; catchment 15.3 ha) (P 1.00) |
| 2 | 1.00 | Paine Street | Bellingham | 0.72 m of water at peak; over 30 cm for 12.0 h; 30 cm reached 13.5 h into the storm; worst hour 26 mm (28% of the storm); a culvert within 100 m is overtopped |
| 3 | 1.00 | Pine Grove Avenue | Bellingham | 0.74 m of water at peak; over 30 cm for 13.0 h; 30 cm reached 12.5 h into the storm; worst hour 26 mm (28% of the storm); a culvert within 100 m is overtopped |
| 4 | 1.00 | (unnamed) | Holliston | 0.61 m of water at peak; over 30 cm for 12.5 h; 30 cm reached 13.0 h into the storm; worst hour 26 mm (20% of the storm); a culvert within 100 m is overtopped |
| 5 | 1.00 | (unnamed) | Blackstone | 0.62 m of water at peak; over 30 cm for 11.5 h; 30 cm reached 14.0 h into the storm; worst hour 26 mm (28% of the storm); a culvert within 100 m is overtopped |
| 6 | 1.00 | (unnamed) | Holliston | 0.59 m of water at peak; over 30 cm for 12.0 h; 30 cm reached 13.5 h into the storm; worst hour 24 mm (18% of the storm); a culvert within 100 m is overtopped |
| 7 | 1.00 | Little Tree Lane | Framingham | 0.56 m of water at peak; over 30 cm for 13.0 h; 30 cm reached 1.0 h into the storm; worst hour 30 mm (23% of the storm); a culvert within 100 m is overtopped |
| 8 | 0.99 | Hopping Brook Road | Holliston | 0.54 m of water at peak; over 30 cm for 12.0 h; 30 cm reached 13.5 h into the storm; worst hour 26 mm (20% of the storm); a culvert within 100 m is overtopped |
| 9 | 0.99 | Route 9 | Framingham | 0.54 m of water at peak; over 30 cm for 13.5 h; 30 cm reached 2.0 h into the storm; worst hour 33 mm (24% of the storm); water beside the road 0.09 m above its crest (design freeboard 0.30 m; P 1.00); a culvert within 100 m is overtopped |
| 10 | 0.99 | Route 9 | Framingham | 0.54 m of water at peak; over 30 cm for 13.5 h; 30 cm reached 2.0 h into the storm; worst hour 32 mm (24% of the storm); a culvert within 100 m is overtopped |
| 11 | 0.99 | Richard Road | Holliston | 0.53 m of water at peak; over 30 cm for 6.5 h; 30 cm reached 13.5 h into the storm; worst hour 27 mm (19% of the storm); a culvert within 100 m is overtopped |
| 12 | 0.99 | Wrentham Road | Bellingham | 0.52 m of water at peak; over 30 cm for 12.0 h; 30 cm reached 13.5 h into the storm; worst hour 26 mm (28% of the storm); water beside the road 0.05 m below its crest (design freeboard 0.30 m; P 0.95); road sag 0.9 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 26 mm; catchment 171.4 ha) (P 0.26); a culvert within 100 m is overtopped |
| 13 | 0.98 | Bellingham Street | Mendon | 0.50 m of water at peak; over 30 cm for 11.0 h; 30 cm reached 14.5 h into the storm; worst hour 26 mm (26% of the storm); a culvert within 100 m is overtopped |
| 14 | 0.97 | Beech Street | Bellingham | 0.48 m of water at peak; over 30 cm for 10.5 h; 30 cm reached 15.0 h into the storm; worst hour 26 mm (22% of the storm); a culvert within 100 m is overtopped |
| 15 | 0.96 | Fisher Street | Holliston | 0.48 m of water at peak; over 30 cm for 10.0 h; 30 cm reached 15.5 h into the storm; worst hour 26 mm (21% of the storm); culvert (Hopping Brook): headwater 2.24 m vs road crest 2.22 m, 11.9 m3/s |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
