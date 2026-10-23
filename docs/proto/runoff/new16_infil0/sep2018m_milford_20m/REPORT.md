# Road-closure prototype: sep2018m_loss_sep2018m_milford_20m

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on CPU (OpenMP)), 20 m grid, storm from 2018-09-18T08:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 5,024 |
| Expected closures (sum of probabilities) | 46.3 |
| Segments with closure probability >= 50% | 21 (16.0 km) |
| Further segments that may close (stream reaches the road crest) | 18 (13.4 km) |
| Culverts overtopped / surcharged | 90 / 1 of 863 |
| Road segments cut off from hospitals | 519 |
| Worst added trip time to a hospital | 26.0 min |
| Heaviest hour of rain | 51.8 mm |
| Flood model run time | 1181 s |

## Checks against what happened

- Storm-day flood reports in the area: 1; water >= 10 cm within 100 m of 100% of them, vs 45% of random points (any day).
- Segments flagged impassable are 0.0x as likely as an average segment to have a report within 200 m.
- MassDOT repeating flood sites in the area: 8; 0 have a segment within 150 m at P >= 0.5 (share of all segments at P >= 0.5: 0.4%).

## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 1.00 | Paine Street | Bellingham | 0.71 m of water at peak; over 30 cm for 7.0 h; 30 cm reached 11.5 h into the storm; worst hour 26 mm (63% of the storm); a culvert within 100 m is overtopped |
| 2 | 1.00 | (unnamed) | Blackstone | 1.00 m of water at peak; over 30 cm for 9.5 h; 30 cm reached 9.0 h into the storm; worst hour 48 mm (62% of the storm); a culvert within 100 m is overtopped |
| 3 | 1.00 | Pine Grove Avenue | Bellingham | 0.73 m of water at peak; over 30 cm for 7.5 h; 30 cm reached 11.0 h into the storm; worst hour 27 mm (61% of the storm); a culvert within 100 m is overtopped |
| 4 | 1.00 | Bubbling Brook Drive | Franklin | 0.84 m of water at peak; over 30 cm for 7.5 h; 30 cm reached 11.0 h into the storm; worst hour 35 mm (53% of the storm); a culvert within 100 m is overtopped |
| 5 | 1.00 | Cemetery Street | Mendon | 0.64 m of water at peak; over 30 cm for 5.5 h; 30 cm reached 9.5 h into the storm; worst hour 38 mm (49% of the storm); a culvert within 100 m is overtopped |
| 6 | 1.00 | Bellingham Street | Mendon | 0.67 m of water at peak; over 30 cm for 7.0 h; 30 cm reached 10.0 h into the storm; worst hour 40 mm (46% of the storm); a culvert within 100 m is overtopped |
| 7 | 1.00 | Pond Street | Franklin | 0.61 m of water at peak; over 30 cm for 9.0 h; 30 cm reached 9.5 h into the storm; worst hour 46 mm (51% of the storm); a culvert within 100 m is overtopped |
| 8 | 1.00 | Beech Street | Franklin | 0.61 m of water at peak; over 30 cm for 8.5 h; 30 cm reached 10.0 h into the storm; worst hour 46 mm (50% of the storm); a culvert within 100 m is overtopped |
| 9 | 0.99 | (unnamed) | Bellingham | 0.54 m of water at peak; over 30 cm for 8.0 h; 30 cm reached 10.0 h into the storm; worst hour 38 mm (56% of the storm); runoff beside / along the road at 0.9 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.40); a culvert within 100 m is overtopped |
| 10 | 0.98 | (unnamed) | Bellingham | 0.51 m of water at peak; over 30 cm for 6.5 h; 30 cm reached 12.0 h into the storm; worst hour 30 mm (59% of the storm); a culvert within 100 m is overtopped |
| 11 | 0.94 | Wrentham Road | Bellingham | 0.46 m of water at peak; over 30 cm for 7.5 h; 30 cm reached 11.0 h into the storm; worst hour 27 mm (62% of the storm); water beside the road 0.18 m below its crest (design freeboard 0.30 m; P 0.79); a culvert within 100 m is overtopped |
| 12 | 0.93 | Rogerson Crossing | Uxbridge | 0.45 m of water at peak; over 30 cm for 1.0 h; 30 cm reached 0.5 h into the storm; worst hour 24 mm (46% of the storm); a culvert within 100 m is overtopped |
| 13 | 0.90 | Railroad Street | Bellingham | 0.43 m of water at peak; over 30 cm for 5.5 h; 30 cm reached 10.5 h into the storm; worst hour 37 mm (58% of the storm); water beside the road 0.48 m below its crest (design freeboard 0.30 m; P 0.12); a culvert within 100 m is overtopped |
| 14 | 0.90 | Ramp-Rt 495 Sb To Rt 140 | Franklin | 0.43 m of water at peak; over 30 cm for 3.5 h; 30 cm reached 10.0 h into the storm; worst hour 40 mm (46% of the storm); a culvert within 100 m is overtopped |
| 15 | 0.85 | Hartford Avenue East | Mendon | 0.40 m of water at peak; over 30 cm for 2.5 h; 30 cm reached 10.0 h into the storm; worst hour 39 mm (49% of the storm); a culvert within 100 m is overtopped |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
