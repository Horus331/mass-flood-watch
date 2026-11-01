# Road-closure prototype: may2018_loss_may2018_shrewsbury_20m

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on CPU (OpenMP)), 20 m grid, storm from 2018-05-15T14:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 9,355 |
| Expected closures (sum of probabilities) | 21.8 |
| Segments with closure probability >= 50% | 5 (3.1 km) |
| Further segments that may close (stream reaches the road crest) | 13 (8.1 km) |
| Culverts overtopped / surcharged | 15 / 0 of 1400 |
| Road segments cut off from hospitals | 40 |
| Worst added trip time to a hospital | 11.7 min |
| Heaviest hour of rain | 17.3 mm |
| Flood model run time | 1145 s |

## Checks against what happened

- Storm-day flood reports in the area: 1; water >= 10 cm within 100 m of 0% of them, vs 12% of random points (any day).
- Segments flagged impassable are 0.0x as likely as an average segment to have a report within 200 m.
- MassDOT repeating flood sites in the area: 10; 0 have a segment within 150 m at P >= 0.5 (share of all segments at P >= 0.5: 0.1%).

## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 1.00 | Martin Luther King Jr Boulevard | Worcester | 1.59 m of water at peak; over 30 cm for 17.5 h; 30 cm reached 1.0 h into the storm; worst hour 12 mm (66% of the storm); water beside the road 1.51 m above its crest (design freeboard 0.30 m; P 1.00); road sag 3.2 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 12 mm; catchment 60.2 ha) (P 1.00) |
| 2 | 1.00 | Martin Luther King Jr Boulevard | Worcester | 0.89 m of water at peak; over 30 cm for 17.5 h; 30 cm reached 1.0 h into the storm; worst hour 12 mm (66% of the storm); water beside the road 0.38 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 0.6 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.11); road sag 3.2 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 12 mm; catchment 60.2 ha) (P 1.00) |
| 3 | 1.00 | Foster Street | Worcester | 1.00 m of water at peak; over 30 cm for 16.0 h; 30 cm reached 2.5 h into the storm; worst hour 12 mm (66% of the storm); water beside the road 0.40 m below its crest (design freeboard 0.30 m; P 0.25); a culvert within 100 m is overtopped |
| 4 | 0.79 | Bearfoot Road | Northborough | 0.38 m of water at peak; worst hour 12 mm (63% of the storm); water beside the road 0.16 m below its crest (design freeboard 0.30 m; P 0.82); a culvert within 100 m is overtopped |
| 5 | 0.68 | Stafford Street | Worcester | 0.35 m of water at peak; over 30 cm for 0.5 h; 30 cm reached 0.5 h into the storm; worst hour 16 mm (71% of the storm); a culvert within 100 m is overtopped |
| 6 | 0.35 | James Street | Worcester | 0.26 m of water at peak; worst hour 15 mm (70% of the storm); a culvert within 100 m is overtopped |
| 7 | 0.30 | Millbury Street | Grafton | 0.25 m of water at peak; worst hour 7 mm (51% of the storm) |
| 8 | 0.22 | Rockland Road | Auburn | 0.22 m of water at peak; worst hour 14 mm (70% of the storm); a culvert within 100 m is overtopped |
| 9 | 0.19 | Ramp-West Boylston Dr To Rt 190 Nb | Worcester | 0.21 m of water at peak; worst hour 12 mm (56% of the storm); water beside the road 0.07 m above its crest (design freeboard 0.30 m; P 0.99); road sag 0.8 m deep (underpass, drains sized for the 50-yr hour, 58 mm; peak hour here 12 mm; catchment 52.2 ha) (P 0.20) |
| 10 | 0.18 | Route 12 | Auburn | 0.21 m of water at peak; worst hour 14 mm (68% of the storm); runoff beside / along the road at 1.5 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.12); a culvert within 100 m is overtopped |
| 11 | 0.14 | Washington Street | Worcester | 0.19 m of water at peak; worst hour 12 mm (66% of the storm); water beside the road 0.17 m below its crest (design freeboard 0.30 m; P 0.81); a culvert within 100 m is overtopped |
| 12 | 0.10 | Ramp-Rt 12 Nb To Rt 190 Nb | Worcester | 0.17 m of water at peak; worst hour 12 mm (57% of the storm); water beside the road 0.10 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.8 m deep (underpass, drains sized for the 50-yr hour, 58 mm; peak hour here 12 mm; catchment 52.2 ha) (P 0.20) |
| 13 | 0.10 | (unnamed) | Westborough | 0.17 m of water at peak; worst hour 14 mm (67% of the storm); a culvert within 100 m is overtopped |
| 14 | 0.10 | Hampton Street | Auburn | 0.17 m of water at peak; worst hour 13 mm (68% of the storm); water beside the road 0.42 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 0.8 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.21); a culvert within 100 m is overtopped |
| 15 | 0.06 | West Boylston Drive | Worcester | 0.15 m of water at peak; worst hour 12 mm (56% of the storm) |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
