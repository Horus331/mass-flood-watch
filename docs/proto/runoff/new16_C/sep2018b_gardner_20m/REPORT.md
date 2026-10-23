# Road-closure prototype: sep2018b_loss_sep2018b_gardner_20m

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on CPU (OpenMP)), 20 m grid, storm from 2018-09-26T18:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 1,927 |
| Expected closures (sum of probabilities) | 15.0 |
| Segments with closure probability >= 50% | 12 (4.4 km) |
| Further segments that may close (stream reaches the road crest) | 8 (4.9 km) |
| Culverts overtopped / surcharged | 25 / 0 of 451 |
| Road segments cut off from hospitals | 18 |
| Worst added trip time to a hospital | 13.7 min |
| Heaviest hour of rain | 28.2 mm |
| Flood model run time | 1338 s |

## Checks against what happened

- Storm-day flood reports in the area: 0; water >= 10 cm within 100 m of 0% of them, vs 33% of random points (any day).
- MassDOT repeating flood sites in the area: 1; 0 have a segment within 150 m at P >= 0.5 (share of all segments at P >= 0.5: 0.6%).

## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 0.84 | Oakmont Avenue | Westminster | 0.40 m of water at peak; over 30 cm for 7.5 h; 30 cm reached 11.0 h into the storm; worst hour 23 mm (72% of the storm); a culvert within 100 m is overtopped |
| 2 | 0.56 | Veterans Of Foreign Wars Circle | Gardner | 0.32 m of water at peak; over 30 cm for 1.5 h; 30 cm reached 11.0 h into the storm; worst hour 25 mm (69% of the storm); a culvert within 100 m is overtopped |
| 3 | 0.54 | Route 2 | Gardner | 0.31 m of water at peak; over 30 cm for 0.5 h; 30 cm reached 10.5 h into the storm; worst hour 25 mm (67% of the storm); a culvert within 100 m is overtopped |
| 4 | 0.54 | Route 2 | Gardner | 0.31 m of water at peak; over 30 cm for 0.5 h; 30 cm reached 10.5 h into the storm; worst hour 25 mm (66% of the storm); a culvert within 100 m is overtopped |
| 5 | 0.54 | Pearson Boulevard | Gardner | 0.31 m of water at peak; over 30 cm for 1.0 h; 30 cm reached 11.0 h into the storm; worst hour 25 mm (69% of the storm); a culvert within 100 m is overtopped |
| 6 | 0.54 | Route 68 | Gardner | 0.31 m of water at peak; over 30 cm for 0.5 h; 30 cm reached 10.5 h into the storm; worst hour 24 mm (64% of the storm); a culvert within 100 m is overtopped |
| 7 | 0.54 | Route 68 | Gardner | 0.31 m of water at peak; over 30 cm for 0.5 h; 30 cm reached 10.5 h into the storm; worst hour 24 mm (64% of the storm) |
| 8 | 0.54 | Ramp-Rt 68 To Rt 2 Eb | Gardner | 0.31 m of water at peak; over 30 cm for 0.5 h; 30 cm reached 10.5 h into the storm; worst hour 25 mm (66% of the storm); a culvert within 100 m is overtopped |
| 9 | 0.52 | Pearson Boulevard | Gardner | 0.31 m of water at peak; over 30 cm for 0.5 h; 30 cm reached 11.5 h into the storm; worst hour 25 mm (69% of the storm); a culvert within 100 m is overtopped |
| 10 | 0.52 | American Legion Circle | Gardner | 0.31 m of water at peak; over 30 cm for 0.5 h; 30 cm reached 10.5 h into the storm; worst hour 24 mm (64% of the storm); a culvert within 100 m is overtopped |
| 11 | 0.52 | Route 68 | Gardner | 0.31 m of water at peak; over 30 cm for 0.5 h; 30 cm reached 10.5 h into the storm; worst hour 24 mm (64% of the storm) |
| 12 | 0.52 | Victoria Street | Gardner | 0.30 m of water at peak; over 30 cm for 0.5 h; 30 cm reached 11.5 h into the storm; worst hour 25 mm (69% of the storm); a culvert within 100 m is overtopped |
| 13 | 0.37 | Temple Street | Gardner | 0.27 m of water at peak; worst hour 26 mm (68% of the storm); water beside the road 0.40 m below its crest (design freeboard 0.30 m; P 0.24); a culvert within 100 m is overtopped |
| 14 | 0.33 | Pitcherville Road | Hubbardston | 0.26 m of water at peak; worst hour 18 mm (60% of the storm); a culvert within 100 m is overtopped |
| 15 | 0.32 | Dyer Street | Gardner | 0.25 m of water at peak; worst hour 23 mm (66% of the storm) |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
