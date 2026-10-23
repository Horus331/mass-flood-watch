# Road-closure prototype: aug2018b_loss_aug2018b_holden_20m

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on CPU (OpenMP)), 20 m grid, storm from 2018-08-11T08:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 4,422 |
| Expected closures (sum of probabilities) | 18.1 |
| Segments with closure probability >= 50% | 7 (5.8 km) |
| Further segments that may close (stream reaches the road crest) | 8 (7.9 km) |
| Culverts overtopped / surcharged | 11 / 1 of 864 |
| Road segments cut off from hospitals | 12 |
| Worst added trip time to a hospital | 12.3 min |
| Heaviest hour of rain | 24.1 mm |
| Flood model run time | 1271 s |

## Checks against what happened

- Storm-day flood reports in the area: 0; water >= 10 cm within 100 m of 0% of them, vs 13% of random points (any day).
- MassDOT repeating flood sites in the area: 2; 0 have a segment within 150 m at P >= 0.5 (share of all segments at P >= 0.5: 0.2%).

## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 1.00 | Water Street | Clinton | 0.72 m of water at peak; over 30 cm for 22.0 h; 30 cm reached 0.5 h into the storm; worst hour 6 mm (16% of the storm) |
| 2 | 1.00 | Route 62 | Berlin | 1.01 m of water at peak; over 30 cm for 1.0 h; 30 cm reached 0.5 h into the storm; worst hour 5 mm (20% of the storm); water beside the road 0.42 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 1.3 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.29) |
| 3 | 1.00 | (unnamed) | Clinton | 0.60 m of water at peak; worst hour 6 mm (17% of the storm); a culvert within 100 m is overtopped |
| 4 | 0.97 | Barnes Hill Road | Berlin | 0.49 m of water at peak; worst hour 5 mm (23% of the storm); water beside the road 0.80 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 1.4 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.77); a culvert within 100 m is overtopped |
| 5 | 0.92 | (unnamed) | Berlin | 0.44 m of water at peak; over 30 cm for 0.5 h; 30 cm reached 0.5 h into the storm; worst hour 5 mm (21% of the storm); water beside the road 0.49 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 1.1 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.24) |
| 6 | 0.89 | Route 62 | Berlin | 0.42 m of water at peak; over 30 cm for 0.5 h; 30 cm reached 0.5 h into the storm; worst hour 5 mm (22% of the storm); runoff beside / along the road at 1.1 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.15) |
| 7 | 0.78 | Mill Street | Holden | 0.38 m of water at peak; over 30 cm for 1.0 h; 30 cm reached 0.5 h into the storm; worst hour 8 mm (18% of the storm) |
| 8 | 0.39 | Route 62 | Clinton | 0.27 m of water at peak; worst hour 6 mm (17% of the storm); water beside the road 0.82 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 0.9 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.45); a culvert within 100 m is overtopped |
| 9 | 0.37 | Wilson Street | Clinton | 0.27 m of water at peak; worst hour 6 mm (17% of the storm); a culvert within 100 m is overtopped |
| 10 | 0.37 | (unnamed) | Berlin | 0.27 m of water at peak; worst hour 5 mm (19% of the storm); water beside the road 4.40 m above its crest (design freeboard 0.30 m; P 1.00); fast water: depth x speed 0.75 m2/s (small cars unstable from 0.3); runoff beside / along the road at 3.2 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.99) |
| 11 | 0.34 | Route 62 | Clinton | 0.26 m of water at peak; worst hour 5 mm (17% of the storm); a culvert within 100 m is overtopped |
| 12 | 0.32 | Route 70 | Clinton | 0.25 m of water at peak; worst hour 11 mm (20% of the storm); a culvert within 100 m is overtopped |
| 13 | 0.29 | (unnamed) | Holden | 0.24 m of water at peak; worst hour 7 mm (18% of the storm); runoff beside / along the road at 1.1 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.45); a culvert within 100 m is overtopped |
| 14 | 0.24 | Parker Road | Lancaster | 0.23 m of water at peak; worst hour 13 mm (23% of the storm) |
| 15 | 0.22 | Route 62 | Clinton | 0.22 m of water at peak; worst hour 6 mm (17% of the storm); a culvert within 100 m is overtopped |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
