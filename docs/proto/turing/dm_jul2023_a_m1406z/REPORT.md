# Road-closure prototype: jul2023_proto_dm_jul2023_a_m1406z

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on GPU (cuda)), 20 m grid, storm from 2023-07-14T06:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 45,099 |
| Expected closures (sum of probabilities) | 177.5 |
| Segments with closure probability >= 50% | 72 (57.1 km) |
| Further segments that may close (stream reaches the road crest) | 133 (93.3 km) |
| Culverts overtopped / surcharged | 242 / 5 of 10736 |
| Road segments cut off from hospitals | 858 |
| Worst added trip time to a hospital | 31.4 min |
| Heaviest hour of rain | 31.3 mm |
| Flood model run time | 266 s |

## Checks against what happened

- Storm-day flood reports in the area: 4; water >= 10 cm within 100 m of 0% of them, vs 14% of random points (any day).
- Segments flagged impassable are 0.0x as likely as an average segment to have a report within 200 m.
- MassDOT repeating flood sites in the area: 30; 2 have a segment within 150 m at P >= 0.5 (share of all segments at P >= 0.5: 0.2%).

## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 1.00 | (unnamed) | Framingham | 0.91 m of water at peak; over 30 cm for 5.0 h; 30 cm reached 15.5 h into the storm; worst hour 22 mm (41% of the storm); water beside the road 0.65 m above its crest (design freeboard 0.30 m; P 1.00); road sag 2.9 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 22 mm; catchment 15.3 ha) (P 1.00) |
| 2 | 1.00 | Wrentham Road | Bellingham | 0.77 m of water at peak; over 30 cm for 6.5 h; 30 cm reached 14.0 h into the storm; worst hour 23 mm (24% of the storm); water beside the road 0.20 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.9 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 23 mm; catchment 171.4 ha) (P 0.97); a culvert within 100 m is overtopped |
| 3 | 1.00 | Paine Street | Bellingham | 1.05 m of water at peak; over 30 cm for 6.0 h; 30 cm reached 14.5 h into the storm; worst hour 22 mm (23% of the storm); a culvert within 100 m is overtopped |
| 4 | 1.00 | Pine Grove Avenue | Bellingham | 1.06 m of water at peak; over 30 cm for 6.5 h; 30 cm reached 14.0 h into the storm; worst hour 23 mm (24% of the storm); water beside the road 0.23 m below its crest (design freeboard 0.30 m; P 0.69); a culvert within 100 m is overtopped |
| 5 | 1.00 | (unnamed) | Southbridge | 0.80 m of water at peak; over 30 cm for 6.5 h; 30 cm reached 14.0 h into the storm; worst hour 25 mm (30% of the storm); culvert (Unnamed tributary): headwater 8.68 m vs road crest 0.49 m, 0.4 m3/s |
| 6 | 1.00 | (unnamed) | Blackstone | 0.92 m of water at peak; over 30 cm for 6.0 h; 30 cm reached 14.5 h into the storm; worst hour 23 mm (24% of the storm); a culvert within 100 m is overtopped |
| 7 | 1.00 | Cemetery Street | Mendon | 0.76 m of water at peak; over 30 cm for 5.5 h; 30 cm reached 15.0 h into the storm; worst hour 26 mm (27% of the storm); a culvert within 100 m is overtopped |
| 8 | 1.00 | Bellingham Street | Mendon | 0.80 m of water at peak; over 30 cm for 5.0 h; 30 cm reached 15.5 h into the storm; worst hour 28 mm (28% of the storm); a culvert within 100 m is overtopped |
| 9 | 1.00 | (unnamed) | Bellingham | 0.59 m of water at peak; over 30 cm for 6.0 h; 30 cm reached 14.5 h into the storm; worst hour 28 mm (28% of the storm); a culvert within 100 m is overtopped |
| 10 | 1.00 | Railroad Street | Bellingham | 0.56 m of water at peak; over 30 cm for 5.5 h; 30 cm reached 15.0 h into the storm; worst hour 27 mm (27% of the storm); water beside the road 0.44 m below its crest (design freeboard 0.30 m; P 0.17); a culvert within 100 m is overtopped |
| 11 | 0.99 | (unnamed) | Holliston | 0.56 m of water at peak; over 30 cm for 5.5 h; 30 cm reached 15.0 h into the storm; worst hour 31 mm (34% of the storm); a culvert within 100 m is overtopped |
| 12 | 0.99 | (unnamed) | Bellingham | 0.54 m of water at peak; over 30 cm for 4.5 h; 30 cm reached 16.0 h into the storm; worst hour 25 mm (25% of the storm); a culvert within 100 m is overtopped |
| 13 | 0.98 | Pulaski Boulevard | Bellingham | 0.51 m of water at peak; over 30 cm for 4.0 h; 30 cm reached 16.5 h into the storm; worst hour 26 mm (26% of the storm); a culvert within 100 m is overtopped |
| 14 | 0.97 | Hartford Avenue East | Mendon | 0.49 m of water at peak; over 30 cm for 3.5 h; 30 cm reached 15.0 h into the storm; worst hour 27 mm (28% of the storm); a culvert within 100 m is overtopped |
| 15 | 0.95 | Rogerson Crossing | Uxbridge | 0.47 m of water at peak; over 30 cm for 8.5 h; 30 cm reached 0.5 h into the storm; worst hour 21 mm (28% of the storm); a culvert within 100 m is overtopped |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
