# Road-closure prototype: jul2023d_loss_jul2023d_hubbardston_20m

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on CPU (OpenMP)), 20 m grid, storm from 2023-07-21T15:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 1,317 |
| Expected closures (sum of probabilities) | 33.0 |
| Segments with closure probability >= 50% | 26 (23.0 km) |
| Further segments that may close (stream reaches the road crest) | 47 (40.4 km) |
| Culverts overtopped / surcharged | 63 / 1 of 385 |
| Road segments cut off from hospitals | 201 |
| Worst added trip time to a hospital | 33.5 min |
| Heaviest hour of rain | 46.3 mm |
| Flood model run time | 1420 s |

## Checks against what happened

- Storm-day flood reports in the area: 2; water >= 10 cm within 100 m of 0% of them, vs 38% of random points (any day).
- Segments flagged impassable are 0.0x as likely as an average segment to have a report within 200 m.

## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 1.00 | Lackey Lane | Barre | 1.81 m of water at peak; over 30 cm for 11.0 h; 30 cm reached 7.5 h into the storm; worst hour 39 mm (68% of the storm); water beside the road 0.01 m above its crest (design freeboard 0.30 m; P 0.98); runoff beside / along the road at 1.3 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.69); a culvert within 100 m is overtopped |
| 2 | 1.00 | Williamsville Road | Hubbardston | 1.03 m of water at peak; over 30 cm for 5.5 h; 30 cm reached 6.0 h into the storm; worst hour 38 mm (46% of the storm); runoff beside / along the road at 0.9 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.38); a culvert within 100 m is overtopped |
| 3 | 1.00 | Route 62 | Barre | 0.69 m of water at peak; over 30 cm for 2.5 h; 30 cm reached 7.0 h into the storm; worst hour 32 mm (48% of the storm); runoff beside / along the road at 1.8 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.88); a culvert within 100 m is overtopped |
| 4 | 1.00 | Birches Road | Hubbardston | 0.81 m of water at peak; over 30 cm for 7.0 h; 30 cm reached 5.5 h into the storm; worst hour 30 mm (41% of the storm); water beside the road 0.53 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 1.3 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.69); a culvert within 100 m is overtopped |
| 5 | 1.00 | Pitcherville Road | Hubbardston | 0.78 m of water at peak; over 30 cm for 7.0 h; 30 cm reached 5.5 h into the storm; worst hour 28 mm (38% of the storm); runoff beside / along the road at 0.6 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.19); a culvert within 100 m is overtopped |
| 6 | 0.98 | Chelsea Street | Gardner | 0.51 m of water at peak; over 30 cm for 8.0 h; 30 cm reached 10.5 h into the storm; worst hour 24 mm (36% of the storm); a culvert within 100 m is overtopped |
| 7 | 0.95 | Dyer Street | Gardner | 0.46 m of water at peak; over 30 cm for 10.0 h; 30 cm reached 8.5 h into the storm; worst hour 22 mm (35% of the storm); water beside the road 0.43 m below its crest (design freeboard 0.30 m; P 0.19) |
| 8 | 0.94 | Thompson Road | Hubbardston | 0.45 m of water at peak; over 30 cm for 1.5 h; 30 cm reached 6.0 h into the storm; worst hour 44 mm (48% of the storm); water beside the road 0.13 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 1.0 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.34); a culvert within 100 m is overtopped |
| 9 | 0.93 | Hubbardston Road | Templeton | 0.45 m of water at peak; over 30 cm for 4.5 h; 30 cm reached 6.0 h into the storm; worst hour 32 mm (43% of the storm); a culvert within 100 m is overtopped |
| 10 | 0.91 | High Bridge Road | Hubbardston | 0.44 m of water at peak; over 30 cm for 2.0 h; 30 cm reached 7.0 h into the storm; worst hour 31 mm (41% of the storm); water beside the road 0.04 m above its crest (design freeboard 0.30 m; P 0.99); a culvert within 100 m is overtopped |
| 11 | 0.89 | East Broadway | Gardner | 0.42 m of water at peak; over 30 cm for 7.0 h; 30 cm reached 11.5 h into the storm; worst hour 24 mm (34% of the storm); water beside the road 0.32 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 0.8 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.34) |
| 12 | 0.89 | Ragged Hill Road | Hubbardston | 0.42 m of water at peak; over 30 cm for 2.5 h; 30 cm reached 6.0 h into the storm; worst hour 30 mm (41% of the storm); water beside the road 0.29 m below its crest (design freeboard 0.30 m; P 0.54); runoff beside / along the road at 0.7 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.26); a culvert within 100 m is overtopped |
| 13 | 0.87 | New Templeton Road | Hubbardston | 0.41 m of water at peak; over 30 cm for 1.5 h; 30 cm reached 6.0 h into the storm; worst hour 33 mm (42% of the storm); runoff beside / along the road at 2.2 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.28); a culvert within 100 m is overtopped |
| 14 | 0.80 | Mill Street | Gardner | 0.38 m of water at peak; over 30 cm for 9.0 h; 30 cm reached 9.5 h into the storm; worst hour 23 mm (36% of the storm); a culvert within 100 m is overtopped |
| 15 | 0.75 | Williamsville Road | Barre | 0.37 m of water at peak; over 30 cm for 1.5 h; 30 cm reached 7.0 h into the storm; worst hour 42 mm (48% of the storm); a culvert within 100 m is overtopped |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
