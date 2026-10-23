# Road-closure prototype: may2018_loss_may2018_shrewsbury_20m

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on CPU (OpenMP)), 20 m grid, storm from 2018-05-15T14:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 9,355 |
| Expected closures (sum of probabilities) | 24.1 |
| Segments with closure probability >= 50% | 6 (2.6 km) |
| Further segments that may close (stream reaches the road crest) | 13 (8.1 km) |
| Culverts overtopped / surcharged | 17 / 0 of 1400 |
| Road segments cut off from hospitals | 42 |
| Worst added trip time to a hospital | 11.7 min |
| Heaviest hour of rain | 17.3 mm |
| Flood model run time | 1229 s |

## Checks against what happened

- Storm-day flood reports in the area: 1; water >= 10 cm within 100 m of 0% of them, vs 12% of random points (any day).
- Segments flagged impassable are 0.0x as likely as an average segment to have a report within 200 m.
- MassDOT repeating flood sites in the area: 10; 0 have a segment within 150 m at P >= 0.5 (share of all segments at P >= 0.5: 0.1%).

## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 1.00 | Martin Luther King Jr Boulevard | Worcester | 1.25 m of water at peak; over 30 cm for 17.5 h; 30 cm reached 1.0 h into the storm; worst hour 12 mm (66% of the storm); water beside the road 1.17 m above its crest (design freeboard 0.30 m; P 1.00); road sag 3.2 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 12 mm; catchment 60.2 ha) (P 1.00) |
| 2 | 1.00 | Foster Street | Worcester | 0.69 m of water at peak; over 30 cm for 11.5 h; 30 cm reached 7.0 h into the storm; worst hour 12 mm (66% of the storm); water beside the road 0.40 m below its crest (design freeboard 0.30 m; P 0.25); a culvert within 100 m is overtopped |
| 3 | 1.00 | Foster Street | Worcester | 0.69 m of water at peak; over 30 cm for 11.5 h; 30 cm reached 7.0 h into the storm; worst hour 12 mm (66% of the storm); water beside the road 0.28 m below its crest (design freeboard 0.30 m; P 0.55); a culvert within 100 m is overtopped |
| 4 | 0.99 | Martin Luther King Jr Boulevard | Worcester | 0.55 m of water at peak; over 30 cm for 17.5 h; 30 cm reached 1.0 h into the storm; worst hour 12 mm (66% of the storm); water beside the road 0.04 m above its crest (design freeboard 0.30 m; P 0.99); runoff beside / along the road at 0.6 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.11); road sag 3.2 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 12 mm; catchment 60.2 ha) (P 1.00) |
| 5 | 0.99 | (unnamed) | Worcester | 0.52 m of water at peak; over 30 cm for 6.5 h; 30 cm reached 12.0 h into the storm; worst hour 14 mm (69% of the storm); a culvert within 100 m is overtopped |
| 6 | 0.83 | Bearfoot Road | Northborough | 0.40 m of water at peak; worst hour 12 mm (63% of the storm); water beside the road 0.16 m below its crest (design freeboard 0.30 m; P 0.82); a culvert within 100 m is overtopped |
| 7 | 0.42 | Stafford Street | Worcester | 0.28 m of water at peak; worst hour 16 mm (71% of the storm); a culvert within 100 m is overtopped |
| 8 | 0.42 | Ludlow Street | Worcester | 0.28 m of water at peak; worst hour 16 mm (70% of the storm); a culvert within 100 m is overtopped |
| 9 | 0.33 | Providence Street | Millbury | 0.26 m of water at peak; worst hour 10 mm (59% of the storm); a culvert within 100 m is overtopped |
| 10 | 0.30 | Millbury Street | Grafton | 0.25 m of water at peak; worst hour 7 mm (51% of the storm) |
| 11 | 0.21 | James Street | Worcester | 0.22 m of water at peak; worst hour 15 mm (70% of the storm); a culvert within 100 m is overtopped |
| 12 | 0.20 | Ramp-West Boylston Dr To Rt 190 Nb | Worcester | 0.21 m of water at peak; worst hour 12 mm (56% of the storm); water beside the road 0.07 m above its crest (design freeboard 0.30 m; P 0.99); road sag 0.8 m deep (underpass, drains sized for the 50-yr hour, 58 mm; peak hour here 12 mm; catchment 52.2 ha) (P 0.20) |
| 13 | 0.18 | Route 12 | Auburn | 0.21 m of water at peak; worst hour 14 mm (68% of the storm); runoff beside / along the road at 1.5 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.10); a culvert within 100 m is overtopped |
| 14 | 0.13 | Washington Street | Worcester | 0.19 m of water at peak; worst hour 12 mm (66% of the storm); water beside the road 0.17 m below its crest (design freeboard 0.30 m; P 0.80); a culvert within 100 m is overtopped |
| 15 | 0.11 | Hampton Street | Auburn | 0.18 m of water at peak; worst hour 13 mm (68% of the storm); water beside the road 0.42 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 0.7 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.21); a culvert within 100 m is overtopped |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
