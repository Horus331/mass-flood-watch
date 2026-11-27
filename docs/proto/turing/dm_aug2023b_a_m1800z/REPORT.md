# Road-closure prototype: aug2023b_proto_dm_aug2023b_a_m1800z

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on GPU (cuda)), 20 m grid, storm from 2023-08-18T00:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 45,099 |
| Expected closures (sum of probabilities) | 309.9 |
| Segments with closure probability >= 50% | 117 (89.3 km) |
| Further segments that may close (stream reaches the road crest) | 223 (150.5 km) |
| Culverts overtopped / surcharged | 583 / 7 of 10736 |
| Road segments cut off from hospitals | 2003 |
| Worst added trip time to a hospital | 57.7 min |
| Heaviest hour of rain | 46.0 mm |
| Flood model run time | 330 s |

## Checks against what happened

- Storm-day flood reports in the area: 3; water >= 10 cm within 100 m of 33% of them, vs 27% of random points (any day).
- Segments flagged impassable are 0.0x as likely as an average segment to have a report within 200 m.
- MassDOT repeating flood sites in the area: 30; 2 have a segment within 150 m at P >= 0.5 (share of all segments at P >= 0.5: 0.3%).

## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 1.00 | (unnamed) | Framingham | 1.20 m of water at peak; over 30 cm for 7.5 h; 30 cm reached 16.0 h into the storm; worst hour 29 mm (52% of the storm); water beside the road 0.93 m above its crest (design freeboard 0.30 m; P 1.00); road sag 2.9 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 28 mm; catchment 15.3 ha) (P 1.00) |
| 2 | 1.00 | Route 117 | Lancaster | 1.05 m of water at peak; over 30 cm for 23.0 h; 30 cm reached 0.5 h into the storm; worst hour 38 mm (55% of the storm); culvert (Trib to Still River): headwater 5.10 m vs road crest 2.74 m, 27.2 m3/s |
| 3 | 1.00 | Depot Street | Fitchburg | 0.80 m of water at peak; over 30 cm for 10.0 h; 30 cm reached 0.5 h into the storm; worst hour 41 mm (53% of the storm); a culvert within 100 m is overtopped |
| 4 | 1.00 | (unnamed) | Barre | 0.66 m of water at peak; over 30 cm for 7.5 h; 30 cm reached 15.5 h into the storm; worst hour 42 mm (55% of the storm); water beside the road 0.37 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 0.6 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.17); a culvert within 100 m is overtopped |
| 5 | 1.00 | Route 67 | Barre | 0.65 m of water at peak; over 30 cm for 7.5 h; 30 cm reached 15.5 h into the storm; worst hour 42 mm (55% of the storm); a culvert within 100 m is overtopped |
| 6 | 1.00 | (unnamed) | Spencer | 0.78 m of water at peak; over 30 cm for 8.5 h; 30 cm reached 15.0 h into the storm; worst hour 43 mm (58% of the storm) |
| 7 | 1.00 | West Brookfield Road | New Braintree | 0.65 m of water at peak; over 30 cm for 5.0 h; 30 cm reached 16.0 h into the storm; worst hour 46 mm (58% of the storm); a culvert within 100 m is overtopped |
| 8 | 1.00 | Route 12 | Fitchburg | 0.57 m of water at peak; over 30 cm for 8.0 h; 30 cm reached 15.5 h into the storm; worst hour 41 mm (53% of the storm); a culvert within 100 m is overtopped |
| 9 | 0.99 | John Fitch Highway | Fitchburg | 0.55 m of water at peak; over 30 cm for 7.5 h; 30 cm reached 16.0 h into the storm; worst hour 42 mm (55% of the storm) |
| 10 | 0.99 | Route 67 | North Brookfield | 0.55 m of water at peak; over 30 cm for 5.0 h; 30 cm reached 15.5 h into the storm; worst hour 46 mm (59% of the storm); a culvert within 100 m is overtopped |
| 11 | 0.99 | Mill Road | North Brookfield | 0.55 m of water at peak; over 30 cm for 4.0 h; 30 cm reached 15.0 h into the storm; worst hour 45 mm (58% of the storm); a culvert within 100 m is overtopped |
| 12 | 0.99 | Reservoir Road | Lunenburg | 0.52 m of water at peak; over 30 cm for 7.5 h; 30 cm reached 16.0 h into the storm; worst hour 42 mm (53% of the storm); culvert (N. Branch Catacunemaug): headwater 1.73 m vs road crest 1.07 m, 1.5 m3/s |
| 13 | 0.98 | Cider Mill Road | North Brookfield | 0.52 m of water at peak; over 30 cm for 3.5 h; 30 cm reached 15.5 h into the storm; worst hour 46 mm (59% of the storm); a culvert within 100 m is overtopped |
| 14 | 0.98 | Water Street | Leominster | 0.50 m of water at peak; over 30 cm for 7.0 h; 30 cm reached 16.5 h into the storm; worst hour 41 mm (56% of the storm); a culvert within 100 m is overtopped |
| 15 | 0.97 | (unnamed) | Leominster | 0.49 m of water at peak; over 30 cm for 7.0 h; 30 cm reached 16.5 h into the storm; worst hour 42 mm (56% of the storm); a culvert within 100 m is overtopped |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
