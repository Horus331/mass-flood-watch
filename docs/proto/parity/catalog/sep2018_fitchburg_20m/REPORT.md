# Road-closure prototype: sep2018_loss_sep2018_fitchburg_20m

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on CPU (OpenMP)), 20 m grid, storm from 2018-09-18T06:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 3,097 |
| Expected closures (sum of probabilities) | 23.4 |
| Segments with closure probability >= 50% | 7 (6.5 km) |
| Further segments that may close (stream reaches the road crest) | 10 (4.5 km) |
| Culverts overtopped / surcharged | 42 / 0 of 520 |
| Road segments cut off from hospitals | 48 |
| Worst added trip time to a hospital | 25.2 min |
| Heaviest hour of rain | 24.2 mm |
| Flood model run time | 1208 s |

## Checks against what happened

- Storm-day flood reports in the area: 3; water >= 10 cm within 100 m of 0% of them, vs 53% of random points (any day).
- Segments flagged impassable are 0.0x as likely as an average segment to have a report within 200 m.
- MassDOT repeating flood sites in the area: 1; 0 have a segment within 150 m at P >= 0.5 (share of all segments at P >= 0.5: 0.2%).

## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 1.00 | Depot Street | Fitchburg | 0.75 m of water at peak; over 30 cm for 16.5 h; 30 cm reached 0.5 h into the storm; worst hour 15 mm (21% of the storm); a culvert within 100 m is overtopped |
| 2 | 1.00 | Sanborn Street | Fitchburg | 0.63 m of water at peak; over 30 cm for 8.5 h; 30 cm reached 8.0 h into the storm; worst hour 16 mm (21% of the storm); runoff beside / along the road at 1.5 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.74); a culvert within 100 m is overtopped |
| 3 | 0.94 | Oakmont Avenue | Westminster | 0.45 m of water at peak; over 30 cm for 10.5 h; 30 cm reached 8.0 h into the storm; worst hour 20 mm (24% of the storm); runoff beside / along the road at 0.9 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.22); a culvert within 100 m is overtopped |
| 4 | 0.73 | Westminster Hill Road | Fitchburg | 0.36 m of water at peak; over 30 cm for 3.5 h; 30 cm reached 9.5 h into the storm; worst hour 16 mm (22% of the storm); a culvert within 100 m is overtopped |
| 5 | 0.72 | Route 12 | Ashburnham | 0.36 m of water at peak; over 30 cm for 1.5 h; 30 cm reached 9.0 h into the storm; worst hour 17 mm (22% of the storm); runoff beside / along the road at 0.7 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.37); a culvert within 100 m is overtopped |
| 6 | 0.65 | Fred Smith Road | Westminster | 0.34 m of water at peak; over 30 cm for 1.5 h; 30 cm reached 9.5 h into the storm; worst hour 17 mm (22% of the storm); a culvert within 100 m is overtopped |
| 7 | 0.58 | John Fitch Highway | Fitchburg | 0.32 m of water at peak; over 30 cm for 3.0 h; 30 cm reached 10.0 h into the storm; worst hour 16 mm (23% of the storm) |
| 8 | 0.45 | Route 31 | Fitchburg | 0.29 m of water at peak; worst hour 18 mm (24% of the storm); a culvert within 100 m is overtopped |
| 9 | 0.39 | Brook Street | Fitchburg | 0.27 m of water at peak; worst hour 14 mm (21% of the storm); water beside the road 0.19 m above its crest (design freeboard 0.30 m; P 1.00) |
| 10 | 0.36 | Ashby West Road | Fitchburg | 0.26 m of water at peak; worst hour 16 mm (21% of the storm); culvert (Tributary to Falulah Brook): headwater 1.66 m vs road crest 1.01 m, 25% blocked, 1.6 m3/s |
| 11 | 0.35 | Veterans Of Foreign Wars Circle | Gardner | 0.26 m of water at peak; worst hour 14 mm (19% of the storm); a culvert within 100 m is overtopped |
| 12 | 0.35 | Dyer Street | Gardner | 0.26 m of water at peak; worst hour 13 mm (18% of the storm) |
| 13 | 0.33 | Pearson Boulevard | Gardner | 0.26 m of water at peak; worst hour 14 mm (19% of the storm); a culvert within 100 m is overtopped |
| 14 | 0.33 | Route 2 | Gardner | 0.26 m of water at peak; worst hour 14 mm (19% of the storm); a culvert within 100 m is overtopped |
| 15 | 0.32 | Pearson Boulevard | Gardner | 0.25 m of water at peak; worst hour 14 mm (19% of the storm); a culvert within 100 m is overtopped |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
