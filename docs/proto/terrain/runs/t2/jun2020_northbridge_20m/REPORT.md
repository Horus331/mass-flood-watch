# Road-closure prototype: jun2020_loss_jun2020_northbridge_20m

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on CPU (OpenMP)), 20 m grid, storm from 2020-06-28T14:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 4,247 |
| Expected closures (sum of probabilities) | 36.5 |
| Segments with closure probability >= 50% | 20 (15.8 km) |
| Further segments that may close (stream reaches the road crest) | 9 (6.3 km) |
| Culverts overtopped / surcharged | 76 / 0 of 592 |
| Road segments cut off from hospitals | 283 |
| Worst added trip time to a hospital | 23.8 min |
| Heaviest hour of rain | 54.0 mm |
| Flood model run time | 1254 s |

## Checks against what happened

- Storm-day flood reports in the area: 3; water >= 10 cm within 100 m of 0% of them, vs 28% of random points (any day).
- Segments flagged impassable are 0.0x as likely as an average segment to have a report within 200 m.
- MassDOT repeating flood sites in the area: 6; 0 have a segment within 150 m at P >= 0.5 (share of all segments at P >= 0.5: 0.5%).

## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 1.00 | Paine Street | Bellingham | 0.73 m of water at peak; over 30 cm for 8.5 h; 30 cm reached 10.0 h into the storm; worst hour 35 mm (52% of the storm); a culvert within 100 m is overtopped |
| 2 | 1.00 | Pine Grove Avenue | Bellingham | 0.80 m of water at peak; over 30 cm for 9.0 h; 30 cm reached 9.5 h into the storm; worst hour 37 mm (54% of the storm); a culvert within 100 m is overtopped |
| 3 | 1.00 | (unnamed) | Blackstone | 0.84 m of water at peak; over 30 cm for 10.0 h; 30 cm reached 8.5 h into the storm; worst hour 43 mm (54% of the storm); a culvert within 100 m is overtopped |
| 4 | 1.00 | Cemetery Street | Mendon | 0.77 m of water at peak; over 30 cm for 5.0 h; 30 cm reached 10.0 h into the storm; worst hour 45 mm (56% of the storm); a culvert within 100 m is overtopped |
| 5 | 1.00 | Bellingham Street | Mendon | 0.74 m of water at peak; over 30 cm for 6.5 h; 30 cm reached 10.0 h into the storm; worst hour 45 mm (58% of the storm); a culvert within 100 m is overtopped |
| 6 | 0.97 | Hartford Avenue East | Mendon | 0.49 m of water at peak; over 30 cm for 2.5 h; 30 cm reached 10.0 h into the storm; worst hour 45 mm (56% of the storm); a culvert within 100 m is overtopped |
| 7 | 0.96 | Wrentham Road | Bellingham | 0.48 m of water at peak; over 30 cm for 8.5 h; 30 cm reached 9.5 h into the storm; worst hour 36 mm (53% of the storm); water beside the road 0.15 m below its crest (design freeboard 0.30 m; P 0.85); a culvert within 100 m is overtopped |
| 8 | 0.94 | Hollis Street | Uxbridge | 0.45 m of water at peak; over 30 cm for 4.0 h; 30 cm reached 9.0 h into the storm; worst hour 44 mm (59% of the storm); a culvert within 100 m is overtopped |
| 9 | 0.89 | (unnamed) | Bellingham | 0.42 m of water at peak; over 30 cm for 6.0 h; 30 cm reached 9.5 h into the storm; worst hour 48 mm (60% of the storm); runoff beside / along the road at 0.7 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.32); a culvert within 100 m is overtopped |
| 10 | 0.88 | Pond Street | Franklin | 0.41 m of water at peak; over 30 cm for 5.5 h; 30 cm reached 13.0 h into the storm; worst hour 36 mm (54% of the storm); a culvert within 100 m is overtopped |
| 11 | 0.86 | Beech Street | Franklin | 0.41 m of water at peak; over 30 cm for 5.5 h; 30 cm reached 13.0 h into the storm; worst hour 36 mm (55% of the storm); a culvert within 100 m is overtopped |
| 12 | 0.84 | Route 16 | Mendon | 0.40 m of water at peak; over 30 cm for 1.5 h; 30 cm reached 9.0 h into the storm; worst hour 47 mm (65% of the storm); a culvert within 100 m is overtopped |
| 13 | 0.79 | Railroad Street | Bellingham | 0.38 m of water at peak; over 30 cm for 4.0 h; 30 cm reached 10.0 h into the storm; worst hour 45 mm (57% of the storm); water beside the road 0.48 m below its crest (design freeboard 0.30 m; P 0.11); a culvert within 100 m is overtopped |
| 14 | 0.74 | (unnamed) | Bellingham | 0.37 m of water at peak; over 30 cm for 4.5 h; 30 cm reached 11.5 h into the storm; worst hour 41 mm (55% of the storm); a culvert within 100 m is overtopped |
| 15 | 0.70 | Vincent Road | Mendon | 0.35 m of water at peak; over 30 cm for 1.0 h; 30 cm reached 10.0 h into the storm; worst hour 46 mm (54% of the storm); a culvert within 100 m is overtopped |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
