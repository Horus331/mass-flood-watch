# Road-closure prototype: jul2023d_loss_jul2023d_hubbardston_20m

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on CPU (OpenMP)), 20 m grid, storm from 2023-07-21T15:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 1,317 |
| Expected closures (sum of probabilities) | 15.2 |
| Segments with closure probability >= 50% | 8 (7.1 km) |
| Further segments that may close (stream reaches the road crest) | 11 (10.3 km) |
| Culverts overtopped / surcharged | 32 / 1 of 385 |
| Road segments cut off from hospitals | 62 |
| Worst added trip time to a hospital | 42.9 min |
| Heaviest hour of rain | 46.3 mm |
| Flood model run time | 1691 s |

## Checks against what happened

- Storm-day flood reports in the area: 2; water >= 10 cm within 100 m of 0% of them, vs 38% of random points (any day).
- Segments flagged impassable are 0.0x as likely as an average segment to have a report within 200 m.

## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 1.00 | Lackey Lane | Barre | 1.15 m of water at peak; over 30 cm for 10.5 h; 30 cm reached 8.0 h into the storm; worst hour 39 mm (68% of the storm); a culvert within 100 m is overtopped |
| 2 | 1.00 | Williamsville Road | Hubbardston | 0.63 m of water at peak; over 30 cm for 6.5 h; 30 cm reached 7.0 h into the storm; worst hour 38 mm (46% of the storm); runoff beside / along the road at 0.8 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.15); a culvert within 100 m is overtopped |
| 3 | 0.98 | Birches Road | Hubbardston | 0.52 m of water at peak; over 30 cm for 6.0 h; 30 cm reached 6.5 h into the storm; worst hour 30 mm (41% of the storm); water beside the road 0.31 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 0.9 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.45); a culvert within 100 m is overtopped |
| 4 | 0.98 | Pitcherville Road | Hubbardston | 0.50 m of water at peak; over 30 cm for 6.0 h; 30 cm reached 6.5 h into the storm; worst hour 28 mm (38% of the storm); a culvert within 100 m is overtopped |
| 5 | 0.88 | Route 62 | Barre | 0.41 m of water at peak; over 30 cm for 1.5 h; 30 cm reached 7.5 h into the storm; worst hour 32 mm (48% of the storm); runoff beside / along the road at 1.2 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.54); a culvert within 100 m is overtopped |
| 6 | 0.63 | Chelsea Street | Gardner | 0.33 m of water at peak; over 30 cm for 2.5 h; 30 cm reached 16.0 h into the storm; worst hour 24 mm (36% of the storm); a culvert within 100 m is overtopped |
| 7 | 0.56 | Dyer Street | Gardner | 0.32 m of water at peak; over 30 cm for 2.5 h; 30 cm reached 12.0 h into the storm; worst hour 22 mm (35% of the storm); water beside the road 0.49 m below its crest (design freeboard 0.30 m; P 0.10) |
| 8 | 0.50 | Ragged Hill Road | Hubbardston | 0.30 m of water at peak; over 30 cm for 0.5 h; 30 cm reached 7.0 h into the storm; worst hour 30 mm (41% of the storm); a culvert within 100 m is overtopped |
| 9 | 0.42 | Thompson Road | Hubbardston | 0.28 m of water at peak; worst hour 44 mm (48% of the storm); runoff beside / along the road at 0.6 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.13); a culvert within 100 m is overtopped |
| 10 | 0.42 | Hubbardston Road | Templeton | 0.28 m of water at peak; worst hour 32 mm (43% of the storm); a culvert within 100 m is overtopped |
| 11 | 0.40 | East Broadway | Gardner | 0.28 m of water at peak; worst hour 24 mm (34% of the storm); water beside the road 0.18 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 0.6 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.13) |
| 12 | 0.39 | Minott Street | Gardner | 0.27 m of water at peak; worst hour 22 mm (31% of the storm); a culvert within 100 m is overtopped |
| 13 | 0.36 | Mill Street | Gardner | 0.26 m of water at peak; worst hour 23 mm (36% of the storm); a culvert within 100 m is overtopped |
| 14 | 0.34 | New Templeton Road | Hubbardston | 0.26 m of water at peak; worst hour 33 mm (42% of the storm); runoff beside / along the road at 1.6 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.19); a culvert within 100 m is overtopped |
| 15 | 0.26 | South Main Street | Gardner | 0.23 m of water at peak; worst hour 23 mm (36% of the storm); a culvert within 100 m is overtopped |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
