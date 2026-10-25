# Road-closure prototype: sep2023f_transfer_sep2023f_nnerockland_20m

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on CPU (OpenMP)), 20 m grid, storm from 2023-09-10T10:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 14,306 |
| Expected closures (sum of probabilities) | 37.4 |
| Segments with closure probability >= 50% | 11 (3.2 km) |
| Further segments that may close (stream reaches the road crest) | 8 (2.6 km) |
| Culverts overtopped / surcharged | 32 / 1 of 810 |
| Road segments cut off from hospitals | 0 |
| Worst added trip time to a hospital | 0.0 min |
| Heaviest hour of rain | 47.1 mm |
| Flood model run time | 1273 s |


## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 0.95 | Route 3 | Weymouth | 0.47 m of water at peak; over 30 cm for 6.0 h; 30 cm reached 12.5 h into the storm; worst hour 17 mm (47% of the storm); a culvert within 100 m is overtopped |
| 2 | 0.94 | Libbey Industrial Parkway | Weymouth | 0.46 m of water at peak; over 30 cm for 6.0 h; 30 cm reached 12.5 h into the storm; worst hour 16 mm (47% of the storm); culvert (Unnamed Tributary): headwater 78.63 m vs road crest 1.52 m, 3.7 m3/s |
| 3 | 0.92 | Elm Street | Weymouth | 0.44 m of water at peak; over 30 cm for 6.5 h; 30 cm reached 10.5 h into the storm; worst hour 25 mm (49% of the storm) |
| 4 | 0.92 | Elm Street | Weymouth | 0.44 m of water at peak; over 30 cm for 6.5 h; 30 cm reached 10.5 h into the storm; worst hour 25 mm (49% of the storm) |
| 5 | 0.85 | Route 3 | Weymouth | 0.40 m of water at peak; over 30 cm for 5.0 h; 30 cm reached 12.5 h into the storm; worst hour 18 mm (46% of the storm); a culvert within 100 m is overtopped |
| 6 | 0.85 | Route 3 | Weymouth | 0.40 m of water at peak; over 30 cm for 5.5 h; 30 cm reached 12.0 h into the storm; worst hour 23 mm (49% of the storm); a culvert within 100 m is overtopped |
| 7 | 0.82 | Free Street | Hingham | 0.39 m of water at peak; over 30 cm for 8.0 h; 30 cm reached 10.5 h into the storm; worst hour 34 mm (50% of the storm); a culvert within 100 m is overtopped |
| 8 | 0.81 | Leavitt Street | Hingham | 0.39 m of water at peak; over 30 cm for 8.5 h; 30 cm reached 10.0 h into the storm; worst hour 34 mm (56% of the storm); a culvert within 100 m is overtopped |
| 9 | 0.81 | Leavitt Street | Hingham | 0.39 m of water at peak; over 30 cm for 8.5 h; 30 cm reached 10.0 h into the storm; worst hour 34 mm (56% of the storm); a culvert within 100 m is overtopped |
| 10 | 0.74 | Pleasant Street | Weymouth | 0.36 m of water at peak; over 30 cm for 5.0 h; 30 cm reached 11.0 h into the storm; worst hour 23 mm (49% of the storm); a culvert within 100 m is overtopped |
| 11 | 0.55 | Route 139 | Rockland | 0.31 m of water at peak; over 30 cm for 1.5 h; 30 cm reached 12.0 h into the storm; worst hour 32 mm (72% of the storm); a culvert within 100 m is overtopped |
| 12 | 0.38 | (unnamed) | Pembroke | 0.27 m of water at peak; worst hour 36 mm (43% of the storm); a culvert within 100 m is overtopped |
| 13 | 0.29 | Route 14 | Pembroke | 0.24 m of water at peak; worst hour 38 mm (52% of the storm); a culvert within 100 m is overtopped |
| 14 | 0.23 | Henry Turner Bailey Road | Scituate | 0.23 m of water at peak; worst hour 17 mm (48% of the storm); a culvert within 100 m is overtopped |
| 15 | 0.21 | Route 3 | Weymouth | 0.22 m of water at peak; worst hour 23 mm (49% of the storm); a culvert within 100 m is overtopped |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
