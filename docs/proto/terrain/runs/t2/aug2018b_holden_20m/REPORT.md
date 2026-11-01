# Road-closure prototype: aug2018b_loss_aug2018b_holden_20m

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on CPU (OpenMP)), 20 m grid, storm from 2018-08-11T08:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 4,422 |
| Expected closures (sum of probabilities) | 18.0 |
| Segments with closure probability >= 50% | 9 (7.4 km) |
| Further segments that may close (stream reaches the road crest) | 7 (6.4 km) |
| Culverts overtopped / surcharged | 12 / 1 of 864 |
| Road segments cut off from hospitals | 19 |
| Worst added trip time to a hospital | 11.5 min |
| Heaviest hour of rain | 24.1 mm |
| Flood model run time | 1328 s |

## Checks against what happened

- Storm-day flood reports in the area: 0; water >= 10 cm within 100 m of 0% of them, vs 16% of random points (any day).
- MassDOT repeating flood sites in the area: 2; 0 have a segment within 150 m at P >= 0.5 (share of all segments at P >= 0.5: 0.2%).

## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 1.00 | Water Street | Clinton | 0.59 m of water at peak; over 30 cm for 7.5 h; 30 cm reached 0.5 h into the storm; worst hour 6 mm (16% of the storm) |
| 2 | 1.00 | (unnamed) | Clinton | 0.59 m of water at peak; worst hour 6 mm (17% of the storm); a culvert within 100 m is overtopped |
| 3 | 1.00 | Route 62 | Berlin | 0.57 m of water at peak; worst hour 5 mm (20% of the storm); runoff beside / along the road at 1.3 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.14) |
| 4 | 0.99 | (unnamed) | Berlin | 0.52 m of water at peak; over 30 cm for 0.5 h; 30 cm reached 0.5 h into the storm; worst hour 5 mm (21% of the storm); water beside the road 0.42 m above its crest (design freeboard 0.30 m; P 1.00) |
| 5 | 0.98 | Route 62 | Berlin | 0.51 m of water at peak; over 30 cm for 0.5 h; 30 cm reached 0.5 h into the storm; worst hour 5 mm (22% of the storm) |
| 6 | 0.97 | Barnes Hill Road | Berlin | 0.49 m of water at peak; worst hour 5 mm (23% of the storm); water beside the road 0.80 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 0.6 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.21); a culvert within 100 m is overtopped |
| 7 | 0.89 | Route 62 | Clinton | 0.42 m of water at peak; worst hour 6 mm (17% of the storm); a culvert within 100 m is overtopped |
| 8 | 0.82 | Route 62 | Clinton | 0.39 m of water at peak; over 30 cm for 1.0 h; 30 cm reached 0.5 h into the storm; worst hour 5 mm (17% of the storm); a culvert within 100 m is overtopped |
| 9 | 0.60 | Mill Street | Holden | 0.33 m of water at peak; over 30 cm for 0.5 h; 30 cm reached 0.5 h into the storm; worst hour 8 mm (18% of the storm) |
| 10 | 0.36 | (unnamed) | Holden | 0.27 m of water at peak; worst hour 7 mm (18% of the storm); runoff beside / along the road at 1.1 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.55); a culvert within 100 m is overtopped |
| 11 | 0.31 | Route 62 | Clinton | 0.25 m of water at peak; worst hour 6 mm (17% of the storm); water beside the road 0.81 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 0.9 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.40); a culvert within 100 m is overtopped |
| 12 | 0.25 | (unnamed) | Berlin | 0.23 m of water at peak; worst hour 5 mm (19% of the storm); water beside the road 4.40 m above its crest (design freeboard 0.30 m; P 1.00); fast water: depth x speed 0.48 m2/s (small cars unstable from 0.3); runoff beside / along the road at 3.1 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.99) |
| 13 | 0.25 | Route 70 | Clinton | 0.23 m of water at peak; worst hour 11 mm (20% of the storm); a culvert within 100 m is overtopped |
| 14 | 0.20 | Ash Street | Clinton | 0.22 m of water at peak; worst hour 7 mm (16% of the storm); water beside the road -0.00 m below its crest (design freeboard 0.30 m; P 0.98) |
| 15 | 0.15 | (unnamed) | Clinton | 0.20 m of water at peak; worst hour 5 mm (17% of the storm); water beside the road 1.94 m above its crest (design freeboard 0.30 m; P 1.00); fast water: depth x speed 0.43 m2/s (small cars unstable from 0.3); runoff beside / along the road at 3.7 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 1.00) |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
