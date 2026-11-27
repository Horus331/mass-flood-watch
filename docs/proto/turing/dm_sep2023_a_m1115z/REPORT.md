# Road-closure prototype: sep2023_proto_dm_sep2023_a_m1115z

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on GPU (cuda)), 20 m grid, storm from 2023-09-11T15:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 45,099 |
| Expected closures (sum of probabilities) | 107.3 |
| Segments with closure probability >= 50% | 24 (19.6 km) |
| Further segments that may close (stream reaches the road crest) | 64 (47.1 km) |
| Culverts overtopped / surcharged | 109 / 6 of 10736 |
| Road segments cut off from hospitals | 244 |
| Worst added trip time to a hospital | 47.9 min |
| Heaviest hour of rain | 38.3 mm |
| Flood model run time | 472 s |

## Checks against what happened

- Storm-day flood reports in the area: 11; water >= 10 cm within 100 m of 0% of them, vs 6% of random points (any day).
- Segments flagged impassable are 0.0x as likely as an average segment to have a report within 200 m.
- MassDOT repeating flood sites in the area: 30; 0 have a segment within 150 m at P >= 0.5 (share of all segments at P >= 0.5: 0.1%).

## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 1.00 | Ash Street | Clinton | 1.07 m of water at peak; over 30 cm for 10.5 h; 30 cm reached 27.0 h into the storm; worst hour 4 mm (25% of the storm); water beside the road 0.86 m above its crest (design freeboard 0.30 m; P 1.00) |
| 2 | 1.00 | Ash Street | Clinton | 0.74 m of water at peak; over 30 cm for 5.5 h; 30 cm reached 32.0 h into the storm; worst hour 4 mm (25% of the storm); water beside the road 0.67 m above its crest (design freeboard 0.30 m; P 1.00) |
| 3 | 0.99 | Pine Grove Avenue | Bellingham | 0.56 m of water at peak; over 30 cm for 19.0 h; 30 cm reached 7.5 h into the storm; worst hour 21 mm (31% of the storm); a culvert within 100 m is overtopped |
| 4 | 0.99 | Paine Street | Bellingham | 0.53 m of water at peak; over 30 cm for 15.0 h; 30 cm reached 8.0 h into the storm; worst hour 22 mm (30% of the storm); a culvert within 100 m is overtopped |
| 5 | 0.93 | (unnamed) | Barre | 0.45 m of water at peak; over 30 cm for 6.5 h; 30 cm reached 10.5 h into the storm; worst hour 38 mm (51% of the storm); water beside the road 0.28 m above its crest (design freeboard 0.30 m; P 1.00); a culvert within 100 m is overtopped |
| 6 | 0.93 | Wrentham Road | Bellingham | 0.45 m of water at peak; over 30 cm for 14.0 h; 30 cm reached 7.5 h into the storm; worst hour 22 mm (30% of the storm); water beside the road 0.11 m below its crest (design freeboard 0.30 m; P 0.89); a culvert within 100 m is overtopped |
| 7 | 0.92 | Route 67 | Barre | 0.44 m of water at peak; over 30 cm for 6.5 h; 30 cm reached 10.5 h into the storm; worst hour 38 mm (51% of the storm); a culvert within 100 m is overtopped |
| 8 | 0.88 | West Brookfield Road | New Braintree | 0.42 m of water at peak; over 30 cm for 4.0 h; 30 cm reached 11.0 h into the storm; worst hour 35 mm (47% of the storm); a culvert within 100 m is overtopped |
| 9 | 0.78 | Belknap Road | Framingham | 0.38 m of water at peak; over 30 cm for 0.5 h; 30 cm reached 0.5 h into the storm; worst hour 5 mm (24% of the storm); a culvert within 100 m is overtopped |
| 10 | 0.77 | Maple Street | Northborough | 0.37 m of water at peak; over 30 cm for 0.5 h; 30 cm reached 0.5 h into the storm; worst hour 6 mm (29% of the storm); a culvert within 100 m is overtopped |
| 11 | 0.74 | Mill Road | North Brookfield | 0.37 m of water at peak; over 30 cm for 3.0 h; 30 cm reached 10.0 h into the storm; worst hour 32 mm (46% of the storm); a culvert within 100 m is overtopped |
| 12 | 0.70 | (unnamed) | Berlin | 0.35 m of water at peak; over 30 cm for 0.5 h; 30 cm reached 0.5 h into the storm; worst hour 3 mm (23% of the storm); water beside the road 0.42 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 1.1 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.13) |
| 13 | 0.68 | Route 62 | Berlin | 0.35 m of water at peak; over 30 cm for 0.5 h; 30 cm reached 0.5 h into the storm; worst hour 3 mm (23% of the storm); runoff beside / along the road at 1.1 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.13) |
| 14 | 0.58 | Bartlett Street | Northborough | 0.32 m of water at peak; over 30 cm for 1.5 h; 30 cm reached 0.5 h into the storm; worst hour 6 mm (27% of the storm); a culvert within 100 m is overtopped |
| 15 | 0.58 | Amy Road | Framingham | 0.32 m of water at peak; worst hour 5 mm (23% of the storm); water beside the road 1.53 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.5 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 5 mm; catchment 15.6 ha) (P 0.99) |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
