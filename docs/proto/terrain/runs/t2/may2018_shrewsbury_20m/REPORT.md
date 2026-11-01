# Road-closure prototype: may2018_loss_may2018_shrewsbury_20m

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on CPU (OpenMP)), 20 m grid, storm from 2018-05-15T14:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 9,355 |
| Expected closures (sum of probabilities) | 16.9 |
| Segments with closure probability >= 50% | 1 (0.9 km) |
| Further segments that may close (stream reaches the road crest) | 6 (3.6 km) |
| Culverts overtopped / surcharged | 11 / 0 of 1400 |
| Road segments cut off from hospitals | 37 |
| Worst added trip time to a hospital | 11.7 min |
| Heaviest hour of rain | 17.3 mm |
| Flood model run time | 1187 s |

## Checks against what happened

- Storm-day flood reports in the area: 1; water >= 10 cm within 100 m of 0% of them, vs 9% of random points (any day).
- Segments flagged impassable are 0.0x as likely as an average segment to have a report within 200 m.
- MassDOT repeating flood sites in the area: 10; 0 have a segment within 150 m at P >= 0.5 (share of all segments at P >= 0.5: 0.0%).

## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 0.72 | Bearfoot Road | Northborough | 0.36 m of water at peak; worst hour 12 mm (63% of the storm); water beside the road 0.20 m below its crest (design freeboard 0.30 m; P 0.75); a culvert within 100 m is overtopped |
| 2 | 0.35 | Stafford Street | Worcester | 0.26 m of water at peak; worst hour 16 mm (71% of the storm); a culvert within 100 m is overtopped |
| 3 | 0.31 | Millbury Street | Grafton | 0.25 m of water at peak; worst hour 7 mm (51% of the storm) |
| 4 | 0.17 | Route 12 | Auburn | 0.20 m of water at peak; worst hour 14 mm (68% of the storm); a culvert within 100 m is overtopped |
| 5 | 0.16 | James Street | Worcester | 0.20 m of water at peak; worst hour 15 mm (70% of the storm); a culvert within 100 m is overtopped |
| 6 | 0.14 | Route 20 | Northborough | 0.19 m of water at peak; worst hour 13 mm (64% of the storm); a culvert within 100 m is overtopped |
| 7 | 0.10 | Martin Luther King Jr Boulevard | Worcester | 0.17 m of water at peak; worst hour 12 mm (66% of the storm); water beside the road 0.09 m above its crest (design freeboard 0.30 m; P 0.99); road sag 3.2 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 12 mm; catchment 60.2 ha) (P 0.10) |
| 8 | 0.10 | Hampton Street | Auburn | 0.17 m of water at peak; worst hour 13 mm (68% of the storm); water beside the road 0.42 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 0.7 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.21); a culvert within 100 m is overtopped |
| 9 | 0.05 | Auburn Street | Auburn | 0.13 m of water at peak; worst hour 12 mm (66% of the storm) |
| 10 | 0.05 | Dawson Road | Worcester | 0.13 m of water at peak; worst hour 12 mm (56% of the storm) |
| 11 | 0.05 | Ramp-Church St To Rt 290 Wb | Northborough | 0.13 m of water at peak; worst hour 15 mm (66% of the storm) |
| 12 | 0.04 | Washington Street | Worcester | 0.13 m of water at peak; worst hour 12 mm (66% of the storm); water beside the road 0.21 m below its crest (design freeboard 0.30 m; P 0.74) |
| 13 | 0.04 | (unnamed) | Northborough | 0.12 m of water at peak; worst hour 10 mm (57% of the storm); water beside the road 0.11 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 1.4 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.66) |
| 14 | 0.04 | Rockland Road | Auburn | 0.12 m of water at peak; worst hour 14 mm (70% of the storm) |
| 15 | 0.04 | (unnamed) | Northborough | 0.12 m of water at peak; worst hour 12 mm (63% of the storm); water beside the road 1.65 m above its crest (design freeboard 0.30 m; P 1.00); fast water: depth x speed 0.21 m2/s (small cars unstable from 0.3); runoff beside / along the road at 2.3 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.96); a culvert within 100 m is overtopped |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
