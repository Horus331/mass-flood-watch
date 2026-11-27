# Road-closure prototype: jul2021_proto_dm_jul2021_ref

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on GPU (cuda)), 20 m grid, storm from 2021-07-09T08:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 45,099 |
| Expected closures (sum of probabilities) | 119.2 |
| Segments with closure probability >= 50% | 20 (15.9 km) |
| Further segments that may close (stream reaches the road crest) | 128 (83.7 km) |
| Culverts overtopped / surcharged | 81 / 4 of 10736 |
| Road segments cut off from hospitals | 298 |
| Worst added trip time to a hospital | 14.7 min |
| Heaviest hour of rain | 28.7 mm |
| Flood model run time | 226 s |

## Checks against what happened

- Storm-day flood reports in the area: 9; water >= 10 cm within 100 m of 11% of them, vs 20% of random points (any day).
- Segments flagged impassable are 10.38x as likely as an average segment to have a report within 200 m.
- MassDOT repeating flood sites in the area: 30; 1 have a segment within 150 m at P >= 0.5 (share of all segments at P >= 0.5: 0.0%).

## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 1.00 | (unnamed) | Framingham | 1.42 m of water at peak; over 30 cm for 10.0 h; 30 cm reached 8.5 h into the storm; worst hour 18 mm (26% of the storm); water beside the road 1.15 m above its crest (design freeboard 0.30 m; P 1.00); road sag 2.9 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 18 mm; catchment 15.3 ha) (P 1.00) |
| 2 | 1.00 | East Park Terrace | Worcester | 0.71 m of water at peak; over 30 cm for 9.5 h; 30 cm reached 9.0 h into the storm; worst hour 14 mm (26% of the storm); water beside the road 0.61 m above its crest (design freeboard 0.30 m; P 1.00); road sag 4.3 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 14 mm; catchment 127.8 ha) (P 1.00) |
| 3 | 0.99 | Pine Grove Avenue | Bellingham | 0.55 m of water at peak; over 30 cm for 10.0 h; 30 cm reached 8.5 h into the storm; worst hour 13 mm (19% of the storm); a culvert within 100 m is overtopped |
| 4 | 0.99 | Route 117 | Lancaster | 0.53 m of water at peak; over 30 cm for 18.0 h; 30 cm reached 0.5 h into the storm; worst hour 14 mm (27% of the storm) |
| 5 | 0.99 | Paine Street | Bellingham | 0.52 m of water at peak; over 30 cm for 9.5 h; 30 cm reached 9.0 h into the storm; worst hour 13 mm (19% of the storm); a culvert within 100 m is overtopped |
| 6 | 0.98 | Cambridge Street | Worcester | 0.52 m of water at peak; over 30 cm for 6.0 h; 30 cm reached 12.5 h into the storm; worst hour 13 mm (25% of the storm); water beside the road 0.37 m above its crest (design freeboard 0.30 m; P 1.00); road sag 2.0 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 13 mm; catchment 77.2 ha) (P 0.98) |
| 7 | 0.97 | Shrewsbury Street | Worcester | 0.49 m of water at peak; over 30 cm for 8.0 h; 30 cm reached 10.5 h into the storm; worst hour 14 mm (27% of the storm); water beside the road 0.41 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.9 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 14 mm; catchment 127.8 ha) (P 0.99) |
| 8 | 0.81 | Shrewsbury Street | Worcester | 0.39 m of water at peak; over 30 cm for 7.0 h; 30 cm reached 11.5 h into the storm; worst hour 14 mm (27% of the storm); water beside the road 0.31 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.9 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 14 mm; catchment 127.8 ha) (P 0.99) |
| 9 | 0.80 | Wrentham Road | Bellingham | 0.39 m of water at peak; over 30 cm for 9.5 h; 30 cm reached 9.0 h into the storm; worst hour 13 mm (19% of the storm); water beside the road 0.18 m below its crest (design freeboard 0.30 m; P 0.79); a culvert within 100 m is overtopped |
| 10 | 0.75 | Fantasia Drive | Worcester | 0.37 m of water at peak; over 30 cm for 6.5 h; 30 cm reached 12.0 h into the storm; worst hour 14 mm (26% of the storm); water beside the road 0.30 m above its crest (design freeboard 0.30 m; P 1.00); road sag 1.3 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 14 mm; catchment 127.8 ha) (P 0.75) |
| 11 | 0.74 | Coolidge Road | Worcester | 0.37 m of water at peak; over 30 cm for 4.5 h; 30 cm reached 12.0 h into the storm; worst hour 13 mm (28% of the storm); water beside the road 0.49 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.7 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 13 mm; catchment 17.7 ha) (P 0.98) |
| 12 | 0.72 | Route 9 | Framingham | 0.36 m of water at peak; over 30 cm for 2.0 h; 30 cm reached 2.0 h into the storm; worst hour 17 mm (29% of the storm); a culvert within 100 m is overtopped |
| 13 | 0.72 | Route 9 | Framingham | 0.36 m of water at peak; over 30 cm for 2.0 h; 30 cm reached 2.0 h into the storm; worst hour 17 mm (29% of the storm); a culvert within 100 m is overtopped |
| 14 | 0.70 | Kinnicutt Road | Worcester | 0.35 m of water at peak; over 30 cm for 2.0 h; 30 cm reached 10.5 h into the storm; worst hour 14 mm (29% of the storm); water beside the road 0.25 m above its crest (design freeboard 0.30 m; P 1.00) |
| 15 | 0.70 | Martin Luther King Jr Boulevard | Worcester | 0.35 m of water at peak; over 30 cm for 9.0 h; 30 cm reached 9.5 h into the storm; worst hour 14 mm (27% of the storm); water beside the road 0.27 m above its crest (design freeboard 0.30 m; P 1.00); road sag 3.2 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 14 mm; catchment 60.2 ha) (P 0.70) |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
