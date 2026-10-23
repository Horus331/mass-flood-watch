# Road-closure prototype: sep2018_loss_sep2018_fitchburg_20m

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on CPU (OpenMP)), 20 m grid, storm from 2018-09-18T06:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 3,097 |
| Expected closures (sum of probabilities) | 59.3 |
| Segments with closure probability >= 50% | 38 (24.3 km) |
| Further segments that may close (stream reaches the road crest) | 40 (25.4 km) |
| Culverts overtopped / surcharged | 100 / 0 of 520 |
| Road segments cut off from hospitals | 175 |
| Worst added trip time to a hospital | 38.0 min |
| Heaviest hour of rain | 24.2 mm |
| Flood model run time | 1944 s |

## Checks against what happened

- Storm-day flood reports in the area: 3; water >= 10 cm within 100 m of 0% of them, vs 60% of random points (any day).
- Segments flagged impassable are 0.0x as likely as an average segment to have a report within 200 m.
- MassDOT repeating flood sites in the area: 1; 0 have a segment within 150 m at P >= 0.5 (share of all segments at P >= 0.5: 1.2%).

## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 1.00 | Depot Street | Fitchburg | 1.33 m of water at peak; over 30 cm for 18.0 h; 30 cm reached 0.5 h into the storm; worst hour 15 mm (21% of the storm); runoff beside / along the road at 0.8 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.34); a culvert within 100 m is overtopped |
| 2 | 1.00 | John Fitch Highway | Fitchburg | 0.64 m of water at peak; over 30 cm for 8.0 h; 30 cm reached 8.0 h into the storm; worst hour 16 mm (23% of the storm) |
| 3 | 1.00 | Oakmont Avenue | Westminster | 0.84 m of water at peak; over 30 cm for 12.0 h; 30 cm reached 6.5 h into the storm; worst hour 20 mm (24% of the storm); runoff beside / along the road at 0.9 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.46); a culvert within 100 m is overtopped |
| 4 | 1.00 | Sanborn Street | Fitchburg | 1.15 m of water at peak; over 30 cm for 12.5 h; 30 cm reached 6.0 h into the storm; worst hour 16 mm (21% of the storm); overtopping at 4.2 m/s at a stream crossing (grass-covered fill erodes from ~1.5 m/s); runoff beside / along the road at 2.5 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.80); a culvert within 100 m is overtopped |
| 5 | 1.00 | Westminster Hill Road | Fitchburg | 0.66 m of water at peak; over 30 cm for 7.0 h; 30 cm reached 8.0 h into the storm; worst hour 16 mm (22% of the storm); a culvert within 100 m is overtopped |
| 6 | 1.00 | Fred Smith Road | Westminster | 0.61 m of water at peak; over 30 cm for 5.0 h; 30 cm reached 8.0 h into the storm; worst hour 17 mm (22% of the storm); a culvert within 100 m is overtopped |
| 7 | 1.00 | Route 12 | Ashburnham | 0.59 m of water at peak; over 30 cm for 5.5 h; 30 cm reached 7.0 h into the storm; worst hour 17 mm (22% of the storm); runoff beside / along the road at 1.3 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.42); a culvert within 100 m is overtopped |
| 8 | 0.99 | Route 31 | Fitchburg | 0.56 m of water at peak; over 30 cm for 8.5 h; 30 cm reached 10.0 h into the storm; worst hour 18 mm (24% of the storm); a culvert within 100 m is overtopped |
| 9 | 0.98 | Main Street | Fitchburg | 0.51 m of water at peak; over 30 cm for 6.0 h; 30 cm reached 9.5 h into the storm; worst hour 13 mm (19% of the storm); a culvert within 100 m is overtopped |
| 10 | 0.97 | Dyer Street | Gardner | 0.50 m of water at peak; over 30 cm for 8.5 h; 30 cm reached 10.0 h into the storm; worst hour 13 mm (18% of the storm); water beside the road 0.41 m below its crest (design freeboard 0.30 m; P 0.22) |
| 11 | 0.96 | Veterans Of Foreign Wars Circle | Gardner | 0.48 m of water at peak; over 30 cm for 6.5 h; 30 cm reached 8.5 h into the storm; worst hour 14 mm (19% of the storm); a culvert within 100 m is overtopped |
| 12 | 0.95 | Pearson Boulevard | Gardner | 0.47 m of water at peak; over 30 cm for 6.5 h; 30 cm reached 8.5 h into the storm; worst hour 14 mm (19% of the storm); a culvert within 100 m is overtopped |
| 13 | 0.95 | Pearson Boulevard | Gardner | 0.46 m of water at peak; over 30 cm for 6.0 h; 30 cm reached 8.5 h into the storm; worst hour 14 mm (19% of the storm); a culvert within 100 m is overtopped |
| 14 | 0.94 | Victoria Street | Gardner | 0.46 m of water at peak; over 30 cm for 6.0 h; 30 cm reached 8.5 h into the storm; worst hour 14 mm (19% of the storm); a culvert within 100 m is overtopped |
| 15 | 0.94 | Route 2 | Gardner | 0.45 m of water at peak; over 30 cm for 5.0 h; 30 cm reached 8.5 h into the storm; worst hour 14 mm (19% of the storm); a culvert within 100 m is overtopped |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
