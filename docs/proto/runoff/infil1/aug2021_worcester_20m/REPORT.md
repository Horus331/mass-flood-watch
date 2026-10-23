# Road-closure prototype: aug2021_loss_aug2021_worcester_20m

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on CPU (OpenMP)), 20 m grid, storm from 2021-08-19T09:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 8,566 |
| Expected closures (sum of probabilities) | 171.7 |
| Segments with closure probability >= 50% | 121 (73.2 km) |
| Further segments that may close (stream reaches the road crest) | 187 (97.7 km) |
| Culverts overtopped / surcharged | 218 / 4 of 1347 |
| Road segments cut off from hospitals | 833 |
| Worst added trip time to a hospital | 22.8 min |
| Heaviest hour of rain | 89.6 mm |
| Flood model run time | 1594 s |

## Checks against what happened

- Storm-day flood reports in the area: 5; water >= 10 cm within 100 m of 60% of them, vs 57% of random points (any day).
- Segments flagged impassable are 1.12x as likely as an average segment to have a report within 200 m.
- MassDOT repeating flood sites in the area: 10; 3 have a segment within 150 m at P >= 0.5 (share of all segments at P >= 0.5: 1.4%).

## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 1.00 | Martin Luther King Jr Boulevard | Worcester | 3.70 m of water at peak; over 30 cm for 17.5 h; 30 cm reached 1.0 h into the storm; worst hour 24 mm (43% of the storm); water beside the road 3.62 m above its crest (design freeboard 0.30 m; P 1.00); road sag 3.2 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 24 mm; catchment 60.2 ha) (P 1.00); a culvert within 100 m is overtopped |
| 2 | 1.00 | Martin Luther King Jr Boulevard | Worcester | 3.00 m of water at peak; over 30 cm for 17.5 h; 30 cm reached 1.0 h into the storm; worst hour 24 mm (43% of the storm); water beside the road 2.68 m above its crest (design freeboard 0.30 m; P 1.00); fast water: depth x speed 0.21 m2/s (small cars unstable from 0.3); runoff beside / along the road at 2.5 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.98); road sag 3.2 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 24 mm; catchment 60.2 ha) (P 1.00); a culvert within 100 m is overtopped |
| 3 | 1.00 | Foster Street | Worcester | 1.98 m of water at peak; over 30 cm for 12.5 h; 30 cm reached 6.0 h into the storm; worst hour 25 mm (44% of the storm); water beside the road 0.01 m below its crest (design freeboard 0.30 m; P 0.97); road sag 1.2 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 25 mm; catchment 22.1 ha) (P 0.15); a culvert within 100 m is overtopped |
| 4 | 1.00 | Foster Street | Worcester | 1.98 m of water at peak; over 30 cm for 12.5 h; 30 cm reached 6.0 h into the storm; worst hour 25 mm (44% of the storm); water beside the road -0.00 m below its crest (design freeboard 0.30 m; P 0.98); road sag 1.2 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 25 mm; catchment 22.1 ha) (P 0.15); a culvert within 100 m is overtopped |
| 5 | 1.00 | Major Taylor Boulevard | Worcester | 1.11 m of water at peak; over 30 cm for 10.5 h; 30 cm reached 8.0 h into the storm; worst hour 25 mm (44% of the storm); water beside the road 0.86 m above its crest (design freeboard 0.30 m; P 1.00); road sag 1.1 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 24 mm; catchment 60.2 ha) (P 1.00); a culvert within 100 m is overtopped |
| 6 | 1.00 | Major Taylor Boulevard | Worcester | 1.11 m of water at peak; over 30 cm for 10.5 h; 30 cm reached 8.0 h into the storm; worst hour 25 mm (44% of the storm); water beside the road 0.86 m above its crest (design freeboard 0.30 m; P 1.00); road sag 1.1 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 24 mm; catchment 60.2 ha) (P 1.00); a culvert within 100 m is overtopped |
| 7 | 1.00 | Route 122 | Northbridge | 1.93 m of water at peak; over 30 cm for 18.0 h; 30 cm reached 0.5 h into the storm; worst hour 70 mm (68% of the storm); a culvert within 100 m is overtopped |
| 8 | 1.00 | Martin Luther King Jr Boulevard | Worcester | 0.67 m of water at peak; over 30 cm for 7.5 h; 30 cm reached 11.0 h into the storm; worst hour 24 mm (43% of the storm); water beside the road 0.50 m above its crest (design freeboard 0.30 m; P 1.00); a culvert within 100 m is overtopped |
| 9 | 1.00 | Providence Street | Millbury | 1.27 m of water at peak; over 30 cm for 14.0 h; 30 cm reached 4.5 h into the storm; worst hour 49 mm (54% of the storm); a culvert within 100 m is overtopped |
| 10 | 1.00 | Auburn Street | Auburn | 0.86 m of water at peak; over 30 cm for 9.5 h; 30 cm reached 9.0 h into the storm; worst hour 31 mm (48% of the storm); water beside the road 0.35 m below its crest (design freeboard 0.30 m; P 0.37) |
| 11 | 1.00 | Providence Road | Sutton | 0.65 m of water at peak; over 30 cm for 9.5 h; 30 cm reached 6.0 h into the storm; worst hour 37 mm (52% of the storm); a culvert within 100 m is overtopped |
| 12 | 1.00 | (unnamed) | Worcester | 3.00 m of water at peak; over 30 cm for 12.5 h; 30 cm reached 6.0 h into the storm; worst hour 23 mm (43% of the storm); a culvert within 100 m is overtopped |
| 13 | 1.00 | Chasm Loop Trail | Sutton | 0.98 m of water at peak; over 30 cm for 12.5 h; 30 cm reached 6.0 h into the storm; worst hour 64 mm (69% of the storm); runoff beside / along the road at 5.0 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.96); road sag 0.5 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 63 mm; catchment 2.0 ha) (P 0.93); a culvert within 100 m is overtopped |
| 14 | 1.00 | Bridge Street | Worcester | 0.94 m of water at peak; over 30 cm for 10.0 h; 30 cm reached 8.5 h into the storm; worst hour 24 mm (44% of the storm); water beside the road 0.63 m above its crest (design freeboard 0.30 m; P 1.00); road sag 2.3 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 24 mm; catchment 22.1 ha) (P 1.00); a culvert within 100 m is overtopped |
| 15 | 1.00 | Sycamore Street | Millbury | 0.73 m of water at peak; over 30 cm for 13.0 h; 30 cm reached 5.5 h into the storm; worst hour 50 mm (52% of the storm); runoff beside / along the road at 0.7 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.23); a culvert within 100 m is overtopped |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
