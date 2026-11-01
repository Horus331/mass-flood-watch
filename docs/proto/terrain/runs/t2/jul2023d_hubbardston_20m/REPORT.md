# Road-closure prototype: jul2023d_loss_jul2023d_hubbardston_20m

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on CPU (OpenMP)), 20 m grid, storm from 2023-07-21T15:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 1,317 |
| Expected closures (sum of probabilities) | 8.4 |
| Segments with closure probability >= 50% | 4 (4.0 km) |
| Further segments that may close (stream reaches the road crest) | 3 (3.0 km) |
| Culverts overtopped / surcharged | 19 / 1 of 385 |
| Road segments cut off from hospitals | 46 |
| Worst added trip time to a hospital | 38.7 min |
| Heaviest hour of rain | 46.3 mm |
| Flood model run time | 1554 s |

## Checks against what happened

- Storm-day flood reports in the area: 2; water >= 10 cm within 100 m of 0% of them, vs 0% of random points (any day).
- Segments flagged impassable are 0.0x as likely as an average segment to have a report within 200 m.

## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 1.00 | Lackey Lane | Barre | 0.70 m of water at peak; over 30 cm for 9.0 h; 30 cm reached 8.5 h into the storm; worst hour 39 mm (68% of the storm); water beside the road 0.26 m below its crest (design freeboard 0.30 m; P 0.61); a culvert within 100 m is overtopped |
| 2 | 0.98 | Williamsville Road | Hubbardston | 0.51 m of water at peak; over 30 cm for 3.5 h; 30 cm reached 7.0 h into the storm; worst hour 38 mm (46% of the storm); a culvert within 100 m is overtopped |
| 3 | 0.76 | Pitcherville Road | Hubbardston | 0.37 m of water at peak; over 30 cm for 1.5 h; 30 cm reached 7.0 h into the storm; worst hour 28 mm (38% of the storm); a culvert within 100 m is overtopped |
| 4 | 0.59 | Birches Road | Hubbardston | 0.32 m of water at peak; over 30 cm for 1.0 h; 30 cm reached 7.0 h into the storm; worst hour 30 mm (41% of the storm); water beside the road 0.02 m below its crest (design freeboard 0.30 m; P 0.97); runoff beside / along the road at 0.6 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.17); a culvert within 100 m is overtopped |
| 5 | 0.36 | Route 62 | Barre | 0.26 m of water at peak; worst hour 32 mm (48% of the storm); runoff beside / along the road at 1.1 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.39); a culvert within 100 m is overtopped |
| 6 | 0.24 | Thompson Road | Hubbardston | 0.23 m of water at peak; worst hour 44 mm (48% of the storm); runoff beside / along the road at 0.6 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.11); a culvert within 100 m is overtopped |
| 7 | 0.17 | Ragged Hill Road | Hubbardston | 0.21 m of water at peak; worst hour 30 mm (41% of the storm); a culvert within 100 m is overtopped |
| 8 | 0.17 | Mill Street | Gardner | 0.20 m of water at peak; worst hour 23 mm (36% of the storm); a culvert within 100 m is overtopped |
| 9 | 0.16 | Williamsville Road | Barre | 0.20 m of water at peak; worst hour 42 mm (48% of the storm); a culvert within 100 m is overtopped |
| 10 | 0.16 | Minott Street | Gardner | 0.20 m of water at peak; worst hour 22 mm (31% of the storm); a culvert within 100 m is overtopped |
| 11 | 0.10 | Dyer Street | Gardner | 0.17 m of water at peak; worst hour 22 mm (35% of the storm) |
| 12 | 0.10 | New Templeton Road | Hubbardston | 0.17 m of water at peak; worst hour 33 mm (42% of the storm); a culvert within 100 m is overtopped |
| 13 | 0.10 | Route 62 | Hubbardston | 0.17 m of water at peak; worst hour 38 mm (63% of the storm); a culvert within 100 m is overtopped |
| 14 | 0.09 | South Main Street | Gardner | 0.16 m of water at peak; worst hour 23 mm (36% of the storm); a culvert within 100 m is overtopped |
| 15 | 0.09 | East Broadway | Gardner | 0.16 m of water at peak; worst hour 24 mm (34% of the storm); water beside the road 0.14 m below its crest (design freeboard 0.30 m; P 0.85) |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
