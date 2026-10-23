# Road-closure prototype: sep2018w_loss_sep2018w_shrewsbury_20m

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on CPU (OpenMP)), 20 m grid, storm from 2018-09-18T07:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 6,283 |
| Expected closures (sum of probabilities) | 47.6 |
| Segments with closure probability >= 50% | 35 (27.7 km) |
| Further segments that may close (stream reaches the road crest) | 24 (18.3 km) |
| Culverts overtopped / surcharged | 57 / 0 of 1265 |
| Road segments cut off from hospitals | 153 |
| Worst added trip time to a hospital | 15.6 min |
| Heaviest hour of rain | 26.7 mm |
| Flood model run time | 1507 s |

## Checks against what happened

- Storm-day flood reports in the area: 1; water >= 10 cm within 100 m of 0% of them, vs 14% of random points (any day).
- Segments flagged impassable are 0.0x as likely as an average segment to have a report within 200 m.
- MassDOT repeating flood sites in the area: 4; 0 have a segment within 150 m at P >= 0.5 (share of all segments at P >= 0.5: 0.6%).

## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 1.00 | Boundary Street | Marlborough | 0.64 m of water at peak; over 30 cm for 18.0 h; 30 cm reached 0.5 h into the storm; worst hour 15 mm (39% of the storm); runoff beside / along the road at 1.2 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.58); a culvert within 100 m is overtopped |
| 2 | 0.98 | (unnamed) | Berlin | 0.52 m of water at peak; worst hour 12 mm (31% of the storm); water beside the road 0.03 m below its crest (design freeboard 0.30 m; P 0.96); a culvert within 100 m is overtopped |
| 3 | 0.97 | Ramp-Solomon Pond Rd To Rt 290 Eb | Northborough | 0.49 m of water at peak; over 30 cm for 1.0 h; 30 cm reached 0.5 h into the storm; worst hour 14 mm (38% of the storm); water beside the road 0.53 m above its crest (design freeboard 0.30 m; P 1.00); a culvert within 100 m is overtopped |
| 4 | 0.97 | Ramp-Rt 290 Eb To Solomon Pond Rd Nb | Northborough | 0.49 m of water at peak; over 30 cm for 1.0 h; 30 cm reached 0.5 h into the storm; worst hour 14 mm (37% of the storm); water beside the road 1.58 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 1.4 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.76); a culvert within 100 m is overtopped |
| 5 | 0.96 | Hudson Street | Northborough | 0.48 m of water at peak; worst hour 17 mm (42% of the storm); water beside the road 0.48 m below its crest (design freeboard 0.30 m; P 0.12); a culvert within 100 m is overtopped |
| 6 | 0.95 | Hudson Street | Northborough | 0.46 m of water at peak; worst hour 16 mm (40% of the storm); a culvert within 100 m is overtopped |
| 7 | 0.94 | (unnamed) | Marlborough | 0.46 m of water at peak; worst hour 21 mm (48% of the storm); a culvert within 100 m is overtopped |
| 8 | 0.94 | Route 85 | Southborough | 0.46 m of water at peak; worst hour 24 mm (54% of the storm); a culvert within 100 m is overtopped |
| 9 | 0.93 | Cedar Hill Street | Marlborough | 0.45 m of water at peak; worst hour 24 mm (51% of the storm); water beside the road 1.55 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 1.8 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.82); a culvert within 100 m is overtopped |
| 10 | 0.93 | Crosby Road | Berlin | 0.45 m of water at peak; worst hour 12 mm (32% of the storm); water beside the road 2.52 m above its crest (design freeboard 0.30 m; P 1.00); fast water: depth x speed 1.46 m2/s (small cars unstable from 0.3); runoff beside / along the road at 3.3 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 1.00); a culvert within 100 m is overtopped |
| 11 | 0.92 | Whitney Street | Northborough | 0.44 m of water at peak; worst hour 14 mm (37% of the storm); a culvert within 100 m is overtopped |
| 12 | 0.90 | Route 20 | Northborough | 0.43 m of water at peak; worst hour 16 mm (41% of the storm); overtopping at 2.4 m/s at a stream crossing (grass-covered fill erodes from ~1.5 m/s); a culvert within 100 m is overtopped |
| 13 | 0.85 | Allen Court | Northborough | 0.41 m of water at peak; worst hour 17 mm (42% of the storm); a culvert within 100 m is overtopped |
| 14 | 0.85 | Sears Road | Southborough | 0.40 m of water at peak; worst hour 26 mm (55% of the storm); a culvert within 100 m is overtopped |
| 15 | 0.83 | Linden Street | Berlin | 0.40 m of water at peak; worst hour 12 mm (30% of the storm); water beside the road 1.52 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 2.1 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.95); a culvert within 100 m is overtopped |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
